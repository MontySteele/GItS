"""The funnel's fixed shapes: the four questions, the refusals, the dials.

Cut out of `staged_turn.py` by `EB-180`. Every name here is the one
that file declared, at the value it declared, and `staged_turn.py`
re-exports all of them -- so `staged_turn.QUESTIONS` and
`staged_turn.DOMINANCE_GAP` still resolve. It sits at the BOTTOM of
the seam stack: it imports nothing from this package.

`QA_DIR` and `LEDGER` are NOT here. They stay on `staged_turn.py`,
because they are what a caller reaches in and swaps, and a seam that
bound its own copy at import would never see the swap.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from understudy import face_defects


REPO = Path(__file__).resolve().parents[1]
TURN_DIR = Path(__file__).resolve().parent / "turns"
# EB-202's slot registration, which lives beside a round's boards and is NOT a
# board. The name is repeated here rather than imported because
# `understudy/slot_plan.py` READS THE CARD SHEETS, and this module builds the
# blind packet: a sheet reader may not be in scope where the packet is built,
# which is the same rule `resource_order` states about itself and
# `local_tester._post_read` keeps. `cmd_check` imports `slot_plan` lazily.
# `test_the_slot_file_name_is_the_same_string_in_both_modules` pins the pair.
SLOT_FILE_NAME = "slots.yaml"

# ---------------------------------------------------------------------------
# THE ONE PROVISIONAL CONSTANT (R212 derived-not-picked; disclosed in every
# packet, pinned by `test_dominance_gap_is_the_pilots_own_doubling`).
#
# `closeness` reports gap = (best - runner_up) / best, in the pilot's own
# scoring currency. DOMINANCE_GAP is the gap above which the turn is refused
# as "one line overwhelmingly dominates".
#
# DERIVED, not chosen. 0.5 is exactly the point where best > 2 x runner_up:
# the winning line is worth more than two of the next-best line put together.
# That boundary is the pilot's own, not one invented here -- `make_pilot`
# already treats its score as a value scale with a hard floor at zero
# (`if best_score <= 0: return None`), so "twice the runner-up" is a statement
# in the units the surface already defines rather than a number laid on top
# of it.
#
# THE ERROR DIRECTION IS ONE-WAY, which is the R212 condition. A 2x gap in the
# pilot's own currency is enormous; a threshold this high can only ever
# UNDER-refuse, letting a merely-lopsided turn through to the next filter --
# which is the four-question form, and then [USER]. It cannot refuse a turn
# that was genuinely close. A constant whose only failure mode is "the funnel
# does less work" is a constant that cannot corrupt a verdict.
#
# ALTERNATIVES CONSIDERED AND RECORDED RATHER THAN ASKED (R212):
#   * an ABSOLUTE gap in score points (e.g. "6, one basic card's worth of
#     output"). Rejected: the score scale is not stable across characters or
#     board sizes -- `_score` sums weighted damage, block, scaling and tempo,
#     so six points means something different on a two-enemy board than on a
#     one-enemy board, and a falsifier whose threshold drifts with the board
#     is a falsifier that refuses different things on different turns.
#   * the pilot's `cost` weight, 0.1 per energy in `pilots/generic.yaml`.
#     Rejected: that is the surface's TIE-BREAK resolution -- the smallest
#     difference it can express -- and the smallest expressible difference is
#     the opposite of a dominance threshold.
DOMINANCE_GAP = 0.5

# A compute bound, not a design number: `closeness` refuses rather than
# truncates when a hand's line space is bigger than this. Truncating would
# make the reported gap depend on which lines happened to be enumerated
# first, and a falsifier whose answer depends on iteration order is not one.
MAX_LINES = 20_000

# The weighting R213's second guard asks for, made concrete and simple.
# A grader whose answer to QUESTION TWO disagrees with [USER]'s on at least
# WEIGHT_DISAGREE of the last WEIGHT_WINDOW turns they both played loses its
# power to mark a turn SURVIVES ALONE: the verdict still says SURVIVES, and
# `survives_alone` goes false, so the turn needs [USER]'s own form before it
# counts as having passed step two. Question two is the one weighted because
# it is the one R213 names as the slice's readiness test.
WEIGHT_WINDOW = 5
WEIGHT_DISAGREE = 3

# The grader identity R213 reserves for [USER]'s own cold play. One spelling,
# so a ledger row cannot be a comparison against somebody else's form.
USER_GRADER = "user"

# The four questions, in the form's own field names. Verbatim from R213's
# "Play form" paragraph; `qa_form.md` prints the same four and
# `test_the_form_questions_are_r213s_verbatim` pins that the two agree.
QUESTIONS: dict[str, str] = {
    "q1_what_did_you_play": "What did you play?",
    "q2_other_line_considered": "What other line did you seriously consider?",
    "q3_what_it_gave_up": "What did your chosen line give up?",
    "q4_different_intent": "Would a different enemy intent have changed it?",
}

# Every way this funnel refuses a turn, as data, so a verdict can name the
# rule that refused it and a reader never has to grep for the sentence.
FALSIFIERS: dict[str, str] = {
    "packet_mismatch":
        "the form was answered against a different packet than the one on "
        "disk for this turn",
    "grader_is_designer":
        "the grader declared it designed these cards; R213's first guard is "
        "that the QA agent is never the designer of the cards it reads",
    "incomplete_form":
        "one of the four answers is missing, so the form cannot be read",
    "empty_line":
        "the form names no cards played, so there is no turn to read",
    "no_second_line":
        "question two has no answer: no other line was seriously considered, "
        "which is R213's readiness test and the slice fails it",
    "intent_insensitive":
        "question four is no: a different enemy intent would not have "
        "changed the line, so the intent is not part of the decision",
    # `EB-236` item (d), the staged twin of `EB-229`. A board that REGISTERED
    # pre-commit questions and got a form with no answers to them has not
    # been read the way it was registered: the forecast is the one answer
    # that has to be written before the line, and a form that skips it is
    # answering a different board. Absent on every board that asks nothing.
    "forecast_missing":
        "the board registered questions to be answered BEFORE the line and "
        "the form carries no answer, or fewer answers than questions -- a "
        "forecast collected after the line is a rationalisation",
    # EB-203. A card that aims at one enemy, played at nobody. Checked BEFORE
    # every rule that reads the reader's prose, because a line the bridge
    # cannot play is not a reading that failed -- it is a reading that was
    # never tested, and KLEESPARK-R1 sealed two of eight in that state. The
    # derivation is the card sheet (`understudy/targeting.py`); the packet
    # carries no targeting field.
    "target_missing":
        "a play names a card whose printed effects aim at ONE enemy and "
        "carries no target, so the line cannot be replayed at all",
    "board_mismatch":
        "the live board is not the board the packet showed, so replaying the "
        "graded line would be playing a different turn",
    "line_dominates":
        "the decision-closeness falsifier reads one line as overwhelmingly "
        "dominating the next best",
    # EB-170. A replay refusal, not a grading one: the line passes through a
    # modal prompt and neither the form nor the operator said what to pick.
    # `execute` STOPS here rather than guessing, because a heuristic pick is a
    # replay of a line nobody played -- and a replay of the wrong line looks
    # exactly like a replay of the right one in the post-state.
    "modal_unanswered":
        "the line reached a modal prompt the form did not answer, and a "
        "replayer that guessed would be replaying a line nobody played",
    # EB-169. The one rule here that refuses a BOARD rather than a FORM, and
    # the only one that fires before a game is launched. It is in this table
    # anyway, because the table's promise is that every refusal this funnel
    # can make is data a reader can find without grepping for a sentence.
    face_defects.RULE: face_defects.WHY,
}

# EB-170. THE TWO MODAL PROMPTS A LINE CAN PASS THROUGH, and the form key that
# answers each. The atlas's warning that "`card_select` is three screens
# wearing one name" is why the mapping is on the SCREEN TYPE the wire reports
# and not on anything guessed from what is on the screen:
#
#   `hand_select`  -- the hand itself enters select mode; no screen is built
#                     (`NPlayerHand.SelectCards`). This is Kokomi's "which card
#                     gets Exhausted", so the form key is `exhaust` and its
#                     value is a card's PRINTED TITLE.
#   `card_select`  -- a built screen offering faces that are not hand cards
#                     (`NChooseACardSelectionScreen`). This is a choose-one
#                     card's MODES, so the form key is `choose` and its value
#                     is the option's own PRINTED TEXT, which for the slice's
#                     either-faces is a whole sentence ("Deal 14 damage").
#
# Both keys are optional and nullable on every play: a line that passes through
# no prompt says nothing, and a form written before these keys existed loads
# and replays exactly as it did.
MODAL_KEY_FOR_SCREEN: dict[str, str] = {
    "hand_select": "exhaust",
    "card_select": "choose",
}
MODAL_KEYS: tuple[str, ...] = tuple(MODAL_KEY_FOR_SCREEN.values())

# A bound, not a design number: how many prompts one play may raise before the
# replayer calls it a loop. Three is well past anything the roster prints (a
# mode choice followed by that mode's own selection is two) and a replayer that
# span forever on a screen it kept failing to close would hang an attended
# session with the game up.
MAX_MODALS_PER_PLAY = 3

# What "no answer" looks like when a grader writes prose instead of leaving a
# field empty. Deliberately narrow: a long answer that happens to open with
# "no" is a real answer, and only a short flat refusal is read as one.
_NEGATIVE_WORDS = {"no", "none", "nothing", "nope", "n/a", "na", "-", "--"}
_NEGATIVE_PHRASES = {
    "no other line", "none seriously", "there was none", "nothing else",
    "no second line", "not really", "no it would not", "no it wouldn't",
    "there is no other line", "i did not consider another line",
}

def _norm(text: Any) -> str:
    return " ".join(str(text or "").strip().lower().split()).strip(" .!?,;:")


def is_negative(text: Any) -> bool:
    """"No", "none", "nothing else" -- an answer that is the absence of one.

    Narrow on purpose. A long answer that opens with "no" is an answer ("no
    line beat it, but I weighed X against Y"), and reading it as a refusal
    would falsify a turn that passed. Only a flat short negative counts.
    """
    n = _norm(text)
    if not n:
        return True
    if n in _NEGATIVE_WORDS or n in _NEGATIVE_PHRASES:
        return True
    words = n.split()
    return words[0] in _NEGATIVE_WORDS and len(words) <= 3
