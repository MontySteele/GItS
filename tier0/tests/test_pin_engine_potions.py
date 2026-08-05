"""Pin tests for the combat-side potion USE POLICY (engine/potions.py).

These lock down the arithmetic and the exact boundaries the bounded-greedy
policy already uses today:

* how a telegraph is turned into a damage estimate (multi-hit ``times``,
  ``ramp``/``ramp_after`` growth),
* the defensive drink trigger (standing Block is netted off first; the drink
  fires at exactly ``POTION_DEFENSIVE_MARGIN`` and not one HP earlier),
* the offensive branch (fire's inclusive kill range, the big-hit threshold
  measured against MAX HP, and the node-context gate closed for the default
  ``""`` battery context).

Every test states the rule it pins in its docstring and asserts the current
behaviour of the code, boundary included.
"""

from tier0 import constants as C
from tier0.engine import potions
from tier0.tests.conftest import make_enemy, make_state


def _attacker(amount, times=1, hp=50, is_boss=False, name="dummy", **extra):
    """A living enemy telegraphing one attack intent."""
    intent = {"kind": "attack", "amount": amount, "times": times}
    intent.update(extra)
    return make_enemy(hp=hp, name=name, is_boss=is_boss, intents=[intent])


def _player(st, hp, max_hp=80, potion_list=(), node_kind="", block=0):
    p = st.player
    p.hp = hp
    p.max_hp = max_hp
    p.block = block
    p.potions = list(potion_list)
    p.node_kind = node_kind
    return p


# ==========================================================================
# Telegraph estimation: every hit counts, and ramp growth counts.
# ==========================================================================

def test_multi_hit_telegraph_is_estimated_as_every_hit_not_one():
    """A telegraphed attack with ``times`` > 1 is estimated as the per-hit
    damage multiplied by the number of hits, so a lethal multi-hit turn reads
    as lethal to the defensive drink trigger."""
    st = make_state(hp=25, enemies=[_attacker(10, times=3)])
    _player(st, hp=25, potion_list=["block_potion"])

    # 10 damage x 3 hits = 30 incoming, not 10.
    assert potions.estimate_incoming(st) == 30
    assert potions._intent_damage(st, st.enemies[0]) == 30

    # ...and the policy acts on the full 30: 25 HP - 30 is lethal, so the
    # block potion is drunk. A single hit of 10 would have left them safe.
    potions.try_use_potions(st)
    assert st.player.potions == []
    assert st.player.block == C.POTION_BLOCK


def test_single_hit_telegraph_of_the_same_size_does_not_trigger_the_drink():
    """CONTROL for the multi-hit rule: the same 10-damage intent with the
    default ``times`` of 1 estimates at 10 and leaves the potion held."""
    st = make_state(hp=25, enemies=[_attacker(10)])
    _player(st, hp=25, potion_list=["block_potion"])

    assert potions.estimate_incoming(st) == 10

    potions.try_use_potions(st)
    assert st.player.potions == ["block_potion"]
    assert st.player.block == 0


def test_ramping_telegraph_estimate_grows_by_ramp_per_turn_after_ramp_after():
    """A ramping intent is estimated at ``amount + ramp * (turn - ramp_after)``
    once the current turn is past ``ramp_after``, and at its plain ``amount``
    on or before that turn -- the growth is never clamped negative."""
    st = make_state(hp=80, enemies=[_attacker(5, ramp=3, ramp_after=2)])
    _player(st, hp=80)

    st.turn = 6                       # 4 turns past ramp_after
    assert potions.estimate_incoming(st) == 5 + 3 * 4

    st.turn = 3                       # 1 turn past ramp_after
    assert potions.estimate_incoming(st) == 5 + 3 * 1

    st.turn = 2                       # exactly at ramp_after: base only
    assert potions.estimate_incoming(st) == 5

    st.turn = 0                       # before it: still base, never below
    assert potions.estimate_incoming(st) == 5


# ==========================================================================
# Defensive trigger: Block first, then the exact margin boundary.
# ==========================================================================

def test_standing_block_is_netted_off_before_the_defensive_drink():
    """The defensive trigger measures the telegraph AFTER the player's
    already-standing Block, so a hit that Block fully absorbs never spends a
    potion."""
    st = make_state(hp=20, enemies=[_attacker(20)])
    _player(st, hp=20, potion_list=["block_potion"], block=25)

    potions.try_use_potions(st)

    assert st.player.potions == ["block_potion"]      # nothing drunk
    assert st.player.block == 25                      # untouched
    assert not any(e["event"] == "potion_used" for e in st.log)


def test_defensive_drink_fires_when_block_only_partly_covers_the_hit():
    """CONTROL for the Block rule: with less Block than the telegraph the
    leftover damage is still lethal, so the defensive potion is drunk."""
    st = make_state(hp=20, enemies=[_attacker(20)])
    _player(st, hp=20, potion_list=["block_potion"], block=0)

    potions.try_use_potions(st)

    assert st.player.potions == []
    assert st.player.block == C.POTION_BLOCK


def test_defensive_drink_fires_at_exactly_the_safety_margin_not_one_hp_above():
    """The defensive potion is drunk when the projected post-turn HP is at or
    below POTION_DEFENSIVE_MARGIN -- a telegraph that lands the player exactly
    on the margin triggers it; one HP of slack does not."""
    margin = C.POTION_DEFENSIVE_MARGIN

    # Projected HP lands exactly ON the margin -> drink.
    on_margin = make_state(hp=20 + margin, enemies=[_attacker(20)])
    _player(on_margin, hp=20 + margin, potion_list=["block_potion"])
    potions.try_use_potions(on_margin)
    assert on_margin.player.potions == []
    assert on_margin.player.block == C.POTION_BLOCK

    # One HP above the margin -> projected to survive, keep the potion.
    above = make_state(hp=21 + margin, enemies=[_attacker(20)])
    _player(above, hp=21 + margin, potion_list=["block_potion"])
    potions.try_use_potions(above)
    assert above.player.potions == ["block_potion"]
    assert above.player.block == 0


# ==========================================================================
# Offensive branch: fire kill range, big-hit threshold, node gate.
# ==========================================================================

def test_fire_potion_kill_range_includes_an_enemy_at_exactly_the_fire_damage():
    """fire_potion is spent to close a kill on any living enemy whose HP is at
    or below POTION_FIRE_DAMAGE -- the bound is inclusive, so an enemy sitting
    on exactly that HP is killable; one HP more is out of range."""
    exact = make_state(hp=80, enemies=[_attacker(5, hp=C.POTION_FIRE_DAMAGE)])
    _player(exact, hp=80, potion_list=["fire_potion"], node_kind="elite")
    potions.try_use_potions(exact)
    assert not exact.enemies[0].alive
    assert exact.player.potions == []

    # One HP outside the range: the kill is not closed, the potion is kept.
    over = make_state(hp=80, enemies=[_attacker(5, hp=C.POTION_FIRE_DAMAGE + 1)])
    _player(over, hp=80, potion_list=["fire_potion"], node_kind="elite")
    potions.try_use_potions(over)
    assert over.enemies[0].alive
    assert over.player.potions == ["fire_potion"]


def test_big_hit_threshold_is_measured_against_max_hp_not_current_hp():
    """The "big telegraphed hit" threshold is POTION_BIG_HIT_FRACTION of the
    player's MAX HP, not of their current HP, so a wounded player does not
    start treating small telegraphs as big ones."""
    # 15 damage is well above 35% of the WOUNDED 20 HP but below 35% of the
    # 80 max HP -> not a big hit -> weak_potion stays held.
    small = make_state(hp=20, enemies=[_attacker(15)])
    _player(small, hp=20, max_hp=80, potion_list=["weak_potion"],
            node_kind="elite")
    assert 15 > C.POTION_BIG_HIT_FRACTION * 20
    assert 15 < C.POTION_BIG_HIT_FRACTION * 80
    potions.try_use_potions(small)
    assert small.player.potions == ["weak_potion"]
    assert small.enemies[0].powers.get("weak", 0) == 0

    # Same wounded player, a telegraph above 35% of MAX HP -> big hit -> drunk.
    big_amount = int(C.POTION_BIG_HIT_FRACTION * 80) + 1
    big = make_state(hp=20, enemies=[_attacker(big_amount)])
    _player(big, hp=20, max_hp=80, potion_list=["weak_potion"],
            node_kind="elite")
    potions.try_use_potions(big)
    assert big.player.potions == []
    assert big.enemies[0].powers.get("weak", 0) == C.POTION_WEAK


def test_default_empty_node_context_never_reaches_the_offensive_branch():
    """The offensive branch is gated to the "elite"/"boss" node contexts only.
    The DEFAULT empty node context -- what every loader-built / battery player
    carries -- is outside the gate, so no offensive potion is ever drunk there."""
    st = make_state(hp=80, enemies=[_attacker(5, hp=C.POTION_FIRE_DAMAGE)])
    p = _player(st, hp=80, potion_list=["fire_potion"], node_kind="")
    assert p.node_kind == ""                       # the loader/battery default

    potions.try_use_potions(st)

    assert st.enemies[0].alive                     # kill not closed
    assert st.player.potions == ["fire_potion"]    # potion still held
    assert not any(e["event"] == "potion_used" for e in st.log)

    # CONTROL: the identical fight on an elite node does drink.
    elite = make_state(hp=80, enemies=[_attacker(5, hp=C.POTION_FIRE_DAMAGE)])
    _player(elite, hp=80, potion_list=["fire_potion"], node_kind="elite")
    potions.try_use_potions(elite)
    assert not elite.enemies[0].alive
    assert elite.player.potions == []
