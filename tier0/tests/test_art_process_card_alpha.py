"""Card portraits are written WITHOUT an alpha channel, and lose no colour.

`EB-158`, defect 1. `art_process.process()` composites every `/cards/` output
onto the opaque `CARD_BG` -- so the alpha band it then saved was a constant
255 plane, roughly a quarter of the raw pixel data carrying no information, on
887 planned card rows. The fix is one `convert("RGB")`.

The claim that has to be tested is NOT "the file got smaller". It is that
NOTHING ELSE MOVED: a colour-managed or premultiplying conversion would shrink
the file and repaint every semi-transparent edge pixel, which is exactly the
kind of change that reaches a card frame without reaching a diff. So the test
composites the expected result by hand and compares pixel for pixel.

Runs on a bare clone: the fixture image is synthetic and `art_process.RAW` is
pointed at tmp_path, because `ImageGen/` and `art/raw/` are gitignored Tier F
and a worktree has neither.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

pytest.importorskip("PIL", reason="art_process needs Pillow to open anything")

from PIL import Image  # noqa: E402

import art_process  # noqa: E402
from art_fetch import rawname  # noqa: E402


TITLE = "Eb158 Synthetic Source.png"


def _row(out: str, mode: str = "contain") -> dict:
    return {
        "asset_id": "eb158_probe", "out": out, "w": 40, "h": 30,
        "mode": mode, "focus": "center", "pick": "auto", "rank": 1,
        "source": "png", "title": TITLE, "frame": None,
        "register": "item", "source_group": None,
    }


@pytest.fixture()
def raw_source(tmp_path, monkeypatch):
    """A source with REAL transparency, including partial alpha.

    Partial alpha is the load-bearing part of the fixture: a source that was
    either fully opaque or fully clear could not tell a correct composite from
    a premultiplying one.
    """
    src = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    for x in range(20):
        for y in range(20):
            src.putpixel((x, y), (10 + 7 * x, 200 - 3 * y, 128, y * 13 % 256))
    raw = tmp_path / "raw"
    raw.mkdir()
    src.save(raw / rawname(TITLE))
    monkeypatch.setattr(art_process, "RAW", raw)
    return src


def test_card_portrait_is_written_without_an_alpha_channel(raw_source, tmp_path):
    dest = tmp_path / "out" / "cards" / "klee" / "probe.png"
    assert art_process.process(_row("ImageGen/images/cards/klee/probe.png"), dest)
    with Image.open(dest) as got:
        assert got.mode == "RGB"
        assert got.size == (40, 30)


def test_dropping_alpha_changes_no_colour_value(raw_source, tmp_path):
    """Byte-for-byte on the colour planes, against a hand-built composite."""
    row = _row("ImageGen/images/cards/klee/probe.png")
    dest = tmp_path / "out" / "cards" / "klee" / "probe.png"
    assert art_process.process(row, dest)

    laid = art_process.contain(raw_source, row["w"], row["h"], art_process.CARD_BG)
    expected = Image.alpha_composite(
        Image.new("RGBA", laid.size, art_process.CARD_BG), laid)
    # Every pixel of that composite is opaque -- which is WHY the band can go.
    assert set(expected.getchannel("A").tobytes()) == {255}

    with Image.open(dest) as got:
        assert got.tobytes() == expected.convert("RGB").tobytes()


def test_icons_keep_their_alpha(raw_source, tmp_path):
    """The change is scoped to `/cards/`; a UI icon's transparency is real."""
    dest = tmp_path / "out" / "ui" / "probe.png"
    assert art_process.process(_row("ImageGen/images/ui/probe.png"), dest)
    with Image.open(dest) as got:
        assert got.mode == "RGBA"
        assert min(got.getchannel("A").tobytes()) == 0
