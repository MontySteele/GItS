"""Pins for tier0/engine/powers.py quantities the suite left unmeasured
(mutation sweep s15, engine-powers group).

Two rules live here: Metallicize's turn-start payout is ADDED to whatever
block the fighter is already holding rather than replacing it, and a power
applied with a stack cap stops at that cap exactly, no matter how many
applications or how big a single one is.
"""

from tier0.engine import combat, powers
from tier0.tests.conftest import make_enemy, make_state


# --- Metallicize adds, never overwrites (HIGH-5) ---

def test_metallicize_adds_to_block_the_fighter_already_holds():
    """Metallicize's turn-start block is a gain on top of current block: a
    player standing on 7 block with 3 Metallicize starts the turn on 10."""
    state = make_state()
    p = state.player
    p.block = 7
    p.powers["metallicize"] = 3

    powers.on_turn_start(state, p)

    assert p.block == 10


def test_metallicize_adds_to_enemy_block_the_enemy_already_holds():
    """The same additive rule applies on the enemy side: an enemy holding 4
    block with 2 Metallicize reaches 6 at its turn start, not 2."""
    enemy = make_enemy()
    state = make_state(enemies=[enemy])
    enemy.block = 4
    enemy.powers["metallicize"] = 2

    powers.on_turn_start(state, enemy)

    assert enemy.block == 6


def test_metallicize_stacks_on_top_of_block_carried_by_barricade():
    """Barricade suppresses the turn-start block clear, so a Metallicize
    player keeps last turn's block AND gains the Metallicize amount on top of
    it: 9 carried plus 3 Metallicize opens the turn on 12."""
    state = make_state()
    p = state.player
    p.block = 9
    p.powers["barricade"] = 1
    p.powers["metallicize"] = 3

    combat._player_turn(state, lambda *a, **k: None)

    assert p.block == 12


# --- stack caps clamp at the cap (MEDIUM-2) ---

def test_capped_power_stops_at_max_stacks_across_applications():
    """A max_stacks cap bounds the RUNNING TOTAL: applying 4 stacks of a
    cap-6 power twice leaves 6, not 8 and not 7."""
    state = make_state()
    p = state.player

    powers.apply_power(state, p, "prevent_exhaust_ward", 4, max_stacks=6)
    assert p.powers["prevent_exhaust_ward"] == 4

    powers.apply_power(state, p, "prevent_exhaust_ward", 4, max_stacks=6)
    assert p.powers["prevent_exhaust_ward"] == 6


def test_single_application_over_the_cap_lands_exactly_on_the_cap():
    """One oversized application is clamped the same way: 9 stacks of a cap-6
    power land on 6 exactly."""
    state = make_state()
    enemy = state.enemies[0]

    powers.apply_power(state, enemy, "prevent_exhaust_ward", 9, max_stacks=6)

    assert enemy.powers["prevent_exhaust_ward"] == 6
