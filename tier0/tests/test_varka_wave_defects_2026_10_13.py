"""THE VARKA WAVE'S DEFECTS (review/records/varka-wave-2026-10-13.md, "To
change"), the generated-text and tooltip halves:

  * a shared Companion that applies an element in Varka's deck switches his
    current element like any card of his, so it carries the in-combat
    "(Makes X current)" line and the switch tip (Lisa - Violet Arc made Electro
    current with no line saying so);
  * every Anemo card's "Applies Anemo" tip names the Swirl and its 2 damage to
    ALL enemies (Windbound Execution's face never said so);
  * (Tidal Bulwark's own-Block pin left with its Block: the Varka text pass,
    2026-10-13, ruled (a), took the Block off the card.)
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from tools import gen_klee_cards as gen

REPO = Path(__file__).resolve().parents[2]
GENERATED = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"
SHEET = REPO / "docs" / "prototype-surface.yaml"


def _row(row_id: str) -> dict:
    rows = yaml.safe_load(SHEET.read_text(encoding="utf-8"))
    return next(r for r in rows if isinstance(r, dict) and r.get("id") == row_id)


def _cs(cls: str) -> str:
    return (GENERATED / f"{cls}.cs").read_text(encoding="utf-8")


def test_a_shared_companion_that_applies_its_element_says_it_switches():
    lisa = _row("proto_mc_lisa_violet_arc")
    assert gen.varka_switch_element(lisa, gen.KLEE_PROFILE) == "electro"
    cs = _cs("ProtoMcLisaVioletArc")
    assert "{InCombat:{VarkaSwitch}|}" in cs
    assert 'description.Add("VarkaSwitch", VarkaOath.SwitchLine(this, Element.Electro))' in cs
    assert "ArmKeywordTips.ForElementSwitch(" in cs


def test_a_shared_companion_that_applies_nothing_carries_no_switch():
    # Noelle's Breastplate is Geo (no Oath element); Jean's Dandelion Breeze
    # is Anemo. Neither can make an element current.
    for row_id in ("proto_mc_noelle_breastplate", "proto_mc_jean_dandelion_breeze"):
        assert gen.varka_switch_element(_row(row_id), gen.KLEE_PROFILE) is None


def test_the_applies_anemo_tip_names_the_swirl_and_its_damage_to_all():
    words = json.loads((REPO / "klee-mod" / "pck-src" / "klee" / "localization"
                        / "eng" / "card_keywords.json").read_text(encoding="utf-8"))
    tip = words["KLEEMOD-APPLIES_ANEMO.description"]
    assert "[gold]Swirls[/gold]" in tip
    assert "[blue]2[/blue] unblockable damage to ALL enemies" in tip
