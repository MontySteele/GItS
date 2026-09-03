"""The LOCAL backend for whole-run blind play, end to end, with NO GAME AND NO
MODEL SERVER.

Two doubles do the whole job and neither of them is new:

  * the GAME is `blindplay.ScriptedWire` over the same recorded
    `review/qa/<turn>/observed.json` fixtures `test_understudy_blindplay.py`
    drives, so the pages the local tester reads are the pages the codex seat
    would have read; and
  * the MODEL is a real HTTP server on a loopback port -- `_StubEndpoint`
    below -- speaking `GET /v1/models`, `GET /props` and `POST
    /v1/chat/completions`. A stub rather than a monkeypatched client on
    purpose: the thing most likely to be wrong about a new backend is the
    WIRE (does it send `response_format`, does it read `reasoning_content`,
    does it notice `finish_reason: "length"`), and a patched method proves
    none of that.

So this file exercises the loop the operator's live run will exercise, minus
the two things only tonight can prove: a real model's judgement, and a real
llama-server's behaviour under a run-long conversation.
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from understudy import blindplay, local_model, local_play

REPO = Path(__file__).resolve().parents[2]
RECORDED_COMBAT = (REPO / "review" / "qa" / "kokomi-slice1-r3-t01"
                   / "observed.json")

SERVED = "qwen3.8-27b-UD-Q4_K_XL.gguf"


# ------------------------------------------------------------ the fixtures --

def combat_state() -> dict:
    """RECORDED. The same real staged Kokomi turn the codex tests use."""
    return json.loads(RECORDED_COMBAT.read_text(encoding="utf-8"))["state"]


def rewards_state() -> dict:
    """SYNTHETIC, and a COPY of the codex file's, so the two backends are
    driven over identical screens rather than similar ones."""
    return {"state_type": "rewards",
            "rewards": {"items": [{"name": "Gold", "description": "25 gold"},
                                  {"name": "Card"}]}}


def game_over_state() -> dict:
    return {"state_type": "game_over", "run": {"floor": 9},
            "game_over": {"result": "Defeat"}}


def fight_states() -> list[dict]:
    a = combat_state()
    b = json.loads(json.dumps(a))
    b["battle"]["enemies"][0]["hp"] = 20
    return [a, b, rewards_state(), game_over_state()]


# ------------------------------------------------------------- the stub -----

class _StubEndpoint:
    """An OpenAI-compatible endpoint made of a list of replies.

    Serves the three routes this backend touches and records every request
    body, so a test can assert what actually went on the wire. Each scripted
    reply is a dict; `content` is the reply text, and the optional
    `reasoning_content`, `finish_reason` and `status` let a test drive the
    refusal paths without a model that misbehaves on cue.
    """

    def __init__(self, replies: list[dict], model: str = SERVED,
                 props: dict | None = None):
        self.replies = list(replies)
        self.model = model
        self.props = {"total_slots": 1,
                      "build_info": "b10433-stub"} if props is None else props
        self.requests: list[dict] = []
        self.paths: list[str] = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *a):                       # noqa: A003
                pass

            def version_string(self) -> str:
                # `send_response` writes this as the `Server:` header, which
                # is one of the two places llama-server volunteers a build.
                return "llama.cpp/stub"

            def _send(self, code: int, blob) -> None:
                body = json.dumps(blob).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):                                # noqa: N802
                outer.paths.append(self.path)
                if self.path.rstrip("/").endswith("/models"):
                    return self._send(200, {"object": "list", "data": [
                        {"id": outer.model, "object": "model"}]})
                if self.path.rstrip("/").endswith("props"):
                    return self._send(200, dict(outer.props))
                return self._send(404, {"error": "no such route"})

            def do_POST(self):                               # noqa: N802
                outer.paths.append(self.path)
                n = int(self.headers.get("Content-Length") or 0)
                blob = json.loads(self.rfile.read(n).decode("utf-8"))
                outer.requests.append(blob)
                if not outer.replies:
                    return self._send(500, {"error": "the stub ran out"})
                reply = dict(outer.replies.pop(0))
                status = int(reply.pop("status", 200))
                if status != 200:
                    return self._send(status, {"error": {
                        "message": reply.get("content") or "stub error"}})
                message = {"role": "assistant",
                           "content": reply.get("content", "")}
                if reply.get("reasoning_content"):
                    message["reasoning_content"] = reply["reasoning_content"]
                return self._send(200, {
                    "model": outer.model,
                    "choices": [{"index": 0, "message": message,
                                 "finish_reason": reply.get("finish_reason",
                                                            "stop")}],
                    "usage": {"prompt_tokens": 11, "completion_tokens": 7}})

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       daemon=True)

    def __enter__(self) -> "_StubEndpoint":
        self.thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    @property
    def base_url(self) -> str:
        host, port = self.server.server_address[:2]
        return f"http://{host}:{port}/v1"

    def client(self, ctx: int = 262144) -> local_model.Client:
        return local_model.Client(base_url=self.base_url, ctx=ctx,
                                  timeout_s=20, retries=1, backoff_s=0.0)


def _reply(**row) -> dict:
    """One scripted completion whose `content` is the JSON the driver wants."""
    finish = row.pop("finish_reason", "stop")
    reasoning = row.pop("reasoning_content", "")
    text = row.pop("text", None)
    content = json.dumps(row) if text is None else text
    out = {"content": content, "finish_reason": finish}
    if reasoning:
        out["reasoning_content"] = reasoning
    return out


def _session(tmp_path, stub, states=None, **budget):
    thread = local_play.LocalThread(tmp_path / "turns", client=stub.client())
    wire = blindplay.ScriptedWire(states if states is not None
                                  else fight_states())
    s = blindplay.Session(thread, wire=wire, session_id="t",
                          budget=blindplay.Budget(**budget),
                          log_root=tmp_path)
    thread.transcript = s.transcript
    return s, s.run(), wire, thread


def _rows(tmp_path) -> list[dict]:
    return [json.loads(line) for line in
            (tmp_path / "t" / "transcript.jsonl").read_text(
                encoding="utf-8").splitlines()]


# -------------------------------------------------------------- the loop ----

def test_a_whole_scripted_fight_runs_on_the_local_backend(tmp_path):
    """THE POINT OF THE FILE. Observation -> command -> POST -> next screen,
    the fight record at the end of the fight and the run record at the end of
    the run, with no game and no model server -- the same assertions the codex
    path's `test_a_scripted_fight_runs_end_to_end` makes, against the other
    backend."""
    replies = [
        _reply(command='play "Pearl Barrage" on "Nibbit"', thinking="chip"),
        _reply(command="end turn", thinking="nothing left"),
        _reply(record="I opened with the exhaust attack."),
        _reply(command='choose "Gold"', thinking="take it"),
        _reply(record="Kokomi seems to want a full rotation."),
    ]
    with _StubEndpoint(replies) as stub:
        s, summary, wire, thread = _session(tmp_path, stub)
    assert summary["termination"] == "run_over"
    assert summary["actions"] == 3
    assert [p["action"] for p in wire.posts] == ["play_card", "end_turn",
                                                 "claim_reward"]
    assert wire.posts[0]["target"] == "NIBBIT_0"
    assert summary["fight_records"] == ["I opened with the exhaust attack."]
    assert summary["run_record"].startswith("Kokomi seems")
    assert len(summary["prompt_sha256"]) == 64


def test_the_two_seats_are_sent_the_same_brief_and_the_same_pages(tmp_path):
    """THE ANTI-DRIFT PIN. `Session` owns the prompt, so the local backend
    gets the codex seat's brief on page one and a bare screen after it, and
    the `prompt_sha256` sealed into the record is the SAME string a codex run
    seals. What the local path adds is the schema block codex is handed as a
    `--output-schema` flag, and it is appended AFTER the page rather than
    woven into it."""
    replies = [_reply(command="end turn", thinking="x"),
               _reply(record="words")]
    with _StubEndpoint(replies) as stub:
        s, summary, _wire, _thread = _session(tmp_path, stub,
                                              states=[combat_state()],
                                              max_actions=1)
        sent = [m["messages"][-1]["content"] for m in stub.requests]
    body = blindplay.seat.template_body(
        blindplay.PROMPT_PATH.read_text(encoding="utf-8"))
    assert summary["prompt_sha256"] == blindplay.sha256(body)
    assert "Everything you know is on the page" in sent[0]
    assert "Everything you know is on the page" not in sent[1]
    assert "OUTPUT FORMAT" in sent[0]
    # The brief is the codex seat's, verbatim, and the schema is bolted on the
    # end rather than edited into it.
    assert body in sent[0]


def test_the_run_s_context_is_kept_here_because_the_route_is_stateless(
        tmp_path):
    """`codex exec resume` keeps the thread on the vendor's side; a chat route
    has no thread at all. So the conversation is this object's `messages`, and
    it grows by one user turn and one assistant turn per screen -- which is
    the difference between a run report and eleven disconnected turn
    reports."""
    replies = [_reply(command="end turn", thinking="a"),
               _reply(command="end turn", thinking="b"),
               _reply(record="r")]
    with _StubEndpoint(replies) as stub:
        _s, _summary, _wire, thread = _session(tmp_path, stub,
                                               states=[combat_state()],
                                               max_actions=2)
        lengths = [len(m["messages"]) for m in stub.requests]
    # 1 user; then user+assistant+user; then five.
    assert lengths == [1, 3, 5]
    assert [m["role"] for m in thread.messages[:4]] == [
        "user", "assistant", "user", "assistant"]


def test_the_reply_shape_is_sent_as_a_grammar_and_the_temperature_is_greedy(
        tmp_path):
    replies = [_reply(command="end turn", thinking="x"), _reply(record="w")]
    with _StubEndpoint(replies) as stub:
        _session(tmp_path, stub, states=[combat_state()], max_actions=1)
        first = stub.requests[0]
    assert first["temperature"] == 0.0
    assert first["stream"] is False
    fmt = first["response_format"]
    assert fmt["type"] == "json_schema"
    assert fmt["json_schema"]["schema"] == blindplay.command_schema()
    assert fmt["json_schema"]["schema"]["additionalProperties"] is False


# --------------------------------------------------------- reasoning ---------

def test_a_reasoning_field_is_stripped_before_the_parser_and_kept(tmp_path):
    """`--reasoning-format deepseek` returns `reasoning_content` beside
    `content`. It never reaches the command parser and it does reach the
    transcript row, because the scratchpad is the most interesting thing about
    this experiment and the least admissible."""
    replies = [_reply(command="end turn", thinking="x",
                      reasoning_content="I should end turn. Or play. End."),
               _reply(record="w")]
    with _StubEndpoint(replies) as stub:
        _s, summary, wire, _t = _session(tmp_path, stub,
                                         states=[combat_state()],
                                         max_actions=1)
    assert summary["actions"] == 1 and len(wire.posts) == 1
    rows = [r for r in _rows(tmp_path) if r["kind"] == "local_reply"]
    assert rows[0]["reasoning"].startswith("I should end turn")
    assert rows[0]["reasoning_chars"] > 0
    # And it is beside the turn's own files, not only in the row.
    assert (tmp_path / "turns" / "turn-001" / "reasoning.txt").is_file()


def test_an_inline_think_block_is_stripped_too(tmp_path):
    """A server launched WITHOUT `--reasoning-format deepseek` inlines the
    scratchpad into `content`. Same rule, same row -- and the JSON that
    follows it is still read as the command."""
    text = ('<think>The board has 3 energy. "end turn" is safest.</think>\n'
            '{"command": "end turn", "thinking": "safest"}')
    with _StubEndpoint([_reply(text=text), _reply(record="w")]) as stub:
        _s, summary, wire, _t = _session(tmp_path, stub,
                                         states=[combat_state()],
                                         max_actions=1)
    assert summary["actions"] == 1 and wire.posts[0]["action"] == "end_turn"
    row = [r for r in _rows(tmp_path) if r["kind"] == "local_reply"][0]
    assert "safest" in row["reasoning"]
    assert "<think>" not in row["reasoning"]


@pytest.mark.parametrize("text,answer,thought", [
    ("<think>a</think>{}", "{}", "a"),
    ("<thinking>a</thinking> {}", "{}", "a"),
    ("<think>a</think>{}<think>b</think>", "{}", "a\n\nb"),
    ("<think>unclosed and truncated", "", "unclosed and truncated"),
    ("{}", "{}", ""),
    ("", "", ""),
])
def test_the_scratchpad_shapes_a_local_model_actually_returns(text, answer,
                                                             thought):
    assert local_play.strip_reasoning(text) == (answer, thought)


def test_a_fenced_reply_is_still_read(tmp_path):
    """A local model wraps JSON in a fence often enough that a wrapper which
    could not recover would refuse a command that is right there."""
    with _StubEndpoint([_reply(text='```json\n{"command": "end turn", '
                                    '"thinking": "x"}\n```'),
                        _reply(record="w")]) as stub:
        _s, summary, wire, _t = _session(tmp_path, stub,
                                         states=[combat_state()],
                                         max_actions=1)
    assert summary["actions"] == 1 and wire.posts[0]["action"] == "end_turn"


# -------------------------------------------------------- the refusals ------

def test_a_truncated_answer_refuses_and_never_plays_a_partial_command(
        tmp_path):
    """The FIRST of the tester seat's four conditions, in the run lane: a
    reply that stopped at the ceiling has no command, and a partial answer is
    not a partial decision. The run stops and posts nothing."""
    with _StubEndpoint([_reply(command="end turn", thinking="x",
                               finish_reason="length")]) as stub:
        _s, summary, wire, _t = _session(tmp_path, stub,
                                         states=[combat_state()])
    assert summary["termination"] == "seat_refused"
    assert wire.posts == [] and summary["actions"] == 0
    detail = [r for r in _rows(tmp_path) if r["kind"] == "seat_error"][0]
    assert "answer_truncated" in detail["detail"]
    assert any(r["kind"] == "local_refusal"
               and r["reason"] == "answer_truncated" for r in _rows(tmp_path))


def test_a_prompt_that_does_not_fit_refuses_and_is_never_truncated(tmp_path):
    """The conversation grows every screen, and the window is finite. A page
    the model would only be half-shown REFUSES: the run stops with the fight
    records it already has rather than playing on from half a board."""
    replies = [_reply(command="end turn", thinking="x") for _ in range(3)]
    with _StubEndpoint(replies) as stub:
        thread = local_play.LocalThread(tmp_path / "turns",
                                        client=stub.client(ctx=64))
        wire = blindplay.ScriptedWire([combat_state()])
        s = blindplay.Session(thread, wire=wire, session_id="t",
                              budget=blindplay.Budget(), log_root=tmp_path)
        thread.transcript = s.transcript
        summary = s.run()
    assert summary["termination"] == "seat_refused"
    assert wire.posts == []
    row = [r for r in _rows(tmp_path) if r["kind"] == "seat_error"][0]
    assert "prompt_exceeds_ctx" in row["detail"]
    assert "NOTHING WAS TRUNCATED" in row["detail"]


def test_a_reply_with_no_json_refuses_rather_than_guessing_a_command(tmp_path):
    with _StubEndpoint([_reply(text="I would end the turn here.")]) as stub:
        _s, summary, wire, _t = _session(tmp_path, stub,
                                         states=[combat_state()])
    assert summary["termination"] == "seat_refused" and wire.posts == []
    assert "no_reply_json" in [r for r in _rows(tmp_path)
                               if r["kind"] == "seat_error"][0]["detail"]


def test_a_reply_missing_a_required_key_refuses(tmp_path):
    with _StubEndpoint([_reply(thinking="I have no command")]) as stub:
        _s, summary, wire, _t = _session(tmp_path, stub,
                                         states=[combat_state()])
    assert summary["termination"] == "seat_refused" and wire.posts == []
    assert "reply_incomplete" in [r for r in _rows(tmp_path)
                                  if r["kind"] == "seat_error"][0]["detail"]


def test_the_budgets_and_the_refusal_counter_are_the_driver_s_own(tmp_path):
    """Nothing about the backend moves the budgets: a tester that keeps naming
    a card that is not there is stopped by `Session`, exactly as the codex
    seat is."""
    replies = [_reply(command='play "Fireball"', thinking="?")
               for _ in range(5)]
    with _StubEndpoint(replies) as stub:
        _s, summary, wire, _t = _session(tmp_path, stub,
                                         states=[combat_state()],
                                         max_refusals=2)
    assert summary["termination"] == "refusal_limit"
    assert wire.posts == [] and summary["actions"] == 0


def test_a_server_without_grammar_support_retries_once_and_says_so(tmp_path):
    """`response_format` is the strongest constraint available and not every
    server has it. A 400 naming it costs ONE retry without it and is recorded
    as `schema_enforced: false`; the schema is in the prompt either way, so
    the retry is a weaker constraint and never a missing one."""
    replies = [{"status": 400,
                "content": "response_format json_schema is not supported"},
               _reply(command="end turn", thinking="x"),
               _reply(record="w")]
    with _StubEndpoint(replies) as stub:
        _s, summary, wire, thread = _session(tmp_path, stub,
                                             states=[combat_state()],
                                             max_actions=1)
        sent = list(stub.requests)
    assert summary["actions"] == 1 and wire.posts[0]["action"] == "end_turn"
    assert thread.schema_enforced is False
    assert "response_format" in sent[0] and "response_format" not in sent[1]
    assert thread.identity()["schema_enforced"] is False


@pytest.mark.parametrize("detail,retry", [
    ("http 400: unknown field response_format", True),
    ("http 400: json_schema unsupported", True),
    ("http 500: internal", False),
    ("no answer from http://x after 1 attempt(s): connection refused", False),
    ("http 400: your prompt was empty", False),
])
def test_only_a_rejected_request_shape_earns_the_retry(detail, retry):
    assert local_play._rejected_the_schema(detail) is retry


def test_an_unreachable_endpoint_is_an_error_not_a_silent_pass(tmp_path):
    client = local_model.Client(base_url="http://127.0.0.1:1/v1", retries=1,
                                backoff_s=0.0, timeout_s=1, model="qwen-x")
    thread = local_play.LocalThread(tmp_path / "turns", client=client)
    wire = blindplay.ScriptedWire([combat_state()])
    s = blindplay.Session(thread, wire=wire, session_id="t",
                          budget=blindplay.Budget(), log_root=tmp_path)
    thread.transcript = s.transcript
    summary = s.run()
    assert summary["termination"] == "seat_refused"
    assert "endpoint_error" in [r for r in _rows(tmp_path)
                                if r["kind"] == "seat_error"][0]["detail"]


def test_an_unset_url_is_refused_with_the_variable_named(monkeypatch,
                                                         tmp_path):
    monkeypatch.delenv(local_model.ENV_URL, raising=False)
    with pytest.raises(local_play.LocalPlayError) as exc:
        local_play.thread(tmp_path, env={})
    assert local_model.ENV_URL in str(exc.value)


# --------------------------------------------------------- the identity -----

def test_the_identity_block_names_the_backend_the_model_and_the_family(
        tmp_path):
    """R217 C is read off a record by MODEL FAMILY, and `local` names a chair
    rather than a vendor -- so the record carries both, plus the name the
    endpoint itself reported and the version the server volunteered."""
    replies = [_reply(command="end turn", thinking="x"), _reply(record="w")]
    with _StubEndpoint(replies) as stub:
        _s, summary, _wire, thread = _session(tmp_path, stub,
                                              states=[combat_state()],
                                              max_actions=1)
        identity = thread.identity()
        assert identity["endpoint"] == stub.base_url
    assert identity["model_requested"] == "local"
    assert identity["model_observed"] == SERVED
    assert identity["seat_family"] == "qwen"
    assert identity["backend"] == "local"
    assert identity["server_version"] == "b10433-stub"
    assert "props" in identity["server_version_source"]
    assert "STRUCTURAL" in identity["blindness"]
    assert "OPTION" in identity["seat_status"]


def test_the_sealed_record_prints_every_one_of_those_lines(tmp_path):
    replies = [_reply(command="end turn", thinking="x"),
               _reply(record="Kokomi wants a rotation.")]
    with _StubEndpoint(replies) as stub:
        s, summary, _wire, thread = _session(tmp_path, stub,
                                             states=[combat_state()],
                                             max_actions=1)
        identity = {**thread.identity(),
                    "build_version": "0.2.2007+proto.dirty",
                    "build_version_source": "the deployed manifest",
                    "game_version": "v0.111.0",
                    "game_version_source": "release_info.json",
                    "run_seed": "HUMWKRKNCE",
                    "prompt_sha256": summary["prompt_sha256"],
                    "actions": summary["actions"],
                    "termination": summary["termination"]}
    path = blindplay.seal(summary, identity, log_dir=s.dir,
                          record_root=tmp_path / "committed")
    text = path.read_text(encoding="utf-8")
    for want in ("**model_requested**: local", "**seat_family**: qwen",
                 "**backend**: local", "**server_version**: b10433-stub",
                 "R217 G", "not approval", "HUMWKRKNCE",
                 "Kokomi wants a rotation."):
        assert want in text, want
    assert summary["prompt_sha256"] in text
    # `wire.json` is written for this backend exactly as it is for codex.
    blob = json.loads((tmp_path / "committed" / "t" / "wire.json").read_text(
        encoding="utf-8"))
    assert blob["session_id"] == "t" and blob["snapshots"]


def test_a_codex_record_is_unchanged_by_the_new_identity_keys(tmp_path):
    """The four keys above are ABSENT from a codex run's identity, so this
    function writes for the codex seat exactly what it always wrote."""
    summary = {"session_id": "t", "guardrail": blindplay.PLAY_GUARDRAIL,
               "fight_records": [], "run_record": "", "wire": []}
    identity = {"model_requested": "gpt-5.6-sol",
                "model_observed": "gpt-5.6-sol",
                "codex_version": "codex-cli 0.150.1", "actions": 3,
                "termination": "run_over"}
    text = blindplay.record_markdown(summary, identity)
    for absent in ("backend", "seat_family", "endpoint", "server_version",
                   "schema_enforced", "blindness", "seat_status"):
        assert f"**{absent}**" not in text, absent
    assert "**codex_version**: codex-cli 0.150.1" in text


@pytest.mark.parametrize("name,family", [
    ("qwen3.8-27b-UD-Q4_K_XL.gguf", "qwen"),
    ("/models/Qwen3.8-27B/model.gguf", "qwen"),
    ("llama-3.3-70b-instruct", "llama"),
    ("mixtral-8x7b", "mistral"),
    ("gpt-oss-120b", "gpt-oss"),
    ("some-unheard-of-thing", "unknown"),
    ("", "unknown"),
])
def test_the_vendor_family_is_derived_from_the_served_name(name, family):
    assert local_play.seat_family(name, env={}) == family


def test_the_vendor_family_can_be_overridden_but_is_never_guessed():
    assert local_play.seat_family("mystery.gguf", env={}) == "unknown"
    assert local_play.seat_family(
        "mystery.gguf", env={local_play.ENV_SEAT_FAMILY: "Qwen"}) == "qwen"


def test_a_server_that_will_not_say_its_version_gets_an_empty_string(tmp_path):
    with _StubEndpoint([], props={"total_slots": 2}) as stub:
        version, source = local_play.server_version(stub.client())
    # `props` carried no build string, so the `Server:` header is the answer,
    # and a server offering neither would leave both empty rather than
    # inventing one.
    assert version == "llama.cpp/stub" and "Server" in source


def test_the_author_s_own_family_could_never_take_this_chair(tmp_path):
    """R217 C, asked of the LOCAL seat where the served model's name is
    finally known. `local:` is the spelling `authorship` resolves first, so a
    locally served `gpt-oss` is the local chair and not the Codex seat -- and
    a locally served Claude is refused like any other."""
    with _StubEndpoint([], model="claude-3-haiku.gguf") as stub:
        with pytest.raises(blindplay.BlindPlayError) as exc:
            local_play.LocalThread(tmp_path / "turns", client=stub.client())
    assert "family" in str(exc.value)


# ----------------------------------------------------- structural pins ------

def _imported(path: Path) -> list[str]:
    names: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        if isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
    return names


def test_the_local_backend_cannot_reach_a_sheet_or_a_policy():
    """The same no-leak pin `blindplay` carries. A backend that could reach a
    sheet could put a design tag on the page it hands the tester, which is the
    one thing this whole lane exists to prevent."""
    named = _imported(Path(local_play.__file__))
    banned = {"harness", "policy_v0", "policy_v1", "soak", "scenario",
              "adapter", "naming", "staged_turn", "replay", "embark"}
    assert not [m for m in named
                if m.split(".")[0] in ("tier0", "tier05")], named
    assert not [m for m in named if m.rsplit(".", 1)[-1] in banned], named


def test_blindplay_reaches_the_local_backend_lazily():
    """`local_play` imports `blindplay` at module scope, so `blindplay` must
    NOT import it back at module scope -- and the driver's import list is what
    the no-leak pin reads, so a new module-level import there is a change to
    a tested surface."""
    # The FAMILY `EB-180` split the blind module into: a module-scope import
    # in any seam carries the same weight the facade's would.
    from tier0.tests.conftest import seam_files
    for path in seam_files("blindplay"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        top = [n for n in tree.body
               if isinstance(n, (ast.Import, ast.ImportFrom))]
        assert not [n for n in top if "local_play" in ast.dump(n)], \
            f"{path} imports local_play at module scope"
    source = Path(blindplay.__file__).read_text(encoding="utf-8")
    assert "local_play" in source


def test_the_backend_flag_defaults_to_codex_and_offers_exactly_two():
    """The Codex path is the default and stays the default: a run that types
    no flag is the run this repo has always run, and a backend nobody built
    is a parse error rather than a fallback."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), pytest.raises(SystemExit):
        blindplay.main(["session", "--help"])
    text = buf.getvalue()
    assert "--backend" in text and "codex" in text and "local" in text
    with contextlib.redirect_stderr(io.StringIO()), pytest.raises(SystemExit):
        blindplay.main(["session", "--backend", "ollama"])


def test_the_codex_path_still_gets_its_default_model(monkeypatch, tmp_path):
    """`--model` lost its argparse default so the local backend can mean
    "whatever /v1/models reports" by leaving it blank. The codex path must
    still resolve `seat.DEFAULT_MODEL` from an empty string, or an unflagged
    run would ask codex for a model called ''."""
    seen: dict = {}

    class _Fake:
        def __init__(self, log_dir, model=""):
            seen["model"] = model

    monkeypatch.setattr(blindplay, "CodexThread", _Fake)
    blindplay.build_thread(tmp_path, "codex", "")
    assert seen["model"] == blindplay.seat.DEFAULT_MODEL
    blindplay.build_thread(tmp_path, "codex", "gpt-5.6-sol")
    assert seen["model"] == "gpt-5.6-sol"


def test_a_reply_whose_json_is_the_tail_of_the_reasoning_is_read(tmp_path):
    """Seen live 2026-09-02 (`kokomi-r3-local-a`, turn 7): the served model
    wrote its whole JSON reply as the last line of its thinking, closed the
    block and stopped with an EMPTY `content`. The command is read from the
    scratchpad's tail, once, and the record says so in its own row."""
    scratch = ("Enemy is weak and only hits for 8. Need exactly one command.\n"
               '{"command":"end turn","thinking":"spend on damage, not block"}')
    replies = [_reply(text="", reasoning_content=scratch), _reply(record="w")]
    with _StubEndpoint(replies) as stub:
        _s, summary, wire, _t = _session(tmp_path, stub,
                                         states=[combat_state()],
                                         max_actions=1)
    assert summary["actions"] == 1 and len(wire.posts) == 1
    kinds = [r["kind"] for r in _rows(tmp_path)]
    assert "local_answer_from_reasoning" in kinds


def test_a_schema_quoted_mid_thought_is_not_mistaken_for_the_answer(tmp_path):
    scratch = ('The schema is {"command": "", "thinking": ""} and I have not '
               "decided yet.")
    with _StubEndpoint([_reply(text="", reasoning_content=scratch)]) as stub:
        _s, summary, wire, _t = _session(tmp_path, stub,
                                         states=[combat_state()])
    assert summary["termination"] == "seat_refused" and wire.posts == []
