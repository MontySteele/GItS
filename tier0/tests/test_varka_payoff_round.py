"""THE VARKA PAYOFF ROUND'S "CLAUDE SHIPS" LIST, the sim twin
(review/records/varka-payoff-round-2026-10-10.md). The C# side is
`klee-mod/KleeTests/Prototype/VarkaPayoffRoundTests.cs`.

  * Stoke the Flames and Ember Cleave switch to Pyro BEFORE their gain, so
    Dawn Wind's March sees a current-element gain.
  * Wolfpack shuffles an exhausting copy into the draw pile; a copy played
    fires it again, so one real card and one copy circulate.
  * The sheet's player-facing strings.
"""
from __future__ import annotations

import random
from pathlib import Path

import pytest
import yaml

from tier0.content import loader
from tier0.engine import combat
from tier0.engine import varka_oath as V
from tier0.engine.state import CombatState, Enemy

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def varka():
    loader.reset_arm_caches()
    try:
        yield
    finally:
        loader.reset_arm_caches()


def _vk(name):
    return "proto_vk_" + name


def _state(element="hydro"):
    e = Enemy(hp=500, max_hp=500, name="e",
              intents=[{"kind": "block", "amount": 0}])
    p = V.build_player(element, fang=False)
    p.draw_pile = [loader.get_card("strike") for _ in range(10)]
    st = CombatState(player=p, enemies=[e], rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _play(st, card):
    if isinstance(card, str):
        card = loader.get_card(card)
    st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)
    return card


def _row(card_id):
    rows = yaml.safe_load(
        (REPO_ROOT / "docs" / "prototype-surface.yaml").read_text(
            encoding="utf-8"))
    rows = rows if isinstance(rows, list) else rows.get("cards", [])
    return next(r for r in rows if r.get("id") == card_id)


def test_ember_cleave_gain_sees_pyro_current(varka):
    # Its hit makes Pyro current (the open Oath) and credits 1; its own gain
    # then lands as the current element's: Dawn Wind's March pays twice.
    st = _state()
    led = V.ledger(st.player)
    led.current = "electro"
    st.player.powers[V.DAWN_WINDS_MARCH] = 4
    st.player.hand = []
    _play(st, _vk("ember_cleave"))
    assert led.current == "pyro" and led.oath["pyro"] == 2
    assert st.player.block == 8


def test_stoke_the_flames_switch_lands_before_the_gain(varka):
    st = _state()
    led = V.ledger(st.player)
    led.current = "cryo"
    st.player.powers[V.DAWN_WINDS_MARCH] = 3
    st.player.hand = [loader.get_card("defend")]
    seen = []
    real_gain = V.gain

    def spy(state, element, n, *a, **kw):
        seen.append((element, V.ledger(state.player).current))
        return real_gain(state, element, n, *a, **kw)

    V.gain = spy
    try:
        _play(st, _vk("stoke_the_flames"))
    finally:
        V.gain = real_gain
    assert ("pyro", "pyro") in seen
    assert st.player.block == 3


def test_a_wolfpack_copy_exhausts_and_fires_again(varka):
    st = _state()
    p = st.player
    p.powers[V.WOLFPACK] = 1
    _play(st, _vk("four_winds_ascension"))
    copy = next(c for c in p.draw_pile if c.id == V.ASCENSION_ID)
    assert copy.exhaust
    p.draw_pile.remove(copy)
    _play(st, copy)
    # The copy Exhausted, and shuffled a new exhausting copy in.
    assert copy in p.exhaust_pile
    fresh = [c for c in p.draw_pile if c.id == V.ASCENSION_ID]
    assert len(fresh) == 1 and fresh[0].exhaust and fresh[0] is not copy
    # The real card went to the discard pile, as before.
    assert [c.id for c in p.discard_pile].count(V.ASCENSION_ID) == 1


def test_the_sheet_strings(varka):
    assert _row(_vk("stoke_the_flames"))["description"] == (
        "[gold]Exhaust[/gold] a card. [gold]Pyro[/gold] becomes your "
        "[gold]current element[/gold]. Gain {VkAmount:diff()} "
        "[gold]Pyro[/gold] [gold]Oath[/gold].")
    assert _row(_vk("wolfpack"))["description"] == (
        "Whenever you play Four Winds' Ascension, shuffle a copy of it into "
        "your [gold]Draw Pile[/gold]. The copy [gold]Exhausts[/gold].")
    assert _row(_vk("wolfpack"))["upgrade"] == {"innate": True}
    assert _row(_vk("unwavering_banner"))["description"] == (
        "Only [gold]Knights[/gold] change your [gold]current element[/gold]. "
        "Whenever another card would, gain 1 [gold]Oath[/gold] of your "
        "[gold]current element[/gold] instead.")
    # Numbers held.
    assert _row(_vk("stoke_the_flames"))["upgrade"] == {"varka_amount": 1}
    ember = _row(_vk("ember_cleave"))
    assert ember["upgrade"] == {"varka_base": 3}
    assert ember["effects"][0]["base"] == 9
    assert ember["effects"][2]["amount"] == 1
