"""Pins for the pilot's incoming-damage forecast and its self-buff cap.

Two scorer inputs that no other test exercises: the multi-hit multiplier on
an enemy telegraph (the number the pilot blocks against) and the per-power
ceiling on self `apply_power` scaling value.
"""

from tier0 import constants as C
from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state


def _telegraph(amount, times=None):
    intent = {"kind": "attack", "amount": amount}
    if times is not None:
        intent["times"] = times
    return make_enemy(hp=60, intents=[intent])


def _self_power(amount):
    return Card(
        id="probe_self_power", name="Probe Self Power", cost=1, type="power",
        effects=[{"op": "apply_power", "power": "strength",
                  "amount": amount, "target": "self"}],
    )


def test_incoming_damage_counts_every_hit_of_a_multi_hit_intent():
    """A telegraphed attack that lands `times` hits forecasts as per-hit
    damage multiplied by the hit count, not as a single hit."""
    single = make_state([_telegraph(6)])
    triple = make_state([_telegraph(6, times=3)])

    assert policy._incoming_damage(single) == 6
    assert policy._incoming_damage(triple) == 18


def test_block_is_valued_against_the_whole_multi_hit_swing():
    """Block is priced by the damage it actually prevents, so against a
    multi-hit telegraph it is worth up to the full multiplied swing rather
    than being clipped to one hit's worth."""
    state = make_state([_telegraph(6, times=3)])
    blocker = Card(id="probe_blk", name="Probe Blk", cost=1, type="skill",
                   effects=[{"op": "block", "amount": 15}])

    assert policy._block_value(state, blocker) == 15


def test_self_power_scaling_value_is_capped_at_six_stacks():
    """Self-applied power stacks are priced at 3 per stack, and the count
    that gets priced stops at 6 -- a bigger grant is worth no more than a
    6-stack one."""
    state = make_state([make_enemy()])
    assert state.turn == 0            # no setup taper on the pinned numbers

    assert policy._scaling_value(state, _self_power(5)) == 15
    assert policy._scaling_value(state, _self_power(6)) == 18
    assert policy._scaling_value(state, _self_power(7)) == 18
    assert policy._scaling_value(state, _self_power(9)) == 18


def test_self_power_scaling_value_still_decays_with_the_setup_taper():
    """The capped stack value is the pre-taper number: it is scaled down by
    how far into the fight the buff would land."""
    state = make_state([make_enemy()])
    state.turn = int(C.PILOT_SETUP_TAPER_TURNS) // 2

    assert policy._scaling_value(state, _self_power(9)) == 9.0
