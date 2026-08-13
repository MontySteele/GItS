"""The REGRET DISTRIBUTION PRINTER -- BACKLOG `EB-72` leg (1), QUEUE `M13`.

    python tools/regret_distribution.py --character klee --archetype demolition
    python tools/regret_distribution.py --runs 200 --seed 42 --jobs 0
    python tools/regret_distribution.py --runs 200 --json out.json
    python tools/regret_distribution.py --runs 200 --draft-sample 1.0

WHAT THIS IS FOR. `M13` asks where `ROUTE_REGRET_MARGIN` and its drafter twin
(`draft.DRAFT_REGRET_MARGIN`, the `+ 1.0`) came from. Nowhere: both are
literals with no recorded derivation, and R164 (2026-08-10) ruled that the
measurement gets PRE-REGISTERED and that `+1.0` is NOT ratified in the
meantime. A pre-registration needs something to pre-register against, and
until this file there was nothing:

  * `run_metrics.pooled_route_regret` emits NO percentiles, on purpose and
    correctly -- p50/p90 are not recoverable from per-act summaries, and a
    median of medians is a number that looks like a distribution read and is
    not one. It says in its own docstring that a caller wanting the pooled
    distribution should sample the gaps itself.
  * `print_run_report` prints the drafter's regret COUNT and no route-regret
    block at all, so the route sampler's output reaches no human surface.
  * `draft_regret` returns an integer. The magnitudes it thresholded were
    computed and thrown away.

So this prints the pooled gap distributions, both of them, MARGIN-FREE.

WHAT MARGIN-FREE MEANS HERE, precisely. The gap sample is collected without
consulting any threshold -- `run_metrics.route_regret_gaps` and
`draft.draft_regret_gaps` are the collection loops and neither takes a margin
argument. Every number in the DISTRIBUTION blocks below is therefore a fact
about the drafter and the route policy alone. The margin appears exactly once
per block, on the line labelled `in-tree literal`, which reports what the
current 1.0 would count and labels it as unratified. Nothing else on the page
depends on it.

WHAT THIS FILE DOES NOT DO. It proposes no margin, no band, no acceptance
target and no percentile as "the" percentile. Every ladder rung is printed at
equal weight for that reason. Which number (if any) becomes a threshold is a
[USER] act at `M13`, downstream of the registration draft that accompanies
this tool (`review/active/regret-margin-registration-2026-08-12.md`), and that
draft states the circularity hazard in reading a threshold off this output.

READING THE OUTPUT -- the one trap. Two denominators are printed and they are
not interchangeable:

  * ALL SAMPLED -- every sampled decision, zeros included. A decision the
    policy got right in hindsight contributes a 0.0. This is the honest
    denominator for "how much regret does this pipeline carry".
  * NON-ZERO -- the same sample conditioned on being positive. Useful for
    seeing the shape of the tail, and a percentile read off it is a percentile
    of the regrets rather than of the decisions. The two are labelled and
    never merged.

The route distribution is heavily zero-inflated by construction (in the
DECIDING state the sampler reads exactly zero -- the planner took the argmax
over those very path values -- so only the hindsight shift can produce a
positive), which is why the split matters more here than it looks.

UNITS ARE NOT SHARED. A route gap is a difference of PATH values -- a sum of
room `want`s over sixteen floors. A draft gap is a difference of CARD scores
-- one card's worth of printed damage/Block. The two blocks are printed on one
page because `M13` names both numbers; a point in one is not a point in the
other, and the tool never combines them.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tier0 import constants as C                            # noqa: E402
from tier0.content import loader                            # noqa: E402
from tier05 import cells, draft, run_metrics, stats          # noqa: E402

#: The percentile ladder, printed at equal weight. Deliberately a LADDER and
#: not a shortlist: printing three candidate cut points would be a proposal
#: wearing a report's clothes, and the choice of cut point is [USER]'s.
LADDER = (0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99)

#: The rng offsets `model._run_range` uses for the two samplers. Quoted here
#: rather than re-derived so this tool re-prices EXACTLY the sample the live
#: run priced -- the `cross-check` line below is what proves it did.
#: (The offset registry itself lives in `understudy/rng.py`.)
DRAFT_STREAM_OFFSET = 10 ** 9
ROUTE_STREAM_OFFSET = 5 * 10 ** 9


# ------------------------------------------------------------- collection ---

def route_gaps(results: list) -> dict:
    """Pool `route_regret_gaps` over every act of every run.

    Re-prices on the SAME dedicated stream the live run used, one fresh
    `Random` per act, because that is what `model._run_range` does -- and then
    checks its own arithmetic against the summaries the run already carries.
    A mismatch means this tool and the live sampler have drifted apart, which
    would make every number below a description of a pipeline nobody runs.
    """
    gaps: list[float] = []
    forced = decisions = acts = mismatches = 0
    for r in results:
        walks = [w for w in r.route_decisions if w["hindsight"] is not None]
        for w, live in zip(walks, r.route_regret):
            g, f = run_metrics.route_regret_gaps(
                random.Random(r.seed + ROUTE_STREAM_OFFSET), w["map"],
                w["decisions"], w["hindsight"], r.route)
            gaps.extend(g)
            forced += f
            decisions += len(w["decisions"])
            acts += 1
            # The live summary is a reduction of this same sample. Compare the
            # reduction, not the sample -- the sample is not stored on the run.
            if (live["sampled"], live["forced"],
                    live["max_regret"]) != (len(g), f,
                                            max(g) if g else 0.0):
                mismatches += 1
    return {"gaps": gaps, "forced": forced, "decisions": decisions,
            "acts": acts, "mismatches": mismatches,
            "sample_rate": C.ROUTE_REGRET_SAMPLE}


def draft_gaps(results: list, archetype: str,
               sample: float = C.DRAFT_REGRET_SAMPLE) -> dict:
    """Pool `draft_regret_gaps` over every reward screen of every run.

    Same construction, same self-check: the count of gaps over the in-tree
    margin has to reproduce `RunResult.regret_samples`, which the live run
    filled from `draft_regret` on this stream.

    THE SELF-CHECK ONLY HOLDS AT THE DEFAULT SAMPLE RATE. The drafter re-scores
    one screen in ten in-run; raising `sample` re-scores screens the run never
    priced, so the recomputed count is legitimately larger and the check is
    reported as `n/a` rather than as a failure. A raised rate buys a bigger
    sample off the same runs and costs nothing but wall clock -- it is a
    reading of finished runs on a dedicated stream, so no run moves.
    """
    gaps: list[float] = []
    screens = live_regrets = 0
    recomputed = 0
    for r in results:
        g = draft.draft_regret_gaps(
            random.Random(r.seed + DRAFT_STREAM_OFFSET), r.decisions,
            [loader.peek_card(cid) for cid in r.deck_ids], archetype,
            sample=sample)
        gaps.extend(g)
        screens += len(r.decisions)
        live_regrets += r.regret_samples
        recomputed += sum(1 for x in g if x > draft.DRAFT_REGRET_MARGIN)
    census = sample != C.DRAFT_REGRET_SAMPLE
    return {"gaps": gaps, "screens": screens, "live_regrets": live_regrets,
            "recomputed_regrets": recomputed,
            "mismatches": (None if census
                           else int(recomputed != live_regrets)),
            "sample_rate": sample}


# -------------------------------------------------------------- reduction ---

def describe(gaps: list[float], margin: float) -> dict:
    """The margin-free reduction, plus ONE margin-dependent line.

    `above_margin` is the only key here that reads `margin`, and it is
    reported so the page can say what the in-tree literal currently counts.
    Every other key is a fact about the sample alone.
    """
    nonzero = [g for g in gaps if g > 0.0]
    zero = sum(1 for g in gaps if g == 0.0)
    return {
        "n": len(gaps),
        "zero": zero,
        "zero_share": zero / len(gaps) if gaps else 0.0,
        # Route gaps are clamped at 0 and can never land here. Draft gaps can
        # (a skipped screen scores the pick at 0.0), and a negative is neither
        # a zero nor a regret, so it gets its own count rather than being
        # rounded into either.
        "negative": sum(1 for g in gaps if g < 0.0),
        "mean": sum(gaps) / len(gaps) if gaps else 0.0,
        "max": max(gaps) if gaps else 0.0,
        "min": min(gaps) if gaps else 0.0,
        "ladder": {q: stats.percentile(gaps, q) for q in LADDER},
        "nonzero": {
            "n": len(nonzero),
            "mean": sum(nonzero) / len(nonzero) if nonzero else 0.0,
            "ladder": {q: stats.percentile(nonzero, q) for q in LADDER},
        },
        "above_margin": sum(1 for g in gaps if g > margin),
        "above_margin_share": (sum(1 for g in gaps if g > margin) / len(gaps)
                               if gaps else 0.0),
        "margin": margin,
    }


# ---------------------------------------------------------------- printing ---

def _ladder_line(ladder: dict) -> str:
    return "  ".join(f"p{int(q * 100)} {v:.4f}" for q, v in ladder.items())


def print_block(title: str, unit: str, d: dict, accounting: str) -> None:
    print()
    print(title)
    print(f"  units          {unit}")
    print(f"  accounting     {accounting}")
    print("  ALL SAMPLED (margin-free; zeros are decisions, not absences)")
    print(f"    n {d['n']}   zero {d['zero']} ({d['zero_share']:.1%})   "
          f"negative {d['negative']}   "
          f"mean {d['mean']:.4f}   min {d['min']:.4f}   max {d['max']:.4f}")
    print(f"    {_ladder_line(d['ladder'])}")
    nz = d["nonzero"]
    print("  NON-ZERO ONLY (a DIFFERENT denominator -- percentiles here are")
    print("  percentiles of the regrets, not of the decisions)")
    print(f"    n {nz['n']}   mean {nz['mean']:.4f}")
    print(f"    {_ladder_line(nz['ladder'])}")
    print(f"  in-tree literal margin {d['margin']}: {d['above_margin']} of "
          f"{d['n']} sampled ({d['above_margin_share']:.2%}) would count as")
    print("  regretted. UNCALIBRATED, NOT RATIFIED (R164). Printed so the "
          "page says what")
    print("  the current code does; it derives nothing and blesses nothing.")


def report(cell: cells.Cell, route: dict, drafted: dict) -> None:
    cells.print_header(
        cell, "Regret distribution -- margin-free (EB-72, QUEUE M13)")
    print("  The two blocks below are the two numbers M13 names. Neither is a")
    print("  proposal. No threshold, band or acceptance target is stated here.")

    rd = describe(route["gaps"], run_metrics.ROUTE_REGRET_MARGIN)
    print_block(
        "ROUTE REGRET -- run_metrics.route_regret_gaps, pooled over acts",
        "path value (a sum of room `want`s over the act's floors)", rd,
        f"acts {route['acts']}   floors {route['decisions']}   "
        f"forced {route['forced']}   sampled {rd['n']}   "
        f"sample rate {route['sample_rate']}")
    print(f"  cross-check vs the live per-act summaries: "
          f"{route['mismatches']} mismatched of {route['acts']} acts")
    print("  NOTE: in the DECIDING state this sampler reads exactly zero by")
    print("  construction (the planner took the argmax over these very path")
    print("  values). Every positive above is the hindsight shift and nothing")
    print("  else, which is why the zero share is large and is not a defect.")

    dd = describe(drafted["gaps"], draft.DRAFT_REGRET_MARGIN)
    print_block(
        "DRAFT REGRET -- draft.draft_regret_gaps, pooled over reward screens",
        "card score (one card's worth of printed damage/Block)", dd,
        f"screens {drafted['screens']}   sampled {dd['n']}   "
        f"sample rate {drafted['sample_rate']}")
    if drafted["mismatches"] is None:
        print("  cross-check vs the live RunResult.regret_samples: n/a -- the "
              "sample rate was")
        print(f"  raised to {drafted['sample_rate']}, so screens the run never "
              "priced are in this sample.")
    else:
        print(f"  cross-check vs the live RunResult.regret_samples: "
              f"{drafted['recomputed_regrets']} recomputed against "
              f"{drafted['live_regrets']} recorded")
    print("  NOTE: a SKIPPED screen scores the pick at 0.0 by convention, so a")
    print("  screen where every offer re-scored negative gives a NEGATIVE gap.")
    print("  Not clamped -- see draft.draft_regret_gaps.")

    print()
    print("=" * 78)
    print("Descriptive only. Which percentile (if any) becomes a margin is a")
    print("[USER] call at QUEUE M13, and the registration draft states why")
    print("reading one off THIS page needs its pipeline named:")
    print("  review/active/regret-margin-registration-2026-08-12.md")
    print("=" * 78)


# -------------------------------------------------------------------- cli ---

def collect(cell: cells.Cell,
            draft_sample: float = C.DRAFT_REGRET_SAMPLE) -> dict:
    """Run the cell and reduce it to the two gap samples."""
    results = cell.run()
    return {"route": route_gaps(results),
            "draft": draft_gaps(results, cell.archetype, draft_sample)}


def _payload(cell: cells.Cell, data: dict) -> dict:
    """The JSON view. Carries the stamp: an unstamped number is not citable
    (R68), and a JSON file outlives the terminal it was printed in."""
    return {
        "stamp": cell.stamp(),
        "cell": {"name": cell.name, "character": cell.character,
                 "archetype": cell.archetype, "pilot": cell.pilot,
                 "runs": cell.runs, "seed": cell.seed, "route": cell.route,
                 "policy": cell.policy, "realistic": cell.realistic,
                 "n_acts": cell.n_acts},
        "versions": cell.versions,
        "route": {**{k: v for k, v in data["route"].items() if k != "gaps"},
                  "distribution": describe(data["route"]["gaps"],
                                           run_metrics.ROUTE_REGRET_MARGIN)},
        "draft": {**{k: v for k, v in data["draft"].items() if k != "gaps"},
                  "distribution": describe(data["draft"]["gaps"],
                                           draft.DRAFT_REGRET_MARGIN)},
    }


def _take(args: list[str], flag: str) -> str | None:
    if flag not in args:
        return None
    i = args.index(flag)
    if i + 1 >= len(args):
        raise SystemExit(f"{flag} needs a value")
    value = args[i + 1]
    del args[i:i + 2]
    return value


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "-h" in args or "--help" in args:
        print(__doc__)
        return 0
    out = _take(args, "--json")
    character = _take(args, "--character")
    archetype = _take(args, "--archetype")
    # The drafter's in-run rate is 0.10. Raising it here re-scores screens the
    # run never priced -- a bigger sample off the same runs, at the cost of
    # the `regret_samples` cross-check. See `draft_gaps`.
    draft_sample = float(_take(args, "--draft-sample")
                         or C.DRAFT_REGRET_SAMPLE)
    # The base is the ratified cell (R68), so a run of this tool with no
    # arguments describes a world someone else can reproduce. Character and
    # plan move together through `but()`, which validates the pair.
    base = cells.CANONICAL.but(name="regret-distribution")
    deltas = {}
    if character:
        deltas["character"] = character
    if archetype:
        deltas["archetype"] = archetype
    if deltas:
        base = base.but(**deltas)
    cell, rest = cells.parse_overrides(args, base)
    if rest:
        raise SystemExit(f"unexpected argument(s): {' '.join(rest)}")

    data = collect(cell, draft_sample)
    report(cell, data["route"], data["draft"])
    if out:
        Path(out).write_text(
            json.dumps(_payload(cell, data), indent=1,
                       default=lambda k: str(k)),
            encoding="utf-8")
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
