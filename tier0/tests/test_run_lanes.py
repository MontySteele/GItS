"""A LANE FOR THE WHOLE-RUN HARNESS: `--lane N`, `GITS_LANE`, and the hazards.

`EB-206` gave the staged-turn funnel two game instances out of one install
(`local_tester --lanes 2`). The whole-run entry points -- `embark`, `soak`,
`scenario run` and the three `blindplay` commands -- had no way to say which
game they meant, so an agent's run could only ever play in the one instance the
owner was already playing in. This is the door: one flag on the three commands
that launch a game, and one environment variable for the three that attach to
one.

NOTHING HERE LAUNCHES A GAME, and everything here is a fact that has to be
true before one is worth launching: which port a command talks to, which user
tree it reads, which halves of the SHARED install it may write, and what a
lane-0 command does (exactly what it did before, byte for byte, file names
included).
"""

from __future__ import annotations

import json
import shutil
import threading
from pathlib import Path

import pytest

from understudy import bridge, embark, instances, scenario, soak


@pytest.fixture(autouse=True)
def _unbound():
    """Every test starts on an unbound thread and leaves it that way.

    `bridge.use` is thread-local and pytest runs these in one thread, so a
    test that bound a lane and did not put it back would hand the next test a
    lane it never asked for -- which is the shape of the very bug this build
    exists to prevent, in the test suite instead of in a round.
    """
    bridge.use_default()
    yield
    bridge.use_default()


# ------------------------------------------------------- naming one lane ---

def test_a_lane_is_spelled_the_same_way_at_every_door():
    """`--lane 1`, `GITS_LANE=1` and `GITS_LANE=lane1` are one request."""
    assert instances.label_for(1) == "lane1"
    assert instances.label_for("1") == "lane1"
    assert instances.label_for("lane1") == "lane1"
    assert instances.label_for(0) == instances.DEFAULT_LABEL == "lane0"


def test_a_lane_that_does_not_exist_is_refused_by_name():
    """Refused HERE rather than by an unreachable bridge on a port nobody is
    listening on -- which is a true sentence about the wrong problem."""
    for bad in (9, "lane9", "banana", ""):
        with pytest.raises(ValueError) as excinfo:
            instances.label_for(bad)
        assert "lane0" in str(excinfo.value)
        assert "lane1" in str(excinfo.value)


def test_the_default_lane_is_no_lane_at_all():
    """`cli_lane(0)` is `None`, and the difference is not cosmetic: an
    instance binds the thread, stamps a `-lane0` infix into every run log and
    writes an `appdata` into the record. Lane 0 must do none of that, or "the
    default is unchanged" is a claim no file on disk agrees with."""
    assert instances.cli_lane(0) is None
    assert instances.cli_lane("lane0") is None
    assert instances.cli_lane(1, game_dir=Path("G:/game")).port == 15527


def test_a_wire_lane_carries_a_port_and_a_tree_and_no_game_directory():
    """The client half of a lane. `bridge` is imported by tests on machines
    with no game and no `klee-mod/local.props`, and `instances.lane()` would
    `SystemExit` on them: it resolves `GameDir`, which a client that only
    talks to a port has no business asking for."""
    lane1 = instances.wire_lane("lane1")
    assert lane1.game_dir is None
    assert lane1.port == instances.DEFAULT_PORT + 1 == 15527
    assert lane1.appdata == instances.LANE_ROOT / "lane1"
    assert lane1.base == "http://localhost:15527"
    assert lane1.log_path() == (instances.LANE_ROOT / "lane1"
                                ).joinpath(*instances.LOG_RELATIVE)

    lane0 = instances.wire_lane()
    assert (lane0.port, lane0.appdata, lane0.is_default) == (15526, None, True)


def test_the_wire_lane_is_why_the_client_needs_no_local_props(monkeypatch):
    """The lock, seen to fail first: `lane()` really does exit without the
    file, so the client half really does need its own constructor."""
    monkeypatch.setattr(soak, "LOCAL_PROPS", Path("Z:/nope/local.props"))
    with pytest.raises(SystemExit):
        instances.lane("lane1")
    assert instances.wire_lane("lane1").port == 15527       # unaffected


# ------------------------------------------- the variable and the client ---

def test_the_variable_moves_the_bridge_client(monkeypatch):
    """`GITS_LANE=1` is how the three `blindplay` commands -- which take no
    flag, and may not import `instances` at all -- reach the second game."""
    monkeypatch.setenv(instances.LANE_ENV, "1")
    assert bridge.current_base() == "http://localhost:15527"
    assert bridge.current_label() == "lane1"
    inst = bridge.current_instance()
    assert inst is not None and inst.appdata == instances.LANE_ROOT / "lane1"
    # Every URL constant is a PATH carrier, rebased at call time.
    assert bridge._rebase(bridge.SEED).startswith("http://localhost:15527/")
    assert bridge._rebase(bridge.SINGLEPLAYER).endswith("/api/v1/singleplayer")

    monkeypatch.setenv(instances.LANE_ENV, "lane1")
    assert bridge.current_base() == "http://localhost:15527"


def test_lane_zero_and_an_unset_variable_are_the_client_unchanged(monkeypatch):
    """`None`, not lane 0's instance: an unbound thread is what every command
    did before this existed, and `EB-210`'s crossing check is skipped on a
    lane with no tree of its own."""
    monkeypatch.delenv(instances.LANE_ENV, raising=False)
    assert bridge.current_base() == bridge.BASE == "http://localhost:15526"
    assert bridge.current_label() == "lane0"
    assert bridge.current_instance() is None
    assert bridge._rebase(bridge.SEED) == bridge.SEED

    for off in ("0", "lane0", ""):
        monkeypatch.setenv(instances.LANE_ENV, off)
        assert bridge.current_instance() is None
        assert bridge.current_base() == bridge.BASE


def test_a_bound_thread_beats_the_variable(monkeypatch):
    """A two-lane round binds its workers, and must never be second-guessed
    by whatever the operator happened to export into the shell."""
    monkeypatch.setenv(instances.LANE_ENV, "1")
    bridge.use(instances.wire_lane("lane0"))
    assert bridge.current_base() == "http://localhost:15526"
    assert bridge.current_label() == "lane0"

    bridge.use_default()
    assert bridge.current_base() == "http://localhost:15527"


def test_the_variable_reaches_a_worker_thread_too(monkeypatch):
    """It is read per call rather than captured at import, so a thread that
    never binds still answers on the lane the process was started for."""
    monkeypatch.setenv(instances.LANE_ENV, "1")
    seen: list[str] = []
    t = threading.Thread(target=lambda: seen.append(bridge.current_base()))
    t.start()
    t.join()
    assert seen == ["http://localhost:15527"]


def test_a_mistyped_variable_is_refused_rather_than_dialled(monkeypatch):
    monkeypatch.setenv(instances.LANE_ENV, "2")
    with pytest.raises(ValueError):
        bridge.current_base()


def test_the_blind_commands_reach_the_wire_only_through_the_client():
    """WHY THE VARIABLE IS ENOUGH FOR `observe` / `act` / `session`. They own
    no URL of their own -- every read and every post goes through `bridge`,
    which is the module the lane lookup lives in -- so a lane reaches them
    without one line of that design-blind file changing (and it may not
    import `instances` or `soak` at all: `test_understudy_blindplay` pins
    that line, and a `--lane` flag there would have to cross it)."""
    src = (Path(__file__).resolve().parents[2] / "understudy"
           / "blindplay.py").read_text(encoding="utf-8")
    assert "localhost" not in src
    assert "urllib" not in src
    assert "import instances" not in src and "import soak" not in src


# ------------------------------------------------- the godot.log cursor ----

def test_the_log_cursor_reads_the_lanes_own_log(monkeypatch):
    """`EB-292`'s `log_lacks` check is the one check that does not read the
    wire, so it is the one check a lane can silently point at the wrong game.
    `_LogWindow.path` resolves through `bridge.current_instance()`, which now
    answers the variable as well as an explicit bind."""
    monkeypatch.setenv("APPDATA", str(Path("C:/Users/x/AppData/Roaming")))
    monkeypatch.delenv(instances.LANE_ENV, raising=False)
    assert scenario.LOG_WINDOW.path() == Path(
        "C:/Users/x/AppData/Roaming").joinpath(*instances.LOG_RELATIVE)

    monkeypatch.setenv(instances.LANE_ENV, "1")
    assert scenario.LOG_WINDOW.path() == (instances.LANE_ROOT / "lane1"
                                          ).joinpath(*instances.LOG_RELATIVE)

    bridge.use(instances.wire_lane("lane0"))
    assert scenario.LOG_WINDOW.path() == Path(
        "C:/Users/x/AppData/Roaming").joinpath(*instances.LOG_RELATIVE)


# -------------------------------------------------- the shared install -----

def _installed(root: Path) -> Path:
    """Stage a bridge in `root` the way `deploy_bridge.ps1` stages one."""
    where = root / soak.BRIDGE_RELATIVE
    where.mkdir(parents=True, exist_ok=True)
    (where / soak.BRIDGE_MANIFEST).write_text("{}", encoding="utf-8")
    (where / soak.BRIDGE_DLL).write_bytes(b"MZ")
    return root


def _tasklist(*pids: int):
    """A `subprocess.run` double answering `tasklist` with these pids."""
    class _Done:
        returncode = 0
        stderr = ""
        stdout = ("\n".join(f'"SlayTheSpire2.exe","{p}","Console","1","1 K"'
                            for p in pids)
                  or "INFO: No tasks are running which match the criteria.")

    return lambda *a, **k: _Done()


def test_lane_zero_owns_the_shared_halves_and_asks_no_questions(monkeypatch):
    """`(None, True)`: no instance, and the bridge deploy is this session's,
    exactly as it always was. It does not even look at the game directory."""
    def _no(*_a, **_k):                                       # pragma: no cover
        raise AssertionError("lane 0 must not resolve the game directory")

    monkeypatch.setattr(soak, "game_dir", _no)
    assert soak.lane_setup(0) == (None, True)
    assert soak.lane_setup("lane0") == (None, True)


def test_a_higher_lane_asks_for_the_bridge_like_every_other_lane(tmp_path,
                                                                 monkeypatch):
    """The refusal that used to live here was OURS, and a live attempt
    (2026-09-02) proved it: the owner's Steam-launched game had no
    `mods\\STS2_MCP` in the install and held nothing, and refusing the lane
    outright blocked a second instance that was in no danger. The refcount is
    in `_deploy_bridge` (a current install is reused) and the lock is the
    deploy script's, which is the only party that can see one."""
    monkeypatch.setattr(soak, "game_dir", lambda: _installed(tmp_path))
    inst, install_bridge = soak.lane_setup(1)
    assert install_bridge is True
    assert inst.label == "lane1" and inst.port == 15527
    assert inst.appdata == instances.LANE_ROOT / "lane1"

    monkeypatch.setattr(soak, "game_dir", lambda: tmp_path / "bare")
    assert soak.lane_setup(1)[1] is True     # no bridge: still not a refusal


def test_an_install_is_both_files_or_neither(tmp_path):
    """A directory holding one of the two files `deploy_bridge.ps1` stages is
    a half-install, and reusing one would be worse than deploying."""
    assert soak.bridge_installed(tmp_path) is False
    _installed(tmp_path)
    assert soak.bridge_installed(tmp_path) is True
    (tmp_path / soak.BRIDGE_RELATIVE / soak.BRIDGE_MANIFEST).unlink()
    assert soak.bridge_installed(tmp_path) is False


def test_a_running_game_is_read_by_image_name_and_a_bad_probe_says_yes():
    """The one question in this module a pid cannot answer, asked about a
    directory every lane shares. A probe that could not run has NOT shown that
    nothing is running, so it answers as though something is."""
    assert soak.game_is_running(probe=_tasklist(4740, 51)) == "4740, 51"
    assert soak.game_is_running(probe=_tasklist()) == ""

    def _boom(*a, **k):
        raise OSError("tasklist is not on PATH")

    assert soak.game_is_running(probe=_boom).startswith("<probe failed")


# ------------------------------- EB-310: the bridge is nobody's to remove --
#
# Observed live 2026-09-02 with NO game running and the bridge already staged
# by `deploy_proto.ps1`: `embark --lane 1` re-deployed it and wrote it down as
# its OWN install, because the old rule counted an install as pre-existing only
# when a game was UP on it. `embark --teardown --lane 1` then printed
# "Deployed mods\STS2_MCP ... REVERTED" and took it out, and the owner's next
# Steam launch would have had no bridge. The three cases below are the whole
# rule: reused, refreshed, installed -- and a teardown that leaves it in all
# three. Evidence: `review/qa/lane1-live-reads-2026-09-02/`.


def _bridge_session(tmp_path, monkeypatch, *, installed: bool, pids: str,
                    ran: list):
    """A `Session` on a prepared game directory, with the deploy script faked.

    The fake STAGES AND UNSTAGES FOR REAL -- `_installed` on a plain call, an
    `rmtree` on `-Remove` -- so "the bridge is still there after teardown" is a
    claim about the directory rather than about a call list.
    """
    root = tmp_path / "game"
    root.mkdir(parents=True, exist_ok=True)
    if installed:
        _installed(root)
    monkeypatch.setattr(soak, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "game_dir", lambda: root)
    monkeypatch.setattr(soak, "game_is_running", lambda *a, **k: pids)

    class _Ok:
        returncode = 0
        stdout = stderr = ""

    def _fake_powershell(argv, *a, **k):
        ran.append(list(argv))
        if "-Remove" in argv:
            shutil.rmtree(root / soak.BRIDGE_RELATIVE, ignore_errors=True)
        else:
            _installed(root)
        return _Ok()

    monkeypatch.setattr(soak.subprocess, "run", _fake_powershell)
    return soak.Session("stamp", do_setup=False), root


def _bridge_row(sess) -> dict:
    rows = [e for e in sess.ledger.entries
            if e["change"].startswith("Deployed `mods")]
    assert len(rows) == 1, rows
    return rows[0]


def _teardown_leaves_the_bridge(sess, root, ran) -> None:
    """The half `EB-310` is actually about, asserted the same way three times."""
    before = len(ran)
    sess.teardown()
    assert soak.bridge_installed(root), (
        "a teardown removed the shared bridge; the owner's next Steam launch "
        "would have had none")
    assert all("-Remove" not in call for call in ran[before:])
    # The attribute is gone, not merely unused: an entry to hold would be an
    # invitation to wire the removal back up.
    assert not hasattr(sess, "_bridge_entry")


def test_an_installed_bridge_with_no_game_is_refreshed_and_left_shared(
        tmp_path, monkeypatch):
    """(a) THE CASE THAT WENT WRONG LIVE. Nothing holds the dll, so the vendor
    pin is re-staged -- and the row says `shared, left in place`, which is what
    keeps `deploy_proto.ps1`'s install from being torn out by the first
    teardown after it."""
    ran: list = []
    sess, root = _bridge_session(tmp_path, monkeypatch, installed=True,
                                 pids="", ran=ran)
    sess._deploy_bridge()

    row = _bridge_row(sess)
    assert row["state"] == "REVERTED" and row["pre_existing"] is True
    assert "shared, left in place" in row["note"]
    assert "refreshed" in row["note"]
    assert ran and str(soak.DEPLOY_BRIDGE) in ran[-1]
    assert "-Remove" not in ran[-1]
    _teardown_leaves_the_bridge(sess, root, ran)


def test_a_bridge_with_a_game_up_on_it_is_reused_never_rewritten(
        tmp_path, monkeypatch, capsys):
    """(b) THE PARALLEL CASE. A session that finds an install with a game
    already running on it writes NOTHING to disk, so it does not rewrite a dll
    that game may hold -- and the row is `shared, left in place` for the same
    reason case (a)'s is."""
    ran: list = []
    sess, root = _bridge_session(tmp_path, monkeypatch, installed=True,
                                 pids="4740", ran=ran)
    sess._deploy_bridge()

    assert ran == [], "this must not redeploy over a running game"
    row = _bridge_row(sess)
    assert row["state"] == "REVERTED" and row["pre_existing"] is True
    assert "shared, left in place" in row["note"] and "4740" in row["note"]
    assert "reusing it" in capsys.readouterr().out
    _teardown_leaves_the_bridge(sess, root, ran)


def test_an_install_with_no_bridge_gets_one_and_still_never_loses_it(
        tmp_path, monkeypatch):
    """(c) A session may PUT the bridge there -- and still may not take it
    away. The harness has no remover at all now: `deploy_bridge.ps1 -Remove`
    is run by hand, by whoever decides the machine is done with it."""
    ran: list = []
    sess, root = _bridge_session(tmp_path, monkeypatch, installed=False,
                                 pids="", ran=ran)
    assert not soak.bridge_installed(root)
    sess._deploy_bridge()

    assert soak.bridge_installed(root)
    row = _bridge_row(sess)
    assert row["state"] == "REVERTED" and row["pre_existing"] is True
    assert "shared, left in place" in row["note"]
    assert "installed here" in row["note"]
    assert ran and str(soak.DEPLOY_BRIDGE) in ran[-1]
    _teardown_leaves_the_bridge(sess, root, ran)


def test_the_harness_has_no_bridge_remover_left(tmp_path, monkeypatch):
    """The rule stated where a future edit would trip over it: no undo step,
    no ledger slot, no method. The one row `_deploy_bridge` writes carries the
    BY HAND instruction in its own undo text, so a person reading the ledger is
    told who removes it."""
    assert not hasattr(soak.Session, "_remove_bridge")
    assert all(attr != "_bridge_entry" for attr, _ in embark._LEDGER_SLOTS)

    ran: list = []
    sess, _root = _bridge_session(tmp_path, monkeypatch, installed=True,
                                  pids="", ran=ran)
    sess._deploy_bridge()
    undo = _bridge_row(sess)["undo"]
    assert "-Remove" in undo and "BY HAND" in undo


def test_a_game_running_on_an_install_with_no_bridge_still_deploys(
        tmp_path, monkeypatch):
    """The live blocker, from the other side: the owner's game holds nothing
    when the install carries no bridge, so a lane may put one there and
    launch. This is the case the old refusal made impossible."""
    ran: list = []
    sess, root = _bridge_session(tmp_path, monkeypatch, installed=False,
                                 pids="4740", ran=ran)
    sess._deploy_bridge()
    assert soak.bridge_installed(root)
    assert ran and str(soak.DEPLOY_BRIDGE) in ran[-1]


def test_the_bridge_deploy_refuses_a_held_file_not_a_running_game():
    """`deploy_bridge.ps1:73` used to throw whenever ANY game process existed.
    The owner's Steam-launched game holds nothing when the install carries no
    bridge, so that refusal blocked the lane rather than protecting it -- and
    Steam's tolerance of a second instance went untested for a reason that was
    never Steam's. The question it asks now is whether the files it is about
    to rewrite are LOCKED."""
    src = (Path(__file__).resolve().parents[2] / "klee-mod" / "build"
           / "deploy_bridge.ps1").read_text(encoding="utf-8")
    assert "function Test-FileHeld" in src
    assert "[System.IO.FileShare]::None" in src
    # The throw is conditioned on a held file, not on a process existing.
    guard = src.split("if (-not $BuildOnly) {", 1)[1].split("if ($Remove)", 1)[0]
    assert "if ($held) {" in guard
    assert "throw" in guard.split("if ($held) {", 1)[1]
    assert "Get-Process -Name 'SlayTheSpire2'" in guard      # still reported
    # A running game with nothing locked is told what it needs to know: mods
    # load at boot, so THIS deploy reaches the next launch and not that game.
    assert "load at BOOT" in guard


def test_the_dev_deploy_leaves_the_install_parallel_ready():
    """Mods load at BOOT and this script is the one moment the game is
    guaranteed closed, so it is the only moment the bridge can be put in front
    of a launch the OWNER makes from Steam. A warning rather than a failure:
    the klee package is already deployed by then."""
    src = (Path(__file__).resolve().parents[2] / "klee-mod" / "build"
           / "deploy_proto.ps1").read_text(encoding="utf-8")
    assert "deploy_bridge.ps1" in src
    tail = src.split("Deploying to $target", 1)[1]
    assert "deploy_bridge.ps1" in tail, "the bridge install must come last"
    assert "try {" in tail and "catch" in tail
    assert "WARNING" in tail


def test_the_deploy_refuses_while_any_lane_holds_the_dll():
    """The third shared half, and the one that CANNOT be refcounted:
    `mods\\klee` is one deployed build for every lane. The check is by image
    NAME rather than by pid on purpose -- by pid it would miss the other
    lane's game, whose lock on `klee.dll` is exactly the same lock."""
    src = (Path(__file__).resolve().parents[2] / "klee-mod" / "build"
           / "deploy_proto.ps1").read_text(encoding="utf-8")
    assert "Get-Process -Name 'SlayTheSpire2'" in src
    refusal = src.split("Get-Process -Name 'SlayTheSpire2'", 1)[1][:1200]
    assert "throw" in refusal
    assert "klee.dll" in refusal
    assert "lane" in refusal.lower()
    # And it happens before anything is built or copied.
    assert src.index("Get-Process -Name 'SlayTheSpire2'") < src.index(
        "dotnet build")


# ------------------------------------------------------------- embark ------

class _SpySession:
    """`soak.Session`'s constructor signature, and nothing else."""

    instances_made: list["_SpySession"] = []

    def __init__(self, stamp, do_setup=True, intent=None, instance=None,
                 install_bridge=True):
        self.stamp = stamp
        self.do_setup = do_setup
        self.instance = instance
        self.install_bridge = install_bridge
        self.ledger = soak.Reversibility(Path("rev.json"))
        type(self).instances_made.append(self)

    @property
    def label(self):
        return getattr(self.instance, "label", "lane0")

    def setup(self):
        pass

    def teardown(self):                                       # pragma: no cover
        pass


class _SpyDriver:
    character_actual = "Klee"
    log = Path("run.jsonl")

    def __init__(self, *a, **kw):
        pass

    def _to_main_menu(self):
        return {"state_type": "menu"}

    def _embark(self, state):
        return state

    def _verify_character(self, state):
        return {"state_type": "map", "run": {"floor": 1}}


def _embark_stubs(tmp_path, monkeypatch):
    _SpySession.instances_made = []
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "Session", _SpySession)
    monkeypatch.setattr(soak, "RunDriver", _SpyDriver)
    monkeypatch.setattr(bridge, "current_seed", lambda: "SEEDSEED")


def test_an_embark_on_lane_one_launches_the_second_game(tmp_path, monkeypatch):
    """The sidecar is the run's own manifest and the file `--teardown` reads,
    so the lane goes on it: the label, the port and the user tree are the
    three facts a reader needs to find the log that belongs to this run."""
    _embark_stubs(tmp_path, monkeypatch)
    lane1 = instances.lane("lane1", game_dir=tmp_path / "game")

    blob = embark.embark("klee", instance=lane1, install_bridge=False)

    session = _SpySession.instances_made[-1]
    assert session.instance is lane1
    assert session.install_bridge is False
    assert blob["instance"] == "lane1"
    assert blob["port"] == "15527"
    assert blob["appdata"] == str(instances.LANE_ROOT / "lane1")
    # THE STANDING RULE, IN THE FILE. A caveat that lives only in a comment is
    # a caveat that is not in the record.
    assert blob["run_of_record"] is False
    assert blob["lane_guardrail"] == instances.LANE_GUARDRAIL
    assert "is a run of record" in instances.LANE_GUARDRAIL

    on_disk = json.loads(
        (tmp_path / f"embark-{blob['stamp']}.json").read_text(encoding="utf-8"))
    assert on_disk["instance"] == "lane1"


def test_an_embark_on_lane_zero_is_the_embark_that_always_ran(tmp_path,
                                                              monkeypatch):
    _embark_stubs(tmp_path, monkeypatch)
    blob = embark.embark("klee")
    session = _SpySession.instances_made[-1]
    assert session.instance is None
    assert session.install_bridge is True
    assert blob["instance"] == "lane0"
    assert "port" not in blob and "appdata" not in blob
    assert "lane_guardrail" not in blob and "run_of_record" not in blob


def _sidecar(dir_: Path, stamp: str, lane: str, ledger: Path) -> None:
    blob = {"stamp": stamp, "ledger": str(ledger), "hold": False,
            "instance": lane, "character_requested": "KLEEMOD-KLEE"}
    (dir_ / f"embark-{stamp}.json").write_text(json.dumps(blob),
                                               encoding="utf-8")


def test_a_teardown_picks_the_named_lanes_embark(tmp_path, monkeypatch):
    """With two games open the NEWEST sidecar is whichever was started last,
    and tearing that one down is a coin flip over somebody else's run."""
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    _sidecar(tmp_path, "20260902-100000", "lane1", tmp_path / "l1.json")
    _sidecar(tmp_path, "20260902-110000", "lane0", tmp_path / "l0.json")

    assert embark.latest_stamp() == "20260902-110000"          # unchanged
    assert embark.latest_stamp("lane1") == "20260902-100000"
    assert embark.latest_stamp("lane0") == "20260902-110000"

    # A sidecar written before lanes existed carries no `instance` key at all.
    (tmp_path / "embark-20260902-090000.json").write_text(
        json.dumps({"stamp": "x", "ledger": "y", "hold": False}),
        encoding="utf-8")
    assert embark.sidecar_lane(json.loads(
        (tmp_path / "embark-20260902-090000.json").read_text(
            encoding="utf-8"))) == "lane0"


def test_a_teardown_of_a_lane_one_embark_touches_only_lane_one(
        tmp_path, monkeypatch):
    """Its ledger has no bridge row and no appid row -- lane 1 installed
    neither -- so the two shared halves are not reverted, and the wire calls
    that ARE made go to lane 1's own port even from a shell that never heard
    of it."""
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "game_dir", lambda: tmp_path / "game")
    monkeypatch.setenv(instances.LANE_ENV, "")     # the shell knows nothing

    ledger = tmp_path / "reversibility-20260902-100000.json"
    ledger.write_text(json.dumps([
        {"n": 1, "change": "May set a chosen run seed via "
                           "`POST /api/v1/gits/seed`",
         "undo": "x", "state": "APPLIED"},
        {"n": 2, "change": "Set FastMode=Instant and TimeScale=8.0",
         "undo": "y", "state": "APPLIED"},
    ]), encoding="utf-8")
    _sidecar(tmp_path, "20260902-100000", "lane1", ledger)

    where: list[str] = []
    monkeypatch.setattr(bridge, "clear_seed",
                        lambda: where.append(bridge.current_base()) or {})
    monkeypatch.setattr(bridge, "set_speed",
                        lambda *a, **k: where.append(bridge.current_base()) or {})

    def _no_powershell(*a, **k):                              # pragma: no cover
        raise AssertionError("a lane-1 teardown must run no deploy script")

    monkeypatch.setattr(soak.subprocess, "run", _no_powershell)

    table = embark.teardown(lane=1)

    assert where == ["http://localhost:15527", "http://localhost:15527"]
    assert bridge.current_label() == "lane1"
    assert "REVERTED" in table
    assert not (tmp_path / "game").exists()      # nothing shared was touched


def test_a_teardown_refuses_another_lanes_embark(tmp_path, monkeypatch):
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    _sidecar(tmp_path, "20260902-100000", "lane0", tmp_path / "l0.json")
    with pytest.raises(embark.EmbarkError) as excinfo:
        embark.teardown("20260902-100000", lane=1)
    assert "lane0" in str(excinfo.value)


def test_the_embark_prints_the_export_line_for_the_blind_commands(
        tmp_path, monkeypatch, capsys):
    """`observe` / `act` / `session` take no flag, so the operator is handed
    the one thing that points them at the same game."""
    monkeypatch.setattr(soak, "lane_setup",
                        lambda v: (instances.lane("lane1",
                                                  game_dir=tmp_path), False))
    monkeypatch.setattr(embark, "embark", lambda *a, **k: {
        "stamp": "S", "instance": "lane1", "port": "15527",
        "appdata": str(instances.LANE_ROOT / "lane1"),
        "character_actual": "Klee", "run_seed": "ABC", "screen": "map",
        "floor": 1})

    assert embark.main(["--character", "klee", "--lane", "1"]) == 0
    out = capsys.readouterr().out
    assert "GITS_LANE" in out
    assert "$env:GITS_LANE = '1'" in out
    assert "export GITS_LANE=1" in out
    assert "--teardown --lane 1" in out
    assert "NOT A RUN OF RECORD" in out.upper()


def test_a_lane_zero_embark_prints_no_lane_noise(tmp_path, monkeypatch,
                                                 capsys):
    monkeypatch.setattr(soak, "lane_setup", lambda v: (None, True))
    monkeypatch.setattr(embark, "embark", lambda *a, **k: {
        "stamp": "S", "instance": "lane0", "character_actual": "Klee",
        "run_seed": "ABC", "screen": "map", "floor": 1})
    assert embark.main(["--character", "klee"]) == 0
    out = capsys.readouterr().out
    assert "GITS_LANE" not in out
    assert "python -m understudy.embark --teardown\n" in out


# --------------------------------------------------------------- soak ------

def test_the_soak_takes_a_lane_and_names_its_index_after_it(tmp_path,
                                                            monkeypatch):
    """Two soaks starting in the same second would otherwise write one index
    over the other -- the third shape of the interleaving defect the live
    two-lane proof found in the run logs."""
    monkeypatch.setattr(soak, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "Session", _SpySession)
    monkeypatch.setattr(soak, "game_dir", lambda: _installed(tmp_path))
    _SpySession.instances_made = []

    result = soak.soak(0, soak.DEFAULT_CHARACTER, do_setup=False, lane=1)
    session = _SpySession.instances_made[-1]
    assert session.instance.label == "lane1"
    assert result["instance"] == "lane1"
    assert list(tmp_path.glob("soak-*-lane1-index.json"))

    _SpySession.instances_made = []
    result = soak.soak(0, soak.DEFAULT_CHARACTER, do_setup=False)
    session = _SpySession.instances_made[-1]
    assert session.instance is None and session.install_bridge is True
    assert result["instance"] == "lane0"
    assert not list(tmp_path.glob("soak-*-lane0-index.json"))


def test_the_soak_cli_carries_the_flag(monkeypatch):
    seen: dict = {}
    monkeypatch.setattr(soak, "soak",
                        lambda *a, **k: seen.update(k) or {"stamp": "s"})
    assert soak.main(["--runs", "1", "--lane", "1"]) == 0
    assert seen["lane"] == "1"

    seen.clear()
    assert soak.main(["--runs", "1"]) == 0
    assert seen["lane"] == 0


def test_the_soak_cli_reports_a_lane_that_is_not_a_lane(monkeypatch, capsys):
    """A typo'd lane number never reaches a launch. Note what this does NOT
    do: it does not go near the game directory, which is why it is safe to
    run on the machine the owner is playing on."""
    monkeypatch.setattr(soak, "soak",
                        lambda *a, **k: pytest.fail("must not run"))
    assert soak.main(["--runs", "1", "--lane", "9"]) == 2
    assert "lane error" in capsys.readouterr().err


# ------------------------------------------------------------ scenario -----

def test_a_scenario_runs_in_a_lane_and_binds_it_before_the_cursor(
        tmp_path, monkeypatch):
    """The ordering IS the fix: `Runner.__init__` resets `LOG_WINDOW`, whose
    path resolves through the thread's lane, so a thread bound only later by
    the Session would take its cursor from lane 0's `godot.log`."""
    seen: dict = {}

    def _run_scripted(policy, stamp, **kw):
        seen.update(kw)
        seen["cursor"] = scenario.LOG_WINDOW.path()
        seen["base"] = bridge.current_base()
        return {"outcome": "bounded"}

    monkeypatch.setattr(soak, "run_scripted", _run_scripted)
    monkeypatch.setattr(soak, "lane_setup",
                        lambda v: (instances.lane("lane1", game_dir=tmp_path),
                                   False))
    monkeypatch.setattr(scenario, "LOG_DIR", tmp_path)
    a_scenario = sorted(scenario.SCENARIO_DIR.glob("*.yaml"))[0]

    # `ok is None` (no combat screen was reached) is exit 2, and expected: the
    # run is stubbed out. What this asserts is everything around it.
    assert scenario.main(["run", str(a_scenario), "--why", "lane test",
                          "--lane", "1"]) == 2
    assert seen["instance"].label == "lane1"
    assert seen["install_bridge"] is False
    assert seen["base"] == "http://localhost:15527"
    assert seen["cursor"] == (instances.LANE_ROOT / "lane1"
                              ).joinpath(*instances.LOG_RELATIVE)
    assert list(tmp_path.glob("scenario-*-lane1.jsonl"))


def test_a_lane_zero_scenario_is_unchanged(tmp_path, monkeypatch):
    seen: dict = {}
    monkeypatch.setattr(soak, "run_scripted",
                        lambda p, s, **kw: seen.update(kw) or {})
    monkeypatch.setattr(scenario, "LOG_DIR", tmp_path)
    a_scenario = sorted(scenario.SCENARIO_DIR.glob("*.yaml"))[0]

    assert scenario.main(["run", str(a_scenario), "--why", "lane test"]) == 2
    assert seen["instance"] is None
    assert seen["install_bridge"] is True
    assert bridge.current_instance() is None
    assert list(tmp_path.glob("scenario-*.jsonl"))
    assert not list(tmp_path.glob("scenario-*-lane0.jsonl"))


def test_a_scenario_reports_a_lane_that_is_not_a_lane(tmp_path, monkeypatch,
                                                      capsys):
    """Refused before `run_scripted` is reached, so nothing launches and
    nothing deploys -- the property that lets this file run on the machine the
    owner is playing on."""
    monkeypatch.setattr(soak, "run_scripted",
                        lambda *a, **k: pytest.fail("must not run"))
    monkeypatch.setattr(scenario, "LOG_DIR", tmp_path)
    a_scenario = sorted(scenario.SCENARIO_DIR.glob("*.yaml"))[0]
    assert scenario.main(["run", str(a_scenario), "--why", "x",
                          "--lane", "9"]) == 2
    assert "lane error" in capsys.readouterr().err
