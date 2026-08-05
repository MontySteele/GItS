"""Pins for tier0/engine/effects.py riders and ceilings that the suite left
unmeasured (mutation sweep s15, engine-effects group).

Three rules live here: a detonation's per-detonation `bonus` really is added
to every bomb that goes off, Kokomi's prevention ward can never prevent more
damage than the hit actually carries, and a CREATED card cannot push the hand
past MAX_HAND_SIZE. Each test drives the mechanic the way a card row would and
asserts the runtime quantity.
"""

from tier0 import constants as C
from tier0.engine import combat, effects
from tier0.engine.state import Bomb, Card
from tier0.tests.conftest import make_enemy, make_state


def _card(cid="c", type="skill", cost=0, fx=None):
    return Card(id=cid, name=cid, cost=cost, type=type,
                effects=fx if fx is not None else [])


def _play(state, fx):
    driver = _card("driver", fx=fx)
    state.player.hand.append(driver)
    combat.play_card(state, driver)
    return driver


# --- detonation bonus (HIGH-3) ---

def test_detonation_bonus_is_added_to_every_bomb_that_goes_off():
    """A detonation's bonus rider raises the damage of EACH bomb it cashes:
    two 4-damage bombs detonated with a bonus of 3 hit for 7 apiece, not 4."""
    enemy = make_enemy(hp=100)
    enemy.bombs = [Bomb(damage=4, element=None), Bomb(damage=4, element=None)]
    state = make_state(enemies=[enemy])

    effects.detonate_bombs(state, enemy, bonus=3)

    detonations = [ev["damage"] for ev in state.log
                   if ev["event"] == "bomb_detonation"]
    assert detonations == [7, 7]
    assert enemy.hp == 100 - 14


def test_detonation_without_a_bonus_pays_only_the_bomb_damage():
    """The bonus is a rider, not a baseline: an unbonused detonation of a
    4-damage bomb deals exactly 4."""
    enemy = make_enemy(hp=100)
    enemy.bombs = [Bomb(damage=4, element=None)]
    state = make_state(enemies=[enemy])

    effects.detonate_bombs(state, enemy)

    assert [ev["damage"] for ev in state.log
            if ev["event"] == "bomb_detonation"] == [4]
    assert enemy.hp == 100 - 4


# --- prevention ward clamp (HIGH-4) ---

def _ward_state(stacks=6, hp=80):
    state = make_state(hp=hp)
    state.player.powers["prevent_exhaust_ward"] = stacks
    state.player.draw_pile = [_card("fuel_0"), _card("fuel_1")]
    return state


def test_prevention_ward_never_prevents_more_than_the_incoming_damage():
    """Prevention is capped by the hit: a 6-stack ward asked to absorb a
    2-damage hit prevents 2, not its full 6."""
    state = _ward_state(stacks=6)

    prevented = effects.prevent_damage_exhaust(state, 2)

    assert prevented == 2
    assert [ev["amount"] for ev in state.log
            if ev["event"] == "prevent_exhaust"] == [2]


def test_prevention_ward_pays_full_stacks_only_against_a_bigger_hit():
    """The other side of the same clamp: when the hit exceeds the ward, the
    ward prevents all of its stacks and the remainder gets through."""
    state = _ward_state(stacks=6)

    assert effects.prevent_damage_exhaust(state, 9) == 6


def test_a_small_hit_through_the_ward_pays_out_nothing_extra():
    """A hit smaller than the ward is fully absorbed and nothing more: the
    player neither rises above their HP nor banks Encore out of the surplus
    prevention, because prevention stops at the size of the hit."""
    enemy = make_enemy(hp=50, intents=[{"kind": "attack", "amount": 2}])
    state = _ward_state(stacks=6)
    state.enemies = [enemy]

    combat._enemy_turn(state, enemy)

    assert state.player.hp == state.player.max_hp
    assert state.player.encore == 0
    assert [ev["amount"] for ev in state.log
            if ev["event"] == "player_hit"] == [0]
    assert not [ev for ev in state.log if ev["event"] == "encore_absorb"]


# --- created cards respect the hand ceiling (MEDIUM-1) ---

def test_a_created_card_goes_to_discard_when_the_hand_is_already_full():
    """A card created into the hand cannot push it past MAX_HAND_SIZE: with
    the hand at the ceiling the token is diverted to the discard pile."""
    state = make_state()
    state.player.hand = [_card(f"filler_{i}") for i in range(C.MAX_HAND_SIZE)]

    _play(state, [{"op": "add_card", "card": "strike", "amount": 1,
                   "zone": "hand"}])

    assert len(state.player.hand) == C.MAX_HAND_SIZE
    assert "strike" not in [c.id for c in state.player.hand]
    # the spent driver discards itself after resolving; the token is there too
    assert [c.id for c in state.player.discard_pile] == ["strike", "driver"]


def test_a_created_card_lands_in_hand_with_one_slot_left():
    """The ceiling is a ceiling, not a fence one card short: with the hand one
    card below MAX_HAND_SIZE the created token still goes to the hand."""
    state = make_state()
    state.player.hand = [_card(f"filler_{i}")
                         for i in range(C.MAX_HAND_SIZE - 1)]

    _play(state, [{"op": "add_card", "card": "strike", "amount": 1,
                   "zone": "hand"}])

    assert len(state.player.hand) == C.MAX_HAND_SIZE
    assert state.player.hand[-1].id == "strike"
    # only the spent driver discards; the token was not diverted
    assert [c.id for c in state.player.discard_pile] == ["driver"]
