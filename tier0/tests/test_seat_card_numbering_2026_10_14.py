"""A hand number names one card until that card leaves the hand (Yae seats,
2026-10-14; a Furina seat before).

Three blind seats saw `Strike (1)` / `Defend (2)` move to another copy: after
a play the next page re-counted the hand, and after an Edit (Red Ink on a
Strike) the copy was found again by its OLD face, which now belonged to the
other Strike. The label is now tracked card by card across the hand
(`blindplay_faces.hand_labels`): a played copy's number leaves with it, an
edited card keeps its number, and a card new to the hand takes a fresh one.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""
from __future__ import annotations

import copy

from understudy import blindplay, blindplay_faces, blindplay_shape

from tier0.tests.test_refusal_changed_under_the_seat import (  # noqa: F401
    _act, _hand_of, _observe, _sting, lane)


def _strike(**over):
    return _sting(**dict({"id": "STRIKE", "name": "Strike",
                          "description": "Deal 6 damage."}, **over))


def _defend(**over):
    return _sting(**dict({"id": "DEFEND", "name": "Defend",
                          "description": "Gain 5 Block."}, **over))


def _played(state, index):
    """The game's answer to the play just sent: that card leaves the hand."""
    state = copy.deepcopy(state)
    del state["player"]["hand"][index]
    for i, c in enumerate(state["player"]["hand"]):
        c["index"] = i
    return state


def _look(capsys) -> str:
    capsys.readouterr()
    assert blindplay.cmd_observe(_observe()) == 0
    return capsys.readouterr().out


def _sent(posted) -> int:
    return posted[-1][2]["card_index"]


def test_a_copy_keeps_its_number_after_another_copy_is_played(lane, capsys):
    screen, posted = lane
    screen["now"] = _hand_of([_strike(), _defend(), _strike(), _strike()])
    page = _look(capsys)
    assert "Strike (1)" in page and "Strike (3)" in page
    assert blindplay.cmd_act(_act('play "Strike (1)"')) == 0
    assert _sent(posted) == 0
    screen["now"] = _played(screen["now"], 0)
    # The next look does not re-count: the two left are still (2) and (3).
    page = _look(capsys)
    assert "Strike (2)" in page and "Strike (3)" in page
    assert "Strike (1)" not in page
    # And the old label of another copy still names that copy.
    assert blindplay.cmd_act(_act('play "Strike (3)"')) == 0
    assert _sent(posted) == 2
    screen["now"] = _played(screen["now"], 2)
    assert blindplay.cmd_act(_act('play "Strike (2)"')) == 0
    assert _sent(posted) == 1


def test_an_edit_that_changes_a_face_keeps_the_label(lane, capsys):
    screen, posted = lane
    screen["now"] = _hand_of([_strike(), _strike(), _defend(), _defend()])
    page = _look(capsys)
    assert "Strike (1)" in page and "Defend (2)" in page
    # Red Ink lands on Strike (1) and on Defend (2): new faces, same cards.
    edited = copy.deepcopy(screen["now"])
    for i in (0, 3):
        card = edited["player"]["hand"][i]
        card["description"] += " Red Ink."
        card["enchantment"] = {"id": "RED_INK", "name": "Red Ink"}
    screen["now"] = edited
    page = _look(capsys)
    assert "Strike (1)" in page and "Defend (2)" in page
    # The labels still name the edited cards, not the copies whose face now
    # matches the face the seat first read.
    assert blindplay.cmd_act(_act('play "Strike (1)"')) == 0
    assert _sent(posted) == 0
    screen["now"] = _played(screen["now"], 0)
    assert blindplay.cmd_act(_act('play "Defend (2)"')) == 0
    assert _sent(posted) == 2
    assert screen["now"]["player"]["hand"][2]["enchantment"]["name"] \
        == "Red Ink"


def test_an_edit_made_without_a_look_between_still_hits_the_edited_card(
        lane, capsys):
    screen, posted = lane
    screen["now"] = _hand_of([_strike(), _strike()])
    _look(capsys)
    edited = copy.deepcopy(screen["now"])
    edited["player"]["hand"][0]["description"] += " Red Ink."
    screen["now"] = edited
    assert blindplay.cmd_act(_act('play "Strike (1)"')) == 0
    assert _sent(posted) == 0


def test_a_new_draw_takes_a_fresh_number(lane, capsys):
    screen, posted = lane
    screen["now"] = _hand_of([_strike(), _strike()])
    _look(capsys)
    assert blindplay.cmd_act(_act('play "Strike (1)"')) == 0
    screen["now"] = _played(screen["now"], 0)
    drawn = copy.deepcopy(screen["now"])
    drawn["player"]["hand"].append(dict(_strike(), index=1))
    screen["now"] = drawn
    # Typed before the next look: the played copy's label is a skip, and it
    # is never handed to the Strike just drawn.
    capsys.readouterr()
    assert blindplay.cmd_act(_act('play "Strike (1)"')) == 1
    assert "was played since your last look" in capsys.readouterr().out
    assert len(posted) == 1
    assert blindplay_shape.refusal_streak() == 0
    page = _look(capsys)
    # The new Strike is (3): neither the live (2) nor the played (1).
    assert "Strike (2)" in page and "Strike (3)" in page
    assert "Strike (1)" not in page
    assert blindplay.cmd_act(_act('play "Strike (3)"')) == 0
    assert _sent(posted) == 1


def test_a_number_no_card_carries_is_not_re_aimed(lane, capsys):
    screen, posted = lane
    screen["now"] = _hand_of([_strike(), _strike()])
    _look(capsys)
    assert blindplay.cmd_act(_act('play "Strike (1)"')) == 0
    screen["now"] = _played(screen["now"], 0)
    _look(capsys)
    # One Strike left, printed `Strike (2)`: `(1)` is not it.
    assert blindplay.cmd_act(_act('play "Strike (1)"')) == 1
    assert "REFUSED" in capsys.readouterr().out
    assert len(posted) == 1


def test_a_new_turn_numbers_a_fresh_hand_from_one(lane, capsys):
    screen, _ = lane
    screen["now"] = _hand_of([_strike(), _strike()])
    _look(capsys)
    blindplay.cmd_act(_act('play "Strike (1)"'))
    screen["now"] = _played(screen["now"], 0)
    _look(capsys)
    turn = _hand_of([_strike(), _strike(), _defend()])
    turn["battle"]["round"] = (screen["now"]["battle"].get("round") or 1) + 1
    screen["now"] = turn
    page = _look(capsys)
    assert "Strike (1)" in page and "Strike (2)" in page


def test_a_hand_chooser_prints_the_hand_labels():
    hand = _hand_of([_strike(), _strike(), _strike()])
    assert blindplay_faces.hand_labels(hand) == [
        "Strike (1)", "Strike (2)", "Strike (3)"]
    blindplay_faces.hand_card_left(hand, 0)
    after = _played(hand, 0)
    # An Edit's pick over the two left: the names the fight page printed.
    cards = copy.deepcopy(after["player"]["hand"])
    assert blindplay_faces.chooser_labels(after, cards) == [
        "Strike (2)", "Strike (3)"]
