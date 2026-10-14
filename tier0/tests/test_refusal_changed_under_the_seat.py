"""A command refused because the fight changed under it since the seat's
last look is a skip, not a refusal (co-op Spiral Abyss 2026-10-14, lanes 4
host Klee / 5 client Varka, twice in one night).

The client chained `play` commands; the host's Bombs killed the last enemy
(or the named one) in between, the rest were refused, and three in a row
tripped the sticky REFUSAL STOP. Now a refusal whose room changed since the
last `observe`, or whose target was alive on that look and is gone now, is
skipped: not sent, not counted. A refusal on the board the seat looked at --
a bad name, an unaffordable card -- still counts.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""
from __future__ import annotations

import argparse
import copy
import re

import pytest

from understudy import blindplay, blindplay_shape

from tier0.tests.test_understudy_blindplay import combat_state, map_state


@pytest.fixture
def lane(monkeypatch):
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", None)
    monkeypatch.setenv("GITS_LANE", "5")
    monkeypatch.delenv(blindplay_shape.MAX_ACTIONS_ENV, raising=False)
    monkeypatch.setattr(blindplay_shape, "lane_embark_stamp",
                        lambda lane=None: "")
    monkeypatch.setattr(blindplay, "_lane_guard", lambda args: "")
    monkeypatch.setattr(blindplay, "_warn_build_skew", lambda state: None)
    screen = {"now": combat_state()}
    monkeypatch.setattr(blindplay, "_live_load",
                        lambda args, **kw: screen["now"])
    posted: list = []
    monkeypatch.setattr(blindplay, "post_when_the_room_is_open",
                        lambda *a, **kw: posted.append(a) or {})
    blindplay.forget_run()
    yield screen, posted
    blindplay.forget_run()


def _act(command):
    return argparse.Namespace(raw_file="", dry_run=False, brief=True,
                              command=command)


def _observe():
    return argparse.Namespace(raw_file="", brief=True, define="")


def _enemies(state):
    return state["battle"]["enemies"]


def _nibbit_dead(state, *, second_alive: bool):
    """The same board with the Nibbit killed by the partner, and (if asked)
    a second enemy still standing so the fight goes on."""
    state = copy.deepcopy(state)
    nibbit = _enemies(state)[0]
    if second_alive:
        slug = copy.deepcopy(nibbit)
        slug.update(name="Slug", entity_id="SLUG_0", hp=10)
        _enemies(state).append(slug)
    nibbit["hp"] = 0
    return state


def test_the_fixture_has_one_living_nibbit():
    names = [e["name"] for e in _enemies(combat_state())]
    assert names == ["Nibbit"]
    assert blindplay.living_targets(combat_state()) == ["nibbit", "a"]


def test_a_target_the_partner_killed_is_skipped_and_holds_end_turn(
        lane, capsys):
    screen, posted = lane
    assert blindplay.cmd_observe(_observe()) == 0
    capsys.readouterr()
    screen["now"] = _nibbit_dead(combat_state(), second_alive=True)
    for command in ('play "Pearl Barrage" on "Nibbit"',
                    'play "All Streams Flow to the Sea" on "A"',
                    'play "Pearl Barrage" on "Nibbit"'):
        assert blindplay.cmd_act(_act(command)) == 1
        out = capsys.readouterr().out
        assert re.match(r'Skipped: "(Nibbit|A)" is gone since your last '
                        r'look: nothing was sent', out), out
        assert "is gone since your last look" in out
        assert "not counted as a refusal. Look again." in out
        assert "REFUSED" not in out
    assert blindplay_shape.refusal_streak() == 0
    assert posted == []
    # A chained `end turn` on the same board is held once, so the turn the
    # seat meant to spend on that card is not thrown away unseen.
    assert blindplay.cmd_act(_act("end turn")) == 1
    assert "REFUSED: your last command this turn" in capsys.readouterr().out
    assert blindplay_shape.refusal_streak() == 0


def test_every_enemy_down_is_a_skip(lane, capsys):
    screen, posted = lane
    assert blindplay.cmd_observe(_observe()) == 0
    capsys.readouterr()
    screen["now"] = _nibbit_dead(combat_state(), second_alive=False)
    for _ in range(4):
        assert blindplay.cmd_act(_act('play "Pearl Barrage"')) == 1
        out = capsys.readouterr().out
        assert out.startswith("Skipped: every enemy went down since your "
                              "last look"), out
    assert blindplay_shape.refusal_streak() == 0
    assert posted == []


def test_a_partner_moving_the_screen_is_a_skip(lane, capsys):
    screen, posted = lane
    assert blindplay.cmd_observe(_observe()) == 0
    capsys.readouterr()
    # Nothing this seat sent left the fight: the partner did.
    screen["now"] = map_state()
    for command in ('play "Pearl Barrage" on "Nibbit"', "confirm",
                    "end turn"):
        assert blindplay.cmd_act(_act(command)) == 1
        out = capsys.readouterr().out
        assert out.startswith("Skipped: the fight ended since your last "
                              "look"), out
        assert "## What you can say" in out
    assert blindplay_shape.refusal_streak() == 0
    assert posted == []
    # A look on the new screen ends it: refusals there are refusals.
    assert blindplay.cmd_observe(_observe()) == 0
    capsys.readouterr()
    assert blindplay.cmd_act(_act("confirm")) == 1
    assert "REFUSED" in capsys.readouterr().out
    assert blindplay_shape.refusal_streak() == 1


def test_a_bad_target_name_still_counts(lane, capsys):
    screen, posted = lane
    assert blindplay.cmd_observe(_observe()) == 0
    capsys.readouterr()
    for command in ('play "Pearl Barrage" on "Gremlin Nob"',
                    'play "No Such Card"'):
        assert blindplay.cmd_act(_act(command)) == 1
        assert "REFUSED" in capsys.readouterr().out
    assert blindplay_shape.refusal_streak() == 2
    # Naming an enemy the look never showed alive is a bad name even after
    # the board changed.
    screen["now"] = _nibbit_dead(combat_state(), second_alive=True)
    assert blindplay.cmd_act(_act('play "Pearl Barrage" on "Gremlin"')) == 1
    assert "REFUSAL STOP: 3 commands in a row" in capsys.readouterr().out
    assert posted == []


def test_an_unaffordable_card_still_counts(lane, capsys):
    screen, posted = lane
    assert blindplay.cmd_observe(_observe()) == 0
    capsys.readouterr()
    broke = copy.deepcopy(combat_state())
    for card in broke["player"]["hand"]:
        if card.get("name") == "Pearl Barrage":
            card["can_play"] = False
            card["unplayable_reason"] = "NotEnoughEnergy"
    screen["now"] = broke
    assert blindplay.cmd_act(_act('play "Pearl Barrage" on "Nibbit"')) == 1
    out = capsys.readouterr().out
    assert out.startswith("REFUSED: 'Pearl Barrage' cannot be played"), out
    assert blindplay_shape.refusal_streak() == 1


def test_a_stale_look_does_not_skip(lane):
    blindplay_shape.remember_look("fight", ["nibbit"], now=0.0)
    assert blindplay_shape.read_look(now=1.0)["room"] == "fight"
    late = blindplay_shape.REFUSAL_MARK_TTL_S + 1.0
    assert blindplay_shape.read_look(now=late) is None


def test_reset_refusals_clears_the_look(lane, capsys):
    blindplay_shape.remember_look("fight", ["nibbit"])
    assert blindplay.main(["reset-refusals", "--lane", "lane5"]) == 0
    assert blindplay_shape.read_look() is None
