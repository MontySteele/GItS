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

4. DECLARED SHADOWS (`EB-322`). A prototype row that REWRITES a shipped row
   keeps the shipped row's printed name, and the arm hides the shipped one:
   it is substituted out of the pool, so one of the pair is reachable in a
   build. The row declares that by ending its `name:` with " (proto)", and
   this lint reads the suffix as the declaration rather than as a second
   name. What the suffix is NOT is a title:
   `tier0.content.loader.display_name` strips it in both engines, so the
   player sees the bare name -- which is why the lint has to know the rule.
   Without it a " (proto)" name would look unique here while printing the
   shipped row's exact title on the card face.

   The relaxation is narrow, and each half is a refusal:

     * a shadow coexists with AT MOST ONE live row of the bare name -- it
       shadows that row, and nothing else;
     * two shadows of one bare name still collide, because only one of them
       can be the rewrite;
     * two LIVE rows of one bare name still collide, exactly as before -- the
       suffix buys a rewrite a name, never a duplicate;
     * a shadow of a name no live row holds is a finding: it shadows nothing,
       so the suffix is only a suffix, and it would print a bare title this
       lint never checked.

   The reserved list (3) reads the BARE name, since that is the name the
   player would see.

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

#: `EB-322`. The shadow declaration, and the ONE place its spelling lives on
#: this side. `tier0.content.loader.PROTOTYPE_SHADOW_SUFFIX` is the same string
#: on the engines' side and `tier0/tests/test_prototype_surface.py` pins the
#: two against each other -- restated here rather than imported so this lint
#: keeps running as a bare script with no `PYTHONPATH`, which is how
#: `tools/run_lints.py` and the atlas both invoke it.
SHADOW_SUFFIX = " (proto)"

#: `EB-549`. THE SHADOW RULE HAD NO ROWS TO RULE ON.
#:
#: `EB-322` taught this lint what a ` (proto)` name means, and then no
#: invocation ever handed it a sheet holding one: `loader.DOCS_CARD_SHEETS` is
#: the shipped six, and every declared shadow lives on
#: `docs/prototype-surface.yaml`. So the rule was dead code and the Furina r13
#: seat met both halves of one -- `Kaeya -- Frostgnaw` as an 8-damage reward
#: card and as a 6-damage fetched one, `Dahlia -- Sacramental Shower` as an
#: Attack and as a Skill -- with the lint green throughout.
#:
#: THE SURFACE COMES IN SHADOW ROWS ONLY, and that is a scope rule rather than
#: a convenience. Most of the surface is a WHOLE-KIT swap: Klee's overhaul
#: replaces her entire offerable pool, so `proto_ko_pop` and the shipped `Pop!`
#: are the same card at two stages and no run can show both. Those rows declare
#: no shadow and are not in this namespace. A row that ends in ` (proto)` is
#: making the opposite claim -- "I rewrite ONE shipped row, and the arm hides
#: it" -- and that claim is exactly what this lint exists to check.
SHADOW_ONLY_SHEETS = ("prototype-surface.yaml",)

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

    # BARE name -> list of (kind, source, id, is_shadow). Keyed on the name
    # the PLAYER sees (`EB-322`), so a declared shadow and the row it shadows
    # meet here rather than passing each other as two unrelated strings.
    seen = {}
    for sheet in sheets:
        shadows_only = Path(sheet).name in SHADOW_ONLY_SHEETS
        for c in load_cards(sheet):
            name = c.get("name")
            if not name:
                continue
            shadow = name.endswith(SHADOW_SUFFIX)
            # `EB-549`: a whole-kit swap declares no shadow and is not in this
            # namespace -- see `SHADOW_ONLY_SHEETS`.
            if shadows_only and not shadow:
                continue
            bare = name[:-len(SHADOW_SUFFIX)] if shadow else name
            seen.setdefault(bare, []).append(
                ("card", Path(sheet).name, c.get("id", "?"), shadow))
    n_relics = 0
    for name, source in load_relic_names():
        n_relics += 1
        # A relic title is already the printed title; there is no shadow
        # channel on that side and a relic that spelled one would be printing
        # the suffix.
        seen.setdefault(name, []).append(("relic", source, "-", False))

    failed = False

    # 1 + 2 + 4. duplicates within and across kinds, shadows excepted.
    for name, uses in sorted(seen.items()):
        live = [u for u in uses if not u[3]]
        shadows = [u for u in uses if u[3]]
        if len(live) > 1:
            failed = True
            locs = ", ".join(f"{k} {s}:{i}" for k, s, i, _ in live)
            kinds = {k for k, _, _, _ in live}
            label = ("DUPLICATE NAME" if len(kinds) == 1
                     else "CROSS-KIND NAME COLLISION")
            print(f"{label}: {name!r} used by {len(live)} objects -> {locs}")
        if len(shadows) > 1:
            # Only one row can be THE rewrite of a shipped row; two both
            # claiming it print one title between them.
            failed = True
            locs = ", ".join(f"{k} {s}:{i}" for k, s, i, _ in shadows)
            print(f"DUPLICATE SHADOW: {len(shadows)} rows declare "
                  f"{name + SHADOW_SUFFIX!r} -> {locs}")
        if shadows and not live:
            # The suffix says "this rewrites the row of that name"; with no
            # such row it says nothing, and the title it prints -- the bare
            # name -- was never in this lint's namespace at all.
            failed = True
            locs = ", ".join(f"{k} {s}:{i}" for k, s, i, _ in shadows)
            print(f"SHADOW OF NOTHING: {name + SHADOW_SUFFIX!r} shadows "
                  f"{name!r}, which no row holds -> {locs}")

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
            offenders = [(k, s, i) for k, s, i, _ in uses if k != owner]
            if not offenders:
                continue
            failed = True
            locs = ", ".join(f"{k} {s}:{i}" for k, s, i in offenders)
            print(f"RESERVED NAME: {name!r} is taken by {src} "
                  f"-- used by {locs}")

    if not failed:
        n_cards = sum(1 for uses in seen.values() for k, _, _, _ in uses
                      if k == "card")
        print(f"OK: {n_cards} card + {n_relics} relic names unique across "
              f"{len(sheets)} sheet(s)"
              + (", reserved list honored" if reserved_path.exists() else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
