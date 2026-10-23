#!/usr/bin/env python3
"""Compose the Steam Workshop preview from the five characters' idle renders.

    python tools/make_workshop_preview.py            # writes ImageGen/images/workshop_preview.png
    python tools/make_workshop_preview.py --out x.png

Each idle frame sheet (`ImageGen/images/**/model/frames/<id>_idle.png`) is a
grid of frames, except Kokomi's: she stands in her character-select pose
from a single still (chosen when her idle's far hand read as a dark tangle
at this size; kept after the 2026-10-22 idle fix, which brought the idle
close to the select pose, so the still is no worse and needs no re-pick),
`kokomi/model/frames/kokomi_preview.png` (char_render/render.py
`--stills select` at the combat ppu and outline, painted by post.py). The
first frame is cut out by its alpha and scaled by canon
height (Klee 0.72 of an adult, memory "scale by real heights"), then the five
stand on one floor over a dark radial gradient, Klee in front. 1280x720,
well under the Workshop's 1 MB limit. `tools/package_workshop.py` uses the
result as `image.png`; the in-game Mods-screen badge (`mod_image.png`) is a
separate file and is not touched.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "ImageGen" / "images"
OUT = IMAGES / "workshop_preview.png"
W, H = 1280, 720
BASE = 600          # an adult's height in pixels
FLOOR = H - 40

# (sheet, height as a share of an adult, centre x, frame), drawn outside-in.
# `frame` None is the sheet's first cell; ("sheet", i) is frame i of that
# sheet in `tools/char_render/<char>_frames.json`, picked so the five stand in
# five different poses (user, 2026-10-22: Varka's second sword floated behind
# him, and Furina, Kokomi and Yae all stood hand on hip, palm up).
CAST = [
    ("varka/model/frames/varka_merchant.png", 1.00, 252, None),
    ("yae/model/frames/yae_cast.png", 0.95, 1115, ("cast", 10)),
    ("furina/model/frames/furina_rejoice.png", 0.90, 545, ("rejoice", 15)),
    ("kokomi/model/frames/kokomi_preview.png", 0.90, 890, None),
    ("model/frames/klee_idle.png", 0.72, 705, None),
]


def _runs(mask: np.ndarray) -> list[tuple[int, int]]:
    out, start = [], None
    for i, on in enumerate(mask):
        if on and start is None:
            start = i
        elif not on and start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(mask)))
    return out


def first_frame(sheet: Path) -> Image.Image:
    im = Image.open(sheet).convert("RGBA")
    alpha = np.array(im)[:, :, 3] > 8
    r0, r1 = _runs(alpha.any(1))[0]
    c0, c1 = _runs(alpha[r0:r1].any(0))[0]
    cell = im.crop((c0, r0, c1, r1))
    return cell.crop(cell.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox())


def sheet_frame(rel: str, sheet: str, index: int) -> Image.Image:
    """Frame `index` of `sheet`, cut by its packed rect."""
    char = rel.split("/")[0]
    meta = json.loads((ROOT / "tools" / "char_render" / f"{char}_frames.json")
                      .read_text(encoding="utf-8"))["sheets"][sheet]
    f = meta["frames"][index]
    x, y, w, h = f["rect"][:4]
    page = IMAGES / char / "model" / "frames" / meta["pages"][f["page"]]["file"]
    cell = Image.open(page).convert("RGBA").crop((x, y, x + w, y + h))
    return cell.crop(cell.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox())


def background() -> Image.Image:
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H * 0.55) / H) ** 2)
    t = np.clip(d / 0.75, 0, 1)[..., None]
    rgb = np.array([46, 58, 96]) * (1 - t) + np.array([12, 14, 26]) * t
    return Image.fromarray(rgb.astype("uint8"), "RGB").convert("RGBA")


def compose() -> Image.Image:
    canvas = background()
    for rel, share, cx, pick in CAST:
        frame = first_frame(IMAGES / rel) if pick is None else sheet_frame(rel, *pick)
        h = int(BASE * share)
        frame = frame.resize((int(frame.width * h / frame.height), h), Image.LANCZOS)
        shadow = Image.new("RGBA", (int(frame.width * 0.9), 40), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).ellipse((0, 0, shadow.width, 40), fill=(0, 0, 0, 110))
        shadow = shadow.filter(ImageFilter.GaussianBlur(8))
        canvas.alpha_composite(shadow, (cx - shadow.width // 2, FLOOR - 22))
        canvas.alpha_composite(frame, (cx - frame.width // 2, FLOOR - frame.height))
    return canvas.convert("RGB")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    compose().save(args.out, optimize=True)
    print(f"{args.out} {args.out.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
