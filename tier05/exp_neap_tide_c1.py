"""C1 (Neap Tide addendum): the retrodiction. Was it visible before we looked?

R73 cut the pulse multiplier because the assistant's §2.2 reader-hierarchy
objection was right: a BASIC card's jellyfish out-read both rate-limited Rare
readers. That objection was argued from arithmetic. The question C1 asks is
whether the repo was already MEASURING it, in a column that was printed on
every Kokomi report and read by nobody.

It was. See the finding at the bottom.

WHAT THIS SCRIPT DOES. It runs today's world in the canonical cell and prints
it beside the archived pre-sprint table. It is not an A/B and must not be read
as one -- the baseline is CONSTANTS_VERSION 3 and today is 4, so the two
columns describe different worlds by construction and the archive discipline
says so plainly. The A/B was E1, which held everything but the multiplier
fixed. This is a reading of what the OLD instrument said in the OLD world,
which is the only thing a retrodiction can be.

REPRODUCING THE BASELINE COLUMN. The numbers below were taken by checking out
the true baseline into a worktree and running the same cell:

    git worktree add <path> c3e11b6
    cd <path> && PYTHONPATH=<path> python -m tier05.exp_neap_tide_c1 600

c3e11b6 ("Conscript recruits are combat-scoped") is the last commit before A1,
i.e. the world the sprint started from. Do NOT use the runner's bare default
loadout for this -- it is a different cell (no relics, no potions) and returns
0.0% win on all four plans, which is not the world any sprint number came from.

Usage: python -m tier05.exp_neap_tide_c1 [runs]
"""

from __future__ import annotations

import sys
import time

from tier05 import cells, kurage_telemetry

PLANS = ("priest", "commander", "assist", "generic")

# Archived: c3e11b6, cells.CANONICAL, seed 11, 600 runs/plan, jobs=1,
# stamp RT7/D10/P3/C3. {plan: (win%, act1%, {act: (p50, p95, max, chg, n)})}
BASELINE = {
    "priest": (11.5, 67.5, {
        1: (24, 64, 124, 6.2, 5562),
        2: (48, 112, 196, 12.1, 3594),
        3: (64, 136, 212, 15.7, 1419)}),
    "commander": (9.5, 70.8, {
        1: (20, 52, 108, 5.3, 5410),
        2: (40, 96, 176, 10.1, 3830),
        3: (52, 108, 172, 12.8, 1323)}),
    "assist": (2.0, 57.8, {
        1: (20, 48, 104, 4.7, 5590),
        2: (32, 80, 168, 7.9, 3219),
        3: (40, 92, 140, 10.2, 499)}),
    "generic": (9.2, 64.2, {
        1: (20, 48, 104, 4.7, 5783),
        2: (32, 84, 228, 8.5, 4234),
        3: (44, 104, 240, 11.5, 1517)}),
}

# What the pulse was supposed to sit UNDER. nereids_ascension is a Rare, 2-cost,
# Exhaust, all-enemies attack: 12 flat + 1 per 2 Charge. Every rate limit §2.2
# has, on one card. The pulse has none of them -- it is a Basic, and it fires at
# every turn end for free.
def nereids_read(charge: float) -> float:
    return 12 + charge / 2


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    base = cells.CANONICAL.but(character="kokomi", archetype="priest", jobs=1)
    if argv:
        base = base.but(runs=int(argv[0]))

    print("C1 -- retrodiction: today's world beside the archived baseline")
    print(f"  today    {base.stamp()}")
    print("  baseline c3e11b6, same cell, seed 11, RT7/D10/P3/C3")
    print("  NOT an A/B. Different CONSTANTS_VERSION; see the docstring.")
    print()

    t0 = time.perf_counter()
    for plan in PLANS:
        arm = base.but(archetype=plan).arm()
        per_act = kurage_telemetry.by_act(
            [pair for r in arm["results"] for pair in r.kurage_traces])
        b_win, b_act1, b_acts = BASELINE[plan]
        print(f"{plan}")
        print(f"  win   {b_win:5.1f} -> {arm['win']*100:5.1f}     "
              f"act1  {b_act1:5.1f} -> {arm['act1']*100:5.1f}")
        print(f"  {'act':>5} {'p95 base':>9} {'p95 now':>8} "
              f"{'max base':>9} {'max now':>8} {'chg base':>9} {'chg now':>8} "
              f"{'nereid base':>12}")
        for act in sorted(set(b_acts) | {a + 1 for a in per_act}):
            b = b_acts.get(act)
            n = per_act.get(act - 1)
            print(f"  {act:>5} "
                  f"{(b[1] if b else 0):9.0f} {(n['p95'] if n else 0):8.0f} "
                  f"{(b[2] if b else 0):9.0f} {(n['max'] if n else 0):8.0f} "
                  f"{(b[3] if b else 0):9.1f} "
                  f"{(n['mean_charge'] if n else 0):8.1f} "
                  f"{(nereids_read(b[3]) if b else 0):12.1f}")
        print()

    print(f"({base.runs} runs/plan in {time.perf_counter() - t0:.1f}s)")
    print(FINDING)
    return 0


FINDING = """
THE FINDING (C1, 2026-07-26). YES -- and in the row nobody was told to read.

R56's standing caveat was "Osty's HP can drop, Charge cannot, so watch ACT 3",
and kurage_telemetry was built to serve exactly that sentence. It did. The act-3
column was printed on every Kokomi report from the day it existed, it answered
the question it was asked, and the answer was "no runaway": act-3 p95 is about
2.1x act-1 p95 at baseline (priest 136 vs 64), and about the same ratio today
(121 vs 46). R73 lowered the whole curve and did not flatten it, because the
curve was never the problem.

The problem was the LEVEL, and it was in the act-1 row.

At baseline, priest act 1: p95 64, max 124, mean bank 6.2. The card the §2.2
hierarchy says should sit ABOVE the pulse -- nereids_ascension, Rare, 2-cost,
Exhaust, one cast -- reads 15.1 at that bank. So at the 95th percentile a BASIC
card's free turn-end pulse was hitting FOUR TIMES the rate-limited Rare, in
act 1, from the opening deck, and act-1 elites are 75-140 HP.

Three reasons it stayed unread, all fixable and none about anyone's attention:

  1. The telemetry printed the pulse and never printed what it was supposed to
     sit under. A tail is only large RELATIVE to something, and the something
     lived in a design document. This script prints the nereids read next to
     the pulse for that reason.
  2. "Watch act 3" pointed at the thinnest sample in the table. Baseline priest
     threw 10,575 pulses: 53% in act 1, 13% in act 3. The instructed column had
     an eighth of the evidence and the ignored column had half.
  3. Both readings were true. Act 3 does not run away; the ratio really is
     flat. A correct answer to the asked question read as an all-clear for the
     unasked one.

WHAT THIS CHANGES GOING FORWARD. A "watch X" caveat should name the comparator,
not just the cell -- "watch act 3" produced an instrument that could not be
wrong and could not be informative. The A1b WATCH block in tier0/constants.py is
written that way on purpose: it carries a worked example against the Rare
readers, and test_pulse_multiplier_claims checks the arithmetic still holds.
"""


if __name__ == "__main__":
    raise SystemExit(main())
