"""`EB-704`: `EB-674`'s confirm note prints on every chooser path.

THE FIND (Kokomi r31 lane 1, and Klee r27 lane 2 before it). The sentence
saying that a pick here is TWO commands -- `choose`, then `confirm`, with the
chooser staying up between them -- was printed on the card grid and not on
every screen that takes a pick that way. Five refusals in a row at the elite.

THE POTION CHOOSER IS A CARD GRID, and this file used to say it was
`BuildChooseCardState`'s `screen_type: "choose"`. **That reconstruction was
wrong and `EB-779` caught it** (proofs-9 lane 1 sec.9). `BuildChooseCardState`
hardwires `can_confirm: false` -- it is not a flag that arms -- and
`ExecuteConfirmSelection` refuses that screen outright with *"Choose-a-card
screen requires no confirmation"*. The chooser `EB-674` was filed from took a
`confirm` and it worked, so it was never that screen: it is one of the grid
screens `BuildCardSelectState` serialises (`simple_select` here), where
`can_confirm` really does arm with the pick. The fixture is corrected to that
shape, and the ordering it pins is unchanged: the sentence is about the SCREEN
and the `Confirm is ...` line under it is about this instant.

AND THE ONE-PRESS CHOOSER GETS THE OTHER SENTENCE (`EB-779`). One `choose`
closes `screen_type: "choose"` and resolves the pick -- read live -- so the
two-command sentence was false on it, and the `confirm` it told a seat to say
cost a refusal about eight times a run. `chooser_note` picks by the wire's own
`screen_type`, and `assert_chooser_note` now refuses BOTH directions: a grid
that offers `confirm` without the sentence, and a one-press chooser whose page
says `confirm` at all.

THE BUNDLE PICKER WAS THE PATH WITH NO NOTE. It offers `confirm` in its own
command list and printed nothing about it.

AND THE RULE IS PINNED ON THE GRAMMAR, not on the two branches: `render` now
refuses any page that offers `confirm` without the sentence, so a screen that
starts offering the verb tomorrow owes it too.
"""

from __future__ import annotations

import pytest

from understudy import blindplay
from understudy.blindplay_notes import (CHOOSER_CONFIRM_NOTE,
                                        CHOOSER_ONE_CHOICE_NOTE)
from understudy.blindplay_render import assert_chooser_note
from understudy.blindplay_shape import BlindPlayError

NOTE = "Say `confirm` after `choose` to take it"


def _card(index: int, name: str, text: str) -> dict:
    return {"index": index, "id": f"KLEEMOD-{name.upper()}", "name": name,
            "description": text, "cost": 1, "card_type": "Skill"}


def potion_chooser_state() -> dict:
    """SYNTHETIC, in `BuildCardSelectState`'s shape -- the card GRID a potion
    opens, which is the screen `EB-674` was filed from (`confirm` was refused
    as a verb, then worked once a card was armed). `can_confirm` is false here
    because nothing is picked yet, not because the screen has no button.
    `EB-779` corrected this fixture off `screen_type: "choose"`."""
    return {"state_type": "card_select",
            "player": {"character": "klee", "potions": [], "relics": [],
                       "max_potion_slots": 3},
            "card_select": {"screen_type": "simple_select",
                            "prompt": "Choose a card to make free.",
                            "can_skip": False, "can_cancel": False,
                            "preview_showing": False, "can_confirm": False,
                            "selection_known": True,
                            "cards": [_card(0, "Strike", "Deal 6 damage."),
                                      _card(1, "Defend", "Gain 5 Block.")]}}


def bundle_state() -> dict:
    """SYNTHETIC, in `BuildBundleSelectState`'s shape."""
    return {"state_type": "bundle_select",
            "player": {"character": "klee", "potions": [], "relics": [],
                       "max_potion_slots": 3},
            "bundle_select": {"prompt": "Choose a bundle.",
                              "preview_showing": False, "can_confirm": False,
                              "bundles": [
                                  {"index": 0, "card_count": 1,
                                   "cards": [_card(0, "Strike",
                                                   "Deal 6 damage.")]},
                                  {"index": 1, "card_count": 1,
                                   "cards": [_card(0, "Defend",
                                                   "Gain 5 Block.")]}]}}


# ---------------------------------------------------------------------------
# THE POTION CHOOSER
# ---------------------------------------------------------------------------

def test_the_potion_chooser_carries_the_confirm_note():
    page = blindplay.observe(potion_chooser_state())
    assert "Choose a card to make free" in page
    assert NOTE in page


def test_the_note_sits_above_the_buttons_own_state():
    """`EB-674`'s order: the sentence is about the screen, the line under it
    about this instant."""
    page = blindplay.observe(potion_chooser_state())
    assert page.index(NOTE) < page.index("Confirm is not available")


# ---------------------------------------------------------------------------
# THE BUNDLE PICKER -- THE PATH THAT HAD NONE
# ---------------------------------------------------------------------------

def test_the_bundle_picker_carries_the_confirm_note():
    page = blindplay.observe(bundle_state())
    assert NOTE in page


def test_the_bundle_picker_does_not_claim_the_button_is_dead():
    """It offers `confirm` on every render, so a `Confirm is not available`
    line would contradict its own grammar three lines down."""
    page = blindplay.observe(bundle_state())
    assert "Confirm is not available" not in page
    assert "- `confirm`" in page


# ---------------------------------------------------------------------------
# AND THE RULE, READ OFF THE GRAMMAR
# ---------------------------------------------------------------------------

def one_press_chooser_state() -> dict:
    """SYNTHETIC, in `BuildChooseCardState`'s shape -- the mode chooser. That
    builder hardwires `can_confirm: false` and the screen closes on one
    `choose` (`EB-779`, read live)."""
    state = potion_chooser_state()
    state["card_select"]["screen_type"] = "choose"
    state["card_select"]["prompt"] = "Choose one."
    return state


def test_the_one_press_chooser_never_says_confirm():
    """Seen to FAIL: this page told a seat to say `confirm` first, which is a
    refusal on a screen with no confirm button -- about eight a run."""
    page = blindplay.observe(one_press_chooser_state())
    assert "One `choose` takes your answer here and closes this screen" in page
    assert "`confirm`" not in page
    assert "Confirm is" not in page


def test_a_one_press_page_that_says_confirm_is_refused():
    with pytest.raises(BlindPlayError) as caught:
        assert_chooser_note(
            {"screen": "card_select", "select_kind": "choose",
             "commands": ['choose "<option>"']},
            "# Choose one.\n\n" + CHOOSER_ONE_CHOICE_NOTE
            + "\n\nsay `confirm` to take it\n")
    assert "no confirm button" in str(caught.value)


def test_a_one_press_page_without_its_own_sentence_is_refused():
    with pytest.raises(BlindPlayError) as caught:
        assert_chooser_note(
            {"screen": "card_select", "select_kind": "choose",
             "commands": ['choose "<option>"']},
            "# Choose one.\n")
    assert "one `choose` closes it" in str(caught.value)


def test_a_page_offering_confirm_without_the_sentence_is_refused():
    with pytest.raises(BlindPlayError) as caught:
        assert_chooser_note({"screen": "card_select", "commands": ["confirm"]},
                            "# Choose a card\n")
    assert "two commands" in str(caught.value)


def test_a_page_that_does_not_offer_confirm_is_untouched():
    assert_chooser_note({"screen": "map", "commands": ['go "<node>"']},
                        "# The map\n")


def test_the_pinned_sentence_is_the_one_the_page_prints():
    assert NOTE in CHOOSER_CONFIRM_NOTE
