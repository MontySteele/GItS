"""Render every Klee surface from the official model, paint it and pack it: one command.

    python tools/klee_render/build.py --pmx <可莉2.0.pmx> --work <scratch dir> \
        [--blender <blender.exe>] [--art-root <main checkout>] [--only-render]

The PMX stays wherever the operator keeps it (never in the repo: its terms
forbid redistribution). `--work` receives the raw renders (render.py, under
<work>/raw), `post.py` paints the 2D half (G's chain plus H3 lite) over every frame and still
(the shader half is render.py's), and `pack.py` then
writes the sheets/stills into <art-root>/ImageGen and the manifest
tools/klee_rig/klee_frames.json. Run from a worktree with --art-root pointing
at the main checkout (operations/art.md: ImageGen lives only there).

THE SCALE, in one place. COMBAT_PPU is texture px per model unit for combat,
drawn at 0.5, so 150 screen px per unit at 1080p: her hat-to-boot height is
~165 px and ~177 px to the feather tip standing (measured on clips.STAND;
the battle stance is lower), about 0.72 of the base adults' ~235
(paper pick 2 as corrected: 4'2" against 5'6"-5'10"). The merchant draws her
at 1.7x (base merchant scale over combat scale) from a 1.5x texture; the rest
site at 1.33x (base 0.38 over 0.28-0.29) through BaseLib's 0.5 container; the
select close-up and the roster tile
(select_portrait.png) are cropped by pack.py.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BLENDER = r"C:\Users\Monty\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe"

COMBAT_PPU = 300.0
OUTLINE_PX = 2.2                       # texture px at COMBAT_PPU (1.1 screen px)
MERCHANT_PPU = COMBAT_PPU * 1.7 * 0.75  # 1.7x on screen from a 1.5x texture
REST_PPU = COMBAT_PPU * (0.38 / 0.285)  # 1.33x on screen; 2x texture under the 0.5 container
SELECT_PPU = 1700.0

JOBS = [
    {"clips": "idle,idle_low,attack,hurt,death,cast,setoff,jumpy", "stills": "stance_a,stand", "ppu": COMBAT_PPU,
     "outline": OUTLINE_PX},
    {"clips": "merchant", "stills": "", "ppu": MERCHANT_PPU, "outline": OUTLINE_PX * MERCHANT_PPU / COMBAT_PPU},
    {"clips": "", "stills": "rest", "ppu": REST_PPU, "outline": OUTLINE_PX * REST_PPU / COMBAT_PPU},
    {"clips": "", "stills": "select,portrait", "ppu": SELECT_PPU, "outline": 6.0},
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pmx", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--blender", default=BLENDER)
    ap.add_argument("--art-root", default=str(ROOT))
    ap.add_argument("--only-render", action="store_true", help="render and paint; do not pack")
    args = ap.parse_args(argv)
    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)
    for job in JOBS:
        cmd = [args.blender, "-b", "--factory-startup", "-P", str(HERE / "render.py"), "--",
               "--pmx", args.pmx, "--out", str(work), "--ppu", f"{job['ppu']:.4f}",
               "--outline-px", f"{job['outline']:.3f}"]
        if job["clips"]:
            cmd += ["--clips", job["clips"]]
        if job["stills"]:
            cmd += ["--stills", job["stills"]]
        print(">", job["clips"] or "-", job["stills"] or "-", f"ppu {job['ppu']:.1f}", flush=True)
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        for line in res.stdout.splitlines():
            if line.startswith(("CLIP", "STILL", "WARN", "Traceback", "Error")):
                print("  ", line)
        if res.returncode != 0 or "Traceback" in res.stdout + res.stderr:
            print(res.stdout[-3000:], res.stderr[-3000:])
            return 1
    from post import main as post_main  # noqa: E402  (sibling module)
    if post_main(["--renders", str(work)]) != 0:
        return 1
    if args.only_render:
        return 0
    from pack import main as pack_main  # noqa: E402  (sibling module)
    return pack_main(["--renders", str(work), "--art-root", args.art_root])


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    sys.exit(main())
