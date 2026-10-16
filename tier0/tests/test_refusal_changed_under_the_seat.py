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


# ---- a numbered copy played since the look (Kokomi seat, lane 5, 2026-10-14)
#
# The seat sent `play "Sting (1)"` four times in one batch. The first played
# it; that copy was gone from the page the seat had read, the other three were
# refused, and three refusals in a row tripped the sticky REFUSAL STOP in act
# 3 with the seat alive. A numbered copy that was on the last look and has
# since been played (or left the hand) is now a skip: not sent, not counted,
# and never re-aimed at another copy -- the seat chooses.

def _sting(**over):
    from tier0.tests.test_kokomi_round_2_fixes_2026_10_13 import _guard
    return _guard(**dict({"id": "KLEEMOD-STING", "name": "Sting",
                          "description": "Deal 3 damage."}, **over))


def _hand_of(cards):
    from tier0.tests.test_kokomi_round_2_fixes_2026_10_13 import _fight
    return _fight(cards)


def _drop(state, title, n=1):
    """The same board with the first `n` copies of `title` gone."""
    state = copy.deepcopy(state)
    hand = state["player"]["hand"]
    for _ in range(n):
        hand.pop(next(i for i, c in enumerate(hand) if c["name"] == title))
    for i, c in enumerate(hand):
        c["index"] = i
    return state


def test_four_chained_plays_of_one_numbered_copy_skip_three(lane, capsys):
    screen, posted = lane
    screen["now"] = _hand_of([_sting() for _ in range(3)])
    assert blindplay.cmd_observe(_observe()) == 0
    assert "Sting (3)" in capsys.readouterr().out
    assert blindplay.cmd_act(_act('play "Sting (1)"')) == 0
    assert len(posted) == 1
    screen["now"] = _drop(screen["now"], "Sting")
    capsys.readouterr()
    for _ in range(3):
        assert blindplay.cmd_act(_act('play "Sting (1)"')) == 1
        out = capsys.readouterr().out
        assert out.startswith('Skipped: "Sting (1)" was played since your '
                              'last look: nothing was sent, and this is not '
                              'counted as a refusal.'), out
        assert "look again" in out
        assert "REFUSED" not in out and "REFUSAL STOP" not in out
    assert blindplay_shape.refusal_streak() == 0
    # Never re-aimed: the two Stings left were not played for the seat.
    assert len(posted) == 1
    # A genuine refusal on the same board still counts.
    assert blindplay.cmd_act(_act('play "No Such Card"')) == 1
    assert "REFUSED" in capsys.readouterr().out
    assert blindplay_shape.refusal_streak() == 1


def test_a_copy_that_left_the_hand_unplayed_is_a_skip(lane, capsys):
    screen, posted = lane
    screen["now"] = _hand_of([_sting(), _sting(), _sting(name="Ward")])
    assert blindplay.cmd_observe(_observe()) == 0
    capsys.readouterr()
    # Both Stings left the hand (discarded, exhausted) without this seat
    # playing them.
    screen["now"] = _drop(screen["now"], "Sting", n=2)
    assert blindplay.cmd_act(_act('play "Sting (2)"')) == 1
    out = capsys.readouterr().out
    assert out.startswith('Skipped: "Sting (2)" left your hand since your '
                          'last look'), out
    assert blindplay_shape.refusal_streak() == 0
    assert posted == []


def test_a_copy_printed_differently_now_is_still_that_copy(lane, capsys):
    screen, posted = lane
    screen["now"] = _hand_of([_sting(), _sting(cost="0"), _sting()])
    assert blindplay.cmd_observe(_observe()) == 0
    capsys.readouterr()
    # Every copy left now prints a face the page never showed. Yae seats
    # (2026-10-14): a number is the card's while it is in hand, so "(2)" is
    # still the middle copy -- not a refusal, and not another copy.
    moved = copy.deepcopy(screen["now"])
    for card in moved["player"]["hand"]:
        card["cost"] = "2"
    moved["player"]["hand"][1]["cost"] = "3"
    screen["now"] = moved
    assert blindplay.cmd_act(_act('play "Sting (2)"')) == 0
    assert blindplay_shape.refusal_streak() == 0
    assert [p[2]["card_index"] for p in posted] == [1]


def test_the_skip_line_reads_names_with_quotes_in_them():
    from understudy import blindplay_grammar as g
    for name in ("Sting (1)", "Kokomi's Ward (2)"):
        for template, what in ((g.SHOWN_CARD_PLAYED, "was played"),
                               (g.SHOWN_CARD_GONE, "left your hand")):
            line = g.copy_left_since_look(template.format(name=name))
            assert line.startswith(f'Skipped: "{name}" {what} since your '
                                   f'last look'), line
    assert g.copy_left_since_look(
        g.SHOWN_CARD_GONE.format(name="Sting (2)")
        + " as it was printed; the copies now: Sting (1)") == ""
    assert g.copy_left_since_look("no card named 'Sting (9)'") == ""
