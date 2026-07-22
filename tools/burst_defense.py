"""Burst-defense probe: can the character WALL a spike turn, everything on?

WHY THIS TOOL EXISTS
--------------------
A3 (block economy) scores total-damage-blocked / energy -- a THROUGHPUT
average. The realistic Act-1 roster does not kill by throughput; it kills by
BURST: Bygone Effigy 23, Phantasmal peak 28, Vantom's Dismember 27, all on
ONE turn. Putting up 5 block a turn and putting up 25 block on THE turn are
different skills, and A3 credits them identically -- so the sim under-rates
a thin-block character's fragility, and doubly so for a no-heal HP bar
(Klee, A4=0.5) where an unblocked spike is permanent.

This probe measures the thing A3 cannot: on the roster's spike turns, how
much of the incoming did the player's wall actually absorb? It runs the
character with its FULL realistic loadout (drafted deck + relics + potion
belt, node_kind=elite so block potions are live) against the bursty pool
(the 3 Act-1 elites + Vantom), and reads per-turn incoming vs blocked
straight off the combat log (player_hit: amount=HP lost, blocked=block
consumed; incoming = amount+blocked). Spike turn = incoming >= THRESHOLD.

Reported per character: how often a spike turn is survived intact, the
median share of a spike the wall covers, the median HP torn off on a spike,
and the block CEILING (largest wall the deck ever raised in one turn).
"""

from __future__ import annotations

import argparse
import random
import sys

from tier0.content import loader
from tier0.engine.combat import run_fight
from tier0.pilot.policy import make_pilot
from tier05 import act1, draft, model
from tools.realistic_axis_scores import _loadout, _reached_boss, _percentile

SPIKE = 20          # a turn whose total incoming >= this is a "spike"


def _bursty_specs() -> list[dict]:
    """The roster's spike-dealers: all 3 elites + the boss."""
    return list(act1.pools()["elite"]) + [act1.boss_encounter()]


def _turn_incoming(state) -> dict[int, tuple[int, int]]:
    """turn -> (incoming, blocked) from the log. incoming = HP lost + block
    consumed across every hit that turn; blocked = block consumed."""
    inc: dict[int, int] = {}
    blk: dict[int, int] = {}
    for ev in state.log:
        if ev["event"] == "player_hit":
            t = ev["turn"]
            inc[t] = inc.get(t, 0) + ev["amount"] + ev["blocked"]
            blk[t] = blk.get(t, 0) + ev["blocked"]
    return {t: (inc[t], blk.get(t, 0)) for t in inc}


def probe(character: str, runs: int, sample: int, fights: int,
          seed: int) -> dict:
    pilot = make_pilot(loader.pilot_weights("generic"))
    results = model.run_many(character, "generic", "generic",
                             draft.POLICIES["assigned"], runs, seed,
                             grant_relics=True, grant_potions=True)
    loaded = [r for r in results if _reached_boss(r)]
    if len(loaded) > sample:
        stride = len(loaded) / sample
        loaded = [loaded[int(i * stride)] for i in range(sample)]

    specs = _bursty_specs()
    coverage: list[float] = []      # blocked/incoming on each spike turn
    spike_hp_loss: list[float] = []  # HP torn off on each spike turn
    survived_intact = 0             # spike turns with 0 HP loss
    spike_turns = 0
    ceilings: list[float] = []      # per-fight max block consumed in a turn
    deaths = 0
    n_fights = 0

    for idx, r in enumerate(loaded):
        deck, relic_fx, belt, slots = _loadout(r, character)
        for si, spec in enumerate(specs):
            for k in range(fights):
                rng = random.Random(seed + 1009 * idx + 31 * si + k)
                enemies = act1.spawn(spec, rng)
                player = loader.build_player_from_ids(
                    character, deck,
                    relic_effects=list(relic_fx) if relic_fx else None,
                    potions=list(belt) if belt else None,
                    potion_slots=slots, node_kind="elite")
                state = run_fight(player, enemies, pilot,
                                  seed=rng.randrange(2 ** 31))
                n_fights += 1
                if not state.player.alive:
                    deaths += 1
                per_turn = _turn_incoming(state)
                fight_ceiling = 0
                for t, (inc, blk) in per_turn.items():
                    fight_ceiling = max(fight_ceiling, blk)
                    if inc >= SPIKE:
                        spike_turns += 1
                        coverage.append(blk / inc)
                        hp_loss = inc - blk
                        spike_hp_loss.append(hp_loss)
                        if hp_loss == 0:
                            survived_intact += 1
                ceilings.append(fight_ceiling)

    return {
        "character": character,
        "n_loadouts": len(loaded), "n_fights": n_fights,
        "spike_turns": spike_turns,
        "intact_rate": survived_intact / max(1, spike_turns),
        "median_coverage": _percentile(coverage, 0.5),
        "median_spike_hp_loss": _percentile(spike_hp_loss, 0.5),
        "p90_spike_hp_loss": _percentile(spike_hp_loss, 0.9),
        "block_ceiling_p50": _percentile(ceilings, 0.5),
        "block_ceiling_p90": _percentile(ceilings, 0.9),
        "death_rate": deaths / max(1, n_fights),
    }


def _print(rep: dict) -> None:
    print(f"\n=== {rep['character']}: BURST DEFENSE vs Act-1 spike pool "
          f"(spike turn >= {SPIKE} incoming) ===")
    print(f"  {rep['n_loadouts']} loadouts x {rep['n_fights']} fights | "
          f"{rep['spike_turns']} spike turns seen | "
          f"death rate {rep['death_rate']:.0%}")
    print(f"  spike survived intact (0 HP lost): {rep['intact_rate']:.0%}")
    print(f"  median wall coverage on a spike:   "
          f"{rep['median_coverage']:.0%}  (share of the hit blocked)")
    print(f"  HP torn off on a spike turn:       "
          f"med {rep['median_spike_hp_loss']:.0f}, "
          f"p90 {rep['p90_spike_hp_loss']:.0f}")
    print(f"  block CEILING (max wall in a turn): "
          f"p50 {rep['block_ceiling_p50']:.0f}, "
          f"p90 {rep['block_ceiling_p90']:.0f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Burst-defense probe on the Act-1 spike pool.")
    ap.add_argument("--characters", nargs="+",
                    default=["ref_ironclad", "real_ironclad", "klee"])
    ap.add_argument("--runs", type=int, default=200)
    ap.add_argument("--sample", type=int, default=15)
    ap.add_argument("--fights", type=int, default=8,
                    help="fights per (loadout, spike encounter)")
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    for ch in args.characters:
        _print(probe(ch, args.runs, args.sample, args.fights, args.seed))
