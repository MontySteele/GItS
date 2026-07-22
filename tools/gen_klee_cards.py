#!/usr/bin/env python3
"""
Emit C# card classes for Klee from the canonical YAML design sheet.

The sheet (docs/klee-cards.yaml) is the single source of truth through
implementation, per spec C2. This script owns the mechanical subset of it --
cards whose whole behaviour is damage / block / draw / self-HP-loss -- and
refuses to guess at anything else.

WHAT IT DELIBERATELY WILL NOT DO
--------------------------------
Cards with bombs, sparks, burst energy, conditionals, X costs, or formula-driven
values are NOT emitted. They depend on systems that do not exist yet, and a
generator that emits a plausible-looking wrong body is worse than one that emits
nothing: the C# would compile, ship, and silently misplay. Those cards are
listed in the manifest with the op that blocked them, and are hand-finished.

Every emitted file carries a DO-NOT-EDIT header naming this script and the
sheet, so a hand edit is visibly wrong rather than quietly lost on regen.

Usage:  python tools/gen_klee_cards.py [--check]
        --check exits nonzero if regenerating would change anything (CI guard).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
SHEET = REPO / "docs" / "klee-cards.yaml"
# Mirrors tier0/content/upgrades.py UPGRADE_SHEETS, in the same order.
UPGRADE_SHEETS = (REPO / "docs" / "klee-upgrades.yaml",
                  REPO / "docs" / "furina-upgrades.yaml")

# Companion sheets -> home nation. The nation is what the reward slot's
# SAME_NATION_REWARD_SHARE weighting keys on, and tier0's loader derives it
# from the sheet FILENAME (loader.py: `nation = sheet.split("-", 1)[0]`), so
# the mapping is stated once here rather than re-derived per card.
#
# Fontaine entered Klee's slot by user ruling (2026-07-21): "it's probably
# best to have some non-Mondstadt cards in the pool to make sure Klee doesn't
# inadvertently overperform with a 100% Mondstadt roster."
COMPANION_SHEETS = ((REPO / "docs" / "mondstadt-companions.yaml", "mondstadt"),
                    (REPO / "docs" / "fontaine-companions.yaml", "fontaine"))
OUT_DIR = REPO / "klee-mod" / "KleeCode" / "Cards" / "Generated"
MANIFEST = REPO / "klee-mod" / "KleeCode" / "Cards" / "Generated" / "manifest.json"

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
                  "apply_power", "discard", "discard_for_sparks",
                  "detonate", "move_bombs", "modify_bombs",
                  "chance_bomb_per_detonation", "conditional",
                  "energy", "scry_discard", "add_card", "exhaust_from",
                  "apply_aura", "swirl", "buff_next_attack", "block_next_turn",
                  "cost_mod", "copy_companion_in_hand",
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
ADD_CARD_FIELDS = {"op", "card", "card_id", "pool", "zone", "to", "amount",
                   "cost_override"}
ENERGY_FIELDS = {"op", "amount"}
SCRY_FIELDS = {"op", "amount"}
# exhaust_from: dodge_roll's shape only -- a random Status from hand. The
# filterless form (kit-exempt any-card) blocks until a card needs it.
EXHAUST_FROM_FIELDS = {"op", "zone", "filter", "amount"}

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
}

# The if-clause each predicate renders on the card.
PREDICATE_TEXT = {
    "this_cost_zero": "If this cost 0",
    "has_spark": "If you have [gold]Spark[/gold]",
    "reaction_triggered_by_this": "If it triggered an [gold]Elemental Reaction[/gold]",
    "reaction_triggered_this_turn": "If an [gold]Elemental Reaction[/gold] triggered this turn",
    "killed_target": "If it kills",
}

CONDITIONAL_FIELDS = {"op", "if", "then", "else"}

# Ops legal inside a conditional branch: plain resolvers with literal (or
# delta-var) amounts and no local declarations outside their own braces.
# repeat_this is legal ONLY as a conditional's entire then-branch.
BRANCH_OPS = {"damage", "block", "draw", "gain_spark", "place_bomb", "burst_energy",
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
# stack cap or None, card-text template with {X} for the amount).
#
# The cap is DOUBLE-ENTERED deliberately: the C# class enforces it in
# TryModifyPowerAmountReceived (the sim clamps in powers.py apply_power), and
# codegen cross-checks the sheet's max_stacks against this table so cap drift
# between sheet and C# fails the regen loudly instead of shipping.
#
# sparks_n_splash is deliberately ABSENT: the Burst kit card lands LAST in
# the power-card pass (standing plan) with its own cost/grant machinery.
APPLY_POWERS = {
    "bomb_damage_up": ("BombDamageUpPower", 4,
        "Your [gold]Bombs[/gold] detonate for {X} more damage. (Max 4.)"),
    "zero_cost_attacks_up": ("ZeroCostAttacksUpPower", 4,
        "Your Attacks that cost 0 deal {X} more damage. (Max 4.)"),
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
    "bomb_and_spark_per_turn": ("BombAndSparkPerTurnPower", 1,
        "At the start of your turn, place a 5-damage [gold]Bomb[/gold] on a "
        "random enemy and gain {X} [gold]Spark[/gold]."),
    # Native debuffs (weak/vulnerable batch, 2026-07-20). Semantics verified
    # against the decompiled core: WeakPower x0.75 dealt / VulnerablePower
    # x1.5 taken, Counter stacks, tick at enemy side turn end -- exactly
    # tier0's WEAK_DEALT_MULT / VULNERABLE_TAKEN_MULT and DECAYING rule.
    # No cap either side. {TO} renders the target clause (build_description).
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
        "[gold]Vaporize[/gold] and [gold]Melt[/gold] amplify {X}% more. "
        "At the end of your turn, deal 4 damage and apply [gold]Pyro[/gold] "
        "to a random enemy."),
    "celestial_gift": ("CelestialGiftPower", None,
        "Your Attacks deal {X} more damage. At the start of your turn, "
        "gain 4 [gold]Block[/gold]."),
    "solar_isotoma": ("SolarIsotomaPower", None,
        "For {X} turns: your Attacks against enemies holding an elemental "
        "aura grant 3 [gold]Block[/gold] per hit."),
    "attack_up_this_turn": ("AttackUpThisTurnPower", None,
        "Your Attacks deal {X} more damage this turn."),
    # Fontaine (2026-07-21 ruling). shatter_bonus is a flat rider the sim adds
    # inside the Shatter's raw HP subtraction, so FrozenPower reads it there.
    "shatter_bonus": ("ShatterBonusPower", None,
        "Your [gold]Shatters[/gold] deal {X} more damage."),
}

# Powers applied to ENEMIES (native debuffs). Everything else in APPLY_POWERS
# is a self power; blocked_reason enforces the split both ways.
ENEMY_APPLY_POWERS = {"weak", "vulnerable"}

# Sheet fields apply_power may carry. Anything else encodes a mechanic this
# generator does not understand -- fail loudly (UNPARSEABLE discipline).
APPLY_POWER_FIELDS = {"op", "power", "amount", "target", "max_stacks", "note",
                      "splash_procs_per_turn",
                      # Companion sheet annotations (oz/albedo): the summon's
                      # element and aura consumption live in the POWER's C#
                      # implementation; the fields are documentation.
                      "summon_element", "consumes_aura"}

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
EXPRESSIBLE_DELTAS = ({"damage", "block", "draw", "spark", "bomb_damage", "burst_energy", "cost",
                       "discard", "sparks", "innate", "bonus", "chance",
                       "conditional_bonus", "condition", "bombs",
                       "bonus_per_detonation", "cards", "remove",
                       "copy_cost_override", "add"}
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


def _x_expr(val, bombs_var: bool = False) -> str:
    """C# expression for a tier0 amount formula ('x' is ResolveEnergyXValue,
    declared at the top of OnPlay)."""
    if val == "X":
        return "x"
    n = int(val[len("X_plus_"):])
    if bombs_var:
        return 'x + DynamicVars["Bombs"].IntValue'
    return f"x + {n}"


def blocked_reason(card: dict) -> str | None:
    """Return why this card cannot be generated, or None if it can."""
    if card["id"] in HAND_WRITTEN:
        return "hand-written"

    if is_companion(card):
        # Companions apply their element via the card-level IElementalCard,
        # so mixed elemental/non-elemental damage on one card cannot be
        # expressed (tier0 reads applies_element per effect).
        applies = {bool(e.get("applies_element"))
                   for e in card.get("effects", []) if e.get("op") == "damage"}
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
                    and bf.partition("_per_")[0].isdigit()):
                # The Big One's grammar; the fanfare variant is Furina-stream.
                return f"bonus_formula '{bf}'"
            if "bonus_vs_bombed" in eff or "bonus_vs_aura" in eff:
                return "conditional damage bonus (needs aura/bomb systems)"
            times = eff.get("times", 1)
            if not isinstance(times, int) and _x_formula_reason(card, times):
                return _x_formula_reason(card, times)
        if op == "place_bomb":
            if eff.get("target") not in BOMB_TARGETS:
                return f"bomb target '{eff.get('target')}'"
            amt = eff.get("amount")
            if not isinstance(amt, int) and _x_formula_reason(card, amt):
                return _x_formula_reason(card, amt)
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
            if power not in APPLY_POWERS:
                return f"apply_power power '{power}' (no PowerModel in the registry)"
            if power in ENEMY_APPLY_POWERS:
                # Native debuffs aim at enemies (tier0 _op_apply_power ->
                # _pick_targets). random targeting has no verified idiom yet.
                if eff.get("target") not in ("enemy", "all_enemies"):
                    return (f"apply_power target '{eff.get('target')}' "
                            f"for enemy debuff '{power}'")
            elif eff.get("target") != "self":
                return f"apply_power target '{eff.get('target')}' (self power aimed at enemies)"
            unknown = set(eff) - APPLY_POWER_FIELDS
            if unknown:
                # UNPARSEABLE discipline: an unrecognized field encodes a
                # mechanic; block loudly, never approximate.
                return f"apply_power field(s) {sorted(unknown)} not understood"
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
            if eff.get("zone") != "hand":
                return f"exhaust_from zone '{eff.get('zone')}'"
            if eff.get("filter") != "status":
                return "exhaust_from without status filter (any-card pool not built)"
            if eff.get("amount", 1) != 1:
                return "exhaust_from amount > 1 (re-pool loop not built)"
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
        if op == "conditional":
            unknown = set(eff) - CONDITIONAL_FIELDS
            if unknown:
                return f"conditional field(s) {sorted(unknown)} not understood"
            if eff.get("if") not in PREDICATES_CS:
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
                    "burst_energy": {"op", "amount"},
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


def build_vars(card: dict) -> list[str]:
    """DynamicVar declarations, in the order the effects use them."""
    out = []
    for eff in card["effects"]:
        op = eff["op"]
        # Constructor shapes differ per var and are NOT uniform: DamageVar and
        # BlockVar take (decimal, ValueProp); CardsVar takes a bare int;
        # HpLossVar takes a bare decimal. Verified against the decompiled
        # sts2 sources -- assuming a uniform shape here does not compile.
        if op == "damage" and eff["target"] == "self":
            out.append(f'new HpLossVar({eff["amount"]}m)')
        elif op == "damage":
            out.append(f'new DamageVar({eff["amount"]}m, ValueProp.Move)')
            if "bonus_formula" in eff and bonus_per_upgrade(card):
                n = int(eff["bonus_formula"].partition("_per_")[0])
                out.append(f'new DynamicVar("BonusPer", {n}m)')
        elif op == "block":
            out.append(f'new BlockVar({eff["amount"]}m, ValueProp.Move)')
        elif op == "draw":
            out.append(f'new CardsVar({int(eff["amount"])})')
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
        elif op == "burst_energy" and burst_upgrade(card):
            # Same rule as Sparks: a var only when the upgrade must render.
            out.append(f'new DynamicVar("BurstEnergy", {int(eff["amount"])}m)')
        elif op in POWER_UPGRADE_OPS and power_upgrade(card):
            # Same rule again: only an upgradeable amount needs a var. The
            # sim binds these deltas to the FIRST top-level apply_power or
            # buff_next_attack, and build_vars only walks top level, so a
            # conditional rider never claims the var.
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
            for e in eff.get("then", []):
                if e["op"] == "damage" and cb:
                    out.append(f'new ExtraDamageVar({e["amount"]}m)')
                    cb = 0                       # first damage only
                elif e["op"] == "draw" and bd:
                    out.append(f'new CardsVar({int(e["amount"])})')
            for e in eff.get("else", []):
                if e["op"] == "draw" and bd:
                    out.append(f'new DynamicVar("DrawElse", {int(e["amount"])}m)')
    if added_draw_upgrade(card):
        out.append(f"new CardsVar({added_draw_upgrade(card)})")
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
                                  for e in effects),
        "spark": any(e["op"] == "gain_spark" for e in effects),
        "bomb_damage": any(e["op"] == "place_bomb" for e in effects),
        "burst_energy": any(e["op"] == "burst_energy" for e in effects),
        "cost": str(card.get("cost")) != "X",
        # R36: both keys ride the one discard_for_sparks effect.
        "discard": any(e["op"] == "discard_for_sparks" for e in effects),
        "sparks": any(e["op"] == "discard_for_sparks" for e in effects),
        # R37: card-level, any card can become Innate.
        "innate": True,
        # Bomb-op batch: bonus rides a bonus-carrying bomb op; chance is
        # the chance_bomb_per_detonation replacement.
        "bonus": any(e["op"] in BONUS_OPS and "bonus" in e for e in effects),
        "chance": any(e["op"] == "chance_bomb_per_detonation" for e in effects),
        # Structural `add` upgrades currently support one exact, verified
        # shape: append a draw effect. It is emitted as an IsUpgraded-gated
        # draw at the end of OnPlay, matching upgrades.py's list append.
        "add": True,
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
                    and value.get("op") == "draw"
                    and isinstance(value.get("amount"), int)
                    and value["amount"] > 0):
                return {}, f"delta 'add: {value}' (only a positive draw effect is expressible)"
            if any(e.get("op") == "draw" for e in everywhere):
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
    return int(added["amount"]) if isinstance(added, dict) else 0


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


def branch_draw_upgrade(card: dict) -> int:
    """Ruled `draw: +N` when the card's draws live inside conditional
    branches (eager_to_help). tier0 bumps ALL draw ops; the branch draws ride
    the Cards (then) and DrawElse (else) vars. A card with BOTH a top-level
    draw and branch draws would need three vars -- loud stop until real."""
    delta = int(upgrade_plan(card)[0].get("draw", 0))
    if not delta:
        return 0
    branch_draws = [e for e in _effects_everywhere(card)
                    if e.get("op") == "draw"]
    top_draws = [e for e in card["effects"] if e.get("op") == "draw"]
    if len(branch_draws) > len(top_draws) and top_draws:
        raise SystemExit(
            f"gen_klee_cards: {card['id']}: draw delta with draws both at "
            "top level and inside branches -- var plan has no third name.")
    return delta if len(branch_draws) > len(top_draws) else 0


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
    if "times_formula" in eff:
        # 2_plus_sparks (Gleeful Barrage), the sim's only times formula.
        # SparksAtPlay: R39 (2026-07-21 ruling) -- the sim computes times from
        # state.sparks_at_play, the bank BEFORE this card's own spend, because
        # hitting the threshold that makes the card free was otherwise exactly
        # what deleted the sparks it counts.
        call.append(
            ".WithHitCount(2 + SparkPower.SparksAtPlay(Owner.Creature))")
    elif x_times:
        # times: "X" (fish_blasting). tier0 loops range(times): X = 0 means
        # NO hits, so the whole attack statement is gated below.
        call.append(f".WithHitCount({_x_expr(times)})")
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
    if x_times:
        stmt = ("if (x > 0)\n        {\n            "
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


def _emit_branch_op(card: dict, eff: dict, lines: list[str], ctx: dict,
                    in_then: bool, cb_state: dict) -> None:
    """Conditional-branch resolvers. Amounts are literals unless a ruled
    delta claims them (see build_vars): conditional_bonus -> then-first
    damage via ExtraDamage; draw delta -> Cards (then) / DrawElse (else)."""
    op = eff["op"]
    if op == "damage":
        if in_then and cb_state.get("pending"):
            cb_state["pending"] = False
            _emit_damage(card, eff, lines, ctx, "DynamicVars.ExtraDamage.BaseValue")
        else:
            _emit_damage(card, eff, lines, ctx, f'{int(eff["amount"])}m')
    elif op == "block":
        lines.append(
            "await CreatureCmd.GainBlock(Owner.Creature, "
            f'new BlockVar({int(eff["amount"])}m, ValueProp.Move), cardPlay);'
        )
    elif op == "draw":
        if branch_draw_upgrade(card):
            expr = ("DynamicVars.Cards.BaseValue" if in_then
                    else 'DynamicVars["DrawElse"].IntValue')
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


def build_body(card: dict) -> list[str]:
    """OnPlay statements. Every call here has a verified base-game call site."""
    lines = []
    ctx = {"thrown": False}
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
            lines.append(
                "await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block, cardPlay);"
            )

        elif op == "draw":
            lines.append(
                "await CardPileCmd.Draw(choiceContext, DynamicVars.Cards.BaseValue, Owner);"
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
            amount_expr = "DynamicVars.Damage.BaseValue"
            if "bonus_formula" in eff:
                # N_per_detonation_this_combat (The Big One): flat rider on
                # the printed number, before external buffs -- adding into
                # the Attack amount is exactly the sim's `base +=`.
                per = ('DynamicVars["BonusPer"].IntValue'
                       if bonus_per_upgrade(card)
                       else eff["bonus_formula"].partition("_per_")[0])
                amount_expr += (f" + {per} * "
                                "BombPower.DetonationsThisCombat(CombatState!)")
            _emit_damage(card, eff, lines, ctx, amount_expr)

        elif op == "gain_spark":
            lines.append(_stmt_gain_spark(card, eff))

        elif op == "burst_energy":
            lines.append(_stmt_burst_energy(card, eff))

        elif op == "apply_power":
            cls = APPLY_POWERS[eff["power"]][0]
            amount = (
                'DynamicVars["PowerAmount"].IntValue'
                if power_upgrade(card)
                else str(int(eff["amount"]))
            )
            # Stack caps are enforced by the power's own
            # TryModifyPowerAmountReceived (the sim clamps at apply too), so
            # the call site stays a plain Apply.
            if eff["power"] in ENEMY_APPLY_POWERS:
                # tier0 _op_apply_power -> _pick_targets: chosen enemy or
                # every living enemy. Native debuff classes; applier is us.
                if eff["target"] == "enemy":
                    _target_guard(lines, ctx)
                    lines.append(
                        f"await PowerCmd.Apply<{cls}>(choiceContext, cardPlay.Target, "
                        f"{amount}, applier: Owner.Creature, cardSource: this);"
                    )
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
            n = int(eff.get("amount", 1))
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
            lines.append(
                "foreach (var companionId in CompanionPlays.PlayedThisCombat(CombatState!))\n"
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
            if tgt == "enemy":
                _target_guard(lines, ctx)
                lines.append(
                    f"await ElementalHit.ApplyOnly(choiceContext, cardPlay.Target, "
                    f"{element}, Owner.Creature);"
                )
            elif tgt == "all_enemies":
                lines.append(
                    "foreach (var auraTarget in CombatState!.HittableEnemies.ToList())\n"
                    "        {\n"
                    f"            await ElementalHit.ApplyOnly(choiceContext, auraTarget, "
                    f"{element}, Owner.Creature);\n"
                    "        }"
                )
            else:  # random_enemy
                lines.append(
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

        elif op == "buff_next_attack":
            # tier0 _op_buff_next_attack -> next_attack_up, consumed by the
            # next attack card (NextAttackUpPower's AfterCardPlayed).
            amount = ('DynamicVars["PowerAmount"].IntValue'
                      if power_upgrade(card) else str(int(eff["amount"])))
            lines.append(
                f"await PowerCmd.Apply<NextAttackUpPower>(choiceContext, "
                f"Owner.Creature, {amount}, "
                "applier: Owner.Creature, cardSource: this);"
            )

        elif op == "block_next_turn":
            # tier0 _op_block_next_turn: a power the sim POPS at the next
            # player turn start, granting the Block after that turn's reset.
            lines.append(
                f"await PowerCmd.Apply<BlockNextTurnPower>(choiceContext, "
                f'Owner.Creature, {int(eff["amount"])}, '
                "applier: Owner.Creature, cardSource: this);"
            )

        elif op == "energy":
            # tier0 _op_energy: flat gain, no cap (the game clamps nothing
            # either -- PlayerCmd.GainEnergy is the base-game call).
            lines.append(f'await PlayerCmd.GainEnergy({int(eff["amount"])}, Owner);')

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

        elif op == "conditional":
            then = eff.get("then", [])
            if any(e.get("op") == "repeat_this" for e in then):
                # Evaluated at the conditional's position (sim: the predicate
                # reads counters as of this point in the effect list); the
                # replay itself lands after the list (repeat tail below).
                times = int(then[0].get("times", 1))
                lines.append(
                    f"var repeatTimes = ({PREDICATES_CS[eff['if']]}) ? {times} : 0;"
                )
            else:
                pred = PREDICATES_CS[eff["if"]]
                if condition_upgrade(card):
                    # condition: unconditional (tier0 hoists the then-branch
                    # on upgrade) -- the upgraded card runs it always.
                    pred = f"IsUpgraded || {pred}"
                cb_state = {"pending": conditional_bonus_upgrade(card) > 0}
                then_lines: list[str] = []
                for e in then:
                    _emit_branch_op(card, e, then_lines, ctx, True, cb_state)
                else_lines: list[str] = []
                for e in eff.get("else", []):
                    _emit_branch_op(card, e, else_lines, ctx, False, cb_state)
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
                var = "Cards" if in_then else "DrawElse"
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
    for eff in card["effects"]:
        op = eff["op"]

        if op == "block":
            parts.append("Gain {Block:diff()} [gold]Block[/gold].")

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
            parts.append("Draw {Cards:diff()} card{Cards:plural:|s}.")

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
            if isinstance(times, str):        # times: "X"
                suffix = " X times"
                times = 2                     # phrasing: plural targets
            else:
                suffix = {1: "", 2: " twice", 3: " three times", 4: " four times"}.get(
                    times, f" {times} times"
                )
            if target == "enemy":
                parts.append(f"Deal {{Damage:diff()}} damage{suffix}.")
            elif target == "all_enemies":
                parts.append(f"Deal {{Damage:diff()}} damage to ALL enemies{suffix}.")
            else:
                plural = "random enemies" if times > 1 else "a random enemy"
                parts.append(f"Deal {{Damage:diff()}} damage to {plural}{suffix}.")
            if "bonus_formula" in eff:
                per = ("{BonusPer:diff()}" if bonus_per_upgrade(card)
                       else eff["bonus_formula"].partition("_per_")[0])
                parts.append(
                    f"+{per} damage per [gold]Bomb[/gold] detonated this combat.")

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

        elif op == "apply_power":
            template = APPLY_POWERS[eff["power"]][2]
            x = ("{PowerAmount:diff()}" if power_upgrade(card)
                 else str(int(eff["amount"])))
            to = " to ALL enemies" if eff.get("target") == "all_enemies" else ""
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

        elif op == "buff_next_attack":
            n = ("{PowerAmount:diff()}" if power_upgrade(card)
                 else str(int(eff["amount"])))
            parts.append(f"Your next Attack deals {n} more damage.")

        elif op == "energy":
            n = int(eff["amount"])
            parts.append(f"Gain {n} Energy.")

        elif op == "scry_discard":
            parts.append(
                f'Look at the top {int(eff["amount"])} cards of your draw '
                "pile; discard one.")

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
            pred_txt = PREDICATE_TEXT[eff["if"]]
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

    return " ".join(parts)


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
    key_for = {"block": "block", "draw": "draw", "gain_spark": "spark", "place_bomb": "bomb_damage",
               "burst_energy": "burst_energy"}
    var_for = {"block": "DynamicVars.Block", "draw": "DynamicVars.Cards", "gain_spark": 'DynamicVars["Sparks"]',
               "burst_energy": 'DynamicVars["BurstEnergy"]', "apply_power": 'DynamicVars["PowerAmount"]',
               "buff_next_attack": 'DynamicVars["PowerAmount"]'}
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
            key = next((k for k in POWER_UPGRADE_KEYS if k in deltas), None)
        elif op == "damage" and eff["target"] != "self":
            key = "damage"
        else:
            key = key_for.get(op)
        if key is None or key not in deltas or key in done:
            continue
        done.add(key)
        var = "DynamicVars.Damage" if key == "damage" else (
            f"DynamicVars.{bomb_var(card)}" if key == "bomb_damage" else var_for[op])
        lines.append(f"{var}.UpgradeValueBy({int(deltas[key])}m);")
    if "conditional_bonus" in deltas:
        # tier0: bump the then-branch's first damage (the ExtraDamage var;
        # expressibility gated in upgrade_plan/conditional_bonus_upgrade).
        lines.append(
            f'DynamicVars.ExtraDamage.UpgradeValueBy({int(deltas["conditional_bonus"])}m);')
    if branch_draw_upgrade(card):
        # tier0 draw deltas bump ALL draw ops, branches included.
        d = int(deltas["draw"])
        lines.append(f"DynamicVars.Cards.UpgradeValueBy({d}m);")
        lines.append(f'DynamicVars["DrawElse"].UpgradeValueBy({d}m);')
    if "condition" in deltas:
        lines.append(
            "// condition: unconditional -- expressed at play time as "
            "(IsUpgraded || predicate); the text swaps via {IfUpgraded:show:...}.")
    if "bombs" in deltas:
        lines.append(f'DynamicVars["Bombs"].UpgradeValueBy({int(deltas["bombs"])}m);')
    if "bonus_per_detonation" in deltas:
        lines.append(
            f'DynamicVars["BonusPer"].UpgradeValueBy({int(deltas["bonus_per_detonation"])}m);')
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
    if "add" in deltas:
        lines.append(
            "// add: draw -- expressed at play time as an IsUpgraded-gated "
            "draw appended after the base effects.")
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
    return lines


def emit(card: dict) -> str:
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
        elemental = is_attack
        element_cs = "Element.Pyro"

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
        source_element = card["element"] if is_companion(card) else "pyro"
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
    body = build_body(card)
    upgrade = build_upgrade(card)
    _, no_upgrade_reason = upgrade_plan(card)
    desc = build_description(card)

    interfaces = "CustomCardModel"
    if elemental:
        interfaces += ", IElementalCard"
    if is_companion(card):
        interfaces += ", ICompanionCard"
    # Sheet `skill_tag` -> ISkillTagCard: worth BURST_PER_SKILL_TAG burst
    # energy when played (KleeElementalHooks.AfterCardPlayed reads the marker).
    if "skill_tag" in card.get("tags", []):
        interfaces += ", ISkillTagCard"

    ind = "\n        "
    vars_cs = (",".join(f"{ind}    {v}" for v in vars_)).lstrip()
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

    element_member = ""
    if elemental and is_companion(card):
        element_member = (
            "\n    /// <summary>Sheet applies_element: this companion attack applies its element.</summary>\n"
            f"    public Element Element => {element_cs};\n"
        )
    elif elemental:
        element_member = (
            "\n    /// <summary>Sheet: all Klee attacks apply Pyro (catalyst-grade cadence).</summary>\n"
            "    public Element Element => Element.Pyro;\n"
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
    if "skill_tag" in card.get("tags", []):
        keywords.append("KleeKeywords.ElementalSkill")
    keywords.extend(aura_keyword_by_element[e] for e in aura_elements)
    keywords_member = ""
    if keywords:
        keywords_member = (
            "\n    public override IEnumerable<CardKeyword> CanonicalKeywords =>\n"
            "        new[] { " + ", ".join(keywords) + " };\n"
        )

    tooltip_member = ""
    if preview_element_cs is not None or includes_bomb_rules:
        trigger_arg = preview_element_cs or "Element.None"
        bomb_arg = "true" if includes_bomb_rules else "false"
        tooltip_member = (
            "\n    protected override IEnumerable<IHoverTip> ExtraHoverTips =>\n"
            "        KleeCardTooltips.ForCard(base.ExtraHoverTips, this, "
            f"{trigger_arg}, includesBombRules: {bomb_arg});\n"
        )
    hover_using = (
        "\nusing MegaCrit.Sts2.Core.HoverTips;" if tooltip_member else "")

    return f'''// <auto-generated>
//     Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml.
//     DO NOT EDIT. Edits are lost on the next regen -- change the sheet instead.
//
//     Sheet entry: id={card["id"]} rarity={card["rarity"]} cost={card["cost"]}
//     Upgrade deltas come from docs/klee-upgrades.yaml (R24 2026-07-20: the
//     upgrades sheet is the single source of truth; codegen defaults abolished).
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
using KleeMod.Powers;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;{hover_using}
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards.Generated;

public sealed class {cls} : {interfaces}
{{{element_member}{keywords_member}{tooltip_member}
    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("{card["id"]}");

    public override List<(string, string)>? Localization => new()
    {{
        ("title", "{card["name"].replace('"', chr(92) + chr(34))}"),
        ("description", "{desc}"),
    }};

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {{
            {vars_cs}
        }};

    // autoAdd: false -- KleeCardPool declares pool membership itself in
    // GenerateAllCards. BaseLib's auto-registration would need a [Pool]
    // attribute and would register every card a second time.
    public {cls}()
        : base({0 if str(card["cost"]) == "X" else card["cost"]}, {TYPE_CS[card["type"]]}, {RARITY_CS[card["rarity"]]}, {target_type}, autoAdd: false)
    {{
    }}

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {{
        {body_cs}
    }}

    protected override void OnUpgrade()
    {{
        {upgrade_cs}
    }}
}}
'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if output would change")
    args = ap.parse_args()

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

    if args.check:
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


if __name__ == "__main__":
    raise SystemExit(main())
