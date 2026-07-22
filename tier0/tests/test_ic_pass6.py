"""Data-free pins for the bounded Ironclad pass-6 primitives."""

from tier0.content import upgrades
from tier0.engine import combat, effects, refpowers, resources
from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state
from tier05 import draft


def card(cid="c", type="attack", cost=0, fx=None, **kw):
    return Card(id=cid, name=cid, cost=cost, type=type,
                effects=fx if fx is not None else [], **kw)


def test_drum_of_battle_pays_energy_only_when_exhausted():
    state = make_state()
    state.player.energy = 1
    drum = card("drum", type="skill", on_exhaust_energy=2)
    burner = card("burner", type="skill", fx=[
        {"op": "exhaust_from", "amount": 1},
    ])
    state.player.hand = [drum, burner]

    combat.play_card(state, burner)

    assert state.player.energy == 3
    assert drum in state.player.exhaust_pile
    assert state.cards_exhausted_this_turn == 1


def test_drum_energy_obeys_no_energy_gain():
    state = make_state()
    state.player.energy = 1
    state.no_energy_gain_ceiling = 1

    refpowers.exhaust_card(
        state, card("drum", type="skill", on_exhaust_energy=2))

    assert state.player.energy == 1
    assert any(ev["event"] == "energy_gain_denied" for ev in state.log)


def test_multi_block_branch_preserves_each_block_gained_hook():
    state = make_state(enemies=[make_enemy(hp=30)])
    state.player.energy = 1
    state.cards_exhausted_this_turn = 1
    state.player.powers.update({"unmovable": 1, "juggernaut": 3})
    evil_eye = card("evil", type="skill", cost=1, fx=[{
        "op": "conditional", "if": "card_exhausted_this_turn",
        "then": [{"op": "block", "amount": 4},
                 {"op": "block", "amount": 4}],
        "else": [{"op": "block", "amount": 4}],
    }])
    state.player.hand = [evil_eye]

    combat.play_card(state, evil_eye)

    assert state.player.block == 16       # current CardPlay doubled as a unit
    assert state.enemies[0].hp == 24      # Juggernaut fires for both gains
    assert state.block_gain_card_plays_this_turn == 2


def test_forgotten_ritual_predicate_reads_prior_exhaust_this_turn():
    ritual = card("ritual", type="skill", fx=[{
        "op": "conditional", "if": "card_exhausted_this_turn",
        "then": [{"op": "energy", "amount": 3}],
    }])
    cold = make_state()
    effects.resolve_card(cold, ritual)
    assert cold.player.energy == 0

    live = make_state()
    live.cards_exhausted_this_turn = 1
    effects.resolve_card(live, ritual)
    assert live.player.energy == 3


def test_perfected_strike_counts_all_strike_named_cards_including_itself():
    state = make_state()
    perfected = card("ic_perfected_strike", tags=["strike"], fx=[{
        "op": "damage", "target": "enemy",
        "amount_formula": {"base": 2, "per": 3, "count": "strike_cards"},
    }])
    state.player.hand = [perfected]
    state.player.draw_pile = [card("ic_pommel_strike", tags=["strike"]),
                              card("not_a_hit")]
    state.player.discard_pile = [card("ic_setup_strike", tags=["strike"])]

    effects.resolve_card(state, perfected)

    assert state.enemies[0].hp == state.enemies[0].max_hp - 11
    assert policy._expected_damage(state, perfected) == 11
    assert draft._static_power(perfected, state.player.draw_pile) > 0

    # Names are not tags: leaked or modded strike-like ids cannot inflate it.
    state.player.draw_pile.append(card("not_really_a_strike"))
    assert policy._expected_damage(state, perfected) == 11


def test_rampage_mutates_only_its_circulating_card_instance():
    state = make_state(enemies=[make_enemy(hp=30)])
    rampage = card("rampage", fx=[
        {"op": "damage", "amount": 3, "target": "enemy"},
        {"op": "grow_damage", "amount": 2},
    ])

    effects.resolve_card(state, rampage)
    effects.resolve_card(state, rampage)

    assert state.enemies[0].hp == 22       # 3, then the grown 5
    assert rampage.effects[0]["amount"] == 7


def test_armaments_upgrade_preserves_rampage_growth(monkeypatch):
    monkeypatch.setattr(upgrades, "_upgrade_index", lambda: {
        "rampage": {"damage_growth": 4},
    })
    state = make_state()
    grown = card("rampage", fx=[
        {"op": "damage", "amount": 7, "target": "enemy"},
        {"op": "grow_damage", "amount": 2},
    ])
    state.player.hand = [grown]

    effects._op_upgrade_in_hand(
        state, {"op": "upgrade_in_hand", "scope": "chosen"}, card("arm"))

    upgraded = state.player.hand[0]
    assert upgraded.id == "rampage+"
    assert upgraded.effects[0]["amount"] == 7       # live growth survives
    assert upgraded.effects[1]["amount"] == 6       # upgrade moves growth rate


def test_second_wind_exhausts_non_attacks_and_blocks_per_card():
    state = make_state()
    state.player.energy = 1
    second_wind = card("second_wind", type="skill", cost=1, exhaust=True,
                       fx=[
                           {"op": "exhaust_from", "amount": "all",
                            "filter": "non_attack"},
                           {"op": "block", "amount": 5,
                            "times": "exhausted_this_card"},
                       ])
    skill = card("skill", type="skill")
    power = card("power", type="power")
    attack = card("attack")
    state.player.hand = [skill, power, attack, second_wind]

    combat.play_card(state, second_wind)

    assert skill in state.player.exhaust_pile
    assert power in state.player.exhaust_pile
    assert attack in state.player.hand
    assert state.player.block == 10
    assert state.block_gains_this_card == 2


def test_spite_predicate_and_turn_reset_follow_true_hp_loss():
    state = make_state(enemies=[make_enemy(hp=30)])
    spite = card("spite", fx=[{
        "op": "conditional", "if": "hp_lost_this_turn",
        "then": [{"op": "damage", "amount": 4, "times": 2,
                  "target": "enemy"}],
        "else": [{"op": "damage", "amount": 4, "target": "enemy"}],
    }])
    resources.note_player_hp_loss(state, 2)
    effects.resolve_card(state, spite)
    assert state.enemies[0].hp == 22

    refpowers.reset_turn_counters(state)
    assert state.hp_lost_this_turn == 0
    assert state.cards_exhausted_this_turn == 0


def test_stomp_cost_reads_attacks_already_played_this_turn():
    state = make_state(enemies=[make_enemy(hp=50)])
    state.player.energy = 5
    setup = card("setup", cost=0, fx=[
        {"op": "damage", "amount": 1, "target": "enemy"},
    ])
    stomp = card("stomp", cost=3, cost_reduction_per_attack_this_turn=1)
    state.player.hand = [setup, stomp]

    assert combat.card_cost(state, stomp) == 3
    combat.play_card(state, setup)
    assert combat.card_cost(state, stomp) == 2
    refpowers.reset_turn_counters(state)
    assert combat.card_cost(state, stomp) == 3


def test_tear_asunder_counts_damage_events_not_hp_amount():
    state = make_state(enemies=[make_enemy(hp=40)])
    resources.note_player_hp_loss(state, 7)
    resources.note_player_hp_loss(state, 1)
    tear = card("tear", fx=[{
        "op": "damage", "amount": 3, "target": "enemy",
        "times_formula": {"base": 1, "per": 1,
                          "count": "player_damage_events"},
    }])

    effects.resolve_card(state, tear)

    assert state.player_damage_events == 2
    assert state.enemies[0].hp == 31       # three hits, not nine
    assert policy._expected_damage(state, tear) == 9
