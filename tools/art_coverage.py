#!/usr/bin/env python3
"""Card-art coverage check (docs/furina-art-pass-requirements.md §9.5).

Reads the CANONICAL sheets -- never a prose bill -- and compares expected card
IDs to the PNG stems actually present in the output directories. Reports three
disjoint sets, because §11 turns on keeping them apart:

  COVERED  expected ID has a matching file
  MISSING  expected ID has no file          (the art bill)
  STALE    file has no expected ID          (never counted as coverage)

Born from a real defect. The §1/§7 prose bill in the requirements doc was
written against a stale reading of the output directory and disagreed with the
sheets on three counts at once:

  D1  dahlia_sacramental_shower was billed as missing ("never reached the
      final output directory"). It is present, 500x380 opaque RGBA, from the
      same 2026-07-21 14:04 batch as the six the doc DOES count. The bill's
      "22 missing companions" is 21, and the older 21-note in
      klee-mod/DECISIONS.md that §1 explicitly overrode was right.
  D2  albedo_solar_isotoma, durin_witchs_flame and nicole_celestial_gift sit
      in §7's "missing NORMAL Companion portraits" table but are rarity:rare
      (5-star, one card each). They need art; they are not normal rows, so
      they cannot reconcile against a 28-normal-row denominator.
  D3  the three Neuvillette Guest Stars are billed in §6 as a surface
      SEPARATE from the companion count, but they are ordinary rows in
      fontaine-companions.yaml -- so a sheet-driven check sees them twice.

D2 and D3 cancelled each other numerically (3 rares swapped in, 3 guest stars
dropped out), which is why the doc's arithmetic looked self-consistent while
being wrong in both directions. That is the whole argument for this file: the
bill is a DERIVED number and belongs to a tool, not to prose that drifts.

Standalone:  python tools/art_coverage.py            # report, exit 0
             python tools/art_coverage.py --strict   # missing => exit 1
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "ImageGen" / "images" / "cards"

# Canonical sheet -> (output dir, surface label). Order fixes report order.
SHEETS = [
    (ROOT / "docs" / "furina-cards.yaml", IMAGES / "furina", "Furina personal sheet"),
    (ROOT / "docs" / "mondstadt-companions.yaml", IMAGES / "companions", "Companions (Mondstadt/shared)"),
    (ROOT / "docs" / "fontaine-companions.yaml", IMAGES / "companions", "Companions (Fontaine)"),
]

# Tokens live in the runtime content tree and are mostly other characters'.
# rarity:token is the selector grammar (kickoff §3.1); `confiscated` is
# rarity:status and is Klee's, so this predicate picks out exactly Furina's
# Ethereal Spotlight without hardcoding its id.
TOKENS = ROOT / "tier0" / "content" / "cards" / "tokens.yaml"

# KNOWN-set pattern (as in tools/art_lint.py): a stale file with a reason on
# record is a NOTE, not a failure. Never prune an entry without a new reason.
KNOWN_STALE = {
    # Printed strings stay ASCII: this runs on a cp1252 Windows console, where
    # a section sign comes out as a replacement char.
    "xingqiu_raincutter": (
        "predates the current Companion sheets; Xingqiu is not a roster row. "
        "Requirements sec.1 calls it out explicitly. Harmless on disk, but it "
        "must never be read as coverage."
    ),
}


def sheet_rows(path):
    """Every card row in a flat card-list sheet, in file order."""
    rows = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [r for r in rows if isinstance(r, dict) and "id" in r]


def token_rows(path):
    rows = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [r for r in rows if isinstance(r, dict) and r.get("rarity") == "token"]


# Two different groupings, because the two surfaces are reviewed differently
# (§10). Companions group by CHARACTER -- that is the §9.3 source_group axis and
# the only way sibling crop differentiation gets reviewed together. Furina's own
# cards group by RARITY: `archetypes` is a LIST on the sheet (a third of the
# rows carry two), so the doc's clean per-archetype tables are an editorial
# review split, not a derivable field. Rarity is unambiguous and matches the
# §4 directive that rares get the most generous crop review.
def group_key(row, by):
    if by == "character":
        return row["id"].split("_", 1)[0]
    return row.get("rarity", "?")


RARITY_ORDER = {"basic": 0, "common": 1, "uncommon": 2, "rare": 3, "token": 4}


def stems(directory):
    if not directory.is_dir():
        return set()
    return {p.stem for p in directory.glob("*.png")}


def main():
    strict = "--strict" in sys.argv

    surfaces = []
    for path, outdir, label in SHEETS:
        by = "character" if "companions" in path.name else "rarity"
        surfaces.append((label, outdir, sheet_rows(path), by))
    surfaces.insert(1, ("Furina token", IMAGES / "furina", token_rows(TOKENS), "rarity"))

    all_expected = {}          # outdir -> set of expected ids
    total_expected = total_covered = 0
    missing_by_surface = []

    print("=" * 72)
    print("CARD-ART COVERAGE  (source of truth: canonical YAML sheets)")
    print("=" * 72)

    for label, outdir, rows, by in surfaces:
        present = stems(outdir)
        all_expected.setdefault(outdir, set()).update(r["id"] for r in rows)
        covered = [r for r in rows if r["id"] in present]
        missing = [r for r in rows if r["id"] not in present]
        total_expected += len(rows)
        total_covered += len(covered)
        if missing:
            missing_by_surface.append((label, missing, by))
        print(f"\n{label}")
        print(f"  expected {len(rows):3d}   covered {len(covered):3d}   missing {len(missing):3d}")
        if covered:
            print(f"  have: {', '.join(sorted(r['id'] for r in covered))}")

    print("\n" + "-" * 72)
    print("MISSING (the art bill)")
    print("-" * 72)
    for label, missing, by in missing_by_surface:
        print(f"\n{label} -- {len(missing)}  (by {by})")
        groups = {}
        for r in missing:
            groups.setdefault(group_key(r, by), []).append(r["id"])
        order = (lambda k: (RARITY_ORDER.get(k, 9), k)) if by == "rarity" else (lambda k: k)
        for key in sorted(groups, key=order):
            ids = sorted(groups[key])
            print(f"  {key:12s} {len(ids):3d}  {', '.join(ids)}")

    print("\n" + "-" * 72)
    print("STALE (files with no sheet row -- NOT coverage)")
    print("-" * 72)
    unknown_stale = []
    for outdir, expected in all_expected.items():
        for s in sorted(stems(outdir) - expected):
            if s in KNOWN_STALE:
                print(f"  [known] {s}.png -- {KNOWN_STALE[s]}")
            else:
                print(f"  [NEW]   {s}.png in {outdir.relative_to(ROOT)}")
                unknown_stale.append(s)

    total_missing = total_expected - total_covered
    print("\n" + "=" * 72)
    print(f"TOTAL card-sized outputs expected: {total_expected}")
    print(f"  covered: {total_covered}    missing: {total_missing}")
    print("=" * 72)

    if unknown_stale:
        print(f"\nFAIL: {len(unknown_stale)} unrecorded stale file(s); add a KNOWN_STALE reason or delete.")
        return 1
    if strict and total_missing:
        print(f"\nFAIL (--strict): {total_missing} missing output(s).")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
