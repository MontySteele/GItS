#!/usr/bin/env python3
"""Identifier-registry lint -- checks ADDITIONS, never the corpus.

Opened 2026-08-06 by the housekeeping sweep (Track X) of the "Strike the Set"
batch, alongside `docs/registry/identifiers.md`.

WHY IT IS DIFF-SHAPED, STATED SO IT IS NOT "FIXED" LATER
--------------------------------------------------------
The repo mints short codes freely and several tokens are already ambiguous:
seven independent namespaces mint a bare `G1`. Auditing the *corpus* against
the registry would mean every historical document fights this lint forever, for
zero benefit -- the collisions that exist are resolved by
`docs/registry/identifiers.md`, not by editing thirty sprint logs.

So the lint grandfathers everything present today via a committed baseline
snapshot (`docs/registry/known-identifiers.tsv`) and fails on exactly two
things:

  RULE 1 -- a NEW identifier (one not in the snapshot) appears in a tracked
            namespace and is not written down in `docs/registry/identifiers.md`.

  RULE 2 -- a NEW document (a file not in the snapshot's file list) uses a BARE
            `G<n>` whose number is minted by two or more namespaces in the
            registry's collision table, instead of the qualified form.

  RULE 3 -- a NEW document mints an OPEN-ITEM ROW outside the two homes an open
            item has: `docs/registry/user-queue.md` and `docs/dockets/`.
            Added 2026-08-06 by the docs diet (Track Z, Z-3), which retired
            five parallel registers into those two. See the registry's 16.

All three are cheap to satisfy: add the row, write `S4-G6` instead of `G6`, or
put the open item in the queue. The escape hatches are the markers

    identifier-registry: allow-bare      (RULE 2)
    open-items: allow-elsewhere          (RULE 3)

anywhere in the offending file. RULE 3 additionally exempts any document whose
lifecycle header (Z-1) says REFERENCE or ARCHIVED: a frozen record is allowed
to restate the history of an item it does not own.

Deletions are never an error. Re-use of an existing token in an existing file is
never an error. Better to under-flag than to make every future doc commit fight
the lint.

USAGE
-----
    python tools/lint_identifier_registry.py            # check (CI)
    python tools/lint_identifier_registry.py --update-baseline
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = REPO / "docs" / "registry" / "identifiers.md"
BASELINE = REPO / "docs" / "registry" / "known-identifiers.tsv"

# Directories swept. Markdown only, on purpose: code comments and design sheets
# carry historical inline labels that are self-qualifying in context
# ("G8 (Neap Tide v2.1)") and linting them would be pure noise.
SCAN_ROOTS = ("docs", "review")
# The archive volume (R-D ledger split, 2026-08-06) is scanned like the live
# ledger; missing-file entries are skipped, so this is safe pre- and post-split.
EXTRA_FILES = ("tier0/DECISIONS.md", "tier0/DECISIONS-archive-R39-R99.md",
               "klee-mod/DECISIONS.md", "README.md")

# The registry and its snapshot are the resolver; they name every token by
# construction and must not be scanned as if they minted them.
EXCLUDE = {
    "docs/registry/identifiers.md",
    "docs/registry/user-queue.md",
    "docs/registry/known-identifiers.tsv",
}

ALLOW_BARE_MARKER = "identifier-registry: allow-bare"
ALLOW_OPEN_ITEM_MARKER = "open-items: allow-elsewhere"

# RULE 3 -- the two homes an open item is allowed to live in.
OPEN_ITEM_HOMES = ("docs/registry/user-queue.md", "docs/dockets/")

# A lifecycle header (Z-1) of REFERENCE or ARCHIVED exempts a file: a frozen
# record restates history, it does not mint work.
FROZEN_LIFECYCLE = re.compile(r"\*\*Lifecycle:\s*(REFERENCE|ARCHIVED)\b")

# What "minting an open-item row" looks like. Deliberately narrow: the line must
# BE a row (a bullet or a table cell) and must carry a marker that declares the
# item open in this document. Prose that merely mentions an open question is not
# a row and is not flagged.
OPEN_ITEM_ROW = re.compile(
    r"(?mi)^\s*(?:[-*+]\s|\|)"          # a bullet or a table row
    r"(?=.*(?:"
    r"AWAITING\s+\[USER\]"              # the standing marker for an owed reply
    r"|\*\*OPEN\*\*"                    # the standing marker for an owed item
    r"|\bOPEN ITEM\b"
    r"|\bTODO\b"
    r"|\bNEEDS (?:A )?RULING\b"
    r"|\bSTILL OWED\b"
    r"))"
    r".*$"
)

# Tracked namespaces. Narrow, high-precision patterns -- a namespace earns a
# row here only when its tokens travel outside their minting document.
PATTERNS = {
    # gates and sprint task-ids of the G family, bare or qualified
    "gate": re.compile(r"(?<![A-Za-z0-9])((?:[A-Z][A-Z0-9]{0,4}-)?G-?\d{1,2})(?![0-9A-Za-z])"),
    # S13 exploit mechanism families
    "exploit": re.compile(r"(?<![A-Za-z0-9])(X\d{1,2})(?![0-9A-Za-z])"),
    # S14 non-card parity families
    "noncard": re.compile(r"(?<![A-Za-z0-9])(NC-\d{1,2})(?![0-9A-Za-z])"),
    # S1 card parity systemic families
    "systemic": re.compile(r"(?<![A-Za-z0-9])(SYS-\d{1,2})(?![0-9A-Za-z])"),
    # held flags
    "flag": re.compile(r"(?<![A-Za-z0-9])(FLAG-\d{1,2})(?![0-9A-Za-z])"),
}

# Ruling / D-series headings, mined only from the two ledgers' `## R12` form.
LEDGERS = ("tier0/DECISIONS.md", "tier0/DECISIONS-archive-R39-R99.md",
           "klee-mod/DECISIONS.md")
HEADING = re.compile(r"(?m)^##\s+(R\d+|D\d+)\b")


def rel(p: pathlib.Path) -> str:
    return p.relative_to(REPO).as_posix()


def scanned_files() -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for root in SCAN_ROOTS:
        base = REPO / root
        if base.exists():
            out.extend(sorted(base.rglob("*.md")))
    for name in EXTRA_FILES:
        p = REPO / name
        if p.exists():
            out.append(p)
    return [p for p in out if rel(p) not in EXCLUDE]


def harvest() -> tuple[set[tuple[str, str]], set[str]]:
    """Return ({(namespace, token)}, {scanned file paths})."""
    found: set[tuple[str, str]] = set()
    files: set[str] = set()
    for path in scanned_files():
        files.add(rel(path))
        text = path.read_text(encoding="utf-8", errors="replace")
        for ns, pat in PATTERNS.items():
            for m in pat.finditer(text):
                found.add((ns, m.group(1)))
    for name in LEDGERS:
        p = REPO / name
        if not p.exists():
            continue
        for m in HEADING.finditer(p.read_text(encoding="utf-8", errors="replace")):
            tok = m.group(1)
            found.add(("ruling" if tok[0] == "R" else "dseries", tok))
    return found, files


def load_baseline() -> tuple[set[tuple[str, str]], set[str]]:
    tokens: set[tuple[str, str]] = set()
    files: set[str] = set()
    if not BASELINE.exists():
        return tokens, files
    for line in BASELINE.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if parts[0] == "token" and len(parts) >= 3:
            tokens.add((parts[1], parts[2]))
        elif parts[0] == "file" and len(parts) >= 2:
            files.add(parts[1])
    return tokens, files


def write_baseline(tokens: set[tuple[str, str]], files: set[str]) -> None:
    lines = [
        "# GENERATED by tools/lint_identifier_registry.py --update-baseline.",
        "# Grandfathering snapshot: every identifier and every scanned file that",
        "# existed when the registry opened. The lint flags ADDITIONS to this set,",
        "# never the set itself. Do not hand-edit; regenerate.",
        "# kind\tnamespace-or-path\ttoken",
    ]
    for ns, tok in sorted(tokens):
        lines.append(f"token\t{ns}\t{tok}")
    for f in sorted(files):
        lines.append(f"file\t{f}")
    BASELINE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ambiguous_gate_numbers() -> set[str]:
    """Numbers minted by >=2 namespaces, read off the registry's own tables.

    A number counts as ambiguous when the registry writes two or more distinct
    qualified forms for it (`S4-G1`, `CC-G1`, `SS-G1`, ...). Derived rather than
    hardcoded so the collision table stays the single source of truth.
    """
    if not REGISTRY.exists():
        return set()
    text = REGISTRY.read_text(encoding="utf-8", errors="replace")
    by_number: dict[str, set[str]] = {}
    for m in re.finditer(r"(?<![A-Za-z0-9])([A-Z][A-Z0-9]{0,4})-G(\d{1,2})(?![0-9A-Za-z])", text):
        by_number.setdefault(m.group(2), set()).add(m.group(1))
    return {n for n, prefixes in by_number.items() if len(prefixes) >= 2}


def check() -> int:
    if not REGISTRY.exists():
        print(f"FAIL: {rel(REGISTRY)} is missing -- the registry is the resolver.")
        return 1

    registry_text = REGISTRY.read_text(encoding="utf-8", errors="replace")
    base_tokens, base_files = load_baseline()
    found, files = harvest()

    problems: list[str] = []

    # RULE 1 -- new identifiers must be registered.
    for ns, tok in sorted(found - base_tokens):
        pat = re.compile(rf"(?<![A-Za-z0-9]){re.escape(tok)}(?![0-9A-Za-z])")
        if not pat.search(registry_text):
            problems.append(
                f"RULE 1: new {ns} identifier `{tok}` is not in {rel(REGISTRY)}.\n"
                f"        Add a row for it (or, if it is not really an identifier, "
                f"rename it), then refresh the snapshot:\n"
                f"        python tools/lint_identifier_registry.py --update-baseline"
            )

    # RULE 2 -- new documents may not mint a bare ambiguous G-token.
    ambiguous = ambiguous_gate_numbers()
    bare = re.compile(r"(?<![A-Za-z0-9-])G-?(\d{1,2})(?![0-9A-Za-z])")
    for path_str in sorted(files - base_files):
        text = (REPO / path_str).read_text(encoding="utf-8", errors="replace")
        if ALLOW_BARE_MARKER in text:
            continue
        hits = sorted({m.group(1) for m in bare.finditer(text)} & ambiguous)
        if hits:
            joined = ", ".join(f"G{h}" for h in hits)
            problems.append(
                f"RULE 2: new document {path_str} uses bare {joined}, and those "
                f"numbers are minted by two or more namespaces.\n"
                f"        Use the qualified form (see {rel(REGISTRY)} 2.1), or add "
                f"the marker `{ALLOW_BARE_MARKER}` if the bare use is deliberate."
            )

    # RULE 3 -- new documents may not mint open-item rows outside queue/dockets.
    for path_str in sorted(files - base_files):
        if path_str.startswith(OPEN_ITEM_HOMES):
            continue
        text = (REPO / path_str).read_text(encoding="utf-8", errors="replace")
        if ALLOW_OPEN_ITEM_MARKER in text or FROZEN_LIFECYCLE.search(text):
            continue
        hits = [m.group(0).strip() for m in OPEN_ITEM_ROW.finditer(text)]
        if hits:
            shown = "\n".join(f"          {h[:110]}" for h in hits[:3])
            more = f"\n          ... and {len(hits) - 3} more" if len(hits) > 3 else ""
            problems.append(
                f"RULE 3: new document {path_str} mints {len(hits)} open-item "
                f"row(s), but an open item lives in "
                f"docs/registry/user-queue.md or docs/dockets/ (see "
                f"{rel(REGISTRY)} 16).\n{shown}{more}\n"
                f"        Move the row to the queue or a docket and point here "
                f"instead; or, if this document is a frozen record, give it the "
                f"REFERENCE/ARCHIVED lifecycle header; or add the marker "
                f"`{ALLOW_OPEN_ITEM_MARKER}`."
            )

    if problems:
        print("identifier-registry lint: FAIL\n")
        for p in problems:
            print(p + "\n")
        return 1

    print(
        f"identifier-registry lint: OK "
        f"({len(found)} identifiers over {len(files)} files; "
        f"{len(found - base_tokens)} new, all registered)"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--update-baseline",
        action="store_true",
        help="rewrite docs/registry/known-identifiers.tsv from the current tree",
    )
    args = ap.parse_args()
    if args.update_baseline:
        tokens, files = harvest()
        write_baseline(tokens, files)
        print(f"wrote {rel(BASELINE)}: {len(tokens)} identifiers, {len(files)} files")
        return 0
    return check()


if __name__ == "__main__":
    sys.exit(main())
