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
OUT_DIR = REPO / "klee-mod" / "KleeCode" / "Cards" / "Generated"
MANIFEST = REPO / "klee-mod" / "KleeCode" / "Cards" / "Generated" / "manifest.json"

# Ops this generator can express with verified Cmd APIs. Anything else blocks
# the card. Keep this set honest -- widening it without a verified call site is
# how we ship silently-wrong cards.
MECHANICAL_OPS = {"damage", "block", "draw"}

# Damage targets we have a confirmed builder for (see AttackCommand).
DAMAGE_TARGETS = {"enemy", "all_enemies", "random_enemy", "random_enemies", "self"}

# Cards already hand-written; never overwrite them.
HAND_WRITTEN = {"kaboom", "duck_and_cover", "jumpy_dumpty", "pop"}

# Upgrade deltas are NOT in the sheet. These are codegen defaults, flagged in
# the manifest for design triage -- they are a placeholder for a ruling, not a
# ruling. Matches the hand-written basics (Kaboom +3, Duck and Cover +3).
UPGRADE_DAMAGE_SINGLE = 3
UPGRADE_DAMAGE_MULTI = 2  # aoe or multi-hit: +N applies per hit, so smaller
UPGRADE_BLOCK = 3
UPGRADE_DRAW = 1

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

    if card.get("type") == "power":
        return "power card (needs a PowerModel, hand-finished)"

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
    return None


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
    return out


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
            n = eff["amount"]
            parts.append("Draw {Cards:diff()} card." if n == 1 else "Draw {Cards:diff()} cards.")

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

    return " ".join(parts)


def build_upgrade(card: dict) -> list[str]:
    lines = []
    for eff in card["effects"]:
        op = eff["op"]
        if op == "block":
            lines.append(f"DynamicVars.Block.UpgradeValueBy({UPGRADE_BLOCK}m);")
        elif op == "draw":
            lines.append(f"DynamicVars.Cards.UpgradeValueBy({UPGRADE_DRAW}m);")
        elif op == "damage" and eff["target"] != "self":
            multi = eff.get("times", 1) > 1 or eff["target"] in ("all_enemies", "random_enemies")
            delta = UPGRADE_DAMAGE_MULTI if multi else UPGRADE_DAMAGE_SINGLE
            lines.append(f"DynamicVars.Damage.UpgradeValueBy({delta}m);")
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

    vars_ = build_vars(card)
    body = build_body(card)
    upgrade = build_upgrade(card)
    desc = build_description(card)

    interfaces = "CustomCardModel"
    if elemental:
        interfaces += ", IElementalCard"

    ind = "\n        "
    vars_cs = (",".join(f"{ind}    {v}" for v in vars_)).lstrip()
    body_cs = ind.join(body)
    upgrade_cs = ind.join(upgrade) if upgrade else "// No upgrade defined by the sheet."

    element_member = ""
    if elemental:
        element_member = (
            "\n    /// <summary>Sheet: all Klee attacks apply Pyro (catalyst-grade cadence).</summary>\n"
            "    public Element Element => Element.Pyro;\n"
        )

    return f'''// <auto-generated>
//     Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml.
//     DO NOT EDIT. Edits are lost on the next regen -- change the sheet instead.
//
//     Sheet entry: id={card["id"]} rarity={card["rarity"]} cost={card["cost"]}
//     Upgrade values are a CODEGEN DEFAULT, not a design ruling; the sheet does
//     not specify them. See tools/gen_klee_cards.py.
// </auto-generated>

// Roslyn treats <auto-generated> files as outside the project's nullable
// context, so the ? annotations below need it re-enabled explicitly (CS8669).
#nullable enable

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards.Generated;

public sealed class {cls} : {interfaces}
{{{element_member}
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

    generated, blocked = {}, {}
    for card in cards:
        reason = blocked_reason(card)
        if reason:
            blocked[card["id"]] = reason
        else:
            generated[card["id"]] = emit(card)

    manifest = {
        "_comment": (
            "Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml. "
            "'blocked' cards need systems or hand-finishing; the reason names what stopped codegen."
        ),
        "generated": sorted(generated),
        "blocked": dict(sorted(blocked.items())),
        "upgrade_defaults": {
            "_comment": "NOT from the sheet. Placeholder pending a design ruling.",
            "damage_single": UPGRADE_DAMAGE_SINGLE,
            "damage_multi": UPGRADE_DAMAGE_MULTI,
            "block": UPGRADE_BLOCK,
            "draw": UPGRADE_DRAW,
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
