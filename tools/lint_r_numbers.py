"""One R/D namespace, frozen at the tag — no reuse, no citations from the future.

Successor to lint_ledger_numbers.py (retired 2026-08-06 with the DECISIONS
ledgers themselves; retrievable at tag pre-simplification-2026-08-06). That
tool asserted each `## R<n>` / `## D<n>` heading appeared in exactly one
ledger volume, exactly once. The ledgers are gone, but the namespace is not:
every number issued before the migration — R1..R121, D1..D15 — is frozen in
git history at the tag, and docs/current/ still cites those numbers as
provenance. New rulings land in commit messages ([USER]'s verbatim words per
CLAUDE.md), and the CEILINGS below are bumped in the same commit.

Two assertions, both answerable from a depth-1 clone with no tags fetched:

1. DECLARATIONS: a `## R<n>` / `## D<n>` heading in docs/current/ must be
   unique across the whole tree AND above the frozen ceiling — re-heading a
   retired number forks its meaning against the tag.
2. CITATIONS: an `R<n>` token in docs/current/ prose must not exceed the
   ceiling — either it cites a ruling that was never issued (typo), or a new
   ruling landed without its ceiling bump. Bump R_CEILING here in the ruling's
   own commit; two branches issuing "the next number" then collide on this
   constant instead of silently sharing it. (D citations are not
   ceiling-checked: bare `D<n>` tokens collide with sprint item ids like
   `AS2-D5`; D declarations are still guarded.)

Usage: python tools/lint_r_numbers.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = "docs/current"

# Highest number issued under each prefix. Frozen namespace below these lives
# at tag pre-simplification-2026-08-06; bump in the same commit as the ruling.
R_CEILING = 187
D_CEILING = 15

HEADING = re.compile(r"(?m)^##\s+([RD]\d+)\b")
R_TOKEN = re.compile(r"\bR(\d+)\b")


def pages() -> list[Path]:
    return sorted((REPO / DOCS).rglob("*.md"))


def findings() -> list[str]:
    out: list[str] = []
    declared: dict[str, list[str]] = collections.defaultdict(list)
    for page in pages():
        rel = page.relative_to(REPO).as_posix()
        text = page.read_text(encoding="utf-8")
        for m in HEADING.finditer(text):
            declared[m.group(1)].append(rel)
        for m in R_TOKEN.finditer(text):
            if int(m.group(1)) > R_CEILING:
                out.append(f"R{m.group(1)} cited in {rel} exceeds "
                           f"R_CEILING={R_CEILING} — unissued number, or a "
                           "ruling landed without its ceiling bump")
    for tok, files in sorted(declared.items(),
                             key=lambda kv: (kv[0][0], int(kv[0][1:]))):
        ceiling = R_CEILING if tok[0] == "R" else D_CEILING
        if int(tok[1:]) <= ceiling:
            out.append(f"{tok} re-declared as a heading in {', '.join(files)} "
                       "— that number is frozen at the tag")
        if len(files) > 1:
            out.append(f"{tok} declared {len(files)} times: "
                       + ", ".join(files))
    return out


def main() -> int:
    if not pages():
        print(f"r-numbers: no pages found under {DOCS}/")
        return 1
    bad = findings()
    if bad:
        print(f"r-numbers: {len(bad)} finding(s)")
        for b in bad:
            print(f"  {b}")
        return 1
    total = sum(
        len(R_TOKEN.findall(p.read_text(encoding="utf-8"))) for p in pages())
    print(f"r-numbers OK: {total} R-citations across {len(pages())} pages, "
          f"all within R1..R{R_CEILING}, no frozen number re-declared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
