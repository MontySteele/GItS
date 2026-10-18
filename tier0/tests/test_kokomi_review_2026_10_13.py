"""The Kokomi review (2026-10-13), section 4.A ("Build now").

Fable's review of the level-pass wave, its A-list built as ruled (provenance
"Kokomi review, 2026-10-13"). The C# twin is
`klee-mod/KleeTests/Prototype/KokomiReviewTests.cs`. War Council's row was
built separately (#1201).
"""
from __future__ import annotations

import copy

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, kokomi_plan
from tier0.engine.state import Card
from tier0.tests.test_arm_keyword_tips import proto
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, carry_out, kokomi_state)
from understudy import blindplay

ATTACKER = [{"kind": "attack", "amount": 5}]


def _rows() -> dict:
    return {c.id: c for c in loader.prototype_cards()}


def _face(card_id: str) -> str:
    return {r["id"]: r for r in proto._rows()}[card_id]["description"]


def _card(cid: str) -> Card:
    return copy.deepcopy(loader.get_card(cid))


def _probe_plan() -> Card:
    return Card(id="proto_kk_probe", name="probe", cost=1, type="skill",
                effects=[], plan=[{"op": "draw", "amount": 1}])


# --- 1. Tide Wall: the face names the turn it reads ------------------------

def test_tide_wall_face_names_the_turn_it_lands():
    assert _face("proto_kk_tide_wall") == (
        "Gain 4 [gold]Block[/gold]. [gold]Plan[/gold]: Gain "
        "{PlanBlock:diff()} [gold]Block[/gold], plus the biggest attack an "
        "enemy intends on the turn it lands.")
    # The behaviour is unchanged: the read happens at carry-out.
    assert _rows()["proto_kk_tide_wall"].plan == [
        {"op": "block_max_intent", "amount": 6}]


# --- 1 and 6. the seat page: the live total and the first Plan --------------

def _page(queue: list[dict]) -> str:
    state = {"state_type": "monster",
             "player": {"character": "Kokomi", "hp": 60, "max_hp": 80,
                        "block": 0, "energy": 3, "max_energy": 3, "hand": [],
                        "potions": [], "relics": [], "status": [],
                        "pets": [],
                        "draw_pile_count": 5, "discard_pile_count": 0,
                        "exhaust_pile_count": 0,
                        "kokomi_plans": {
                            "pet": True, "pet_name": "Bake-Kurage",
                            "pet_entity_id": "KURAGE",
                            "pending": len(queue), "twice": False,
                            "queue": queue, "carried_out": []}},
             "battle": {"round": 2, "enemies": [
                 {"entity_id": "SEAPUNK", "combat_id": 1, "name": "Seapunk",
                  "hp": 30, "max_hp": 44, "block": 0,
                  "intents": [{"type": "Attack", "damage": 23}],
                  "status": []}]}}
    blindplay.forget_run()
    try:
        return blindplay.observe(state)
    finally:
        blindplay.forget_run()


def test_a_waiting_tide_wall_prints_its_total_against_the_board_now():
    page = _page([{"name": "Tide Wall", "clauses": 1, "damage": 0,
                   "aim": "", "block_now": 29}])
    assert ("  1. **Tide Wall** (29 Block against the attacks intended now; "
            "it reads them again on the turn it lands)") in page


def test_an_older_bridge_or_another_plan_prints_no_total():
    page = _page([{"name": "Kelp Wall", "clauses": 1, "damage": 0,
                   "aim": "", "block_now": None},
                  {"name": "Tide Wall", "clauses": 1, "damage": 0,
                   "aim": ""}])
    assert "Block against the attacks intended now" not in page


def test_the_first_of_two_waiting_plans_is_named_first():
    page = _page([{"name": "Ambush", "clauses": 1, "damage": 12,
                   "aim": "front"},
                  {"name": "Kelp Wall", "clauses": 1, "damage": 0,
                   "aim": ""}])
    assert "  1. **Ambush** (first)" in page
    assert "  2. **Kelp Wall**" in page
    assert "**Kelp Wall** (first)" not in page


def test_a_lone_plan_is_not_marked_first():
    page = _page([{"name": "Ambush", "clauses": 1, "damage": 12,
                   "aim": "front"}])
    assert "(first)" not in page


# --- 2. a waiting Attack Plan into Block --------------------------------------

def test_into_block_reads_into_n_block():
    from understudy import blindplay_notes
    assert blindplay_notes.PLAN_INTO_BLOCK_CLAUSE.format(block=8) == (
        " (into 8 Block)")


# --- 3. Grand Design: unplayable with nothing to plan -------------------------

def _grand_design() -> Card:
    return _card("proto_kk_grand_design")


def test_grand_design_needs_a_card_to_plan():
    st = kokomi_state()
    st.player.energy = 3
    gd = _grand_design()
    assert kokomi_plan.needs_a_plannable_card(gd) is True
    st.player.hand = [gd, _card("proto_kk_shoal_call")]
    assert combat.card_playable(st, gd) is False
    st.player.hand.append(_probe_plan())
    assert combat.card_playable(st, gd) is True


def test_grand_design_does_not_count_itself():
    st = kokomi_state()
    st.player.energy = 3
    gd = _grand_design()
    st.player.hand = [gd]
    assert combat.card_playable(st, gd) is False


def test_grand_designs_face_is_unchanged():
    # 2026-10-18 (ruled): "Basic cards included."
    assert _face("proto_kk_grand_design") == (
        "Plan up to {KkAmount:diff()} cards from your [gold]Hand[/gold], "
        "Basic cards included. They cost 0.")


# --- 4. Change of Plans: only with a Plan waiting -----------------------------

def test_change_of_plans_face_and_gate():
    assert _face("proto_kk_change_of_plans").startswith(
        "Can only be played if a [gold]Plan[/gold] is waiting. ")
    card = _card("proto_kk_change_of_plans")
    st = kokomi_state()
    st.player.energy = 3
    assert combat.card_playable(st, card) is False
    kokomi_plan.schedule(st, _probe_plan())
    assert combat.card_playable(st, card) is True


def test_no_gate_off_kokomi():
    """The clause is hers: on another character nothing is refused."""
    st = kokomi_state()
    st.player.character_id = "klee"
    card = _card("proto_kk_change_of_plans")
    assert kokomi_plan.refuses_for_no_plan(st, card) is False


# --- 5. Treatise: the face names what counts ----------------------------------

def test_treatise_face():
    assert _face("proto_kk_treatise") == (
        "The first time each turn you play a [gold]Plan[/gold] card or a "
        "[gold]Companion[/gold] without planning it, draw 1 card.")


def test_masterstroke_can_only_be_planned():
    """A Plan-only card (no now-line) is always planned, so Treatise never
    counts it, and the new face says why: "without planning it"."""
    row = _rows()["proto_kk_masterstroke"]
    assert row.effects == [] and row.plan


# --- 8. Tidal Riposte (stored since the Kokomi card paper v2, 2026-10-18) ---

def test_tidal_riposte_face():
    assert _face("proto_kk_tidal_riposte") == (
        "Whenever you fully [gold]Block[/gold] an enemy's attack, your next "
        "Attack deals {PowerAmount:diff()} additional damage.")


# --- 9. the rarity swap -------------------------------------------------------

def test_shoal_call_common_and_brine_sting_uncommon():
    rows = _rows()
    assert rows["proto_kk_shoal_call"].rarity == "common"
    assert rows["proto_kk_brine_sting"].rarity == "uncommon"
    # The pool overhaul (2026-10-13): a Counter Plan line; 8 -> 10 in the
    # numbers pass (kokomi-review-r5-2026-10-14).
    assert _face("proto_kk_brine_sting") == (
        "Deal 10 [gold]Hydro[/gold] damage. [gold]Plan[/gold]: Deal 10 "
        "[gold]Hydro[/gold] damage to each enemy that attacked you since "
        "you planned this.")
    assert _face("proto_kk_shoal_call") == (
        "Add {KkAmount:diff()} [gold]Stings[/gold] to your "
        "[gold]Hand[/gold].")


def test_the_pool_stays_20_38_20():
    import collections
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == 79  # Kokomi v3 (2026-10-18): Unbroken Tide
    rarity = collections.Counter(loader.get_card(cid).rarity for cid in ids)
    assert rarity == {"common": 20, "uncommon": 39, "rare": 20}


# --- 10. Kurage's Wake: three Stings ------------------------------------------

def test_kurages_wake_plans_three_stings():
    row = _card("proto_kk_kurages_wake")
    assert row.plan == [{"op": "add_stings", "amount": 3}]
    assert "[gold]Plan[/gold]: Add 3 [gold]Stings[/gold]" in _face(
        "proto_kk_kurages_wake")
    st = kokomi_state()
    st.player.hand = []
    kokomi_plan.schedule(st, row)
    carry_out(st)
    assert [c.id for c in st.player.hand].count("proto_kk_sting") == 3
