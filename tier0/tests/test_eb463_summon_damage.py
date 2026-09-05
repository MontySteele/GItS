"""`EB-463` / `EB-565`: a summon's damage takes the Guest Cast fold.

THE FIND (Furina r8 (c) 1). Guest Cast -- "Spotlight every Companion card.
Their printed damage and Block are 50% stronger" -- raised Lynette's and
Diona's Block 5 to 7 and left Chiori -- Fluttering Hasode's 6 Geo at 6 on the
same screen. `EB-565` is the same miss one card over (Furina r14 lane 2 (c) 2):
Amber -- Explosive Puppet printed 8 and dealt 8 while Chevreuse went 7 to 10
and Gorou 8 to 12.

WHY THOSE TWO AND NOT THE OTHERS. A Companion whose damage is a `damage` op
runs it through `_spotlight_scale` like any printed number. A row whose whole
body is `apply_power` prints a number the POWER deals LATER, so it never
reached that path at all -- there was nothing between the card and the power to
carry it. The sheet grammar `apply_power: summon_damage:` is that carrier, and
it snapshots the fold at PLAY (R72), because the power fires turns later when
the card is gone and the mode may have expired.

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
    monkeypatch.setattr(C, "COMPANION_OVERHAUL", True)
    loader.reset_arm_caches()
    yield
    loader.reset_arm_caches()


def _state(guest_cast: bool):
    state = make_state(enemies=[make_enemy(hp=60), make_enemy(hp=60)])
    state.player.character_id = "klee"
    if guest_cast:
        state.player.spotlight = C.SPOTLIGHT_GUEST_CAST
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
    assert [fx.get("summon_damage") for fx in amber.effects] == [8]


def test_a_row_with_no_grammar_banks_nothing(arm):
    """Absent means today's behaviour exactly: the power keeps its constant,
    and nothing is written where nothing was declared."""
    state = _state(guest_cast=True)
    _play(state, "proto_mc_diona_icy_paws")
    assert state.player.summon_damage == {}


# --- `EB-463`: Chiori prints and deals 9 --------------------------------


def test_chiori_under_guest_cast_banks_nine(arm):
    state = _state(guest_cast=True)
    _play(state, "proto_mi_chiori_hasode")
    assert state.player.summon_damage["mi_tamoto"] == 9


def test_chiori_off_guest_cast_banks_her_printed_six(arm):
    state = _state(guest_cast=False)
    _play(state, "proto_mi_chiori_hasode")
    assert state.player.summon_damage["mi_tamoto"] == C.MI_TAMOTO_DMG


def test_the_tamoto_volley_deals_the_banked_number(arm):
    """The whole point of the snapshot: the volley fires at the END of a turn,
    when the card is gone, and it still pays what the card printed."""
    state = _state(guest_cast=True)
    _play(state, "proto_mi_chiori_hasode")
    before = sum(e.hp for e in state.enemies)
    effects.companion_overhaul_turn_end(state)
    assert before - sum(e.hp for e in state.enemies) == 9


def test_the_volley_off_the_mode_is_the_printed_six(arm):
    state = _state(guest_cast=False)
    _play(state, "proto_mi_chiori_hasode")
    before = sum(e.hp for e in state.enemies)
    effects.companion_overhaul_turn_end(state)
    assert (before - sum(e.hp for e in state.enemies)
            == C.MI_TAMOTO_DMG)


# --- `EB-565`: Amber prints and deals 12 --------------------------------


def test_amber_under_guest_cast_banks_twelve(arm):
    state = _state(guest_cast=True)
    _play(state, "proto_mc_amber_explosive_puppet")
    assert state.player.summon_damage["mc_baron_bunny"] == 12


def test_amber_off_guest_cast_banks_her_printed_eight(arm):
    state = _state(guest_cast=False)
    _play(state, "proto_mc_amber_explosive_puppet")
    assert state.player.summon_damage["mc_baron_bunny"] == C.MC_BARON_BUNNY_DMG


def test_the_puppet_triggers_for_the_banked_number(arm):
    """A trap answers an enemy ATTACK, which is later still: the fold has to
    have been taken at play or there is nothing left to take it from."""
    state = _state(guest_cast=True)
    _play(state, "proto_mc_amber_explosive_puppet")
    before = sum(e.hp for e in state.enemies)
    effects.companion_overhaul_before_enemy_hit(state, state.enemies[0], 10)
    assert before - sum(e.hp for e in state.enemies) == 12 * 2
