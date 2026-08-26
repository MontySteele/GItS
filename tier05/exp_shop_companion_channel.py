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
    AFFORDABLE ON ARRIVAL. A purchase log cannot supply that -- it only
    records what the purse could already reach.
  * whether a companion purchase PRECEDED a relic purchase in the same
    visit, and the relic buy rate with and without a companion buy. That is
    the crowding-out read at visit resolution, where the existing CROWD-OUT
    CHECK block is a run-total comparison across two arms.

THE PRICED-OUT READ, 2026-08-11 (the third instrument defect). The arrival
affordability flag above was printed under the heading "was a preferred
purchase ever priced out?", and when no offer was unaffordable on arrival this
file printed "gold was never the constraint". Neither claim was supported: a
card can be affordable at the door and out of reach by the time the policy
asks for it, and `visit_shop` had two exits that recorded nothing --

  (a) the buy loop's preferred pick costing more than the gold LEFT after
      earlier purchases in the same visit (the entry is dropped and the policy
      re-asked), and
  (b) the loop guard ending the visit the moment gold falls below the cheapest
      remaining shelf entry, stranding whatever is still on the shelf.

Both are now logged in `RunResult.shop_priced_out`, and this file reports the
counts instead of asserting the conclusion. `spent_before` on each record is
the gold already committed at that shop, so "never affordable here at all"
(0) and "priced out by what this visit already bought" (>0) are separable.
The records are pure bookkeeping: nothing reads them and appending them draws
no rng, so every run plays out exactly as it did before they existed.

THE CELL REROUTE, 2026-08-26 (EB-141 half (b), once `M14`'s run was taken and
graded and the world-freeze it declared was spent). Half (a) had made this
file PRINT the live `RT/D/P/C` stamp beside a `model.run_many` it called
itself, which was the most a registration window allowed: a `Cell` carries its
own seed, runs, plan resolution and run entry, so rerouting inside the window
could have moved the registered seed. It no longer can, and R68's actual
answer is now in force -- every arm is a `Cell` derived from `BASE_CELL`, and
the stamp is the run object's own. The reroute is argument-for-argument the
call it replaces, and `tier05/tests/test_eb141b_shop_cell.py` pins that by
CAPTURING the arguments rather than by re-running the registered-seed sweep.

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

from tier05 import cells, expcli, stats

RUNS = 500
CHARACTERS = [("klee", "demolition"), ("furina", "salon"), ("kokomi", "priest")]
SEED = 20260725


# The repo's standard read for a winrate cell. Was a second implementation of
# run_metrics._wilson95 with the same arithmetic and the same return shape;
# unified into tier05.stats by the sim-hygiene sprint (2026-07-29). This copy
# is where the [0, 1] clamp came from and the shared one keeps it.
wilson = stats.wilson95


# THE BASE CELL (EB-141b, 2026-08-26). The instrument used to call
# `model.run_many` directly and print the world beside the run; it now runs a
# `Cell`, which is R68's actual answer -- the stamp is CARRIED BY THE OBJECT
# THAT DOES THE RUN, so a report cannot name a world its rows did not come
# from. Every field here is the argument the direct call was already passing,
# written down instead of implied:
#
#   * REALISTIC + 3 acts -- the world every archived winrate cell was measured
#     in (relics and potions on; a bare 1-act run wins ~0% and would make P2 a
#     comparison of two zeroes).
#   * `jobs=1` is LOAD-BEARING, not a default. The arms differ by a
#     monkeypatch on `shop.visit_shop`, which worker PROCESSES do not inherit;
#     `Cell`'s own default is 0 (one worker per CPU), so leaving it out would
#     silently run the "on" arm with the channel off.
#   * `policy="assigned"` resolves to the same `draft.assigned_policy` object
#     the direct call passed, through `draft.POLICIES` -- and the plan's pilot
#     resolves to the archetype id for all three rows, which is what the
#     direct call hardcoded by passing `archetype` twice.
#
# The reroute is therefore ARGUMENT-FOR-ARGUMENT the pre-existing call and
# the registered seed plays out unchanged; `tier05/tests/test_eb141b_shop_cell.py`
# asserts exactly that, by capturing the arguments rather than by running the
# sweep.
BASE_CELL = cells.Cell(name="§4.7 companion channel",
                       character=CHARACTERS[0][0], archetype=CHARACTERS[0][1],
                       runs=RUNS, seed=SEED, route="hunter",
                       policy="assigned", realistic=True, n_acts=3, jobs=1)


def arm_cell(character: str, archetype: str, runs: int, companions: bool):
    """The Cell for one arm, DECLARED as a delta off `BASE_CELL`.

    `companions` cannot be a Cell field -- it is a monkeypatch on
    `shop.visit_shop`, not a run parameter -- so it goes in the NAME, which is
    where `Cell` puts every other divergence it cannot carry structurally
    (`pilot_override`, `force_cards`). A stamp that did not say which arm it
    came from would be an on-arm row claiming to be the control.
    """
    return BASE_CELL.but(
        character=character, archetype=archetype, runs=runs,
        name=f"§4.7 {character}/{archetype} "
             f"companions={'on' if companions else 'off'}")


def arm(character: str, archetype: str, runs: int, companions: bool):
    import tier05.shop as shop_mod
    original = shop_mod.visit_shop

    def patched(*args, **kwargs):
        kwargs["companions"] = companions
        return original(*args, **kwargs)

    cell = arm_cell(character, archetype, runs, companions)
    shop_mod.visit_shop = patched
    try:
        return cell.run()
    finally:
        shop_mod.visit_shop = original


def main() -> int:
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else RUNS
    # The R68 stamp, now ROUTED rather than printed (EB-141b). Half (a) read
    # the four live version attributes and printed them beside a run this file
    # made itself; the run is now a `Cell` and the line is that Cell's own
    # `stamp()`, so the world, the seed and n come off the object that did the
    # work. `Cell.stamp()` names no character, so heading a three-character
    # sweep with the base cell's line claims nothing the rows do not support --
    # each arm renames itself in `arm_cell` and the arm names are what carry
    # the on/off divergence.
    header = BASE_CELL if runs == BASE_CELL.runs else BASE_CELL.but(runs=runs)
    print(header.stamp())
    # KEPT VERBATIM. Every line this instrument printed before is printed
    # unchanged, so the numbers already published against it -- the graded M14
    # read of 2026-08-26 among them -- stay line-comparable.
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
    unaffordable_on_arrival: Counter = Counter()   # (slot, rarity) -> offers
    gold_at_visit: list[int] = []

    # NEW (2026-08-11): the two exits that used to record nothing. Keyed the
    # same way so the three reads read side by side.
    pick_priced_out: Counter = Counter()     # (channel/slot, rarity)
    pick_priced_out_after_buys = 0           # of those, spent_before > 0
    residual_stranded: Counter = Counter()
    residual_by_exit: Counter = Counter()    # "guard" vs "skip"
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
                    unaffordable_on_arrival[
                        (offer["slot"], offer["rarity"])] += 1
                if offer["visit"] not in visits_seen:
                    visits_seen.add(offer["visit"])
                    gold_at_visit.append(offer["gold_at_visit"])

            # NEW (2026-08-11): what gold could not reach DURING the visit.
            # Two kinds, and they answer different halves of the money
            # question: a preferred pick the policy named and could not pay
            # for (`residual` False), and a shelf entry still unaffordable
            # when the loop ended (`residual` True). `spent_before` > 0 is the
            # case the arrival flag structurally cannot see -- the card was
            # inside the purse at the door and outside it by the time the
            # policy asked.
            for ev in r.shop_priced_out:
                where = (f"slot {ev['slot']}" if ev["channel"] == "companion"
                         else "character shelf")
                if ev["residual"]:
                    residual_stranded[(where, ev["rarity"])] += 1
                    residual_by_exit[ev["exit"]] += 1
                else:
                    pick_priced_out[(where, ev["rarity"])] += 1
                    if ev["spent_before"] > 0:
                        pick_priced_out_after_buys += 1

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
    print("\nNEW  MONEY AT THE DOOR, AND DURING THE VISIT (what gold could "
          "not reach, and when)")
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
    n_arrival = sum(unaffordable_on_arrival.values())
    if unaffordable_on_arrival:
        detail = ", ".join(
            f"slot {s} {r} x{n}"
            for (s, r), n in sorted(unaffordable_on_arrival.items()))
        print(f"NEW      unaffordable on arrival: {n_arrival} ({detail})")
    else:
        print("NEW      unaffordable on arrival: none")

    # The two mid-visit exits. Reported as counts, never as a verdict: whether
    # these numbers mean price governs the channel is the [USER] call the
    # re-run registration reserves (Q2, §5).
    n_pick = sum(pick_priced_out.values())
    if pick_priced_out:
        detail = ", ".join(f"{w} {r} x{n}"
                           for (w, r), n in sorted(pick_priced_out.items()))
        print(f"NEW      preferred picks priced out mid-visit: {n_pick} "
              f"({pick_priced_out_after_buys} after earlier buys in the same "
              f"visit, {n_pick - pick_priced_out_after_buys} unaffordable "
              f"from the door) -- {detail}")
    else:
        print("NEW      preferred picks priced out mid-visit: 0")

    n_res = sum(residual_stranded.values())
    if residual_stranded:
        detail = ", ".join(f"{w} {r} x{n}"
                           for (w, r), n in sorted(residual_stranded.items()))
        print(f"NEW      shelf entries stranded at loop exit: {n_res} "
              f"({residual_by_exit['guard']} on the gold guard, "
              f"{residual_by_exit['skip']} on a policy skip) -- {detail}")
    else:
        print("NEW      shelf entries stranded at loop exit: 0")

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
    expcli.help_if_asked(__doc__)
    raise SystemExit(main())
