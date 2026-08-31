"""EB-250: a pool with no commons must still roll its offers.

THE DEFECT. `_RARITY_FALLBACK` walked DOWNWARD only -- rare -> uncommon ->
common -- so `while rarity not in pool` had nowhere to go once it reached
`common`, and a pool that genuinely lacks a common tier raised `KeyError:
'common'` out of the middle of a reward screen. The ladder exists because the
reference pools have no rares at all and a substituted screen beats an empty
one; nobody had asked what happens at the other end.

THE BASE GAME'S ANSWER, which is the direction this takes. There is no
renormalisation for a missing tier anywhere in the assembly:
`CardFactory.RollForRarity` rolls normally and then
`GetNextHighestRarityWithWrapping` walks Basic -> Common -> Uncommon -> Rare ->
Common until it lands on a rarity the filtered pool contains. The machinery
exists because the game's own colorless pool has NO commons: 0 of 65, so a
Common roll against it silently becomes Uncommon -- not re-rolled, not
renormalised (`research/colorless-anchor-2026-08-30.md` §6.3).

WHY BOTH DIRECTIONS, AND WHY DOWN STILL GOES FIRST. Adopting the wrap alone
would have re-pointed the reference pools' rare rolls from uncommon to common
and moved every archived number taken on them. So the walk keeps its existing
downward step as the FIRST thing it tries -- which is what those pools have
always taken -- and falls forward only where the downward ladder runs off its
end, which is exactly and only the case that used to raise.
"""

import random

import pytest

from tier05 import rewards
from tier0.content import loader


def _pool(*rarities: str) -> dict[str, list]:
    """A stand-in pool holding one real card per named tier. The cards are
    the loader's own, so `loader.get_card` on the pick resolves."""
    by_rarity: dict[str, list] = {}
    for card in loader._card_index().values():
        if card.rarity in rarities and card.rarity not in by_rarity:
            by_rarity[card.rarity] = [card]
    assert set(by_rarity) == set(rarities), f"no card for {rarities}"
    return by_rarity


@pytest.fixture
def commonless(monkeypatch):
    """The colorless shape: uncommon and rare, no common tier at all."""
    pool = _pool("uncommon", "rare")
    monkeypatch.setattr(rewards, "character_pool", lambda cid: pool)
    return pool


def test_a_commonless_pool_rolls_its_offers(commonless):
    """The row's acceptance. Every seed, because the rolled rarity is what
    decides whether the old ladder walked off its end, and `common` is 65%
    of the odds table -- most seeds hit it."""
    for seed in range(40):
        offers = rewards.roll_card_offers(random.Random(seed), "anything", 3)
        assert len(offers) == 3
        assert all(c.rarity in ("uncommon", "rare") for c in offers)


def test_a_common_roll_against_a_commonless_pool_becomes_uncommon(commonless):
    """The base game's own substitution, named rather than left to the
    ladder's shape: fall FORWARD, one step, not re-rolled."""
    offers = rewards.roll_card_offers(random.Random(0), "anything", 1,
                                      card_rarity="common")
    assert [c.rarity for c in offers] == ["uncommon"]


def test_a_commonless_pool_rolls_distinct_screens_too(commonless):
    """`distinct=True` is the event screens' setting and it walks the ladder
    a second time, on its own question -- a tier whose cards are all already
    on the screen. It walked off the same end."""
    offers = rewards.roll_card_offers(random.Random(3), "anything", 4,
                                      distinct=True)
    assert len({c.id for c in offers}) == len(offers)


def test_the_reference_pools_downward_walk_is_untouched(monkeypatch):
    """THE OTHER DIRECTION, and the reason down is tried first. The
    reference pools have no rares; a rare roll against one has always been
    served an uncommon, and every archived number on them was taken that
    way. Falling forward with wrapping would hand it a common instead."""
    pool = _pool("common", "uncommon")
    monkeypatch.setattr(rewards, "character_pool", lambda cid: pool)
    offers = rewards.roll_card_offers(random.Random(0), "anything", 1,
                                      card_rarity="rare")
    assert [c.rarity for c in offers] == ["uncommon"]


def test_a_pool_that_has_the_rolled_tier_never_walks(monkeypatch):
    """The common case, pinned so a ladder change cannot quietly reprice a
    complete pool: with all three tiers present, the roll stands."""
    pool = _pool("common", "uncommon", "rare")
    monkeypatch.setattr(rewards, "character_pool", lambda cid: pool)
    for want in ("common", "uncommon", "rare"):
        offers = rewards.roll_card_offers(random.Random(1), "anything", 2,
                                          card_rarity=want)
        assert [c.rarity for c in offers] == [want, want]


def test_a_single_tier_pool_resolves_from_either_end(monkeypatch):
    """The degenerate case both walks have to survive: one tier, and every
    roll has to reach it however it rolled. `distinct=True` as well, whose
    own ladder has to terminate on a pool with nowhere else to step -- one
    card is a screen smaller than itself, which is the existing `break`."""
    for only in ("common", "uncommon", "rare"):
        pool = _pool(only)
        monkeypatch.setattr(rewards, "character_pool", lambda cid: pool)
        for want in ("common", "uncommon", "rare"):
            offers = rewards.roll_card_offers(random.Random(2), "anything", 1,
                                              card_rarity=want)
            assert [c.rarity for c in offers] == [only]
            offers = rewards.roll_card_offers(random.Random(2), "anything", 2,
                                              card_rarity=want, distinct=True)
            assert [c.rarity for c in offers] == [only]
