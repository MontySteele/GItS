#!/usr/bin/env python3
"""Track C diagnostic cells for the Featured Banner going live (R64).

R14 APPLIES: these are DIAGNOSTICS, never acceptance targets. Nothing here is
a gate; the numbers exist so the red-pen session can see what the banner did.

C1 -- Furina slot-1 Rare-offer availability with the banner live.
     Which Fontaine Rare gets excluded, how often slot 1 can answer a Rare
     roll from her own nation, and how often the ladder's nation-widening rung
     fires. Registered expectation: the widening rate drops to ~0 for Fontaine
     now that she has four Rares, where it used to be the everyday path.

C2 -- winrate spread across banner rolls, Furina, one archetype, everything
     else fixed. Registered expectation, graded in writing BEFORE the run:
     the spread is SMALL. The pool is enabler-grade and no single Rare should
     swing a run. A large spread is a §4.3 smell on whichever card drives it,
     not a banner problem -- and the knob order if it lands out of expectation
     is the CARD's numbers first, banner constants never (banner constants are
     structure, not tuning).

Offers are read off real runs (RunResult.shop_companion_offers, .banner)
rather than synthesised, so the cells measure the channel players meet.

    python tools/banner_variance_cells.py [--runs N] [--archetype NAME]
"""
from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

# parents[2], not parent.parent: this file moved down a level into
# tools/archive/ (audit sec.6). The old two-hop landed on tools/ and made the
# module unimportable -- archiving a script must not silently break it.
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tier0 import constants as C            # noqa: E402
from tier05 import draft, model, rewards, run_metrics    # noqa: E402


def c1(results, home: str = "fontaine") -> dict:
    roster = {c.id for c in rewards.five_star_roster(home)}
    excluded = collections.Counter()
    slot1_total = slot1_home_rare = slot1_widened = 0
    slot1_rarity = collections.Counter()

    for r in results:
        missing = roster - r.banner
        for card_id in missing:
            excluded[card_id] += 1
        for offer in r.shop_companion_offers:
            if offer.get("slot") != 1:
                continue
            slot1_total += 1
            slot1_rarity[offer.get("rarity")] += 1
            card = offer.get("id")
            nation = None
            try:
                from tier0.content import loader
                nation = loader.get_card(card).nation
            except Exception:                       # pragma: no cover
                pass
            if nation != home:
                slot1_widened += 1
            elif offer.get("rarity") == "rare":
                slot1_home_rare += 1

    return {
        "runs": len(results),
        "roster": sorted(roster),
        "excluded_counts": dict(excluded),
        "slot1_offers": slot1_total,
        "slot1_rarity_mix": dict(slot1_rarity),
        "slot1_home_rare": slot1_home_rare,
        "slot1_widened": slot1_widened,
        "slot1_widen_rate": (slot1_widened / slot1_total) if slot1_total else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=200)
    ap.add_argument("--archetype", default="salon")
    ap.add_argument("--seed", type=int, default=4100)
    args = ap.parse_args()

    print(f"BANNER_FEATURED_SLOTS = {C.BANNER_FEATURED_SLOTS}")
    print(f"designed nations      = {rewards.designed_nations()}")
    for nation in rewards.designed_nations():
        roster = rewards.five_star_roster(nation)
        live = "SELECTIVE" if len(roster) > C.BANNER_FEATURED_SLOTS else "features all"
        print(f"  {nation:10s} {len(roster)} 5-star(s)  [{live}]")

    print(f"\nrunning {args.runs} Furina/{args.archetype} runs...")
    # REALISTIC LOADOUT, not the bare world. The house measurement convention
    # runs with relics and potions granted, and it is not optional here: the
    # bare world's Furina winrate is ~0, and a winrate SPREAD measured across
    # banner groups that all lost is 0.000 for a reason that has nothing to do
    # with the banner. Measured before fixing it: 200 bare runs, 0 wins,
    # spread 0.000 -- a cell that looks like a clean pass and says nothing.
    results = model.run_many("furina", args.archetype, args.archetype,
                             draft.assigned_policy, runs=args.runs,
                             seed=args.seed, jobs=0,
                             grant_relics=True, grant_potions=True)

    print("\n--- C1: slot-1 Rare availability, banner live ---")
    cell = c1(results)
    for k in ("runs", "slot1_offers", "slot1_rarity_mix", "slot1_home_rare",
              "slot1_widened", "slot1_widen_rate"):
        print(f"  {k:18s} {cell[k]}")
    print("  excluded-from-banner counts (each run drops exactly one):")
    for cid, n in sorted(cell["excluded_counts"].items()):
        print(f"    {cid:38s} {n:4d}  ({n / max(1, cell['runs']):.1%})")
    missing_never = set(cell["roster"]) - set(cell["excluded_counts"])
    if missing_never:
        print(f"    NEVER EXCLUDED (permanently featured): {sorted(missing_never)}")

    print("\n--- C2: winrate spread across banner rolls ---")
    bv = run_metrics.banner_variance(results)
    print(f"  distinct_banners  {bv['distinct_banners']}")
    print(f"  degenerate        {bv['degenerate']}")
    print(f"  spread            {bv['spread']:.3f}")
    overall = sum(r.won for r in results) / len(results)
    print(f"  overall winrate   {overall:.3f}")

    # GRADE AGAINST THE NOISE BAND, NOT AGAINST A FEELING. "The spread is
    # small" is not gradeable on its own: a spread is only evidence of a real
    # effect if it exceeds what identical groups would produce by sampling
    # alone. Expected RANGE of k binomial groups is ~2.5 sd for small k, and sd
    # here is sqrt(p(1-p)/n) at the per-group width. A spread INSIDE this band
    # is consistent with "no card swings a run" -- it is not proof of it, and
    # the honest statement is that the cell cannot distinguish them at this n.
    counts = list(bv["runs_per_banner"].values())
    per_group = sum(counts) / len(counts) if counts else 0
    sd = (overall * (1 - overall) / per_group) ** 0.5 if per_group else 0.0
    band = 2.5 * sd
    print(f"  per-group n       {per_group:.0f}")
    print(f"  noise band (~2.5 sd of the range) {band:.3f}")
    verdict = ("WITHIN the noise band -- consistent with the registered "
               "expectation, and NOT evidence of a real effect"
               if bv["spread"] <= band else
               "EXCEEDS the noise band -- a real spread; per the registered "
               "grading this is a 4.3 smell on a CARD, and the knob is that "
               "card's numbers, never a banner constant")
    print(f"  grading           {verdict}")
    thin = {b: n for b, n in bv["runs_per_banner"].items() if n < 30}
    if thin:
        print(f"  NOTE: {len(thin)} banner group(s) under 30 runs; treat the "
              "spread as indicative only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
