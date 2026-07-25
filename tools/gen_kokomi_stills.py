"""Re-derive Kokomi's still surfaces from the governing render.

Kokomi art pass, character-shell track (2026-07-25). Same six surfaces and the
same CENTRING RULE as Furina's B4 pass -- see tools/char_stills.py, which owns
the framing math for both characters.

Outputs (all gitignored Tier F, ledgered in art/SOURCES.tsv):
    ImageGen/images/kokomi/model/combat_model.png        240x280  static fallback
    ImageGen/images/kokomi/ui/select_portrait.png        132x195
    ImageGen/images/kokomi/ui/select_portrait_locked.png 132x195
    ImageGen/images/kokomi/ui/selection_splash.png      1920x1200
    ImageGen/images/kokomi/ui/char_icon.png               88x88
    ImageGen/images/kokomi/ui/map_marker.png              49x64

WHY SHE NEEDS A CUT AND FURINA DID NOT. Furina's governing render arrived as a
transparent cutout. Kokomi's best full-body art -- Sangonomiya Kokomi Portrait,
4900x5700 -- is flattened onto WHITE. Fed to the same code it produces a full-
frame alpha bbox, every framing rule degrades to frame-centring, and the pass
silently reintroduces the exact defect B4 was called to fix. The cut is
therefore a precondition, not a nicety; char_stills.cutout_from_plate keys it
by CONNECTIVITY so her white stockings and kimono panel survive.

The cut is expensive (28M pixels), so it is cached at
ImageGen/images/kokomi/model/kokomi_portrait_cutout.png -- the same place
Furina's cutout lives. Pass --recut to force it.

HEAD FRACTIONS ARE HERS, NOT FURINA'S. Her alpha bbox is 4464x5405: much wider
relative to its height than Furina's 227x440, because the Portrait includes a
companion fish out to her left and a large fin sweeping right. A head window
sized as a fraction of subject HEIGHT therefore reads differently on her, and
the values below were set by eye against rendered crops.

Usage: .venv/Scripts/python tools/gen_kokomi_stills.py [--recut]
"""
from pathlib import Path
import sys

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from char_stills import (alpha_bbox, cutout_from_plate, fit,  # noqa: E402
                         head_crop, locked_variant)

ROOT = Path(__file__).resolve().parents[1]
PLATE = ROOT / "art" / "raw" / "Sangonomiya_Kokomi_Portrait.png"
CUTOUT = ROOT / "ImageGen" / "images" / "kokomi" / "model" / "kokomi_portrait_cutout.png"
UI = ROOT / "ImageGen" / "images" / "kokomi" / "ui"
MODEL = ROOT / "ImageGen" / "images" / "kokomi" / "model"

# Set by eye (see module docstring). Larger fraction = wider shot.
PORTRAIT_HEAD_FRAC = 0.42
ICON_HEAD_FRAC = 0.20
MARKER_HEAD_FRAC = 0.24

# Selection splash. She sits left of centre because the select screen's info
# panel occupies the right third (mirrors Furina's offset).
#
# THE TEXTURE IS 1920x1200 BUT ONLY 1080 ROWS ARE EVER SEEN. char_select_bg_
# kokomi.tscn draws the splash in a 1920x1080 TextureRect with stretch_mode 6
# (KEEP_ASPECT_COVERED), so the texture scales 1:1 on width and the top and
# bottom 60 rows are cropped away. Framing against the full 1200 put her head
# under the top cut and took her feet off entirely -- the surface looked
# correct in the file and wrong in the game, which is the only kind of art
# defect that survives review. Everything below is measured against the
# VISIBLE band instead, and the band is derived from the scene's geometry
# rather than typed in.
SPLASH_BOX = (1920, 1200)
SPLASH_VISIBLE_H = 1080                                    # the TextureRect
SPLASH_VISIBLE_TOP = (SPLASH_BOX[1] - SPLASH_VISIBLE_H) // 2
SPLASH_FILL = 0.97        # subject height as a fraction of the VISIBLE band
SPLASH_FOOT_GAP = 0.02    # clearance under her feet, same units
SPLASH_X_OFFSET = -300


def load_cutout(recut=False):
    if CUTOUT.exists() and not recut:
        return Image.open(CUTOUT).convert("RGBA")
    if not PLATE.exists():
        raise SystemExit(f"source missing: {PLATE}")
    print(f"  cutting {PLATE.name} (connectivity white-key, one-off)...")
    cut = cutout_from_plate(Image.open(PLATE))
    CUTOUT.parent.mkdir(parents=True, exist_ok=True)
    cut.save(CUTOUT)
    x0, y0, x1, y1 = alpha_bbox(cut)
    print(f"  cutout cached: {CUTOUT.name}  subject {x1 - x0}x{y1 - y0}")
    return cut


def main():
    recut = "--recut" in sys.argv[1:]
    cutout = load_cutout(recut)
    UI.mkdir(parents=True, exist_ok=True)
    MODEL.mkdir(parents=True, exist_ok=True)

    # Combat static fallback: the 240x280 box the rig ships in, feet on the
    # bottom edge. She has no layered combat rig yet, so unlike Furina this is
    # the surface the game actually draws in battle, not just a fallback.
    fit(cutout, 240, 280).save(MODEL / "combat_model.png")
    print("  combat_model.png       240x280")

    portrait = head_crop(cutout, 132, 195, head_frac=PORTRAIT_HEAD_FRAC,
                         centre_on="head")
    portrait.save(UI / "select_portrait.png")
    locked_variant(portrait).save(UI / "select_portrait_locked.png")
    print("  select_portrait.png    132x195 (+ locked, identical framing)")

    head_crop(cutout, 88, 88, head_frac=ICON_HEAD_FRAC,
              centre_on="head").save(UI / "char_icon.png")
    head_crop(cutout, 49, 64, head_frac=MARKER_HEAD_FRAC,
              centre_on="head").save(UI / "map_marker.png")
    print("  char_icon.png 88x88, map_marker.png 49x64")

    # Selection splash. Framed off the ALPHA BBOX rather than the image frame
    # -- the Portrait carries ~9% empty margin all round, so scaling by frame
    # height would leave her floating short of the bottom edge.
    x0, y0, x1, y1 = alpha_bbox(cutout)
    subject = cutout.crop((x0, y0, x1, y1))
    scale = SPLASH_VISIBLE_H * SPLASH_FILL / subject.height
    body = subject.resize((round(subject.width * scale), round(subject.height * scale)),
                          Image.LANCZOS)
    w, h = SPLASH_BOX
    splash = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    feet = SPLASH_VISIBLE_TOP + SPLASH_VISIBLE_H * (1 - SPLASH_FOOT_GAP)
    splash.alpha_composite(body, ((w - body.width) // 2 + SPLASH_X_OFFSET,
                                  round(feet) - body.height))
    splash.save(UI / "selection_splash.png")
    print(f"  selection_splash.png  {w}x{h} (visible band "
          f"{SPLASH_VISIBLE_TOP}..{SPLASH_VISIBLE_TOP + SPLASH_VISIBLE_H})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
