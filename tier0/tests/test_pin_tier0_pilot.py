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


# --- EB-5: the weight set and the stamp that labels it --------------------
#
# The stamp is only worth having if editing a weight forces a decision about
# it, so the two are pinned TOGETHER: change any value below and this test
# fails, and the fix is to bump C.PILOT_WEIGHTS_VERSION (or to say in the
# commit why the reading did not move). That is the DRAFTER_VERSION
# discipline made mechanical rather than remembered.
#
# v1 was the set as EB-5 found it -- nothing retuned, values byte-identical to
# the inline literals they replaced. v2 (POLICY 7, R176) is v1 plus one NEW
# weight, `PILOT_COMPANION_COPY_VALUE`, filed in the policy.py half: no v1
# value moved, but the SET did, which is what the stamp labels.
PILOT_WEIGHT_SET_V2 = {
    "PILOT_REACTION_TRIGGER_VALUE": 6.0,
    "PILOT_REACTION_SEED_VALUE": 2.0,
    "PILOT_DRAW_WHILE_VALUE": 2.0,
    "PILOT_SPARK_VALUE": 0.7,
    "PILOT_BURST_DIVISOR": 10.0,
    "PILOT_ENCORE_VALUE": 0.8,
    "PILOT_SPOTLIGHT_DESIGNATE_SEQUENCING": 20.0,
    "PILOT_SPOTLIGHT_DESIGNATE_GENERATOR": 0.1,
    "PILOT_SPOTLIGHT_DESIGNATE_OPENING": 4.0,
    "PILOT_SPOTLIGHT_DESIGNATE_REDESIGNATE": 0.3,
    "PILOT_SPOTLIGHT_BOOST_COMBAT": 3.0,
    "PILOT_SPOTLIGHT_BOOST_TURN": 1.5,
    "PILOT_SPOTLIGHT_BOOST_EARLY": 0.3,
    "PILOT_GUEST_STAR_VALUE": 2.5,
    "PILOT_SPOTLIGHT_COPY_VALUE": 3.5,
    "PILOT_SETUP_TAPER_TURNS": 12.0,
    "PILOT_SELF_POWER_STACK_CAP": 6,
    "PILOT_SELF_POWER_VALUE": 3,
    "PILOT_ENEMY_DEBUFF_VALUE": 2,
    "PILOT_SELF_DAMAGE_COST_WEIGHT": 0.5,
    "PILOT_FUTURE_DAMAGE_DISCOUNT": 0.8,
    "PILOT_CHARGE_GAIN_VALUE": 0.6,
    "PILOT_CONSCRIPT_CREATE_VALUE": 3.0,
    "PILOT_CONSCRIPT_TRANSFORM_VALUE": 2.0,
    "PILOT_EXHAUST_ALL_ESTIMATE": 3,
    "PILOT_DELIBERATE_EXHAUST_VALUE": 0.8,
    "PILOT_SELF_MILL_VALUE": 0.5,
    "PILOT_GARMENT_CHARGE_VALUE": 1.2,
    "PILOT_GARMENT_BASE_VALUE": 2.0,
}
# The half that stays in policy.py for the C# parity reason written at its
# head. Filed elsewhere, stamped the same.
POLICY_FILED_WEIGHT_SET_V2 = {
    "STOKE_DEPLOY_OPEN": 6.0,
    "STOKE_DEPLOY_FULL": 1.5,
    "STOKE_RUNWAY_TURNS": 2.0,
    "STOKE_FUEL_HUNGRY": 1.2,
    "STOKE_FUEL_SATED": 0.15,
    # v2, POLICY 7 (R176): the companion-copy valuation in `_tempo_value`.
    "PILOT_COMPANION_COPY_VALUE": 1.5,
}


def test_the_pilot_weight_set_is_stamped_at_v2():
    assert C.PILOT_WEIGHTS_VERSION == 2
    for name, value in PILOT_WEIGHT_SET_V2.items():
        assert getattr(C, name) == value, name
    for name, value in POLICY_FILED_WEIGHT_SET_V2.items():
        assert getattr(policy, name) == value, name


def test_every_pilot_weight_in_constants_is_in_the_stamped_set():
    """A weight added to the `PILOT_*` block without being listed above would
    be unstamped again -- the exact defect EB-5 closed. Catching it here is
    what keeps the stamp honest as the pilot grows."""
    live = {n for n in dir(C)
            if n.startswith("PILOT_") and n != "PILOT_WEIGHTS_VERSION"}
    assert live == set(PILOT_WEIGHT_SET_V2)


def test_the_pilot_stamp_is_not_part_of_the_run_cell_stamp():
    """It is an instrument version on the A6 pattern, not a fourth axis of
    RT/D/P/C -- adding it moved no cell and archived no number."""
    from tier05 import cells
    assert "PILOT_WEIGHTS_VERSION" not in cells.Cell(name="probe").stamp()
