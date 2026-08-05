"""Track O / slice 08 reproducer 1.

D1's `reaction_damage_amp` is read off the `reaction` event's `amp_delta`,
which `reactions._react` computes as `out - damage` at the moment the aura is
consumed -- which is BEFORE the rest of `effects.deal_damage_to_enemy`'s
multiplier chain (Vulnerable, Slow, refpowers' DoubleDamage...) scales the
already-amplified hit.

The corpus declares one direction of this ("amp over-reads on overkill and on
blocked hits", docs/reactions-corpus-2026-08-05.md sec.1). It does not declare
the other: every multiplicative modifier that lands AFTER the reaction scales
the amp's contribution too, and none of that uplift reaches the amp bucket.

Run:  PYTHONPATH=. python review/redteam/fixtures/track_o/s08-amp-before-multipliers.py
"""
from __future__ import annotations

import random

from tier0.engine import effects, powers, reactions
from tier0.engine.state import CombatState, Enemy, Player
from tier0.harness import metrics


def _state(hp=10_000):
    return CombatState(player=Player(hp=80, max_hp=80),
                       enemies=[Enemy(hp=hp, max_hp=hp, name="dummy",
                                      intents=[{"kind": "attack",
                                                "amount": 0}])],
                       rng=random.Random(0))


BASE = 20


def measured(vulnerable: int) -> dict:
    st = _state()
    e = st.enemies[0]
    reactions.apply_aura(st, e, "hydro")            # set the aura up
    if vulnerable:
        powers.apply_power(st, e, "vulnerable", vulnerable)
    effects.deal_damage_to_enemy(st, e, BASE, element="pyro", source="attack")
    s = metrics.extract(st, hp_start=80)
    return {"all": s.damage_all_ops, "amp": s.reaction_damage_amp,
            "base_ops": s.damage_from_base_ops,
            "share": round(s.reaction_share, 4)}


def counterfactual(vulnerable: int) -> int:
    """The same hit with NO aura on the enemy: what the deck would have dealt
    without the reaction. all - this is the reaction's true contribution."""
    st = _state()
    e = st.enemies[0]
    if vulnerable:
        powers.apply_power(st, e, "vulnerable", vulnerable)
    effects.deal_damage_to_enemy(st, e, BASE, element="pyro", source="attack")
    return metrics.extract(st, hp_start=80).damage_all_ops


def main() -> None:
    for vuln in (0, 2):
        got = measured(vuln)
        no_react = counterfactual(vuln)
        truth = got["all"] - no_react
        tag = "vulnerable" if vuln else "clean"
        print(f"[{tag}] base hit {BASE} pyro into a hydro aura")
        print(f"    total damage dealt      {got['all']}")
        print(f"    same hit, no aura       {no_react}")
        print(f"    reaction's TRUE uplift  {truth}")
        print(f"    D1 reaction_damage_amp  {got['amp']}"
              f"   <-- reported")
        print(f"    D1 damage_from_base_ops {got['base_ops']}"
              f"   (true base = {no_react})")
        print(f"    D1 reaction_share       {got['share']}"
              f"   (true = {round(truth / got['all'], 4)})")
        print()


if __name__ == "__main__":
    main()
