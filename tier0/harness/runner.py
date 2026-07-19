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
                 seed: int) -> dict:
    """Full battery for baseline + target config -> 7-axis scorecard."""
    base_stats = run_full_battery(*BASELINE, pilot_id, fights, seed)
    base_raw = axes.raw_axes(base_stats)
    base_dpt = None                      # baseline is self-referential for A7
    target_is_baseline = (character, deck) == BASELINE
    if target_is_baseline:
        stats, raw = base_stats, base_raw
    else:
        pooled = [s for ss in base_stats.values() for s in ss]
        base_dpt = sum(s.total_damage_dealt / max(1, s.turns)
                       for s in pooled) / len(pooled)
        stats = run_full_battery(character, deck, pilot_id, fights, seed)
        raw = axes.raw_axes(stats, baseline_dpt=base_dpt)
    scores = axes.normalize(raw, base_raw)
    pressure_delta = (metrics.summarize(stats["punisher"])["winrate"]
                      - metrics.summarize(stats["attrition"])["winrate"])
    return {
        "scores": scores, "raw": raw,
        "curve_exponent": axes.curve_exponent(stats["tank_boss"]),
        "pressure_delta": pressure_delta,
        # The baseline is flat-3.0 by construction; the shape heuristic
        # only means something for compared configs.
        "heuristic_flags": ([] if target_is_baseline
                            else axes.heuristic_flags(scores)),
        "stats": stats,
    }


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
    ap.add_argument("--score", action="store_true",
                    help="run full battery + baseline and print the "
                         "7-axis scorecard")
    args = ap.parse_args(argv)

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
    t0 = time.perf_counter()
    total_fights = 0
    for enc in encounters:
        stats = run_battery(args.character, args.deck, enc, args.pilot,
                            args.fights, args.seed)
        total_fights += len(stats)
        summary = metrics.summarize(stats)
        report.print_summary(args.character, args.deck, enc, summary)
        for i, s in enumerate(stats):
            rows.append({"encounter": enc, "fight": i, "won": s.won,
                         "turns": s.turns, "hp_delta": s.hp_delta,
                         "damage": s.total_damage_dealt,
                         "block": s.total_block_gained,
                         "energy": s.energy_spent,
                         "reactions": s.reactions,
                         "flags": "|".join(s.flags)})
    elapsed = time.perf_counter() - t0
    print(f"\n{total_fights} fights in {elapsed:.2f}s "
          f"({total_fights / elapsed:.0f} fights/sec)")

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"wrote {len(rows)} rows to {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
