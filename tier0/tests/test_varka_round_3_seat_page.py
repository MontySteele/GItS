"""THE VARKA ROUND 3 SEAT-PAGE FIXES
(review/records/varka-round-3-2026-10-10.md, "What changes", item 5):

  * a Knight's hand row carries its element ("Knight, Electro.");
  * the glossary's Oath note says a Swirl's Oath is of the element it Swirls;
  * the "would take N" line folds a power's plain end-of-turn Block off its
    hover text, and names one it cannot count under "Not counted";
  * while a relic forbids drawing on your turn (Fiddle), a face that prints
    "Draw N" says "(no draw: Fiddle)";
  * Kaiser Crab's Surrounded says what turns you
    (`SurroundedPower.BeforeCardPlayed`, 0.111.0 decompile).

The card changes (Stormward Stance, Sworn Brotherhood, Frost Ward) are pinned
in `test_varka_oath`, `test_power_cost_sweep_2026_09_30` and
`test_varka_rebalance`.
"""
from __future__ import annotations

import pytest

from understudy import blindplay, blindplay_render
from tier0.tests.test_control_seat_fixes_2026_09_26 import _crab
from tier0.tests.test_varka_amber_round import _card, _hand, _rows_after
from tier0.tests.test_varka_seat_page import varka_state


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    blindplay.forget_run()
    yield
    blindplay.forget_fight()
    blindplay.forget_run()


@pytest.fixture(autouse=True)
def _no_live_speed(monkeypatch):
    from understudy import blindplay_faces as faces
    monkeypatch.setattr(faces, "FAST_MODE_READER", lambda: "")


# ---- the Knight tag -----------------------------------------------------------

def test_a_knight_row_names_its_element():
    state = varka_state()
    _hand(state, _card(state, "Lisa: Infinite Circuit",
                       "Knight. Deal 5 Electro damage.", "Electro"))
    rows = _rows_after(blindplay.observe(state), "Lisa: Infinite Circuit")
    assert rows[1] == "    Knight, Electro. Deal 5 Electro damage."


def test_a_card_that_is_not_a_knight_is_untouched():
    state = varka_state()
    _hand(state, _card(state, "Kindled Edge", "Deal 6 Pyro damage.", "Pyro"))
    rows = _rows_after(blindplay.observe(state), "Kindled Edge")
    assert rows[1] == "    Deal 6 Pyro damage."


def test_the_tag_reads_the_printed_element_not_an_override():
    c = {"text": "Knight. Deal 6 Pyro damage.", "printed_element": "Pyro",
         "element": "Electro"}
    assert blindplay_render._knight_tagged(c).startswith("Knight, Pyro.")


# ---- the Oath note ------------------------------------------------------------

def test_the_oath_note_says_whose_oath_a_swirl_gives():
    state = varka_state()
    _hand(state, _card(state, "Windbound Execution",
                       "Deal 6 damage. Gain 1 Oath of your current element.",
                       "Anemo"))
    glossary = blindplay.observe(state).split("## Words on this screen", 1)[1]
    assert ("Element cards read their own, others the current. A Swirl gives "
            "1 Oath of the element it Swirls, not of your current element."
            ) in glossary


# ---- the would-take line ------------------------------------------------------

line = blindplay_render._incoming_line


def _you(powers=(), relics=(), block=0):
    return {"hp": 60, "max_hp": 80, "block": block, "powers": list(powers),
            "relics": list(relics), "orbs": None}


def _hit(n):
    return [{"name": "Nibbit", "hp": 20, "intents": [
        {"type": "Attack", "label": str(n), "title": "Butt"}]}]


def _power(name, text, stacks=1):
    return {"name": name, "stacks": stacks, "text": text}


def test_a_plain_end_of_turn_block_power_is_folded():
    gale = _power("Gale Ward", "At the end of your turn, Swirl the enemy "
                               "with the most auras and gain 6 Block.")
    assert line(_hit(10), _you([gale]), [], []) == (
        "- Incoming this turn: 10 (your Block 0): you would take 4 "
        "(Gale Ward adds 6 Block first). You would be at 56/80 HP.")


def test_a_conditional_end_of_turn_block_power_is_named():
    mantle = _power("Gale Mantle", "At the end of your turn, gain Block "
                                   "equal to half your total Oath.")
    iffy = _power("Bombproof", "At the end of your turn, gain 4 Block if "
                               "none of your Bombs went off.")
    got = line(_hit(10), _you([mantle, iffy]), [], [])
    assert got.startswith("- Incoming this turn: 10 (your Block 0): you "
                          "would take 10.")
    assert got.endswith("Not counted: Gale Mantle and Bombproof.")


def test_a_power_with_no_end_of_turn_block_changes_nothing():
    dawn = _power("Dawn Wind's March", "Whenever you gain Oath of your "
                                       "current element, gain 3 Block.")
    assert line(_hit(10), _you([dawn]), [], []) == (
        "- Incoming this turn: 10 (your Block 0): you would take 10. "
        "You would be at 50/80 HP.")


def test_the_power_eot_block_reader():
    read = blindplay_render._power_eot_block
    assert read("At the end of your turn, gain 5 Block.") == 5
    assert read("Lose 3 HP. At the end of your turn deal 5 Electro damage "
                "to ALL enemies and gain 5 Block.") == 5
    assert read("At the end of your turn, keep up to 6 of your Block.") == 0
    assert read("At the end of your turn deal 6 damage to a random enemy if "
                "you are above 70% HP; otherwise, gain 6 Block.") is None
    assert read("Whenever you play a card, gain 1 Block.") == 0


# ---- Fiddle -------------------------------------------------------------------

FIDDLE = {"id": "FIDDLE", "name": "Fiddle", "counter": None, "keywords": [],
          "description": "At the start of your turn, draw 2 additional "
                         "cards. You may not draw cards during your turn."}


def test_fiddle_tags_a_face_that_draws():
    state = varka_state()
    state["player"]["relics"].append(FIDDLE)
    _hand(state,
          _card(state, "Tailwind Stride", "Gain 5 Block. Draw 1 card.",
                card_type="Skill"),
          _card(state, "Gale Sweep", "Deal 5 Anemo damage.", "Anemo"))
    page = blindplay.observe(state)
    assert _rows_after(page, "Tailwind Stride")[1] == (
        "    Gain 5 Block. Draw 1 card. (no draw: Fiddle)")
    assert _rows_after(page, "Gale Sweep")[1] == "    Deal 5 Anemo damage."


def test_no_tag_without_fiddle():
    state = varka_state()
    _hand(state, _card(state, "Tailwind Stride", "Gain 5 Block. Draw 1 card.",
                       card_type="Skill"))
    assert "(no draw:" not in blindplay.observe(state)


# ---- Kaiser Crab ----------------------------------------------------------------

def test_surrounded_says_what_turns_you():
    page = blindplay.observe(_crab(["5"]))
    assert ("Behind you now: **Rocket**. Playing a card on an enemy turns you "
            "to face it.") in page
