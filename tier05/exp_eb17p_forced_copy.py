"""EB-17p: the force-first-copy PAIRED winrate sweep.

MEASUREMENT ONLY. This script runs no design, moves no constant, and reads
nothing into its own output. It is the runner for the registration at
`review/records/eb17p-registration-draft-2026-08-08.md`, and every choice it
makes is a choice that packet already made -- the cell, the seeds, the arms,
the columns and the tests are all fixed there, not here.

WHAT IT DOES. One CONTROL arm and one TREATED arm per swept card, all on the
SAME seeds. A treated arm forces one copy of its card into the deck at the end
of run start (`model.run_one(force_cards=[...])`), which is late enough that
the two arms have consumed identical randomness when they enter floor 1: same
map, same relics, same gold, one card apart. That is what makes the pairing by
INDEX legitimate -- run i of every arm is a pure function of `seed + i`.

The control arm is run ONCE and reused as the paired partner for every card.
Re-running an identical control per card would burn budget reproducing the
same list of results.

THE FILLER IS NOT A CARD UNDER TEST. Every treated arm adds a card, so every
treated arm also DILUTES the deck by one. The filler arm forces a duplicate of
Klee's own basic Attack, whose value is understood and is not what the sweep
is about, so dilution is measured rather than confounded with the card. That
is why the report carries TWO deltas per card: against the control, and
against the filler.

INTENT-TO-TREAT, stated in the output and not just here. Assignment happens at
run start; the run may then upgrade the copy at a smith node or remove it at a
rest node, and a control run may draft the card on its own. Those runs stay in
their assigned arms. The compliance census is what tells a reader how much of
the contrast survived, and it is printed BEFORE the deltas for that reason.

RNG DISCIPLINE. The bootstrap is NEW sampling, so it runs on its own dedicated
stream with its own constant seed, unrelated to any seed the sim consumes --
the `exp_reactions_corpus` rule. It is constructed after every run has already
resolved and cannot perturb one.

Usage:

    PYTHONPATH=. python -m tier05.exp_eb17p_forced_copy --runs 2400 --jobs 0
    PYTHONPATH=. python -m tier05.exp_eb17p_forced_copy --smoke --runs 12

`--smoke` moves the sweep onto the seeds section 4 EXCLUDES by construction.
Use it for every "does it run" check. The bare form runs on the REGISTERED
seed base, and that is the sweep itself: it happens once, after the
predictions commit exists, and its output is not opened by the author of the
predictions.
"""

from __future__ import annotations

import random
import statistics
import sys
import time

from tier0.content import upgrades
from tier0.harness import metrics, report
from tier05 import cells, expcli, stats

# --- the registered configuration (§3, §4, §5) -----------------------------

#: §3's base cell: the ratified cell (R68) moved to klee/reaction, the plan
#: every swept card belongs to. Seed 11, route hunter, policy assigned,
#: realistic loadout, all registered acts.
BASE = cells.CANONICAL.but(character="klee", archetype="reaction",
                           name="eb17p")

#: §5's sweep, in the register's own order, plus the filler. The filler is
#: LAST because it is the baseline the rows above it are read against, and a
#: reader meets it after the rows that need it.
FILLER = "kaboom"
SWEPT = ("friendly_visit", "study_buddy", "borrowed_brilliance",
         "elemental_ecstasy", FILLER)

#: Its own stream, its own constant. Not derived from any run seed: a
#: bootstrap that shares a stream with the sim is a bootstrap that can move a
#: fight. One generator per ROW so each interval is independently
#: reproducible from the published number alone.
BOOTSTRAP_SEED = 17_000_000
BOOTSTRAP_RESAMPLES = 10_000


def _family(cid: str) -> tuple[str, str]:
    """A card id and its upgraded form.

    §5.2: a smith node rewrites the id IN PLACE, so every read here pools `X`
    with `X+`. A read keyed on the bare id would score an upgraded forced copy
    as an absent one -- which would look exactly like the copy being removed.
    """
    return cid, cid + upgrades.SUFFIX


def _holds(deck, cid: str) -> bool:
    return any(d in _family(cid) for d in deck)


def _count(deck, cid: str) -> int:
    fam = _family(cid)
    return sum(d in fam for d in deck)


# --- arms ------------------------------------------------------------------

def run_arms(runs: int, jobs: int) -> tuple[cells.Cell, dict]:
    """The control arm plus one treated arm per swept card.

    Returns the base cell (for the stamp) and `{arm_name: results}`, with
    `"control"` the untreated one. Every arm runs the same seeds in the same
    order, so `zip` is the pairing.
    """
    base = BASE.but(runs=runs, jobs=jobs, name="eb17p")
    arms: dict[str, list] = {}
    t0 = time.time()
    control = base.but(name="eb17p-control")
    print(f"  running control ({runs} runs) ...", flush=True)
    arms["control"] = control.run()
    print(f"    {time.time() - t0:.0f}s", flush=True)
    for cid in SWEPT:
        t = time.time()
        print(f"  running forced({cid}) ({runs} runs) ...", flush=True)
        arms[cid] = base.but(name=f"eb17p-forced-{cid}",
                             force_cards=(cid,)).run()
        print(f"    {time.time() - t:.0f}s", flush=True)
    return base, arms


# --- §6.1 the primary contrast ---------------------------------------------

def paired_binary(treated: list, control: list, rng) -> dict:
    """§6.1's row: a paired winrate delta with the counts that make it
    checkable, and both of the registered readings of it."""
    pairs = [(t.won, k.won) for t, k in zip(treated, control)]
    b, c, both, neither = stats.discordant_counts(pairs)
    n = len(pairs)
    wt = sum(t.won for t in treated)
    wk = sum(k.won for k in control)
    lo, hi = stats.paired_bootstrap_delta(pairs, rng,
                                          resamples=BOOTSTRAP_RESAMPLES)
    return {
        "n": n,
        "win_treated": wt / n if n else 0.0,
        "win_control": wk / n if n else 0.0,
        "delta": (wt - wk) / n if n else 0.0,
        "b": b, "c": c, "both": both, "neither": neither,
        "p_mcnemar": stats.mcnemar_exact(b, c),
        "ci": (lo, hi),
        # Printed for continuity with every other roster table, and
        # explicitly NOT the test -- these ignore the pairing the whole
        # design was bought to get.
        "wilson_treated": stats.wilson95(wt, n),
        "wilson_control": stats.wilson95(wk, n),
    }


def paired_numeric(treated: list, control: list, get, rng) -> dict:
    """§6.2's shape: the same pairing on a real-valued run outcome. No
    McNemar -- that test is for a binary outcome and does not apply here."""
    pairs = [(get(t), get(k)) for t, k in zip(treated, control)]
    n = len(pairs)
    lo, hi = stats.paired_bootstrap_delta(pairs, rng, resamples=2000)
    return {
        "n": n,
        "treated": statistics.mean(t for t, _ in pairs) if n else 0.0,
        "control": statistics.mean(k for _, k in pairs) if n else 0.0,
        "delta": statistics.mean(t - k for t, k in pairs) if n else 0.0,
        "ci": (lo, hi),
    }


# --- §6.3 compliance and contamination -------------------------------------

def compliance(treated: list, control: list, cid: str) -> dict:
    """Q3: did the assignment survive the run, and how contaminated is the
    control?

    Printed BEFORE the deltas, because it is what says whether a delta is
    even about the thing it claims to be about. A control arm that drafts the
    card on its own attenuates the ITT contrast by construction, and the
    packet says so before the number exists.

    HONEST LIMIT, stated in the column names: when a treated run holds two
    copies of the family, nothing distinguishes the forced one from a drafted
    one. These are counts of the FAMILY, not of the assigned copy.
    """
    n = len(treated) or 1
    fam = _family(cid)
    removed = sum(any(action == "remove" and target in fam
                      for _, action, target in t.rests) for t in treated)
    smithed = sum(any(action == "upgrade" and target in fam
                      for _, action, target in t.rests) for t in treated)
    return {
        "held_at_end": sum(_holds(t.deck_ids, cid) for t in treated) / n,
        "upgraded_at_end": sum(cid + upgrades.SUFFIX in t.deck_ids
                               for t in treated) / n,
        "rest_removed": removed / n,
        "rest_smithed": smithed / n,
        "mean_copies_treated": statistics.mean(
            _count(t.deck_ids, cid) for t in treated) if treated else 0.0,
        # The contamination bound: how often the control got there by itself.
        "natural_acquisition_control": (
            sum(_holds(k.deck_ids, cid) for k in control) / (len(control) or 1)),
    }


# --- §6.4 the pre-registered secondary subgroup -----------------------------

def clean_subgroup(treated: list, control: list, cid: str, rng) -> dict:
    """Δ restricted to pairs whose CONTROL run never acquired the family.

    SECONDARY, and it may not be promoted to primary after the read. A delta
    that appears only here is a hypothesis for a new registration, not a
    finding -- which is why it is reported with its own `n` and under its own
    heading rather than folded into the primary row.
    """
    keep = [(t, k) for t, k in zip(treated, control)
            if not _holds(k.deck_ids, cid)]
    if not keep:
        return {"n": 0}
    return paired_binary([t for t, _ in keep], [k for _, k in keep], rng)


# --- printing --------------------------------------------------------------

def _pp(x: float) -> str:
    return f"{100.0 * x:+.2f}pp"


def _pct(x: float) -> str:
    return f"{100.0 * x:.2f}%"


def print_primary(cid: str, row: dict, label: str) -> None:
    lo, hi = row["ci"]
    print(f"  {label:<22} delta {_pp(row['delta'])}  "
          f"[{_pp(lo)}, {_pp(hi)}]  "
          f"McNemar b={row['b']} c={row['c']} p={row['p_mcnemar']:.4f}")
    print(f"    {'':<20} arms {_pct(row['win_treated'])} vs "
          f"{_pct(row['win_control'])}  "
          f"concordant both={row['both']} neither={row['neither']}  "
          f"n={row['n']}")


def print_card(cid: str, res: dict) -> None:
    print("-" * 78)
    print(f"CARD {cid}")
    comp = res["compliance"]
    print(f"  compliance  forced copy family held at end "
          f"{_pct(comp['held_at_end'])}, upgraded "
          f"{_pct(comp['upgraded_at_end'])}, removed at rest "
          f"{_pct(comp['rest_removed'])}, smithed at rest "
          f"{_pct(comp['rest_smithed'])}")
    print(f"              mean family copies in the treated final deck "
          f"{comp['mean_copies_treated']:.2f}")
    print(f"  contamination  control arm acquired the family on its own in "
          f"{_pct(comp['natural_acquisition_control'])} of runs")
    print("  -- 6.1 primary: forced vs control (paired by seed) --")
    print_primary(cid, res["vs_control"], "vs control")
    if res["vs_filler"] is not None:
        print("  -- 6.1b co-primary: forced vs filler (paired by seed) --")
        print_primary(cid, res["vs_filler"], "vs filler")
    else:
        print("  -- 6.1b co-primary: this arm IS the filler --")
    print("  -- 6.2 secondary run-level (paired) --")
    for name, row in res["secondary"].items():
        lo, hi = row["ci"]
        print(f"    {name:<12} delta {row['delta']:+.4f} "
              f"[{lo:+.4f}, {hi:+.4f}]   "
              f"({row['treated']:.3f} vs {row['control']:.3f})")
    print("  -- 6.4 secondary subgroup: control never acquired the family --")
    sub = res["subgroup"]
    if sub["n"] == 0:
        print("    no such pairs (the control arm always acquired it)")
    else:
        print_primary(cid, sub, "clean pairs")
    print("  -- 6.5 card flow, forced arm, this family only --")
    flow = res["flow"]
    if not flow.get("by_card"):
        print("    the forced arm never drew or played the family")
    else:
        report.print_card_flow(f"forced({cid})", flow)
        # The FAMILY-POOLED line, printed because §5.2 requires every read to
        # pool `X` with `X+` and `card_flow_profile` keys by bare id -- so the
        # instrument hands back two rows where the registration asks one
        # question. Reconstructing the pooled rate by hand from two printed
        # rows is how a grade gets argued about instead of recorded.
        pooled = flow["pooled"]
        rate = ("n/a" if pooled["dead_in_hand_rate"] is None
                else _pct(pooled["dead_in_hand_rate"]))
        pwd = ("n/a" if pooled["played_when_drawn_rate"] is None
               else _pct(pooled["played_when_drawn_rate"]))
        print(f"    POOLED {cid} + {cid}+   draws {pooled['draws']}  "
              f"plays {pooled['plays']}  "
              f"played-when-drawn {pwd}  dead-in-hand {rate}")
    print("  -- 6.1 unpaired Wilson intervals (continuity ONLY, not the "
          "test) --")
    row = res["vs_control"]
    tlo, thi = row["wilson_treated"]
    klo, khi = row["wilson_control"]
    print(f"    treated {_pct(row['win_treated'])} "
          f"[{_pct(tlo)}, {_pct(thi)}]   "
          f"control {_pct(row['win_control'])} [{_pct(klo)}, {_pct(khi)}]")


def _flow_for(results: list, cid: str) -> dict:
    """`card_flow_profile` over the arm, cut down to the swept family.

    The instrument pools every card the cohort saw; the registered read is
    about one family, and printing 90 rows around it is how the row that
    matters gets scrolled away.

    A `pooled` block is added alongside `by_card`. `card_flow_profile` keys by
    BARE id, so a family that got smithed comes back as two rows -- and §5.2's
    rule is that every read pools `X` with `X+`, because a smith node rewrites
    the id in place and a read keyed on the bare id would score an upgraded
    forced copy as an absent one. The pooled block is that rule applied to the
    instrument's own output; it introduces no new measurement, only the
    addition §5.2 already requires. RATES are recomputed from the pooled
    counts rather than averaged from the two rows, because averaging two rates
    with different denominators is a different and wrong number.
    """
    flow = metrics.card_flow_profile(
        [s for r in results for s in r.fight_stats])
    if not flow:
        return {}
    fam = _family(cid)
    by_card = {k: v for k, v in flow["by_card"].items() if k in fam}
    draws = sum(r["draws"] for r in by_card.values())
    pooled = {
        "draws": draws,
        "plays": sum(r["plays"] for r in by_card.values()),
        "played_when_drawn": sum(r["played_when_drawn"]
                                 for r in by_card.values()),
        "dead_in_hand": sum(r["dead_in_hand"] for r in by_card.values()),
    }
    # None, not 0.0, on a family the arm never drew: an undefined rate is not
    # a zero rate, and a trigger that reads "at least 25% dead" must not fire
    # or clear on a card nobody ever saw.
    pooled["played_when_drawn_rate"] = (
        pooled["played_when_drawn"] / draws if draws else None)
    pooled["dead_in_hand_rate"] = (
        pooled["dead_in_hand"] / draws if draws else None)
    return dict(flow, by_card=by_card, pooled=pooled)


# --- main ------------------------------------------------------------------

def analyse(arms: dict) -> dict:
    """Every registered column, for every swept card.

    Each row gets its OWN bootstrap generator, seeded from the row's index off
    `BOOTSTRAP_SEED`, so an interval can be reproduced without re-running the
    sweep and no two rows share a stream.
    """
    control = arms["control"]
    filler = arms[FILLER]
    out = {}
    for i, cid in enumerate(SWEPT):
        treated = arms[cid]
        rng = random.Random(BOOTSTRAP_SEED + 1000 * i)
        out[cid] = {
            "vs_control": paired_binary(treated, control, rng),
            # §6.1b: the card against the deck-dilution baseline. BOTH arms
            # are treated here, so this contrast does NOT get the
            # byte-identical-run-start property the control comparison has --
            # the two arms diverge from floor 1. The pairing is still by
            # seed and still worth having; it is just a weaker pairing, and
            # the registration says so rather than letting the identical
            # machinery imply an identical guarantee.
            "vs_filler": (None if cid == FILLER
                          else paired_binary(treated, filler,
                                             random.Random(BOOTSTRAP_SEED
                                                           + 1000 * i + 500))),
            "secondary": {
                "act1": paired_numeric(treated, control,
                                       lambda r: float(r.acts_completed >= 1),
                                       rng),
                "acts": paired_numeric(treated, control,
                                       lambda r: float(r.acts_completed), rng),
                "decksize": paired_numeric(treated, control,
                                           lambda r: float(len(r.deck_ids)),
                                           rng),
                "fights": paired_numeric(treated, control,
                                         lambda r: float(len(r.fight_stats)),
                                         rng),
            },
            "compliance": compliance(treated, control, cid),
            "subgroup": clean_subgroup(treated, control, cid, rng),
            "flow": _flow_for(treated, cid),
        }
    return out


#: The THROWAWAY seed base. §4 of the registration excludes seeds
#: `424242 ...` from the registered range BY CONSTRUCTION, which is what makes
#: them safe to look at: a number read off them is outside the experiment and
#: can never be quoted into it.
SMOKE_SEED = 424242


def main(argv: list[str]) -> int:
    # --smoke moves the whole sweep onto the excluded seeds. It exists
    # because the registered base seed is 11 and the default `runs` is small
    # enough to make "just check it runs" cheap -- which is precisely how a
    # registered range gets read before the predictions are committed. Making
    # the safe path the flagged one, and the flag loud, is cheaper than
    # trusting everyone to type `--seed 424242`.
    smoke = "--smoke" in argv
    argv = [a for a in argv if a != "--smoke"]
    base, args = cells.parse_overrides(argv, BASE)
    if args:
        raise SystemExit(f"unexpected argument(s): {' '.join(args)}")
    if smoke:
        base = base.but(seed=SMOKE_SEED, name="eb17p-SMOKE")
        print("!" * 78)
        print("SMOKE RUN -- excluded seeds. NOT the registered sweep.")
        print("Nothing printed below may be quoted into the EB-17p report or "
              "its grade.")
        print("!" * 78)
    cells.print_header(
        base, "EB-17p -- force-first-copy PAIRED winrate",
        subject="klee/reaction, forced first copy vs control",
        varying=())
    print("  ARMS: 1 control + "
          f"{len(SWEPT)} treated ({', '.join(SWEPT)}), same seeds, "
          f"{base.runs} runs each")
    print("  ESTIMAND: intent-to-treat. A forced copy may be upgraded or "
          "removed by the run;")
    print("            a control run may draft the card by itself. Both stay "
          "in their arms.")
    print(f"  FILLER ARM: {FILLER}, Klee's own basic Attack -- the "
          "deck-dilution baseline.")
    print("  The bootstrap runs on its own stream "
          f"(seed {BOOTSTRAP_SEED}), never a run seed.")
    _, arms = run_arms(base.runs, base.jobs)
    results = analyse(arms)
    for cid in SWEPT:
        print_card(cid, results[cid])
    print("=" * 78)
    print("Numbers only. No threshold is applied here and no card is graded "
          "here: the")
    print("grade is a blind comparison against the registration's committed "
          "section 8 table.")
    return 0


if __name__ == "__main__":       # pragma: no cover
    expcli.help_if_asked(__doc__)
    sys.exit(main(sys.argv[1:]))
