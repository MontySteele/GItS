"""The Kokomi round 3 A-list (2026-10-13; review
`review/active/kokomi-review-r3-2026-10-13.md` sections 4 and 5A).

Second Wave's window, Bubble Ward 6 [9], Kurage Canopy's Wards, Albedo's
target, and the page receipts: a generated card a full hand sent to the
discard pile, the turn's-end Ethereal Exhaust, Change of Plans with four
Plans waiting at 0 Energy, and when a Plan reads Strength. The C# twin is
`klee-mod/KleeTests/Prototype/KokomiRound3AListTests.cs`.
"""
from __future__ import annotations

import copy

from tier0.content import loader, upgrades
from tier0.engine import combat, kokomi_plan
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy
from tier0.tests.test_arm_keyword_tips import proto
from tier0.tests.test_blindplay_seat_page_3 import ev, queen, row, since
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, carry_out, kokomi_state)
from understudy import blindplay_board, blindplay_render

QUIET = [{"kind": "block", "amount": 5}]


def _face(card_id: str) -> str:
    return {r["id"]: r for r in proto._rows()}[card_id]["description"]


def _card(cid: str) -> Card:
    return copy.deepcopy(loader.get_card(cid))


def _up(cid: str) -> Card:
    return upgrades.apply_upgrade(loader.get_card(cid))


def _probe_plan(i: int = 0) -> Card:
    return Card(id=f"proto_kk_probe{i}", name="probe", cost=1, type="skill",
                effects=[], plan=[{"op": "energy", "amount": 1}])


# --- the cards ------------------------------------------------------------------

def test_second_wave_names_the_plan_written_after_it_this_turn():
    assert _face("proto_kk_second_wave") == (
        "Deal 7 [gold]Hydro[/gold] damage. [gold]Plan[/gold]: The "
        "[gold]Plan[/gold] written after it this turn is carried out twice.")
    assert _card("proto_kk_second_wave").effects[0]["amount"] == 7
    assert _up("proto_kk_second_wave").effects[0]["amount"] == 9


def test_bubble_ward_is_7_and_10():
    # The pool sweep (2026-10-18): 6 [9] -> 7 [10].
    assert _face("proto_kk_bubble_ward") == (
        "Gain 7 [gold]Block[/gold]. Add a [gold]Ward[/gold] to your "
        "[gold]Hand[/gold].")
    assert _card("proto_kk_bubble_ward").effects[0]["amount"] == 7
    assert _up("proto_kk_bubble_ward").effects[0]["amount"] == 10


def test_albedo_deals_geo_to_all_per_attack():
    # 2026-10-13: "a Rare should be more dramatic and the Mondstadt pool
    # already has powers for free block".
    assert _face("proto_mc_albedo_solar_isotoma") == (
        "At the end of your turn, deal 2 [gold]Geo[/gold] damage to ALL "
        "enemies for each Attack you played this turn.")


def test_jean_swirls_an_enemy_with_an_aura():
    # An enemy holds at most one aura, so "the most auras" named nothing.
    assert _face("proto_mc_jean_dandelion_breeze") == (
        "At the end of your turn, [gold]Swirl[/gold] an enemy with an aura "
        "and gain 6 [gold]Block[/gold].")


def test_kurage_canopy_face():
    assert _face("proto_kk_kurage_canopy") == (
        "Whenever the [gold]Bake-Kurage[/gold] carries out a "
        "[gold]Plan[/gold] that is not a [gold]Sting[/gold] or "
        "[gold]Ward[/gold], add {IfUpgraded:show:an upgraded|a} "
        "[gold]Ward[/gold] to your [gold]Hand[/gold].")


def test_kurage_canopy_stops_at_a_full_hand_in_the_sim(caches):
    """The sim's `_add_token` rule stops a token at a full hand; the game
    sends it to the discard pile (`KokomiCards.AddJellyfish`)."""
    from tier0 import constants as C
    st = kokomi_state()
    st.player.powers[kokomi_plan.KURAGE_CANOPY] = 1
    st.player.hand = [_card("proto_kk_sting")
                      for _ in range(C.MAX_HAND_SIZE)]
    kokomi_plan.schedule(st, _probe_plan())
    carry_out(st)
    assert len(st.player.hand) == C.MAX_HAND_SIZE
    assert not any(c.id == kokomi_plan.WARD_ID for c in st.player.hand)


# --- Change of Plans: four Plans waiting, no Energy ---------------------------

def test_change_of_plans_plays_at_0_energy_with_four_plans_waiting(caches):
    """Lane 4 F6 read "unplayable: no Energy" with four Plans waiting. Not
    reproduced: the card costs 0 and its one gate is a waiting Plan."""
    st = kokomi_state()
    for i in range(4):
        kokomi_plan.schedule(st, _probe_plan(i))
    assert len(st.kk_plan_queue) == 4
    st.player.energy = 0
    card = _card("proto_kk_change_of_plans")
    assert card.cost == 0 and _up("proto_kk_change_of_plans").cost == 0
    assert combat.card_playable(st, card) is True
    st.player.hand.append(card)
    combat.play_card(st, card)
    assert len(st.kk_plan_queue) == 3


# --- when a Plan reads Strength -----------------------------------------------

def test_a_plans_strength_is_read_when_it_is_written(caches):
    """Lane 4 F8 ("Strength is read when written") against lane 2 F16
    (Masterstroke 40 not 42 under Tender's this-turn loss): both are the one
    rule. Her Strength is folded into the number when the Plan is WRITTEN
    (`kokomi_plan.hers`, C# `KokomiPlan.Hers`); Strength gained or lost
    after that does not move the carry-out."""
    enemy = make_enemy(hp=300, intents=QUIET)
    st = kokomi_state()
    st.enemies = [enemy]
    st.player.powers["strength"] = 2
    plan = Card(id="proto_kk_probe_hit", name="hit", cost=1, type="skill",
                effects=[], plan=[{"op": "damage", "amount": 10,
                                   "target": "front_enemy"}])
    kokomi_plan.schedule(st, plan)
    assert st.kk_plan_queue[0].clauses[0]["amount"] == 12
    st.player.powers["strength"] = 7
    carry_out(st)
    assert enemy.hp == 300 - 12


# --- the page receipts ----------------------------------------------------------

def test_the_two_new_kinds_reach_the_page():
    assert "discarded" in blindplay_board.PAGE_EVENT_KINDS
    assert "ethereal" in blindplay_board.PAGE_EVENT_KINDS


def test_a_full_hand_prints_the_discard_receipt():
    state = queen(round_=2)
    state["player"]["resolutions"] = [
        row("Kurage's Wake", [ev("discarded", 1, card="Sting",
                                 on_player=True)])]
    assert since(state) == [
        "- Since last page: 1 Sting to the discard pile (hand full)."]


def test_two_to_the_discard_count_as_one_phrase():
    state = queen(round_=2)
    state["player"]["resolutions"] = [
        row("Kurage's Wake", [ev("discarded", 1, card="Sting",
                                 on_player=True),
                              ev("discarded", 2, card="Sting",
                                 on_player=True)])]
    assert since(state) == [
        "- Since last page: 2 Stings to the discard pile (hand full)."]


def test_the_turns_end_ethereal_exhaust_prints():
    state = queen(round_=2)
    state["player"]["resolutions"] = [
        row("", [ev("ethereal", 1, card="Sting", on_player=True),
                 ev("ethereal", 2, card="Sting", on_player=True),
                 ev("ethereal", 3, card="Ward", on_player=True)])]
    assert since(state) == [
        "- Since last page: exhausted (Ethereal): Sting x2, Ward."]


def test_an_upgraded_title_pluralises_before_the_plus():
    assert blindplay_render._plural_card("Ward+", 2) == "Wards+"
    assert blindplay_render._plural_card("Sting", 1) == "Sting"
