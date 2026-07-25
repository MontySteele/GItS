#!/usr/bin/env python3
"""Parity lint: C# mirrored constants vs tier0, the single source of truth.

WHY THIS EXISTS. Every balance number in the mod lives twice -- once in
tier0 (constants.py, the character yamls) where it was MEASURED, and once in
C# where it is PLAYED. The C# copies carry doc comments swearing they mirror
the sim and must never be re-derived, and until now that promise was kept by
discipline alone. Discipline is not a gate: a sim-side retune that nobody
mirrors produces a mod that plays to numbers no simulation ever endorsed, and
it does so SILENTLY -- the build is green, the tests pass, the tuning report
describes a game nobody is playing.

There is no C# test project (and no cheap way to add one against a Godot game
assembly), so a running fixture is not available. This is the static form of
the same guarantee, and it is strictly the more valuable half: a fixture pins
behaviour at the numbers it was written with, while this pins the numbers
themselves against the model that chose them.

DISCIPLINE (tier0's UNAPPLIABLE, applied to linting). Every `public const int`
in the mod must be classified: either MIRRORED (with the tier0 expression it
copies, compared by value) or UNMIRRORED (with a written reason it has no sim
counterpart). A constant in neither map is a FINDING, not a skip. That is what
makes the lint survive contact with future work -- adding a C# balance number
forces a decision about where it came from, at the moment the author still
knows the answer.

Run: python tools/lint_constant_parity.py
Exit 1 with findings on stdout when a mirror has drifted or is unclassified.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import yaml  # noqa: E402

from tier0 import constants as C  # noqa: E402

CS_ROOT = REPO / "klee-mod" / "KleeCode"


def _char(name: str, key: str):
    """A value from a tier0 character sheet (burst_max and friends live there,
    not in constants.py, because they are per-character statline)."""
    path = REPO / "tier0" / "content" / "characters" / f"{name}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))[key]


def _salon(member: str, phase: str, key: str):
    """A number out of the SALON_MEMBERS table. Furina's members are typed, so
    their tick/bow numbers are table entries rather than named constants."""
    return C.SALON_MEMBERS[member][phase][key]


# --------------------------------------------------------------------------
# MIRRORED: C# constant -> the tier0 value it copies.
#
# The right-hand side is evaluated here, so this table doubles as the written
# record of WHERE each C# number came from -- which is the question that is
# expensive to answer six months later and free to answer today.
# --------------------------------------------------------------------------
def _ancient_hook(relic_id: str, hook: str) -> int:
    """A number out of tier05's ancient-relic table.

    Relic effects are DATA rather than named constants, so the sim's copy of an
    Ancient's number lives in tier05/content/relics.yaml. Reading it here is
    what makes a relic number mirrorable at all -- the alternative was to file
    every Ancient under UNMIRRORED as "the sim does not model relics", which
    stopped being true the day the starter-upgrade hook landed.
    """
    from tier05 import relics as _relics
    for fx in _relics.ancient_pool()[relic_id]["effects"]:
        if fx.get("hook") == hook:
            return int(fx["amount"])
    raise KeyError(f"{relic_id} has no {hook} effect")


MIRRORED: dict[str, object] = {
    # Klee's upgraded starter (Touch of Orobas -> Explosive Frags). The sim's
    # copy is a relic row, not a constant; see _ancient_hook.
    "ExplosiveFrags.OpeningSparks":
        _ancient_hook("touch_of_orobas_klee", "combat_start_spark"),
    # Shared elemental table (tier0/constants.py, reaction block).
    "ReactionConstants.AuraDurationTurns": C.AURA_DURATION_TURNS,
    "ReactionConstants.OverloadSplash": C.OVERLOAD_SPLASH,
    "ReactionConstants.OverloadWeak": C.OVERLOAD_WEAK,
    "ReactionConstants.SuperconductVuln": C.SUPERCONDUCT_VULN,
    "ReactionConstants.ElectroChargedDot": C.ELECTROCHARGED_DOT,
    "ReactionConstants.ElectroChargedDotTurns": C.ELECTROCHARGED_DOT_TURNS,
    "ReactionConstants.CrystallizeBlock": C.CRYSTALLIZE_BLOCK,
    "ReactionConstants.ShatterDamage": C.SHATTER_DAMAGE,
    "ReactionConstants.FrozenBossVuln": C.FROZEN_BOSS_VULN,
    "ReactionKitConstants.CatalyticBurstPerReaction":
        C.CATALYTIC_BURST_PER_REACTION,

    # Klee.
    "BurstConstants.PerSkillTag": C.BURST_PER_SKILL_TAG,
    "BurstConstants.PerReaction": C.BURST_PER_REACTION,
    "BurstConstants.KleeMax": _char("klee", "burst_max"),
    "KitBurstConstants.VolleyHits": C.SPARKS_N_SPLASH_HITS,
    "KitBurstConstants.VolleyHitDamage": C.SPARKS_N_SPLASH_HIT_DMG,
    "SparkPower.Threshold": C.SPARKS_FOR_FREE_ATTACK,
    "DemolitionConstants.SplashBurst": C.DETONATION_SPLASH_BURST,
    "DemolitionConstants.SplashProcCapPerTurn": C.DETONATION_SPLASH_PROC_CAP,
    "DemolitionConstants.PlaytimeBombDamage": C.PLAYTIME_BOMB_DAMAGE,
    "CompanionConstants.OzDamage": C.OZ_DMG,
    "CompanionConstants.WitchsFlameBurst": C.WITCHS_FLAME_BURST,
    "CompanionConstants.SolarIsotomaBlock": C.SOLAR_ISOTOMA_BLOCK,
    "CompanionConstants.CelestialGiftBlock": C.CELESTIAL_GIFT_BLOCK,

    # Furina.
    "FurinaResourceConstants.FanfarePerHpLost": C.FANFARE_PER_HP_LOST,
    "FurinaResourceConstants.FanfarePerEncoreGained":
        C.FANFARE_PER_ENCORE_GAINED,
    "FurinaResourceConstants.FanfarePerEncoreSpent":
        C.FANFARE_PER_ENCORE_SPENT,
    "FurinaResourceConstants.FanfareFloorPerPower": C.FANFARE_FLOOR_PER_POWER,
    "FurinaResourceConstants.FanfareFloorPerPowerRare":
        C.FANFARE_FLOOR_PER_POWER_RARE,
    "FurinaResourceConstants.BurstPerSkillTag": C.BURST_PER_SKILL_TAG,
    "FurinaResourceConstants.BurstPerReaction": C.BURST_PER_REACTION,
    "FurinaResourceConstants.BurstPerEncoreSpent": C.BURST_PER_ENCORE_SPENT,
    "FurinaResourceConstants.BurstPerSalonTick": C.SALON_TICK_BURST,
    "FurinaResourceConstants.BurstMax": _char("furina", "burst_max"),
    "SpotlightSystem.FanfarePerCenterStagePlay": C.FANFARE_PER_SPOTLIGHT_CARD,
    "SalonConstants.MemberSlots": C.SALON_MEMBER_SLOTS,
    "SalonConstants.FocusPerFanfare": C.SALON_FOCUS_PER,
    "SalonConstants.ReplacementNumericMultiplier": C.SALON_REPLACE_NUMERIC_MULT,
    "SalonConstants.ReplacementDamageMultiplier": C.SALON_REPLACE_DAMAGE_MULT,
    "SalonConstants.TickEncoreCost": C.SALON_TICK_ENCORE_COST,
    "SalonConstants.CrabalettaTick": _salon("crabaletta", "tick", "damage"),
    "SalonConstants.CrabalettaBow": _salon("crabaletta", "bow", "damage"),
    "SalonConstants.UsherTick": _salon("usher", "tick", "block"),
    "SalonConstants.UsherBow": _salon("usher", "bow", "block"),
    "SalonConstants.ChevalmarinTick": _salon("chevalmarin", "tick", "damage"),
    "SalonConstants.ChevalmarinBowEncore": _salon("chevalmarin", "bow", "encore"),

    # Kokomi.
    "KokomiConstants.ChargePerExhaust": C.CHARGE_PER_EXHAUST,
    "KokomiConstants.BurstPerExhaust": C.KOKOMI_BURST_PER_EXHAUST,
    "KokomiConstants.BurstPerReaction": C.BURST_PER_REACTION,
    "KokomiConstants.KurageDuration": C.KURAGE_DURATION,
    "KokomiConstants.KuragePulseBase": C.KURAGE_PULSE_BASE,
    "KokomiConstants.KuragePulsePerCharge": C.KURAGE_PULSE_PER_CHARGE,
    "KokomiConstants.KuragePulseBlock": C.KURAGE_PULSE_BLOCK,
    "KokomiConstants.GarmentAttackBlock": C.GARMENT_ATTACK_BLOCK,
    "KokomiConstants.GarmentTurns": C.CEREMONIAL_GARMENT_TURNS,
    "KokomiConstants.GarmentChargeDivisor": C.GARMENT_CHARGE_DIVISOR,
    "KokomiConstants.ConscriptCostDelta": C.CONSCRIPT_COST_DELTA,
    "KokomiConstants.BurstMax": _char("kokomi", "burst_max"),
}

# --------------------------------------------------------------------------
# UNMIRRORED: C# constants with no tier0 counterpart, each with its reason.
#
# "The sim does not model this" is a legitimate answer and always has been --
# relics, Ancients and the run layer are game-side content. What is not
# legitimate is leaving the question unanswered.
# --------------------------------------------------------------------------
UNMIRRORED: dict[str, str] = {
    "ExplosiveFrags.SparksPerDetonation":
        "the BASE starter's rate, carried forward unchanged by the upgrade -- "
        "which is the ratified design (the windfall is OpeningSparks; the "
        "doubling of this rate was rejected at the 2026-07-26 red-pen). Its "
        "sim counterpart is a literal at the detonation site in effects.py "
        "(`gain_sparks(state, 1)` under spark_on_detonation), not a named "
        "constant, so there is nothing to compare against by value. "
        "NOTE: this entry used to read 'tier0 has no relic-upgrade layer', "
        "which stopped being true when combat_start_spark and "
        "touch_of_orobas_klee landed -- OpeningSparks is now MIRRORED against "
        "that row.",
    "PearlOfInsightRelic.ChargePerExhaust":
        "derived: KokomiConstants.ChargePerExhaust * 2. The compiler enforces "
        "the link, so mirroring the doubling here would just be a second place "
        "to forget. The x2 itself is the upgrade's design, not a sim number.",
    "PearlOfInsightRelic.BurstPerExhaust":
        "derived: KokomiConstants.BurstPerExhaust * 2, same reasoning.",
}

CLASS_RE = re.compile(
    r"^\s*(?:public|internal)\s+(?:static\s+|sealed\s+|abstract\s+|partial\s+)*"
    r"(?:class|record|struct)\s+(\w+)")
CONST_RE = re.compile(r"^\s*public\s+const\s+int\s+(\w+)\s*=\s*([^;]+);")


def collect() -> dict[str, tuple[str, Path]]:
    """Every `public const int` in the mod, keyed Class.Member.

    The enclosing class is the most recent class declaration above the line.
    That is a lexical approximation rather than a parse, and it is exact for
    this codebase because constant blocks are always declared at the top of
    their own class; a nested-class constant would need a real parse, and the
    duplicate-key guard below is what would catch the confusion.
    """
    found: dict[str, tuple[str, Path]] = {}
    for path in sorted(CS_ROOT.rglob("*.cs")):
        cls = None
        for line in path.read_text(encoding="utf-8").splitlines():
            if (m := CLASS_RE.match(line)) is not None:
                cls = m.group(1)
                continue
            if (m := CONST_RE.match(line)) is None:
                continue
            key = f"{cls}.{m.group(1)}"
            if key in found:
                raise SystemExit(
                    f"FINDING: duplicate constant key {key} "
                    f"({found[key][1]} and {path}); the lint's class "
                    "attribution is ambiguous and must be fixed before it can "
                    "be trusted.")
            found[key] = (m.group(2).strip(), path)
    return found


def main() -> int:
    findings: list[str] = []
    found = collect()

    if not found:
        print("FINDING: no `public const int` found -- the lint's pattern or "
              "the source layout changed, and a lint that passes because it "
              "read nothing is not a gate.")
        return 1

    for key, (raw, path) in sorted(found.items()):
        rel = path.relative_to(REPO)
        if key in UNMIRRORED:
            continue
        if key not in MIRRORED:
            findings.append(
                f"{rel}: {key} = {raw} is classified nowhere. Add it to "
                f"MIRRORED with the tier0 value it copies, or to UNMIRRORED "
                f"with the reason the sim has no counterpart.")
            continue
        try:
            got = int(raw)
        except ValueError:
            findings.append(
                f"{rel}: {key} = {raw} is in MIRRORED but is not an integer "
                f"literal, so its value cannot be compared. Make it a literal "
                f"or move it to UNMIRRORED as derived.")
            continue
        want = MIRRORED[key]
        if got != want:
            findings.append(
                f"{rel}: {key} = {got}, but tier0 says {want}. The sim is the "
                f"source of truth: the mod would play to a number no "
                f"simulation endorsed. Mirror it, or re-measure and move both.")

    for key in sorted(MIRRORED):
        if key not in found:
            findings.append(
                f"MIRRORED lists {key}, but no such constant exists in the "
                f"mod. It was renamed or deleted -- update the table so the "
                f"gate keeps covering what it claims to cover.")
    for key in sorted(UNMIRRORED):
        if key not in found:
            findings.append(
                f"UNMIRRORED lists {key}, but no such constant exists in the "
                f"mod. Drop the entry.")

    for finding in findings:
        print(f"FINDING: {finding}")
    if findings:
        return 1
    print(f"constant parity: OK ({len(MIRRORED)} mirrored, "
          f"{len(UNMIRRORED)} declared unmirrored)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
