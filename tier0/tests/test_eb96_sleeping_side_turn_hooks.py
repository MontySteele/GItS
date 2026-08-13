"""EB-96: a sleeping enemy is still a side-turn participant.

`_enemy_turn` returned as soon as `sleep_turns > 0` -- above the block clear,
above `powers.on_turn_start` (metallicize, dot), above
`refpowers.enemy_side_turn_start` (poison), and never reaching
`powers.on_turn_end` (duration decay, temp-Strength revert). So a sleeping
enemy's debuffs never decayed, its dot stalled and its temporary Strength
never reverted.

The authority counts a sleeping creature as a participant: `CombatManager.cs`
builds `creaturesStartingTurn` with no Asleep filter, `Creature.cs` shows
sleep suppressing only `TakeTurn`, and `AsleepPower.cs` itself hangs off
`AfterSideTurnEnd(participants.Contains(Owner))`.

Two things the early return WAS load-bearing for are asserted preserved
below: no `advance_intent` on a sleep turn, and no Nemesis Intangible toggle
on a sleep turn.
"""

from tier0.engine import combat, powers
from tier0.tests.conftest import make_enemy, make_state


def _sleeper(**kw):
    enemy = make_enemy(**kw)
    enemy.sleep_turns = 1
    return enemy


def test_sleeping_enemy_dot_ticks():
    enemy = _sleeper(hp=50)
    state = make_state(enemies=[enemy])
    enemy.powers["dot"] = 3
    combat._enemy_turn(state, enemy)
    assert enemy.hp == 47
    assert enemy.powers["dot"] == 2


def test_sleeping_enemy_duration_debuffs_decay():
    enemy = _sleeper()
    state = make_state(enemies=[enemy])
    powers.apply_power(state, enemy, "vulnerable", 2, applier=state.player)
    powers.apply_power(state, enemy, "weak", 1, applier=state.player)
    combat._enemy_turn(state, enemy)
    assert enemy.powers["vulnerable"] == 1
    assert enemy.powers.get("weak", 0) == 0


def test_sleeping_enemy_temp_strength_reverts():
    enemy = _sleeper()
    state = make_state(enemies=[enemy])
    enemy.powers["strength"] = -4
    enemy.powers["temp_strength_down"] = 4        # Mangle
    combat._enemy_turn(state, enemy)
    assert enemy.powers.get("strength", 0) == 0
    assert "temp_strength_down" not in enemy.powers


def test_sleeping_enemy_block_is_cleared():
    enemy = _sleeper()
    state = make_state(enemies=[enemy])
    enemy.block = 12
    combat._enemy_turn(state, enemy)
    assert enemy.block == 0


def test_sleeping_enemy_metallicize_still_grants_block():
    """Site A runs, so a sleeper that owns Metallicize re-earns its block
    after the clear -- the same order an acting enemy gets."""
    enemy = _sleeper()
    state = make_state(enemies=[enemy])
    enemy.block = 12
    enemy.powers["metallicize"] = 3
    combat._enemy_turn(state, enemy)
    assert enemy.block == 3


def test_sleeping_enemy_burns_exactly_one_sleep_turn_and_takes_no_action():
    enemy = _sleeper(hp=50, intents=[{"kind": "attack", "amount": 9},
                                     {"kind": "attack", "amount": 9}])
    enemy.sleep_turns = 2
    state = make_state(enemies=[enemy])
    hp0 = state.player.hp
    combat._enemy_turn(state, enemy)
    assert enemy.sleep_turns == 1
    assert state.player.hp == hp0                # TakeTurn is what sleep stops


def test_sleep_turn_does_not_advance_the_intent():
    """PRESERVED. The sleeper wakes onto the intent it was pointed at."""
    enemy = _sleeper(intents=[{"kind": "attack", "amount": 9},
                              {"kind": "attack", "amount": 1}])
    state = make_state(enemies=[enemy])
    combat._enemy_turn(state, enemy)
    assert enemy.intent_index == 0
    hp0 = state.player.hp
    combat._enemy_turn(state, enemy)             # awake now
    assert hp0 - state.player.hp == 9
    assert enemy.intent_index == 1


def test_sleep_turn_does_not_toggle_nemesis_intangible():
    """PRESERVED. _settle_phases opens Intangible at the revive, and the
    respawn sleep turn must not immediately close it (dossier turn table)."""
    enemy = _sleeper()
    state = make_state(enemies=[enemy])
    enemy.powers["nemesis"] = 1
    enemy.powers["intangible"] = 1
    combat._enemy_turn(state, enemy)
    assert enemy.powers.get("intangible", 0) == 1


def test_a_sleeper_killed_by_its_own_dot_does_not_reach_the_turn_end():
    enemy = _sleeper(hp=2)
    state = make_state(enemies=[enemy])
    enemy.powers["dot"] = 5
    powers.apply_power(state, enemy, "vulnerable", 2, applier=state.player)
    combat._enemy_turn(state, enemy)
    assert not enemy.alive
    assert enemy.powers["vulnerable"] == 2       # same as the acting path
