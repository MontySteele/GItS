"""`EB-577`: the Klee arm's first card rewards each carry a Spark-priced row.

THE READING SIX ROUNDS MADE. Sparks are inert until a sink is drafted -- r17
through r21 all said it, and the r21 lane-2 seat ended fights holding 3, 4 and
5 with Dig In the deck's one reader. The resource the kit mints on every
explosion did nothing at all for two acts, because the reward screens that
could have taught it never offered one.

AN OFFER RULE AND NOT A SHEET CHANGE (Klee r21 packet sec.5, a D default). No
card's rarity, price or face moves; what moves is which cards a reward screen
may show on floors 1 to `C.KLEE_OVERHAUL_SPARK_SEED_FLOORS` while the deck
holds no reader.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE (R215 B). These are shape
assertions about an offer rule, not numbers about a game.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat
from tier05 import rewards


@pytest.fixture
def arm(monkeypatch):
    monkeypatch.setattr(C, "KLEE_OVERHAUL", True)
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()
    yield
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()


def _offers(seed: int, floor: int | None, character: str = "klee"):
    return rewards.roll_card_offers(random.Random(seed), character,
                                    C.REWARD_CARD_OFFERS, floor=floor)


def _sparks(offers) -> int:
    return sum(1 for c in offers if combat.spark_cost(c))


SEEDS = range(24)


def test_every_seeded_floor_offers_a_spark_priced_row(arm):
    """The acceptance, over enough seeds that a lucky roll cannot pass it.

    Seen to FAIL: the roll is rarity-first and Spark rows are a minority of
    every tier, so the first two rewards of a run were routinely three cards
    that could not read the resource the kit was minting.
    """
    for floor in range(1, C.KLEE_OVERHAUL_SPARK_SEED_FLOORS + 1):
        for seed in SEEDS:
            assert _sparks(_offers(seed, floor)) >= 1, (floor, seed)


def test_the_rule_expires_and_does_not_become_a_tax_on_the_pool(arm):
    """Floor 4 on is the roll it always was, so the guarantee is a seam at the
    start of a run rather than a permanent thumb on the pool."""
    unseeded = [seed for seed in SEEDS
                if _sparks(_offers(seed, C.KLEE_OVERHAUL_SPARK_SEED_FLOORS + 1))
                == 0]
    assert unseeded, "no floor-4 screen rolled without a Spark row"


def test_a_screen_that_already_rolled_one_is_untouched(arm):
    """The swap is the smallest intervention it could be: where the roll did
    the work itself, the offers are byte-identical to the unseeded roll."""
    for seed in SEEDS:
        bare = _offers(seed, None)
        if _sparks(bare) == 0:
            continue
        assert [c.id for c in _offers(seed, 1)] == [c.id for c in bare]


def test_the_seed_is_quarantined(monkeypatch):
    """`C.KLEE_OVERHAUL` off, any character but Klee, or a caller with no floor
    to give: the identity, in every direction."""
    monkeypatch.setattr(C, "KLEE_OVERHAUL", False)
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()
    for seed in SEEDS:
        assert ([c.id for c in _offers(seed, 1)]
                == [c.id for c in _offers(seed, None)])
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()


def test_no_floor_is_the_identity(arm):
    """The event layer's card screens pass no floor, and a rule about the
    first two REWARDS of a run must not reach them."""
    for seed in SEEDS:
        bare = _offers(seed, None)
        assert [c.id for c in bare] == [
            c.id for c in rewards.roll_card_offers(
                random.Random(seed), "klee", C.REWARD_CARD_OFFERS)]


def test_the_pick_is_derived_and_spends_no_rng(arm):
    """The roll this runs after has already been made, so a draw here would
    move the run's shared stream and a seed replayed with the arm off would
    diverge for a reason that has nothing to do with combat. Same seed, same
    floor, same card -- and the rng is left exactly where the roll left it."""
    for seed in SEEDS:
        rng_a, rng_b = random.Random(seed), random.Random(seed)
        a = rewards.roll_card_offers(rng_a, "klee", C.REWARD_CARD_OFFERS,
                                     floor=1)
        b = rewards.roll_card_offers(rng_b, "klee", C.REWARD_CARD_OFFERS,
                                     floor=1)
        assert [c.id for c in a] == [c.id for c in b]
        # The unseeded roll consumed the same rng: the seed drew nothing.
        rng_c = random.Random(seed)
        rewards.roll_card_offers(rng_c, "klee", C.REWARD_CARD_OFFERS,
                                 floor=None)
        assert rng_a.random() == rng_c.random()


def test_the_two_seeded_screens_of_a_run_can_differ(arm):
    """A derived pick is not a constant one: the floor indexes the eligible
    rows, so the run's two seeded rewards do not hand out the same card."""
    picked = {floor: {_offers(seed, floor)[0].id for seed in SEEDS}
              for floor in (1, 2, 3)}
    assert picked[1] != picked[2] or picked[2] != picked[3]


def test_the_swap_keeps_the_rolled_rarity_where_the_pool_has_one(arm):
    """The guarantee is about WHICH card and never about how good one is, so
    the swapped offer is drawn from the tier the roll had already landed on."""
    pool = rewards.character_pool("klee")
    tiers = {rarity for rarity, cards in pool.items()
             if any(combat.spark_cost(c) for c in cards)}
    assert tiers, "the arm has no Spark-priced row at any rarity"
    for seed in SEEDS:
        bare = _offers(seed, None)
        if _sparks(bare) or not any(c.rarity in tiers for c in bare):
            continue
        seeded = _offers(seed, 1)
        moved = [(b, s) for b, s in zip(bare, seeded) if b.id != s.id]
        assert len(moved) == 1
        assert moved[0][0].rarity == moved[0][1].rarity
