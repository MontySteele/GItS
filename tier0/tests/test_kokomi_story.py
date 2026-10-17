"""Kokomi's story in the run (review/active/kokomi-story-2026-10-16.md): the C#
story table against the sheet.

The words are pinned against the paper by the C# suite
(klee-mod/KleeTests/KokomiStoryTests.cs). What only the sheet and the art plan
know is pinned here: that the cards the events add are her sheet rows under
the paper's names, that "Choose 1 of 3 Gorou cards" draws from her four Gorou
rows, and that every borrowed picture (the eight event portraits and Public
Address's) has a plan row.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SHEET = ROOT / "docs" / "prototype-surface.yaml"
TABLE = ROOT / "klee-mod" / "KleeCode" / "Story" / "KokomiStory.cs"
CURSE = ROOT / "klee-mod" / "KleeCode" / "Cards" / "PublicAddress.cs"
PLAN = ROOT / "art" / "plan.tsv"


def _rows() -> dict[str, dict]:
    return {r["id"]: r for r in yaml.safe_load(SHEET.read_text(encoding="utf-8"))
            if isinstance(r, dict) and "id" in r}


def test_the_cards_the_events_add_are_her_sheet_rows_under_the_papers_names():
    rows = _rows()
    expected = {
        "proto_kk_treatise": "Treatise",
        "proto_kk_kurage_canopy": "Kurage Canopy",
    }
    for card_id, name in expected.items():
        assert rows[card_id]["name"] == name
        assert rows[card_id]["character"] == "kokomi"


def test_the_gorou_choice_is_her_four_gorou_rows():
    rows = _rows()
    gorou = sorted(r["id"] for r in rows.values()
                   if r["id"].startswith("proto_mi_gorou_") and r.get("character") == "kokomi")
    assert gorou == [
        "proto_mi_gorou_crystal_collapse",
        "proto_mi_gorou_inuzaka",
        "proto_mi_gorou_juuga",
        "proto_mi_gorou_war_banner",
    ]
    text = TABLE.read_text(encoding="utf-8")
    body = text[text.index("GorouCards() =>"):]
    classes = re.findall(r"ModelDb\.Card<(ProtoMiGorou\w+)>", body)
    assert classes == ["ProtoMiGorouInuzaka", "ProtoMiGorouWarBanner",
                       "ProtoMiGorouJuuga", "ProtoMiGorouCrystalCollapse"]


def test_every_borrowed_picture_has_a_plan_row():
    keys = re.findall(r'Art\.CardPortrait\("([a-z0-9_]+)"\)', TABLE.read_text(encoding="utf-8"))
    assert len(keys) == 8  # her eight events
    keys += re.findall(r'Art\.CardPortrait\("([a-z0-9_]+)"\)', CURSE.read_text(encoding="utf-8"))
    assert len(keys) == 9
    plan = {line.split("\t", 1)[0] for line in PLAN.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")}
    for key in keys:
        assert key in plan, key
