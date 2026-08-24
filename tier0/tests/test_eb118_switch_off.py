"""EB-118 with the switch OFF: the two call sites are the pre-policy code.

The whole staging argument rests on this file. `policy.PILOT_POLICIES_ENABLED`
ships False, so bomb placement is still `_pick_targets`' lowest-HP aim and a
chosen exhaust is still `_worst_card`'s highest-cost non-Attack -- and every
Klee/Kokomi number on this branch, the frozen calibration battery included,
is the number it was. The ON half lives in test_eb118_policies.
"""

from tier0.engine import effects
from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state


def _skill(cid, cost, effs=None, **kw) -> Card:
    return Card(id=cid, name=cid, cost=cost, type="skill",
                effects=effs or [], **kw)


def test_the_switch_ships_off():
    assert policy.PILOT_POLICIES_ENABLED is False
    assert effects._pilot_policies() is None


def test_placement_is_still_the_lowest_hp_aim():
    """The inversion test_eb118_policies pins, from the other side: this bomb
    is thrown away on a target that cannot absorb it, and with the switch off
    that is still exactly what happens."""
    low, high = make_enemy(hp=3, name="low"), make_enemy(hp=60, name="high")
    state = make_state([low, high])
    effects._op_place_bomb(state, {"op": "place_bomb", "amount": 1,
                                   "target": "enemy", "bomb_damage": 5},
                           _skill("probe", 1))
    assert len(low.bombs) == 1
    assert high.bombs == []


def test_chosen_exhaust_is_still_highest_cost_non_attack():
    dud = _skill("dud", 0)
    payoff = _skill("payoff", 2, [{"op": "block", "amount": 12}])
    state = make_state([make_enemy()])
    state.player.hand = [dud, payoff]
    effects._op_exhaust_from(state, {"op": "exhaust_from", "amount": 1,
                                     "select": "chosen"}, _skill("src", 1))
    assert [c.id for c in state.player.exhaust_pile] == ["payoff"]


def test_the_legacy_tie_break_mirror_is_in_sync():
    """`policy._legacy_worst_key` exists so ties in the ON path resolve to the
    pick the OFF path makes. If the two ever drift, a board the policy has
    nothing to say about stops resolving the way it used to."""
    cards = [_skill("a", 1), _skill("b", 3),
             Card(id="c", name="c", cost=3, type="attack", effects=[])]
    assert effects._worst_card(cards) is max(cards, key=policy._legacy_worst_key)
