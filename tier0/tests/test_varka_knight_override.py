"""The lane override for Varka's starting Knight (the Varka payoff round,
review/records/varka-payoff-round-2026-10-10.md, "Next round": "Add a lane
override for the starting Knight (`GITS_VARKA_KNIGHT`)").

`understudy.embark --varka-knight` validates the element before any launch,
hands it to the launched game through `soak.Session(extra_env=...)`, records
it in the sidecar, and a parallel `--lanes` embark passes one per lane. The
mod side (`VarkaStarterKnight.Override`) is pinned in
`klee-mod/KleeTests/Prototype/VarkaPayoffRoundTests.cs`.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from understudy import bridge, embark, soak
from understudy import soak_session

REPO = Path(__file__).resolve().parents[2]


def test_the_words_it_takes():
    assert embark.varka_knight("pyro") == "pyro"
    assert embark.varka_knight(" Cryo ") == "cryo"
    assert embark.varka_knight("ELECTRO") == "electro"
    assert embark.varka_knight("hydro") == "hydro"
    for roll in ("", None, "roll", "-", "none"):
        assert embark.varka_knight(roll) == ""
    for bad in ("anemo", "amber", "pyro,cryo"):
        with pytest.raises(embark.EmbarkError):
            embark.varka_knight(bad)
    # The mod reads the same variable.
    fang = (REPO / "klee-mod" / "KleeCode" / "Relics"
            / "VarkaStarterKnight.cs").read_text(encoding="utf-8")
    assert f'"{embark.VARKA_KNIGHT_ENV}"' in fang


def test_each_lane_gets_its_own_knight():
    labels = ["lane1", "lane2", "lane3"]
    cmds = embark.lane_commands(
        labels, characters=["varka"] * 3, seeds=["A", "B", "C"],
        ascension=0, max_actions=0, arms=[],
        knights=["pyro", "roll", "Cryo"])
    assert cmds[0][-2:] == ["--varka-knight", "pyro"]
    assert "--varka-knight" not in cmds[1]
    assert cmds[2][-2:] == ["--varka-knight", "cryo"]
    # One value is every lane's.
    assert embark._per_lane("pyro", labels, "varka-knight") == ["pyro"] * 3
    # No list: no flag on any lane, as before.
    plain = embark.lane_commands(
        labels, characters=["varka"] * 3, seeds=[None] * 3, ascension=None,
        max_actions=0, arms=[])
    assert all("--varka-knight" not in c for c in plain)


def test_a_parallel_embark_refuses_a_bad_knight_before_launching(
        monkeypatch, capsys):
    launched = []
    monkeypatch.setattr(embark, "embark_lanes",
                        lambda *a, **kw: launched.append(a) or [])
    code = embark.main(["--lanes", "1,2", "--character", "varka",
                        "--varka-knight", "pyro,anemo"])
    assert code == 2 and not launched
    assert "--varka-knight" in capsys.readouterr().err


def test_the_cli_passes_one_knight_per_lane(monkeypatch):
    seen = {}

    def fake(labels, commands, **kw):
        seen["commands"] = commands
        return []

    monkeypatch.setattr(embark, "embark_lanes", fake)
    embark.main(["--lanes", "1,2", "--character", "varka",
                 "--varka-knight", "pyro,electro"])
    assert [c[c.index("--varka-knight") + 1] for c in seen["commands"]] == [
        "pyro", "electro"]


def test_co_op_refuses_it(capsys):
    code = embark.main(["--coop", "--lanes", "2,3", "--characters",
                        "varka", "--varka-knight", "pyro"])
    assert code == 2
    assert "--varka-knight" in capsys.readouterr().err


class _Session:
    made: list["_Session"] = []

    def __init__(self, stamp, do_setup=True, intent=None, instance=None,
                 install_bridge=True, extra_env=None):
        self.instance = instance
        self.extra_env = extra_env
        self.ledger = soak.Reversibility(Path("rev.json"))
        type(self).made.append(self)

    def setup(self):
        pass


class _Driver:
    character_actual = "Varka"
    log = Path("run.jsonl")

    def __init__(self, *a, **kw):
        pass

    def _to_main_menu(self):
        return {"state_type": "menu"}

    def _embark(self, state):
        return state

    def _verify_character(self, state):
        return {"state_type": "map", "run": {"floor": 1, "ascension": 0}}


def _stubs(tmp_path, monkeypatch):
    _Session.made = []
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "Session", _Session)
    monkeypatch.setattr(soak, "RunDriver", _Driver)
    monkeypatch.setattr(bridge, "seed_read_back", lambda: "SEEDSEED")


def test_the_embark_hands_the_game_the_knight_and_records_it(
        tmp_path, monkeypatch):
    _stubs(tmp_path, monkeypatch)
    blob = embark.embark("VARKA", knight="Pyro")
    assert _Session.made[-1].extra_env == {"GITS_VARKA_KNIGHT": "pyro"}
    assert blob["varka_knight_requested"] == "pyro"
    on_disk = json.loads((tmp_path / f"embark-{blob['stamp']}.json")
                         .read_text(encoding="utf-8"))
    assert on_disk["varka_knight_requested"] == "pyro"


def test_no_knight_assigns_it_empty_so_a_stray_export_cannot_reach_the_game(
        tmp_path, monkeypatch):
    _stubs(tmp_path, monkeypatch)
    blob = embark.embark("VARKA")
    assert _Session.made[-1].extra_env == {"GITS_VARKA_KNIGHT": ""}
    assert blob["varka_knight_requested"] == ""


def test_the_session_puts_its_extra_env_on_every_launch(monkeypatch):
    seen = {}

    class _Popen:
        pid = 4242

        def __init__(self, cmd, cwd=None, env=None, **kw):
            seen["env"] = env

    session = object.__new__(soak_session.Session)
    session.instance = None
    session.dir = Path(".")
    session.intent = ""
    session.extra_args = ()
    session.extra_env = {"GITS_VARKA_KNIGHT": "cryo"}

    class _Ledger:
        def record(self, *a, **kw):
            return {}

        def flush(self):
            pass

    session.ledger = _Ledger()
    monkeypatch.setattr(soak_session.subprocess, "Popen", _Popen)
    monkeypatch.setenv("GITS_VARKA_KNIGHT", "pyro")
    session._launch_unlocked()
    assert seen["env"]["GITS_VARKA_KNIGHT"] == "cryo"
    assert os.environ["GITS_VARKA_KNIGHT"] == "pyro"
