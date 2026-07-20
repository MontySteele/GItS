"""Tier 0.5 CLI — same drill as Tier 0: single command, terminal summary,
optional CSV. Fast iteration loop > elegance.

Usage:
    python -m tier05.runner --character klee --archetype demolition \
        --runs 500 --seed 42
    python -m tier05.runner --character ref_ironclad --runs 500   # anchor
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from tier0 import constants as C
from tier05 import draft, model, run_metrics

ARCHETYPE_PILOTS = {"demolition": "demolition", "spark": "spark",
                    "reaction": "reaction", "generic": "generic"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Tier 0.5 draft-level simulator")
    ap.add_argument("--character", default="klee")
    ap.add_argument("--archetype", default="demolition",
                    choices=sorted(ARCHETYPE_PILOTS))
    ap.add_argument("--runs", type=int, default=200)
    ap.add_argument("--seed", type=int, default=C.DEFAULT_SEED)
    ap.add_argument("--csv", default=None)
    args = ap.parse_args(argv)

    archetype = args.archetype
    if args.character == "ref_ironclad":
        archetype = "generic"           # the anchor drafts power, not plans
    pilot = ARCHETYPE_PILOTS[archetype]

    t0 = time.perf_counter()
    results = model.run_many(args.character, archetype, pilot,
                             draft.assigned_policy, args.runs, args.seed)
    summary = run_metrics.summarize_runs(results)
    run_metrics.print_run_report(args.character, archetype, summary,
                                 results[0].node_kinds)
    print(f"\n({args.runs} runs in {time.perf_counter() - t0:.1f}s)")

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["seed", "won", "death_node", "deck_size",
                        "time_to_online", "final_hp"])
            for r in results:
                w.writerow([r.seed, r.won, r.death_node, len(r.deck_ids),
                            r.time_to_online,
                            r.hp_by_node[-1] if r.hp_by_node else 0])
        print(f"wrote {len(results)} rows to {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
