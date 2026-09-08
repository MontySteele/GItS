"""`EB-691`: the blind lane's watchdog, tested without a game and without a
storm.

The failure this defends against was found by hand after fifteen minutes and
19 GB of `godot.log`, and it can only be produced live by walking a `?` node
into the Punch Off room. So the judgement is exercised here instead: a FAKE
log that grows past the bar and a FAKE process reading trip it, and a quiet
lane does not.

NOTHING BELOW IS EVIDENCE ABOUT THE GAME. It is evidence about whether the
watchdog can tell a storm from an ordinary lane, and about what the seat is
handed when it fires.
"""

from __future__ import annotations

import json

import pytest

from understudy import lanewatch

#: The 2026-09-08 lane-2 storm, on the two numbers that were measured: 19 GB
#: of log in about fifteen minutes, and a 3.2 GB process.
LIVE_FLOOD_BYTES_PER_S = 19_000_000_000 / (15 * 60)
LIVE_PROC_BYTES = 3_200_000_000


@pytest.fixture()
def lane(tmp_path, monkeypatch):
    """A lane whose store, sidecars and ledger are all under `tmp_path`."""
    monkeypatch.setattr(lanewatch, "_STORE_DIR", tmp_path)
    monkeypatch.setattr(lanewatch, "LOG_DIR", tmp_path)
    monkeypatch.delenv(lanewatch.LANE_ENV, raising=False)
    return "2"


def _sidecar(tmp_path, lane="lane2", pid=4242, appdata="C:/lane2"):
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps(
        [{"change": "Launched `SlayTheSpire2.exe` directly",
          "state": "APPLIED", "pid": pid}]), encoding="utf-8")
    (tmp_path / "embark-20260908-000001.json").write_text(json.dumps(
        {"stamp": "20260908-000001", "instance": lane, "hold": False,
         "appdata": appdata, "ledger": str(ledger)}), encoding="utf-8")


def _sizes(*values):
    """A `sizer` that answers the given sizes in order, then repeats the
    last."""
    seen = list(values)

    def _go(_path):
        return seen.pop(0) if len(seen) > 1 else seen[0]
    return _go


def _memory(value):
    return lambda _pid, **_kw: value


# ----------------------------------------------------------- the bars ------

def test_the_live_storm_is_comfortably_over_both_bars():
    """Both bars are set from one live observation, so the observation is the
    test. A threshold the measured storm did not clear would be a watchdog
    watching the wrong thing."""
    assert LIVE_FLOOD_BYTES_PER_S > lanewatch.LOG_RATE_BYTES_PER_S * 4
    assert LIVE_PROC_BYTES > lanewatch.PROC_BYTES


def test_the_flood_bar_is_hangwatchs_own_number():
    """One storm, one bar. A second copy could be retuned on its own and leave
    the two watchdogs disagreeing about what a flood is."""
    from understudy import hangwatch
    assert lanewatch.LOG_RATE_BYTES_PER_S == hangwatch.FLOOD_BYTES_PER_S


# ------------------------------------------------------- a quiet lane ------

def test_a_quiet_lane_is_not_touched(tmp_path, lane):
    """An ordinary session gains single-digit KB per second and a game holds
    about a gigabyte. Neither is a signal, and a watchdog that fired on them
    is a watchdog somebody turns off."""
    _sidecar(tmp_path)
    lanewatch.arm(lane)
    now = 1000.0
    quiet = lanewatch.check(lane, now=now, sizer=_sizes(1_000_000),
                            memory=_memory(1_000_000_000))
    assert not quiet.dead
    # 30 s later, 90 KB of ordinary logging: 3 KB/s.
    later = lanewatch.check(lane, now=now + 30.0,
                            sizer=_sizes(1_090_000),
                            memory=_memory(1_100_000_000))
    assert not later.dead
    assert later.evidence["log_bytes_per_s"] == pytest.approx(3000.0)


def test_a_long_quiet_gap_is_not_a_flood(tmp_path, lane):
    """The seat thinks for minutes between commands. Absolute growth over such
    a gap is large for an ordinary lane too, which is why the RATE is the
    signal and the growth floor is only a noise floor under it."""
    _sidecar(tmp_path)
    lanewatch.arm(lane)
    lanewatch.check(lane, now=0.0, sizer=_sizes(0), memory=_memory(None))
    # An hour at 5 KB/s: 18 MB grown, nine times the floor, and still quiet.
    v = lanewatch.check(lane, now=3600.0, sizer=_sizes(18_000_000),
                        memory=_memory(None))
    assert not v.dead


def test_a_rotated_log_reads_as_no_reading(tmp_path, lane):
    """The game writes a fresh `godot.log` per launch. A shrinking file is the
    watchdog looking at a different file, not a flood running backwards."""
    _sidecar(tmp_path)
    lanewatch.arm(lane)
    lanewatch.check(lane, now=0.0, sizer=_sizes(5_000_000_000),
                    memory=_memory(None))
    v = lanewatch.check(lane, now=10.0, sizer=_sizes(4096),
                        memory=_memory(None))
    assert not v.dead


def test_two_commands_a_moment_apart_cannot_divide_into_a_flood(tmp_path,
                                                                lane):
    """An `observe` the seat follows immediately with an `act`. A few hundred
    KB flushed in a fraction of a second is a rate that looks like a storm and
    is not one."""
    _sidecar(tmp_path)
    lanewatch.arm(lane)
    lanewatch.check(lane, now=0.0, sizer=_sizes(0), memory=_memory(None))
    v = lanewatch.check(lane, now=0.2, sizer=_sizes(400_000),
                        memory=_memory(None))
    assert not v.dead


# --------------------------------------------------------- the storm -------

def test_a_growing_fake_log_trips_the_watchdog(tmp_path, lane):
    """The synthetic storm: the log grows at the measured rate between two
    commands sixty seconds apart, which is the gap the live seat's retries
    were at."""
    _sidecar(tmp_path)
    lanewatch.arm(lane)
    lanewatch.check(lane, now=0.0, sizer=_sizes(10_000_000),
                    memory=_memory(1_000_000_000))
    grown = int(LIVE_FLOOD_BYTES_PER_S * 60)
    v = lanewatch.check(lane, now=60.0, sizer=_sizes(10_000_000 + grown),
                        memory=_memory(1_000_000_000))
    assert v.dead
    assert "godot.log grew" in v.reason
    assert v.line().startswith(lanewatch.BLOCKED)


def test_a_fat_process_trips_the_watchdog_on_its_own(tmp_path, lane):
    """The second signal is independent: a machine whose log this cannot read
    still has the memory reading, and vice versa."""
    _sidecar(tmp_path)
    lanewatch.arm(lane)
    v = lanewatch.check(lane, now=0.0, sizer=_sizes(None),
                        memory=_memory(LIVE_PROC_BYTES))
    assert v.dead
    assert "holds 3.2 GB" in v.reason


def test_an_unreadable_memory_reading_is_not_a_death(tmp_path, lane):
    """`None` is "cannot tell" -- no `tasklist`, an exited pid, a locale this
    does not parse -- and it must remove the signal, never read as a zero or
    as a hang."""
    _sidecar(tmp_path)
    lanewatch.arm(lane)
    v = lanewatch.check(lane, now=0.0, sizer=_sizes(None),
                        memory=_memory(None))
    assert not v.dead


# -------------------------------------------------- the timeout counter ----

def test_two_state_timeouts_with_health_answering_end_the_lane(tmp_path,
                                                               lane):
    _sidecar(tmp_path)
    lanewatch.arm(lane)
    assert lanewatch.record_state_timeout(lane, health_answers=True) == 1
    v = lanewatch.check(lane, now=0.0, sizer=_sizes(None),
                        memory=_memory(None))
    assert not v.dead, "one timeout is a slow room load"
    assert lanewatch.record_state_timeout(lane, health_answers=True) == 2
    v = lanewatch.check(lane, now=1.0, sizer=_sizes(None),
                        memory=_memory(None))
    assert v.dead
    assert "timed out 2 times running" in v.reason


def test_a_timeout_with_health_silent_is_not_charged(tmp_path, lane):
    """A root endpoint that has also gone quiet is an ordinary unreachable
    bridge, or a process that exited. Different failure, different answer."""
    _sidecar(tmp_path)
    lanewatch.arm(lane)
    lanewatch.record_state_timeout(lane, health_answers=False)
    lanewatch.record_state_timeout(lane, health_answers=False)
    v = lanewatch.check(lane, now=0.0, sizer=_sizes(None),
                        memory=_memory(None))
    assert not v.dead


def test_a_state_read_that_answers_resets_the_count(tmp_path, lane):
    """They have to be CONSECUTIVE: a lane that timed out once an hour ago and
    has been playing since is not stalled."""
    _sidecar(tmp_path)
    lanewatch.arm(lane)
    lanewatch.record_state_timeout(lane, health_answers=True)
    lanewatch.record_state_ok(lane)
    lanewatch.record_state_timeout(lane, health_answers=True)
    v = lanewatch.check(lane, now=0.0, sizer=_sizes(None),
                        memory=_memory(None))
    assert not v.dead


def test_a_timeout_is_told_from_a_refused_connection():
    assert lanewatch.is_timeout(TimeoutError("timed out"))
    assert lanewatch.is_timeout(RuntimeError(
        "bridge connection failed at http://localhost:15528: "
        "TimeoutError: timed out"))
    assert not lanewatch.is_timeout(RuntimeError(
        "bridge unreachable at http://localhost:15528: "
        "[WinError 10061] connection refused"))


# ------------------------------------------------------ what happens next --

def test_the_death_tears_the_lane_down_once_and_stays_dead(tmp_path, lane):
    """The teardown runs on the command that FINDS the storm. A second command
    is told the same thing -- the process is gone by then, so re-reading its
    log would find it quiet and wave the seat back on."""
    _sidecar(tmp_path)
    lanewatch.arm(lane)
    torn: list = []
    lanewatch.check(lane, now=0.0, sizer=_sizes(0), memory=_memory(None))
    line = lanewatch.guard(lane, now=60.0, teardown=torn.append,
                           sizer=_sizes(int(LIVE_FLOOD_BYTES_PER_S * 60)),
                           memory=_memory(None))
    assert line.startswith(lanewatch.BLOCKED)
    assert torn == [lane]
    again = lanewatch.guard(lane, now=120.0, teardown=torn.append,
                            sizer=_sizes(0), memory=_memory(None))
    assert again.startswith(lanewatch.BLOCKED)
    assert torn == [lane], "the teardown does not run twice"


def test_a_failed_teardown_still_stops_the_seat(tmp_path, lane):
    """The lane is dead either way, and the seat's stop must not depend on the
    undo succeeding."""
    _sidecar(tmp_path)
    lanewatch.arm(lane)
    lanewatch.check(lane, now=0.0, sizer=_sizes(0), memory=_memory(None))

    def _boom(_lane):
        return "TEARDOWN FAILED (EmbarkError: no ledger)"
    line = lanewatch.guard(lane, now=60.0, teardown=_boom,
                           sizer=_sizes(int(LIVE_FLOOD_BYTES_PER_S * 60)),
                           memory=_memory(None))
    assert line.startswith(lanewatch.BLOCKED)
    assert "TEARDOWN FAILED" in line


def test_arming_clears_a_previous_games_cursor(tmp_path, lane):
    """An embark is a new run. A cursor left from the last game would have the
    first `observe` compare against a log that no longer exists."""
    _sidecar(tmp_path)
    lanewatch.arm(lane)
    lanewatch.check(lane, now=0.0, sizer=_sizes(9_000_000_000),
                    memory=_memory(None))
    lanewatch.arm(lane)
    row = lanewatch.read_store(lane)
    assert row["log_bytes"] is None and not row["dead"]


# ------------------------------------------------- reading the machine -----

def test_the_pid_and_the_log_come_off_the_lanes_own_embark(tmp_path, lane):
    """With two games up, an image-name reading answers about both. The pid is
    the one the lane's own launch wrote to its ledger (`EB-231`), and the log
    is under that lane's `APPDATA`."""
    _sidecar(tmp_path, lane="lane2", pid=4242, appdata=str(tmp_path / "l2"))
    _sidecar(tmp_path)          # rewritten, same lane -- newest wins
    row = lanewatch.sidecar_row(lane)
    assert lanewatch.lane_pid(lane, row) == 4242
    log = lanewatch.lane_log_path(lane, row)
    assert log is not None and log.parts[-3:] == lanewatch.LOG_RELATIVE


def test_another_lanes_embark_is_not_read(tmp_path, lane):
    _sidecar(tmp_path, lane="lane1", pid=99)
    assert lanewatch.sidecar_row(lane) == {}
    assert lanewatch.lane_pid(lane) is None


def test_a_hold_embark_names_no_process(tmp_path, lane):
    """A `--hold` attached to a game somebody else launched: it wrote no
    launch row, so there is no pid of ours in its ledger and nothing here may
    claim one."""
    ledger = tmp_path / "held.json"
    ledger.write_text("[]", encoding="utf-8")
    (tmp_path / "embark-20260908-000009.json").write_text(json.dumps(
        {"instance": "lane2", "hold": True, "ledger": str(ledger)}),
        encoding="utf-8")
    assert lanewatch.sidecar_row(lane) == {}


def test_the_working_set_is_parsed_out_of_tasklists_csv():
    row = ('"SlayTheSpire2.exe","20792","Console","1","3,355,444 K"\n')
    assert lanewatch.working_set_bytes(20792, query=lambda _pid: row) == (
        3_355_444 * 1024)


def test_unparseable_tasklist_output_is_not_a_reading():
    for out in ("", "INFO: No tasks are running which match the criteria.",
                '"a","b"'):
        assert lanewatch.working_set_bytes(7, query=lambda _pid, o=out: o) \
            is None


# ------------------------------------------------------- the two doors ----

def test_both_blind_commands_stop_on_a_dead_lane(monkeypatch, capsys):
    """THE WIRING, not the module. The seat drives exactly `observe` and
    `act`, one process per call, and a watchdog wired into neither is the
    defect this row exists for."""
    from understudy import blindplay
    monkeypatch.setattr(lanewatch, "guard",
                        lambda *a, **k: f"{lanewatch.BLOCKED} (a storm)")
    for argv in (["observe"], ["act", "end turn"]):
        assert blindplay.main(argv) == lanewatch.EXIT_LANE_DEAD
        out = capsys.readouterr().out
        assert out.startswith(lanewatch.BLOCKED), argv


def test_a_state_timeout_is_counted_where_the_command_meets_it(monkeypatch):
    """The third signal has exactly one live surface: the state read the two
    commands make. A timeout there with health still answering is charged; a
    refused connection is re-raised untouched, because a process that is GONE
    is a different failure with a different answer."""
    from understudy import blindplay
    args = type("A", (), {"raw_file": "", "dry_run": False})()
    charged: list = []
    monkeypatch.setattr(lanewatch, "record_state_timeout",
                        lambda *a, **k: charged.append(k) or 1)
    monkeypatch.setattr(lanewatch, "guard", lambda *a, **k: "")
    monkeypatch.setattr(blindplay.bridge, "health", lambda: {"status": "ok"})

    def _timeout(_args):
        raise blindplay.bridge.BridgeError(
            "bridge connection failed: TimeoutError: timed out")
    monkeypatch.setattr(blindplay, "_load_state", _timeout)
    with pytest.raises(blindplay.bridge.BridgeError):
        blindplay._live_load(args)
    assert charged == [{"health_answers": True}]

    def _refused(_args):
        raise blindplay.bridge.BridgeError("bridge unreachable: refused")
    monkeypatch.setattr(blindplay, "_load_state", _refused)
    with pytest.raises(blindplay.bridge.BridgeError):
        blindplay._live_load(args)
    assert len(charged) == 1


def test_the_second_timeout_reaches_the_seat_as_a_dead_lane(monkeypatch):
    from understudy import blindplay
    args = type("A", (), {"raw_file": "", "dry_run": False})()
    monkeypatch.setattr(lanewatch, "record_state_timeout", lambda *a, **k: 2)
    monkeypatch.setattr(lanewatch, "guard",
                        lambda *a, **k: f"{lanewatch.BLOCKED} (stalled)")
    monkeypatch.setattr(blindplay.bridge, "health", lambda: {"status": "ok"})
    monkeypatch.setattr(blindplay, "_load_state", lambda _a: (_ for _ in ()
                                                              ).throw(
        TimeoutError("timed out")))
    with pytest.raises(blindplay.LaneDead) as caught:
        blindplay._live_load(args)
    assert str(caught.value).startswith(lanewatch.BLOCKED)


def test_a_saved_state_is_not_watched(tmp_path, monkeypatch, capsys):
    """`--raw-file` touches no game: a fixture renders whatever the lane is
    doing, and refusing it would make a recorded frame unreadable after the
    round it came from ended."""
    from understudy import blindplay
    asked: list = []
    monkeypatch.setattr(lanewatch, "guard",
                        lambda *a, **k: asked.append(1) or "dead")
    raw = tmp_path / "state.json"
    raw.write_text(json.dumps({"state_type": "menu", "options": []}),
                   encoding="utf-8")
    blindplay.main(["observe", "--raw-file", str(raw)])
    capsys.readouterr()
    assert asked == []


def test_a_dead_lane_is_reported_ahead_of_the_action_budget(monkeypatch,
                                                            capsys):
    """A dead lane reported as `budget reached` is a true sentence about the
    wrong problem, and the seat's record would carry the wrong stop."""
    from understudy import blindplay
    monkeypatch.setattr(lanewatch, "guard",
                        lambda *a, **k: f"{lanewatch.BLOCKED} (a storm)")
    monkeypatch.setattr(blindplay, "budget_spent", lambda *a, **k: (99, 10))
    assert blindplay.main(["act", "end turn"]) == lanewatch.EXIT_LANE_DEAD
    assert blindplay.BUDGET_REACHED not in capsys.readouterr().out


def test_lane_tag_matches_the_blind_modules_own_spelling():
    """`--lane 2`, `GITS_LANE=2` and `GITS_LANE=lane2` are one lane, and the
    two stores have to agree on the filename or a watch is armed on one lane
    and read on another."""
    from understudy import blindplay_shape
    for value in (2, "2", "lane2", "LANE2"):
        assert lanewatch.lane_tag(value) == blindplay_shape.lane_tag(value)
    assert lanewatch.LANE_ENV == blindplay_shape.LANE_ENV
