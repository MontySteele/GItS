"""Multi-act §10.2 engine ops (RATIFIED 2026-07-23): status-card injection,
enemy self-heal, on-ally-death (Crab Rage), HP-threshold phases, and the
status cards' combat semantics. All ops are inert-by-default -- the frozen
battery never sets them -- so these tests are the ops' only exercisers."""

import random

from tier0 import constants as C
from tier0.engine import combat, statuses
from tier0.engine.state import Card, Enemy
from tier0.tests.conftest import make_enemy, make_state

NULL_PILOT = (lambda state: None)


def _clog(n=8):
    """Plain unplayable-ish filler so draws/flushes have material."""
    return [Card(id=f"filler{i}", name="f", cost=9, type="skill")
            for i in range(n)]


# --- statuses: unplayable, correct per-status semantics ---------------------


def test_status_cards_are_unplayable_and_fresh_instances():
    st = make_state()
    st.player.energy = 99
    for sid in statuses.status_ids():
        card = statuses.make_status(sid)
        st.player.hand.append(card)
        assert not combat.card_playable(st, card)
    assert statuses.make_status("dazed") is not statuses.make_status("dazed")


def test_inject_intent_fills_the_named_pile():
    st = make_state()
    enemy = st.enemies[0]
    enemy.intents = [
        {"kind": "inject", "status": "dazed", "count": 3, "pile": "draw"},
        {"kind": "inject", "status": "toxic", "count": 2},           # discard
        {"kind": "inject", "status": "burn", "count": 1, "pile": "hand"},
    ]
    combat._enemy_turn(st, enemy)
    assert sum(c.id == "status_dazed" for c in st.player.draw_pile) == 3
    combat._enemy_turn(st, enemy)
    assert sum(c.id == "status_toxic" for c in st.player.discard_pile) == 2
    combat._enemy_turn(st, enemy)
    assert sum(c.id == "status_burn" for c in st.player.hand) == 1


def test_toxic_costs_hp_on_draw():
    st = make_state()
    st.player.draw_pile = [statuses.make_status("toxic")] + _clog(4)
    hp0 = st.player.hp
    st.draw(5)
    assert st.player.hp == hp0 - 2
    assert any(ev["event"] == "status_draw_damage" for ev in st.log)


def test_burn_and_wither_tick_at_turn_end_blockable_dazed_is_ethereal():
    st = make_state()
    p = st.player
    p.draw_pile = _clog(5)
    p.hand = [statuses.make_status("burn"), statuses.make_status("wither"),
              statuses.make_status("dazed")]
    p.block = 0
    hp0 = p.hp
    combat._player_turn(st, NULL_PILOT)
    # burn 2 + wither 3, no block held at turn end (pilot played nothing).
    assert p.hp == hp0 - 5
    # dazed exhausted via the ethereal flush; burn/wither discarded.
    assert any(c.id == "status_dazed" for c in p.exhaust_pile)
    assert not any(c.id == "status_dazed" for c in p.discard_pile)
    assert any(c.id == "status_burn" for c in p.discard_pile)
    assert any(c.id == "status_wither" for c in p.discard_pile)


def test_status_eot_damage_eats_block_first():
    st = make_state()
    p = st.player
    p.draw_pile = _clog(5)
    p.hand = [statuses.make_status("wither")]
    hp0 = p.hp

    def block_pilot(state):
        state.player.block = 10          # simulate a block play, once
        return None

    combat._player_turn(st, block_pilot)
    assert p.hp == hp0                   # 3 fully blocked
    assert p.block == 7


# --- heal intent ------------------------------------------------------------


def test_heal_intent_caps_at_max_hp():
    st = make_state()
    enemy = st.enemies[0]
    enemy.hp = 30
    enemy.intents = [{"kind": "heal", "amount": 45}]
    combat._enemy_turn(st, enemy)
    assert enemy.hp == enemy.max_hp == 50
    assert any(ev["event"] == "enemy_heal" and ev["amount"] == 20
               for ev in st.log)


# --- on_ally_death (Crab Rage) ----------------------------------------------


def test_ally_death_buff_fires_once_at_next_turn_start():
    claw_a = make_enemy(hp=50, name="crusher")
    claw_b = make_enemy(hp=50, name="rocket")
    claw_b.ally_death_buff = {"powers": {"strength": 6}, "block": 99}
    st = make_state(enemies=[claw_a, claw_b])

    combat._enemy_turn(st, claw_b)
    assert claw_b.powers.get("strength", 0) == 0     # ally alive: no trigger

    claw_a.hp = 0
    combat._enemy_turn(st, claw_b)
    assert claw_b.powers["strength"] == 6
    assert claw_b.block >= 99                        # applied after block reset
    combat._enemy_turn(st, claw_b)
    assert claw_b.powers["strength"] == 6            # fires ONCE


# --- phases -----------------------------------------------------------------


def _phased_boss():
    e = Enemy(hp=20, max_hp=20, name="test_subject", is_boss=True,
              intents=[{"kind": "attack", "amount": 5}],
              phases=[{"hp": 30, "intents": [{"kind": "attack", "amount": 9}]}],
              counts_for_fatal=False)
    return e


def test_phase_down_revives_with_fresh_bar_moves_and_cleared_powers():
    e = _phased_boss()
    st = make_state(enemies=[e])
    e.powers["vulnerable"] = 3
    e.hp = 0
    combat._settle_phases(st)
    assert e.alive and e.hp == e.max_hp == 30
    assert e.current_intent()["amount"] == 9
    assert e.powers == {}
    assert e.counts_for_fatal                  # last phase: a real death now
    assert not st.over
    e.hp = 0
    combat._settle_phases(st)                  # no phases left: stays dead
    assert not e.alive and st.over


def test_phased_boss_fight_runs_through_both_bars():
    e = _phased_boss()
    p_cards = [Card(id=f"hit{i}", name="hit", cost=0, type="attack",
                    effects=[{"op": "damage", "amount": 12}])
               for i in range(12)]
    st = make_state(enemies=[e])
    st.player.hp = st.player.max_hp = 500
    st.player.draw_pile = p_cards

    def pilot(state):
        playable = [c for c in state.player.hand
                    if combat.card_playable(state, c)]
        return playable[0] if playable else None

    end = combat.run_fight(st.player, [e], pilot, seed=3)
    assert any(ev["event"] == "phase_change" for ev in end.log)
    assert not e.alive
    assert end.player.alive


# --- Slow / Skittish (§10.9 promotions, red-pen 2026-07-23) -----------------


def _attack(amount, i=0):
    return Card(id=f"atk{i}", name="atk", cost=0, type="attack",
                effects=[{"op": "damage", "amount": amount}])


def test_slow_amps_attack_damage_per_card_played_this_turn():
    st = make_state()
    e = st.enemies[0]
    e.slow = 10
    st.player.energy = 9
    st.player.hand = [_attack(10, 0), _attack(10, 1)]
    st.cards_played_this_turn = 0
    combat.play_card(st, st.player.hand[0])
    # 1st card of the turn counts itself: 10 * 1.1 = 11.
    assert e.hp == 50 - 11
    combat.play_card(st, st.player.hand[0])
    # 2nd card: 10 * 1.2 = 12.
    assert e.hp == 50 - 11 - 12


def test_slow_does_not_amp_skill_damage():
    st = make_state()
    e = st.enemies[0]
    e.slow = 10
    st.player.energy = 9
    skill = Card(id="zap", name="zap", cost=0, type="skill",
                 effects=[{"op": "damage", "amount": 10}])
    st.player.hand = [skill]
    combat.play_card(st, skill)
    assert e.hp == 50 - 10          # "more damage from Attacks" only


def test_skittish_blocks_after_first_hit_each_turn_and_latch_resets():
    st = make_state()
    e = st.enemies[0]
    e.skittish = 6
    st.player.energy = 9
    st.player.draw_pile = _clog(5)
    st.player.hand = [_attack(5, 0), _attack(5, 1)]
    combat.play_card(st, st.player.hand[0])
    # First hit lands unmitigated; the 6 Block arrives AFTER it resolves.
    assert e.hp == 50 - 5
    assert e.block == 6 and e.skittish_fired
    combat.play_card(st, st.player.hand[0])
    # Second hit of the turn eats the Skittish block.
    assert e.hp == 50 - 5
    assert e.block == 1
    combat._player_turn(st, NULL_PILOT)
    assert not e.skittish_fired      # per-turn latch
