"""Derive Varka's still surfaces from his governing render.

Varka prototype art pass (2026-09-29). Same six surfaces and the same
CENTRING RULE as Furina's B4 pass and Kokomi's shell pass -- tools/char_stills.py
owns the framing math; this script keeps only HIS numbers.

Outputs (all gitignored Tier F, ledgered in art/SOURCES.tsv):
    ImageGen/images/varka/model/combat_model.png        240x280  static combat body
    ImageGen/images/varka/ui/select_portrait.png        132x195
    ImageGen/images/varka/ui/select_portrait_locked.png 132x195
    ImageGen/images/varka/ui/selection_splash.png      1920x1200
    ImageGen/images/varka/ui/char_icon.png               88x88
    ImageGen/images/varka/ui/map_marker.png              49x64

SOURCE. `Varka Portrait.png` (1376x1776, official, fetched by the Varka block
of art/plan.tsv into art/raw/). Unlike Kokomi's Portrait it already ships as an
RGBA CUTOUT, so no plate cut is needed: it is read straight from art/raw/.
Its alpha bbox is nearly the whole frame because his claymore and cape run to
both side edges; the head therefore sits well left of the bbox centre, which is
why every head crop below centres on the head band (centre_on="head"), the rule
Kokomi's fin and fish already needed.

He has no layered combat rig (no fence config in tools/combat_layer_fences/),
so combat_model.png is the surface the game draws in battle, exactly as
Kokomi's is.

Usage: .venv/Scripts/python tools/gen_varka_stills.py [--art-root <checkout>] [--check]

--art-root reads art/raw/ and writes ImageGen/ under another checkout, the way
art_process.py's flag does: Tier F pixels live only on the main checkout and a
worktree must never link them in. --check re-derives every surface in memory and
fails if a shipped file differs.
"""
from pathlib import Path
import sys

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from char_stills import alpha_bbox, fit, head_crop, locked_variant  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REL = Path("art") / "raw" / "Varka_Portrait.png"
UI_REL = Path("ImageGen") / "images" / "varka" / "ui"
MODEL_REL = Path("ImageGen") / "images" / "varka" / "model"

# Set by eye against rendered crops. Larger fraction = wider shot.
PORTRAIT_HEAD_FRAC = 0.40
ICON_HEAD_FRAC = 0.17
MARKER_HEAD_FRAC = 0.21

# Selection splash: measured against the VISIBLE 1080 band of the 1920x1200
# texture (see gen_kokomi_stills.py for why), left of centre for the info panel.
SPLASH_BOX = (1920, 1200)
SPLASH_VISIBLE_H = 1080
SPLASH_VISIBLE_TOP = (SPLASH_BOX[1] - SPLASH_VISIBLE_H) // 2
SPLASH_FILL = 0.97
SPLASH_FOOT_GAP = 0.02
SPLASH_X_OFFSET = -300


def _take(argv, flag):
    if flag not in argv:
        return None
    i = argv.index(flag)
    if i + 1 >= len(argv):
        sys.exit(f"{flag} needs a value")
    value = argv[i + 1]
    del argv[i:i + 2]
    return value


def render(cutout):
    """Every surface, as {relative out-path: image}."""
    out = {}
    out[MODEL_REL / "combat_model.png"] = fit(cutout, 240, 280)

    portrait = head_crop(cutout, 132, 195, head_frac=PORTRAIT_HEAD_FRAC,
                         centre_on="head")
    out[UI_REL / "select_portrait.png"] = portrait
    out[UI_REL / "select_portrait_locked.png"] = locked_variant(portrait)
    out[UI_REL / "char_icon.png"] = head_crop(
        cutout, 88, 88, head_frac=ICON_HEAD_FRAC, centre_on="head")
    out[UI_REL / "map_marker.png"] = head_crop(
        cutout, 49, 64, head_frac=MARKER_HEAD_FRAC, centre_on="head")

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
    out[UI_REL / "selection_splash.png"] = splash
    return out


def main(argv):
    argv = list(argv)
    art_root = _take(argv, "--art-root")
    base = Path(art_root).resolve() if art_root else ROOT
    check = "--check" in argv

    source = base / SOURCE_REL
    if not source.exists():
        # Tier F art is absent on a runner or a fresh clone.
        print(f"SKIPPED: no source at {source}")
        return 0
    cutout = Image.open(source).convert("RGBA")

    stale = []
    for rel, img in render(cutout).items():
        path = base / rel
        if check:
            if not path.exists():
                stale.append(f"{rel} does not exist")
            elif Image.open(path).convert("RGBA").tobytes() != img.tobytes():
                stale.append(f"{rel} differs from a fresh derivation")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path)
        print(f"  {rel.as_posix()}  {img.width}x{img.height}")
    if check:
        for s in stale:
            print("STALE: " + s, file=sys.stderr)
        if not stale:
            print("gen_varka_stills --check: OK")
        return 1 if stale else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
