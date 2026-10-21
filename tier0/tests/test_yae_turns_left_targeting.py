"""Turns-left targeting (the user's ruling, 2026-10-20), from a friend's
report: "A couple of times I had a Sakura with 7+ turns left on it and the
kill oldest card replaced it with one only had 3 turns." The user: "For cards
designed to benefit you, they should target the one with the most turns left.
For cards designed to cost something, they should target the one with the
fewest turns left. This might not be the same as the planting order."

A cost (Fallen Petals, Replanting, Hide Behind the Shrine) reaches
`next_to_wither`; a benefit (Evergreen Charm, Falling Blossom, Dawn Prayer,
Fox Fire Draft, a Level tie) reaches `last_to_wither`. Sim half; the C# half
is `klee-mod/KleeTests/Prototype/YaeTurnsLeftTargetingTests.cs`.
"""

from __future__ import annotations

import random

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


def _play(st, name):
    card = loader.get_card("proto_ym_" + name)
    st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)
    return card


def _led(st):
    return Y.ledger(st.player)


def _friends_shrine():
    """Evergreen Charm twice on the only Sakura (A, 7 turns left), then two
    more planted (3 each)."""
    st = _state()
    Y.plant(st, 1)
    a = _led(st).sakura[0]
    _play(st, "evergreen_charm")
    _play(st, "evergreen_charm")
    assert a.turns_left == 7
    Y.plant(st, 2)
    return st, a


def test_replanting_withers_the_3_turn_sakura_not_the_7_turn_one():
    st, a = _friends_shrine()
    b = _led(st).sakura[1]
    assert Y.next_to_wither(_led(st)) is b       # 3 and 3: the older
    _play(st, "replanting")
    assert a in _led(st).sakura and a.turns_left == 7
    assert b not in _led(st).sakura
    assert len(_led(st).sakura) == 3
    assert _led(st).sakura[-1].level == b.level + 1


def test_fallen_petals_and_hide_behind_the_shrine_wither_the_fewest_turns_left():
    st, a = _friends_shrine()
    _, b, c = _led(st).sakura
    _play(st, "fallen_petals")
    assert b not in _led(st).sakura
    _play(st, "hide_behind_the_shrine")
    assert _led(st).sakura == [a]
    assert c not in _led(st).sakura


def test_the_benefit_cards_reach_the_most_turns_left():
    st, a = _friends_shrine()
    assert Y.last_to_wither(_led(st)) is a
    _play(st, "dawn_prayer")                      # its Levels land on A
    assert [s.level for s in _led(st).sakura] == [3, 1, 1]
    hp = st.enemies[0].hp
    _play(st, "falling_blossom")                  # A strikes this enemy
    assert st.enemies[0].hp < hp
    assert a.turns_left == 7
    loader_up = loader.get_card("proto_ym_fox_fire_draft+")
    st.player.hand.append(loader_up)
    combat.play_card(st, loader_up)               # A, then the newer 3
    assert [s.has(Y.FOX_FIRE) for s in _led(st).sakura] == [True, False, True]


def test_a_tie_goes_to_the_newest_for_a_benefit_and_the_oldest_for_a_cost():
    st = _state()
    assert Y.last_to_wither(_led(st)) is None
    assert Y.next_to_wither(_led(st)) is None
    Y.plant(st, 3)
    led = _led(st)
    assert Y.last_to_wither(led) is led.sakura[2]
    assert Y.next_to_wither(led) is led.sakura[0]
    assert Y.wither_order(led) == led.sakura


def test_deadline_extension_comes_first_for_a_benefit_and_last_for_a_cost():
    st = _state()
    Y.plant(st, 3)
    led = _led(st)
    dl = led.sakura[0]
    dl.add(Y.DEADLINE)
    led.sakura[2].turns_left += 3                 # 6 turns, no Deadline
    assert Y.last_to_wither(led) is dl           # 3 turns, but it never ticks
    assert Y.next_to_wither(led) is led.sakura[1]
    assert Y.wither_order(led) == [led.sakura[1], led.sakura[2], dl]


def test_evergreen_charm_skips_a_deadline_extension_sakura():
    st = _state()
    Y.plant(st, 2)
    first, dl = _led(st).sakura
    dl.add(Y.DEADLINE)
    _play(st, "evergreen_charm")
    assert first.turns_left == Y.SAKURA_TURNS + 2
    assert dl.turns_left == Y.SAKURA_TURNS
    # Every one carries it: none is extended.
    st = _state()
    Y.plant(st, 1, annotation=Y.DEADLINE)
    assert Y.extend_most_turns_left(_led(st), 2) is False
    assert _led(st).sakura[0].turns_left == Y.SAKURA_TURNS


def test_a_level_tie_goes_to_the_most_turns_left():
    st = _state()
    Y.plant(st, 1, lasts=2)                       # 5 turns
    Y.plant(st, 1)                                # 3 turns
    led = _led(st)
    assert Y.highest(led) is led.sakura[0]
    assert Y.highest(led, Y.DAMAGE_KINDS) is led.sakura[0]
