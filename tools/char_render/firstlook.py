"""First-look sheet for one kit model: render, paint (style G), compose.

    python tools/char_render/firstlook.py --char furina --models <scratch>/models \
        --base <dir with b1_ironclad.png/.json, b1_silent.png/.json> \
        --out <scratch>/models/firstlook [--art-root <main checkout>] [--skip-render]

Renders the neutral rest pose and the draft battle stance (render.py, in
Blender), paints them with style G's 2D half (tools/klee_render/post.py,
imported, not copied: it is pure numpy/Pillow), and lays them out at 1080p
game scale on one ground line beside base Ironclad and Silent and the kit's
current combat sprite (<art-root>/ImageGen/images/<char>/model/combat_model.png,
read only, drawn 1:1 as its static fallback is). A 2x row follows for detail.

Scratch only: nothing here writes into the repo, ImageGen or art/. The model
packs stay under the operator's scratch models/ directory.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BLENDER = r"C:\Users\Monty\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe"
sys.path.insert(0, str(HERE))
import chars as CH  # noqa: E402


def _load_klee(name: str):
    """tools/klee_render/<name>.py by path, under a private module name."""
    spec = importlib.util.spec_from_file_location(f"klee_render_{name}", ROOT / "tools" / "klee_render" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BG = (58, 56, 66, 255)
GROUND = (74, 70, 80, 255)


def down(im: Image.Image, f: float) -> Image.Image:
    """Premultiplied-alpha downsample by factor f (the game's 0.5 draw)."""
    a = np.asarray(im.convert("RGBA")).astype(np.float32) / 255
    pm = a.copy()
    pm[..., :3] *= pm[..., 3:4]
    W, H = max(1, round(im.width / f)), max(1, round(im.height / f))
    o = np.stack([np.asarray(Image.fromarray(pm[..., c]).resize((W, H), Image.LANCZOS)) for c in range(4)], -1)
    al = np.clip(o[..., 3:4], 1e-6, 1)
    o[..., :3] = np.where(o[..., 3:4] > 1e-4, o[..., :3] / al, 0)
    return Image.fromarray((np.clip(o, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")


def render(char: str, models: Path, work: Path, blender: str) -> None:
    cfg = CH.CHARS[char]
    cmd = [blender, "-b", "--factory-startup", "-P", str(HERE / "render.py"), "--",
           "--char", char, "--pmx", str(models / cfg["pmx"]), "--out", str(work)]
    if cfg["prop"]:
        cmd += ["--prop", str(models / cfg["prop"])]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    for line in res.stdout.splitlines():
        if line.startswith(("SCALE", "STILL", "WARN", "Traceback", "Error")):
            print("  ", line)
    if res.returncode != 0 or "Traceback" in res.stdout + res.stderr:
        print(res.stdout[-3000:], res.stderr[-3000:])
        raise SystemExit(1)


def paint(work: Path, names) -> None:
    post = _load_klee("post")
    for n in names:
        # s = 1: every combat render is drawn at 0.5 whatever its ppu, so the
        # 2D strokes keep their texture-px size (post.py's REF scale)
        post.paint(Image.open(work / "raw" / f"{n}.png"), Image.open(work / "raw" / "aux" / f"{n}_X.png"),
                   1.0).save(work / f"{n}.png")


def figure(work: Path, name: str, zoom: float, shadow: bool):
    meta = json.loads((work / f"{name}.json").read_text(encoding="utf-8"))
    im = Image.open(work / f"{name}.png").convert("RGBA")
    sc = CH.COMBAT_SCALE * zoom
    fig = down(im, 1 / sc) if sc < 1 else im
    ox, oy = meta["origin_px"]
    pad = round(40 * zoom)
    can = Image.new("RGBA", (fig.width + 2 * pad, fig.height + pad), (0, 0, 0, 0))
    anchor = (pad + ox * sc, oy * sc)
    if shadow:
        pack = _load_klee("pack")
        bbox = im.getchannel("A").getbbox()
        full_h = (oy - bbox[1]) * sc
        w = round(max(0.55 * full_h, 0.0) * 0.9)
        h = max(1, round(w * pack.SHADOW_ASPECT))
        t = pack.shadow_texture(w * 2, h * 2).resize((w, h), Image.LANCZOS)
        can.alpha_composite(t, (round(anchor[0] - w / 2), round(anchor[1] - h / 2)))
    can.alpha_composite(fig, (pad, 0))
    body = (oy - im.getchannel("A").getbbox()[1]) * CH.COMBAT_SCALE
    return can, anchor, body, meta


def base(base_dir: Path, c: str, zoom: int):
    tag = "b1" if zoom == 1 else "b2"
    im = Image.open(base_dir / f"{tag}_{c}.png").convert("RGBA")
    o = json.loads((base_dir / f"{tag}_{c}.json").read_text())["origin"]
    return im, tuple(o)


def current_sprite(art_root: Path, char: str, zoom: int):
    p = art_root / "ImageGen" / "images" / char / "model" / "combat_model.png"
    if not p.exists():
        return None
    im = Image.open(p).convert("RGBA")
    bb = im.getchannel("A").getbbox()
    if zoom != 1:
        im = im.resize((im.width * zoom, im.height * zoom), Image.LANCZOS)
    return im, (im.width / 2, bb[3] * zoom)


def sheet(char: str, work: Path, base_dir: Path, art_root: Path, out: Path) -> dict:
    F = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
    FB = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 18)
    rows, info = [], {}
    for zoom in (1, 2):
        items = [("Ironclad", *base(base_dir, "ironclad", zoom))]
        for n, label in (("rest", "rest pose"), ("stance", "draft stance + shadow")):
            can, anc, body, meta = figure(work, n, zoom, shadow=(n == "stance"))
            items.append((f"{char} {label} ({body:.0f} px)", can, anc))
            info[n] = {"body_px_1080p": round(body, 1), "ppu": meta["ppu"]}
        cur = current_sprite(art_root, char, zoom)
        if cur:
            items.append((f"{char} now (combat_model.png)", *cur))
        items.append(("Silent", *base(base_dir, "silent", zoom)))
        ground = max(a[1] for _l, _i, a in items) + 10
        height = ground + 40 * zoom
        gap = 18
        W = sum(i.width for _l, i, _a in items) + gap * (len(items) + 1)
        can = Image.new("RGBA", (W, round(height) + 28), BG)
        d = ImageDraw.Draw(can)
        d.rectangle((0, ground + 28, W, height + 28), fill=GROUND)
        target = CH.body_px(CH.CHARS[char]["height_in"])
        d.text((8, 4), f"{char}: style G first look, {'1080p' if zoom == 1 else '2x'} "
                       f"(canon {CH.CHARS[char]['height_in']:.0f} in -> {target:.0f} px; base adults ~235)",
               font=FB, fill=(240, 240, 240))
        x = gap
        for label, im, (ox, oy) in items:
            can.alpha_composite(im, (round(x), round(ground + 28 - oy)))
            d.text((x, height + 28 - 20), label, font=F, fill=(220, 220, 220))
            x += im.width + gap
        rows.append(can)
    W = max(r.width for r in rows)
    outim = Image.new("RGBA", (W, sum(r.height for r in rows)), BG)
    y = 0
    for r in rows:
        outim.alpha_composite(r, (0, y))
        y += r.height
    out.mkdir(parents=True, exist_ok=True)
    outim.convert("RGB").save(out / f"{char}.png")
    return info


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--char", required=True, choices=sorted(CH.CHARS))
    ap.add_argument("--models", required=True, help="scratch models root (models/<char>/unpacked/...)")
    ap.add_argument("--base", required=True, help="dir with b1_/b2_ ironclad and silent PNG + JSON")
    ap.add_argument("--out", required=True)
    ap.add_argument("--art-root", default=str(ROOT))
    ap.add_argument("--blender", default=BLENDER)
    ap.add_argument("--skip-render", action="store_true")
    args = ap.parse_args(argv)
    out = Path(args.out)
    work = out / f"{args.char}_work"
    if not args.skip_render:
        render(args.char, Path(args.models), work, args.blender)
    paint(work, ("rest", "stance"))
    info = sheet(args.char, work, Path(args.base), Path(args.art_root), out)
    print(args.char, json.dumps(info), "->", out / f"{args.char}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
