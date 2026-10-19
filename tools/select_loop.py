"""Character select, stage 2: a rendered idle loop of the close-up, for Klee, Varka, Furina and Yae.

[USER], 2026-10-14: "during character select, none of the art pieces for the
base game's characters are static; the character does a small idle loop with
particle effects." Stage 1 (PR #1303) breathed the still close-up and drifted
element particles over it. Stage 2 (this file) renders the close-up itself as
a short loop from the official model: the SAME pose, camera, scale, outline and
paint as `select_closeup.png`, moved through half a breath (chest, head, arms,
and the pigtails or coat tails or cloth, each a cosine of the loop). The game
plays it forward then back, so there is no seam and no popping: frame 0 is
the still, and the last frame is the exhale.

    python tools/select_loop.py build --char klee|varka|furina|yae --models <scratch>/models \
        --work <scratch dir> [--pmx <klee pmx>] [--art-root <main checkout>] [--blender <exe>]
    python tools/select_loop.py render --char ... --models ... --work ...   # Blender + post.py only
    python tools/select_loop.py pack   --char ... --work ... [--art-root ...] [--check]

THE MODELS NEVER ENTER THE REPO (their terms forbid redistribution). Renders go
to --work (scratch); pack writes under <art-root>/ImageGen/images (gitignored)
and the committed manifest tools/select_loop.json (sizes, grid, box, no pixels).

Producers (one each, tools/art_lint.py): this file writes, per character,
  ui/select_loop.png            the loop's frames in one sheet (a grid of cells)
  ui/select_closeup_static.png  the close-up with the moving region cleared
                                (none when nothing is left: Klee and Furina
                                breathe with the whole figure, so the box is
                                the figure and the plate would be blank; the
                                manifest then names static_file null)
(Klee's under ImageGen/images/ui, the others' under ImageGen/images/<char>/ui).
Only the region that moves is rendered into the sheet (the box of every pixel
that differs from frame 0), so Varka's planted blades and the rest of the
frame cost nothing; the still `select_closeup.png` stays beside them,
untouched, and tools/select_bg.py draws the old stage-1 scene when the manifest
has no entry for a character. The sheet ships VRAM-compressed (about one byte
a texel: build_pck.ps1 writes its .import), so its pixels ARE its size.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools" / "select_loop.json"
BLENDER = r"C:\Users\Monty\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe"

#: texel budget of one character's sheet (VRAM-compressed, ~1 byte a texel)
BUDGET_PX = 8_000_000
#: a pixel moves if a channel differs from frame 0 by more than this
MOVE_THRESHOLD = 6
#: margin round the moving box, then rounded out to the 4-texel compression block
BOX_PAD = 8
SHEET_MAX = 8192
SCALE_STEP = 0.05
SCALE_MIN = 0.6

#: per character: its renderer, its select ppu and outline (the same numbers as
#: the still's: klee_render/build.py JOBS, char_render/build.py SELECT_PPU)
CHARS = {
    "klee": {"kind": "klee", "ppu": 1700.0, "outline": 6.0, "art": ("ui",)},
    "varka": {"kind": "kit", "ppu": 1100.0, "outline": 7.0, "art": ("varka", "ui")},
    "furina": {"kind": "kit", "ppu": 1300.0, "outline": 7.0, "art": ("furina", "ui")},
    "yae": {"kind": "kit", "ppu": 1200.0, "outline": 7.0, "art": ("yae", "ui")},
}
SHEET_FILE = "select_loop.png"
STATIC_FILE = "select_closeup_static.png"


def art_dir(char: str, art_root: str | Path) -> Path:
    return Path(art_root).joinpath("ImageGen", "images", *CHARS[char]["art"])


# ---------------------------------------------------------------------------
# render (Blender, then post.py)
# ---------------------------------------------------------------------------


def render(char: str, models: str, work: Path, pmx: str = "", blender: str = BLENDER) -> None:
    c = CHARS[char]
    work.mkdir(parents=True, exist_ok=True)
    if c["kind"] == "klee":
        if not pmx:
            raise SystemExit("klee needs --pmx (the official Klee PMX)")
        cmd = [blender, "-b", "--factory-startup", "-P", str(ROOT / "tools" / "klee_render" / "render.py"), "--",
               "--pmx", pmx, "--out", str(work), "--ppu", f"{c['ppu']:.4f}", "--outline-px", f"{c['outline']:.3f}",
               "--clips", "select_loop", "--stills", "select"]
    else:
        cmd = [blender, "-b", "--factory-startup", "-P", str(ROOT / "tools" / "char_render" / "render.py"), "--",
               "--char", char, "--models", models, "--out", str(work), "--ppu", f"{c['ppu']:.4f}",
               "--outline-px", f"{c['outline']:.3f}", "--clips", "select_loop", "--stills", "select"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    for line in res.stdout.splitlines():
        if line.startswith(("CLIP", "STILL", "WARN", "Traceback", "Error")):
            print("  ", line)
    if res.returncode != 0 or "Traceback" in res.stdout + res.stderr:
        print(res.stdout[-3000:], res.stderr[-3000:])
        raise SystemExit(1)
    sys.path.insert(0, str(ROOT / "tools" / "klee_render"))
    from post import main as post_main  # noqa: E402

    if post_main(["--renders", str(work), "--only", "select_loop,select"]) != 0:
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# pack
# ---------------------------------------------------------------------------


def _placer(char: str, R: Path):
    """(place, rec): the still's framing as a function (see char_render/pack.py
    select_placer); Klee's is its pack.py's, inline there, written out here."""
    from PIL import Image

    if char != "klee":
        sys.path.insert(0, str(ROOT / "tools" / "char_render"))
        import importlib.util

        spec = importlib.util.spec_from_file_location("char_render_pack", ROOT / "tools" / "char_render" / "pack.py")
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(ROOT / "tools" / "klee_render"))
        spec.loader.exec_module(mod)
        return mod.select_placer(R)
    sys.path.insert(0, str(ROOT / "tools" / "klee_render"))
    import pack as KP

    sel = Image.open(R / "select.png").convert("RGBA")
    sb = KP.alpha_box([sel])
    sel = sel.crop(sb)
    target_h = 2150
    k = target_h / sel.height
    new_w = round(sel.width * k)
    x0 = 1260 - new_w // 2

    def place(im, at=(0, 0)):
        pad = 96
        base = Image.new("RGBA", (sb[2] + pad * 2 + im.width, sb[3] + pad * 2 + im.height), (0, 0, 0, 0))
        base.paste(im, (round(at[0]) + pad, round(at[1]) + pad))
        part = base.crop((sb[0] + pad, sb[1] + pad, sb[2] + pad, sb[3] + pad)).resize((new_w, target_h), Image.LANCZOS)
        canvas = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        canvas.paste(part, (x0, 36), part)
        return canvas
    return place, {"size": [1920, 1080], "figure_h": target_h}


def _ceil4(n: float) -> int:
    return int(math.ceil(n / 4.0)) * 4


def pack(char: str, R: Path, art_root: str | Path, check: bool = False) -> dict:
    import numpy as np
    from PIL import Image

    place, _rec = _placer(char, R)
    still_meta = json.loads((R / "select.json").read_text(encoding="utf-8"))
    loop_meta = json.loads((R / "select_loop.json").read_text(encoding="utf-8"))
    n = len(loop_meta["times"])
    at = (still_meta["origin_px"][0] - loop_meta["origin_px"][0], still_meta["origin_px"][1] - loop_meta["origin_px"][1])
    # the two renders frame their own boxes, so their feet anchors differ by a
    # fraction of a texel: shift by the fraction (bicubic), place by the whole
    fx, fy = at[0] - round(at[0]), at[1] - round(at[1])

    def load(i):
        im = Image.open(R / "select_loop" / f"f_{i:03d}.png").convert("RGBA")
        if abs(fx) > 0.01 or abs(fy) > 0.01:
            im = im.transform(im.size, Image.AFFINE, (1, 0, -fx, 0, 1, -fy), resample=Image.BICUBIC)
        return place(im, (round(at[0]), round(at[1])))
    frames = [load(i) for i in range(n)]
    still = place(Image.open(R / "select.png").convert("RGBA"))
    a0, a1 = np.asarray(still, np.int16), np.asarray(frames[0], np.int16)
    drift = float(np.abs(a0 - a1).mean())
    assert drift < 0.5, f"frame 0 is not the still (mean channel difference {drift:.3f})"

    ref = np.asarray(frames[0], np.int16)
    moved = np.zeros(ref.shape[:2], bool)
    for f in frames[1:]:
        cur = np.asarray(f, np.int16)
        d_a = np.abs(cur[..., 3] - ref[..., 3]) > MOVE_THRESHOLD
        d_c = (np.abs(cur[..., :3] - ref[..., :3]).max(axis=2) > MOVE_THRESHOLD) & ((cur[..., 3] > 0) | (ref[..., 3] > 0))
        moved |= d_a | d_c
    ys, xs = np.nonzero(moved)
    x0, x1 = max(0, _floor4(xs.min() - BOX_PAD)), min(1920, _ceil4(xs.max() + 1 + BOX_PAD))
    y0, y1 = max(0, _floor4(ys.min() - BOX_PAD)), min(1080, _ceil4(ys.max() + 1 + BOX_PAD))
    bw, bh = x1 - x0, y1 - y0

    s = min(1.0, math.sqrt(BUDGET_PX / (n * bw * bh)))
    s = max(SCALE_MIN, math.floor(s / SCALE_STEP) * SCALE_STEP)
    cw, ch = _ceil4(bw * s), _ceil4(bh * s)
    cols = min(range(1, n + 1), key=lambda c: (max(c * cw, math.ceil(n / c) * ch) > SHEET_MAX, c * cw * math.ceil(n / c) * ch))
    rows = math.ceil(n / cols)
    sheet = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        cell = f.crop((x0, y0, x1, y1))
        if (cw, ch) != (bw, bh):
            cell = cell.resize((cw, ch), Image.LANCZOS)
        sheet.paste(cell, ((i % cols) * cw, (i // cols) * ch))
    plate = frames[0].copy()
    plate.paste(Image.new("RGBA", (bw, bh), (0, 0, 0, 0)), (x0, y0))
    # A blank plate still costs a 1920x1080 texture in the pck (~2 MB,
    # VRAM-compressed): ship none, and the scene draws no Splash.
    static_file = STATIC_FILE if plate.getchannel("A").getbbox() else None

    out = art_dir(char, art_root)
    sheet_path, plate_path = out / SHEET_FILE, out / STATIC_FILE
    rec = {"frames": n, "fps": loop_meta["fps"], "box": [x0, y0, bw, bh], "scale": round(s, 4),
           "cell": [cw, ch], "grid": [cols, rows], "sheet": [sheet.width, sheet.height],
           "sheet_file": SHEET_FILE, "static_file": static_file, "ppu": still_meta["ppu"],
           "texel_mb": round(sheet.width * sheet.height / 1e6, 2)}
    print(f"{char}: {n} frames at {loop_meta['fps']} fps, moving box {bw}x{bh} at ({x0},{y0}), scale {s:.2f}, "
          f"cell {cw}x{ch}, grid {cols}x{rows}, sheet {sheet.width}x{sheet.height} = {rec['texel_mb']} M texels; "
          f"frame 0 vs still: mean diff {drift:.3f}" + ("" if static_file else "; nothing outside the box, no static plate"))
    if check:
        return rec
    out.mkdir(parents=True, exist_ok=True)
    sheet.save(sheet_path, optimize=True)
    rec["sheet_png_bytes"] = sheet_path.stat().st_size
    if static_file:
        plate.save(plate_path, optimize=True)
        rec["static_png_bytes"] = plate_path.stat().st_size
    else:
        plate_path.unlink(missing_ok=True)
    data = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    data["_doc"] = ("Generated by tools/select_loop.py from renders of the official models (never committed). "
                    "Sizes, the moving box, the grid and the timing only; the sheets live under ImageGen/images. "
                    "tools/select_bg.py draws the stage-1 scene for a character with no entry.")
    data[char] = {k: v for k, v in rec.items() if not k.endswith("_bytes")}
    MANIFEST.write_text(json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return rec


def _floor4(n: float) -> int:
    return int(math.floor(n / 4.0)) * 4


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python tools/select_loop.py")
    ap.add_argument("cmd", choices=["render", "pack", "build"])
    ap.add_argument("--char", required=True, choices=sorted(CHARS))
    ap.add_argument("--models", default="")
    ap.add_argument("--pmx", default="")
    ap.add_argument("--work", required=True)
    ap.add_argument("--blender", default=BLENDER)
    ap.add_argument("--art-root", default=str(ROOT))
    ap.add_argument("--check", action="store_true", help="pack: report, write nothing")
    args = ap.parse_args(argv)
    work = Path(args.work)
    t0 = time.time()
    if args.cmd in ("render", "build"):
        render(args.char, args.models, work, args.pmx, args.blender)
        print(f"render + paint: {time.time() - t0:.0f} s")
    if args.cmd in ("pack", "build"):
        pack(args.char, work, args.art_root, args.check)
    return 0


if __name__ == "__main__":
    sys.exit(main())
