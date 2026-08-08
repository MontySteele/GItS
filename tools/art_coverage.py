#!/usr/bin/env python3
"""Card-art coverage check, ROSTER-WIDE (docs/furina-art-pass-requirements.md §9.5).

Started as Furina's instrument; it now bills the whole roster, because the
question "what art do we still owe" stopped being a one-character question
the moment a second character shipped on borrowed assets.

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

  D4  the sheets are not the whole shipped set. A card can ship in C# with a
      portrait request and no sheet row at all -- and this tool, billing from
      the sheets alone, could not see it: not COVERED, not MISSING, not even
      STALE. Three cards shipped the BETA placeholder that way
      (missed-requirements sec.4.1): `spotlight_center_stage` and
      `spotlight_guest_cast`, the C#-only halves of Furina's selector, plus
      `confiscated`, which HAS a tokens.yaml row but is rarity:status and so
      fell through the rarity:token filter below. "Art bill 0 missing" and
      "all 78 portraits resolve" were both true while three cards rendered a
      placeholder. Fixed by adding a second universe -- every art key the
      shipped mod actually asks for (MOD_SRC) -- and billing the keys the
      sheet surfaces do not already expect. The bill is still derived: the
      keys are read out of the C# that requests them, never listed here.

Standalone:  python tools/art_coverage.py            # report, exit 0
             python tools/art_coverage.py --strict   # missing => exit 1
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "ImageGen" / "images" / "cards"

# Canonical sheet -> (output dir, surface label). Order fixes report order.
SHEETS = [
    (ROOT / "docs" / "klee-cards.yaml", IMAGES / "klee", "Klee personal sheet"),
    (ROOT / "docs" / "furina-cards.yaml", IMAGES / "furina", "Furina personal sheet"),
    # Kokomi joined 2026-07-25, at zero coverage. Listing a surface with no
    # files yet is the entire point of an instrument like this: her shell
    # ships on Klee's art via the pck builder's fallback, which means the
    # game LOOKS finished and the bill is invisible everywhere except here.
    (ROOT / "docs" / "kokomi-cards.yaml", IMAGES / "kokomi", "Kokomi personal sheet"),
    (ROOT / "docs" / "inazuma-companions.yaml", IMAGES / "companions", "Companions (Inazuma)"),
    (ROOT / "docs" / "mondstadt-companions.yaml", IMAGES / "companions", "Companions (Mondstadt/shared)"),
    (ROOT / "docs" / "fontaine-companions.yaml", IMAGES / "companions", "Companions (Fontaine)"),
]

# Tokens live in the runtime content tree and are mostly other characters'.
# rarity:token is the selector grammar (kickoff §3.1); `confiscated` is
# rarity:status and is Klee's, so this predicate picks out exactly Furina's
# Ethereal Spotlight without hardcoding its id.
TOKENS = ROOT / "tier0" / "content" / "cards" / "tokens.yaml"

# D4's second universe. RosterArt.CardPortrait("<id>") is the ONE way a card
# asks for a portrait at runtime (klee-mod/KleeCode/KleeArt.cs), so the set of
# literal keys in the mod source is exactly the set of art the game will try to
# load -- generated cards, hand-written cards and C#-only tokens alike. Keys
# the sheet surfaces already expect are billed there; the remainder is the
# surface that used to be invisible.
MOD_SRC = ROOT / "klee-mod" / "KleeCode"
ART_KEY_RE = re.compile(r"Art\.CardPortrait\(\"([a-z0-9_]+)\"\)")

# Deploy stages every character's card dir into ONE flat images/cards next to
# the dll (klee-mod/build/deploy.ps1), keyed by id, and ids are unique across
# the sheets (tools/lint_unique_names.py gates that). So for a card with no
# sheet row there is no "its" output dir: a png with that stem in ANY of the
# staged dirs is the art that ships. Derived from SHEETS rather than relisted,
# so a new character's dir cannot be added in one place and missed here.
CARD_DIRS = tuple(dict.fromkeys(outdir for _p, outdir, _l in SHEETS))

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
    "swift_currents": (
        "G8 (Neap Tide v2.1) MERGED this card into moonlit_offering, which "
        "keeps its own art. Kept rather than deleted because the merge is one "
        "ruling old and the pool has an open art debt -- if the velocity Rare "
        "is ever split back out, or another Sly piece wants a current motif, "
        "this is a painted asset already cleared through SOURCES.tsv. It is "
        "NOT coverage for anything and must never be counted as such. "
        "CONSIDERED AND REJECTED 2026-07-29 (Track A): it is a KOKOMI chibi "
        "sticker on a kokomi/ out-path -- a different character. No crop of "
        "it can serve a Furina card, so the 'current motif' framing above "
        "only ever applied to a future KOKOMI row."
    ),
    "rising_tide": (
        "A4 (playtest-2 red-pen, 2026-07-28) CUT Rising Tide from the pool: "
        "pure application + buffer at common, an effect the deploy cards "
        "already carry as a rider. Kept rather than deleted because it is a "
        "painted asset already cleared through SOURCES.tsv and the pool "
        "carries an open art debt -- if a salon application common is ever "
        "re-authored, the motif is on disk. It is "
        "NOT coverage for anything and must never be counted as such. "
        "CONSIDERED AND REJECTED 2026-07-29 (Track A): the brief offered it "
        "as a re-crop for casting_call or take_your_bow. Opened it. THE "
        "LEDGER DESCRIPTION WAS WRONG -- 'water climbing the stage' describes "
        "the plan's INTENT, not the shipped bytes, which are 'A Wish For "
        "Smooth Sailing Quest Still 2': a chibi resort-map panorama with a "
        "dozen small figures and no Furina focus. Wrong voice for either "
        "salon card and a multi-figure scene besides. The note above is "
        "corrected accordingly; a ledger that describes a file it has not "
        "looked at is worse than no ledger."
    ),
}


def sheet_rows(path):
    """Every card row in a flat card-list sheet, in file order."""
    rows = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [r for r in rows if isinstance(r, dict) and "id" in r]


def token_rows(path):
    rows = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [r for r in rows if isinstance(r, dict) and r.get("rarity") == "token"]


def mod_art_keys(src=MOD_SRC):
    """id -> the C# file that asks for it, for every literal portrait request.

    Deliberately literal-only: the single non-literal call site is the
    definition in KleeArt.cs (`CardPortrait(cardId)`), which requests nothing.
    Missing tree (a clone without the mod) is an empty universe, not a crash --
    the sheet surfaces still bill.
    """
    keys = {}
    if not src.is_dir():
        return keys
    for path in sorted(src.rglob("*.cs")):
        text = path.read_text(encoding="utf-8")
        for match in ART_KEY_RE.finditer(text):
            keys.setdefault(match.group(1), path)
    return keys


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
    if by == "source":
        # D4 rows have no sheet and therefore no rarity; the C# file that asks
        # for the art is the only grouping that means anything for them, and it
        # is also the thing a reader has to open next.
        return row["source"]
    return row.get("rarity", "?")


RARITY_ORDER = {"basic": 0, "common": 1, "uncommon": 2, "rare": 3, "token": 4}


def stems(directory):
    if not directory.is_dir():
        return set()
    return {p.stem for p in directory.glob("*.png")}


def main():
    strict = "--strict" in sys.argv

    surfaces = []              # (label, outdirs, rows, grouping)
    for path, outdir, label in SHEETS:
        by = "character" if "companions" in path.name else "rarity"
        surfaces.append((label, (outdir,), sheet_rows(path), by))
    surfaces.insert(1, ("Furina token", (IMAGES / "furina",), token_rows(TOKENS), "rarity"))

    # D4: everything the shipped mod asks for that no sheet surface expects.
    # Computed after the sheet surfaces so the subtraction is against the real
    # expected set, which is what makes `confiscated` -- a tokens.yaml row the
    # rarity:token filter drops -- land here instead of vanishing.
    from_sheets = {r["id"] for _l, _d, rows, _b in surfaces for r in rows}
    extra_rows = [{"id": key, "source": str(path.relative_to(ROOT))}
                  for key, path in sorted(mod_art_keys().items())
                  if key not in from_sheets]
    if extra_rows:
        surfaces.append(("Shipped in C# with no sheet row (mod art keys)",
                         CARD_DIRS, extra_rows, "source"))

    all_expected = {}          # outdir -> set of expected ids
    total_expected = total_covered = 0
    missing_by_surface = []

    print("=" * 72)
    print("CARD-ART COVERAGE  (source of truth: canonical YAML sheets + mod art keys)")
    print("=" * 72)

    for label, outdirs, rows, by in surfaces:
        present = set().union(*(stems(d) for d in outdirs))
        for outdir in outdirs:
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
