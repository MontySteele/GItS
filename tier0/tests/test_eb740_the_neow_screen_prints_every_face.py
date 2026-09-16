"""`EB-740`: Neow's three options, each printing what it hands over.

THE FIND (Furina, the Stage, round one, lane 1). The middle option printed

    **Lead Paperweight** — Choose 1 of 2 Colorless cards to add to your Deck.
    *this option's own words promise a card and the feed carried no face for
    it -- no rules text, no cost, no type -- so this page can offer it by name
    only*

and the seat rejected it for exactly that reason: *"It was not a choice I
made; it was a choice the screen removed from me by not printing it."*

AND THE ROW HAD ITS RULES TEXT. `EventOption.FromRelic` sets `Relic` on every
option Neow builds (`AncientEventModel.RelicOption` -> `EventModel.RelicOption`
-> `FromRelic`), so `BuildEventState` sends `relic_name` and
`relic_description` beside the option's own title and body -- and the body IS
the relic's text. What emptied `names`, and so fired `EB-393`'s note, was
`_option_faces`'s dedupe: a face whose name repeats the row's own heading is
dropped so the page does not print `Lead Paperweight` twice. Correct for the
printing; read as "the feed carried no face", it put the note on the one row
that did not need it.

The two Colorless cards themselves are rolled by the relic AFTER it is
obtained (`LeadPaperweight.AfterObtained` -> `CardFactory.CreateForReward`), so
no feed at this screen could carry them and this page no longer says it was
owed them.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a renderer.
"""

import pytest

from understudy import blindplay, blindplay_board


# The three options as `BuildEventState` sends them: `title` and `description`
# from the option, `relic_name` / `relic_description` merged in from its relic.
ARCANE_SCROLL = {
    "index": 0, "title": "Arcane Scroll",
    "description": "Obtain a random Rare card.",
    "relic_name": "Arcane Scroll",
    "relic_description": "Obtain a random Rare card.",
    "is_locked": False, "is_proceed": False, "was_chosen": False,
    "keywords": [],
}
LEAD_PAPERWEIGHT = {
    "index": 1, "title": "Lead Paperweight",
    "description": "Choose 1 of 2 Colorless cards to add to your Deck.",
    "relic_name": "Lead Paperweight",
    "relic_description": "Choose 1 of 2 Colorless cards to add to your Deck.",
    "is_locked": False, "is_proceed": False, "was_chosen": False,
    "keywords": [],
}
SILVER_CRUCIBLE = {
    "index": 2, "title": "Silver Crucible",
    "description": ("The first 3 card rewards you see are Upgraded. The first "
                    "Treasure Chest you open is empty."),
    "relic_name": "Silver Crucible",
    "relic_description": ("The first 3 card rewards you see are Upgraded. The "
                          "first Treasure Chest you open is empty."),
    "is_locked": False, "is_proceed": False, "was_chosen": False,
    "keywords": [],
}

# The Bugslayer rows `EB-393` was filed for, and the reason the note stays: a
# title, a sentence promising a named card, and no face key on the entry at all.
BUGSLAYER = {
    "index": 0, "title": "Learn Extermination Technique",
    "description": "Add Exterminate to your Deck.",
    "is_locked": False, "is_proceed": False, "was_chosen": False,
    "keywords": [],
}


def _neow(options):
    return {"state_type": "event",
            "player": {"character": "furina", "hp": 78, "max_hp": 78,
                       "gold": 99, "relics": [], "potions": [], "status": []},
            "event": {"event_id": "NEOW", "event_name": "Neow",
                      "is_ancient": True, "in_dialogue": False,
                      "body": "Neow offers you a gift.",
                      "options": list(options)}}


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


NOTE_WORDS = "the feed carried no face for it"


# ---------------------------------------------------------------------------
# THE THREE-OPTION PAGE
# ---------------------------------------------------------------------------

def test_every_neow_option_prints_its_rules_text():
    page = blindplay.observe(_neow([ARCANE_SCROLL, LEAD_PAPERWEIGHT,
                                    SILVER_CRUCIBLE]))
    assert "**Arcane Scroll**" in page
    assert "Obtain a random Rare card." in page
    assert "**Lead Paperweight**" in page
    assert "Choose 1 of 2 Colorless cards to add to your Deck." in page
    assert "**Silver Crucible**" in page
    assert "The first 3 card rewards you see are Upgraded." in page


def test_the_row_that_prints_its_text_is_not_told_it_has_none():
    """The whole find: the note fired on the one option that had printed
    everything the feed carried."""
    page = blindplay.observe(_neow([ARCANE_SCROLL, LEAD_PAPERWEIGHT,
                                    SILVER_CRUCIBLE]))
    assert NOTE_WORDS not in page


def test_the_relics_own_name_is_still_not_printed_twice():
    """`_option_faces`'s dedupe is right and stays: the heading IS the relic."""
    page = blindplay.observe(_neow([LEAD_PAPERWEIGHT]))
    assert page.count("Lead Paperweight") == 1


# ---------------------------------------------------------------------------
# AND THE ROW THE NOTE WAS WRITTEN FOR
# ---------------------------------------------------------------------------

def test_an_option_that_names_nothing_at_all_still_states_the_gap():
    page = blindplay.observe(_neow([BUGSLAYER]))
    assert NOTE_WORDS in page


def test_the_decision_is_the_raw_entry_and_not_the_printed_list():
    """Directly, because the two differ only on a row whose face repeats its
    own heading -- which is every relic option in the game."""
    assert blindplay_board._event_option(LEAD_PAPERWEIGHT)["names"] == []
    assert not blindplay_board._event_option(LEAD_PAPERWEIGHT)["note"]
    assert blindplay_board._event_option(BUGSLAYER).get("note")
