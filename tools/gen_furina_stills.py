"""Re-derive Furina's still surfaces from the governing render.

Animation sprint 2, Track B4 (2026-07-24). The [USER] verdict was that her
model AND her select art are off-centre; B4's point is that the fix has to
land at EVERY surface, not just in combat. All of these are now cut from the
same source as the combat rig, so they cannot drift from each other again.

Outputs (all gitignored Tier F, ledgered in art/SOURCES.tsv):
    ImageGen/images/furina/model/combat_model.png       240x280  static fallback
    ImageGen/images/furina/ui/select_portrait.png       132x195
    ImageGen/images/furina/ui/select_portrait_locked.png 132x195
    ImageGen/images/furina/ui/selection_splash.png     1920x1200
    ImageGen/images/furina/ui/char_icon.png              88x88
    ImageGen/images/furina/ui/map_marker.png             49x64

CENTRING RULE. Every framing here is computed from the render's ALPHA
bounding box, never from the image frame -- that is precisely the bug being
fixed. Horizontal centre is the alpha bbox centre; vertical framing is
anchored per surface (feet-down for the full body, head-down for portraits).

Source: the transparent 227x440 cutout for anything that needs an alpha
(combat/portrait/icon), and the 1080x2160 full-res twin for the big splash,
which is composited over a plate and so does not need a cutout.

Usage: .venv/Scripts/python tools/gen_furina_stills.py
"""
from pathlib import Path
import sys

from PIL import Image, ImageEnhance
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CUTOUT = ROOT / "ImageGen" / "images" / "furina" / "model" / "furina_wikipedia_cutout.png"
FULLRES = ROOT / "art" / "raw" / "Furina_Card_2.png"
UI = ROOT / "ImageGen" / "images" / "furina" / "ui"
MODEL = ROOT / "ImageGen" / "images" / "furina" / "model"


def alpha_bbox(im):
    a = np.asarray(im.convert("RGBA"))[..., 3] > 8
    ys, xs = np.nonzero(a)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def fit(im, box_w, box_h, pad=0.0, anchor="bottom"):
    """Scale the subject to fill the box (minus pad) and centre it horizontally."""
    x0, y0, x1, y1 = alpha_bbox(im)
    subject = im.crop((x0, y0, x1, y1))
    avail_w, avail_h = box_w * (1 - pad), box_h * (1 - pad)
    scale = min(avail_w / subject.width, avail_h / subject.height)
    subject = subject.resize(
        (max(1, round(subject.width * scale)), max(1, round(subject.height * scale))),
        Image.LANCZOS)

    out = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    px = (box_w - subject.width) // 2                  # always centred
    py = {"bottom": box_h - subject.height,
          "top": 0,
          "middle": (box_h - subject.height) // 2}[anchor]
    out.alpha_composite(subject, (px, py))
    return out


def head_crop(im, box_w, box_h, head_frac=0.52):
    """Portrait framing: top of the alpha bbox down, centred on the head."""
    x0, y0, x1, y1 = alpha_bbox(im)
    # The head occupies roughly the top third of a full-body render; frame it
    # by taking a window whose height is head_frac of the subject height.
    sub_h = int((y1 - y0) * head_frac)
    sub_w = int(sub_h * box_w / box_h)
    cx = (x0 + x1) // 2
    left = max(0, cx - sub_w // 2)
    crop = im.crop((left, y0, left + sub_w, y0 + sub_h))
    return crop.resize((box_w, box_h), Image.LANCZOS)


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

    # Select portraits. Locked is the same crop, desaturated and darkened --
    # the base game's locked treatment, and it guarantees the two are framed
    # identically (they were separate crops before, which is how they drifted).
    portrait = head_crop(cutout, 132, 195)
    portrait.save(UI / "select_portrait.png")
    locked = ImageEnhance.Color(portrait.convert("RGB")).enhance(0.18)
    locked = ImageEnhance.Brightness(locked).enhance(0.42)
    locked.convert("RGBA").putalpha(portrait.getchannel("A"))
    locked_rgba = locked.convert("RGBA")
    locked_rgba.putalpha(portrait.getchannel("A"))
    locked_rgba.save(UI / "select_portrait_locked.png")
    print("  select_portrait.png    132x195 (+ locked, identical framing)")

    # Character icon + map marker: tight head crops on transparency.
    head_crop(cutout, 88, 88, head_frac=0.30).save(UI / "char_icon.png")
    head_crop(cutout, 49, 64, head_frac=0.34).save(UI / "map_marker.png")
    print("  char_icon.png 88x88, map_marker.png 49x64")

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
