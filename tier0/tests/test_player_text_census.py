"""`tools/player_text_census.py` sees all the writing a player reads.

The census is the review surface for every line of player text before public
launch, so what it misses is invisible to the review. These arms pin the
parts that can be counted from outside the tool:

  1. every card row the generator built is in its owner's card section;
  2. every story event (each `new StoryEvent(...)` in `Story/`) is there;
  3. the Spiral Abyss has its 14 Blessings and 12 Shadows, each with text;
  4. no item carries empty text.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import player_text_census as census  # noqa: E402

GENERATED = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"
STORY = REPO / "klee-mod" / "KleeCode" / "Story"


@pytest.fixture(scope="module")
def data() -> dict:
    return census.census()


def _items(data: dict):
    for owner, sections in data["characters"].items():
        for section, items in sections.items():
            for item in items:
                yield owner, section, item


def test_shape(data):
    assert set(data["characters"]) == set(census.CHARACTERS)
    assert data["generated"] and data["commit"]
    for _, _, item in _items(data):
        for key in ("id", "name", "kind", "text", "source"):
            assert key in item, item
        assert re.search(r":\d+$", item["source"]), item


def test_every_live_card_row_is_in_its_owners_card_section(data):
    manifest = json.loads((GENERATED / "manifest.json").read_text(encoding="utf-8"))
    live = set(manifest["generated"])
    sheet = {r["id"] for r in census.yaml_rows()}
    live &= sheet
    assert len(live) > 400, "the generated manifest lost its rows"
    found: dict[str, tuple[str, str]] = {}
    for owner, section, item in _items(data):
        if section == "Cards" or section.startswith("Companion cards"):
            found[item["id"]] = (owner, section)
    missing = sorted(live - set(found))
    assert not missing, f"card rows missing from the census: {missing[:20]}"
    for cid in live:
        owner = next(o for p, o in census.PREFIX_OWNER.items() if cid.startswith(p))
        assert found[cid][0] == owner, (cid, found[cid])


def test_every_story_event_appears(data):
    events = set()
    for path in STORY.glob("*.cs"):
        src = path.read_text(encoding="utf-8")
        for m in re.finditer(r"EventType:\s*typeof\((?:[\w.]+\.)?(\w+)\)", src):
            events.add(m.group(1))
    assert len(events) >= 30, "the story tables moved; the pattern no longer finds them"
    titled = {item["id"] for _, section, item in _items(data)
              if item["kind"] == "event title" and "story" in section.lower()}
    assert not sorted(events - titled), sorted(events - titled)
    # each event has its page and at least two options
    for ev in events:
        ids = [item for _, s, item in _items(data)
               if item["id"] == ev or item["id"].startswith(ev + ".")]
        kinds = [i["kind"] for i in ids]
        assert "page" in kinds and kinds.count("option") >= 2, (ev, kinds)


def test_spiral_abyss_has_14_blessings_and_12_shadows(data):
    shared = data["characters"]["Shared"]
    blessings = shared.get("Spiral Abyss: Blessings", [])
    shadows = shared.get("Spiral Abyss: Shadows", [])
    assert len(blessings) == 14, [b["name"] for b in blessings]
    assert len(shadows) == 12, [s["name"] for s in shadows]
    for item in blessings + shadows:
        assert item["name"] and "{?" not in item["name"], item
        assert "{?" not in item["text"], item
    # numbers that move by act carry all three acts
    assert any("variants" in b and len(b["variants"]) == 3 for b in blessings)


def test_no_item_has_empty_text(data):
    empty = [(o, s, i["id"]) for o, s, i in _items(data) if not str(i["text"]).strip()]
    assert not empty, empty[:10]


def test_every_kit_has_its_core_sections(data):
    for owner in ("Klee", "Kokomi", "Furina", "Varka", "Yae"):
        sections = data["characters"][owner]
        for name in ("Character select & profile", "Starter deck", "Cards", "Relics",
                     "Architect finale"):
            assert sections.get(name), (owner, name)
