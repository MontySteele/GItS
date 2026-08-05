"""Track O, slice 12 -- fixture for the Track H aura/payoff counters.

Synthetic FightStats only: no game, no RNG, no content load. Drive with

    PYTHONPATH=. python review/redteam/fixtures/track_o/s12-pooling-fixture.py

Three axes, in order:

  S12-1  aura_ops and aura_applications are not on one scale, and the declared
         source label `swirl_op` is unreachable by construction.
  S12-2  absent / zero / untracked all render as the same 0 in every scalar
         Track H column.
  S12-3  THE HEADLINE. `run_battery` merges the two combats of the `gauntlet`
         encounter into ONE FightStats before any aggregate sees it, so
         `aura_profile`'s and `summarize`'s per-fight rates carry a different
         unit on that encounter than on the other five -- and the battery-wide
         row pools the two units together.
"""
from __future__ import annotations

import copy
import sys

from tier0.harness import metrics


def fight(*, turns, apps_by_source=None, ops=None, reactions=0,
          cond_eval=None, cond_fired=None, wasted=0, damage=0):
    """One COMBAT's worth of Track H counters. Everything else is inert."""
    return metrics.FightStats(
        won=True, turns=turns, hp_start=80, hp_end=80,
        total_damage_dealt=damage, damage_by_turn={}, energy_by_turn={},
        total_block_gained=0, damage_blocked=0, energy_spent=0,
        cards_drawn_extra=0, energy_generated_extra=0, healing=0,
        encore_absorbed=0, debuff_stacks_applied=0, debuffed_intents=0,
        aura_intents=0, total_intents=0, reactions=reactions,
        reaction_damage=0, auras_wasted=wasted,
        aura_ops=dict(ops or {}),
        aura_applications_by_source=dict(apps_by_source or {}),
        aura_applications_by_element={
            "pyro": sum((apps_by_source or {}).values())},
        conditional_evaluated=dict(cond_eval or {}),
        conditional_fired=dict(cond_fired or {}))


# --------------------------------------------------------------------------
# S12-3: the two-combat gauntlet, both granularities.
# --------------------------------------------------------------------------
# Stage 1 of a gauntlet: four auras land, one reaction, a payoff rider is
# evaluated twice. Stage 2: the deck bricks -- no aura, no reaction at all.
STAGE_1 = fight(turns=5, apps_by_source={"hit": 4}, ops={"apply_aura": 2},
                reactions=1, wasted=1,
                cond_eval={"reaction_triggered_by_this": 2},
                cond_fired={"reaction_triggered_by_this": 1})
STAGE_2 = fight(turns=5, apps_by_source={}, ops={}, reactions=0, wasted=0,
                cond_eval={}, cond_fired={})


def main() -> int:
    combats = [copy.deepcopy(STAGE_1), copy.deepcopy(STAGE_2)]
    merged = [metrics.merge_stages([copy.deepcopy(STAGE_1),
                                    copy.deepcopy(STAGE_2)])]

    pc, pm = metrics.aura_profile(combats), metrics.aura_profile(merged)
    sc, sm = metrics.summarize(combats), metrics.summarize(merged)
    qc, qm = metrics.payoff_profile(combats), metrics.payoff_profile(merged)

    print("S12-3  one gauntlet = two combats, merged into one FightStats")
    print(f"  applications_per_fight   REPORTED {pm['applications_per_fight']:.4f}"
          f"   TRUE per-combat {pc['applications_per_fight']:.4f}")
    print(f"  aura_ops_per_fight       REPORTED {pm['aura_ops_per_fight']:.4f}"
          f"   TRUE per-combat {pc['aura_ops_per_fight']:.4f}")
    print(f"  auras_wasted_per_fight   REPORTED {sm['auras_wasted_per_fight']:.4f}"
          f"   TRUE per-combat {sc['auras_wasted_per_fight']:.4f}")
    print(f"  aura_starved_fights      REPORTED {sm['aura_starved_fights']:.4f}"
          f"   TRUE per-combat {sc['aura_starved_fights']:.4f}")
    print(f"  fights_with_any_aura     REPORTED {pm['fights_with_any_aura']}"
          f"/{len(merged)}   TRUE {pc['fights_with_any_aura']}/{len(combats)}")
    k = "reaction_triggered_by_this"
    print(f"  evaluated_per_fight[{k}]  REPORTED "
          f"{qm['by_predicate'][k]['evaluated_per_fight']:.4f}   TRUE "
          f"{qc['by_predicate'][k]['evaluated_per_fight']:.4f}")
    print("  (pooled COUNTS are identical; only the /fight and /fights"
          " figures move)")

    # ----------------------------------------------------------------------
    # S12-2: absent vs zero vs untracked
    # ----------------------------------------------------------------------
    print("\nS12-2  absent / zero / untracked all read as 0")
    for label, s in (("aura verbs in deck, none resolved",
                      fight(turns=3, ops={}, apps_by_source={"hit": 2})),
                     ("no aura verb exists in the deck",
                      fight(turns=3, ops={}, apps_by_source={"hit": 2})),
                     ("swirl resolved, landed nothing",
                      fight(turns=3, ops={"swirl": 3},
                            apps_by_source={"hit": 2}))):
        print(f"  {label:38} aura_ops scalar = {sum(s.aura_ops.values())}"
              f"  by-key dict = {s.aura_ops}")
    print("  -> the first two rows are indistinguishable in every scalar"
          " column (runner.py CSV `aura_ops`, exp_reactions_corpus"
          " `aura_ops_total`), and the dict distinguishes them only by"
          " ABSENCE, never by an explicit 0.")

    # ----------------------------------------------------------------------
    # S12-1: aura_ops is not a denominator for applications
    # ----------------------------------------------------------------------
    print("\nS12-1  aura_ops vs applications are different units")
    swarm = fight(turns=4, ops={"swirl": 4},
                  apps_by_source={"swirl_spread": 12})
    p = metrics.aura_profile([swarm])
    print(f"  one swirl op onto 3 bodies x4: ops={p['aura_ops_total']} "
          f"applications={p['applications']} -> apps/op="
          f"{p['applications'] / p['aura_ops_total']:.2f}")
    print("  `swirl_op` is a DECLARED source (metrics.py:108, tier0/README"
          " l.72) that can never be recorded: effects.py:957 passes it with"
          " element='anemo' and reactions.apply_aura returns early for any"
          " element outside AURA_ELEMENTS (reactions.py:60-62).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
