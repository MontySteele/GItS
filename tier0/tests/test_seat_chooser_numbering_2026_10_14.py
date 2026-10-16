"""A hand chooser names each card by the label the fight page gave THAT card
(Yae bloom r4 seat, 2026-10-14, on the build with #1290).

Turn 1: Sakura Seal's Edit went on `Defend (1)` through the hand chooser,
then Proofread's Edit was aimed at `Defend (2)` and landed on the sealed
copy, replacing the Seal. The bridge posts a chooser pick by its place among
the hand's UI holders (`ExecuteCombatSelectCard`, `hand.ActiveHolders`),
while the fight page's hand is the combat pile (`combatState.Hand.Cards`); a
card that went through a selection need not come back to the same place
among the holders. The chooser used to give its own list the remembered
hand's labels in order, so a moved holder took its neighbour's number.

Now the chooser finds each offered card in the hand by its face
(`blindplay_faces.chooser_labels`), and a card picked through a chooser keeps
its label on the next look wherever it lands (`hand_card_picked`).

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""
from __future__ import annotations

import copy

import pytest

from understudy import blindplay, blindplay_faces

from tier0.tests.test_refusal_changed_under_the_seat import (  # noqa: F401
    _act, _hand_of, _observe, _sting, lane)


def _card(name, text, **over):
    return _sting(**dict({"id": name.upper().replace(" ", "_"),
                          "name": name, "description": text,
                          "cost": "0", "type": "Skill",
                          "target_type": "Self"}, **over))


def _defend():
    return _card("Defend", "Gain 5 Block.", cost="1")


class _Game:
    """The two orders the bridge reads: the combat pile (the fight page's
    hand, `play_card`'s index) and the hand's UI holders (the chooser's list,
    `combat_select_card`'s index). Each physical card carries a uid held
    here, never on the wire."""

    def __init__(self, cards, *, pile_moves: bool):
        self.cards = {i: c for i, c in enumerate(cards)}
        self.pile = list(self.cards)
        self.ui = list(self.cards)
        self.pile_moves = pile_moves

    def combat(self, base):
        state = copy.deepcopy(base)
        state["state_type"] = base.get("state_type", "monster")
        state.pop("hand_select", None)
        state["player"]["hand"] = [dict(self.cards[u], index=i)
                                   for i, u in enumerate(self.pile)]
        return state

    def chooser(self, base, played):
        """The Edit's hand chooser: every card in hand but the one played."""
        state = self.combat(base)
        state["state_type"] = "hand_select"
        state["hand_select"] = {
            "mode": "simple_select", "prompt": "Choose a card to Edit.",
            "cards": [dict(self.cards[u], index=i)
                      for i, u in enumerate(u for u in self.ui
                                            if u != played)],
            "can_confirm": False}
        return state

    def play(self, pile_index):
        uid = self.pile[pile_index]
        self.pile.remove(uid)
        self.ui.remove(uid)
        return uid

    def chooser_uid(self, played, index):
        return [u for u in self.ui if u != played][index]

    def edit(self, uid, annotation):
        card = self.cards[uid]
        card["description"] = "Gain 5 Block. " + annotation + "."
        card["enchantment"] = {"id": annotation.upper(), "name": annotation,
                               "description": annotation, "amount": 1,
                               "shows_amount": False}
        # The selected holder comes back at the end of the hand's UI row.
        self.ui.remove(uid)
        self.ui.append(uid)
        if self.pile_moves:
            self.pile.remove(uid)
            self.pile.append(uid)


def _look(capsys):
    capsys.readouterr()
    assert blindplay.cmd_observe(_observe()) == 0
    return capsys.readouterr().out


def _label_of(game, state, uid):
    return blindplay_faces.hand_labels(state, remember=False)[
        game.pile.index(uid)]


@pytest.mark.parametrize("pile_moves", [False, True])
def test_the_second_edit_lands_on_the_copy_the_page_named(
        lane, capsys, pile_moves):
    screen, posted = lane
    game = _Game([_card("Sakura Seal", "Edit a card in your hand: "
                                       "Sakura Seal."),
                  _card("Proofread", "Edit a card in your hand: Red Ink."),
                  _defend(), _defend(), _defend()], pile_moves=pile_moves)
    base = _hand_of([])
    screen["now"] = game.combat(base)
    page = _look(capsys)
    assert "Defend (1)" in page and "Defend (3)" in page
    d1, d2, d3 = game.pile[2:]

    # Sakura Seal, then its Edit on Defend (1) through the chooser.
    assert blindplay.cmd_act(_act('play "Sakura Seal"')) == 0
    seal = game.play(posted[-1][2]["card_index"])
    screen["now"] = game.chooser(base, seal)
    _look(capsys)
    assert blindplay.cmd_act(_act('choose "Defend (1)"')) == 0
    assert posted[-1][1] == "combat_select_card"
    picked = game.chooser_uid(seal, posted[-1][2]["card_index"])
    assert picked == d1
    assert blindplay.cmd_act(_act("confirm")) == 0
    game.edit(picked, "Sakura Seal")
    screen["now"] = game.combat(base)

    # The look after the Edit: the sealed copy is still Defend (1).
    page = _look(capsys)
    assert _label_of(game, screen["now"], d1) == "Defend (1)"
    assert _label_of(game, screen["now"], d2) == "Defend (2)"
    assert _label_of(game, screen["now"], d3) == "Defend (3)"

    # Proofread, and its Edit on Defend (2), the copy the page named (2).
    assert blindplay.cmd_act(_act('play "Proofread"')) == 0
    proof = game.play(posted[-1][2]["card_index"])
    assert game.cards[proof]["name"] == "Proofread"
    screen["now"] = game.chooser(base, proof)
    page = _look(capsys)
    labels = blindplay_faces.chooser_labels(
        screen["now"], screen["now"]["hand_select"]["cards"])
    by_uid = dict(zip([u for u in game.ui if u != proof], labels))
    assert by_uid == {d1: "Defend (1)", d2: "Defend (2)", d3: "Defend (3)"}
    assert blindplay.cmd_act(_act('choose "Defend (2)"')) == 0
    assert game.chooser_uid(proof, posted[-1][2]["card_index"]) == d2
    assert blindplay.cmd_act(_act("confirm")) == 0
    game.edit(d2, "Red Ink")
    screen["now"] = game.combat(base)
    _look(capsys)
    # Each Annotated copy keeps the label it was Edited under.
    assert _label_of(game, screen["now"], d1) == "Defend (1)"
    assert _label_of(game, screen["now"], d2) == "Defend (2)"
    assert _label_of(game, screen["now"], d3) == "Defend (3)"
    assert game.cards[d1]["enchantment"]["name"] == "Sakura Seal"


def test_a_card_picked_to_leave_the_hand_takes_its_number_with_it(lane):
    """A discard chooser: the copy picked goes, and its number is not
    handed to the copy left behind."""
    screen, _ = lane
    state = _hand_of([_defend(), _defend(), _defend()])
    assert blindplay_faces.hand_labels(state) == [
        "Defend (1)", "Defend (2)", "Defend (3)"]
    chooser = copy.deepcopy(state)
    chooser["state_type"] = "hand_select"
    chooser["hand_select"] = {"cards": copy.deepcopy(state["player"]["hand"]),
                              "can_confirm": False}
    blindplay_faces.hand_card_picked(chooser, 1)
    after = copy.deepcopy(state)
    del after["player"]["hand"][1]
    assert blindplay_faces.hand_labels(after) == ["Defend (1)", "Defend (3)"]


def test_the_chooser_lists_the_hand_in_hand_order(lane, capsys):
    """A Yae seat (2026-10-14): the Edit chooser listed the holders' order,
    not the hand's, and the seat picked the wrong card twice. The page now
    prints a hand chooser in the order the fight page printed the hand, with
    the same labels, and `choose` still posts the bridge's own index."""
    screen, posted = lane
    game = _Game([_card("Sakura Seal", "Edit a card in your hand: "
                                       "Sakura Seal."),
                  _card("Proofread", "Edit a card in your hand: Red Ink."),
                  _defend(), _card("Strike", "Deal 6 damage.", cost="1"),
                  _defend()], pile_moves=False)
    base = _hand_of([])
    screen["now"] = game.combat(base)
    _look(capsys)
    d1, strike, d2 = game.pile[2:]
    assert blindplay.cmd_act(_act('play "Sakura Seal"')) == 0
    seal = game.play(posted[-1][2]["card_index"])
    screen["now"] = game.chooser(base, seal)
    _look(capsys)
    assert blindplay.cmd_act(_act('choose "Defend (1)"')) == 0
    assert game.chooser_uid(seal, posted[-1][2]["card_index"]) == d1
    assert blindplay.cmd_act(_act("confirm")) == 0
    game.edit(d1, "Sakura Seal")          # its holder moves to the end
    screen["now"] = game.combat(base)
    _look(capsys)

    assert blindplay.cmd_act(_act('play "Proofread"')) == 0
    proof = game.play(posted[-1][2]["card_index"])
    screen["now"] = game.chooser(base, proof)
    # The holders' order is Strike, Defend (2), Defend (1); the hand's is
    # Defend (1), Strike, Defend (2).
    assert [u for u in game.ui if u != proof] == [strike, d2, d1]
    page = _look(capsys)
    at = [page.index(t) for t in ("Defend (1)", "Strike", "Defend (2)")]
    assert at == sorted(at)
    for name, uid in (("Defend (1)", d1), ("Strike", strike),
                      ("Defend (2)", d2)):
        assert blindplay.cmd_act(_act(f'choose "{name}"')) == 0
        assert game.chooser_uid(proof, posted[-1][2]["card_index"]) == uid
