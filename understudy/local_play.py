"""A LOCAL model in the blind PLAYER's chair -- the `session` driver's second
backend.

`understudy/blindplay.py` already owns the whole of blind play: the scrubber,
the command grammar, the one-command-per-screen loop, the fight and run
records, `wire.json`, the budgets and the sealed record. What it had exactly
one of was a TESTER -- `CodexThread`, one `codex exec` thread for the run. This
module is a second object of that same shape, backed by an OpenAI-compatible
chat endpoint on this machine, and it changes nothing else. `Session` cannot
tell the two apart: both answer `identity()` and `send(prompt, schema)`, and
the prompt they are sent is byte-for-byte the same page, built by the same
builder, stamped by the same `prompt_sha256`.

WHY IT IS ONLY AN OPTION (READ THIS BEFORE QUOTING A RUN)
----------------------------------------------------------
The Codex seat's ADVANCE of 2026-08-29 covered the STAGED SINGLE-TURN tester
seat and nothing else, and it attached four conditions to that. Whole-run
blind play by a locally served model is a DIFFERENT and much longer-horizon
job -- forty screens of accumulated context instead of one board -- and no
seat has been asked whether the local model can hold it. So this backend
EXISTS, it is tested, and no round relies on it: it is a pick for [USER], not
a seat. Everything `local_seat.py` says about what a local reading is not --
not human validation, not balance evidence, not an approved doctrine seat --
is true here and is written into the record it seals.

THE THREE DIFFERENCES FROM THE CODEX THREAD, EACH OF THEM DELIBERATE
---------------------------------------------------------------------
  * **The thread is ours, not the vendor's.** `codex exec resume <id>` keeps
    the run's context on OpenAI's side. A chat endpoint is stateless, so the
    conversation is kept HERE, in `self.messages`, and grows by one user turn
    and one assistant turn per screen. That is the same guarantee stated the
    other way round: a blind PLAYER must have seen the previous board, which
    is the door `seat.py` deliberately did not walk through.
  * **Blindness is STRUCTURAL, not transcript-proved.** `seat.guard` refuses a
    codex run for `seat_used_tools` off three allowlisted sources. There is no
    transcript here to refuse from -- this is HTTP POSTs to a chat route with
    no tools, no filesystem and no repo root, so there is nothing the model
    could have read. That is an argument from the protocol's shape rather than
    from evidence, and `identity()["blindness"]` says so in words so a later
    reader cannot mistake it for the codex seat's guard.
  * **Reasoning is stripped before the parser and kept in the transcript.**
    `--reasoning-format deepseek` returns `reasoning_content` beside
    `content`; a server launched without it inlines `<think>...</think>`. Both
    are lifted out BEFORE the command is read, because a scratchpad that
    happens to contain the word `end turn` is not a command -- and both are
    written to the run's transcript row and to the turn's own
    `reasoning.txt`, because the scratchpad is the most interesting thing
    about this experiment and the least admissible.

NOTHING IS EVER TRUNCATED, IN EITHER DIRECTION
-----------------------------------------------
A prompt whose estimate does not fit `GITS_LOCAL_MODEL_CTX` REFUSES
(`prompt_exceeds_ctx`) and a reply that stopped at the answer ceiling REFUSES
(`answer_truncated`, the first of the tester seat's four conditions). Both
raise `BlindPlayError`, which `Session.run` catches as `seat_refused` -- so
the run stops with its fight records intact rather than playing on from a page
the model was only partly shown. A whole run's conversation grows, so the
window is the thing an operator sizes before a live run: at roughly 1-3k
tokens a screen, forty screens is a six-figure window, and this backend tells
the transcript when the prompt passes `WINDOW_WARN_FRACTION` of it.
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from pathlib import Path
from typing import Any, Mapping, Sequence

from understudy import blindplay, local_model, local_seat

# Playing is not grading, but it is not agentic tool use either: the tester
# picks one command off a page it can see all of. Greedy, and written into
# every artifact, so a re-read can tell a greedy decode from a sampled one.
PLAY_TEMPERATURE = 0.0

# One command plus a sentence of `thinking` is a few dozen tokens; a reasoning
# model asked for them can spend thousands getting there. A CEILING, not a
# target -- `finish_reason: "length"` refuses. Runaway thinking is bounded on
# the SERVER (`llama-server --reasoning-budget 4096`), because only the server
# can stop a model mid-scratchpad; this is the backstop that notices.
ENV_PLAY_TOKENS = "GITS_LOCAL_PLAY_TOKENS"
DEFAULT_PLAY_MAX_TOKENS = 4096

# `seat_family` is what R217 C is read off: independence is by MODEL FAMILY,
# author against tester, and `authorship.model_family()` answers `local` for
# everything this endpoint could serve -- which is the right answer for
# ATTRIBUTION and the wrong one for reading the independence rule off a
# record, because `local` names a chair and not a vendor. So the record
# carries both: `local` as the authorship family, and the vendor family here.
ENV_SEAT_FAMILY = "GITS_LOCAL_SEAT_FAMILY"
SEAT_FAMILIES: tuple[tuple[str, str], ...] = (
    ("qwen", "qwen"), ("llama", "llama"), ("mistral", "mistral"),
    ("mixtral", "mistral"), ("gemma", "gemma"), ("phi", "phi"),
    ("deepseek", "deepseek"), ("command-r", "cohere"), ("granite", "granite"),
    ("gpt-oss", "gpt-oss"), ("olmo", "olmo"), ("yi-", "yi"),
    ("glm", "glm"), ("nemotron", "nemotron"),
)

# Say it in the transcript BEFORE the refusal, so an operator watching a live
# run can see the window filling rather than discovering it at the stop.
WINDOW_WARN_FRACTION = 0.8

# `<think>...</think>` -- what a server launched WITHOUT `--reasoning-format
# deepseek` inlines into `content`. Non-greedy and DOTALL: a reply may carry
# more than one block, and every one of them comes out.
_THINK = re.compile(r"<(think|thinking|reasoning)>(.*?)</\1>",
                    re.DOTALL | re.IGNORECASE)

# The same shape a truncated scratchpad leaves behind: an opening tag with no
# close, because the answer stopped inside it. Everything from the tag on is
# reasoning, and what is left is almost certainly empty -- which is exactly
# what `answer_truncated` and `no_command` are for.
_THINK_OPEN = re.compile(r"<(think|thinking|reasoning)>(.*)\Z",
                         re.DOTALL | re.IGNORECASE)

# codex is handed the reply shape as `--output-schema`, a flag. A chat
# endpoint has two places to put it and this backend uses BOTH: the schema is
# APPENDED to the page as an instruction (the belt `local_seat.py` already
# established, and the only one that works on a server with no grammar
# support) and sent as `response_format` (the braces, where the server will
# take them). The SYSTEM PROMPT is untouched by either, so `prompt_sha256`
# pins the same text for both seats.
SCHEMA_INSTRUCTION = """

--------------------------------------------------------------------------
OUTPUT FORMAT. Answer with ONE JSON object and nothing else -- no prose
before it, no prose after it, no markdown fence. It must match this schema
exactly, including every required key:

{schema}
"""


class LocalPlayError(RuntimeError):
    """The local backend could not be set up. A SETUP fault, not a refusal."""


# ------------------------------------------------------------- the pieces ---

def play_max_tokens(env: "Mapping[str, str] | None" = None) -> int:
    """The answer ceiling. Junk falls back rather than raising mid-run."""
    return local_seat._tokens_env(ENV_PLAY_TOKENS, DEFAULT_PLAY_MAX_TOKENS,
                                  env)


def seat_family(model_name: str, env: "Mapping[str, str] | None" = None
                ) -> str:
    """The VENDOR family of the served model, for reading R217 C off a record.

    Derived from the name the endpoint reports, because that is the only thing
    on the wire that says what is actually answering. An override exists for
    the case the derivation cannot cover -- a GGUF renamed on disk -- and it
    is an override rather than the input, so the ordinary path records a fact
    instead of a claim. An unrecognised name is `unknown`, never a guess: a
    record that says `unknown` can be corrected, and one that says `qwen`
    because a fallback picked the commonest answer cannot.
    """
    e = os.environ if env is None else env
    override = str(e.get(ENV_SEAT_FAMILY) or "").strip().lower()
    if override:
        return override
    low = str(model_name or "").lower()
    for marker, family in SEAT_FAMILIES:
        if marker in low:
            return family
    return "unknown"


def _refuse_the_authors_own_weights(model_name: str) -> None:
    """R217 C on the SERVED NAME, and only for the author's own family.

    `authorship.MODEL_FAMILIES` resolves the `local:` prefix first and on
    purpose, so `local:claude-3-haiku.gguf` reads as the local chair -- which
    is right for attributing a reading and wrong for deciding whether the
    reading is independent. Running the author's weights on the author's
    machine is still the author. Narrow by construction: this refuses the one
    family that may not sit here and passes everything else, including a name
    the table has never heard of.
    """
    from understudy import authorship
    low = str(model_name or "").lower()
    for marker in authorship.MODEL_FAMILIES.get(authorship.AUTHOR_FAMILY, ()):
        if marker in low:
            raise blindplay.BlindPlayError(
                f"{model_name!r} is the AUTHOR's own model family "
                f"({authorship.AUTHOR_FAMILY!r}, matched on {marker!r}) and "
                f"may not be the tester however it is served -- independence "
                f"is by family, and serving the author's weights on the "
                f"author's machine does not create any (R217 C)")


def _answer_from_reasoning(reasoning: str, schema: dict) -> "dict | None":
    """The JSON reply, if the model left it as the TAIL of its scratchpad.

    Only the last line of the reasoning that opens an object is tried, and
    only if it carries every key the schema requires with a non-empty
    value: an object quoted mid-thought ("the schema is {command,
    thinking}") does not qualify, and a half-formed one raises inside
    `extract_json` and is treated as absent.
    """
    if not reasoning or "{" not in reasoning:
        return None
    last_open = reasoning.rfind("{")
    line_start = reasoning.rfind(chr(10), 0, last_open) + 1
    for text in (reasoning[line_start:].strip(), reasoning[last_open:]):
        try:
            blob = local_seat.extract_json(text)
        except ValueError:
            continue
        required = schema.get("required") or []
        if all(str(blob.get(k) or "").strip() for k in required):
            return blob
    return None


def strip_reasoning(text: str) -> tuple[str, str]:
    """`(answer, reasoning)` -- the scratchpad out, before the parser.

    Handles the two shapes a llama.cpp-served reasoning model produces in
    `content`: closed `<think>...</think>` blocks, and the unclosed opener a
    reply truncated mid-thought leaves behind. `reasoning_content`, which is
    what `--reasoning-format deepseek` returns, never reaches `content` at all
    and is joined on by the caller.
    """
    raw = str(text or "")
    thoughts: list[str] = []

    def _take(m: "re.Match[str]") -> str:
        thoughts.append(m.group(2).strip())
        return ""

    body = _THINK.sub(_take, raw)
    open_ended = _THINK_OPEN.search(body)
    if open_ended:
        thoughts.append(open_ended.group(2).strip())
        body = body[: open_ended.start()]
    return body.strip(), "\n\n".join(t for t in thoughts if t)


def server_version(client: "local_model.Client",
                   timeout_s: float = 3.0) -> tuple[str, str]:
    """`(version, source)` off the server's own routes, or `("", "")`.

    llama-server publishes a build string on `/props` and, on some builds, a
    `Server:` response header; neither is an OpenAI route, so both are read
    here rather than through `Client._request`. NOTHING IS INVENTED: a server
    that will not say gets an empty string and the record prints
    `(not read)`, which is the same discipline `build_version` follows for the
    mod build.
    """
    base = str(client.base_url or "").rstrip("/")
    for suffix in ("/v1", "/api/v1"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    for path in ("/props", "/health"):
        try:
            req = urllib.request.Request(base + path, method="GET")
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                header = str(resp.headers.get("Server") or "").strip()
                blob = json.loads(resp.read().decode("utf-8", "replace"))
        except Exception:                                     # noqa: BLE001
            continue
        if isinstance(blob, dict):
            for key in ("build_info", "server_version", "version",
                        "build", "llama_cpp_version"):
                value = str(blob.get(key) or "").strip()
                if value:
                    return value, f"the server's own `GET {path}` `{key}`"
        if header:
            return header, f"the server's own `Server:` header on `{path}`"
    return "", ""


# --------------------------------------------------------------- the seat ---

class LocalThread:
    """ONE conversation with a locally served model, for a whole blind run.

    The same object shape `blindplay.CodexThread` has -- `identity()`,
    `send(prompt, schema)`, `close()` -- so `blindplay.Session` drives either
    one without knowing which it has. Serial by construction: the server this
    was built for runs `--parallel 1` or `2` and one run is one caller.
    """

    def __init__(self, session: Path, *, client: "local_model.Client",
                 model: str = "", max_tokens: int = 0,
                 temperature: float = PLAY_TEMPERATURE,
                 transcript: Any = None):
        self.session = Path(session)
        self.client = client
        self.max_tokens = int(max_tokens or play_max_tokens())
        self.temperature = float(temperature)
        self.transcript = transcript
        if model:
            self.client.model = model
        try:
            self.model = self.client.resolve_model()
        except local_model.LocalModelError as exc:
            raise LocalPlayError(str(exc)) from None
        # R217 C, asked of the seat that is actually running, and asked TWICE
        # because the two questions have different right answers.
        #
        # THE ATTRIBUTION. `local:` is the spelling `local_seat` writes into
        # `grader.model` and the one `authorship.MODEL_FAMILIES` resolves
        # FIRST, so an open-weight name sharing a substring with a vendor's --
        # `gpt-oss` -- is read as the local chair and not as the Codex seat.
        blindplay.check_independent(f"local:{self.model}")
        # THE WEIGHTS. That prefix wins by design, which means it would also
        # mask the one model that may never sit here: serving the AUTHOR's own
        # weights locally does not make them independent of the author. So the
        # BARE served name is asked as well, and only ever to refuse the
        # author's family -- an unrecognised name is still fine, because
        # `unknown` is not `claude` and refusing every model this table has
        # not heard of would be a rule nobody ruled.
        _refuse_the_authors_own_weights(self.model)
        self.seat_family = seat_family(self.model)
        self.server_version, self.server_version_source = server_version(
            self.client)
        self.model_observed = ""
        self.schema_enforced = True
        self.turn = 0
        # THE THREAD. A chat route is stateless, so the run's context is this
        # list and nothing else; `Session` sends the brief on the first page
        # only, exactly as it does for codex, and every page after it is read
        # against what is already in here.
        self.messages: list[dict[str, str]] = []

    # -- the shape `Session` drives ---------------------------------------

    def identity(self) -> dict[str, Any]:
        """What the sealed record's identity block says about this tester.

        `model_requested` is the BACKEND, spelled `local`: a record has to say
        at a glance which chair played the run, and the served model's own
        name is the next line down. `seat_family` is the vendor family R217 C
        is read off, which `local` cannot answer.
        """
        return {"model_requested": "local",
                "model_observed": self.model_observed or self.model,
                "seat_family": self.seat_family,
                "backend": "local",
                "endpoint": self.client.base_url,
                "server_version": self.server_version,
                "server_version_source": self.server_version_source,
                "temperature": self.temperature,
                "schema_enforced": self.schema_enforced,
                "blindness": (
                    "STRUCTURAL, not evidentiary: this tester is a series of "
                    "HTTP chat requests with no tools, no filesystem and no "
                    "repo root, so there is nothing it could have read -- but "
                    "unlike the codex seat there is no transcript here "
                    "PROVING it, and `seat_used_tools` has no counterpart on "
                    "this route"),
                "seat_status": (
                    "AN OPTION, NOT A SEAT. The Codex seat's ADVANCE of "
                    "2026-08-29 covered the staged single-turn tester only; "
                    "whole-run blind play by a local model is a pick for "
                    "[USER] and no round rests on it")}

    def close(self) -> None:
        """Nothing to tear down: no scratch root, no process, no login."""

    # -- one screen --------------------------------------------------------

    def send(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        """One page in, one JSON reply out. Refuses rather than truncating."""
        self.turn += 1
        d = self.session / f"turn-{self.turn:03d}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "prompt.md").write_text(prompt, encoding="utf-8")
        (d / "schema.json").write_text(json.dumps(schema, indent=1) + "\n",
                                       encoding="utf-8")

        body = prompt + SCHEMA_INSTRUCTION.format(
            schema=json.dumps(schema, indent=1))
        messages = self.messages + [{"role": "user", "content": body}]
        estimate = local_model.messages_tokens(messages)
        ctx = int(self.client.ctx or 0)
        if ctx and estimate + self.max_tokens > ctx:
            # The FIRST of the tester seat's four conditions, in the run lane:
            # a page the model was only partly shown produces a command that
            # looks like a decision. Refuse, and keep the records already got.
            self._row(kind="local_refusal", reason="prompt_exceeds_ctx",
                      turn=self.turn, estimated_prompt_tokens=estimate,
                      ctx=ctx)
            raise blindplay.BlindPlayError(
                f"prompt_exceeds_ctx: the run's conversation no longer fits "
                f"-- ~{estimate} estimated prompt token(s) + "
                f"{self.max_tokens} reserved for the answer against "
                f"{local_model.ENV_CTX}={ctx}. NOTHING WAS TRUNCATED: a "
                f"tester played on from a page it was half-shown would look "
                f"exactly like a tester making a decision. Raise the "
                f"server's -c and {local_model.ENV_CTX} together, or run a "
                f"shorter Act.")
        if ctx and estimate > ctx * WINDOW_WARN_FRACTION:
            self._row(kind="local_window", turn=self.turn,
                      estimated_prompt_tokens=estimate, ctx=ctx)

        reply = self._chat(messages, schema, d)
        (d / "reply.txt").write_text(reply.text, encoding="utf-8")

        answer, inline = strip_reasoning(reply.text)
        reasoning = "\n\n".join(x for x in (reply.reasoning, inline) if x)
        if reasoning:
            (d / "reasoning.txt").write_text(reasoning, encoding="utf-8")
        self.model_observed = reply.model_observed or self.model_observed

        # RECORDED, NEVER PARSED, and written to the run's own transcript so
        # the scratchpad sits beside the command it produced.
        self._row(kind="local_reply", turn=self.turn,
                  finish_reason=reply.finish_reason,
                  prompt_tokens=reply.prompt_tokens,
                  completion_tokens=reply.completion_tokens,
                  wall_s=round(reply.wall_s, 1),
                  reasoning_chars=len(reasoning), reasoning=reasoning,
                  answer_chars=len(answer))

        if reply.finish_reason == "length":
            self._row(kind="local_refusal", reason="answer_truncated",
                      turn=self.turn, ceiling=self.max_tokens)
            raise blindplay.BlindPlayError(
                f"answer_truncated: the reply stopped at the "
                f"{self.max_tokens}-token ceiling, so there is no command "
                f"-- a partial answer is not a partial decision "
                f"(${ENV_PLAY_TOKENS} raises the ceiling; runaway thinking "
                f"is the server's --reasoning-budget, not this)")

        try:
            blob = local_seat.extract_json(answer)
        except ValueError as exc:
            # THE ANSWER IN THE SCRATCHPAD. Seen live 2026-09-02 (session
            # `kokomi-r3-local-a`, turn 7): the served model wrote its whole
            # JSON reply as the last line of its thinking, closed the think
            # block, and stopped with `finish_reason: "stop"` and an EMPTY
            # `content`. The command is right there; refusing it would
            # throw a real decision away for a formatting slip the model
            # did not repeat on the six turns before. So the reasoning tail
            # is read ONCE, as a fallback, and the record says so in its own
            # row -- the scratchpad is otherwise never parsed.
            blob = _answer_from_reasoning(reasoning, schema)
            if blob is None:
                self._row(kind="local_refusal", reason="no_reply_json",
                          turn=self.turn, detail=str(exc))
                raise blindplay.BlindPlayError(
                    f"no_reply_json: the reply carries no JSON object once "
                    f"the reasoning is stripped, so there is nothing to read "
                    f"as a command ({exc}); the raw reply is at "
                    f"{d / 'reply.txt'}")
            self._row(kind="local_answer_from_reasoning", turn=self.turn,
                      detail="content was empty; the JSON reply was the "
                             "tail of the reasoning block")
        missing = [k for k in (schema.get("required") or [])
                   if not str(blob.get(k) or "").strip()
                   and not isinstance(blob.get(k), list)]
        if missing:
            self._row(kind="local_refusal", reason="reply_incomplete",
                      turn=self.turn, missing=missing)
            raise blindplay.BlindPlayError(
                f"reply_incomplete: the reply is JSON but is missing "
                f"{missing}, which the schema requires")
        (d / "reply.json").write_text(json.dumps(blob, indent=1) + "\n",
                                      encoding="utf-8")

        # THE THREAD GROWS BY THE ANSWER, NOT BY THE SCRATCHPAD. Feeding a
        # model its own reasoning back is neither what codex does nor what the
        # chat protocol means by an assistant turn, and it would double the
        # window every screen.
        self.messages = messages + [{"role": "assistant",
                                     "content": json.dumps(blob)}]
        return blob

    # -- transport ---------------------------------------------------------

    def _chat(self, messages: Sequence[Mapping[str, Any]],
              schema: dict[str, Any], d: Path) -> "local_model.Reply":
        """One completion, with the schema in the braces where it is taken.

        `response_format: json_schema` is llama.cpp's grammar door and is the
        strongest constraint available; a server that does not know it answers
        HTTP 400 rather than ignoring it, so ONE retry goes without it and the
        record says `schema_enforced: false`. The schema is in the prompt
        either way, so the retry is a weaker constraint and never a missing
        one.
        """
        fmt = {"type": "json_schema",
               "json_schema": {"name": "blind_play_reply", "strict": True,
                               "schema": schema}}
        (d / "request.json").write_text(
            json.dumps({"model": self.client.model,
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                        "messages": len(messages),
                        "response_format": fmt}, indent=1) + "\n",
            encoding="utf-8")
        try:
            return self.client.chat(messages, max_tokens=self.max_tokens,
                                    temperature=self.temperature,
                                    response_format=fmt)
        except local_model.ContextError as exc:
            raise blindplay.BlindPlayError(f"prompt_exceeds_ctx: {exc}")
        except local_model.LocalModelError as exc:
            if not _rejected_the_schema(str(exc)):
                raise blindplay.BlindPlayError(
                    f"endpoint_error: {exc}") from None
            self.schema_enforced = False
            self._row(kind="local_schema", turn=self.turn, enforced=False,
                      detail=str(exc)[:300])
        try:
            return self.client.chat(messages, max_tokens=self.max_tokens,
                                    temperature=self.temperature)
        except local_model.ContextError as exc:
            raise blindplay.BlindPlayError(f"prompt_exceeds_ctx: {exc}")
        except local_model.LocalModelError as exc:
            raise blindplay.BlindPlayError(f"endpoint_error: {exc}") from None

    def _row(self, **row: Any) -> None:
        """One transcript row, where a transcript has been attached."""
        if self.transcript is not None:
            self.transcript.write(**row)


def _rejected_the_schema(detail: str) -> bool:
    """Did the server refuse the REQUEST SHAPE rather than the request?

    Narrow on purpose. A 400 naming `response_format` or `json_schema` is a
    server without grammar support; every other failure -- a refused
    connection, a 500, a timeout -- is a fault to report rather than a reason
    to send the same thing again with a weaker constraint.
    """
    low = detail.lower()
    if "http 400" not in low and "http 422" not in low and \
            "http 501" not in low:
        return False
    return "response_format" in low or "json_schema" in low or \
        "grammar" in low or "unsupported" in low or "unknown field" in low


# --------------------------------------------------------------- the door ---

def thread(session: Path, *, model: str = "", max_tokens: int = 0,
           env: "Mapping[str, str] | None" = None) -> LocalThread:
    """The tester `blindplay session --backend local` hands to `Session`.

    `GITS_LOCAL_MODEL_URL` is REQUIRED and has no default here for the reason
    `local_model.Client.from_env` gives: a harness that silently fell back to
    localhost would spend a quarter of an hour timing out against nothing and
    the operator would read the timeout as a model problem.
    """
    try:
        client = local_model.Client.from_env(env)
    except local_model.LocalModelError as exc:
        raise LocalPlayError(str(exc)) from None
    return LocalThread(session, client=client, model=model,
                       max_tokens=max_tokens)
