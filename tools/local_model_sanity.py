#!/usr/bin/env python3
"""Is the local model any use as a playtester? Ask it CLOSED work and compare.

THE EXPERIMENT, AND WHY IT IS SHAPED THIS WAY. A 27B model on one desktop GPU
is not a hosted frontier model, and the honest question is not "is it as good"
-- it is "is it good enough to be worth reading while a quota is out". That
question has an answer only against work whose right reading is already
recorded, so this harness runs the local seat on turns that are CLOSED, each
with an `opus-5-fresh` and a `codex-gpt-5.6-sol-fresh` verdict already beside
it, and reports the three side by side.

WHAT IT NEVER DOES. It never writes inside a closed turn's directory. A
published measurement record stands as published (R101b), and a third form
landing beside two graded ones months later would read as a third grade rather
than as an experiment about the reader. Everything -- the form, the verdict,
the report -- lands under `review/qa/local-sanity-<date>/`, and the report says
in its first paragraph what it is not.

WHAT AGREEMENT MEANS HERE, AND WHAT IT DOES NOT
------------------------------------------------
Three readings are compared on three axes, weakest claim first:

  * **The VERDICT** (`SURVIVES` / `REFUSED`). Cheapest to match and least
    informative: the falsifiers refuse a form for shape (no second line, a
    fourth answer of "no"), so a model that writes a well-formed nothing
    matches every SURVIVES in the set.
  * **The LINE.** The ordered card titles it played. This is the reading.
  * **The MISREAD CLASSES.** Klee slice 1 round 1's failure was not a bad
    line; it was a reader who thought the wrong Attack was free and reasoned
    correctly from there. `understudy/misreads.py` looks for exactly that
    shape -- a claim that a card is free, checked against the cost the packet
    PRINTS -- and for the arithmetic one the Codex seat caught on this very
    read, a prevention claim quoting the residual instead. Both live down
    there rather than here because the LIVE tester path
    (`understudy/local_tester.py`) runs the same two checks, and two copies
    would drift. A grader that misreads the board produces confident,
    plausible, useless feedback, and that is the specific failure a weaker
    model is most likely to reproduce.

None of the three is evidence about the GAME. Agreement says something about
the READER; a local model agreeing with two hosted ones on eight closed turns
means it is worth reading next time, and nothing more.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Iterable, Sequence

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from understudy import (local_model, local_seat, misreads as _misreads,  # noqa: E402
                        seat, staged_turn)

# RE-EXPORTED, not re-implemented (see `understudy/misreads.py`): the live
# tester path runs the same two checks, and two copies would drift the day
# one of them grew a third class.
FREE_CLAIMS = _misreads.FREE_CLAIMS
CLAIM_WINDOW = _misreads.CLAIM_WINDOW
printed_costs = _misreads.printed_costs
free_card_misreads = _misreads.free_card_misreads
intent_damages = _misreads.intent_damages
block_prevention_misreads = _misreads.block_prevention_misreads
misreads = _misreads.misreads

QA_DIR = REPO / "review" / "qa"

# The two rounds the brief names. A pattern that matches nothing is REPORTED
# rather than silently dropped -- `klee-slice1-r3-*` lives in the operator's
# main checkout and is not committed, so on a fresh clone it legitimately
# matches nothing and the operator needs to be told that rather than left to
# wonder why the run was short.
DEFAULT_PATTERNS: tuple[str, ...] = ("klee-slice1-r3-t*", "kokomi-slice2-t*")

# The two recorded readings a turn must carry to be comparable. Matched as
# GLOBS on the verdict filename because the grader id carries the model
# version (`codex-gpt-5.6-sol-fresh`) and pinning the version here would make
# this file stale the next time the seat's model moves.
RECORDED: dict[str, str] = {
    "claude": "verdict-*opus*.json",
    "gpt": "verdict-*codex*.json",
}

# The doctrine prompt to re-run under `--doctrine`, first that exists. The
# kokomi one is the brief's first choice and is NOT committed (it inlines a
# proposal); the klee one is, so a fresh clone still has something to run.
DOCTRINE_PROMPTS: tuple[str, ...] = (
    "kokomi-kurage-memory-doctrine-review-prompt.txt",
    "kokomi-kurage-memory-review-prompt.txt",
    "klee-sparks-doctrine-review-prompt.txt",
)
DOCTRINE_RECORDED = "*doctrine-review-codex-*.md"

REPORT_GUARDRAIL = (
    "WHAT THIS IS. A local model re-read turns that are already CLOSED, and "
    "its reading is printed beside the two that are recorded. It is "
    "SUBJECTIVE FEEDBACK about the READER.\n\n"
    "WHAT THIS IS NOT. Not human validation. Not balance evidence. Not a "
    "grade: nothing here enters a record, a register or the ledger, and the "
    "`local` family is not an approved doctrine seat. Agreement with a "
    "recorded reading says the local model was worth reading on these turns; "
    "it says nothing about whether any turn is fun."
)


# ------------------------------------------------------------ discovery ----

def has_recorded(turn_dir: Path) -> dict[str, Path]:
    """`{family: verdict path}` for the recorded readings this turn carries."""
    found: dict[str, Path] = {}
    for family, pattern in RECORDED.items():
        hits = sorted(turn_dir.glob(pattern))
        if hits:
            found[family] = hits[0]
    return found


def discover(qa_dir: Path | None = None,
             patterns: Sequence[str] = DEFAULT_PATTERNS,
             *, any_closed: bool = False) -> tuple[list[str], list[str]]:
    """`(turn ids, notes)` -- every closed turn with BOTH recorded readings.

    A turn missing one of the two is skipped rather than compared against one:
    the whole design is a three-way read, and a two-way one would quietly
    change what an "agreement rate" means halfway down the table.
    """
    d = qa_dir or QA_DIR
    notes: list[str] = []
    if not d.is_dir():
        return [], [f"no {d}"]
    candidates = sorted(p for p in d.iterdir() if p.is_dir())

    def matches(name: str) -> bool:
        return any(fnmatch.fnmatch(name, pat) for pat in patterns)

    chosen = [p for p in candidates if (any_closed or matches(p.name))
              and len(has_recorded(p)) == len(RECORDED)]
    if not any_closed:
        for pat in patterns:
            if not any(fnmatch.fnmatch(p.name, pat) for p in candidates):
                notes.append(f"pattern {pat!r} matched no directory under "
                             f"{d} (it may live only in the operator's main "
                             f"checkout and not in git)")
    skipped = [p.name for p in candidates
               if (any_closed or matches(p.name))
               and 0 < len(has_recorded(p)) < len(RECORDED)]
    if skipped:
        notes.append(f"skipped (only one recorded reading): "
                     f"{', '.join(skipped)}")
    return [p.name for p in chosen], notes


# ---------------------------------------------------------- the readings ---

def line_titles(chosen_line: Iterable[Any]) -> list[str]:
    out: list[str] = []
    for play in chosen_line or []:
        if isinstance(play, dict) and play.get("card"):
            out.append(str(play["card"]))
    return out


def reading(verdict_path: Path) -> dict[str, Any]:
    """One recorded verdict, reduced to the fields the comparison uses."""
    blob = json.loads(verdict_path.read_text(encoding="utf-8"))
    return {
        "grader": str((blob.get("grader") or {}).get("id") or "?"),
        "model": str((blob.get("grader") or {}).get("model") or "?"),
        "verdict": str(blob.get("verdict") or "?"),
        "refused_by": list(blob.get("refused_by") or []),
        "line": line_titles(blob.get("chosen_line")),
        "answers": dict(blob.get("answers") or {}),
        "path": str(verdict_path),
    }


def prose_of(form: dict[str, Any]) -> str:
    return _misreads.prose_of(form, staged_turn.QUESTIONS)


# ------------------------------------------------------------- the run -----

def out_root(qa_dir: Path | None = None, stamp: str = "") -> Path:
    return ((qa_dir or QA_DIR)
            / f"local-sanity-{stamp or time.strftime('%Y%m%d')}")


def run_turn(turn_id: str, *, client: local_model.Client, out_dir: Path,
             qa_dir: Path | None = None,
             log_root: Path | None = None) -> dict[str, Any]:
    """One turn: local seat, then the three-way comparison row."""
    d = (qa_dir or QA_DIR) / turn_id
    land = out_dir / turn_id
    land.mkdir(parents=True, exist_ok=True)

    row: dict[str, Any] = {"turn_id": turn_id, "recorded": {}}
    for family, path in has_recorded(d).items():
        row["recorded"][family] = reading(path)

    blob = local_seat.grade_turn(turn_id, client=client, qa_dir=qa_dir,
                                 land_dir=land, log_root=log_root)
    row["seat"] = {k: blob.get(k) for k in (
        "grader_id", "model_requested", "model_observed", "temperature",
        "refused", "refused_why", "wall_s", "prompt_tokens",
        "completion_tokens", "estimated_prompt_tokens", "session")}

    if blob.get("refused"):
        row["local"] = None
        row["misreads"] = []
        return row

    form = staged_turn.load_form(blob["form"])
    verdict = staged_turn.grade(turn_id, form, root=qa_dir or QA_DIR)
    (land / f"verdict-{blob['grader_id']}.json").write_text(
        json.dumps(verdict, indent=1) + "\n", encoding="utf-8")

    row["local"] = {
        "grader": blob["grader_id"],
        "model": str((form.get("grader") or {}).get("model") or "?"),
        "verdict": verdict["verdict"],
        "refused_by": verdict["refused_by"],
        "line": line_titles(form.get("chosen_line")),
        "answers": {q: str(form.get(q) or "") for q in staged_turn.QUESTIONS},
    }
    packet_md = (d / "packet.md").read_text(encoding="utf-8")
    row["misreads"] = misreads(packet_md, prose_of(form))
    # ...and the same check on the RECORDED readings, so the report can say
    # whether the misread class is the local model's or the turn's.
    row["recorded_misreads"] = {
        fam: free_card_misreads(packet_md,
                                "\n".join(read["answers"].values()))
        for fam, read in row["recorded"].items()}
    return row


# ----------------------------------------------------------- the report ----

def _agree(a: dict[str, Any] | None, b: dict[str, Any] | None,
           key: str) -> str:
    if not a or not b:
        return "n/a"
    return "agree" if a.get(key) == b.get(key) else "disagree"


def summarise(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "turns": len(rows),
        "refused_seat": sum(1 for r in rows if r["seat"].get("refused")),
        "graded": sum(1 for r in rows if r.get("local")),
        "misread_turns": sum(1 for r in rows if r.get("misreads")),
        "wall_s": round(sum(float(r["seat"].get("wall_s") or 0)
                            for r in rows), 1),
        "completion_tokens": sum(int(r["seat"].get("completion_tokens") or 0)
                                 for r in rows),
        "prompt_tokens": sum(int(r["seat"].get("prompt_tokens") or 0)
                             for r in rows),
    }
    for family in RECORDED:
        pairs = [(r["local"], r["recorded"].get(family)) for r in rows
                 if r.get("local") and r["recorded"].get(family)]
        out[f"verdict_agree_{family}"] = sum(
            1 for a, b in pairs if a["verdict"] == b["verdict"])
        out[f"line_agree_{family}"] = sum(
            1 for a, b in pairs if a["line"] == b["line"])
        out[f"comparable_{family}"] = len(pairs)
    return out


def _rate(n: int, d: int) -> str:
    return f"{n}/{d}" + (f" ({n / d:.0%})" if d else "")


def report(rows: Sequence[dict[str, Any]], notes: Sequence[str],
           *, client: local_model.Client, stamp: str) -> str:
    s = summarise(rows)
    out: list[str] = []
    out.append(f"# Local model sanity read -- {stamp}\n")
    out.append(REPORT_GUARDRAIL + "\n")
    out.append(f"- endpoint: `{client.base_url}`, ctx {client.ctx}, "
               f"temperature {local_seat.GRADE_TEMPERATURE} (greedy)")
    models = {r["seat"].get("model_observed") or r["seat"].get(
        "model_requested") for r in rows}
    out.append(f"- model requested / served: "
               f"{', '.join(sorted(m for m in models if m)) or '(none)'}")
    graders = {r["seat"].get("grader_id") for r in rows}
    out.append(f"- grader id: {', '.join(sorted(g for g in graders if g))}")
    out.append(f"- turns: {s['turns']}, graded {s['graded']}, seat refused "
               f"{s['refused_seat']}")
    out.append(f"- wall: {s['wall_s']}s total, "
               f"{s['completion_tokens']} completion token(s), "
               f"{s['prompt_tokens']} prompt token(s)")
    for note in notes:
        out.append(f"- note: {note}")
    out.append("")

    out.append("## Summary\n")
    out.append("| against | verdict agrees | line agrees | comparable |")
    out.append("| --- | --- | --- | --- |")
    for family in RECORDED:
        d = s[f"comparable_{family}"]
        out.append(f"| {family} | {_rate(s[f'verdict_agree_{family}'], d)} "
                   f"| {_rate(s[f'line_agree_{family}'], d)} | {d} |")
    out.append("")
    out.append(f"Turns where the local reading made a round-1-class "
               f"\"which card is free\" misread: "
               f"{_rate(s['misread_turns'], s['graded'])}.")
    out.append("")

    out.append("## Per turn\n")
    out.append("| turn | local | opus | codex | v. opus | v. codex | "
               "line = opus | line = codex | misread | wall s | out tok |")
    out.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | "
               "--- | --- |")
    for r in rows:
        loc = r.get("local")
        cl = r["recorded"].get("claude")
        gp = r["recorded"].get("gpt")
        local_cell = (loc["verdict"] if loc
                      else f"REFUSED-SEAT ({r['seat'].get('refused')})")
        out.append(
            f"| {r['turn_id']} | {local_cell} "
            f"| {cl['verdict'] if cl else '-'} "
            f"| {gp['verdict'] if gp else '-'} "
            f"| {_agree(loc, cl, 'verdict')} | {_agree(loc, gp, 'verdict')} "
            f"| {_agree(loc, cl, 'line')} | {_agree(loc, gp, 'line')} "
            f"| {len(r.get('misreads') or []) or '-'} "
            f"| {r['seat'].get('wall_s') or '-'} "
            f"| {r['seat'].get('completion_tokens') or '-'} |")
    out.append("")

    out.append("## The lines, in full\n")
    for r in rows:
        out.append(f"### {r['turn_id']}\n")
        loc = r.get("local")
        if loc:
            out.append(f"- local (`{loc['grader']}`): "
                       f"{' -> '.join(loc['line']) or '(empty)'}")
        else:
            out.append(f"- local: SEAT REFUSED `{r['seat'].get('refused')}` "
                       f"-- {r['seat'].get('refused_why')}")
        for family in RECORDED:
            rec = r["recorded"].get(family)
            if rec:
                out.append(f"- {family} (`{rec['grader']}`): "
                           f"{' -> '.join(rec['line']) or '(empty)'}")
        if loc:
            q1 = loc["answers"].get("q1_what_did_you_play", "")
            out.append(f"- local's stated line: {q1.strip() or '(blank)'}")
        for line in r.get("misreads") or []:
            out.append(f"- MISREAD (local): {line}")
        for family, hits in (r.get("recorded_misreads") or {}).items():
            for line in hits:
                out.append(f"- MISREAD ({family}): {line}")
        out.append("")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------- the dry run ----

def dry_run(turn_ids: Sequence[str], notes: Sequence[str], *,
            client: local_model.Client | None,
            qa_dir: Path | None = None,
            doctrine: bool = False) -> str:
    """What WOULD run, and how many tokens each call is estimated to cost.

    Runs with no endpoint on purpose: the first question about a local model
    is whether the prompts fit its context window at all, and that is
    answerable from the files.
    """
    d = qa_dir or QA_DIR
    ctx = client.ctx if client else local_model.DEFAULT_CTX
    lines: list[str] = []
    lines.append(f"PLAN -- nothing is sent. ctx {ctx}, "
                 f"{local_seat.form_max_tokens()} tokens reserved per answer.")
    if client:
        lines.append(f"endpoint: {client.base_url} "
                     f"(model {client.model or 'read from /v1/models'})")
    else:
        lines.append(f"endpoint: UNSET (${local_model.ENV_URL})")
    for note in notes:
        lines.append(f"note: {note}")
    total = 0
    for turn_id in turn_ids:
        packet = d / turn_id / "packet.md"
        if not packet.is_file():
            lines.append(f"  {turn_id:28s} NO PACKET")
            continue
        prompt = local_seat.build_grade_prompt(
            packet.read_text(encoding="utf-8"), "0" * 64)
        est = local_model.estimate_tokens(prompt)
        total += est
        fits = ("fits" if est + local_seat.form_max_tokens() <= ctx
                else "DOES NOT FIT")
        lines.append(f"  {turn_id:28s} ~{est:6d} prompt tok  {fits}")
    lines.append(f"{len(turn_ids)} turn(s), ~{total} prompt token(s) total, "
                 f"one call each, SERIAL (the server runs --parallel 1).")

    if doctrine:
        prompt_path = doctrine_prompt(d)
        if prompt_path is None:
            lines.append("doctrine: no prompt file found; nothing to run")
        else:
            body = prompt_path.read_text(encoding="utf-8")
            est = local_model.estimate_tokens(seat.build_review_prompt(body))
            fits = ("fits" if est + local_seat.review_max_tokens() <= ctx
                    else "DOES NOT FIT")
            lines.append(f"doctrine: {prompt_path.name} ~{est} prompt tok  "
                         f"{fits}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------- the doctrine ---

def doctrine_prompt(qa_dir: Path | None = None) -> Path | None:
    d = qa_dir or QA_DIR
    for name in DOCTRINE_PROMPTS:
        path = d / name
        if path.is_file():
            return path
    return None


def run_doctrine(*, client: local_model.Client, out_dir: Path,
                 qa_dir: Path | None = None) -> str:
    """The seat's doctrine-gate prompt through the local model, diffed.

    `seat.build_review_prompt` is called rather than re-implemented, so the
    local reader is held to the SAME protocol -- FOLLOWS /
    REQUIRES_MODIFICATION and the clause named, no remedy -- as the seat whose
    recorded answer it is being compared against. A different frame would make
    the diff a diff of two questions.
    """
    d = qa_dir or QA_DIR
    prompt_path = doctrine_prompt(d)
    if prompt_path is None:
        raise FileNotFoundError(
            f"no doctrine prompt under {d}; looked for "
            f"{', '.join(DOCTRINE_PROMPTS)}")
    body = prompt_path.read_text(encoding="utf-8")

    asks = seat.remedy_findings(body)
    prompt = seat.build_review_prompt(body)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "doctrine-prompt.md").write_text(prompt, encoding="utf-8")

    reply = client.chat([{"role": "user", "content": prompt}],
                        max_tokens=local_seat.review_max_tokens(),
                        temperature=local_seat.GRADE_TEMPERATURE)
    (out_dir / "doctrine-reply.md").write_text(reply.text, encoding="utf-8")
    if reply.reasoning:
        (out_dir / "doctrine-reasoning.txt").write_text(reply.reasoning,
                                                        encoding="utf-8")

    recorded = sorted(d.glob(DOCTRINE_RECORDED))
    lines: list[str] = []
    lines.append(f"# Local doctrine read -- {prompt_path.name}\n")
    lines.append(REPORT_GUARDRAIL + "\n")
    lines.append(f"- prompt: `{prompt_path}` "
                 f"({local_model.estimate_tokens(prompt)} est. tok)")
    lines.append(f"- model: {reply.model_observed or reply.model_requested}, "
                 f"temperature {reply.temperature}")
    lines.append(f"- wall {reply.wall_s:.1f}s, {reply.completion_tokens} "
                 f"completion token(s)")
    if asks:
        lines.append(f"- NOTE: `seat review` would REFUSE this brief "
                     f"(review_asks_for_a_remedy: {', '.join(asks)}); it was "
                     f"run here anyway because this reading is not a record")
    lines.append("")
    lines.append("## Verdict and clauses, local\n")
    lines.append(_clause_block(reply.text))
    lines.append("\n## Verdict and clauses, recorded GPT read\n")
    if recorded:
        lines.append(f"source: `{recorded[-1].name}`\n")
        lines.append(_clause_block(
            recorded[-1].read_text(encoding="utf-8")))
    else:
        lines.append("(no recorded doctrine review to diff against)")
    lines.append("\n## Diff of the verdict words\n")
    local_words = set(_verdicts_in(reply.text))
    rec_words = set(_verdicts_in(recorded[-1].read_text(encoding="utf-8"))
                    if recorded else [])
    lines.append(f"- local said: {', '.join(sorted(local_words)) or '(none)'}")
    lines.append(f"- recorded said: "
                 f"{', '.join(sorted(rec_words)) or '(none)'}")
    lines.append(f"- same verdict vocabulary: "
                 f"{'yes' if local_words == rec_words else 'NO'}")
    text = "\n".join(lines) + "\n"
    (out_dir / "doctrine-report.md").write_text(text, encoding="utf-8")
    return text


_VERDICT = re.compile(r"\b(FOLLOWS|REQUIRES_MODIFICATION)\b")


def _verdicts_in(text: str) -> list[str]:
    return _VERDICT.findall(str(text or ""))


def _clause_block(text: str) -> str:
    """The lines carrying a verdict word, which is where the clauses are.

    A whole-document diff of two prose reviews is unreadable; the protocol
    says the output is a verdict per arm plus the clause, so those are the
    lines pulled.
    """
    kept = [ln.strip() for ln in str(text or "").splitlines()
            if _VERDICT.search(ln)]
    if not kept:
        return ("(no FOLLOWS / REQUIRES_MODIFICATION line found -- the "
                "reader did not answer in the protocol's shape)")
    return "\n".join(f"- {ln}" for ln in kept[:60])


# ----------------------------------------------------------------- main ----

def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("turns", nargs="*",
                    help="staged-turn ids. Default: every closed turn "
                         f"matching {list(DEFAULT_PATTERNS)} that carries "
                         f"BOTH recorded readings")
    ap.add_argument("--any-closed", action="store_true",
                    help="widen the default to EVERY turn dir with both "
                         "recorded readings")
    ap.add_argument("--doctrine", action="store_true",
                    help="also run the doctrine-gate prompt and diff it "
                         "against the recorded GPT review")
    ap.add_argument("--doctrine-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="list what would run and the estimated prompt "
                         "tokens per call; send nothing, write nothing")
    ap.add_argument("--out", default="",
                    help="output directory. Default "
                         "review/qa/local-sanity-<date>/")
    ap.add_argument("--qa-dir", default="")
    ap.add_argument("--log-root", default="")
    args = ap.parse_args(list(argv) if argv is not None else sys.argv[1:])

    qa_dir = Path(args.qa_dir) if args.qa_dir else QA_DIR
    stamp = time.strftime("%Y%m%d")

    notes: list[str] = []
    if args.turns:
        turn_ids = list(args.turns)
    else:
        turn_ids, notes = discover(qa_dir, any_closed=args.any_closed)
    if args.doctrine_only:
        turn_ids = []

    # The env is read even for a dry run, but its ABSENCE is fatal only for a
    # real one: the whole point of the dry run is answering "will the packets
    # fit" before the endpoint exists.
    client: local_model.Client | None = None
    try:
        client = local_model.Client.from_env()
    except local_model.LocalModelError as exc:
        if not args.dry_run:
            print(f"local model: {exc}", file=sys.stderr)
            print("Nothing was written.", file=sys.stderr)
            return 2
        notes.append(str(exc))

    if args.dry_run:
        print(dry_run(turn_ids, notes, client=client, qa_dir=qa_dir,
                      doctrine=args.doctrine or args.doctrine_only), end="")
        return 0

    assert client is not None
    out_dir = Path(args.out) if args.out else out_root(qa_dir, stamp)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_root = Path(args.log_root) if args.log_root else None

    rows: list[dict[str, Any]] = []
    for turn_id in turn_ids:                        # SERIAL: --parallel 1
        print(f"... {turn_id}", file=sys.stderr)
        rows.append(run_turn(turn_id, client=client, out_dir=out_dir,
                             qa_dir=qa_dir, log_root=log_root))

    if rows:
        text = report(rows, notes, client=client, stamp=stamp)
        (out_dir / "report.md").write_text(text, encoding="utf-8")
        (out_dir / "rows.json").write_text(
            json.dumps(rows, indent=1) + "\n", encoding="utf-8")
        print(text)
        print(f"report: {out_dir / 'report.md'}")

    if args.doctrine or args.doctrine_only:
        print(run_doctrine(client=client, out_dir=out_dir, qa_dir=qa_dir))
        print(f"doctrine: {out_dir / 'doctrine-report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
