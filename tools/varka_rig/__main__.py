"""Varka's combat and merchant scenes: generate or check.

    python -m tools.varka_rig gen            # write combat.tscn + merchant_character.tscn
    python -m tools.varka_rig gen --check    # exit 1 if either scene is stale

Needs no art and no engine: the scenes are text from varka.yaml and the
committed manifest tools/char_render/varka_frames.json.
"""
from __future__ import annotations

import argparse
import sys

from . import rig


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tools.varka_rig")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    stale = 0
    for path, text in ((rig.SCENE, rig.render_scene()), (rig.MERCHANT_SCENE, rig.render_merchant_scene())):
        if args.check:
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != text:
                print(f"STALE: {path} differs from the generator; run `python -m tools.varka_rig gen`.")
                stale = 1
            else:
                print(f"{path.name} is current.")
            continue
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {path.relative_to(rig.ROOT)} ({len(text)} bytes)")
    return stale


if __name__ == "__main__":
    sys.exit(main())
