"""Render and pack the Bake-Kurage's frame sheet: one command.

    python tools/kurage_render/build.py --work <scratch dir> [--art-root <dir>] [--blender <blender.exe>]

render.py (Blender, headless) builds the jellyfish and writes its raw frames
to --work; pack.py outlines and packs them into
<art-root>/ImageGen/images/kokomi/model/frames/kokomi_kurage.png and the
committed manifest tools/kurage_render/kurage_frames.json. Then
`python -m tools.kokomi_rig gen` writes bake_kurage.tscn from the manifest.
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BLENDER = r"C:\Users\Monty\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--art-root", default=str(ROOT))
    ap.add_argument("--blender", default=BLENDER)
    args = ap.parse_args(argv)
    res = subprocess.run([args.blender, "-b", "--factory-startup", "-P", str(HERE / "render.py"), "--",
                          "--out", args.work], capture_output=True, text=True, encoding="utf-8", errors="replace")
    for line in res.stdout.splitlines():
        if line.startswith(("CLIP", "Traceback", "Error")):
            print("  ", line)
    if res.returncode != 0 or "Traceback" in res.stdout + res.stderr:
        print(res.stdout[-3000:], res.stderr[-3000:])
        return 1
    spec = importlib.util.spec_from_file_location("kurage_pack", HERE / "pack.py")
    pack = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pack)
    return pack.main(["--renders", args.work, "--art-root", args.art_root])


if __name__ == "__main__":
    sys.exit(main())
