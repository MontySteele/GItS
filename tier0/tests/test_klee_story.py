"""Klee's story in the run (review/ruled/klee-story-batch-1-2026-10-12.md and
klee-story-batch-2-2026-10-12.md): the C# story table against the sheet.

The words are pinned against the papers by the C# suite
(klee-mod/KleeTests/KleeStoryTests.cs). What only the sheet knows is pinned
here: which of Klee's cards place a Bomb (A Letter from Jean's "Upgrade 2
random cards that place a Bomb" draws from that list), and that the cards the
events add are the sheet's rows under the paper's names.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SHEET = ROOT / "docs" / "prototype-surface.yaml"
TABLE = ROOT / "klee-mod" / "KleeCode" / "Story" / "KleeStory.cs"
VARKA = ROOT / "klee-mod" / "KleeCode" / "Story" / "VarkaStory.cs"
PLAN = ROOT / "art" / "plan.tsv"


def _rows() -> list[dict]:
    return [r for r in yaml.safe_load(SHEET.read_text(encoding="utf-8")) if isinstance(r, dict)]


def _ops(node):
    if isinstance(node, dict):
        if "op" in node:
            yield node
        for v in node.values():
            yield from _ops(v)
    elif isinstance(node, list):
        for v in node:
            yield from _ops(v)


def _places_a_bomb(row: dict) -> bool:
    for op in _ops(row.get("effects") or []):
        if op["op"] == "plant_bomb" and not op.get("mine"):
            return True
        if op["op"] in ("plant_bomb_copy_largest", "plant_homework_bomb"):
            return True
        # Jumpy Dumpty Mk.III: "Each hit places a Bomb 4 on that enemy."
        if op.get("plant_on_hit"):
            return True
    return False


def _table_bomb_placers() -> set[str]:
    text = TABLE.read_text(encoding="utf-8")
    block = text[text.index("BombPlacers = new HashSet<string>"):]
    block = block[: block.index("}")]
    return set(re.findall(r'"(proto_[a-z0-9_]+)"', block))


def test_bomb_placers_are_exactly_the_sheets_klee_rows_that_place_a_bomb():
    sheet = {r["id"] for r in _rows() if r.get("character") == "klee" and _places_a_bomb(r)}
    assert _table_bomb_placers() == sheet


def test_the_cards_the_events_add_are_the_sheets_rows_under_the_papers_names():
    names = {r["id"]: r.get("name") for r in _rows()}
    assert names["proto_ko_fish_blasting"] == "Fish Blasting"
    assert names["proto_mc_kaeya_glacial_waltz"] == "Kaeya — Glacial Waltz"
    assert names["proto_mc_noelle_breastplate"] == "Noelle — Breastplate"
    assert names["proto_mc_albedo_solar_isotoma"] == "Albedo — Solar Isotoma"
    # The story chains (review/active/klee-varka-story-chains-2026-10-14.md).
    assert names["proto_ko_dodoco_tag"] == "Dodoco Tag"
    assert names["proto_ko_alices_recipe"] == "Alice's Recipe"
    assert names["proto_ko_alices_introduction_magic"] == "Alice's Introduction Magic"
    assert names["proto_vk_four_winds_ascension"] == "Four Winds' Ascension"
    assert names["proto_mc_jean_dandelion_breeze"] == "Jean — Dandelion Breeze"


def test_every_borrowed_event_picture_has_a_plan_row():
    # Klee's eight events and Varka's eight (the story chains): each borrows
    # a card's picture until it has its own (BACKLOG "Art owed, story chains").
    text = TABLE.read_text(encoding="utf-8") + VARKA.read_text(encoding="utf-8")
    keys = re.findall(r'Art\.CardPortrait\("([a-z0-9_]+)"\)', text)
    assert len(keys) == 16
    plan = {line.split("\t", 1)[0] for line in PLAN.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")}
    for key in keys:
        assert key in plan, key
