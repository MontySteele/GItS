"""Furina kickoff §8: the pre-registered achievability experiment.

    P(>=N same-character companion cards by act 2) under nation-weighted
    rewards, swept over 2-card vs 3-card Fontaine kits, with and without
    Encore Performance, and with and without Guest Star generators.

Run: PYTHONPATH=. python -m tier05.exp_furina_achievability

WHAT THIS MEASURES (and what it does not): the companion OFFER stream and
two bracketing draft strategies over it, using the real reward primitives
(_roll_rarity + _nation_weighted_choice + the real card index) over the
RUNTEMPLATE_VERSION 2 screen count. It deliberately does NOT run combat:
Furina's card sheet does not exist yet, so run mortality would measure
the ref-proxy starter, not draft geometry. Combat-coupled achievability
re-runs at sheet pass 1 (logged as an obligation in the sprint report).

Strategies bracketing real drafting:
  take-all:  depth ceiling -- P(the stream even OFFERS N of one character)
  committed: commit to the first-offered Fontaine character, count only
             that character's subsequent offers (the median-ish floor)

PROTOTYPE ARMS -- experiment scaffolding, NOT ratified card designs:
  +EP  (Encore Performance, duplication): models exactly ONE drafted EP
       per run; it adds +1 depth iff drafted depth >= 1 (you cannot copy
       a card you never drafted -- duplication needs a target).
  +GS  (Guest Star generator, generation): models a drafted generator as
       an effective-depth FLOOR of 1 (a legal Spotlight target always
       exists this combat); it never stacks drafted depth.

Registered prediction under test (kickoff §8, null results binding):
  1. 3-card kits alone put one-character depth 4+ at "reachable but
     luck-gated" (correct for the slot).
  2. Duplication separates the archetype's median from its ceiling.
  3. Neither duplication nor generation substitutes for drafted depth.
"""

from __future__ import annotations

import random
from collections import Counter

from tier0 import constants as C
from tier0.content import loader
from tier05 import rewards

SCREENS = 10          # RUNTEMPLATE_VERSION 2: 8 N + 2 E reward screens
RUNS = 2000
SEED = 20260720
FONTAINE = ("chevreuse", "lynette", "charlotte", "freminet")


def companion_pool(kit_size: int) -> dict[str, list]:
    """rarity -> cards, mirroring rewards.companion_pool + the per-run
    filters roll_rewards applies for Furina (guest/personal exclusions).
    kit_size=2 drops each Fontaine character's uncommon payoff -- the
    2-card-kit counterfactual arm."""
    pool: dict[str, list] = {}
    for c in loader._card_index().values():
        if not c.is_companion or c.guest_star:
            continue
        if c.personal_pool not in (None, "furina"):
            continue
        if (kit_size == 2 and c.nation == "fontaine"
                and c.rarity == "uncommon"):
            continue
        pool.setdefault(c.rarity, []).append(c)
    return {r: sorted(cs, key=lambda c: c.id) for r, cs in pool.items()}


def offer_stream(rng: random.Random, pool: dict[str, list]) -> list:
    offers = []
    for _ in range(SCREENS):
        rarity = rewards._roll_rarity(rng)
        while rarity not in pool:
            rarity = {"rare": "uncommon", "uncommon": "common"}[rarity]
        offers.append(rewards._nation_weighted_choice(
            rng, pool[rarity], "fontaine"))
    return offers


def depths(offers) -> tuple[int, int]:
    counts = Counter(c.character for c in offers
                     if c.character in FONTAINE)
    take_all = max(counts.values(), default=0)
    committed = 0
    for c in offers:                      # commit to first Fontaine char
        if c.character in FONTAINE:
            committed = counts[c.character]
            break
    return take_all, committed


def cell(kit_size: int, ep: bool, gs: bool, strategy: int) -> dict:
    pool = companion_pool(kit_size)
    rng = random.Random(SEED)
    ds = []
    for _ in range(RUNS):
        d = depths(offer_stream(rng, pool))[strategy]
        if ep and d >= 1:
            d += 1                        # one duplication, needs a target
        if gs:
            d = max(d, 1)                 # generation floors, never stacks
        ds.append(d)
    ds.sort()
    return {
        "median": ds[len(ds) // 2],
        "p1": sum(d >= 1 for d in ds) / RUNS,
        "p2": sum(d >= 2 for d in ds) / RUNS,
        "p3": sum(d >= 3 for d in ds) / RUNS,
        "p4": sum(d >= 4 for d in ds) / RUNS,
    }


def main() -> None:
    print(f"Furina achievability (kickoff §8) -- {RUNS} runs/cell, "
          f"seed {SEED}, {SCREENS} screens, "
          f"share={C.SAME_NATION_REWARD_SHARE}")
    header = (f"{'cell':<28}{'median':>7}{'P>=1':>8}{'P>=2':>8}"
              f"{'P>=3':>8}{'P>=4':>8}")
    for strategy, name in ((0, "take-all (ceiling)"),
                           (1, "committed (floor-ish)")):
        print(f"\n== strategy: {name} ==")
        print(header)
        for kit in (3, 2):
            for ep in (False, True):
                for gs in (False, True):
                    r = cell(kit, ep, gs, strategy)
                    label = (f"kit{kit}"
                             + ("+EP" if ep else "")
                             + ("+GS" if gs else ""))
                    print(f"{label:<28}{r['median']:>7}{r['p1']:>8.3f}"
                          f"{r['p2']:>8.3f}{r['p3']:>8.3f}{r['p4']:>8.3f}")


if __name__ == "__main__":
    main()
