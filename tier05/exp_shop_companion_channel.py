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

INSTRUMENT REPAIRS, 2026-08-10 (two confirmed defects; the world moved the
same day, see CONSTANTS_VERSION 9). Numbers this file printed before today
were measured with a broken P1 and a guessed slot-2 rarity AND in a world
where slot 2 could sell Commons; they are archive twice over.

  (a) P1 ATTRIBUTION. A purchase used to be matched to an offer by SLOT
      ALONE, over a set built per RUN: `bought = {p["slot"] for p in r.shop}`.
      Both logs are flattened across every shop the run walks into, so one
      slot-1 purchase at the third shop marked slot 1 as bought at the first
      and second shops too. On a 3-act run that is up to three visits, and
      the reported buy rate was inflated by exactly the visits the player
      declined. The join is now (visit, slot): `shop.visit_shop` stamps a
      run-local visit index on every offer and every purchase record.
  (b) SLOT-2 PURCHASE RARITY. It used to be inferred as
      `"rare" if price >= 150 else "uncommon"`, with a comment claiming the
      rarity was "recoverable from the price band". It was not: while slot 2
      could roll Commons, every 50-gold Common purchase was counted as an
      Uncommon, which is the exact bucket P3 grades. The purchase record now
      carries the card's TRUE rarity and this file reads it.

NEW READS added the same day, all additive and printed on lines marked NEW --
every pre-existing output line is unchanged so the published numbers stay
reproducible:

  * gold in hand at each shop visit, and whether each companion offer was
    AFFORDABLE at that moment. This is the money question S4-G10 asks
    ("was a preferred purchase ever priced out?"), and a purchase log cannot
    answer it -- it only records what the purse could already reach.
  * whether a companion purchase PRECEDED a relic purchase in the same
    visit, and the relic buy rate with and without a companion buy. That is
    the crowding-out read at visit resolution, where the existing CROWD-OUT
    CHECK block is a run-total comparison across two arms.

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

    # NEW (2026-08-10), all additive: the affordability read, the purse at the
    # door, and the visit-level crowd-out.
    offered_by_slot: Counter = Counter()
    affordable_by_slot: Counter = Counter()
    priced_out: Counter = Counter()          # (slot, rarity) -> offers out of reach
    gold_at_visit: list[int] = []
    visits_with_companion = visits_without_companion = 0
    companion_then_relic = relic_without_companion = 0

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
            # THE JOIN IS (visit, slot), not slot. Both logs are flattened
            # across every shop the run entered, so a slot key alone credits
            # one purchase to every visit that offered that slot -- see the
            # module docstring, repair (a).
            bought = {(p["visit"], p["slot"]) for p in r.shop
                      if p.get("channel") == "companion"}
            visits_seen: set[int] = set()
            for offer in r.shop_companion_offers:
                key = (offer["visit"], offer["slot"])
                if offer["slot"] == 1:
                    slot1_offered += 1
                    if key in bought:
                        slot1_bought += 1
                else:
                    slot2_rarities[offer["rarity"]] += 1

                # NEW (2026-08-10): the money read. `affordable` is priced
                # against gold at the START of the visit, so it answers "could
                # the player have had this at all", not "was there change left
                # after the character shelf".
                offered_by_slot[offer["slot"]] += 1
                if offer["affordable"]:
                    affordable_by_slot[offer["slot"]] += 1
                else:
                    priced_out[(offer["slot"], offer["rarity"])] += 1
                if offer["visit"] not in visits_seen:
                    visits_seen.add(offer["visit"])
                    gold_at_visit.append(offer["gold_at_visit"])

            # NEW: crowding-out at VISIT resolution. Within a visit the
            # companion slots resolve inside visit_shop and the relic shelf
            # is offered afterwards by model.resolve_shop, so a companion
            # purchase always PRECEDES a relic purchase in the same visit by
            # construction -- which is precisely why the interesting number is
            # the relic buy rate conditioned on whether the purse was already
            # spent on a companion.
            comp_visits = {p["visit"] for p in r.shop
                           if p.get("channel") == "companion"}
            relic_visits = {p["visit"] for p in r.shop
                            if p.get("buy") == "relic"}
            for v in visits_seen:
                if v in comp_visits:
                    visits_with_companion += 1
                    if v in relic_visits:
                        companion_then_relic += 1
                else:
                    visits_without_companion += 1
                    if v in relic_visits:
                        relic_without_companion += 1

            for p in r.shop:
                if p.get("channel") == "companion":
                    price_paid += p["price"]
                    if p["slot"] == 2:
                        # TRUE rarity off the purchase record. This used to be
                        # a two-way guess from the price band, which folded
                        # every Common buy into the Uncommon bucket -- the
                        # bucket P3 grades. See the docstring, repair (b).
                        slot2_bought_rarities[p["rarity"]] += 1

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

    # --- NEW reads (2026-08-10). Everything above this line prints exactly
    # what it printed before the instrument repair, so the published numbers
    # stay reproducible; everything below is additional and labelled NEW.
    print("\nNEW  MONEY AT THE DOOR (was a preferred purchase ever priced "
          "out?)")
    if gold_at_visit:
        ordered = sorted(gold_at_visit)
        mean_gold = sum(ordered) / len(ordered)
        median_gold = ordered[len(ordered) // 2]
        print(f"NEW      gold on arrival: mean {mean_gold:6.1f}  median "
              f"{median_gold:4d}  min {ordered[0]}  max {ordered[-1]}  "
              f"({len(ordered)} visits)")
    for slot in (1, 2):
        n = offered_by_slot[slot]
        ok = affordable_by_slot[slot]
        rate = ok / n if n else 0.0
        print(f"NEW      slot {slot}: {ok}/{n} offers affordable on arrival "
              f"({rate:.1%})")
    if priced_out:
        detail = ", ".join(f"slot {s} {r} x{n}"
                           for (s, r), n in sorted(priced_out.items()))
        print(f"NEW      priced out: {detail}")
    else:
        print("NEW      priced out: none -- gold was never the constraint")

    print("\nNEW  CROWD-OUT AT VISIT RESOLUTION (a companion buy always "
          "precedes the relic shelf in the same visit)")
    for label, visits, relics in (
            ("companion bought", visits_with_companion, companion_then_relic),
            ("none bought", visits_without_companion, relic_without_companion)):
        rate = relics / visits if visits else 0.0
        print(f"NEW      {label:18s} {visits:6d} visits   relic also bought "
              f"{relics:6d} ({rate:.1%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
