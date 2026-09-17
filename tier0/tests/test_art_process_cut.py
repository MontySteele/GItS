"""`mode=cut` removes the backdrop and nothing but the backdrop.

The Teyvat still portraits are cut out of `Category:Enemy Archive Images`
captures, which are opaque screenshots (`docs/current/research/
teyvat-portrait-sources-2026-09-16.md` sec.1), while
`docs/current/operations/media.md` sec.3 requires RGBA because the portrait
composites over the arena rather than over a plate. `art_process.cut` is the
step that bridges those two facts, and these tests pin the five properties the
81-row bill depends on:

  1. alpha lands where the FIGURE is and not where the backdrop is;
  2. a dark patch INSIDE the figure survives even though it is backdrop
     coloured -- the reason the matte is a border-reachable flood fill and not
     a global colour threshold;
  3. a faint star in the backdrop does NOT survive as a speck -- the reason
     for the island prune, without which the alpha bbox is the whole frame and
     the content trim silently does nothing (measured on four of five real
     samples before the prune existed);
  4. an ENCLOSED pocket of backdrop -- sky trapped inside the silhouette,
     which border-reachability cannot reach by construction -- IS removed once
     it is large, while a small keyed region is NOT, which is what keeps the
     pocket pass from re-opening the hole property 2 closes;
  5. a source that ALREADY carries a matte is passed through rather than
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


def _plate(*, hole=0, star=False, size=(W, H)):
    """A flat-ish Archive capture: vertical gradient, centred figure block.

    `hole` paints a square of BACKDROP-coloured pixels fully enclosed by the
    figure, `hole` pixels on a side. Size is the only difference between the
    two cases that matter, and that is the point: a small one is a body's own
    shadow and must survive, a large one is sky trapped inside the silhouette
    and must go. Both are unreachable from the border, so the first pass
    cannot tell them apart and the second pass decides by area.
    """
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
    if hole:
        for y in range(100, 100 + hole):
            for x in range(100, 100 + hole):
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


def test_a_small_backdrop_coloured_patch_inside_the_figure_survives():
    """Why the matte is REACHABILITY and not a colour threshold.

    The shadow patch is within tolerance of the corner colour, so a global
    test would key a hole straight through the body. It is not connected to
    the border, so the first pass leaves it alone -- and it is well under the
    pocket threshold (12x12 = 144 px against a 230 px floor at this frame
    size), so the second pass leaves it alone too.
    """
    matte = art_process._backdrop_alpha(_plate(hole=12),
                                        art_process.CUT_TOLERANCE)
    assert matte.getpixel((105, 105)) == 255
    assert matte.getpixel((2, 2)) == 0


def test_a_large_enclosed_pocket_of_backdrop_is_removed():
    """The pocket pass, found by eye on the first 81-row run.

    `hilichurl_fighter` kept a navy starfield block in the gap between its
    raised club and its head and `hydro_abyss_mage` kept a dark arc at the
    bottom edge: real backdrop, enclosed by the silhouette, unreachable from
    the border. 44x44 here is 1936 px, well over the 0.4% floor.
    """
    matte = art_process._backdrop_alpha(_plate(hole=44),
                                        art_process.CUT_TOLERANCE)
    assert matte.getpixel((120, 120)) == 0      # the pocket went
    assert matte.getpixel((80, 60)) == 255      # the body around it did not


def test_the_pocket_threshold_is_a_row_level_knob():
    """A row may raise the floor above a pocket to keep it, or lower it."""
    plate = _plate(hole=44)
    kept = art_process._backdrop_alpha(plate, art_process.CUT_TOLERANCE,
                                       pocket_frac=0.2)
    assert kept.getpixel((120, 120)) == 255
    dropped = art_process._backdrop_alpha(plate, art_process.CUT_TOLERANCE,
                                          pocket_frac=0.001)
    assert dropped.getpixel((120, 120)) == 0


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


def test_the_spec_column_parses_tolerance_fit_focus_and_pocket():
    tol, pock = art_process.CUT_TOLERANCE, art_process.CUT_POCKET_FRAC
    chr_, fig = art_process.CUT_CHROMA, "main"
    assert art_process._cut_spec("cut") == (tol, "cover", "top", pock, chr_, fig)
    assert art_process._cut_spec("cut@64") == (64.0, "cover", "top", pock, chr_, fig)
    assert art_process._cut_spec("cut@64/center") == (
        64.0, "cover", "center", pock, chr_, fig)
    assert art_process._cut_spec("cut/contain") == (
        tol, "contain", "center", pock, chr_, fig)
    assert art_process._cut_spec("cut@64/top:0.01") == (
        64.0, "cover", "top", 0.01, chr_, fig)
    assert art_process._cut_spec("cut:0") == (tol, "cover", "top", 0.0, chr_, fig)
    # A bare focus keyword is the "default matte, this framing" spelling.
    assert art_process._cut_spec("center") == (
        tol, "cover", "center", pock, chr_, fig)


def test_the_spec_column_takes_the_keyword_options_too():
    """`;key=value` is how the grammar grows without a fifth punctuation mark."""
    tol, pock = art_process.CUT_TOLERANCE, art_process.CUT_POCKET_FRAC
    assert art_process._cut_spec("cut;figure=all") == (
        tol, "cover", "top", pock, art_process.CUT_CHROMA, "all")
    assert art_process._cut_spec("cut@70;chroma=60") == (
        70.0, "cover", "top", pock, 60.0, "main")
    assert art_process._cut_spec("cut@50/center:0.01;chroma=20;figure=all") == (
        50.0, "cover", "center", 0.01, 20.0, "all")
    with pytest.raises(SystemExit):
        art_process._cut_spec("cut;figure=biggest")
    with pytest.raises(SystemExit):
        art_process._cut_spec("cut;nonesuch=1")


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


# --------------------------------------------------------------------------
# The three defects [USER] found on the 2026-09-17 veto sheet, one fixture
# each. All three are properties of the KEY, not of the framing, so each is
# read off `_backdrop_alpha` directly.
# --------------------------------------------------------------------------

BODY_BLACK = (18, 20, 34)   # a black body in shade: dark, and NEARLY NEUTRAL


def _plate_with_black_limb():
    """Backdrop gradient, gold body, and a black limb reaching the LEFT edge.

    The limb is the defect that caused most of the rejections. Its colour is
    32 RGB from the corner navy, i.e. inside the old flat `cut@48` key, and it
    touches the frame edge, so border-reachability could not save it either:
    the flood walked straight up the limb and hollowed the body out
    (`frostarm_lawachurl`, the Rifthounds, the Fatui). It is NOT navy, though
    -- its blue chroma is ~15 where the backdrop's is ~50 -- which is what the
    chroma gate reads.
    """
    img = _plate()
    px = img.load()
    for y in range(110, 140):
        for x in range(0, FIG[0] + 10):
            px[x, y] = BODY_BLACK + (255,)
    return img


def test_a_black_body_reachable_from_the_border_survives():
    matte = art_process._backdrop_alpha(_plate_with_black_limb())
    assert matte.getpixel((5, 125)) == 255      # limb at the frame edge
    assert matte.getpixel((60, 125)) == 255     # limb mid-way in
    assert matte.getpixel((120, 120)) == 255    # and the body it feeds
    assert matte.getpixel((5, 30)) == 0         # sky above it still goes
    assert matte.getpixel((5, 220)) == 0        # and below


def _plate_with_bubble():
    """A bright ring enclosing backdrop haze, with a dark face inside it.

    `electro_abyss_mage`: the pocket pass removed the haze inside his shield
    bubble by AREA, and his face went with it because a face is dark. The face
    here is the same near-neutral black as the limb above; the haze is the
    backdrop's own colour.
    """
    img = _plate()
    px = img.load()
    for y in range(H):
        for x in range(W):
            dx, dy = x - 120, y - 120
            d2 = dx * dx + dy * dy
            if d2 > 95 ** 2:
                continue
            if d2 > 80 ** 2:
                px[x, y] = FIGURE + (255,)            # the ring
            else:
                px[x, y] = BACKDROP_TOP + (255,)      # haze inside it
    for y in range(112, 132):
        for x in range(112, 132):
            px[x, y] = BODY_BLACK + (255,)            # the face
    return img


def test_the_pocket_pass_takes_the_haze_and_leaves_the_face():
    matte = art_process._backdrop_alpha(_plate_with_bubble())
    assert matte.getpixel((120, 122)) == 255    # the eyes are still there
    assert matte.getpixel((120, 33)) == 255     # ...and so is the ring
    assert matte.getpixel((120, 170)) == 0      # haze below the face: gone
    assert matte.getpixel((2, 2)) == 0          # and the sky outside


def _plate_group():
    """Three bodies on the backdrop: a big centred one and two flankers.

    The Archive slime captures are group shots, and cover-fitting the whole
    alpha bbox left the flanking bodies half in frame (`dendro_slime`).
    """
    w, h = 360, 240
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        row = tuple(round(a + (b - a) * t)
                    for a, b in zip(BACKDROP_TOP, BACKDROP_BOTTOM))
        for x in range(w):
            px[x, y] = row
    blobs = [(150, 60, 210, 190), (20, 120, 70, 180), (300, 120, 350, 180)]
    for x0, y0, x1, y1 in blobs:
        for y in range(y0, y1):
            for x in range(x0, x1):
                px[x, y] = FIGURE
    return img.convert("RGBA")


def test_figure_selection_keeps_the_main_body_and_drops_the_flankers():
    dropped = []
    matte = art_process._backdrop_alpha(_plate_group(), dropped=dropped)
    assert matte.getpixel((180, 120)) == 255    # the centre body stays
    assert matte.getpixel((45, 150)) == 0       # left flanker gone
    assert matte.getpixel((325, 150)) == 0      # right flanker gone
    assert len(dropped) == 2                    # ...and the run says so


def test_figure_all_keeps_every_body():
    """`figure=all` is the row-level escape (fatui_cryo_cicin_mage's cicins)."""
    dropped = []
    matte = art_process._backdrop_alpha(_plate_group(), figure="all",
                                        dropped=dropped)
    assert matte.getpixel((180, 120)) == 255
    assert matte.getpixel((45, 150)) == 255
    assert matte.getpixel((325, 150)) == 255
    assert dropped == []
