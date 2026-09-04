"""THE BOMB, rule by rule (QUARANTINED, `C.KLEE_OVERHAUL`) -- `EB-312`.

`tier0/engine/klee_overhaul.py` is the sim twin of
`klee-mod/KleeCode/Powers/Prototype/ProtoBombPower.cs` and its neighbours, and
this file is that twin checked AGAINST THE C# READING rather than against
itself: it mirrors `klee-mod/KleeTests/Prototype/KleeOverhaulRuleTests.cs` case
by case, and every test names the sentence in the mod it is pinning.

WHAT IS DIFFERENT FROM THE C# PINS, and it is the same difference twice. The
headless C# harness cannot reach `PowerCmd`, `ElementalHit.Deal` or a card
PLAY, so half of `KleeOverhaulRuleTests` is a STRUCTURAL pin read off the
compiled method (does `BeforeSideTurnStart` call `GrowBy` and nothing that
deals damage?). tier 0 has no such boundary: every one of those becomes a real
call on a real board here, which is the point of having a twin at all. The
cases that are structural on the C# side say so in their own docstring.

`tier0/tests/test_klee_overhaul.py` keeps the OTHER half -- that the flag ships
OFF, that OFF is byte-identical, and that the ops refuse off the arm. This file
is what happens with it on.

NOTHING MEASURED HERE IS QUOTABLE ANYWHERE (R215 B). These are shape assertions
about an engine, not numbers about a game.
"""

import collections

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, klee_overhaul
from tier0.engine.combat import run_fight
from tier0.engine.state import Card, KleeCharge
from tier0.pilot.policy import make_pilot
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards

ATTACKER = [{"kind": "attack", "amount": 5}]
BLOCKER = [{"kind": "block", "amount": 5}]


@pytest.fixture
def overhaul(monkeypatch):
    """The flag on, with both id-resolving caches cleared on the way in and
    out -- `test_klee_overhaul.overhaul`'s fixture, for its reasons."""
    loader._card_prototype.cache_clear()
    rewards.character_pool.cache_clear()
    monkeypatch.setattr(C, "KLEE_OVERHAUL", True)
    yield
    loader._card_prototype.cache_clear()
    rewards.character_pool.cache_clear()


def klee_state(enemies=None, hp=62):
    """A Klee seat. `live()` reads the flag AND the character, so both halves
    have to be true for anything in the arm to run."""
    st = make_state(enemies=enemies, hp=hp)
    st.player.character_id = "klee"
    st.player.element = "pyro"
    st.player.cadence = "catalyst"
    st.player.relic_hooks.append(klee_overhaul.SPARK_RELIC_HOOK)
    st.in_player_turn = True
    return st


def probe(effects_, cid="proto_ko_probe", ctype="attack", cost=0):
    """A probe row. `proto_ko_`-prefixed so it reads as what it is; nothing in
    this file loads it through the sheet."""
    return Card(id=cid, name="probe", cost=cost, type=ctype,
                effects=list(effects_))


def load(cid):
    return loader.get_card(cid)


def counts(state):
    return collections.Counter(e["event"] for e in state.log)


def sizes(enemy):
    return [c.size for c in enemy.ko_charges]


# ---------------------------------------------------------------------------
# THE FLAG, OFF -- `The_arm_ships_off`
# ---------------------------------------------------------------------------

def test_the_arm_ships_off_and_the_gate_reads_the_character_too():
    """`The_arm_ships_off`, plus the half the C# spells at each seam instead of
    in one place: `KleeOverhaul.Enabled` is the build switch and every site
    that reads it also asks `player.Character is IKleeCharacter`. `live()` is
    those two clauses in one function, so a co-op Furina never grows Bombs."""
    assert C.KLEE_OVERHAUL is False
    assert klee_overhaul.live(klee_state()) is False


def test_the_gate_needs_both_clauses(overhaul):
    assert klee_overhaul.live(klee_state()) is True
    other = klee_state()
    other.player.character_id = "furina"
    assert klee_overhaul.live(other) is False


def test_the_shipped_bomb_is_not_touched_by_the_arm(overhaul):
    """`The_shipped_bomb_is_not_edited_by_this_arm`, from this side: the arm
    keeps its charges on a SECOND field, so nothing it does can reach
    `Enemy.bombs` -- the list the shipped start-of-turn detonation empties."""
    enemy = make_enemy()
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 8)
    assert enemy.bombs == []
    assert sizes(enemy) == [8]


# ---------------------------------------------------------------------------
# RULE 5's OTHER HALF -- whose Attacks apply Pyro, and whose do not
# ---------------------------------------------------------------------------

def test_the_base_games_strike_applies_nothing_and_hers_still_do(overhaul):
    """[USER], 2026-09-02: "I think we actually SHOULD remove the elemental
    application from the basic Strikes for all characters. Those cards are
    supposed to be bad!" R242 put the base game's Strike and Defend into her
    starter, and `_is_base_game_basic` is the exemption's two tests: `basic`
    rarity AND no owning `character:`. `CatalystCadence.IsBaseGameBasic` is the
    mod's twin.

    THE ARM'S OWN ATTACKS ARE UNMOVED, which is the half that matters here:
    `proto_ko_kapow` is `rarity: basic` too and it carries `character: klee`,
    so it fails the second test and still applies her Pyro -- and an explosion
    never asks the cadence at all, because it names Pyro outright."""
    state = klee_state([make_enemy(hp=200)])

    strike, defend = load("strike"), load("defend")
    assert effects._is_base_game_basic(strike) is True
    assert effects._element_for(state, strike.effects[0], strike) is None

    kapow = load("proto_ko_kapow")
    assert (kapow.rarity, kapow.character) == ("basic", "klee")
    assert effects._is_base_game_basic(kapow) is False
    assert effects._element_for(
        state, {"op": "damage", "amount": 4, "target": "enemy"},
        kapow) == "pyro"
    assert effects._is_base_game_basic(defend) is True


def test_kapow_retains_at_base_and_the_upgrade_moves_its_damage(overhaul):
    """The 2026-09-02 balance pass moved the starter's detonator: Retain is
    PRINTED now (it used to be what the upgrade bought), and the upgrade buys
    the number instead. Read off the sheet rather than retyped, so a further
    move follows the yaml."""
    from tier0.content import upgrades

    upgrades._prototype_upgrade_index.cache_clear()
    upgrades._upgrade_index.cache_clear()
    try:
        base = load("proto_ko_kapow")
        upgraded = load("proto_ko_kapow+")
        assert base.retain is True and upgraded.retain is True
        assert base.effects[0]["damage"] == 4
        assert upgraded.effects[0]["damage"] == 7
    finally:
        upgrades._prototype_upgrade_index.cache_clear()
        upgrades._upgrade_index.cache_clear()


# ---------------------------------------------------------------------------
# RULE 1 -- the Bomb grows, and never goes off by itself
# ---------------------------------------------------------------------------

def test_rule1_every_charge_grows_by_the_same_amount(overhaul):
    """`Rule1_every_charge_grows_by_the_same_amount`."""
    enemy = make_enemy()
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 5)
    klee_overhaul.place(state, enemy, 8)

    klee_overhaul.grow_pile(enemy, C.KLEE_OVERHAUL_BOMB_GROWTH)

    assert sizes(enemy) == [5 + C.KLEE_OVERHAUL_BOMB_GROWTH,
                            8 + C.KLEE_OVERHAUL_BOMB_GROWTH]
    assert klee_overhaul.total_size(enemy) == 13 + 2 * C.KLEE_OVERHAUL_BOMB_GROWTH


def test_rule1_growth_is_the_constant_by_default(overhaul):
    """`Rule1_growth_is_three_by_default`, read off the CONSTANT rather than
    off the literal 3: rule 1's growth is a placeholder the brief says is not a
    claim, and a test that retyped it would fail the day it is re-baselined
    instead of following it."""
    assert klee_overhaul.growth_for(klee_state()) == C.KLEE_OVERHAUL_BOMB_GROWTH


def test_rule1_the_workshop_adds_one_more_per_stack(overhaul):
    """`Rule1_the_workshop_adds_one_more_per_stack`."""
    state = klee_state()
    state.player.powers[klee_overhaul.BOMB_GROWTH_UP] = 1
    assert klee_overhaul.growth_for(state) == (
        C.KLEE_OVERHAUL_BOMB_GROWTH + C.KLEE_OVERHAUL_WORKSHOP_GROWTH)

    state.player.powers[klee_overhaul.BOMB_GROWTH_UP] = 3
    assert klee_overhaul.growth_for(state) == (
        C.KLEE_OVERHAUL_BOMB_GROWTH + 3 * C.KLEE_OVERHAUL_WORKSHOP_GROWTH)


def test_rule1_alices_recipe_doubles_the_workshops_growth_too(overhaul):
    """`Rule1_alices_recipe_multiplies_the_whole_growth` -- the 2026-09-02
    balance pass, which turned the Rare from "grow by 4 instead of 3" (a
    strictly weaker Explosives Workshop: a second Workshop reached 5 and a
    second Recipe still read 4) into "your Bombs grow twice each turn".

    ADD-THEN-MULTIPLY is the composition, and `GrowthFor` is where it lives:
    "twice" is twice the growth the turn would otherwise have had, the
    Workshop's +1 included. The other order would make the Rare read "twice the
    base and the Workshop once", which neither card says."""
    state = klee_state()
    state.player.powers[klee_overhaul.ALICES_RECIPE] = 1
    assert klee_overhaul.growth_for(state) == (
        C.KLEE_OVERHAUL_BOMB_GROWTH * C.KLEE_OVERHAUL_ALICE_MULTIPLIER)

    state.player.powers[klee_overhaul.BOMB_GROWTH_UP] = 1
    assert klee_overhaul.growth_for(state) == (
        (C.KLEE_OVERHAUL_BOMB_GROWTH + C.KLEE_OVERHAUL_WORKSHOP_GROWTH)
        * C.KLEE_OVERHAUL_ALICE_MULTIPLIER)

    # THE WORKED EXAMPLE, at today's constants and stated as an arithmetic
    # identity rather than as two bare literals: growth 4 gives Recipe alone 8
    # and Recipe-plus-one-Workshop 10. If the constants move the identity
    # follows them, which is what the whole rule-1 placeholder note asks for.
    assert (C.KLEE_OVERHAUL_BOMB_GROWTH, C.KLEE_OVERHAUL_ALICE_MULTIPLIER,
            C.KLEE_OVERHAUL_WORKSHOP_GROWTH) == (4, 2, 1)
    assert klee_overhaul.growth_for(state) == 10
    state.player.powers.pop(klee_overhaul.BOMB_GROWTH_UP)
    assert klee_overhaul.growth_for(state) == 8


def test_rule1_the_turn_start_hook_grows_and_does_not_detonate(overhaul):
    """`Rule1_the_turn_start_hook_grows_and_does_not_detonate`, which is a
    STRUCTURAL pin on the C# side (running the hook needs a combat) and a real
    one here: rule 7's whole point is that the hook the shipped Bomb uses to
    FIRE is the hook this arm uses only to GROW."""
    enemy = make_enemy(hp=50)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 6)

    klee_overhaul.turn_start(state)

    assert sizes(enemy) == [6 + C.KLEE_OVERHAUL_BOMB_GROWTH]
    assert enemy.hp == 50
    assert "ko_explosion" not in counts(state)


def test_rule1_a_whole_fight_never_detonates_a_bomb_by_itself(overhaul):
    """RULE 7 over a real fight: every explosion in the log is preceded by a
    `ko_set_off` or a `ko_mines_answer` -- her card, or her Mine answering an
    attack on her. There is no third way."""
    pilot = make_pilot(loader.pilot_weights("demolition"))
    player = loader.build_player("klee")
    state = run_fight(player, loader.build_encounter("punisher"), pilot,
                      seed=7)
    armed = False
    for entry in state.log:
        if entry["event"] in ("ko_set_off", "ko_mines_answer"):
            armed = True
        elif entry["event"] == "ko_explosion":
            assert armed, "an explosion with no Set off and no Mine behind it"
        elif entry["event"] in ("turn_open", "turn_close"):
            armed = False
    assert counts(state)["ko_explosion"] > 0, "the fight never cooked one"


# ---------------------------------------------------------------------------
# RULE 2 -- Set off, one at a time, before the card's own damage
# ---------------------------------------------------------------------------

def test_rule2_the_pile_is_taken_whole_before_anything_resolves(overhaul):
    """`Rule2_the_pile_is_taken_whole_before_anything_resolves`. Emptied FIRST,
    which is what stops a kill mid-payload re-entering the pile (the shipped
    Bomb's EB-138 discipline, inherited)."""
    enemy = make_enemy()
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 4)
    klee_overhaul.place(state, enemy, 6, is_mine=True)

    taken = klee_overhaul.take_all(enemy)

    assert [c.size for c in taken] == [4, 6]
    assert enemy.ko_charges == []
    assert klee_overhaul.total_size(enemy) == 0
    assert klee_overhaul.take_all(enemy) == []


def test_rule2_set_off_explodes_one_at_a_time_and_then_the_card_hits(overhaul):
    """`Rule2_set_off_explodes_one_at_a_time_and_then_the_card_hits`, and it is
    a real call here where the C# pin reads the IL call sequence.

    THE ORDER IS THE RULE: three separate Pyro hits, then the card's own
    damage. The log is the evidence -- three `ko_explosion` entries, each with
    its own `damage`, and the card's hit last."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    for size in (4, 5, 6):
        klee_overhaul.place(state, enemy, size)

    effects.resolve_card(state, probe(
        [{"op": "set_off", "target": "enemy", "damage": 7}]))

    fired = [e for e in state.log
             if e["event"] in ("ko_explosion", "damage")]
    assert [e.get("size") for e in fired if e["event"] == "ko_explosion"] == [
        4, 5, 6]
    assert [e["base"] for e in fired if e["event"] == "damage"] == [4, 5, 6, 7]
    assert enemy.hp == 200 - (4 + 5 + 6 + 7)
    assert enemy.ko_charges == []


def test_rule2_a_damage_less_set_off_is_a_set_off_with_no_attack(overhaul):
    """"A Set off with no Attack behind it" -- the sheet's absent `damage:`
    key, and Quick Fuse's whole body."""
    enemy = make_enemy(hp=100)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 9)

    effects.resolve_card(state, probe([{"op": "set_off", "target": "enemy"}]))

    assert enemy.hp == 91


def test_rule2_a_random_target_set_off_re_rolls_per_hit(overhaul):
    """`Rule2_a_random_target_set_off_re_rolls_per_hit`. Rule 2's last
    sentence: "For random-target Attacks, per target hit." Two rolls is TWO Set
    offs, so both loaded enemies pop even though each holds its own pile."""
    a, b = make_enemy(hp=100, name="a"), make_enemy(hp=100, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 5)
    klee_overhaul.place(state, b, 5)

    # Both bodies are rolled once each: the stream is fixed by the fixture's
    # seed, so this asserts the SHAPE -- a Set off per roll -- rather than a
    # particular roll.
    effects.resolve_card(state, probe(
        [{"op": "set_off", "target": "random_enemy", "damage": 3,
          "times": 8}]))

    assert counts(state)["ko_set_off"] == 2, (
        "one Set off per LOADED body rolled; an empty pile logs nothing")
    assert a.ko_charges == [] and b.ko_charges == []


def test_rule2_an_all_enemies_set_off_takes_the_aura_filter(overhaul):
    """Flame Dance: "Set off each enemy with a non-Pyro aura." The filter reads
    the board as it stands when each enemy is reached, which is what "each
    enemy that HAS" says."""
    cold, hot, bare = (make_enemy(hp=100, name="cold"),
                       make_enemy(hp=100, name="hot"),
                       make_enemy(hp=100, name="bare"))
    cold.aura, hot.aura = "cryo", "pyro"
    state = klee_state([cold, hot, bare])
    for enemy in (cold, hot, bare):
        klee_overhaul.place(state, enemy, 5)

    effects.resolve_card(state, probe(
        [{"op": "set_off", "target": "all_enemies", "aura": "non_pyro"}]))

    assert cold.ko_charges == []
    assert sizes(hot) == [5] and sizes(bare) == [5]


# ---------------------------------------------------------------------------
# RULE 3 -- the Jump
# ---------------------------------------------------------------------------

def test_rule3_a_bomb_whose_enemy_died_moves_at_its_current_size(overhaul):
    """`Rule3_a_bomb_whose_enemy_died_moves_at_its_current_size`. A jump is a
    MOVE, so the size, the Mine flag and the payload all travel."""
    dead, live_ = make_enemy(hp=1, name="dead"), make_enemy(name="live")
    state = klee_state([dead, live_])
    dead.hp = 0

    klee_overhaul.jump_charges(state, dead, [KleeCharge(11, True, 3)])

    assert sizes(live_) == [11]
    assert live_.ko_charges[0].is_mine is True
    assert live_.ko_charges[0].payload_mine_all == 3


def test_rule3_set_off_jumps_the_charges_behind_a_kill(overhaul):
    """`Rule3_set_off_jumps_the_charges_behind_a_kill`, the brief's OWN worked
    example: "The second of three Bombs killed the enemy: the third jumps."

    The test is read per charge and BEFORE the charge resolves, so the Bomb
    that lands the kill still goes off on a live enemy and every Bomb behind it
    jumps."""
    doomed, other = make_enemy(hp=9, name="doomed"), make_enemy(name="other")
    state = klee_state([doomed, other])
    for size in (4, 5, 6):
        klee_overhaul.place(state, doomed, size)

    exploded = klee_overhaul.set_off(state, doomed)

    assert exploded == 2                  # 4 then 5 kills; 6 never fires
    assert not doomed.alive
    assert sizes(other) == [6]


def test_rule3_a_set_off_aimed_at_a_corpse_moves_the_whole_pile(overhaul):
    """The case R210's bind makes reachable -- the aim is one creature for the
    whole play, DEAD OR ALIVE -- and the C#'s answer taken literally: `SetOff`
    takes the pile before it looks at anything, so every charge jumps."""
    dead, other = make_enemy(hp=1, name="dead"), make_enemy(name="other")
    state = klee_state([dead, other])
    klee_overhaul.place(state, dead, 7)
    dead.hp = 0

    assert klee_overhaul.set_off(state, dead) == 0
    assert sizes(other) == [7]


def test_rule3_a_death_this_arm_did_not_cause_is_swept(overhaul):
    """`Rule3_a_death_this_arm_did_not_cause_is_swept`: "A partner or a poison
    killed the enemy: all of them jump."

    NO REGISTER IS NEEDED ON THIS SIDE, and the test says so: the mod keeps one
    because the game strips a corpse's powers inline, and tier 0 tears nothing
    down -- so the board itself is the register."""
    poisoned, other = make_enemy(hp=10, name="poisoned"), make_enemy(
        name="other")
    state = klee_state([poisoned, other])
    klee_overhaul.place(state, poisoned, 5)
    klee_overhaul.place(state, poisoned, 6, is_mine=True)
    poisoned.hp = 0                       # something that is not a Set off

    klee_overhaul.sweep_jumps(state)

    assert poisoned.ko_charges == []
    assert sorted(sizes(other)) == [5, 6]
    assert klee_overhaul.mine_count(other) == 1


def test_rule3_the_sweep_runs_after_every_card_play(overhaul):
    """`KleeOverhaulSweepHooks.AfterCardPlayed`, the backstop `EB-279` added:
    whatever else happened, the Bombs are on a living enemy before the next
    card is played."""
    doomed, other = make_enemy(hp=4, name="doomed"), make_enemy(name="other")
    state = klee_state([doomed, other])
    klee_overhaul.place(state, doomed, 9)
    state.player.hand.append(probe([{"op": "damage", "amount": 20,
                                     "target": "enemy"}], ctype="attack"))
    state.player.energy = 3

    combat.play_card(state, state.player.hand[0])

    assert not doomed.alive
    assert doomed.ko_charges == []
    assert sizes(other) == [9]


def test_rule3_with_no_living_enemy_the_charges_are_simply_dropped(overhaul):
    """"With no living enemy left there is nowhere to go" -- the only answer
    available, because the fight is over."""
    only = make_enemy(hp=1)
    state = klee_state([only])
    klee_overhaul.place(state, only, 9)
    only.hp = 0

    klee_overhaul.sweep_jumps(state)

    assert only.ko_charges == []


# ---------------------------------------------------------------------------
# RULE 4 -- one Spark per explosion, and no other source
# ---------------------------------------------------------------------------

def test_rule4_one_spark_per_explosion(overhaul):
    """`Rule4_the_spark_comes_off_the_explosion_bus`. THE RELIC IS THE RULE
    (the brief sec.8), so a three-Bomb Set off banks three: the bus rings once
    per EXPLOSION, not once per card."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    for size in (3, 4, 5):
        klee_overhaul.place(state, enemy, size)

    klee_overhaul.set_off(state, enemy)

    assert state.player.sparks == 3 * C.KLEE_OVERHAUL_SPARK_PER_EXPLOSION


def test_rule4_without_the_relic_hook_no_spark_is_minted(overhaul):
    """The gate is the starter's own hook, which is the honest test for "this
    player runs the Spark economy" -- `relics.combat_start_spark`'s own
    argument, and the C#'s `applier.Player != Owner` clause one seat over."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.relic_hooks.clear()
    klee_overhaul.place(state, enemy, 5)

    klee_overhaul.set_off(state, enemy)

    assert state.player.sparks == 0


def test_rule4_she_starts_every_combat_with_the_opening_spark(overhaul):
    """R242 pick 1, and it is a KIT rule rather than a relic clause -- so it
    lands on turn 1 at site E/F, the moment `KleeOverhaulOpening` names."""
    pilot = make_pilot(loader.pilot_weights("demolition"))
    player = loader.build_player("klee")
    state = run_fight(player, loader.build_encounter("punisher"), pilot,
                      seed=11)
    opening = [e for e in state.log if e["event"] == "ko_opening_spark"]
    assert len(opening) == 1
    assert opening[0]["amount"] == C.KLEE_OVERHAUL_OPENING_SPARK
    assert state.log.index(opening[0]) < 40, "not on turn one"


def test_rule4_no_slice_row_mints_a_spark(overhaul):
    """`Rule4_no_slice_card_mints_a_spark`: "Under this flag Sparks come ONLY
    from explosions." Every slice row is swept, so a future row printing
    `gain_spark` fails here rather than quietly opening a second income."""
    rows = [c for c in loader.prototype_cards() if c.id.startswith("proto_ko_")]
    assert rows
    for card in rows:
        assert not any(fx.get("op") == "gain_spark" for fx in card.effects), \
            card.id


def test_rule4_catalytic_converter_pays_only_on_a_reaction(overhaul):
    """"Whenever a Bomb REACTS, gain 1 extra Spark." EXTRA, on top of the
    explosion's own, and only when the explosion reacted -- which is a fact
    only the bus carries, because by the time a listener could look the aura it
    consumed is gone."""
    wet, dry = make_enemy(hp=200, name="wet"), make_enemy(hp=200, name="dry")
    wet.aura = "hydro"
    state = klee_state([wet, dry])
    state.player.powers[klee_overhaul.BOMB_REACTION_SPARK] = 1
    klee_overhaul.place(state, wet, 5)
    klee_overhaul.place(state, dry, 5)

    klee_overhaul.set_off(state, dry)
    assert state.player.sparks == 1        # the explosion's own, and no more

    klee_overhaul.set_off(state, wet)
    assert state.player.sparks == 3        # one for the pop, one for the react
    assert state.ko_reacted_this_turn == 1


def test_rule4_the_upgraded_relics_opening_windfall_is_off(overhaul):
    """`Rule4_the_upgraded_relic_keeps_the_rate_and_loses_the_windfall`. An
    act-2 Touch of Orobas must not hand out a bank before any Bomb has gone
    off; the RATE is untouched (the test above proves it still pays)."""
    from tier0.engine import relics

    state = klee_state()
    state.player.relic_effects = [{"hook": "combat_start_spark", "amount": 4}]
    relics.apply_combat_start(state)
    assert state.player.sparks == 0


def test_rule4_a_spark_priced_row_spends_sparks_and_not_energy(overhaul):
    """Rule 4's last clause: "Some cards cost Sparks instead of energy." The
    sheet spells the price as a top-level `spend_spark`, which `spark_cost`
    reads and `card_playable` gates on -- the same seam the mod declares as
    `PrintedSparkPrice` and gates at `IsPlayable`."""
    enemy = make_enemy(hp=100)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 6)
    card = load("proto_ko_fwoosh")
    assert combat.spark_cost(card) == 1
    assert combat.card_cost(state, card) == 0

    state.player.sparks = 0
    assert combat.card_playable(state, card) is False
    state.player.sparks = 1
    assert combat.card_playable(state, card) is True

    state.player.energy = 3
    state.player.hand.append(card)
    combat.play_card(state, card)
    assert state.player.sparks == 1        # spent 1, and the explosion paid 1
    assert state.player.energy == 3


def test_rule7_the_base_free_attack_rule_is_retired(overhaul):
    """RULE 7: "no automatic free attack, no 'at 3 Sparks'". The C# retires the
    base rule for the whole of `PROTOTYPE_CARDS`
    (`SparkPower.BaseRuleActive == false`), and this is that retirement at this
    engine's two sites -- the zeroing in `card_cost` and the automatic consume
    in `play_card`."""
    state = klee_state()
    state.player.sparks = 9
    attack = probe([{"op": "damage", "amount": 6, "target": "enemy"}],
                   cid="proto_ko_probe_attack", cost=1)
    assert combat.card_cost(state, attack) == 1

    state.player.energy = 3
    state.player.hand.append(attack)
    combat.play_card(state, attack)
    assert state.player.sparks == 9        # nothing was consumed implicitly


def test_the_arm_neither_feeds_nor_shows_burst(overhaul):
    """`EB-266`: under the arm Sparks are her only meter, so nothing may fill
    Burst -- the mod's one-line guard inside `BurstResource.Find`, at this
    engine's own funnel."""
    from tier0.engine import resources

    state = klee_state()
    state.player.burst_max = 40
    resources.gain_burst(state, 5, "probe")
    assert state.player.burst_energy == 0


# ---------------------------------------------------------------------------
# RULE 5 -- Pyro, and an ordinary hit
# ---------------------------------------------------------------------------

def test_rule5_an_explosion_is_an_ordinary_pyro_hit(overhaul):
    """Rule 5 as R248 left it: every reaction in the element table and the
    TARGET's own modifiers apply to a cooked bomb without a word printed on her
    cards. The brief's "Strength on Klee" is the half `EB-343` overturned, and
    `test_eb343_*` below is where that is pinned."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    enemy.powers["vulnerable"] = 1
    klee_overhaul.place(state, enemy, 10)

    klee_overhaul.set_off(state, enemy)

    hit = next(e for e in state.log if e["event"] == "damage")
    assert hit["base"] == 10
    assert hit["amount"] == 15, "the enemy's Vulnerable rode the charge"
    assert enemy.aura == "pyro", "the explosion applied Pyro"


def test_eb343_a_bomb_carries_the_targets_modifiers_only(overhaul):
    """`EB-343` (ruled R248): a Bomb is the enemy's burden.

    [USER]'s OWN BOARD, 2026-09-03: three Bombs of printed 6, 4 and 4 into
    Tender's minus 5 Strength put `Bomb -1` on the badge. A printed 6 is a Bomb
    6, always -- PLACEMENT stores the printed size (which this engine always
    did) and the SET OFF no longer adds her Strength or takes her Weak (which
    it did until now).
    """
    enemy = make_enemy(hp=400)
    state = klee_state([enemy])
    state.player.powers["strength"] = -5
    state.player.powers["weak"] = 2
    klee_overhaul.place(state, enemy, 6)
    klee_overhaul.place(state, enemy, 4)
    klee_overhaul.place(state, enemy, 4)

    # PLACEMENT: the printed size, at any Strength.
    assert [c.size for c in enemy.ko_charges] == [6, 4, 4]
    assert klee_overhaul.total_size(enemy) == 14

    klee_overhaul.set_off(state, enemy)

    hits = [e for e in state.log if e["event"] == "damage"
            and e["source"] == klee_overhaul.EXPLOSION_SOURCE]
    assert [h["amount"] for h in hits] == [6, 4, 4], \
        "nothing of Klee's reached the charges"

    # And the other direction: positive Strength does not inflate one either.
    other = make_enemy(hp=400)
    state = klee_state([other])
    state.player.powers["strength"] = 3
    klee_overhaul.place(state, other, 6)

    klee_overhaul.set_off(state, other)

    hit = next(e for e in state.log if e["event"] == "damage")
    assert hit["amount"] == 6


def test_eb343_the_targets_own_terms_still_bite_per_hit(overhaul):
    """The other side of the same rule: the ENEMY's terms do apply, and a cap
    applies per HIT rather than to the pile. Intangible is this engine's cap
    (`refpowers._intangible_cap`); the mod's twin reads the same hook and finds
    Hard To Kill there too, which tier 0 has no enemy for."""
    enemy = make_enemy(hp=400)
    enemy.powers["intangible"] = 1
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 9)
    klee_overhaul.place(state, enemy, 9)

    klee_overhaul.set_off(state, enemy)

    hits = [e for e in state.log if e["event"] == "damage"
            and e["source"] == klee_overhaul.EXPLOSION_SOURCE]
    assert [h["amount"] for h in hits] == [1, 1], "capped per hit, not per pile"


def test_rule5_an_explosion_is_not_an_attack_card_hit(overhaul):
    """The reading, and it is the C#'s: `Explode` goes out through
    `ElementalHit.Deal`, the funnel for every NON-Attack hit, not through
    `DamageCmd.Attack`. In tier 0 `source == "attack"` is what gates Shatter,
    the shipped on-hit detonation and Skittish; an explosion takes none of
    them."""
    enemy = make_enemy(hp=200)
    enemy.skittish = 5
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 8)

    klee_overhaul.set_off(state, enemy)

    hit = next(e for e in state.log if e["event"] == "damage")
    assert hit["source"] == klee_overhaul.EXPLOSION_SOURCE != "attack"
    assert enemy.block == 0, "Skittish is an Attack-card rule and did not fire"


# ---------------------------------------------------------------------------
# RULE 6 -- the Mine
# ---------------------------------------------------------------------------

def test_rule6_only_the_mines_go_off_and_plain_bombs_stay(overhaul):
    """`Rule6_only_the_mines_go_off_and_plain_bombs_stay`."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 4, is_mine=True)
    klee_overhaul.place(state, enemy, 9)
    klee_overhaul.place(state, enemy, 6, is_mine=True)
    assert klee_overhaul.mine_count(enemy) == 2

    mines = klee_overhaul.take_mines(enemy)

    assert [c.size for c in mines] == [4, 6]
    assert sizes(enemy) == [9]
    assert klee_overhaul.mine_count(enemy) == 0
    assert klee_overhaul.take_mines(enemy) == []


def test_rule6_a_mine_grows_exactly_like_a_bomb(overhaul):
    """`Rule6_a_mine_grows_exactly_like_a_bomb`."""
    enemy = make_enemy()
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 4, is_mine=True)
    klee_overhaul.place(state, enemy, 4)

    klee_overhaul.grow_pile(enemy, C.KLEE_OVERHAUL_BOMB_GROWTH)

    grown = 4 + C.KLEE_OVERHAUL_BOMB_GROWTH
    assert sizes(enemy) == [grown, grown]
    assert enemy.ko_charges[0].is_mine is True


def test_rule6_the_mine_fires_before_the_hit_lands(overhaul):
    """`Rule6_the_mine_fires_before_the_hit_lands`, which is a STRUCTURAL pin
    on the C# side (the hit needs a combat) and a real enemy turn here.

    A Mine big enough to kill the attacker means the attack never lands at all,
    which is the strongest available statement of "before"."""
    enemy = make_enemy(hp=6, name="attacker", intents=ATTACKER)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 9, is_mine=True)
    hp_before = state.player.hp

    combat._enemy_turn(state, enemy)

    assert not enemy.alive
    assert state.player.hp == hp_before, "the attack landed after all"


def test_rule6_a_plain_bomb_does_not_answer_an_attack(overhaul):
    """Rule 7 on the pile the Mine is not: a plain Bomb stays exactly where it
    is when the enemy swings."""
    enemy = make_enemy(hp=50, name="attacker", intents=ATTACKER)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 9)

    combat._enemy_turn(state, enemy)

    assert sizes(enemy) == [9]
    assert state.player.hp < state.player.max_hp


def test_rule6_a_multi_hit_intent_finds_no_second_mine(overhaul):
    """"NO PER-ACTION LATCH IS NEEDED": the Mines are CONSUMED, so the second
    hit of a multi-hit intent finds none. The rule is self-limiting."""
    enemy = make_enemy(hp=200, name="attacker",
                       intents=[{"kind": "attack", "amount": 3, "times": 3}])
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 5, is_mine=True)

    combat._enemy_turn(state, enemy)

    assert counts(state)["ko_explosion"] == 1


def test_eb336_a_lethal_mine_costs_the_player_no_hp(overhaul):
    """`EB-336`, on the seat's own board: a Chomper on 4 HP under a `Mine 4`,
    swinging `8x2`, with the player holding Block.

    THE MOD IS WHAT MOVED, NOT THIS. `combat._enemy_turn` has always taken the
    `enemy.alive` test between the trap and the Block spend, so a lethal Mine
    has always cost this engine's player nothing; the mod read `dealer.IsDead`
    once at the top of a call the Mine fires from the middle of, so its first
    hit landed for the full 8. Pinned on BOTH numbers -- HP and Block --
    because HP is the acceptance the two engines share and Block is the one
    thing they do not (`ProtoBombPower.Preempted` says so on the other side).
    """
    enemy = make_enemy(hp=4, name="attacker",
                       intents=[{"kind": "attack", "amount": 8, "times": 2}])
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 4, is_mine=True)
    state.player.block = 6
    hp_before = state.player.hp

    combat._enemy_turn(state, enemy)

    assert not enemy.alive
    assert state.player.hp == hp_before, "the hit landed after all"
    assert state.player.block == 6, "the pre-empted hit spent Block"


def test_eb336_a_mine_that_does_not_kill_leaves_the_hit_intact(overhaul):
    """The other half of `EB-336`'s acceptance, and the half that must not
    move: a Mine too small to kill answers the attack, and the attack still
    lands for what it prints."""
    enemy = make_enemy(hp=40, name="attacker",
                       intents=[{"kind": "attack", "amount": 8}])
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 4, is_mine=True)
    hp_before = state.player.hp

    combat._enemy_turn(state, enemy)

    assert enemy.alive
    assert counts(state)["ko_explosion"] == 1, "the Mine did not answer"
    assert state.player.hp == hp_before - 8


# ---------------------------------------------------------------------------
# THE PAYLOAD (Jumpy Dumpty)
# ---------------------------------------------------------------------------

def test_the_payload_rides_the_explosion_not_the_card(overhaul):
    """`The_payload_rides_the_explosion_not_the_card`, and it is the whole of
    what makes the starter's promise legible: the Mines arrive when the big
    Bomb finally goes off, not when it was planted."""
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])

    effects.resolve_card(state, probe(
        [{"op": "plant_bomb", "target": "enemy", "size": 8,
          "payload_mine_all": 3}], ctype="skill"))
    planted = a if a.ko_charges else b
    assert klee_overhaul.mine_count(a) + klee_overhaul.mine_count(b) == 0

    klee_overhaul.set_off(state, planted)

    assert klee_overhaul.mine_count(a) == 1
    assert klee_overhaul.mine_count(b) == 1
    assert sizes(a) == [3] and sizes(b) == [3]


def test_the_payload_travels_with_the_charge_that_carries_it(overhaul):
    """`The_payload_travels_with_the_charge_that_carries_it`, and the CARRIER
    is a plain Bomb."""
    enemy = make_enemy()
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 8, payload_mine_all=3)

    taken = klee_overhaul.take_all(enemy)

    assert taken[0].payload_mine_all == 3
    assert taken[0].is_mine is False


def test_the_payload_pays_from_inside_a_stacked_pile(overhaul):
    """`EB-395`, and the C# twin is
    `The_payload_survives_being_stacked_with_a_plain_bomb`.

    THE BOARD IS THE ROUND-10 SEAT'S FIGHT 3 (`opus-run4-act1.md`): Jumpy
    Dumpty planted, a Pop! Bomb stacked onto the same enemy, two of Klee's
    turns of growth, then one Set off on an aggregate the badge printed as
    `Bomb 25 / Bombs here: 2`. The seat came out of that detonation with no
    Mine badge anywhere, where every SINGLE-Bomb Set off in the same run had
    placed one, and could not tell from any printed face whether the rider had
    failed or fired and been eaten.

    WHAT THIS ENGINE ANSWERS, which is the half the row asks to be pinned
    first: the rider is not lost in the stack. A charge is a charge -- `place`
    stores the payload on the one that carries it, `grow_pile` moves `size`
    and touches nothing else, `take_all` hands the list back in placement
    order, and `_explode` reads the payload off each charge as it goes off. So
    the carrier pays from inside a pile of two exactly as it pays alone, on
    every enemy, and the Mine it leaves is a Mine on the pile the badge
    counts.
    """
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 8, payload_mine_all=3)   # Jumpy Dumpty
    klee_overhaul.place(state, a, 5)                       # Pop!
    klee_overhaul.turn_start(state)
    klee_overhaul.turn_start(state)
    growth = 2 * klee_overhaul.growth_for(state)
    assert sizes(a) == [8 + growth, 5 + growth]
    assert klee_overhaul.mine_count(a) + klee_overhaul.mine_count(b) == 0

    exploded = klee_overhaul.set_off(state, a)

    assert exploded == 2
    # THE RIDER PAID, on every enemy and at its printed size -- growth is the
    # carrier's, never the payload's.
    assert sizes(a) == [3] and sizes(b) == [3]
    # AND THE BADGE PRINTS IT: `mine_count` is the number the mod's
    # `{Mines}` var is written from (`SyncDisplay`), so a pile the page can
    # count is a pile the badge says "including 1 Mine" about.
    assert klee_overhaul.mine_count(a) == 1
    assert klee_overhaul.mine_count(b) == 1


def test_a_merge_carries_every_payload_it_moved(overhaul):
    """`A_merge_carries_every_payload_it_moved`, `EB-395`'s other suspect.

    Careful Arrangement moves every Bomb onto one enemy AS ONE Bomb, and a
    merge is a MOVE: the merged charge is a Mine if any part of it was and it
    carries the summed payload, so a card whose face only says it moves Bombs
    cannot delete a rider. Read here as the rider PAYING after the merge,
    rather than as the field surviving it.
    """
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 8, payload_mine_all=3)   # Jumpy Dumpty
    klee_overhaul.place(state, b, 5)                       # Pop!, elsewhere

    klee_overhaul.merge_all_to(state, b, growth=5)

    assert sizes(a) == [] and sizes(b) == [8 + 5 + 5]
    assert b.ko_charges[0].payload_mine_all == 3

    klee_overhaul.set_off(state, b)

    assert klee_overhaul.mine_count(a) == 1
    assert klee_overhaul.mine_count(b) == 1


# ---------------------------------------------------------------------------
# RULE 7 -- the two per-turn counters and the two memories
# ---------------------------------------------------------------------------

def test_rule7_both_counters_are_written_at_one_site(overhaul):
    """`Rule7_both_counters_are_written_at_one_site`."""
    state = klee_state()
    klee_overhaul.note_explosion(state, reacted=False, damage_dealt=5)
    klee_overhaul.note_explosion(state, reacted=True, damage_dealt=7)

    assert state.ko_set_off_this_turn == 2
    assert state.ko_reacted_this_turn == 1
    assert state.ko_damage_set_off_this_play == 12


def test_rule7_grounded_reads_last_turns_count_and_the_turn_rolls(overhaul):
    """`Rule7_grounded_reads_last_turns_count_and_the_turn_rolls`."""
    state = klee_state()
    klee_overhaul.roll_to(state, 1)
    klee_overhaul.note_explosion(state, reacted=False, damage_dealt=4)
    assert (state.ko_set_off_this_turn, state.ko_set_off_last_turn) == (1, 0)

    klee_overhaul.roll_to(state, 2)
    assert (state.ko_set_off_this_turn, state.ko_set_off_last_turn) == (0, 1)

    klee_overhaul.roll_to(state, 3)
    assert state.ko_set_off_last_turn == 0


def test_rule7_a_skipped_round_reports_an_honest_zero(overhaul):
    """`Rule7_a_skipped_round_reports_an_honest_zero`. The roll is on the round
    STAMP, so a jump of more than one round means Klee had no turn in between.
    Unreachable from `combat._player_turn`, which always advances by one --
    written anyway, because the C# reads the stamp and a twin that assumed the
    increment would be a different function wearing the same name."""
    state = klee_state()
    klee_overhaul.roll_to(state, 1)
    klee_overhaul.note_explosion(state, reacted=False, damage_dealt=4)
    klee_overhaul.roll_to(state, 5)
    assert state.ko_set_off_last_turn == 0


def test_rule7_grounded_pays_for_the_quiet_turn_and_not_the_loud_one(overhaul):
    """Grounded's condition, end to end. LAST turn and not this one is the
    whole design: the decision it pays for was made a turn ago.

    UNPOWERED, the mod's `ValueProp.Unpowered`: it is a POWER's Block, so Frail
    does not bite it."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.GROUNDED] = 6
    state.player.powers["frail"] = 2

    klee_overhaul.roll_to(state, 1)
    klee_overhaul.turn_start_late(state)
    assert state.player.block == 6, "quiet turn: paid, and unreduced by Frail"

    state.player.block = 0
    klee_overhaul.place(state, enemy, 5)
    klee_overhaul.set_off(state, enemy)          # a loud turn
    klee_overhaul.roll_to(state, 2)
    klee_overhaul.turn_start_late(state)
    assert state.player.block == 0, "it went off last turn: Grounded stays quiet"


def test_eb344_the_held_turn_also_grants_one_spark(overhaul):
    """`EB-344` (ruled R248): "gain 6 Block AND 1 Spark".

    ONE CONDITION, TWO PAYOUTS -- a turn after a detonation grants NEITHER,
    which is what makes the Spark part of the same decision rather than a
    second rule to keep in step. Rule 4 mints one Spark per EXPLOSION, so the
    held turn this card is written for is the one turn that mints none.
    """
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.GROUNDED] = 6
    sparks_before = state.player.sparks

    klee_overhaul.roll_to(state, 1)
    klee_overhaul.turn_start_late(state)
    assert state.player.block == 6
    assert state.player.sparks == sparks_before + C.KLEE_OVERHAUL_GROUNDED_SPARK

    banked = state.player.sparks
    state.player.block = 0
    klee_overhaul.place(state, enemy, 5)
    klee_overhaul.set_off(state, enemy)          # a loud turn
    sparks_after_explosions = state.player.sparks
    klee_overhaul.roll_to(state, 2)
    klee_overhaul.turn_start_late(state)

    assert state.player.block == 0, "no Block after a detonation"
    assert state.player.sparks == sparks_after_explosions, \
        "and no Spark either: one condition, both halves"
    assert banked <= sparks_after_explosions      # the explosion paid its own


def test_eb344_the_upgrade_moves_the_block_and_not_the_spark(overhaul):
    """The number's home. `power_amount: +2` is the BLOCK (6 -> 8); the Spark
    is the kit's rate and is 1 at both levels."""
    state = klee_state()
    state.player.powers[klee_overhaul.GROUNDED] = 8      # the upgraded card
    sparks_before = state.player.sparks

    klee_overhaul.roll_to(state, 1)
    klee_overhaul.turn_start_late(state)

    assert state.player.block == 8
    assert state.player.sparks == sparks_before + C.KLEE_OVERHAUL_GROUNDED_SPARK
    assert C.KLEE_OVERHAUL_GROUNDED_SPARK == 1


def test_rule7_run_away_reads_the_turn_counter(overhaul):
    """The other half of the contested thing: Run Away! pays for the turn in
    which something DID go off. The predicate is the ledger's own counter, the
    same expression the emitter writes into the card."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    card = load("proto_ko_run_away")

    effects.resolve_card(state, card)
    quiet = state.player.block

    state.player.block = 0
    klee_overhaul.place(state, enemy, 5)
    klee_overhaul.set_off(state, enemy)
    effects.resolve_card(state, card)

    assert quiet == 3
    assert state.player.block == 7


def test_rule7_the_two_predicates_answer_off_the_ledger(overhaul):
    """Sizzle and Perfect Timing read `ReactedThisTurn`, Run Away! and Ammo
    Scavenging read `SetOffThisTurn`. Neither predicate is a synonym for
    `reaction_triggered_this_turn`, which counts EVERY reaction."""
    state = klee_state()
    assert effects._predicate(state, "bomb_went_off_this_turn") is False
    assert effects._predicate(state, "bomb_reacted_this_turn") is False

    state.reactions_this_turn = 3          # somebody else's reaction
    assert effects._predicate(state, "bomb_reacted_this_turn") is False

    klee_overhaul.note_explosion(state, reacted=True, damage_dealt=1)
    assert effects._predicate(state, "bomb_went_off_this_turn") is True
    assert effects._predicate(state, "bomb_reacted_this_turn") is True


def test_the_per_play_memory_is_opened_by_the_card_that_reads_it(overhaul):
    """`The_per_play_size_memory_is_opened_by_the_card_that_reads_it`, and the
    turn counter is NOT reset by a play: Run Away! and Ammo Scavenging read the
    TURN, Big Badda Boom reads the PLAY."""
    state = klee_state()
    klee_overhaul.note_explosion(state, reacted=False, damage_dealt=9)

    klee_overhaul.begin_play(state, probe([{"op": "damage", "amount": 1}]))
    assert state.ko_damage_set_off_this_play == 9, "an ordinary row opens nothing"

    klee_overhaul.begin_play(state, probe(
        [{"op": "set_off", "target": "enemy", "damage": 12},
         {"op": "damage_set_off_total", "target": "enemy"}]))
    assert state.ko_damage_set_off_this_play == 0
    assert state.ko_set_off_this_turn == 1


def test_big_badda_boom_hits_again_for_what_the_bombs_dealt(overhaul):
    """`EB-270`: the ledger banks what each explosion LANDED for, so the second
    clause is the card's printed promise and not the raw charge sum. Under the
    ENEMY's Vulnerable the two part company, which is the whole reason the
    number is banked -- `EB-343` (R248) moved which modifier can do the parting
    and not the claim, Klee's own Weak no longer reaching a Bomb at all."""
    enemy = make_enemy(hp=400)
    enemy.powers["vulnerable"] = 1        # the charges land BIGGER
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 8)
    klee_overhaul.place(state, enemy, 9)

    effects.resolve_card(state, load("proto_ko_big_badda_boom"))

    explosions = [e for e in state.log
                  if e["event"] == "damage" and e["source"] == "set_off"]
    dealt = sum(e["amount"] for e in explosions)
    hits = [e for e in state.log
            if e["event"] == "damage" and e["source"] == "attack"]
    assert len(hits) == 2, "the printed 12, then the banked total"
    assert hits[1]["base"] == dealt
    assert dealt > 17, "Vulnerable moved what the charges landed for"


def test_the_multiplier_is_armed_by_the_card_and_spent_by_its_set_off(overhaul):
    """`The_multiplier_is_armed_by_the_card_and_spent_by_its_set_off`. R243
    ([USER]: "move The Big One to 4x with no flat number"): the flag became
    the row's own number, and an unarmed Set off is x1."""
    state = klee_state()
    assert klee_overhaul.peek_multiplier(state) == 1

    klee_overhaul.arm_multiplier(state, 4)
    assert klee_overhaul.peek_multiplier(state) == 4     # a Mine may not eat it
    assert klee_overhaul.take_multiplier(state) == 4
    assert klee_overhaul.take_multiplier(state) == 1     # "this way" = this card


def test_the_big_one_multiplies_only_its_own_set_off(overhaul):
    """The row's order IS the rule: `multiply_set_off` sits ahead of the
    `set_off` it pays for, and the next Set off after that one is unaffected.
    The row's multiplier is 4 and the card has no hit of its own (R243), so
    on a Bomb-less board it is refused like Quick Fuse (`EB-261`)."""
    enemy = make_enemy(hp=400)
    state = klee_state([enemy])
    card = load("proto_ko_the_big_one")
    assert klee_overhaul.refuses_for_no_bomb(state, card)
    klee_overhaul.place(state, enemy, 10)
    assert not klee_overhaul.refuses_for_no_bomb(state, card)

    effects.resolve_card(state, card)
    assert [e["size"] for e in state.log if e["event"] == "ko_explosion"] == [40]
    assert not [e for e in state.log
                if e["event"] == "damage" and e["source"] == "attack"], \
        "no flat number: the card's whole body is the Set off"

    klee_overhaul.place(state, enemy, 10)
    klee_overhaul.set_off(state, enemy)
    assert [e["size"] for e in state.log
            if e["event"] == "ko_explosion"] == [40, 10]


def test_a_mine_peeks_the_multiplier_without_spending_it(overhaul):
    """`PeekMultiplier`'s whole reason: an enemy attack must not eat the window
    The Big One armed for its own Set off."""
    enemy = make_enemy(hp=200, name="attacker", intents=ATTACKER)
    state = klee_state([enemy])
    klee_overhaul.arm_multiplier(state, 4)
    klee_overhaul.place(state, enemy, 5, is_mine=True)

    combat._enemy_turn(state, enemy)

    assert klee_overhaul.peek_multiplier(state) == 4
    assert [e["size"] for e in state.log if e["event"] == "ko_explosion"] == [20]


# ---------------------------------------------------------------------------
# THE CARD VERBS THAT ARE NOT A SET OFF
# ---------------------------------------------------------------------------

def test_careful_arrangement_merges_the_board_into_one_bomb(overhaul):
    """`MergeAllTo`, and its TWO REPORTED DEFAULTS the card text does not
    state: the merged Bomb is a MINE if any merged charge was one, and it
    carries the payloads of every merged charge, summed. A merge is a move, and
    a move loses nothing."""
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 5, is_mine=True)
    klee_overhaul.place(state, a, 6)
    klee_overhaul.place(state, b, 7, payload_mine_all=3)

    klee_overhaul.merge_all_to(state, b, growth=2)

    assert a.ko_charges == []
    assert sizes(b) == [5 + 6 + 7 + 2]
    assert b.ko_charges[0].is_mine is True
    assert b.ko_charges[0].payload_mine_all == 3


def test_chain_fuse_grows_one_enemys_pile_only(overhaul):
    """`GrowOn`: "Each Bomb on the enemy grows by 3." One body, every charge on
    it."""
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 4)
    klee_overhaul.place(state, a, 5)
    klee_overhaul.place(state, b, 6)
    state.card_aim, state.card_aim_bound = a, True

    effects._resolve_effects(
        state, [{"op": "grow_bombs", "target": "enemy", "amount": 3}],
        probe([]))

    assert sizes(a) == [7, 8]
    assert sizes(b) == [6]


def test_sorry_jean_removes_the_largest_and_blocks_for_its_size(overhaul):
    """`The_emergency_exit_removes_one_charge_and_reports_its_size`, plus the
    reported default the card text does not state: THE LARGEST, the only
    deterministic answer a player can plan around."""
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 3)
    klee_overhaul.place(state, b, 11)
    klee_overhaul.place(state, b, 7)

    effects.resolve_card(state, load("proto_ko_sorry_jean"))

    assert sizes(a) == [3] and sizes(b) == [7]
    assert state.player.block == 11


def test_sorry_jean_on_an_empty_board_is_a_printed_no_op(overhaul):
    state = klee_state([make_enemy()])
    effects.resolve_card(state, load("proto_ko_sorry_jean"))
    assert state.player.block == 0


def test_ammo_scavenging_draws_one_per_bomb_that_went_off_this_turn(overhaul):
    """`DrawPerSetOff`: rule 7's first counter, spent."""
    enemy = make_enemy(hp=400)
    state = klee_state([enemy])
    state.player.draw_pile = [probe([], cid=f"filler{i}", ctype="skill")
                              for i in range(5)]
    for size in (3, 4, 5):
        klee_overhaul.place(state, enemy, size)
    klee_overhaul.set_off(state, enemy)

    hand_before = len(state.player.hand)
    klee_overhaul.draw_per_set_off(state)

    assert len(state.player.hand) == hand_before + 3


# ---------------------------------------------------------------------------
# THE POOL PASS -- the energy-priced plain detonator (round 10, 2026-09-04)
# ---------------------------------------------------------------------------

def test_countdown_sets_off_the_whole_pile_and_then_draws(overhaul):
    """`ProtoKoCountdown`. The arm's one detonator priced in ENERGY: three
    round-10 seats held Spark-priced detonators at 0 Spark with a fat Bomb
    sitting on the enemy and nothing in hand that could cash it.

    THE ORDER IS THE CARD. The Set off is first, so the card the draw finds is
    drawn into a board the explosion has already resolved -- the C# twin pins
    the same order off the compiled `OnPlay`
    (`klee-mod/KleeTests/Prototype/PoolPassTests.cs`)."""
    enemy = make_enemy(hp=400)
    state = klee_state([enemy])
    state.player.energy = 3
    state.player.draw_pile = [probe([], cid=f"filler{i}", ctype="skill")
                              for i in range(5)]
    for size in (3, 4, 5):
        klee_overhaul.place(state, enemy, size)

    card = load("proto_ko_countdown")
    assert [fx["op"] for fx in card.effects] == ["set_off", "draw"]
    assert combat.spark_cost(card) == 0
    assert combat.card_cost(state, card) == 1

    hand_before = len(state.player.hand)
    effects.resolve_card(state, card)

    assert sizes(enemy) == [], "every Bomb on the target went off"
    assert enemy.hp < 400
    assert len(state.player.hand) == hand_before + 1


def test_countdown_upgraded_draws_two(overhaul):
    """The row's only printed number is its draw, so that is what the smith
    moves (`upgrade: {draw: 1}`, the `Cards` var on the C# side)."""
    enemy = make_enemy(hp=400)
    state = klee_state([enemy])
    state.player.draw_pile = [probe([], cid=f"filler{i}", ctype="skill")
                              for i in range(5)]
    klee_overhaul.place(state, enemy, 5)

    card = load("proto_ko_countdown+")
    assert card.effects[1] == {"op": "draw", "amount": 2}

    hand_before = len(state.player.hand)
    effects.resolve_card(state, card)

    assert sizes(enemy) == []
    assert len(state.player.hand) == hand_before + 2


def test_countdown_still_draws_on_a_bomb_less_board(overhaul):
    """`EB-261`'s gate does NOT cover this row and must not: the draw is a
    second clause that pays whatever the board holds, so Countdown is a
    playable cantrip with no Bomb out rather than a dead card."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.energy = 3
    state.player.sparks = 0
    state.player.draw_pile = [probe([], cid=f"filler{i}", ctype="skill")
                              for i in range(5)]

    card = load("proto_ko_countdown")
    assert klee_overhaul.set_off_only(card) is False
    assert combat.card_playable(state, card) is True

    hand_before = len(state.player.hand)
    effects.resolve_card(state, card)

    assert len(state.player.hand) == hand_before + 1
    assert enemy.hp == 200


def test_sparks_n_splash_echoes_the_pile_without_spending_it(overhaul):
    """`BombEchoPower`, R250 (2026-09-04): "at the end of your turn, deal
    Pyro damage to a random enemy equal to its LARGEST Bomb" -- the largest
    single charge, not the sum ([USER]'s own 2026-09-02 design predates R250,
    which replaced the sum it paid at first).

    IT READS THE PILE AND DOES NOT SPEND IT, which is the whole card and the
    whole of why rule 7 survives it. The row printed an automatic Set off
    before this, and the Rare the growth deck most wants was the one card that
    cashed its pile without being asked ("auto-detonation on Sparks n' Splash
    completely bricks the growth build")."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.BOMB_ECHO] = 1
    klee_overhaul.place(state, enemy, 4)
    klee_overhaul.place(state, enemy, 3)

    klee_overhaul.turn_end(state)

    assert sizes(enemy) == [4, 3], "the Bombs stay and keep growing"
    assert enemy.hp == 196, "the echo dealt the LARGEST charge (4), not 4+3"
    # NOTHING EXPLODED, so rule 4 mints nothing and neither of rule 7's
    # counters moves -- the ledger is not touched at all.
    assert state.player.sparks == 0
    assert (state.ko_set_off_this_turn, state.ko_reacted_this_turn) == (0, 0)
    assert counts(state)["ko_explosion"] == 0
    # It pays AGAIN next turn, and bigger, because the pile grew: the largest
    # charge is now 4 + growth.
    klee_overhaul.turn_start(state)
    klee_overhaul.turn_end(state)
    assert enemy.hp == 196 - (4 + C.KLEE_OVERHAUL_BOMB_GROWTH)


def test_sparks_n_splash_pays_per_copy_its_own_random_target(overhaul):
    """`EB-358`, default applied: a second Sparks 'n' Splash badges 2 (the
    power's stack count) and used to pay the pile ONCE. Now each copy is its
    OWN end-of-turn hit, each paying its own random target's largest Bomb --
    on a one-enemy board that means two hits landing on the same enemy."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.BOMB_ECHO] = 2
    klee_overhaul.place(state, enemy, 5)
    klee_overhaul.place(state, enemy, 3)

    klee_overhaul.turn_end(state)

    assert sizes(enemy) == [5, 3], "still not spent, by either copy"
    assert enemy.hp == 200 - 2 * 5, "two hits, each the largest Bomb (5)"
    assert counts(state)["ko_bomb_echo"] == 2, "the badge's count is the hits"


def test_the_echo_rolls_only_over_bombed_enemies(overhaul):
    """"A random enemy ... equal to the Bombs on it" -- so the roll is over the
    enemies that actually hold one, and a board with none does nothing at all.
    The auto-detonation it replaces rolled over EVERY enemy."""
    bare, loaded = make_enemy(hp=200, name="bare"), make_enemy(hp=200,
                                                              name="loaded")
    state = klee_state([bare, loaded])
    state.player.powers[klee_overhaul.BOMB_ECHO] = 1

    klee_overhaul.turn_end(state)
    assert counts(state)["ko_bomb_echo"] == 0

    klee_overhaul.place(state, loaded, 6)
    for _ in range(8):
        klee_overhaul.turn_end(state)
    assert bare.hp == 200, "an unbombed enemy is never rolled"
    assert loaded.hp == 200 - 8 * 6


def test_the_echo_is_pyro_and_is_not_an_attack(overhaul):
    """`ElementalHit.Deal`, the same funnel an explosion takes: the echo reacts
    with an aura and carries her Strength, and no card is being played so
    nothing that keys off Attacks sees it. A THIRD source name, because the
    echo is not an explosion and a log that conflated them could not answer
    "how many Bombs went off"."""
    enemy = make_enemy(hp=200)
    enemy.skittish = 5
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.BOMB_ECHO] = 1
    state.player.powers["strength"] = 2
    klee_overhaul.place(state, enemy, 6)

    klee_overhaul.turn_end(state)

    hit = next(e for e in state.log if e["event"] == "damage")
    assert hit["source"] == klee_overhaul.ECHO_SOURCE
    assert klee_overhaul.ECHO_SOURCE not in ("attack",
                                             klee_overhaul.EXPLOSION_SOURCE)
    assert hit["amount"] == 8, "Strength rode it"
    assert enemy.aura == "pyro"
    assert enemy.block == 0, "Skittish is an Attack-card rule and did not fire"


def test_chained_reactions_re_bombs_once_per_explosion(overhaul):
    """"Whenever one of your Bombs goes off, place a Bomb 3 on a random
    enemy." Once per EXPLOSION, so a three-Bomb Set off is three new Bombs --
    and each is a plain Bomb, so nothing it places can fire by itself."""
    enemy = make_enemy(hp=400)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.CHAINED_REACTIONS] = 3
    for size in (2, 3, 4):
        klee_overhaul.place(state, enemy, size)

    klee_overhaul.set_off(state, enemy)

    assert sizes(enemy) == [3, 3, 3]
    assert klee_overhaul.mine_count(enemy) == 0


# ---------------------------------------------------------------------------
# THE PLAYABILITY GATE -- `EB-261`
# ---------------------------------------------------------------------------

def test_a_set_off_only_card_is_unplayable_on_a_bomb_less_board(overhaul):
    """`EB-261`, the mod's `IsPlayable` gate at this engine's twin seam. Quick
    Fuse was playable on a Bomb-less board: it spent the Spark and did
    nothing."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.sparks = 3
    state.player.energy = 3
    quick_fuse = load("proto_ko_quick_fuse")
    assert klee_overhaul.set_off_only(quick_fuse) is True

    assert combat.card_playable(state, quick_fuse) is False
    klee_overhaul.place(state, enemy, 5)
    assert combat.card_playable(state, quick_fuse) is True


def test_a_set_off_that_carries_damage_is_never_gated(overhaul):
    """The clause is deliberately narrow: Ka-pow! with no Bombs on the board is
    still an Attack, and refusing it would be a balance change rather than a
    legibility fix."""
    state = klee_state([make_enemy(hp=200)])
    state.player.energy = 3
    kapow = load("proto_ko_kapow")
    assert klee_overhaul.set_off_only(kapow) is False
    assert combat.card_playable(state, kapow) is True


def test_every_slice_row_agrees_with_the_emitters_own_gate(overhaul):
    """The two implementations of `card_is_set_off_only` are checked against
    each other over the whole surface, which is the only way "the same list"
    stays true."""
    from tools import gen_klee_cards

    for card in loader.prototype_cards():
        if not card.id.startswith("proto_ko_"):
            continue
        row = {"effects": card.effects}
        assert klee_overhaul.set_off_only(card) == \
            gen_klee_cards.card_is_set_off_only(row), card.id


# ---------------------------------------------------------------------------
# THE WHOLE SLICE LOADS AND RESOLVES
# ---------------------------------------------------------------------------

def test_every_slice_row_resolves_without_raising(overhaul):
    """THE ACCEPTANCE THIS TWIN EXISTS FOR: every row on the surface, played
    against a loaded board, resolves. A row whose op or field the twin cannot
    read fails HERE rather than in the middle of a 300-run read."""
    ids = list(C.KLEE_OVERHAUL_STARTER_IDS) + list(C.KLEE_OVERHAUL_POOL_IDS)
    for cid in sorted(set(i for i in ids if i.startswith("proto_ko_"))):
        a = make_enemy(hp=400, name="a")
        b = make_enemy(hp=400, name="b")
        state = klee_state([a, b])
        state.player.sparks = 5
        state.player.energy = 5
        state.player.draw_pile = [probe([], cid=f"filler{i}", ctype="skill")
                                  for i in range(5)]
        klee_overhaul.place(state, a, 6)
        klee_overhaul.place(state, b, 4, is_mine=True)
        effects.resolve_card(state, load(cid))


def test_the_ops_all_resolve_through_the_module(overhaul):
    """`effects.OPS` points at the arm's own resolvers and at nothing else, so
    a rule cannot be re-expressed at a call site."""
    for op in klee_overhaul.OVERHAUL_OPS:
        assert op in effects.OPS
        assert effects.OPS[op].__name__ != "_op_klee_overhaul_off"


# ---------------------------------------------------------------------------
# THE HEXEREI READERS -- R244 (`review/ruled/klee-hexerei-readers-2026-09-02.md`)
# ---------------------------------------------------------------------------
#
# Three rows in Klee's own pool that read the coven's one-word family mark.
# The C# twins are `klee-mod/KleeTests/Prototype/HexereiReaderTests.cs`, case
# for case; where a case is structural there (the headless harness cannot play
# a card) it is a real board here, which is the whole point of the twin.


def witch(cid="proto_mc_witch", ctype="skill"):
    """A Hexerei card by the PRINTED mark -- the sheet key, not an id list."""
    card = probe([], cid=cid, ctype=ctype)
    card.hexerei = True
    return card


def test_coven_errand_places_one_bomb_with_no_witch_played(overhaul):
    """"Place a Bomb 5." The else arm, and the honest read of the card alone:
    a Pop! that costs 1, which the ruled packet calls "a little under the
    Common bar ... the price of the upside"."""
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    state.card_aim, state.card_aim_bound = a, True
    effects.resolve_card(state, load("proto_ko_coven_errand"))
    assert sizes(a) == [5]
    assert sizes(b) == []


def test_coven_errand_goes_wide_after_a_witch(overhaul):
    """"If you played a Hexerei card this turn, place it on ALL enemies
    instead." INSTEAD is the load-bearing word: the aimed enemy holds ONE
    Bomb, not two, which is what makes the widening a target change rather
    than a second placement."""
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    combat._finish_play(state, witch())
    state.card_aim, state.card_aim_bound = a, True
    effects.resolve_card(state, load("proto_ko_coven_errand"))
    assert sizes(a) == [5]
    assert sizes(b) == [5]


def test_coven_errands_upgrade_moves_both_arms(overhaul):
    """"Upgrade: Bomb 7." ONE printed number, so the wide arm and the aimed
    arm cannot upgrade to different Bombs -- which is the reason the widening
    is a field on the op rather than two `plant_bomb`s in a conditional."""
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    state.card_aim, state.card_aim_bound = a, True
    effects.resolve_card(state, load("proto_ko_coven_errand+"))
    assert sizes(a) == [7]

    state = klee_state([a := make_enemy(hp=200, name="a"),
                        b := make_enemy(hp=200, name="b")])
    combat._finish_play(state, witch())
    state.card_aim, state.card_aim_bound = a, True
    effects.resolve_card(state, load("proto_ko_coven_errand+"))
    assert sizes(a) == [7]
    assert sizes(b) == [7]


def test_the_hexerei_count_is_per_turn(overhaul):
    """The window is the TURN, and the ledger rolls with it -- the same stamp
    rule rule 7's two counters take."""
    state = klee_state([make_enemy(hp=200)])
    klee_overhaul.roll_to(state, 1)
    combat._finish_play(state, witch())
    assert klee_overhaul.played_hexerei_this_turn(state) is True
    klee_overhaul.roll_to(state, 2)
    assert klee_overhaul.played_hexerei_this_turn(state) is False


def test_witches_circle_plants_per_witch_and_is_dead_alone(overhaul):
    """"Whenever you play a Hexerei card, place a Bomb 3 on a random enemy."

    DEAD ALONE IS THE CARD, not a defect: the ruled packet's pick 2 was taken
    at its default, so a deck with no witch in it never sets this off. Both
    halves are asserted, because the second is the one a future "fix" would
    quietly remove."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    effects.resolve_card(state, load("proto_ko_witches_circle"))
    assert state.player.powers[klee_overhaul.WITCHES_CIRCLE] == 3

    # A plain card pays nothing.
    combat._finish_play(state, probe([], cid="proto_ko_plain"))
    assert sizes(enemy) == []
    # A witch pays once, per play.
    combat._finish_play(state, witch())
    combat._finish_play(state, witch())
    assert sizes(enemy) == [3, 3]


def test_witches_circle_upgrades_the_bomb_it_plants(overhaul):
    """"Upgrade: Bomb 5." The stack IS the size, Chained Reactions' grammar."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    effects.resolve_card(state, load("proto_ko_witches_circle+"))
    combat._finish_play(state, witch())
    assert sizes(enemy) == [5]


def test_alices_introduction_magic_makes_the_hand_a_coven_for_one_turn(
        overhaul):
    """THE ROW'S OWN ACCEPTANCE: a card that is NOT Hexerei counts as one for
    the rest of this turn, and does not next turn.

    Both readers are watched through one board, because the point of the card
    is that every reader sees the same widened family: Witches' Circle plants
    for the marked card while the window is open and plants nothing for it
    after the window shuts.
    """
    enemy = make_enemy(hp=400)
    state = klee_state([enemy])
    plain = probe([], cid="proto_ko_plain", ctype="skill")
    state.player.hand = [plain]
    effects.resolve_card(state, load("proto_ko_witches_circle"))
    effects.resolve_card(state, load("proto_ko_alices_introduction_magic"))

    from tier0.engine import companion_hexerei
    assert plain.hexerei is False           # the PRINTED mark never moved
    assert companion_hexerei.is_hexerei(state, plain) is True
    combat._finish_play(state, plain)
    assert sizes(enemy) == [3]

    # ... AND NOT THE NEXT TURN. The window closes at the arm's turn end.
    klee_overhaul.turn_end(state)
    assert companion_hexerei.is_hexerei(state, plain) is False
    combat._finish_play(state, plain)
    assert sizes(enemy) == [3]


def test_alices_window_covers_the_hand_it_saw_and_not_a_later_draw(overhaul):
    """The ruling's first derived reading, and the reason the upgrade is
    Retain: "the window is this turn, over the cards in hand when it is
    played (a card drawn later this turn is not counted)"."""
    state = klee_state([make_enemy(hp=200)])
    held = probe([], cid="proto_ko_held", ctype="skill")
    later = probe([], cid="proto_ko_later", ctype="skill")
    state.player.hand = [held]
    effects.resolve_card(state, load("proto_ko_alices_introduction_magic"))
    state.player.hand.append(later)

    from tier0.engine import companion_hexerei
    assert companion_hexerei.is_hexerei(state, held) is True
    assert companion_hexerei.is_hexerei(state, later) is False


def test_alices_introduction_magic_is_itself_hexerei_and_upgrades_to_retain(
        overhaul):
    """The ruling's second derived reading ("it counts as Hexerei itself, so
    it does not need a second witch to start a circle") and the upgrade the
    packet names."""
    card = load("proto_ko_alices_introduction_magic")
    assert card.hexerei is True
    assert card.retain is False
    upgraded = load("proto_ko_alices_introduction_magic+")
    assert upgraded.hexerei is True
    assert upgraded.retain is True


# ---------------------------------------------------------------------------
# THE DEFENCE SHELF -- R252
# (`review/ruled/klee-overhaul-round-9-2026-09-04.md`, pick 1 at its default)
# ---------------------------------------------------------------------------
#
# Four rows in Klee's own pool plus one companion stand-in (Barbara's, pinned
# with the rest of the seam in `test_companion_standins.py`). The round-9 run
# died on act-2 floor 22 with no Block in hand, and the brief's own weakness
# stands -- so every row here is keyed to the Bomb state and none is a plain
# Block. The C# twins are `klee-mod/KleeTests/Prototype/DefenceShelfTests.cs`,
# case for case.


def test_dodoco_cover_places_and_blocks_on_one_card(overhaul):
    """The opening hand's answer to "no placer": a Bomb 4 AND 5 Block, so a
    turn that draws no Cook card is still a turn that cooked something."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.card_aim, state.card_aim_bound = enemy, True

    effects.resolve_card(state, load("proto_ko_dodoco_cover"))

    assert sizes(enemy) == [4]
    assert state.player.block == 5


def test_dodoco_covers_upgrade_moves_both_printed_numbers(overhaul):
    """`{bomb_size: +2, block: +2}`: the row prints two numbers and the smith
    moves both, which is what keeps the `+` card from being a copy."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.card_aim, state.card_aim_bound = enemy, True

    effects.resolve_card(state, load("proto_ko_dodoco_cover+"))

    assert sizes(enemy) == [6]
    assert state.player.block == 7


def test_careful_now_blocks_for_the_largest_bomb_and_spends_nothing(overhaul):
    """Careful Now: "Gain Block equal to your largest Bomb when played, up to 10."

    THE LARGEST SINGLE CHARGE, BOARD-WIDE (`klee_overhaul.largest_size`, the
    Splash's own reader since R250) -- not the sum, and not one enemy's.

    AND IT SPENDS NOTHING, which is the one line separating it from Sorry,
    Jean... above: every charge is exactly where it was afterwards, still
    growing.
    """
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 3)
    klee_overhaul.place(state, a, 4)
    klee_overhaul.place(state, b, 7)

    effects.resolve_card(state, load("proto_ko_careful_now"))

    assert state.player.block == 7          # the largest ONE, not 3+4 or 14
    assert sizes(a) == [3, 4] and sizes(b) == [7]


def test_careful_now_is_capped_and_the_upgrade_raises_the_cap(overhaul):
    """The cap is the row's printed number and the ONLY thing its upgrade
    moves -- which is what keeps the row from turning Grounded's cook turn
    into a stall."""
    enemy = make_enemy(hp=400)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 40)

    effects.resolve_card(state, load("proto_ko_careful_now"))
    assert state.player.block == 10

    state.player.block = 0
    effects.resolve_card(state, load("proto_ko_careful_now+"))
    assert state.player.block == 13


def test_careful_now_on_a_bomb_less_board_is_a_printed_no_op(overhaul):
    """No Bomb, no Block -- `remove_bomb_for_block`'s own answer one row over.
    A Retain card that banked its cap on an empty board would be exactly the
    flat Block this shelf is written not to be."""
    state = klee_state([make_enemy()])
    effects.resolve_card(state, load("proto_ko_careful_now"))
    assert state.player.block == 0


def test_careful_now_retains_and_keeps_retaining_upgraded(overhaul):
    """Retain is on the BASE card (the row's own `retain: true`) and the
    upgrade is the cap, so the `+` card keeps the keyword it was printed
    with."""
    assert load("proto_ko_careful_now").retain is True
    assert load("proto_ko_careful_now+").retain is True


# ---------------------------------------------------------------------------
# THE POOL PASS, ROUND 11 -- Stoke the Fuse, the Spark sink
# ---------------------------------------------------------------------------

def stoke(state, enemies, sparks, cid="proto_ko_stoke_the_fuse"):
    """Play Stoke the Fuse at a bank of `sparks`, through `play_card`.

    THROUGH `play_card` AND NOT `resolve_card`, which every other row in this
    file may use: the growth is priced per Spark SPENT and reads
    `state.sparks_at_play`, a field only a real play sets. A test that
    resolved the body directly would be measuring a card nobody played.
    """
    card = load(cid)
    state.player.sparks = sparks
    state.player.energy = 3
    state.player.hand.append(card)
    combat.play_card(state, card)
    return card


def test_stoke_the_fuse_is_unplayable_at_zero_sparks(overhaul):
    """THE X PRICE'S GATE. "Spend all your Sparks" charges ONE at the
    playability seam -- an empty bank cannot pay, any bank holding a Spark
    can -- which is `PrintedSparkPrice => 1` in the mod and
    `effects.spend_spark_price` here. Without it the card would be playable
    at 0 and resolve to nothing, which is exactly the silent no-play the
    Spark cost line exists to refuse."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 6)
    card = load("proto_ko_stoke_the_fuse")

    assert combat.spark_cost(card) == 1
    assert combat.card_cost(state, card) == 0

    state.player.sparks = 0
    assert combat.card_playable(state, card) is False
    state.player.sparks = 1
    assert combat.card_playable(state, card) is True


def test_stoke_the_fuse_spends_the_whole_bank_and_grows_per_spark(overhaul):
    """Three Sparks grow the Bomb by 9 (3 per Spark) and leave the bank at 0.

    The bank is EMPTIED, not decremented by a printed price: the row's price
    is X, so what it pays is whatever it holds -- and what it pays is what the
    growth is measured in."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 6)

    stoke(state, [enemy], 3)

    assert sizes(enemy) == [6 + 9]
    assert state.player.sparks == 0
    assert state.player.energy == 3        # a 0-energy row


def test_stoke_the_fuse_upgraded_pays_four_per_spark(overhaul):
    """`upgrade: {grow: +1}` -- the rate is the row's one printed number and
    the only thing the smith moves, so three Sparks buy 12 instead of 9."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 6)

    stoke(state, [enemy], 3, cid="proto_ko_stoke_the_fuse+")

    assert sizes(enemy) == [6 + 12]
    assert state.player.sparks == 0


def test_stoke_the_fuse_grows_the_largest_of_two_bombs(overhaul):
    """"Your largest Bomb", board-wide and ONE charge -- `block_largest_bomb`'s
    scope with `grow_bombs`'s effect, and neither one's spread: the other
    charges are exactly where they were."""
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 4)
    klee_overhaul.place(state, a, 9)
    klee_overhaul.place(state, b, 7)

    stoke(state, [a, b], 2)

    assert sizes(a) == [4, 9 + 6]          # the 9 took all of it
    assert sizes(b) == [7]


def test_stoke_the_fuse_sets_nothing_off(overhaul):
    """IT IS NOT A DETONATOR. The Sparks buy a bigger Bomb and the cash-out is
    still a separate card, which is what keeps hold-or-cash in the player's
    hands. The enemy takes no damage and the pile is still standing."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 6)

    stoke(state, [enemy], 4)

    assert enemy.hp == 200
    assert sizes(enemy) == [6 + 12]
    assert counts(state)["ko_bomb_exploded"] == 0


def test_stoke_the_fuse_on_a_bomb_less_board_still_spends(overhaul):
    """A REAL COST, REPORTED. Nothing on the board is a legal place to play
    this -- the row is not `set_off_only` and takes no Bomb gate (it is a
    grow, not a Set off) -- so the bank goes and nothing grows. That is the
    row's losing line, and it is the one the charter asks every card to
    keep."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])

    stoke(state, [enemy], 3)

    assert state.player.sparks == 0
    assert sizes(enemy) == []
    assert klee_overhaul.set_off_only(load("proto_ko_stoke_the_fuse")) is False


