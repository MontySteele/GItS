"""The Kokomi review, round 5 (2026-10-14), section A ("Built without a pick").

The seat page's halves: the Plan strip's lands-and-Strength row (A2), the
Defend warning (A1), the order line (A2), Energy "N left of M" (A4), the
reaction preview that already counts its amplifier (A5), the capped
carry-out receipt (A6). Ripple Basin (A7) is pinned in
`test_seat_page_backlog_2026_10_13.py`, Sea Glass Harvest (A8) in
`test_kokomi_status_batch.py`. The C# twin is
`klee-mod/KleeTests/Prototype/KokomiReviewR5Tests.cs`.
"""
from __future__ import annotations

from tier0.tests.test_understudy_blindplay import (TWO_PLANS,
                                                   _past_lethal_state,
                                                   morning_of,
                                                   plans_combat_state)
from understudy import blindplay, blindplay_render

DEFEND = {"type": "Defend", "label": "", "title": "Defensive",
          "description": "This enemy intends to Block."}


def _page(queue, enemies=None) -> list[str]:
    state = _past_lethal_state(queue=queue, hp=40, enemies=enemies)
    return blindplay.render(blindplay.observation(state)).splitlines()


# ---- A2: what a waiting Plan lands, Strength named -------------------------

def test_a_waiting_plan_says_what_it_lands_with_strength_named():
    lines = _page([{"name": "Pearl Barrage", "clauses": 1, "damage": 0,
                    "aim": "all", "written": 10, "written_strength": -2}])
    assert ("     - Lands 10 to ALL next turn; your Strength was -2 when "
            "written.") in lines


def test_no_strength_clause_at_zero_and_nothing_for_an_older_bridge():
    lines = _page([{"name": "Kurage's Oath", "clauses": 1, "damage": 9,
                    "aim": "front", "written": 9, "written_strength": 0}])
    assert "     - Lands 9 at the front enemy next turn." in lines
    old = _page([{"name": "Kurage's Oath", "clauses": 1}])
    assert not any("Lands" in line for line in old)


def test_the_order_line_and_the_reworded_note_are_on_the_panel():
    lines = _page([{"name": "Kurage's Oath", "clauses": 1}])
    assert "- Plans carry out in the order written." in lines
    assert blindplay.PLAN_WRITTEN_NUMBER_NOTE in lines
    assert "- Strength is read when the Plan is written." not in lines


# ---- A1: a damage Plan into a body that intends to Block -------------------

def test_a_plan_into_a_defend_intent_names_the_enemy_and_the_number():
    seapunk = {"entity_id": "SEAPUNK_0", "combat_id": 1, "name": "Seapunk",
               "hp": 30, "max_hp": 30, "block": 0, "status": [],
               "intents": [DEFEND]}
    lines = _page([{"name": "Kurage's Oath", "clauses": 1, "damage": 9,
                    "aim": "front", "written": 9}], enemies=[seapunk])
    assert ("     - Seapunk intends to Block; Kurage's Oath (9) lands into "
            "that Block.") in lines


def test_no_warning_when_the_target_attacks():
    lines = _page([{"name": "Kurage's Oath", "clauses": 1, "damage": 9,
                    "aim": "front", "written": 9}])
    assert not any("intends to Block" in line for line in lines)


# ---- A4: Energy left of the turn's ----------------------------------------

def test_energy_reads_left_of():
    page = blindplay.observe(plans_combat_state(TWO_PLANS))
    assert any(line.startswith("- Energy ") and " left of " in line
               for line in page.splitlines())


# ---- A5: the reaction preview a hand's number already counts --------------

def _card(text, written=None):
    return {"text": text, "written_face": written}


def test_a_preview_that_already_counts_prints_it_once():
    k = {"name": "Reaction preview: Vaporize",
         "text": ("The triggering hit deals 1.5x damage and consumes the "
                  "aura. The 21 on this card already counts it: into that "
                  "Hydro aura it lands 21.")}
    got = blindplay_render._reaction_preview_text(
        _card("Deal 21 Electro damage."), k)
    assert got.endswith("aura. 21 (Vaporize counted).")


def test_an_older_mods_second_multiplier_is_caught_off_the_face():
    k = {"name": "Reaction preview: Vaporize",
         "text": ("The triggering hit deals 1.5x damage and consumes the "
                  "aura. Into that Hydro aura this card's 21 lands 31.")}
    got = blindplay_render._reaction_preview_text(
        _card("Deal 21 damage to ALL enemies.",
              "Deal 14 damage to ALL enemies."), k)
    assert "31" not in got and got.endswith("21 (Vaporize counted).")
    # A face that does not already count it prints as sent.
    plain = blindplay_render._reaction_preview_text(
        _card("Deal 14 damage.", None), dict(k, text=k["text"].replace(
            "21 lands 31", "14 lands 21")))
    assert plain.endswith("this card's 14 lands 21.")


# ---- A6: the carry-out receipt under Hard To Kill -------------------------

def test_a_capped_carry_out_says_asked_and_landed():
    state = plans_combat_state(morning_of(
        {"card": "Kurage's Oath+", "number": 18, "kind": "damage",
         "asked": 12, "line": "Bake-Kurage: Kurage's Oath+, 18",
         "moved": [{"target": "Exoskeleton", "amount": 9}]}))
    battle = dict(state["battle"])
    battle["enemies"] = [
        {"entity_id": "EXO_0", "combat_id": 1, "name": "Exoskeleton",
         "hp": 20, "max_hp": 29, "block": 0,
         "status": [{"id": "HARD_TO_KILL", "name": "Hard To Kill",
                     "amount": 9, "type": "Buff",
                     "description": "No single hit takes more than 9."}],
         "intents": [{"type": "Attack", "label": "5", "title": "Bite",
                      "description": "This enemy intends to Attack for 5."}]}]
    state = dict(state, battle=battle)
    page = blindplay.render(blindplay.observation(state))
    assert ("Bake-Kurage: Kurage's Oath+, 18 — asked for 12, 9 landed "
            "(Hard To Kill).") in page
    assert "the clause asked for 12" not in page
