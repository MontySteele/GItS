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
from tier0.content import loader
from tier05 import ab, draft, model, run_metrics

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
    ap.add_argument("--policy", default="assigned",
                    choices=sorted(draft.POLICIES))
    ap.add_argument("--ab", action="store_true",
                    help="M6 A/B: assigned vs adaptive over the same seeds")
    args = ap.parse_args(argv)

    # The death-heatmap bar is a block glyph; a cp1252 console (Windows
    # default) raises UnicodeEncodeError the moment ANY node records a
    # death, which killed the report mid-table. Pre-existing, found
    # 2026-07-21 -- and a plausible reason the HP bands this module has
    # always printed were never actually read.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):       # non-reconfigurable stream
        pass

    archetype = args.archetype
    if args.character == "ref_ironclad":
        archetype = "generic"           # the anchor drafts power, not plans
    pilot = ARCHETYPE_PILOTS[archetype]

    if args.ab:
        t0 = time.perf_counter()
        result = ab.run_ab(args.character, archetype, pilot,
                           args.runs, args.seed)
        ab.print_ab_report(args.character, archetype, result)
        print(f"\n({2 * args.runs} runs in {time.perf_counter() - t0:.1f}s)")
        return 0

    t0 = time.perf_counter()
    results = model.run_many(args.character, archetype, pilot,
                             draft.POLICIES[args.policy], args.runs, args.seed)
    summary = run_metrics.summarize_runs(results)
    max_hp = loader._character_index()[args.character]["hp"]
    survival = run_metrics.survival_profile(results, max_hp)
    run_metrics.print_run_report(args.character, archetype, summary,
                                 results[0].node_kinds, survival)
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
