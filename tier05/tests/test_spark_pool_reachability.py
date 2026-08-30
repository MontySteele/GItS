"""THE DRAFTER CAN BE OFFERED A PRICED SPARK ROW (R220 pick 6(d)).

`KLEESPARK-R1` sec.11.6 item 5 records the gap as a limitation of the round:
*"`loader._pool_substitutions` returns `{}` for Klee, so the tier 0.5 drafter
structurally cannot be offered a prototype Spark row; P5 and P6 read a deck
assembled by id from PICK 4's own map."* The Kokomi arm had a pool seam and
the Klee arm did not, which was an omission rather than a decision. The seam
is now shared: `C.SPARK_ALT_POOL_SUBS`, read at the same
`loader._pool_substitutions`, gated on the same `C.SPARK_ALT_COST_ENABLED`.

WHAT THIS FILE PINS, and the first two matter most:

  * FLAG OFF, NOTHING EXISTS. No substitution, no second index, no prototype
    id anywhere in `rewards.character_pool` -- the R213 quarantine, unmoved.
  * FLAG ON, THE SIX ROWS ARE REACHABLE, and they are reachable through the
    ONE function every offer surface reads (`rewards.character_pool`), so
    fight rewards, the shop, event card screens and the drafter all see them
    or none of them do.
  * RARITY IS PRESERVED, so the offer ODDS do not move: three commons, two
    uncommons, one rare, in and out. A substitution that moved a tier would
    be a balance change wearing a quarantine's clothes, and
    `character_pool` refuses one by name.
  * KOKOMI'S ARM IS UNTOUCHED by the shared seam.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B).
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier05 import rewards


def _clear():
    loader._card_prototype.cache_clear()
    loader._substituted_card_index.cache_clear()
    rewards.character_pool.cache_clear()


@pytest.fixture
def spark_pool(monkeypatch):
    """The flag ON with every memo a flip invalidates cleared both ways.

    `character_pool` is `lru_cache`d and reads the substitution map, so a
    test that flips the flag without clearing it reads the other arm.
    """
    _clear()
    monkeypatch.setattr(C, "SPARK_ALT_COST_ENABLED", True)
    yield
    _clear()


def proto_ids(pool):
    return sorted(c.id for cards in pool.values() for c in cards
                  if c.id.startswith(loader.PROTOTYPE_ID_PREFIX))


# --- flag off: the quarantine is exactly where it was ----------------------

def test_flag_off_no_substitution_and_no_prototype_in_the_pool():
    assert C.SPARK_ALT_COST_ENABLED is False
    _clear()
    assert loader.pool_substitutions("klee") == {}
    assert proto_ids(rewards.character_pool("klee")) == []
    assert loader._substituted_card_index() == {}


def test_flag_off_the_shipped_rows_are_still_offerable():
    _clear()
    pool = rewards.character_pool("klee")
    ids = {c.id for cards in pool.values() for c in cards}
    for shipped in C.SPARK_ALT_POOL_SUBS:
        assert shipped in ids


# --- flag on: the six rows are reachable ------------------------------------

def test_flag_on_the_six_prototype_rows_are_offerable(spark_pool):
    pool = rewards.character_pool("klee")
    assert proto_ids(pool) == sorted(C.SPARK_ALT_POOL_SUBS.values())


def test_flag_on_the_shipped_rows_they_replace_are_gone(spark_pool):
    pool = rewards.character_pool("klee")
    ids = {c.id for cards in pool.values() for c in cards}
    for shipped in C.SPARK_ALT_POOL_SUBS:
        assert shipped not in ids, "a converted row must not also be offered"


def test_the_swap_moves_no_card_between_rarities(monkeypatch):
    """Same tier, same count -- so the offer odds are untouched. The
    ValueError `character_pool` raises on a tier move is the loud half; this
    is the quiet half. Both readings are taken here, in one test, because the
    claim is a COMPARISON."""
    _clear()
    off = {r: len(cs) for r, cs in rewards.character_pool("klee").items()}
    monkeypatch.setattr(C, "SPARK_ALT_COST_ENABLED", True)
    _clear()
    on = {r: len(cs) for r, cs in rewards.character_pool("klee").items()}
    _clear()
    assert off == on


def test_a_reward_roll_can_actually_produce_one(spark_pool):
    """END TO END through the function every offer surface reads. A pool
    membership nobody can roll is not reachability."""
    seen = set()
    for seed in range(200):
        for card in rewards.roll_card_offers(random.Random(seed), "klee", 3):
            if card.id.startswith(loader.PROTOTYPE_ID_PREFIX):
                seen.add(card.id)
    assert seen, "200 reward screens offered no prototype row"


def test_an_offered_prototype_resolves_by_id(spark_pool):
    """The run layer stores decks as id strings and re-derives them on every
    screen, so an offer whose id does not resolve is a run that dies on the
    next screen. `_substituted_card_index` is what makes it resolve."""
    for proto in C.SPARK_ALT_POOL_SUBS.values():
        assert loader.get_card(proto).id == proto


def test_kokomis_arm_is_untouched(spark_pool):
    """One seam, two characters, no interference."""
    assert loader.pool_substitutions("kokomi") == (
        {C.KURAGE_MEMORY_POOL_DROP: C.KURAGE_MEMORY_POOL_ADD}
        if C.KURAGE_MEMORY else {})
    assert loader.pool_substitutions("furina") == {}
