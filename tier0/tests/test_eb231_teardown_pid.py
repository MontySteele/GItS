"""EB-231: a teardown may not report a kill it did not make.

`KLEESPARK-W3`'s teardown wrote **REVERTED** over the launch entry and the
bridge removal then failed on a live PID -- twice -- and the operator finished
it by hand. The marker was not merely wrong, it was the WORST kind of wrong:
the next deploy reads a ledger saying the game is closed and goes to war with
a running one.

THE MECHANISM, and it is one line. `embark --teardown` rebuilds the session
from the ledger ON DISK. That session holds no `Popen`, so `Session._kill`
found `self.proc is None` and did nothing, and `_stop_game` returned
"process terminated" regardless -- a string the ledger writes as REVERTED.

The repair is in two halves and both are locked below: the pid is RECORDED on
the launch entry at launch, so a rebuilt session has a handle at all, and the
exit is PROVEN against the process table before the marker is written. On a
timeout `_stop_game` raises, `_step` records NOT REVERTED naming what is still
alive, and nothing downstream is told the game is gone.

NO PROCESS IS STARTED OR KILLED HERE. The process table is a mock -- one dict
of pids the fake `tasklist` answers from -- which is what makes the "still
alive" arm testable at all: the failure this row is about is a live game, and
a test that needed one could never run in the suite.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from understudy import soak


# --------------------------------------------------------- the mock table --

class _Table:
    """The pids the fake `tasklist` will admit to, and the calls it saw."""

    def __init__(self, alive: dict[int, str] | None = None):
        self.alive = dict(alive or {})
        self.taskkills: list[list[str]] = []

    def run(self, argv, **kwargs):
        if argv and argv[0] == "tasklist":
            pid = int(str(argv[2]).split()[-1])
            name = self.alive.get(pid)
            rows = (f'"{name}","{pid}","Console","1","1,234,567 K"\n'
                    if name else
                    "INFO: No tasks are running which match the specified "
                    "criteria.\n")
            return subprocess.CompletedProcess(argv, 0, rows, "")
        if argv and argv[0] == "taskkill":
            self.taskkills.append(list(argv))
            return subprocess.CompletedProcess(argv, 0, "", "")
        raise AssertionError(f"no other process is spawned by these tests: "
                             f"{argv!r}")


@pytest.fixture()
def table(monkeypatch):
    t = _Table()
    monkeypatch.setattr(soak.subprocess, "run", t.run)
    monkeypatch.setattr(soak.time, "sleep", lambda *_: None)
    monkeypatch.setattr(soak, "PID_EXIT_TIMEOUT_S", 0.05)
    monkeypatch.setattr(soak, "PID_EXIT_POLL_S", 0.0)
    return t


def _session(tmp_path: Path, pid: int | None) -> soak.Session:
    """A session rebuilt the way `embark --teardown` rebuilds one.

    `Session.__new__` and nothing else: no setup ran, no game was launched by
    this object, and `proc` is None -- which is the whole condition the defect
    lived in.
    """
    s = soak.Session.__new__(soak.Session)
    s.dir = tmp_path
    s.ledger = soak.Reversibility(path=tmp_path / "ledger.json")
    entry = s.ledger.record("Launched `SlayTheSpire2.exe` directly",
                            "process terminated at teardown")
    if pid is not None:
        entry["pid"] = pid
        s.ledger.flush()
    s._launch_entry = entry
    return s


def _state(session: soak.Session) -> dict:
    return json.loads(session.ledger.path.read_text(encoding="utf-8"))[0]


# ------------------------------------------------- the lock, seen to FAIL --

def test_a_live_pid_is_never_marked_reverted(tmp_path, table):
    """THE LOCK. On the old code this row read REVERTED / "process
    terminated" with the game still on screen, which is `KLEESPARK-W3` exactly.

    Here the mock table keeps answering with the pid, `taskkill` is a no-op
    that changes nothing (a real force-kill can also fail -- that is the case
    being modelled), and the marker must not be written.
    """
    s = _session(tmp_path, 31448)
    table.alive[31448] = "SlayTheSpire2.exe"

    s._step(s._launch_entry, s._stop_game)

    row = _state(s)
    assert row["state"] == "NOT REVERTED"
    assert "31448" in row["error"] and "SlayTheSpire2.exe" in row["error"]
    assert "STILL ALIVE" in row["error"]
    # And it says what to do, naming the pid rather than the image: an image
    # name is what `taskkill /IM` takes, and that belt is gone on purpose.
    assert "taskkill /F /T /PID 31448" in row["error"]


def test_a_pid_that_is_gone_is_marked_reverted_and_says_so(tmp_path, table):
    """The other direction, because a check that refuses everything is not a
    check. Nothing holds the number, so the marker is written -- and the note
    quotes the pid it proved gone rather than asserting a kill in the
    abstract."""
    s = _session(tmp_path, 31448)

    s._step(s._launch_entry, s._stop_game)

    row = _state(s)
    assert row["state"] == "REVERTED"
    assert row["note"] == "process terminated -- pid 31448 verified gone"


def test_a_pid_that_leaves_during_the_wait_is_still_a_clean_teardown(
        tmp_path, table, monkeypatch):
    """A game does not exit the instant it is asked to. The wait is a wait."""
    s = _session(tmp_path, 31448)
    table.alive[31448] = "SlayTheSpire2.exe"
    monkeypatch.setattr(soak, "PID_EXIT_TIMEOUT_S", 30.0)

    seen = {"n": 0}
    real = soak.pid_image

    def fading(pid):
        seen["n"] += 1
        if seen["n"] >= 3:
            table.alive.pop(pid, None)
        return real(pid)

    monkeypatch.setattr(soak, "pid_image", fading)
    s._step(s._launch_entry, s._stop_game)

    assert _state(s)["state"] == "REVERTED"
    assert seen["n"] >= 3


# --------------------------------------------------- the pid on the ledger --

def test_the_launch_entry_carries_the_pid_on_disk(tmp_path, monkeypatch):
    """Half one: without the number written down, a rebuilt session has no
    handle on the game at all and every check below is unreachable."""

    class _Popen:
        pid = 4242

        def __init__(self, *a, **k):
            pass

    (tmp_path / soak.GAME_EXE).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / soak.GAME_EXE).write_text("", encoding="utf-8")
    monkeypatch.setattr(soak.subprocess, "Popen", _Popen)

    s = soak.Session.__new__(soak.Session)
    s.dir = tmp_path
    s.ledger = soak.Reversibility(path=tmp_path / "ledger.json")
    s._launch_entry = None
    s.instance = None
    s.intent = ""
    s.proc = None
    s._launch()

    assert s.pid == 4242
    assert json.loads((tmp_path / "ledger.json").read_text(
        encoding="utf-8"))[0]["pid"] == 4242


def test_a_rebuilt_session_reads_its_pid_off_the_ledger(tmp_path, table):
    """The `--teardown` path: no `Popen`, and the pid is still known."""
    s = _session(tmp_path, 777)
    assert s.proc is None
    assert s.pid == 777


def test_a_rebuilt_session_kills_by_that_pid_and_no_other(tmp_path, table):
    """It must actually TRY. A check that only refuses would turn every
    teardown into hand work, which is what this row was filed about."""
    s = _session(tmp_path, 777)
    table.alive[777] = "SlayTheSpire2.exe"
    s._kill()
    assert table.taskkills == [["taskkill", "/F", "/T", "/PID", "777"]]


def test_a_ledger_written_before_this_change_refuses_rather_than_claims(
        tmp_path, table):
    """An entry from an older run carries no pid. That is not a licence to
    assume the process is gone -- the marker is refused and the operator is
    told what to do by hand."""
    s = _session(tmp_path, None)

    s._step(s._launch_entry, s._stop_game)

    row = _state(s)
    assert row["state"] == "NOT REVERTED"
    assert "no pid" in row["error"]
    assert "deploy_bridge.ps1 -Remove" in row["error"]


# ------------------------------------------------------------- the probe ---

def test_an_unanswerable_probe_counts_as_alive(tmp_path, monkeypatch):
    """A probe that cannot run has proved NOTHING, and this function exists to
    prove the process gone. No `tasklist`, no marker."""
    def boom(*a, **k):
        raise FileNotFoundError("tasklist")

    monkeypatch.setattr(soak.subprocess, "run", boom)
    image = soak.pid_image(31448)
    assert image is not None and "probe failed" in image
    assert "FileNotFoundError" in image


def test_a_nonzero_probe_exit_counts_as_alive(monkeypatch):
    monkeypatch.setattr(
        soak.subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 1, "", "denied"))
    assert "probe exited 1" in (soak.pid_image(31448) or "")


def test_a_pid_is_not_matched_inside_a_longer_number(monkeypatch):
    """`3144` must not match the row for `31448`. The pid is matched inside
    its own quotes, which is why the CSV format is asked for."""
    rows = '"SlayTheSpire2.exe","31448","Console","1","1,234,567 K"\n'
    monkeypatch.setattr(
        soak.subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 0, rows, ""))
    assert soak.pid_image(31448) == "SlayTheSpire2.exe"
    assert soak.pid_image(3144) is None


# ------------------------------------------------ the watchdog's own marker --

def test_the_hang_watchdog_proves_its_kill_too(tmp_path, table):
    """`halt_spin`'s row is a REVERTED marker on the same entry, written by a
    different caller. One proof function, both callers (`_kill_and_prove`)."""
    s = _session(tmp_path, 31448)
    table.alive[31448] = "SlayTheSpire2.exe"
    with pytest.raises(RuntimeError) as caught:
        s._kill_and_prove()
    assert "STILL ALIVE" in str(caught.value)

    table.alive.clear()
    assert s._kill_and_prove() == "pid 31448 verified gone"
