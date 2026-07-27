"""Pins for coverage pass 5 -- the last of the Silent's parity powers.

Same contract as test_si_powers.py: every test drives the mechanic the way a
card row would and asserts on the runtime quantity, and NO number extracted
from the game appears here. These run on CI, where game_ref/ does not exist.

TWO OF THESE POWERS CANNOT BE APPLIED BY A STRUCTURALLY EXTRACTED ROW, and
that is deliberate rather than a gap: InfiniteBlades creates the owner's
token and PhantomBlades reads the owner's card TAG, both of which are game
data that may not appear in committed engine code. The row carries them as a
`payload` instead (extract_base_game_pool.PAYLOAD_POWERS), so a card that
applies one without saying what to work on is EXCLUDED rather than emitted
inert. The payload plumbing is pinned here; the exclusion is pinned by the
extractor's own reason string.
"""

import random

from tier0 import constants as C
from tier0.engine import combat, effects, powers, refpowers
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state


def card(cid="c", type="skill", cost=0, fx=None, **kw):
    return Card(id=cid, name=cid, cost=cost, type=type,
                effects=fx if fx is not None else [], **kw)


def play(state, fx, **kw):
    c = card("driver", fx=fx, **kw)
    state.player.hand.append(c)
    combat.play_card(state, c)
    return c


# --- Accuracy: a flat bonus that only tagged cards collect ------------------

def test_tag_damage_pays_only_the_tagged_card():
    state = make_state()
    enemy = make_enemy(hp=60)
    state.enemies = [enemy]
    powers.apply_power(state, state.player, "tag_damage_shiv", 4)
    play(state, [{"op": "damage", "amount": 5, "target": "enemy"}],
         type="attack", tags=["shiv"])
    assert enemy.hp == 51
    play(state, [{"op": "damage", "amount": 5, "target": "enemy"}],
         type="attack")
    assert enemy.hp == 46


# --- Tracking: the stacks ARE the multiplier, and only vs Weak --------------

def test_tracking_multiplies_only_against_a_weak_target():
    state = make_state()
    enemy = make_enemy(hp=200)
    powers.apply_power(state, state.player, "tracking", 2)
    assert powers.modify_damage_taken(enemy, 10.0, state.player) == 10
    powers.apply_power(state, enemy, "weak", 1)
    assert powers.modify_damage_taken(enemy, 10.0, state.player) > 10


def test_tracking_stacks_raise_the_multiplier_itself():
    """base.Amount IS the multiplier: a second application makes it 3x, not
    2x twice. Reading it as a percentage or a flat double would be a large
    silent difference on the card's second copy."""
    state = make_state()
    enemy = make_enemy(hp=500)
    powers.apply_power(state, enemy, "weak", 1)
    powers.apply_power(state, state.player, "tracking", 2)
    two = powers.modify_damage_taken(enemy, 10.0, state.player)
    powers.apply_power(state, state.player, "tracking", 1)
    three = powers.modify_damage_taken(enemy, 10.0, state.player)
    assert three == two * 3 / 2


def test_a_card_can_read_its_own_power_before_applying_it():
    """Tracking's own OnPlay: 1 more if the owner already has it, 2 if not,
    so the second copy is worth half the first."""
    row = [{"op": "conditional", "if": "self_has_power_tracking",
            "then": [{"op": "apply_power", "power": "tracking",
                      "amount": 1, "target": "self"}],
            "else": [{"op": "apply_power", "power": "tracking",
                      "amount": 2, "target": "self"}]}]
    state = make_state()
    play(state, row)
    assert state.player.powers["tracking"] == 2
    play(state, row)
    assert state.player.powers["tracking"] == 3


# --- Wraith Form: the cost that never stops ---------------------------------

def test_wraith_form_takes_dexterity_every_turn_forever():
    state = make_state()
    powers.apply_power(state, state.player, "wraith_form", 1)
    refpowers.player_turn_start_late(state)
    assert state.player.powers["dexterity"] == -1
    refpowers.player_turn_start_late(state)
    assert state.player.powers["dexterity"] == -2


def test_the_wraith_form_hole_actually_reaches_the_block_funnel():
    """A Dexterity debuff nobody reads is decoration. Dexterity lives in
    powers.modify_block_gained, so that is where this has to bite."""
    state = make_state()
    powers.apply_power(state, state.player, "wraith_form", 2)
    refpowers.player_turn_start_late(state)
    assert powers.modify_block_gained(state.player, 5) == 3


# --- Shadow Step -> DoubleDamage --------------------------------------------

def test_shadow_step_converts_itself_at_the_next_turn_start():
    state = make_state()
    powers.apply_power(state, state.player, "shadow_step", 1)
    refpowers.player_turn_start_late(state)
    assert "shadow_step" not in state.player.powers
    assert state.player.powers["double_damage"] == 1


def test_double_damage_is_a_flat_double_not_a_per_stack_multiplier():
    """DoubleDamagePower returns a literal 2; its stacks are a TURN counter.
    Reading them as a multiplier would quadruple a two-stack player."""
    state = make_state()
    enemy = make_enemy(hp=500)
    powers.apply_power(state, state.player, "double_damage", 2)
    assert powers.modify_damage_taken(enemy, 10.0, state.player,
                                      from_card=True) == 20


def test_double_damage_ignores_damage_with_no_card_source():
    """`cardSource == null` -> no doubling: a bomb or a poison tick is not a
    card's Attack."""
    state = make_state()
    enemy = make_enemy(hp=500)
    powers.apply_power(state, state.player, "double_damage", 1)
    assert powers.modify_damage_taken(enemy, 10.0, state.player,
                                      from_card=False) == 10


def test_double_damage_decrements_at_the_owners_turn_end():
    state = make_state()
    powers.apply_power(state, state.player, "double_damage", 2)
    refpowers.on_fighter_turn_end(state, state.player)
    assert state.player.powers["double_damage"] == 1
    refpowers.on_fighter_turn_end(state, state.player)
    assert state.player.powers["double_damage"] == 0


# --- Infinite Blades: a power that makes the OWNER's card -------------------

def test_the_payload_is_what_the_power_creates():
    """The card id lives on the row, never in the engine. Without a payload
    the power refuses LOUDLY rather than making nothing quietly."""
    state = make_state()
    play(state, [{"op": "apply_power", "power": "infinite_blades",
                  "amount": 2, "target": "self", "payload": "strike"}])
    assert state.player.power_payloads["infinite_blades"] == "strike"
    refpowers.before_hand_draw(state)
    assert [c.id for c in state.player.hand] == ["strike", "strike"]


def test_a_payload_power_with_no_payload_says_so():
    state = make_state()
    powers.apply_power(state, state.player, "infinite_blades", 1)
    refpowers.before_hand_draw(state)
    assert state.player.hand == []
    assert any(e.get("event") == "UNIMPLEMENTED" for e in state.log)


def test_the_created_cards_land_before_the_hand_draw():
    """BeforeHandDraw, not after: the tokens are in hand before the draw
    counts against the hand cap, which is what makes a full hand lose the
    DRAW rather than the token."""
    state = make_state()
    state.player.power_payloads["infinite_blades"] = "strike"
    powers.apply_power(state, state.player, "infinite_blades", 1)
    state.player.draw_pile.extend(card(f"d{i}") for i in range(20))
    combat._player_turn(state, lambda s: None)
    assert any(c.id == "strike" for c in state.player.hand + state.player.discard_pile)


# --- Phantom Blades: retain by tag, and only the first play pays ------------

def test_phantom_blades_retains_every_tagged_card_at_the_flush():
    state = make_state()
    state.player.power_payloads["phantom_blades"] = "shiv"
    powers.apply_power(state, state.player, "phantom_blades", 9)
    flushing = [card("t1", tags=["shiv"]), card("plain"),
                card("t2", tags=["shiv"])]
    kept = refpowers.retain_at_flush(state, flushing)
    assert {c.id for c in kept} == {"t1", "t2"}


def test_phantom_blades_does_not_spend_well_laid_plans_allowance():
    """Two powers, two allowances. Counting the retained tokens against Well
    Laid Plans would silently shrink a power nobody touched."""
    state = make_state()
    state.player.power_payloads["phantom_blades"] = "shiv"
    powers.apply_power(state, state.player, "phantom_blades", 9)
    powers.apply_power(state, state.player, "well_laid_plans", 1)
    flushing = [card("t1", tags=["shiv"]), card("plain", type="attack")]
    kept = refpowers.retain_at_flush(state, flushing)
    assert {c.id for c in kept} == {"t1", "plain"}


def test_only_the_first_tagged_card_each_turn_takes_the_bonus():
    state = make_state()
    enemy = make_enemy(hp=200)
    state.enemies = [enemy]
    state.player.power_payloads["phantom_blades"] = "shiv"
    powers.apply_power(state, state.player, "phantom_blades", 9)
    play(state, [{"op": "damage", "amount": 4, "target": "enemy"}],
         type="attack", tags=["shiv"])
    assert enemy.hp == 187                      # 4 + 9
    play(state, [{"op": "damage", "amount": 4, "target": "enemy"}],
         type="attack", tags=["shiv"])
    assert enemy.hp == 183                      # 4, the bonus is spent


def test_the_bonus_comes_back_next_turn():
    state = make_state()
    enemy = make_enemy(hp=200)
    state.enemies = [enemy]
    state.player.power_payloads["phantom_blades"] = "shiv"
    powers.apply_power(state, state.player, "phantom_blades", 9)
    play(state, [{"op": "damage", "amount": 4, "target": "enemy"}],
         type="attack", tags=["shiv"])
    refpowers.reset_turn_counters(state)
    play(state, [{"op": "damage", "amount": 4, "target": "enemy"}],
         type="attack", tags=["shiv"])
    assert enemy.hp == 200 - 13 - 13


def test_an_untagged_card_neither_takes_the_bonus_nor_spends_it():
    state = make_state()
    enemy = make_enemy(hp=200)
    state.enemies = [enemy]
    state.player.power_payloads["phantom_blades"] = "shiv"
    powers.apply_power(state, state.player, "phantom_blades", 9)
    play(state, [{"op": "damage", "amount": 4, "target": "enemy"}],
         type="attack")
    assert enemy.hp == 196
    play(state, [{"op": "damage", "amount": 4, "target": "enemy"}],
         type="attack", tags=["shiv"])
    assert enemy.hp == 183


# --- the dial itself --------------------------------------------------------

def test_the_payload_powers_are_refused_by_the_extractor_not_emitted():
    """A card applying one of these WITHOUT a payload must never reach a
    pool: it would read as a buff and do nothing, which is exactly the
    failure the CO-OP ONLY category was created to prevent."""
    import importlib.util
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location(
        "_x", root / "tools" / "extract_base_game_pool.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert set(mod.PAYLOAD_POWERS) == {"InfiniteBladesPower",
                                       "PhantomBladesPower"}
    for power, reason in mod.PAYLOAD_POWERS.items():
        assert "payload" in reason.lower()
        assert power not in mod.SUPPORTED_POWERS
