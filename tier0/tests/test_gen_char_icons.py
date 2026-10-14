"""tools/gen_char_icons.py: the top-bar icons match the base game's canvas.

The base cast's `images/ui/top_panel/character_icon_<char>.png` are 85x85 with
a ~4px transparent margin (measured out of SlayTheSpire2.pck, 2026-10-13; the
tool's docstring has the numbers). Ours were 88x88 squares running to every
edge. The synthetic tests run anywhere; the real-art test skips when the
gitignored ImageGen/ sources are absent, as every Tier F test does.
"""
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import gen_char_icons as gci  # noqa: E402

BASE_CANVAS = 85


def _synthetic_source():
    """An opaque block standing in for a portrait cutout."""
    im = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
    im.paste((200, 120, 90, 255), (50, 20, 350, 400))
    return im


def _spec():
    return gci.Icon(source="x.png", out="y.png", source_size=(400, 400),
                    source_bbox=(50, 20, 350, 400),
                    face_cx=200, crown_y=40, chin_y=200)


def test_canvas_is_the_base_games():
    assert gci.CANVAS == BASE_CANVAS


def test_icon_has_base_dimensions_and_margin():
    icon = gci.build_icon(_synthetic_source(), _spec())
    assert icon.size == (BASE_CANVAS, BASE_CANVAS)
    a = np.asarray(icon)[..., 3]
    # The base icons never touch the canvas sides; ours keep the same margin
    # so the outline halo (r ~4.5px) is not clipped.
    margin = 4
    assert a[:margin, :].max() == 0 and a[-margin:, :].max() == 0
    assert a[:, :margin].max() == 0 and a[:, -margin:].max() == 0
    # And the disc is filled where the source is opaque.
    assert a[BASE_CANVAS // 2, BASE_CANVAS // 2] == 255


def test_unknown_character_is_refused(capsys):
    assert gci.main(["--chars", "nobody", "--art-root", str(ROOT)]) == 2


def test_all_four_characters_have_a_row():
    # Furina joined 2026-10-13, cut from her model's select close-up (#1241).
    assert {"klee", "varka", "kokomi", "furina"} <= set(gci.CHARS)


def test_a_re_rendered_source_is_refused(tmp_path, capsys):
    # Landmarks are pinned to the source they were measured on; a source of
    # another size or alpha bbox fails with "re-measure", never reframes.
    spec = gci.CHARS["furina"]
    src = tmp_path / spec.source
    src.parent.mkdir(parents=True)
    _synthetic_source().save(src)
    assert gci.main(["--chars", "furina", "--art-root", str(tmp_path),
                     "--out-root", str(tmp_path / "out")]) == 1
    assert "re-measure" in capsys.readouterr().err
    assert not (tmp_path / "out" / spec.out).exists()


def test_one_producer_per_icon():
    from tools import art_lint
    for name, spec in gci.CHARS.items():
        assert art_lint.GENERATOR_OWNED[spec.out] == "gen_char_icons.py", name
    for stills in ("gen_kokomi_stills.py", "gen_varka_stills.py",
                   "gen_furina_stills.py"):
        text = (ROOT / "tools" / stills).read_text(encoding="utf-8")
        assert '"char_icon.png"' not in text, stills
    plan = (ROOT / "art" / "plan.tsv").read_text(encoding="utf-8")
    live = [l for l in plan.splitlines() if not l.startswith("#")]
    for spec in gci.CHARS.values():
        assert not any(f"\t{spec.out}\t" in l for l in live), spec.out


_HAVE_ART = [n for n, s in gci.CHARS.items() if (ROOT / s.source).exists()]


@pytest.mark.skipif(not _HAVE_ART, reason="ImageGen/ sources absent (Tier F)")
@pytest.mark.parametrize("name", _HAVE_ART)
def test_real_icons_have_base_dimensions(tmp_path, name):
    rc = gci.main(["--chars", name, "--art-root", str(ROOT),
                   "--out-root", str(tmp_path)])
    if rc == 1:
        # The source predates (or postdates) the art its landmarks were
        # measured on, e.g. Varka's select close-up before PR #1238's re-render.
        pytest.skip(f"{name}: source differs from the measured one")
    assert rc == 0
    icon = Image.open(tmp_path / gci.CHARS[name].out)
    assert icon.size == (BASE_CANVAS, BASE_CANVAS), name
    a = np.asarray(icon.convert("RGBA"))[..., 3]
    assert a[:, :4].max() == 0 and a[:, -4:].max() == 0, name
