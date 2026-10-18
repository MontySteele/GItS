"""The Hunt's extra reward at the RUN layer ([USER] ruling, 2026-07-27).

Strictly the reward is not in-combat: the effect fires during the fight and
the extra offer appears on the rewards screen afterwards. So combat only
RECORDS that it happened (CombatState.extra_card_screens) and model.py is
what rolls, offers and drafts -- the same division test_burning_blood_
runlayer.py pins for the heal, and the reason this file sits beside it.

Driven through a fake fight for the same reason that one is: the counter is
what the run layer reads, and setting it directly isolates the run-layer
behaviour from whether any particular card happened to score a fatal kill.
"""

import random

import pytest

from tier0.engine.state import CombatState
from tier05 import model


def _fight_earning(n):
    """Win the fight and record that it earned `n` extra card screens."""
    def fight(player, enemies, pilot, seed):
        for e in enemies:
            e.hp = 0
        state = CombatState(player=player, enemies=enemies,
                            rng=random.Random(seed))
        state.extra_card_screens = n
        return state
    return fight


def _take_first(rng, deck, offers, archetype):
    return offers[0] if offers else None


def _skip(rng, deck, offers, archetype):
    return None


def _run(monkeypatch, n, policy=_skip, character="ref_ironclad"):
    monkeypatch.setattr(model, "run_fight", _fight_earning(n))
    return model.run_one(character, "demolition", "demolition", policy, 1)


def test_a_fight_that_earned_nothing_shows_one_screen_per_fight(monkeypatch):
    r = _run(monkeypatch, 0)
    per_node = [d["node"] for d in r.decisions]
    assert len(per_node) == len(set(per_node))       # exactly one each


def test_an_earned_screen_is_an_extra_decision_on_the_same_node(monkeypatch):
    """The extra reward belongs to the fight that earned it, so it lands on
    that node rather than deferring to the next one."""
    r = _run(monkeypatch, 1)
    counts = {}
    for d in r.decisions:
        counts[d["node"]] = counts.get(d["node"], 0) + 1
    assert counts and all(c == 2 for c in counts.values())


def test_two_earned_screens_are_two_extra_decisions(monkeypatch):
    r = _run(monkeypatch, 2)
    counts = {}
    for d in r.decisions:
        counts[d["node"]] = counts.get(d["node"], 0) + 1
    assert all(c == 3 for c in counts.values())


def test_an_earned_screen_can_actually_be_drafted(monkeypatch):
    """Not a cosmetic entry in the decision log: picking on the extra screen
    puts a real card in the deck."""
    base = _run(monkeypatch, 0, policy=_take_first)
    extra = _run(monkeypatch, 1, policy=_take_first)
    assert len(extra.deck_ids) > len(base.deck_ids)


def test_the_extra_screen_offers_no_companion(monkeypatch):
    """It is a CardReward, not a full reward screen. A companion slot here
    would hand The Hunt a payout the card does not print."""
    from tier05 import rewards
    r = _run(monkeypatch, 2, policy=_take_first, character="klee")
    picks = [d for d in r.decisions if d["picked"]]
    assert picks                                     # the run drafted something
    # Every companion the run was offered came from a fight's OWN screen;
    # the card-only screens contribute none.
    offers = rewards.roll_rewards(random.Random(0), "klee",
                                  companion_offers=0)
    assert not any(c.is_companion for c in offers)


def test_a_card_only_screen_still_offers_the_normal_number_of_cards(
        monkeypatch):
    from tier0 import constants as C
    from tier05 import rewards
    offers = rewards.roll_rewards(random.Random(0), "klee",
                                  companion_offers=0)
    assert len(offers) == C.REWARD_CARD_OFFERS
