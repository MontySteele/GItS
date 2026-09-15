"""`EB-766`: telling a STALLED boot from a slow one, without a game.

The fairness read of 2026-09-15 launched 30 games: 24 reached the menu in
about 20 s and 6 blew the whole scaled EB-763 budget -- up to 426 s each,
spent on a process that was alive, answering `GET /`, and never going to
answer `/api/v1/singleplayer` again. The judgment that separates those two
populations is what costs a night when it is wrong, so it is a pure function
(`soak_shape.boot_stall_verdict`) and it is exercised here rather than by
hanging a real game.

Nothing in this file launches, kills or waits on anything: the wire is a
double, the log is a file in `tmp_path`, and the clock is fake, so the whole
module runs in milliseconds.
"""

import pytest

from understudy import soak, soak_session
from understudy.soak_shape import (BOOT_STALL_AFTER_S,
                                   BOOT_STALL_LOG_QUIET_S, BOOT_STALL_RETRIES,
                                   PROFILE_READY_MARKER, RELAUNCH_DEAD_GAP_S,
                                   boot_stall_verdict)


# ---------------------------------------------------------- the verdict ---

def test_a_boot_inside_the_fuse_is_never_a_stall():
    """The fuse is 45 s because the slowest good boot measured was 27.4 s. A
    watchdog that fired inside that window would be killing games that were
    about to come up."""
    assert not boot_stall_verdict(
        elapsed_s=BOOT_STALL_AFTER_S - 0.1, health_ok=True, state_recent=False,
        marker_seen=False, log_quiet_s=999)


def test_a_state_endpoint_that_is_still_answering_is_not_this_defect():
    """The stall is the game thread wedged behind `/api/v1/singleplayer`
    (EB-489's shape). A state endpoint that is STILL ANSWERING is a game that
    is merely still booting, and a relaunch would throw away its progress."""
    assert not boot_stall_verdict(
        elapsed_s=600, health_ok=True, state_recent=True, marker_seen=False,
        log_quiet_s=999)


def test_a_state_endpoint_that_answered_once_and_went_quiet_is_a_stall():
    """The 2026-09-15 miss, at the verdict. `state_recent` used to be
    `ever_state`, a latch -- and `wait_for_menu` documents the pre-menu answer
    that closes it at ~20 s, before the 45 s fuse is ever consulted. So the
    fuse could not fire on the one shape it was written for."""
    assert boot_stall_verdict(
        elapsed_s=600, health_ok=True, state_recent=False, marker_seen=False,
        log_quiet_s=999)


def test_a_silent_root_endpoint_is_a_different_failure_and_gets_no_relaunch():
    """`GET /` is answered on the ThreadPool worker that took the request, so
    its silence means the process or the wire is gone -- not that the game
    thread is wedged. Relaunching on that reading would paper over a crash."""
    assert not boot_stall_verdict(
        elapsed_s=600, health_ok=False, state_recent=False, marker_seen=False,
        log_quiet_s=999)


def test_the_marker_absent_at_the_fuse_is_a_stall_even_with_a_growing_log():
    """`Profile-scoped data path initialized` lands after the boot has
    rewritten the whole run-history store. Past the fuse with a live root
    endpoint, a dead state endpoint and no marker, the boot is wedged."""
    assert boot_stall_verdict(
        elapsed_s=BOOT_STALL_AFTER_S, health_ok=True, state_recent=False,
        marker_seen=False, log_quiet_s=0.0)


def test_a_marker_reached_and_a_log_gone_quiet_is_a_stall():
    """The other half of the OR: the profile came up and then everything
    stopped, which is what the lost boots looked like on the wire."""
    assert boot_stall_verdict(
        elapsed_s=BOOT_STALL_AFTER_S, health_ok=True, state_recent=False,
        marker_seen=True, log_quiet_s=BOOT_STALL_LOG_QUIET_S)


def test_a_marker_reached_and_a_log_still_growing_is_only_slow():
    """A boot that is still writing store lines is still working, and the
    EB-763 budget -- not a kill -- is what it is owed."""
    assert not boot_stall_verdict(
        elapsed_s=BOOT_STALL_AFTER_S, health_ok=True, state_recent=False,
        marker_seen=True, log_quiet_s=BOOT_STALL_LOG_QUIET_S - 0.1)


# ------------------------------------------------------------- the wire ---

class FakeWire:
    """The three calls the boot watch makes, and a script for each."""

    class BridgeError(Exception):
        pass

    def __init__(self, states=(), healthy=True, error="timed out"):
        self.states = list(states)
        self.healthy = healthy
        self.error = error
        self.health_calls = 0

    def get_state(self):
        if not self.states:
            raise self.BridgeError(self.error)
        nxt = self.states.pop(0)
        if nxt is None:
            raise self.BridgeError(self.error)
        return nxt

    def health(self):
        self.health_calls += 1
        if not self.healthy:
            raise self.BridgeError("bridge unreachable")
        return {"status": "ok"}

    def use(self, instance):
        pass

    def current_label(self):
        return "lane0"


class FakeClock:
    """A stand-in for the `time` module: `sleep` moves the clock, nothing
    waits. The boot watch reads `time.time`, the dead gap reads
    `time.monotonic`, and both must advance together."""

    def __init__(self):
        self.now = 1000.0
        self.slept = []

    def time(self):
        return self.now

    def monotonic(self):
        return self.now

    def sleep(self, s):
        self.slept.append(s)
        self.now += s


MENU = {"state_type": "menu", "menu_screen": "main", "options": ["Embark"]}


@pytest.fixture
def clock(monkeypatch):
    c = FakeClock()
    monkeypatch.setattr(soak_session, "time", c)
    # THE DEAD-GAP CLOCK IS ZEROED WITH THE CLOCK ITSELF, and that is an
    # order-dependence fix rather than tidiness: `_last_kill_at` is a
    # process-wide monotonic reading, and `test_eb231_teardown_pid.py` drives
    # the real `Session._kill` -- which sets it to a REAL monotonic reading
    # some hours larger than this fake clock's 1000.0. A dead-gap test that
    # ran after that file read a kill in its own future and slept. Sorted
    # before this module by filename, so the whole suite saw it and this
    # module alone did not.
    monkeypatch.setattr(soak_session, "_last_kill_at", None, raising=False)
    return c


@pytest.fixture
def session(tmp_path, monkeypatch):
    """A `Session` built the way the harness's other doubles are: through
    `__new__`, so no game directory, no ledger file and no launch exist."""
    s = soak.Session.__new__(soak.Session)
    s.stamp = "20260915-0001"
    s.instance = None
    s.proc = None
    s.dir = tmp_path / "game"
    s._launch_entry = None
    s.ledger = soak.Reversibility(tmp_path / "ledger.json")
    log = tmp_path / "appdata" / "SlayTheSpire2" / "logs" / "godot.log"
    log.parent.mkdir(parents=True)
    log.write_text("[INFO] OVERWRITING cloud saves with local saves.\n",
                   encoding="utf-8")
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    s._test_log = log
    # The dead-gap clock is process-wide, so a test that does not mean to
    # exercise it starts from "nothing has been killed".
    monkeypatch.setattr(soak_session, "_last_kill_at", None, raising=False)
    return s


# -------------------------------------------------------- the boot watch ---

def test_a_good_boot_returns_the_menu_and_never_relaunches(
        session, clock, monkeypatch):
    """The compatibility half: a game that comes up is untouched by any of
    this, and the fuse costs it nothing but a `GET /` it never makes."""
    wire = FakeWire(states=[None, MENU])
    monkeypatch.setattr(soak, "bridge", wire)
    session._launch = lambda: pytest.fail("a good boot must not relaunch")
    assert session.wait_for_menu(300.0) is MENU
    assert wire.health_calls == 0, "the fuse never fired, so nobody asked"


def test_a_stall_is_killed_and_relaunched_and_the_second_boot_is_kept(
        session, clock, monkeypatch):
    """The row's whole point. The first process answers `GET /` forever and
    `/api/v1/singleplayer` never; at the fuse it is killed and relaunched, and
    the relaunched game's menu is what the caller gets -- 45 s in, not 426."""
    wire = FakeWire(states=[])
    monkeypatch.setattr(soak, "bridge", wire)
    killed = []
    session._kill = lambda: killed.append(clock.now)

    def _relaunch():
        wire.states = [MENU]
    session._launch = _relaunch

    assert session.wait_for_menu(426.0) is MENU
    assert len(killed) == 1, "exactly one relaunch"
    assert killed[0] - 1000.0 >= BOOT_STALL_AFTER_S
    assert killed[0] - 1000.0 < 2 * BOOT_STALL_AFTER_S, "and it fired early"
    assert wire.health_calls >= 1


def test_the_stalled_boots_log_is_copied_aside_before_the_relaunch(
        session, clock, monkeypatch):
    """Godot keeps five logs and rotates on launch, so the evidence for this
    defect is gone by morning unless the relaunch copies it first. The six
    stalled boots of 2026-09-15 have no logs at all, and that is why."""
    wire = FakeWire(states=[])
    monkeypatch.setattr(soak, "bridge", wire)
    monkeypatch.setattr(soak_session, "GODOT_LOG_ARCHIVE",
                        session.dir.parent / "archive")
    session._kill = lambda: None
    session._launch = lambda: wire.states.append(MENU)
    session.wait_for_menu(426.0)
    copies = sorted((session.dir.parent / "archive").glob("*.log"))
    assert [p.name for p in copies] == ["20260915-0001-nopid-stall1.log"]
    assert "OVERWRITING cloud saves" in copies[0].read_text(encoding="utf-8")


def test_the_retries_are_bounded_and_the_last_attempt_keeps_the_budget(
        session, clock, monkeypatch):
    """A machine where the fuse is simply wrong must degrade to today's
    behaviour, not to an infinite relaunch loop: two retries, then the full
    scaled EB-763 budget, then the same `SystemExit` as before."""
    wire = FakeWire(states=[])
    monkeypatch.setattr(soak, "bridge", wire)
    launches = []
    session._kill = lambda: None
    session._launch = lambda: launches.append(clock.now)
    with pytest.raises(SystemExit) as e:
        session.wait_for_menu(426.0)
    assert len(launches) == BOOT_STALL_RETRIES
    assert "within 426s" in str(e.value)
    # The last attempt really did spend the budget rather than the fuse.
    assert clock.now - launches[-1] >= 426.0


def test_giving_up_names_the_last_bridge_read_in_the_message_and_the_log(
        session, clock, monkeypatch, capsys):
    """"bridge unreachable" and "root ok, state endpoint hung" are the same
    `SystemExit` today, and the console that would have told them apart is
    not what gets read the morning after. Both now carry the read."""
    wire = FakeWire(states=[], error="timed out at /api/v1/singleplayer")
    monkeypatch.setattr(soak, "bridge", wire)
    session._kill = lambda: None
    session._launch = lambda: None
    with pytest.raises(SystemExit) as e:
        session.wait_for_menu(426.0)
    assert "timed out at /api/v1/singleplayer" in str(e.value)
    assert "timed out at /api/v1/singleplayer" in capsys.readouterr().out
    assert session.last_boot_read.startswith("bridge connection failed") \
        or "timed out" in session.last_boot_read


def test_a_dead_wire_is_not_relaunched_and_says_so(
        session, clock, monkeypatch):
    """The other reading of the pair. With `GET /` silent too, nothing is
    killed: this is a crash or a wire that is gone, and the budget expires on
    a message that names it."""
    wire = FakeWire(states=[], healthy=False, error="bridge unreachable")
    monkeypatch.setattr(soak, "bridge", wire)
    session._kill = lambda: pytest.fail("a dead wire is not relaunched")
    session._launch = lambda: pytest.fail("a dead wire is not relaunched")
    with pytest.raises(SystemExit) as e:
        session.wait_for_menu(60.0)
    assert "bridge unreachable" in str(e.value)


def test_the_marker_is_read_off_the_real_log_file(session, clock, monkeypatch):
    """The signal is a line in the game's own log, not a mock: a log that has
    reached the profile marker and is still growing is a slow boot and keeps
    its budget."""
    wire = FakeWire(states=[])
    monkeypatch.setattr(soak, "bridge", wire)
    session._kill = lambda: pytest.fail("a growing log is not a stall")
    session._launch = lambda: pytest.fail("a growing log is not a stall")
    original = soak_session._file_size

    def _growing(path):
        # Every look sees more bytes, which is what a boot still writing the
        # remote store looks like.
        _growing.n += 1
        return original(path) + _growing.n
    _growing.n = 0
    monkeypatch.setattr(soak_session, "_file_size", _growing)
    session._test_log.write_text(
        f"[INFO] {PROFILE_READY_MARKER}: user://steam/x\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        session.wait_for_menu(90.0)


def test_the_marker_scan_is_bounded_and_still_finds_the_line(tmp_path):
    """EB-1's spin writes ~1.3 MB/s to this file and once grew it to 2.4 GB in
    half an hour, so the scan reads the TAIL rather than the file -- and the
    boot's ~65 KB of store lines sit comfortably inside it."""
    log = tmp_path / "godot.log"
    log.write_bytes(b"x" * 3_000_000
                    + f"[INFO] {PROFILE_READY_MARKER}: user://steam/x\n"
                    .encode("utf-8"))
    assert soak_session._log_has_marker(log)
    assert not soak_session._log_has_marker(tmp_path / "absent.log")


# ------------------------------------------- the 2026-09-15 stall, twice ---

class Proofs5Wire(FakeWire):
    """LAUNCH 6 OF THE 2026-09-15 DEPLOY PROOFS, on the wire (`git show
    d47d9fcc:review/records/teyvat-proofs-5-2026-09-15.md`).

    `GET /` answers (the root endpoint is served off the ThreadPool worker
    that took the request, so it survives a wedged game thread), and
    `/api/v1/singleplayer` answers ONCE, early, the way every boot's pre-menu
    read does -- `{"state_type": "loading"}`, no options -- and then never
    again. That one answer is the whole defect: it used to latch `ever_state`
    and disarm the fuse for the life of the watch, and the launch spent all
    444 s of its budget in silence.
    """

    def __init__(self):
        super().__init__(states=[{"state_type": "loading",
                                  "menu_screen": None}],
                         healthy=True,
                         error=("bridge connection failed at "
                                "http://localhost:15526/api/v1/singleplayer: "
                                "TimeoutError: timed out"))


def test_the_proofs_5_signal_pattern_is_a_stall_and_fires_at_the_fuse(
        session, clock, monkeypatch, capsys):
    """The exact four signals launch 6 showed, from the entry point EMBARK
    uses -- `Session.setup()`, not `wait_for_menu` reached by hand: health ok,
    the state endpoint silent after one early pre-menu answer, the profile
    marker ABSENT, and a log frozen at 21,753 bytes. The fuse must fire at
    45 s and the relaunch path must be taken."""
    wire = Proofs5Wire()
    monkeypatch.setattr(soak, "bridge", wire)
    monkeypatch.setattr(soak_session, "GODOT_LOG_ARCHIVE",
                        session.dir.parent / "archive")
    monkeypatch.setattr(soak_session.keepawake, "acquire", lambda why: False)
    # THE LOG IS FROZEN, at the size the record read off the archived copy,
    # and it never reaches `Profile-scoped data path initialized`.
    session._test_log.write_bytes(
        b"[INFO] Wrote 20621 bytes to modded/profile1/saves/history/"
        b"1786232408.run in steam remote store\n" * 229)
    assert 21_000 < session._test_log.stat().st_size < 23_000
    assert not soak_session._log_has_marker(session._test_log)

    session.do_setup = True
    killed, launched = [], []
    session._steam_appid = lambda: None
    session._deploy_bridge = lambda: None
    session._menu_budget = lambda: 444.0
    session._speed_on = lambda: None
    session._kill = lambda: killed.append(clock.now)

    def _launch():
        launched.append(clock.now)
        if len(launched) > 1:            # the relaunched game comes up
            wire.states = [MENU]
    session._launch = _launch

    session.setup()

    assert len(launched) == 2, "the stall was relaunched, once"
    assert len(killed) == 1
    stalled_for = killed[0] - launched[0]
    assert stalled_for >= BOOT_STALL_AFTER_S, "the fuse is 45 s"
    assert stalled_for < 2 * BOOT_STALL_AFTER_S, "and not 444"
    assert wire.health_calls >= 1, "the root endpoint was asked"
    out = capsys.readouterr().out
    assert "boot looks STALLED" in out
    assert "marker is ABSENT" in out
    # And the evidence was copied aside before the relaunch rotated it.
    assert (session.dir.parent / "archive").glob("*-stall1.log")


def test_an_http_error_body_is_not_a_state_answer(session, clock, monkeypatch):
    """`bridge._request` returns the JSON of an HTTP 500 rather than raising,
    and `McpMod.HandleGetState` answers 500 with `{"error", "stack_trace"}`
    when the main-thread hop throws. A watch that read that as "the state
    endpoint is alive" would be reading the wedge as health."""
    wire = FakeWire(states=[{"error": "Failed to read game state: ...",
                             "exception_type": "System.NullReferenceException",
                             "stack_trace": "..."}] * 40)
    monkeypatch.setattr(soak, "bridge", wire)
    killed = []
    session._kill = lambda: killed.append(clock.now)
    session._launch = lambda: setattr(wire, "states", [MENU])
    assert session.wait_for_menu(444.0) is MENU
    assert len(killed) == 1, "the error bodies did not disarm the fuse"


def test_a_state_endpoint_answering_every_poll_keeps_its_whole_budget(
        session, clock, monkeypatch):
    """The other direction, and the reason the signal is recency rather than
    silence-since-launch: a slow boot whose bridge answers each poll is still
    booting, and killing it would throw the progress away."""
    wire = FakeWire(states=[{"state_type": "loading", "menu_screen": None}]
                    * 500)
    monkeypatch.setattr(soak, "bridge", wire)
    session._kill = lambda: pytest.fail("a live state endpoint is not a stall")
    session._launch = lambda: pytest.fail("nor is it relaunched")
    with pytest.raises(SystemExit):
        session.wait_for_menu(90.0)


def test_the_fuse_says_which_guard_refused_when_it_does_not_fire(
        session, clock, monkeypatch, capsys):
    """The record's own ask: 444 s of silence is what made launch 6 expensive
    to diagnose. Past the deadline with no stall called, one DIAG line names
    every signal the verdict saw."""
    wire = FakeWire(states=[], healthy=False)
    monkeypatch.setattr(soak, "bridge", wire)
    session._kill = lambda: None
    session._launch = lambda: None
    with pytest.raises(SystemExit):
        session.wait_for_menu(120.0)
    out = capsys.readouterr().out
    assert out.count("boot fuse deadline") == 1, "once, not every poll"
    assert "health_ok=False" in out and "state_recent=False" in out


def test_embark_reaches_the_menu_only_through_session_setup():
    """Structural, and the reason the stall test above drives `setup()`: the
    fuse has to be on the path EMBARK takes, not only on the one `soak.py`
    takes. `understudy/embark.py` must not grow a second menu wait."""
    src = open(soak_session.__file__.replace("soak_session.py", "embark.py"),
               encoding="utf-8").read()
    assert "session.setup()" in src
    assert "wait_for_menu" not in src, \
        "embark waits for the menu through setup(), and nowhere else"


# --------------------------------------------------------- the dead gap ---

def test_the_first_launch_of_a_process_waits_for_nothing(clock):
    """Nothing has been killed, so there is no teardown to wait out."""
    assert soak_session.await_dead_gap() == 0.0
    assert clock.slept == []


def test_a_launch_right_after_a_kill_waits_out_steams_teardown(clock):
    """3 of the 8 launches that came ~1 s after killing a short-lived game
    stalled; 0 of the 12 that followed a longer session did."""
    soak_session.note_kill()
    clock.now += 1.1
    slept = soak_session.await_dead_gap()
    assert slept == pytest.approx(RELAUNCH_DEAD_GAP_S - 1.1)
    assert clock.slept == [pytest.approx(RELAUNCH_DEAD_GAP_S - 1.1)]


def test_a_launch_that_is_already_late_enough_waits_no_longer(clock):
    """The gap is a floor, not a tax: a session that ran for minutes pays
    nothing."""
    soak_session.note_kill()
    clock.now += RELAUNCH_DEAD_GAP_S + 5
    assert soak_session.await_dead_gap() == 0.0
    assert clock.slept == []


def test_the_gap_is_the_launchers_and_not_each_callers(session, clock,
                                                       monkeypatch):
    """Structural: `_launch` owes the gap, so `restart`, the stall retry and a
    second `setup` in the same process all pay it without remembering to."""
    src = (soak_session.__file__ and
           open(soak_session.__file__, encoding="utf-8").read())
    launch = src.split("    def _launch(self)", 1)[1].split(
        "\n    def ", 1)[0]
    assert "await_dead_gap()" in launch
    kill = src.split("    def _kill(self)", 1)[1].split("\n    def ", 1)[0]
    assert "note_kill()" in kill


# ------------------------------------------------------- the log archive ---

def test_teardown_copies_the_log_and_never_moves_it(session, clock,
                                                    monkeypatch):
    """A COPY: the live log belongs to the game, and a harness that moved it
    would break the thing it was trying to read."""
    monkeypatch.setattr(soak_session, "GODOT_LOG_ARCHIVE",
                        session.dir.parent / "archive")
    dest = session.archive_log()
    assert dest is not None and dest.is_file()
    assert session._test_log.is_file(), "the game's own log is left alone"
    assert dest.read_text(encoding="utf-8") == session._test_log.read_text(
        encoding="utf-8")


def test_an_oversized_log_is_archived_head_and_tail_with_a_marker(
        session, clock, monkeypatch, capsys):
    """`EB-766`. The Punch-Off VFX spin wrote a 2.56 GB `godot.log` in about
    two minutes and this method copied every byte of it. Past the cap the head
    and the tail are kept, the middle is dropped, and one line says so. The
    dials are moved down here so the test writes kilobytes rather than
    megabytes; the arithmetic is the same."""
    monkeypatch.setattr(soak_session, "GODOT_LOG_ARCHIVE",
                        session.dir.parent / "archive")
    monkeypatch.setattr(soak_session, "ARCHIVE_LOG_MAX_BYTES", 800)
    monkeypatch.setattr(soak_session, "ARCHIVE_LOG_HEAD_BYTES", 100)
    monkeypatch.setattr(soak_session, "ARCHIVE_LOG_TAIL_BYTES", 400)
    head = b"H" * 100
    middle = b'ERROR: Parameter "particles" is null\n' * 400
    tail = b"T" * 400
    session._test_log.write_bytes(head + middle + tail)
    size = session._test_log.stat().st_size

    dest = session.archive_log()

    assert dest is not None
    body = dest.read_bytes()
    assert body.startswith(head)
    assert body.endswith(tail)
    assert len(body) < size, "the archive is smaller than the log"
    assert b"omitted by the archiver" in body
    assert str(size - 500).encode() in body, "it names the bytes dropped"
    assert middle not in body, "the repeated spin lines are gone"
    assert session._test_log.stat().st_size == size, "the game's log is whole"
    out = capsys.readouterr().out
    assert "archived TRUNCATED" in out and str(size) in out


def test_a_log_inside_the_cap_is_still_copied_byte_for_byte(
        session, clock, monkeypatch, capsys):
    """The cap is a ceiling, not a policy: an ordinary 400 KB boot log is
    archived exactly as it always was, and nothing is printed about it."""
    monkeypatch.setattr(soak_session, "GODOT_LOG_ARCHIVE",
                        session.dir.parent / "archive")
    session._test_log.write_bytes(b"[INFO] boot\n" * 1000)
    dest = session.archive_log()
    assert dest.read_bytes() == session._test_log.read_bytes()
    assert "TRUNCATED" not in capsys.readouterr().out


def test_a_missing_log_is_not_an_error(session, clock, monkeypatch):
    """Called from a teardown whose whole contract is that every step runs."""
    monkeypatch.setattr(soak_session, "GODOT_LOG_ARCHIVE",
                        session.dir.parent / "archive")
    session._test_log.unlink()
    assert session.archive_log() is None


def test_the_archive_directory_is_gitignored():
    """The engine's raw output on this machine, kept so a failure can be read
    back -- the same rule blindplay/ and seat/ next door carry."""
    from understudy.soak_shape import GODOT_LOG_ARCHIVE
    ignore = GODOT_LOG_ARCHIVE / ".gitignore"
    assert ignore.is_file(), "understudy/logs/godot/ needs its own .gitignore"
    body = ignore.read_text(encoding="utf-8")
    assert "*" in body and "!.gitignore" in body
