#!/usr/bin/env python3
"""Process art/raw/ into ImageGen targets per art/plan.tsv (spec §2 step 3).

- cover: scale to fill W×H, crop (focus=top keeps the top of the frame — right
  for TCG card art and full-body renders; center otherwise). focus may instead
  be a fractional anchor `x<f>`, `y<f>` or `x<f>,y<f>` naming where in the
  SOURCE the crop should centre — see cover() for why top/center is not enough.
- contain: fit inside W×H, pad to exact size on transparency (icons)
- cover_autocrop: crop to the art's content first (splash/Wish sources float
  the figure in a large transparent void), then fit — focus carries
  `cover|contain[@margin]`, default cover@0.06
- cut: REMOVE an opaque backdrop, then trim + fit. For the Enemy Archive
  captures behind the Teyvat still portraits (docs/current/research/
  teyvat-portrait-sources-2026-09-16.md): every one is a `truecolour` screen
  capture of the in-game Archive page, and media.md §3 requires alpha because
  a still portrait composites over the arena. focus carries
  `cut[@tolerance][/fit-focus]`, default `cut@48/top`.
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


def cover(img, w, h, focus):
    """Scale to fill w*h and crop.

    focus is `top`, `center`, or a fractional anchor `x<f>[,y<f>]` naming the
    point in the SOURCE the crop centres on. Either may carry `@zoom`.

    The anchor exists because top/center cannot express the common case
    (2026-07-23 taste pass): official portrait art puts the face ~25-33% down
    and parks the GENSHIN IMPACT / HOYOVERSE wordmarks on the top and bottom
    edges. `center` cropped 500x380 out of the middle and returned a headless
    torso; `top` would have returned the wordmark. `y0.28` returns the face.
    """
    # focus "center@1.5" punches the crop 1.5x into the frame (taste-pass
    # directive 2: VFX gif frames want the blast, not the whole battlefield).
    zoom = 1.0
    if "@" in focus:
        focus, z = focus.split("@", 1)
        zoom = float(z)
    scale = max(w / img.width, h / img.height) * zoom
    if scale > UPSCALE_FLAG:
        flags.append(f"upscale x{scale:.1f}")
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
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


CUT_TOLERANCE = 48      # RGB euclidean distance from the seeded backdrop
CUT_WORK_MAX = 900      # the matte is solved at this size, not on a 2880px plate
CUT_FEATHER = 1.2       # gaussian sigma on the matte, in WORK pixels
CUT_BORDER_ALPHA = 0.98  # border already this transparent => honour that alpha
CUT_SPECK_FRAC = 0.0005  # foreground islands below this share of the frame go


def _cut_spec(spec):
    """Parse the `cut` row's focus column: `cut[@tolerance][/fit-focus]`.

    Three things have to ride in one TSV column, so they are separated rather
    than overloaded: `@` is the tolerance (the only knob the matte has) and
    `/` is the focus handed to the FIT afterwards. `cut`, `cut@60`,
    `cut@60/center` and `cut/contain` are all legal; a bare focus keyword
    (`top`) is accepted too, so a row that says nothing about the matte reads
    as "default tolerance, this focus".

    Returns (tolerance, fit, focus) with fit in {cover, contain}.
    """
    spec = (spec or "").strip() or "cut"
    head, _, focus = spec.partition("/")
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
    fit = "cover"
    if focus == "contain":
        fit, focus = "contain", "center"
    return tolerance, fit, focus


def _backdrop_alpha(img, tolerance):
    """Alpha for an Archive capture: opaque figure, transparent backdrop.

    The backdrop is not flat and the naive thresholds both fail on it. It is a
    dark navy vignette with a faint starfield and a reflective floor, so a
    single global colour test keys holes through any dark part of the figure,
    and a plain `getbbox` sees nothing at all because every pixel is opaque.
    What works is the classic matte: seed on the FOUR CORNERS (which are
    backdrop on every capture in the survey -- the Archive centres the body
    with headroom), accept a pixel as backdrop when it is within `tolerance`
    of a corner colour, and then keep only the part of that set REACHABLE FROM
    THE BORDER. The reachability pass is what stops a dark navy belly or a
    shadowed flank from being punched out: it is the same colour as the
    backdrop but it is not connected to it.

    Solved at CUT_WORK_MAX, not at native size. The sources run to 2880x2880
    and the target is 240x280, so a full-resolution flood fill would spend
    8.3M pixels of Python to decide sub-pixel detail that the LANCZOS
    downscale then averages away.

    A source that ALREADY carries alpha (the handful of files a wiki editor
    cut by hand -- `Enemy Ruin Guard.png`, the `NPC` portraits) is passed
    through untouched: re-matting a cut-out would only be a second chance to
    get it wrong.
    """
    import numpy as np

    a = np.asarray(img.getchannel("A"), dtype=np.uint8)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    if (border < 8).mean() >= CUT_BORDER_ALPHA:
        return None                      # already cut out; keep its own matte

    # int32, NOT int16: a squared channel difference reaches 255**2 = 65025,
    # which wraps negative in int16 and hands `sqrt` a negative number. The
    # warning is the symptom; the matte silently keeping a wrapped pixel is
    # the defect.
    rgb = np.asarray(img.convert("RGB"), dtype=np.int32)
    h, w = rgb.shape[:2]
    seeds = np.array([rgb[0, 0], rgb[0, w - 1], rgb[h - 1, 0], rgb[h - 1, w - 1]],
                     dtype=np.int32)
    # distance to the NEAREST corner colour: the vignette darkens toward the
    # bottom, so the top corners and the bottom corners are different colours
    # and one seed alone leaves a band of backdrop opaque.
    d = np.sqrt(((rgb[:, :, None, :] - seeds[None, None, :, :]) ** 2)
                .sum(axis=3).min(axis=2))
    cand = d <= tolerance

    seeds_xy = ([(0, x) for x in range(w)] + [(h - 1, x) for x in range(w)]
                + [(y, 0) for y in range(h)] + [(y, w - 1) for y in range(h)])
    background = _flood(cand, seeds_xy)

    # THE STARFIELD. The Archive backdrop is sprinkled with faint stars, and a
    # star is not backdrop-coloured, so the matte above keeps every one of
    # them -- which leaves the alpha bbox equal to the whole frame and the
    # content trim a no-op (measured: 100% of the frame still "opaque" on four
    # of five samples). So drop foreground islands too small to be a body.
    # The threshold is a fraction of the frame rather than a pixel count
    # because the matte is solved at a fixed working size; at CUT_WORK_MAX it
    # is ~20x20px, well under Boreas's floating ice shards and well over a
    # star.
    fg = ~background
    keep = np.zeros_like(fg)
    min_area = max(16, int(CUT_SPECK_FRAC * h * w))
    ys, xs = np.nonzero(fg)
    todo = np.ones_like(fg)
    for y, x in zip(ys.tolist(), xs.tolist()):
        if not todo[y, x]:
            continue
        comp = _flood(fg & todo, [(y, x)])
        todo &= ~comp
        if int(comp.sum()) >= min_area:
            keep |= comp
    if not keep.any():                    # nothing survived: keep the raw matte
        keep = fg
    return Image.fromarray(np.where(keep, 255, 0).astype("uint8"), "L")


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
    tolerance, fit, focus = _cut_spec(spec)
    work = img
    scale = CUT_WORK_MAX / max(img.width, img.height)
    if scale < 1:
        work = img.resize((max(1, round(img.width * scale)),
                           max(1, round(img.height * scale))), Image.LANCZOS)
    matte = _backdrop_alpha(work, tolerance)
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
