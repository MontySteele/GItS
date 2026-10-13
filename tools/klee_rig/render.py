"""Review renders of Klee's combat scene, drawn by the engine.

MegaDot renders every frame (render.gd, with a window). Python only
assembles: per animation a contact sheet and a GIF at the in-game combat
size (1x) and at 2x.
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
    for p in written:
        print(p)
    return 0
