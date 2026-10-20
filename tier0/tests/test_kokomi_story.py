"""Kokomi's story in the run (review/active/kokomi-story-2026-10-16.md): the C#
story table against the sheet.

The words are pinned against the paper by the C# suite
(klee-mod/KleeTests/KokomiStoryTests.cs). What only the sheet and the art plan
know is pinned here: that, since the story rewards pass, the events name no
card of hers and Gorou's report offers Uncommon Companions, and that every
borrowed picture (the eight event portraits and Public
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


def test_the_events_name_no_card_of_hers():
    """The story rewards pass (review/active/story-rewards-pass-2026-10-19.md,
    ruled all (a)): Treatise+, Kurage Canopy+ and the Gorou choice became
    rarity offers, so the table adds no card of her pool by name."""
    text = TABLE.read_text(encoding="utf-8")
    assert re.findall(r"StoryEffectKind\.Add\w*Card, 0, typeof\((Proto\w+)\)", text) == []
    assert "GorouCards" not in text
    assert "ChoicePool" not in text


def test_gorous_report_offers_uncommon_companions():
    text = TABLE.read_text(encoding="utf-8")
    body = text[text.index('"SEND_FOR_REINFORCEMENTS"'):]
    body = body[:body.index("new StoryOption(", 1)]
    assert "Choose 1 of 3 random Uncommon Companions to add to your deck." in body
    assert "StoryEffect.ChooseCompanion(CardRarity.Uncommon)" in body
    # Her four Gorou rows are still hers, and still Companions she can be offered.
    rows = _rows()
    gorou = sorted(r["id"] for r in rows.values()
                   if r["id"].startswith("proto_mi_gorou_") and r.get("character") == "kokomi")
    assert gorou == [
        "proto_mi_gorou_crystal_collapse",
        "proto_mi_gorou_inuzaka",
        "proto_mi_gorou_juuga",
        "proto_mi_gorou_war_banner",
    ]


def test_every_borrowed_picture_has_a_plan_row():
    keys = re.findall(r'Art\.CardPortrait\("([a-z0-9_]+)"\)', TABLE.read_text(encoding="utf-8"))
    assert len(keys) == 8  # her eight events
    keys += re.findall(r'Art\.CardPortrait\("([a-z0-9_]+)"\)', CURSE.read_text(encoding="utf-8"))
    assert len(keys) == 9
    plan = {line.split("\t", 1)[0] for line in PLAN.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")}
    for key in keys:
        assert key in plan, key
