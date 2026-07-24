"""Tier 0.5 CLI — same drill as Tier 0: single command, terminal summary,
optional CSV. Fast iteration loop > elegance.

Usage:
    python -m tier05.runner --character klee --archetype demolition \
        --runs 500 --seed 42
    python -m tier05.runner --character furina --archetype salon \
        --realistic --runs 500 --seed 42
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

# The run model itself is character-agnostic; this is the CLI's honest list of
# plans with authored draft tags + combat pilots. Keeping it character-scoped
# prevents a syntactically valid but meaningless pairing such as
# ``furina/demolition`` or ``klee/spotlight``.
CHARACTER_PLANS = {
    "klee": {
        "generic": "generic",
        "demolition": "demolition",
        "spark": "spark",
        "reaction": "reaction",
    },
    "furina": {
        "salon": "salon",
        "spotlight": "spotlight",
        "fanfare": "fanfare",
    },
    "kokomi": {
        # v0.2 sheet pass (2026-07-24): plans mirror her tier0 archetype
        # pilots. Requires DRAFTER_VERSION >= 7 -- the v6 scorer read her
        # conscript/gain_charge/Sly verbs as literal zero.
        "generic": "generic",
        "commander": "commander",
        "priest": "priest",
        "assist": "assist",
    },
    "ref_ironclad": {"generic": "generic"},
    "real_ironclad": {"generic": "generic"},
}

DEFAULT_PLAN = {
    "klee": "demolition",
    "furina": "salon",
    "kokomi": "priest",
    "ref_ironclad": "generic",
    "real_ironclad": "generic",
}


def resolve_plan(character: str, archetype: str | None) -> tuple[str, str]:
    """Return the assigned-plan id and its combat pilot, or fail loudly."""
    if character not in CHARACTER_PLANS:
        raise ValueError(
            f"unsupported character {character!r}; choose one of "
            f"{', '.join(sorted(CHARACTER_PLANS))}")
    plan = archetype or DEFAULT_PLAN[character]
    pilots = CHARACTER_PLANS[character]
    if plan not in pilots:
        raise ValueError(
            f"character {character!r} has no archetype {plan!r}; choose one "
            f"of {', '.join(pilots)}")
    return plan, pilots[plan]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Tier 0.5 draft-level simulator")
    ap.add_argument("--character", default="klee",
                    choices=sorted(CHARACTER_PLANS))
    ap.add_argument("--archetype", default=None,
                    help="assigned plan; defaults by character (Klee: "
                         "demolition, Furina: salon, Ironclads: generic)")
    ap.add_argument("--runs", type=int, default=200)
    ap.add_argument("--seed", type=int, default=C.DEFAULT_SEED)
    ap.add_argument("--csv", default=None)
    ap.add_argument("--policy", default="assigned",
                    choices=sorted(draft.POLICIES))
    ap.add_argument("--ab", action="store_true",
                    help="M6 A/B: assigned vs adaptive over the same seeds")
    ap.add_argument(
        "--realistic", action="store_true",
        help="enable the realistic run power budget: relic granting and "
             "potion drops/shop/use (default preserves the historical bare "
             "run world)",
    )
    ap.add_argument(
        "--acts", type=int, default=None,
        help="acts the run spans (§10.1); default = every act registered in "
             "RUN_ACTS. --acts 1 is the supported single-act instrument.",
    )
    args = ap.parse_args(argv)

    try:
        archetype, pilot = resolve_plan(args.character, args.archetype)
    except ValueError as exc:
        ap.error(str(exc))

    if args.ab and args.character == "furina":
        ap.error(
            "--ab is not valid for Furina: the adaptive classifier currently "
            "recognizes only Klee's Demolition/Spark/Reaction shapes. Use "
            "assigned runs (omit --ab).")

    # The death-heatmap bar is a block glyph; a cp1252 console (Windows
    # default) raises UnicodeEncodeError the moment ANY node records a
    # death, which killed the report mid-table. Pre-existing, found
    # 2026-07-21 -- and a plausible reason the HP bands this module has
    # always printed were never actually read.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):       # non-reconfigurable stream
        pass

    if args.ab:
        t0 = time.perf_counter()
        result = ab.run_ab(args.character, archetype, pilot,
                           args.runs, args.seed,
                           grant_relics=args.realistic,
                           grant_potions=args.realistic,
                           n_acts=args.acts)
        ab.print_ab_report(args.character, archetype, result)
        print(f"  loadout         "
              f"{'realistic (relics + potions)' if args.realistic else 'bare'}")
        print(f"\n({2 * args.runs} runs in {time.perf_counter() - t0:.1f}s)")
        return 0

    t0 = time.perf_counter()
    results = model.run_many(args.character, archetype, pilot,
                             draft.POLICIES[args.policy], args.runs, args.seed,
                             grant_relics=args.realistic,
                             grant_potions=args.realistic,
                             n_acts=args.acts)
    summary = run_metrics.summarize_runs(results)
    max_hp = loader._character_index()[args.character]["hp"]
    survival = run_metrics.survival_profile(results, max_hp)
    run_metrics.print_run_report(args.character, archetype, summary,
                                 results[0].node_kinds, survival)
    print(f"  loadout         "
          f"{'realistic (relics + potions)' if args.realistic else 'bare'}")
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
