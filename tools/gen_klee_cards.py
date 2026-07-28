#!/usr/bin/env python3
"""
Emit C# card classes from canonical character YAML design sheets.

The historical filename remains the Klee-compatible entry point. Character
profiles now own sheet, output, namespace, element cadence, and identity;
tools/gen_roster_cards.py runs every profile. Each sheet remains the single
source of truth through implementation, per spec C2. The emitter owns only
mechanics backed by verified C# APIs and refuses to guess at anything else.

WHAT IT DELIBERATELY WILL NOT DO
--------------------------------
Any effect, card-level cost, condition, or lifecycle rule without an implemented
runtime is NOT emitted. A generator that emits a plausible-looking wrong body
is worse than one that emits nothing: the C# would compile, ship, and silently
misplay. Blocked cards are listed in the character manifest with the exact
semantic reason.

Every emitted file carries a DO-NOT-EDIT header naming this script and the
sheet, so a hand edit is visibly wrong rather than quietly lost on regen.

Usage:  python tools/gen_klee_cards.py [--check] [--character klee|furina|all]
        python tools/gen_roster_cards.py [--check]
        --check exits nonzero if regenerating would change anything (CI guard).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

# Emitted-source newline. Kept as a name so generated C# templates never
# carry backslash escapes through this file's own string literals.
NEWLINE = chr(10)
NEWLINE_JOIN = NEWLINE

REPO = Path(__file__).resolve().parent.parent
SHEET = REPO / "docs" / "klee-cards.yaml"
# Mirrors tier0/content/upgrades.py UPGRADE_SHEETS, in the same order.
UPGRADE_SHEETS = (REPO / "docs" / "klee-upgrades.yaml",
                  REPO / "docs" / "furina-upgrades.yaml",
                  REPO / "docs" / "kokomi-upgrades.yaml")

# Companion sheets -> home nation. The nation is what the reward slot's
# SAME_NATION_REWARD_SHARE weighting keys on, and tier0's loader derives it
# from the sheet FILENAME (loader.py: `nation = sheet.split("-", 1)[0]`), so
# the mapping is stated once here rather than re-derived per card.
#
# Fontaine entered Klee's slot by user ruling (2026-07-21): "it's probably
# best to have some non-Mondstadt cards in the pool to make sure Klee doesn't
# inadvertently overperform with a 100% Mondstadt roster."
COMPANION_SHEETS = ((REPO / "docs" / "mondstadt-companions.yaml", "mondstadt"),
                    (REPO / "docs" / "fontaine-companions.yaml", "fontaine"),
                    (REPO / "docs" / "inazuma-companions.yaml", "inazuma"))
OUT_DIR = REPO / "klee-mod" / "KleeCode" / "Cards" / "Generated"
MANIFEST = REPO / "klee-mod" / "KleeCode" / "Cards" / "Generated" / "manifest.json"
FURINA_SHEET = REPO / "docs" / "furina-cards.yaml"
FURINA_OUT_DIR = (
    REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina" / "Generated"
)
FURINA_MANIFEST = FURINA_OUT_DIR / "manifest.json"
KOKOMI_SHEET = REPO / "docs" / "kokomi-cards.yaml"
KOKOMI_OUT_DIR = (
    REPO / "klee-mod" / "KleeCode" / "Cards" / "Kokomi" / "Generated"
)
KOKOMI_MANIFEST = KOKOMI_OUT_DIR / "manifest.json"


@dataclass(frozen=True)
class CharacterProfile:
    """Character-specific rules that the shared card emitter must not infer.

    The original generator predates the roster mod and baked Klee's sheet,
    namespace, Pyro cadence, and art helper directly into emitted classes.
    Keeping those choices in a profile makes adding a character an explicit
    data operation while leaving Klee's existing output stable.
    """

    character_id: str
    sheet: Path
    out_dir: Path
    manifest: Path
    namespace: str
    native_element: str
    cadence: str
    generator_script: str
    art_loader: str
    emit_character_identity: bool = False

    def damage_applies_element(self, card: dict) -> bool:
        """Whether this character card's damaging effects carry its element."""
        if self.cadence == "catalyst_attack":
            return card.get("type") == "attack"
        if self.cadence == "skill_grade":
            tags = set(card.get("tags", []))
            has_damage = any(
                effect.get("op") == "damage"
                and effect.get("target") != "self"
                for effect in card.get("effects", [])
            )
            return has_damage and (
                card.get("type") == "skill"
                or "skill_tag" in tags
                or "burst_tag" in tags
            )
        raise ValueError(
            f"{self.character_id}: unknown elemental cadence {self.cadence!r}"
        )


KLEE_PROFILE = CharacterProfile(
    character_id="klee",
    sheet=SHEET,
    out_dir=OUT_DIR,
    manifest=MANIFEST,
    namespace="KleeMod.Cards.Generated",
    native_element="pyro",
    cadence="catalyst_attack",
    generator_script="tools/gen_klee_cards.py",
    art_loader="KleeArt",
)

FURINA_PROFILE = CharacterProfile(
    character_id="furina",
    sheet=FURINA_SHEET,
    out_dir=FURINA_OUT_DIR,
    manifest=FURINA_MANIFEST,
    namespace="KleeMod.Cards.Furina.Generated",
    native_element="hydro",
    cadence="skill_grade",
    generator_script="tools/gen_roster_cards.py",
    art_loader="RosterArt",
    emit_character_identity=True,
)

KOKOMI_PROFILE = CharacterProfile(
    character_id="kokomi",
    sheet=KOKOMI_SHEET,
    out_dir=KOKOMI_OUT_DIR,
    manifest=KOKOMI_MANIFEST,
    namespace="KleeMod.Cards.Kokomi.Generated",
    native_element="hydro",
    # CATALYST, ruled R52 ask N1: every attack of hers applies Hydro. That is
    # the structural third of her elite A6 -- application uptime comes from
    # the cadence, not from authored lines -- so it must be the profile's
    # business and not something each card re-declares.
    cadence="catalyst_attack",
    generator_script="tools/gen_roster_cards.py",
    art_loader="RosterArt",
    emit_character_identity=True,
)

PROFILES = {
    KLEE_PROFILE.character_id: KLEE_PROFILE,
    FURINA_PROFILE.character_id: FURINA_PROFILE,
    KOKOMI_PROFILE.character_id: KOKOMI_PROFILE,
}

# Ops this generator can express with verified Cmd APIs. Anything else blocks
# the card. Keep this set honest -- widening it without a verified call site is
# how we ship silently-wrong cards.
#
# gain_spark landed with the Sparks system (C3 gap-list unlock #1): the call
# site is SparkPower.Gain -> PowerCmd.Apply, the same verified idiom
# BombPower.Place uses. The amount is a LITERAL unless klee-upgrades.yaml
# carries a `spark: +N` delta for the card (M9 ruling 2026-07-20, moved off
# the inline `upgrade:` key by R20); then it
# becomes a named DynamicVar("Sparks", n). That name is not an invented
# placeholder (finding 15's lesson): the base class ctor is
# DynamicVar(string, decimal), DynamicVarSet has a public string indexer,
# and the base game itself ships name-only vars (DynamicVar("Times", ...)
# in CardModel's hover tips) -- all verified in the sts2 decompile.
#
# burst_energy landed with the Burst-energy spike (standing plan item 2): the
# call site is KleeBurstResource.Gain -> CustomResources<T> + PowerCmd, the
# same verified shape SparkPower.Gain uses. Amount is a LITERAL unless
# klee-upgrades.yaml carries a `burst_energy: +N` delta; then it becomes a
# named DynamicVar("BurstEnergy", n) -- the Sparks idiom exactly.
# discard + discard_for_sparks (R36 batch): random discard is
# CardCmd.Discard on a random pick from the kit-exempt pool; chosen discard
# is CardSelectCmd.FromHandForDiscard (the MockDiscardAndAddShivsPotion
# idiom -- forced pick of N, auto-selects-all on a short hand) with the
# SAME kit-exempt filter. KitGrant.NotKitCard is the exemption both ride
# (v1.9 invariant: the Burst is never fodder -- the obligation DECISIONS
# recorded when the kit sprint landed).
# Bomb-manipulation ops (standing-plan batch, 2026-07-20): detonate rides
# BombPower.DetonateOn/DetonateAll (returns the count -- Chained Reactions
# prices its re-bomb per detonation caused by the play, the sim's counter
# diff); modify_bombs rides BombPower.ModifyAll (round stamps mirror
# tier0's Bomb.turn_placed); move_bombs rides BombPower.MoveAllTo (charges
# keep their stamps, +bonus each). chance_bomb_per_detonation rolls
# Rng.CombatTargets.NextFloat() < chance (verified decompile; CombatTargets
# is the established in-combat pick stream).
MECHANICAL_OPS = {"damage", "block", "draw", "place_bomb", "gain_spark", "burst_energy",
                  "gain_encore", "spend_encore", "raise_fanfare_cap",
                  "gain_fanfare_floor",
                  "generate_guest_star",
                  "copy_spotlighted_in_hand",
                  "heal",
                  "apply_power", "discard", "discard_for_sparks",
                  "detonate", "move_bombs", "modify_bombs",
                  "chance_bomb_per_detonation", "conditional",
                  "energy", "scry_discard", "add_card", "exhaust_from",
                  "apply_aura", "swirl", "buff_next_attack", "block_next_turn",
                  "cost_mod", "copy_companion_in_hand",
                  # Curtain Call consolidation ("Take a Bow"): grow_damage is
                  # Rampage's permanent per-instance growth (BaseValue raised
                  # on the card's own var, the SyncDisplay idiom);
                  # refresh_all_auras reuses AuraPower's same-element refresh
                  # so the duration it refreshes TO has one definition.
                  "grow_damage", "refresh_all_auras",
                  # Kokomi (playtest sprint, Track B). gain_charge rides
                  # KokomiResources.GainCharge; summon_kurage rides
                  # KurageSummon.Field (refresh-never-stack); conscript rides
                  # KokomiConscript.Run. All three have verified call sites in
                  # klee-mod/KleeCode/Powers -- the whitelist stays honest.
                  "gain_charge", "summon_kurage", "conscript",
                  "replay_next_companion", "copy_companions_played_this_combat"}

# --- companion batch (2026-07-21) --------------------------------------------
def is_companion(card: dict) -> bool:
    """Companion sheet rows carry `star` (4/5); Klee's sheet never does."""
    return "star" in card


ELEMENT_CS = {"pyro": "Element.Pyro", "hydro": "Element.Hydro",
              "electro": "Element.Electro", "cryo": "Element.Cryo",
              "anemo": "Element.Anemo", "geo": "Element.Geo"}

APPLY_AURA_FIELDS = {"op", "element", "target"}
SWIRL_FIELDS = {"op", "target"}
BUFF_NEXT_FIELDS = {"op", "amount"}

# Charlotte, Enduring Frosthelm (tier0 _op_block_next_turn).
BLOCK_NEXT_TURN_FIELDS = {"op", "amount"}

# --- small ops (2026-07-20 batch) --------------------------------------------
# add_card token registry: sheet card id -> hand-written C# class. A pool
# reference resolves against the SHEET at generation time instead (the
# archetype/rarity data lives only there), and every resolved member must
# itself be a generated class -- both enforced in blocked_reason.
ADD_CARD_CLASSES = {"confiscated": "Confiscated"}
ADD_CARD_FIELDS = {
    # Kokomi/Silent Sly: extra effects that fire when the card is DISCARDED.
    "sly","op", "card", "card_id", "pool", "zone", "to", "amount",
                   "cost_override"}
GUEST_STAR_FIELDS = {"op", "rarity", "amount", "to", "cost_override"}
ENERGY_FIELDS = {"op", "amount"}
SCRY_FIELDS = {"op", "amount"}
# exhaust_from: dodge_roll's shape only -- a random Status from hand. The
# filterless form (kit-exempt any-card) blocks until a card needs it.
EXHAUST_FROM_FIELDS = {"op", "zone", "filter", "amount",
                       # Kokomi (playtest sprint): `select: chosen` is the
                       # PLAYER picking the victims, not the rng. Her whole
                       # engine is "choose what to rotate out", so a random
                       # pick would not be a smaller version of the card --
                       # it would be a different card.
                       "select"}

# --- conditional op (2026-07-20 batch) ---------------------------------------
# Predicates with a verified C# read, each mirroring tier0 effects.py
# _predicate exactly:
#   this_cost_zero  -> EnergyCost.GetResolved(): "current cost including all
#                      modifiers clamped to 0" (decompile doc) -- the spark
#                      zeroing rides Hook.ModifyEnergyCostInCombat, so a
#                      spark-freed attack reads 0 here, same as the sim's
#                      current_card_cost.
#   has_spark       -> SparkPower.Amount is the bank.
#   reaction_triggered_by_this / killed_target -> snapshot diffs captured at
#                      the top of OnPlay (the sim resets its per-card
#                      counters at resolve_card start).
PREDICATES_CS = {
    "this_cost_zero": "EnergyCost.GetResolved() == 0",
    # SparksAsResolved, NOT the raw Amount: the sim spends the spark charge
    # BEFORE effects resolve; the C# consume executes after (Snap fix), so
    # mid-play reads subtract the pending spend.
    "has_spark": "SparkPower.SparksAsResolved(Owner.Creature) > 0",
    "reaction_triggered_by_this": "ReactionEffects.TotalResolved > reactionsAtStart",
    # tier0: state.reactions_this_turn > 0, a window opened at the top of the
    # player turn BEFORE start-of-turn detonation. ReactionEffects keeps the
    # window as a snapshot of the same monotonic counter.
    "reaction_triggered_this_turn": "ReactionEffects.ReactionTriggeredThisTurn",
    "killed_target": "enemiesAtStart.Any(e => e.IsDead)",
    # fanfare_at_least_N is PARAMETRIC (see predicate_cs / predicate_text):
    # the bar is authored per card and moves at red-pen, so a literal map
    # turned every new threshold into a codegen KeyError.
    "has_salon_members": "SalonMemberPower.Count(Owner.Creature) > 0",
    "spotlight_moved_this_turn":
        "SpotlightSystem.MovedThisTurn(Owner.Creature)",
    # Curtain Call ("Take a Bow"). Both read through CurtainCallHooks rather
    # than inline, so the mirror of each sim predicate lives next to its
    # tracker and the divergence risk is one file, not every card that reads
    # it. enemy_intends_attack drops the sim's `sleep_turns == 0` clause on
    # purpose: nothing in the game SETS sleep, and a sleeping enemy
    # telegraphs SleepIntent rather than AttackIntent, so it fails the intent
    # test on its own (the helper checks IsStunned too).
    "enemy_intends_attack":
        "CurtainCallHooks.EnemyIntendsAttack(Owner.Creature)",
    "hp_lost_this_turn":
        "CurtainCallHooks.HpLostThisTurn(Owner.Creature)",
}

# The if-clause each predicate renders on the card.
PREDICATE_TEXT = {
    "this_cost_zero": "If this cost 0",
    "has_spark": "If you have [gold]Spark[/gold]",
    "reaction_triggered_by_this": "If it triggered an [gold]Elemental Reaction[/gold]",
    "reaction_triggered_this_turn": "If an [gold]Elemental Reaction[/gold] triggered this turn",
    "killed_target": "If it kills",
    "has_salon_members": "If you have a [gold]Salon Member[/gold]",
    "spotlight_moved_this_turn":
        "If you moved the [gold]Spotlight[/gold] this turn",
    "enemy_intends_attack": "If an enemy intends to attack",
    "hp_lost_this_turn": "If you have lost HP this turn",
}

_FANFARE_BAR = re.compile(r"^fanfare_at_least_(\d+)$")
# Same parametric treatment, same reason (see predicate_cs): these bars are
# balance numbers authored per card, so they must be a card edit and never a
# codegen table edit. Kokomi's two banks are the exhaust pile (a count the
# engine already keeps) and Charge.
_CHARGE_BAR = re.compile(r"^charge_at_least_(\d+)$")
_EXHAUST_PILE_BAR = re.compile(r"^exhaust_pile_at_least_(\d+)$")
# Curtain Call: Encore is a HELD buffer, so a threshold on it is the same
# shape as Fanfare's and gets the same parametric treatment for the same
# reason -- moving the bar must be a card edit, never a codegen edit.
_ENCORE_BAR = re.compile(r"^encore_at_least_(\d+)$")


def predicate_cs(name: str) -> str | None:
    """C# expression for a sheet predicate, or None if unsupported.

    `fanfare_at_least_N` is generated rather than tabled: the bar is a
    balance number authored per card and moved at red-pen, so tabling it
    made every new threshold a codegen KeyError instead of a card edit.
    """
    name = name or ""
    hit = _FANFARE_BAR.match(name)
    if hit:
        return f"FurinaResources.Fanfare(Owner.Creature) >= {hit.group(1)}"
    hit = _CHARGE_BAR.match(name)
    if hit:
        return f"KokomiResources.GetCharge(Owner.Creature) >= {hit.group(1)}"
    hit = _EXHAUST_PILE_BAR.match(name)
    if hit:
        return (f"KokomiResources.ExhaustPileCount(Owner.Creature) "
                f">= {hit.group(1)}")
    hit = _ENCORE_BAR.match(name)
    if hit:
        return f"FurinaResources.Encore(Owner.Creature) >= {hit.group(1)}"
    return PREDICATES_CS.get(name)


def predicate_text(name: str) -> str | None:
    """The if-clause the predicate renders on the card face."""
    name = name or ""
    hit = _FANFARE_BAR.match(name)
    if hit:
        return f"If you have at least {hit.group(1)} [gold]Fanfare[/gold]"
    hit = _CHARGE_BAR.match(name)
    if hit:
        return f"If you have at least {hit.group(1)} [gold]Charge[/gold]"
    hit = _EXHAUST_PILE_BAR.match(name)
    if hit:
        return (f"If {hit.group(1)} or more cards are "
                "[gold]Exhausted[/gold]")
    hit = _ENCORE_BAR.match(name)
    if hit:
        return f"If you have at least {hit.group(1)} Encore"
    return PREDICATE_TEXT.get(name)


CONDITIONAL_FIELDS = {"op", "if", "then", "else"}

# Ops legal inside a conditional branch: plain resolvers with literal (or
# delta-var) amounts and no local declarations outside their own braces.
# repeat_this is legal ONLY as a conditional's entire then-branch.
BRANCH_OPS = {"damage", "block", "draw", "gain_spark", "gain_encore",
              "place_bomb", "burst_energy", "energy",
              "buff_next_attack"}

# Cards carrying a repeat-conditional re-resolve their other effects (sim
# resolve_card: the repeat excludes only the repeat machinery). The repeated
# body lands inside a for-block, so those other effects must not declare
# method-scope locals a second time -- restrict them to declaration-free ops.
REPEAT_SAFE_OPS = {"damage", "block", "draw", "gain_spark", "burst_energy"}

# Field whitelists for the bomb ops (UNPARSEABLE discipline: an unknown
# field encodes a mechanic; block loudly, never approximate).
DETONATE_FIELDS = {"op", "target", "bonus"}
MOVE_BOMBS_FIELDS = {"op", "target", "bonus"}
MODIFY_BOMBS_FIELDS = {"op", "scope", "bonus"}
CHANCE_BOMB_FIELDS = {"op", "chance", "bomb_damage"}

# apply_power (power-card pass): sheet power id -> (C# PowerModel class,
# stack cap or None, card-text template with {X} for the amount). Stackable
# powers normally use None, matching native Slay the Spire power stacking;
# a numeric cap is reserved for an explicitly designed exception and is
# cross-checked against the sheet below.
#
# sparks_n_splash is deliberately ABSENT: the Burst kit card lands LAST in
# the power-card pass (standing plan) with its own cost/grant machinery.
APPLY_POWERS = {
    "bomb_damage_up": ("BombDamageUpPower", None,
        "Your [gold]Bombs[/gold] detonate for {X} more damage."),
    "zero_cost_attacks_up": ("ZeroCostAttacksUpPower", None,
        "Your Attacks that cost 0 deal {X} more damage."),
    "spark_per_turn": ("SparkPerTurnPower", None,
        "At the start of your turn, gain {X} [gold]Spark[/gold]."),
    "reaction_bonus_spark_energy": ("ReactionBonusSparkEnergyPower", None,
        "[gold]Elemental Reactions[/gold] grant {X} extra [gold]Spark[/gold] "
        "and 5 extra [gold]Burst Energy[/gold]."),
    "detonation_splash": ("DetonationSplashPower", None,
        "When a [gold]Bomb[/gold] detonates: deal {X} damage to ALL enemies, "
        "ignoring Block, and gain 3 [gold]Burst Energy[/gold]. "
        "Up to 3 times per turn."),
    "detonation_vuln": ("DetonationVulnPower", None,
        "When a [gold]Bomb[/gold] detonates, apply {X} [gold]Vulnerable[/gold] "
        "to that enemy."),
    "spark_threshold_down": ("SparkThresholdDownPower", None,
        "You need {X} fewer [gold]Spark[/gold] for your Attacks to cost 0."),
    "amp_reaction_up": ("AmpReactionUpPower", None,
        "[gold]Vaporize[/gold] and [gold]Melt[/gold] amplify {X}% more."),
    "bomb_and_spark_per_turn": ("BombAndSparkPerTurnPower", None,
        "At the start of your turn, place a 5-damage [gold]Bomb[/gold] on a "
        "random enemy and gain {X} [gold]Spark[/gold]."),
    # Native debuffs (weak/vulnerable batch, 2026-07-20). Semantics verified
    # against the decompiled core: WeakPower x0.75 dealt / VulnerablePower
    # x1.5 taken, Counter stacks, tick at enemy side turn end -- exactly
    # tier0's WEAK_DEALT_MULT / VULNERABLE_TAKEN_MULT and DECAYING rule.
    # No cap either side. {TO} renders the target clause (build_description).
    # Kokomi (playtest sprint, Track B). kurage_ward is ours
    # (Powers/KuragePowers.cs); the other two are the BASE GAME's own
    # Ironclad powers, reused rather than reimplemented -- her sheet asked
    # for exactly their semantics and a private copy would be a second
    # implementation of a rule the engine already owns.
    "metallicize": ("MetallicizePower", None,
        "At the start of your turn, gain {X} Block."),
    # Cap 6 mirrors the sheet's `max_stacks: 6` -- a single-application ward,
    # not a stacking one. Vigil's upgrade moves amount AND cap together
    # (test_vigil_upgrade_moves_the_cap_with_the_amount pins that), so the
    # registry cap has to move with them or the upgrade is silently swallowed.
    "prevent_exhaust_ward": ("PreventExhaustWardPower", 6,
        "The first time you would take unblocked attack damage each turn, "
        "prevent up to {X} of it and [gold]Exhaust[/gold] a random card from "
        "your draw pile."),
    "kurage_ward": ("KurageWardPower", None,
        "Each [gold]Bake-Kurage[/gold] pulse also grants {X} Block."),
    # R73/G2. No cap: the stacking is the ruling, not an oversight, and a cap
    # here would implement the ban [USER] considered and rejected.
    "kurage_amp": ("KurageAmpPower", None,
        "Each [gold]Bake-Kurage[/gold] pulse reads your [gold]Charge[/gold] "
        "for {X} more damage per point."),
    "feel_no_pain": ("FeelNoPainPower", None,
        "Whenever a card is [gold]Exhausted[/gold], gain {X} Block."),
    "dark_embrace": ("DarkEmbracePower", None,
        "Whenever a card is [gold]Exhausted[/gold], draw {X} card(s)."),
    "weak": ("WeakPower", None,
        "Apply {X} [gold]Weak[/gold]{TO}."),
    "vulnerable": ("VulnerablePower", None,
        "Apply {X} [gold]Vulnerable[/gold]{TO}."),
    # Companion powers (2026-07-21, CompanionPowers.cs): each mirrors a
    # tier0 player_turn_start/end trigger or attack-bonus branch. No caps
    # (the sim clamps none of these).
    "oz_summon": ("OzSummonPower", None,
        "Summon Oz for {X} turns: at the end of your turn, he deals 3 damage "
        "and applies [gold]Electro[/gold] to a random enemy."),
    "witchs_flame": ("WitchsFlamePower", None,
        "At the end of your turn, consume [gold]Pyro[/gold] from each enemy. "
        "For each aura consumed, deal {X} damage and gain 3 "
        "[gold]Burst Energy[/gold]."),
    # Redesigned 2026-07-26 (red-pen item 4): a per-turn Strength ratchet plus
    # the same per-turn Block, replacing a static flat attack bonus.
    "celestial_gift": ("CelestialGiftPower", None,
        "At the start of your turn, gain {X} [gold]Strength[/gold] and 4 "
        "[gold]Block[/gold]."),
    "solar_isotoma": ("SolarIsotomaPower", None,
        "For {X} turns: your Attacks against enemies holding an elemental "
        "aura grant 3 [gold]Block[/gold] per hit."),
    "attack_up_this_turn": ("AttackUpThisTurnPower", None,
        "Your Attacks deal {X} more damage this turn."),
    "strength": ("StrengthPower", None,
        "Gain {X} [gold]Strength[/gold]."),
    # Fontaine (2026-07-21 ruling). shatter_bonus is a flat rider the sim adds
    # inside the Shatter's raw HP subtraction, so FrozenPower reads it there.
    "shatter_bonus": ("ShatterBonusPower", None,
        "Your [gold]Shatters[/gold] deal {X} more damage."),
    # Fontaine 5-star Rares (R64, 2026-07-25). Amounts live on the cards, so
    # none of these adds a constant for the parity lint to drift on.
    "cannon_fire_support": ("CannonFireSupportPower", None,
        "Whenever you play a [gold]Companion[/gold] card, gain {X} "
        "[gold]Block[/gold]."),
    "night_vigil": ("NightVigilPower", None,
        "Your Attacks against enemies holding an elemental aura deal {X} "
        "more damage."),
    "ancient_sea_authority": ("AncientSeaAuthorityPower", None,
        "Elemental auras you apply last {X} extra turn(s)."),
    "masque_red_death": ("MasqueRedDeathPower", None,
        "At the start of each turn, gain {X} [gold]Strength[/gold]. Each turn "
        "your [gold]Bond of Life[/gold] consumes the first 5 "
        "[gold]Block[/gold] you gain."),
    "fanfare_attack_per10": ("FanfareAttackPer10Power", None,
        "Your Attacks deal {X} more damage per 10 [gold]Fanfare[/gold]."),
    "salon_member": ("SalonMemberPower", None,
        "Add {X} typed [gold]Salon Member(s)[/gold]. Maximum 3; a full "
        "stage bows its OLDEST member out (its unique payoff) and "
        "empowers this card's later effects."),
    "salon_damage_up": ("SalonDamageUpPower", None,
        "[gold]Salon Member[/gold] numbers are {X} higher."),
    # ALL max_stacks DROPPED across Furina's sheet (user ruling 2026-07-24).
    # Two rounds: the first dropped the four non-compounding powers; this one
    # drops the rest, matching base StS where Power dupes always stack. An A/B
    # (2000 runs/arm x2 seeds, assigned pilots) put the whole cap set at 0.0pp
    # for the first four and +0.4-0.5pp (p~0.02, favorable) for the compounders,
    # i.e. non-binding at present difficulty. Two of these -- spotlight_mult_bonus
    # and ovation_spend_boost -- ARE genuinely compounding (per-copy % multipliers
    # that pass1-rulings-round2's exponent argument was about); they read minimal
    # ONLY because spotlight/fanfare win <1% pre-calibration. FLAGGED to re-check
    # at difficulty calibration. `salon_member`'s "Maximum 3" is NOT a max_stacks
    # cap -- it is the roster size (a full stage bows the oldest out), core salon
    # rules, and stays. NO numeric cap remains in this registry now.
    "spotlight_discount": ("SpotlightDiscountPower", None,
        "The first [gold]Spotlighted[/gold] card each turn costs {X} less."),
    "spotlight_draw": ("SpotlightDrawPower", None,
        "The first [gold]Spotlighted[/gold] card each turn draws {X} card."),
    "spotlight_mult_bonus": ("SpotlightMultBonusPower", None,
        "[gold]Spotlighted[/gold] Companion numbers are {X}% stronger "
        "this combat."),
    "spotlight_mult_bonus_turn": ("SpotlightMultBonusTurnPower", None,
        "[gold]Spotlighted[/gold] Companion numbers are {X}% stronger "
        "this turn."),
    "spotlight_flat_damage": ("SpotlightFlatDamagePower", None,
        "[gold]Spotlighted[/gold] Companion damage gains {X}."),
    "spotlight_flat_damage_turn": ("SpotlightFlatDamageTurnPower", None,
        "[gold]Spotlighted[/gold] Companion damage gains {X} this turn."),
    "ovation_spend_boost": ("OvationSpendBoostPower", None,
        "Whenever you spend Encore, [gold]Spotlighted[/gold] Companion "
        "numbers are {X}% stronger this turn."),
    "spotlight_encore_first": ("SpotlightEncoreFirstPower", None,
        "The first [gold]Spotlighted[/gold] card each turn grants {X} Encore."),
    # Curtain Call's activity-triggered set (R85), ported by the "Take a Bow"
    # consolidation sprint. Every one of them pays on an EVENT the player
    # caused rather than on a turn tick -- see Powers/CurtainCallPowers.cs for
    # the trigger sites and their tier0 mirrors. No caps: the activity gate IS
    # the rate limit, so a stack ceiling would be a second, redundant one.
    "salon_deploy_block": ("SalonDeployBlockPower", None,
        "Whenever you deploy a [gold]Salon Member[/gold], gain {X} Block."),
    "salon_bow_block": ("SalonBowBlockPower", None,
        "Whenever a [gold]Salon Member[/gold] takes its final bow, gain "
        "{X} Block."),
    "salon_bow_encore": ("SalonBowEncorePower", None,
        "Whenever a [gold]Salon Member[/gold] takes its final bow, gain "
        "{X} Encore."),
    "cross_examination": ("CrossExaminationPower", None,
        "The first [gold]Elemental Reaction[/gold] you trigger each turn "
        "applies {X} [gold]Vulnerable[/gold] and {X} [gold]Weak[/gold] to "
        "its target."),
    "encore_spend_draw": ("EncoreSpendDrawPower", None,
        "The first time you spend Encore each turn, draw {X} card."),
    "first_attack_draw": ("FirstAttackDrawPower", None,
        "The first Attack you play each turn draws {X} card."),
}

# Powers applied to ENEMIES (native debuffs). Everything else in APPLY_POWERS
# is a self power; blocked_reason enforces the split both ways.
ENEMY_APPLY_POWERS = {"weak", "vulnerable"}

# Sheet fields apply_power may carry. Anything else encodes a mechanic this
# generator does not understand -- fail loudly (UNPARSEABLE discipline).
APPLY_POWER_FIELDS = {"op", "power", "amount", "target", "max_stacks", "note",
                      "splash_procs_per_turn",
                      # Salon v2: the typed-member rider on salon_member
                      # deploys (rework plan §1).
                      "member",
                      # Companion sheet annotations (oz/albedo): the summon's
                      # element and aura consumption live in the POWER's C#
                      # implementation; the fields are documentation.
                      "summon_element", "consumes_aura"}

# The C# each `member:` value emits. `random` is a NULL, which
# SalonMemberPower.Deploy resolves per iteration off the shared combat RNG
# stream (A11). Keyed rather than inlined so an unrecognised member is a
# named blocker instead of a KeyError mid-emit.
SALON_MEMBER_CS = {
    "crabaletta": "SalonMember.Crabaletta",
    "usher": "SalonMember.Usher",
    "chevalmarin": "SalonMember.Chevalmarin",
    "random": "null",
}

# Upgrade keys that all mean "bump the applied power amount" at card level
# (tier0 upgrades.py handles them in one branch too).
# All of these bump the amount of the card's FIRST apply_power/buff_next_attack
# effect -- tier0 upgrades.py handles them in one branch, and `duration` (Oz,
# Solar Isotoma) and `buff` (both Bennetts) join it because the "amount" of
# those powers IS the duration / the attack bonus.
POWER_UPGRADE_KEYS = {"power_amount", "amp_percent", "splash_damage", "vulnerable",
                      "weak", "duration", "buff"}

# Ops the POWER_UPGRADE_KEYS deltas may land on, in the sim's own precedence:
# `next(fx for fx in top if fx["op"] in (...))` -- the FIRST top-level one
# only, which is why Chevreuse's conditional rider stays at its printed value
# while her base buff scales.
POWER_UPGRADE_OPS = ("apply_power", "buff_next_attack")

# Bomb placement targets we have a verified selection idiom for.
BOMB_TARGETS = {"enemy", "random_enemy", "random_enemies"}

# Damage targets we have a confirmed builder for (see AttackCommand).
DAMAGE_TARGETS = {"enemy", "all_enemies", "random_enemy", "random_enemies", "self"}

# Cards already hand-written; never overwrite them.
#
# jumpy_dumpty came off this list once place_bomb landed: its whole sheet entry
# (damage x2 at random enemies + a bomb) is now expressible, and its C1 stub was
# actively wrong -- it dropped the bomb half and retargeted to a chosen enemy.
# Kaboom and DuckAndCover stay hand-written as the reference examples the rest
# of the codebase's comments point at; Pop stays because it is the verified
# bomb card the playtest signed off on.
HAND_WRITTEN = {"kaboom", "duck_and_cover", "pop"}

# R23 aura-application batch (2026-07-20): hand-written because their ops read
# aura/bomb state (conditional-vs-aura, bonus_vs_aura, bonus_vs_bombed,
# refresh_all_auras) -- per-target bonuses live in ModifyDamageAdditive, which
# codegen does not emit.
HAND_WRITTEN |= {"sizzle", "flame_dance", "kaboom_beetle_swarm", "elemental_ecstasy"}

# Kit-grant sprint (2026-07-20): the Burst card is hand-written because its
# lifecycle is machinery, not ops -- granted by KitGrant at a full meter,
# BaseLib custom-resource cost (SetCanonicalCost 60 / full-meter Spend),
# Retain keyword, never pool-registered. See Powers/KitBurst.cs.
HAND_WRITTEN |= {"sparks_n_splash"}

# Non-Klee hand-written cards. A SEPARATE set from HAND_WRITTEN above, which
# is Klee-scoped both by its guard and by lint_handwritten_parity.py, whose
# parity rules only know Klee's ops and whose file lookup only knows Cards/.
#
# The point of listing them at all is truthfulness in the generator's report.
# Without this, `ceremonial_garment` came back as "kit card (hand-write it
# against the KitBurst machinery)" -- an instruction that had already been
# carried out, which reads to the next person as outstanding work. A blocked
# reason should say why the generator declined, not hand out a stale TODO.
HAND_WRITTEN_ROSTER = {"let_the_people_rejoice", "ceremonial_garment"}

# R24 (2026-07-20): codegen upgrade defaults are ABOLISHED, not demoted.
# docs/klee-upgrades.yaml is the single source of truth for upgrade deltas.
# A generated card whose sheet entry is missing, or whose ruled delta this
# generator cannot express, ships with NO upgrade path and a loud manifest
# flag (the tier0 UNAPPLIABLE discipline, applied to C#) -- silent defaults
# are how cant_catch_me shipped +3 block against a ruled +2.
#
# Delta keys this generator can express on a card's effects:
#   damage      -> the card's non-self damage effect (DynamicVars.Damage)
#   block       -> block effect (DynamicVars.Block)
#   draw        -> draw effect (DynamicVars.Cards)
#   spark       -> gain_spark effect (DynamicVars["Sparks"], M9 ruling)
#   bomb_damage -> place_bomb effect (Damage or ExtraDamage, see bomb_var)
#   cost        -> EnergyCost.UpgradeBy(n) -- the idiom CardModel.OnUpgrade's
#                  own doc comment prescribes (verified in the decompile)
# Structural upgrades stay blocked unless an exact play-time mirror exists.
# `add: {op: draw, amount: N}` is the current exception: codegen appends an
# IsUpgraded-gated draw after the base effects, matching upgrades.py.
#   discard     -> discard_for_sparks count (DynamicVars["Discards"], R36)
#   sparks      -> discard_for_sparks Spark cap (DynamicVars["Sparks"], R36;
#                  distinct from `spark` = gain_spark on purpose)
#   innate      -> AddKeyword(CardKeyword.Innate) in OnUpgrade (R37; keywords
#                  are instance-owned LocalKeywords, and the base game's own
#                  Innate drives opening-hand placement + keyword text)
#   bonus       -> the detonate/move_bombs/modify_bombs bonus field
#                  (DynamicVars["Bonus"]; single bonus-carrying effect per
#                  card, guarded)
#   chance      -> chance_bomb_per_detonation REPLACEMENT (tier0 upgrades.py
#                  replaces, not bumps); codegen renders percent and emits
#                  the delta in points, computed from the sheet's base
#   conditional_bonus -> bumps the then-branch's first damage (tier0
#                  upgrades.py bumps first damage|block in then; codegen
#                  expresses the damage form via the ExtraDamage var and
#                  flags a then-block card as structural)
#   condition   -> "unconditional" only: tier0 hoists the then-branch out of
#                  the conditional; C# reads (IsUpgraded || pred) at play and
#                  swaps the text via {IfUpgraded:show:...|...} (the runtime
#                  form BaseLib's SimpleLoc generates for upgrade swaps)
#   bombs       -> X-cost bomb count: X_plus_N -> X_plus_(N+val) in tier0;
#                  codegen renders "X+{Bombs:diff()}" off a Bombs var
EXPRESSIBLE_DELTAS = ({"damage", "block", "draw", "spark", "encore",
                       "encore_cost", "fanfare_cost", "fanfare_cap",
                       "fanfare_floor", "heal",
                       "bomb_damage", "burst_energy", "cost",
                       "discard", "sparks", "innate", "retain", "bonus", "chance",
                       "conditional_bonus", "condition", "bombs",
                       "bonus_per_detonation", "cards", "remove",
                       "copy_cost_override", "add"}
                      | {"generate_cost_override"}
                      # Kokomi (playtest sprint, Track B). Three deltas her
                      # sheet already rules but codegen could not express, so
                      # three of her cards -- one of them a STARTER -- were
                      # shipping with no campfire upgrade at all (G-C1 lint).
                      | {"kurage_turns", "energy", "block_next_turn",
                         # `exhaust: +N` moves how many cards an exhaust_from
                         # takes. The VAR emitter ("Exhausts") already existed;
                         # the key was simply never declared expressible, so
                         # the first card to use it reported "structural
                         # upgrade" and shipped with no campfire path at all.
                         "exhaust",
                         # `formula_per: +N` bumps the PER term of an
                         # amount_formula, which is the ExtraDamage var in the
                         # CalculatedDamageVar triple -- the same slot the
                         # conditional_bonus delta moves.
                         "formula_per",
                         # `times: +N` moves a multi-hit attack's HIT COUNT
                         # (A5, 2026-07-28: Undercurrent 3 -> 5 hits). tier0
                         # has bumped `times` since Klee, but codegen baked
                         # the count in as a literal `.WithHitCount(3)`, so
                         # the key was unexpressible and the first card to
                         # rule it would have shipped with NO campfire path.
                         # Binds to the same effect tier0 does: the first
                         # damage op carrying a literal int `times`.
                         "times",
                         # `formula_base: +N` bumps the BASE term (the
                         # CalculationBase var). Added by F4 because only the
                         # per-term existed, and on an UNCAPPED count the two
                         # are different rulings: per is a slope on something
                         # that only grows, base pays once and stops.
                         "formula_base"}
                      | POWER_UPGRADE_KEYS)

# Ops whose `bonus` field the "bonus" upgrade delta may target.
BONUS_OPS = ("detonate", "move_bombs", "modify_bombs")

RARITY_CS = {
    "basic": "CardRarity.Basic",
    "common": "CardRarity.Common",
    "uncommon": "CardRarity.Uncommon",
    "rare": "CardRarity.Rare",
}

TYPE_CS = {"attack": "CardType.Attack", "skill": "CardType.Skill", "power": "CardType.Power"}

TARGET_CS = {
    "enemy": "TargetType.AnyEnemy",
    "all_enemies": "TargetType.AllEnemies",
    "random_enemy": "TargetType.AllEnemies",
    "random_enemies": "TargetType.AllEnemies",
    "self": "TargetType.Self",
}

# A card-level field can alter playability or lifecycle without appearing in
# effects. Treating unknown fields as harmless metadata is therefore unsafe:
# that is how an Encore/Fanfare cost could otherwise disappear while the body
# still compiles. Descriptive/draft metadata is allowlisted beside every
# currently implemented lifecycle field.
CARD_FIELDS = {
    # Kokomi/Silent Sly: extra effects that fire when the card is DISCARDED.
    "sly",
    "id", "name", "cost", "type", "rarity", "solve", "archetypes", "role",
    "effects", "tags", "exhaust", "kit_card", "requires",
    # A9 (2026-07-28): Innate on the BASE card, not only as an upgrade delta.
    # tier0 needed nothing -- Card.innate already existed and combat's
    # surface_innate reads it on any card -- but the generator emitted the
    # keyword only from OnUpgrade, so the field was unknown here and the
    # first card to rule it was BLOCKED. That block is the design working:
    # hearts_swelling reported "card field(s) ['innate'] not understood"
    # rather than shipping a card that starts in hand in the sim and does
    # not in the game.
    "innate",
    # Companion identity/reward metadata.
    "star", "element", "role_c", "personal_pool", "nation", "character",
    "guest_star",
    # Furina resource gates. BaseLib provides affordability and post-effect
    # Fanfare spend; FurinaResourceHooks moves Encore spend pre-effect.
    "encore_cost", "fanfare_cost",
    # Curtain Call (R85): the register a card's NAME speaks in. Purely
    # descriptive naming metadata (salon | archon | private on Furina's
    # sheet) -- nothing mechanical to emit, so it is whitelisted as inert
    # rather than treated as an unexpressed mechanic.
    "register",
    # Internal, never authored on a sheet: _sly_view stamps it so the text
    # and body emitters know they are rendering the discard branch. Listed
    # here because that view is now run through blocked_reason like any
    # other card, and the field whitelist is deliberately total.
    "_sly_branch",
}


def card_level_reason(
    card: dict, profile: CharacterProfile = KLEE_PROFILE
) -> str | None:
    """Return a blocker for card-level semantics the emitter cannot honor."""
    unknown = set(card) - CARD_FIELDS
    if unknown:
        return f"card field(s) {sorted(unknown)} not understood"
    return None


def pascal(card_id: str) -> str:
    """kaboom -> Kaboom, sorry_jean -> SorryJean, jumpy_dumpty_mk2 -> JumpyDumptyMk2."""
    return "".join(p.capitalize() for p in re.split(r"[_\-]", card_id) if p)


_sheet_cards_cache: list | None = None


def _sheet_cards() -> list[dict]:
    global _sheet_cards_cache
    if _sheet_cards_cache is None:
        _sheet_cards_cache = yaml.safe_load(SHEET.read_text(encoding="utf-8"))
    return _sheet_cards_cache


def _pool_members(pool: str) -> list[dict]:
    """tier0 loader.cards_in_pool, resolved against the sheet at generation
    time (archetype/rarity live only there): '<archetype>_<rarity>s'."""
    archetype, _, rarity = pool.rpartition("_")
    rarity = rarity.rstrip("s")
    return sorted((c for c in _sheet_cards()
                   if c.get("rarity") == rarity
                   and archetype in c.get("archetypes", [])
                   and not c.get("kit_card")),
                  key=lambda c: c["id"])


def _x_formula_reason(card: dict, val) -> str | None:
    """tier0 _amount grammar: 'X' or 'X_plus_N', legal only on an X-cost
    card (state.current_x is the energy spent). None = expressible."""
    if str(card.get("cost")) != "X":
        return f"amount formula '{val}' on a non-X-cost card"
    if val == "X" or (isinstance(val, str) and val.startswith("X_plus_")
                      and val[len("X_plus_"):].isdigit()):
        return None
    return f"amount formula '{val}'"


# Runtime counts legal as a `times:` hit count. Curtain Call's Matinee
# Performance is the one user: a per-member hit whose count is the live cast
# size. Read at resolution off the power stack the deploy site mirrors, which
# is the same read tier0's _runtime_count does -- and the same precedent
# Mirage's enemy_poison_total set for counting over power stacks.
#
# Deliberately a SMALL allowlist, not "any count token". A times value the
# generator cannot express must stay a named blocker: guessing it produces a
# card that compiles and quietly hits once forever while the face promises
# scaling, which is the worst failure this generator has.
RUNTIME_TIMES = {
    "salon_members": "SalonMemberPower.Count(Owner.Creature)",
}

# The clause each runtime count renders on the face. Separate from the C#
# expression because the player reads the CAST, not the power stack that
# happens to mirror it.
RUNTIME_TIMES_TEXT = {
    "salon_members": " once per [gold]Salon Member[/gold]",
}


def _x_expr(val, bombs_var: bool = False) -> str:
    """C# expression for a tier0 amount formula ('x' is ResolveEnergyXValue,
    declared at the top of OnPlay)."""
    if val == "X":
        return "x"
    n = int(val[len("X_plus_"):])
    if bombs_var:
        return 'x + DynamicVars["Bombs"].IntValue'
    return f"x + {n}"


def blocked_reason(
    card: dict, profile: CharacterProfile = KLEE_PROFILE
) -> str | None:
    """Return why this card cannot be generated, or None if it can."""
    card_reason = card_level_reason(card, profile)
    if card_reason:
        return card_reason

    # The Sly branch is CARD BEHAVIOUR and gets the same scrutiny as the
    # played face. It did not, and the result was tidal_lure: its sheet says
    # Vulnerable 1 to a RANDOM enemy, the apply_power emitter treats
    # anything-but-"enemy" as all-enemies, and the guard that would have
    # caught that only ever looked at `effects`. The card generated, compiled,
    # and debuffed the whole room. An unchecked branch is not a smaller
    # surface; it is the same surface with the alarm disconnected.
    if card.get("sly"):
        sly_reason = blocked_reason(_sly_view(card), profile)
        if sly_reason:
            return f"sly branch: {sly_reason}"

    if profile is KLEE_PROFILE and card["id"] in HAND_WRITTEN:
        return "hand-written"

    if card["id"] in HAND_WRITTEN_ROSTER:
        return "hand-written"

    if is_companion(card):
        # Companions apply their element via the card-level IElementalCard,
        # so mixed elemental/non-elemental damage on one card cannot be
        # expressed (tier0 reads applies_element per effect).
        applies = {bool(e.get("applies_element"))
                   for e in card.get("effects", [])
                   if e.get("op") == "damage" and e.get("target") != "self"}
        if len(applies) > 1:
            return "mixed applies_element damage on one companion card"

    # X cost (R34 batch): HasEnergyCostX => true + ResolveEnergyXValue()
    # (CapturedXValue through Hook.ModifyXValue -- the game-canonical X
    # read). The spark-spend exemption for X attacks is already in
    # SparkPower.AppliesTo (!CostsX), the sim's R34 rule.

    # Kit cards: granted-not-drafted, requires-full gate, meter spend. The
    # machinery landed 2026-07-20 (Powers/KitBurst.cs) with sparks_n_splash
    # hand-written; a FUTURE kit card hitting this guard needs the same
    # decision (hand-write it or teach codegen the kit lifecycle) -- loud
    # either way, never generated as ordinary loot.
    if card.get("kit_card") or card.get("requires"):
        return "kit card (hand-write it against the KitBurst machinery)"

    # `amount_formula` (Kokomi's exhaust-pile scalers, playtest sprint Track B).
    # A computed amount that reads a PILE SIZE at resolve time. The generator
    # has no grammar for it, and the failure mode of guessing is the worst
    # kind: a card that emits, compiles, and quietly deals its `base` forever
    # while the face promises scaling. Block loudly instead -- UNPARSEABLE
    # discipline. Teaching this needs a CalculatedVar bound to the exhaust
    # pile, which is Track C work, not a codegen shortcut.
    for effect in card.get("effects", []):
        if "amount_formula" in effect and exhaust_pile_calc_rider(
                card, effect) is None:
            formula = effect["amount_formula"]
            return (f"amount_formula (reads {formula.get('count')}) -- needs a "
                    "CalculatedVar bound to that count, not a literal")

    # R20: inline upgrade fields are deprecated repo-wide -- deltas live in
    # *-upgrades.yaml sheets. Block loudly so a stray inline key can never
    # silently diverge from the upgrades sheet.
    if "upgrade" in card:
        return "inline `upgrade:` field (deprecated by R20 -- put the delta in klee-upgrades.yaml)"

    # "Sparks" is one DynamicVar name: a card carrying BOTH gain_spark and
    # discard_for_sparks would collide on it. No such card exists; block
    # loudly if one appears rather than silently overwrite.
    ops_present = {e.get("op") for e in card.get("effects", [])}
    if {"gain_spark", "discard_for_sparks"} <= ops_present:
        return "gain_spark + discard_for_sparks on one card (Sparks var collision)"

    for eff in card.get("effects", []):
        op = eff.get("op")
        if op not in MECHANICAL_OPS:
            return f"op '{op}'"
        # B1 CLASS FIX (2026-07-28). A `bonus_formula` on a NON-damage op is a
        # blocker unless a rider actually expresses it.
        #
        # Damage is exempt because damage riders always resolve: an
        # unconverted one still rides the PrintedDamage path at resolution
        # (it merely fails to show on the face, which is what the Legibility
        # sprint converted). Every OTHER op had no such path -- the formula
        # was read by nothing, so the card silently shipped its bare base.
        # Thunderous Ovation lost `1_per_2_fanfare` that way for two
        # playtests. Blocking is the honest failure: an UNAPPLIABLE card is
        # visible in the manifest, a quietly-wrong one is not.
        if op != "damage" and eff.get("bonus_formula") is not None \
                and block_calc_rider(card, eff) is None:
            return (f"bonus_formula '{eff['bonus_formula']}' on op '{op}' is "
                    "expressed by no rider (it would render as the bare base)")
        if op == "damage":
            tgt = eff.get("target")
            if tgt not in DAMAGE_TARGETS:
                return f"damage target '{tgt}'"
            if eff.get("times_formula", "2_plus_sparks") != "2_plus_sparks":
                # The sim's only times formula (effects.py raises on others).
                return f"times_formula '{eff['times_formula']}'"
            bf = eff.get("bonus_formula")
            if bf is not None and not (
                    bf.endswith("_per_detonation_this_combat")
                    and bf.partition("_per_")[0].isdigit()) and not re.fullmatch(
                        r"\d+_per_\d+_fanfare", bf) and not re.fullmatch(
                        # Kokomi's Charge reader. Same CalculatedDamageVar path
                        # as Fanfare's -- see charge_calc_rider for why an
                        # honest printed number matters more here than there.
                        r"\d+_per_\d+_charge", bf) and not re.fullmatch(
                        # Curtain Call: Body Slam's grammar -- an attack priced
                        # off the held Encore buffer. READ only, never spent.
                        r"\d+_per_\d+_encore", bf) and not re.fullmatch(
                        # A14: the per-member slope. No divisor -- the salon is
                        # a capped count, so every member is a full step.
                        r"\d+_per_salon_member", bf):
                return f"bonus_formula '{bf}'"
            if "bonus_vs_bombed" in eff:
                return "conditional damage bonus (needs bomb system)"
            if "bonus_vs_aura" in eff:
                if eff.get("target") not in {"enemy", "all_enemies"} \
                        or not isinstance(eff["bonus_vs_aura"], int):
                    return (
                        "bonus_vs_aura requires enemy damage and "
                        "a literal int")
            times = eff.get("times", 1)
            if (not isinstance(times, int) and times not in RUNTIME_TIMES
                    and _x_formula_reason(card, times)):
                return _x_formula_reason(card, times)
        if op == "place_bomb":
            if eff.get("target") not in BOMB_TARGETS:
                return f"bomb target '{eff.get('target')}'"
            amt = eff.get("amount")
            if not isinstance(amt, int) and _x_formula_reason(card, amt):
                return _x_formula_reason(card, amt)
        if op in {"gain_encore", "spend_encore", "raise_fanfare_cap",
                  "gain_fanfare_floor"}:
            unknown = set(eff) - {"op", "amount"}
            if unknown:
                return f"{op} field(s) {sorted(unknown)} not understood"
            if not isinstance(eff.get("amount"), int) or eff["amount"] <= 0:
                return f"{op} amount must be a positive literal int"
        if op == "heal":
            unknown = set(eff) - {"op", "amount"}
            if unknown:
                return f"heal field(s) {sorted(unknown)} not understood"
            if not isinstance(eff.get("amount"), int) or eff["amount"] <= 0:
                return "heal amount must be a positive literal int"
            if card.get("rarity") != "rare" or not card.get("exhaust"):
                return "heal requires a Rare card with Exhaust"
        if op == "detonate":
            if eff.get("target") not in {"enemy", "all_enemies"}:
                return f"detonate target '{eff.get('target')}'"
            unknown = set(eff) - DETONATE_FIELDS
            if unknown:
                return f"detonate field(s) {sorted(unknown)} not understood"
        if op == "move_bombs":
            if eff.get("target") != "enemy":
                return f"move_bombs target '{eff.get('target')}' (only a chosen enemy has a selection idiom)"
            unknown = set(eff) - MOVE_BOMBS_FIELDS
            if unknown:
                return f"move_bombs field(s) {sorted(unknown)} not understood"
        if op == "modify_bombs":
            if eff.get("scope", "all") not in {"all", "placed_this_turn"}:
                return f"modify_bombs scope '{eff.get('scope')}'"
            unknown = set(eff) - MODIFY_BOMBS_FIELDS
            if unknown:
                return f"modify_bombs field(s) {sorted(unknown)} not understood"
        if op == "chance_bomb_per_detonation":
            unknown = set(eff) - CHANCE_BOMB_FIELDS
            if unknown:
                return f"chance_bomb_per_detonation field(s) {sorted(unknown)} not understood"
            # The count source is the detonate call earlier in THIS card's
            # effect list (tier0 diffs its counter around the card play; the
            # generated body reads the DetonateOn/DetonateAll return).
            idx = card["effects"].index(eff)
            if not any(e.get("op") == "detonate" for e in card["effects"][:idx]):
                return "chance_bomb_per_detonation without a preceding detonate (no count source)"
        if op == "apply_power":
            power = eff.get("power")
            # A7 (2026-07-28) DEFERRED C# PORT, recorded by name so the
            # manifest entry reads as a decision rather than an oversight --
            # the Curtain Call 12-card deferral pattern (R85/R86).
            #
            # The sheet and tier0 both implement it. The C# port is blocked on
            # a real structural gap, not on effort: the trigger has to fire
            # from FurinaResources' three Fanfare mutators, and those are
            # SYNCHRONOUS (`static void GainFanfare`, `static int
            # DecayFanfare`), while every block grant in this mod goes through
            # `await CreatureCmd.GainBlock`. The two ways out are both worse
            # than waiting:
            #   * thread async through GainFanfare/GainEncore/SpendEncore --
            #     a co-op-critical refactor touching every generated Encore
            #     card, far outside this ruling's blast radius;
            #   * call Creature.GainBlockInternal synchronously -- no
            #     precedent anywhere in the mod, and no decompile evidence for
            #     whether it runs the hooks/VFX the command layer runs.
            # Inventing an unverified idiom on a resource path is exactly what
            # produced the 2026-07-27 Vigil desync, so it waits for a pass
            # that can do the async surface properly.
            if power == "fanfare_delta_block":
                return ("apply_power power 'fanfare_delta_block' -- A7 C# "
                        "port DEFERRED: the Fanfare mutators are sync and "
                        "every block grant here is async (see comment)")
            if power not in APPLY_POWERS:
                return f"apply_power power '{power}' (no PowerModel in the registry)"
            if power in ENEMY_APPLY_POWERS:
                # Native debuffs aim at enemies (tier0 _op_apply_power ->
                # _pick_targets). random targeting has no verified idiom yet.
                if eff.get("target") not in (
                        "enemy", "all_enemies", "random_enemy"):
                    return (f"apply_power target '{eff.get('target')}' "
                            f"for enemy debuff '{power}'")
            elif eff.get("target") != "self":
                return f"apply_power target '{eff.get('target')}' (self power aimed at enemies)"
            unknown = set(eff) - APPLY_POWER_FIELDS
            if unknown:
                # UNPARSEABLE discipline: an unrecognized field encodes a
                # mechanic; block loudly, never approximate.
                return f"apply_power field(s) {sorted(unknown)} not understood"
            # A11: the member value is emitted through a lookup, and a lookup
            # miss mid-emit is a KeyError -- a stack trace, not a decision.
            # Refuse the card by name instead, the way every other
            # unexpressible value on this sheet is refused.
            if "member" in eff and eff["member"] not in SALON_MEMBER_CS:
                return (f"salon member '{eff['member']}' is not one of "
                        f"{sorted(SALON_MEMBER_CS)}")
            cap = APPLY_POWERS[power][1]
            if eff.get("max_stacks") != cap and not (eff.get("max_stacks") is None and cap is None):
                # Cap drift between the sheet and the C# power class const.
                raise SystemExit(
                    f"gen_klee_cards: {card['id']}: sheet max_stacks "
                    f"{eff.get('max_stacks')!r} != registered cap {cap!r} for "
                    f"power '{power}' -- update BOTH the C# power and the registry.")
            if power == "detonation_splash" and eff.get("splash_procs_per_turn") != 3:
                raise SystemExit(
                    f"gen_klee_cards: {card['id']}: splash_procs_per_turn "
                    f"{eff.get('splash_procs_per_turn')!r} != 3; the C# cap is the "
                    f"DemolitionConstants.SplashProcCapPerTurn const -- change both.")
        if op == "cost_mod":
            unknown = set(eff) - {"op", "scope", "delta", "duration"}
            if unknown:
                return f"cost_mod field(s) {sorted(unknown)} not understood"
            if eff.get("scope") != "companion_cards":
                return f"cost_mod scope '{eff.get('scope')}'"
            if eff.get("duration") != "this_turn":
                return f"cost_mod duration '{eff.get('duration')}'"
            if not isinstance(eff.get("delta"), int) or eff["delta"] >= 0:
                return "cost_mod delta must be a negative literal int"
        if op == "copy_companion_in_hand":
            # `temp` accepted and IGNORED: tier0 _op_copy_companion_in_hand
            # never reads it (the copy persists) -- the sim is LAW, so the
            # mirror ignores it too rather than inventing a mechanic.
            unknown = set(eff) - {"op", "amount", "temp", "cost_override"}
            if unknown:
                return f"copy_companion_in_hand field(s) {sorted(unknown)} not understood"
            if eff.get("amount", 1) != 1:
                return "copy_companion_in_hand amount > 1 (single-pick idiom only)"
            if "cost_override" in eff and not isinstance(eff["cost_override"], int):
                return "copy_companion_in_hand cost_override must be a literal int"
        if op == "copy_spotlighted_in_hand":
            unknown = set(eff) - {"op", "amount", "cost_override"}
            if unknown:
                return (
                    "copy_spotlighted_in_hand field(s) "
                    f"{sorted(unknown)} not understood")
            if eff.get("amount", 1) != 1:
                return (
                    "copy_spotlighted_in_hand amount > 1 "
                    "(single-pick idiom only)")
            if "cost_override" in eff and not isinstance(
                    eff["cost_override"], int):
                return (
                    "copy_spotlighted_in_hand cost_override must be "
                    "a literal int")
        if op == "replay_next_companion":
            unknown = set(eff) - {"op", "times", "duration"}
            if unknown:
                return f"replay_next_companion field(s) {sorted(unknown)} not understood"
            if eff.get("duration") != "this_turn":
                return f"replay_next_companion duration '{eff.get('duration')}'"
            if not isinstance(eff.get("times", 1), int):
                return "replay_next_companion times must be a literal int"
        if op == "copy_companions_played_this_combat":
            unknown = set(eff) - {"op", "zone", "cost_override"}
            if unknown:
                return f"copy_companions_played field(s) {sorted(unknown)} not understood"
            if eff.get("zone", "hand") != "hand":
                return f"copy_companions_played zone '{eff.get('zone')}'"
            if "cost_override" in eff and not isinstance(eff["cost_override"], int):
                return "copy_companions_played cost_override must be a literal int"
        if op == "apply_aura":
            unknown = set(eff) - APPLY_AURA_FIELDS
            if unknown:
                return f"apply_aura field(s) {sorted(unknown)} not understood"
            if eff.get("element") not in ELEMENT_CS:
                return f"apply_aura element '{eff.get('element')}'"
            if eff.get("target", "enemy") not in ("enemy", "random_enemy",
                                                  "all_enemies"):
                return f"apply_aura target '{eff.get('target')}'"
        if op == "swirl":
            unknown = set(eff) - SWIRL_FIELDS
            if unknown:
                return f"swirl field(s) {sorted(unknown)} not understood"
            if eff.get("target", "enemy") not in ("enemy", "random_enemy",
                                                  "all_enemies"):
                return f"swirl target '{eff.get('target')}'"
        if op == "block_next_turn":
            unknown = set(eff) - BLOCK_NEXT_TURN_FIELDS
            if unknown:
                return f"block_next_turn field(s) {sorted(unknown)} not understood"
            if not isinstance(eff.get("amount"), int):
                return "block_next_turn amount must be a literal int"
        if op == "buff_next_attack":
            unknown = set(eff) - BUFF_NEXT_FIELDS
            if unknown:
                return f"buff_next_attack field(s) {sorted(unknown)} not understood"
            if not isinstance(eff.get("amount"), int):
                return "buff_next_attack amount must be a literal int"
        if op == "energy":
            unknown = set(eff) - ENERGY_FIELDS
            if unknown:
                return f"energy field(s) {sorted(unknown)} not understood"
            if not isinstance(eff.get("amount"), int):
                return "energy amount must be a literal int"
        if op == "scry_discard":
            unknown = set(eff) - SCRY_FIELDS
            if unknown:
                return f"scry_discard field(s) {sorted(unknown)} not understood"
            if not isinstance(eff.get("amount"), int):
                return "scry_discard amount must be a literal int"
        if op == "exhaust_from":
            unknown = set(eff) - EXHAUST_FROM_FIELDS
            if unknown:
                return f"exhaust_from field(s) {sorted(unknown)} not understood"
            # Hand is the only zone either character exhausts from, and it
            # is the sim's default for an omitted `zone` (Kokomi's sheet
            # omits it on every row). Requiring the key explicitly blocked
            # six of her cards -- including a STARTER -- over a field that
            # has exactly one legal value.
            if eff.get("zone", "hand") != "hand":
                return f"exhaust_from zone '{eff.get('zone')}'"
            # An UNFILTERED exhaust_from is legal when the player picks the
            # victims: the sim's pool is "hand minus kit cards" and the
            # chosen branch emits exactly that filter. The any-card pool that
            # was never built is the RANDOM one -- rolling a victim out of the
            # whole hand -- and that is still blocked below.
            if eff.get("filter") != "status" and eff.get("select") != "chosen":
                return "exhaust_from without status filter (any-card pool not built)"
            if eff.get("filter") not in (None, "status"):
                return f"exhaust_from filter '{eff.get('filter')}'"
            # amount > 1 is expressible ONLY on the chosen branch, and the
            # distinction is not pedantry. The sim's RANDOM branch re-rolls
            # against a pool that shrinks after each victim; expressing that
            # faithfully needs a loop that re-reads the hand, which is the
            # thing that was never built. The CHOSEN branch has no such
            # problem: CardSelectCmd.FromHand takes a count and returns N
            # distinct cards in one prompt, which is exactly the sim's
            # "pick the worst, remove it from the pool, repeat" without the
            # loop. Blanket-blocking both cost cleansing_tide (a Common) and
            # moonlit_offering their upgrade paths for no reason.
            if eff.get("amount", 1) != 1 and eff.get("select") != "chosen":
                return "exhaust_from amount > 1 (random re-pool loop not built)"
        if op == "add_card":
            unknown = set(eff) - ADD_CARD_FIELDS
            if unknown:
                return f"add_card field(s) {sorted(unknown)} not understood"
            zone = eff.get("zone") or eff.get("to", "discard")
            if zone not in ("hand", "discard"):
                return f"add_card zone '{zone}'"
            if "pool" in eff:
                members = _pool_members(eff["pool"])
                if not members:
                    return f"add_card pool '{eff['pool']}' resolves empty"
                # Every member must itself generate: CreateCard needs a class.
                bad = [m["id"] for m in members
                       if m["id"] == card["id"] or blocked_reason(m)]
                if bad:
                    return (f"add_card pool '{eff['pool']}' contains "
                            f"ungenerated card(s) {bad}")
            else:
                cid = eff.get("card_id") or eff.get("card")
                if cid not in ADD_CARD_CLASSES:
                    return f"add_card card '{cid}' (no C# token class registered)"
        if op == "generate_guest_star":
            unknown = set(eff) - GUEST_STAR_FIELDS
            if unknown:
                return (
                    "generate_guest_star field(s) "
                    f"{sorted(unknown)} not understood")
            if eff.get("rarity") not in {"common", "uncommon"}:
                return (
                    "generate_guest_star rarity "
                    f"'{eff.get('rarity')}'")
            rarity_rank = {"common": 0, "uncommon": 1, "rare": 2}
            if rarity_rank[eff["rarity"]] > rarity_rank.get(
                    card.get("rarity"), -1):
                return (
                    "generate_guest_star cannot create above generator rarity")
            if not isinstance(eff.get("amount", 1), int) \
                    or eff.get("amount", 1) <= 0:
                return "generate_guest_star amount must be a positive literal int"
            if eff.get("to", "hand") != "hand":
                return (
                    "generate_guest_star destination "
                    f"'{eff.get('to')}'")
            if "cost_override" in eff and not isinstance(
                    eff["cost_override"], int):
                return "generate_guest_star cost_override must be a literal int"
            if not card.get("exhaust"):
                return "generate_guest_star generator must Exhaust"
        if op == "conditional":
            unknown = set(eff) - CONDITIONAL_FIELDS
            if unknown:
                return f"conditional field(s) {sorted(unknown)} not understood"
            if predicate_cs(eff.get("if")) is None:
                return f"conditional predicate '{eff.get('if')}' (no verified C# read)"
            then, els = eff.get("then", []), eff.get("else", [])
            if any(e.get("op") == "repeat_this" for e in then + els):
                # Sim law (resolve_card): repeat_requested re-resolves the
                # effect list minus the repeat machinery. Codegen expresses
                # exactly the sheet's shape: a then-branch that IS the repeat.
                if len(then) != 1 or els:
                    return "repeat_this must be the conditional's entire then-branch"
                if not isinstance(then[0].get("times", 1), int):
                    return "repeat_this times must be a literal int"
                bad = [e["op"] for e in card["effects"]
                       if e is not eff and e["op"] not in REPEAT_SAFE_OPS]
                if bad:
                    return (f"repeat-conditional beside op(s) {sorted(set(bad))} "
                            "(repeated body would redeclare locals)")
            else:
                branch_fields = {
                    "damage": {"op", "amount", "target"},
                    "block": {"op", "amount"},
                    "draw": {"op", "amount"},
                    "gain_spark": {"op", "amount"},
                    "gain_encore": {"op", "amount"},
                    "burst_energy": {"op", "amount"},
                    "energy": {"op", "amount"},
                    "place_bomb": {"op", "amount", "target", "bomb_damage"},
                    "buff_next_attack": {"op", "amount"},
                }
                for branch in (then, els):
                    for e in branch:
                        if e.get("op") not in BRANCH_OPS:
                            return f"op '{e.get('op')}' inside a conditional branch"
                        unknown = set(e) - branch_fields[e["op"]]
                        if unknown:
                            return (f"branch {e['op']} field(s) {sorted(unknown)} "
                                    "not understood")
                        if (e.get("op") == "damage"
                                and (e.get("target") not in DAMAGE_TARGETS
                                     or e.get("target") == "self")):
                            return f"branch damage target '{e.get('target')}'"
                        if (e.get("op") == "place_bomb"
                                and e.get("target") not in BOMB_TARGETS):
                            return f"branch place_bomb target '{e.get('target')}'"
                        if not isinstance(e.get("amount", e.get("bomb_damage")), int):
                            return f"branch {e['op']} amount must be a literal int"
    if sum(1 for e in card.get("effects", []) if e.get("op") == "detonate") > 1:
        return "two detonate effects on one card (count variable collision)"
    if sum(1 for e in card.get("effects", [])
           if e.get("op") == "conditional"
           and any(x.get("op") == "repeat_this" for x in e.get("then", []))) > 1:
        return "two repeat-conditionals on one card (repeatTimes collision)"
    return None


def bomb_var(card: dict) -> str:
    """
    Which DynamicVar carries bomb damage.

    A card that both attacks and places a bomb needs two distinct numbers, and
    both cannot be "Damage" -- DynamicVarSet is keyed by name, so the second
    would overwrite the first. ExtraDamage is a real base-game var with its own
    accessor, so the loc system resolves {ExtraDamage} without inventing a
    custom name whose placeholder support is unverified.

    Cards that only place bombs keep plain Damage, which matches the
    hand-written Pop and keeps their card text reading naturally.
    """
    has_attack = any(
        e["op"] == "damage" and e["target"] != "self" for e in card.get("effects", [])
    )
    return "ExtraDamage" if has_attack else "Damage"


def fanfare_calc_rider(card: dict, eff: dict) -> tuple[int, int, int] | None:
    """Furina Legibility sprint (2026-07-24): a plain Fanfare damage rider
    (`N_per_M_fanfare`) rendered through the base game's CalculatedDamageVar so
    the card face / hover preview and the resolved hit share ONE value path --
    base + N*(Fanfare/M) -- instead of the display showing only the static base
    while PrintedDamage silently adds the rider at resolution (the playtest bug).

    Returns (base, per_n, fanfare_div) or None. Scope guards, both card-level so
    build_vars and build_body agree and no deferred modifier is dropped:
      * a non-self damage effect carrying an N_per_M_fanfare formula;
      * NOT a salon-deploy card -- the salon x3 replacement multiplier is the
        deferred entangled modifier, so those stay on the PrintedDamage path.
    The Spotlight PrintedDamage wrap this bypasses is identity for Furina's own
    cards (Center Stage does not scale her own numbers), so no resolved number
    changes."""
    if eff.get("op") != "damage" or eff.get("target") == "self":
        return None
    m = re.fullmatch(r"(\d+)_per_(\d+)_fanfare", eff.get("bonus_formula", ""))
    if not m:
        return None
    if salon_deploy_card(card):
        return None
    return int(eff["amount"]), int(m.group(1)), int(m.group(2))


def exhaust_pile_calc_rider(card: dict, eff: dict) -> tuple[int, int, str] | None:
    """`amount_formula: {base, per, count: exhaust_pile}` -- her finishers that
    read everything she has rotated off the line so far.

    Same CalculatedDamageVar path as the Charge and Fanfare riders, for the
    same reason: the pile grows all combat, so a face printing only `base`
    would understate the card by more than it states by the time anyone casts
    it. Only the exhaust_pile count is expressible; any other count token
    stays a named blocker rather than a guess.
    """
    if eff.get("op") != "damage" or eff.get("target") == "self":
        return None
    formula = eff.get("amount_formula")
    if not isinstance(formula, dict) or formula.get("count") != "exhaust_pile":
        return None
    return (int(formula.get("base", 0)), int(formula.get("per", 1)),
            "static (card, _) => "
            "KokomiResources.ExhaustPileCount(card.Owner.Creature)")


def charge_calc_rider(card: dict, eff: dict) -> tuple[int, int, int] | None:
    """Kokomi's Charge damage rider (`N_per_M_charge`), rendered through the
    base game's CalculatedDamageVar for exactly the reason Furina's Fanfare
    rider is (Legibility sprint, 2026-07-24): the face, the hover preview and
    the resolved hit must share ONE value path.

    This matters more for Charge than it did for Fanfare. The bank is uncapped
    and never spent, so by act 3 the rider is routinely larger than the printed
    base -- a face showing only the base would be understating the card by more
    than it states. `all_streams_flow` is her signature reader; if any card in
    the game has to print an honest number, it is that one.

    Returns (base, per_n, charge_div) or None.
    """
    if eff.get("op") != "damage" or eff.get("target") == "self":
        return None
    m = re.fullmatch(r"(\d+)_per_(\d+)_charge", eff.get("bonus_formula", ""))
    if not m:
        return None
    return int(eff["amount"]), int(m.group(1)), int(m.group(2))


def encore_calc_rider(card: dict, eff: dict) -> tuple[int, int, int] | None:
    """Curtain Call's Encore damage rider (`N_per_M_encore`), rendered through
    the same CalculatedDamageVar path as the Fanfare and Charge riders.

    Same argument as those two, and it binds hardest here: Encore is a buffer
    the player deliberately banks, so at the moment anyone casts Poised
    Riposte the rider is exactly the part they were planning around. A face
    printing only the base would understate the card precisely when the play
    matters. The bank is READ, never spent -- consulting it costs nothing.

    Returns (base, per_n, encore_div) or None.
    """
    if eff.get("op") != "damage" or eff.get("target") == "self":
        return None
    m = re.fullmatch(r"(\d+)_per_(\d+)_encore", eff.get("bonus_formula", ""))
    if not m:
        return None
    return int(eff["amount"]), int(m.group(1)), int(m.group(2))


def salon_member_calc_rider(card: dict, eff: dict) -> tuple[int, int, int] | None:
    """A13/A14 (2026-07-28): a per-Salon-member slope (`N_per_salon_member`).

    Grammar note: no `_M_` divisor, unlike the Fanfare/Charge/Encore riders.
    Those divide because they read a large pool where 1:1 would pay absurdly;
    the salon is a capped count of 3 (4 with A12's cap-raise), so every member
    is a full step. `_bonus_formula` in tier0/engine/effects.py splits the same
    two grammars the same way.

    Rendered through the Calculated var path rather than PrintedDamage for the
    Legibility-sprint reason: the whole POINT of the A13/A14 rework is that the
    pilot can see the stage paying. A face that printed only the base would
    hide exactly the number the rework exists to show, and would read
    identically to the threshold version it replaces.

    Returns (base, per_n, 1) -- the trailing 1 keeps the shape of the other
    riders' (base, per, divisor) triple; the multiplier lambda is the raw
    member count.
    """
    if eff.get("op") != "damage" or eff.get("target") == "self":
        return None
    m = re.fullmatch(r"(\d+)_per_salon_member", eff.get("bonus_formula", ""))
    if not m:
        return None
    # A deploy card scaling off the stage it is currently setting would read
    # its own arrival, so those stay on the replacement-multiplier path.
    if salon_deploy_card(card):
        return None
    return int(eff["amount"]), int(m.group(1)), 1


SALON_MEMBER_COUNT_CS = "SalonMemberPower.Count(card.Owner.Creature)"


def salon_deploy_card(card: dict) -> bool:
    """Salon-deploy cards render their replacement multiplier through
    `salon_calc_rider` instead of the other riders' path (their scaled value
    depends on the company, not on Spotlight/Fanfare), so the Spotlight and
    Fanfare predicates hand them off here."""
    return any(
        e.get("op") == "apply_power" and e.get("power") == "salon_member"
        for e in card.get("effects", []))


# The var each scaled op renders through, and which replacement constant
# scales it. Damage and block bow x3, every other numeric x2 -- the split the
# inline `(salonReplacements > 0 ? 3 : 1)` / `? 2 : 1` expressions encoded.
SALON_SCALED_VARS = {
    "block": ("CalculatedBlock", "ReplacementDamageMultiplier"),
    "damage": ("CalculatedDamage", "ReplacementDamageMultiplier"),
    # NOT "Cards": DynamicVarSet.Cards is a TYPED accessor that casts to
    # CardsVar, so a CalculatedVar under that name would throw on any read
    # through the property. "Encore"/"PowerAmount" have no typed accessor.
    "draw": ("DrawCards", "ReplacementNumericMultiplier"),
    "gain_encore": ("Encore", "ReplacementNumericMultiplier"),
    "apply_power": ("PowerAmount", "ReplacementNumericMultiplier"),
}


def _salon_calc_target(card: dict) -> tuple[dict, int, str, str] | None:
    """The ONE effect on a salon-deploy card whose printed number the
    replacement rule scales and which can render through a CalculatedVar:
    (effect, deploys before it, var name, multiplier constant).

    Only one, because `CalculatedDamageVar`, `CalculatedBlockVar` and the
    plain `CalculatedVar` all take their base term from the single
    `CalculationBase` var -- a second converted number on the same card would
    compute itself off the first one's base. First eligible effect wins; any
    others keep the inline `salonReplacements` expression (and their face
    keeps under-reporting, which is logged, not silently fixed).

    The deploy count must be STATIC: `WillReplace` is a closed form over the
    pre-play company size plus the deploys this card runs first, so an
    upgradeable deploy amount (a "PowerAmount" var on the deploy itself)
    disqualifies the card rather than guessing.
    """
    if not salon_deploy_card(card):
        return None
    effects = card.get("effects", [])
    deploys = 0
    for eff in effects:
        op = eff.get("op")
        if op == "apply_power" and eff.get("power") == "salon_member":
            if eff is power_upgrade_effect(card):
                return None              # deploy count is not static
            amount = eff.get("amount", 1)
            if not isinstance(amount, int):
                return None
            deploys += amount
            continue
        if deploys == 0:
            continue                     # nothing has bowed yet: not scaled
        if op not in SALON_SCALED_VARS:
            continue
        if op == "damage":
            # self-damage is unscaled; a card carrying its own rider would
            # need a compound multiplier (none exist -- salon cards are
            # excluded from the Fanfare/aura/Spotlight riders).
            if eff.get("target") == "self":
                continue
            if "bonus_formula" in eff or "bonus_vs_aura" in eff:
                continue
        if op == "apply_power":
            # PowerAmount is ours to own only if no OTHER effect already
            # claims it for its upgrade delta (DynamicVarSet throws on a
            # duplicate name -- the 2026-07-23 reward-screen softlock).
            upgrade_owner = power_upgrade_effect(card)
            if upgrade_owner is not None and upgrade_owner is not eff:
                continue
        if op == "draw":
            # A branch draw or an upgrade-added draw emits its own CardsVar;
            # two "Cards" vars is the same duplicate-name softlock.
            if added_draw_upgrade(card) or branch_draw_upgrade(card):
                continue
        if op == "gain_encore":
            # The ruled encore delta lands on EVERY gain_encore site, so the
            # var may only own the amount when there is exactly one site.
            if len([e for e in _effects_everywhere(card)
                    if e.get("op") == "gain_encore"]) != 1:
                continue
            if added_encore_upgrade(card):
                continue
        # One effect per op, so the converted number is unambiguous. The
        # deploys themselves are apply_power too, and never compete for the
        # var, so they do not count against a scaled power.
        if len([e for e in effects if e.get("op") == op
                and not (op == "apply_power"
                         and e.get("power") == "salon_member")]) != 1:
            continue
        var, mult = SALON_SCALED_VARS[op]
        return eff, deploys, var, mult
    return None


def salon_calc_rider(card: dict, eff: dict) -> tuple[int, int, str, str] | None:
    """Furina Legibility sprint, Track L-A4 (salon half): the effect scaled by
    the Salon replacement rule, rendered through a CalculatedVar so the card
    face shows the bowed-in value instead of the unscaled print.
    Returns (printed base, deploys before it, var name, multiplier constant).

    The multiplier calls `SalonMemberPower.ReplacementDelta`, which asks
    `SalonMemberPower.StageIsFull` -- the same predicate `Deploy`'s loop uses.
    One expression of the replacement rule, two readers.

    Timing note that the emission relies on: the card's own deploys mutate the
    company mid-resolution, so the body captures this value at the TOP of
    OnPlay, against the same pre-play state the preview reads.
    """
    target = _salon_calc_target(card)
    if target is None or eff is not target[0]:
        return None
    _, deploys, var, mult = target
    return int(eff["amount"]), deploys, var, mult


def rider_tip_args(card: dict) -> str:
    """Track L-C: the C# arguments for the re-homed rider tip, or "".

    Only riders that were CONVERTED get a tip, because only those have had
    their arithmetic removed from the card text. An unconverted rider (the
    Bomb-detonation formula, an AoE aura rider) keeps its full sentence on the
    face, so re-homing it would delete the only place the player could read
    it."""
    args = []
    for eff in card.get("effects", []):
        # B1: a converted BLOCK rider has had its arithmetic removed from the
        # face exactly as a converted damage rider has, so it earns the same
        # tip. Without this the fix would trade a silent drop for a silent
        # number -- "{CalculatedBlock}" with nothing saying where it came from.
        if calc_rider(card, eff) is None \
                and block_calc_rider(card, eff) is None:
            continue
        m = re.fullmatch(r"(\d+)_per_(\d+)_fanfare", eff.get("bonus_formula", ""))
        members = re.fullmatch(r"(\d+)_per_salon_member",
                               eff.get("bonus_formula", ""))
        if m:
            args.append(f"fanfarePer: {int(m.group(1))}")
            args.append(f"fanfareStep: {int(m.group(2))}")
        elif members:
            # A13/A14: same re-homing bargain as the Fanfare rider. The face
            # keeps a short marker, the RATE and what the stage is paying
            # right now live here.
            args.append(f"salonPer: {int(members.group(1))}")
            if eff.get("op") == "block":
                args.append("salonGrantsBlock: true")
        elif "bonus_vs_aura" in eff:
            args.append(f"auraBonus: {int(eff['bonus_vs_aura'])}")
    return ", ".join(args)


def salon_scaled_snapshot(card: dict) -> str | None:
    """The C# local a converted salon card captures before its first deploy,
    or None. Named per var so the body reads plainly."""
    target = _salon_calc_target(card)
    if target is None:
        return None
    return "salonScaled" + target[2].removeprefix("Calculated")


def aura_calc_rider(card: dict, eff: dict) -> tuple[int, int] | None:
    """Furina Legibility sprint, pass 2: a SINGLE-TARGET `bonus_vs_aura` rider
    rendered through CalculatedDamageVar. Returns (base, bonus) or None.

    This is the shape CalculatedVar was built for: `Calculate(target)` receives
    the hovered creature during preview and the real one at resolution, so the
    face greens exactly when you hover an aura'd enemy and the hit agrees.

    AoE (`target: all_enemies`) is deliberately EXCLUDED, and not merely as a
    display nicety: those cards emit a per-target `foreach` that re-tests
    `AuraCmd.Find` for each enemy, whereas AttackCommand resolves a
    CalculatedDamageVar once with `singleTarget == null`. Converting them would
    collapse a per-enemy decision into one flat value -- a real gameplay change
    (Furina's crashing_waves, Klee's flame_dance). They stay as they are."""
    if eff.get("op") != "damage" or eff.get("target") != "enemy":
        return None
    if "bonus_vs_aura" not in eff:
        return None
    if salon_deploy_card(card):
        return None
    return int(eff["amount"]), int(eff["bonus_vs_aura"])


def spotlight_calc_rider(card: dict, eff: dict) -> tuple[int, int] | None:
    """Furina Legibility sprint, pass 3 (Track L-A4): a COMPANION card's plain
    damage rendered through CalculatedDamageVar so the Spotlight GuestCast
    scaling (1.5x + flat) shows on the face and the enemy hover instead of only
    at resolution. Returns (base, 1) or None.

    Companions only. On Furina's own cards the `PrintedDamage` wrap is identity
    -- its bonus path needs `Mode == GuestCast`, and under GuestCast
    `IsSpotlighted` accepts only `ICompanionCard` -- so converting them would
    add a var for no visible change.

    Only the plain shape: a card carrying its own rider (bonus_formula /
    bonus_vs_aura) already owns the CalculatedDamageVar for that rider, and the
    two cannot share one var. None exist today; the guard keeps it that way.
    """
    if not is_companion(card):
        return None
    if eff.get("op") != "damage" or eff.get("target") == "self":
        return None
    if "bonus_formula" in eff or "bonus_vs_aura" in eff:
        return None
    if salon_deploy_card(card):
        return None
    return int(eff["amount"]), 1


def spotlight_block_rider(card: dict, eff: dict) -> int | None:
    """Track L-A4, block half: a COMPANION card's block rendered through the
    base game's `CalculatedBlockVar` so the Spotlight GuestCast scaling shows on
    the face. Returns the printed base, or None.

    `CalculatedBlockVar` is the exact block twin of `CalculatedDamageVar` --
    it overrides UpdateCardPreview to run `Hook.ModifyBlock`, so block-modifying
    powers still reach the preview. It reads `CalculationBase` + `CalculationExtra`.

    Excluded: a card whose DAMAGE already converts. `CalculatedDamageVar` and
    `CalculatedBlockVar` both take their base from the single `CalculationBase`
    var, so a card doing both would compute its block off the damage base.
    freminet_pressurized_floe is the only one, and its damage conversion wins.
    Also excluded: more than one block effect (same collision), and salon-deploy
    cards (the x3 replacement multiplier is still inline)."""
    if not is_companion(card) or eff.get("op") != "block":
        return None
    if salon_deploy_card(card):
        return None
    effects = card.get("effects", [])
    if sum(1 for e in effects if e.get("op") == "block") != 1:
        return None
    if any(calc_rider(card, e) is not None for e in effects):
        return None
    return int(eff["amount"])


def block_calc_rider(card: dict, eff: dict) -> tuple[int, int, str] | None:
    """B1 (playtest-2, 2026-07-28): a scaling rider on a BLOCK op, rendered
    through `CalculatedBlockVar`. Returns (base, extra, multiplier-lambda) or
    None -- the block twin of `calc_rider`, and the same one-predicate-four-
    sites discipline.

    THE DEFECT THIS CLOSES. Every rider predicate in this file gated on
    `op != "damage"`, because until Curtain Call C every rider in the pool
    was a damage rider. Thunderous Ovation hung `1_per_2_fanfare` on a
    *block* op and the generator dropped it without a word: the sheet said
    "6, +1 per 2 Fanfare", the card gave a flat 6, and the playtest reported
    exactly that ("just gave 6 block"). The sim had implemented the rider all
    along, so this was a pure C#-side silent drop.

    The rail already existed -- `spotlight_block_rider` renders companion
    block this way and `salon_calc_rider` renders usher's -- so this adds a
    predicate, not a mechanism.

    Guards mirror `spotlight_block_rider`'s, and for the same reason:
    `CalculationBase` is a SINGLE var, so a card converting two numbers
    through it would compute one off the other's base.
    """
    if eff.get("op") != "block":
        return None
    formula = eff.get("bonus_formula", "")
    m = re.fullmatch(r"(\d+)_per_(\d+)_fanfare", formula)
    # A13 (2026-07-28): the per-member slope rides the same rail on a block op
    # -- Dinner Service is its first card, and the whole point of the rework is
    # that the face shows the stage paying.
    members = re.fullmatch(r"(\d+)_per_salon_member", formula)
    if not m and not members:
        return None
    if salon_deploy_card(card):
        return None
    effects = card.get("effects", [])
    if sum(1 for e in effects if e.get("op") == "block") != 1:
        return None
    # Damage conversions and the two other block conversions all claim
    # CalculationBase; whichever the card already has wins and this stays off.
    if any(calc_rider(card, e) is not None for e in effects):
        return None
    if any(spotlight_block_rider(card, e) is not None
           or salon_calc_rider(card, e) is not None for e in effects):
        return None
    if members:
        return int(eff["amount"]), int(members.group(1)), (
            f"static (card, _) => {SALON_MEMBER_COUNT_CS}")
    return int(eff["amount"]), int(m.group(1)), (
        "static (card, _) => "
        f"FurinaResources.Fanfare(card.Owner.Creature) / {int(m.group(2))}")


def calc_rider(card: dict, eff: dict) -> tuple[int, int, str] | None:
    """Unified view of every damage rider that renders through a
    CalculatedDamageVar: (base, extra, multiplier-lambda source). The four
    emission sites -- vars, OnPlay, description token, upgrade target -- all key
    off this one predicate so they cannot disagree about which shape a card is.
    The multiplier func must be static (CalculatedVar rejects instance targets).
    """
    fanfare = fanfare_calc_rider(card, eff)
    if fanfare is not None:
        base, per_n, div = fanfare
        return base, per_n, (
            "static (card, _) => "
            f"FurinaResources.Fanfare(card.Owner.Creature) / {div}")
    pile = exhaust_pile_calc_rider(card, eff)
    if pile is not None:
        return pile
    charge = charge_calc_rider(card, eff)
    if charge is not None:
        base, per_n, div = charge
        return base, per_n, (
            "static (card, _) => "
            f"KokomiResources.GetCharge(card.Owner.Creature) / {div}")
    encore = encore_calc_rider(card, eff)
    if encore is not None:
        base, per_n, div = encore
        return base, per_n, (
            "static (card, _) => "
            f"FurinaResources.Encore(card.Owner.Creature) / {div}")
    members = salon_member_calc_rider(card, eff)
    if members is not None:
        base, per_n, _ = members
        return base, per_n, f"static (card, _) => {SALON_MEMBER_COUNT_CS}"
    aura = aura_calc_rider(card, eff)
    if aura is not None:
        base, bonus = aura
        # Guard the null: preview calls Calculate(null) whenever nothing is
        # hovered, and AuraCmd.Find would throw on it.
        return base, bonus, (
            "static (_, target) => "
            "target != null && AuraCmd.Find(target) != null ? 1 : 0")
    spotlight = spotlight_calc_rider(card, eff)
    if spotlight is not None:
        base, extra = spotlight
        # base + 1 * (PrintedDamage(base) - base) == PrintedDamage(base):
        # the same number the card resolves today, now also the number it
        # prints. The delta lives in SpotlightSystem so the arithmetic has
        # exactly one home.
        return base, extra, (
            "static (card, _) => SpotlightSystem.PrintedDamageDelta(card)")
    return None


def salon_calc_var_decls(card: dict, eff: dict) -> list[str] | None:
    """The CalculationBase + extra + CalculatedVar trio for a salon-scaled
    number, or None. Damage reads its extra term from `ExtraDamage` (that is
    what `CalculatedDamageVar.GetExtraVar` overrides to); everything else
    reads `CalculationExtra`."""
    rider = salon_calc_rider(card, eff)
    if rider is None:
        return None
    base, deploys, var, mult = rider
    calc = (
        f"new {var}Var(ValueProp.Move)"
        if var in ("CalculatedDamage", "CalculatedBlock")
        else f'new CalculatedVar("{var}")')
    return [
        f'new CalculationBaseVar({base}m)',
        ('new ExtraDamageVar(1m)' if var == "CalculatedDamage"
         else 'new CalculationExtraVar(1m)'),
        f'{calc}.WithMultiplier(static (card, _) => '
        f'SalonMemberPower.ReplacementDelta(card, {deploys}, '
        f'SalonConstants.{mult}))',
    ]


def build_vars(card: dict) -> list[str]:
    """DynamicVar declarations, in the order the effects use them."""
    out = []
    for eff in card["effects"]:
        op = eff["op"]
        salon_decls = salon_calc_var_decls(card, eff)
        if salon_decls is not None:
            out.extend(salon_decls)
            continue
        # Constructor shapes differ per var and are NOT uniform: DamageVar and
        # BlockVar take (decimal, ValueProp); CardsVar takes a bare int;
        # HpLossVar takes a bare decimal. Verified against the decompiled
        # sts2 sources -- assuming a uniform shape here does not compile.
        if op == "damage" and eff["target"] == "self":
            out.append(f'new HpLossVar({eff["amount"]}m)')
        elif op == "damage":
            rider = calc_rider(card, eff)
            if rider is not None:
                base, extra, mult = rider
                # PerfectedStrike idiom: base + extra * multiplier, so the
                # face/preview (:diff green) and the hit resolve identically.
                out.append(f'new CalculationBaseVar({base}m)')
                out.append(f'new ExtraDamageVar({extra}m)')
                out.append(
                    'new CalculatedDamageVar(ValueProp.Move)'
                    f'.WithMultiplier({mult})')
            elif eff is not damage_var_effect(card):
                pass          # literal; only the upgraded hit declares a var
            else:
                out.append(f'new DamageVar({eff["amount"]}m, ValueProp.Move)')
                if "bonus_formula" in eff and bonus_per_upgrade(card):
                    n = int(eff["bonus_formula"].partition("_per_")[0])
                    out.append(f'new DynamicVar("BonusPer", {n}m)')
            # An upgradeable HIT COUNT is independent of the damage var: A5's
            # Undercurrent upgrades times (3 -> 5) and leaves the per-hit 2
            # alone, so this is not an `elif` on the branches above.
            if eff is times_var_effect(card):
                out.append(f'new DynamicVar("Times", {eff["times"]}m)')
        elif op == "block":
            block_rider = block_calc_rider(card, eff)
            block_base = spotlight_block_rider(card, eff)
            if block_rider is not None:
                base, extra, mult = block_rider
                out.append(f'new CalculationBaseVar({base}m)')
                out.append(f'new CalculationExtraVar({extra}m)')
                out.append(
                    'new CalculatedBlockVar(ValueProp.Move)'
                    f'.WithMultiplier({mult})')
            elif block_base is not None:
                # Mirage idiom: base + 1 * (PrintedBlock(base) - base), which
                # is PrintedBlock(base) -- the number the card already gains,
                # now also the number it prints.
                out.append(f'new CalculationBaseVar({block_base}m)')
                out.append('new CalculationExtraVar(1m)')
                out.append(
                    'new CalculatedBlockVar(ValueProp.Move).WithMultiplier('
                    'static (card, _) => '
                    'SpotlightSystem.PrintedBlockDelta(card))')
            else:
                out.append(f'new BlockVar({eff["amount"]}m, ValueProp.Move)')
        elif op == "draw":
            out.append(f'new CardsVar({int(eff["amount"])})')
        elif op == "discard" and plain_discard_upgrade(card):
            # G6: only an UPGRADEABLE plain discard needs a var, so every
            # existing card keeps its literal and its generated file does not
            # churn. "Discards" collides with no base-game var name (CardsVar
            # is `Cards`, and this card already spends that on its draw).
            out.append(f'new DynamicVar("Discards", {int(eff["amount"])}m)')
        elif op == "place_bomb":
            if bomb_var(card) == "ExtraDamage":
                out.append(f'new ExtraDamageVar({eff["bomb_damage"]}m)')
            else:
                out.append(f'new DamageVar({eff["bomb_damage"]}m, ValueProp.Move)')
            if isinstance(eff.get("amount"), str) and bombs_upgrade(card):
                # X_plus_N with a ruled bombs delta: the +N renders/upgrades.
                n = int(eff["amount"][len("X_plus_"):])
                out.append(f'new DynamicVar("Bombs", {n}m)')
        elif op == "gain_spark" and spark_upgrade(card):
            # Only an upgradeable spark amount needs a var (the new value must
            # render); "Sparks" collides with no base-game var name. Cards
            # without a sheet upgrade keep the literal (see MECHANICAL_OPS).
            out.append(f'new DynamicVar("Sparks", {int(eff["amount"])}m)')
        elif op == "summon_kurage" and kurage_turns_upgrade(card):
            # Same rule as Sparks/BurstEnergy: a var ONLY when the upgrade has
            # to render. Duration is the only thing bake_kurage's upgrade may
            # move -- the pulse numbers are constants and the +1 Charge is
            # untouchable under the resource-curve law -- so one var covers it.
            out.append(
                f'new DynamicVar("KurageTurns", {int(eff.get("amount", 1))}m)')
        elif op == "energy" and energy_upgrade(card):
            out.append(f'new DynamicVar("Energy", {int(eff["amount"])}m)')
        elif op == "block_next_turn" and block_next_turn_upgrade(card):
            out.append(
                f'new DynamicVar("BlockNextTurn", {int(eff["amount"])}m)')
        elif op == "exhaust_from" and exhaust_upgrade(card):
            out.append(
                f'new DynamicVar("Exhausts", {int(eff.get("amount", 1))}m)')
        elif op == "burst_energy" and burst_upgrade(card):
            # Same rule as Sparks: a var only when the upgrade must render.
            out.append(f'new DynamicVar("BurstEnergy", {int(eff["amount"])}m)')
        elif op == "raise_fanfare_cap":
            out.append(
                f'new DynamicVar("FanfareCap", {int(eff["amount"])}m)')
        elif op == "gain_fanfare_floor":
            # Always a var, never a literal: BOTH sheet cards carrying this op
            # have a fanfare_floor upgrade delta, so the new value must render
            # on the upgraded card. (G-A2.)
            out.append(
                f'new DynamicVar("FanfareFloor", {int(eff["amount"])}m)')
        elif op == "heal":
            out.append(f'new DynamicVar("Heal", {int(eff["amount"])}m)')
        elif op in POWER_UPGRADE_OPS and eff is power_upgrade_effect(card):
            # Same rule again: only an upgradeable amount needs a var, and
            # only the ONE effect the sim's delta binds to may own it -- a
            # second apply_power on the same card must stay a literal, or the
            # duplicate "PowerAmount" key throws in the DynamicVarSet
            # constructor at reward time (2026-07-23 softlock).
            out.append(f'new DynamicVar("PowerAmount", {int(eff["amount"])}m)')
        elif op == "discard_for_sparks" and discard_upgrade(card) != (0, 0):
            # R36: both numbers render, so both become vars together.
            out.append(f'new DynamicVar("Discards", {int(eff["amount"])}m)')
            out.append(f'new DynamicVar("Sparks", {int(eff["sparks"])}m)')
        elif op in BONUS_OPS and "bonus" in eff and bonus_upgrade(card):
            # Same rule as Sparks: a var only when the upgrade must render.
            out.append(f'new DynamicVar("Bonus", {int(eff["bonus"])}m)')
        elif op == "chance_bomb_per_detonation" and chance_upgrade(card):
            # Rendered as a PERCENT (50 -> 75); the body divides by 100.
            out.append(
                f'new DynamicVar("Chance", {int(round(float(eff["chance"]) * 100))}m)')
        elif op == "add_card" and stash_upgrade(card):
            out.append(f'new DynamicVar("Stash", {int(eff.get("amount", 1))}m)')
        elif op == "conditional":
            # Branch amounts are literals unless a ruled delta targets them:
            # conditional_bonus -> then-first damage (ExtraDamage), draw ->
            # branch draws (Cards then / DrawElse else). repeat-conditionals
            # carry no numbers of their own.
            if any(e.get("op") == "repeat_this" for e in eff.get("then", [])):
                continue
            cb = conditional_bonus_upgrade(card)
            bd = branch_draw_upgrade(card)
            then_var, else_var = branch_draw_vars(card)
            for e in eff.get("then", []):
                if e["op"] == "damage" and cb:
                    out.append(f'new ExtraDamageVar({e["amount"]}m)')
                    cb = 0                       # first damage only
                elif e["op"] == "draw" and bd:
                    out.append(
                        f'new CardsVar({int(e["amount"])})'
                        if then_var == "Cards"
                        else f'new DynamicVar("{then_var}", '
                             f'{int(e["amount"])}m)')
            for e in eff.get("else", []):
                if e["op"] == "draw" and bd:
                    out.append(
                        f'new DynamicVar("{else_var}", {int(e["amount"])}m)')
    if added_draw_upgrade(card):
        out.append(f"new CardsVar({added_draw_upgrade(card)})")
    # DynamicVarSet's constructor throws on a duplicate name, and it runs
    # inside CardFactory.CreateForReward -- a collision is a reward-screen
    # softlock on whatever run happens to roll the card. Fail the GENERATOR
    # instead. Typed vars carry their class-derived name (DamageVar ->
    # "Damage"), named vars declare theirs.
    names = [
        (m.group(1)
         if (m := re.search(r'(?:DynamicVar|CalculatedVar)\("(\w+)"', decl))
         else re.match(r"new (\w+?)Var\(", decl).group(1))
        for decl in out
    ]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        raise SystemExit(
            f"gen_klee_cards: {card['id']}: duplicate DynamicVar name(s) "
            f"{dupes} -- DynamicVarSet throws at reward time "
            "(2026-07-23 softlock).")
    return out


_upgrade_deltas: dict | None = None


def upgrade_deltas() -> dict:
    """Per-card delta maps, merged across the upgrade sheets exactly as
    tier0/content/upgrades.py._upgrade_index does (R20: the upgrade sheets are
    the only home for deltas; inline `upgrade:` keys block the card).

    Two sheets since the Fontaine companions entered Klee's reward slot
    (2026-07-21 ruling): their deltas live in furina-upgrades.yaml, and the
    sim merges both, so a generator reading only klee-upgrades.yaml would emit
    unupgradeable cards the sim happily smiths. Duplicate ids across sheets are
    a hard error on the sim side; mirrored here rather than silently
    last-wins.
    """
    global _upgrade_deltas
    if _upgrade_deltas is None:
        merged: dict = {}
        for sheet in UPGRADE_SHEETS:
            if not sheet.exists():
                continue
            entries = yaml.safe_load(sheet.read_text(encoding="utf-8")) or {}
            dupes = set(entries) & set(merged)
            if dupes:
                raise SystemExit(
                    f"gen_klee_cards: {sheet.name}: duplicate upgrade ids "
                    f"{sorted(dupes)} -- the sim raises on this too.")
            merged.update(entries)
        _upgrade_deltas = merged
    return _upgrade_deltas


def upgrade_plan(card: dict) -> tuple[dict, str | None]:
    """(deltas, None) when every ruled delta key is expressible on this card,
    ({}, reason) otherwise.

    Partial application is forbidden (R24): expressing half a ruled upgrade
    silently approximates the other half, which is exactly the failure mode
    the UNAPPLIABLE discipline exists to prevent. A card with an inexpressible
    key gets no upgrade lines at all and a manifest flag naming the key.
    """
    deltas = upgrade_deltas().get(card["id"])
    if not deltas:
        return {}, "no ratified delta in klee-upgrades.yaml"
    effects = card.get("effects", [])
    # Branch effects too: tier0's `everywhere` (draw deltas bump ALL draw
    # ops, branches included -- "both branches" is sheet law).
    everywhere = list(effects)
    for e in effects:
        if e.get("op") == "conditional":
            everywhere.extend(e.get("then", []))
            everywhere.extend(e.get("else", []))
    non_repeat_conditionals = [
        e for e in effects
        if e.get("op") == "conditional"
        and not any(x.get("op") == "repeat_this" for x in e.get("then", []))]
    has = {
        "damage": any(e["op"] == "damage" and e["target"] != "self" for e in effects),
        "block": any(e["op"] == "block" for e in effects),
        "draw": any(e["op"] == "draw" for e in everywhere),
        # conditional_bonus: tier0 bumps the then-branch's first damage|block;
        # codegen expresses the damage form (ExtraDamage var). A then-block
        # first would need a second Block var -- structural until needed.
        "conditional_bonus": any(
            next((x for x in c.get("then", [])
                  if x.get("op") in ("damage", "block")), {}
                 ).get("op") == "damage"
            for c in non_repeat_conditionals),
        "condition": bool(non_repeat_conditionals),
        # bombs: tier0 rewrites X_plus_N -> X_plus_(N+val).
        "bombs": any(e["op"] == "place_bomb"
                     and isinstance(e.get("amount"), str) for e in effects),
        # bonus_per_detonation: tier0 rewrites the bonus_formula's N.
        "bonus_per_detonation": any("bonus_formula" in e for e in effects),
        # cards: tier0 bumps the add_card amount.
        "cards": any(e["op"] == "add_card" for e in effects),
        # remove: value-checked in the loop below (only 'exhaust' lands;
        # 'self_damage' remains structural).
        "remove": bool(card.get("exhaust")),
        # copy_cost_override: play-time IsUpgraded read in the copy emission.
        "copy_cost_override": any(e["op"] == "copy_companion_in_hand"
                                  for e in effects) or any(
            e["op"] == "copy_spotlighted_in_hand" for e in effects),
        "generate_cost_override": any(
            e["op"] == "generate_guest_star" for e in effects),
        "spark": any(e["op"] == "gain_spark" for e in effects),
        "encore": any(e["op"] == "gain_encore" for e in everywhere),
        "encore_cost": int(card.get("encore_cost", 0)) > 0,
        "fanfare_cost": int(card.get("fanfare_cost", 0)) > 0,
        "fanfare_cap": any(e["op"] == "raise_fanfare_cap" for e in effects),
        # G-A2. upgrades.py binds this delta to the first TOP-LEVEL
        # gain_fanfare_floor, so `effects` (not `everywhere`) is the right
        # scope -- a floor grant nested inside a conditional would not be the
        # one the sim bumps, and pretending otherwise would silently upgrade
        # the wrong branch.
        "fanfare_floor": any(
            e["op"] == "gain_fanfare_floor" for e in effects),
        "heal": any(e["op"] == "heal" for e in effects),
        "bomb_damage": any(e["op"] == "place_bomb" for e in effects),
        "burst_energy": any(e["op"] == "burst_energy" for e in effects),
        "cost": str(card.get("cost")) != "X",
        # R36: both keys ride the one discard_for_sparks effect.
        # G6 (Neap Tide v2.1) also lets `discard` bind the PLAIN discard op,
        # which Kokomi's Sly lane uses and Klee's Spark lane does not. Mirrors
        # tier0/content/upgrades.py, which tries discard_for_sparks FIRST and
        # falls back -- the two appliers must agree on which effect a delta
        # lands on or the generated card and the simulated card upgrade
        # differently, which no test would catch by value.
        "discard": any(e["op"] in ("discard_for_sparks", "discard")
                       for e in effects),
        "sparks": any(e["op"] == "discard_for_sparks" for e in effects),
        # R37: card-level, any card can become Innate or Retain.
        "innate": True,
        "retain": True,
        # Bomb-op batch: bonus rides a bonus-carrying bomb op; chance is
        # the chance_bomb_per_detonation replacement.
        "bonus": any(e["op"] in BONUS_OPS and "bonus" in e for e in effects),
        "chance": any(e["op"] == "chance_bomb_per_detonation" for e in effects),
        # Structural `add` upgrades currently support one exact, verified
        # shape: append a draw effect. It is emitted as an IsUpgraded-gated
        # draw at the end of OnPlay, matching upgrades.py's list append.
        "add": True,
        # Kokomi. Each binds to the op that owns the number, so a delta on a
        # card without that op is still reported unexpressible rather than
        # silently dropped on the floor.
        "kurage_turns": any(e["op"] == "summon_kurage" for e in effects),
        "energy": any(e["op"] == "energy" for e in effects),
        "block_next_turn": any(e["op"] == "block_next_turn" for e in effects),
        # Only the CHOSEN branch: raising a RANDOM exhaust_from above 1 has no
        # C# path (the re-pooling loop was never built), so such a card must
        # stay unexpressible and loudly blocked rather than generate wrong.
        "exhaust": any(e["op"] == "exhaust_from"
                       and e.get("select") == "chosen" for e in effects),
        # times: tier0 bumps the first damage|apply_power op's `times`.
        # Codegen expresses the DAMAGE form (the Times var feeds
        # DamageCmd.Attack().WithHitCount). A repeat on apply_power would
        # need its own var and has no card yet -- structural until then, and
        # reported unexpressible rather than silently dropped.
        "times": any(e["op"] == "damage" and e.get("target") != "self"
                     and isinstance(e.get("times"), int) and e["times"] > 1
                     for e in effects),
        "formula_per": any(
            exhaust_pile_calc_rider(card, e) is not None for e in effects),
        "formula_base": any(
            exhaust_pile_calc_rider(card, e) is not None for e in effects),
    }
    # tier0 binds every POWER_UPGRADE_KEYS delta to the first TOP-LEVEL
    # apply_power OR buff_next_attack (upgrades.py takes `next(fx for fx in
    # top if fx["op"] in (...))`), which is how `buff` reaches both Bennett's
    # apply_power and Chevreuse's buff_next_attack.
    for pkey in POWER_UPGRADE_KEYS:
        has[pkey] = any(e["op"] in POWER_UPGRADE_OPS for e in effects)
    for key, value in deltas.items():
        if key not in EXPRESSIBLE_DELTAS:
            return {}, f"delta key '{key}: {value}' not expressible by codegen (structural upgrade)"
        if key == "add":
            if not (isinstance(value, dict)
                    and set(value) == {"op", "amount"}
                    and value.get("op") in {"draw", "gain_encore"}
                    and isinstance(value.get("amount"), int)
                    and value["amount"] > 0):
                return {}, (
                    f"delta 'add: {value}' (only a positive draw or "
                    "gain_encore effect is expressible)")
            if value["op"] == "draw" and any(
                    e.get("op") == "draw" for e in everywhere):
                return {}, "delta 'add: draw' on a card with an existing draw (Cards var collision)"
            if any(e.get("op") == "conditional" and any(
                    x.get("op") == "repeat_this" for x in e.get("then", []))
                   for e in effects):
                return {}, "delta 'add: draw' on a repeating card (repeat semantics not expressible)"
        if key == "condition" and value != "unconditional":
            return {}, f"delta 'condition: {value}' (only 'unconditional' is tier0 grammar)"
        if key == "remove" and value != "exhaust":
            return {}, f"delta 'remove: {value}' not expressible by codegen (structural upgrade)"
        if not has[key]:
            return {}, f"delta key '{key}' has no matching effect on this card (sheet/card mismatch)"
    return dict(deltas), None


def added_draw_upgrade(card: dict) -> int:
    """Amount of an upgrade-only draw appended by `add`, or zero.

    The full upgrade plan validates the structural shape and collision rules;
    callers only need the amount for vars, text, and play-time emission.
    """
    added = upgrade_plan(card)[0].get("add")
    return (int(added["amount"])
            if isinstance(added, dict) and added.get("op") == "draw" else 0)


def added_encore_upgrade(card: dict) -> int:
    """Upgrade-only gain_encore effect appended by `add`, or zero."""
    added = upgrade_plan(card)[0].get("add")
    return (int(added["amount"])
            if isinstance(added, dict)
            and added.get("op") == "gain_encore" else 0)


def encore_upgrade(card: dict) -> int:
    """Ruled Encore delta. The sim applies it to every gain_encore effect,
    branches included; generated play/text use IsUpgraded at each site."""
    return int(upgrade_plan(card)[0].get("encore", 0))


def spark_upgrade(card: dict) -> int:
    """Ruled Spark upgrade delta (M9): `spark: +N` in klee-upgrades.yaml. 0 = none.
    Zero when the card's upgrade plan is unappliable -- no upgrade renders."""
    return int(upgrade_plan(card)[0].get("spark", 0))


def burst_upgrade(card: dict) -> int:
    """Ruled Burst-energy upgrade delta: `burst_energy: +N`. 0 = none."""
    return int(upgrade_plan(card)[0].get("burst_energy", 0))


def discard_upgrade(card: dict) -> tuple[int, int]:
    """Ruled R36 deltas on discard_for_sparks: (discard: +N, sparks: +M).
    (0, 0) = none; either key alone still upgrades both vars' rendering."""
    deltas = upgrade_plan(card)[0]
    return int(deltas.get("discard", 0)), int(deltas.get("sparks", 0))


def plain_discard_upgrade(card: dict) -> int:
    """G6: a `discard` delta landing on the PLAIN discard op, not Crackle's.

    Zero when the card has no such delta, or when it carries
    discard_for_sparks -- which wins the binding in BOTH appliers (tier0
    upgrades.py tries it first, and this mirrors that order). Getting the
    precedence wrong here would not fail a build; it would upgrade a
    different effect than the simulator does, which is the class of
    divergence the constant-parity gate exists for and cannot see.
    """
    effects = _effects_everywhere(card)
    if any(e["op"] == "discard_for_sparks" for e in effects):
        return 0
    if not any(e["op"] == "discard" for e in effects):
        return 0
    return int(upgrade_plan(card)[0].get("discard", 0))


def bonus_upgrade(card: dict) -> int:
    """Ruled `bonus: +N` delta on the card's bomb op. 0 = none. One
    DynamicVar name ("Bonus") serves it, so a second bonus-carrying effect
    on the same card is a loud stop, not a silent overwrite."""
    delta = int(upgrade_plan(card)[0].get("bonus", 0))
    if delta:
        n = sum(1 for e in card["effects"]
                if e.get("op") in BONUS_OPS and "bonus" in e)
        if n > 1:
            raise SystemExit(
                f"gen_klee_cards: {card['id']}: {n} bonus-carrying bomb ops "
                "-- one 'Bonus' var cannot serve two effects.")
    return delta


def chance_upgrade(card: dict) -> float:
    """Ruled `chance: X` REPLACEMENT (tier0 upgrades.py replaces, never
    bumps). 0.0 = none."""
    return float(upgrade_plan(card)[0].get("chance", 0.0))


def stash_upgrade(card: dict) -> int:
    """Ruled `cards: +N` (secret_stash): bumps the add_card amount. Rides a
    'Stash' var ('Cards' is the draw CardsVar's name). 0 = none."""
    return int(upgrade_plan(card)[0].get("cards", 0))


def bonus_per_upgrade(card: dict) -> int:
    """Ruled `bonus_per_detonation: +N` (grand_finale): the bonus_formula's
    per-detonation rate, rendered/upgraded via the BonusPer var. 0 = none."""
    return int(upgrade_plan(card)[0].get("bonus_per_detonation", 0))


def times_var_effect(card: dict) -> dict | None:
    """The ONE damage effect whose hit count is upgradeable, or None.

    tier0's `times` delta is a _bump_first over damage|apply_power, so only
    the FIRST literal multi-hit damage op is upgradeable -- the same
    first-effect-owns-the-var rule as damage_var_effect. Every other
    multi-hit op keeps rendering its literal count.
    """
    if not times_upgrade(card):
        return None
    return next((e for e in card.get("effects", [])
                 if e["op"] == "damage" and e.get("target") != "self"
                 and isinstance(e.get("times"), int) and e["times"] > 1),
                None)


def times_upgrade(card: dict) -> int:
    """Ruled `times: +N` (A5 undercurrent): the hit count moves on upgrade,
    so the count rides a Times var and renders with diff(). 0 = none."""
    return int(upgrade_plan(card)[0].get("times", 0))


def bombs_upgrade(card: dict) -> int:
    """Ruled `bombs: +N` (controlled_demolition): X_plus_1 -> X_plus_2.
    Rides the Bombs var so the +1 renders with diff(). 0 = none."""
    return int(upgrade_plan(card)[0].get("bombs", 0))


def conditional_bonus_upgrade(card: dict) -> int:
    """Ruled `conditional_bonus: +N` (tail_of_flame): bumps the then-branch's
    first damage. 0 = none. The bump rides the ExtraDamage var, so a card
    whose bombs already claim ExtraDamage is a loud stop."""
    delta = int(upgrade_plan(card)[0].get("conditional_bonus", 0))
    if delta and any(e.get("op") == "place_bomb"
                     for e in _effects_everywhere(card)):
        raise SystemExit(
            f"gen_klee_cards: {card['id']}: conditional_bonus needs the "
            "ExtraDamage var but the card also places bombs -- two claims "
            "on one var name.")
    return delta


def condition_upgrade(card: dict) -> bool:
    """Ruled `condition: unconditional` (patched_dress): the upgraded card
    runs the then-branch always. C#: predicate reads (IsUpgraded || pred);
    text swaps via {IfUpgraded:show:...|...}."""
    return upgrade_plan(card)[0].get("condition") == "unconditional"


def branch_draw_vars(card: dict) -> tuple[str, str]:
    """(then-branch var, else-branch var) for a card's branch draws.

    Normally the then-branch rides `Cards`, because a card whose draws live
    ONLY in branches has no top-level draw competing for that name
    (eager_to_help). Compose Herself broke that assumption at Curtain Call:
    it draws 2 at top level AND 1 more inside its Encore branch, and tier0's
    draw delta bumps ALL draw ops, so both numbers are upgradeable and both
    need a var. `Cards` is already spoken for by the top-level draw, so the
    branch takes `DrawThen`.

    A third NAME rather than a shared var: DynamicVarSet throws on duplicates
    inside CardFactory.CreateForReward, which is a reward-screen softlock on
    whatever run happens to roll the card.
    """
    top_draws = [e for e in card["effects"] if e.get("op") == "draw"]
    return ("DrawThen" if top_draws else "Cards"), "DrawElse"


def branch_draw_upgrade(card: dict) -> int:
    """Ruled `draw: +N` when the card's draws live inside conditional
    branches (eager_to_help, and Compose Herself which also draws at top
    level). tier0 bumps ALL draw ops; the branch draws ride the vars
    `branch_draw_vars` assigns."""
    delta = int(upgrade_plan(card)[0].get("draw", 0))
    if not delta:
        return 0
    branch_draws = [e for e in _effects_everywhere(card)
                    if e.get("op") == "draw"]
    top_draws = [e for e in card["effects"] if e.get("op") == "draw"]
    # _effects_everywhere is a superset of the top level, so equal counts mean
    # there are no branch draws at all and the plain top-level path applies.
    return 0 if len(branch_draws) == len(top_draws) else delta


def _effects_everywhere(card: dict) -> list[dict]:
    out = []
    for e in card.get("effects", []):
        out.append(e)
        if e.get("op") == "conditional":
            out.extend(e.get("then", []))
            out.extend(e.get("else", []))
    return out


def power_upgrade(card: dict) -> int:
    """Ruled power-amount delta (power_amount/amp_percent/splash_damage/
    vulnerable all bump the applied amount -- tier0 upgrades.py handles them
    in one branch too). 0 = none."""
    deltas = upgrade_plan(card)[0]
    keys = [k for k in POWER_UPGRADE_KEYS if k in deltas]
    if len(keys) > 1:
        raise SystemExit(
            f"gen_klee_cards: {card['id']}: multiple power upgrade keys {keys} "
            "-- one apply_power effect cannot take two amount deltas.")
    return int(deltas[keys[0]]) if keys else 0


def damage_var_effect(card: dict) -> dict | None:
    """The ONE top-level damage effect that owns the `Damage` var.

    Exactly the power_upgrade_effect rule, one var-name over: tier0's `damage`
    delta is a _bump_first over top-level non-self damage ops, so only the
    FIRST such effect is upgradeable and only it may declare a var. Every
    later damage effect renders its printed literal.

    Curtain Call's Matinee Performance is the first card in the pool with two
    top-level damage ops (a flat hit, then a per-member hit). Before this rule
    both declared "Damage" and the generator's own duplicate-name check fired
    -- which is the check standing in for a DynamicVarSet constructor throw
    inside CardFactory.CreateForReward, i.e. a reward-screen softlock on
    whatever run rolled the card.
    """
    return next((fx for fx in card.get("effects", [])
                 if fx.get("op") == "damage"
                 and fx.get("target") != "self"), None)


def power_upgrade_effect(card: dict) -> dict | None:
    """The ONE top-level effect the ruled power delta binds to, mirroring
    tier0/content/upgrades.py exactly: `weak`/`vulnerable` bump the first
    apply_power whose power NAME contains the word; every other key takes the
    first top-level apply_power/buff_next_attack. Every other power effect on
    the card renders its printed literal and declares NO var -- two effects
    sharing the "PowerAmount" name is a DynamicVarSet constructor throw that
    kills the reward screen (playtest 2026-07-23: stage_lights,
    courtroom_drama)."""
    if not power_upgrade(card):
        return None
    deltas = upgrade_plan(card)[0]
    key = next(k for k in POWER_UPGRADE_KEYS if k in deltas)
    effects = card["effects"]
    if key in ("weak", "vulnerable"):
        word = "vuln" if key == "vulnerable" else "weak"
        hit = next((fx for fx in effects if fx.get("op") == "apply_power"
                    and word in fx.get("power", "")), None)
    else:
        hit = next((fx for fx in effects
                    if fx.get("op") in POWER_UPGRADE_OPS), None)
    if hit is None:
        # upgrade_plan vets "some POWER_UPGRADE_OPS effect exists" but not the
        # weak/vuln name match; the sim would fail to apply this delta, so a
        # silent literal here would ship a card whose upgrade does nothing.
        raise SystemExit(
            f"gen_klee_cards: {card['id']}: power delta '{key}' matches no "
            "top-level effect (tier0 upgrades.py binding rule) -- fix the "
            "sheet or the delta key.")
    return hit


def _target_guard(lines: list[str], ctx: dict) -> None:
    """One ThrowIfNull per OnPlay (cardPlay.Target is nullable; a
    single-target card played with no target is a bug in the caller, so fail
    loudly rather than silently no-op -- mirrors the hand-written Kaboom).
    ctx-tracked because conditional branches emit into sub-lists, where a
    text scan of `lines` cannot see the outer guard."""
    if not ctx["thrown"]:
        ctx["thrown"] = True
        lines.append(
            'ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");'
        )


def _emit_damage(card: dict, eff: dict, lines: list[str], ctx: dict,
                 amount_expr: str) -> None:
    """The one attack-damage builder -- top level, conditional branches and
    the repeat tail all route here so the targeting idiom cannot drift."""
    times = eff.get("times", 1)
    target = eff["target"]

    call = [f"await DamageCmd.Attack({amount_expr})"]
    x_times = isinstance(times, str)
    # A runtime hit count is gated on the same ">0 or no hits at all" rule as
    # X: tier0 loops `range(times)`, so a count of zero deals NOTHING rather
    # than one default hit. DamageCmd would treat a 0 hit count as one swing.
    times_guard = ("x" if times == "X" or (isinstance(times, str)
                                           and times.startswith("X_plus_"))
                   else RUNTIME_TIMES.get(times) if x_times else None)
    if "times_formula" in eff:
        # 2_plus_sparks (Gleeful Barrage), the sim's only times formula.
        # SparksAtPlay: R39 (2026-07-21 ruling) -- the sim computes times from
        # state.sparks_at_play, the bank BEFORE this card's own spend, because
        # hitting the threshold that makes the card free was otherwise exactly
        # what deleted the sparks it counts.
        call.append(
            ".WithHitCount(2 + SparkPower.SparksAtPlay(Owner.Creature))")
    elif x_times:
        # times: "X" (fish_blasting) or a runtime count (salon_members).
        # tier0 loops range(times): 0 means NO hits, so the whole attack
        # statement is gated below.
        call.append(
            f".WithHitCount({RUNTIME_TIMES.get(times) or _x_expr(times)})")
    elif eff is times_var_effect(card):
        # Ruled `times: +N`: the count lives in a var so OnUpgrade can bump it
        # and the face renders the diff. Literal counts keep the literal.
        call.append('.WithHitCount(DynamicVars["Times"].IntValue)')
    elif times > 1:
        call.append(f".WithHitCount({times})")
    call.append(".FromCard(this)")

    if target == "enemy":
        _target_guard(lines, ctx)
        call.append(".Targeting(cardPlay.Target)")
    elif target == "all_enemies":
        # CombatState is declared nullable but is always set while a
        # card is resolving -- every base-game AoE card dereferences it
        # unguarded.
        call.append(".TargetingAllOpponents(CombatState!)")
    else:  # random_enemy / random_enemies
        call.append(".TargetingRandomOpponents(CombatState!)")

    call.append('.WithHitFx("vfx/vfx_attack_slash")')
    if target == "all_enemies":
        call.append(".SpawningHitVfxOnEachCreature()")
    call.append(".Execute(choiceContext);")

    stmt = "\n            ".join(call)
    if times_guard:
        stmt = (f"if ({times_guard} > 0)\n        {{\n            "
                + stmt.replace("\n", "\n    ")
                + "\n        }")
    lines.append(stmt)


def _emit_place_bomb(card: dict, eff: dict, lines: list[str], ctx: dict,
                     dmg_expr: str) -> None:
    n = eff["amount"]
    if isinstance(n, str):
        # X-cost count (controlled_demolition): tier0 _amount, X or X_plus_N.
        n = _x_expr(n, bombs_var=bombs_upgrade(card) > 0)
    if eff["target"] == "enemy":
        _target_guard(lines, ctx)
        place = (
            f"await BombPower.Place(choiceContext, cardPlay.Target, {dmg_expr}, "
            "Owner.Creature, this);"
        )
        if n == 1:
            lines.append(place)
        else:
            lines.append(
                f"for (var i = 0; i < {n}; i++)\n        {{\n"
                f"            {place}\n        }}"
            )
    else:
        # Each bomb rolls its own target, so N bombs can land on N
        # different enemies -- matching Tier 0's per-bomb target pick.
        # HittableEnemies can be empty if the last enemy died earlier in
        # this card's resolution, and NextItem would throw on that.
        lines.append(
            f"for (var i = 0; i < {n}; i++)\n"
            "        {\n"
            "            var candidates = CombatState!.HittableEnemies.ToList();\n"
            "            if (candidates.Count == 0) break;\n"
            "            var bombTarget = Owner.RunState.Rng.CombatTargets.NextItem(candidates);\n"
            "            if (bombTarget == null) break;\n"
            f"            await BombPower.Place(choiceContext, bombTarget, {dmg_expr}, "
            "Owner.Creature, this);\n"
            "        }"
        )


def _stmt_gain_spark(card: dict, eff: dict) -> str:
    amount = ('DynamicVars["Sparks"].IntValue' if spark_upgrade(card)
              else str(int(eff["amount"])))
    return f"await SparkPower.Gain(choiceContext, Owner.Creature, {amount}, this);"


def _stmt_burst_energy(card: dict, eff: dict) -> str:
    amount = ('DynamicVars["BurstEnergy"].IntValue' if burst_upgrade(card)
              else str(int(eff["amount"])))
    return f"await KleeBurstResource.Gain(choiceContext, Owner.Creature, {amount}, this);"


def _encore_amount_expr(card: dict, eff: dict) -> str:
    base = int(eff["amount"])
    delta = encore_upgrade(card)
    return f"(IsUpgraded ? {base + delta} : {base})" if delta else str(base)


def energy_upgrade(card: dict) -> int:
    """Ruled energy delta: `energy: +N` in kokomi-upgrades.yaml."""
    return int(upgrade_plan(card)[0].get("energy", 0))


def block_next_turn_upgrade(card: dict) -> int:
    """Ruled deferred-block delta: `block_next_turn: +N` (Sayu's daruma)."""
    return int(upgrade_plan(card)[0].get("block_next_turn", 0))


def exhaust_upgrade(card: dict) -> int:
    """Ruled chosen-exhaust delta: `exhaust: +N` in kokomi-upgrades.yaml."""
    return int(upgrade_plan(card)[0].get("exhaust", 0))


def kurage_turns_upgrade(card: dict) -> int:
    """Ruled Bake-Kurage duration delta: `kurage_turns: +N`. 0 = none."""
    return int(upgrade_plan(card)[0].get("kurage_turns", 0))


def kurage_turns_expr(card: dict, eff: dict) -> str:
    """Duration of a summoned Bake-Kurage.

    A LITERAL unless kokomi-upgrades.yaml carries a `kurage_turns: +N` delta
    for this card, in which case it becomes the named DynamicVar the face
    reads -- the Sparks/BurstEnergy idiom. Duration is the ONLY thing an
    upgrade may move here: the pulse numbers are constants, and the +1 Charge
    is untouchable under the resource-curve law.
    """
    if kurage_turns_upgrade(card):
        return 'DynamicVars["KurageTurns"].IntValue'
    return str(int(eff.get("amount", 1)))


def _conscript_phrase(eff: dict) -> str:
    """Player-facing conscript text.

    R55 VOICE LAW: exhaust is ROTATION, never sacrifice. Forced service is
    Shogunate behaviour and the resistance were volunteers, so the display
    family is Muster/Enlist/Rally. The internal op name stays `conscript`;
    the FACE never says it.

    R78 (Neap Tide v2.1): the grammar is a KEYWORD now. Every conscript card
    used to restate the whole rule -- "transform N cards in your hand into a
    random Inazuma Companion that costs 1 less and Exhausts" -- on nine cards,
    which is ~90 characters of identical text per face and the reason several
    of them were at text budget. "Muster N" says it once; the hover tip
    (KokomiRiderTips.ForMuster, attached by codegen to every conscript card)
    carries the definition.

    DEVIATIONS WRITE OUT ONLY THE DEVIATION, which is the half that makes the
    keyword worth having. `create` mode adds the unit instead of replacing a
    card, and a cost_override pins the recruit's cost -- each prints its own
    clause and nothing else, so what a reader sees on the face is exactly what
    is different about this card.
    """
    n = int(eff.get("amount", 1))
    phrase = f"[gold]Muster[/gold] {n}"
    if eff.get("mode") == "create":
        # The deviation is WHERE the units land, not what they are.
        phrase += f", adding the unit{'' if n == 1 else 's'} to your hand"
    if "cost_override" in eff:
        # The deviation is the price. The keyword's own "costs 1 less" is
        # replaced, not stacked with -- KokomiConscript.RollRecruit treats
        # cost_override as reaching the target ABSOLUTELY.
        phrase += f", at cost {int(eff['cost_override'])}"
    return phrase


def _stmt_gain_encore(
    card: dict, eff: dict, *, salon_scaled: bool = False
) -> str:
    amount = _encore_amount_expr(card, eff)
    if salon_scaled:
        amount = f"{amount} * (salonReplacements > 0 ? 2 : 1)"
    return (
        "FurinaResources.GainEncore(Owner.Creature, "
        f"{amount});")


def _emit_branch_op(
    card: dict, eff: dict, lines: list[str], ctx: dict,
    in_then: bool, cb_state: dict, spotlight_capable: bool
) -> None:
    """Conditional-branch resolvers. Amounts are literals unless a ruled
    delta claims them (see build_vars): conditional_bonus -> then-first
    damage via ExtraDamage; draw delta -> Cards (then) / DrawElse (else)."""
    op = eff["op"]
    if op == "damage":
        if in_then and cb_state.get("pending"):
            cb_state["pending"] = False
            amount = "DynamicVars.ExtraDamage.BaseValue"
        else:
            amount = f'{int(eff["amount"])}m'
        if spotlight_capable:
            amount = f"SpotlightSystem.PrintedDamage(this, {amount})"
        _emit_damage(card, eff, lines, ctx, amount)
    elif op == "block":
        amount = f'{int(eff["amount"])}m'
        if spotlight_capable:
            amount = f"SpotlightSystem.PrintedBlock(this, {amount})"
        lines.append(
            "await CreatureCmd.GainBlock(Owner.Creature, "
            f"new BlockVar({amount}, ValueProp.Move), cardPlay);"
        )
    elif op == "draw":
        if branch_draw_upgrade(card):
            then_var, else_var = branch_draw_vars(card)
            expr = (("DynamicVars.Cards.BaseValue" if then_var == "Cards"
                     else f'DynamicVars["{then_var}"].IntValue') if in_then
                    else f'DynamicVars["{else_var}"].IntValue')
        else:
            expr = f'{int(eff["amount"])}m'
        lines.append(f"await CardPileCmd.Draw(choiceContext, {expr}, Owner);")
    elif op == "gain_spark":
        # Branch sparks are literal (no delta grammar reaches them yet;
        # spark_upgrade targets the top-level gain_spark).
        lines.append(
            f'await SparkPower.Gain(choiceContext, Owner.Creature, {int(eff["amount"])}, this);'
        )
    elif op == "burst_energy":
        lines.append(
            f'await KleeBurstResource.Gain(choiceContext, Owner.Creature, {int(eff["amount"])}, this);'
        )
    elif op == "gain_encore":
        lines.append(_stmt_gain_encore(card, eff))
    elif op == "energy":
        # DEFECT FIXED HERE (found by G8, 2026-07-26). An `energy` delta made
        # the CanonicalVars entry and the OnUpgrade bump, but the play emitted
        # the LITERAL -- so an upgraded swift_currents gained 2 energy in the
        # mod while the sim gave 3, and the card face printed 2 either way.
        # It shipped that way. Reading the var is what makes the declared
        # upgrade real; the description half is fixed alongside it.
        amount = ('DynamicVars["Energy"].IntValue' if energy_upgrade(card)
                  else int(eff["amount"]))
        lines.append(f"await PlayerCmd.GainEnergy({amount}, Owner);")
    elif op == "place_bomb":
        _emit_place_bomb(card, eff, lines, ctx, str(int(eff["bomb_damage"])))
    elif op == "buff_next_attack":
        # Always literal in a branch: the POWER_UPGRADE_KEYS deltas bind to
        # the first TOP-LEVEL effect only (tier0 upgrades.py), which is what
        # keeps Chevreuse's reaction rider at its printed value while her base
        # buff scales.
        lines.append(
            f"await PowerCmd.Apply<NextAttackUpPower>(choiceContext, "
            f'Owner.Creature, {int(eff["amount"])}, '
            "applier: Owner.Creature, cardSource: this);"
        )


def _conditional_block(pred: str, then_lines: list[str],
                       else_lines: list[str]) -> str:
    def body(stmts: list[str]) -> str:
        return "\n".join("            " + s.replace("\n", "\n    ")
                         for s in stmts)
    out = f"if ({pred})\n        {{\n{body(then_lines)}\n        }}"
    if else_lines:
        out += f"\n        else\n        {{\n{body(else_lines)}\n        }}"
    return out


def build_body(
    card: dict, profile: CharacterProfile = KLEE_PROFILE
) -> list[str]:
    """OnPlay statements. Every call here has a verified base-game call site."""
    lines = []
    ctx = {"thrown": False}
    spotlight_capable = is_companion(card) or profile is FURINA_PROFILE
    salon_deploy_present = any(
        effect.get("op") == "apply_power"
        and effect.get("power") == "salon_member"
        for effect in card.get("effects", []))
    salon_deployed = False
    if salon_deploy_present:
        lines.append("var salonReplacements = 0;")
    salon_snapshot = salon_scaled_snapshot(card)
    if salon_snapshot is not None:
        # The card's own deploys mutate the company as they run, so the
        # scaled value is captured HERE -- against the pre-play company the
        # card face read -- and spent below. Face and effect are then the
        # same evaluation of the same expression on the same state.
        target = _salon_calc_target(card)
        var = target[2]
        read = (f"DynamicVars.{var}.Calculate(null)"
                if var in ("CalculatedDamage", "CalculatedBlock")
                else f'((CalculatedVar)DynamicVars["{var}"]).Calculate(null)')
        lines.append(f"var {salon_snapshot} = {read};")
    # Predicate snapshots: the sim resets its per-card counters at
    # resolve_card START, so the C# diff bases are captured at the top of
    # OnPlay, before any effect resolves -- not at the conditional's site.
    preds = {e["if"] for e in card["effects"] if e.get("op") == "conditional"}
    if "reaction_triggered_by_this" in preds:
        lines.append("var reactionsAtStart = ReactionEffects.TotalResolved;")
    if "killed_target" in preds:
        lines.append("var enemiesAtStart = CombatState!.HittableEnemies.ToList();")
    if str(card.get("cost")) == "X":
        # tier0 play_card: current_x = energy actually spent. The captured
        # X value (through Hook.ModifyXValue) is the game's same number.
        lines.append("var x = ResolveEnergyXValue();")
    for eff in card["effects"]:
        op = eff["op"]

        if op == "block":
            if salon_calc_rider(card, eff) is not None:
                lines.append(
                    "await CreatureCmd.GainBlock(Owner.Creature, "
                    f"{salon_snapshot}, "
                    "DynamicVars.CalculatedBlock.Props, cardPlay);")
                continue
            if (spotlight_block_rider(card, eff) is not None
                    or block_calc_rider(card, eff) is not None):
                # Base game's own idiom (Mirage): resolve through the same var
                # the face reads, so preview and gain cannot drift.
                lines.append(
                    "await CreatureCmd.GainBlock(Owner.Creature, "
                    "DynamicVars.CalculatedBlock.Calculate(cardPlay.Target), "
                    "DynamicVars.CalculatedBlock.Props, cardPlay);")
                continue
            amount = ("new BlockVar(" + str(int(eff["amount"]))
                      + "m, ValueProp.Move)" if _is_sly_branch(card)
                      else "DynamicVars.Block")
            if salon_deployed:
                amount = (
                    "new BlockVar(DynamicVars.Block.BaseValue * "
                    "(salonReplacements > 0 ? 3 : 1), ValueProp.Move)")
            if spotlight_capable:
                raw = (
                    "DynamicVars.Block.BaseValue * "
                    "(salonReplacements > 0 ? 3 : 1)"
                    if salon_deployed else "DynamicVars.Block.BaseValue")
                amount = (
                    "new BlockVar(SpotlightSystem.PrintedBlock("
                    f"this, {raw}), ValueProp.Move)")
            lines.append(
                f"await CreatureCmd.GainBlock(Owner.Creature, {amount}, cardPlay);"
            )

        elif op == "draw":
            amount = (str(int(eff["amount"])) if _is_sly_branch(card)
                      else "DynamicVars.Cards.BaseValue")
            if salon_calc_rider(card, eff) is not None:
                amount = f"(int){salon_snapshot}"
            elif salon_deployed:
                amount += " * (salonReplacements > 0 ? 2 : 1)"
            lines.append(
                f"await CardPileCmd.Draw(choiceContext, {amount}, Owner);"
            )

        elif op == "damage" and eff["target"] == "self":
            # Unblockable | Unpowered so self-damage ignores our own Block and
            # Strength, matching how the base game models HP cost.
            lines.append(
                "await CreatureCmd.Damage(choiceContext, Owner.Creature, "
                "DynamicVars.HpLoss.BaseValue, "
                "ValueProp.Unblockable | ValueProp.Unpowered, this);"
            )

        elif op == "place_bomb":
            _emit_place_bomb(card, eff, lines, ctx,
                             f"(int)DynamicVars.{bomb_var(card)}.BaseValue")

        elif op == "damage":
            if calc_rider(card, eff) is not None:
                # Face/preview and hit both route through the one var.
                _emit_damage(card, eff, lines, ctx,
                             "DynamicVars.CalculatedDamage")
                continue
            if salon_calc_rider(card, eff) is not None:
                # Same var, but spent from the pre-deploy snapshot: passing
                # the var itself would make AttackCommand call Calculate()
                # after this card's own deploys had already grown the company.
                _emit_damage(card, eff, lines, ctx, salon_snapshot)
                continue
            amount_expr = (str(int(eff["amount"])) + "m"
                           if _is_sly_branch(card)
                           or eff is not damage_var_effect(card)
                           else "DynamicVars.Damage.BaseValue")
            if "bonus_vs_aura" in eff:
                aura_target = (
                    "cardPlay.Target!" if eff["target"] == "enemy"
                    else "auraTarget")
                amount_expr += (
                    f" + (AuraCmd.Find({aura_target}) != null ? "
                    f"{int(eff['bonus_vs_aura'])} : 0)")
            if "bonus_formula" in eff:
                formula = eff["bonus_formula"]
                if formula.endswith("_per_detonation_this_combat"):
                    # The Big One: flat rider on the printed number, before
                    # external buffs -- exactly the sim's `base +=`.
                    per = ('DynamicVars["BonusPer"].IntValue'
                           if bonus_per_upgrade(card)
                           else formula.partition("_per_")[0])
                    # EPOCH 2 / D2: the count is PER-PLAYER now, so the reader
                    # has to say whose. `Owner` on a CardModel is the Player
                    # (the Creature lives at Owner.Creature) -- the same
                    # distinction that bit KokomiResourceHooks. Passing the
                    # owner keeps a co-op partner's detonations out of this
                    # card's bonus.
                    amount_expr += (
                        f" + {per} * "
                        "BombPower.DetonationsThisCombat(CombatState!, Owner)")
                else:
                    n, _, rest = formula.partition("_per_")
                    per_fanfare = rest.partition("_")[0]
                    amount_expr += (
                        f" + {n} * "
                        f"(FurinaResources.Fanfare(Owner.Creature) / {per_fanfare})")
            if salon_deployed:
                amount_expr = (
                    f"({amount_expr}) * "
                    "(salonReplacements > 0 ? 3 : 1)")
            if spotlight_capable:
                amount_expr = (
                    f"SpotlightSystem.PrintedDamage(this, {amount_expr})")
            if "bonus_vs_aura" in eff and eff["target"] == "all_enemies":
                lines.append(
                    "foreach (var auraTarget in "
                    "CombatState!.HittableEnemies.ToList())\n"
                    "        {\n"
                    f"            await DamageCmd.Attack({amount_expr})\n"
                    "                .FromCard(this)\n"
                    "                .Targeting(auraTarget)\n"
                    '                .WithHitFx("vfx/vfx_attack_slash")\n'
                    "                .Execute(choiceContext);\n"
                    "        }")
            else:
                _emit_damage(card, eff, lines, ctx, amount_expr)

        elif op == "gain_spark":
            lines.append(_stmt_gain_spark(card, eff))

        elif op == "burst_energy":
            lines.append(_stmt_burst_energy(card, eff))

        elif op == "gain_charge":
            # The PREMIUM accrual (kickoff 2.1). The universal exhaust->Charge
            # funnel is the relic's, never card text, so these lines are pure
            # bonus on top and carry no identity gate of their own -- GainCharge
            # gates internally.
            lines.append(
                "KokomiResources.GainCharge(Owner.Creature, "
                f"{int(eff['amount'])});")

        elif op == "summon_kurage":
            lines.append(
                "await KurageSummon.Field(choiceContext, Owner.Creature, "
                f"{kurage_turns_expr(card, eff)}, this);")

        elif op == "conscript":
            override = eff.get("cost_override")
            lines.append(
                "await KokomiConscript.Run(choiceContext, Owner, this, "
                f"{int(eff.get('amount', 1))}, "
                f"createMode: {'true' if eff.get('mode') == 'create' else 'false'}, "
                f"costOverride: {override if override is not None else 'null'});")

        elif op == "gain_encore":
            if salon_calc_rider(card, eff) is not None:
                lines.append(
                    "FurinaResources.GainEncore(Owner.Creature, "
                    f"(int){salon_snapshot});")
                continue
            lines.append(
                _stmt_gain_encore(
                    card, eff, salon_scaled=salon_deployed))

        elif op == "spend_encore":
            lines.append(
                "await FurinaResources.SpendEncoreOrHp("
                f"choiceContext, Owner.Creature, {int(eff['amount'])}, this);")

        elif op == "raise_fanfare_cap":
            lines.append(
                "FurinaResources.RaiseFanfareCap("
                "Owner.Creature, DynamicVars[\"FanfareCap\"].IntValue);")

        elif op == "gain_fanfare_floor":
            lines.append(
                "FurinaResources.GainFanfareFloor("
                "Owner.Creature, DynamicVars[\"FanfareFloor\"].IntValue);")

        elif op == "heal":
            lines.append(
                "await CreatureCmd.Heal(Owner.Creature, "
                "DynamicVars[\"Heal\"].BaseValue);")

        elif op == "apply_power":
            cls = APPLY_POWERS[eff["power"]][0]
            amount = (
                'DynamicVars["PowerAmount"].IntValue'
                if eff is power_upgrade_effect(card)
                else str(int(eff["amount"]))
            )
            if salon_calc_rider(card, eff) is not None:
                amount = f"(int){salon_snapshot}"
            elif salon_deployed and eff["power"] != "salon_member":
                amount = f"{amount} * (salonReplacements > 0 ? 2 : 1)"
            # Stack caps are enforced by the power's own
            # TryModifyPowerAmountReceived (the sim clamps at apply too), so
            # the call site stays a plain Apply.
            if eff["power"] == "salon_member":
                # Salon v2 (rework plan §1): deploys are member-TYPED. The
                # C# enum mirrors tier0's C.SALON_MEMBERS keys.
                # A11: `random` emits a null, which Deploy resolves per
                # iteration off the shared combat RNG stream. The sim rolls
                # per iteration too, so a multi-deploy card fields a mixed
                # stage in both engines.
                member = SALON_MEMBER_CS[eff.get("member", "crabaletta")]
                lines.append(
                    "salonReplacements += await SalonMemberPower.Deploy("
                    f"choiceContext, Owner.Creature, {amount}, this, "
                    f"{member});")
                salon_deployed = True
            elif eff["power"] in ENEMY_APPLY_POWERS:
                # tier0 _op_apply_power -> _pick_targets: chosen enemy or
                # every living enemy. Native debuff classes; applier is us.
                if eff["target"] == "enemy":
                    _target_guard(lines, ctx)
                    lines.append(
                        f"await PowerCmd.Apply<{cls}>(choiceContext, cardPlay.Target, "
                        f"{amount}, applier: Owner.Creature, cardSource: this);"
                    )
                elif eff["target"] == "random_enemy":
                    # tier0 _pick_targets: ONE enemy, rolled. Same shape the
                    # aura emitter uses. Emitted separately because the
                    # all-enemies branch below used to swallow this target and
                    # debuff the whole room off a one-target sheet line.
                    lines.append(NEWLINE.join([
                        "{",
                        "            var debuffCandidates = CombatState!"
                        ".HittableEnemies.ToList();",
                        "            if (debuffCandidates.Count > 0)",
                        "            {",
                        "                var debuffTarget = Owner.RunState"
                        ".Rng.CombatTargets.NextItem(debuffCandidates);",
                        "                if (debuffTarget != null)",
                        "                {",
                        f"                    await PowerCmd.Apply<{cls}>("
                        f"choiceContext, debuffTarget, {amount}, "
                        "applier: Owner.Creature, cardSource: this);",
                        "                }",
                        "            }",
                        "        }",
                    ]))
                else:  # all_enemies (snapshot: an apply cannot kill, but stay
                    # consistent with every other all-enemies loop we emit)
                    lines.append(
                        "foreach (var debuffTarget in CombatState!.HittableEnemies.ToList())\n"
                        "        {\n"
                        f"            await PowerCmd.Apply<{cls}>(choiceContext, debuffTarget, "
                        f"{amount}, applier: Owner.Creature, cardSource: this);\n"
                        "        }"
                    )
            else:
                lines.append(
                    f"await PowerCmd.Apply<{cls}>(choiceContext, Owner.Creature, "
                    f"{amount}, applier: Owner.Creature, cardSource: this);"
                )

        elif op == "detonate":
            # tier0 _op_detonate: only enemies WITH bombs detonate (DetonateOn
            # returns 0 on a bombless target); bonus rides each bomb inside
            # the same pre-amplification sum as bomb_damage_up. The count
            # feeds chance_bomb_per_detonation when the card carries one.
            bonus = int(eff.get("bonus", 0))
            bonus_arg = (
                ', DynamicVars["Bonus"].IntValue' if bonus_upgrade(card)
                else (f", {bonus}" if bonus else "")
            )
            prefix = (
                "var detonations = "
                if any(e.get("op") == "chance_bomb_per_detonation"
                       for e in card["effects"])
                else ""
            )
            if eff["target"] == "enemy":
                _target_guard(lines, ctx)
                lines.append(
                    f"{prefix}await BombPower.DetonateOn(choiceContext, "
                    f"cardPlay.Target{bonus_arg});"
                )
            else:  # all_enemies
                lines.append(
                    f"{prefix}await BombPower.DetonateAll(choiceContext, "
                    f"CombatState!.HittableEnemies.ToList(){bonus_arg});"
                )

        elif op == "modify_bombs":
            # tier0 _op_modify_bombs: every live bomb (or only this round's --
            # the stamp mirrors Bomb.turn_placed) gains the bonus. Effect
            # order is preserved by this loop, so Chain Fuse's own bomb,
            # placed by the NEXT effect, is not buffed -- same as the sim.
            this_round = "true" if eff.get("scope", "all") == "placed_this_turn" else "false"
            bonus_expr = (
                'DynamicVars["Bonus"].IntValue' if bonus_upgrade(card)
                else str(int(eff["bonus"]))
            )
            lines.append(
                f"BombPower.ModifyAll(CombatState!.HittableEnemies, {bonus_expr}, "
                f"placedThisRoundOnly: {this_round}, CombatState!.RoundNumber);"
            )

        elif op == "move_bombs":
            # tier0 _op_move_bombs: gather ALL bombs from other enemies onto
            # the chosen target, +bonus each; stamps travel with the charges.
            bonus_expr = (
                'DynamicVars["Bonus"].IntValue' if bonus_upgrade(card)
                else str(int(eff.get("bonus", 0)))
            )
            _target_guard(lines, ctx)
            lines.append(
                f"await BombPower.MoveAllTo(choiceContext, cardPlay.Target, "
                f"CombatState!.HittableEnemies, {bonus_expr}, Owner.Creature, this);"
            )

        elif op == "chance_bomb_per_detonation":
            # tier0: per detonation this card caused, roll < chance -> fresh
            # bomb on a random living enemy. `detonations` is the DetonateOn/
            # DetonateAll return captured above (blocked_reason guarantees
            # the preceding detonate). Roll and pick both ride CombatTargets,
            # the established in-combat stream.
            chance_expr = (
                'DynamicVars["Chance"].IntValue / 100f' if chance_upgrade(card)
                else f'{float(eff["chance"])}f'
            )
            lines.append(
                "for (var i = 0; i < detonations; i++)\n"
                "        {\n"
                f"            if (Owner.RunState.Rng.CombatTargets.NextFloat() >= {chance_expr}) continue;\n"
                "            var candidates = CombatState!.HittableEnemies.ToList();\n"
                "            if (candidates.Count == 0) break;\n"
                "            var bombTarget = Owner.RunState.Rng.CombatTargets.NextItem(candidates);\n"
                "            if (bombTarget == null) break;\n"
                f'            await BombPower.Place(choiceContext, bombTarget, {int(eff["bomb_damage"])}, '
                "Owner.Creature, this);\n"
                "        }"
            )

        elif op == "discard":
            # Random discard, kit-exempt pool (tier0 _op_discard: re-pool per
            # pick, stop when empty). CombatTargets is the established rng
            # stream for in-combat random picks (bomb targeting idiom).
            # G6: an upgradeable count reads the VAR, so the loop bound and
            # the printed face cannot disagree after an upgrade -- the same
            # preview-truth rule the Furina legibility sprint established.
            n = ('DynamicVars["Discards"].IntValue'
                 if plain_discard_upgrade(card) else int(eff.get("amount", 1)))
            lines.append(
                f"for (var i = 0; i < {n}; i++)\n"
                "        {\n"
                "            var pool = CardPile.Get(PileType.Hand, Owner)?"
                ".Cards.Where(KitGrant.NotKitCard).ToList();\n"
                "            if (pool == null || pool.Count == 0) break;\n"
                "            var victim = Owner.RunState.Rng.CombatTargets.NextItem(pool);\n"
                "            if (victim == null) break;\n"
                "            await CardCmd.Discard(choiceContext, victim);\n"
                "        }"
            )

        elif op == "discard_for_sparks":
            # R36: forced player-chosen discard of N (auto-selects-all on a
            # short hand -- FromHand's own rule), kit-exempt filter; then
            # Sparks priced by the cards ACTUALLY discarded, capped at M.
            # Empty eligible hand -> empty selection -> no Spark.
            if discard_upgrade(card) != (0, 0):
                n = 'DynamicVars["Discards"].IntValue'
                m = 'DynamicVars["Sparks"].IntValue'
            else:
                n = str(int(eff["amount"]))
                m = str(int(eff["sparks"]))
            lines.append(
                "var picked = (await CardSelectCmd.FromHandForDiscard(\n"
                "            choiceContext, Owner,\n"
                "            new CardSelectorPrefs(CardSelectorPrefs.DiscardSelectionPrompt, "
                f"{n}),\n"
                "            KitGrant.NotKitCard, this)).ToList();\n"
                "        await CardCmd.Discard(choiceContext, picked);\n"
                f"        var sparkGain = Math.Min({m}, picked.Count);\n"
                "        if (sparkGain > 0)\n"
                "        {\n"
                "            await SparkPower.Gain(choiceContext, Owner.Creature, sparkGain, this);\n"
                "        }"
            )

        elif op == "cost_mod":
            # tier0 _op_cost_mod: companion_cost_delta_this_turn += delta.
            # Amount is the REDUCTION (positive; PowerModel amounts are
            # non-negative by default).
            lines.append(
                f"await PowerCmd.Apply<CompanionCostThisTurnPower>(choiceContext, "
                f'Owner.Creature, {-int(eff["delta"])}, '
                "applier: Owner.Creature, cardSource: this);"
            )

        elif op == "copy_companion_in_hand":
            # tier0: random companion in hand, fresh copy to hand. The
            # upgrade's copy_cost_override is a play-time IsUpgraded read
            # (patched_dress precedent -- codegen cannot rewrite OnPlay from
            # OnUpgrade).
            cost_line = ""
            if "cost_override" in eff:
                cost_line = (
                    f"                    copyToken.EnergyCost.SetThisCombat({int(eff['cost_override'])});\n"
                )
            elif "copy_cost_override" in upgrade_plan(card)[0]:
                override = int(upgrade_plan(card)[0]["copy_cost_override"])
                cost_line = (
                    "                    if (IsUpgraded)\n"
                    "                    {\n"
                    f"                        copyToken.EnergyCost.SetThisCombat({override});\n"
                    "                    }\n"
                )
            lines.append(
                "{\n"
                "            var companionsInHand = CardPile.Get(PileType.Hand, Owner)?\n"
                "                .Cards.Where(c => c is ICompanionCard).ToList();\n"
                "            if (companionsInHand != null && companionsInHand.Count > 0)\n"
                "            {\n"
                "                var pickedCompanion = Owner.RunState.Rng.CombatTargets.NextItem(companionsInHand);\n"
                "                if (pickedCompanion != null)\n"
                "                {\n"
                "                    var copyToken = CombatState!.CreateCard(\n"
                "                        ModelDb.GetById<CardModel>(pickedCompanion.Id), Owner);\n"
                + cost_line
                + "                    await CardPileCmd.AddGeneratedCardToCombat(copyToken, PileType.Hand, Owner);\n"
                "                }\n"
                "            }\n"
                "        }"
            )

        elif op == "copy_spotlighted_in_hand":
            cost_line = ""
            if "cost_override" in eff:
                cost_line = (
                    "                    spotlightCopy.EnergyCost.SetThisCombat("
                    f"{int(eff['cost_override'])});\n")
            elif "copy_cost_override" in upgrade_plan(card)[0]:
                override = int(
                    upgrade_plan(card)[0]["copy_cost_override"])
                cost_line = (
                    "                    if (IsUpgraded)\n"
                    "                    {\n"
                    "                        spotlightCopy.EnergyCost"
                    f".SetThisCombat({override});\n"
                    "                    }\n")
            lines.append(
                "{\n"
                "            var spotlightTargets = CardPile.Get("
                "PileType.Hand, Owner)?.Cards\n"
                "                .Where(SpotlightSystem.IsSpotlighted)"
                ".ToList();\n"
                "            if (spotlightTargets != null "
                "&& spotlightTargets.Count > 0)\n"
                "            {\n"
                "                var selectedSpotlight = Owner.RunState.Rng"
                ".CombatTargets.NextItem(spotlightTargets);\n"
                "                if (selectedSpotlight != null)\n"
                "                {\n"
                "                    var spotlightCopy = CombatState!"
                ".CreateCard(\n"
                "                        ModelDb.GetById<CardModel>("
                "selectedSpotlight.Id), Owner);\n"
                + cost_line
                + "                    await CardPileCmd"
                ".AddGeneratedCardToCombat(\n"
                "                        spotlightCopy, PileType.Hand, "
                "Owner);\n"
                "                }\n"
                "            }\n"
                "        }")

        elif op == "replay_next_companion":
            lines.append(
                f"await PowerCmd.Apply<ReplayNextCompanionPower>(choiceContext, "
                f'Owner.Creature, {int(eff.get("times", 1))}, '
                "applier: Owner.Creature, cardSource: this);"
            )

        elif op == "copy_companions_played_this_combat":
            # tier0: unique companions played this combat, in first-play
            # order, fresh tokens (cost_override) to hand.
            override_line = ""
            if "cost_override" in eff:
                override_line = (
                    f"            playedToken.EnergyCost.SetThisCombat({int(eff['cost_override'])});\n"
                )
            # G-B1: owner-scoped. The tracker is combat-wide storage, so the
            # query has to name whose plays it wants -- unfiltered, this card
            # copied the co-op partner's companions.
            lines.append(
                "foreach (var companionId in CompanionPlays.PlayedThisCombat(CombatState!, Owner))\n"
                "        {\n"
                "            var playedToken = CombatState!.CreateCard(\n"
                "                ModelDb.GetById<CardModel>(companionId), Owner);\n"
                + override_line
                + "            await CardPileCmd.AddGeneratedCardToCombat(playedToken, PileType.Hand, Owner);\n"
                "        }"
            )

        elif op in ("apply_aura", "swirl"):
            # tier0 _op_apply_aura / _op_swirl: resolve_hit with 0 damage --
            # ElementalHit.ApplyOnly is exactly that (apply / refresh /
            # consume+react, no damage call). Swirl IS "trigger anemo".
            element = (ELEMENT_CS[eff["element"]] if op == "apply_aura"
                       else "Element.Anemo")
            tgt = eff.get("target", "enemy")
            aura_lines: list[str] = []
            if tgt == "enemy":
                _target_guard(aura_lines, ctx)
                aura_lines.append(
                    f"await ElementalHit.ApplyOnly(choiceContext, cardPlay.Target, "
                    f"{element}, Owner.Creature);"
                )
            elif tgt == "all_enemies":
                aura_lines.append(
                    "foreach (var auraTarget in CombatState!.HittableEnemies.ToList())\n"
                    "        {\n"
                    f"            await ElementalHit.ApplyOnly(choiceContext, auraTarget, "
                    f"{element}, Owner.Creature);\n"
                    "        }"
                )
            else:  # random_enemy
                aura_lines.append(
                    "{\n"
                    "            var auraCandidates = CombatState!.HittableEnemies.ToList();\n"
                    "            if (auraCandidates.Count > 0)\n"
                    "            {\n"
                    "                var auraTarget = Owner.RunState.Rng.CombatTargets.NextItem(auraCandidates);\n"
                    "                if (auraTarget != null)\n"
                    "                {\n"
                    f"                    await ElementalHit.ApplyOnly(choiceContext, auraTarget, "
                    f"{element}, Owner.Creature);\n"
                    "                }\n"
                    "            }\n"
                    "        }"
                )
            if salon_deployed:
                body = "\n".join(
                    "            " + statement.replace("\n", "\n    ")
                    for statement in aura_lines)
                lines.append(
                    "for (var salonRepeat = 0; salonRepeat < "
                    "(salonReplacements > 0 ? 2 : 1); salonRepeat++)\n"
                    "        {\n"
                    f"{body}\n"
                    "        }")
            else:
                lines.extend(aura_lines)

        elif op == "refresh_all_auras":
            # tier0 _op_refresh_all_auras: every living enemy holding an aura
            # has its remaining duration set back to full. The helper reuses
            # AuraPower's own same-element refresh path, so the value it
            # refreshes TO is defined once.
            lines.append(
                "await CurtainCallHooks.RefreshAllAuras("
                "choiceContext, Owner.Creature, this);"
            )

        elif op == "grow_damage":
            # tier0 _op_grow_damage (Rampage): permanently raise THIS card
            # instance's printed damage. Targets whichever var actually holds
            # the printed number -- CalculationBase on a card carrying a
            # rider, Damage otherwise -- which is the same var the upgrade
            # bumps, so growth and upgrade compound instead of one silently
            # overwriting the other. ResetToBase + the display invalidation
            # are BombPower.SyncDisplay's idiom: without them the card resolves
            # overwriting the other.
            #
            # A bare `BaseValue +=` is the whole operation: DynamicVar's
            # BaseValue setter calls ResetToBase() itself, so the enchanted
            # and preview values follow without a second statement. NOT
            # UpgradeValueBy -- that sets WasJustUpgraded and would paint the
            # number as freshly upgraded every time the card grows.
            grow_var = ('DynamicVars.CalculationBase'
                        if any(calc_rider(card, e) is not None
                               for e in card.get("effects", []))
                        else "DynamicVars.Damage")
            lines.append(f"{grow_var}.BaseValue += {int(eff['amount'])}m;")

        elif op == "buff_next_attack":
            # tier0 _op_buff_next_attack -> next_attack_up, consumed by the
            # next attack card (NextAttackUpPower's AfterCardPlayed).
            amount = ('DynamicVars["PowerAmount"].IntValue'
                      if eff is power_upgrade_effect(card)
                      else str(int(eff["amount"])))
            lines.append(
                f"await PowerCmd.Apply<NextAttackUpPower>(choiceContext, "
                f"Owner.Creature, {amount}, "
                "applier: Owner.Creature, cardSource: this);"
            )

        elif op == "block_next_turn":
            # tier0 _op_block_next_turn: a power the sim POPS at the next
            # player turn start, granting the Block after that turn's reset.
            amount = str(int(eff["amount"]))
            if spotlight_capable:
                amount = f"(int)SpotlightSystem.PrintedBlock(this, {amount})"
            lines.append(
                f"await PowerCmd.Apply<BlockNextTurnPower>(choiceContext, "
                f"Owner.Creature, {amount}, "
                "applier: Owner.Creature, cardSource: this);"
            )

        elif op == "energy":
            # tier0 _op_energy: flat gain, no cap (the game clamps nothing
            # either -- PlayerCmd.GainEnergy is the base-game call).
            # An upgradeable amount reads the var. This is the TOP-LEVEL
            # emitter; there is a second one for branch bodies, and the fix
            # had to land on both -- patching only the other one produced a
            # card whose FACE said "Gain {Energy:diff()}" while its play still
            # granted the base, which is the same preview-vs-effect drift in a
            # new place.
            amount = ('DynamicVars["Energy"].IntValue' if energy_upgrade(card)
                      else int(eff["amount"]))
            lines.append(f'await PlayerCmd.GainEnergy({amount}, Owner);')

        elif op == "scry_discard":
            # tier0 _op_scry_discard looks at the top N and discards the
            # "worst" via the shared pilot heuristic -- which is the sim's
            # stand-in for PLAYER CHOICE (R36 precedent: Crackle's heuristic
            # discard landed as FromHandForDiscard). Top of pile is index 0
            # (CardPile.MoveToTopInternal inserts at 0), so Take(N) is the
            # sim's draw_pile[:n]. The unpicked card stays in place.
            n = int(eff["amount"])
            lines.append(
                "{\n"
                f"            var top = CardPile.Get(PileType.Draw, Owner)?.Cards.Take({n}).ToList();\n"
                "            if (top != null && top.Count > 0)\n"
                "            {\n"
                "                var scryPick = (await CardSelectCmd.FromSimpleGrid(\n"
                "                    choiceContext, top, Owner,\n"
                "                    new CardSelectorPrefs(CardSelectorPrefs.DiscardSelectionPrompt, 1))).ToList();\n"
                "                await CardCmd.Discard(choiceContext, scryPick);\n"
                "            }\n"
                "        }"
            )

        elif op == "exhaust_from" and eff.get("select") == "chosen":
            # Kokomi: the player chooses. Kit cards stay exempt (v1.9 -- the
            # Burst is never fodder), the same filter the discard ops ride.
            # Every exhaust pays Charge through the relic funnel, so this op
            # is her engine's throttle and the CHOICE is the gameplay -- a
            # random pick would not be a smaller version of this card, it
            # would be a different card.
            n = ('DynamicVars["Exhausts"].IntValue'
                 if exhaust_upgrade(card) else str(int(eff.get("amount", 1))))
            lines.append(NEWLINE.join([
                "{",
                "            var toExhaust = (await CardSelectCmd.FromHand(",
                "                choiceContext, Owner,",
                "                new CardSelectorPrefs(",
                "                    CardSelectorPrefs.ExhaustSelectionPrompt, "
                f"{n}),",
                "                KitGrant.NotKitCard, this)).ToList();",
                "            foreach (var victim in toExhaust)",
                "            {",
                "                await CardCmd.Exhaust(choiceContext, victim);",
                "            }",
                "        }",
            ]))

        elif op == "exhaust_from":
            # tier0 _op_exhaust_from with filter status: RANDOM victim from
            # the hand's Status cards (not chosen -- the sim rolls rng).
            lines.append(
                "{\n"
                "            var statusCards = CardPile.Get(PileType.Hand, Owner)?\n"
                "                .Cards.Where(c => c.Rarity == CardRarity.Status).ToList();\n"
                "            if (statusCards != null && statusCards.Count > 0)\n"
                "            {\n"
                "                var victim = Owner.RunState.Rng.CombatTargets.NextItem(statusCards);\n"
                "                if (victim != null)\n"
                "                {\n"
                "                    await CardCmd.Exhaust(choiceContext, victim);\n"
                "                }\n"
                "            }\n"
                "        }"
            )

        elif op == "add_card":
            zone = eff.get("zone") or eff.get("to", "discard")
            pile = "PileType.Hand" if zone == "hand" else "PileType.Discard"
            n = int(eff.get("amount", 1))
            if "pool" in eff:
                # Pool resolved from the sheet at generation time; picks are
                # WITH replacement (tier0: rng.choice per pick), each pick a
                # fresh instance. AddGeneratedCardToCombat's own full-hand
                # rule (redirect to discard) is the sim's _add_token rule.
                members = _pool_members(eff["pool"])
                count = ('DynamicVars["Stash"].IntValue'
                         if stash_upgrade(card) else str(n))
                model_list = ",\n".join(
                    f"                ModelDb.Card<{pascal(m['id'])}>()"
                    for m in members)
                cost_line = ""
                if "cost_override" in eff:
                    # tier0 token.cost stays overridden for the token's whole
                    # combat lifetime -> SetThisCombat.
                    cost_line = (f"                token.EnergyCost.SetThisCombat("
                                 f'{int(eff["cost_override"])});\n')
                lines.append(
                    "{\n"
                    "            var stashPool = new List<CardModel>\n"
                    "            {\n"
                    f"{model_list}\n"
                    "            };\n"
                    f"            for (var i = 0; i < {count}; i++)\n"
                    "            {\n"
                    "                var canonical = Owner.RunState.Rng.CombatTargets.NextItem(stashPool);\n"
                    "                if (canonical == null) break;\n"
                    "                var token = CombatState!.CreateCard(canonical, Owner);\n"
                    f"{cost_line}"
                    f"                await CardPileCmd.AddGeneratedCardToCombat(token, {pile}, Owner);\n"
                    "            }\n"
                    "        }"
                )
            else:
                cid = eff.get("card_id") or eff.get("card")
                cls = ADD_CARD_CLASSES[cid]
                token_lines = (
                    f"            var token = CombatState!.CreateCard<{cls}>(Owner);\n"
                    f"            await CardPileCmd.AddGeneratedCardToCombat(token, {pile}, Owner);\n"
                )
                body = token_lines if n == 1 else (
                    f"            for (var i = 0; i < {n}; i++)\n"
                    "            {\n"
                    + token_lines.replace("            ", "                ")
                    + "            }\n"
                )
                lines.append("{\n" + body + "        }")

        elif op == "generate_guest_star":
            override = eff.get("cost_override")
            ruled_override = upgrade_plan(card)[0].get(
                "generate_cost_override")
            if override is not None:
                override_expr = str(int(override))
            elif ruled_override is not None:
                override_expr = (
                    f"IsUpgraded ? {int(ruled_override)} : (int?)null")
            else:
                override_expr = "null"
            lines.append(
                "await GuestStarGenerator.Generate("
                f"choiceContext, this, \"{eff['rarity']}\", "
                f"{int(eff.get('amount', 1))}, {override_expr});")

        elif op == "conditional":
            then = eff.get("then", [])
            if any(e.get("op") == "repeat_this" for e in then):
                # Evaluated at the conditional's position (sim: the predicate
                # reads counters as of this point in the effect list); the
                # replay itself lands after the list (repeat tail below).
                times = int(then[0].get("times", 1))
                lines.append(
                    f"var repeatTimes = ({predicate_cs(eff['if'])}) ? {times} : 0;"
                )
            else:
                pred = predicate_cs(eff["if"])
                if condition_upgrade(card):
                    # condition: unconditional (tier0 hoists the then-branch
                    # on upgrade) -- the upgraded card runs it always.
                    pred = f"IsUpgraded || {pred}"
                cb_state = {"pending": conditional_bonus_upgrade(card) > 0}
                then_lines: list[str] = []
                for e in then:
                    _emit_branch_op(
                        card, e, then_lines, ctx, True, cb_state,
                        spotlight_capable)
                else_lines: list[str] = []
                for e in eff.get("else", []):
                    _emit_branch_op(
                        card, e, else_lines, ctx, False, cb_state,
                        spotlight_capable)
                lines.append(_conditional_block(pred, then_lines, else_lines))

    # Structural upgrade append (tier0 upgrades.py: card.effects.append).
    # It resolves after every base effect and before the repeat tail.
    if added_draw_upgrade(card):
        lines.append(
            "if (IsUpgraded)\n"
            "        {\n"
            "            await CardPileCmd.Draw(choiceContext, DynamicVars.Cards.BaseValue, Owner);\n"
            "        }"
        )
    if added_encore_upgrade(card):
        amount = str(added_encore_upgrade(card))
        if salon_deploy_present:
            amount += " * (salonReplacements > 0 ? 2 : 1)"
        lines.append(
            "if (IsUpgraded)\n"
            "        {\n"
            "            FurinaResources.GainEncore("
            f"Owner.Creature, {amount});\n"
            "        }"
        )

    # Repeat tail (sim resolve_card): a repeat-conditional re-resolves the
    # effect list minus the repeat machinery, `times` more times. The
    # replayed ops are REPEAT_SAFE_OPS only (blocked_reason), so the block
    # declares no method-scope locals twice.
    rep = next((e for e in card["effects"] if e.get("op") == "conditional"
                and any(x.get("op") == "repeat_this"
                        for x in e.get("then", []))), None)
    if rep is not None:
        body: list[str] = []
        for eff in card["effects"]:
            if eff is rep:
                continue
            op = eff["op"]
            if op == "damage":
                _emit_damage(card, eff, body, ctx, "DynamicVars.Damage.BaseValue")
            elif op == "block":
                body.append(
                    "await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block, cardPlay);"
                )
            elif op == "draw":
                body.append(
                    "await CardPileCmd.Draw(choiceContext, DynamicVars.Cards.BaseValue, Owner);"
                )
            elif op == "gain_spark":
                body.append(_stmt_gain_spark(card, eff))
            elif op == "burst_energy":
                body.append(_stmt_burst_energy(card, eff))
        lines.append(
            "for (var r = 0; r < repeatTimes; r++)\n        {\n"
            + "\n".join("            " + s.replace("\n", "\n    ") for s in body)
            + "\n        }"
        )

    return lines


def _branch_text(card: dict, branch: list[dict], in_then: bool) -> str:
    """Card text for a conditional branch: literal numbers unless a ruled
    delta claims the var (mirrors _emit_branch_op's amount policy)."""
    bits = []
    cb_pending = in_then and conditional_bonus_upgrade(card) > 0
    for e in branch:
        op = e["op"]
        if op == "damage":
            tgt = {"all_enemies": " to ALL enemies",
                   "random_enemy": " to a random enemy",
                   "random_enemies": " to a random enemy"}.get(e["target"], "")
            if cb_pending:
                cb_pending = False
                bits.append(f"deal {{ExtraDamage:diff()}} damage{tgt}")
            else:
                bits.append(f'deal {int(e["amount"])} damage{tgt}')
        elif op == "block":
            bits.append(f'gain {int(e["amount"])} [gold]Block[/gold]')
        elif op == "draw":
            if branch_draw_upgrade(card):
                then_var, else_var = branch_draw_vars(card)
                var = then_var if in_then else else_var
                bits.append(
                    f"draw {{{var}:diff()}} card{{{var}:plural:|s}}")
            else:
                n = int(e["amount"])
                bits.append("draw 1 card" if n == 1 else f"draw {n} cards")
        elif op == "gain_spark":
            n = int(e["amount"])
            bits.append("gain 1 [gold]Spark[/gold]" if n == 1
                        else f"gain {n} [gold]Sparks[/gold]")
        elif op == "burst_energy":
            bits.append(f'gain {int(e["amount"])} [gold]Burst Energy[/gold]')
        elif op == "gain_charge":
            bits.append(f'gain {int(e["amount"])} [gold]Charge[/gold]')
        elif op == "summon_kurage":
            bits.append("summon [gold]Bake-Kurage[/gold]")
        elif op == "conscript":
            bits.append(_conscript_phrase(e))
        elif op == "gain_encore":
            base = int(e["amount"])
            delta = encore_upgrade(card)
            amount = (
                f"{{IfUpgraded:show:{base + delta}|{base}}}"
                if delta else str(base))
            bits.append(f"gain {amount} [gold]Encore[/gold]")
        elif op == "energy":
            bits.append(f"gain {int(e['amount'])} Energy")
        elif op == "place_bomb":
            n, d = e["amount"], int(e["bomb_damage"])
            if n == 1:
                where = "" if e["target"] == "enemy" else " on a random enemy"
                bits.append(f"place a [gold]Bomb[/gold]{where} dealing {d} damage")
            else:
                where = "" if e["target"] == "enemy" else " on random enemies"
                bits.append(
                    f"place {n} [gold]Bombs[/gold]{where}, each dealing {d} damage")
        elif op == "buff_next_attack":
            # Literal: POWER_UPGRADE_KEYS deltas bind to the first TOP-LEVEL
            # effect, so a branch rider never renders a var.
            bits.append(
                f'your next Attack deals {int(e["amount"])} more damage')
        else:
            # A branch op with no text arm renders an EMPTY clause -- which is
            # how Chevreuse first generated "If a reaction triggered: ."
            # BRANCH_OPS and this table must move together.
            raise SystemExit(
                f"gen_klee_cards: {card['id']}: branch op '{op}' is in "
                "BRANCH_OPS but has no _branch_text arm -- it would render an "
                "empty clause.")
    return " and ".join(bits) + "."


def build_description(card: dict) -> str:
    """
    Card text. Syntax is copied from base-game strings observed at runtime:
    single-braced SmartFormat placeholders, :diff() for the upgrade delta, and
    [gold] for keyword highlight.
    """
    parts = []
    deltas = upgrade_plan(card)[0]
    for field, label in (("encore_cost", "Encore"),
                         ("fanfare_cost", "Fanfare")):
        base_cost = int(card.get(field, 0))
        if not base_cost:
            continue
        delta = int(deltas.get(field, 0))
        rendered = (
            f"{{IfUpgraded:show:{max(0, base_cost + delta)}|{base_cost}}}"
            if delta else str(base_cost))
        parts.append(f"Spend {rendered} [gold]{label}[/gold].")
    for eff in card["effects"]:
        op = eff["op"]

        if op == "block":
            if _is_sly_branch(card):
                parts.append(
                    f'Gain {int(eff["amount"])} [gold]Block[/gold].')
                continue
            tok = ("CalculatedBlock"
                   if spotlight_block_rider(card, eff) is not None
                   or salon_calc_rider(card, eff) is not None
                   or block_calc_rider(card, eff) is not None else "Block")
            parts.append(f"Gain {{{tok}:diff()}} [gold]Block[/gold].")
            # The L-C bargain both ways: a CONVERTED rider's arithmetic moves
            # to the hover tip, but the face must still declare that the card
            # scales, or it reads as a flat number on the reward screen -- the
            # exact misread B1 shipped. The damage path has always emitted
            # this marker; the block path did not, so B1's fix traded a silent
            # drop for a silent number. Fixed here (A13).
            if block_calc_rider(card, eff) is not None:
                formula = eff.get("bonus_formula", "")
                stat = ("Salon" if formula.endswith("_per_salon_member")
                        else formula.rpartition("_")[2].title())
                parts.append(f"Scales with [gold]{stat}[/gold].")

        elif op == "block_next_turn":
            # Literal: the `block` delta binds to the plain block op (sheet:
            # "now-block 3->5; next-turn block stays 3").
            parts.append(
                f'At the start of your next turn, gain {int(eff["amount"])} '
                "[gold]Block[/gold].")

        elif op == "draw":
            # {Cards:plural:|s} pluralizes off the LIVE value, so "Draw 1
            # card" correctly becomes "Draw 2 cards" after upgrade. This is
            # the token BaseLib's SimpleLoc pipeline generates for "card(s)"
            # in #-prefixed strings; we emit runtime form directly.
            if _is_sly_branch(card):
                n = int(eff["amount"])
                parts.append("Draw 1 card." if n == 1 else f"Draw {n} cards.")
                continue
            v = ("DrawCards" if salon_calc_rider(card, eff) is not None
                 else "Cards")
            parts.append(f"Draw {{{v}:diff()}} card{{{v}:plural:|s}}.")

        elif op == "place_bomb":
            var = bomb_var(card)
            n = eff["amount"]
            if isinstance(n, str):
                # X_plus_N renders "X+N"; with a ruled bombs delta the +N
                # rides the Bombs var so the upgrade shows.
                if bombs_upgrade(card):
                    n = "X+{Bombs:diff()}"
                else:
                    n = f'X+{int(n[len("X_plus_"):])}' if n != "X" else "X"
            where = "" if eff["target"] == "enemy" else " on random enemies"
            if n == 1:
                where = "" if eff["target"] == "enemy" else " on a random enemy"
                parts.append(
                    f"Place a [gold]Bomb[/gold]{where} dealing {{{var}:diff()}} damage."
                )
            else:
                parts.append(
                    f"Place {n} [gold]Bombs[/gold]{where}, each dealing "
                    f"{{{var}:diff()}} damage."
                )

        elif op == "damage" and eff["target"] == "self":
            parts.append("Lose {HpLoss} HP.")

        elif op == "damage":
            times = eff.get("times", 1)
            target = eff["target"]
            if "times_formula" in eff:        # 2_plus_sparks
                parts.append(
                    "Deal {Damage:diff()} damage to a random enemy, "
                    "2+[gold]Sparks[/gold] times.")
                continue
            if times in RUNTIME_TIMES:        # times: a live count
                suffix = RUNTIME_TIMES_TEXT[times]
                times = 2                     # phrasing: plural targets
            elif isinstance(times, str):      # times: "X"
                suffix = " X times"
                times = 2                     # phrasing: plural targets
            elif eff is times_var_effect(card):
                # Ruled `times: +N`: the count must render from the var so the
                # upgrade shows green, which also means no "twice"/"three
                # times" word form -- the diff token needs a numeral.
                suffix = " {Times:diff()} times"
                times = 2                     # phrasing: plural targets
            else:
                suffix = {1: "", 2: " twice", 3: " three times", 4: " four times"}.get(
                    times, f" {times} times"
                )
            tok = ("CalculatedDamage"
                   if calc_rider(card, eff) is not None
                   or salon_calc_rider(card, eff) is not None else "Damage")
            if _is_sly_branch(card):
                tok = None                    # literal, see _sly_view
            if tok == "Damage" and eff is not damage_var_effect(card):
                tok = None                    # see damage_var_effect
            if tok is None:
                amount_txt = str(int(eff["amount"]))
                where = {"enemy": "",
                         "all_enemies": " to ALL enemies"}.get(
                             target, " to a random enemy")
                parts.append(f"Deal {amount_txt} damage{where}{suffix}.")
                continue
            if target == "enemy":
                parts.append(f"Deal {{{tok}:diff()}} damage{suffix}.")
            elif target == "all_enemies":
                parts.append(f"Deal {{{tok}:diff()}} damage to ALL enemies{suffix}.")
            else:
                plural = "random enemies" if times > 1 else "a random enemy"
                parts.append(f"Deal {{{tok}:diff()}} damage to {plural}{suffix}.")
            # Track L-C: a rider whose arithmetic now lands inside the printed
            # number keeps only a short marker here; the rate (and what it is
            # worth right now) moves to the hover tip. A rider that is NOT
            # converted keeps its full sentence -- its number is not on the
            # face, so the text is the only place the player can read it.
            rehomed = calc_rider(card, eff) is not None
            if exhaust_pile_calc_rider(card, eff) is not None:
                # The number is already honest (it renders through the
                # CalculatedVar); this sentence says WHY it moves. Without it
                # the card is a damage number that changes for no stated
                # reason, which is the exact confusion Track C exists to stop.
                parts.append(
                    "Scales with the number of cards [gold]Exhausted[/gold].")
            if "bonus_formula" in eff:
                formula = eff["bonus_formula"]
                if formula.endswith("_per_detonation_this_combat"):
                    per = ("{BonusPer:diff()}" if bonus_per_upgrade(card)
                           else formula.partition("_per_")[0])
                    parts.append(
                        f"+{per} damage per [gold]Bomb[/gold] detonated this combat.")
                elif rehomed:
                    # Name the RESOURCE the formula actually reads. This said
                    # "Fanfare" unconditionally, which put another character's
                    # mechanic on the face of every Kokomi Charge reader --
                    # including her signature one -- while the arithmetic
                    # underneath was correct. A face that names the wrong stat
                    # is worse than one that says nothing.
                    # A13/A14: `rpartition("_")` would name this rider
                    # "Member", which is not what anything in the game or on
                    # the sheet is called. The stage is the Salon.
                    stat = ("Salon" if formula.endswith("_per_salon_member")
                            else formula.rpartition("_")[2].title())
                    parts.append(f"Scales with [gold]{stat}[/gold].")
                else:
                    n, _, rest = formula.partition("_per_")
                    step, _, stat = rest.partition("_")
                    parts.append(
                        f"+{n} damage per {step} [gold]{stat.title()}[/gold].")
            if "bonus_vs_aura" in eff:
                if rehomed:
                    parts.append("Bonus damage vs. an elemental aura.")
                else:
                    parts.append(
                        f"+{int(eff['bonus_vs_aura'])} damage if the enemy "
                        "has an elemental aura.")

        elif op == "gain_spark":
            if spark_upgrade(card):
                # Plural token off the LIVE value, same idiom as draw above.
                parts.append(
                    "Gain {Sparks:diff()} [gold]Spark{Sparks:plural:|s}[/gold]."
                )
            else:
                n = int(eff["amount"])
                parts.append(
                    "Gain 1 [gold]Spark[/gold]." if n == 1
                    else f"Gain {n} [gold]Sparks[/gold]."
                )

        elif op == "burst_energy":
            if burst_upgrade(card):
                parts.append("Gain {BurstEnergy:diff()} [gold]Burst Energy[/gold].")
            else:
                parts.append(f'Gain {int(eff["amount"])} [gold]Burst Energy[/gold].')

        elif op == "gain_charge":
            parts.append(
                f'Gain {int(eff["amount"])} [gold]Charge[/gold].')

        elif op == "summon_kurage":
            # The pulse arithmetic is NOT spelled out here. It is a computed
            # number (base + per-Charge x bank) and belongs in the rendered
            # var / hover tip where it updates live -- the Furina legibility
            # lesson: a face that prints stale arithmetic teaches the wrong
            # number. The face says what the card DOES; the tip says what it
            # is worth right now.
            turns = ("{KurageTurns:diff()}" if kurage_turns_upgrade(card)
                     else str(int(eff.get("amount", 1))))
            parts.append(
                f"Summon [gold]Bake-Kurage[/gold] for {turns} turn"
                + ("{KurageTurns:plural:|s}" if kurage_turns_upgrade(card)
                   else ("" if int(eff.get("amount", 1)) == 1 else "s"))
                + ".")

        elif op == "conscript":
            phrase = _conscript_phrase(eff)
            parts.append(phrase[0].upper() + phrase[1:] + ".")

        elif op == "gain_encore":
            base = int(eff["amount"])
            delta = encore_upgrade(card)
            if salon_calc_rider(card, eff) is not None:
                # The var carries both the upgrade (CalculationBase bumps)
                # and the salon x2, so it replaces the IfUpgraded swap.
                amount = "{Encore:diff()}"
            else:
                amount = (
                    f"{{IfUpgraded:show:{base + delta}|{base}}}"
                    if delta else str(base))
            parts.append(f"Gain {amount} [gold]Encore[/gold].")

        elif op == "spend_encore":
            parts.append(
                f"Spend {int(eff['amount'])} [gold]Encore[/gold]; "
                "lose HP for any shortfall.")

        elif op == "raise_fanfare_cap":
            parts.append(
                "Increase your [gold]Fanfare[/gold] cap by "
                "{FanfareCap:diff()} this combat.")

        elif op == "gain_fanfare_floor":
            # "Baseline", not "floor" or "minimum": the meter's rule text
            # already says it fades "never below the baseline your Powers have
            # built", so the card and the meter have to use one word for one
            # concept. "This combat" is stated because the grant does NOT
            # persist across fights.
            parts.append(
                "Permanently raise your [gold]Fanfare[/gold] baseline by "
                "{FanfareFloor:diff()} this combat.")

        elif op == "heal":
            parts.append("Heal {Heal:diff()} HP.")

        elif op == "apply_power":
            template = APPLY_POWERS[eff["power"]][2]
            if eff.get("member") == "random":
                # A11: the shared template says "typed", which was true when
                # every deploy named its member. On a random deploy that word
                # tells the player nothing and implies a choice they do not
                # have. B5 will name the specific members; this only has to
                # stop the random one from lying.
                template = template.replace(
                    "{X} typed [gold]Salon Member(s)[/gold]",
                    "{X} RANDOM [gold]Salon Member(s)[/gold]")
            x = ("{PowerAmount:diff()}"
                 if eff is power_upgrade_effect(card)
                 or salon_calc_rider(card, eff) is not None
                 else str(int(eff["amount"])))
            to = {"all_enemies": " to ALL enemies",
                  "random_enemy": " to a random enemy"}.get(
                      eff.get("target"), "")
            parts.append(template.replace("{X}", x).replace("{TO}", to))

        elif op == "detonate":
            where = ("an enemy's" if eff["target"] == "enemy" else "ALL")
            parts.append(f"Detonate {where} [gold]Bombs[/gold].")
            bonus = int(eff.get("bonus", 0))
            if bonus_upgrade(card):
                parts.append("Detonations deal {Bonus:diff()} more damage.")
            elif bonus:
                parts.append(f"Detonations deal {bonus} more damage.")

        elif op == "modify_bombs":
            scope = ("placed this turn "
                     if eff.get("scope", "all") == "placed_this_turn" else "")
            amt = ("{Bonus:diff()}" if bonus_upgrade(card)
                   else str(int(eff["bonus"])))
            parts.append(
                f"[gold]Bombs[/gold] {scope}deal {amt} more damage."
            )

        elif op == "move_bombs":
            parts.append("Move ALL [gold]Bombs[/gold] to an enemy.")
            bonus = int(eff.get("bonus", 0))
            if bonus_upgrade(card):
                parts.append("Moved [gold]Bombs[/gold] deal {Bonus:diff()} more damage.")
            elif bonus:
                parts.append(f"Moved [gold]Bombs[/gold] deal {bonus} more damage.")

        elif op == "chance_bomb_per_detonation":
            chance = ("{Chance:diff()}" if chance_upgrade(card)
                      else str(int(round(float(eff["chance"]) * 100))))
            parts.append(
                f"Each detonation: {chance}% chance to place a new "
                f'{int(eff["bomb_damage"])}-damage [gold]Bomb[/gold] on a '
                "random enemy."
            )

        elif op == "generate_guest_star":
            amount = int(eff.get("amount", 1))
            rarity = eff["rarity"].capitalize()
            noun = "card" if amount == 1 else "cards"
            parts.append(
                f"Add {amount} random {rarity} [gold]Companion[/gold] "
                f"{noun} to your hand.")
            if "generate_cost_override" in deltas:
                parts.append(
                    "{IfUpgraded:show:They cost 0 this turn.|}")

        elif op == "cost_mod":
            n = -int(eff["delta"])
            parts.append(
                f"[gold]Companion[/gold] cards cost {n} less this turn.")

        elif op == "copy_companion_in_hand":
            base_txt = ("Add a copy of a random [gold]Companion[/gold] card "
                        "in your hand to your hand.")
            if "cost_override" in eff:
                parts.append(base_txt + f" The copy costs {int(eff['cost_override'])}.")
            elif "copy_cost_override" in upgrade_plan(card)[0]:
                o = int(upgrade_plan(card)[0]["copy_cost_override"])
                parts.append(
                    "{IfUpgraded:show:" + base_txt + f" The copy costs {o}.|"
                    + base_txt + "}")
            else:
                parts.append(base_txt)

        elif op == "copy_spotlighted_in_hand":
            base_txt = (
                "Add a copy of a random [gold]Spotlighted[/gold] card "
                "in your hand to your hand.")
            if "cost_override" in eff:
                parts.append(
                    base_txt
                    + f" The copy costs {int(eff['cost_override'])}.")
            elif "copy_cost_override" in upgrade_plan(card)[0]:
                override = int(
                    upgrade_plan(card)[0]["copy_cost_override"])
                parts.append(
                    "{IfUpgraded:show:" + base_txt
                    + f" The copy costs {override}.|"
                    + base_txt + "}")
            else:
                parts.append(base_txt)

        elif op == "replay_next_companion":
            t = int(eff.get("times", 1))
            times_txt = "an extra time" if t == 1 else f"{t} extra times"
            parts.append(
                "The next [gold]Companion[/gold] card you play this turn "
                f"is played {times_txt}.")

        elif op == "copy_companions_played_this_combat":
            clause = ("Add a copy of every [gold]Companion[/gold] card "
                      "played this combat to your hand.")
            if eff.get("cost_override") is not None:
                clause += f' They cost {int(eff["cost_override"])}.'
            parts.append(clause)

        elif op == "apply_aura":
            el = eff["element"].capitalize()
            where = {"enemy": "", "random_enemy": " to a random enemy",
                     "all_enemies": " to ALL enemies"}[eff.get("target", "enemy")]
            parts.append(f"Apply [gold]{el}[/gold]{where}.")

        elif op == "swirl":
            tgt = eff.get("target", "enemy")
            parts.append("[gold]Swirl[/gold] ALL enemies' auras."
                         if tgt == "all_enemies"
                         else "[gold]Swirl[/gold] an enemy's aura.")

        elif op == "refresh_all_auras":
            parts.append("Refresh ALL elemental auras.")

        elif op == "grow_damage":
            parts.append(
                f'Permanently increase this card\'s damage by '
                f'{int(eff["amount"])} this combat.')

        elif op == "buff_next_attack":
            n = ("{PowerAmount:diff()}" if eff is power_upgrade_effect(card)
                 else str(int(eff["amount"])))
            parts.append(f"Your next Attack deals {n} more damage.")

        elif op == "energy":
            n = int(eff["amount"])
            # Same defect as the play emitter: an upgradeable amount printed
            # its BASE forever. The var renders the diff so the face, the
            # upgrade preview and the energy actually gained all agree.
            parts.append("Gain {Energy:diff()} Energy."
                         if energy_upgrade(card) else f"Gain {n} Energy.")

        elif op == "scry_discard":
            parts.append(
                f'Look at the top {int(eff["amount"])} cards of your draw '
                "pile; discard one.")

        elif op == "exhaust_from" and eff.get("select") == "chosen":
            n = ("{Exhausts:diff()}" if exhaust_upgrade(card)
                 else str(int(eff.get("amount", 1))))
            plural = "" if str(n) == "1" else "s"
            # VOICE LAW (R55): the card says what happens, and what happens is
            # a rotation. No "sacrifice", no "destroy" -- the unit leaves the
            # line intact. Exhaust is the game's keyword and stays.
            parts.append(
                f"[gold]Exhaust[/gold] {n} card{plural} from your hand.")

        elif op == "exhaust_from":
            parts.append("Exhaust a random Status card from your hand.")

        elif op == "add_card":
            n = eff.get("amount", 1)
            zone_txt = ("your hand"
                        if (eff.get("zone") or eff.get("to", "discard")) == "hand"
                        else "your discard pile")
            if "pool" in eff:
                archetype, _, rarity = eff["pool"].rpartition("_")
                rarity = rarity.rstrip("s").capitalize()
                count = "{Stash:diff()}" if stash_upgrade(card) else str(int(n))
                clause = (f"Add {count} random [gold]{archetype}[/gold] "
                          f"{rarity} cards to {zone_txt}.")
                if eff.get("cost_override") == 0:
                    clause += " They cost 0 this combat."
                elif "cost_override" in eff:
                    clause += f' They cost {int(eff["cost_override"])} this combat.'
                parts.append(clause)
            else:
                name = eff.get("card_id") or eff.get("card")
                name = name.replace("_", " ").title()
                a_card = (f"a [gold]{name}[/gold]" if int(n) == 1
                          else f"{int(n)} [gold]{name}[/gold] cards")
                parts.append(f"Add {a_card} to {zone_txt}.")

        elif op == "conditional":
            pred_txt = predicate_text(eff["if"])
            then = eff.get("then", [])
            if any(e.get("op") == "repeat_this" for e in then):
                parts.append(f"{pred_txt}: play this card again.")
            else:
                then_txt = _branch_text(card, then, in_then=True)
                clause = f"{pred_txt}: {then_txt}"
                els = eff.get("else", [])
                if els:
                    clause += f" Otherwise: {_branch_text(card, els, in_then=False)}"
                if condition_upgrade(card):
                    # {IfUpgraded:show:upgraded|normal} -- the runtime form
                    # BaseLib's SimpleLoc MakeUpgradeSwap generates. Pipe is
                    # the separator, so pipes in either arm (e.g. plural
                    # tokens) would break parsing -- stop loudly.
                    upgraded = then_txt[0].upper() + then_txt[1:]
                    if "|" in upgraded or "|" in clause:
                        raise SystemExit(
                            f"gen_klee_cards: {card['id']}: condition-swap "
                            "text contains '|' -- cannot nest in "
                            "{IfUpgraded:show:...}.")
                    clause = "{IfUpgraded:show:" + upgraded + "|" + clause + "}"
                parts.append(clause)

        elif op == "discard":
            n = int(eff.get("amount", 1))
            if plain_discard_upgrade(card):
                # Upgradeable: the face must show the NEW number, so it
                # renders through the var like every other upgraded count.
                parts.append("Discard {Discards:diff()} random card(s).")
            else:
                parts.append(
                    "Discard a random card." if n == 1
                    else f"Discard {n} random cards."
                )

        elif op == "discard_for_sparks":
            # `sparks` is a CAP on the total, never a rate: tier0
            # _op_discard_for_sparks does `gain = min(fx["sparks"], discarded)`
            # -- 1 Spark per card ACTUALLY discarded, capped (R36 ratifies the
            # same reading, and the emitted C# matches with Math.Min).
            #
            # Bug hunt 2026-07-21: the old template substituted that cap into
            # "gain {Sparks} Sparks PER CARD DISCARDED", which reads as a rate.
            # At 1/1 the two coincide, so only the upgrade lied -- Crackle+ read
            # "discard 2: gain 2 Sparks per card discarded" (parsed as 4) and
            # granted 2, which is the difference between crossing the 3-Spark
            # free-attack threshold and not. The rate is always 1; the cap is
            # printed separately, and only when it can actually bind.
            n, m = int(eff["amount"]), int(eff["sparks"])
            d_n, d_m = discard_upgrade(card)
            if (d_n, d_m) != (0, 0):
                text = ("Discard {Discards:diff()} card{Discards:plural:|s}: "
                        "gain 1 [gold]Spark[/gold] per card discarded.")
                # The cap binds only if it can be lower than the discard count
                # in some reachable state (base or upgraded).
                if m < n or (m + d_m) < (n + d_n):
                    text += " Maximum {Sparks:diff()}."
                parts.append(text)
            else:
                cards_w = "a card" if n == 1 else f"{n} cards"
                text = f"Discard {cards_w}: gain 1 [gold]Spark[/gold] per card discarded."
                if m < n:
                    text += f" Maximum {m}."
                parts.append(text)

    if added_draw_upgrade(card):
        n = added_draw_upgrade(card)
        draw = "Draw 1 card." if n == 1 else f"Draw {n} cards."
        parts.append("{IfUpgraded:show:" + draw + "|}")
    if added_encore_upgrade(card):
        n = added_encore_upgrade(card)
        parts.append(
            "{IfUpgraded:show:Gain "
            f"{n} [gold]Encore[/gold].|}}")

    # Sly. DEFECT FIX (v0.5 fill): the discard hook generated correctly from
    # the first Sly card onward, but the card FACE never mentioned it -- so
    # drifting_lantern, the sheet's self-declared "Sly teaching card", printed
    # "Gain 4 Block." and taught nothing. A mechanic a player cannot read is a
    # mechanic that does not exist at the table. Rendered off the same text
    # builder as the played face, through _sly_view so the numbers here are
    # LITERAL: no upgrade delta reaches a Sly branch (upgrades sheet header,
    # "no sly-delta key exists in the applier"), and rendering a {Var:diff()}
    # would print the played face's upgraded number on a line that never moves.
    if card.get("sly"):
        sly_text = build_description(_sly_view(card)).strip()
        if sly_text:
            parts.append(f"[gold]Sly[/gold]: {sly_text}")

    return " ".join(parts)


def _is_sly_branch(card: dict) -> bool:
    """True while emitting a card's Sly branch (see _sly_view).

    Every amount inside a Sly branch is LITERAL. The played face's
    DynamicVars belong to the played face: a Sly branch that reached for
    them printed and dealt the upgraded number on a line the sim never
    upgrades, and -- worse -- reached for vars the card does not declare at
    all when the branch used an op the played face lacks (Quiet Harbor's
    Sly draw against a card whose only var is Block).
    """
    return bool(card.get("_sly_branch"))


def _sly_view(card: dict) -> dict:
    """The card as its Sly branch sees itself: the sly list as the effects,
    and an id no upgrade sheet knows.

    The id swap is the load-bearing part. Both the text builder and the body
    emitter ask `upgrade_plan(card)` whether a delta claims a given op, and
    they key that on the card id -- so a Sly branch built under the real id
    inherited the PLAYED face's deltas. Driftglass (hit 8, Sly hit 5) emitted
    `DynamicVars.Damage` for the Sly hit and so dealt 8 on discard, and
    drifting_lantern's Sly Block upgraded from 4 to 6 alongside its played
    face. Both contradict the sim, which never moves a Sly number.
    """
    view = {**card, "id": card["id"] + "__sly", "_sly_branch": True,
            "effects": card["sly"], "cost": card.get("cost", 0)}
    # A Sly branch has no Sly branch of its own. Leaving the key in place
    # made build_description recurse into itself forever.
    view.pop("sly", None)
    return view


def build_upgrade(card: dict) -> list[str]:
    # R24: every line comes from a ruled delta in klee-upgrades.yaml; effects
    # without a delta key upgrade nothing (e.g. snap's Spark rider stays put
    # while its damage bumps -- R1: the upgrade must not move the resource
    # curve). Lines follow effect order; a cost delta lands last. The `done`
    # set guards against a delta double-applying if a card ever carries two
    # effects of the same op.
    deltas, reason = upgrade_plan(card)
    if reason:
        return []
    key_for = {"block": "block", "draw": "draw", "gain_spark": "spark",
               "place_bomb": "bomb_damage", "burst_energy": "burst_energy",
               "heal": "heal",
               "summon_kurage": "kurage_turns", "energy": "energy",
               "block_next_turn": "block_next_turn",
               # G6: the PLAIN discard op. Shares the "Discards" var name with
               # discard_for_sparks deliberately -- no card carries both ops
               # (plain_discard_upgrade returns 0 if it does), so the name is
               # unambiguous per card and the two grammars read alike.
               "discard": "discard",
               "exhaust_from": "exhaust"}
    var_for = {"block": "DynamicVars.Block", "draw": "DynamicVars.Cards", "gain_spark": 'DynamicVars["Sparks"]',
               "burst_energy": 'DynamicVars["BurstEnergy"]', "apply_power": 'DynamicVars["PowerAmount"]',
               "buff_next_attack": 'DynamicVars["PowerAmount"]',
               "heal": 'DynamicVars["Heal"]',
               "summon_kurage": 'DynamicVars["KurageTurns"]',
               "energy": 'DynamicVars["Energy"]',
               "block_next_turn": 'DynamicVars["BlockNextTurn"]',
               "discard": 'DynamicVars["Discards"]',
               "exhaust_from": 'DynamicVars["Exhausts"]'}
    lines, done = [], set()
    for eff in card["effects"]:
        op = eff["op"]
        if op == "discard_for_sparks":
            # R36: one effect, two delta keys -- both vars move together.
            for key, var in (("discard", 'DynamicVars["Discards"]'),
                             ("sparks", 'DynamicVars["Sparks"]')):
                if key in deltas and key not in done:
                    done.add(key)
                    lines.append(f"{var}.UpgradeValueBy({int(deltas[key])}m);")
            continue
        if op in BONUS_OPS and "bonus" in eff and "bonus" in deltas \
                and "bonus" not in done:
            done.add("bonus")
            lines.append(
                f'DynamicVars["Bonus"].UpgradeValueBy({int(deltas["bonus"])}m);')
            continue
        if op == "chance_bomb_per_detonation" and "chance" in deltas \
                and "chance" not in done:
            # tier0 upgrades.py REPLACES chance; a DynamicVar only bumps, so
            # the delta is computed here from the sheet's base -- both values
            # are static, so the rendered number is exact.
            done.add("chance")
            pts = int(round(float(deltas["chance"]) * 100
                            - float(eff["chance"]) * 100))
            lines.append(f'DynamicVars["Chance"].UpgradeValueBy({pts}m);')
            continue
        if op in POWER_UPGRADE_OPS:
            # Only the effect the sim binds the delta to owns the var (see
            # power_upgrade_effect) -- keying off "first POWER_UPGRADE_OPS
            # effect" here would bump the wrong effect for a name-matched
            # weak/vulnerable delta listed after another power.
            key = (next((k for k in POWER_UPGRADE_KEYS if k in deltas), None)
                   if eff is power_upgrade_effect(card) else None)
        elif op == "damage" and eff["target"] != "self":
            key = "damage"
        else:
            key = key_for.get(op)
        if key is None or key not in deltas or key in done:
            continue
        done.add(key)
        if salon_calc_rider(card, eff) is not None:
            # Salon-converted numbers (block/draw/power alike) all keep their
            # printed base in CalculationBase, so that is what upgrades.
            var = "DynamicVars.CalculationBase"
        elif key == "damage":
            # Converted riders have no "Damage" var -- their base lives in
            # CalculationBase (the CalculatedDamageVar's base term).
            var = ("DynamicVars.CalculationBase"
                   if calc_rider(card, eff) is not None
                   else "DynamicVars.Damage")
        elif key == "block" and (spotlight_block_rider(card, eff) is not None
                                 or block_calc_rider(card, eff) is not None):
            # Converted block has no "Block" var -- its base is CalculationBase.
            var = "DynamicVars.CalculationBase"
        elif key == "bomb_damage":
            var = f"DynamicVars.{bomb_var(card)}"
        else:
            var = var_for[op]
        lines.append(f"{var}.UpgradeValueBy({int(deltas[key])}m);")
    if "times" in deltas and times_var_effect(card) is not None:
        # Post-loop: the loop keys a damage op to "damage", so a card that
        # upgrades BOTH its per-hit number and its hit count (none today, but
        # the sheet can rule it) would otherwise drop whichever key lost.
        lines.append(
            f'DynamicVars["Times"].UpgradeValueBy({int(deltas["times"])}m);')
    if "formula_per" in deltas:
        # The PER term of an amount_formula lives in ExtraDamage (the middle
        # slot of the CalculatedDamageVar triple: base + per * count), so the
        # upgrade bumps that var and the face re-renders itself.
        lines.append(
            f'DynamicVars.ExtraDamage.UpgradeValueBy({int(deltas["formula_per"])}m);')
    if "formula_base" in deltas:
        # The BASE term lives in CalculationBase (the first slot of the same
        # triple). Same var the plain `damage` delta already targets on a
        # converted rider -- see the calc_rider branch above -- so this is the
        # existing path, reached by an explicit key instead of by inference.
        lines.append(
            f'DynamicVars.CalculationBase.UpgradeValueBy({int(deltas["formula_base"])}m);')
    if "conditional_bonus" in deltas:
        # tier0: bump the then-branch's first damage (the ExtraDamage var;
        # expressibility gated in upgrade_plan/conditional_bonus_upgrade).
        lines.append(
            f'DynamicVars.ExtraDamage.UpgradeValueBy({int(deltas["conditional_bonus"])}m);')
    if branch_draw_upgrade(card):
        # tier0 draw deltas bump ALL draw ops, branches included. Only the
        # BRANCH vars are emitted here: when the card also draws at top level
        # that draw owns `Cards` and the plain top-level draw path above has
        # already bumped it, so repeating it here would upgrade one number
        # twice (caught on Compose Herself, whose OnUpgrade briefly carried
        # two identical Cards bumps).
        d = int(deltas["draw"])
        for name in dict.fromkeys(branch_draw_vars(card)):
            if not any(f'"{name}"' in decl or f"{name}Var(" in decl
                       for decl in build_vars(card)):
                continue
            lines.append(
                f"DynamicVars.Cards.UpgradeValueBy({d}m);" if name == "Cards"
                else f'DynamicVars["{name}"].UpgradeValueBy({d}m);')
    if "condition" in deltas:
        lines.append(
            "// condition: unconditional -- expressed at play time as "
            "(IsUpgraded || predicate); the text swaps via {IfUpgraded:show:...}.")
    if "bombs" in deltas:
        lines.append(f'DynamicVars["Bombs"].UpgradeValueBy({int(deltas["bombs"])}m);')
    if "bonus_per_detonation" in deltas:
        lines.append(
            f'DynamicVars["BonusPer"].UpgradeValueBy({int(deltas["bonus_per_detonation"])}m);')
    if "encore" in deltas:
        salon_encore = next(
            (e for e in card["effects"]
             if e.get("op") == "gain_encore"
             and salon_calc_rider(card, e) is not None), None)
        if salon_encore is not None:
            # A salon-converted encore prints {Encore:diff()} off the
            # CalculatedVar, so its base upgrades like any other var instead
            # of the amount swapping on an IsUpgraded read.
            lines.append(
                "DynamicVars.CalculationBase.UpgradeValueBy("
                f'{int(deltas["encore"])}m);')
        else:
            lines.append(
                "// encore: every gain_encore site reads IsUpgraded at play "
                "time (branches included).")
    if "fanfare_cap" in deltas:
        lines.append(
            'DynamicVars["FanfareCap"].UpgradeValueBy('
            f'{int(deltas["fanfare_cap"])}m);')
    if "fanfare_floor" in deltas:
        lines.append(
            'DynamicVars["FanfareFloor"].UpgradeValueBy('
            f'{int(deltas["fanfare_floor"])}m);')
    if "cards" in deltas:
        lines.append(f'DynamicVars["Stash"].UpgradeValueBy({int(deltas["cards"])}m);')
    if deltas.get("remove") == "exhaust":
        # tier0: card.exhaust = False. Keywords are instance-owned, so this
        # touches only the upgraded copy; the auto-keyword text follows.
        lines.append("RemoveKeyword(CardKeyword.Exhaust);")
    if "copy_cost_override" in deltas:
        lines.append(
            "// copy_cost_override: expressed at play time as an IsUpgraded "
            "read in OnPlay; the text swaps via {IfUpgraded:show:...}.")
    if "generate_cost_override" in deltas:
        lines.append(
            "// generate_cost_override: applied to each generated card at "
            "play time when IsUpgraded.")
    if "add" in deltas:
        add_op = deltas["add"]["op"]
        if add_op == "draw":
            lines.append(
                "// add: draw -- expressed at play time as an IsUpgraded-gated "
                "draw appended after the base effects.")
        else:
            lines.append(
                "// add: gain_encore -- expressed at play time as an "
                "IsUpgraded-gated effect appended after the base effects.")
    if "encore_cost" in deltas:
        lines.append(
            "CustomResources<EncoreResource>.Cost(this)!.UpgradeCostBy("
            f'{int(deltas["encore_cost"])});')
    if "fanfare_cost" in deltas:
        lines.append(
            "CustomResources<FanfareResource>.Cost(this)!.UpgradeCostBy("
            f'{int(deltas["fanfare_cost"])});')
    if "cost" in deltas:
        lines.append(f'EnergyCost.UpgradeBy({int(deltas["cost"])});')
    if "innate" in deltas:
        # R37: boolean, only `true` is a ruling (tier0 applier enforces the
        # same). Keywords are instance-owned, so this touches only the
        # upgraded copy.
        if deltas["innate"] is not True:
            raise SystemExit(
                f"gen_klee_cards: {card['id']}: innate delta must be `true`")
        lines.append("AddKeyword(CardKeyword.Innate);")
    if "retain" in deltas:
        if deltas["retain"] is not True:
            raise SystemExit(
                f"gen_klee_cards: {card['id']}: retain delta must be `true`")
        lines.append("AddKeyword(CardKeyword.Retain);")
    return lines


def emit(
    card: dict, profile: CharacterProfile = KLEE_PROFILE
) -> str:
    cls = pascal(card["id"])
    is_attack = card["type"] == "attack"
    # Sheet header: "ALL attacks apply pyro; applies_element omitted = true for
    # attacks". Skills carry no element. COMPANIONS are exempt from cadence
    # (tier0 _element_for): they apply their element only where the sheet
    # says applies_element -- the card-level interface carries it, so a
    # companion card mixing elemental and non-elemental damage would be
    # inexpressible (blocked_reason guards it).
    if is_companion(card):
        elemental = any(e.get("op") == "damage" and e.get("applies_element")
                        for e in card.get("effects", []))
        element_cs = ELEMENT_CS[card["element"]]
    else:
        elemental = profile.damage_applies_element(card)
        element_cs = ELEMENT_CS[profile.native_element]

    # UI affordances derive from the same mechanics as play resolution.
    # A damage-bearing IElementalCard supplies its card element; apply-only
    # skills supply the element written on their effect; Swirl supplies Anemo.
    preview_element_cs = element_cs if elemental else None
    if preview_element_cs is None:
        elemental_effect = next((e for e in card.get("effects", [])
                                 if e.get("op") in ("apply_aura", "swirl")), None)
        if elemental_effect is not None:
            preview_element_cs = (
                ELEMENT_CS[elemental_effect["element"]]
                if elemental_effect["op"] == "apply_aura"
                else "Element.Anemo")

    aura_keyword_by_element = {
        "pyro": "KleeKeywords.AppliesPyro",
        "hydro": "KleeKeywords.AppliesHydro",
        "electro": "KleeKeywords.AppliesElectro",
        "cryo": "KleeKeywords.AppliesCryo",
    }
    aura_elements = []
    if elemental:
        source_element = (
            card["element"] if is_companion(card) else profile.native_element
        )
        if source_element in aura_keyword_by_element:
            aura_elements.append(source_element)
    for e in card.get("effects", []):
        if e.get("op") == "apply_aura" and e.get("element") in aura_keyword_by_element:
            aura_elements.append(e["element"])
    aura_elements = list(dict.fromkeys(aura_elements))
    includes_bomb_rules = any(e.get("op") in {
        "place_bomb", "detonate", "modify_bombs", "move_bombs",
        "chance_bomb_per_detonation"
    } for e in card.get("effects", []))

    # The card's declared TargetType follows its FIRST damaging effect; a card
    # that only blocks or draws targets Self.
    target_type = "TargetType.Self"
    for eff in card["effects"]:
        if eff["op"] == "damage" and eff["target"] != "self":
            target_type = TARGET_CS[eff["target"]]
            break
        # A bomb aimed at a chosen enemy makes the whole card enemy-targeted,
        # even when nothing about it deals direct damage (e.g. Double Pop).
        if eff["op"] == "place_bomb":
            target_type = TARGET_CS[eff["target"]]
            break
        # Same rule for the bomb-manipulation ops: a chosen-enemy detonate
        # (Quick Fuse) or move destination (Careful Arrangement) makes the
        # card enemy-targeted; detonate-all reads as AllEnemies.
        if eff["op"] in ("detonate", "move_bombs"):
            target_type = TARGET_CS[eff["target"]]
            break
        # Enemy debuffs too: Surprise Visit is nothing but a chosen-enemy
        # Vulnerable, so the apply is what makes the card aimable.
        if (eff["op"] == "apply_power"
                and eff.get("power") in ENEMY_APPLY_POWERS):
            target_type = TARGET_CS[eff["target"]]
            break
        # Element ops (companions): a chosen-enemy swirl/apply_aura makes
        # the card aimable, same rule as place_bomb.
        if eff["op"] in ("apply_aura", "swirl"):
            target_type = TARGET_CS[eff.get("target", "enemy")]
            break

    vars_ = build_vars(card)
    body = build_body(card, profile)
    upgrade = build_upgrade(card)
    _, no_upgrade_reason = upgrade_plan(card)
    desc = build_description(card)

    interfaces = "CustomCardModel"
    if elemental:
        interfaces += ", IElementalCard"
    if is_companion(card):
        interfaces += ", ICompanionCard"
    elif profile.emit_character_identity:
        interfaces += ", ICharacterCard"
    # Sheet `skill_tag` -> ISkillTagCard: worth BURST_PER_SKILL_TAG burst
    # energy when played (KleeElementalHooks.AfterCardPlayed reads the marker).
    if "skill_tag" in card.get("tags", []):
        interfaces += ", ISkillTagCard"

    ind = "\n        "
    vars_cs = (",".join(f"{ind}    {v}" for v in vars_)).lstrip()
    vars_block = f"            {vars_cs}\n" if vars_cs else ""
    body_cs = ind.join(body)
    # RULED 2026-07-21: companions upgrade like any other card. They used to
    # emit MaxUpgradeLevel 0 on the companion sheets' "companions never scale"
    # header, which contradicted the upgrade sheets -- the sim honours those
    # deltas and tier05 smiths companions at rest sites, so the mod was
    # measuring a power curve it could not produce.
    upgrade_cs = (
        ind.join(upgrade)
        if upgrade
        else f"// R24: NO upgrade path -- {no_upgrade_reason}. Flagged in manifest."
    )

    # Sly (Kokomi, playtest sprint): the card's `sly` list fires when the card
    # is DISCARDED, not played. tier0 resolves victim.sly at the discard site,
    # so the mod hangs it on the card's own AfterCardDiscarded hook -- the
    # effects are the card's, and putting them anywhere else would separate a
    # card's behaviour from the card.
    sly_cs = ""
    if card.get("sly"):
        # _sly_view, not a plain effects swap: see its docstring. Under the
        # card's own id the emitter reached for the played face's DynamicVars
        # and silently printed the wrong number on discard.
        sly_body = ind.join(build_body(_sly_view(card), profile))
        # Only declare the placeholder when the body actually threads one
        # through; an unconditional declaration is a CS0219 on every Sly
        # branch that happens not to need it.
        cardplay_decl = ""
        if "cardPlay" in sly_body:
            cardplay_decl = (
                "        // A discard is not a play, so there is no CardPlay "
                "to attribute\n"
                "        // these effects to. The shared body emitter threads "
                "one through for\n"
                "        // VFX and source attribution; null is the honest "
                "value here, and\n"
                "        // every API it reaches takes a nullable CardPlay.\n"
                "        CardPlay? cardPlay = null;\n")
        sly_cs = f'''
    /// <summary>Sly: resolves when THIS card is discarded.</summary>
    public override async Task AfterCardDiscarded(
        PlayerChoiceContext choiceContext, CardModel card)
    {{
        if (card != this) return;
{cardplay_decl}        {sly_body}
    }}
'''

    element_member = ""
    if elemental and is_companion(card):
        element_member = (
            "\n    /// <summary>Sheet applies_element: this companion attack applies its element.</summary>\n"
            f"    public Element Element => {element_cs};\n"
        )
    elif elemental:
        if profile is KLEE_PROFILE:
            element_member = (
                "\n    /// <summary>Sheet: all Klee attacks apply Pyro (catalyst-grade cadence).</summary>\n"
                "    public Element Element => Element.Pyro;\n"
            )
        else:
            element_member = (
                "\n    /// <summary>Sheet cadence: damaging Skills, Burst-tagged cards, "
                "and skill-tagged cards apply Hydro.</summary>\n"
                f"    public Element Element => {element_cs};\n"
            )
    if profile.emit_character_identity and not is_companion(card):
        element_member += (
            "\n    /// <summary>Roster identity used by character-aware mechanics "
            "such as Spotlight.</summary>\n"
            f'    public string CharacterId => "{profile.character_id}";\n'
        )
    if is_companion(card):
        personal = card.get("personal_pool")
        personal_cs = f'"{personal}"' if personal else "null"
        element_member += (
            "\n    /// <summary>Companion identity (companion sheet): star drives the\n"
            "    /// reward slot's rarity tier; PersonalPool gates per-character\n"
            "    /// offers; Nation drives SAME_NATION_REWARD_SHARE weighting.</summary>\n"
            f"    public int Star => {int(card['star'])};\n\n"
            f"    public Element CompanionElement => {element_cs};\n\n"
            f"    public string? PersonalPool => {personal_cs};\n\n"
            f'    public string? Nation => "{card["nation"]}";\n'
        )
    if str(card["cost"]) == "X":
        # X cost: canonical 0 + the CardModel virtual (CardEnergyCost ctor
        # ignores the canonical when CostsX).
        element_member += (
            "\n    protected override bool HasEnergyCostX => true;\n"
        )

    # exhaust: true -> the base game's own Exhaust keyword. CanonicalKeywords
    # is the virtual CardModel exposes for exactly this; keyword text renders
    # via the game's auto-keyword pipeline, so the description string does NOT
    # hand-write "Exhaust." (first exercised by da_da_da/all_my_treasures when
    # gain_spark unblocked them -- every earlier exhaust card was blocked, so
    # the generator never needed this before).
    #
    # skill_tag additionally emits the ElementalSkill DISPLAY keyword
    # (playtest finding 2026-07-20: the tag was invisible on cards). Gameplay
    # still reads ISkillTagCard; the keyword is what the player sees.
    keywords = []
    if card.get("exhaust"):
        keywords.append("CardKeyword.Exhaust")
    # A9: base-card Innate rides the same CanonicalKeywords rail as Exhaust,
    # so the banner renders through the game's auto-keyword pipeline and the
    # description string stays free of the word (see the note above).
    # OnUpgrade's AddKeyword path is unchanged and still serves `innate: true`
    # deltas -- a card can be born Innate or become it, not both.
    if card.get("innate"):
        keywords.append("CardKeyword.Innate")
    if "skill_tag" in card.get("tags", []):
        keywords.append("KleeKeywords.ElementalSkill")
    keywords.extend(aura_keyword_by_element[e] for e in aura_elements)
    keywords_member = ""
    if keywords:
        keywords_member = (
            "\n    public override IEnumerable<CardKeyword> CanonicalKeywords =>\n"
            "        new[] { " + ", ".join(keywords) + " };\n"
        )

    includes_confiscated_rules = any(
        eff.get("op") == "add_card" and eff.get("card") == "confiscated"
        for eff in card.get("effects", []))
    tooltip_member = ""
    tips_expr = ""
    if preview_element_cs is not None or includes_bomb_rules or includes_confiscated_rules:
        trigger_arg = preview_element_cs or "Element.None"
        bomb_arg = "true" if includes_bomb_rules else "false"
        confiscated_arg = (
            ", includesConfiscatedRules: true"
            if includes_confiscated_rules else "")
        tips_expr = (
            "KleeCardTooltips.ForCard(base.ExtraHoverTips, this, "
            f"{trigger_arg}, includesBombRules: {bomb_arg}"
            f"{confiscated_arg})")
    # Track L-C: the arithmetic the card text no longer carries. Wraps the
    # element/bomb tips when both apply, so one override yields both lists.
    rider_args = rider_tip_args(card)
    if rider_args:
        tips_expr = (
            f"FurinaRiderTips.ForCard({tips_expr or 'base.ExtraHoverTips'}, "
            f"this, {rider_args})")
    # Kokomi's two hidden reads. Neither can render on a card face -- the
    # pulse resolves at end of turn from a bank that will have moved, and the
    # Garment rider lands on OTHER cards -- so the hover tip is the only
    # surface either number has. See KokomiRiderTips for the argument.
    if profile is KOKOMI_PROFILE:
        if any(eff.get("op") == "summon_kurage"
               for eff in card.get("effects", [])):
            tips_expr = (
                "KokomiRiderTips.ForKuragePulse("
                f"{tips_expr or 'base.ExtraHoverTips'}, this)")
        if card.get("type") == "attack":
            tips_expr = (
                "KokomiRiderTips.ForGarmentAttack("
                f"{tips_expr or 'base.ExtraHoverTips'}, this)")
        # R78: every Muster card carries the keyword's definition, because
        # the faces no longer restate it. Attached from the OP rather than
        # from a card list, so a new conscript card cannot ship with a
        # keyword nothing on screen defines.
        if any(eff.get("op") == "conscript"
               for eff in _effects_everywhere(card)):
            tips_expr = (
                "KokomiRiderTips.ForMuster("
                f"{tips_expr or 'base.ExtraHoverTips'}, this)")
    if tips_expr:
        tooltip_member = (
            "\n    protected override IEnumerable<IHoverTip> ExtraHoverTips =>\n"
            f"        {tips_expr};\n"
        )
    hover_using = (
        "\nusing MegaCrit.Sts2.Core.HoverTips;" if tooltip_member else "")

    source_header = (
        "//     Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml.\n"
        if profile is KLEE_PROFILE
        else (
            f"//     Generated by {profile.generator_script} from "
            f"docs/{profile.sheet.name}.\n"
        )
    )
    upgrade_header = (
        "//     Upgrade deltas come from docs/klee-upgrades.yaml (R24 2026-07-20: the\n"
        "//     upgrades sheet is the single source of truth; codegen defaults abolished).\n"
        if profile is KLEE_PROFILE
        else (
            f"//     Upgrade deltas come from docs/{profile.character_id}-upgrades.yaml; "
            "unexpressible deltas block the upgrade path.\n"
        )
    )
    extra_usings = ""
    if profile is not KLEE_PROFILE:
        extra_usings = "\nusing KleeMod;\nusing KleeMod.Cards;"
    pool_comment = (
        "    // autoAdd: false -- KleeCardPool declares pool membership itself in\n"
        "    // GenerateAllCards. BaseLib's auto-registration would need a [Pool]\n"
        "    // attribute and would register every card a second time."
        if profile is KLEE_PROFILE
        else (
            "    // autoAdd: false -- the character-aware roster pool owns membership.\n"
            "    // Partially generated character sheets must never auto-register cards."
        )
    )
    # Base-game content keys on CardTag.Strike/Defend AND CardRarity.Basic
    # together: LargeCapsule.GetStrikeForCharacter is
    # `CardPool.AllCards.First(c => c.Rarity == Basic && c.Tags.Contains(
    # CardTag.Strike))` -- an untagged basic makes that First() throw inside
    # the Ancient event's option handler and hangs the room (playtest
    # 2026-07-23). Mirror the hand-written Kaboom/DuckAndCover pair: the
    # basic attack is the character's Strike, the basic blocker its Defend.
    tag = None
    if card["rarity"] == "basic":
        if card["type"] == "attack" and any(
                e.get("op") == "damage" and e.get("target") != "self"
                for e in card["effects"]):
            tag = "Strike"
        elif any(e.get("op") == "block" for e in card["effects"]):
            tag = "Defend"
    tags_member = (
        "\n\n    protected override HashSet<CardTag> CanonicalTags => "
        f"new() {{ CardTag.{tag} }};"
        if tag else "")
    resource_cost_setup = []
    if int(card.get("encore_cost", 0)) > 0:
        resource_cost_setup.append(
            "CustomResources<EncoreResource>.SetCanonicalCost("
            f"this, {int(card['encore_cost'])});")
    if int(card.get("fanfare_cost", 0)) > 0:
        resource_cost_setup.append(
            "CustomResources<FanfareResource>.SetCanonicalCost("
            f"this, {int(card['fanfare_cost'])});")
    resource_cost_cs = (
        "        " + "\n        ".join(resource_cost_setup) + "\n"
        if resource_cost_setup else "")

    return f'''// <auto-generated>
{source_header.rstrip()}
//     DO NOT EDIT. Edits are lost on the next regen -- change the sheet instead.
//
//     Sheet entry: id={card["id"]} rarity={card["rarity"]} cost={card["cost"]}
{upgrade_header.rstrip()}
// </auto-generated>

// Roslyn treats <auto-generated> files as outside the project's nullable
// context, so the ? annotations below need it re-enabled explicitly (CS8669).
#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Elements;
using KleeMod.Powers;{extra_usings}
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;{hover_using}
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace {profile.namespace};

public sealed class {cls} : {interfaces}
{{{element_member}{keywords_member}{tooltip_member}
    public override Texture2D? CustomPortrait => {profile.art_loader}.CardPortrait("{card["id"]}");

    public override List<(string, string)>? Localization => new()
    {{
        ("title", "{card["name"].replace('"', chr(92) + chr(34))}"),
        ("description", "{desc}"),
    }};{tags_member}

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {{
{vars_block.rstrip()}
        }};

{pool_comment}
    public {cls}()
        : base({0 if str(card["cost"]) == "X" else card["cost"]}, {TYPE_CS[card["type"]]}, {RARITY_CS[card["rarity"]]}, {target_type}, autoAdd: false)
    {{
{resource_cost_cs}    }}

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {{
        {body_cs}
    }}

    protected override void OnUpgrade()
    {{
        {upgrade_cs}
    }}
{sly_cs}}}
'''


def _run_klee(check: bool) -> int:
    cards = yaml.safe_load(SHEET.read_text(encoding="utf-8"))

    generated, blocked, no_upgrade = {}, {}, {}
    for card in cards:
        reason = blocked_reason(card)
        if reason:
            blocked[card["id"]] = reason
        else:
            generated[card["id"]] = emit(card)
            _, upgrade_reason = upgrade_plan(card)
            if upgrade_reason:
                no_upgrade[card["id"]] = upgrade_reason

    # Companions -- a blocked companion is a build failure, not a manifest
    # entry. Both rosters are user-ratified in scope (Mondstadt 2026-07-21;
    # Fontaine same day, "as long as the 50% nationality weighting is
    # respected"). Guest Star cards are skipped: they are Furina personal-pool
    # cameos generated mid-combat by her own cards, never offered in a reward
    # slot (tier05 companion_pool filters `not c.guest_star`), and nothing in
    # the Klee mod can create one.
    companions = {}
    for sheet_path, nation in COMPANION_SHEETS:
        for card in yaml.safe_load(sheet_path.read_text(encoding="utf-8")):
            if card.get("guest_star"):
                continue
            card.setdefault("nation", nation)
            reason = blocked_reason(card)
            if reason:
                raise SystemExit(
                    f"gen_klee_cards: companion {card['id']} blocked: {reason} "
                    "-- the whole roster is ratified in scope; extend the "
                    "generator, do not skip.")
            companions[card["id"]] = emit(card)

            # MANIFEST HOLE CLOSED (bug hunt 2026-07-21). This loop used to
            # skip upgrade_plan entirely, so no_upgrade_path listed only
            # klee-cards.yaml rows -- and the R24 safety net, which exists to
            # make "the sim can upgrade this and the mod cannot" visible,
            # covered zero companions while hiding 14 real divergences.
            # RULED 2026-07-21: companions upgrade per the sheets, so the
            # divergence is closed at the source; what remains here are the
            # genuinely inexpressible deltas, same as any other card.
            _, upgrade_reason = upgrade_plan(card)
            if upgrade_reason:
                no_upgrade[card["id"]] = upgrade_reason
    generated.update(companions)

    # The roster class the reward slot draws from (CompanionSlot.Roll):
    # generated so the sheet stays the single source of truth.
    roster_entries = "\n".join(
        f"        ModelDb.Card<{pascal(cid)}>()," for cid in sorted(companions))
    generated["companion_roster"] = f'''// <auto-generated>
//     Generated by tools/gen_klee_cards.py from docs/mondstadt-companions.yaml.
//     DO NOT EDIT. Edits are lost on the next regen -- change the sheet instead.
// </auto-generated>

#nullable enable

using System.Collections.Generic;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Generated;

/// <summary>
/// Every companion card. The 4th reward slot (CompanionSlot) draws from
/// here; companions are NOT in KleeCardPool (tier05 character_pool excludes
/// them -- the slot is their only door).
/// </summary>
public static class CompanionRoster
{{
    private static List<CardModel>? _all;

    public static IReadOnlyList<CardModel> All => _all ??= new List<CardModel>
    {{
{roster_entries}
    }};
}}
'''

    manifest = {
        "_comment": (
            "Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml. "
            "'blocked' cards need systems or hand-finishing; the reason names what stopped codegen."
        ),
        "generated": sorted(set(generated) - set(companions)
                            - {"companion_roster"}),
        "companions": sorted(companions),
        "blocked": dict(sorted(blocked.items())),
        "upgrades": {
            "_comment": "R24 (2026-07-20): docs/klee-upgrades.yaml is the single "
                        "source of truth for upgrade deltas; codegen defaults are "
                        "ABOLISHED. Generated cards listed below ship with NO "
                        "upgrade path (UNAPPLIABLE discipline) until their delta "
                        "is ratified, made numeric, or hand-finished.",
            "no_upgrade_path": dict(sorted(no_upgrade.items())),
        },
    }
    manifest_src = json.dumps(manifest, indent=2) + "\n"

    if check:
        stale = []
        for cid, src in generated.items():
            p = OUT_DIR / f"{pascal(cid)}.cs"
            if not p.exists() or p.read_text(encoding="utf-8") != src:
                stale.append(cid)
        expected_files = {f"{pascal(cid)}.cs" for cid in generated}
        actual_files = {p.name for p in OUT_DIR.glob("*.cs")}
        extra_files = sorted(actual_files - expected_files)
        manifest_stale = (
            not MANIFEST.exists()
            or MANIFEST.read_text(encoding="utf-8") != manifest_src
        )
        if stale or extra_files or manifest_stale:
            if stale:
                print(f"stale generated cards: {', '.join(sorted(stale))}", file=sys.stderr)
            if extra_files:
                print(f"stale generated files: {', '.join(extra_files)}", file=sys.stderr)
            if manifest_stale:
                print("stale generated manifest", file=sys.stderr)
            return 1
        print("gen_klee_cards: up to date")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Clear stale files so a card removed from the sheet does not linger.
    for old in OUT_DIR.glob("*.cs"):
        old.unlink()

    for cid, src in generated.items():
        (OUT_DIR / f"{pascal(cid)}.cs").write_text(src, encoding="utf-8")

    MANIFEST.write_text(manifest_src, encoding="utf-8")

    print(f"generated {len(generated)} cards, blocked {len(blocked)}")
    by_reason: dict[str, int] = {}
    for reason in blocked.values():
        key = reason.split("(")[0].strip()
        by_reason[key] = by_reason.get(key, 0) + 1
    for reason, n in sorted(by_reason.items(), key=lambda kv: -kv[1]):
        print(f"  blocked x{n}: {reason}")
    for cid, why in sorted(no_upgrade.items()):
        print(f"  no upgrade path: {cid} -- {why}")
    return 0


def _furina_runtime_cluster(card: dict, reason: str) -> str:
    """Stable workstream labels for Furina's blocked coverage manifest."""
    # Hand-written is not a GAP -- it is a finished decision, and bucketing it
    # under a workstream turns completed work into a standing item on the
    # coverage report. Checked first so no ops-based rule can reclaim it.
    if reason == "hand-written":
        return "hand_written"
    effects = card.get("effects", [])
    ops = {effect.get("op") for effect in effects}
    powers = {
        effect.get("power")
        for effect in effects
        if effect.get("op") == "apply_power"
    }
    predicates = {
        effect.get("if")
        for effect in effects
        if effect.get("op") == "conditional"
    }
    if (
        reason.startswith(("encore_cost", "fanfare_cost"))
        or ops
        & {
            "gain_encore",
            "spend_encore",
            "raise_fanfare_cap",
            "gain_fanfare_floor",
        }
        or any("fanfare" in str(power) for power in powers)
        or any("fanfare" in str(predicate) for predicate in predicates)
    ):
        return "encore_fanfare_resources"
    if (
        any("salon" in str(power) for power in powers)
        or any("salon" in str(predicate) for predicate in predicates)
    ):
        return "salon"
    if (
        "spotlight" in reason
        or "companion" in reason
        or any("spotlight" in str(power) for power in powers)
        or any("spotlight" in str(predicate) for predicate in predicates)
    ):
        return "spotlight"
    if "guest" in reason:
        return "guest_stars"
    if reason.startswith("kit card"):
        return "kit_burst"
    if "heal" in reason:
        return "healing"
    if "raise_fanfare_cap" in reason:
        return "encore_fanfare_resources"
    return "shared_emitter_gap"


def _run_furina(check: bool) -> int:
    """Emit the runtime-safe Furina subset and a complete blocker manifest.

    A partial character pool is intentionally inert: generated classes use
    autoAdd:false and no Furina pool references them until all runtime clusters
    exist. This lets codegen advance without accidentally shipping a partial
    reward pool.
    """
    cards = yaml.safe_load(FURINA_PROFILE.sheet.read_text(encoding="utf-8"))
    generated: dict[str, str] = {}
    blocked: dict[str, str] = {}
    no_upgrade: dict[str, str] = {}

    for card in cards:
        reason = blocked_reason(card, FURINA_PROFILE)
        if reason:
            blocked[card["id"]] = reason
            continue
        generated[card["id"]] = emit(card, FURINA_PROFILE)
        _, upgrade_reason = upgrade_plan(card)
        if upgrade_reason:
            no_upgrade[card["id"]] = upgrade_reason

    main_generated_ids = set(generated)

    main_entries = "\n".join(
        f"        ModelDb.Card<{pascal(card_id)}>(),"
        for card_id in sorted(main_generated_ids))
    generated["furina_card_roster"] = f'''// <auto-generated>
//     Generated by tools/gen_roster_cards.py from docs/furina-cards.yaml.
//     Every generated personal-pool card; FurinaCardPool owns membership.
// </auto-generated>

#nullable enable

using System.Collections.Generic;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Furina.Generated;

public static class FurinaCardRoster
{{
    private static List<CardModel>? _all;

    public static IReadOnlyList<CardModel> All => _all ??= new List<CardModel>
    {{
{main_entries}
    }};
}}
'''

    # Guest Stars are temporary Companion cards generated only by Furina's
    # personal-pool cards. They are emitted beside Furina (not into the shared
    # reward roster), and are intentionally not smithable.
    guest_star_ids: list[str] = []
    fontaine_sheet = next(
        path for path, nation in COMPANION_SHEETS if nation == "fontaine")
    for guest in yaml.safe_load(fontaine_sheet.read_text(encoding="utf-8")):
        if not guest.get("guest_star"):
            continue
        guest.setdefault("nation", "fontaine")
        reason = blocked_reason(guest, FURINA_PROFILE)
        if reason:
            raise SystemExit(
                f"gen_roster_cards: guest star {guest['id']} blocked: "
                f"{reason}")
        generated[guest["id"]] = emit(guest, FURINA_PROFILE)
        guest_star_ids.append(guest["id"])

    guest_entries = "\n".join(
        f"        ModelDb.Card<{pascal(card_id)}>(),"
        for card_id in sorted(guest_star_ids))
    generated["guest_star_roster"] = f'''// <auto-generated>
//     Generated by tools/gen_roster_cards.py from docs/fontaine-companions.yaml.
//     Guest Stars are temporary Furina generation targets, never reward cards.
// </auto-generated>

#nullable enable

using System.Collections.Generic;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Furina.Generated;

public static class GuestStarRoster
{{
    private static List<CardModel>? _all;

    public static IReadOnlyList<CardModel> All => _all ??= new List<CardModel>
    {{
{guest_entries}
    }};
}}
'''

    clusters: dict[str, list[str]] = {}
    cards_by_id = {card["id"]: card for card in cards}
    for card_id, reason in blocked.items():
        cluster = _furina_runtime_cluster(cards_by_id[card_id], reason)
        clusters.setdefault(cluster, []).append(card_id)

    manifest = {
        "_comment": (
            "Generated by tools/gen_roster_cards.py from docs/furina-cards.yaml. "
            "Only cards whose complete runtime grammar is implemented are emitted. "
            "Blocked cards are not auto-registered or added to a partial pool."
        ),
        "profile": {
            "character": FURINA_PROFILE.character_id,
            "element": FURINA_PROFILE.native_element,
            "cadence": (
                "damage on Skill, skill_tag, or burst_tag cards applies Hydro; "
                "plain Attacks do not"
            ),
            "namespace": FURINA_PROFILE.namespace,
        },
        "coverage": {
            "total": len(cards),
            "generated": len(main_generated_ids),
            "blocked": len(blocked),
        },
        "generated": sorted(main_generated_ids),
        "guest_stars": sorted(guest_star_ids),
        "blocked": dict(sorted(blocked.items())),
        "runtime_clusters": {
            key: sorted(value) for key, value in sorted(clusters.items())
        },
        "upgrades": {
            "_comment": (
                "docs/furina-upgrades.yaml is authoritative. A generated card "
                "listed below ships without an upgrade until its full delta is "
                "expressible; partial upgrade application is forbidden."
            ),
            "no_upgrade_path": dict(sorted(no_upgrade.items())),
        },
    }
    manifest_src = json.dumps(manifest, indent=2) + "\n"

    if check:
        stale = []
        for card_id, source in generated.items():
            path = FURINA_PROFILE.out_dir / f"{pascal(card_id)}.cs"
            if not path.exists() or path.read_text(encoding="utf-8") != source:
                stale.append(card_id)
        expected_files = {f"{pascal(card_id)}.cs" for card_id in generated}
        actual_files = {
            path.name for path in FURINA_PROFILE.out_dir.glob("*.cs")
        }
        extra_files = sorted(actual_files - expected_files)
        manifest_stale = (
            not FURINA_PROFILE.manifest.exists()
            or FURINA_PROFILE.manifest.read_text(encoding="utf-8")
            != manifest_src
        )
        if stale or extra_files or manifest_stale:
            if stale:
                print(
                    f"stale Furina generated cards: {', '.join(sorted(stale))}",
                    file=sys.stderr,
                )
            if extra_files:
                print(
                    f"stale Furina generated files: {', '.join(extra_files)}",
                    file=sys.stderr,
                )
            if manifest_stale:
                print("stale Furina generated manifest", file=sys.stderr)
            return 1
        print("gen_roster_cards: furina up to date")
        return 0

    FURINA_PROFILE.out_dir.mkdir(parents=True, exist_ok=True)
    for old in FURINA_PROFILE.out_dir.glob("*.cs"):
        old.unlink()
    for card_id, source in generated.items():
        path = FURINA_PROFILE.out_dir / f"{pascal(card_id)}.cs"
        path.write_text(source, encoding="utf-8")
    FURINA_PROFILE.manifest.write_text(manifest_src, encoding="utf-8")

    print(
        f"furina: generated {len(main_generated_ids)} cards "
        f"(+{len(guest_star_ids)} Guest Stars), "
        f"blocked {len(blocked)}"
    )
    for cluster, card_ids in sorted(clusters.items()):
        print(f"  {cluster}: {len(card_ids)}")
    for card_id, why in sorted(no_upgrade.items()):
        print(f"  no upgrade path: {card_id} -- {why}")
    return 0


def _run_kokomi(check: bool) -> int:
    """Emit the runtime-safe Kokomi subset and a complete blocker manifest.

    Same discipline as Furina's path: a partial pool is intentionally INERT.
    Generated classes use autoAdd:false and no Kokomi pool references them, so
    codegen can advance card by card without ever shipping a half-built reward
    pool. Blocked cards are named, counted, and clustered rather than silently
    dropped -- an unlisted card is a bug, an unlisted BLOCKER is a lie.
    """
    cards = yaml.safe_load(KOKOMI_PROFILE.sheet.read_text(encoding="utf-8"))
    generated: dict[str, str] = {}
    blocked: dict[str, str] = {}
    no_upgrade: dict[str, str] = {}

    for card in cards:
        reason = blocked_reason(card, KOKOMI_PROFILE)
        if reason:
            blocked[card["id"]] = reason
            continue
        generated[card["id"]] = emit(card, KOKOMI_PROFILE)
        _, upgrade_reason = upgrade_plan(card)
        if upgrade_reason:
            no_upgrade[card["id"]] = upgrade_reason

    main_generated_ids = set(generated)

    main_entries = NEWLINE_JOIN.join(
        f"        ModelDb.Card<{pascal(card_id)}>(),"
        for card_id in sorted(main_generated_ids))
    generated["kokomi_card_roster"] = f'''// <auto-generated>
//     Generated by tools/gen_roster_cards.py from docs/kokomi-cards.yaml.
//     Every generated personal-pool card; KokomiCardPool owns membership.
// </auto-generated>

#nullable enable

using System.Collections.Generic;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Kokomi.Generated;

public static class KokomiCardRoster
{{
    private static List<CardModel>? _all;

    public static IReadOnlyList<CardModel> All => _all ??= new List<CardModel>
    {{
{main_entries}
    }};
}}
'''

    clusters: dict[str, list[str]] = {}
    cards_by_id = {card["id"]: card for card in cards}
    for card_id, reason in blocked.items():
        clusters.setdefault(
            _kokomi_runtime_cluster(cards_by_id[card_id], reason),
            []).append(card_id)

    manifest = {
        "_comment": (
            "Generated by tools/gen_roster_cards.py from docs/kokomi-cards.yaml. "
            "Only cards whose complete runtime grammar is implemented are emitted. "
            "Blocked cards are not auto-registered or added to a partial pool."
        ),
        "profile": {
            "character": KOKOMI_PROFILE.character_id,
            "element": KOKOMI_PROFILE.native_element,
            "cadence": (
                "CATALYST (R52 ask N1): every Attack applies Hydro. Application "
                "uptime is structural, not authored per card."
            ),
            "namespace": KOKOMI_PROFILE.namespace,
        },
        "coverage": {
            "total": len(cards),
            "generated": len(main_generated_ids),
            "blocked": len(blocked),
        },
        "generated": sorted(main_generated_ids),
        "blocked": dict(sorted(blocked.items())),
        "runtime_clusters": {
            key: sorted(value) for key, value in sorted(clusters.items())
        },
        "upgrades": {
            "_comment": (
                "docs/kokomi-upgrades.yaml is authoritative. A generated card "
                "listed below ships without an upgrade until its full delta is "
                "expressible; partial upgrade application is forbidden."
            ),
            "no_upgrade_path": dict(sorted(no_upgrade.items())),
        },
    }
    manifest_src = json.dumps(manifest, indent=2) + NEWLINE

    if check:
        stale = []
        for card_id, source in generated.items():
            path = KOKOMI_PROFILE.out_dir / f"{pascal(card_id)}.cs"
            if not path.exists() or path.read_text(encoding="utf-8") != source:
                stale.append(card_id)
        expected_files = {f"{pascal(card_id)}.cs" for card_id in generated}
        actual_files = {
            path.name for path in KOKOMI_PROFILE.out_dir.glob("*.cs")
        } if KOKOMI_PROFILE.out_dir.exists() else set()
        extra_files = sorted(actual_files - expected_files)
        manifest_stale = (
            not KOKOMI_PROFILE.manifest.exists()
            or KOKOMI_PROFILE.manifest.read_text(encoding="utf-8")
            != manifest_src
        )
        if stale or extra_files or manifest_stale:
            if stale:
                print(
                    f"stale Kokomi generated cards: {', '.join(sorted(stale))}",
                    file=sys.stderr,
                )
            if extra_files:
                print(
                    f"stale Kokomi generated files: {', '.join(extra_files)}",
                    file=sys.stderr,
                )
            if manifest_stale:
                print("stale Kokomi generated manifest", file=sys.stderr)
            return 1
        print("gen_roster_cards: kokomi up to date")
        return 0

    KOKOMI_PROFILE.out_dir.mkdir(parents=True, exist_ok=True)
    for old in KOKOMI_PROFILE.out_dir.glob("*.cs"):
        old.unlink()
    for card_id, source in generated.items():
        path = KOKOMI_PROFILE.out_dir / f"{pascal(card_id)}.cs"
        path.write_text(source, encoding="utf-8")
    KOKOMI_PROFILE.manifest.write_text(manifest_src, encoding="utf-8")

    print(
        f"kokomi: generated {len(main_generated_ids)} cards, "
        f"blocked {len(blocked)}"
    )
    for cluster, card_ids in sorted(clusters.items()):
        print(f"  {cluster}: {len(card_ids)}")
    return 0


def _kokomi_runtime_cluster(card: dict, reason: str) -> str:
    """Group blockers by the RUNTIME SYSTEM they wait on, not by card.

    The cluster name is what tells a reader whether the gap is one afternoon
    of work or a system nobody has built -- "12 cards blocked" says nothing,
    "12 cards blocked on the ward" says exactly what to do next.
    """
    # Hand-written first, for the same reason as Furina's mapper: it is a
    # finished decision, not a coverage gap, and every ops-based rule below
    # would happily reclaim it into a workstream that has nothing left to do.
    # ceremonial_garment trips `charge_engine` on exactly this path.
    if reason == "hand-written":
        return "hand_written"
    ops = {eff.get("op") for eff in card.get("effects", [])}
    powers = {eff.get("power") for eff in card.get("effects", [])
              if eff.get("op") == "apply_power"}
    if "prevent_exhaust_ward" in powers:
        return "prevention_ward"
    if {"conscript"} & ops:
        return "conscript"
    if {"gain_charge", "summon_kurage"} & ops:
        return "charge_engine"
    if "sly" in str(card.get("tags", [])):
        return "sly_discard"
    if reason.startswith("kit card"):
        return "kit_burst"
    return "shared_emitter_gap"


def main(
    argv: list[str] | None = None, *, default_character: str = "klee"
) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--check", action="store_true", help="fail if output would change"
    )
    ap.add_argument(
        "--character",
        choices=(*PROFILES, "all"),
        default=default_character,
        help="character profile to generate (legacy script defaults to klee)",
    )
    args = ap.parse_args(argv)

    results = []
    if args.character in ("klee", "all"):
        results.append(_run_klee(args.check))
    if args.character in ("furina", "all"):
        results.append(_run_furina(args.check))
    if args.character in ("kokomi", "all"):
        results.append(_run_kokomi(args.check))
    return max(results, default=0)


if __name__ == "__main__":
    raise SystemExit(main())
