"""R221, item (4): the round's RESULTS SECTION, written from the records.

[USER], on the funnel's throughput: *"4) yes, agreed"* -- to *generate packet
§11 from the records*. Roughly thirty of the seventy minutes a blind-QA round
costs are agent-bound, and most of that half is transcribing what is already on
disk: which grader read which board, what the verdict was, which falsifier
refused it, whether the replay confirmed the arithmetic, what the seed was.
None of that is judgment. All of it is in `review/qa/<turn>/` and
`review/qa/ledger.tsv` already, and a table typed by hand from those files is a
table that can disagree with them.

So this module reads the records and prints the section. It renders the shape
the packets already use -- `review/active/kokomi-slice-2-2026-08-29.md` §8 is
the reference -- with one deliberate difference: **the prose read is a marked
EMPTY SLOT.** The tables are mechanical and this tool owns them; the paragraph
that says what the round MEANS is the agent's and is never generated. A
generator that wrote that paragraph would be a generator inventing a reading,
which is the one thing in this funnel nobody may do.

WHAT IT WILL NOT DO.

  * It does not grade, re-grade or re-read anything. Every verdict it prints
    was written by `staged_turn.grade`; every replay line was written by
    `staged_turn execute`. R101b: a published record is quoted, never revised.
  * It does not open a form. The four answers are in the ledger already, cell-
    bounded, and a section that re-quoted the raw prose would be a second copy
    of the testimony drifting from the first.
  * It carries the ledger's OWN banners verbatim -- Guardrail-7, the
    down-weighting rule, the UNRUN note -- rather than restating them, for the
    same reason: one wording, one place.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Iterable

from understudy import authorship, staged_turn

REPO = Path(__file__).resolve().parents[1]
QA_DIR = REPO / "review" / "qa"

# The slot the agent fills, and the words that say it is a slot. Printed
# verbatim so a section left unfinished is obvious in review rather than
# plausible.
PROSE_SLOT = (
    "> **[AGENT'S PROSE READ -- NOT GENERATED. Replace this block.]** What the\n"
    "> round means, what it does not settle, which falsifiers stayed silent and\n"
    "> what that is worth, and the pair read's own words. Everything above this\n"
    "> line is transcribed from the records by\n"
    "> `python -m understudy.staged_turn packet-section <round-slug>`; nothing\n"
    "> above it is a judgment and nothing below it is mechanical."
)


def turn_dirs(slug: str, root: Path | None = None) -> list[Path]:
    """`review/qa/<slug>-t*/`, in printed order.

    The `-t` is required rather than a bare prefix: `klee-slice1` and
    `klee-slice1-r2` are two rounds, and a bare-prefix glob would fold the
    second round's boards into the first round's section.
    """
    base = root or QA_DIR
    return sorted(p for p in base.glob(f"{slug}-t*") if p.is_dir())


def _read(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _family(grader_id: str) -> str:
    fam = authorship.model_family(grader_id)
    return fam or "unknown"


def slot_map(directory: Path | None = None) -> dict[str, list[str]]:
    """`turn id -> its registered slots`, read off the TURN FILES.

    The turn file is where a slot is declared (R221 B), so it is where the
    section reads them from. A board whose file has been moved or deleted
    falls back to its own id, which is what an undeclared board carries
    anyway.
    """
    out: dict[str, list[str]] = {}
    for path in staged_turn.all_turns(directory):
        try:
            turn = staged_turn.load(path)
        except Exception:                                     # noqa: BLE001
            continue
        out[turn.id] = turn.registered_slots()
    return out


def board(directory: Path,
          slots: dict[str, list[str]] | None = None) -> dict[str, Any]:
    """One board's whole record, folded into the shape the section prints."""
    tid = directory.name
    packet = _read(directory / "packet.json")
    unrun = _read(directory / "unrun.json")
    closeness = _read(directory / "closeness.json")

    graders: list[dict[str, Any]] = []
    for vpath in sorted(directory.glob("verdict-*.json")):
        verdict = _read(vpath)
        gid = str((verdict.get("grader") or {}).get("id")
                  or vpath.stem[len("verdict-"):])
        replay = _read(directory / f"execute-{gid}.json")
        tester = _read(directory / f"tester-{gid}.json")
        graders.append({
            "grader": gid,
            "family": _family(gid),
            "verdict": str(verdict.get("verdict") or "-"),
            "refused_by": list(verdict.get("refused_by") or []),
            "survives_alone": bool(verdict.get("survives_alone")),
            "replay": _replay_line(replay),
            "flags": _flags(tester),
            "seat_review": list(tester.get("seat_review_reasons") or []),
        })
    return {
        "turn_id": tid,
        "seed": str(packet.get("run_seed") or unrun.get("seed") or "-"),
        "slots": list((slots or {}).get(tid)
                      or unrun.get("slots") or [tid]),
        "unrun": bool(unrun),
        "unrun_why": str(unrun.get("why") or ""),
        "closeness": closeness,
        "graders": graders,
    }


def _replay_line(replay: dict[str, Any]) -> str:
    """One cell for the replay, or `-` where none was recorded."""
    if not replay:
        return "-"
    check = replay.get("board_check") or {}
    if not replay.get("ok"):
        why = "; ".join(str(f) for f in (replay.get("failures") or [])) \
            or "; ".join(str(d) for d in (check.get("differences") or []))
        return f"REFUSED -- {why or 'the replay did not complete'}"
    if not check.get("ok", True):
        return ("board MISMATCH -- "
                + "; ".join(str(d) for d in (check.get("differences") or [])))
    return "confirms -- " + _outcome_cell(replay.get("outcome") or {})


def _outcome_cell(out: dict[str, Any]) -> str:
    """The replay's post-state, in one readable cell.

    Deliberately NOT the whole `outcome` blob. That blob carries the guardrail
    sentence, the diagnostic-reading sentence and every resource on the
    character, and pasted into a table cell it is a wall nobody reads -- which
    is how a generated section stops being read at all. What a reviewer checks
    is the arithmetic: what the enemy's HP did, what Block did, and which
    meters MOVED. Everything else is in the record, one file away.
    """
    bits: list[str] = []
    for e in out.get("enemies") or []:
        bits.append(f"{e.get('name', '?')} {e.get('hp_before')} -> "
                    f"{e.get('hp_after')}")
    player = out.get("player") or {}
    before, after = player.get("before") or {}, player.get("after") or {}
    if before.get("hp") != after.get("hp"):
        bits.append(f"HP {before.get('hp')} -> {after.get('hp')}")
    bits.append(f"Block {before.get('block', 0)} -> {after.get('block', 0)}")
    rb = player.get("resources_before") or {}
    ra = player.get("resources_after") or {}
    for name in sorted(set(rb) | set(ra)):
        if rb.get(name) != ra.get(name):
            short = name.replace("KLEEMOD_", "")
            bits.append(f"{short} {rb.get(name)} -> {ra.get(name)}")
    return "; ".join(bits) or "no change recorded"


def _flags(tester: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    if tester.get("refused"):
        flags.append(f"refused:{tester['refused']}")
    for hit in tester.get("resource_order_flag") or []:
        flags.append(f"resource_order:{hit.get('why', '')[:40]}")
    for hit in tester.get("misreads") or []:
        flags.append(f"misread:{str(hit)[:40]}")
    return flags


# --------------------------------------------------------------- tallies ---

def slot_grades(boards: Iterable[dict[str, Any]]) -> dict[str, list[str]]:
    """R221 B's own arithmetic, on the records: slot -> the grades it carries.

    SURVIVES reads PREDICTED and REFUSED reads MISSED -- the funnel's two
    mechanical verdicts, mapped onto the registration vocabulary the stopping
    rule is written in. A board that declares no slot carries one, its own id
    (`StagedTurn.registered_slots`).
    """
    out: dict[str, list[str]] = {}
    for b in boards:
        for slot in (b["slots"] or [b["turn_id"]]):
            bucket = out.setdefault(slot, [])
            if b["unrun"]:
                continue
            for g in b["graders"]:
                bucket.append("PRED" if g["verdict"] == "SURVIVES" else "MISS")
    return out


def slot_state(grades: dict[str, list[str]]) -> dict[str, str]:
    """DECIDED on two or more grades that all agree; UNDECIDED otherwise."""
    return {slot: ("DECIDED" if len(g) >= 2 and len(set(g)) == 1
                   else "UNDECIDED")
            for slot, g in grades.items()}


def codex_spend(boards: Iterable[dict[str, Any]]) -> dict[str, int]:
    """How much of the round's scarcest budget it actually spent."""
    spend = {"codex_reads": 0, "local_reads": 0, "control_reads": 0}
    for b in boards:
        for g in b["graders"]:
            if g["family"] == "gpt":
                spend["codex_reads"] += 1
            elif g["family"] == "local":
                spend["local_reads"] += 1
            else:
                spend["control_reads"] += 1
    return spend


def ledger_banners(root: Path | None = None) -> list[str]:
    """The `#` lines the ledger already carries. Quoted, never restated."""
    path = (root or QA_DIR) / "ledger.tsv"
    if not path.is_file():
        return []
    return [line.lstrip("# ").rstrip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith("#")]


# --------------------------------------------------------------- rendering -

def render(slug: str, root: Path | None = None,
           heading: str = "", turn_dir: Path | None = None) -> str:
    dirs = turn_dirs(slug, root)
    if not dirs:
        raise staged_turn.TurnError(
            f"no board records under {(root or QA_DIR)}/{slug}-t* -- the "
            f"section is generated FROM the records, so there is nothing to "
            f"write yet")
    slots = slot_map(turn_dir)
    boards = [board(d, slots) for d in dirs]
    grades = slot_grades(boards)
    state = slot_state(grades)
    spend = codex_spend(boards)
    run = [b for b in boards if not b["unrun"]]
    unrun = [b for b in boards if b["unrun"]]

    L: list[str] = []
    L.append(heading or f"## THE ROUND -- `{slug}`")
    L.append("")
    L.append(f"Generated from the records by `python -m understudy.staged_turn "
             f"packet-section {slug}` on "
             f"{time.strftime('%Y-%m-%d')}. Every table below is transcribed "
             f"from `review/qa/{slug}-t*/` and `review/qa/ledger.tsv`; nothing "
             f"here is re-graded and nothing is re-read (R101b).")
    L.append("")
    L.append(f"**{len(run)} board(s) run, {len(unrun)} UNRUN, "
             f"{sum(len(b['graders']) for b in run)} form(s) graded.**")
    L.append("")

    # --- per turn
    L.append("### The boards, grader by grader")
    L.append("")
    L.append("| turn | seed | grader | family | verdict | refused by | "
             "falsifier hits | replay |")
    L.append("|---|---|---|---|---|---|---|---|")
    for b in run:
        if not b["graders"]:
            L.append(f"| `{b['turn_id']}` | `{b['seed']}` | -- | -- | "
                     f"NOT GRADED | -- | -- | -- |")
            continue
        for i, g in enumerate(b["graders"]):
            L.append("| " + " | ".join([
                f"`{b['turn_id']}`" if i == 0 else "",
                f"`{b['seed']}`" if i == 0 else "",
                f"`{g['grader']}`", g["family"], f"**{g['verdict']}**",
                ", ".join(g["refused_by"]) or "--",
                "; ".join(g["flags"] + g["seat_review"]) or "--",
                g["replay"],
            ]) + " |")
    L.append("")

    # --- per slot
    L.append("### The registered slots")
    L.append("")
    L.append("A slot is **DECIDED** on two or more grades that all agree, "
             "**UNDECIDED** on any split or on fewer than two (R221 B). "
             "SURVIVES reads PREDICTED, REFUSED reads MISSED.")
    L.append("")
    L.append("| slot | grades | reading |")
    L.append("|---|---|---|")
    for slot in sorted(state):
        got = grades.get(slot) or []
        L.append(f"| `{slot}` | {', '.join(got) or '--'} "
                 f"({len(got)}) | **{state[slot]}** |")
    L.append("")

    # --- spend
    L.append("### What the round spent")
    L.append("")
    L.append(f"- **Codex seat reads:** {spend['codex_reads']} -- the scarce "
             f"budget, one record each.")
    L.append(f"- **Local tester reads:** {spend['local_reads']}.")
    L.append(f"- **Control / other reads:** {spend['control_reads']}.")
    L.append("")

    # --- unrun
    L.append("### UNRUN boards (R221 B)")
    L.append("")
    if not unrun:
        L.append("None -- every board in the pre-registered order was run.")
    else:
        L.append("| turn | seed | slots | why |")
        L.append("|---|---|---|---|")
        for b in unrun:
            L.append(f"| `{b['turn_id']}` | `{b['seed']}` | "
                     f"{', '.join(f'`{s}`' for s in b['slots']) or '--'} | "
                     f"{b['unrun_why'] or '--'} |")
        L.append("")
        L.append("**Their seeds are pinned.** A later round runs these exact "
                 "boards, not re-rolled ones.")
    L.append("")

    # --- banners, verbatim
    banners = ledger_banners(root)
    if banners:
        L.append("### The banners the ledger carries")
        L.append("")
        for line in banners:
            L.append(f"> {line}")
        L.append("")

    L.append("### The read")
    L.append("")
    L.append(PROSE_SLOT)
    L.append("")
    return "\n".join(L) + "\n"


def append_to(packet: Path, text: str) -> Path:
    """Append the section to a packet, with a rule above it.

    APPEND, never rewrite. The packets are the published argument and a tool
    that edited one in place would be a tool that could silently move a
    sentence somebody signed.
    """
    packet = Path(packet)
    existing = packet.read_text(encoding="utf-8") if packet.is_file() else ""
    sep = "" if existing.endswith("\n\n") else ("\n" if existing.endswith("\n")
                                                else "\n\n")
    packet.write_text(existing + sep + "---\n\n" + text, encoding="utf-8")
    return packet
