"""Furina sheet pass 1 — the pre-registered experiment battery.

Three blocks, all registered in furina-sheet-pass-1-plan.md before running
(null results binding):

A. SPOTLIGHT BASELINE DELTA (DECISIONS 63, mandatory): winrate of her
   decks with the Ethereal Spotlight relic enabled vs disabled, in points.
   Also produces the §8 acceptance-criteria numbers: self-carry vs the
   real archetypes (criterion 1) and the companions-only delete-test probe
   (criterion 2).

B. EP + GS COMBAT-COUPLED (DECISIONS 64, ONE experiment): drafted decks
   from the real offer stream, then real fights. Measures (i) whether
   Encore Performance separates the committed archetype's median from its
   ceiling, and (ii) the Guest Star draw-variance floor that offer
   geometry cannot see.

C. PLACEHOLDER SWEEPS (redpen ruling c): FANFARE_CAP_FRACTION and
   SPOTLIGHT_SELF_MULT swept for the user's pick. The stamped defaults do
   not move; the sweep monkeypatches per cell and restores.

Usage: python -m tier05.exp_furina_sheetpass
Seed 20260720 throughout; deterministic.
"""

from __future__ import annotations

import random
import statistics
from collections import defaultdict

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.combat import run_fight
from tier0.harness import metrics
from tier0.pilot.policy import make_pilot
from tier05.rewards import _nation_weighted_choice, _roll_rarity, companion_pool

SEED = 20260720
FIGHTS = 1000
ENCOUNTERS = ("punisher", "swarm", "attrition", "tank_boss")


def _battery(deck: str, pilot_id: str, strip_relic: bool, fights: int,
             seed: int) -> dict[str, float]:
    """Winrate per encounter for a Furina package, optionally without the
    Ethereal Spotlight relic (no selector ever arrives -> no designation
    -> the baseline multiplier never fires)."""
    pilot = make_pilot(loader.pilot_weights(pilot_id))
    out = {}
    for enc in ENCOUNTERS:
        wins = 0
        for i in range(fights):
            player = loader.build_player("furina", deck)
            if strip_relic:
                player.relic_hooks = [h for h in player.relic_hooks
                                      if h != "ethereal_spotlight"]
            state = run_fight(player, loader.build_encounter(enc), pilot,
                              seed=seed + i)
            s = metrics.extract(state, player.max_hp)
            wins += s.won
        out[enc] = wins / fights
    return out


def block_a() -> None:
    print("=" * 72)
    print("A. SPOTLIGHT BASELINE DELTA (relic on vs off; 1000 fights/cell)")
    print("=" * 72)
    configs = [("salon_weighted", "salon"), ("spotlight_weighted", "spotlight"),
               ("fanfare_weighted", "fanfare"), ("self_carry", "fanfare"),
               ("spotlight_companions_only", "spotlight")]
    results = {}
    for deck, pilot in configs:
        on = _battery(deck, pilot, strip_relic=False, fights=FIGHTS, seed=SEED)
        off = _battery(deck, pilot, strip_relic=True, fights=FIGHTS, seed=SEED)
        results[deck] = (on, off)
        row = "  ".join(f"{enc}: {on[enc]:.1%} vs {off[enc]:.1%} "
                        f"({(on[enc] - off[enc]) * 100:+.1f}pt)"
                        for enc in ENCOUNTERS)
        print(f"{deck:<28} {row}")
    print()
    avg = {d: statistics.mean((results[d][0][e] - results[d][1][e])
                              for e in ENCOUNTERS) * 100 for d, _ in configs}
    for d, delta in avg.items():
        print(f"  mean baseline delta {d:<28} {delta:+.1f}pt")
    print("\n  §8 criterion 1 (self-carry must NOT beat the archetypes at "
          "median):")
    for enc in ENCOUNTERS:
        sc = results["self_carry"][0][enc]
        sa = results["salon_weighted"][0][enc]
        sp = results["spotlight_weighted"][0][enc]
        verdict = "OK" if sc <= max(sa, sp) else "VIOLATION"
        print(f"    {enc:<12} self_carry {sc:.1%}  salon {sa:.1%}  "
              f"spotlight {sp:.1%}  -> {verdict}")
    print("\n  §8 criterion 2 delete-test (companions-only probe vs the "
          "full Spotlight deck):")
    for enc in ENCOUNTERS:
        full = results["spotlight_weighted"][0][enc]
        probe = results["spotlight_companions_only"][0][enc]
        print(f"    {enc:<12} full {full:.1%}  companions-only {probe:.1%} "
              f"({(full - probe) * 100:+.1f}pt of the win is her cards)")


# ---------------------------------------------------------------------------

KIT = ("chevreuse_interdiction_fire", "chevreuse_vanguards_valor",
       "chevreuse_bursting_grenades")
SCREENS = 10
RUNS = 400
EP_CARDS = ["encore_performance"]
GS_CARDS = ["an_invitation", "guest_list"]
# ARCHIVE NOTE (pass 2): the R16 re-author replaced warm_reception /
# props_department (limelight / stage_lights). The pass-1 REPORT is this
# experiment's archive; a re-run measures the CURRENT sheet, not pass 1.
# Fillers updated to existing ids so the script still executes.
FILLER_PRIORITY = ("graceful_retreat", "limelight", "shared_billing",
                   "stage_lights", "swelling_overture")


def _draft_committed(rng: random.Random) -> list[str]:
    """The sprint-1 committed strategy, on the real reward primitives:
    take every Chevreuse-kit offer from the companion slot; fill a few
    generic slots from her own pool by fixed priority (crude but uniform
    across arms — the arms differ ONLY in the appended machinery)."""
    taken = []
    comps = companion_pool()
    for _ in range(SCREENS):
        rarity = _roll_rarity(rng)
        while rarity not in comps:
            rarity = {"rare": "uncommon", "uncommon": "common"}[rarity]
        pool = [c for c in comps[rarity]
                if c.personal_pool in (None, "furina")]
        offer = _nation_weighted_choice(rng, pool, "fontaine")
        if offer.id in KIT:
            taken.append(offer.id)
    return taken


def block_b() -> None:
    print()
    print("=" * 72)
    print(f"B. EP + GS COMBAT-COUPLED ({RUNS} runs x {len(ENCOUNTERS)} "
          f"fights; committed Chevreuse strategy)")
    print("=" * 72)
    arms = {
        "base": [],
        "+EP": EP_CARDS,
        "+GS": GS_CARDS,
        "+EP+GS": EP_CARDS + GS_CARDS,
    }
    pilot = make_pilot(loader.pilot_weights("spotlight"))
    winrates: dict[str, list[float]] = defaultdict(list)
    spotlight_played: dict[str, list[int]] = defaultdict(list)
    depth_seen = []
    rng = random.Random(SEED)
    for r in range(RUNS):
        drafted = _draft_committed(rng)
        depth_seen.append(len(drafted))
        filler = list(FILLER_PRIORITY[:max(0, 6 - len(drafted))])
        for arm, extra in arms.items():
            deck_ids = drafted + filler + extra
            wins, sp_played = 0, 0
            for j, enc in enumerate(ENCOUNTERS):
                player = loader.build_player_from_ids("furina",
                    loader.starting_deck("furina") + deck_ids)
                state = run_fight(player, loader.build_encounter(enc), pilot,
                                  seed=SEED + r * 31 + j)
                wins += int(bool(state.player.alive)
                            and not state.living_enemies)
                sp_played += sum(1 for e in state.log
                                 if e["event"] == "spotlight_card_played")
            winrates[arm].append(wins / len(ENCOUNTERS))
            spotlight_played[arm].append(sp_played)
    print(f"  drafted Chevreuse depth: median "
          f"{statistics.median(depth_seen)}, mean "
          f"{statistics.mean(depth_seen):.2f}\n")
    print(f"  {'arm':<8} {'median WR':>10} {'mean WR':>9} {'P90 WR':>8} "
          f"{'spotlighted plays/run':>22}")
    for arm in arms:
        w = sorted(winrates[arm])
        p90 = w[int(0.9 * (len(w) - 1))]
        print(f"  {arm:<8} {statistics.median(w):>10.3f} "
              f"{statistics.mean(w):>9.3f} {p90:>8.3f} "
              f"{statistics.mean(spotlight_played[arm]):>22.2f}")
    print("\n  Registration (i) duplication median-vs-ceiling: compare +EP "
          "median lift vs P90 lift over base.")
    print("  Registration (ii) GS draw-variance floor: +GS spotlighted "
          "plays/run vs base, and its winrate delta.")


# ---------------------------------------------------------------------------

def block_c() -> None:
    print()
    print("=" * 72)
    print("C. PLACEHOLDER SWEEPS (500 fights/cell; stamped defaults do not "
          "move)")
    print("=" * 72)
    print("\n  C1. FANFARE_CAP_FRACTION (fanfare_weighted, the deck the cap "
          "binds):")
    default_cap = C.FANFARE_CAP_FRACTION
    for frac in (0.25, 0.5, 0.75):
        C.FANFARE_CAP_FRACTION = frac
        wr = _battery("fanfare_weighted", "fanfare", strip_relic=False,
                      fights=500, seed=SEED)
        row = "  ".join(f"{e}: {wr[e]:.1%}" for e in ENCOUNTERS)
        mark = "  <- stamped default" if frac == default_cap else ""
        print(f"    cap {frac:.2f}x maxHP   {row}{mark}")
    C.FANFARE_CAP_FRACTION = default_cap

    print("\n  C2. SPOTLIGHT_SELF_MULT (self_carry, the deck the self-rate "
          "governs):")
    default_self = C.SPOTLIGHT_SELF_MULT
    for mult in (1.0, 1.25, 1.5):
        C.SPOTLIGHT_SELF_MULT = mult
        wr = _battery("self_carry", "fanfare", strip_relic=False,
                      fights=500, seed=SEED)
        row = "  ".join(f"{e}: {wr[e]:.1%}" for e in ENCOUNTERS)
        mark = "  <- stamped default" if mult == default_self else ""
        print(f"    self-rate {mult:.2f}x   {row}{mark}")
    C.SPOTLIGHT_SELF_MULT = default_self


if __name__ == "__main__":
    block_a()
    block_b()
    block_c()
