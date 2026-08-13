"""Book of Five Rings counts event deck-adds (EB-111).

The C# relic ticks in `BookOfFiveRings.AfterCardChangedPiles` on
`pile.Type == PileType.Deck` -- and `PileType.Deck` is the MASTER deck
("where cards live between rooms", per the enum's own doc comment on the
pinned assembly), not a combat pile. So every card that enters the deck ticks
it, whatever put it there. The sim wired only two of the ~10 add sites (shop
buys, reward picks) and every event add went uncounted.

Two levels here: the event resolver tallies each add site into
`EventState.cards_added`, and the run layer hands that total to
`HeldRelics.note_cards_added`. The tally is per-site by construction rather
than a net `len(deck_ids)` diff, because a diff undercounts an option that
removes N and adds M -- the game counts M.
"""

from __future__ import annotations

import random

import pytest

from tier0.content import loader
from tier05 import events, model
from tier05.tests.test_relics_runlayer import (  # noqa: F401  (fixtures)
    ARCH, BASE_HP, CHAR, PILOT, SEED, _legacy_spine, _single_act, _win_stub)


def _state(deck_ids=None):
    return events.EventState(
        character=CHAR, archetype=ARCH, hp=40, max_hp=BASE_HP, gold=0,
        deck_ids=list(deck_ids if deck_ids is not None else _starter_deck()))


def _starter_deck():
    return list(loader._character_index()[CHAR]["starting_deck"])


def _resolve(opt, st, seed=3):
    events.resolve(random.Random(seed), {"id": "test_event"}, opt, st)


# --- the door: every event add site feeds it ------------------------------

def test_add_card_is_counted():
    st = _state()
    _resolve({"label": "x", "add_card": "curse_guilty"}, st)
    assert st.cards_added == 1


def test_curse_is_counted():
    st = _state()
    _resolve({"label": "x", "curse": "curse_guilty"}, st)
    assert st.cards_added == 1


def test_random_card_counts_each_body():
    st = _state()
    _resolve({"label": "x", "random_card": {"n": 3}}, st)
    assert st.cards_added == 3


def test_card_reward_counts_the_pick():
    st = _state()
    _resolve({"label": "x", "card_reward": 3}, st)
    assert st.cards_added == 1


def test_card_screens_counts_one_pick_per_screen():
    st = _state()
    _resolve({"label": "x", "card_screens": 2}, st)
    assert st.cards_added == 2


def test_pick_cards_counts_every_take():
    st = _state()
    _resolve({"label": "x", "pick_cards": {"of": 5, "take": 2}}, st)
    assert st.cards_added == 2


def test_duplicate_deck_counts_the_whole_copy():
    deck = _starter_deck()
    st = _state(deck)
    _resolve({"label": "x", "duplicate_deck": True}, st)
    assert st.cards_added == len(deck)


def test_transform_counts_the_replacement_not_the_net_change():
    """A remove-one/add-one option nets zero cards and still ticks the Book
    once: the game counts the card that ARRIVED. This is the case a
    `len(deck_ids)` diff gets wrong."""
    deck = _starter_deck()
    st = _state(deck)
    _resolve({"label": "x", "transform": 1}, st)
    assert len(st.deck_ids) == len(deck)          # net zero
    assert st.cards_added == 1                    # one card still arrived


# --- the wiring: the run layer pays the heal ------------------------------

def test_run_layer_pays_the_book_heal_for_event_adds(monkeypatch,
                                                     scripted_map):
    """A run holding the Book meets one event that adds 5 cards; the 5th
    completes a chunk, so the run leaves the event 20 HP up on the same run
    without the relic. Before EB-111 the event's adds were invisible to
    `held` and the two runs matched exactly."""
    def _five_adds(rng, act, st, seen, held=None, bag=None, policy=None,
                   policy_rng=None):
        for _ in range(5):
            st.deck_ids.append("curse_guilty")
            st.note_add()
        st.log.append({"event": "stub_five_adds", "option": "x"})

    monkeypatch.setattr(events, "visit", _five_adds)
    monkeypatch.setattr(model, "run_fight", _win_stub(20))
    scripted_map(["N", "event", "B"])

    base = model.run_one(CHAR, ARCH, PILOT, _skip, SEED)
    book = model.run_one(CHAR, ARCH, PILOT, _skip, SEED,
                         relics=["book_of_five_rings"])

    assert base.node_kinds == ["N", "event", "B"]
    assert base.hp_by_node[1] == BASE_HP - 20     # the event itself is free
    assert book.hp_by_node[1] == min(BASE_HP, base.hp_by_node[1] + 20)
    assert book.hp_by_node[1] > base.hp_by_node[1]


def _skip(rng, deck, offers, archetype):
    return None
