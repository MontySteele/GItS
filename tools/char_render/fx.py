"""Neutral slash trails and impact bursts for a bladed clip, from the blade
track render.py records. numpy and Pillow only; no Blender, no model.

    from fx import clip_fx, tint
    frames, first, pad = clip_fx(meta)     # meta: render.py's <clip>.json

Varka's attacks carry the element he strikes with ([USER], 2026-10-13: "special
animations (effect colors) for the element of his attack - anemo, pyro, hydro,
electro or cryo"). The body is rendered once, colourless; the colour lives in
this separate layer, drawn over the body and tinted per element at runtime.

THE LAYER, per frame, is RGBA where
  A        coverage (0 nothing, 1 solid);
  R=G=B    heat: 1.0 the white-hot core along the blade's edge, about 0.5 the
           soft rim and glow.
A plain `modulate = element colour` tints it flat. The look in the review
sheets is tint(): colour = mix(element, white, smoothstep(0.72, 1.0, heat)),
alpha unchanged -- a two-line CanvasItem shader in the game.

The trails come from the blade's own swept arc: render.py samples each blade's
base (past the guard) and tip in canvas px SUBSTEPS times per frame interval.
For each frame at time t inside a clip's trail window, the ribbon between the
blade's outer part (TRAIL_INNER of the way from base to tip, narrowing to
TRAIL_TAPER at the tail) and its tip is filled over the last TRAIL_AGE
seconds, oldest faintest: a crescent. Each marked burst
(`bursts` in the clip spec) adds a ring, a flash and radial streaks where the
blade strikes ("slash"), or a flattened shock ring and rising streaks on the
ground ("ground"). Every pixel length is at REF_PPU and scales with the clip's
ppu. Deterministic: same meta, same pixels.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image

REF_PPU = 263.4          # Varka's combat texture scale (2x of 1080p)
TRAIL_INNER = 0.60       # the ribbon covers the blade from here (0 base, 1 tip) out to the tip, at its head
TRAIL_TAPER = 0.85       # ... and its tail narrows to this, so the sweep reads as a crescent
TRAIL_AGE = 0.13         # seconds of sweep a frame shows (a trail window's `age` overrides it)
TRAIL_FADE = 0.12        # seconds the last ribbon takes to fade after the window closes
GLOW_SIGMA = 7.0         # px at REF_PPU
BURST_LEN = 0.26         # seconds a burst lasts
PAD = 160                # px at REF_PPU added round the clip canvas for bursts
SUPER = 2                # supersampling for the polygon fill
#: The mod's element colours: KleeMod.Vfx.ReactionFx.ElementFlashHex
#: (klee-mod/KleeCode/Vfx/ReactionFx.cs), the one complete element table.
ELEMENTS = {"anemo": "#8fffd6", "pyro": "#ff9a5c", "hydro": "#5cb8ff", "electro": "#c08cff", "cryo": "#a8f0ff"}


def hex_rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


# ------------------------------------------------------------------ rasterising
def fill_triangle(buf, tri, vals):
    """Max-composite one triangle into `buf` with its three vertex values
    interpolated (barycentric). tri: [(x, y)] in buf px."""
    (x0, y0), (x1, y1), (x2, y2) = tri
    H, W = buf.shape
    bx0, bx1 = max(0, int(math.floor(min(x0, x1, x2)))), min(W, int(math.ceil(max(x0, x1, x2))) + 1)
    by0, by1 = max(0, int(math.floor(min(y0, y1, y2)))), min(H, int(math.ceil(max(y0, y1, y2))) + 1)
    if bx0 >= bx1 or by0 >= by1:
        return
    den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(den) < 1e-9:
        return
    ys, xs = np.mgrid[by0:by1, bx0:bx1].astype(np.float32) + 0.5
    l0 = ((y1 - y2) * (xs - x2) + (x2 - x1) * (ys - y2)) / den
    l1 = ((y2 - y0) * (xs - x2) + (x0 - x2) * (ys - y2)) / den
    l2 = 1 - l0 - l1
    inside = (l0 >= -1e-4) & (l1 >= -1e-4) & (l2 >= -1e-4)
    v = l0 * vals[0] + l1 * vals[1] + l2 * vals[2]
    sub = buf[by0:by1, bx0:bx1]
    np.maximum(sub, np.where(inside, v, 0), out=sub)


def fill_quad(buf, quad, vals):
    fill_triangle(buf, (quad[0], quad[1], quad[2]), (vals[0], vals[1], vals[2]))
    fill_triangle(buf, (quad[0], quad[2], quad[3]), (vals[0], vals[2], vals[3]))


def stroke(buf, a, b, width, val):
    """A tapered line from a (full width) to b (a point), as a triangle pair."""
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    n = math.hypot(dx, dy)
    if n < 1e-6:
        return
    nx, ny = -dy / n * width / 2, dx / n * width / 2
    fill_triangle(buf, ((ax + nx, ay + ny), (ax - nx, ay - ny), (bx, by)), (val, val, val * 0.6))


def gauss(x, sigma):
    if sigma <= 0:
        return x
    r = max(1, int(round(sigma * 3)))
    t = np.arange(-r, r + 1, dtype=np.float32)
    k = np.exp(-t * t / (2 * sigma * sigma))
    k /= k.sum()
    p = np.pad(x, r, mode="constant")
    H, W = x.shape
    tmp = sum(k[i] * p[:, i:i + W] for i in range(2 * r + 1))
    return sum(k[i] * tmp[i:i + H] for i in range(2 * r + 1))


def downsample(x, f):
    if f == 1:
        return x
    H, W = x.shape
    return x[:H - H % f, :W - W % f].reshape(H // f, f, W // f, f).mean((1, 3))


# ------------------------------------------------------------------ the layer
def _lerp(p, q, k):
    return (p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k)


def _samples(meta, side, t0, t1):
    """The blade track samples of `side` with t0 <= t <= t1, oldest first."""
    return [s for s in meta["blades"] if t0 - 1e-6 <= s["t"] <= t1 + 1e-6 and s.get(side)]


def _sample_at(meta, side, t):
    best = min((s for s in meta["blades"] if s.get(side)), key=lambda s: abs(s["t"] - t))
    return best[side]


def trail_heat(meta, t, shape, shift, s):
    """The ribbon coverage of every trail window open at t (supersampled)."""
    buf = np.zeros(shape, np.float32)
    k = SUPER
    for win in meta.get("trails", []):
        if not (win["from"] - 1e-6 <= t <= win["to"] + TRAIL_FADE):
            continue
        fade = 1.0 if t <= win["to"] else 1 - (t - win["to"]) / TRAIL_FADE
        t_hi = min(t, win["to"])
        age = win.get("age", TRAIL_AGE)
        sm = _samples(meta, win["blade"], max(win["from"], t_hi - age), t_hi)
        for a, b in zip(sm, sm[1:]):
            ages = [min(1.0, (t_hi - x["t"]) / age) for x in (a, b)]
            w = [(1 - g) ** 1.1 * fade for g in ages]
            pa, pb = a[win["blade"]], b[win["blade"]]
            ka, kb = (TRAIL_INNER + (TRAIL_TAPER - TRAIL_INNER) * g for g in ages)
            ia, ib = _lerp(pa[0], pa[1], ka), _lerp(pb[0], pb[1], kb)
            ta, tb = pa[1], pb[1]

            def P(p):
                return ((p[0] + shift[0]) * k, (p[1] + shift[1]) * k)

            # inner edge faint, tip edge hot
            fill_quad(buf, (P(ia), P(ta), P(tb), P(ib)), (0.15 * w[0], w[0], w[1], 0.15 * w[1]))
    return buf


def burst_heat(meta, t, shape, shift, s):
    """Every marked burst live at t (supersampled)."""
    buf = np.zeros(shape, np.float32)
    k = SUPER
    rng_base = 7
    for n, b in enumerate(meta.get("bursts", [])):
        u = (t - b["t"]) / BURST_LEN
        if not (0 <= u <= 1):
            continue
        sc = b.get("scale", 1.0) * s * k
        rng = np.random.default_rng(rng_base + n)
        if b["kind"] == "ground":
            tips = [_sample_at(meta, sd, b["t"])[1] for sd in ("L", "R") if _sample_at(meta, sd, b["t"])]
            cx = sum(p[0] for p in tips) / len(tips)
            cy = meta["origin_px"][1]
        else:
            # "both": the two blades strike together; the flash sits between them
            sides = ("L", "R") if b["blade"] == "both" else (b["blade"],)
            pts = [_lerp(bl[0], bl[1], 0.72) for bl in (_sample_at(meta, sd, b["t"]) for sd in sides)]
            cx, cy = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
        cx, cy = (cx + shift[0]) * k, (cy + shift[1]) * k
        flat = 0.30 if b["kind"] == "ground" else 1.0
        ys, xs = np.mgrid[0:shape[0], 0:shape[1]].astype(np.float32)
        rr = np.hypot((xs - cx), (ys - cy) / flat)
        # the flash: a hot disc in the first fifth
        if u < 0.25:
            fl = (1 - u / 0.25) * np.clip(1 - rr / (46 * sc), 0, 1) ** 1.5
            np.maximum(buf, fl, out=buf)
        # the ring: expanding, thinning, fading
        R = (24 + 120 * (1 - (1 - u) ** 2)) * sc
        wdt = (16 * (1 - u) + 3) * sc
        ring = np.clip(1 - np.abs(rr - R) / wdt, 0, 1) * (1 - u) ** 1.3
        np.maximum(buf, ring, out=buf)
        # streaks: fixed directions per burst, shooting out
        count = 10 if b["kind"] == "slash" else 9
        for i in range(count):
            if b["kind"] == "ground":
                ang = math.radians(-90 + rng.uniform(-70, 70))
            else:
                ang = rng.uniform(0, 2 * math.pi)
            length = rng.uniform(70, 150) * sc
            r0 = (10 + 60 * u) * sc
            r1 = r0 + length * (0.4 + 0.6 * min(1.0, u * 2.5))
            c, si = math.cos(ang), math.sin(ang) * (0.8 if b["kind"] == "ground" else 1.0)
            stroke(buf, (cx + c * r0, cy + si * r0), (cx + c * r1, cy + si * r1),
                   rng.uniform(7, 12) * sc * (1 - u * 0.6), (1 - u) ** 1.1)
    return buf


def frame_layer(meta, t, s, pad):
    """One frame's neutral RGBA layer on the padded canvas."""
    w, h = meta["canvas"]
    W, H = w + 2 * pad, h + 2 * pad
    shape = (H * SUPER, W * SUPER)
    heat = np.maximum(trail_heat(meta, t, shape, (pad, pad), s), burst_heat(meta, t, shape, (pad, pad), s))
    heat = downsample(heat, SUPER)
    glow = gauss(heat, GLOW_SIGMA * s)
    alpha = np.clip(heat * 1.0 + glow * 0.9, 0, 1)
    # the core is only the hottest part of the ribbon/burst, so a tint keeps
    # most of the layer coloured; the glow round it reads at about half heat
    core = np.clip((heat - 0.55) / 0.45, 0, 1) ** 1.2
    val = np.clip(0.50 + 0.50 * core, 0, 1)
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = np.round(val * 255)[..., None].astype(np.uint8)
    out[..., 3] = np.round(alpha * 255).astype(np.uint8)
    out[out[..., 3] == 0] = 0
    return Image.fromarray(out, "RGBA")


def clip_fx(meta):
    """(frames, first, pad): the layer for every frame from the first that
    carries anything to the last, the index of that first frame, and the px
    pad added round the clip's canvas (the layer's ground anchor is the
    clip's origin + pad). ([], None, pad) for a clip with no trail or burst."""
    s = float(meta["ppu"]) / REF_PPU
    pad = int(round(PAD * s))
    live = []
    for i, t in enumerate(meta["times"]):
        # a window's first instant has one sample and no sweep yet
        on = any(w["from"] + 1e-6 < t <= w["to"] + TRAIL_FADE for w in meta.get("trails", [])) or \
            any(0 <= (t - b["t"]) / BURST_LEN <= 1 for b in meta.get("bursts", []))
        if on:
            live.append(i)
    if not live:
        return [], None, pad
    first, last = live[0], live[-1]
    frames = [frame_layer(meta, meta["times"][i], s, pad) for i in range(first, last + 1)]
    return frames, first, pad


# ------------------------------------------------------------------ the ground burst
#: Four Winds' Ascension's ground burst ([USER], round 3: "a mirrored ground
#: particle effect on him and the target enemy"), its own sprite clip: radial
#: cracks and a flattened shock ring on the ground and a column of streaks
#: rising from it (his Special E: scratch reference/NOTES.md, Talent Demo 1,
#: Character Details 3). The game places it twice from the impact frame, at
#: the blade's point and, flipped, under the target. Same heat format as the
#: trail layer; every length at REF_PPU.
GROUND_LEN = 0.55        # seconds
GROUND_FLAT = 0.32       # the ground plane's squash under the 5-degree camera
GROUND_UP, GROUND_DOWN, GROUND_HALF = 470, 160, 440   # the cell round the anchor, px at REF_PPU
GROUND_SEED = 11


def _segment(buf, a, b, width, va, vb):
    """A constant-width strip from a to b, heat va at a and vb at b."""
    (ax, ay), (bx, by) = a, b
    n = math.hypot(bx - ax, by - ay)
    if n < 1e-6:
        return
    nx, ny = -(by - ay) / n * width / 2, (bx - ax) / n * width / 2
    fill_quad(buf, ((ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)), (va, vb, vb, va))


def ground_burst_heat(u, shape, c, s):
    """The burst at phase u (0..1) round ground point c (supersampled px)."""
    buf = np.zeros(shape, np.float32)
    k = SUPER * s
    cx, cy = c
    rng = np.random.default_rng(GROUND_SEED)
    ys, xs = np.mgrid[0:shape[0], 0:shape[1]].astype(np.float32)
    rr = np.hypot(xs - cx, (ys - cy) / GROUND_FLAT)
    if u < 0.22:                                  # the flash, where the point went in
        np.maximum(buf, (1 - u / 0.22) * np.clip(1 - rr / (100 * k), 0, 1) ** 1.4, out=buf)
    R = (40 + 350 * (1 - (1 - u) ** 2)) * k       # the shock ring on the ground
    wdt = (26 * (1 - u) + 4) * k
    np.maximum(buf, np.clip(1 - np.abs(rr - R) / wdt, 0, 1) * (1 - u) ** 1.3, out=buf)
    grow = min(1.0, u / 0.22)                     # the cracks: jagged, radial, on the ground
    heat = 1.0 if u < 0.3 else max(0.0, 1 - (u - 0.3) / 0.7) ** 0.8
    for i in range(9):
        ang = 2 * math.pi * (i + rng.uniform(-0.3, 0.3)) / 9
        length = rng.uniform(210, 380) * k * grow
        pts, r = [(cx, cy)], 0.0
        while r < length:
            r = min(length, r + 34 * k)
            j = rng.uniform(-12, 12) * k
            px, py = math.cos(ang) * r - math.sin(ang) * j, math.sin(ang) * r + math.cos(ang) * j
            pts.append((cx + px, cy + py * GROUND_FLAT))
        for n, (a, b) in enumerate(zip(pts, pts[1:])):
            f0, f1 = n / max(1, len(pts) - 1), (n + 1) / max(1, len(pts) - 1)
            _segment(buf, a, b, (14 - 9 * f0) * k, heat * (1 - 0.5 * f0), heat * (1 - 0.5 * f1))
    for i in range(11):                           # the column: streaks rising from the point
        x = cx + rng.uniform(-100, 100) * k
        length = rng.uniform(200, 360) * k
        r0 = (6 + 90 * u) * k * rng.uniform(0.5, 1.0)
        r1 = r0 + length * (0.3 + 0.7 * min(1.0, u * 3))
        stroke(buf, (x, cy - r0), (x + rng.uniform(-12, 12) * k, cy - r1),
               rng.uniform(11, 20) * k * (1 - 0.6 * u), (1 - u) ** 1.1)
    return buf


def ground_burst(ppu: float = REF_PPU, fps: int = 20):
    """(frames, origin): the ground burst's neutral RGBA frames, every one on
    the same cell, and the ground point's px in that cell (the anchor the game
    puts on the blade's point or the target's feet). Deterministic."""
    s = float(ppu) / REF_PPU
    W, H = int(round(2 * GROUND_HALF * s)), int(round((GROUND_UP + GROUND_DOWN) * s))
    origin = (W / 2, GROUND_UP * s)
    shape = (H * SUPER, W * SUPER)
    frames = []
    for i in range(int(math.ceil(GROUND_LEN * fps))):
        u = i / fps / GROUND_LEN
        heat = downsample(ground_burst_heat(u, shape, (origin[0] * SUPER, origin[1] * SUPER), s), SUPER)
        glow = gauss(heat, GLOW_SIGMA * s)
        alpha = np.clip(heat + glow * 0.9, 0, 1)
        core = np.clip((heat - 0.55) / 0.45, 0, 1) ** 1.2
        val = np.clip(0.50 + 0.50 * core, 0, 1)
        out = np.zeros((H, W, 4), np.uint8)
        out[..., :3] = np.round(val * 255)[..., None].astype(np.uint8)
        out[..., 3] = np.round(alpha * 255).astype(np.uint8)
        out[out[..., 3] == 0] = 0
        frames.append(Image.fromarray(out, "RGBA"))
    return frames, origin


def tint(im: Image.Image, color) -> Image.Image:
    """The review sheets' element look: colour = mix(element, white,
    smoothstep(0.72, 1, heat)), alpha unchanged."""
    a = np.asarray(im.convert("RGBA")).astype(np.float32) / 255
    heat = a[..., 0]
    k = np.clip((heat - 0.72) / 0.28, 0, 1)
    k = k * k * (3 - 2 * k)
    rgb = np.array(color, np.float32)[None, None, :] * (1 - k[..., None]) + k[..., None]
    out = np.dstack([rgb, a[..., 3:4]])
    return Image.fromarray(np.round(np.clip(out, 0, 1) * 255).astype(np.uint8), "RGBA")
