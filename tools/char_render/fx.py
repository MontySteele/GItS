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
        u = (t - b["t"]) / b.get("len", BURST_LEN)
        if not (0 <= u <= 1):
            continue
        sc = b.get("scale", 1.0) * s * k
        rng = np.random.default_rng(rng_base + n)
        if b["kind"] == "tide":
            c = ((meta["origin_px"][0] + shift[0]) * k, (meta["origin_px"][1] + shift[1]) * k)
            np.maximum(buf, tide_heat(u, shape, c, sc, rng), out=buf)
            continue
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


#: Nereid's Ascension's "tide" (Kokomi, art polish 2026-10-21): a ring of water
#: rising round her feet and soft jellyfish lights drifting up out of it. Every
#: length in px at REF_PPU; the ring's back half shows only at her sides, so
#: the layer (drawn over her body) never veils her. A burst may set its own
#: `len` (seconds) where the slash bursts take BURST_LEN.
TIDE_R = 215             # the ring's settled radius
TIDE_FLAT = 0.26         # the ground plane's squash under the camera
TIDE_STREAKS = 16        # the water rising off the ring
TIDE_LIGHTS = 8          # the jellyfish lights


def _bell(buf, c, r, val, sway):
    """A jellyfish light: a dome, hot at its crown, and three short trailing
    tentacles that sway (supersampled px)."""
    cx, cy = c
    H, W = buf.shape
    x0, x1 = max(0, int(cx - r * 1.2)), min(W, int(cx + r * 1.2) + 1)
    y0, y1 = max(0, int(cy - r * 1.1)), min(H, int(cy + r * 0.4) + 1)
    if x0 < x1 and y0 < y1:
        ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        dx, dy = (xs - cx) / r, (ys - cy) / r
        dome = np.where(dy <= 0.15, np.clip(1 - np.hypot(dx, dy / 0.85), 0, 1) ** 0.6, 0)
        crown = np.clip(1 - np.hypot(dx, (dy + 0.35) / 0.6) / 0.55, 0, 1)
        sub = buf[y0:y1, x0:x1]
        np.maximum(sub, val * np.clip(0.62 * dome + 0.5 * crown, 0, 1), out=sub)
    for j in (-0.5, 0.0, 0.5):
        a = (cx + j * r, cy + 0.1 * r)
        e = (cx + j * r * 0.8 + sway * r, cy + r * (1.5 - 0.3 * abs(j)))
        stroke(buf, a, e, r * 0.28, val * 0.55)


def tide_heat(u, shape, c, sc, rng):
    """The tide at phase u (0..1) round the feet point c (supersampled px):
    the ring opens fast and holds, water lifts off it, the lights rise; all of
    it fades over the last third."""
    buf = np.zeros(shape, np.float32)
    cx, cy = c
    fade = 1.0 if u < 0.68 else max(0.0, 1 - (u - 0.68) / 0.32) ** 1.2
    grow = 1 - (1 - min(1.0, u / 0.3)) ** 3
    R = (60 + (TIDE_R - 60) * grow) * sc
    ys, xs = np.mgrid[0:shape[0], 0:shape[1]].astype(np.float32)
    ex, ey = (xs - cx) / R, (ys - cy) / (R * TIDE_FLAT)
    rr = np.hypot(ex, ey)
    # the back half of the ring hides behind her: it shows only past her sides
    side = np.clip((np.abs(ex) - 0.45) / 0.3, 0, 1)
    vis = np.where(ey >= 0, 1.0, side)
    wdt = (9 + 10 * (1 - grow)) * sc / R
    ring = np.clip(1 - np.abs(rr - 1) / wdt, 0, 1) * vis * fade
    np.maximum(buf, 0.92 * ring, out=buf)
    # a pale sheen of water inside the front of the ring
    sheen = np.where((rr < 1) & (ey > 0), 0.22 * np.clip(ey, 0, 1), 0) * fade
    np.maximum(buf, sheen, out=buf)
    # the water lifting off the ring: wavering streaks, front and sides only
    lift = min(1.0, max(0.0, (u - 0.08) / 0.4))
    for i in range(TIDE_STREAKS):
        a = 2 * math.pi * (i + rng.uniform(-0.3, 0.3)) / TIDE_STREAKS
        ca, sa = math.cos(a), math.sin(a)
        if sa < 0 and abs(ca) < 0.75:
            continue
        x, y = cx + ca * R, cy + sa * R * TIDE_FLAT
        h = rng.uniform(90, 230) * sc * lift * (0.6 if sa > 0 else 1.0)
        wob = rng.uniform(-14, 14) * sc
        if h > 1:
            stroke(buf, (x, y), (x + wob, y - h), rng.uniform(9, 15) * sc, 0.62 * fade)
    # the jellyfish lights: out of the ring at her sides, up past her hands
    for i in range(TIDE_LIGHTS):
        side_ = -1 if i % 2 else 1
        born = 0.06 + 0.05 * i + rng.uniform(0, 0.04)
        dx = side_ * rng.uniform(150, 235)
        top = rng.uniform(330, 560)
        r = rng.uniform(13, 19)
        bob = rng.uniform(0, 2 * math.pi)
        v = (u - born) / (1 - born)
        if v <= 0:
            continue
        up = 1 - (1 - min(1.0, v)) ** 1.6
        x = cx + (dx - side_ * 40 * up + 10 * math.sin(bob + 7 * v)) * sc
        y = cy - (10 + top * up) * sc
        glow = min(1.0, v / 0.2) * fade
        _bell(buf, (x, y), r * sc, 0.95 * glow, 0.25 * math.sin(bob + 9 * v))
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
            any(0 <= (t - b["t"]) / b.get("len", BURST_LEN) <= 1 for b in meta.get("bursts", []))
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


#: Spend's canvas (w, h, origin x, origin y) at REF_PPU: wide enough that
#: the confetti thrown out sideways fades before the edge (at 640 it was cut,
#: edge alpha 151, a pale box in game; every effect's canvas is held to edge
#: alpha <= 3 by tier0/tests/test_char_render.py)
SPEND_CELL = (900, 620, 480, 380)


def spend_burst(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Spend: a golden burst of confetti and stage sparkle thrown up from
    Furina -- a flash, a ring, forty spinning confetti slips flung out and
    falling, and sparkles winking round her. 0.8 s."""
    s = float(ppu) / REF_PPU
    k = SUPER * s
    cw, ch, ox, oy = SPEND_CELL
    W, H = int(round(cw * s)), int(round(ch * s))
    origin = (ox * s, oy * s)
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


#: px at REF_PPU of canvas behind her chest (left of it): Drain's drops need
#: 100; Repay's heal bloom and ring reach about 170 out from her chest, glow
#: included, so at 100 its frames 12 to 17 were cut flat at the canvas edge
#: and the game drew a pale box round the glow (border alpha up to 55)
STREAM_BACK = {"drain": 100, "repay": 200}


def _stream(ppu, fps, length, reverse, glow_end, back=100):
    s = float(ppu) / REF_PPU
    k = SUPER * s
    W, H = int(round((STAGE_DX + 100 + back) * s)), int(round(300 * s))
    origin = (back * s, 200 * s)                  # her chest
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
    return _stream(ppu, fps, 0.9, reverse=False, glow_end=False, back=STREAM_BACK["drain"])


def repay_return(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Repay: the droplets come back from the stage and slow into her, then a
    soft heal glow blooms on her. 1.0 s."""
    return _stream(ppu, fps, 1.0, reverse=True, glow_end=True, back=STREAM_BACK["repay"])


STAGE_EFFECTS = {"spend": spend_burst, "drain": drain_stream, "repay": repay_return}


# ------------------------------------------------------------------ Furina's guest effects
#: One short effect per guest star, Furina's plan item "guest-star pizazz"
#: ([USER]: "unique particle effects or similar for each guest";
#: review/active/furina-guest-fx-2026-10-16.md). Same heat format as the
#: stage effects, every length at REF_PPU, each 0.5 to 0.7 s at STAGE_FPS.
#: Each returns (frames, origin): every frame on one cell, `origin` the
#: anchor -- the GUEST_ANCHOR point of the creature it plays on ("feet" the
#: bottom of its hitbox, "center" its effect spawn point).
GUEST_SEED = 41
#: Overloaded's pink: ReactionFx.For(Reaction.Overload)'s flash
#: (klee-mod/KleeCode/Vfx/ReactionFx.cs); Geo gold: ElementFlashHex(Geo).
OVERLOAD_HEX = "#ff6fd0"
GEO_HEX = "#ffd36b"
GUEST_TINTS = {
    "charlotte": ELEMENTS["cryo"], "chevreuse": OVERLOAD_HEX, "clorinde": ELEMENTS["electro"],
    "escoffier": ELEMENTS["cryo"], "freminet": ELEMENTS["cryo"], "lynette": ELEMENTS["anemo"],
    "lyney": ELEMENTS["pyro"], "navia": GEO_HEX, "neuvillette": ELEMENTS["hydro"],
    "sigewinne": ELEMENTS["hydro"], "wriothesley": ELEMENTS["cryo"],
}
GUEST_ANCHOR = {
    "charlotte": "center", "chevreuse": "center", "clorinde": "center", "escoffier": "feet",
    "freminet": "center", "lynette": "center", "lyney": "center", "navia": "center",
    "neuvillette": "center", "sigewinne": "center", "wriothesley": "feet",
}
#: seconds each runs
GUEST_LEN = {
    "charlotte": 0.5, "chevreuse": 0.5, "clorinde": 0.55, "escoffier": 0.7, "freminet": 0.6,
    "lynette": 0.65, "lyney": 0.7, "navia": 0.6, "neuvillette": 0.5, "sigewinne": 0.7,
    "wriothesley": 0.6,
}


def _poly(buf, pts, val):
    """A convex polygon at one heat, as a triangle fan."""
    for a, b in zip(pts[1:], pts[2:]):
        fill_triangle(buf, (pts[0], a, b), (val, val, val))


def _line(buf, a, b, width, val):
    _segment(buf, a, b, width, val, val)
    _disc(buf, a, width / 2, val, 0.2)
    _disc(buf, b, width / 2, val, 0.2)


def _shard(buf, c, ang, length, width, val):
    """An angular ice or crystal shard: a long kite, point first along ang."""
    ca, sa = math.cos(ang), math.sin(ang)
    tip = (c[0] + ca * length * 0.62, c[1] + sa * length * 0.62)
    back = (c[0] - ca * length * 0.38, c[1] - sa * length * 0.38)
    left = (c[0] - sa * width / 2, c[1] + ca * width / 2)
    right = (c[0] + sa * width / 2, c[1] - ca * width / 2)
    fill_triangle(buf, (tip, left, right), (val, val * 0.8, val * 0.8))
    fill_triangle(buf, (back, left, right), (val * 0.6, val * 0.8, val * 0.8))


def _lens(buf, a, b, width, val, n=18):
    """A slash: a thin lens from a to b, widest at the middle."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    m = math.hypot(dx, dy)
    if m < 1e-6 or val <= 0:
        return
    nx, ny = -dy / m, dx / m
    pts = [_lerp(a, b, i / n) for i in range(n + 1)]
    for i in range(n):
        w0 = width / 2 * math.sin(math.pi * i / n) ** 0.7
        w1 = width / 2 * math.sin(math.pi * (i + 1) / n) ** 0.7
        p, q = pts[i], pts[i + 1]
        fill_quad(buf, ((p[0] + nx * w0, p[1] + ny * w0), (q[0] + nx * w1, q[1] + ny * w1),
                        (q[0] - nx * w1, q[1] - ny * w1), (p[0] - nx * w0, p[1] - ny * w0)), (val, val, val, val))


def _heart(buf, c, r, val):
    _disc(buf, (c[0] - 0.5 * r, c[1] - 0.2 * r), 0.58 * r, val, 0.4)
    _disc(buf, (c[0] + 0.5 * r, c[1] - 0.2 * r), 0.58 * r, val, 0.4)
    fill_triangle(buf, ((c[0] - 1.02 * r, c[1] - 0.02 * r), (c[0] + 1.02 * r, c[1] - 0.02 * r),
                        (c[0], c[1] + 1.1 * r)), (val, val, val))


def _fade(u, start):
    """1 until `start`, then down to 0 at the end."""
    return 1.0 if u < start else max(0.0, 1 - (u - start) / (1 - start))


def _guest_frames(name, ppu, fps, cell, draw):
    """Run draw(buf, t, u, c, k, i) over the effect's frames: `cell` is
    (w, h, origin x, origin y) at REF_PPU, `c` the origin in supersampled px,
    `k` px per REF_PPU px in the buffer, `u` the phase 0..1."""
    s = float(ppu) / REF_PPU
    w, h, ox, oy = cell
    W, H = int(round(w * s)), int(round(h * s))
    origin = (ox * s, oy * s)
    k = SUPER * s
    c = (origin[0] * SUPER, origin[1] * SUPER)
    length = GUEST_LEN[name]
    out = []
    for i in range(int(math.ceil(length * fps - 1e-9))):
        t = i / fps
        buf = np.zeros((H * SUPER, W * SUPER), np.float32)
        draw(buf, t, t / length, c, k, i)
        out.append(_finish(buf, s))
    return out, origin


def wriothesley_shock(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Wriothesley: an upward shock from the target's feet, six angular ice
    shards flung up and out. 0.6 s."""
    rng = np.random.default_rng(GUEST_SEED)
    shards = [(math.radians(-150 + i * 24 + rng.uniform(-7, 7)), rng.uniform(520, 760), rng.uniform(-6, 6),
               rng.uniform(52, 76), rng.uniform(16, 22)) for i in range(6)]
    column = [(rng.uniform(-60, 60), rng.uniform(150, 260), rng.uniform(9, 15)) for _ in range(5)]

    def draw(buf, t, u, c, k, i):
        cx, cy = c
        if u < 0.22:
            _disc(buf, (cx, cy - 30 * k), 85 * k, 1 - u / 0.22)
        _ring(buf, (cx, cy), (30 + 220 * (1 - (1 - u) ** 2)) * k, (14 * (1 - u) + 3) * k, 0.9 * (1 - u) ** 1.3,
              flat=GROUND_FLAT)
        if u < 0.65:
            g = u / 0.65
            for dx, length, w in column:
                r0 = 80 * g * k
                r1 = r0 + length * min(1.0, g * 3) * k
                stroke(buf, (cx + dx * k, cy - r0), (cx + dx * 1.2 * k, cy - r1), w * k * (1 - 0.6 * g),
                       (1 - g) ** 1.1)
        fade = _fade(u, 0.55)
        for ang, speed, spin, length, width in shards:
            x = cx + math.cos(ang) * speed * t * k
            y = cy - 40 * k + (math.sin(ang) * speed * t + 0.5 * 1500 * t * t) * k
            _shard(buf, (x, y), ang + spin * t, length * k, width * k, 0.95 * fade)
    return _guest_frames("wriothesley", ppu, fps, (700, 640, 340, 500), draw)


def lynette_swirl(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Lynette: a swirl ring tightening onto the target, three star
    sparkles. 0.65 s."""
    stars = [(math.radians(a), r, t0, size) for a, r, t0, size in
             ((-40, 120, 0.12, 30), (160, 105, 0.24, 26), (70, 125, 0.36, 32))]

    def draw(buf, t, u, c, k, i):
        cx, cy = c
        g = min(1.0, u / 0.75)
        R = 175 - 145 * (1 - (1 - g) ** 1.6)
        fade = _fade(u, 0.7)
        for arm in range(3):
            head = arm * 2 * math.pi / 3 + 10.0 * t
            n = 14
            for j in range(n):
                f0, f1 = j / n, (j + 1) / n           # tail (0) to head (1)
                a0, a1 = head - 1.9 * (1 - f0), head - 1.9 * (1 - f1)
                r0, r1 = R * (1 + 0.35 * (1 - f0)), R * (1 + 0.35 * (1 - f1))
                p = (cx + math.cos(a0) * r0 * k, cy + math.sin(a0) * r0 * k)
                q = (cx + math.cos(a1) * r1 * k, cy + math.sin(a1) * r1 * k)
                _segment(buf, p, q, (3 + 11 * f1) * k, (0.2 + 0.8 * f0) * fade, (0.2 + 0.8 * f1) * fade)
        if u > 0.62:
            w = (u - 0.62) / 0.38
            _disc(buf, (cx, cy), (40 + 40 * w) * k, math.sin(math.pi * min(1.0, w * 1.3)) * 0.95)
        for ang, r, t0, size in stars:
            w = (u - t0) / 0.4
            if 0 <= w <= 1:
                rr = r * (1 - 0.3 * w)
                _star(buf, (cx + math.cos(ang) * rr * k, cy + math.sin(ang) * rr * k),
                      size * k * math.sin(math.pi * w), math.sin(math.pi * w))
    return _guest_frames("lynette", ppu, fps, (500, 500, 240, 260), draw)


def clorinde_cross(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Clorinde: two crossing slashes, an X, and a flash where they cross.
    0.55 s."""
    rng = np.random.default_rng(GUEST_SEED + 2)
    sparks = [(rng.uniform(0, 2 * math.pi), rng.uniform(70, 120)) for _ in range(7)]

    def draw(buf, t, u, c, k, i):
        cx, cy = c
        for (ax, ay), (bx, by), t0 in (((-165, -150), (165, 150), 0.0), ((165, -150), (-165, 150), 0.14)):
            if u < t0:
                continue
            p = min(1.0, 0.3 + (u - t0) / 0.2)    # a cut is already under way on its first frame
            v = _fade(u, 0.42)
            a = (cx + ax * k, cy + ay * k)
            e = (cx + (ax + (bx - ax) * p) * k, cy + (ay + (by - ay) * p) * k)
            _lens(buf, a, e, 26 * k, 0.6 * v)
            _lens(buf, a, e, 9 * k, 1.0 * v)
        g = (u - 0.3) / 0.45
        if 0 <= g <= 1:
            _disc(buf, (cx, cy), (45 + 55 * g) * k, math.sin(math.pi * min(1.0, g * 1.6)) ** 0.8)
            for ang, length in sparks:
                r0 = (30 + 60 * g) * k
                r1 = r0 + length * (1 - g) * k
                stroke(buf, (cx + math.cos(ang) * r0, cy + math.sin(ang) * r0),
                       (cx + math.cos(ang) * r1, cy + math.sin(ang) * r1), 7 * k, 1 - g)
    return _guest_frames("clorinde", ppu, fps, (480, 460, 240, 230), draw)


def lyney_cards(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Lyney: small playing cards flipping out from the centre, each
    trailing a flame tip. 0.7 s."""
    rng = np.random.default_rng(GUEST_SEED + 3)
    cards = [(math.radians(-90 + i * 60 + rng.uniform(-12, 12)), rng.uniform(380, 470), rng.uniform(0, math.pi),
              rng.uniform(-3, 3)) for i in range(6)]

    def draw(buf, t, u, c, k, i):
        cx, cy = c
        if u < 0.16:
            _disc(buf, (cx, cy), 55 * k, 1 - u / 0.16)
        fade = _fade(u, 0.7)
        for n, (ang, speed, flip0, spin) in enumerate(cards):
            r = speed * t * (1 - 0.5 * min(1.0, t / 0.7))
            ca, sa = math.cos(ang), math.sin(ang)
            x, y = cx + ca * r * k, cy + sa * r * k
            # the flame tip, trailing back toward the centre, flickering
            flick = 0.8 + 0.2 * math.sin(40 * t + n * 1.7)
            tail = (x - ca * (34 + 26 * flick) * k, y - sa * (34 + 26 * flick) * k)
            stroke(buf, (x - ca * 10 * k, y - sa * 10 * k), tail, 22 * k * flick, 0.9 * fade)
            _disc(buf, (x - ca * 8 * k, y - sa * 8 * k), 12 * k, 0.95 * fade, 0.8)
            # the card, flipping: its width follows |cos| of the flip
            rot = ang + math.pi / 2 + spin * t
            hw = 17 * k * max(0.14, abs(math.cos(flip0 + 13 * t)))
            hh = 24 * k
            cr, sr = math.cos(rot), math.sin(rot)
            pts = [(x + dx * cr - dy * sr, y + dx * sr + dy * cr) for dx, dy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]
            fill_quad(buf, pts, (0.45 * fade,) * 4)
            for a, b in zip(pts, pts[1:] + pts[:1]):
                _segment(buf, a, b, 4.5 * k, 1.0 * fade, 1.0 * fade)
    return _guest_frames("lyney", ppu, fps, (600, 560, 300, 280), draw)


def escoffier_frost(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Escoffier: a low ring of frosty steam that widens and settles at the
    target's feet, with snow sparkles falling. 0.7 s."""
    rng = np.random.default_rng(GUEST_SEED + 4)
    puffs = [(2 * math.pi * j / 22 + rng.uniform(-0.1, 0.1), rng.uniform(0.8, 1.2), rng.uniform(10, 34))
             for j in range(22)]
    flakes = [(rng.uniform(-220, 220), rng.uniform(-300, -150), rng.uniform(0.0, 0.25), rng.uniform(140, 220),
               rng.uniform(11, 17), rng.uniform(0, 2 * math.pi)) for _ in range(9)]

    def draw(buf, t, u, c, k, i):
        cx, cy = c
        if u < 0.2:
            _disc(buf, (cx, cy - 10 * k), 60 * k, 0.8 * (1 - u / 0.2))
        R = 40 + 230 * (1 - (1 - u) ** 3)
        v = (1 - u) ** 0.8
        _ring(buf, (cx, cy), R * k, (8 * (1 - u) + 3) * k, 0.85 * (1 - u) ** 1.5, flat=GROUND_FLAT)
        for ang, size, lift in puffs:
            x = cx + math.cos(ang) * R * k
            y = cy + math.sin(ang) * R * GROUND_FLAT * k - lift * min(1.0, u * 2) * k
            _disc(buf, (x, y), (22 + 26 * u) * size * k, 0.55 * v, 2.0)
        for x0, y0, t0, fall, size, ph in flakes:
            w = (t - t0) / (GUEST_LEN["escoffier"] - t0)
            if 0 <= w <= 1:
                x = cx + (x0 + 14 * math.sin(6 * t + ph)) * k
                y = cy + (y0 + fall * (t - t0)) * k
                _star(buf, (x, y), size * k, math.sin(math.pi * min(1.0, w * 1.2)) ** 0.7)
    return _guest_frames("escoffier", ppu, fps, (640, 460, 320, 340), draw)


def charlotte_flash(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Charlotte: a camera flash on Furina -- a white rectangular frame with
    corner brackets snaps in and fades. 0.5 s."""
    def draw(buf, t, u, c, k, i):
        cx, cy = c
        if u < 0.28:
            _disc(buf, (cx, cy), 150 * k, (1 - u / 0.28) ** 1.4, 1.2)
        sc = 1.25 - 0.25 * min(1.0, t / 0.08)
        v = _fade(u, 0.4) ** 1.2
        hw, hh = 130 * sc * k, 95 * sc * k
        corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        for (ax, ay), (bx, by) in zip(corners, corners[1:] + corners[:1]):
            _segment(buf, (cx + ax, cy + ay), (cx + bx, cy + by), 3 * k, 0.7 * v, 0.7 * v)
        arm = 48 * sc * k
        o = 14 * sc * k
        for ax, ay in corners:
            sx, sy = (1 if ax < 0 else -1), (1 if ay < 0 else -1)
            p = (cx + ax - sx * o, cy + ay - sy * o)
            _line(buf, p, (p[0] + sx * arm, p[1]), 9 * k, v)
            _line(buf, p, (p[0], p[1] + sy * arm), 9 * k, v)
    return _guest_frames("charlotte", ppu, fps, (440, 380, 220, 190), draw)


def sigewinne_bubbles(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Sigewinne: six bubbles rising from Furina, one small heart-shaped
    sparkle at the top. 0.7 s."""
    rng = np.random.default_rng(GUEST_SEED + 6)
    bubbles = [(rng.uniform(-90, 90), rng.uniform(0.0, 0.18), rng.uniform(300, 400), rng.uniform(13, 22),
                rng.uniform(0, 2 * math.pi)) for _ in range(6)]
    bubbles[0] = (bubbles[0][0], 0.0, *bubbles[0][2:])    # one rises from the first frame

    def draw(buf, t, u, c, k, i):
        cx, cy = c
        fade = _fade(u, 0.72)
        for x0, t0, speed, r, ph in bubbles:
            if t < t0:
                continue
            dt = t - t0
            x = cx + (x0 + 16 * math.sin(7 * dt + ph)) * k
            y = cy + (60 - speed * dt) * k
            rr = r * (1 + 0.35 * min(1.0, dt / 0.5)) * k
            a = min(1.0, (dt + 0.04) / 0.08) * fade
            _ring(buf, (x, y), rr, 3.2 * k, 0.9 * a)
            _disc(buf, (x, y), rr, 0.22 * a, 3.0)
            _disc(buf, (x - 0.38 * rr, y - 0.38 * rr), 0.28 * rr, a, 0.8)
        w = (u - 0.42) / 0.58
        if 0 <= w <= 1:
            pop = math.sin(math.pi * min(1.0, w * 1.15)) ** 0.6
            hc = (cx + 6 * k, cy - (250 + 20 * w) * k)
            _heart(buf, hc, 22 * k * (0.7 + 0.3 * pop), pop)
            _star(buf, (hc[0] + 30 * k, hc[1] - 24 * k), 14 * k * pop, pop)
    return _guest_frames("sigewinne", ppu, fps, (380, 540, 190, 380), draw)


#: px at REF_PPU from her chest to the plate's centre: in front of her,
#: toward the enemies (her body is about 230 px wide at REF_PPU)
FREMINET_FRONT = 130


def freminet_plate(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Freminet: a hexagonal ice plate flashes in front of Furina and fades.
    0.6 s. The origin is her chest; the plate stands FREMINET_FRONT px
    toward the enemies, narrowed so it reads as a shield held out."""
    def draw(buf, t, u, c, k, i):
        hx, hy = c[0] + FREMINET_FRONT * k, c[1]
        g = min(1.0, u / 0.15)
        sc = 0.8 + 0.2 * g
        v = (0.5 + 0.5 * g) * _fade(u, 0.35) ** 1.3
        if u < 0.22:
            _disc(buf, (hx, hy), 120 * k, 1 - u / 0.22)
        R = 120 * sc * k
        pts = [(hx + math.cos(math.radians(-90 + 60 * j)) * R * 0.62, hy + math.sin(math.radians(-90 + 60 * j)) * R)
               for j in range(6)]
        _poly(buf, pts, 0.3 * v)
        inner = [(hx + (p[0] - hx) * 0.58, hy + (p[1] - hy) * 0.58) for p in pts]
        for a, b in zip(pts, pts[1:] + pts[:1]):
            _line(buf, a, b, 7 * k, v)
        for a, b in zip(inner, inner[1:] + inner[:1]):
            _segment(buf, a, b, 3 * k, 0.6 * v, 0.6 * v)
        for p in pts:
            _segment(buf, (hx, hy), p, 2.5 * k, 0.5 * v, 0.5 * v)
        w = (u - 0.15) / 0.35
        if 0 <= w <= 1:
            _star(buf, pts[0], 28 * k * math.sin(math.pi * w), math.sin(math.pi * w))
    return _guest_frames("freminet", ppu, fps, (420, 380, 120, 190), draw)


def navia_shards(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Navia: a spray of gold crystal shards and a few confetti bits off
    her. 0.6 s."""
    rng = np.random.default_rng(GUEST_SEED + 8)
    shards = [(math.radians(rng.uniform(-165, -15)), rng.uniform(420, 660), rng.uniform(-8, 8),
               rng.uniform(30, 50), rng.uniform(14, 20)) for _ in range(9)]
    bits = [(math.radians(rng.uniform(-160, -20)), rng.uniform(240, 440), rng.uniform(0, 2 * math.pi),
             rng.uniform(8, 18), rng.uniform(9, 13), rng.uniform(4, 6)) for _ in range(10)]

    def draw(buf, t, u, c, k, i):
        cx, cy = c
        if u < 0.18:
            _disc(buf, (cx, cy), 65 * k, 1 - u / 0.18)
        fade = _fade(u, 0.6)
        for ang, speed, spin, length, width in shards:
            x = cx + math.cos(ang) * speed * t * k
            y = cy + (math.sin(ang) * speed * t + 0.5 * 1300 * t * t) * k
            _shard(buf, (x, y), ang + spin * t, length * k, width * k, 0.95 * fade)
        for ang, speed, spin0, spin_v, lw, lh in bits:
            x = cx + math.cos(ang) * speed * t * k
            y = cy + (math.sin(ang) * speed * t + 0.5 * 800 * t * t) * k
            a = spin0 + spin_v * t
            ca, sa = math.cos(a), math.sin(a)
            hw, hh = lw * k / 2, lh * k / 2 * (0.4 + 0.6 * abs(ca))
            quad = [(x + dx * ca - dy * sa, y + dx * sa + dy * ca) for dx, dy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]
            v = (0.55 + 0.45 * abs(math.cos(a * 1.7))) * fade
            fill_quad(buf, quad, (v, v, v, v))
    return _guest_frames("navia", ppu, fps, (640, 540, 340, 340), draw)


def neuvillette_ring(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Neuvillette: a thin water ring that widens fast over the target.
    0.5 s."""
    def draw(buf, t, u, c, k, i):
        cx, cy = c
        if u < 0.14:
            _disc(buf, (cx, cy), 32 * k, 1 - u / 0.14)
        for t0, val in ((0.0, 0.95), (0.16, 0.55)):
            w = (u - t0) / (1 - t0)
            if 0 <= w <= 1:
                R = 16 + 225 * (1 - (1 - min(1.0, w / 0.8)) ** 2)
                _ring(buf, (cx, cy), R * k, (5 * (1 - w) + 2) * k, val * (1 - w) ** 1.1)
    return _guest_frames("neuvillette", ppu, fps, (520, 520, 260, 260), draw)


def chevreuse_crackle(ppu: float = REF_PPU, fps: int = STAGE_FPS):
    """Chevreuse: a small Overloaded crackle spark off her. 0.5 s."""
    def draw(buf, t, u, c, k, i):
        cx, cy = c
        rng = np.random.default_rng(GUEST_SEED + 10 + i // 2)    # the bolts re-strike every two frames
        if u < 0.3:
            _disc(buf, (cx, cy), 38 * k, 1 - u / 0.3)
        v = _fade(u, 0.45)
        for j in range(5):
            ang = 2 * math.pi * (j + rng.uniform(-0.3, 0.3)) / 5
            length = rng.uniform(60, 110) * (0.6 + 0.4 * min(1.0, u * 4))
            pts, r = [(cx, cy)], 0.0
            while r < length:
                r = min(length, r + 22)
                jit = rng.uniform(-12, 12)
                pts.append((cx + (math.cos(ang) * r - math.sin(ang) * jit) * k,
                            cy + (math.sin(ang) * r + math.cos(ang) * jit) * k))
            last = max(1, len(pts) - 1)
            for n, (a, b) in enumerate(zip(pts, pts[1:])):
                _segment(buf, a, b, (5 - 3 * n / last) * k, v * (1 - 0.4 * n / last), v * (1 - 0.4 * (n + 1) / last))
        for j in range(6):
            ang = 2 * math.pi * j / 6 + 0.4
            r = (20 + 140 * u) * k
            _disc(buf, (cx + math.cos(ang) * r, cy + math.sin(ang) * r - 30 * u * u * k), 5 * k, v * 0.9, 0.6)
    return _guest_frames("chevreuse", ppu, fps, (320, 340, 160, 180), draw)


#: guest name -> its effect, in the manifest's guest order
GUEST_EFFECTS = {
    "charlotte": charlotte_flash, "chevreuse": chevreuse_crackle, "clorinde": clorinde_cross,
    "escoffier": escoffier_frost, "freminet": freminet_plate, "lynette": lynette_swirl, "lyney": lyney_cards,
    "navia": navia_shards, "neuvillette": neuvillette_ring, "sigewinne": sigewinne_bubbles,
    "wriothesley": wriothesley_shock,
}
