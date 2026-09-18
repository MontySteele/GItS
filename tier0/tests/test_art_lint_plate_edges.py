"""L13 measures the CANVAS EDGE of a plate, and the thresholds mean what they say.

[USER] on 0.2.3674 (2026-09-17): "many of our images have weirdly clipped
assets around the edge of the image that weren't obvious on a contact sheet but
do show up as the edge of the in-game model." A contact sheet draws every plate
inside a rectangle, so a figure sliced flat against the canvas reads as a
FRAME; in the game there is no frame and the same flat edge reads as the
model's own silhouette.

The three properties the 122-plate bill depends on:

  1. a figure touching an edge for 30px FLAGS (the defect);
  2. a figure with a 4px transparent margin all round does NOT (the fix
     `contain` produces);
  3. a 3px stray at a corner does NOT (a speck is not a clipped model, and a
     rule that fired on one would flag every plate with an FX mote).

Synthetic 240x280 fixtures, so this runs on a bare clone: `ImageGen/` is
gitignored Tier F and a worktree has none of it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

pytest.importorskip("PIL", reason="the edge measurement opens a PNG")

from PIL import Image  # noqa: E402

import art_lint  # noqa: E402

W, H = 240, 280
FIGURE = (200, 120, 60, 255)


def plate(tmp_path, box, name="p.png"):
    """A 240x280 transparent plate with one opaque rectangle at `box`."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste(FIGURE, box)
    out = tmp_path / name
    img.save(out)
    return out


def test_figure_touching_the_left_edge_for_30px_flags(tmp_path):
    # x0 == 0: the figure is cut flat against the canvas for 30 rows.
    flagged = art_lint.plate_edges(plate(tmp_path, (0, 100, 80, 130)))
    assert set(flagged) == {"left"}
    run, frac = flagged["left"]
    assert run == 30
    assert frac == pytest.approx(30 / H)


def test_a_four_pixel_margin_all_round_is_clean(tmp_path):
    # What `contain` produces: the figure fits, so no edge is opaque at all.
    assert art_lint.plate_edges(plate(tmp_path, (4, 4, W - 4, H - 4))) == {}


def test_a_three_pixel_corner_stray_is_not_a_clip(tmp_path):
    # 3px is under EDGE_RUN_PX on both edges it touches, and 3/240 and 3/280
    # are both under EDGE_FRACTION -- a mote, not a sliced model.
    assert art_lint.plate_edges(plate(tmp_path, (0, 0, 3, 3))) == {}


def test_a_broken_edge_flags_on_FRACTION_even_with_short_runs(tmp_path):
    """The second threshold earns its place: many short runs, no long one.

    A spray of FX crossing the edge never makes a 12px run, and the run test
    alone would call it clean while a tenth of the edge is opaque.
    """
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for x in range(0, 120, 4):          # 30 runs of 2px = 60px of 240 = 25%
        img.paste(FIGURE, (x, 0, x + 2, 1))
    out = tmp_path / "broken.png"
    img.save(out)
    flagged = art_lint.plate_edges(out)
    assert set(flagged) == {"top"}
    run, frac = flagged["top"]
    assert run < art_lint.EDGE_RUN_PX
    assert frac >= art_lint.EDGE_FRACTION


def test_alpha_below_the_opaque_threshold_does_not_count(tmp_path):
    """Soft FX feathering off the edge is not a model silhouette."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    faint = (200, 120, 60, art_lint.EDGE_ALPHA_OPAQUE - 1)
    img.paste(faint, (0, 0, 1, H))
    out = tmp_path / "faint.png"
    img.save(out)
    assert art_lint.plate_edges(out) == {}


def test_thresholds_are_the_documented_numbers():
    """Pin the constants: the bill in the PR quotes these three."""
    assert art_lint.EDGE_ALPHA_OPAQUE == 40
    assert art_lint.EDGE_RUN_PX == 12
    assert art_lint.EDGE_FRACTION == 0.10


def test_the_lint_skips_when_the_art_tree_is_absent(tmp_path, capsys):
    """CI has no ImageGen. A skip with a note, never a failure on a runner."""
    rows = [{"asset_id": "portrait_x", "out": art_lint.EDGE_PLATE_PREFIX + "x.png",
             "focus": "cut"}]
    assert art_lint.edge_clipping(rows, art_root=tmp_path) == []
    assert "L13 SKIP" in capsys.readouterr().out


def test_pending_repick_entries_are_plate_rows():
    """Rot guard on the DEBT set's other end: an id nobody plans is dead."""
    from art_fetch import read_plan
    plates = {r["asset_id"] for r in read_plan()
              if r["out"].startswith(art_lint.EDGE_PLATE_PREFIX)}
    stale = sorted(art_lint.PENDING_EDGE_REPICK - plates)
    assert not stale, f"PENDING_EDGE_REPICK names non-plate rows: {stale}"
