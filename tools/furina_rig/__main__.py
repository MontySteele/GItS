"""Furina's combat, merchant and guest scenes: generate or check.

    python -m tools.furina_rig gen            # write every scene (hers, the guests', their effects')
    python -m tools.furina_rig gen --check    # exit 1 if any scene is stale

Needs no art and no engine: the scenes are text from furina.yaml and the
committed manifest tools/char_render/furina_frames.json.
"""
from __future__ import annotations

import argparse
import sys

from . import guest_fx, guests, rig


def scenes() -> list[tuple]:
    out = [(rig.SCENE, rig.render_scene()), (rig.MERCHANT_SCENE, rig.render_merchant_scene()),
           (rig.SELECT_SCENE, rig.render_select_scene())]
    out += [(guests.scene_path(name), text) for name, text in guests.render_guests().items()]
    out += [(guest_fx.scene_path(name), text) for name, text in guest_fx.render_guest_fx().items()]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tools.furina_rig")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    stale = 0
    for path, text in scenes():
        if args.check:
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != text:
                print(f"STALE: {path} differs from the generator; run `python -m tools.furina_rig gen`.")
                stale = 1
            else:
                print(f"{path.name} is current.")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {path.relative_to(rig.ROOT)} ({len(text)} bytes)")
    return stale


if __name__ == "__main__":
    sys.exit(main())
