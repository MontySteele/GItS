"""Re-derive Furina's still surfaces from the governing render.

Animation sprint 2, Track B4 (2026-07-24). The [USER] verdict was that her
model AND her select art are off-centre; B4's point is that the fix has to
land at EVERY surface, not just in combat. All of these are now cut from the
same source as the combat rig, so they cannot drift from each other again.

Outputs (all gitignored Tier F, ledgered in art/SOURCES.tsv):
    ImageGen/images/furina/model/combat_model.png       240x280  static fallback
                                                         (the game draws her
                                                         model frames)
    ImageGen/images/furina/ui/selection_splash.png     1920x1200
    (ui/char_icon.png left 2026-10-13: tools/gen_char_icons.py draws it)
    (ui/map_marker.png left 2026-10-19: tools/gen_map_markers.py draws a pin from the model close-up)

CENTRING RULE. Every framing here is computed from the render's ALPHA
bounding box, never from the image frame -- that is precisely the bug being
fixed. Horizontal centre is the alpha bbox centre; vertical framing is
anchored per surface (feet-down for the full body, head-down for portraits).
The rule now lives in tools/char_stills.py, because Kokomi's pass needs the
same six surfaces and a centring rule duplicated across two files is a
centring rule that will drift. This script keeps only HER numbers.

The roster tile (ui/select_portrait.png and its locked twin) left this script
on 2026-10-13: tools/char_render/pack.py cuts it from her model's select pose,
and one out-path has one producer.

Source: the transparent 227x440 cutout for anything that needs an alpha
(combat/portrait/icon), and the 1080x2160 full-res twin for the big splash,
which is composited over a plate and so does not need a cutout.

Usage: .venv/Scripts/python tools/gen_furina_stills.py
"""
from pathlib import Path
import sys

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from char_stills import fit  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CUTOUT = ROOT / "ImageGen" / "images" / "furina" / "model" / "furina_wikipedia_cutout.png"
FULLRES = ROOT / "art" / "raw" / "Furina_Card_2.png"
UI = ROOT / "ImageGen" / "images" / "furina" / "ui"
MODEL = ROOT / "ImageGen" / "images" / "furina" / "model"


def main():
    for path in (CUTOUT, FULLRES):
        if not path.exists():
            raise SystemExit(f"source missing: {path}")

    cutout = Image.open(CUTOUT).convert("RGBA")
    UI.mkdir(parents=True, exist_ok=True)
    MODEL.mkdir(parents=True, exist_ok=True)

    # Combat static fallback: the same 240x280 box the rig ships in, feet on
    # the bottom edge exactly like the layered scene.
    fit(cutout, 240, 280).save(MODEL / "combat_model.png")
    print("  combat_model.png       240x280")

    # The icon and the map marker are tools/gen_char_icons.py's and
    # tools/gen_map_markers.py's, from her model close-up.

    # Selection splash: the full-res twin, framed so she sits centred in the
    # left-of-centre third the info panel leaves free.
    full = Image.open(FULLRES).convert("RGBA")
    splash = Image.new("RGBA", (1920, 1200), (0, 0, 0, 0))
    scale = 1200 / full.height * 1.04
    body = full.resize((round(full.width * scale), round(full.height * scale)),
                       Image.LANCZOS)
    splash.alpha_composite(body, ((1920 - body.width) // 2 - 300, 0))
    splash.save(UI / "selection_splash.png")
    print("  selection_splash.png  1920x1200")
    return 0


if __name__ == "__main__":
    sys.exit(main())
