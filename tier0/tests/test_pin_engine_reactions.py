"""Pins for tier0/engine/reactions.py quantities the suite left unmeasured
(mutation sweep s15, engine-reactions group).

Crystallize's Block is ADDED to whatever Block the player is already
holding (it never replaces it), and Catalytic Converter pays nothing without
its power. (Its Burst half left with the Burst meter, 2026-10-08.)
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


# --- Catalytic Converter is a rider on its power (HIGH-8) ---


def test_no_catalytic_sparks_without_the_power():
    """The catalytic payout is a rider on the power, not a baseline: a
    reaction with no reaction_bonus_spark_energy stacks grants no sparks."""
    state = make_state(enemies=[make_enemy(hp=60)])
    enemy = state.enemies[0]

    hit(state, enemy, "pyro", 0)
    hit(state, enemy, "hydro", 5)

    assert state.player.sparks == 0
