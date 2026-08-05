"""Every clause-bearing R-number citation in `canon_role_tempo.py` must resolve.

WHY THIS IS A LINT AND NOT FIVE MORE EDITS
------------------------------------------
S4 finding F14 caught ONE wrong citation: the generated header of
`docs/role-tempo-floors.yaml` cited "R91/1c" for a clause that is R90's. R107
fixed that one. The surplus-week sweep then found the generator carrying the
SAME misattribution in four more places -- one comment, one docstring, and two
strings the generator writes into `docs/role-tempo-baseline.md`. Five instances
of one defect, produced by one file, none of them catchable by any existing
check: `lint_text_encoding` reads calls, `lint_constant_parity` reads numbers,
and no instrument in the repo reads a citation.

That is the house pattern for a structurally invisible defect, at the count
where it graduates: the human catch becomes a curated check that runs. Prose is
where a stale citation does its damage -- someone resolving "R91/1c" lands on
the tag-review ruling, reads clauses 2a-2d, finds nothing about packages, and
either guesses or gives up.

WHAT IT CHECKS, AND THE NARROWNESS IS DELIBERATE
------------------------------------------------
Scope is exactly ONE file (`TARGET`). This is not a repo-wide citation checker
and must not quietly become one: the same misattribution is live in
`tools/lint_role_tempo_coverage.py` and in the generated
`docs/role-tempo-baseline.md`, and widening the scope to sweep them is a
separate decision that has not been taken. A lint whose scope grew by accident
is a lint nobody can reason about.

Within that file it checks CLAUSE-BEARING citations only, in the two forms the
file actually writes:

    R90/1c            R91 (Ruling 1c)

A citation resolves when (1) `tier0/DECISIONS.md` has an entry `## R<n> ...`
and (2) that entry's body declares the clause, in DECISIONS' own clause idiom
`**<clause> --`. A BARE ruling reference with no clause ("R91 leaves that
designation standing") is NOT checked: whether a ruling supports a paraphrase
is a reading, and a lint that tried to judge it would be inventing authority.
Clause presence is a fact about the text, which is the only thing worth
asserting mechanically.

Usage: python tools/lint_r_citations.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DECISIONS = REPO / "tier0" / "DECISIONS.md"
TARGET = REPO / "tools" / "canon_role_tempo.py"

# `## R90 -- ...` opens an entry; the next `## ` closes it.
_ENTRY = re.compile(r"^##\s+R(\d+)\b", re.M)

# The two citation shapes this file writes. Both capture (number, clause).
_CITES = (
    re.compile(r"R(\d+)\s*/\s*(\d[a-z])"),
    re.compile(r"R(\d+)\s*\(\s*Ruling\s+(\d[a-z])\s*\)"),
)


def _entries(text: str) -> dict[str, str]:
    """R-number -> that entry's body text, headings excluded from the next one."""
    bounds = [(m.group(1), m.start()) for m in _ENTRY.finditer(text)]
    heads = [m.start() for m in re.finditer(r"^##\s", text, re.M)]
    out: dict[str, str] = {}
    for number, start in bounds:
        later = [h for h in heads if h > start]
        end = later[0] if later else len(text)
        # A number can be headed twice (a DRAFT and its countersign); keep the
        # union so a clause declared in either half resolves.
        out[number] = out.get(number, "") + text[start:end]
    return out


def _declares(body: str, clause: str) -> bool:
    """DECISIONS' clause idiom: bolded marker, then a dash."""
    return bool(re.search(r"\*\*\s*" + re.escape(clause) + r"\s*(--|—)", body))


def main() -> int:
    entries = _entries(DECISIONS.read_text(encoding="utf-8"))
    src = TARGET.read_text(encoding="utf-8").splitlines()

    seen: set[tuple[int, str, str]] = set()
    findings: list[str] = []
    checked = 0
    for lineno, line in enumerate(src, 1):
        for pattern in _CITES:
            for number, clause in pattern.findall(line):
                key = (lineno, number, clause)
                if key in seen:
                    continue
                seen.add(key)
                checked += 1
                body = entries.get(number)
                if body is None:
                    findings.append(
                        f"{TARGET.name}:{lineno}: cites R{number}/{clause}, but "
                        f"tier0/DECISIONS.md has no entry R{number}")
                elif not _declares(body, clause):
                    owners = sorted(
                        n for n, b in entries.items() if _declares(b, clause))
                    hint = (f" -- clause {clause} is declared by "
                            f"{', '.join('R' + o for o in owners)}"
                            if owners else
                            f" -- no entry declares a clause {clause}")
                    findings.append(
                        f"{TARGET.name}:{lineno}: cites R{number}/{clause}, but "
                        f"R{number} declares no clause {clause}{hint}")

    if findings:
        print(f"R-citations: {len(findings)} finding(s)")
        for finding in findings:
            print(f"  {finding}")
        return 1

    print(f"R-citations OK: {checked} clause-bearing citation(s) in "
          f"{TARGET.relative_to(REPO)} resolve against tier0/DECISIONS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
