#!/usr/bin/env python3
"""Generate map markers in the base game's pin look, from the model-rendered select close-up.

The ONE producer of `ui/map_marker.png` for all five kits (2026-10-19). Klee's
was the wiki side icon (Klee visual paper, pick 3 (a): "the map marker is
refit to its box"; it filled only the lower two-thirds of its box and read
about 0.7 the size of the others); Yae borrowed Klee's through build_pck's
Copy-YaeFallback; Furina's, Kokomi's and Varka's were square crops of official
art from their stills scripts. [USER], 2026-10-19, on the Klee and Yae pins:
"I think all 5 should get pins."

THE SLOT (SlayTheSpire2.pck, read 2026-10-19). The base markers
(`images/packed/map/icons/map_marker_<char>.png`) are 49x64 RGBA: one flat
symbol in the character's colour (Ironclad's red chevron, Defect's cyan
orb-and-point, Necrobinder's pink ribbon), pointing DOWN at the map node,
with a 2-3 px halo of black at alpha 0.5 round the whole silhouette and no
background. `NMapMarker` (and the co-op reaction wheel) draw the texture as
is.

THE PIN. Defect's shape, which reads as a pin: a disc on top and a point
below, filled with the character's map colour (`CharacterModel.MapDrawingColor`,
lit from above), a 2.5 px ring of it round the face, the point reaching
row TIP_Y, and the base halo outside everything. Inside the disc is the
character's face, cut from the same model-rendered select close-up and
landmarks `tools/gen_char_icons.py` frames the top-bar icon from (one
measurement per render: a re-rendered close-up fails there and here alike).

Drawn at SS times the size and reduced with LANCZOS, so every edge is
antialiased. Deterministic: same close-up in, same bytes out.

Usage:
    .venv/Scripts/python tools/gen_map_markers.py [--chars klee,varka,furina,kokomi,yae] [--art-root <checkout>]
        [--out-root <dir>] [--check]

`--art-root` reads the close-ups under another checkout's ImageGen/ (a worktree
reaching the main checkout's gitignored art); `--out-root` writes (or checks)
under another root, default the art root. A character whose close-up is absent
is SKIPPED (exit 0), as every Tier F generator is on a runner.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_char_icons as GI  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

W, H = 49, 64
SS = 8
#: the disc (the face window plus its ring) and the point's tip, canvas px
DISC_CX, DISC_CY, DISC_R = 24.5, 22.5, 19.5
RING = 2.5
TIP_Y = 60.5
#: the base halo: black at this alpha, this many px round the silhouette
HALO_PX, HALO_ALPHA = 2.5, 128
#: crown-to-chin span of the face in the window, and the crown's row
HEAD_PX, CROWN_AT = 24.0, 9.0


@dataclass(frozen=True)
class Marker:
    icon: str          # the gen_char_icons.CHARS row whose source and landmarks it uses
    out: str           # relative to the out root
    color: str         # the pin's colour, hex (each kit's own; five distinct hues)
    spec: GI.Icon | None = None   # landmarks of its own, where the icon's source is not the close-up


#: Klee's and Yae's colours are their MapDrawingColor; Furina, Kokomi and Varka
#: share a cyan family there, so their pins take a hue of their own each:
#: Varka Anemo teal, Furina deep Hydro blue, Kokomi coral (her frame tint).
CHARS = {
    "klee": Marker(icon="klee", out="ImageGen/images/ui/map_marker.png", color="C4472F"),
    "varka": Marker(icon="varka", out="ImageGen/images/varka/ui/map_marker.png", color="2FA58A"),
    "furina": Marker(icon="furina", out="ImageGen/images/furina/ui/map_marker.png", color="3A63C8"),
    # her top-bar icon is cut from her official splash; the pin uses her
    # model close-up (crown under the bun, eyes at x 1317 and 1432, chin 451)
    "kokomi": Marker(icon="kokomi", out="ImageGen/images/kokomi/ui/map_marker.png", color="E8848F",
                     spec=GI.Icon(source="ImageGen/images/kokomi/ui/select_closeup.png",
                                  out="ImageGen/images/kokomi/ui/map_marker.png",
                                  source_size=(1920, 1080), source_bbox=(1056, 36, 1890, 1080),
                                  face_cx=1372, crown_y=112, chin_y=451)),
    "yae": Marker(icon="yae", out="ImageGen/images/yae/ui/map_marker.png", color="B07FE0"),
}


def _grid():
    ys, xs = np.mgrid[0:H * SS, 0:W * SS]
    return (xs + 0.5) / SS, (ys + 0.5) / SS


def pin_mask() -> np.ndarray:
    """The pin's coverage at SS: the disc plus the point (the triangle from
    the disc's two tangent points to the tip)."""
    x, y = _grid()
    disc = (x - DISC_CX) ** 2 + (y - DISC_CY) ** 2 <= DISC_R ** 2
    d = TIP_Y - DISC_CY
    t = np.arcsin(DISC_R / d)                      # half-angle at the tip
    # inside the cone, between the tangent points' row and the tip
    dx, dy = np.abs(x - DISC_CX), TIP_Y - y
    cone = (dy >= 0) & (dx <= dy * np.tan(t)) & (y >= DISC_CY + DISC_R ** 2 / d)
    return disc | cone


def _dilate(m: np.ndarray, r: int) -> np.ndarray:
    out = m.copy()
    h, w = m.shape
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy > r * r:
                continue
            src = m[max(0, -dy):h - max(0, dy), max(0, -dx):w - max(0, dx)]
            out[max(0, dy):max(0, dy) + src.shape[0], max(0, dx):max(0, dx) + src.shape[1]] |= src
    return out


def _face(src: Image.Image, spec: GI.Icon) -> Image.Image:
    """The face, scaled so crown-to-chin is HEAD_PX, the crown at CROWN_AT
    and the face centre on the disc's centre line, at SS."""
    scale = HEAD_PX / (spec.chin_y - spec.crown_y)          # canvas px per source px
    x0 = spec.face_cx - DISC_CX / scale
    y0 = spec.crown_y - CROWN_AT / scale
    pad = int(max(W, H) / scale) + 2
    padded = Image.new("RGBA", (src.width + 2 * pad, src.height + 2 * pad))
    padded.paste(src, (pad, pad))
    box = (x0 + pad, y0 + pad, x0 + pad + W / scale, y0 + pad + H / scale)
    return padded.resize((W * SS, H * SS), Image.LANCZOS, box=box)


def build_marker(src: Image.Image, spec: GI.Icon, color: str) -> Image.Image:
    rgb = np.array([int(color[i:i + 2], 16) for i in (0, 2, 4)], np.float64)
    x, y = _grid()
    pin = pin_mask()
    halo = _dilate(pin, round(HALO_PX * SS)) & ~pin
    # the pin's fill: the map colour lit from above (x1.2 at the top, x0.7 at the tip)
    lit = 1.2 - 0.5 * np.clip((y - (DISC_CY - DISC_R)) / (TIP_Y - DISC_CY + DISC_R), 0, 1)
    fill = np.clip(rgb[None, None, :] * lit[..., None], 0, 255)
    out = np.zeros((H * SS, W * SS, 4), np.float64)
    out[halo] = (0, 0, 0, HALO_ALPHA)
    out[pin, :3] = fill[pin]
    out[pin, 3] = 255
    # the face window: the disc less the ring, a dark ground under the face
    window = (x - DISC_CX) ** 2 + (y - DISC_CY) ** 2 <= (DISC_R - RING) ** 2
    out[window, :3] = rgb * 0.35
    face = np.asarray(_face(src.convert("RGBA"), spec), np.float64)
    fa = face[..., 3:4] / 255 * window[..., None]
    out[..., :3] = out[..., :3] * (1 - fa) + face[..., :3] * fa
    img = Image.fromarray(np.round(out).astype(np.uint8), "RGBA")
    small = img.resize((W, H), Image.LANCZOS)
    a = np.asarray(small).copy()
    a[a[..., 3] == 0, :3] = 0
    return Image.fromarray(a, "RGBA")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--chars", default=",".join(CHARS))
    ap.add_argument("--art-root", type=Path, default=ROOT)
    ap.add_argument("--out-root", type=Path, default=None)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    art_root = args.art_root.resolve()
    out_root = (args.out_root or args.art_root).resolve()
    names = [n.strip() for n in args.chars.split(",") if n.strip()]
    unknown = [n for n in names if n not in CHARS]
    if unknown:
        print(f"unknown character(s): {', '.join(unknown)}; known: {', '.join(CHARS)}", file=sys.stderr)
        return 2
    problems = []
    for name in names:
        m = CHARS[name]
        spec = m.spec or GI.CHARS[m.icon]
        src_path = art_root / spec.source
        if not src_path.exists():
            print(f"SKIPPED: {name} -- no source at {spec.source}")
            continue
        src = Image.open(src_path).convert("RGBA")
        if src.size != spec.source_size or GI.alpha_bbox(src) != spec.source_bbox:
            problems.append(f"{name}: {spec.source} was re-rendered; re-measure its gen_char_icons.py row")
            continue
        img = build_marker(src, spec, m.color)
        path = out_root / m.out
        if args.check:
            if not path.exists():
                problems.append(f"{m.out} does not exist")
            elif Image.open(path).convert("RGBA").tobytes() != img.tobytes():
                problems.append(f"{m.out} differs from a fresh derivation")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path)
        print(f"wrote {path} ({W}x{H})  [{name}]")
    for p in problems:
        print("STALE: " + p, file=sys.stderr)
    if problems:
        return 1
    if args.check:
        print("gen_map_markers --check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
