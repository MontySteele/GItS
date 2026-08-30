"""The INDEPENDENT-MODEL SEAT: OpenAI's Codex CLI as a blind grader (EB-149).

R213's first guard on the QA funnel is procedural -- the agent that answers a
staged turn must never be the agent that designed the cards. A fresh Claude
session satisfies the letter of that. A DIFFERENT VENDOR'S MODEL satisfies it
structurally: `codex exec` cannot have seen this repo's design conversation,
because it is not this repo's design conversation.

This module wraps `codex exec` in two roles:

  * `grade` -- the DESIGN-BLIND seat. One fresh, sandboxed, config-less Codex
    turn is handed exactly the text `qa_grader_prompt.md` prescribes, with
    `<PACKET>` and `<SHA>` substituted, and nothing else. Its reply is saved
    verbatim and fed to `staged_turn grade`.
  * `review` -- the REPO-VISIBLE seat. Not blind, not a grader: a second
    reader for a diff or a design question, run read-only at the repo root.

THE GUARD, AND THE THREE PLACES IT LOOKS
----------------------------------------
`--sandbox read-only` stops Codex WRITING. It does not stop it READING: a
read-only sandbox still lets a model run `cat docs/kokomi-cards.yaml` or
`rg tempo_band`, and a grader that has read the sheet is not blind however the
process was launched. The sandbox is therefore not the blindness claim.

Blindness is proven from the TRANSCRIPT -- and the first design of this module
got that wrong in a way worth writing down, because the correction is the
whole guard. **`--json`'s stdout event stream does not show tool-call
attempts.** Measured on this machine (codex-cli 0.150.1, 2026-08-28): in a
smoke where the model attempted three shell commands -- `powershell` twice,
`cmd` once -- stdout carried `thread.started`, `turn.started`, one
`item.completed` holding an `agent_message`, and `turn.completed`. Nothing
else. A guard reading only that stream would have certified that seat blind.

So `guard` reads THREE sources and refuses if any of them shows a tool:

  1. **`events.jsonl`** -- the `--json` stdout stream, allowlisted by event
     type and item type. Necessary, not sufficient.
  2. **`rollout.jsonl`** -- codex's own session record, which IS complete.
     `--ephemeral` is therefore NOT passed to `grade`: the rollout is the
     evidence, and a seat that suppressed its own record could not be
     checked. It is found by the `thread_id` from `thread.started` under
     `$CODEX_HOME/sessions/**/`, copied beside the run, and allowlisted twice
     over -- `response_item` payload types (`message`, `reasoning` only, so a
     `custom_tool_call`, `function_call`, `local_shell_call` or
     `web_search_call` refuses) and `event_msg` item types (`UserMessage`,
     `AgentMessage`, `Reasoning`). **A missing rollout REFUSES**
     (`seat_no_transcript`): no evidence is not the same as good evidence.
     The rollout also carries the guard's one POSITIVE reading: a
     `world_state` line states what the environment held, and its `agents_md`
     map is EMPTY when no project instruction file was in reach. A non-empty
     one refuses with `seat_saw_instructions` -- in this repo an `AGENTS.md`
     is the map to the design docs.
  3. **`stderr.txt`** -- where a REJECTED attempt lands. Under a read-only
     sandbox on this box every shell command is blocked, and the attempt is
     logged as `ERROR codex_core::tools::router: error=exec_command failed
     for ...: Rejected(... blocked by policy)`. Any line naming that router,
     or `exec_command`, refuses.

Every layer is an ALLOWLIST, and **unknown types REFUSE**. A Codex release
that adds a tool fails closed on the day it ships rather than passing silently
until somebody notices. The published SDK item union was already short by one
tool -- `collab_tool_call` is in the 0.150.1 binary and not in the docs -- on
the day this was written, which is the concrete reason the list is not a
denylist.

Note what the guard does NOT rely on: that the sandbox blocked the command. It
refuses on the ATTEMPT, and it would equally catch an attempt that SUCCEEDED,
because the rollout records the call either way. The sandbox is a second wall,
not the measurement.

`--ignore-user-config` and `--ignore-rules` close the two other routes to a
tool the wrapper did not ask for: the user's MCP servers and hooks in
`$CODEX_HOME/config.toml`, and project execpolicy `.rules` files. Auth still
reads `CODEX_HOME`, so the ChatGPT-plan sign-in survives both.

THE SCRATCH ROOT IS OUTSIDE THE REPO, AND THAT IS NOT TIDINESS
--------------------------------------------------------------
`-C` points at an empty temporary directory created outside every checkout,
and the run is refused if anything is in it or if it resolves inside the repo.
Codex reads `AGENTS.md` from its working root, and this repo HAS one, which
routes an agent to `CLAUDE.md` and the design docs. A scratch root inside the
tree would hand the blind grader the map. The smoke confirms the fix: with
`-C <temp dir>` the model reported "project instructions: NONE" and the
rollout's `world_state` recorded `agents_md: {}`. The directory is recorded in
`seat.json` and removed after the run.

THE IDENTITY FILL, AND ITS EXACT LIMIT
--------------------------------------
The form asks for `grader.id`, and a model cannot know the string this repo's
ledger groups it by -- `staged_turn.is_down_weighted` needs that string stable
across turns, and it is a fact about the SEAT, not about the answer. So the
wrapper writes exactly three fields: `grader.id`, `grader.kind` (always
`llm`), and `grader.model`. Nothing else. `turn_id`, `packet_sha256`,
`grader.designed_these_cards`, `chosen_line` and all four answers are
byte-for-byte the model's; `form-raw.json` is kept beside the filled copy; and
`test_understudy_seat` proves the wrapper cannot move a fourth field. A
`designed_these_cards: true` from the model survives into the form and REFUSES
the turn, which is the correct outcome and not one the wrapper may tidy away.

WHAT IS COMMITTED, AND WHAT IS NOT
----------------------------------
Committed: `review/qa/<turn-id>/form-<grader-id>.json`, and the verdict and
ledger rows `staged_turn` writes from it. NOT committed: the session directory
under `understudy/logs/seat/`, which is gitignored -- it holds the packet
inlined into a prompt, a third party's system prompt, and a third party's raw
model output.

VERIFIED FACTS (codex-cli 0.150.1 on this machine, 2026-08-28)
--------------------------------------------------------------
* `--json` stdout is the SDK `ThreadEvent` shape: a top-level object keyed
  `type`, no `id`, no `msg`. Eight types exist -- `thread.started`,
  `turn.started`, `turn.completed`, `turn.failed`, `item.started`,
  `item.updated`, `item.completed`, `error` -- and the `item.*` three carry an
  `item` whose kind is on `item.type` (never `item_type`; that spelling is a
  column in codex's history DB, though a pre-0.44 build emitted it and
  `_line_types` still reads it defensively). Observed live: `thread.started`
  with `thread_id`, `turn.started`, `item.completed` with an `agent_message`,
  `turn.completed` with a `usage` block of five token counters.
* **No event carries a `model` key** (openai/codex#14736 asked for one on
  `thread.started`; it is not implemented). The model is read from the
  ROLLOUT, and the requested `-m` value is recorded beside it -- a seat that
  asked for one model and was served another is a fact the record must be
  able to state.
* Rollout lines are `{"ordinal", "timestamp", "type", "payload"}`. `type` is
  `session_meta` (payload: `session_id`, `cwd`, `originator: "codex_exec"`,
  `cli_version`, `source: "exec"`, `model_provider`, `base_instructions`),
  `turn_context` (carries `model`), `response_item`, `event_msg`, or
  `world_state` -- the last being codex's environment snapshot, where the
  smoke read `agents_md: {}` and `cwd` equal to the temp scratch directory.
* `--output-schema <FILE>` takes a PATH to a JSON Schema and works: a smoke
  with `additionalProperties: false` returned exactly the object asked for.
  `-o/--output-last-message <FILE>` writes that final message to a file, and
  that file is `form-raw.json`.
* `codex login status` prints `Not logged in` when there is no sign-in.
* Cost: a one-line prompt was ~13k input tokens, 11k of it the cached system
  prompt, so a packet grade runs ~15-20k.

NOT BUILT, ON PURPOSE. `codex exec resume <SESSION_ID|--last> [PROMPT]`
continues a session; that is the door a future multi-turn Act-1 tester walks
through, and it is exactly the door a blind grader must not have. R213: one
agent, one turn, one packet -- a grader that has seen the previous board is no
longer reading this one cold.

GUARDRAIL-7 IS UNCHANGED. Nothing this seat returns is a claim about whether
a turn is fun, and a `SURVIVES` from it means not-yet-falsified and nothing
else.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
QA_DIR = REPO / "review" / "qa"
PROMPT_TEMPLATE = Path(__file__).resolve().parent / "qa_grader_prompt.md"
LOG_ROOT = Path(__file__).resolve().parent / "logs" / "seat"

# Ten minutes. A seat that has not answered by then is not thinking, and a
# timeout is a REFUSAL rather than a retry: a second attempt at the same
# packet is a second look at the same board, which is the one thing the
# funnel's first guard forbids.
TIMEOUT_S = 600

# The CLI's own default on 2026-08-28, read back out of a smoke's rollout.
# `-m` is passed ALWAYS and never left implicit, so the ledger's grader id
# names a model rather than "whatever codex defaulted to that month".
DEFAULT_MODEL = "gpt-5.6-sol"

# ------------------------------------------------------------ the guard ----

# (1) The `--json` stdout stream. Lifecycle events the seat may emit...
ALLOWED_EVENTS = frozenset({
    "thread.started", "turn.started", "turn.completed",
    "item.started", "item.updated", "item.completed",
})
# ...and the two that mean the run went wrong. Recognised as EVENTS so the
# guard names the failure honestly instead of calling a crash a tool call;
# they still refuse the seat, under `codex_error`.
FAILURE_EVENTS = frozenset({"turn.failed", "error"})

# The only two item types a blind grader produces. A grader thinks and then
# answers; anything else is a tool.
ALLOWED_ITEMS = frozenset({"agent_message", "reasoning"})

# (2) The rollout. Top-level line kinds. `world_state` is codex's own
# environment snapshot -- observed live on 0.150.1, and it is not a model
# action but a record OF one's surroundings. It is allowlisted and then read
# again below, because it is where `agents_md` is, and `agents_md` is the
# single best positive evidence that no project instruction reached the seat.
ALLOWED_ROLLOUT_TYPES = frozenset({
    "session_meta", "turn_context", "response_item", "event_msg",
    "world_state", "compacted",
})
# ...the model-facing items inside a `response_item`. `custom_tool_call`,
# `custom_tool_call_output`, `function_call`, `function_call_output`,
# `local_shell_call`, `web_search_call` and anything unlisted REFUSE.
ALLOWED_RESPONSE_ITEMS = frozenset({"message", "reasoning"})
# ...codex's own lifecycle inside an `event_msg`...
ALLOWED_EVENT_MSGS = frozenset({
    "session_configured", "task_started", "task_complete", "token_count",
    "user_message", "agent_message", "agent_message_delta",
    "agent_reasoning", "agent_reasoning_delta",
    "agent_reasoning_section_break",
    "item_started", "item_updated", "item_completed",
    # ONLY EVER SEEN ON A RESUMED THREAD, which is why it took EB-168's first
    # live session to find it: `seat grade` fires one-shot `codex exec` and
    # never resumes, so this file had never met a `codex exec resume`. It is a
    # SNAPSHOT OF THE THREAD'S OWN SETTINGS, not a model action -- and the
    # snapshot is evidence FOR the seat rather than against it: the payload
    # observed live on 0.150.1 carried a restricted read-only filesystem,
    # restricted network, the temp scratch as cwd and a null
    # `developer_instructions`. Refusing it made every blind run die on its
    # second action.
    "thread_settings_applied",
})
# ...and the item kinds an `item_*` event_msg may carry. CamelCase here: the
# rollout and the stdout stream do not share a spelling, and assuming they did
# is how an allowlist quietly becomes a pass-through.
ALLOWED_EVENT_MSG_ITEMS = frozenset({"UserMessage", "AgentMessage",
                                     "Reasoning"})

# (2b) The positive half of the rollout check: `world_state.payload.state`
# carries `agents_md`, which is EMPTY when no project instruction file was in
# reach. The smoke read `{}` with `-C` on a temp dir, and the model itself
# reported "project instructions: NONE". A non-empty map means an `AGENTS.md`
# was loaded, which for a blind grader in this repo would be the map to the
# design docs.
#
# (3) stderr. A tool call the sandbox REJECTED still logs, under these.
STDERR_TOOL_MARKERS = ("codex_core::tools::router", "exec_command")

REFUSAL_REASONS = {
    "cwd_not_empty": "the seat's scratch directory was not empty before the "
                     "run, so the sandbox had something to read",
    "cwd_inside_repo": "the seat's scratch directory is inside the repo, so "
                       "AGENTS.md and the design docs were in reach",
    "codex_missing": "no `codex` on PATH",
    # EB-227. Not a defect in the turn and not a failure of the seat: the
    # meter says this call would spend budget the harness was told to keep.
    "codex_budget_primary": "the Codex five-hour window is at or past the "
                            "stop line, so this call was not spent",
    "codex_budget_weekly": "the Codex WEEKLY window is at or past the stop "
                           "line, so this call was not spent -- a week spent "
                           "early is a week with no independent seat in it",
    "codex_failed": "codex exited non-zero",
    "codex_error": "the event stream carries an error or a failed turn",
    "codex_timeout": "the seat did not answer inside the timeout",
    "seat_no_transcript": "codex wrote no session rollout, so there is no "
                          "complete record to check blindness against -- and "
                          "no evidence is not good evidence",
    "seat_saw_instructions": "the rollout shows a project instruction file "
                             "(AGENTS.md) was loaded into the seat, which in "
                             "this repo is the map to the design docs",
    "seat_used_tools": "a transcript carries an event, item or log line "
                       "outside the allowlist, so this seat is not provably "
                       "blind",
    "no_form": "codex wrote no last message, or it did not parse as JSON",
    "turn_mismatch": "the form's turn_id is not the turn that was staged",
    "packet_mismatch": "the form's packet_sha256 is not the packet that was "
                       "handed over",
    # EB-169. The BRACES to `staged_turn`'s belt: the preflight already
    # refuses at `check` and at `stage`, but a packet on disk outlives the
    # command that wrote it, and this is the last place a defective face can
    # be stopped before a third party's quota is spent reading it.
    "open_face_defect": "the packet's hand holds a card with an OPEN defect "
                        "against its printed or runtime meaning, so a blind "
                        "seat would be asked to reason from a face the repo "
                        "already knows is wrong",
    # EB-190. The one refusal that is about WHO WROTE THE ROW rather than
    # about the seat's transcript or the packet's faces. R217 C fixes the
    # roles at two families and OPERATIONS' doctrine-seat block says why: a
    # seat that grades a row its own family authored has graded its own work,
    # and the outcome is not evidence. Klee slice 1 is the case.
    "seat_authored_row": "the turn under this seat carries a prototype row "
                         "whose `authored_by` names the seat's OWN model "
                         "family, so its answer would be a grade of its own "
                         "work rather than an independent reading",
}

# ------------------------------------------------- the review seat's brief --
#
# EB-190, third limb. The doctrine / pair-review seat's OUTPUT SHAPE is
# protocol (OPERATIONS "Doctrine seat protocol"), and until now it lived only
# in whichever prompt file the operator happened to write that round. A
# protocol re-typed per round is a protocol that drifts, and the drift already
# cost a round: the seat supplied Rummage's replacement text verbatim, it was
# used, and both of that arm's grades are provisional because of it.
#
# So the text ships here and is PREPENDED to every review prompt. It does not
# replace the caller's brief; it is the frame the brief goes in.
REVIEW_PROTOCOL = """\
THE PROTOCOL FOR THIS SEAT. It overrides anything below that conflicts with
it.

You are reading a proposal against a written charter or brief. Your output is,
PER ARM:

  * FOLLOWS, or REQUIRES_MODIFICATION; and
  * the CLAUSE you ruled against, named.

That is the whole output. You may NOT supply card text, a number, a mode, a
rewritten row, or any other remedy. A remedy you volunteer is DISCARDED
unread, and the reasoning that produced it is discarded with it -- so a
verdict that leans on your remedy is a verdict that gets thrown away. Where a
number has to be chosen it is derived by lifting a value off a shipped card,
and your only part in that is confirming that the derived row FOLLOWS.

WHY. Independence here is by MODEL FAMILY, author against grader (R217 C).
A seat that writes part of a row and then reads it has read its own work, and
the reading is not evidence. Naming the clause keeps you on the reading side
of that line; naming the fix moves you across it.
"""

# THE SEAT HAS TWO REVIEW JOBS AND THEY HAVE DIFFERENT OUTPUT SHAPES.
# `REVIEW_PROTOCOL` above is the DOCTRINE GATE: it reads a proposal against a
# charter BEFORE anything is built, and its whole output is a verdict and a
# clause. The other job is the PAIR READ, which runs AFTER a round -- shipped
# half against prototype half, with the forms, the verdicts and the live
# replays inline -- and its output is the round's five questions and
# RETURN / ADVANCE / ESCALATE.
#
# Klee ROUND 3 is where the single protocol bit. `EB-190` shipped one text and
# prepended it to every `seat review`, and its two strongest lines -- "It
# overrides anything below that conflicts with it" and "That is the whole
# output" -- do exactly what they say: the round-3 pair read came back as two
# lines, "PAIR A: FOLLOWS", "PAIR B: FOLLOWS", with no reading and no
# ADVANCE/RETURN, because the seat obeyed the protocol over the brief. Round 3
# was the first pair read since that door landed, so it was the first run that
# could find it.
#
# The half that is NOT negotiable is the same in both roles and is repeated
# verbatim below: the seat may not supply text, a number, a mode or a
# rewritten row, and a volunteered remedy is discarded. Only the OUTPUT SHAPE
# is role-specific, and the default is unchanged, so a caller that names no
# role still gets the doctrine gate exactly as before.
PAIR_REVIEW_PROTOCOL = """\
THE PROTOCOL FOR THIS SEAT. It overrides anything below that conflicts with
it, EXCEPT the numbered questions the brief asks you -- those are the output
shape and you answer them.

You are reading a COMPLETED blind-QA round: for each arm, a shipped half and a
prototype half of the same board, the graders' verbatim forms, the falsifier's
verdict on each form, and what the live game did when each graded line was
replayed. Your output is, PER ARM: the brief's numbered questions answered in
order, and a judgment of RETURN, ADVANCE or ESCALATE.

You may NOT supply card text, a number, a mode, a rewritten row, or any other
remedy. A remedy you volunteer is DISCARDED unread, and the reasoning that
produced it is discarded with it -- so a judgment that leans on your remedy is
a judgment that gets thrown away. You may say that an arm's BOARD did not ask
its question and RETURN it for that; you may not design the replacement board.
Where a number has to be chosen it is derived by lifting a value off a shipped
card, and that is not your job.

ADVANCE means the arm is worth asking again with whole-fight play. It is NOT
ship approval, not a balance reading and not validation, and nothing you write
here is any of those.

WHY. Independence here is by MODEL FAMILY, author against grader (R217 C).
A seat that writes part of a row and then reads it has read its own work, and
the reading is not evidence. Reading the evidence keeps you on the reading
side of that line; naming the fix moves you across it.
"""

REVIEW_ROLES: dict[str, str] = {
    "doctrine": REVIEW_PROTOCOL,
    "pair": PAIR_REVIEW_PROTOCOL,
}

# The phrases that make a brief an ASK FOR A REMEDY. Deliberately a short,
# literal list rather than anything clever: this guards an operator writing
# the round's prompt in a hurry, not an adversary, and a matcher subtle enough
# to refuse a legitimate brief would just be reworded around -- which is the
# failure it exists to prevent. Every entry is documented by being readable.
REMEDY_ASKS: tuple[str, ...] = (
    # Ask-SHAPED forms only. The bare verbs ("rewrite", "re-author") also
    # occur DESCRIPTIVELY in material a brief inlines -- a proposal's reader
    # table says "Re-author." of a row, a sheet comment says "this rewrite
    # is what completes R208" -- and the first shipped brief that inlined a
    # proposal was refused for exactly that (kokomi-kurage-memory, 2026-08-29).
    "rewrite the", "rewrite it", "rewrite this", "re-write the",
    "re-author the", "re-author it", "re-author this", "reauthor the",
    "re-draft the", "redraft the",
    "propose a fix", "propose an alternative", "propose a number",
    "propose new", "suggest a fix", "suggest an alternative",
    "suggest a number", "suggest new", "recommend a number",
    "what number", "which number", "pick a number", "choose a number",
    "write the text", "write new text", "new card text",
    "how would you fix", "how should it be worded",
)
# ...and the allowlist. An occurrence is EXEMPT when one of these appears in
# the NEGATION_WINDOW characters before it, because that is a brief FORBIDDING
# the remedy -- the protocol above being restated, not broken.
REMEDY_NEGATIONS: tuple[str, ...] = (
    "do not ", "do not, ", "don't ", "never ", "may not ", "must not ",
    "cannot ", "not asked to ", "without ", "no ", "not ",
)
NEGATION_WINDOW = 28


class SeatError(RuntimeError):
    """The seat could not be set up. Distinct from a REFUSAL, which is a
    finished run whose transcript disqualifies it."""


def _line_types(event: dict[str, Any]) -> tuple[str, str]:
    """`(shape, type)` for one stdout JSONL line, or `("", "")` if neither."""
    if isinstance(event.get("msg"), dict):
        # The app-server / mcp-server protocol, which `codex exec` does not
        # speak. Reading one means this is not the stream we launched. Named
        # rather than lumped in with `<unrecognised-line>` so the refusal can
        # say what it saw.
        return "msg", str(event["msg"].get("type") or "")
    etype = event.get("type")
    if isinstance(etype, str) and etype:
        item = event.get("item")
        if isinstance(item, dict):
            itype = item.get("type") or item.get("item_type") or ""
            return "item", f"{etype}/{itype}"
        return "event", etype
    return "", ""


def guard_events(events: list[dict[str, Any]]) -> tuple[list[str], bool,
                                                        dict[str, int]]:
    """Source (1): the `--json` stdout stream.

    Returns `(offenders, errored, counts)`. NOT sufficient on its own -- a
    tool call rejected by the sandbox never reaches this stream, which is
    measured fact and the reason `guard` reads two more sources.
    """
    counts: dict[str, int] = {}
    offenders: list[str] = []
    errored = False
    for event in events:
        shape, typ = _line_types(event)
        key = typ or "<unrecognised-line>"
        counts[key] = counts.get(key, 0) + 1
        if shape == "msg":
            offenders.append(f"msg:{typ or '<no type>'}")
        elif shape == "item":
            etype, _, itype = typ.partition("/")
            if etype in FAILURE_EVENTS:
                errored = True
            elif etype not in ALLOWED_EVENTS:
                offenders.append(etype)
            elif itype not in ALLOWED_ITEMS:
                offenders.append(itype or "<no item.type>")
        elif shape == "event":
            if typ in FAILURE_EVENTS:
                errored = True
            elif typ not in ALLOWED_EVENTS:
                offenders.append(typ)
        else:
            offenders.append("<unrecognised-line>")
    return offenders, errored, counts


def guard_rollout(lines: list[dict[str, Any]]) -> tuple[list[str],
                                                        dict[str, int]]:
    """Source (2): codex's own session rollout -- the COMPLETE record.

    Two allowlists, because the rollout carries the same turn twice in two
    vocabularies: the model-facing `response_item` stream (`message`,
    `reasoning`) and codex's `event_msg` lifecycle, whose `item_*` payloads
    name items in CamelCase. A tool call appears in the first as a
    `custom_tool_call`, and that is where it is caught.
    """
    counts: dict[str, int] = {}
    offenders: list[str] = []
    for line in lines:
        rtype = str(line.get("type") or "")
        payload = line.get("payload")
        payload = payload if isinstance(payload, dict) else {}
        ptype = str(payload.get("type") or "")
        key = f"{rtype or '<no type>'}/{ptype}" if ptype else \
            (rtype or "<no type>")
        counts[key] = counts.get(key, 0) + 1
        if rtype not in ALLOWED_ROLLOUT_TYPES:
            offenders.append(f"rollout:{rtype or '<no type>'}")
            continue
        if rtype == "response_item":
            if ptype not in ALLOWED_RESPONSE_ITEMS:
                offenders.append(ptype or "<no payload.type>")
        elif rtype == "event_msg":
            if ptype not in ALLOWED_EVENT_MSGS:
                offenders.append(ptype or "<no payload.type>")
                continue
            item = payload.get("item")
            if isinstance(item, dict):
                itype = str(item.get("type") or "")
                if itype not in ALLOWED_EVENT_MSG_ITEMS:
                    offenders.append(itype or "<no item.type>")
    return offenders, counts


def rollout_instructions(lines: list[dict[str, Any]]) -> list[str]:
    """Source (2b): the names of any project instruction files codex loaded.

    Empty is the passing answer, and it is a POSITIVE reading rather than the
    absence of a bad one: `world_state` states what the environment held, so
    an empty `agents_md` is evidence that nothing was there, not merely that
    nothing was recorded.
    """
    names: list[str] = []
    for line in lines:
        if line.get("type") != "world_state":
            continue
        payload = line.get("payload")
        state = (payload or {}).get("state") if isinstance(payload, dict) else None
        agents = (state or {}).get("agents_md") if isinstance(state, dict) else None
        if isinstance(agents, dict):
            names += [str(k) for k in agents]
        elif agents:
            names.append(str(agents))
    return sorted(set(names))


def guard_stderr(text: str) -> list[str]:
    """Source (3): the log line a REJECTED tool call leaves behind.

    Under a read-only sandbox on this box every shell command is blocked, so
    an attempt shows up here as a `Rejected(... blocked by policy)` from the
    tool router and nowhere on stdout. The seat is refused for the ATTEMPT,
    not for the rejection -- a sandbox that let the command through would be
    caught by the rollout instead.
    """
    hits: list[str] = []
    for line in text.splitlines():
        for marker in STDERR_TOOL_MARKERS:
            if marker in line:
                hits.append(f"stderr:{marker}")
                break
    return sorted(set(hits))


def guard(events: list[dict[str, Any]], rollout: list[dict[str, Any]] | None,
          stderr: str) -> tuple[str, list[str], dict[str, int]]:
    """All three sources at once. `reason` is `""` when the seat is clean."""
    offenders, errored, counts = guard_events(events)
    if rollout is None:
        # No rollout, no claim. Checked BEFORE the tool verdict so a missing
        # record can never be reported as a clean one.
        return "seat_no_transcript", sorted(set(offenders)), counts
    roll_offenders, roll_counts = guard_rollout(rollout)
    offenders = offenders + roll_offenders + guard_stderr(stderr)
    for key, n in roll_counts.items():
        counts[f"rollout:{key}"] = n
    if offenders:
        # Tools first: "this seat may not have been blind" is the graver
        # finding, and an error alongside it does not excuse it.
        return "seat_used_tools", sorted(set(offenders)), counts
    loaded = rollout_instructions(rollout)
    if loaded:
        return "seat_saw_instructions", loaded, counts
    if errored:
        return "codex_error", [], counts
    return "", [], counts


def rollout_model(lines: list[dict[str, Any]]) -> str:
    """The model the rollout says answered.

    Recorded BESIDE the requested model, never instead of it. The stdout
    stream carries no `model` key at all on 0.150.1, so this is the only
    place the served model can be read.
    """
    for line in lines:
        payload = line.get("payload")
        if isinstance(payload, dict):
            value = payload.get("model")
            if isinstance(value, str) and value:
                return value
        value = line.get("model")
        if isinstance(value, str) and value:
            return value
    return ""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Every JSONL line as a dict. A line that is not a JSON object is kept
    as `{}` so a guard sees it and refuses it, rather than skipped."""
    events: list[dict[str, Any]] = []
    if not path.is_file():
        return events
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            blob = json.loads(line)
        except json.JSONDecodeError:
            events.append({})
            continue
        events.append(blob if isinstance(blob, dict) else {})
    return events


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))


def thread_id(events: list[dict[str, Any]]) -> str:
    for event in events:
        if event.get("type") == "thread.started":
            return str(event.get("thread_id") or "")
    return ""


def find_rollout(tid: str, *, home: Path | None = None) -> Path | None:
    """`$CODEX_HOME/sessions/YYYY/MM/DD/rollout-<stamp>-<thread_id>.jsonl`.

    Located by THREAD ID, never by "the most recent file": two seats run
    minutes apart must not be able to certify each other's transcript.
    """
    if not tid:
        return None
    sessions = (home or codex_home()) / "sessions"
    if not sessions.is_dir():
        return None
    found = sorted(sessions.rglob(f"rollout-*-{tid}.jsonl"))
    return found[0] if found else None


# ----------------------------------------------------------- the prompt ----

def template_body(text: str | None = None) -> str:
    """The text between the two `---` rules in `qa_grader_prompt.md`.

    That file says "paste everything between the rules", so the rules are the
    contract and this reads them rather than restating the prompt. A second
    copy of the prompt in Python would drift from the one a human pastes, and
    then two graders would have answered two different questions.
    """
    raw = (text if text is not None
           else PROMPT_TEMPLATE.read_text(encoding="utf-8"))
    lines = raw.splitlines()
    rules = [i for i, ln in enumerate(lines) if ln.strip() == "---"]
    if len(rules) < 2:
        raise SeatError(f"{PROMPT_TEMPLATE.name} has no two `---` rules to "
                        f"read the prompt from")
    return "\n".join(lines[rules[0] + 1:rules[1]]).strip() + "\n"


def build_prompt(packet_md: str, packet_sha: str, *,
                 template: str | None = None) -> str:
    """The prompt, with `<PACKET>` and `<SHA>` substituted.

    `packet_md` goes in VERBATIM and nothing from `packet.json`'s envelope
    goes in at all -- the envelope carries `run_seed`, and the encounter is
    generated from it, so a grader that saw it could reproduce the board it
    is supposed to be reading cold.
    """
    body = template_body(template)
    return body.replace("<SHA>", packet_sha).replace("<PACKET>", packet_md)


def remedy_findings(text: str) -> list[str]:
    """Every phrase in a review brief that asks this seat for a REMEDY.

    Case-folded substring search with the negation allowlist applied. Returns
    the offending phrases, in the order the list declares them, so a refusal
    can print exactly what to delete.
    """
    # Only the brief's own prose is searched: markdown table rows, comment
    # lines and fenced code are inlined MATERIAL (a sheet, a proposal's
    # tables), not an ask, and are skipped line by line.
    kept: list[str] = []
    fenced = False
    for line in str(text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            fenced = not fenced
            continue
        if fenced or stripped.startswith("|") or stripped.startswith("#"):
            continue
        kept.append(line)
    low = chr(10).join(kept).casefold()
    found: list[str] = []
    for phrase in REMEDY_ASKS:
        start = 0
        while (i := low.find(phrase, start)) != -1:
            before = low[max(0, i - NEGATION_WINDOW):i]
            if not any(neg in before for neg in REMEDY_NEGATIONS):
                found.append(phrase)
                break
            start = i + len(phrase)
    return found


def build_review_prompt(body: str, role: str = "doctrine") -> str:
    """The protocol for this ROLE, then the caller's brief. Never the brief
    alone, and never a role the caller invented: an unknown role raises rather
    than falling back, because a silent fallback is how a pair read gets the
    doctrine gate's output shape without anyone noticing."""
    try:
        protocol = REVIEW_ROLES[role]
    except KeyError:
        raise SeatError(
            f"unknown review role {role!r}; the seat has two review jobs and "
            f"they have different output shapes: "
            f"{', '.join(sorted(REVIEW_ROLES))}") from None
    return protocol + "\n" + str(body or "")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ------------------------------------------------------ the reply schema ---

def form_schema() -> dict[str, Any]:
    """A JSON Schema for `qa_form.md`'s form, handed to `--output-schema`.

    It constrains the SHAPE and never the content: no enum on an answer, no
    minimum length, nothing that could push a grader toward one verdict.
    `designed_these_cards` is required and unconstrained on purpose -- R213's
    first guard is DECLARED, and a schema that forbade `true` would forbid
    the declaration rather than the conflict.

    `target` is `["string", "null"]` and REQUIRED rather than optional: a
    strict `additionalProperties: false` schema wants every property listed
    in `required`, and `staged_turn.load_form` only ever requires `card`. A
    null target reads as "this card needed none", which is what an omitted
    one meant.

    `exhaust` and `choose` (EB-170) are listed the same way and for the same
    reason: nullable, required by the strict schema, and meaning "this play
    raised no such prompt" when null. They are the only fields on the form
    that are about the game's MACHINERY rather than the grader's reasoning,
    and they are still stated in the printed vocabulary -- a card's title, an
    option's own text -- because that is all a blind grader has.
    """
    play = {
        "type": "object",
        "properties": {"card": {"type": "string"},
                       "target": {"type": ["string", "null"]},
                       "exhaust": {"type": ["string", "null"]},
                       "choose": {"type": ["string", "null"]}},
        "required": ["card", "target", "exhaust", "choose"],
        "additionalProperties": False,
    }
    grader = {
        "type": "object",
        "properties": {"id": {"type": "string"},
                       "kind": {"type": "string"},
                       "model": {"type": "string"},
                       "designed_these_cards": {"type": "boolean"}},
        "required": ["id", "kind", "model", "designed_these_cards"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "turn_id": {"type": "string"},
            "packet_sha256": {"type": "string"},
            "grader": grader,
            "chosen_line": {"type": "array", "items": play},
            "q1_what_did_you_play": {"type": "string"},
            "q2_other_line_considered": {"type": "string"},
            "q3_what_it_gave_up": {"type": "string"},
            "q4_different_intent": {"type": "string"},
            "q4_changed": {"type": "boolean"},
        },
        "required": ["turn_id", "packet_sha256", "grader", "chosen_line",
                     "q1_what_did_you_play", "q2_other_line_considered",
                     "q3_what_it_gave_up", "q4_different_intent",
                     "q4_changed"],
        "additionalProperties": False,
    }


# ---------------------------------------------------------- identity fill --

def fill_identity(raw: dict[str, Any], grader_id: str,
                  model: str) -> dict[str, Any]:
    """`form-raw.json` plus the three fields the model cannot know.

    ONLY `grader.id`, `grader.kind` and `grader.model`. Every other key --
    including `grader.designed_these_cards` -- is copied through untouched,
    and `test_understudy_seat` proves it. This function is the entire licence
    the wrapper has over a grader's answers, and it is deliberately three
    string assignments long.
    """
    form = json.loads(json.dumps(raw))
    grader = form.get("grader")
    grader = dict(grader) if isinstance(grader, dict) else {}
    grader["id"] = grader_id
    grader["kind"] = "llm"
    grader["model"] = model
    form["grader"] = grader
    return form


# ------------------------------------------------------------- the codex ---

def codex_path() -> str:
    found = shutil.which("codex")
    if not found:
        raise SeatError("no `codex` on PATH -- `npm install -g @openai/codex`")
    return found


def _codex_version(codex: str) -> str:
    try:
        done = subprocess.run([codex, "--version"], capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              timeout=60)
        return (done.stdout or done.stderr or "").strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return f"<{exc}>"


def _run(argv: list[str], *, stdin_text: str, stdout: Path, stderr: Path,
         cwd: Path, timeout: int = TIMEOUT_S) -> tuple[int, bool]:
    """Run codex, streaming stdout/stderr to files. `(returncode, timed_out)`.

    `cwd` is the PROCESS's directory as well as the agent's root: for the
    blind seat both are the empty scratch dir outside the repo, so no
    relative path resolves back into a checkout.
    """
    with stdout.open("w", encoding="utf-8", newline="") as out, \
            stderr.open("w", encoding="utf-8", newline="") as err:
        proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=out,
                                stderr=err, text=True, encoding="utf-8",
                                errors="replace", cwd=str(cwd),
                                env=os.environ.copy())
        try:
            proc.communicate(stdin_text, timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            return (proc.returncode if proc.returncode is not None else -1,
                    True)
    return proc.returncode, False


def session_dir(turn_id: str, *, root: Path | None = None) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    d = (root or LOG_ROOT) / f"{turn_id}-{stamp}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def scratch_root() -> Path:
    """An empty directory OUTSIDE every checkout.

    Outside is the requirement, not merely empty: codex reads `AGENTS.md`
    from its working root, and this repo has one that routes an agent to
    `CLAUDE.md` and the design docs.
    """
    return Path(tempfile.mkdtemp(prefix="gits-seat-")).resolve()


def is_inside_repo(path: Path) -> bool:
    try:
        Path(path).resolve().relative_to(REPO)
    except ValueError:
        return False
    return True


def grade_argv(codex: str, session: Path, scratch: Path, *,
               model: str = DEFAULT_MODEL) -> list[str]:
    """Every flag the blind seat runs with, in one place so the dry run and
    the real run cannot diverge -- and so a test can assert the list.

    `--ephemeral` is deliberately ABSENT: it suppresses the session rollout,
    and the rollout is the only complete record of what the seat did. A seat
    that hid its own transcript could not be certified blind.
    """
    return [
        codex, "exec",
        "-C", str(scratch),                # empty, and outside the repo
        "--skip-git-repo-check",           # ...so it is not a git repo
        "--sandbox", "read-only",          # write nothing
        "--ignore-user-config",            # no user MCP servers, no hooks
        "--ignore-rules",                  # no project execpolicy
        "--json",                          # transcript source (1)
        "--color", "never",
        "--output-schema", str(session / "form-schema.json"),
        "-o", str(session / "form-raw.json"),
        "-m", model,                       # always explicit; see DEFAULT_MODEL
        "-",                               # prompt on stdin
    ]


def review_argv(codex: str, out: Path, *, model: str = "") -> list[str]:
    """The REPO-VISIBLE seat. No `--json`, no schema, no scratch root, and
    `--ephemeral` is fine here because there is no blindness to prove."""
    argv = [
        codex, "exec",
        "-C", str(REPO),
        "--sandbox", "read-only",
        "--ignore-user-config",
        "--ephemeral",
        "--color", "never",
        "-o", str(out),
    ]
    if model:
        argv += ["-m", model]
    argv.append("-")
    return argv


# ----------------------------------------------------------------- verbs ---

def cmd_check(args) -> int:
    ready = False
    try:
        codex = codex_path()
    except SeatError as exc:
        print(f"codex: NOT FOUND ({exc})")
        print("NOT LOGGED IN")
        return 0
    print(f"codex: {codex}")
    print(f"version: {_codex_version(codex)}")
    try:
        done = subprocess.run([codex, "login", "status"], capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              timeout=60)
        status = (done.stdout or done.stderr or "").strip()
    except (OSError, subprocess.SubprocessError) as exc:
        status = f"<{exc}>"
    print(f"login: {status}")
    ready = bool(status) and "not logged in" not in status.lower()
    print(f"CODEX_HOME: {codex_home()}")
    print("READY" if ready else
          "NOT LOGGED IN -- run `codex login` once, interactively")
    return 0


def cmd_grade(args) -> int:
    turn_id = args.turn_id
    d = QA_DIR / turn_id
    packet_md_path = d / "packet.md"
    packet_json_path = d / "packet.json"
    if not packet_md_path.is_file():
        print(f"no packet at {packet_md_path}", file=sys.stderr)
        return 2
    packet_md = packet_md_path.read_text(encoding="utf-8")
    envelope: dict[str, Any] = {}
    if packet_json_path.is_file():
        envelope = json.loads(packet_json_path.read_text(encoding="utf-8"))
    packet_sha = str(envelope.get("packet_sha256") or sha256(packet_md))

    model = args.model or DEFAULT_MODEL
    grader_id = args.grader_id or f"codex-{model}-fresh"
    prompt = build_prompt(packet_md, packet_sha)

    session = session_dir(turn_id,
                          root=Path(args.log_root) if args.log_root else None)
    (session / "prompt.md").write_text(prompt, encoding="utf-8")
    (session / "form-schema.json").write_text(
        json.dumps(form_schema(), indent=1) + "\n", encoding="utf-8")

    try:
        codex = codex_path()
    except SeatError as exc:
        if not args.dry_run:
            print(f"seat error: {exc}", file=sys.stderr)
            return 2
        codex = "codex"

    scratch = scratch_root()
    argv = grade_argv(codex, session, scratch, model=model)

    seat: dict[str, Any] = {
        "turn_id": turn_id,
        "grader_id": grader_id,
        "session": str(session),
        "scratch_cwd": str(scratch),
        "argv": argv,
        "prompt_sha256": sha256(prompt),
        "packet_sha256": packet_sha,
        "model_requested": model,
        "model_observed": "",
        "codex_version": _codex_version(codex) if not args.dry_run else "",
        "codex_home": str(codex_home()),
        "timeout_s": TIMEOUT_S,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "guardrail": ("staged board: a blind seat's answer is a falsifier "
                      "input and never a claim about whether a turn is fun"),
    }

    # EB-169, and before codex is even located: a packet whose printed hand
    # holds a card with an OPEN face/runtime defect is not gradeable, and
    # spending a third party's quota to learn that is the round-2 mistake in
    # miniature. The import is LOCAL, exactly like `staged_turn`'s below --
    # the blind seat's module-level import graph stays as narrow as
    # `test_the_seat_cannot_reach_a_sheet` found it.
    from understudy import authorship, face_defects

    # EB-190, and BEFORE the face check for the same reason that one comes
    # before codex is located: this refusal is about whether the seat may read
    # this turn AT ALL, which is a prior question to whether the turn is
    # readable. Resolution is turn id -> the turn's yaml -> the prototype rows
    # it grants and mirrors; the PACKET cannot be the route, because it is
    # design-blind and prints titles rather than row ids. A turn holding only
    # shipped cards resolves to no rows and passes.
    proto_rows = authorship.rows_in_turn(turn_id)
    seat["prototype_rows"] = proto_rows
    hits = authorship.conflicts(model, proto_rows)
    if hits:
        seat["authorship_conflicts"] = hits
        return _refuse(seat, session, "seat_authored_row", hits)

    hand_titles = [str(c.get("title") or c.get("name") or "")
                   for c in ((envelope.get("board") or {}).get("hand") or [])]
    defects = face_defects.hits(hand_titles)
    if defects:
        seat["open_face_defects"] = defects
        return _refuse(seat, session, "open_face_defect",
                       [f"{h['matched']} -- {h['eb']}" for h in defects])

    if args.dry_run:
        seat["dry_run"] = True
        (session / "seat.json").write_text(
            json.dumps(seat, indent=1) + "\n", encoding="utf-8")
        print("DRY RUN -- nothing was executed")
        print(" ".join(argv))
        print(f"prompt:  {session / 'prompt.md'}")
        print(f"schema:  {session / 'form-schema.json'}")
        print(f"scratch: {scratch}")
        return 0

    # EB-227, and BEFORE the sandbox checks for the same reason EB-190 comes
    # before codex is located: whether this call may be spent AT ALL is prior
    # to whether the seat is set up correctly to spend it. The record lands in
    # `seat.json` either way, so the per-call cost of a graded turn is
    # learnable from a night's sessions rather than guessed.
    seat["codex_usage"], over_budget = budget_check()
    if over_budget:
        return _refuse(seat, session, over_budget[0], [over_budget[1]],
                       scratch=scratch)

    if is_inside_repo(scratch):
        return _refuse(seat, session, "cwd_inside_repo", [str(scratch)],
                       scratch=None)
    leftovers = list(scratch.iterdir())
    if leftovers:
        return _refuse(seat, session, "cwd_not_empty",
                       [p.name for p in leftovers], scratch=scratch)

    t0 = time.time()
    code, timed_out = _run(argv, stdin_text=prompt,
                           stdout=session / "events.jsonl",
                           stderr=session / "stderr.txt",
                           cwd=scratch)
    seat["wall_s"] = round(time.time() - t0, 1)
    seat["exit_code"] = code
    seat["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    events = read_jsonl(session / "events.jsonl")
    stderr_text = (session / "stderr.txt").read_text(encoding="utf-8",
                                                     errors="replace")
    tid = thread_id(events)
    seat["thread_id"] = tid

    # Copy the rollout BESIDE the run before reading it: the record that
    # certified a seat has to outlive the next `codex` invocation, and
    # $CODEX_HOME is codex's to prune.
    source = find_rollout(tid)
    rollout: list[dict[str, Any]] | None = None
    if source is not None:
        shutil.copyfile(source, session / "rollout.jsonl")
        seat["rollout_source"] = str(source)
        rollout = read_jsonl(session / "rollout.jsonl")

    reason, offenders, counts = guard(events, rollout, stderr_text)
    seat["event_counts"] = counts
    seat["model_observed"] = rollout_model(rollout or [])
    seat["guard"] = reason or "clean"
    seat["guard_offenders"] = offenders

    if timed_out:
        return _refuse(seat, session, "codex_timeout", [], scratch=scratch)
    if reason:
        return _refuse(seat, session, reason, offenders, scratch=scratch)
    if code != 0:
        return _refuse(seat, session, "codex_failed", [f"exit {code}"],
                       scratch=scratch)

    raw_path = session / "form-raw.json"
    try:
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("the last message is not a JSON object")
    except (OSError, ValueError) as exc:
        return _refuse(seat, session, "no_form", [str(exc)], scratch=scratch)

    # Refuse EARLY and say which. `staged_turn` checks the packet hash too,
    # but its refusal is about the FORM; this one is about the SEAT, and a
    # seat that answered a different packet is a wiring defect, not a grade.
    if str(raw.get("turn_id") or "") != turn_id:
        return _refuse(seat, session, "turn_mismatch",
                       [str(raw.get("turn_id"))], scratch=scratch)
    if str(raw.get("packet_sha256") or "") != packet_sha:
        return _refuse(seat, session, "packet_mismatch",
                       [str(raw.get("packet_sha256"))], scratch=scratch)

    form = fill_identity(raw, grader_id, seat["model_observed"] or model)
    blob = json.dumps(form, indent=1) + "\n"
    (session / "form.json").write_text(blob, encoding="utf-8")
    landed = d / f"form-{grader_id}.json"
    landed.write_text(blob, encoding="utf-8")

    seat["form"] = str(landed)
    seat["refused"] = ""
    (session / "seat.json").write_text(json.dumps(seat, indent=1) + "\n",
                                       encoding="utf-8")
    _drop_scratch(scratch)

    print(f"seat: {session}")
    print(f"form: {landed}")
    from understudy import staged_turn
    # `staged_turn` prints the verdict and its path itself; printing a
    # second one here would put two paths on screen for one grade.
    return staged_turn.main(["grade", turn_id, str(landed)])


def budget_check(*, quiet: bool = False) -> tuple[dict[str, Any],
                                                   tuple[str, str] | None]:
    """EB-227: read the seat's own meter, and say whether to spend the call.

    Returns `(record, over)` -- the record goes into whatever this call
    already writes (`seat.json` for `grade`, `<out>.usage.json` for
    `review`) so an overnight run learns what a call actually COSTS, and
    `over` is `(reason, detail)` when a stop line is reached.

    A MISSING ROLLOUT IS NOT A REFUSAL. The read is a convenience the harness
    gets for free from a file codex already wrote; a machine that has never
    run `codex`, or a pruned `$CODEX_HOME`, must not be able to stop a round.
    Log it and proceed.
    """
    from understudy import codex_usage

    usage = codex_usage.probe()
    if usage is None:
        if not quiet:
            print("codex budget: no rate-limit read available -- proceeding",
                  file=sys.stderr)
        return {"available": False,
                "primary_stop_percent": codex_usage.primary_stop(),
                "weekly_stop_percent": codex_usage.weekly_stop()}, None
    if not quiet:
        print(usage.summary())
    record = usage.record()
    record["available"] = True
    return record, usage.over()


def _drop_scratch(scratch: Path | None) -> None:
    if scratch is not None and not is_inside_repo(scratch):
        shutil.rmtree(scratch, ignore_errors=True)


def _refuse(seat: dict[str, Any], session: Path, reason: str,
            detail: list[str], *, scratch: Path | None = None) -> int:
    """A refused seat NEVER reaches `staged_turn grade`.

    The distinction matters: a refusal here says the seat is not a usable
    reading, which is not the same claim as the funnel's REFUSED verdict on a
    turn. Filing one as the other would put a wiring failure into the ledger
    as a design finding.
    """
    seat["refused"] = reason
    seat["refused_why"] = REFUSAL_REASONS.get(reason, reason)
    seat["refused_detail"] = detail
    session.mkdir(parents=True, exist_ok=True)
    (session / "seat.json").write_text(json.dumps(seat, indent=1) + "\n",
                                       encoding="utf-8")
    _drop_scratch(scratch)
    print(f"SEAT REFUSED  {reason}: {seat['refused_why']}", file=sys.stderr)
    if detail:
        print(f"  {', '.join(detail)}", file=sys.stderr)
    print(f"  {session / 'seat.json'}", file=sys.stderr)
    return 1


def cmd_review(args) -> int:
    prompt_path = Path(args.prompt_file)
    if not prompt_path.is_file():
        print(f"no prompt file at {prompt_path}", file=sys.stderr)
        return 2
    body = prompt_path.read_text(encoding="utf-8")

    # EB-190. Two refusals, both BEFORE codex is located, both about the seat
    # being asked to do the author's job.
    from understudy import authorship

    asks = remedy_findings(body)
    if asks:
        print(f"SEAT REFUSED  review_asks_for_a_remedy: this brief asks the "
              f"seat for a fix rather than for a verdict", file=sys.stderr)
        print(f"  {prompt_path}", file=sys.stderr)
        print(f"  offending phrase(s): {', '.join(asks)}", file=sys.stderr)
        print("  The seat answers FOLLOWS / REQUIRES_MODIFICATION and NAMES "
              "THE CLAUSE. A remedy it volunteers is discarded (R217 C; "
              "OPERATIONS 'Doctrine seat protocol').", file=sys.stderr)
        return 1

    # The rows this brief covers, resolved the same way `grade` resolves them
    # -- by the turn ids the brief names, plus any row named outright.
    model_for_family = args.model or DEFAULT_MODEL
    rows = authorship.rows_named_in(body)
    hits = authorship.conflicts(model_for_family, rows)
    if hits:
        print(f"SEAT REFUSED  seat_authored_row: "
              f"{REFUSAL_REASONS['seat_authored_row']}", file=sys.stderr)
        print(f"  {'; '.join(hits)}", file=sys.stderr)
        return 1

    role = getattr(args, "role", "doctrine") or "doctrine"
    prompt = build_review_prompt(body, role)
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    out = Path(args.out) if args.out else LOG_ROOT / f"review-{stamp}.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        codex = codex_path()
    except SeatError as exc:
        if not args.dry_run:
            print(f"seat error: {exc}", file=sys.stderr)
            return 2
        codex = "codex"
    argv = review_argv(codex, out, model=args.model or "")

    if args.dry_run:
        print("DRY RUN -- nothing was executed")
        print(" ".join(argv))
        print(f"would land: {out}")
        print(f"protocol:   {role} ({len(REVIEW_ROLES[role])} chars) "
              f"prepended; rows covered: {', '.join(rows) or '(none)'}")
        return 0

    # EB-227. The review role spends the same meter the grade role does, so
    # it reads it first and refuses in the shape this role already refuses in
    # -- printed and returning 1, never an exception that would kill a round
    # mid-flight. The record lands beside the review's own output.
    usage_record, over_budget = budget_check()
    try:
        out.with_suffix(".usage.json").write_text(
            json.dumps(usage_record, indent=1) + "\n",
            encoding="utf-8")
    except OSError:
        pass
    if over_budget:
        print(f"SEAT REFUSED  {over_budget[0]}: "
              f"{REFUSAL_REASONS[over_budget[0]]}", file=sys.stderr)
        print(f"  {over_budget[1]}", file=sys.stderr)
        print("  Raise it for one run with GITS_CODEX_PRIMARY_STOP / "
              "GITS_CODEX_WEEKLY_STOP, or wait for the window.",
              file=sys.stderr)
        return 1

    # NOT BLIND and not a grader: this seat reads the repo on purpose, so
    # there is no transcript guard here, and its output may never be filed as
    # a grade.
    code, timed_out = _run(argv, stdin_text=prompt,
                           stdout=out.with_suffix(".stdout.txt"),
                           stderr=out.with_suffix(".stderr.txt"),
                           cwd=REPO)
    if timed_out:
        print("review timed out", file=sys.stderr)
        return 1
    print(f"review: {out}")
    return code


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="is the seat available and signed in")
    c.set_defaults(func=cmd_check)

    g = sub.add_parser("grade", help="run the BLIND seat on a staged turn")
    g.add_argument("turn_id")
    g.add_argument("--model", default="",
                   help=f"passed to `codex -m`. Default {DEFAULT_MODEL!r}, "
                        f"always sent explicitly so the ledger names a model")
    g.add_argument("--grader-id", default="",
                   help="the ledger's grouping string. Default "
                        "`codex-<model>-fresh`, and it must be STABLE across "
                        "turns for the same seat")
    g.add_argument("--dry-run", action="store_true",
                   help="write the prompt and the schema, print the argv, "
                        "run nothing")
    g.add_argument("--log-root", default="",
                   help="where the session directory lands. Defaults to "
                        "understudy/logs/seat/; the tests point it at a "
                        "temporary directory")
    g.set_defaults(func=cmd_grade)

    r = sub.add_parser("review", help="run the REPO-VISIBLE seat (not blind)")
    r.add_argument("prompt_file")
    r.add_argument("--role", default="doctrine", choices=sorted(REVIEW_ROLES),
                   help="which of the seat's two review jobs this is. "
                        "`doctrine` (the default, and unchanged) reads a "
                        "proposal against a charter and answers FOLLOWS / "
                        "REQUIRES_MODIFICATION plus the clause. `pair` reads "
                        "a COMPLETED round -- forms, verdicts and replays -- "
                        "and answers the brief's questions plus RETURN / "
                        "ADVANCE / ESCALATE. Both forbid a remedy")
    r.add_argument("--model", default="")
    r.add_argument("--out", default="")
    r.add_argument("--dry-run", action="store_true")
    r.set_defaults(func=cmd_review)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except SeatError as exc:
        print(f"seat error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
