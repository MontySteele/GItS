#!/usr/bin/env python3
"""Doc-path citation lint -- every cited `docs/` path must RESOLVE.

Opened 2026-08-06 by R121 `Q20` ("agreed, MOVE-WITH-RESOLVER"), the ruling that
let Clear the Stage Track R-B move the 45 root REFERENCE files that an
append-only DECISIONS volume cites by path.

THE PROBLEM THIS EXISTS FOR
---------------------------
Rail 1: a frozen record is never rewritten. So when a ledger-cited document
moves, its ledger citation cannot be repointed -- the byte stays stale forever.
Before `Q20` the house answer was "then it does not move", which put 45 files
at the docs root permanently and the charter's `docs/*.md` <= 15 target out of
reach.

`Q20` chose the third option: move the file, leave the ledger byte alone, and
write the redirect down. This lint is the half that makes that safe.

  A cited path that EXISTS                                  -> green.
  A cited path that does NOT exist but resolves through the
  resolver table to a file that DOES exist                  -> green.
  A cited path that does not exist and has no resolver row  -> FAIL.
  A resolver row whose new path does not exist              -> FAIL.

The resolver table lives in `docs/registry/identifiers.md` section 17 and is
parsed from there. It is deliberately NOT duplicated in this file: the registry
is the single source of truth, and a mapping kept in two places is a mapping
that will disagree.

SCOPE
-----
Default: the DECISIONS volumes -- the frozen records the resolver exists for.
`--all` additionally sweeps `tools/`, which `tier0/tests/test_doc_citation_targets.py`
already covers by existence alone; the resolver makes that check survive a move
instead of breaking on one.

USAGE
-----
    python tools/lint_doc_citations.py          # ledgers (CI)
    python tools/lint_doc_citations.py --all    # ledgers + tools/
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = REPO / "docs" / "registry" / "identifiers.md"

LEDGERS = (
    "tier0/DECISIONS.md",
    "tier0/DECISIONS-archive-R39-R99.md",
    "klee-mod/DECISIONS.md",
)

# A path-shaped citation into docs/ or review/. Same shape the citation-graph
# extractor uses, so the two agree about what counts as a citation.
CITATION = re.compile(
    r"(?<![A-Za-z0-9_/.-])(?:docs|review)/[A-Za-z0-9_./-]+"
    r"\.(?:md|yaml|yml|tsv|json|txt|png|html)"
)

# One resolver row: | `old` | `new` | ... |. Anchored on the two backticked
# path cells so prose and the section's other tables cannot be mistaken for it.
RESOLVER_ROW = re.compile(
    r"^\|\s*`((?:docs|review)/[^`]+)`\s*\|\s*`((?:docs|review)/[^`]+)`\s*\|"
)

TRAILING = ".,;:)]}\"'`"


def load_resolver() -> dict[str, str]:
    """old path -> new path, read off `identifiers.md` section 17."""
    if not REGISTRY.exists():
        return {}
    text = REGISTRY.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"(?m)^##\s*17\.[^\n]*\n", text)
    if not m:
        return {}
    section = text[m.end():]
    nxt = re.search(r"(?m)^##\s", section)
    if nxt:
        section = section[: nxt.start()]
    out: dict[str, str] = {}
    for line in section.splitlines():
        row = RESOLVER_ROW.match(line.strip())
        if row:
            out[row.group(1)] = row.group(2)
    return out


def cited_paths(files: list[str]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for rel in files:
        p = REPO / rel
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in CITATION.finditer(text):
            out.setdefault(m.group(0).rstrip(TRAILING), set()).add(rel)
    return out


def tool_files() -> list[str]:
    return [p.relative_to(REPO).as_posix() for p in sorted((REPO / "tools").rglob("*.py"))]


def check(sweep_tools: bool) -> int:
    resolver = load_resolver()
    problems: list[str] = []

    if not resolver:
        problems.append(
            f"the resolver table is empty or unparseable in {REGISTRY.relative_to(REPO).as_posix()} "
            f"section 17 -- it is the single source of truth for moved doc paths."
        )

    # A resolver row that points at nothing is worse than no row at all.
    for old, new in sorted(resolver.items()):
        if not (REPO / new).exists():
            problems.append(
                f"resolver row `{old}` -> `{new}`: the NEW path does not exist.\n"
                f"        Fix the row (section 17) or restore the file; a resolver that "
                f"resolves to nothing is the failure this lint is for."
            )
        if (REPO / old).exists():
            problems.append(
                f"resolver row `{old}` -> `{new}`: the OLD path exists again.\n"
                f"        Two files now answer one citation. Remove the row, or move "
                f"the reoccupied path aside."
            )

    files = list(LEDGERS) + (tool_files() if sweep_tools else [])
    cited = cited_paths(files)
    resolved = 0
    for target, who in sorted(cited.items()):
        if (REPO / target).exists():
            continue
        if target in resolver:
            resolved += 1
            continue
        problems.append(
            f"`{target}` is cited by {', '.join(sorted(who))} and does not exist,\n"
            f"        and no row in {REGISTRY.relative_to(REPO).as_posix()} section 17 "
            f"resolves it.\n"
            f"        A paper pass moved or renamed it: add the resolver row in the "
            f"move commit (frozen citer), or repoint the citer (live citer)."
        )

    if problems:
        print("doc-citation lint: FAIL\n")
        for p in problems:
            print(p + "\n")
        return 1

    print(
        f"doc-citation lint: OK ({len(cited)} distinct doc paths cited from "
        f"{len(files)} file(s); {resolved} stale path(s) resolved through "
        f"{len(resolver)} resolver rows)"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all", action="store_true", help="also sweep tools/")
    args = ap.parse_args()
    return check(args.all)


if __name__ == "__main__":
    sys.exit(main())
