"""`tools/lint_element_text.py`, driven both ways.

[USER], 2026-10-02, after a co-op run: "Unify the language across all cards -
say if it does an element and also apply the symbol to the card". The lint is
what keeps the words from drifting off the faces again; these tests are what
keep the lint from passing by reading nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import gen_klee_cards as gen                    # noqa: E402
import gen_prototype_cards as proto             # noqa: E402
import lint_element_text as lint                # noqa: E402


def test_the_surface_is_clean_and_the_scan_is_not_vacuous():
    stats: dict = {}
    assert lint.findings(stats) == []
    assert stats["checked"] >= 100


def test_a_cadence_hit_owes_its_element_and_a_named_one_pays_it():
    klee = proto._profile_for("klee")
    row = {"id": "x", "type": "attack",
           "effects": [{"op": "damage", "amount": 6, "target": "enemy"}]}
    assert lint.owed_elements(row, klee, "Deal 6 damage.") == ["pyro"]
    face = "Deal 6 [gold]Pyro[/gold] damage."
    assert lint.owed_elements(row, klee, face) == ["pyro"]
    assert "[gold]Pyro[/gold]" in face


def test_a_face_with_no_hit_sentence_owes_no_cadence_word():
    """The Big One sets off Bombs and prints no hit of its own."""
    klee = proto._profile_for("klee")
    row = {"id": "x", "type": "attack",
           "effects": [{"op": "set_off", "target": "enemy"}]}
    face = "[gold]Set off[/gold]. Your [gold]Bombs[/gold] deal quadruple damage."
    assert lint.owed_elements(row, klee, face) == []


def test_a_companion_hit_owes_its_own_element_only_when_it_applies_it():
    klee = proto._profile_for("klee")
    row = {"id": "x", "type": "attack", "star": 4, "element": "geo",
           "effects": [{"op": "damage", "amount": 8, "target": "enemy",
                        "applies_element": True}]}
    assert lint.owed_elements(row, klee, "Deal 8 damage.") == ["geo"]
    plain = dict(row, effects=[dict(row["effects"][0], applies_element=False)])
    assert lint.owed_elements(plain, klee, "Deal 8 damage.") == []


def test_a_swirl_owes_no_word_but_wears_the_anemo_keyword():
    klee = proto._profile_for("klee")
    row = {"id": "x", "type": "skill", "star": 4, "element": "anemo",
           "effects": [{"op": "swirl", "target": "enemy"}]}
    assert lint.owed_elements(row, klee, "[gold]Swirl[/gold] the enemy.") == []
    assert gen.element_tag_elements_for(row, klee, False) == ["anemo"]


def test_a_damaging_plan_owes_hydro():
    kokomi = proto._profile_for("kokomi")
    row = {"id": "x", "type": "skill", "effects": [],
           "plan": [{"op": "damage", "amount": 12, "target": "enemy"}]}
    assert lint.owed_elements(row, kokomi, "[gold]Plan[/gold]: Deal 12 damage.") \
        == ["hydro"]


def test_a_generated_companion_face_names_its_element():
    """The rendered path (rows with no `description:`) prints the word."""
    row = {"id": "x", "type": "attack", "star": 4, "element": "cryo",
           "cost": 1, "rarity": "common",
           "effects": [{"op": "damage", "amount": 7, "target": "enemy",
                        "applies_element": True}]}
    assert "[gold]Cryo[/gold] damage" in gen.build_description(row)
    silent = dict(row, effects=[dict(row["effects"][0], applies_element=False)])
    assert "[gold]Cryo[/gold]" not in gen.build_description(silent)
