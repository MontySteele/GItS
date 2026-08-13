"""Event card screens roll rarity like every other reward screen (EB-112).

`card_reward` and `card_screens` are declared in the event grammar as "an
ordinary reward screen". They were not one: both built their offers by
flattening the whole character pool into a single list and drawing uniformly
WITH REPLACEMENT, so a Klee pool of 29/28/14 put Rare at 14/71 = 19.7% per
offer against the 60/35/5 in `C.RARITY_ODDS`, and an 8-wide screen could show
the same card twice. Three shipped options carry this in acts 1 and 2 for
every character (Brain Leech, The Trial, The Future of Potions).

`pick_cards` is deliberately NOT changed: its grammar line honestly says
"choose N of M random pool cards", so its uniform draw is a declaration, not
a defect. Its with-replacement collision is a separate open gallery note.
"""

from __future__ import annotations

import collections
import random

import pytest

from tier0 import constants as C
from tier05 import events, rewards

CHAR = "klee"
_TRIALS = 4000


def _state():
    return events.EventState(character=CHAR, archetype="demolition", hp=40,
                             max_hp=62, gold=0, deck_ids=[])


def _pick_nothing(rng, deck, offers, archetype):
    """A policy that declines, so the deck never grows and every screen is
    rolled against the same (empty) deck -- the offers are the subject."""
    return None


def _screen_rarities(opt, trials=_TRIALS):
    rng = random.Random(11)
    counts = collections.Counter()
    seen_offers = []

    def _spy(prng, deck, offers, archetype):
        seen_offers.append(list(offers))
        return None

    for _ in range(trials):
        events.resolve(rng, {"id": "t"}, opt, _state(), policy=_spy)
    for offers in seen_offers:
        counts.update(c.rarity for c in offers)
    return counts, seen_offers


def test_event_card_reward_honours_rarity_odds():
    counts, offers = _screen_rarities({"label": "x", "card_reward": 3})
    total = sum(counts.values())
    assert total == 3 * _TRIALS
    rare = counts["rare"] / total
    # Uniform-over-the-flat-pool put this at 14/71 = 0.197. The declared
    # odds are 0.05; 4000 x 3 offers keeps the sampling error well inside
    # one point.
    assert C.RARITY_ODDS["rare"] == pytest.approx(0.05)
    assert rare == pytest.approx(0.05, abs=0.01)
    assert counts["common"] / total == pytest.approx(0.60, abs=0.02)
    assert counts["uncommon"] / total == pytest.approx(0.35, abs=0.02)


def test_event_card_screens_honours_rarity_odds():
    counts, offers = _screen_rarities({"label": "x", "card_screens": 2})
    total = sum(counts.values())
    # `card_screens: N` is N INDEPENDENT screens of the standard width.
    assert total == 2 * C.REWARD_CARD_OFFERS * _TRIALS
    assert counts["rare"] / total == pytest.approx(0.05, abs=0.01)


def test_event_screen_offers_are_distinct():
    """A declared 3-wide choice is three cards. The old with-replacement
    draw narrowed it: an 8-wide screen held a duplicate 33.6% of the time."""
    _, offers = _screen_rarities({"label": "x", "card_reward": 8},
                                 trials=500)
    assert offers
    for screen in offers:
        ids = [c.id for c in screen]
        assert len(ids) == len(set(ids)) == 8


def test_pick_cards_keeps_its_declared_uniform_draw():
    """`pick_cards` declares "choose N of M random pool cards" and is left
    alone -- routing it through the reward constructor would silently
    redefine an option whose grammar line is honest."""
    pool = rewards.character_pool(CHAR)
    flat_rare = len(pool["rare"]) / sum(len(v) for v in pool.values())
    assert flat_rare > 0.15                       # the uniform pool's share
    src = events._random_pool_cards(random.Random(9), _state(), 6000)
    got = collections.Counter(c.rarity for c in src)
    assert got["rare"] / 6000 == pytest.approx(flat_rare, abs=0.02)


def test_roll_rewards_card_half_is_unmoved():
    """The shared helper is `roll_rewards`' own card loop, factored out with
    its historical (non-distinct) draw and rng consumption intact -- the
    post-fight screen and every archived number taken from it must not have
    moved."""
    a = rewards.roll_rewards(random.Random(4), CHAR, companion_offers=1)
    b = rewards.roll_rewards(random.Random(4), CHAR, companion_offers=1)
    assert [c.id for c in a] == [c.id for c in b]
    direct = rewards.roll_card_offers(random.Random(4), CHAR,
                                      C.REWARD_CARD_OFFERS)
    assert [c.id for c in a[:C.REWARD_CARD_OFFERS]] == [c.id for c in direct]
