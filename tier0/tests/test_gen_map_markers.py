"""The five map markers: one producer, the base slot, five distinct pins.

[USER], 2026-10-19: "I think all 5 should get pins." tools/gen_map_markers.py
draws each kit's 49x64 marker from its model-rendered select close-up; the
pixels need the gitignored art and are held by `--check` on the art-bearing
checkout. These hold what can break without art.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import art_lint  # noqa: E402
import gen_map_markers as gm  # noqa: E402


def test_every_kit_has_a_pin_and_one_producer():
    assert set(gm.CHARS) == {"klee", "varka", "furina", "kokomi", "yae"}
    for name, m in gm.CHARS.items():
        assert art_lint.GENERATOR_OWNED[m.out] == "gen_map_markers.py", name
        assert m.out.endswith("ui/map_marker.png"), name
    for stills in ("gen_kokomi_stills.py", "gen_varka_stills.py", "gen_furina_stills.py"):
        text = (ROOT / "tools" / stills).read_text(encoding="utf-8")
        assert '"map_marker.png"' not in text, stills


def test_the_pins_are_the_base_slot_and_five_distinct_colours():
    assert (gm.W, gm.H) == (49, 64)
    assert len({m.color.upper() for m in gm.CHARS.values()}) == 5


def test_the_pin_shape_is_a_disc_over_a_point_inside_the_canvas():
    m = gm.pin_mask()
    ys, xs = m.nonzero()
    margin = gm.HALO_PX * gm.SS
    assert xs.min() >= margin and xs.max() < gm.W * gm.SS - margin
    assert ys.min() >= margin and ys.max() < gm.H * gm.SS - margin
    # the point: the lowest rows are narrow, and centred
    low = xs[ys >= ys.max() - gm.SS]
    assert low.max() - low.min() < 2 * gm.SS
    assert abs((low.max() + low.min()) / 2 / gm.SS - gm.DISC_CX) < 1
