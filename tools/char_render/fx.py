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
ground ("ground"), or a long thin streak along the blade from the hand out
past the point ("thrust": Furina's phantom rapier). A trail window may set
its own `inner` and `taper`. Every pixel length is at REF_PPU and scales with the clip's
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
            inner, taper = win.get("inner", TRAIL_INNER), win.get("taper", TRAIL_TAPER)
            ka, kb = (inner + (taper - inner) * g for g in ages)
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
        if b["kind"] == "thrust":
            # a rapier's thrust: a long thin streak along the blade, from the
            # hand out past the point, flashing at the point and fading
            (bx, by), (tx, ty) = _sample_at(meta, b["blade"], b["t"])
            dx, dy = tx - bx, ty - by
            reach = 1.0 + 0.35 * min(1.0, u * 3)
            a = ((bx + shift[0]) * k, (by + shift[1]) * k)
            e = ((bx + dx * reach + shift[0]) * k, (by + dy * reach + shift[1]) * k)
            mid = (a[0] + (e[0] - a[0]) * 0.7, a[1] + (e[1] - a[1]) * 0.7)
            fade = (1 - u) ** 1.2
            w = 14 * sc * (1 - 0.5 * u)
            stroke(buf, mid, a, w, fade)
            stroke(buf, mid, e, w, fade)
            if u < 0.35:
                ys, xs = np.mgrid[0:shape[0], 0:shape[1]].astype(np.float32)
                tip = ((tx + shift[0]) * k, (ty + shift[1]) * k)
                fl = (1 - u / 0.35) * np.clip(1 - np.hypot(xs - tip[0], ys - tip[1]) / (40 * sc), 0, 1) ** 1.5
                np.maximum(buf, fl, out=buf)
            continue
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


# ------------------------------------------------------------------ Furina's stage effects
#: Spend, Drain and Repay, the three moves of Furina's stage
#: (review/active/furina-visual-paper-2026-10-13.md), as effect sprite clips of
#: their own in the same heat format, every length at REF_PPU. Today none has
#: a look of its own (the Fanfare number drops; the base damage and heal
#: numbers play); phase B places them. Each returns (frames, origin, to):
#: every frame on one cell, `origin` the anchor on Furina (her chest), `to`
#: the other end in the same cell px (the stage: the first guest seat), or None.
STAGE_FPS = 20
STAGE_DX = 400           # px at REF_PPU from her chest to the first guest seat (about 200 screen px)
STAGE_SEED = 23
#: the tint each is meant to take: Spend the gold of the Fanfare, Drain and
#: Repay Hydro (ReactionFx's Hydro)
STAGE_TINTS = {"spend": "#ffd36b", "drain": ELEMENTS["hydro"], "repay": ELEMENTS["hydro"]}


def _finish(heat, s):
    """Supersampled heat -> one neutral RGBA frame (ground_burst's look)."""
    heat = downsample(heat, SUPER)
    glow = gauss(heat, GLOW_SIGMA * s)
    alpha = np.clip(heat + glow * 0.9, 0, 1)
    core = np.clip((heat - 0.55) / 0.45, 0, 1) ** 1.2
    val = np.clip(0.50 + 0.50 * core, 0, 1)
    out = np.zeros(heat.shape + (4,), np.uint8)
    out[..., :3] = np.round(val * 255)[..., None].astype(np.uint8)
    out[..., 3] = np.round(alpha * 255).astype(np.uint8)
    out[out[..., 3] == 0] = 0
    return Image.fromarray(out, "RGBA")


def _disc(buf, c, r, val, power=1.4):
    if r <= 0 or val <= 0:
        return
    H, W = buf.shape
    x0, x1 = max(0, int(c[0] - r - 1)), min(W, int(c[0] + r + 2))
    y0, y1 = max(0, int(c[1] - r - 1)), min(H, int(c[1] + r + 2))
    if x0 >= x1 or y0 >= y1:
        return
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32) + 0.5
    v = val * np.clip(1 - np.hypot(xs - c[0], ys - c[1]) / r, 0, 1) ** power
    sub = buf[y0:y1, x0:x1]
    np.maximum(sub, v, out=sub)


def _ring(buf, c, R, width, val, flat=1.0):
    if val <= 0 or R <= 0:
        return
    H, W = buf.shape
    x0, x1 = max(0, int(c[0] - R - width - 1)), min(W, int(c[0] + R + width + 2))
    y0, y1 = max(0, int(c[1] - (R + width) * flat - 1)), min(H, int(c[1] + (R + width) * flat + 2))
    if x0 >= x1 or y0 >= y1:
        return
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32) + 0.5
    v = val * np.clip(1 - np.abs(np.hypot(xs - c[0], (ys - c[1]) / flat) - R) / width, 0, 1)
    sub = buf[y0:y1, x0:x1]
    np.maximum(sub, v, out=sub)


def _star(buf, c, r, val):
    """A four-point sparkle: two thin crossed tapered lines and a hot dot."""
    if r <= 0:
        return
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        stroke(buf, (c[0] + math.cos(a) * r * 0.08, c[1] + math.sin(a) * r * 0.08),
               (c[0] + math.cos(a) * r, c[1] + math.sin(a) * r), r * 0.22, val)
    _disc(buf, c, r * 0.25, val, 1.0)


def _drop(buf, c, vel, r, val):
    """A water droplet moving along vel: a round head and a tapered tail behind it."""
    _disc(buf, c, r, val, 0.8)
    n = math.hypot(*vel)
    if n > 1e-6:
        back = (c[0] - vel[0] / n * r * 3.2, c[1] - vel[1] / n * r * 3.2)
        stroke(buf, c, back, r * 1.6, val * 0.85)


def spend_burst(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Spend: a golden burst of confetti and stage sparkle thrown up from
    Furina -- a flash, a ring, forty spinning confetti slips flung out and
    falling, and sparkles winking round her. 0.8 s."""
    s = float(ppu) / REF_PPU
    k = SUPER * s
    W, H = int(round(640 * s)), int(round(620 * s))
    origin = (W / 2, 380 * s)
    rng = np.random.default_rng(STAGE_SEED)
    pieces = [(rng.uniform(-math.pi * 0.95, -math.pi * 0.05), rng.uniform(260, 620), rng.uniform(0, 2 * math.pi),
               rng.uniform(8, 22), rng.uniform(9, 15), rng.uniform(4, 7), rng.uniform(0.8, 1.0)) for _ in range(40)]
    stars = [(rng.uniform(-230, 230), rng.uniform(-300, 60), rng.uniform(0.05, 0.55), rng.uniform(18, 34))
             for _ in range(12)]
    frames = []
    for i in range(int(math.ceil(0.8 * fps))):
        t = i / fps
        u = t / 0.8
        buf = np.zeros((H * SUPER, W * SUPER), np.float32)
        cx, cy = origin[0] * SUPER, origin[1] * SUPER
        if u < 0.2:
            _disc(buf, (cx, cy), 90 * k, 1 - u / 0.2)
        if u < 0.62:
            _ring(buf, (cx, cy), (30 + 200 * (1 - (1 - min(1, u * 1.6)) ** 2)) * k, (10 * (1 - u) + 3) * k,
                  (1 - u / 0.62) ** 1.3 * 0.8)
        fade = 1.0 if u < 0.7 else max(0.0, 1 - (u - 0.7) / 0.3)
        for ang, speed, spin0, spin_v, lw, lh, val in pieces:
            # thrown out and up, then gravity
            x = cx + math.cos(ang) * speed * t * k
            y = cy + (math.sin(ang) * speed * t + 0.5 * 900 * t * t) * k
            a = spin0 + spin_v * t
            ca, sa = math.cos(a), math.sin(a)
            flick = 0.55 + 0.45 * abs(math.cos(a * 1.7))        # a slip catching the light as it turns
            hw, hh = lw * k / 2, lh * k / 2 * (0.4 + 0.6 * abs(ca))
            quad = [(x + dx * ca - dy * sa, y + dx * sa + dy * ca) for dx, dy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]
            v = val * flick * fade
            fill_quad(buf, quad, (v, v, v, v))
        for dx, dy, t0, r in stars:
            w = (t - t0) / 0.22
            if 0 <= w <= 1:
                _star(buf, (cx + dx * k, cy + dy * k), r * k * math.sin(math.pi * w), math.sin(math.pi * w))
        frames.append(_finish(buf, s))
    return frames, origin, None


def _stream(ppu, fps, length, reverse, glow_end):
    s = float(ppu) / REF_PPU
    k = SUPER * s
    W, H = int(round((STAGE_DX + 200) * s)), int(round(300 * s))
    origin = (100 * s, 200 * s)                   # her chest
    to = (origin[0] + STAGE_DX * s, origin[1])    # the first guest seat
    rng = np.random.default_rng(STAGE_SEED + (1 if reverse else 0))
    drops = [(rng.uniform(0.0, 0.45), rng.uniform(-50, 50), rng.uniform(0.32, 0.45), rng.uniform(10, 16),
              rng.uniform(-24, 24)) for _ in range(16)]
    ax, ay = to if reverse else origin
    bx, by = origin if reverse else to
    frames = []
    for i in range(int(math.ceil(length * fps))):
        t = i / fps
        buf = np.zeros((H * SUPER, W * SUPER), np.float32)
        for t0, lift, dur, r, wob in drops:
            w = (t - t0) / dur
            if not 0 <= w <= 1:
                continue
            # a drop leaves slowly and is pulled faster (Drain), or arrives
            # fast and slows into her (Repay)
            e = w * w if not reverse else 1 - (1 - w) ** 2
            de = 2 * w if not reverse else 2 * (1 - w)
            x = ax + (bx - ax) * e
            y = ay + (by - ay) * e - math.sin(math.pi * e) * lift * s + wob * s * math.sin(6 * w)
            vel = ((bx - ax) * de + 1e-3, -math.cos(math.pi * e) * math.pi * lift * s * de)
            size = r * (1 - 0.35 * w) if not reverse else r * (0.65 + 0.35 * (1 - w))
            fade = min(1.0, w / 0.12) * (min(1.0, (1 - w) / 0.12) if not reverse else 1.0)
            _drop(buf, (x * SUPER, y * SUPER), vel, size * k, 0.95 * fade)
        if glow_end:
            # Repay's soft heal glow: a bloom on her as the drops arrive, a
            # widening soft ring and a few motes rising
            g = (t - 0.38) / 0.5
            if 0 <= g <= 1:
                cx, cy = origin[0] * SUPER, origin[1] * SUPER
                _disc(buf, (cx, cy), (60 + 50 * g) * k, 0.75 * math.sin(math.pi * min(1, g * 1.4)) ** 0.8, 2.2)
                _ring(buf, (cx, cy), (40 + 90 * g) * k, 14 * k, 0.6 * (1 - g) ** 1.2, flat=0.6)
                for j in range(6):
                    _disc(buf, (cx + (j - 2.5) * 22 * k, cy - (20 + 120 * g + 14 * (j % 3)) * k), 7 * k,
                          0.8 * (1 - g), 1.0)
        frames.append(_finish(buf, s))
    return frames, origin, to


def drain_stream(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Drain: Hydro droplets drawn out of Furina and pulled along a shallow
    arc to the stage (the first guest seat), speeding as they go. 0.9 s."""
    return _stream(ppu, fps, 0.9, reverse=False, glow_end=False)


def repay_return(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Repay: the droplets come back from the stage and slow into her, then a
    soft heal glow blooms on her. 1.0 s."""
    return _stream(ppu, fps, 1.0, reverse=True, glow_end=True)


STAGE_EFFECTS = {"spend": spend_burst, "drain": drain_stream, "repay": repay_return}
