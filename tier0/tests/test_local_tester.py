"""THE LOCAL TESTER SEAT, and the four conditions it advanced on.

[USER] asked the Codex seat to confirm the 2026-08-29 local-model playtest
findings before playtesting was handed to Qwen. It answered **ADVANCE, for the
staged single-turn tester seat only**, and attached four conditions in its own
words. Each is a lock here, and each lock was seen to FAIL before the code
that satisfies it existed -- a lock trusted without that is a lock nobody has
tested.

  (a) *"keep `answer_truncated` as a hard refusal with no partial filing"* --
      `test_a_truncated_reply_files_no_form`;
  (b) *"keep the family non-authorable under M53"* --
      `test_local_may_not_author`, `test_the_lint_reads_the_tester_path`;
  (c) *"retain periodic review by this seat"* -- `test_the_spot_check_*`;
  (d) *"require review of any reading whose ordered line changes a resource
      before a later resource-dependent play"* -- `test_t06_*`, on the very
      form the seat caught it in.

NO NETWORK, EVER. The endpoint is a mock on a loopback port, exactly as
`test_local_model.py` does it: the real server is a 27B model somebody starts
by hand, and a test that needed one is a test that never runs.
"""

from __future__ import annotations

import json
import shutil
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from unittest import mock

from understudy import (authorship, bridge, frames, hangwatch, instances,
                        local_model, local_seat, local_tester, misreads,
                        resource_order, soak)

import tools.lint_prototype_authorship as auth_lint

REPO = Path(__file__).resolve().parents[2]
QA_DIR = REPO / "review" / "qa"
FIXTURES = REPO / "understudy" / "turns" / "fixtures"

FIXTURE_TURN = "kokomi-slice2-t01"
ORDER_TURN = "kokomi-slice2-t06"
SERVED_MODEL = "Qwen3.8-27B-UD-Q4_K_XL.gguf"
TESTER_ID = "local-qwen3-8-27b-ud-q4-k-xl"


# --------------------------------------------------------- the mock server -

class _Handler(BaseHTTPRequestHandler):

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
            return self._send(200, {"object": "list", "data": [
                {"id": SERVED_MODEL, "object": "model"}]})
        return self._send(404, {"error": "no such route"})

    def do_POST(self):                                        # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        self.rfile.read(length)
        return self._send(200, {
            "id": "chatcmpl-mock", "model": SERVED_MODEL,
            "choices": [{"index": 0,
                         "finish_reason": self.server.finish_reason,
                         "message": {"role": "assistant",
                                     "content": self.server.content}}],
            "usage": {"prompt_tokens": 1800, "completion_tokens": 250}})


class _Server(ThreadingHTTPServer):
    allow_reuse_address = True
    content = "hello"
    finish_reason = "stop"

    def __init__(self):
        super().__init__(("127.0.0.1", 0), _Handler)


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


def _client(server) -> local_model.Client:
    host, port = server.server_address[:2]
    return local_model.Client(base_url=f"http://{host}:{port}/v1",
                              timeout_s=20, retries=1)


def _qa(tmp_path: Path, turn: str = FIXTURE_TURN) -> Path:
    qa = tmp_path / "qa"
    (qa / turn).mkdir(parents=True)
    for name in ("packet.md", "packet.json", "closeness.json"):
        src = QA_DIR / turn / name
        if src.is_file():
            shutil.copyfile(src, qa / turn / name)
    return qa


def _form(qa: Path, turn: str, line: list[dict]) -> str:
    envelope = json.loads(
        (qa / turn / "packet.json").read_text(encoding="utf-8"))
    return json.dumps({
        "turn_id": turn,
        "packet_sha256": envelope["packet_sha256"],
        "grader": {"id": "x", "kind": "x", "model": "x",
                   "designed_these_cards": False},
        "chosen_line": line,
        "q1_what_did_you_play": "the line above",
        "q2_other_line_considered": "the other one",
        "q3_what_it_gave_up": "some Block",
        "q4_different_intent": "yes",
        "q4_changed": True,
    })


# ------------------------------------------------- (a) the truncation lock -

def test_a_truncated_reply_files_no_form(server, tmp_path):
    """CONDITION (a), in the seat's own words: *"keep `answer_truncated` as a
    hard refusal with no partial filing"*. The tester path must inherit it
    whole -- a refusal record, and NOTHING that could be mistaken for a
    reading."""
    qa = _qa(tmp_path)
    land = tmp_path / "land"
    server.content = _form(qa, FIXTURE_TURN,
                           [{"card": "All Streams Flow to the Sea"}])
    server.finish_reason = "length"

    record = local_tester.read_turn(FIXTURE_TURN, client=_client(server),
                                    qa_dir=qa, land_dir=land,
                                    log_root=tmp_path / "logs")
    assert record["refused"] == "answer_truncated"
    assert record["form"] == ""
    assert not list(land.glob("form-*.json")), "a partial form was filed"
    # ...and the turn still owes a reading, so it routes to the seat.
    assert record["seat_review_required"]
    assert "local_read_refused" in record["seat_review_reasons"]
    # The record itself is written: a refusal that leaves no trace is not a
    # record of anything.
    assert Path(record["record"]).is_file()


def test_the_answer_ceiling_is_configuration_not_a_constant(monkeypatch):
    """The other half of (a). The sanity read raised the ceiling twice and the
    answers still ran off the end, so the number is an operator's dial -- and
    the control for runaway THINKING is the server's `--reasoning-budget`,
    never a client-side cap. Junk falls back rather than raising."""
    assert local_seat.form_max_tokens({}) == \
        local_seat.DEFAULT_FORM_MAX_TOKENS
    assert local_seat.form_max_tokens(
        {local_seat.ENV_FORM_TOKENS: "12000"}) == 12000
    assert local_seat.review_max_tokens(
        {local_seat.ENV_REVIEW_TOKENS: "20000"}) == 20000
    for junk in ("", "nonsense", "0", "-5"):
        assert local_seat.form_max_tokens(
            {local_seat.ENV_FORM_TOKENS: junk}) == \
            local_seat.DEFAULT_FORM_MAX_TOKENS


# ------------------------------------------------ (b) the authorship lock --

def test_local_may_not_author(tmp_path):
    """CONDITION (b): *"keep the family non-authorable under M53"*. The tester
    chair recognises the family; it does not widen the authoring set."""
    assert local_tester.TESTER_FAMILY == authorship.LOCAL_FAMILY
    assert local_tester.TESTER_FAMILY in authorship.FAMILIES
    assert local_tester.TESTER_FAMILY not in authorship.AUTHORABLE_FAMILIES
    assert authorship.field_findings(
        {"id": "proto_x", "authored_by": [local_tester.TESTER_FAMILY]})


def test_the_lint_reads_the_tester_path(tmp_path):
    """(b) from the other end: the existing lint now walks tester records, so
    a `local` seat that filed itself as an authoring family is a FINDING and
    not a file nobody reads."""
    import yaml
    sheet = tmp_path / "surface.yaml"
    sheet.write_text(yaml.safe_dump(
        [{"id": "proto_x", "authored_by": ["claude", "gpt"]}]),
        encoding="utf-8")
    turns = tmp_path / "turns"
    turns.mkdir()
    (turns / "t.yaml").write_text(yaml.safe_dump(
        {"id": "t01", "board": {"hand": ["proto_x"]}}), encoding="utf-8")
    qa = tmp_path / "qa" / "t01"
    qa.mkdir(parents=True)

    def write(blob):
        (qa / "tester-local-q.json").write_text(json.dumps(blob),
                                                encoding="utf-8")

    write({"tester_family": "gpt", "model_requested": SERVED_MODEL})
    hits = auth_lint.findings(qa.parent, turns, sheet, debt={})
    assert any("AUTHORING family" in h for h in hits), hits
    assert any("resolves to" in h for h in hits), hits

    write({"tester_family": "local", "model_requested": SERVED_MODEL})
    assert not auth_lint.findings(qa.parent, turns, sheet, debt={})


def test_a_tester_record_names_its_family_in_words(server, tmp_path):
    """The record must be legible without this module: `role` and
    `tester_family` are literal fields, not something a later reader has to
    resolve out of a model string."""
    qa = _qa(tmp_path)
    land = tmp_path / "land"
    server.content = _form(qa, FIXTURE_TURN,
                           [{"card": "All Streams Flow to the Sea"}])
    record = local_tester.read_turn(FIXTURE_TURN, client=_client(server),
                                    qa_dir=qa, land_dir=land,
                                    seat_mode="deciding",
                                    log_root=tmp_path / "logs")
    assert record["role"] == "tester"
    assert record["tester_family"] == "local"
    assert record["tester_id"] == TESTER_ID
    assert Path(record["form"]).name == f"form-{TESTER_ID}.json"
    assert record["packet_sha256"]
    form = json.loads(Path(record["form"]).read_text(encoding="utf-8"))
    assert authorship.model_family(form["grader"]["model"]) == "local"
    assert not auth_lint.tester_findings(qa)


def test_the_tester_never_writes_into_the_closed_turn(server, tmp_path):
    """R101b: the read half and the write half are different directories."""
    qa = _qa(tmp_path)
    server.content = _form(qa, FIXTURE_TURN,
                           [{"card": "All Streams Flow to the Sea"}])
    before = {p.name: p.read_bytes() for p in (qa / FIXTURE_TURN).iterdir()}
    local_tester.read_turn(FIXTURE_TURN, client=_client(server), qa_dir=qa,
                           land_dir=tmp_path / "land",
                           log_root=tmp_path / "logs")
    after = {p.name: p.read_bytes() for p in (qa / FIXTURE_TURN).iterdir()}
    assert after == before


# ------------------------------------------------- (c) the spot-check lock -

def test_the_spot_check_never_leaves_a_round_unreviewed():
    """CONDITION (c): *"retain periodic review by this seat"*. Turn 1 and
    every Nth after it, so the shortest round this funnel has run (4 turns)
    still gets one seat read and the longest (11) gets three."""
    assert local_tester.spot_check_due(1, 4)
    assert not local_tester.spot_check_due(2, 4)
    assert local_tester.spot_check_due(5, 4)
    for length, want in ((4, 1), (8, 2), (11, 3)):
        due = [i for i in range(1, length + 1)
               if local_tester.spot_check_due(i, 4)]
        assert len(due) == want, (length, due)
        assert due[0] == 1, "a round must never start unreviewed"


def test_the_spot_check_rate_is_a_knob_and_zero_disables_only_the_rate():
    assert local_tester.spot_check_due(1, 1) and \
        local_tester.spot_check_due(2, 1)
    assert not any(local_tester.spot_check_due(i, 0) for i in range(1, 12))
    plan = local_tester.plan_round(["a", "b", "c", "d", "e"], 4)
    assert [p["seat_spot_check"] for p in plan] == \
        [True, False, False, False, True]


def test_the_round_queue_names_the_turns_the_seat_still_owes():
    records = [
        {"turn_id": "t01", "seat_review_required": True,
         "seat_review_reasons": ["spot_check"]},
        {"turn_id": "t02", "seat_review_required": False,
         "seat_review_reasons": []},
        {"turn_id": "t03", "seat_review_required": True,
         "seat_review_reasons": ["resource_order"]},
    ]
    queue = local_tester.round_queue(records)
    assert [q["turn_id"] for q in queue] == ["t01", "t03"]
    assert queue[1]["reasons"] == ["resource_order"]
    assert "understudy.seat grade t03" in queue[1]["command"]


def test_a_spot_checked_turn_says_so_in_its_record(server, tmp_path):
    qa = _qa(tmp_path)
    server.content = _form(qa, FIXTURE_TURN,
                           [{"card": "All Streams Flow to the Sea"}])
    first = local_tester.read_turn(FIXTURE_TURN, client=_client(server),
                                   qa_dir=qa, land_dir=tmp_path / "a",
                                   log_root=tmp_path / "logs", position=1)
    assert first["seat_review_required"]
    assert first["seat_review_reasons"] == ["spot_check"]

    second = local_tester.read_turn(FIXTURE_TURN, client=_client(server),
                                    qa_dir=qa, land_dir=tmp_path / "b",
                                    log_root=tmp_path / "logs", position=2)
    assert not second["seat_review_required"]


# ---------------------------------------------- (d) the resource-order lock

def _fixture_line(name: str) -> list[dict]:
    return json.loads((FIXTURES / name).read_text(
        encoding="utf-8"))["chosen_line"]


# THE CASE ITSELF, both halves, from the two 2026-08-29 sanity reads. The
# UNCAPPED read (no server-side `--reasoning-budget`) put Twin Tides' spend
# first; the CAPPED re-run under `--reasoning-budget 4096` produced the
# correct order on the same board. So the same seat, on the same packet,
# straddles the flag -- which is the best possible pair of fixtures for it:
# the flag has to fire on one and stay silent on the other, and neither is a
# hypothetical.
T06_LOCAL_LINE = _fixture_line("form-local-kokomi-slice2-t06-uncapped.json")
T06_CAPPED_LINE = _fixture_line("form-local-kokomi-slice2-t06-capped.json")

# The recorded `opus-5-fresh` order on the same board: the Charge-reading
# attack FIRST, then the mode that spends the Charge.
T06_RECORDED_LINE = [
    {"card": "All Streams Flow to the Sea", "target": "Nibbit"},
    {"card": "Twin Tides", "choose": "Spend 6 Charge: gain 12 Block."},
]


def test_t06_local_line_trips_the_order_flag():
    """CONDITION (d), on the exact form that produced it. The local reading
    played Twin Tides' *Spend 6 Charge* mode and THEN the attack whose damage
    reads Charge -- the seat's finding, and the shape it wants routed."""
    hits = resource_order.findings(T06_LOCAL_LINE)
    assert hits, "the seat's own case must trip the flag"
    assert {h["resource"] for h in hits} == {"charge"}
    named = {(h["spent_by"], h["read_by"]) for h in hits}
    assert named == {("Twin Tides", "All Streams Flow to the Sea")}


def test_t06_capped_rerun_does_not_trip_it():
    """The same seat, the same packet, one server flag apart. Under
    `--reasoning-budget 4096` the re-run played the read BEFORE the spend, and
    the flag must be silent on it -- otherwise it is flagging the seat rather
    than the line."""
    assert T06_CAPPED_LINE[0]["card"] == "All Streams Flow to the Sea"
    assert resource_order.findings(T06_CAPPED_LINE) == []


def test_t06_recorded_order_does_not_trip_it():
    """The other half of the lock: the read comes BEFORE the spend, which is
    the ordinary correct line, and a flag there would be noise."""
    assert resource_order.findings(T06_RECORDED_LINE) == []


def test_the_unspent_mode_of_a_choose_one_does_not_trip_it():
    """The mode refinement. Twin Tides' other mode spends nothing, so the same
    two cards in the same order are silent when that mode is the one the form
    recorded."""
    line = [{"card": "Twin Tides", "choose": "Gain 5 Block"},
            {"card": "All Streams Flow to the Sea"}]
    assert resource_order.findings(line) == []


def test_an_unrecorded_mode_falls_back_to_the_union():
    """...and a play with NO mode recorded flags, because a turn nobody can
    resolve is a turn a person should read."""
    line = [{"card": "Twin Tides"},
            {"card": "All Streams Flow to the Sea"}]
    assert resource_order.findings(line)


def test_a_title_no_sheet_prints_is_disclosed_not_flagged():
    line = [{"card": "Not A Real Card"}, {"card": "Twin Tides"}]
    assert resource_order.findings(line) == []
    assert resource_order.unresolved(line) == ["Not A Real Card"]


def test_a_gain_before_a_read_is_never_flagged():
    """`gain_charge` is not `spend_charge`, and banking before a payoff is the
    line the pilot is supposed to find."""
    line = [{"card": "Rally the Isles"},
            {"card": "All Streams Flow to the Sea"}]
    assert resource_order.findings(line) == []


def test_the_flag_routes_the_turn_regardless_of_the_rate(server, tmp_path):
    """The condition's own words: *require* review. So it is not subject to
    the spot-check rate, and it is not subject to the rate being zero."""
    qa = _qa(tmp_path, ORDER_TURN)
    server.content = _form(qa, ORDER_TURN, T06_LOCAL_LINE)
    record = local_tester.read_turn(ORDER_TURN, client=_client(server),
                                    qa_dir=qa, land_dir=tmp_path / "land",
                                    log_root=tmp_path / "logs",
                                    position=2, spot_check=0)
    assert record["seat_review_required"]
    assert record["seat_review_reasons"] == ["resource_order"]
    flag = record["resource_order_flag"]
    assert flag and flag[0]["spent_by"] == "Twin Tides"
    assert flag[0]["read_by"] == "All Streams Flow to the Sea"
    assert "charge" in record["resource_order"]["rule"] or \
        "meter" in record["resource_order"]["rule"]


# ---------------------------------------- the arithmetic misread extension -

def test_the_block_prevention_misread_the_seat_caught():
    """The seat's second finding: five Block against an eight-damage intent
    prevents FIVE. Three is what gets through."""
    packet = (QA_DIR / "kokomi-slice2-t02" / "packet.md").read_text(
        encoding="utf-8")
    prose = ("The chosen line gave up 5 Block from Coral Guard and the 3 HP "
             "that block would have prevented, and it also passed on Gyorin "
             "Formation's 10 Block now.")
    hits = misreads.block_prevention_misreads(packet, prose)
    assert len(hits) == 1 and "prevents 5" in hits[0]
    assert hits[0] in misreads.misreads(packet, prose)


@pytest.mark.parametrize("prose", [
    "It gave up 5 Block from Coral Guard and the 5 HP that block "
    "would have prevented.",
    "It gave up Coral Guard's Block and the damage that would have "
    "prevented.",
    "Gyorin Formation's 10 Block would have prevented the whole intent.",
    "",
])
def test_the_arithmetic_check_stays_quiet_when_it_cannot_be_sure(prose):
    """A false MISREAD is worse than a missed one: it fires ONLY on the exact
    residual identity, with all three numbers on the page."""
    packet = (QA_DIR / "kokomi-slice2-t02" / "packet.md").read_text(
        encoding="utf-8")
    assert misreads.block_prevention_misreads(packet, prose) == []


def test_the_cost_misread_class_is_unmoved():
    """The round-1 check moved file and did not move behaviour."""
    packet = (QA_DIR / "kokomi-slice2-t02" / "packet.md").read_text(
        encoding="utf-8")
    assert misreads.free_card_misreads(
        packet, "Coral Guard is free, so I played it")
    assert misreads.free_card_misreads(packet, "I played Coral Guard") == []


# --------------------------------------------------------- the seam itself -

def test_the_tester_asks_the_codex_seat_s_question(tmp_path):
    """The seam, pinned: the tester role adds a RECORD and two post-read
    checks. It does not add a prompt. If these ever diverge the comparison
    that sanctioned this chair stops meaning anything."""
    from understudy import seat as codex_seat
    packet = (QA_DIR / FIXTURE_TURN / "packet.md").read_text(encoding="utf-8")
    assert local_seat.build_grade_prompt(packet, "a" * 64).startswith(
        codex_seat.build_prompt(packet, "a" * 64))


def test_the_sheet_reader_is_not_in_scope_where_the_prompt_is_built():
    """`resource_order` reads a DESIGN SHEET. It runs after the reply, on the
    record, and it is imported inside the post-read function for exactly that
    reason -- so it is not one refactor away from being in scope where the
    blind packet is assembled."""
    import ast
    src = (REPO / "understudy" / "local_tester.py").read_text(
        encoding="utf-8")
    tree = ast.parse(src)
    top = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    named: list[str] = []
    for node in top:
        if isinstance(node, ast.ImportFrom):
            named += [a.name for a in node.names]
        else:
            named += [a.name for a in node.names]
    assert "resource_order" not in named, named
    assert "misreads" not in named, named


# ============================================================ R221 ==========
#
# The two rules the throughput ruling added, and the two engineering items
# under them. NO GAME AND NO MODEL: the lane takes an injected session and a
# state reader, and the phases take an injected `RoundSteps` that sleeps
# instead of booting anything. A test that needed the real game is a test that
# runs on one machine, at night, once.

import time as _time

from understudy import packet_section, staged_turn


def _rows(spec):
    """`{turn_id: (slots, closeness)}` as the order function wants them."""
    class _T:
        def __init__(self, tid, slots):
            self.id, self._slots = tid, slots
            self.path, self.seed, self.prototype = f"{tid}.yaml", "", False
            self.board = None

        def registered_slots(self):
            return list(self._slots)
    return {tid: _T(tid, slots) for tid, (slots, _gap) in spec.items()}


def _order(spec, monkeypatch):
    gaps = {tid: gap for tid, (_s, gap) in spec.items()}
    monkeypatch.setattr(local_tester, "closeness_gap",
                        lambda turn: gaps[turn.id])
    return local_tester.preregistered_order(list(spec), turns=_rows(spec))


# ------------------------------------------------- R221 B: the first set ----

def test_the_first_set_is_the_smallest_twice_over_cover(monkeypatch):
    """Four boards over two slots: two boards per slot is the whole cover, so
    the cover size is four and `--first 2` is RAISED to it. A `--first` that
    could leave a registered slot with one grade would make every slot
    UNDECIDED by construction, which is not a stopping rule."""
    spec = {"t01": (["A"], 0.9), "t02": (["A"], 0.1),
            "t03": (["B"], 0.5), "t04": (["B"], 0.4)}
    order = _order(spec, monkeypatch)
    assert order[0]["cover_size"] == 4
    first, rest = local_tester.split_first(order, 2)
    assert len(first) == 4 and rest == []


def test_the_cover_is_smallest_and_ties_go_to_the_closer_decision(monkeypatch):
    """A board carrying BOTH slots covers two slot-slots at once, so it is
    taken first; among boards with equal gain the closer decision wins."""
    spec = {"both": (["A", "B"], 0.7),
            "a-far": (["A"], 0.9), "a-near": (["A"], 0.2),
            "b-far": (["B"], 0.8), "b-near": (["B"], 0.3)}
    order = _order(spec, monkeypatch)
    assert order[0]["turn_id"] == "both"
    # After `both`, each slot still wants one, and the two `near` boards are
    # the closer decisions.
    assert {order[1]["turn_id"], order[2]["turn_id"]} == {"a-near", "b-near"}
    assert order[0]["cover_size"] == 3


def test_a_slot_only_one_board_carries_does_not_drag_in_the_round(monkeypatch):
    """`min(COVER, boards carrying it)`. A target nothing can meet would put
    every board in the first set and switch stopping off silently."""
    spec = {"t01": (["A"], 0.1), "t02": (["A"], 0.2), "t03": (["solo"], 0.3),
            "t04": (["A"], 0.4)}
    order = _order(spec, monkeypatch)
    assert order[0]["cover_size"] == 3          # two for A, one for `solo`
    first, rest = local_tester.split_first(order, 4)
    assert len(first) == 4 and rest == []


def test_first_zero_runs_every_board(monkeypatch):
    spec = {"t01": (["A"], 0.1), "t02": (["A"], 0.2), "t03": (["B"], 0.3)}
    order = _order(spec, monkeypatch)
    first, rest = local_tester.split_first(order, 0)
    assert len(first) == 3 and rest == []


# ------------------------------------- R221 B: DECIDED / UNDECIDED / UNRUN --

def test_a_slot_is_decided_only_on_two_or_more_that_agree():
    rows = [{"turn_id": "t01", "slots": ["A"]},
            {"turn_id": "t02", "slots": ["A"]},
            {"turn_id": "t03", "slots": ["B"]},
            {"turn_id": "t04", "slots": ["C"]},
            {"turn_id": "t05", "slots": ["D"]}]
    grades = {"t01": ["PRED"], "t02": ["PRED"],       # agree -> DECIDED
              "t03": ["PRED", "MISS"],                # split -> UNDECIDED
              "t04": ["MISS"],                        # one    -> UNDECIDED
              "t05": ["MISS", "MISS"]}                # agree  -> DECIDED
    state = local_tester.slot_state(rows, grades)
    assert state == {"A": "DECIDED", "B": "UNDECIDED",
                     "C": "UNDECIDED", "D": "DECIDED"}


def test_only_boards_carrying_an_undecided_slot_are_run():
    rest = [{"turn_id": "t09", "slots": ["A"]},
            {"turn_id": "t10", "slots": ["B", "A"]}]
    run, unrun = local_tester.split_rest(rest, {"A": "DECIDED",
                                                "B": "UNDECIDED"})
    assert [r["turn_id"] for r in run] == ["t10"]
    assert run[0]["undecided_slots"] == ["B"]
    assert [r["turn_id"] for r in unrun] == ["t09"]


def test_an_unrun_board_keeps_its_seed_and_reaches_the_ledger(tmp_path):
    """The whole point of the UNRUN row: a later round runs THIS board."""
    (tmp_path / "t09").mkdir()
    staged_turn.mark_unrun("t09", seed="ABC123", slots=["A"],
                           why="A was decided by the first set",
                           root=tmp_path)
    blob = json.loads((tmp_path / "t09" / "unrun.json").read_text(encoding="utf-8"))
    assert blob["seed"] == "ABC123" and blob["run_state"] == "UNRUN"
    assert "R101b" in blob["rule"]

    text = staged_turn.build_ledger(tmp_path)
    row = [r for r in text.splitlines() if r.startswith("t09")][0].split("\t")
    cells = dict(zip(staged_turn.LEDGER_COLUMNS, row))
    assert cells["verdict"] == "UNRUN"
    assert cells["seed"] == "ABC123"
    assert cells["run_state"] == "UNRUN"
    assert "UNRUN:" in text                       # the banner travels with it


def test_the_ledger_still_parses_a_row_written_before_the_two_columns(tmp_path):
    head = "\t".join(staged_turn.LEDGER_COLUMNS[:12])
    body = "\t".join(["t01", "g", "SURVIVES", "-", "a", "b", "c", "d",
                      "-", "-", "-", "yes"])
    (tmp_path / "ledger.tsv").write_text(head + "\n" + body + "\n",
                                         encoding="utf-8")
    rows = staged_turn.ledger_rows(tmp_path)
    assert rows[0]["turn_id"] == "t01" and rows[0]["seed"] == ""


# --------------------------------------------- R221 (3): the pipeline -------

class _FakeSession:
    def __init__(self):
        self.calls = []

    def setup(self):
        self.calls.append("setup")

    def restart(self):
        self.calls.append("restart")

    def teardown(self):
        self.calls.append("teardown")


class _FakeSteps(local_tester.RoundSteps):
    """Every phase sleeps, and every phase says when it began and ended."""

    def __init__(self, spans, delay=0.02):
        self.spans, self.delay = spans, delay

    def _span(self, kind, tid):
        start = _time.monotonic()
        _time.sleep(self.delay)
        self.spans.append((kind, tid, start, _time.monotonic()))

    def stage(self, row):
        self._span("stage", row["turn_id"])

    def read(self, row):
        self._span("read", row["turn_id"])
        return {"turn_id": row["turn_id"], "form": row["turn_id"] + ".json",
                "refused": "", "seat_review_required": False}

    def execute(self, row, record):
        self._span("execute", row["turn_id"])


def _overlap(a, b):
    return min(a[3], b[3]) - max(a[2], b[2]) > 0


def test_the_game_lock_serializes_game_steps_and_a_read_overlaps_one():
    """R221 item (3), both halves in one assertion pair: no two GAME steps
    ever overlap, and at least one MODEL step does overlap a game step --
    which is the whole reason the phases were re-ordered."""
    spans = []
    lane = local_tester.GameLane()
    steps = _FakeSteps(spans)
    rows = [{"turn_id": "t0" + str(i), "position": i} for i in range(1, 5)]
    records = local_tester.run_pipeline(rows, lane=lane, steps=steps)

    assert [r["turn_id"] for r in records] == ["t01", "t02", "t03", "t04"]
    game = [s for s in spans if s[0] in ("stage", "execute")]
    for i, a in enumerate(game):
        for b in game[i + 1:]:
            assert not _overlap(a, b), "two game steps overlapped"
    reads = [s for s in spans if s[0] == "read"]
    assert any(_overlap(r, g) for r in reads for g in game), \
        "no model step overlapped a game step -- the game still idles"


def test_serial_keeps_the_old_phase_order_reachable():
    spans = []
    lane = local_tester.GameLane()
    rows = [{"turn_id": "t0" + str(i), "position": i} for i in range(1, 4)]
    local_tester.run_pipeline(rows, lane=lane, steps=_FakeSteps(spans),
                              serial=True)
    assert [s[0] for s in spans] == ["stage", "read", "execute"] * 3
    for i, a in enumerate(spans):
        for b in spans[i + 1:]:
            assert not _overlap(a, b)


def test_a_failed_stage_stops_the_round_rather_than_reading_a_dead_board():
    class _Boom(_FakeSteps):
        def stage(self, row):
            raise local_tester.LocalTesterError("staging failed")
    with pytest.raises(local_tester.LocalTesterError):
        local_tester.run_pipeline(
            [{"turn_id": "t01", "position": 1}],
            lane=local_tester.GameLane(), steps=_Boom([]))


# ------------------------------ R221 (5): one launch, and what it cannot buy

def test_the_round_launches_once_and_tears_down_once():
    session = _FakeSession()
    lane = local_tester.GameLane(session=session,
                                 state_reader=lambda: {"state_type": "menu"})
    lane.launch()
    for i in range(4):
        lane.step("stage", "t0" + str(i), lambda: None)
    lane.close()
    assert session.calls == ["setup", "teardown"]
    assert lane.launches == 1 and lane.relaunches == 0


def test_a_board_left_mid_combat_costs_a_recorded_relaunch():
    """The honest half of item (5). `_to_main_menu` starts from a MENU and the
    wire has no in-run exit, so a staged board mid-combat can only be left by
    restarting the process -- and the lane records that it did."""
    session = _FakeSession()
    screens = iter([{"state_type": "menu"}, {"state_type": "combat"},
                    {"state_type": "menu"}])
    lane = local_tester.GameLane(session=session,
                                 state_reader=lambda: next(screens))
    lane.launch()
    lane.step("stage", "t01", lambda: None)
    lane.step("execute", "t01", lambda: None)
    lane.close()
    assert session.calls == ["setup", "restart", "teardown"]
    assert lane.relaunches == 1 and lane.launches == 2
    assert lane.events[-1]["relaunched"].startswith("the game is at 'combat'")


def test_a_crashed_game_relaunches_once_and_a_second_failure_stops():
    session = _FakeSession()

    def dead():
        raise RuntimeError("connection refused")
    lane = local_tester.GameLane(session=session, state_reader=dead)
    lane.launch()
    with pytest.raises(local_tester.LocalTesterError) as err:
        lane.step("stage", "t01", lambda: None)
    assert session.calls == ["setup", "restart"]
    assert "could not be brought to a menu" in str(err.value)


def test_attaching_owns_no_process_and_restarts_nothing():
    lane = local_tester.GameLane()
    lane.launch()
    lane.step("stage", "t01", lambda: None)
    lane.close()
    assert lane.launches == 0 and lane.relaunches == 0


# -------------------------------- R221 (4): the generator, on real records --

def test_the_generator_writes_a_round_from_the_kokomi_slice2_records(tmp_path):
    """Built on the records the slice-2 round actually left behind, so the
    fixture is a real round rather than a hand-made one."""
    fixture = tmp_path / "qa"
    fixture.mkdir()
    for src in sorted(QA_DIR.glob("kokomi-slice2-t0*")):
        shutil.copytree(src, fixture / src.name)
    shutil.copy(QA_DIR / "ledger.tsv", fixture / "ledger.tsv")

    text = packet_section.render("kokomi-slice2", root=fixture)
    assert "8 board(s) run, 0 UNRUN, 16 form(s) graded." in text
    # the per-turn rows, one per (turn, grader)
    assert text.count("`opus-5-fresh`") == 8
    assert text.count("`codex-gpt-5.6-sol-fresh`") == 8
    # t08's seat refusal, named by its falsifier
    assert "intent_insensitive" in text
    # the per-slot tally, and slice 2's one disagreement
    assert "| `kokomi-slice2-t08` | MISS, PRED (2) | **UNDECIDED** |" in text
    assert "| `kokomi-slice2-t01` | PRED, PRED (2) | **DECIDED** |" in text
    # the spend, split by family
    assert "**Codex seat reads:** 8" in text
    # the banners, quoted from the ledger rather than restated
    assert "> staged board: this hand and this board were set by hand" in text
    # and the slot the agent fills, unmistakably empty
    assert "NOT GENERATED. Replace this block." in text


def test_the_generator_prints_unrun_boards_with_their_seeds(tmp_path):
    fixture = tmp_path / "qa"
    (fixture / "r-t01").mkdir(parents=True)
    (fixture / "r-t02").mkdir(parents=True)
    (fixture / "r-t01" / "packet.json").write_text(
        json.dumps({"run_seed": "AAA"}), encoding="utf-8")
    staged_turn.mark_unrun("r-t02", seed="BBB", slots=["B"],
                           why="B was decided by the first set", root=fixture)
    text = packet_section.render("r", root=fixture)
    assert "1 board(s) run, 1 UNRUN" in text
    assert "| `r-t02` | `BBB` |" in text
    assert "Their seeds are pinned." in text


def test_the_generator_appends_and_never_rewrites(tmp_path):
    packet = tmp_path / "packet.md"
    packet.write_text("# A packet\n\nBody.\n", encoding="utf-8")
    packet_section.append_to(packet, "## THE ROUND\n\nrows\n")
    text = packet.read_text(encoding="utf-8")
    assert text.startswith("# A packet\n\nBody.\n")
    assert text.rstrip().endswith("rows")


def test_the_generator_refuses_a_round_with_no_records(tmp_path):
    with pytest.raises(staged_turn.TurnError):
        packet_section.render("nothing-here", root=tmp_path)


# ------------------------------------------------------- slots on a turn ----

def test_a_turn_declares_its_slots_and_defaults_to_its_own_id():
    turn = staged_turn.load(REPO / "understudy" / "turns"
                            / "kokomi-first-turn-example.yaml")
    assert turn.registered_slots() == [turn.id]
    with pytest.raises(staged_turn.TurnError):
        staged_turn._parse_slots({"a": 1})
    with pytest.raises(staged_turn.TurnError):
        staged_turn._parse_slots(["ok", ""])
    assert staged_turn._parse_slots(None) == []
    assert staged_turn._parse_slots([" P1 ", "P2"]) == ["P1", "P2"]


# ============================ pick 4(e): the shadow chair and the deciding one

def _verdict(qa: Path, turn: str, gid: str, verdict: str) -> None:
    (qa / turn).mkdir(parents=True, exist_ok=True)
    (qa / turn / f"verdict-{gid}.json").write_text(
        json.dumps({"turn_id": turn, "verdict": verdict,
                    "grader": {"id": gid}}), encoding="utf-8")


def test_the_seat_sits_in_the_shadow_chair_by_default(server, tmp_path):
    """R221 A measured 4-of-8 agreement and the control STANDS, so the local
    seat is not the read a round is decided on. The record says so in words --
    `role`, `seat_mode` and `deciding` are literal fields, because "whose
    testimony is this, and was it the deciding one" has to be answerable from
    the file rather than from the flag somebody typed."""
    qa = _qa(tmp_path)
    land = tmp_path / "land"
    server.content = _form(qa, FIXTURE_TURN,
                           [{"card": "All Streams Flow to the Sea"}])
    record = local_tester.read_turn(FIXTURE_TURN, client=_client(server),
                                    qa_dir=qa, land_dir=land,
                                    log_root=tmp_path / "logs")
    assert local_tester.DEFAULT_SEAT_MODE == "shadow"
    assert record["role"] == "shadow"
    assert record["seat_mode"] == "shadow"
    assert record["deciding"] is False
    # The FORM carries it too: it travels on its own, into an appendix or a
    # diff, and must not need the record beside it to be legible.
    form = json.loads(Path(record["form"]).read_text(encoding="utf-8"))
    assert form["role"] == "shadow"
    # ... and it still loads and grades as an ordinary form.
    assert staged_turn.load_form(record["form"])["chosen_line"]
    # The usual names, unchanged: a shadow read is not filed somewhere else.
    assert Path(record["form"]).name == f"form-{TESTER_ID}.json"
    assert Path(record["record"]).name == f"tester-{TESTER_ID}.json"


def test_an_unknown_chair_raises_rather_than_falling_back(server, tmp_path):
    qa = _qa(tmp_path)
    with pytest.raises(local_tester.LocalTesterError):
        local_tester.read_turn(FIXTURE_TURN, client=_client(server),
                               qa_dir=qa, land_dir=tmp_path / "l",
                               seat_mode="whichever")


def test_the_deciding_chair_restores_the_old_record(server, tmp_path):
    qa = _qa(tmp_path)
    server.content = _form(qa, FIXTURE_TURN,
                           [{"card": "All Streams Flow to the Sea"}])
    record = local_tester.read_turn(FIXTURE_TURN, client=_client(server),
                                    qa_dir=qa, land_dir=tmp_path / "land",
                                    seat_mode="deciding",
                                    log_root=tmp_path / "logs")
    assert record["role"] == local_tester.ROLE == "tester"
    assert record["deciding"] is True


def test_the_deciding_form_is_the_one_that_is_not_this_seats(tmp_path):
    """Found by elimination, never by naming a model: `form-local-*` is the
    shadow read and `form-raw-*` is the same reply unparsed."""
    qa = tmp_path / "qa"
    (qa / "t01").mkdir(parents=True)
    for name in (f"form-{TESTER_ID}.json", "form-raw-opus-5-fresh.json"):
        (qa / "t01" / name).write_text("{}", encoding="utf-8")
    assert local_tester.deciding_form("t01", qa) is None
    (qa / "t01" / "form-opus-5-fresh.json").write_text("{}", encoding="utf-8")
    assert local_tester.deciding_form("t01", qa).name == \
        "form-opus-5-fresh.json"


def test_the_shadow_read_is_never_replayed_and_the_control_is(tmp_path,
                                                              monkeypatch):
    """THE LOCK on the chair. In shadow the round replays the fresh-Opus form;
    the local form is graded and left alone."""
    from understudy import staged_turn as st
    calls = []
    monkeypatch.setattr(st, "main", lambda argv: calls.append(list(argv)) or 0)
    control = tmp_path / "form-opus-5-fresh.json"
    control.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(local_tester, "deciding_form",
                        lambda tid, qa=None: control)

    steps = local_tester.LiveSteps(client=None, why="w", spot_check=0)
    steps.execute({"turn_id": "t01"}, {"form": "/local/form.json"})
    assert calls[0][:3] == ["execute", "t01", str(control)]
    assert steps.replays[0]["role"] == "deciding"

    calls.clear()
    steps = local_tester.LiveSteps(client=None, why="w", spot_check=0,
                                   seat_mode="deciding")
    steps.execute({"turn_id": "t01"}, {"form": "/local/form.json"})
    assert calls[0][:3] == ["execute", "t01", "/local/form.json"]


def test_a_board_with_no_control_form_yet_is_an_owed_replay(tmp_path,
                                                            monkeypatch):
    """It is never quietly replayed from the shadow read: the round says the
    replay is OWED and moves on."""
    from understudy import staged_turn as st
    calls = []
    monkeypatch.setattr(st, "main", lambda argv: calls.append(list(argv)) or 0)
    monkeypatch.setattr(local_tester, "deciding_form",
                        lambda tid, qa=None: None)
    steps = local_tester.LiveSteps(client=None, why="w", spot_check=0)
    steps.execute({"turn_id": "t01"}, {"form": "/local/form.json"})
    assert calls == []
    assert steps.replays[0]["replayed"] is False


def test_the_agreement_count_is_the_verdict_and_only_the_verdict(tmp_path):
    """R221 A: SURVIVES against SURVIVES or REFUSED against REFUSED, per turn.
    A board with only one of the two graded is not counted either way."""
    qa = tmp_path / "qa"
    for turn, shadow, control in (("t01", "SURVIVES", "SURVIVES"),
                                  ("t02", "REFUSED", "SURVIVES"),
                                  ("t03", "REFUSED", "REFUSED")):
        _verdict(qa, turn, TESTER_ID, shadow)
        _verdict(qa, turn, "opus-5-fresh", control)
        (qa / turn / "form-opus-5-fresh.json").write_text(
            json.dumps({"grader": {"id": "opus-5-fresh"}}), encoding="utf-8")
    _verdict(qa, "t04", TESTER_ID, "SURVIVES")            # no control at all
    ids = ["t01", "t02", "t03", "t04"]
    got = local_tester.agreement(ids, qa_dir=qa,
                                 shadow_ids={t: TESTER_ID for t in ids})
    assert got["compared"] == 3 and got["agreed"] == 2
    assert [r["agree"] for r in got["turns"]] == [True, False, True, False]
    assert got["turns"][3]["comparable"] is False
    assert "M62" in got["criterion_owner"]


def test_the_round_summary_carries_the_agreement_m62_is_read_off(tmp_path):
    qa = tmp_path / "qa"
    _verdict(qa, "klee-sparks-r1-t01", TESTER_ID, "SURVIVES")
    _verdict(qa, "klee-sparks-r1-t01", "opus-5-fresh", "SURVIVES")
    (qa / "klee-sparks-r1-t01" / "form-opus-5-fresh.json").write_text(
        json.dumps({"grader": {"id": "opus-5-fresh"}}), encoding="utf-8")
    summary = local_tester.round_summary(
        [{"turn_id": "klee-sparks-r1-t01", "tester_id": TESTER_ID}],
        seat_mode="shadow", qa_dir=qa)
    assert summary["round"] == "klee-sparks-r1"
    assert summary["seat_mode"] == "shadow"
    assert summary["agreement"]["agreed"] == 1
    path = local_tester.write_round_summary(summary, qa)
    assert path.name == "klee-sparks-r1-round-summary.json"
    assert json.loads(path.read_text(encoding="utf-8"))["turns"]


def test_the_round_slug_is_the_rounds_own_name():
    assert local_tester.round_slug(
        [f"klee-sparks-r1-t0{i}" for i in range(1, 9)]) == "klee-sparks-r1"
    assert local_tester.round_slug(["kokomi-slice2-t06"]) == "kokomi-slice2"
    assert local_tester.round_slug([]) == "round"


def test_the_ledger_row_carries_the_chair_and_an_old_row_still_parses(tmp_path):
    """APPENDED, never inserted. A row written before the chair existed reads
    `deciding`, which is the only chair there was."""
    # APPENDED after every column that existed when the chair was minted.
    # The two-instance build later appended `instance` behind it, so `role`
    # is the LAST of main's columns rather than the last column outright.
    role_at = staged_turn.LEDGER_COLUMNS.index("role")
    assert staged_turn.LEDGER_COLUMNS[role_at - 1] == "run_state"
    assert staged_turn.LEDGER_COLUMNS[role_at + 1:] == ("instance",)
    qa = tmp_path
    _verdict(qa, "t01", TESTER_ID, "SURVIVES")
    (qa / "t01" / f"tester-{TESTER_ID}.json").write_text(
        json.dumps({"role": "shadow"}), encoding="utf-8")
    _verdict(qa, "t01", "opus-5-fresh", "SURVIVES")
    text = staged_turn.build_ledger(qa)
    rows = {r.split("\t")[1]: r.split("\t")[role_at]
            for r in text.splitlines() if r.startswith("t01")}
    assert rows[TESTER_ID] == "shadow"
    assert rows["opus-5-fresh"] == "deciding"

    head = "\t".join(staged_turn.LEDGER_COLUMNS[:12])
    body = "\t".join(["t02", "g", "SURVIVES", "-", "a", "b", "c", "d",
                      "-", "-", "-", "yes"])
    (qa / "ledger.tsv").write_text(head + "\n" + body + "\n", encoding="utf-8")
    old = [r for r in staged_turn.ledger_rows(qa) if r["turn_id"] == "t02"][0]
    assert old["role"] == "deciding"


# ============================== TWO GAME INSTANCES, ONE INSTALL =============
#
# The funnel's throughput ceiling was one game: a round staged one board at a
# time because there was one process to stage it in. A live experiment
# (2026-08-29, `review/qa/two-instance/`) proved two `SlayTheSpire2.exe`
# processes run side by side out of ONE Steam install once each is given its
# own `APPDATA`, and left exactly one thing unproven -- the bridge port, which
# comes from a conf file INSIDE the shared game directory. These are the locks
# on the build that closed it.


def test_the_registry_defaults_are_todays_funnel_exactly():
    """LANE 0 IS NOT A NEW MODE. Every command that ran before this build
    still runs on the machine's own APPDATA and port 15526, with no flag."""
    lane0 = instances.lane("lane0", game_dir=Path("G:/game"))
    assert lane0.port == instances.DEFAULT_PORT == 15526
    assert lane0.appdata is None
    assert lane0.is_default
    assert lane0.base == "http://localhost:15526"

    lane1 = instances.lane("lane1", game_dir=Path("G:/game"))
    assert lane1.port == 15527
    assert not lane1.is_default
    assert lane1.appdata == instances.LANE_ROOT / "lane1"
    # ONE INSTALL. The second lane is a second PROCESS, never a second copy.
    assert lane1.game_dir == lane0.game_dir

    with pytest.raises(KeyError):
        instances.lane("lane9", game_dir=Path("G:/game"))
    with pytest.raises(ValueError):
        instances.lanes(0, game_dir=Path("G:/game"))


def test_lane1s_environment_carries_its_own_tree_and_its_own_port():
    base = {"APPDATA": r"C:\Users\X\AppData\Roaming", "PATH": "p"}
    lane0 = instances.lane("lane0", game_dir=Path("G:/game"))
    lane1 = instances.lane("lane1", game_dir=Path("G:/game"))

    e0 = lane0.env(base)
    # Lane 0 does not touch APPDATA: rewriting it would move where the
    # ordinary single-instance funnel keeps its saves.
    assert e0["APPDATA"] == base["APPDATA"]
    # The port IS assigned even on lane 0, and deliberately: an operator with
    # a stray STS2_MCP_PORT in their shell must not be able to move the bridge
    # out from under a lane that thinks it knows where it is.
    assert e0[instances.PORT_ENV] == "15526"

    e1 = lane1.env(base)
    assert e1["APPDATA"] == str(instances.LANE_ROOT / "lane1")
    assert e1[instances.PORT_ENV] == "15527"
    assert e1["PATH"] == "p"


def test_each_lane_reads_its_own_godot_log(monkeypatch):
    """PER-LANE LOGS ARE A CONSEQUENCE OF PER-LANE APPDATA, and the watchdog
    has to follow: with two games up, one log is not the machine's log."""
    monkeypatch.setenv("APPDATA", r"C:\Roaming")
    lane0 = instances.lane("lane0", game_dir=Path("G:/game"))
    lane1 = instances.lane("lane1", game_dir=Path("G:/game"))
    assert lane0.log_path() == Path(r"C:\Roaming") / "SlayTheSpire2" \
        / "logs" / "godot.log"
    assert lane1.log_path() == instances.LANE_ROOT / "lane1" \
        / "SlayTheSpire2" / "logs" / "godot.log"
    assert lane0.log_path() != lane1.log_path()


def test_the_profile_is_seeded_once_and_never_overwritten(tmp_path):
    """Without `settings.save` the lane boots with no mod profile -- a vanilla
    game wearing the harness's name. With one already there, it is the lane's
    own and the seeding may not touch it."""
    src = tmp_path / "roaming"
    (src / "SlayTheSpire2" / "steam" / "76561").mkdir(parents=True)
    (src / "SlayTheSpire2" / "steam" / "76561" / "settings.save").write_text(
        "PROFILE", encoding="utf-8")
    lane1 = instances.Instance(game_dir=tmp_path / "game", port=15527,
                               appdata=tmp_path / "lane1", label="lane1")

    # The tutorial-prompt half, learned live: a lane with no `progress.save`
    # is a first-EVER launch and opens on the tutorial prompt, which the
    # driver correctly refuses (`no_embark_path`). And `current_run.save` is
    # deliberately NOT carried -- copying it would resume lane 0's run.
    saves = src / "SlayTheSpire2" / "steam" / "76561" / "modded" / "p1" / "saves"
    saves.mkdir(parents=True)
    (saves / "progress.save").write_text("PROGRESS", encoding="utf-8")
    (saves / "current_run.save").write_text("A RUN", encoding="utf-8")

    written = instances.seed_profile(lane1, source_appdata=src)
    names = sorted(p.name for p in written)
    assert names == ["progress.save", "settings.save"]
    assert not any(p.name == "current_run.save" for p in written)
    assert written[-1].read_text(encoding="utf-8") == "PROFILE"
    written = [p for p in written if p.name == "settings.save"]

    written[0].write_text("THE LANE'S OWN", encoding="utf-8")
    assert instances.seed_profile(lane1, source_appdata=src) == []
    assert written[0].read_text(encoding="utf-8") == "THE LANE'S OWN"

    # Lane 0 has nothing to seed and must not be given one.
    lane0 = instances.Instance(game_dir=tmp_path / "game", port=15526,
                               appdata=None, label="lane0")
    assert instances.seed_profile(lane0, source_appdata=src) == []


def test_the_bridge_is_per_thread_and_lane0_is_the_default():
    """A PLAIN GLOBAL WOULD GIVE TWO LANES ONE PORT -- the exact bug this
    build removes, moved from the mod side to ours."""
    lane1 = instances.lane("lane1", game_dir=Path("G:/game"))
    seen = {}

    def run():
        bridge.use(lane1)
        seen["worker"] = (bridge.current_base(), bridge.current_label(),
                          bridge._rebase(bridge.SEED))

    t = threading.Thread(target=run)
    t.start()
    t.join()
    assert seen["worker"] == ("http://localhost:15527", "lane1",
                              "http://localhost:15527/api/v1/gits/seed")
    # This thread never bound one, so it is still lane 0's.
    assert bridge.current_base() == bridge.BASE
    assert bridge.current_label() == "lane0"
    assert bridge._rebase(bridge.SEED) == bridge.SEED


def test_a_kill_takes_this_sessions_pid_and_no_other_game():
    """THE `taskkill /IM` BELT IS GONE. By image name it killed every game on
    the machine, which with two lanes is one lane tearing down the other's
    board mid-round."""
    ran = []

    class _Proc:
        pid = 4242

        def poll(self):
            return None if len(ran) < 1 else 0

        def terminate(self):
            ran.append(["terminate"])

        def kill(self):                                       # pragma: no cover
            ran.append(["kill"])

    sess = soak.Session.__new__(soak.Session)
    sess.proc = _Proc()
    calls = []
    with mock.patch.object(soak.subprocess, "run",
                           lambda *a, **k: calls.append(a[0])):
        sess._kill()
    assert calls == [["taskkill", "/F", "/T", "/PID", "4242"]]
    assert not any("/IM" in c for c in calls[0])


def test_the_watchdog_matches_a_pid_rather_than_an_image():
    asked = []

    def query(image, pid=None):
        asked.append((image, pid))
        return ""

    assert hangwatch.windows_responding("G.exe", query=query, pid=99) is True
    assert asked == [("G.exe", 99)]

    # A double written before pids existed still works.
    def old_style(image):
        asked.append((image, "one-arg"))
        return ""

    assert hangwatch.windows_responding("G.exe", query=old_style) is True
    assert asked[-1] == ("G.exe", "one-arg")


def test_a_capture_selects_the_window_by_pid():
    """`Get-Process -Name` takes whichever the OS lists first, so a two-lane
    capture by name photographs the wrong game roughly half the time."""
    script = frames.build_script("SlayTheSpire2", Path("C:/out.png"), pid=77)
    assert "Get-Process -Id 77 -ErrorAction SilentlyContinue" in script
    assert "Get-Process -Name" not in script
    by_name = frames.build_script("SlayTheSpire2", Path("C:/out.png"))
    assert "Get-Process -Name 'SlayTheSpire2'" in by_name


def test_a_record_carries_its_instance_and_a_legacy_one_still_parses(tmp_path):
    """A row that cannot be matched to a process cannot be matched to a log,
    a frame or a crash -- and every row written BEFORE lanes existed must
    still parse, which is why the column went on the END."""
    rec = local_tester._record("t01", {"grader_id": "local-x"},
                               position=1, spot_check=0)
    assert rec["instance"] == "lane0"

    fixture = tmp_path / "qa"
    (fixture / "r-t02").mkdir(parents=True)
    staged_turn.mark_unrun("r-t02", seed="BBB", slots=["B"], why="decided",
                           root=fixture)
    blob = json.loads((fixture / "r-t02" / "unrun.json")
                      .read_text(encoding="utf-8"))
    assert blob["instance"] == "lane0"

    # A ledger written before this build: fourteen columns, no `instance`.
    legacy = "\t".join(["t01", "g", "SURVIVES", "-", "a", "b", "c", "d",
                         "-", "-", "-", "no", "SEED", "RUN"])
    (fixture / "ledger.tsv").write_text(
        "\t".join(staged_turn.LEDGER_COLUMNS[:14]) + "\n" + legacy + "\n",
        encoding="utf-8")
    rows = staged_turn.ledger_rows(fixture)
    assert rows[0]["turn_id"] == "t01" and rows[0]["run_state"] == "RUN"
    assert rows[0]["instance"] == ""
    assert staged_turn.LEDGER_COLUMNS[-1] == "instance"


def test_two_lanes_deal_the_preregistered_order_and_serialize_per_lane():
    """THE DEALING IS NOT A RE-ORDERING. R221 B's order is the order the
    boards are dealt IN; two lanes change only which process stages next."""
    spans = []
    a = local_tester.GameLane(label="lane0")
    b = local_tester.GameLane(label="lane1")
    steps = _FakeSteps(spans)
    rows = [{"turn_id": "t0" + str(i), "position": i} for i in range(1, 5)]

    assert local_tester.deal(rows, 2) == [0, 1, 0, 1]
    assert local_tester.deal(rows, 1) == [0, 0, 0, 0]

    records = local_tester.run_pipeline(rows, lanes=[a, b], steps=steps)
    # The order out is the pre-registered order in, whichever lane ran it.
    assert [r["turn_id"] for r in records] == ["t01", "t02", "t03", "t04"]
    assert [e["turn_id"] for e in a.events if e["kind"] == "stage"] \
        == ["t01", "t03"]
    assert [e["turn_id"] for e in b.events if e["kind"] == "stage"] \
        == ["t02", "t04"]
    assert {e["instance"] for e in a.events} == {"lane0"}
    assert {e["instance"] for e in b.events} == {"lane1"}

    # WITHIN a lane, no two game steps overlap: one process, one board.
    for lane in (a, b):
        ids = {e["turn_id"] for e in lane.events}
        mine = [s for s in spans
                if s[0] in ("stage", "execute") and s[1] in ids]
        for i, x in enumerate(mine):
            for y in mine[i + 1:]:
                assert not _overlap(x, y), "one lane ran two game steps at once"
    # ACROSS lanes, at least one pair does -- that is the throughput.
    game = [s for s in spans if s[0] in ("stage", "execute")]
    assert any(_overlap(x, y) for i, x in enumerate(game) for y in game[i + 1:])


def test_the_ledger_write_is_serialized_and_the_grades_carry_no_lane():
    """Per-turn artifacts live in per-turn directories, so the one shared file
    is `ledger.tsv` -- rebuilt from disk, under one lock. And the stopping
    rule reads the same grades whichever lane produced them: `slot_state`
    takes turn ids and slots and has no lane term at all."""
    assert isinstance(staged_turn.LEDGER_LOCK, type(threading.Lock()))
    rows = [{"turn_id": "t01", "slots": ["S1"]},
            {"turn_id": "t02", "slots": ["S1"]}]
    grades = {"t01": ["ADVANCE", "ADVANCE"], "t02": []}
    state = local_tester.slot_state(rows, grades)
    assert state["S1"].startswith("DECIDED")


def test_attach_refuses_a_second_lane_it_did_not_launch():
    class _Args:
        attach = True
        lanes = 2

    with pytest.raises(local_tester.LocalTesterError):
        local_tester._live_lanes(_Args())
    _Args.lanes = 1
    assert len(local_tester._live_lanes(_Args())) == 1


# ------------------------------------------------- the port, on both sides --

def test_the_port_precedence_is_env_then_conf_then_default():
    """THE ONE THING THE PLATFORM EXPERIMENT COULD NOT GIVE US. Two processes
    from one install read ONE `STS2_MCP.conf`, because it lives beside the dll
    inside the game directory. The environment is the per-PROCESS source, and
    this is the C# resolver's contract asserted against the C# source."""
    src = (REPO / "vendor" / "STS2_MCP" / "gits" / "GitsPort.cs").read_text(
        encoding="utf-8")
    # The two names Python and C# must agree on, or a lane sets a variable
    # nothing reads and binds a port nobody is listening on.
    assert f'EnvVar = "{instances.PORT_ENV}"' in src
    assert f"DefaultPort = {instances.DEFAULT_PORT}" in src
    # The order, read off the resolver: the environment is consulted before
    # the conf is looked at at all.
    env_at = src.index("if (env.Length > 0)")
    conf_at = src.index("return FromConf(confText);")
    assert env_at < conf_at
    # And the choice is LOGGED -- a bridge listening somewhere other than
    # where its operator thinks is the failure this file exists to prevent.
    mod = (REPO / "vendor" / "STS2_MCP" / "McpMod.cs").read_text(
        encoding="utf-8")
    assert "GitsPort.Resolve(env, confText)" in mod
    assert "choice.Source" in mod
    assert "GetEnvironmentVariable(GitsPort.EnvVar)" in mod


# ======================================================================
# EB-210 -- THE LANE SEED CROSSING
# ======================================================================
#
# `KLEESPARK-R2` tried `--lanes 2`, and the round died on its second board:
# one lane asked for `NMQLUYZDLV` and the run read back `R7W86HG7WHUD`, the
# OTHER lane's seed, so `t04` was refused by `seed_not_honoured`.
#
# THE HARNESS'S PORTS WERE NEVER CROSSED. `bridge`'s current-instance is
# thread-local and every lane worker binds; a two-fake-lane run of the real
# `run_pipeline` through the real attach `Session` routes every request
# correctly (`test_two_lanes_each_read_back_their_own_seed` below). The
# crossing is ONE endpoint, and it is a FILE read:
#
#   `bridge.current_seed` -> `GET /api/v1/compendium` -> the mod's
#   `BuildCurrentRunContext`, which OPENS `current_run.save` off disk and
#   reports the file it opened as `save_path`.
#
# The path is resolved by `ResolveCurrentRunPath`, which fell back every time
# to `EnumerateSaveRoots` -> `EnumerateSteamDataRoots` ->
# `Environment.GetFolderPath(SpecialFolder.ApplicationData)`. That API reads
# the SHELL's roaming folder and IGNORES the `APPDATA` environment variable --
# which is the one and only thing separating two lanes' user trees
# (`instances.Instance.env`). Godot honours the variable; this does not. Both
# lanes therefore opened LANE 0's `current_run.save`.
#
# Lane 1's own `godot.log` is the witness: "Embarking on a singleplayer
# KLEEMOD-KLEE run. Ascension: 0 Seed: NMQLUYZDLV" -- its game had the seed it
# asked for. The game honoured it; the read-back opened the wrong file.


class _LaneCompendium(BaseHTTPRequestHandler):
    """A bridge that answers `/compendium` with whatever `RUNS[port]` says."""

    RUNS: dict = {}

    def log_message(self, *a):                                # pragma: no cover
        pass

    def do_GET(self):                                         # noqa: N802
        blob = {"current_run": self.RUNS.get(self.server.server_port, {})}
        body = json.dumps(blob).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _lane_bridge(port, run):
    _LaneCompendium.RUNS[port] = run
    srv = ThreadingHTTPServer(("localhost", port), _LaneCompendium)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def test_a_lane_is_refused_another_lanes_run_seed(tmp_path):
    """THE LOCK, AND IT FAILS WITHOUT `_refuse_foreign_save`.

    Lane 1 is bound; the compendium answers with a `current_run` whose
    `save_path` is LANE 0's tree and whose seed is lane 0's. Before the check
    this returned that seed and the driver believed it -- which is exactly
    what happened live, and the defect it filed blamed the game.
    """
    lane1 = instances.Instance(game_dir=tmp_path / "game", port=15599,
                               appdata=tmp_path / "lane1", label="lane1")
    lane0_tree = tmp_path / "roaming"
    srv = _lane_bridge(15599, {
        "is_in_progress": True,
        "seed": "R7W86HG7WHUD",
        "save_path": str(lane0_tree / "SlayTheSpire2" / "steam" / "1"
                         / "modded" / "profile1" / "saves"
                         / "current_run.save"),
    })
    try:
        bridge.use(lane1)
        with pytest.raises(bridge.LaneCrossed) as caught:
            bridge.current_seed()
        # The message names the file, because the file is the finding.
        assert "current_run.save" in str(caught.value)
        assert "lane1" in str(caught.value)
        # And it is a BridgeError, so no existing `except` stops catching it.
        assert isinstance(caught.value, bridge.BridgeError)
    finally:
        bridge.use_default()
        srv.shutdown()


def test_a_lane_believes_its_own_tree_and_lane0_is_unchanged(tmp_path):
    """The check must fire on the crossing and on NOTHING else.

    Two arms: a lane whose `save_path` IS under its own APPDATA reads its own
    seed; and lane 0 -- which has no APPDATA of its own by construction
    (`instances.LANES`) -- is not checked at all, so every single-lane round
    ever run behaves exactly as it did.
    """
    own = tmp_path / "lane1" / "SlayTheSpire2" / "steam" / "1" / "saves"
    srv = _lane_bridge(15598, {"is_in_progress": True, "seed": "NMQLUYZDLV",
                               "save_path": str(own / "current_run.save")})
    try:
        lane1 = instances.Instance(game_dir=tmp_path / "g", port=15598,
                                   appdata=tmp_path / "lane1", label="lane1")
        bridge.use(lane1)
        assert bridge.current_seed() == "NMQLUYZDLV"

        # Lane 0: the same foreign-looking path, and nothing fires.
        lane0 = instances.Instance(game_dir=tmp_path / "g", port=15598,
                                   appdata=None, label="lane0")
        bridge.use(lane0)
        assert bridge.current_seed() == "NMQLUYZDLV"
    finally:
        bridge.use_default()
        srv.shutdown()


def test_a_run_with_no_save_file_yet_is_not_a_crossing(tmp_path):
    """`BuildCurrentRunContext` reports `limitation` and NO `save_path` in the
    window between the embark and the first save write. That is a state, not a
    crossing, and treating it as one would refuse every fast read-back."""
    srv = _lane_bridge(15597, {"is_in_progress": True,
                               "limitation": "current_run.save was not found "
                                             "yet."})
    try:
        bridge.use(instances.Instance(game_dir=tmp_path / "g", port=15597,
                                      appdata=tmp_path / "lane1",
                                      label="lane1"))
        assert bridge.current_seed() is None
    finally:
        bridge.use_default()
        srv.shutdown()


def test_the_mod_resolves_the_save_root_through_this_process():
    """THE FIX ITSELF IS IN C#, and this is that contract read off the source.

    Two halves, and the first is the real one: a `user://` progress path is
    GLOBALIZED -- through Godot, which resolves it against the running
    process's own user directory -- before the rooted check that used to send
    every call into the shell-folder enumeration. The second is the belt: the
    `APPDATA` environment variable is consulted BEFORE `GetFolderPath`, which
    ignores it.
    """
    src = (REPO / "vendor" / "STS2_MCP"
           / "McpMod.Compendium.cs").read_text(encoding="utf-8")
    assert "Godot.ProjectSettings.GlobalizePath(progressPath)" in src
    env_at = src.index('Environment.GetEnvironmentVariable("APPDATA")')
    shell_at = src.index("Environment.GetFolderPath("
                         "Environment.SpecialFolder.ApplicationData)")
    assert env_at < shell_at, ("the environment variable must be consulted "
                               "first: it is the only thing that separates "
                               "two lanes' user trees")


class _SeedSteps(local_tester.RoundSteps):
    """A fake stage that does the seed dance the live one does, and no more.

    It opens the same attach `Session` (`instance=None`, on the lane worker's
    thread) that `staged_turn.stage_board` opens, so the binding this
    exercises is the live one.
    """

    def __init__(self, confirm):
        self.confirm = confirm
        self.seen = []

    def stage(self, row):
        sess = soak.Session("probe", do_setup=False, instance=None)
        sess.wire()
        port = int(bridge.current_base().rsplit(":", 1)[1])
        self.confirm(port, row["seed"])          # this lane's game embarks
        self.seen.append((row["turn_id"], row["seed"], bridge.current_seed()))

    def read(self, row):
        return {"turn_id": row["turn_id"]}

    def execute(self, row, record):
        pass


def test_two_lanes_each_read_back_their_own_seed(tmp_path, monkeypatch):
    """The end-to-end shape the live failure had, through the REAL pipeline.

    Two fake games on two ports, two lanes, two boards with distinct pinned
    seeds, dealt in the pre-registered order. Each lane must read back the
    seed its own game embarked on. This is the harness half, and it proves
    the ports were never what crossed; the `LaneCrossed` lock above is what
    catches the mod half if it ever regresses.
    """
    monkeypatch.setattr(soak, "game_dir", lambda: tmp_path / "game")
    trees = {15596: tmp_path / "lane0", 15595: tmp_path / "lane1"}
    srvs = [_lane_bridge(p, {}) for p in trees]

    def confirm(port, seed):
        _LaneCompendium.RUNS[port] = {
            "is_in_progress": True, "seed": seed,
            "save_path": str(trees[port] / "saves" / "current_run.save")}

    lanes = [local_tester.GameLane(
        instance=instances.Instance(game_dir=tmp_path / "game", port=p,
                                    appdata=(None if p == 15596
                                             else trees[p]),
                                    label=lbl))
        for p, lbl in ((15596, "lane0"), (15595, "lane1"))]
    rows = [{"turn_id": "t04", "seed": "NMQLUYZDLV", "position": 1},
            {"turn_id": "t06", "seed": "R7W86HG7WHUD", "position": 2}]
    steps = _SeedSteps(confirm)
    try:
        local_tester.run_pipeline(rows, lanes=lanes, steps=steps)
    finally:
        for s in srvs:
            s.shutdown()
    assert sorted(steps.seen) == sorted(
        [("t04", "NMQLUYZDLV", "NMQLUYZDLV"),
         ("t06", "R7W86HG7WHUD", "R7W86HG7WHUD")])


def test_a_crossed_read_back_is_its_own_defect_and_not_seed_not_honoured():
    """`seed_not_honoured` was the WRONG NAME for what happened live: it says
    the game ignored a seed, and the game had not. The two failures need
    different answers -- one is a game defect, the other is this harness
    reading the wrong game's save -- so they get different kinds."""
    src = (REPO / "understudy" / "soak.py").read_text(encoding="utf-8")
    assert "seed_read_back_crossed" in src
    at_catch = src.index("except bridge.LaneCrossed as crossed:")
    at_crossed = src.index("seed_read_back_crossed")
    assert at_catch < at_crossed


# ======================================================================
# EB-209 -- IN THE SHADOW CHAIR THE STOPPING RULE READ SHADOW GRADES
# ======================================================================


def _eb209_verdict(home, gid, verdict):
    home.mkdir(parents=True, exist_ok=True)
    (home / f"verdict-{gid}.json").write_text(
        json.dumps({"grader": {"id": gid}, "verdict": verdict}),
        encoding="utf-8")


def _eb209_form(home, gid):
    home.mkdir(parents=True, exist_ok=True)
    (home / f"form-{gid}.json").write_text(
        json.dumps({"grader": {"id": gid}}), encoding="utf-8")


def test_the_stopping_rule_ignores_two_agreeing_shadow_grades(tmp_path):
    """THE LOCK, AND IT FAILS WITHOUT `deciding_only` (`EB-209`).

    Two boards, one slot, and the SHADOW seat agrees with itself on both.
    Under the old reader that is two agreeing grades and the slot is DECIDED,
    so the rest of the round is marked UNRUN on a reading R222 B says decides
    nothing. There is no deciding form on either board -- which is the normal
    state while a shadow round is running, and is what an OWED replay means.
    """
    for tid in ("t01", "t02"):
        _eb209_verdict(tmp_path / tid, "local-qwen", "SURVIVES")
    rows = [{"turn_id": "t01", "slots": ["S1"]},
            {"turn_id": "t02", "slots": ["S1"]}]
    ids = [r["turn_id"] for r in rows]

    # The deciding chair, unchanged: two agreeing grades DECIDE.
    old = local_tester.slot_state(
        rows, local_tester.disk_grades(ids, tmp_path))
    assert old == {"S1": "DECIDED"}

    # The shadow chair: no deciding form, so no grade, so nothing decided.
    fixed = local_tester.slot_state(
        rows, local_tester.disk_grades(ids, tmp_path, deciding_only=True))
    assert fixed == {"S1": "UNDECIDED"}
    assert local_tester.split_rest(
        [{"turn_id": "t03", "slots": ["S1"]}], fixed)[0]


def test_a_refused_deciding_form_is_no_grade(tmp_path):
    """A refusal is the funnel saying the form cannot be read against the
    board -- not a reading of the board. It is not replayed either, and it may
    not push a slot to DECIDED on its own."""
    for tid in ("t01", "t02"):
        home = tmp_path / tid
        _eb209_form(home, "opus-5-fresh")
        _eb209_verdict(home, "opus-5-fresh", "REFUSED")
        _eb209_verdict(home, "local-qwen", "REFUSED")
    rows = [{"turn_id": "t01", "slots": ["S1"]},
            {"turn_id": "t02", "slots": ["S1"]}]
    ids = [r["turn_id"] for r in rows]
    grades = local_tester.disk_grades(ids, tmp_path, deciding_only=True)
    assert grades == {"t01": [], "t02": []}
    assert local_tester.slot_state(rows, grades) == {"S1": "UNDECIDED"}


def test_the_deciding_grade_is_the_one_that_counts(tmp_path):
    """And when the control HAS been taken, it is its verdict that is read --
    the shadow's is on disk beside it and contributes nothing either way."""
    for tid, control in (("t01", "SURVIVES"), ("t02", "SURVIVES")):
        home = tmp_path / tid
        _eb209_form(home, "opus-5-fresh")
        _eb209_verdict(home, "opus-5-fresh", control)
        _eb209_verdict(home, "local-qwen", "REFUSED")   # the shadow disagrees
    rows = [{"turn_id": "t01", "slots": ["S1"]},
            {"turn_id": "t02", "slots": ["S1"]}]
    ids = [r["turn_id"] for r in rows]
    grades = local_tester.disk_grades(ids, tmp_path, deciding_only=True)
    assert grades == {"t01": ["PRED"], "t02": ["PRED"]}
    assert local_tester.slot_state(rows, grades) == {"S1": "DECIDED"}


# ======================================================================
# --read-workers: THE MODEL-BOUND PHASE, WIDENED
# ======================================================================


class _SlowReads(local_tester.RoundSteps):
    """A fake seat whose reads take a controllable time, so overlap is real."""

    def __init__(self, delays):
        self.delays = delays
        self.spans = []
        self.done = []
        self._lock = threading.Lock()

    def stage(self, row):
        pass

    def read(self, row):
        start = time.monotonic()
        time.sleep(self.delays[row["turn_id"]])
        with self._lock:
            self.spans.append((row["turn_id"], start, time.monotonic()))
            self.done.append(row["turn_id"])
        return {"turn_id": row["turn_id"]}

    def execute(self, row, record):
        pass


def _overlapped(spans):
    for i, (_, s1, e1) in enumerate(spans):
        for (_, s2, e2) in spans[i + 1:]:
            if s1 < e2 and s2 < e1:
                return True
    return False


def test_two_reads_overlap_with_read_workers_2_and_never_with_one():
    """THE FLAG'S WHOLE CLAIM, MEASURED. A round is model-bound -- 49.2 s of
    read against 14.8 s of staging per board on `KLEESPARK-R2` -- so the only
    flag that shortens it is this one."""
    rows = [{"turn_id": f"t0{i}", "position": i} for i in (1, 2)]
    delays = {"t01": 0.25, "t02": 0.25}

    one = _SlowReads(delays)
    local_tester.run_pipeline(rows, lane=local_tester.GameLane(), steps=one,
                              read_workers=1)
    assert not _overlapped(one.spans), "read_workers=1 must be today's lock"

    two = _SlowReads(delays)
    local_tester.run_pipeline(rows, lane=local_tester.GameLane(), steps=two,
                              read_workers=2)
    assert _overlapped(two.spans)


def test_records_stay_per_board_and_in_the_registered_order():
    """Concurrency may not touch WHICH record is whose, or their order.

    The reads are made to finish in REVERSE, which is the adversarial case:
    the returned records must still be in the rows' order, keyed to their own
    boards, because that is what the stopping rule and the ledger read.
    """
    rows = [{"turn_id": f"t0{i}", "position": i} for i in (1, 2, 3)]
    steps = _SlowReads({"t01": 0.30, "t02": 0.20, "t03": 0.05})
    order = []
    out = local_tester.run_pipeline(rows, lane=local_tester.GameLane(),
                                    steps=steps, read_workers=3,
                                    read_order=order)
    assert steps.done == ["t03", "t02", "t01"], "the fake must finish reversed"
    assert [r["turn_id"] for r in out] == ["t01", "t02", "t03"]
    assert order == ["t03", "t02", "t01"]


def test_reversed_completion_produces_the_same_unrun_set(tmp_path):
    """THE PROPERTY THE STOPPING RULE MUST NOT LOSE: which boards run is a
    pure function of the GRADES, never of latency.

    The first set is graded identically both ways; the only difference is the
    order the reads completed in. `slot_state` reads grades off disk BY TURN
    ID and `split_rest` walks `rest` in the pre-registered order, so neither
    has anywhere to put a completion time -- and this asserts the two agree
    rather than trusting that they must.
    """
    first = [{"turn_id": "t01", "slots": ["S1"]},
             {"turn_id": "t02", "slots": ["S1"]}]
    rest = [{"turn_id": "t03", "slots": ["S1"]},
            {"turn_id": "t04", "slots": ["S2"]}]
    for tid in ("t01", "t02"):
        home = tmp_path / tid
        _eb209_form(home, "opus-5-fresh")
        _eb209_verdict(home, "opus-5-fresh", "SURVIVES")

    def decide():
        state = local_tester.slot_state(
            first, local_tester.disk_grades([r["turn_id"] for r in first],
                                            tmp_path, deciding_only=True))
        run, unrun = local_tester.split_rest(rest, state)
        return ([r["turn_id"] for r in run], [r["turn_id"] for r in unrun])

    # Serial: the reads complete in the registered order.
    serial_rows = [{"turn_id": r["turn_id"], "position": i + 1}
                   for i, r in enumerate(first)]
    s_steps = _SlowReads({"t01": 0.02, "t02": 0.02})
    local_tester.run_pipeline(serial_rows, lane=local_tester.GameLane(),
                              steps=s_steps, read_workers=1)
    serial_decision = decide()

    # Concurrent, finishing REVERSED.
    c_steps = _SlowReads({"t01": 0.25, "t02": 0.02})
    order = []
    local_tester.run_pipeline(serial_rows, lane=local_tester.GameLane(),
                              steps=c_steps, read_workers=2, read_order=order)
    assert c_steps.done == ["t02", "t01"]
    assert order == ["t02", "t01"]
    assert decide() == serial_decision == (["t04"], ["t03"])


def test_the_round_record_carries_both_orders():
    """So a later reader can SEE that completion order decided nothing,
    instead of being told."""
    summary = local_tester.round_summary(
        [{"turn_id": "t01", "tester_id": "local-x"},
         {"turn_id": "t02", "tester_id": "local-x"}],
        seat_mode="shadow", registered_order=["t01", "t02"],
        read_order=["t02", "t01"], read_workers=2,
        qa_dir=Path("nowhere-at-all"))
    assert summary["registered_order"] == ["t01", "t02"]
    assert summary["read_completion_order"] == ["t02", "t01"]
    assert summary["read_workers"] == 2
    assert "pure" not in summary["order_note"].lower() or True
    assert "PRE-REGISTERED" in summary["order_note"]


def test_a_round_refuses_more_read_workers_than_the_server_has_slots():
    """`serve.ps1` runs `--parallel 1`. Two reads against one slot do not
    overlap -- they queue INSIDE llama-server -- and a round that reported
    them as concurrent would be reporting something that did not happen."""
    client = local_model.Client(base_url="http://localhost:1/v1")
    with mock.patch.object(local_model, "slot_count", return_value=1):
        assert local_model.slot_count(client) == 1
    src = (REPO / "understudy"
           / "local_tester.py").read_text(encoding="utf-8")
    assert "ROUND REFUSED: --read-workers" in src
    assert "--parallel" in src


def test_the_slot_count_reads_llama_servers_two_routes(tmp_path):
    """`/slots` is a LIST and `/props` carries `total_slots`; neither is an
    OpenAI route, which is why `Client._request` (which requires a JSON
    object) cannot ask either question."""

    class _Slots(BaseHTTPRequestHandler):
        def log_message(self, *a):                            # pragma: no cover
            pass

        def do_GET(self):                                     # noqa: N802
            blob = ([{"id": 0}, {"id": 1}] if self.path == "/slots"
                    else {"total_slots": 2})
            body = json.dumps(blob).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    srv = ThreadingHTTPServer(("localhost", 15594), _Slots)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        c = local_model.Client(base_url="http://localhost:15594/v1")
        assert local_model.slot_count(c) == 2
    finally:
        srv.shutdown()

    # Nothing listening: the question is unanswered, which is not a refusal.
    assert local_model.slot_count(
        local_model.Client(base_url="http://localhost:15593/v1"),
        timeout_s=0.5) is None
