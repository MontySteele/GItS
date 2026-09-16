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

  D5  a row saying `art_of: <neighbour>` wears that neighbour's illustration,
      so the generator emits the NEIGHBOUR's key and the row's own id is
      requested by nothing. It is not COVERED, not MISSING and not STALE --
      D4's blind spot one seam over, and D4's fix cannot reach it, because
      that fix reads the keys the mod asks for and a proxy asks for someone
      else's. Coven Errand, Witches' Circle and Alice's Introduction Magic
      (EB-326's three) have worn a neighbour since 2026-09-02 and no surface
      has ever said so. Fixed by a third section -- a BILL, not a failure:
      wearing a neighbour is a sanctioned stand-in, and the defect was that
      the debt was unsayable rather than that it existed. See `art_of_proxies`.

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
    "proto_ko_fwoosh": (
        "R271 (2026-09-14) CUT Fwoosh! from the Klee overhaul pool (EB-749): "
        "Pocket Match is the same card at 5 with Retain. Kept rather than "
        "deleted as the rows below are: a painted Klee-out-path asset on disk "
        "for a future Klee Common. It is NOT coverage for anything."),
    "proto_ko_powder_charge": (
        "R271 (2026-09-14) redesigned Powder Charge as Booby Trap "
        "(proto_ko_booby_trap, EB-749), a new id on the art bill. Kept: the "
        "painting is a placed charge and is the natural candidate when Booby "
        "Trap's art pass runs (art_of or a re-fetch, the pass decides). It is "
        "NOT coverage for anything."),
    "proto_kk_the_moon_overlooks_the_waters": (
        "EB-570 (2026-09-05) WITHDREW The Moon Overlooks the Waters from the "
        "Kokomi arm: the doctrine audit returned REQUIRES_MODIFICATION on C1 "
        "twice (any now-copy removes waiting's price; card-audit ledger 5.9) "
        "and the row was deleted under R213 B. Kept rather than deleted as "
        "rising_tide and swift_currents are: a painted asset cleared through "
        "SOURCES.tsv on a kokomi/ out-path, on disk for a future Kokomi Rare. "
        "It is NOT coverage for anything and must never be counted as such."),
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


# D5 (`EB-778`). THE PROXY BILL. A sheet row may say `art_of: <neighbour>`,
# and the generator then emits the NEIGHBOUR's key in that card's
# `CustomPortrait` getter (`tools/gen_klee_cards.py`: `card.get("art_of") or
# card["id"]`). So the row asks for no art of its own, its own id never
# reaches `mod_art_keys`, and it is neither COVERED, MISSING nor STALE -- D4's
# blind spot one seam over, and D4's own fix cannot see it because the fix
# reads what the mod ASKS FOR and a proxy asks for someone else's.
#
# Three rows wear a neighbour today (EB-326's): Coven Errand, Witches' Circle
# and Alice's Introduction Magic. Wearing one is a legitimate stand-in, not a
# defect -- what is a defect is that no surface says the debt exists, so it
# can never be worked off. Hence a BILL and not a failure: the section names
# each proxy, whose art it wears and whether its own key has a plan row yet.
#
# DERIVED, never listed: every flat card-list sheet in docs/ is read, so a
# fourth proxy joins this bill the day it is written. `docs/notes/` is out of
# scope on purpose -- `retired-prototype-rows.yaml` lives there and a retired
# row owes no art.
SHEET_DIR = ROOT / "docs"

# The shortlist/plan universe. Column 0 is asset_id, column 1 the out-path
# (art/plan.tsv's own header). A proxy whose own key appears here has had its
# art pass planned; one that does not has nothing on the bill anywhere.
PLAN = ROOT / "art" / "plan.tsv"


def plan_out_paths(path=PLAN):
    """asset_id -> the out-paths its plan rows name. Missing file => empty."""
    out = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        cells = line.split("\t")
        if len(cells) < 2:
            continue
        out.setdefault(cells[0], []).append(cells[1])
    return out


def art_of_proxies(sheet_dir=SHEET_DIR):
    """Every row wearing a neighbour's art, as [{id, wears, sheet}].

    Flat card-list sheets only: the `*-upgrades.yaml` files are mappings and
    carry no rows.
    """
    rows = []
    for path in sorted(sheet_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            continue
        for r in data:
            if isinstance(r, dict) and r.get("art_of") and "id" in r:
                rows.append({"id": r["id"], "wears": r["art_of"],
                             "sheet": path.name})
    return rows


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


#: `public sealed class Foo : ModalOptionCard` and its `, IMeterPricedCard`
#: form -- the generated face of one mode of a choose-one card
#: (`ModalChoice.cs`, `EB-746`).
MODAL_FACE_RE = re.compile(
    r"^\s*public\s+sealed\s+class\s+(\w+)\s*:\s*ModalOptionCard\b", re.M)


def portraitless_modal_faces(src=MOD_SRC):
    """Mode faces that ask for no portrait. STRUCTURAL, not an art bill.

    THE DEFECT (proofs-8a, 2026-09-16). `ModalOptionCard` declared
    `CustomPortrait => null`, which is the pre-`EB-275` answer: the game falls
    back to its OWN `card_atlas`, finds no sprite under an id only this mod
    knows, and logs

        [WARN] AtlasResourceLoader: Missing sprite
               'furina/kleemod-proto_fs_curtain_rise_mode_a' in card_atlas

    on every draw of the chooser -- the exact shape `EB-275` closed for
    ordinary rows, reopened by a card class that bypassed the getter. Two
    Curtain Rise faces shipped that way and were seen live in lane 0's log.

    A mode owes NO ART: it wears its parent's illustration, so the bill does
    not move and this check never reads a PNG. What it refuses is a modal row
    shipping with no portrait request AT ALL -- which is why it fails whether
    or not `--strict` was asked for, and whether or not `ImageGen/` is on this
    machine. The generator emits the parent's key
    (`tools/gen_klee_cards.py`, the `modal_option_classes` block); a
    hand-written face has to say so too.

    Returns `[(class name, file)]`, and a class's request is looked for inside
    its own declaration -- the parent card in the same file has one of its
    own, so a file-wide search would pass every face for free.
    """
    out = []
    if not src.is_dir():
        return out
    for path in sorted(src.rglob("*.cs")):
        text = path.read_text(encoding="utf-8")
        hits = list(MODAL_FACE_RE.finditer(text))
        for i, match in enumerate(hits):
            end = (hits[i + 1].start() if i + 1 < len(hits) else len(text))
            if not ART_KEY_RE.search(text[match.start():end]):
                out.append((match.group(1), path))
    return out


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

    # D5 / `EB-778`: the proxy bill. A REPORT and not a gate -- wearing a
    # neighbour's illustration is a sanctioned stand-in, and what was missing
    # was any surface that said the debt exists.
    proxies = art_of_proxies()
    planned = plan_out_paths()
    print("\n" + "-" * 72)
    print("ART_OF PROXIES (rows wearing a neighbour's art -- invisible above)")
    print("-" * 72)
    if not proxies:
        print("  none.")
    for row in proxies:
        wears = row["wears"]
        worn = any((d / f"{wears}.png").exists() for d in CARD_DIRS)
        own = planned.get(row["id"])
        plan_note = (f"plan row -> {own[0]}" if own
                     else "NO plan row for its own key")
        print(f"  {row['id']:44s} wears {wears}"
              f" [{'painted' if worn else 'UNPAINTED'}]  {plan_note}")
    if proxies:
        unplanned = [r["id"] for r in proxies if r["id"] not in planned]
        print(f"\n  {len(proxies)} proxy row(s); {len(unplanned)} with no plan "
              f"row of their own: {', '.join(sorted(unplanned)) or 'none'}")
        print("  Each wears its neighbour by design; the bill is what a "
              "rank-1 pass would have to place (R212).")

    # STRUCTURAL, and it gates without `--strict`: a mode face with no
    # portrait request is not an art debt, it is a missing-sprite warn on
    # every draw of the chooser (proofs-8a, 2026-09-16). See
    # `portraitless_modal_faces`.
    portraitless = portraitless_modal_faces()
    print("\n" + "-" * 72)
    print("MODE FACES (choose-one option cards -- each wears its PARENT's art)")
    print("-" * 72)
    if portraitless:
        for name, path in portraitless:
            print(f"  [FAIL]  {name} in {path.relative_to(ROOT)} "
                  f"requests no portrait")
    else:
        print("  all mode faces request a portrait.")

    if portraitless:
        print(f"\nFAIL: {len(portraitless)} choose-one mode face(s) ask for no "
              f"portrait; the game then logs AtlasResourceLoader: Missing "
              f"sprite on every draw of the chooser. A mode wears its "
              f"parent's illustration and owes no new art row.")
        return 1
    if unknown_stale:
        print(f"\nFAIL: {len(unknown_stale)} unrecorded stale file(s); add a KNOWN_STALE reason or delete.")
        return 1
    if strict and total_missing:
        print(f"\nFAIL (--strict): {total_missing} missing output(s).")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
