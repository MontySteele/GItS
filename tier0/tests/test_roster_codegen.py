"""Character-profile and honesty guards for the roster card generator."""

from __future__ import annotations

import json
import re
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
#
# THE NEXT GAP ARRIVED 2026-08-06 and CLOSED 2026-08-24. `encore_performance`
# was named here because its only delta was `copy_cost_override: 0` and
# R110/S-1 (S13 family X3) made the base card cost 0 -- a 0-cost card cannot
# be discounted to 0, so the delta meant nothing. [USER] deleted it (Y-4) and
# the generator correctly emitted the card with no upgrade path.
#
# M27 (RULED 2026-08-24) authored the replacement -- `{retain: true}`, which
# answers the card's real weakness (target-dependence: a 0-cost Rare that does
# nothing unless a Spotlighted card is in hand) by buying TIMING rather than a
# bigger copy. That fired this entry's gate exactly as it was written:
# "deleted together with both curated entries in
# `tools/lint_upgrade_coverage.py` (SHEET_EXEMPT for layer 1, CODEGEN_DEBT for
# layer 2). Three registers, one debt, one removal." All three went together.
#
# Kept as an empty set rather than deleted, the same way F-B1 and F-D left it:
# the invariant "every non-kit card has an upgrade path" is asserted
# positively below, and the next gap needs somewhere to be named.
#
# THE NEXT GAP ARRIVED 2026-08-25, at W3 (EB-118 Phase 3, R211), and CLOSED
# the same day at EB-140. It was a DIFFERENT KIND from every entry above it:
# those were cards whose sheet delta had died with a retired grammar -- nothing
# to express. This one had a perfectly good ratified delta that TIER0 APPLIED
# CORRECTLY and the GENERATOR COULD NOT EMIT -- `take_it_from_the_top`'s
# `{conditional_damage: +4}` (10 -> 14 on a branch), with Klee's
# `hold_the_line` the same gap on the Block side.
#
# IT WAS NOT ANSWERED WITH A DESIGN CHANGE, which is the part to keep. R211's
# deltas stand as printed; the EMITTER learned both keys, on the shape that
# already shipped -- `curtain_cue`'s `(IsUpgraded ? 4 : 3)` inside a branch
# with `{IfUpgraded:show:4|3}` rendered beside it. Both ids left this set and
# `lint_upgrade_coverage.CODEGEN_DEBT` in the SAME commit as the emitter
# change: two registers, one debt, one removal.
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


def test_klee_profile_remains_the_legacy_default():
    assert gen.KLEE_PROFILE.sheet == gen.SHEET
    assert gen.KLEE_PROFILE.out_dir == gen.OUT_DIR
    assert gen.KLEE_PROFILE.namespace == "KleeMod.Cards.Generated"
    assert gen.KLEE_PROFILE.cadence == "catalyst_attack"


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


def _ethereal_probe(**kw) -> dict:
    card = {
        "id": "eb118_codegen_probe",
        "name": "EB118 Codegen Probe",
        "cost": 1,
        "type": "skill",
        "rarity": "common",
        "character": "klee",
        "effects": [{"op": "block", "amount": 5}],
    }
    card.update(kw)
    return card


def test_base_ethereal_rides_the_canonical_keyword_rail(monkeypatch):
    """EB-118. The keyword IS the implementation -- the game's own
    end-of-turn sweep reads `Keywords` and exhausts the card -- so a card
    ruled Ethereal from print emits a keyword and no body, and its
    remove-on-upgrade delta emits the one line canon uses (Apparition,
    EchoForm, VoidForm each do exactly this and nothing else).
    """
    monkeypatch.setattr(gen, "_upgrade_deltas",
                        {"eb118_codegen_probe": {"remove": "ethereal"}})
    card = _ethereal_probe(ethereal=True)
    assert gen.blocked_reason(card, gen.KLEE_PROFILE) is None
    source = gen.emit(card, gen.KLEE_PROFILE)
    assert ("public override IEnumerable<CardKeyword> CanonicalKeywords =>\n"
            "        new[] { CardKeyword.Ethereal };") in source
    assert gen.build_upgrade(card) == ["RemoveKeyword(CardKeyword.Ethereal);"]
    # No hook, no power, no per-card sweep: the mod reuses the game's.
    assert "Ethereal" not in source.replace("CardKeyword.Ethereal", "")


def test_ethereal_precedes_exhaust_in_the_keyword_array(monkeypatch):
    # Canon spells the common pairing in this order (Apparition), and the two
    # keywords ride the same array.
    monkeypatch.setattr(gen, "_upgrade_deltas", {})
    source = gen.emit(_ethereal_probe(ethereal=True, exhaust=True),
                      gen.KLEE_PROFILE)
    assert "new[] { CardKeyword.Ethereal, CardKeyword.Exhaust };" in source


def test_a_card_without_the_field_never_mentions_the_keyword(monkeypatch):
    monkeypatch.setattr(gen, "_upgrade_deltas", {})
    assert "Ethereal" not in gen.emit(_ethereal_probe(), gen.KLEE_PROFILE)


def test_remove_delta_must_match_a_keyword_the_card_prints(monkeypatch):
    """`remove:` is checked against the base card by VALUE. Removing a
    keyword the card never printed would generate an upgraded copy identical
    to its base -- a dead campfire choice, which R24 forbids -- so it is
    reported as a sheet/card mismatch rather than emitted."""
    monkeypatch.setattr(gen, "_upgrade_deltas",
                        {"eb118_codegen_probe": {"remove": "ethereal"}})
    assert gen.upgrade_plan(_ethereal_probe())[1] == (
        "delta 'remove: ethereal' on a card that does not print ethereal "
        "(sheet/card mismatch)")
    monkeypatch.setattr(gen, "_upgrade_deltas",
                        {"eb118_codegen_probe": {"remove": "exhaust"}})
    assert gen.upgrade_plan(_ethereal_probe(ethereal=True))[1] == (
        "delta 'remove: exhaust' on a card that does not print exhaust "
        "(sheet/card mismatch)")


def test_register_never_reaches_the_generated_csharp():
    """`register` is a SHEET-SIDE voice label. Codegen tolerates it and
    ignores it: strip the field and every generated file must come out
    byte-identical. Run over the prototype surface's Furina rows since legacy
    cleanup stage 6 deleted her shipped sheet.

    Asserted as byte-identity rather than as "the word does not appear",
    because the failure that matters is not a stray literal -- it is the
    field silently participating in a decision (a tag, a keyword, a sort
    order, a rarity nudge). An output diff catches every form of that; a
    substring search catches only the clumsiest.

    The engine-side half of the same law lives in the register lint
    (tools/lint_register_isolation.py): nothing under tier0/engine or tier05
    may READ the field either.
    """
    import copy
    from tools import gen_prototype_cards as gp

    profile = gp._profile_for("furina")
    cards = [c for c in gp._rows() if c.get("character") == "furina"
             and "register" in c]
    assert cards, "no surface row carries a register -- vacuous"
    for row in cards:
        card = copy.deepcopy(row)
        gp.effective_upgrade(card)
        if gen.blocked_reason(card, profile) is not None:
            continue
        bare = {k: v for k, v in card.items() if k != "register"}
        assert gen.emit(card, profile) == gen.emit(bare, profile), card["id"]


def test_aoe_aura_riders_stay_per_target():
    # NOT a display nicety -- a correctness guard. AttackCommand resolves a
    # CalculatedDamageVar ONCE with singleTarget == null, so converting an AoE
    # aura rider would collapse a per-enemy "does this one have an aura?"
    # decision into a single flat value for the whole board. Emitted off a
    # probe row in Crashing Waves' shape: the last shipped AoE aura rider
    # left with v2 Furina (the Salon's Tab, 2026-10-05), and the emitter
    # path stays live for the next one.
    card = {"id": "proto_fs_probe_waves", "name": "Probe Waves",
            "character": "furina", "cost": 1, "type": "attack",
            "rarity": "uncommon",
            "effects": [{"op": "damage", "amount": 8,
                         "target": "all_enemies", "bonus_vs_aura": 5}]}
    assert gen.blocked_reason(card, gen.FURINA_PROFILE) is None
    source = gen.emit(card, gen.FURINA_PROFILE)
    assert "foreach (var auraTarget" in source
    assert "AuraCmd.Find(auraTarget)" in source
    assert "CalculatedDamageVar" not in source


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


def test_a_non_basic_strike_carries_the_strike_tag():
    # 2026-09-29, a Varka seat: Strike Dummy paid on Strike and Strike+ and
    # not on Oathsworn Strike. The base game tags its offered Strikes (Twin
    # Strike, Perfected Strike); a sheet row says so with `tags: [strike]`.
    # Read off the COMMITTED C#, which is what ships.
    cs = (Path(gen.__file__).resolve().parents[1] / "klee-mod" / "KleeCode"
          / "Cards" / "Prototype" / "Generated" / "ProtoVkOathswornStrike.cs")
    assert "CanonicalTags => new() { CardTag.Strike };" in cs.read_text(
        encoding="utf-8")

    # A basic may not take the offer's word: its answer is `basic_tag:`.
    basic = {"id": "proto_probe_basic", "name": "Probe", "cost": 1,
             "type": "attack", "rarity": "basic", "tags": ["strike"],
             "effects": [{"op": "damage", "amount": 6, "target": "enemy"}]}
    assert "basic_tag" in (gen.card_level_reason(basic) or "")


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


# ---------------------------------------------------------------------------
# S1 parity sweep hardening (L1b / L2 / L8 / SYS-14). Every test below sweeps
# the SHIPPED artifacts on disk across ALL generated profiles -- the classes
# the game actually loads -- because each pins a defect that shipped green
# while the generator-level checks passed.

_ALL_GENERATED_DIRS = [
    gen.KLEE_PROFILE.out_dir,
    gen.FURINA_PROFILE.out_dir,
    gen.KOKOMI_PROFILE.out_dir,
]


def _all_generated_sources() -> dict[str, str]:
    out = {}
    for d in _ALL_GENERATED_DIRS:
        for path in sorted(d.glob("*.cs")):
            out[str(path.relative_to(gen.REPO))] = path.read_text(
                encoding="utf-8")
    return out


def test_onupgrade_bumped_vars_have_a_reader():
    """L1b (SYS-1): a var bumped in OnUpgrade must be READ somewhere --
    OnPlay, the description, or a Calculated*Var that consumes it. The
    inert-var shape is how tideline_watch and sayu_daruma_gift shipped
    upgrades that displayed and granted the base number: OnUpgrade moved
    `BlockNextTurn` and nothing ever read it back.

    CalculationBase / CalculationExtra / ExtraDamage are exempt only when a
    Calculated*Var is declared (it consumes them at runtime) -- the same
    conditional exemption lint_generated_structure applies to orphan vars.
    """
    import re
    trio = {"CalculationBase", "CalculationExtra", "ExtraDamage"}
    bump = re.compile(
        r'DynamicVars(?:\["(?P<q>\w+)"\]|\.(?P<p>\w+))\.UpgradeValueBy')
    offenders = []
    for rel, src in _all_generated_sources().items():
        for m in bump.finditer(src):
            name = m.group("q") or m.group("p")
            if name in trio and "new Calculated" in src:
                continue
            # Occurrences that are not the OnUpgrade bump and not the
            # declaration: a face token {Name:...}, an OnPlay read, or a
            # snapshot through the var.
            reads = (
                src.count(f"{{{name}:")                     # face token
                + src.count(f'DynamicVars["{name}"].IntValue')
                + src.count(f'DynamicVars["{name}"]).Calculate')
                + src.count(f"DynamicVars.{name}.BaseValue")
                + src.count(f"DynamicVars.{name}.Calculate")
                + src.count(f"DynamicVars.{name}, ")        # passed whole
                + src.count(f"DynamicVars.{name})")
            )
            if reads == 0:
                offenders.append(f"{rel}: OnUpgrade bumps {name}")
    assert not offenders, (
        "OnUpgrade moves a number nothing reads back (the SYS-1 inert-var "
        "shape):\n  " + "\n  ".join(offenders))


def test_cadence_comment_comes_from_the_profile():
    """L2 (SYS-10): the cadence doc-comment must match the PROFILE, never a
    hardcoded character branch -- all 18 elemental Kokomi cards shipped
    carrying Furina's skill-grade sentence while her ruled cadence (R52) is
    catalyst."""
    for profile in (gen.KLEE_PROFILE, gen.FURINA_PROFILE, gen.KOKOMI_PROFILE):
        for path in sorted(profile.out_dir.glob("*.cs")):
            src = path.read_text(encoding="utf-8")
            if "public Element Element =>" not in src:
                continue
            if "this companion attack applies its element" in src:
                continue                       # companion cadence exemption
            if profile.cadence == "catalyst_attack":
                assert "catalyst-grade cadence" in src, path
                assert "damaging Skills" not in src, (
                    f"{path}: carries the skill-grade sentence on a "
                    "catalyst profile")
            else:
                assert "damaging Skills, Burst-tagged cards" in src, path


def test_salon_replacement_multiplier_is_never_a_bare_literal():
    """SYS-14 (lint candidate L5): the replacement multipliers reach the
    emitted C# only as SalonConstants members, never as inline `? 2 : 1` /
    `? 3 : 1` -- a bare literal escapes the constant-parity gate, which is
    how SalonDebut and OverflowingHospitality shipped one."""
    for rel, src in _all_generated_sources().items():
        # The precise expression, not any `? 2 : 1` -- an IsUpgraded literal
        # swap (CurtainCue) is a different, legitimate shape.
        assert ("salonReplacements > 0 ? 2 : 1" not in src
                and "salonReplacements > 0 ? 3 : 1" not in src), (
            f"{rel}: bare replacement multiplier literal")


def _discard_probe(**eff) -> dict:
    """A minimal Kokomi-shaped card whose only effect is one `discard`."""
    fx = {"op": "discard", "amount": 2}
    fx.update(eff)
    return {
        "id": "discard_select_probe",
        "name": "Discard Select Probe",
        "cost": 1,
        "type": "skill",
        "rarity": "common",
        "solve": ["utility"],
        "archetypes": ["assist"],
        "role": "glue",
        "effects": [fx],
    }


def test_a_chosen_discard_emits_the_selection_screen_not_a_random_loop(
        monkeypatch):
    """`select: chosen` is a claim about WHO PICKS, and the emitter used to
    drop it on the floor: every `discard` op generated the random-victim
    loop, so three EB-69 cards ruled as chosen discards shipped a C# body
    that discarded at random and a face that said so.

    The chosen branch rides the SAME verified idiom `discard_for_sparks`
    uses -- one `FromHandForDiscard` selection, then one batch
    `CardCmd.Discard` -- which is also what makes the two engines agree on
    selection TIMING: the whole batch is picked before any of it leaves the
    hand, matching tier0 `_op_discard`'s chosen path.
    """
    monkeypatch.setattr(gen, "_upgrade_deltas", {})
    src = gen.emit(_discard_probe(select="chosen"), gen.KOKOMI_PROFILE)
    assert "CardSelectCmd.FromHandForDiscard(" in src
    assert "CardSelectorPrefs.DiscardSelectionPrompt, 2)" in src
    assert "null, this)).ToList();" in src
    assert "await CardCmd.Discard(choiceContext, picked);" in src
    # The random loop must be GONE, not merely accompanied.
    assert "Rng.CombatTargets.NextItem" not in src
    # ... and the face must not keep claiming a random victim.
    assert "Discard 2 cards." in src
    assert "random" not in src


def test_a_default_discard_keeps_the_random_loop(monkeypatch):
    """The other half of the pin. Random stays the DEFAULT and stays a
    re-polling loop -- every card that discards without `select:` was priced
    against it, and a silent flip to a selection screen would re-price them.
    """
    monkeypatch.setattr(gen, "_upgrade_deltas", {})
    src = gen.emit(_discard_probe(), gen.KOKOMI_PROFILE)
    assert "Rng.CombatTargets.NextItem(pool);" in src
    assert "CardSelectCmd.FromHandForDiscard" not in src
    assert "Discard 2 random cards." in src


def _add_before_probe() -> dict:
    return {
        "id": "add_before_probe",
        "name": "Add Before Probe",
        "cost": 0,
        "type": "skill",
        "rarity": "common",
        "character": "kokomi",
        "archetypes": ["assist"],
        "role": "glue",
        "effects": [{"op": "draw", "amount": 1},
                    {"op": "exhaust_from", "amount": 1, "select": "chosen"}],
    }


def test_codegen_honours_the_add_before_position(monkeypatch):
    """`add_before` is a tier0 applier key (send_the_runner+'s ruled middle
    insertion). This file used to pin the REFUSAL -- the emitter appended, full
    stop, so the delta had to come back unexpressible rather than ship an
    upgraded card that resolved in a different order from the one the sim
    upgrades to. EB-122 built the position, so the pin becomes the positive
    claim: the gated effect is emitted BEFORE the op the key names, in the body
    AND on the face.

    D2a's order is draw 2 -> discard 1 chosen -> exhaust 1 chosen. Appended, it
    read draw / exhaust / discard, and the player exhausted before being asked
    what to throw -- a different card."""
    card = _add_before_probe()
    monkeypatch.setattr(gen, "_upgrade_deltas", {
        "add_before_probe": {"add": {"op": "discard", "amount": 1,
                                     "select": "chosen"},
                             "add_before": "exhaust_from"}})
    assert gen.upgrade_plan(card)[1] is None
    src = gen.emit(card, gen.KOKOMI_PROFILE)
    gated = src.index("var pickedUpgrade")
    exhaust = src.index("ExhaustSelection.Open(this);")
    assert gated < exhaust, "the appended discard must resolve first"
    # The FACE reads in the order it plays, or a positioned upgrade lies about
    # itself in exactly the way the position exists to prevent.
    # `EB-571`: the separator rides inside the shown branch when the clause
    # is not last, so the base face has no double space where it vanishes.
    text_add = src.index("{IfUpgraded:show:Discard 1 card. |}")
    text_exhaust = src.index("[gold]Exhaust[/gold] 1 card from your hand.")
    assert text_add < text_exhaust


def test_codegen_still_refuses_an_add_before_it_cannot_place(monkeypatch):
    """The three ways a position is not honourable, each a NAMED block rather
    than a silent append -- the same three tier0's applier makes."""
    card = _add_before_probe()

    # (a) a position with nothing to place.
    monkeypatch.setattr(gen, "_upgrade_deltas", {
        "add_before_probe": {"add_before": "exhaust_from"}})
    assert "position modifier" in gen.upgrade_plan(card)[1]

    # (b) an op this card does not print, which is how an edit to the base body
    # surfaces instead of sliding the insertion somewhere else.
    monkeypatch.setattr(gen, "_upgrade_deltas", {
        "add_before_probe": {"add": {"op": "gain_encore", "amount": 1},
                             "add_before": "place_bomb"}})
    assert "does not print at top level" in gen.upgrade_plan(card)[1]

    # (c) a repeat, which re-runs the whole body and has no position in it.
    # The probe's ops are all repeat-safe, so the ONLY thing that can refuse
    # this row is the position guard -- an `exhaust_from` here would be caught
    # a line earlier for a different (also correct) reason and prove nothing.
    repeatable = dict(card, effects=[{"op": "draw", "amount": 1},
                                     {"op": "block", "amount": 5}])
    monkeypatch.setattr(gen, "_upgrade_deltas", {
        "add_before_probe": {"add": {"op": "repeat_this", "times": 1},
                             "add_before": "block"}})
    assert "no position within it" in gen.upgrade_plan(repeatable)[1]


# --- EB-140: the two branch-moving upgrade keys ------------------------------
#
# W3 (R211) ratified `{conditional_block: +3}` on `hold_the_line` and
# `{conditional_damage: +4}` on `take_it_from_the_top`, and the emitter could
# say neither, so both cards shipped an empty `OnUpgrade` -- a campfire choice
# in the sim and none in the live game. These pins are on the SHIPPED .cs
# rather than on a re-emission, because only one of the two is what the game
# loads (see `_generated_source`). The C# twin -- the same two cards upgraded
# through the game's own `CardModel.UpgradeInternal` -- is
# `klee-mod/KleeTests/ConditionalUpgradePinTests.cs`.


def _klee_generated_source(class_name: str) -> str:
    path = gen.KLEE_PROFILE.out_dir / f"{class_name}.cs"
    assert path.exists(), (
        f"{class_name} is not generated -- regenerate with "
        "`python tools/gen_roster_cards.py`")
    return path.read_text(encoding="utf-8")


# --- `EB-729`: a whole-card delta holes EVERY branch, not the then-arm alone --
#
# THE DEFECT, found on `EB-723` and worked around there by authoring the base
# number's hole on the row. `conditional_damage` / `conditional_block` bump
# every matching clause (tier0 `upgrades.apply` walks `everywhere`), so a
# conditional carrying a number in EACH arm has two numbers to hole. On a row
# that states its own `description:`, `_authored_face_with_tokens` walks the
# printed numbers with a cursor that only moves forward, and the arms used to
# be yielded then-first -- so a face written "Deal 7 damage. If ...: deal 13
# instead." spent the cursor on the 13 and left the 7 bare. The card then dealt
# 10 and printed 7, which is the `EB-288` / `EB-291` defect class: a printed
# number that is not the number the card does.
#
# These are re-emissions on a synthetic row rather than reads off a shipped
# `.cs`, because no row on any sheet carries this shape today -- the two live
# both-arm rows print their pair through the `PlainDamage` / `BranchDamage`
# fold instead. Regenerating after the fix moved no committed file, and that is
# the acceptance: the emitter can now say it, and nothing shipped had to move.


def _both_arm_probe(op: str, printed: int, branch: int, text: str) -> dict:
    """A row whose conditional prints a number in BOTH arms and states its own
    face, with the ELSE number written first -- the order the fix reads."""
    return {"id": "eb729_both_arm_probe", "name": "Both Arm Probe",
            "cost": 1, "type": "attack" if op == "damage" else "skill",
            "rarity": "common", "description": text,
            "effects": [{"op": "conditional", "if": "enemy_intends_attack",
                         "then": [dict({"op": op, "amount": branch},
                                       **({"target": "enemy"}
                                          if op == "damage" else {}))],
                         "else": [dict({"op": op, "amount": printed},
                                       **({"target": "enemy"}
                                          if op == "damage" else {}))]}]}


def test_a_whole_card_conditional_delta_holes_both_printed_numbers(
        monkeypatch):
    """THE LOCK, both keys. Seen to FAIL before the fix: the `then` number was
    holed and the base literal was printed bare."""
    for key, op, printed, branch, delta, text in (
            ("conditional_damage", "damage", 7, 13, 3,
             "Deal 7 damage. If an enemy intends to attack: deal 13 instead."),
            ("conditional_block", "block", 5, 10, 3,
             "Gain 5 [gold]Block[/gold]. If an enemy intends to attack: "
             "gain 10 instead.")):
        card = _both_arm_probe(op, printed, branch, text)
        monkeypatch.setattr(gen, "_upgrade_deltas",
                            {"eb729_both_arm_probe": {key: delta}})
        face = gen.build_description(card)

        assert "{IfUpgraded:show:%d|%d}" % (printed + delta, printed) in face, \
            f"{key}: the BASE literal is still bare -- {face}"
        assert "{IfUpgraded:show:%d|%d}" % (branch + delta, branch) in face, \
            f"{key}: the branch literal is not holed -- {face}"
        # No bare copy of either number survives beside its hole.
        assert re.search(rf"(?<![\d:|]){printed}(?![\d}}])", face) is None, face
        assert re.search(rf"(?<![\d:|]){branch}(?![\d}}])", face) is None, face


def test_the_then_arm_is_still_first_when_the_face_prints_it_first(
        monkeypatch):
    """The order is READ, not flipped. A face that prints the then number first
    -- the rendered path's own order -- still holes both, so the fix cannot
    have traded one direction of the defect for the other."""
    card = _both_arm_probe(
        "damage", 7, 13,
        "If an enemy intends to attack: deal 13 damage. Otherwise: deal 7.")
    monkeypatch.setattr(gen, "_upgrade_deltas",
                        {"eb729_both_arm_probe": {"conditional_damage": 3}})
    face = gen.build_description(card)

    assert "{IfUpgraded:show:16|13}" in face, face
    assert "{IfUpgraded:show:10|7}" in face, face
    assert face.index("16|13") < face.index("10|7"), face


def test_the_rendered_path_holed_both_arms_all_along(monkeypatch):
    """The other half of the acceptance, and the reason the defect was only
    ever an AUTHORED-face one: a row with no `description:` renders its own
    text, in then/else order, and has holed both arms since `EB-140`."""
    card = _both_arm_probe(
        "damage", 7, 13,
        "")                       # no authored face
    card.pop("description")
    monkeypatch.setattr(gen, "_upgrade_deltas",
                        {"eb729_both_arm_probe": {"conditional_damage": 3}})
    face = gen.build_description(card)

    assert "{IfUpgraded:show:16|13}" in face, face
    assert "{IfUpgraded:show:10|7}" in face, face


def test_a_conditional_delta_with_no_op_to_bump_is_still_refused(monkeypatch):
    """The keys are expressible, not unconditional. A row that rules one with
    nothing to land on is a sheet/card mismatch and says so."""
    card = _ethereal_probe()
    monkeypatch.setattr(gen, "_upgrade_deltas",
                        {"eb118_codegen_probe": {"conditional_damage": 4}})
    reason = gen.upgrade_plan(card)[1]
    assert "conditional_damage" in reason and "non-self `damage`" in reason


def test_a_second_top_level_target_keeps_a_conditional_delta_structural(
        monkeypatch):
    """One op, one var. Two top-level blocks would need two Block vars, so the
    delta is reported structural rather than half-applied (R24)."""
    card = dict(_ethereal_probe(),
                effects=[{"op": "block", "amount": 4},
                         {"op": "block", "amount": 3}])
    monkeypatch.setattr(gen, "_upgrade_deltas",
                        {"eb118_codegen_probe": {"conditional_block": 3}})
    reason = gen.upgrade_plan(card)[1]
    assert "2 top-level" in reason and "structural upgrade" in reason


# --- `condition:`, the bar-moving spelling (2026-09-06) ---------------------
#
# `condition:` used to accept `unconditional` and nothing else: the upgrade
# DELETES the gate and the branch is hoisted out. On a 0-cost threshold reader
# that is the strongest card in its pool and the one card in it with no
# relationship to the meter its arm is about, which is what the 2026-09-06
# balance review read off `proto_fr_florid_cadenza`. The second spelling names
# the UPGRADED BAR, and the gate stays: `bank >= (IsUpgraded ? up : base)` in
# the body, `{IfUpgraded:show:up|base}` on the face, and tier0's applier
# rewriting the same conditional's `if:` (`content/upgrades.py`). Both bars are
# authored; nothing here computes a threshold.


def _bar_probe(**kw) -> dict:
    """A Furina threshold reader: draw 1, and 2 more at 6 Fanfare."""
    return dict(_ethereal_probe(character="furina"),
                effects=[{"op": "draw", "amount": 1},
                         {"op": "conditional", "if": "fanfare_at_least_6",
                          "then": [{"op": "draw", "amount": 2}]}],
                **kw)


def test_a_moved_bar_emits_one_comparison_and_prints_both_numbers(monkeypatch):
    """ONE COMPARISON AND NOT TWO, which is the difference the player sees:
    the `+` card still asks the question. `unconditional`'s emission is the
    other shape on purpose (`IsUpgraded || pred`), because that upgrade takes
    the question away."""
    monkeypatch.setattr(
        gen, "_upgrade_deltas",
        {"eb118_codegen_probe": {"condition": "fanfare_at_least_3"}})
    card = _bar_probe()
    assert gen.upgrade_plan(card)[1] is None
    source = gen.emit(card, gen.FURINA_PROFILE)

    assert ("if (FurinaResources.ReadableFanfare(Owner.Creature) "
            ">= (IsUpgraded ? 3 : 6))") in source
    assert ("If you have at least {IfUpgraded:show:3|6} [gold]Fanfare[/gold]"
            in source)
    assert "IsUpgraded ||" not in source


def test_the_unconditional_spelling_is_untouched_by_the_second_one(monkeypatch):
    """The byte-identical claim for every card already ruled `unconditional`:
    the gate goes away, the branch is hoisted, and the face swaps whole."""
    monkeypatch.setattr(gen, "_upgrade_deltas",
                        {"eb118_codegen_probe": {"condition": "unconditional"}})
    source = gen.emit(_bar_probe(), gen.FURINA_PROFILE)

    assert ("if (IsUpgraded || FurinaResources.ReadableFanfare(Owner.Creature) "
            ">= 6)") in source
    assert "IsUpgraded ? 3" not in source


def test_an_upgraded_bar_on_another_meter_is_refused(monkeypatch):
    """An upgrade MOVES a bar; it does not change the question. Charge is
    Kokomi's bank, and a Fanfare reader whose `+` card asked it would be a
    different card wearing the same face."""
    monkeypatch.setattr(
        gen, "_upgrade_deltas",
        {"eb118_codegen_probe": {"condition": "charge_at_least_3"}})
    reason = gen.upgrade_plan(_bar_probe())[1]
    assert "different meter" in reason


def test_a_moved_bar_on_a_card_that_prints_none_is_refused(monkeypatch):
    """Sheet/card mismatch, reported as one rather than silently dropped --
    the same rule every other delta key here keeps."""
    monkeypatch.setattr(
        gen, "_upgrade_deltas",
        {"eb118_codegen_probe": {"condition": "fanfare_at_least_3"}})
    reason = gen.upgrade_plan(_ethereal_probe(character="furina"))[1]
    assert "prints no top-level meter bar" in reason


def test_two_printed_bars_make_a_moved_bar_structural(monkeypatch):
    """One bar, one owner. tier0 rewrites the FIRST matching conditional and
    this emitter would rewrite every one, so a second printed bar is two
    engines upgrading different numbers -- refused, not half-applied."""
    card = _bar_probe()
    card["effects"] = card["effects"] + [
        {"op": "conditional", "if": "fanfare_at_least_10",
         "then": [{"op": "draw", "amount": 1}]}]
    monkeypatch.setattr(
        gen, "_upgrade_deltas",
        {"eb118_codegen_probe": {"condition": "fanfare_at_least_3"}})
    reason = gen.upgrade_plan(card)[1]
    assert "2 top-level meter bars" in reason


def test_a_condition_value_that_is_not_a_bar_is_still_refused(monkeypatch):
    """The grammar grew one shape, not a free-text field."""
    monkeypatch.setattr(
        gen, "_upgrade_deltas",
        {"eb118_codegen_probe": {"condition": "has_spark"}})
    reason = gen.upgrade_plan(_bar_probe())[1]
    assert "meter bar predicate" in reason


# --------------------------------------------------------------------------
# EB-230: a Bomb's face prints the Bomb's own amount
# --------------------------------------------------------------------------

# Vars whose rendered value is resolved against the PLAYER's live attack
# modifiers (Strength, Weak, and every ModifyDamage hook). `DamageVar`,
# `ExtraDamageVar` and `CalculatedDamageVar` are all of that family.
_LIVE_ATTACK_VARS = {"Damage", "ExtraDamage", "CalculatedDamage"}

# Every "N-damage Bomb" shape a face can carry. Group 1 is the number the
# face shows for one Bomb's payload.
_BOMB_FACE_SHAPES = (
    # "...[gold]Bomb[/gold] on EACH enemy dealing X damage"
    # "...[gold]Bombs[/gold], each dealing X damage"
    re.compile(r"\[gold\]Bombs?\[/gold\][^.|]*?dealing (\{\w+:diff\(\)\}|\d+)"),
    # chance_bomb_per_detonation: "place a new X-damage [gold]Bomb[/gold]"
    re.compile(r"(\{\w+:diff\(\)\}|\d+)-damage \[gold\]Bomb\[/gold\]"),
)

_DESCRIPTION_LINE = re.compile(r'\("description", "(.*)"\),')


def _bomb_card_sources() -> dict[str, str]:
    """Every C# card source that could carry a Bomb face -- generated,
    prototype-generated and hand-written alike. The defect shipped on a
    GENERATED face, but Pop and Jumpy Dumpty Mk.Omega are hand-written and
    print the same clause, so the lock sweeps them too."""
    out = {}
    dirs = _ALL_GENERATED_DIRS + [
        gen.REPO / "klee-mod" / "KleeCode" / "Cards",
        gen.REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated",
    ]
    for d in dirs:
        for path in sorted(d.glob("*.cs")):
            src = path.read_text(encoding="utf-8")
            if "[gold]Bomb" not in src:
                continue
            out[str(path.relative_to(gen.REPO))] = src
    return out


def test_every_place_bomb_face_prints_the_bombs_own_amount():
    """EB-230. `place_bomb` hands `BombPower.Place` / tier0's `_op_place_bomb`
    a LITERAL payload (the sheet's `bomb_damage`, or the var's BaseValue) --
    neither engine reads the player's attack modifiers at placement or at
    detonation (BombPower deals its charge `ValueProp.Unpowered`). A face
    token from the DamageVar family resolves against those modifiers anyway:
    `AllMyTreasures` printed "each dealing 4 damage" under a debuff
    (KLEESPARK-W3 turn-029) while the stack dealt 6.

    So a Bomb clause may print a literal, or a var that is a PLAIN
    `DynamicVar` -- never `Damage` / `ExtraDamage` / `CalculatedDamage`.
    """
    offenders = []
    for rel, src in _bomb_card_sources().items():
        for desc in _DESCRIPTION_LINE.findall(src):
            for shape in _BOMB_FACE_SHAPES:
                for shown in shape.findall(desc):
                    if not shown.startswith("{"):
                        continue
                    name = shown[1:shown.index(":")]
                    if name in _LIVE_ATTACK_VARS:
                        offenders.append(
                            f"{rel}: Bomb face prints {{{name}:diff()}}, "
                            "which resolves against live attack modifiers")
                    elif f'new DynamicVar("{name}", ' not in src:
                        offenders.append(
                            f"{rel}: Bomb face prints {{{name}:diff()}} with "
                            "no plain DynamicVar declaring it")
    assert not offenders, (
        "A Bomb's face must print the Bomb's own amount (EB-230):\n  "
        + "\n  ".join(offenders))


