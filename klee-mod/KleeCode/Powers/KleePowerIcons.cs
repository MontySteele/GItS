using System;
using System.Collections.Generic;
using HarmonyLib;
using MegaCrit.Sts2.Core.Models;
#if PROTOTYPE_CARDS
// QUARANTINED. Imported rather than qualified inline so every switch arm below
// reads as a bare type name -- which is what `tools/lint_power_icons.py` parses
// to decide whether a power has an icon case at all.
using KleeMod.Powers.Prototype;
#endif

namespace KleeMod.Powers;

/// <summary>
/// Routes our powers' icons to klee.pck textures.
///
/// PowerModel's icon surface is NON-virtual -- PackedIconPath is a plain
/// getter, and Icon, IconPath and the preloader all resolve through it or
/// through ResolvedBigIconPath -- and our powers deliberately derive from the
/// raw PowerModel rather than BaseLib's CustomPowerModel (they are combat
/// mechanics owned by our own systems, not pool content), so BaseLib's
/// CustomPackedIconPath redirect never sees them. Patching the two PATH
/// getters fixes every consumer at once; returning a texture from get_Icon
/// alone would leave IconPath string consumers pointing at the atlas.
///
/// Each mapping is gated through KleePck.Path, so a missing pack (or a
/// missing per-element aura file) falls through to the original getter and
/// behaves exactly like today's placeholder state.
/// </summary>
internal static class KleePowerIcons
{
    internal static string? PathFor(PowerModel power) => power switch
    {
        SparkPower => KleePck.Path("klee/powers/spark.png"),
        BombPower => KleePck.Path("klee/powers/bomb.png"),
        BurstMeterPower => KleePck.Path("klee/powers/burst.png"),
        BombDamageUpPower => KleePck.Path("klee/powers/bomb_damage_up.png"),
        DetonationSplashPower => KleePck.Path("klee/powers/detonation_splash.png"),
        DetonationVulnPower => KleePck.Path("klee/powers/detonation_vuln.png"),
        BombAndSparkPerTurnPower => KleePck.Path("klee/powers/bomb_and_spark_per_turn.png"),
        SparkPerTurnPower => KleePck.Path("klee/powers/spark_per_turn.png"),
        ZeroCostAttacksUpPower => KleePck.Path("klee/powers/zero_cost_attacks_up.png"),
        SparkThresholdDownPower => KleePck.Path("klee/powers/spark_threshold_down.png"),
#if PROTOTYPE_CARDS
        // QUARANTINED (the Sparks alternative-cost arm). It borrows the icon of
        // the power it replaces -- True Spark Knight's old body was
        // spark_threshold_down and the re-authored card keeps the id, the
        // rarity and the cost. No new art for a prototype row, per the slice.
        SparkAttackCostPower => KleePck.Path("klee/powers/spark_threshold_down.png"),
        // QUARANTINED (the Klee overhaul, slice one). Every one of these borrows
        // the icon of the shipped power whose job it takes over, for the reason
        // the row above gives: art is commissioned when a slice is ACCEPTED, and
        // a prototype that shipped new art would be paying for a card that may
        // be deleted next week. The Bomb itself borrows the shipped Bomb badge,
        // which is also the "reuse the existing badge rendering" the slice's
        // sec.5 asks for in as many words.
        ProtoBombPower => KleePck.Path("klee/powers/bomb.png"),
        ExplosivesWorkshopGrowthPower =>
            KleePck.Path("klee/powers/bomb_damage_up.png"),
        AlicesRecipePower =>
            KleePck.Path("klee/powers/bomb_damage_up.png"),
        ChainedReactionsPower =>
            KleePck.Path("klee/powers/bomb_and_spark_per_turn.png"),
        EndOfTurnSetOffPower =>
            KleePck.Path("klee/powers/sparks_n_splash.png"),
        BombReactionSparkPower =>
            KleePck.Path("klee/powers/reaction_bonus_spark_energy.png"),
        GroundedPower => KleePck.Path("klee/powers/spark_per_turn.png"),
#endif
        ReactionBonusSparkEnergyPower => KleePck.Path("klee/powers/reaction_bonus_spark_energy.png"),
        AmpReactionUpPower => KleePck.Path("klee/powers/amp_reaction_up.png"),
        SparksNSplashPower => KleePck.Path("klee/powers/sparks_n_splash.png"),
        // Companion summons/auras. These four had NO case at all and fell to
        // `_ => null`, i.e. the base-game placeholder -- the gap the 2026-07-24
        // sweep found from Oz and Solar Isotoma. Wiring the paths ahead of the
        // assets is deliberate: KleePck.Path returns null while a file is
        // absent, so behaviour is unchanged until the PNG lands, and the miss
        // is logged ONCE by name instead of failing silently forever.
        OzSummonPower => KleePck.Path("klee/powers/oz_summon.png"),
        SolarIsotomaPower => KleePck.Path("klee/powers/solar_isotoma.png"),
        WitchsFlamePower => KleePck.Path("klee/powers/witchs_flame.png"),
        CelestialGiftPower => KleePck.Path("klee/powers/celestial_gift.png"),

        // The six powers the 2026-07-24 companion sweep MISSED, because that
        // sweep framed itself as "summons" and these are not summons. They had
        // no case at all and rendered the base-game placeholder.
        CompanionCostThisTurnPower => KleePck.Path("klee/powers/friendly_visit.png"),
        ReplayNextCompanionPower => KleePck.Path("klee/powers/study_buddy.png"),
        AttackUpThisTurnPower => KleePck.Path("klee/powers/fantastic_voyage.png"),
        NextAttackUpPower => KleePck.Path("klee/powers/passion_overload.png"),
        ShatterBonusPower => KleePck.Path("klee/powers/shattering_pressure.png"),
        FrozenPower => KleePck.Path("klee/powers/frozen.png"),

        // FURINA. This block used to route all of her powers at KLEE textures
        // (the Salon rendered a BOMB, Encore a SPARK) and was recorded as art
        // debt on the grounds that dedicated paths would regress to
        // placeholders. Sprint 2 Track E closed that by fetching the art
        // first: every path below has a file, cut from Furina's own talent and
        // constellation sigils. See docs/archive/icon-gap-2026-07-24.md.
        FanfareMeterPower => KleePck.Path("furina/powers/fanfare.png"),
        FanfareAttackPer10Power => KleePck.Path("furina/powers/rising_ovation.png"),
        SalonMemberPower => KleePck.Path("furina/powers/salon_member.png"),
        SalonDamageUpPower => KleePck.Path("furina/powers/grand_salon.png"),
        EncorePerTurnPower => KleePck.Path("furina/powers/all_the_worlds_a_stage.png"),

        // The Spotlight family. The old entry matched the SpotlightPower BASE
        // and so read as a handful of powers; it was in fact TEN distinct
        // powers all rendering Dodoco's Duet. Every one is now named, and the
        // six that derive from SpotlightPower MUST precede any base-class
        // pattern or C# would match the base first and silently collapse them
        // all back to one icon.
        CenterStagePower => KleePck.Path("furina/powers/center_stage.png"),
        GuestCastPower => KleePck.Path("furina/powers/guest_cast.png"),
        SpotlightDiscountPower => KleePck.Path("furina/powers/leading_role.png"),
        SpotlightDrawPower => KleePck.Path("furina/powers/supporting_cast.png"),
        SpotlightMultBonusPower => KleePck.Path("furina/powers/top_billing.png"),
        SpotlightMultBonusTurnPower => KleePck.Path("furina/powers/limelight.png"),
        SpotlightFlatDamagePower => KleePck.Path("furina/powers/star_of_the_show.png"),
        SpotlightFlatDamageTurnPower => KleePck.Path("furina/powers/stage_lights.png"),
        OvationSpendBoostPower => KleePck.Path("furina/powers/standing_ovation.png"),
        SpotlightEncoreFirstPower => KleePck.Path("furina/powers/ovation_trickle.png"),

        // Curtain Call's activity-triggered set (R85), shipped by the "Take a
        // Bow" consolidation sprint. Paths are wired AHEAD of the art, which
        // is this file's established policy (see the companion-summon block
        // above): KleePck.Path returns null while a file is absent, so each of
        // these behaves exactly like today's placeholder until its PNG lands,
        // and the miss is logged ONCE by name instead of being invisible.
        // Named individually rather than grouped -- the two Stagehands halves
        // are separate powers and a shared icon would read as intentional.
        SalonDeployBlockPower => KleePck.Path("furina/powers/fortissimo_guard.png"),
        SalonBowBlockPower => KleePck.Path("furina/powers/stagehands.png"),
        SalonBowEncorePower => KleePck.Path("furina/powers/stagehands_encore.png"),
        CrossExaminationPower => KleePck.Path("furina/powers/courtroom_drama.png"),
        EncoreSpendDrawPower => KleePck.Path("furina/powers/the_gallery_stirs.png"),
        FirstAttackDrawPower => KleePck.Path("furina/powers/quick_change.png"),

        // A7 (2026-07-29), the last sheet card to reach C#. Same path-ahead-of-
        // art policy as the block above: null until the PNG lands, and R13
        // stops it from being an invisible omission in the meantime.
        FanfareDeltaBlockPower => KleePck.Path(
            "furina/powers/unheard_confession.png"),

        // KOKOMI (EB-67). This block did not exist at all: every one of her six
        // powers fell to `_ => null` and drew the base-game placeholder, which
        // is the `Bake-Kurage` badge the 2026-08-08 live session captured. The
        // gap was BOTH halves at once -- no case here AND no file, because the
        // pck's kokomi\ block carried model\, ui\ and summon\ and nothing else.
        // Named individually rather than grouped for the reason recorded above:
        // the three Kurage powers are three different effects and one shared
        // jellyfish would read as intentional.
        //
        // Bake-Kurage has a SECOND, unrelated sprite at kokomi/summon/
        // bake_kurage.png -- that one is the CREATURE on the field (the
        // end-of-turn attribution docket), this one is the status badge. Both
        // ship; they are different sizes and different jobs.
        KurageSummonPower => KleePck.Path("kokomi/powers/bake_kurage.png"),
        KurageWardPower => KleePck.Path("kokomi/powers/kurages_oath.png"),
        KurageAmpPower => KleePck.Path("kokomi/powers/before_sun_and_moon.png"),
        CeremonialGarmentPower => KleePck.Path(
            "kokomi/powers/ceremonial_garment.png"),
        PreventExhaustWardPower => KleePck.Path(
            "kokomi/powers/vigil_of_the_deep.png"),
        ChargePerTurnPower => KleePck.Path(
            "kokomi/powers/princess_of_watatsumi.png"),

        // NO SpotlightPower base case, deliberately. A future subclass added
        // without an icon should fall to `_ => null` and show the base-game
        // placeholder -- which reads as "no art yet" -- rather than inherit a
        // sibling's sigil, which reads as intentional and is the exact failure
        // this whole sweep was cleaning up. R13 turns that into a boot failure
        // rather than something only a manual sweep would find.

        AuraPower aura => KleePck.Path(
            "klee/powers/aura_" + aura.Element.ToString().ToLowerInvariant() + ".png"),

        // EncoreMeterPower and FurinaBurstMeterPower are absent on purpose:
        // sprint 2 E1 retired both as displays (Encore's ambient home is the
        // Salon stage ribbon, Burst's is the overhead gauge) and nothing
        // applies them any more. They stay registered only so a mid-combat
        // save written before the retirement still loads. R13 exempts them.
        _ => null,
    };

    /// <summary>
    /// Powers that are allowed to have no icon, with the reason. R13 fails on
    /// any other iconless PowerModel in this assembly.
    /// </summary>
    internal static readonly Dictionary<Type, string> IconExempt = new()
    {
        [typeof(EncoreMeterPower)] = "retired display (sprint 2 E1); save-compat only",
        [typeof(FurinaBurstMeterPower)] = "retired display (sprint 2 E1); save-compat only",
        [typeof(SpotlightPower)] = "abstract base; every concrete subclass is named",
    };
}

[HarmonyPatch(typeof(PowerModel), nameof(PowerModel.PackedIconPath), MethodType.Getter)]
internal static class PowerModel_PackedIconPath_KleeIcons_Patch
{
    [HarmonyPrefix]
    public static bool Prefix(PowerModel __instance, ref string __result)
    {
        var path = KleePowerIcons.PathFor(__instance);
        if (path == null)
        {
            return true;
        }
        __result = path;
        return false;
    }
}

/// <remarks>
/// Also bypasses PowerModel's _resolvedBigIconPath cache for our powers,
/// which is fine: KleePck.Path caches its own existence check.
/// </remarks>
[HarmonyPatch(typeof(PowerModel), nameof(PowerModel.ResolvedBigIconPath), MethodType.Getter)]
internal static class PowerModel_ResolvedBigIconPath_KleeIcons_Patch
{
    [HarmonyPrefix]
    public static bool Prefix(PowerModel __instance, ref string __result)
    {
        var path = KleePowerIcons.PathFor(__instance);
        if (path == null)
        {
            return true;
        }
        __result = path;
        return false;
    }
}
