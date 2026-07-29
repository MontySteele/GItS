"""§4.7 shop companion channel -- the Track C measurement cell (R61).

Grades the three predictions pre-registered in
`docs/archive/shop-companion-channel-sprint.md` §3, BEFORE the numbers are read:

  P1  slot-1 buy rate lands in 10-35% of visits where slot 1 was offered.
      Below 10% = pricing over-governs (the premium slot goes unbought);
      above 35% = under-priced against card-remove and relic competition.
  P2  winrate delta from enabling the channel is POSITIVE but <= +2.0pp.
      Targeted access, not a power injection.
  P3  slot-2 realized rarity mix is Uncommon-heavy (>= 60% of slot-2
      purchases), because gold pressure biases toward the cheaper tier.
      DIAGNOSTIC, not an acceptance target (R14 discipline).

ONE VARIABLE PER CELL: the only thing that differs between the two arms is
`companions`. Same seeds, same character, same policy, same everything else.
The arms are not strictly paired -- switching the channel on also consumes
rng, so run N diverges rather than differing only at the shop -- which is why
the read is a distribution over many runs and not a per-seed diff.

Usage: python -m tier05.exp_shop_companion_channel [runs]
"""

from __future__ import annotations

import sys
from collections import Counter

from tier05 import draft, model, stats

RUNS = 500
CHARACTERS = [("klee", "demolition"), ("furina", "salon"), ("kokomi", "priest")]
SEED = 20260725


# The repo's standard read for a winrate cell. Was a second implementation of
# run_metrics._wilson95 with the same arithmetic and the same return shape;
# unified into tier05.stats by the sim-hygiene sprint (2026-07-29). This copy
# is where the [0, 1] clamp came from and the shared one keeps it.
wilson = stats.wilson95


def arm(character: str, archetype: str, runs: int, companions: bool):
    import tier05.shop as shop_mod
    original = shop_mod.visit_shop

    def patched(*args, **kwargs):
        kwargs["companions"] = companions
        return original(*args, **kwargs)

    # REALISTIC + 3 acts, matching the world every archived winrate cell was
    # measured in (relics and potions on; a bare 1-act run wins ~0% and would
    # make P2 a comparison of two zeroes). jobs stays 1: the arms differ by a
    # monkeypatch, which worker PROCESSES would not inherit.
    shop_mod.visit_shop = patched
    try:
        return model.run_many(character, archetype, archetype,
                              draft.assigned_policy, runs, SEED,
                              grant_relics=True, grant_potions=True,
                              n_acts=3)
    finally:
        shop_mod.visit_shop = original


def main() -> int:
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else RUNS
    print(f"§4.7 companion channel -- {runs} runs/arm, seed {SEED}\n")

    slot1_offered = slot1_bought = 0
    slot2_rarities: Counter = Counter()
    slot2_bought_rarities: Counter = Counter()
    price_paid = 0
    deltas = []

    # P1's band assumes the drafter TRADES OFF companions against card-remove
    # and relics for the same gold. visit_shop buys CARDS FIRST by
    # construction, and model.py offers the relic later still, so companions
    # get first claim on the purse. Measuring what the other two doors do
    # across the arms is what separates "under-priced" from "first in line" --
    # if the channel were merely cheap, removals and relics would be roughly
    # unchanged; if it is crowding them out, they fall.
    crowding = {"removals": [0, 0], "relics": [0, 0], "gold_left": [0, 0]}

    for character, archetype in CHARACTERS:
        off = arm(character, archetype, runs, companions=False)
        on = arm(character, archetype, runs, companions=True)

        for i, batch in enumerate((off, on)):
            crowding["removals"][i] += sum(r.removal_uses for r in batch)
            crowding["relics"][i] += sum(
                1 for r in batch for p in r.shop if p.get("buy") == "relic")
            crowding["gold_left"][i] += sum(r.gold for r in batch)

        w_off = sum(1 for r in off if r.won) / len(off)
        w_on = sum(1 for r in on if r.won) / len(on)
        lo, hi = wilson(sum(1 for r in on if r.won), len(on))
        deltas.append((character, w_off, w_on, w_on - w_off))
        print(f"{character:8s} {archetype:12s} "
              f"off {w_off:6.1%}  on {w_on:6.1%}  "
              f"delta {(w_on - w_off) * 100:+5.2f}pp  "
              f"(on 95% CI {lo:.1%}-{hi:.1%})")

        for r in on:
            bought = {(p["slot"]) for p in r.shop
                      if p.get("channel") == "companion"}
            for offer in r.shop_companion_offers:
                if offer["slot"] == 1:
                    slot1_offered += 1
                    if 1 in bought:
                        slot1_bought += 1
                else:
                    slot2_rarities[offer["rarity"]] += 1
            for p in r.shop:
                if p.get("channel") == "companion":
                    price_paid += p["price"]
                    if p["slot"] == 2:
                        # rarity is recoverable from the price band
                        slot2_bought_rarities[
                            "rare" if p["price"] >= 150 else "uncommon"] += 1

    print()
    p1 = slot1_bought / slot1_offered if slot1_offered else 0.0
    print(f"P1  slot-1 buy rate: {p1:.1%} "
          f"({slot1_bought}/{slot1_offered} visits)   "
          f"{'IN BAND' if 0.10 <= p1 <= 0.35 else 'OUT OF BAND'} (10-35%)")

    mean_delta = sum(d for _, _, _, d in deltas) / len(deltas)
    p2_ok = 0 < mean_delta <= 0.02
    print(f"P2  mean winrate delta: {mean_delta * 100:+.2f}pp   "
          f"{'IN BAND' if p2_ok else 'OUT OF BAND'} (positive, <= +2.00pp)")

    n2 = sum(slot2_bought_rarities.values())
    unc = slot2_bought_rarities["uncommon"] / n2 if n2 else 0.0
    print(f"P3  slot-2 purchases: {unc:.1%} uncommon of {n2}   "
          f"{'IN BAND' if unc >= 0.60 else 'OUT OF BAND'} (>= 60%, DIAGNOSTIC)")
    print(f"    slot-2 OFFERED mix: {dict(slot2_rarities)}")
    print(f"    total gold spent on companions: {price_paid}")

    print("\nCROWD-OUT CHECK (does the channel take gold from the other "
          "doors, or just get there first?)")
    for label in ("removals", "relics", "gold_left"):
        a, b = crowding[label]
        pct = (b - a) / a * 100 if a else 0.0
        print(f"    {label:10s} off {a:7d}   on {b:7d}   {pct:+6.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
