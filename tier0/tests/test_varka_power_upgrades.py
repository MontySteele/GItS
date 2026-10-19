"""VARKA, THE POWER UPGRADE PASS (2026-10-19) -- the sim's pins for the eight
power upgrades that stopped being Innate or a cost cut. [USER], 2026-10-19:
"You do have a habit of making too many powers just decrease their cost by 1
on upgrade though." Each upgraded card installs a Plus power
(`upgraded_power`, rewritten by `tier0/content/upgrades.py`); Comrades of the
Expedition bumps its stack. Rules: `tier0/engine/varka_oath.py`; the C# twin
is `klee-mod/KleeTests/Prototype/VarkaPowerUpgradeTests.cs`. Staging paper:
`review/active/varka-fang-next-2026-10-19.md`.
"""

from __future__ import annotations

import random

import pytest

from tier0.content import loader
from tier0.engine import varka_oath as V
from tier0.engine.state import CombatState, Enemy


@pytest.fixture
def varka():
    loader.reset_arm_caches()
    try:
        yield
    finally:
        loader.reset_arm_caches()


def _state():
    e = Enemy(hp=100, max_hp=100, name="e",
              intents=[{"kind": "block", "amount": 0}])
    p = V.build_player("pyro")
    p.draw_pile = [loader.get_card("strike") for _ in range(10)]
    st = CombatState(player=p, enemies=[e], rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _vk(name):
    return "proto_vk_" + name


PLUS = {
    "unwavering_banner": V.UNWAVERING_BANNER_PLUS,
    "wildfire_oath": V.WILDFIRE_OATH_PLUS,
    "absolute_zero": V.ABSOLUTE_ZERO_PLUS,
    "wolfpack": V.WOLFPACK_PLUS,
    "weathervane": V.WEATHERVANE_PLUS,
    "eye_of_stormterror": V.EYE_OF_STORMTERROR_PLUS,
    "west_winds_blessing": "vk_west_winds_blessing_plus",
}


def test_the_upgraded_cards_install_the_plus_power_and_are_not_innate(varka):
    for name, power in PLUS.items():
        up = loader.get_card(_vk(name) + "+")
        base = loader.get_card(_vk(name))
        assert not up.innate, name
        assert up.cost == base.cost, name
        assert up.effects[0]["power"] == power, name
    comrades = loader.get_card(_vk("comrades_of_the_expedition") + "+")
    assert comrades.cost == 2 and comrades.effects[0]["amount"] == 2


def test_banner_plus_pays_two(varka):
    st = _state()
    led = V.ledger(st.player)
    led.current = "pyro"
    st.player.powers[V.UNWAVERING_BANNER_PLUS] = 1
    assert V.has_banner(st.player)
    V.banner_holds(st, "cryo")
    assert led.oath["pyro"] == V.BANNER_OATH_UPGRADED == 2


def test_banner_plain_still_pays_one(varka):
    st = _state()
    led = V.ledger(st.player)
    led.current = "pyro"
    st.player.powers[V.UNWAVERING_BANNER] = 1
    V.banner_holds(st, "cryo")
    assert led.oath["pyro"] == 1


def test_wildfire_plus_adds_three(varka):
    st = _state()
    led = V.ledger(st.player)
    led.oath["pyro"] = 4
    st.player.powers[V.WILDFIRE_OATH_PLUS] = 1
    V._wildfire(st, st.enemies[0])
    assert st.enemies[0].hp == 100 - (4 + 3)


def test_absolute_zero_plus_adds_three(varka):
    st = _state()
    led = V.ledger(st.player)
    led.oath["cryo"] = 2
    st.player.powers[V.ABSOLUTE_ZERO_PLUS] = 1
    V.on_debuff_applied(st, st.enemies[0], "weak", 1)
    assert st.enemies[0].hp == 100 - (2 + 3)


def test_eye_plus_draws_on_the_fourth_swirl(varka):
    st = _state()
    led = V.ledger(st.player)
    p = st.player
    led.swirls_this_turn = 3            # the fourth comes next
    p.powers[V.EYE_OF_STORMTERROR] = 1
    p.powers[V.EYE_OF_STORMTERROR_PLUS] = 1
    hand = len(p.hand)
    st.enemies[0].aura, st.enemies[0].aura_turns_left = "pyro", 2
    V.on_swirl(st, st.enemies[0], "pyro")
    assert led.swirls_this_turn == 4
    assert len(p.hand) == hand + 1      # the Plus form only


def test_weathervane_plus_gains_one_oath_of_the_choice(varka):
    st = _state()
    led = V.ledger(st.player)
    led.current = "pyro"
    led.oath.update(pyro=1, cryo=2)
    st.player.powers[V.WEATHERVANE_PLUS] = 1
    led.weathervane_choice = "cryo"
    V.turn_start(st)
    assert led.current == "cryo"
    assert led.oath["cryo"] == 2 + V.WEATHERVANE_OATH_UPGRADED


def test_weathervane_plus_gains_nothing_on_keep(varka):
    st = _state()
    led = V.ledger(st.player)
    led.current = "pyro"
    led.oath.update(pyro=1, cryo=2)
    st.player.powers[V.WEATHERVANE_PLUS] = 1
    led.weathervane_choice = "keep"
    V.turn_start(st)
    assert led.current == "pyro" and led.oath == {**led.oath, "pyro": 1,
                                                   "cryo": 2}


def test_lupical_plus_shuffles_an_upgraded_copy(varka):
    st = _state()
    p = st.player
    p.powers[V.WOLFPACK_PLUS] = 1
    card = loader.get_card(V.ASCENSION_ID)
    p.hand.append(card)
    p.energy = 10
    from tier0.engine import combat
    combat.play_card(st, card)
    copies = [c for c in p.draw_pile if c.id == V.ASCENSION_ID + "+"]
    assert len(copies) == 1 and copies[0].exhaust
