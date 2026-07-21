#!/usr/bin/env python3
"""Autocrop + aspect-fit for splash/Wish card art.

Problem this solves: Wish/splash sources (typically 2048x1024) frame the
figure in a large transparent void, so at 500x380 card size the character
shrinks to a blob. This crops to the content, fits the card aspect, and
resizes. Sources are larger than the card, so this is a DOWNSCALE -- no
quality loss.

Two alpha thresholds, deliberately:
  - CENTER_THRESH (high, ~200): the opaque figure. Used to compute the
    centering box, so composition centers on the CHARACTER, not on
    asymmetric VFX that would otherwise pull the figure off-center.
  - INCLUDE_THRESH (low, ~10): figure + faint effects. The final crop is
    expanded to include these so the splash (Fischl's raven, Chevreuse's
    musket-flash) isn't clipped.

LANDED as the plan.tsv mode 'cover_autocrop' (art_process.cover_autocrop,
2026-07-21), which supersedes this script for pipeline use. Two differences
in the ported version, both learned from rendering the real set:
  - it gained a fit flag (cover|contain). This file implements the CONTAIN
    behaviour only (crop to content, letterbox to the card aspect); the
    pipeline defaults to cover, which fills the frame and centre-crops on
    the figure.
  - it uses PIL's thresholded getbbox instead of numpy, so the art tooling
    keeps a single dependency.
Kept as the standalone prototype for one-off crops and for diffing against
the pipeline. Note the mode is a no-op on full-bleed sources (the Birthday
renders are 100% opaque); it only pays off on float-in-void art like
Klee Wish, where content is 35% of the canvas.

Usage: autocrop_card_art.py <in.png> <out.png> [card_w card_h]
"""
import sys
from PIL import Image
import numpy as np

CENTER_THRESH = 200
INCLUDE_THRESH = 10
MARGIN_FRAC = 0.06


def autocrop(inp, out, card_w=500, card_h=380):
    im = Image.open(inp).convert("RGBA")
    a = np.array(im)[:, :, 3]

    inc_ys, inc_xs = np.where(a > INCLUDE_THRESH)
    if len(inc_xs) == 0:
        # fully transparent or opaque-less; fall back to a plain resize
        im.resize((card_w, card_h), Image.LANCZOS).save(out)
        return "fallback-resize"

    ix0, ix1, iy0, iy1 = inc_xs.min(), inc_xs.max(), inc_ys.min(), inc_ys.max()

    ctr_ys, ctr_xs = np.where(a > CENTER_THRESH)
    if len(ctr_xs) > 0:
        cx = (ctr_xs.min() + ctr_xs.max()) / 2
        cy = (ctr_ys.min() + ctr_ys.max()) / 2
    else:
        cx, cy = (ix0 + ix1) / 2, (iy0 + iy1) / 2

    # include-box, expanded by margin
    cw, ch = ix1 - ix0, iy1 - iy0
    mx, my = int(cw * MARGIN_FRAC), int(ch * MARGIN_FRAC)
    x0 = max(0, ix0 - mx); y0 = max(0, iy0 - my)
    x1 = min(im.width, ix1 + mx); y1 = min(im.height, iy1 + my)

    crop = im.crop((x0, y0, x1, y1))

    # fit to card aspect on a transparent canvas, biasing the pad so the
    # opaque-figure center sits at the card center
    target_ar = card_w / card_h
    cw, ch = crop.size
    ar = cw / ch
    if ar > target_ar:
        new_h = int(round(cw / target_ar))
        # where is the figure center within the crop, vertically?
        fig_cy = cy - y0
        pad_top = int(round(new_h / 2 - fig_cy))
        pad_top = max(0, min(new_h - ch, pad_top))
        canvas = Image.new("RGBA", (cw, new_h), (0, 0, 0, 0))
        canvas.paste(crop, (0, pad_top), crop)
    else:
        new_w = int(round(ch * target_ar))
        fig_cx = cx - x0
        pad_left = int(round(new_w / 2 - fig_cx))
        pad_left = max(0, min(new_w - cw, pad_left))
        canvas = Image.new("RGBA", (new_w, ch), (0, 0, 0, 0))
        canvas.paste(crop, (pad_left, 0), crop)

    canvas.resize((card_w, card_h), Image.LANCZOS).save(out)
    return "ok"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: autocrop_card_art.py <in.png> <out.png> [w h]")
        sys.exit(2)
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 500
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 380
    print(autocrop(sys.argv[1], sys.argv[2], w, h))
