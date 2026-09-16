"""`EB-615`: the gallery reads a face wrapped in `FurinaBurstRider.Face`.

THE FIND (`EB-369` read, 2026-09-06). `render_card_gallery._LOC_RE` matched a
bare `("description", "...")` pair and nothing else, and thirteen Furina rows
do not print one: they print

    ("description", FurinaBurstRider.Face("<arm face>", "<shipped face>"))

which is a per-BUILD choice between two wordings. The regex wants the close
paren straight after the string, so those rows scraped an EMPTY in-game
description, `ingame_index` reported them as carrying no shipped text, and the
tile fell back to the sheet's own op lines -- the one thing this page exists
not to do, since the whole value of the in-game column is that it comes from a
second producer and makes sheet-vs-mod drift visible. `gentilhomme_usher` and
`high_tide` were the two verified by hand on that read.

WHICH FACE THE GALLERY SHOWS is the row's one pick, taken at its stated
default (a D pick under CLAUDE.md's ladder -- one-way error direction, no
number moves): the SHIPPED face is the tile's face, and the arm face prints
beside it under a label. A gallery is read to see what ships, and the other
half is exactly the drift a reader opens the page for.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a review
surface.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

import render_card_gallery as gallery  # noqa: E402

ARM = "Add 1 [gold]Gentilhomme Usher[/gold] to your [gold]Salon[/gold]."
SHIPPED = ARM + " [gold]Burst[/gold] +5."

RIDER_SOURCE = f'''
public override List<(string, string)>? Localization => new()
{{
    ("title", "Gentilhomme Usher"),
    ("description", FurinaBurstRider.Face("{ARM}", "{SHIPPED}")),
}};
'''

BARE_SOURCE = '''
public override List<(string, string)>? Localization => new()
{
    ("title", "Plain Row"),
    ("description", "Deal 6 damage."),
};
'''


def _scrape(source: str) -> dict:
    """What `ingame_index` puts in a row's `shipped` entry, off one file's
    text -- the two regexes and nothing else, so this pins the read and not
    the directory walk."""
    loc = dict(gallery._LOC_RE.findall(source))
    rider = gallery._RIDER_RE.search(source)
    if rider:
        loc["description"] = rider.group(2)
    return {"title": gallery._unescape_cs(loc.get("title", "")),
            "description": gallery._unescape_cs(loc.get("description", "")),
            "arm": gallery._unescape_cs(rider.group(1)) if rider else ""}


def test_the_red_one_a_bare_regex_reads_a_rider_row_as_empty():
    """The defect, stated as the control: `_LOC_RE` alone finds no description
    on a rider-wrapped row. This is what the gallery was doing."""
    assert "description" not in dict(gallery._LOC_RE.findall(RIDER_SOURCE))


def test_a_rider_wrapped_row_scrapes_the_shipped_face():
    scraped = _scrape(RIDER_SOURCE)
    assert scraped["description"] == SHIPPED
    assert scraped["title"] == "Gentilhomme Usher"


def test_the_arm_face_comes_back_beside_it():
    assert _scrape(RIDER_SOURCE)["arm"] == ARM


def test_a_one_faced_row_is_byte_identical_to_what_it_was():
    """The half that must NOT move: a row printing one literal scrapes exactly
    what it always did and reports no arm face."""
    scraped = _scrape(BARE_SOURCE)
    assert scraped == {"title": "Plain Row",
                       "description": "Deal 6 damage.", "arm": ""}


def test_the_tile_prints_the_shipped_face_and_the_arm_face_under_a_label():
    class _Card:
        id, name, cost, type, rarity = "gentilhomme_usher", "Usher", 1, "Skill", "common"
        character, exhaust = "furina", False
        archetypes: list[str] = []
        effects: list[dict] = []

    ship = dict(_scrape(RIDER_SOURCE),
                src="klee-mod/KleeCode/Cards/Furina/Generated/GentilhommeUsher.cs")
    html = gallery.tile(_Card(), None, False, False, REPO,
                        {"gentilhomme_usher": ship}, {})
    assert 'data-ingame="shipped"' in html, (
        "a rider-wrapped row must no longer read as having no shipped text")
    assert "Burst" in html, "the shipped face is the tile's face"
    assert "ig-arm" in html and "under the arm" in html, (
        "the arm face prints beside it, labelled")
    # The arm face is the shipped face minus its Burst clause, so the shipped
    # one must still be the one carrying that clause.
    body = html.split('class="ig-text"')[1].split("</div>")[0]
    assert "Burst" in body


def test_the_rider_regex_finds_the_real_rows_in_the_mod():
    """The live half: the shipped tree really does hold rider-wrapped rows,
    so this fixture is pinning a shape that exists. Skipped rather than failed
    where the mod tree is absent, the way the gallery itself degrades."""
    cards = gallery.MOD_CARDS_DIR
    if not cards.exists():
        return
    hits = [p for p in cards.rglob("*.cs")
            if gallery._RIDER_RE.search(p.read_text(encoding="utf-8",
                                                    errors="replace"))]
    assert hits, "no FurinaBurstRider.Face row found; has the rider retired?"
    for path in hits:
        src = path.read_text(encoding="utf-8", errors="replace")
        assert re.search(r'FurinaBurstRider\.Face\(', src)
