"""Five seat lanes, and embarking several of them at once (2026-10-05).

The registry is derived from one count; the shared game install is taken
under one machine-wide lock with a launch stagger; an embark's stamp is
claimed, not assumed unique; and `embark --lanes 1,2,3` starts one ordinary
embark per lane at once and reports each.
"""
from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

from understudy import embark, instances, soak, soak_session


# ------------------------------------------------------------ registry ----

def test_five_seat_lanes_above_lane_zero_each_with_its_own_port_and_tree():
    assert instances.SEAT_LANE_COUNT == 5
    assert instances.lane_labels() == [f"lane{n}" for n in range(6)]
    assert instances.seat_lane_labels() == [f"lane{n}" for n in range(1, 6)]
    assert instances.LANES["lane0"] == (15526, None)
    for n in range(1, 6):
        port, appdata = instances.LANES[f"lane{n}"]
        assert port == 15526 + n == instances.port_for(f"lane{n}")
        assert appdata == instances.LANE_ROOT / f"lane{n}"
    assert instances.LANES["lane5"][0] == 15531
    ports = [port for port, _ in instances.LANES.values()]
    assert len(set(ports)) == len(ports)


def test_lane_five_is_reachable_by_every_door():
    assert instances.label_for(5) == instances.label_for("lane5") == "lane5"
    assert instances.env_label({instances.LANE_ENV: "5"}) == "lane5"
    wire = instances.wire_lane("lane5")
    assert wire.port == 15531 and wire.game_dir is None
    lane = instances.lane("lane5", game_dir=Path("G:/game"))
    assert lane.env({})[instances.PORT_ENV] == "15531"
    assert [i.label for i in instances.lanes(6, game_dir=Path("G:/game"))] \
        == instances.lane_labels()
    with pytest.raises(ValueError):
        instances.label_for(6)


# --------------------------------------------------------- install lock ----

def test_the_install_lock_excludes_a_second_process(tmp_path):
    """The lock is an OS lock: another PROCESS cannot take it while this one
    holds it, and takes it the moment it is released."""
    probe = (
        "import sys, pathlib\n"
        "from understudy import instances\n"
        "instances.LOCK_ROOT = pathlib.Path(sys.argv[1])\n"
        "try:\n"
        "    with instances.install_lock(timeout_s=0.5):\n"
        "        print('GOT')\n"
        "except instances.InstallLockTimeout:\n"
        "    print('BLOCKED')\n")
    root = Path(__file__).resolve().parents[2]

    def other() -> str:
        return subprocess.run([sys.executable, "-c", probe, str(tmp_path)],
                              capture_output=True, text=True, cwd=str(root),
                              timeout=60).stdout.strip()

    held = instances.LOCK_ROOT
    instances.LOCK_ROOT = tmp_path
    try:
        with instances.install_lock(timeout_s=1):
            assert other().endswith("BLOCKED")
        assert other().endswith("GOT")
    finally:
        instances.LOCK_ROOT = held


def test_the_install_lock_is_reentrant_and_serialises_threads():
    order: list[str] = []
    with instances.install_lock(timeout_s=1):
        with instances.install_lock(timeout_s=1):       # reentrant
            order.append("inner")

        def other():
            with instances.install_lock(timeout_s=5):
                order.append("thread")

        t = threading.Thread(target=other)
        t.start()
        time.sleep(0.3)
        order.append("outer-still-held")
    t.join(5)
    assert order == ["inner", "outer-still-held", "thread"]


def test_the_install_lock_times_out_rather_than_hanging():
    got: list[object] = []
    with instances.install_lock(timeout_s=1):
        def other():
            try:
                with instances.install_lock(timeout_s=0.2):
                    got.append("got")
            except instances.InstallLockTimeout as exc:
                got.append(exc)
        t = threading.Thread(target=other)
        t.start()
        t.join(5)
    assert len(got) == 1 and isinstance(got[0], instances.InstallLockTimeout)


def test_the_launch_stagger_waits_only_the_gap_still_owed(monkeypatch):
    monkeypatch.setattr(instances, "LAUNCH_STAGGER_S", 8.0)
    slept: list[float] = []
    assert instances.await_launch_stagger(now=lambda: 100.0,
                                          sleep=slept.append) == 0.0
    instances.note_launch("lane1", 1234, now=lambda: 100.0)
    assert instances.last_launch_at() == 100.0
    assert instances.await_launch_stagger(now=lambda: 103.0,
                                          sleep=slept.append) == 5.0
    assert instances.await_launch_stagger(now=lambda: 120.0,
                                          sleep=slept.append) == 0.0
    # a clock that went backwards owes nothing rather than a long sleep
    assert instances.await_launch_stagger(now=lambda: 50.0,
                                          sleep=slept.append) == 0.0
    assert slept == [5.0]


def _fake_session(tmp_path, monkeypatch, events, label):
    s = soak.Session.__new__(soak.Session)
    s.dir = tmp_path
    s.stamp = f"s-{label}"
    s.do_setup = True
    s.ledger = soak.Reversibility(path=tmp_path / f"ledger-{label}.json")
    s.instance = None
    s.intent = ""
    s.proc = None
    s._launch_entry = None
    s.wire = lambda: None
    s._quiet_label = lambda: label
    s._menu_budget = lambda: 1.0
    s._speed_on = lambda: None

    def appid():
        events.append((label, "appid-in"))
        time.sleep(0.05)
        events.append((label, "appid-out"))

    def bridge():
        events.append((label, "bridge-in"))
        time.sleep(0.05)
        events.append((label, "bridge-out"))

    def launch_unlocked():
        events.append((label, "launch"))

    s._steam_appid = appid
    s._deploy_bridge = bridge
    s._launch_unlocked = launch_unlocked
    s.wait_for_menu = lambda timeout: events.append((label, "menu-wait"))
    return s


def test_two_setups_never_interleave_on_the_shared_install(tmp_path,
                                                           monkeypatch):
    """The 2026-09-25 defect: two embarks both deployed the bridge, and one's
    rewrite landed under the other's booting game. Inside the lock, each
    lane's appid -> bridge -> launch runs whole before the next lane's
    starts; the menu waits (outside it) are free to overlap."""
    monkeypatch.setattr(soak_session.keepawake, "acquire", lambda why: False)
    monkeypatch.setattr(soak_session, "_last_kill_at", None, raising=False)
    (tmp_path / soak.GAME_EXE).write_text("", encoding="utf-8")
    events: list[tuple[str, str]] = []
    sessions = [_fake_session(tmp_path, monkeypatch, events, f"lane{n}")
                for n in (1, 2, 3)]
    threads = [threading.Thread(target=s.setup) for s in sessions]
    for t in threads:
        t.start()
    for t in threads:
        t.join(10)
    critical = [e for e in events if e[1] != "menu-wait"]
    for i in range(0, len(critical), 5):
        block = critical[i:i + 5]
        assert len({lane for lane, _ in block}) == 1, critical
        assert [step for _, step in block] == [
            "appid-in", "appid-out", "bridge-in", "bridge-out", "launch"]
    assert len(critical) == 15


def test_the_session_holds_the_lock_from_appid_through_launch():
    src = Path(soak_session.__file__).read_text(encoding="utf-8")
    setup = src[src.index("    def setup(self)"):src.index(
        "    def _menu_budget(self)")]
    locked = setup[setup.index("with instances.install_lock("):
                   setup.index("self.wait_for_menu(timeout)")]
    for step in ("self._steam_appid()", "self._deploy_bridge()",
                 "self._launch()"):
        assert step in locked
    launch = src[src.index("    def _launch(self)"):src.index(
        "    def _launch_unlocked(self)")]
    assert "instances.install_lock(" in launch
    assert "await_launch_stagger()" in launch
    assert "note_launch(" in launch


# --------------------------------------------------------- the stamp ------

def test_two_embarks_in_one_second_claim_two_stamps(tmp_path, monkeypatch):
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    readings = iter(["20261005-120000", "20261005-120000",
                     "20261005-120001"])
    first = embark.reserve_stamp("1", clock=lambda fmt: "20261005-120000")
    second = embark.reserve_stamp("2", clock=lambda fmt: next(readings),
                                  sleep=lambda s: None)
    assert first == "20261005-120000"
    assert second == "20261005-120001"
    blob = json.loads((tmp_path / f"embark-{second}.json").read_text(
        encoding="utf-8"))
    assert blob["instance"] == "lane2"


def test_a_stamp_that_never_frees_is_an_embark_error(tmp_path, monkeypatch):
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    embark.reserve_stamp("1", clock=lambda fmt: "X")
    with pytest.raises(embark.EmbarkError):
        embark.reserve_stamp("2", clock=lambda fmt: "X",
                             sleep=lambda s: None, attempts=3)


# ------------------------------------------------------ parallel embark ----

def test_parse_seat_lanes_refuses_lane_zero_twice_and_typos():
    assert embark.parse_seat_lanes("1,2,3,4,5") == [
        f"lane{n}" for n in range(1, 6)]
    for bad in ("0,1", "1,1", "", "1,9"):
        with pytest.raises(embark.EmbarkError):
            embark.parse_seat_lanes(bad)


def test_each_lane_gets_its_own_seed_and_one_command():
    labels = ["lane1", "lane2"]
    cmds = embark.lane_commands(
        labels, characters=["klee", "klee"], seeds=["AAA", "BBB"],
        ascension=0, max_actions=1500, arms=[])
    assert cmds[0][1:] == ["-m", "understudy.embark", "--lane", "1",
                           "--character", "klee", "--seed", "AAA",
                           "--ascension", "0", "--max-actions", "1500"]
    assert cmds[1][cmds[1].index("--seed") + 1] == "BBB"
    assert embark._per_lane("x", labels, "seeds") == ["x", "x"]
    with pytest.raises(embark.EmbarkError):
        embark._per_lane("a,b,c", labels, "seeds")


def test_embark_lanes_starts_them_all_before_waiting_and_reports_each(
        tmp_path):
    started: list[str] = []
    waited: list[str] = []
    side = tmp_path / "embark-x.json"
    side.write_text(json.dumps({"stamp": "x", "character_actual": "Klee",
                                "run_seed": "AAA", "ascension": 0}),
                    encoding="utf-8")

    class Proc:
        def __init__(self, cmd, stdout, **kw):
            self.lane = cmd[cmd.index("--lane") + 1]
            started.append(self.lane)
            if self.lane == "1":
                stdout.write(f"sidecar:   {side}\n")
            else:
                stdout.write("embark error: menu never became ready\n")

        def wait(self):
            # every lane was started before the first wait
            assert len(started) == 2
            waited.append(self.lane)
            return 0 if self.lane == "1" else 2

    cmds = embark.lane_commands(["lane1", "lane2"], characters=["klee"] * 2,
                                seeds=["AAA", "BBB"], ascension=0,
                                max_actions=0, arms=[])
    rows = embark.embark_lanes(["lane1", "lane2"], cmds, popen=Proc,
                               log_dir=tmp_path)
    assert waited == ["1", "2"]
    assert rows[0]["exit"] == 0 and rows[0]["run_seed"] == "AAA"
    assert rows[0]["port"] == 15527
    assert rows[1]["exit"] == 2 and "menu never" in rows[1]["error"]
    text = embark.render_lane_rows(rows)
    assert "lane1  port 15527  UP" in text and "lane2  port 15528  FAILED" \
        in text


def test_the_cli_routes_lanes_without_coop_to_the_parallel_embark(
        monkeypatch, capsys):
    seen = {}

    def fake(labels, commands, **kw):
        seen["labels"], seen["commands"] = labels, commands
        return [{"lane": lb, "port": instances.port_for(lb), "exit": 0,
                 "log": "l", "character": "Klee", "run_seed": "S",
                 "ascension": 0, "stamp": "t", "error": ""}
                for lb in labels]
    monkeypatch.setattr(embark, "embark_lanes", fake)
    code = embark.main(["--lanes", "1,5", "--character", "klee",
                        "--seeds", "A,B", "--ascension", "0"])
    assert code == 0
    assert seen["labels"] == ["lane1", "lane5"]
    assert "lane5  port 15531  UP" in capsys.readouterr().out
    assert embark.main(["--lanes", "0,1"]) == 2
