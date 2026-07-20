"""Reward generation (spec §3) — OUR design, the thing under test.

After each fight: REWARD_CARD_OFFERS character cards rarity-rolled, plus
the companion slot (standard mode in M5; choose3/pity land in M7). Skip
is always allowed — the draft policy decides.

5-star companions appear at rare odds only; 4-stars fill common/uncommon.
Nation weighting (§4.1) is implemented as a mechanism even though v0.1 is
single-nation — the weights table is the design artifact.
"""

from __future__ import annotations

import random
from functools import lru_cache

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import Card


@lru_cache(maxsize=8)
def character_pool(character_id: str) -> dict[str, list[Card]]:
    """rarity -> character cards eligible as fight rewards."""
    if character_id == "ref_ironclad":
        # Spec §5: build his pool from starter+package cards — he is still
        # the 3.0 anchor, so his rewards come only from his own kit.
        ids = set(loader.character_packages("ref_ironclad")
                  .get("archetype_package", []))
        cards = [loader.get_card(cid) for cid in sorted(ids)]
        pool: dict[str, list[Card]] = {}
        for c in cards:
            pool.setdefault(c.rarity if c.rarity in C.RARITY_ODDS
                            else "common", []).append(c)
        return pool
    index = loader._card_index()
    pool = {}
    for c in index.values():
        if c.is_companion or c.rarity not in C.RARITY_ODDS:
            continue
        pool.setdefault(c.rarity, []).append(c)
    return {r: sorted(cs, key=lambda c: c.id) for r, cs in pool.items()}


@lru_cache(maxsize=1)
def companion_pool() -> dict[str, list[Card]]:
    """rarity -> companion cards. 5-star cards ARE the rares (§3)."""
    pool: dict[str, list[Card]] = {}
    for c in loader._card_index().values():
        if c.is_companion:
            pool.setdefault(c.rarity, []).append(c)
    return {r: sorted(cs, key=lambda c: c.id) for r, cs in pool.items()}


def _roll_rarity(rng: random.Random) -> str:
    roll = rng.random()
    acc = 0.0
    for rarity, odds in C.RARITY_ODDS.items():
        acc += odds
        if roll < acc:
            return rarity
    return "common"


def _nation_weighted_choice(rng: random.Random, cards: list[Card]) -> Card:
    # §4.1 mechanism: weight by nation. v0.1 is all-Mondstadt, so this is
    # a uniform pick wearing its future shape.
    weights = [C.NATION_WEIGHTS.get("mondstadt", 1.0) for _ in cards]
    return rng.choices(cards, weights=weights, k=1)[0]


def roll_rewards(rng: random.Random, character_id: str,
                 slot_mode: str = "standard") -> list[Card]:
    """One post-fight reward screen: card offers + the companion slot."""
    pool = character_pool(character_id)
    offers = []
    for _ in range(C.REWARD_CARD_OFFERS):
        rarity = _roll_rarity(rng)
        while rarity not in pool:            # ref pool may lack a rarity
            rarity = {"rare": "uncommon", "uncommon": "common"}[rarity]
        offers.append(loader.get_card(rng.choice(pool[rarity]).id))
    if character_id != "ref_ironclad":       # no companions for the anchor
        if slot_mode != "standard":
            raise ValueError(f"slot mode {slot_mode!r} lands in M7")
        comps = companion_pool()
        rarity = _roll_rarity(rng)
        while rarity not in comps:
            rarity = {"rare": "uncommon", "uncommon": "common"}[rarity]
        offers.append(loader.get_card(
            _nation_weighted_choice(rng, comps[rarity]).id))
    return offers
