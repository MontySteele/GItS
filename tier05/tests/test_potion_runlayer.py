"""Run-layer potion proofs (potion pass).

These seed a run via ``model.run_one(..., grant_potions=True)`` and assert the
RUN-SCOPED half of the potion layer that lives in tier05/model.py +
tier05/potions.py -- drops after won fights, the held-bag slot cap + overflow
discard, shop stock, the Potion Belt slot bump, and the consumed-potion
sync-back. The COMBAT half (engine/potions.py, the drink policy) is exercised
by tier0/tests; here combat is a deterministic stub so a potion's run-layer
bookkeeping is isolated from combat noise -- the same ``_win``/pop-stub trick
test_shop_economy and test_relics_runlayer use.

The load-bearing lock is last: ``grant_potions=False`` (the default) must leave
a run byte-for-byte the pre-potion model -- two such runs reproduce each other
decision-for-decision under REAL combat, with both potion fields empty. The
anchor-lock + battery-boundary assertions are re-run here so THIS file fails
loudly the moment a potion leaks into the frozen 3.0 battery.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import CombatState
from tier0.tests import test_anchor_lock
from tier05 import draft, model, potions as potion_pool
from tier05 import relics as relic_pool

CHAR = "klee"
ARCH = "demolition"
PILOT = "demolition"

# Drop nodes: every won N/E fight offers a drop; the boss (B) does not.
# Template "NNNRETN$ERB" -> N,N,N,E,N,E = 6 drop opportunities per won run.
_DROP_NODES = 6


# --- combat stubs -----------------------------------------------------------

def _win_stub():
    """Every fight is an instant win, player untouched, potions NEVER drunk
    (real combat is bypassed, so engine/potions.try_use_potions never runs).
    Isolates the RUN-layer drop/shop/slot bookkeeping from the drink policy."""
    def stub(player, enemies, pilot, seed):
        for e in enemies:
            e.hp = 0
        return CombatState(player=player, enemies=enemies,
                           rng=random.Random(seed))
    return stub


def _pop_one_stub(popped):
    """Instant win, but if the fight's player holds any potion, DRINK the first
    one (pop it off player.potions) and record it. This is exactly the mutation
    real combat performs on a drink, so the model's consumed-sync (_consumed +
    bag reassignment) must reproduce `popped` in res.potions_used."""
    def stub(player, enemies, pilot, seed):
        if player.potions:
            popped.append(player.potions.pop(0))
        for e in enemies:
            e.hp = 0
        return CombatState(player=player, enemies=enemies,
                           rng=random.Random(seed))
    return stub


def _skip(rng, deck, offers, archetype):
    return None


# ===========================================================================
# Drops
# ===========================================================================

def test_drops_land_after_won_fights_near_drop_chance(monkeypatch):
    # Huge slots so nothing is ever discarded, and the win stub never drinks,
    # so every successful drop survives in potions_end. Drops = held minus the
    # potions the shop sold (both accrue with no consumption). Over many seeds
    # the drop rate must sit near POTION_DROP_CHANCE (loose statistical bound).
    monkeypatch.setattr(model, "run_fight", _win_stub())
    monkeypatch.setattr(model, "_potion_slots", lambda held: 99)

    drops = 0
    for seed in range(200):
        r = model.run_one(CHAR, ARCH, PILOT, _skip, seed, grant_potions=True)
        assert r.won
        shop_bought = sum(1 for p in r.shop if p.get("buy") == "potion")
        drops += len(r.potions_end) - shop_bought
    rate = drops / (200 * _DROP_NODES)
    assert 0.30 < rate < 0.50                      # ~POTION_DROP_CHANCE (0.40)
    assert C.POTION_DROP_CHANCE == pytest.approx(0.40)


def test_held_never_exceeds_slot_count(monkeypatch):
    # Default 3 slots, real drop chance: the bag must never carry more than the
    # slot cap however the drops fall.
    monkeypatch.setattr(model, "run_fight", _win_stub())
    for seed in range(100):
        r = model.run_one(CHAR, ARCH, PILOT, _skip, seed, grant_potions=True)
        assert len(r.potions_end) <= C.POTION_SLOTS


def test_saturates_at_slot_cap_and_discards_overflow(monkeypatch):
    # Force a drop after EVERY won N/E fight (5 land before the shop): with 3
    # slots the bag fills to exactly 3 and the surplus is discarded, never
    # stored -- the run-layer face of the overflow rule.
    monkeypatch.setattr(model, "run_fight", _win_stub())
    monkeypatch.setattr(C, "POTION_DROP_CHANCE", 1.0)
    r = model.run_one(CHAR, ARCH, PILOT, _skip, 1, grant_potions=True)
    assert len(r.potions_end) == C.POTION_SLOTS     # saturated, not over-filled


def test_potion_bag_overflow_is_discarded_not_stored():
    # Unit-level proof of the discard rule the run relies on.
    bag = potion_pool.PotionBag(potions=[], slots=2)
    assert bag.add("block_potion") is True
    assert bag.add("fire_potion") is True
    assert bag.full()
    assert bag.add("swift_potion") is False         # overflow rejected
    assert bag.potions == ["block_potion", "fire_potion"]   # NOT stored
    assert bag.discarded == ["swift_potion"]        # discarded, logged
    assert len(bag.potions) == 2                     # never past the slot cap


# ===========================================================================
# Shop stock + sale
# ===========================================================================

def test_shop_stocks_and_sells_a_potion(monkeypatch):
    # Huge slots (a slot is always free) + the fixed win income (gold 204 at the
    # shop) means the shop's 1-2 rolled potions are both affordable and fit:
    # they sell. Each sale costs POTION_PRICE and the bought potion enters the
    # bag (never drunk under the win stub, so it survives to potions_end).
    monkeypatch.setattr(model, "run_fight", _win_stub())
    monkeypatch.setattr(model, "_potion_slots", lambda held: 99)
    r = model.run_one(CHAR, ARCH, PILOT, _skip, 1, grant_potions=True)

    buys = [p for p in r.shop if p.get("buy") == "potion"]
    assert 1 <= len(buys) <= 2                       # shelf is randint(1, 2)
    for p in buys:
        assert p["price"] == C.POTION_PRICE
        assert p["id"] in potion_pool.pool()         # a real pool potion
        assert p["id"] in r.potions_end              # actually entered the bag
    # Income is the fixed 269 (see test_shop_economy); the only spend is potions.
    assert r.gold == 269 - C.POTION_PRICE * len(buys)


def test_shop_skips_purchase_when_no_slot(monkeypatch):
    # Drop after every fight fills the 3 slots before the shop, so despite ample
    # gold the shop can sell nothing -- the slot gate.
    monkeypatch.setattr(model, "run_fight", _win_stub())
    monkeypatch.setattr(C, "POTION_DROP_CHANCE", 1.0)
    r = model.run_one(CHAR, ARCH, PILOT, _skip, 1, grant_potions=True)
    assert len(r.potions_end) == C.POTION_SLOTS      # bag was full at the shop
    assert [p for p in r.shop if p.get("buy") == "potion"] == []


def test_shop_skips_purchase_when_gold_short(monkeypatch):
    # Price above any reachable gold: the gold gate blocks every sale even with
    # slots free.
    monkeypatch.setattr(model, "run_fight", _win_stub())
    monkeypatch.setattr(C, "POTION_PRICE", 10 ** 9)
    for seed in range(10):
        r = model.run_one(CHAR, ARCH, PILOT, _skip, seed, grant_potions=True)
        assert [p for p in r.shop if p.get("buy") == "potion"] == []


# ===========================================================================
# Potion Belt: +2 slots
# ===========================================================================

def test_potion_belt_bonus_slots():
    assert model._potion_slots(None) == C.POTION_SLOTS
    assert model._potion_slots(relic_pool.HeldRelics.empty(CHAR)) == \
        C.POTION_SLOTS
    belt = relic_pool.HeldRelics.hold(["potion_belt"], CHAR)
    assert model._potion_slots(belt) == C.POTION_SLOTS + C.POTION_BELT_BONUS_SLOTS


def test_potion_belt_raises_run_slot_cap(monkeypatch):
    # Drop after every fight; without the belt the run holds at most 3, with it
    # the cap rises by exactly POTION_BELT_BONUS_SLOTS (2) to 5.
    monkeypatch.setattr(model, "run_fight", _win_stub())
    monkeypatch.setattr(C, "POTION_DROP_CHANCE", 1.0)
    plain = model.run_one(CHAR, ARCH, PILOT, _skip, 1, grant_potions=True)
    belt = model.run_one(CHAR, ARCH, PILOT, _skip, 1, grant_potions=True,
                         relics=["potion_belt"])
    assert len(plain.potions_end) == C.POTION_SLOTS
    assert len(belt.potions_end) == C.POTION_SLOTS + C.POTION_BELT_BONUS_SLOTS
    assert len(belt.potions_end) - len(plain.potions_end) == \
        C.POTION_BELT_BONUS_SLOTS


# ===========================================================================
# Consumed potions sync back; res records used/held
# ===========================================================================

def test_consumed_potions_sync_back_into_used(monkeypatch):
    # The pop-stub drinks the first held potion each fight (the exact mutation
    # real combat makes). The model must sync the survivors back into the bag
    # and record each drunk potion in res.potions_used -- so the recorded
    # used-list reproduces precisely what the stub popped, in order.
    popped = []
    monkeypatch.setattr(model, "run_fight", _pop_one_stub(popped))
    monkeypatch.setattr(C, "POTION_DROP_CHANCE", 1.0)   # keep the bag stocked
    r = model.run_one(CHAR, ARCH, PILOT, _skip, 1, grant_potions=True)

    assert popped                                    # the stub really drank some
    assert r.potions_used == popped                  # sync-back is exact
    # A drunk potion is gone from the bag: held never carries more than the cap,
    # and every recorded id is a real pool potion.
    assert len(r.potions_end) <= C.POTION_SLOTS
    known = set(potion_pool.pool())
    assert set(r.potions_used) <= known
    assert set(r.potions_end) <= known


def test_result_potion_fields_empty_without_grant(monkeypatch):
    monkeypatch.setattr(model, "run_fight", _win_stub())
    r = model.run_one(CHAR, ARCH, PILOT, _skip, 1)     # grant_potions default
    assert r.potions_used == []
    assert r.potions_end == []


# ===========================================================================
# CRITICAL INVARIANT: grant_potions=False is byte-for-byte the pre-potion model
# ===========================================================================

def test_grant_potions_false_is_byte_for_byte_unchanged():
    # REAL combat (no stub): the potion path must be dead when nothing is
    # granted, so a no-potion run reproduces the default run decision-for-
    # decision, and BOTH potion fields stay empty.
    for seed in (1, 2, 3, 7, 11):
        default = model.run_one(CHAR, ARCH, PILOT, draft.assigned_policy, seed)
        variants = [
            model.run_one(CHAR, ARCH, PILOT, draft.assigned_policy, seed,
                          grant_potions=False),
            model.run_one(CHAR, ARCH, PILOT, draft.assigned_policy, seed,
                          grant_potions=False),
        ]
        for other in variants:
            assert other.deck_ids == default.deck_ids
            assert other.hp_by_node == default.hp_by_node
            assert other.gold == default.gold
            assert other.death_node == default.death_node
            assert other.shop == default.shop
            assert other.rests == default.rests
            assert other.removal_uses == default.removal_uses
            assert [d["picked"] for d in other.decisions] == \
                   [d["picked"] for d in default.decisions]
            assert other.potions_used == []
            assert other.potions_end == []


# ===========================================================================
# LAYER-BOUNDARY LOCK: potions never touch the frozen 3.0 battery
# ===========================================================================

def test_battery_player_has_no_potions():
    """A player built by the battery path carries NO potions, so the whole
    combat-side potion engine is a dead branch on the anchor/battery."""
    for character, deck in (("ref_ironclad", "starter"),
                            ("ref_ironclad", "archetype_package"),
                            ("klee", "starter")):
        p = loader.build_player(character, deck)
        assert p.potions == [], (character, deck)


def test_anchor_lock_still_exact():
    """Re-run the anchor-lock assertions: if potions ever perturb the frozen
    battery, one of these moves and THIS file fails loudly."""
    test_anchor_lock.test_baseline_is_still_ref_ironclad_starter()
    test_anchor_lock.test_ref_ironclad_spec_is_byte_identical()
    test_anchor_lock.test_ref_ironclad_battery_numbers_locked()
