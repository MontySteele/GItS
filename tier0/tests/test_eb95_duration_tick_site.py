"""EB-95: the player's duration debuffs tick at AfterSideTurnEnd(enemy).

The defect: `powers.on_turn_end` decremented every DECAYING power at the
OWNER's turn end, and `combat._player_turn` calls it as the last act of the
player turn -- BEFORE `_run_rounds` takes the enemy turns the debuff is
supposed to amplify. So an enemy-applied Vulnerable covered one fewer enemy
round than the game does, and a 1-stack application covered none at all.

The authority ticks duration debuffs at `AfterSideTurnEnd(side == Enemy)` and
additionally sets `SkipNextDurationTick` inside `Apply` for a Debuff freshly
landed on a player-side creature, so the application is not eaten by the tick
at the end of the very side turn that applied it.

Two things must NOT move, and are asserted below:
  * enemy-OWNED durations keep ticking at their own turn end (bag_of_marbles
    and fear_potion prose depend on a player-applied Vulnerable covering
    exactly the enemy action it was bought for);
  * enemy-applied Weak/Frail on the player were already correct -- they bite
    during PLAYER turns, which precede the tick under either clock.
"""

from tier0 import constants as C
from tier0.engine import combat, powers, refpowers
from tier0.tests.conftest import make_enemy, make_state


def _round(state, enemy):
    """One full round from the player's turn end through the enemy side."""
    powers.on_turn_end(state, state.player)          # AfterSideTurnEnd(player)
    combat._enemy_turn(state, enemy)
    refpowers.after_enemy_side_turn_end(state)       # AfterSideTurnEnd(enemy)


def test_enemy_applied_vulnerable_amplifies_the_next_enemy_attack():
    """The red proof. Old clock: the debuff lands on enemy round 1, the
    player's own turn end on round 2 spends it, and the round-2 attack is
    unamplified -- a 1-stack Vulnerable did literally nothing."""
    enemy = make_enemy(intents=[{"kind": "debuff", "power": "vulnerable",
                                 "amount": 1},
                                {"kind": "attack", "amount": 10}])
    state = make_state(enemies=[enemy])
    p = state.player

    _round(state, enemy)                     # enemy applies Vulnerable 1
    # SkipNextDurationTick: the application survives its own side's tick.
    assert p.powers.get("vulnerable", 0) == 1

    hp0 = p.hp
    _round(state, enemy)                     # the attack, amplified
    assert hp0 - p.hp == int(10 * C.VULNERABLE_TAKEN_MULT)
    # ...and now it is spent: exactly one enemy round of cover per stack.
    assert p.powers.get("vulnerable", 0) == 0
    assert "vulnerable" not in p.skip_next_duration_tick


def test_the_skip_is_spent_once_not_held_forever():
    state = make_state()
    p = state.player
    powers.apply_power(state, p, "vulnerable", 2)
    refpowers.after_enemy_side_turn_end(state)       # skipped
    assert p.powers["vulnerable"] == 2
    refpowers.after_enemy_side_turn_end(state)       # ticks
    assert p.powers["vulnerable"] == 1
    refpowers.after_enemy_side_turn_end(state)
    assert p.powers["vulnerable"] == 0


def test_enemy_owned_durations_still_tick_at_the_enemy_turn_end():
    """bag_of_marbles / fear_potion: a player-applied Vulnerable on an enemy
    covers the enemy action it was bought for and then expires. This site is
    already inside the enemy side, so it does not move -- and enemies take no
    skip flag."""
    enemy = make_enemy(intents=[{"kind": "attack", "amount": 5}])
    state = make_state(enemies=[enemy])
    powers.apply_power(state, enemy, "vulnerable", 1, applier=state.player)
    assert not enemy.skip_next_duration_tick
    _round(state, enemy)
    assert enemy.powers.get("vulnerable", 0) == 0


def test_enemy_applied_weak_still_bites_the_following_player_turn():
    """Weak on the player is read during PLAYER turns, before either tick
    site, so the move must leave its uptime exactly where it was: applied on
    enemy round 1, live on player turn 2, gone on player turn 3."""
    enemy = make_enemy(intents=[{"kind": "debuff", "power": "weak",
                                 "amount": 1},
                                {"kind": "attack", "amount": 5},
                                {"kind": "attack", "amount": 5}])
    state = make_state(enemies=[enemy])
    p = state.player

    _round(state, enemy)                     # enemy applies Weak 1
    assert powers.modify_damage_dealt(p, 10) == 10 * C.WEAK_DEALT_MULT
    _round(state, enemy)                     # player turn 2 spent under Weak
    assert powers.modify_damage_dealt(p, 10) == 10
