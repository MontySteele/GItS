"""Furina, the Stage -- round three's page defects.

The read is not on main: it is on PR #476's branch, so it is retrieved the way
CLAUDE.md sec."History retrieval" gives --
`git show origin/furina-r3:review/active/furina-stage-round-3-2026-09-09.md`,
sec.4. Three of its six rows are the blind-play page's and this file pins them:

  * THE MODE CHOOSER TOOK TWO COMMANDS AND ONE OF THEM COULD ONLY BE REFUSED.
    "The Spend mode chooser needs `choose` twice: the first returns ok and the
    chooser stays open, the next commands are refused; about eight occurrences
    a run, two refusals spent on it." The screen is the game's choose-a-card
    screen, which resolves on the pick and has no confirm button; the page
    printed `EB-674`'s two-command sentence on it anyway.

  * THE GLOSSARY ALTERNATED BETWEEN TWO SENTENCES INSIDE ONE FIGHT, because
    the arm signal was the combat block and a chooser overlay is not a combat
    screen. The arm is a fact about the RUN and is latched for it now.

  * `EB-728`, the same signal's other row: `Fanfare` is a word both of
    Furina's kits print, and the table stated the Stage's bar unconditionally.

  * TWO COPIES OF ONE CARD IN HAND PRINTED AS TWO IDENTICAL ROWS. The
    blind-play page has numbered repeats since `EB-177`; the QA packet, the
    parallel renderer, never got it.
"""

import pytest

from understudy import blindplay, blindplay_faces, qa_packet
from understudy.blindplay_notes import (CHOOSER_CONFIRM_NOTE,
                                        FANFARE_SHIPPED_ROW, _stage_arm)


# --- the chooser that cost two refusals a pick -----------------------------

def _chooser_state() -> dict:
    """SYNTHETIC, in `BuildChooseCardState`'s shape -- the screen a modal card
    opens. `can_confirm` is false as that builder always sends it."""
    card = {"index": 0, "id": "KLEEMOD-MODE", "name": "Deal 5 damage",
            "description": "Deal 5 damage", "cost": 0, "card_type": "Skill"}
    return {"state_type": "card_select",
            "player": {"character": "furina", "potions": [], "relics": [],
                       "max_potion_slots": 3},
            "card_select": {"screen_type": "choose",
                            "prompt": "Choose one.",
                            "can_skip": False, "can_cancel": False,
                            "preview_showing": False, "can_confirm": False,
                            "selection_known": True, "cards": [card]}}


def test_the_chooser_note_says_one_choose_closes_it():
    # "about eight occurrences a run, two refusals spent on it": the seats said
    # `confirm` because the page told them to.
    #
    # `EB-779` (proofs-9 lane 1 sec.9) SETTLED WHICH PRESS THIS SCREEN TAKES,
    # which the harness could not open the game to ask when #566 landed: one
    # `choose` came back ok, the next state carried no `card_select` at all and
    # the enemy had taken the mode's damage. So the page no longer names both
    # ways out -- it names the one that is true here, and never prints the word
    # that can only be refused on this screen.
    page = blindplay.observe(_chooser_state())

    assert "One `choose` takes your answer here and closes this screen" in page
    assert "`confirm`" not in page
    # And no line about a button this screen does not have.
    assert "Confirm is" not in page


def test_the_note_still_carries_eb674s_own_sentence():
    # `EB-674`'s reading is not replaced: the chooser it was filed from is a
    # card GRID, which really does take `confirm`, and that half is untouched.
    assert "arms a pick; it does not close the screen" in CHOOSER_CONFIRM_NOTE
    assert "Say `confirm` after `choose` to take it" in CHOOSER_CONFIRM_NOTE
    # The second-`choose` fallback #566 added is gone with the question it was
    # hedging: the mode chooser takes its answer on the FIRST `choose`, so that
    # sentence was wrong about the one screen it was written for.
    assert "choose` again on the same option" not in CHOOSER_CONFIRM_NOTE


# --- the arm, held for the run ---------------------------------------------

@pytest.fixture(autouse=True)
def _forget_the_arm():
    blindplay_faces.forget_stage_arm()
    yield
    blindplay_faces.forget_stage_arm()


def _run_state(character: str = "Furina", floor: int = 4) -> dict:
    return {"player": {"character": character}, "run": {"floor": floor}}


def test_a_screen_that_cannot_answer_reads_what_the_fight_before_it_said():
    assert blindplay_faces.stage_arm(_run_state(), True) is True
    # The chooser overlay, the reward, the shop: no combat block at all.
    assert blindplay_faces.stage_arm(_run_state(), None) is True


def test_the_latch_holds_the_shipped_reading_too():
    assert blindplay_faces.stage_arm(_run_state(), False) is False
    assert blindplay_faces.stage_arm(_run_state(), None) is False


def test_another_character_is_another_run_and_is_not_answered():
    blindplay_faces.stage_arm(_run_state("Furina"), True)

    assert blindplay_faces.stage_arm(_run_state("Klee"), None) is None


def test_a_floor_that_went_backwards_is_a_run_started_since():
    blindplay_faces.stage_arm(_run_state(floor=9), True)

    assert blindplay_faces.stage_arm(_run_state(floor=2), None) is None


def test_the_glossarys_arm_reads_the_screen_first_and_the_latch_second():
    assert _stage_arm({"combat": {"stage": {"seats": []}}}) is True
    assert _stage_arm({"stage_arm": True}) is True
    assert _stage_arm({"stage_arm": False}) is False
    # Nothing has ever answered: the reading every page had before the latch.
    assert _stage_arm({}) is False


# --- `EB-728`: one Fanfare row per arm -------------------------------------

def test_the_shipped_fanfare_row_is_the_meters_and_not_the_bars():
    # The two readings are different rules for one word, and the shipped seat
    # was handed the arm's beside `METER_RULES["Fanfare"]`.
    assert "meter" in FANFARE_SHIPPED_ROW
    assert "no stage" in FANFARE_SHIPPED_ROW
    assert "A performer's own bar" not in FANFARE_SHIPPED_ROW


def _furina_obs(arm: bool) -> dict:
    return {"character": "Furina",
            "stage_arm": arm,
            "hand": [{"title": "Applause Line",
                      "text": "Gain 2 Fanfare."}]}


def test_the_fanfare_row_is_the_bars_under_the_arm_and_the_meters_off_it():
    from understudy.blindplay_notes import keyword_notes

    def row(obs):
        return next((r["text"] for r in keyword_notes(obs)
                     if r["name"] == "Fanfare"), None)

    on, off = row(_furina_obs(True)), row(_furina_obs(False))

    assert on is not None and off is not None
    assert on != off
    assert off == FANFARE_SHIPPED_ROW
    assert "performer" in on


# --- the packet's hand, numbered -------------------------------------------

def _hand_state(*names: str) -> dict:
    return {"player": {"hand": [{"name": n, "description": f"{n} does a thing."}
                                for n in names]}}


def test_two_copies_of_one_card_are_two_numbered_rows():
    hand = qa_packet._hand(_hand_state("Rising Applause", "Rising Applause",
                                       "Scene Change"), {})

    assert [c["title"] for c in hand] == ["Rising Applause (1)",
                                          "Rising Applause (2)",
                                          "Scene Change"]


def test_a_hand_of_distinct_cards_reads_the_way_it_always_did():
    hand = qa_packet._hand(_hand_state("Rising Applause", "Scene Change"), {})

    assert [c["title"] for c in hand] == ["Rising Applause", "Scene Change"]
