"""Pins for tier0/engine/reactions.py quantities the suite left unmeasured
(mutation sweep s15, engine-reactions group).

Two rules live here: Crystallize's Block is ADDED to whatever Block the
player is already holding (it never replaces it), and Catalytic Converter's
bonus burst energy scales with the number of reaction_bonus_spark_energy
stacks rather than paying a flat amount per reaction.
"""

from tier0 import constants as C
from tier0.engine import reactions
from tier0.tests.conftest import make_enemy, make_state


def hit(state, enemy, element, dmg=10):
    return reactions.resolve_hit(state, enemy, element, dmg)


# --- Crystallize Block accumulates (HIGH-9) ---

def test_crystallize_block_adds_to_block_the_player_already_holds():
    """Crystallize grants Block on top of existing Block: a player standing
    on 6 Block who triggers a geo reaction ends on 6 + CRYSTALLIZE_BLOCK,
    never on CRYSTALLIZE_BLOCK alone."""
    state = make_state()
    enemy = state.enemies[0]
    state.player.block = 6

    hit(state, enemy, "pyro", 0)
    hit(state, enemy, "geo", 5)

    assert state.player.block == 6 + C.CRYSTALLIZE_BLOCK


def test_two_crystallizes_in_a_row_stack_their_block():
    """Repeated geo reactions each pay their own Block: two Crystallizes in
    one turn leave the player on twice CRYSTALLIZE_BLOCK."""
    state = make_state()
    enemy = state.enemies[0]

    hit(state, enemy, "pyro", 0)
    hit(state, enemy, "geo", 5)
    hit(state, enemy, "pyro", 0)
    hit(state, enemy, "geo", 5)

    assert state.player.block == 2 * C.CRYSTALLIZE_BLOCK


# --- Catalytic burst scales per stack (HIGH-8) ---

def test_catalytic_burst_scales_with_reaction_bonus_stacks():
    """Catalytic Converter pays CATALYTIC_BURST_PER_REACTION burst energy
    PER STACK of reaction_bonus_spark_energy: at two stacks one reaction
    grants double the burst (and double the sparks) of one stack."""
    state = make_state()
    enemy = state.enemies[0]
    state.player.powers["reaction_bonus_spark_energy"] = 2

    hit(state, enemy, "pyro", 0)
    hit(state, enemy, "hydro", 5)

    catalytic = [ev["amount"] for ev in state.log
                 if ev["event"] == "burst_income"
                 and ev["source"] == "catalytic"]
    assert catalytic == [2 * C.CATALYTIC_BURST_PER_REACTION]
    assert state.player.sparks == 2


def test_catalytic_burst_at_one_stack_pays_the_base_amount():
    """One stack of reaction_bonus_spark_energy is the unit of the scaling:
    a single reaction grants exactly CATALYTIC_BURST_PER_REACTION burst and
    one spark."""
    state = make_state()
    enemy = state.enemies[0]
    state.player.powers["reaction_bonus_spark_energy"] = 1

    hit(state, enemy, "pyro", 0)
    hit(state, enemy, "hydro", 5)

    catalytic = [ev["amount"] for ev in state.log
                 if ev["event"] == "burst_income"
                 and ev["source"] == "catalytic"]
    assert catalytic == [C.CATALYTIC_BURST_PER_REACTION]
    assert state.player.sparks == 1


def test_no_catalytic_burst_without_the_power():
    """The catalytic payout is a rider on the power, not a baseline: a
    reaction with no reaction_bonus_spark_energy stacks grants no catalytic
    burst income and no sparks."""
    state = make_state(enemies=[make_enemy(hp=60)])
    enemy = state.enemies[0]

    hit(state, enemy, "pyro", 0)
    hit(state, enemy, "hydro", 5)

    assert not [ev for ev in state.log
                if ev["event"] == "burst_income"
                and ev["source"] == "catalytic"]
    assert state.player.sparks == 0
