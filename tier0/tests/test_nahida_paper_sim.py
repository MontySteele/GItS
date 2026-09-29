"""The Nahida paper sim (exploratory, 2026-09-29): switched off it is
invisible, and switched on it plays the rules the paper and the Dendro
ruling wrote.

`tier0/engine/dendro.py`, `tier0/engine/nahida_seeds.py`,
`tier0/pilot/nahida.py`, `tier0/harness/exp_nahida_paper.py`. Nothing here
pins a balance number: the card numbers are the paper's placeholders.
"""

from __future__ import annotations

import hashlib
import json
import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, dendro, effects, nahida_seeds as ns, reactions
from tier0.engine.combat import run_fight
from tier0.engine.state import CombatState, Enemy
from tier0.pilot.nahida import make_nahida_pilot
from tier0.pilot.policy import make_pilot


def _digest(state) -> str:
    return hashlib.sha256(json.dumps(state.log, sort_keys=True, default=str)
                          .encode("utf-8")).hexdigest()


def _klee_fight():
    pilot = make_pilot(loader.pilot_weights("demolition"))
    return run_fight(loader.build_player("klee"),
                     loader.build_encounter("punisher"), pilot, seed=7)


@pytest.fixture
def world():
    ns.enable()
    try:
        yield
    finally:
        ns.disable()


# --- 1. OFF IS INVISIBLE -------------------------------------------------------

def test_both_switches_ship_off():
    assert ns.NAHIDA_PAPER is False
    assert dendro.DENDRO_ENGINE is False
    assert not reactions.REACTION_LISTENERS
    assert not any(op.startswith("nahida_") for op in effects.OPS)
    assert "dendro" not in reactions.AURA_ELEMENTS


def test_the_pinned_klee_fight_is_unchanged_off_and_after_a_round_trip():
    """`test_klee_overhaul`'s literal: the reaction layer's refactor (one
    `note_reaction`, the Dendro branch) moves nothing with the switch off,
    and enabling then disabling leaves nothing behind."""
    pinned = "20b877d3411ccdc5306f6b8c0664c8d0f0dd7f9b30421d73af411aa8c3dbe9fa"
    assert _digest(_klee_fight()) == pinned
    ns.enable()
    ns.disable()
    assert _digest(_klee_fight()) == pinned
    assert not reactions.REACTION_LISTENERS


# --- 2. DENDRO, AS RULED ----------------------------------------------------------

def _state(*hps):
    p = ns.build_player([], relic=False)
    enemies = [Enemy(hp=h, max_hp=h, name=f"e{i}",
                     intents=[{"kind": "attack", "amount": 10}])
               for i, h in enumerate(hps)]
    st = CombatState(player=p, enemies=enemies, rng=random.Random(1))
    st.turn = 1
    return st


def _hit(st, e, element, dmg=0):
    return reactions.resolve_hit(st, e, element, dmg)


def test_bloom_leaves_a_core_that_bursts_at_the_end_of_the_next_turn(world):
    st = _state(50)
    e = st.enemies[0]
    _hit(st, e, "hydro")
    _hit(st, e, "dendro")
    assert e.aura is None and dendro.of(st, e).cores == [1]
    dendro.turn_end(st)                      # end of the Bloom's own turn
    assert e.hp == 50
    st.turn = 2
    dendro.turn_end(st)                      # end of the next turn
    assert e.hp == 50 - dendro.CORE_BURST and not dendro.of(st, e).cores


def test_pyro_burgeons_to_every_enemy_and_electro_hyperblooms_one(world):
    st = _state(50, 50)
    a, b = st.enemies
    _hit(st, a, "hydro"); _hit(st, a, "dendro")
    _hit(st, a, "pyro")
    assert (a.hp, b.hp) == (44, 44)
    _hit(st, b, "hydro"); _hit(st, b, "dendro")
    _hit(st, b, "electro")
    assert b.hp == 44 - 12


def test_quicken_adds_three_to_dendro_and_electro_hits_only(world):
    st = _state(50)
    e = st.enemies[0]
    _hit(st, e, "electro"); _hit(st, e, "dendro")
    assert dendro.of(st, e).quicken == dendro.QUICKEN_TURNS
    assert _hit(st, e, "dendro", 5) == 8
    assert _hit(st, e, "hydro", 5) == 5


def test_cryo_and_dendro_do_not_react_and_the_aura_stands(world):
    st = _state(50)
    e = st.enemies[0]
    _hit(st, e, "cryo"); _hit(st, e, "dendro")
    assert e.aura == "cryo" and st.reactions_this_turn == 0


def test_burning_holds_pyro_and_a_hydro_hit_ends_it(world):
    st = _state(50)
    e = st.enemies[0]
    _hit(st, e, "pyro"); _hit(st, e, "dendro")
    assert e.aura == "pyro" and dendro.of(st, e).burning == 3
    dendro.turn_end(st)
    assert e.hp == 50 - dendro.BURNING_DOT
    _hit(st, e, "hydro")                     # Vaporize consumes the held Pyro
    assert dendro.of(st, e).burning == 0


# --- 3. SEEDS AND PURIFICATION -------------------------------------------------------

def test_purification_fires_once_a_turn_from_reactions(world):
    st = _state(50, 50)
    a, b = st.enemies
    ns.add_seed(st, a, 2)
    for e in (a, b):
        _hit(st, e, "hydro")
    _hit(st, a, "dendro")                    # Bloom on a seeded enemy
    _hit(st, b, "dendro")                    # b is unseeded: no trigger
    ns.flush(st)
    assert a.hp == 50 - 4                     # 2 per Seed x 2
    ns.add_seed(st, b, 1)
    _hit(st, b, "electro"); _hit(st, b, "dendro")  # Quicken, seeded
    ns.flush(st)
    assert a.hp == 46                         # the turn's trigger is spent
    ns.turn_start(st)
    ns.field_of(st).powers["mandate"] = 1
    assert ns.trigger_cap(st) == 2


def test_akasha_puts_the_second_seed_on_another_enemy(world):
    st = ns.build_player([], relic=True)
    state = CombatState(player=st, enemies=[
        Enemy(hp=30, max_hp=30, name="a", intents=[{"kind": "attack", "amount": 5}]),
        Enemy(hp=40, max_hp=40, name="b", intents=[{"kind": "attack", "amount": 5}])],
        rng=random.Random(1))
    ns.field_of(state).chooser = make_nahida_pilot("spread")
    ns.add_seed(state, state.enemies[0], 1)
    ns.add_seed(state, state.enemies[0], 1)
    assert [ns.seeds(state, e) for e in state.enemies] == [2, 1]


def test_the_papers_worked_foresight_turn():
    """Paper sec.5: both Seeds on the attacker -> its 14 lands as 12 and
    Purify deals it 4; one each -> 13, and 2 to each enemy."""
    from tier0.harness.exp_nahida_paper import foresight_turn
    r = foresight_turn()
    assert r["both_on_attacker"]["attacker_hit_landed"] == 12
    assert r["both_on_attacker"]["purify_to_attacker"] == 4
    assert r["one_each"]["attacker_hit_landed"] == 13
    assert (r["one_each"]["purify_to_attacker"],
            r["one_each"]["purify_to_buffer"]) == (2, 2)
    assert not ns.NAHIDA_PAPER


def test_a_nahida_fight_runs_and_the_switch_comes_back_off():
    from tier0.harness import exp_nahida_paper as X
    with X.nahida_world():
        recs = X.run_nahida(X.SEEDBED, "swarm", "spread", n=3)
    assert len(recs) == 3 and all(r.turns > 0 for r in recs)
    assert not ns.NAHIDA_PAPER and not dendro.DENDRO_ENGINE
    assert C.SWIRL_PAYS is False
