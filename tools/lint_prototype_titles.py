#!/usr/bin/env python3
"""No two rows on the prototype surface may print ONE TITLE.

WHY (`EB-581`, Kokomi r21 lane 1 (c) 1 and (c) 2). The coordinator granted
`proto_kurages_oath_memory` -- the `KURAGE_MEMORY` base kit's Power -- into a
`KOKOMI_OVERHAUL` run and the seat played two rounds around a card that could
not do anything, because the arm has no jellyfish memory for "whenever the
Bake-Kurage plays a card from its memory" to fire on. What made that COSTLY
rather than merely wrong is the second half: `proto_kk_kurages_oath`, the
arm's own starter Skill, prints the same title. Two prototype rows, one name,
and nothing on the seat's screen -- or in the grant line, or in the packet --
to say which was which.

`tools/lint_unique_names.py` COULD NOT SEE IT, and that is a scope gap rather
than a bug in that lint. Its `SHADOW_ONLY_SHEETS` rule reads the surface for
declared shadows only (` (proto)`), because most of the surface is a WHOLE-KIT
swap whose rows legitimately print shipped titles -- so a surface row with no
suffix is skipped there by construction. That rule is about a prototype row
against a SHIPPED one. This lint asks the other question: two rows on the
SURFACE, against each other.

THE TITLE, NOT THE SHEET NAME. `tier0.content.loader.display_name` strips the
` (proto)` shadow suffix in both engines and `gen_klee_cards` emits the
stripped form as the card's `("title", ...)`, so "Kurage's Oath (proto)" and
"Kurage's Oath" are ONE name on the card face. Comparing `name:` finds
nothing, which is exactly the state this row was found in.

THE ONE EXEMPTION IS DERIVED AND NOT CURATED, which is what keeps it from
going stale: a pair may share a title only where one of the two is a row an
arm of its own kit SUPERSEDES (`C.PROTOTYPE_ARM_SUPERSEDED`) -- one card at two
stages, on arms that cannot both be on. That map is the same one
`understudy.embark.check_arms` refuses a grant against, so the exemption here
and the refusal there are one fact; delete the refusal and this lint starts
finding the pairs again.

Usage: python tools/lint_prototype_titles.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tier0.content.loader import display_name        # noqa: E402

SURFACE = REPO / "docs" / "prototype-surface.yaml"



def superseded() -> dict[str, str]:
    """`{row id: the arm that supersedes it}` -- `C.PROTOTYPE_ARM_SUPERSEDED`,
    read through a function so the import stays local to the one caller."""
    from tier0 import constants as C

    return dict(C.PROTOTYPE_ARM_SUPERSEDED)


def rows(path: Path | None = None) -> list[dict]:
    # `SURFACE` read at CALL time and not bound as a default: the negative
    # test points this lint at a synthetic surface, and a default bound at
    # import would make that test assert about the real one.
    path = path or SURFACE
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(doc, dict):
        doc = doc.get("cards") or doc.get("rows") or []
    return [r for r in (doc or []) if isinstance(r, dict)]


def main() -> int:
    if not SURFACE.is_file():
        print(f"prototype surface not found: {SURFACE}. The lint would "
              f"otherwise pass by scanning nothing.")
        return 1

    retired = superseded()
    by_title: dict[str, list[str]] = defaultdict(list)
    for row in rows(SURFACE):
        name = row.get("name")
        cid = row.get("id")
        if not name or not cid:
            continue
        by_title[display_name(str(name))].append(str(cid))

    findings = 0
    exempted = 0
    for title, ids in sorted(by_title.items()):
        if len(ids) < 2:
            continue
        # EXACTLY ONE of the pair may be a superseded row. Two live rows under
        # one title is the finding; two SUPERSEDED rows would be two arms
        # claiming the same retirement, which is not a state any map declares.
        live = [i for i in ids if i not in retired]
        if len(ids) == 2 and len(live) == 1:
            exempted += 1
            continue
        findings += 1
        print(f"DUPLICATE TITLE: {title!r} is printed by {len(ids)} "
              f"prototype rows -> {', '.join(sorted(ids))}")

    if findings:
        print(f"{findings} finding(s). A prototype row's title is what the "
              f"seat reads on the card, in the grant line and in the packet; "
              f"two rows under one title is a grant nobody can check.")
        return 1
    print(f"prototype titles unique: {len(by_title)} title(s) over "
          f"{sum(len(v) for v in by_title.values())} row(s); {exempted} "
          f"pair(s) exempt because one half is a superseded arm's row "
          f"({len(retired)} such rows declared).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
