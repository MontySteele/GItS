"""VARKA PAPER ARM (exploration; `tier0.engine.varka_paper`, switch off).

Pins the paper kit's rules as the sim reads them
(`review/active/varka-paper-kit-2026-09-28.md` sec.3, sec.5, sec.6), and that
the switch off leaves the shared engine as it was. The measuring tool is
`tools/varka_paper_report.py`.
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.engine import effects, reactions, varka_paper as V
from tier0.tests.conftest import make_enemy, make_state


@pytest.fixture
def arm(monkeypatch):
    monkeypatch.setattr(C, "SWIRL_PAYS", True)
    monkeypatch.setattr(C, "CRYSTALLIZE_KEEPS_AURA", True)
    monkeypatch.setattr(V, "VARKA_PAPER", True)
    monkeypatch.setitem(effects.OPS, "varka", V.op_varka)


def varka_state(n=3, hp=40):
    st = make_state(enemies=[make_enemy(hp=hp, name=f"e{i}")
                             for i in range(n)])
    st.player = V.build_player()
    st.player.energy = 3
    st.turn = 1
    return st


def play(st, name, aim=None):
    card = V.make_card(name)
    vs = st.player.varka
    vs.playing = card
    vs.aim = aim
    effects.resolve_card(st, card)
    return card


def test_the_switch_is_off_and_registers_nothing():
    assert V.VARKA_PAPER is False
    assert "varka" not in effects.OPS
    # The hooks read the switch first: a state with no Varka on it is inert.
    st = make_state()
    assert V.intercept_hit(st, st.enemies[0], "anemo", 5) is None
    assert V.attack_bonus(st, V.make_card("squall")) == 0


@pytest.mark.usefixtures("arm")
def test_the_fang_absorbs_the_first_attack_on_a_fresh_aura():
    st = varka_state()
    a, b, c = st.enemies
    reactions.apply_aura(st, a, "pyro")
    play(st, "strike", aim=a)
    # Absorb: the aura LEAVES the struck enemy; spent copies on the others.
    assert a.aura is None
    assert b.aura == "pyro" and b.aura_spent
    assert c.aura == "pyro" and c.aura_spent
    # Flat 2 to all (the Strike's 6 on top for a).
    assert (b.hp, c.hp) == (38, 38) and a.hp == 40 - 2 - 6
    assert st.player.varka.winds == {"pyro": 1}
    # Pyro Wind: Attacks deal +2 from here on.
    assert V.attack_bonus(st, V.make_card("squall")) == 2


@pytest.mark.usefixtures("arm")
def test_the_fang_is_once_a_turn_and_not_spent_on_a_miss():
    st = varka_state(n=2)
    a, b = st.enemies
    play(st, "strike", aim=a)                  # no aura: Fang not used
    assert st.player.varka.fang_turn == -1
    reactions.apply_aura(st, a, "hydro")
    reactions.apply_aura(st, b, "cryo")
    play(st, "strike", aim=a)                  # absorbs Hydro
    assert a.aura is None and st.player.varka.fang_turn == 1
    # b's Cryo was replaced by the spent Hydro copy (the spread replaces).
    assert b.aura == "hydro" and b.aura_spent
    reactions.apply_aura(st, b, "cryo")
    play(st, "strike", aim=b)                  # second Attack: plain Strike
    assert b.aura == "cryo" and not b.aura_spent
    assert set(st.player.varka.winds) == {"hydro"}


@pytest.mark.usefixtures("arm")
def test_an_absorb_card_on_a_spent_copy_does_nothing():
    st = varka_state(n=2)
    a, b = st.enemies
    reactions.apply_aura(st, a, "electro")
    play(st, "strike", aim=a)
    assert b.aura_spent
    play(st, "windbound_execution", aim=b)
    assert b.aura == "electro" and b.aura_spent      # untouched
    assert len(st.player.varka.absorbs) == 1


@pytest.mark.usefixtures("arm")
def test_winds_pay_on_later_swirls():
    st = varka_state(n=1)
    (a,) = st.enemies
    vs = st.player.varka
    vs.winds = {"hydro": 0, "cryo": 0}
    reactions.apply_aura(st, a, "pyro")
    block = st.player.block
    play(st, "windbound_execution", aim=a)
    assert st.player.block == block + V.HYDRO_WIND_BLOCK
    assert a.powers.get("weak") == V.CRYO_WIND_WEAK


@pytest.mark.usefixtures("arm")
def test_ascension_is_six_plus_six_per_wind():
    st = varka_state(n=1, hp=100)
    st.player.varka.winds = {"hydro": 0, "cryo": 0}
    play(st, "four_winds_ascension", aim=st.enemies[0])
    assert st.enemies[0].hp == 100 - 18
    assert st.player.varka.ascension == [(1, 2, 18)]


@pytest.mark.usefixtures("arm")
def test_converging_overload_lands_on_its_enemy_only():
    st = varka_state(n=3)
    a, b, c = st.enemies
    st.player.varka.converging = True
    st.player.varka.fang_turn = 1               # a plain Swirl, no Absorb
    reactions.apply_aura(st, a, "pyro")
    reactions.apply_aura(st, b, "electro")
    play(st, "squall", aim=a)
    # b: the flat 2 carrying Pyro Overloads there, splash on b alone.
    assert b.aura is None
    assert c.aura == "pyro" and c.aura_spent       # bare: a spent copy
    assert c.hp == 40 - 2
    assert b.hp == 40 - 2 - C.OVERLOAD_SPLASH
