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
  L8  an effective card pick's source must not be smaller than the card in
      BOTH axes. Added after `Talent <Card Name>.png` sigils (128x128, exact
      name matches for five Furina rares) were nearly promoted as portraits;
      L3 missed them because it keys on the declared register.
  L7  source_group siblings must differ by CROP. Added for the Furina pass
      (furina-art-pass-requirements.md 9.3): Companion characters get one
      strong source family and three deliberately different crops, which L1
      read as a violation. The group makes that reuse legal -- but only when
      the crop actually changes, or the two cards are the same picture twice.

The `source_group` column carries the character family. Rows LEAVE IT BLANK
by default, and blank keeps strict L1. That default is load-bearing: Furina's
own 76 cards are one character but must never share a source with each other
(requirements 2, "one effective source should not serve two unrelated Furina
cards"), so grouping by character would have quietly legalised exactly the
reuse the rule exists to stop. Only sibling sets that are SUPPOSED to share a
source -- Chevreuse's three, Lynette's three, the Neuvillette Guest Stars --
carry a group.

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
# L8 exemptions. Both registers are small-by-construction, not defective --
# see undersized()'s docstring for the shipped Klee cards that proved it.
UNDERSIZE_EXEMPT_REGISTERS = {"item", "sticker"}

# L8, shipped-and-ratified allowlist (same KNOWN-set pattern as PENDING_RED_PEN).
# Only for picks the user already approved by eye; a NEW pick must not land here.
KNOWN_UNDERSIZED = {
    # 480x270 clip frame -- short on width by 4% and height by 29%, which is a
    # mild upscale rather than a sigil. Shipped in the Klee taste pass.
    "bombs_away",
}

# L8, AWAITING THE RED-PEN SESSION. Reported as a note, not a failure, exactly
# like PENDING_RED_PEN -- these are picks where the undersize is real but the
# content match is the best available, so the call is the user's with the image
# in front of them. Resolve by approving (move to KNOWN_UNDERSIZED) or
# re-picking; then DELETE the entry so the lint guards the resolution.
PENDING_UNDERSIZE = {
    # The Salon Solitaire ability previews are all 480x270 -- the same size the
    # user already accepted for bombs_away. For "Salon Members dancing in a
    # persistent circular pattern" they are the ONLY art showing the Members in
    # motion; the non-gif alternatives are a 700x1720 text page or reusing
    # salon_debut's source. Content is right, resolution is marginal.
    "endless_waltz",
    # Batch 2: the three named Salon Members ARE the subject of these cards, and
    # the only art showing each Member is a 480x270 Salon Solitaire ability gif
    # (same 480x270 the user accepted for bombs_away). Surfaced for the red-pen
    # session, not self-approved.
    "gentilhomme_usher",        # Salon Solitaire Ousia Preview.gif
    "mademoiselle_crabaletta",  # Salon Solitaire Plunging Water Preview.gif
    "full_ensemble",            # Salon Solitaire Pneuma Preview.gif (all Members)
    # 447x328 applause-crowd art -- a genuine content match for "Rapturous
    # Applause", short of 500x380 by 11%/14%. Mild upscale, user's call.
    "rapturous_applause",       # FCFH Applause and Cheer.png
    # Batch 3: the supporting cast IS the Salon Members; the Members walking on
    # water (480x270 gif) is the ensemble-in-motion shot, same case as above.
    "supporting_cast",          # Salon Solitaire Water Walk Preview.gif
}

# L9: wiki source families that are NOT illustrations. A card portrait cannot
# be checked for "is this a picture of the character" by any rule the repo can
# express -- the pixels are gitignored and nothing in the plan records what a
# file depicts. So the 2026-07-23 taste pass, which rejected 13 batch-1 cards,
# is written down here as an enumerated ban instead: each entry is a family the
# user (or a follow-up spot check) actually looked at and disqualified.
#
# Match is a case-insensitive prefix on the wiki title. Adding a family here is
# cheap; every entry must carry WHY, so a later pass can tell a real ban from a
# guess. Verified by eye against art/raw/ before being listed.
BANNED_SOURCE_FAMILIES = [
    ("Splashscreen ",
     "version wish banner: carries the GENSHIN IMPACT wordmark, the wish name "
     "and the run dates as burnt-in text, and frames two banner characters "
     "rather than one subject. User rejected 5 of these by name; the other 2 "
     "in the plan were spot-checked and are identical in construction."),
    ("Furina Character Notes ",
     "in-game Training Guide infographic -- 'Artifact Recommendations', "
     "'Weapon Recommendations', stat text and item icons. Not art at all."),
    ("Furina Character Details ",
     "character-screen lore page. Details 7 is solid body text (user rejected "
     "it as graceful_retreat). Others in the family are an illustration under "
     "a title/tagline overlay, which is still burnt-in text on a card."),
    ("Opera Epiclese Passage ",
     "empty corridor screenshot -- no character in frame. User rejected "
     "Passage 2 as fortissimo_guard: 'a random hallway'."),
    ("Test Run ",
     "Character Trial Event UI banner: headline text plus a row of character "
     "cards with names and star ratings burnt in."),
    ("Namecard Banner ",
     "1024x140 namecard strip. Filling a 500x380 card from a 140px-tall source "
     "is a 2.7x vertical upscale -- L8 misses it because only one axis is short."),
    ("Furina Introduction Banner",
     "carries a large burnt-in FURINA wordmark over the figure's left. At the "
     "500x380 card aspect the widest possible right-crop (clamped to width-500) "
     "still includes the 'NA' tail -- the text cannot be cropped out. Verified "
     "2026-07-23: x0.70 anchor still showed it."),
]

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

    seen: dict[tuple, dict] = {}
    for r in effective:
        key = (r["title"], r["frame"])
        if key in seen:
            prev = seen[key]
            frame = f" @{r['frame']}%" if r["frame"] is not None else ""
            group = r.get("source_group")
            same_family = group is not None and group == prev.get("source_group")
            crop = (r["mode"], r["focus"])
            prev_crop = (prev["mode"], prev["focus"])

            if same_family and crop != prev_crop:
                # The intended Companion pattern: one strong source family,
                # siblings differentiated by crop (requirements 3, 7).
                pass
            elif same_family:
                # Same family AND same crop = byte-identical portraits on two
                # different cards. L1's own rationale, one scope in.
                problems.append(
                    f"L7 {r['asset_id']}: source_group '{group}' sibling of "
                    f"{prev['asset_id']} reuses '{r['title']}'{frame} with an "
                    f"IDENTICAL crop {crop} -- siblings must differ by crop"
                )
            else:
                msg = (
                    f"L1 {r['asset_id']}: effective source '{r['title']}'{frame} "
                    f"already used by {prev['asset_id']}"
                )
                if group and prev.get("source_group"):
                    msg += (
                        f" (source_group '{group}' vs "
                        f"'{prev['source_group']}' -- cross-family reuse is illegal)"
                    )
                if frozenset({r["asset_id"], prev["asset_id"]}) in PENDING_RED_PEN:
                    print(f"PENDING RED-PEN (allowlisted): {msg}")
                else:
                    problems.append(msg)
        else:
            seen[key] = r

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

    problems.extend(undersized(effective))
    problems.extend(banned_families(effective))

    for note in clip_warnings(effective):
        print(note)

    return problems


def banned_families(effective) -> list[str]:
    """L9: an effective card pick drawn from a known non-illustration family.

    Applies to card portraits only. The sec.8 power/relic/UI sets legitimately
    want icons and wordmarks, and a banned family may still be a fine source
    there, so the rule keys on the output living under /cards/.
    """
    problems = []
    for r in effective:
        title = r["title"]
        for prefix, why in BANNED_SOURCE_FAMILIES:
            if title.lower().startswith(prefix.lower()):
                problems.append(
                    f"L9 {r['asset_id']}: source '{title}' is from the banned "
                    f"'{prefix.strip()}' family -- {why}")
                break
    return problems


def undersized(effective) -> list[str]:
    """L8: an effective card pick whose source is smaller than the card BOTH ways.

    Caught a real defect on its first run (Furina batch 1, 2026-07-23). The
    wiki hosts `Talent <Card Name>.png` files whose names match card names
    exactly -- `Talent Let the People Rejoice.png`, `Talent The Sea Is My
    Stage.png` -- which makes them look like ideal sources. They are 128x128
    talent SIGILS. Blown up to a 500x380 portrait that is a 4x upscale, and
    they are precisely what L3 means by "128px sigils read as UI at card
    size". L3 could not catch them because L3 keys on the DECLARED register,
    and declaring one `tcg` walks straight past it.

    The test is both-dimensions-short on purpose. A source short on ONE axis
    is normal and shipped: TCG character cards are 420x720 (portrait-shaped by
    construction, and cover crops the height anyway), stickers are square-ish.
    Only a source smaller than the card in width AND height is being upscaled
    no matter how it is cropped.

    `item` and `sticker` are exempt, and that exemption is not a loophole --
    it is what the first run taught. Written without it, this rule failed six
    ALREADY-SHIPPED Klee cards whose picks the user had approved by eye
    (duck_and_cover, perfect_timing, run_away and snap on 340x340 Paimon's
    Paintings emoji, rapid_fire on a 144x144 one). Both registers are small by
    construction: items are contain-fitted rather than fill-cropped (Klee
    shipped Item Kaboom Box at 176x180 of a 256x256 sheet) and emoji stickers
    have no large original. A gate that retroactively condemns ratified art is
    measuring the wrong thing.

    Silently skipped when Pillow or the raw file is absent, same as L6: the
    plan must stay lintable before a fetch and without an image decoder.
    """
    try:
        from PIL import Image
    except ImportError:
        return []
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from art_fetch import rawname

    raw_dir = Path(__file__).resolve().parent.parent / "art" / "raw"
    problems = []
    for r in effective:
        if r["register"] in UNDERSIZE_EXEMPT_REGISTERS:
            continue
        if r["asset_id"] in KNOWN_UNDERSIZED:
            continue
        src = raw_dir / rawname(r["title"])
        if not src.exists():
            continue
        try:
            w, h = Image.open(src).size
        except Exception:
            continue
        if w < r["w"] and h < r["h"]:
            msg = (
                f"L8 {r['asset_id']}: source '{r['title']}' is {w}x{h}, "
                f"smaller than the {r['w']}x{r['h']} card in BOTH axes -- "
                f"upscale blur. If it is a talent/constellation sigil it "
                f"belongs on a power or relic icon slot, not a card."
            )
            if r["asset_id"] in PENDING_UNDERSIZE:
                print(f"PENDING RED-PEN (undersize, allowlisted): {msg}")
            else:
                problems.append(msg)
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
