"""The relics smoke seats (2026-09-27): the page's half of the fixes.

Records (gitignored): `review/qa/seats-2026-09-27/relics-lane1.md` (Klee) and
`relics-lane2.md` (Furina). The mod's pins are in
`klee-mod/KleeTests/Prototype/ArmRelicsPotionsTests.cs`.

NOTHING MEASURED ON A PROTOTYPE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import copy

from understudy import blindplay, blindplay_board
from understudy.blindplay_notes import ARM_KEYWORDS, keyword_notes
from understudy.blindplay_render import _render_stage_log

from tier0.tests.test_furina_seat_defects_2026_09_26 import _beat, _seat
from tier0.tests.test_understudy_blindplay import combat_state


def _reward(*faces):
    return {"screen": "card_reward", "character": "Furina",
            "stage_arm": True,
            "offers": [{"title": t, "text": x} for t, x in faces]}


def _names(*faces):
    return [r["name"] for r in keyword_notes(_reward(*faces))]


# ---- Stagehand's Gloves: its Block is named --------------------------------

def test_a_relic_that_gave_block_is_named_with_what_it_gave():
    state = copy.deepcopy(combat_state())
    state["player"]["relic_answers"] = [
        {"source": "Stagehand's Gloves", "amount": 3, "target": "",
         "combat_id": "", "carried": False, "unit": "Block"}]
    assert blindplay_board.relic_answers(state["player"])[0]["unit"] == "Block"
    assert "- **Stagehand's Gloves** gave you 3 Block." in blindplay.observe(
        state)


# ---- "fade" is defined wherever the page says it ---------------------------

def test_the_fade_is_defined_in_one_clause():
    # The second text pass (2026-09-28): on a row of its own, for every
    # performer behind the front.
    assert ARM_KEYWORDS["fade"] == (
        "At the end of your turn, each performer behind the front loses half "
        "its Fanfare above 5, rounded down.")
    assert "fade" not in ARM_KEYWORDS["back performer"]


def test_a_face_that_says_fade_prints_the_row_that_defines_it():
    # The second text pass (2026-09-28): the fade's own row.
    assert "fade" in _names(
        ("Held Applause", "Gain 6 Block. Your performers don't fade this "
                          "turn."))
    assert "fade" in _names(
        ("Echoing Hall", "Whenever a performer fades, your front performer "
                         "gains half the Fanfare lost."))


# ---- Guest Book: what a Guest Star is --------------------------------------

def test_the_guest_star_row_says_which_cards_and_not_the_trio():
    # The second text pass (2026-09-28): the row says one of each; the
    # Summon row beside it (a Guest Star's face says "Summon") says the rest.
    row = ARM_KEYWORDS["Guest Star"]
    assert row.startswith("You can have one of each on stage.")


def test_naming_the_trio_does_not_print_their_rows():
    names = _names(("Star Billing+", "Whenever a Guest Star joins the stage, "
                                     "draw 2 cards."))
    assert "Guest Star" in names
    for trio in ("Gentilhomme Usher", "Surintendante Chevalmarin",
                 "Mademoiselle Crabaletta"):
        assert trio not in names


# ---- the play log: the seat an act was made from ---------------------------

def test_an_act_names_the_seat_it_acted_from_not_the_seat_it_holds_now():
    """Lane 2: "Chevalmarin (front seat) acted" was the middle seat when it
    acted. The beat carries its seat and the count standing then."""
    seats = [_seat("chevalmarin", "Chevalmarin", 0, 4, 1),
             _seat("chevalmarin", "Chevalmarin", 1, 3, 2)]
    lines = _render_stage_log({"seats": seats, "log": [
        _beat("act", "chevalmarin", "Chevalmarin", seat=1, bar=3, moved=0,
              key=2, standing=3)]})
    assert lines[0].startswith("  - **Chevalmarin** (middle seat) acted")
