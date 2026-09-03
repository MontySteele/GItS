"""What a staged turn IS: the two refusals, the board, the turn.

Cut out of `staged_turn.py` by `EB-180`: `TurnError`, `FormError`,
`Board` and `StagedTurn`, moved whole and re-exported, so
`staged_turn.TurnError` and `staged_turn.Board(...)` still resolve.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from understudy import scenario


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
    # `EB-240`. THE STRUCTURED HALF OF `assumptions:`, AND THE ONLY HALF A
    # MACHINE CAN CHECK. Every `KLEESPARK-BT2` board asserted in prose that
    # *"the run carries Klee's starting relic and no other"* while the page
    # printed TWO, and every board declared `set_hp: {who: first, amount: 55}`
    # against live bodies of 45, 46 and 40. Neither moved a grade -- the
    # second relic is inert in combat, and the largest line was 40 against 45
    # so *no lethal line* held by 5 -- and both were false as printed, in a
    # block the packet reproduces for the reader verbatim.
    #
    # THE ENGLISH IS NOT PARSED AND NEVER WILL BE: a preflight that reads
    # prose is a preflight that is wrong in a new way on every board. A board
    # that wants a wire fact CHECKED declares it here, in a shape with one
    # meaning, and the stage REFUSES on a mismatch. Absent on every board
    # written before this key existed, and absent is not a failure -- it is
    # the same board it always was, with the automatic `set_hp` read-back as
    # its only check, which costs nothing to declare because the `set_hp`
    # step already declared it.
    expects: dict[str, Any] = field(default_factory=dict)

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
