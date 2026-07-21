#!/usr/bin/env python3
"""Plan lint for art/plan.tsv (docs/art-taste-pass.md process directives 3-4).

Checks EFFECTIVE card picks only (auto rows and shortlist rank 1) -- shortlist
alternates may share sources freely, since only one of them ever ships.

Rules, each a defect that actually shipped in the first art sprint:
  L1  no two cards may share an effective source (same title AND, for gifs,
      same frame_pct -- distinct frames of one clip are distinct images).
      Shipped as: big_badda_boom wearing blazing_delight's constellation, and
      boom_goes_the_dynamite twinning crackle.
  L2  every effective card pick declares a register
      (sticker|item|vfx|tcg|splash|icon).
  L3  register `icon` is BANNED from card portraits (128px sigils read as UI
      at card size; they belong on power/relic icon slots).
  L4  register `item` must use mode `contain` (small transparent renders under
      `cover` smear their edges across the frame).
  L5  gif sources must pin a frame_pct (frame choice is a taste parameter,
      not a default).

Codified by the art vibe-check ruling (2026-07-20): L1's scope IS the dedupe
law -- effective picks (auto, or shortlist rank 1 unless red-pen resolves
otherwise) in card-register slots (/cards/ out-paths). Register-CROSSING
reuse is legal by construction (only /cards/ rows enter L1): a card sharing
its own power icon's source is natural, and splash/model/select reuse never
collides with cards. Worked example: Klee Wish = big_badda_boom's card AND
the selection splash -- legal. Shortlist alternates sharing sources (e.g.
Imaginary Friend Dodoco on duck_and_cover r3 while clockwork_toy r1 wears
it) are blessed: dead ranks don't ship.

Standalone: python tools/art_lint.py    (also run by art_process before work)
"""
import sys
from pathlib import Path

REGISTERS = {"sticker", "item", "vfx", "tcg", "splash", "icon"}

# L4: item renders must FIT, never FILL. `contain` has always been legal;
# `cover_autocrop` joined it (2026-07-21) because autocrop attacks L4's actual
# rationale -- it removes the transparent margin that smears, and item sources
# are ~50% dead canvas (Item Kaboom Box: 176x180 of a 256x256 sheet), so
# autocrop+contain is what finally makes the object fill the card. The fill
# half of cover_autocrop stays banned for items and the arm below enforces it.
ITEM_MODES = {"contain", "cover_autocrop"}

# L6 clip-detect thresholds. cover crops to fill, so a source whose figure is
# small-in-frame or off-centre gets zoomed into the wrong body part -- round 3
# lost the_big_one to a torso crop, tail_of_flame to shorts, patched_dress to
# a chest. These flag the shape of that failure; they are a POINTER to look,
# not a verdict (a spark effect SHOULD crop hard, having no head to lose).
CLIP_ASPECT_RATIO = 1.6   # source-vs-card aspect mismatch that crops ~25%+
# `tcg` is deliberately EXCLUDED: trading-card sources are portrait-shaped, so
# a landscape card crop always trims ~56% of their height by construction, and
# that crop is the intended framing (process() also trims the printed border
# first). Including them buried the two real signals in nine false ones.
CLIP_REGISTERS = {"splash", "sticker"}   # registers that depict a figure

# Known L1 collisions AWAITING THE RED-PEN SESSION (the domination lint's
# KNOWN-set pattern): reported as a note, not a failure, until resolved.
# Both were created by the 2026-07-20 vibe-check ruling's replace list, whose
# premises missed that the incoming source already had a card-space owner.
# Resolve by re-picking one side (or re-hunting); then DELETE the entry so
# the lint guards the resolution.
PENDING_RED_PEN = {
    # Klee Character Card: ruled onto spark_knight_style ("regular = the
    # Style" pairing), but it is ALSO kaboom's auto pick -- not "only a
    # model source" as the ruling assumed.
    frozenset({"kaboom", "spark_knight_style"}),
    # Dodoco's Marvelous Magic: ruled onto catalytic_conversion (promoted
    # from its power icon), but it is ALSO spark_collection's effective r1,
    # and spark_collection's r2 is vermillion_pact's passed pick.
    frozenset({"spark_collection", "catalytic_conversion"}),
}


def lint(rows) -> list[str]:
    problems = []
    effective = [
        r for r in rows
        if "/cards/" in r["out"] and (r["pick"] == "auto" or r["rank"] == 1)
    ]

    seen: dict[tuple, str] = {}
    for r in effective:
        key = (r["title"], r["frame"])
        if key in seen:
            frame = f" @{r['frame']}%" if r["frame"] is not None else ""
            msg = (
                f"L1 {r['asset_id']}: effective source '{r['title']}'{frame} "
                f"already used by {seen[key]}"
            )
            if frozenset({r["asset_id"], seen[key]}) in PENDING_RED_PEN:
                print(f"PENDING RED-PEN (allowlisted): {msg}")
            else:
                problems.append(msg)
        else:
            seen[key] = r["asset_id"]

        reg = r["register"]
        if reg is None:
            problems.append(f"L2 {r['asset_id']}: effective pick has no register")
        elif reg not in REGISTERS:
            problems.append(
                f"L2 {r['asset_id']}: unknown register '{reg}' "
                f"(want one of {'|'.join(sorted(REGISTERS))})"
            )
        if reg == "icon":
            problems.append(
                f"L3 {r['asset_id']}: register 'icon' is banned from card "
                "portraits -- redirect the sigil to a power/relic icon slot"
            )
        if reg == "item" and r["mode"] not in ITEM_MODES:
            problems.append(
                f"L4 {r['asset_id']}: item render must fit, not fill -- want "
                f"mode 'contain' or 'cover_autocrop' with fit contain "
                f"(has '{r['mode']}' focus '{r['focus']}'); filling an item "
                "crops the object and smears its transparent edges"
            )
        elif (reg == "item" and r["mode"] == "cover_autocrop"
                and not str(r["focus"]).startswith("contain")):
            problems.append(
                f"L4 {r['asset_id']}: item on cover_autocrop must declare fit "
                f"'contain' (has focus '{r['focus']}'); cover-filling a small "
                "item crops the object -- Item Supersized Firework loses 37% "
                "of its height that way"
            )
        if r["source"] == "gif" and r["frame"] is None:
            problems.append(f"L5 {r['asset_id']}: gif pick without a frame_pct")

    for note in clip_warnings(effective):
        print(note)

    return problems


def clip_warnings(effective) -> list[str]:
    """L6 (WARN, never a failure): cover crops that probably eat the figure.

    Round 3's pipeline lesson: `cover` is excellent when the figure is large
    and centred, and fails when it is small-in-frame or off-centre -- it zooms
    into the wrong body part. So cover REQUIRES a per-card contain fallback,
    and this is the instrument that says where to look.

    A WARN by design. Cropping hard is correct for an abstract source (a spark
    effect has no head to lose) and wrong for a portrait, and only eyes can
    tell those apart -- so this points, and the red-pen rules. Silently
    skipped when Pillow or the raw file is absent; the lint's other rules must
    keep working without an image decoder installed.
    """
    try:
        from PIL import Image
    except ImportError:
        return []
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from art_fetch import rawname

    raw_dir = Path(__file__).resolve().parent.parent / "art" / "raw"
    notes = []
    for r in effective:
        if r["mode"] != "cover" or r["register"] not in CLIP_REGISTERS:
            continue
        src = raw_dir / rawname(r["title"])
        if not src.exists():
            continue
        try:
            img = Image.open(src).convert("RGBA")
            box = (img.getchannel("A").point(lambda v: 255 if v > 10 else 0)
                      .getbbox())
        except Exception:
            continue
        if not box:
            continue
        cw, ch = box[2] - box[0], box[3] - box[1]
        if not ch:
            continue
        card_ar = r["w"] / r["h"]
        content_ar = cw / ch
        # cover scales to fill, so the narrower axis is what gets trimmed.
        lost = 1 - (content_ar / card_ar) if content_ar < card_ar else \
               1 - (card_ar / content_ar)
        if lost >= 1 - 1 / CLIP_ASPECT_RATIO:
            axis = "height" if content_ar < card_ar else "width"
            notes.append(
                f"L6 WARN {r['asset_id']}: cover trims ~{lost:.0%} of the "
                f"source {axis} ('{r['title']}'). If it depicts a figure, "
                "check for a head/limb clip and fall back to "
                "cover_autocrop@contain."
            )
    return notes


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from art_fetch import read_plan
    problems = lint(read_plan())
    if problems:
        for p in problems:
            print("LINT: " + p, file=sys.stderr)
        return 1
    print("art_lint: plan OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
