"""Review renders of the Klee mesh rig, drawn by the engine.

MegaDot renders every frame (render.gd, with a window: skinning needs a real
renderer). Python only assembles: per animation a contact sheet and a GIF at
the in-game combat size (1x) and at 2x, plus the rest pose at 3x with the mesh
wireframe and the bones drawn over it, and a dominant-bone weight map.
Renders are review material only; they go to `--out` (a scratch dir), never
into the repo.
"""
from __future__ import annotations

import math
import shutil
from pathlib import Path

from . import engine, rig

BG = (43, 47, 58, 255)
W, H, OX, OY = 340, 330, 160, 312
GIF_FPS = 30
#: The frame of each motion with the largest joint angles (RESET first).
DETAIL_KEYS = [("RESET", 0), ("attack", 0.42), ("hurt", 0.1), ("death", 1.0),
               ("cast", 0.38), ("power", 0.38), ("idle_low", 0.0), ("idle", 0.9), ("setoff", 0.27)]
LAYER_COLOURS = {"Smoke": (140, 200, 255), "Floaters": (255, 220, 90), "Dumpty": (255, 120, 90),
                 "Body": (120, 255, 140), "Dodoco": (255, 140, 255)}


def _times(length: float, n: int, loop: bool) -> list[float]:
    if loop:
        return [round(length * i / n, 4) for i in range(n)]
    return [round(length * i / (n - 1), 4) for i in range(n)]


def _flatten(path: Path):
    from PIL import Image

    return _flatten_im(Image.open(path))


def _flatten_im(im):
    from PIL import Image

    im = im.convert("RGBA")
    bg = Image.new("RGBA", im.size, BG)
    bg.alpha_composite(im)
    return bg.convert("RGB")


def _sheet(frames, times, label_scale: int):
    from PIL import Image, ImageDraw

    fw, fh = frames[0].size
    cols = 5 if len(frames) > 6 else len(frames)
    rows = math.ceil(len(frames) / cols)
    sheet = Image.new("RGB", (fw * cols, fh * rows), BG[:3])
    d = ImageDraw.Draw(sheet)
    for i, (f, t) in enumerate(zip(frames, times)):
        x, y = (i % cols) * fw, (i // cols) * fh
        sheet.paste(f, (x, y))
        d.rectangle([x, y, x + fw - 1, y + fh - 1], outline=(70, 75, 90))
        d.text((x + 4, y + 4), t if isinstance(t, str) else f"t={t:.3f}", fill=(230, 230, 230))
    return sheet


def _overlay(rest_png: Path, scale: int, out: Path) -> None:
    from PIL import Image, ImageDraw

    r = rig.Rig(rig.load_spec(), rig.load_cells())
    meshes = rig.build_meshes(r)
    base = Image.open(rest_png).convert("RGBA")
    bg = Image.new("RGBA", base.size, BG)
    bg.alpha_composite(base)
    ox, oy = OX * scale, OY * scale
    rx, ry = r.spec["rig_position"]

    def P(p):
        return (ox + (rx + p[0]) * scale, oy + (ry + p[1]) * scale)

    wire = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(wire)
    for m in meshes:
        col = LAYER_COLOURS[m.layer] + (70,)
        for q in m.quads:
            pts = [P(m.polygon[i]) for i in q]
            d.line(pts + [pts[0]], fill=col, width=1)
    bg.alpha_composite(wire)
    d = ImageDraw.Draw(bg)
    for name in r.order:
        b = r.bones[name]
        a = P(b.at)
        end = P(b.tip) if b.tip else None
        if end:
            d.line([a, end], fill=(255, 255, 255, 255), width=3)
            d.line([a, end], fill=(230, 40, 40, 255), width=1)
        if b.parent:
            d.line([P(r.bones[b.parent].at), a], fill=(255, 255, 255, 90), width=1)
        d.ellipse([a[0] - 4, a[1] - 4, a[0] + 4, a[1] + 4], fill=(255, 230, 0, 255), outline=(0, 0, 0, 255))
        d.text((a[0] + 5, a[1] - 6), name, fill=(255, 255, 255, 255))
    bg.convert("RGB").save(out)

    # dominant-bone weight map
    wm = Image.new("RGBA", base.size, BG)
    d = ImageDraw.Draw(wm)
    palette = {}
    for i, name in enumerate(r.order):
        h = (i * 0.61803) % 1.0
        import colorsys
        palette[name] = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, 0.65, 0.95))
    for m in meshes:
        for q in m.quads:
            pts = [P(m.polygon[i]) for i in q]
            c = [0.0, 0.0, 0.0]
            for i in q:
                for b, ws in m.weights.items():
                    for k in range(3):
                        c[k] += ws[i] * palette[b][k] / 4
            d.polygon(pts, fill=tuple(int(v) for v in c) + (255,))
    for name in r.order:
        a = P(r.bones[name].at)
        d.text((a[0] + 3, a[1] - 6), name, fill=(255, 255, 255, 255))
    wm.convert("RGB").save(out.with_name("rest_weights_3x.png"))


def main(art_root: Path, out: Path, frames: int) -> int:
    from PIL import Image

    out.mkdir(parents=True, exist_ok=True)
    work = out / "_project"
    raw = out / "_frames"
    if raw.exists():
        shutil.rmtree(raw)
    raw.mkdir()
    engine.make_project(work, art_root)
    engine.import_project(work)
    spec = rig.load_spec()
    passes = []
    for scale in (1, 2):
        sheet_jobs, gif_jobs = [], []
        for name in rig.ANIMATION_ORDER:
            a = spec["animations"][name]
            L, loop = float(a["length"]), bool(a.get("loop"))
            sheet_jobs.append([name, _times(L, frames, loop)])
            gif_jobs.append([name, _times(L, max(2, round(L * GIF_FPS)), loop)])
        common = {"scene": "res://klee/model/combat.tscn", "out": raw.as_posix(), "scale": scale,
                  "w": W * scale, "h": H * scale, "origin": [OX * scale, OY * scale], "facing": 1}
        passes.append({**common, "prefix": f"sheet{scale}_", "jobs": sheet_jobs})
        passes.append({**common, "prefix": f"gif{scale}_", "jobs": gif_jobs})
    passes.append({"scene": "res://klee/model/combat.tscn", "out": raw.as_posix(), "scale": 3,
                   "w": W * 3, "h": H * 3, "origin": [OX * 3, OY * 3], "facing": 1,
                   "prefix": "rest3_", "jobs": [["RESET", [0]]]})
    # Joint close-ups: each motion's most deformed key at 4x, Rig held at
    # rest so the crop stays on the body (a review aid, not the motion).
    passes.append({"scene": "res://klee/model/combat.tscn", "out": raw.as_posix(), "scale": 4,
                   "w": W * 4, "h": H * 4, "origin": [OX * 4, OY * 4], "facing": 1,
                   "prefix": "detail4_", "pin_rig": True,
                   "jobs": [[name, [t]] for name, t in DETAIL_KEYS]})
    engine.render(work, passes)

    written = []
    for scale in (1, 2):
        for name in rig.ANIMATION_ORDER:
            a = spec["animations"][name]
            L, loop = float(a["length"]), bool(a.get("loop"))
            st = _times(L, frames, loop)
            sf = [_flatten(raw / f"sheet{scale}_{name}_{i:03d}.png") for i in range(len(st))]
            p = out / f"{name}_sheet_{scale}x.png"
            _sheet(sf, st, scale).save(p)
            written.append(p)
            gt = _times(L, max(2, round(L * GIF_FPS)), loop)
            gf = [_flatten(raw / f"gif{scale}_{name}_{i:03d}.png") for i in range(len(gt))]
            p = out / f"{name}_{scale}x.gif"
            gf[0].save(p, save_all=True, append_images=gf[1:], duration=round(1000 / GIF_FPS),
                       loop=0, disposal=2)
            written.append(p)
    crop = (OX * 4 - 300, OY * 4 - 800, OX * 4 + 420, OY * 4 - 20)
    tiles = [Image.open(raw / f"detail4_RESET_000.png")] +         [Image.open(raw / f"detail4_{n}_000.png") for n, _t in DETAIL_KEYS[1:]]
    tiles = [_flatten_im(t).crop(crop) for t in tiles]
    labels = ["rest"] + [f"{n} t={t}" for n, t in DETAIL_KEYS[1:]]
    _sheet(tiles, labels, 4).save(out / "joints_detail_4x.png")
    written.append(out / "joints_detail_4x.png")
    _overlay(raw / "rest3_RESET_000.png", 3, out / "rest_overlay_3x.png")
    written += [out / "rest_overlay_3x.png", out / "rest_weights_3x.png"]
    for p in written:
        print(p)
    return 0
