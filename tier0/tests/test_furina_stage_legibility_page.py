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
from understudy.blindplay_notes import ARM_KEYWORDS, SUMMON_NAMED_ROW


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


def test_a_named_summon_prints_the_summon_row_and_its_performers_row():
    page = blindplay.observe(_reward(
        "Summon Chevalmarin. If she is already on stage, Raise 3 on her "
        "instead.", [SALON_SOLITAIRE]))
    # The NAMED variant: no full-stage sentence beside "Raise 3 instead".
    assert f"- **Summon** — {SUMMON_NAMED_ROW}" in page
    assert "the lead takes a Bow" not in page
    assert _row("Surintendante Chevalmarin") in page
    assert _row("Mademoiselle Crabaletta") not in page


def test_a_screen_with_both_kinds_of_summon_prints_both_variants():
    state = _reward("Summon Usher. If he is already on stage, Raise 3 on him "
                    "instead.", [SALON_SOLITAIRE])
    state["card_select"]["cards"].append(
        dict(state["card_select"]["cards"][0], index=1,
             description="Summon a random performer."))
    page = blindplay.observe(state)
    assert (f"- **Summon** — Random: {ARM_KEYWORDS['Summon']} Named: "
            f"{SUMMON_NAMED_ROW}") in page


def test_a_random_summon_prints_every_performer_it_can_field():
    page = blindplay.observe(_reward("Summon two random performers.",
                                     [SALON_SOLITAIRE]))
    assert _row("Summon") in page
    for who in ("Gentilhomme Usher", "Surintendante Chevalmarin",
                "Mademoiselle Crabaletta"):
        assert _row(who) in page, who


def test_a_mid_sentence_summon_is_the_same_word():
    """Improvised Number prints it lowercase, and the mod attaches the tip
    off the op, not the capital."""
    page = blindplay.observe(_reward(
        "Deal 6 damage. If the stage is empty, summon a random performer.",
        [SALON_SOLITAIRE]))
    assert _row("Summon") in page
    assert _row("Mademoiselle Crabaletta") in page


def test_the_shipped_kit_is_not_taught_the_arms_performers():
    """The shipped Salon's Usher is a different rule under the same name."""
    page = blindplay.observe(_reward(
        "Deploy Usher. He performs when you play a Companion.", [SPOTLIGHT]))
    assert _row("Gentilhomme Usher") not in page
    assert "End of your turn: gain 3 Block." not in page


def test_another_characters_run_is_not_taught_the_stages_summon():
    page = blindplay.observe(_reward("Summon the Bake-Kurage.", [],
                                     character="Kokomi"))
    assert "- **Summon** —" not in page


def test_the_full_stage_bow_says_why_the_lead_left():
    assert STAGE_LEAVE_REASONS["recast"] == (
        "took its Bow to make room for a summon, and comes back to the back "
        "seat with its Fanfare")
