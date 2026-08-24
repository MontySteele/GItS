"""EB-118's two switches: one thrown, one still off, and the code behind both.

TWO flags rather than one, and that is a ruling rather than an accident: R191
gave the mode chooser its own activation window and the 2A pair flips first in
the ruled sequence, so one flag would have activated mode valuation inside 2A's
window. **That is no longer hypothetical -- 2A is thrown and 2C is not**, and
this file is where the separation is asserted rather than assumed:

  `policy.PILOT_POLICIES_ENABLED`   True  -- Phase 2A, 2026-08-24
                                             (`POLICY_VERSION` 8,
                                              `PILOT_WEIGHTS_VERSION` 3)
  `policy.MODE_CHOOSER_ENABLED`     False -- 2C, staged, its bump reserved

WHAT THIS FILE GUARDED, AND WHAT IT GUARDS NOW. Written for the staging window,
it held the inert half of the argument: both flags shipped False, so bomb
placement was still `_pick_targets`' lowest-HP aim, a chosen exhaust was still
`_worst_card`'s highest-cost non-Attack, a modal card still resolved the fixed
index, and every Klee, Kokomi and Furina number on the branch -- the frozen
calibration battery included -- was the number it had been.

The 2A half of that window has closed. Its tests are NOT deleted with it,
because the code they pin is not: the pre-policy path is still live behind the
switch and is the only way the pre-flip world can be run at all -- it is what
`tier05.pilot_weight_sweep.sandbox(force=False)` holds down to prove that a
weight reaches the engine ONLY through the gate, which is the byte-identity arm
the whole sweep's validity rests on. So the 2A tests below now state the switch
state they assert in instead of inheriting it from the shipped default:

  * the default assertion INVERTED -- it pins ON, and pins that the gate hands
    the policy module back rather than `None`;
  * the two behaviour tests keep their boards and their claims verbatim and
    force the switch off for their own duration, which is exactly the state
    they were always describing;
  * the tie-break mirror is unchanged: it never depended on the switch.

The 2C half is untouched by the 2A flip and its assertions stand verbatim.
The ON halves are test_eb118_policies and test_eb118_mode_chooser.
"""

import pytest

from tier0.content import loader
from tier0.engine import effects
from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state


@pytest.fixture
def policies_off(monkeypatch):
    """The 2A pair's legacy path, held down explicitly.

    Before the flip this fixture would have been a no-op and the tests below
    read the shipped default. Naming the state is what keeps them meaningful
    across a switch that has now moved once and may move again.
    """
    monkeypatch.setattr(policy, "PILOT_POLICIES_ENABLED", False)


def _skill(cid, cost, effs=None, **kw) -> Card:
    return Card(id=cid, name=cid, cost=cost, type="skill",
                effects=effs or [], **kw)


def test_the_switch_ships_on():
    """The inversion of this file's founding assertion, kept rather than
    deleted: a flip that quietly removed the line pinning the default would
    leave nothing at all asserting which world ships."""
    assert policy.PILOT_POLICIES_ENABLED is True
    assert effects._pilot_policies() is policy


def test_the_gate_still_closes_when_the_switch_is_off(policies_off):
    """The gate is a switch, not a landing: `_pilot_policies` returns None on
    the off side, which is what makes the two fallbacks below reachable."""
    assert effects._pilot_policies() is None


def test_the_mode_chooser_switch_ships_off_too():
    assert policy.MODE_CHOOSER_ENABLED is False
    assert effects._mode_chooser() is None


def test_the_two_switches_are_independent():
    """R191's own window, mechanically -- and no longer a hypothetical.

    This used to monkeypatch the 2A flag on to show that doing so left mode
    valuation alone. The flag is now ON in the SHIPPED tree, so the assertion
    is made against the tree itself: 2A is live, 2C is not, and 2C therefore
    still has a flip of its own to attribute a POLICY_VERSION bump to.
    """
    assert policy.PILOT_POLICIES_ENABLED is True
    assert policy.MODE_CHOOSER_ENABLED is False
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
    The battery cannot move on this branch, and this is why. Unaffected by the
    2A flip: Deep Breath places no bomb and exhausts nothing chosen.
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


def test_placement_is_still_the_lowest_hp_aim(policies_off):
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


def test_chosen_exhaust_is_still_highest_cost_non_attack(policies_off):
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
    nothing to say about stops resolving the way it used to. Switch-independent
    by construction -- it compares two pure functions -- so it is asserted
    against the shipped world, which is now the ON one."""
    cards = [_skill("a", 1), _skill("b", 3),
             Card(id="c", name="c", cost=3, type="attack", effects=[])]
    assert effects._worst_card(cards) is max(cards, key=policy._legacy_worst_key)
