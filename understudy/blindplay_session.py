"""One blind run: one screen at a time, one command at a time.

Cut out of `blindplay.py` by `EB-180`: the tester (`CodexThread` and
the two shipped doubles), the budget, the transcript and the loop that
drives them. Re-exported from `blindplay.py`, so
`blindplay.Session(thread, wire=...)`, `blindplay.ScriptedWire` and
`blindplay.ScriptedThread` still resolve.
"""
from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from understudy import authorship, bridge, qa_packet, seat
from understudy.blindplay_grammar import act
from understudy.blindplay_observe import observation
from understudy.blindplay_read import _int, settle, settle_board, _text
from understudy.blindplay_render import render, sha256, still_in_fight
from understudy.blindplay_shape import (BlindPlayError, _is_rate_limited,
                                        LOG_ROOT, PLAY_GUARDRAIL, PROMPT_PATH,
                                        SeatBudgetExhausted, SETTLE_DELAY_S,
                                        SETTLE_TRIES)
from understudy.blindplay_snapshot import (ledger_rows, SNAPSHOT_VERBS,
                                           wire_snapshot)


# ------------------------------------------------------------- transcript --

class Transcript:
    """One JSONL row per observation, command and post. Gitignored.

    It holds the observation SHA rather than the observation: the page itself
    is reproducible from the state and the file is meant to be read by a
    person checking what the seat was shown and what it said.
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.rows: list[dict[str, Any]] = []

    def write(self, **row: Any) -> dict[str, Any]:
        row["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.rows.append(row)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
        return row


# ------------------------------------------------------------- the tester --

# Independence is by model FAMILY (R217 C). The slice's author is Claude, so a
# Claude seat is refused however fresh its context is -- "a fresh context on
# the same model does not satisfy it" is the ruling's own wording. A driver
# that a person points at a model name needs that refusal in code.
#
# EB-190 MOVED THE RULE, IT DID NOT COPY IT. `understudy/authorship.py` now
# owns the family table and the check, because `seat.py` needs the SAME
# refusal asked the other way round -- not "who is running" but "what does the
# row record about who wrote it" -- and two doors answering one question is
# how a governance rule ends up enforced in one place and remembered in the
# other. `authorship` imports nothing but yaml and reads exactly two keys off
# the prototype surface (`id`, `authored_by`), so the no-sheet pin on this
# module is unchanged. The names below stay bound here: this is where every
# caller and every test already reaches for them.
AUTHOR_FAMILY = authorship.AUTHOR_FAMILY
MODEL_FAMILIES = authorship.MODEL_FAMILIES
model_family = authorship.model_family


def check_independent(model: str, author: str = AUTHOR_FAMILY, *,
                      rows: Any = ()) -> None:
    """Refuse the author's own model family as tester. R217 C, EB-190.

    Thin: the rule is `authorship.check_independent`. This wrapper exists only
    to keep the failure spelled `BlindPlayError`, which is what the driver's
    own error handling and this module's tests catch.
    """
    try:
        authorship.check_independent(model, author, rows=rows)
    except authorship.IndependenceError as exc:
        raise BlindPlayError(str(exc)) from None


def command_schema(forecast_asks: int = 0) -> dict[str, Any]:
    """The reply shape for a play turn. Shape only -- never content.

    `EB-229`, the RUN-lane twin of `EB-239`. `KURAGEMEM002` graded `P1`, `P2`
    and `P4` UNREACHED not because the display failed but because THE QUESTION
    WAS NEVER ASKED: this schema was `command` and `thinking` and nothing
    else, so the tester says why it plays what it plays and is never asked
    what it EXPECTS. §13.5's *stated IN ADVANCE* rule was on the record with
    nothing enforcing it, and `KURAGEMEM001` met it by accident.

    A registration that wants a forecast switches it on and the field
    APPEARS; every other run gets this function's default and the schema it
    has always had, byte for byte. When it is on the field is DECLARED and
    required, `additionalProperties` stays `False`, and `forecast` is the
    FIRST property and the FIRST required key -- a reply is written top to
    bottom, so the pre-commitment is asked BEFORE the command rather than
    beside it.
    """
    if forecast_asks <= 0:
        return {"type": "object",
                "properties": {"command": {"type": "string"},
                               "thinking": {"type": "string"}},
                "required": ["command", "thinking"],
                "additionalProperties": False}
    return {"type": "object",
            "properties": {"forecast": {"type": "array",
                                        "items": {"type": "string"}},
                           "command": {"type": "string"},
                           "thinking": {"type": "string"}},
            "required": ["forecast", "command", "thinking"],
            "additionalProperties": False}


def forecast_block(questions: list[str]) -> str:
    """The pre-commit questions, printed for a blind RUN's tester.

    The same position `qa_packet` gives the staged twin: BEFORE the board,
    because a forecast collected after the line is a rationalisation. An
    empty list prints nothing at all, which is what every unregistered run
    gets.
    """
    if not questions:
        return ""
    out = ["## Before you decide", "",
           "Answer these BEFORE you choose your command, and write the "
           "answers into your reply's `forecast` list in this order. They "
           "are predictions about what is about to happen, not questions "
           "about what you did:", ""]
    out += [f"{i}. {q}" for i, q in enumerate(questions, 1)]
    return "\n".join(out)


def record_schema() -> dict[str, Any]:
    """The reply shape for a fight or run record. Shape only."""
    return {"type": "object",
            "properties": {"record": {"type": "string"}},
            "required": ["record"],
            "additionalProperties": False}


class ScriptedThread:
    """A tester made of a list. The whole loop runs without codex or a game."""

    def __init__(self, replies: list[dict[str, Any]], model: str = "gpt-test"):
        self.replies = list(replies)
        self.model = model
        self.sent: list[str] = []
        # `EB-229`. The SCHEMA is half of what a turn asks for, so a test that
        # wants to know what the tester was asked has to be able to read it.
        self.schemas: list[dict[str, Any]] = []
        self.calls = 0

    def identity(self) -> dict[str, Any]:
        return {"model_requested": self.model, "model_observed": self.model,
                "codex_version": "(scripted)", "thread_id": "(scripted)"}

    def send(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        self.sent.append(prompt)
        self.schemas.append(schema)
        self.calls += 1
        if not self.replies:
            raise BlindPlayError("the scripted tester ran out of replies")
        return self.replies.pop(0)


class ScriptedWire:
    """A game made of a list of states. Shipped, not test-only.

    `get_state` returns the next scripted state on every POST and the current
    one otherwise, which is enough to walk a whole fight: the scenario author
    writes the frames the seat will see and the driver does not know the
    difference. Every POST is recorded so a test can assert the wire body the
    grammar produced.
    """

    def __init__(self, states: list[dict[str, Any]],
                 ledger: list[list[dict[str, Any]]] | None = None):
        self.states = list(states)
        self.posts: list[dict[str, Any]] = []
        self.i = 0
        # `EB-216`. The meter ledger the far side would be keeping: one list
        # per POST, cumulative, the way the mod's own is. `None` scripts a wire
        # with no ledger route at all, which is a release build.
        self.ledger = None if ledger is None else list(ledger)

    def get_state(self) -> dict[str, Any]:
        return self.states[min(self.i, len(self.states) - 1)]

    def post(self, action: str, **params: Any) -> dict[str, Any]:
        self.posts.append({"action": action, **params})
        self.i += 1
        return {"status": "ok", "message": ""}

    def health(self) -> dict[str, Any]:
        return {"mod_version": "0.0-scripted"}

    def meter_ledger(self) -> dict[str, Any]:
        if self.ledger is None:
            # What a release build answers: the route is there, the mod that
            # keeps a ledger is not.
            return {"status": "ok", "available": False, "rows": [], "count": 0}
        rows = self.ledger[min(max(self.i - 1, 0), len(self.ledger) - 1)]
        return {"status": "ok", "available": True, "rows": rows,
                "count": len(rows)}


class CodexThread:
    """ONE `codex exec` thread for a whole run (EB-168).

    `codex exec` for the first turn and `codex exec resume <thread id>` after
    it, which is the door `seat.py` deliberately did not walk through: a blind
    GRADER must not have seen the previous board, and a blind PLAYER must.
    Everything else is `seat.py`'s -- the same flags, the same empty scratch
    root outside the repo, and the same three-source transcript guard applied
    to EVERY reply, not just the first.
    """

    def __init__(self, session: Path, *, model: str = seat.DEFAULT_MODEL,
                 timeout: int = seat.TIMEOUT_S):
        check_independent(model)
        self.session = session
        self.model = model
        self.timeout = timeout
        self.codex = seat.codex_path()
        self.codex_version = seat._codex_version(self.codex)
        self.scratch = seat.scratch_root()
        if seat.is_inside_repo(self.scratch):
            raise BlindPlayError("the seat's scratch directory resolved "
                                 "inside the repo")
        self.thread_id = ""
        self.model_observed = ""
        self.turn = 0

    def identity(self) -> dict[str, Any]:
        return {"model_requested": self.model,
                "model_observed": self.model_observed,
                "codex_version": self.codex_version,
                "thread_id": self.thread_id}

    def close(self) -> None:
        shutil.rmtree(self.scratch, ignore_errors=True)

    def _argv(self, d: Path) -> list[str]:
        """`codex exec` for the first turn, `codex exec resume` after it.

        THE TWO SUBCOMMANDS DO NOT TAKE THE SAME FLAGS, and the first live
        acceptance run is what proved it: `codex exec resume` accepts neither
        `-C` nor `--sandbox` nor `--color` (codex-cli 0.150.1 answers
        `error: unexpected argument '-C' found` and exits 2), so a session
        built by pasting the first turn's argv after `resume` dies on its
        SECOND action every time -- one action in, no fight, no record.

        What each dropped flag is replaced by, rather than given up:
          `-C`        the process cwd, which is already `self.scratch`
          `--sandbox` `-c sandbox_mode=...`, the config key the flag sets
          `--color`   nothing; the stream is `--json` either way
        """
        common = ["--skip-git-repo-check", "--ignore-user-config",
                  "--ignore-rules", "--json",
                  "--output-schema", str(d / "schema.json"),
                  "-o", str(d / "reply.json"), "-m", self.model, "-"]
        if self.thread_id:
            return [self.codex, "exec", "resume", self.thread_id,
                    "-c", 'sandbox_mode="read-only"'] + common
        return [self.codex, "exec", "-C", str(self.scratch),
                "--sandbox", "read-only", "--color", "never"] + common

    def send(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        self.turn += 1
        d = self.session / f"turn-{self.turn:03d}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "prompt.md").write_text(prompt, encoding="utf-8")
        (d / "schema.json").write_text(json.dumps(schema, indent=1) + "\n",
                                       encoding="utf-8")
        argv = self._argv(d)
        (d / "argv.json").write_text(json.dumps(argv, indent=1) + "\n",
                                     encoding="utf-8")
        code, timed_out = seat._run(argv, stdin_text=prompt,
                                    stdout=d / "events.jsonl",
                                    stderr=d / "stderr.txt",
                                    cwd=self.scratch, timeout=self.timeout)
        if timed_out:
            raise BlindPlayError("the seat did not answer inside the timeout")
        events = seat.read_jsonl(d / "events.jsonl")
        self.thread_id = self.thread_id or seat.thread_id(events)
        source = seat.find_rollout(self.thread_id)
        rollout = None
        if source is not None:
            shutil.copyfile(source, d / "rollout.jsonl")
            rollout = seat.read_jsonl(d / "rollout.jsonl")
        stderr_text = (d / "stderr.txt").read_text(encoding="utf-8",
                                                   errors="replace")
        reason, offenders, _counts = seat.guard(events, rollout, stderr_text)
        if reason:
            raise BlindPlayError(
                f"seat refused ({reason}): "
                f"{seat.REFUSAL_REASONS.get(reason, reason)}"
                + (f" -- {', '.join(offenders)}" if offenders else ""))
        if code != 0:
            if _is_rate_limited(stderr_text):
                raise SeatBudgetExhausted(
                    f"codex exited {code} on a usage limit: "
                    f"{stderr_text.strip()[:300]}")
            raise BlindPlayError(
                f"codex exited {code}: {stderr_text.strip()[:300]}")
        self.model_observed = seat.rollout_model(rollout or [])
        try:
            reply = json.loads((d / "reply.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise BlindPlayError(f"the seat's reply did not parse: {exc}")
        if not isinstance(reply, dict):
            raise BlindPlayError("the seat's reply is not a JSON object")
        return reply


# --------------------------------------------------------------- the loop --

@dataclass
class Budget:
    """Three ways to stop, all of them declared before the run starts."""
    max_actions: int = 60
    max_wall_s: float = 3600.0
    max_refusals: int = 3
    # `EB-173`. The other three stop a session that is going WRONG; this one
    # stops a session that is going NOWHERE, which the first three cannot see.
    # A command the resolver accepts and the wire answers with an error resets
    # the refusal counter and spends an action, so a screen the tester cannot
    # get off loops until the action budget is gone -- observed live, 150+
    # identical `confirm`s at one bundle screen. Stall = the rendered page
    # unchanged, this many times running.
    max_stalls: int = 6


FIGHT_QUESTIONS = """That fight is over. In a short paragraph each, and in
plain language:

1. What line did you take, and why that one?
2. What other line did you seriously consider, and what would it have given up?
3. Would a different enemy intent, or a different draw, have changed your
   choice?
4. Which cards became automatic, and which became dead?
5. Did your plan change during the fight, and where?
6. Was anything on the screen confusing to read?"""

RUN_QUESTIONS = """The run is over. In a short paragraph each, and in plain
language:

1. How do you think this character works?
2. Which tension came up again and again?
3. Which cards defined the run?
4. Where did play start to feel repetitive?
5. What would you avoid drafting next time, and why?"""

RECORD_DISCLAIMER = (
    "None of this is a judgement of whether the game is fun or good that "
    "anyone will treat as approval. It is one model's account of one run, "
    "recorded for iteration.")


class Session:
    """One blind run: one screen at a time, one command at a time.

    `wire` is anything with `get_state()` and `post(action, **params)` --
    `understudy.bridge` in the live case and a scripted double in the tests, so
    the whole loop is exercised without the game or codex.
    """

    def __init__(self, thread: Any, *, wire: Any = bridge,
                 session_id: str = "", budget: Budget | None = None,
                 log_root: Path | None = None,
                 prompt_path: Path | None = None,
                 forecast: list[str] | None = None,
                 settle_tries: int = SETTLE_TRIES,
                 settle_delay_s: float = SETTLE_DELAY_S):
        self.thread = thread
        self.wire = wire
        self.settle_tries = settle_tries
        self.settle_delay_s = settle_delay_s
        self.budget = budget or Budget()
        self.session_id = session_id or time.strftime("%Y%m%d-%H%M%S",
                                                      time.gmtime())
        self.dir = (log_root or LOG_ROOT) / self.session_id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.transcript = Transcript(self.dir / "transcript.jsonl")
        self.prompt_text = (prompt_path or PROMPT_PATH).read_text(
            encoding="utf-8")
        self.prompt = seat.template_body(self.prompt_text)
        self.prompt_sha = sha256(self.prompt)
        # `EB-229`. OPT-IN and EMPTY BY DEFAULT: a run that registers no
        # forecast prints no such block, is sent the schema it has always
        # been sent, and seals a record with no forecast key in it.
        self.forecast = [str(q).strip() for q in (forecast or [])
                         if str(q).strip()]
        # The questions are printed on the blind page, so they answer to the
        # same leak rule every other line of it does (`staged_turn` checks
        # its own the same way).
        bad = qa_packet.leaks(list(self.forecast))
        if bad:
            rule, hit, ctx = bad[0]
            raise BlindPlayError(
                f"forecast question leaks design vocabulary ({rule}: {hit!r} "
                f"in {ctx[:80]!r}): it is printed at the top of the blind "
                f"page -- ask it in the vocabulary the page prints")
        self.forecasts: list[dict[str, Any]] = []
        self.actions = 0
        self.refusals = 0
        # `EB-216`. One row per play and per end turn, machine-written off the
        # wire and never rendered to the seat.
        self.wire_rows: list[dict[str, Any]] = []
        # The highest meter-ledger row index already filed on a snapshot, so
        # each snapshot carries the rows THIS action minted and not the fight's
        # whole history over again.
        self._ledger_seen = 0
        self.fight_records: list[str] = []
        self.run_record = ""
        self.stopped = ""
        self.started = time.time()

    # -- the two things the seat is ever sent ------------------------------

    def _page(self, obs_md: str, feedback: str,
              forecast: list[str] | None = None) -> str:
        parts = []
        # `EB-229`. FIRST, and that position is the whole point -- the same
        # one `qa_packet` gives the staged twin. The tester reads top to
        # bottom, so a question printed under the board is a question asked
        # after the line has been chosen.
        block = forecast_block(list(forecast or []))
        if block:
            parts.append(block)
        parts.append(obs_md)
        if feedback:
            parts.append(f"## What happened last time\n\n{feedback}")
        parts.append("Answer with ONE command from the grammar.")
        return "\n\n".join(parts)

    def _settle(self, state: dict[str, Any]) -> dict[str, Any]:
        """Ride out a MOMENT rather than reporting it as a screen.

        The first live acceptance run died here: the seat walked onto a Monster
        node, the very next read answered `state_type: "unknown"` because the
        room had not been entered yet, and the driver stopped the session
        TOOL-BLOCKED against a transition. `soak._settle_transient` had already
        learned this on the same wire, and the fix is the same shape -- poll,
        bounded, and hand back whatever is there when the bound runs out so a
        wire that really is stuck is still reported as blocked rather than
        waited on forever. A missing `state_type` key is the same moment one
        frame earlier and settles the same way.

        `EB-175` added the third shape -- a combat screen the game has not
        handed back yet -- to `transient()`, which is where all three now
        live so the CLI's own live reads ride out the same moments.

        `EB-381` ADDED A SECOND WAIT AFTER IT, and it is a different question.
        `transient` asks whether this is a SCREEN; `settle_board` asks whether
        the BODIES on it have finished changing. A card play is handed to the
        game's action queue and answered at once, so a read taken a few
        milliseconds later can carry the damage action's HP and not the
        `PowerCmd.Apply` behind it -- which is how the r9 act-3 seat read "no
        aura at all" off a body that had one, twice, and wrote off a Vaporize
        that then happened. The order is load-bearing: settle the screen first,
        because there is no board to settle on a frame that has none.
        """
        state = settle(state, self.wire, self.settle_tries,
                       self.settle_delay_s)
        return settle_board(state, self.wire, delay=self.settle_delay_s)

    def _ask_record(self, questions: str) -> str:
        reply = self.thread.send(f"{questions}\n\n{RECORD_DISCLAIMER}\n",
                                 record_schema())
        text = str(reply.get("record") or "").strip()
        self.transcript.write(kind="record", chars=len(text))
        return text

    # -- the loop ----------------------------------------------------------

    def run(self) -> dict[str, Any]:
        feedback = ""
        first = True
        in_fight = False
        last_page_sha = ""
        stalls = 0
        while True:
            if self.actions >= self.budget.max_actions:
                self.stopped = "max_actions"
                break
            if time.time() - self.started > self.budget.max_wall_s:
                self.stopped = "max_wall"
                break

            state = self._settle(self.wire.get_state())
            try:
                obs = observation(state)
            except qa_packet.PacketLeak as exc:
                self.stopped = "observation_leak"
                self.transcript.write(kind="leak", detail=str(exc))
                break
            page = render(obs)
            page_sha = sha256(page)
            if page_sha == last_page_sha:
                stalls += 1
                if stalls >= self.budget.max_stalls:
                    self.stopped = "stalled"
                    self.transcript.write(kind="stall", page_sha256=page_sha,
                                          repeats=stalls)
                    break
            else:
                stalls = 0
            last_page_sha = page_sha
            self.transcript.write(kind="observation",
                                  state_type=obs["state_type"],
                                  screen=obs["screen"],
                                  blocked=obs["blocked"],
                                  observation_sha256=page_sha)

            was_in_fight, in_fight = in_fight, still_in_fight(obs, in_fight)
            if was_in_fight and not in_fight and self.actions:
                # SAME REASONING AS THE RUN RECORD BELOW (b0de780): a seat that
                # cannot answer at a fight boundary must not take the fight
                # records already gathered down with it.
                try:
                    self.fight_records.append(
                        self._ask_record(FIGHT_QUESTIONS))
                except SeatBudgetExhausted as exc:
                    self.stopped = "budget:rate_limit"
                    self.transcript.write(kind="seat_budget", detail=str(exc),
                                          at="fight_record")
                    break
                except BlindPlayError as exc:
                    self.stopped = "seat_refused"
                    self.transcript.write(kind="seat_error", detail=str(exc),
                                          at="fight_record")
                    break

            if obs["blocked"]:
                self.stopped = ("run_over" if obs["screen"] == "game_over"
                                else "tool_blocked")
                break

            # `EB-229`. A forecast is a PER-TURN pre-commitment, so it is
            # asked on the screens that have turns. A map walk, a shop or a
            # reward screen has no next turn to predict, and asking there
            # would collect a forecast about a board the tester is not on.
            asks = list(self.forecast) if obs["screen"] == "combat" else []
            body = self._page(page, feedback, asks)
            prompt = f"{self.prompt}\n\n---\n\n{body}\n" if first else body
            first = False
            try:
                reply = self.thread.send(prompt, command_schema(len(asks)))
            except SeatBudgetExhausted as exc:
                self.stopped = "budget:rate_limit"
                self.transcript.write(kind="seat_budget", detail=str(exc))
                break
            except BlindPlayError as exc:
                self.stopped = "seat_refused"
                self.transcript.write(kind="seat_error", detail=str(exc))
                break
            if asks:
                # RECORDED, NEVER GRADED HERE. The registration that switched
                # the channel on is what grades the answers against the wire;
                # this driver's whole job is that the answer EXISTS, is
                # attached to the page it was written on, and is countable.
                # A short answer is COUNTED SHORT rather than stopping the
                # run: the staged lane can refuse a form and re-read it, a
                # live run cannot un-spend the game time, and a slot whose
                # denominator is short is a fact its grader can see.
                answers = [str(a).strip()
                           for a in (reply.get("forecast") or [])]
                row = {"action": self.actions + 1,
                       "observation_sha256": page_sha,
                       "questions": list(asks),
                       "answers": answers,
                       "asked": len(asks),
                       "answered": len([a for a in answers if a])}
                row["short"] = row["answered"] < row["asked"]
                self.forecasts.append(row)
                self.transcript.write(kind="forecast", **row)

            command = str(reply.get("command") or "").strip()
            if not command:
                self.stopped = "no_command"
                break

            res = act(state, command)
            self.transcript.write(kind="command", command=command,
                                  ok=res["ok"], verb=res["verb"],
                                  printed=res["printed"],
                                  post=res["post"], refusal=res["refusal"])
            if not res["ok"]:
                self.refusals += 1
                feedback = f"That did not work: {res['refusal']}"
                if self.refusals >= self.budget.max_refusals:
                    self.stopped = "refusal_limit"
                    break
                continue

            self.refusals = 0
            # `EB-216`. The board the seat decided on, written down before the
            # POST moves it. Only `play` and `end turn`: a map walk or a shop
            # purchase has no turn, no bank and no intent to count against.
            snap = None
            if res["verb"] in SNAPSHOT_VERBS:
                snap = wire_snapshot(state, index=len(self.wire_rows) + 1,
                                     verb=res["verb"], command=command)
                self.wire_rows.append(snap)
                self.transcript.write(kind="wire", index=snap["index"],
                                      verb=snap["verb"], turn=snap["turn"])
            post = dict(res["post"] or {})
            action = post.pop("action")
            result = post_when_the_room_is_open(
                self.wire, action, post, tries=self.settle_tries,
                delay=self.settle_delay_s)
            # `EB-216`, R225's clause. AFTER the POST, because the ledger row
            # this play minted does not exist until the play has resolved --
            # the board above is the decision, this is what the decision cost
            # and what it gave back. A gain that lands later (a turn-start kit
            # response after an `end turn`) is on the NEXT snapshot's rows,
            # which is where the engine actually put it.
            if snap is not None:
                rows, note = ledger_rows(self.wire, self._ledger_seen)
                snap["ledger"] = rows
                if note:
                    snap["ledger_note"] = note
                for row in rows:
                    self._ledger_seen = max(self._ledger_seen,
                                            _int(row.get("index")))
            self.actions += 1
            # `EB-341`: the decision first, in the screen's own words, and
            # then the game's answer. A screen that says nothing about what
            # arrived leaves the tester with the row it took; a screen that
            # does say leaves it with both, in that order.
            feedback = " ".join(x for x in (taken_line(res),
                                            _result_line(result)) if x)
            self.transcript.write(kind="result", action=action,
                                  summary=feedback)

        # ASKED EVEN ON A TRUNCATED RUN -- a session that hit its action budget
        # still has an account worth keeping -- but never at the cost of the
        # record already gathered: a seat that has just refused cannot answer,
        # and losing the fight records to that would be losing the session.
        if self.actions and not self.run_record:
            try:
                self.run_record = self._ask_record(RUN_QUESTIONS)
            except BlindPlayError as exc:
                self.transcript.write(kind="seat_error", detail=str(exc),
                                      at="run_record")
        return self.summary()

    def summary(self) -> dict[str, Any]:
        # `EB-229`. The key is present only where the channel was switched
        # on, so an unregistered run's sealed record is what it has always
        # been -- the same discipline `wire` is written under.
        extra = {"forecast_questions": list(self.forecast),
                 "forecasts": list(self.forecasts)} if self.forecast else {}
        return {
            **extra,
            "session_id": self.session_id,
            "actions": self.actions,
            "termination": self.stopped or "unknown",
            "prompt_sha256": self.prompt_sha,
            "wire": list(self.wire_rows),
            "fight_records": list(self.fight_records),
            "run_record": self.run_record,
            "transcript": str(self.transcript.path),
            "guardrail": PLAY_GUARDRAIL,
            **self.thread.identity(),
        }


# `EB-520`. THE ROOM THE STATE READ CAN SEE AND THE ACTION CANNOT.
#
# THE DEFECT, three seats over two days. Kokomi r18 lane 1, floor 10: `rest`
# came back `Rest site room is not open` "while the screen was printing Rest as
# an option and listing `rest` as a thing I could say"; `choose "Rest"` a moment
# later worked. Klee r10 saw it twice on `rest` and the Ironclad control seat
# saw it on `upgrade` "issued immediately after `go` ... while simultaneously
# echoing `Took: Smith` -- the room had not finished loading."
#
# THE TWO READS ARE OF DIFFERENT THINGS, which is why the page is not lying and
# the post is not wrong. `BuildState` reports the room off `RunState`, which the
# walk commits at once; `ExecuteChooseRestOption` needs `NRestSiteRoom.Instance`
# -- the SCENE -- which Godot instantiates a frame or two later. Between the two
# the page is a rest site with every option on it and the action has nothing to
# click. `_settle` cannot see this: it asks the wire what SCREEN this is, and
# the wire says rest site, correctly.
#
# SO IT IS RIDDEN OUT AT THE POST, `_settle`'s own shape one door over: poll,
# bounded by the settle budget, and hand back the LAST answer when the bound
# runs out so a room that really is shut is still reported to the seat. Only
# this one sentence is retried -- a room that is not open is a moment, and every
# other refusal the bridge gives is an answer.
ROOM_NOT_OPEN = "room is not open"


def post_when_the_room_is_open(wire: Any, action: str,
                               params: dict[str, Any], *, tries: int,
                               delay: float) -> dict[str, Any]:
    """POST, and re-POST while the bridge says the room is still loading."""
    result = wire.post(action, **params)
    for _ in range(max(tries, 0)):
        if ROOM_NOT_OPEN not in _text(
                (result or {}).get("error") if isinstance(result, dict) else ""):
            break
        time.sleep(delay)
        result = wire.post(action, **params)
    return result


def _result_line(result: Any) -> str:
    """The wire's answer to a POST, in the tester's vocabulary.

    Only the game's own `message`, `error` and `status` cross back -- a full
    state dump would carry ids, and the next observation is where the board is
    read anyway. Scrubbed like everything else.

    `EB-269`, THE HALF THAT MADE THE DEFECT INVISIBLE. The bridge writes a
    refusal's reason under `error`, never `message`
    (`vendor/STS2_MCP/McpMod.Helpers.cs:158-161`), and this line read `status`
    and `message` only -- so EVERY refusal the game gave reached the tester as
    the single word `error` with the sentence dropped on the floor. The r2 Opus
    seat had to report a potion that "cannot be used" three times over because
    the game had said `No potion in slot 0` three times and nobody was carrying
    it across. A refusal is words now, which is the row's own next action.
    """
    if not isinstance(result, dict):
        return ""
    text = " ".join(x for x in (_text(result.get("status")),
                                _text(result.get("message")),
                                _text(result.get("error"))) if x)
    leaks = qa_packet.leaks(text)
    if leaks:
        return "(the game answered with something this tool will not repeat)"
    return text


# What each verb's answer opens with. A word per verb rather than one flat
# "Took", because "Bought" and "Went to" are what a player would say and this
# line is read in a stream of them.
_TAKEN_VERB = {"buy": "Bought", "go": "Went to"}
# The keys a resolution files its printed decision under, best first. One
# resolution ever carries one of them.
_TAKEN_KEYS = ("option", "card", "bundle", "item", "node")


def taken_line(res: dict[str, Any]) -> str:
    """What the tester just took, in the names the screen used (`EB-341`).

    THE DEFECT. A choice's outcome was legible only on some LATER screen. The
    r7b act-3 seat learned that The Round Tea Party's random relic was `Bag of
    Marbles`, and what `Forgotten Soul` does, "from the relic list of a later
    combat screen"; the act-2b seat could not say which of two identically
    titled options it had taken; and eleven one-way choices across four seats
    "name a thing and never say what it does". The wire's own answer to a POST
    is one short sentence and often says nothing at all.

    What the page DOES have is the row it just resolved -- the name it matched
    and the body printed under it -- and that body is where a screen says what
    it grants (`Obtain Royal Poison. Heal to full HP.`). So the line after a
    choice is the row that was taken, in the screen's own words, ahead of
    whatever the game answers. It reports a DECISION and never an outcome: the
    game's own answer follows it, and is the only thing that says what landed.

    Scrubbed like `_result_line`, and for the same reason -- it is assembled
    from wire text and it goes to a third party's model.
    """
    printed = res.get("printed") or {}
    if not isinstance(printed, dict):
        return ""
    name = next((_text(printed.get(k)) for k in _TAKEN_KEYS
                 if _text(printed.get(k))), "")
    if not name:
        return ""
    line = f"{_TAKEN_VERB.get(str(res.get('verb') or ''), 'Took')}: {name}"
    kind = _text(printed.get("kind"))
    if kind:
        line += f" ({kind})"
    price = printed.get("price")
    if isinstance(price, int):
        line += f", for {price} gold"
    body = _text(printed.get("text"))
    if body:
        line += f" — {body}"
    line = line.rstrip(".") + "."
    # `EB-448`. WHAT THE ROW HANDED OVER, BY NAME. The sentence above is the
    # screen's promise ("Add a card to your deck"); these are the faces the
    # feed carried beside it and the page used to drop, so Klee r13's granted
    # egg was a sentence and the card itself turned up two fights later.
    # Appended rather than folded in, because the promise and the thing are
    # two different claims and only the second one is a card now owned.
    for named in printed.get("names") or []:
        if not isinstance(named, dict) or not _text(named.get("name")):
            continue
        line += f" It names **{_text(named['name'])}**"
        body = _text(named.get("text"))
        line += f": {body.rstrip('.')}." if body else "."
    return "" if qa_packet.leaks(line) else line
