"""One row per (turn, grader), and the markers for a board nobody ran.

Cut out of `staged_turn.py` by `EB-180`: the ledger columns, the
agreement reads, the UNRUN / UNREACHED markers and `build_ledger`.
Re-exported from `staged_turn.py`, so `staged_turn.build_ledger()`
and `staged_turn.LEDGER_COLUMNS` still resolve.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any, Sequence

from understudy import bridge, qa_packet
from understudy.staged_turn_shape import (is_negative, _norm, USER_GRADER,
                                          WEIGHT_DISAGREE, WEIGHT_WINDOW)


def _st():
    """`understudy.staged_turn` itself, imported at CALL time.

    `QA_DIR` is declared on the facade because that is where a caller (and
    the suite) reaches in and swaps it. Binding it here at import would take
    a private copy and the swap would never be seen.
    """
    from understudy import staged_turn
    return staged_turn


# ---------------------------------------------------------------- ledger ---

# R221 B added the last two, at the END and nowhere else: `ledger_rows` pads
# a short row, so every ledger written before this parses unchanged and every
# reader that indexes by name keeps working. `seed` is the pin a later round
# needs to run an UNRUN board rather than a re-rolled one, and `run_state` is
# RUN for a graded row and UNRUN for a board sequential stopping did not run.
# The two-instance build added `instance`, at the END for the same reason
# `seed` and `run_state` were added there: `ledger_rows` pads a short row, so
# every ledger written before this parses unchanged and a row with no lane on
# it reads as the empty string rather than shifting every column after it.
LEDGER_COLUMNS = ("turn_id", "grader", "verdict", "refused_by",
                  "q1", "q2", "q3", "q4",
                  "agree_q1", "agree_q2", "agree_q4", "survives_alone",
                  "seed", "run_state",
                  # pick 4(e). WHICH CHAIR this row's grader sat in --
                  # `shadow` for a read that was taken but is not the deciding
                  # verdict, `deciding` for everything else, which is every
                  # row written before the chair existed. APPENDED, never
                  # inserted: `ledger_rows` zips the columns onto whatever
                  # cells a line has, so a short historical row parses and
                  # simply reads `deciding`.
                  "role",
                  # The two-instance build's lane, LAST -- after `role`, which
                  # main countersigned first. Same padding argument.
                  "instance")


def _cell(text: Any, width: int = 90) -> str:
    """One ledger cell: no tabs, no newlines, bounded."""
    s = " ".join(str(text or "").split())
    return (s[:width - 1] + "…") if len(s) > width else s


def _line_titles(form: dict[str, Any]) -> list[str]:
    return [_norm(p.get("card")) for p in (form.get("chosen_line") or [])]


def q2_agrees(a: dict[str, Any], b: dict[str, Any],
              titles: list[str]) -> bool | None:
    """Do two graders' second answers name a card in common?

    `titles` is the printed titles from the packet, which is the only
    vocabulary either answer could be written in. Deliberately shallow: this
    is not a semantic comparison and does not pretend to be one -- it asks
    whether the two people were weighing the same alternative, which is the
    thing R213's guard is about. `None` when neither answer names a card at
    all, so an unreadable pair does not count as a disagreement.
    """
    na, nb = _norm(a.get("q2_other_line_considered")), \
        _norm(b.get("q2_other_line_considered"))
    sa = {t for t in titles if t and t in na}
    sb = {t for t in titles if t and t in nb}
    if not sa and not sb:
        return None
    return bool(sa & sb)


def ledger_rows(root: Path | None = None) -> list[dict[str, str]]:
    path = (root or _st().QA_DIR) / "ledger.tsv"
    if not path.is_file():
        return []
    rows = []
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if not raw.strip() or raw.startswith("#"):
            continue
        cells = raw.split("\t")
        if i == 0 and cells and cells[0] == "turn_id":
            continue
        row = dict(zip(LEDGER_COLUMNS, cells + [""] * len(LEDGER_COLUMNS)))
        # A row written before the chair existed says nothing about it, and
        # "nothing" means the only chair there was.
        row["role"] = row.get("role") or DECIDING_ROLE
        rows.append(row)
    return rows


DECIDING_ROLE = "deciding"


def grader_role(turn_id: str, gid: str, root: Path | None = None) -> str:
    """Which chair a grader sat in for this turn, off its own tester record.

    Only the local seat writes a `tester-<id>.json`, and only it can be in the
    shadow chair; every other grader, and every record written before the
    chair existed, is `deciding`.
    """
    path = (root or _st().QA_DIR) / turn_id / f"tester-{gid}.json"
    if not path.is_file():
        return DECIDING_ROLE
    try:
        blob = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return DECIDING_ROLE
    return str(blob.get("role") or DECIDING_ROLE)


def is_down_weighted(gid: str, root: Path | None = None) -> tuple[bool, str]:
    """R213's second guard, made concrete.

    A grader that is not [USER] and whose QUESTION TWO disagreed with [USER]'s
    on at least WEIGHT_DISAGREE of the last WEIGHT_WINDOW turns they both
    answered loses the power to mark a turn SURVIVES ALONE. Turns where the
    comparison could not be made (no [USER] form, or neither answer named a
    card) are not counted either way -- an absent comparison is not a
    disagreement.
    """
    if gid == USER_GRADER:
        return False, ""
    shared = [r for r in ledger_rows(root)
              if r["grader"] == gid and r["agree_q2"] in ("yes", "no")]
    window = shared[-WEIGHT_WINDOW:]
    disagreements = sum(1 for r in window if r["agree_q2"] == "no")
    if disagreements >= WEIGHT_DISAGREE:
        return True, (
            f"grader {gid!r} is down-weighted: its answer to question two "
            f"disagreed with [USER]'s on {disagreements} of the last "
            f"{len(window)} turns they both played, so its SURVIVES needs "
            f"[USER]'s own cold-play form beside it "
            f"(threshold: {WEIGHT_DISAGREE} of {WEIGHT_WINDOW})")
    return False, ""


def _packet_titles(turn_id: str, root: Path | None = None) -> list[str]:
    p = (root or _st().QA_DIR) / turn_id / "packet.json"
    if not p.is_file():
        return []
    blob = json.loads(p.read_text(encoding="utf-8"))
    return [_norm(c.get("title"))
            for c in ((blob.get("board") or {}).get("hand") or [])]


def _packet_seed(turn_id: str, root: Path | None = None) -> str:
    p = (root or _st().QA_DIR) / turn_id / "packet.json"
    if not p.is_file():
        return "-"
    blob = json.loads(p.read_text(encoding="utf-8"))
    return str(blob.get("run_seed") or "-")


# ------------------------------------------------- R221 B: the UNRUN board --

UNRUN_NOTE = (
    "R221 B: sequential stopping. This board was staged in the round's "
    "pre-registered order and NOT run, because every registered slot it "
    "carries was already DECIDED -- two or more grades that all agreed -- "
    "before its turn came. Its seed is pinned here so a later round runs THIS "
    "board rather than a re-rolled one. Nothing about it was graded, and an "
    "UNRUN board is a board with no record, never a struck one (R101b)")


def mark_unrun(turn_id: str, *, seed: str, slots: Sequence[str],
               why: str, root: Path | None = None) -> Path:
    """Record a board the stopping rule did not run. One file, one row."""
    home = (root or _st().QA_DIR) / turn_id
    home.mkdir(parents=True, exist_ok=True)
    path = home / "unrun.json"
    path.write_text(json.dumps({
        "turn_id": turn_id,
        "instance": bridge.current_label(),
        "run_state": "UNRUN",
        "seed": seed or "-",
        "slots": list(slots),
        "why": why,
        "rule": UNRUN_NOTE,
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }, indent=1) + "\n", encoding="utf-8")
    return path


# ------------------------------------------ EB-208: the UNREACHED board ----

UNREACHED_NOTE = (
    "EB-208: the live-count preflight. A staged board cannot REQUIRE an enemy "
    "count -- the encounter is generated and a seed grants or refuses the "
    "bodies the turn file asked for -- and EB-202's ceiling is computed off "
    "the DECLARED board by construction, so a board that declared three and "
    "staged one still counted toward a counting slot's ceiling. After staging, "
    "the live enemy count is compared with the declared one; where they "
    "differ, this board is UNREACHED for every registered slot whose "
    "predicate reads `enemy_count`, and those slots take NO GRADE from it -- "
    "a board that cannot be asked is UNREACHED by the slate's own rule. The "
    "board is still read, graded and replayed: it may answer its other slots, "
    "and a shadow read costs nothing. Nothing here is struck (R101b); the "
    "board's own grades stand for the slots it could pose")


def live_enemy_count(turn_id: str, root: Path | None = None) -> int | None:
    """How many bodies the game actually staged, or `None` where nothing says.

    OFF `observed.json`, which is the tool's own record of the RAW wire state
    (`export_packet`). Its `digest.enemies` is the same list the packet's
    scrubbed board is built from, and it is read first because it is the
    unscrubbed one; `state.battle.enemies` and then the packet's own board are
    read after it so a board staged by an older build still answers.

    `None` IS NOT ZERO. A board with no record on disk has not been staged and
    says nothing about its live count, and the preflight must not read that
    silence as a mismatch.
    """
    home = (root or _st().QA_DIR) / turn_id
    for name, path_to in (("observed.json",
                           (("digest", "enemies"),
                            ("state", "battle", "enemies"))),
                          ("packet.json", (("board", "enemies"),))):
        path = home / name
        if not path.is_file():
            continue
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for keys in path_to:
            node: Any = blob
            for key in keys:
                node = node.get(key) if isinstance(node, dict) else None
            if isinstance(node, list):
                return len(node)
    return None


def mark_unreached(turn_id: str, *, seed: str, slots: Sequence[str],
                   declared: int, live: int,
                   root: Path | None = None) -> Path:
    """Record the slots this board cannot pose. One file, beside the rest."""
    home = (root or _st().QA_DIR) / turn_id
    home.mkdir(parents=True, exist_ok=True)
    path = home / "unreached.json"
    why = (f"the board declared {declared} enem(ies) and the game staged "
           f"{live} on seed {seed or '-'}; a slot that counts enemies cannot "
           f"be posed by this board")
    path.write_text(json.dumps({
        "turn_id": turn_id,
        "instance": bridge.current_label(),
        # THE BOARD RAN. `run_state` is the ledger's own column and this
        # board earns its RUN: it was staged, read, graded and replayed. What
        # is UNREACHED is a SLOT ON IT, which is why that is a separate key
        # and not a second ledger column.
        "run_state": "RUN",
        "slot_state": "UNREACHED",
        "seed": seed or "-",
        "slots": list(slots),
        "declared_enemies": int(declared),
        "live_enemies": int(live),
        "why": why,
        "rule": UNREACHED_NOTE,
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }, indent=1) + "\n", encoding="utf-8")
    return path


def unreached_boards(root: Path | None = None) -> list[dict[str, Any]]:
    """Every UNREACHED marker on disk, by turn id."""
    base = root or _st().QA_DIR
    out = []
    for q in sorted(base.glob("*/unreached.json")):
        blob = json.loads(q.read_text(encoding="utf-8"))
        blob.setdefault("turn_id", q.parent.name)
        out.append(blob)
    return out


def unreached_slots(root: Path | None = None) -> dict[str, list[str]]:
    """`turn id -> the slots that board may not be graded on` (EB-208)."""
    return {str(b["turn_id"]): [str(s) for s in (b.get("slots") or [])]
            for b in unreached_boards(root)}


def unrun_boards(root: Path | None = None) -> list[dict[str, Any]]:
    """Every UNRUN marker on disk, by turn id."""
    base = root or _st().QA_DIR
    out = []
    for q in sorted(base.glob("*/unrun.json")):
        blob = json.loads(q.read_text(encoding="utf-8"))
        blob.setdefault("turn_id", q.parent.name)
        out.append(blob)
    return out


def _row_instance(tid: str, gid: str, root: Path | None) -> str:
    """Which lane replayed this (turn, grader), off the execute record.

    The verdict does not carry it -- grading is mechanical and touches no
    game -- so the lane is read from the replay that DID touch one. `-` where
    a turn was never replayed, and for every row written before lanes existed.
    """
    home = (root or _st().QA_DIR) / tid
    for name in (f"execute-{gid}.json", "execute.json"):
        path = home / name
        if not path.is_file():
            continue
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        return str(blob.get("instance") or "-")
    return "-"


#: R221 + the two-instance build. Two lanes write per-turn artifacts into
#: their OWN `review/qa/<turn-id>/` directories, so those never collide -- but
#: `ledger.tsv` is ONE file for the whole round, rebuilt from disk rather than
#: appended to. This lock is what keeps a rebuild from two lanes at once from
#: interleaving a read of the directory with somebody else's write of the file.
LEDGER_LOCK = threading.Lock()


def build_ledger(root: Path | None = None) -> str:
    """One row per (turn, grader), with the agreement columns filled in.

    Rebuilt from the verdicts on disk rather than appended to, so a re-graded
    turn cannot leave a stale row behind arguing with its own replacement.
    """
    base = root or _st().QA_DIR
    by_turn: dict[str, dict[str, dict[str, Any]]] = {}
    # `verdict-<grader>.json` and NOT `verdict.json`: the latter is the
    # brief's fixed path for "the verdict on this turn" and is rewritten by
    # every grade, so globbing it too would enter the most recent grader
    # twice.
    for verdict_path in sorted(base.glob("*/verdict-*.json")):
        blob = json.loads(verdict_path.read_text(encoding="utf-8"))
        tid = str(blob.get("turn_id") or verdict_path.parent.name)
        gid = str((blob.get("grader") or {}).get("id") or "unknown")
        by_turn.setdefault(tid, {})[gid] = blob

    out = ["\t".join(LEDGER_COLUMNS)]
    for tid in sorted(by_turn):
        graders = by_turn[tid]
        titles = _packet_titles(tid, root)
        user = graders.get(USER_GRADER)
        for gid in sorted(graders):
            v = graders[gid]
            answers = v.get("answers") or {}
            agree = {"agree_q1": "-", "agree_q2": "-", "agree_q4": "-"}
            if user is not None and gid != USER_GRADER:
                ua = user.get("answers") or {}
                agree["agree_q1"] = _yn(
                    _line_titles(v) == _line_titles(user))
                a2 = q2_agrees({"q2_other_line_considered":
                                answers.get("q2_other_line_considered")},
                               {"q2_other_line_considered":
                                ua.get("q2_other_line_considered")}, titles)
                agree["agree_q2"] = "-" if a2 is None else _yn(a2)
                agree["agree_q4"] = _yn(
                    is_negative(answers.get("q4_different_intent"))
                    == is_negative(ua.get("q4_different_intent")))
            out.append("\t".join([
                tid, gid, str(v.get("verdict") or ""),
                ",".join(v.get("refused_by") or []) or "-",
                _cell(answers.get("q1_what_did_you_play")),
                _cell(answers.get("q2_other_line_considered")),
                _cell(answers.get("q3_what_it_gave_up")),
                _cell(answers.get("q4_different_intent")),
                agree["agree_q1"], agree["agree_q2"], agree["agree_q4"],
                _yn(bool(v.get("survives_alone"))),
                _packet_seed(tid, root), "RUN",
                grader_role(tid, gid, root),
                _row_instance(tid, gid, root),
            ]))
    # R221 B. The boards the stopping rule did not run, with their seeds
    # still pinned. They sit in the SAME table as the graded rows
    # deliberately: a round's record has to say what it did not do, or
    # "we ran four boards" and "there were only four boards" read the same
    # way afterwards.
    for blob in unrun_boards(root):
        if str(blob.get("turn_id")) in by_turn:
            continue
        out.append("\t".join([
            str(blob.get("turn_id") or ""), "-", "UNRUN",
            _cell(blob.get("why")) or "-",
            "-", "-", "-", "-", "-", "-", "-", "-",
            str(blob.get("seed") or "-"), "UNRUN", "-",
            str(blob.get("instance") or "-"),
        ]))
    out.append(f"# {qa_packet.PACKET_GUARDRAIL}")
    out.append(f"# down-weighting: a grader whose q2 disagrees with "
               f"[USER] on {WEIGHT_DISAGREE} of its last {WEIGHT_WINDOW} "
               f"shared turns cannot mark a turn SURVIVES alone")
    out.append(f"# UNRUN: {UNRUN_NOTE}")
    return "\n".join(out) + "\n"


def _yn(value: bool) -> str:
    return "yes" if value else "no"
