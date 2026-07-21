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
UPGRADES_SHEET = REPO / "docs" / "klee-upgrades.yaml"
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
                  "chance_bomb_per_detonation"}

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
}

# Sheet fields apply_power may carry. Anything else encodes a mechanic this
# generator does not understand -- fail loudly (UNPARSEABLE discipline).
APPLY_POWER_FIELDS = {"op", "power", "amount", "target", "max_stacks", "note",
                      "splash_procs_per_turn"}

# Upgrade keys that all mean "bump the applied power amount" at card level
# (tier0 upgrades.py handles them in one branch too).
POWER_UPGRADE_KEYS = {"power_amount", "amp_percent", "splash_damage", "vulnerable"}

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
# Anything else (remove:, add:, condition:, ...) is structural and blocks the
# card's upgrade path until it is hand-finished or re-ruled numeric.
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
EXPRESSIBLE_DELTAS = ({"damage", "block", "draw", "spark", "bomb_damage", "burst_energy", "cost",
                       "discard", "sparks", "innate", "bonus", "chance"}
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


def blocked_reason(card: dict) -> str | None:
    """Return why this card cannot be generated, or None if it can."""
    if card["id"] in HAND_WRITTEN:
        return "hand-written"

    if str(card.get("cost")) == "X":
        return "X cost (needs energy-scaling support)"

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
            if "times_formula" in eff or "bonus_formula" in eff:
                return "formula-driven damage"
            if "bonus_vs_bombed" in eff or "bonus_vs_aura" in eff:
                return "conditional damage bonus (needs aura/bomb systems)"
        if op == "place_bomb":
            if eff.get("target") not in BOMB_TARGETS:
                return f"bomb target '{eff.get('target')}'"
            if not isinstance(eff.get("amount"), int):
                return "formula-driven bomb count"
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
            if eff.get("target") != "self":
                return f"apply_power target '{eff.get('target')}' (only self powers land this pass)"
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
    if sum(1 for e in card.get("effects", []) if e.get("op") == "detonate") > 1:
        return "two detonate effects on one card (count variable collision)"
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
        elif op == "block":
            out.append(f'new BlockVar({eff["amount"]}m, ValueProp.Move)')
        elif op == "draw":
            out.append(f'new CardsVar({int(eff["amount"])})')
        elif op == "place_bomb":
            if bomb_var(card) == "ExtraDamage":
                out.append(f'new ExtraDamageVar({eff["bomb_damage"]}m)')
            else:
                out.append(f'new DamageVar({eff["bomb_damage"]}m, ValueProp.Move)')
        elif op == "gain_spark" and spark_upgrade(card):
            # Only an upgradeable spark amount needs a var (the new value must
            # render); "Sparks" collides with no base-game var name. Cards
            # without a sheet upgrade keep the literal (see MECHANICAL_OPS).
            out.append(f'new DynamicVar("Sparks", {int(eff["amount"])}m)')
        elif op == "burst_energy" and burst_upgrade(card):
            # Same rule as Sparks: a var only when the upgrade must render.
            out.append(f'new DynamicVar("BurstEnergy", {int(eff["amount"])}m)')
        elif op == "apply_power" and power_upgrade(card):
            # Same rule again: only an upgradeable amount needs a var.
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
    return out


_upgrade_deltas: dict | None = None


def upgrade_deltas() -> dict:
    """Per-card delta maps from klee-upgrades.yaml (R20: the upgrades sheet is
    the only home for upgrade deltas; inline `upgrade:` keys block the card)."""
    global _upgrade_deltas
    if _upgrade_deltas is None:
        _upgrade_deltas = yaml.safe_load(UPGRADES_SHEET.read_text(encoding="utf-8")) or {}
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
    has = {
        "damage": any(e["op"] == "damage" and e["target"] != "self" for e in effects),
        "block": any(e["op"] == "block" for e in effects),
        "draw": any(e["op"] == "draw" for e in effects),
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
    }
    for pkey in POWER_UPGRADE_KEYS:
        has[pkey] = any(e["op"] == "apply_power" for e in effects)
    for key, value in deltas.items():
        if key not in EXPRESSIBLE_DELTAS:
            return {}, f"delta key '{key}: {value}' not expressible by codegen (structural upgrade)"
        if not has[key]:
            return {}, f"delta key '{key}' has no matching effect on this card (sheet/card mismatch)"
    return dict(deltas), None


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


def build_body(card: dict) -> list[str]:
    """OnPlay statements. Every call here has a verified base-game call site."""
    lines = []
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
            var = bomb_var(card)
            n = eff["amount"]
            dmg = f"(int)DynamicVars.{var}.BaseValue"

            if eff["target"] == "enemy":
                if not any("ThrowIfNull" in l for l in lines):
                    lines.append(
                        'ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");'
                    )
                place = (
                    f"await BombPower.Place(choiceContext, cardPlay.Target, {dmg}, "
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
                    f"            await BombPower.Place(choiceContext, bombTarget, {dmg}, "
                    "Owner.Creature, this);\n"
                    "        }"
                )

        elif op == "damage":
            times = eff.get("times", 1)
            target = eff["target"]

            call = ["await DamageCmd.Attack(DynamicVars.Damage.BaseValue)"]
            if times > 1:
                call.append(f".WithHitCount({times})")
            call.append(".FromCard(this)")

            if target == "enemy":
                # cardPlay.Target is nullable; a single-target card played with
                # no target is a bug in the caller, so fail loudly rather than
                # silently no-op. Mirrors the hand-written Kaboom.
                if not any("ThrowIfNull" in l for l in lines):
                    lines.append(
                        'ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");'
                    )
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

            lines.append("\n            ".join(call))

        elif op == "gain_spark":
            amount = (
                'DynamicVars["Sparks"].IntValue'
                if spark_upgrade(card)
                else str(int(eff["amount"]))
            )
            lines.append(
                f"await SparkPower.Gain(choiceContext, Owner.Creature, {amount}, this);"
            )

        elif op == "burst_energy":
            amount = (
                'DynamicVars["BurstEnergy"].IntValue'
                if burst_upgrade(card)
                else str(int(eff["amount"]))
            )
            lines.append(
                f"await KleeBurstResource.Gain(choiceContext, Owner.Creature, {amount}, this);"
            )

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
                if not any("ThrowIfNull" in l for l in lines):
                    lines.append(
                        'ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");'
                    )
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
            if not any("ThrowIfNull" in l for l in lines):
                lines.append(
                    'ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");'
                )
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

    return lines


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

        elif op == "draw":
            # {Cards:plural:|s} pluralizes off the LIVE value, so "Draw 1
            # card" correctly becomes "Draw 2 cards" after upgrade. This is
            # the token BaseLib's SimpleLoc pipeline generates for "card(s)"
            # in #-prefixed strings; we emit runtime form directly.
            parts.append("Draw {Cards:diff()} card{Cards:plural:|s}.")

        elif op == "place_bomb":
            var = bomb_var(card)
            n = eff["amount"]
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
            parts.append(template.replace("{X}", x))

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

        elif op == "discard":
            n = int(eff.get("amount", 1))
            parts.append(
                "Discard a random card." if n == 1
                else f"Discard {n} random cards."
            )

        elif op == "discard_for_sparks":
            if discard_upgrade(card) != (0, 0):
                parts.append(
                    "Discard {Discards:diff()} card{Discards:plural:|s}: gain "
                    "{Sparks:diff()} [gold]Spark{Sparks:plural:|s}[/gold] per "
                    "card discarded."
                )
            else:
                n, m = int(eff["amount"]), int(eff["sparks"])
                cards_w = "a card" if n == 1 else f"{n} cards"
                sparks_w = ("1 [gold]Spark[/gold]" if m == 1
                            else f"{m} [gold]Sparks[/gold]")
                parts.append(f"Discard {cards_w}: gain {sparks_w} per card discarded.")

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
               "burst_energy": 'DynamicVars["BurstEnergy"]', "apply_power": 'DynamicVars["PowerAmount"]'}
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
        if op == "apply_power":
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
    # attacks". Skills carry no element.
    elemental = is_attack

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

    vars_ = build_vars(card)
    body = build_body(card)
    upgrade = build_upgrade(card)
    _, no_upgrade_reason = upgrade_plan(card)
    desc = build_description(card)

    interfaces = "CustomCardModel"
    if elemental:
        interfaces += ", IElementalCard"
    # Sheet `skill_tag` -> ISkillTagCard: worth BURST_PER_SKILL_TAG burst
    # energy when played (KleeElementalHooks.AfterCardPlayed reads the marker).
    if "skill_tag" in card.get("tags", []):
        interfaces += ", ISkillTagCard"

    ind = "\n        "
    vars_cs = (",".join(f"{ind}    {v}" for v in vars_)).lstrip()
    body_cs = ind.join(body)
    upgrade_cs = (
        ind.join(upgrade)
        if upgrade
        else f"// R24: NO upgrade path -- {no_upgrade_reason}. Flagged in manifest."
    )

    element_member = ""
    if elemental:
        element_member = (
            "\n    /// <summary>Sheet: all Klee attacks apply Pyro (catalyst-grade cadence).</summary>\n"
            "    public Element Element => Element.Pyro;\n"
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
    keywords_member = ""
    if keywords:
        keywords_member = (
            "\n    public override IEnumerable<CardKeyword> CanonicalKeywords =>\n"
            "        new[] { " + ", ".join(keywords) + " };\n"
        )

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
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards.Generated;

public sealed class {cls} : {interfaces}
{{{element_member}{keywords_member}
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
        : base({card["cost"]}, {TYPE_CS[card["type"]]}, {RARITY_CS[card["rarity"]]}, {target_type}, autoAdd: false)
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

    manifest = {
        "_comment": (
            "Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml. "
            "'blocked' cards need systems or hand-finishing; the reason names what stopped codegen."
        ),
        "generated": sorted(generated),
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

    if args.check:
        stale = []
        for cid, src in generated.items():
            p = OUT_DIR / f"{pascal(cid)}.cs"
            if not p.exists() or p.read_text(encoding="utf-8") != src:
                stale.append(cid)
        if stale:
            print(f"stale generated cards: {', '.join(sorted(stale))}", file=sys.stderr)
            return 1
        print("gen_klee_cards: up to date")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Clear stale files so a card removed from the sheet does not linger.
    for old in OUT_DIR.glob("*.cs"):
        old.unlink()

    for cid, src in generated.items():
        (OUT_DIR / f"{pascal(cid)}.cs").write_text(src, encoding="utf-8")

    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

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
