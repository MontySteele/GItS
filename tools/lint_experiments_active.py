#!/usr/bin/env python3
"""Correction D: "Active registrations" means ACTIVE. A graded cell is not active.

WHY THIS EXISTS. `EXPERIMENTS.md`'s **Active registrations** list is the
answer to one question a session asks constantly -- *what measurement is
currently open, and what is frozen because of it?* A registration that has been
run and graded answers "nothing is open here", and leaving it in the list makes
the reader carry a finished experiment's freeze, its tripwires and its world
pin as if they still bound. As of 2026-08-26 the list is eight entries and four
of them open with `RUN AND GRADED` or `RUN AND BLIND-GRADED`: half the section
is history filed under the heading that means the opposite.

This is the closed-items-leave-HEAD norm, applied to the one register that had
no gate for it. A graded registration's outcome belongs in its `QUEUE` row and
in the packet; the pointer here belongs to the next unrun cell.

WHAT IS CHECKED. Every top-level `- ` entry under the `## Active
registrations` heading, tested on its HEADLINE -- the first `HEADLINE_CHARS`
characters, which is where these entries put their status. An UPPERCASE
completion marker there (`GRADED`, `RUN AND GRADED`, `BLIND-GRADED`) fails.

**The headline, not the body, and that distinction is the whole design.** Every
live registration discusses grading -- it is a pre-registration; grading is
what it is FOR. `EB-78`'s entry says "DRAFT, unrun" and then explains how its
slots will be graded; a lint that searched the body would fail exactly the
entries that belong in the list, which is the failure mode that makes people
delete lints.

**HOW IT SHIPS GREEN.** `DEBT` names the entries that are graded today, keyed
by a stable fragment of the entry's title. As in the sibling Correction-D
lints, the set is a work list, not an exemption: a `DEBT` entry that is no
longer graded-in-headline FAILS until its entry is deleted, and so does one
whose title is gone from the section. The set can only shrink.

    python tools/lint_experiments_active.py
    python tools/lint_experiments_active.py --print-debt
    python tools/lint_experiments_active.py --self-test

Exit 1 with findings on stdout.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

EXPERIMENTS = "docs/current/EXPERIMENTS.md"
SECTION = "## Active registrations"

# How much of an entry counts as its headline. These entries lead with their
# status in bold; 250 characters is about two wrapped lines, comfortably past
# the title and the status and comfortably short of the narrative.
HEADLINE_CHARS = 250

# UPPERCASE only. `graded blind` in a lower-case sentence is a live entry
# describing its own method; `RUN AND GRADED` in the headline is a status.
DONE = re.compile(r"\bRUN AND (?:BLIND-)?GRADED\b|\bBLIND-GRADED\b|\bGRADED\b")

# The entry's key: the bolded title it opens with, e.g.
# `- **payoff-reach re-registration** -- ...` -> `payoff-reach re-registration`.
TITLE = re.compile(r"^-\s*\*\*(.+?)\*\*", re.DOTALL)


def entries(text: str) -> list[tuple[str, str]]:
    """`(title, full entry text)` for every top-level bullet in the section."""
    lines = text.splitlines()
    try:
        # startswith, not equality: the live heading carries a parenthetical
        # ("(pointers -- packets live in `review/active/`)") and an exact
        # match would silently find no section at all, which is the failure
        # mode the VACUOUS check below exists to make loud.
        start = next(i for i, line in enumerate(lines)
                     if line.startswith(SECTION))
    except StopIteration:
        return []
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break

    out: list[tuple[str, str]] = []
    buffer: list[str] = []
    for line in lines[start + 1:end]:
        if line.startswith("- "):
            if buffer:
                out.append(_keyed(buffer))
            buffer = [line]
        elif buffer:
            buffer.append(line)
    if buffer:
        out.append(_keyed(buffer))
    return out


def _keyed(buffer: list[str]) -> tuple[str, str]:
    body = "\n".join(buffer)
    match = TITLE.match(body)
    title = " ".join(match.group(1).split()) if match else body[2:60].strip()
    return title, body


def headline(body: str) -> str:
    return " ".join(body.split())[:HEADLINE_CHARS]


# --- THE CURATED DEBT SET --------------------------------------------------
# Frozen 2026-08-26 against `gov-d-mechanisms`. Four of the eight entries are
# finished measurements still filed as active. Each leaves the list when its
# outcome has been carried into its QUEUE row and its packet -- and the entry
# must leave DEBT in the same commit, or rule 2 fails.
DEBT: frozenset[str] = frozenset()


def findings(text: str | None = None,
             debt: frozenset[str] | None = None) -> tuple[list[str], int]:
    debt = DEBT if debt is None else debt
    if text is None:
        page = REPO / EXPERIMENTS
        if not page.exists():
            return ([f"MISSING: {EXPERIMENTS} does not exist -- this lint "
                     f"cannot answer the question it claims to answer."], 0)
        text = page.read_text(encoding="utf-8")

    found = entries(text)
    graded = {title for title, body in found if DONE.search(headline(body))}
    out: list[str] = []

    for title in sorted(graded - debt):
        out.append(f"GRADED BUT ACTIVE: {title!r} is filed under "
                   f"'{SECTION.lstrip('# ')}' and its headline says it has "
                   f"been run and graded. A finished measurement opens no "
                   f"freeze and binds no tripwire; its outcome belongs in its "
                   f"QUEUE row and its packet. Closed items leave HEAD.")

    for title in sorted(debt - graded):
        if any(t == title for t, _ in found):
            out.append(f"DEBT PAID: {title!r} no longer reads as graded in its "
                       f"headline. Delete it from DEBT in this file -- the set "
                       f"only shrinks.")
        else:
            out.append(f"STALE DEBT: no entry titled {title!r} is in the "
                       f"section any more. Drop the entry in the same commit "
                       f"as the removal.")
    return out, len(found)


def self_test() -> list[str]:
    bad: list[str] = []
    head = f"{SECTION}\n"
    live = "- **a live cell** — **DRAFT, unrun**, its slots will be graded blind later.\n"
    done = "- **a finished cell** — **RUN AND GRADED 2026-08-24.** nine misses.\n"
    blind = "- **another finished cell** — **COUNTERSIGNED, RUN AND BLIND-GRADED 2026-08-26.**\n"

    clean, count = findings(head + live, frozenset())
    if clean or count != 1:
        bad.append(f"self-test: a live DRAFT entry that merely MENTIONS "
                   f"grading was refused: {clean}")

    hit, _ = findings(head + live + done, frozenset())
    if not any("a finished cell" in f for f in hit):
        bad.append("self-test: a RUN AND GRADED entry was accepted")

    hit, _ = findings(head + blind, frozenset())
    if not any("another finished cell" in f for f in hit):
        bad.append("self-test: a BLIND-GRADED entry was accepted")

    carried, _ = findings(head + done, frozenset({"a finished cell"}))
    if carried:
        bad.append(f"self-test: a DEBT entry was reported as a failure: "
                   f"{carried}")

    paid, _ = findings(head + live, frozenset({"a live cell"}))
    if not any(f.startswith("DEBT PAID:") for f in paid):
        bad.append("self-test: a DEBT entry that is no longer graded was not "
                   "reported")

    stale, _ = findings(head + live, frozenset({"a cell that left"}))
    if not any(f.startswith("STALE DEBT:") for f in stale):
        bad.append("self-test: a DEBT entry with no entry was not reported")

    # A graded marker DEEP in the body must not fire -- that is a live entry
    # describing what will be done to it.
    deep = ("- **a long live cell** — **DRAFT, unrun.**\n" + "  filler.\n" * 40
            + "  the outcome was RUN AND GRADED elsewhere.\n")
    late, _ = findings(head + deep, frozenset())
    if late:
        bad.append(f"self-test: a marker past the headline fired: {late}")

    # And a section that moved must not read clean.
    moved, count = findings("## Something else\n" + done, frozenset())
    if count:
        bad.append("self-test: entries were found outside the section")
    return bad


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        bad = self_test()
        for line in bad:
            print(line)
        print(f"self-test: 8 case(s), {len(bad)} failure(s)")
        return 1 if bad else 0

    if "--print-debt" in argv:
        text = (REPO / EXPERIMENTS).read_text(encoding="utf-8")
        print("DEBT: frozenset[str] = frozenset({")
        for title, body in entries(text):
            if DONE.search(headline(body)):
                print(f"    {title!r},")
        print("})")
        return 0

    bad, count = findings()
    for line in bad:
        print(line)
    print(f"scope: {count} registration(s) under '{SECTION.lstrip('# ')}' in "
          f"{EXPERIMENTS}; {len(DEBT)} carried as DEBT")
    if not count:
        print("VACUOUS: no registrations were found at all. The section "
              "heading or the bullet shape moved; this lint is reporting "
              "nothing, not health.")
        return 1
    if bad:
        print(f"\n{len(bad)} finding(s).")
        return 1
    print(f"experiments-active OK: every registration outside the "
          f"{len(DEBT)}-entry DEBT set is genuinely open.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
