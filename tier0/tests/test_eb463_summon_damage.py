"""`EB-463` / `EB-565`: a summon banks the damage its card prints.

A row whose whole body is `apply_power` prints a number the POWER deals
LATER. The sheet grammar `apply_power: summon_damage:` carries that number from
the card to the power, snapshotted at PLAY (R72), because the power fires turns
later when the card is gone. (It was found through the shipped Guest Cast fold,
Furina r8 (c) 1 and r14 lane 2 (c) 2; the Spotlight left the sim on 2026-10-08
and its fold with it, so what is pinned here is the banked printed number.)

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects
from tier0.tests.conftest import make_enemy, make_state


@pytest.fixture
def arm(monkeypatch):
    loader.reset_arm_caches()
    yield
    loader.reset_arm_caches()


def _state():
    state = make_state(enemies=[make_enemy(hp=60), make_enemy(hp=60)])
    state.player.character_id = "klee"
    return state


def _play(state, card_id: str):
    card = loader.get_card(card_id)
    effects.resolve_card(state, card)
    return card


# --- the grammar --------------------------------------------------------


def test_the_two_rows_declare_the_summons_printed_damage(arm):
    """The sheet says the number, once, where both engines read it."""
    chiori = loader.peek_card("proto_mi_chiori_hasode")
    amber = loader.peek_card("proto_mc_amber_explosive_puppet")
    assert [fx.get("summon_damage") for fx in chiori.effects] == [6]
    # Amber's first effect is her Strength loss (2026-10-02); the trap is second.
    assert [fx.get("summon_damage") for fx in amber.effects] == [None, 8]


def test_a_row_with_no_grammar_banks_nothing(arm):
    """Absent means today's behaviour exactly: the power keeps its constant,
    and nothing is written where nothing was declared."""
    state = _state()
    _play(state, "proto_mc_diona_icy_paws")
    assert state.player.summon_damage == {}


# --- `EB-463`: Chiori banks her printed 6 ------------------------------


def test_chiori_off_guest_cast_banks_her_printed_six(arm):
    state = _state()
    _play(state, "proto_mi_chiori_hasode")
    assert state.player.summon_damage["mi_tamoto"] == C.MI_TAMOTO_DMG


def test_the_volley_off_the_mode_is_the_printed_six(arm):
    state = _state()
    _play(state, "proto_mi_chiori_hasode")
    before = sum(e.hp for e in state.enemies)
    effects.companion_overhaul_turn_end(state)
    assert (before - sum(e.hp for e in state.enemies)
            == C.MI_TAMOTO_DMG)


# --- `EB-565`: Amber banks her printed 8 -------------------------------


def test_amber_off_guest_cast_banks_her_printed_eight(arm):
    state = _state()
    _play(state, "proto_mc_amber_explosive_puppet")
    assert state.player.summon_damage["mc_baron_bunny"] == C.MC_BARON_BUNNY_DMG

