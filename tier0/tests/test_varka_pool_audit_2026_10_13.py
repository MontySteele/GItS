"""VARKA POOL AUDIT, 2026-10-13 -- the sim engine's pins.

[USER]'s rulings (provenance, "Varka pool audit, 2026-10-13"): Blazing
Charge plus 1 per Pyro Oath; Kindled Edge's bonus 5 [7]; Chain Lightning
costs 0 and discards 2; Tempest of the Four Winds 6 [8]; Downburst 18 [24]
and 2 Oath of each element; Eula: Icetide Vortex costs 1, 8 [11]. The
behaviour pins live beside each card's older tests; these are the numbers.
"""

from __future__ import annotations

import random

import pytest

from tier0.content import loader
from tier0.engine import combat
from tier0.engine import varka_oath as V
from tier0.engine.state import CombatState, Enemy


@pytest.fixture
def varka():
    loader.reset_arm_caches()
    try:
        yield
    finally:
        loader.reset_arm_caches()


def _vk(name):
    return "proto_vk_" + name


def _fx(card_id, op):
    return next(f for f in loader.get_card(card_id).effects if f["op"] == op)


def _enemy(hp=100, name="e", aura=None):
    e = Enemy(hp=hp, max_hp=hp, name=name,
              intents=[{"kind": "block", "amount": 0}])
    if aura:
        e.aura, e.aura_turns_left = aura, 2
    return e


def _play(st, card_id):
    card = loader.get_card(card_id)
    st.player.hand.append(card)
    st.player.energy = 10
    combat.play_card(st, card)


def _state(enemies):
    p = V.build_player("pyro", fang=False)
    p.draw_pile = [loader.get_card("strike") for _ in range(10)]
    st = CombatState(player=p, enemies=enemies, rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def test_the_ruled_numbers(varka):
    blazing = _vk("blazing_charge")
    assert loader.get_card(blazing).cost == 1
    assert (_fx(blazing, "varka")["base"], _fx(blazing, "varka")["per"]) == (8, 1)
    assert _fx(blazing + "+", "varka")["base"] == 11
    assert _fx(blazing + "+", "varka")["per"] == 1
    edge = _vk("kindled_edge")
    assert (_fx(edge, "varka")["base"], _fx(edge, "varka")["amount"]) == (7, 5)
    assert (_fx(edge + "+", "varka")["base"],
            _fx(edge + "+", "varka")["amount"]) == (10, 7)
    tempest = _vk("tempest_of_the_four_winds")
    assert _fx(tempest, "varka")["base"] == 6
    assert _fx(tempest + "+", "varka")["base"] == 8
    downburst = _vk("downburst")
    assert _fx(downburst, "damage")["amount"] == 18
    assert _fx(downburst + "+", "damage")["amount"] == 24
    assert _fx(downburst, "varka")["amount"] == 2
    eula = loader.get_card(_vk("eula_icetide_vortex"))
    assert eula.cost == 1
    assert _fx(eula.id, "damage")["amount"] == 8
    assert _fx(eula.id + "+", "damage")["amount"] == 11


def test_kindled_edge_bonus_is_its_own_number(varka):
    st = _state([_enemy(name="a", aura="hydro")])
    _play(st, _vk("kindled_edge"))
    hits = [r for r in st.log if r.get("event") == "damage"
            and r.get("target") == "a"]
    assert [h["base"] for h in hits] == [7, 5]
    st = _state([_enemy(name="b")])
    _play(st, _vk("kindled_edge"))
    assert st.enemies[0].hp == 100 - 7


def test_tempest_deals_six_four_times(varka):
    st = _state([_enemy(name="a", hp=200)])
    _play(st, _vk("tempest_of_the_four_winds"))
    # Reactions between its own four hits may add; at least the printed 24.
    assert 200 - st.enemies[0].hp >= 4 * 6
