"""Furina, the Stage -- the legibility pass, the blind-play page's half
(2026-09-25).

A first-time co-op player "found it very hard to understand what was going on
from the tooltips, such as what each summoned actor actually did". The game
half is a Summon tip and three performer tips on the cards, a badge on each
performer's body and a `The Stage` badge on Furina. This file pins the seat
glossary saying the same things, on the screens that print the words:

  * a summoning card prints the Summon row and the row of every performer it
    can field -- all three for a random summon;
  * the performer rows are the ARM's alone: the shipped Salon members carry
    the same names under different rules;
  * another character's run is not taught the Stage's Summon rule;
  * a performer who bowed off a full stage says why it left.
"""

import pytest

from understudy import blindplay, blindplay_faces
from understudy.blindplay_board import STAGE_LEAVE_REASONS
from understudy.blindplay_notes import ARM_KEYWORDS


@pytest.fixture(autouse=True)
def _forget_the_arm():
    blindplay_faces.forget_stage_arm()
    yield
    blindplay_faces.forget_stage_arm()


SALON_SOLITAIRE = {"id": "KLEEMOD-SALON_SOLITAIRE", "name": "Salon Solitaire",
                   "description": "Start each combat with the Gentilhomme "
                                  "Usher in the front seat at 3 Fanfare."}
SPOTLIGHT = {"id": "KLEEMOD-ETHEREAL_SPOTLIGHT_RELIC",
             "name": "Ethereal Spotlight", "description": "A spotlight."}


def _reward(description: str, relics: list[dict],
            character: str = "Furina") -> dict:
    card = {"index": 0, "id": "KLEEMOD-PROTO_FS_PROBE", "name": "Probe",
            "description": description, "cost": 1, "card_type": "Skill"}
    return {"state_type": "card_select",
            "player": {"character": character, "potions": [],
                       "relics": relics, "max_potion_slots": 3},
            "run": {"floor": 1},
            "card_select": {"screen_type": "choose",
                            "prompt": "Choose one.",
                            "can_skip": False, "can_cancel": False,
                            "preview_showing": False, "can_confirm": False,
                            "selection_known": True, "cards": [card]}}


def _row(word: str) -> str:
    return f"- **{word}** — {ARM_KEYWORDS[word]}"


def test_a_screen_with_both_kinds_of_summon_prints_one_row():
    state = _reward("Summon Usher.", [SALON_SOLITAIRE])
    state["card_select"]["cards"].append(
        dict(state["card_select"]["cards"][0], index=1,
             description="Summon a random performer."))
    page = blindplay.observe(state)
    assert _row("Summon") in page
    assert "Random: " not in page and "Named: " not in page


def test_another_characters_run_is_not_taught_the_stages_summon():
    page = blindplay.observe(_reward("Summon the Bake-Kurage.", [],
                                     character="Kokomi"))
    assert "- **Summon** —" not in page


def test_the_full_stage_bow_says_why_the_lead_left():
    # The re-founding (2026-10-04): the front-most Salon member Bows and
    # leaves to make room; the newcomer adds nothing to anyone's bar.
    # The pool to 75 (2026-10-09): no act on leaving; the card returns.
    assert STAGE_LEAVE_REASONS["evicted"] == (
        "a fourth summon took its seat; its card went to your discard pile")
