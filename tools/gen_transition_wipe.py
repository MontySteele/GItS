#!/usr/bin/env python3
"""Generate Klee's character-select transition wipe texture (Tier O, procedural).

The game's transition materials are a tiny canvas_item shader that sweeps a
threshold over a grayscale texture: bright pixels wipe first, dark last
(see materials/transitions/ironclad_transition_mat.tres in the game pck).
Klee's read: a blast expanding from center -- radial gradient, ragged edge.

Deterministic (fixed seed) so the pck build is reproducible. Output is not in
art/plan.tsv because it is generated, not wiki-sourced; build_pck.ps1 picks it
up from ImageGen/images/ui/ like every other ui texture.
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "ImageGen/images/ui/transition_wipe.png"
W, H = 960, 540
SEED = 20260720

rng = random.Random(SEED)

# Low-frequency value noise for the ragged blast edge: random grid, upscaled
# smoothly, blurred. Amplitude ~18% of the radius reads as flame licks without
# breaking the overall outward sweep.
GRID = 12
noise_small = Image.new("L", (GRID, GRID))
noise_small.putdata([rng.randrange(256) for _ in range(GRID * GRID)])
noise = noise_small.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))
npx = noise.load()

img = Image.new("L", (W, H))
px = img.load()
cx, cy = W / 2, H / 2
max_r = math.hypot(cx, cy)
for y in range(H):
    for x in range(W):
        r = math.hypot(x - cx, y - cy) / max_r          # 0 center .. 1 corner
        n = (npx[x, y] / 255 - 0.5) * 0.36              # +-18% ragged edge
        v = 1.0 - (r + n)                                # bright center wipes first
        px[x, y] = max(0, min(255, round(v * 255)))

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT)
print(f"wrote {OUT} ({W}x{H})")
