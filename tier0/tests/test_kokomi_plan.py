"""THE PLAN, clause by clause (QUARANTINED, `C.KOKOMI_OVERHAUL`, draft 6).

`tier0/engine/kokomi_plan.py` is the sim twin of
`klee-mod/KleeCode/Powers/Prototype/KokomiPlan.cs`, and this file is that twin
checked AGAINST THE C# READING rather than against itself: every test names the
sentence in the mod it is pinning, and the ones that pin a READING (the
resolution hook, the Casket's dealer, "also happen now", "last turn" at
carry-out, Nereid read per entry) say so in their own docstring.

`tier0/tests/test_kokomi_overhaul.py` keeps the OTHER half -- that the flag
ships OFF and that OFF is byte-identical. This file is what happens with it on.

NOTHING MEASURED HERE IS QUOTABLE ANYWHERE (R215 B). These are shape
assertions about an engine, not numbers about a game.
"""

import collections

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, kokomi_plan, powers
from tier0.engine.combat import run_fight
from tier0.engine.state import Card
from tier0.pilot.policy import make_pilot
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards

ATTACKER = [{"kind": "attack", "amount": 5}]
BLOCKER = [{"kind": "block", "amount": 5}]


@pytest.fixture
def overhaul(monkeypatch):
    """The flag on, with both id-resolving caches cleared on the way in and
    out -- `test_kokomi_overhaul.overhaul`'s fixture, for its reasons.

    THE UPGRADE INDEX IS THE THIRD, cleared for exactly the reason the two
    above are: `upgrades._upgrade_index` is `lru_cache`d and carries the
    PROTOTYPE deltas only when the flag was on the first time it was filled,
    so a run that reached an upgrade with the flag off left every
    `apply_upgrade` here raising "no applicable upgrade". A real cross-file
    flake before anything in this file read it -- `-k "kokomi or upgrade"`
    over the suite fell on `test_both_defensive_rows_load_and_smith` -- and it
    belongs on the fixture that already owns the flag."""
    def clear_upgrade_caches():
        # GUARDED, because a test may have monkeypatched one of these to a
        # plain function for the length of its own case: a cache that is not
        # a cache right now has nothing to clear and is not an error.
        from tier0.content import upgrades

        for fn in (upgrades._upgrade_index,
                   upgrades._prototype_upgrade_index):
            getattr(fn, "cache_clear", lambda: None)()

    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()
    clear_upgrade_caches()
    monkeypatch.setattr(C, "KOKOMI_OVERHAUL", True)
    yield
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()
    clear_upgrade_caches()


def kokomi_state(enemies=None, hp=80):
    st = make_state(enemies=enemies, hp=hp)
    st.player.character_id = "kokomi"
    st.player.element = "hydro"
    st.player.cadence = "catalyst"
    st.in_player_turn = True
    return st


def plan_card(clauses, effects_=None, cid="proto_kk_probe"):
    """A probe row carrying a Plan line. `proto_`-prefixed because
    `loader._validate_plan_shape` refuses a Plan on a shipped id, and this
    keeps the probe legal by the same rule the sheet is."""
    return Card(id=cid, name="probe", cost=1, type="skill",
                effects=list(effects_ or []), plan=list(clauses))


def counts(state):
    return collections.Counter(e["event"] for e in state.log)


# --- 1. SHAPE: the loader's half of `gen_klee_cards.plan_reason` -----------

def test_every_shipped_plan_line_passes_the_shape_check():
    """The 16 Plan rows on the surface, through the same gate the emitter
    puts them through. Read off the loaded cards, which is the whole point of
    `plan:` no longer being stripped."""
    planned = [c for c in loader.prototype_cards() if c.plan]
    # FIFTEEN since 2026-09-02: Sango Isshin traded its Plan line for a
    # condition on one ([USER]: "this requires absolutely 0 setup or combo").
    # SIXTEEN with R236's Gorou Personal, the first Plan line on a COMPANION
    # row -- the shape check is the row's owner's, not the row's kind's.
    # SEVENTEEN with `EB-335`'s Tide Wall (R246 pick 2), the first Plan line
    # whose clause multiplies the morning it is carried out in.
    # EIGHTEEN with the tempo shelf's Ripple (round 9 pick 1, 2026-09-04),
    # whose Plan line is the arm's first to pay Energy.
    # TWENTY-ONE after the pool pass (`EB-492`): Riptide, Pincer, Flank and
    # Feigned Retreat printed one, and Nereid's Ascension GAVE one up -- it is
    # a Power now, so the Rare that doubles Plans is no longer a Plan.
    # TWENTY-SIX after pool pass two (`EB-643`): Opening Gambit,
    # Second Wave, Scout Ahead and the two DUSK rows print a Plan
    # line; Second Thoughts, Ebb Tide and Converging Tide are
    # now-lines that operate on the queue and print none.
    assert len(planned) == 26
    for card in planned:
        assert kokomi_plan.plan_shape_reason(card.plan) is None, card.id


@pytest.mark.parametrize("clauses,fragment", [
    ([], "non-empty"),
    ([{"op": "detonate", "amount": 1}], "not one of the planned clauses"),
    ([{"op": "damage", "amount": 4, "target": "enemy"}], "a planned clause lands"),
    ([{"op": "damage", "amount": 4}], "a planned clause lands"),
    ([{"op": "draw", "amount": "X"}], "positive literal int"),
    ([{"op": "draw", "amount": 0}], "positive literal int"),
    ([{"op": "apply_power", "power": "strength", "amount": 2,
       "target": "front_enemy"}], "not one of"),
    ([{"op": "draw", "amount": 1, "times": 2}], "not understood"),
])
def test_the_shape_check_refuses_what_the_emitter_refuses(clauses, fragment):
    """Closed clause table, closed target spellings, literal positive amounts.

    A LITERAL AMOUNT is the load-bearing one: a Plan is read a turn after it
    was written, so a formula resolved against combat state would be printed
    text meaning something different every time it is carried out -- the
    `spend_spark_amount` / `block_at_turn_start_turns` precedent.
    """
    reason = kokomi_plan.plan_shape_reason(clauses)
    assert reason and fragment in reason


def test_a_shipped_row_may_not_print_a_plan():
    """`plan:` is prototype surface only, the way `description:` is."""
    with pytest.raises(ValueError, match="prototype surface only"):
        loader._validate_plan_shape(
            Card(id="waters_edge", name="x", cost=1, type="skill",
                 plan=[{"op": "draw", "amount": 1}]))


def test_the_plan_survives_a_deepcopy_as_its_own_list():
    """`Card.__deepcopy__` copies exactly `_MUTABLE_FIELDS`, and `plan` is a
    list -- a new mutable field left off that tuple is silently SHARED between
    copies, which `test_state.py` exists to catch and this says one more
    time for the field this branch added."""
    import copy
    card = plan_card([{"op": "draw", "amount": 1}])
    twin = copy.deepcopy(card)
    assert twin.plan == card.plan
    assert twin.plan is not card.plan


# --- 2. THE FLAG OFF -------------------------------------------------------

def test_nothing_plans_with_the_flag_off():
    st = kokomi_state()
    card = plan_card([{"op": "draw", "amount": 1}])
    assert kokomi_plan.live(st) is False
    assert kokomi_plan.plan_aimed_at_pet(st, card) is False
    kokomi_plan.schedule(st, card)
    assert st.kk_plan_queue == []


def test_nothing_plans_for_a_seat_that_is_not_kokomi(overhaul):
    """`KokomiOverhaul.LiveFor`'s character limb. A debuff-applying Furina
    must not start writing Plans or answering with a jellyfish."""
    st = kokomi_state()
    st.player.character_id = "furina"
    card = plan_card([{"op": "draw", "amount": 1}])
    assert kokomi_plan.live(st) is False
    assert kokomi_plan.plan_aimed_at_pet(st, card) is False


# --- 3. ONE CLAUSE KIND PER TEST ------------------------------------------

def carry_out(state, clauses, replay=None):
    """Write one Plan and carry it out at the next turn start, which is the
    only way a Plan ever resolves. Returns the state for chaining."""
    card = plan_card(clauses)
    kokomi_plan.schedule(state, card, replay=replay)
    kokomi_plan.resolve_all(state)
    return state


def test_draw(overhaul):
    st = kokomi_state()
    st.player.draw_pile = [plan_card([], cid=f"proto_kk_f{i}")
                           for i in range(5)]
    carry_out(st, [{"op": "draw", "amount": 3}])
    assert len(st.player.hand) == 3


def test_energy(overhaul):
    st = kokomi_state()
    st.player.energy = 0
    carry_out(st, [{"op": "energy", "amount": 2}])
    assert st.player.energy == 2


def test_block_is_powered(overhaul):
    """RULE 3: "your Strength and Dexterity count, since the plans are hers".

    Draft 2's planned Block was `Unpowered` (the NC-11 power-sourced line);
    draft 6 states the opposite rule in the brief, and the C# clause carries
    `ValueProp.Move` with its own comment saying so. `modify_block_gained` is
    this engine's name for that prop -- Frail bites it, Dexterity feeds it.
    """
    st = kokomi_state()
    st.player.powers["frail"] = 1
    carry_out(st, [{"op": "block", "amount": 10}])
    assert st.player.block == powers.modify_block_gained(st.player, 10)
    assert st.player.block < 10


def test_mend_never_goes_above_entry_hp(overhaul):
    """`KokomiRules.Mend`'s whole rule, and the one number the arm's ledger
    carries per combat."""
    st = kokomi_state(hp=80)
    st.mi_entry_hp = 80
    st.player.hp = 72
    carry_out(st, [{"op": "mend", "amount": 15}])
    assert st.player.hp == 80


def test_damage_lands_on_the_front_enemy_meaning_leftmost_alive(overhaul):
    """Rule 3's targeting sentence. NOT lowest-HP, which is this engine's
    ordinary aim -- `KokomiPlan.FrontEnemy` is board order's first LIVING
    creature, so a dead leftmost slot hands the job to the next one."""
    front = make_enemy(hp=40, name="front")
    back = make_enemy(hp=5, name="back")
    st = kokomi_state(enemies=[front, back])
    carry_out(st, [{"op": "damage", "amount": 9, "target": "front_enemy"}])
    assert front.hp == 31 and back.hp == 5

    front.hp = 0
    carry_out(st, [{"op": "damage", "amount": 4, "target": "front_enemy"}])
    assert back.hp == 1


def test_front_enemy_skips_a_minion(overhaul):
    """`R250`, round-5 sec.6 pick 1 at its default. Two round-5 formations put
    a Minion-flagged decoy on the leftmost slot on purpose -- The Kin's
    Followers absorbed a Feint Plan meant for the Priest, and Queen's Torch
    Head Amalgam took every single-target Plan for a whole fight (round-5
    packet sec.2) -- so `front_enemy` now reads `is_minion`, the sim's own
    mirror of the game's `MinionPower` (state.py, NC-7 alpha), rather than the
    raw leftmost-alive read `KokomiPlan.FrontEnemy`'s header used to state
    alone."""
    decoy = make_enemy(hp=40, name="decoy")
    decoy.is_minion = True
    boss = make_enemy(hp=40, name="boss")
    st = kokomi_state(enemies=[decoy, boss])
    carry_out(st, [{"op": "damage", "amount": 9, "target": "front_enemy"}])
    assert boss.hp == 31 and decoy.hp == 40

    # A board of Minions ALONE still takes the hit -- landing on nothing
    # would be worse than landing on the decoy.
    only_minion = make_enemy(hp=40, name="only-minion")
    only_minion.is_minion = True
    st2 = kokomi_state(enemies=[only_minion])
    carry_out(st2, [{"op": "damage", "amount": 9, "target": "front_enemy"}])
    assert only_minion.hp == 31


def test_damage_to_every_enemy(overhaul):
    a, b = make_enemy(hp=40, name="a"), make_enemy(hp=40, name="b")
    st = kokomi_state(enemies=[a, b])
    carry_out(st, [{"op": "damage", "amount": 5, "target": "all_enemies"}])
    assert (a.hp, b.hp) == (35, 35)


def test_a_planned_hit_is_the_jellyfishs_and_applies_hydro(overhaul):
    """`EB-334`, R246 pick 1. THE BAKE-KURAGE DEALS IT, so nothing of hers is
    read AT THE MORNING, and the Hydro still lands -- which is the half of
    rule 3 the ruling left alone.

    Round four-c is the defect: her Weak cut two banked Plans at the morning
    (12 to 9, 5 to 3) and no screen said so, while the enemy's own Vulnerable
    raised nothing. The three pins below are the three modifiers the row names,
    one apiece.

    `EB-599` MOVED HER STRENGTH TO WRITING TIME, so the buff here is picked up
    AFTER the Plan is written: what R246 pick 1 refuses is a carry-out reading
    her buffs at the morning, and that is exactly what is still refused."""
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    card = plan_card([{"op": "damage", "amount": 9, "target": "front_enemy"}])
    kokomi_plan.schedule(st, card)
    st.player.powers["strength"] = 3
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 40 - 9
    assert enemy.aura == "hydro"


def test_the_oaths_now_line_applies_hydro_like_its_carry_out(overhaul):
    """`EB-462` (D default, Kokomi r14 packet sec.4), the sim half.

    "Kurage's Oath prints [Hydro] in its title while a rider says its own hit
    applies no aura and only the carry-out is a Hydro hit; a seat built a turn
    on the tag, and the same Electro-then-Hydro sequence reacted with Deep
    Current and not with the Oath's now-line."

    The row declares `applies_element` on its own damage clause, which beats
    the cadence -- the cadence elements her ATTACKS and this is a Skill -- and
    `_element_for` falls back to the CHARACTER's element for a character row,
    which carries none of its own. The mod's twin is the `IElementalCard` the
    generator now emits on this class.

    Seen to FAIL: the enemy was bare after the now-line, and the Electro aura
    below survived it.
    """
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    effects.resolve_card(st, loader.get_card("proto_kk_kurages_oath"))
    assert enemy.hp == 40 - 3
    assert enemy.aura == "hydro"

    # AND IT REACTS, which is the thing the seat was denied: an Electro aura
    # standing in front of the now-line is consumed rather than ignored.
    charged = make_enemy(hp=40)
    charged.aura = "electro"
    charged.aura_turns_left = 3
    st2 = kokomi_state(enemies=[charged])
    effects.resolve_card(st2, loader.get_card("proto_kk_kurages_oath"))
    assert charged.aura != "electro"


def test_her_weak_does_not_shrink_a_planned_hit(overhaul):
    """`EB-334` PIN 1: Weak ON KOKOMI, no effect. The seat's own arithmetic --
    "Plan: Deal 12 damage" paying 9 the next morning, exactly x0.75."""
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    st.player.powers["weak"] = 2
    carry_out(st, [{"op": "damage", "amount": 12, "target": "front_enemy"}])
    assert enemy.hp == 40 - 12


def test_enemy_vulnerable_multiplies_a_planned_hit(overhaul):
    """`EB-334` PIN 2: Vulnerable ON THE ENEMY, x1.5. The half that paid
    nothing before -- "27 landed where x1.5 would have been 40"."""
    enemy = make_enemy(hp=60)
    enemy.powers["vulnerable"] = 2
    st = kokomi_state(enemies=[enemy])
    carry_out(st, [{"op": "damage", "amount": 12, "target": "front_enemy"}])
    assert enemy.hp == 60 - 18


def test_an_attack_buff_on_kokomi_reaches_the_line_she_wrote_it_under(
        overhaul):
    """`EB-334` PIN 3, AS `EB-599` LEFT IT. Strength is this engine's whole
    vocabulary for a flat attack buff -- `powers.modify_damage_dealt` is where
    every one of them lands -- so what it pins is the class.

    The r22 default reversed the direction: her Strength is folded into the
    number WRITTEN DOWN, because that is what the player was reading when they
    committed the turn. A buff she picks up afterwards still pays nothing,
    which is the pin above.
    """
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    st.player.powers["strength"] = 5
    carry_out(st, [{"op": "damage", "amount": 7, "target": "front_enemy"}])
    assert enemy.hp == 40 - 12


def test_eb545_a_planned_feigned_retreat_pays_both_halves(overhaul):
    """`EB-545`. THE TWO HALVES THAT LOOKED LIKE THEY POINTED APART.

    Kokomi r19 lane 1 read Feigned Retreat's Plan as adding damage but not
    Block, while the face says "Plan: Gain 4 Block and deal 6 damage" -- so
    either the Block clause was not carried out or the morning block did not
    print it. THE BLOCK LANDS: the carry-out pays 4 Block and 6 damage, both
    clauses, and this is the pin that says so from the sheet's own row rather
    than from a probe card.

    The seat's own sentence is about the FACE, not the payment: "the Plan adds
    damage but not block, so the block half is strictly worse for waiting". The
    now-line and the Plan line print the same 4, which is the card's shape and
    a design reading, not a defect. Nothing in the payment moves here.
    """
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    st.player.block = 0

    card = loader.get_card("proto_kk_feigned_retreat")
    kokomi_plan.schedule(st, card)
    kokomi_plan.resolve_all(st)

    assert st.player.block == 4, "the planned Block is paid"
    assert enemy.hp == 200 - 6
    # BOTH CLAUSES SAY SO IN THE LOG, in the order the card prints them --
    # which is what the morning block's line and its HP rows are built from.
    said = [ev for ev in st.log
            if ev["event"] in ("block", "damage")]
    assert [ev["event"] for ev in said] == ["block", "damage"]
    assert said[0]["amount"] == 4 and said[1]["amount"] == 6


def test_eb545_the_upgrade_moves_both_planned_halves(overhaul):
    """And the `+` card pays 6 and 8, which is the other half of the sheet's
    own claim: `plan_block` and `plan_damage` are separate deltas and a card
    that upgraded one of them would be the defect the row suspected."""
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    st.player.block = 0

    kokomi_plan.schedule(st, loader.get_card("proto_kk_feigned_retreat+"))
    kokomi_plan.resolve_all(st)

    assert st.player.block == 6
    assert enemy.hp == 200 - 8


def test_skittish_does_not_fire_on_a_carry_out(overhaul):
    """`EB-538`. A CARRY-OUT IS NOT A HIT, and the seat could not tell.

    Kokomi r19 lane 2: Skittish gave no Block to a body hit by Kurage's Oath's
    and Ambush's carry-outs, and 6 Block to a plain Strike on the same enemy in
    the same fight -- "either a defect or a large undocumented advantage of
    planning into blockers". It is the second, and it is the rule Klee's Set
    off already prints: `source="plan"` is not `"attack"`, and `"attack"` is
    what gates Shatter, the on-hit detonation and Skittish in this engine, as
    `ElementalHit.Deal`'s `ValueProp.Unpowered` does in the mod. The rule does
    not move; the Plan tip now says it.
    """
    enemy = make_enemy(hp=200)
    enemy.skittish = 6
    st = kokomi_state(enemies=[enemy])

    carry_out(st, [{"op": "damage", "amount": 9, "target": "front_enemy"}])

    hit = next(e for e in st.log if e["event"] == "damage")
    assert hit["source"] == "plan" != "attack"
    assert enemy.block == 0, "Skittish is an Attack-card rule and did not fire"

    # AND THE SAME BODY, SAME FIGHT, TAKES AN ATTACK CARD: the seat's own
    # control, and what makes the first half a rule rather than an inert enemy.
    effects.deal_damage_to_enemy(st, enemy, 6, source="attack")
    assert enemy.block == 6


def test_a_plan_caused_debuff_is_still_hers(overhaul):
    """`EB-334`, the half the flag deliberately does NOT move: the applier
    stays her, so the Tamakushi Casket answers a debuff a Plan applies. If the
    fix had swapped the applier to the pet this would read 40."""
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
    carry_out(st, [{"op": "apply_power", "power": "weak", "amount": 1,
                    "target": "front_enemy"}])
    assert enemy.powers.get("weak") == 1
    assert enemy.hp == 40 - C.KOKOMI_OVERHAUL_CASKET_STRIKE


# --- `EB-335`: the kit's own defence in act 2 (R246 pick 2) ---------------

def test_tide_wall_blocks_per_plan_of_the_whole_morning(overhaul):
    """TIDE WALL. "Gain 3 Block for each Plan the Bake-Kurage carries out this
    morning" -- the packet's own example is a three-Plan morning paying 9."""
    st = kokomi_state()
    for i in range(2):
        kokomi_plan.schedule(st, plan_card([{"op": "draw", "amount": 1}],
                                           cid=f"proto_kk_f{i}"))
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.BLOCK_PER_PLAN, "amount": 3}]))
    st.player.draw_pile = [plan_card([], cid=f"proto_kk_d{i}")
                           for i in range(5)]
    kokomi_plan.resolve_all(st)
    assert st.kk_plans_this_morning == 3
    assert st.player.block == 9


def test_tide_wall_does_not_care_where_in_the_queue_it_sits(overhaul):
    """THE ORDER CANNOT MOVE THE NUMBER, which is why the count is taken once
    at the drain rather than grown as the drain goes: a card whose Block
    depended on the order the player happened to write in would be unplayable
    to plan around."""
    blocks = []
    for slot in (0, 1, 2):
        st = kokomi_state()
        st.player.draw_pile = [plan_card([], cid=f"proto_kk_d{i}")
                               for i in range(6)]
        for i in range(3):
            clauses = ([{"op": kokomi_plan.BLOCK_PER_PLAN, "amount": 3}]
                       if i == slot else [{"op": "draw", "amount": 1}])
            kokomi_plan.schedule(st, plan_card(clauses, cid=f"proto_kk_f{i}"))
        kokomi_plan.resolve_all(st)
        blocks.append(st.player.block)
    assert blocks == [9, 9, 9]


def test_tide_wall_pays_nothing_on_a_morning_that_drained_nothing(overhaul):
    """A PRINTED NO-OP AND NOT A FAILURE: Change of Plans can carry this Plan
    out on a turn whose own morning was empty, and zero times three is the
    honest answer to "for each Plan carried out this morning"."""
    st = kokomi_state()
    kokomi_plan.roll_turn(st)                 # a fresh turn, nothing drained
    assert st.kk_plans_this_morning == 0
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.BLOCK_PER_PLAN, "amount": 3}]))
    kokomi_plan.resolve_front(st)
    assert st.player.block == 0


def test_tide_walls_block_is_powered(overhaul):
    """Rule 3, the half R246 pick 1 left alone: her Dexterity counts and Frail
    bites, exactly as they do on the flat planned `block` clause."""
    st = kokomi_state()
    st.player.powers["dexterity"] = 2
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.BLOCK_PER_PLAN, "amount": 3}]))
    kokomi_plan.resolve_all(st)
    assert st.player.block == 5           # 3 x 1 plan, then +2 Dexterity


def test_tide_wall_is_plan_only(overhaul):
    """The count it multiplies is a fact about a MORNING, so a now-line
    spelling would read a number that is zero every time it is asked. The
    engine refuses it from a body by name rather than resolving it quietly."""
    st = kokomi_state()
    card = Card(id="proto_kk_probe", name="probe", cost=1, type="skill",
                effects=[{"op": kokomi_plan.BLOCK_PER_PLAN, "amount": 3}])
    with pytest.raises(NotImplementedError, match="PLAN-ONLY"):
        effects.resolve_card(st, card)


def test_shell_guard_blocks_on_every_casket_strike(overhaul):
    """SHELL GUARD. "Until your next turn, whenever the Tamakushi Casket
    strikes, gain 3 Block." The seats watched the Casket strike five and six
    times a turn off the deck's own status lines."""
    enemy = make_enemy(hp=60)
    st = kokomi_state(enemies=[enemy])
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
    st.player.powers[kokomi_plan.SHELL_GUARD] = 3
    for _ in range(3):
        powers.apply_power(st, enemy, "weak", 1, applier=st.player)
    assert st.player.block == 9


def test_shell_guard_pays_nothing_without_the_casket(overhaul):
    """The card names the RELIC, which is what keeps it separable from The
    Clouds Like Waves Rippling one row over: that card pays per debuff
    APPLIED, this pays per Casket STRIKE."""
    enemy = make_enemy(hp=60)
    st = kokomi_state(enemies=[enemy])
    st.player.powers[kokomi_plan.SHELL_GUARD] = 3
    powers.apply_power(st, enemy, "weak", 1, applier=st.player)
    assert st.player.block == 0


def test_shell_guards_window_covers_the_morning_and_then_closes(overhaul):
    """"UNTIL YOUR NEXT TURN" INCLUDES THAT TURN'S MORNING, R246 pick 2's own
    sentence: "the morning's Plans that apply Weak strike it too, so the Block
    is there before the enemy swings". So the window is closed one step AFTER
    the drain, and everything after that is outside it."""
    enemy = make_enemy(hp=60)
    st = kokomi_state(enemies=[enemy])
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
    st.player.powers[kokomi_plan.SHELL_GUARD] = 3

    # The morning's own Weak Plan strikes the Casket inside the window.
    kokomi_plan.roll_turn(st)
    kokomi_plan.schedule(st, plan_card(
        [{"op": "apply_power", "power": "weak", "amount": 1,
          "target": "front_enemy"}]))
    kokomi_plan.resolve_all(st)
    assert st.player.block == 3

    # And then it is gone: a debuff applied later in the same turn pays
    # nothing.
    kokomi_plan.close_shell_guard(st)
    assert kokomi_plan.SHELL_GUARD not in st.player.powers
    powers.apply_power(st, enemy, "vulnerable", 1, applier=st.player)
    assert st.player.block == 3


def test_the_shell_guard_window_closes_on_a_morning_with_no_plans(overhaul):
    """The close is UNCONDITIONAL inside the arm's turn-start block, because
    `resolve_all` returns early on an empty queue -- a window that only closed
    on mornings with Plans in them would outlive its printed text."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.SHELL_GUARD] = 3
    kokomi_plan.resolve_all(st)               # nothing due
    kokomi_plan.close_shell_guard(st)
    assert kokomi_plan.SHELL_GUARD not in st.player.powers


def test_both_defensive_rows_load_and_smith(overhaul):
    """The two rows themselves, off the sheet: R246's 4/3 and 5/3, upgrading
    to 6/4 and 7/4."""
    from tier0.content import upgrades

    wall = loader.get_card("proto_kk_tide_wall")
    assert wall.rarity == "uncommon" and wall.cost == 1
    assert wall.effects == [{"op": "block", "amount": 4}]
    assert wall.plan == [{"op": kokomi_plan.BLOCK_PER_PLAN, "amount": 3}]
    up = upgrades.apply_upgrade(wall)
    assert up.effects[0]["amount"] == 6
    assert up.plan[0]["amount"] == 4

    guard = loader.get_card("proto_kk_shell_guard")
    assert guard.rarity == "uncommon" and guard.cost == 1
    assert guard.plan == []
    assert [e["amount"] for e in guard.effects] == [5, 3]
    up = upgrades.apply_upgrade(guard)
    assert [e["amount"] for e in up.effects] == [7, 4]


def test_damage_quarter_max_hp_rounds_down(overhaul):
    """Sango Isshin. ONE formula, read by the now-line and the planned half
    alike, so they cannot round differently (`KokomiRules.QuarterOfMaxHp`)."""
    enemy = make_enemy(hp=60)
    st = kokomi_state(enemies=[enemy], hp=81)
    assert kokomi_plan.quarter_of_max_hp(st) == 20
    carry_out(st, [{"op": "damage_quarter_max_hp", "target": "all_enemies"}])
    assert enemy.hp == 40


def test_sango_isshin_pays_the_quarter_only_after_a_plan_was_carried_out(overhaul):
    """[USER], live 2026-09-02: "It's fine if Rares are strong (see: Knife
    Trap), but this requires absolutely 0 setup or combo - it's just 'press
    button, delete act 1'." So the quarter is now the PAYOFF of a morning she
    planned for, and the card's floor is a plain 8 to one enemy."""
    a, b = make_enemy(hp=60, name="a"), make_enemy(hp=60, name="b")
    st = kokomi_state(enemies=[a, b], hp=80)
    card = loader.get_card("proto_kk_sango_isshin")

    # No Plan carried out this turn: the floor, aimed, and only at one enemy.
    assert st.kk_plan_carried_out_this_turn is False
    effects.resolve_card(st, card)
    assert (a.hp, b.hp) == (52, 60)

    # A Plan carried out this morning turns it into the wall.
    carry_out(st, [{"op": "draw", "amount": 1}])
    assert st.kk_plan_carried_out_this_turn is True
    effects.resolve_card(st, card)
    assert (a.hp, b.hp) == (32, 40)          # 20 apiece at 80 Max HP


def test_the_condition_is_written_wherever_a_plan_is_carried_out(overhaul):
    """"Carried out" is one event with two doors -- the morning queue and
    Change of Plans -- and the flag is written at the bottom of
    `_resolve_entry`, which both pass through. It is also a per-TURN fact: the
    boundary clears it.

    TWO DOORS AND NOT THREE SINCE `EB-570`: The Moon Overlooks the Waters was
    the third and is withdrawn, so WRITING a Plan now carries nothing out.
    """
    st = kokomi_state()
    kokomi_plan.schedule(st, plan_card([{"op": "draw", "amount": 1}]))
    assert st.kk_plan_carried_out_this_turn is False   # written, not carried
    kokomi_plan.resolve_front(st)                      # Change of Plans' door
    assert st.kk_plan_carried_out_this_turn is True

    kokomi_plan.roll_turn(st)
    assert st.kk_plan_carried_out_this_turn is False

    # And the morning is the other door.
    kokomi_plan.schedule(st, plan_card([{"op": "draw", "amount": 1}]))
    assert st.kk_plan_carried_out_this_turn is False   # written, not carried
    kokomi_plan.resolve_all(st)
    assert st.kk_plan_carried_out_this_turn is True


def test_damage_per_companion_last_turn_reads_last_turn(overhaul):
    """Chain of Command, and it is a READING the C# records: "last turn" is
    read at CARRY-OUT. The Plan is written on turn N and resolves at the top
    of N+1, by which time `combat._player_turn` has rolled the ledger -- so
    the count it finds is turn N's, the turn the player was looking at."""
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    st.companion_plays_this_turn = 3          # THIS turn: not what it reads
    st.companion_plays_last_turn = 2
    carry_out(st, [{"op": "damage_per_companion_last_turn", "amount": 4,
                    "target": "front_enemy"}])
    assert enemy.hp == 40 - 8


def test_chain_of_command_now_line_reads_companions_played_this_turn(overhaul):
    """`R250` pick 1 (round-4d sec.6, default): the now-line beside the Plan
    clause above, "Deal 3 damage for each Companion card you played this
    turn" -- the live half, read off the real sheet row through the ordinary
    `damage` + `amount_formula` rail (the same shape
    `test_inazuma_companion_overhaul.test_heartstopper_reads_the_swirls_this_turn`
    exercises for `swirls_this_turn`), not `damage_per_companion_last_turn`'s
    Plan-only handover."""
    st = kokomi_state(enemies=[make_enemy(hp=90, name="only")])
    st.companion_plays_this_turn = 2
    effects.resolve_card(st, loader.get_card("proto_kk_chain_of_command"))
    assert st.enemies[0].hp == 90 - 6


def test_applying_weak_and_vulnerable(overhaul):
    a, b = make_enemy(name="a"), make_enemy(name="b")
    st = kokomi_state(enemies=[a, b])
    carry_out(st, [{"op": "apply_power", "power": "weak", "amount": 2,
                    "target": "all_enemies"},
                   {"op": "apply_power", "power": "vulnerable", "amount": 1,
                    "target": "front_enemy"}])
    assert a.powers["weak"] == 2 and b.powers["weak"] == 2
    assert a.powers["vulnerable"] == 1 and "vulnerable" not in b.powers


# --- 4. NEREID'S ASCENSION -------------------------------------------------

def test_the_ascension_doubles_every_plan_in_the_morning(overhaul):
    """THE READING the C# records at `ResolveAll`: `carry_out_times` is asked
    INSIDE the drain loop, before each entry. Since `EB-492` the Rare is a
    POWER -- it is played, not planned -- so every Plan the morning holds is
    carried out twice."""
    enemy = make_enemy(hp=90)
    st = kokomi_state(enemies=[enemy])
    powers.apply_power(st, st.player, kokomi_plan.NEREIDS_ASCENSION, 1)
    kokomi_plan.schedule(st, plan_card([{"op": "damage", "amount": 5,
                                         "target": "front_enemy"}]))
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 90 - 10


def test_without_the_ascension_a_plan_is_carried_out_once(overhaul):
    """The other half of the same read, so the doubling is the power's and not
    the loop's."""
    enemy = make_enemy(hp=90)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, plan_card([{"op": "damage", "amount": 5,
                                         "target": "front_enemy"}]))
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 90 - 5


def test_a_second_ascension_doubles_and_never_triples(overhaul):
    """`EB-492`. The stack is a MARKER: `carry_out_times` reads whether the
    power is worn and never its amount, so a second copy of the Rare is a dead
    card rather than a third carry-out. `NereidsAscensionPower` says the same
    in its header."""
    enemy = make_enemy(hp=90)
    st = kokomi_state(enemies=[enemy])
    powers.apply_power(st, st.player, kokomi_plan.NEREIDS_ASCENSION, 1)
    powers.apply_power(st, st.player, kokomi_plan.NEREIDS_ASCENSION, 1)
    assert st.player.powers[kokomi_plan.NEREIDS_ASCENSION] == 2
    assert kokomi_plan.carry_out_times(st) == 2
    kokomi_plan.schedule(st, plan_card([{"op": "damage", "amount": 5,
                                         "target": "front_enemy"}]))
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 90 - 10


def test_the_ascension_lasts_the_fight(overhaul):
    """`EB-492`. It was a two-turn window installed by a Plan; it is a Power
    now, so nothing ticks it down and the turn boundary leaves it alone."""
    st = kokomi_state()
    powers.apply_power(st, st.player, kokomi_plan.NEREIDS_ASCENSION, 1)
    kokomi_plan.roll_turn(st)
    assert kokomi_plan.carry_out_times(st) == 2


def test_the_retired_plan_twice_clause_is_refused_at_load(overhaul):
    """`EB-492` RETIRED the clause rather than leaving it standing with no row
    to spell it: a `plan:` list that says `plan_twice` is a load failure on
    both sides, which is what "a clause outside this table is never an
    approximation" means."""
    assert "plan_twice" not in kokomi_plan.PLAN_KINDS
    assert kokomi_plan.plan_shape_reason([{"op": "plan_twice", "amount": 2}])


# --- 5. THE QUEUE ITSELF ---------------------------------------------------

def test_plans_are_carried_out_in_the_order_they_were_written(overhaul):
    st = kokomi_state()
    st.player.energy = 0
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                       cid="proto_kk_first"))
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 2}],
                                       cid="proto_kk_second"))
    kokomi_plan.resolve_all(st)
    order = [e["card"] for e in st.log if e["event"] == "plan_carried_out"]
    assert order == ["proto_kk_first", "proto_kk_second"]
    assert st.kk_plan_queue == []


def test_the_queue_is_drained_before_the_first_clause_runs(overhaul):
    """`ResolveAll`'s own rule: a Plan written DURING resolution waits for the
    next turn like every other one. Moon's Reflection's replay can reach a
    card that writes one, so this is not only a discipline."""
    st = kokomi_state()
    written = plan_card([{"op": "draw", "amount": 1}], cid="proto_kk_child")

    def child(_state, _entry, _clause, **_kwargs):
        kokomi_plan.schedule(st, written)

    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}]))
    original = kokomi_plan._resolve_clause
    kokomi_plan._resolve_clause = child
    try:
        kokomi_plan.resolve_all(st)
    finally:
        kokomi_plan._resolve_clause = original
    assert [e.card_id for e in st.kk_plan_queue] == ["proto_kk_child"]


def test_writing_a_plan_carries_nothing_out(overhaul):
    """`EB-570`. THE MOON OVERLOOKS THE WATERS IS WITHDRAWN, so writing is
    writing: the Plan is queued and the board does not move until the morning.

    THE ROW WAS THE ONLY WAY IN. "Plans also happen now" deleted the kit's one
    question rather than answering it -- rule 2 IS the delay -- and Battle
    Plan is why no smaller shape reached it: its Plan line is double its play
    line, so ANY now-copy takes the price off waiting. The withdrawal is
    Rolling Tide's (`EB-552`), one arm over: the row and its pins left the
    surface under R213 B's deletion rule.
    """
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, plan_card([{"op": "damage", "amount": 6,
                                         "target": "front_enemy"}]))
    assert enemy.hp == 40                      # nothing happened NOW
    assert len(st.kk_plan_queue) == 1          # it is queued, whole
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 34


def test_the_moon_overlooks_the_waters_is_off_the_surface(overhaul):
    """`EB-570` from the other side: the row is not offerable, its power is
    not a name this engine knows, and the pool moved by exactly one."""
    from tier0 import constants as C
    from tier0.content import loader

    assert "proto_kk_the_moon_overlooks_the_waters"         not in C.KOKOMI_OVERHAUL_POOL_IDS
    # FORTY after pool pass two (`EB-643`, R265) and `EB-649`
    # (round 23, Ebb Tide retired): seven rows that reach INTO the
    # queue. The count the row was filed against was 34, and what it
    # pins is the withdrawal, not the size -- so it moves with the
    # pool and the absence does not.
    assert len(C.KOKOMI_OVERHAUL_POOL_IDS) == 40
    assert not hasattr(kokomi_plan, "PLANS_ALSO_NOW")
    ids = {card.id for card in loader.prototype_cards()}
    assert "proto_kk_the_moon_overlooks_the_waters" not in ids


def test_change_of_plans_carries_out_the_front_and_removes_it(overhaul):
    """It LEAVES the queue, which is what 'carries out' means everywhere else
    in the arm -- one resolution moved forward, not a copy."""
    st = kokomi_state()
    st.player.energy = 0
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                       cid="proto_kk_first"))
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 2}],
                                       cid="proto_kk_second"))
    kokomi_plan.resolve_front(st)
    assert st.player.energy == 1
    assert [e.card_id for e in st.kk_plan_queue] == ["proto_kk_second"]


def test_change_of_plans_is_not_doubled_by_nereid(overhaul):
    """`CarryOutTimes` is read inside `ResolveAll`'s drain loop and nowhere
    else, so the Rare pays the MORNING and not this card. Taken from the C#'s
    shape literally rather than argued here."""
    st = kokomi_state()
    st.player.energy = 0
    powers.apply_power(st, st.player, kokomi_plan.NEREIDS_ASCENSION, 1)
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}]))
    kokomi_plan.resolve_front(st)
    assert st.player.energy == 1


def test_an_empty_queue_is_a_printed_no_op(overhaul):
    st = kokomi_state()
    kokomi_plan.resolve_front(st)
    kokomi_plan.resolve_all(st)
    assert counts(st)["plan_front_empty"] == 1


# --- 6. MOON'S REFLECTION --------------------------------------------------

def test_moons_reflection_takes_a_chosen_cards_own_plan_line(overhaul):
    """Two clause shapes out of one screen, split by the chosen card's face:
    a card that HAS a Plan line contributes that line verbatim."""
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    burned = plan_card([{"op": "damage", "amount": 7, "target": "front_enemy"}],
                       cid="proto_kk_burned")
    st.player.exhaust_pile = [burned]
    reflection = plan_card([], cid="proto_kk_reflection")
    kokomi_plan.schedule_from_exhaust(st, reflection)
    assert st.kk_plan_queue[0].clauses == burned.plan
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 33
    assert burned in st.player.exhaust_pile     # its LINE was taken, not it


def test_moons_reflection_replays_a_card_with_no_plan_line(overhaul):
    """The screen's other shape: a card with no Plan of its own is replayed
    WHOLE, and it leaves the exhaust pile before it resolves -- the
    `KurageMemory.Fire` argument, a card must not resolve out of a pile it is
    still a member of."""
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    burned = Card(id="proto_kk_plain", name="plain", cost=1, type="attack",
                  effects=[{"op": "damage", "amount": 6, "target": "enemy"}])
    st.player.exhaust_pile = [burned]
    kokomi_plan.schedule_from_exhaust(st, plan_card([], cid="proto_kk_ref"))
    assert st.kk_plan_queue[0].clauses == [{"op": kokomi_plan.REPLAY_EXHAUSTED}]
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 34
    assert burned not in st.player.exhaust_pile


def test_an_empty_exhaust_pile_is_a_no_op_and_not_a_screen(overhaul):
    st = kokomi_state()
    kokomi_plan.schedule_from_exhaust(st, plan_card([], cid="proto_kk_ref"))
    assert st.kk_plan_queue == []
    assert counts(st)["plan_from_exhaust_empty"] == 1


# --- 7. THE PLAN BUS: Treatise and Song of Pearls --------------------------

def test_treatise_draws_once_per_plan_and_not_once_per_clause(overhaul):
    """'When the jellyfish carries out a Plan' is once per ENTRY. War Council
    prints two clauses and is ONE Plan, which is what its face says -- "Deal 4
    damage to every enemy AND apply 1 Weak to each" is one sentence."""
    st = kokomi_state()
    st.player.draw_pile = [plan_card([], cid=f"proto_kk_f{i}")
                           for i in range(6)]
    st.player.powers[kokomi_plan.TREATISE] = 1
    carry_out(st, [{"op": "energy", "amount": 1},
                   {"op": "energy", "amount": 1}])
    assert len(st.player.hand) == 1


def test_song_of_pearls_blocks_once_per_plan(overhaul):
    st = kokomi_state()
    st.player.powers[kokomi_plan.SONG_OF_PEARLS] = 3
    carry_out(st, [{"op": "energy", "amount": 1},
                   {"op": "energy", "amount": 1}])
    assert st.player.block == 3


def test_two_plans_in_one_morning_pay_the_bus_once(overhaul):
    """[USER], live 2026-09-02: "Treatise looks too good (one draw per turn if
    a Plan fired might be ok; one draw per Plan is too abuseable)", and
    "Likewise" of Song of Pearls. TWO Plans carried out in one morning, which
    is the ordinary case the cards were written for, and both pay once."""
    st = kokomi_state()
    st.player.draw_pile = [plan_card([], cid=f"proto_kk_f{i}")
                           for i in range(6)]
    st.player.powers[kokomi_plan.TREATISE] = 1
    st.player.powers[kokomi_plan.SONG_OF_PEARLS] = 3
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                       cid="proto_kk_a"))
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                       cid="proto_kk_b"))
    kokomi_plan.resolve_all(st)
    assert len(st.player.hand) == 1
    assert st.player.block == 3
    # And it is a CAP and not a one-shot: the next turn pays again.
    kokomi_plan.roll_turn(st)
    st.player.block = 0
    carry_out(st, [{"op": "energy", "amount": 1}])
    assert len(st.player.hand) == 2
    assert st.player.block == 3


def test_the_bus_pays_change_of_plans_early_resolution_too(overhaul):
    """The C#: "the notify at the bottom is the only place that fires", so
    every door onto a carry-out pays the bus. Since `EB-570` withdrew The Moon
    Overlooks the Waters, Change of Plans is the mid-turn door that pin is
    about.

    SINCE 2026-09-02 THE TURN IS THE CAP, so what "pays them too" means is
    that the early resolution is what CLAIMS the turn's payout when it happens
    first -- the morning that follows it in the same turn adds nothing, and the
    NEXT turn pays again. The alternative reading, a bus that skipped the early
    resolution, would make Change of Plans turn Song of Pearls off for a turn.
    """
    st = kokomi_state()
    st.player.powers[kokomi_plan.SONG_OF_PEARLS] = 3
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                       cid="proto_kk_a"))
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                       cid="proto_kk_b"))
    kokomi_plan.resolve_front(st)               # Change of Plans' door
    assert st.player.block == 3                 # the early resolution
    kokomi_plan.resolve_all(st)
    assert st.player.block == 3                 # the morning's is the cap
    kokomi_plan.roll_turn(st)
    carry_out(st, [{"op": "energy", "amount": 1}])
    assert st.player.block == 6                 # a new turn, a new payout


# --- 7b. THE TEMPO SHELF (round 9 pick 1, default applied 2026-09-04) ------
#
# TWO ROWS AND NOT FOUR: Held Tide and Tidal Rhythm were withdrawn on the R253
# charter audit and are not on the surface, so `kk_tidal_rhythm` is not a power
# this engine knows and nothing on the shelf Retains.

def test_plans_held_is_the_queue_and_not_the_morning(overhaul):
    """"Holds" is WRITTEN AND NOT YET CARRIED OUT, so it is `kk_plan_queue` --
    `kk_plans_this_morning` keeps the drained morning's depth and would answer
    for Plans the jellyfish no longer holds. NO ROW SPENDS THIS COUNT since
    R257 took it off Tide Chart; the C# twin `KokomiPlan.PlansHeld` is still
    read, by Change of Plans' unplayable reason, and reads `Pending` for the
    same reason this reads the queue."""
    st = kokomi_state()
    assert effects._runtime_count(st, "plans_held") == 0
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                       cid="proto_kk_a"))
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                       cid="proto_kk_b"))
    assert effects._runtime_count(st, "plans_held") == 2
    kokomi_plan.resolve_all(st)
    assert st.kk_plans_this_morning == 2        # the morning, still two
    assert effects._runtime_count(st, "plans_held") == 0     # held, none


def _tide_chart_morning(st, plans, card):
    """Play `card` this turn, bank `plans` Plans, and take the next turn's
    start in `combat._player_turn`'s order: the roll, the morning, the
    payment. Returns the hand the morning left."""
    for i in range(plans):
        kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                           cid=f"proto_kk_p{i}"))
    effects.resolve_card(st, card)
    assert st.player.hand == []                 # THE PLAY DRAWS NOTHING
    kokomi_plan.roll_turn(st)
    kokomi_plan.resolve_all(st)
    kokomi_plan.pay_tide_charts(st)
    return st.player.hand


def _tide_chart_state():
    st = kokomi_state()
    st.player.draw_pile = [plan_card([], cid=f"proto_kk_f{i}")
                           for i in range(6)]
    return st


def test_tide_chart_pays_the_morning_after_for_what_was_carried_out(overhaul):
    """`EB-478`, R257: "Next turn, after the Bake-Kurage carries out its
    Plans, draw 1 card for each." The play writes a promise and draws nothing;
    the morning after pays for the Plans that were actually carried out.

    THE OLD ROW READ THE QUEUE AT PLAY TIME and drew zero on three plays out
    of four (Kokomi r15), because a seat plays its cheap cards before it
    writes its Plans -- which is what this test now writes in the order that
    used to pay nothing. `KokomiPlan.PromiseDraw` / `PayPromisedDraws`."""
    card = loader._card_prototype("proto_kk_tide_chart")
    assert len(_tide_chart_morning(_tide_chart_state(), 2, card)) == 2
    # NONE CARRIED OUT DRAWS NOTHING: the base row is worth exactly the Plans
    # the jellyfish had, and an empty morning had none.
    assert _tide_chart_morning(_tide_chart_state(), 0, card) == []


def test_tide_chart_upgraded_adds_one_flat_card(overhaul):
    """"Draw 1 more": one card on top of the one per Plan carried out, which
    is the ONLY reading that leaves the upgraded row live on an empty morning.
    tier0 bumps the op's `amount` (`upgrades.apply_upgrade`'s `tide_draw`);
    the C# reads the same half off `IsUpgraded` in `PromiseDraw`."""
    from tier0.content import upgrades

    up = upgrades.apply_upgrade(loader.get_card("proto_kk_tide_chart"))
    assert up.effects == [{"op": "draw_after_plans", "amount": 1, "per": 1}]
    assert len(_tide_chart_morning(_tide_chart_state(), 2, up)) == 3
    assert len(_tide_chart_morning(_tide_chart_state(), 0, up)) == 1


def test_a_tide_chart_promise_is_paid_once(overhaul):
    """The promise is cleared BY the payment, so a second morning with no new
    Tide Chart draws nothing -- `pay_tide_charts` clears before it draws, and
    `PayPromisedDraws` removes the entry before its `CardPileCmd.Draw`."""
    st = _tide_chart_state()
    card = loader._card_prototype("proto_kk_tide_chart")
    assert len(_tide_chart_morning(st, 2, card)) == 2
    st.player.hand.clear()
    kokomi_plan.roll_turn(st)
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                       cid="proto_kk_q"))
    kokomi_plan.resolve_all(st)
    kokomi_plan.pay_tide_charts(st)
    assert st.player.hand == []


def test_ripple_pays_block_now_and_energy_and_block_on_the_plan(overhaul):
    """A cheap Plan whose now-line is worth playing (2 Block for 0) and whose
    Plan pays tempo (1 Energy and 4 Block)."""
    card = loader._card_prototype("proto_kk_ripple")
    st = kokomi_state()
    st.player.energy = 0
    effects.resolve_card(st, card)
    assert st.player.block == 2
    st.player.block = 0
    kokomi_plan.schedule(st, card)
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 1
    assert st.player.block == 4


# --- 8. THE TAMAKUSHI CASKET ----------------------------------------------

def casket_state(**kw):
    st = kokomi_state(**kw)
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
    return st


def test_the_casket_strikes_on_a_debuff_she_applies(overhaul):
    enemy = make_enemy(hp=40)
    st = casket_state(enemies=[enemy])
    powers.apply_power(st, enemy, "weak", 1, applier=st.player)
    assert enemy.hp == 40 - C.KOKOMI_OVERHAUL_CASKET_STRIKE
    assert counts(st)["casket_strike"] == 1


def test_the_casket_strike_is_the_pets_and_carries_no_strength(overhaul):
    """A READING the C# records: "the slice says 'it strikes that enemy for
    2', so the applier handed to the shared elemental pipeline is the PET. A
    pet carries no Strength, so the 2 is a flat 2" -- which is what keeps this
    the relic's number instead of the best Strength payoff in her pool, now
    that draft 6 gives her Strength back."""
    enemy = make_enemy(hp=40)
    st = casket_state(enemies=[enemy])
    st.player.powers["strength"] = 5
    powers.apply_power(st, enemy, "weak", 1, applier=st.player)
    assert enemy.hp == 40 - C.KOKOMI_OVERHAUL_CASKET_STRIKE


def test_the_casket_strike_is_otherwise_a_real_hit(overhaul):
    """The C#: "Block, Vulnerable, the aura and the reaction all apply, because it goes
    through the same ElementalHit funnel every other non-attack hit in this mod
    does." Block first, then Vulnerable, then the aura."""
    enemy = make_enemy(hp=40)
    enemy.block = 1
    st = casket_state(enemies=[enemy])
    powers.apply_power(st, enemy, "vulnerable", 1, applier=st.player)
    assert enemy.block == 0
    assert enemy.aura == "hydro"
    # 2 Hydro, amplified by the Vulnerable that provoked it, minus 1 Block.
    assert enemy.hp < 40


def test_the_casket_does_not_answer_its_own_answer(overhaul):
    """THE LATCH IS NOT PARANOIA (the C#'s own words): the answer is a Hydro
    hit, a Hydro hit into a Cryo aura Freezes, and in a boss room Frozen is
    Vulnerable -- a debuff she applied to an enemy. Without the latch the relic
    would answer its own answer until the stack ran out."""
    enemy = make_enemy(hp=60, is_boss=True)
    enemy.aura = "cryo"
    enemy.aura_turns_left = 3
    st = casket_state(enemies=[enemy])
    powers.apply_power(st, enemy, "weak", 1, applier=st.player)
    assert counts(st)["casket_strike"] == 1


def test_the_casket_ignores_a_debuff_that_is_not_hers(overhaul):
    """Two of the four clauses at once: her own Weak is not a debuff she
    applied to an ENEMY, and in co-op the other seat's Weak is not HERS."""
    enemy = make_enemy(hp=40)
    st = casket_state(enemies=[enemy])
    powers.apply_power(st, st.player, "weak", 1, applier=enemy)
    powers.apply_power(st, enemy, "weak", 1, applier=enemy)
    assert enemy.hp == 40
    assert counts(st)["casket_strike"] == 0


def test_a_debuff_ticking_down_is_not_one_being_applied(overhaul):
    enemy = make_enemy(hp=40)
    st = casket_state(enemies=[enemy])
    powers.apply_power(st, enemy, "weak", 0, applier=st.player)
    assert enemy.hp == 40


def test_a_frozen_reaction_feeds_the_casket(overhaul):
    """Frozen is a POWER in the mod and a FIELD here, so it is the one debuff
    application that does not reach `powers.apply_power`. The C# names it as a
    feeder, so `reactions.resolve_hit` raises the event by hand."""
    from tier0.engine import reactions
    enemy = make_enemy(hp=40)
    enemy.aura = "cryo"
    enemy.aura_turns_left = 3
    st = casket_state(enemies=[enemy])
    reactions.resolve_hit(st, enemy, "hydro", 0, "probe")
    assert counts(st)["casket_strike"] == 1
    assert kokomi_plan.has_debuff(enemy) is True


def test_the_clouds_like_waves_pays_per_application_not_per_stack(overhaul):
    """The C#: "War Council's 'apply 1 Weak to each' over three enemies is three
    applications and three payouts; one card applying 2 Weak to one enemy is
    one." It shares the Casket's one predicate and takes no latch, which the
    C# power does not either."""
    a, b = make_enemy(name="a"), make_enemy(name="b")
    st = kokomi_state(enemies=[a, b])
    st.player.powers[kokomi_plan.CLOUDS_LIKE_WAVES] = 2
    powers.apply_power(st, a, "weak", 2, applier=st.player)
    assert st.player.block == 2
    powers.apply_power(st, b, "weak", 1, applier=st.player)
    assert st.player.block == 4


# --- 9. THE COMPANION HOOKS ------------------------------------------------

def companion_card(cid="proto_kk_ally"):
    return Card(id=cid, name="ally", cost=1, type="skill", role_c="applier")


def test_the_generals_banner_weaks_the_front_enemy_once_a_turn(overhaul):
    """[USER], live 2026-09-02: "The General's Banner applies a LOT of Weak.
    Probably too strong." TWO Companion plays in one turn apply ONE Weak, and
    the next turn applies one more -- a cap, not a one-shot.

    The front enemy is `front_enemy`'s, the same reader a planned hit uses, so
    "the front enemy" means one thing in this arm and is defined once."""
    front, back = make_enemy(name="front"), make_enemy(name="back")
    st = kokomi_state(enemies=[front, back])
    st.player.powers[kokomi_plan.GENERALS_BANNER] = 1
    card = companion_card()
    kokomi_plan.note_companion_played(st, card)
    kokomi_plan.note_companion_played(st, card)
    assert front.powers["weak"] == 1
    assert "weak" not in back.powers

    kokomi_plan.roll_turn(st)
    kokomi_plan.note_companion_played(st, card)
    assert front.powers["weak"] == 2


def test_the_banner_ignores_a_card_that_is_not_a_companion(overhaul):
    enemy = make_enemy()
    st = kokomi_state(enemies=[enemy])
    st.player.powers[kokomi_plan.GENERALS_BANNER] = 1
    kokomi_plan.note_companion_played(st, plan_card([]))
    assert "weak" not in enemy.powers


def test_the_ledger_rolls_this_turns_count_into_last_turns(overhaul):
    """`KokomiOverhaulLedger.RollTo`'s handover, at the one place the per-turn
    counter moves."""
    st = kokomi_state()
    st.companion_plays_this_turn = 4
    kokomi_plan.roll_turn(st)
    assert st.companion_plays_last_turn == 4


# --- 10. RALLY AND CLEANSING WAVE ------------------------------------------

def test_rally_is_one_stack_always(overhaul):
    """The C#: "two Rallies in one turn do not make the next Companion cost two less,
    because the card says 'costs 1 less' and not 'costs 1 less per Rally'."""
    st = kokomi_state()
    kokomi_plan.next_companion_discount(st)
    kokomi_plan.next_companion_discount(st)
    assert st.player.powers[kokomi_plan.NEXT_COMPANION_DISCOUNT] == 1


def test_rally_discounts_the_next_companion_and_is_then_spent(overhaul):
    """A DISCOUNT, NOT A ZEROING -- draft 6's change from draft 2's Vanguard --
    and it is consumed by the play that spends it."""
    from tier0.engine.combat import card_cost
    st = kokomi_state()
    ally = companion_card()
    ally.cost = 2
    assert card_cost(st, ally) == 2
    kokomi_plan.next_companion_discount(st)
    assert card_cost(st, ally) == 2 - C.KOKOMI_OVERHAUL_RALLY_DISCOUNT
    kokomi_plan.spend_companion_discount(st, ally)
    assert card_cost(st, ally) == 2


def test_cleansing_wave_removes_the_first_standing_debuff(overhaul):
    """A READING, recorded because the card says "a debuff" and not "the worst
    one": the FIRST on her power list goes, which is the oldest one standing,
    and the card offers no choice."""
    st = kokomi_state()
    st.player.powers["weak"] = 2
    st.player.powers["vulnerable"] = 3
    kokomi_plan.remove_one_debuff(st)
    assert "weak" not in st.player.powers
    assert st.player.powers["vulnerable"] == 3


def test_undertow_reads_a_standing_debuff(overhaul):
    enemy = make_enemy()
    st = kokomi_state(enemies=[enemy])
    assert kokomi_plan.has_debuff(enemy) is False
    enemy.powers["vulnerable"] = 1
    assert kokomi_plan.has_debuff(enemy) is True


# --- 11. THE PILOT RULE ----------------------------------------------------

def test_an_empty_now_line_always_plans(overhaul):
    """Half one of the sim's own rule: there is nothing to give up."""
    st = kokomi_state(enemies=[make_enemy(intents=ATTACKER)])
    assert kokomi_plan.plan_aimed_at_pet(
        st, plan_card([{"op": "draw", "amount": 1}])) is True


def test_a_card_with_a_now_line_plans_only_when_nothing_intends_to_attack(
        overhaul):
    """Half two, and it is the SIM's rule and not a design claim: a Plan trades
    this turn for next turn, so take the trade when this turn is cheap. The
    brief says nothing about when to plan -- a human decides, and this engine
    has no human."""
    card = plan_card([{"op": "block", "amount": 3}],
                     effects_=[{"op": "block", "amount": 3}])
    attacking = kokomi_state(enemies=[make_enemy(intents=ATTACKER)])
    assert kokomi_plan.plan_aimed_at_pet(attacking, card) is False
    quiet = kokomi_state(enemies=[make_enemy(intents=BLOCKER)])
    assert kokomi_plan.plan_aimed_at_pet(quiet, card) is True
    mixed = kokomi_state(enemies=[make_enemy(name="a", intents=BLOCKER),
                                  make_enemy(name="b", intents=ATTACKER)])
    assert kokomi_plan.plan_aimed_at_pet(mixed, card) is False


def test_a_card_with_no_plan_line_never_plans(overhaul):
    st = kokomi_state(enemies=[make_enemy(intents=BLOCKER)])
    plain = Card(id="proto_kk_plain", name="x", cost=1, type="skill",
                 effects=[{"op": "block", "amount": 3}])
    assert kokomi_plan.plan_aimed_at_pet(st, plain) is False


def test_the_pilots_forecast_and_the_play_read_the_same_function(overhaul):
    """The Track C.2 lesson. `policy._active_effects` swaps in the Plan line
    for a pet-bound play by asking `plan_aimed_at_pet`, which is the SAME pure
    function `effects._resolve_card_bound` asks a moment later -- so the half
    the pilot priced is the half that runs.

    EB-311 PUT A PRICE ON THE TURN OF DELAY, so the planned half is now
    forecast at `C.PLAN_DELAY_DISCOUNT` of its face and the now-line still at
    face. The assertion is written against the constant rather than against
    6.75, because what it pins is WHICH HALF is read and that the delay is
    charged at all -- the dial's value is an instrument question and moving it
    should move this test with it, not break it."""
    from tier0.pilot import policy
    quiet = kokomi_state(enemies=[make_enemy(intents=BLOCKER)])
    card = plan_card([{"op": "damage", "amount": 9, "target": "front_enemy"}],
                     effects_=[{"op": "damage", "amount": 4,
                                "target": "enemy"}])
    assert policy._expected_damage(quiet, card) == 9 * C.PLAN_DELAY_DISCOUNT
    attacking = kokomi_state(enemies=[make_enemy(intents=ATTACKER)])
    assert policy._expected_damage(attacking, card) == 4


def test_a_play_on_the_pet_does_none_of_its_now_line(overhaul):
    """The mod's `OnPlay` schedules and RETURNS. The cost is already paid and
    the card is already out of hand, which is the whole shape of rule 2."""
    enemy = make_enemy(hp=40, intents=BLOCKER)
    st = kokomi_state(enemies=[enemy])
    card = plan_card([{"op": "draw", "amount": 1}],
                     effects_=[{"op": "damage", "amount": 4,
                                "target": "enemy"}])
    effects.resolve_card(st, card)
    assert enemy.hp == 40
    assert len(st.kk_plan_queue) == 1


# --- 12. THE RESOLUTION POINT ---------------------------------------------

def test_planned_block_and_energy_survive_the_turn_setup(overhaul):
    """THE HOOK IS A READING, and it is the mod's: `AfterPlayerTurnStart`, NOT
    the pre-draw point the slice's sec.2 prose asks for. There is no broadcast
    between the energy reset and the draw, so a Plan resolved "before the draw"
    resolves before the BLOCK CLEAR and the ENERGY RESET too -- and Read the
    Field's planned Block, Coral Bulwark's, Cleansing Wave's and Ripple's
    planned Energy would all be wiped by the setup that follows them.

    RIPPLE AND NOT BATTLE PLAN SINCE `EB-655`: pool pass three took the
    `energy` clause off Battle Plan (it paid the write back its own cost), so
    the Energy half of this claim is read off the row that still prints one.

    This is that claim made falsifiable: a Plan written on turn N leaves Block
    and Energy standing when the pilot gets to decide on turn N+1.
    """
    ids = ["proto_kk_read_the_field"] * 4 + ["proto_kk_ripple"] * 4
    player = loader.build_player_from_ids("kokomi", ids)
    seen = {}

    def pilot(state):
        seen.setdefault(state.turn, (state.player.block, state.player.energy))
        for card in state.player.hand:
            if card.plan:
                return card
        return None

    run_fight(player, [make_enemy(hp=400, intents=BLOCKER)], pilot, seed=3)
    # Turn 2 opens with BOTH: the Block turn 1's Read the Field Plans wrote
    # (8 apiece, past a block clear that would have zeroed it) and the Energy
    # its Ripple Plans wrote (1 apiece, past an energy reset that would
    # have overwritten it). Under the pre-draw hook the slice's prose asks for,
    # both of these read exactly the turn's own defaults.
    block, energy = seen[2]
    assert block >= 8
    assert energy > C.BASE_ENERGY_PER_TURN


# --- 13. THE SMOKE: nothing refuses to resolve ----------------------------

REFUSALS = (NotImplementedError, ValueError, KeyError)


def test_the_starter_deck_runs_a_handful_of_fights_without_refusing(overhaul):
    """THE ARM, RUN. Ten cards, five encounters, five seeds -- and the only
    assertion is that nothing raised and the fight ended. `_op_kokomi_-
    overhaul_off` and `_op_kokomi_plan_only` both raise `NotImplementedError`,
    so a verb this branch forgot to build cannot pass silently.
    """
    pilot = make_pilot(loader.pilot_weights("priest"))
    encounters = ["punisher", "swarm", "attrition", "burst_check", "tank_boss"]
    planned = 0
    for encounter in encounters:
        for seed in (3, 7, 11, 23, 41):
            board = loader.build_encounter(encounter)
            state = run_fight(loader.build_player("kokomi"), board, pilot,
                              seed=seed)
            assert state.over
            planned += counts(state)["plan_carried_out"]
    # AND THE ARM ACTUALLY USED ITS ONE RULE. A smoke that only proved nothing
    # raised would pass just as well on a build where the pilot never planned
    # at all, which is the failure this line exists to make visible.
    assert planned > 0


def test_every_row_in_her_pool_resolves(overhaul):
    """THE OTHER HALF OF THE SMOKE, and the one that reaches the verbs a
    starter deck never prints: Change of Plans, Moon's Reflection, Rally, the
    two Rares, Undertow's predicate. Every one of the 26 offerable rows is
    played by hand against a live board, and the assertion is that none of them
    refuses -- the shape `test_the_new_ops_refuse_to_resolve` used to assert
    from the other side.
    """
    for cid in C.KOKOMI_OVERHAUL_POOL_IDS + C.KOKOMI_OVERHAUL_STARTER_IDS:
        card = loader.get_card(cid)
        state = kokomi_state(enemies=[make_enemy(hp=200, name="a"),
                                      make_enemy(hp=200, name="b")])
        state.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
        state.mi_entry_hp = 80
        # R242: her basics are the BASE GAME's Strike and Defend, so the pile
        # a draw-reading row looks at is built from `strike`.
        state.player.draw_pile = [loader.get_card("strike")
                                  for _ in range(5)]
        state.player.exhaust_pile = [loader.get_card("proto_kk_salt_line")]
        state.kk_plan_queue = []
        kokomi_plan.schedule(state, loader.get_card("proto_kk_ambush"))
        state.card_aim = state.enemies[0]
        state.card_aim_bound = True
        try:
            effects.resolve_card(state, card)
            kokomi_plan.resolve_all(state)
        except REFUSALS as exc:                 # pragma: no cover - diagnostic
            pytest.fail(f"{cid} refused to resolve: {exc!r}")


def test_a_plan_only_clause_refuses_from_a_body(overhaul):
    """`damage_per_companion_last_turn` and its two siblings are legal inside
    a `plan:` list and nowhere else. They stay in `effects.OPS` because the
    loader validates a `plan:` list through the same vocabulary check the body
    takes; reaching one from a BODY is a defect, and it says so."""
    st = kokomi_state()
    for op in sorted(kokomi_plan.PLAN_ONLY_OPS):
        card = Card(id="proto_kk_probe", name="probe", cost=1, type="skill",
                    effects=[{"op": op, "amount": 1}])
        with pytest.raises(NotImplementedError, match="PLAN-ONLY"):
            effects.OPS[op](st, card.effects[0], card)


# --- 12. THE PLAN LINE UPGRADES (`EB-315`) ---------------------------------
#
# [USER], playing the arm: *"Plan cards often seem to lack upgrades, though
# (Kurage's Oath, Ambush) - I thought we had a test for that?"* The
# Prototype-stage rule read a row's `effects:` and nothing else, so a
# Plan-ONLY row had no printed number it could see and a TWO-LINE row upgraded
# only its now-line -- `Feint+` dealt 6+3 when played and a literal 9 at dawn,
# for ever. The rule reads both printed lines now, under `plan_*` keys, and
# these pin the applier half: which clause moves, and that nothing else does.
#
# The C# twin is `gen_klee_cards.plan_var_effects` (one table, imported from
# `upgrades.PLAN_DELTA_OPS`, so neither engine can bind a key to a different
# clause) and `tier0/tests/test_prototype_surface.py` holds every arm row to
# having a path at all.

def test_a_plan_only_rows_upgrade_moves_its_plan_number(monkeypatch):
    from tier0.content import upgrades

    monkeypatch.setattr(upgrades, "_upgrade_index",
                        lambda: {"proto_kk_probe": {"plan_damage": 3}})
    card = plan_card([{"op": "damage", "amount": 12, "target": "front_enemy"}])
    upgraded = upgrades.apply_upgrade(card)
    assert upgraded.id == "proto_kk_probe+"
    assert upgraded.plan == [{"op": "damage", "amount": 15,
                              "target": "front_enemy"}]


def test_a_two_line_row_upgrades_both_lines(monkeypatch):
    """The half that LOOKED fine: the now-line moved, the plan clause did
    not, and only a played turn could tell."""
    from tier0.content import upgrades

    monkeypatch.setattr(
        upgrades, "_upgrade_index",
        lambda: {"proto_kk_probe": {"damage": 3, "plan_damage": 3}})
    card = plan_card([{"op": "damage", "amount": 10, "target": "front_enemy"}],
                     effects_=[{"op": "damage", "amount": 6,
                                "target": "enemy"}])
    upgraded = upgrades.apply_upgrade(card)
    assert upgraded.effects[0]["amount"] == 9
    assert upgraded.plan[0]["amount"] == 13


def test_a_plan_key_binds_only_the_first_clause_of_its_op(monkeypatch):
    """The one-owner rule every other key keeps, one printed line over: the
    C# declares ONE var per key and the face prints it once, so a delta that
    moved every matching clause would upgrade numbers the card never shows."""
    from tier0.content import upgrades

    monkeypatch.setattr(upgrades, "_upgrade_index",
                        lambda: {"proto_kk_probe": {"plan_power_amount": 1}})
    card = plan_card([
        {"op": "apply_power", "power": "vulnerable", "amount": 1,
         "target": "front_enemy"},
        {"op": "apply_power", "power": "weak", "amount": 1,
         "target": "front_enemy"}])
    upgraded = upgrades.apply_upgrade(card)
    assert [c["amount"] for c in upgraded.plan] == [2, 1]


def test_a_plan_key_on_a_row_with_no_such_clause_raises(monkeypatch):
    """Loud, not silent -- R24's no-partial-upgrades discipline. The codegen
    refuses the same row at `upgrade_plan` ("has no matching effect on this
    card"), so neither engine can ship the half-upgrade."""
    from tier0.content import upgrades

    monkeypatch.setattr(upgrades, "_upgrade_index",
                        lambda: {"proto_kk_probe": {"plan_block": 3}})
    card = plan_card([{"op": "damage", "amount": 8, "target": "front_enemy"}])
    with pytest.raises(ValueError, match="found no matching effect"):
        upgrades.apply_upgrade(card)


def test_the_upgraded_plan_is_what_the_jellyfish_carries_out(overhaul,
                                                             monkeypatch):
    """End to end in this engine, which is the whole point of the key: the
    queue is written from the card's OWN clauses, so a smithed card schedules
    the smithed number. The mod's twin is `PlanClauses` being a PROPERTY that
    reads `DynamicVars["PlanDamage"].IntValue` -- before `EB-315` it carried a
    literal, and `Feint+` dealt its base number at dawn for ever."""
    from tier0.content import upgrades

    monkeypatch.setattr(upgrades, "_upgrade_index",
                        lambda: {"proto_kk_probe": {"plan_damage": 3}})
    target = make_enemy(hp=60, name="front")
    st = kokomi_state(enemies=[target])
    card = upgrades.apply_upgrade(
        plan_card([{"op": "damage", "amount": 12, "target": "front_enemy"}]))
    kokomi_plan.schedule(st, card)
    kokomi_plan.resolve_all(st)
    assert target.hp == 60 - 15


# --- 6b. CRYSTAL COLLAPSE: the Plan that HOLDS a card (R236) ---------------
#
# `proto_mi_gorou_crystal_collapse`, the Inazuma workshop's one Personal:
# "Plan: play a copy of the last other Companion card you played this turn."
# The capture happens when the Plan is WRITTEN and the copy is played at the
# morning, which is the whole shape of the card -- so the two halves are
# pinned separately below.


def a_companion(cid, name, damage=6):
    """A Companion card that hits, so a copy of it is visible in the HP."""
    return Card(id=cid, name=name, cost=1, type="attack", role_c="applier",
                effects=[{"op": "damage", "amount": damage,
                          "target": "enemy"}])


def crystal_collapse():
    return Card(id="proto_mi_gorou_crystal_collapse",
                name="Gorou — Crystal Collapse", cost=1, type="skill",
                role_c="trigger",
                plan=[{"op": kokomi_plan.PLAY_COPY_OF_COMPANION}])


def play_companions(state, cards):
    """`combat._finish_play`'s half of a Companion play, which is where the
    arm records one -- and it runs BEFORE the card's body, which is why the
    card writing the Plan is already on the list when it asks."""
    for card in cards:
        kokomi_plan.note_companion_played(state, card)


def test_crystal_collapse_captures_the_last_other_companion(overhaul):
    """"The last OTHER Companion card", and the word other is load-bearing:
    `combat._finish_play` records the play before the body resolves, so this
    card is already the last one on the list when its own Plan is written."""
    st = kokomi_state(enemies=[make_enemy(hp=40)])
    first = a_companion("proto_mi_a", "Gorou — Inuzaka")
    second = a_companion("proto_mi_b", "Gorou — Juuga")
    card = crystal_collapse()
    play_companions(st, [first, second, card])
    kokomi_plan.schedule(st, card)
    entry = st.kk_plan_queue[0]
    assert entry.card is second
    assert entry.label == "Crystal Collapse: Gorou — Juuga"


def test_a_non_companion_play_is_not_what_it_catches(overhaul):
    """The face says Companion card, so an ordinary Skill played after one
    does not move what the Plan will hold."""
    st = kokomi_state(enemies=[make_enemy(hp=40)])
    comp = a_companion("proto_mi_a", "Gorou — Juuga")
    plain = Card(id="proto_kk_plain", name="plain", cost=1, type="skill")
    card = crystal_collapse()
    play_companions(st, [comp, plain, card])
    kokomi_plan.schedule(st, card)
    assert st.kk_plan_queue[0].card is comp


def test_a_turn_with_no_other_companion_writes_an_empty_plan(overhaul):
    """THE EMPTY CASE IS WRITTEN DOWN, not refused: the face says what it does
    with nothing, and a Plan that silently declined to queue would make the
    strip lie about the queue's depth."""
    st = kokomi_state(enemies=[make_enemy(hp=40)])
    card = crystal_collapse()
    play_companions(st, [card])
    kokomi_plan.schedule(st, card)
    entry = st.kk_plan_queue[0]
    assert entry.card is None
    assert entry.label == "Crystal Collapse: nothing"
    kokomi_plan.resolve_all(st)
    assert counts(st)["plan_copy_empty"] == 1
    assert counts(st)["plan_copy"] == 0
    assert st.enemies[0].hp == 40


def test_the_morning_plays_a_free_copy_and_keeps_the_original(overhaul):
    """A COPY, which is the difference from Moon's Reflection's replay: the
    card it caught stays where the first play sent it, and the copy is
    exhausted after so the deck is not one card longer either."""
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    caught = a_companion("proto_mi_b", "Gorou — Juuga")
    st.player.discard_pile = [caught]
    card = crystal_collapse()
    play_companions(st, [caught, card])
    kokomi_plan.schedule(st, card)
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 34                       # the copy hit for its 6
    assert caught in st.player.discard_pile     # the original never moved
    copies = [c for c in st.player.exhaust_pile if c.id == "proto_mi_b"]
    assert len(copies) == 1
    assert copies[0] is not caught


def test_the_copy_is_doubled_by_nereids_ascension(overhaul):
    """Nereid's Ascension carries out the drain's first Plan twice, and this
    Plan is not special: two carry-outs, two copies, two hits."""
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    caught = a_companion("proto_mi_b", "Gorou — Juuga")
    card = crystal_collapse()
    play_companions(st, [caught, card])
    kokomi_plan.schedule(st, card)
    powers.apply_power(st, st.player, kokomi_plan.NEREIDS_ASCENSION, 1)
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 28
    assert counts(st)["plan_copy"] == 2


def test_nothing_is_recorded_or_planned_with_the_flag_off():
    """The arm's own gate, and it is the whole file's rule one card over: with
    `C.KOKOMI_OVERHAUL` off the recorder records nothing and the Plan is never
    written, so the row cannot be reached at all."""
    st = kokomi_state(enemies=[make_enemy(hp=40)])
    caught = a_companion("proto_mi_b", "Gorou — Juuga")
    card = crystal_collapse()
    play_companions(st, [caught, card])
    kokomi_plan.schedule(st, card)
    assert st.kk_companions_this_turn == []
    assert st.kk_plan_queue == []


def test_the_memory_is_cleared_at_the_turn_boundary(overhaul):
    """"This turn" is cleared rather than handed over, unlike the Companion
    COUNT beside it: the capture already happened when the Plan was written,
    so what survives the boundary is the card on the entry."""
    st = kokomi_state()
    play_companions(st, [a_companion("proto_mi_b", "Gorou — Juuga")])
    assert st.kk_companions_this_turn
    kokomi_plan.roll_turn(st)
    assert st.kk_companions_this_turn == []


# ---------------------------------------------------------------------------
# THE PLAYABILITY GATE -- `EB-455`
# ---------------------------------------------------------------------------

def test_change_of_plans_is_unplayable_while_no_plan_is_written(overhaul):
    """`EB-455`, the mod's `IsPlayable` gate at this engine's twin seam.

    THE FIND (Kokomi r13 (b)). Change of Plans "was dead in hand three fights
    before it was good once and its face never says it needs a written Plan; a
    first reader plays it into an empty jellyfish". It is `EB-261`'s Set-off
    gate one mechanic over: the card pays its energy, exhausts itself and
    resolves to nothing.
    """
    from tier0.engine import combat

    st = kokomi_state(enemies=[make_enemy(hp=40)])
    st.player.energy = 3
    card = loader.get_card("proto_kk_change_of_plans")
    assert kokomi_plan.carry_out_only(card) is True

    assert combat.card_playable(st, card) is False
    kokomi_plan.schedule(st, plan_card(ATTACKER))
    assert combat.card_playable(st, card) is True


def test_the_gate_is_inert_with_the_flag_off():
    """`live()` first, this file's rule: nothing the arm invents may reach a
    release build's playability read."""
    from tier0.engine import combat

    st = kokomi_state(enemies=[make_enemy(hp=40)])
    st.player.energy = 3
    card = Card(id="proto_kk_probe", name="probe", cost=1, type="skill",
                effects=[{"op": "carry_out_front_plan"}])

    assert kokomi_plan.refuses_for_no_plan(st, card) is False


def test_a_carry_out_beside_another_effect_is_never_gated(overhaul):
    """The clause is deliberately narrow, `set_off_only`'s rule: a card that
    also draws still does something on an empty jellyfish, and refusing it
    would be a rules change rather than a legibility fix."""
    from tier0.engine import combat

    st = kokomi_state(enemies=[make_enemy(hp=40)])
    st.player.energy = 3
    card = Card(id="proto_kk_probe", name="probe", cost=1, type="skill",
                effects=[{"op": "carry_out_front_plan"},
                         {"op": "draw", "amount": 1}])

    assert kokomi_plan.carry_out_only(card) is False
    assert combat.card_playable(st, card) is True


def test_every_kokomi_row_agrees_with_the_emitters_own_gate(overhaul):
    """The two implementations of `card_is_carry_out_only` are checked against
    each other over the whole surface -- `test_klee_overhaul_rules`' pin on the
    Set-off pair, which is the only way "the same list" stays true."""
    from tools import gen_klee_cards

    for card in loader.prototype_cards():
        if not card.id.startswith("proto_kk_"):
            continue
        row = {"effects": card.effects}
        assert kokomi_plan.carry_out_only(card) == \
            gen_klee_cards.card_is_carry_out_only(row), card.id


# --- THE POOL PASS (`EB-492`) ----------------------------------------------
#
# One section per new piece of engine: the multi-hit Plan clause (Pincer), the
# intent-keyed set aim (Flank), and the morning count on a now-line (Well
# Laid). Nereid's Ascension's redesign is pinned in section 4 above, beside
# the reading it changed. Every number here is a PROTOTYPE number and none of
# it is quotable (R215 B).


def test_a_planned_times_clause_is_that_many_whole_hits(overhaul):
    """Pincer. THREE HITS OF 3, not one hit of 9, and the difference is the
    number of damage EVENTS rather than the total: each pass goes out through
    `deal_damage_to_enemy` on its own, so each reacts on its own and each is
    one strike for anything hung off a hit. `KokomiPlan.Hit` loops the same
    way."""
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    carry_out(st, [{"op": "damage", "amount": 3, "target": "front_enemy",
                    "times": 3}])
    assert enemy.hp == 40 - 9
    assert counts(st)["damage"] == 3


def test_a_times_clause_re_reads_its_aim_between_hits(overhaul):
    """The front enemy killed by the first pass hands the next one to the
    enemy behind it -- "leftmost alive" read three times rather than a second
    rule."""
    first, second = make_enemy(hp=3), make_enemy(hp=40)
    st = kokomi_state(enemies=[first, second])
    carry_out(st, [{"op": "damage", "amount": 3, "target": "front_enemy",
                    "times": 3}])
    assert first.hp == 0
    assert second.hp == 40 - 6


def test_times_is_refused_outside_the_flat_hit(overhaul):
    """`PLAN_TIMES_OPS` is the flat hit and nothing else: the scaled damage
    kinds already derive their size from a count, and a debuff applied twice
    in one beat is two stacks rather than two applications."""
    assert kokomi_plan.plan_shape_reason(
        [{"op": "damage", "amount": 3, "target": "front_enemy", "times": 2}]
    ) is None
    assert kokomi_plan.plan_shape_reason(
        [{"op": "apply_power", "power": "weak", "amount": 1,
          "target": "front_enemy", "times": 2}])
    # A literal of 2 or more, for `amount`'s reason: the count is read a turn
    # after it was written.
    assert kokomi_plan.plan_shape_reason(
        [{"op": "damage", "amount": 3, "target": "front_enemy", "times": 1}])


def test_the_intent_set_is_fixed_when_the_plan_is_written(overhaul):
    """Flank. The enemies caught are the ones telegraphing an attack AT
    WRITING TIME -- an enemy whose intent changes overnight is still hit, and
    one that was Defending when the Plan was written is not."""
    swinger = make_enemy(hp=40, intents=ATTACKER)
    guard = make_enemy(hp=40, intents=BLOCKER)
    st = kokomi_state(enemies=[swinger, guard])
    card = plan_card([{"op": "damage", "amount": 8,
                       "target": "enemies_intending_attack"}])
    kokomi_plan.schedule(st, card)
    # The board changes its mind between the writing and the morning.
    swinger.intents = BLOCKER
    guard.intents = ATTACKER
    kokomi_plan.resolve_all(st)
    assert swinger.hp == 40 - 8
    assert guard.hp == 40


def test_the_intent_set_skips_a_body_that_died(overhaul):
    """"Each carry-out hit lands on those enemies that are still alive." A
    corpse is not a target, which is the rule every other aim already keeps."""
    dying = make_enemy(hp=40, intents=ATTACKER)
    other = make_enemy(hp=40, intents=ATTACKER)
    st = kokomi_state(enemies=[dying, other])
    card = plan_card([{"op": "damage", "amount": 8,
                       "target": "enemies_intending_attack"}])
    kokomi_plan.schedule(st, card)
    dying.hp = 0
    kokomi_plan.resolve_all(st)
    assert other.hp == 40 - 8


def test_an_empty_intent_set_is_a_plan_that_carries_out_nothing(overhaul):
    """The Plan is WRITTEN -- the queue's depth is honest and the strip says
    so -- and it hits no one. The label is what says so."""
    guard = make_enemy(hp=40, intents=BLOCKER)
    st = kokomi_state(enemies=[guard])
    card = plan_card([{"op": "damage", "amount": 8,
                       "target": "enemies_intending_attack"}])
    kokomi_plan.schedule(st, card)
    assert len(st.kk_plan_queue) == 1
    assert st.kk_plan_queue[0].label.endswith(": nothing")
    kokomi_plan.resolve_all(st)
    assert guard.hp == 40


def test_the_aimed_label_names_the_bodies_it_caught(overhaul):
    """`KokomiPlan.AimedLabel`'s twin: a Plan whose targets were decided when
    it was written has to say which bodies it caught, for `plan_label`'s
    reason one aim over."""
    swinger = make_enemy(hp=40, intents=ATTACKER)
    swinger.name = "Cultist"
    st = kokomi_state(enemies=[swinger, make_enemy(hp=40, intents=BLOCKER)])
    card = plan_card([{"op": "damage", "amount": 8,
                       "target": "enemies_intending_attack"}])
    kokomi_plan.schedule(st, card)
    assert st.kk_plan_queue[0].label == "probe: Cultist"


def test_a_sleeping_enemy_intends_nothing(overhaul):
    """The arm's one intent read, and it is the shipped predicate's two
    clauses: an attack intent AND `sleep_turns == 0`."""
    sleeper = make_enemy(hp=40, intents=ATTACKER)
    sleeper.sleep_turns = 2
    st = kokomi_state(enemies=[sleeper])
    card = plan_card([{"op": "damage", "amount": 8,
                       "target": "enemies_intending_attack"}])
    kokomi_plan.schedule(st, card)
    kokomi_plan.resolve_all(st)
    assert sleeper.hp == 40


def test_the_captured_set_never_touches_the_printed_card(overhaul):
    """The capture is written onto a COPY of the clause. `card.plan` is the
    SHEET's list, shared by every instance of the row, and writing this turn's
    board into it would put a corpse on a printed card."""
    st = kokomi_state(enemies=[make_enemy(hp=40, intents=ATTACKER)])
    card = plan_card([{"op": "damage", "amount": 8,
                       "target": "enemies_intending_attack"}])
    kokomi_plan.schedule(st, card)
    assert "targets" not in card.plan[0]
    assert st.kk_plan_queue[0].clauses[0]["targets"]


def well_laid():
    """Well Laid's own now-line, off a probe row rather than the sheet: the
    sheet's numbers are a `D` default and this file pins the ENGINE."""
    return Card(id="proto_kk_probe_well_laid", name="probe", cost=0,
                type="attack",
                effects=[{"op": "damage", "target": "enemy",
                          "amount_formula": {
                              "base": 2, "per": 3,
                              "count": "plans_carried_out_this_morning"}}])


def test_well_laids_count_is_the_morning_tide_wall_reads(overhaul):
    """`plans_carried_out_this_morning` is `kk_plans_this_morning`, written
    once at the drain -- the same number Tide Wall's planned Block multiplies,
    so the morning a now-line sees and the morning a Plan clause sees are one
    fact."""
    enemy = make_enemy(hp=60)
    st = kokomi_state(enemies=[enemy])
    for i in range(3):
        kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                           cid=f"proto_kk_p{i}"))
    kokomi_plan.resolve_all(st)
    assert effects._runtime_count(
        st, "plans_carried_out_this_morning") == 3
    # And the now-line prices off it: 2 + 3 x 3.
    effects.resolve_card(st, well_laid())
    assert enemy.hp == 60 - 11


def test_a_morning_that_drained_nothing_reads_an_honest_zero(overhaul):
    """`roll_turn` clears the count, so Well Laid on a quiet morning is a
    worse Strike rather than yesterday's payout."""
    enemy = make_enemy(hp=60)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}]))
    kokomi_plan.resolve_all(st)
    kokomi_plan.roll_turn(st)
    assert effects._runtime_count(
        st, "plans_carried_out_this_morning") == 0
    effects.resolve_card(st, well_laid())
    assert enemy.hp == 60 - 2


# --- POOL PASS TWO (`EB-643`, R265): the queue as something you operate on --
#
# Eight rows, one trial keyword (Dusk), three plan clauses, three now-lines and
# one lane rule. The C# is the spec and these are the sim twin's pins; the
# structural half is `KokomiPoolPassTwoTests`. Prototype numbers, D by the
# ladder, and nothing here is quotable (R215 B).


def dusk_card(clauses, effects_=None, cid="proto_kk_dusk_probe"):
    """A probe row whose Plan line is a DUSK line."""
    card = plan_card(clauses, effects_, cid=cid)
    card.plan_dusk = True
    return card


def hit(amount, target="front_enemy"):
    return {"op": "damage", "amount": amount, "target": target}


# --- the two riders: order, and what "the next Plan" means -----------------

def test_gambit_then_riptide_doubles_riptide(overhaul):
    """The next Plan is the entry carried out IMMEDIATELY AFTER this one in
    the same drain, so a rider written first reaches the hit written second."""
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.NEXT_PLAN_DOUBLE_DAMAGE}], cid="proto_kk_gambit"))
    kokomi_plan.schedule(st, plan_card([hit(13)], cid="proto_kk_riptide"))
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 200 - 26


def test_riptide_then_gambit_doubles_nothing(overhaul):
    """A rider written by the LAST entry of a drain reaches nothing: it falls
    off the end of a local rather than waiting for a morning nobody wrote it
    in. The pin is the ORDER, and it is the whole of the rider's rule."""
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, plan_card([hit(13)], cid="proto_kk_riptide"))
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.NEXT_PLAN_DOUBLE_DAMAGE}], cid="proto_kk_gambit"))
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 200 - 13
    # And it does not survive into the next morning either.
    kokomi_plan.roll_turn(st)
    kokomi_plan.schedule(st, plan_card([hit(13)], cid="proto_kk_riptide2"))
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 200 - 26


def test_a_rider_with_no_follower_says_so(overhaul):
    """`EB-645`. The r23 defence lane wrote Second Wave with no Plan behind it
    in the same morning; the rider fell off the end of the drain as designed
    and the page said nothing at all. The drain now finishes the sentence."""
    st = kokomi_state()
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.NEXT_PLAN_EXTRA_CARRY_OUT}],
        cid="proto_kk_second_wave"))
    kokomi_plan.resolve_all(st)
    said = [e for e in st.log if e["event"] == "plan_no_follower"]
    assert len(said) == 1
    assert said[0]["card"] == "proto_kk_second_wave"
    assert said[0]["line"] == "proto_kk_second_wave: no Plan followed"


def test_a_rider_that_reached_a_follower_says_nothing(overhaul):
    """The line is about the EMPTY case only: a rider that landed needs no
    receipt, because the entry it doubled printed one."""
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.NEXT_PLAN_DOUBLE_DAMAGE}], cid="proto_kk_gambit"))
    kokomi_plan.schedule(st, plan_card([hit(13)], cid="proto_kk_riptide"))
    kokomi_plan.resolve_all(st)
    assert counts(st)["plan_no_follower"] == 0
    assert enemy.hp == 200 - 26


def test_the_no_follower_line_names_the_card_that_wrote_the_rider(overhaul):
    """Two entries, and the LAST one is the one still holding a rider: the
    flags are cleared at the top of every entry, so what is pending at the end
    of the drain was written by the entry immediately before it."""
    st = kokomi_state()
    kokomi_plan.schedule(st, plan_card([{"op": "draw", "amount": 0}],
                                       cid="proto_kk_first"))
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.NEXT_PLAN_DOUBLE_DAMAGE}],
        cid="proto_kk_opening_gambit"))
    kokomi_plan.resolve_all(st)
    said = [e for e in st.log if e["event"] == "plan_no_follower"]
    assert [e["card"] for e in said] == ["proto_kk_opening_gambit"]


def test_a_dusk_rider_with_no_follower_says_so_too(overhaul):
    """The dusk drain is the same loop, so it finishes the same sentence and
    marks WHICH drain ran out."""
    st = kokomi_state()
    kokomi_plan.schedule(st, dusk_card(
        [{"op": kokomi_plan.NEXT_PLAN_EXTRA_CARRY_OUT}],
        cid="proto_kk_dusk_wave"))
    kokomi_plan.resolve_dusk(st)
    said = [e for e in st.log if e["event"] == "plan_no_follower"]
    assert len(said) == 1 and said[0]["why"] == "dusk"


def test_change_of_plans_never_says_no_plan_followed(overhaul):
    """`resolve_front` carries ONE entry out and does not come through the
    drain, so there is no "next" for the word to name -- and a drain of one
    that never had a follower to lose says nothing."""
    st = kokomi_state()
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.NEXT_PLAN_DOUBLE_DAMAGE}], cid="proto_kk_gambit"))
    kokomi_plan.resolve_front(st)
    assert counts(st)["plan_no_follower"] == 0


def test_two_riders_in_a_row_reach_two_different_entries(overhaul):
    """Each rider is spent by the entry it reaches, so two in a row cannot
    both land on a third: the doubling rides onto Second Wave, and Second
    Wave's own rider rides onto the hit."""
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.NEXT_PLAN_DOUBLE_DAMAGE}], cid="proto_kk_gambit"))
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.NEXT_PLAN_EXTRA_CARRY_OUT}],
        cid="proto_kk_second_wave"))
    kokomi_plan.schedule(st, plan_card([hit(13)], cid="proto_kk_riptide"))
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 200 - 26


def test_two_riders_on_one_entry_stack_on_the_entry_that_follows(overhaul):
    """Both riders printed by ONE Plan reach the one entry after it: the hit
    is doubled AND carried out twice."""
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.NEXT_PLAN_DOUBLE_DAMAGE},
         {"op": kokomi_plan.NEXT_PLAN_EXTRA_CARRY_OUT}],
        cid="proto_kk_both"))
    kokomi_plan.schedule(st, plan_card([hit(13)], cid="proto_kk_riptide"))
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 200 - 52


def test_second_wave_under_nereids_is_two_carry_outs(overhaul):
    """`EB-655`. The two rules NO LONGER MEET on one entry, and that is the
    pass's rule read literally: Nereid's Ascension doubles the FIRST entry of
    the drain, Second Wave reaches the entry AFTER itself, and no entry is both.
    So Second Wave written first is carried out twice (it is first), prints its
    rider twice -- a FLAG, so still once -- and the entry behind it runs
    1 + 1 = 2."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.NEREIDS_ASCENSION] = 1
    st.player.energy = 0
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.NEXT_PLAN_EXTRA_CARRY_OUT}],
        cid="proto_kk_second_wave"))
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                       cid="proto_kk_payload"))
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 2


def test_change_of_plans_neither_sets_nor_consumes_a_rider(overhaul):
    """`resolve_front` carries ONE entry out and there is no next for the word
    to name."""
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.NEXT_PLAN_DOUBLE_DAMAGE}], cid="proto_kk_gambit"))
    kokomi_plan.schedule(st, plan_card([hit(13)], cid="proto_kk_riptide"))
    kokomi_plan.resolve_front(st)          # the Gambit, alone
    kokomi_plan.resolve_all(st)            # the hit, next morning
    assert enemy.hp == 200 - 13


# --- Scout Ahead ----------------------------------------------------------

@pytest.mark.parametrize("position", [0, 1, 2])
def test_scout_ahead_counts_the_whole_drain_wherever_it_sits(overhaul,
                                                             position):
    """`EB-679`. THE COUNT INCLUDES ITSELF AND IGNORES POSITION: three entries
    in one morning is 3, whether Scout Ahead was written first, second or
    last. That is the redesign -- the old clause paid 2 at the front and 0 at
    the back, which made the card's whole value its place in the queue."""
    st = kokomi_state()
    rows = [plan_card([{"op": "energy", "amount": 1}], cid=f"proto_kk_p{i}")
            for i in range(3)]
    rows[position] = plan_card(
        [{"op": kokomi_plan.DRAW_PER_PLAN_THIS_TURN, "amount": 1}],
        cid="proto_kk_scout")
    for row in rows:
        kokomi_plan.schedule(st, row)
    kokomi_plan.resolve_all(st)
    drew = [e for e in st.log if e["event"] == "plan_scout_ahead"]
    assert [e["cards"] for e in drew] == [3]


def test_scout_ahead_written_alone_draws_one(overhaul):
    """`EB-679`. ITSELF IS A CARRY-OUT, so the floor is 1 rather than 0 -- the
    old clause drew nothing at all when it was the only Plan of the morning,
    which is the shape a seat declines to write."""
    st = kokomi_state()
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.DRAW_PER_PLAN_THIS_TURN, "amount": 1}],
        cid="proto_kk_scout"))
    kokomi_plan.resolve_all(st)
    drew = [e for e in st.log if e["event"] == "plan_scout_ahead"]
    assert [e["cards"] for e in drew] == [1]


def test_scout_ahead_hurried_by_change_of_plans_draws_one(overhaul):
    """`EB-679`. A drain of ONE is one carry-out, which is the face read
    literally: this Plan was carried out this turn."""
    st = kokomi_state()
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.DRAW_PER_PLAN_THIS_TURN, "amount": 1}],
        cid="proto_kk_scout"))
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                       cid="proto_kk_p0"))
    kokomi_plan.resolve_front(st)
    drew = [e for e in st.log if e["event"] == "plan_scout_ahead"]
    assert [e["cards"] for e in drew] == [1]


def test_scout_ahead_under_nereids_counts_the_extra_carry_out(overhaul):
    """`EB-679`. The count is CARRY-OUTS and not entries (`EB-501`), so the
    Rare's second run at the FIRST entry of the drain is one more Plan carried
    out: three entries read 4. Scout Ahead written first is itself carried out
    twice, and both carry-outs read the same 4 -- the number is the drain's."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.NEREIDS_ASCENSION] = 1
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.DRAW_PER_PLAN_THIS_TURN, "amount": 1}],
        cid="proto_kk_scout"))
    for i in range(2):
        kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                           cid=f"proto_kk_p{i}"))
    kokomi_plan.resolve_all(st)
    drew = [e for e in st.log if e["event"] == "plan_scout_ahead"]
    assert [e["cards"] for e in drew] == [4, 4]


# --- Second Thoughts ------------------------------------------------------

def test_second_thoughts_returns_the_card_and_refunds_its_cost(overhaul):
    """The LAST entry, its card out of the discard pile into the hand, and the
    Energy back."""
    st = kokomi_state()
    st.player.energy = 0
    written = plan_card([hit(10)], cid="proto_kk_written")
    written.cost = 2
    st.player.discard_pile.append(written)
    kokomi_plan.schedule(st, written)
    kokomi_plan.cancel_last_plan(st)
    assert st.kk_plan_queue == []
    assert written in st.player.hand
    assert written not in st.player.discard_pile
    assert st.player.energy == 2


def test_second_thoughts_takes_the_newest_and_leaves_the_rest(overhaul):
    """Change of Plans hurries the OLDEST; this takes back the NEWEST."""
    st = kokomi_state()
    for i in range(2):
        kokomi_plan.schedule(st, plan_card([hit(5)], cid=f"proto_kk_p{i}"))
    kokomi_plan.cancel_last_plan(st)
    assert [e.card_id for e in st.kk_plan_queue] == ["proto_kk_p0"]


def test_second_thoughts_on_an_empty_queue_is_a_printed_no_op(overhaul):
    st = kokomi_state()
    st.player.energy = 0
    kokomi_plan.cancel_last_plan(st)
    assert counts(st)["plan_cancel_last_empty"] == 1
    assert st.player.energy == 0


def test_a_moons_reflection_entry_returns_nothing(overhaul):
    """The Plan is cancelled and no card comes back: what the face promises is
    the card, and one written off the EXHAUST pile is not in the discard pile
    to promise."""
    st = kokomi_state()
    st.player.energy = 0
    exhausted = plan_card([hit(9)], cid="proto_kk_exhausted")
    exhausted.cost = 3
    st.player.exhaust_pile.append(exhausted)
    moon = Card(id="proto_kk_moon", name="probe", cost=1, type="skill",
                effects=[{"op": "plan_from_exhaust"}])
    kokomi_plan.schedule_from_exhaust(st, moon)
    assert len(st.kk_plan_queue) == 1
    kokomi_plan.cancel_last_plan(st)
    assert st.kk_plan_queue == []
    assert st.player.energy == 0
    assert st.player.hand == []


# --- Ebb Tide -------------------------------------------------------------

def test_ebb_tide_cashes_the_whole_queue_per_entry(overhaul):
    """Three queued: 3 Energy, 3 cards, queue empty."""
    st = kokomi_state()
    st.player.energy = 0
    st.player.draw_pile = [Card(id=f"strike{i}", name="s", cost=1,
                                type="attack", effects=[])
                           for i in range(5)]
    for i in range(3):
        kokomi_plan.schedule(st, plan_card([hit(5)], cid=f"proto_kk_p{i}"))
    kokomi_plan.cancel_all_plans_cash(st)
    assert st.kk_plan_queue == []
    assert st.player.energy == 3
    assert len(st.player.hand) == 3


def test_ebb_tide_on_an_empty_queue_pays_nothing(overhaul):
    st = kokomi_state()
    st.player.energy = 0
    kokomi_plan.cancel_all_plans_cash(st)
    assert st.player.energy == 0


# --- Converging Tide ------------------------------------------------------

def test_converging_tide_lands_front_aimed_plans_on_the_target(overhaul):
    front = make_enemy(hp=80, name="front")
    back = make_enemy(hp=80, name="back")
    st = kokomi_state(enemies=[front, back])
    kokomi_plan.schedule(st, plan_card([hit(10)], cid="proto_kk_feint"))
    kokomi_plan.redirect_queued_plans(st, back)
    kokomi_plan.resolve_all(st)
    assert front.hp == 80 and back.hp == 70


def test_converging_tide_leaves_an_all_enemies_clause_alone(overhaul):
    """An ALL clause does not aim at the front, so there is nothing on it for
    instead-of-the-front to be about."""
    front = make_enemy(hp=80, name="front")
    back = make_enemy(hp=80, name="back")
    st = kokomi_state(enemies=[front, back])
    kokomi_plan.schedule(st, plan_card([hit(10, target="all_enemies")],
                                       cid="proto_kk_oath"))
    kokomi_plan.redirect_queued_plans(st, back)
    kokomi_plan.resolve_all(st)
    assert front.hp == 70 and back.hp == 70


def test_a_dead_redirect_target_falls_back_to_the_front(overhaul):
    front = make_enemy(hp=80, name="front")
    back = make_enemy(hp=80, name="back")
    st = kokomi_state(enemies=[front, back])
    kokomi_plan.schedule(st, plan_card([hit(10)], cid="proto_kk_feint"))
    kokomi_plan.redirect_queued_plans(st, back)
    back.hp = 0
    kokomi_plan.resolve_all(st)
    assert front.hp == 70


def test_a_plan_written_after_the_redirect_aims_at_the_front(overhaul):
    """The face names the queue as it stands; a rule that kept re-aiming later
    writes would be a Power the row does not print."""
    front = make_enemy(hp=80, name="front")
    back = make_enemy(hp=80, name="back")
    st = kokomi_state(enemies=[front, back])
    kokomi_plan.redirect_queued_plans(st, back)
    kokomi_plan.schedule(st, plan_card([hit(10)], cid="proto_kk_feint"))
    kokomi_plan.resolve_all(st)
    assert front.hp == 70 and back.hp == 80


# --- DUSK -----------------------------------------------------------------

def test_a_dusk_plan_lands_at_the_end_of_the_turn_it_was_written_on(overhaul):
    """Breakwater's 7 Block is on her when the enemy hits."""
    st = kokomi_state()
    kokomi_plan.schedule(st, dusk_card([{"op": "block", "amount": 7}],
                                       cid="proto_kk_breakwater"))
    assert st.player.block == 0
    kokomi_plan.resolve_dusk(st)
    assert st.player.block == 7
    assert st.kk_plan_queue == []


def test_a_dusk_drain_leaves_the_morning_entries_where_they_are(overhaul):
    st = kokomi_state()
    kokomi_plan.schedule(st, plan_card([hit(5)], cid="proto_kk_morning"))
    kokomi_plan.schedule(st, dusk_card([{"op": "block", "amount": 7}],
                                       cid="proto_kk_breakwater"))
    kokomi_plan.resolve_dusk(st)
    assert [e.card_id for e in st.kk_plan_queue] == ["proto_kk_morning"]


def test_a_dusk_carry_out_is_a_carry_out(overhaul):
    """Treatise draws on it, and the `plan_carried_out` event fires."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.TREATISE] = 1
    st.player.draw_pile = [Card(id="strike", name="s", cost=1, type="attack",
                                effects=[])]
    kokomi_plan.schedule(st, dusk_card([{"op": "block", "amount": 7}],
                                       cid="proto_kk_breakwater"))
    kokomi_plan.resolve_dusk(st)
    assert counts(st)["plan_carried_out"] == 1
    assert counts(st)["plan_treatise"] == 1


def test_a_dusk_carry_out_does_not_touch_the_mornings_depth(overhaul):
    """Tide Wall, Well Laid and Tide Chart print this morning, and an evening
    is not one."""
    st = kokomi_state()
    kokomi_plan.schedule(st, dusk_card([{"op": "block", "amount": 7}],
                                       cid="proto_kk_breakwater"))
    kokomi_plan.resolve_dusk(st)
    assert st.kk_plans_this_morning == 0


def test_change_of_plans_pops_a_dusk_entry_too(overhaul):
    """The card says your front Plan, the queue is one queue, and a Dusk Plan
    at the front of it is the front Plan."""
    st = kokomi_state()
    kokomi_plan.schedule(st, dusk_card([{"op": "block", "amount": 7}],
                                       cid="proto_kk_breakwater"))
    kokomi_plan.resolve_front(st)
    assert st.player.block == 7
    assert st.kk_plan_queue == []


def test_a_dusk_rider_reaches_only_the_dusk_drain(overhaul):
    """Riders written on a dusk entry apply to the next entry in THAT drain."""
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, dusk_card(
        [{"op": kokomi_plan.NEXT_PLAN_DOUBLE_DAMAGE}],
        cid="proto_kk_dusk_gambit"))
    kokomi_plan.schedule(st, plan_card([hit(13)], cid="proto_kk_riptide"))
    kokomi_plan.resolve_dusk(st)
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 200 - 13


def test_the_sheets_two_dusk_rows_are_the_only_ones(overhaul):
    """`plan_dusk:` is a ROW flag and the sheet is where it is declared."""
    dusk = [c.id for c in loader.prototype_cards() if c.plan_dusk]
    assert dusk == ["proto_kk_breakwater", "proto_kk_night_watch"]


def _row(cid):
    return next(c for c in loader.prototype_cards() if c.id == cid)


def _faces():
    """The printed faces, off the SHEET: `description:` is the emitted C#
    face and the loader does not keep it on a `Card`."""
    import pathlib

    import yaml
    repo = pathlib.Path(__file__).resolve().parents[2]
    rows = yaml.safe_load(
        (repo / "docs" / "prototype-surface.yaml").read_text(encoding="utf-8"))
    return {r["id"]: r["description"] for r in rows if "description" in r}


def test_the_dusk_lines_are_written_only(overhaul):
    """`EB-646` (round 23) priced the face-up half to the Dusk line and the
    seat still never played it; `EB-655` (pool pass three) takes the now-line
    off both rows instead. WRITTEN-ONLY: no `effects` at all, so the card's
    only legal target is the Bake-Kurage (`gen_klee_cards._plan_only_line`,
    `KokomiTargets.PetOnly`) and its whole face is the Dusk clause.

    `EB-679` (pool pass four) KEPT THE SHAPE AND CHANGED BOTH LINES: Breakwater
    reads the morning it followed and Night Watch drops its Block for a Weak on
    every body. Written-only is what the pass did not touch."""
    breakwater = _row("proto_kk_breakwater")
    assert breakwater.effects == []
    assert breakwater.plan == [
        {"op": "block", "amount": 5},
        {"op": "block_per_plan_this_morning", "amount": 3},
    ]
    assert breakwater.upgrade == {"plan_block": 2}

    watch = _row("proto_kk_night_watch")
    assert watch.effects == []
    assert watch.plan == [{"op": "apply_power", "power": "weak", "amount": 1,
                           "target": "all_enemies"}]
    assert watch.upgrade == {"plan_power_amount": 1}


def test_breakwater_reads_the_mornings_carry_outs_and_not_its_own(overhaul):
    """`EB-679`. THE COUNT IS THE MORNING'S, which is what makes the card the
    wall behind the engine: a turn that carried out two Plans at dawn pays
    5 + 3 x 2 at dusk, and the Dusk entry itself is not one of the two --
    `resolve_dusk` deliberately leaves `kk_plans_this_morning` alone."""
    st = kokomi_state()
    for i in range(2):
        kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                           cid=f"proto_kk_p{i}"))
    kokomi_plan.resolve_all(st)
    # WRITTEN AFTER THE MORNING, which is the only order a Dusk Plan can be
    # written in: `resolve_all` drains the queue it finds, so an entry that
    # waits for a dusk was played on the turn the dusk ends.
    kokomi_plan.schedule(st, dusk_card(
        [{"op": "block", "amount": 5},
         {"op": kokomi_plan.BLOCK_PER_PLAN, "amount": 3}],
        cid="proto_kk_breakwater"))
    st.player.block = 0
    kokomi_plan.resolve_dusk(st)
    assert st.player.block == 5 + 3 * 2


def test_breakwater_after_an_empty_morning_pays_its_base_alone(overhaul):
    """`EB-679`. Zero times three is the honest answer to "for each Plan
    carried out this turn", so a Dusk Plan written on a morning that drained
    nothing is a plain 5 Block."""
    st = kokomi_state()
    kokomi_plan.schedule(st, dusk_card(
        [{"op": "block", "amount": 5},
         {"op": kokomi_plan.BLOCK_PER_PLAN, "amount": 3}],
        cid="proto_kk_breakwater"))
    kokomi_plan.resolve_dusk(st)
    assert st.player.block == 5


def test_the_three_rider_faces_print_the_window_the_rider_lives_in(overhaul):
    """`EB-645`. The rider is spent by the entry carried out immediately after
    this one IN THIS DRAIN, and a face that did not say so read as a promise
    about the whole fight."""
    faces = _faces()
    assert faces["proto_kk_second_wave"] == (
        "Gain 4 [gold]Block[/gold]. [gold]Plan[/gold]: The next "
        "[gold]Plan[/gold] carried out with this one is carried out twice.")
    assert faces["proto_kk_opening_gambit"].endswith(
        "The next [gold]Plan[/gold] carried out with this one deals double "
        "damage.")
    # `EB-679` took Scout Ahead OUT of this family: its count is no longer a
    # window on the drain but the whole of it, so the face states the turn.
    assert faces["proto_kk_scout_ahead"].endswith(
        "Draw 1 card for each [gold]Plan[/gold] carried out this turn.")


def test_ebb_tide_is_off_the_sheet_and_out_of_the_pool(overhaul):
    """`EB-649`, round 23: three draws on the cap lane, never played. The op
    stays registered with nothing spelling it -- see
    `kokomi_plan.cancel_all_plans_cash`, whose pins drive it directly."""
    assert "proto_kk_ebb_tide" not in {c.id for c in loader.prototype_cards()}
    assert "proto_kk_ebb_tide" not in C.KOKOMI_OVERHAUL_POOL_IDS
    assert "cancel_all_plans_cash" in effects.OPS


# --- the two-Plan cap -----------------------------------------------------

def test_the_cap_carries_out_two_and_holds_the_third(monkeypatch, overhaul):
    """At 2, three queued entries carry out two and the third waits for the
    next morning -- in order, and not re-sorted."""
    monkeypatch.setattr(C, "KOKOMI_PLAN_CAP", 2)
    st = kokomi_state()
    st.player.energy = 0
    for i in range(3):
        kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                           cid=f"proto_kk_p{i}"))
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 2
    assert [e.card_id for e in st.kk_plan_queue] == ["proto_kk_p2"]
    assert st.kk_plans_this_morning == 2
    kokomi_plan.roll_turn(st)
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 3
    assert st.kk_plan_queue == []


def test_a_capped_morning_reports_what_is_still_held(monkeypatch, overhaul):
    """Round 23, beside `EB-650`. THE BADGE READ ABSENT WHILE A PLAN WAS HELD:
    the C# clears the queue, syncs the pending badge at depth 0 -- which
    REMOVES it -- drains, and puts the held entries back afterwards with no
    second sync. `KokomiPlan.ResolveAll` re-syncs off the true depth now; this
    engine has no badge, so its half is the number on the log."""
    monkeypatch.setattr(C, "KOKOMI_PLAN_CAP", 2)
    st = kokomi_state()
    st.player.energy = 0
    for i in range(3):
        kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                           cid=f"proto_kk_p{i}"))
    kokomi_plan.resolve_all(st)
    held = [e for e in st.log if e["event"] == "plan_cap_held"]
    assert len(held) == 1
    assert held[0]["plans"] == 1 and held[0]["cap"] == 2
    # The badge's number: one Plan is still written after the morning.
    assert held[0]["pending"] == 1 == len(st.kk_plan_queue)


def test_the_cap_does_not_count_dusk_carry_outs(monkeypatch, overhaul):
    """A Dusk Plan has already waited for nothing, so the morning's allowance
    is untouched by one."""
    monkeypatch.setattr(C, "KOKOMI_PLAN_CAP", 2)
    st = kokomi_state()
    st.player.energy = 0
    kokomi_plan.schedule(st, dusk_card([{"op": "energy", "amount": 1}],
                                       cid="proto_kk_dusk"))
    for i in range(2):
        kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                           cid=f"proto_kk_p{i}"))
    kokomi_plan.resolve_dusk(st)
    assert st.player.energy == 1
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 3
    assert st.kk_plan_queue == []


def test_the_cap_defaults_to_unlimited(overhaul):
    """0 is today's behaviour, which is what makes the toggle a trial."""
    assert C.KOKOMI_PLAN_CAP == 0
    st = kokomi_state()
    st.player.energy = 0
    for i in range(4):
        kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                           cid=f"proto_kk_p{i}"))
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 4
    assert st.kk_plan_queue == []


def test_the_new_clauses_are_plan_only_from_a_body(overhaul):
    """A now-line spelling would name a drain that is not running."""
    for op in (kokomi_plan.DRAW_PER_PLAN_THIS_TURN,
               kokomi_plan.NEXT_PLAN_DOUBLE_DAMAGE,
               kokomi_plan.NEXT_PLAN_EXTRA_CARRY_OUT):
        assert op in kokomi_plan.PLAN_ONLY_OPS
        with pytest.raises(NotImplementedError, match="PLAN-ONLY"):
            effects.OPS[op](kokomi_state(), {"op": op},
                            Card(id="proto_kk_x", name="x", cost=1,
                                 type="skill", effects=[]))


# =============================================================================
# POOL PASS THREE (`EB-655`, R266): competing faces instead of a cap.
#
# THE FINDING. Every two-line row printed the same trade -- a small now-line, a
# bigger Plan -- so "write it" was the right answer on nearly every safe turn
# and the two-Plan cap was an attempt to fix the shape from outside the cards.
# The cap is retired as a rule; what replaces it is nine changes that give the
# NOW-LINE something the written half cannot buy. Provenance:
# docs/notes/prototype-surface-provenance.md, "Kokomi pool pass three".
# =============================================================================

def test_feint_pays_the_planned_number_after_a_carry_out(overhaul):
    """Sango Isshin's shape at Common. The branch reads the same
    `plan_carried_out_this_turn` predicate the Rare's condition does, so "a
    Plan was carried out this turn" has one definition in the arm.
    `ProtoKkFeint.OnPlay` is the twin."""
    row = _row("proto_kk_feint")
    branch = row.effects[0]
    assert branch["op"] == "conditional"
    assert branch["if"] == "plan_carried_out_this_turn"
    assert branch["then"] == [{"op": "damage", "amount": 10,
                               "target": "enemy"}]
    assert branch["else"] == [{"op": "damage", "amount": 5, "target": "enemy"}]
    assert row.plan == [{"op": "damage", "amount": 10,
                         "target": "front_enemy"}]


def test_feints_two_printed_numbers_upgrade_by_different_amounts(overhaul):
    """5 -> 7 and 10 -> 13, which is what `conditional_then_damage` exists for:
    `conditional_damage` moves both branches and the then-branch takes one
    more. Read off the SMITHED card, so the sheet's two keys and the applier
    agree."""
    from tier0.content import upgrades

    row = _row("proto_kk_feint")
    assert row.upgrade == {"conditional_damage": 2,
                           "conditional_then_damage": 1, "plan_damage": 3}
    up = upgrades.apply_upgrade(_row("proto_kk_feint"))
    branch = up.effects[0]
    assert branch["then"][0]["amount"] == 13
    assert branch["else"][0]["amount"] == 7
    assert up.plan[0]["amount"] == 13


def test_read_the_field_bottoms_the_costliest_of_the_top_two(overhaul):
    """THE PILOT'S CHOICE, STATED. The sim has no human, so `scry_bottom`
    bottoms the highest-cost card of the N it looked at -- the crude legible
    version of "the one I can least afford next turn". The mod puts a real
    selection screen here instead (`ScryBottom.Prompt`)."""
    st = kokomi_state()
    cheap = Card(id="cheap", name="cheap", cost=0, type="skill", effects=[])
    dear = Card(id="dear", name="dear", cost=3, type="skill", effects=[])
    tail = Card(id="tail", name="tail", cost=1, type="skill", effects=[])
    st.player.draw_pile = [cheap, dear, tail]
    effects.OPS["scry_bottom"](st, {"op": "scry_bottom", "amount": 2},
                               _row("proto_kk_read_the_field"))
    # The pick LEAVES THE TOP AND STAYS IN THE PILE: nothing is discarded.
    assert [c.id for c in st.player.draw_pile] == ["cheap", "tail", "dear"]
    assert any(e["event"] == "scry_bottom" for e in st.log)


def test_scry_bottom_on_an_empty_pile_is_a_printed_no_op(overhaul):
    """A look with nothing to look at is nothing said, and nothing raised."""
    st = kokomi_state()
    st.player.draw_pile = []
    effects.OPS["scry_bottom"](st, {"op": "scry_bottom", "amount": 2},
                               _row("proto_kk_read_the_field"))
    assert not [e for e in st.log if e["event"] == "scry_bottom"]


# =============================================================================
# POOL PASS FOUR (`EB-679`): the r26 dead faces, rebuilt. Provenance:
# docs/notes/prototype-surface-provenance.md, "Kokomi pool pass four".
# =============================================================================

def test_read_the_field_takes_one_card_and_bottoms_what_it_saw(overhaul):
    """`EB-679`. SELECTION AND NOT A LOOK: the chosen card goes to the HAND
    and every other card the player was shown goes to the bottom, in the order
    it was seen. The pilot takes the LOWEST-cost card of the N, which is
    `_op_scry_bottom`'s stand-in read the other way round -- the card wanted
    now is the one that can be paid for now."""
    st = kokomi_state()
    cheap = Card(id="cheap", name="cheap", cost=0, type="skill", effects=[])
    dear = Card(id="dear", name="dear", cost=3, type="skill", effects=[])
    mid = Card(id="mid", name="mid", cost=1, type="skill", effects=[])
    tail = Card(id="tail", name="tail", cost=1, type="skill", effects=[])
    st.player.draw_pile = [dear, cheap, mid, tail]
    effects.OPS["scry_take"](st, {"op": "scry_take", "amount": 3},
                             _row("proto_kk_read_the_field"))
    assert [c.id for c in st.player.hand] == ["cheap"]
    assert [c.id for c in st.player.draw_pile] == ["tail", "dear", "mid"]
    assert any(e["event"] == "scry_take" for e in st.log)


def test_scry_take_on_an_empty_pile_is_a_printed_no_op(overhaul):
    """A look with nothing to look at is nothing said, and nothing raised --
    `scry_bottom`'s shape one verb over."""
    st = kokomi_state()
    st.player.draw_pile = []
    effects.OPS["scry_take"](st, {"op": "scry_take", "amount": 3},
                             _row("proto_kk_read_the_field"))
    assert not [e for e in st.log if e["event"] == "scry_take"]
    assert st.player.hand == []


def test_scry_take_reads_a_short_pile_short(overhaul):
    """Fewer cards than the printed number is read short rather than refused:
    one card seen is one card taken and nothing to bottom."""
    st = kokomi_state()
    only = Card(id="only", name="only", cost=2, type="skill", effects=[])
    st.player.draw_pile = [only]
    effects.OPS["scry_take"](st, {"op": "scry_take", "amount": 3},
                             _row("proto_kk_read_the_field"))
    assert [c.id for c in st.player.hand] == ["only"]
    assert st.player.draw_pile == []


def test_read_the_field_is_a_selection_and_a_planned_wall(overhaul):
    """`EB-679`. The 5 Block face-up is gone -- r26 read it as a dead slot
    beside a Dusk Plan -- and both remaining numbers upgrade, one per half."""
    from tier0.content import upgrades

    row = _row("proto_kk_read_the_field")
    assert row.effects == [{"op": "scry_take", "amount": 3}]
    assert row.plan == [{"op": "block", "amount": 10}]
    assert row.upgrade == {"scry": 1, "plan_block": 2}
    up = upgrades.apply_upgrade(_row("proto_kk_read_the_field"))
    assert up.effects[0]["amount"] == 4
    assert up.plan[0]["amount"] == 12


def test_night_watch_upgrades_to_two_weak_on_every_body(overhaul):
    """`EB-679`. Slack Water's pair: one body or three, the Dusk Weak lands
    before the swing it was written against."""
    from tier0.content import upgrades

    up = upgrades.apply_upgrade(_row("proto_kk_night_watch"))
    assert up.plan == [{"op": "apply_power", "power": "weak", "amount": 2,
                        "target": "all_enemies"}]


def test_breakwaters_upgrade_moves_the_base_and_not_the_rate(overhaul):
    """`EB-679`. `plan_block` binds to the FLAT clause first
    (`upgrades.PLAN_DELTA_OPS`), so the wall gets taller and the morning it
    reads is priced the same."""
    from tier0.content import upgrades

    up = upgrades.apply_upgrade(_row("proto_kk_breakwater"))
    assert up.plan == [{"op": "block", "amount": 7},
                       {"op": "block_per_plan_this_morning", "amount": 3}]


def test_riptide_adds_its_rider_per_debuffed_body(overhaul):
    """The AoE rider CANNOT fold -- one printed number would have to stand for
    a board that takes several -- so it is added per enemy, and the clean
    enemy takes the base alone. `ProtoKkRiptide`'s emitted loop is the twin."""
    clean = make_enemy(hp=200)
    sick = make_enemy(hp=200)
    sick.powers["weak"] = 1
    st = kokomi_state(enemies=[clean, sick])
    row = _row("proto_kk_riptide")
    assert row.effects[0]["bonus_vs_debuff"] == 4
    effects.resolve_card(st, row)
    assert 200 - clean.hp == 9
    assert 200 - sick.hp == 13


def test_riptides_base_and_rider_upgrade_by_different_amounts(overhaul):
    """12 / 6 more / Plan 17: the `damage` key moves the base it rides on and
    `bonus_vs_debuff` moves the rider's own number."""
    from tier0.content import upgrades

    up = upgrades.apply_upgrade(_row("proto_kk_riptide"))
    assert up.effects[0]["amount"] == 12
    assert up.effects[0]["bonus_vs_debuff"] == 6
    assert up.plan[0]["amount"] == 17


def test_battle_plan_writes_a_draw_and_the_rider_and_no_energy(overhaul):
    """The `energy` clause paid the write back its own cost, so writing was
    free and the now-line was a strictly smaller card. It is gone, and what
    replaced it is DAMAGE rather than a discount (`EB-668`)."""
    row = _row("proto_kk_battle_plan")
    assert row.effects == [{"op": "draw", "amount": 1}]
    assert row.plan == [{"op": "draw", "amount": 2},
                        {"op": "next_attack_damage"}]
    assert not any(fx["op"] == "energy" for fx in row.plan)
    assert row.upgrade == {"draw": 1, "plan_draw": 1}


def test_the_rider_pays_a_face_up_attack_and_not_a_write(overhaul):
    """THE FACE-UP CLAUSE, which is what stops the reward paying for more
    writing -- and `EB-668`'s whole point, since it is now asked where the
    play is known instead of at a cost seam the mod cannot make target-aware.
    `flat_attack_bonus` is pure and asks `plan_aimed_at_pet`, so a card that
    would be WRITTEN reads its printed number and one that would be PLAYED
    reads the rider."""
    enemy = make_enemy(hp=200, intents=ATTACKER)
    st = kokomi_state(enemies=[enemy])
    st.player.powers[kokomi_plan.NEXT_ATTACK_BONUS] = 1
    attack = Card(id="proto_kk_a", name="a", cost=2, type="attack",
                  effects=[{"op": "damage", "amount": 5, "target": "enemy"}])
    skill = Card(id="proto_kk_s", name="s", cost=2, type="skill",
                 effects=[{"op": "block", "amount": 5}])
    assert (effects.flat_attack_bonus(st, attack, 2)
            == C.KOKOMI_OVERHAUL_BATTLE_PLAN_BONUS)
    # A SKILL IS NOT AN ATTACK, so the rider does not reach it.
    assert effects.flat_attack_bonus(st, skill, 2) == 0
    # AND A WRITE IS NOT A FACE-UP PLAY: a row with no now-line at all is a
    # write whatever the board intends, and it reads its printed number.
    written = Card(id="proto_kk_w", name="w", cost=2, type="attack",
                   effects=[],
                   plan=[{"op": "damage", "amount": 9,
                          "target": "front_enemy"}])
    assert kokomi_plan.plan_aimed_at_pet(st, written) is True
    assert effects.flat_attack_bonus(st, written, 2) == 0
    # AND THE COST SEAM IS GONE: the row moves damage, not price (`EB-668`).
    from tier0.engine import combat
    assert combat.card_cost(st, attack) == 2


def test_the_rider_is_one_stack_and_is_spent_by_the_play(overhaul):
    """Rally's two readings one card type over: the face says "deals 4 more
    damage", not "per Plan", and the rider is consumed by the play that takes
    it. A WRITE keeps it -- the pin `EB-668` was filed on."""
    st = kokomi_state(enemies=[make_enemy(hp=200, intents=ATTACKER)])
    kokomi_plan.next_attack_bonus(st)
    kokomi_plan.next_attack_bonus(st)
    assert st.player.powers[kokomi_plan.NEXT_ATTACK_BONUS] == 1
    written = Card(id="proto_kk_w", name="w", cost=1, type="attack",
                   effects=[],
                   plan=[{"op": "damage", "amount": 9,
                          "target": "front_enemy"}])
    kokomi_plan.spend_attack_bonus(st, written)
    assert st.player.powers[kokomi_plan.NEXT_ATTACK_BONUS] == 1
    skill = Card(id="proto_kk_s", name="s", cost=1, type="skill", effects=[])
    kokomi_plan.spend_attack_bonus(st, skill)
    assert st.player.powers[kokomi_plan.NEXT_ATTACK_BONUS] == 1
    attack = Card(id="proto_kk_a", name="a", cost=1, type="attack",
                  effects=[{"op": "damage", "amount": 5, "target": "enemy"}])
    kokomi_plan.spend_attack_bonus(st, attack)
    assert kokomi_plan.NEXT_ATTACK_BONUS not in st.player.powers


def test_the_rider_rides_every_hit_of_the_attack_it_pays(overhaul):
    """PER HIT, folded in where `next_attack_up` is folded in -- so a two-hit
    Attack collects it twice, and the play that took it spends it."""
    enemy = make_enemy(hp=200, intents=[])
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.next_attack_bonus(st)
    attack = Card(id="proto_kk_a", name="a", cost=0, type="attack",
                  effects=[{"op": "damage", "amount": 5, "target": "enemy",
                            "times": 2}])
    before = enemy.hp
    effects.resolve_card(st, attack)
    assert before - enemy.hp == 2 * (5 + C.KOKOMI_OVERHAUL_BATTLE_PLAN_BONUS)
    assert kokomi_plan.NEXT_ATTACK_BONUS not in st.player.powers


def test_nereids_doubles_only_the_first_plan_of_a_drain(overhaul):
    """"Every Plan twice" paid for writing MORE, which is the shape this pass
    undoes. The FIRST entry of each drain is doubled and the rest are not, so
    three written Plans are four carry-outs."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.NEREIDS_ASCENSION] = 1
    st.player.energy = 0
    for i in range(3):
        kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                           cid="proto_kk_p%d" % i))
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 4
    # AND THE MORNING'S DEPTH IS THE SAME FOUR, which is the number Tide Wall,
    # Well Laid and Tide Chart all read.
    assert st.kk_plans_this_morning == 4


def test_a_one_plan_morning_under_nereids_is_still_paid(overhaul):
    """The point of the change: the Rare no longer needs a deep morning to say
    anything."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.NEREIDS_ASCENSION] = 1
    st.player.energy = 0
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                       cid="proto_kk_one"))
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 2


def test_the_dusk_drain_pays_its_own_first_entry(overhaul):
    """"Each turn" is read as "each DRAIN": a morning and a dusk are two drains
    on one turn and each pays its own first entry, which is the drain-local
    reading "the next Plan" already takes."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.NEREIDS_ASCENSION] = 1
    st.player.energy = 0
    card = plan_card([{"op": "energy", "amount": 1}], cid="proto_kk_dusk")
    card.plan_dusk = True
    kokomi_plan.schedule(st, card)
    kokomi_plan.resolve_dusk(st)
    assert st.player.energy == 2


def test_converging_tide_is_off_the_sheet_and_out_of_the_pool(overhaul):
    """`EB-655`. The row re-aimed a queued Plan, and this pass makes the queue
    shallower on purpose. The RESOLVER stays with nothing spelling it, which is
    `EB-649`'s shape."""
    assert "proto_kk_converging_tide" not in C.KOKOMI_OVERHAUL_POOL_IDS
    assert not [c for c in loader.prototype_cards()
                if c.id == "proto_kk_converging_tide"]
    assert "redirect_queued_plans" in effects.OPS


def test_the_written_only_dusk_rows_can_only_be_written(overhaul):
    """No now-line at all, so `plan_aimed_at_pet` is True whatever the board
    intends -- the sim's reading of `KokomiTargets.PetOnly`, whose face leads
    with "Play on the Bake-Kurage."."""
    st = kokomi_state(enemies=[make_enemy(hp=200, intents=ATTACKER)])
    for cid in ("proto_kk_breakwater", "proto_kk_night_watch"):
        row = _row(cid)
        assert row.effects == []
        assert kokomi_plan.plan_aimed_at_pet(st, row) is True


def test_battle_plans_rider_is_plan_only_from_a_body(overhaul):
    """A now-line spelling would be a different, unpriced card."""
    op = "next_attack_damage"
    assert op in kokomi_plan.PLAN_ONLY_OPS
    with pytest.raises(NotImplementedError, match="PLAN-ONLY"):
        effects.OPS[op](kokomi_state(), {"op": op},
                        Card(id="proto_kk_x", name="x", cost=1,
                             type="skill", effects=[]))
