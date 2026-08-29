"""The LOCAL grader seat, proved against a mock server. No network, no model.

Everything here runs against a stdlib `http.server` on a loopback port that
speaks the two routes the client uses and returns canned JSON. That is the
only honest way to test this: the real endpoint is a 27B model somebody starts
by hand, so a test that needed it would be a test that never runs.

WHAT EACH GROUP PINS
--------------------
  * the CLIENT -- that it reads `content` and records `reasoning_content`
    without parsing it, that it carries the server's own model name back
    beside the requested one, and that the context guard REFUSES rather than
    truncating;
  * the FAMILY -- that a locally served model resolves to `local`, that
    `local` is not authorable on a prototype row, and that the door still
    refuses the author family;
  * the SEAT -- that the grader id and both artifact names follow the served
    model's slug, and that a form lands where `land_dir` says and NOWHERE
    ELSE, which is what keeps a closed turn closed (R101b);
  * the HARNESS -- that the report is generated, and that the round-1 misread
    class is detected off the packet's PRINTED costs.
"""

from __future__ import annotations

import json
import shutil
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from understudy import authorship, local_model, local_seat

import tools.local_model_sanity as sanity

REPO = Path(__file__).resolve().parents[2]
QA_DIR = REPO / "review" / "qa"

# A real closed turn with both recorded readings. Copied into a tmp dir per
# test; never written to in place.
FIXTURE_TURN = "kokomi-slice2-t01"
SERVED_MODEL = "Qwen3.8-27B-UD-Q4_K_XL.gguf"


# --------------------------------------------------------- the mock server -

class _Handler(BaseHTTPRequestHandler):
    """`/v1/models` and `/v1/chat/completions`, and nothing else."""

    def log_message(self, *_args):                            # noqa: D102
        return

    def _send(self, code: int, blob: dict) -> None:
        body = json.dumps(blob).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):                                         # noqa: N802
        if self.path.rstrip("/").endswith("/models"):
            self.server.seen.append(("GET", self.path, None))
            return self._send(200, {"object": "list", "data": [
                {"id": SERVED_MODEL, "object": "model"}]})
        return self._send(404, {"error": "no such route"})

    def do_POST(self):                                        # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        payload = json.loads(self.rfile.read(length) or b"{}")
        self.server.seen.append(("POST", self.path, payload))
        if self.server.http_error:
            return self._send(self.server.http_error, {"error": "nope"})
        return self._send(200, {
            "id": "chatcmpl-mock",
            "model": SERVED_MODEL,
            "choices": [{
                "index": 0,
                "finish_reason": self.server.finish_reason,
                "message": {
                    "role": "assistant",
                    "content": self.server.content,
                    # llama.cpp with --reasoning-format deepseek.
                    "reasoning_content": "I should think about this first.",
                },
            }],
            "usage": {"prompt_tokens": 1800, "completion_tokens": 250},
        })


class _Server(ThreadingHTTPServer):
    allow_reuse_address = True
    content = "hello"
    finish_reason = "stop"
    http_error = 0

    def __init__(self):
        super().__init__(("127.0.0.1", 0), _Handler)
        self.seen: list[tuple] = []


@pytest.fixture()
def server():
    srv = _Server()
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    try:
        yield srv
    finally:
        srv.shutdown()
        srv.server_close()
        thread.join(timeout=5)


def _client(server, **kw) -> local_model.Client:
    host, port = server.server_address[:2]
    kw.setdefault("retries", 1)
    return local_model.Client(base_url=f"http://{host}:{port}/v1",
                              timeout_s=20, **kw)


# ------------------------------------------------------------- the client --

def test_models_and_resolve_read_the_served_name(server):
    client = _client(server)
    assert client.models() == [SERVED_MODEL]
    assert client.resolve_model() == SERVED_MODEL


def test_chat_returns_content_and_records_reasoning_separately(server):
    server.content = "the answer"
    reply = _client(server).chat([{"role": "user", "content": "q"}],
                                 max_tokens=64)
    assert reply.text == "the answer"
    # RECORDED, and not part of the answer: a scratchpad that happened to
    # contain JSON must never be read as the form.
    assert reply.reasoning == "I should think about this first."
    assert "the answer" not in reply.reasoning
    assert reply.model_observed == SERVED_MODEL
    assert reply.model_requested == SERVED_MODEL
    assert reply.prompt_tokens == 1800 and reply.completion_tokens == 250
    assert reply.temperature == 0.0
    assert reply.as_dict()["reasoning"]


def test_the_request_is_greedy_and_unstreamed(server):
    _client(server).chat([{"role": "user", "content": "q"}], max_tokens=32)
    _, _, payload = server.seen[-1]
    assert payload["temperature"] == 0.0
    assert payload["stream"] is False
    assert payload["max_tokens"] == 32


def test_the_ctx_guard_refuses_and_never_truncates(server):
    client = _client(server, ctx=100)
    with pytest.raises(local_model.ContextError) as exc:
        client.chat([{"role": "user", "content": "x" * 10_000}],
                    max_tokens=64)
    assert "NOTHING WAS TRUNCATED" in str(exc.value)
    # ...and the proof it is a REFUSAL: no request was made.
    assert not [row for row in server.seen if row[0] == "POST"]


def test_an_http_status_is_not_retried(server):
    server.http_error = 400
    client = _client(server, retries=3)
    with pytest.raises(local_model.LocalModelError) as exc:
        client.chat([{"role": "user", "content": "q"}], max_tokens=8)
    assert "HTTP 400" in str(exc.value)
    assert len([r for r in server.seen if r[0] == "POST"]) == 1


def test_a_dead_endpoint_says_so_after_its_retries():
    client = local_model.Client(base_url="http://127.0.0.1:9/v1",
                                model="m", timeout_s=2, retries=2,
                                backoff_s=0.01)
    with pytest.raises(local_model.LocalModelError) as exc:
        client.chat([{"role": "user", "content": "q"}], max_tokens=8)
    assert "2 attempt(s)" in str(exc.value)


def test_from_env_refuses_an_unset_url():
    with pytest.raises(local_model.LocalModelError) as exc:
        local_model.Client.from_env({})
    assert local_model.ENV_URL in str(exc.value)


def test_from_env_reads_all_four_vars():
    client = local_model.Client.from_env({
        local_model.ENV_URL: "http://x:1/v1/",
        local_model.ENV_NAME: "m",
        local_model.ENV_CTX: "4096",
        local_model.ENV_TIMEOUT: "30"})
    assert client.base_url == "http://x:1/v1"      # trailing slash trimmed
    assert (client.model, client.ctx, client.timeout_s) == ("m", 4096, 30)


@pytest.mark.parametrize("name,want", [
    ("Qwen3.8-27B-UD-Q4_K_XL.gguf", "qwen3-8-27b-ud-q4-k-xl"),
    ("qwen3:27b", "qwen3-27b"),
    ("/models/foo/Bar.Baz.gguf", "bar-baz"),
    ("", "unknown"),
])
def test_the_slug_is_stable_and_filename_safe(name, want):
    assert local_model.slug(name) == want


def test_the_grader_id_is_local_plus_the_slug():
    assert local_model.grader_id(SERVED_MODEL) == \
        "local-qwen3-8-27b-ud-q4-k-xl"


# ------------------------------------------------------------ the family --

@pytest.mark.parametrize("model", [
    "local:Qwen3.8-27B-UD-Q4_K_XL.gguf", "qwen3:27b", "llama3.1:70b",
    "mistral-small", "ollama/gemma2", "local:gpt-oss-20b",
])
def test_a_locally_served_model_is_the_local_family(model):
    assert authorship.model_family(model) == authorship.LOCAL_FAMILY


@pytest.mark.parametrize("model,family", [
    ("claude-opus-5", "claude"), ("gpt-5.6-sol", "gpt"),
])
def test_the_hosted_families_are_unmoved(model, family):
    assert authorship.model_family(model) == family


def test_local_is_recognised_but_may_not_author_a_row():
    """The asymmetry, pinned. `local` is a family the refusal can NAME; it is
    not a family that may write a prototype row -- OPERATIONS' doctrine block
    fixes the authoring roles at two and this does not widen them."""
    assert authorship.LOCAL_FAMILY in authorship.FAMILIES
    assert authorship.LOCAL_FAMILY not in authorship.AUTHORABLE_FAMILIES
    findings = authorship.field_findings(
        {"id": "proto_x", "authored_by": ["local"]})
    assert findings and "unknown famil" in findings[0]


def test_the_local_seat_is_independent_of_the_claude_author():
    """It passes the author door -- which is the whole reason it can read a
    packet at all -- while a Claude model still does not."""
    authorship.check_independent("local:qwen3-27b")
    with pytest.raises(authorship.IndependenceError):
        authorship.check_independent("claude-opus-5")


def test_a_local_seat_is_refused_from_a_row_that_named_it(tmp_path):
    """Unreachable through the surface today, and pinned anyway: if a row ever
    recorded `local`, the same door that refuses gpt must refuse it."""
    import yaml
    sheet = tmp_path / "surface.yaml"
    sheet.write_text(yaml.safe_dump(
        [{"id": "proto_x", "authored_by": ["claude", "local"]}]),
        encoding="utf-8")
    with pytest.raises(authorship.IndependenceError):
        authorship.check_independent("local:qwen3-27b", rows=["proto_x"],
                                     sheet=sheet)


# -------------------------------------------------------------- the seat --

def _qa_fixture(tmp_path: Path) -> Path:
    qa = tmp_path / "qa"
    (qa / FIXTURE_TURN).mkdir(parents=True)
    for name in ("packet.md", "packet.json", "closeness.json",
                 "verdict-opus-5-fresh.json",
                 "verdict-codex-gpt-5.6-sol-fresh.json"):
        src = QA_DIR / FIXTURE_TURN / name
        if src.is_file():
            shutil.copyfile(src, qa / FIXTURE_TURN / name)
    return qa


def _good_form(qa: Path) -> str:
    envelope = json.loads(
        (qa / FIXTURE_TURN / "packet.json").read_text(encoding="utf-8"))
    return json.dumps({
        "turn_id": FIXTURE_TURN,
        "packet_sha256": envelope["packet_sha256"],
        "grader": {"id": "ignored", "kind": "ignored", "model": "ignored",
                   "designed_these_cards": False},
        "chosen_line": [
            {"card": "All Streams Flow to the Sea", "target": "Sludge "
             "Spinner", "exhaust": None, "choose": None}],
        "q1_what_did_you_play": "All Streams Flow to the Sea into the Spinner",
        "q2_other_line_considered": "Gyorin Formation for the block instead",
        "q3_what_it_gave_up": "ten Block and the next turn's six",
        "q4_different_intent": "yes, a block intent takes Gyorin Formation",
        "q4_changed": True,
    })


def test_the_seat_writes_the_named_artifacts_and_a_verdict(server, tmp_path):
    qa = _qa_fixture(tmp_path)
    server.content = _good_form(qa)
    land = tmp_path / "sanity" / FIXTURE_TURN

    blob = local_seat.grade_turn(FIXTURE_TURN, client=_client(server),
                                 qa_dir=qa, land_dir=land,
                                 log_root=tmp_path / "logs")
    assert blob["refused"] == ""
    gid = "local-qwen3-8-27b-ud-q4-k-xl"
    assert blob["grader_id"] == gid
    assert Path(blob["form"]).name == f"form-{gid}.json"
    assert (land / f"form-{gid}.json").is_file()

    form = json.loads(Path(blob["form"]).read_text(encoding="utf-8"))
    # `fill_identity`'s three fields, and the `local:` prefix that makes the
    # family resolvable from the artifact alone.
    assert form["grader"]["id"] == gid
    assert form["grader"]["kind"] == "llm"
    assert form["grader"]["model"] == f"local:{SERVED_MODEL}"
    assert authorship.model_family(form["grader"]["model"]) == "local"
    # ...and nothing else was rewritten.
    assert form["grader"]["designed_these_cards"] is False
    assert form["q1_what_did_you_play"].startswith("All Streams")


def test_the_seat_never_writes_into_the_closed_turn(server, tmp_path):
    """R101b, made mechanical: a re-read of closed work leaves it byte-clean.
    """
    qa = _qa_fixture(tmp_path)
    server.content = _good_form(qa)
    before = {p.name: p.read_bytes()
              for p in (qa / FIXTURE_TURN).iterdir()}
    local_seat.grade_turn(FIXTURE_TURN, client=_client(server), qa_dir=qa,
                          land_dir=tmp_path / "sanity" / FIXTURE_TURN,
                          log_root=tmp_path / "logs")
    after = {p.name: p.read_bytes()
             for p in (qa / FIXTURE_TURN).iterdir()}
    assert after == before


def test_a_fenced_reply_still_parses(server, tmp_path):
    qa = _qa_fixture(tmp_path)
    server.content = ("Here is my answer.\n\n```json\n" + _good_form(qa)
                      + "\n```\n")
    blob = local_seat.grade_turn(FIXTURE_TURN, client=_client(server),
                                 qa_dir=qa,
                                 land_dir=tmp_path / "s" / FIXTURE_TURN,
                                 log_root=tmp_path / "logs")
    assert blob["refused"] == ""


@pytest.mark.parametrize("content,reason", [
    ("I would rather not answer.", "no_form"),
    ('{"turn_id": "some-other-turn", "packet_sha256": "x"}',
     "turn_mismatch"),
])
def test_an_unusable_reply_refuses_by_name(server, tmp_path, content, reason):
    qa = _qa_fixture(tmp_path)
    server.content = content
    blob = local_seat.grade_turn(FIXTURE_TURN, client=_client(server),
                                 qa_dir=qa,
                                 land_dir=tmp_path / "s" / FIXTURE_TURN,
                                 log_root=tmp_path / "logs")
    assert blob["refused"] == reason
    assert not list((tmp_path / "s" / FIXTURE_TURN).glob("form-*.json")) \
        if (tmp_path / "s" / FIXTURE_TURN).is_dir() else True


def test_a_truncated_answer_is_not_a_partial_grade(server, tmp_path):
    qa = _qa_fixture(tmp_path)
    server.content = _good_form(qa)
    server.finish_reason = "length"
    blob = local_seat.grade_turn(FIXTURE_TURN, client=_client(server),
                                 qa_dir=qa,
                                 land_dir=tmp_path / "s" / FIXTURE_TURN,
                                 log_root=tmp_path / "logs")
    assert blob["refused"] == "answer_truncated"


def test_the_seat_asks_the_same_question_as_the_codex_seat(tmp_path):
    """The prompts must not drift: one template, one substitution, and the
    schema appended where codex gets it as a flag."""
    from understudy import seat as codex_seat
    packet = (QA_DIR / FIXTURE_TURN / "packet.md").read_text(encoding="utf-8")
    local = local_seat.build_grade_prompt(packet, "a" * 64)
    assert local.startswith(codex_seat.build_prompt(packet, "a" * 64))
    assert "OUTPUT FORMAT" in local
    assert packet in local


def test_the_seat_records_both_model_names(server, tmp_path):
    qa = _qa_fixture(tmp_path)
    server.content = _good_form(qa)
    blob = local_seat.grade_turn(FIXTURE_TURN, client=_client(server),
                                 qa_dir=qa,
                                 land_dir=tmp_path / "s" / FIXTURE_TURN,
                                 log_root=tmp_path / "logs")
    assert blob["model_requested"] == SERVED_MODEL
    assert blob["model_observed"] == SERVED_MODEL
    assert blob["temperature"] == 0.0
    assert "not human validation" in blob["guardrail"].lower() or \
        "not human validation" in blob["guardrail"]


# ------------------------------------------------------------ the harness --

def test_printed_costs_are_read_off_the_packet():
    packet = (QA_DIR / FIXTURE_TURN / "packet.md").read_text(encoding="utf-8")
    costs = sanity.printed_costs(packet)
    assert costs["All Streams Flow to the Sea"] == 1
    assert costs["Gyorin Formation"] == 2


def test_the_round_one_misread_class_is_detected():
    packet = (QA_DIR / FIXTURE_TURN / "packet.md").read_text(encoding="utf-8")
    hits = sanity.free_card_misreads(
        packet, "Coral Guard is free this turn, so I led with it.")
    assert hits and "Coral Guard" in hits[0] and "Cost: 1" in hits[0]
    # ...and it does not fire on prose that makes no such claim.
    assert not sanity.free_card_misreads(
        packet, "I played Coral Guard for the Block.")


def test_discovery_needs_both_recorded_readings(tmp_path):
    qa = _qa_fixture(tmp_path)
    turns, _ = sanity.discover(qa, patterns=("kokomi-slice2-t*",))
    assert turns == [FIXTURE_TURN]
    (qa / FIXTURE_TURN / "verdict-codex-gpt-5.6-sol-fresh.json").unlink()
    turns, notes = sanity.discover(qa, patterns=("kokomi-slice2-t*",))
    assert turns == []
    assert any("only one recorded reading" in n for n in notes)


def test_the_dry_run_needs_no_endpoint_and_estimates_each_call(tmp_path):
    qa = _qa_fixture(tmp_path)
    text = sanity.dry_run([FIXTURE_TURN], ["a note"], client=None, qa_dir=qa)
    assert "nothing is sent" in text
    assert FIXTURE_TURN in text and "prompt tok" in text and "fits" in text
    assert "a note" in text


def test_the_dry_run_says_when_a_packet_will_not_fit(tmp_path):
    qa = _qa_fixture(tmp_path)
    tiny = local_model.Client(base_url="http://x/v1", model="m", ctx=512)
    assert "DOES NOT FIT" in sanity.dry_run([FIXTURE_TURN], [], client=tiny,
                                            qa_dir=qa)


def test_an_unset_url_exits_two_and_writes_nothing(tmp_path, monkeypatch,
                                                   capsys):
    monkeypatch.delenv(local_model.ENV_URL, raising=False)
    out = tmp_path / "out"
    code = sanity.main(["--out", str(out), "--qa-dir",
                        str(_qa_fixture(tmp_path))])
    assert code == 2
    assert not out.exists()
    assert local_model.ENV_URL in capsys.readouterr().err


def test_the_report_puts_the_three_readings_side_by_side(server, tmp_path,
                                                         monkeypatch):
    qa = _qa_fixture(tmp_path)
    server.content = _good_form(qa)
    host, port = server.server_address[:2]
    monkeypatch.setenv(local_model.ENV_URL, f"http://{host}:{port}/v1")
    monkeypatch.setenv(local_model.ENV_TIMEOUT, "20")
    out = tmp_path / "report-out"

    code = sanity.main([FIXTURE_TURN, "--qa-dir", str(qa), "--out", str(out),
                        "--log-root", str(tmp_path / "logs")])
    assert code == 0
    text = (out / "report.md").read_text(encoding="utf-8")
    assert "Not human validation" in text
    assert "Not balance evidence" in text
    assert FIXTURE_TURN in text
    assert "verdict agrees" in text and "line agrees" in text
    assert "local-qwen3-8-27b-ud-q4-k-xl" in text
    assert "opus-5-fresh" in text and "codex-gpt-5.6-sol-fresh" in text
    # the local seat's own artifacts landed OUTSIDE the closed turn
    assert (out / FIXTURE_TURN /
            "form-local-qwen3-8-27b-ud-q4-k-xl.json").is_file()
    assert (out / FIXTURE_TURN /
            "verdict-local-qwen3-8-27b-ud-q4-k-xl.json").is_file()
    assert not list((qa / FIXTURE_TURN).glob("*local*"))
    assert json.loads((out / "rows.json").read_text(encoding="utf-8"))
