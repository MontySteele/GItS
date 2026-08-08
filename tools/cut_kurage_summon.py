"""Cut the Bake-Kurage out of the summon art as a field entity sprite.

EB-53/N1, the attribution pass (2026-08-08). Produces the gitignored art:

    ImageGen/images/kokomi/summon/bake_kurage.png
    ImageGen/images/kokomi/summon/kurage.json   (sprite size, shipped 2x)

from art/raw/Bake-Kurage_Summon.png (420x720).

WHY THIS SOURCE. It is the one the register names -- EB-53 says "art exists:
`Bake-Kurage Summon` 420x720" -- and it is the only asset in which the
jellyfish is a full-body render rather than a talent sigil or a 480x270
gameplay preview. It is already fetched (art/SOURCES.tsv rows for
before_sun_and_moon/r1 and grand_conscription/r2 point at the same URL), so
this generator adds no fetch.

WHY HAND POLYGON, following tools/cut_salon_members.py verbatim. That file's
argument was that the silhouette IS the deliverable, so it is drawn rather
than inferred. The same holds here and more so: this sprite renders at ~36px
in a docket slot, where the only thing that survives is outline. A luminance
key would also have worked on this darker card, and that is exactly why it was
not used -- a second, different matting method in the same repo is a second
thing to maintain and a second thing to be surprised by.

WHAT IS CUT, and what is dropped. The polygon follows the bell and the dense
tentacle skirt below it. The wide translucent side-wings that sweep out to the
card edges are OUTSIDE it: they are soft, they are half background, and a
polygon generous enough to hold them would enclose more dark card than
jellyfish, which is the failure the salon cut recorded for Crabaletta's shell.
Bell plus skirt is an unmistakable jellyfish at glance distance, which is the
acceptance question.

Coordinates are specific to this artwork revision (URL in art/SOURCES.tsv).

Usage: .venv/Scripts/python tools/cut_kurage_summon.py [--check]
"""
from pathlib import Path
import argparse
import json
import sys

from PIL import Image, ImageDraw, ImageFilter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "art" / "raw" / "Bake-Kurage_Summon.png"
OUT = ROOT / "ImageGen" / "images" / "kokomi" / "summon"

# Cut once and fitted at runtime by TurnEndPreviewBridge -- the amendment
# SalonVisualsBridge already made to the pre-scaled-art house rule, for the
# same reason (the slot pitch is computed, so there is no single size the art
# could be cut at). 128 is 2x the largest slot the docket can give it.
TARGET_H = 128

# Hand-digitised silhouette, source px, clockwise from the top of the bell.
KURAGE = [
    (228, 114), (258, 120), (282, 134), (299, 157), (309, 186), (311, 215),
    (304, 238), (293, 251), (290, 268), (292, 300), (286, 332), (276, 362),
    (264, 392), (250, 416), (236, 432), (222, 416), (210, 392), (198, 362),
    (190, 332), (186, 300), (188, 268), (185, 251),
    (170, 235), (159, 213), (157, 186), (166, 157), (180, 134), (202, 120),
]


def cut_one(src, poly, feather=1.0):
    """Mask src by poly, trim to content, return RGBA image."""
    w, h = src.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    if feather:
        mask = mask.filter(ImageFilter.GaussianBlur(feather))
    out = src.copy()
    out.putalpha(mask)
    return out.crop(out.getbbox())


def build(out_dir):
    src = Image.open(SRC).convert("RGBA")
    out_dir.mkdir(parents=True, exist_ok=True)
    sprite = cut_one(src, KURAGE)
    scale = TARGET_H / sprite.height
    sprite = sprite.resize(
        (max(1, round(sprite.width * scale)), TARGET_H), Image.LANCZOS)
    path = out_dir / "bake_kurage.png"
    sprite.save(path)
    meta = {"file": path.name, "w": sprite.width, "h": sprite.height}
    opaque = (np.asarray(sprite)[..., 3] > 128).mean()
    print(f"  bake_kurage  {sprite.width:3d}x{sprite.height:3d}  "
          f"fill {opaque * 100:.0f}%")
    (out_dir / "kurage.json").write_text(
        json.dumps({"target_h": TARGET_H, "sprite": meta}, indent=2),
        encoding="utf-8")
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="rebuild to a temp dir and diff against shipped art")
    args = ap.parse_args()

    if not SRC.exists():
        raise SystemExit(f"source missing: {SRC}")

    if args.check:
        import filecmp
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            build(tmp)
            bad = []
            for produced in sorted(tmp.iterdir()):
                shipped = OUT / produced.name
                if not shipped.exists():
                    bad.append(f"MISSING on disk: {produced.name}")
                elif not filecmp.cmp(produced, shipped, shallow=False):
                    bad.append(f"DIFFERS: {produced.name}")
            for line in bad:
                print("  " + line)
            print("byte-identical" if not bad else f"{len(bad)} mismatch(es)")
            return 1 if bad else 0

    print(f"{SRC.relative_to(ROOT)} -> {OUT.relative_to(ROOT)}")
    build(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
