"""Furina sheet pass 1: the card pool, Salon Members, Fanfare payoffs,
Guest Star generation, Encore Performance, Spotlight texture powers and
the Burst meter (docs/furina-cards.yaml; furina-sheet-pass-1-plan.md).
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects
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
    assert len(by_rarity["common"]) == 31
    assert len(by_rarity["uncommon"]) == 25
    assert len(by_rarity["rare"]) == 15
    kit = [c for c in by_rarity["rare"] if c.kit_card]
    assert [c.id for c in kit] == ["let_the_people_rejoice"]   # 14 draftable


def test_starter_invitation_and_aria_curve():
    starter = loader.starting_deck("furina")
    assert len(starter) == 10
    assert starter.count("aria_of_recompense") == 1
    assert starter.count("an_invitation") == 1

    aria = loader.get_card("aria_of_recompense")
    aria_plus = loader.get_card("aria_of_recompense+")
    assert aria.effects == [{"op": "gain_encore", "amount": 5}]
    assert aria_plus.effects == [{"op": "gain_encore", "amount": 8}]

    stage = loader.get_card("stage_presence")
    stage_plus = loader.get_card("stage_presence+")
    assert stage.effects == [{"op": "block", "amount": 5}]
    assert stage_plus.effects == [{"op": "block", "amount": 8}]


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


# --- Salon Members (kickoff §5, on the oz_summon rails) ---

def test_salon_tick_damages_applies_hydro_and_drains_encore():
    st = furina_state()
    p = st.player
    p.powers["salon_member"] = 2
    p.encore = 5
    hp0 = st.enemies[0].hp
    effects.salon_tick(st)
    assert st.enemies[0].hp == hp0 - 2 * C.SALON_MEMBER_DMG
    assert st.enemies[0].aura == "hydro"            # the application engine
    assert p.encore == 5 - 2 * C.SALON_TICK_ENCORE_COST


def test_dry_salon_ticks_deal_half_damage_without_overdraw():
    st = furina_state()
    p = st.player
    p.powers["salon_member"] = 2
    p.encore = 0
    hp0 = p.hp
    enemy_hp0 = st.enemies[0].hp
    effects.salon_tick(st)
    assert p.hp == hp0
    assert st.enemies[0].hp == (
        enemy_hp0 - 2 * int(C.SALON_MEMBER_DMG * C.SALON_DRY_DAMAGE_MULT))
    assert not any(e["event"] == "encore_overdraw" for e in st.log)
    assert p.fanfare == 0


def test_salon_ticks_only_throttle_after_encore_runs_out():
    st = furina_state()
    p = st.player
    p.powers["salon_member"] = 2
    p.encore = 1
    enemy_hp0 = st.enemies[0].hp
    effects.salon_tick(st)
    assert p.encore == 0
    assert p.hp == p.max_hp
    assert st.enemies[0].hp == (
        enemy_hp0 - C.SALON_MEMBER_DMG
        - int(C.SALON_MEMBER_DMG * C.SALON_DRY_DAMAGE_MULT))


def test_salon_slots_cap_at_three_and_overflow_takes_a_final_bow():
    st = furina_state()
    p = st.player
    p.powers["salon_member"] = 2
    enemy_hp0 = st.enemies[0].hp
    effects.resolve_card(st, loader.get_card("mademoiselle_crabaletta"))
    assert p.powers["salon_member"] == C.SALON_MEMBER_SLOTS == 3
    bow = C.SALON_REPLACE_DAMAGE_MULT * C.SALON_MEMBER_DMG
    assert st.enemies[0].hp == enemy_hp0 - bow
    assert st.enemies[0].aura == "hydro"
    assert p.encore == 0                          # final bows have no upkeep
    assert p.burst_energy == C.SALON_TICK_BURST


def test_each_overflowed_member_takes_a_final_bow():
    st = furina_state()
    p = st.player
    p.powers["salon_member"] = C.SALON_MEMBER_SLOTS
    enemy_hp0 = st.enemies[0].hp
    effects.resolve_card(st, loader.get_card("full_ensemble"))
    assert p.powers["salon_member"] == C.SALON_MEMBER_SLOTS
    bow = C.SALON_REPLACE_DAMAGE_MULT * C.SALON_MEMBER_DMG
    assert st.enemies[0].hp == enemy_hp0 - 3 * bow


def test_replacing_member_triples_block_rider_once():
    st = furina_state()
    p = st.player
    p.powers["salon_member"] = C.SALON_MEMBER_SLOTS
    effects.resolve_card(st, loader.get_card("gentilhomme_usher"))
    assert p.powers["salon_member"] == C.SALON_MEMBER_SLOTS
    assert p.block == 4 * C.SALON_REPLACE_DAMAGE_MULT


def test_replacing_member_doubles_encore_rider_once():
    st = furina_state()
    p = st.player
    p.powers["salon_member"] = C.SALON_MEMBER_SLOTS
    effects.resolve_card(st, loader.get_card("surintendante_chevalmarin"))
    assert p.encore == 3 * C.SALON_REPLACE_NUMERIC_MULT


def test_replacement_multiplier_ends_with_the_deploying_card():
    st = furina_state()
    p = st.player
    p.powers["salon_member"] = C.SALON_MEMBER_SLOTS
    effects.resolve_card(st, loader.get_card("surintendante_chevalmarin"))
    after_replacement = p.encore
    effects.resolve_card(st, loader.get_card("curtain_up"))
    assert p.encore == after_replacement + 2


def test_multiple_replacements_do_not_multiply_rider_more_than_once():
    st = furina_state()
    p = st.player
    p.powers["salon_member"] = C.SALON_MEMBER_SLOTS
    effects.resolve_card(st, loader.get_card("grand_gala"))
    assert p.powers["salon_member"] == C.SALON_MEMBER_SLOTS
    assert p.encore == 4 * C.SALON_REPLACE_NUMERIC_MULT


def test_replacing_member_doubles_salon_power_without_clipping():
    st = furina_state()
    p = st.player
    p.powers["salon_member"] = C.SALON_MEMBER_SLOTS
    effects.resolve_card(st, loader.get_card("endless_waltz"))
    assert p.powers["salon_damage_up"] == 3 * C.SALON_REPLACE_NUMERIC_MULT


def test_replacing_member_doubles_draw_rider():
    st = furina_state()
    p = st.player
    p.powers["salon_member"] = C.SALON_MEMBER_SLOTS
    p.encore = 2
    p.draw_pile = [loader.get_card("stage_presence") for _ in range(2)]
    effects.resolve_card(st, loader.get_card("dress_rehearsal"))
    assert len(p.hand) == 2


def test_salon_damage_up_scales_ticks():
    st = furina_state()
    p = st.player
    p.powers["salon_member"] = 1
    p.powers["salon_damage_up"] = 2
    p.encore = 3
    hp0 = st.enemies[0].hp
    effects.salon_tick(st)
    assert st.enemies[0].hp == hp0 - (C.SALON_MEMBER_DMG + 2)


def test_salon_ticks_and_encore_spend_feed_the_burst_meter():
    st = furina_state()
    p = st.player
    p.powers["salon_member"] = 1
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
    assert made.generated_by_guest_star              # selector-v4 provenance


def test_upgraded_generator_discounts_the_guest():
    st = furina_state()
    effects.resolve_card(st, loader.get_card("an_invitation+"))
    assert st.player.hand[0].cost == 0              # Discovery parity


# --- Encore Performance (the duplication rare; DECISIONS 64) ---

def test_encore_performance_copies_only_the_spotlighted_character():
    st = furina_state()
    p = st.player
    chev = hand_card(st, "chevreuse_interdiction_fire")
    hand_card(st, "lynette_box_trick")
    p.spotlight = "chevreuse"
    effects.resolve_card(st, loader.get_card("encore_performance"))
    copies = [c for c in p.hand if c.character == "chevreuse"]
    assert len(copies) == 2 and copies[1].id == chev.id


def test_encore_performance_dead_without_designation_or_target():
    st = furina_state()
    hand_card(st, "chevreuse_interdiction_fire")
    effects.resolve_card(st, loader.get_card("encore_performance"))
    assert len(st.player.hand) == 1                 # no spotlight: no copy
    st.player.spotlight = "lynette"                 # spotlight, no target
    effects.resolve_card(st, loader.get_card("encore_performance"))
    assert len(st.player.hand) == 1


# --- Spotlight texture powers (ratified design space, kickoff §3.2) ---

def test_leading_role_discounts_first_spotlighted_card_only():
    st = furina_state()
    p = st.player
    p.spotlight = "chevreuse"
    p.powers["spotlight_discount"] = 1
    card = loader.get_card("chevreuse_interdiction_fire")
    assert combat.card_cost(st, card) == 0          # first: 1 -> 0
    st.spotlighted_cards_this_turn = 1
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
    effects.resolve_card(st, loader.get_card("chevreuse_interdiction_fire"))
    # R16 world: 5 printed -> x BASE_MULT -> +3 flat.
    expect = int(5 * C.SPOTLIGHT_BASE_MULT) + 3
    assert st.enemies[0].hp == hp0 - expect


# --- R16 card-mediated boosting (pass 2) ---

def test_card_mediated_boosts_stack_through_the_pipe():
    """R16: her cards grant the multiplier. top_billing stacks to +50%
    and no further; limelight's turn window closes at end of turn."""
    from tier0.engine import powers
    st = furina_state()
    p = st.player
    p.spotlight = "chevreuse"
    for _ in range(3):                       # third copy hits the ceiling
        effects.resolve_card(st, loader.get_card("top_billing"))
    assert p.powers["spotlight_mult_bonus"] == 50
    card = loader.get_card("chevreuse_interdiction_fire")
    assert effects.spotlight_mult(st, card) == C.SPOTLIGHT_BASE_MULT + 0.5
    effects.resolve_card(st, loader.get_card("limelight"))
    assert effects.spotlight_mult(st, card) == C.SPOTLIGHT_BASE_MULT + 0.75
    powers.on_turn_end(st, p)                # the window closes
    assert effects.spotlight_mult(st, card) == C.SPOTLIGHT_BASE_MULT + 0.5
    assert "spotlight_mult_bonus_turn" not in p.powers


def test_delete_test_passes_by_construction():
    """R16.4: with no Furina boost cards played, a companion card sees
    only the residual base rate -- remove her cards and the empowerment
    leaves with them."""
    st = furina_state()
    st.player.spotlight = "chevreuse"
    card = loader.get_card("chevreuse_interdiction_fire")
    assert effects.spotlight_mult(st, card) == C.SPOTLIGHT_BASE_MULT


def test_star_of_the_show_errata_grants_printed_three():
    """Pass-2 errata: max_stacks is in POWER UNITS -- the pass-1 row
    (max_stacks 1) silently shipped +1. Printed +3 applies once and
    never re-stacks."""
    st = furina_state()
    effects.resolve_card(st, loader.get_card("star_of_the_show"))
    assert st.player.powers["spotlight_flat_damage"] == 3
    effects.resolve_card(st, loader.get_card("star_of_the_show"))
    assert st.player.powers["spotlight_flat_damage"] == 3


def test_upgraded_power_amount_lifts_its_own_stack_cap():
    """The applier bumps max_stacks alongside amount when they are equal
    (single-application encoding) -- an upgraded Star of the Show must
    actually grant +4, not silently cap at the old 3."""
    from tier0.content import upgrades
    st = furina_state()
    effects.resolve_card(st, upgrades.apply_upgrade(
        loader.get_card("star_of_the_show")))
    assert st.player.powers["spotlight_flat_damage"] == 4


# --- selector aiming v2 (the depth contest; DECISIONS-bound in report) ---

def test_selector_depth_contest_self_beats_shallow_companion():
    """v3 keeps v1's lesson: a shallow guest must NOT hijack the
    Spotlight from a deep self-kit (sub-threshold depth -> self
    fallback). With NO self cards at all, any stage beats none -- the
    guest gets the beam as the last resort (v2's tie rule, archived,
    happened to agree here)."""
    st = furina_state()                       # real starter: 10 furina cards
    hand_card(st, "lynette_box_trick")        # one shallow companion
    effects.resolve_card(st, loader.get_card("ethereal_spotlight"))
    assert st.player.spotlight == "furina"    # self depth 10 wins
    st2 = furina_state()
    st2.player.draw_pile.clear()
    hand_card(st2, "lynette_box_trick")       # tie: 1 companion vs 0 self
    effects.resolve_card(st2, loader.get_card("ethereal_spotlight"))
    assert st2.player.spotlight == "lynette"  # companion wins the tie


# --- selector-payoff predicates ---

def test_spotlight_moved_predicates():
    st = furina_state()
    p = st.player
    p.draw_pile.clear()              # isolate from the starter's self-depth
    hand_card(st, "chevreuse_interdiction_fire")
    assert not effects._predicate(st, "spotlight_moved_this_turn")
    assert not effects._predicate(st, "spotlight_unmoved_this_combat")
    effects.resolve_card(st, loader.get_card("ethereal_spotlight"))
    assert p.spotlight == "chevreuse"
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
    combat.play_card(st, hand_card(st, "usher_the_waves"))   # skill_tag: +5
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
