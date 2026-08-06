"""Probe (e)'s sim-side reading: tier0 run on the identical scripted sequence.

Registration: `docs/probe-e-corpse-detonation-registration-draft.md`, method
step 4 — "Read the sim's own behaviour on the identical scripted sequence, so
that the comparison is sim-vs-game on one script rather than game-vs-prose."
The `klee-mod/DECISIONS.md` prose describing the sim's behaviour is under an
`NC-18` question and is deliberately NOT consulted; this script reads the
behaviour off `tier0/engine/effects.py` by executing it.

Sequence (mirrors `understudy/probe_corpse.py`, both arms):
    place one Pop! bomb (5 damage, 1 bomb — confounder 4's stated magnitude)
    on the lowest-HP enemy, then hit it once with Kaboom! (7 damage).
    kill arm:    the target starts at 6 HP, so the hit kills it.
    control arm: the target starts at 20 HP, so the hit leaves it alive.

Read-only over tier0; no constant, card or rule is touched.

    python -m tools.probe_e_sim
"""

from __future__ import annotations

import random
import sys

from tier0.content import loader
from tier0.engine import effects
from tier0.engine.state import CombatState, Enemy

from understudy.replay import Names


def run_arm(names: Names, target_hp: int, label: str) -> dict:
    player = loader.build_player("klee")
    player.hand = []
    player.draw_pile = []
    player.discard_pile = []
    player.energy = 99
    target = Enemy(hp=target_hp, max_hp=max(target_hp, 20), name="target",
                   intents=[])
    other = Enemy(hp=50, max_hp=50, name="bystander", intents=[])
    state = CombatState(player=player, enemies=[target, other],
                        rng=random.Random(0), turn=1)
    pop = names.card("Pop!", played=True)
    kaboom = names.card("Kaboom!", played=True)
    assert pop is not None and kaboom is not None

    effects.resolve_card(state, pop)          # the bomb: a SKILL, not a hit
    after_bomb = {
        "target_bombs": len(target.bombs),
        "detonations": state.detonations_total,
        "sparks": player.sparks,
    }
    effects.resolve_card(state, kaboom)       # the blow
    after_blow = {
        "target_hp": target.hp,
        "target_alive": target.alive,
        "target_bombs": len(target.bombs),
        "detonations": state.detonations_total,
        "sparks": player.sparks,
        "bystander_hp": other.hp,
        "player_hp": player.hp,
    }
    row = {"arm": label, "target_hp_start": target_hp,
           "relic_hooks": sorted(player.relic_hooks),
           "after_bomb": after_bomb, "after_blow": after_blow}
    return row


def main() -> int:
    names = Names()
    for hp, label in ((6, "kill"), (20, "control")):
        row = run_arm(names, hp, label)
        print(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
