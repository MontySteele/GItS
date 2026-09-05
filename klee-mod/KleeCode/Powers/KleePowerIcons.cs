using System;
using System.Collections.Generic;
using HarmonyLib;
using MegaCrit.Sts2.Core.Models;

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
        BombEchoPower =>
            KleePck.Path("klee/powers/sparks_n_splash.png"),
        BombReactionSparkPower =>
            KleePck.Path("klee/powers/reaction_bonus_spark_energy.png"),
        GroundedPower => KleePck.Path("klee/powers/spark_per_turn.png"),
        // R252's DEFENCE-SHELF POWER, on the block above's terms verbatim: it
        // borrows Grounded's icon, because Grounded is the power whose job it
        // takes over one trigger along -- both pay Block off the arm's own
        // explosion ledger, one for the turn nothing went off and one for the
        // turn something did. Its own illustration stays owed until the slice
        // is accepted.
        // R244's TWO COVEN READERS, on the block above's terms verbatim: the
        // Circle borrows the icon of the arm power whose job it takes over
        // (Chained Reactions -- a Bomb per trigger, one trigger over), and the
        // Introduction Magic borrows the Hexerei family's own badge, because
        // what it does is turn a hand into witches. The three rows' own
        // illustrations stay owed until the slice is accepted.
        WitchesCirclePower =>
            KleePck.Path("klee/powers/bomb_and_spark_per_turn.png"),
        IntroductionMagicPower =>
            KleePck.Path("klee/powers/witchs_flame.png"),
        // QUARANTINED (the Kokomi overhaul, draft 6). Every one of these
        // borrows the icon of the SHIPPED Kokomi power whose job it takes over,
        // on the block above's argument verbatim: art is commissioned when a
        // slice is ACCEPTED, and a prototype that shipped new art would be
        // paying for a card that may be deleted next week. The marker itself
        // borrows the shipped Bake-Kurage badge, which is the same jellyfish
        // wearing a different rule. Named individually rather than grouped, for
        // the reason the Kokomi block further down records: one shared icon
        // across unrelated effects reads as intentional.
        ProtoBakeKuragePower => KleePck.Path("kokomi/powers/bake_kurage.png"),
        SongOfPearlsPower => KleePck.Path("kokomi/powers/kurages_oath.png"),
        CloudsLikeWavesPower => KleePck.Path(
            "kokomi/powers/vigil_of_the_deep.png"),
        NereidsAscensionPower => KleePck.Path(
            "kokomi/powers/before_sun_and_moon.png"),
        // The five with no shipped Kokomi power to borrow from -- the Plan
        // badge, its draw rider, its Rare and the two Commander powers -- take
        // the nearest shipped SHAPE instead: a Klee companion power for the
        // two that read Companions, and her own Ancient's drip for the badge
        // that counts something waiting to arrive.
        PendingPlansPower => KleePck.Path(
            "kokomi/powers/princess_of_watatsumi.png"),
        TreatisePower => KleePck.Path("klee/powers/spark_per_turn.png"),
        PlansAlsoNowPower => KleePck.Path(
            "kokomi/powers/princess_of_watatsumi.png"),
        GeneralsBannerPower => KleePck.Path("klee/powers/study_buddy.png"),
        NextCompanionDiscountPower =>
            KleePck.Path("klee/powers/friendly_visit.png"),
        // `EB-335`. Shell Guard is a Block window, so it borrows the shipped
        // Kokomi power that already means "the jellyfish is protecting you".
        ShellGuardPower => KleePck.Path("kokomi/powers/kurages_oath.png"),
        // QUARANTINED (the Mondstadt companion overhaul). Every one of these
        // borrows the icon of the SHIPPED companion power whose job it takes
        // over, on the block above's argument verbatim: art is commissioned
        // when a slice is ACCEPTED, and the workshop's own sec.5 defers all
        // sixteen new illustrations to the Balance stage. Wiring a path ahead
        // of an asset is the established shape in this file -- KleePck.Path
        // returns null while a file is absent, so a missing PNG changes
        // nothing and the miss is logged once by name.
        SignatureMixPower => KleePck.Path("klee/powers/celestial_gift.png"),
        RevelationPower => KleePck.Path("klee/powers/celestial_gift.png"),
        StellarisOmenPower => KleePck.Path("klee/powers/detonation_vuln.png"),
        GlacialWaltzPower => KleePck.Path("klee/powers/oz_summon.png"),
        MondstadtOzPower => KleePck.Path("klee/powers/oz_summon.png"),
        LightningRosePower => KleePck.Path("klee/powers/oz_summon.png"),
        GrandOdePower => KleePck.Path("klee/powers/amp_reaction_up.png"),
        DandelionBreezePower => KleePck.Path("klee/powers/amp_reaction_up.png"),
        SolarIsotomaBloomPower =>
            KleePck.Path("klee/powers/solar_isotoma.png"),
        // The same arm's SECOND WAVE, on the same terms: each borrows the
        // shipped icon of the power whose job it takes over, or of the shipped
        // companion power it is the rewrite of.
        IcyPawsPower => KleePck.Path("klee/powers/frozen.png"),
        MelodyLoopPower => KleePck.Path("klee/powers/oz_summon.png"),
        PassionOverloadPower =>
            KleePck.Path("klee/powers/passion_overload.png"),
        SwirlChargePower => KleePck.Path("klee/powers/amp_reaction_up.png"),
        StarfrostDiscountPower =>
            KleePck.Path("klee/powers/zero_cost_attacks_up.png"),
        LightningFangPower =>
            KleePck.Path("klee/powers/passion_overload.png"),
        SturmUndDrangPower => KleePck.Path("klee/powers/amp_reaction_up.png"),
        FavonianFavorPower => KleePck.Path("klee/powers/celestial_gift.png"),
        BinaryFormWhitePower => KleePck.Path("klee/powers/witchs_flame.png"),
        BinaryFormDarkPower => KleePck.Path("klee/powers/witchs_flame.png"),
        SacramentalShowerPower =>
            KleePck.Path("klee/powers/detonation_splash.png"),
        BaronBunnyPower => KleePck.Path("klee/powers/detonation_splash.png"),
        LightfallSwordPower =>
            KleePck.Path("klee/powers/shattering_pressure.png"),
        // THE INAZUMA ARM, on the same terms again: each borrows the shipped
        // icon of the power whose job it takes over, and the workshop's own
        // illustrations are deferred to the Balance stage.
        WarBannerPower => KleePck.Path("klee/powers/celestial_gift.png"),
        JuugaPower => KleePck.Path("klee/powers/oz_summon.png"),
        MujiMujiDarumaPower => KleePck.Path("klee/powers/oz_summon.png"),
        NaptimePower => KleePck.Path("klee/powers/celestial_gift.png"),
        SanctifyingRingPower => KleePck.Path("klee/powers/oz_summon.png"),
        BlazingBarrierPower => KleePck.Path("klee/powers/celestial_gift.png"),
        CrimsonOoyoroiPower =>
            KleePck.Path("klee/powers/passion_overload.png"),
        CrowfeatherCoverPower =>
            KleePck.Path("klee/powers/passion_overload.png"),
        TenguStormcallPower =>
            KleePck.Path("klee/powers/passion_overload.png"),
        SesshouSakuraPower => KleePck.Path("klee/powers/oz_summon.png"),
        AurousBlazePower => KleePck.Path("klee/powers/detonation_splash.png"),
        SoumetsuPower => KleePck.Path("klee/powers/oz_summon.png"),
        KyoukaPower => KleePck.Path("klee/powers/passion_overload.png"),
        SurpriseDispatchPower =>
            KleePck.Path("klee/powers/detonation_splash.png"),
        TamotoPower => KleePck.Path("klee/powers/shattering_pressure.png"),
        // THE SAME ARM'S STAND-IN SLICE, on the same terms once more, and the
        // borrow is easier to argue here than anywhere above: a stand-in wears
        // the Universal's own illustration (its row's `art_of:`), so its badge
        // borrows the icon that Universal's power already uses.
        ShakenNotPurredPower => KleePck.Path("klee/powers/frozen.png"),
        ColdBloodedPower => KleePck.Path("klee/powers/frozen.png"),
        IGotYourBackPower => KleePck.Path("klee/powers/celestial_gift.png"),
        LionsFangPower => KleePck.Path("klee/powers/spark_per_turn.png"),
        // R252's fifth caretaker. Let the Show Begin♪ prints no power, so this
        // one takes the second half of the block's rule: the icon of the power
        // whose job the stand-in takes over, which is Noelle's I Got Your Back
        // -- the same repeating this-turn Block watcher with the Mines-only
        // clause taken off.
        FrontRowSeatPower => KleePck.Path("klee/powers/celestial_gift.png"),
        // THE SAME SLICE'S HEXEREI FAMILY (R236 sec.3), the same borrow: each
        // of the four wears its Universal's illustration, so the badge takes
        // the icon that Universal's own power already uses (Albedo's Isotoma,
        // Nicole's Revelation-as-a-Hexerei-payoff) -- or, where the Universal
        // it replaces printed no power at all (Fischl's Nightrider, Sucrose's
        // Wind Spirit Creation), the icon of the arm power whose job the
        // stand-in takes over.
        TectonicTidePower => KleePck.Path("klee/powers/solar_isotoma.png"),
        SinfulHexPower => KleePck.Path("klee/powers/oz_summon.png"),
        MollisFavoniusPower => KleePck.Path("klee/powers/amp_reaction_up.png"),
        LadderOfAscentPower => KleePck.Path("klee/powers/witchs_flame.png"),
        // KLEE'S COVEN PERSONALS (R236), same arm and same terms again: each
        // borrows the shipped icon of the power whose job it takes over, and
        // the four rows' own illustrations are deferred to the Balance stage.
        HexhunterChimePower => KleePck.Path("klee/powers/amp_reaction_up.png"),
        HeraldOfFrostPower => KleePck.Path("klee/powers/oz_summon.png"),
        YueguiPower => KleePck.Path("klee/powers/oz_summon.png"),
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
