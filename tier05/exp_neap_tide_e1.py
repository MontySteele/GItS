"""E1 (Neap Tide v2.1): the pulse multiplier, alone, on paired seeds.

R73 halves KURAGE_PULSE_PER_CHARGE, 4 -> 2. Section 5 of the sprint pins the
knob order -- A1 lands ALONE and is measured before anything else moves -- so
this script varies exactly one number and nothing else.

WHAT THE TWO ARMS ARE, stated because it is easy to misread:

    x4   NOT the archived C3 measurement. It is today's tree, today's drafter,
         today's routes, with the multiplier patched back to its old value.
    x2   the same, at the shipped value.

That is deliberate. An A/B against a number taken in an older world would
confound the knob with every other change since, which is the exact failure
the CONSTANTS_VERSION discipline exists to prevent. Both arms here are the
SAME world differing in one constant, which is the only comparison that
isolates the knob. Neither arm is comparable to a pre-C4 report.

Paired seeds: both arms run the same Cell seed, so a difference between them
is the multiplier and not sampling.

REPLICATING ON A SECOND SEED -- SEPARATE IT BY AT LEAST `runs`. `run_many`
seeds run i as `seed + i`, so at 600 runs, seed 11 and seed 23 share 588 of
their 600 runs. The first replication attempt used seed 23 and reproduced seed
11 to within 0.2pp on every cell, which reads as a beautifully stable result
and is actually a 98% overlapping sample. Seed 1011 is a real second draw:
it moved the per-plan deltas by up to 1.5pp while keeping every sign, which
is what an independent replication is supposed to look like.

WHY jobs IS FORCED TO 1. The arms are produced by patching a module attribute
on tier0.constants. Windows spawns worker processes rather than forking them,
and a spawned worker re-imports constants from source -- so the patch does NOT
apply in the workers, and the x4 arm quietly measures x2.

That is not hypothetical: the first run of this script pinned jobs=0 believing
it meant serial. It means ONE WORKER PER CPU (model.run_many), so it selected
maximum parallelism and produced two byte-identical arms -- the wrong number,
silently, which is the thing this instrument exists to avoid. The tell was
that the delta column was +0.0pp on all four plans AND the pulse tails matched
to the unit, which is not what a halved multiplier can look like.

`jobs=1` is the serial path. Slower and correct.

Usage: python -m tier05.exp_neap_tide_e1 [--runs N] [--seed N] [--route NAME]
"""

from __future__ import annotations

import sys
import time

from tier0 import constants as C
from tier05 import cells, kurage_telemetry

# Her four registered plans. All of them, not just the Kurage lane: the pulse
# is fed by the exhaust funnel, which every Kokomi deck runs, so "which plans
# actually notice" is part of what E1 is for rather than an assumption to
# bake in here.
PLANS = ("priest", "commander", "assist", "generic")

# (label, multiplier). Baseline first so the report reads old -> new.
#
# x3 is here because the sprint PRE-COMMITTED it as the single weak-side
# response, and a pre-committed fallback that only gets measured after the
# result is in is not pre-committed in any useful sense. Measuring all three
# in one invocation means the fallback is chosen against numbers from the
# same run as the numbers that triggered it.
ARMS = (("x4 (pre-R73)", 4), ("x3 (fallback)", 3), ("x2 (R73)", 2))


def _run_arm(cell: cells.Cell, multiplier: int) -> dict:
    """One arm, with the multiplier patched for the duration of the run."""
    previous = C.KURAGE_PULSE_PER_CHARGE
    C.KURAGE_PULSE_PER_CHARGE = multiplier
    try:
        arm = cell.arm()
    finally:
        C.KURAGE_PULSE_PER_CHARGE = previous
    arm["pulses"] = kurage_telemetry.by_act(
        [pair for r in arm["results"] for pair in r.kurage_traces])
    return arm


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    base = cells.CANONICAL.but(character="kokomi", archetype="priest")
    base, rest = cells.parse_overrides(argv, base)
    if rest:
        raise SystemExit(f"unexpected argument(s): {' '.join(rest)}")
    # See the module docstring. jobs=1 is SERIAL; jobs=0 would be one worker
    # per CPU and would lose the patch. Not negotiable via a flag, because
    # the flag would be a way to produce a wrong number quietly.
    base = base.but(jobs=1)

    cells.print_header(
        base, "E1 -- R73 pulse multiplier, alone (Neap Tide v2.1)",
        subject="kokomi, all four plans", varying=("archetype",))
    print("  arms: x4 (pre-R73) vs x2 (R73), SAME seeds, one constant apart.")
    print("  Both arms are today's world. Neither is comparable to a pre-C4 "
          "report.")

    t0 = time.perf_counter()
    table: dict[str, dict[str, dict]] = {}
    for plan in PLANS:
        cell = base.but(archetype=plan)
        table[plan] = {label: _run_arm(cell, mult) for label, mult in ARMS}

    print()
    print(f"{'plan':11} {'arm':14} {'win%':>6} {'act1%':>6} {'acts':>5} "
          f"{'deck':>5} {'fights':>6}")
    print("-" * 60)
    for plan in PLANS:
        for label, _ in ARMS:
            a = table[plan][label]
            print(f"{plan:11} {label:14} {a['win']*100:6.1f} "
                  f"{a['act1']*100:6.1f} {a['acts']:5.2f} "
                  f"{a['decksize']:5.1f} {a['fights']:6.2f}")
        # Every non-baseline arm gets its own delta line. With three arms a
        # single "delta" row would silently mean whichever pair the loop
        # happened to hold, which is how a fallback gets graded against the
        # wrong reference.
        base_win = table[plan][ARMS[0][0]]["win"]
        for label, _ in ARMS[1:]:
            d = (table[plan][label]["win"] - base_win) * 100
            print(f"{'':11} {'d vs x4: ' + label:14} {d:+6.1f}pp")
        print()

    # The tail is the thing R73 was aimed at, so it is reported next to the
    # win rates rather than in a separate pass. A win rate that barely moves
    # while p95 halves is the SUCCESS case, not a null result: the knob was
    # aimed at the shape of the damage curve, not at the outcome.
    print("Kurage pulse tail, by act (the term R73 actually edits)")
    print("-" * 60)
    for plan in PLANS:
        for label, _ in ARMS:
            per_act = table[plan][label]["pulses"]
            if not per_act:
                continue
            cells_txt = "  ".join(
                f"a{act}: p95 {d['p95']:.0f} max {d['max']:.0f} "
                f"chg {d['mean_charge']:.1f}"
                for act, d in sorted(per_act.items()))
            print(f"{plan:11} {label:14} {cells_txt}")
        print()

    print(f"({base.runs} runs/arm, {len(PLANS)} plans, {len(ARMS)} arms "
          f"in {time.perf_counter() - t0:.1f}s)")
    print(f"  {base.stamp()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
