"""Reward generation (spec §3) — OUR design, the thing under test.

After each fight: REWARD_CARD_OFFERS character cards rarity-rolled, plus
the companion slot (one offer; the spec's pity(k) and choose3 modes were
deleted 2026-10-18). Skip
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
from tier0.engine import yae_shrine
from tier0.engine.state import Card

# The calibration references draft only from their own pool. For
# real_ironclad this is the PARITY rule, not a flavour call: companions are
# Klee/Furina content and would inject elements and reactions into a run
# whose whole purpose is to be scored in the same relic-less, potion-less,
# element-less world Klee was. The guard is a bare string, so it stays inert
# on a clone where game_ref/ (and therefore real_ironclad) does not exist.
NO_COMPANION_CHARACTERS = frozenset({"ref_ironclad", "real_ironclad",
                                     "real_silent"})


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
            # SKIP, never remap. This branch used to refile any off-table
            # rarity as `common`, which is a silent promotion: a basic, a
            # status or an Ancient landing in his package would have started
            # appearing on his reward screens wearing common's odds. The
            # general branch below drops off-table rarities outright, and
            # this one now agrees with it -- an anchor's pool must not be
            # the one place where the rarity vocabulary is lenient.
            if c.rarity not in C.RARITY_ODDS:
                continue
            pool.setdefault(c.rarity, []).append(c)
        return pool
    # EACH CURRENT KIT'S POOL IS ITS PROTOTYPE ROSTER (`loader.pool_replacement`).
    # The rows are read through `peek_card`, which resolves a `proto_` id
    # (`loader._card_prototype`); `_card_index` carries none of them. Off-table
    # rarities are DROPPED rather than refiled, the same rule the general loop
    # below applies.
    replacement = loader.pool_replacement(character_id)
    if replacement is not None:
        pool = {}
        for cid in replacement:
            c = loader.peek_card(cid)
            if c.rarity not in C.RARITY_ODDS:
                continue
            pool.setdefault(c.rarity, []).append(c)
        return {r: sorted(cs, key=lambda c: c.id) for r, cs in pool.items()}
    index = loader._card_index()
    pool = {}
    for c in index.values():
        # kit_card (v1.9): Bursts are kit, not loot -- never offered. This
        # is what makes the rare tier 14 draftable instead of 15.
        if c.is_companion or c.kit_card or c.rarity not in C.RARITY_ODDS:
            continue
        # Ownership is REQUIRED, not merely non-conflicting. The old test
        # was `if c.character and c.character != character_id` -- it dropped
        # cards belonging to someone ELSE but let cards belonging to NOBODY
        # through to everybody. The cards/ reference sheets predate the
        # drafting layer entirely (commit 8b5ac16, when every deck was
        # passed in explicitly and card ownership was not yet a concept), so
        # they carried character=None and leaked into every character's
        # rewards: 11 stand-ins, ~12% of Klee's offers and ~32% of
        # real_ironclad's, including Silent cards on the Ironclad.
        #
        # This one MATTERS to balance, it is not hygiene: shrug_it_off_like
        # is 8 block + draw for 1 energy, which beat 11 of Klee's own 12
        # block cards. Her measured survivability was propped up by borrowed
        # Ironclad block that will never ship in the mod. Ratified
        # 2026-07-21: "We NEED to make the sim results reflect the real card
        # pool. If that damages the baseline, so be it."
        if c.character != character_id:
            continue
        pool.setdefault(c.rarity, []).append(c)
    return {r: sorted(cs, key=lambda c: c.id) for r, cs in pool.items()}


@lru_cache(maxsize=1)
def _companion_roster() -> list[Card]:
    """Every companion an offer surface may see -- the ONE reader of the
    Mondstadt companion overhaul's seam (`C.COMPANION_OVERHAUL`).

    Both companion surfaces (the reward slot and the shop) go through this, so
    they cannot disagree about which companions exist in a run. The
    seam is `loader.companion_roster_replacement`, whose C# twin is
    `KleeMod.CompanionPool.All`; it returns None on every flag-off tree and
    this is then the shipped index filtered exactly as it always was.
    """
    replacement = loader.companion_roster_replacement()
    if replacement is not None:
        return replacement
    return [c for c in loader._card_index().values() if c.is_companion]


@lru_cache(maxsize=1)
def companion_pool() -> dict[str, list[Card]]:
    """rarity -> companion cards. 5-star cards ARE the rares (§3)."""
    pool: dict[str, list[Card]] = {}
    for c in _companion_roster():
        # guest_star (Furina kickoff §9): generated cameos, personal-pool
        # scoped. Never offered as rewards -- the only door is a generator.
        #
        # The rarity gate mirrors `character_pool` above rather than
        # answering a live defect: no companion carries an acquisition-only
        # rarity today. It is here so the two reward pools cannot disagree
        # about what "offerable" means -- the asymmetry is exactly how an
        # Ancient (or a status, or a curse) would find a door on the
        # companion slot that it does not have on the character slot.
        if (c.is_companion and not c.guest_star
                and c.rarity in C.RARITY_ODDS):
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


# The rarity ladder a screen walks down when the tier it rolled has nothing
# to offer -- a pool may genuinely lack a tier (the reference pools have no
# rares at all), and a substituted screen beats an empty one.
_RARITY_FALLBACK = {"rare": "uncommon", "uncommon": "common"}

# EB-250: and the ladder UP, for the end the downward one walks off. A pool
# with no common tier used to raise `KeyError: 'common'` out of the middle of
# a reward screen, because `while rarity not in pool` had nowhere left to
# step. That pool is not hypothetical -- the base game's own colorless pool
# has 0 commons of 65.
#
# THE BASE GAME'S DIRECTION, which is what this adopts. There is no
# renormalisation for a missing tier anywhere in its assembly:
# `CardFactory.RollForRarity` rolls normally and `GetNextAllowedRarity` walks
# `GetNextHighestRarityWithWrapping` (Basic -> Common -> Uncommon -> Rare ->
# Common) until it lands on a rarity the filtered pool actually contains, so
# a Common roll against a colorless-only pool silently becomes Uncommon --
# not re-rolled (`research/colorless-anchor-2026-08-30.md` §6.3).
#
# WHY DOWN IS STILL TRIED FIRST, and why this is not simply the wrapping
# walk. Taking the wrap whole would re-point the REFERENCE pools' rare rolls
# from uncommon to common -- those pools have no rares, that step is the one
# they have always taken, and every archived number on them was taken with
# it. So `_rarity_ladder` offers the downward tiers first, in the order they
# have always been tried, and the upward ones only after: identical for every
# pool that used to resolve, and defined for the one that used to raise.
_RARITY_FALLBACK_UP = {"common": "uncommon", "uncommon": "rare"}


# The forced post-boss companion's one fallback ([USER] 2026-10-18, legacy
# review pick 3): a Rare, or an Uncommon when no Rare companion can be offered.
_FORCED_COMPANION_FALLBACK = {"rare": "uncommon"}


def _rarity_ladder(rarity: str) -> list[str]:
    """The tiers a roll of `rarity` will accept, in the order it tries them:
    itself, then down while there is a step down, then up."""
    ladder = [rarity]
    step = rarity
    while step in _RARITY_FALLBACK:
        step = _RARITY_FALLBACK[step]
        ladder.append(step)
    step = rarity
    while step in _RARITY_FALLBACK_UP:
        step = _RARITY_FALLBACK_UP[step]
        ladder.append(step)
    return ladder


def _present_rarity(pool: dict[str, list[Card]], rarity: str) -> str:
    """The first tier of `rarity`'s ladder the pool actually holds.

    Raises rather than returning a tier that is not there: `roll_card_offers`
    has already refused an empty pool above, so nothing reaching here can
    legitimately have no tier at all, and a silent `None` would push the
    failure one frame further from its cause.
    """
    for step in _rarity_ladder(rarity):
        if step in pool:
            return step
    raise ValueError(
        f"no rarity tier in the pool for a {rarity!r} roll -- the pool holds "
        f"{sorted(pool)}, which the ladder cannot reach from {rarity!r}")


def roll_card_offers(rng: random.Random, character_id: str, n: int,
                     card_rarity: str | None = None,
                     distinct: bool = False) -> list[Card]:
    """`n` card offers rolled the way a reward screen rolls them: a rarity
    per offer through `C.RARITY_ODDS` FIRST, then a pick inside that tier.

    This is `roll_rewards`' card half, factored out so the event layer's
    card screens can share it (EB-112). Event screens flattened the whole
    character pool and drew uniformly, which put Rare at 14/71 = 19.7% per
    offer against the 5% the odds table declares.

    `distinct=True` is the event screens' setting: an offer never repeats a
    card already on the same screen, so a declared N-wide choice really is
    N cards. When the rolled tier holds nothing new the ladder steps down
    exactly as an absent tier does -- downward only, on its own question
    (EB-250). `distinct=False` reproduces
    `roll_rewards`' historical draw -- same rng consumption, same picks, so
    archived post-fight numbers are untouched.
    """
    pool = character_pool(character_id)
    if not pool:
        raise ValueError(
            f"no draftable cards for character {character_id!r} -- every "
            "reward card must be owned by the character being offered it. "
            "Check the id, or that its sheet sets `character`.")
    offers: list[Card] = []
    taken: set[str] = set()
    for _ in range(n):
        rarity = card_rarity or _roll_rarity(rng)
        rarity = _present_rarity(pool, rarity)   # pool may lack a rarity
        cands = pool[rarity]
        if distinct:
            # This second walk asks a DIFFERENT question -- a tier whose
            # cards are all already on the screen -- and it keeps its
            # downward-only step, because a screen that has exhausted the
            # commons wants the uncommons, not a wrap back to where it
            # started. `seen` is what makes that safe now that a step can
            # resolve forward: without it a commonless pool would step
            # `uncommon -> common`, resolve `common` back to `uncommon`, and
            # spin on a tier it had already rejected.
            seen = {rarity}
            while all(c.id in taken for c in cands):
                nxt = _RARITY_FALLBACK.get(rarity)
                if nxt is None:
                    break
                nxt = _present_rarity(pool, nxt)
                if nxt in seen:
                    break
                rarity = nxt
                seen.add(rarity)
                cands = pool[rarity]
            cands = [c for c in cands if c.id not in taken] or [
                c for cs in pool.values() for c in cs if c.id not in taken]
            if not cands:
                break                        # pool smaller than the screen
        pick = loader.get_card(rng.choice(cands).id)
        offers.append(pick)
        taken.add(pick.id)
    return offers


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
                 companion_rarity: str | None = None,
                 card_rarity: str | None = None) -> list[Card]:
    """One post-fight reward screen: card offers + the companion slot.
    companion_offers > 1 is the pity/choose-3 slot (triage ruling 4
    pulled the mechanism forward from M7; the run model decides when).

    Every companion in the pool is offerable in every run: there is no
    Featured Banner ([USER] 2026-10-18, "Agreed on (a)!" -- scrap the banner
    everywhere). ``companion_rarity="rare"`` is
    the post-boss rule for the Companion slot (Uncommon when no Rare companion
    can be offered); ``card_rarity="rare"`` forces
    the ordinary card offers, which is §10.1's boundary reward ("choice-of-3
    Rare cards"). The Ironclad-0.6% diagnosis (2026-07-23) found the shipped
    boundary forced only the companion slot -- a no-companion character got
    plain act-1-odds commons at the act transition, and nobody got the
    ratified Rare cards. A pool with no card in the forced tier falls down
    the same rare->uncommon->common ladder the natural roll uses (the ref
    pool has no rares at all; a substituted screen beats an empty one).
    """
    for label, forced in (("companion", companion_rarity),
                          ("card", card_rarity)):
        if forced is not None and forced not in C.RARITY_ODDS:
            raise ValueError(f"unknown {label} rarity {forced!r}")
    pool = character_pool(character_id)
    if not pool:
        # Reachable since ownership became REQUIRED above: a character with
        # no cards of its own now has a genuinely empty pool where it used
        # to inherit the ownerless reference cards. The old code walked the
        # rare->uncommon->common fallback off the end and died on a bare
        # KeyError deep in a dict literal; say what is actually wrong.
        raise ValueError(
            f"no draftable cards for character {character_id!r} -- every "
            "reward card must be owned by the character being offered it. "
            "Check the id, or that its sheet sets `character`.")
    offers = roll_card_offers(rng, character_id, C.REWARD_CARD_OFFERS,
                              card_rarity=card_rarity)
    # companion_offers=0 is a CARD-ONLY screen (The Hunt's extra reward): the
    # slot is absent, not empty, so none of the companion machinery runs.
    if companion_offers and character_id not in NO_COMPANION_CHARACTERS:
        # personal_pool cards are only offered to their own character --
        # a no-op while Klee is the only character, load-bearing the moment
        # a second one exists (Prune must not show up in Furina's rewards).
        comps = {r: cs for r, cs in
                 ((r, [c for c in cs
                       if c.personal_pool in (None, character_id)
                       and not yae_shrine.hidden_from(c.id, character_id)])
                  for r, cs in companion_pool().items()) if cs}
        home = loader.character_nation(character_id)
        for _ in range(companion_offers):
            # THE COMPANION ROLLS LIKE THE CARDS BESIDE IT ([USER]
            # 2026-10-18, legacy review pick 3): the same rarity table and
            # the same empty-tier ladder as the card offers above. The mod
            # rolls the base game's own reward odds (elite odds, the pity
            # counter) and gives the companion the native upgrade roll; the
            # sim's card offers model neither -- one flat RARITY_ODDS, no
            # pity, no reward upgrades -- so the companion matches the cards
            # the sim actually rolls. After a boss it is a Rare, an Uncommon
            # when no Rare companion can be offered.
            if not comps:
                break
            if companion_rarity is not None:
                rarity = companion_rarity
                if rarity not in comps:
                    rarity = _FORCED_COMPANION_FALLBACK.get(rarity, rarity)
                if rarity not in comps:
                    continue
            else:
                rarity = _present_rarity(comps, _roll_rarity(rng))
            pick = _nation_weighted_choice(rng, comps[rarity], home).id
            offers.append(loader.get_card(pick))
    return offers
