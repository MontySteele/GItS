"""EB-149 (R213 process step 2): the BLIND QA funnel for one staged turn.

    python -m understudy.staged_turn check     understudy/turns/<t>.yaml
    python -m understudy.staged_turn closeness understudy/turns/<t>.yaml
    python -m understudy.staged_turn stage     understudy/turns/<t>.yaml --why "..."
    python -m understudy.staged_turn stage     understudy/turns/<t>.yaml --hold --why "..."
    python -m understudy.staged_turn grade     <turn-id> <form.json>
    python -m understudy.staged_turn execute   <turn-id> <form.json> --why "..."
    python -m understudy.staged_turn execute   <turn-id> <form.json> --why "..." \
        --answer "<prompt>=<printed choice>"
    python -m understudy.staged_turn ledger

WHAT THIS IS, IN ONE PARAGRAPH
------------------------------
R213 accepted a four-step funnel and this file is step two. A STAGED TURN is a
board set up by hand in the real game from a YAML file. A BLIND GRADER -- an
LLM agent with no repo access, or [USER] playing the same board cold -- sees
only the printed truth of that board and answers four questions: what did you
play, what other line did you seriously consider, what did your chosen line
give up, would a different enemy intent have changed it. THE FORM IS A
FALSIFIER AND NOT A SCORE. A turn whose second question has no answer, or whose
fourth is "no", is REFUSED and never reaches [USER]. Nothing in this file rates
a turn, ranks a turn, or says a turn is good; there is no verdict here but
REFUSED and SURVIVES, and SURVIVES means only "not yet falsified".

THE ONE NUMBER, AND THE ONE PLACE IT IS QUOTABLE (R213 F, R215 B)
-----------------------------------------------------------------
`closeness` reads the staged board into a tier0 `CombatState`, enumerates the
plausible lines, scores each with the PILOT'S OWN `_score` surface, and reports
the gap between the best two. It exists to refuse a turn where one line
overwhelmingly dominates. It is not evidence that a decision is fun, it is not
a balance reading, and it may not be compared across turns.

R215 B put the exception in LAW in as many words: no number measured on a
prototype row is quotable, EXCEPT the decision-closeness falsifier, because
the falsifier reads the TURN and not the row. Every verdict this file writes
carries that sentence, so a number lifted out of one arrives with its licence.

WHY THE PACKET IS A SEPARATE MODULE
-----------------------------------
`qa_packet.py` builds the blind packet and imports nothing from `tier0` -- not
the sheet loaders, not the engine, not the pilot. THIS file imports all three,
because the falsifier needs them. Keeping them apart is what makes "the agent
sees no design context" a structural fact rather than a promise: the code that
writes the packet cannot open a sheet, and an AST walk in
`tier0/tests/test_staged_turn.py` says so.

ATTENDED ONLY, LIKE EVERY OTHER STAGED THING
---------------------------------------------
This module grants cards and writes a board, so it sits on `scenario.py`'s side
of the line and `soak.py` does not import it -- pinned structurally, the same
way `test_understudy_scenario` pins the scenario harness's absence. It reaches
a fight through `soak.run_scripted`, the same setup / policy-swap / teardown
dance every attended instrument uses; nothing about the embark is reimplemented
here.

THE FILE FORMAT
---------------
YAML, under `understudy/turns/`. Two halves that describe the same board, and
the parser refuses a file where they disagree:

    id: kokomi-first-turn-example
    character: KLEEMOD-KOKOMI
    exact_hand: true               # EB-165: empty the dealt hand first
    assumptions: ["..."]
    staging:                       # scenario SETUP verbs, run against the game
      - give: {card: KLEEMOD-PEARL_BARRAGE, pile: hand}
      - set_energy: 3
    board:                         # the tier0 mirror, read ONLY by `closeness`
      character: kokomi
      pilot: generic
      hp: 62
      hand: [pearl_barrage, coral_guard]
      enemies:
        - {name: "Jaw Worm", hp: 32, intent: {kind: attack, amount: 11}}

`exact_hand: true` (EB-165) is how a turn asks for the hand it declared and no
other. The game deals its own opening hand on top of the granted one, so
without it a five-card turn stages with ten; with it, `stage` runs the bridge's
`clear_hand` op BEFORE the first grant -- the cards go to the bottom of the
draw pile through the pile move that sits underneath discard and exhaust, so no
trigger fires -- and `export_packet` REFUSES to write a packet whose live hand
is not the declared multiset.

REPLAYING A LINE THROUGH A MODAL PROMPT (EB-170)
------------------------------------------------
A card can stop the turn and ask a question: WHICH card gets Exhausted
(`hand_select`), or WHICH half of a "Choose one" face resolves (`card_select`).
Round 3 of the Kokomi slice met three of those and the replayer walked into the
next play, which reported `no enemy 'Twig Slime (S)'; the fight has []` -- a
true sentence about a card-selection screen and a useless one. So a play's
entry in `chosen_line` may carry two optional keys, both in the grader's own
printed vocabulary:

    {"card": "Tidal Barrage", "target": "Nibbit", "exhaust": "Send the Runner"}
    {"card": "Itto - Oni Rush", "choose": "Deal 14 damage"}

`execute` answers the prompt from them. When a prompt appears and NOBODY said
what to pick, it STOPS with `modal_unanswered`, naming the prompt and listing
what was on the table -- never a heuristic pick, because the first offer, the
biggest number and the cheapest card are all plausible guesses and all three
produce a post-state indistinguishable from a real replay. `--answer
"<prompt>=<printed choice>"` is the OPERATOR's answer for a form written before
these keys existed, read off the grader's own q1 prose; it is logged as
`source: "operator"` on the row and in the record, and it never overrides an
answer the form itself carries.

`staging` may not contain `play`, `end_turn` or `expect`: a staged turn is a
BOARD, and the line is the grader's answer, not the file's. The two halves are
checked against each other by `scenario.card_key`, so a card added to the hand
in one half and forgotten in the other is a parse error and not a falsifier
reading taken on a board nobody staged.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import yaml

from understudy import bridge, face_defects, qa_packet, scenario

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
# COMMITTED, unlike `understudy/logs/`. A packet is the artifact the funnel
# exists to produce and a verdict is the record of a refusal; both are prose
# about one hand-set board and neither is a measurement, so they belong in the
# tree where a later reader can find the turn a verdict refused.
QA_DIR = REPO / "review" / "qa"
LEDGER = QA_DIR / "ledger.tsv"

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


class TurnError(RuntimeError):
    """A turn file that cannot be used: a bad key, two halves that disagree."""


class FormError(RuntimeError):
    """A form file that is not a form: missing fields, wrong shape."""


# ------------------------------------------------------------------ parse ---

@dataclass
class Board:
    """The tier0 mirror of the staged board. Read by `closeness` and nothing
    else -- never by the packet, which reads the LIVE game and only the live
    game."""
    character: str
    hand: list[str]
    enemies: list[dict[str, Any]]
    pilot: str = "generic"
    hp: int = 70
    max_hp: int = 70
    block: int = 0
    energy: int = 3
    turn: int = 1
    resources: dict[str, int] = field(default_factory=dict)


@dataclass
class StagedTurn:
    id: str
    character: str
    staging: list[tuple[str, Any]]
    board: Board
    path: Path | None = None
    seed: str | None = None
    notes: str = ""
    assumptions: list[str] = field(default_factory=list)
    # MIRRORS `scenario.Scenario.prototype` (EB-147), and is the same
    # declaration for the same reason one file over: this turn names cards on
    # the QUARANTINED prototype surface (R213 B), which is deliberately
    # outside `loader._card_index()`, so the tooling has to be TOLD rather
    # than have its resolvers loosened for every turn. It is an explicit
    # DEV-ROUTE DECLARATION: with it, `closeness` also resolves ids through
    # `loader.prototype_cards()`; without it, a `proto_` id is refused by
    # name rather than quietly read as unrepresentable. The reading it
    # produces is still a falsifier of the TURN, which is R215 B's one
    # exception to the prototype no-quote clause.
    prototype: bool = False
    # EB-165. THE GAME DEALS ITS OWN OPENING HAND ON TOP OF THE GRANTED ONE, so
    # a turn that declares five cards is staged with ten and the blind grader
    # reads a board nobody designed. With `exact_hand: true` the staging opens
    # with the bridge's `clear_hand` op -- BEFORE the first grant, because a
    # clear after them would take the declared cards too -- and `export_packet`
    # REFUSES to write a packet whose live hand is not the declared multiset.
    # Default False, so every turn written before this door existed still
    # stages exactly as it did.
    exact_hand: bool = False
    # R221 B. THE REGISTERED SLOTS THIS BOARD IS EVIDENCE ABOUT. Sequential
    # stopping is a rule about SLOTS, not about turns: "run the rest only if
    # they carry an undecided slot" needs a board to say which slots it
    # carries, and a board that says nothing carries exactly one -- itself.
    # Declared on the turn file rather than derived, because a derived slot
    # map would be a map chosen after the boards were written, which is the
    # forking path the rule exists to close.
    slots: list[str] = field(default_factory=list)
    # EB-236. THE BOARD'S OWN DECLARATION OF ITS RESOURCE QUESTION -- an
    # `slot_plan.ResourceRound`, or None where the file declares none, which
    # is legal and is what every board committed before this row carries. A
    # board that claims two uses are MUTUALLY EXCLUSIVE says so HERE and not
    # in a header comment, and `local_tester round --plan-only` walks every
    # order of play, relic refunds included, to see whether the claim holds.
    # `KLEESPARK-BT1`'s `t02` made that claim in prose and the shipped world
    # falsified it three plays later.
    #
    # TYPED `Any` ON PURPOSE: `slot_plan` reads the card SHEETS and this
    # module builds the blind packet, so the import stays lazy -- exactly as
    # `slot_report`'s does, and for the same reason.
    resource_round: Any = None
    # `EB-236` item (d), and the STAGED-ROUND TWIN of `EB-229`. The
    # questions a registration asks the reader to answer BEFORE it commits
    # to a line, in printed vocabulary, one per entry. They are printed at
    # the TOP of the blind packet and the form carries one answer each; a
    # board that registers none prints no such block and is graded exactly
    # as every board written before this key existed. `EB-229` is the blind
    # RUN's half of the same gap -- a reply schema of `command` and
    # `thinking` has nowhere to put a prediction -- and it stays open.
    forecast: list[str] = field(default_factory=list)
    # `EB-236` item (e). A staged single turn has no next turn (packet
    # §11.6 item 1), so a board whose question is *"what does the bank read
    # NEXT turn"* has to buy one: with this set, `execute` ends the turn
    # after the graded line and takes one more reading. Opt-in, because
    # ending the turn hands the enemy its telegraphed attack, and no board
    # written before this key existed asked for that.
    replay_next_turn: bool = False

    def registered_slots(self) -> list[str]:
        """The slots this board covers. Its own id when it declares none."""
        return list(self.slots) or [self.id]

    def as_scenario(self) -> scenario.Scenario:
        """The staging half as a `scenario.Scenario`, so the existing runner
        executes it. Built directly rather than through `scenario.parse`,
        which requires an `expect` -- a staged turn asserts nothing, by
        design: it sets a board and stops."""
        # THE CLEAR GOES FIRST AND THE TOOL PUTS IT THERE. A turn file may not
        # write the verb itself (`parse` refuses it), because the whole
        # correctness of the door is its POSITION: after any grant it would
        # empty the declared hand into the draw pile and the packet would show
        # nothing at all.
        opening = [("clear_hand", {})] if self.exact_hand else []
        return scenario.Scenario(
            name=self.id, character=self.character,
            steps=opening + list(self.staging)
            + [("read", {"label": "staged board"})],
            path=self.path, seed=self.seed,
            assumptions=list(self.assumptions),
            # Forwarded so the scenario the runner sees agrees with the turn
            # about what it is. NOTE the one asymmetry, recorded rather than
            # hidden: `test_a_prototype_scenario_grants_only_prototype_ids`
            # requires a prototype SCENARIO to grant nothing else, and a
            # matched-pair turn deliberately grants a prototype card BESIDE
            # the shipped alternatives that make the decision live. That lint
            # sweeps `scenario.all_scenarios()` -- the files under
            # understudy/scenarios/ -- and never sees a turn-derived
            # Scenario, so the two rules do not meet; if they are ever made
            # to, the turn is the one that is right.
            prototype=self.prototype)


_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# The staging half may only SET things up. `play`, `end_turn` and `expect` are
# the three verbs that would make the file answer its own question.
STAGING_VERBS = scenario.SETUP_STEPS + ("read", "mark")


def parse(blob: dict[str, Any], path: Path | None = None) -> StagedTurn:
    if not isinstance(blob, dict):
        raise TurnError("a turn file is a mapping at the top level")
    for required in ("id", "character", "staging", "board"):
        if not blob.get(required):
            raise TurnError(f"missing '{required}'")
    turn_id = str(blob["id"])
    if not _ID_RE.match(turn_id):
        # The id names a directory under `review/qa/` and is printed into the
        # blind packet, so it is constrained at both ends: a path-safe slug,
        # and one the packet's own leak scrub will accept.
        raise TurnError(
            f"id {turn_id!r} must be a lowercase hyphenated slug -- it names "
            f"a directory under review/qa/ and is printed in the blind packet")

    raw_steps = blob["staging"]
    if not isinstance(raw_steps, list):
        raise TurnError("'staging' must be a list")
    steps: list[tuple[str, Any]] = []
    for i, entry in enumerate(raw_steps):
        if not isinstance(entry, dict) or len(entry) != 1:
            raise TurnError(
                f"staging step {i}: each step is a single-key mapping; "
                f"got {entry!r}")
        verb, raw = next(iter(entry.items()))
        if verb == "clear_hand":
            # EB-165. The verb is real and the scenario pack may write it; a
            # TURN may not, because here its position is load-bearing and the
            # tool owns it. Declare `exact_hand: true` and it is prepended.
            raise TurnError(
                f"staging step {i}: a turn does not write 'clear_hand' -- its "
                f"POSITION is the whole door, and after a grant it would empty "
                f"the declared hand. Declare `exact_hand: true` at the top "
                f"level and the clear is run before the first grant")
        if verb not in STAGING_VERBS:
            raise TurnError(
                f"staging step {i}: '{verb}' is not a staging verb. A staged "
                f"turn sets a BOARD; the line is the grader's answer, not the "
                f"file's. One of: " + ", ".join(STAGING_VERBS))
        body = scenario._as_body(verb, raw)
        scenario._validate(i, verb, body)
        steps.append((verb, body))

    board = _parse_board(blob["board"])
    turn = StagedTurn(
        id=turn_id, character=str(blob["character"]), staging=steps,
        board=board, path=path, seed=blob.get("seed") or None,
        notes=str(blob.get("notes") or ""),
        assumptions=[str(a) for a in (blob.get("assumptions") or [])],
        prototype=bool(blob.get("prototype", False)),
        exact_hand=bool(blob.get("exact_hand", False)),
        slots=_parse_slots(blob.get("slots")),
        resource_round=_parse_resource_round(blob, path),
        forecast=_parse_forecast(blob.get("forecast")),
        replay_next_turn=bool(blob.get("replay_next_turn", False)))
    _check_halves_agree(turn)
    _check_assumptions_blind(turn)
    return turn


def _parse_slots(raw: Any) -> list[str]:
    """R221 B's `slots:` key: a list of short registered-slot names, or absent.

    Refused rather than coerced. A slot name reaches the ledger, the packet's
    results section and the stopping rule, so a mapping or a bare string here
    would silently become a slot nobody registered.
    """
    if raw in (None, "", []):
        return []
    if not isinstance(raw, list) or not all(
            isinstance(s, str) and s.strip() for s in raw):
        raise TurnError(
            "'slots' is a list of non-empty strings -- the registered "
            "prediction slots this board is evidence about (R221 B). Omit it "
            "and the board carries one slot, its own id")
    return [s.strip() for s in raw]


def _parse_resource_round(blob: dict[str, Any], path: Path | None) -> Any:
    """EB-236's `resource_round:` block, or None. Refuses, never coerces.

    The import is LAZY -- `slot_plan` reads the card sheets, this module
    builds the blind packet, and the two are kept a function call apart on
    purpose (see `SLOT_FILE_NAME` and `slot_report`).
    """
    raw = blob.get("resource_round")
    if raw is None:
        return None
    from understudy import slot_plan
    try:
        return slot_plan.parse_resource_round(raw, where=str(path or blob["id"]))
    except slot_plan.BoardDesignError as exc:
        raise TurnError(str(exc)) from exc


def _parse_forecast(raw: Any) -> list[str]:
    """`forecast:` -- the pre-commit questions, or absent. Refuses, never
    coerces. Blindness is checked with the assumptions, since these are
    printed on the page beside them."""
    if raw in (None, "", []):
        return []
    if not isinstance(raw, list) or not all(
            isinstance(q, str) and q.strip() for q in raw):
        raise TurnError(
            "'forecast' is a list of non-empty question strings, printed at "
            "the top of the blind packet and answered BEFORE the line. Omit "
            "it and the board asks for no forecast")
    return [q.strip() for q in raw]


def _check_assumptions_blind(turn: StagedTurn) -> None:
    """The assumptions are folded into the packet's disclosures VERBATIM, so
    they are scrubbed by the same rules as a card face -- and the scrub runs
    at export, AFTER the game has been booted, embarked and boarded. Refusing
    here, at parse, is what makes `check` the gate it says it is: the first
    slice cited a register id in an assumption, `check` passed all eleven
    files, and the first `stage` burned a real launch to learn what a parse
    could have said.
    """
    bad = qa_packet.leaks(list(turn.assumptions))
    if bad:
        rule, hit, ctx = bad[0]
        raise TurnError(
            f"assumption leaks design vocabulary ({rule}: {hit!r} in "
            f"{ctx[:80]!r}): assumptions are printed in the blind packet, "
            f"so they follow the packet's own scrub -- state the fact, not "
            f"the citation")
    # The forecast questions are printed on the same page and follow the same
    # scrub, for the same reason: a question naming an id would teach a
    # reader the one thing the page exists to withhold.
    bad = qa_packet.leaks(list(turn.forecast))
    if bad:
        rule, hit, ctx = bad[0]
        raise TurnError(
            f"forecast question leaks design vocabulary ({rule}: {hit!r} in "
            f"{ctx[:80]!r}): it is printed at the top of the blind packet -- "
            f"ask it in the vocabulary the page prints")


def _parse_board(raw: Any) -> Board:
    if not isinstance(raw, dict):
        raise TurnError("'board' must be a mapping")
    for required in ("character", "hand", "enemies"):
        if not raw.get(required):
            raise TurnError(f"board: missing '{required}'")
    enemies = []
    for i, e in enumerate(raw["enemies"]):
        if not isinstance(e, dict) or not e.get("name"):
            raise TurnError(f"board enemy {i}: needs a mapping with a 'name'")
        enemies.append(dict(e))
    return Board(
        character=str(raw["character"]),
        hand=[str(c) for c in raw["hand"]],
        enemies=enemies,
        pilot=str(raw.get("pilot") or "generic"),
        hp=int(raw.get("hp", 70)),
        max_hp=int(raw.get("max_hp", raw.get("hp", 70))),
        block=int(raw.get("block", 0)),
        energy=int(raw.get("energy", 3)),
        turn=int(raw.get("turn", 1)),
        resources={str(k): int(v) for k, v in (raw.get("resources") or {}).items()},
    )


def _check_halves_agree(turn: StagedTurn) -> None:
    """The staged hand and the mirrored hand are the same multiset of cards.

    Checked through `scenario.card_key`, which folds the three spellings this
    repo uses. Without this, `closeness` would answer about a board nobody
    staged and the packet would show a board nobody scored -- and the two
    would look like one reading.
    """
    staged = sorted(scenario.card_key(str(b.get("card")))
                    for v, b in turn.staging
                    if v == "give" and str(b.get("pile") or "hand") == "hand"
                    for _ in range(int(b.get("count", 1))))
    mirrored = sorted(scenario.card_key(c) for c in turn.board.hand)
    if staged != mirrored:
        raise TurnError(
            f"the staged hand and board.hand disagree: staged {staged}, "
            f"board {mirrored}. They describe the same board, so a card in "
            f"one and not the other is a falsifier reading taken on a board "
            f"nobody staged")


def load(path: str | Path) -> StagedTurn:
    p = Path(path)
    return parse(yaml.safe_load(p.read_text(encoding="utf-8")), path=p)


def all_turns(directory: Path | None = None) -> list[Path]:
    """Every turn file, RECURSIVELY.

    Recursive because a slice is a set of MATCHED PAIRS that only mean
    anything together, so they live in one subdirectory
    (`understudy/turns/kokomi-slice-1/`) rather than scattered through a flat
    list beside the worked example. `fixtures/` is excluded by name: it holds
    grader FORMS, not turns, and `check` would report every one of them BAD.
    `slots.yaml` is excluded for the same reason: it is EB-202's slot
    registration for the round it sits in, not a board, and `check` reads it
    through `slot_plan` rather than as a turn.
    """
    d = directory or TURN_DIR
    if not d.is_dir():
        return []
    return sorted(path for path in d.rglob("*.yaml")
                  if "fixtures" not in path.relative_to(d).parts
                  and path.name != SLOT_FILE_NAME)


def turn_dir(turn_id: str) -> Path:
    return QA_DIR / turn_id


# --------------------------------------------------------------- staging ---

class _StagingComplete(RuntimeError):
    """The board is set. Raised to stop the driver where the turn begins.

    `RunDriver.run` files any escaping exception as a `harness_exception`
    defect and returns its summary, which is exactly the behaviour wanted
    here: the run STOPS at the staged board instead of handing it to
    `policy_v1`, which would play the turn the grader is supposed to play.
    The summary's outcome is checked for this class's name rather than for
    success, and `cmd_stage` says so in its output.
    """


class StagingPolicy:
    """`policy_v1` everywhere but the first combat screen, where it stops.

    `scenario.ScenarioPolicy` hands combat BACK to `policy_v1` so the fight
    can end. This one must not: the whole point is a board frozen at the
    moment the turn begins, either for a packet export or for a person to sit
    down in front of.
    """

    def __init__(self, runner: scenario.Runner):
        from understudy import policy_v1
        self._policy = policy_v1
        self.POLICY_VERSION = "staged_turn/" + policy_v1.POLICY_VERSION
        self.BLOCK_MATTERS_FRACTION = policy_v1.BLOCK_MATTERS_FRACTION
        self.COMPANION_SHARE_FOR_GUEST_CAST = \
            policy_v1.COMPANION_SHARE_FOR_GUEST_CAST
        self.Memo = policy_v1.Memo
        self.runner = runner
        self.staged_state: dict[str, Any] | None = None
        self.ok: bool | None = None

    def decide(self, state: dict[str, Any], memo: Any,
               commit: str | None = None):
        st = str(state.get("state_type") or "")
        if self.staged_state is None and st in scenario.COMBAT_SCREENS:
            self.ok = self.runner.run()
            self.staged_state = self.runner.state or state
            raise _StagingComplete(
                "the board is staged; the driver stops here so the turn is "
                "not played by a bot")
        return self._policy.decide(state, memo, commit=commit)


def stage_board(turn: StagedTurn, why: str, *, hold: bool,
                out_path: Path, seed: str | None = None
                ) -> tuple[dict[str, Any], dict[str, Any]]:
    """Boot, embark, reach the first fight, set the board. Returns
    `(live wire state, the run summary)`.

    `seed` PINS THE RUN, and the run summary reports back the seed the game
    actually used either way -- `None` is R95's read-back arm (the game rolls,
    we record) and a string is P1.5's chosen arm, which `RunDriver` verifies
    and files as a `seed_not_honoured` defect if the game ignored it. The
    ENCOUNTER IS GENERATED FROM THAT SEED, which is why the recorded value is
    the difference between a packet that can be replayed and one that cannot:
    the first live `execute` of this tool rolled its own seed, drew a Sludge
    Spinner where the packet showed a Shrinker Beetle, and refused at the
    first targeted play.
    """
    from understudy import soak

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        runner = scenario.Runner(turn.as_scenario(), why, out=fh)
        runner.emit({"step": "staged_turn_begin", "turn": turn.id,
                     "character": turn.character, "hold": hold,
                     "file": str(turn.path),
                     "assumptions": turn.assumptions})
        policy = StagingPolicy(runner)
        # `--hold` attaches to a game somebody else launched, and that is not
        # a convenience: `run_scripted`'s `finally` tears the session down,
        # and a teardown that owns the launch KILLS THE GAME -- which is the
        # one thing a hold must not do. With `do_setup=False` the session
        # makes no game-dir changes and owns no process, so the reversibility
        # ledger is empty and the staged board is still on the screen when
        # this returns.
        summary = soak.run_scripted(policy, stamp, character=turn.character,
                                    max_fights=1,
                                    chosen_seed=seed or turn.seed,
                                    do_setup=not hold)
        runner.emit({"step": "staged_turn_end", "staged": policy.staged_state
                     is not None, "steps_ok": policy.ok,
                     "seed_requested": seed or turn.seed,
                     "seed_used": summary.get("seed"), "run": summary})
    if policy.staged_state is None:
        raise TurnError(
            f"no combat screen was ever reached, so nothing was staged "
            f"(run outcome: {summary.get('outcome')} "
            f"{summary.get('detail')})")
    if not policy.ok:
        raise TurnError(
            f"a staging step failed; the board is not the one the file "
            f"describes. See {out_path}")
    return policy.staged_state, summary


def declared_hand_keys(turn: StagedTurn) -> list[str]:
    """The declared hand as sorted `scenario.card_key`s, one per copy.

    Read off the GIVE steps rather than off `board.hand`, because the give
    steps are what the game was actually told; `_check_halves_agree` has
    already pinned the two equal, so the choice is about which record is the
    instruction and not about which is right.
    """
    return sorted(scenario.card_key(str(b.get("card")))
                  for v, b in turn.staging
                  if v == "give" and str(b.get("pile") or "hand") == "hand"
                  for _ in range(int(b.get("count", 1))))


def staged_card_names(turn: StagedTurn) -> list[str]:
    """Every card the turn names, in both halves: the granted ids and the
    mirrored hand. Both, deliberately -- `_check_halves_agree` has pinned them
    equal for the HAND, but a `give` into `draw` or `discard` is in neither
    hand and can still be drawn into the grader's turn."""
    names = [str(b.get("card")) for v, b in turn.staging
             if v == "give" and b.get("card")]
    return names + list(turn.board.hand)


def face_defect_preflight(turn: StagedTurn,
                          register: dict[str, Any] | None = None) -> None:
    """EB-169. Refuse a turn that stages a card with an OPEN face defect.

    RAISES BEFORE THE GAME IS LAUNCHED, which is the whole point. Round 2 of
    the Kokomi slice staged `all_streams_flow` on eleven boards while `EB-164`
    sat open against that face, graded them, replayed them and pair-read them,
    and only then learned that the arithmetic every refusal rested on was the
    repo's own defect. The cost of learning it late is eleven launches and
    seven manufactured refusals; the cost of learning it here is a parse.

    Called by `check` and by `stage`, and NOT by `execute`: a replay is how a
    misread already in the record gets settled against the board, so refusing
    it would take away the one tool that answers the question. `grade` has its
    own copy of this check on the packet's printed hand (see `seat.py`), which
    is the belt to this one's braces.
    """
    found = face_defects.hits(staged_card_names(turn), register)
    if found:
        raise TurnError(face_defects.refusal(found))


# EB-187. AN ASSUMPTION MAY NOT CLAIM A GAIN THE FACE ALREADY PRINTS.
#
# Klee slice 1 `t06` is the case that filed it. The board's assumptions told
# the grader that "a Skill-tagged card adds 5 to [the Burst meter] on play,
# over and above anything the card's own text grants" -- while the face the
# grader was reading printed `Gain 10 Burst Energy. Burst +5`, where the
# `Burst +5` IS that tag, written onto the face by the description builder for
# every row carrying it (`tools/lint_burst_legibility.py` is the join that
# keeps the two in step). A grader who believes both counts the tag twice, and
# one did: it predicted 20 -> 40 where the board produced 20 -> 35, and the
# pair read named the arithmetic in RETURNing the arm.
#
# THE CHECK IS STRUCTURAL RATHER THAN TEXTUAL, because the face text is not
# available with no game running. The tag is: a staged row either carries
# `skill_tag` or it does not, and the lint above pins that a row carrying it
# prints the rider. So a claim of the shape "adds <N> ... over and above the
# card's own text" is refused when a staged card carries a tag whose rider is
# printed and worth exactly <N>.
#
# NARROW ON PURPOSE. It refuses a sentence that says the gain is ADDITIONAL to
# what the face says; a sentence that says the rider IS what the face prints,
# which is what those two files now say, is exactly what it wants and passes.
PRINTED_RIDERS: dict[str, tuple[str, str]] = {
    # tag -> (the tier0 constant that sizes it, what the face prints)
    "skill_tag": ("BURST_PER_SKILL_TAG", "Burst +{n}"),
}

_RIDER_CLAIM_RE = re.compile(
    r"\b(?:adds?|grants?|gives?)\s+(\d+)\b[^.]*?"
    r"\b(?:over and above|on top of|in addition to|as well as|besides)\b",
    re.I | re.S)


def _staged_tags(turn: StagedTurn) -> dict[str, list[str]]:
    """`{tag: [card ids carrying it]}` over everything the turn stages."""
    from tier0.content import loader

    index: dict[str, list[str]] = {}
    proto = ({c.id: c for c in loader.prototype_cards()}
             if turn.prototype else {})
    for raw in staged_card_names(turn):
        # `card_key` folds the three spellings onto a SPACED key, which is
        # what the face-defect register is written in; a sheet id is the same
        # key with underscores, so the fold is reused and re-spelled rather
        # than re-implemented.
        key = scenario.card_key(str(raw)).replace(" ", "_")
        card = proto.get(key)
        if card is None:
            try:
                card = loader.peek_card(key)
            except (KeyError, ValueError):
                continue
        for tag in card.tags or ():
            index.setdefault(str(tag), []).append(key)
    return index


def assumption_rider_conflicts(turn: StagedTurn) -> list[str]:
    """Every assumptions line claiming a gain the staged faces already print."""
    from tier0 import constants as C

    tags = _staged_tags(turn)
    found: list[str] = []
    for line in turn.assumptions:
        for m in _RIDER_CLAIM_RE.finditer(" ".join(str(line).split())):
            claimed = int(m.group(1))
            for tag, (const_name, printed) in PRINTED_RIDERS.items():
                amount = int(getattr(C, const_name))
                if claimed != amount or tag not in tags:
                    continue
                found.append(
                    f"an assumption says {m.group(0)!r}, but "
                    f"{', '.join(sorted(set(tags[tag])))} carr"
                    f"{'y' if len(set(tags[tag])) > 1 else 'ies'} `{tag}` and "
                    f"the face already prints "
                    f"'{printed.format(n=amount)}' -- a grader who believes "
                    f"both counts it twice")
    return found


def assumption_preflight(turn: StagedTurn) -> None:
    """EB-187. Refuse a turn whose assumptions double-count a printed rider."""
    found = assumption_rider_conflicts(turn)
    if found:
        raise TurnError(
            "the assumptions block claims a gain the card's own face already "
            "prints; say the printed rider IS the tag, or drop the sentence: "
            + "; ".join(found))


def exact_hand_difference(turn: StagedTurn, state: dict[str, Any]) -> str:
    """`""` when the live hand IS the declared hand, else what differs.

    EB-165's acceptance, checked at the one place it can be checked: after the
    clear and after the grants, against the board the packet is about to be
    written from. A multiset, in `card_key`'s folded vocabulary, so the wire's
    `KLEEMOD-CORAL_GUARD` and the file's `coral_guard` compare equal and two
    Coral Guards do not compare equal to one.
    """
    want = declared_hand_keys(turn)
    got = sorted(scenario.card_key(str(c.get("id") or c.get("name") or ""))
                 for c in scenario._hand(state))
    if want == got:
        return ""
    from collections import Counter
    extra = sorted((Counter(got) - Counter(want)).elements())
    missing = sorted((Counter(want) - Counter(got)).elements())
    parts = []
    if extra:
        parts.append(f"the board holds {extra} that the file did not declare")
    if missing:
        parts.append(f"the file declared {missing} that the board does not "
                     f"hold")
    return "; ".join(parts)


def export_packet(turn: StagedTurn, state: dict[str, Any], *,
                  run_seed: str | None = None) -> dict[str, Any]:
    """Write `packet.md`, `packet.json` and `observed.json`. Returns a report.

    THREE FILES, AND THE THIRD IS NOT PART OF THE PACKET. `packet.md` and
    `packet.json` are what a grader is handed and they are scrubbed;
    `observed.json` is the tool's own record of the live board -- the RAW wire
    state, entity ids and wire card ids included -- and it is never given to a
    grader.

    THE RAW STATE IS KEPT BECAUSE THE LIVE BOARD IS NOT THE DECLARED ONE, and
    the first live run of this tool is what proved it: the game deals its own
    opening hand, so a turn that grants five cards is staged with TEN in hand,
    and the encounter is generated, so the enemy and its telegraph are
    whatever rolled. `closeness --observed` reads this file and scores the
    board the grader actually saw. The declared `board:` half stays useful --
    it is the reading available with no game -- but where the two disagree the
    observed one is the turn.
    """
    if turn.exact_hand:
        # EB-165'S ACCEPTANCE, AND IT REFUSES RATHER THAN WARNS. A turn that
        # asked for an exact hand and got something else is a turn whose blind
        # packet would show a board the file did not describe -- the exact
        # failure the door exists to end -- and writing it anyway would put
        # that board in front of a grader who has no way to know.
        diff = exact_hand_difference(turn, state)
        if diff:
            raise TurnError(
                f"exact_hand: the live hand is not the declared hand -- "
                f"{diff}. The clear or a grant did not land; the packet is "
                f"NOT written")
    d = turn_dir(turn.id)
    d.mkdir(parents=True, exist_ok=True)
    # THE DISCLOSURES ARE SCRUBBED LIKE EVERYTHING ELSE, which is why none of
    # them names a ruling: the packet's own leak rules refuse an `R213` as
    # readily in a disclosure as in a card face, and they are right to -- a
    # grader who can see a ruling number can look up what the ruling wanted.
    # The constant is disclosed because a falsifier the grader cannot see the
    # threshold of is a filter, not a disclosure; the citation for it lives in
    # the verdict and in this module's docstring, where no grader reads.
    disclosures = [
        f"A decision-closeness falsifier reads this turn with a dominance "
        f"threshold of {DOMINANCE_GAP}.",
        "You are not being asked whether this turn is fun.",
    ] + list(turn.assumptions)
    packet = qa_packet.build(state, turn.id, repo=REPO,
                             disclosures=disclosures,
                             forecast=list(turn.forecast))
    md = qa_packet.render(packet)
    digest = qa_packet.sha256(md)
    # THE ENVELOPE, ADDED AFTER THE SCRUB AND NEVER RENDERED INTO packet.md.
    # `packet.md` is the page a grader reads and these two keys are not on
    # it: the hash is what a form is answered AGAINST, and the seed is what
    # `execute` embarks with so the encounter regenerates identically. Both
    # are facts about the RUN rather than about the board, so a grader that
    # was handed the json instead of the page learns nothing about the game
    # from either -- but neither belongs on the page.
    packet["packet_sha256"] = digest
    packet["run_seed"] = run_seed
    (d / "packet.md").write_text(md, encoding="utf-8")
    (d / "packet.json").write_text(qa_packet.dumps(packet), encoding="utf-8")
    (d / "observed.json").write_text(
        json.dumps({"turn_id": turn.id,
                    "guardrail": qa_packet.PACKET_GUARDRAIL,
                    "pilot": turn.board.pilot,
                    "run_seed": run_seed,
                    "not_a_packet": ("the RAW wire state, ids included. Tool "
                                     "side only -- never hand this to a "
                                     "grader"),
                    "digest": scenario.digest(state),
                    "state": state}, indent=1, default=str) + "\n",
        encoding="utf-8")
    live = [c["title"] for c in packet["board"]["hand"]]
    return {"dir": d, "packet_md": d / "packet.md",
            "packet_json": d / "packet.json",
            "observed_json": d / "observed.json", "sha256": digest,
            "run_seed": run_seed, "exact_hand": turn.exact_hand,
            "cards": len(live), "hand": live,
            "declared_cards": len(turn.board.hand),
            "enemies": len(packet["board"]["enemies"])}


# ----------------------------------------------------------------- form ----

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


def load_form(path: str | Path) -> dict[str, Any]:
    blob = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(blob, dict):
        raise FormError("a form is a JSON object")
    for key in ("grader", "chosen_line", *QUESTIONS):
        if key not in blob:
            raise FormError(f"the form has no {key!r}")
    grader = blob["grader"]
    if not isinstance(grader, dict) or not grader.get("id"):
        raise FormError("'grader' needs at least an 'id' -- the packet has to "
                        "record who answered it and on what")
    line = blob["chosen_line"]
    if not isinstance(line, list):
        raise FormError("'chosen_line' is an ordered list of plays")
    for i, play in enumerate(line):
        if not isinstance(play, dict) or not play.get("card"):
            raise FormError(f"chosen_line[{i}] needs a 'card' -- the PRINTED "
                            f"title, which is the only spelling the grader was "
                            f"shown")
        # EB-170. OPTIONAL and NULLABLE, so every form written before these
        # keys existed still loads unchanged. Both are stated in the PRINTED
        # vocabulary the grader was shown -- a card's title for the Exhaust
        # choice, an option's own text for a mode choice -- because that is
        # the only spelling a blind grader has.
        for key in MODAL_KEYS:
            if play.get(key) is not None and not isinstance(play[key], str):
                raise FormError(
                    f"chosen_line[{i}].{key} is the PRINTED text of the "
                    f"choice, as a string (or absent). Got "
                    f"{type(play[key]).__name__}")
    return blob


def grader_id(form: dict[str, Any]) -> str:
    return str((form.get("grader") or {}).get("id") or "unknown")


# ------------------------------------------------------------- the grade ---

def forecast_answers(form: dict[str, Any]) -> list[str]:
    """The form's `forecast` list as strings. `EB-236` item (d).

    A LIST AND NOT A MAPPING: the questions are printed and numbered on the
    page, so the answers are positional and a grader never has to spell a
    key. Numbers are accepted and stringified -- most of these ask for one.
    """
    raw = form.get("forecast")
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise FormError("'forecast' is a LIST of answers, one per question "
                        "the page numbered, in that order")
    return [str(a).strip() for a in raw]


def apply_falsifiers(turn_id: str, form: dict[str, Any], *,
                     packet_sha: str | None,
                     closeness: dict[str, Any] | None,
                     targets: dict[str, Any] | None = None,
                     forecast_asks: int = 0) -> list[str]:
    """Every rule that refuses this form, in the order they are checked.

    `targets` is EB-203's reading, computed by `grade` off the card sheet and
    the packet's hand. It defaults to `None` -- absent, not clean -- so a
    caller with no board (the ledger rebuilders, the tests that hand a bare
    form) grades exactly as it did before this rule existed.
    """
    refused: list[str] = []
    if targets and targets.get("refused"):
        refused.append("target_missing")
    given = str(form.get("packet_sha256") or "")
    if packet_sha and given and given != packet_sha:
        refused.append("packet_mismatch")
    if bool((form.get("grader") or {}).get("designed_these_cards")):
        refused.append("grader_is_designer")
    if any(not _norm(form.get(q)) for q in QUESTIONS):
        refused.append("incomplete_form")
    if not form.get("chosen_line"):
        refused.append("empty_line")
    if is_negative(form.get("q2_other_line_considered")):
        refused.append("no_second_line")
    # BOTH HALVES, and the boolean is not the authority on its own: a form
    # that ticks `q4_changed: true` and then writes "no" has answered no.
    if (form.get("q4_changed") is False
            or is_negative(form.get("q4_different_intent"))):
        refused.append("intent_insensitive")
    if closeness and closeness.get("verdict") == "REFUSED":
        refused.append("line_dominates")
    # DEFAULTS TO ZERO -- absent, not clean -- so every caller with no packet
    # (the ledger rebuilders, the tests that hand a bare form) grades exactly
    # as it did before this rule existed.
    if forecast_asks:
        answers = [a for a in forecast_answers(form) if a]
        if len(answers) < forecast_asks:
            refused.append("forecast_missing")
    return refused


def grade(turn_id: str, form: dict[str, Any], *,
          root: Path | None = None) -> dict[str, Any]:
    d = (root or QA_DIR) / turn_id
    packet_md = d / "packet.md"
    packet_sha = (qa_packet.sha256(packet_md.read_text(encoding="utf-8"))
                  if packet_md.is_file() else None)
    closeness_path = d / "closeness.json"
    closeness = (json.loads(closeness_path.read_text(encoding="utf-8"))
                 if closeness_path.is_file() else None)

    # EB-203, and it reads a SHEET, so it is imported here rather than at
    # module scope -- the same rule `local_tester._post_read` keeps and for
    # the same reason: nothing that builds a blind packet may be one refactor
    # away from a design sheet.
    from understudy import targeting
    targets = targeting.summary(form.get("chosen_line") or [],
                                hand=targeting.packet_titles(d))

    # `EB-236` item (d). HOW MANY QUESTIONS THE BOARD ASKED IS READ OFF THE
    # PACKET, not off the turn file: the packet is what the grader was
    # handed, and a turn file edited after a packet was written would be
    # grading a form against questions nobody was shown.
    packet_json = d / "packet.json"
    asks = 0
    if packet_json.is_file():
        blob = json.loads(packet_json.read_text(encoding="utf-8"))
        asks = len(blob.get("forecast") or [])

    refused = apply_falsifiers(turn_id, form, packet_sha=packet_sha,
                               closeness=closeness, targets=targets,
                               forecast_asks=asks)
    gid = grader_id(form)
    down, why_down = is_down_weighted(gid, root=root)
    verdict = {
        "turn_id": turn_id,
        "verdict": "REFUSED" if refused else "SURVIVES",
        "refused_by": refused,
        "reasons": [f"{rule}: {FALSIFIERS[rule]}" for rule in refused],
        "grader": dict(form.get("grader") or {}),
        "packet_sha256": packet_sha,
        "chosen_line": list(form.get("chosen_line") or []),
        "answers": {q: str(form.get(q) or "") for q in QUESTIONS},
        # `EB-236` item (d): A FIELD TO COUNT. `EB-229`'s finding was that a
        # forecast slot had nothing to grade because nothing recorded one;
        # this is the record, positional against the questions the packet
        # printed, and it is carried on every verdict including a refused
        # one.
        "forecast_asked": asks,
        "forecast": forecast_answers(form),
        # SURVIVES means NOT YET FALSIFIED and nothing else. It is written out
        # in the record because a one-word verdict read six months later is
        # exactly the kind of thing that gets promoted into "the tool liked
        # it".
        "survives_means": ("not yet falsified -- this funnel refuses turns "
                           "and never rates them"),
        "survives_alone": not refused and not down,
        "why_not_alone": why_down if (down and not refused) else "",
        "closeness": closeness,
        # EB-203. Carried on every verdict, refused or not: the list of the
        # hand's aimed cards is what makes the refusal actionable, and on a
        # clean form it is the record that the check ran.
        "targets": targets,
        "closeness_quotability": (
            "the decision-closeness gap is a falsifier reading of the TURN "
            "and is quotable under R215 B's exception; it is never evidence "
            "that a decision is fun"),
        "guardrail": qa_packet.PACKET_GUARDRAIL,
        "graded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    return verdict


# ------------------------------------------------------------- closeness ---

def build_combat_state(board: Board, *, prototype: bool = False):
    """The staged board as a tier0 `CombatState`.

    Returns `(state, unrepresentable)`. `unrepresentable` is the list of hand
    cards the sim has no row for; the caller REFUSES the falsifier for that
    turn rather than guessing, because a line scored with a card missing from
    it is a line nobody could play.

    `prototype` is the turn's own DEV-ROUTE DECLARATION (R213 B). Prototype
    ids are absent from `loader._card_index()` BY CONSTRUCTION -- that
    absence is the quarantine, and it is structural rather than a filter --
    so with the flag set they are resolved through the surface's own reader,
    `loader.prototype_cards()`, and only then. The flag is required rather
    than inferred from the prefix: an explicit declaration is what makes a
    prototype turn distinguishable from a turn that has a typo in it, and
    "the id started with proto_" is not a decision anybody made.
    """
    import random

    from tier0.content import loader
    from tier0.engine.state import CombatState, Enemy, Player

    proto_index: dict[str, Any] = {}
    if prototype:
        proto_index = {c.id: c for c in loader.prototype_cards()}
    else:
        # Refused BY NAME, and loudly. Without the flag a `proto_` id would
        # fall through to `unrepresentable` and the falsifier would answer
        # NOT READ -- a verdict that reads as "the sim cannot model this
        # card" when what actually happened is that the file forgot to say
        # what it was. Two very different facts must not share one output.
        stray = [n for n in board.hand
                 if str(n).startswith(loader.PROTOTYPE_ID_PREFIX)]
        if stray:
            raise TurnError(
                f"board.hand names prototype row(s) {stray} but the turn does "
                f"not declare `prototype: true`. A quarantined row is outside "
                f"the sim's card index on purpose (R213 B); the falsifier "
                f"reaches it only down the declared dev route.")

    hand = []
    unrepresentable: list[str] = []
    for name in board.hand:
        card = proto_index.get(name)
        if card is not None:
            # A COPY, because `peek_card` hands back the shared prototype and
            # every caller here is expected not to mutate it -- but
            # `prototype_cards()` builds fresh objects per call, so two hand
            # slots naming one row would otherwise be the SAME object and a
            # line that played one would consume the other.
            hand.append(copy.deepcopy(card))
            continue
        try:
            hand.append(loader.peek_card(name))
        except (KeyError, ValueError):
            unrepresentable.append(name)
    if unrepresentable:
        return None, unrepresentable

    player = Player(hp=board.hp, max_hp=board.max_hp, block=board.block,
                    energy=board.energy, hand=hand,
                    character_id=board.character)
    for key, amount in board.resources.items():
        if not hasattr(player, key):
            raise TurnError(
                f"board.resources names {key!r}, which is not a field on the "
                f"sim's Player -- a resource the sim cannot hold is a board "
                f"the falsifier cannot read")
        setattr(player, key, int(amount))

    enemies = []
    for e in board.enemies:
        intent = dict(e.get("intent") or {"kind": "block", "amount": 0})
        hp = int(e.get("hp", 1))
        enemies.append(Enemy(hp=hp, max_hp=int(e.get("max_hp", hp)),
                             block=int(e.get("block", 0)),
                             name=str(e["name"]), intents=[intent],
                             aura=e.get("aura")))
    state = CombatState(player=player, enemies=enemies,
                        # Never consumed: every scoring path below is pure,
                        # and a line that drew from the stream would make the
                        # gap depend on enumeration order.
                        rng=random.Random(0), turn=board.turn)
    return state, []


class _TooManyLines(RuntimeError):
    """The bounded walk hit its ceiling. Refuses; never truncates."""


def _enumerate_lines(state, weights, max_lines: int
                     ) -> tuple[dict[frozenset[int], float], int, int]:
    """Every line the board can actually play, scored in the pilot's currency.

    A DEPTH-FIRST WALK THAT PLAYS AS IT GOES, rather than an enumeration of
    subsets filtered afterwards, and the difference is what makes this usable
    on a live board. The game deals its own opening hand, so a staged hand is
    ten cards, not five -- and ten cards is 9.8 million orderings if you
    enumerate first and check playability second. Walking prunes at the first
    card the energy cannot buy, which takes the same board to a few hundred
    playouts.

    Each card is scored by `pilot.policy._score` against the state AS IT IS
    WHEN THAT CARD IS PLAYED, and then actually resolved through
    `combat.play_card`, so an ordering that sets something up before spending
    it scores differently from the reverse. That is why the playout is real
    rather than a sum of static reads.

    Returns `(best score per SET of cards, playouts walked, plays refused)`.
    The collapse onto sets is the other half: "what other line did you
    seriously consider" is a question about WHICH CARDS, and a top-two made of
    two orderings of the same three cards would report a gap of nearly zero
    and refuse nothing, ever.
    """
    from tier0.engine import combat
    from tier0.pilot import policy

    n = len(state.player.hand)
    best: dict[frozenset[int], float] = {}
    walked = 0
    refused = 0

    def walk(s, slots, chosen: frozenset[int], total: float) -> None:
        nonlocal walked, refused
        for i in range(n):
            if i in chosen:
                continue
            card = slots[i]
            # `Card` is a value-equality dataclass and `play_card` removes the
            # instance from hand, so the SLOT LIST -- taken before the first
            # play and copied alongside the state -- is what keeps index `i`
            # meaning the same card for the whole line. A lookup by id or by
            # equality would find the first EQUAL card instead.
            if card not in s.player.hand or not combat.card_playable(s, card):
                continue
            if walked >= max_lines:
                raise _TooManyLines(walked)
            s2, slots2 = copy.deepcopy((s, slots))
            try:
                score = total + policy._score(s2, slots2[i], weights)
                combat.play_card(s2, slots2[i])
            except Exception:                                # noqa: BLE001
                # A line the sim cannot resolve is not a line the grader could
                # have chosen, so it leaves the walk rather than scoring zero.
                refused += 1
                continue
            walked += 1
            key = chosen | {i}
            if score > best.get(key, float("-inf")):
                best[key] = score
            walk(s2, slots2, key, score)

    walk(state, list(state.player.hand), frozenset(), 0.0)
    return best, walked, refused


# The registered resources the sim holds as named Player fields. `adapter`
# does not map them (nothing in the bot loop reads them off the wire), and a
# Charge reader scored against a bank of zero is a card scored as a different
# card -- which on this repo's one shipped meter reader is the whole
# difference between a live choice and a small attack. Explicit table rather
# than a `setattr(k.lower())` guess: an unmapped resource is REPORTED, so a
# meter the falsifier silently could not see never passes for one it read.
#
# THE THREE BURST METERS ALL LAND ON ONE FIELD, and by `max` rather than by
# assignment: the wire registers `KLEEMOD_BURST`, `KLEEMOD_FURINA_BURST` and
# `KLEEMOD_KOKOMI_BURST` separately while the sim holds one
# `Player.burst_energy`, and on any real board exactly one of them is
# non-zero. `max` makes the order the dict is walked in irrelevant, which
# assignment would not.
#
# KNOWN GAP, stated rather than hidden: `burst_max` is NOT on the wire, so a
# card gated on `requires: burst_energy_full` reads as playable on an observed
# board whatever the meter holds. Nothing in this funnel's way uses that gate
# today; the day one does, this is where it breaks.
WIRE_RESOURCES = {"KLEEMOD_CHARGE": "charge", "KLEEMOD_ENCORE": "encore",
                  "KLEEMOD_FANFARE": "fanfare",
                  "KLEEMOD_BURST": "burst_energy",
                  "KLEEMOD_FURINA_BURST": "burst_energy",
                  "KLEEMOD_KOKOMI_BURST": "burst_energy"}


def observed_state(blob: dict[str, Any], *, prototype: bool = False):
    """The LIVE board from an `observed.json`, as a tier0 `CombatState`.

    Reuses `understudy.adapter.build_combat_state`, which is the repo's
    existing wire-to-sim constructor and already carries the two decisions
    that matter here: a hand card resolves to its SHEET row where the wire id
    names one (and is flagged approximate where it does not), and enemy powers
    are dropped because the intent label the wire prints has already folded
    them in.

    Returns `(state, unrepresentable, notes)`.
    """
    from understudy import adapter

    raw = blob.get("state") or {}
    if not raw:
        raise TurnError(
            "observed.json holds no raw state -- it was written by a build of "
            "this tool that only kept the digest. Re-stage the turn")
    cs, notes = adapter.build_combat_state(raw, prototype=prototype)
    wire = (raw.get("player") or {}).get("resources") or {}
    unmapped = []
    for key, amount in wire.items():
        field_name = WIRE_RESOURCES.get(str(key))
        if field_name is None:
            unmapped.append(str(key))
            continue
        setattr(cs.player, field_name,
                max(int(amount or 0), int(getattr(cs.player, field_name, 0))))
    notes = dict(notes, unmapped_resources=sorted(unmapped))
    return cs, list(notes.get("approximate_cards") or []), notes


def closeness(board: Board, *, max_lines: int = MAX_LINES,
              prototype: bool = False) -> dict[str, Any]:
    """The R213 F falsifier on the DECLARED board. Refuses; never rates."""
    state, unrepresentable = build_combat_state(board, prototype=prototype)
    return _closeness(state, board.pilot, unrepresentable,
                      max_lines=max_lines,
                      source=("declared board (prototype route)" if prototype
                              else "declared board"))


def closeness_observed(blob: dict[str, Any], *, pilot: str = "",
                       max_lines: int = MAX_LINES,
                       prototype: bool = False) -> dict[str, Any]:
    """The same falsifier on the board the grader actually saw.

    `prototype` reaches the wire resolver for the same reason it reaches the
    declared one: without it a live prototype card degrades to the adapter's
    text approximation and the reading is refused as approximate, which is
    the wrong answer to give about a card the sim has an exact row for.
    """
    state, unrepresentable, notes = observed_state(blob, prototype=prototype)
    result = _closeness(state, pilot or str(blob.get("pilot") or "generic"),
                        unrepresentable, max_lines=max_lines,
                        source="observed board (live wire state)")
    return dict(result, observed_notes=notes)


def _closeness(state, pilot: str, unrepresentable: list[str], *,
               max_lines: int, source: str) -> dict[str, Any]:
    from tier0.content import loader

    base = {
        "source": source,
        "falsifier": "decision-closeness (R213 F)",
        "dominance_gap": DOMINANCE_GAP,
        "quotability": (
            "a falsifier reading of the TURN, quotable under R215 B's "
            "exception to the prototype clause; never a claim that a "
            "decision is fun and never comparable across turns"),
        "guardrail": qa_packet.PACKET_GUARDRAIL,
    }
    if unrepresentable:
        return dict(base, applicable=False, verdict="NOT READ",
                    reason=f"not representable in the sim: "
                           f"{', '.join(unrepresentable)}",
                    unrepresentable=unrepresentable)

    weights = loader.pilot_weights(pilot)
    try:
        best_by_set, walked, unplayable = _enumerate_lines(state, weights,
                                                           max_lines)
    except _TooManyLines:
        return dict(base, applicable=False, verdict="NOT READ",
                    reason=f"the board's line space passed the {max_lines} "
                           f"playout bound; the falsifier refuses rather "
                           f"than truncating, because a gap that depends on "
                           f"which lines were walked first is not a reading")

    ranked = sorted(((score, sorted(key)) for key, score in best_by_set.items()),
                    key=lambda t: (-t[0], t[1]))
    named = [{"cards": [state.player.hand[i].name for i in cards],
              "score": round(score, 4)} for score, cards in ranked[:5]]
    if len(ranked) < 2:
        return dict(base, applicable=False, verdict="NOT READ",
                    reason=f"only {len(ranked)} playable line(s) on this "
                           f"board; there is no second line to be close to",
                    lines=named)
    top1, top2 = ranked[0][0], ranked[1][0]
    if top1 <= 0:
        return dict(base, applicable=False, verdict="NOT READ",
                    reason="the pilot's surface values no line above zero "
                           "here, so a ratio against it says nothing",
                    lines=named)
    gap = (top1 - top2) / top1
    dominated = gap > DOMINANCE_GAP
    return dict(base, applicable=True,
                verdict="REFUSED" if dominated else "SURVIVES",
                gap=round(gap, 4), top1=round(top1, 4), top2=round(top2, 4),
                lines_considered=len(best_by_set),
                playouts=walked, plays_refused=unplayable,
                pilot=pilot, lines=named,
                reason=(FALSIFIERS["line_dominates"] if dominated else
                        "no line dominates by more than the derived gap"))


# ---------------------------------------------------------------- ledger ---

# R221 B added the last two, at the END and nowhere else: `ledger_rows` pads
# a short row, so every ledger written before this parses unchanged and every
# reader that indexes by name keeps working. `seed` is the pin a later round
# needs to run an UNRUN board rather than a re-rolled one, and `run_state` is
# RUN for a graded row and UNRUN for a board sequential stopping did not run.
# The two-instance build added `instance`, at the END for the same reason
# `seed` and `run_state` were added there: `ledger_rows` pads a short row, so
# every ledger written before this parses unchanged and a row with no lane on
# it reads as the empty string rather than shifting every column after it.
LEDGER_COLUMNS = ("turn_id", "grader", "verdict", "refused_by",
                  "q1", "q2", "q3", "q4",
                  "agree_q1", "agree_q2", "agree_q4", "survives_alone",
                  "seed", "run_state",
                  # pick 4(e). WHICH CHAIR this row's grader sat in --
                  # `shadow` for a read that was taken but is not the deciding
                  # verdict, `deciding` for everything else, which is every
                  # row written before the chair existed. APPENDED, never
                  # inserted: `ledger_rows` zips the columns onto whatever
                  # cells a line has, so a short historical row parses and
                  # simply reads `deciding`.
                  "role",
                  # The two-instance build's lane, LAST -- after `role`, which
                  # main countersigned first. Same padding argument.
                  "instance")


def _cell(text: Any, width: int = 90) -> str:
    """One ledger cell: no tabs, no newlines, bounded."""
    s = " ".join(str(text or "").split())
    return (s[:width - 1] + "…") if len(s) > width else s


def _line_titles(form: dict[str, Any]) -> list[str]:
    return [_norm(p.get("card")) for p in (form.get("chosen_line") or [])]


def q2_agrees(a: dict[str, Any], b: dict[str, Any],
              titles: list[str]) -> bool | None:
    """Do two graders' second answers name a card in common?

    `titles` is the printed titles from the packet, which is the only
    vocabulary either answer could be written in. Deliberately shallow: this
    is not a semantic comparison and does not pretend to be one -- it asks
    whether the two people were weighing the same alternative, which is the
    thing R213's guard is about. `None` when neither answer names a card at
    all, so an unreadable pair does not count as a disagreement.
    """
    na, nb = _norm(a.get("q2_other_line_considered")), \
        _norm(b.get("q2_other_line_considered"))
    sa = {t for t in titles if t and t in na}
    sb = {t for t in titles if t and t in nb}
    if not sa and not sb:
        return None
    return bool(sa & sb)


def ledger_rows(root: Path | None = None) -> list[dict[str, str]]:
    path = (root or QA_DIR) / "ledger.tsv"
    if not path.is_file():
        return []
    rows = []
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if not raw.strip() or raw.startswith("#"):
            continue
        cells = raw.split("\t")
        if i == 0 and cells and cells[0] == "turn_id":
            continue
        row = dict(zip(LEDGER_COLUMNS, cells + [""] * len(LEDGER_COLUMNS)))
        # A row written before the chair existed says nothing about it, and
        # "nothing" means the only chair there was.
        row["role"] = row.get("role") or DECIDING_ROLE
        rows.append(row)
    return rows


DECIDING_ROLE = "deciding"


def grader_role(turn_id: str, gid: str, root: Path | None = None) -> str:
    """Which chair a grader sat in for this turn, off its own tester record.

    Only the local seat writes a `tester-<id>.json`, and only it can be in the
    shadow chair; every other grader, and every record written before the
    chair existed, is `deciding`.
    """
    path = (root or QA_DIR) / turn_id / f"tester-{gid}.json"
    if not path.is_file():
        return DECIDING_ROLE
    try:
        blob = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return DECIDING_ROLE
    return str(blob.get("role") or DECIDING_ROLE)


def is_down_weighted(gid: str, root: Path | None = None) -> tuple[bool, str]:
    """R213's second guard, made concrete.

    A grader that is not [USER] and whose QUESTION TWO disagreed with [USER]'s
    on at least WEIGHT_DISAGREE of the last WEIGHT_WINDOW turns they both
    answered loses the power to mark a turn SURVIVES ALONE. Turns where the
    comparison could not be made (no [USER] form, or neither answer named a
    card) are not counted either way -- an absent comparison is not a
    disagreement.
    """
    if gid == USER_GRADER:
        return False, ""
    shared = [r for r in ledger_rows(root)
              if r["grader"] == gid and r["agree_q2"] in ("yes", "no")]
    window = shared[-WEIGHT_WINDOW:]
    disagreements = sum(1 for r in window if r["agree_q2"] == "no")
    if disagreements >= WEIGHT_DISAGREE:
        return True, (
            f"grader {gid!r} is down-weighted: its answer to question two "
            f"disagreed with [USER]'s on {disagreements} of the last "
            f"{len(window)} turns they both played, so its SURVIVES needs "
            f"[USER]'s own cold-play form beside it "
            f"(threshold: {WEIGHT_DISAGREE} of {WEIGHT_WINDOW})")
    return False, ""


def _packet_titles(turn_id: str, root: Path | None = None) -> list[str]:
    p = (root or QA_DIR) / turn_id / "packet.json"
    if not p.is_file():
        return []
    blob = json.loads(p.read_text(encoding="utf-8"))
    return [_norm(c.get("title"))
            for c in ((blob.get("board") or {}).get("hand") or [])]


def _packet_seed(turn_id: str, root: Path | None = None) -> str:
    p = (root or QA_DIR) / turn_id / "packet.json"
    if not p.is_file():
        return "-"
    blob = json.loads(p.read_text(encoding="utf-8"))
    return str(blob.get("run_seed") or "-")


# ------------------------------------------------- R221 B: the UNRUN board --

UNRUN_NOTE = (
    "R221 B: sequential stopping. This board was staged in the round's "
    "pre-registered order and NOT run, because every registered slot it "
    "carries was already DECIDED -- two or more grades that all agreed -- "
    "before its turn came. Its seed is pinned here so a later round runs THIS "
    "board rather than a re-rolled one. Nothing about it was graded, and an "
    "UNRUN board is a board with no record, never a struck one (R101b)")


def mark_unrun(turn_id: str, *, seed: str, slots: Sequence[str],
               why: str, root: Path | None = None) -> Path:
    """Record a board the stopping rule did not run. One file, one row."""
    home = (root or QA_DIR) / turn_id
    home.mkdir(parents=True, exist_ok=True)
    path = home / "unrun.json"
    path.write_text(json.dumps({
        "turn_id": turn_id,
        "instance": bridge.current_label(),
        "run_state": "UNRUN",
        "seed": seed or "-",
        "slots": list(slots),
        "why": why,
        "rule": UNRUN_NOTE,
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }, indent=1) + "\n", encoding="utf-8")
    return path


# ------------------------------------------ EB-208: the UNREACHED board ----

UNREACHED_NOTE = (
    "EB-208: the live-count preflight. A staged board cannot REQUIRE an enemy "
    "count -- the encounter is generated and a seed grants or refuses the "
    "bodies the turn file asked for -- and EB-202's ceiling is computed off "
    "the DECLARED board by construction, so a board that declared three and "
    "staged one still counted toward a counting slot's ceiling. After staging, "
    "the live enemy count is compared with the declared one; where they "
    "differ, this board is UNREACHED for every registered slot whose "
    "predicate reads `enemy_count`, and those slots take NO GRADE from it -- "
    "a board that cannot be asked is UNREACHED by the slate's own rule. The "
    "board is still read, graded and replayed: it may answer its other slots, "
    "and a shadow read costs nothing. Nothing here is struck (R101b); the "
    "board's own grades stand for the slots it could pose")


def live_enemy_count(turn_id: str, root: Path | None = None) -> int | None:
    """How many bodies the game actually staged, or `None` where nothing says.

    OFF `observed.json`, which is the tool's own record of the RAW wire state
    (`export_packet`). Its `digest.enemies` is the same list the packet's
    scrubbed board is built from, and it is read first because it is the
    unscrubbed one; `state.battle.enemies` and then the packet's own board are
    read after it so a board staged by an older build still answers.

    `None` IS NOT ZERO. A board with no record on disk has not been staged and
    says nothing about its live count, and the preflight must not read that
    silence as a mismatch.
    """
    home = (root or QA_DIR) / turn_id
    for name, path_to in (("observed.json",
                           (("digest", "enemies"),
                            ("state", "battle", "enemies"))),
                          ("packet.json", (("board", "enemies"),))):
        path = home / name
        if not path.is_file():
            continue
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for keys in path_to:
            node: Any = blob
            for key in keys:
                node = node.get(key) if isinstance(node, dict) else None
            if isinstance(node, list):
                return len(node)
    return None


def mark_unreached(turn_id: str, *, seed: str, slots: Sequence[str],
                   declared: int, live: int,
                   root: Path | None = None) -> Path:
    """Record the slots this board cannot pose. One file, beside the rest."""
    home = (root or QA_DIR) / turn_id
    home.mkdir(parents=True, exist_ok=True)
    path = home / "unreached.json"
    why = (f"the board declared {declared} enem(ies) and the game staged "
           f"{live} on seed {seed or '-'}; a slot that counts enemies cannot "
           f"be posed by this board")
    path.write_text(json.dumps({
        "turn_id": turn_id,
        "instance": bridge.current_label(),
        # THE BOARD RAN. `run_state` is the ledger's own column and this
        # board earns its RUN: it was staged, read, graded and replayed. What
        # is UNREACHED is a SLOT ON IT, which is why that is a separate key
        # and not a second ledger column.
        "run_state": "RUN",
        "slot_state": "UNREACHED",
        "seed": seed or "-",
        "slots": list(slots),
        "declared_enemies": int(declared),
        "live_enemies": int(live),
        "why": why,
        "rule": UNREACHED_NOTE,
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }, indent=1) + "\n", encoding="utf-8")
    return path


def unreached_boards(root: Path | None = None) -> list[dict[str, Any]]:
    """Every UNREACHED marker on disk, by turn id."""
    base = root or QA_DIR
    out = []
    for q in sorted(base.glob("*/unreached.json")):
        blob = json.loads(q.read_text(encoding="utf-8"))
        blob.setdefault("turn_id", q.parent.name)
        out.append(blob)
    return out


def unreached_slots(root: Path | None = None) -> dict[str, list[str]]:
    """`turn id -> the slots that board may not be graded on` (EB-208)."""
    return {str(b["turn_id"]): [str(s) for s in (b.get("slots") or [])]
            for b in unreached_boards(root)}


def unrun_boards(root: Path | None = None) -> list[dict[str, Any]]:
    """Every UNRUN marker on disk, by turn id."""
    base = root or QA_DIR
    out = []
    for q in sorted(base.glob("*/unrun.json")):
        blob = json.loads(q.read_text(encoding="utf-8"))
        blob.setdefault("turn_id", q.parent.name)
        out.append(blob)
    return out


def _row_instance(tid: str, gid: str, root: Path | None) -> str:
    """Which lane replayed this (turn, grader), off the execute record.

    The verdict does not carry it -- grading is mechanical and touches no
    game -- so the lane is read from the replay that DID touch one. `-` where
    a turn was never replayed, and for every row written before lanes existed.
    """
    home = (root or QA_DIR) / tid
    for name in (f"execute-{gid}.json", "execute.json"):
        path = home / name
        if not path.is_file():
            continue
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        return str(blob.get("instance") or "-")
    return "-"


#: R221 + the two-instance build. Two lanes write per-turn artifacts into
#: their OWN `review/qa/<turn-id>/` directories, so those never collide -- but
#: `ledger.tsv` is ONE file for the whole round, rebuilt from disk rather than
#: appended to. This lock is what keeps a rebuild from two lanes at once from
#: interleaving a read of the directory with somebody else's write of the file.
LEDGER_LOCK = threading.Lock()


def build_ledger(root: Path | None = None) -> str:
    """One row per (turn, grader), with the agreement columns filled in.

    Rebuilt from the verdicts on disk rather than appended to, so a re-graded
    turn cannot leave a stale row behind arguing with its own replacement.
    """
    base = root or QA_DIR
    by_turn: dict[str, dict[str, dict[str, Any]]] = {}
    # `verdict-<grader>.json` and NOT `verdict.json`: the latter is the
    # brief's fixed path for "the verdict on this turn" and is rewritten by
    # every grade, so globbing it too would enter the most recent grader
    # twice.
    for verdict_path in sorted(base.glob("*/verdict-*.json")):
        blob = json.loads(verdict_path.read_text(encoding="utf-8"))
        tid = str(blob.get("turn_id") or verdict_path.parent.name)
        gid = str((blob.get("grader") or {}).get("id") or "unknown")
        by_turn.setdefault(tid, {})[gid] = blob

    out = ["\t".join(LEDGER_COLUMNS)]
    for tid in sorted(by_turn):
        graders = by_turn[tid]
        titles = _packet_titles(tid, root)
        user = graders.get(USER_GRADER)
        for gid in sorted(graders):
            v = graders[gid]
            answers = v.get("answers") or {}
            agree = {"agree_q1": "-", "agree_q2": "-", "agree_q4": "-"}
            if user is not None and gid != USER_GRADER:
                ua = user.get("answers") or {}
                agree["agree_q1"] = _yn(
                    _line_titles(v) == _line_titles(user))
                a2 = q2_agrees({"q2_other_line_considered":
                                answers.get("q2_other_line_considered")},
                               {"q2_other_line_considered":
                                ua.get("q2_other_line_considered")}, titles)
                agree["agree_q2"] = "-" if a2 is None else _yn(a2)
                agree["agree_q4"] = _yn(
                    is_negative(answers.get("q4_different_intent"))
                    == is_negative(ua.get("q4_different_intent")))
            out.append("\t".join([
                tid, gid, str(v.get("verdict") or ""),
                ",".join(v.get("refused_by") or []) or "-",
                _cell(answers.get("q1_what_did_you_play")),
                _cell(answers.get("q2_other_line_considered")),
                _cell(answers.get("q3_what_it_gave_up")),
                _cell(answers.get("q4_different_intent")),
                agree["agree_q1"], agree["agree_q2"], agree["agree_q4"],
                _yn(bool(v.get("survives_alone"))),
                _packet_seed(tid, root), "RUN",
                grader_role(tid, gid, root),
                _row_instance(tid, gid, root),
            ]))
    # R221 B. The boards the stopping rule did not run, with their seeds
    # still pinned. They sit in the SAME table as the graded rows
    # deliberately: a round's record has to say what it did not do, or
    # "we ran four boards" and "there were only four boards" read the same
    # way afterwards.
    for blob in unrun_boards(root):
        if str(blob.get("turn_id")) in by_turn:
            continue
        out.append("\t".join([
            str(blob.get("turn_id") or ""), "-", "UNRUN",
            _cell(blob.get("why")) or "-",
            "-", "-", "-", "-", "-", "-", "-", "-",
            str(blob.get("seed") or "-"), "UNRUN", "-",
            str(blob.get("instance") or "-"),
        ]))
    out.append(f"# {qa_packet.PACKET_GUARDRAIL}")
    out.append(f"# down-weighting: a grader whose q2 disagrees with "
               f"[USER] on {WEIGHT_DISAGREE} of its last {WEIGHT_WINDOW} "
               f"shared turns cannot mark a turn SURVIVES alone")
    out.append(f"# UNRUN: {UNRUN_NOTE}")
    return "\n".join(out) + "\n"


def _yn(value: bool) -> str:
    return "yes" if value else "no"


# --------------------------------------------------------------- execute ---

def execute_steps(turn: StagedTurn, form: dict[str, Any]
                  ) -> list[tuple[str, Any]]:
    """The staging steps, a mark, then the grader's line as `play` steps.

    THE TRANSLATION FROM TITLE TO ID HAPPENS HERE AND NOWHERE THE GRADER CAN
    SEE. `scenario.find_card` matches a printed title against the hand the
    wire just returned and hands the POST a card INDEX -- so the agent's
    answer stays a list of faces and the bridge still gets the identity it
    needs. Same for a target: `find_enemy` takes the enemy's display name.
    """
    # THE SAME OPENING `stage` USES, and for the same reason: a turn that asked
    # for an exact hand and is replayed without the clear is replayed onto the
    # dealt hand, which is a different board. The guard below would catch it --
    # and did, the first time this ran on an exact-hand turn -- but catching it
    # is not the same as replaying the turn.
    steps = ([("clear_hand", {})] if turn.exact_hand else []) + list(turn.staging)
    # BEFORE THE MARK AND BEFORE EVERY PLAY. A line replayed onto a board the
    # packet never showed is not a replay of anything.
    steps.append(("board_check", {}))
    steps.append(("mark", {}))
    for play in form.get("chosen_line") or []:
        body: dict[str, Any] = {"card": str(play["card"])}
        if play.get("target"):
            body["target"] = str(play["target"])
        # EB-184: THE MODE TRAVELS WITH THE PLAY, not only with the screen that
        # follows it. The form's `choose` is answered a step later, on the
        # choose-a-card screen -- but the bridge has to decide whether the play
        # needs aiming BEFORE that screen exists, because the game aims a card
        # before its mode is chosen. Told the mode here, it asks the mode; told
        # nothing, it asks the card TYPE and refuses a targetless Block half of
        # an Attack-typed modal, which is exactly how slice 1 round 4 `t02`
        # ended UNTESTED. The value is the same string the `answer_modal` step
        # below carries, off the same form key: one reading, two readers.
        if play.get("choose"):
            body["mode"] = str(play["choose"])
        steps.append(("play", body))
        # EB-170. ONE AFTER EVERY PLAY, unconditionally, and not only after
        # the plays whose form entry carries a key. A modal is a property of
        # the card and the board, not of what the grader remembered to write
        # down: the step is a no-op when no screen is up, and the whole point
        # of the row is that a prompt nobody declared is REPORTED rather than
        # walked into by the next play. Round 3 walked into three of them and
        # read `no enemy 'Twig Slime (S)'; the fight has []` -- a true
        # sentence about a card-selection screen, and a useless one.
        answers = {k: str(play[k]) for k in MODAL_KEYS
                   if play.get(k) is not None}
        steps.append(("answer_modal", {"card": str(play["card"]), **answers}))
    steps.append(("read", {"label": "after the graded line"}))
    if turn.replay_next_turn:
        # `EB-236` item (e). END THE TURN AND READ AGAIN. A price whose refund
        # arrives at the START of the next turn -- Bombs sitting on a body
        # until the turn-start sweep pops them and `Pounding Surprise` pays
        # one Spark each -- cannot be read on a board that stops when the
        # line does. The enemy takes its telegraphed turn in between, which
        # is why this is opt-in and why the board that asks for it declares
        # the incoming damage in its own assumptions.
        steps.append(("end_turn", {}))
        steps.append(("read", {"label": "the start of the next turn"}))
    return steps


def parse_answers(raw: list[str] | None) -> list[tuple[str, str]]:
    """`--answer "<prompt>=<printed choice>"`, as ordered (match, choice).

    THE OPERATOR'S ANSWER, AND IT IS LABELLED AS ONE. It exists for exactly
    one situation: a form written BEFORE the `exhaust` / `choose` keys existed,
    whose q1 prose names the choice unambiguously, being replayed so the record
    stops saying "untested". The operator reads the prose, states the answer on
    the command line, and every row it fills is logged with
    `source: "operator"` and the prose it came from is the reader's to check.
    It is never a default, never a heuristic, and it never overrides the form:
    a form that says `exhaust` is the grader's own answer and wins.

    The left-hand side matches the live PROMPT TEXT (case-insensitive
    substring) or the screen's own wire name, because a screen can arrive with
    no prompt at all and an operator still has to be able to name it.
    """
    out: list[tuple[str, str]] = []
    for entry in raw or []:
        if "=" not in str(entry):
            raise FormError(
                f"--answer takes '<prompt>=<printed choice>'; got {entry!r}. "
                f"The left side matches the prompt the game shows (or the "
                f"screen name, hand_select / card_select) and the right side "
                f"is the PRINTED text of the choice")
        match, choice = str(entry).split("=", 1)
        if not match.strip() or not choice.strip():
            raise FormError(f"--answer {entry!r}: both halves are required")
        out.append((match.strip(), choice.strip()))
    return out


def board_differences(packet: dict[str, Any],
                      state: dict[str, Any]) -> list[str]:
    """How the LIVE board differs from the one the packet showed.

    Compared in the grader's own vocabulary and in no other: the enemies'
    PRINTED names and the hand's PRINTED titles as a MULTISET. Not ids, not
    HP, not intents. The question this answers is "is this the same turn the
    form was answered about", and the two things that make it a different turn
    are a different encounter and a different hand -- both of which the first
    live `execute` produced at once, because it rolled its own seed.

    A multiset and not a set: three Coral Guards and one Coral Guard are
    different hands, and a set comparison would call them equal.
    """
    from understudy import adapter

    want_enemies = sorted(qa_packet._text(e.get("name"))
                          for e in (packet.get("board") or {}).get("enemies") or [])
    got_enemies = sorted(qa_packet._text(e.get("name"))
                         for e in adapter.enemy_blobs(state))
    want_hand = sorted(qa_packet._text(c.get("title"))
                       for c in (packet.get("board") or {}).get("hand") or [])
    got_hand = sorted(qa_packet._text(c.get("name"))
                      for c in scenario._hand(state))
    out: list[str] = []
    if want_enemies != got_enemies:
        out.append(f"enemies: packet showed {want_enemies}, the fight has "
                   f"{got_enemies}")
    if want_hand != got_hand:
        out.append(f"hand: packet showed {want_hand}, the board has "
                   f"{got_hand}")
    return out


class ExecuteRunner(scenario.Runner):
    """`scenario.Runner` with one extra verb: `board_check`.

    THE GUARD RUNS BEFORE THE FIRST PLAY AND REFUSES BY NAME. `_do_play`'s own
    "no enemy 'Shrinker Beetle'" is a fine second line of defence and it is
    kept, but it fires per play and reads as one bad target rather than as the
    whole board being somebody else's -- which is what it actually was the
    first time this ran live. A guard that names `board_mismatch` and lists
    both differences is a failure a person can act on.

    A subclass rather than a verb added to `scenario.py`: `Runner._step`
    dispatches on `_do_<verb>`, so the verb exists exactly where its meaning
    does, and the scenario pack's parser still refuses it as unknown.
    """

    def __init__(self, *args: Any, packet: dict[str, Any] | None = None,
                 answers: list[tuple[str, str]] | None = None,
                 **kw: Any):
        super().__init__(*args, **kw)
        self.packet = packet or {}
        # EB-170. The operator's answers, in order, each consumed at most once
        # so a single `--answer` cannot silently drive two different prompts.
        self.answers = list(answers or [])
        self.answers_used: list[dict[str, Any]] = []
        self.modals: list[dict[str, Any]] = []

    def _do_board_check(self, body: dict[str, Any]) -> None:
        self.read()
        diffs = board_differences(self.packet, self.state)
        self.emit({"step": "board_check", "rule": "board_mismatch",
                   "ok": not diffs, "differences": diffs,
                   "packet_sha256": self.packet.get("packet_sha256"),
                   "run_seed": self.packet.get("run_seed")})
        if diffs:
            raise scenario.ExpectFailed(
                "board_mismatch", FALSIFIERS["board_mismatch"] + " -- "
                + "; ".join(diffs), self.state, self.state)

    # ---------------------------------------------------- EB-170: modals ---

    def _operator_answer(self, screen: str, prompt: str
                         ) -> tuple[str, int] | None:
        """The first UNUSED `--answer` whose left side matches this prompt.

        Matched against the prompt text first and the screen's wire name
        second, so `--answer "Choose a card.=Deal 14 damage"` and
        `--answer "card_select=Deal 14 damage"` both work and an operator
        facing a screen that arrives with no prompt still has a handle.
        """
        used = {u["index"] for u in self.answers_used}
        want = (prompt or "").casefold()
        for i, (match, choice) in enumerate(self.answers):
            if i in used:
                continue
            m = match.casefold()
            if (want and m in want) or m == screen.casefold():
                return choice, i
        return None

    def _do_answer_modal(self, body: dict[str, Any]) -> None:
        """Close whatever prompt the play just raised, from the form's own
        words -- or STOP, naming the prompt.

        THE THREE OUTCOMES, and each is a row:
          * no screen is up -- `answered: false`, and the step is a no-op. This
            is the common case and it costs one GET.
          * a screen is up and somebody said what to pick -- the pick is posted
            through `scenario`'s own `select` / `confirm`, so the two screens'
            two different verb pairs are resolved in exactly one place.
          * a screen is up and nobody said -- `modal_unanswered`, naming the
            PROMPT and listing the offered text. Never a heuristic pick: the
            first offer, the biggest number and the cheapest card are all
            plausible guesses and all three would produce a post-state
            indistinguishable from a real replay.
        """
        # EACH KEY ANSWERS AT MOST ONE PROMPT PER PLAY. Without this, a screen
        # that failed to close would be answered with the same word forever --
        # the replayer would look like it was working while playing the same
        # pick over and over.
        used_keys: set[str] = set()
        for _ in range(MAX_MODALS_PER_PLAY):
            self.read()
            screen, blob = scenario._select_blob(self.state)
            if not screen:
                self.emit({"step": "answer_modal", "card": body.get("card"),
                           "answered": False, "screen": "",
                           "why": "no selection screen is up"})
                return
            prompt = str(blob.get("prompt") or "")
            offered = [c for c in (blob.get("cards") or [])
                       if isinstance(c, dict)] or scenario._hand(self.state)
            titles = [str(c.get("name") or c.get("id") or "") for c in offered]
            key = MODAL_KEY_FOR_SCREEN.get(screen, "")
            choice = (str(body.get(key) or "")
                      if key and key not in used_keys else "")
            source = "form"
            operator = None
            if not choice:
                operator = self._operator_answer(screen, prompt)
                if operator is not None:
                    choice, source = operator[0], "operator"
            if not choice:
                detail = (f"{FALSIFIERS['modal_unanswered']} -- screen "
                          f"{screen!r}, prompt {prompt!r}, offering {titles}. "
                          f"State it on the play as "
                          f"{key or 'exhaust/choose'!r}, in the printed "
                          f"vocabulary, or pass "
                          f"--answer \"{prompt or screen}=<printed choice>\"")
                self.emit({"step": "answer_modal", "card": body.get("card"),
                           "answered": False, "screen": screen,
                           "prompt": prompt, "offered": titles,
                           "rule": "modal_unanswered"})
                self.modals.append({"card": body.get("card"), "screen": screen,
                                    "prompt": prompt, "offered": titles,
                                    "answered": False, "source": "",
                                    "choice": ""})
                raise scenario.ExpectFailed("modal_unanswered", detail,
                                            self.state, self.state)
            if scenario.find_card(offered, choice) is None:
                raise scenario.ExpectFailed(
                    "modal_unanswered",
                    f"{choice!r} is not on the screen. Prompt {prompt!r} "
                    f"offers {titles}; an answer that is not on the table is "
                    f"not an answer", self.state, self.state)
            self.emit({"step": "answer_modal", "card": body.get("card"),
                       "answered": True, "screen": screen, "prompt": prompt,
                       "offered": titles, "choice": choice, "source": source})
            self.modals.append({"card": body.get("card"), "screen": screen,
                                "prompt": prompt, "offered": titles,
                                "answered": True, "source": source,
                                "choice": choice})
            if operator is not None:
                self.answers_used.append(
                    {"index": operator[1], "prompt": prompt,
                     "screen": screen, "choice": choice})
            used_keys.add(key)
            self._do_select({"cards": [choice]})
            self._do_confirm({})
        raise scenario.ExpectFailed(
            "modal_unanswered",
            f"one play raised more than {MAX_MODALS_PER_PLAY} prompts; the "
            f"replayer is not closing them and stops rather than spinning",
            self.state, self.state)


def _outcome(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """HP/Block/resource deltas across the graded line. DIAGNOSTIC ONLY."""
    def creature(d, key):
        return {"hp": (d.get(key) or {}).get("hp"),
                "block": (d.get(key) or {}).get("block")}

    enemies_before = {e["id"]: e for e in before.get("enemies") or []}
    enemies_after = {e["id"]: e for e in after.get("enemies") or []}
    return {
        "player": {"before": creature(before, "player"),
                   "after": creature(after, "player"),
                   "resources_before": (before.get("player") or {}).get("resources"),
                   "resources_after": (after.get("player") or {}).get("resources")},
        "enemies": [{"id": eid,
                     "name": enemies_before[eid].get("name"),
                     "hp_before": enemies_before[eid].get("hp"),
                     "hp_after": (enemies_after.get(eid) or {}).get("hp"),
                     "block_before": enemies_before[eid].get("block"),
                     "block_after": (enemies_after.get(eid) or {}).get("block")}
                    for eid in enemies_before],
        # GUARDRAIL-7, on the row and not in a header. These numbers exist to
        # catch a DEFECT -- a card that did not do what its face says when a
        # person's line played it. They are not a comparison, not a balance
        # reading, and not evidence about the turn.
        "reading": ("diagnostic only: a hand-set board, played once. A number "
                    "here is evidence of a DEFECT or of nothing at all"),
        "guardrail": qa_packet.PACKET_GUARDRAIL,
    }


# ------------------------------------------------------------------ main ---

def cmd_check(args) -> int:
    paths = [Path(args.file)] if args.file else all_turns()
    if not paths:
        print("no turn files found", file=sys.stderr)
        return 1
    bad = 0
    loaded: list[StagedTurn] = []
    for p in paths:
        try:
            t = load(p)
            face_defect_preflight(t)
            assumption_preflight(t)
            loaded.append(t)
            print(f"OK   {p.name}: id={t.id} {len(t.staging)} staging step(s), "
                  f"{len(t.board.hand)} card(s) in hand, "
                  f"{len(t.board.enemies)} enem(ies), "
                  f"{len(t.assumptions)} assumption(s)"
                  + (", exact_hand" if t.exact_hand else ""))
        except (TurnError, scenario.ScenarioError, yaml.YAMLError) as e:
            bad += 1
            print(f"BAD  {p.name}: {e}", file=sys.stderr)
    # EB-202. A slot's threshold against what its own board set can produce.
    # Checked over whole DIRECTORIES, because a round is a directory: checking
    # one file would compute a ceiling of one and pass everything.
    bad += slot_report(loaded)
    return 1 if bad else 0


def slot_report(turns: Sequence["StagedTurn"]) -> int:
    """Print each counting slot's ceiling. Returns the number unreachable.

    `slot_plan` is imported HERE: it reads the card sheets and this module
    builds the blind packet (see `SLOT_FILE_NAME`).
    """
    from understudy import slot_plan
    try:
        report, refusals = slot_plan.check_round(turns)
    except slot_plan.SlotError as exc:
        print(f"SLOTS BAD  {exc}", file=sys.stderr)
        return 1
    for row in report:
        mark = "OK  " if row["reachable"] else "LOW "
        print(f"SLOT {mark} {row['slot']}: threshold {row['threshold']}, "
              f"ceiling {row['ceiling']} of {row['boards']} board(s)"
              + (f"  [{', '.join(row['qualifying'])}]"
                 if row["qualifying"] else ""))
    for line in refusals:
        print(f"SLOT REFUSED  {line}", file=sys.stderr)
    return len(refusals)


def cmd_closeness(args) -> int:
    turn = load(args.file)
    observed = turn_dir(turn.id) / "observed.json"
    if args.observed and not observed.is_file():
        print(f"no observed board at {observed}; stage the turn first",
              file=sys.stderr)
        return 2
    if args.observed:
        result = closeness_observed(
            json.loads(observed.read_text(encoding="utf-8")),
            pilot=turn.board.pilot, prototype=turn.prototype)
    else:
        result = closeness(turn.board, prototype=turn.prototype)
    d = turn_dir(turn.id)
    d.mkdir(parents=True, exist_ok=True)
    (d / "closeness.json").write_text(
        json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(f"turn: {turn.id}   pilot: {turn.board.pilot}   "
          f"source: {result['source']}")
    print(f"GUARDRAIL: {qa_packet.PACKET_GUARDRAIL}")
    if not result["applicable"]:
        print(f"NOT READ: {result['reason']}")
        return 0
    print(f"gap {result['gap']:.4f}  (top1 {result['top1']:.3f}, "
          f"top2 {result['top2']:.3f}) over {result['lines_considered']} "
          f"line(s); DOMINANCE_GAP {DOMINANCE_GAP}")
    for line in result["lines"]:
        print(f"  {line['score']:8.3f}  {' + '.join(line['cards'])}")
    print(f"{result['verdict']}: {result['reason']}")
    for note in (result.get("observed_notes") or {}).get(
            "unmapped_resources") or []:
        print(f"  UNMAPPED RESOURCE (read as zero): {note}")
    print(f"closeness: {d / 'closeness.json'}")
    return 0


def cmd_stage(args) -> int:
    if not str(args.why).strip():
        print("stage needs a --why: it grants cards and writes a board",
              file=sys.stderr)
        return 2
    turn = load(args.file)
    # EB-169, and BEFORE the launch: `stage_board` boots the game.
    face_defect_preflight(turn)
    assumption_preflight(turn)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    log = scenario.LOG_DIR / f"staged-{turn.id}-{stamp}.jsonl"
    print(f"turn: {turn.id}  ({turn.character})")
    for a in turn.assumptions:
        print(f"  ASSUMES: {a}")
    print(f"GUARDRAIL: {bridge.GRANT_GUARDRAIL}")
    state, summary = stage_board(turn, args.why, hold=args.hold, out_path=log,
                                 seed=args.seed or None)
    # THE SEED THE GAME ACTUALLY USED, read back off the run rather than taken
    # from the request -- R95's rule, and the whole reason the packet can be
    # replayed at all. `--seed` re-stages a recorded board; with no `--seed`
    # the game rolls and this is where the roll is captured.
    report = export_packet(turn, state, run_seed=summary.get("seed"))
    print(f"\nlog:    {log}")
    print(f"packet: {report['packet_md']}")
    print(f"json:   {report['packet_json']}")
    print(f"sha256: {report['sha256']}")
    print(f"seed:   {report['run_seed']}"
          + ("  (as requested)" if args.seed else "  (game-generated)"))
    print(f"        {report['cards']} card(s) in hand, "
          f"{report['enemies']} enem(ies)")
    if args.hold:
        print("\nHOLDING: the game is still at the staged board.\n"
              "  Play the turn cold, then write your answers into a form "
              "(understudy/qa_form.md is the template) with\n"
              f"  grader.id = {USER_GRADER!r} and packet_sha256 = the hash "
              "above, and grade it with:\n"
              f"    python -m understudy.staged_turn grade {turn.id} "
              f"<your-form.json>")
    return 0


def cmd_grade(args) -> int:
    form = load_form(args.form)
    verdict = grade(args.turn_id, form)
    d = turn_dir(args.turn_id)
    d.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(verdict, indent=1) + "\n"
    name = f"verdict-{grader_id(form)}.json"
    (d / name).write_text(blob, encoding="utf-8")
    # The fixed path too: one turn has one verdict a reader can find without
    # knowing who graded it, and it is the most recent grade. The per-grader
    # copy beside it is what the ledger reads, so a second grader does not
    # erase the first.
    (d / "verdict.json").write_text(blob, encoding="utf-8")
    print(f"{verdict['verdict']}  {args.turn_id}  "
          f"(grader {grader_id(form)})")
    for reason in verdict["reasons"]:
        print(f"  REFUSED BY {reason}")
    # EB-203. The refusal names the play AND prints the hand's aimed cards --
    # half a message ("you played it at nobody") is not actionable by somebody
    # holding the page.
    targets = verdict.get("targets") or {}
    if "target_missing" in (verdict.get("refused_by") or []):
        for hit in targets.get("findings") or []:
            print(f"    play {hit['position']}: {hit['card']} takes a target "
                  f"and carried none")
        takes = targets.get("hand_takes_a_target") or []
        print(f"    cards in this hand that take a target: "
              f"{', '.join(takes) if takes else '(none)'}")
        print(f"    derived from {targets.get('derived_from')}")
    if verdict["verdict"] == "SURVIVES":
        print(f"  {verdict['survives_means']}")
        if not verdict["survives_alone"]:
            print(f"  NOT ALONE: {verdict['why_not_alone']}")
    print(f"verdict: {d / name}")
    return 0


def cmd_execute(args) -> int:
    if not str(args.why).strip():
        print("execute needs a --why: it grants cards and writes a board",
              file=sys.stderr)
        return 2
    from understudy import soak

    form = load_form(args.form)
    answers = parse_answers(getattr(args, "answer", None))
    path = next((p for p in all_turns() if load(p).id == args.turn_id), None)
    if path is None:
        print(f"no turn file with id {args.turn_id!r} under {TURN_DIR}",
              file=sys.stderr)
        return 2
    turn = load(path)
    d = turn_dir(turn.id)
    packet_json = d / "packet.json"
    if not packet_json.is_file():
        print(f"no packet at {packet_json}; stage the turn first",
              file=sys.stderr)
        return 2
    packet = json.loads(packet_json.read_text(encoding="utf-8"))

    # TWO REFUSALS BEFORE THE GAME IS EVEN LAUNCHED, and both are cheaper to
    # take here than to discover at the first play.
    given = str(form.get("packet_sha256") or "")
    if given and given != str(packet.get("packet_sha256") or ""):
        print(f"packet_mismatch: {FALSIFIERS['packet_mismatch']}\n"
              f"  form:   {given}\n"
              f"  packet: {packet.get('packet_sha256')}", file=sys.stderr)
        return 2
    seed = args.seed or packet.get("run_seed") or turn.seed
    if not seed:
        # THE ENCOUNTER IS GENERATED, so a replay with no seed is a replay
        # onto whatever the game felt like making. The first live `execute`
        # of this tool did exactly that and drew a different monster.
        print("no recorded run seed for this packet, so the encounter cannot "
              "be regenerated and a replay would be a replay of nothing. "
              "Re-stage the turn (a `stage` records the seed it ran on), or "
              "pass --seed.", file=sys.stderr)
        return 2

    stamp = time.strftime("%Y%m%d-%H%M%S")
    log = scenario.LOG_DIR / f"executed-{turn.id}-{stamp}.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)

    replay = scenario.Scenario(name=f"{turn.id}/executed",
                               character=turn.character,
                               steps=execute_steps(turn, form),
                               path=turn.path, seed=seed,
                               assumptions=turn.assumptions)
    print(f"turn: {turn.id}   grader: {grader_id(form)}   seed: {seed}")
    for match, choice in answers:
        print(f"  OPERATOR ANSWER: {match!r} -> {choice!r}")
    with log.open("w", encoding="utf-8") as fh:
        runner = ExecuteRunner(replay, args.why, out=fh, packet=packet,
                               answers=answers)
        runner.emit({"step": "execute_begin", "turn": turn.id,
                     "grader": grader_id(form), "seed_requested": seed,
                     "packet_sha256": packet.get("packet_sha256"),
                     "chosen_line": form.get("chosen_line"),
                     # EB-170. ON THE FIRST ROW OF THE LOG, so a reader who
                     # opens the replay learns before anything else that an
                     # answer came from the operator and not from the form.
                     "operator_answers": [{"match": m, "choice": c}
                                          for m, c in answers]})
        policy = scenario.ScenarioPolicy(runner, turns=1)
        summary = soak.run_scripted(policy, stamp, character=turn.character,
                                    max_fights=1, chosen_seed=seed,
                                    do_setup=not args.no_setup)
        # THE BRACKET IS THE WHOLE LINE, not the last play. `Runner.before`
        # is reset by every action step, so reading it here would report the
        # final card's own delta and call it the turn's. The `mark` step
        # emitted the board as it stood when the line began; that row is the
        # left-hand side.
        marks = [r for r in runner.rows if r.get("step") == "mark"]
        outcome = _outcome(marks[-1]["at"] if marks
                           else scenario.digest(runner.before),
                           scenario.digest(runner.state))
        runner.emit({"step": "execute_end", "ok": policy.ok,
                     "seed_used": summary.get("seed"),
                     "outcome": outcome, "run": summary})

    # `"ok" in r` AND NOT `step == "board_check"` ALONE. When the check fails,
    # `Runner.run` emits a SECOND row under the same step name -- its generic
    # `expect_failed` record, which carries no `ok` key -- and taking the last
    # row by step name picked that one and raised a KeyError while reporting
    # the very failure it was reporting. The failure row is still the source of
    # the difference, so it is read for its detail rather than dropped.
    checks = [r for r in runner.rows
              if r.get("step") == "board_check" and "ok" in r]
    failures = [r for r in runner.rows
                if r.get("step") == "board_check" and r.get("expect_failed")]
    if checks:
        board_check = checks[-1]
    elif failures:
        board_check = {"ok": False, "rule": failures[-1]["expect_failed"],
                       "differences": [failures[-1].get("detail", "")]}
    else:
        board_check = {"ok": False,
                       "differences": ["the board check was never reached"]}
    record = {
        "turn_id": turn.id,
        "grader": grader_id(form),
        # WHICH GAME REPLAYED IT. Two lanes replay two boards at once; a
        # record that does not say which process ran cannot be matched to a
        # log, a frame or a crash.
        "instance": bridge.current_label(),
        "packet_sha256": packet.get("packet_sha256"),
        "seed_requested": seed,
        "seed_used": summary.get("seed"),
        "seed_honoured": summary.get("seed") == seed,
        "board_check": board_check,
        "chosen_line": list(form.get("chosen_line") or []),
        "played": [r.get("step") for r in runner.rows
                   if str(r.get("step", "")).startswith("play ")],
        # EB-170. Every prompt the line met, whether it was answered, and by
        # WHOM -- `form` for the grader's own words, `operator` for an answer
        # read off the grader's q1 prose and stated on the command line.
        "modals": list(runner.modals),
        "operator_answers": [{"match": m, "choice": c} for m, c in answers],
        "operator_answers_used": list(runner.answers_used),
        "ok": bool(policy.ok),
        "failures": runner.failures,
        "outcome": outcome,
        "reading": ("diagnostic only, under Guardrail-7: a hand-set board "
                    "played once. A number here is evidence of a DEFECT or "
                    "of nothing at all -- never a comparison, never a "
                    "balance reading, and never a claim about the turn"),
        "guardrail": qa_packet.PACKET_GUARDRAIL,
        "log": str(log),
        "executed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    out_path = d / f"execute-{grader_id(form)}.json"
    out_path.write_text(json.dumps(record, indent=1, default=str) + "\n",
                        encoding="utf-8")
    print(f"log:    {log}")
    print(f"record: {out_path}")
    print(f"seed:   requested {seed}, ran {summary.get('seed')}")
    print("board:  " + ("MATCHES the packet" if board_check["ok"]
                        else "MISMATCH -- refused"))
    for diff in board_check["differences"]:
        print(f"        {diff}")
    for m in runner.modals:
        print(f"modal:  {m['screen']} {m['prompt']!r} -> "
              + (f"{m['choice']!r} ({m['source']})" if m["answered"]
                 else "UNANSWERED"))
    print(json.dumps(outcome, indent=1))
    return 0 if policy.ok else 1


def cmd_packet_section(args) -> int:
    """R221 item (4): the round's results block, written from the records."""
    from understudy import packet_section
    text = packet_section.render(args.slug, heading=args.heading or "")
    # The section quotes packet prose, and a packet is UTF-8. A Windows
    # console defaults to cp1252 and would raise on the first em-dash it was
    # handed, which is a generator that works on one operator's machine.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    sys.stdout.write(text)
    if args.write:
        out = packet_section.append_to(Path(args.write), text)
        print(f"appended to: {out}", file=sys.stderr)
    return 0


def cmd_ledger(args) -> int:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    text = build_ledger()
    with LEDGER_LOCK:
        LEDGER.write_text(text, encoding="utf-8")
    print(text, end="")
    print(f"\nledger: {LEDGER}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="parse only; no game involved")
    c.add_argument("file", nargs="?", default="")
    c.set_defaults(func=cmd_check)

    cl = sub.add_parser("closeness", help="the R213 F falsifier; no game")
    cl.add_argument("file")
    cl.add_argument("--observed", action="store_true",
                    help="read the board the grader actually saw, from the "
                         "observed.json a previous `stage` wrote, instead of "
                         "the file's declared mirror. The live board is the "
                         "one with the game's own opening hand in it")
    cl.set_defaults(func=cmd_closeness)

    s = sub.add_parser("stage", help="set the board and export a blind packet")
    s.add_argument("file")
    s.add_argument("--why", default="",
                   help="one line, logged on every row. REQUIRED")
    s.add_argument("--seed", default="",
                   help="re-stage a RECORDED board. The encounter is "
                        "generated from the run seed, so this is what makes "
                        "a packet reproducible; with no --seed the game rolls "
                        "and the roll is recorded into packet.json")
    s.add_argument("--hold", action="store_true",
                   help="leave the game at the staged board for a human to "
                        "play cold. Attaches to a game that is already up, "
                        "because a session that owns the launch kills it at "
                        "teardown")
    s.set_defaults(func=cmd_stage)

    g = sub.add_parser("grade", help="apply the falsifier rules to one form")
    g.add_argument("turn_id")
    g.add_argument("form")
    g.set_defaults(func=cmd_grade)

    e = sub.add_parser("execute", help="replay a graded line live")
    e.add_argument("turn_id")
    e.add_argument("form")
    e.add_argument("--why", default="")
    e.add_argument("--seed", default="",
                   help="override the seed recorded in packet.json. Normally "
                        "unnecessary and normally wrong")
    e.add_argument("--answer", action="append", default=[],
                   metavar="PROMPT=CHOICE",
                   help="EB-170. THE OPERATOR'S OWN ANSWER to a modal prompt "
                        "the form did not carry, for replaying a form written "
                        "before the `exhaust` / `choose` keys existed. The "
                        "left side matches the prompt text (or the screen "
                        "name); the right side is the PRINTED choice. Logged "
                        "as `source: operator` on the row and in the record, "
                        "never silently, and never over a form's own answer. "
                        "Repeatable; each is consumed at most once")
    e.add_argument("--no-setup", action="store_true")
    e.set_defaults(func=cmd_execute)

    ps = sub.add_parser("packet-section",
                        help="write a round's results block FROM the records")
    ps.add_argument("slug", help="the round's slug -- the records are "
                                 "review/qa/<slug>-t*/")
    ps.add_argument("--write", default="",
                    help="also APPEND the section to this packet file")
    ps.add_argument("--heading", default="",
                    help="override the section heading")
    ps.set_defaults(func=cmd_packet_section)

    ld = sub.add_parser("ledger", help="rebuild review/qa/ledger.tsv")
    ld.set_defaults(func=cmd_ledger)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except (TurnError, FormError, scenario.ScenarioError,
            qa_packet.PacketLeak, yaml.YAMLError) as exc:
        print(f"staged turn error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
