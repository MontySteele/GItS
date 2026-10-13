"""Style H1 + H3 lite's 2D half: paint Klee's raw renders into the frames pack.py packs.

    python tools/klee_render/post.py --renders <render.py --out dir> [--only idle,select,...]

render.py writes each frame raw to <renders>/raw/<clip>/f_NNN.png (stills to
<renders>/raw/<name>.png) with its `style` pass beside it in aux/<stem>_X.png:
R is the face/bomb protect mask, G and B the brush grain as noise in her own
surface space. This script writes the painted frame to <renders>/<clip>/f_NNN.png
(stills to <renders>/<name>.png), which is what pack.py reads. It never touches
the raw renders, so running it twice gives the same pixels.

The chain, in order (style G's 2D half, ruled 2026-10-13, then H3 lite on
top: [USER], "Let's do H1 + H3 lite"; review/active/klee-visual-paper-2026-10-12.md;
the shader half, H1, is render.py's STYLE), steps 1-3 under a protect mask grown
2 px and feathered so the face and the bomb keep their render (without it her
eyes vanish at game scale):

  1. the interior thin-line fade, strength 0.6 (the silhouette line is the
     shader's texture-tinted hull, so only interior lines are touched);
  2. the grade: Lab chroma soft-knee at 38 / max 54, L* top compressed 97 -> 88,
     whites +4 b*, soft posterise of L* with step 9 at strength 0.3;
  3. anisotropic Kuwahara at radius 2.0 (Kyprianidis, Kang and Doellner 2009);
  4. brush grain at sigma 1.0 L*, read from the `style` pass, so the grain is
     fixed to her surface and moves with her instead of crawling over her;
  5. H3 lite, over the whole finished frame: in CIELAB, chroma above C* 20 is
     squeezed by H3_SQUEEZE (hue and L* untouched), pulling her toward the
     base cast's saturation. Full H3 measured 0.616 (the Ironclad + Silent C*
     p90 against style G's); lite takes half that pull, 0.808. A fixed
     constant, never measured per run.

Every length above is in texture px at COMBAT_PPU (the combat frames) and
scales with a job's ppu, so the merchant, rest and select renders get the same
look on screen. numpy and Pillow only.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

REF_PPU = 300.0         # build.COMBAT_PPU: the scale the parameters below are tuned at

LINES = {"strength": 0.6, "bh_size": 5, "bh_thr": 9.0, "protect_chroma": 28.0,
         "soft_sigma": 0.7, "close_sigma": 0.6}
GRADE = {"c_knee": 38.0, "c_max": 54.0, "l_lo": 12.0, "l_hi": 88.0, "l_src_hi": 97.0,
         "cream": 4.0, "post_step": 9.0, "post_strength": 0.3}
AKF = {"radius": 2.0, "q": 8.0, "alpha": 1.0, "sectors": 8, "sigma_t": 2.0}
GRAIN = {"amp": 1.0, "mottle": 0.6, "length": 6, "angle": 62.0}
PROTECT = {"grow": 2, "feather": 1.0}
#: The `style` pass's grain channels as written (8-bit, display-encoded):
#: centre and spread, measured on the idle frames (2026-10-13). Fixed, not
#: measured per frame, so the grain's strength never flickers.
GRAIN_CENTRE = 187.4
GRAIN_SD = {"fine": 4.0, "mottle": 11.0, "fine_smeared": 0.32}
#: Above this scale the Kuwahara runs on a reduced copy and only its change is
#: carried back up (the select close-up, rendered at ~5.7x): the same strokes
#: on screen at a tractable cost.
AKF_MAX_SCALE = 2.0
#: H3 lite: C* above H3_KNEE is scaled by H3_SQUEEZE = 1 - (1 - 0.616) * 0.5.
H3_KNEE = 20.0
H3_SQUEEZE = 1 - (1 - 0.616) * 0.5


# ------------------------------------------------------------ small image ops
def _pad(x, r, mode="reflect"):
    """Pad the first two axes by r. 'reflect' is OpenCV's BORDER_REFLECT_101."""
    w = [(r, r), (r, r)] + [(0, 0)] * (x.ndim - 2)
    return np.pad(x, w, mode=mode)


def gauss(x, sigma):
    if sigma <= 0:
        return x
    r = max(1, int(round(sigma * 4)))
    t = np.arange(-r, r + 1, dtype=np.float32)
    k = np.exp(-t * t / (2 * sigma * sigma))
    k /= k.sum()
    p = _pad(x.astype(np.float32), r)
    H, W = x.shape[:2]
    tmp = sum(k[i] * p[:, i:i + W] for i in range(2 * r + 1))
    return sum(k[i] * tmp[i:i + H] for i in range(2 * r + 1))


def sobel(x):
    p = _pad(x, 1)
    H, W = x.shape[:2]

    def s(dy, dx):
        return p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]

    gx = (s(-1, 1) + 2 * s(0, 1) + s(1, 1)) - (s(-1, -1) + 2 * s(0, -1) + s(1, -1))
    gy = (s(1, -1) + 2 * s(1, 0) + s(1, 1)) - (s(-1, -1) + 2 * s(-1, 0) + s(-1, 1))
    return gx, gy


def ellipse_offsets(size):
    """OpenCV's MORPH_ELLIPSE structuring element of size x size, as offsets."""
    r = size // 2
    if r == 0:
        return [(0, 0)]
    out = []
    inv_r2 = 1.0 / (r * r)
    for i in range(size):
        dy = i - r
        if abs(dy) <= r:
            dx = int(round(r * math.sqrt(max(0.0, 1 - dy * dy * inv_r2))))
            out += [(dy, j) for j in range(-dx, dx + 1)]
    return out


def morph(x, size, op):
    offs = ellipse_offsets(size)
    r = size // 2
    fill = -np.inf if op == "dilate" else np.inf
    p = np.pad(x.astype(np.float32), [(r, r), (r, r)] + [(0, 0)] * (x.ndim - 2), constant_values=fill)
    H, W = x.shape[:2]
    f = np.maximum if op == "dilate" else np.minimum
    out = None
    for dy, dx in offs:
        v = p[r + dy:r + dy + H, r + dx:r + dx + W]
        out = v.copy() if out is None else f(out, v)
    return out


def close(x, size):
    return morph(morph(x, size, "dilate"), size, "erode")


def push_pull(rgb, known):
    """Fill the unknown pixels from the known ones (a pull-push pyramid), so a
    filter reaching past her edge reads her own colours, never black. The
    first few rings grow from the nearest known pixels (as an inpaint does),
    so the rim takes the colour right beside it; the pyramid fills the rest."""
    known = known.copy()
    rgb = np.where(known[..., None], rgb, 0).astype(np.float32)
    for _ in range(3):
        w = known.astype(np.float32)
        pw = np.pad(w, 1)
        pc = np.pad(rgb * w[..., None], [(1, 1), (1, 1), (0, 0)])
        H, W = w.shape
        ws = sum(pw[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1))
        cs = sum(pc[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1))
        grow = (~known) & (ws > 0)
        if not grow.any():
            break
        rgb = np.where(grow[..., None], cs / np.maximum(ws, 1e-8)[..., None], rgb)
        known = known | grow
    w = known.astype(np.float32)
    if w.sum() == 0:
        return rgb
    levels = [(rgb * w[..., None], w)]
    while min(levels[-1][1].shape) > 1:
        c, ww = levels[-1]
        H, W = ww.shape
        H2, W2 = (H + 1) // 2, (W + 1) // 2
        cp = np.zeros((H2 * 2, W2 * 2, 3), np.float32)
        wp = np.zeros((H2 * 2, W2 * 2), np.float32)
        cp[:H, :W], wp[:H, :W] = c, ww
        c2 = cp.reshape(H2, 2, W2, 2, 3).sum((1, 3))
        w2 = wp.reshape(H2, 2, W2, 2).sum((1, 3))
        levels.append((c2, w2))
    col = levels[-1][0] / np.maximum(levels[-1][1], 1e-8)[..., None]
    for c, ww in reversed(levels[:-1]):
        H, W = ww.shape
        up = np.repeat(np.repeat(col, 2, 0), 2, 1)[:H, :W]
        own = c / np.maximum(ww, 1e-8)[..., None]
        t = np.clip(ww, 0, 1)[..., None]
        col = own * t + up * (1 - t)
    return np.where(known[..., None], rgb, col)


# ------------------------------------------------------------ colour
_M = np.array([[0.412453, 0.357580, 0.180423],
               [0.212671, 0.715160, 0.072169],
               [0.019334, 0.119193, 0.950227]], np.float32)
_WHITE = np.array([0.950456, 1.0, 1.088754], np.float32)


def to_lab(rgb):
    c = np.clip(rgb, 0, 1)
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    xyz = lin @ _M.T / _WHITE
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    L = np.where(xyz[..., 1] > 0.008856, 116 * f[..., 1] - 16, 903.3 * xyz[..., 1])
    return np.dstack([L, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])]).astype(np.float32)


def from_lab(lab):
    L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    fy = (L + 16) / 116
    fx, fz = fy + A / 500, fy - B / 200
    f = np.dstack([fx, fy, fz])
    xyz = np.where(f > 0.206893, f ** 3, (f - 16 / 116) / 7.787) * _WHITE
    lin = xyz @ np.linalg.inv(_M).T
    lin = np.clip(lin, 0, 1)
    c = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)
    return np.clip(c, 0, 1).astype(np.float32)


# ------------------------------------------------------------ the chain
def protect_mask(r_channel, a, s):
    face = (r_channel > 0.5) & (a > 0.4)
    grow = max(1, int(round(PROTECT["grow"] * s)))
    p = morph(face.astype(np.float32), 2 * grow + 1, "dilate")
    return gauss(p, PROTECT["feather"] * s)


def line_fade(rgb, a, protect, s):
    """Fade the thin dark interior lines toward the fill (variant D at
    band 0: the silhouette is left to the shader's tinted hull)."""
    size = 2 * int(round(LINES["bh_size"] * s / 2)) + 1
    lab = to_lab(rgb)
    L = lab[..., 0]
    blackhat = close(L, size) - L
    C = np.hypot(lab[..., 1], lab[..., 2])
    inside = a >= 0.5
    mline = (blackhat > LINES["bh_thr"]) & (C < LINES["protect_chroma"]) & inside & (protect < 0.5)
    soft = gauss(mline.astype(np.float32), LINES["soft_sigma"] * s)[..., None]
    closed = gauss(np.dstack([close(rgb[..., i], size) for i in range(3)]), LINES["close_sigma"] * s)
    k = LINES["strength"]
    return rgb * (1 - k * soft) + closed * (k * soft)


def grade(rgb):
    g = GRADE
    lab = to_lab(rgb)
    L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    C = np.hypot(A, B)
    h = np.arctan2(B, A)
    span = g["c_max"] - g["c_knee"]
    C2 = np.where(C > g["c_knee"], g["c_knee"] + span * (1 - np.exp(-np.maximum(C - g["c_knee"], 0) / span)), C)
    L2 = np.where(L > g["l_lo"], g["l_lo"] + (L - g["l_lo"]) * (g["l_hi"] - g["l_lo"]) / (g["l_src_hi"] - g["l_lo"]), L)
    A2, B2 = C2 * np.cos(h), C2 * np.sin(h)
    wt = np.clip((L - 70) / 25, 0, 1) * np.clip(1 - C / 20, 0, 1)
    A2 = A2 + wt * g["cream"] * 0.25
    B2 = B2 + wt * g["cream"]
    q = np.round(L2 / g["post_step"]) * g["post_step"]
    L2 = L2 + (q - L2) * g["post_strength"]
    return from_lab(np.dstack([L2, A2, B2]))


def akf(rgb, radius, q=8.0, alpha=1.0, sectors=8, sigma_t=2.0):
    """Anisotropic Kuwahara: each pixel takes the weighted mean of the
    flattest of `sectors` sectors of an ellipse aligned to the local
    structure, so flat areas become strokes and edges stay put."""
    H, W, _ = rgb.shape
    gx, gy = sobel(rgb)
    gx, gy = gx / 8, gy / 8
    E, Fm, G = (gauss(x, sigma_t) for x in ((gx * gx).sum(-1), (gx * gy).sum(-1), (gy * gy).sum(-1)))
    tr = E + G
    det = np.sqrt(np.maximum((E - G) ** 2 + 4 * Fm * Fm, 0))
    l1, l2 = (tr + det) / 2, (tr - det) / 2
    tx, ty = l1 - E, -Fm
    n = np.hypot(tx, ty)
    ok = n > 1e-8
    tx = np.where(ok, tx / np.maximum(n, 1e-8), 1.0)
    ty = np.where(ok, ty / np.maximum(n, 1e-8), 0.0)
    A = np.where(tr > 1e-8, (l1 - l2) / np.maximum(tr, 1e-8), 0.0)
    phi = np.arctan2(ty, tx)
    a_ = radius * np.clip((alpha + A) / alpha, 0.1, 2.0)
    b_ = radius * np.clip(alpha / (alpha + A), 0.1, 2.0)
    cphi, sphi = np.cos(phi), np.sin(phi)
    R = int(math.ceil(radius * 2))
    pad = np.pad(rgb, [(R, R), (R, R), (0, 0)], mode="symmetric")
    m = np.zeros((sectors, H, W, 3), np.float32)
    s2 = np.zeros_like(m)
    w = np.zeros((sectors, H, W), np.float32)
    centres = 2 * np.pi * np.arange(sectors) / sectors
    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            u = (cphi * dx + sphi * dy) / a_
            v = (-sphi * dx + cphi * dy) / b_
            rr = u * u + v * v
            inside = rr <= 1.0
            if not inside.any():
                continue
            g = (np.exp(-rr * 2.0) * inside).astype(np.float32)
            ang = np.arctan2(v, u)
            c = pad[R + dy:R + dy + H, R + dx:R + dx + W]
            cc = c * c
            for k in range(sectors):
                if dx or dy:
                    d = np.angle(np.exp(1j * (ang - centres[k])))
                    ww = g * np.exp(-(d / (np.pi / sectors)) ** 2 * 1.5).astype(np.float32)
                else:
                    ww = np.full_like(g, 1.0 / sectors)
                w[k] += ww
                m[k] += ww[..., None] * c
                s2[k] += ww[..., None] * cc
    out = np.zeros_like(rgb)
    tot = np.zeros((H, W), np.float32)
    for k in range(sectors):
        wk = np.maximum(w[k], 1e-6)[..., None]
        mk = m[k] / wk
        sd = np.sqrt(np.abs(s2[k] / wk - mk * mk).sum(-1)) * 255
        ak = 1.0 / (1.0 + np.power(sd, q / 4.0))
        out += ak[..., None] * mk
        tot += ak
    return out / tot[..., None]


def _resize(x, size):
    chans = x if x.ndim == 3 else x[..., None]
    out = [np.asarray(Image.fromarray(chans[..., i].astype(np.float32), "F").resize(size, Image.BICUBIC))
           for i in range(chans.shape[-1])]
    o = np.dstack(out)
    return o if x.ndim == 3 else o[..., 0]


def kuwahara(rgb, s):
    radius = AKF["radius"] * s
    kw = {k: AKF[k] for k in ("q", "alpha", "sectors")}
    if s <= AKF_MAX_SCALE:
        return akf(rgb, radius, sigma_t=AKF["sigma_t"] * s, **kw)
    f = s / AKF_MAX_SCALE
    H, W = rgb.shape[:2]
    small = _resize(rgb, (max(1, round(W / f)), max(1, round(H / f))))
    delta = akf(small, AKF["radius"] * AKF_MAX_SCALE, sigma_t=AKF["sigma_t"] * AKF_MAX_SCALE, **kw) - small
    return np.clip(rgb + _resize(delta, (W, H)), 0, 1)


def smear(x, length, angle):
    """Average along a line `length` px each way at `angle` degrees: the
    stroke direction of the brush grain."""
    t = math.radians(angle)
    offs = sorted({(int(round(i * math.sin(t))), int(round(i * math.cos(t))))
                   for i in range(-length, length + 1)})
    r = length
    p = np.pad(x, r)
    H, W = x.shape
    return sum(p[r + dy:r + dy + H, r + dx:r + dx + W] for dy, dx in offs) / len(offs)


def grain(rgb, aux, s):
    """Brush grain on L*: the `style` pass's surface-space noise, smeared
    into short strokes (as the prototype's screen noise was) plus a coarse
    mottle. The noise is her surface's, so it moves with her; the smear is a
    fixed screen direction, as a brush's is."""
    on = (aux[..., 3] > 127).astype(np.float32)     # where the pass covers her
    length = max(1, int(round(GRAIN["length"] * s)))
    fine = (aux[..., 1] - GRAIN_CENTRE) / GRAIN_SD["fine"] * on
    fine = smear(fine, length, GRAIN["angle"]) / np.maximum(smear(on, length, GRAIN["angle"]), 1e-3)
    fine = fine / GRAIN_SD["fine_smeared"]
    mottle = (aux[..., 2] - GRAIN_CENTRE) / GRAIN_SD["mottle"] * on
    n = np.clip((fine + GRAIN["mottle"] * mottle) / math.sqrt(1 + GRAIN["mottle"] ** 2), -3, 3)
    lab = to_lab(rgb)
    lab[..., 0] = np.clip(lab[..., 0] + GRAIN["amp"] * n, 0, 100)
    return from_lab(lab)


def h3_lite(rgb):
    """H3 lite: squeeze chroma above the knee; L* and hue are untouched."""
    lab = to_lab(rgb)
    A, B = lab[..., 1], lab[..., 2]
    C = np.hypot(A, B)
    k = np.where(C > H3_KNEE, (H3_KNEE + (C - H3_KNEE) * H3_SQUEEZE) / np.maximum(C, 1e-6), 1.0)
    lab[..., 1], lab[..., 2] = A * k, B * k
    return from_lab(lab)


def paint(im: Image.Image, aux: Image.Image, s: float) -> Image.Image:
    """One frame through the whole chain; `s` = this render's ppu / REF_PPU.
    Alpha is never changed. Each step reads her colours bled past the edge
    (push_pull), so the half-covered rim takes the fill just inside it."""
    arr = np.asarray(im.convert("RGBA")).astype(np.float32) / 255
    rgb, a = arr[..., :3], arr[..., 3]
    x = np.asarray(aux.convert("RGBA")).astype(np.float32)
    prot = protect_mask(x[..., 0] / 255, a, s)
    body = a >= 0.5
    r = line_fade(push_pull(rgb, a >= 0.02), a, prot, s)
    r = grade(push_pull(r, body))
    r = kuwahara(push_pull(r, body), s) * (1 - prot[..., None]) + r * prot[..., None]
    r = grain(r, x, s)
    r = h3_lite(r)
    r = np.where(a[..., None] > 0, r, 0)
    out = np.dstack([np.clip(r * 255 + 0.5, 0, 255), np.clip(a * 255 + 0.5, 0, 255)]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def _job(src: Path, dst: Path, s: float):
    aux = src.parent / "aux" / f"{src.stem}_X.png"
    dst.parent.mkdir(parents=True, exist_ok=True)
    paint(Image.open(src), Image.open(aux), s).save(dst)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", required=True, help="render.py --out dir")
    ap.add_argument("--only", default="", help="comma list of clips/stills (default: all found)")
    ap.add_argument("--jobs", type=int, default=0, help="worker processes (default: cpu count)")
    args = ap.parse_args(argv)
    R = Path(args.renders)
    raw = R / "raw"
    only = {x for x in args.only.split(",") if x}
    work = []
    for meta_path in sorted(R.glob("*.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        name = meta.get("clip") or meta.get("still")
        if not name or (only and name not in only):
            continue
        s = float(meta["ppu"]) / REF_PPU
        if "clip" in meta:
            for i in range(len(meta["times"])):
                work.append((raw / name / f"f_{i:03d}.png", R / name / f"f_{i:03d}.png", s))
        else:
            work.append((raw / f"{name}.png", R / f"{name}.png", s))
    missing = [str(w[0]) for w in work if not w[0].exists()]
    if missing:
        print("missing raw renders:", missing[:5])
        return 1
    import concurrent.futures as cf
    import os
    n = args.jobs or max(1, (os.cpu_count() or 2) - 1)
    with cf.ProcessPoolExecutor(n) as ex:
        list(ex.map(_job, *zip(*work)))
    print(f"post: painted {len(work)} frames under {R}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
