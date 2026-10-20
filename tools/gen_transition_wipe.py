#!/usr/bin/env python3
"""Generate the character-select transition wipe textures (Tier O, procedural).

The game's transition materials are a tiny canvas_item shader that sweeps a
threshold over a grayscale texture: bright pixels wipe first, dark last
(see materials/transitions/ironclad_transition_mat.tres in the game pck).

Each character gets a wipe that reads as their element:
    klee    a blast expanding from center -- radial gradient, ragged edge
    kokomi  a tide coming in -- sweeps bottom-up behind a rolling wave crest
    varka   a gale -- a two-armed vortex that opens from the centre outward
    yae     a lightning stroke -- a forked bolt splits the screen corner to
            corner and the reveal spreads out from it (Electro)

Furina deliberately has no wipe of her own and keeps Klee's via build_pck's
Copy-FurinaFallback (art-sprint-spec sec.8 sanctions the shared fallback).

Deterministic (fixed seed per character) so the pck build is reproducible.
Outputs are not in art/plan.tsv because they are generated, not wiki-sourced;
build_pck.ps1 picks them up from the ui/ dirs like every other ui texture.
Registered in art_lint.GENERATOR_OWNED so no plan row can claim these paths.

Usage: .venv/Scripts/python tools/gen_transition_wipe.py [--art-root <checkout>] [--chars yae,...]

--chars writes only those characters' wipes (default: all), so a pass on one
kit never rewrites another kit's file.

--art-root writes under another checkout's ImageGen/, the way art_process.py's
flag does: a worktree must never link the gitignored tree in.
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
W, H = 960, 540


def value_noise(rng, grid, blur):
    """Low-frequency value noise: random grid, upscaled smoothly, blurred."""
    small = Image.new("L", (grid, grid))
    small.putdata([rng.randrange(256) for _ in range(grid * grid)])
    return small.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur))


def klee_blast(rng):
    """Bright center wipes first; +-18% ragged edge reads as flame licks."""
    npx = value_noise(rng, 12, 6).load()
    img = Image.new("L", (W, H))
    px = img.load()
    cx, cy = W / 2, H / 2
    max_r = math.hypot(cx, cy)
    for y in range(H):
        for x in range(W):
            r = math.hypot(x - cx, y - cy) / max_r      # 0 center .. 1 corner
            n = (npx[x, y] / 255 - 0.5) * 0.36          # +-18% ragged edge
            v = 1.0 - (r + n)                            # bright center wipes first
            px[x, y] = max(0, min(255, round(v * 255)))
    return img


def kokomi_tide(rng):
    """Bottom wipes first, behind a rolling crest.

    Two sine components of different wavelength keep the crest from reading as
    a machined ripple, and the noise term is gentler than Klee's (+-11% vs
    +-18%): a tide edge is smooth where a blast edge is ragged.
    """
    npx = value_noise(rng, 9, 9).load()
    img = Image.new("L", (W, H))
    px = img.load()
    phase = rng.random() * math.tau
    for y in range(H):
        base = y / H                                     # 0 top .. 1 bottom
        for x in range(W):
            u = x / W
            crest = (0.055 * math.sin(u * math.tau * 1.5 + phase)
                     + 0.028 * math.sin(u * math.tau * 3.7 + phase * 2.1))
            n = (npx[x, y] / 255 - 0.5) * 0.22           # +-11%, softer edge
            v = base + crest + n                         # bright bottom wipes first
            px[x, y] = max(0, min(255, round(v * 255)))
    return img


def varka_gale(rng):
    """Centre wipes first, carried round a two-armed vortex (Anemo).

    A pure radial term (Klee's blast) plus a spiral term whose arms trail as
    the radius grows, so the reveal reads as wind winding outward rather than
    an explosion. Noise is gentle (+-9%): a gust edge is streaky, not ragged.
    """
    npx = value_noise(rng, 10, 7).load()
    img = Image.new("L", (W, H))
    px = img.load()
    cx, cy = W / 2, H / 2
    max_r = math.hypot(cx, cy)
    phase = rng.random()
    for y in range(H):
        for x in range(W):
            r = math.hypot(x - cx, y - cy) / max_r
            a = (math.atan2(y - cy, x - cx) / math.tau + phase) % 1.0
            arm = (2 * a + 1.6 * r) % 1.0                # two trailing arms
            n = (npx[x, y] / 255 - 0.5) * 0.18
            v = 1.0 - (0.72 * r + 0.28 * arm + n)
            px[x, y] = max(0, min(255, round(v * 255)))
    return img


def _bolt(rng, a, b, depth, jag):
    """A jagged polyline from a to b by midpoint displacement: each segment's
    midpoint pushed sideways by up to `jag` of its length, `depth` times."""
    pts = [a, b]
    for _ in range(depth):
        out = [pts[0]]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            dx, dy = x1 - x0, y1 - y0
            ln = math.hypot(dx, dy)
            off = (rng.random() * 2 - 1) * jag * ln
            out += [((x0 + x1) / 2 - dy / ln * off, (y0 + y1) / 2 + dx / ln * off), (x1, y1)]
        pts = out
    return pts


def _seg_dist(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def yae_bolt(rng):
    """The bolt wipes first and the reveal spreads out from it (Electro).

    One main stroke corner to corner (top right to bottom left) and one fork
    off its middle toward the bottom right; brightness falls with distance to
    the nearest stroke, with a ragged +-8% noise so the spreading edge
    crackles rather than rings. Computed on a quarter grid and upscaled
    smoothly: the falloff is low frequency, and the per-pixel distance to
    every segment at full size is slow in pure Python."""
    main = _bolt(rng, (W * 0.84, -10), (W * 0.14, H + 10), 5, 0.16)
    mid = main[len(main) // 2]
    fork = _bolt(rng, mid, (W * 0.78, H + 10), 4, 0.18)
    segs = list(zip(main, main[1:])) + list(zip(fork, fork[1:]))
    q = 4
    small = Image.new("L", (W // q, H // q))
    sp = small.load()
    ds = [[min(_seg_dist(x * q + q / 2, y * q + q / 2, a, b) for a, b in segs) for x in range(W // q)]
          for y in range(H // q)]
    max_d = max(max(row) for row in ds)       # the farthest corner wipes last
    for y in range(H // q):
        for x in range(W // q):
            sp[x, y] = max(0, min(255, round(255 * ds[y][x] / max_d)))
    dist = small.resize((W, H), Image.BICUBIC).load()
    npx = value_noise(rng, 14, 5).load()
    img = Image.new("L", (W, H))
    px_ = img.load()
    for y in range(H):
        for x in range(W):
            n = (npx[x, y] / 255 - 0.5) * 0.16
            v = 1.0 - (dist[x, y] / 255 + n)
            px_[x, y] = max(0, min(255, round(v * 255)))
    return img


# seed, builder, out-path. Klee's seed and builder are unchanged from the
# original single-character script, so his texture stays byte-identical.
WIPES = {
    "klee":   (20260720, klee_blast,  "ImageGen/images/ui/transition_wipe.png"),
    "kokomi": (20260725, kokomi_tide, "ImageGen/images/kokomi/ui/transition_wipe.png"),
    "varka":  (20260929, varka_gale,  "ImageGen/images/varka/ui/transition_wipe.png"),
    "yae":    (20261019, yae_bolt,    "ImageGen/images/yae/ui/transition_wipe.png"),
}


def main(argv):
    base = ROOT
    if "--art-root" in argv:
        i = argv.index("--art-root")
        if i + 1 >= len(argv):
            sys.exit("--art-root needs a value")
        base = Path(argv[i + 1]).resolve()
    names = list(WIPES)
    if "--chars" in argv:
        i = argv.index("--chars")
        if i + 1 >= len(argv):
            sys.exit("--chars needs a value")
        names = [n for n in argv[i + 1].split(",") if n]
        unknown = [n for n in names if n not in WIPES]
        if unknown:
            sys.exit(f"unknown character(s): {', '.join(unknown)}; known: {', '.join(WIPES)}")
    for name in names:
        seed, build, out = WIPES[name]
        img = build(random.Random(seed))
        path = base / out
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path)
        print(f"wrote {path} ({W}x{H})  [{name}]")


if __name__ == "__main__":
    main(sys.argv[1:])
