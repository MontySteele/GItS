#!/usr/bin/env python3
"""Process art/raw/ into ImageGen targets per art/plan.tsv (spec §2 step 3).

- cover: scale to fill W×H, crop (focus=top keeps the top of the frame — right
  for TCG card art and full-body renders; center otherwise)
- contain: fit inside W×H, pad to exact size on transparency (icons)
- cover_autocrop: crop to the art's content first (splash/Wish sources float
  the figure in a large transparent void), then fit — focus carries
  `cover|contain[@margin]`, default cover@0.06
- raw: byte-for-byte copy (combat-model source art)
- gif sources: extract the frame at frame_pct% through the clip
- svg sources: render via macOS qlmanage; fall back to the wiki's same-name PNG
  (upscaled — flagged if the upscale factor is ugly)

auto rows  -> final target path.
shortlist  -> art/candidates/<asset_id>/r<rank>.png at target dims,
              plus rank 1 ALSO written to the final target as the provisional
              pick (art never blocks the build; overridden by --apply-picks).
--apply-picks art/picks.tsv  (asset_id<TAB>rank per line) promotes selections.

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

from PIL import Image, ImageEnhance, ImageSequence

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "art" / "raw"
CAND = ROOT / "art" / "candidates"
MANIFEST = ROOT / "art" / "manifest.csv"

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


def cover(img, w, h, focus):
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
    x = (img.width - w) // 2
    y = 0 if focus == "top" else (img.height - h) // 2
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
    for i in range(n0, len(flags)):
        flags[i] = f"{row['asset_id']} r{row['rank']}: {flags[i]}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest)
    return True


def apply_picks(rows, picks_path):
    picks = {}
    for line in Path(picks_path).read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            aid, rank = line.split("\t")[:2]
            picks[aid] = int(rank)
    n = 0
    for r in rows:
        if r["pick"] == "shortlist" and picks.get(r["asset_id"]) == r["rank"]:
            src = CAND / r["asset_id"] / f"r{r['rank']}.png"
            dest = ROOT / r["out"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
            print(f"pick applied: {r['asset_id']} <- r{r['rank']}")
            n += 1
    print(f"{n} picks promoted")


def update_manifest(status_by_asset):
    if not MANIFEST.exists():
        return
    lines = MANIFEST.read_text().splitlines()
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
    MANIFEST.write_text("\n".join(out) + "\n")


class _ListWriter:
    def __init__(self, buf):
        self.buf = buf

    def write(self, s):
        self.buf.append(s)


def main():
    rows = read_plan()
    # Taste-pass directive 3: the plan must lint clean before any pixels move.
    from art_lint import lint
    problems = lint(rows)
    if problems:
        for p in problems:
            print("LINT: " + p, file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) > 2 and sys.argv[1] == "--apply-picks":
        apply_picks(rows, sys.argv[2])
        return

    done, gaps, status = 0, [], {}
    for r in rows:
        if r["pick"] == "shortlist":
            ok = process(r, CAND / r["asset_id"] / f"r{r['rank']}.png")
            if ok and r["rank"] == 1:
                process(r, ROOT / r["out"])  # provisional pick
                status[r["asset_id"]] = ("candidate", r["title"])
        else:
            ok = process(r, ROOT / r["out"])
            if ok:
                status[r["asset_id"]] = ("found", r["title"])
        if ok:
            done += 1
        else:
            gaps.append(f"{r['asset_id']} r{r['rank']} ({r['title']})")

    # derived: locked select portrait
    sp = ROOT / "ImageGen/images/ui/select_portrait.png"
    if sp.exists():
        img = Image.open(sp).convert("RGBA")
        locked = ImageEnhance.Brightness(ImageEnhance.Color(img).enhance(0.15)).enhance(0.55)
        locked.save(sp.parent / "select_portrait_locked.png")
        status["select_portrait_locked"] = ("found", "derived: select_portrait desaturated")

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
