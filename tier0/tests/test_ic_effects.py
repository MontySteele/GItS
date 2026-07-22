"""Pins for the base-game-parity PRIMITIVES added to effects.py.

These are the DSL ops the not-yet-emitted Ironclad cards need (Anger,
AshenStrike, BodySlam, Bully, Dismantle, Dominate, MoltenFist, ExpectAFight,
PactsEnd, Pillage). Every test drives an op the way a card row would and
asserts on the RUNTIME quantity the real game reads at resolution time -- the
property that a fixed number can never capture. No number extracted from the
game appears here; stacks and amounts are chosen for readability.
"""

from tier0 import constants as C
from tier0.engine import combat, effects, powers
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state


def card(cid="c", type="attack", cost=0, fx=None, **kw):
    return Card(id=cid, name=cid, cost=cost, type=type,
                effects=fx if fx is not None else [], **kw)


# --- Anger: clone THIS instance, not a fresh base copy ---------------------

def test_anger_clones_the_playing_instance_into_discard():
    state = make_state()
    anger = card("anger", cost=0, fx=[
        {"op": "damage", "amount": 6, "target": "enemy"},
        {"op": "add_card", "card": "self", "to": "discard"}])
    effects.resolve_card(state, anger)
    disc = state.player.discard_pile
    assert len(disc) == 1
    assert disc[0].id == "anger"
    assert disc[0] is not anger                 # a distinct object (a clone)


def test_anger_clone_inherits_upgrade_state_not_a_downgrade():
    # The clone is a deepcopy of the played card, so an "upgraded" Anger (its
    # damage op already at 8) clones an 8, where a fixed card_id re-add would
    # reload the base id and hand back a 6.
    state = make_state()
    anger_plus = card("anger", cost=0, fx=[
        {"op": "damage", "amount": 8, "target": "enemy"},
        {"op": "add_card", "card": "self", "to": "discard"}])
    effects.resolve_card(state, anger_plus)
    clone = state.player.discard_pile[0]
    assert clone.effects[0]["amount"] == 8


def test_summoned_enemies_are_ineligible_for_fatal_kills():
    summoner = make_enemy(hp=50, intents=[{
        "kind": "summon",
        "wave": [{"hp": 3, "name": "add",
                  "intents": [{"kind": "attack", "amount": 1}]}],
    }])
    state = make_state(enemies=[summoner])

    combat._enemy_turn(state, summoner)
    add = state.enemies[-1]
    assert not add.counts_for_fatal

    effects.resolve_card(state, card(
        "kill_add", fx=[{"op": "damage", "amount": 3,
                         "target": "enemy"}]))
    assert state.kills_this_card == 1
    assert state.fatal_kills_this_card == 0


# --- AshenStrike / BodySlam: base + per * runtime count --------------------

def test_ashen_strike_scales_with_the_exhaust_pile():
    state = make_state()
    state.player.exhaust_pile = [card("x"), card("y")]      # count 2
    fx = [{"op": "damage", "target": "enemy",
           "amount_formula": {"base": 6, "per": 3, "count": "exhaust_pile"}}]
    effects.resolve_card(state, card("ashen", fx=fx))
    assert state.enemies[0].hp == state.enemies[0].max_hp - (6 + 3 * 2)


def test_body_slam_reads_current_block():
    state = make_state()
    state.player.block = 9
    fx = [{"op": "damage", "target": "enemy",
           "amount_formula": {"base": 0, "per": 1, "count": "player_block"}}]
    effects.resolve_card(state, card("slam", fx=fx))
    assert state.enemies[0].hp == state.enemies[0].max_hp - 9


# --- Bully: per-target rider off the DEFENDER's power ------------------------

def test_bully_adds_per_target_vulnerable_stack():
    state = make_state()
    e = state.enemies[0]
    e.powers["vulnerable"] = 2
    fx = [{"op": "damage", "amount": 4, "target": "enemy",
           "bonus_per_target_power": {"power": "vulnerable", "per": 2}}]
    effects.resolve_card(state, card("bully", fx=fx))
    expected = int((4 + 2 * 2) * C.VULNERABLE_TAKEN_MULT)   # rider, then amp
    assert e.hp == e.max_hp - expected


# --- Dismantle: predicate picks the hit count -------------------------------

def _damage_events(state):
    return [ev for ev in state.log if ev["event"] == "damage"]


def test_dismantle_hits_twice_only_when_the_target_is_vulnerable():
    fx = [{"op": "conditional", "if": "target_has_power_vulnerable",
           "then": [{"op": "damage", "amount": 8, "times": 2,
                     "target": "enemy"}],
           "else": [{"op": "damage", "amount": 8, "target": "enemy"}]}]

    no_vuln = make_state()
    effects.resolve_card(no_vuln, card("dis", fx=fx))
    assert len(_damage_events(no_vuln)) == 1

    vuln = make_state()
    vuln.enemies[0].powers["vulnerable"] = 1
    effects.resolve_card(vuln, card("dis", fx=fx))
    assert len(_damage_events(vuln)) == 2


# --- Dominate / MoltenFist: apply_power Amount off a live stack --------------

def test_dominate_gains_strength_equal_to_the_targets_vulnerable_after_applying():
    state = make_state()
    e = state.enemies[0]
    e.powers["vulnerable"] = 2
    fx = [{"op": "apply_power", "power": "vulnerable", "amount": 1,
           "target": "enemy"},
          {"op": "apply_power", "power": "strength", "target": "self",
           "amount_formula": {"target_power": "vulnerable"}}]
    effects.resolve_card(state, card("dom", type="skill", fx=fx))
    assert e.powers["vulnerable"] == 3                      # 2 + the applied 1
    assert state.player.powers["strength"] == 3            # read AFTER the +1


def test_molten_fist_doubles_vulnerable_but_is_inert_without_it():
    fx = [{"op": "damage", "amount": 10, "target": "enemy"},
          {"op": "apply_power", "power": "vulnerable", "target": "enemy",
           "amount_formula": {"target_power": "vulnerable"}, "guard": "nonzero"}]

    hit = make_state(enemies=[make_enemy(hp=80)])
    hit.enemies[0].powers["vulnerable"] = 2
    effects.resolve_card(hit, card("molten", fx=fx))
    assert hit.enemies[0].powers["vulnerable"] == 4        # doubled

    miss = make_state(enemies=[make_enemy(hp=80)])
    effects.resolve_card(miss, card("molten", fx=fx))
    assert miss.enemies[0].powers.get("vulnerable", 0) == 0   # guard skipped


# --- ExpectAFight: energy off the Attack count in hand ----------------------

def test_expect_a_fight_gains_energy_per_attack_in_hand():
    state = make_state()
    state.player.energy = 0
    state.player.hand = [card("a1"), card("a2"), card("a3"),
                         card("s1", type="skill")]
    fx = [{"op": "energy",
           "amount_formula": {"per": 1, "count": "attacks_in_hand"}}]
    effects.resolve_card(state, card("eaf", type="skill", fx=fx))
    assert state.player.energy == 3               # 3 attacks, the skill uncounted


# --- PactsEnd: exhaust-pile threshold predicate -----------------------------

def test_pacts_end_fires_only_at_three_exhausted():
    fx = [{"op": "conditional", "if": "exhaust_pile_at_least_3",
           "then": [{"op": "damage", "amount": 17, "target": "all_enemies"}]}]

    short = make_state()
    short.player.exhaust_pile = [card("x"), card("y")]      # only 2
    effects.resolve_card(short, card("pacts", fx=fx))
    assert not _damage_events(short)

    ready = make_state()
    ready.player.exhaust_pile = [card("x"), card("y"), card("z")]
    effects.resolve_card(ready, card("pacts", fx=fx))
    assert len(_damage_events(ready)) == 1


# --- Pillage: draw one at a time, exit on the first non-Attack --------------

def test_pillage_keeps_drawing_while_attacks_and_keeps_the_stopper():
    state = make_state()
    state.player.hand = []
    state.player.draw_pile = [card("a1"), card("a2"),
                              card("s1", type="skill"), card("a3")]
    effects.resolve_card(state, card("pillage", type="skill",
                                     fx=[{"op": "draw_while",
                                          "while_type": "attack"}]))
    hand_ids = [c.id for c in state.player.hand]
    assert hand_ids == ["a1", "a2", "s1"]         # stops AFTER the skill, keeps it
    assert [c.id for c in state.player.draw_pile] == ["a3"]


def test_pillage_is_safe_on_an_empty_deck():
    state = make_state()
    state.player.hand = []
    state.player.draw_pile = []
    state.player.discard_pile = []
    effects.resolve_card(state, card("pillage", type="skill",
                                     fx=[{"op": "draw_while",
                                          "while_type": "attack"}]))
    assert state.player.hand == []
