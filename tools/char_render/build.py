"""Render every surface of one kit from its official model, paint it and pack it: one command.

    python tools/char_render/build.py --char varka|furina|kokomi|yae --models <scratch>/models --work <scratch dir> \
        [--blender <blender.exe>] [--art-root <dir>] [--only-render]

The kit twin of tools/klee_render/build.py. The packs stay under the
operator's scratch models/ directory (never the repo: their terms forbid
redistribution). `--work` receives the raw renders (render.py), post.py
(tools/klee_render/post.py: the 2D half of style H1 + H3 lite, shared) paints
every frame and still, and pack.py writes <art-root>/ImageGen/images/<char>/...
and the manifest tools/char_render/<char>_frames.json. From a worktree, point
--art-root at a scratch art root and copy across only once reviewed
(operations/art.md: ImageGen lives only in the main checkout).

THE SCALE, in one place: combat_ppu() is chars.target_ppu over the rest
height measured on the model, so the figure stands at its canon height over
an adult (docs/current/LAW.md, "Scale by real heights"), drawn at 0.5. The
shop draws him at 1.7x (base merchant over combat scale) from a 1.5x
texture; the rest site at 1.33x (base 0.38 over 0.285) through BaseLib's 0.5
container; the select close-up and roster tile are rendered at SELECT_PPU.
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_spec = importlib.util.spec_from_file_location("char_render_chars", HERE / "chars.py")
CH = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CH)

BLENDER = r"C:\Users\Monty\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe"
#: The rest-pose height of each kit's model in units (import 0.08), measured
#: by render.py's SCALE line (bounding box of the body mesh), 2026-10-13.
#: Kokomi's (2026-10-14) was read off the PMX's vertices without Blender
#: (max - min of the rest-pose heights x IMPORT_SCALE), the same box: the
#: method gives Varka's and Furina's figures to four places. Yae's
#: (2026-10-14) the same way: 1.8057, her ears and hair ornament on top; her
#: select ppu keeps the close-up near the others' size (~2170 px of figure).
REST_HEIGHT = {"varka": 2.0468, "furina": 1.7224, "kokomi": 1.6261, "yae": 1.8057}
SELECT_PPU = {"varka": 1100.0, "furina": 1300.0, "kokomi": 1300.0, "yae": 1200.0}
#: each kit's combat clips (pack.py packs the same set) and its extra job
COMBAT_CLIPS = {"varka": "idle,idle_low,attack,cast,hurt,death,ascension",
                "furina": "idle,idle_low,attack,cast,hurt,death,rejoice",
                "kokomi": "idle,idle_low,attack,cast,hurt,death,ascension",
                "yae": "idle,idle_low,attack,cast,hurt,death"}
SELECT_OUTLINE = 7.0


def combat_ppu(char: str) -> float:
    return round(CH.target_ppu(char, REST_HEIGHT[char]), 2)


def jobs(char: str) -> list[dict]:
    ppu = combat_ppu(char)
    shop = ppu * 1.7 * 0.75
    rest = ppu * (0.38 / 0.285)
    o = CH.OUTLINE_PX
    out = [
        {"clips": COMBAT_CLIPS[char], "stills": "stance_a,stand", "ppu": ppu, "outline": o},
        {"clips": "merchant", "stills": "", "ppu": shop, "outline": o * shop / ppu},
        {"clips": "", "stills": "rest", "ppu": rest, "outline": o * rest / ppu},
        {"clips": "", "stills": "select,portrait", "ppu": SELECT_PPU[char], "outline": SELECT_OUTLINE},
    ]
    if char == "furina":
        # her eleven guest stars, one still each, at her px per inch
        # (chars.guest_ppu; the outline stays OUTLINE_PX texture px)
        out.append({"clips": "", "stills": "", "guests": ",".join(sorted(CH.GUESTS)), "ppu": ppu, "outline": o})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--char", default="varka", choices=sorted(REST_HEIGHT))
    ap.add_argument("--models", required=True, help="scratch models root (models/<char>/unpacked/...)")
    ap.add_argument("--work", required=True)
    ap.add_argument("--blender", default=BLENDER)
    ap.add_argument("--art-root", default=str(ROOT))
    ap.add_argument("--only-render", action="store_true", help="render and paint; do not pack")
    ap.add_argument("--skip-render", action="store_true", help="paint and pack what --work already holds")
    ap.add_argument("--jobs", default="", help="render only these jobs (indices into jobs(), e.g. 0,4)")
    args = ap.parse_args(argv)
    # Blender's lines carry Chinese bone names; a cp1252 console would crash
    # echoing them, so the echo is utf-8 and replaces what it cannot show
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)
    pick = {int(j) for j in args.jobs.split(",") if j}
    for n, job in enumerate([] if args.skip_render else jobs(args.char)):
        if pick and n not in pick:
            continue
        cmd = [args.blender, "-b", "--factory-startup", "-P", str(HERE / "render.py"), "--",
               "--char", args.char, "--models", args.models, "--out", str(work),
               "--ppu", f"{job['ppu']:.4f}", "--outline-px", f"{job['outline']:.3f}"]
        if job["clips"]:
            cmd += ["--clips", job["clips"]]
        if job["stills"]:
            cmd += ["--stills", job["stills"]]
        if job.get("guests"):
            cmd += ["--guests", job["guests"]]
        print(">", job["clips"] or "-", job["stills"] or job.get("guests") or "-", f"ppu {job['ppu']:.1f}", flush=True)
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        for line in res.stdout.splitlines():
            if line.startswith(("CLIP", "STILL", "WARN", "SCALE", "Traceback", "Error")):
                print("  ", line)
        if res.returncode != 0 or "Traceback" in res.stdout + res.stderr:
            print(res.stdout[-3000:], res.stderr[-3000:])
            return 1
    # post.py by its own name, appended so this directory's pack/render win:
    # its worker processes re-import it, so it must be importable, not exec'd
    sys.path.append(str(ROOT / "tools" / "klee_render"))
    import post  # noqa: E402
    if post.main(["--renders", str(work)]) != 0:
        return 1
    if args.only_render:
        return 0
    spec = importlib.util.spec_from_file_location("char_render_pack", HERE / "pack.py")
    pack = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pack)
    return pack.main(["--char", args.char, "--renders", str(work), "--art-root", args.art_root])


if __name__ == "__main__":
    sys.exit(main())
