"""`EB-695`: a relic's answering hit is named on the played-card path too.

THE FIND (Kokomi r30, lane 2, debrief 1). The Tamakushi Casket answers
"whenever you apply a debuff to an enemy" with a 2-damage Hydro strike from the
jellyfish. Inside a PLAN carry-out that strike is named -- "Inside the same
beat: Tamakushi Casket 2 on Damp Cultist", the clause `EB-453` built and
`EB-518` put the body on -- because `KokomiPlan.NoteRider` is standing there to
catch it. Play the same debuff card FROM HAND and the same strike lands with
nothing anywhere naming it: the seat subtracted it from HP by hand on every
such play.

THE ASYMMETRY WAS AN ACCIDENT OF WHERE THE RECEIPT LIVED. `NoteRider` files a
rider against the Plan being resolved RIGHT NOW and drops it where no Plan is
running -- correct for a Plan's own accounting, and exactly the played-card
path. So the mod keeps that half in `KleeMod.Powers.RelicAnswerLog`, on
`ReactionLog`'s shape and window, and the Casket writes there only where the
rider was NOT filed, so one strike is named once.

WHAT THIS FILE PINS is the page half on a feed shaped as the bridge sends one:
a played debuff prints `Tamakushi Casket 2` on the body, two strikes on one
body are two rows, a row from the unwatched window says so, and the states that
must not move -- a turn with no answer, and a build with no log -- print no
section at all.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a renderer.
"""

import copy

from understudy import blindplay, blindplay_board, blindplay_notes

from tier0.tests.test_understudy_blindplay import combat_state


def _answered(*rows: dict) -> dict:
    state = copy.deepcopy(combat_state())
    state["player"]["relic_answers"] = list(rows)
    return state


def _answer(target: str = "Damp Cultist", amount: int = 2,
            combat_id: str = "", carried: bool = False) -> dict:
    return {"source": "Tamakushi Casket", "amount": amount, "target": target,
            "combat_id": combat_id, "carried": carried}


def test_the_red_one_a_played_debuff_names_the_casket_on_the_body():
    """Seen to FAIL: a Slack Water played from hand moved a body by its own
    number plus 2, and no line on any screen owned the 2."""
    page = blindplay.observe(_answered(_answer()))
    assert blindplay_notes.RELIC_ANSWERS_HEADING in page
    assert "- **Tamakushi Casket** 2 on **Damp Cultist**." in page


def test_two_strikes_on_one_body_are_two_rows():
    """`EB-518`'s whole point, on this path: three entries reading `Tamakushi
    Casket 2` cannot be divided among bodies by a reader, and the beat that
    does not add up is the one that struck the same body twice."""
    page = blindplay.observe(_answered(_answer(), _answer()))
    assert page.count("- **Tamakushi Casket** 2 on **Damp Cultist**.") == 2


def test_a_strike_from_the_unwatched_window_says_so():
    """`EB-710`'s clause, on `EB-710`'s reasoning: a strike that landed after
    the player ended their turn is printed rather than dropped, and carries
    its own window because the rest of the page is about this turn."""
    page = blindplay.observe(_answered(_answer(carried=True)))
    line = next(l for l in page.splitlines() if "Tamakushi Casket" in l
                and l.startswith("- **"))
    assert line.endswith(blindplay_notes.REACTION_CARRIED_CLAUSE.strip())


def test_a_turn_with_no_answer_prints_no_section():
    """No empty line here, unlike the reaction log: that section prints one
    because a seat read its SILENCE as "may or may not have fired", and no
    such question exists about a relic nobody is holding."""
    assert blindplay_notes.RELIC_ANSWERS_HEADING not in blindplay.observe(
        _answered())


def test_a_build_with_no_log_is_byte_identical_to_what_it_was():
    assert blindplay_board.relic_answers({}) is None
    assert blindplay_notes.RELIC_ANSWERS_HEADING not in blindplay.observe(
        combat_state())


def test_a_zero_strike_is_not_a_row():
    """The number reported is the DELIVERED one, and a strike that delivered
    nothing is not a subtraction anybody is trying to account for. Both halves
    refuse it -- the mod at the note, the reader at the read."""
    assert blindplay_board.relic_answers(
        {"relic_answers": [_answer(amount=0)]}) == []


def test_the_body_is_named_the_way_the_enemy_list_names_it():
    """`EB-329`/`EB-427`: the page owns the names. A receipt naming a body one
    way while the list four lines down names it another is the mix the r11
    seat read as the numbering having shifted."""
    state = _answered(_answer())
    standing = blindplay_board._enemies(state)
    assert standing, "the recorded fixture has enemies to name against"
    row = state["player"]["relic_answers"][0]
    row["combat_id"] = str(standing[0]["combat_id"])
    row["target"] = "a stale title"

    page = blindplay.observe(state)

    assert "a stale title" not in page, (
        "a body still on the board takes the page's own name")
    assert f"on **{standing[0]['name']}**" in page


def test_the_reader_carries_the_five_keys_the_mod_sends():
    rows = blindplay_board.relic_answers({"relic_answers": [_answer()]})
    assert rows and sorted(rows[0]) == sorted(
        ["source", "amount", "target", "combat_id", "carried"])
