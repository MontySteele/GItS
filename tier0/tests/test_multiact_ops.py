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


def test_turn_start_damage_that_empties_a_bar_revives_instead_of_winning():
    """EB-29a: Salon upkeep damages enemies inside player_turn_start_triggers,
    which sat between the last _settle_phases and the state.over early-return.
    A phased boss killed there ended the combat as a WIN with bars still
    queued -- 66% of Furina/test_subject wins were counterfeit."""
    e = _phased_boss()
    e.hp = 6                                     # crabaletta's tick kills it
    st = make_state(enemies=[e])
    st.player.draw_pile = _clog()
    st.player.salon = ["crabaletta"]
    st.player.encore = 5
    combat._player_turn(st, NULL_PILOT)
    assert e.alive and e.max_hp == 30            # revived into the queued bar
    assert not st.over


def test_revive_costs_the_boss_its_respawn_turn():
    """EB-29b: the real Test Subject spends a full enemy turn reviving and
    deals nothing on it (dossier :51-58,129,134); the sim revived instantly,
    silently denying the player one free turn per knockdown."""
    e = _phased_boss()
    st = make_state(enemies=[e])
    e.hp = 0
    combat._settle_phases(st)
    assert e.sleep_turns == 1
    hp_before = st.player.hp
    combat._enemy_turn(st, e)                    # the respawn turn: skipped
    assert st.player.hp == hp_before
    assert e.current_intent()["amount"] == 9     # intent did not advance
    combat._enemy_turn(st, e)                    # next turn: acts normally
    assert st.player.hp < hp_before


# --- R128: the promoted Test Subject mechanics (EB-29q, 2026-08-07) ---------

def _skill(cid="a_skill"):
    return Card(id=cid, name="skill", cost=0, type="skill", effects=[])


def test_enrage_feeds_strength_per_skill_and_survives_revives():
    e = _phased_boss()
    e.powers["enrage"] = 2
    st = make_state(enemies=[e])
    combat._finish_play(st, _skill())
    assert e.powers["strength"] == 2
    combat._finish_play(st, Card(id="atk", name="atk", cost=0,
                                 type="attack", effects=[]))
    assert e.powers["strength"] == 2             # attacks feed nothing
    e.hp = 0
    combat._settle_phases(st)                    # revive: a new body EXCEPT
    assert e.powers["strength"] == 2             # Strength and Enrage
    assert e.powers["enrage"] == 2               # (dossier :240)
    combat._finish_play(st, _skill("b_skill"))
    assert e.powers["strength"] == 4


def test_painful_stabs_wounds_per_unblocked_hit():
    e = Enemy(hp=50, max_hp=50, name="ts2",
              intents=[{"kind": "attack", "amount": 10, "times": 3}],
              powers={"painful_stabs": 1})
    st = make_state(enemies=[e])
    st.player.hp = st.player.max_hp = 200
    combat._enemy_turn(st, e)
    wounds = [c for c in st.player.discard_pile if c.id == "status_wound"]
    assert len(wounds) == 3                      # one per unblocked HIT
    st.player.discard_pile.clear()
    st.player.block = 100                        # fully blocked: no wounds
    combat._enemy_turn(st, e)
    assert not [c for c in st.player.discard_pile if c.id == "status_wound"]


def test_nemesis_toggles_intangible_and_the_phase_opens_capped():
    e = Enemy(hp=20, max_hp=20, name="ts",
              intents=[{"kind": "attack", "amount": 5}],
              phases=[{"hp": 30, "powers": {"nemesis": 1},
                       "intents": [{"kind": "attack", "amount": 5}]}])
    st = make_state(enemies=[e])
    st.player.hp = st.player.max_hp = 200
    e.hp = 0
    combat._settle_phases(st)
    assert e.powers["nemesis"] == 1
    assert e.powers["intangible"] == 1           # the phase opens capped
    combat._enemy_turn(st, e)                    # respawn sleep: no toggle
    assert e.powers["intangible"] == 1
    combat._enemy_turn(st, e)                    # acting turn 1 ends: off
    assert "intangible" not in e.powers
    combat._enemy_turn(st, e)                    # acting turn 2 ends: on
    assert e.powers["intangible"] == 1


def test_intangible_caps_the_direct_hp_sites_too():
    from tier0.engine import refpowers
    e = make_enemy(hp=40)
    st = make_state(enemies=[e])
    e.powers["intangible"] = 1
    refpowers.unblockable_unpowered_damage(st, e, 30)
    assert e.hp == 40 - C.INTANGIBLE_DAMAGE_CAP  # unblockable != uncappable
    refpowers.unpowered_damage(st, e, 25)
    assert e.hp == 40 - 2 * C.INTANGIBLE_DAMAGE_CAP


def test_times_ramp_per_use_grows_the_hit_count():
    e = Enemy(hp=500, max_hp=500, name="ts2",
              intents=[{"kind": "attack", "amount": 10, "times": 3,
                        "times_ramp_per_use": 1}])
    st = make_state(enemies=[e])
    st.player.hp = st.player.max_hp = 500
    combat._enemy_turn(st, e)
    assert st.player.hp == 500 - 30              # 3 hits of 10
    combat._enemy_turn(st, e)
    assert st.player.hp == 500 - 30 - 40         # then 4 -- the real claw


# --- intent ramps (2026-07-24: the Test Subject act-3 diagnosis) ------------
#
# `ramp` is per TURN and counts from the start of the enemy's CURRENT phase;
# `ramp_per_use` is per USE of that intent. Both are read through one helper
# (Enemy.ramped_amount) so the enemy turn and the pilot's incoming-damage
# estimate cannot drift apart, which they had.


def test_unphased_ramp_still_counts_from_combat_start():
    """The frozen PUNISHER's shape: atk 9, ramp +2 after turn 3. An unphased
    enemy has phase_start_turn 0, so this must be bit-identical to the
    pre-phase-relative behaviour -- the whole battery calibration rests on it.
    """
    e = make_enemy(intents=[{"kind": "attack", "amount": 9, "ramp": 2,
                             "ramp_after": 3}])
    got = [e.ramped_amount(e.current_intent(), turn) for turn in range(1, 8)]
    assert got == [9, 9, 9, 11, 13, 15, 17]


def test_ramp_inside_a_phase_counts_from_the_phase_change():
    """THE act-3 bug. A ramping intent that first appears in a boss's second
    bar must not arrive pre-ramped by however long the first bar took."""
    e = Enemy(hp=10, max_hp=10, name="phased", is_boss=True,
              intents=[{"kind": "attack", "amount": 5}],
              phases=[{"hp": 30,
                       "intents": [{"kind": "attack", "amount": 10,
                                    "ramp": 3}]}],
              counts_for_fatal=False)
    st = make_state(enemies=[e])
    st.turn = 9                      # the first bar took nine turns to chew
    e.hp = 0
    combat._settle_phases(st)
    assert e.phase_start_turn == 9
    # Opens at its printed amount on the turn the bar flips, not 10 + 3*9.
    assert e.ramped_amount(e.current_intent(), 9) == 10
    assert e.ramped_amount(e.current_intent(), 11) == 16


def test_ramp_per_use_grows_per_use_not_per_turn():
    """Test Subject's Multi-Claw gains a HIT each time it is taken. A turn
    ramp cannot express that: the value would depend on how many non-attack
    beats sit between two uses, so adding a beat would silently retune it."""
    e = make_enemy(hp=999, intents=[
        {"kind": "attack", "amount": 10, "times": 3, "ramp_per_use": 3},
        {"kind": "block", "amount": 1},          # the beat in between
    ])
    st = make_state(enemies=[e], hp=500)      # survive the whole sequence:
    seen = []                                 # a dead player stops advancing
    for _ in range(6):                           # three uses, three beats
        if e.current_intent()["kind"] == "attack":
            seen.append(e.ramped_amount(e.current_intent(), st.turn) * 3)
        st.turn += 1
        combat._enemy_turn(st, e)
    assert seen == [30, 39, 48]                  # the authored act-3 line


def test_ramp_per_use_counters_reset_on_a_phase_change():
    e = Enemy(hp=10, max_hp=10, name="phased",
              intents=[{"kind": "attack", "amount": 4, "ramp_per_use": 5}],
              phases=[{"hp": 30, "intents": [{"kind": "attack", "amount": 10,
                                              "ramp_per_use": 3}]}],
              counts_for_fatal=False)
    st = make_state(enemies=[e])
    combat._enemy_turn(st, e)                    # first bar takes its move
    combat._enemy_turn(st, e)
    assert e.intent_uses                         # counted
    e.hp = 0
    combat._settle_phases(st)
    assert e.intent_uses == {}
    assert e.ramped_amount(e.current_intent(), st.turn) == 10


def test_pilot_and_enemy_turn_agree_on_a_ramped_intent():
    """These were duplicated formulas. A pilot that mispredicts incoming
    damage blocks against the wrong number."""
    from tier0.pilot import policy
    e = make_enemy(hp=999, intents=[{"kind": "attack", "amount": 10,
                                     "ramp": 4}])
    st = make_state(enemies=[e])
    st.turn = 5
    e.phase_start_turn = 2
    predicted = policy._incoming_damage(st)
    hp0 = st.player.hp
    combat._enemy_turn(st, e)
    assert predicted == hp0 - st.player.hp == 22      # 10 + 4 * (5 - 2)


def test_test_subject_second_bar_opens_at_its_authored_number():
    """End-to-end on the shipped roster row. R128 promoted Multi-Claw to the
    real gains-a-hit shape, so the curve is the dossier's 30 -> 40 -> 50
    (3, then 4, then 5 hits of 10) -- not the retired 30 -> 39 -> 48
    amount-ramp approximation this test used to pin."""
    from tier05 import acts
    spec = next(s for s in acts.boss_pool(2) if s["id"] == "test_subject")
    boss = acts.spawn(spec, random.Random(0))[0]
    st = make_state(enemies=[boss], hp=500)   # ditto: read the curve, not the
    st.turn = 12                              # kill. A realistic first bar.
    boss.hp = 0
    combat._settle_phases(st)
    st.turn += 1
    combat._enemy_turn(st, boss)   # EB-29b: the revive spends the respawn
    #                                turn first; the curve starts after it
    seen = []
    for _ in range(3):
        if boss.current_intent()["kind"] == "attack":
            seen.append(boss.ramped_amount(boss.current_intent(), st.turn)
                        * boss.ramped_times(boss.current_intent()))
        st.turn += 1
        combat._enemy_turn(st, boss)
    assert seen == [30, 40, 50]


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
