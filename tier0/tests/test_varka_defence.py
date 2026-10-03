"""VARKA DEFENCE -- the sim engine's pins for the ruled paper
`review/active/varka-defence-2026-10-01.md` (both picks ruled 2026-10-01):
Gale Mantle, Gust Ward and Windborne Resolve in place of Squall, Four Banners
and Favonian Standard; Oathbound Aegis at half the total Oath, uncapped;
Boreas's Fang makes the starter Knight's element current at combat start.
Rules: `tier0/engine/varka_oath.py`; rows: the `proto_vk_` block of
`docs/prototype-surface.yaml`. The C# twin is
`klee-mod/KleeTests/Prototype/VarkaDefenceTests.cs`.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine import varka_oath as V
from tier0.engine.state import CombatState, Enemy


@pytest.fixture
def varka():
    saved = (C.SWIRL_PAYS, C.CRYSTALLIZE_KEEPS_AURA)
    C.SWIRL_PAYS, C.CRYSTALLIZE_KEEPS_AURA = True, True
    loader.reset_arm_caches()
    try:
        yield
    finally:
        C.SWIRL_PAYS, C.CRYSTALLIZE_KEEPS_AURA = saved
        loader.reset_arm_caches()


def _vk(name):
    return "proto_vk_" + name


def _enemy(hp=100):
    return Enemy(hp=hp, max_hp=hp, name="e",
                 intents=[{"kind": "block", "amount": 0}])


def _state(element="pyro", fang=False):
    p = V.build_player(element, fang=fang)
    p.draw_pile = [loader.get_card("strike") for _ in range(10)]
    st = CombatState(player=p, enemies=[_enemy()], rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _play(st, cid, energy=10):
    card = loader.get_card(cid)
    st.player.hand.append(card)
    st.player.energy = energy
    combat.play_card(st, card)
    return card


def _fx(cid, op):
    return [f for f in loader.get_card(cid).effects if f["op"] == op][0]


# ---------------------------------------------------------------------------
# 1. The pool: 78 at 20 / 35 / 23, three in and three out.
# ---------------------------------------------------------------------------

# Gust Ward left with the rebalance (2026-10-03): Storm Battery's place.
NEW = {"gale_mantle": "common", "windborne_resolve": "uncommon"}
GONE = ("squall", "four_banners", "favonian_standard")


def test_the_pool_stays_78_with_the_three_swaps(varka):
    pool = {c.id: c for c in loader.prototype_cards()
            if c.id.startswith(V.ID_PREFIX) and c.rarity != "basic"}
    assert len(pool) == 78
    by = {r: sum(1 for c in pool.values() if c.rarity == r)
          for r in ("common", "uncommon", "rare")}
    assert by == {"common": 20, "uncommon": 35, "rare": 23}
    assert {_vk(x): pool[_vk(x)].rarity for x in NEW} == {
        _vk(x): r for x, r in NEW.items()}
    assert not {_vk(x) for x in GONE} & set(pool)
    assert not hasattr(V, "FAVONIAN_STANDARD")


def test_tailwind_guard_is_unchanged(varka):
    f = _fx(_vk("tailwind_guard"), "block")["amount_formula"]
    assert (f["base"], f["per"], f["count"]) == (0, 3, "oath_elements")
    up = _fx(_vk("tailwind_guard") + "+", "block")["amount_formula"]
    assert up["per"] == 4


# ---------------------------------------------------------------------------
# 2. The three new cards.
# ---------------------------------------------------------------------------

def test_gale_mantle_gains_5_plus_half_the_total_oath(varka):
    card = loader.get_card(_vk("gale_mantle"))
    assert (card.cost, card.type) == (1, "skill")
    assert _fx(_vk("gale_mantle") + "+", "block")["amount_formula"]["base"] == 8
    st = _state()
    _play(st, _vk("gale_mantle"))
    assert st.player.block == 5                       # no Oath yet
    led = V.ledger(st.player)
    led.oath.update(pyro=3, hydro=4, cryo=0, electro=2)    # 9 -> 4
    st.player.block = 0
    _play(st, _vk("gale_mantle"))
    assert st.player.block == 5 + 4                   # half rounds down
    assert effects._runtime_count(st, "half_total_oath") == 4
    led.oath.update(pyro=10, hydro=10, cryo=10, electro=10)
    st.player.block = 0
    _play(st, _vk("gale_mantle") + "+")
    assert st.player.block == 8 + 20                  # no cap


def test_half_total_oath_is_zero_for_anyone_else():
    from tier0.engine.state import Player
    st = CombatState(player=Player(hp=80, max_hp=80, character_id="klee"),
                     enemies=[_enemy()], rng=random.Random(0))
    assert effects._runtime_count(st, "half_total_oath") == 0


def test_windborne_resolve_rows(varka):
    card = loader.get_card(_vk("windborne_resolve"))
    assert (card.cost, card.type) == (1, "power")
    assert _fx(_vk("windborne_resolve"), "apply_power")["power"] == \
        V.WINDBORNE_RESOLVE
    st = _state()
    _play(st, _vk("windborne_resolve"))
    _play(st, _vk("windborne_resolve") + "+")
    assert st.player.powers[V.WINDBORNE_RESOLVE] == 5 + 7
    _play(st, _vk("kaeya_glacial_waltz"))             # None -> Cryo
    assert st.player.block == 5 + 12


# ---------------------------------------------------------------------------
# 3. Oathbound Aegis, re-aimed.
# ---------------------------------------------------------------------------

def test_oathbound_aegis_rows(varka):
    assert loader.get_card(_vk("oathbound_aegis")).cost == 2
    assert loader.get_card(_vk("oathbound_aegis") + "+").cost == 1
    assert _fx(_vk("oathbound_aegis") + "+", "apply_power")["amount"] == 1
    st = _state()
    _play(st, _vk("oathbound_aegis"))
    V.ledger(st.player).oath.update(pyro=40, hydro=1)
    st.player.block = 0
    V.turn_end(st)
    assert st.player.block == 20                      # 41 // 2, no cap


# ---------------------------------------------------------------------------
# 4. Boreas's Fang: the starter Knight's element at combat start.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("element", V.ELEMENTS)
def test_the_fang_makes_the_starter_element_current_on_turn_one(varka,
                                                                 element):
    st = _state(element, fang=True)
    led = V.ledger(st.player)
    assert led.current is None
    V.turn_start(st)
    assert led.current == element
    assert sum(led.oath.values()) == 0                # no Oath gained
    assert not led.fang_fired                         # Ascension still waits


def test_the_fang_is_a_change_and_only_on_turn_one(varka):
    st = _state("hydro", fang=True)
    st.player.powers[V.WINDBORNE_RESOLVE] = 5
    V.turn_start(st)
    assert st.player.block == 5                       # a change pays
    led = V.ledger(st.player)
    led.current = "pyro"
    st.turn = 2
    V.turn_start(st)
    assert led.current == "pyro"                      # turn 2: nothing


def test_no_fang_no_starting_element(varka):
    st = _state("cryo", fang=False)
    V.turn_start(st)
    assert V.ledger(st.player).current is None


def test_the_upgraded_fang_does_it_too(varka):
    p = V.build_player("electro", fang_upgraded=True)
    st = CombatState(player=p, enemies=[_enemy()], rng=random.Random(0))
    st.turn = 1
    V.turn_start(st)
    assert V.ledger(p).current == "electro"


def test_the_starting_element_falls_back_to_the_starter_knight(varka):
    p = V.build_player("cryo", fang=True)
    p.varka_starter_element = None                    # an unrecorded run
    assert V.starting_element(p) == "cryo"            # Kaeya in the deck
    p.draw_pile = [c for c in p.draw_pile
                   if c.id not in V.STARTER_KNIGHT_IDS.values()]
    assert V.starting_element(p) is None


def test_a_whole_fight_opens_on_the_starter_element(varka):
    import tools.varka_expansion_sim as X
    p = V.build_player("hydro")
    s = combat.run_fight(p, [_enemy(hp=30)], X.make_pilot(), seed=3)
    events = [r for r in s.log if r.get("event") in ("varka_fang_element",
                                                     "varka_current")]
    assert events[0] == {**events[0], "event": "varka_fang_element",
                         "element": "hydro"}
    assert events[1]["event"] == "varka_current"
    assert events[1]["element"] == "hydro" and events[1]["knight"] is False
