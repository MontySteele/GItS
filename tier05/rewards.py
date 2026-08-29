"""Reward generation (spec §3) — OUR design, the thing under test.

After each fight: REWARD_CARD_OFFERS character cards rarity-rolled, plus
the companion slot. All three spec slot modes now exist -- standard (M5),
pity(k) (triage ruling 4), choose3 (EB-27) -- and `model.run_one` is what
decides how many offers the slot shows on any given screen. Skip
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
    index = loader._card_index()
    # The QUARANTINED offerable-pool swap, and the only one there is
    # (`loader._pool_substitutions`, behind `C.KURAGE_MEMORY`): {} on every
    # flag-off tree, so the loop below is byte-for-byte what it has always
    # been. This function is the single source of truth for "which ids can be
    # offered to this character" -- `roll_card_offers`, `roll_rewards`,
    # `shop.shop_offer`, every `events` card screen and the tier 0.5 drafter
    # read it and nothing else -- so gating it HERE gates every offer surface
    # at once, which is the point of putting the seam at the source instead of
    # at the five mouths.
    subs = loader.pool_substitutions(character_id)
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
        if c.id in subs:
            # SAME RARITY SLOT, SAME WEIGHT: the prototype is filed under the
            # SHIPPED row's rarity, and a prototype that declares a different
            # one is refused rather than quietly promoted or demoted. A
            # substitution is a face swap; moving a card between tiers would
            # move the odds it is offered at, which is a balance change
            # smuggled in as a quarantine.
            proto = loader.peek_card(subs[c.id])
            if proto.rarity != c.rarity:
                raise ValueError(
                    f"pool substitution {c.id!r} -> {proto.id!r}: the "
                    f"prototype is {proto.rarity!r} but the shipped row is "
                    f"{c.rarity!r}; a substitution must not move a card "
                    "between rarity tiers")
            c = proto
        pool.setdefault(c.rarity, []).append(c)
    return {r: sorted(cs, key=lambda c: c.id) for r, cs in pool.items()}


@lru_cache(maxsize=1)
def companion_pool() -> dict[str, list[Card]]:
    """rarity -> companion cards. 5-star cards ARE the rares (§3)."""
    pool: dict[str, list[Card]] = {}
    for c in loader._card_index().values():
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


@lru_cache(maxsize=1)
def designed_nations() -> tuple[str, ...]:
    """Every nation with at least one banner-eligible 5-star, sorted.

    DERIVED, never listed. The literal default this replaced -- roll_banner's
    ``nations=("mondstadt",)`` -- was correct on the day it was written and
    silently wrong from the day Inazuma got its first 5-star: the run model's
    one call site never passed an argument, so every run of every character
    rolled a MONDSTADT-ONLY banner, and `_banner_filtered` then dropped every
    other nation's 5-stars from both the reward slot and the shop. Measured
    before the fix: across 400 seeds a Kokomi run was offered Albedo, Durin and
    Nicole and never Itto or Raiden -- Inazuma's own Rares, one of them written
    as "the conscription jackpot", unreachable in her own runs.

    A hardcoded nation list is a thing someone must remember to update. This is
    not.
    """
    nations = {c.nation for c in loader._card_index().values()
               if c.is_companion and c.star == 5 and c.nation
               and c.personal_pool is None and not c.guest_star}
    return tuple(sorted(nations))


def roll_banner(rng: random.Random,
                nations: tuple[str, ...] | None = None) -> frozenset[str]:
    """The run's Featured Banner: BANNER_FEATURED_SLOTS limited 5-stars per
    nation, drawn once per run and fixed for its duration.

    Returns the set of featured 5-star card ids. Nations with no more
    designed 5-stars than slots feature all of them, which is why this is a
    no-op at the v0.1 roster and why the roll is still worth having: the
    governor exists before the roster needs it.

    In co-op each player rolls their own banner -- divergent lineups are the
    point -- so this deliberately takes an rng rather than reading a global.

    ``nations=None`` means EVERY designed nation, which is what §4.2 describes
    ("3 limited 5-stars per nation") and the only correct setting for a run:
    the reward slot's uniform half and the shop's wildcard slot both offer
    off-nation 5-stars, so a banner that omits a nation does not thin that
    nation -- it DELETES it. See designed_nations().
    """
    if nations is None:
        nations = designed_nations()
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


# The rarity ladder a screen walks down when the tier it rolled has nothing
# to offer -- a pool may genuinely lack a tier (the reference pools have no
# rares at all), and a substituted screen beats an empty one.
_RARITY_FALLBACK = {"rare": "uncommon", "uncommon": "common"}


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
    exactly as an absent tier does. `distinct=False` reproduces
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
        while rarity not in pool:            # ref pool may lack a rarity
            rarity = _RARITY_FALLBACK[rarity]
        cands = pool[rarity]
        if distinct:
            while all(c.id in taken for c in cands):
                nxt = _RARITY_FALLBACK.get(rarity)
                if nxt is None:
                    break
                rarity = nxt
                while rarity not in pool:
                    rarity = _RARITY_FALLBACK[rarity]
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
                 banner: frozenset[str] | None = None,
                 companion_rarity: str | None = None,
                 card_rarity: str | None = None) -> list[Card]:
    """One post-fight reward screen: card offers + the companion slot.
    companion_offers > 1 is the pity/choose-3 slot (triage ruling 4
    pulled the mechanism forward from M7; the run model decides when).

    banner is the run's Featured Banner (v1.8); None means unrestricted,
    which is the pre-v1.8 behaviour and what the Tier 0 fight-level tests
    still want. Off-banner 5-stars are removed before the rarity roll, so a
    banner that empties the rare tier falls through to uncommon exactly as a
    naturally rare-less pool already does. ``companion_rarity="rare"`` is
    the post-boss rule for the Companion slot; ``card_rarity="rare"`` forces
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
                 ((r, [c for c in _banner_filtered(cs, banner)
                       if c.personal_pool in (None, character_id)])
                  for r, cs in companion_pool().items()) if cs}
        home = loader.character_nation(character_id)
        for _ in range(companion_offers):
            rarity = companion_rarity or _roll_rarity(rng)
            if companion_rarity is not None:
                # Rare-only means rare-only: if a future roster has no card
                # in the forced tier, omit the slot rather than substituting
                # a lower-rarity companion.
                if rarity not in comps:
                    continue
            else:
                while rarity not in comps:
                    rarity = {"rare": "uncommon", "uncommon": "common"}[rarity]
            offers.append(loader.get_card(
                _nation_weighted_choice(rng, comps[rarity], home).id))
    return offers
