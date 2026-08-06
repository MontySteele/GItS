"""Every clause-bearing R-number citation in `tools/*.py` must resolve.

WHY THIS IS A LINT AND NOT FIVE MORE EDITS
------------------------------------------
S4 finding F14 caught ONE wrong citation: the generated header of
`docs/role-tempo-floors.yaml` cited R91 for clause 1c, a clause that is R90's.
R107 fixed that one. (The defect is spelled out in words here rather than in
citation form, because since the Q15 widening this file sweeps itself and a
verbatim bad example would be its own finding.) The surplus-week sweep then found the generator carrying the
SAME misattribution in four more places -- one comment, one docstring, and two
strings the generator writes into `docs/role-tempo-baseline.md`. Five instances
of one defect, produced by one file, none of them catchable by any existing
check: `lint_text_encoding` reads calls, `lint_constant_parity` reads numbers,
and no instrument in the repo reads a citation.

That is the house pattern for a structurally invisible defect, at the count
where it graduates: the human catch becomes a curated check that runs. Prose is
where a stale citation does its damage -- someone resolving the bad citation
(R91, clause 1c) lands on the tag-review ruling, reads clauses 2a-2d, finds
nothing about packages, and either guesses or gives up.

WHAT IT CHECKS, AND HOW THE SCOPE GOT HERE
------------------------------------------
Scope is `tools/*.py` (non-recursive, the queue row's own words). It began as
exactly ONE file (`canon_role_tempo.py`), deliberately: the same
misattribution was known to be live in `tools/lint_role_tempo_coverage.py`,
and widening a lint's scope is a decision, not a repair. That decision was
then taken: **WIDENED 2026-08-06 per Q15 (R117, verbatim "15) Widen")** — the
sweep extends to `tools/*.py` and the three occurrences in
`lint_role_tempo_coverage.py` were repaired to satisfy it, comments and
docstrings only. A lint whose scope grew by accident is a lint nobody can
reason about; this one's growth is on the record.

Within those files it checks CLAUSE-BEARING citations only, in the two forms
the tools actually write:

    R90/1c            R90 (Ruling 1c)

A citation resolves when (1) a tier0 DECISIONS volume has an entry `## R<n> ...`
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


def _decision_volumes() -> list[Path]:
    """Every tier0 DECISIONS volume. A glob, not a single path, since the R-D
    ledger split (2026-08-06, `docs/registry/ledger-layout-note-2026-08-06.md`):
    R39-R99 live in `tier0/DECISIONS-archive-R39-R99.md`, R100+ in the live
    file, and the citations this lint checks (R90/1c and kin) are mostly in
    the archive range -- so the resolver reads BOTH files, one namespace."""
    return sorted((REPO / "tier0").glob("DECISIONS*.md"))


def _targets() -> list[Path]:
    """`tools/*.py`, non-recursive (Q15's own scope wording) -- the archive
    subdirectory holds retired tools and stays out, exactly as a shell glob
    would leave it. This file sweeps itself: its own docstring examples must
    resolve like anyone else's."""
    return sorted((REPO / "tools").glob("*.py"))

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
    entries: dict[str, str] = {}
    for volume in _decision_volumes():
        for number, body in _entries(volume.read_text(encoding="utf-8")).items():
            # Union across volumes, same reason as within one: a clause
            # declared in either half of a twice-headed number must resolve.
            entries[number] = entries.get(number, "") + body

    targets = _targets()
    findings: list[str] = []
    checked = 0
    for target in targets:
        src = target.read_text(encoding="utf-8").splitlines()
        seen: set[tuple[int, str, str]] = set()
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
                            f"{target.name}:{lineno}: cites "
                            f"R{number}/{clause}, but no tier0 DECISIONS "
                            f"volume has an entry R{number}")
                    elif not _declares(body, clause):
                        owners = sorted(
                            n for n, b in entries.items()
                            if _declares(b, clause))
                        hint = (f" -- clause {clause} is declared by "
                                f"{', '.join('R' + o for o in owners)}"
                                if owners else
                                f" -- no entry declares a clause {clause}")
                        findings.append(
                            f"{target.name}:{lineno}: cites "
                            f"R{number}/{clause}, but R{number} declares no "
                            f"clause {clause}{hint}")

    if findings:
        print(f"R-citations: {len(findings)} finding(s)")
        for finding in findings:
            print(f"  {finding}")
        return 1

    print(f"R-citations OK: {checked} clause-bearing citation(s) across "
          f"{len(targets)} file(s) in tools/*.py resolve against "
          f"the tier0 DECISIONS volumes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
