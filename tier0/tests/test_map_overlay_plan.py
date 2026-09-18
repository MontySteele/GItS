"""The Teyvat map overlay: the bill, the mask, and the revert that made room.

2026-09-17. [USER], on the shipped frame: *"the map is harder to read than the
normal Slay the Spire 2 map; I like the basic idea but perhaps we went off the
rails replacing the map background with Genshin images and we should instead try
to come up with a Genshin-themed map overlay that keeps the basic idea of the
map intact."*

Three things this file holds shut, each of which is silent on its own:

  * the REVERT. Eighteen plan rows and eighteen ledger rows stopped existing,
    and a single one left behind would put a location still back under the map
    nodes on one face while the other five looked right.
  * the BILL. Twelve rows replace them, two a face, and their shapes are load-
    bearing: the vignette must be authored at exactly the ground's 2035x1440 or
    its clear centre will not line up with the map it is covering, and the
    wordmark must be the 900x160 strip `MapOverlay.WordmarkSize` positions.
  * the MASK. "Transparent where the nodes are" is the whole design, and it is
    one arithmetic expression in `tools/art_process.vignette`. A sign error
    there produces a picture that looks fine on a contact sheet and is opaque
    over the middle of the map in the game.

The C# half -- the gate, the tint table, the never-throw discipline -- is
`klee-mod/KleeTests/TeyvatMapOverlayTests.cs`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PLAN = ROOT / "art" / "plan.tsv"
LEDGER = ROOT / "media" / "ACT.tsv"
OVERLAY_CS = ROOT / "klee-mod" / "KleeCode" / "Teyvat" / "MapOverlay.cs"

FACES = ("mondstadt", "liyue", "natlan", "inazuma", "fontaine", "sumeru")


def plan_rows() -> list[dict[str, str]]:
    """`art/plan.tsv` as dicts. Read the tolerant way every ledger reader is."""
    columns = ["asset_id", "out", "w", "h", "mode", "focus", "pick", "rank",
               "source", "wiki_title", "frame_pct", "register"]
    rows = []
    with PLAN.open("r", encoding="utf-8", newline="") as handle:
        for line in handle:
            line = line.rstrip("\r\n")
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < len(columns):
                parts += [""] * (len(columns) - len(parts))
            rows.append(dict(zip(columns, parts)))
    return rows


def ledger_rows() -> list[dict[str, str]]:
    with LEDGER.open("r", encoding="utf-8", newline="") as handle:
        lines = [line.rstrip("\r\n") for line in handle if line.strip()]
    header = lines[0].split("\t")
    return [dict(zip(header, line.split("\t"))) for line in lines[1:]]


# --------------------------------------------------------------------------
# the revert
# --------------------------------------------------------------------------

def test_no_plan_row_produces_a_map_ground_plate():
    """The eighteen `map_bgs` rows are gone, and none may come back quietly.

    The out-path is the assertion and not the asset id, because the defect this
    catches is a row re-added under any name: `ActModel.MapTopBgPath` derives
    from the act id, so ANY file at that path becomes the map ground again.
    """
    offenders = [r["out"] for r in plan_rows() if "teyvat/map_bgs/" in r["out"]]
    assert offenders == [], offenders


def test_no_ledger_row_records_a_map_ground_plate():
    offenders = [r["out"] for r in ledger_rows() if "teyvat/map_bgs/" in r["out"]]
    assert offenders == [], offenders


def test_the_generator_plans_no_map_path_either():
    """The other producer. One of the two reverting is not the revert."""
    from tools import gen_act_placeholders as gen

    assert [row for row in gen.plan() if "map_bgs" in row.res] == []


def test_the_pck_contract_no_longer_claims_a_face_map_ground():
    """A contract row with no producer is a build that fails on nothing."""
    from tools.visual_qa import contract

    fixture = ROOT / "tools" / "visual_qa" / "fixtures" / "sample.contract.txt"
    parsed = contract.parse(fixture.read_text(encoding="utf-8"))
    for face in FACES:
        assert not any(f"map_bgs/{face}/" in r for r in parsed.resource_set), face


def test_the_c_sharp_revert_sends_all_three_getters_back():
    """`ActMapBgPathPatch` must cover top, middle AND bottom.

    Two of three is the worst outcome available: the map draws two thirds of
    the base zone's wall and one third of nothing.
    """
    patch = (ROOT / "klee-mod" / "KleeCode" / "Teyvat" / "Patches"
             / "ActMapBgPathPatch.cs").read_text(encoding="utf-8")
    for getter in ("get_MapTopBgPath", "get_MapMidBgPath", "get_MapBotBgPath"):
        assert getter in patch, getter


# --------------------------------------------------------------------------
# the bill
# --------------------------------------------------------------------------

def test_every_face_has_a_wordmark_row_and_a_vignette_row():
    rows = {r["out"]: r for r in plan_rows()}
    for face in FACES:
        word = rows[f"ImageGen/images/teyvat/map/{face}_wordmark.png"]
        assert (word["w"], word["h"]) == ("900", "160"), face
        # `contain` and never `cover`: an emblem cropped to fill a 5.6:1 strip
        # is an emblem with its sides cut off.
        assert word["mode"] == "contain", face
        assert word["wiki_title"].startswith("Emblem "), face
        assert word["wiki_title"].endswith(" White.png"), face

        vig = rows[f"ImageGen/images/teyvat/map/{face}_vignette.png"]
        # The ground's own size, so the clear centre lines up with the map.
        assert (vig["w"], vig["h"]) == ("2035", "1440"), face
        assert vig["mode"] == "vignette", face
        # The GENSHIN IMPACT mark is burnt into the bottom-right of every one
        # of these stills; x0.42 is what spends the spare width off the right
        # (research/teyvat-act-art-sources-2026-09-17.md sec.1).
        assert vig["focus"] == "x0.42", face


def test_the_vignette_reuses_a_still_the_retired_map_rows_already_fetched():
    """Six new downloads, not twelve: the wordmarks only.

    Not thrift for its own sake -- every fetch is one more
    PLACEHOLDER-COPYRIGHTED row to replace before anything can be public, and
    the landscape the map's margin should show is the one the face's map middle
    already picked.
    """
    ledger = {r["out"]: r for r in ledger_rows()}
    for face in FACES:
        row = ledger[f"ImageGen/images/teyvat/map/{face}_vignette.png"]
        assert row["raw"].startswith("art/raw/"), face
        assert not row["raw"].startswith("art/raw/Emblem_"), face


def test_every_overlay_row_is_ledgered_with_its_terms():
    ledger = {r["out"]: r for r in ledger_rows()}
    for face in FACES:
        for surface in ("wordmark", "vignette"):
            row = ledger[f"ImageGen/images/teyvat/map/{face}_{surface}.png"]
            assert row["dressing"] == face
            assert row["surface"] == f"map_{surface}"
            # The pre-public pass is `grep PLACEHOLDER-COPYRIGHTED media/*.tsv`
            # and a row that forgets the column passes it silently.
            assert row["licence"] == "PLACEHOLDER-COPYRIGHTED", row["out"]
            assert row["origin"].startswith(
                "https://genshin-impact.fandom.com/wiki/File:"), row["out"]


def test_build_pck_packs_the_overlay_directory():
    """Pixels with no copy block never reach the pack."""
    script = (ROOT / "tools" / "build_pck.ps1").read_text(encoding="utf-8")
    assert r"teyvat\map'" in script


def test_the_c_sharp_paths_match_the_bill():
    """`MapOverlay` names `res://teyvat/map/<id>_{wordmark,vignette}.png`.

    The plan writes to `ImageGen/images/teyvat/map/` and `build_pck` copies
    that directory to `res://teyvat/map/`; if the reader spelled either half
    differently the overlay would stand down silently on every face, which
    looks exactly like the arm being off.
    """
    source = OVERLAY_CS.read_text(encoding="utf-8")
    assert '"res://teyvat/map/"' in source
    assert '"_wordmark.png"' in source
    assert '"_vignette.png"' in source
    assert "new(900, 160)" in source


# --------------------------------------------------------------------------
# the mask
# --------------------------------------------------------------------------

def _vignette(width=203, height=144):
    """A small vignette off a flat source, so the mask is what is measured."""
    Image = pytest.importorskip("PIL.Image")
    from tools import art_process

    source = Image.new("RGBA", (width * 2, height * 2), (255, 255, 255, 255))
    return art_process.vignette(source, width, height, "center")


def test_the_centre_of_the_vignette_is_fully_transparent():
    """Where the nodes, the path lines and the legend are drawn, nothing.

    This is the design in one assertion: the whole reason the location still is
    allowed back on the map screen at all is that it is not ON the map.
    """
    img = _vignette()
    alpha = img.getchannel("A")
    assert alpha.getpixel((img.width // 2, img.height // 2)) == 0


def test_the_whole_declared_clear_box_is_transparent():
    """Not just the centre pixel: the entire 70% x 80% box.

    A centre-only check passes for a mask whose ramp starts at zero, which is a
    vignette that dims the nodes everywhere.
    """
    from tools import art_process

    img = _vignette()
    cx, cy = art_process.VIGNETTE_CLEAR
    alpha = img.getchannel("A")
    x0 = round((img.width - 1) * (1 - cx) / 2)
    x1 = round((img.width - 1) * (1 + cx) / 2)
    y0 = round((img.height - 1) * (1 - cy) / 2)
    y1 = round((img.height - 1) * (1 + cy) / 2)
    box = alpha.crop((x0, y0, x1 + 1, y1 + 1))
    assert box.getextrema() == (0, 0)


def test_the_corner_reaches_the_declared_edge_alpha():
    """~0.6 at the frame's corner, which is where the margin is darkest."""
    from tools import art_process

    img = _vignette()
    alpha = img.getchannel("A")
    want = round(art_process.VIGNETTE_EDGE_ALPHA * 255)
    for corner in ((0, 0), (img.width - 1, 0),
                   (0, img.height - 1), (img.width - 1, img.height - 1)):
        assert alpha.getpixel(corner) == pytest.approx(want, abs=1), corner


def test_the_vignette_is_darkened_where_it_draws_at_all():
    """A margin picture at full brightness is a bright frame round the map."""
    from tools import art_process

    img = _vignette()
    # The source was pure white, so the corner's RGB is the darkening factor.
    r, g, b, _ = img.getpixel((0, 0))
    want = round(255 * art_process.VIGNETTE_DARKEN)
    assert r == pytest.approx(want, abs=2)
    assert (r, g, b) == (r, r, r)


def test_the_mask_is_monotonic_from_the_clear_box_outwards():
    """No banding, no ring: alpha only ever rises toward the edge.

    Cheap to assert and the one property a hand-tuned ease can lose.
    """
    img = _vignette()
    alpha = img.getchannel("A")
    row = img.height // 2
    values = [alpha.getpixel((x, row)) for x in range(img.width // 2, img.width)]
    assert values == sorted(values)
    assert values[0] == 0
    assert values[-1] > 0
