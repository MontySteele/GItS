"""Pins for coverage pass 6 -- per-instance card cost state and the gates.

Same contract as test_si_pass4/5: every test drives the mechanic the way a
card row would, asserts on the runtime quantity, and contains NO number
extracted from the game. These run on CI, where game_ref/ does not exist.

The theme is state that lives on the CARD OBJECT rather than on the player.
Two copies of a self-discounting card discount themselves separately, and a
card that leaves hand and comes back keeps what it earned -- neither of which
a player-level counter can express.
"""

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


# --- Bullet Time: the whole hand, free, this turn ---------------------------

def test_freeing_the_hand_costs_nothing_to_play_from():
    state = make_state()
    held = [card("a", cost=2), card("b", cost=3)]
    state.player.hand.extend(held)
    play(state, [{"op": "cost_mod", "scope": "hand_free_this_turn"}])
    assert all(combat.card_cost(state, c) == 0 for c in held)


def test_an_x_cost_card_is_exempt_from_the_free_hand():
    """`if (!card.EnergyCost.CostsX)`. Not cosmetic: an X card resolves at
    the energy it spent, so freeing one makes it resolve at X = 0 and do
    nothing -- the card would be destroyed by its own buff."""
    state = make_state()
    state.player.energy = 3
    x_card = card("x", cost="X")
    state.player.hand.append(x_card)
    play(state, [{"op": "cost_mod", "scope": "hand_free_this_turn"}])
    assert x_card.free_this_turn is False
    assert combat.card_cost(state, x_card) == 3


def test_the_free_hand_expires_at_the_turn_boundary():
    state = make_state()
    held = card("a", cost=2)
    state.player.hand.append(held)
    play(state, [{"op": "cost_mod", "scope": "hand_free_this_turn"}])
    refpowers.reset_turn_counters(state)
    assert combat.card_cost(state, held) == 2


def test_a_freed_card_that_was_discarded_does_not_come_back_free():
    """The sweep covers every pile for exactly this reason."""
    state = make_state()
    held = card("a", cost=2)
    state.player.hand.append(held)
    play(state, [{"op": "cost_mod", "scope": "hand_free_this_turn"}])
    state.player.hand.remove(held)
    state.player.discard_pile.append(held)
    refpowers.reset_turn_counters(state)
    assert held.free_this_turn is False


# --- Up My Sleeve: each copy discounts ITSELF, for the combat ---------------

def test_a_card_can_discount_itself_for_the_rest_of_the_combat():
    state = make_state()
    c = card("driver", cost=2,
             fx=[{"op": "cost_mod", "scope": "self_this_combat",
                  "delta": -1}])
    state.player.hand.append(c)
    combat.play_card(state, c)
    assert combat.card_cost(state, c) == 1
    state.player.hand.append(c)
    combat.play_card(state, c)
    assert combat.card_cost(state, c) == 0


def test_the_self_discount_survives_the_turn_boundary():
    """AddThisCombat, not AddThisTurn -- the turn sweep must not touch it."""
    state = make_state()
    c = card("driver", cost=2,
             fx=[{"op": "cost_mod", "scope": "self_this_combat",
                  "delta": -1}])
    state.player.hand.append(c)
    combat.play_card(state, c)
    refpowers.reset_turn_counters(state)
    assert combat.card_cost(state, c) == 1


def test_one_copys_discount_does_not_reach_the_other():
    """Per-INSTANCE. A player-level counter would make the second copy
    arrive already discounted, which is a different and better card."""
    state = make_state()
    first = card("driver", cost=2,
                 fx=[{"op": "cost_mod", "scope": "self_this_combat",
                      "delta": -1}])
    second = card("driver", cost=2,
                  fx=[{"op": "cost_mod", "scope": "self_this_combat",
                       "delta": -1}])
    state.player.hand.append(first)
    combat.play_card(state, first)
    assert combat.card_cost(state, second) == 2


def test_the_discount_never_drives_a_cost_below_zero():
    state = make_state()
    c = card("driver", cost=1,
             fx=[{"op": "cost_mod", "scope": "self_this_combat",
                  "delta": -1}])
    for _ in range(3):
        state.player.hand.append(c)
        combat.play_card(state, c)
    assert combat.card_cost(state, c) == 0


# --- Pinpoint: cheaper per Skill played this turn ---------------------------

def test_a_card_can_cost_less_per_skill_played_this_turn():
    state = make_state()
    target = card("pin", cost=3, type="attack",
                  cost_reduction_per_skill_this_turn=1)
    assert combat.card_cost(state, target) == 3
    play(state, [], type="skill")
    assert combat.card_cost(state, target) == 2
    play(state, [], type="skill")
    assert combat.card_cost(state, target) == 1


def test_attacks_do_not_discount_the_skill_reader():
    state = make_state()
    target = card("pin", cost=3, type="attack",
                  cost_reduction_per_skill_this_turn=1)
    play(state, [], type="attack")
    assert combat.card_cost(state, target) == 3


def test_the_skill_discount_resets_each_turn():
    state = make_state()
    target = card("pin", cost=3, type="attack",
                  cost_reduction_per_skill_this_turn=1)
    play(state, [], type="skill")
    refpowers.reset_turn_counters(state)
    assert combat.card_cost(state, target) == 3


# --- Grand Finale: a real playability gate ----------------------------------

def test_a_gated_card_is_unplayable_until_its_condition_holds():
    state = make_state()
    state.player.energy = 3
    gated = card("finale", cost=0, type="attack", requires="draw_pile_empty")
    state.player.draw_pile.append(card("x"))
    assert not combat.card_playable(state, gated)
    state.player.draw_pile.clear()
    assert combat.card_playable(state, gated)


def test_the_pilot_never_plays_a_card_its_gate_refuses():
    """policy filters on card_playable, so the gate is inherited rather than
    reimplemented -- this pins that the wiring actually holds."""
    from tier0.content import loader
    from tier0.pilot import policy
    pilot = policy.make_pilot(loader.pilot_weights("generic"))
    state = make_state()
    state.player.energy = 3
    state.player.hand.append(
        card("finale", cost=0, type="attack", requires="draw_pile_empty"))
    state.player.draw_pile.append(card("x"))
    assert pilot(state) is None


# --- Hand Trick: single-turn Sly --------------------------------------------

def test_granted_sly_auto_plays_the_card_when_it_is_discarded():
    state = make_state()
    enemy = make_enemy(hp=40)
    state.enemies = [enemy]
    victim = card("gift", type="skill",
                  fx=[{"op": "damage", "amount": 6, "target": "enemy"}])
    state.player.hand.append(victim)
    play(state, [{"op": "grant_sly_this_turn", "card_type": "skill"}])
    assert victim.sly_this_turn
    play(state, [{"op": "discard", "amount": 1, "select": "chosen"}])
    assert enemy.hp == 34


def test_the_grant_skips_a_card_that_already_has_it():
    """`!card.IsSlyThisTurn` -- a second copy must pick a different card
    rather than waste itself on the same one."""
    state = make_state()
    a, b = card("a", type="skill"), card("b", type="skill")
    state.player.hand.extend([a, b])
    play(state, [{"op": "grant_sly_this_turn", "card_type": "skill"}])
    play(state, [{"op": "grant_sly_this_turn", "card_type": "skill"}])
    assert a.sly_this_turn and b.sly_this_turn


def test_the_grant_only_looks_at_the_named_type():
    state = make_state()
    attack = card("a", type="attack")
    state.player.hand.append(attack)
    play(state, [{"op": "grant_sly_this_turn", "card_type": "skill"}])
    assert not attack.sly_this_turn


def test_granted_sly_expires_with_the_turn():
    state = make_state()
    victim = card("gift", type="skill")
    state.player.hand.append(victim)
    play(state, [{"op": "grant_sly_this_turn", "card_type": "skill"}])
    refpowers.reset_turn_counters(state)
    assert not victim.sly_this_turn


# --- created tokens that arrive upgraded ------------------------------------

def test_add_card_can_create_the_upgraded_form():
    state = make_state()
    play(state, [{"op": "add_card", "card": "strike", "amount": 1,
                  "zone": "hand", "upgraded": True}])
    assert [c.id for c in state.player.hand] == ["strike+"]


def test_a_missing_upgrade_entry_is_logged_not_faked():
    state = make_state()
    play(state, [{"op": "add_card", "card": "curse_clumsy", "amount": 1,
                  "zone": "hand", "upgraded": True}])
    assert any(e.get("event") == "UNIMPLEMENTED" for e in state.log)
    assert [c.id for c in state.player.hand] == ["curse_clumsy"]


# --- Knife Trap: replay the exhaust pile ------------------------------------

def test_autoplay_from_exhaust_plays_every_tagged_card():
    state = make_state()
    enemy = make_enemy(hp=60)
    state.enemies = [enemy]
    for i in range(2):
        state.player.exhaust_pile.append(
            card(f"t{i}", type="attack", tags=["shiv"],
                 fx=[{"op": "damage", "amount": 4, "target": "enemy"}]))
    state.player.exhaust_pile.append(card("other", type="attack"))
    play(state, [{"op": "autoplay_from_exhaust", "tag": "shiv"}])
    assert enemy.hp == 52


def test_it_does_not_replay_what_it_exhausted_while_resolving():
    """The tokens it plays exhaust themselves straight back into the pile it
    is iterating; the source snapshots the list first, and so must this."""
    state = make_state()
    enemy = make_enemy(hp=200)
    state.enemies = [enemy]
    state.player.exhaust_pile.append(
        card("t", type="attack", tags=["shiv"], exhaust=True,
             fx=[{"op": "damage", "amount": 4, "target": "enemy"}]))
    play(state, [{"op": "autoplay_from_exhaust", "tag": "shiv"}])
    assert enemy.hp == 196


def test_an_empty_exhaust_pile_is_a_no_op():
    state = make_state()
    play(state, [{"op": "autoplay_from_exhaust", "tag": "shiv"}])
    assert state.player.exhaust_pile == []


# --- Nightmare: remember now, copy next turn --------------------------------

def test_the_remembered_card_arrives_next_turn():
    state = make_state()
    state.player.hand.append(card("strike", type="attack"))
    play(state, [{"op": "remember_card", "power": "nightmare"},
                 {"op": "apply_power", "power": "nightmare", "amount": 3,
                  "target": "self"}])
    assert state.player.powers["nightmare"] == 3
    state.player.hand.clear()
    refpowers.before_hand_draw(state)
    assert [c.id for c in state.player.hand] == ["strike"] * 3


def test_it_pays_out_once_and_removes_itself():
    state = make_state()
    state.player.hand.append(card("strike", type="attack"))
    play(state, [{"op": "remember_card", "power": "nightmare"},
                 {"op": "apply_power", "power": "nightmare", "amount": 1,
                  "target": "self"}])
    state.player.hand.clear()
    refpowers.before_hand_draw(state)
    refpowers.before_hand_draw(state)
    assert len(state.player.hand) == 1
    assert "nightmare" not in state.player.powers


def test_remembering_nothing_is_reported_not_faked():
    state = make_state()
    play(state, [{"op": "remember_card", "power": "nightmare"},
                 {"op": "apply_power", "power": "nightmare", "amount": 3,
                  "target": "self"}])
    refpowers.before_hand_draw(state)
    assert any(e.get("event") == "UNIMPLEMENTED" for e in state.log)


# --- Fan Of Knives: a power that retargets another card ---------------------

def test_a_power_can_widen_a_rows_target():
    state = make_state()
    state.enemies = [make_enemy(hp=40, name="a"), make_enemy(hp=40, name="b")]
    row = [{"op": "damage", "amount": 4, "target": "enemy",
            "target_all_if_power": "fan_of_knives"}]
    play(state, row, type="attack")
    assert sorted(e.hp for e in state.enemies) == [36, 40]
    powers.apply_power(state, state.player, "fan_of_knives", 1)
    play(state, row, type="attack")
    assert sorted(e.hp for e in state.enemies) == [32, 36]


def test_the_row_is_single_target_without_the_power():
    """Which is what made the single-target translation EXACT for as long as
    the power could not exist -- the condition its refusal was written under."""
    state = make_state()
    state.enemies = [make_enemy(hp=40, name="a"), make_enemy(hp=40, name="b")]
    play(state, [{"op": "damage", "amount": 4, "target": "enemy",
                  "target_all_if_power": "fan_of_knives"}], type="attack")
    assert sorted(e.hp for e in state.enemies) == [36, 40]


def test_an_unrelated_power_does_not_widen_it():
    state = make_state()
    state.enemies = [make_enemy(hp=40, name="a"), make_enemy(hp=40, name="b")]
    powers.apply_power(state, state.player, "strength", 5)
    play(state, [{"op": "damage", "amount": 4, "target": "enemy",
                  "target_all_if_power": "fan_of_knives"}], type="attack")
    assert sorted(e.hp for e in state.enemies) == [31, 40]
