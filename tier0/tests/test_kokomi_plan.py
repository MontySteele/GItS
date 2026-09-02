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
    out -- `test_kokomi_overhaul.overhaul`'s fixture, for its reasons."""
    loader._card_prototype.cache_clear()
    rewards.character_pool.cache_clear()
    monkeypatch.setattr(C, "KOKOMI_OVERHAUL", True)
    yield
    loader._card_prototype.cache_clear()
    rewards.character_pool.cache_clear()


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
    assert len(planned) == 16
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


def test_damage_to_every_enemy(overhaul):
    a, b = make_enemy(hp=40, name="a"), make_enemy(hp=40, name="b")
    st = kokomi_state(enemies=[a, b])
    carry_out(st, [{"op": "damage", "amount": 5, "target": "all_enemies"}])
    assert (a.hp, b.hp) == (35, 35)


def test_a_planned_hit_is_hers_and_applies_hydro(overhaul):
    """RULE 3's other half: "your Strength and Dexterity count, and planned
    damage from an Attack applies Hydro the way her Attacks do." The C# gets
    both from one call -- `ElementalHit.Deal(..., kokomi)` -- and this engine
    gets both from `deal_damage_to_enemy(..., element="hydro")`, whose dealer
    is always the player."""
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    st.player.powers["strength"] = 3
    carry_out(st, [{"op": "damage", "amount": 9, "target": "front_enemy"}])
    assert enemy.hp == 40 - 12
    assert enemy.aura == "hydro"


def test_damage_quarter_max_hp_rounds_down(overhaul):
    """Sango Isshin. ONE formula, read by the now-line and the planned half
    alike, so they cannot round differently (`KokomiRules.QuarterOfMaxHp`)."""
    enemy = make_enemy(hp=60)
    st = kokomi_state(enemies=[enemy], hp=81)
    assert kokomi_plan.quarter_of_max_hp(st) == 20
    carry_out(st, [{"op": "damage_quarter_max_hp", "target": "all_enemies"}])
    assert enemy.hp == 40


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

def test_plan_twice_doubles_every_plan_but_not_its_own(overhaul):
    """THE READING the C# records at `ResolveAll`: `CarryOutTimes` is asked
    INSIDE the drain loop, before each entry, so the Rare's own clause -- which
    is what installs the doubling -- does not double itself, and every Plan
    written after it in the same morning is doubled."""
    enemy = make_enemy(hp=90)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, plan_card([{"op": "plan_twice", "amount": 2}]))
    kokomi_plan.schedule(st, plan_card([{"op": "damage", "amount": 5,
                                         "target": "front_enemy"}]))
    kokomi_plan.resolve_all(st)
    # The Ascension resolved ONCE (a second resolution would only re-wear the
    # same window), and the hit behind it resolved TWICE.
    assert st.player.powers[kokomi_plan.PLAN_TWICE] == 2
    assert enemy.hp == 90 - 10


def test_a_second_ascension_extends_the_window_and_never_doubles_it(overhaul):
    """`PlanTwicePower.Wear` tops the window UP to `turns` and returns early
    when it is already there -- "the same construction every other windowed
    power in this mod takes". `apply_power` is additive, so the top-up is a
    DELTA and not the printed amount."""
    st = kokomi_state()
    kokomi_plan.wear_plan_twice(st, 2)
    kokomi_plan.wear_plan_twice(st, 2)
    assert st.player.powers[kokomi_plan.PLAN_TWICE] == 2
    kokomi_plan.wear_plan_twice(st, 3)
    assert st.player.powers[kokomi_plan.PLAN_TWICE] == 3
    kokomi_plan.wear_plan_twice(st, 1)
    assert st.player.powers[kokomi_plan.PLAN_TWICE] == 3


def test_the_window_ticks_at_the_end_of_her_turn(overhaul):
    st = kokomi_state()
    kokomi_plan.wear_plan_twice(st, 2)
    kokomi_plan.tick_windows(st)
    assert st.player.powers[kokomi_plan.PLAN_TWICE] == 1
    kokomi_plan.tick_windows(st)
    assert kokomi_plan.PLAN_TWICE not in st.player.powers


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

    def child(_state, _entry, _clause):
        kokomi_plan.schedule(st, written)

    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}]))
    original = kokomi_plan._resolve_clause
    kokomi_plan._resolve_clause = child
    try:
        kokomi_plan.resolve_all(st)
    finally:
        kokomi_plan._resolve_clause = original
    assert [e.card_id for e in st.kk_plan_queue] == ["proto_kk_child"]


def test_plans_also_happen_now_and_are_still_queued(overhaul):
    """The Moon Overlooks the Waters, and "also" taken at its word -- the C#'s
    reading, with its argument: reading it as "instead" would DELETE rule 2
    rather than break it."""
    enemy = make_enemy(hp=40)
    st = kokomi_state(enemies=[enemy])
    st.player.powers[kokomi_plan.PLANS_ALSO_NOW] = 1
    kokomi_plan.schedule(st, plan_card([{"op": "damage", "amount": 6,
                                         "target": "front_enemy"}]))
    assert enemy.hp == 34                      # it happened NOW
    assert len(st.kk_plan_queue) == 1          # and it is still queued
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 28


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
    else, so the Rare's window pays the MORNING and not this card. Taken from
    the C#'s shape literally rather than argued here."""
    st = kokomi_state()
    st.player.energy = 0
    kokomi_plan.wear_plan_twice(st, 2)
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
    """'Whenever the jellyfish carries out a Plan' is once per ENTRY. War
    Council prints two clauses and is ONE Plan, which is what its face says --
    "Deal 4 damage to every enemy AND apply 1 Weak to each" is one sentence."""
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


def test_the_bus_pays_the_also_now_resolution_too(overhaul):
    """The C#: "the notify at the bottom is the only place that fires -- so The Moon
    Overlooks the Waters' extra resolution pays them too, which is what 'also
    happen now' says."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.SONG_OF_PEARLS] = 3
    st.player.powers[kokomi_plan.PLANS_ALSO_NOW] = 1
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}]))
    assert st.player.block == 3                 # the now-resolution
    kokomi_plan.resolve_all(st)
    assert st.player.block == 6                 # and the morning's


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


def test_the_generals_banner_weaks_the_front_enemy_per_companion_play(overhaul):
    """PER PLAY AND NOT PER CARD, and the front enemy is `front_enemy`'s --
    the same reader a planned hit uses, so "the front enemy" means one thing
    in this arm and is defined once."""
    front, back = make_enemy(name="front"), make_enemy(name="back")
    st = kokomi_state(enemies=[front, back])
    st.player.powers[kokomi_plan.GENERALS_BANNER] = 1
    card = companion_card()
    kokomi_plan.note_companion_played(st, card)
    kokomi_plan.note_companion_played(st, card)
    assert front.powers["weak"] == 2
    assert "weak" not in back.powers


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
    Field's planned Block, Coral Bulwark's, Cleansing Wave's and Battle Plan's
    planned Energy would all be wiped by the setup that follows them.

    This is that claim made falsifiable: a Plan written on turn N leaves Block
    and Energy standing when the pilot gets to decide on turn N+1.
    """
    ids = ["proto_kk_read_the_field"] * 4 + ["proto_kk_battle_plan"] * 4
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
    # its Battle Plan Plans wrote (2 apiece, past an energy reset that would
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
    """`plan_twice` and `damage_per_companion_last_turn` are legal inside a
    `plan:` list and nowhere else. They stay in `effects.OPS` because the
    loader validates a `plan:` list through the same vocabulary check the body
    takes; reaching one from a BODY is a defect, and it says so."""
    st = kokomi_state()
    for op in sorted(kokomi_plan.PLAN_ONLY_OPS):
        card = Card(id="proto_kk_probe", name="probe", cost=1, type="skill",
                    effects=[{"op": op, "amount": 1}])
        with pytest.raises(NotImplementedError, match="PLAN-ONLY"):
            effects.OPS[op](st, card.effects[0], card)
