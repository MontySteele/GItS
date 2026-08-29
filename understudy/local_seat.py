"""The LOCAL seat: the same blind-QA prompt, run through a model on this box.

`understudy/seat.py` is the independent seat and this is not a replacement for
it. It is a THIRD chair with a much weaker occupant and a much weaker claim:

  * it runs the SAME prompt (`understudy/qa_grader_prompt.md`, through
    `seat.build_prompt`) against the SAME `packet.md`, and
  * it writes the SAME artifacts -- `form-local-<slug>.json` beside the turn,
    handed to `staged_turn grade`, which writes `verdict-local-<slug>.json` --
  * so that a reading can be COMPARED with the two recorded ones, and for
    nothing else.

WHAT IT IS NOT, WRITTEN HERE BECAUSE A FILE OUTLIVES A CONVERSATION.
A `local` grade is subjective feedback. It is not human validation, it is not
balance evidence, and the `local` family is not an approved doctrine seat --
`seat review`'s chair is still GPT's. Nothing this module produces enters a
record, a register or a ledger row that a decision rests on.

THE BLINDNESS CLAIM IS DIFFERENT, AND WEAKER, AND SAID SO
----------------------------------------------------------
`seat.py` proves blindness from a TRANSCRIPT: three allowlisted sources, and a
missing rollout refuses. There is no transcript here to prove anything from --
this is one HTTP request to a chat endpoint. What it has instead is that the
request is the WHOLE input: the prompt is built and posted, there are no
tools, no filesystem, no repo root and no `AGENTS.md`, because the protocol
has no way to offer any of them. That is a STRUCTURAL argument rather than an
evidentiary one, and `seat.json`'s `blindness` field says exactly that in
words so a later reader cannot mistake it for the codex seat's guard.

WHAT IT DOES KEEP FROM THE REAL SEAT. All three of the refusals that are about
whether the packet may be read at all, in the same order and before any token
is spent: `seat_authored_row` (EB-190), `open_face_defect` (EB-169), and the
turn/packet hash checks that catch a form answered against another board. A
weaker grader is a reason for MORE of those doors, not fewer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Sequence

from understudy import local_model, seat

REPO = Path(__file__).resolve().parents[1]
QA_DIR = REPO / "review" / "qa"
LOG_ROOT = Path(__file__).resolve().parent / "logs" / "local-seat"

# A form is a few hundred tokens of JSON; a reasoning model asked for one can
# spend thousands getting there. Generous, and it is a CEILING rather than a
# target -- `finish_reason: "length"` is recorded and refuses the form.
FORM_MAX_TOKENS = 8192
REVIEW_MAX_TOKENS = 8192

# Grading is not agentic work. Greedy, and written into every artifact.
GRADE_TEMPERATURE = 0.0

# The model is asked for JSON in the prompt, but a local model returns it
# wrapped in prose or a fence often enough that a wrapper which could not
# recover would report "no_form" for answers that are right there.
_FENCE = re.compile(r"```(?:json)?\s*(.+?)\s*```", re.DOTALL)


class LocalSeatError(RuntimeError):
    """The local seat could not be set up."""


# The schema cannot be ENFORCED here -- llama-server's grammar support is a
# different flag on a different route, and a wrapper that silently used a
# different constraint from the codex seat's would make the two forms
# incomparable, which is the one thing this tool exists to do. So the schema
# is APPENDED to the prompt as an instruction and the reply is validated after
# the fact by `staged_turn.load_form`, exactly as a hand-written form is.
SCHEMA_INSTRUCTION = """

--------------------------------------------------------------------------
OUTPUT FORMAT. Answer with ONE JSON object and nothing else -- no prose
before it, no prose after it, no markdown fence. It must match this schema
exactly, including every required key:

{schema}
"""


def build_grade_prompt(packet_md: str, packet_sha: str) -> str:
    """The codex seat's prompt, plus the schema codex gets as a flag.

    `seat.build_prompt` is called rather than re-implemented, so the two seats
    provably answer the same question: if the template moves, both move.
    """
    body = seat.build_prompt(packet_md, packet_sha)
    schema = json.dumps(seat.form_schema(), indent=1)
    return body + SCHEMA_INSTRUCTION.format(schema=schema)


def extract_json(text: str) -> dict[str, Any]:
    """The one JSON object in a reply, fence or no fence.

    Three attempts, narrowest first: the whole reply, a fenced block, then the
    outermost brace pair. Anything looser would start reading JSON out of a
    model's reasoning about JSON.
    """
    raw = str(text or "").strip()
    for candidate in _json_candidates(raw):
        try:
            blob = json.loads(candidate)
        except ValueError:                                    # noqa: PERF203
            continue
        if isinstance(blob, dict):
            return blob
    raise ValueError("the reply carries no JSON object")


def _json_candidates(raw: str) -> list[str]:
    out = [raw]
    fenced = _FENCE.search(raw)
    if fenced:
        out.append(fenced.group(1))
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end > start:
        out.append(raw[start:end + 1])
    return out


# --------------------------------------------------------------- the verb --

def grade_turn(turn_id: str, *, client: local_model.Client,
               grader_id: str = "", qa_dir: Path | None = None,
               land_dir: Path | None = None,
               log_root: Path | None = None,
               dry_run: bool = False) -> dict[str, Any]:
    """Run the local seat on one staged turn. Returns the `seat.json` blob.

    Raises `LocalSeatError` for a setup fault and returns a blob with a
    non-empty `refused` for a run that finished and disqualified itself --
    the same distinction `seat.py` draws, for the same reason.

    `land_dir` SPLITS READ FROM WRITE, and it is the reason the sanity
    harness is safe to point at closed work. The packet is always read from
    the turn's own directory; the form lands wherever `land_dir` says, which
    for a re-read of a CLOSED turn is a fresh
    `review/qa/local-sanity-<date>/<turn>/` and never the closed directory. A
    published record stands as published (R101b), and a third form appearing
    beside two graded ones months later would read as a third grade.
    """
    d = (qa_dir or QA_DIR) / turn_id
    packet_md_path = d / "packet.md"
    if not packet_md_path.is_file():
        raise LocalSeatError(f"no packet at {packet_md_path}")
    packet_md = packet_md_path.read_text(encoding="utf-8")
    envelope: dict[str, Any] = {}
    packet_json_path = d / "packet.json"
    if packet_json_path.is_file():
        envelope = json.loads(packet_json_path.read_text(encoding="utf-8"))
    packet_sha = str(envelope.get("packet_sha256") or seat.sha256(packet_md))

    model = client.model or (client.resolve_model() if not dry_run
                             else "(unresolved)")
    gid = grader_id or local_model.grader_id(model)
    prompt = build_grade_prompt(packet_md, packet_sha)
    estimate = local_model.estimate_tokens(prompt)

    session = (log_root or LOG_ROOT) / (
        f"{turn_id}-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}")
    session.mkdir(parents=True, exist_ok=True)
    (session / "prompt.md").write_text(prompt, encoding="utf-8")

    blob: dict[str, Any] = {
        "turn_id": turn_id,
        "grader_id": gid,
        "seat": "local",
        "session": str(session),
        "url": client.base_url,
        "model_requested": model,
        "model_observed": "",
        "temperature": GRADE_TEMPERATURE,
        "max_tokens": FORM_MAX_TOKENS,
        "ctx": client.ctx,
        "prompt_sha256": seat.sha256(prompt),
        "prompt_chars": len(prompt),
        "estimated_prompt_tokens": estimate,
        "packet_sha256": packet_sha,
        "timeout_s": client.timeout_s,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "blindness": ("STRUCTURAL, not evidentiary: this seat is one HTTP "
                      "chat request with no tools, no filesystem and no repo "
                      "root, so there is nothing it could have read -- but "
                      "unlike the codex seat there is no transcript here "
                      "PROVING it, and this reading is never a substitute "
                      "for that one"),
        "guardrail": ("a local model's answer is SUBJECTIVE FEEDBACK for "
                      "comparison against recorded readings. It is not human "
                      "validation, not balance evidence, and the local "
                      "family is not an approved doctrine seat; nothing it "
                      "produces enters a record"),
        "refused": "",
    }

    # EB-190 and EB-169, in `seat.py`'s order and before a token is spent.
    from understudy import authorship, face_defects

    proto_rows = authorship.rows_in_turn(turn_id)
    blob["prototype_rows"] = proto_rows
    hits = authorship.conflicts(model, proto_rows)
    if hits:
        return _refuse(blob, session, "seat_authored_row", hits)

    hand_titles = [str(c.get("title") or c.get("name") or "")
                   for c in ((envelope.get("board") or {}).get("hand") or [])]
    defects = face_defects.hits(hand_titles)
    if defects:
        return _refuse(blob, session, "open_face_defect",
                       [f"{h['matched']} -- {h['eb']}" for h in defects])

    if client.ctx and estimate + FORM_MAX_TOKENS > client.ctx:
        return _refuse(blob, session, "prompt_exceeds_ctx",
                       [f"~{estimate} + {FORM_MAX_TOKENS} > {client.ctx}"])

    if dry_run:
        blob["dry_run"] = True
        _write(blob, session)
        return blob

    try:
        reply = client.chat([{"role": "user", "content": prompt}],
                            max_tokens=FORM_MAX_TOKENS,
                            temperature=GRADE_TEMPERATURE)
    except local_model.LocalModelError as exc:
        return _refuse(blob, session, "endpoint_error", [str(exc)])

    blob.update(reply.as_dict())
    blob["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (session / "reply.txt").write_text(reply.text, encoding="utf-8")
    if reply.reasoning:
        # RECORDED, never parsed. A local reasoning model's scratchpad is the
        # most interesting thing about this experiment and the least
        # admissible.
        (session / "reasoning.txt").write_text(reply.reasoning,
                                               encoding="utf-8")

    if reply.finish_reason == "length":
        return _refuse(blob, session, "answer_truncated",
                       [f"the model hit the {FORM_MAX_TOKENS}-token ceiling "
                        f"mid-answer"])

    try:
        raw = extract_json(reply.text)
    except ValueError as exc:
        return _refuse(blob, session, "no_form", [str(exc)])
    (session / "form-raw.json").write_text(json.dumps(raw, indent=1) + "\n",
                                           encoding="utf-8")

    if str(raw.get("turn_id") or "") != turn_id:
        return _refuse(blob, session, "turn_mismatch",
                       [str(raw.get("turn_id"))])
    if str(raw.get("packet_sha256") or "") != packet_sha:
        return _refuse(blob, session, "packet_mismatch",
                       [str(raw.get("packet_sha256"))])

    # `local:` prefixed on purpose: `authorship.model_family` resolves the
    # family off this string, and the prefix is the only spelling that cannot
    # be mistaken for a vendor's. The served name is kept inside it, so the
    # artifact still names the file that answered.
    observed = reply.model_observed or model
    form = seat.fill_identity(raw, gid, f"local:{observed}")
    form_blob = json.dumps(form, indent=1) + "\n"
    (session / "form.json").write_text(form_blob, encoding="utf-8")
    home = land_dir or d
    home.mkdir(parents=True, exist_ok=True)
    landed = home / f"form-{gid}.json"
    landed.write_text(form_blob, encoding="utf-8")

    blob["model_observed"] = observed
    blob["form"] = str(landed)
    _write(blob, session)
    return blob


def _write(blob: dict[str, Any], session: Path) -> None:
    session.mkdir(parents=True, exist_ok=True)
    (session / "seat.json").write_text(json.dumps(blob, indent=1) + "\n",
                                       encoding="utf-8")


REFUSAL_REASONS = {
    "seat_authored_row": seat.REFUSAL_REASONS["seat_authored_row"],
    "open_face_defect": seat.REFUSAL_REASONS["open_face_defect"],
    "turn_mismatch": seat.REFUSAL_REASONS["turn_mismatch"],
    "packet_mismatch": seat.REFUSAL_REASONS["packet_mismatch"],
    "no_form": "the reply carries no JSON object, so there is no form",
    "endpoint_error": "the local endpoint could not be reached or refused "
                      "the request",
    "prompt_exceeds_ctx": "the prompt does not fit the declared context "
                          "window, and nothing here truncates one",
    "answer_truncated": "the answer stopped at the token ceiling, so the "
                        "form is incomplete and is not a partial grade",
}


def _refuse(blob: dict[str, Any], session: Path, reason: str,
            detail: list[str]) -> dict[str, Any]:
    blob["refused"] = reason
    blob["refused_why"] = REFUSAL_REASONS.get(reason, reason)
    blob["refused_detail"] = detail
    _write(blob, session)
    return blob


# ----------------------------------------------------------------- CLI -----

def cmd_check(args) -> int:
    return local_model.main(["probe"] + (["--no-chat"] if args.no_chat
                                         else []))


def cmd_grade(args) -> int:
    try:
        client = local_model.Client.from_env()
    except local_model.LocalModelError as exc:
        print(f"local seat: {exc}", file=sys.stderr)
        return 2
    if args.model:
        client.model = args.model
    try:
        blob = grade_turn(args.turn_id, client=client,
                          grader_id=args.grader_id,
                          log_root=Path(args.log_root) if args.log_root
                          else None,
                          dry_run=args.dry_run)
    except (LocalSeatError, local_model.LocalModelError) as exc:
        print(f"local seat: {exc}", file=sys.stderr)
        return 2

    if blob["refused"]:
        print(f"LOCAL SEAT REFUSED  {blob['refused']}: "
              f"{blob['refused_why']}", file=sys.stderr)
        for line in blob.get("refused_detail") or []:
            print(f"  {line}", file=sys.stderr)
        print(f"  {Path(blob['session']) / 'seat.json'}", file=sys.stderr)
        return 1
    if args.dry_run:
        print("DRY RUN -- nothing was sent")
        print(f"grader:  {blob['grader_id']}")
        print(f"prompt:  {Path(blob['session']) / 'prompt.md'}")
        print(f"tokens:  ~{blob['estimated_prompt_tokens']} + "
              f"{FORM_MAX_TOKENS} reserved, ctx {blob['ctx']}")
        return 0

    print(f"seat: {blob['session']}")
    print(f"form: {blob['form']}")
    from understudy import staged_turn
    return staged_turn.main(["grade", args.turn_id, str(blob["form"])])


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="is the endpoint up, and what model")
    c.add_argument("--no-chat", action="store_true")
    c.set_defaults(func=cmd_check)

    g = sub.add_parser("grade", help="run the LOCAL seat on a staged turn")
    g.add_argument("turn_id")
    g.add_argument("--model", default="",
                   help=f"overrides ${local_model.ENV_NAME}; default is "
                        f"whatever /v1/models reports")
    g.add_argument("--grader-id", default="",
                   help="default `local-<slug of the model>`, and it must be "
                        "STABLE across turns for the same seat")
    g.add_argument("--dry-run", action="store_true",
                   help="write the prompt, print the token estimate, send "
                        "nothing")
    g.add_argument("--log-root", default="")
    g.set_defaults(func=cmd_grade)

    args = ap.parse_args(list(argv) if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
