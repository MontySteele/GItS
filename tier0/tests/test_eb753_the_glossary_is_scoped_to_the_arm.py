"""`EB-753`: the glossary is scoped to the arm the run's character owns.

THE FIND (Klee r27, lane 1 and cook, fight 2 reward). The Furina Stage's
`Spend` row -- lead performer, Bow, an empty stage -- printed on a KLEE card
reward screen. R270 made Spark a currency and Klee's sinks print the word
"Spend", so the Stage's keyword pattern fired on ordinary prose and the seat
was handed a rule about three performers on a screen with no performers and no
way to get one.

TWO GATES, AND THEY ARE NOT THE SAME RULE.

`_ARM_KEYWORD_CHARACTER` (`EB-504` / `EB-583`) covers `Hexerei` and `Oz`:
words printed BY faces every run can draft, so the word really is on the
screen and the reader is owed the sentence saying it is inert here.

`_ARM_KEYWORD_ARM` (this row) covers the words a KIT owns. `Spend`, `Bow`,
`Raise`, `Rotate`, `Mine`, `Plan`, `Mend` are ordinary English that another
kit's prose says for its own reasons; a match off the owning run is a FALSE
POSITIVE, and a false positive owes no entry at all -- there is nothing to say
"is inert here" about.

A FEED THAT DOES NOT NAME THE CHARACTER GETS EVERY ROW, which is `EB-504`'s
own direction: silence about the character is not evidence it is somebody
else's.
"""

from __future__ import annotations

import pytest

from understudy import blindplay, blindplay_notes


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


#: One word per kit, each the kit's own and each a word another kit's prose can
#: say by accident -- which is the whole find.
OWNED = {"klee": ("Spark", "Bomb", "Mine"),
         "kokomi": ("Plan", "Dusk", "Mend"),
         # The text pass (2026-09-25) retired `Rotate`; the front seat's
         # word is the third Stage word here now.
         "furina": ("Spend", "Bow", "front performer")}

#: The face that says every one of them at once, so one screen answers the
#: whole acceptance in both directions.
EVERY_WORD = ("Spend 2 Sparks to place a Bomb and a Mine, then give the "
              "front performer Fanfare, take a Bow, Mend 3 and write a Plan "
              "at Dusk.")


def _reward(character: str, text: str = EVERY_WORD) -> str:
    """A card-reward screen for one character, offering one card."""
    return blindplay.observe({
        "state_type": "card_reward",
        "player": {"character": character, "potions": [], "relics": [],
                   "max_potion_slots": 3},
        "card_reward": {"prompt": "Add a card to your deck.",
                        "can_skip": True,
                        "cards": [{"index": 0, "id": "KLEEMOD-X",
                                   "name": "Some Card", "cost": "1",
                                   "card_type": "Skill",
                                   "description": text}]}})


def _rows(page: str) -> set[str]:
    if "## Words on this screen" not in page:
        return set()
    block = page.split("## Words on this screen", 1)[1].split("\n## ", 1)[0]
    return {line.split("**")[1] for line in block.splitlines()
            if line.startswith("- **")}


# ---------------------------------------------------------------------------
# THE FIND
# ---------------------------------------------------------------------------

def test_the_stage_spend_row_does_not_print_on_a_klee_screen():
    page = _reward("Klee", "Spend 2 Sparks: deal 13 damage instead.")
    assert "**Spend**" not in page
    assert "front performer" not in page
    # and the word it is really about is still defined
    assert "**Spark**" in page


# ---------------------------------------------------------------------------
# AND THE ACCEPTANCE, BOTH DIRECTIONS, ONE SCREEN PER KIT
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("character", sorted(OWNED))
def test_a_run_reads_its_own_kits_words(character):
    rows = _rows(_reward(character))
    for word in OWNED[character]:
        assert word in rows, word


@pytest.mark.parametrize("character", sorted(OWNED))
def test_a_run_reads_no_other_kits_words(character):
    rows = _rows(_reward(character))
    for other, words in OWNED.items():
        if other == character:
            continue
        assert not rows & set(words), (character, other, rows & set(words))


def test_the_universal_words_are_scoped_to_nobody():
    """`Companion`, `Swirl`, `Grounded` and `Oz` ride faces the whole roster
    drafts, so none of them is owned and each keeps the treatment it already
    had. (`Hexerei` was the fifth until R276 pick 2 retired it.)"""
    for word in ("Companion", "Swirl", "Grounded", "Oz"):
        assert word not in blindplay_notes._ARM_KEYWORD_ARM, word


def test_oz_still_prints_its_off_arm_sentence_on_another_run():
    """`EB-583` is untouched: that word IS on a face this run can draft, so
    the row says it is inert here rather than vanishing."""
    page = _reward("Kokomi", "Deal 7 damage. If Oz is out, he deals 5 more.")
    assert "**Oz**" in page
    assert "the clause never fires" in page


def test_the_retired_hexerei_word_has_no_row():
    """R276 pick 2: the word is on no face, so a stale feed that still prints
    it gets no definition of a rule that no longer exists."""
    page = _reward("Klee", "A Hexerei card. Deal 6 damage.")
    assert "**Hexerei**" not in page


def test_a_feed_that_does_not_name_the_character_gets_every_row():
    rows = _rows(_reward(""))
    for words in OWNED.values():
        assert set(words) <= rows, words


# ---------------------------------------------------------------------------
# THE TABLE ITSELF
# ---------------------------------------------------------------------------

def test_every_owned_word_is_a_word_the_glossary_can_raise():
    """A row here that matches no pattern would be a dead entry, and a typo in
    one would scope nothing."""
    for word in blindplay_notes._ARM_KEYWORD_ARM:
        assert (word in blindplay_notes._ARM_KEYWORD_RE
                or word in blindplay_notes.ARM_KEYWORDS), word


def test_every_owner_is_a_character_on_the_roster():
    assert set(blindplay_notes._ARM_KEYWORD_ARM.values()) == {
        "klee", "kokomi", "furina"}
