"""EB-1's soft-lock, made legible to an unattended soak.

WHAT THIS IS FOR
`understudy/soak.py` already tells a dead process (`process_died`) from a dead
wire (`bridge_unreachable`), and `Session.died` exists because a process that
is CRASHING is not yet a process that has EXITED. EB-1 is the third shape, and
neither of the two names it:

    entering the Punch Off event room, `PunchOff.PunchEachOther()` instantiates
    a PackedScene whose GPUParticles RID comes back null; the engine logs
    `ERROR: Parameter "particles" is null` once per particle-property setter in
    an UNBOUNDED loop. The main thread spins. The process stays alive, so
    `died()` says no. The wire stops answering, so every request raises. The
    only other thing that moves is `godot.log`, which reached **2.4 GB in ~30
    minutes** -- about 1.3 MB/s -- and the window stops pumping messages, so
    Windows reports the process as not responding.

Filed under `bridge_unreachable` that is a HARNESS-side kind: the instrument
blames its own wire for a build defect it has just caught, which is the exact
misreading `Session.died`'s docstring was written to prevent. So the signature
gets its own name, `unresponsive_spin`, and this module is how it is read.

THE SIGNATURE, AND WHY IT IS TWO SIGNALS AND NOT ONE
A spin is only diagnosable from OUTSIDE the process, and the two observations
available from outside are independent:

  * the log is growing at a rate no ordinary session produces. This one is
    quantitative, it is the loudest half of the signature, and it is the half
    that survives on a machine whose process-status query is unavailable.
  * the process is not pumping messages. On Windows this is what `tasklist`
    calls `Not Responding`. It is cheap and it is the half that survives when
    nobody knows where the log lives.

EITHER is sufficient WHEN THE WIRE IS ALREADY DEAD, and the wire being dead is
a precondition rather than a signal: a game that is answering is not hung,
however loudly it logs. The not-responding signal additionally requires EVERY
sample in the probe window to agree, because a single sample of "not
responding" is also what a long room load looks like, and a watchdog that
files a defect against a slow load is a watchdog that gets turned off.

WHAT THIS MODULE DOES NOT DO
It does not kill anything, write anything, or decide anything. It samples and
it classifies; `soak.Session` owns the teardown, so that the kill stays on the
reversibility ledger with everything else. Every OS-touching call is injected,
which is why the classification can be tested without a game (and is).

Nothing here is a rules change, a stamp, or a measurement. It is a watchdog
bound, in the same sense as `MENU_TIMEOUT_S` and `RUN_TIMEOUT_S`.
"""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------- dials ----
# Watchdog bounds. None of these is a balance number.

# The observed flood was ~1.33 MB/s sustained. The bar is set at roughly a
# fifth of that: high enough that no ordinary session reaches it (a normal
# `godot.log` gains single-digit KB per second even while loading), low enough
# that a slower machine's version of the same unbounded loop still trips it.
FLOOD_BYTES_PER_S = 250_000.0

# The probe window. Long enough that one slow frame cannot fill it, short
# enough that the answer arrives in seconds rather than in the thirty minutes
# it took to notice this by hand.
PROBE_SAMPLES = 5
PROBE_INTERVAL_S = 1.0

# The Godot user-data log, which is NOT in the game directory. Overridable by
# environment because an unusual install moves it and this module must never
# guess silently: an unreadable path yields `None`, which removes the log
# signal rather than faking it.
LOG_ENV = "GITS_GODOT_LOG"
DEFAULT_LOG_RELATIVE = ("SlayTheSpire2", "logs", "godot.log")

# The defect kind this module exists to make filable. Named here rather than in
# `soak` so the string has one home.
DEFECT_KIND = "unresponsive_spin"

# `EB-489`. THE FOURTH SHAPE, and the one the r10 Furina lane died of.
#
# WHAT THE LANE SAW. After `go "Unknown (path 1)"` from a Treasure floor, nine
# consecutive `observe` calls raised `TimeoutError: timed out` against
# `/api/v1/singleplayer` -- while `/` went on answering. The lane stayed that
# way until it was torn down; 22 of 120 actions were lost.
#
# THAT PAIR IS THE WHOLE DIAGNOSIS, and it is structural rather than a guess.
# The two endpoints do NOT run in the same place:
#
#   `/`                       is answered on the ThreadPool worker that took
#                             the request (`McpMod.HandleRequest`), touching
#                             nothing of the game;
#   `/api/v1/singleplayer`    hops to the game thread --
#                             `RunOnMainThread(() => BuildGameState())` and
#                             then `stateTask.GetAwaiter().GetResult()`
#                             (`McpMod.HandleGetState`).
#
# That queue is drained by `ProcessMainThreadQueue`, connected to the
# `SceneTree.ProcessFrame` signal at `Initialize`. So the moment the game
# thread stops reaching a process frame -- a room transition that never
# completes, a scene load that blocks, an awaited modal -- the queued build
# never runs, `GetResult()` waits with NO TIMEOUT AND NO CANCELLATION, and the
# state endpoint is dead for the rest of the process's life while the root
# endpoint keeps saying `status: ok`. Each attempt after that leaks another
# ThreadPool worker parked on the same queue, which is why nine tries did not
# recover and could not.
#
# HOW IT IS TOLD FROM `unresponsive_spin`. It is not told from it by the root
# endpoint -- EB-1's spin answers `/` too, for the same reason. It is told from
# it by the ABSENCE of EB-1's two signals: a spin floods `godot.log` at ~1.3
# MB/s and stops pumping window messages, and this shape does neither. So the
# order in `classify` is: EB-1's signature first, and a root that still answers
# with neither of those signals is this.
#
# NOT FIXED HERE. The repair is on the bridge side of the wire -- a bounded
# wait on that hop, answering 503 with the queue depth instead of blocking a
# worker forever -- and that is a `vendor/STS2_MCP` change that cannot be
# proved without a build and a lane. Named, so the next lane files it as this
# rather than as "the bridge stopped answering".
STATE_STALL_KIND = "state_thread_stall"


def default_log_path(env: dict[str, str] | None = None) -> Path | None:
    """`%APPDATA%\\SlayTheSpire2\\logs\\godot.log`, or whatever overrides it.

    Returns `None` rather than a guess when neither is available: a log path
    that does not exist must remove the log signal, not fabricate a zero.
    """
    env = os.environ if env is None else env
    override = (env.get(LOG_ENV) or "").strip()
    if override:
        return Path(override)
    appdata = (env.get("APPDATA") or "").strip()
    if not appdata:
        return None
    return Path(appdata).joinpath(*DEFAULT_LOG_RELATIVE)


# ------------------------------------------------------------- probing ----

def file_size(path: Path | None) -> int | None:
    """Size in bytes, or `None` for anything this cannot read.

    A missing file is `None` and not `0`. Zero is a measurement claiming the
    log is empty; `None` is the truth, which is that we did not see it.
    """
    if path is None:
        return None
    try:
        return path.stat().st_size
    except OSError:
        return None


def _tasklist(image_name: str, pid: int | None = None) -> str:
    # BY PID WHERE THERE IS ONE. With two lanes running, an IMAGENAME filter
    # answers about BOTH games: lane 0 hanging would read as lane 1 hanging,
    # and a watchdog that files a defect against the wrong process is worse
    # than one that files none. The image filter stays for the single-lane
    # callers that have no pid to give.
    where = ([f"PID eq {int(pid)}"] if pid is not None
             else [f"IMAGENAME eq {image_name}"])
    r = subprocess.run(
        ["tasklist", "/FI", where[0],
         "/FI", "STATUS eq NOT RESPONDING", "/NH"],
        capture_output=True, text=True, timeout=20)
    return r.stdout or ""


def windows_responding(image_name: str, query=_tasklist,
                       pid: int | None = None) -> bool | None:
    """`False` when Windows says the image is Not Responding, else `True`.

    `None` is "cannot tell", and it is deliberately common: a non-Windows host,
    a `tasklist` that is absent, a query that raised. A watchdog whose unknown
    reads as a positive is a watchdog that files defects against nothing.
    """
    try:
        # A caller-supplied `query` written before pids existed takes one
        # argument; the two-argument call is tried first and falls back, so
        # every existing test double keeps working.
        try:
            out = query(image_name, pid)
        except TypeError:
            out = query(image_name)
    except Exception:                                        # noqa: BLE001
        return None
    if out is None:
        return None
    text = out.strip()
    if not text:
        # An empty table under this filter pair means the image is present and
        # responding, OR that the image is not running at all. The caller
        # already knows the process is alive -- that is the precondition -- so
        # empty means responding.
        return True
    lowered = text.lower()
    if "no tasks" in lowered or lowered.startswith("info:"):
        return True
    if image_name.lower() in lowered:
        return False
    # Output we do not recognise. Not an answer, and it must not read as one.
    return None


@dataclass(frozen=True)
class Probe:
    """One sampling window, as raw as it can be kept.

    The rate is derived rather than stored so a reader of a defect record can
    check the arithmetic against the two byte counts that produced it.
    """
    log_path: str | None = None
    log_bytes_start: int | None = None
    log_bytes_end: int | None = None
    elapsed_s: float = 0.0
    responding: tuple = ()
    #: `EB-489`. Whether the bridge's ROOT endpoint answered during the window,
    #: `None` where nobody asked. It is the half of the pair that separates a
    #: game-thread stall from a wire that is simply gone -- see
    #: `STATE_STALL_KIND` for why the two endpoints answer from different
    #: threads and what that makes readable.
    root_answers: bool | None = None

    @property
    def log_bytes_per_s(self) -> float | None:
        if (self.log_bytes_start is None or self.log_bytes_end is None
                or self.elapsed_s <= 0):
            return None
        grown = self.log_bytes_end - self.log_bytes_start
        if grown < 0:
            # The log rotated under us (the game writes a fresh one per
            # launch). That is not a shrinking flood; it is no reading.
            return None
        return grown / self.elapsed_s

    def as_evidence(self) -> dict:
        rate = self.log_bytes_per_s
        return {
            "log_path": self.log_path,
            "log_bytes_start": self.log_bytes_start,
            "log_bytes_end": self.log_bytes_end,
            "log_bytes_per_s": None if rate is None else round(rate, 1),
            "flood_threshold_bytes_per_s": FLOOD_BYTES_PER_S,
            "elapsed_s": round(self.elapsed_s, 2),
            "responding_samples": list(self.responding),
            "root_answers": self.root_answers,
        }


def sample(log_path: Path | None, image_name: str,
           samples: int = PROBE_SAMPLES,
           interval: float = PROBE_INTERVAL_S,
           sizer=file_size, responder=windows_responding,
           sleep=time.sleep, clock=time.monotonic,
           pid: int | None = None, rooter=None) -> Probe:
    """Watch the log and the message pump for `samples` ticks.

    Every OS call is a parameter. That is not ceremony: the whole value of this
    module is a judgment that must be right the first time it fires, at 3am,
    unattended, and a judgment that can only be exercised by hanging a real
    game is a judgment nobody exercises.

    `rooter` (`EB-489`) is the one WIRE call, and it is optional for the same
    reason every other call is injected: a caller that cannot ask leaves
    `root_answers` at `None`, which removes the signal rather than faking it.
    `understudy.bridge.health` is the live one -- it requests `BASE + "/"`,
    which is the endpoint that went on answering while the lane's state reads
    timed out.
    """
    samples = max(2, int(samples))
    start_bytes = sizer(log_path)
    t0 = clock()
    def ask():
        try:
            return responder(image_name, pid=pid)
        except TypeError:
            return responder(image_name)

    responding: list = [ask()]
    for _ in range(samples - 1):
        sleep(interval)
        responding.append(ask())
    end_bytes = sizer(log_path)
    root: bool | None = None
    if rooter is not None:
        try:
            rooter()
            root = True
        except Exception:                                    # noqa: BLE001
            root = False
    return Probe(
        log_path=None if log_path is None else str(log_path),
        log_bytes_start=start_bytes, log_bytes_end=end_bytes,
        elapsed_s=clock() - t0, responding=tuple(responding),
        root_answers=root)


# --------------------------------------------------------- the verdict ----

@dataclass(frozen=True)
class Verdict:
    hung: bool
    reason: str
    signals: tuple = ()
    evidence: dict = field(default_factory=dict)

    def detail(self) -> str:
        return self.reason


def classify(probe: Probe, *, alive: bool, wire_dead: bool,
             flood_bytes_per_s: float = FLOOD_BYTES_PER_S) -> Verdict:
    """Is this the EB-1 shape? Pure function of the probe and two booleans.

    The order of the two refusals matters and both are refusals, not signals:

      * a wire that answered is not a hang, whatever the log is doing;
      * a process that has EXITED is `process_died`'s, and this must not take
        it -- `Session.died` already applies the grace period that makes that
        question answerable, and two kinds competing for one failure is how a
        defect table stops being readable.
    """
    evidence = probe.as_evidence()
    if not wire_dead:
        return Verdict(False, "the bridge answered; there is nothing to "
                              "classify", (), evidence)
    if not alive:
        return Verdict(False, "the process has exited; `process_died` owns "
                              "this failure", (), evidence)

    signals: list[str] = []
    rate = probe.log_bytes_per_s
    if rate is not None and rate >= flood_bytes_per_s:
        signals.append(
            f"log flood: {rate:,.0f} B/s >= {flood_bytes_per_s:,.0f} B/s over "
            f"{probe.elapsed_s:.1f}s")
    seen = [r for r in probe.responding if r is not None]
    if len(seen) >= 2 and all(r is False for r in seen):
        signals.append(
            f"not responding on all {len(seen)} sampled tick(s) of the probe "
            f"window")

    if not signals:
        # `EB-489`. THE ROOT ENDPOINT SPLITS THIS BRANCH IN TWO. It is asked
        # only AFTER EB-1's signature has failed to fire, because a spin
        # answers `/` as readily as a stall does -- the root handler never
        # leaves the ThreadPool worker. What separates them is that a spin
        # floods the log and stops the message pump and this does neither.
        if probe.root_answers is True:
            return Verdict(
                False,
                "the state endpoint is dead, the process is alive and "
                "responding, and the bridge's ROOT endpoint still answers. "
                "The two are served from different threads: `/` replies on "
                "the ThreadPool worker, and `/api/v1/singleplayer` hops to "
                "the game thread (`RunOnMainThread(BuildGameState)` then a "
                "`GetResult()` with no timeout) whose queue is drained from "
                "`SceneTree.ProcessFrame`. So the game thread has stopped "
                f"reaching a process frame; this is `{STATE_STALL_KIND}`, and "
                "every further read parks another worker on the same queue. "
                "Recovery is a teardown -- there is no unblocking it from "
                "this side",
                (f"root endpoint answers, {STATE_STALL_KIND}",), evidence)
        return Verdict(
            False,
            "the wire is dead and the process is alive, but neither the log "
            "rate nor the message pump says the main thread is spinning; this "
            "is `bridge_unreachable`",
            (), evidence)

    return Verdict(
        True,
        "the process is alive, the wire is dead, and " + "; ".join(signals)
        + ". That is EB-1's signature (an unbounded engine-error loop on the "
          "main thread). The run save is expected to be POISONED: relaunching "
          "and choosing `continue` re-enters the room and hangs again, so the "
          "recovery is `abandon_run` from the main menu, which is what the "
          "soak's own restart path already does.",
        tuple(signals), evidence)


def diagnose(image_name: str, *, alive: bool, wire_dead: bool = True,
             log_path: Path | None = None, pid: int | None = None,
             **probe_kwargs) -> Verdict:
    """`sample` then `classify`, which is the whole of the live entry point.

    `log_path` and `pid` are how a LANE is watched rather than a machine: with
    two games up, `%APPDATA%` is per-process, so each lane has its own
    `godot.log` and its own pid, and a watchdog given neither is watching
    whichever game the shell happened to point at.
    """
    if log_path is None:
        log_path = default_log_path()
    probe = sample(log_path, image_name, pid=pid, **probe_kwargs)
    return classify(probe, alive=alive, wire_dead=wire_dead)
