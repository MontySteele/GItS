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


def test_second_thoughts_after_both_cancels_vanguard(overhaul):
    """The playtest's turn: Riptide, Vanguard, Second Thoughts. Vanguard is
    the last Plan; the morning pays Riptide's 2 Energy alone."""
    st = kokomi_state(enemies=[make_enemy(hp=60)])
    _deck(st)
    kokomi_plan.schedule(st, _row("proto_kk_riptide"))
    kokomi_plan.schedule(st, _row("proto_kk_vanguard"))
    kokomi_plan.cancel_last_plan(st)
    assert [e.card_id for e in st.kk_plan_queue] == ["proto_kk_riptide"]
    st.player.energy = 0
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 2


# --- Kokomi follow-ups, 2026-10-01: a cancel is an undo ---------------------

def test_a_cancelled_exhaust_plan_comes_back_to_the_hand(overhaul):
    """Main session: "Exhaust applies when the card is played normally or
    its Plan is carried out, not when it is cancelled." Vanguard (0, Exhaust)
    written for real sits in the exhaust pile; Second Thoughts brings it back."""
    st = kokomi_state(enemies=[make_enemy(hp=60, intents=QUIET)])
    _deck(st)
    vanguard = _write(st, "proto_kk_vanguard")
    assert [e.card_id for e in st.kk_plan_queue] == ["proto_kk_vanguard"]
    assert vanguard in st.player.exhaust_pile
    kokomi_plan.cancel_last_plan(st)
    assert st.kk_plan_queue == []
    assert vanguard in st.player.hand
    assert vanguard not in st.player.exhaust_pile


def test_all_streams_gives_every_card_back_exhaust_too(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])
    _deck(st)
    vanguard = _write(st, "proto_kk_vanguard")
    riptide = _write(st, "proto_kk_riptide")
    assert len(st.kk_plan_queue) == 2
    kokomi_plan.all_streams(st)
    assert st.kk_plan_queue == []
    assert vanguard in st.player.hand and riptide in st.player.hand
    assert vanguard not in st.player.exhaust_pile
    assert riptide not in st.player.discard_pile
    assert st.kk_next_plan_extra == 2


def test_the_cancel_row_says_the_cards_come_back(overhaul):
    # Second Thoughts left the pool in the payoff pass (2026-10-01); its
    # `cancel_last_plan` op stays, exercised directly above.
    rows = {r["id"]: r for r in yaml.safe_load(
        loader.PROTOTYPE_SHEET.read_text(encoding="utf-8"))}
    assert "proto_kk_second_thoughts" not in rows
    assert "take their cards back" in rows[
        "proto_kk_all_streams_flow_to_the_sea"]["description"]
    assert _row("proto_kk_all_streams_flow_to_the_sea").exhaust


def test_riptide_draws_two_and_three_upgraded(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=60)])
    _deck(st)
    kokomi_plan.schedule(st, upgrades.apply_upgrade(_row("proto_kk_riptide")))
    kokomi_plan.resolve_all(st)
    assert len(st.player.hand) == 3
