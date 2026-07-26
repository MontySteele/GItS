"""E2 (Neap Tide v2.1): the full batch, measured where it landed.

Section 5's knob order was A1 alone -> E1 -> A-remainder + F batch -> E2. This
is that second measurement.

WHAT E2 IS COMPARED AGAINST, and why it is not a patched arm. E1 could vary
its knob with a module attribute, so both its arms ran in one process. The F
batch is a SHEET change -- cards merged, dropped, re-costed, re-rarified -- and
there is no attribute that recovers the old pool. So E2 reports the landed
world and is read against two references that already exist:

  * E1's x3 arm, which is the MULTIPLIER-ONLY world at the same cell, same
    seed, same constants. The E1x3 -> E2 delta is therefore the F batch's
    own contribution, which is exactly the attribution P9 asks for.
  * the same-world roster anchors (tier05.exp_roster_anchors), which say
    whether the landed numbers are calibrated rather than merely changed.

Neither reference is quoted from an archive. Both were produced under C4, and
the anchors can be re-run in one command against this same tree.

HONEST CAVEAT, stated because it would otherwise be buried: the F batch
changed the DRAFT POOL (swift_currents merged away, before_sun_and_moon added),
so E1's arms and E2 do not draw from an identical pool. That is unavoidable --
it is the change under test -- and it means the E1x3 -> E2 delta is "the F
batch including its pool effects", not a clean single-variable contrast. It is
labelled that way everywhere it is reported.

Usage: python -m tier05.exp_neap_tide_e2 [--runs N] [--seed N] [--route NAME]
"""

from __future__ import annotations

import sys
import time

from tier05 import burst_telemetry, cells, kurage_telemetry

PLANS = ("priest", "commander", "assist", "generic")

# E1's x3 arm, 600 runs, seed 11, C4 -- the multiplier-only world. Recorded
# here as literals ON PURPOSE: they are a measurement this repo already made
# and can re-make (python -m tier05.exp_neap_tide_e1), and a script that
# re-ran them every time would triple E2's cost to restate a known row.
# act-1 clear %, win %, mean charge at pulse time in act 1.
E1_X3 = {
    "priest":    {"act1": 60.3, "win": 8.7, "charge_a0": 6.4},
    "commander": {"act1": 66.0, "win": 6.7, "charge_a0": 5.3},
    "assist":    {"act1": 50.2, "win": 1.2, "charge_a0": 4.7},
    "generic":   {"act1": 55.7, "win": 6.0, "charge_a0": 4.8},
}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    base = cells.CANONICAL.but(character="kokomi", archetype="priest")
    base, rest = cells.parse_overrides(argv, base)
    if rest:
        raise SystemExit(f"unexpected argument(s): {' '.join(rest)}")

    cells.print_header(
        base, "E2 -- the full batch (Neap Tide v2.1)",
        subject="kokomi, all four plans", varying=("archetype",))
    print("  Landed world: R73 x3 + Before Sun and Moon + the F batch")
    print("  (R74 Garment splash, R75 Honor Guard, R77 Shoal, R78 Muster,")
    print("   G6 tactical_retreat, G8 moonlit_offering merge).")
    print("  Reference: E1's x3 arm = multiplier-only, same cell/seed/C4.")
    print("  CAVEAT: the F batch moved the draft pool, so this delta is 'the")
    print("  F batch including its pool effects', not a single variable.")

    t0 = time.perf_counter()
    arms = {}
    for plan in PLANS:
        arm = base.but(archetype=plan).arm()
        arm["pulses"] = kurage_telemetry.by_act(
            [pair for r in arm["results"] for pair in r.kurage_traces])
        arm["burst"] = burst_telemetry.tally(arm["results"])
        arms[plan] = arm

    print()
    print(f"{'plan':11} {'win%':>6} {'d E1x3':>7} {'act1%':>6} {'d E1x3':>7} "
          f"{'acts':>5} {'deck':>5} {'fights':>6}")
    print("-" * 66)
    for plan in PLANS:
        a, ref = arms[plan], E1_X3[plan]
        print(f"{plan:11} {a['win']*100:6.1f} {a['win']*100-ref['win']:+7.1f} "
              f"{a['act1']*100:6.1f} {a['act1']*100-ref['act1']:+7.1f} "
              f"{a['acts']:5.2f} {a['decksize']:5.1f} {a['fights']:6.2f}")

    # P9: the accrual question. Section 5 sanctioned ONE accrual reduction
    # (G6) and the batch shipped two -- G8 also removed moonlit_offering's
    # exhaust_from 2 and gain_charge 3. Mean charge AT PULSE TIME in act 1 is
    # the reading that answers it, and it is already act-tagged.
    print()
    print("P9 -- act-1 Charge accrual (mean bank at pulse time)")
    print("-" * 66)
    print(f"{'plan':11} {'E1x3':>7} {'E2':>7} {'delta':>7}")
    for plan in PLANS:
        per_act = arms[plan]["pulses"]
        now = per_act.get(0, {}).get("mean_charge")
        ref = E1_X3[plan]["charge_a0"]
        if now is None:
            print(f"{plan:11} {ref:7.1f} {'--':>7}   (no act-1 pulses)")
            continue
        print(f"{plan:11} {ref:7.1f} {now:7.1f} {now - ref:+7.1f}")

    print()
    for plan in PLANS:
        block = kurage_telemetry.format_block(arms[plan]["pulses"])
        if block:
            print(f"[{plan}]")
            print(block)
    print()
    for plan in PLANS:
        block = burst_telemetry.format_block(arms[plan]["burst"])
        if block:
            print(f"[{plan}]")
            print(block)

    print(f"\n({base.runs} runs/plan, {len(PLANS)} plans "
          f"in {time.perf_counter() - t0:.1f}s)")
    print(f"  {base.stamp()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
