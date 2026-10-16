"""Furina's story in the run (review/active/furina-story-2026-10-15.md): the C#
story table against the sheet.

The words are pinned against the paper by the C# suite
(klee-mod/KleeTests/FurinaStoryTests.cs). What only the sheet and the art plan
know is pinned here: that the cards the events add are her sheet rows under
the paper's names, and that every borrowed picture (the eight event portraits
and Stage Fright's) has a plan row.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SHEET = ROOT / "docs" / "prototype-surface.yaml"
TABLE = ROOT / "klee-mod" / "KleeCode" / "Story" / "FurinaStory.cs"
CURSE = ROOT / "klee-mod" / "KleeCode" / "Cards" / "StageFright.cs"
PLAN = ROOT / "art" / "plan.tsv"


def _rows() -> dict[str, dict]:
    return {r["id"]: r for r in yaml.safe_load(SHEET.read_text(encoding="utf-8"))
            if isinstance(r, dict) and "id" in r}


def test_the_cards_the_events_add_are_her_sheet_rows_under_the_papers_names():
    rows = _rows()
    expected = {
        "proto_fs_understudys_debut": "Understudy's Debut",
        "proto_fs_let_the_people_rejoice": "Let the People Rejoice",
        "proto_fs_tearful_monologue": "Tearful Monologue",
    }
    for card_id, name in expected.items():
        assert rows[card_id]["name"] == name
        assert rows[card_id]["character"] == "furina"
    guests = [r for r in rows.values()
              if r["id"].startswith("proto_fs_guest_star_") and r.get("character") == "furina"]
    assert len(guests) == 11  # "Choose 1 of 3 random Guest Stars" draws from the eleven


def test_every_borrowed_picture_has_a_plan_row():
    keys = re.findall(r'Art\.CardPortrait\("([a-z0-9_]+)"\)', TABLE.read_text(encoding="utf-8"))
    assert len(keys) == 8  # her eight events
    keys += re.findall(r'Art\.CardPortrait\("([a-z0-9_]+)"\)', CURSE.read_text(encoding="utf-8"))
    assert len(keys) == 9
    plan = {line.split("\t", 1)[0] for line in PLAN.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")}
    for key in keys:
        assert key in plan, key
