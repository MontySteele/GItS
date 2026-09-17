"""`mode=cut` removes the backdrop and nothing but the backdrop.

The Teyvat still portraits are cut out of `Category:Enemy Archive Images`
captures, which are opaque screenshots (`docs/current/research/
teyvat-portrait-sources-2026-09-16.md` sec.1), while
`docs/current/operations/media.md` sec.3 requires RGBA because the portrait
composites over the arena rather than over a plate. `art_process.cut` is the
step that bridges those two facts, and these tests pin the four properties the
81-row bill depends on:

  1. alpha lands where the FIGURE is and not where the backdrop is;
  2. a dark patch INSIDE the figure survives even though it is backdrop
     coloured -- the reason the matte is a border-reachable flood fill and not
     a global colour threshold;
  3. a faint star in the backdrop does NOT survive as a speck -- the reason
     for the island prune, without which the alpha bbox is the whole frame and
     the content trim silently does nothing (measured on four of five real
     samples before the prune existed);
  4. a source that ALREADY carries a matte is passed through rather than
     re-cut.

Synthetic fixtures, so this runs on a bare clone: `art/raw/` and `ImageGen/`
are gitignored Tier F and a worktree has neither.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

pytest.importorskip("PIL", reason="art_process needs Pillow to open anything")
pytest.importorskip("numpy", reason="the cut matte is solved in numpy")

from PIL import Image  # noqa: E402

import art_process  # noqa: E402

BACKDROP_TOP = (3, 18, 63)
BACKDROP_BOTTOM = (8, 16, 45)
FIGURE = (230, 196, 96)      # a gold mek: nowhere near the navy backdrop
FIGURE_SHADOW = (6, 17, 55)  # ...and one patch of it that IS the backdrop
STAR = (210, 216, 240)

W = H = 240
FIG = (70, 40, 170, 200)     # left, top, right, bottom of the figure block


def _plate(*, shadow=False, star=False, size=(W, H)):
    """A flat-ish Archive capture: vertical gradient, centred figure block."""
    w, h = size
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        px_row = tuple(round(a + (b - a) * t)
                       for a, b in zip(BACKDROP_TOP, BACKDROP_BOTTOM))
        for x in range(w):
            px[x, y] = px_row
    for y in range(FIG[1], FIG[3]):
        for x in range(FIG[0], FIG[2]):
            px[x, y] = FIGURE
    if shadow:
        for y in range(90, 130):
            for x in range(90, 130):
                px[x, y] = FIGURE_SHADOW
    if star:
        # Two pixels of starfield out in the corner, far from the figure.
        px[20, 20] = STAR
        px[21, 20] = STAR
    return img.convert("RGBA")


def _alpha_at(img, xy):
    return img.getpixel(xy)[3]


def test_backdrop_becomes_transparent_and_the_figure_does_not():
    """The property the whole bill rests on, read off the matte itself."""
    matte = art_process._backdrop_alpha(_plate(), art_process.CUT_TOLERANCE)
    assert matte is not None
    assert matte.getpixel((2, 2)) == 0          # corner: backdrop
    assert matte.getpixel((W - 3, H - 3)) == 0  # other corner, other gradient end
    assert matte.getpixel((120, 120)) == 255    # middle of the figure


def test_a_backdrop_coloured_patch_inside_the_figure_survives():
    """Why the matte is REACHABILITY and not a colour threshold.

    The shadow patch is within tolerance of the corner colour, so a global
    test would key a hole straight through the body. It is not connected to
    the border, so the flood fill leaves it alone.
    """
    matte = art_process._backdrop_alpha(_plate(shadow=True),
                                        art_process.CUT_TOLERANCE)
    assert matte.getpixel((110, 110)) == 255
    assert matte.getpixel((2, 2)) == 0


def test_a_star_in_the_backdrop_is_not_kept_as_a_speck():
    """Why the island prune exists: a surviving star is a full-frame bbox."""
    matte = art_process._backdrop_alpha(_plate(star=True),
                                        art_process.CUT_TOLERANCE)
    assert matte.getpixel((20, 20)) == 0
    assert matte.getpixel((120, 120)) == 255


def test_cut_trims_to_the_figure_and_returns_rgba_at_the_asked_size():
    out = art_process.cut(_plate(star=True), 240, 280, "cut")
    assert out.mode == "RGBA"
    assert out.size == (240, 280)
    alpha = out.getchannel("A")
    # Trimmed to the figure and then cover-fitted, so the frame is (nearly)
    # all figure: the point is that the crop is not 100 px of dead backdrop.
    assert sum(alpha.tobytes()) / (240 * 280) > 200


def test_an_already_cut_source_is_passed_through_untouched():
    """`Enemy Ruin Guard.png` and the NPC portraits arrive with a real matte."""
    src = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for y in range(FIG[1], FIG[3]):
        for x in range(FIG[0], FIG[2]):
            src.putpixel((x, y), FIGURE + (255,))
    assert art_process._backdrop_alpha(src, art_process.CUT_TOLERANCE) is None
    out = art_process.cut(src, 240, 280, "cut")
    assert out.size == (240, 280)
    assert _alpha_at(out, (120, 140)) == 255


def test_the_spec_column_parses_tolerance_and_fit_focus():
    assert art_process._cut_spec("cut") == (art_process.CUT_TOLERANCE, "cover", "top")
    assert art_process._cut_spec("cut@64") == (64.0, "cover", "top")
    assert art_process._cut_spec("cut@64/center") == (64.0, "cover", "center")
    assert art_process._cut_spec("cut/contain") == (art_process.CUT_TOLERANCE,
                                                    "contain", "center")
    # A bare focus keyword is the "default matte, this framing" spelling.
    assert art_process._cut_spec("center") == (art_process.CUT_TOLERANCE,
                                               "cover", "center")


def test_a_hopeless_cut_is_flagged_rather_than_placed_in_silence():
    """An in-world screenshot (NPC Remus, NPC Katayoun) has no matte to find.

    The bill needs to hear about that on the contact sheet, so the run prints
    a flag instead of writing a plausible-looking opaque plate quietly.
    """
    noise = Image.new("RGB", (W, H))
    px = noise.load()
    for y in range(H):
        for x in range(W):
            px[x, y] = ((x * 7) % 256, (y * 11) % 256, (x * y) % 256)
    before = len(art_process.flags)
    art_process.cut(noise.convert("RGBA"), 240, 280, "cut")
    assert any("removed almost nothing" in f
               for f in art_process.flags[before:])
    del art_process.flags[before:]
