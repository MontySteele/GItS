"""Shared framing math for the per-character still surfaces.

Extracted from tools/gen_furina_stills.py (animation sprint 2, track B4) when
Kokomi needed the same six surfaces. It is deliberately a MODULE rather than a
copied block: B4's verdict was a centring rule, and a rule that exists in two
files drifts the moment one of them is touched. Furina's outputs are pinned
byte-for-byte by tier0/tests/test_char_stills.py so this extraction cannot
silently reframe art the user already approved.

THE CENTRING RULE (B4). Every framing here is computed from the render's ALPHA
bounding box, never from the image frame -- framing off the frame is precisely
the bug B4 fixed. Horizontal centre is the alpha bbox centre; vertical framing
is anchored per surface (feet-down for the full body, head-down for portraits).

Callers supply a CUTOUT -- a render whose alpha is the subject. Where the
official art ships on a white plate instead (Kokomi's Portrait), see
`cutout_from_plate` below.
"""
from collections import deque

import numpy as np
from PIL import Image, ImageEnhance

# Alpha at or below this reads as background. Matches the B4 original.
ALPHA_FLOOR = 8

# Fraction of subject height treated as "the head band" by centre_on="head".
# 0.18 comfortably contains the head and hair ornaments on a full-body render
# without reaching the hips, where the costume silhouette widens asymmetrically.
HEAD_BAND = 0.18


def alpha_bbox(im):
    """(x0, y0, x1, y1) of the subject -- the half-open box of visible alpha."""
    a = np.asarray(im.convert("RGBA"))[..., 3] > ALPHA_FLOOR
    ys, xs = np.nonzero(a)
    if not len(xs):
        raise ValueError("render has no visible alpha; is this a cutout?")
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


def head_crop(im, box_w, box_h, head_frac=0.52, centre_on="bbox"):
    """Portrait framing: top of the alpha bbox down, centred on the head.

    `centre_on` picks what "centred" means horizontally:

    "bbox" -- the midpoint of the full-body alpha bbox. Correct when the
        silhouette is the figure and nothing else, which is Furina's cutout.
        This is the B4 default and Furina's outputs are pinned to it.

    "head" -- the MEDIAN alpha column within the top band of the subject.
        Needed when the render carries composition outside the body: Kokomi's
        Portrait sweeps a large fin to her right and floats a fish beside her
        raised hand, which drags the bbox midpoint 275px right of her actual
        head and lands her face visibly left of frame. Median rather than the
        band's min/max midpoint because median is mass-weighted and so ignores
        a small bright fish: measured across top-band sizes of 12/18/25/35%,
        the median moves 2165->2221 while the min/max midpoint swings
        2191->2667->2608->2215.

    Framing off anything but the subject is the defect B4 exists to prevent;
    "head" is that same rule applied to a noisier silhouette.
    """
    x0, y0, x1, y1 = alpha_bbox(im)
    # The head occupies roughly the top third of a full-body render; frame it
    # by taking a window whose height is head_frac of the subject height.
    sub_h = int((y1 - y0) * head_frac)
    sub_w = int(sub_h * box_w / box_h)
    if centre_on == "head":
        band = np.asarray(im.convert("RGBA"))[y0:y0 + max(1, int((y1 - y0) * HEAD_BAND)),
                                              :, 3] > ALPHA_FLOOR
        cols = np.nonzero(band)[1]
        cx = int(np.median(cols)) if len(cols) else (x0 + x1) // 2
    elif centre_on == "bbox":
        cx = (x0 + x1) // 2
    else:
        raise ValueError(f"unknown centre_on: {centre_on!r}")
    left = max(0, cx - sub_w // 2)
    crop = im.crop((left, y0, left + sub_w, y0 + sub_h))
    return crop.resize((box_w, box_h), Image.LANCZOS)


def locked_variant(portrait):
    """The base game's locked treatment: same crop, desaturated and darkened.

    Deriving it from the finished portrait (rather than re-cropping) is what
    guarantees the two are framed identically -- they were separate crops
    before B4, which is exactly how they drifted apart.
    """
    locked = ImageEnhance.Color(portrait.convert("RGB")).enhance(0.18)
    locked = ImageEnhance.Brightness(locked).enhance(0.42)
    locked_rgba = locked.convert("RGBA")
    locked_rgba.putalpha(portrait.getchannel("A"))
    return locked_rgba


def cutout_from_plate(im, threshold=246):
    """Key a flat white plate off a render, returning an RGBA cutout.

    Furina's governing render was already a transparent cutout. Kokomi's
    Portrait (4900x5700) is the same kind of clean full-body art but ships
    FLATTENED ONTO WHITE, so `alpha_bbox` sees the whole frame and every
    framing rule above silently degrades to frame-centring -- the B4 bug,
    reintroduced by the source rather than by the code.

    Keying by colour alone is wrong here: she wears white stockings and a white
    kimono panel, and a global white test punches holes straight through her.
    So we key by CONNECTIVITY -- only near-white that is reachable from the
    image border is background. Interior whites are enclosed by her outline and
    are kept.

    Scanline flood fill (span-per-row, numpy row slices) rather than
    per-pixel recursion: the plate is 28M pixels.
    """
    rgb = np.asarray(im.convert("RGB"))
    h, w = rgb.shape[:2]
    near_white = rgb.min(axis=2) >= threshold

    filled = np.zeros_like(near_white)
    stack = deque()
    for x in range(w):
        if near_white[0, x]:
            stack.append((0, x))
        if near_white[h - 1, x]:
            stack.append((h - 1, x))
    for y in range(h):
        if near_white[y, 0]:
            stack.append((y, 0))
        if near_white[y, w - 1]:
            stack.append((y, w - 1))

    while stack:
        y, x = stack.pop()
        if filled[y, x] or not near_white[y, x]:
            continue
        row, frow = near_white[y], filled[y]
        x0 = x
        while x0 > 0 and row[x0 - 1] and not frow[x0 - 1]:
            x0 -= 1
        x1 = x
        while x1 < w - 1 and row[x1 + 1] and not frow[x1 + 1]:
            x1 += 1
        frow[x0:x1 + 1] = True
        for ny in (y - 1, y + 1):
            if not 0 <= ny < h:
                continue
            seg = (near_white[ny] & ~filled[ny])[x0:x1 + 1]
            idx = np.flatnonzero(seg)
            if not len(idx):
                continue
            # One seed per contiguous run in the span above/below.
            starts = np.concatenate(([idx[0]], idx[np.flatnonzero(np.diff(idx) > 1) + 1]))
            for s in starts:
                stack.append((ny, x0 + int(s)))

    alpha = np.where(filled, 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([rgb, alpha]), "RGBA")
