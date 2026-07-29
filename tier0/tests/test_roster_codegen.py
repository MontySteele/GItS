"""Character-profile and honesty guards for the roster card generator."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from tools import gen_klee_cards as gen


FURINA_HAND_WRITTEN = {"let_the_people_rejoice"}

# A7's async deferral is CLOSED (2026-07-29) and the set is DELETED rather
# than emptied, following the Curtain Call precedent below -- a dormant escape
# hatch just makes the next silent skip easy, and the positive assertion in
# test_furina_profile_emits_every_non_kit_card states the invariant directly.
#
# It stood for two sprints on a real gap: the trigger fires from Fanfare
# mutators that are synchronous, while every block grant in the mod is `await
# CreatureCmd.GainBlock`. The gate it named was "make the resource surface
# async, or establish a verified sync block-grant idiom", and NEITHER is what
# released it. The third option was the one already shipping next door --
# note synchronously, settle at the next awaited hook, exactly as
# CurtainCallHooks.NoteEncoreSpent has done on the same funnel since R85. The
# lesson worth keeping: a deferral's stated gate is a hypothesis about the
# solution, and re-reading the neighbours beat waiting for the refactor.
#
# See FurinaResources.PendingDeltaBlock and tier0/tests/test_a7_port.py.

# Cards deliberately DEFERRED from C# generation while a sprint is mid-flight,
# each with the gate that releases it. A curated list rather than a silent
# skip: an ungenerated card is a card that does nothing in the live game, and
# that must never be discoverable only by playing it.
#
# "The Tide Turns" F-D (the live C# Fanfare package) was HARD-GATED on F-C's
# tier-0.5 gates. Until it landed, `gain_fanfare_floor` had no C# home, and
# emitting a call to a method that does not exist would have traded a visible
# deferral for a build break.
#
# RELEASED 2026-07-25 by the "Ship What We Know" sprint, track G-A2. F-C never
# ran and never will -- the fanfare sprint closed on a null and its gates went
# with it -- so F-D was resurrected as its own pass with a trace-parity
# acceptance instead. `FurinaResources.GainFanfareFloor` now exists and both
# cards generate.
#
# Kept as an empty set rather than deleted, exactly as
# FURINA_UPGRADE_GAP_PENDING_FB1 was: the invariant "every non-kit card is
# emitted" is then asserted POSITIVELY, and the next deferral has somewhere to
# be named instead of becoming a silent skip.
FURINA_DEFERRED_TO_FD: set[str] = set()

# Curtain Call (R85) deferred twelve cards to a consolidation sprint while
# their grammar had no C# home. "Take a Bow" (2026-07-27) shipped all of it --
# the six activity-triggered Powers, the Body-Slam encore read, the three new
# predicates, grow_damage, refresh_all_auras and the salon-member hit count --
# so FURINA_DEFERRED_TO_CONSOLIDATION is DELETED rather than left empty. The
# next deferral gets a fresh set with its own gate written down; a dormant
# escape hatch just makes the next silent skip easy.

# Cards whose UPGRADE is unauthored because the delta it used to carry died
# with a retired grammar. Same curation rule as above: an unupgradable card
# is a dead campfire choice, so the gap is named and gated, never tolerated
# silently.
#
# CLOSED by F-B1 (2026-07-24). florid_cadenza's only ratified delta had been
# {fanfare_cost: -3}; it is now a threshold reader whose upgrade DROPS the
# gate ({condition: unconditional}) rather than adding cards. Kept as an
# empty set rather than deleted, so the invariant "every card has an upgrade
# path" is asserted positively and the next gap has somewhere to be named.
FURINA_UPGRADE_GAP_PENDING_FB1: set[str] = set()


def _generated_source(class_name: str) -> str:
    """The SHIPPED C# for a generated card, read off disk.

    Used where a fixture is making a claim about the artifact the game loads
    rather than about the generator's output for a hypothetical card. The two
    agree by construction -- `--check` fails the build if they drift -- but
    only one of them is what actually ships, and a test that has a choice
    should assert against that one.
    """
    path = (gen.FURINA_PROFILE.out_dir / f"{class_name}.cs")
    assert path.exists(), (
        f"{class_name} is not generated -- regenerate with "
        "`python tools/gen_roster_cards.py --character furina`")
    return path.read_text(encoding="utf-8")


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
    # dress_rehearsal since Curtain Call B: crowd_work became a Power (its
    # encore_cost install gate was dropped with the conversion), so the
    # spend-gate emission pin moves to the surviving Spend-2 card.
    rehearsal = gen.emit(by_id["dress_rehearsal"], gen.FURINA_PROFILE)
    assert (
        "CustomResources<EncoreResource>.SetCanonicalCost(this, 2);"
        in rehearsal
    )
    # Its upgrade softens the gate (Spend 2 -> 1), so the face renders the
    # templated form rather than a bare literal.
    assert "Spend {IfUpgraded:show:1|2} [gold]Encore[/gold]." in rehearsal

    # ENCORE is the only card-level resource gate. Fanfare's retired with the
    # spend grammar ("The Tide Turns", F-A4): it is a read-only momentum stat
    # and no card spends it, so no Fanfare cost line may be emitted anywhere.
    # (Blocked cards are skipped: emit() over unregistered grammar is a crash
    # by design -- UNPARSEABLE discipline -- not a parity statement.)
    for card in _furina_cards():
        if gen.blocked_reason(card, gen.FURINA_PROFILE):
            continue
        emitted = gen.emit(card, gen.FURINA_PROFILE)
        assert "CustomResources<FanfareResource>.SetCanonicalCost" not in emitted
        assert "CustomResources<FanfareResource>.Cost(" not in emitted

    crescendo = gen.emit(by_id["crescendo"], gen.FURINA_PROFILE)
    # Legibility sprint (2026-07-24): the Fanfare rider renders through a
    # CalculatedDamageVar (face/preview and hit share one value path) instead
    # of inline PrintedDamage arithmetic. The scaling lives in the multiplier.
    # Untouched by F-A -- READING the meter is exactly what survives.
    assert "FurinaResources.ReadableFanfare(card.Owner.Creature) / 2" in crescendo
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


def test_register_never_reaches_the_generated_csharp():
    """`register` is a SHEET-SIDE voice label. Codegen tolerates it and
    ignores it: strip the field and every generated file must come out
    byte-identical.

    Asserted as byte-identity rather than as "the word does not appear",
    because the failure that matters is not a stray literal -- it is the
    field silently participating in a decision (a tag, a keyword, a sort
    order, a rarity nudge). An output diff catches every form of that; a
    substring search catches only the clumsiest.

    The engine-side half of the same law lives in the register lint
    (tools/lint_register_isolation.py): nothing under tier0/engine or tier05
    may READ the field either. Together they say the column is documentation
    until somebody rules otherwise.
    """
    cards = _furina_cards()
    stripped = [{k: v for k, v in card.items() if k != "register"}
                for card in cards]
    assert any("register" in card for card in cards), (
        "no card carries a register -- this test would be vacuous")

    for card, bare in zip(cards, stripped):
        if gen.blocked_reason(card, gen.FURINA_PROFILE) is not None:
            continue
        assert (gen.emit(card, gen.FURINA_PROFILE)
                == gen.emit(bare, gen.FURINA_PROFILE)), card["id"]


def test_furina_profile_emits_every_non_kit_card():
    all_ids = {card["id"] for card in _furina_cards()}
    generated = {
        card["id"]
        for card in _furina_cards()
        if gen.blocked_reason(card, gen.FURINA_PROFILE) is None
    }
    withheld = FURINA_HAND_WRITTEN | FURINA_DEFERRED_TO_FD
    assert generated == all_ids - withheld

    # A7 IS RELEASED (2026-07-29) and this is the positive assertion that
    # replaces the deferral check. Written as its own line rather than left to
    # the set arithmetic above, because "unheard_confession generates" is the
    # single fact two sprints of deferral were about, and it should fail by
    # name if it ever regresses.
    assert "unheard_confession" in generated
    assert gen.blocked_reason(
        by_id_of(_furina_cards())["unheard_confession"],
        gen.FURINA_PROFILE) is None

    # The deferral must be for the REASON we think it is. A card that stopped
    # generating for some unrelated breakage would otherwise hide inside the
    # curated set and read as intentional. Vacuous while a set is empty, and
    # deliberately kept so: it re-arms the moment anything is deferred again.
    for cid in FURINA_DEFERRED_TO_FD:
        reason = gen.blocked_reason(by_id_of(_furina_cards())[cid],
                                    gen.FURINA_PROFILE)
        assert reason is not None, cid

    # Both deferral sets are empty and asserted so. G-A2 emptied FD; the "Take
    # a Bow" consolidation sprint emptied the Curtain Call set by shipping the
    # C# parity R85 gated on, and DELETED it rather than leaving an empty
    # escape hatch behind -- an empty set is an invitation, and the positive
    # assertion above already covers the invariant it existed to state.
    assert not FURINA_DEFERRED_TO_FD

    manifest = json.loads(
        gen.FURINA_PROFILE.manifest.read_text(encoding="utf-8")
    )
    # 79 cards: A4 (playtest-2 red-pen, 2026-07-28) CUT rising_tide, A12 added
    # the salon cap-raise power back, and the FANFARE REWORK (2026-07-28)
    # added ONE more -- take_your_bow, the Track D on-demand-bow probe.
    #
    # `blocked` HELD AT 2 THROUGH THE REWORK, which is the number worth
    # reading here: the sprint introduced four new codegen surfaces (base-card
    # `retain`, the `crash_fanfare` and `salon_bow` ops, and a Companion-tempo
    # bonus_formula) and every one of them was IMPLEMENTED rather than
    # deferred. Each surfaced first as a loud block -- "card field(s)
    # ['retain'] not understood", "op 'crash_fanfare'" -- which is the design
    # working: a card that retains in the sim and does not in the game is
    # exactly the divergence the blocker exists to stop.
    #
    # The two still withheld are the hand-written kit Burst and A7's
    # unheard_confession, both unchanged (as of that sprint).
    # COMPENSATION PASS (2026-07-28): 79 -> 82, three new common readers.
    # `blocked` HELD AT 2 AGAIN, and this time for the quieter reason: the pass
    # introduced no new codegen surface at all. Every card it added or rewrote
    # is built from ops the generator already emits, which is what "reader
    # density" means mechanically -- more cards on the rails the rework built,
    # not more rails.
    #
    # A7 (2026-07-29): blocked 2 -> 1. Every card on this sheet now exists in
    # the actual game except the hand-written kit Burst, which is not a gap.
    # The count is the whole point of the deferral discipline: it was 2 for two
    # sprints, visibly, and it moved when the gap closed rather than when
    # somebody remembered.
    assert manifest["coverage"] == {
        "total": 82,
        "generated": 81,
        "blocked": 1,
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
    #
    # UN-DEFERRED by the "Take a Bow" consolidation sprint. torrential_turn is
    # the pool's only single-target bonus_vs_aura card, and while its
    # refresh_all_auras op had no C# home this could only run on a direct
    # emit() -- a fixture describing a card that did not ship. Now it reads
    # the GENERATED FILE, so the assertion is about the artifact the game
    # loads rather than about what the generator would produce if asked.
    torrential = _generated_source("TorrentialTurn")

    assert "new CalculationBaseVar(10m)" in torrential
    assert "new ExtraDamageVar(3m)" in torrential
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

    # The damaging-skill cadence pin has now moved twice for the same reason:
    # Curtain Call B retyped usher_the_waves to a plain attack, moving the pin
    # to undercurrent, and A5 (2026-07-28) retyped undercurrent the same way.
    # flood_of_emotion is a damaging skill that KEEPS its skill_tag.
    damaging_skill = gen.emit(by_id["flood_of_emotion"], gen.FURINA_PROFILE)
    assert "IElementalCard" in damaging_skill
    assert "public Element Element => Element.Hydro;" in damaging_skill

    # A5's other half, pinned as a POSITIVE statement of the cadence law
    # rather than left as an absence: undercurrent is now a plain attack, and
    # a plain attack never applies hydro no matter how much damage it deals.
    # This is the assertion that fails if someone re-adds its skill_tag.
    retyped_aoe = gen.emit(by_id["undercurrent"], gen.FURINA_PROFILE)
    assert "IElementalCard" not in retyped_aoe
    assert "KleeKeywords.AppliesHydro" not in retyped_aoe

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

    # courtroom_drama, the softlock's second witness, became a Power at
    # Curtain Call B (cross_examination is deferred codegen grammar, R85),
    # so its half of this pin retired with the shape. The regression stays
    # covered: stage_lights above is the two-apply_power one-var case, and
    # test_named_power_delta_follows_the_name pins the name-binding rule
    # the drama half existed to witness.


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

    # macaron_break carries the negative pin. It moved here at Curtain Call C
    # because the cards that held it (crowd_work, then swelling_overture) had
    # become deferred grammar and emit() crashes by design on grammar it does
    # not know. "Take a Bow" shipped both, so the constraint is gone -- but
    # the pin stays on macaron_break, because a non-basic is a non-basic and
    # moving it back would be churn for its own sake.
    non_basic = gen.emit(by_id["macaron_break"], gen.FURINA_PROFILE)
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


def test_a_random_deploy_emits_a_null_and_says_so_on_the_face():
    """A11: `member: random` -> null, which Deploy resolves per iteration off
    the SHARED combat stream.

    The face assertion is not decoration. The shared template says "typed",
    which was true while every deploy named its member; on a random deploy
    that word implies a choice the player does not have. A card whose text
    still claims a type is worse than one that says nothing.
    """
    by_id = {card["id"]: card for card in _furina_cards()}
    debut = gen.emit(by_id["salon_debut"], gen.FURINA_PROFILE)
    named = gen.emit(by_id["surintendante_chevalmarin"], gen.FURINA_PROFILE)

    assert "SalonMemberPower.Deploy(choiceContext, Owner.Creature, 1, this, null)" in debut
    # B5 reworded this from "RANDOM Salon Member(s)" to the named-member
    # grammar; the requirement is unchanged -- the face must say the member is
    # not chosen.
    assert "random Salon Member" in debut
    assert "SalonMemberTips.ForCard(base.ExtraHoverTips, this, randomMember: true)" in debut
    assert "members: new[]" not in debut

    # The Common it was de-duped FROM keeps naming its member. If this ever
    # goes null too, the de-dupe has been undone in the other direction.
    assert "this, SalonMember.Chevalmarin)" in named


def test_every_deploy_card_names_its_member_and_carries_its_tip():
    """B5 (playtest-2 defect, 2026-07-28), swept across the whole sheet.

    Written as a SWEEP rather than as one case per card on purpose: the
    defect was that eight cards shared one nameless paragraph, so a fixture
    that named the cards individually would leave the ninth to be found in
    play. Any future deploy card is covered the moment it is authored.
    """
    seen = 0
    for card in _furina_cards():
        deploys = [e for e in card.get("effects", [])
                   if e.get("op") == "apply_power"
                   and e.get("power") == "salon_member"]
        if not deploys or gen.blocked_reason(card, gen.FURINA_PROFILE):
            continue
        seen += 1
        source = gen.emit(card, gen.FURINA_PROFILE)

        # The face names WHO -- every member this card can field.
        for eff in deploys:
            name = gen.SALON_MEMBER_NAMES[eff.get("member", "crabaletta")]
            assert f"[gold]{name}[/gold]" in source, (card["id"], name)

        # The cap paragraph is GONE from the face. It moved to the tip, and
        # since A12 the number in it is not even a constant any more.
        assert "Maximum 3" not in source, card["id"]
        assert "bows its OLDEST member out" not in source, card["id"]

        # ...and the tip that replaced it is attached.
        assert "SalonMemberTips.ForCard(" in source, card["id"]

    assert seen == 9, f"expected 9 deploy cards, swept {seen}"


def test_the_face_and_the_tooltip_call_members_the_same_thing():
    """The face says "Add Gentilhomme Usher" and the tooltip explaining him is
    titled "Gentilhomme Usher". Those strings live in two languages -- Python
    and C# -- so nothing but a test makes them agree, and if they drift the
    player cannot tell the two are about the same member."""
    tips = (Path(gen.REPO) / "klee-mod" / "KleeCode" / "Cards"
            / "SalonMemberTips.cs").read_text(encoding="utf-8")
    loc = (Path(gen.REPO) / "klee-mod" / "KleeCode"
           / "KleeMod.cs").read_text(encoding="utf-8")
    for member, name in gen.SALON_MEMBER_NAMES.items():
        if member == "random":
            continue
        assert f'"{name}"' in tips, (member, name)
        assert f'"{name}"' in loc, (member, name)


def test_an_unrecognised_member_is_refused_by_name():
    """The member value is emitted through a lookup, and a lookup miss is a
    KeyError -- a stack trace mid-emit, not a decision. Every other
    unexpressible value on this sheet is refused by name; so is this one."""
    card = {
        "id": "not_a_real_card", "name": "Not A Real Card", "cost": 1,
        "type": "skill", "rarity": "common", "solve": ["utility"],
        "archetypes": ["salon"], "role": "enabler",
        "effects": [{"op": "apply_power", "power": "salon_member",
                     "amount": 1, "target": "self", "member": "neuvillette"}],
    }
    reason = gen.blocked_reason(card, gen.FURINA_PROFILE)
    assert reason is not None
    assert "neuvillette" in reason, reason


def test_the_per_member_slope_renders_through_the_calculated_rail():
    """A13/A14: both halves of the per-member slope, pinned STRUCTURALLY.

    Deliberately not a text assertion. Both cards' faces read the same whether
    the rider is there or not -- "Deal {CalculatedDamage} damage" renders
    identically over a live multiplier and over a var that never scales -- and
    that is exactly how B1 and the GrandFinale regression both got past a
    green suite. So this pins the multiplier expression itself.
    """
    by_id = {card["id"]: card for card in _furina_cards()}
    house = gen.emit(by_id["house_call"], gen.FURINA_PROFILE)
    dinner = gen.emit(by_id["dinner_service"], gen.FURINA_PROFILE)

    # A14: damage half. Base 6, slope 2, multiplier is the raw member count --
    # no divisor, because the salon is a capped count where every member is a
    # full step (the Fanfare/Charge riders divide; this one must not).
    assert "new CalculationBaseVar(6m)" in house
    assert "new ExtraDamageVar(2m)" in house
    assert (
        "new CalculatedDamageVar(ValueProp.Move).WithMultiplier("
        "static (card, _) => SalonMemberPower.Count(card.Owner.Creature))"
        in house
    )
    assert "DynamicVars.CalculationBase.UpgradeValueBy(2m);" in house

    # A13: block half. Same slope, same rail, on the op that had no rider
    # rail at all until B1 built one.
    assert "new CalculationBaseVar(2m)" in dinner
    assert "new CalculationExtraVar(2m)" in dinner
    assert (
        "new CalculatedBlockVar(ValueProp.Move).WithMultiplier("
        "static (card, _) => SalonMemberPower.Count(card.Owner.Creature))"
        in dinner
    )

    # The threshold shape both cards replace must be GONE. Leaving it would
    # pay the old conditional on top of the new slope.
    for source in (house, dinner):
        assert "SalonMemberPower.Count(Owner.Creature) > 0" not in source


def test_a_converted_rider_always_declares_itself_on_the_face():
    """The L-C bargain, both ops.

    A converted rider's arithmetic moves to the hover tip, so the face MUST
    keep a short marker naming the mechanism -- otherwise a card read on a
    reward screen is a flat number with no hint that it scales. The damage
    path always emitted this; the block path did not, so B1's fix traded a
    silent drop for a silent number. Thunderous Ovation is the regression
    case: it is the card B1 was reported against.
    """
    by_id = {card["id"]: card for card in _furina_cards()}
    thunder = gen.emit(by_id["thunderous_ovation"], gen.FURINA_PROFILE)
    dinner = gen.emit(by_id["dinner_service"], gen.FURINA_PROFILE)
    house = gen.emit(by_id["house_call"], gen.FURINA_PROFILE)

    assert "Scales with [gold]Fanfare[/gold]." in thunder
    assert "Scales with [gold]Salon[/gold]." in dinner
    assert "Scales with [gold]Salon[/gold]." in house
    # Not "Member": rpartition on the formula would name it that, and nothing
    # in the game or on the sheet calls the stage that.
    assert "[gold]Member[/gold]" not in dinner + house

    # And the rate itself reaches the tip, with the block/damage noun set.
    assert "FurinaRiderTips.ForCard(base.ExtraHoverTips, this, salonPer: 2)" in house
    assert (
        "FurinaRiderTips.ForCard(base.ExtraHoverTips, this, salonPer: 2, "
        "salonGrantsBlock: true)" in dinner
    )


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
    # Anchored to THIS FILE, not to the working directory. It was written as
    # a bare relative `Path(...)` and passed every full-repo pytest run,
    # because those all start at the repo root -- but validate.ps1's portable
    # suite runs pytest from the STAGED PACKAGE directory, where the relative
    # path resolves to nothing and the test died with FileNotFoundError
    # instead of checking anything. A test that only works from one cwd is a
    # test that silently stops running when the harness moves.
    repo = Path(__file__).resolve().parent.parent.parent
    source = (
        (repo / "klee-mod/KleeCode/Cards/Furina/LetThePeopleRejoice.cs")
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
    assert f"FurinaResources.ReadableFanfare(card.Owner.Creature) / {div}" in source
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
    # Both cards were deferred grammar when this fixture was written and could
    # only be checked through emit(). "Take a Bow" shipped them, so the
    # fixture now reads the generated files -- the tips are a DISPLAY claim,
    # and a display claim should be made against what is displayed.
    crescendo = _generated_source("Crescendo")
    assert "Scales with [gold]Fanfare[/gold]." in crescendo
    assert "+1 damage per 2" not in crescendo
    assert (
        "FurinaRiderTips.ForCard(base.ExtraHoverTips, this, "
        "fanfarePer: 1, fanfareStep: 2)" in crescendo
    )

    torrential = _generated_source("TorrentialTurn")
    assert "Bonus damage vs. an elemental aura." in torrential
    assert "+3 damage if the enemy" not in torrential
    assert "FurinaRiderTips.ForCard(base.ExtraHoverTips, this, auraBonus: 3)" in torrential


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
    # The VAR, not just the sentence. Caught during the 2026-07-28 sprint:
    # A5's Times-var insertion captured the BonusPer lines into its own branch
    # by indentation, so grand_finale silently stopped declaring BonusPer and
    # lost its campfire upgrade -- with the whole 1305-test suite green,
    # because every assertion on this card read its TEXT. The bare sentence
    # renders identically either way; only the var declaration differs.
    assert 'new DynamicVar("BonusPer", 2m)' in big_one, (
        "grand_finale lost its BonusPer var: the bonus_per_detonation upgrade "
        "is silently dead while the card text still reads correctly")


def test_crackle_prints_the_sentence_its_semantics_were_pinned_against():
    """Audit sec.4 item 5: Crackle's semantics are pinned twice, its SENTENCE never.

    `test_crackle_spark_is_priced_by_the_discard` and
    `test_crackle_upgrade_applies_r36_deltas` both pin what the card DOES.
    Neither reads what the card SAYS, and the card's text is the only place a
    player learns that an empty hand pays nothing -- the whole R10 replacement
    design ("discard is a real cost, not an engine, for Klee").

    The "1" in "gain 1 Spark per card discarded" is a LITERAL, while every
    other number on the face is a bound `{Var:diff()}` token. That is safe
    today for exactly one reason: R36 moved `Discards` and `Sparks` by the
    same delta, so `Math.Min(Sparks, picked.Count)` always equals the number
    of cards actually discarded. Bump one without the other and the sentence
    starts lying with the whole lint suite green -- which is why the pin below
    asserts the sentence AND the invariant that makes it true, not just the
    sentence.
    """
    klee_by_id = {
        card["id"]: card
        for card in yaml.safe_load(gen.SHEET.read_text(encoding="utf-8"))
    }
    crackle = gen.emit(klee_by_id["crackle"], gen.KLEE_PROFILE)

    assert (
        '"Deal {Damage:diff()} damage to a random enemy. '
        'Discard {Discards:diff()} card{Discards:plural:|s}: '
        'gain 1 [gold]Spark[/gold] per card discarded."' in crackle
    ), crackle

    # The plural token, not a hardcoded "s": Crackle+ discards 2.
    assert "{Discards:plural:|s}" in crackle

    # The invariant the literal "1" rests on. Both vars, same delta.
    assert 'DynamicVars["Discards"].UpgradeValueBy(1m);' in crackle
    assert 'DynamicVars["Sparks"].UpgradeValueBy(1m);' in crackle

    # "empty hand = no Spark" is the design, and it lives in the Min, not in
    # the text. The sentence is only honest while this clamp is here.
    assert ('Math.Min(DynamicVars["Sparks"].IntValue, picked.Count)'
            in crackle), crackle
