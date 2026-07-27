"""Pins for the base-game-parity primitives the SILENT anchor needs.

Same contract as test_ic_effects.py: every test drives a mechanic the way a
card row would and asserts on the runtime quantity, and NO number extracted
from the game appears here. These run on CI, where game_ref/ does not exist --
the mechanics are ours even though the pool that motivates them is not.

The three pinned here are the sprint's P0s, in the order the first Silent
extraction's exclusion histogram put them:

  chosen discard  -- Survivor is in the STARTING DECK, so real_silent cannot
                     be built at all without it
  poison          -- the only power gating more than two cards
  dexterity       -- the block funnel the whole defensive kit leans on
"""

from tier0 import constants as C
from tier0.engine import combat, effects, powers, refpowers
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state


def card(cid="c", type="skill", cost=0, fx=None, **kw):
    return Card(id=cid, name=cid, cost=cost, type=type,
                effects=fx if fx is not None else [], **kw)


# --- C-1: chosen discard --------------------------------------------------

def test_chosen_discard_takes_the_worst_card_not_a_random_one():
    """`select: chosen` routes through the same `_worst_card` pilot surface
    `exhaust_from` already uses, so a discard-cost card is priced against a
    player who discards their worst card -- which is what a player does."""
    state = make_state()
    keep = card("keep", type="attack", cost=1,
                fx=[{"op": "damage", "amount": 9, "target": "enemy"}])
    dead = card("dead", type="skill", cost=3, fx=[])
    state.player.hand = [keep, dead]
    effects.resolve_card(state, card("survivor_like", fx=[
        {"op": "block", "amount": 8},
        {"op": "discard", "amount": 1, "select": "chosen"}]))
    assert [c.id for c in state.player.hand] == ["keep"]
    assert [c.id for c in state.player.discard_pile] == ["dead"]


def test_random_stays_the_default_for_every_card_that_already_discarded():
    """The default flip would silently re-price every existing discard card,
    so the op keeps random unless a row asks for chosen."""
    state = make_state()
    state.rng.seed(0)
    state.player.hand = [card(f"c{i}") for i in range(6)]
    effects.resolve_card(state, card("d", fx=[{"op": "discard", "amount": 1}]))
    events = [e for e in state.log if e["event"] == "discard"]
    assert events and "chosen" not in events[-1]


def test_a_chosen_discard_still_triggers_kokomis_sly():
    """Two different mechanics wear the word Sly (this one is Kokomi's Assist
    lane; the base-game keyword is a different rule the extractor excludes).
    A chosen discard is still a CARD-EFFECT discard, which is the trigger
    scope, so the lane must not quietly stop firing for it."""
    state = make_state()
    assisted = card("assisted", cost=3,
                    sly=[{"op": "block", "amount": 4}])
    state.player.hand = [assisted]
    before = state.player.block
    effects.resolve_card(state, card("d", fx=[
        {"op": "discard", "amount": 1, "select": "chosen"}]))
    assert state.player.block == before + 4
    assert any(e["event"] == "sly" for e in state.log)


def test_chosen_discard_on_an_empty_hand_discards_nothing():
    state = make_state()
    state.player.hand = []
    effects.resolve_card(state, card("d", fx=[
        {"op": "discard", "amount": 2, "select": "chosen"}]))
    assert state.player.discard_pile == []


# --- C-2: poison ----------------------------------------------------------

def test_poison_deals_its_stack_then_decrements_by_one():
    """PowerCmd.Damage(Amount) then PowerCmd.Decrement -- ONE stack per tick,
    not a full expiry and not a halving."""
    state = make_state()
    enemy = state.enemies[0]
    hp = enemy.hp
    powers.apply_power(state, enemy, "poison", 4)
    refpowers.poison_tick(state, enemy)
    assert hp - enemy.hp == 4
    assert enemy.powers["poison"] == 3
    refpowers.poison_tick(state, enemy)
    assert hp - enemy.hp == 4 + 3
    assert enemy.powers["poison"] == 2


def test_poison_bypasses_block_entirely():
    """Unblockable | Unpowered. `unpowered_damage` would let Block absorb it;
    poison is BOTH flags and the block must be untouched as well as unused."""
    state = make_state()
    enemy = state.enemies[0]
    enemy.block = 50
    hp = enemy.hp
    powers.apply_power(state, enemy, "poison", 3)
    refpowers.poison_tick(state, enemy)
    assert hp - enemy.hp == 3
    assert enemy.block == 50


def test_poison_does_not_scale_with_strength_or_vulnerable():
    """Unpowered: neither the poisoner's Strength nor the victim's
    Vulnerable touches it. Routing poison through the powered attack
    pipeline is the mistake this pins shut."""
    state = make_state()
    enemy = state.enemies[0]
    powers.apply_power(state, state.player, "strength", 5)
    powers.apply_power(state, enemy, "vulnerable", 3)
    hp = enemy.hp
    powers.apply_power(state, enemy, "poison", 3)
    refpowers.poison_tick(state, enemy)
    assert hp - enemy.hp == 3


def test_poison_applications_stack_additively():
    state = make_state()
    enemy = state.enemies[0]
    powers.apply_power(state, enemy, "poison", 2)
    powers.apply_power(state, enemy, "poison", 3)
    assert enemy.powers["poison"] == 5


def test_poison_that_kills_does_not_decrement():
    """`if (base.Owner.IsAlive) await PowerCmd.Decrement(this)` -- the
    alive-gate is in the source, so it is in the model."""
    state = make_state()
    enemy = state.enemies[0]
    enemy.hp = 2
    powers.apply_power(state, enemy, "poison", 6)
    refpowers.poison_tick(state, enemy)
    assert not enemy.alive
    assert enemy.powers["poison"] == 6


def test_poison_ticks_once_per_turn_while_accelerant_is_unimplemented():
    """TriggerCount = min(Amount, 1 + Accelerant). Accelerant is not
    implemented and its card stays excluded, so the loop runs exactly once
    -- but the min() is transcribed, not assumed away."""
    state = make_state()
    enemy = state.enemies[0]
    hp = enemy.hp
    powers.apply_power(state, enemy, "poison", 9)
    refpowers.poison_tick(state, enemy)
    assert hp - enemy.hp == 9            # one tick, not nine


def test_poison_is_not_dot_and_neither_reschedules_the_other():
    """`dot` (Electro-Charged) ticks at site A, before the draw; poison ticks
    at site F, after it. Klee and Kokomi are balanced around `dot`'s clock,
    so the parity work is forbidden from moving it -- the two coexist."""
    state = make_state()
    enemy = state.enemies[0]
    hp = enemy.hp
    powers.apply_power(state, enemy, "dot", 3)
    powers.apply_power(state, enemy, "poison", 3)
    powers.on_turn_start(state, enemy)               # site A only
    assert hp - enemy.hp == 3
    assert enemy.powers["poison"] == 3               # untouched by site A
    refpowers.enemy_side_turn_start(state, enemy)    # site F
    assert hp - enemy.hp == 3 + 3
    assert enemy.powers["dot"] == 2 and enemy.powers["poison"] == 2


def test_poison_on_an_enemy_ticks_through_a_real_fight():
    """The wiring, not just the function: an enemy carrying poison loses HP
    at its own turn start when the fight actually runs it."""
    state = make_state(enemies=[make_enemy(hp=60)])
    enemy = state.enemies[0]
    powers.apply_power(state, enemy, "poison", 5)
    hp = enemy.hp
    combat._enemy_turn(state, enemy)
    assert hp - enemy.hp == 5
    assert enemy.powers["poison"] == 4


# --- C-3: dexterity -------------------------------------------------------

def test_dexterity_adds_to_card_block():
    state = make_state()
    powers.apply_power(state, state.player, "dexterity", 3)
    effects.resolve_card(state, card("b", fx=[{"op": "block", "amount": 5}]))
    assert state.player.block == 8


def test_dexterity_does_not_touch_unpowered_power_block():
    """`props.IsPoweredCardOrMonsterMoveBlock()` gates the additive hook, and
    that is the same line tier0 already draws: refpowers.gain_block carries
    the Unpowered power-block that Frail is (correctly) not allowed to
    reduce either."""
    state = make_state()
    p = state.player
    powers.apply_power(state, p, "dexterity", 3)
    refpowers.gain_block(state, p, 5)
    assert p.block == 5


def test_dexterity_is_additive_BEFORE_frail_is_multiplicative():
    """ModifyBlockAdditive runs before ModifyBlockMultiplicative, so it is
    (base + dex) * 0.75 and not base * 0.75 + dex. The two readings agree on
    small numbers and disagree on real ones, which is exactly how an
    interaction order gets shipped wrong."""
    state = make_state()
    p = state.player
    powers.apply_power(state, p, "dexterity", 3)
    powers.apply_power(state, p, "frail", 1)
    assert powers.modify_block_gained(p, 11) == int(14 * C.FRAIL_BLOCK_MULT)
    assert powers.modify_block_gained(p, 11) != (int(11 * C.FRAIL_BLOCK_MULT)
                                                 + 3)


def test_negative_dexterity_floors_at_zero_block():
    """DexterityPower.AllowNegative is true. A negative stack must not drive
    block below zero, and must not invert Frail's multiplier by going
    negative before it."""
    state = make_state()
    p = state.player
    powers.apply_power(state, p, "dexterity", -9)
    assert powers.modify_block_gained(p, 5) == 0
    powers.apply_power(state, p, "frail", 1)
    assert powers.modify_block_gained(p, 5) == 0


def test_a_block_op_with_no_block_gains_nothing_from_dexterity():
    """The funnel's `amount <= 0` early-out predates Dexterity; a card that
    gains no block must not start gaining Dexterity's worth of it."""
    state = make_state()
    powers.apply_power(state, state.player, "dexterity", 4)
    assert powers.modify_block_gained(state.player, 0) == 0
