"""Klee's combat scene: generate, check, verify, render.

    python -m tools.klee_rig gen                    # write combat, merchant + select scenes
    python -m tools.klee_rig gen --check            # exit 1 if either scene is stale
    python -m tools.klee_rig verify [--art-root <main checkout>] [--godot]
    python -m tools.klee_rig render --out <dir> [--art-root <main checkout>]

`gen`, `gen --check` and `verify` without flags need no art and no engine.
`verify --godot` and `render` run MegaDot (tools/build_pck.ps1's editor) on
the frame sheets under `<art-root>/ImageGen/images/model/frames` (a worktree
passes the main checkout); `verify --godot` headless, `render` with a window.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import rig


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tools.klee_rig")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen")
    g.add_argument("--check", action="store_true")
    v = sub.add_parser("verify")
    v.add_argument("--art-root", default=str(rig.ROOT))
    v.add_argument("--godot", action="store_true")
    v.add_argument("--work", default=None, help="scratch dir for the engine project")
    r = sub.add_parser("render")
    r.add_argument("--art-root", default=str(rig.ROOT))
    r.add_argument("--out", required=True)
    r.add_argument("--frames", type=int, default=10)
    args = ap.parse_args(argv)

    if args.cmd == "gen":
        stale = 0
        for path, text in ((rig.SCENE, rig.render_scene()), (rig.MERCHANT_SCENE, rig.render_merchant_scene()),
                               (rig.SELECT_SCENE, rig.render_select_scene())):
            if args.check:
                current = path.read_text(encoding="utf-8") if path.exists() else ""
                if current != text:
                    print(f"STALE: {path} differs from the generator; run `python -m tools.klee_rig gen`.")
                    stale = 1
                else:
                    print(f"{path.name} is current.")
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
            print(f"wrote {path.relative_to(rig.ROOT)} ({len(text)} bytes)")
        return stale

    if args.cmd == "verify":
        from . import verify

        return verify.main(Path(args.art_root), args.godot, args.work)

    if args.cmd == "render":
        from . import render

        return render.main(Path(args.art_root), Path(args.out), args.frames)
    return 2


if __name__ == "__main__":
    sys.exit(main())
