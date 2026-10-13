"""Klee mesh rig: generate, check, extract, verify, render.

    python -m tools.klee_rig gen                    # write combat.tscn + merchant_character.tscn
    python -m tools.klee_rig gen --check            # exit 1 if either scene is stale
    python -m tools.klee_rig extract [--art-root <main checkout>] [--check]
    python -m tools.klee_rig verify [--art-root <main checkout>] [--godot]
    python -m tools.klee_rig render --out <dir> [--art-root <main checkout>]

`gen`, `gen --check` and `verify` without flags need no art and no engine.
`extract` and `verify` coverage read the combat layer PNGs under
`<art-root>/ImageGen/images/model/layers/combat` (a worktree passes the main
checkout). `verify --godot` and `render` run MegaDot (tools/build_pck.ps1's
editor), `render` with a window.
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
    e = sub.add_parser("extract")
    e.add_argument("--art-root", default=str(rig.ROOT))
    e.add_argument("--check", action="store_true")
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
        for path, text in ((rig.SCENE, rig.render_scene()), (rig.MERCHANT_SCENE, rig.render_merchant_scene())):
            if args.check:
                current = path.read_text(encoding="utf-8") if path.exists() else ""
                if current != text:
                    print(f"STALE: {path} differs from the generator; run `python -m tools.klee_rig gen`.")
                    stale = 1
                else:
                    print(f"{path.name} is current.")
                continue
            path.write_text(text, encoding="utf-8", newline="\n")
            print(f"wrote {path.relative_to(rig.ROOT)} ({len(text)} bytes)")
        return stale

    if args.cmd == "extract":
        from . import cells

        data = cells.dump(cells.extract(rig.load_spec(), Path(args.art_root)))
        if args.check:
            current = rig.CELLS.read_text(encoding="utf-8")
            if current != data:
                print("STALE: klee_cells.json differs from the art; run `extract`.")
                return 1
            print("klee_cells.json matches the art.")
            return 0
        rig.CELLS.write_text(data, encoding="utf-8", newline="\n")
        print(f"wrote {rig.CELLS.relative_to(rig.ROOT)}")
        return 0

    if args.cmd == "verify":
        from . import verify

        return verify.main(Path(args.art_root), args.godot, args.work)

    if args.cmd == "render":
        from . import render

        return render.main(Path(args.art_root), Path(args.out), args.frames)
    return 2


if __name__ == "__main__":
    sys.exit(main())
