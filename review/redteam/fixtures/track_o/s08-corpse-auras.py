"""Track O / slice 08 reproducer 4 -- H1's `aura_applications` counts the
auras a KILLING BLOW puts on a corpse.

Mechanism (the mirror image of Family A). `effects.deal_damage_to_enemy` calls
`reactions.resolve_hit` at line 363 -- BEFORE the hit is applied to HP at line
382. An element-tagged hit on a clean enemy therefore emits `aura_applied`
while the enemy is still alive, and the very next statement kills it. The aura
is on a corpse: it can never react, it can never be refreshed, and
`reactions.tick_auras` walks `state.living_enemies` only, so it is never
recorded as `aura_wasted` either.

`aura_applications` / `aura_applications_by_source` / `..._by_element` are the
published H1 numerator (docs/reactions-corpus-2026-08-05.md sec.2, "aura
apps/fight", and sec.2.2's provenance table). Nothing in the corpus or in
`metrics.py` declares that a share of that numerator landed on dead bodies.

Part A proves the mechanism on one hit. Part B measures the rate over real
decks and the real pilot (own enemies, so names are unique and per-body HP can
be reconstructed exactly -- `damage.amount` is already overkill-clamped, so a
body's damage events sum to its max HP exactly when it dies).

Run:  PYTHONPATH=. python review/redteam/fixtures/track_o/s08-corpse-auras.py
"""
from __future__ import annotations

import random

from tier0.content import loader
from tier0.engine import effects
from tier0.engine.combat import run_fight
from tier0.engine.state import CombatState, Enemy, Player
from tier0.harness import metrics
from tier0.pilot.policy import make_pilot


def part_a() -> None:
    e = Enemy(hp=5, max_hp=5, name="doomed",
              intents=[{"kind": "attack", "amount": 0}])
    st = CombatState(player=Player(hp=80, max_hp=80), enemies=[e],
                     rng=random.Random(0))
    effects.deal_damage_to_enemy(st, e, 12, element="pyro", source="attack")
    s = metrics.extract(st, hp_start=80)
    print("A. one pyro hit for 12 into a clean 5 HP body")
    print(f"    enemy alive after   : {e.alive}   (hp {e.hp})")
    print(f"    enemy.aura          : {e.aura!r}  <- an aura on a corpse")
    print(f"    H1 aura_applications: {s.aura_applications} "
          f"{s.aura_applications_by_source}")
    print(f"    auras_wasted        : {s.auras_wasted}  "
          f"(tick_auras walks living_enemies only)")
    print()


ARMS = [("klee", "reaction_weighted", "reaction"),
        ("klee", "demolition_weighted", "demolition"),
        ("furina", "spotlight_weighted", "spotlight"),
        ("kokomi", "commander_weighted", "commander")]


def _enemies(n=3, hp=40):
    return [Enemy(hp=hp, max_hp=hp, name=f"body{i}",
                  intents=[{"kind": "attack", "amount": 6}])
            for i in range(n)]


def _corpse_auras(state) -> tuple[int, int]:
    """(corpse auras, all aura applications) for one finished fight."""
    caps = {e.name: e.max_hp for e in state.enemies}
    taken: dict[str, int] = {}
    corpse = total = 0
    log = state.log
    for i, ev in enumerate(log):
        if ev["event"] == "damage" and ev.get("target") in caps:
            taken[ev["target"]] = taken.get(ev["target"], 0) + ev["amount"]
        elif ev["event"] == "aura_applied":
            total += 1
            # The hit's own `damage` emit is the next event on this path.
            nxt = log[i + 1] if i + 1 < len(log) else None
            if (nxt and nxt["event"] == "damage"
                    and nxt.get("target") == ev["target"]
                    and (taken.get(ev["target"], 0) + nxt["amount"]
                         >= caps[ev["target"]])):
                corpse += 1
    return corpse, total


def part_b(fights=300, seed=20260805) -> None:
    print(f"B. {fights} fights per arm, 3 bodies of 40 HP, real deck + pilot")
    print(f"    {'arm':<34} {'aura apps':>10} {'on corpses':>11} {'share':>7}")
    for character, deck, pilot_id in ARMS:
        pilot = make_pilot(loader.pilot_weights(pilot_id))
        corpse = total = 0
        for i in range(fights):
            player = loader.build_player(character, deck)
            st = run_fight(player, _enemies(), pilot, seed=seed + i)
            c, t = _corpse_auras(st)
            corpse += c
            total += t
        share = corpse / max(1, total)
        print(f"    {character + '/' + deck:<34} {total:>10} {corpse:>11} "
              f"{share:>7.1%}")


if __name__ == "__main__":
    part_a()
    part_b()
