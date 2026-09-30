#!/usr/bin/env python3
"""No two cards one run can hold may differ only in punctuation.

WHY (2026-09-29, a Varka seat). The seat's deck held "Kaeya: Frostgnaw" (a
Knight in Varka's personal pool) and "Kaeya — Frostgnaw" (a Mondstadt
companion), and told them apart only from the reward list. Both other name
lints were green: `lint_unique_names` compares exact strings over the shipped
sheets (and the surface's declared shadows only), and `lint_prototype_titles`
compares exact titles on the surface. A colon against an em dash is two
strings to both, and one name to a player.

THE RULE. Normalise every name -- drop the " (proto)" shadow suffix and the
eighth note, turn colon, em dash, en dash and hyphen into spaces, collapse
whitespace, fold case -- and then no card in a character's OWN pool may share
a normalised name with a card any run can offer as a companion.

WHO OWNS A ROW:

  * a row with `personal_pool:` belongs to each character it names (Varka's
    Knights, Klee's personals);
  * otherwise a row on a `*-companions.yaml` sheet, or a surface row with a
    `nation:`, is a UNIVERSAL -- conservatively reachable in every run;
  * otherwise it is its sheet's character's (`*-cards.yaml`) or its
    `character:`'s (the surface).

Own rows are NOT compared with each other: most of the surface is a whole-kit
swap whose rows print shipped titles on purpose (`proto_ko_pop` and `Pop!` are
one card at two stages), and exact duplicates are `lint_unique_names`' and
`lint_prototype_titles`' question.

ALLOWED is shrink-only: an entry that no longer clashes is itself a finding,
so the list can only get shorter. It is empty.

Usage: python tools/lint_run_name_clashes.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from understudy.report import console_safe          # noqa: E402

DOCS = REPO / "docs"
CHARACTER_SHEETS = {"klee-cards.yaml": "klee", "furina-cards.yaml": "furina",
                    "kokomi-cards.yaml": "kokomi"}
COMPANION_SHEETS = ("mondstadt-companions.yaml", "fontaine-companions.yaml",
                    "inazuma-companions.yaml")
SURFACE = "prototype-surface.yaml"

#: Known clashes held open, as `(own row id, universal row id)`. SHRINK-ONLY:
#: a pair here that no longer clashes fails the lint. Add nothing.
ALLOWED: frozenset[tuple[str, str]] = frozenset()

SHADOW_SUFFIX = " (proto)"
_PUNCT = re.compile("[:—–\\-♪]")


def normalise(name: str) -> str:
    name = name.strip()
    if name.endswith(SHADOW_SUFFIX):
        name = name[:-len(SHADOW_SUFFIX)]
    return " ".join(_PUNCT.sub(" ", name).lower().split())


def _load(path: Path) -> list[dict]:
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(doc, dict):
        doc = doc.get("cards") or []
    return [r for r in (doc or []) if isinstance(r, dict)]


def sort_rows(sheets: dict[str, list[dict]]):
    """`({character: [row]}, [universal row])` from `{sheet file name: rows}`."""
    own: dict[str, list[dict]] = defaultdict(list)
    universal: list[dict] = []
    for sheet, rows in sheets.items():
        for row in rows:
            if not row.get("name") or not row.get("id"):
                continue
            pool = row.get("personal_pool")
            if pool:
                for ch in (pool if isinstance(pool, list) else [pool]):
                    own[str(ch)].append(row)
            elif sheet in COMPANION_SHEETS or (
                    sheet == SURFACE and row.get("nation")):
                universal.append(row)
            else:
                ch = CHARACTER_SHEETS.get(sheet) or row.get("character")
                if ch:
                    own[str(ch)].append(row)
    return own, universal


def clashes(sheets: dict[str, list[dict]]) -> list[tuple[str, dict, dict]]:
    """Every `(character, own row, universal row)` sharing a normalised name."""
    own, universal = sort_rows(sheets)
    by_name: dict[str, list[dict]] = defaultdict(list)
    for row in universal:
        by_name[normalise(str(row["name"]))].append(row)
    out = []
    for ch in sorted(own):
        for row in own[ch]:
            for other in by_name.get(normalise(str(row["name"])), ()):
                if other["id"] != row["id"]:
                    out.append((ch, row, other))
    return out


def read_sheets(docs: Path = DOCS) -> dict[str, list[dict]]:
    names = (*CHARACTER_SHEETS, *COMPANION_SHEETS, SURFACE)
    missing = [n for n in names if not (docs / n).is_file()]
    if missing:
        raise FileNotFoundError(
            f"sheet(s) not found: {missing}. The lint would otherwise pass by "
            f"scanning nothing.")
    return {n: _load(docs / n) for n in names}


def findings(sheets: dict[str, list[dict]],
             allowed: frozenset[tuple[str, str]] = ALLOWED) -> list[str]:
    out = []
    seen = set()
    for ch, row, other in clashes(sheets):
        pair = (str(row["id"]), str(other["id"]))
        seen.add(pair)
        if pair in allowed:
            continue
        out.append(f"NAME CLASH ({ch}): {row['name']!r} ({row['id']}) and "
                   f"{other['name']!r} ({other['id']}) differ only in "
                   f"punctuation or case")
    for pair in sorted(allowed - seen):
        out.append(f"STALE ALLOW-LIST ENTRY: {pair} no longer clashes; "
                   f"delete it (the list is shrink-only)")
    return out


def main() -> int:
    console_safe()
    sheets = read_sheets()
    found = findings(sheets)
    for line in found:
        print(line)
    if found:
        print(f"{len(found)} finding(s). Rename the character's own row; a "
              f"player cannot tell two cards apart by a colon.")
        return 1
    own, universal = sort_rows(sheets)
    print(f"run names distinct: {sum(len(v) for v in own.values())} own row(s) "
          f"over {len(own)} character(s) against {len(universal)} companion "
          f"row(s); {len(ALLOWED)} allow-listed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
