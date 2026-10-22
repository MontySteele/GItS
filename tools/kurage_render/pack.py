"""Outline and pack the Bake-Kurage's rendered clips into one frame sheet.

    python tools/kurage_render/pack.py --renders <render.py --out dir> [--art-root <dir>] [--check]

Reads render.py's raw frames and writes

  <art-root>/ImageGen/images/kokomi/model/frames/kokomi_kurage.png
      every frame of every clip, each trimmed to its own texels and
      shelf-packed (tools/char_render/pack.py's sheets_for), in clip order;

and the committed manifest tools/kurage_render/kurage_frames.json (the one
cell and origin all four clips share, per frame its rect and offset, per clip
its frame range, fps and times -- no pixels), which tools/kokomi_rig turns
into klee-mod/pck-src/kokomi/model/bake_kurage.tscn. build_pck.ps1 copies the
sheet with a VRAM-compressed import, as every file under kokomi/model/frames.

THE GLOW is drawn here, in 2D, under the frame: its alpha weighted by
brightness and blurred by clips.GLOW_PX in clips.COLORS["glow"], a soft
bloom (2026-10-22; it replaced a dark navy outline that made the jellyfish
read as a solid toy). The glow is feathered to nothing at the edge of the box
the old outline reached (the silhouette grown by clips.OUTLINE_PX), so the
cell and the origin do not move.

From a worktree, --art-root is a scratch art root; copy the sheet into the
main checkout's ImageGen once reviewed (docs/current/operations/art.md).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


C = _load(HERE / "clips.py", "kurage_clips")
CP = _load(ROOT / "tools" / "char_render" / "pack.py", "char_render_pack")

SHEET_FILE = "kokomi_kurage.png"
MANIFEST = HERE / "kurage_frames.json"
#: the scene draws the 2x texture at this scale (every kit's combat frames)
SCALE = 0.5
TEXTURE_IMPORT = "vram_compressed"
#: the alpha a texel needs to count as silhouette for the outline: the
#: tentacles' faded tips stay soft rather than drawing a line round a ghost
OUTLINE_ALPHA = 110


def footprint(im: Image.Image) -> Image.Image:
    """The frame's reach as the old outlined sheet had it: the silhouette
    (alpha >= OUTLINE_ALPHA, opened) grown by OUTLINE_PX, plus every visible
    texel. The glow is kept inside the union of these boxes, so the cell and
    origin stay the old outline's."""
    a = np.asarray(im.getchannel("A"))
    mask = Image.fromarray(((a >= OUTLINE_ALPHA) * 255).astype(np.uint8), "L")
    mask = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    grow = int(round(C.OUTLINE_PX))
    out = np.maximum(np.asarray(mask.filter(ImageFilter.MaxFilter(2 * grow + 1))), a)
    return Image.fromarray(out.astype(np.uint8), "L")


#: the halo's strength and the feather (texture px) that fades it to nothing
#: at the edge of the frames' box
GLOW_ALPHA = 0.62
GLOW_FEATHER = 10


def glowing(im: Image.Image, box) -> Image.Image:
    """A soft bloom under the frame: its alpha, weighted by brightness,
    blurred by GLOW_PX in COLORS["glow"] -- light in water, where the old
    sheet drew a dark line. Feathered to zero at `box`'s edges."""
    px = np.asarray(im, dtype=np.float32) / 255.0
    src = px[..., 3] * (0.35 + 0.65 * px[..., :3].max(axis=2))
    halo = np.asarray(Image.fromarray((src * 255).astype(np.uint8), "L")
                      .filter(ImageFilter.GaussianBlur(C.GLOW_PX)), dtype=np.float32) / 255.0
    halo = np.clip(halo * 1.8, 0, 1) * GLOW_ALPHA
    h, w = halo.shape
    x0, y0, x1, y1 = box
    xs = np.clip(np.minimum(np.arange(w) - x0, x1 - 1 - np.arange(w)) / GLOW_FEATHER, 0, 1)
    ys = np.clip(np.minimum(np.arange(h) - y0, y1 - 1 - np.arange(h)) / GLOW_FEATHER, 0, 1)
    halo *= ys[:, None] * xs[None, :]
    under = Image.new("RGBA", im.size, tuple(round(v * 255) for v in C.COLORS["glow"]) + (0,))
    under.putalpha(Image.fromarray((halo * 255).round().astype(np.uint8), "L"))
    under.alpha_composite(im)
    return under


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", required=True)
    ap.add_argument("--art-root", default=str(ROOT))
    ap.add_argument("--check", action="store_true", help="only report; write nothing")
    args = ap.parse_args(argv)
    R = Path(args.renders)
    frames, clips, origin, canvas = [], {}, None, None
    for name in C.CLIPS:
        meta = json.loads((R / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["times"] == C.times(C.CLIPS[name]), f"{name}: rendered from other clips"
        if origin is None:
            origin, canvas = meta["origin_px"], meta["canvas"]
        assert meta["origin_px"] == origin and meta["canvas"] == canvas, f"{name}: another camera"
        clips[name] = {"first": len(frames), "count": len(meta["times"]), "fps": meta["fps"],
                       "length": meta["length"], "loop": meta["loop"], "times": meta["times"]}
        frames += [Image.open(R / "raw" / name / f"f_{i:03d}.png").convert("RGBA")
                   for i in range(len(meta["times"]))]
    box = CP.tight_box([Image.merge("RGBA", (*im.split()[:3], footprint(im))) for im in frames])
    frames = [glowing(im, box) for im in frames]
    sheets, rec = CP.sheets_for(frames, origin, SHEET_FILE)
    manifest = {"_doc": "Generated by tools/kurage_render/pack.py from tools/kurage_render/render.py's renders "
                        "(a jellyfish built in Blender; no model). The one cell and origin every clip shares, "
                        "per-frame rects and offsets, per-clip frame ranges; the sheet lives in "
                        "ImageGen/images/kokomi/model/frames.",
                "scale": SCALE, "ppu": C.PPU, "texture_import": TEXTURE_IMPORT, **rec, "clips": clips}
    print(f"{rec['count']} frames  cell {rec['cell']}  origin {rec['origin']}  pages "
          f"{[tuple(p['size']) for p in rec['pages']]}")
    text = json.dumps(manifest, indent=1) + "\n"
    if args.check:
        current = MANIFEST.read_text(encoding="utf-8") if MANIFEST.exists() else ""
        if current != text:
            print(f"STALE: {MANIFEST.name} differs from these renders")
            return 1
        print(f"{MANIFEST.name} matches these renders")
        return 0
    out = Path(args.art_root) / "ImageGen" / "images" / "kokomi" / "model" / "frames"
    out.mkdir(parents=True, exist_ok=True)
    for name, im in sheets:
        im.save(out / name, optimize=True)
        print("wrote", out / name)
    MANIFEST.write_text(text, encoding="utf-8", newline="\n")
    print("wrote", MANIFEST.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
