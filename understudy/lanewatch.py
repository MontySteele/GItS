"""`EB-691`: the watchdog a BLIND-PLAY LANE has, and did not.

WHAT THIS IS FOR, AND WHY `hangwatch` IS NOT IT
`hangwatch.py` reads EB-1's signature -- a spinning main thread, a flooding
`godot.log`, a message pump that stopped -- and it is wired into ONE caller,
`soak_driver.RunDriver._check`. That driver owns its own process and takes an
action every few seconds, so a five-second probe window costs it nothing.

A blind-play lane is the opposite shape and has none of that. The seat sees
exactly two commands, `blindplay observe` and `blindplay act`; each is a
SEPARATE PROCESS holding no session, no `Popen` and no memory of the last
call; and the gap between two of them is however long a model takes to think.
On 2026-09-08 round 29's lane 2 entered the Punch Off room (EB-1, the third
recorded observation -- `understudy/README.md`, "Surviving EB-1"). The log
reached 143M lines / 19 GB, the process 3.2 GB, the bridge's HEALTH endpoint
went on answering while `state` timed out, and the seat -- correctly, per its
brief -- retried `observe` sixteen times over fifteen minutes. Nothing was
watching, because nothing in that path watches.

SO THE WATCH IS FILE-BACKED AND IT RUNS BEFORE THE WIRE CALL. The cursor a
long-lived driver keeps in memory lives here in one small JSON file per lane
(the arrangement `blindplay_shape`'s action budget and `blindplay_faces`'
deck memory already use, for the same one-process-per-call reason): the last
`godot.log` size and the moment it was read. Two consecutive commands are the
probe window, and the seat's own thinking time is what makes it long enough
to be a rate rather than a sample.

THREE SIGNALS, EACH A SEPARATE READING OF THE SAME EVENT (thresholds below):

  * the lane's `godot.log` grew at a flood RATE since the last command;
  * the lane's game process holds more memory than a playing game ever does;
  * the state endpoint timed out twice running WHILE health kept answering.

Any one of them ends the lane. That is deliberately looser than `hangwatch`'s
"either signal, but only on a dead wire": this watchdog's cost of being wrong
is a torn-down disposable lane and a round that stops early, and its cost of
being silent was measured at fifteen minutes and 19 GB.

WHAT HAPPENS THEN. The lane is TORN DOWN -- `embark.teardown`, the same undo
`--teardown` walks, so the kill stays on the reversibility ledger with
everything else -- and the command prints `TOOL-BLOCKED: lane dead (<reason>)`
and exits non-zero. `TOOL-BLOCKED` is the word the seat brief already tells a
seat to stop on, so no seat needs a new rule to obey this one; the brief gains
a sentence saying which stop it is.

`embark` IS IMPORTED INSIDE `tear_down`, NOT AT MODULE SCOPE, and that is a
blindness rule rather than a style: `blindplay` calls this module, and
`test_blindplay_cannot_reach_a_sheet_or_a_policy` forbids that family from
reaching `embark`, `soak` and every sheet loader behind them. Nothing on the
READ path here imports any of them -- the pid and the log path are read out of
the embark sidecar's own JSON -- and the one import that does happen happens
only on the death path, after which nothing is rendered to anybody.

None of the numbers here is a balance number, a stamp or a measurement. They
are watchdog bounds, in the same sense `hangwatch`'s are, and D-picks under
the R212 ladder.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from understudy import hangwatch

# --------------------------------------------------------------- dials ----

#: THE FLOOD RATE, and it is `hangwatch`'s number rather than a second copy:
#: one storm, one bar, and a retune of the soak's watchdog moves the lane's
#: too. 250,000 B/s is about a fifth of the 1.33 MB/s the 2026-08-13 read
#: measured, and about two orders of magnitude above what an ordinary session
#: writes (single-digit KB/s, even while loading a room).
LOG_RATE_BYTES_PER_S = hangwatch.FLOOD_BYTES_PER_S

#: THE NOISE FLOOR under the rate, in bytes grown since the last command. Two
#: commands can land a fraction of a second apart -- an `observe` the seat
#: immediately follows with an `act` -- and a few hundred KB flushed in that
#: window divides into a rate that looks like a flood. 2 MB is more than a
#: quiet lane writes between any two commands and is reached in under two
#: seconds of the real storm.
LOG_GROWTH_FLOOR_BYTES = 2 * 1024 * 1024

#: The shortest window a RATE is computed over at all. Below this the
#: arithmetic is division by a rounding error, and the reading is skipped
#: rather than guessed.
MIN_WINDOW_S = 1.0

#: THE MEMORY BAR. The two-instance experiment measured roughly 1 GB of RAM
#: per game (`understudy/instances.py`); lane 2 was at 3.2 GB when it was
#: found by hand. 2.5 GB is above anything a playing game has been seen at and
#: below what the storm reaches, so it fires while the machine is still
#: comfortable.
PROC_BYTES = 2_500_000_000

#: HOW MANY STATE TIMEOUTS, WITH HEALTH STILL ANSWERING, END THE LANE. One is
#: a slow room load and must not; two running is the `EB-489` /
#: `hangwatch.STATE_STALL_KIND` pair, which has no recovery from this side --
#: every further read parks another worker on the same queue. The counter is
#: reset by any state read that succeeds, so two must be CONSECUTIVE.
STATE_TIMEOUTS = 2

#: The line the seat is given. `TOOL-BLOCKED` is load-bearing: the brief
#: already says to stop and write the record on one.
BLOCKED = "TOOL-BLOCKED: lane dead"

#: What a command exits with after printing it. Distinct from the leak/shape
#: refusal (1) and the budget refusal (2) so a coordinator reading exit codes
#: can tell a dead lane from a stopped round.
EXIT_LANE_DEAD = 3

_STORE_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR = _STORE_DIR

#: `instances.LANE_ENV`'s value, spelled rather than imported for
#: `blindplay_shape.LANE_ENV`'s reason and held in step from the test side.
LANE_ENV = "GITS_LANE"

#: `instances.LOG_RELATIVE`, same discipline.
LOG_RELATIVE = ("SlayTheSpire2", "logs", "godot.log")


# ------------------------------------------------------- naming a lane ----

def lane_tag(lane: object = None) -> str:
    """`1` / `"1"` / `"lane1"` -> `"1"`; unset or unreadable -> `"0"`.

    A byte-for-byte reading of `blindplay_shape.lane_tag`, and deliberately a
    second one: this module is reached from `embark` as well as from the blind
    commands, and importing the blind family from the launcher half would make
    a cycle out of a six-line function.
    """
    raw = os.environ.get(LANE_ENV, "") if lane is None else str(lane)
    raw = re.sub(r"[^A-Za-z0-9]", "", raw).lower()
    if raw.startswith("lane"):
        raw = raw[4:]
    return raw or "0"


def lane_label(lane: object = None) -> str:
    return f"lane{lane_tag(lane)}"


# ------------------------------------------------------------- the store --

def store_path(lane: object = None) -> Path:
    return _STORE_DIR / f"_lanewatch-lane{lane_tag(lane)}.json"


def read_store(lane: object = None) -> dict:
    """This lane's cursor, or an empty one. Never raises."""
    try:
        blob = json.loads(store_path(lane).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        blob = {}
    return blob if isinstance(blob, dict) else {}


def _write_store(row: dict, lane: object = None) -> None:
    try:
        _STORE_DIR.mkdir(parents=True, exist_ok=True)
        store_path(lane).write_text(json.dumps(row), encoding="utf-8")
    except OSError:
        pass                    # a read-only tree simply keeps no cursor


def arm(lane: object = None) -> dict:
    """Start a fresh watch for this lane. The coordinator's write, at embark.

    Zeroing is the point, exactly as it is for the action budget: an embark is
    a new run, and a cursor left over from the lane's last game would make the
    first `observe` of this one compare against a log that no longer exists.
    """
    row = {"log_bytes": None, "seen_at": None, "state_timeouts": 0,
           "dead": "", "armed_at": time.time()}
    _write_store(row, lane)
    return row


def forget(lane: object = None) -> None:
    """Drop this lane's watch. The operator's reset, and the tests'."""
    try:
        store_path(lane).unlink()
    except OSError:
        pass


# --------------------------------------------------- reading the machine --

def sidecar_row(lane: object = None, log_dir: Path | None = None) -> dict:
    """The newest launching embark sidecar for this lane, or `{}`.

    READ AS JSON, NOT THROUGH `embark`. Everything wanted here -- which user
    tree the lane's game writes into, and which ledger holds its pid -- is a
    plain field on a file `embark` already wrote, and importing that module to
    re-read it would drag `soak` and every sheet loader behind it into the
    blind commands' process.
    """
    root = LOG_DIR if log_dir is None else log_dir
    label = lane_label(lane)
    best: dict = {}
    try:
        paths = sorted(root.glob("embark-*.json"))
    except OSError:
        return {}
    for path in paths:
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(blob, dict) or blob.get("hold"):
            # A `--hold` embark launched nothing, so it names no pid and its
            # lane's game belongs to somebody else.
            continue
        if str(blob.get("instance") or "lane0") == label:
            best = blob
    return best


def lane_log_path(lane: object = None,
                  row: dict | None = None) -> Path | None:
    """This lane's own `godot.log`, or `None` when it cannot be named.

    `None` rather than a guess, for `hangwatch.default_log_path`'s reason: a
    log path that does not exist must REMOVE the log signal, not fabricate a
    quiet reading of somebody else's file. Lane 0 falls back to `hangwatch`'s
    `%APPDATA%` resolution, which is the same file by a different route.
    """
    row = sidecar_row(lane) if row is None else row
    appdata = str(row.get("appdata") or "")
    if appdata and appdata != "default":
        return Path(appdata).joinpath(*LOG_RELATIVE)
    return hangwatch.default_log_path()


def lane_pid(lane: object = None, row: dict | None = None) -> int | None:
    """The pid of the game this lane's embark launched, off the ledger.

    `Session` writes it there the moment it launches (`EB-231`), which is the
    same fact `embark --teardown` rebuilds a kill from; this reads it rather
    than re-deriving one by port or image name, because with two games up an
    image-name reading answers about both.
    """
    row = sidecar_row(lane) if row is None else row
    ledger = str(row.get("ledger") or "")
    if not ledger:
        return None
    try:
        entries = json.loads(Path(ledger).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(entries, list):
        return None
    for entry in reversed(entries):
        if isinstance(entry, dict) and entry.get("pid"):
            try:
                return int(entry["pid"])
            except (TypeError, ValueError):
                return None
    return None


def _tasklist_mem(pid: int) -> str:
    r = subprocess.run(
        ["tasklist", "/FI", f"PID eq {int(pid)}", "/FO", "CSV", "/NH"],
        capture_output=True, text=True, timeout=20)
    return r.stdout or ""


def working_set_bytes(pid: int | None, query=_tasklist_mem) -> int | None:
    """The process's memory, in bytes, or `None` for anything unreadable.

    `None` is deliberately common and must never read as zero -- a host with
    no `tasklist`, a pid that has exited, output in a locale this does not
    parse. An unknown removes the memory signal; it does not clear the lane.
    """
    if pid is None:
        return None
    try:
        out = query(pid)
    except Exception:                                        # noqa: BLE001
        return None
    if not out:
        return None
    # `"SlayTheSpire2.exe","20792","Console","1","3,355,444 K"` -- the last
    # quoted field, in KB, with the locale's thousands separators in it.
    fields = re.findall(r'"([^"]*)"', out.strip().splitlines()[0])
    if len(fields) < 5:
        return None
    digits = re.sub(r"[^0-9]", "", fields[-1])
    if not digits:
        return None
    return int(digits) * 1024


# ------------------------------------------------------------ the verdict --

@dataclass(frozen=True)
class Verdict:
    dead: bool
    reason: str = ""
    evidence: dict = field(default_factory=dict)

    def line(self) -> str:
        return f"{BLOCKED} ({self.reason})"


ALIVE = Verdict(False)


def check(lane: object = None, *, now: float | None = None,
          sizer=hangwatch.file_size, memory=working_set_bytes) -> Verdict:
    """Read the three signals and update the cursor. Posts nothing, kills
    nothing.

    Every OS call is a parameter, for the reason `hangwatch.sample`'s are: a
    judgement that only fires during a storm is a judgement nobody can
    exercise unless it can be exercised without one.
    """
    now = time.time() if now is None else now
    row = read_store(lane)
    if row.get("dead"):
        # STICKY. The teardown already ran; a second command on the same lane
        # must be told the same thing rather than re-reading a log whose
        # process is gone and finding it quiet.
        return Verdict(True, str(row["dead"]), {"sticky": True})

    sidecar = sidecar_row(lane)
    log_path = lane_log_path(lane, sidecar)
    pid = lane_pid(lane, sidecar)
    size = sizer(log_path)
    last_bytes = row.get("log_bytes")
    last_seen = row.get("seen_at")
    evidence: dict = {
        "lane": lane_label(lane),
        "log_path": None if log_path is None else str(log_path),
        "log_bytes": size,
        "log_bytes_last": last_bytes,
        "pid": pid,
    }

    verdict = ALIVE
    if (isinstance(size, int) and isinstance(last_bytes, int)
            and isinstance(last_seen, (int, float))):
        grown = size - last_bytes
        elapsed = now - float(last_seen)
        # A SHRINKING LOG IS NO READING, not a negative flood: the game writes
        # a fresh `godot.log` per launch, so a rotation under the cursor is
        # exactly what this looks like.
        if grown >= 0 and elapsed >= MIN_WINDOW_S:
            rate = grown / elapsed
            evidence.update({"log_grown": grown,
                             "window_s": round(elapsed, 2),
                             "log_bytes_per_s": round(rate, 1)})
            if grown >= LOG_GROWTH_FLOOR_BYTES and rate >= LOG_RATE_BYTES_PER_S:
                verdict = Verdict(
                    True,
                    f"godot.log grew {grown / 1e6:,.1f} MB in "
                    f"{elapsed:,.0f}s ({rate / 1e6:,.2f} MB/s, bar "
                    f"{LOG_RATE_BYTES_PER_S / 1e6:,.2f} MB/s) -- EB-1's "
                    f"error storm",
                    evidence)

    if not verdict.dead:
        rss = memory(pid)
        evidence["proc_bytes"] = rss
        if isinstance(rss, int) and rss >= PROC_BYTES:
            verdict = Verdict(
                True,
                f"the game process (pid {pid}) holds {rss / 1e9:,.1f} GB, "
                f"past the {PROC_BYTES / 1e9:,.1f} GB bar",
                evidence)

    if not verdict.dead:
        stale = int(row.get("state_timeouts") or 0)
        evidence["state_timeouts"] = stale
        if stale >= STATE_TIMEOUTS:
            verdict = Verdict(
                True,
                f"the state endpoint timed out {stale} times running while "
                f"health kept answering -- the game thread has stopped "
                f"reaching a process frame and every further read parks "
                f"another worker on its queue",
                evidence)

    row.update({"log_bytes": size, "seen_at": now})
    if verdict.dead:
        row["dead"] = verdict.reason
        row["evidence"] = evidence
    _write_store(row, lane)
    # THE EVIDENCE RIDES ON A LIVE VERDICT TOO. What the watchdog measured on
    # a lane it passed is the only way to check its arithmetic without a
    # storm, and a caller holding an answer with no numbers on it cannot say
    # why the lane was cleared.
    return verdict if verdict.dead else Verdict(False, "", evidence)


# -------------------------------------------------- the timeout counter ---

def is_timeout(exc: BaseException) -> bool:
    """Is this bridge failure a TIMEOUT rather than a refused connection?

    The distinction is the whole of the third signal. A refused or reset
    connection means the process is GONE, which is a different failure with a
    different answer; a timeout with health still answering is the game thread
    stalled. `bridge` wraps every stdlib shape into `BridgeError`, so the
    reading is of the message as well as the type.
    """
    if isinstance(exc, TimeoutError):
        return True
    text = f"{exc}".lower()
    return "timed out" in text or "timeout" in text


def record_state_timeout(lane: object = None, *, health_answers: bool = True
                         ) -> int:
    """Charge one state timeout to this lane, and return the new count.

    `health_answers=False` does NOT charge: a lane whose root endpoint has
    also gone quiet is an ordinary unreachable bridge (or a game that exited),
    and this counter exists only for the pair where the two disagree.
    """
    if not health_answers:
        return int(read_store(lane).get("state_timeouts") or 0)
    row = read_store(lane)
    row["state_timeouts"] = int(row.get("state_timeouts") or 0) + 1
    _write_store(row, lane)
    return row["state_timeouts"]


def record_state_ok(lane: object = None) -> None:
    """A state read answered: the timeouts must be CONSECUTIVE to count."""
    row = read_store(lane)
    if row.get("state_timeouts"):
        row["state_timeouts"] = 0
        _write_store(row, lane)


# ---------------------------------------------------------- the teardown --

def tear_down(lane: object = None) -> str:
    """Walk this lane's embark back, through `embark.teardown` and nothing
    else.

    Imported HERE rather than at module scope -- see this module's header: the
    blind commands may not reach `embark`, and this is the one path that does,
    after which nothing is rendered to a seat. A teardown that fails is
    REPORTED and never raised: the lane is dead either way, and the seat's
    stop must not depend on the undo succeeding.
    """
    try:
        from understudy import embark
    except Exception as exc:                                 # noqa: BLE001
        return f"teardown unavailable ({type(exc).__name__}: {exc})"
    try:
        embark.teardown(lane=lane_tag(lane))
        return "lane torn down"
    except Exception as exc:                                 # noqa: BLE001
        return (f"TEARDOWN FAILED ({type(exc).__name__}: {exc}) -- the game "
                f"may still be up; tear it down by hand")


def guard(lane: object = None, *, teardown=tear_down, **kwargs) -> str:
    """The whole watchdog for one command: `""` on a quiet lane, else the
    line.

    A quiet lane pays one `stat` and one `tasklist`, and nothing else changes
    about the command it fronts.
    """
    verdict = check(lane, **kwargs)
    if not verdict.dead:
        return ""
    if verdict.evidence.get("sticky"):
        # Already torn down on the command that found it. Saying it again is
        # the point; doing it again is not.
        return verdict.line()
    return f"{verdict.line()}. {teardown(lane)}"
