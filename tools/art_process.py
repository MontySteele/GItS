#!/usr/bin/env python3
"""Process art/raw/ into ImageGen targets per art/plan.tsv (spec §2 step 3).

- cover: scale to fill W×H, crop (focus=top keeps the top of the frame — right
  for TCG card art and full-body renders; center otherwise)
- contain: fit inside W×H, pad to exact size on transparency (icons)
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
flags = []


def load_source(row):
    """Return an RGBA PIL image for the plan row, or None if raw file missing."""
    p = RAW / rawname(row["title"])
    if row["source"] == "svg":
        if p.exists():
            png = render_svg(p, max(row["w"], row["h"]))
            if png is not None:
                return png
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
        r = subprocess.run(
            ["qlmanage", "-t", "-s", str(max(size, 256)), "-o", td, str(path)],
            capture_output=True)
        outs = list(Path(td).glob("*.png"))
        if r.returncode == 0 and outs:
            return Image.open(outs[0]).convert("RGBA")
    return None


def cover(img, w, h, focus):
    scale = max(w / img.width, h / img.height)
    if scale > UPSCALE_FLAG:
        flags.append(f"upscale x{scale:.1f}")
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    x = (img.width - w) // 2
    y = 0 if focus == "top" else (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def contain(img, w, h):
    scale = min(w / img.width, h / img.height)
    if scale > UPSCALE_FLAG:
        flags.append(f"upscale x{scale:.1f}")
    img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(img, ((w - img.width) // 2, (h - img.height) // 2), img)
    return canvas


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
    out = cover(img, row["w"], row["h"], row["focus"]) if row["mode"] == "cover" \
        else contain(img, row["w"], row["h"])
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
