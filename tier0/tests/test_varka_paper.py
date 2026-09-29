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


# --------------------------------------------------------------------------
#  Revision two (paper sec.9): Absorb is not a Swirl, Winds pay on Swirl
# --------------------------------------------------------------------------

def varka2(n=3, hp=40, **kw):
    st = make_state(enemies=[make_enemy(hp=hp, name=f"e{i}")
                             for i in range(n)])
    st.player = V.build_player(rev=2, **kw)
    st.player.energy = 3
    st.turn = 1
    return st


def play2(st, name, aim=None, fang=False):
    card = V.make_card(name)
    vs = st.player.varka
    vs.playing, vs.aim, vs.fang_want = card, aim, fang
    effects.resolve_card(st, card)
    return card


@pytest.mark.usefixtures("arm")
def test_rev2_fang_absorb_takes_the_aura_and_spreads_nothing():
    st = varka2()
    a, b, c = st.enemies
    reactions.apply_aura(st, a, "pyro")
    play2(st, "strike", aim=a, fang=True)
    assert a.aura is None
    assert b.aura is None and c.aura is None           # no spread
    assert (a.hp, b.hp, c.hp) == (34, 40, 40)          # no flat 2
    assert st.player.varka.winds == {"pyro": 1}
    assert st.player.varka.swirls == 0


@pytest.mark.usefixtures("arm")
def test_rev2_fang_is_optional_and_a_decline_does_not_use_it():
    st = varka2(n=1)
    (a,) = st.enemies
    reactions.apply_aura(st, a, "hydro")
    play2(st, "strike", aim=a, fang=False)
    assert a.aura == "hydro" and not a.aura_spent
    assert st.player.varka.fang_turn == -1 and not st.player.varka.winds
    play2(st, "strike", aim=a, fang=True)
    assert a.aura is None and "hydro" in st.player.varka.winds


@pytest.mark.usefixtures("arm")
def test_rev2_absorb_card_on_a_held_winds_aura_swirls_by_default():
    assert V.ABSORB_HELD_SWIRLS is True
    st = varka2(n=2)
    a, b = st.enemies
    st.player.varka.winds = {"pyro": 0}
    reactions.apply_aura(st, a, "pyro")
    play2(st, "windbound_execution", aim=a)
    assert a.aura == "pyro" and a.aura_spent              # a Swirl
    assert b.aura == "pyro" and b.aura_spent
    assert st.player.varka.swirls == 1


@pytest.mark.usefixtures("arm")
def test_rev2_every_wind_pays_on_a_swirl():
    st = varka2(n=1, hp=60)
    (a,) = st.enemies
    vs = st.player.varka
    vs.winds = {el: 0 for el in V.WIND_ELEMENTS}
    st.player.draw_pile = [V.make_card("defend") for _ in range(3)]
    hand = len(st.player.hand)
    reactions.apply_aura(st, a, "electro")
    play2(st, "tempest_charge", aim=a)
    # 8 + flat 2 + Pyro Wind's 3; Hydro 3 Block; Electro 1 card (+1 for
    # Tempest's own draw); Cryo 1 Weak.
    assert a.hp == 60 - 8 - 2 - V.R2_PYRO_SWIRL_DAMAGE
    assert st.player.block == V.R2_HYDRO_BLOCK
    assert len(st.player.hand) == hand + 2
    assert a.powers.get("weak") == V.R2_CRYO_WEAK
    # and no +2 on Attacks in revision two
    assert V.attack_bonus(st, V.make_card("squall")) == 0


@pytest.mark.usefixtures("arm")
def test_rev2_gale_sweep_swirls_its_snapshot():
    st = varka2(n=2)
    a, b = st.enemies
    reactions.apply_aura(st, a, "pyro")
    reactions.apply_aura(st, b, "electro")
    play2(st, "gale_sweep")
    assert st.player.varka.swirls == 2
    assert [x[1] for x in st.player.varka.swirl_log] == ["pyro", "electro"]


@pytest.mark.usefixtures("arm")
def test_rev2_ascension_b_spends_its_winds_and_they_can_return():
    st = varka2(n=1, hp=100, asc_version="B")
    (a,) = st.enemies
    vs = st.player.varka
    vs.winds = {"hydro": 0, "cryo": 0}
    card = play2(st, "four_winds_ascension", aim=a)
    assert a.hp == 100 - (V.ASCENSION_BASE + 2 * V.ASCENSION_B_PER_WIND)
    assert vs.winds == {} and vs.lost == {"hydro", "cryo"}
    assert V.make_card("four_winds_ascension").exhaust      # A still does
    assert not [c for c in st.player.draw_pile + st.player.hand
                if c.id == card.id and c.exhaust]
    reactions.apply_aura(st, a, "hydro")
    play2(st, "strike", aim=a, fang=True)
    assert "hydro" in vs.winds and vs.recollect == 1


@pytest.mark.usefixtures("arm")
def test_rev2_grand_masters_order_repeat_may_choose_another_knight():
    st = varka2(n=2)
    a, b = st.enemies
    vs = st.player.varka
    play2(st, "grand_masters_order")
    vs.muster_choice, vs.muster_choice2, vs.aim2 = "pyro", "cryo", b
    play2(st, "knights_muster", aim=a)
    assert a.aura == "pyro" and b.aura == "cryo"


def test_ascension_b_is_refused_in_revision_one():
    with pytest.raises(ValueError):
        V.build_player(asc_version="B")
