"""THE PLAN, clause by clause (`C.KOKOMI_OVERHAUL`, draft 6).

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

# THE SHIPPED WORLD, NAMED (legacy cleanup stage 3, 2026-10-01): the sim
# defaults to the current kits, and these pins read the shipped ones.

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
    yield
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()
    clear_upgrade_caches()


@pytest.fixture
def plan_line(monkeypatch):
    """A Plan stays open (2026-10-01): pin the pilot's line choice to the
    default, the Plan line, for a test about what the Plan line does.
    `kokomi_plan.line_policy` is an instrument surface; these tests are about
    the rule underneath it."""
    monkeypatch.setattr(kokomi_plan, "line_policy",
                        lambda state, entry: "plan")
    yield


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
    # TWENTY-FIVE after pool pass five (`EB-685`): Night Watch is retired and
    # Slack Water's Plan line, already counted, moved to Dusk.
    # TWENTY-SEVEN with the co-op set (review/records/coop-set-2026-09-25.md):
    # Joint Orders and Coordinated Strike, the multiplayer tier's two Plans.
    # THIRTY with the Casket pass (2026-09-28): Cleansing Wave and Ripple cut,
    # and Signal Arrow, Surging Shoal, Pearl Diver, Shell of Sanctuary and
    # Pearl Current added.
    # TWENTY-NINE with the cleanup pass (2026-09-29): Scout Ahead cut.
    # THIRTY-TWO with the feed pass (2026-09-29): Exposed Flank cut, Coral
    # Bulwark's Plan line gone, five Plan-only Commons added.
    # THIRTY-EIGHT with expansion batch one (2026-09-29): Lull, Undertide
    # Lance, Masterstroke, Undercurrent Snare, Evening Watch and Brace for the
    # Tide.
    # FORTY with pool completion (2026-10-01): Tidal Screen, and the
    # multiplayer Tactical Relay.
    assert len(planned) == 40
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


def test_a_skills_now_line_applies_hydro_and_reacts(overhaul):
    """`EB-462`'s finding, and R276 pick 2's rule: a Skill of hers that hits
    face-up applies Hydro like her Attacks, so an Electro aura standing in
    front of it reacts. The row the finding was filed on (Kurage's Oath) gains
    Block face-up since R276 pick 1, so the pin rides Opening Gambit's hit.

    Seen to FAIL before R276 pick 2: the enemy was bare after the now-line,
    and the Electro aura below survived it.
    """
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    effects.resolve_card(st, loader.get_card("proto_kk_opening_gambit"))
    assert enemy.hp == 40 - 7                     # 7 since the Casket pass
    assert enemy.aura == "hydro"

    charged = make_enemy(hp=40)
    charged.aura = "electro"
    charged.aura_turns_left = 3
    st2 = kokomi_state(enemies=[charged])
    effects.resolve_card(st2, loader.get_card("proto_kk_opening_gambit"))
    assert charged.aura != "electro"


def test_war_councils_face_and_its_hit_agree_about_the_aura(overhaul):
    """`EB-561`. Played directly the card applies Weak to every enemy and
    NOTHING ELSE -- no damage, no element -- so it leaves no aura and eats
    none. Since R276 pick 1 its Plan line is Energy, so neither half hits and
    the face carries no aura statement at all: no gem, no Plan-element rider.
    """
    bare = make_enemy(hp=40)
    st = kokomi_state(enemies=[bare])
    effects.resolve_card(st, loader.get_card("proto_kk_war_council"))
    assert bare.powers.get("weak") == 1
    assert bare.hp == 40, "the now-line deals no damage"
    assert bare.aura is None, "the now-line leaves no aura"

    charged = make_enemy(hp=40)
    charged.aura = "electro"
    charged.aura_turns_left = 3
    st2 = kokomi_state(enemies=[charged])
    effects.resolve_card(st2, loader.get_card("proto_kk_war_council"))
    assert charged.aura == "electro"

    # THE CARRY-OUT IS ENERGY (R276 pick 1): two, and no aura.
    planned = make_enemy(hp=40)
    st3 = kokomi_state(enemies=[planned])
    energy = st3.player.energy
    carry_out(st3, loader.get_card("proto_kk_war_council").plan)
    assert planned.aura is None
    assert st3.player.energy == energy + 2

    import pathlib
    repo = pathlib.Path(__file__).resolve().parents[2]
    face = (repo / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
            / "Generated" / "ProtoKkWarCouncil.cs").read_text(encoding="utf-8")
    assert "ArmKeywordTips.ForPlanElement(" not in face
    assert "KleeKeywords.AppliesHydro" not in face


def test_the_casket_strikes_nothing_since_the_casket_pass(overhaul):
    """THE CASKET PASS (2026-09-28) retired the debuff strike `EB-562` asked
    about: the relic COUNTS carried-out Plans now. A debuff she applies with
    the relic held moves no HP and lays no aura, and the page's glossary no
    longer admits a relic that applies an element."""
    bare = make_enemy(hp=40)
    st = casket_state(enemies=[bare])
    powers.apply_power(st, bare, "weak", 1, applier=st.player)
    assert bare.hp == 40
    assert bare.aura is None or bare.aura == "none" or not bare.aura
    assert counts(st).get("casket_strike", 0) == 0
    assert not hasattr(kokomi_plan, "casket_strike")

    from understudy import blindplay_notes
    assert "re-arms Hydro" not in (
        blindplay_notes.ARM_KEYWORDS["Tamakushi Casket"])
    gloss = blindplay_notes.REACTION_KEYWORDS["Elemental Reaction"]
    assert "one relic's line does" not in gloss
    assert "Casket" not in gloss

def test_eb714_a_second_plan_re_aims_at_the_next_living_body(overhaul):
    """`EB-714`. THE ACCEPTANCE: no Plan lands on a corpse.

    THE READ (r32 lane 1, fight 1 turn 2): "the two carry-outs both landed on
    Leaf Slime (S) -- 8 killed it down to 3, the second 8 killed it with 5
    wasted. They did not retarget." Read again with the numbers: the body was
    at 11, the first Plan took it to 3, and it was STILL ALIVE when the second
    arrived. The 5 is OVERKILL on a living body, which is what a second 8 into
    a 3-HP enemy is in any deck; it is not a Plan landing on a corpse, and the
    seat's own complaint one sentence later is the true one -- "nothing on the
    Plan screen warns you" -- which is a legibility row and not this one.

    THE AIM IS RE-READ PER ENTRY and always was: `_aimed` resolves at
    carry-out and `front_enemy` is leftmost ALIVE, which is a read of `hp`.
    This is that, driven: a front body the FIRST Plan kills, and a second
    entry that finds the next one.
    """
    front = make_enemy(hp=8, name="front")
    behind = make_enemy(hp=40, name="behind")
    st = kokomi_state(enemies=[front, behind])
    clause = [{"op": "damage", "amount": 8, "target": "front_enemy"}]
    kokomi_plan.schedule(st, plan_card(clause))
    kokomi_plan.schedule(st, plan_card(clause))
    kokomi_plan.resolve_all(st)

    assert front.hp <= 0 and not front.alive
    assert behind.hp == 40 - 8, "the second entry found the next living body"


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


# --- `EB-335`: the kit's own defence in act 2 (R246 pick 2) ---------------

def test_shell_guard_is_the_caskets_defensive_reader(overhaul):
    """SHELL GUARD, re-aimed (main session, 2026-09-28) after the Casket pass
    retired the strike it paid on: "Gain 5 Block, plus 1 for each point in
    the Casket." Block through the ordinary funnel (Dexterity and Frail
    count)."""
    st = kokomi_state(enemies=[make_enemy(hp=60)])
    effects.resolve_card(st, loader.get_card("proto_kk_shell_guard"))
    assert st.player.block == 5
    st2 = kokomi_state(enemies=[make_enemy(hp=60)])
    st2.kk_casket = 4
    effects.resolve_card(st2, loader.get_card("proto_kk_shell_guard"))
    assert st2.player.block == 9
    assert not hasattr(kokomi_plan, "SHELL_GUARD")
    assert not hasattr(kokomi_plan, "close_shell_guard")


def test_both_defensive_rows_load_and_smith(overhaul):
    """The two rows themselves, off the sheet. Tide Wall since the cleanup
    pass (2026-09-29): 4 Block now, Plan 6 Block plus the intent, upgrading to
    6 and 9 plus the intent. Shell Guard since its re-aim (2026-09-28): 5 plus
    1 per Casket point, base 8 upgraded; a Common since the cleanup pass."""
    from tier0.content import upgrades

    wall = loader.get_card("proto_kk_tide_wall")
    assert wall.rarity == "uncommon" and wall.cost == 1
    assert wall.effects == [{"op": "block", "amount": 4}]
    assert wall.plan == [{"op": "block_front_intent", "amount": 6}]
    up = upgrades.apply_upgrade(wall)
    assert up.effects[0]["amount"] == 6
    assert up.plan[0]["amount"] == 9

    guard = loader.get_card("proto_kk_shell_guard")
    assert guard.rarity == "common" and guard.cost == 1
    assert guard.type == "skill"
    assert guard.plan == []
    assert guard.effects == [{"op": "block", "amount_formula": {
        "base": 5, "per": 1, "count": "casket_count"}}]
    up = upgrades.apply_upgrade(guard)
    assert up.effects[0]["amount_formula"] == {
        "base": 8, "per": 1, "count": "casket_count"}


def test_damage_quarter_max_hp_rounds_down(overhaul):
    """Sango Isshin. ONE formula, read by the now-line and the planned half
    alike, so they cannot round differently (`KokomiRules.QuarterOfMaxHp`)."""
    enemy = make_enemy(hp=60)
    st = kokomi_state(enemies=[enemy], hp=81)
    assert kokomi_plan.quarter_of_max_hp(st) == 20
    carry_out(st, [{"op": "damage_quarter_max_hp", "target": "all_enemies"}])
    assert enemy.hp == 40


def test_sango_isshin_pays_six_to_all_per_plan_carried_out(overhaul):
    """THE CASKET PASS (2026-09-28), with a base since 2026-09-29: "Deal 8
    damage to ALL enemies, plus 6 for each Plan carried out this turn." A turn
    with none carried out deals the base 8; two carry-outs deal 20 to each."""
    a, b = make_enemy(hp=60, name="a"), make_enemy(hp=60, name="b")
    st = kokomi_state(enemies=[a, b], hp=80)
    card = loader.get_card("proto_kk_sango_isshin")

    assert st.kk_plans_carried_out_this_turn == 0
    effects.resolve_card(st, card)
    assert (a.hp, b.hp) == (52, 52)

    carry_out(st, [{"op": "draw", "amount": 1}])
    carry_out(st, [{"op": "draw", "amount": 1}])
    assert st.kk_plans_carried_out_this_turn == 2
    effects.resolve_card(st, card)
    assert (a.hp, b.hp) == (32, 32)

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
    # FORTY-SIX since the Casket pass (2026-09-28); FORTY-FOUR since the
    # cleanup pass (2026-09-29); SIXTY-NINE since expansion batch one;
    # SEVENTY since the payoff pass (2026-10-01); SEVENTY-EIGHT since pool
    # completion (2026-10-01); still SEVENTY-EIGHT since the status batch
    # (2026-10-01: seven cut, seven added).
    assert len(C.KOKOMI_OVERHAUL_POOL_IDS) == 78
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


# --- 7. THE CORE PASS PAYOFFS: Treatise and Song of Pearls ----------------
#
# Kokomi core pass (review/active/kokomi-core-pass-2026-09-27.md). Treatise
# pays for playing a Plan card's now-line; Song of Pearls pays for a morning
# with nothing written. Neither rides the plan bus any more.

def _deck(st, n=6):
    st.player.draw_pile = [plan_card([], cid=f"proto_kk_f{i}")
                           for i in range(n)]


def test_treatise_draws_on_a_face_up_plan_card_once_a_turn(overhaul):
    """"Once per turn, when you play a card with a Plan line normally, draw 1
    card." Two face-up Plan cards in a turn draw one card; the next turn pays
    again."""
    enemy = make_enemy(hp=200, intents=ATTACKER)   # intends: not a write
    st = kokomi_state(enemies=[enemy])
    _deck(st)
    st.player.powers[kokomi_plan.TREATISE] = 1
    card = plan_card([{"op": "energy", "amount": 1}],
                     effects_=[{"op": "block", "amount": 1}])
    assert not kokomi_plan.plan_aimed_at_pet(st, card)
    effects.resolve_card(st, card)
    assert len(st.player.hand) == 1
    effects.resolve_card(st, card)
    assert len(st.player.hand) == 1, "once per turn"
    kokomi_plan.roll_turn(st)
    effects.resolve_card(st, card)
    assert len(st.player.hand) == 2, "a new turn pays again"


def test_treatise_does_not_draw_on_a_written_plan(overhaul):
    """"Normally" is the now-line target. A card written on the Bake-Kurage
    draws nothing, and neither does its carry-out."""
    st = kokomi_state(enemies=[make_enemy(hp=80, intents=BLOCKER)])  # a write
    _deck(st)
    st.player.powers[kokomi_plan.TREATISE] = 1
    card = plan_card([{"op": "energy", "amount": 1}],
                     effects_=[{"op": "block", "amount": 1}])
    assert kokomi_plan.plan_aimed_at_pet(st, card)
    effects.resolve_card(st, card)
    assert len(st.kk_plan_queue) == 1
    kokomi_plan.resolve_all(st)
    assert st.player.hand == []
    assert counts(st)["plan_treatise"] == 0


def test_treatise_ignores_a_card_with_no_plan_line(overhaul):
    enemy = make_enemy(hp=200, intents=ATTACKER)
    st = kokomi_state(enemies=[enemy])
    _deck(st)
    st.player.powers[kokomi_plan.TREATISE] = 1
    plain = Card(id="proto_kk_plain", name="p", cost=1, type="skill",
                 effects=[{"op": "block", "amount": 1}])
    effects.resolve_card(st, plain)
    assert st.player.hand == []


def test_treatise_copies_add_cards_still_once_a_turn(overhaul):
    enemy = make_enemy(hp=200, intents=ATTACKER)
    st = kokomi_state(enemies=[enemy])
    _deck(st)
    st.player.powers[kokomi_plan.TREATISE] = 2
    card = plan_card([{"op": "energy", "amount": 1}],
                     effects_=[{"op": "block", "amount": 1}])
    effects.resolve_card(st, card)
    effects.resolve_card(st, card)
    assert len(st.player.hand) == 2


def _song_turn(st, pilot=None):
    """One real player turn, so the queue is read where `combat` reads it."""
    from tier0.engine import combat

    combat._player_turn(st, pilot or (lambda state: None))


def test_the_bus_no_longer_pays_treatise_or_song(overhaul):
    """A carry-out rings the bus; neither payoff answers it now."""
    st = kokomi_state()
    _deck(st)
    st.player.powers[kokomi_plan.TREATISE] = 1
    carry_out(st, [{"op": "energy", "amount": 1}])
    assert st.player.hand == []
    assert st.player.block == 0


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


# --- 8. THE TAMAKUSHI CASKET ----------------------------------------------

def casket_state(**kw):
    st = kokomi_state(**kw)
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
    return st


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


def test_a_frozen_reaction_is_still_a_debuff_she_applied(overhaul):
    """Frozen is a POWER in the mod and a FIELD here, so `reactions.resolve_hit`
    raises the debuff event by hand. It fed the Casket's strike until the
    Casket pass (2026-09-28); it still counts as a debuff on the enemy, and
    the relic answers it with nothing."""
    from tier0.engine import reactions
    enemy = make_enemy(hp=40)
    enemy.aura = "cryo"
    enemy.aura_turns_left = 3
    st = casket_state(enemies=[enemy])
    reactions.resolve_hit(st, enemy, "hydro", 0, "probe")
    assert counts(st).get("casket_strike", 0) == 0
    assert kokomi_plan.has_debuff(enemy) is True

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


# --- 10. RALLY AND CLEANSING WAVE ------------------------------------------

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
    # Riptide since the Casket pass (2026-09-28) cut Ripple: its Plan line is
    # 2 Energy and a card.
    ids = ["proto_kk_read_the_field"] * 4 + ["proto_kk_riptide"] * 4
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
    # its Riptide Plans wrote (2 apiece, past an energy reset that would
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
        # Salt Line until the Casket pass cut it; any card will do, and
        # Open the Casket gives What the Tokoyo Returns one to fetch.
        state.player.exhaust_pile = [loader.get_card("proto_kk_ambush"),
                                     kokomi_plan.open_the_casket_card()]
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


def test_a_damageless_follower_is_unchanged_and_the_face_says_so(overhaul):
    """`EB-687`. The rider pays nothing when the Plan behind it deals no
    damage -- a Block Plan is carried out exactly as written -- and the face
    used to promise "the next Plan ... deals double damage" without naming
    the object, so seats spent the energy and learned the condition from the
    no-Plan-followed line afterwards. The rule is here; the words are on the
    card, which is the half this row moved."""
    st = kokomi_state()
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.NEXT_PLAN_DOUBLE_DAMAGE}],
        cid="proto_kk_opening_gambit"))
    kokomi_plan.schedule(st, plan_card([{"op": "block", "amount": 8}],
                                       cid="proto_kk_coral_bulwark"))
    kokomi_plan.resolve_all(st)
    assert st.player.block == 8
    # THE 2026-09-25 TEXT PASS: the clause still names what it doubles.
    assert _faces()["proto_kk_opening_gambit"].endswith(
        "The [gold]Plan[/gold] after this one deals double damage.")


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

def scout_cards(state):
    """`EB-718`. WHAT SCOUT AHEAD ACTUALLY DREW in a drain: the card is paid at
    every later CARRY-OUT rather than once off a count, so the pin is the sum
    and not one event's figure."""
    return sum(e["cards"] for e in state.log
               if e["event"] == "plan_scout_ahead")


def test_the_whole_drain_count_is_kept_resolved_on_no_row(overhaul):
    """R267 pick 3. `draw_per_plan_this_turn` is `EB-679`'s spelling and no
    row spells it now. It stays REGISTERED and RESOLVED the way `scry_bottom`
    and `redirect_queued_plans` are, so a sheet can reach for it without a
    build: three entries, itself included, is 3."""
    assert kokomi_plan.DRAW_PER_PLAN_THIS_TURN in kokomi_plan.PLAN_KINDS
    assert not [c for c in loader.prototype_cards()
                if any(cl.get("op") == kokomi_plan.DRAW_PER_PLAN_THIS_TURN
                       for cl in (c.plan or []))]
    st = kokomi_state()
    kokomi_plan.schedule(st, plan_card(
        [{"op": kokomi_plan.DRAW_PER_PLAN_THIS_TURN, "amount": 1}],
        cid="proto_kk_scout"))
    for i in range(2):
        kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                           cid=f"proto_kk_p{i}"))
    kokomi_plan.resolve_all(st)
    drew = [e for e in st.log if e["event"] == "plan_scout_ahead"]
    assert [e["cards"] for e in drew] == [3]


# --- Second Thoughts ------------------------------------------------------

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
    """The `plan_carried_out` event fires. Treatise no longer draws on a
    carry-out (core pass): it pays for a face-up play."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.TREATISE] = 1
    st.player.draw_pile = [Card(id="strike", name="s", cost=1, type="attack",
                                effects=[])]
    kokomi_plan.schedule(st, dusk_card([{"op": "block", "amount": 7}],
                                       cid="proto_kk_breakwater"))
    kokomi_plan.resolve_dusk(st)
    assert counts(st)["plan_carried_out"] == 1
    assert counts(st)["plan_treatise"] == 0


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


def test_the_sheets_one_dusk_row_is_the_only_one(overhaul):
    """`plan_dusk:` is a ROW flag and the sheet is where it is declared.

    R267 PICK 1 TOOK SLACK WATER BACK OFF IT. Pool pass five had moved the
    starter's Plan half to Dusk; the brief names the next-morning Weak as the
    kit's turn-one decision and a starter card is [USER]'s, so Breakwater is
    the surface's only Dusk row again. The machinery is untouched --
    `plan_dusk:` is still a fact about a row's Plan LINE and
    `loader._validate_plan_dusk` still asks only that there be one."""
    dusk = [c.id for c in loader.prototype_cards() if c.plan_dusk]
    # The Casket pass (2026-09-28) added a second: Shell of Sanctuary.
    # Expansion batch one (2026-09-29): Evening Watch, Brace for the Tide.
    assert dusk == ["proto_kk_breakwater", "proto_kk_shell_of_sanctuary",
                    "proto_kk_evening_watch", "proto_kk_brace_for_the_tide"]


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

    `EB-685` (pool pass five) LEAVES BREAKWATER THE ONLY ONE: Night Watch is
    retired and Slack Water carries the Dusk Weak with its now-line intact.
    What the pass moved on this row is the COUNT and not the shape."""
    breakwater = _row("proto_kk_breakwater")
    assert breakwater.effects == []
    assert breakwater.plan == [
        {"op": "block", "amount": 5},
        {"op": "block_per_plan_held", "amount": 3},
    ]
    assert breakwater.upgrade == {"plan_block": 2}


def _breakwater(st):
    """Write the sheet's own Breakwater line onto the queue."""
    kokomi_plan.schedule(st, dusk_card(
        [{"op": "block", "amount": 5},
         {"op": kokomi_plan.BLOCK_PER_PLAN_HELD, "amount": 3}],
        cid="proto_kk_breakwater"))


def test_breakwater_pays_for_the_plans_the_jellyfish_is_holding(overhaul):
    """`EB-685`. THE WALL RISES ON THE TURN THE ENGINE IS WRITTEN: two Plans
    written this turn and still waiting for the next morning pay 5 + 3 x 2 at
    dusk. Pass four read the morning just drained, which a Plan written today
    can never be in -- r27's two seats counted 0 on four plays out of four."""
    st = kokomi_state()
    _breakwater(st)
    for i in range(2):
        kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                           cid=f"proto_kk_p{i}"))
    kokomi_plan.resolve_dusk(st)
    assert st.player.block == 5 + 3 * 2
    # AND THE TWO IT COUNTED ARE STILL THERE: it paid for the queue, it did
    # not spend it.
    assert len(st.kk_plan_queue) == 2


def test_breakwater_holding_nothing_pays_its_base_alone(overhaul):
    """`EB-685`. Zero times three is the honest answer to "for each", so a
    Breakwater with no Plan standing behind it is a plain 5 Block."""
    st = kokomi_state()
    _breakwater(st)
    kokomi_plan.resolve_dusk(st)
    assert st.player.block == 5


def test_breakwater_never_counts_itself_or_a_second_dusk_plan(overhaul):
    """`EB-685`. BY CONSTRUCTION AND NOT BY A FILTER: `resolve_dusk` takes
    every dusk entry off the queue before the first clause runs, so the count
    excludes this entry and any Dusk Plan written beside it -- neither is
    waiting for the next morning, which is what the face says."""
    st = kokomi_state()
    _breakwater(st)
    kokomi_plan.schedule(st, dusk_card([{"op": "block", "amount": 1}],
                                       cid="proto_kk_other_dusk"))
    kokomi_plan.resolve_dusk(st)
    assert st.player.block == 5 + 1


def test_a_plan_hurried_out_before_dusk_is_no_longer_held(overhaul):
    """`EB-685`. Change of Plans carries the front Plan out and it LEAVES the
    queue, so the wall behind the engine is one Plan shorter -- which is the
    trade the two cards make with each other."""
    st = kokomi_state()
    for i in range(2):
        kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                           cid=f"proto_kk_p{i}"))
    _breakwater(st)
    kokomi_plan.resolve_front(st)      # hurries proto_kk_p0 out of the queue
    st.player.energy = 0
    st.player.block = 0
    kokomi_plan.resolve_dusk(st)
    assert st.player.block == 5 + 3 * 1


def test_breakwaters_count_is_not_the_mornings_depth(overhaul):
    """`EB-685`. The two counts part here, which is the whole pass: a deep
    morning already drained buys nothing, and the queue written after it
    buys the wall."""
    st = kokomi_state()
    for i in range(3):
        kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}],
                                           cid=f"proto_kk_m{i}"))
    kokomi_plan.resolve_all(st)
    assert st.kk_plans_this_morning == 3
    _breakwater(st)
    st.player.block = 0
    kokomi_plan.resolve_dusk(st)
    assert st.player.block == 5


def test_slack_waters_plan_half_is_a_morning_line(overhaul):
    """R267 PICK 1. The starter is back to exactly its pre-pass-five form: 4
    damage and a single Weak now, the multi-body Weak next morning. The Plan
    half is what makes turn one a choice -- one Weak on the front enemy today
    or one on every body tomorrow -- which is the brief's turn-one decision,
    and `ProtoKkSlackWater.OnPlay` schedules with no `dusk:` argument."""
    row = _row("proto_kk_slack_water")
    assert row.plan_dusk is False
    assert row.effects == [
        {"op": "damage", "amount": 4, "target": "enemy"},
        {"op": "apply_power", "power": "weak", "amount": 1,
         "target": "enemy"},
    ]
    assert row.plan == [{"op": "apply_power", "power": "weak", "amount": 1,
                         "target": "all_enemies"}]


def test_slack_waters_weak_waits_for_the_next_morning(overhaul):
    """R267 PICK 1. The multi-body Weak is a MORNING line again, so writing it
    on turn one buys the whole board a debuff a turn later rather than now --
    the trade the brief names as the kit's turn-one decision. The Plan is
    still on the queue when the player's turn ends, and it lands when the next
    morning drains."""
    from tier0.engine import combat

    front = make_enemy(hp=80, name="front", intents=ATTACKER)
    back = make_enemy(hp=80, name="back", intents=ATTACKER)
    st = kokomi_state(enemies=[front, back])

    def write_it(state):
        kokomi_plan.schedule(state, _row("proto_kk_slack_water"))

    combat._player_turn(st, write_it)
    # NOTHING LANDED THIS TURN: the Plan is held, which is what makes writing
    # it a bet on the turn after.
    assert front.powers.get("weak") is None
    assert back.powers.get("weak") is None
    assert len(st.kk_plan_queue) == 1
    kokomi_plan.resolve_all(st)
    assert front.powers.get("weak") == 1
    assert back.powers.get("weak") == 1
    assert st.kk_plan_queue == []


def test_the_three_rider_faces_print_the_window_the_rider_lives_in(overhaul):
    """`EB-645`. The rider is spent by the entry carried out immediately after
    this one IN THIS DRAIN, and a face that did not say so read as a promise
    about the whole fight."""
    faces = _faces()
    # THE 2026-09-25 TEXT PASS retired "carried out with this one", the
    # census's example of undefined jargon. "The Plan after this one" is the
    # same window in plain words on all three rider faces -- the next entry in
    # the drain, and the entries behind this one in it -- where "your next
    # Plan" read as the next one WRITTEN (`EB-687`, `EB-645`).
    assert faces["proto_kk_second_wave"] == (
        "Deal 7 [gold]Hydro[/gold] damage. [gold]Plan[/gold]: The [gold]Plan[/gold] "
        "after this one is carried out twice.")
    assert faces["proto_kk_opening_gambit"].endswith(
        "The [gold]Plan[/gold] after this one deals double damage.")
    # Scout Ahead, the third, was cut in the cleanup pass (2026-09-29).
    for face in faces.values():
        assert "carried out with this one" not in face


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

def test_feint_pays_three_per_carry_out(overhaul):
    """THE CASKET PASS (2026-09-28): "Deal 4 damage, plus 3 for each Plan
    carried out this turn. Plan: Apply 1 Vulnerable." The count is the one
    Sango Isshin reads, so "carried out this turn" has one definition. A base
    of 6 since the cleanup pass (2026-09-29)."""
    row = _row("proto_kk_feint")
    assert row.effects == [{"op": "damage", "target": "enemy",
                            "amount_formula": {
                                "base": 6, "per": 3,
                                "count": "plans_carried_out_this_turn"}}]
    assert row.plan == [{"op": "apply_power", "power": "vulnerable",
                         "amount": 1, "target": "front_enemy"}]
    enemy = make_enemy(hp=100)
    st = kokomi_state(enemies=[enemy])
    effects.resolve_card(st, row)
    assert 100 - enemy.hp == 6
    carry_out(st, [{"op": "draw", "amount": 1}])
    carry_out(st, [{"op": "draw", "amount": 1}])
    before = enemy.hp
    effects.resolve_card(st, row)
    assert before - enemy.hp == 6 + 3 * 2

def test_feints_upgrade_moves_the_base_and_the_plans_vulnerable(overhaul):
    """Base 6 -> 9 (the cleanup pass, 2026-09-29), 3 per carry-out
    unchanged, the Plan's Vulnerable 1 -> 2. Read off the SMITHED card."""
    from tier0.content import upgrades

    row = _row("proto_kk_feint")
    assert row.upgrade == {"formula_base": 3, "plan_power_amount": 1}
    up = upgrades.apply_upgrade(_row("proto_kk_feint"))
    assert up.effects[0]["amount_formula"]["base"] == 9
    assert up.effects[0]["amount_formula"]["per"] == 3
    assert up.plan[0]["amount"] == 2

def test_feints_face_prints_the_plan_line_it_can_write(overhaul):
    """`EB-660`: the face prints its Plan line. Since R276 pick 1 the line is
    a debuff ready before the enemy's next swing, not the hit made bigger."""
    faces = _faces()
    assert "[gold]Plan[/gold]: Apply 1 [gold]Vulnerable[/gold]." in \
        faces["proto_kk_feint"]


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


def test_night_watch_is_off_the_sheet_and_out_of_the_pool(overhaul):
    """`EB-685`, pool pass five: it lost every draft comparison in r27 and
    Slack Water's Dusk half is its job. It spelled no op of its own, so
    nothing stays registered behind it the way `cancel_all_plans_cash` and
    `redirect_queued_plans` do."""
    assert "proto_kk_night_watch" not in {
        c.id for c in loader.prototype_cards()}
    assert "proto_kk_night_watch" not in C.KOKOMI_OVERHAUL_POOL_IDS


def test_breakwaters_upgrade_moves_the_base_and_not_the_rate(overhaul):
    """`EB-679`. `plan_block` binds to the FLAT clause first
    (`upgrades.PLAN_DELTA_OPS`), so the wall gets taller and the morning it
    reads is priced the same."""
    from tier0.content import upgrades

    up = upgrades.apply_upgrade(_row("proto_kk_breakwater"))
    assert up.plan == [{"op": "block", "amount": 7},
                       {"op": "block_per_plan_held", "amount": 3}]


def test_riptide_adds_its_rider_per_debuffed_body(overhaul):
    """The AoE rider CANNOT fold -- one printed number would have to stand for
    a board that takes several -- so it is added per enemy, and the clean
    enemy takes the base alone. `ProtoKkRiptide`'s emitted loop is the twin."""
    clean = make_enemy(hp=200)
    sick = make_enemy(hp=200)
    sick.powers["weak"] = 1
    st = kokomi_state(enemies=[clean, sick])
    row = _row("proto_kk_riptide")
    # 11 and 3 more since the Casket pass (2026-09-28).
    assert row.effects[0]["bonus_vs_debuff"] == 3
    effects.resolve_card(st, row)
    assert 200 - clean.hp == 11
    assert 200 - sick.hp == 14


def test_riptides_base_and_rider_upgrade_by_different_amounts(overhaul):
    """14 / 4 more (the Casket pass, 2026-09-28): the `damage` key moves the
    base it rides on and `bonus_vs_debuff` moves the rider's own number. The
    Plan's draw goes 2 -> 3 ([USER], 2026-09-30); its 2 Energy does not move."""
    from tier0.content import upgrades

    up = upgrades.apply_upgrade(_row("proto_kk_riptide"))
    assert up.effects[0]["amount"] == 14
    assert up.effects[0]["bonus_vs_debuff"] == 4
    assert up.plan == [{"op": "energy", "amount": 2},
                       {"op": "draw", "amount": 3}]


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
    row = _row("proto_kk_breakwater")
    assert row.effects == []
    assert kokomi_plan.plan_aimed_at_pet(st, row) is True


def test_an_auto_play_never_aims_at_the_pet(overhaul):
    """`EB-347`. THE PET IS A DELIBERATE TARGET, AND AN AUTO-PLAY HAS NO HAND
    ON THE MOUSE.

    THE FIND (Kokomi r4d act 1, fight 3). Uproar's "Play a random Attack from
    your Draw Pile" pulled `Slack Water` and wrote it onto the Bake-Kurage as a
    Plan instead of playing it at the enemy -- 0 damage on a turn priced at 12
    -- while one fight earlier the identical card pulled by the identical
    Uproar had gone at the enemy.

    Both auto-play doors are read: the base game's forced-random plays
    (`force_random_targeting`, set by `_free_play` for Havoc, Cascade, Uproar
    and the on-exhaust sweep) and the jellyfish's own replay
    (`kurage_autoplaying`). The C# twin is `KokomiPlan.PlayedOnPet`, which
    asks `cardPlay.IsAutoPlay`.

    Seen to FAIL: the empty-now-line card below plans on every read before
    this row, free play or not.
    """
    card = plan_card([{"op": "draw", "amount": 1}])
    st = kokomi_state(enemies=[make_enemy(intents=ATTACKER)])
    # The pilot's own rule still says yes on a deliberate play.
    assert kokomi_plan.plan_aimed_at_pet(st, card) is True

    st.force_random_targeting = True
    assert kokomi_plan.plan_aimed_at_pet(st, card) is False
    st.force_random_targeting = False

    st.kurage_autoplaying = True
    assert kokomi_plan.plan_aimed_at_pet(st, card) is False
    st.kurage_autoplaying = False
    assert kokomi_plan.plan_aimed_at_pet(st, card) is True


# --- R276 pick 2, now on the card (2026-10-05), and her Ancient ------------

def _arm_card(cid):
    return next(c for c in loader.prototype_cards() if c.id == cid)


def test_r276_her_damaging_skills_apply_hydro_face_up(overhaul):
    """Opening Gambit and Second Wave are Skills whose face-up half prints
    "Deal 7 [gold]Hydro[/gold] damage". R276 pick 2 got them there through an
    arm-wide rule; [USER] retired that rule on 2026-10-05 ("that effect just
    lives in the card pool as a symbol on relevant elemental cards"), so each
    row declares `applies_element: true` and the hit is Hydro because the
    CARD says so. `CatalystCadence.PrintedElement` is the twin."""
    st = kokomi_state()
    # Chain of Command left the pool in the status batch (2026-10-01).
    for cid in ("proto_kk_opening_gambit", "proto_kk_second_wave"):
        card = _arm_card(cid)
        assert card.type == "skill", cid
        hit = next(fx for fx in card.effects if fx["op"] == "damage")
        assert effects._element_for(st, hit, card) == "hydro", cid


def test_r276_the_base_strike_and_klee_are_outside_it(overhaul):
    """The base game's Strike applies nothing, and a damaging Skill that
    declares no element applies nothing in anyone's seat."""
    st = kokomi_state()
    strike = loader.get_card("strike")
    assert effects._element_for(st, strike.effects[0], strike) is None

    klee = make_state()
    klee.player.character_id = "klee"
    klee.player.element = "pyro"
    klee.player.cadence = "catalyst"
    skill = Card(id="probe_skill", name="probe", cost=1, type="skill",
                 effects=[{"op": "damage", "amount": 3, "target": "enemy"}])
    assert effects._element_for(klee, skill.effects[0], skill) is None


def test_a_no_element_mod_damage_card_played_by_kokomi_applies_nothing(
        overhaul):
    """[USER], 2026-10-05: "I think that that Kokomi effect is a legacy
    design. We changed things (or tried to change them) so that that effect
    just lives in the card pool as a symbol on relevant elemental cards and
    the card states 'deals [element] damage' or 'applies [element]'."

    Furina's Surging Waters (Cheered On until the Salon's Tab, 2026-10-05)
    is a mod-authored Attack that deals damage and names no element. In Kokomi's hand the sim used to read nothing (off-sheet) and
    the mod Hydro (the character fallback); both now read the CARD, and it
    says nothing. Klee's Forbidden Fun, which prints Pyro, keeps its Pyro in
    Kokomi's hand -- the element comes with the card. C# twin:
    `KokomiR276Tests.A_no_element_mod_damage_card_played_by_kokomi_applies_nothing`."""
    st = kokomi_state()
    cheered = _arm_card("proto_fs_surging_waters")
    assert (cheered.type, cheered.character) == ("attack", "furina")
    hit = next(fx for fx in cheered.effects if fx["op"] == "damage")
    assert effects._element_for(st, hit, cheered) is None

    fun = _arm_card("proto_ko_forbidden_fun")
    hit = next(fx for fx in fun.effects if fx["op"] == "damage")
    assert effects._element_for(st, hit, fun) == "pyro"


def test_r276_princess_of_watatsumi_pays_on_every_plan_under_the_arm(overhaul):
    """Her Ancient under the arm: "Whenever the Bake-Kurage carries out a
    Plan, gain 2 Block and draw 1 card." Every Plan, not once a turn. (The
    shipped Charge drip its row still applies is read by nothing: Charge left
    the sim on 2026-10-08.)"""
    st = kokomi_state()
    st.player.draw_pile = [loader.get_card("defend") for _ in range(5)]
    princess = loader.get_card("princess_of_watatsumi")
    effects.resolve_card(st, princess)
    assert st.player.powers[kokomi_plan.PRINCESS_OF_WATATSUMI] == 2

    clause = [{"op": "block", "amount": 1}]
    kokomi_plan.schedule(st, plan_card(clause))
    kokomi_plan.schedule(st, plan_card(clause))
    hand, block = len(st.player.hand), st.player.block
    kokomi_plan.resolve_all(st)
    assert st.player.block == block + 2 * (1 + 2)
    assert len(st.player.hand) == hand + 2


def test_r276_princess_upgrades_to_three_block():
    up = loader.get_card("princess_of_watatsumi+")
    amounts = {fx["power"]: fx["amount"] for fx in up.effects}
    assert amounts == {"charge_per_turn": 4,
                       kokomi_plan.PRINCESS_OF_WATATSUMI: 3}


# --- R276 pick 1: the halves rewrite's five new Plan clauses ---------------

def _attack(amount=5, cid="proto_kk_probe_attack"):
    return Card(id=cid, name="a", cost=1, type="attack",
                effects=[{"op": "damage", "amount": amount,
                          "target": "enemy"}])


def test_r276_pincer_plays_the_first_face_up_attack_twice(overhaul):
    """Pincer's Plan: "This turn, your first Attack is played twice." A write
    neither takes nor spends it; the first face-up Attack does."""
    from tier0.engine import combat
    enemy = make_enemy(hp=200, intents=ATTACKER)
    st = kokomi_state(enemies=[enemy])
    carry_out(st, _arm_card("proto_kk_pincer").plan)
    assert st.player.powers[kokomi_plan.FIRST_ATTACK_TWICE] == 1

    # A WRITE: an Attack with no now-line goes onto the Bake-Kurage.
    written = Card(id="proto_kk_w", name="w", cost=0, type="attack",
                   effects=[], plan=[{"op": "draw", "amount": 1}])
    st.player.hand.append(written)
    st.player.energy = 9
    combat.play_card(st, written)
    assert len(st.kk_plan_queue) == 1, "one write, not two"
    assert st.player.powers[kokomi_plan.FIRST_ATTACK_TWICE] == 1

    attack = _attack(5)
    st.player.hand.append(attack)
    combat.play_card(st, attack)
    assert enemy.hp == 200 - 2 * 5
    assert kokomi_plan.FIRST_ATTACK_TWICE not in st.player.powers

    second = _attack(5, cid="proto_kk_probe_attack_2")
    st.player.hand.append(second)
    combat.play_card(st, second)
    assert enemy.hp == 200 - 3 * 5, "only the FIRST Attack is doubled"


def test_r276_stolen_chapter_makes_the_first_card_free(overhaul):
    """Stolen Chapter's Plan: "This turn, the first card you play costs 0."
    Pure at the cost seam, spent by the first card paid for."""
    from tier0.engine import combat
    st = kokomi_state(enemies=[make_enemy(hp=200)])
    carry_out(st, _arm_card("proto_kk_stolen_chapter").plan)
    first = Card(id="proto_kk_c1", name="c1", cost=2, type="skill",
                 effects=[{"op": "block", "amount": 1}])
    second = Card(id="proto_kk_c2", name="c2", cost=2, type="skill",
                  effects=[{"op": "block", "amount": 1}])
    assert combat.card_cost(st, first) == 0
    assert combat.card_cost(st, first) == 0, "asking does not spend it"
    st.player.hand += [first, second]
    st.player.energy = 3
    combat.play_card(st, first)
    assert st.player.energy == 3
    assert combat.card_cost(st, second) == 2
    combat.play_card(st, second)
    assert st.player.energy == 1


def test_r276_tide_wall_blocks_the_front_enemys_intent(overhaul):
    """Tide Wall's Plan: 6 Block (9 upgraded) plus the damage the front enemy
    intends to deal -- every hit of a multi-hit intent. A non-attack intent
    adds 0, so an Empower turn still pays the flat 6 (the cleanup pass,
    2026-09-29)."""
    front = make_enemy(hp=40, intents=[{"kind": "attack", "amount": 6,
                                        "times": 2}])
    behind = make_enemy(hp=40, intents=[{"kind": "attack", "amount": 20}])
    st = kokomi_state(enemies=[front, behind])
    st.player.block = 0
    assert kokomi_plan.front_intent_damage(st) == 12
    carry_out(st, _arm_card("proto_kk_tide_wall").plan)
    assert st.player.block == 6 + 12

    st = kokomi_state(enemies=[make_enemy(hp=40, intents=BLOCKER)])
    st.player.block = 0
    carry_out(st, _arm_card("proto_kk_tide_wall").plan)
    assert st.player.block == 6, "a non-attack intent reads 0, plus 6"

    from tier0.content import upgrades
    up = upgrades.apply_upgrade(_arm_card("proto_kk_tide_wall"))
    st = kokomi_state(enemies=[make_enemy(hp=40, intents=BLOCKER)])
    st.player.block = 0
    carry_out(st, up.plan)
    assert st.player.block == 9, "a non-attack intent reads 0, plus 9"


# --- the Kokomi core pass (review/active/kokomi-core-pass-2026-09-27.md) ---

def _up(cid):
    return loader.get_card(cid + "+")


_VULN2 = {"op": "apply_power", "power": "vulnerable", "amount": 2,
          "target": "enemy"}
_DRAW2_DISCARD1 = [{"op": "draw", "amount": 2},
                   {"op": "discard", "amount": 1, "select": "chosen"}]
_COC_NOW = {"op": "damage", "target": "enemy",
            "amount_formula": {"base": 0, "per": 3,
                               "count": "companions_played_this_turn"}}


@pytest.mark.parametrize("cid,now,plan,up_now,up_plan", [
    ("proto_kk_ambush", [_VULN2],
     [{"op": "damage", "amount": 12, "target": "front_enemy"}],
     [_VULN2], [{"op": "damage", "amount": 15, "target": "front_enemy"}]),
    # 2026-10-05: the row declares the Hydro its face prints.
    ("proto_kk_second_wave", [{"op": "damage", "amount": 7,
                               "target": "enemy", "applies_element": True}],
     [{"op": "next_plan_extra_carry_out"}],
     [{"op": "damage", "amount": 9, "target": "enemy",
       "applies_element": True}],
     [{"op": "next_plan_extra_carry_out"}]),
])
def test_core_pass_rows_and_upgrades(overhaul, cid, now, plan, up_now,
                                     up_plan):
    row = _row(cid)
    assert row.effects == now
    assert row.plan == plan
    up = _up(cid)
    assert up.effects == up_now
    assert up.plan == up_plan


@pytest.mark.parametrize("cid,power,amount,up_amount", [
    # Song of Pearls was cut in the cleanup pass (2026-09-29); its power stays
    # registered and is pinned directly above.
    ("proto_kk_treatise", kokomi_plan.TREATISE, 1, 1),
])
def test_core_pass_powers_and_upgrades(overhaul, cid, power, amount,
                                       up_amount):
    row = _row(cid)
    assert row.effects == [{"op": "apply_power", "power": power,
                            "amount": amount, "target": "self"}]
    up = _up(cid)
    assert up.effects[0]["amount"] == up_amount


def test_core_pass_treatise_upgrade_is_innate(overhaul):
    assert _row("proto_kk_treatise").upgrade == {"innate": True}
    assert _up("proto_kk_treatise").innate


def test_core_pass_faces(overhaul):
    faces = _faces()
    assert faces["proto_kk_ambush"] == (
        "Apply 2 [gold]Vulnerable[/gold]. [gold]Plan[/gold]: Deal 12 [gold]Hydro[/gold] damage.")
    assert faces["proto_kk_treatise"] == (
        "Once per turn, when you play a card with a [gold]Plan[/gold] line "
        "normally, draw 1 card.")


def test_core_pass_second_waves_hit_applies_hydro(overhaul):
    """Every damaging card of hers applies Hydro, Skills included."""
    st = kokomi_state()
    card = _row("proto_kk_second_wave")
    assert card.type == "skill"
    assert effects._element_for(st, card.effects[0], card) == "hydro"


def _companion(cid="proto_kk_probe_companion", cost=2):
    return Card(id=cid, name="c", cost=cost, type="skill",
                effects=[{"op": "block", "amount": 1}], tags=["companion"])


