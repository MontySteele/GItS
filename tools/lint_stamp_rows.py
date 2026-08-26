#!/usr/bin/env python3
"""Correction D: STATE.md's live-cell rows are STAMPS, and a stamp is short.

WHY THIS EXISTS. `STATE.md` is one of the two always-read documents. Its Live
cell table answers exactly four questions -- what `RT`, `D`, `P` and `C` are
right now -- and every session pays for its length on every read. The `what
this value covers` cell has been absorbing the CHANGELOG of each bump: as of
2026-08-26 the four rows are 379 / 2,389 / 1,895 / 7,477 characters, so the
`C` row alone is longer than this tool. Narrative about how a version got where
it is belongs in the commit that moved it and in the window's own packet; the
stamp table's job is to say what the number IS.

The `RT` row shows the target is reachable rather than aspirational: it holds
its whole scope in 379 characters and passes today.

WHAT IS CHECKED. Every data row of the `## Live cell` table is at most
`MAX_ROW` characters of row text. Nothing else -- not the value, not the
source, not the wording. This lint is deliberately one rule: the four stamps
are gated for VERSION correctness by `lint_r_numbers.py` and by the suite's
constant pins, and duplicating that here would be a second thing to keep true.

**HOW IT SHIPS GREEN.** `DEBT` names the rows that fail today. As in
`lint_register_shape.py`, the set is a work list and not an exemption: a debt
row that has since been trimmed FAILS until its entry is deleted, so the set
can only shrink. A row not in `DEBT` -- including any row added later -- is
gated from this commit forward.

    python tools/lint_stamp_rows.py
    python tools/lint_stamp_rows.py --self-test

Exit 1 with findings on stdout.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

STATE = "docs/current/STATE.md"
SECTION = "## Live cell"

# One screen-ish. The `RT` row lives inside it today with room to spare, which
# is what makes this a target rather than a wish.
MAX_ROW = 400

# The stamp a row keys on: `` `RT` `RUNTEMPLATE_VERSION` `` -> `RT`.
KEY = re.compile(r"`([A-Z]{1,2})`")


def stamp_rows(text: str) -> list[tuple[str, str]]:
    """`(stamp, row text)` for every data row under `## Live cell`.

    Scoped to that one section on purpose: `STATE.md` carries a roster table
    and several others, and a lint that policed every table in the file would
    be making a claim about documents it was never asked to shorten.
    """
    out: list[tuple[str, str]] = []
    inside = False
    header_seen = False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() == SECTION
            header_seen = False
            continue
        if not inside:
            continue
        stripped = line.strip()
        if not stripped.startswith("|"):
            header_seen = False
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(set(c) <= set("-: ") and c for c in cells):
            header_seen = True
            continue
        if not header_seen:
            continue
        match = KEY.search(cells[0])
        out.append((match.group(1) if match else cells[0][:12], stripped))
    return out


# --- THE CURATED DEBT SET --------------------------------------------------
# Frozen 2026-08-26 against `gov-d-mechanisms` at `D` 2,389 / `P` 1,895 / `C`
# 7,477 characters; PAID the same day when Correction B's STATE diet landed on
# `gov-2026-08-26` (RT 318 / D 282 / P 338 / C 368; history -> STAMPS.md). The
# set is empty and only ever shrinks: a row that grows past 400 again FAILS,
# it does not get a new entry here.
DEBT: frozenset[str] = frozenset()


def findings(text: str | None = None,
             debt: frozenset[str] | None = None) -> tuple[list[str], int]:
    debt = DEBT if debt is None else debt
    if text is None:
        page = REPO / STATE
        if not page.exists():
            return ([f"MISSING: {STATE} does not exist -- this lint cannot "
                     f"answer the question it claims to answer."], 0)
        text = page.read_text(encoding="utf-8")

    rows = stamp_rows(text)
    over = {stamp for stamp, row in rows if len(row) > MAX_ROW}
    out: list[str] = []

    for stamp, row in rows:
        if len(row) > MAX_ROW and stamp not in debt:
            out.append(f"STAMP ROW: `{stamp}` is {len(row)} chars > {MAX_ROW}. "
                       f"STATE.md is read by every session; the live-cell "
                       f"table says what the number IS, and how it got there "
                       f"belongs in the commit that moved it.")

    for stamp in sorted(debt - over):
        if any(s == stamp for s, _ in rows):
            out.append(f"DEBT PAID: `{stamp}` now fits in {MAX_ROW} chars. "
                       f"Delete it from DEBT in this file -- the set only "
                       f"shrinks.")
        else:
            out.append(f"STALE DEBT: the live-cell table has no `{stamp}` row "
                       f"any more. Drop the entry in the same commit.")
    return out, len(rows)


def self_test() -> list[str]:
    bad: list[str] = []
    header = (f"{SECTION}\n\n| stamp | value | source | what this value "
              f"covers |\n|---|---|---|---|\n")
    short = "| `RT` `RUNTEMPLATE_VERSION` | **12** | `tier0/constants.py` | ok |"
    long_row = short.replace("ok", "x" * (MAX_ROW + 100))

    clean, count = findings(header + short, frozenset())
    if clean or count != 1:
        bad.append(f"self-test: a short stamp row was refused: {clean}")

    hit, _ = findings(header + long_row, frozenset())
    if not any(f.startswith("STAMP ROW:") for f in hit):
        bad.append("self-test: an over-long stamp row was accepted")

    carried, _ = findings(header + long_row, frozenset({"RT"}))
    if carried:
        bad.append(f"self-test: a DEBT row was reported as a failure: {carried}")

    paid, _ = findings(header + short, frozenset({"RT"}))
    if not any(f.startswith("DEBT PAID:") for f in paid):
        bad.append("self-test: a trimmed DEBT row was not reported")

    stale, _ = findings(header + short, frozenset({"ZZ"}))
    if not any(f.startswith("STALE DEBT:") for f in stale):
        bad.append("self-test: a DEBT entry with no row was not reported")

    # A table OUTSIDE the section must be invisible to this lint.
    other = header + short + "\n\n## Roster\n\n| id | x |\n|---|---|\n| `klee` | " \
            + "y" * (MAX_ROW + 100) + " |"
    elsewhere, count = findings(other, frozenset())
    if elsewhere or count != 1:
        bad.append(f"self-test: a table outside `{SECTION}` was scanned: "
                   f"{elsewhere}")
    return bad


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        bad = self_test()
        for line in bad:
            print(line)
        print(f"self-test: 6 case(s), {len(bad)} failure(s)")
        return 1 if bad else 0

    bad, count = findings()
    for line in bad:
        print(line)
    print(f"scope: {count} live-cell row(s) in {STATE}, limit {MAX_ROW} chars, "
          f"{len(DEBT)} carried as DEBT")
    if not count:
        print("VACUOUS: the live-cell table was not found at all. The section "
              "or the row shape moved; this lint is reporting nothing, not "
              "health.")
        return 1
    if bad:
        print(f"\n{len(bad)} finding(s).")
        return 1
    print(f"stamp-rows OK: every live-cell row outside the {len(DEBT)}-row "
          f"DEBT set fits in {MAX_ROW} characters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
