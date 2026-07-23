"""Pins for the base-game Ironclad powers (tier0/engine/refpowers.py).

The recon spec ranked ten timing traps by how badly each would bias the
Klee-vs-Ironclad comparison. Every one of them has a test here, named after
the trap, because "the power exists" is not the property that matters -- the
property that matters is that it fires at the right site.

No number extracted from the game appears in this file: stacks are chosen for
readability and the tests assert on RELATIONSHIPS (doubled, halved, reverted,
deferred), never on a card's printed value.
"""

import pytest

from tier0 import constants as C
from tier0.engine import combat, effects, powers, refpowers
from tier0.engine.combat import run_fight
from tier0.engine.state import Card, Player
from tier0.tests.conftest import make_enemy, make_state


# --- helpers ---------------------------------------------------------------

def card(cid="c", type="attack", cost=0, fx=None, **kw):
    return Card(id=cid, name=cid, cost=cost, type=type,
                effects=fx if fx is not None else [], **kw)


def bound_state(**kw):
    state = make_state(**kw)
    refpowers.bind(state)
    return state


@pytest.fixture(autouse=True)
def _unbind():
    yield
    refpowers.bind(None)


# --- Group A: trivial in tier0 --------------------------------------------

def test_pyre_raises_the_turn_refill_and_does_not_compound():
    # ModifyMaxEnergy => amount + Amount. It is a reset TO max, so two turns
    # of Pyre do not accumulate.
    state = bound_state()
    state.player.powers["pyre"] = 2
    assert refpowers.energy_for_turn(state) == C.BASE_ENERGY_PER_TURN + 2
    state.player.energy = 99
    assert refpowers.energy_for_turn(state) == C.BASE_ENERGY_PER_TURN + 2


def test_barricade_suppresses_the_turn_start_block_clear():
    p = Player(hp=50, max_hp=50)
    assert refpowers.should_clear_block(p) is True
    p.powers["barricade"] = 1
    assert refpowers.should_clear_block(p) is False


def test_demon_form_grants_strength_after_the_draw_not_before():
    # Site F (AfterSideTurnStart). Pinned via the late hook itself: running
    # it at tier0's pre-draw powers.on_turn_start would be wrong-by-
    # construction even though Strength happens not to read the hand.
    state = bound_state()
    state.player.powers["demon_form"] = 2
    refpowers.player_turn_start_late(state)
    assert state.player.powers["strength"] == 2
    refpowers.player_turn_start_late(state)
    assert state.player.powers["strength"] == 4      # permanent, additive


def test_colossus_halves_only_when_the_dealer_is_vulnerable():
    state = bound_state()
    p, e = state.player, state.enemies[0]
    p.powers["colossus"] = 1
    assert powers.modify_damage_taken(p, 10, e) == 10     # dealer not vuln
    e.powers["vulnerable"] = 1
    assert powers.modify_damage_taken(p, 10, e) == 5


def test_colossus_decrements_on_the_enemy_side_turn_end():
    # `if (side == CombatSide.Enemy) Decrement` -- stacks are turns of
    # protection remaining, not magnitude.
    state = bound_state()
    state.player.powers["colossus"] = 2
    powers.on_turn_end(state, state.player)               # player turn end
    assert state.player.powers["colossus"] == 2           # untouched
    refpowers.after_enemy_side_turn_end(state)
    assert state.player.powers["colossus"] == 1


def test_cruelty_adds_percentage_points_to_vulnerable_only():
    state = bound_state()
    p, e = state.player, state.enemies[0]
    p.powers["cruelty"] = 25
    assert powers.modify_damage_taken(e, 100, p) == 100   # target not vuln
    e.powers["vulnerable"] = 1
    # 1.50 base + 0.25 from Cruelty, not 1.50 * something.
    assert powers.modify_damage_taken(e, 100, p) == pytest.approx(175.0)


def test_cruelty_reaches_the_effects_damage_pipeline_without_an_attacker_arg():
    # effects.deal_damage_to_enemy calls modify_damage_taken with two
    # arguments; refpowers recovers the dealer from the bound state. Without
    # that recovery Cruelty would be unreachable from any real card.
    state = bound_state()
    p, e = state.player, state.enemies[0]
    e.powers["vulnerable"] = 1
    p.powers["cruelty"] = 100                             # +100 points => x2.5
    effects.deal_damage_to_enemy(state, e, 10)
    assert e.hp == e.max_hp - 25


def test_setup_strike_restores_the_magnitude_not_a_single_stack():
    # TemporaryStrengthPower applies +-Amount Strength and reverts the SAME
    # magnitude at its owner's turn end. A decaying stack would leak +2.
    state = bound_state()
    p = state.player
    p.powers["strength"] = 1
    powers.apply_power(state, p, "temp_strength", 3)
    assert p.powers["strength"] == 4
    powers.on_turn_end(state, p)
    assert p.powers["strength"] == 1
    assert "temp_strength" not in p.powers


def test_mangle_debuffs_exactly_one_enemy_action():
    # Applied to an ENEMY during the player's turn; reverts at that enemy's
    # own turn end, which tier0 reaches in combat._enemy_turn.
    state = bound_state()
    e = state.enemies[0]
    e.powers["strength"] = 5
    powers.apply_power(state, e, "temp_strength_down", 3)
    assert e.powers["strength"] == 2
    powers.on_turn_end(state, e)
    assert e.powers["strength"] == 5


def test_mangle_cannot_drive_an_intent_below_zero_damage():
    # Hooks.Hook.ModifyDamage ends `return Math.Max(0m, num)`, so the clamp
    # happens before the number reaches the creature. Unclamped, tier0's
    # `blocked = min(block, dmg); block -= blocked` turns a -4 into FOUR BLOCK
    # GAINED from being attacked -- and Mangle's StrengthLoss dwarfs a typical
    # tier0 intent, so it is the practical source of negative damage.
    state = bound_state(enemies=[make_enemy(
        intents=[{"kind": "attack", "amount": 6}])])
    p, e = state.player, state.enemies[0]
    p.block = 5
    hp0 = p.hp
    powers.apply_power(state, e, "temp_strength_down", 10)
    combat._enemy_turn(state, e)
    assert p.hp == hp0
    assert p.block == 5                      # NOT 9


def test_no_draw_denies_draws_but_not_the_turn_start_hand_draw():
    state = bound_state()
    p = state.player
    p.draw_pile = [card(f"d{i}") for i in range(6)]
    p.powers["no_draw"] = 1
    state.draw(2)
    assert p.hand == []
    state.draw(2, from_hand_draw=True)            # ShouldDraw => fromHandDraw
    assert len(p.hand) == 2


def test_no_draw_is_removed_whole_at_the_owners_turn_end():
    state = bound_state()
    state.player.powers["no_draw"] = 3
    powers.on_turn_end(state, state.player)
    assert "no_draw" not in state.player.powers   # Remove, not Decrement


# --- Trap 3: NoEnergyGain must NOT be a turn-skipper ------------------------

def test_no_energy_gain_leaves_the_turn_refill_alone():
    # ResetEnergy() never calls PlayerCmd.GainEnergy, so ModifyEnergyGain
    # never sees it. Implemented at the refill, ExpectAFight would become a
    # hard turn-skipper and the card's rating would invert.
    state = bound_state()
    state.player.powers["no_energy_gain"] = 1
    assert refpowers.energy_for_turn(state) == C.BASE_ENERGY_PER_TURN


def test_no_energy_gain_keeps_its_own_gain_and_denies_the_next():
    state = bound_state()
    p = state.player
    p.energy = 3
    gainer = card("gain", type="skill", fx=[{"op": "energy", "amount": 2}])
    p.hand = [gainer]
    # The power lands mid-card, after the card's own gain: ceiling is seeded
    # at that moment, so ExpectAFight's own energy survives.
    p.energy = 5
    powers.apply_power(state, p, "no_energy_gain", 1)
    assert p.energy == 5
    combat.play_card(state, gainer)
    assert p.energy == 5                          # the later gain is denied
    assert any(e["event"] == "energy_gain_denied" for e in state.log)


def test_second_no_energy_gain_card_gains_nothing():
    # PowerStackType.Single: the re-Apply is a no-op and the LIVE power's
    # ModifyEnergyGain still returns 0, so ExpectAFight #2 banks nothing.
    # Reseeding the ceiling on re-application laundered that gain, because
    # tier0 resolves the `energy` op before the `apply_power` op.
    state = bound_state()
    p = state.player
    p.energy = 3
    fx = [{"op": "energy", "amount": 3},
          {"op": "apply_power", "power": "no_energy_gain", "amount": 1,
           "target": "self"}]
    for _ in range(2):
        c = card("eaf", type="skill", cost=2, fx=fx)
        p.hand = [c]
        combat.play_card(state, c)
    assert p.energy == 2                     # 3 -2 +3 -2 +0
    assert any(e["event"] == "energy_gain_denied" for e in state.log)


# --- FreeAttack / Corruption ------------------------------------------------

def test_free_attack_zeroes_attacks_and_decrements_per_play_index():
    state = bound_state()
    p = state.player
    p.energy = 0
    p.powers["free_attack"] = 2
    atk = card("atk", cost=2)
    p.hand = [atk]
    assert combat.card_cost(state, atk) == 0
    assert combat.card_playable(state, atk)
    combat.play_card(state, atk)
    assert p.powers["free_attack"] == 1
    # Persists across turns: no turn-end removal, unlike almost everything else.
    powers.on_turn_end(state, p)
    assert p.powers["free_attack"] == 1


def test_free_attack_and_spark_are_both_consumed():
    # FreeAttackPower.BeforeCardPlayed decrements on ANY owner Attack play --
    # it does not check whether its discount was the one that mattered. So a
    # spark-freed attack burns the spark bank (tier0's native branch runs
    # first in card_cost) AND a FreeAttack stack. Pinning the double spend is
    # the point; either answer is defensible, silence is not.
    state = bound_state()
    p = state.player
    p.sparks = combat.spark_threshold(state)
    p.powers["free_attack"] = 1
    atk = card("atk", cost=2)
    p.hand = [atk]
    combat.play_card(state, atk)
    assert p.sparks == 0
    assert p.powers["free_attack"] == 0


def test_free_attack_does_not_zero_an_x_cost_attack():
    # Both Unrelenting (the only FreeAttack grantor) and Whirlwind (the only
    # X-cost attack) are now in the emitted pool, so this interaction is live
    # and must be pinned rather than left implicit.
    #
    # The power's own hook sets modifiedCost = 0 for ANY owner Attack, but an
    # X card never reaches it: CardEnergyCost.GetAmountToSpend() returns the
    # owner's whole energy under `if (CostsX)` before touching
    # GetWithModifiers, and GetWithModifiers returns under its own
    # `if (CostsX)` before its Hook.ModifyEnergyCostInCombat call. X stays
    # full-price, and the stack is still spent because BeforeCardPlayed never
    # asks whether the discount applied.
    state = bound_state()
    p = state.player
    p.energy = 3
    p.powers["free_attack"] = 1
    atk = card("wind", cost="X")
    p.hand = [atk]
    assert combat.card_cost(state, atk) == 3
    combat.play_card(state, atk)
    assert state.current_x == 3          # X = energy actually spent, not 0
    assert p.energy == 0
    assert p.powers["free_attack"] == 0


def test_corruption_zeroes_skills_and_exhausts_them():
    state = bound_state()
    p = state.player
    p.powers["corruption"] = 1
    skill = card("sk", type="skill", cost=2)
    p.hand = [skill]
    assert combat.card_cost(state, skill) == 0
    combat.play_card(state, skill)
    assert skill in p.exhaust_pile and skill not in p.discard_pile


# --- Trap 1: Power cards must not reach the exhaust pile --------------------

def test_played_power_card_is_removed_from_combat_not_exhausted():
    # GetResultPileTypeForCardPlay: Type == Power => PileType.None. Ironclad
    # has 11 Power cards; exhausting them would have paid out FeelNoPain and
    # DarkEmbrace eleven times a deck.
    state = bound_state()
    p = state.player
    p.powers["feel_no_pain"] = 5
    pw = card("pw", type="power")
    p.hand = [pw]
    combat.play_card(state, pw)
    assert pw not in p.exhaust_pile
    assert pw not in p.discard_pile
    assert p.block == 0                     # FeelNoPain did not fire


# --- FeelNoPain / DarkEmbrace ----------------------------------------------

def test_feel_no_pain_blocks_on_every_exhaust():
    state = bound_state()
    p = state.player
    p.powers["feel_no_pain"] = 4
    refpowers.exhaust_card(state, card("x"))
    assert p.block == 4
    refpowers.exhaust_card(state, card("y"))
    assert p.block == 8


def test_feel_no_pain_sees_exhausts_caused_during_a_card_play():
    # effects._op_exhaust_from lives in a file this pass may not edit; the
    # per-card-play exhaust funnel covers it anyway, and is exact.
    state = bound_state()
    p = state.player
    p.powers["feel_no_pain"] = 3
    victim = card("victim", type="skill")
    burner = card("burner", type="skill",
                  fx=[{"op": "exhaust_from", "amount": 1}])
    p.hand = [victim, burner]
    combat.play_card(state, burner)
    assert victim in p.exhaust_pile
    assert p.block == 3


def test_feel_no_pain_block_is_unpowered_and_escapes_the_card_block_funnel():
    # The exhaust sweep runs before the card-block delta, so FeelNoPain's
    # gain_block used to land INSIDE `p.block - snap["block"]` and be
    # re-processed as card block. UnmovablePower returns 1m when
    # `!props.IsCardOrMonsterMove()`, so Unpowered block is never doubled --
    # and a card that gained no block of its own must not spend an allowance
    # slot (the game's filter is `e.Props.IsCardOrMonsterMove()`).
    state = bound_state()
    p = state.player
    p.powers["feel_no_pain"] = 3
    p.powers["unmovable"] = 1
    victim = card("victim", type="skill")
    burner = card("burner", type="skill",
                  fx=[{"op": "exhaust_from", "amount": 1}])
    p.hand = [victim, burner]
    combat.play_card(state, burner)
    assert p.block == 3                              # not 6
    assert state.block_gain_card_plays_this_turn == 0


def test_feel_no_pain_pays_juggernaut_exactly_once():
    # gain_block already fired AfterBlockGained; the delta path fired it a
    # second time for the same single BlockGainedEntry, and the phantom
    # trigger was invisible in the log (only one "block" event was emitted).
    state = bound_state()
    p, e = state.player, state.enemies[0]
    p.powers["feel_no_pain"] = 3
    p.powers["juggernaut"] = 5
    victim = card("victim", type="skill")
    burner = card("burner", type="skill",
                  fx=[{"op": "exhaust_from", "amount": 1}])
    p.hand = [victim, burner]
    combat.play_card(state, burner)
    assert e.hp == e.max_hp - 5                      # not 10


def test_a_cards_own_block_still_reaches_the_funnel_alongside_an_exhaust():
    # The baseline adjustment must subtract only the SWEPT block: a card that
    # both exhausts and blocks still gets its own block doubled and still
    # pays Juggernaut for it.
    state = bound_state()
    p, e = state.player, state.enemies[0]
    p.powers["feel_no_pain"] = 3
    p.powers["unmovable"] = 1
    p.powers["juggernaut"] = 5
    victim = card("victim", type="skill")
    both = card("both", type="skill",
                fx=[{"op": "exhaust_from", "amount": 1},
                    {"op": "block", "amount": 4}])
    p.hand = [victim, both]
    combat.play_card(state, both)
    assert p.block == 3 + 4 * 2                      # only the card block doubles
    assert e.hp == e.max_hp - 10                     # one Juggernaut per gain
    assert state.block_gain_card_plays_this_turn == 1


def test_dark_embrace_draws_now_on_a_normal_exhaust():
    state = bound_state()
    p = state.player
    p.powers["dark_embrace"] = 1
    p.draw_pile = [card("d0"), card("d1")]
    refpowers.exhaust_card(state, card("x"))
    assert len(p.hand) == 1


# --- Trap 4: DarkEmbrace's ethereal draw is deferred past the hand flush ----

def test_dark_embrace_defers_ethereal_exhausts_until_after_the_hand_flush():
    state = bound_state()
    p = state.player
    p.powers["dark_embrace"] = 1
    p.draw_pile = [card("d0"), card("d1")]
    refpowers.exhaust_card(state, card("eth"), caused_by_ethereal=True)
    assert p.hand == []                          # NOT drawn at exhaust time
    assert state.dark_embrace_ethereal_count == 1
    powers.on_turn_end(state, p)                 # site M, past the hand flush
    assert len(p.hand) == 1
    assert state.dark_embrace_ethereal_count == 0


def test_dark_embrace_ethereal_draw_lands_after_the_real_hand_flush():
    # The site ordering, end to end: combat._player_turn exhausts ethereals,
    # flushes the hand, and only then calls powers.on_turn_end. A card drawn
    # by the deferred flush must survive into the next turn rather than being
    # discarded on the line after it was drawn.
    p = Player(hp=200, max_hp=200, powers={"dark_embrace": 1},
               draw_pile=[card("d0"), card("d1"), card("d2")],
               hand=[card("eth", type="skill", tags=["ethereal"])])
    state = run_fight(p, [make_enemy(hp=1, intents=[{"kind": "block",
                                                     "amount": 0}])],
                      lambda s: None, seed=0)
    drawn = [e for e in state.log if e["event"] == "extra_draw"]
    assert drawn, "the deferred ethereal draw never fired"
    assert any(c.id == "eth" for c in state.player.exhaust_pile)


# --- Juggernaut / Unmovable / Rage -----------------------------------------

def test_juggernaut_fires_on_every_block_gain_and_ignores_strength():
    # ValueProp.Unpowered: routing this through the powered attack pipeline
    # would scale it with Strength, which on a DemonForm turn is badly wrong.
    state = bound_state()
    p, e = state.player, state.enemies[0]
    p.powers["juggernaut"] = 5
    p.powers["strength"] = 10
    refpowers.gain_block(state, p, 3)
    assert e.hp == e.max_hp - 5


def test_juggernaut_ignores_target_vulnerable():
    state = bound_state()
    p, e = state.player, state.enemies[0]
    p.powers["juggernaut"] = 4
    e.powers["vulnerable"] = 2
    refpowers.gain_block(state, p, 1)
    assert e.hp == e.max_hp - 4


def test_unmovable_doubles_only_card_block_and_only_n_plays_per_turn():
    state = bound_state()
    p = state.player
    p.powers["unmovable"] = 1
    blocker = card("blk", type="skill", fx=[{"op": "block", "amount": 5}])
    p.hand = [blocker]
    combat.play_card(state, blocker)
    assert p.block == 10                     # first card play this turn
    p.hand = [blocker]
    combat.play_card(state, blocker)
    assert p.block == 15                     # allowance spent


def test_unmovable_does_not_double_passive_block():
    # ModifyBlockMultiplicative requires props.IsCardOrMonsterMove(); Plating,
    # Rage, FeelNoPain and CrimsonMantle are all Unpowered passives.
    state = bound_state()
    p = state.player
    p.powers["unmovable"] = 3
    p.powers["plating"] = 6
    refpowers.before_side_turn_end_early(state)
    assert p.block == 6


def test_rage_pays_per_attack_and_is_removed_at_turn_end():
    state = bound_state()
    p = state.player
    p.powers["rage"] = 3
    atk = card("atk")
    p.hand = [atk]
    combat.play_card(state, atk)
    assert p.block == 3
    p.hand = [card("sk", type="skill")]
    combat.play_card(state, p.hand[0])
    assert p.block == 3                      # skills do not pay
    powers.on_turn_end(state, p)
    assert "rage" not in p.powers            # Remove, not Decrement


# --- Vicious ---------------------------------------------------------------

def test_vicious_draws_per_creature_the_player_vulnerables():
    state = bound_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
    state.in_player_turn = True
    p = state.player
    p.powers["vicious"] = 1
    p.draw_pile = [card(f"d{i}") for i in range(4)]
    for e in state.enemies:
        powers.apply_power(state, e, "vulnerable", 2)
    assert len(p.hand) == 2                  # once per target, not once total


def test_vicious_does_not_draw_off_an_enemy_applied_vulnerable():
    state = bound_state()
    p = state.player
    p.powers["vicious"] = 2
    p.draw_pile = [card(f"d{i}") for i in range(4)]
    state.in_player_turn = False
    powers.apply_power(state, p, "vulnerable", 2, applier=state.enemies[0])
    assert p.hand == []


# --- CrimsonMantle / Inferno / Rupture -------------------------------------

def test_crimson_mantle_takes_self_damage_then_blocks():
    state = bound_state()
    p = state.player
    p.powers["crimson_mantle"] = 6
    p.powers["crimson_mantle_self_damage"] = 2      # two copies played
    p.block = 50                                     # Unblockable: ignored
    hp0 = p.hp
    refpowers.player_turn_start_late(state)
    assert p.hp == hp0 - 2
    assert p.block == 56


def test_crimson_mantle_counts_self_damage_per_play_not_per_stack():
    # `PowerCmd.Apply<CrimsonMantlePower>(Amount)?.IncrementSelfDamage()`:
    # SelfDamage starts at 0 and rises by ONE PER PLAY, never by Amount. With
    # no driver at all the card read as permanent block with zero drawback.
    state = bound_state()
    p = state.player
    mantle = card("mantle", type="power",
                  fx=[{"op": "apply_power", "power": "crimson_mantle",
                       "amount": 4, "target": "self"}])
    for _ in range(2):
        p.hand = [mantle]
        combat.play_card(state, mantle)
    assert p.powers["crimson_mantle"] == 8
    assert p.powers["crimson_mantle_self_damage"] == 2      # not 8
    hp0 = p.hp
    refpowers.player_turn_start_late(state)
    assert p.hp == hp0 - 2
    assert p.block == 8


def test_inferno_counts_self_damage_per_play_and_starts_its_own_engine():
    # The turn-start self-hit is what feeds the AfterDamageReceived AoE, so a
    # counter stuck at 0 left Inferno a purely reactive power in every run.
    state = bound_state()
    state.in_player_turn = True
    p, e = state.player, state.enemies[0]
    inferno = card("inferno", type="power",
                   fx=[{"op": "apply_power", "power": "inferno",
                        "amount": 3, "target": "self"}])
    for _ in range(2):
        p.hand = [inferno]
        combat.play_card(state, inferno)
    assert p.powers["inferno_self_damage"] == 2             # not 6
    hp0, ehp0 = p.hp, e.hp
    refpowers.player_turn_start_late(state)
    assert p.hp == hp0 - 2                                  # (a) self-damage
    assert e.hp == ehp0 - p.powers["inferno"]               # (b) retaliation


def test_inferno_self_damage_feeds_its_own_retaliation():
    # (a) AfterPlayerTurnStart self-damage, (b) AfterDamageReceived AoE.
    # (a) feeding (b) is the intended engine, not an accident.
    state = bound_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
    state.in_player_turn = True
    p = state.player
    p.powers["inferno"] = 3
    p.powers["inferno_self_damage"] = 1
    refpowers.player_turn_start_late(state)
    assert p.hp == p.max_hp - 1
    for e in state.enemies:
        assert e.hp == e.max_hp - 3


# --- Trap 2: the CurrentSide check on Inferno and Rupture -------------------

def test_inferno_and_rupture_never_trigger_on_the_enemy_turn():
    # Without the side check Rupture stops being a self-damage payoff and
    # silently becomes a passive tank power, and Inferno becomes a defensive
    # scaling engine. Both would be a large, invisible bias.
    state = bound_state()
    p, e = state.player, state.enemies[0]
    p.powers["inferno"] = 5
    p.powers["rupture"] = 2
    state.in_player_turn = False
    refpowers.on_damage_received(state, p, unblocked=7, dealer=e,
                                 powered_attack=True)
    assert e.hp == e.max_hp                  # Inferno silent
    assert "strength" not in p.powers        # Rupture silent


# --- Trap 5: Rupture's mid-card deferral ------------------------------------

def test_rupture_strength_lands_after_the_card_finishes():
    # Applied immediately, the strength would buff the remaining hits of the
    # very card whose self-damage granted it.
    state = bound_state()
    state.in_player_turn = True
    p = state.player
    p.powers["rupture"] = 2
    hurt = card("hurt", type="attack",
                fx=[{"op": "damage", "target": "self", "amount": 3},
                    {"op": "damage", "amount": 5}])
    p.hand = [hurt]
    e = state.enemies[0]
    combat.play_card(state, hurt)
    assert e.hp == e.max_hp - 5              # the hit saw strength 0
    assert p.powers["strength"] == 2         # granted once the card finished
    assert state.rupture_pending == 0


# --- Trap 6: FlameBarrier's removal site ------------------------------------

def test_flame_barrier_retaliates_per_hit_and_survives_the_player_turn_end():
    state = bound_state()
    p, e = state.player, state.enemies[0]
    p.powers["flame_barrier"] = 4
    state.in_player_turn = False
    for _ in range(2):                       # a two-hit intent
        refpowers.on_damage_received(state, p, unblocked=3, dealer=e,
                                     powered_attack=True)
    assert e.hp == e.max_hp - 8
    powers.on_turn_end(state, p)             # the PLAYER's turn end
    assert p.powers["flame_barrier"] == 4    # must still be here
    refpowers.after_enemy_side_turn_end(state)
    assert "flame_barrier" not in p.powers


def test_flame_barrier_burns_a_fully_blocked_hit():
    # FlameBarrierPower ignores the DamageResult entirely (`DamageResult _`).
    state = bound_state()
    p, e = state.player, state.enemies[0]
    p.powers["flame_barrier"] = 4
    state.in_player_turn = False
    refpowers.on_damage_received(state, p, unblocked=0, dealer=e,
                                 powered_attack=True)
    assert e.hp == e.max_hp - 4


# --- OneTwoPunch ------------------------------------------------------------

def test_one_two_punch_doubles_n_attacks_not_one_attack_n_times():
    # Amount stacks => Amount future attacks each played twice.
    state = bound_state()
    p, e = state.player, state.enemies[0]
    p.powers["one_two_punch"] = 2
    atk = card("atk", fx=[{"op": "damage", "amount": 4}])
    p.hand = [atk]
    combat.play_card(state, atk)
    assert e.hp == e.max_hp - 8
    assert p.powers["one_two_punch"] == 1
    powers.on_turn_end(state, p)
    assert "one_two_punch" not in p.powers   # Remove at turn end


def test_one_two_punch_pays_rage_twice():
    # Before/AfterCardPlayed fire per play INDEX (trap 10).
    state = bound_state()
    p = state.player
    p.powers["one_two_punch"] = 1
    p.powers["rage"] = 2
    atk = card("atk")
    p.hand = [atk]
    combat.play_card(state, atk)
    assert p.block == 4


# --- Trap 8: Plating's turn-1 decrement exemption ---------------------------

def test_plating_blocks_at_turn_end_and_skips_the_turn_one_decrement():
    state = bound_state()
    p = state.player
    p.powers["plating"] = 3
    state.turn = 1
    refpowers.player_turn_start_late(state)
    assert p.powers["plating"] == 3          # exempt on the first turn
    refpowers.before_side_turn_end_early(state)
    assert p.block == 3
    state.turn = 2
    refpowers.player_turn_start_late(state)
    assert p.powers["plating"] == 2
    p.block = 0
    refpowers.before_side_turn_end_early(state)
    assert p.block == 2


# --- Juggling ---------------------------------------------------------------

def test_juggling_fires_on_exactly_the_third_attack():
    state = bound_state()
    p = state.player
    p.powers["juggling"] = 1
    for i in range(5):
        atk = card("atk")
        p.hand = [atk]
        combat.play_card(state, atk)
        clones = [e for e in state.log if e["event"] == "juggling_clone"]
        assert len(clones) == (0 if i < 2 else 1)   # ==3, never % 3 == 0


def test_juggling_clone_redirects_to_discard_instead_of_vanishing():
    # CardPileCmd's `isFullHandAdd` check REDIRECTS to the discard pile rather
    # than dropping the card, so the clone stays in the deck and is drawable
    # next turn. tier0 used to `break` and destroy it.
    state = bound_state()
    p = state.player
    p.powers["juggling"] = 1
    for i in range(3):
        atk = card("atk")
        # Fill the hand so the third attack's clone has nowhere to land.
        p.hand = [atk] + [card(f"filler{i}{j}") for j in range(C.MAX_HAND_SIZE)]
        combat.play_card(state, atk)
    assert [c.id for c in p.discard_pile].count("atk") == 4   # 3 played + clone
    clones = [e for e in state.log if e["event"] == "juggling_clone"]
    assert len(clones) == 1 and clones[0]["zone"] == "discard"


# --- Trap 7: Aggression runs before the draw --------------------------------

def test_aggression_pulls_from_discard_at_site_a_before_the_draw():
    state = bound_state()
    p = state.player
    p.powers["aggression"] = 2
    p.discard_pile = [card("a1"), card("a2"), card("s1", type="skill")]
    refpowers.side_turn_start_early(state)
    assert len(p.hand) == 2
    assert all(c.type == "attack" for c in p.hand)
    assert len(p.discard_pile) == 1          # only the skill is left


def test_aggression_logs_unimplemented_rather_than_handing_over_unupgraded():
    # No `+` entry exists for a synthetic id. The move half is real; the
    # upgrade half must be VISIBLE, not silently skipped.
    state = bound_state()
    p = state.player
    p.powers["aggression"] = 1
    p.discard_pile = [card("no_such_upgrade")]
    refpowers.side_turn_start_early(state)
    assert len(p.hand) == 1
    assert any(e["event"] == "UNIMPLEMENTED" and e.get("power") == "aggression"
               for e in state.log)


# --- Group C: refused -------------------------------------------------------

def test_stampede_and_hellraiser_are_refused_loudly():
    assert set(refpowers.UNIMPLEMENTED) == {"stampede", "hellraiser"}
    state = bound_state()
    for name in refpowers.UNIMPLEMENTED:
        refpowers.refuse(state, name)
    logged = [e for e in state.log if e["event"] == "UNIMPLEMENTED"]
    assert {e["power"] for e in logged} == {"stampede", "hellraiser"}
    assert all(e["reason"] for e in logged)


def test_multiplayer_only_cards_are_named_for_exclusion():
    # CardMultiplayerConstraint.MultiplayerOnly -- these two must be dropped
    # from the 87-card pool, which also deletes TankPower from the work list.
    assert refpowers.MULTIPLAYER_ONLY_CARDS == ("Tank", "DemonicShield")


# --- Regression: the impoverished world is unchanged for everyone else ------

def test_no_ironclad_power_is_reachable_from_an_empty_power_set():
    # Every hook must be a no-op for a fighter carrying none of these powers.
    # This is the Klee/Furina bit-identity guarantee stated structurally.
    state = bound_state()
    p = state.player
    before = (p.hp, p.block, p.energy, dict(p.powers), len(p.hand))
    refpowers.side_turn_start_early(state)
    refpowers.player_turn_start_late(state)
    refpowers.before_side_turn_end_early(state)
    refpowers.after_enemy_side_turn_end(state)
    powers.on_turn_end(state, p)
    assert (p.hp, p.block, p.energy, dict(p.powers), len(p.hand)) == before
    assert state.enemies[0].hp == state.enemies[0].max_hp
