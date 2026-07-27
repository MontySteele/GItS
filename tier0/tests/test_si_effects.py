"""Pins for the base-game-parity primitives the SILENT anchor needs.

Same contract as test_ic_effects.py: every test drives a mechanic the way a
card row would and asserts on the runtime quantity, and NO number extracted
from the game appears here. These run on CI, where game_ref/ does not exist --
the mechanics are ours even though the pool that motivates them is not.

The three pinned here are the sprint's P0s, in the order the first Silent
extraction's exclusion histogram put them:

  chosen discard  -- Survivor is in the STARTING DECK, so real_silent cannot
                     be built at all without it
  poison          -- the only power gating more than two cards
  dexterity       -- the block funnel the whole defensive kit leans on
"""

from tier0 import constants as C
from tier0.engine import combat, effects, powers, refpowers
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state


def card(cid="c", type="skill", cost=0, fx=None, **kw):
    return Card(id=cid, name=cid, cost=cost, type=type,
                effects=fx if fx is not None else [], **kw)


# --- C-1: chosen discard --------------------------------------------------

def test_chosen_discard_takes_the_worst_card_not_a_random_one():
    """`select: chosen` routes through the same `_worst_card` pilot surface
    `exhaust_from` already uses, so a discard-cost card is priced against a
    player who discards their worst card -- which is what a player does."""
    state = make_state()
    keep = card("keep", type="attack", cost=1,
                fx=[{"op": "damage", "amount": 9, "target": "enemy"}])
    dead = card("dead", type="skill", cost=3, fx=[])
    state.player.hand = [keep, dead]
    effects.resolve_card(state, card("survivor_like", fx=[
        {"op": "block", "amount": 8},
        {"op": "discard", "amount": 1, "select": "chosen"}]))
    assert [c.id for c in state.player.hand] == ["keep"]
    assert [c.id for c in state.player.discard_pile] == ["dead"]


def test_random_stays_the_default_for_every_card_that_already_discarded():
    """The default flip would silently re-price every existing discard card,
    so the op keeps random unless a row asks for chosen."""
    state = make_state()
    state.rng.seed(0)
    state.player.hand = [card(f"c{i}") for i in range(6)]
    effects.resolve_card(state, card("d", fx=[{"op": "discard", "amount": 1}]))
    events = [e for e in state.log if e["event"] == "discard"]
    assert events and "chosen" not in events[-1]


def test_a_chosen_discard_still_triggers_kokomis_sly():
    """Two different mechanics wear the word Sly (this one is Kokomi's Assist
    lane; the base-game keyword is a different rule the extractor excludes).
    A chosen discard is still a CARD-EFFECT discard, which is the trigger
    scope, so the lane must not quietly stop firing for it."""
    state = make_state()
    assisted = card("assisted", cost=3,
                    sly=[{"op": "block", "amount": 4}])
    state.player.hand = [assisted]
    before = state.player.block
    effects.resolve_card(state, card("d", fx=[
        {"op": "discard", "amount": 1, "select": "chosen"}]))
    assert state.player.block == before + 4
    assert any(e["event"] == "sly" for e in state.log)


def test_chosen_discard_on_an_empty_hand_discards_nothing():
    state = make_state()
    state.player.hand = []
    effects.resolve_card(state, card("d", fx=[
        {"op": "discard", "amount": 2, "select": "chosen"}]))
    assert state.player.discard_pile == []


# --- C-2: poison ----------------------------------------------------------

def test_poison_deals_its_stack_then_decrements_by_one():
    """PowerCmd.Damage(Amount) then PowerCmd.Decrement -- ONE stack per tick,
    not a full expiry and not a halving."""
    state = make_state()
    enemy = state.enemies[0]
    hp = enemy.hp
    powers.apply_power(state, enemy, "poison", 4)
    refpowers.poison_tick(state, enemy)
    assert hp - enemy.hp == 4
    assert enemy.powers["poison"] == 3
    refpowers.poison_tick(state, enemy)
    assert hp - enemy.hp == 4 + 3
    assert enemy.powers["poison"] == 2


def test_poison_bypasses_block_entirely():
    """Unblockable | Unpowered. `unpowered_damage` would let Block absorb it;
    poison is BOTH flags and the block must be untouched as well as unused."""
    state = make_state()
    enemy = state.enemies[0]
    enemy.block = 50
    hp = enemy.hp
    powers.apply_power(state, enemy, "poison", 3)
    refpowers.poison_tick(state, enemy)
    assert hp - enemy.hp == 3
    assert enemy.block == 50


def test_poison_does_not_scale_with_strength_or_vulnerable():
    """Unpowered: neither the poisoner's Strength nor the victim's
    Vulnerable touches it. Routing poison through the powered attack
    pipeline is the mistake this pins shut."""
    state = make_state()
    enemy = state.enemies[0]
    powers.apply_power(state, state.player, "strength", 5)
    powers.apply_power(state, enemy, "vulnerable", 3)
    hp = enemy.hp
    powers.apply_power(state, enemy, "poison", 3)
    refpowers.poison_tick(state, enemy)
    assert hp - enemy.hp == 3


def test_poison_applications_stack_additively():
    state = make_state()
    enemy = state.enemies[0]
    powers.apply_power(state, enemy, "poison", 2)
    powers.apply_power(state, enemy, "poison", 3)
    assert enemy.powers["poison"] == 5


def test_poison_that_kills_does_not_decrement():
    """`if (base.Owner.IsAlive) await PowerCmd.Decrement(this)` -- the
    alive-gate is in the source, so it is in the model."""
    state = make_state()
    enemy = state.enemies[0]
    enemy.hp = 2
    powers.apply_power(state, enemy, "poison", 6)
    refpowers.poison_tick(state, enemy)
    assert not enemy.alive
    assert enemy.powers["poison"] == 6


def test_poison_ticks_once_per_turn_while_accelerant_is_unimplemented():
    """TriggerCount = min(Amount, 1 + Accelerant). Accelerant is not
    implemented and its card stays excluded, so the loop runs exactly once
    -- but the min() is transcribed, not assumed away."""
    state = make_state()
    enemy = state.enemies[0]
    hp = enemy.hp
    powers.apply_power(state, enemy, "poison", 9)
    refpowers.poison_tick(state, enemy)
    assert hp - enemy.hp == 9            # one tick, not nine


def test_poison_is_not_dot_and_neither_reschedules_the_other():
    """`dot` (Electro-Charged) ticks at site A, before the draw; poison ticks
    at site F, after it. Klee and Kokomi are balanced around `dot`'s clock,
    so the parity work is forbidden from moving it -- the two coexist."""
    state = make_state()
    enemy = state.enemies[0]
    hp = enemy.hp
    powers.apply_power(state, enemy, "dot", 3)
    powers.apply_power(state, enemy, "poison", 3)
    powers.on_turn_start(state, enemy)               # site A only
    assert hp - enemy.hp == 3
    assert enemy.powers["poison"] == 3               # untouched by site A
    refpowers.enemy_side_turn_start(state, enemy)    # site F
    assert hp - enemy.hp == 3 + 3
    assert enemy.powers["dot"] == 2 and enemy.powers["poison"] == 2


def test_poison_on_an_enemy_ticks_through_a_real_fight():
    """The wiring, not just the function: an enemy carrying poison loses HP
    at its own turn start when the fight actually runs it."""
    state = make_state(enemies=[make_enemy(hp=60)])
    enemy = state.enemies[0]
    powers.apply_power(state, enemy, "poison", 5)
    hp = enemy.hp
    combat._enemy_turn(state, enemy)
    assert hp - enemy.hp == 5
    assert enemy.powers["poison"] == 4


# --- C-3: dexterity -------------------------------------------------------

def test_dexterity_adds_to_card_block():
    state = make_state()
    powers.apply_power(state, state.player, "dexterity", 3)
    effects.resolve_card(state, card("b", fx=[{"op": "block", "amount": 5}]))
    assert state.player.block == 8


def test_dexterity_does_not_touch_unpowered_power_block():
    """`props.IsPoweredCardOrMonsterMoveBlock()` gates the additive hook, and
    that is the same line tier0 already draws: refpowers.gain_block carries
    the Unpowered power-block that Frail is (correctly) not allowed to
    reduce either."""
    state = make_state()
    p = state.player
    powers.apply_power(state, p, "dexterity", 3)
    refpowers.gain_block(state, p, 5)
    assert p.block == 5


def test_dexterity_is_additive_BEFORE_frail_is_multiplicative():
    """ModifyBlockAdditive runs before ModifyBlockMultiplicative, so it is
    (base + dex) * 0.75 and not base * 0.75 + dex. The two readings agree on
    small numbers and disagree on real ones, which is exactly how an
    interaction order gets shipped wrong."""
    state = make_state()
    p = state.player
    powers.apply_power(state, p, "dexterity", 3)
    powers.apply_power(state, p, "frail", 1)
    assert powers.modify_block_gained(p, 11) == int(14 * C.FRAIL_BLOCK_MULT)
    assert powers.modify_block_gained(p, 11) != (int(11 * C.FRAIL_BLOCK_MULT)
                                                 + 3)


def test_negative_dexterity_floors_at_zero_block():
    """DexterityPower.AllowNegative is true. A negative stack must not drive
    block below zero, and must not invert Frail's multiplier by going
    negative before it."""
    state = make_state()
    p = state.player
    powers.apply_power(state, p, "dexterity", -9)
    assert powers.modify_block_gained(p, 5) == 0
    powers.apply_power(state, p, "frail", 1)
    assert powers.modify_block_gained(p, 5) == 0


def test_a_block_op_with_no_block_gains_nothing_from_dexterity():
    """The funnel's `amount <= 0` early-out predates Dexterity; a card that
    gains no block must not start gaining Dexterity's worth of it."""
    state = make_state()
    powers.apply_power(state, state.player, "dexterity", 4)
    assert powers.modify_block_gained(state.player, 0) == 0


# --- A4: the base-game Sly keyword ----------------------------------------
#
# Ruled 2026-07-27: implement it as the game has it. CardCmd.DiscardAndDraw
# collects the Sly cards while discarding the batch, then CardCmd.AutoPlay
# plays each one through the SAME CardModel.OnPlayWrapper a manual play uses
# with ResourceInfo.EnergySpent = 0. So it is a whole card play that happens
# to be free -- not an effect list that resolves, which is Kokomi's `sly` and
# a different mechanic sharing the word.

def test_a_sly_card_plays_itself_when_a_card_effect_discards_it():
    state = make_state()
    state.enemies = [make_enemy(hp=60)]
    sly = card("sly", type="attack", cost=2, sly_keyword=True,
               fx=[{"op": "damage", "amount": 7, "target": "enemy"}])
    state.player.hand = [sly]
    hp = state.enemies[0].hp
    effects.resolve_card(state, card("discarder", fx=[
        {"op": "discard", "amount": 1, "select": "chosen"}]))
    assert state.enemies[0].hp == hp - 7
    assert [c.id for c in state.player.discard_pile] == ["sly"]


def test_the_sly_play_is_free_and_does_not_touch_energy():
    """EnergySpent = 0 whatever the card's printed cost -- an auto-play the
    player cannot pay for is the entire point of the keyword."""
    state = make_state()
    state.player.energy = 1
    sly = card("sly", cost=3, sly_keyword=True, fx=[{"op": "block",
                                                     "amount": 6}])
    state.player.hand = [sly]
    effects.resolve_card(state, card("discarder", fx=[
        {"op": "discard", "amount": 1, "select": "chosen"}]))
    assert state.player.energy == 1
    assert state.player.block == 6


def test_the_sly_play_counts_as_a_card_played():
    """OnPlayWrapper fires BeforeCardPlayed and History.CardPlayStarted
    whether or not the play was automatic, so an auto-play is a play for
    every counter that reads one."""
    state = make_state()
    state.cards_played_this_turn = 0
    sly = card("sly", sly_keyword=True, fx=[{"op": "block", "amount": 3}])
    state.player.hand = [sly]
    effects.resolve_card(state, card("discarder", fx=[
        {"op": "discard", "amount": 1, "select": "chosen"}]))
    assert state.cards_played_this_turn == 1
    plays = [e for e in state.log if e["event"] == "play"]
    assert len(plays) == 1 and plays[0]["free"] is True


def test_a_sly_card_with_exhaust_exhausts_after_its_free_play():
    """Result-pile routing is OnPlayWrapper's, not the discard's: the card
    goes where its own keywords send it once the free play resolves."""
    state = make_state()
    sly = card("sly", sly_keyword=True, exhaust=True,
               fx=[{"op": "block", "amount": 2}])
    state.player.hand = [sly]
    effects.resolve_card(state, card("discarder", fx=[
        {"op": "discard", "amount": 1, "select": "chosen"}]))
    assert [c.id for c in state.player.exhaust_pile] == ["sly"]
    assert state.player.discard_pile == []


def test_the_whole_batch_is_discarded_before_any_sly_card_plays():
    """CardCmd.Discard's own docstring warns that discarding in a loop gets
    the Sly timing wrong. With two Sly cards the second is already in the
    pile while the first resolves, so a pile-reading effect sees it."""
    state = make_state()
    seen = []
    a = card("a", sly_keyword=True, fx=[{"op": "block", "amount": 1}])
    b = card("b", sly_keyword=True, fx=[{"op": "block", "amount": 1}])
    state.player.hand = [a, b]
    original = effects.OPS["block"]

    def spy(st, fx, c):
        seen.append(sorted(x.id for x in st.player.discard_pile))
        return original(st, fx, c)

    effects.OPS["block"] = spy
    try:
        effects.resolve_card(state, card("discarder", fx=[
            {"op": "discard", "amount": 2, "select": "chosen"}]))
    finally:
        effects.OPS["block"] = original
    # First auto-play already sees BOTH cards in the discard pile (its own
    # has been lifted out of it for the play, so it sees the other one).
    assert seen[0] == ["b"] and seen[1] == ["a"]


def test_the_end_of_turn_hand_flush_is_not_a_sly_trigger():
    """CombatManager.FlushPlayerHand adds the hand straight to the discard
    pile via CardPileCmd.Add; it never goes through CardCmd.Discard. A
    silent turn therefore pays nothing, matching the activity-gating law."""
    state = make_state()
    state.enemies = [make_enemy(hp=60)]
    sly = card("sly", sly_keyword=True, fx=[{"op": "block", "amount": 5}])
    state.player.hand = [sly]
    combat._player_turn(state, lambda s: None)       # play nothing, then flush
    assert sly in state.player.discard_pile
    assert state.player.block == 0
    assert state.cards_played_this_turn == 0


def test_kokomis_sly_and_the_base_game_sly_are_separate_fields():
    """One word, two mechanics, and the extractor maps the keyword onto the
    base-game one. A card carrying only the Assist-lane list must not play
    itself, and a card carrying only the keyword must not need a list."""
    state = make_state()
    assist = card("assist", sly=[{"op": "block", "amount": 4}],
                  fx=[{"op": "block", "amount": 99}])
    state.player.hand = [assist]
    effects.resolve_card(state, card("discarder", fx=[
        {"op": "discard", "amount": 1, "select": "chosen"}]))
    assert state.player.block == 4          # the list, not the card
    assert state.cards_played_this_turn == 0


def test_a_free_play_does_not_clobber_the_outer_cards_context():
    """The reason effects._free_play refuses to resolve effects inline: a
    whole card resolves mid-resolution, and the outer card must finish
    reading its OWN kills and exhausts."""
    state = make_state()
    state.enemies = [make_enemy(hp=60)]
    state.kills_this_card = 3
    state.current_card_cost = 2
    # NOT placed in hand: resolve_free_play's contract says the trigger site
    # already removed the card from its source pile.
    sly = card("sly", type="attack", cost=1, sly_keyword=True,
               fx=[{"op": "damage", "amount": 1, "target": "enemy"}])
    combat.resolve_free_play(state, sly)
    assert state.kills_this_card == 3
    assert state.current_card_cost == 2


# --- the coverage pass's runtime-count tokens ------------------------------
#
# Each is a CalculatedVar multiplier read off the DLL, and each is the whole
# reason one more of her cards can be scored instead of excluded. Driven the
# way a card row drives them, so a token that silently returns the wrong
# quantity fails here rather than in a statline nobody can explain.

def test_hit_count_from_attacks_played_this_turn():
    state = make_state()
    state.enemies = [make_enemy(hp=90)]
    state.attacks_played_this_turn = 3
    effects.resolve_card(state, card("finisher_like", type="attack", fx=[
        {"op": "damage", "amount": 6, "target": "enemy",
         "times_formula": {"base": 0, "per": 1,
                           "count": "attacks_played_this_turn"}}]))
    assert state.enemies[0].hp == 90 - 18


def test_hit_count_from_skills_in_hand_counts_only_skills():
    state = make_state()
    state.enemies = [make_enemy(hp=90)]
    state.player.hand = [card("s1"), card("s2"),
                         card("a1", type="attack"), card("p1", type="power")]
    effects.resolve_card(state, card("flechettes_like", type="attack", fx=[
        {"op": "damage", "amount": 5, "target": "enemy",
         "times_formula": {"base": 0, "per": 1,
                           "count": "skills_in_hand"}}]))
    assert state.enemies[0].hp == 90 - 10


def test_hit_count_from_x_matches_the_energy_the_card_spent():
    """Skewer's hits and an X card's damage must read the same number, or an
    X attack can pay for energy it did not convert into hits."""
    state = make_state()
    state.enemies = [make_enemy(hp=90)]
    state.current_x = 3
    effects.resolve_card(state, card("skewer_like", type="attack", cost="X",
                                     fx=[{"op": "damage", "amount": 8,
                                          "target": "enemy", "times": "X"}]))
    assert state.enemies[0].hp == 90 - 24


def test_damage_scales_with_discards_this_turn_and_resets():
    state = make_state()
    state.enemies = [make_enemy(hp=90)]
    state.player.hand = [card("junk1"), card("junk2")]
    effects.resolve_card(state, card("discarder", fx=[
        {"op": "discard", "amount": 2, "select": "chosen"}]))
    assert state.discards_this_turn == 2
    effects.resolve_card(state, card("memento_like", type="attack", fx=[
        {"op": "damage", "target": "enemy",
         "amount_formula": {"base": 9, "per": 4,
                            "count": "discards_this_turn"}}]))
    assert state.enemies[0].hp == 90 - 17
    refpowers.reset_turn_counters(state)
    assert state.discards_this_turn == 0


def test_the_end_of_turn_flush_does_not_count_as_a_discard():
    """CardDiscardedEntry comes from CardCmd.Discard; the flush reaches the
    pile through CardPileCmd.Add. Counting it would hand Memento Mori a free
    scaling term every turn."""
    state = make_state()
    state.enemies = [make_enemy(hp=200)]
    state.player.hand = [card("junk")]
    combat._player_turn(state, lambda s: None)
    assert state.discards_this_turn == 0


def test_damage_scales_with_cards_drawn_across_the_whole_combat():
    """Murder's history entry is unfiltered by turn, so this counter is NOT
    reset with the per-turn ones."""
    state = make_state()
    state.enemies = [make_enemy(hp=90)]
    state.player.draw_pile = [card(f"c{i}") for i in range(4)]
    state.draw(4)
    refpowers.reset_turn_counters(state)
    assert state.cards_drawn_this_combat == 4
    effects.resolve_card(state, card("murder_like", type="attack", fx=[
        {"op": "damage", "target": "enemy",
         "amount_formula": {"base": 1, "per": 1,
                            "count": "cards_drawn_this_combat"}}]))
    assert state.enemies[0].hp == 90 - 5


def test_block_scales_with_total_poison_on_living_enemies():
    state = make_state()
    alive = make_enemy(hp=40, name="alive")
    dead = make_enemy(hp=40, name="dead")
    state.enemies = [alive, dead]
    alive.powers["poison"] = 5
    dead.powers["poison"] = 100
    dead.hp = 0                                   # a corpse's poison is gone
    effects.resolve_card(state, card("mirage_like", fx=[
        {"op": "block", "amount_formula": {"base": 0, "per": 1,
                                           "count": "enemy_poison_total"}}]))
    assert state.player.block == 5


def test_damage_falls_with_the_rest_of_the_hand():
    """Precise Cut counts OTHER cards: the playing card has already left hand
    by resolution time, so the hand as it stands IS 'other'."""
    state = make_state()
    state.enemies = [make_enemy(hp=90)]
    state.player.hand = [card("h1"), card("h2")]
    effects.resolve_card(state, card("precise_like", type="attack", fx=[
        {"op": "damage", "target": "enemy",
         "amount_formula": {"base": 13, "per": -2,
                            "count": "other_cards_in_hand"}}]))
    assert state.enemies[0].hp == 90 - 9


def test_a_negative_formula_result_deals_no_damage_rather_than_healing():
    state = make_state()
    state.enemies = [make_enemy(hp=90)]
    state.player.hand = [card(f"h{i}") for i in range(9)]
    effects.resolve_card(state, card("precise_like", type="attack", fx=[
        {"op": "damage", "target": "enemy",
         "amount_formula": {"base": 13, "per": -2,
                            "count": "other_cards_in_hand"}}]))
    assert state.enemies[0].hp == 90
