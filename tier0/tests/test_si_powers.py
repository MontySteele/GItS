"""Pins for the SILENT's parity powers (coverage pass, 2026-07-27).

Same contract as test_si_effects.py and test_ic_effects.py: every test drives
a mechanic the way a card row would and asserts on the runtime quantity, and
NO number extracted from the game appears here. These run on CI, where
game_ref/ does not exist -- the mechanics are ours even though the pool that
motivates them is not.

Nineteen powers went on the SUPPORTED_POWERS dial in this pass. They are
ordinary parity powers that happen to be hers, and every one is a dead branch
for the roster: no committed card applies any of them.

TWO OF HERS ARE NOT HERE AND THAT IS THE POINT. Sneaky and Flanking are
recorded in refpowers.MULTIPLAYER_ONLY_POWERS instead of implemented, because
in a single-player fight neither can fire at all -- see the last test.
"""

from tier0 import constants as C
from tier0.engine import combat, effects, powers, refpowers
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state


def card(cid="c", type="skill", cost=0, fx=None, **kw):
    return Card(id=cid, name=cid, cost=cost, type=type,
                effects=fx if fx is not None else [], **kw)


def play(state, fx, **kw):
    """Resolve a one-off card through the full play path (hooks included)."""
    c = card("driver", fx=fx, **kw)
    state.player.hand.append(c)
    combat.play_card(state, c)
    return c


# --- retaliation and mitigation -------------------------------------------

def test_thorns_hits_the_dealer_even_through_full_block():
    """ThornsPower.BeforeDamageReceived never looks at the DamageResult, so a
    fully blocked hit is still thorned -- the same shape FlameBarrier has."""
    state = make_state()
    enemy = make_enemy(hp=40)
    state.enemies = [enemy]
    powers.apply_power(state, state.player, "thorns", 3)
    state.player.block = 99
    refpowers.on_damage_received(state, state.player, 0, enemy,
                                 powered_attack=True)
    assert enemy.hp == 37


def test_thorns_ignores_an_unpowered_source():
    state = make_state()
    enemy = make_enemy(hp=40)
    state.enemies = [enemy]
    powers.apply_power(state, state.player, "thorns", 3)
    refpowers.on_damage_received(state, state.player, 5, enemy,
                                 powered_attack=False)
    assert enemy.hp == 40


def test_thorns_survives_the_enemy_turn_end():
    """FlameBarrier is removed at the enemy side's turn end and Thorns is
    not. Sharing the code path must not make them share the lifetime."""
    state = make_state()
    powers.apply_power(state, state.player, "thorns", 3)
    powers.apply_power(state, state.player, "flame_barrier", 3)
    refpowers.after_enemy_side_turn_end(state)
    assert state.player.powers.get("thorns") == 3
    assert not state.player.powers.get("flame_barrier")


def test_intangible_caps_a_hit_at_one_and_leaves_a_smaller_one_alone():
    state = make_state()
    powers.apply_power(state, state.player, "intangible", 2)
    assert powers.modify_damage_taken(state.player, 40) == C.INTANGIBLE_DAMAGE_CAP
    assert powers.modify_damage_taken(state.player, 0) == 0


def test_intangible_is_the_last_word_over_vulnerable():
    """It is a CAP, not a multiplier: an amplified hit still lands as 1."""
    state = make_state()
    powers.apply_power(state, state.player, "intangible", 1)
    powers.apply_power(state, state.player, "vulnerable", 3)
    assert powers.modify_damage_taken(state.player, 20) == C.INTANGIBLE_DAMAGE_CAP


def test_intangible_caps_unblockable_damage_and_a_poison_tick():
    """Unblockable is not uncappable: ModifyHpLostAfterOsty clamps ALL HP
    loss to 1, and the poison tick routes through the unblockable path --
    surviving poison at 1/tick is most of what Wraith Form promises."""
    state = make_state()
    powers.apply_power(state, state.player, "intangible", 1)
    hp = state.player.hp
    refpowers.damage_player_unblockable(state, 9, reason="test")
    assert state.player.hp == hp - C.INTANGIBLE_DAMAGE_CAP
    powers.apply_power(state, state.player, "poison", 5)
    refpowers.poison_tick(state, state.player)
    assert state.player.hp == hp - 2 * C.INTANGIBLE_DAMAGE_CAP
    assert state.player.powers["poison"] == 4      # decrement is untouched


def test_intangible_caps_an_enemy_poison_tick_too():
    state = make_state()
    enemy = make_enemy(hp=40)
    state.enemies = [enemy]
    powers.apply_power(state, enemy, "intangible", 1)
    powers.apply_power(state, enemy, "poison", 6)
    refpowers.poison_tick(state, enemy)
    assert enemy.hp == 40 - C.INTANGIBLE_DAMAGE_CAP


def test_intangible_ticks_down_on_the_enemy_side_turn_end():
    state = make_state()
    powers.apply_power(state, state.player, "intangible", 2)
    refpowers.after_enemy_side_turn_end(state)
    assert state.player.powers["intangible"] == 1


# --- block economy ---------------------------------------------------------

def test_blur_carries_block_across_one_turn_boundary_per_stack():
    state = make_state()
    powers.apply_power(state, state.player, "blur", 1)
    assert refpowers.should_clear_block(state.player) is False
    refpowers.player_turn_start_late(state)          # site F decrements
    assert state.player.powers["blur"] == 0
    assert refpowers.should_clear_block(state.player) is True


def test_shadowmeld_doubles_card_block_and_power_block_exactly_once():
    """ModifyBlockMultiplicative carries no card/power guard, and tier0's two
    block paths are disjoint -- so the doubling has to live in both funnels
    and must not compound when a gain passes through one of them."""
    state = make_state()
    p = state.player
    powers.apply_power(state, p, "shadowmeld", 2)    # 2^2
    assert powers.modify_block_gained(p, 5) == 20
    p.block = 0
    refpowers.gain_block(state, p, 5)
    assert p.block == 20


def test_afterimage_pays_per_card_played_but_not_for_its_own_play():
    """The Dictionary<CardModel,int> filled at BeforeCardPlayed is what stops
    the card that GRANTS Afterimage from paying itself."""
    state = make_state()
    play(state, [{"op": "apply_power", "power": "afterimage", "amount": 2,
                  "target": "self"}], type="power")
    assert state.player.block == 0                   # granting play pays 0
    play(state, [])
    assert state.player.block == 2


def test_block_next_turn_lands_after_the_reset_not_before():
    state = make_state()
    state.enemies = [make_enemy(hp=200)]
    play(state, [{"op": "block_next_turn", "amount": 7}])
    combat._player_turn(state, lambda s: None)
    assert state.player.block == 7
    assert "block_next_turn" not in state.player.powers


# --- poison engine ---------------------------------------------------------

def test_envenom_poisons_only_on_an_unblocked_powered_hit():
    state = make_state()
    enemy = make_enemy(hp=40)
    state.enemies = [enemy]
    powers.apply_power(state, state.player, "envenom", 2)
    enemy.block = 99
    effects.deal_damage_to_enemy(state, enemy, 5, source="attack")
    assert not enemy.powers.get("poison")            # fully blocked
    enemy.block = 0
    effects.deal_damage_to_enemy(state, enemy, 5, source="attack")
    assert enemy.powers["poison"] == 2


def test_an_unpowered_tick_does_not_envenom():
    state = make_state()
    enemy = make_enemy(hp=40)
    state.enemies = [enemy]
    powers.apply_power(state, state.player, "envenom", 2)
    refpowers.unpowered_damage(state, enemy, 5)
    assert not enemy.powers.get("poison")


def test_noxious_fumes_poisons_every_enemy_at_the_late_turn_start():
    state = make_state()
    state.enemies = [make_enemy(hp=40, name="a"), make_enemy(hp=40, name="b")]
    powers.apply_power(state, state.player, "noxious_fumes", 3)
    refpowers.player_turn_start_late(state)
    assert all(e.powers["poison"] == 3 for e in state.enemies)


def test_outbreak_fires_on_every_third_poison_application():
    """The counter is per APPLICATION, not per stack: one nine-stack poison
    does not fire it, and three separate one-stack poisons do."""
    state = make_state()
    enemy = make_enemy(hp=90)
    state.enemies = [enemy]
    state.in_player_turn = True
    powers.apply_power(state, state.player, "outbreak", 5)
    powers.apply_power(state, enemy, "poison", 9, applier=state.player)
    assert enemy.hp == 90                            # one application only
    powers.apply_power(state, enemy, "poison", 1, applier=state.player)
    powers.apply_power(state, enemy, "poison", 1, applier=state.player)
    assert enemy.hp == 85                            # the third one pays
    assert state.outbreak_poisonings == 0


def test_corrosive_wave_poisons_on_every_draw_and_expires_that_turn():
    state = make_state()
    enemy = make_enemy(hp=40)
    state.enemies = [enemy]
    state.player.draw_pile = [card("a"), card("b")]
    powers.apply_power(state, state.player, "corrosive_wave", 2)
    state.draw(2)
    assert enemy.powers["poison"] == 4               # per CARD, not per draw
    powers.on_turn_end(state, state.player)
    assert "corrosive_wave" not in state.player.powers


def test_accelerant_is_read_by_the_poison_clock_it_was_always_written_for():
    """AccelerantPower has no hooks of its own -- it exists to be read by
    PoisonPower's TriggerCount, which poison_tick already transcribed. Putting
    it on the dial implements the card; the behaviour was already here."""
    state = make_state()
    enemy = make_enemy(hp=40)
    state.enemies = [enemy]
    enemy.powers["poison"] = 4
    powers.apply_power(state, state.player, "accelerant", 1)
    refpowers.poison_tick(state, enemy)
    # Two ticks, and the second is SMALLER: each tick deals the current stack
    # and then decrements it, so 4 + 3 rather than 4 + 4.
    assert enemy.hp == 33
    assert enemy.powers["poison"] == 2


# --- tempo and velocity ----------------------------------------------------

def test_speedster_hits_on_a_mid_turn_draw_but_not_on_the_opening_hand():
    state = make_state()
    enemy = make_enemy(hp=40)
    state.enemies = [enemy]
    state.in_player_turn = True
    state.player.draw_pile = [card("a"), card("b")]
    powers.apply_power(state, state.player, "speedster", 3)
    state.draw(1, from_hand_draw=True)
    assert enemy.hp == 40
    state.draw(1)
    assert enemy.hp == 37


def test_draw_cards_next_turn_pays_once_at_the_next_turn_start():
    state = make_state()
    state.enemies = [make_enemy(hp=200)]
    state.player.draw_pile = [card(f"c{i}") for i in range(20)]
    powers.apply_power(state, state.player, "draw_cards_next_turn", 2)
    hands = []
    combat._player_turn(state, lambda s: hands.append(len(s.player.hand)))
    combat._player_turn(state, lambda s: hands.append(len(s.player.hand)))
    assert hands[0] == C.CARDS_DRAWN_PER_TURN + 2
    assert hands[1] == C.CARDS_DRAWN_PER_TURN


def test_tools_of_the_trade_draws_more_and_gives_the_same_number_back():
    """The card is a FILTER, not card advantage: +Amount at site D, then
    -Amount as a chosen discard at site E."""
    state = make_state()
    state.enemies = [make_enemy(hp=200)]
    state.player.draw_pile = [card(f"c{i}") for i in range(20)]
    powers.apply_power(state, state.player, "tools_of_the_trade", 2)
    hands = []
    combat._player_turn(state, lambda s: hands.append(len(s.player.hand)))
    assert hands[0] == C.CARDS_DRAWN_PER_TURN
    assert len(state.player.discard_pile) >= 2


def test_burst_replays_a_skill_once_and_spends_a_stack():
    state = make_state()
    powers.apply_power(state, state.player, "burst", 1)
    play(state, [{"op": "block", "amount": 3}])
    assert state.player.block == 6
    assert state.player.powers["burst"] == 0
    play(state, [{"op": "block", "amount": 3}])
    assert state.player.block == 9                   # no stack left


def test_burst_does_not_replay_an_attack():
    state = make_state()
    state.enemies = [make_enemy(hp=60)]
    powers.apply_power(state, state.player, "burst", 1)
    play(state, [{"op": "damage", "amount": 5, "target": "enemy"}],
         type="attack")
    assert state.enemies[0].hp == 55
    assert state.player.powers["burst"] == 1


def test_free_skill_zeroes_a_skill_and_is_spent_on_the_play():
    state = make_state()
    state.player.energy = 3
    powers.apply_power(state, state.player, "free_skill", 1)
    play(state, [], cost=2)
    assert state.player.energy == 3
    assert state.player.powers["free_skill"] == 0


def test_well_laid_plans_retains_cards_that_would_have_flushed():
    state = make_state()
    state.enemies = [make_enemy(hp=200)]
    keeper = card("keeper", type="attack", cost=1,
                  fx=[{"op": "damage", "amount": 9, "target": "enemy"}])
    junk = card("junk", cost=3)
    powers.apply_power(state, state.player, "well_laid_plans", 1)

    def pilot(s):
        if not s.player.hand:
            s.player.hand.extend([keeper, junk])
        return None

    combat._player_turn(state, pilot)
    assert keeper in state.player.hand
    assert junk in state.player.discard_pile


def test_well_laid_plans_flush_conserves_equal_twin_cards():
    """Card is a dataclass, so two copies of the same card compare EQUAL
    while being distinct instances. Retaining one copy must not make its
    twin vanish from every pile -- the flush filters by identity."""
    state = make_state()
    state.enemies = [make_enemy(hp=200)]
    twins = [card("twin", type="attack", cost=1,
                  fx=[{"op": "damage", "amount": 9, "target": "enemy"}])
             for _ in range(2)]
    junk = card("junk", cost=3)
    powers.apply_power(state, state.player, "well_laid_plans", 1)

    def pilot(s):
        if not s.player.hand:
            s.player.hand.extend(twins + [junk])
        return None

    combat._player_turn(state, pilot)
    assert len(state.player.hand) == 1
    assert len(state.player.discard_pile) == 2
    survivors = state.player.hand + state.player.discard_pile
    assert {id(c) for c in survivors} == {id(c) for c in twins + [junk]}


def test_well_laid_plans_retains_two_distinct_instances_of_a_twin():
    """With Amount 2 and a hand of equal twins, BOTH instances stay -- the
    picker must never hand the same instance out twice."""
    state = make_state()
    state.enemies = [make_enemy(hp=200)]
    twins = [card("twin", cost=1) for _ in range(2)]
    powers.apply_power(state, state.player, "well_laid_plans", 2)

    def pilot(s):
        if not s.player.hand:
            s.player.hand.extend(twins)
        return None

    combat._player_turn(state, pilot)
    assert len(state.player.hand) == 2
    assert state.player.hand[0] is not state.player.hand[1]
    assert not state.player.discard_pile


# --- per-play payouts ------------------------------------------------------

def test_serpent_form_damages_an_enemy_after_each_card_played():
    state = make_state()
    state.enemies = [make_enemy(hp=60)]
    play(state, [{"op": "apply_power", "power": "serpent_form", "amount": 4,
                  "target": "self"}], type="power")
    assert state.enemies[0].hp == 60                 # not on its own play
    play(state, [])
    assert state.enemies[0].hp == 56


def test_strangle_bleeds_the_enemy_it_sits_on_per_card_the_player_plays():
    state = make_state()
    enemy = make_enemy(hp=60)
    state.enemies = [enemy]
    enemy.block = 99
    powers.apply_power(state, enemy, "strangle", 3)
    play(state, [])
    assert enemy.hp == 57                            # Unblockable
    assert enemy.block == 99


def test_strangle_is_removed_at_the_enemy_turn_end_not_the_players():
    state = make_state()
    enemy = make_enemy(hp=60)
    state.enemies = [enemy]
    powers.apply_power(state, enemy, "strangle", 3)
    powers.on_turn_end(state, state.player)
    assert enemy.powers["strangle"] == 3
    powers.on_turn_end(state, enemy)
    assert "strangle" not in enemy.powers


def test_master_planner_marks_the_played_skill_sly_for_the_rest_of_combat():
    state = make_state()
    powers.apply_power(state, state.player, "master_planner", 1)
    skill = play(state, [])
    assert skill.sly_keyword is True
    attack = play(state, [], type="attack")
    assert attack.sly_keyword is False


def test_anticipate_applies_real_dexterity_and_gives_the_whole_lot_back():
    """TemporaryDexterityPower unapplies its MAGNITUDE at the owner's turn
    end. Decrementing by one instead would leave permanent Dexterity behind."""
    state = make_state()
    powers.apply_power(state, state.player, "temp_dexterity", 4)
    assert state.player.powers["dexterity"] == 4
    powers.on_turn_end(state, state.player)
    assert state.player.powers["dexterity"] == 0
    assert "temp_dexterity" not in state.player.powers


# --- the two that are refused ---------------------------------------------

def test_the_co_op_only_powers_are_recorded_rather_than_implemented():
    """Sneaky and Flanking cannot fire in a single-player fight at all. They
    are a THIRD category beside "on the dial" and "unimplemented", and the
    extractor reports them as such -- implementing either would produce a
    card that reads as a buff and measurably does nothing."""
    assert set(refpowers.MULTIPLAYER_ONLY_POWERS) == {"sneaky", "flanking"}
    for key, reason in refpowers.MULTIPLAYER_ONLY_POWERS.items():
        assert "Card:" in reason
        assert key not in refpowers.UNIMPLEMENTED
