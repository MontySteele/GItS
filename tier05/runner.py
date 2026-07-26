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
from tier0 import roster
from tier0.content import loader
from tier05 import (ab, draft, elite_blitz, kurage_telemetry, model,
                    overlap_telemetry, route, run_metrics)

# `cells` is imported inside main(), not here. R68 put resolve_plan in this
# module and made it the single source of truth for plan->pilot, so cells.py
# has to reach back for it -- and cells validates its CANONICAL literal at
# import time, which would land in a half-built runner if the dependency ran
# both ways at module scope. The one-way module-level edge is cells -> runner;
# this is the return trip, deferred to call time.

# The run model itself is character-agnostic; this is the CLI's honest list of
# plans with authored draft tags + combat pilots. Keeping it character-scoped
# prevents a syntactically valid but meaningless pairing such as
# ``furina/demolition`` or ``klee/spotlight``.
#
# F1: the ROSTER half is DERIVED from tier0/roster.py rather than repeated
# here. The reference anchors keep their literals -- they are deliberately not
# roster members (no art, no pool, no C# class; see roster.REFERENCE_IDS) and
# folding them in would make every roster sweep either wrong or full of
# exceptions. A character added to the registry appears here with no edit,
# which is the whole point: this was one of the ~26 sites where forgetting was
# silent, and `runner.resolve_plan` is the R68 single source of truth for
# plan->pilot that everything else asks.
CHARACTER_PLANS: dict[str, dict[str, str]] = {
    c.id: dict(c.plans) for c in roster.ROSTER
}
CHARACTER_PLANS.update({
    "ref_ironclad": {"generic": "generic"},
    "real_ironclad": {"generic": "generic"},
})

DEFAULT_PLAN = {
    **{c.id: c.default_plan for c in roster.ROSTER},
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
    from tier05 import cells        # see the import note at module top

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
    ap.add_argument("--route", default="hunter",
                    choices=sorted(route.POLICIES),
                    help="§11 route policy: 'hunter' seeks elites for their "
                         "relics (the realistic default), 'cautious' routes "
                         "around them")
    ap.add_argument("--route-ab", action="store_true",
                    help="§11 A/B: hunter vs cautious over the same seeds. "
                         "Pathing is the second policy confounder -- a "
                         "finding that flips between these arms is a finding "
                         "about ROUTING, not about the character")
    ap.add_argument(
        "--realistic", action="store_true",
        help="enable the realistic run power budget: relic granting and "
             "potion drops/shop/use (default preserves the historical bare "
             "run world)",
    )
    ap.add_argument(
        "--jobs", "-j", type=int, default=1,
        help="worker PROCESSES to spread the runs over (0 = one per CPU). "
             "Wall-clock only: run i is a pure function of seed+i, so the "
             "results are identical at any job count.")
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

    if args.route_ab:
        t0 = time.perf_counter()
        out = ab.run_route_ab(args.character, archetype, pilot, args.runs,
                              args.seed, policy_name=args.policy,
                              grant_relics=args.realistic,
                              grant_potions=args.realistic,
                              n_acts=args.acts, jobs=args.jobs)
        ab.print_route_ab(args.character, out)
        print(f"\n({2 * args.runs} runs in {time.perf_counter() - t0:.1f}s)")
        return 0

    if args.ab:
        t0 = time.perf_counter()
        result = ab.run_ab(args.character, archetype, pilot,
                           args.runs, args.seed,
                           grant_relics=args.realistic,
                           grant_potions=args.realistic,
                           n_acts=args.acts, jobs=args.jobs,
                           route_name=args.route)
        ab.print_ab_report(args.character, archetype, result)
        print(f"  loadout         "
              f"{'realistic (relics + potions)' if args.realistic else 'bare'}")
        print(f"\n({2 * args.runs} runs in {time.perf_counter() - t0:.1f}s)")
        return 0

    t0 = time.perf_counter()
    # R68: the CLI's own configuration is a Cell too, so the stamp on a
    # runner report and the stamp on an experiment report are produced by
    # one piece of code and cannot drift into two formats.
    cell = cells.Cell(
        name="cli", character=args.character, archetype=archetype,
        runs=args.runs, seed=args.seed, route=args.route,
        policy=args.policy, realistic=args.realistic, n_acts=args.acts,
        jobs=args.jobs)
    results = cell.run()
    summary = run_metrics.summarize_runs(results)
    max_hp = loader._character_index()[args.character]["hp"]
    survival = run_metrics.survival_profile(results, max_hp)
    run_metrics.print_run_report(
        args.character, archetype, summary,
        run_metrics.floor_kind_labels(results), survival,
        stamp=cell.stamp())
    print(f"  loadout         "
          f"{'realistic (relics + potions)' if args.realistic else 'bare'}")
    # P2 (playtest sprint): report-only. Prints nothing at all unless this
    # cohort actually fielded a Bake-Kurage, so it is silent for the rest of
    # the roster rather than a row of zeroes everyone learns to skip.
    pulses = kurage_telemetry.by_act(
        [pair for r in results for pair in r.kurage_traces])
    block = kurage_telemetry.format_block(pulses)
    if block:
        print(block)
    # C4 (Neap Tide addendum): the carry-card overlap watch. Same silence rule
    # -- prints nothing unless one of the watched cards was actually drafted.
    # It is on the DEFAULT report rather than behind a flag on purpose: the
    # pair that carried playtest two was invisible because nothing put it in
    # front of anyone, and an instrument you have to remember to ask for has
    # the same failure mode as no instrument.
    block = overlap_telemetry.format_block(
        overlap_telemetry.aggregate(results))
    if block:
        print(block)
    # C2 (Neap Tide addendum): the elite columns. Not character-gated -- every
    # roster meets elites, and "act-1 clear moved" is an elite question for all
    # of them. Silent only when the cohort never entered one.
    block = elite_blitz.format_block(elite_blitz.aggregate(results))
    if block:
        print(block)
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
