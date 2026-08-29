"""A LOCAL model behind an OpenAI-compatible endpoint, as a third grader seat.

WHY THIS EXISTS. The independent seat (`understudy/seat.py`) is a third
party's quota, and when that quota is out the funnel stops. A model running on
this machine has no quota and no vendor: it can read a packet at three in the
morning for the cost of electricity. It is also, on today's hardware, a good
deal weaker than either hosted seat, so what it produces is SUBJECTIVE
FEEDBACK and a sanity comparison -- never a grade that stands on its own, and
never balance evidence. `tools/local_model_sanity.py` is the whole point: run
it on turns that are already CLOSED, with two recorded readings beside it, and
see whether it agrees.

WHAT IT TALKS TO. `POST <base>/v1/chat/completions` and `GET <base>/v1/models`
-- the two routes llama.cpp's `llama-server`, Ollama and LM Studio all speak.
The stack this was built for is `llama-server` (b10433, native Windows CUDA)
on port 8010 serving unsloth's Qwen3.8-27B-UD-Q4_K_XL, launched `--parallel 1`
so the server answers ONE request at a time. Every caller here is therefore
SERIAL by construction; there is no fan-out and adding one would queue behind
itself and look like a hang.

STDLIB ONLY. `urllib.request`, because a grader wrapper that drags a vendor
SDK into the tree is a dependency the funnel does not need and a second thing
to pin.

THE THREE THINGS THIS MODULE REFUSES TO DO QUIETLY
--------------------------------------------------
  * **Truncate.** A prompt whose token estimate does not fit
    `GITS_LOCAL_MODEL_CTX` raises `ContextError` naming both numbers. A
    silently truncated packet is a grader answering a board it was not shown,
    and the answer would look exactly like a grade.
  * **Guess which model answered.** Every reply carries the server's OWN
    reported model beside the one that was asked for, and both go into the
    artifact -- `model_requested` / `model_observed`, the same pair
    `seat grade` writes for codex.
  * **Grade on reasoning.** `--reasoning-format deepseek` makes llama.cpp
    return a `reasoning_content` field beside `content`. It is RECORDED as
    `reasoning` and never parsed: a form is the `content`, and a scratchpad
    that happened to contain JSON is not an answer.

SAMPLING. The bakeoff pinned temp 1.0 / top_p 0.95 / top_k 20 for agentic
work. Grading is not agentic work: `temperature=0` is the default here and is
written into every artifact, so a re-read six months later can tell a greedy
decode from a sampled one.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

# The llama-server the bakeoff stood up. Overridable, and the override is the
# expected case for an Ollama (`:11434`) or LM Studio (`:1234`) box.
DEFAULT_URL = "http://localhost:8010/v1"

# Qwen3.8-27B's native window with a q8_0 KV cache, which is what -c passes.
# This is a REFUSAL threshold, not a request: nothing here asks the server to
# allocate it.
DEFAULT_CTX = 262144

# Generous on purpose. 27B at ~39-57 tok/s decode means a 2k-token form takes
# the better part of a minute, and a doctrine review of a 160KB brief is
# minutes. A timeout that fires mid-answer costs the whole call.
DEFAULT_TIMEOUT_S = 1800

# Conservative: 3.5 characters per token UNDER-counts nothing in practice for
# English prose and JSON, where the real figure is nearer 4. The guard is
# meant to refuse early rather than to be accurate, and an estimator that
# rounded the other way would let a prompt through that the server then
# truncated in silence.
CHARS_PER_TOKEN = 3.5

# Connection refused is the ordinary state of this endpoint (the server is
# started by hand), so a retry loop must not paper over it: three tries, short
# backoff, and then say plainly that nothing is listening.
RETRIES = 3
BACKOFF_S = 1.5

ENV_URL = "GITS_LOCAL_MODEL_URL"
ENV_NAME = "GITS_LOCAL_MODEL_NAME"
ENV_CTX = "GITS_LOCAL_MODEL_CTX"
ENV_TIMEOUT = "GITS_LOCAL_MODEL_TIMEOUT"


class LocalModelError(RuntimeError):
    """The endpoint could not be reached, or answered something unusable."""


class ContextError(LocalModelError):
    """The prompt does not fit the declared context window. Never truncated."""


# ------------------------------------------------------------- the slug ----

def slug(name: str) -> str:
    """A stable, filename-safe grader suffix for a served model name.

    `qwen3.8-27b-UD-Q4_K_XL.gguf` -> `qwen3-8-27b-ud-q4-k-xl`. Stable is the
    requirement rather than pretty: the slug lands in `form-<id>.json` and in
    the ledger's grouping column, and a slug that moved between rounds would
    split one seat's history into two graders.
    """
    low = str(name or "").strip().lower()
    for suffix in (".gguf", ".bin", ".safetensors"):
        if low.endswith(suffix):
            low = low[: -len(suffix)]
    # A served name is often a PATH (`/models/qwen3.8-27b/...`) or a tag
    # (`qwen3:27b`). Take the last path segment, keep the tag.
    low = low.replace("\\", "/").rsplit("/", 1)[-1]
    out: list[str] = []
    for ch in low:
        out.append(ch if (ch.isalnum()) else "-")
    text = "".join(out)
    while "--" in text:
        text = text.replace("--", "-")
    return text.strip("-") or "unknown"


def grader_id(model: str) -> str:
    """`local-<slug>` -- the third seat's id, beside `opus-5-fresh` and
    `codex-gpt-5.6-sol-fresh`."""
    return f"local-{slug(model)}"


def estimate_tokens(text: str) -> int:
    return int(math.ceil(len(str(text or "")) / CHARS_PER_TOKEN))


def messages_tokens(messages: Sequence[Mapping[str, Any]]) -> int:
    """The estimate for a whole message list, plus the per-message envelope.

    Four tokens per message is the figure OpenAI's own counting note uses for
    the role/delimiter overhead; it is small and it is on the safe side.
    """
    return sum(estimate_tokens(m.get("content")) + 4 for m in messages)


# ------------------------------------------------------------- the reply ---

@dataclass
class Reply:
    """One completion, with everything an artifact has to record about it."""

    text: str
    reasoning: str = ""
    model_requested: str = ""
    model_observed: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    wall_s: float = 0.0
    temperature: float = 0.0
    finish_reason: str = ""
    attempts: int = 1
    estimated_prompt_tokens: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "model_requested": self.model_requested,
            "model_observed": self.model_observed,
            "temperature": self.temperature,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "estimated_prompt_tokens": self.estimated_prompt_tokens,
            "wall_s": round(self.wall_s, 1),
            "finish_reason": self.finish_reason,
            "attempts": self.attempts,
            # RECORDED, never parsed. See the module docstring.
            "reasoning": self.reasoning,
        }


# ------------------------------------------------------------ the client ---

@dataclass
class Client:
    """One `llama-server`-shaped endpoint. Serial by construction."""

    base_url: str = ""
    model: str = ""
    ctx: int = DEFAULT_CTX
    timeout_s: int = DEFAULT_TIMEOUT_S
    retries: int = RETRIES
    backoff_s: float = BACKOFF_S
    _calls: list[dict[str, Any]] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self.base_url = str(self.base_url or "").rstrip("/")

    # -- construction ------------------------------------------------------
    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Client":
        """Built from the four env vars. Raises if the URL is unset.

        UNSET IS AN ERROR AND NOT A DEFAULT: a harness that silently fell back
        to localhost would spend a quarter of an hour timing out against
        nothing, and the operator would read the timeout as a model problem.
        `DEFAULT_URL` is what the operator is TOLD to set, not what is assumed.
        """
        e = os.environ if env is None else env
        url = str(e.get(ENV_URL) or "").strip()
        if not url:
            raise LocalModelError(
                f"{ENV_URL} is unset. Point it at an OpenAI-compatible base "
                f"URL -- for this repo's llama-server that is "
                f"{DEFAULT_URL!r} (Ollama: http://localhost:11434/v1, "
                f"LM Studio: http://localhost:1234/v1)")
        return cls(
            base_url=url,
            model=str(e.get(ENV_NAME) or "").strip(),
            ctx=_int_env(e, ENV_CTX, DEFAULT_CTX),
            timeout_s=_int_env(e, ENV_TIMEOUT, DEFAULT_TIMEOUT_S),
        )

    # -- transport ---------------------------------------------------------
    def _post(self, path: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self._request(path, json.dumps(payload).encode("utf-8"))

    def _request(self, path: str, body: bytes | None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json"}
        last: Exception | None = None
        for attempt in range(1, max(1, self.retries) + 1):
            req = urllib.request.Request(url, data=body, headers=headers,
                                         method="POST" if body else "GET")
            try:
                with urllib.request.urlopen(req,
                                            timeout=self.timeout_s) as resp:
                    raw = resp.read().decode("utf-8", errors="replace")
                blob = json.loads(raw)
                if not isinstance(blob, dict):
                    raise LocalModelError(f"{url} did not answer with a JSON "
                                          f"object")
                blob["_attempts"] = attempt
                return blob
            except urllib.error.HTTPError as exc:
                # An HTTP status is the SERVER's answer, not a connection
                # fault: retrying a 400 sends the same bad request again.
                detail = exc.read().decode("utf-8", errors="replace")[:400]
                raise LocalModelError(
                    f"{url} answered HTTP {exc.code}: {detail}") from exc
            except (urllib.error.URLError, OSError, ValueError) as exc:
                last = exc
                if attempt < max(1, self.retries):
                    time.sleep(self.backoff_s * attempt)
        raise LocalModelError(
            f"no answer from {url} after {max(1, self.retries)} attempt(s): "
            f"{last}. Is the local model server running? "
            f"({ENV_URL}={self.base_url!r})")

    # -- routes ------------------------------------------------------------
    def models(self) -> list[str]:
        """Every model id `GET /models` reports, in the order it reports."""
        blob = self._request("/models", None)
        out: list[str] = []
        for row in (blob.get("data") or []):
            if isinstance(row, dict) and row.get("id"):
                out.append(str(row["id"]))
        return out

    def resolve_model(self) -> str:
        """The model to ASK FOR: the configured name, else the served one.

        llama-server serves exactly one model and reports it by whatever name
        it was loaded under, so leaving `GITS_LOCAL_MODEL_NAME` unset and
        reading `/models` is the ordinary path -- and it means the grader id
        names the file that actually answered.
        """
        if self.model:
            return self.model
        served = self.models()
        if not served:
            raise LocalModelError(
                f"{self.base_url}/models reported no models, and "
                f"{ENV_NAME} is unset, so there is no model name to ask for "
                f"or to build a grader id from")
        self.model = served[0]
        return self.model

    def chat(self, messages: Sequence[Mapping[str, Any]], *,
             max_tokens: int, temperature: float = 0.0,
             model: str = "") -> Reply:
        """One completion. Refuses rather than truncates; never streams."""
        want = model or self.model or self.resolve_model()
        estimate = messages_tokens(messages)
        if self.ctx and estimate + max_tokens > self.ctx:
            raise ContextError(
                f"this prompt does not fit: ~{estimate} estimated prompt "
                f"token(s) + {max_tokens} reserved for the answer = "
                f"~{estimate + max_tokens}, against {ENV_CTX}={self.ctx}. "
                f"NOTHING WAS TRUNCATED -- a grader answering a packet it was "
                f"only partly shown produces a form that looks like a grade. "
                f"Raise the server's -c and {ENV_CTX} together, or grade a "
                f"shorter packet.")

        payload: dict[str, Any] = {
            "model": want,
            "messages": [dict(m) for m in messages],
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
            "stream": False,
        }
        t0 = time.time()
        blob = self._post("/chat/completions", payload)
        wall = time.time() - t0

        choices = blob.get("choices") or []
        if not choices or not isinstance(choices[0], dict):
            raise LocalModelError(
                f"the endpoint answered with no choices: "
                f"{json.dumps(blob)[:400]}")
        message = choices[0].get("message") or {}
        usage = blob.get("usage") or {}
        reply = Reply(
            text=str(message.get("content") or ""),
            reasoning=str(message.get("reasoning_content")
                          or message.get("reasoning") or ""),
            model_requested=want,
            model_observed=str(blob.get("model") or ""),
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            completion_tokens=int(usage.get("completion_tokens") or 0),
            wall_s=wall,
            temperature=float(temperature),
            finish_reason=str(choices[0].get("finish_reason") or ""),
            attempts=int(blob.get("_attempts") or 1),
            estimated_prompt_tokens=estimate,
        )
        self._calls.append(reply.as_dict())
        return reply

    @property
    def calls(self) -> list[dict[str, Any]]:
        """Every completion this client made, for an artifact's call log."""
        return list(self._calls)


def _int_env(env: Mapping[str, str], key: str, default: int) -> int:
    raw = str(env.get(key) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise LocalModelError(f"{key}={raw!r} is not an integer") from exc


# ---------------------------------------------------------------- probe ----

PROBE_PROMPT = ("Answer with one short sentence and nothing else: what is "
                "the capital of France?")


def cmd_probe(args) -> int:
    try:
        client = Client.from_env()
    except LocalModelError as exc:
        print(f"local model: {exc}", file=sys.stderr)
        return 2
    print(f"url:     {client.base_url}")
    print(f"ctx:     {client.ctx} ({ENV_CTX})")
    print(f"timeout: {client.timeout_s}s ({ENV_TIMEOUT})")
    try:
        served = client.models()
    except LocalModelError as exc:
        print(f"models:  UNREACHABLE -- {exc}", file=sys.stderr)
        return 1
    print(f"models:  {', '.join(served) or '(none reported)'}")
    try:
        model = client.resolve_model()
    except LocalModelError as exc:
        print(f"model:   {exc}", file=sys.stderr)
        return 1
    print(f"model:   {model}")
    print(f"grader:  {grader_id(model)}")
    if args.no_chat:
        return 0
    try:
        reply = client.chat([{"role": "user", "content": PROBE_PROMPT}],
                            max_tokens=args.max_tokens, temperature=0.0)
    except LocalModelError as exc:
        print(f"chat:    FAILED -- {exc}", file=sys.stderr)
        return 1
    print(f"reply:   {reply.text.strip()[:300]!r}")
    if reply.reasoning:
        print(f"reasoning: {len(reply.reasoning)} chars (recorded, never "
              f"graded)")
    print(f"observed model: {reply.model_observed or '(not reported)'}")
    print(f"tokens:  prompt {reply.prompt_tokens}, completion "
          f"{reply.completion_tokens}")
    print(f"wall:    {reply.wall_s:.1f}s")
    if reply.completion_tokens and reply.wall_s:
        print(f"decode:  ~{reply.completion_tokens / reply.wall_s:.1f} tok/s")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("probe", help="list models and send a one-line prompt")
    p.add_argument("--max-tokens", type=int, default=64)
    p.add_argument("--no-chat", action="store_true",
                   help="list models and stop; send nothing")
    p.set_defaults(func=cmd_probe)
    # `--probe` as a bare flag too, because that is what the brief asks for
    # and because a one-verb tool should not need its verb typed.
    raw = list(argv) if argv is not None else sys.argv[1:]
    # `--probe` and a bare call both mean the one verb this module has.
    raw = ["probe" if a == "--probe" else a for a in raw] or ["probe"]
    args = ap.parse_args(raw)
    if not getattr(args, "func", None):
        ap.print_help()
        return 2
    try:
        return args.func(args)
    except LocalModelError as exc:
        print(f"local model: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
