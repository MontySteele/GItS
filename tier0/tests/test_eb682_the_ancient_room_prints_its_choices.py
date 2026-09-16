"""`EB-682`: the Ancient room prints the choices it is offering.

THE FIND (Kokomi r27 lane 1, and again in r32's Pael room). The act-2 Ancient
room, Tezcatara, printed a heading, then the "this room prints no Proceed and
this page has no verb that leaves one" note, and nothing between them:

    "I typed `choose 1` on a guess and it silently worked, handing me Very Hot
    Cocoa (+4 energy every combat, the single biggest item of the run). Had I
    trusted the screen I would have called it a stuck room and stopped the
    round. That is the most serious defect I hit."

THE ROOM HAD THREE OPTIONS. `Tezcatara.GenerateInitialOptions` rolls one relic
from each of its three pools (decompiled: Very Hot Cocoa or Yummy Cookie, then
one of Biiig Hug / Storybook / Toasty Mittens, then one of Golden Compass /
Pumpkin Candle / Toy Box / Seal of Gold, plus Nutritious Soup where the deck
still holds a basic Strike). What was empty was the bridge's read, not the
room: `BuildEventState` enumerated `NEventOptionButton` under the live scene,
and an Ancient layout animates its buttons in after its dialogue
(`NAncientEventLayout.AnimateButtonsIn`), so a state read taken before that
answers none -- while `EventModel.CurrentOptions` is the list the room is
offering and the list those buttons are built FROM.

So the bridge falls back to the model's own list, ONLY where the UI read found
nothing, marking each row `from_model`. The page needs no new renderer: an
Ancient room is an `EventRoom`, its screen is `state_type: "event"`, and the
rows print the way every event's rows print -- which is what this file pins,
on a Tezcatara-shaped feed.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a renderer.
"""

import pytest

from understudy import blindplay, blindplay_board


def _relic_option(index, name, text, from_model=True):
    """One Tezcatara row as the bridge now sends it: the option's own title
    and body, the relic's face merged in, and the mark saying the row was read
    off the model because no button answered."""
    row = {"index": index, "title": name, "description": text,
           "relic_name": name, "relic_description": text,
           "is_locked": False, "is_proceed": False, "was_chosen": False,
           "keywords": []}
    if from_model:
        row["from_model"] = True
    return row


VERY_HOT_COCOA = _relic_option(
    0, "Very Hot Cocoa",
    "At the start of each combat, gain an additional 4 Energy.")
STORYBOOK = _relic_option(
    1, "Storybook", "Whenever you add a card to your deck, gain 15 Gold.")
GOLDEN_COMPASS = _relic_option(
    2, "Golden Compass", "You may always see where each path leads.")

TEZCATARA = [VERY_HOT_COCOA, STORYBOOK, GOLDEN_COMPASS]


def _ancient(options):
    return {"state_type": "event",
            "player": {"character": "kokomi", "hp": 54, "max_hp": 80,
                       "gold": 212, "relics": [], "potions": [],
                       "status": []},
            "event": {"event_id": "TEZCATARA", "event_name": "Tezcatara",
                      "is_ancient": True, "in_dialogue": False,
                      "body": "The ancient regards you.",
                      "options": list(options)}}


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


NO_PROCEED = "This room prints no Proceed"


# ---------------------------------------------------------------------------
# THE ROOM THE SEAT WOULD HAVE CALLED STUCK
# ---------------------------------------------------------------------------

def test_the_ancient_rooms_three_choices_are_printed():
    page = blindplay.observe(_ancient(TEZCATARA))
    assert "**Very Hot Cocoa**" in page
    assert "**Storybook**" in page
    assert "**Golden Compass**" in page


def test_each_choice_prints_what_it_hands_over():
    page = blindplay.observe(_ancient(TEZCATARA))
    assert "At the start of each combat, gain an additional 4 Energy." in page
    assert "Whenever you add a card to your deck, gain 15 Gold." in page
    assert "You may always see where each path leads." in page


def test_the_rows_keep_the_order_choose_indexes_into():
    """`choose 1` was the seat's guess, and it paid Very Hot Cocoa. The
    fallback preserves the model's order, which is the order the buttons
    `ExecuteChooseEventOption` indexes are built in, so the same verb is a
    reading now."""
    page = blindplay.observe(_ancient(TEZCATARA))
    rows = [line for line in page.splitlines() if line.startswith("- **")]
    assert rows[0] == "- **Very Hot Cocoa**"
    assert rows[1] == "- **Storybook**"
    assert rows[2] == "- **Golden Compass**"
    assert 'choose "<option>"' in page


def test_the_no_proceed_note_still_stands_beside_the_rows():
    """`EB-393`'s note is right about this room -- there is no Proceed -- and
    what made it read as a dead end was the empty list above it."""
    page = blindplay.observe(_ancient(TEZCATARA))
    assert NO_PROCEED in page


def test_a_row_read_off_the_model_prints_like_any_other():
    """`from_model` is a diagnosis for a reader of the feed, not a caveat on
    the page: the rows are the same rows, read one layer down."""
    live = blindplay_board._event_option(
        _relic_option(0, "Very Hot Cocoa", "Gain 4 Energy.", from_model=False))
    modelled = blindplay_board._event_option(
        _relic_option(0, "Very Hot Cocoa", "Gain 4 Energy.", from_model=True))
    assert live == modelled


# ---------------------------------------------------------------------------
# AND THE ROOM THAT REALLY IS OFFERING NOTHING
# ---------------------------------------------------------------------------

def test_an_event_with_no_options_is_unchanged():
    page = blindplay.observe(_ancient([]))
    assert "Tezcatara" in page
    assert NO_PROCEED in page
