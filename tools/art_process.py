#!/usr/bin/env python3
"""Process art/raw/ into ImageGen targets per art/plan.tsv (spec §2 step 3).

- cover: scale to fill W×H, crop (focus=top keeps the top of the frame — right
  for TCG card art and full-body renders; center otherwise). focus may instead
  be a fractional anchor `x<f>`, `y<f>` or `x<f>,y<f>` naming where in the
  SOURCE the crop should centre — see cover() for why top/center is not enough.
  `ground<f>[,x<f>]` is the third spelling: it lands SOURCE row `f` on the
  plate's COMBAT FEET LINE rather than at the crop's centre, which is what a
  combat background needs — see COMBAT_FEET_ROW.
- contain: fit inside W×H, pad to exact size on transparency (icons)
- cover_autocrop: crop to the art's content first (splash/Wish sources float
  the figure in a large transparent void), then fit — focus carries
  `cover|contain[@margin]`, default cover@0.06
- cut: REMOVE an opaque backdrop, then trim + fit. For the Enemy Archive
  captures behind the Teyvat still portraits (docs/current/research/
  teyvat-portrait-sources-2026-09-16.md): every one is a `truecolour` screen
  capture of the in-game Archive page, and media.md §3 requires alpha because
  a still portrait composites over the arena. focus carries
  `cut[@tolerance][/fit-focus][:pocket][;key=value...]`, default
  `cut@30/top:0.004;chroma=12;figure=main;split=0`. The matte keys against a
  LOCAL
  backdrop MODEL (a robust quadratic surface fit to the border) rather than a
  flat RGB distance from one corner colour, plus a blue-chroma gate, because
  the Archive backdrop is navy and a flat 48 also matched black body pixels
  (2026-09-17: frostarm_lawachurl, the Rifthounds and the Fatui came back full
  of holes). `figure=main` then keeps the main body and drops the detached
  flanking figures the Archive GROUP captures bring along (the slimes);
  `figure=all` keeps every component, and `;split=N` parts two bodies joined
  by a bridge thinner than 2N+1 (the slimes overlap at the leaves) before the
  figure is chosen -- off by default, because a staff handle is thin too.
- raw: byte-for-byte copy (combat-model source art)
- gif sources: extract the frame at frame_pct% through the clip
- svg sources: render via macOS qlmanage; fall back to the wiki's same-name PNG
  (upscaled — flagged if the upscale factor is ugly)

auto rows  -> final target path.
shortlist  -> art/candidates/<asset_id>/r<rank>.png at target dims,
              plus rank 1 ALSO written to the final target as the provisional
              pick (art never blocks the build; overridden by --apply-picks).
--apply-picks art/picks.tsv  (asset_id<TAB>rank per line) promotes selections.
--assets a,b,c   render ONLY those ids' shortlist candidates; nothing placed,
                 manifest untouched (a gate review must not promote a rank 1).
--art-root PATH  read art/raw/ and write art/candidates/ AND the ImageGen
                 out-paths under PATH instead of this checkout -- how a
                 worktree reaches the main checkout's gitignored art WITHOUT
                 linking it in (operations/worktrees.md). All three move
                 together on purpose: a run that read the main checkout's
                 sources and then wrote the shipping pixels into the worktree's
                 own ImageGen put them where build_pck.ps1 never looks, so the
                 flag did half its job and said nothing about the other half.
                 art/plan.tsv and art/SOURCES.tsv still come from THIS
                 checkout, which is the point -- the branch's plan rendered
                 against, and into, the main checkout's pixels.

Derived extras: ui/select_portrait_locked.png (desaturated+darkened).
Updates art/manifest.csv status/tier/source columns in place.

Requires Pillow: python3 -m venv .venv && .venv/bin/pip install pillow
"""
import csv
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageSequence

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "art" / "raw"
CAND = ROOT / "art" / "candidates"
MANIFEST = ROOT / "art" / "manifest.csv"
# Where a plan row's `out` column lands. Same as ROOT unless --art-root moves
# the whole gitignored art tree to another checkout; see main().
ART_OUT = ROOT

sys.path.insert(0, str(ROOT / "tools"))
from art_fetch import read_plan, rawname  # noqa: E402

UPSCALE_FLAG = 1.6  # source-to-target scale factor above which we warn

# THE COMBAT FEET LINE. Every creature in a fight stands on one row of the
# bg_00 plate, and it is a property of the layer geometry, not of the window:
# the layer TextureRect is 2764.8x1296 anchored to its parent's CENTRE
# (klee-mod/pck-src/scenes/backgrounds/<id>/layers/<id>_bg_00_a.tscn), so a
# 1382x648 plate is drawn at 2x, centred, and scaled with the canvas. Measured
# 2026-09-17 off two captures at DIFFERENT window aspects by locating the
# creature HP-bar widget, whose top edge is the creature's floor:
#   4:3  (2160x1620) bar top view row 1069, centre 810,  scale 1.2855
#        -> 201.5 design px below centre
#   16:9 (3840x2160) bar top view row 1483, centre 1080, scale 1.986
#        -> 202.9 design px below centre
# 202 design px = 101 plate rows below the plate's own centre (324). The
# fraction of the WINDOW is 0.660 and 0.687 respectively, which is why this is
# a plate row and never a window fraction. See operations/act-assets.md.
COMBAT_PLATE_H = 648
COMBAT_FEET_ROW = 425            # 0.6559 of the plate; NOT of the window

# Flat backing for item renders on card portraits (taste-pass directive 1):
# transparent renders under `cover` smear their edge pixels across the frame,
# and transparent padding reads as a hole in the card. Warm parchment, close
# to the game's card-art paper. Icons keep transparent padding.
CARD_BG = (0xEF, 0xE4, 0xCE, 0xFF)
flags = []


def load_source(row):
    """Return an RGBA PIL image for the plan row, or None if raw file missing."""
    p = RAW / rawname(row["title"])
    if row["source"] == "svg":
        if p.exists():
            png = render_svg(p, max(row["w"], row["h"]))
            if png is not None:
                return png
        # Wiki-rendered raster (fetched by art_fetch on every platform;
        # qlmanage only exists on macOS).
        thumb = RAW / (rawname(row["title"]) + ".thumb.png")
        if thumb.exists():
            return Image.open(thumb).convert("RGBA")
        fb = RAW / rawname(row["title"][:-4] + ".png")
        if fb.exists():
            flags.append(f"{row['asset_id']}: svg render failed, using 64px png fallback (upscale)")
            return Image.open(fb).convert("RGBA")
        return None
    if not p.exists():
        return None
    img = Image.open(p)
    if row["source"] == "gif":
        frames = list(ImageSequence.Iterator(img))
        idx = min(len(frames) - 1, round((row["frame"] or 50) / 100 * (len(frames) - 1)))
        img = frames[idx].convert("RGBA")
    return img.convert("RGBA")


def render_svg(path, size):
    with tempfile.TemporaryDirectory() as td:
        try:
            r = subprocess.run(
                ["qlmanage", "-t", "-s", str(max(size, 256)), "-o", td, str(path)],
                capture_output=True)
        except FileNotFoundError:
            # qlmanage is macOS-only; on Windows fall through to the wiki's
            # same-name .png fallback that load_source already handles.
            return None
        outs = list(Path(td).glob("*.png"))
        if r.returncode == 0 and outs:
            return Image.open(outs[0]).convert("RGBA")
    return None


def _anchor(focus):
    """Parse `x<frac>`, `y<frac>` or `x<frac>,y<frac>` into (ax, ay) fractions.

    Returns None for anything else, which keeps the legacy `top` / `center`
    keywords on their original code path byte-for-byte -- shipped Klee art
    must not shift because a new spelling was added.
    """
    ax = ay = None
    for part in focus.split(","):
        part = part.strip()
        try:
            if part.startswith("x"):
                ax = float(part[1:])
            elif part.startswith("y"):
                ay = float(part[1:])
            else:
                return None
        except ValueError:
            return None
    return None if (ax is None and ay is None) else (ax, ay)


def _ground(focus):
    """Parse `ground<f>` (optionally with `,x<f>`) into (gy, ax), else None.

    Returns None for every legacy spelling, which keeps `top` / `center` /
    `x<f>` / `y<f>` on their original code path byte-for-byte -- shipped Klee
    art must not shift because a new spelling was added.
    """
    gy = ax = None
    for part in focus.split(","):
        part = part.strip()
        try:
            if part.startswith("ground"):
                gy = float(part[len("ground"):])
            elif part.startswith("x"):
                ax = float(part[1:])
            else:
                return None
        except ValueError:
            return None
    return None if gy is None else (gy, ax)


def cover(img, w, h, focus):
    """Scale to fill w*h and crop.

    focus is `top`, `center`, a fractional anchor `x<f>[,y<f>]` naming the
    point in the SOURCE the crop centres on, or `ground<f>[,x<f>]` naming the
    SOURCE row that must land on the plate's COMBAT FEET LINE. Any of them may
    carry `@zoom`.

    The anchor exists because top/center cannot express the common case
    (2026-07-23 taste pass): official portrait art puts the face ~25-33% down
    and parks the GENSHIN IMPACT / HOYOVERSE wordmarks on the top and bottom
    edges. `center` cropped 500x380 out of the middle and returned a headless
    torso; `top` would have returned the wordmark. `y0.28` returns the face.

    `ground` exists because a combat background is not framed, it is REGISTERED
    (2026-09-17): the picture is wrong unless the ground plane in it falls on
    the one row the engine stands creatures on. `y<f>` cannot say that, because
    it centres the named row at h/2 and the feet line is lower. Under `top` all
    six Teyvat faces put the feet line on far terrain, open sea or rooftops,
    which is the "characters in midair" the report of 2026-09-17 named.
    """
    # focus "center@1.5" punches the crop 1.5x into the frame (taste-pass
    # directive 2: VFX gif frames want the blast, not the whole battlefield).
    # The zoom runs to the NEXT COMMA, not to the end of the string: it used to
    # take everything after the `@`, which was invisible while every spelling
    # put the zoom last, and broke the moment one did not
    # (`ground0.70@1.32,x0.46` -> float("1.32,x0.46")).
    zoom = 1.0
    if "@" in focus:
        head, _, tail = focus.partition("@")
        number, comma, rest = tail.partition(",")
        zoom = float(number)
        focus = head + (comma + rest if comma else "")
    scale = max(w / img.width, h / img.height) * zoom
    if scale > UPSCALE_FLAG:
        flags.append(f"upscale x{scale:.1f}")
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    ground = _ground(focus)
    if ground is not None:
        gy, ax = ground
        y = round(gy * img.height - h * COMBAT_FEET_ROW / COMBAT_PLATE_H)
        if not 0 <= y <= img.height - h:
            # The source cannot deliver the asked-for ground at this zoom. Say
            # so: a silently clamped ground row is exactly the defect this
            # focus exists to catch.
            flags.append(f"ground {gy} clamped (raise @zoom)")
        y = max(0, min(img.height - h, y))
        x = ((img.width - w) // 2 if ax is None
             else max(0, min(img.width - w, round(ax * img.width - w / 2))))
        return img.crop((x, y, x + w, y + h))
    anchor = _anchor(focus)
    if anchor is None:
        x = (img.width - w) // 2
        y = 0 if focus == "top" else (img.height - h) // 2
    else:
        ax, ay = anchor
        x = (img.width - w) // 2 if ax is None else round(ax * img.width - w / 2)
        y = (img.height - h) // 2 if ay is None else round(ay * img.height - h / 2)
        x = max(0, min(img.width - w, x))
        y = max(0, min(img.height - h, y))
    return img.crop((x, y, x + w, y + h))


CENTER_THRESH = 200   # opaque FIGURE: what composition centers on
INCLUDE_THRESH = 10   # figure + faint FX: what the crop must not clip
AUTOCROP_MARGIN = 0.06


def _alpha_box(img, thresh):
    """Bbox of pixels whose alpha exceeds `thresh` (PIL-only, no numpy)."""
    return img.getchannel("A").point(lambda v: 255 if v > thresh else 0).getbbox()


def cover_autocrop(img, w, h, spec):
    """Crop a float-in-void splash to its content, then fit the card.

    Wish/splash sources frame the figure inside a large transparent void
    (Klee Wish: 2048x1024 canvas, content only 35% of it), so under plain
    `cover` the character shrinks to a blob. This finds the content first.

    Two thresholds, deliberately: the CENTER box is the opaque figure, so
    composition centres on the CHARACTER and not on asymmetric VFX that
    would drag it off-centre; the INCLUDE box adds faint effects so the
    splash (Fischl's raven, Chevreuse's musket-flash) is not clipped.

    spec (the plan's `focus` column) is `fit[@margin]`:
      cover   - scale to FILL w*h and centre-crop on the figure. Default.
      contain - scale to FIT inside w*h, pad on the card backing. The
                per-card fallback for sources where cover clips the figure.
    Margin defaults to 6% (user-ratified: reviewed tight-vs-14%, tight won
    everywhere; medium only added dead canvas). It stays a parameter.

    Thin FX tips (Barbara's staff, Bennett's flare) MAY clip the frame edge
    by design -- that is a wisp, not the figure. Do not widen to chase them.
    """
    fit, margin = "cover", AUTOCROP_MARGIN
    if spec and spec not in ("center", "top"):
        if "@" in spec:
            fit, m = spec.split("@", 1)
            margin = float(m)
        else:
            fit = spec
    if fit not in ("cover", "contain"):
        raise SystemExit(
            f"cover_autocrop: unknown fit {fit!r} (want cover|contain[@margin])")

    inc = _alpha_box(img, INCLUDE_THRESH)
    if inc is None:                      # fully transparent: nothing to crop
        return cover(img, w, h, "center") if fit == "cover" else contain(img, w, h)
    ctr = _alpha_box(img, CENTER_THRESH) or inc

    mx = int((inc[2] - inc[0]) * margin)
    my = int((inc[3] - inc[1]) * margin)
    x0, y0 = max(0, inc[0] - mx), max(0, inc[1] - my)
    x1, y1 = min(img.width, inc[2] + mx), min(img.height, inc[3] + my)
    crop = img.crop((x0, y0, x1, y1))

    if fit == "contain":
        return contain(crop, w, h)

    # cover: scale to fill, then centre the crop window on the FIGURE centre
    # (clamped into the image) rather than on the geometric middle.
    scale = max(w / crop.width, h / crop.height)
    if scale > UPSCALE_FLAG:
        flags.append(f"upscale x{scale:.1f}")
    crop = crop.resize((max(1, round(crop.width * scale)),
                        max(1, round(crop.height * scale))), Image.LANCZOS)
    fx = ((ctr[0] + ctr[2]) / 2 - x0) * scale
    fy = ((ctr[1] + ctr[3]) / 2 - y0) * scale
    x = max(0, min(crop.width - w, round(fx - w / 2)))
    y = max(0, min(crop.height - h, round(fy - h / 2)))
    return crop.crop((x, y, x + w, y + h))


CUT_TOLERANCE = 30      # RGB distance from the LOCAL backdrop model (see below)
CUT_CHROMA = 12         # how much blue chroma a backdrop pixel may be missing
CUT_WORK_MAX = 900      # the matte is solved at this size, not on a 2880px plate
CUT_FEATHER = 1.2       # gaussian sigma on the matte, in WORK pixels
CUT_BORDER_ALPHA = 0.98  # border already this transparent => honour that alpha
CUT_SPECK_FRAC = 0.0005  # foreground islands below this share of the frame go
CUT_POCKET_FRAC = 0.004  # ENCLOSED backdrop at or above this share is removed
CUT_POCKET_RESID = 0.55  # ...and only if it matches the model this tightly
CUT_BRIDGE = 2          # hairline leaks this thin do not carry the flood
CUT_BORDER_BAND = 0.012  # share of the long edge sampled as "certainly backdrop"
CUT_FIGURE_MARGIN = 0.08  # a satellite inside the main bbox grown by this stays
CUT_FIGURE_TIE = 0.80   # components this close in area to the largest tie-break
CUT_SPLIT = 0           # `;split=N` parts figures joined by a bridge thinner
                        # than 2N+1. OFF by default: a staff handle is a thin
                        # bridge too, and splitting one loses a real feature.


def _cut_spec(spec):
    """Parse the `cut` row's focus column.

    `cut[@tolerance][/fit-focus][:pocket][;key=value][;key=value]`

    The positional fields are separated rather than overloaded: `@` is the
    matte tolerance, `/` is the focus handed to the FIT afterwards, and `:` is
    the enclosed-pocket threshold as a fraction of the frame. Anything added
    after those rides as `;key=value` so the grammar can grow without a fifth
    punctuation mark; `chroma`, `figure` and `split` are the keys today. `cut`,
    `cut@60`, `cut@60/center`, `cut/contain`, `cut@60/top:0.01` and
    `cut;figure=all` are all legal, and a bare focus keyword (`top`) is
    accepted too, so a row that says nothing about the matte reads as "default
    matte, this focus".

    Returns (tolerance, fit, focus, pocket, chroma, figure, split) with fit in
    {cover, contain} and figure in {main, all}.
    """
    spec = (spec or "").strip() or "cut"
    head, *extras = spec.split(";")
    head, _, pocket = head.partition(":")
    head, _, focus = head.partition("/")
    head, _, tol = head.partition("@")
    head = head.strip() or "cut"
    if head != "cut":
        # `focus`-only spelling: `top`, `center`, `y0.30`, `contain`.
        focus, head = head, "cut"
    focus = (focus or "top").strip()
    try:
        tolerance = float(tol) if tol else CUT_TOLERANCE
    except ValueError:
        raise SystemExit(f"cut: bad tolerance {tol!r} (want cut[@tolerance])")
    try:
        pocket_frac = float(pocket) if pocket.strip() else CUT_POCKET_FRAC
    except ValueError:
        raise SystemExit(
            f"cut: bad pocket fraction {pocket!r} (want cut[...][:fraction])")
    chroma, figure, split = CUT_CHROMA, "main", CUT_SPLIT
    for extra in extras:
        extra = extra.strip()
        if not extra:
            continue
        key, _, value = extra.partition("=")
        key, value = key.strip(), value.strip()
        if key == "chroma":
            try:
                chroma = float(value)
            except ValueError:
                raise SystemExit(f"cut: bad chroma {value!r} (want ;chroma=N)")
        elif key == "figure":
            if value not in ("main", "all"):
                raise SystemExit(
                    f"cut: bad figure {value!r} (want ;figure=main|all)")
            figure = value
        elif key == "split":
            try:
                split = int(value)
            except ValueError:
                raise SystemExit(f"cut: bad split {value!r} (want ;split=N)")
            if split < 0:
                raise SystemExit(f"cut: split must not be negative ({value!r})")
        else:
            raise SystemExit(
                f"cut: unknown option {extra!r} "
                f"(want ;chroma=N, ;figure=main|all or ;split=N)")
    fit = "cover"
    if focus == "contain":
        fit, focus = "contain", "center"
    return tolerance, fit, focus, pocket_frac, chroma, figure, split


def _erode(mask, k):
    """k iterations of a 4-connected erosion, treating OUTSIDE the frame as set.

    Outside-is-set matters: the flood is seeded on the border, so eroding the
    border ring away would leave the seed row empty and the matte would key
    nothing at all.
    """
    import numpy as np
    for _ in range(k):
        p = np.pad(mask, 1, constant_values=True)
        mask = (p[1:-1, 1:-1] & p[:-2, 1:-1] & p[2:, 1:-1]
                & p[1:-1, :-2] & p[1:-1, 2:])
    return mask


def _dilate(mask, k):
    import numpy as np
    for _ in range(k):
        p = np.pad(mask, 1, constant_values=False)
        mask = (p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1]
                | p[1:-1, :-2] | p[1:-1, 2:])
    return mask


def _components(mask):
    """Every 4-connected component of `mask`, largest first, as bool arrays."""
    import numpy as np
    out = []
    todo = mask.copy()
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys.tolist(), xs.tolist()):
        if not todo[y, x]:
            continue
        comp = _flood(todo, [(y, x)])
        todo &= ~comp
        out.append(comp)
    out.sort(key=lambda c: -int(c.sum()))
    return out


def _backdrop_model(rgb, band):
    """Robust quadratic surface fit to the border ring, per channel.

    Why a MODEL and not a colour. The Archive backdrop is a smooth navy
    vignette with a starfield and a reflective floor, so the shipped rule --
    "within `tolerance` RGB of the nearest corner colour" -- had to run a wide
    tolerance (48) just to cover the vignette's own swing from the top corners
    to the bottom ones. At 48 a black body pixel is INSIDE the key: measured
    2026-09-17, frostarm_lawachurl's shaded fur sits ~35-48 from the corner
    navy, and the first 81-row cut came back with the body full of holes
    wherever a hairline of keyed pixels let the border flood in. Fitting the
    vignette instead removes that swing from the residual: the border ring's
    own 99th-percentile distance to the fitted surface is 9-12 across the hard
    cases, so a tolerance of 26 is still three sigma of real backdrop and no
    longer reaches a neutral black.

    Robust because the figure TOUCHES the border on some captures (the slimes,
    Boreas): a plain least squares would drag the surface toward a green slime
    and then key half the sky as figure. Four rounds of fit-and-reject on the
    residual, keeping the pixels the surface already explains.
    """
    import numpy as np

    h, w = rgb.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    X, Y = (xx / w).astype(np.float64), (yy / h).astype(np.float64)
    basis = np.stack([np.ones_like(X), X, Y, X * X, Y * Y, X * Y], axis=-1)

    k = max(2, int(band * max(h, w)))
    m = np.zeros((h, w), dtype=bool)
    m[:k] = m[-k:] = True
    m[:, :k] = m[:, -k:] = True

    model = None
    for _ in range(4):
        A = basis[m]
        if len(A) < 60:
            break
        model = np.zeros(rgb.shape, dtype=np.float64)
        for c in range(3):
            coef, *_ = np.linalg.lstsq(A, rgb[:, :, c][m].astype(np.float64),
                                       rcond=None)
            model[:, :, c] = basis @ coef
        r = np.sqrt(((rgb - model) ** 2).sum(axis=2))
        keep = m & (r <= max(8.0, float(np.percentile(r[m], 70)) * 2.0))
        if keep.sum() < 60 or keep.sum() == m.sum():
            break
        m = keep
    return model


def _box(a, r, axis):
    """Unnormalised box sum of width 2r+1 along `axis`, edges clamped."""
    import numpy as np
    a = np.moveaxis(a, axis, 0)
    pad = np.concatenate([np.repeat(a[:1], r, axis=0), a,
                          np.repeat(a[-1:], r, axis=0)], axis=0)
    c = np.cumsum(pad, axis=0)
    c = np.concatenate([np.zeros_like(c[:1]), c], axis=0)
    out = (c[2 * r + 1:] - c[:-(2 * r + 1)]) / (2 * r + 1)
    return np.moveaxis(out, 0, axis)


def _refine_model(rgb, model, tolerance):
    """Inpaint the quadratic with the backdrop's own LOCAL colour.

    A quadratic carries the vignette but not the nebula: several captures
    (frostarm_lawachurl, rock_shield_hilichurl_guard) have a lighter cloud
    washed across one corner, and a surface smooth enough to be robust cannot
    follow it -- so the nebula sat 30-40 off the model and came through the cut
    as a navy scarf draped over the body. This second pass takes the pixels the
    quadratic ALREADY explains as certain backdrop, blurs them heavily with a
    weighted (normalised-convolution) blur so the estimate spreads across the
    figure from the sky around it, and keys against that. Where no confident
    backdrop is near, the weight goes to zero and the quadratic stands.
    """
    import numpy as np

    h, w = rgb.shape[:2]
    conf = np.sqrt(((rgb - model) ** 2).sum(axis=2)) <= max(10.0, tolerance * 0.6)
    if conf.mean() < 0.05:
        return model
    radius = max(4, int(0.06 * max(h, w)))

    def _blur(arr):
        # Three box passes ~= a gaussian, and a box pass is two cumsums --
        # PIL's GaussianBlur will not take an "F" image and scipy is not a
        # dependency of this repo.
        a = arr.astype(np.float64)
        for _ in range(3):
            a = _box(_box(a, radius, 0), radius, 1)
        return a

    den = _blur(conf.astype(np.float64))
    out = model.copy()
    good = den > 0.02
    for c in range(3):
        num = _blur(rgb[:, :, c] * conf)
        out[:, :, c] = np.where(good, num / np.maximum(den, 1e-6), model[:, :, c])
    return out


def _blueness(a):
    """How blue a colour is, independent of how bright it is.

    The Archive backdrop is navy: B runs 40-85 while R and G sit near 20, so
    its blueness is +30 to +50. A body's black is NEUTRAL -- R, G and B within
    a few points of each other, blueness near 0 -- even when its luminance is
    the backdrop's. That is the one axis on which "dark body" and "dark sky"
    separate at all, and it is the second half of the key.
    """
    return a[..., 2] - 0.5 * (a[..., 0] + a[..., 1])


def _backdrop_alpha(img, tolerance=CUT_TOLERANCE, pocket_frac=CUT_POCKET_FRAC,
                    chroma=CUT_CHROMA, figure="main", dropped=None,
                    split=CUT_SPLIT):
    """Alpha for an Archive capture: opaque figure, transparent backdrop.

    Five passes, each closing a defect the one before it opens:

    1. KEY against the local backdrop model (`_backdrop_model`), not a flat
       distance from a corner colour, and require the pixel to be as blue as
       the model says the backdrop is there (`_blueness`, within `chroma`).
       Distance alone cannot separate a shaded navy torso from the sky --
       frostarm_lawachurl's belly reads (13,19,64) against a (7,20,63)
       backdrop -- so the chroma gate is what saves neutral blacks, and
       reachability below is what saves the rest.
    2. REACHABILITY from the border, on the key ERODED by CUT_BRIDGE first.
       Eroding is the fix for the leak that ate the bodies: a two-pixel
       hairline of keyed colour between an arm and the frame carried the flood
       into the torso and hollowed it out. The reached set is dilated back and
       re-intersected with the key, so the matte keeps its true edge.
    3. ENCLOSED POCKETS -- sky trapped inside the silhouette, which pass 2
       cannot reach by construction (`hilichurl_fighter`'s raised club).
       Removed by area AND by fit: a pocket only goes if it matches the
       backdrop model TIGHTLY (mean residual under CUT_POCKET_RESID of the
       tolerance). Area alone took electro_abyss_mage's EYES with the haze
       inside his shield bubble; a face is dark but it is not the backdrop.
    4. THE STARFIELD -- foreground islands too small to be a body are pruned,
       or the alpha bbox is the whole frame and the content trim is a no-op.
    5. FIGURE SELECTION (`figure=main`, the default) -- Archive GROUP captures
       (the slimes: three bodies) left the flanking figures half in frame once
       cover() fitted the whole bbox. Keep the largest component plus anything
       inside its bbox grown by CUT_FIGURE_MARGIN; drop the rest. `figure=all`
       keeps every component, for a body whose detached parts matter.

    Solved at CUT_WORK_MAX, not at native size. The sources run to 2880x2880
    and the target is 240x280.

    A source that ALREADY carries alpha (`Enemy Ruin Guard.png`, the `NPC`
    portraits) is passed through untouched: re-matting a cut-out would only be
    a second chance to get it wrong.

    `dropped`, if given, is a list the figure pass appends one
    "<area share> at <bbox>" line to per component it removed, so the run can
    print what it threw away instead of losing it in silence.
    """
    import numpy as np

    a = np.asarray(img.getchannel("A"), dtype=np.uint8)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    if (border < 8).mean() >= CUT_BORDER_ALPHA:
        return None                      # already cut out; keep its own matte

    # float64, NOT int16: a squared channel difference reaches 255**2 = 65025,
    # which wraps negative in int16 and hands `sqrt` a negative number.
    rgb = np.asarray(img.convert("RGB"), dtype=np.float64)
    h, w = rgb.shape[:2]
    model = _backdrop_model(rgb, CUT_BORDER_BAND)
    if model is None:                     # frame too small to fit anything
        return None
    model = _refine_model(rgb, model, tolerance)
    resid = np.sqrt(((rgb - model) ** 2).sum(axis=2))
    chroma_deficit = _blueness(model) - _blueness(rgb)
    cand = (resid <= tolerance) & (chroma_deficit <= chroma)

    seeds_xy = ([(0, x) for x in range(w)] + [(h - 1, x) for x in range(w)]
                + [(y, 0) for y in range(h)] + [(y, w - 1) for y in range(h)])
    if CUT_BRIDGE:
        core = _erode(cand, CUT_BRIDGE)
        background = _dilate(_flood(core, seeds_xy), CUT_BRIDGE) & cand
    else:
        background = _flood(cand, seeds_xy)

    if pocket_frac > 0:
        enclosed = cand & ~background
        min_pocket = max(16, int(pocket_frac * h * w))
        for comp in _components(enclosed):
            if int(comp.sum()) < min_pocket:
                continue
            if float(resid[comp].mean()) > tolerance * CUT_POCKET_RESID:
                continue                  # dark, but not the backdrop
            background |= comp

    fg = ~background
    keep = np.zeros_like(fg)
    min_area = max(16, int(CUT_SPECK_FRAC * h * w))
    comps = [c for c in _components(fg) if int(c.sum()) >= min_area]
    for comp in comps:
        keep |= comp
    if not comps:                         # nothing survived: keep the raw matte
        return Image.fromarray(np.where(fg, 255, 0).astype("uint8"), "L")

    if figure == "main":
        # THE UNITS a figure is chosen among. Normally the alpha components
        # themselves -- but `dendro_slime` showed that a flanking body can be
        # JOINED to the subject through a couple of overlapping leaves, which
        # makes the pair one component and puts it out of this pass's reach.
        # `split=N` opens the matte (erode N, dilate N) first, so a bridge
        # thinner than 2N+1 parts while every thick part survives, and the
        # figure is chosen among the THICK regions instead. It is OFF by
        # default because a staff handle, a whip and a leash are thin bridges
        # too, and cutting one of those loses a real feature.
        units = comps
        if split > 0:
            opened = _dilate(_erode(keep, split), split) & keep
            thick = [c for c in _components(opened) if int(c.sum()) >= min_area]
            if len(thick) > 1:
                units = thick
        if len(units) > 1:
            main = _pick_figure(units, h, w)
            mbox = _mask_box(main)
            kept_units, drops = [main], []
            for comp in units:
                if comp is main:
                    continue
                (kept_units if _box_inside(_mask_box(comp), mbox) else
                 drops).append(comp)
            if drops:
                removed = np.zeros_like(keep)
                for comp in drops:
                    removed |= comp
                    if dropped is not None:
                        y0, y1, x0, x1 = _mask_box(comp)
                        dropped.append(f"{int(comp.sum()) / (h * w):.1%} at "
                                       f"({x0},{y0})-({x1},{y1})")
                # Re-grow through what is LEFT, seeded on the units we keep:
                # with the dropped bodies excised, the bridge stub that joined
                # them stays attached to the subject (the subject's own leaf),
                # and with `split=0` this is exactly the old union of kept
                # components, because those are disconnected by construction.
                survivors = keep & ~removed
                seeds = []
                for comp in kept_units:
                    sy, sx = np.nonzero(comp & survivors)
                    seeds.extend(zip(sy.tolist(), sx.tolist()))
                if seeds:
                    keep = _flood(survivors, seeds)
    return Image.fromarray(np.where(keep, 255, 0).astype("uint8"), "L")


def _mask_box(mask):
    """(y0, y1, x0, x1) of a boolean mask's set pixels."""
    import numpy as np
    ys, xs = np.nonzero(mask)
    return int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())


def _box_inside(box, outer, margin=CUT_FIGURE_MARGIN):
    """Is `box` inside `outer` grown by `margin` of its own size?"""
    oy0, oy1, ox0, ox1 = outer
    gy = (oy1 - oy0 + 1) * margin
    gx = (ox1 - ox0 + 1) * margin
    y0, y1, x0, x1 = box
    return (y0 >= oy0 - gy and y1 <= oy1 + gy
            and x0 >= ox0 - gx and x1 <= ox1 + gx)


def _pick_figure(units, h, w):
    """The largest unit, tie-broken toward the frame centre.

    The Archive centres the main body, so when two units are near the same
    size the centred one is the subject and the other is a flanking group
    member.
    """
    import numpy as np
    best = max(units, key=lambda c: int(c.sum()))
    best_area = int(best.sum())
    by, bx = np.nonzero(best)
    best_d = abs(by.mean() - h / 2) + abs(bx.mean() - w / 2)
    for comp in units:
        if comp is best or int(comp.sum()) < best_area * CUT_FIGURE_TIE:
            continue
        cy, cx = np.nonzero(comp)
        d = abs(cy.mean() - h / 2) + abs(cx.mean() - w / 2)
        if d < best_d:
            best, best_d = comp, d
    return best


def _flood(mask, seeds):
    """Breadth-first 4-connected reachable subset of `mask` from `seeds`.

    numpy holds the arrays and python walks the frontier: without scipy there
    is no `ndimage.label` here, and the alternatives (iterated dilation, a
    raster/anti-raster reconstruction) are either O(diameter) passes over the
    whole frame or not expressible as array ops at all. The walk is bounded by
    the REACHABLE area, which is why the matte is solved at CUT_WORK_MAX.
    """
    import numpy as np
    from collections import deque

    h, w = mask.shape
    seen = np.zeros((h, w), dtype=bool)
    q = deque()
    for y, x in seeds:
        if mask[y, x] and not seen[y, x]:
            seen[y, x] = True
            q.append((y, x))
    push = q.append
    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                push((ny, nx))
    return seen


def cut(img, w, h, spec):
    """Matte an opaque Archive capture, trim to the figure, then fit w*h.

    The three steps are deliberately the three existing ones: the matte above,
    `cover_autocrop`'s content trim (via `_alpha_box`, so faint FX at the
    figure's edge are kept rather than clipped), and then `cover()` or
    `contain()` -- the same fitters every other mode uses, with the row's own
    focus. Nothing about framing is re-decided here.
    """
    tolerance, fit, focus, pocket_frac, chroma, figure, split = _cut_spec(spec)
    work = img
    scale = CUT_WORK_MAX / max(img.width, img.height)
    if scale < 1:
        work = img.resize((max(1, round(img.width * scale)),
                           max(1, round(img.height * scale))), Image.LANCZOS)
    dropped = []
    matte = _backdrop_alpha(work, tolerance, pocket_frac, chroma, figure,
                            dropped, split)
    for d in dropped:
        flags.append(f"figure={figure} dropped a component: {d}")
    if matte is not None:
        if CUT_FEATHER:
            matte = matte.filter(ImageFilter.GaussianBlur(CUT_FEATHER))
        work = work.copy()
        work.putalpha(matte)

    box = _alpha_box(work, INCLUDE_THRESH)
    if box is None:
        flags.append(f"cut@{tolerance:g} removed EVERYTHING -- tolerance too high")
        return contain(img, w, h)
    covered = ((box[2] - box[0]) * (box[3] - box[1])) / (work.width * work.height)
    if covered > 0.97:
        flags.append(f"cut@{tolerance:g} removed almost nothing "
                     f"({covered:.0%} of the frame still opaque)")
    work = work.crop(box)
    return cover(work, w, h, focus) if fit == "cover" else contain(work, w, h)


def sprite(img, w, h):
    """Combat/rest-site model sprites: trim to the alpha bbox, fit in W×H, and
    anchor the feet on the bottom edge -- the game positions these textures
    with their bottom at ground level, so bottom padding floats the character.
    """
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    scale = min(w / img.width, h / img.height)
    if scale > UPSCALE_FLAG:
        flags.append(f"upscale x{scale:.1f}")
    img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    # plain paste (no mask): copies pixels alpha included; a mask here would
    # square the alpha of soft edges -- see contain() note.
    canvas.paste(img, ((w - img.width) // 2, h - img.height))
    return canvas


def contain(img, w, h, bg=(0, 0, 0, 0)):
    scale = min(w / img.width, h / img.height)
    if scale > UPSCALE_FLAG:
        flags.append(f"upscale x{scale:.1f}")
    img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), bg)
    # alpha_composite, NOT paste-with-mask: paste blends the alpha channel
    # itself, so soft edges stay semi-transparent even over an opaque bg and
    # render as black fringing in-game (found 2026-07-20 on big_badda_boom).
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay.paste(img, ((w - img.width) // 2, (h - img.height) // 2))
    return Image.alpha_composite(canvas, overlay)


def process(row, dest):
    if row["mode"] == "raw":
        src = RAW / rawname(row["title"])
        if not src.exists():
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        return True
    img = load_source(row)
    if img is None:
        return False
    # TCG cards are full-bleed art inside a printed frame + rounded corners —
    # trim the frame before cropping so borders never show in the portrait.
    if row["title"].endswith("Card.png") or row["title"].endswith("Card Golden.png"):
        dx, dy = round(img.width * 0.065), round(img.height * 0.045)
        img = img.crop((dx, dy, img.width - dx, img.height - dy))
    n0 = len(flags)
    if row["mode"] == "cover":
        out = cover(img, row["w"], row["h"], row["focus"])
    elif row["mode"] == "cover_autocrop":
        out = cover_autocrop(img, row["w"], row["h"], row["focus"])
    elif row["mode"] == "cut":
        out = cut(img, row["w"], row["h"], row["focus"])
    elif row["mode"] == "sprite":
        out = sprite(img, row["w"], row["h"])
    else:
        # Card portraits get the flat backing; icons keep transparency.
        bg = CARD_BG if "/cards/" in row["out"] else (0, 0, 0, 0)
        out = contain(img, row["w"], row["h"], bg)
    # Card portraits must be opaque regardless of mode: several official
    # splashes (e.g. Klee Wish) ship on transparency, and alpha holes read as
    # missing art over the card frame. alpha_composite (not paste) so edge
    # pixels come out fully opaque -- see contain() note.
    if "/cards/" in row["out"]:
        out = Image.alpha_composite(Image.new("RGBA", out.size, CARD_BG), out)
        # ...and so they are written WITHOUT an alpha channel (`EB-158`). The
        # composite above sets every pixel to alpha=255, so the alpha band that
        # was still being saved was a constant plane -- a quarter of the raw
        # pixel data paying for information the line above had just destroyed,
        # across 887 planned card rows. Pillow's RGBA->RGB copies R, G and B
        # and drops the band; it does not premultiply or otherwise touch a
        # colour value, so the portrait is byte-for-byte the same picture.
        # Icons and every non-card surface stay RGBA: their alpha is real.
        out = out.convert("RGB")
    for i in range(n0, len(flags)):
        flags[i] = f"{row['asset_id']} r{row['rank']}: {flags[i]}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest)
    return True


def apply_picks(rows, picks_path):
    picks = {}
    for line in Path(picks_path).read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            aid, rank = line.split("\t")[:2]
            picks[aid] = int(rank)
    n = 0
    for r in rows:
        if r["pick"] == "shortlist" and picks.get(r["asset_id"]) == r["rank"]:
            src = CAND / r["asset_id"] / f"r{r['rank']}.png"
            dest = ART_OUT / r["out"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
            print(f"pick applied: {r['asset_id']} <- r{r['rank']}")
            n += 1
    print(f"{n} picks promoted")


def update_manifest(status_by_asset):
    if not MANIFEST.exists():
        return
    lines = MANIFEST.read_text(encoding="utf-8").splitlines()
    out = [lines[0]]
    for line in lines[1:]:
        cells = next(csv.reader([line]))
        # manifest ids are card_<id> / power_<id> / bare ui ids
        aid = cells[0]
        hit = status_by_asset.get(aid) or status_by_asset.get(aid.removeprefix("card_"))
        if hit:
            cells[3] = "F"          # tier
            cells[4] = hit[0]       # status: found | candidate
            cells[5] = hit[1]       # source wiki title (rank 1)
        buf = []
        w = csv.writer(_ListWriter(buf))
        w.writerow(cells)
        out.append(buf[0].rstrip("\r\n"))
    MANIFEST.write_text("\n".join(out) + "\n", encoding="utf-8")


class _ListWriter:
    def __init__(self, buf):
        self.buf = buf

    def write(self, s):
        self.buf.append(s)


def _take(argv, flag):
    """Pull `--flag VALUE` out of argv and return VALUE (or None).

    Hand-rolled rather than argparse so `--apply-picks` keeps its exact
    positional spelling; the point of both flags below is that they can be
    added without moving the shipped invocation.
    """
    if flag not in argv:
        return None
    i = argv.index(flag)
    if i + 1 >= len(argv):
        sys.exit(f"{flag} needs a value")
    value = argv[i + 1]
    del argv[i:i + 2]
    return value


def main():
    global RAW, CAND, MANIFEST, ART_OUT
    argv = sys.argv[1:]

    # --art-root: read the pixels from ANOTHER checkout. `art/raw/` and
    # `art/candidates/` are gitignored Tier F and exist only on the art-bearing
    # main checkout, and operations/worktrees.md forbids linking them into a
    # worktree -- `git worktree remove` follows a junction and deletes what it
    # finds, which has destroyed non-regenerable files. So a worktree points at
    # the main checkout by ABSOLUTE path instead. Only the art/ tree moves;
    # `art/plan.tsv` still comes from THIS checkout, which is the point -- the
    # branch's plan rendered against the main checkout's pixels.
    art_root = _take(argv, "--art-root")
    if art_root:
        art_root = Path(art_root).resolve()
        RAW = art_root / "art" / "raw"
        CAND = art_root / "art" / "candidates"
        MANIFEST = art_root / "art" / "manifest.csv"
        ART_OUT = art_root

    # --assets: render ONLY these asset ids' shortlist candidates. Nothing is
    # PLACED and the manifest is NOT touched -- a gate review renders crops to
    # LOOK at, and must never quietly promote an unreviewed rank 1 into the
    # shipping tree. Same spelling and same reason as art_contact_sheet's
    # `--assets`: a gate is not a batch.
    only = _take(argv, "--assets")
    only = {a.strip() for a in only.split(",") if a.strip()} if only else None

    rows = read_plan()
    # Taste-pass directive 3: the plan must lint clean before any pixels move.
    from art_lint import lint
    problems = lint(rows)
    if problems:
        for p in problems:
            print("LINT: " + p, file=sys.stderr)
        sys.exit(1)
    if len(argv) > 1 and argv[0] == "--apply-picks":
        apply_picks(rows, argv[1])
        return

    if only is not None:
        for missing in sorted(only - {r["asset_id"] for r in rows}):
            print(f"NOTE: '{missing}' has no plan row -- not rendered, "
                  f"not silently dropped")
        done, gaps = 0, []
        for r in rows:
            if r["asset_id"] not in only or r["pick"] != "shortlist":
                continue
            if process(r, CAND / r["asset_id"] / f"r{r['rank']}.png"):
                done += 1
            else:
                gaps.append(f"{r['asset_id']} r{r['rank']} ({r['title']})")
        print(f"{done} candidate crop(s) written under {CAND}; "
              f"nothing placed, manifest untouched")
        for g in gaps:
            print("  GAP: " + g)
        for f in flags:
            print("  FLAG: " + f)
        return

    done, gaps, status = 0, [], {}
    for r in rows:
        if r["pick"] == "shortlist":
            ok = process(r, CAND / r["asset_id"] / f"r{r['rank']}.png")
            if ok and r["rank"] == 1:
                process(r, ART_OUT / r["out"])  # provisional pick
                status[r["asset_id"]] = ("candidate", r["title"])
        else:
            ok = process(r, ART_OUT / r["out"])
            if ok:
                status[r["asset_id"]] = ("found", r["title"])
        if ok:
            done += 1
        else:
            gaps.append(f"{r['asset_id']} r{r['rank']} ({r['title']})")

    # derived: locked select portrait -- one per character. The roster put
    # Furina's portrait at ImageGen/images/furina/ui/; Klee's historical layout
    # is ImageGen/images/ui/. Derive the locked variant next to EVERY
    # select_portrait a plan row produced, not just Klee's hardcoded path.
    sp_outs = {
        (ART_OUT / r["out"]) for r in rows
        if Path(r["out"]).name == "select_portrait.png"
    }
    for sp in sorted(sp_outs):
        if not sp.exists():
            continue
        img = Image.open(sp).convert("RGBA")
        locked = ImageEnhance.Brightness(ImageEnhance.Color(img).enhance(0.15)).enhance(0.55)
        locked.save(sp.parent / "select_portrait_locked.png")
        key = "select_portrait_locked" if sp.parent == ROOT / "ImageGen/images/ui" \
            else f"{sp.parent.parent.name}_select_portrait_locked"
        status[key] = ("found", f"derived: {sp.parent.name}/select_portrait desaturated")

    update_manifest(status)
    print(f"{done}/{len(rows)} plan rows processed; {len(status)} assets placed")
    if flags:
        print("\nFLAGS (check by eye / consider reframe):")
        for f in flags:
            print("  " + f)
    if gaps:
        print("\nGAPS (Tier P frame stays in place):")
        for g in gaps:
            print("  " + g)


if __name__ == "__main__":
    main()
