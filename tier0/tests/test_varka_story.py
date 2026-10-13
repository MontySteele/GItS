"""Varka's story in the run (review/active/varka-story-2026-10-13.md): the C#
story table against the sheet.

The words are pinned against the paper by the C# suite
(klee-mod/KleeTests/VarkaStoryTests.cs). What only the sheet and the art plan
know is pinned here: that the cards the events add are the sheet's rows under
the paper's names (act 3's three are his Uncommons), and that every borrowed
picture (the three event portraits and Overdue Reports') has a plan row.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SHEET = ROOT / "docs" / "prototype-surface.yaml"
TABLE = ROOT / "klee-mod" / "KleeCode" / "Story" / "VarkaStory.cs"
CURSE = ROOT / "klee-mod" / "KleeCode" / "Cards" / "OverdueReports.cs"
PLAN = ROOT / "art" / "plan.tsv"


def _rows() -> dict[str, dict]:
    return {r["id"]: r for r in yaml.safe_load(SHEET.read_text(encoding="utf-8"))
            if isinstance(r, dict) and "id" in r}


def test_the_cards_the_events_add_are_the_sheets_rows_under_the_papers_names():
    rows = _rows()
    assert rows["proto_vk_razor_claw_and_thunder"]["name"] == "Razor: Awakening"
    expected = {
        "proto_vk_eula_icetide_vortex": "Eula: Icetide Vortex",
        "proto_vk_noelle_steadfast_maid": "Noelle: Steadfast Maid",
        "proto_vk_diluc_searing_onslaught": "Diluc: Searing Onslaught",
    }
    for card_id, name in expected.items():
        assert rows[card_id]["name"] == name
        assert rows[card_id]["character"] == "varka"
        assert rows[card_id]["rarity"] == "uncommon", card_id


def test_every_borrowed_picture_has_a_plan_row():
    keys = re.findall(r'Art\.CardPortrait\("([a-z0-9_]+)"\)', TABLE.read_text(encoding="utf-8"))
    assert len(keys) == 3
    keys += re.findall(r'Art\.CardPortrait\("([a-z0-9_]+)"\)', CURSE.read_text(encoding="utf-8"))
    assert len(keys) == 4
    plan = {line.split("\t", 1)[0] for line in PLAN.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")}
    for key in keys:
        assert key in plan, key
