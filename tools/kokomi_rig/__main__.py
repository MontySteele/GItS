"""Kokomi's combat and merchant scenes: generate or check.

    python -m tools.kokomi_rig gen            # write both scenes
    python -m tools.kokomi_rig gen --check    # exit 1 if either scene is stale

Needs no art and no engine: the scenes are text from kokomi.yaml and the
committed manifest tools/char_render/kokomi_frames.json. Until her first
render writes that manifest there is nothing to generate: `gen` says so and
exits 2, `gen --check` says so and passes (her layer-cut rig still ships).
"""
from __future__ import annotations

import argparse
import sys

from . import rig


def scenes() -> list[tuple]:
    return [(rig.SCENE, rig.render_scene()), (rig.MERCHANT_SCENE, rig.render_merchant_scene())]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tools.kokomi_rig")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    if not rig.FRAMES.exists():
        print(f"{rig.FRAMES.name} does not exist yet: render and pack her first "
              "(tools/char_render/build.py --char kokomi).")
        return 0 if args.check else 2
    stale = 0
    for path, text in scenes():
        if args.check:
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != text:
                print(f"STALE: {path} differs from the generator; run `python -m tools.kokomi_rig gen`.")
                stale = 1
            else:
                print(f"{path.name} is current.")
            continue
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {path.relative_to(rig.ROOT)} ({len(text)} bytes)")
    return stale


if __name__ == "__main__":
    sys.exit(main())
