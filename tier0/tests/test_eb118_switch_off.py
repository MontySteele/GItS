"""EB-118 with the switches OFF: the three call sites are the pre-policy code.

The whole staging argument rests on this file. `policy.PILOT_POLICIES_ENABLED`
ships False, so bomb placement is still `_pick_targets`' lowest-HP aim and a
chosen exhaust is still `_worst_card`'s highest-cost non-Attack; 2C's own
`policy.MODE_CHOOSER_ENABLED` ships False beside it, so a modal card still
resolves the fixed index the seam was staged with -- and every Klee, Kokomi
and Furina number on this branch, the frozen calibration battery included, is
the number it was. The ON halves are test_eb118_policies and
test_eb118_mode_chooser.

TWO flags rather than one, and that is a ruling rather than an accident: R191
gave the mode chooser its own activation window and the 2A pair flips first in
the ruled sequence, so one flag would have activated mode valuation inside
2A's window.
"""

from tier0.content import loader
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


def test_the_mode_chooser_switch_ships_off_too():
    assert policy.MODE_CHOOSER_ENABLED is False
    assert effects._mode_chooser() is None


def test_the_two_switches_are_independent(monkeypatch):
    """R191's own window, mechanically. Flipping the 2A pair must not turn
    mode valuation on, or 2C would have no flip of its own to attribute a
    POLICY_VERSION bump to."""
    monkeypatch.setattr(policy, "PILOT_POLICIES_ENABLED", True)
    assert effects._pilot_policies() is policy
    assert effects._mode_chooser() is None


def test_a_modal_card_still_resolves_the_fixed_index():
    """The staged behaviour, unchanged: mode 0, whatever the board says. The
    chooser exists and would take the second mode here -- that inversion is
    pinned in test_eb118_mode_chooser -- and with the switch off it is not
    consulted at all."""
    state = make_state([make_enemy(hp=60)])
    modes = [{"label": "a", "effects": [{"op": "block", "amount": 5}]},
             {"label": "b", "effects": [{"op": "damage", "amount": 9,
                                         "target": "enemy"}]}]
    assert effects._chosen_mode(state, modes, None) == 0
    effects.resolve_card(state, _skill("probe", 1,
                                       [{"op": "choose_one", "modes": modes}]))
    assert state.player.block == 5
    assert state.enemies[0].hp == 60


def test_deep_breath_resolves_exactly_as_it_did_before_the_conversion():
    """THE INERTNESS PROOF for the sheet half of 2C.

    The modal conversion kept mode 1 as the card's own shipped body, and with
    the switch off mode 1 is the mode that resolves -- so the converted card
    and the effect list it replaced put the same numbers on the same board.
    The battery cannot move on this branch, and this is why.
    """
    old_body = [{"op": "energy", "amount": 1},
                {"op": "gain_encore", "amount": 2}]
    before = make_state([make_enemy()])
    before.player.energy, before.player.encore = 3, 4
    effects.resolve_card(before, _skill("deep_breath", 1, old_body,
                                        exhaust=True))

    after = make_state([make_enemy()])
    after.player.energy, after.player.encore = 3, 4
    effects.resolve_card(after, loader._card_index()["deep_breath"])

    assert (after.player.energy, after.player.encore, after.player.hp) \
        == (before.player.energy, before.player.encore, before.player.hp)
    assert (after.player.energy, after.player.encore) == (4, 6)


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
