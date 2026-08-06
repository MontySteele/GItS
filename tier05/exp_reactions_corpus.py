"""Last Call, track H: the reactions measurement harvest.

MEASUREMENT ONLY. This script runs no design and moves no constant. It exists
to put three counts in front of a future reactions design session that has so
far had to argue from an audit sentence:

  1. reactions' SHARE of damage, decomposed amp / splash / dot (track D's
     instrument, `metrics.reaction_share` and `tier05.reaction_telemetry`);
  2. AURA-OP FREQUENCY -- how often an aura-applying verb resolves, and what
     actually puts auras on the board (track H's `metrics.aura_profile`);
  3. PAYOFF-OP TRIGGERS -- how often the conditional riders that cash a
     reaction in actually fire (track H's `metrics.payoff_profile`). The
     2026-07-26 audit asserts these are unused, at roughly zero triggers, and
     the claim had never had a count under it.

TWO SURFACES, deliberately kept apart because they answer different questions
and must never be pooled into one row:

  cohort   tier 0.5, 3-act, --realistic, DRAFTED decks. What a reaction share
           looks like in a real run, where the drafter decides how much
           reaction the deck even contains. Cut by act.
  battery  tier 0, the frozen 6-encounter battery on AUTHORED decks. What the
           same numbers look like when the deck composition is held fixed.
           Cut by encounter.

DENOMINATORS (O-1, ruled 2026-08-06). `n_fights` counts RECORDS -- one per
encounter attempt -- and `n_combats` counts the combats inside them. They
differ only on the tier 0 battery's two-stage `gauntlet`, where one attempt is
two combats. Every per-fight EVENT rate here divides by `n_combats`; the
pooled counts and the pooled share are ratios of sums and are the same either
way. The battery TSV published on 2026-08-05 predates this and divided by
records throughout -- see the erratum in docs/archive/reactions-corpus-2026-08-05.md.

CONFIDENCE INTERVALS. The pooled share is a ratio of sums, not a mean, so its
interval is a percentile BOOTSTRAP resampling FIGHTS (the independent unit --
runs within a cohort share a draft, fights within a run share a deck; the
fight-level bootstrap is therefore mildly anticonservative for the cohort
surface and is labelled as such rather than silently widened). The per-fight
MEAN share gets the ordinary normal-approximation interval, mean +- 1.96 SE.

The bootstrap is NEW SAMPLING, so per repo discipline it runs on its own
dedicated RNG stream: one generator per ROW, seeded `BOOTSTRAP_SEED + 1000 *
arm_index (+ cut)`, a constant unrelated to any seed the sim consumes. It is
constructed after every fight in the arm has already resolved, draws nothing
from `CombatState.rng`, and therefore cannot perturb a single fight; the
per-row seeding also makes each interval independently reproducible.

Usage:

    PYTHONPATH=. python -m tier05.exp_reactions_corpus --cohort --runs 2000
    PYTHONPATH=. python -m tier05.exp_reactions_corpus --battery --fights 500
"""

from __future__ import annotations

import argparse
import csv
import random
import statistics
import sys
import time

from tier0 import constants as C
from tier0 import roster
from tier0.content import loader
from tier0.harness import metrics
from tier0.harness.runner import run_battery
from tier05 import cells, reaction_telemetry

# Its own stream, its own constant. Not derived from any run seed: a bootstrap
# that shares a stream with the sim is a bootstrap that can move a fight.
BOOTSTRAP_SEED = 8_050_000
BOOTSTRAP_RESAMPLES = 2000

COHORT_SEED = 20260805
BATTERY_SEED = 20260805

# The cohort arms: every roster character x every archetype it has a plan for,
# plus the reference anchors as the roster-external contrast. Derived from
# tier0/roster.py rather than listed, per F1 -- a character added to the
# registry appears here with no edit to this file.
COHORT_ARMS: list[tuple[str, str]] = [
    (c.id, plan) for c in roster.ROSTER for plan in c.plans
    if plan != "generic"
] + [("ref_ironclad", "generic")]

# The battery arms: starter (the shared floor) plus each authored package.
# `loader.archetype_decks` is deck -> pilot, which is the tier 0 half of the
# same routing table.
def _battery_arms() -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    for c in roster.ROSTER:
        out.append((c.id, "starter", "generic"))
        for deck, pilot in loader.archetype_decks(c.id).items():
            out.append((c.id, deck, pilot))
    out.append(("ref_ironclad", "starter", "generic"))
    return out


ALL_PAYOFF_PREDICATES = (metrics.REACTION_PAYOFF_PREDICATES
                         + metrics.AURA_PAYOFF_PREDICATES)


def payoff_card_index() -> dict[str, list[str]]:
    """predicate -> the card ids that carry it, read off the live sheet.

    The corpus needs THREE states told apart, not two: a payoff predicate can
    be (a) on no card the cohort drafted, (b) on a card that was drafted and
    never played, or (c) played and evaluated. Trigger counts alone cannot
    distinguish (a) from (b), and those are different findings with different
    owners -- (a) is a draft-reach question, (b) is a pilot question. The
    `*_cards_drafted` columns supply the missing leg.
    """
    out: dict[str, list[str]] = {p: [] for p in ALL_PAYOFF_PREDICATES}
    for cid, card in loader._card_index().items():
        blob = str(card.effects)
        for pred in ALL_PAYOFF_PREDICATES:
            if pred in blob:
                out[pred].append(cid)
    return {k: sorted(v) for k, v in out.items()}


# --- interval helpers -----------------------------------------------------

def bootstrap_share_ci(fight_stats: list, seed: int,
                       resamples: int = BOOTSTRAP_RESAMPLES) -> tuple:
    """95% percentile bootstrap for the POOLED share, resampling fights.

    Returns (lo, hi). ('', '') on an empty or zero-damage battery -- an
    undefined interval is reported as no interval, never as [0, 0]. The
    resample carries the (numerator, denominator) PAIR per fight, which is
    what makes it a ratio bootstrap rather than a mean-of-shares bootstrap.

    numpy only because 2000 resamples of ~15k fights is 30M draws and the
    pure-Python loop takes minutes per row; the fallback below is the same
    estimator at fewer resamples, so a machine without numpy gets a wider but
    honest interval rather than a missing column. Either way this is its own
    dedicated stream (`seed` is BOOTSTRAP_SEED + arm index), consumes nothing
    the sim consumes, and runs after every fight has already been resolved.
    """
    num = [s.damage_from_reactions for s in fight_stats]
    den = [s.damage_all_ops for s in fight_stats]
    n = len(num)
    if not n or not sum(den):
        return ("", "")
    try:
        import numpy as np
    except ImportError:
        rng = random.Random(seed)
        resamples = min(resamples, 200)
        shares = []
        for _ in range(resamples):
            a = b = 0
            for _ in range(n):
                j = rng.randrange(n)
                a += num[j]
                b += den[j]
            shares.append(a / b if b else 0.0)
    else:
        rng = np.random.default_rng(seed)
        anum = np.asarray(num, dtype=np.int64)
        aden = np.asarray(den, dtype=np.int64)
        shares = []
        chunk = max(1, min(64, 2_000_000 // max(1, n)))
        done = 0
        while done < resamples:
            k = min(chunk, resamples - done)
            idx = rng.integers(0, n, size=(k, n))
            s_num = anum[idx].sum(axis=1)
            s_den = aden[idx].sum(axis=1)
            shares.extend((s_num / np.maximum(1, s_den)).tolist())
            done += k
    shares.sort()
    lo = shares[int(0.025 * len(shares))]
    hi = shares[min(len(shares) - 1, int(0.975 * len(shares)))]
    return (lo, hi)


def mean_share_ci(fight_stats: list) -> tuple:
    """Normal-approximation 95% CI on the PER-FIGHT MEAN share."""
    xs = [s.reaction_share for s in metrics.per_combat(fight_stats)]
    if len(xs) < 2:
        return ("", "")
    m = statistics.fmean(xs)
    se = statistics.stdev(xs) / (len(xs) ** 0.5)
    return (m - 1.96 * se, m + 1.96 * se)


# --- row assembly ---------------------------------------------------------

FIELDS = [
    "surface", "character", "archetype_or_deck", "pilot", "cut",
    "n_runs", "n_fights", "n_combats", "seed", "stamp",
    "damage_all_ops", "damage_from_reactions", "damage_from_base_ops",
    "share_pooled", "share_pooled_ci_lo", "share_pooled_ci_hi",
    "share_fight_mean", "share_fight_mean_ci_lo", "share_fight_mean_ci_hi",
    "amp", "splash", "dot",
    "reactions", "reactions_per_fight", "fights_with_any_reaction_damage",
    "aura_ops_total", "aura_ops_per_fight", "aura_ops_detail",
    "aura_applications", "aura_applications_per_fight",
    "aura_applications_by_source", "aura_applications_by_element",
    "auras_wasted", "reactions_by_name",
    "reaction_payoff_evaluated", "reaction_payoff_fired",
    "reaction_payoff_rate", "reaction_payoff_detail",
    "reaction_payoff_absent",
    "aura_payoff_evaluated", "aura_payoff_fired", "aura_payoff_rate",
    "aura_payoff_detail", "aura_payoff_absent",
    "payoff_cards_drafted",
]


def _kv(d: dict) -> str:
    return ";".join(f"{k}={v}" for k, v in sorted(d.items())) or "-"


def _row(surface, character, arch, pilot, cut, n_runs, fight_stats, seed,
         stamp, boot_seed, drafted: dict | None = None) -> dict:
    share = metrics.reaction_share(fight_stats)
    aura = metrics.aura_profile(fight_stats)
    pay = metrics.payoff_profile(fight_stats)
    lo, hi = bootstrap_share_ci(fight_stats, boot_seed)
    mlo, mhi = mean_share_ci(fight_stats)

    def _slice(key, prefix):
        sl = pay[key]
        return {
            f"{prefix}_evaluated": sl["evaluated"],
            f"{prefix}_fired": sl["fired"],
            f"{prefix}_rate": round(sl["rate"], 5),
            f"{prefix}_detail": ";".join(
                f"{p}={v['fired']}/{v['evaluated']}"
                for p, v in sl["predicates"].items()) or "-",
            f"{prefix}_absent": ",".join(sl["absent"]) or "-",
        }

    row = {
        "surface": surface, "character": character,
        "archetype_or_deck": arch, "pilot": pilot, "cut": cut,
        "n_runs": n_runs, "n_fights": share["fights"],
        "n_combats": share["combats"], "seed": seed,
        "stamp": stamp,
        "damage_all_ops": share["damage_all_ops"],
        "damage_from_reactions": share["damage_from_reactions"],
        "damage_from_base_ops": share["damage_from_base_ops"],
        "share_pooled": round(share["share"], 5),
        "share_pooled_ci_lo": round(lo, 5) if lo != "" else "",
        "share_pooled_ci_hi": round(hi, 5) if hi != "" else "",
        "share_fight_mean": round(share["share_by_fight_mean"], 5),
        "share_fight_mean_ci_lo": round(mlo, 5) if mlo != "" else "",
        "share_fight_mean_ci_hi": round(mhi, 5) if mhi != "" else "",
        "amp": share["amp"], "splash": share["splash"], "dot": share["dot"],
        "reactions": aura["reactions"],
        "reactions_per_fight": round(aura["reactions"]
                                     / max(1, share["combats"]), 4),
        "fights_with_any_reaction_damage":
            share["fights_with_any_reaction_damage"],
        "aura_ops_total": aura["aura_ops_total"],
        "aura_ops_per_fight": round(aura["aura_ops_per_fight"], 4),
        "aura_ops_detail": _kv(aura["aura_ops"]),
        "aura_applications": aura["applications"],
        "aura_applications_per_fight": round(aura["applications_per_fight"], 4),
        "aura_applications_by_source": _kv(aura["applications_by_source"]),
        "aura_applications_by_element": _kv(aura["applications_by_element"]),
        "auras_wasted": aura["auras_wasted"],
        "reactions_by_name": _kv(aura["reactions_by_name"]),
    }
    row.update(_slice("reaction_payoff", "reaction_payoff"))
    row.update(_slice("aura_payoff", "aura_payoff"))
    # Draft reach: runs whose DECK held a payoff-carrying card. Blank where
    # the question does not apply (the tier 0 battery authors its deck, so
    # "was it drafted" is not a question there), never 0 -- see payoff_card_index.
    row["payoff_cards_drafted"] = ("" if drafted is None
                                   else (_kv(drafted) if drafted else "none"))
    return row


# --- the two harvests -----------------------------------------------------

def harvest_cohort(runs: int, seed: int, jobs: int) -> list[dict]:
    rows: list[dict] = []
    payoff_cards = payoff_card_index()
    for i, (character, archetype) in enumerate(COHORT_ARMS):
        boot = BOOTSTRAP_SEED + 1000 * i
        cell = cells.Cell(name=f"trackH-{character}-{archetype}",
                          character=character, archetype=archetype,
                          runs=runs, seed=seed, realistic=True, jobs=jobs)
        t0 = time.perf_counter()
        results = cell.run()
        pilot = cell.pilot
        stamp = cell.stamp()
        every = [fs for r in results for fs in r.fight_stats]
        drafted: dict[str, int] = {}
        for r in results:
            held = set(r.deck_ids)
            for pred, cids in payoff_cards.items():
                for cid in cids:
                    if cid in held:
                        key = f"{pred}:{cid}"
                        drafted[key] = drafted.get(key, 0) + 1
        rows.append(_row("cohort", character, archetype, pilot, "all",
                         runs, every, seed, stamp, boot, drafted))
        # Act cut. reaction_telemetry owns the act alignment (it is the same
        # _fight_contexts rule elite_blitz uses); we reuse its contexts rather
        # than re-deriving them here, so one module owns "which act is this
        # fight in".
        by_act: dict[int, list] = {}
        for r in results:
            ctx = reaction_telemetry._fight_contexts(r)
            for (act, _kind), fs in zip(ctx, list(r.fight_stats)):
                by_act.setdefault(act, []).append(fs)
        for act in sorted(by_act):
            rows.append(_row("cohort", character, archetype, pilot,
                             f"act{act + 1}", runs, by_act[act], seed,
                             stamp, boot + act + 1))
        print(f"  {character}/{archetype:<10} {len(every):>6} fights  "
              f"{time.perf_counter() - t0:5.1f}s  {stamp}", file=sys.stderr)
    return rows


def harvest_battery(fights: int, seed: int) -> list[dict]:
    rows: list[dict] = []
    stamp = (f"tier0 battery frozen (M2)  fights/encounter={fights} "
             f"seed={seed}  D{C.DRAFTER_VERSION}/C{C.CONSTANTS_VERSION}")
    for i, (character, deck, pilot) in enumerate(_battery_arms()):
        boot = BOOTSTRAP_SEED + 500_000 + 1000 * i
        t0 = time.perf_counter()
        every: list = []
        for j, enc in enumerate(loader.encounter_ids()):
            stats = run_battery(character, deck, enc, pilot, fights, seed)
            every.extend(stats)
            rows.append(_row("battery", character, deck, pilot, enc,
                             "", stats, seed, stamp, boot + j + 1))
        rows.append(_row("battery", character, deck, pilot, "all", "",
                         every, seed, stamp, boot))
        print(f"  {character}/{deck:<22} {len(every):>6} fights  "
              f"{time.perf_counter() - t0:5.1f}s", file=sys.stderr)
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cohort", action="store_true")
    ap.add_argument("--battery", action="store_true")
    ap.add_argument("--runs", type=int, default=2000,
                    help="tier 0.5 runs per cohort arm")
    ap.add_argument("--fights", type=int, default=500,
                    help="tier 0 fights per encounter per battery arm")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--jobs", "-j", type=int, default=0)
    ap.add_argument("--tsv", default=None, help="write the rows to TSV")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    if not (args.cohort or args.battery):
        ap.error("choose --cohort and/or --battery")

    rows: list[dict] = []
    if args.cohort:
        print("cohort (tier 0.5, 3 acts, realistic):", file=sys.stderr)
        rows += harvest_cohort(args.runs, args.seed or COHORT_SEED, args.jobs)
    if args.battery:
        print("battery (tier 0, frozen 6 encounters):", file=sys.stderr)
        rows += harvest_battery(args.fights, args.seed or BATTERY_SEED)

    out = args.tsv
    if out:
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS, delimiter="\t")
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {len(rows)} rows to {out}", file=sys.stderr)
    else:
        w = csv.DictWriter(sys.stdout, fieldnames=FIELDS, delimiter="\t",
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
