from tier0.engine import powers, refpowers
from tier0.tests.conftest import make_state


def test_weak_vulnerable_decay(state):
    """EB-95: the player's durations tick at the ENEMY side end, not at the
    player's own turn end. Stacks written straight into the dict carry no
    skip flag, so the first enemy-side end spends one."""
    p = state.player
    p.powers["weak"] = 2
    p.powers["vulnerable"] = 1
    powers.on_turn_end(state, p)
    assert p.powers["weak"] == 2              # the player's turn end does NOT tick
    assert p.powers["vulnerable"] == 1
    refpowers.after_enemy_side_turn_end(state)
    assert p.powers["weak"] == 1
    assert p.powers["vulnerable"] == 0


def test_strength_not_decaying(state):
    p = state.player
    p.powers["strength"] = 3
    powers.on_turn_end(state, p)
    assert p.powers["strength"] == 3


def test_metallicize_grants_block(state):
    p = state.player
    p.powers["metallicize"] = 3
    powers.on_turn_start(state, p)
    assert p.block == 3


def test_dot_ticks_and_decays(state):
    e = state.enemies[0]
    e.block = 10
    e.powers["dot"] = 4
    powers.on_turn_start(state, e)
    assert e.hp == 46          # ignores block
    assert e.powers["dot"] == 3
