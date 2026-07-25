"""Framing math for the per-character still surfaces (tools/char_stills.py).

The B4 centring rule -- frame off the ALPHA BBOX, never off the image frame --
was a [USER] verdict, and it now has two callers (Furina, Kokomi). A rule with
two callers and no test is a rule that drifts on the next edit.

Most of these are SYNTHETIC: they build their own subject-on-a-plate rather
than reading art. Tier F art is gitignored, so a fresh clone has none of it,
and a test that reads it reports the machine rather than the code (the lesson
already recorded in test_art_coverage). The one test that does touch real art
skips when it is absent.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from tier0.content import loader

REPO = Path(loader.__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

np = pytest.importorskip("numpy")
PIL = pytest.importorskip("PIL")
from PIL import Image  # noqa: E402

import char_stills  # noqa: E402


def subject_on_transparent(size=(400, 600), body=(150, 60, 250, 560),
                           extra=None):
    """A figure-shaped blob, optionally with a decoration off to one side."""
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    px = im.load()
    for x in range(body[0], body[2]):
        for y in range(body[1], body[3]):
            px[x, y] = (200, 180, 220, 255)
    if extra:
        for x in range(extra[0], extra[2]):
            for y in range(extra[1], extra[3]):
                px[x, y] = (0, 200, 255, 255)
    return im


def test_alpha_bbox_ignores_the_frame():
    im = subject_on_transparent()
    assert char_stills.alpha_bbox(im) == (150, 60, 250, 560)


def test_alpha_bbox_rejects_a_render_with_no_alpha():
    """The failure mode that made Kokomi need a cut in the first place.

    A flattened render has full-frame alpha, so every framing rule silently
    degrades to frame-centring -- the B4 bug, reintroduced by the source. It
    must not degrade silently, but a fully opaque image is a legal bbox, so
    the guard is on the EMPTY case; the opaque case is caught by the caller
    cutting first. Assert the empty case raises rather than returning junk.
    """
    with pytest.raises(ValueError):
        char_stills.alpha_bbox(Image.new("RGBA", (10, 10), (0, 0, 0, 0)))


def test_head_crop_bbox_centring_is_pulled_off_the_head_by_decoration():
    """Why centre_on='head' had to exist.

    Kokomi's Portrait sweeps a fin right and floats a fish beside her hand,
    which drags the bbox midpoint 275px off her head at source scale. This
    reproduces that geometry in miniature and asserts the OLD behaviour is
    genuinely wrong, so the new mode is not solving an imaginary problem.
    """
    # Body centred on x=200; decoration far to the right, in the head band.
    im = subject_on_transparent(extra=(300, 70, 390, 130))
    x0, _, x1, _ = char_stills.alpha_bbox(im)
    assert (x0 + x1) // 2 > 210, "decoration must actually shift the bbox mid"

    bbox_crop = char_stills.head_crop(im, 132, 195, head_frac=0.3, centre_on="bbox")
    head_crop = char_stills.head_crop(im, 132, 195, head_frac=0.3, centre_on="head")

    def body_centre(crop):
        """Mean column of BODY-coloured pixels, in crop space."""
        a = np.asarray(crop)
        mask = (a[..., 3] > 8) & (a[..., 2] > 200) & (a[..., 1] < 200)
        return a.shape[1] / 2 if not mask.any() else np.nonzero(mask)[1].mean()

    off_bbox = abs(body_centre(bbox_crop) - 66)
    off_head = abs(body_centre(head_crop) - 66)
    assert off_head < off_bbox, (off_head, off_bbox)


def test_head_crop_rejects_an_unknown_centring():
    with pytest.raises(ValueError):
        char_stills.head_crop(subject_on_transparent(), 88, 88, centre_on="middle")


def test_fit_bottom_anchors_and_horizontally_centres():
    im = subject_on_transparent()
    out = char_stills.fit(im, 240, 280)
    a = np.asarray(out)[..., 3] > 8
    ys, xs = np.nonzero(a)
    assert ys.max() == 279, "feet must sit on the bottom edge"
    assert abs((xs.min() + xs.max()) / 2 - 119.5) <= 1


def test_locked_variant_keeps_the_portrait_alpha_and_darkens():
    portrait = char_stills.head_crop(subject_on_transparent(), 132, 195)
    locked = char_stills.locked_variant(portrait)
    assert locked.size == portrait.size
    assert (np.asarray(locked)[..., 3] == np.asarray(portrait)[..., 3]).all(), \
        "identical framing is the whole point of deriving locked from portrait"
    lit = np.asarray(portrait.convert("L"), float)
    dim = np.asarray(locked.convert("L"), float)
    assert dim.mean() < lit.mean()


def test_cutout_from_plate_keeps_enclosed_white():
    """Connectivity, not colour.

    Kokomi wears white stockings and a white kimono panel. A global white key
    punches holes straight through her, so background is defined as near-white
    REACHABLE FROM THE BORDER. Here: a dark ring with a white centre -- the
    centre must survive, the surrounding plate must not.
    """
    im = Image.new("RGB", (120, 120), (255, 255, 255))
    px = im.load()
    for x in range(30, 90):
        for y in range(30, 90):
            edge = x in (30, 89) or y in (30, 89) or not (34 < x < 85 and 34 < y < 85)
            px[x, y] = (20, 20, 20) if edge else (255, 255, 255)

    cut = char_stills.cutout_from_plate(im)
    a = np.asarray(cut)[..., 3]
    assert a[5, 5] == 0, "outer plate must be keyed out"
    assert a[60, 60] == 255, "enclosed white must survive the key"
    assert a[31, 60] == 255, "the dark ring itself must survive"


def test_cutout_from_plate_reaches_concave_pockets():
    """A four-ray or scanline-only fill leaves concave pockets opaque.

    The gap between an arm and a torso is exactly such a pocket, and a white
    blob left there reads in-game as a rendering artifact rather than as art.
    """
    im = Image.new("RGB", (120, 120), (255, 255, 255))
    px = im.load()
    # A "C" opening to the right: its interior is white and border-reachable
    # only by going around through the mouth.
    for x in range(20, 100):
        for y in range(20, 100):
            if x < 40 or y < 40 or y >= 80:
                px[x, y] = (10, 10, 10)
    cut = char_stills.cutout_from_plate(im)
    a = np.asarray(cut)[..., 3]
    assert a[60, 70] == 0, "the pocket inside the C must be reached and keyed"


FURINA_UI = REPO / "ImageGen" / "images" / "furina" / "ui"


@pytest.mark.skipif(not (FURINA_UI / "select_portrait.png").exists(),
                    reason="Tier F art is gitignored; only meaningful where it has been generated")
def test_furina_stills_are_reproducible():
    """Re-running her generator must not move a pixel.

    char_stills.py was extracted FROM gen_furina_stills.py, and her six
    surfaces carry a [USER] verdict. Any future edit to the shared framing
    math has to prove it left the approved art alone.
    """
    import hashlib

    def digest():
        parts = sorted(FURINA_UI.glob("*.png")) + \
            [REPO / "ImageGen/images/furina/model/combat_model.png"]
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in parts}

    before = digest()
    res = subprocess.run([sys.executable, str(REPO / "tools" / "gen_furina_stills.py")],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    assert digest() == before
