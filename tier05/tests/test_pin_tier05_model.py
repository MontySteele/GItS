"""Pin tests for the run model's three unguarded arithmetic edges: the
campfire heal's max-HP cap and its truncation, the shop relic's gold debit,
and the rest-site defense quota's post-removal denominator.

Each test states the rule it locks and asserts the number the model produces
today; none of them encodes a preference about what the rule should be.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import CombatState
from tier05 import model


def _skip(rng, deck, offers, archetype):
    """Draft/shop policy that never takes an offer: isolates a run's node
    arithmetic from card-buying noise."""
    return None


def _win_fights(hit):
    """A run_fight stand-in that wins every fight for a fixed HP cost, so the
    HP a node is entered with is exact rather than combat-dependent."""
    def fight(player, enemies, pilot, seed):
        player.hp = max(1, player.hp - hit)
        for e in enemies:
            e.hp = 0
        return CombatState(player=player, enemies=enemies,
                           rng=random.Random(seed))
    return fight


# --- campfire heal: capped at max HP -------------------------------------

def test_rest_heal_is_capped_at_max_hp(monkeypatch, scripted_map):
    """A campfire heal can never leave a run above its maximum HP: the 30%-of-
    max heal is clamped to max_hp, so healing 18 onto 50/62 lands on 62, not
    68."""
    monkeypatch.setattr(model, "run_fight", _win_fights(12))
    scripted_map("NRB")                  # the rest leads only into the boss
    max_hp = loader._character_index()["klee"]["hp"]
    assert max_hp == 62

    res = model.run_one("klee", "demolition", "demolition", _skip, 0,
                        n_acts=1)

    assert res.node_kinds == ["N", "R", "B"]
    assert res.hp_by_node[0] == 50               # 62 - 12, entering the rest
    assert res.rests == [(1, "heal", None)]      # the rest healed
    # Uncapped this would be 50 + int(0.30 * 62) = 68.
    assert 50 + int(C.REST_HEAL_FRACTION * max_hp) == 68
    assert res.hp_by_node[1] == max_hp == 62
    assert all(hp <= max_hp for hp in res.hp_by_node)


def test_rest_heal_floors_rather_than_rounds(monkeypatch, scripted_map):
    """The campfire heal truncates. The authority lands its 30%-of-max heal
    through `SetCurrentHpInternal`, whose body is
    `CurrentHp = (int)Math.Min(amount, MaxHp)` — an explicit truncation — so
    Klee's 0.30 x 62 = 18.6 heals 18, not the 19 a round() would give
    (EB-110)."""
    monkeypatch.setattr(model, "run_fight", _win_fights(30))
    scripted_map("NRB")                  # the rest leads only into the boss
    max_hp = loader._character_index()["klee"]["hp"]
    assert max_hp == 62
    assert C.REST_HEAL_FRACTION * max_hp == pytest.approx(18.6)

    res = model.run_one("klee", "demolition", "demolition", _skip, 0,
                        n_acts=1)

    assert res.node_kinds == ["N", "R", "B"]
    assert res.hp_by_node[0] == 32               # 62 - 30, entering the rest
    assert res.rests == [(1, "heal", None)]      # the rest healed
    # Well clear of the max-HP cap, so the heal size itself is observable.
    assert res.hp_by_node[1] == 50               # 32 + 18, NOT 32 + 19


# --- shop relic: the 150g is actually debited ----------------------------

def test_shop_relic_purchase_debits_its_price_from_gold(scripted_map):
    """Buying a relic off the shop shelf costs SHOP_RELIC_PRICE gold: a run
    that banks two treasure lumps and buys one relic ends on start + income -
    price, not on the undebited income."""
    scripted_map("TT$")                  # two treasure lumps, then the shop

    res = model.run_one("klee", "demolition", "demolition", _skip, 0,
                        n_acts=1, grant_relics=True)

    relic_buys = [p for p in res.shop if p["buy"] == "relic"]
    assert len(relic_buys) == 1
    assert relic_buys[0]["price"] == C.SHOP_RELIC_PRICE == 150
    income = C.GOLD_START + 2 * C.TREASURE_GOLD          # 99 + 40 + 40
    assert income == 179
    assert res.gold == income - C.SHOP_RELIC_PRICE == 29


# --- rest-site thinning: the defense quota is judged AFTER the cut --------

def _quota_deck():
    """One basic block card plus five non-basic, non-block cards: the only
    thinnable basic is a blocker, and the deck holds exactly one block card."""
    return ["duck_and_cover"] + ["kaeya_frostgnaw"] * 5


def test_rest_keeps_block_card_when_cut_would_break_defense_quota():
    """A rest only thins a basic block card if the block density of the deck
    AS IT WOULD BE AFTER the cut still clears DRAFT_BLOCK_DENSITY_MIN: with 1
    block card in 6, the post-cut density is 0/5 = 0.0, so the blocker stays
    and the rest smiths instead."""
    deck = _quota_deck()
    n_block = 1
    assert (n_block - 1) / (len(deck) - 1) < C.DRAFT_BLOCK_DENSITY_MIN
    assert n_block / (len(deck) - 1) >= C.DRAFT_BLOCK_DENSITY_MIN   # pre-cut

    action, target = model.rest_action(deck, 100, 100, "demolition",
                                       next_fight=False)

    assert (action, target) == ("upgrade", "duck_and_cover")


def test_rest_thins_block_card_when_quota_survives_the_cut():
    """The same rule the other way round: with 2 block cards in 6, the post-cut
    density is 1/5 = 0.2, which clears DRAFT_BLOCK_DENSITY_MIN, so the rest
    does remove a basic blocker."""
    deck = ["duck_and_cover"] * 2 + ["kaeya_frostgnaw"] * 4
    n_block = 2
    assert (n_block - 1) / (len(deck) - 1) >= C.DRAFT_BLOCK_DENSITY_MIN

    action, target = model.rest_action(deck, 100, 100, "demolition",
                                       next_fight=False)

    assert (action, target) == ("remove", "duck_and_cover")
