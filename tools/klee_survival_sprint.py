"""Measurement grid for the Klee survival sprint.

This is deliberately a report tool, not a balance implementation.  It runs the
four assigned Klee plans through the realistic Act-1 layer with relic and
potion granting enabled, then prints the survival signals used by
``docs/klee-survival-sprint-plan.md``.

Usage:
    python -m tools.klee_survival_sprint --runs 1500 --seed 11
"""

from __future__ import annotations

import argparse
import hashlib
import math
import subprocess

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import powers
from tier0.harness import axes
from tier0.harness import metrics as fight_metrics
from tier0.harness.runner import run_battery
from tier05 import draft, model, run_metrics


PLANS = ("generic", "demolition", "spark", "reaction")
FURINA_PLANS = (
    ("salon", "salon"),
    ("spotlight", "spotlight"),
    ("fanfare", "fanfare"),
)
PREVIOUS_FRONTLOAD = {
    "kaboom": 6,
    "jumpy_dumpty": 7,
    "big_badda_boom": 12,
    "blast_radius": 6,
    "pocket_fireworks": 4,
    "rapid_fire": 3,
    "snap": 5,
    "sizzle": 7,
    "boom_goes_the_dynamite": 16,
    "flame_dance": 7,
}


def _git_world() -> tuple[str, str]:
    """Commit and tracked-worktree digest for concurrent-sprint attribution."""
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


def _print_world() -> None:
    commit, dirty = _git_world()
    print(
        "world: "
        f"git={commit} tracked_diff={dirty} "
        f"CONSTANTS={C.CONSTANTS_VERSION} "
        f"DRAFTER={C.DRAFTER_VERSION} "
        f"RUNTEMPLATE={C.RUNTEMPLATE_VERSION} "
        f"A6={axes.A6_INSTRUMENT_VERSION}"
    )


def _wilson(wins: int, runs: int, z: float = 1.96) -> tuple[float, float]:
    if runs == 0:
        return 0.0, 0.0
    p = wins / runs
    denom = 1 + z * z / runs
    center = (p + z * z / (2 * runs)) / denom
    half = z * math.sqrt(
        p * (1 - p) / runs + z * z / (4 * runs * runs)
    ) / denom
    return center - half, center + half


def _normal_loss(results: list[model.RunResult], max_hp: int) -> tuple[float, float]:
    losses: list[int] = []
    for run in results:
        fight_kinds = [kind for kind in run.node_kinds if kind in ("N", "E", "B")]
        for kind, stats in zip(fight_kinds, run.fight_stats):
            if kind == "N":
                losses.append(max(0, stats.hp_start - stats.hp_end))
    raw = sum(losses) / len(losses) if losses else 0.0
    return raw, raw / max_hp if max_hp else 0.0


def _disable_bomb_suppression() -> None:
    """Install the pre-Window-A damage rule for an adjacent control.

    The parallel simulator-fix thread may advance HEAD during this sprint.
    A switch in the current world is safer than comparing a treatment to an
    archived checkout with different bug fixes.
    """

    def control_damage(attacker, base):
        damage = base + attacker.powers.get("strength", 0)
        if attacker.powers.get("weak", 0) > 0:
            damage *= C.WEAK_DEALT_MULT
        return damage if damage > 0 else 0.0

    powers.modify_damage_dealt = control_damage


def _disable_frontload_pass(card_ids: set[str] | None = None) -> None:
    """Restore selected pre-Window-B card bodies for an adjacent control.

    ``card_ids`` makes it possible to trim the table without editing the
    sheet between cells. Omitting it restores the complete pre-sprint set.
    """
    restore = card_ids if card_ids is not None else set(PREVIOUS_FRONTLOAD)
    cards = loader._card_index()
    for card_id in restore:
        amount = PREVIOUS_FRONTLOAD[card_id]
        hit = next(
            effect for effect in cards[card_id].effects
            if effect.get("op") == "damage" and effect.get("target") != "self"
        )
        hit["amount"] = amount
    if "sizzle" in restore:
        sizzle_rider = next(
            effect for effect in cards["sizzle"].effects
            if effect.get("op") == "conditional"
        )
        sizzle_rider["then"][0]["amount"] = 5


def _disable_companion_rework() -> None:
    """Restore the four pre-Window-D companion-interface rows."""
    cards = loader._card_index()
    cards["friendly_visit"].effects = cards["friendly_visit"].effects[1:]
    cards["elemental_ecstasy"].effects = (
        cards["elemental_ecstasy"].effects[:-1]
    )
    cards["borrowed_brilliance"].effects[0].pop("cost_override", None)
    cards["study_buddy"].effects = cards["study_buddy"].effects[1:]
    upgrades._upgrade_index()["borrowed_brilliance"] = {
        "copy_cost_override": 0,
    }


def measure(
    runs: int,
    seed: int,
    bomb_suppression: bool = True,
    frontload_pass: bool = True,
    excluded_frontload: set[str] | None = None,
    companion_rework: bool = True,
    overload_stagger: bool = True,
) -> None:
    if not bomb_suppression:
        _disable_bomb_suppression()
    if not frontload_pass:
        _disable_frontload_pass()
    elif excluded_frontload:
        _disable_frontload_pass(excluded_frontload)
    if not companion_rework:
        _disable_companion_rework()
    if not overload_stagger:
        C.OVERLOAD_WEAK = 0
    _print_world()
    print(
        f"cell: runs={runs} seed={seed} policy=assigned "
        f"relics=on potions=on bomb_suppression={'on' if bomb_suppression else 'off'} "
        f"frontload={'on' if frontload_pass else 'off'} "
        f"excluded={','.join(sorted(excluded_frontload or ())) or '-'} "
        f"companions={'on' if companion_rework else 'off'} "
        f"overload_stagger={'on' if overload_stagger else 'off'}"
    )
    print()
    print(
        "plan          win% [Wilson95]      normal loss (%max)  "
        "act HP%  near-death  online"
    )
    for plan in PLANS:
        results = model.run_many(
            "klee", plan, plan, draft.POLICIES["assigned"], runs, seed,
            grant_relics=True, grant_potions=True,
        )
        summary = run_metrics.summarize_runs(results)
        max_hp = loader._character_index()["klee"]["hp"]
        survival = run_metrics.survival_profile(results, max_hp)
        wins = sum(run.won for run in results)
        lo, hi = _wilson(wins, runs)
        loss, loss_pct = _normal_loss(results, max_hp)
        print(
            f"{plan:<13} {summary['winrate']:>5.1%} "
            f"[{lo:>5.1%}, {hi:>5.1%}]   "
            f"{loss:>6.2f} ({loss_pct:>5.1%})       "
            f"{survival['act_median_hp_pct']:>6.1%}   "
            f"{survival['near_death_rate']:>6.1%}    "
            f"{summary['online_rate']:>6.1%}"
        )


def measure_bands(
    fights: int,
    seed: int,
    bomb_suppression: bool = True,
    frontload_pass: bool = True,
    excluded_frontload: set[str] | None = None,
    companion_rework: bool = True,
    overload_stagger: bool = True,
) -> None:
    if not bomb_suppression:
        _disable_bomb_suppression()
    if not frontload_pass:
        _disable_frontload_pass()
    elif excluded_frontload:
        _disable_frontload_pass(excluded_frontload)
    if not companion_rework:
        _disable_companion_rework()
    if not overload_stagger:
        C.OVERLOAD_WEAK = 0
    _print_world()
    print(
        f"tier0 bands: fights={fights} seed={seed} "
        f"bomb_suppression={'on' if bomb_suppression else 'off'} "
        f"frontload={'on' if frontload_pass else 'off'} "
        f"excluded={','.join(sorted(excluded_frontload or ())) or '-'} "
        f"companions={'on' if companion_rework else 'off'} "
        f"overload_stagger={'on' if overload_stagger else 'off'}"
    )
    for deck, pilot in (
        ("demolition_weighted", "demolition"),
        ("spark_weighted", "spark"),
        ("reaction_weighted", "reaction"),
    ):
        tank = fight_metrics.summarize(
            run_battery("klee", deck, "tank_boss", pilot, fights, seed)
        )["winrate"]
        extra = ""
        if deck == "reaction_weighted":
            gauntlet = fight_metrics.summarize(
                run_battery("klee", deck, "gauntlet", pilot, fights, seed)
            )["winrate"]
            extra = f" gauntlet={gauntlet:.1%}"
        print(f"{deck:<24} tank_boss={tank:.1%}{extra}")


def measure_furina(runs: int, seed: int, overload_stagger: bool = True) -> None:
    """Cross-character guard for the shared Overload change."""
    if not overload_stagger:
        C.OVERLOAD_WEAK = 0
    _print_world()
    print(
        f"furina cross-check: runs={runs} seed={seed} policy=assigned "
        f"relics=on potions=on "
        f"overload_stagger={'on' if overload_stagger else 'off'}"
    )
    for archetype, pilot in FURINA_PLANS:
        results = model.run_many(
            "furina", archetype, pilot, draft.POLICIES["assigned"], runs, seed,
            grant_relics=True, grant_potions=True,
        )
        wins = sum(run.won for run in results)
        lo, hi = _wilson(wins, runs)
        print(
            f"{archetype:<12} {wins / runs:>5.1%} "
            f"[{lo:>5.1%}, {hi:>5.1%}]"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=1500)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument(
        "--bomb-suppression", choices=("on", "off"), default="on",
        help="run current behavior or the adjacent pre-Window-A control",
    )
    parser.add_argument(
        "--frontload", choices=("on", "off"), default="on",
        help="run current card bodies or the adjacent pre-Window-B control",
    )
    parser.add_argument(
        "--tier0-bands", action="store_true",
        help="measure archetype tank-boss bands instead of realistic runs",
    )
    parser.add_argument(
        "--furina-check", action="store_true",
        help="run the Furina cross-character guard for Overload instead",
    )
    parser.add_argument(
        "--exclude-frontload", action="append", default=[],
        choices=tuple(PREVIOUS_FRONTLOAD),
        help="restore one changed card to its pre-sprint body (repeatable)",
    )
    parser.add_argument(
        "--companion-rework", choices=("on", "off"), default="on",
        help="run current interface cards or their adjacent pre-sprint control",
    )
    parser.add_argument(
        "--overload-stagger", choices=("on", "off"), default="on",
        help="run Overload Weak or its adjacent no-stagger control",
    )
    args = parser.parse_args()
    if args.furina_check:
        measure_furina(
            args.runs, args.seed,
            overload_stagger=args.overload_stagger == "on",
        )
        return
    fn = measure_bands if args.tier0_bands else measure
    fn(args.runs, args.seed,
       bomb_suppression=args.bomb_suppression == "on",
       frontload_pass=args.frontload == "on",
       excluded_frontload=set(args.exclude_frontload),
       companion_rework=args.companion_rework == "on",
       overload_stagger=args.overload_stagger == "on")


if __name__ == "__main__":
    main()
