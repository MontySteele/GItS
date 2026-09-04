"""THE FURINA REFRAME'S POOL SEAM (QUARANTINED, `furina_reframe.FURINA_REFRAME`).

Round 2 pick 1, taken at its default 2026-09-04. Four shipped rows gate on a
Fanfare bar the arm's performance-only meter does not reach -- 12, 12, 15 and
20, against a meter that ranged 0 to 15 across three rounds -- so under the arm
the shipped id leaves the offer surface and an arm-only copy at 6, 6, 8 and 10
takes its slot at the SAME rarity. Nothing on the shipped sheet moves.

The seam is `furina_reframe.POOL_SUBS`, read by
`loader._pool_substitutions` at the one door `tier05.rewards.character_pool`
already reads (fight rewards, the shop, every event card screen and the tier
0.5 drafter). Its C# twin is `FurinaReframeRoster.SwapOfferedRiders`, wired
into `FurinaCardPool.FilterThroughEpochs` beside Kokomi's Oath swap.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): these are shape assertions about an
offer surface, not numbers about a game.
"""

import pytest

from tier0.content import loader
from tier0.engine import furina_reframe as fr
from tier05 import rewards


@pytest.fixture
def reframe(monkeypatch):
    """The master flag on, with both id-resolving caches cleared on the way in
    and out -- `test_kokomi_overhaul.overhaul`'s fixture, for its reasons."""
    loader.reset_caches()
    rewards.character_pool.cache_clear()
    monkeypatch.setattr(fr, "FURINA_REFRAME", True)
    yield
    loader.reset_caches()
    rewards.character_pool.cache_clear()


def pool_ids(character="furina"):
    return {c.id for cards in rewards.character_pool(character).values()
            for c in cards}


def by_rarity(character="furina"):
    return {r: len(cs)
            for r, cs in rewards.character_pool(character).items()}


def test_the_map_is_the_sheets_own_replaces_key():
    """DERIVED IN NEITHER DIRECTION, COMPARED IN BOTH. The map is a literal in
    `furina_reframe` (the flag lives there rather than in `constants.py`, for
    the reason that module's header gives) and the rows carry `replaces:`; a
    fifth copy on the surface that nobody named here would otherwise be a row
    that is never offered, which is exactly the defect
    `lint_arm_pool_parity` was written for one arm over."""
    on_sheet = {c.replaces: c.id for c in loader.prototype_cards()
                if c.replaces is not None and not c.personal_pool
                and c.character == "furina"}
    assert on_sheet == fr.POOL_SUBS


def test_the_arm_off_offers_the_shipped_rows_and_no_prototype():
    """The acceptance condition on the flag, pinned rather than intended."""
    loader.reset_caches()
    rewards.character_pool.cache_clear()
    assert loader.pool_substitutions("furina") == {}
    ids = pool_ids()
    for shipped, proto in fr.POOL_SUBS.items():
        assert shipped in ids
        assert proto not in ids


def test_the_arm_on_offers_the_copy_and_not_the_shipped_row(reframe):
    assert loader.pool_substitutions("furina") == dict(fr.POOL_SUBS)
    ids = pool_ids()
    for shipped, proto in fr.POOL_SUBS.items():
        assert shipped not in ids
        assert proto in ids


def test_the_swap_moves_no_card_between_rarity_tiers(reframe):
    """A substitution is a face swap. Moving a card between tiers would move
    the odds it is offered at, which is a balance change smuggled in as a
    quarantine -- `rewards.character_pool` raises on one, and this is the read
    from the other side: the buckets are the same size with the arm on."""
    off = by_rarity()
    loader.reset_caches()
    rewards.character_pool.cache_clear()
    with_arm = by_rarity()
    assert off == with_arm
    for shipped, proto in fr.POOL_SUBS.items():
        assert (loader.peek_card(shipped).rarity
                == loader.peek_card(proto).rarity)


def test_the_copies_carry_the_arms_thresholds_and_the_shipped_rows_do_not(
        reframe):
    """The whole reason the swap exists. The shipped bars are 12, 12, 15 and
    20; the copies read 6, 6, 8 and 10, and the shipped rows are untouched."""
    bars = {"florid_cadenza": ("fanfare_at_least_12", "fanfare_at_least_6"),
            "dramatic_entrance": ("fanfare_at_least_12", "fanfare_at_least_6"),
            "universal_revelry": ("fanfare_at_least_15", "fanfare_at_least_8"),
            "flood_of_emotion": ("fanfare_at_least_20", "fanfare_at_least_10")}
    for shipped, (shipped_bar, proto_bar) in bars.items():
        assert _bar(loader.get_card(shipped)) == shipped_bar
        assert _bar(loader.peek_card(fr.POOL_SUBS[shipped])) == proto_bar


def _bar(card):
    return next(fx["if"] for fx in card.effects
                if fx.get("op") == "conditional")


def test_no_other_character_moves(reframe):
    """Every leg of this arm is character-scoped (`is_furina`), and the pool
    seam is no exception: in co-op the other seat may be Klee."""
    for other in ("klee", "kokomi"):
        assert loader.pool_substitutions(other) == {}
