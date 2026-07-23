"""Character-profile and honesty guards for the roster card generator."""

from __future__ import annotations

import json

import yaml

from tools import gen_klee_cards as gen


FURINA_GENERATED = {
    "commanding_gaze",
    "courtroom_drama",
    "duet",
    "fortissimo_guard",
    "graceful_retreat",
    "matinee_performance",
    "poised_riposte",
    "quick_change",
    "regal_bearing",
    "soloists_solicitation",
    "stage_presence",
    "swelling_overture",
    "undercurrent",
    "usher_the_waves",
    "warmup_act",
    "witness_stand",
}


def _furina_cards() -> list[dict]:
    return yaml.safe_load(
        gen.FURINA_PROFILE.sheet.read_text(encoding="utf-8")
    )


def test_klee_profile_remains_the_legacy_default():
    assert gen.KLEE_PROFILE.sheet == gen.SHEET
    assert gen.KLEE_PROFILE.out_dir == gen.OUT_DIR
    assert gen.KLEE_PROFILE.namespace == "KleeMod.Cards.Generated"
    assert gen.KLEE_PROFILE.cadence == "catalyst_attack"


def test_card_level_resource_costs_block_instead_of_disappearing():
    by_id = {card["id"]: card for card in _furina_cards()}
    assert gen.blocked_reason(
        by_id["crowd_work"], gen.FURINA_PROFILE
    ).startswith("encore_cost")
    assert gen.blocked_reason(
        by_id["crescendo"], gen.FURINA_PROFILE
    ).startswith("fanfare_cost")


def test_unknown_card_level_semantics_block_loudly():
    card = {
        "id": "future_card",
        "name": "Future Card",
        "cost": 1,
        "type": "skill",
        "rarity": "common",
        "effects": [{"op": "block", "amount": 5}],
        "future_resource_cost": 3,
    }
    assert gen.blocked_reason(
        card, gen.FURINA_PROFILE
    ) == "card field(s) ['future_resource_cost'] not understood"


def test_furina_profile_emits_only_the_runtime_safe_subset():
    generated = {
        card["id"]
        for card in _furina_cards()
        if gen.blocked_reason(card, gen.FURINA_PROFILE) is None
    }
    assert generated == FURINA_GENERATED

    manifest = json.loads(
        gen.FURINA_PROFILE.manifest.read_text(encoding="utf-8")
    )
    assert manifest["coverage"] == {
        "total": 76,
        "generated": 16,
        "blocked": 60,
    }
    assert set(manifest["generated"]) == FURINA_GENERATED
    assert not manifest["upgrades"]["no_upgrade_path"]


def test_furina_skill_grade_cadence_and_character_identity():
    by_id = {card["id"]: card for card in _furina_cards()}

    normal_attack = gen.emit(
        by_id["soloists_solicitation"], gen.FURINA_PROFILE
    )
    assert "IElementalCard" not in normal_attack
    assert 'public string CharacterId => "furina";' in normal_attack

    damaging_skill = gen.emit(by_id["usher_the_waves"], gen.FURINA_PROFILE)
    assert "IElementalCard" in damaging_skill
    assert "public Element Element => Element.Hydro;" in damaging_skill

    nondamaging_skill = gen.emit(by_id["duet"], gen.FURINA_PROFILE)
    assert "IElementalCard" not in nondamaging_skill
    assert "KleeKeywords.AppliesHydro" not in nondamaging_skill
