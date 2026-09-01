#!/usr/bin/env python3
"""The review tree says what it is, and nothing points at a packet that moved.

WHY THIS EXISTS. `review/active/` is supposed to hold what is actually
active. On 2026-09-01 it held 61 files and five of them had an open pick; the
other 56 were finished decision packets and published measurements that a
session had to open to find out they were finished. Three directories now
carry the three kinds of thing, and one line at the top of each file says
which:

    review/active/   a packet with an open pick        Status: OPEN (picks ...)
    review/ruled/    a decision packet, all picks answered
                                                       Status: RULED R### DATE
    review/records/  a published measurement or log     Status: RECORD

plus `Status: SUPERSEDED by <path>` anywhere, for a packet a later one
replaced.

WHAT IS CHECKED, in three parts.

1. STATUS SHAPE. Every `.md` file in the three directories opens with a
   `Status:` line in one of the four forms. `review/active/` takes only OPEN;
   `review/ruled/` and `review/records/` take anything but OPEN. Raw results
   files (`.txt`, `.tsv`, `.json`) carry no status line -- they are machine
   output and a prepended header would corrupt them; their registration's
   `.md` carries the status for them.

2. DEAD CITATIONS. Every `review/...` path cited under `docs/current/`,
   `CLAUDE.md`, `AGENTS.md`, `tools/`, `tier0/`, `tier05/` or `understudy/`
   must exist. Two forms are deliberately not checked: a `git show <commit>:`
   retrieval path, which names a file that left HEAD on purpose (CLAUDE.md
   sec.History retrieval), and a glob or template (`*`, `{`, `<`).

3. SIZE, AS A WARNING. More than `ACTIVE_WARN` files in `review/active/`
   prints a warning and exits 0. The number is a reading habit, not a rule,
   so it does not fail a build.

    python tools/lint_review_status.py
    python tools/lint_review_status.py --self-test

Exit 1 with findings on stdout.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

ACTIVE = "review/active"
RULED = "review/ruled"
RECORDS = "review/records"
ACTIVE_WARN = 10

# The four forms, anchored at the start of the file's first line.
OPEN = re.compile(r"^Status: OPEN \(.+\)$")
RULED_RE = re.compile(r"^Status: RULED (R\d+ \d{4}-\d{2}-\d{2}"
                      r"|\(see RULINGS\.md\))$")
RECORD = re.compile(r"^Status: RECORD$")
SUPERSEDED = re.compile(r"^Status: SUPERSEDED by \S+$")

# Where a citation of a review path is a live pointer rather than history.
CITING_ROOTS = ("docs/current", "tools", "tier0", "tier05", "understudy")
CITING_FILES = ("CLAUDE.md", "AGENTS.md")
CITING_EXT = {".py", ".md", ".tsv", ".yaml", ".yml", ".ps1", ".json", ".txt"}
# understudy/turns holds staged run artifacts: the paths in them are the
# record of what a past run was handed, not a pointer this repo maintains.
CITING_SKIP = ("understudy/turns",)

CITATION = re.compile(r"review/[A-Za-z0-9._/-]*[A-Za-z0-9]")
# This file's own self-test strings are examples, not pointers.
SELF = "tools/lint_review_status.py"


def status_line(path: Path) -> str:
    with path.open(encoding="utf-8") as handle:
        return handle.readline().rstrip("\n").rstrip("\r")


def check_statuses() -> tuple[list[str], int]:
    """Findings, and how many files carried a status at all."""
    bad: list[str] = []
    seen = 0
    for folder in (ACTIVE, RULED, RECORDS):
        root = REPO / folder
        if not root.is_dir():
            bad.append(f"{folder}/ does not exist")
            continue
        for path in sorted(root.glob("*.md")):
            seen += 1
            line = status_line(path)
            rel = f"{folder}/{path.name}"
            forms = (OPEN, RULED_RE, RECORD, SUPERSEDED)
            if not any(form.match(line) for form in forms):
                bad.append(f"{rel}: first line is not a status line "
                           f"in one of the four forms -- {line[:70]!r}")
                continue
            if folder == ACTIVE and not OPEN.match(line):
                bad.append(f"{rel}: review/active/ holds only OPEN packets; "
                           f"this one says {line!r}. Move it to "
                           f"review/ruled/ or review/records/.")
            if folder in (RULED, RECORDS) and OPEN.match(line):
                bad.append(f"{rel}: {folder}/ holds finished work; this one "
                           f"says OPEN. Move it back to review/active/.")
    return bad, seen


def citing_files() -> list[Path]:
    out: list[Path] = []
    for name in CITING_FILES:
        if (REPO / name).is_file():
            out.append(REPO / name)
    for folder in CITING_ROOTS:
        root = REPO / folder
        if not root.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            rel = Path(dirpath).relative_to(REPO).as_posix()
            if any(rel == skip or rel.startswith(skip + "/")
                   for skip in CITING_SKIP):
                dirnames[:] = []
                continue
            for filename in filenames:
                if Path(filename).suffix.lower() in CITING_EXT:
                    out.append(Path(dirpath) / filename)
    return sorted(out)


def citations(text: str) -> list[tuple[str, int]]:
    """Every checkable `review/...` path in this text, with its line number."""
    out: list[tuple[str, int]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for match in CITATION.finditer(line):
            path = match.group(0)
            if match.start() and line[match.start() - 1] == ":":
                # `git show <tag-or-commit>:review/...` -- a path that left
                # HEAD on purpose, retrieved by ref (CLAUDE.md sec.History
                # retrieval). A prose colon is followed by a space.
                continue
            if any(ch in path for ch in "*{<"):
                continue                      # a glob or a template
            name = path.rsplit("/", 1)[-1]
            if "." not in name:
                continue                      # a directory, not a file
            if len(name) < 4:
                continue                      # a test fixture such as `x.md`
            out.append((path, number))
    return out


def check_citations() -> tuple[list[str], int]:
    bad: list[str] = []
    count = 0
    for path in citing_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if "review/" not in text:
            continue
        rel = path.relative_to(REPO).as_posix()
        if rel == SELF:
            continue
        for cited, number in citations(text):
            count += 1
            if not (REPO / cited).exists():
                bad.append(f"{rel}:{number}: cites {cited}, which does not "
                           f"exist. Point it at the file's new home, or at "
                           f"its commit in the `git show <commit>:<path>` "
                           f"form CLAUDE.md sec.History retrieval gives.")
    return bad, count


def self_test() -> list[str]:
    """The four forms parse, and the three rejections reject."""
    bad = []
    good = [
        "Status: OPEN (pick P5a)",
        "Status: RULED R220 2026-08-29",
        "Status: RULED (see RULINGS.md)",
        "Status: RECORD",
        "Status: SUPERSEDED by review/ruled/furina-reframe-2026-08-29.md",
    ]
    forms = (OPEN, RULED_RE, RECORD, SUPERSEDED)
    for line in good:
        if not any(form.match(line) for form in forms):
            bad.append(f"self-test: {line!r} should parse and does not")
    for line in ("Status: OPEN", "# A packet", "Status: RULED R220",
                 "Status: SUPERSEDED"):
        if any(form.match(line) for form in forms):
            bad.append(f"self-test: {line!r} should be rejected and is not")
    retrieval = "see `git show 1f07d94a:review/ruled/gone.md`"
    if [c for c, _ in citations(retrieval)]:
        bad.append("self-test: a git-show retrieval path must not be checked")
    tagged = "see `git show pre-simplification-2026-08-06:review/x/gone.md`"
    if [c for c, _ in citations(tagged)]:
        bad.append("self-test: a tag retrieval path must not be checked")
    if [c for c, _ in citations("under `review/active/*.md`")]:
        bad.append("self-test: a glob must not be checked")
    cited = [c for c, _ in citations("read `review/ruled/machinery.md` now")]
    if cited != ["review/ruled/machinery.md"]:
        bad.append(f"self-test: a plain citation must be checked, got {cited}")
    return bad


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        bad = self_test()
        for line in bad:
            print(line)
        print(f"self-test: {len(bad)} failure(s)")
        return 1 if bad else 0

    status_bad, status_seen = check_statuses()
    citation_bad, citation_seen = check_citations()
    for line in status_bad + citation_bad:
        print(line)

    active = sorted((REPO / ACTIVE).glob("*")) if (REPO / ACTIVE).is_dir() \
        else []
    print(f"scope: {status_seen} packet(s) across {ACTIVE}/, {RULED}/ and "
          f"{RECORDS}/; {citation_seen} review path(s) cited from live code "
          f"and docs")

    if not status_seen:
        print("VACUOUS: no packets were found at all. The directory names "
              "moved; this lint is reporting nothing, not health.")
        return 1
    if status_bad or citation_bad:
        print(f"\n{len(status_bad) + len(citation_bad)} finding(s).")
        return 1

    print(f"review-status OK: every packet says what it is, and every cited "
          f"review path exists.")
    if len(active) > ACTIVE_WARN:
        print(f"WARNING (not a failure): {ACTIVE}/ holds {len(active)} files, "
              f"over the {ACTIVE_WARN} a session can hold in its head. A "
              f"packet whose picks are answered belongs in {RULED}/; a "
              f"measurement belongs in {RECORDS}/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
