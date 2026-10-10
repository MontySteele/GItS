"""`act --observe` (2026-10-09): one call per move.

Seats chained `a ... && o` in one Bash call; a permission classifier refuses
compound commands for subagents, so each move became two calls, each paying a
Python start and a bridge round trip (10-20 s a move, up from 3.5-5). `act
--observe` prints, after a sent act, the page `observe --brief` would print
next, from the same process and the same settled read; the lane's `a` script
passes it.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from unittest import mock

import pytest

from understudy import blindplay, blindplay_shape
from tier0.tests.test_understudy_blindplay import combat_state, map_state

REPO = Path(__file__).resolve().parents[2]
GO = 'go "Monster (path 1)"'


class _Wire:
    """A wire that answers `before` until the first POST and `after` from
    then on, recording every POST."""

    def __init__(self, before, after):
        self.before, self.after = before, after
        self.posts = []

    def get_state(self):
        return json.loads(json.dumps(self.after if self.posts
                                     else self.before))

    def post(self, action, **kw):
        self.posts.append((action, kw))
        return {"status": "ok", "message": f"Doing {action}"}


@pytest.fixture
def lane(monkeypatch):
    """The conftest's per-test lane root, lane 3, with a cap of 10. The
    settles are pass-throughs: theirs is the real bridge, bound at import,
    and both reads (the act's and the page's) go through the one
    `_load_state` either way."""
    monkeypatch.setattr(blindplay, "settle", lambda s, *a, **k: s)
    monkeypatch.setattr(blindplay, "settle_board", lambda s, *a, **k: s)
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", None)
    monkeypatch.setenv("GITS_LANE", "3")
    monkeypatch.delenv(blindplay_shape.MAX_ACTIONS_ENV, raising=False)
    blindplay.set_budget(10)
    yield
    blindplay.forget_fight()


def _fresh_lane(monkeypatch, tag: str) -> None:
    monkeypatch.setenv("GITS_LANE", tag)
    blindplay.set_budget(10)
    blindplay.forget_fight()
    blindplay.forget_briefed()


def _act(command=GO, **kw):
    return argparse.Namespace(raw_file=kw.get("raw_file", ""),
                              dry_run=kw.get("dry_run", False),
                              brief=True, observe=kw.get("observe", True),
                              command=command)


def test_act_observe_prints_what_act_then_observe_would(lane, monkeypatch,
                                                        capsys):
    """The page after the act is the page a separate `observe --brief` call
    would print, with the lane's `actions:` line printed once, by the act."""
    # Two calls on lane 4: `act`, then `observe`.
    _fresh_lane(monkeypatch, "4")
    wire = _Wire(map_state(), combat_state())
    with mock.patch.object(blindplay, "bridge", wire):
        assert blindplay.cmd_act(_act(observe=False)) == 0
        acted = capsys.readouterr().out
        assert blindplay.cmd_observe(argparse.Namespace(
            raw_file="", brief=True)) == 0
        observed = capsys.readouterr().out

    # One call on lane 5: `act --observe`.
    _fresh_lane(monkeypatch, "5")
    wire = _Wire(map_state(), combat_state())
    with mock.patch.object(blindplay, "bridge", wire):
        assert blindplay.cmd_act(_act()) == 0
    one = capsys.readouterr().out

    assert len(wire.posts) == 1
    assert acted.rstrip().endswith("actions: 1 of 10")
    page, _, budget_line = observed.rstrip().rpartition("\n\n")
    assert budget_line == "actions: 1 of 10 on this lane"
    assert one == acted + "\n" + page + "\n"
    assert one.count("actions:") == 1


def test_the_page_is_read_after_the_post(lane, capsys):
    """The page is the screen the act led to, not the one it was typed on."""
    wire = _Wire(map_state(), combat_state())
    with mock.patch.object(blindplay, "bridge", wire):
        blindplay.forget_fight()
        blindplay.forget_briefed()
        assert blindplay.cmd_act(_act()) == 0
    out = capsys.readouterr().out
    blindplay.forget_fight()
    blindplay.forget_briefed()
    combat = blindplay._page(blindplay.screen_page(combat_state(),
                                                   full=False),
                             argparse.Namespace(brief=True))
    # The combat page's own first line, which the map page never prints.
    first = combat.strip().splitlines()[0]
    assert first in out
    assert out.index("actions: 1 of 10") < out.index(first)


@pytest.mark.parametrize("how", ["raw_file", "dry_run"])
def test_no_page_on_a_saved_state_or_a_dry_run(lane, tmp_path, capsys, how):
    raw = tmp_path / "map.json"
    raw.write_text(json.dumps(map_state()), encoding="utf-8")
    wire = _Wire(map_state(), combat_state())
    kw = {"raw_file": str(raw)} if how == "raw_file" else {"dry_run": True}
    with mock.patch.object(blindplay, "bridge", wire):
        assert blindplay.cmd_act(_act(**kw)) == 0
    out = capsys.readouterr().out
    assert out.startswith("Not sent")
    assert out.strip().count("\n") == 0
    assert wire.posts == []


def test_a_refused_act_prints_the_unchanged_page(lane, capsys):
    """Nothing was posted, so the page is the read the act already made."""
    wire = _Wire(map_state(), combat_state())
    with mock.patch.object(blindplay, "bridge", wire):
        assert blindplay.cmd_act(_act('go "Nowhere"')) == 1
    out = capsys.readouterr().out
    assert out.startswith("REFUSED: ")
    blindplay.forget_briefed()
    page = blindplay._page(blindplay.screen_page(map_state(), full=False),
                           argparse.Namespace(brief=True))
    assert page.strip().splitlines()[0] in out
    assert wire.posts == []
    assert blindplay.budget_spent() == (0, 10)


def test_without_the_flag_act_prints_no_page(lane, capsys):
    wire = _Wire(map_state(), combat_state())
    with mock.patch.object(blindplay, "bridge", wire):
        assert blindplay.cmd_act(_act(observe=False)) == 0
        assert blindplay.cmd_act(_act('go "Nowhere"', observe=False)) == 1
    out = capsys.readouterr().out.strip().splitlines()
    assert out[-1].startswith("REFUSED: ")
    assert out[-2] == "actions: 1 of 10"


def test_the_parser_takes_the_flag():
    with mock.patch.object(blindplay, "cmd_act", return_value=0) as cmd:
        assert blindplay.main(["act", GO, "--brief", "--observe"]) == 0
    assert cmd.call_args.args[0].observe is True


# ---- the lane scripts ------------------------------------------------------

def _seat():
    spec = importlib.util.spec_from_file_location(
        "seat_tool_1009", REPO / "tools" / "seat.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_act_script_observes_and_the_observe_script_is_unchanged():
    scripts = _seat().lane_scripts(2)
    assert ('-m understudy.blindplay act --brief --observe "$@"\n'
            in scripts["a"])
    assert ('-m understudy.blindplay observe --brief "$@"\n'
            in scripts["o"])
    assert "--observe" not in scripts["o"]


def test_the_brief_tells_the_seat_the_act_script_prints_the_page(tmp_path):
    seat = _seat()
    text = seat.brief_text(2, "KLEEMOD-KLEE", scratch=str(tmp_path))
    assert "to act, which also prints the new page" in text
    assert "`act --observe`" in text
