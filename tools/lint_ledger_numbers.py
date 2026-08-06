"""No duplicate R/D numbers across the DECISIONS volumes — one namespace.

Grew out of the CI `ledger` job's inline script (adopted 2026-07-27, Serenitea
Sweep II B1), which checked `tier0/DECISIONS.md` and `klee-mod/DECISIONS.md`
for duplicates PER FILE. Track R-D (Clear the Stage, 2026-08-06) split the
tier0 ledger into volumes (`tier0/DECISIONS-archive-R39-R99.md` + the live
file), which adds the failure mode the per-file check cannot see: the same
number headed in two volumes. So the scan widened to the globs
`tier0/DECISIONS*.md` + `klee-mod/DECISIONS*.md` and the assertion became
cross-file: a `## R<n>` / `## D<n>` heading appears in EXACTLY ONE volume,
exactly once. (The live file's volume-pointer block therefore must not
re-declare `## R<n>` headings — pointing is prose, not a heading.)

Numbering law unchanged: one shared R-sequence across ledgers
(`docs/registry/identifiers.md` §3), renumbering forbidden (charter §5).

Usage: python tools/lint_ledger_numbers.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

GLOBS = (("tier0", "DECISIONS*.md"), ("klee-mod", "DECISIONS*.md"))
HEADING = re.compile(r"(?m)^##\s+([RD]\d+)\b")


def volumes() -> list[Path]:
    out: list[Path] = []
    for d, pat in GLOBS:
        out.extend(sorted((REPO / d).glob(pat)))
    return out


def findings() -> list[str]:
    where: dict[str, list[str]] = collections.defaultdict(list)
    for vol in volumes():
        rel = vol.relative_to(REPO).as_posix()
        for m in HEADING.finditer(vol.read_text(encoding="utf-8")):
            where[m.group(1)].append(rel)
    out = []
    for tok, files in sorted(where.items(),
                             key=lambda kv: (kv[0][0], int(kv[0][1:]))):
        if len(files) > 1:
            out.append(f"{tok} declared {len(files)} times across volumes: "
                       + ", ".join(files))
    return out


def main() -> int:
    vols = volumes()
    if not vols:
        print("ledger-numbers: no DECISIONS volumes found")
        return 1
    bad = findings()
    if bad:
        print(f"ledger-numbers: {len(bad)} duplicate(s)")
        for b in bad:
            print(f"  {b}")
        return 1
    total = sum(
        len(HEADING.findall(v.read_text(encoding="utf-8"))) for v in vols)
    print(f"ledger-numbers OK: {total} R/D headings across "
          f"{len(vols)} volume(s), one namespace, no duplicates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
