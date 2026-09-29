"""VARKA OATH REWORK ARM (exploration; `tier0.engine.varka_oath`, riding
`varka_paper.VARKA_PAPER`, off).

Pins sec.11 of `review/active/varka-paper-kit-2026-09-28.md` as the sim
reads it, including the paper's own worked turn (sec.11.3). The measuring
tool is `tools/varka_oath_report.py`.
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.engine import effects, reactions, varka_oath as O
from tier0.engine import varka_paper as V
from tier0.tests.conftest import make_enemy, make_state


@pytest.fixture
def arm(monkeypatch):
    monkeypatch.setattr(C, "SWIRL_PAYS", True)
    monkeypatch.setattr(C, "CRYSTALLIZE_KEEPS_AURA", True)
    monkeypatch.setattr(V, "VARKA_PAPER", True)
    monkeypatch.setitem(effects.OPS, "varka", V.op_varka)
    monkeypatch.setitem(effects.OPS, "varka_oath", O.op_oath)


def oath_state(n=2, hp=40, **kw):
    st = make_state(enemies=[make_enemy(hp=hp, name=f"e{i}")
                             for i in range(n)])
    st.player = O.build_player([], **kw)
    st.player.energy = 3
    st.turn = 1
    return st


def play(st, name_or_card, aim=None):
    card = (O.make_card(name_or_card) if isinstance(name_or_card, str)
            else name_or_card)
    vs = st.player.varka
    vs.playing = card
    vs.aim = aim
    if card in st.player.hand:
        st.player.hand.remove(card)
    effects.resolve_card(st, card)
    return card


def test_the_switch_is_off_and_registers_nothing():
    assert V.VARKA_PAPER is False
    assert "varka_oath" not in effects.OPS
    st = make_state()
    V.turn_start(st)                          # inert with the switch off


@pytest.mark.usefixtures("arm")
def test_the_worked_turn_of_sec_11_3():
    st = oath_state(n=2)
    a, b = st.enemies
    vs = st.player.varka
    play(st, "barbara_shining_miracle")
    assert vs.current == "hydro" and vs.oath["hydro"] == 2
    assert st.player.block == 7
    asc = [c for c in st.player.hand if c.id == "varka_four_winds_ascension"]
    assert len(asc) == 1                       # the Fang's one Ascension
    play(st, "windbound_execution")
    assert vs.oath["hydro"] == 4
    assert st.player.block == 13               # 7 + 3 + 3
    assert a.aura == "hydro" and a.aura_spent
    play(st, asc[0], aim=a)
    # 6 Anemo on a spent aura (no Swirl), then 3 x 4 Hydro, which refreshes.
    assert vs.asc[-1]["oath"] == 4 and vs.asc[-1]["printed"] == 18
    assert vs.oath["hydro"] == 5
    assert a.aura == "hydro" and not a.aura_spent
    # Enemy a: 4 (Windbound) + 2 + 2 (both Swirls' flat 2) + 6 + 12.
    assert a.hp == 40 - 4 - 2 - 2 - 6 - 12


@pytest.mark.usefixtures("arm")
def test_payout_is_the_current_element_only():
    st = oath_state(n=1)
    (a,) = st.enemies
    vs = st.player.varka
    play(st, "amber_fiery_rain", aim=a)        # current Pyro, Pyro Oath 1
    reactions.apply_aura(st, a, "hydro")       # a partner's Hydro
    hp = a.hp
    play(st, "updraft", aim=a)                 # Swirls Hydro: pays PYRO 3
    assert vs.oath == {"pyro": 1, "hydro": 1, "electro": 0, "cryo": 0}
    assert a.hp == hp - 8 - 2 - 3
    assert st.player.block == 0


@pytest.mark.usefixtures("arm")
def test_electro_pays_2_to_all_and_cryo_pays_vulnerable():
    # 2026-09-29 spec change: Electro 2 to ALL per Swirl; Cryo 1 Vulnerable.
    st = oath_state(n=3)
    a, b, c = st.enemies
    vs = st.player.varka
    vs.current = "electro"
    reactions.apply_aura(st, a, "pyro")
    play(st, "updraft", aim=a)
    assert (b.hp, c.hp) == (40 - 2 - 2, 40 - 2 - 2)   # flat 2 + Electro 2
    assert vs.pay["electro_dmg"] == 6
    st = oath_state(n=1)
    (a,) = st.enemies
    play(st, "kaeya_glacial_waltz", aim=a)
    assert a.powers.get("vulnerable", 0) == 1 and not a.powers.get("weak")
    a.aura_spent = False
    play(st, "updraft", aim=a)                           # Swirls the Cryo
    assert a.powers.get("vulnerable", 0) == 2


def test_headwind_is_cut_from_the_pool():
    assert sum(len(v) for v in O.POOL.values()) == 23
    assert [len(O.POOL[r]) for r in ("common", "uncommon", "rare")] == [
        9, 9, 5]


@pytest.mark.usefixtures("arm")
def test_variants_no_payout_and_swirl_only_oath():
    st = oath_state(n=2, payout=False)
    play(st, "barbara_shining_miracle")
    play(st, "windbound_execution")
    assert st.player.block == 7                # no Hydro 3s
    st = oath_state(n=2, apply_oath=False)
    vs = st.player.varka
    play(st, "barbara_shining_miracle")
    assert vs.oath["hydro"] == 0 and not vs.fang_done
    play(st, "windbound_execution")
    assert vs.oath["hydro"] == 2 and vs.fang_done


@pytest.mark.usefixtures("arm")
def test_movers_and_readers():
    st = oath_state(n=1)
    (a,) = st.enemies
    vs = st.player.varka
    vs.oath = {"pyro": 3, "hydro": 2, "electro": 1, "cryo": 0}
    vs.current = "pyro"
    play(st, "eye_of_the_storm")
    assert st.player.block == 6
    play(st, "rally_to_the_banner")
    assert vs.oath == {"pyro": 6, "hydro": 0, "electro": 0, "cryo": 0}
    play(st, "four_winds_accord")
    assert vs.oath == {"pyro": 2, "hydro": 2, "electro": 2, "cryo": 2}
    play(st, "oath_of_the_knights")
    play(st, "sworn_brotherhood")
    st.player.block = 0
    V.turn_start(st)
    assert vs.oath["pyro"] == 3 and st.player.block == 3
