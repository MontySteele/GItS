"""Pack Klee's rendered frames into the game's sheets and stills.

    python tools/klee_render/pack.py --renders <scratch dir> [--art-root <main checkout>] [--check]

Reads what tools/klee_render/render.py wrote (per clip: f_NNN.png + <clip>.json;
per still: <name>.png + <name>.json) and writes, under <art-root>/ImageGen:

  images/model/frames/klee_<clip>.png   one sheet per combat clip (and the
                                        merchant loop), cells in reading order
  images/model/klee_rest.png            the seated rest-site still, padded so
                                        BaseLib's centred sprite puts her seat
                                        on the rest-site anchor
  images/ui/select_closeup.png          the character-select close-up, 1920x1080

and the committed manifest tools/klee_rig/klee_frames.json (sizes, frame
counts, times and anchors -- no pixels), which `python -m tools.klee_rig gen`
reads to build combat.tscn and build_pck.ps1's merchant scene reads too.
This script is the ONE producer of those paths (art_lint GENERATOR_OWNED).

Scale contract (review/active/klee-visual-paper-2026-10-12.md, ruled 2026-10-12):
combat frames are rendered at 288 texture px per model unit and drawn at
scale 0.5, i.e. 144 screen px per unit at 1080p -- her hat-to-boot height is
about 166 px, 0.71 of the base adults' ~235. The merchant draws the same
figure at 1.7x (texture 1.5x, scale 1/1.5); the rest site at 1.33x (BaseLib's
0.5 container, so the texture is 2x that); select is a close-up.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tools" / "klee_rig" / "klee_frames.json"

#: combat clips, drawn at 0.5 (2x textures for 4K)
COMBAT = ("idle", "idle_low", "attack", "hurt", "death", "cast")
COMBAT_SCALE = 0.5
#: Spelled out, not formatted: art_lint's GENERATOR_OWNED rot check greps this
#: file for every out-path's basename.
SHEET_FILES = {"idle": "klee_idle.png", "idle_low": "klee_idle_low.png", "attack": "klee_attack.png",
               "hurt": "klee_hurt.png", "death": "klee_death.png", "cast": "klee_cast.png",
               "merchant": "klee_merchant.png"}
MERCHANT_SCALE = round(1 / 1.5, 6)
MAX_SHEET = 4096
PAD = 2


def alpha_box(ims):
    box = None
    for im in ims:
        b = im.getchannel("A").point(lambda v: 255 if v > 0 else 0).getbbox()
        if b is None:
            continue
        box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    return box


def sheet_for(clip_dir: Path, meta: dict):
    frames = [Image.open(clip_dir / f"f_{i:03d}.png").convert("RGBA") for i in range(len(meta["times"]))]
    x0, y0, x1, y1 = alpha_box(frames)
    x0, y0 = max(0, x0 - PAD), max(0, y0 - PAD)
    x1, y1 = min(frames[0].width, x1 + PAD), min(frames[0].height, y1 + PAD)
    cw, ch = x1 - x0, y1 - y0
    n = len(frames)
    cols = max(1, min(n, MAX_SHEET // cw, math.ceil(math.sqrt(n * ch / cw))))
    rows = math.ceil(n / cols)
    assert rows * ch <= MAX_SHEET, (meta["clip"], rows, ch)
    sheet = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        sheet.paste(im.crop((x0, y0, x1, y1)), ((i % cols) * cw, (i // cols) * ch))
    ox, oy = meta["origin_px"]
    return sheet, {
        "cell": [cw, ch], "hframes": cols, "vframes": rows, "count": n,
        "fps": meta["fps"], "length": meta["length"], "loop": meta["loop"],
        "motion_end": meta.get("motion_end"), "times": meta["times"],
        # whole texels, so the sprite's offset never lands between two
        "origin": [round(ox - x0), round(oy - y0)], "ppu": meta["ppu"],
    }


def body_metrics(still: Path, meta: dict, scale: float) -> dict:
    """Her on-screen height at 1080p: the full alpha box (feather tip to boot)
    and hat-top to boot (the first row wider than the feather)."""
    im = Image.open(still).convert("RGBA")
    a = im.getchannel("A")
    bx = a.getbbox()
    w, h = im.size
    px = a.load()
    hat_top = None
    for y in range(bx[1], bx[3]):
        run = sum(1 for x in range(w) if px[x, y] > 128)
        if run >= 24:
            hat_top = y
            break
    foot = meta["origin_px"][1]
    return {
        "full_px": round((foot - bx[1]) * scale, 1),
        "hat_to_boot_px": round((foot - hat_top) * scale, 1),
        "width_px": round((bx[2] - bx[0]) * scale, 1),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", required=True, help="render.py --out dir (combat + merchant + stills)")
    ap.add_argument("--art-root", default=str(ROOT))
    ap.add_argument("--check", action="store_true", help="only report; write nothing")
    args = ap.parse_args(argv)
    R = Path(args.renders)
    art = Path(args.art_root) / "ImageGen" / "images"
    out_frames = art / "model" / "frames"
    manifest = {"_doc": "Generated by tools/klee_render/pack.py from renders of the official Klee model "
                        "(never committed). Cells, counts, times and anchors only; the sheets live in "
                        "ImageGen/images/model/frames.",
                "combat_scale": COMBAT_SCALE, "merchant_scale": MERCHANT_SCALE, "sheets": {}}
    writes = []
    for clip in (*COMBAT, "merchant"):
        meta = json.loads((R / f"{clip}.json").read_text(encoding="utf-8"))
        assert not meta.get("keys_only"), f"{clip}: a --keys-only render is a preview, not frames"
        sheet, rec = sheet_for(R / clip, meta)
        rec["file"] = SHEET_FILES[clip]
        manifest["sheets"][clip] = rec
        writes.append((out_frames / rec["file"], sheet))
        print(f"{clip:9s} {rec['count']:3d} frames  cell {rec['cell']}  grid {rec['hframes']}x{rec['vframes']}"
              f"  sheet {sheet.size}  origin {rec['origin']}")

    # stance A measured at combat scale: the scale check
    sa = json.loads((R / "stance_a.json").read_text(encoding="utf-8"))
    manifest["measure"] = body_metrics(R / "stance_a.png", sa, COMBAT_SCALE)
    print("stance A at 1080p:", manifest["measure"])

    # rest: BaseLib centres the texture at y = -0.1 h inside a 0.5 container,
    # so a point at (w/2, 0.6 h) of the texture lands on the anchor. Pad so
    # her seat (the hips' head) is that point.
    rest_meta = json.loads((R / "rest.json").read_text(encoding="utf-8"))
    rest = Image.open(R / "rest.png").convert("RGBA")
    rb = alpha_box([rest])
    rest = rest.crop(rb)
    hx, hy = rest_meta["hips_px"][0] - rb[0], rest_meta["hips_px"][1] - rb[1]
    half_w = math.ceil(max(hx, rest.width - hx)) + PAD
    # need hy' = 0.6 H with hy' >= hy and H - hy' >= rest.height - hy
    H = math.ceil(max(hy / 0.6, (rest.height - hy) / 0.4)) + PAD
    top = round(0.6 * H - hy)
    canvas = Image.new("RGBA", (2 * half_w, H), (0, 0, 0, 0))
    canvas.paste(rest, (round(half_w - hx), top))
    writes.append((art / "model" / "klee_rest.png", canvas))
    manifest["rest"] = {"file": "klee_rest.png", "size": list(canvas.size), "ppu": rest_meta["ppu"],
                        "seat_px": [half_w, round(0.6 * H)]}
    print("rest     ", canvas.size, "seat at", manifest["rest"]["seat_px"])

    # select: a 1920x1080 close-up, figure right of centre, bleeding off the bottom
    sel = Image.open(R / "select.png").convert("RGBA")
    sb = alpha_box([sel])
    sel = sel.crop(sb)
    target_h = 2150                      # full figure height: hat to waist on screen, the rest bleeds off
    k = target_h / sel.height
    sel = sel.resize((round(sel.width * k), target_h), Image.LANCZOS)
    canvas = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    canvas.paste(sel, (1260 - sel.width // 2, 36), sel)
    writes.append((art / "ui" / "select_closeup.png", canvas))
    manifest["select"] = {"file": "select_closeup.png", "size": [1920, 1080], "figure_h": target_h}

    if args.check:
        current = MANIFEST.read_text(encoding="utf-8") if MANIFEST.exists() else ""
        text = json.dumps(manifest, indent=1, ensure_ascii=False) + "\n"
        if current != text:
            print("STALE: klee_frames.json differs from these renders")
            return 1
        print("klee_frames.json matches these renders")
        return 0
    for path, im in writes:
        path.parent.mkdir(parents=True, exist_ok=True)
        im.save(path, optimize=True)
        print("wrote", path)
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("wrote", MANIFEST.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
