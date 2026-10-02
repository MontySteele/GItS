"""THE CO-OP PLAYTEST, 2026-09-30 (a guest played Kokomi): the sim half.

1. "Hydro doesn't always seem to apply -- possibly Plans." The sim ticks auras
   BEFORE the morning drain, so a Plan's Hydro lands whole. The mod ran its
   tick after the drain and now spares a morning hit's aura that one tick
   (`AuraPower.SpareThisTurnStartTick`); these pins hold the sim's side.
2. "Riptide and Vanguard both on the Plan gave 2 Energy instead of 3." Two
   Energy clauses on two entries add; the game log shows Second Thoughts was
   played after both, and it cancels the NEWEST Plan, which was Vanguard.
4. [USER]: "Riptide - buff the Draw from 1 to 2, and upgrades to 3".

The C# twin is `KleeTests/Prototype/KokomiCoopPlaytestFixesTests.cs`.
NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import inspect

import yaml

from tier0.content import loader, upgrades
from tier0.engine import combat, kokomi_plan, reactions
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import (  # noqa: F401
    kokomi_state, overhaul, plan_card)


def _row(cid):
    return loader.get_card(cid)


def _deck(st, n=6):
    st.player.draw_pile = [plan_card([], cid=f"proto_kk_f{i}")
                           for i in range(n)]


def test_the_sim_ticks_auras_before_the_morning_drain():
    """The order the C# spare reproduces: tick, then carry the Plans out."""
    src = inspect.getsource(combat._player_turn)
    assert (src.index("reactions.tick_auras(state)")
            < src.index("kokomi_plan.resolve_all(state)"))


def test_a_plan_hit_lands_a_whole_hydro_aura(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=60)])
    kokomi_plan.schedule(st, _row("proto_kk_nip"))
    kokomi_plan.resolve_all(st)
    enemy = st.enemies[0]
    assert enemy.aura == "hydro"
    assert enemy.aura_turns_left == reactions.aura_duration(st)


def test_riptide_and_vanguard_plans_pay_three_energy(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=60)])
    _deck(st)
    st.player.energy = 0
    kokomi_plan.schedule(st, _row("proto_kk_riptide"))
    kokomi_plan.schedule(st, _row("proto_kk_vanguard"))
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 3
    assert len(st.player.hand) == 2


QUIET = [{"kind": "block", "amount": 5}]


def _write(st, cid, energy=10):
    """Play a card onto the Bake-Kurage through the real play path."""
    card = _row(cid)
    st.player.energy = energy
    st.player.hand.append(card)
    combat.play_card(st, card)
    return card


# --- Kokomi follow-ups, 2026-10-01: a cancel is an undo ---------------------

def test_riptide_draws_two_and_three_upgraded(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=60)])
    _deck(st)
    kokomi_plan.schedule(st, upgrades.apply_upgrade(_row("proto_kk_riptide")))
    kokomi_plan.resolve_all(st)
    assert len(st.player.hand) == 3
