"""Curtain Call (R85): the two Track B powers current rows still apply.

  first_attack_draw    Quick Change -- first ATTACK play each turn
  cross_examination    Courtroom Drama -- first REACTION each turn

The Salon, Encore and shipped-sheet pins left with the shipped kits (legacy
cleanup stage 6).
"""

import random

from tier0.content import loader
from tier0.engine import combat, effects, reactions, resources
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy
import pytest



def furina_state(enemies=None, seed=0):
    p = loader.build_player("furina")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def _card(**kw):
    d = dict(id="cc_test", name="t", cost=0, type="skill",
             character="furina")
    d.update(kw)
    return Card(**d)



def test_quick_change_draws_on_first_attack_only():
    st = furina_state()
    p = st.player
    p.powers["first_attack_draw"] = 1
    p.draw_pile.extend(_card(id=f"filler{i}") for i in range(5))
    st.attacks_played_this_turn = 0
    swing = _card(type="attack", effects=[{"op": "damage", "amount": 3}])
    p.hand.append(swing)
    p.energy = 3
    before = len(p.hand)                         # includes the swing
    combat.play_card(st, swing)
    # played card left hand (-1), first-attack draw came in (+1)
    assert len(p.hand) == before
    swing2 = _card(id="cc_test2", type="attack",
                   effects=[{"op": "damage", "amount": 3}])
    p.hand.append(swing2)
    before = len(p.hand)
    combat.play_card(st, swing2)
    assert len(p.hand) == before - 1             # second attack: no draw


def test_cross_examination_debuffs_first_reaction_target_once():
    st = furina_state()
    p = st.player
    p.powers["cross_examination"] = 1
    e = st.enemies[0]
    st.reactions_this_turn = 0
    reactions.apply_aura(st, e, "hydro")
    reactions.resolve_hit(st, e, "pyro", 5)      # vaporize: first reaction
    assert e.powers.get("vulnerable", 0) >= 1
    assert e.powers.get("weak", 0) >= 1
    v, w = e.powers["vulnerable"], e.powers["weak"]
    reactions.apply_aura(st, e, "hydro")
    reactions.resolve_hit(st, e, "pyro", 5)      # second reaction: latched
    assert e.powers["vulnerable"] == v and e.powers["weak"] == w

