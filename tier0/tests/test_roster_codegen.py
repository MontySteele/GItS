"""Character-profile and honesty guards for the roster card generator."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from tools import gen_klee_cards as gen


FURINA_HAND_WRITTEN = {"let_the_people_rejoice"}

# Cards deliberately DEFERRED from C# generation while a sprint is mid-flight,
# each with the gate that releases it. A curated list rather than a silent
# skip: an ungenerated card is a card that does nothing in the live game, and
# that must never be discoverable only by playing it.
#
# "The Tide Turns" F-D (the live C# Fanfare package) is HARD-GATED on F-C's
# tier-0.5 gates. Until those pass, `gain_fanfare_floor` has no C# home, and
# emitting a call to a method that does not exist would trade a visible
# deferral for a build break. Released by: F-D.
FURINA_DEFERRED_TO_FD = {"the_sea_is_my_stage", "lasting_impression"}

# Cards whose UPGRADE is unauthored because the delta it used to carry died
# with a retired grammar. Same curation rule as above: an unupgradable card
# is a dead campfire choice, so the gap is named and gated, never tolerated
# silently.
#
# florid_cadenza's only ratified delta was {fanfare_cost: -3} -- "Spend 10 ->
# Spend 7". With no spend line there is nothing for it to discount, and every
# replacement (cheaper threshold? one more card? Retain?) is a BALANCE call
# that belongs to F-B1 and red-pen, not to a mechanical grammar removal.
# Released by: F-B1, which re-authors the card as a threshold reader.
FURINA_UPGRADE_GAP_PENDING_FB1 = {"florid_cadenza"}


def by_id_of(cards: list[dict]) -> dict[str, dict]:
    return {card["id"]: card for card in cards}


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

    # ENCORE is the only card-level resource gate. Fanfare's retired with the
    # spend grammar ("The Tide Turns", F-A4): it is a read-only momentum stat
    # and no card spends it, so no Fanfare cost line may be emitted anywhere.
    for card in _furina_cards():
        emitted = gen.emit(card, gen.FURINA_PROFILE)
        assert "CustomResources<FanfareResource>.SetCanonicalCost" not in emitted
        assert "CustomResources<FanfareResource>.Cost(" not in emitted

    crescendo = gen.emit(by_id["crescendo"], gen.FURINA_PROFILE)
    # Legibility sprint (2026-07-24): the Fanfare rider renders through a
    # CalculatedDamageVar (face/preview and hit share one value path) instead
    # of inline PrintedDamage arithmetic. The scaling lives in the multiplier.
    # Untouched by F-A -- READING the meter is exactly what survives.
    assert "FurinaResources.Fanfare(card.Owner.Creature) / 2" in crescendo
    assert "DamageCmd.Attack(DynamicVars.CalculatedDamage)" in crescendo


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
    withheld = FURINA_HAND_WRITTEN | FURINA_DEFERRED_TO_FD
    assert generated == all_ids - withheld

    # The deferral must be for the REASON we think it is. A card that stopped
    # generating for some unrelated breakage would otherwise hide inside the
    # curated set and read as intentional.
    for cid in FURINA_DEFERRED_TO_FD:
        reason = gen.blocked_reason(by_id_of(_furina_cards())[cid],
                                    gen.FURINA_PROFILE)
        assert reason == "op 'gain_fanfare_floor'", reason

    manifest = json.loads(
        gen.FURINA_PROFILE.manifest.read_text(encoding="utf-8")
    )
    # 78 cards since F-B2 added lasting_impression, the common floor source.
    # Two withheld while F-D is gated (see FURINA_DEFERRED_TO_FD) -- both are
    # gain_fanfare_floor cards, which is the whole of the deferral.
    assert manifest["coverage"] == {
        "total": 78,
        "generated": 75,
        "blocked": 3,
    }
    assert set(manifest["generated"]) == generated
    assert set(manifest["blocked"]) == withheld
    assert (set(manifest["upgrades"]["no_upgrade_path"])
            == FURINA_UPGRADE_GAP_PENDING_FB1)


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


def test_companion_block_renders_spotlight_scaling_on_the_face():
    # Block half of L-A4. CalculatedBlockVar is the exact twin of
    # CalculatedDamageVar -- it overrides UpdateCardPreview to run
    # Hook.ModifyBlock, so block-modifying powers still reach the preview --
    # and it reads CalculationBase + CalculationExtra. Resolution goes through
    # the same var (the base game's own Mirage idiom) so face and gain agree.
    by_id = {card["id"]: card for card in _companion_rows()}
    diona = gen.emit(by_id["diona_icy_paws"])

    assert "new CalculationBaseVar(5m)" in diona
    assert "new CalculationExtraVar(1m)" in diona
    assert (
        "new CalculatedBlockVar(ValueProp.Move).WithMultiplier("
        "static (card, _) => SpotlightSystem.PrintedBlockDelta(card))"
        in diona
    )
    assert "DynamicVars.CalculatedBlock.Calculate(cardPlay.Target)" in diona
    assert "{CalculatedBlock:diff()}" in diona
    assert "PrintedBlock(this" not in diona
    assert "DynamicVars.CalculationBase.UpgradeValueBy(2m);" in diona


def test_card_doing_both_damage_and_block_converts_only_its_damage():
    # CalculatedDamageVar and CalculatedBlockVar BOTH take their base from the
    # single CalculationBase var, so a card converting both would compute its
    # block off the damage base. freminet_pressurized_floe is the only card
    # doing both; its damage conversion wins and its block stays inline.
    by_id = {card["id"]: card for card in _companion_rows()}
    freminet = gen.emit(by_id["freminet_pressurized_floe"])

    assert freminet.count("new CalculationBaseVar(") == 1
    assert "new CalculatedDamageVar(" in freminet
    assert "new CalculatedBlockVar(" not in freminet
    assert "new BlockVar(" in freminet
    assert "PrintedBlock(this" in freminet


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


def test_salon_scaled_number_renders_the_replacement_multiplier():
    # Legibility sprint, salon half. A salon-deploy card whose later effect is
    # scaled by the bow-out multiplier used to print its unscaled base and
    # resolve larger. It now renders through a CalculatedVar whose multiplier
    # asks SalonMemberPower -- the same StageIsFull predicate Deploy's own loop
    # uses -- so the face and the effect are one expression.
    by_id = {card["id"]: card for card in _furina_cards()}
    usher = gen.emit(by_id["gentilhomme_usher"], gen.FURINA_PROFILE)

    assert "new CalculationBaseVar(4m)" in usher
    assert "new CalculationExtraVar(1m)" in usher
    assert (
        "new CalculatedBlockVar(ValueProp.Move).WithMultiplier("
        "static (card, _) => SalonMemberPower.ReplacementDelta("
        "card, 1, SalonConstants.ReplacementDamageMultiplier))"
        in usher
    )
    assert "{CalculatedBlock:diff()}" in usher
    # The inline expression it replaces must be gone: keeping both would apply
    # the multiplier twice.
    assert "salonReplacements > 0 ? 3 : 1" not in usher
    assert "DynamicVars.CalculationBase.UpgradeValueBy(2m);" in usher


def test_salon_scaled_value_is_captured_before_the_cards_own_deploys():
    # The timing rule that makes the closed form correct. WillReplace reads the
    # PRE-PLAY company size, but a card's own Deploy calls grow that company
    # mid-resolution -- so the scaled value is captured at the top of OnPlay,
    # before the first deploy, which is the state the card face read. Spending
    # the var afterwards instead would answer a different question than the
    # preview did.
    by_id = {card["id"]: card for card in _furina_cards()}
    usher = gen.emit(by_id["gentilhomme_usher"], gen.FURINA_PROFILE)

    snapshot = usher.index("var salonScaledBlock =")
    deploy = usher.index("SalonMemberPower.Deploy(")
    gain = usher.index("CreatureCmd.GainBlock(")
    assert snapshot < deploy < gain
    assert "GainBlock(Owner.Creature, salonScaledBlock" in usher


def test_salon_numeric_multiplier_covers_draw_encore_and_power():
    # x2 numerics take the same route as the x3 damage/block, through a plain
    # CalculatedVar (the base game only ships typed Damage/Block subclasses).
    by_id = {card["id"]: card for card in _furina_cards()}
    numeric = "SalonConstants.ReplacementNumericMultiplier"

    rehearsal = gen.emit(by_id["dress_rehearsal"], gen.FURINA_PROFILE)
    # NOT named "Cards": DynamicVarSet.Cards is a typed accessor that casts to
    # CardsVar, so a CalculatedVar under that name throws on any read.
    assert f'new CalculatedVar("DrawCards").WithMultiplier(' in rehearsal
    assert numeric in rehearsal
    assert "{DrawCards:diff()}" in rehearsal
    assert "new CardsVar(" not in rehearsal

    gala = gen.emit(by_id["grand_gala"], gen.FURINA_PROFILE)
    assert 'new CalculatedVar("Encore")' in gala
    assert "{Encore:diff()}" in gala
    # The upgrade moves onto the var's base instead of an IsUpgraded text swap,
    # so the printed number carries both the upgrade and the salon scaling.
    assert "DynamicVars.CalculationBase.UpgradeValueBy(3m);" in gala
    assert "IfUpgraded:show:7|4" not in gala

    waltz = gen.emit(by_id["endless_waltz"], gen.FURINA_PROFILE)
    assert 'new CalculatedVar("PowerAmount")' in waltz
    assert "{PowerAmount:diff()}" in waltz


def test_only_one_salon_number_per_card_converts():
    # Every calculated var on a card -- typed or plain -- takes its base term
    # from the single CalculationBase var, so a second conversion would compute
    # itself off the first one's base. One per card; the rest keep the inline
    # expression (and are logged as remaining gaps, not silently dropped).
    for card in _furina_cards():
        if not gen.salon_deploy_card(card):
            continue
        source = gen.emit(card, gen.FURINA_PROFILE)
        assert source.count("new CalculationBaseVar(") <= 1, card["id"]
        converted = [
            eff for eff in card["effects"]
            if gen.salon_calc_rider(card, eff) is not None
        ]
        assert len(converted) <= 1, card["id"]


def test_salon_deploy_count_must_be_static_to_convert():
    # WillReplace is a closed form over (pre-play company size + this card's
    # own deploys so far). An upgradeable deploy amount makes that count a
    # runtime value the face cannot know, so the card stays inline rather than
    # guessing. mademoiselle_crabaletta is the live case.
    import copy

    by_id = {card["id"]: card for card in _furina_cards()}
    crabaletta = copy.deepcopy(by_id["mademoiselle_crabaletta"])
    crabaletta["effects"].append({"op": "draw", "amount": 1})
    assert gen._salon_calc_target(crabaletta) is None

    # Control: the identical card with a literal deploy count does convert, so
    # the exclusion above is the static-count rule and not some other guard.
    static = copy.deepcopy(crabaletta)
    static["id"] = "synthetic_static_deploy"   # no upgrade deltas -> no var
    assert gen.power_upgrade_effect(static) is None
    assert gen._salon_calc_target(static) is not None


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

    # Track L-C: the rider's arithmetic moved to the hover tip, so the face
    # keeps only the marker. Hand-written card, wired by hand -- pin both ends
    # so it cannot drift from the generated cards' treatment.
    assert f"fanfarePer: {n}, fanfareStep: {div}" in source
    assert "Scales with [gold]Fanfare[/gold]." in source
    assert f"plus {n} damage per" not in source


def test_converted_riders_move_their_arithmetic_to_the_hover_tip():
    # Track L-C. Once the rider renders inside the printed number, restating
    # "+1 damage per 2 Fanfare" on the face is duplicate bookkeeping -- the
    # number already shows the answer. The face keeps a marker naming the
    # mechanism (so a reward-screen read still declares that it scales) and
    # the rate moves to a tip that can also price it live.
    by_id = {card["id"]: card for card in _furina_cards()}

    crescendo = gen.emit(by_id["crescendo"], gen.FURINA_PROFILE)
    assert "Scales with [gold]Fanfare[/gold]." in crescendo
    assert "+1 damage per 2" not in crescendo
    assert (
        "FurinaRiderTips.ForCard(base.ExtraHoverTips, this, "
        "fanfarePer: 1, fanfareStep: 2)" in crescendo
    )

    torrential = gen.emit(by_id["torrential_turn"], gen.FURINA_PROFILE)
    assert "Bonus damage vs. an elemental aura." in torrential
    assert "+4 damage if the enemy" not in torrential
    assert "FurinaRiderTips.ForCard(base.ExtraHoverTips, this, auraBonus: 4)" in torrential


def test_unconverted_riders_keep_their_sentence_on_the_face():
    # The other half of the L-C rule, and the one that matters: a rider whose
    # number is NOT inside the printed value must keep its full sentence,
    # because the text is the only place the player can read it. Klee's
    # detonation rider and the AoE aura riders are both on that side of the
    # line (AoE aura riders stay per-target, see the L-B pass-2 guard).
    furina_by_id = {card["id"]: card for card in _furina_cards()}
    waves = gen.emit(furina_by_id["crashing_waves"], gen.FURINA_PROFILE)
    assert "damage if the enemy has an elemental aura." in waves
    assert "FurinaRiderTips" not in waves

    klee_by_id = {
        card["id"]: card
        for card in yaml.safe_load(gen.SHEET.read_text(encoding="utf-8"))
    }
    big_one = gen.emit(klee_by_id["grand_finale"], gen.KLEE_PROFILE)
    assert "damage per [gold]Bomb[/gold] detonated this combat." in big_one
    assert "FurinaRiderTips" not in big_one
