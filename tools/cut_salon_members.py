"""Cut the three Salon members out of the summon art as stage mini-sprites.

Animation sprint 2, Track A3b/D1 (2026-07-24). Produces the gitignored art:

    ImageGen/images/furina/salon/member_{usher,chevalmarin,crabaletta}.png
    ImageGen/images/furina/salon/members.json   (per-sprite size, shipped 2x)

from art/raw/Salon_Members_Summon.png (420x720).

WHY THIS SOURCE. A File:-namespace hunt on the wiki returns no individual
full-body render for any of the three members, and the gameplay preview GIF is
480x270. This card art is the only asset in which the three read as three
DIFFERENT creatures -- top-hatted octopus, ruffed seahorse, big crab -- which
is the entire premise of the D-track redesign. [USER] pick, 2026-07-24.

WHY HAND POLYGONS. Two automatic mattes were tried and both failed: a row-
median background model is contaminated by creature pixels in the lower half
(it keys holes straight through the crab), and a quadratic gradient fitted to
known-background patches still leaves ~72% of the card classified foreground
because the art's lavender lower background and the crab's white shell sit at
the same luminance. The silhouette IS the deliverable here -- D5's acceptance
question is silhouette legibility at glance distance -- so it is drawn by hand
rather than inferred. Polygons follow the true outline including concavities,
so no background survives inside a sprite.

Coordinates are specific to this artwork revision (URL in art/SOURCES.tsv).

Usage: .venv/Scripts/python tools/cut_salon_members.py [--check]
"""
from pathlib import Path
import argparse
import json
import sys

from PIL import Image, ImageDraw, ImageFilter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "art" / "raw" / "Salon_Members_Summon.png"
OUT = ROOT / "ImageGen" / "images" / "furina" / "salon"

# Shipped sprites are pre-scaled (house rule: no runtime minification). The
# stage slots are ~72 px tall in creature space; 2x that gives headroom for the
# deploy pop without resampling artefacts.
TARGET_H = 144

# Hand-digitised silhouettes, source px, clockwise. Each is a closed polygon.
MEMBERS = {
    # Top-hatted octopus, middle left. The full outline is reachable -- he is
    # the only one of the three not clipped by the card frame.
    "usher": [
        (96, 212), (116, 216), (130, 228), (138, 246), (140, 264), (134, 276),
        (146, 282), (150, 296), (144, 310), (152, 318), (166, 330), (170, 344),
        (160, 352), (146, 348), (136, 336), (130, 348), (134, 366), (128, 378),
        (114, 380), (106, 368), (104, 352), (94, 360), (88, 376), (74, 384),
        (60, 378), (58, 362), (66, 348), (52, 350), (36, 344), (28, 330),
        (36, 318), (52, 316), (44, 304), (46, 288), (56, 278), (50, 264),
        (52, 244), (62, 226), (78, 214),
    ],
    # Ruffed seahorse/seal, top right: rounded head with a crest, an ear bump
    # on the left, and two swept fins on the right. Capped at ~y285 where the
    # body runs behind the crab -- head + fins is a complete read on its own.
    "chevalmarin": [
        (238, 70), (258, 76), (272, 92), (282, 110), (296, 104), (316, 108),
        (334, 122), (340, 140), (330, 158), (312, 168), (296, 170), (300, 186),
        (322, 190), (348, 200), (364, 214), (360, 230), (340, 236), (314, 230),
        (292, 218), (280, 232), (272, 252), (262, 272), (246, 284), (228, 282),
        (216, 268), (210, 246), (206, 224), (196, 206), (186, 188), (180, 168),
        (178, 146), (180, 124), (174, 110), (178, 96), (190, 86), (206, 76),
        (222, 70),
    ],
    # The crab -- the one member the card art cannot yield whole. She runs off
    # the frame on BOTH the right and the bottom, and at stage scale the
    # visible remainder is a big pale shell that reads as a featureless blob
    # (tried first; rejected on the D5 criterion). Shipped instead as her
    # raised CLAW, which is unmistakably crustacean and cannot be confused
    # with an octopus or a seahorse at a glance. Flagged in the sprint log:
    # if silhouette parity with the other two matters, she needs better source
    # art, and no such art exists on the wiki today.
    "crabaletta": [
        (128, 352), (156, 346), (180, 354), (196, 372), (204, 396), (210, 422),
        (224, 446), (236, 472), (234, 496), (218, 510), (194, 512), (170, 502),
        (148, 488), (128, 470), (110, 448), (100, 422), (100, 394), (108, 370),
    ],
}


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
    meta = {}
    for name, poly in MEMBERS.items():
        sprite = cut_one(src, poly)
        scale = TARGET_H / sprite.height
        sprite = sprite.resize(
            (max(1, round(sprite.width * scale)), TARGET_H), Image.LANCZOS)
        path = out_dir / f"member_{name}.png"
        sprite.save(path)
        meta[name] = {"file": path.name, "w": sprite.width, "h": sprite.height}
        opaque = (np.asarray(sprite)[..., 3] > 128).mean()
        print(f"  {name:12s} {sprite.width:3d}x{sprite.height:3d}  "
              f"fill {opaque * 100:.0f}%")
    (out_dir / "members.json").write_text(
        json.dumps({"target_h": TARGET_H, "members": meta}, indent=2))
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
