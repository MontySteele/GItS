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
    # Legibility sprint (2026-07-24): the Fanfare rider now renders through a
    # CalculatedDamageVar (face/preview and hit share one value path) instead
    # of inline PrintedDamage arithmetic. The scaling lives in the multiplier.
    assert "FurinaResources.Fanfare(card.Owner.Creature) / 2" in crescendo
    assert "DamageCmd.Attack(DynamicVars.CalculatedDamage)" in crescendo

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
    # 77 cards since the Salon-v2 rework added standing_room_only.
    assert manifest["coverage"] == {
        "total": 77,
        "generated": 76,
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


def test_single_target_aura_rider_renders_through_a_calculated_var():
    # Legibility sprint pass 2 (2026-07-24): CalculatedVar.Calculate(target)
    # receives the hovered creature during preview and the real one at
    # resolution, so a single-target bonus_vs_aura greens exactly when you
    # hover an aura'd enemy -- and the hit agrees, because AttackCommand
    # resolves the same var. The multiplier must be static (CalculatedVar
    # rejects instance targets) and must null-guard: preview calls
    # Calculate(null) whenever nothing is hovered.
    by_id = {card["id"]: card for card in _furina_cards()}
    torrential = gen.emit(by_id["torrential_turn"], gen.FURINA_PROFILE)

    assert "new CalculationBaseVar(10m)" in torrential
    assert "new ExtraDamageVar(4m)" in torrential
    assert (
        "static (_, target) => "
        "target != null && AuraCmd.Find(target) != null ? 1 : 0"
        in torrential
    )
    assert "DamageCmd.Attack(DynamicVars.CalculatedDamage)" in torrential
    assert "{CalculatedDamage:diff()}" in torrential
    # The base term moved out of Damage, so the upgrade must follow it.
    assert "DynamicVars.CalculationBase.UpgradeValueBy(3m);" in torrential
    assert "DynamicVars.Damage" not in torrential


def test_aoe_aura_riders_stay_per_target():
    # NOT a display nicety -- a correctness guard. AttackCommand resolves a
    # CalculatedDamageVar ONCE with singleTarget == null, so converting an AoE
    # aura rider would collapse a per-enemy "does this one have an aura?"
    # decision into a single flat value for the whole board. Both of these
    # must keep their per-target foreach, Furina's and Klee's alike.
    furina_by_id = {card["id"]: card for card in _furina_cards()}
    klee_by_id = {
        card["id"]: card
        for card in yaml.safe_load(gen.SHEET.read_text(encoding="utf-8"))
    }

    for source in (
        gen.emit(furina_by_id["crashing_waves"], gen.FURINA_PROFILE),
        gen.emit(klee_by_id["flame_dance"], gen.KLEE_PROFILE),
    ):
        assert "foreach (var auraTarget" in source
        assert "AuraCmd.Find(auraTarget)" in source
        assert "CalculatedDamageVar" not in source


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


def test_power_var_binds_only_the_effect_the_sim_upgrades():
    # 2026-07-23 reward-screen softlock: stage_lights and courtroom_drama
    # each declared "PowerAmount" twice (one per apply_power), and
    # DynamicVarSet's constructor throws on the duplicate inside
    # CardFactory.CreateForReward. The var may exist exactly once, on the
    # effect tier0 upgrades.py actually bumps; every other power effect
    # renders its printed literal.
    by_id = {card["id"]: card for card in _furina_cards()}

    lights = gen.emit(by_id["stage_lights"], gen.FURINA_PROFILE)
    assert lights.count('new DynamicVar("PowerAmount"') == 1
    assert 'new DynamicVar("PowerAmount", 2m)' in lights
    assert "Apply 1 [gold]Weak[/gold] to ALL enemies." in lights
    assert "Apply<WeakPower>(choiceContext, debuffTarget, 1," in lights

    drama = gen.emit(by_id["courtroom_drama"], gen.FURINA_PROFILE)
    assert drama.count('new DynamicVar("PowerAmount"') == 1
    assert 'new DynamicVar("PowerAmount", 2m)' in drama
    assert "Apply 1 [gold]Weak[/gold]." in drama
    assert "Apply<WeakPower>(choiceContext, cardPlay.Target, 1," in drama


def test_named_power_delta_follows_the_name_not_effect_order(monkeypatch):
    # tier0 upgrades.py binds a `vulnerable` delta to the first apply_power
    # whose power NAME contains "vuln" -- not to the first power effect.
    # A weak rider listed first must stay literal while the named effect
    # takes the var and the OnUpgrade bump.
    card = {
        "id": "synthetic_order_probe",
        "name": "Synthetic Order Probe",
        "cost": 1,
        "type": "skill",
        "rarity": "common",
        "effects": [
            {"op": "apply_power", "power": "weak", "amount": 1,
             "target": "enemy"},
            {"op": "apply_power", "power": "vulnerable", "amount": 2,
             "target": "enemy"},
        ],
    }
    monkeypatch.setattr(
        gen, "_upgrade_deltas", {"synthetic_order_probe": {"vulnerable": 1}})
    assert gen.power_upgrade_effect(card) is card["effects"][1]
    variables = gen.build_vars(card)
    assert variables == ['new DynamicVar("PowerAmount", 2m)']
    upgrade = gen.build_upgrade(card)
    assert upgrade == ['DynamicVars["PowerAmount"].UpgradeValueBy(1m);']


def test_duplicate_dynamic_var_names_fail_the_generator():
    # The guard exists so a collision dies at emit time, not on the reward
    # screen of whatever run happens to roll the card.
    import pytest

    card = {
        "id": "synthetic_dupe_probe",
        "name": "Synthetic Dupe Probe",
        "cost": 1,
        "type": "skill",
        "rarity": "common",
        "effects": [
            {"op": "heal", "amount": 3},
            {"op": "heal", "amount": 5},
        ],
    }
    with pytest.raises(SystemExit, match="duplicate DynamicVar"):
        gen.build_vars(card)


def test_basics_carry_the_tags_base_game_content_keys_on():
    # LargeCapsule.GetStrikeForCharacter: `AllCards.First(c => c.Rarity ==
    # Basic && c.Tags.Contains(CardTag.Strike))` -- an untagged basic hangs
    # the Ancient event room (2026-07-23 softlock, Furina's first relic).
    by_id = {card["id"]: card for card in _furina_cards()}

    strike = gen.emit(by_id["soloists_solicitation"], gen.FURINA_PROFILE)
    assert "CanonicalTags => new() { CardTag.Strike };" in strike

    defend = gen.emit(by_id["stage_presence"], gen.FURINA_PROFILE)
    assert "CanonicalTags => new() { CardTag.Defend };" in defend

    non_basic = gen.emit(by_id["crowd_work"], gen.FURINA_PROFILE)
    assert "CanonicalTags" not in non_basic

    klee_by_id = {
        card["id"]: card
        for card in yaml.safe_load(gen.SHEET.read_text(encoding="utf-8"))
    }
    jumpy = gen.emit(klee_by_id["jumpy_dumpty"], gen.KLEE_PROFILE)
    assert "CanonicalTags => new() { CardTag.Strike };" in jumpy


def _companion_rows() -> list[dict]:
    rows = []
    for sheet_path, nation in gen.COMPANION_SHEETS:
        for card in yaml.safe_load(sheet_path.read_text(encoding="utf-8")):
            # The generator stamps nation from the sheet it came from; emit()
            # requires it.
            card.setdefault("nation", nation)
            rows.append(card)
    return rows


def test_companion_damage_renders_spotlight_scaling_on_the_face():
    # Legibility sprint pass 3 (Track L-A4): Spotlight's GuestCast scaling
    # (1.5x + flat) used to reach the number only at resolution, via
    # PrintedDamage inside OnPlay -- the card printed its base and hit for
    # more. Routing it through a CalculatedDamageVar puts face, enemy hover
    # and hit on one value: base + 1 * (PrintedDamage(base) - base), which is
    # PrintedDamage(base) exactly, so no resolved number moves.
    by_id = {card["id"]: card for card in _companion_rows()}
    kaeya = gen.emit(by_id["kaeya_frostgnaw"])

    assert "new CalculationBaseVar(6m)" in kaeya
    assert "new ExtraDamageVar(1m)" in kaeya
    assert "static (card, _) => SpotlightSystem.PrintedDamageDelta(card)" in kaeya
    assert "DamageCmd.Attack(DynamicVars.CalculatedDamage)" in kaeya
    assert "{CalculatedDamage:diff()}" in kaeya
    # The scaling now lives in the var, so the OnPlay wrap must be gone --
    # leaving both would apply Spotlight twice.
    assert "PrintedDamage(this" not in kaeya


def test_furina_own_cards_keep_the_identity_spotlight_wrap():
    # PrintedDamage is identity for a non-companion: its bonus path requires
    # Mode == GuestCast, and under GuestCast IsSpotlighted accepts only
    # ICompanionCard, while CenterStage forces the multiplier to 1m. Furina's
    # own plain-damage cards therefore gain nothing from conversion, and
    # converting them would add a var (and an upgrade-target move) for no
    # visible change. Keep them on the plain DamageVar.
    by_id = {card["id"]: card for card in _furina_cards()}
    plain = gen.emit(by_id["soloists_solicitation"], gen.FURINA_PROFILE)

    assert "new DamageVar(" in plain
    assert "CalculatedDamageVar" not in plain
    assert "PrintedDamage(this" in plain


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

    # Legibility sprint (2026-07-24): the Fanfare rider renders through a
    # CalculatedDamageVar (base + N*(Fanfare/M)) so face/preview and the hit
    # agree -- same form the generator emits for own-card fanfare riders.
    n, _, rest = damage["bonus_formula"].partition("_per_")
    div = rest.partition("_")[0]
    assert f'new CalculationBaseVar({damage["amount"]}m)' in source
    assert f'new ExtraDamageVar({n}m)' in source
    assert f"FurinaResources.Fanfare(card.Owner.Creature) / {div}" in source
    assert "DamageCmd.Attack(DynamicVars.CalculatedDamage)" in source
    assert f"FurinaResources.GainEncore(Owner.Creature, {encore['amount']});" in source
    assert "CustomResources<FurinaBurstResource>.SetCanonicalCost" in source
    assert "FurinaResourceConstants.BurstMax" in source
    assert "CardKeyword.Retain" in source
    assert "IElementalCard" in source
    assert "Element Element => Element.Hydro" in source
