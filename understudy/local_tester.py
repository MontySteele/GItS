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
import sys
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from understudy import local_model, local_seat

REPO = Path(__file__).resolve().parents[1]
QA_DIR = REPO / "review" / "qa"

ROLE = "tester"
TESTER_FAMILY = "local"

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
              dry_run: bool = False) -> dict[str, Any]:
    """One staged turn, READ by the local model in the tester role.

    Returns the tester record. `land_dir` splits read from write exactly as
    `local_seat.grade_turn` does, and for the same reason: a re-read of closed
    work lands somewhere else and leaves the closed directory byte-clean
    (R101b).
    """
    blob = local_seat.grade_turn(turn_id, client=client,
                                 grader_id=tester_id, qa_dir=qa_dir,
                                 land_dir=land_dir, log_root=log_root,
                                 dry_run=dry_run)
    record = _record(turn_id, blob, position=position, spot_check=spot_check)

    if blob.get("refused") or dry_run or not blob.get("form"):
        if blob.get("refused"):
            _route(record, "local_read_refused")
        return _land(record, blob, land_dir, qa_dir, turn_id)

    form = json.loads(Path(blob["form"]).read_text(encoding="utf-8"))
    _post_read(record, form, turn_id, qa_dir)
    return _land(record, blob, land_dir, qa_dir, turn_id)


def _record(turn_id: str, blob: Mapping[str, Any], *, position: int,
            spot_check: int) -> dict[str, Any]:
    record: dict[str, Any] = {
        "turn_id": turn_id,
        "role": ROLE,
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


def cmd_round(args) -> int:
    plan = plan_round(args.turn_ids, args.seat_spot_check)
    print(f"round of {len(plan)} turn(s), seat spot-check every "
          f"{args.seat_spot_check or 'never'}")
    for row in plan:
        mark = "SEAT" if row["seat_spot_check"] else "    "
        print(f"  {row['position']:>2}  {mark}  {row['turn_id']}")
    if args.plan_only:
        return 0

    try:
        client = _client(args)
    except local_model.LocalModelError as exc:
        print(f"local tester: {exc}", file=sys.stderr)
        return 2

    records: list[dict[str, Any]] = []
    for row in plan:
        print(f"\n--- {row['turn_id']} ---")
        record = read_turn(row["turn_id"], client=client,
                           position=row["position"],
                           spot_check=args.seat_spot_check,
                           log_root=Path(args.log_root) if args.log_root
                           else None)
        _print(record)
        records.append(record)

    queue = round_queue(records)
    print(f"\nseat review owed on {len(queue)} of {len(records)} turn(s):")
    for row in queue:
        print(f"  {row['turn_id']}  ({', '.join(row['reasons'])})")
        print(f"    {row['command']}")
    return 0


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
    common(q)
    q.set_defaults(func=cmd_round)

    args = ap.parse_args(list(argv) if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
