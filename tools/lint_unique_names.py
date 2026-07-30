#!/usr/bin/env python3
"""Player-facing display-name uniqueness lint.

THE NAMESPACE IS "NAMES THE PLAYER SEES", not "names in card sheets". That
distinction is the whole of R69 (2026-07-26). This lint used to read card
sheets only, and while it did, "Explosive Frags" was simultaneously a Klee
Rare Power card and Klee's Orobas relic upgrade -- two unrelated effects
under one name, both reachable in a single run, and the lint was green the
entire time. Relics were always in the namespace the lint was written to
protect; its SCOPE was just narrower than its PURPOSE.

Three guarantees:

1. INTERNAL uniqueness (automatic): no two cards across the mod's sheets
   may share a display `name`. This catches accidental collisions the
   moment a new card lands -- e.g. two "Grand Finale"s in different pools.

2. CROSS-KIND uniqueness (automatic, R69): no relic display name may
   collide with a card display name, or with another relic's. Relic names
   are read out of the C# `("title", "...")` localization entries, which is
   where they are actually defined -- there is no relic sheet to read, and
   a lint that checked a manifest instead of the emitted C# would be the
   one-layer-lint failure this repo has already been bitten by once.

3. RESERVED names (opt-in): names listed in docs/reserved-card-names.txt
   (one per line, '#' comments allowed) are treated as taken by content
   OUTSIDE this repo -- the base game and other installed mods (Downfall's
   Silent, etc.). The repo cannot see those card lists, so this file is
   the hand-maintained record of known external collisions. A mod card
   whose name appears here fails the lint. Keep it curated; it is the only
   defense against a cross-mod name clash, which the engine resolves
   unpredictably.

   R69 additionally reserves BOTH sides of a settled collision, annotated
   with which side owns it, so neither name can be re-minted on the other
   side of the card/relic line later. A reserved entry whose annotation
   names the owning kind is skipped for that kind and enforced for every
   other -- otherwise reserving "Dodoco Tales" would fail the very relic
   that legitimately holds it.

Usage: lint_unique_names.py <sheet.yaml> [<sheet.yaml> ...]
       (relic sources are found automatically under klee-mod/KleeCode)
Exit 0 = clean, 1 = collision(s) found (printed to stdout).
"""
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
RELIC_DIRS = (REPO / "klee-mod" / "KleeCode" / "Relics",)

#: `("title", "Some Name"),` inside a Localization initializer. Deliberately
#: matched on the literal rather than parsed: these files are hand-written C#
#: and a real parser is a dependency this lint does not need.
_TITLE_RE = re.compile(r'\(\s*"title"\s*,\s*"([^"]+)"\s*\)')


def load_cards(path):
    # encoding EXPLICIT and a context manager, the repo's standard idiom
    # (tools/lint_text_encoding.py enforces the first half): the sheets are
    # UTF-8, the Windows default is cp1252, and `Salon Debut`'s accented `e`
    # decodes to mojibake in a name this lint compares for UNIQUENESS -- a
    # mangled name is still unique, so the defect would land as a pass.
    with open(path, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    cards = doc["cards"] if isinstance(doc, dict) and "cards" in doc else doc
    return cards or []


def load_relic_names(dirs=RELIC_DIRS):
    """Relic display names, as (name, source) pairs.

    Reads the C# that ships, not a manifest describing it. If a relic
    directory is missing entirely the lint says so rather than reporting a
    clean run over zero files -- a gate that silently scans nothing is the
    §3.1/§3.7 failure class, and this repo has two of those already.
    """
    out = []
    for d in dirs:
        if not d.exists():
            raise FileNotFoundError(
                f"relic source directory not found: {d}. The lint would "
                f"otherwise pass by scanning nothing.")
        for path in sorted(d.rglob("*.cs")):
            text = path.read_text(encoding="utf-8")
            for m in _TITLE_RE.finditer(text):
                out.append((m.group(1), f"{path.name}"))
    return out


def main(argv):
    sheets = argv[1:]
    if not sheets:
        print("usage: lint_unique_names.py <sheet.yaml> [...]")
        return 2

    # name -> list of (kind, source, id)
    seen = {}
    for sheet in sheets:
        for c in load_cards(sheet):
            name = c.get("name")
            if not name:
                continue
            seen.setdefault(name, []).append(
                ("card", Path(sheet).name, c.get("id", "?")))
    n_relics = 0
    for name, source in load_relic_names():
        n_relics += 1
        seen.setdefault(name, []).append(("relic", source, "-"))

    failed = False

    # 1 + 2. duplicates within and across kinds.
    for name, uses in sorted(seen.items()):
        if len(uses) > 1:
            failed = True
            locs = ", ".join(f"{k} {s}:{i}" for k, s, i in uses)
            kinds = {k for k, _, _ in uses}
            label = ("DUPLICATE NAME" if len(kinds) == 1
                     else "CROSS-KIND NAME COLLISION")
            print(f"{label}: {name!r} used by {len(uses)} objects -> {locs}")

    # 3. reserved (external) names
    reserved_path = REPO / "docs" / "reserved-card-names.txt"
    if reserved_path.exists():
        reserved = {}
        for raw in reserved_path.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            # optional "Name | source" annotation
            nm = line.split("|", 1)[0].strip()
            src = line.split("|", 1)[1].strip() if "|" in line else "external"
            reserved[nm] = src
        for name, uses in sorted(seen.items()):
            if name not in reserved:
                continue
            src = reserved[name]
            # R69: an entry annotated "<kind>-owned" is reserved AGAINST every
            # other kind, not against its owner. Without this, reserving both
            # sides of a settled collision would fail the objects that
            # legitimately hold those names.
            owner = None
            for kind in ("card", "relic"):
                if f"{kind}-owned" in src:
                    owner = kind
            offenders = [(k, s, i) for k, s, i in uses if k != owner]
            if not offenders:
                continue
            failed = True
            locs = ", ".join(f"{k} {s}:{i}" for k, s, i in offenders)
            print(f"RESERVED NAME: {name!r} is taken by {src} "
                  f"-- used by {locs}")

    if not failed:
        n_cards = sum(1 for uses in seen.values() for k, _, _ in uses
                      if k == "card")
        print(f"OK: {n_cards} card + {n_relics} relic names unique across "
              f"{len(sheets)} sheet(s)"
              + (", reserved list honored" if reserved_path.exists() else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
