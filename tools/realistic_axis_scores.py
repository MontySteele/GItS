"""The 7-axis scorecard measured IN REALISTIC RUNS -- everything ON.

WHY THIS TOOL EXISTS
--------------------
The standing scorecard (tier0/harness) fingerprints a bare deck on the
frozen battery: no relics, no potions. That is the character's identity
anchor, but it is NOT what a real run feels like. For the calibration phase
we want the axes with the FULL power budget live -- drafted deck + accrued
relics + a potion belt -- so we can see where the character actually lands
once everything is on.

The axes are ratios against REF_IRONCLAD starter on the battery = 3.0, so we
keep that same baseline and measure the loaded character two ways (they
answer different questions; we show both):

  SURFACE 1 -- RUN FIGHTS. Pool the FightStats from the actual Act-1 run
  fights (relics + potions live, real roster, HP carrying, potions being
  spent, Fairy one-shot). Purest "in a real run." Caveat, stated not faked:
  A4 sustain here counts only IN-COMBAT heals (Blood Vial, blood potion,
  Encore) -- BETWEEN-fight run heals (Burning Blood, Regal Pillow, rest)
  live in the run economy and never touch a combat FightStats, so they do
  not show. And the real roster has no attrition/swarm/tank_boss pools, so
  A2/A3/A6 fall back to the pooled sample and read noisier than on the
  battery.

  SURFACE 2 -- BATTERY, FULL LOADOUT. Re-run the calibrated 5-encounter
  battery, but equip the player with a real run's drafted deck + that run's
  relics' combat effects + a potion belt (node_kind=elite so both the
  defensive AND offensive potion policies are live). Keeps the curated
  attrition/swarm/tank_boss pools intact, so the axes stay well-defined and
  directly comparable to 3.0 -- with everything on. Approximations, stated:
  relic max-HP pickups are not re-applied (battery uses base max HP), and
  each independent battery fight starts with a FRESH copy of the belt. Within
  a multi-stage gauntlet, however, HP/max HP and potion depletion carry from
  stage to stage just as they do in the existing battery contract.

Both surfaces are reported beside the bare-deck STARTER fingerprint, so the
lift from "identity" to "loaded" is legible per axis.
"""

from __future__ import annotations

import argparse
import sys

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.combat import run_fight
from tier0.harness import axes, metrics, runner
from tier0.pilot.policy import make_pilot
from tier05 import draft, model
from tier05 import relics as relic_pool

BASELINE = ("ref_ironclad", "starter")     # the 3.0 anchor, by construction


# ---------------------------------------------------------------------------
# Battery over an arbitrary drafted deck, optionally with a full loadout.
# Mirrors runner.run_battery but build_player_from_ids, and threads relic
# combat effects + a (fresh-per-independent-fight) potion belt through.
# ---------------------------------------------------------------------------

def _battery(character: str, card_ids: list[str], pilot, fights: int, seed: int,
             relic_effects=None, potions=None, potion_slots: int = C.POTION_SLOTS,
             node_kind: str = "") -> dict[str, list[metrics.FightStats]]:
    out: dict[str, list[metrics.FightStats]] = {}
    for enc in loader.encounter_ids():
        stages = loader.encounter_stages(enc)
        stats = []
        for i in range(fights):
            stage_stats = []
            carry_hp = None
            carry_max_hp = None
            carry_potions = None
            for stage in stages:
                # Each independent replicate starts with the reconstructed
                # belt. A gauntlet's later stages inherit what survived the
                # prior stage instead of silently refreshing consumables.
                stage_potions = (potions if carry_potions is None
                                  else carry_potions)
                player = loader.build_player_from_ids(
                    character, card_ids,
                    relic_effects=list(relic_effects) if relic_effects else None,
                    potions=(list(stage_potions)
                             if stage_potions is not None else None),
                    potion_slots=potion_slots, node_kind=node_kind)
                if carry_hp is not None:
                    player.max_hp = carry_max_hp
                    player.hp = carry_hp        # HP carries; deck/powers reset
                hp_start = player.hp
                state = run_fight(player, loader.build_encounter(stage), pilot,
                                  seed=seed + i)
                stage_stats.append(metrics.extract(state, hp_start))
                carry_hp = state.player.hp
                carry_max_hp = state.player.max_hp
                carry_potions = list(state.player.potions)
                if not state.player.alive:
                    break
            stats.append(metrics.merge_stages(stage_stats))
        out[enc] = stats
    return out


def _score(stats_by_enc, base_raw) -> dict[str, float]:
    return axes.normalize(axes.raw_axes(stats_by_enc), base_raw)


# ---------------------------------------------------------------------------
# Loadout reconstruction for surface 2.
# ---------------------------------------------------------------------------

def _boss_index(node_kinds: list[str]) -> int:
    for i in range(len(node_kinds) - 1, -1, -1):
        if node_kinds[i] == "B":
            return i
    return len(node_kinds) - 1


def _reached_boss(r) -> bool:
    bi = _boss_index(r.node_kinds)
    return r.won or (r.death_node is not None and r.death_node >= bi)


def _loadout(r, character: str, node_kind: str = "E"):
    """(deck, combat effects, belt, slots) in the requested fight context."""
    held = relic_pool.HeldRelics.hold(list(r.relics), character)
    relic_fx = held.combat_effects_for(node_kind, just_rested=False)
    slots = C.POTION_SLOTS + held.potion_slot_bonus()
    # A representative belt: what the run still held at the end, backfilled
    # with what it spent, truncated to the run's slot capacity.
    belt = (list(r.potions_end) + list(r.potions_used))[:slots]
    return list(r.deck_ids), relic_fx, belt, slots


# ---------------------------------------------------------------------------
# Aggregation helpers.
# ---------------------------------------------------------------------------

def _percentile(xs: list[float], q: float) -> float:
    if not xs:
        return 0.0
    s = sorted(xs)
    if len(s) == 1:
        return s[0]
    pos = q * (len(s) - 1)
    lo = int(pos)
    if lo + 1 >= len(s):
        return s[-1]
    return s[lo] + (pos - lo) * (s[lo + 1] - s[lo])


def evaluate(character: str, runs: int, sample: int, fights: int,
             seed: int) -> dict:
    pilot = make_pilot(loader.pilot_weights("generic"))
    base_raw = axes.raw_axes(
        runner.run_full_battery(*BASELINE, "generic", fights, seed))

    # Bare-deck STARTER reference (identity anchor), same battery/baseline.
    starter = _score(_battery(character, loader.starting_deck(character),
                              pilot, fights, seed), base_raw)

    # One realistic run set (everything ON) feeds BOTH surfaces.
    results = model.run_many(character, "generic", "generic",
                             draft.POLICIES["assigned"], runs, seed,
                             grant_relics=True, grant_potions=True,
                             n_acts=1)   # §10: Act-1 instrument, pinned --
    #                          the multi-act axis surface is a Pass-4 decision

    # --- SURFACE 1: pool every real run fight. -----------------------------
    run_fights = [s for r in results for s in r.fight_stats]
    surface1 = _score({"run": run_fights}, base_raw)
    s1_wins = sum(1 for r in results if r.won)

    # --- SURFACE 2: battery, per-run full loadout, aggregated. -------------
    loaded = [r for r in results if _reached_boss(r)]
    if len(loaded) > sample:
        stride = len(loaded) / sample
        loaded = [loaded[int(i * stride)] for i in range(sample)]
    per_axis: dict[str, list[float]] = {ax: [] for ax in axes.AXES}
    for r in loaded:
        deck, relic_fx, belt, slots = _loadout(r, character)
        sc = _score(_battery(character, deck, pilot, fights, seed,
                             relic_effects=relic_fx, potions=belt,
                             potion_slots=slots, node_kind="elite"), base_raw)
        for ax in axes.AXES:
            per_axis[ax].append(sc[ax])
    surface2_med = {ax: _percentile(per_axis[ax], 0.5) for ax in axes.AXES}
    surface2_p10 = {ax: _percentile(per_axis[ax], 0.10) for ax in axes.AXES}
    surface2_p90 = {ax: _percentile(per_axis[ax], 0.90) for ax in axes.AXES}

    return {
        "character": character,
        "n_runs": len(results), "n_run_fights": len(run_fights),
        "run_winrate": s1_wins / max(1, len(results)),
        "n_loadouts": len(loaded),
        "starter": starter, "surface1": surface1,
        "surface2_med": surface2_med, "s2_p10": surface2_p10,
        "s2_p90": surface2_p90,
        "s1_flags": axes.heuristic_flags(surface1),
        "s2_flags": axes.heuristic_flags(surface2_med),
    }


_LABELS = {
    "A1_frontload": "A1 Frontload", "A2_scaling": "A2 Scaling",
    "A3_block": "A3 Block econ", "A4_sustain": "A4 Sustain",
    "A5_velocity": "A5 Velocity", "A6_utility": "A6 Utility",
    "A7_setup_tax": "A7 Setup tax",
}


def _print(rep: dict) -> None:
    print(f"\n=== {rep['character']}: 7-axis scores, EVERYTHING ON "
          f"(REF_IRONCLAD starter = 3.0) ===")
    print(f"  runs {rep['n_runs']} (win {rep['run_winrate']:.0%}) | "
          f"surface-1 pool {rep['n_run_fights']} run fights | "
          f"surface-2 {rep['n_loadouts']} loaded batteries")
    print(f"  {'axis':<14} {'starter':>8} {'run-fights':>11} "
          f"{'battery+loadout med [p10-p90]':>30}")
    for ax in axes.AXES:
        st = rep["starter"][ax]
        s1 = rep["surface1"][ax]
        s2 = rep["surface2_med"][ax]
        p10, p90 = rep["s2_p10"][ax], rep["s2_p90"][ax]
        print(f"  {_LABELS[ax]:<14} {st:>8.1f} {s1:>11.1f} "
              f"{s2:>10.1f}  [{p10:.1f}-{p90:.1f}]")
    if rep["s1_flags"]:
        print("  run-fights flags:   " + " ; ".join(rep["s1_flags"]))
    if rep["s2_flags"]:
        print("  batt+loadout flags: " + " ; ".join(rep["s2_flags"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="7-axis scores with relics+potions+drafted deck ON.")
    ap.add_argument("--characters", nargs="+",
                    default=["ref_ironclad", "real_ironclad", "klee"])
    ap.add_argument("--runs", type=int, default=200,
                    help="realistic runs (grant relics+potions) played")
    ap.add_argument("--sample", type=int, default=20,
                    help="max loaded batteries fingerprinted (surface 2)")
    ap.add_argument("--fights", type=int, default=100,
                    help="battery fights per encounter per surface-2 loadout")
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    for ch in args.characters:
        _print(evaluate(ch, args.runs, args.sample, args.fights, args.seed))
