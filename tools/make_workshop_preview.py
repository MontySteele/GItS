#!/usr/bin/env python3
"""Compose the Steam Workshop preview from the five characters' idle renders.

    python tools/make_workshop_preview.py            # writes ImageGen/images/workshop_preview.png
    python tools/make_workshop_preview.py --out x.png

Each idle frame sheet (`ImageGen/images/**/model/frames/<id>_idle.png`) is a
grid of frames; the first frame is cut out by its alpha and scaled by canon
height (Klee 0.72 of an adult, memory "scale by real heights"), then the five
stand on one floor over a dark radial gradient, Klee in front. 1280x720,
well under the Workshop's 1 MB limit. `tools/package_workshop.py` uses the
result as `image.png`; the in-game Mods-screen badge (`mod_image.png`) is a
separate file and is not touched.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "ImageGen" / "images"
OUT = IMAGES / "workshop_preview.png"
W, H = 1280, 720
BASE = 600          # an adult's height in pixels
FLOOR = H - 40

# (sheet, height as a share of an adult, centre x), drawn outside-in
CAST = [
    ("varka/model/frames/varka_idle.png", 1.00, 230),
    ("yae/model/frames/yae_idle.png", 0.95, 1050),
    ("furina/model/frames/furina_idle.png", 0.90, 450),
    ("kokomi/model/frames/kokomi_idle.png", 0.90, 830),
    ("model/frames/klee_idle.png", 0.72, 625),
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


def background() -> Image.Image:
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H * 0.55) / H) ** 2)
    t = np.clip(d / 0.75, 0, 1)[..., None]
    rgb = np.array([46, 58, 96]) * (1 - t) + np.array([12, 14, 26]) * t
    return Image.fromarray(rgb.astype("uint8"), "RGB").convert("RGBA")


def compose() -> Image.Image:
    canvas = background()
    for rel, share, cx in CAST:
        frame = first_frame(IMAGES / rel)
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
