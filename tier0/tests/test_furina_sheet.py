"""Furina sheet pass 1: the card pool, Salon Members, Fanfare payoffs,
Guest Star generation, Encore Performance, Spotlight texture powers and
the Burst meter (docs/furina-cards.yaml; furina-sheet-pass-1-plan.md).
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, refpowers
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy

NULL_PILOT = lambda s: None


def test_sheet_comments_match_numbers():
    """Sheet red-pen flag 1 (2026-07-20): comments quoting stale numbers
    are tuning-round drift ("Eight points" over amount: 6, caught live).
    The lint is heuristic; a `lint-ok` marker exempts a comment line."""
    import subprocess
    import sys
    repo = loader.DOCS_DIR.parent
    proc = subprocess.run(
        [sys.executable, str(repo / "tools" / "lint_sheet_comments.py"),
         str(loader.DOCS_DIR / "furina-cards.yaml")],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def furina_state(enemies=None, seed=0):
    p = loader.build_player("furina")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def hand_card(state, cid):
    card = loader.get_card(cid)
    state.player.hand.append(card)
    return card


# --- pool composition (template §3.4: the 75-card floor, Klee-shape) ---

def test_pool_composition():
    cards = [c for c in loader._card_index().values()
             if c.character == "furina" and not c.is_companion]
    by_rarity = {}
    for c in cards:
        by_rarity.setdefault(c.rarity, []).append(c)
    assert len(by_rarity["basic"]) == 5          # template §3.4 allows 4-5
    # Curtain Call (R85, 2026-07-27): the ratified §4 shape. The old 33/25/15
    # was rarity-inverted against the official 23/42/30 band, and payoffs are
    # legal only at U/R under the deck-size grammar -- 11 promotions moved
    # the pool to bottom-light. Pool size stays 78 (frozen); the type quota
    # (17 attack / 46 skill / 15 power) is pinned below.
    # PLAYTEST-2 RED-PEN (2026-07-28) moved every number on this block; the
    # pool-size freeze is broken for the first time since Curtain Call.
    #   77 (was 78): A4 CUT rising_tide.
    #   common 19 (was 22): -1 the cut, -2 to uncommon (A1 curtain_cue,
    #     A2 limelight, both promoted for having U-grade Official effects).
    #   uncommon 34 (was 32): +2 those promotions.
    #   rare 19: unchanged. A7 reshaped unheard_confession but did not move it.
    #   78 again, common 20: A12 ADDED the salon cap-raise power (box_seats,
    #     RENAMED to casting_call by the Fanfare rework, Track C.4).
    #     The pool leaves THAT sprint the size it entered, by two opposite
    #     rulings rather than by nothing having happened.
    #   79, uncommon 35: the FANFARE REWORK (2026-07-28) added ONE card --
    #     take_your_bow, the Track D on-demand-bow probe. One card, not a
    #     family: it is a probe and the next playtest is its measurement.
    #     Track C rewrote three cards in place (graceful_retreat,
    #     the_final_verdict, blocking_notes) and renamed a fourth, none of
    #     which moves a count. (lint-ok: pool sizes)
    #   82, common 23: the COMPENSATION PASS (2026-07-28) added THREE common
    #     readers -- applause_line, held_breath, breathless -- because the
    #     archetype's readers clustered at rare (8 of 10) and its commons were
    #     blind Encore batteries. Track 1 put "Fanfare Cap +X" on twelve more
    #     Powers and Track 2 rewrote three cards in place; neither moves a
    #     count. (lint-ok: pool sizes)
    assert len(cards) == 82
    assert len(by_rarity["common"]) == 23
    assert len(by_rarity["uncommon"]) == 35
    assert len(by_rarity["rare"]) == 19
    kit = [c for c in by_rarity["rare"] if c.kit_card]
    assert [c.id for c in kit] == ["let_the_people_rejoice"]   # 18 draftable
    by_type = {}
    for c in cards:
        by_type.setdefault(c.type, []).append(c)
    # Attack landed at 15, not §4's 17: the pre-registered Track B shrink
    # clause fired on the cell-3 hydro-uptime breach and reverted the
    # flood_of_emotion + matinee_performance retypes (sprint log §6 cell 3).
    # Type quota, also moved by the 2026-07-28 red-pen:
    #   attack 16 (was 15): A5 retyped undercurrent skill -> attack.
    #   skill  45 (was 48): -1 that retype, -1 A4's cut, -1 A7's retype.
    #   power  17 (was 15): +1 A7 retyped unheard_confession skill -> power,
    #     +1 A12's new power card.
    assert len(by_type["attack"]) == 18          # 16 -> 18: applause_line and breathless are
                                                 # the compensation pass's two new attacks
    assert len(by_type["skill"]) == 47           # skill-heavy pole+, the cadence reason
                                                 # (46 -> 47: held_breath)
    assert len(by_type["power"]) == 17           # official quota floor (19-21% roster-wide)


def test_starter_invitation_and_aria_curve():
    starter = loader.starting_deck("furina")
    assert len(starter) == 10
    assert starter.count("aria_of_recompense") == 1
    assert starter.count("an_invitation") == 1

    aria = loader.get_card("aria_of_recompense")
    aria_plus = loader.get_card("aria_of_recompense+")
    # COMPENSATION Track 2.4 VETOED (R130, 2026-08-07): the starter does not
    # get a payoff. Aria is a PURE Encore card -- no Fanfare reader clause --
    # and the upgrade moves only the Encore number and the Innate flag.
    assert aria.effects == [{"op": "gain_encore", "amount": 5}]
    assert aria_plus.effects == [{"op": "gain_encore", "amount": 8}]

    stage = loader.get_card("stage_presence")
    stage_plus = loader.get_card("stage_presence+")
    assert stage.effects == [{"op": "block", "amount": 6}]
    assert stage_plus.effects == [{"op": "block", "amount": 9}]


def test_no_furina_card_declares_the_retired_spend_grammar():
    """F-A4 at the sheet level: the seven gates are gone from every row.

    The energy costs are asserted unchanged deliberately -- they were priced
    as DISCOUNTED against ordinary finishers because the card also paid a
    Fanfare toll. That toll is now gone and the discount is not, which is a
    real repricing question and it belongs to F-B1, not here. Pinning the
    current numbers makes that pass a visible edit rather than a silent one.
    """
    for cid in ("dramatic_entrance", "thunderous_ovation", "crescendo",
                "florid_cadenza", "flood_of_emotion", "universal_revelry",
                "high_tide"):
        assert not hasattr(loader.get_card(cid), "fanfare_cost")

    assert loader.get_card("crescendo").cost == 1
    assert loader.get_card("florid_cadenza").cost == 0
    assert loader.get_card("flood_of_emotion").cost == 1
    assert loader.get_card("universal_revelry").cost == 2
    assert loader.get_card("high_tide").cost == 1


def test_the_constellation_card_grants_a_floor_not_a_cap():
    """F-A5: the uncapper retires with the grammar it policed. The blood
    rider survives F-A on purpose -- dropping it is F-B2's edit."""
    stage = loader.get_card("the_sea_is_my_stage")
    assert {"op": "gain_fanfare_floor", "amount": 15} in stage.effects
    assert not any(fx["op"] == "raise_fanfare_cap" for fx in stage.effects)
    assert loader.get_card("the_sea_is_my_stage+").effects[0]["amount"] == 20


def test_targeted_fanfare_floor_repairs():
    suffering = loader.get_card("suffering_for_art")
    thunder = loader.get_card("thunderous_ovation")
    # COMPENSATION Track 2.2 (2026-07-28): the flagship conversion. The wound
    # prints the meter and the third clause reads it, so this is the one card
    # in the pool that both pays Fanfare and spends it on the same face.
    assert suffering.effects == [
        {"op": "damage", "amount": 1, "target": "self"},
        {"op": "gain_encore", "amount": 3},
        {"op": "block", "amount": 0, "bonus_formula": "1_per_4_fanfare"},
    ]
    # F-B1 made it a smooth read; Curtain Call C (R85) steepened the rate
    # and moved the card to its rare payoff slot (base 7->6, 1 per 2).
    assert thunder.effects == [
        {"op": "block", "amount": 6, "bonus_formula": "1_per_2_fanfare"},
    ]


def test_every_archetype_has_the_template_shape():
    """Each archetype: enablers commons-heavy, rares as payoffs (§3.3)."""
    cards = [c for c in loader._card_index().values()
             if c.character == "furina" and not c.is_companion]
    for arch in ("salon", "spotlight", "fanfare"):
        tagged = [c for c in cards if arch in c.archetypes]
        assert len(tagged) >= 15, f"{arch}: {len(tagged)} tagged (<15)"
        assert any(c.rarity == "rare" and c.role == "payoff" for c in tagged)


def _walk(effects_list):
    for fx in effects_list:
        yield fx
        for branch in ("then", "else"):
            if isinstance(fx.get(branch), list):
                yield from _walk(fx[branch])


def test_no_passive_accrual_path_on_the_sheet():
    """No Furina card creates a per-turn resource trickle: every Encore/
    Fanfare gain is a played-card activity. The laundering risk (a
    per-turn Encore power -> passive Fanfare via the gain hook) is what
    this guards; the sheet must never author one."""
    cards = [c for c in loader._card_index().values()
             if c.character == "furina"]
    per_turn_powers = {"spark_per_turn", "bomb_and_spark_per_turn"}
    for c in cards:
        for fx in _walk(c.effects):
            assert not (fx.get("op") == "apply_power"
                        and (fx.get("power") in per_turn_powers
                             or "per_turn" in str(fx.get("power")))), c.id


# --- Salon Members (Salon v2 rework 2026-07-23: typed FIFO queue, unique
# ticks/bows, Fanfare-as-Focus; docs/archive/furina-salon-rework-plan.md §1) ---

CRAB_TICK = C.SALON_MEMBERS["crabaletta"]["tick"]["damage"]
CRAB_BOW = C.SALON_MEMBERS["crabaletta"]["bow"]["damage"]
USHER_TICK = C.SALON_MEMBERS["usher"]["tick"]["block"]
USHER_BOW = C.SALON_MEMBERS["usher"]["bow"]["block"]
CHEV_TICK = C.SALON_MEMBERS["chevalmarin"]["tick"]["damage"]
CHEV_BOW_ENCORE = C.SALON_MEMBERS["chevalmarin"]["bow"]["encore"]


def _company(p, *members):
    """Seed the typed queue directly (the deploy op is tested separately);
    the count power mirrors len(queue), same as the engine maintains."""
    p.salon = list(members)
    p.powers["salon_member"] = len(p.salon)


def test_salon_ticks_are_typed_apply_hydro_and_drain_encore():
    st = furina_state()
    p = st.player
    _company(p, "crabaletta", "chevalmarin")
    p.encore = 5
    hp0 = st.enemies[0].hp
    effects.salon_tick(st)
    assert st.enemies[0].hp == hp0 - CRAB_TICK - CHEV_TICK
    assert st.enemies[0].aura == "hydro"            # the application engine
    assert p.encore == 5 - 2 * C.SALON_TICK_ENCORE_COST


def test_usher_ticks_block_not_damage():
    st = furina_state()
    p = st.player
    _company(p, "usher")
    p.encore = 3
    hp0 = st.enemies[0].hp
    effects.salon_tick(st)
    assert st.enemies[0].hp == hp0
    assert p.block == USHER_TICK


def test_dry_salon_ticks_resolve_at_three_quarters_without_overdraw():
    st = furina_state()
    p = st.player
    _company(p, "crabaletta", "crabaletta")
    p.encore = 0
    hp0 = p.hp
    enemy_hp0 = st.enemies[0].hp
    effects.salon_tick(st)
    assert p.hp == hp0
    assert st.enemies[0].hp == (
        enemy_hp0 - 2 * int(CRAB_TICK * C.SALON_DRY_DAMAGE_MULT))
    assert not any(e["event"] == "encore_overdraw" for e in st.log)
    assert p.fanfare == 0


def test_salon_ticks_only_throttle_after_encore_runs_out():
    st = furina_state()
    p = st.player
    _company(p, "crabaletta", "crabaletta")
    p.encore = 1
    enemy_hp0 = st.enemies[0].hp
    effects.salon_tick(st)
    assert p.encore == 0
    assert p.hp == p.max_hp
    assert st.enemies[0].hp == (
        enemy_hp0 - CRAB_TICK
        - int(CRAB_TICK * C.SALON_DRY_DAMAGE_MULT))


def test_fanfare_is_the_focus_term_on_ticks():
    st = furina_state()
    p = st.player
    _company(p, "crabaletta")
    p.encore = 3
    p.fanfare = 2 * C.SALON_FOCUS_PER               # +2 member numbers
    hp0 = st.enemies[0].hp
    effects.salon_tick(st)
    assert st.enemies[0].hp == hp0 - (CRAB_TICK + 2)


def test_deploy_into_full_stage_bows_the_oldest_member_out():
    st = furina_state()
    p = st.player
    _company(p, "crabaletta", "usher", "chevalmarin")
    enemy_hp0 = st.enemies[0].hp
    effects.resolve_card(st, loader.get_card("mademoiselle_crabaletta"))
    assert p.powers["salon_member"] == C.SALON_MEMBER_SLOTS == 3
    assert p.salon == ["usher", "chevalmarin", "crabaletta"]   # FIFO
    assert st.enemies[0].hp == enemy_hp0 - CRAB_BOW  # the OLDEST bowed
    assert st.enemies[0].aura == "hydro"
    assert p.encore == 0                          # final bows have no upkeep
    assert p.burst_energy == C.SALON_TICK_BURST


def test_usher_bow_blocks_and_chevalmarin_bow_mass_applies_with_encore():
    st = furina_state()
    p = st.player
    _company(p, "usher", "chevalmarin", "crabaletta")
    effects.resolve_card(st, loader.get_card("mademoiselle_crabaletta"))
    assert p.block == USHER_BOW                     # oldest = the Usher
    effects.resolve_card(st, loader.get_card("mademoiselle_crabaletta"))
    assert st.enemies[0].aura == "hydro"            # Chevalmarin: mass apply
    # The bow's Encore is engine-side (_salon_bow), not a card rider, so
    # the replacement numeric multiplier never touches it.
    assert p.encore == CHEV_BOW_ENCORE


def test_full_ensemble_deploys_one_of_each_and_bows_a_full_stage():
    st = furina_state()
    p = st.player
    _company(p, "crabaletta", "crabaletta", "crabaletta")
    enemy_hp0 = st.enemies[0].hp
    effects.resolve_card(st, loader.get_card("full_ensemble"))
    assert p.powers["salon_member"] == C.SALON_MEMBER_SLOTS
    assert p.salon == ["usher", "chevalmarin", "crabaletta"]
    assert st.enemies[0].hp == enemy_hp0 - 3 * CRAB_BOW


def test_replacing_member_triples_block_rider_once():
    st = furina_state()
    p = st.player
    _company(p, "crabaletta", "crabaletta", "crabaletta")
    effects.resolve_card(st, loader.get_card("gentilhomme_usher"))
    assert p.powers["salon_member"] == C.SALON_MEMBER_SLOTS
    assert p.block == 4 * C.SALON_REPLACE_DAMAGE_MULT


def test_replacing_member_doubles_encore_rider_once():
    st = furina_state()
    p = st.player
    _company(p, "crabaletta", "crabaletta", "crabaletta")
    effects.resolve_card(st, loader.get_card("surintendante_chevalmarin"))
    assert p.encore == 3 * C.SALON_REPLACE_NUMERIC_MULT


def test_replacement_multiplier_ends_with_the_deploying_card():
    st = furina_state()
    p = st.player
    _company(p, "crabaletta", "crabaletta", "crabaletta")
    effects.resolve_card(st, loader.get_card("surintendante_chevalmarin"))
    after_replacement = p.encore
    effects.resolve_card(st, loader.get_card("curtain_up"))
    assert p.encore == after_replacement + 2


def test_multiple_replacements_do_not_multiply_rider_more_than_once():
    st = furina_state()
    p = st.player
    _company(p, "usher", "usher", "usher")
    effects.resolve_card(st, loader.get_card("grand_gala"))
    assert p.powers["salon_member"] == C.SALON_MEMBER_SLOTS
    assert p.salon == ["crabaletta", "chevalmarin", "usher"]
    assert p.encore == 4 * C.SALON_REPLACE_NUMERIC_MULT


def test_replacing_member_doubles_salon_power_without_clipping():
    st = furina_state()
    p = st.player
    _company(p, "usher", "usher", "usher")
    effects.resolve_card(st, loader.get_card("endless_waltz"))
    assert p.powers["salon_damage_up"] == 3 * C.SALON_REPLACE_NUMERIC_MULT


def test_replacing_member_doubles_draw_rider():
    st = furina_state()
    p = st.player
    _company(p, "usher", "usher", "usher")
    p.encore = 2
    p.draw_pile = [loader.get_card("stage_presence") for _ in range(2)]
    effects.resolve_card(st, loader.get_card("dress_rehearsal"))
    assert len(p.hand) == 2


def test_salon_damage_up_scales_ticks():
    st = furina_state()
    p = st.player
    _company(p, "crabaletta")
    p.powers["salon_damage_up"] = 2
    p.encore = 3
    hp0 = st.enemies[0].hp
    effects.salon_tick(st)
    assert st.enemies[0].hp == hp0 - (CRAB_TICK + 2)


def test_salon_ticks_and_encore_spend_feed_the_burst_meter():
    st = furina_state()
    p = st.player
    _company(p, "crabaletta")
    p.encore = 3
    assert p.burst_max == 70                        # declared this pass
    effects.salon_tick(st)
    # one tick: SALON_TICK_BURST + the tick's own Encore spend
    assert p.burst_energy == (C.SALON_TICK_BURST
                              + C.SALON_TICK_ENCORE_COST
                              * C.BURST_PER_ENCORE_SPENT)


# --- Fanfare payoffs ---

def test_fanfare_bonus_formula_scales_damage():
    st = furina_state()
    st.player.fanfare = 16
    card = Card(id="t", name="t", cost=1, type="attack", character="furina",
                effects=[{"op": "damage", "amount": 8, "target": "enemy",
                          "bonus_formula": "1_per_4_fanfare"}])
    hp0 = st.enemies[0].hp
    effects.resolve_card(st, card)
    assert st.enemies[0].hp == hp0 - (8 + 4)        # +1 per 4, at 16


def test_fanfare_attack_per10_power():
    st = furina_state()
    st.player.fanfare = 25
    st.player.powers["fanfare_attack_per10"] = 1
    hp0 = st.enemies[0].hp
    effects.resolve_card(st, Card(
        id="t", name="t", cost=1, type="attack", character="furina",
        effects=[{"op": "damage", "amount": 5, "target": "enemy"}]))
    assert st.enemies[0].hp == hp0 - (5 + 2)        # +1 per 10, at 25


def test_fanfare_threshold_predicates():
    st = furina_state()
    st.player.fanfare = 12
    assert effects._predicate(st, "fanfare_at_least_10")
    assert not effects._predicate(st, "fanfare_at_least_20")
    st.player.encore = 3
    assert effects._predicate(st, "encore_at_least_3")


def test_uncapper_raises_cap_and_is_inert_without_the_resource():
    st = furina_state()
    cap0 = st.player.fanfare_cap
    effects.resolve_card(st, loader.get_card("the_sea_is_my_stage"))
    assert st.player.fanfare_cap == cap0 + 15
    # Klee has no Fanfare: same card is inert (burst_max pattern)
    klee = loader.build_player("klee")
    stk = CombatState(player=klee, enemies=[make_enemy()],
                      rng=random.Random(0))
    effects.resolve_card(stk, loader.get_card("the_sea_is_my_stage"))
    assert klee.fanfare_cap == 0


# --- Guest Star generation (kickoff §9: four binding guardrails) ---

def test_generation_pool_guardrails():
    for rarity in ("common", "uncommon"):
        pool = loader.guest_star_generation_pool(rarity)
        assert pool, rarity
        # equal-rarity clause
        assert all(c.rarity == rarity for c in pool)
        # shared companions + Guest Star set only; playable characters'
        # personal cards structurally absent
        assert all(c.is_companion or c.guest_star for c in pool)
        assert not any(c.character in ("klee", "furina") for c in pool)
        # sub-Rare pools cannot reach drafted 5-stars; the only star-5
        # rows are the banner-exempt Guest Star cameos themselves
        assert all(c.star != 5 or c.guest_star for c in pool)
    # the Guest Star set is actually reachable
    assert any(c.guest_star for c in loader.guest_star_generation_pool("common"))


def test_generators_exhaust_and_generate_to_hand():
    st = furina_state()
    gen = loader.get_card("an_invitation")
    assert gen.cost == 0
    assert gen.exhaust                              # guardrail b
    effects.resolve_card(st, gen)
    assert len(st.player.hand) == 1
    made = st.player.hand[0]
    assert made.rarity == "common"                  # guardrail c
    assert made.is_companion or made.guest_star     # guardrail d
    assert made.generated_by_guest_star              # combat-local provenance


def test_upgraded_generator_discounts_the_guest():
    """FLAG-2(ii) (R114, Errata Batch 2 item 8): "costs 0 THIS TURN".

    THE ASSERTION THAT MOVED. It used to read `hand[0].cost == 0`, because
    tier0 wrote the override onto the token's printed cost and left it there
    forever. The sheet says "They cost 0 this turn" and the mod says
    `EnergyCost.SetThisTurn(0)`; tier0 was the only one of the three that
    meant "for the rest of the fight". The cost is now asked of
    `combat.card_cost`, which is the only place that can answer a question
    with a turn in it.
    """
    st = furina_state()
    effects.resolve_card(st, loader.get_card("an_invitation+"))
    guest = st.player.hand[0]
    assert combat.card_cost(st, guest) == 0         # Discovery parity
    assert guest.free_this_turn
    assert guest.cost > 0, (
        "the PRINTED cost must survive: a turn-scoped discount that ate the "
        "printed number has nothing to expire back to")

    # and it expires with the turn that granted it
    refpowers.reset_turn_counters(st)
    assert not guest.free_this_turn
    assert combat.card_cost(st, guest) == guest.cost


# --- Encore Performance (the duplication rare; DECISIONS 64) ---

def test_the_copy_carries_the_printed_bound_not_the_instance_s():
    """FLAG-2(i) (R114, Errata Batch 2 item 8): "Copy ops inherit the printed
    card's bounds... the printed bound travels with the copy."

    The copy used to be a deepcopy of the card in hand, so it inherited
    whatever that instance had picked up in combat -- including the LOSS of a
    bound the sheet prints. It is built from `loader.get_card` now, which is
    what the mod has always done (`CreateCard(ModelDb.GetById(id))`, and a
    printed keyword like Exhaust is declared per MODEL).

    WHAT THIS DOES NOT CLOSE, so nobody reads a green bar as X3's repair: a
    copy is still an extra USE of an Exhaust card. No bound printed on one
    instance can limit the number of instances, and the X3 pin still reports.
    """
    st = furina_state()
    p = st.player
    p.spotlight = "furina"
    victim = hand_card(st, "an_invitation")
    victim.exhaust = True                    # pretend the sheet prints it
    printed_cost = victim.cost
    victim.cost = 99                         # and that combat mangled the rest
    effects.resolve_card(st, loader.get_card("encore_performance"))
    copies = [c for c in p.hand if c.id == "an_invitation" and c is not victim]
    assert len(copies) == 1
    copy_ = copies[0]
    assert copy_.cost == printed_cost, "the instance's mangled cost travelled"

    # and the direction that matters: a bound STRIPPED from the instance is
    # restored on the copy, because the copy reads the sheet.
    st2 = furina_state()
    p2 = st2.player
    p2.spotlight = "furina"
    stripped = hand_card(st2, "an_invitation")
    printed_exhaust = loader.get_card("an_invitation").exhaust
    stripped.exhaust = not printed_exhaust
    effects.resolve_card(st2, loader.get_card("encore_performance"))
    made = [c for c in p2.hand
            if c.id == "an_invitation" and c is not stripped]
    assert made and made[0].exhaust == printed_exhaust


def test_the_copy_reads_the_upgraded_sheet_and_none_of_the_instance():
    """FLAG-2(i) (R114, Errata Batch 2 item 8), the half the pin above leaves
    open: "Copy ops inherit the printed card's bounds... the printed bound
    travels with the copy."

    PRINTED includes the upgrade. `loader.get_card` keys off the instance's
    id and the upgraded form rides the `+` convention, so an upgraded target
    copies as upgraded -- a base-id reload would silently downgrade it. What
    stays behind is combat-acquired instance state: a discount some conscript
    wrote into `cost_delta_this_combat` is not on the sheet, so the copy
    arrives at the printed cost and has to be paid for again.

    R118/Q9's `not c.kit_card` exclusion is pinned here too, since nothing
    else in this file reads it through the copy op: her Burst can be
    Spotlighted and in hand and is still not a legal target.
    """
    st = furina_state()
    p = st.player
    p.spotlight = "furina"
    target = hand_card(st, "limelight+")
    printed_cost = loader.get_card("limelight").cost
    target.cost_delta_this_combat = -1               # what a conscript leaves
    assert combat.card_cost(st, target) == printed_cost - 1
    effects.resolve_card(st, loader.get_card("encore_performance"))
    copies = [c for c in p.hand if c is not target]
    assert len(copies) == 1
    copy_ = copies[0]
    assert copy_.id == "limelight+"          # the upgrade is printed: it rides
    assert copy_.effects == loader.get_card("limelight+").effects
    assert copy_.cost_delta_this_combat == 0
    assert combat.card_cost(st, copy_) == printed_cost, (
        "the instance's combat discount travelled to a card the sheet prints "
        "at full price")

    # R118/Q9: the kit is not draftable and not copyable either.
    st2 = furina_state()
    p2 = st2.player
    p2.spotlight = "furina"
    burst = hand_card(st2, "let_the_people_rejoice")
    assert effects.is_spotlighted(st2, burst) and burst.kit_card
    effects.resolve_card(st2, loader.get_card("encore_performance"))
    assert p2.hand == [burst]                        # no target, so no copy


def test_encore_performance_copies_only_the_spotlighted_character():
    st = furina_state()
    p = st.player
    chev = hand_card(st, "chevreuse_interdiction_fire")
    hand_card(st, "lynette_box_trick")
    p.spotlight = "chevreuse"
    effects.resolve_card(st, loader.get_card("encore_performance"))
    copies = [c for c in p.hand if c.character == "chevreuse"]
    assert len(copies) == 2 and copies[1].id == chev.id


def test_encore_performance_guest_cast_can_copy_any_companion():
    st = furina_state()
    p = st.player
    hand_card(st, "chevreuse_interdiction_fire")
    hand_card(st, "lynette_box_trick")
    p.spotlight = C.SPOTLIGHT_GUEST_CAST
    effects.resolve_card(st, loader.get_card("encore_performance"))
    assert len(p.hand) == 3
    assert all(c.is_companion for c in p.hand)


def test_encore_performance_dead_without_designation_or_target():
    st = furina_state()
    hand_card(st, "chevreuse_interdiction_fire")
    effects.resolve_card(st, loader.get_card("encore_performance"))
    assert len(st.player.hand) == 1                 # no spotlight: no copy
    st.player.spotlight = "lynette"                 # spotlight, no target
    effects.resolve_card(st, loader.get_card("encore_performance"))
    assert len(st.player.hand) == 1


def test_encore_performance_is_free_and_refunds_nothing():
    """X3, closed by sitting 2026-08-06: "Remove the energy rider and make it
    free to play instead."

    The card was cost 1 with an {op: energy, amount: 1} refund. The refund was
    printed to make the copied Companion playable now, and a self-copy loop
    compounded it into an energy-POSITIVE engine. Cost 0 buys the same thing
    and cannot stack above zero. THIS PIN IS THE ONLY THING IN THE SUITE THAT
    READS THE NEW SHAPE -- the errata moved a rare's cost and nothing else
    went red.
    """
    card = loader.get_card("encore_performance")
    assert card.cost == 0
    assert not any(fx.get("op") == "energy" for fx in card.effects)
    assert [fx["op"] for fx in card.effects] == ["copy_spotlighted_in_hand"]


def test_spotlight_machinery_refunds_setup_energy():
    # encore_performance is in this list for the same OBSERVABLE (playing it
    # leaves energy where it was) but by a different mechanism since the X3
    # errata: it is free rather than refunded. See the pin above.
    for cid in ("limelight", "shared_billing", "guest_list",
                "encore_performance"):
        st = furina_state()
        p = st.player
        p.energy = 1
        p.encore = 1
        p.spotlight = C.SPOTLIGHT_GUEST_CAST
        hand_card(st, "chevreuse_interdiction_fire")
        card = hand_card(st, cid)
        combat.play_card(st, card)
        assert p.energy == 1, cid


def test_top_billing_no_longer_bricks_on_empty_encore():
    st = furina_state()
    p = st.player
    p.energy = 1
    card = hand_card(st, "top_billing")
    assert p.encore == 0 and card.encore_cost == 0
    assert combat.card_playable(st, card)
    assert loader.get_card("standing_ovation").cost == 1
    assert loader.get_card("standing_ovation+").cost == 0


# --- Spotlight texture powers (ratified design space, kickoff §3.2) ---

def test_leading_role_discounts_first_spotlighted_card_only():
    st = furina_state()
    p = st.player
    p.spotlight = "chevreuse"
    p.powers["spotlight_discount"] = 1
    card = loader.get_card("chevreuse_interdiction_fire")
    assert combat.card_cost(st, card) == 0          # first: 1 -> 0
    # B2 (2026-07-28): the window is spent by PAID Spotlighted plays, so this
    # case advances the paid counter. Advancing only the activity counter --
    # which is what this test used to do -- no longer closes the window, and
    # that is the whole fix: see
    # test_leading_role_is_not_consumed_by_a_free_spotlighted_play.
    st.spotlighted_cards_this_turn = 1
    st.spotlighted_paid_cards_this_turn = 1
    assert combat.card_cost(st, card) == 1          # later plays full price


def test_supporting_cast_draws_on_first_spotlighted_play_only():
    st = furina_state()
    p = st.player
    p.energy = 9
    p.spotlight = "chevreuse"
    p.powers["spotlight_draw"] = 1
    p.draw_pile = [loader.get_card("stage_presence") for _ in range(4)]
    for cid in ("chevreuse_interdiction_fire", "chevreuse_interdiction_fire"):
        combat.play_card(st, hand_card(st, cid))
    draws = [e for e in st.log if e["event"] == "extra_draw"]
    assert len(draws) == 1                          # first play only


def test_standing_ovation_pays_encore_per_spotlighted_play():
    # Archived pre-flip rate: the per-play power stays engine-supported.
    st = furina_state()
    p = st.player
    p.energy = 9
    p.spotlight = "chevreuse"
    p.powers["spotlight_encore"] = 2
    for _ in range(2):
        combat.play_card(st, hand_card(st, "chevreuse_interdiction_fire"))
    assert p.encore == 4                            # EVERY play, not first


def test_ovation_first_play_trickle_once_per_turn():
    # R32.1 iteration three: the flipped Ovation's income floor uses the
    # Supporting Cast first-play window — once per turn, never per play.
    st = furina_state()
    p = st.player
    p.energy = 9
    p.spotlight = "chevreuse"
    p.powers["spotlight_encore_first"] = 1
    for _ in range(2):
        combat.play_card(st, hand_card(st, "chevreuse_interdiction_fire"))
    assert p.encore == 1                            # first play only


def test_star_of_the_show_flat_rider_on_spotlighted_damage():
    st = furina_state()
    p = st.player
    p.spotlight = "chevreuse"
    p.powers["spotlight_flat_damage"] = 3
    hp0 = st.enemies[0].hp
    card = loader.get_card("chevreuse_interdiction_fire")
    printed = next(fx["amount"] for fx in card.effects
                   if fx.get("op") == "damage")
    effects.resolve_card(st, card)
    expect = int(printed * C.SPOTLIGHT_BASE_MULT) + 3
    assert st.enemies[0].hp == hp0 - expect


# --- R16 card-mediated boosting (pass 2) ---

def test_card_mediated_boosts_stack_through_the_pipe():
    """R16: her cards grant the multiplier. top_billing stacks per copy with
    no ceiling (cap dropped 2026-07-24, uncap-all); limelight's turn window
    still closes at end of turn."""
    from tier0.engine import powers
    st = furina_state()
    p = st.player
    p.spotlight = "chevreuse"
    for _ in range(3):                       # three copies -> +75%, no ceiling
        effects.resolve_card(st, loader.get_card("top_billing"))
    assert p.powers["spotlight_mult_bonus"] == 75
    card = loader.get_card("chevreuse_interdiction_fire")
    assert effects.spotlight_mult(st, card) == C.SPOTLIGHT_BASE_MULT + 0.75
    effects.resolve_card(st, loader.get_card("limelight"))
    assert effects.spotlight_mult(st, card) == C.SPOTLIGHT_BASE_MULT + 1.0
    powers.on_turn_end(st, p)                # the window closes
    assert effects.spotlight_mult(st, card) == C.SPOTLIGHT_BASE_MULT + 0.75
    assert "spotlight_mult_bonus_turn" not in p.powers


def test_delete_test_passes_by_construction():
    """R16.4: with no Furina boost cards played, a companion card sees
    only the residual base rate -- remove her cards and the empowerment
    leaves with them."""
    st = furina_state()
    st.player.spotlight = "chevreuse"
    card = loader.get_card("chevreuse_interdiction_fire")
    assert effects.spotlight_mult(st, card) == C.SPOTLIGHT_BASE_MULT


def test_star_of_the_show_grants_its_printed_amount_per_copy():
    """Printed amount per copy, and copies STACK (cap dropped, user
    ruling 2026-07-24).

    G-D2 note: the printed amount moved 3 -> 5 (PROPOSED, 2026-07-25),
    so this reads it off the SHEET rather than restating it. The test was
    named for the number and asserted it twice; that made a ratified
    reprice look like a regression. What it is actually here to protect is
    the pass-2 errata (max_stacks is in POWER UNITS) and the linearity of
    a second copy -- neither of which is a claim about the value 3.

    The pass-2 errata this test was written for still holds and is still
    checked by the first assertion: max_stacks was in POWER UNITS, so the
    pass-1 row's `max_stacks: 1` silently shipped the card at +1 instead of
    its printed +3. What changed is the second assertion. The cap was 3 --
    exactly one application -- which made a second copy do nothing at all:
    a dead card of the shape lint_strict_domination exists to catch. The
    cap rationale (pass1-rulings-round2) is about PER-TURN COMPOUNDING
    powers; a flat additive read once per Spotlighted card is linear in
    copies, so it now behaves like an ordinary StS Power dupe."""
    printed = loader.get_card("star_of_the_show").effects[0]["amount"]
    st = furina_state()
    effects.resolve_card(st, loader.get_card("star_of_the_show"))
    assert st.player.powers["spotlight_flat_damage"] == printed
    effects.resolve_card(st, loader.get_card("star_of_the_show"))
    assert st.player.powers["spotlight_flat_damage"] == printed * 2


def test_uncapped_spotlight_riders_stack():
    """The other three cap drops (user ruling 2026-07-24).

    Each is gated to ONE proc per turn by its own "first Spotlighted card
    each turn" clause, so a second copy buys a bigger single proc, never a
    second one -- linear, not exponential, and outside the cap rationale."""
    for card_id, power in (("leading_role", "spotlight_discount"),
                           ("supporting_cast", "spotlight_draw"),
                           ("standing_ovation", "spotlight_encore_first")):
        st = furina_state()
        effects.resolve_card(st, loader.get_card(card_id))
        effects.resolve_card(st, loader.get_card(card_id))
        assert st.player.powers[power] == 2, (
            f"{card_id}: {power} should stack to 2, got "
            f"{st.player.powers[power]}")


def test_compounding_spotlight_powers_now_uncap():
    """Round two of the cap ruling (user, 2026-07-24, uncap-all).

    Round one split these two percentage multipliers out and KEPT their
    ceilings; round two dropped them too, after a 2000-run x 2-seed A/B put
    the whole cap set at <=+0.5pp on run success (favorable, non-binding at
    present difficulty). These are the genuinely compounding powers, so this
    test doubles as the record that the drop was deliberate and measured --
    and that the two multipliers now stack per copy like base-StS Power dupes.
    They were FLAGGED for a ceiling re-check at difficulty calibration; if a
    future ceiling is reintroduced, this test is where it gets re-asserted."""
    for card_id, power, per_copy in (
            ("top_billing", "spotlight_mult_bonus", 25),
            ("standing_ovation", "ovation_spend_boost", 10)):
        st = furina_state()
        for _ in range(4):
            effects.resolve_card(st, loader.get_card(card_id))
        assert st.player.powers[power] == 4 * per_copy, (
            f"{card_id}: {power} should stack uncapped to {4 * per_copy}, got "
            f"{st.player.powers[power]}")


def test_upgraded_power_amount_lifts_its_own_stack_cap():
    """An upgraded Star of the Show grants its printed amount + 1.

    HISTORY, because the name no longer describes the mechanism. This test
    was written for the applier's single-application rule -- when a row
    encodes max_stacks == amount, the upgrade bumps BOTH, or the upgraded
    card silently caps at the old value. Star of the Show was the only such
    row, and the 2026-07-24 cap ruling removed its cap entirely, so the +4
    now arrives with no ceiling to lift.

    The assertion is kept as-is: it still guards the upgrade delta landing.
    The applier's max_stacks branch (content/upgrades.py) is now unexercised
    by live content -- no shipped row has max_stacks == amount -- but it is
    deliberately retained as the correctness rule for any future
    single-application capped power."""
    from tier0.content import upgrades
    printed = loader.get_card("star_of_the_show").effects[0]["amount"]
    st = furina_state()
    effects.resolve_card(st, upgrades.apply_upgrade(
        loader.get_card("star_of_the_show")))
    assert st.player.powers["spotlight_flat_damage"] == printed + 1


# --- selector aiming v5 (explicit two-mode choice) ---

def test_selector_guest_cast_does_not_require_character_depth():
    st = furina_state()                       # real starter: 10 Furina cards
    hand_card(st, "lynette_box_trick")        # one ready Companion suffices
    effects.resolve_card(st, loader.get_card("ethereal_spotlight"))
    assert st.player.spotlight == C.SPOTLIGHT_GUEST_CAST
    st.player.hand.clear()
    effects.resolve_card(st, loader.get_card("ethereal_spotlight"))
    assert st.player.spotlight == "furina"


# --- selector-payoff predicates ---

def test_spotlight_moved_predicates():
    st = furina_state()
    p = st.player
    p.draw_pile.clear()              # isolate from the starter's self-depth
    hand_card(st, "chevreuse_interdiction_fire")
    assert not effects._predicate(st, "spotlight_moved_this_turn")
    assert not effects._predicate(st, "spotlight_unmoved_this_combat")
    effects.resolve_card(st, loader.get_card("ethereal_spotlight"))
    assert p.spotlight == C.SPOTLIGHT_GUEST_CAST
    assert effects._predicate(st, "spotlight_moved_this_turn")
    assert effects._predicate(st, "spotlight_unmoved_this_combat")
    st.spotlight_moved_this_turn = False            # next turn's reset
    p.spotlight = "furina"                          # a second, different aim
    st.spotlight_moves_this_combat += 1
    assert not effects._predicate(st, "spotlight_unmoved_this_combat")


# --- Burst wiring (v1.9 kit; meter declared 70 this pass) ---

def test_burst_charges_grants_empties_and_regrants():
    st = furina_state()
    p = st.player
    p.energy = 99
    p.burst_energy = p.burst_max - 1
    # A skill_tag card is what feeds burst particles; usher_the_waves lost its
    # tag at Curtain Call B (skill->attack retype, and plain attacks feed no
    # particles), and rising_tide -- this case's card until then -- was CUT by
    # A4 (2026-07-28 red-pen). overflowing_hospitality carries the same tag.
    combat.play_card(st, hand_card(st, "overflowing_hospitality"))   # skill_tag: +5
    assert any(c.id == "let_the_people_rejoice" for c in p.hand)
    burst = next(c for c in p.hand if c.kit_card)
    assert combat.card_playable(st, burst)
    combat.play_card(st, burst)
    assert p.burst_energy == 0
    assert burst not in p.discard_pile and burst not in p.exhaust_pile


def test_burst_applies_hydro_and_scales_with_fanfare():
    st = furina_state()
    p = st.player
    p.fanfare = 12
    p.burst_energy = p.burst_max
    hp0 = st.enemies[0].hp
    effects.resolve_card(st, loader.get_card("let_the_people_rejoice"))
    assert st.enemies[0].hp == hp0 - (8 + 3)        # +1 per 4 fanfare at 12
    assert st.enemies[0].aura == "hydro"            # burst-tag cadence
    assert p.encore == 6


# --- B2: Leading Role's window is spent by PAID Spotlighted plays only ---

def test_leading_role_is_not_consumed_by_a_free_spotlighted_play():
    """B2 (playtest-2, 2026-07-28): "Leading Role never discounts".

    Both reported causes were real. The discount skips cards printed at 0
    (nothing to reduce), but the shared Spotlight play counter ticked for
    every Spotlighted play including those -- so a free one spent a window
    it could not use. Under Center Stage the relic's free token is itself a
    Spotlighted Furina card arriving every turn, which is why the power read
    as completely dead rather than merely unreliable.
    """
    st = furina_state()
    p = st.player
    p.spotlight = p.character_id            # Center Stage: her cards are lit
    p.powers["spotlight_discount"] = 1
    p.energy = 99

    free = loader.get_card("curtain_cue")   # printed cost 0
    assert free.cost == 0
    combat.play_card(st, hand_card(st, "curtain_cue"))
    assert st.spotlighted_cards_this_turn == 1     # activity still counted
    assert st.spotlighted_paid_cards_this_turn == 0, (
        "a free Spotlighted play spent Leading Role's window -- the B2 defect")

    paid = loader.get_card("stage_presence")       # printed cost 1
    assert combat.card_cost(st, paid) == 0, (
        "Leading Role did not discount the first PAID Spotlighted card")

    # ...and it is spent once a paid card actually goes.
    combat.play_card(st, hand_card(st, "stage_presence"))
    assert st.spotlighted_paid_cards_this_turn == 1
    assert combat.card_cost(st, loader.get_card("stage_presence")) == 1


# --- B4: Grand Salon scopes to every member NUMBER, not just damage ---

def test_grand_salon_scales_ushers_block_not_only_damage():
    """B4 (playtest-2, 2026-07-28) reported "only member damage scaled".

    VERIFIED CLEAN in both engines, and pinned here so it stays that way.
    The salon-rework plan ruled `salon_damage_up` a "+N to member NUMERIC
    effects" term, and both engines honour it: tier0 routes every member
    number through `_salon_amount`, and the C# routes them through
    `SalonPowers.Scaled` (tick via `Num`, bow directly). The power's own name
    is the only thing that still says "damage" -- its printed text already
    reads "Salon Member numbers are N higher", which is what it does.

    Usher is the discriminator: it is the one member whose tick is BLOCK, so
    a damage-only implementation passes every other member's assertions and
    fails only this one.
    """
    st = furina_state()
    p = st.player
    p.salon = ["usher"]
    p.fanfare = 0                     # isolate the Grand Salon term
    p.encore = 99                     # pay upkeep: no dry-multiplier haircut
    p.block = 0
    effects.salon_tick(st)
    baseline = p.block
    assert baseline == C.SALON_MEMBERS["usher"]["tick"]["block"]

    st2 = furina_state()
    p2 = st2.player
    p2.salon = ["usher"]
    p2.fanfare = 0
    p2.encore = 99
    p2.block = 0
    p2.powers["salon_damage_up"] = 2
    effects.salon_tick(st2)
    assert p2.block == baseline + 2, (
        "salon_damage_up did not reach Usher's BLOCK tick -- Grand Salon has "
        "regressed to damage-only, the B4 defect")


def test_casting_call_makes_the_stage_bigger_and_delays_the_bow():
    """A12 (RULED 2026-07-28): the Salon's size stops being a constant.

    Both halves are asserted because they are the same ruling seen from two
    sides, and a cap that grew without delaying the bow would be the worse
    bug -- the player would hold four members AND still be losing one per
    deploy, which reads as the card doing nothing.
    """
    st = furina_state()
    p = st.player
    effects.resolve_card(st, loader.get_card("casting_call"))
    assert p.powers["salon_cap_up"] == 1
    assert effects.salon_slots(p) == C.SALON_MEMBER_SLOTS + 1

    _company(p, "usher", "usher", "usher")
    hp0 = st.enemies[0].hp
    p.block = 0
    effects._deploy_salon_members(st, 1, "crabaletta")
    assert len(p.salon) == 4, "the 4th member did not fit the enlarged stage"
    assert st.salon_replacements_this_card == 0, (
        "someone bowed out of a stage that had room -- the cap grew but the "
        "replacement rule did not follow it")

    # And the 5th still displaces, so the cap is raised, not removed.
    effects._deploy_salon_members(st, 1, "crabaletta")
    assert len(p.salon) == 4
    assert st.salon_replacements_this_card == 1


def test_the_enlarged_stage_pays_every_per_member_reader():
    """The cap is a stat, so a 4th member must count everywhere a member
    counts -- not just in the queue. A13's slope is the discriminator: it is
    the newest per-member reader and the one most likely to have been written
    against a hard 3."""
    st = furina_state()
    p = st.player
    p.powers["salon_cap_up"] = 1
    _company(p, "usher", "usher", "usher", "crabaletta")
    p.block = 0
    effects.resolve_card(st, loader.get_card("dinner_service"))
    assert p.block == 2 + 2 * 4


def test_the_base_cap_constant_is_still_three():
    """The constant-parity gate compares C.SALON_MEMBER_SLOTS by VALUE against
    SalonConstants.MemberSlots. A12 makes the cap a stat on top of that base;
    if the base itself ever moves, the two engines must move together, so the
    pin stays on the constant rather than on the computed slot count."""
    assert C.SALON_MEMBER_SLOTS == 3
    st = furina_state()
    assert effects.salon_slots(st.player) == 3


def test_salon_debut_fields_a_random_member_not_always_chevalmarin():
    """A11 (RULED 2026-07-28): the starter and the Chevalmarin Common were
    the same card at two rarities -- same cost, same member.

    The discriminator is that all three members must be reachable. A roll
    that always returned one member would satisfy "it deploys somebody" and
    leave the duplication exactly where it was.
    """
    landed = set()
    for seed in range(40):
        st = furina_state(seed=seed)
        effects.resolve_card(st, loader.get_card("salon_debut"))
        assert len(st.player.salon) == 1
        landed.add(st.player.salon[0])
    assert landed == set(C.SALON_MEMBERS), landed


def test_the_random_deploy_is_seeded_not_ambient():
    """Same seed, same member -- twice over.

    tier 0.5 replays runs off a seed, and a co-op run is lockstep: a draw
    that is not reproducible from the seed is the shape of defect that
    desynced Vigil of the Deep. This is the sim's half of that guarantee;
    the C# half draws from RunState.Rng.CombatTargets, the shared stream.
    """
    for seed in (0, 7, 99):
        picks = []
        for _ in range(2):
            st = furina_state(seed=seed)
            effects.resolve_card(st, loader.get_card("salon_debut"))
            picks.append(st.player.salon[0])
        assert picks[0] == picks[1], (seed, picks)


def test_a_random_deploy_rolls_per_member_not_once_per_card():
    """Both engines roll INSIDE the deploy loop, so a multi-deploy card can
    field a mixed stage. Pinned because rolling once and reusing it is the
    cheaper implementation and reads identically on a 1-deploy card -- which
    is every card that currently uses the grammar."""
    mixed = False
    for seed in range(40):
        st = furina_state(seed=seed)
        effects._deploy_salon_members(st, 3, "random")
        if len(set(st.player.salon)) > 1:
            mixed = True
            break
    assert mixed, "3 random deploys never produced a mixed stage in 40 seeds"


def test_dinner_service_pays_a_slope_not_a_threshold():
    """A13 (RULED 2026-07-28): "Gain 2 Block, plus 2 per Salon member".

    The threshold it replaces paid the SAME bonus for a stage of one and a
    stage of three, which is what made the second and third deploy feel like
    they bought nothing. So the discriminator is not "does an empty stage pay
    less" -- the old shape passed that too -- it is that every step differs.
    """
    seen = []
    for company in ([], ["usher"], ["usher", "chevalmarin"],
                    ["usher", "chevalmarin", "crabaletta"]):
        st = furina_state()
        p = st.player
        _company(p, *company)
        p.block = 0
        effects.resolve_card(st, loader.get_card("dinner_service"))
        seen.append(p.block)
    assert seen == [2, 4, 6, 8], seen


def test_house_call_pays_a_slope_not_a_threshold():
    """A14 (RULED 2026-07-28): "Deal 6 damage, plus 2 per Salon member".

    Same shape as A13 on the damage half, and pinned separately because the
    two ride different halves of the generator -- A13's rider lands on a block
    op, which had no rider rail at all until B1 built one.
    """
    seen = []
    for company in ([], ["usher"], ["usher", "chevalmarin"],
                    ["usher", "chevalmarin", "crabaletta"]):
        st = furina_state()
        p = st.player
        _company(p, *company)
        hp0 = st.enemies[0].hp
        effects.resolve_card(st, loader.get_card("house_call"))
        seen.append(hp0 - st.enemies[0].hp)
    assert seen == [6, 8, 10, 12], seen


def test_the_per_member_slope_bumps_its_base_on_upgrade_not_its_rate():
    """Both A13/A14 deltas move the BASE; the slope is deliberately untouched.

    Pinned because the upgrade applier is one of the four hand-maintained
    projections a sheet ruling does NOT update for you, and a delta that
    silently bound to the wrong term would still produce a bigger number --
    just the wrong bigger number, and only at full stage.
    """
    st = furina_state()
    p = st.player
    _company(p, "usher", "chevalmarin", "crabaletta")
    p.block = 0
    effects.resolve_card(st, loader.get_card("dinner_service+"))
    assert p.block == 4 + 2 * 3          # base 2->4, slope still 2

    st2 = furina_state()
    _company(st2.player, "usher", "chevalmarin", "crabaletta")
    hp0 = st2.enemies[0].hp
    effects.resolve_card(st2, loader.get_card("house_call+"))
    assert hp0 - st2.enemies[0].hp == 8 + 2 * 3   # base 6->8, slope still 2


# --- reward-pool separation (the cross-character card-reward guard) ---

def test_personal_card_pools_do_not_cross_characters():
    from tier05 import rewards
    klee_pool = rewards.character_pool("klee")
    furina_pool = rewards.character_pool("furina")
    for pool, own in ((klee_pool, "klee"), (furina_pool, "furina")):
        for cards in pool.values():
            assert all(c.character in (None, own) for c in cards), (
                f"{own}'s card rewards leak another character's cards")
    # and both pools actually have all three reward rarities
    for pool in (klee_pool, furina_pool):
        assert set(pool) >= {"common", "uncommon", "rare"}
