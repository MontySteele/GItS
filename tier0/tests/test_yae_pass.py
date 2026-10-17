"""Yae pass 2026-10-16 (review/active/yae-ancients-relics-2026-10-16.md
sec.1, the rate pass). [USER]: "Let's do a design pass over the current Yae
pool. Does anything look too obviously weak or strong for its rarity /
energy rate?" Sim half; the C# half is
`klee-mod/KleeTests/Prototype/YaeAncientsRelicsTests.cs`, which also holds the
Ancients, relics and potions (game-side only until Balance).
"""

from __future__ import annotations

import random
from collections import Counter

import pytest

from tier0.content import loader
from tier0.engine import combat
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy


@pytest.fixture(autouse=True)
def yae():
    loader.reset_arm_caches()
    Y.SCALING = "level"
    try:
        yield
    finally:
        loader.reset_arm_caches()


def _state(seed=0):
    p = Y.build_player()
    p.draw_pile = [loader.get_card("defend") for _ in range(10)]
    st = CombatState(player=p,
                     enemies=[Enemy(hp=200, max_hp=200, name="e0",
                                    intents=[{"kind": "block", "amount": 0}])],
                     rng=random.Random(seed))
    st.turn = 1
    st.in_player_turn = True
    return st


def _card(name):
    return loader.get_card("proto_ym_" + name)


def _play(st, card):
    if isinstance(card, str):
        card = _card(card)
    st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)
    return card


def _yae_fx(card):
    return next(fx for fx in card.effects if fx.get("op") == "yae")


def _led(st):
    return Y.ledger(st.player)


def test_the_pool_stays_78_with_the_two_rarities_swapped():
    rows = [c for c in loader.prototype_cards()
            if c.id.startswith(Y.ID_PREFIX) and c.rarity != "basic"]
    assert Counter(c.rarity for c in rows) == {"common": 20, "uncommon": 38,
                                               "rare": 20}
    assert _card("editorial_priority").rarity == "rare"
    assert _card("mischievous_teasing").rarity == "uncommon"


def test_evergreen_charm_makes_the_oldest_last_2_more_turns():
    st = _state()
    Y.plant(st, 2)
    first, second = _led(st).sakura
    _play(st, "evergreen_charm")
    assert st.player.block == 7
    assert first.turns_left == Y.SAKURA_TURNS + 2
    assert second.turns_left == Y.SAKURA_TURNS
    assert first.annotations == []
    # It ticks as every Sakura does: it withers two turns later.
    for _ in range(Y.SAKURA_TURNS):
        Y.turn_end(st)
        Y.turn_start(st)
    assert _led(st).sakura == [first]
    for _ in range(2):
        Y.turn_end(st)
        Y.turn_start(st)
    assert _led(st).sakura == []


def test_evergreen_charm_with_no_sakura_is_its_block():
    st = _state()
    _play(st, "evergreen_charm+")
    assert st.player.block == 10
    Y.validate_op("x", {"op": "yae", "kind": "extend_oldest", "amount": 2})


def test_fox_fire_draft_upgraded_is_the_2_newest():
    st = _state()
    Y.plant(st, 3)
    _play(st, "fox_fire_draft+")
    assert [s.annotations for s in _led(st).sakura] == [
        [], [Y.FOX_FIRE], [Y.FOX_FIRE]]


def test_thunderbolt_tithe_and_edict_upgrades():
    base, plus = _yae_fx(_card("thunderbolt_tithe")), _yae_fx(_card("thunderbolt_tithe+"))
    assert (base["base"], base["per"]) == (3, 4)
    assert (plus["base"], plus["per"]) == (4, 5)          # 19 with a full shrine
    edict = [fx for fx in _card("edict_of_cleansing+").effects
             if fx.get("op") == "apply_power"][0]
    assert edict["amount"] == 4


def test_fox_trick_draws_2():
    st = _state()
    _play(st, "fox_trick")
    assert len(st.player.hand) == 2
    weak = [fx for fx in _card("fox_trick+").effects if fx.get("op") == "apply_power"][0]
    assert weak["amount"] == 3
