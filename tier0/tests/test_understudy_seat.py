"""The independent-model seat (`understudy/seat.py`), with no codex involved.

`codex exec` is never run here -- a test that needed a ChatGPT sign-in is a
test that does not run in CI. What CAN be pinned without one is everything
that makes the seat trustworthy:

  * the seat cannot reach a design sheet (an AST walk over its imports, the
    same pin `test_staged_turn` puts on `qa_packet.py`);
  * `soak.py` cannot reach the seat, the same way it cannot reach `scenario`;
  * THE THREE-SOURCE GUARD, fixture by fixture -- the stdout stream, codex's
    session rollout, and stderr, each refusing BY NAME, and an UNKNOWN type
    refusing in every one of them;
  * that a MISSING rollout refuses rather than passing, which is the whole
    difference between "no tool call was recorded" and "no record exists";
  * the identity fill's exact limit -- three fields, and a proof the wrapper
    cannot move a fourth;
  * prompt assembly against the REAL `review/qa/kokomi-first-turn-example/`
    files: the packet verbatim, the hash present, and not one envelope key;
  * the dry run's argv, which is the only place the guard flags are asserted
    to be there at all, and the scratch root's two properties -- empty, and
    OUTSIDE the repo, because codex reads `AGENTS.md` from its working root;
  * that the session directory is gitignored, since it holds the packet, a
    third party's system prompt and a third party's raw model output.

Mirrors `test_staged_turn.py` in shape. GUARDRAIL-7 is unchanged: nothing
here is a claim about whether a turn is fun.
"""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

import pytest

from understudy import seat

REPO = Path(__file__).resolve().parents[2]
EXAMPLE = REPO / "review" / "qa" / "kokomi-first-turn-example"


# ------------------------------------------------------- structural pins ---

def _imported_modules(path: Path) -> list[str]:
    named: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            named += [a.name for a in node.names]
        if isinstance(node, ast.ImportFrom):
            named.append(node.module or "")
    return named


def test_the_seat_cannot_reach_a_sheet():
    """The same guarantee as `qa_packet.py`, for the same reason: the module
    that assembles a BLIND prompt must have no route to a `role:` or a
    `tempo_band:` even by accident. `staged_turn` is imported inside the one
    function that files a graded form -- after the prompt has been built and
    the answer is already in."""
    named = _imported_modules(Path(seat.__file__))
    assert not [m for m in named if m.split(".")[0] in ("tier0", "tier05")], \
        f"the blind seat imports {named}"


def test_the_soak_cannot_reach_the_seat():
    """The unattended overnight loop must not be able to spend a third
    party's quota, or file a grade, while nobody is watching. Same pin and
    same reason as `test_understudy_scenario`'s scenario pin."""
    from understudy import soak

    assert not hasattr(soak, "seat")
    src = Path(soak.__file__).read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            assert all("seat" not in a.name.split(".") for a in node.names)
        if isinstance(node, ast.ImportFrom):
            assert "seat" not in (node.module or "").split(".")
            assert all(a.name != "seat" for a in node.names)
    assert "codex" not in src


def test_the_session_directory_is_gitignored():
    """A session holds the packet inlined into a prompt, codex's own system
    prompt, and a third party's raw model output. None of that is this
    repo's to redistribute; the FORM and the verdict under `review/qa/` are
    what get committed."""
    target = REPO / "understudy" / "logs" / "seat" / "x" / "rollout.jsonl"
    done = subprocess.run(
        ["git", "check-ignore", str(target)], cwd=str(REPO),
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert done.returncode == 0, \
        f"{target} is NOT gitignored: {done.stdout}{done.stderr}"
    keep = REPO / "understudy" / "logs" / "seat" / ".gitignore"
    assert keep.is_file(), "the ignore file itself must be committed"


# ---------------------------------------- source (1): the stdout stream ----

def _events(*items: str) -> list[dict]:
    """A `--json` stdout transcript with one item of each named type."""
    stream: list[dict] = [{"type": "thread.started", "thread_id": "abc"},
                          {"type": "turn.started"}]
    for i, kind in enumerate(items):
        stream.append({"type": "item.completed",
                       "item": {"id": f"item_{i}", "type": kind}})
    stream.append({"type": "turn.completed", "usage": {"output_tokens": 1}})
    return stream


CLEAN_ROLLOUT = [
    {"ordinal": 0, "type": "session_meta",
     "payload": {"session_id": "abc", "cwd": "/tmp/gits-seat-x",
                 "originator": "codex_exec", "source": "exec"}},
    {"ordinal": 1, "type": "world_state",
     "payload": {"full": True,
                 "state": {"agents_md": {},
                           "environments": {"environments": {"local": {
                               "cwd": "/tmp/gits-seat-x"}}}}}},
    {"ordinal": 2, "type": "turn_context", "payload": {"model": "gpt-5.6-sol"}},
    {"ordinal": 2, "type": "event_msg", "payload": {"type": "task_started"}},
    {"ordinal": 3, "type": "response_item",
     "payload": {"type": "message", "role": "user"}},
    {"ordinal": 4, "type": "response_item", "payload": {"type": "reasoning"}},
    {"ordinal": 5, "type": "response_item",
     "payload": {"type": "message", "role": "assistant"}},
    {"ordinal": 6, "type": "event_msg",
     "payload": {"type": "item_completed",
                 "item": {"type": "AgentMessage", "text": "{}"}}},
    {"ordinal": 7, "type": "event_msg", "payload": {"type": "task_complete"}},
]

TOOL_CALL_LINE = {
    "ordinal": 4, "type": "response_item",
    "payload": {"type": "custom_tool_call", "name": "exec",
                "input": 'tools.exec_command({cmd: "cat AGENTS.md"})'},
}


def test_a_clean_run_is_accepted():
    reason, offenders, counts = seat.guard(
        _events("reasoning", "agent_message"), CLEAN_ROLLOUT, "")
    assert reason == ""
    assert offenders == []
    assert counts["item.completed/agent_message"] == 1
    assert counts["rollout:response_item/message"] == 2
    assert counts["rollout:world_state"] == 1


@pytest.mark.parametrize("tool", ["command_execution", "mcp_tool_call",
                                  "web_search", "file_change", "todo_list",
                                  "collab_tool_call"])
def test_a_tool_item_on_stdout_refuses_the_seat(tool):
    reason, offenders, _ = seat.guard(_events("reasoning", tool),
                                      CLEAN_ROLLOUT, "")
    assert reason == "seat_used_tools"
    assert offenders == [tool]


def test_an_unknown_item_type_refuses_the_seat():
    """THE ALLOWLIST IS THE POINT. A Codex release that adds a tool item type
    this file has never heard of must fail closed on the day it ships; a
    denylist would pass it silently, and the published item union was already
    short by one tool (`collab_tool_call`) when this was written."""
    reason, offenders, _ = seat.guard(_events("holodeck_access"),
                                      CLEAN_ROLLOUT, "")
    assert reason == "seat_used_tools"
    assert offenders == ["holodeck_access"]


def test_an_unknown_event_type_refuses_the_seat():
    reason, offenders, _ = seat.guard([{"type": "thread.teleported"}],
                                      CLEAN_ROLLOUT, "")
    assert reason == "seat_used_tools"
    assert offenders == ["thread.teleported"]


def test_a_line_in_neither_shape_refuses_the_seat():
    """`read_jsonl` keeps an unparseable line as `{}` for exactly this
    refusal, rather than dropping it. A `msg`-shaped line is the app-server
    protocol, which `codex exec` does not speak -- reading one means this is
    not the stream we launched."""
    reason, offenders, _ = seat.guard(
        [{"hello": "world"}, {}, {"id": "0", "msg": {"type": "agent_message"}}],
        CLEAN_ROLLOUT, "")
    assert reason == "seat_used_tools"
    assert offenders == ["<unrecognised-line>", "msg:agent_message"]


def test_an_error_is_refused_but_is_not_called_a_tool():
    """A crash and a broken blindness claim are different findings, and
    filing one as the other would put a wiring failure into the record as a
    design fact."""
    reason, _, _ = seat.guard(
        [{"type": "turn.started"}, {"type": "turn.failed",
                                    "error": {"message": "boom"}}],
        CLEAN_ROLLOUT, "")
    assert reason == "codex_error"


def test_a_tool_outranks_an_error():
    reason, offenders, _ = seat.guard(
        _events("command_execution") + [{"type": "error", "message": "x"}],
        CLEAN_ROLLOUT, "")
    assert reason == "seat_used_tools"
    assert offenders == ["command_execution"]


# ------------------------------------------- source (2): the rollout -------

def test_the_stdout_stream_alone_cannot_prove_blindness():
    """THE MEASURED FACT THIS GUARD EXISTS FOR. In a live smoke the model
    attempted three shell commands and stdout showed only `agent_message`.
    Here the stdout stream is spotless and the rollout is where the tool call
    is; the seat is refused anyway, which is the entire reason the rollout is
    read."""
    rollout = CLEAN_ROLLOUT + [TOOL_CALL_LINE]
    clean_stdout = _events("reasoning", "agent_message")
    assert seat.guard_events(clean_stdout)[0] == []
    reason, offenders, _ = seat.guard(clean_stdout, rollout, "")
    assert reason == "seat_used_tools"
    assert offenders == ["custom_tool_call"]


@pytest.mark.parametrize("ptype", ["custom_tool_call", "custom_tool_call_output",
                                   "function_call", "local_shell_call",
                                   "web_search_call", "wormhole_call"])
def test_a_tool_response_item_refuses_the_seat(ptype):
    rollout = CLEAN_ROLLOUT + [{"ordinal": 9, "type": "response_item",
                                "payload": {"type": ptype}}]
    reason, offenders, _ = seat.guard(_events("agent_message"), rollout, "")
    assert reason == "seat_used_tools"
    assert offenders == [ptype]


def test_an_unknown_rollout_line_type_refuses_the_seat():
    rollout = CLEAN_ROLLOUT + [{"ordinal": 9, "type": "shadow_realm",
                                "payload": {}}]
    reason, offenders, _ = seat.guard(_events("agent_message"), rollout, "")
    assert reason == "seat_used_tools"
    assert offenders == ["rollout:shadow_realm"]


def test_an_unknown_event_msg_item_refuses_the_seat():
    """The rollout names items in CamelCase where stdout uses snake_case.
    Assuming the two vocabularies matched is how an allowlist quietly becomes
    a pass-through, so the CamelCase list is checked on its own terms."""
    rollout = CLEAN_ROLLOUT + [
        {"ordinal": 9, "type": "event_msg",
         "payload": {"type": "item_completed",
                     "item": {"type": "CommandExecution"}}}]
    reason, offenders, _ = seat.guard(_events("agent_message"), rollout, "")
    assert reason == "seat_used_tools"
    assert offenders == ["CommandExecution"]


def test_a_resumed_thread_s_settings_snapshot_passes_the_guard():
    """FOUND LIVE, on EB-168's first session. `codex exec resume` emits
    `thread_settings_applied`, which one-shot `codex exec` never does -- so
    this file had never met it, and every blind run died on its second action.
    It is a snapshot OF the thread's settings, not a model action, and the one
    observed live carried a restricted read-only filesystem and no developer
    instructions: evidence for the seat, not against it."""
    rollout = CLEAN_ROLLOUT + [
        {"ordinal": 9, "type": "event_msg",
         "payload": {"type": "thread_settings_applied",
                     "thread_settings": {"model": "gpt-5.6-sol",
                                         "permission_profile":
                                             {"network": "restricted"}}}}]
    reason, offenders, _ = seat.guard(_events("agent_message"), rollout, "")
    assert reason == "" and offenders == []


def test_a_missing_rollout_refuses_the_seat():
    """No evidence is not the same as good evidence. `--ephemeral` would
    suppress the rollout, which is why `grade_argv` does not pass it."""
    reason, _, _ = seat.guard(_events("agent_message"), None, "")
    assert reason == "seat_no_transcript"
    assert "no evidence is not good evidence" in \
        seat.REFUSAL_REASONS["seat_no_transcript"]
    assert "--ephemeral" not in seat.grade_argv("codex", Path("s"), Path("c"))


def test_a_loaded_agents_md_refuses_the_seat():
    """THE GUARD'S ONE POSITIVE READING. `world_state` states what the
    environment HELD, so an empty `agents_md` is evidence that nothing was
    there rather than evidence that nothing was recorded. A non-empty one is
    an `AGENTS.md` in reach -- in this repo, the map to the design docs -- and
    it refuses under its own name, not as a tool call."""
    assert seat.rollout_instructions(CLEAN_ROLLOUT) == []
    dirty = [dict(line) for line in CLEAN_ROLLOUT]
    dirty[1] = {"ordinal": 1, "type": "world_state",
                "payload": {"state": {"agents_md": {"AGENTS.md": "..."}}}}
    assert seat.rollout_instructions(dirty) == ["AGENTS.md"]
    reason, offenders, _ = seat.guard(_events("agent_message"), dirty, "")
    assert reason == "seat_saw_instructions"
    assert offenders == ["AGENTS.md"]


def test_the_model_is_read_from_the_rollout():
    """No `--json` event carries a `model` key on 0.150.1, so the rollout is
    the only place the SERVED model can be read."""
    assert seat.rollout_model(CLEAN_ROLLOUT) == "gpt-5.6-sol"
    assert seat.rollout_model([{"type": "event_msg", "payload": {}}]) == ""


def test_the_rollout_is_found_by_thread_id(tmp_path):
    """By id, never by "the most recent file": two seats run minutes apart
    must not be able to certify each other's transcript."""
    day = tmp_path / "sessions" / "2026" / "08" / "28"
    day.mkdir(parents=True)
    mine = day / "rollout-2026-08-28T10-00-00-abc.jsonl"
    other = day / "rollout-2026-08-28T10-05-00-zzz.jsonl"
    for p in (mine, other):
        p.write_text("{}\n", encoding="utf-8")
    assert seat.find_rollout("abc", home=tmp_path) == mine
    assert seat.find_rollout("nope", home=tmp_path) is None
    assert seat.find_rollout("", home=tmp_path) is None
    assert seat.thread_id(_events()) == "abc"
    assert seat.thread_id([{"type": "turn.started"}]) == ""


# -------------------------------------------- source (3): stderr -----------

def test_a_rejected_tool_call_on_stderr_refuses_the_seat():
    """Under a read-only sandbox every shell command is blocked, and the
    attempt lands here and nowhere else. The seat is refused for the ATTEMPT,
    not for the rejection -- a sandbox that let the command through would be
    caught by the rollout instead."""
    stderr = ('2026-08-28T10:00:00 ERROR codex_core::tools::router: '
              'error=exec_command failed for `powershell`: '
              'CreateProcess { message: "Rejected(blocked by policy)" }\n')
    assert seat.guard_stderr(stderr) == ["stderr:codex_core::tools::router"]
    reason, offenders, _ = seat.guard(_events("agent_message"),
                                      CLEAN_ROLLOUT, stderr)
    assert reason == "seat_used_tools"
    assert offenders == ["stderr:codex_core::tools::router"]


def test_ordinary_stderr_noise_is_not_a_refusal():
    assert seat.guard_stderr("Reading prompt from stdin...\nWorkdir: /tmp\n") \
        == []


def test_read_jsonl_keeps_a_bad_line(tmp_path):
    p = tmp_path / "events.jsonl"
    p.write_text('{"type": "turn.started"}\nnot json\n[]\n\n',
                 encoding="utf-8")
    assert seat.read_jsonl(p) == [{"type": "turn.started"}, {}, {}]
    assert seat.read_jsonl(tmp_path / "absent.jsonl") == []


# ------------------------------------------------------- identity fill -----

RAW_FORM = {
    "turn_id": "kokomi-slice1-t01",
    "packet_sha256": "deadbeef",
    "grader": {"id": "assistant", "kind": "assistant",
               "model": "whatever-i-think-i-am",
               "designed_these_cards": False},
    "chosen_line": [{"card": "Coral Guard", "target": None},
                    {"card": "Water's Edge", "target": "Shrinker Beetle"}],
    "q1_what_did_you_play": "one",
    "q2_other_line_considered": "two",
    "q3_what_it_gave_up": "three",
    "q4_different_intent": "four",
    "q4_changed": True,
}


def test_the_fill_touches_exactly_three_fields():
    """The wrapper's ENTIRE licence over a grader's answers. Everything
    outside `grader.id/kind/model` is compared field by field."""
    filled = seat.fill_identity(RAW_FORM, "codex-gpt-5.6-sol-fresh",
                               "gpt-5.6-sol")
    assert filled["grader"]["id"] == "codex-gpt-5.6-sol-fresh"
    assert filled["grader"]["kind"] == "llm"
    assert filled["grader"]["model"] == "gpt-5.6-sol"

    for key in RAW_FORM:
        if key == "grader":
            continue
        assert filled[key] == RAW_FORM[key], f"the wrapper moved {key!r}"
    assert set(filled) == set(RAW_FORM)
    assert set(filled["grader"]) == set(RAW_FORM["grader"])
    # And the source object is not mutated on the way through, so
    # `form-raw.json` beside it is still the model's own words.
    assert RAW_FORM["grader"]["id"] == "assistant"


def test_a_designer_declaration_survives_the_fill_and_refuses():
    """R213's first guard is DECLARED, and the wrapper is not allowed to tidy
    the declaration away. `staged_turn` then refuses the form, which is the
    correct outcome."""
    from understudy import staged_turn

    raw = json.loads(json.dumps(RAW_FORM))
    raw["grader"]["designed_these_cards"] = True
    filled = seat.fill_identity(raw, "codex-fresh", "gpt-5.6-sol")
    assert filled["grader"]["designed_these_cards"] is True
    refused = staged_turn.apply_falsifiers("t", filled, packet_sha=None,
                                           closeness=None)
    assert "grader_is_designer" in refused


def test_a_filled_form_is_a_form_staged_turn_can_read(tmp_path):
    from understudy import staged_turn

    filled = seat.fill_identity(RAW_FORM, "codex-fresh", "gpt-5.6-sol")
    p = tmp_path / "form.json"
    p.write_text(json.dumps(filled), encoding="utf-8")
    loaded = staged_turn.load_form(p)
    assert staged_turn.grader_id(loaded) == "codex-fresh"
    assert staged_turn.apply_falsifiers("t", loaded, packet_sha=None,
                                        closeness=None) == []


def test_the_fill_supplies_a_grader_that_answered_without_one():
    filled = seat.fill_identity({"q1_what_did_you_play": "x"}, "gid", "m")
    assert filled["grader"] == {"id": "gid", "kind": "llm", "model": "m"}
    assert filled["q1_what_did_you_play"] == "x"


# ---------------------------------------------------- the prompt, blind ----

def _example() -> tuple[str, dict]:
    packet_md = (EXAMPLE / "packet.md").read_text(encoding="utf-8")
    envelope = json.loads((EXAMPLE / "packet.json").read_text(encoding="utf-8"))
    return packet_md, envelope


def test_the_prompt_carries_the_packet_verbatim():
    packet_md, envelope = _example()
    prompt = seat.build_prompt(packet_md, envelope["packet_sha256"])
    assert packet_md in prompt
    assert envelope["packet_sha256"] in prompt
    # The four questions came from the template, not from this module.
    assert "What other line did you seriously consider?" in prompt
    assert "<PACKET>" not in prompt and "<SHA>" not in prompt


def test_the_prompt_carries_no_envelope_key():
    """`packet.json` is the ORCHESTRATOR's record; `packet.md` is the
    grader's page. `run_seed` is the reason they are two files: the encounter
    is generated from it, so a grader that saw it could reproduce the board it
    is meant to be reading cold. This asserts the general rule rather than
    that one key, so an envelope key added later is caught on the day it is
    added."""
    packet_md, envelope = _example()
    prompt = seat.build_prompt(packet_md, envelope["packet_sha256"])

    # The keys the grader's page legitimately renders, or the reply template
    # legitimately names. Everything else in the envelope is orchestration.
    rendered = {"turn_id", "packet_sha256", "guardrail", "board",
                "disclosures"}
    for key in envelope:
        if key in rendered:
            continue
        assert key not in prompt, f"envelope key {key!r} reached the grader"
        assert str(envelope[key]) not in prompt, \
            f"the value of {key!r} reached the grader"
    assert "run_seed" not in prompt
    assert envelope["run_seed"] not in prompt


def test_the_template_body_is_read_between_the_rules():
    body = seat.template_body()
    assert body.startswith("You are playing one turn of a card battle")
    assert "For the orchestrator" not in body
    with pytest.raises(seat.SeatError):
        seat.template_body("no rules here\n")


def test_the_form_schema_names_every_field_the_form_needs():
    schema = seat.form_schema()
    for field in ("turn_id", "packet_sha256", "grader", "chosen_line",
                  "q1_what_did_you_play", "q2_other_line_considered",
                  "q3_what_it_gave_up", "q4_different_intent", "q4_changed"):
        assert field in schema["properties"]
        assert field in schema["required"]
    assert schema["additionalProperties"] is False
    grader = schema["properties"]["grader"]["properties"]
    assert set(grader) == {"id", "kind", "model", "designed_these_cards"}
    play = schema["properties"]["chosen_line"]["items"]
    # `target` is nullable-and-required rather than optional: a strict schema
    # wants every property listed in `required`, and a null target reads as
    # "this card needed none", which is what an omitted one meant.
    assert play["properties"]["target"]["type"] == ["string", "null"]
    # EB-170's two optional-and-nullable keys join it on the same rule.
    assert play["properties"]["exhaust"]["type"] == ["string", "null"]
    assert play["properties"]["choose"]["type"] == ["string", "null"]
    assert play["required"] == ["card", "target", "exhaust", "choose"]


# --------------------------------------------------------- the dry run -----

GUARD_FLAGS = ("--skip-git-repo-check", "--sandbox", "read-only",
               "--ignore-user-config", "--ignore-rules", "--json",
               "--color", "never", "--output-schema", "-o", "-C", "-m")


def test_the_dry_run_prints_every_guard_flag(tmp_path, capsys):
    rc = seat.main(["grade", "kokomi-first-turn-example", "--dry-run",
                    "--log-root", str(tmp_path)])
    assert rc == 0
    printed = capsys.readouterr().out
    for flag in GUARD_FLAGS:
        assert flag in printed, f"the dry run does not show {flag}"
    assert "--ephemeral" not in printed, \
        "--ephemeral would suppress the rollout the guard reads"

    sessions = sorted(tmp_path.iterdir())
    assert len(sessions) == 1
    session = sessions[0]
    assert (session / "prompt.md").is_file()
    assert (session / "form-schema.json").is_file()
    # Nothing ran, so there is no transcript and no reply.
    assert not (session / "events.jsonl").exists()
    assert not (session / "form-raw.json").exists()
    assert not (session / "rollout.jsonl").exists()

    blob = json.loads((session / "seat.json").read_text(encoding="utf-8"))
    assert blob["dry_run"] is True
    assert blob["prompt_sha256"] == seat.sha256(
        (session / "prompt.md").read_text(encoding="utf-8"))
    assert blob["model_requested"] == seat.DEFAULT_MODEL
    assert blob["grader_id"] == f"codex-{seat.DEFAULT_MODEL}-fresh"

    # THE SCRATCH ROOT'S TWO PROPERTIES: empty, and outside the repo. Codex
    # reads AGENTS.md from its working root, and this repo has one.
    scratch = Path(blob["scratch_cwd"])
    assert scratch.is_dir()
    assert list(scratch.iterdir()) == []
    assert not seat.is_inside_repo(scratch)
    seat._drop_scratch(scratch)


def test_the_argv_pins_the_scratch_root_and_the_model(tmp_path):
    argv = seat.grade_argv("codex", tmp_path / "session", tmp_path / "scratch",
                           model="gpt-5.6-sol")
    assert argv[:2] == ["codex", "exec"]
    assert argv[argv.index("-C") + 1] == str(tmp_path / "scratch")
    assert argv[argv.index("-m") + 1] == "gpt-5.6-sol"
    assert argv[-1] == "-", "the prompt goes on stdin, never on the argv"
    assert "resume" not in argv, "a blind grader never continues a session"
    # `-m` is not optional here: the ledger's grader id has to name a model,
    # not "whatever codex defaulted to that month".
    assert "-m" in seat.grade_argv("codex", tmp_path, tmp_path)


def test_the_scratch_root_is_outside_the_repo():
    scratch = seat.scratch_root()
    try:
        assert scratch.is_dir()
        assert list(scratch.iterdir()) == []
        assert not seat.is_inside_repo(scratch)
    finally:
        seat._drop_scratch(scratch)
    assert seat.is_inside_repo(REPO / "understudy" / "logs")


def test_a_non_empty_scratch_root_refuses_the_seat(tmp_path, capsys):
    """The seat is supposed to be looking at nothing. A scratch directory
    with a file in it is a seat that had something to read, and that is a
    refusal before codex is ever launched."""
    session = tmp_path / "session"
    session.mkdir()
    rc = seat._refuse({"turn_id": "t"}, session, "cwd_not_empty",
                      ["AGENTS.md"])
    assert rc == 1
    blob = json.loads((session / "seat.json").read_text(encoding="utf-8"))
    assert blob["refused"] == "cwd_not_empty"
    assert blob["refused_detail"] == ["AGENTS.md"]
    assert "cwd_not_empty" in capsys.readouterr().err


def test_the_review_seat_is_not_blind_and_says_so(tmp_path):
    """Two roles, two argvs. The reviewer reads the repo on purpose, so it
    gets no `--skip-git-repo-check`, no `--output-schema`, and no `--json`
    transcript for a guard to read -- and its output may never be filed as a
    grade."""
    argv = seat.review_argv("codex", tmp_path / "out.md")
    assert argv[argv.index("-C") + 1] == str(seat.REPO)
    assert "--sandbox" in argv and "read-only" in argv
    assert "--json" not in argv
    assert "--output-schema" not in argv
    assert "--skip-git-repo-check" not in argv
    # ...and `--ephemeral` IS fine here: there is no blindness to prove.
    assert "--ephemeral" in argv


def test_the_review_dry_run_runs_nothing(tmp_path, capsys):
    prompt = tmp_path / "ask.md"
    prompt.write_text("Read understudy/seat.py and find the guard.\n",
                      encoding="utf-8")
    out = tmp_path / "answer.md"
    assert seat.main(["review", str(prompt), "--out", str(out),
                      "--dry-run"]) == 0
    printed = capsys.readouterr().out
    assert "DRY RUN" in printed and str(out) in printed
    assert not out.exists()


def test_the_refusal_reasons_are_all_explained():
    """A reason string printed to a human with no sentence beside it is a
    reason nobody can act on six months later."""
    for reason in ("cwd_not_empty", "cwd_inside_repo", "codex_failed",
                   "codex_error", "codex_timeout", "seat_no_transcript",
                   "seat_saw_instructions", "seat_used_tools", "no_form",
                   "turn_mismatch",
                   "packet_mismatch"):
        assert seat.REFUSAL_REASONS[reason].strip()


# ------------------------------- EB-169: the preflight, belt and braces ----
#
# `staged_turn check`/`stage` refuse a BOARD holding a card with an open
# face/runtime defect. A packet on disk outlives the command that wrote it, so
# the seat checks the packet's own printed hand before it spends a third
# party's quota reading a face the repo knows is wrong.

FIXTURE_REGISTER = {
    "all_streams_flow": {
        "eb": "EB-164",
        "titles": ("All Streams Flow to the Sea",),
        "defect": "the printed damage already folds Charge in and a second "
                  "sentence claims the fold again, so a reader adds it twice",
    },
}


def test_the_seat_refuses_a_packet_holding_a_registered_face(tmp_path,
                                                             monkeypatch,
                                                             capsys):
    """The worked example's hand really does hold `All Streams Flow to the
    Sea`, so this refusal runs against a REAL packet on disk under a fixture
    register -- which is exactly the situation round 2 of the Kokomi slice
    graded eleven times without noticing."""
    from understudy import face_defects

    monkeypatch.setattr(face_defects, "OPEN_FACE_DEFECTS", FIXTURE_REGISTER)
    rc = seat.main(["grade", "kokomi-first-turn-example", "--dry-run",
                    "--log-root", str(tmp_path)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "open_face_defect" in err and "EB-164" in err
    blob = json.loads(
        next(tmp_path.rglob("seat.json")).read_text(encoding="utf-8"))
    assert blob["refused"] == "open_face_defect"
    assert blob["open_face_defects"][0]["eb"] == "EB-164"


def test_the_refusal_lands_before_anything_is_executed(tmp_path, monkeypatch):
    """It refuses even the DRY RUN, which is the ordering claim: the check is
    ahead of `codex_path`, the scratch dance and the argv, so no part of the
    seat is set up for a packet that will not be graded."""
    from understudy import face_defects

    monkeypatch.setattr(face_defects, "OPEN_FACE_DEFECTS", FIXTURE_REGISTER)
    assert seat.main(["grade", "kokomi-first-turn-example", "--dry-run",
                      "--log-root", str(tmp_path)]) == 1
    blob = json.loads(
        next(tmp_path.rglob("seat.json")).read_text(encoding="utf-8"))
    assert "dry_run" not in blob and "codex_version" in blob


def test_the_shipped_register_lets_the_example_through(tmp_path):
    """The same packet, the same command, the EMPTY shipped register: the dry
    run proceeds. Proof the red above is the register's doing."""
    assert seat.main(["grade", "kokomi-first-turn-example", "--dry-run",
                      "--log-root", str(tmp_path)]) == 0


def test_open_face_defect_is_a_named_seat_refusal():
    assert "open_face_defect" in seat.REFUSAL_REASONS
    assert "OPEN defect" in seat.REFUSAL_REASONS["open_face_defect"]
