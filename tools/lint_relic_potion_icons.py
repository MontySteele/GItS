#!/usr/bin/env python3
"""Every relic and potion this mod ships names an icon that art/plan.tsv produces.

THE DEFECT (found 2026-10-12, the missing-art census after "Ward and Sting are
missing card art"). Varka's seven arm relics and three potions shipped on
2026-10-01 with their icon paths wired -- `varka/relics/<slug>.png`,
`varka/potions/<slug>.png` -- and no art behind them. `KleePck.Path` answers
null for a file the pack does not hold, the getter falls back to the base
class, and the relics drew Ironclad's Burning Blood (`IconBaseName`) and the
potions the base potion for eleven days. No surface could say so:

  * `tools/art_coverage.py` and `tools/shipped_card_art.py` bill CARD
    portraits only.
  * `tools/lint_power_icons.py` covers powers.
  * `tools/art_ledger.py` reads `KleePck.Path("...")` literals; these paths are
    BUILT (`VarkaArmRelics.Icon(Slug)`, `ArmPotions.Image("varka", "...")`),
    and its computed-path section bills only files that already sit under a
    prefix, so a prefix with no file was invisible to it.
  * `KleePck.Path` logs "pck resource missing" once, into godot.log, on the
    machine that plays.

WHAT THIS CHECKS, with no art on the machine (so it runs in CI): every
concrete `CustomRelicModel` / `CustomPotionModel` subclass resolves to a pck
path, and every such path is the out-path of an `art/plan.tsv` row -- the one
tracked ledger of produced art. Klee's historical layout is honoured:
`klee/<surface>/x.png` is produced at `ImageGen/images/<surface>/x.png`
(tools/build_pck.ps1 copies it into the `klee` namespace).

The path is read from the class or its bases, in the four spellings the mod
uses: a literal `"ns/relics/x.png"` (or `/potions/`), a helper call
`Helper.Icon("slug")` whose helper is `"prefix/" + slug + ".png"`, a
`Slug => "x"` override under a base that calls `Helper.Icon(Slug)`, and
`ArmPotions.Image("character", "slug")`.

ICON_DEBT has the lint_power_icons semantics: a named, reasoned exception that
FAILS once it is no longer needed, so the set can only shrink. It is empty.

Run: python tools/lint_relic_potion_icons.py      (exit 1 with findings)
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "klee-mod" / "KleeCode"
ART_PLAN = REPO / "art" / "plan.tsv"

ROOTS = ("CustomRelicModel", "CustomPotionModel")

# Class name -> reason. Delete the row in the commit that gives it art.
ICON_DEBT: dict[str, str] = {}

CLASS = re.compile(
    r"^[ \t]*(?:public|internal)\s+(?P<mods>(?:sealed\s+|abstract\s+|static\s+|partial\s+)*)"
    r"class\s+(?P<name>\w+)\s*(?::\s*(?P<bases>[^{\r\n]+))?", re.M)
LITERAL = re.compile(r'"(?P<path>[a-z0-9_]+/(?:relics|potions)/[a-z0-9_]+\.png)"')
HELPER_DEF = re.compile(
    r'static\s+string\s+(?P<fn>\w+)\(\s*string\s+(?P<arg>\w+)\s*\)\s*=>\s*'
    r'"(?P<prefix>[a-z0-9_/]+/)"\s*\+\s*(?P=arg)\s*\+\s*"\.png"')
HELPER_CALL = re.compile(r'(?P<cls>\w+)\.(?P<fn>\w+)\(\s*"(?P<slug>[a-z0-9_]+)"\s*\)')
SLUG_CALL = re.compile(r'(?P<cls>\w+)\.(?P<fn>\w+)\(\s*Slug\s*\)')
SLUG_DEF = re.compile(r'Slug\s*=>\s*"(?P<slug>[a-z0-9_]+)"')
POTION_IMAGE = re.compile(
    r'\w+\.Image\(\s*"(?P<char>[a-z]+)"\s*,\s*"(?P<slug>[a-z0-9_]+)"\s*\)')


def classes(src: Path = SOURCE) -> dict[str, dict]:
    """name -> {bases, abstract, body, file}; body runs to the next class."""
    out: dict[str, dict] = {}
    for path in sorted(src.rglob("*.cs")):
        text = path.read_text(encoding="utf-8")
        hits = list(CLASS.finditer(text))
        for i, m in enumerate(hits):
            end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
            bases = [b.strip().split("<")[0]
                     for b in (m.group("bases") or "").split(",") if b.strip()]
            out[m.group("name")] = {
                "bases": bases, "abstract": "abstract" in m.group("mods"),
                "static": "static" in m.group("mods"),
                "body": text[m.start():end], "file": path,
            }
    return out


def helpers(known: dict[str, dict]) -> dict[tuple[str, str], str]:
    """(class, fn) -> path prefix, for every `"prefix/" + slug + ".png"`."""
    return {(name, h.group("fn")): h.group("prefix")
            for name, row in known.items()
            for h in HELPER_DEF.finditer(row["body"])}


def lineage(name: str, known: dict[str, dict]) -> list[str]:
    """The class, then its bases up the chain (first base only for a class)."""
    out, cur = [], name
    while cur in known and cur not in out:
        out.append(cur)
        cur = known[cur]["bases"][0] if known[cur]["bases"] else None
    return out


def root_of(name: str, known: dict[str, dict]) -> str | None:
    chain = lineage(name, known)
    last = known[chain[-1]]["bases"][:1] if chain else []
    return last[0] if last and last[0] in ROOTS else None


def icon_paths(name: str, known: dict[str, dict],
               helper_map: dict[tuple[str, str], str]) -> set[str]:
    """Every pck path the class (or its chain) asks for as its icon."""
    chain = lineage(name, known)
    paths: set[str] = set()
    slug = next((m.group("slug") for c in chain
                 if (m := SLUG_DEF.search(known[c]["body"]))), None)
    for c in chain:
        body = known[c]["body"]
        paths |= {m.group("path") for m in LITERAL.finditer(body)}
        for m in HELPER_CALL.finditer(body):
            prefix = helper_map.get((m.group("cls"), m.group("fn")))
            if prefix:
                paths.add(prefix + m.group("slug") + ".png")
        for m in POTION_IMAGE.finditer(body):
            paths.add(f"{m.group('char')}/potions/{m.group('slug')}.png")
        if slug:
            for m in SLUG_CALL.finditer(body):
                prefix = helper_map.get((m.group("cls"), m.group("fn")))
                if prefix:
                    paths.add(prefix + slug + ".png")
    return paths


def produced_at(pck_path: str) -> str:
    """The ImageGen out-path that build_pck.ps1 packs at `pck_path`."""
    ns, rest = pck_path.split("/", 1)
    if ns == "klee":
        return "ImageGen/images/" + rest
    return "ImageGen/images/" + pck_path


def planned_art(path: Path = ART_PLAN) -> set[str]:
    with path.open(encoding="utf-8", newline="") as fh:
        return {row[1].strip() for row in csv.reader(fh, delimiter="\t")
                if len(row) > 1 and not row[0].startswith("#") and row[1].strip()}


def findings(known: dict[str, dict] | None = None,
             plan: set[str] | None = None,
             debt: dict[str, str] | None = None) -> list[str]:
    known = classes() if known is None else known
    plan = planned_art() if plan is None else plan
    debt = ICON_DEBT if debt is None else debt
    helper_map = helpers(known)
    out: list[str] = []
    concrete = sorted(n for n, r in known.items()
                      if not r["abstract"] and not r["static"]
                      and root_of(n, known))
    for name in concrete:
        paths = icon_paths(name, known, helper_map)
        missing = sorted(p for p in paths if produced_at(p) not in plan)
        bad = (not paths) or bool(missing)
        if name in debt:
            if not bad:
                out.append(f"{name}: on ICON_DEBT but its icon is planned now "
                           f"-- delete the entry")
            continue
        rel = known[name]["file"].relative_to(REPO) if known[name]["file"].is_relative_to(REPO) else known[name]["file"]
        if not paths:
            out.append(f"{name} ({rel}): no icon path found -- it draws the "
                       f"base class's placeholder")
        for p in missing:
            out.append(f"{name} ({rel}): icon res://{p} has no art/plan.tsv "
                       f"row producing {produced_at(p)} -- it draws the base "
                       f"class's placeholder")
    for name in sorted(set(debt) - set(concrete)):
        out.append(f"{name}: on ICON_DEBT but no such relic or potion -- "
                   f"delete the entry")
    return out


def main() -> int:
    found = findings()
    for f in found:
        print("  " + f)
    known = classes()
    n = sum(1 for k, r in known.items()
            if not r["abstract"] and not r["static"] and root_of(k, known))
    print(f"relic/potion icons: {'OK' if not found else 'FAIL'} "
          f"({n} relic(s) and potion(s), {len(found)} finding(s))")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
