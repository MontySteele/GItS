"""THE LOCAL TESTER SEAT: the local model READS a staged turn, on conditions.

[USER], 2026-08-29: *"Ask GPT for confirmation on the playtest findings ... and
if they agree, then we can hand off playtesting to Qwen."* The Codex seat
answered **ADVANCE, for the staged single-turn tester seat only**, and attached
four conditions in its own words:

  1. keep `answer_truncated` as a hard refusal with no partial filing;
  2. keep the family non-authorable under `M53`;
  3. retain periodic review by this seat;
  4. require review of any reading whose ordered line changes a resource
     before a later resource-dependent play.

*"Grader work, whole-fight blind play, and the doctrine gate remain with this
seat. This is only advancement to whole-fight questioning, not validation,
balance evidence, or ship approval."* This module is that scope and those four
conditions, and it is deliberately the only place they live.

TESTER, NOT GRADER, AND THE SPLIT IS THE FUNNEL'S OWN
------------------------------------------------------
`understudy/staged_turn.py` already draws the line this seat's ruling draws.
The TESTER is the reader who fills the form: it looks at `packet.md`, picks a
line and answers four questions in prose. The GRADE is what
`staged_turn.grade` then does to that form -- the falsifiers, mechanically,
with no model in the loop. So "the local model takes the tester role" is a
statement about which artifact it produces (`form-local-<slug>.json`) and not
a new pipeline: the form goes to the same `staged_turn grade`, and
`verdict-local-<slug>.json` is a falsifier's output, not a second opinion.

`understudy/local_seat.py` is the transport, unchanged and still shared: the
same prompt (through `seat.build_prompt`, so the two seats cannot drift), the
same `packet_sha256` pin, the same refusals in the same order. What is added
here is everything that happens AFTER the reply -- the record that says whose
testimony this is, the two post-read checks, and the routing decision.

WHAT THE RECORD SAYS, AND WHY IT SAYS IT OUT LOUD
--------------------------------------------------
`tester-local-<slug>.json` carries `tester_family: "local"` and
`role: "tester"` as literal fields, beside the `local:` prefixed model string
the form itself carries. A later reader must be able to tell whose testimony a
form is WITHOUT resolving a family out of a model name, and without knowing
that this module exists. The guardrail and the blindness sentence travel in
the record for the same reason a file outlives a conversation.

WHAT THIS SEAT STILL MAY NOT DO. It may not author a row (`authorship.py`'s
`AUTHORABLE_FAMILIES` is closed at two and `M53` keeps it there), it is not
the doctrine gate, it does not play a whole fight, and nothing it produces is
validation, balance evidence or ship approval.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import threading
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from understudy import bridge, local_model, local_seat

REPO = Path(__file__).resolve().parents[1]
QA_DIR = REPO / "review" / "qa"

ROLE = "tester"
TESTER_FAMILY = "local"

# R221 A / pick 4(e). THE LOCAL SEAT'S CHAIR, AND IT IS NOW THE SHADOW ONE.
#
# The calibration arm was measured on `KLEESPARK-R1` at 4 of 8 verdict
# agreement, and the fresh-Opus control STANDS under every option on `M62`.
# A seat that agrees with the control half the time cannot be the read a round
# is decided on while the control is still riding every packet -- so the
# default flips: the local seat READS every packet, its form and record are
# written under the usual names, and neither is the deciding verdict and
# neither is replayed. The fresh-Opus form is the deciding tester and it is
# what `execute` replays.
#
# `deciding` restores today's behaviour exactly, and it is the mode a round
# runs in the day `M62` retires the control. Nothing else about the seat
# changes between the two: the same prompt, the same refusals, the same
# post-read checks, the same routing to the Codex seat.
SEAT_MODES: tuple[str, ...] = ("shadow", "deciding")
DEFAULT_SEAT_MODE = "shadow"
SHADOW_ROLE = "shadow"

# A form that is NOT the local seat's. `form-raw-*` is the unparsed reply the
# local wrapper keeps beside the form it recovered, so it is excluded by name
# rather than by family -- it is the same seat's text, twice.
DECIDING_FORM_GLOB = "form-*.json"
_NOT_DECIDING = ("form-local-", "form-raw-")

# CONDITION 3, as a number. A round of this funnel has run between 4 and 11
# turns (klee slice 1 r3 = 4, kokomi slice 2 = 8, kokomi slice 1 = 11), so a
# rate has to give a short round at least one seat read and a long one a
# handful without spending the round's whole Codex budget. The rule is turn 1
# and every Nth after it -- `(position - 1) % N == 0`, one-based -- which at
# N=4 is one read on a 4-turn round and three on an 11-turn round, about a
# quarter of the round either way and NEVER zero. The value is [USER]'s to
# ratify; the mechanism does not care what it is.
DEFAULT_SPOT_CHECK = 4

GUARDRAIL = (
    "a local model in the TESTER chair produces SUBJECTIVE FEEDBACK on one "
    "staged turn. It is not human validation, not balance evidence, not ship "
    "approval, and not a grade -- `staged_turn grade` is the grade. Grader "
    "work, whole-fight blind play and the doctrine gate stay with the Codex "
    "seat (its 2026-08-29 ADVANCE, in its own words)"
)

# Why a turn goes back to the Codex seat. Named rather than boolean, because
# "this one was reviewed" and "this one HAD to be reviewed" are different
# facts about a round and a later reader needs both.
REVIEW_REASONS = {
    "spot_check": "the periodic seat review the ADVANCE requires -- this "
                  "turn's position in the round fell on the rate",
    "resource_order": "the ordered line changes a resource before a later "
                      "play that reads it, which the ADVANCE requires a seat "
                      "to read regardless of the rate",
    "misread": "a post-read check found a claim the packet contradicts",
    "local_read_refused": "the local tester refused or produced no form, so "
                          "the turn has no reading at all yet",
}


class LocalTesterError(RuntimeError):
    """The tester seat could not be set up."""


# ---------------------------------------------------------- condition (c) --

def spot_check_due(position: int, rate: int = DEFAULT_SPOT_CHECK) -> bool:
    """Is the `position`-th local-tested turn of a round also a seat read?

    One-based, and turn 1 always is: a rate that could leave a whole short
    round unreviewed is not "periodic review by this seat", it is a rate with
    a hole in it. `rate <= 0` disables the periodic half entirely -- the
    resource-order route still fires, because that one is not a rate.
    """
    if rate <= 0:
        return False
    return position >= 1 and (position - 1) % rate == 0


# ------------------------------------------------------------- the verb ----

def read_turn(turn_id: str, *, client: local_model.Client,
              qa_dir: Path | None = None,
              land_dir: Path | None = None,
              log_root: Path | None = None,
              tester_id: str = "",
              position: int = 1,
              spot_check: int = DEFAULT_SPOT_CHECK,
              seat_mode: str = DEFAULT_SEAT_MODE,
              dry_run: bool = False) -> dict[str, Any]:
    """One staged turn, READ by the local model in the tester role.

    Returns the tester record. `land_dir` splits read from write exactly as
    `local_seat.grade_turn` does, and for the same reason: a re-read of closed
    work lands somewhere else and leaves the closed directory byte-clean
    (R101b).
    """
    if seat_mode not in SEAT_MODES:
        raise LocalTesterError(
            f"unknown seat mode {seat_mode!r}; the local seat has two chairs "
            f"and they are not interchangeable: {', '.join(SEAT_MODES)}")
    blob = local_seat.grade_turn(turn_id, client=client,
                                 grader_id=tester_id, qa_dir=qa_dir,
                                 land_dir=land_dir, log_root=log_root,
                                 dry_run=dry_run)
    record = _record(turn_id, blob, position=position, spot_check=spot_check,
                     seat_mode=seat_mode)

    if blob.get("refused") or dry_run or not blob.get("form"):
        if blob.get("refused"):
            _route(record, "local_read_refused")
        return _land(record, blob, land_dir, qa_dir, turn_id)

    _stamp_form(blob["form"], record["role"], seat_mode)
    form = json.loads(Path(blob["form"]).read_text(encoding="utf-8"))
    _post_read(record, form, turn_id, qa_dir)
    return _land(record, blob, land_dir, qa_dir, turn_id)


def _stamp_form(path: str | Path, role: str, seat_mode: str) -> None:
    """Write the chair onto the FORM as well as the record.

    The form travels on its own -- into a packet's appendix, into a ledger
    rebuild, into somebody's diff six months later -- and "whose reading is
    this, and was it the deciding one" has to be answerable from the file in
    hand. Added AFTER the model replied and outside every hashed surface: the
    packet hash is what the form is answered against and it is untouched, and
    `staged_turn.load_form` ignores keys it does not require, so a stamped
    form loads and grades exactly as an unstamped one.
    """
    p = Path(path)
    try:
        blob = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    if not isinstance(blob, dict):
        return
    blob["role"] = role
    blob["seat_mode"] = seat_mode
    p.write_text(json.dumps(blob, indent=1) + "\n", encoding="utf-8")


def _record(turn_id: str, blob: Mapping[str, Any], *, position: int,
            spot_check: int,
            seat_mode: str = DEFAULT_SEAT_MODE) -> dict[str, Any]:
    record: dict[str, Any] = {
        "turn_id": turn_id,
        # `shadow` in the shadow chair, and the historical `tester` in the
        # deciding one -- an old record read beside a new one must not have to
        # be told which chair the seat was in when there was only one.
        "role": SHADOW_ROLE if seat_mode == SHADOW_ROLE else ROLE,
        "seat_mode": seat_mode,
        "deciding": seat_mode != SHADOW_ROLE,
        "tester_family": TESTER_FAMILY,
        "tester_id": blob.get("grader_id", ""),
        "model_requested": blob.get("model_requested", ""),
        "model_observed": blob.get("model_observed", ""),
        "temperature": blob.get("temperature"),
        "max_tokens": blob.get("max_tokens"),
        "packet_sha256": blob.get("packet_sha256", ""),
        "prompt_sha256": blob.get("prompt_sha256", ""),
        "session": blob.get("session", ""),
        "form": blob.get("form", ""),
        "refused": blob.get("refused", ""),
        "refused_why": blob.get("refused_why", ""),
        "read_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "position_in_round": position,
        # WHICH LANE READ IT. The read itself is model-bound and touches no
        # game, but the BOARD it reads was staged by one particular process,
        # and a record that cannot be matched to that process cannot be
        # matched to its log or its frames either.
        "instance": bridge.current_label(),
        "seat_spot_check_rate": spot_check,
        "resource_order_flag": [],
        "resource_order": {},
        "misreads": [],
        "seat_review_required": False,
        "seat_review_reasons": [],
        "blindness": blob.get("blindness", ""),
        "guardrail": GUARDRAIL,
        "scope": ("staged single-turn reads only; grader work, whole-fight "
                  "blind play and the doctrine gate remain with the Codex "
                  "seat"),
    }
    if spot_check_due(position, spot_check):
        _route(record, "spot_check")
    return record


def _post_read(record: dict[str, Any], form: Mapping[str, Any],
               turn_id: str, qa_dir: Path | None) -> None:
    """The two deterministic checks, on the form the model just filed.

    Imported HERE rather than at module scope on purpose. `resource_order`
    reads a DESIGN SHEET, and this module also builds the blind prompt (via
    `local_seat`); a sheet reader at module scope would be one refactor away
    from being in scope where the packet is built. It runs after the reply, on
    the record, and it stays that way.
    """
    from understudy import misreads as misread_checks
    from understudy import resource_order, staged_turn

    line = list(form.get("chosen_line") or [])
    summary = resource_order.summary(line)
    record["resource_order"] = summary
    record["resource_order_flag"] = summary["findings"]
    if summary["flagged"]:
        _route(record, "resource_order")

    packet = (qa_dir or QA_DIR) / turn_id / "packet.md"
    if packet.is_file():
        hits = misread_checks.misreads(
            packet.read_text(encoding="utf-8"),
            misread_checks.prose_of(form, staged_turn.QUESTIONS))
        record["misreads"] = hits
        if hits:
            _route(record, "misread")


def _route(record: dict[str, Any], reason: str) -> None:
    record["seat_review_required"] = True
    if reason not in record["seat_review_reasons"]:
        record["seat_review_reasons"].append(reason)
    record.setdefault("seat_review_why", {})[reason] = REVIEW_REASONS[reason]


def _land(record: dict[str, Any], blob: Mapping[str, Any],
          land_dir: Path | None, qa_dir: Path | None,
          turn_id: str) -> dict[str, Any]:
    home = land_dir or (qa_dir or QA_DIR) / turn_id
    home.mkdir(parents=True, exist_ok=True)
    name = f"tester-{record['tester_id'] or 'local-unknown'}.json"
    path = home / name
    path.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    record["record"] = str(path)
    return record


# ----------------------------------------------------------- the round -----

def plan_round(turn_ids: Sequence[str],
               rate: int = DEFAULT_SPOT_CHECK) -> list[dict[str, Any]]:
    """Which turns of a round the seat reads, BEFORE any of them are read.

    Committing the periodic half of the schedule up front is the same
    discipline a prediction slate carries: a rate chosen after the readings
    are in is not a rate, it is a selection.
    """
    return [{"turn_id": t, "position": i,
             "seat_spot_check": spot_check_due(i, rate)}
            for i, t in enumerate(turn_ids, 1)]


# ---------------------------------------- R221 B: the pre-registered order --

DEFAULT_FIRST = 4
COVER = 2          # "cover every registered slot AT LEAST TWICE"


def turn_index(turn_dir: Path | None = None) -> dict[str, Any]:
    """`turn id -> StagedTurn`, parsed once for the whole round."""
    from understudy import staged_turn
    out = {}
    for path in staged_turn.all_turns(turn_dir):
        try:
            turn = staged_turn.load(path)
        except Exception:                                     # noqa: BLE001
            continue
        out[turn.id] = turn
    return out


def closeness_gap(turn: Any) -> float:
    """The R213 F falsifier's gap, as a SORT KEY and nothing else.

    A smaller gap is a closer decision, and a closer decision is the more
    informative board -- which is what "ties by closeness score" means in the
    order. A board whose reading is not applicable sorts LAST rather than
    first: an unreadable score may not win a tie it cannot claim. Nothing here
    grades anything; closeness rates nothing (R213 F).
    """
    from understudy import staged_turn
    try:
        result = staged_turn.closeness(turn.board, prototype=turn.prototype)
    except Exception:                                         # noqa: BLE001
        return float("inf")
    if not result.get("applicable"):
        return float("inf")
    return float(result.get("gap", float("inf")))


def preregistered_order(turn_ids: Sequence[str], *,
                        turn_dir: Path | None = None,
                        turns: Mapping[str, Any] | None = None
                        ) -> list[dict[str, Any]]:
    """R221 B's order: the twice-over cover first, then the rest.

    Greedy, and deliberately so. The set-cover this needs is over four to
    eleven boards, so an exact solver would buy nothing a reader could check;
    a greedy pass that takes, at each step, the board covering the most
    still-uncovered slot-slots (ties to the closer decision, then to the id)
    is reproducible from the turn files alone, which is what "pre-registered"
    has to mean here -- somebody else must be able to derive the same order
    from the same files without running this code.
    """
    index = dict(turns or turn_index(turn_dir))
    rows = []
    for tid in turn_ids:
        turn = index.get(tid)
        slots = turn.registered_slots() if turn is not None else [tid]
        rows.append({"turn_id": tid, "slots": slots,
                     "closeness": (closeness_gap(turn) if turn is not None
                                   else float("inf")),
                     "seed": (getattr(turn, "seed", None) or "") if turn
                     else ""})

    # A slot carried by only ONE board cannot be covered twice, and a cover
    # target it can never meet would drag the whole order into the first set.
    # So the target is `min(COVER, boards carrying it)`: as much coverage as
    # exists, and no demand that cannot be met.
    carried: dict[str, int] = {}
    for r in rows:
        for s in r["slots"]:
            carried[s] = carried.get(s, 0) + 1
    need = {s: min(COVER, n) for s, n in carried.items()}

    order: list[dict[str, Any]] = []
    pool = list(rows)
    while pool:
        def gain(r):
            return sum(1 for s in r["slots"] if need.get(s, 0) > 0)
        pool.sort(key=lambda r: (-gain(r), r["closeness"], r["turn_id"]))
        pick = pool.pop(0)
        for s in pick["slots"]:
            if need.get(s, 0) > 0:
                need[s] -= 1
        order.append(pick)
    for i, row in enumerate(order, 1):
        row["order"] = i
    # How many of the order the twice-over cover actually needed: the prefix
    # after which no slot still wants a board.
    cover_size = 0
    want = {s: min(COVER, n) for s, n in carried.items()}
    for i, row in enumerate(order, 1):
        for s in row["slots"]:
            want[s] = max(0, want.get(s, 0) - 1)
        if not any(v > 0 for v in want.values()):
            cover_size = i
            break
    else:
        cover_size = len(order)
    for row in order:
        row["cover_size"] = cover_size
    return order


def split_first(order: Sequence[Mapping[str, Any]], first_n: int
                ) -> tuple[list[dict], list[dict]]:
    """`--first N`, raised where the twice-over cover needs more.

    `first_n <= 0` disables sequential stopping: every board is in the first
    set, which is the pre-R221 behaviour and stays reachable.
    """
    rows = [dict(r) for r in order]
    if first_n <= 0:
        return rows, []
    take = max(first_n, int(rows[0].get("cover_size", first_n)) if rows
               else first_n)
    return rows[:take], rows[take:]


def disk_grades(turn_ids: Sequence[str],
                qa_dir: Path | None = None) -> dict[str, list[str]]:
    """`turn id -> the grades on disk`, PRED for SURVIVES, MISS for REFUSED.

    Read off `verdict-<grader>.json`, which is `staged_turn.grade`'s
    mechanical output. The stopping rule never reads a FORM: it reads what the
    falsifiers said about one, so the reader was blind at read time either way
    and nothing here is a second opinion.
    """
    base = qa_dir or QA_DIR
    out: dict[str, list[str]] = {}
    for tid in turn_ids:
        got = []
        for path in sorted((base / tid).glob("verdict-*.json")):
            try:
                blob = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            got.append("PRED" if str(blob.get("verdict")) == "SURVIVES"
                       else "MISS")
        out[tid] = got
    return out


def slot_state(rows: Sequence[Mapping[str, Any]],
               grades: Mapping[str, Sequence[str]]) -> dict[str, str]:
    """DECIDED on two or more grades that ALL agree; UNDECIDED otherwise."""
    per_slot: dict[str, list[str]] = {}
    for row in rows:
        for slot in row["slots"]:
            per_slot.setdefault(slot, []).extend(grades.get(row["turn_id"], []))
    return {slot: ("DECIDED" if len(g) >= 2 and len(set(g)) == 1
                   else "UNDECIDED")
            for slot, g in per_slot.items()}


def split_rest(rest: Sequence[Mapping[str, Any]],
               state: Mapping[str, str]) -> tuple[list[dict], list[dict]]:
    """Of the boards left, which still carry an UNDECIDED slot.

    Evaluated ONCE, against the first set's grades, and not re-evaluated as
    the remainder runs. Re-reading the state after every board would make the
    stopping rule adaptive, which is the forking path R221 B closes by fixing
    the rule before any board is staged.
    """
    run, unrun = [], []
    for row in rest:
        undecided = [s for s in row["slots"]
                     if state.get(s, "UNDECIDED") == "UNDECIDED"]
        (run if undecided else unrun).append(
            {**row, "undecided_slots": undecided})
    return run, unrun


# --------------------------------- R221 items (3) and (5): the game lane ---
#
# ONE GAME PER ROUND, AND WHAT THAT COULD NOT BUY.
#
# [USER]: "3) yes, let's not have the game idle" and "5) Also agreed" (one
# launch per round). The first is buildable in full; the second is buildable
# only in part, and the part it cannot buy is a fact about the wire rather
# than about this file.
#
#   * `soak.Session` is what deploys `steam_appid.txt`, deploys the MCP
#     bridge, launches the process, waits for the menu, sets Instant speed and
#     writes the reversibility ledger. TODAY every `stage` and every `execute`
#     builds its own, so a round of eight turns pays that setup and its
#     teardown TWENTY-FOUR times -- twenty-four bridge deploys, twenty-four
#     removals, twenty-four speed captures. This lane opens ONE Session for
#     the whole round and hands every game step `do_setup=False`, which is
#     exactly `stage --hold`'s existing attach path. That part is real and it
#     is the bulk of the per-step overhead.
#
#   * IT STILL CANNOT AVOID RE-LAUNCHING THE PROCESS BETWEEN BOARDS, and the
#     reason is in `soak.RunDriver._to_main_menu`: a run starts from a MENU,
#     and anything else is `unexpected_start_state`, a stop-and-surface. A
#     staged board leaves the game mid-combat, and THE WIRE HAS NO IN-RUN
#     EXIT: `menu_select` is a menu verb, `abandon_run` is a MAIN-MENU option
#     (`McpMod.StateBuilder` builds it from `_abandonRunButton` on the main
#     screen), and no action in the vendored contract leaves a fight for the
#     menu. `Session.restart`'s own docstring says the same thing from the
#     other side: "a fresh process plus `abandon_run` is the only reliable way
#     back to the main menu". So the lane checks the screen before every game
#     step and restarts the PROCESS when it is not a menu -- keeping the
#     appid, the bridge deploy, the speed capture and the ledger from the one
#     Session, and recording every relaunch.
#
#   * Seed pinning is unaffected: the seed is fired at `_embark`, between the
#     character pick and the confirm, on every path -- attach included -- and
#     read back off the wire afterwards (R95). Nothing about attaching changes
#     which seed a board runs on.
#
# A round that ends with the game on a menu (a `--first N` stop, say) pays no
# relaunch at all for its last step.

MAX_RELAUNCH_PER_STEP = 1


class GameLane:
    """The ONE game a round launches, and the only thing that may touch it.

    Every game-bound step of the round goes through `step()`, which holds
    `self.lock` for its whole duration. That lock is the serialization the
    pipeline rests on: two `stage`s or a `stage` and an `execute` running at
    once would be two processes driving one game.
    """

    def __init__(self, *, session: Any = None, state_reader: Any = None,
                 clock: Any = None, log: Any = None,
                 instance: Any = None, label: str = ""):
        self.session = session
        self._state = state_reader
        self._clock = clock or time.monotonic
        self._log = log or (lambda _msg: None)
        # THE LANE'S OWN GAME. `None` is lane 0 -- the port and user tree the
        # funnel has always used -- so a one-lane round is unchanged.
        self.instance = (instance if instance is not None
                         else getattr(session, "instance", None))
        self.label = label or getattr(self.instance, "label", "lane0")
        self.lock = threading.Lock()
        self.events: list[dict[str, Any]] = []
        self.relaunches = 0
        self.launches = 0

    def bind(self) -> None:
        """Point the CALLING THREAD's bridge at this lane's game.

        `bridge`'s current-instance is thread-local, so every thread that
        will touch this lane's wire calls this once. A lane with no instance
        (the `--attach` path, and every existing test double) binds nothing
        and the thread keeps the process default.
        """
        if self.instance is not None:
            bridge.use(self.instance)

    # -- lifetime ---------------------------------------------------------
    def launch(self) -> None:
        self.bind()
        if self.session is not None:
            self.session.setup()
            self.launches += 1
            self._log(f"game[{self.label}]: launched once for the round")

    def close(self) -> None:
        self.bind()
        if self.session is not None:
            self.session.teardown()
            self._log(f"game[{self.label}]: torn down")

    # -- the one door -----------------------------------------------------
    def step(self, kind: str, turn_id: str, fn: Any) -> Any:
        with self.lock:
            self.bind()
            relaunched = self._ensure_menu()
            start = self._clock()
            try:
                return fn()
            finally:
                self.events.append({"kind": kind, "turn_id": turn_id,
                                    # ON EVERY EVENT ROW: with two lanes the
                                    # timings are interleaved, and a row that
                                    # does not say which game it is cannot be
                                    # read back into a per-lane wall clock.
                                    "instance": self.label,
                                    "start": start, "end": self._clock(),
                                    "relaunched": relaunched})

    def _ensure_menu(self) -> str:
        """Bring the game to a menu, restarting the process if it must."""
        if self.session is None or self._state is None:
            return ""
        relaunched = ""
        for attempt in range(MAX_RELAUNCH_PER_STEP + 1):
            try:
                state = self._state()
                screen = str((state or {}).get("state_type") or "")
            except Exception as exc:                          # noqa: BLE001
                screen, why = "", (f"the bridge did not answer ({exc}); the "
                                   f"game is treated as crashed")
            else:
                if screen == "menu":
                    # The REASON, not a boolean: the event row has to be able
                    # to say why a relaunch happened, and "it did" is not that.
                    return relaunched
                why = (f"the game is at {screen!r}, not a menu, and the wire "
                       f"has no in-run exit -- a fresh process plus "
                       f"abandon_run is the only way back")
            if attempt >= MAX_RELAUNCH_PER_STEP:
                raise LocalTesterError(
                    f"the game could not be brought to a menu after "
                    f"{self.relaunches} relaunch(es): {why}")
            self._log(f"game[{self.label}]: RELAUNCH -- {why}")
            self.session.restart()
            self.relaunches += 1
            self.launches += 1
            relaunched = why
        return relaunched                                     # unreachable


# --------------------------------------------------- R221 item (3): phases --

class RoundSteps:
    """The three things a round does to a board, as one injectable surface.

    Split out so the pipeline can be tested against a fake that sleeps instead
    of booting a game. The live implementation below drives the EXISTING
    verbs, argv and all: preserving `stage` / `grade` / `execute` exactly is
    what keeps every record format, file name and refusal identical to a
    serial round's.
    """

    def stage(self, row: Mapping[str, Any]) -> Any:            # pragma: no cover
        raise NotImplementedError

    def read(self, row: Mapping[str, Any]) -> dict[str, Any]:  # pragma: no cover
        raise NotImplementedError

    def execute(self, row: Mapping[str, Any],
                record: Mapping[str, Any]) -> Any:             # pragma: no cover
        raise NotImplementedError


def deal(rows: Sequence[Mapping[str, Any]], lane_count: int
         ) -> list[int]:
    """Which lane stages each board, in the PRE-REGISTERED ORDER.

    THE DEALING IS NOT A RE-ORDERING. R221 B's order is the order the boards
    are dealt IN, and it is unchanged by this build: board 1 goes to lane 0,
    board 2 to lane 1, board 3 back to lane 0, and so on. Two lanes change
    only WHICH PROCESS stages next, never which board is next.

    THE STOPPING RULE READS THE SAME GRADES WHICHEVER LANE PRODUCED THEM.
    `split_rest` and `slot_state` take grades off disk by turn id and slot;
    neither has, or wants, a lane term. A board's grade is a fact about the
    board, and the process that staged it is bookkeeping the record carries so
    a reader can find the log -- not an input to the decision.
    """
    return [i % max(1, int(lane_count)) for i in range(len(rows))]


def run_pipeline(rows: Sequence[Mapping[str, Any]], *,
                 lane: GameLane | None = None,
                 lanes: Sequence[GameLane] | None = None,
                 steps: RoundSteps,
                 serial: bool = False,
                 log: Any = None) -> list[dict[str, Any]]:
    """stage -> read -> grade -> execute, per turn, with no game ever idle.

    ONE OR TWO GAMES, ONE MODEL. Game-bound work (`stage`, `execute`) is
    serialized PER LANE by `GameLane.step`'s lock, so two boards never drive
    one process. The model-bound half (`read`, which ends in `staged_turn
    grade`) is serialized ACROSS lanes by `model_lock`: there is one local
    server, and two readings at once would queue inside it anyway while making
    the record's timings a lie about what the model did.

    So the win from a second lane is the game half -- staging and replaying
    two boards at once -- and it is stated that way rather than as a doubling.

    `lane=` (one lane) is kept for every existing caller; `lanes=` is the
    two-lane form. Passing both is an error rather than a merge.
    """
    log = log or (lambda _m: None)
    rows = list(rows)
    if lane is not None and lanes is not None:
        raise ValueError("pass lane= or lanes=, not both")
    pool = list(lanes) if lanes is not None else [lane or GameLane()]
    if not rows:
        return []
    assignment = deal(rows, len(pool))

    if serial:
        out = []
        for row, li in zip(rows, assignment):
            one = pool[li]
            one.step("stage", row["turn_id"], lambda r=row: steps.stage(r))
            record = steps.read(row)
            out.append(record)
            one.step("execute", row["turn_id"],
                     lambda r=row, rec=record: steps.execute(r, rec))
        return out

    records: dict[str, dict[str, Any]] = {}
    errors: list[BaseException] = []
    staged = [threading.Event() for _ in rows]
    model_lock = threading.Lock()

    def worker(i: int, row: Mapping[str, Any]) -> None:
        one = pool[assignment[i]]
        try:
            # LOOK-AHEAD OF EXACTLY ONE, PER LANE. Turn i's stage is
            # submitted only once the previous board ON ITS OWN LANE has
            # finished staging, so each game queue holds at most one
            # un-started stage and the interleave is the one R221 asks for:
            # a game stages the NEXT board while the model reads the last.
            # With one lane this is the previous board, unchanged.
            prev = i - len(pool)
            if prev >= 0:
                staged[prev].wait()
            if errors:
                return
            # The worker thread binds its own lane before it touches the wire:
            # `bridge`'s current-instance is thread-local exactly so these two
            # threads can hold two different ports at once.
            one.bind()
            one.step("stage", row["turn_id"], lambda: steps.stage(row))
            staged[i].set()
            with model_lock:
                record = steps.read(row)
            records[row["turn_id"]] = record
            one.step("execute", row["turn_id"],
                     lambda: steps.execute(row, record))
        except BaseException as exc:                          # noqa: BLE001
            errors.append(exc)
        finally:
            staged[i].set()

    threads = [threading.Thread(target=worker, args=(i, r), daemon=True,
                                name=f"round-{r['turn_id']}")
               for i, r in enumerate(rows)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    if errors:
        raise errors[0]
    return [records[r["turn_id"]] for r in rows if r["turn_id"] in records]


# ------------------------------------- pick 4(e): the two chairs, on disk --

def deciding_form(turn_id: str, qa_dir: Path | None = None) -> Path | None:
    """The form the round REPLAYS in shadow mode: the fresh-Opus control's.

    Found by elimination rather than by naming a model, because the deciding
    tester is whoever is not this seat: `form-local-*` is the shadow read and
    `form-raw-*` is the same reply unparsed. The newest of what is left wins,
    so a re-taken control form supersedes the one it replaced. `None` means
    the control has not been taken yet -- the board's replay is OWED, and a
    round says so rather than quietly replaying the shadow.
    """
    home = (qa_dir or QA_DIR) / turn_id
    if not home.is_dir():
        return None
    candidates = [p for p in home.glob(DECIDING_FORM_GLOB)
                  if not any(p.name.startswith(x) for x in _NOT_DECIDING)]
    if not candidates:
        return None
    return max(candidates, key=lambda p: (p.stat().st_mtime, p.name))


def _verdicts(turn_id: str, qa_dir: Path | None = None) -> dict[str, str]:
    """`{grader id: verdict}` from the per-grader verdicts on disk."""
    home = (qa_dir or QA_DIR) / turn_id
    out: dict[str, str] = {}
    for path in sorted(home.glob("verdict-*.json")):
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        gid = str((blob.get("grader") or {}).get("id")
                  or path.stem[len("verdict-"):])
        out[gid] = str(blob.get("verdict") or "")
    return out


def agreement(turn_ids: Sequence[str], *, shadow_ids: Mapping[str, str],
              qa_dir: Path | None = None) -> dict[str, Any]:
    """R221 A's per-turn agreement count, SHADOW against DECIDING.

    On the VERDICT and nothing else -- SURVIVES against SURVIVES, REFUSED
    against REFUSED -- which is what the ruling says and is deliberately not a
    prose comparison. A turn with only one of the two graded is not counted
    either way: an absent control is not a disagreement, exactly as an absent
    [USER] form is not one in `is_down_weighted`.

    `shadow_ids` maps a turn to the local seat's grader id, so the counter
    never has to guess which of two verdicts on a board is this seat's.
    """
    rows = []
    for tid in turn_ids:
        verdicts = _verdicts(tid, qa_dir)
        sid = shadow_ids.get(tid, "")
        shadow = verdicts.get(sid, "")
        others = {g: v for g, v in verdicts.items() if g != sid}
        # The deciding verdict is the one belonging to the deciding form.
        form = deciding_form(tid, qa_dir)
        deciding_gid = ""
        if form is not None:
            try:
                deciding_gid = str((json.loads(
                    form.read_text(encoding="utf-8")).get("grader")
                    or {}).get("id") or "")
            except (OSError, ValueError):
                deciding_gid = ""
        deciding = others.get(deciding_gid, "")
        if not deciding and len(others) == 1:
            deciding_gid, deciding = next(iter(others.items()))
        rows.append({"turn_id": tid, "shadow_grader": sid,
                     "shadow_verdict": shadow,
                     "deciding_grader": deciding_gid,
                     "deciding_verdict": deciding,
                     "comparable": bool(shadow and deciding),
                     "agree": bool(shadow and deciding
                                   and shadow == deciding)})
    compared = [r for r in rows if r["comparable"]]
    return {
        "rule": ("R221 A: agreement is counted per TURN, on the verdict -- "
                 "SURVIVES against SURVIVES or REFUSED against REFUSED. It is "
                 "not a prose comparison and does not pretend to be one"),
        "turns": rows,
        "compared": len(compared),
        "agreed": sum(1 for r in compared if r["agree"]),
        "criterion_owner": ("M62 -- the criterion that retires the fresh-Opus "
                            "control is [USER]'s and is not set here"),
    }


def round_slug(turn_ids: Sequence[str]) -> str:
    """`klee-sparks-r1` out of `klee-sparks-r1-t01…t08`. The round's own name."""
    if not turn_ids:
        return "round"
    head = str(turn_ids[0])
    for tid in turn_ids[1:]:
        while head and not str(tid).startswith(head):
            head = head[:-1]
    trimmed = re.sub(r"-t\d*$", "", head).rstrip("-")
    return trimmed or str(turn_ids[0])


def round_summary(records: Sequence[Mapping[str, Any]], *,
                  seat_mode: str, unrun: Sequence[Mapping[str, Any]] = (),
                  replays: Sequence[Mapping[str, Any]] = (),
                  qa_dir: Path | None = None) -> dict[str, Any]:
    """The round's own record, including the agreement M62 will be read off."""
    ids = [str(r["turn_id"]) for r in records]
    shadow_ids = {str(r["turn_id"]): str(r.get("tester_id") or "")
                  for r in records}
    return {
        "round": round_slug(ids),
        "seat_mode": seat_mode,
        "turns": ids,
        "unrun": [str(r.get("turn_id") or "") for r in unrun],
        "replays": list(replays),
        "seat_review_owed": round_queue(records),
        "agreement": agreement(ids, shadow_ids=shadow_ids, qa_dir=qa_dir),
        "written_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def write_round_summary(summary: Mapping[str, Any],
                        qa_dir: Path | None = None) -> Path:
    base = qa_dir or QA_DIR
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"{summary['round']}-round-summary.json"
    path.write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    return path


def round_queue(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """The turns this round owes the Codex seat, with the reason for each."""
    return [{"turn_id": r["turn_id"],
             "reasons": list(r.get("seat_review_reasons") or []),
             "command": f"python -m understudy.seat grade {r['turn_id']}"}
            for r in records if r.get("seat_review_required")]


# ------------------------------------------------------------------ CLI ----

def _client(args) -> local_model.Client:
    client = local_model.Client.from_env()
    if args.model:
        client.model = args.model
    return client


def cmd_read(args) -> int:
    try:
        client = _client(args)
    except local_model.LocalModelError as exc:
        print(f"local tester: {exc}", file=sys.stderr)
        return 2
    try:
        record = read_turn(args.turn_id, client=client,
                           tester_id=args.tester_id,
                           position=args.position,
                           spot_check=args.seat_spot_check,
                           seat_mode=args.seat_mode,
                           log_root=Path(args.log_root) if args.log_root
                           else None,
                           dry_run=args.dry_run)
    except (LocalTesterError, local_seat.LocalSeatError,
            local_model.LocalModelError) as exc:
        print(f"local tester: {exc}", file=sys.stderr)
        return 2

    _print(record)
    if record["refused"]:
        return 1
    if args.dry_run:
        return 0
    from understudy import staged_turn
    return staged_turn.main(["grade", args.turn_id, str(record["form"])])


class LiveSteps(RoundSteps):
    """The three phases, driven through the EXISTING verbs and their argv.

    `stage` and `execute` are `staged_turn`'s own subcommands with `--hold` /
    `--no-setup`, which is the attach path the lane's one Session needs; the
    grade is `staged_turn grade`, unchanged and still the only grade. Calling
    the CLI rather than reaching into the functions is deliberate: every
    record format, file name, refusal and printed line is then identical to a
    serial round's by construction rather than by inspection.
    """

    def __init__(self, *, client, why: str, spot_check: int,
                 log_root: Path | None = None,
                 seat_mode: str = DEFAULT_SEAT_MODE):
        self.client = client
        self.why = why
        self.spot_check = spot_check
        self.log_root = log_root
        self.seat_mode = seat_mode
        # What each board was replayed FROM, so the round summary can say it.
        self.replays: list[dict[str, Any]] = []

    def stage(self, row: Mapping[str, Any]) -> None:
        from understudy import staged_turn
        argv = ["stage", str(row["path"]), "--why", self.why, "--hold"]
        if row.get("seed"):
            argv += ["--seed", str(row["seed"])]
        rc = staged_turn.main(argv)
        if rc != 0:
            raise LocalTesterError(
                f"staging {row['turn_id']} failed (exit {rc}); the round "
                f"stops rather than reading a board nobody set")

    def read(self, row: Mapping[str, Any]) -> dict[str, Any]:
        from understudy import staged_turn
        record = read_turn(row["turn_id"], client=self.client,
                           position=row["position"],
                           spot_check=self.spot_check,
                           seat_mode=self.seat_mode,
                           log_root=self.log_root)
        _print(record)
        # THE GRADE STILL RUNS IN BOTH CHAIRS. `staged_turn grade` is a
        # falsifier, not an opinion, and a shadow read with no verdict beside
        # it could not be compared with the control at all -- which is the one
        # thing the shadow chair exists to make possible. What the shadow read
        # does NOT get is the replay and the deciding column.
        if not record.get("refused") and record.get("form"):
            staged_turn.main(["grade", row["turn_id"], str(record["form"])])
        return record

    def execute(self, row: Mapping[str, Any],
                record: Mapping[str, Any]) -> None:
        """Replay the DECIDING line, which in shadow mode is not this seat's."""
        from understudy import staged_turn
        tid = row["turn_id"]
        if self.seat_mode == SHADOW_ROLE:
            form = deciding_form(tid)
            if form is None:
                self.replays.append({"turn_id": tid, "replayed": False,
                                     "form": "",
                                     "why": ("shadow mode: the deciding "
                                             "(fresh-Opus) form has not been "
                                             "taken yet, and the shadow read "
                                             "is never replayed")})
                print(f"  {tid}: NO DECIDING FORM yet -- the replay is OWED. "
                      f"The shadow read is never replayed (pick 4(e)).")
                return
            self.replays.append({"turn_id": tid, "replayed": True,
                                 "form": str(form), "role": "deciding"})
            staged_turn.main(["execute", tid, str(form),
                              "--why", self.why, "--no-setup"])
            return
        if record.get("refused") or not record.get("form"):
            print(f"  no form for {tid}; nothing to replay")
            self.replays.append({"turn_id": tid, "replayed": False,
                                 "form": "", "why": "no form"})
            return
        self.replays.append({"turn_id": tid, "replayed": True,
                             "form": str(record["form"]), "role": "deciding"})
        staged_turn.main(["execute", tid, str(record["form"]),
                          "--why", self.why, "--no-setup"])


def _print_plan(first, rest, rate: int, lane_count: int = 1) -> None:
    print(f"round of {len(first) + len(rest)} board(s) in R221 B's "
          f"pre-registered order; seat spot-check every {rate or 'never'}; "
          f"first set = {len(first)}; lanes = {lane_count}")
    if lane_count > 1:
        print("  the ORDER is unchanged: lanes decide which process stages "
              "next, never which board is next, and the stopping rule reads "
              "the same grades whichever lane produced them")
    all_rows = list(first) + list(rest)
    where_first = deal(first, lane_count)
    where_rest = deal(rest, lane_count)
    for row, li in zip(all_rows, list(where_first) + list(where_rest)):
        mark = "SEAT" if row["seat_spot_check"] else "    "
        where = "FIRST" if row in first else "  ..."
        gap = ("n/a" if row["closeness"] == float("inf")
               else f"{row['closeness']:.3f}")
        print(f"  {row['position']:>2}  {where}  {mark}  lane{li}  "
              f"{row['turn_id']}"
              f"   slots={','.join(row['slots'])}  closeness={gap}")


def cmd_round(args) -> int:
    from understudy import staged_turn
    index = turn_index()
    order = preregistered_order(args.turn_ids, turns=index)
    first, rest = split_first(order, args.first)
    for i, row in enumerate(list(first) + list(rest), 1):
        row["position"] = i
        row["seat_spot_check"] = spot_check_due(i, args.seat_spot_check)
        turn = index.get(row["turn_id"])
        row["path"] = str(getattr(turn, "path", "") or "")
    _print_plan(first, rest, args.seat_spot_check,
                getattr(args, 'lanes', 1))

    # EB-169 AND EB-187, FOR THE WHOLE ROUND, BEFORE THE ONE LAUNCH. `stage`
    # runs both preflights itself, but per board and after the round has
    # already started spending game time. Running them over every planned
    # board here means a round with an open face defect or a double-counting
    # assumption is refused by a parse, which is what the two rows cost their
    # sittings to learn.
    bad = []
    for row in list(first) + list(rest):
        turn = index.get(row["turn_id"])
        if turn is None:
            bad.append(f"{row['turn_id']}: no turn file with that id")
            continue
        try:
            staged_turn.face_defect_preflight(turn)
            staged_turn.assumption_preflight(turn)
        except staged_turn.TurnError as exc:
            bad.append(f"{row['turn_id']}: {exc}")
    if bad:
        for line in bad:
            print(f"PREFLIGHT REFUSED  {line}", file=sys.stderr)
        return 2
    print("preflights: every board passes face-defect and assumption checks")

    # EB-202. THE REACHABILITY CHECK, AND IT RUNS BEFORE THE PLAN IS ACCEPTED
    # -- with the preflights, on the committed boards, before the one launch.
    # A threshold above what this set can produce is an instrument that cannot
    # answer its own question, and the round is refused rather than run to a
    # MISS that says nothing (KLEESPARK-R1 `P1`: threshold 4, ceiling 3).
    planned = [index[row["turn_id"]] for row in list(first) + list(rest)
               if row["turn_id"] in index]
    if staged_turn.slot_report(planned):
        print("ROUND REFUSED: a registered slot cannot be reached by this "
              "board set (EB-202)", file=sys.stderr)
        return 2

    if args.plan_only:
        print("\n--plan-only: nothing was staged, read or run. Commit this "
              "schedule before the round, for the same reason a prediction "
              "slate is committed before a run.")
        return 0

    try:
        client = _client(args)
    except local_model.LocalModelError as exc:
        print(f"local tester: {exc}", file=sys.stderr)
        return 2

    steps = LiveSteps(client=client, why=args.why,
                      spot_check=args.seat_spot_check,
                      seat_mode=args.seat_mode,
                      log_root=Path(args.log_root) if args.log_root else None)
    pool = _live_lanes(args)
    records: list[dict[str, Any]] = []
    unrun: list[dict[str, Any]] = []
    try:
        for one in pool:
            one.launch()
        records += run_pipeline(first, lanes=pool, steps=steps,
                                serial=args.serial, log=print)
        if rest:
            state = slot_state(first, disk_grades([r["turn_id"]
                                                   for r in first]))
            to_run, skipped = split_rest(rest, state)
            print("\nR221 B -- after the first set:")
            for slot in sorted(state):
                print(f"  {slot}: {state[slot]}")
            for row in skipped:
                staged_turn.mark_unrun(
                    row["turn_id"], seed=str(row.get("seed") or "-"),
                    slots=row["slots"],
                    why=("every registered slot this board carries was "
                         "DECIDED by the first set"))
                print(f"  UNRUN {row['turn_id']} "
                      f"(seed {row.get('seed') or '-'} still pinned)")
            unrun = skipped
            records += run_pipeline(to_run, lanes=pool, steps=steps,
                                    serial=args.serial, log=print)
    finally:
        # IN REVERSE. Lane 0 owns the shared game-directory changes -- the
        # appid file and the `mods/STS2_MCP` install -- and removing them
        # while a later lane's game is still up would pull the bridge out
        # from under a running process (and delete a dll it holds a lock on).
        for one in reversed(pool):
            one.close()

    for one in pool:
        print(f"\ngame[{one.label}]: {one.launches} launch(es), "
              f"{one.relaunches} relaunch(es) for the round")
    staged_turn.main(["ledger"])

    # pick 4(e) / R221 A. The round says, in its own record, how often the
    # shadow seat and the deciding tester reached the same verdict -- which is
    # the number `M62`'s criterion is read off. It is written whichever chair
    # the seat sat in: a `deciding` round has no shadow and the count is
    # honestly zero-of-zero rather than absent.
    summary = round_summary(records, seat_mode=args.seat_mode, unrun=unrun,
                            replays=steps.replays)
    path = write_round_summary(summary)
    agree = summary["agreement"]
    print(f"\nseat mode: {args.seat_mode}   agreement (shadow vs deciding): "
          f"{agree['agreed']} of {agree['compared']} comparable turn(s)")
    for row in agree["turns"]:
        if not row["comparable"]:
            print(f"  {row['turn_id']}: not comparable "
                  f"(shadow {row['shadow_verdict'] or '-'}, deciding "
                  f"{row['deciding_verdict'] or '-'})")
            continue
        print(f"  {row['turn_id']}: shadow {row['shadow_verdict']} vs "
              f"deciding {row['deciding_verdict']} -- "
              f"{'AGREE' if row['agree'] else 'DIFFER'}")
    print(f"round summary: {path}")

    queue = round_queue(records)
    print(f"\nseat review owed on {len(queue)} of {len(records)} turn(s):")
    for row in queue:
        print(f"  {row['turn_id']}  ({', '.join(row['reasons'])})")
        print(f"    {row['command']}")
    if unrun:
        print(f"\n{len(unrun)} board(s) recorded UNRUN with their seeds "
              f"pinned; see review/qa/ledger.tsv")
    return 0


def cmd_qualify(args) -> int:
    """M62 (5). Run the seat against the fixed battery and grade it (R223).

    The battery's packets are SEALED and closed, so every read lands in
    `--land-dir` rather than beside them: a requalification may not write into
    a turn directory whose round is published (R101b).

    The verdict is R223's pass mark -- targets 6/6, costs 4/6, intent 4/6, and
    all three must hold -- and it is the EXIT CODE: 0 for PASS, 1 for FAIL.
    Only a battery that cannot be run at all exits 2.
    """
    from understudy import qualify
    battery_path = Path(args.battery) if args.battery else None
    try:
        items = qualify.load_battery(battery_path)
        threshold = qualify.load_threshold(battery_path)
    except (OSError, qualify.BatteryError) as exc:
        print(f"qualify: {exc}", file=sys.stderr)
        return 2
    thin = qualify.thin_categories(items)
    if thin:
        print(f"qualify: the battery is thin in {', '.join(thin)} "
              f"(floor {qualify.MIN_ITEMS_PER_CATEGORY} per category)",
              file=sys.stderr)
        return 2
    unreachable = qualify.unreachable_marks(items, threshold)
    if unreachable:
        print("qualify: the pass mark cannot be reached on this battery -- "
              + "; ".join(unreachable), file=sys.stderr)
        return 2
    try:
        client = _client(args)
    except local_model.LocalModelError as exc:
        print(f"qualify: {exc}", file=sys.stderr)
        return 2

    land_root = Path(args.land_dir) if args.land_dir else (
        QA_DIR / "qualify" / time.strftime("%Y%m%d-%H%M%S"))

    def reader(item) -> dict[str, Any] | None:
        land = land_root / item.turn_id
        land.mkdir(parents=True, exist_ok=True)
        record = read_turn(item.turn_id, client=client, land_dir=land,
                           seat_mode=args.seat_mode,
                           spot_check=0,
                           log_root=Path(args.log_root) if args.log_root
                           else None)
        if record.get("refused") or not record.get("form"):
            return None
        return json.loads(Path(record["form"]).read_text(encoding="utf-8"))

    card = qualify.run_battery(items, reader=reader, seat_id=args.tester_id,
                               threshold=threshold)
    out = qualify.write_scorecard(card, Path(args.out) if args.out else
                                  land_root / "scorecard.json")
    for row in card["items"]:
        print(f"  {'PASS' if row['passed'] else 'FAIL'}  {row['item']:<3} "
              f"{row['category']:<8} {row['turn_id']}  {row['why']}")
    for cat, v in card["per_category"].items():
        print(f"  {'PASS' if v['pass'] else 'FAIL'}  {cat:<8} "
              f"{v['passed']}/{v['items']}, mark {v['required']}")
    print(qualify.one_line(card))
    print(f"scorecard: {out}")
    return 0 if card["pass"] else 1


def _live_lanes(args) -> list[GameLane]:
    """One `soak.Session` per lane, or none at all if the operator holds it.

    `--attach` is the escape hatch for a game somebody else launched (the same
    contract `embark --hold` offers): the lane then owns no process, restarts
    nothing and tears nothing down. It is single-lane by construction -- there
    is one game being held, and this cannot attach to a second one it did not
    launch.

    ONLY THE FIRST LANE INSTALLS THE BRIDGE. Both lanes run out of ONE game
    directory, `deploy_bridge.ps1` deletes and rewrites `mods/STS2_MCP`, and
    it refuses outright while a game is running -- so lane 1, which launches
    after lane 0's game is up, is given `install_bridge=False`. The same flag
    keeps its teardown from removing the shared directory.
    """
    from understudy import instances, soak
    count = max(1, int(getattr(args, "lanes", 1) or 1))
    if args.attach:
        if count > 1:
            raise LocalTesterError(
                "--attach holds ONE game, so it cannot drive two lanes; drop "
                "--lanes or drop --attach")
        return [GameLane(log=print)]
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out = []
    for i, inst in enumerate(instances.lanes(count)):
        session = soak.Session(f"{stamp}-{inst.label}", do_setup=True,
                               intent="staged-turn round",
                               instance=inst, install_bridge=(i == 0))
        out.append(GameLane(session=session, state_reader=bridge.get_state,
                            log=print, instance=inst))
    return out


def _print(record: Mapping[str, Any]) -> None:
    print(f"tester: {record['tester_id']}  family={record['tester_family']}  "
          f"role={record['role']}")
    print(f"record: {record.get('record')}")
    if record["refused"]:
        print(f"REFUSED  {record['refused']}: {record['refused_why']}",
              file=sys.stderr)
    for hit in record.get("resource_order_flag") or []:
        print(f"RESOURCE ORDER: {hit['why']}", file=sys.stderr)
    for hit in record.get("misreads") or []:
        print(f"MISREAD: {hit}", file=sys.stderr)
    if record["seat_review_required"]:
        print(f"SEAT REVIEW OWED: "
              f"{', '.join(record['seat_review_reasons'])}")


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--model", default="")
        p.add_argument("--log-root", default="")
        p.add_argument("--seat-spot-check", type=int,
                       default=DEFAULT_SPOT_CHECK,
                       help=f"every Nth local-tested turn of a round is ALSO "
                            f"read by the Codex seat (default {DEFAULT_SPOT_CHECK}; "
                            f"0 disables the periodic half, never the "
                            f"resource-order route)")
        p.add_argument("--seat-mode", choices=SEAT_MODES,
                       default=DEFAULT_SEAT_MODE,
                       help=f"which chair the local seat sits in (default "
                            f"{DEFAULT_SEAT_MODE!r}). In shadow it reads "
                            f"every packet and is graded, but it is never the "
                            f"deciding verdict and is never replayed -- the "
                            f"fresh-Opus control is. 'deciding' restores the "
                            f"pre-R221-A behaviour")

    r = sub.add_parser("read", help="the local model READS one staged turn")
    r.add_argument("turn_id")
    r.add_argument("--tester-id", default="",
                   help="default `local-<slug of the model>`, and it must be "
                        "STABLE across turns for the same seat")
    r.add_argument("--position", type=int, default=1,
                   help="this turn's one-based position in the round, which "
                        "is what the spot-check rate counts")
    r.add_argument("--dry-run", action="store_true")
    common(r)
    r.set_defaults(func=cmd_read)

    q = sub.add_parser("round", help="read a whole round, then print the "
                                     "turns the Codex seat still owes")
    q.add_argument("turn_ids", nargs="+")
    q.add_argument("--plan-only", action="store_true",
                   help="print the schedule and send nothing")
    q.add_argument("--why", default="staged-turn round (R221)",
                   help="one line, logged on every staged and replayed row")
    q.add_argument("--first", type=int, default=DEFAULT_FIRST,
                   metavar="N",
                   help=f"R221 B sequential stopping: run the first N boards "
                        f"of the pre-registered order, then run the rest only "
                        f"where a slot is still UNDECIDED (default "
                        f"{DEFAULT_FIRST}; raised automatically where the "
                        f"twice-over cover needs more; 0 runs every board)")
    q.add_argument("--serial", action="store_true",
                   help="the pre-R221 phase order -- stage, read, replay, one "
                        "turn at a time with the game idle while the model "
                        "reads. Kept reachable so a live comparison against "
                        "the pipeline is possible")
    q.add_argument("--lanes", type=int, default=1, metavar="N",
                   help="how many GAME INSTANCES the round drives (default "
                        "1, the single-instance funnel unchanged). 2 runs a "
                        "second SlayTheSpire2.exe from the same install with "
                        "its own APPDATA and its own bridge port, and deals "
                        "the pre-registered boards to the lanes in order -- "
                        "the order and the stopping rule are unchanged")
    q.add_argument("--attach", action="store_true",
                   help="do not launch or tear down a game: attach to one "
                        "somebody else is holding (`embark --hold`). The lane "
                        "then owns no process and relaunches nothing")
    common(q)
    q.set_defaults(func=cmd_round)

    b = sub.add_parser("qualify",
                       help="run the seat against the fixed battery of sealed "
                            "packets and grade it against R223's pass mark "
                            "(targets 6/6, costs 4/6, intent 4/6); exits 0 on "
                            "PASS, 1 on FAIL")
    b.add_argument("--battery", default="",
                   help=f"the battery file (default "
                        f"understudy/battery/battery.yaml)")
    b.add_argument("--out", default="",
                   help="where to write the scorecard JSON")
    b.add_argument("--land-dir", default="",
                   help="where the battery's reads land; NEVER the sealed "
                        "turn directories (R101b)")
    b.add_argument("--tester-id", default="")
    common(b)
    b.set_defaults(func=cmd_qualify)

    args = ap.parse_args(list(argv) if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
