"""THE SAKURA LEVELS PAPER (ruled 2026-10-17, picks 1 (a) and 2 (a); the
user: "Agreed on both of these"): `review/active/yae-sakura-levels-2026-10-17.md`.
The sim half; the C# half is
`klee-mod/KleeTests/Prototype/YaeSakuraLevelsTests.cs`.

  1. A Sakura (Thunder) acts for 1 + 2 per Level (Level 1: 3, Level 3: 7,
     Level 5: 11). Foxfire stays 1 + Level to ALL, Kitsune 2 + Level Block;
     Red Ink's +3 adds as before.
  2. Levels carry over on a replace: a plant of another kind into a full
     shrine makes the Sakura closest to withering act and wither, and the
     new one takes its place at the HIGHER of its own plant Level and the
     withered one's Level. A same-kind plant still refreshes it and gives it
     a Level.
"""

from __future__ import annotations

import random

import pytest

from tier0.content import loader
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy


@pytest.fixture(autouse=True)
def yae():
    loader.reset_arm_caches()
    Y.SCALING = "level"
    try:
        yield
    finally:
        Y.SCALING = "level"
        loader.reset_arm_caches()


def _state():
    p = Y.build_player()
    p.draw_pile = []
    st = CombatState(player=p,
                     enemies=[Enemy(hp=100, max_hp=100, name="e0",
                                    intents=[{"kind": "block", "amount": 0}])],
                     rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _led(st):
    return Y.ledger(st.player)


def _sized(st, kind, level, annotation=None):
    s = Y.Sakura(level=level, turns_left=3, seq=1, kind=kind,
                 planted_level=level)
    s.add(annotation)
    return Y.act_size(st, s)


# --- 1. what a Level is worth -------------------------------------------------

def test_a_thunder_level_is_worth_two():
    st = _state()
    assert [_sized(st, Y.THUNDER, n) for n in (1, 3, 5)] == [3, 7, 11]


def test_foxfire_and_kitsune_are_unchanged():
    st = _state()
    assert [_sized(st, Y.FOXFIRE, n) for n in (1, 3, 5)] == [2, 4, 6]
    assert [_sized(st, Y.KITSUNE, n) for n in (1, 3, 5)] == [3, 5, 7]


def test_red_ink_still_adds_three_to_the_new_size():
    st = _state()
    assert _sized(st, Y.THUNDER, 3, Y.RED_INK) == 7 + Y.RED_INK_AMOUNT


def test_the_tenko_clause_prints_the_new_strike():
    st = _state()
    Y.plant(st, 1)
    Y.level_up(st, 2)                                # Level 3
    assert Y.tenko_line(st) == " (Sakura: 7 damage in total)"


# --- 2. Levels carry over on a replace ---------------------------------------

def _full_thunder_shrine(st, levels):
    Y.plant(st, Y.SAKURA_CAP)
    for s, level in zip(_led(st).sakura, levels):
        s.level = level


def test_another_kind_takes_the_replaced_sakuras_level():
    st = _state()
    _full_thunder_shrine(st, [4, 1, 1])
    target = Y.next_to_wither(_led(st))
    assert target.level == 4
    Y.plant(st, 1, kind=Y.KITSUNE)
    led = _led(st)
    assert target not in led.sakura                  # it withered
    new = led.sakura[-1]
    assert (new.kind, new.level, new.planted_level) == (Y.KITSUNE, 4, 4)
    assert [s.level for s in led.sakura] == [1, 1, 4]
    # It still acted first and still withered (Scattered Blossoms reads it).
    assert [r["reason"] for r in st.log
            if r["event"] == "yae_sakura_strike"] == ["full_shrine"]
    assert any(r["event"] == "yae_wither" and r.get("reason") == "replaced"
               for r in st.log)


def test_the_target_is_still_the_one_closest_to_withering():
    st = _state()
    _full_thunder_shrine(st, [1, 6, 1])
    _led(st).sakura[1].turns_left = 1                # the Level 6 is next
    Y.plant(st, 1, kind=Y.FOXFIRE)
    new = _led(st).sakura[-1]
    assert (new.kind, new.level) == (Y.FOXFIRE, 6)


def test_a_lower_replaced_level_does_not_lower_a_higher_plant():
    # Guardian of Narukami's "at Level 3" into a shrine of Level 1s.
    st = _state()
    _full_thunder_shrine(st, [1, 1, 1])
    Y.plant(st, 1, level=3, kind=Y.KITSUNE)
    assert _led(st).sakura[-1].level == 3


def test_mooncall_beats_a_lower_replaced_level_and_loses_to_a_higher():
    st = _state()
    st.player.powers[Y.MOONCALL] = 1                 # planted at Level 2
    _full_thunder_shrine(st, [1, 1, 1])
    Y.plant(st, 1, kind=Y.KITSUNE)
    assert _led(st).sakura[-1].level == 2
    st = _state()
    st.player.powers[Y.MOONCALL] = 1
    _full_thunder_shrine(st, [5, 1, 1])
    Y.plant(st, 1, kind=Y.KITSUNE)
    assert _led(st).sakura[-1].level == 5


def test_same_kind_is_unchanged_refresh_and_one_level():
    st = _state()
    _full_thunder_shrine(st, [4, 1, 1])
    target = _led(st).sakura[0]
    target.turns_left = 1
    Y.plant(st, 1)
    led = _led(st)
    assert len(led.sakura) == Y.SAKURA_CAP and led.sakura[0] is target
    assert [s.level for s in led.sakura] == [5, 1, 1]
    assert target.turns_left == Y.SAKURA_TURNS
    assert not any(r["event"] == "yae_wither" for r in st.log)
