"""`X9READ-S1` — Kokomi's charge reads per turn, a DESCRIPTIVE read. THE RUN.

THE REGISTRATION IS ELSEWHERE AND CAME FIRST:
`review/active/charge-reads-per-turn-registration-2026-08-13.md` §5, the slate
`X9READ-S1` (`X1`–`X7`, `W9` at §5.4), DRAFTED under R212(2) and committed
before any run, revised 2026-08-30 on the pair review's correction and
COUNTERSIGNED in the R233 batch. THE GRADER IS ALSO ELSEWHERE AND ALSO CAME
FIRST: `tier05/charge_telemetry.py`, landed with its unit tests in its own
commit before this run was taken (§5.5's order, §6's order).

This module PREDICTS NOTHING and GRADES NOTHING of its own. It runs the
registered cell, hands the fights' logs to the grader, and prints what the
grader returns.

THE CELL, as §4 registers it and R233 countersigns it:

  character   `kokomi` — the bank is hers.
  archetypes  `priest`, `commander`, `assist`, reported SEPARATELY (`R1`) and
              POOLED, since every §5.3 predicate is a pooled one.
  n           600 runs per archetype — 1,800 runs, three arms.
  seed        11, the cell's standing seed.
  the rest    the cell's standing values: hunter route, `assigned` policy,
              realistic loadout, all registered acts. This measurement moves
              no version and opens no window.
  ceiling     1 hour wall-clock, stop-and-report. A partial result is graded
              as partial and quotes the turns it actually covered.

WHAT IT MOVES: nothing. No constant, no drafter dial, no policy branch, no
engine rule. The one seam is an EMIT-ONLY observer.

THE OBSERVER SEAM, named because monkeypatching is a real cost:

  model._RunCtx._record_traces   the ONE place a fight's `state.log` and its
                                 `act_i` are both in scope. The log does not
                                 survive onto the `RunResult`, so anything not
                                 reduced there is unrecoverable. The wrapper
                                 returns exactly what the wrapped callable
                                 returned, so an observed run and an
                                 unobserved one are the same run.

`jobs` MUST BE 1. A `jobs > 1` batch runs in worker PROCESSES the patch never
reaches, and would return a correct `RunResult` list with an empty observation
set. `main` refuses anything else rather than printing a silent zero.

NOT A BALANCE READ (R213 B / R215 B, Guardrail-7). It grades no design and
cannot on its own fire a nerf; `W9` fires a CANDIDATE — a QUEUE row — and
nothing else.

Usage: python -m tier05.exp_x9read_s1 [--runs N] [--seed N] [--json PATH]
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter

from tier05 import cells, charge_telemetry as ct, expcli, model

#: §4's cell. Named here so the record's header and the registration cannot
#: disagree about what ran.
CELL = cells.CANONICAL.but(name="x9read-s1", character="kokomi",
                           archetype="priest", jobs=1)

#: §4: all three archetypes, reported separately, since exhaust rate and
#: reader density differ per plan.
ARCHETYPES = ("priest", "commander", "assist")

PACKET = "review/active/charge-reads-per-turn-registration-2026-08-13.md"


def _observe(cell) -> list[ct.ChargeTrace]:
    """Run `cell` with the one seam patched and return the fights' traces.

    Restores the patch in a `finally`, so a raised exception cannot leave the
    module edited for whatever runs next in the process.
    """
    traces: list[ct.ChargeTrace] = []
    real_record = model._RunCtx._record_traces

    def record_traces(self, state):
        traces.append(ct.trace(state.log, self.act_i))
        return real_record(self, state)

    model._RunCtx._record_traces = record_traces
    try:
        cell.run()
    finally:
        model._RunCtx._record_traces = real_record
    return traces


def _print_arm(label: str, m: dict) -> None:
    lv = m["levels"]
    print(label)
    print(f"    combats {m['combats']}   sampled player turns {m['turns']}   "
          f"turns opened {m['turns_opened']}   dropped {m['turns_dropped']}")
    print(f"    reads/turn       mean {lv['mean']:.3f}   p50 {lv['p50']:.2f}   "
          f"p90 {lv['p90']:.2f}   p99 {lv['p99']:.2f}   max {lv['max']}")
    print(f"    completed reads  {m['completed_reads']}   "
          + "   ".join(f"{k} {m['share'][k] * 100:5.2f}%"
                       for k in ct.READ_KINDS))
    print(f"    repeatable       {m['repeatable_share'] * 100:.2f}%   "
          f"turns with no pulse {m['turns_without_pulse']}")
    print(f"    attack plays     {m['attack_plays']}   double reads "
          f"{m['double_plays']} ({m['double_share'] * 100:.2f}%)")
    print(f"    turn number      1-5 mean {m['early_mean']:.3f} "
          f"(n={m['early_turns']})   6+ mean {m['late_mean']:.3f} "
          f"(n={m['late_turns']})   gap {m['gap']:+.3f}")
    print(f"    truncation       raw reads {m['raw_total']} vs completed-turn "
          f"{m['completed_reads']} -> {m['reads_dropped']} dropped")
    print(f"    bank at read     medians {m['bank_median']}")
    for act, row in m["by_act"].items():
        print(f"    act {int(act) + 1}            mean {row['mean']:.3f}   "
              f"1-5 {row['early_mean']:.3f}   6+ {row['late_mean']:.3f}   "
              f"n={row['turns']}")
    print()


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", type=int, default=CELL.runs)
    ap.add_argument("--seed", type=int, default=CELL.seed)
    ap.add_argument("--json", default=None, help="write the record here")
    args = ap.parse_args(argv)

    if CELL.jobs != 1:
        print("REFUSED: the observer seam lives in this process; jobs must "
              "be 1.", file=sys.stderr)
        return 2

    stamp = cells.world_stamp()
    print("X9READ-S1 — Kokomi's charge READS PER TURN, descriptive.")
    print(f"  REGISTRATION: {PACKET} §5 (slate §5.3, trigger §5.4), "
          "countersigned R233.")
    print("  GRADER: tier05/charge_telemetry.py, committed with its tests "
          "before this run.")
    print(f"  world stamp {stamp}   {args.runs} runs x {len(ARCHETYPES)} "
          f"archetypes, seed {args.seed}")
    print("  NOT A BALANCE READ (R213 B / R215 B). Counts only. The pilot "
          "does not play toward the double read, so X4 and X6 are FLOORS.")
    print("  §2.1: the killing turn contributes no sample, and the loss is "
          "toward the BUSY end. Every count is a floor; the SHARES are "
          "estimates with an unsigned error, not bounds.")
    print()

    record: dict = {"registration": "X9READ-S1", "packet": PACKET + " §5",
                    "stamp": stamp, "seed": args.seed,
                    "runs_per_archetype": args.runs,
                    "archetypes": list(ARCHETYPES), "arms": {}}

    t0 = time.time()
    all_traces: list[ct.ChargeTrace] = []
    for archetype in ARCHETYPES:
        cell = CELL.but(runs=args.runs, seed=args.seed, archetype=archetype,
                        name=CELL.name)
        started = time.time()
        traces = _observe(cell)
        arm = ct.aggregate(traces)
        arm["seconds"] = round(time.time() - started, 1)
        arm["cell"] = cell.describe()
        all_traces.extend(traces)
        _print_arm(f"{archetype} — RECORDED, graded by nothing (R1)", arm)
        record["arms"][archetype] = arm

    pooled = ct.aggregate(all_traces)
    pooled["seconds"] = round(time.time() - t0, 1)
    _print_arm("POOLED across the three archetypes — THE GRADED ARM", pooled)
    record["pooled"] = pooled

    grades = ct.grade(pooled)
    record["grades"] = grades
    print("THE SLATE, graded against §5.3's registered thresholds:")
    for row in grades:
        print(f"  {row['slot']}  {row['grade']:<10}  {row['read']}")
        print(f"      threshold: {row['threshold']}")
    tally = Counter(row["grade"] for row in grades)
    print()
    print("  " + " / ".join(f"{tally[k]} {k}" for k in
                            ("PREDICTED", "SPLIT", "MISS", "UNREACHED")))
    print()

    w9 = ct.evaluate_w9(pooled)
    record["w9"] = w9
    print("W9 — §5.4's watch trigger:")
    print(f"  Limb A  repeatable (garment + bonus_formula) "
          f"{w9['repeatable_share'] * 100:.2f}% of completed-turn reads   "
          f"> 50%? {'FIRES' if w9['limb_a'] else 'no'}   margin "
          f"{w9['limb_a_margin'] * 100:+.2f} pp")
    print(f"  Limb B  double read {w9['double_share'] * 100:.2f}% of attack "
          f"plays   > 50%? {'FIRES' if w9['limb_b'] else 'no'}   margin "
          f"{w9['limb_b_margin'] * 100:+.2f} pp")
    print(f"  severity indicator (gates nothing): p50 {w9['p50']:.2f} reads "
          f"per turn -> {w9['severity'].upper()}")
    print(f"  kurage_pulse share {w9['kurage_pulse_share'] * 100:.2f}%   "
          f"sampled turns carrying no pulse {w9['turns_without_pulse']}")
    print(f"  => W9 {'FIRES' if w9['fired'] else 'DOES NOT FIRE'}. "
          + ("A QUEUE row is minted; nothing else happens."
             if w9["fired"] else "The margins above are the record."))
    print()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=2, sort_keys=True)
        print(f"record written to {args.json}")
    return 0


if __name__ == "__main__":
    expcli.help_if_asked(__doc__)
    sys.exit(main())
