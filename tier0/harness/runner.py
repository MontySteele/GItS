"""CLI entry point: run N fights x encounters x configs, seeded.

Usage:
    python -m tier0.harness.runner --character ref_ironclad --deck starter \
        --encounter punisher --fights 1000 --seed 42 --csv out.csv

Fast iteration loop > elegance (spec §0): single command, CSV out,
summary table in terminal.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.combat import run_fight
from tier0.harness import axes, metrics, report
from tier0.pilot.policy import make_pilot

BASELINE = ("ref_ironclad", "starter")     # =3.0 on all axes by construction


def run_battery(character: str, deck: str, encounter_id: str, pilot_id: str,
                fights: int, seed: int) -> list[metrics.FightStats]:
    pilot = make_pilot(loader.pilot_weights(pilot_id))
    stages = loader.encounter_stages(encounter_id)
    stats = []
    for i in range(fights):
        stage_stats = []
        carry_hp = None
        for stage in stages:
            player = loader.build_player(character, deck)
            if carry_hp is not None:
                player.hp = carry_hp        # HP carries; deck/powers reset
            hp_start = player.hp
            state = run_fight(player, loader.build_encounter(stage), pilot,
                              seed=seed + i)
            stage_stats.append(metrics.extract(state, hp_start))
            carry_hp = state.player.hp
            if not state.player.alive:
                break
        stats.append(metrics.merge_stages(stage_stats))
    return stats


def run_full_battery(character: str, deck: str, pilot_id: str, fights: int,
                     seed: int) -> dict[str, list[metrics.FightStats]]:
    battery = [e for e in loader.encounter_ids()]
    return {enc: run_battery(character, deck, enc, pilot_id, fights, seed)
            for enc in battery}


def score_config(character: str, deck: str, pilot_id: str, fights: int,
                 seed: int, base_stats: dict | None = None) -> dict:
    """Full battery for baseline + target config -> 7-axis scorecard.
    The baseline ALWAYS uses the generic pilot — a floating anchor would
    make scores incomparable across archetype-pilot runs.

    `base_stats` lets a caller scoring SEVERAL configs at one (fights, seed)
    compute that anchor once and hand it in. It is a deterministic function
    of (fights, seed) and nothing here mutates it, so sharing it is only a
    saving -- score_character used to re-run the whole baseline battery once
    per deck, which was most of its cost. None recomputes it."""
    if base_stats is None:
        base_stats = run_full_battery(*BASELINE, "generic", fights, seed)
    base_raw = axes.raw_axes(base_stats)
    target_is_baseline = (character, deck) == BASELINE
    if target_is_baseline:
        stats, raw = base_stats, base_raw
    else:
        stats = run_full_battery(character, deck, pilot_id, fights, seed)
        raw = axes.raw_axes(stats)
    scores = axes.normalize(raw, base_raw)
    # Round-3 restructure: constraints are HARD on starter (and on the
    # median, checked in score_character); informational on package decks.
    constraint_flags = []
    severity = "CONSTRAINT VIOLATED" if deck == "starter" else "warn (package deck)"
    for con in loader.character_constraints(character):
        left, right = con.split(">")
        if not scores[left] > scores[right]:
            constraint_flags.append(
                f"{severity}: {con} "
                f"({scores[left]:.1f} vs {scores[right]:.1f})")
    # B4: a band annotated as known-stale still fires -- it is ratified law
    # until a ruling moves it -- but the flag carries WHY, so a gate that
    # fires on every run of a character is not mistaken for a live finding.
    stale = loader.stale_bands(character)
    for axis, per_deck in loader.deck_bands(character).items():
        if deck in per_deck and scores[axis] > per_deck[deck]:
            reason = stale.get(axis, {}).get(deck)
            constraint_flags.append(
                f"BAND EXCEEDED: {axis} {scores[axis]:.1f} > "
                f"{per_deck[deck]} for {deck}"
                + (f" ({reason})" if reason else ""))
    pressure_delta = (metrics.summarize(stats["punisher"])["winrate"]
                      - metrics.summarize(stats["attrition"])["winrate"])
    return {
        "scores": scores, "raw": raw,
        "curve_exponent": axes.curve_exponent(stats["tank_boss"]),
        "pressure_delta": pressure_delta,
        # The baseline is flat 3.0 by construction. The SHAPE heuristic
        # runs on starter and the archetype-median only (round 3) —
        # monoculture packages always read extreme and taught us nothing.
        "heuristic_flags": (constraint_flags
                            if target_is_baseline or deck != "starter"
                            else axes.heuristic_flags(scores) + constraint_flags),
        "stats": stats,
    }


def score_character(character: str, fights: int, seed: int) -> dict:
    """Round-3 identity evaluation: starter + per-axis MEDIAN across the
    character's archetype decks. Shape heuristic and constraints are hard
    here; per-deck results carry only their band checks."""
    import statistics
    decks = loader.archetype_decks(character)
    # One anchor battery for every deck scored here (see score_config).
    base_stats = run_full_battery(*BASELINE, "generic", fights, seed)
    results = {"starter": score_config(character, "starter", "generic",
                                       fights, seed, base_stats)}
    for deck, pilot in decks.items():
        results[deck] = score_config(character, deck, pilot, fights, seed,
                                     base_stats)
    median_scores = {
        ax: statistics.median(results[d]["scores"][ax] for d in decks)
        for ax in axes.AXES}
    median_flags = axes.heuristic_flags(median_scores)
    for con in loader.character_constraints(character):
        left, right = con.split(">")
        if not median_scores[left] > median_scores[right]:
            median_flags.append(
                f"CONSTRAINT VIOLATED on median: {con} "
                f"({median_scores[left]:.1f} vs {median_scores[right]:.1f})")
    # Ratified winrate bands (pass-3 closeout): matchup texture is part of
    # each archetype's identity. Process fix: only checked at >=1000
    # fights — below that, binomial noise makes band edges meaningless.
    band_flags = []
    wr_bands = loader.winrate_bands(character)
    if wr_bands and fights < C.WINRATE_BAND_MIN_FIGHTS:
        band_flags.append(f"winrate bands not checked "
                          f"({fights} < {C.WINRATE_BAND_MIN_FIGHTS} fights)")
    elif wr_bands:
        for enc, per_deck in wr_bands.items():
            for deck, (lo, hi) in per_deck.items():
                wr = metrics.summarize(results[deck]["stats"][enc])["winrate"]
                if wr < lo or (hi is not None and wr > hi):
                    hi_s = f"{hi:.0%}" if hi is not None else "-"
                    band_flags.append(
                        f"WINRATE BAND: {deck} vs {enc} {wr:.1%} "
                        f"outside [{lo:.0%}, {hi_s}]")
    return {"per_deck": results, "median_scores": median_scores,
            "median_flags": median_flags, "band_flags": band_flags}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Tier 0 balance simulator")
    ap.add_argument("--character", default="ref_ironclad")
    ap.add_argument("--deck", default="starter",
                    help="'starter' or a package name from the character yaml")
    ap.add_argument("--encounter", default="all",
                    help="encounter id, or 'all' for the whole battery")
    ap.add_argument("--pilot", default="generic")
    ap.add_argument("--fights", type=int, default=C.DEFAULT_FIGHTS_PER_ENCOUNTER)
    ap.add_argument("--seed", type=int, default=C.DEFAULT_SEED)
    ap.add_argument("--csv", default=None, help="write per-fight rows to CSV")
    ap.add_argument("--turns-csv", default=None,
                    help="write the per-TURN record (D2: HP trajectory + "
                         "incoming attacks per turn) to CSV, one row per "
                         "player turn per fight")
    ap.add_argument("--reaction-share", action="store_true",
                    help="print D1's reactions-share-of-damage aggregate for "
                         "each encounter and for the battery as a whole")
    ap.add_argument("--score", action="store_true",
                    help="run full battery + baseline and print the "
                         "7-axis scorecard")
    ap.add_argument("--report-character", action="store_true",
                    help="starter + all archetype decks + the median "
                         "identity evaluation (round-3 canon)")
    args = ap.parse_args(argv)

    # The summary line prints "hpΔ" and the scorecard prints block-glyph
    # bars; a cp1252 console (Windows default) raises UnicodeEncodeError on
    # both, killing the run AFTER the battery has been computed. Same
    # pre-existing bug already fixed in tier05/runner.py -- found here
    # 2026-07-21 when the real_ironclad comparison could not be printed.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):       # non-reconfigurable stream
        pass

    if args.report_character:
        t0 = time.perf_counter()
        rep = score_character(args.character, args.fights, args.seed)
        for deck, result in rep["per_deck"].items():
            report.print_scorecard(args.character, deck, result)
        report.print_median(args.character, rep)
        print(f"\n(character report in {time.perf_counter() - t0:.1f}s)")
        return 0

    if args.score:
        t0 = time.perf_counter()
        result = score_config(args.character, args.deck, args.pilot,
                              args.fights, args.seed)
        for enc in loader.encounter_ids():
            report.print_summary(args.character, args.deck, enc,
                                 metrics.summarize(result["stats"][enc]))
        report.print_scorecard(args.character, args.deck, result)
        print(f"\n(battery + baseline in {time.perf_counter() - t0:.1f}s)")
        return 0

    encounters = (loader.encounter_ids() if args.encounter == "all"
                  else [args.encounter])

    rows = []
    turn_rows = []
    every_stat: list[metrics.FightStats] = []
    t0 = time.perf_counter()
    total_fights = 0
    for enc in encounters:
        stats = run_battery(args.character, args.deck, enc, args.pilot,
                            args.fights, args.seed)
        total_fights += len(stats)
        every_stat.extend(stats)
        summary = metrics.summarize(stats)
        report.print_summary(args.character, args.deck, enc, summary)
        if args.reaction_share:
            report.print_reaction_share(enc, metrics.reaction_share(stats))
        for i, s in enumerate(stats):
            rows.append({"encounter": enc, "fight": i, "won": s.won,
                         "turns": s.turns, "hp_delta": s.hp_delta,
                         "damage": s.total_damage_dealt,
                         "block": s.total_block_gained,
                         "energy": s.energy_spent,
                         "reactions": s.reactions,
                         # D1, per-fight: absolute and share, on the record
                         # that already carries every other per-fight figure.
                         "damage_all_ops": s.damage_all_ops,
                         "damage_reactions": s.damage_from_reactions,
                         "damage_base_ops": s.damage_from_base_ops,
                         "reaction_share": round(s.reaction_share, 4),
                         "flags": "|".join(s.flags)})
            # D2: the per-turn record is a row per TURN, not a cell stuffed
            # into the per-fight row -- a trajectory pickled into CSV text is
            # a number nobody reads twice.
            for t, hp_o, blk_o, blk_e, hits, dmg_in in s.turn_trajectory:
                turn_rows.append({"encounter": enc, "fight": i, "turn": t,
                                  "hp_at_open": hp_o, "block_at_open": blk_o,
                                  "block_at_end": blk_e,
                                  "incoming_hits": hits,
                                  "incoming_damage": dmg_in})
    elapsed = time.perf_counter() - t0
    print(f"\n{total_fights} fights in {elapsed:.2f}s "
          f"({total_fights / elapsed:.0f} fights/sec)")

    if args.reaction_share and len(encounters) > 1:
        report.print_reaction_share("ALL ENCOUNTERS",
                                    metrics.reaction_share(every_stat))

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"wrote {len(rows)} rows to {args.csv}")
    if args.turns_csv and turn_rows:
        with open(args.turns_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=turn_rows[0].keys())
            writer.writeheader()
            writer.writerows(turn_rows)
        print(f"wrote {len(turn_rows)} turn rows to {args.turns_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
