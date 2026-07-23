"""Character-profile and honesty guards for the roster card generator."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from tools import gen_klee_cards as gen


FURINA_HAND_WRITTEN = {"let_the_people_rejoice"}


def _furina_cards() -> list[dict]:
    return yaml.safe_load(
        gen.FURINA_PROFILE.sheet.read_text(encoding="utf-8")
    )


def test_klee_profile_remains_the_legacy_default():
    assert gen.KLEE_PROFILE.sheet == gen.SHEET
    assert gen.KLEE_PROFILE.out_dir == gen.OUT_DIR
    assert gen.KLEE_PROFILE.namespace == "KleeMod.Cards.Generated"
    assert gen.KLEE_PROFILE.cadence == "catalyst_attack"


def test_card_level_resource_costs_emit_explicit_gates_and_cost_upgrades():
    by_id = {card["id"]: card for card in _furina_cards()}
    crowd = gen.emit(by_id["crowd_work"], gen.FURINA_PROFILE)
    assert (
        "CustomResources<EncoreResource>.SetCanonicalCost(this, 2);"
        in crowd
    )
    assert "Spend 2 [gold]Encore[/gold]." in crowd

    crescendo = gen.emit(by_id["crescendo"], gen.FURINA_PROFILE)
    assert (
        "CustomResources<FanfareResource>.SetCanonicalCost(this, 10);"
        in crescendo
    )
    assert "FurinaResources.Fanfare(Owner.Creature) / 2" in crescendo

    florid = gen.emit(by_id["florid_cadenza"], gen.FURINA_PROFILE)
    assert (
        "CustomResources<FanfareResource>.Cost(this)!"
        ".UpgradeCostBy(-3);"
        in florid
    )
    assert "{IfUpgraded:show:7|10}" in florid


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


def test_furina_profile_emits_every_non_kit_card():
    all_ids = {card["id"] for card in _furina_cards()}
    generated = {
        card["id"]
        for card in _furina_cards()
        if gen.blocked_reason(card, gen.FURINA_PROFILE) is None
    }
    assert generated == all_ids - FURINA_HAND_WRITTEN

    manifest = json.loads(
        gen.FURINA_PROFILE.manifest.read_text(encoding="utf-8")
    )
    assert manifest["coverage"] == {
        "total": 76,
        "generated": 75,
        "blocked": 1,
    }
    assert set(manifest["generated"]) == generated
    assert set(manifest["blocked"]) == FURINA_HAND_WRITTEN
    assert not manifest["upgrades"]["no_upgrade_path"]


def test_furina_runtime_clusters_emit_concrete_calls():
    by_id = {card["id"]: card for card in _furina_cards()}

    salon = gen.emit(by_id["salon_debut"], gen.FURINA_PROFILE)
    assert "SalonMemberPower.Deploy" in salon

    guest = gen.emit(by_id["an_invitation"], gen.FURINA_PROFILE)
    assert "GuestStarGenerator.Generate" in guest

    spotlight = gen.emit(by_id["standing_ovation"], gen.FURINA_PROFILE)
    assert "OvationSpendBoostPower" in spotlight

    healing = gen.emit(by_id["singer_of_many_waters"], gen.FURINA_PROFILE)
    assert 'DynamicVars["Heal"].BaseValue' in healing
    assert "CreatureCmd.Heal" in healing

    aura_payoff = gen.emit(by_id["crashing_waves"], gen.FURINA_PROFILE)
    assert "foreach (var auraTarget" in aura_payoff
    assert "AuraCmd.Find(auraTarget)" in aura_payoff


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


def test_handwritten_furina_burst_matches_the_sheet_contract():
    row = next(
        card for card in _furina_cards()
        if card["id"] == "let_the_people_rejoice"
    )
    source = (
        Path("klee-mod/KleeCode/Cards/Furina/LetThePeopleRejoice.cs")
        .read_text(encoding="utf-8")
    )
    damage, encore = row["effects"]

    assert f'new DamageVar({damage["amount"]}m' in source
    assert "FurinaResources.Fanfare(Owner.Creature) / 4" in source
    assert f"FurinaResources.GainEncore(Owner.Creature, {encore['amount']});" in source
    assert "CustomResources<FurinaBurstResource>.SetCanonicalCost" in source
    assert "FurinaResourceConstants.BurstMax" in source
    assert "CardKeyword.Retain" in source
    assert "IElementalCard" in source
    assert "Element Element => Element.Hydro" in source
