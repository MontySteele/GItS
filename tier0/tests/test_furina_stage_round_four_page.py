"""Furina, the Stage -- round four's page fixes.

Two seat rounds on the Stage arm sent these back, and the main session ruled
each fix; this file pins the blind-play page's half of them:

  * FANFARE WAS DEFINED TWO WAYS. Outside combat the glossary gave the shipped
    meter's row ("Furina's own meter ... this run has no stage"), in combat
    the performer's bar. The Stage's starting relic now answers the arm on
    every screen, so every screen of a Stage run prints the bar.
  * THE RAISE ROW carried the empty-stage summon and was generic on where.
    The text pass (2026-09-25) retired `Raise`; the back performer row
    carries the empty-stage summon now.
  * THE OUSIA AND PNEUMA ROWS rode Ousia Surge and Pneuma Refrain because the
    names match; they now print only beside Arkhe Alignment.

The Chevalmarin per-enemy line and the back-seat sentence are pinned beside
the stage section's other lines, in `test_eb735_eb736_the_page_prints_the_
stage.py`.
"""

import pytest

from understudy import blindplay, blindplay_faces
from understudy.blindplay_notes import (ARM_KEYWORDS, FANFARE_SHIPPED_ROW,
                                        keyword_notes)


@pytest.fixture(autouse=True)
def _forget_the_arm():
    blindplay_faces.forget_stage_arm()
    yield
    blindplay_faces.forget_stage_arm()


def _reward_state(relics: list[dict]) -> dict:
    """A choose-a-card screen before any fight has answered the arm: no
    combat block, and an empty latch."""
    card = {"index": 0, "id": "KLEEMOD-PROTO_FS_WARM_RECEPTION",
            "name": "Warm Reception",
            "description": ("Your back performer gains 3 Fanfare. "
                            "Draw 1 card."),
            "cost": 1, "card_type": "Skill"}
    return {"state_type": "card_select",
            "player": {"character": "Furina", "potions": [],
                       "relics": relics, "max_potion_slots": 3},
            "run": {"floor": 1},
            "card_select": {"screen_type": "choose",
                            "prompt": "Choose one.",
                            "can_skip": False, "can_cancel": False,
                            "preview_showing": False, "can_confirm": False,
                            "selection_known": True, "cards": [card]}}


SALON_SOLITAIRE = {"id": "KLEEMOD-SALON_SOLITAIRE", "name": "Salon Solitaire",
                   "description": "At the start of combat, Usher takes the "
                                  "front seat with 3 Fanfare."}


def test_the_stage_relic_answers_the_arm_off_combat():
    page = blindplay.observe(_reward_state([SALON_SOLITAIRE]))

    assert ARM_KEYWORDS["Fanfare"] in page
    assert FANFARE_SHIPPED_ROW not in page


def test_a_run_without_the_relic_keeps_the_shipped_reading():
    page = blindplay.observe(_reward_state(
        [{"id": "KLEEMOD-ETHEREAL_SPOTLIGHT_RELIC",
          "name": "Ethereal Spotlight", "description": "A spotlight."}]))

    assert FANFARE_SHIPPED_ROW in page


def test_the_back_performer_row_carries_the_empty_stage_summon():
    page = blindplay.observe(_reward_state([SALON_SOLITAIRE]))

    assert ("With no one on stage, Fanfare it would gain summons a random "
            "performer instead.") in page
    assert "**Raise**" not in page


# --- Ousia and Pneuma belong to Arkhe Alignment -----------------------------

def _names(obs: dict) -> set[str]:
    return {row["name"] for row in keyword_notes(obs)}


def test_ousia_and_pneuma_do_not_ride_cards_that_share_the_word():
    # The name reached the haystack (a deck line, a play log) with no Arkhe
    # Alignment anywhere on the screen.
    obs = {"character": "Furina", "stage_arm": True,
           "hand": [{"title": "Ousia Surge",
                     "text": "Deal damage equal to the back performer's "
                             "Fanfare."},
                    {"title": "Pneuma Refrain",
                     "text": "Gain Block equal to your front performer's "
                             "Fanfare."}],
           "played": ["You played Ousia Surge.",
                      "You played Pneuma Refrain."]}

    names = _names(obs)
    assert "Ousia" not in names
    assert "Pneuma" not in names


def test_ousia_and_pneuma_print_beside_arkhe_alignment():
    obs = {"character": "Furina", "stage_arm": True,
           "hand": [{"title": "Arkhe Alignment",
                     "text": "At the start of your turn, choose Ousia or "
                             "Pneuma."},
                    {"title": "Ousia Surge",
                     "text": "Deal damage equal to the back performer's "
                             "Fanfare."}]}

    names = _names(obs)
    assert {"Ousia", "Pneuma"} <= names


def test_the_arkhe_power_badge_anchors_them_too():
    obs = {"character": "Furina", "stage_arm": True,
           "combat": {"you": {"powers": [
               {"name": "Arkhe Alignment", "amount": 1,
                "text": "At the start of your turn, choose Ousia or "
                        "Pneuma."}]}}}

    assert {"Ousia", "Pneuma"} <= _names(obs)
