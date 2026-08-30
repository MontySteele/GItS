"""`KLEESPARK-S1` — the Klee Spark arm measured DRAFTED. THE INSTRUMENT.

THE REGISTRATION IS ELSEWHERE AND CAME FIRST:
`review/active/klee-sparks-2026-08-29.md` §17, committed before this file.
This module PREDICTS NOTHING. Every threshold it prints a grade against is
quoted from §17.4 as a literal below, so a reader can check the grade against
the registration without leaving the file, and so no threshold can drift after
a number is seen (R101b).

WHY IT IS A SIBLING AND NOT AN EDIT. `exp_klee_sparks_r1.py` and
`exp_klee_sparks_r2.py` are PUBLISHED instruments — the `KLEESPARK-R1` packet
quotes r1's output — so both stay byte-identical. This is their successor and
it asks a different question: r1 and r2 read a deck assembled BY ID, and R225
item 1 ruled that only a DRAFTED deck can answer whether the one-for-one draft
economy reaches its non-damage sinks.

WHAT IT MOVES: nothing. No constant, no drafter dial, no policy branch, no
engine rule. `SPARK_ALT_COST_ENABLED` is flipped at run time and restored in a
`finally`, and every observer below is EMIT-ONLY — each wrapper returns exactly
what the wrapped callable returned, so an observed run and an unobserved one
are the same run.

THE OBSERVER SEAMS, named because monkeypatching is a real cost:

  model.run_one            opens one run record. `_run_range` calls it as a
                           module global, so the patch is seen.
  model.run_fight          opens one fight record and reads the fight's peak
                           Spark bank off the returned `state.log` -- which
                           does NOT survive onto the RunResult, so this is the
                           only place it can be taken.
  model._RunCtx.mark_hindsight
                           called after EVERY resolved node, so it is the exact
                           per-floor deck snapshot §17.4 asks for: the deck as
                           floor F finished, reward screens and shop included.
  model.make_pilot         wraps the combat pilot so each decision leaves a
                           record of the bank and of what the hand could afford.

`jobs` MUST BE 1. A `jobs > 1` (or `jobs = 0`, which means one worker per CPU)
batch runs in worker PROCESSES that no patch above reaches, and would return a
correct RunResult list with an empty observation set. `main` refuses anything
else rather than printing a silent zero.

Usage: python -m tier05.exp_klee_sparks_s1 [--runs N] [--seed N]
                                           [--json PATH]
"""

from __future__ import annotations

import json
import statistics
import sys

from tier0 import constants as C
from tier0.content import loader
from tier05 import cells, expcli, model

# --- the arm, as §17.2 registered it ----------------------------------------

#: §17.2: the reachable NON-DAMAGE sinks under this arm's pool are the three
#: `EB-218` twins, all priced 2. Rummage is on the list because §16.4 named it
#: one, and it is UNREACHABLE BY DRAFT -- which is slot `S5`'s whole point.
NON_DAMAGE_SINKS = ("proto_powder_charge_spark",     # Set It Off
                    "proto_hold_the_line_spark",     # Dig In
                    "proto_smoke_and_sparks_spark",  # Powder Smoke
                    "proto_spark_priced_draw")       # Rummage -- no pool seam

#: §16.4's six DAMAGE sinks, unchanged so the two reads are comparable.
DAMAGE_SINKS = ("proto_kaboom_sink", "proto_spark_strike",
                "proto_spark_sweep", "proto_spark_double_tap",
                "proto_spark_blast", "proto_spark_finisher")

RUMMAGE = "proto_spark_priced_draw"

#: §17.2: `proto_true_spark_knight` is EXCLUDED on §12.2's published D4 grounds
#: and exactly as `KLEESPARK-W2` excluded it. Popping the SHIPPED key restores
#: the shipped Rare to the offer slot, so the tier's odds are untouched.
EXCLUDED_SUB_KEY = "true_spark_knight"

#: §17.2's cheapest non-damage price, and every affordability threshold below.
NON_DAMAGE_PRICE = 2

#: §17.4: the three floors the maker:sink ratio is read at.
RATIO_FLOORS = (5, 10, 15)

#: §17.3's cell. Named here so the record's header and the registration cannot
#: disagree about what ran.
CELL = cells.CANONICAL.but(name="kleespark-s1", character="klee",
                           archetype="demolition", jobs=1)


def _clear_caches() -> None:
    """Every memo a flag flip invalidates, in one place (r2's list verbatim).

    `_card_prototype` and `_substituted_card_index` both read
    `C.SPARK_ALT_COST_ENABLED`, and `rewards.character_pool` reads the
    substitution map through `loader.pool_substitutions`. Flipping the flag
    without clearing all three silently serves the other arm's cards.
    """
    from tier05 import rewards
    loader._card_prototype.cache_clear()
    loader._substituted_card_index.cache_clear()
    rewards.character_pool.cache_clear()


# --- deck reads (sheet-only, no play) ---------------------------------------

def _top_level_ops(cid: str) -> list[dict]:
    return list(loader.peek_card(cid).effects)


def _is_maker(cid: str) -> bool:
    """§17.2: a MAKER carries a top-level `gain_spark`."""
    return any(fx.get("op") == "gain_spark" for fx in _top_level_ops(cid))


def _is_sink(cid: str) -> bool:
    """§17.2: a SINK carries a top-level `spend_spark` (`spark_cost`'s rule)."""
    return any(fx.get("op") == "spend_spark" for fx in _top_level_ops(cid))


def _makers_sinks(deck: list[str]) -> tuple[int, int]:
    return (sum(_is_maker(cid) for cid in deck),
            sum(_is_sink(cid) for cid in deck))


def _ratio(deck: list[str]) -> float | None:
    """makers / sinks, or None when the deck holds no sink (§17.4: excluded)."""
    makers, sinks = _makers_sinks(deck)
    return None if sinks == 0 else makers / sinks


# --- the observer ------------------------------------------------------------

class _Observer:
    """One arm's records. EMIT-ONLY; see the module docstring."""

    def __init__(self) -> None:
        self.runs: list[dict] = []
        self._run: dict | None = None
        self._fight: dict | None = None

    # -- run ---------------------------------------------------------------
    def open_run(self) -> dict:
        self._run = {"floors": {}, "fights": []}
        self.runs.append(self._run)
        return self._run

    def note_floor(self, floor: int, deck: list[str]) -> None:
        if self._run is not None:
            self._run["floors"][floor] = list(deck)

    # -- fight -------------------------------------------------------------
    def open_fight(self) -> dict:
        self._fight = {"peak": 0, "turns": {}}
        if self._run is not None:
            self._run["fights"].append(self._fight)
        return self._fight

    def note_decision(self, turn: int, bank: int, nd: int, nd_playable: int,
                      any_: int, any_playable: int) -> None:
        if self._fight is None:
            return
        row = self._fight["turns"].setdefault(
            turn, {"nd": 0, "nd_playable": 0, "any": 0, "any_playable": 0,
                   "bank_max": 0})
        row["nd"] = max(row["nd"], nd)
        row["nd_playable"] = max(row["nd_playable"], nd_playable)
        row["any"] = max(row["any"], any_)
        row["any_playable"] = max(row["any_playable"], any_playable)
        row["bank_max"] = max(row["bank_max"], bank)


def _peak_bank(log: list[dict]) -> int:
    """§17.4 `S1`'s falsifier: the max bank the fight ever printed.

    `gain_spark` and `spend_spark` both emit `total` = the bank AFTER the
    movement, and a bank only rises on a gain, so the max over those totals is
    the fight's peak exactly. A fight with no Spark event peaks at 0.
    """
    totals = [row.get("total", 0) for row in log
              if row.get("event") in ("gain_spark", "spend_spark")]
    return max(totals) if totals else 0


def _hand_snapshot(state) -> tuple[int, int, int, int]:
    """`(non-damage affordable, and playable, any affordable, and playable)`.

    §17.4's affordability rule: price >= 1 and price <= the bank. The stricter
    `card_playable` count rides beside it and no threshold is registered on it.
    """
    from tier0.engine.combat import card_playable, spark_price
    nd = nd_p = any_ = any_p = 0
    for card in state.player.hand:
        price = spark_price(state, card)
        if not price or price > state.player.sparks:
            continue
        playable = card_playable(state, card)
        any_ += 1
        any_p += int(playable)
        if card.id in NON_DAMAGE_SINKS:
            nd += 1
            nd_p += int(playable)
    return nd, nd_p, any_, any_p


def _observe(flag_on: bool, cell) -> tuple[list, _Observer, dict]:
    """Run `cell` under the flag with every observer seam patched, and REDUCE
    the observations before the flag comes back off.

    The reduction is inside the flag window on purpose and it is not a
    convenience: `loader.peek_card` resolves a `proto_` id through
    `_substituted_card_index`, which is EMPTY with the flag off, so reading a
    drafted deck's maker/sink counts after the restore would raise. The arm's
    numbers are therefore taken where the arm's cards exist.

    Restores all four patches and the flag in a `finally`, so a raised
    exception cannot leave the module or the world edited.
    """
    obs = _Observer()
    real_run_one = model.run_one
    real_run_fight = model.run_fight
    real_hindsight = model._RunCtx.mark_hindsight
    real_make_pilot = model.make_pilot
    original_flag = C.SPARK_ALT_COST_ENABLED
    original_subs = dict(C.SPARK_ALT_POOL_SUBS)

    def run_one(*a, **kw):
        obs.open_run()
        res = real_run_one(*a, **kw)
        obs.runs[-1]["deck"] = list(res.deck_ids)
        obs.runs[-1]["won"] = bool(res.won)
        obs.runs[-1]["node_kinds"] = list(res.node_kinds)
        return res

    def run_fight(player, enemies, pilot, **kw):
        rec = obs.open_fight()
        state = real_run_fight(player, enemies, pilot, **kw)
        rec["peak"] = _peak_bank(state.log)
        return state

    def mark_hindsight(self):
        obs.note_floor(len(self.res.node_kinds) - 1, self.deck_ids)
        return real_hindsight(self)

    def make_pilot(weights):
        inner = real_make_pilot(weights)

        def watched(state):
            nd, nd_p, any_, any_p = _hand_snapshot(state)
            obs.note_decision(state.turn, state.player.sparks,
                              nd, nd_p, any_, any_p)
            return inner(state)
        return watched

    model.run_one = run_one
    model.run_fight = run_fight
    model._RunCtx.mark_hindsight = mark_hindsight
    model.make_pilot = make_pilot
    C.SPARK_ALT_COST_ENABLED = flag_on
    if flag_on:
        # §17.2: the excluded Rare. Popping the SHIPPED key leaves the shipped
        # row in the Rare offer slot, so the tier's odds are untouched.
        C.SPARK_ALT_POOL_SUBS.pop(EXCLUDED_SUB_KEY, None)
    try:
        _clear_caches()
        results = cell.run()
        arm = _reduce(obs)
    finally:
        model.run_one = real_run_one
        model.run_fight = real_run_fight
        model._RunCtx.mark_hindsight = real_hindsight
        model.make_pilot = real_make_pilot
        C.SPARK_ALT_COST_ENABLED = original_flag
        C.SPARK_ALT_POOL_SUBS.clear()
        C.SPARK_ALT_POOL_SUBS.update(original_subs)
        _clear_caches()
    return results, obs, arm


# --- reduction ---------------------------------------------------------------

def _reduce(obs: _Observer) -> dict:
    """The arm's numbers. Every field is one of §17.4's falsifiers."""
    peaks = [f["peak"] for run in obs.runs for f in run["fights"]]
    turns = [row for run in obs.runs for f in run["fights"]
             for row in f["turns"].values()]
    n_turns = len(turns)
    decks = [run.get("deck", []) for run in obs.runs]

    floors: dict[int, list[float]] = {f: [] for f in RATIO_FLOORS}
    floor_n: dict[int, int] = {f: 0 for f in RATIO_FLOORS}
    for run in obs.runs:
        for floor in RATIO_FLOORS:
            deck = run["floors"].get(floor)
            if deck is None:
                continue
            floor_n[floor] += 1
            r = _ratio(deck)
            if r is not None:
                floors[floor].append(r)

    return {
        "runs": len(obs.runs),
        "fights": len(peaks),
        "turns": n_turns,
        # S1
        "peak_median": statistics.median(peaks) if peaks else 0.0,
        "peak_mean": statistics.mean(peaks) if peaks else 0.0,
        "peak_ge2_share": (sum(p >= NON_DAMAGE_PRICE for p in peaks)
                           / len(peaks)) if peaks else 0.0,
        "peak_hist": {str(k): peaks.count(k)
                      for k in sorted(set(peaks))},
        # S2
        "turns_nd_affordable": sum(t["nd"] > 0 for t in turns),
        "turns_nd_affordable_share": (sum(t["nd"] > 0 for t in turns) / n_turns
                                      if n_turns else 0.0),
        "turns_nd_playable_share": (sum(t["nd_playable"] > 0 for t in turns)
                                    / n_turns if n_turns else 0.0),
        "turns_any_affordable_share": (sum(t["any"] > 0 for t in turns)
                                       / n_turns if n_turns else 0.0),
        # S3
        "decks_with_nd_sink": sum(any(cid in NON_DAMAGE_SINKS for cid in d)
                                  for d in decks),
        "decks_with_nd_sink_share": (
            sum(any(cid in NON_DAMAGE_SINKS for cid in d) for d in decks)
            / len(decks)) if decks else 0.0,
        "decks_with_any_proto_share": (
            sum(any(cid.startswith(loader.PROTOTYPE_ID_PREFIX) for cid in d)
                for d in decks) / len(decks)) if decks else 0.0,
        # S4
        "ratio_median": {str(f): (statistics.median(floors[f])
                                  if floors[f] else None)
                         for f in RATIO_FLOORS},
        "ratio_n": {str(f): floor_n[f] for f in RATIO_FLOORS},
        # S5
        "runs_with_rummage": sum(RUMMAGE in d for d in decks),
        "rummage_share": (sum(RUMMAGE in d for d in decks) / len(decks)
                          if decks else 0.0),
        # diagnostics only (R215 B, Guardrail-7) -- graded by nothing
        "win_share": (sum(bool(r.get("won")) for r in obs.runs) / len(obs.runs)
                      if obs.runs else 0.0),
        "decksize_mean": statistics.mean(len(d) for d in decks) if decks
        else 0.0,
    }


def _grade(arm: dict) -> list[dict]:
    """§17.4's five slots, against §17.4's thresholds and no others."""
    out = []

    # S1
    if arm["fights"] < 100:
        g = "UNREACHED"
    else:
        halves = (arm["peak_median"] >= NON_DAMAGE_PRICE,
                  arm["peak_ge2_share"] >= 0.60)
        g = ("PREDICTED" if all(halves)
             else "SPLIT" if any(halves) else "MISS")
    out.append({"slot": "S1", "grade": g,
                "read": f"median peak {arm['peak_median']:.1f}, "
                        f"share of fights peaking >= 2 "
                        f"{arm['peak_ge2_share'] * 100:.1f}%",
                "threshold": "median >= 2 AND >= 60% of fights peak >= 2"})

    # S2
    share = arm["turns_nd_affordable_share"]
    if arm["decks_with_nd_sink"] == 0:
        g = "UNREACHED"
    else:
        g = ("PREDICTED" if share >= 0.15
             else "SPLIT" if share >= 0.05 else "MISS")
    out.append({"slot": "S2", "grade": g,
                "read": f"{share * 100:.2f}% of {arm['turns']} player turns "
                        f"({arm['turns_nd_affordable']} turns)",
                "threshold": ">= 15% PREDICTED, 5-15% SPLIT, < 5% MISS"})

    # S3
    share = arm["decks_with_nd_sink_share"]
    g = ("PREDICTED" if share >= 0.50
         else "SPLIT" if share >= 0.20 else "MISS")
    out.append({"slot": "S3", "grade": g,
                "read": f"{share * 100:.1f}% of {arm['runs']} runs "
                        f"({arm['decks_with_nd_sink']} decks)",
                "threshold": ">= 50% PREDICTED, 20-50% SPLIT, < 20% MISS"})

    # S4
    r5 = arm["ratio_median"]["5"]
    r15 = arm["ratio_median"]["15"]
    if arm["ratio_n"]["15"] < 30 or r15 is None or r5 is None:
        g = "UNREACHED"
    else:
        halves = (r15 < r5, 0.30 <= r15 <= 0.80)
        g = ("PREDICTED" if all(halves)
             else "SPLIT" if any(halves) else "MISS")
    out.append({"slot": "S4", "grade": g,
                "read": "median maker:sink " + ", ".join(
                    f"floor {f} = "
                    + ("-" if arm['ratio_median'][str(f)] is None
                       else f"{arm['ratio_median'][str(f)]:.3f}")
                    + f" (n={arm['ratio_n'][str(f)]})" for f in RATIO_FLOORS),
                "threshold": "median FALLS 5 -> 15 AND floor-15 median in "
                             "[0.30, 0.80]"})

    # S5
    g = "PREDICTED" if arm["runs_with_rummage"] == 0 else "MISS"
    out.append({"slot": "S5", "grade": g,
                "read": f"{arm['rummage_share'] * 100:.1f}% of runs "
                        f"({arm['runs_with_rummage']} decks) hold Rummage",
                "threshold": "exactly 0.0% PREDICTED, anything > 0 MISS"})
    return out


def _print_arm(label: str, arm: dict) -> None:
    print(label)
    print(f"    runs {arm['runs']}   fights {arm['fights']}   "
          f"player turns {arm['turns']}")
    print(f"    peak Spark bank      median {arm['peak_median']:.1f}   "
          f"mean {arm['peak_mean']:.2f}   "
          f">=2 on {arm['peak_ge2_share'] * 100:.1f}% of fights")
    print(f"    peak histogram       {arm['peak_hist']}")
    print(f"    turns w/ non-damage sink affordable   "
          f"{arm['turns_nd_affordable_share'] * 100:.2f}%   "
          f"(and playable {arm['turns_nd_playable_share'] * 100:.2f}%)")
    print(f"    turns w/ ANY priced sink affordable   "
          f"{arm['turns_any_affordable_share'] * 100:.2f}%")
    print(f"    decks holding a non-damage sink       "
          f"{arm['decks_with_nd_sink_share'] * 100:.1f}%")
    print(f"    decks holding ANY prototype row       "
          f"{arm['decks_with_any_proto_share'] * 100:.1f}%")
    for f in RATIO_FLOORS:
        med = arm["ratio_median"][str(f)]
        print(f"    maker:sink at floor {f:<2}   "
              + ("-" if med is None else f"{med:.3f}")
              + f"   (n={arm['ratio_n'][str(f)]} decks reached it)")
    print(f"    runs holding Rummage  {arm['runs_with_rummage']} "
          f"({arm['rummage_share'] * 100:.1f}%)")
    print(f"    mean deck size {arm['decksize_mean']:.1f}   "
          f"runs won {arm['win_share'] * 100:.1f}%   "
          f"NOT A BALANCE CLAIM (R215 B)")
    print()


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", type=int, default=CELL.runs)
    ap.add_argument("--seed", type=int, default=CELL.seed)
    ap.add_argument("--json", default=None,
                    help="write the record to this path")
    args = ap.parse_args(argv)

    cell = CELL.but(runs=args.runs, seed=args.seed, name=CELL.name)
    if cell.jobs != 1:
        print("REFUSED: the observer seams live in this process; jobs must "
              "be 1.", file=sys.stderr)
        return 2

    stamp = cells.world_stamp()
    print("KLEESPARK-S1 — the Klee Spark arm measured DRAFTED, in the sim.")
    print(f"  REGISTRATION: review/active/klee-sparks-2026-08-29.md §17 "
          f"(slate §17.4), committed before this file and before this run.")
    print(f"  world stamp {stamp}   cell {cell.describe()}")
    print("  NOT A BALANCE READ (R215 B). Counts only; Guardrail-7 applies.")
    print(f"  ARM = flag ON: substituted starter + PICK 4's pool subs + the "
          f"three EB-218 twins, {EXCLUDED_SUB_KEY} EXCLUDED (§12.2).")
    print("  CONTROL = flag OFF, same cell and seeds: RECORDED, NOT GRADED.")
    print()

    record: dict = {"registration": "KLEESPARK-S1",
                    "packet": "review/active/klee-sparks-2026-08-29.md §17",
                    "stamp": stamp, "cell": cell.describe(), "arms": {}}
    for label, flag in (("flag OFF (shipped pool) — CONTROL, NOT GRADED",
                         False),
                        ("flag ON  (the arm) — GRADED", True)):
        _, _obs, arm = _observe(flag, cell)
        _print_arm(label, arm)
        record["arms"]["on" if flag else "off"] = arm

    grades = _grade(record["arms"]["on"])
    record["grades"] = grades
    print("THE SLATE, graded against §17.4's registered thresholds:")
    for row in grades:
        print(f"  {row['slot']}  {row['grade']:<10}  {row['read']}")
        print(f"      threshold: {row['threshold']}")
    inherited = record["arms"]["on"]["ratio_median"]["15"]
    print()
    print("THE RATIO THE LIVE REGISTRATION INHERITS (§17.4 `S4`): "
          + ("UNREACHED — no floor-15 median" if inherited is None
             else f"{inherited:.3f} makers per sink at floor 15"))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=2, sort_keys=True)
        print(f"record written to {args.json}")
    return 0


if __name__ == "__main__":
    expcli.help_if_asked(__doc__)
    sys.exit(main())
