"""`EB-710`: an end-of-turn reaction is still named on the next player page.

THE FIND. "What reacted this turn" said *Nothing reacted this turn* through a
run where Electro-Charged fired six times off Shinobu's Sanctifying Ring -- a
power that fires AT THE END OF YOUR TURN -- and Klee r26 read the header EMPTY
on two Melts and an Overloaded off a played Set off.

THE LOG WAS CLEARED ON THE WRONG WINDOW. `ReactionLog.MarkTurnStart` is called
from `ElementalApplication.AfterSideTurnEnd(Enemy)`, which is the opening of
the player's NEXT turn, and it used to be a straight `Rows.Clear()`. So every
reaction between the player's last action and that moment -- their own
end-of-turn tenants (`CompanionOverhaulTurnEnd` fires the Ring's volley in
`AfterSideTurnEnd(Player)`), then the whole enemy side -- was written into a
list that was emptied before any page could render it. No page ever existed on
which those rows could have printed.

THE FIX IS A MARK AND A SLICE. `ReactionLog.MarkPlayerTurnEnd` is taken in
`KleeElementalHooks.BeforeSideTurnEnd(Player)`, which is earlier than every
end-of-turn tenant that deals an element, and `MarkTurnStart` now keeps the
rows past that mark -- flagged `carried` -- and drops the rest. A carried row
sits BEFORE the next turn's mark, so it is dropped in its turn: a row prints
once and a long enemy side cannot pile up.

WHAT THIS FILE PINS is the page half, on a feed shaped exactly as the bridge
now sends one: an end-of-turn Electro hit is named on the next screen, it says
which window it came from, a turn that also has live reactions prints both
kinds, and the two states that must not move (a turn of ordinary rows, and a
present-and-empty log) are byte-identical to what they were. The C# half's own
pin is `klee-mod/KleeTests/ReactionLogWindowTests.cs`.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a renderer.
"""

import copy

import pytest

from understudy import blindplay, blindplay_board, blindplay_notes

from tier0.tests.test_understudy_blindplay import combat_state


def _reacted(*rows: dict) -> dict:
    state = copy.deepcopy(combat_state())
    state["player"]["reactions"] = list(rows)
    return state


#: The r26/r31 beat: the Ring's volley puts Electro on a body already carrying
#: Hydro, at the end of the player's turn, and the row reaches the page one
#: turn later because nothing rendered a page in between.
RING = {"reaction": "Electro-Charged", "source": "Kuki Shinobu — Sanctifying "
        "Ring", "target": "Damp Cultist", "combat_id": "3", "carried": True}
#: An ordinary row from the turn in front of the reader.
PLAYED = {"reaction": "Overloaded", "source": "Set off",
          "target": "Damp Cultist", "combat_id": "3", "carried": False}


def test_the_red_one_an_end_of_turn_reaction_is_named_on_the_next_page():
    """Seen to FAIL before the mod carried the row: the log was emptied at the
    top of this turn and the page printed `Nothing reacted this turn` over a
    board where Electro-Charged had just fired."""
    page = blindplay.observe(_reacted(RING))
    assert blindplay_notes.REACTIONS_HEADING in page
    assert "**Electro-Charged**" in page
    assert "Sanctifying Ring" in page
    assert "Nothing reacted this turn. A reaction" not in page, (
        "the empty line is the false one here -- something reacted")


def test_a_carried_row_says_which_window_it_came_from():
    """The heading names THIS turn. A row from before it prints its own
    window, or the heading becomes the second false thing on the screen."""
    page = blindplay.observe(_reacted(RING))
    assert blindplay_notes.REACTION_CARRIED_CLAUSE.strip() in page
    line = next(l for l in page.splitlines() if "Electro-Charged**" in l
                and l.startswith("- **"))
    assert line.endswith(blindplay_notes.REACTION_CARRIED_CLAUSE.strip())


def test_a_page_whose_rows_are_all_carried_says_both_facts():
    page = blindplay.observe(_reacted(RING))
    assert blindplay_notes.REACTION_CARRIED_ONLY in page
    # And it stands ABOVE the rows it introduces.
    assert page.index(blindplay_notes.REACTION_CARRIED_ONLY) < page.index(
        "Sanctifying Ring")


def test_a_live_row_beside_a_carried_one_is_not_marked():
    """Both kinds on one screen, each under its own window, in the order the
    mod sends them -- the carried half first, because it resolved first."""
    page = blindplay.observe(_reacted(RING, PLAYED))
    assert blindplay_notes.REACTION_CARRIED_ONLY not in page, (
        "not every row is carried here")
    carried = next(l for l in page.splitlines() if "Sanctifying Ring" in l)
    live = next(l for l in page.splitlines() if "off Set off" in l)
    assert carried.endswith(blindplay_notes.REACTION_CARRIED_CLAUSE.strip())
    assert not live.endswith(blindplay_notes.REACTION_CARRIED_CLAUSE.strip())
    assert page.index(carried) < page.index(live)


def test_an_ordinary_turn_is_byte_identical_to_what_it_was():
    """The half that must not move. A feed of live rows prints the rows it
    always printed, with no new clause anywhere."""
    page = blindplay.observe(_reacted(PLAYED))
    assert "- **Overloaded** on **Damp Cultist**, off Set off." in page
    assert blindplay_notes.REACTION_CARRIED_CLAUSE.strip() not in page
    assert blindplay_notes.REACTION_CARRIED_ONLY not in page


def test_an_empty_log_still_says_nothing_reacted():
    """The present-and-empty state is untouched: it is still the sentence that
    closes `EB-681`'s lane-1 finding, and it is now the honest one, because a
    carried row would have made the list non-empty."""
    page = blindplay.observe(_reacted())
    assert blindplay_notes.NO_REACTION_THIS_TURN in page
    assert blindplay_notes.REACTION_CARRIED_ONLY not in page


def test_a_bridge_that_sends_no_carried_key_reads_as_not_carried():
    """ABSENT IS FALSE. A feed from a build without the mod-side carry sends
    rows with no `carried` key, and those are rows from this turn."""
    rows = blindplay_board.reaction_log(
        {"reactions": [{"reaction": "Melt", "source": "Sparks 'n' Splash",
                        "target": "Cultist", "combat_id": "1"}]})
    assert rows == [{"reaction": "Melt", "source": "Sparks 'n' Splash",
                     "target": "Cultist", "combat_id": "1", "carried": False}]


def test_the_board_reader_carries_the_flag_through():
    rows = blindplay_board.reaction_log({"reactions": [dict(RING)]})
    assert rows and rows[0]["carried"] is True


def test_a_build_with_no_log_still_prints_no_section():
    """The wire's third state, unchanged by any of this."""
    assert blindplay_notes.REACTIONS_HEADING not in blindplay.observe(
        combat_state())
