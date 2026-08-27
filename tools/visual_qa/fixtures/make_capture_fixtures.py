#!/usr/bin/env python3
"""Deterministic fixture captures for the contact-sheet gate.

No PNG binaries are committed. The sheet's determinism claim is only worth
something if its INPUTS are reproducible too, so the fixtures are generated
from this file: same code, same bytes, on any machine with the same Pillow.

Deliberately varied in the ways that break a naive assembler -- different
sizes, non-square aspect ratios, an image with transparency, one that is
larger than a cell and one that is smaller -- so "fits into the cell" and
"centred in the cell" are actually exercised rather than assumed.

    python tools/visual_qa/fixtures/make_capture_fixtures.py <out_dir>
"""

from __future__ import annotations

import sys
from pathlib import Path

#: name -> (width, height, rgba). Fixed, ordered, and NOT derived from a
#: random seed: a fixture whose content depends on a PRNG implementation is
#: one interpreter upgrade away from being a different fixture.
SPECS: tuple[tuple[str, int, int, tuple[int, int, int, int]], ...] = (
    ("idle_000.png", 64, 64, (200, 60, 60, 255)),
    ("idle_001.png", 200, 120, (60, 200, 90, 255)),
    ("attack_000.png", 40, 90, (70, 110, 220, 255)),
    ("hurt_000.png", 128, 128, (240, 200, 40, 128)),
    ("death_000.png", 300, 300, (180, 180, 190, 255)),
)


def write_fixtures(out_dir: Path) -> list[Path]:
    from PIL import Image

    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, width, height, colour in SPECS:
        image = Image.new("RGBA", (width, height), colour)
        # A corner marker, so a sheet built with the wrong orientation or a
        # flipped paste is visible to a human at a glance.
        for x in range(min(8, width)):
            for y in range(min(8, height)):
                image.putpixel((x, y), (255, 255, 255, 255))
        path = out_dir / name
        image.save(path, "PNG", optimize=False)
        written.append(path)
    return written


if __name__ == "__main__":                                # pragma: no cover
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "captures")
    for path in write_fixtures(target):
        print(path)
