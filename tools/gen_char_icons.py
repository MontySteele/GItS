#!/usr/bin/env python3
"""Generate the top-bar character icons (`ui/char_icon.png`) from select art.

The ONE producer of `char_icon.png` for every character listed in `CHARS`
(Klee, Varka, Kokomi and Furina since 2026-10-13). The outline halo beside
each icon is still derived from it by `gen_char_icon_outlines.py`; run that
after this.

THE SLOT -- measured, not assumed (SlayTheSpire2.pck, read 2026-10-13)
---------------------------------------------------------------------
`scenes/ui/top_bar.tscn` draws the run's character in `TopBarPortrait`, a
54x54 Control centred in a 72x68 `TopBarPortraitTip` over the
`top_bar_char_backdrop` atlas sprite. The base icon scenes
(`scenes/ui/character_icons/<char>_icon.tscn`) are a full-rect TextureRect,
expand_mode 1, stretch_mode 5 (keep aspect, centred), so the texture is
scaled into that 54x54 box whatever its size.

The five base textures (`images/ui/top_panel/character_icon_<char>.png`):

    canvas      85x85 logical (BC7, padded to 88x88 by the importer)
    content     alpha bbox x 4..79, y 3..82 at widest (Ironclad 4..79 x 12..73,
                Silent 4..79 x 10..72, Defect 5..79 x 7..78, Regent 4..79 x
                3..82, Necrobinder 5..79 x 4..80): a free silhouette about
                75px wide, centred, never touching the canvas sides, so the
                outline halo (r ~4.5px, see gen_char_icon_outlines.py) fits.
    subject     each character's own face or head, cut out: Ironclad's
                helmet, Silent's skull mask, Defect's head, and so on. Ours
                are our characters' faces to match.

Our icons were 88x88 square crops whose alpha ran to every edge (Klee x 8..85
y 0..87, Varka 0..87 both ways, Kokomi 0..82 x 0..87), so they drew bigger
than the base cast's, as hard-cornered squares, with the halo clipped flat at
the canvas edge.

THE FRAMING (same for every character)
--------------------------------------
Each icon is an 85x85 canvas holding head plus a little shoulder, cut to a
disc of radius `DISC_R` centred on the canvas, so the content occupies x/y
4..81 like the base silhouettes and the head's own outline (hair, hat) shows
where it stays inside the disc. Each character's source is scaled so its
crown-to-chin span is `HEAD_PX` and placed with the crown at `CROWN_Y` and the
face centre on the canvas centre line. The crown is the top of the head mass
the icon keeps (Klee's hat crown, not its feather; Kokomi's hair, not her bow;
Furina's hair, not the tilted top hat on the side of her head).

The landmarks are hand-measured in SOURCE pixels, so each row also pins the
source's size and alpha bbox: a re-rendered source fails loudly ("re-measure")
instead of silently reframing.

Usage:
    .venv/Scripts/python tools/gen_char_icons.py [--chars klee,varka,kokomi,furina]
        [--art-root <checkout>] [--out-root <dir>] [--check]

`--art-root` reads the sources under another checkout's ImageGen/ (a worktree
reaching the main checkout's gitignored art). `--out-root` writes (or checks)
under another root; it defaults to the art root. A character whose source is
absent is SKIPPED (exit 0), as every Tier F generator is on a runner.

Deterministic: same source in, same bytes out.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

# The base game's top-bar icon canvas (logical size, before BC padding).
CANVAS = 85
# The content disc: centred, leaving the base icons' ~4px margin so the
# outline halo is never clipped by the canvas edge.
DISC_CX = DISC_CY = CANVAS / 2
DISC_R = 38.0
# Head placement on the canvas.
HEAD_PX = 50.0     # crown-to-chin span
CROWN_Y = 7.0      # crown row
# Supersampling for the disc's antialiased edge.
_SS = 8


@dataclass(frozen=True)
class Icon:
    source: str            # relative to the art root
    out: str               # relative to the out root
    source_size: tuple     # (w, h) the landmarks were measured on
    source_bbox: tuple     # alpha bbox (x0, y0, x1, y1), half-open, alpha > 8
    face_cx: float         # face centre column (between the eyes / over the chin)
    crown_y: float         # top of the head mass the icon keeps
    chin_y: float          # chin row


CHARS = {
    # Klee: her model-rendered select close-up (tools/klee_render/pack.py).
    "klee": Icon(
        source="ImageGen/images/ui/select_closeup.png",
        out="ImageGen/images/ui/char_icon.png",
        source_size=(1920, 1080), source_bbox=(883, 36, 1616, 1080),
        face_cx=1270, crown_y=215, chin_y=628),
    # Varka: his model-rendered select close-up (tools/char_render/pack.py),
    # the crossed-arms, smirking render of PR #1238.
    "varka": Icon(
        source="ImageGen/images/varka/ui/select_closeup.png",
        out="ImageGen/images/varka/ui/char_icon.png",
        source_size=(1920, 1080), source_bbox=(905, 37, 1627, 1080),
        face_cx=1250, crown_y=45, chin_y=292),
    # Kokomi: her select splash (tools/gen_kokomi_stills.py); she has no model
    # render yet.
    "kokomi": Icon(
        source="ImageGen/images/kokomi/ui/selection_splash.png",
        out="ImageGen/images/kokomi/ui/char_icon.png",
        source_size=(1920, 1200), source_bbox=(227, 70, 1092, 1118),
        face_cx=626, crown_y=110, chin_y=272),
    # Furina: her model-rendered select close-up (tools/char_render/pack.py,
    # PR #1241). Her top hat sits tilted on the side of her head, so the crown
    # is the top of her HAIR under the brim, not the hat; the hat shows where
    # it stays inside the disc. Face centre is the middle of her 3/4 face
    # (eyes at x 1245 and 1342, chin at 1323).
    "furina": Icon(
        source="ImageGen/images/furina/ui/select_closeup.png",
        out="ImageGen/images/furina/ui/char_icon.png",
        source_size=(1920, 1080), source_bbox=(945, 37, 1834, 1080),
        face_cx=1300, crown_y=260, chin_y=537),
}


def alpha_bbox(im: Image.Image) -> tuple:
    a = np.asarray(im)[..., 3] > 8
    ys, xs = np.nonzero(a)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def disc_mask() -> np.ndarray:
    """Antialiased disc coverage on the canvas, float 0..1."""
    n = CANVAS * _SS
    c = (np.arange(n) + 0.5) / _SS
    d2 = (c[None, :] - DISC_CX) ** 2 + (c[:, None] - DISC_CY) ** 2
    hit = (d2 <= DISC_R * DISC_R).astype(np.float64)
    return hit.reshape(CANVAS, _SS, CANVAS, _SS).mean(axis=(1, 3))


def build_icon(src: Image.Image, spec: Icon) -> Image.Image:
    src = src.convert("RGBA")
    scale = HEAD_PX / (spec.chin_y - spec.crown_y)        # canvas px per source px
    # Canvas (0,0)-(CANVAS,CANVAS) in source coordinates.
    x0 = spec.face_cx - DISC_CX / scale
    y0 = spec.crown_y - CROWN_Y / scale
    side = CANVAS / scale
    # Pad so the box never leaves the source (resize's box must lie inside it).
    pad = int(side) + 2
    padded = Image.new("RGBA", (src.width + 2 * pad, src.height + 2 * pad))
    padded.paste(src, (pad, pad))
    box = (x0 + pad, y0 + pad, x0 + pad + side, y0 + pad + side)
    icon = padded.resize((CANVAS, CANVAS), Image.LANCZOS, box=box)
    a = np.asarray(icon).copy()
    a[..., 3] = np.round(a[..., 3] * disc_mask()).astype(np.uint8)
    a[a[..., 3] == 0, :3] = 0
    return Image.fromarray(a, "RGBA")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--chars", default=",".join(CHARS),
                    help="comma-separated characters (default: all)")
    ap.add_argument("--art-root", type=Path, default=ROOT)
    ap.add_argument("--out-root", type=Path, default=None)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    art_root = args.art_root.resolve()
    out_root = (args.out_root or args.art_root).resolve()

    names = [n.strip() for n in args.chars.split(",") if n.strip()]
    unknown = [n for n in names if n not in CHARS]
    if unknown:
        print(f"unknown character(s): {', '.join(unknown)}; "
              f"known: {', '.join(CHARS)}", file=sys.stderr)
        return 2

    problems, done, skipped = [], 0, 0
    for name in names:
        spec = CHARS[name]
        src_path = art_root / spec.source
        if not src_path.exists():
            print(f"SKIPPED: {name} -- no source at {spec.source}")
            skipped += 1
            continue
        src = Image.open(src_path).convert("RGBA")
        if src.size != spec.source_size or alpha_bbox(src) != spec.source_bbox:
            problems.append(
                f"{name}: {spec.source} is {src.size} with alpha bbox "
                f"{alpha_bbox(src)}, but the landmarks were measured on "
                f"{spec.source_size} / {spec.source_bbox}. The source was "
                "re-rendered: re-measure face_cx / crown_y / chin_y and update "
                "the row.")
            continue
        icon = build_icon(src, spec)
        out_path = out_root / spec.out
        done += 1
        if args.check:
            if not out_path.exists():
                problems.append(f"{spec.out} does not exist")
            elif Image.open(out_path).convert("RGBA").tobytes() != icon.tobytes():
                problems.append(f"{spec.out} differs from a fresh derivation")
            continue
        out_path.parent.mkdir(parents=True, exist_ok=True)
        icon.save(out_path)
        print(f"wrote {out_path} ({CANVAS}x{CANVAS})  [{name}]")

    for p in problems:
        print("STALE: " + p, file=sys.stderr)
    if problems:
        return 1
    if args.check:
        print(f"gen_char_icons --check: OK ({done} derived, {skipped} skipped)")
    else:
        print("now run tools/gen_char_icon_outlines.py for the halos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
