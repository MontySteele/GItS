#!/usr/bin/env python3
"""Correction D: the SHAPE of a register row, gated instead of described.

WHY THIS EXISTS. `BACKLOG.md` opens by declaring its own contract — *"Every row
is four things: current scope / next action / gate / acceptance"* — and
`QUEUE.md` opens with R136's admission test, *"every row must contain an
explicit human-only verb"*. Both sentences are prose, and prose is context, not
configuration: `lint_register_ids.py` gates the row's ID and nothing has ever
gated the row's BODY. The result is visible by eye — rows that have grown to
seven thousand characters, rows whose gate is a paragraph rather than a clause,
rows that ask for a decision without naming the options being decided between.
A register that cannot be read in one sitting is not a register.

WHAT IS CHECKED.

  **BACKLOG.md**, per row:
    1. all four field markers present — `**Scope`, `**Next action`, `**Gate`,
       `**Acceptance` (the bold opener is the marker; the trailing colon is
       inside the bold in some rows and outside it in others, and that variance
       is cosmetic);
    2. the row is at most `BACKLOG_MAX` characters of row text.

  **QUEUE.md**, per row:
    3. an ASK — an explicit human-only verb from R136's list, so the row states
       what [USER] is being asked to DO;
    4. a PICK LIST — a numbered option list the answer can be given against
       (`(1)` … `(2)` …), **or** the explicit `eyes-on` marker, which is the
       one legitimate row shape with nothing to enumerate: a taste look has no
       options, only a thing to look at;
    5. a GATE — the Status cell names a status and, after a dash, what the row
       is waiting on;
    6. the row is at most `QUEUE_MAX` characters of row text.

**HOW IT SHIPS GREEN.** Every row failing today is named in `DEBT` below, with
its failing rules, and is reported as debt rather than as a failure. This is
the repo's structurally-invisible-defect pattern: the gate binds from this
commit forward — a NEW row, or an EDIT that pushes a clean row over a limit,
fails — while the existing backlog of over-long rows is a list someone can
shorten one row at a time. **`DEBT` is not a suppression list, it is a work
list**: rule 7 fails a `DEBT` entry that has since become clean, so the set can
only shrink, and rule 8 fails an entry naming a row that no longer exists.
Empty the set and delete it, and this file becomes an ordinary gate.

    python tools/lint_register_shape.py
    python tools/lint_register_shape.py --print-debt   # regenerate the set
    python tools/lint_register_shape.py --self-test    # prove the rules bite

Exit 1 with findings on stdout.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

QUEUE = "docs/current/QUEUE.md"
BACKLOG = "docs/current/BACKLOG.md"

# The ceilings. Not derived from the current rows -- a limit computed from the
# thing it limits is not a limit. These are the lengths at which a row still
# reads as a row: roughly a screen for an engineering item, rather less for a
# decision, which should be a question and its options.
BACKLOG_MAX = 600
QUEUE_MAX = 500

# BACKLOG's own four-field contract. Matched at the bold opener, because the
# colon sits inside the bold in `**Scope: the thing**` and outside it in
# `**Scope:**`, and both spellings are in HEAD today.
BACKLOG_FIELDS = ("Scope", "Next action", "Gate", "Acceptance")

# R136's admission test, verbatim: *choose, ratify, amend, accept taste, or
# approve spend*, plus the four spellings the register actually uses for those
# same acts. `investigate`, `measure`, `draft` are deliberately absent -- a row
# whose only verb is one of those belongs in BACKLOG.
ASK_VERBS = ("choose", "chosen", "ratify", "ratified", "amend", "accept",
             "approve", "pick", "declare", "countersign", "rule on",
             "re-price", "re-stock", "decide")

# A numbered option list the answer can be given against. Two DISTINCT
# parenthesised integers, so `(1)` alone -- a footnote, not a menu -- does not
# satisfy it.
OPTION = re.compile(r"\((\d{1,2})\)")

# The one row shape with nothing to enumerate.
EYES_ON = re.compile(r"eyes-on", re.IGNORECASE)

# A Status cell that names a status AND what it waits on: `OPEN -- table time;
# gated on the EB-53 remnant`.
GATED = re.compile(r"\b(OPEN|RULED|DONE|HELD|BLOCKED|INERT)\b.*[-—–:;,]\s*\S")


def rows(text: str) -> list[tuple[int, str, list[str]]]:
    """`(line number, row key, cells)` for every DATA row of every table.

    A data row is a pipe line that is neither the header nor the `|---|`
    separator. The key is the first cell with its backticks and bold stripped:
    most rows key on an id (`EB-71`), a few on a phrase (`Art debt`), and both
    are rows.
    """
    out: list[tuple[int, str, list[str]]] = []
    header_seen = False
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            header_seen = False
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(set(c) <= set("-: ") and c for c in cells):
            header_seen = True                      # the `|---|` separator
            continue
        if not header_seen:
            continue                                # the header row itself
        key = re.sub(r"[`*]", "", cells[0]).strip()
        if key:
            out.append((number, key, cells))
    return out


def backlog_failures(key: str, line: str) -> list[str]:
    bad = []
    missing = [f for f in BACKLOG_FIELDS
               if not re.search(r"\*\*" + f + r"\b", line, re.IGNORECASE)]
    if missing:
        bad.append("missing " + "/".join(missing))
    if len(line) > BACKLOG_MAX:
        bad.append(f"{len(line)} chars > {BACKLOG_MAX}")
    return bad


def queue_failures(key: str, line: str, cells: list[str]) -> list[str]:
    bad = []
    decision = cells[1] if len(cells) > 1 else ""
    status = cells[2] if len(cells) > 2 else ""
    if not any(v in decision.lower() for v in ASK_VERBS):
        bad.append("no ask verb")
    if len({m for m in OPTION.findall(decision)}) < 2 and not EYES_ON.search(line):
        bad.append("no pick list or eyes-on marker")
    if not GATED.search(status):
        bad.append("no gate in Status")
    if len(line) > QUEUE_MAX:
        bad.append(f"{len(line)} chars > {QUEUE_MAX}")
    return bad


def scan(sources: dict[str, str] | None = None) -> dict[tuple[str, str], list[str]]:
    """`{(register, row key): [failing rule, ...]}` over both registers."""
    out: dict[tuple[str, str], list[str]] = {}
    for rel in (sources or {QUEUE: None, BACKLOG: None}):
        if sources is not None:
            text = sources[rel]
        else:
            page = REPO / rel
            if not page.exists():
                out[(rel, "<missing>")] = ["the register does not exist"]
                continue
            text = page.read_text(encoding="utf-8")
        for _, key, cells in rows(text):
            line = "| " + " | ".join(cells) + " |"
            bad = (backlog_failures(key, line) if rel == BACKLOG
                   else queue_failures(key, line, cells))
            if bad:
                out[(rel, key)] = bad
    return out


# --- THE CURATED DEBT SET --------------------------------------------------
# Frozen 2026-08-26 against `gov-d-mechanisms`. Every row here fails today and
# is EXEMPT until it is rewritten; nothing may be added without shortening
# something else. Regenerate with `--print-debt` ONLY when a rewrite has
# emptied entries, never to absorb a fresh failure -- that is what rules 7
# and 8 below are for.
DEBT: frozenset[tuple[str, str]] = frozenset({
    (BACKLOG, 'EB-1'),   # 3227 chars > 600
    (BACKLOG, 'EB-105'),   # 3695 chars > 600
    (BACKLOG, 'EB-116'),   # 1292 chars > 600
    (BACKLOG, 'EB-12'),   # 795 chars > 600
    (BACKLOG, 'EB-128'),   # 5901 chars > 600
    (BACKLOG, 'EB-137'),   # 3117 chars > 600
    (BACKLOG, 'EB-146'),   # 1785 chars > 600
    (BACKLOG, 'EB-15'),   # 1099 chars > 600
    (BACKLOG, 'EB-33/34/35'),   # 938 chars > 600
    (BACKLOG, 'EB-40'),   # 1626 chars > 600
    (BACKLOG, 'EB-41'),   # 1788 chars > 600
    (BACKLOG, 'EB-53'),   # 2431 chars > 600
    (BACKLOG, 'EB-65'),   # 1419 chars > 600
    (BACKLOG, 'EB-67'),   # 913 chars > 600
    (BACKLOG, 'EB-70'),   # 793 chars > 600
    (BACKLOG, 'EB-71'),   # 697 chars > 600
    (BACKLOG, 'EB-74'),   # 2067 chars > 600
    (BACKLOG, 'EB-78'),   # 2320 chars > 600
    (BACKLOG, 'EB-83'),   # 2632 chars > 600
    (BACKLOG, 'EB-84'),   # 1874 chars > 600
    (BACKLOG, 'SKIP-10.9'),   # 1724 chars > 600
    (QUEUE, 'Art debt'),   # 5904 chars > 500
    (QUEUE, 'M13'),   # no pick list or eyes-on marker; 1623 chars > 500
    (QUEUE, 'M14'),   # 12716 chars > 500
    (QUEUE, 'M16'),   # no ask verb; no pick list or eyes-on marker; 508 chars > 500
    (QUEUE, 'M17'),   # 10246 chars > 500
    (QUEUE, 'M19'),   # no pick list or eyes-on marker; 1615 chars > 500
    (QUEUE, 'M26'),   # no ask verb; 1775 chars > 500
    (QUEUE, 'M45'),   # 4279 chars > 500
    (QUEUE, 'S4-G11'),   # no pick list or eyes-on marker; no gate in Status; 2322 chars > 500
    (QUEUE, 'S4-G12 / CC-G1 / CC-G2'),   # no ask verb; 614 chars > 500
    (QUEUE, 'S4-G13'),   # no pick list or eyes-on marker; 6020 chars > 500
    (QUEUE, 'S4-G14'),   # no ask verb; no pick list or eyes-on marker; 1127 chars > 500
    (QUEUE, 'S4-G17'),   # no pick list or eyes-on marker
    (QUEUE, 'S4-G6'),   # no pick list or eyes-on marker; 862 chars > 500
    (QUEUE, 'S8 + S10 galleries'),   # no ask verb; no pick list or eyes-on marker; 690 chars > 500
})


def findings(sources: dict[str, str] | None = None,
             debt: frozenset[tuple[str, str]] | None = None) -> list[str]:
    debt = DEBT if debt is None else debt
    failures = scan(sources)
    out: list[str] = []

    for (rel, key), bad in sorted(failures.items()):
        if (rel, key) in debt:
            continue
        out.append(f"SHAPE: {rel} row {key!r} -- {'; '.join(bad)}. The "
                   f"register's own contract, gated: BACKLOG rows carry "
                   f"scope/next action/gate/acceptance, QUEUE rows carry an "
                   f"ask, a pick list (or `eyes-on`) and a gate, and neither "
                   f"runs past its length.")

    # Rule 7: debt that has been PAID must leave the set, or the set stops
    # being a work list and becomes a permanent exemption.
    live = {(rel, key) for rel, key, _ in _all_rows(sources)}
    for entry in sorted(debt - set(failures)):
        rel, key = entry
        if entry in live:
            out.append(f"DEBT PAID: {rel} row {key!r} now passes every shape "
                       f"rule. Delete it from DEBT in this file -- the set "
                       f"only shrinks.")
        else:
            # Rule 8: the row closed and left HEAD.
            out.append(f"STALE DEBT: {rel} has no row {key!r} any more. The "
                       f"row closed; drop the entry in the same commit, the "
                       f"way OPEN_IDS is maintained in lint_register_ids.py.")
    return out


def _all_rows(sources: dict[str, str] | None) -> list[tuple[str, str, str]]:
    out = []
    for rel in (sources or {QUEUE: None, BACKLOG: None}):
        text = (sources[rel] if sources is not None
                else (REPO / rel).read_text(encoding="utf-8")
                if (REPO / rel).exists() else "")
        for _, key, cells in rows(text):
            out.append((rel, key, "| " + " | ".join(cells) + " |"))
    return out


def self_test() -> list[str]:
    """Synthetic rows, because the real registers are (correctly) all debt."""
    bad: list[str] = []
    good_backlog = ("| `EB-9` | **Scope:** short. **Next action:** do it. "
                    "**Gate:** none. **Acceptance:** it is done | R1 |")
    header = "| ID | Item | Provenance |\n|---|---|---|\n"

    clean = findings({BACKLOG: header + good_backlog, QUEUE: ""}, frozenset())
    if clean:
        bad.append(f"self-test: a well-shaped BACKLOG row was refused: {clean}")

    for field in BACKLOG_FIELDS:
        holed = good_backlog.replace(f"**{field}:**", "")
        hit = findings({BACKLOG: header + holed, QUEUE: ""}, frozenset())
        if not any(field in f for f in hit):
            bad.append(f"self-test: a row missing **{field}** was accepted")

    fat = good_backlog.replace("short.", "x" * (BACKLOG_MAX + 50))
    if not any("chars >" in f for f in
               findings({BACKLOG: header + fat, QUEUE: ""}, frozenset())):
        bad.append("self-test: an over-long BACKLOG row was accepted")

    qheader = "| ID | Decision needed | Status | Provenance |\n|---|---|---|---|\n"
    good_queue = ("| `M1` | **CHOOSE** between (1) the short bar and (2) the "
                  "long one | OPEN -- gated on the playtest | R2 |")
    clean = findings({QUEUE: qheader + good_queue, BACKLOG: ""}, frozenset())
    if clean:
        bad.append(f"self-test: a well-shaped QUEUE row was refused: {clean}")

    eyes = ("| `M2` | **ACCEPT** the art, eyes-on | OPEN -- taste, gated on "
            "the contact sheet | R3 |")
    if findings({QUEUE: qheader + eyes, BACKLOG: ""}, frozenset()):
        bad.append("self-test: an eyes-on row without a pick list was refused")

    verbless = good_queue.replace("**CHOOSE**", "investigate")
    if not any("no ask verb" in f for f in
               findings({QUEUE: qheader + verbless, BACKLOG: ""}, frozenset())):
        bad.append("self-test: a QUEUE row with no human-only verb was accepted")

    unlisted = good_queue.replace("(1) the short bar and (2) the long one",
                                  "something")
    if not any("pick list" in f for f in
               findings({QUEUE: qheader + unlisted, BACKLOG: ""}, frozenset())):
        bad.append("self-test: a QUEUE row with no options was accepted")

    ungated = good_queue.replace("OPEN -- gated on the playtest", "OPEN")
    if not any("no gate" in f for f in
               findings({QUEUE: qheader + ungated, BACKLOG: ""}, frozenset())):
        bad.append("self-test: a QUEUE row with a bare status was accepted")

    paid = findings({BACKLOG: header + good_backlog, QUEUE: ""},
                    frozenset({(BACKLOG, "EB-9")}))
    if not any(f.startswith("DEBT PAID:") for f in paid):
        bad.append("self-test: a DEBT entry that now passes was not reported")

    stale = findings({BACKLOG: header + good_backlog, QUEUE: ""},
                     frozenset({(BACKLOG, "EB-999")}))
    if not any(f.startswith("STALE DEBT:") for f in stale):
        bad.append("self-test: a DEBT entry whose row is gone was not reported")
    return bad


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        bad = self_test()
        for line in bad:
            print(line)
        print(f"self-test: 13 case(s), {len(bad)} failure(s)")
        return 1 if bad else 0

    failures = scan()
    if "--print-debt" in argv:
        print("DEBT: frozenset[tuple[str, str]] = frozenset({")
        for (rel, key), bad in sorted(failures.items()):
            print(f'    ({"QUEUE" if rel == QUEUE else "BACKLOG"}, {key!r}),'
                  f'   # {"; ".join(bad)}')
        print("})")
        return 0

    bad = findings()
    for line in bad:
        print(line)
    total = len(_all_rows(None))
    print(f"scope: {total} row(s) across 2 register(s); {len(failures)} fail a "
          f"shape rule, {len(DEBT)} of them carried as DEBT")
    if not total:
        print("VACUOUS: no register rows were found at all. The row shape "
              "moved; this lint is reporting nothing, not health.")
        return 1
    if bad:
        print(f"\n{len(bad)} finding(s).")
        return 1
    print(f"register-shape OK: every row outside the {len(DEBT)}-row DEBT set "
          f"carries its register's declared fields and stays inside its "
          f"length. Emptying DEBT is the rewrite this gate is holding open.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
