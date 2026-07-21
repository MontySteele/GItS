#!/usr/bin/env python3
"""Card display-name uniqueness lint.

Two guarantees:

1. INTERNAL uniqueness (automatic): no two cards across the mod's sheets
   may share a display `name`. This catches accidental collisions the
   moment a new card lands -- e.g. two "Grand Finale"s in different pools.

2. RESERVED names (opt-in): names listed in docs/reserved-card-names.txt
   (one per line, '#' comments allowed) are treated as taken by content
   OUTSIDE this repo -- the base game and other installed mods (Downfall's
   Silent, etc.). The repo cannot see those card lists, so this file is
   the hand-maintained record of known external collisions. A mod card
   whose name appears here fails the lint. Keep it curated; it is the only
   defense against a cross-mod name clash, which the engine resolves
   unpredictably.

Usage: lint_unique_names.py <sheet.yaml> [<sheet.yaml> ...]
Exit 0 = clean, 1 = collision(s) found (printed to stdout).
"""
import sys
from pathlib import Path

import yaml


def load_cards(path):
    doc = yaml.safe_load(open(path))
    cards = doc["cards"] if isinstance(doc, dict) and "cards" in doc else doc
    return cards or []


def main(argv):
    sheets = argv[1:]
    if not sheets:
        print("usage: lint_unique_names.py <sheet.yaml> [...]")
        return 2

    # name -> list of (sheet, id)
    seen = {}
    for sheet in sheets:
        for c in load_cards(sheet):
            name = c.get("name")
            if not name:
                continue
            seen.setdefault(name, []).append((Path(sheet).name, c.get("id", "?")))

    failed = False

    # 1. internal duplicates
    for name, uses in sorted(seen.items()):
        if len(uses) > 1:
            failed = True
            locs = ", ".join(f"{s}:{i}" for s, i in uses)
            print(f"DUPLICATE NAME: {name!r} used by {len(uses)} cards -> {locs}")

    # 2. reserved (external) names
    reserved_path = Path(__file__).resolve().parents[1] / "docs" / "reserved-card-names.txt"
    if reserved_path.exists():
        reserved = {}
        for raw in reserved_path.read_text().splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            # optional "Name | source" annotation
            nm = line.split("|", 1)[0].strip()
            src = line.split("|", 1)[1].strip() if "|" in line else "external"
            reserved[nm] = src
        for name, uses in sorted(seen.items()):
            if name in reserved:
                failed = True
                locs = ", ".join(f"{s}:{i}" for s, i in uses)
                print(f"RESERVED NAME: {name!r} is taken by {reserved[name]} "
                      f"-- used by {locs}")

    if not failed:
        total = sum(len(u) for u in seen.values())
        print(f"OK: {total} card names unique across {len(sheets)} sheet(s)"
              + (", reserved list honored" if reserved_path.exists() else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
