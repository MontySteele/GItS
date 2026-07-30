#!/usr/bin/env python3
"""Plan lint for art/plan.tsv (docs/archive/art-taste-pass.md process directives 3-4).

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
  L10 an effective pick's raw source must be DECODABLE if it is present.
      Added 2026-07-29: L8 and the L6 warn both skipped an unreadable file,
      so the one source they could not measure was the one they said nothing
      about. Absent Pillow and absent raw file stay silent skips; present-
      and-unopenable is a finding.
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
import hashlib
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
    # --- Kokomi art pass, 2026-07-25. Both verified by eye before listing. ---
    ("Sangonomiya Kokomi Character Details ",
     "read-across from the banned 'Furina Character Details' family, then "
     "CONFIRMED by eye on Details 1 and 5: identical construction. Details 1 "
     "is her key illustration under a burnt-in name wordmark, a Weapon/"
     "Affiliation/Constellation/Vision stat block and three paragraphs of kit "
     "description; Details 5 is solid body text with a chibi inset. The "
     "underlying illustration on 1 is genuinely good -- if it is ever wanted, "
     "it should be a DELIBERATE manual crop with the user's eyes on it, not a "
     "shortlist row that slips through on a title match."),
    ("Icon Emoji Sangonomiya Kokomi Xiaohongshu",
     "120x120 chat emoji with Chinese caption text burnt across the art "
     "('Xiaohongshu' is the social platform the set was made for). Two "
     "disqualifiers at once: burnt-in text, and a 4x upscale to reach the "
     "500x380 card. The sticker register is UNDERSIZE_EXEMPT, which is exactly "
     "why this needs an explicit ban -- L8 would have waved all 16 through. "
     "The sibling 'Icon Emoji Paimon's Paintings ... Sangonomiya Kokomi' set "
     "is NOT banned: 340x340, transparent, no text, and legitimately her."),
    # --- Track A, 2026-07-29. All four opened and looked at this session
    # while hunting the last five card portraits; each was a candidate that
    # died on inspection, which is precisely the knowledge L9 exists to keep.
    ("Furina Introduction Card",
     "the Introduction BANNER's sibling and the same disqualifier: a burnt-in "
     "'Endless Solo of Solitude' title at the top, a full-width FURINA "
     "wordmark band across the lower third, and HoYoverse/Genshin logos "
     "beside it. No 500x380 crop clears both the title and the band -- the "
     "band sits at 80% height and the title at 10%, so any crop tall enough "
     "to frame the figure eats one of them. The banner half of this family "
     "was already banned in 2026-07-23; this closes the other half."),
    ("New Year's Advice from Teyvat",
     "quote card: a scroll graphic carrying the GENSHIN IMPACT wordmark, a "
     "two-line pull quote in 40px type and a signature. The only art on it is "
     "a chibi inset in the right third, and cropping to the inset still "
     "includes the quote. Not an illustration."),
    ("Ride the Waves to a Rendezvous",
     "framed concept-art PAGE, not the concept art: the painting sits in a "
     "letterboxed panel with the GENSHIN IMPACT wordmark above it and "
     "(c)COGNOSPHERE below, inside a decorative border. The painting itself "
     "-- a lone figure walking onto the opera stage -- is genuinely good and "
     "would suit a salon card, but reaching it needs a manual crop with the "
     "user's eyes on it, not a title match."),
    ("Genshin Impact Commemorative Shikishi Set",
     "MONOCHROME shikishi board photographed in its sleeve, with 'Copyright "
     "(c) miHoYo. All Rights Reserved.' burnt across the bottom and a "
     "signature over the art. Greyscale alone disqualifies it: it would be "
     "the only colourless portrait in a pool of 82."),
]

# L9, AWAITING THE RED-PEN SESSION. Same pattern as PENDING_UNDERSIZE: the
# finding is REAL and the resolution is a taste call, so it is reported every
# run and does not fail the gate. Resolve by re-picking, then DELETE the entry
# so the lint guards the resolution.
PENDING_BANNED_FAMILY = {
    # FOUND 2026-07-29 BY THE NEW BAN, ON A CARD THAT HAD ALREADY SHIPPED --
    # which is the whole argument for writing these families down. curtain_cue
    # wears 'Ride the Waves ... Concept Art 2', and the shipped portrait was
    # opened and confirmed: the GENSHIN IMPACT wordmark sits across the top of
    # the card and the page's beige border runs down both sides.
    #
    # It cannot be cropped out. The panel is letterboxed inside a 1920x1080
    # page, so a 500x380 `cover` uses the FULL source height by construction
    # and no focus anchor changes that; only a different source or a manual
    # crop fixes it.
    #
    # NOT re-picked here on purpose: curtain_cue is outside this sprint's
    # five-card Track A, the honest replacements are all claimed, and picking
    # its portrait is a taste call. Reported instead of silently swapped.
    "curtain_cue",
}

PENDING_RED_PEN = {
    # RESOLVED 2026-07-27 (Sweep II D1) and therefore REMOVED rather than kept
    # with a note: {kaboom, spark_knight_style}. [USER] ruled that kaboom keeps
    # "Klee Character Card" and spark_knight_style re-hunts, so its plan row is
    # commented out in art/plan.tsv and the collision this entry recorded no
    # longer exists -- exactly one card claims that source now. Leaving the
    # entry would suppress a duplicate-source finding that can no longer occur,
    # which is an exemption guarding nothing.
    #
    # The pair is STILL in KNOWN_IDENTICAL below, and that is not a
    # contradiction: the two registries record different facts. This one is
    # about the PLAN (two rows wanting one source -- fixed now). That one is
    # about the SHIPPED PIXELS (two files still byte-identical -- fixed only
    # when the rehunt lands new art).
    #
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

    problems.extend(undecodable(effective))
    problems.extend(undersized(effective))
    problems.extend(banned_families(effective))
    problems.extend(generator_owned(rows))
    # C3: L12 belongs HERE, not only in main(). It used to be reachable solely
    # by running this file as a script, so art_process -- the thing that WRITES
    # the crops -- imported lint() and never pixel-checked its own output.
    problems.extend(identical_crops())

    for note in clip_warnings(effective):
        print(note)

    return problems


# L11: out-paths produced by a dedicated generator script rather than by
# art_process. Curated because nothing in the repo can infer it -- a generator
# writes wherever its own code says, and plan.tsv has no way to know. Each
# entry names the generator so the cross-check below can prove the claim is
# still true; see the "structurally invisible defect" house rule.
GENERATOR_OWNED = {
    "ImageGen/images/furina/model/combat_model.png":        "gen_furina_stills.py",
    "ImageGen/images/furina/ui/select_portrait.png":        "gen_furina_stills.py",
    "ImageGen/images/furina/ui/select_portrait_locked.png": "gen_furina_stills.py",
    "ImageGen/images/furina/ui/selection_splash.png":       "gen_furina_stills.py",
    "ImageGen/images/furina/ui/char_icon.png":              "gen_furina_stills.py",
    "ImageGen/images/furina/ui/map_marker.png":             "gen_furina_stills.py",
    "ImageGen/images/kokomi/model/combat_model.png":        "gen_kokomi_stills.py",
    "ImageGen/images/kokomi/ui/select_portrait.png":        "gen_kokomi_stills.py",
    "ImageGen/images/kokomi/ui/select_portrait_locked.png": "gen_kokomi_stills.py",
    "ImageGen/images/kokomi/ui/selection_splash.png":       "gen_kokomi_stills.py",
    "ImageGen/images/kokomi/ui/char_icon.png":              "gen_kokomi_stills.py",
    "ImageGen/images/kokomi/ui/map_marker.png":             "gen_kokomi_stills.py",
    "ImageGen/images/furina/salon/glyph_damage.png":        "gen_salon_glyphs.py",
    "ImageGen/images/furina/salon/glyph_block.png":         "gen_salon_glyphs.py",
    "ImageGen/images/furina/salon/glyph_support.png":       "gen_salon_glyphs.py",
    "ImageGen/images/ui/transition_wipe.png":               "gen_transition_wipe.py",
    "ImageGen/images/kokomi/ui/transition_wipe.png":        "gen_transition_wipe.py",
}


def generator_owned(rows) -> list[str]:
    """L11: no plan row may claim an out-path a generator script owns.

    Shipped as: animation sprint 2 (B4) moved Furina's six still surfaces onto
    tools/gen_furina_stills.py, which re-derives them with framing computed
    from the ALPHA BBOX -- that centring fix IS the B4 verdict -- but left the
    five old plan rows live. Two producers then claimed one out-path, and both
    halves of that bit the same day: art_fetch rewrote those files' SOURCES.tsv
    provenance back to `Furina Profile.png`, so the ledger LIED about where the
    shipped bytes came from, and the next art_process run would have silently
    overwritten the re-centred art with the old off-centre crops.

    The catch was luck (a fetch happened to run). This makes it structural.
    """
    problems = []
    root = Path(__file__).resolve().parent.parent
    for r in rows:
        gen = GENERATOR_OWNED.get(r["out"])
        if gen:
            problems.append(
                f"L11 {r['asset_id']}: out-path '{r['out']}' is produced by "
                f"tools/{gen}, not by art_process. Two producers for one path "
                "means whichever runs last wins and the SOURCES row goes stale. "
                "Retire the plan row (comment it out) or drop it from "
                "GENERATOR_OWNED if the generator no longer owns it."
            )
    # The curated list must not rot: a generator that is renamed, deleted, or
    # re-pointed leaves entries here silently guarding nothing, which is the
    # same class of invisible defect the rule exists to stop.
    for out, gen in sorted(GENERATOR_OWNED.items()):
        src = root / "tools" / gen
        if not src.exists():
            problems.append(
                f"L11 GENERATOR_OWNED names tools/{gen}, which does not exist")
        elif Path(out).name not in src.read_text(encoding="utf-8"):
            problems.append(
                f"L11 GENERATOR_OWNED claims tools/{gen} produces "
                f"'{out}', but that filename does not appear in it")
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
                msg = (f"L9 {r['asset_id']}: source '{title}' is from the "
                       f"banned '{prefix.strip()}' family -- {why}")
                if r["asset_id"] in PENDING_BANNED_FAMILY:
                    print(f"PENDING RED-PEN (banned family, allowlisted): "
                          f"{msg}")
                else:
                    problems.append(msg)
                break
    return problems


def undecodable(effective) -> list[str]:
    """L10: an effective pick whose raw source is PRESENT and un-openable.

    Both image rules used to `continue` on any `Image.open` failure, so the
    single input neither of them could measure was the one input they reported
    nothing about: a truncated download, a wiki HTML error page saved under a
    .png name, or a WEBP with no decoder in this Pillow build all passed L8
    (undersize) and the L6 aspect warn in silence.

    The DOCUMENTED skips are kept and are different in kind, because both are
    facts about the machine rather than about the pick:

      - no Pillow -> the plan must stay lintable without an image decoder;
      - no raw file -> the plan must stay lintable BEFORE a fetch.

    "The file is here and it is not an image" is neither. It is a finding.
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
        src = raw_dir / rawname(r["title"])
        if not src.exists():
            continue
        try:
            Image.open(src).size
        except Exception as exc:
            problems.append(
                f"L10 {r['asset_id']}: raw source '{src.name}' exists but "
                f"cannot be decoded ({type(exc).__name__}: {exc}) -- L8 and "
                f"the L6 warn cannot measure it, so nothing about this pick "
                f"is checked. Re-fetch it (a truncated or HTML-error download "
                f"is the usual cause) or drop the row."
            )
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
            continue            # already a FINDING -- see undecodable() (L10)
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
            continue            # already a FINDING -- see undecodable() (L10)
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


# L12: pixel-identical rank-1 crops. Curated allowlist for the pairs that were
# already shipped when this check was written -- they are real defects, not
# exemptions, and each needs a re-pick or a red-pen ruling.
#
# RETIRED 2026-07-25: blazing_delight == true_spark_knight. That pair was never
# duplicate ART. blazing_delight had no rank-1 plan row at all, so art_process
# never wrote its out-path; what L12 hashed was a STALE candidate left behind by
# an older plan. The card read as "shipped with a duplicate crop" when it had in
# fact shipped with no crop -- art_coverage was billing it MISSING the whole
# time, and the two gates were describing the same hole in opposite languages.
# It now has its own rank-1 source and hashes differently. Worth keeping in
# view: L12 reads the candidates directory, so a stale file can manufacture a
# duplicate for a card that has no pick.
KNOWN_IDENTICAL = {
    frozenset({"catalytic_conversion", "spark_collection"}),   # also PENDING_RED_PEN
    frozenset({"crowd_work", "standing_ovation"}),
    # ADDED by C3 (Serenitea Sweep), and it is the finding, not the fix.
    # Turning L12 on against the SHIPPED files surfaced this immediately:
    # klee/kaboom.png and klee/spark_knight_style.png are byte-identical
    # (sha256 5649882009...). Both are auto-picks off "Klee Character Card",
    # so the old candidates-only hash could never have seen them -- auto-picks
    # get no candidates directory at all.
    #
    # It was already half-recorded: the pair sits in PENDING_RED_PEN above as
    # a SOURCE collision ("ruled onto spark_knight_style, but it is ALSO
    # kaboom's auto pick -- not 'only a model source' as the ruling assumed").
    # Its two siblings there were also entered here; this one never was, which
    # is the gap missed-requirements sec.4.6 names -- "unlike its two siblings,
    # [it] is in no ledger". Now it is in both.
    #
    # RULED 2026-07-27 ([USER], Serenitea Sweep II D1). The ruling this entry
    # was waiting for: KABOOM KEEPS the Character Card; spark_knight_style
    # gets new art. Registered in art/plan.tsv -- its plan row is commented out
    # with the ruling, and it now sits in the REHUNT PILE beside pop.
    #
    # THE ENTRY STAYS, and the reason it stays is the point of D1. The ruling
    # fixed the PLAN; the two SHIPPED files are still byte-identical and stay
    # that way until someone actually re-crops. So L12 still has a real finding
    # here, and suppressing it is still correct -- for now.
    #
    # REMOVAL IS AUTOMATIC, not remembered: the day new art lands,
    # `test_every_allowlisted_identical_pair_is_still_identical` fails on this
    # pair and the entry has to come out. That is deliberate. An exemption
    # outliving its reason is the B6 ledger lesson, and the fix for it is a
    # test that breaks, not a note asking someone to check.
    #
    # Its PENDING_RED_PEN twin was removed in the same change, because that
    # collision really is gone. Different registry, different fact.
    frozenset({"kaboom", "spark_knight_style"}),
}


def identical_crops() -> list[str]:
    """L12: two cards whose EFFECTIVE crop renders the same pixels.

    THE STRING CHECKS CANNOT SEE THIS. L1 compares (title, frame) and L7
    compares (mode, focus) -- both compare what the plan SAYS. But both crop
    modes clamp:

      - `cover`'s focus is a CENTRE, and the crop is clamped inside the image,
        so every anchor nearer an edge than half the crop lands in the same
        place. y0.14 and y0.30 on a 4900x5700 source are the same picture.
      - `cover_autocrop`'s focus is a MARGIN and clamps to the content bbox,
        so cover@0.22 and cover@0.58 are the same picture too.

    The Kokomi art pass (2026-07-25) shipped ELEVEN identical groups covering
    ~28 cards with a fully green lint before this existed, and found them only
    by hashing the output. That is the whole argument for checking the pixels:
    a plan that differs on paper is not a plan that differs on the card.

    C3 (audit sec.3.7) -- THIS CHECK WAS OFF. Three separate reasons, all fixed
    here:

      1. It hashed `art/candidates/**`, which is gitignored and absent on every
         clean checkout: `is_dir()` was False and it returned [] in silence.
         The one gate that caught the 28-card identical-crop defect had been
         dark on any machine that had not just run an art pass.
      2. It hashed the SHORTLIST rather than the shipped output, so auto-picks
         -- which never get a candidates directory -- were never hashed at all.
         A duplicate between two auto-picked cards was structurally invisible.
      3. It was called only from `main()`, so `art_process`'s import path (and
         every other caller of `lint()`) never pixel-checked.

    Now it hashes `ImageGen/images/cards/**`, which is what actually ships, and
    `lint()` calls it. Two consequences of the move, both deliberate:

      - Ids are the file STEM, taken from the package rather than from a plan
        directory name. That closes the stale-candidate trap noted under
        KNOWN_IDENTICAL: a leftover candidate for a card with no pick can no
        longer manufacture a duplicate, because a card with no pick has no
        shipped file to hash.
      - Absence is still a silent no-op, which is correct here rather than lax:
        `ImageGen/images` is gitignored Tier F, so a bare clone genuinely has
        nothing to compare. "Did the art ship" is S9's question and
        art_coverage.py's; this rule only answers "do two shipped cards render
        the same pixels".
    """
    shipped = (Path(__file__).resolve().parent.parent
               / "ImageGen" / "images" / "cards")
    if not shipped.is_dir():
        return []
    seen: dict[str, list[str]] = {}
    for f in sorted(shipped.rglob("*.png")):
        seen.setdefault(hashlib.sha256(f.read_bytes()).hexdigest(),
                        []).append(f.stem)
    problems = []
    for ids in seen.values():
        if len(ids) < 2:
            continue
        if frozenset(ids) in KNOWN_IDENTICAL:
            print(f"KNOWN IDENTICAL (allowlisted): L12 {' == '.join(ids)}")
            continue
        problems.append(
            f"L12 {' == '.join(ids)}: effective crops are PIXEL-IDENTICAL. "
            f"Both crop modes clamp, so differing focus strings do not "
            f"guarantee differing art -- re-anchor within the source's valid "
            f"range, or give one of them a different source."
        )
    return problems


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from art_fetch import read_plan
    problems = lint(read_plan())        # includes L12 since C3
    if problems:
        for p in problems:
            print("LINT: " + p, file=sys.stderr)
        return 1
    print("art_lint: plan OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
