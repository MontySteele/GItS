"""Run real, boss-reaching Act-1 builds through the frozen Tier-0 battery.

This is the hybrid accepted in the M5 triage: Tier 0.5 supplies plausible
drafted builds; the synthetic battery supplies controlled matchup probes.
Two surfaces are printed because they answer different questions:

``deck``
    The harvested, upgraded deck with no relics or potions. This is the direct
    successor to the authored-deck winrate bands and remains discriminating
    when the old battery is easy for a complete loadout.

``loaded``
    The same deck with its run's combat relic effects and representative
    potion belt. This answers what the real character does, but can saturate
    easy synthetic encounters. Each independent fight starts with a fresh
    copy of the reconstructed belt, matching realistic_axis_scores.py.

Usage:
    python -m tools.real_battery_calibration --runs 1500 --sample 40 --fights 50
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from dataclasses import dataclass

from tier0.content import loader, local_reference
from tier0.engine.combat import run_fight
from tier0.harness import metrics
from tier0.pilot.policy import make_pilot
from tier05 import draft, model
from tools.realistic_axis_scores import _loadout, _reached_boss


@dataclass(frozen=True)
class Config:
    label: str
    character: str
    archetype: str
    pilot: str


CONFIGS = (
    Config("ironclad", "real_ironclad", "generic", "ironclad"),
    Config("klee_generic", "klee", "generic", "generic"),
    Config("klee_demo", "klee", "demolition", "demolition"),
    Config("klee_spark", "klee", "spark", "spark"),
    Config("klee_reaction", "klee", "reaction", "reaction"),
)


def _git_world() -> tuple[str, str]:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], check=True,
            capture_output=True, text=True,
        ).stdout.strip()
        diff = subprocess.run(
            ["git", "diff", "--binary"], check=True, capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return "unknown", "unknown"
    return commit, hashlib.sha256(diff).hexdigest()[:12]


def _game_ref_digest() -> str:
    """Digest of the gitignored game_ref/ sheets the loader consumes.

    WHY: on 2026-07-22/23 a measurement world diverged between two machines
    while their world lines matched, because ``tracked_diff`` hashes only
    ``git diff --binary`` over TRACKED files -- gitignored game_ref content
    (ironclad_pool.yaml, ironclad-upgrades.yaml, char_real_ironclad.yaml,
    the ironclad_pool_pass*.yaml layers) was invisible to provenance. Hash
    every ``*.yaml`` in game_ref/, sorted by name, name and content both,
    so any local-reference difference changes the digest. Absence of the
    directory (or committed-only mode, where the loader consumes none of
    it) is labeled distinctly rather than hashed as empty.
    """
    if local_reference.mode() == local_reference.COMMITTED_ONLY:
        return "committed-only"
    ref_dir = local_reference.game_ref_dir()
    if not ref_dir.is_dir():
        return "absent"
    digest = hashlib.sha256()
    for path in sorted(ref_dir.glob("*.yaml"), key=lambda p: p.name):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\x00")
        digest.update(path.read_bytes())
        digest.update(b"\x00")
    return digest.hexdigest()[:12]


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    pos = q * (len(ordered) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def _sample_evenly(results, sample: int):
    if len(results) <= sample:
        return list(results)
    stride = len(results) / sample
    return [results[int(i * stride)] for i in range(sample)]


def _node_context(encounter: str) -> tuple[str, str]:
    """Relic-layer kind and combat-layer string for a battery encounter."""
    if encounter == "tank_boss":
        return "B", "boss"
    return "E", "elite"


def _fight_stats(character: str, card_ids: list[str], pilot, encounter: str,
                 fights: int, seed: int, *, relic_effects=None,
                 potions=None, potion_slots: int = 3,
                 node_kind: str = "") -> list[metrics.FightStats]:
    """One battery encounter over one harvested build, gauntlet-aware."""
    stages = loader.encounter_stages(encounter)
    output: list[metrics.FightStats] = []
    for i in range(fights):
        stage_stats = []
        carry_hp = None
        carry_max_hp = None
        carry_potions = None
        for stage in stages:
            stage_potions = potions if carry_potions is None else carry_potions
            player = loader.build_player_from_ids(
                character,
                card_ids,
                relic_effects=list(relic_effects) if relic_effects else None,
                potions=(list(stage_potions)
                         if stage_potions is not None else None),
                potion_slots=potion_slots,
                node_kind=node_kind,
            )
            if carry_hp is not None:
                player.hp = carry_hp
                player.max_hp = carry_max_hp
            hp_start = player.hp
            state = run_fight(
                player, loader.build_encounter(stage), pilot, seed=seed + i,
            )
            stage_stats.append(metrics.extract(state, hp_start))
            carry_hp = state.player.hp
            carry_max_hp = state.player.max_hp
            carry_potions = list(state.player.potions)
            if not state.player.alive:
                break
        output.append(metrics.merge_stages(stage_stats))
    return output


def evaluate(config: Config, runs: int, sample: int, fights: int,
             seed: int) -> dict:
    run_results = model.run_many(
        config.character, config.archetype, config.pilot,
        draft.POLICIES["assigned"], runs, seed,
        grant_relics=True, grant_potions=True,
        n_acts=1,   # §10: Act-1 instrument, pinned
    )
    reached = [result for result in run_results if _reached_boss(result)]
    selected = _sample_evenly(reached, sample)
    pilot = make_pilot(loader.pilot_weights(config.pilot))

    per_encounter = {}
    for encounter in loader.encounter_ids():
        deck_rates: list[float] = []
        loaded_rates: list[float] = []
        deck_wins = deck_total = loaded_wins = loaded_total = 0
        relic_kind, combat_kind = _node_context(encounter)
        for result in selected:
            deck = list(result.deck_ids)
            deck_stats = _fight_stats(
                config.character, deck, pilot, encounter, fights, seed,
            )
            deck_summary = metrics.summarize(deck_stats)
            deck_rates.append(deck_summary["winrate"])
            deck_wins += sum(stat.won for stat in deck_stats)
            deck_total += len(deck_stats)

            _, relic_fx, belt, slots = _loadout(
                result, config.character, relic_kind,
            )
            loaded_stats = _fight_stats(
                config.character, deck, pilot, encounter, fights, seed,
                relic_effects=relic_fx, potions=belt, potion_slots=slots,
                node_kind=combat_kind,
            )
            loaded_summary = metrics.summarize(loaded_stats)
            loaded_rates.append(loaded_summary["winrate"])
            loaded_wins += sum(stat.won for stat in loaded_stats)
            loaded_total += len(loaded_stats)

        def surface(rates, wins, total):
            return {
                "pooled": wins / max(1, total),
                "p10": _percentile(rates, 0.10),
                "median": _percentile(rates, 0.50),
                "p90": _percentile(rates, 0.90),
            }

        per_encounter[encounter] = {
            "deck": surface(deck_rates, deck_wins, deck_total),
            "loaded": surface(
                loaded_rates, loaded_wins, loaded_total,
            ),
        }

    return {
        "config": config,
        "run_winrate": sum(result.won for result in run_results) / runs,
        "boss_reached": len(reached),
        "sampled": len(selected),
        "encounters": per_encounter,
    }


def _cell(surface: dict) -> str:
    return (
        f"{surface['pooled']:.1%} "
        f"[{surface['p10']:.0%}/{surface['median']:.0%}/{surface['p90']:.0%}]"
    )


def print_report(report: dict) -> None:
    config = report["config"]
    print(
        f"\n=== {config.label}: {config.character}/{config.archetype} "
        f"pilot={config.pilot} ==="
    )
    print(
        f"real-run win={report['run_winrate']:.1%}; "
        f"boss-reached={report['boss_reached']}; "
        f"battery loadouts={report['sampled']}"
    )
    print("encounter       deck pooled [p10/med/p90]   loaded pooled [p10/med/p90]")
    for encounter, surfaces in report["encounters"].items():
        print(
            f"{encounter:<15} {_cell(surfaces['deck']):<28} "
            f"{_cell(surfaces['loaded'])}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=1500)
    parser.add_argument("--sample", type=int, default=40)
    parser.add_argument("--fights", type=int, default=50)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument(
        "--configs", nargs="+", choices=[config.label for config in CONFIGS],
        default=[config.label for config in CONFIGS],
    )
    args = parser.parse_args()
    chosen = {label for label in args.configs}
    commit, dirty = _git_world()
    print(
        f"world: git={commit} tracked_diff={dirty} "
        f"game_ref={_game_ref_digest()} runs={args.runs} "
        f"sample={args.sample} fights={args.fights} seed={args.seed}"
    )
    available = loader._character_index()
    for config in CONFIGS:
        if config.label in chosen:
            if config.character not in available:
                print(
                    f"\n=== {config.label}: SKIPPED ===\n"
                    f"{config.character!r} is unavailable; restore the local "
                    "game_ref artifacts before using this comparison line."
                )
                continue
            print_report(evaluate(
                config, args.runs, args.sample, args.fights, args.seed,
            ))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    main()
