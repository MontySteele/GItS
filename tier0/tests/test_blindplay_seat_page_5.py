"""Seat page 5 (2026-10-05): compact enemy intent lines.

Every Sonnet seat in the 2026-10-05 round cut its pages with sed/grep to get
around the boilerplate on each intent line. Same facts, fewer words:

1. The side a part lands on stays on the line ("lands on you"); the missing
   target is ONE line under the enemy list, on every page with two or more
   enemies (never once per lane: a sed slice loses once-only text).
2. The game's generic hover sentence is dropped when the line already says
   it; a sentence that carries anything more, or disagrees, is kept.
3. "icon shows 8" for "the number on its icon is 8".
4. The fold, total and defend clauses keep every number in compact form.

The owner's terms: page facts, never a computed plan.
"""
from __future__ import annotations

import copy

from understudy import blindplay, blindplay_notes, blindplay_render

from tier0.tests.test_understudy_blindplay import combat_state


def _breakdown(base, folded, repeats=1, modifiers=()):
    return {"base_damage": base, "folded_damage": folded,
            "repeats": repeats, "total_damage": folded * repeats,
            "modifiers": list(modifiers)}


def _board(*intent_lists) -> dict:
    """The recorded combat with one enemy per intent list."""
    state = copy.deepcopy(combat_state())
    template = state["battle"]["enemies"][0]
    enemies = []
    for n, intents in enumerate(intent_lists):
        body = copy.deepcopy(template)
        body["entity_id"] = f"BODY_{n}"
        body["combat_id"] = n + 1
        body["name"] = f"Body {n}"
        body["intents"] = intents
        enemies.append(body)
    state["battle"]["enemies"] = enemies
    return state


def _intent_lines(page: str) -> list[str]:
    return [ln for ln in page.splitlines()
            if ln.lstrip().startswith(("Intent:", "and also:"))]


ATTACK = {"type": "Attack", "label": "8", "title": "Aggressive",
          "target_side": "you",
          "description": "This enemy intends to Attack for 8 damage."}
BUFF = {"type": "Buff", "label": "", "title": "Empower",
        "target_side": "its own side",
        "description": "This enemy intends to use a Buff."}
STATUS = {"type": "StatusCard", "label": "1", "title": "Strategic",
          "target_side": "you",
          "description": "This enemy intends to give you 1 Status card."}


# ------------------------------------------------ 2. the hover sentence --


def test_a_generic_hover_sentence_is_dropped():
    page = blindplay.observe(_board([ATTACK], [BUFF, STATUS]))
    assert "This enemy intends to Attack for 8 damage." not in page
    assert "This enemy intends to use a Buff." not in page
    assert "This enemy intends to give you 1 Status card." not in page
    assert "Intent: Aggressive (Attack) — icon shows 8 — lands on you" in page


def test_a_hover_sentence_that_says_more_is_kept():
    burn = {"type": "StatusCard", "label": "4", "title": "Strategic",
            "description": "This enemy intends to add 4 Burn to your hand."}
    block = {"type": "Defend", "label": "", "title": "Defensive",
             "description": "This enemy intends to gain 8 Block."}
    page = blindplay.observe(_board([burn], [block]))
    assert "This enemy intends to add 4 Burn to your hand." in page
    assert "This enemy intends to gain 8 Block." in page


def test_a_generic_sentence_with_a_number_not_on_the_icon_is_kept():
    """No label at all: the sentence's 2 is the only place the count is."""
    status = dict(STATUS, label="",
                  description="This enemy intends to give you 2 Status cards.")
    page = blindplay.observe(_board([status]))
    assert "This enemy intends to give you 2 Status cards." in page


def test_a_disagreeing_sentence_is_kept_with_its_clause():
    """`EB-607`: icon 15, sentence 12. Both print, and the clause says so."""
    attack = dict(ATTACK, label="15",
                  description="This enemy intends to Attack for 12 damage.")
    page = blindplay.observe(_board([attack]))
    assert "This enemy intends to Attack for 12 damage." in page
    assert blindplay_notes.INTENT_NUMBER_DISAGREES in page


def test_a_multi_hit_sentence_matching_its_icon_is_dropped():
    attack = dict(ATTACK, label="3x3",
                  description="This enemy intends to Attack for 3 damage 3 "
                              "times.")
    assert blindplay_render._hover_adds_nothing(
        {"label": attack["label"], "text": attack["description"]})
    page = blindplay.observe(_board([attack]))
    assert "3 damage 3 times" not in page


# ------------------------------------------------- 1. the target caveat --


def test_the_target_caveat_prints_once_with_two_or_more_enemies():
    page = blindplay.observe(_board([ATTACK], [BUFF, STATUS], [ATTACK]))
    assert page.count(blindplay_notes.INTENT_TARGET_NOTE) == 1
    for line in _intent_lines(page):
        assert "cannot say which body" not in line
    # Every page, not once per lane: a second observe prints it again.
    again = blindplay.observe(_board([ATTACK], [BUFF, STATUS], [ATTACK]))
    assert blindplay_notes.INTENT_TARGET_NOTE in again


def test_the_target_caveat_is_absent_with_one_enemy():
    page = blindplay.observe(_board([BUFF, STATUS]))
    assert blindplay_notes.INTENT_TARGET_NOTE not in page
    assert "cannot say which body" not in page
    assert "— lands on its own side" in page
    assert "— lands on you" in page


# --------------------------------------- 3/4. the compact number clauses --


def test_the_icon_number_and_part_label_are_short():
    page = blindplay.observe(_board([ATTACK, STATUS]))
    assert "icon shows 8, one part of this move" in page
    assert "the number on its icon" not in page


def test_the_fold_clause_keeps_base_folded_and_modifier():
    attack = dict(ATTACK, breakdown=_breakdown(6, 8, modifiers=["Strength"]))
    page = blindplay.observe(_board([attack]))
    assert "6 base, 8 with **Strength**" in page


def test_the_nothing_folded_and_total_clauses():
    attack = dict(ATTACK, label="3x3", breakdown=_breakdown(3, 3, repeats=3))
    page = blindplay.observe(_board([attack]))
    assert "3 base, nothing folded in" in page
    assert "3 x 3 = 9 if every hit lands" in page


def test_the_defend_clause_says_it_adds_and_has_no_amount():
    defend = {"type": "Defend", "label": "", "title": "Defensive",
              "target_side": "its own side"}
    page = blindplay.observe(_board([ATTACK, defend]))
    assert ("and also: Defensive (Defend) — adds to its Block above; amount "
            "not on the feed — lands on its own side") in page


def test_the_buff_clause_without_a_wire_side():
    page = blindplay.observe(_board([{"type": "Buff", "title": "Empower"}]))
    assert "Intent: Empower (Buff) — lands on its own side, not on you" in page


def test_the_brief_page_keeps_the_target_caveat():
    """The brief page drops standing notes; this one is the line that says
    what the intent lines cannot, so it stays."""
    from understudy import blindplay_brief
    page = blindplay.observe(_board([ATTACK], [BUFF, STATUS]))
    assert blindplay_notes.INTENT_TARGET_NOTE in blindplay_brief.brief(page)
