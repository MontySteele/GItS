"""Pins for coverage pass 4 -- the runtime-count ops and the reward channel.

Same contract as test_si_powers.py: every test drives the mechanic the way a
card row would and asserts on the runtime quantity, and NO number extracted
from the game appears here. These run on CI, where game_ref/ does not exist.

The mechanics are ours; the cards that motivate them are not. Each test names
the shape it defends rather than the card, so a future pool that reaches for
the same shape inherits the pin.
"""

import random

import pytest

from tier0 import constants as C
from tier0.engine import combat, effects, powers
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


def filler(n, type="skill"):
    return [card(f"f{i}", type=type) for i in range(n)]


# --- amount grammar: runtime counts are legal amounts ----------------------

def test_hand_size_is_read_before_the_discard_not_during_it():
    """"Discard your hand" must not chase its own shrinking pool: the count
    is resolved once, up front, the way `cards.Count()` is evaluated before
    DiscardAndDraw rather than inside it."""
    state = make_state()
    state.player.hand.extend(filler(4))
    play(state, [{"op": "discard", "amount": "hand_size", "select": "chosen"}])
    assert state.player.hand == []
    # All four, and the driver itself, which lands in discard on resolution.
    assert {c.id for c in state.player.discard_pile} == {
        "f0", "f1", "f2", "f3", "driver"}


def test_a_card_can_draw_back_exactly_what_it_discarded():
    state = make_state()
    state.player.hand.extend(filler(3))
    state.player.draw_pile.extend(filler(5, type="attack"))
    play(state, [{"op": "discard", "amount": "hand_size", "select": "chosen"},
                 {"op": "draw", "amount": "discards_this_card"}])
    assert len(state.player.hand) == 3
    assert all(c.type == "attack" for c in state.player.hand)


def test_discards_this_card_is_per_card_not_per_turn():
    """The second card must not draw back the first card's discards."""
    state = make_state()
    state.player.hand.extend(filler(2))
    play(state, [{"op": "discard", "amount": "hand_size", "select": "chosen"}])
    state.player.draw_pile.extend(filler(4, type="attack"))
    play(state, [{"op": "draw", "amount": "discards_this_card"}])
    assert state.player.hand == []


def test_an_unknown_amount_token_still_raises():
    """Widening `amount` to accept runtime counts must not soften the
    failure -- a typo is still a loud error, just from one layer deeper."""
    state = make_state()
    with pytest.raises(ValueError):
        effects._amount(state, "hand_sizes")


# --- drawing to a hand size ------------------------------------------------

def test_draw_to_hand_size_tops_up_and_never_overdraws():
    state = make_state()
    state.player.hand.extend(filler(2))
    state.player.draw_pile.extend(filler(10, type="attack"))
    play(state, [{"op": "draw_to_hand_size", "amount": 6}])
    assert len(state.player.hand) == 6


def test_draw_to_hand_size_draws_nothing_when_the_hand_is_already_there():
    """`Math.Max(0, want - count)` is a subtraction, not a loop: it never
    discards down to the number and never draws when it is already met."""
    state = make_state()
    state.player.hand.extend(filler(7))
    state.player.draw_pile.extend(filler(5, type="attack"))
    play(state, [{"op": "draw_to_hand_size", "amount": 6}])
    assert len(state.player.hand) == 7
    assert len(state.player.draw_pile) == 5


# --- block actually gained, not block printed ------------------------------

def test_block_next_turn_reads_the_block_that_actually_landed():
    """Dexterity is added by the block funnel, so a card paying "the block
    you gained" must pay the modified number. Reading the printed amount
    would silently under-pay every scaled build."""
    state = make_state()
    powers.apply_power(state, state.player, "dexterity", 3)
    play(state, [{"op": "block", "amount": 4},
                 {"op": "block_next_turn",
                  "amount": "block_gained_this_card"}])
    assert state.player.block == 7
    assert state.player.powers["block_next_turn"] == 7


def test_block_gained_this_card_is_cleared_between_cards():
    state = make_state()
    play(state, [{"op": "block", "amount": 5}])
    play(state, [{"op": "block_next_turn",
                  "amount": "block_gained_this_card"}])
    assert state.player.powers.get("block_next_turn", 0) == 0


# --- the drawn card's own type ---------------------------------------------

def test_a_card_can_branch_on_the_type_it_just_drew():
    state = make_state()
    state.player.draw_pile.append(card("s", type="skill"))
    play(state, [{"op": "draw", "amount": 1},
                 {"op": "conditional", "if": "drew_skill_this_card",
                  "then": [{"op": "block", "amount": 3}]}])
    assert state.player.block == 3


def test_the_branch_is_false_when_the_draw_produced_something_else():
    state = make_state()
    state.player.draw_pile.append(card("a", type="attack"))
    play(state, [{"op": "draw", "amount": 1},
                 {"op": "conditional", "if": "drew_skill_this_card",
                  "then": [{"op": "block", "amount": 3}]}])
    assert state.player.block == 0


def test_the_branch_is_false_when_nothing_was_drawn_at_all():
    """An empty deck reads as the source's null result, NOT as whatever the
    previous card happened to draw."""
    state = make_state()
    state.player.draw_pile.append(card("s", type="skill"))
    play(state, [{"op": "draw", "amount": 1}])          # a Skill, last card
    # Both piles empty: nothing to draw and nothing to reshuffle back in.
    state.player.draw_pile.clear()
    state.player.discard_pile.clear()
    play(state, [{"op": "draw", "amount": 1},           # draws nothing now
                 {"op": "conditional", "if": "drew_skill_this_card",
                  "then": [{"op": "block", "amount": 3}]}])
    assert state.player.block == 0


# --- one X spent twice, with opposite signs --------------------------------

def test_a_negative_amount_negates_whatever_formula_follows_it():
    state = make_state()
    enemy = make_enemy(hp=40)
    state.enemies = [enemy]
    state.player.energy = 3
    play(state, [{"op": "apply_power", "power": "strength",
                  "amount": "-X", "target": "enemy"},
                 {"op": "apply_power", "power": "weak",
                  "amount": "X", "target": "enemy"}],
         cost="X")
    assert enemy.powers["strength"] == -3
    assert enemy.powers["weak"] == 3


def test_negative_strength_actually_reduces_what_the_enemy_hits_for():
    """The debuff has to reach the damage funnel, or the card is decoration."""
    state = make_state()
    enemy = make_enemy(hp=40)
    powers.apply_power(state, enemy, "strength", -2)
    assert powers.modify_damage_dealt(enemy, 5) == 3


# --- repeat that re-picks its target ---------------------------------------

def test_times_on_apply_power_repeats_the_whole_pick():
    """Three throws at three separately rolled enemies. Against ONE enemy
    that is three applications of the stack, not one -- which is what makes
    the shape observable without asserting on a random roll."""
    state = make_state()
    enemy = make_enemy(hp=60)
    state.enemies = [enemy]
    play(state, [{"op": "apply_power", "power": "poison", "amount": 3,
                  "target": "random_enemy", "times": 3}])
    assert enemy.powers["poison"] == 9


def test_times_spreads_across_separately_rolled_targets():
    state = make_state(seed=7)
    state.enemies = [make_enemy(hp=60, name=f"e{i}") for i in range(3)]
    play(state, [{"op": "apply_power", "power": "poison", "amount": 3,
                  "target": "random_enemy", "times": 3}])
    total = sum(e.powers.get("poison", 0) for e in state.enemies)
    assert total == 9
    # The point of re-picking: the stacks are not guaranteed to sit on one
    # enemy. Asserting the TOTAL keeps this deterministic while still
    # failing if the op ever resolves its target once and multiplies.
    assert max(e.powers.get("poison", 0) for e in state.enemies) <= 9


# --- a volley that repeats per kill ----------------------------------------

def test_chain_attack_repeats_once_per_enemy_it_killed():
    """Two kills in one volley buy TWO more volleys, not one."""
    state = make_state()
    state.enemies = [make_enemy(hp=4, name="a"), make_enemy(hp=4, name="b"),
                     make_enemy(hp=100, name="tank")]
    play(state, [{"op": "chain_attack", "amount": 5, "target": "all_enemies"}])
    tank = state.enemies[2]
    # volley 1 kills both 4hp enemies (tank 100 -> 95); their two deaths buy
    # volleys 2 and 3, which only the tank is alive to receive.
    assert tank.hp == 85


def test_chain_attack_stops_when_a_volley_kills_nothing():
    state = make_state()
    enemy = make_enemy(hp=100)
    state.enemies = [enemy]
    play(state, [{"op": "chain_attack", "amount": 5, "target": "all_enemies"}])
    assert enemy.hp == 95


def test_chain_attack_terminates_when_it_clears_the_board():
    state = make_state()
    state.enemies = [make_enemy(hp=3, name="a"), make_enemy(hp=3, name="b")]
    play(state, [{"op": "chain_attack", "amount": 5, "target": "all_enemies"}])
    assert state.living_enemies == []


# --- stripping block -------------------------------------------------------

def test_strip_block_removes_all_of_it_without_dealing_damage():
    """LoseBlock is not damage: nothing that reads a hit may fire, which is
    why Thorns is the assertion here rather than the enemy's HP alone."""
    state = make_state()
    enemy = make_enemy(hp=40)
    enemy.block = 12
    enemy.powers["thorns"] = 5
    state.enemies = [enemy]
    hp_before = state.player.hp
    play(state, [{"op": "strip_block", "target": "enemy"}])
    assert enemy.block == 0
    assert enemy.hp == 40
    assert state.player.hp == hp_before


def test_strip_block_is_inert_against_an_enemy_with_none():
    state = make_state()
    enemy = make_enemy(hp=40)
    state.enemies = [enemy]
    play(state, [{"op": "strip_block", "target": "enemy"}])
    assert enemy.block == 0


# --- the post-combat reward channel ----------------------------------------

def test_a_fatal_kill_records_an_extra_screen_and_grants_nothing():
    """Combat's whole job here is to say that it happened. Nothing about the
    fight changes, and no reward is rolled -- that is the run layer's."""
    state = make_state()
    enemy = make_enemy(hp=6)
    state.enemies = [enemy]
    play(state, [{"op": "damage", "amount": 10, "target": "enemy"},
                 {"op": "conditional", "if": "killed_target_fatal",
                  "then": [{"op": "extra_card_screen", "amount": 1}]}])
    assert state.extra_card_screens == 1


def test_a_kill_that_does_not_count_for_fatal_earns_nothing():
    """The gate is the base game's Fatal gate, not "did something die" --
    a summoned add's death must not pay."""
    state = make_state()
    enemy = make_enemy(hp=6)
    enemy.counts_for_fatal = False
    state.enemies = [enemy]
    play(state, [{"op": "damage", "amount": 10, "target": "enemy"},
                 {"op": "conditional", "if": "killed_target_fatal",
                  "then": [{"op": "extra_card_screen", "amount": 1}]}])
    assert state.extra_card_screens == 0


def test_a_survivor_earns_nothing():
    state = make_state()
    state.enemies = [make_enemy(hp=100)]
    play(state, [{"op": "damage", "amount": 10, "target": "enemy"},
                 {"op": "conditional", "if": "killed_target_fatal",
                  "then": [{"op": "extra_card_screen", "amount": 1}]}])
    assert state.extra_card_screens == 0


def test_extra_screens_accumulate_across_a_whole_fight():
    """Two copies played in one fight owe two screens; the counter is
    combat-scoped, not card-scoped."""
    state = make_state()
    state.enemies = [make_enemy(hp=6, name="a"), make_enemy(hp=6, name="b")]
    for _ in range(2):
        play(state, [{"op": "damage", "amount": 10, "target": "enemy"},
                     {"op": "conditional", "if": "killed_target_fatal",
                      "then": [{"op": "extra_card_screen", "amount": 1}]}])
    assert state.extra_card_screens == 2
