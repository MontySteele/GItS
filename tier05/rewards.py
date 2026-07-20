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
        # kit_card (v1.9): Bursts are kit, not loot -- never offered. This
        # is what makes the rare tier 14 draftable instead of 15.
        if c.is_companion or c.kit_card or c.rarity not in C.RARITY_ODDS:
            continue
        pool.setdefault(c.rarity, []).append(c)
    return {r: sorted(cs, key=lambda c: c.id) for r, cs in pool.items()}


@lru_cache(maxsize=1)
def companion_pool() -> dict[str, list[Card]]:
    """rarity -> companion cards. 5-star cards ARE the rares (§3)."""
    pool: dict[str, list[Card]] = {}
    for c in loader._card_index().values():
        # guest_star (Furina kickoff §9): generated cameos, personal-pool
        # scoped. Never offered as rewards -- the only door is a generator.
        if c.is_companion and not c.guest_star:
            pool.setdefault(c.rarity, []).append(c)
    return {r: sorted(cs, key=lambda c: c.id) for r, cs in pool.items()}


@lru_cache(maxsize=8)
def five_star_roster(nation: str) -> list[Card]:
    """Every designed 5-star companion for a nation, banner-eligible.

    Standard-banner 5-stars are NOT excluded: per principles v1.8 they
    participate in the roll like anyone else, and the `standard` flag is
    only the escape hatch if banner variance turns out to brick runs.
    """
    return sorted(
        (c for c in loader._card_index().values()
         if c.is_companion and c.star == 5 and c.nation == nation
         and c.personal_pool is None and not c.guest_star),
        key=lambda c: c.id)


def roll_banner(rng: random.Random,
                nations: tuple[str, ...] = ("mondstadt",)) -> frozenset[str]:
    """The run's Featured Banner: BANNER_FEATURED_SLOTS limited 5-stars per
    nation, drawn once per run and fixed for its duration.

    Returns the set of featured 5-star card ids. Nations with no more
    designed 5-stars than slots feature all of them, which is why this is a
    no-op at the v0.1 roster and why the roll is still worth having: the
    governor exists before the roster needs it.

    In co-op each player rolls their own banner -- divergent lineups are the
    point -- so this deliberately takes an rng rather than reading a global.
    """
    featured: set[str] = set()
    for nation in nations:
        roster = five_star_roster(nation)
        if len(roster) <= C.BANNER_FEATURED_SLOTS:
            featured.update(c.id for c in roster)
        else:
            featured.update(c.id for c in
                            rng.sample(roster, C.BANNER_FEATURED_SLOTS))
    return frozenset(featured)


def _banner_filtered(cards: list[Card],
                     banner: frozenset[str] | None) -> list[Card]:
    """Drop off-banner 5-stars from an offer pool. 4-stars are never gated."""
    if banner is None:
        return cards
    return [c for c in cards if c.star != 5 or c.id in banner]


def _roll_rarity(rng: random.Random) -> str:
    roll = rng.random()
    acc = 0.0
    for rarity, odds in C.RARITY_ODDS.items():
        acc += odds
        if roll < acc:
            return rarity
    return "common"


def _nation_weighted_choice(rng: random.Random, cards: list[Card],
                            home_nation: str | None = None) -> Card:
    # §4.1, real as of Furina sprint 1: SAME_NATION_REWARD_SHARE of the
    # slot's weight concentrates on the run character's nation; the rest
    # spreads across ALL cards (relative nation weights, all 1.0 today).
    # With a single-nation pool this reduces exactly to the old uniform
    # pick -- same rng consumption, same picks, archived numbers intact.
    w_all = [C.NATION_WEIGHTS.get(c.nation or "", 1.0) for c in cards]
    n_home = sum(1 for c in cards if home_nation and c.nation == home_nation)
    if not n_home:
        weights = w_all
    else:
        total = sum(w_all)
        share = C.SAME_NATION_REWARD_SHARE
        weights = [(1 - share) * w / total
                   + (share / n_home if c.nation == home_nation else 0.0)
                   for c, w in zip(cards, w_all)]
    return rng.choices(cards, weights=weights, k=1)[0]


def roll_rewards(rng: random.Random, character_id: str,
                 companion_offers: int = 1,
                 banner: frozenset[str] | None = None) -> list[Card]:
    """One post-fight reward screen: card offers + the companion slot.
    companion_offers > 1 is the pity/choose-3 slot (triage ruling 4
    pulled the mechanism forward from M7; the run model decides when).

    banner is the run's Featured Banner (v1.8); None means unrestricted,
    which is the pre-v1.8 behaviour and what the Tier 0 fight-level tests
    still want. Off-banner 5-stars are removed before the rarity roll, so a
    banner that empties the rare tier falls through to uncommon exactly as a
    naturally rare-less pool already does.
    """
    pool = character_pool(character_id)
    offers = []
    for _ in range(C.REWARD_CARD_OFFERS):
        rarity = _roll_rarity(rng)
        while rarity not in pool:            # ref pool may lack a rarity
            rarity = {"rare": "uncommon", "uncommon": "common"}[rarity]
        offers.append(loader.get_card(rng.choice(pool[rarity]).id))
    if character_id != "ref_ironclad":       # no companions for the anchor
        # personal_pool cards are only offered to their own character --
        # a no-op while Klee is the only character, load-bearing the moment
        # a second one exists (Prune must not show up in Furina's rewards).
        comps = {r: cs for r, cs in
                 ((r, [c for c in _banner_filtered(cs, banner)
                       if c.personal_pool in (None, character_id)])
                  for r, cs in companion_pool().items()) if cs}
        home = loader.character_nation(character_id)
        for _ in range(companion_offers):
            rarity = _roll_rarity(rng)
            while rarity not in comps:
                rarity = {"rare": "uncommon", "uncommon": "common"}[rarity]
            offers.append(loader.get_card(
                _nation_weighted_choice(rng, comps[rarity], home).id))
    return offers
