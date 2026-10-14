"""SEAT PAGE BACKLOG BATCH (2026-10-13): seven page-side BACKLOG lines.

- Ripple Basin's 4 Block is folded into Incoming where every one of the
  turn's resolution rows says its card type (the C# twin is
  `ResolutionLedgerTests.A_row_carries_its_card_type`).
- The Tainted per-hit note skips a part the bridge sent a breakdown for, as
  the Weak note does.
- Furina's Incoming names her guests' end-of-turn Block (Freminet); the C#
  twin is `FurinaSpendUpToTests.The_forecast_snapshot_sends_freminets_block`.
- The Vulnerable/Slow note names the "(Deals N damage)" faces that already
  fold the front enemy's.
- Knowledge Demon's briefing says what its Curse cards are.
- A combat board with no living enemy says so, in the refusal's words.
"""
from __future__ import annotations

import copy

from understudy import (blindplay, blindplay_enemies, blindplay_faces,
                        blindplay_render, qa_packet)

from tier0.tests.test_understudy_blindplay import combat_state

line = blindplay_render._incoming_line

RIPPLE = {"name": "Ripple Basin",
          "text": "At the end of your turn, if you did not play any Attacks "
                  "this turn, gain 4 Block."}


def _you(relics=()):
    return {"hp": 60, "max_hp": 80, "block": 0, "powers": [],
            "relics": list(relics), "orbs": None}


def _hit(n: int) -> dict:
    return {"name": "Nibbit", "hp": 20, "intents": [
        {"type": "Attack", "label": str(n), "title": "Butt"}]}


def _row(card_type: str, carried: bool = False) -> dict:
    return {"card": "X", "card_type": card_type, "carried": carried}


# ---- Ripple Basin ---------------------------------------------------------

# Kokomi review r5 (2026-10-14, A7): the relic's Block is printed beside the
# total, never inside it, until an Attack has been played (run 2 attacked
# after the page counted it).
CONDITIONAL = "Ripple Basin: +4 Block if you play no Attack (not in the total)."


def test_ripple_basin_prints_outside_the_total_with_no_attack_yet():
    got = line([_hit(12)], _you([RIPPLE]), [], [],
               [_row("Skill"), _row("Power")])
    assert "you would take 12" in got
    assert CONDITIONAL in got
    assert "Ripple Basin adds 4" not in got
    assert "Not counted" not in got


def test_ripple_basin_adds_nothing_once_an_attack_is_played():
    got = line([_hit(12)], _you([RIPPLE]), [], [],
               [_row("Skill"), _row("Attack")])
    assert "you would take 12" in got
    assert "Ripple Basin" not in got


def test_a_carried_attack_from_last_turn_does_not_count():
    got = line([_hit(12)], _you([RIPPLE]), [], [],
               [_row("Attack", carried=True)])
    assert CONDITIONAL in got


def test_an_empty_turn_and_an_older_mod_print_it_beside_the_total():
    for rows in ([], None, [_row("")]):
        got = line([_hit(12)], _you([RIPPLE]), [], [], rows)
        assert "you would take 12" in got
        assert CONDITIONAL in got
        assert "Not counted: Ripple Basin." not in got


def test_the_board_carries_the_card_type():
    from understudy import blindplay_board
    rows = blindplay_board.resolutions({"resolutions": [
        {"card": "Strike", "card_type": "Attack"}, {"card": "Defend"}]})
    assert [r["card_type"] for r in rows] == ["Attack", ""]


# ---- the per-hit note ------------------------------------------------------

TAINTED = {"name": "Tainted", "stacks": 2,
           "text": "Take 2 additional damage from Attacks."}


def test_the_per_hit_note_skips_a_part_with_a_breakdown():
    you = {"powers": [TAINTED]}
    plain = [{"intents": [{"type": "Attack", "label": "5x3"}]}]
    assert blindplay_render._per_hit_note(you, plain)
    folded = [{"intents": [{"type": "Attack", "label": "7x3", "breakdown": {
        "base": 5, "folded": 7, "repeats": 3, "total": 21,
        "modifiers": []}}]}]
    assert blindplay_render._per_hit_note(you, folded) == []


# ---- Freminet's Block ------------------------------------------------------

def test_the_stage_clause_names_freminets_block():
    stage = {"forecast": {"block": 0, "acts": [
        {"name": "Freminet", "kind": "block", "amount": 14},
        {"name": "Navia", "kind": "damage", "amount": 20}]}}
    assert blindplay_render._stage_block_clause(stage) == (
        " Your guests' end-of-turn acts come first and add 14 Block "
        "(Freminet).")


def test_the_stage_clause_without_a_block_act_is_unchanged():
    stage = {"forecast": {"block": 0, "acts": [
        {"name": "Navia", "kind": "damage", "amount": 20}]}}
    assert blindplay_render._stage_block_clause(stage) == ""


# ---- the Vulnerable/Slow note ----------------------------------------------

VULN = [{"name": "A", "hp": 10, "powers": [
    {"name": "Vulnerable", "stacks": 2}]}]
PLAIN = {"kind": "Attack", "title": "Strike", "text": "Deal 6 damage."}
DEALS = {"kind": "Attack", "title": "Riptide (2)",
         "text": "Deal damage equal to your Block.\n(Deals 15 damage)"}


def test_a_deals_face_is_named_beside_a_plain_one():
    got = blindplay_render._enemy_fold_note(VULN, [PLAIN, DEALS])
    assert got == ["", blindplay_render.ENEMY_FOLD_NOTE_EXCEPT.format(
        cards="**Riptide**")]
    assert "already counts the front enemy's" in got[1]


def test_only_deals_faces_get_the_short_note():
    got = blindplay_render._enemy_fold_note(VULN, [DEALS])
    assert got == ["", blindplay_render.ENEMY_FOLD_NOTE_ONLY.format(
        cards="**Riptide**")]
    assert "leave out" not in got[1]


def test_on_furinas_stage_the_note_stands_whole():
    assert blindplay_render._enemy_fold_note(VULN, [DEALS], stage=True) == [
        "", blindplay_render.ENEMY_FOLD_NOTE]
    assert blindplay_render._enemy_fold_note(VULN, [PLAIN]) == [
        "", blindplay_render.ENEMY_FOLD_NOTE]


def test_the_new_notes_are_blind():
    for note in (blindplay_render.ENEMY_FOLD_NOTE_EXCEPT,
                 blindplay_render.ENEMY_FOLD_NOTE_ONLY):
        qa_packet.assert_blind(note.format(cards="**Riptide**"))


# ---- Knowledge Demon -------------------------------------------------------

def test_the_knowledge_demon_brief_says_what_the_curse_cards_are():
    _name, brief = blindplay_enemies.ENEMY_BRIEFS["KNOWLEDGE_DEMON"]
    for fact in ("debuff for the rest of the fight", "Disintegration",
                 "6, then 7, then 8", "Mind Rot", "Sloth", "Waste Away",
                 "Block takes it"):
        assert fact in brief, fact
    assert not qa_packet.leaks(brief)


# ---- no living enemy -------------------------------------------------------

def _board(enemies: list[dict]) -> dict:
    state = copy.deepcopy(combat_state())
    state["battle"]["enemies"] = enemies
    return state


def test_an_empty_board_names_the_body_waiting_to_revive():
    state = copy.deepcopy(combat_state())
    first = blindplay.observe(state)
    assert "No enemy is standing" not in first
    names = blindplay_faces.remembered_enemy_names()
    assert names
    page = blindplay.observe(_board([]))
    want = blindplay_render.NO_LIVING_ENEMY_LINE.format(
        who=f" ({blindplay_render._and_list(names)})")
    assert want in page
    qa_packet.assert_blind(want)


def test_a_dead_row_on_the_wire_is_named_itself():
    state = copy.deepcopy(combat_state())
    body = copy.deepcopy(state["battle"]["enemies"][0])
    body["hp"] = 0
    page = blindplay.observe(_board([body]))
    assert blindplay_render.NO_LIVING_ENEMY_LINE.format(
        who=f" ({body['name']})") in page
