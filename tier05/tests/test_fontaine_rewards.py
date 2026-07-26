"""§4.1 nation weighting, real as of Furina sprint 1 (kickoff §10).

The concentration must work from both directions: Mondstadt's wide bench
and Fontaine's deliberately narrow one (narrow-deep is pro-Spotlight by
STRUCTURE -- if same-nation reads high for Furina, that is geometry, not
generosity; do not "fix" it).
"""

import random

from tier05 import rewards


def _companion_offers(character_id, n=600, seed=3):
    rng = random.Random(seed)
    offers = []
    for _ in range(n):
        offers.extend(c for c in rewards.roll_rewards(rng, character_id)
                      if c.is_companion)
    return offers


def test_klee_offers_concentrate_on_mondstadt():
    offers = _companion_offers("klee")
    share = sum(c.nation == "mondstadt" for c in offers) / len(offers)
    assert share >= 0.6          # 0.5 concentrated + her slice of uniform
    assert any(c.nation == "fontaine" for c in offers)   # cross-nation
    # access is the uniform half's whole point (off-element fuel, §4.1)


def test_furina_offers_concentrate_on_fontaine():
    offers = _companion_offers("furina")
    share = sum(c.nation == "fontaine" for c in offers) / len(offers)
    assert share >= 0.55         # thin bench still gets its half
    assert any(c.nation == "mondstadt" for c in offers)
    # HISTORY, because the assertion below inverts a previous one. Fontaine
    # used to design no shared 5-stars, so every rare-tier offer fell through
    # to the nations that HAD them (Mondstadt, then Inazuma from 2026-07-24).
    # R64 (2026-07-25) gave Fontaine four, so the fall-through is no longer
    # the construction being pinned -- Furina's own nation now answers a Rare
    # roll, which is the roster gap the sprint existed to close.
    rares = [c for c in offers if c.star == 5]
    assert rares, "no 5-star surfaced at all across the sample"
    assert any(c.nation == "fontaine" for c in rares), (
        "Furina's home nation must now be able to answer a Rare roll")
