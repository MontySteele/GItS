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
        // QUARANTINED (the Sparks alternative-cost arm). It borrows the icon of
        // the power it replaces -- True Spark Knight's old body was
        // spark_threshold_down and the re-authored card keeps the id, the
        // rarity and the cost. No new art for a prototype row, per the slice.
        // QUARANTINED (the Klee overhaul, slice one). Every one of these borrows
        // the icon of the shipped power whose job it takes over, for the reason
        // the row above gives: art is commissioned when a slice is ACCEPTED, and
        // a prototype that shipped new art would be paying for a card that may
        // be deleted next week. The Bomb itself borrows the shipped Bomb badge,
        // which is also the "reuse the existing badge rendering" the slice's
        // sec.5 asks for in as many words.
        ProtoBombPower => KleePck.Path("klee/powers/bomb.png"),
        AlicesRecipePower =>
            KleePck.Path("klee/powers/bomb_damage_up.png"),
        ChainedReactionsPower =>
            KleePck.Path("klee/powers/bomb_and_spark_per_turn.png"),
        BombEchoPower =>
            KleePck.Path("klee/powers/sparks_n_splash.png"),
        // THE POOL PASS's Rare (`EB-491`), on the block above's terms
        // verbatim: it borrows the shipped reaction-payout badge, since the
        // Pact pays a second REACTION off a Bomb's reaction. Its own
        // illustration stays owed until the slice is accepted.
        VermillionPactPower =>
            KleePck.Path("klee/powers/reaction_bonus_spark_energy.png"),
        GroundedPower => KleePck.Path("klee/powers/spark_per_turn.png"),
        // R276's Explosive Frags borrows the shipped Explosive Frags badge,
        // whose job it takes over for the arm's Mine (Vulnerable per charge
        // gone off). Its own illustration stays owed until Balance.
        MineFragsPower =>
            KleePck.Path("klee/powers/detonation_vuln.png"),
        // POOL PASS TWO's two (`EB-732`), on the block above's terms verbatim.
        // Return to Sender borrows the BOMB-PER-TRIGGER badge, because that is
        // what it is -- a Bomb placed off an event, one trigger along from
        // Chained Reactions' explosion. Blazing Delight borrows Grounded's,
        // because Grounded is the arm's other start-of-turn payer and this one
        // pays the same beat in a different currency. Both illustrations stay
        // owed until the slice is accepted.
        ReturnToSenderPower =>
            KleePck.Path("klee/powers/bomb_and_spark_per_turn.png"),
        BlazingDelightPower =>
            KleePck.Path("klee/powers/spark_per_turn.png"),
        // THE POOL EXPANSION (R276), on the block above's terms verbatim: each
        // borrows the icon of the arm power whose job it is nearest to, and
        // its own illustration stays owed until the slice is accepted.
        PlaydatePower => KleePck.Path("klee/powers/friendly_visit.png"),
        BoomBadgePower => KleePck.Path("klee/powers/study_buddy.png"),
        WaitForItPower =>
            KleePck.Path("klee/powers/reaction_bonus_spark_energy.png"),
        AftershockPower =>
            KleePck.Path("klee/powers/reaction_bonus_spark_energy.png"),
        PartyPoppersPower =>
            KleePck.Path("klee/powers/bomb_and_spark_per_turn.png"),
        SecretBasePower =>
            KleePck.Path("klee/powers/bomb_and_spark_per_turn.png"),
        LookOutPower => KleePck.Path("klee/powers/spark_per_turn.png"),
        PatienceKleePower => KleePck.Path("klee/powers/bomb_damage_up.png"),
        // Sit Tight's quiet-turn Block borrows Grounded's badge: both pay
        // Block off the arm's explosion ledger for a turn nothing went off.
        SitTightPower => KleePck.Path("klee/powers/spark_per_turn.png"),
        DodocoPower => KleePck.Path("klee/powers/bomb.png"),
        SparkKnightPower =>
            KleePck.Path("klee/powers/spark_threshold_down.png"),
        AlicesDetonatorBasePower =>
            KleePck.Path("klee/powers/witchs_flame.png"),
        // THE STATUS PACKAGE (2026-10-01), on the block above's terms:
        // Finders Keepers places a Bomb off an event (Party Poppers' badge),
        // Damage Report hits ALL off an event (Spark Knight's), and Solitary
        // Confinement changes a cost (Playdate's). Illustrations owed.
        FindersKeepersPower =>
            KleePck.Path("klee/powers/bomb_and_spark_per_turn.png"),
        DamageReportPower =>
            KleePck.Path("klee/powers/spark_threshold_down.png"),
        // R252's DEFENCE-SHELF POWER, on the block above's terms verbatim: it
        // borrows Grounded's icon, because Grounded is the power whose job it
        // takes over one trigger along -- both pay Block off the arm's own
        // explosion ledger, one for the turn nothing went off and one for the
        // turn something did. Its own illustration stays owed until the slice
        // is accepted.
        // R244's TWO COVEN READERS, on the block above's terms verbatim: the
        // Circle borrows the icon of the arm power whose job it takes over
        // (Chained Reactions -- a Bomb per trigger, one trigger over), and the
        // Introduction Magic borrows the witch family's badge, because what it
        // does is turn a hand into Companion cards (R276). The three rows' own
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
        // THE EXPANSION, BATCH ONE (2026-09-29): Watatsumi's Grace takes the
        // badge of The Clouds Like Waves Rippling, the defensive Power it
        // replaces; Ceremonial Garment wears the shipped Garment's own badge;
        // the others borrow the nearest shipped SHAPE, the block above's rule. Art is commissioned when a slice is ACCEPTED.
        WatatsumisGracePower => KleePck.Path(
            "kokomi/powers/vigil_of_the_deep.png"),
        TidalRipostePower => KleePck.Path(
            "kokomi/powers/vigil_of_the_deep.png"),
        ProtoCeremonialGarmentPower => KleePck.Path(
            "kokomi/powers/ceremonial_garment.png"),
        AtWatersEdgePower => KleePck.Path("klee/powers/solar_isotoma.png"),
        GrandDesignPower => KleePck.Path(
            "kokomi/powers/princess_of_watatsumi.png"),
        KurageSwarmPower => KleePck.Path(
            "kokomi/powers/princess_of_watatsumi.png"),
        // THE PAYOFF PASS (2026-10-01): Kurage Canopy is her Ancient's Block
        // per carry-out, so it wears that badge.
        KurageCanopyPower => KleePck.Path(
            "kokomi/powers/princess_of_watatsumi.png"),
        // THE STATUS BATCH (2026-10-01): Abyssal Salvage feeds the Casket, so
        // it wears Kurage Swarm's Casket-feeding badge until it has its own.
        AbyssalSalvagePower => KleePck.Path(
            "kokomi/powers/princess_of_watatsumi.png"),
        AbyssalSalvagePlusPower => KleePck.Path(
            "kokomi/powers/princess_of_watatsumi.png"),
        // POOL COMPLETION (2026-10-01): the six new Powers and three Ancient
        // Powers borrow the nearest shipped shape, the block above's rule.
        PatientTidePower => KleePck.Path("klee/powers/spark_per_turn.png"),
        SeasReproachPower => KleePck.Path(
            "kokomi/powers/vigil_of_the_deep.png"),
        WatatsumiResistancePower => KleePck.Path(
            "kokomi/powers/princess_of_watatsumi.png"),
        DivineStrategyPower => KleePck.Path(
            "kokomi/powers/before_sun_and_moon.png"),
        AlicesMasterpiecePower => KleePck.Path(
            "klee/powers/bomb_damage_up.png"),
        CenterOfAttentionPower => KleePck.Path(
            "furina/powers/limelight.png"),
        TheLongGamePower => KleePck.Path("klee/powers/spark_per_turn.png"),
        TheLongGamePlusPower => KleePck.Path("klee/powers/spark_per_turn.png"),
        NereidsAscensionPower => KleePck.Path(
            "kokomi/powers/before_sun_and_moon.png"),
        // The four with no shipped Kokomi power to borrow from -- the Plan
        // badge, its draw rider and the two Commander powers -- take
        // the nearest shipped SHAPE instead: a Klee companion power for the
        // two that read Companions, and her own Ancient's drip for the badge
        // that counts something waiting to arrive.
        PendingPlansPower => KleePck.Path(
            "kokomi/powers/princess_of_watatsumi.png"),
        // R276: her Ancient under the arm keeps its own shipped sigil -- it
        // is the same card, paying on the Plan instead of in Charge.
        PrincessOfWatatsumiPlanPower => KleePck.Path(
            "kokomi/powers/princess_of_watatsumi.png"),
        // R276: Pincer's and Stolen Chapter's carry-outs borrow the nearest
        // shipped SHAPE, the block above's rule: a replay, and a free card.
        FirstAttackTwicePower => KleePck.Path("klee/powers/study_buddy.png"),
        FirstCardFreePower => KleePck.Path("klee/powers/friendly_visit.png"),
        TreatisePower => KleePck.Path("klee/powers/spark_per_turn.png"),
        GeneralsBannerPower => KleePck.Path("klee/powers/study_buddy.png"),
        // `EB-668`. Battle Plan's rider borrows the icon of the shipped power
        // that already means "your next Attack hits harder" -- the same
        // standing rule the discount took from Rally, applied to what the
        // clause now says. Art is commissioned when a slice is ACCEPTED.
        // THE CASKET PASS (2026-09-28). Moon Signal borrows her Ancient's
        // sigil, the badge above that counts something waiting to arrive.
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
        // Durin, Principle of Purity (AoE trim, 2026-10-03): Binary Form's icon.
        PurityStrikePower => KleePck.Path("klee/powers/witchs_flame.png"),
        PurityWhitePower => KleePck.Path("klee/powers/witchs_flame.png"),
        PurityDarkPower => KleePck.Path("klee/powers/witchs_flame.png"),
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
        LionsFangPower => KleePck.Path("klee/powers/spark_per_turn.png"),
        // R252's fifth caretaker. Let the Show Begin♪ prints no power, so this
        // one takes the second half of the block's rule: the icon of the power
        // whose job the stand-in takes over, which is Noelle's I Got Your Back
        // -- the same repeating this-turn Block watcher with the Mines-only
        // clause taken off.
        // THE SAME SLICE'S HEXEREI FAMILY (R236 sec.3), the same borrow: each
        // of the four wears its Universal's illustration, so the badge takes
        // the icon that Universal's own power already uses (Albedo's Isotoma,
        // Nicole's Revelation-as-a-Hexerei-payoff) -- or, where the Universal
        // it replaces printed no power at all (Fischl's Nightrider, Sucrose's
        // Wind Spirit Creation), the icon of the arm power whose job the
        // stand-in takes over.
        SinfulHexPower => KleePck.Path("klee/powers/oz_summon.png"),
        MollisFavoniusPower => KleePck.Path("klee/powers/amp_reaction_up.png"),
        LadderOfAscentPower => KleePck.Path("klee/powers/witchs_flame.png"),
        // KLEE'S COVEN PERSONALS (R236), same arm and same terms again: each
        // borrows the shipped icon of the power whose job it takes over, and
        // the four rows' own illustrations are deferred to the Balance stage.
        HexhunterChimePower => KleePck.Path("klee/powers/amp_reaction_up.png"),
        HeraldOfFrostPower => KleePck.Path("klee/powers/oz_summon.png"),
        // THE FURINA REFRAME'S RAPTUROUS APPLAUSE COPY, on the same terms as
        // every borrow above: the arm copy is the shipped clause at a halved
        // threshold, so it wears the shipped power's own sigil rather than
        // asking for art a prototype may not keep.
        // R276: the Ancient's Stage-arm power wears the Ancient's own icon.
        StageRaisePerTurnPower =>
            KleePck.Path("furina/powers/all_the_worlds_a_stage.png"),
        // R276 batch two: the Stage's five powers borrow the shipped Furina
        // sigil nearest their job, on the terms every borrow above takes.
        ThunderousApplausePower =>
            KleePck.Path("furina/powers/standing_ovation.png"),
        // THE SALON'S TAB (2026-10-05): the slice's three new powers borrow
        // the shipped Furina sigil nearest their job, on the same terms.
        SalonsEncorePower =>
            KleePck.Path("furina/powers/grand_salon.png"),
        EndlessWaltzPower =>
            KleePck.Path("furina/powers/rising_ovation.png"),
        UniversalRevelryPower =>
            KleePck.Path("furina/powers/the_gallery_stirs.png"),
        // THE RE-FOUNDING (2026-10-04): Rehearsal and its Rare source
        // borrow the gallery's sigil and Full House's neighbour, on the same
        // terms.
        // The supporting pool's Sold Out (2026-09-26), on the same terms: a
        // shipped stage sigil, and not Full House's, so the two read apart.
        // 2026-09-25: the Stage's four badges -- each performer's own, and
        // The Stage on Furina -- borrow the shipped Salon sigils on the same
        // terms: the member's for a member, Center Stage's for the board.
        // THE GUEST CAST (2026-09-25): each guest's badge wears the guest's
        // own face (the character icon, art/plan.tsv power_furina_guest_*),
        // as standing_ovation wears Furina's.
        ClorindeBadgePower =>
            KleePck.Path("furina/powers/guest_clorinde.png"),
        WriothesleyBadgePower =>
            KleePck.Path("furina/powers/guest_wriothesley.png"),
        CharlotteBadgePower =>
            KleePck.Path("furina/powers/guest_charlotte.png"),
        LynetteBadgePower =>
            KleePck.Path("furina/powers/guest_lynette.png"),
        // The pool to 39 (2026-10-05): the three new guests' faces, from the
        // supporting pool's art pass (art/plan.tsv power_furina_guest_*).
        LyneyBadgePower =>
            KleePck.Path("furina/powers/guest_lyney.png"),
        SigewinneBadgePower =>
            KleePck.Path("furina/powers/guest_sigewinne.png"),
        ChevreuseBadgePower =>
            KleePck.Path("furina/powers/guest_chevreuse.png"),
        // THE SUPPORTING POOL (2026-09-26): the two new guests' faces, from
        // the same art pass, and the batch's nine powers borrowing the
        // shipped Furina sigil nearest their job, on the terms every borrow
        // above takes.
        // The re-founding: her Fanfare badge wears the board's sigil.
        FanfarePower => KleePck.Path(Vfx.FanfareCounter.GlyphPath),
        // THE CO-OP SET (review/records/coop-set-2026-09-25.md): five powers,
        // each borrowing the shipped sigil nearest its job on the terms every
        // borrow above takes -- the Bomb for the two that set Klee's Bombs
        // off, the Stage's board for the lead that shields an ally, an
        // ovation for the crowd, and the Casket's for the Plan payoff.
        PassTheMatchPower => KleePck.Path("klee/powers/bomb.png"),
        KnightsOfFavoniusPower => KleePck.Path("klee/powers/bomb_damage_up.png"),
        SangonomiyasCounselPower =>
            KleePck.Path("kokomi/powers/kurages_oath.png"),
        // The second batch (review/active/coop-concepts-2026-09-27.md), on
        // the same borrowing terms: the Mine's shred wears the Bomb's
        // Vulnerable sigil, the energy gift the reaction-energy one, the
        // toast a spotlight, the crowd an ovation.
        ShrapnelPower => KleePck.Path("klee/powers/detonation_vuln.png"),
        SparksForEveryonePower =>
            KleePck.Path("klee/powers/reaction_bonus_spark_energy.png"),
        // Klee final pass (2026-10-02): Cover Your Ears!'s this-turn Strength
        // loss on an enemy borrows the Bomb's Vulnerable sigil, the badge
        // Shrapnel's enemy debuff already wears. Its own art stays owed.
        ProtoKoCoverYourEarsPower =>
            KleePck.Path("klee/powers/detonation_vuln.png"),
        // Amber, Explosive Puppet's this-turn loss: the same borrowed badge.
        ProtoMcAmberExplosivePuppetPower =>
            KleePck.Path("klee/powers/detonation_vuln.png"),
        // VARKA (the Oath rework): his Oath badge wears the Vision of its
        // current element (the retired Winds' files, the varka-art pass's
        // own); the card powers borrow the three varka power files and
        // Grand Master's Order borrows Study Buddy's, the replay it narrows
        // to Knights. No new art for a prototype.
        PyroOathPower => KleePck.Path("varka/powers/pyro_wind.png"),
        // Element identities sec.7: the element he left wears its badge.
        PyroOathLeftPower => KleePck.Path("varka/powers/pyro_wind.png"),
        HydroOathLeftPower => KleePck.Path("varka/powers/hydro_wind.png"),
        CryoOathLeftPower => KleePck.Path("varka/powers/cryo_wind.png"),
        ElectroOathLeftPower => KleePck.Path("varka/powers/electro_wind.png"),
        HydroOathPower => KleePck.Path("varka/powers/hydro_wind.png"),
        CryoOathPower => KleePck.Path("varka/powers/cryo_wind.png"),
        ElectroOathPower => KleePck.Path("varka/powers/electro_wind.png"),
        UnswornOathPower =>
            KleePck.Path("varka/powers/converging_winds.png"),
        StormwardStancePower =>
            KleePck.Path("varka/powers/stormward_stance.png"),
        ConvergingWindsPower =>
            KleePck.Path("varka/powers/converging_winds.png"),
        BoreasUnboundPower => KleePck.Path("varka/powers/boreas_unbound.png"),
        DawnWindsMarchPower => KleePck.Path("varka/powers/boreas_unbound.png"),
        SwornBrotherhoodPower =>
            KleePck.Path("varka/powers/converging_winds.png"),
        SwornBrotherhoodCurrentPower =>
            KleePck.Path("varka/powers/converging_winds.png"),
        VarkaBaronBunnyPower => KleePck.Path("varka/powers/pyro_wind.png"),
        GrandMastersOrderPower => KleePck.Path("klee/powers/study_buddy.png"),
        // THE EXPANSION (2026-10-01): no new art for a prototype, so each
        // borrows the varka badge nearest its rule -- an element Power its
        // element's Vision, a Swirl reader Converging Winds', a Block or
        // Oath Power Stormward Stance's, an element-change Power Boreas
        // Unbound's, a Knight Power Study Buddy's (Grand Master's Order's).
        StaticFieldPower => KleePck.Path("varka/powers/electro_wind.png"),
        UnwaveringBannerPower =>
            KleePck.Path("varka/powers/stormward_stance.png"),
        CycleOfSeasonsPower => KleePck.Path("varka/powers/boreas_unbound.png"),
        // Varka defence (2026-10-01): Cycle of Seasons' Block twin.
        WindborneResolvePower =>
            KleePck.Path("varka/powers/boreas_unbound.png"),
        EyeWallPower => KleePck.Path("varka/powers/converging_winds.png"),
        AssemblyAtTheCathedralPower =>
            KleePck.Path("klee/powers/study_buddy.png"),
        WildfireOathPower => KleePck.Path("varka/powers/pyro_wind.png"),
        // The combo pass (2026-10-04): Pyro's Exhaust engine.
        PyreOathPower => KleePck.Path("varka/powers/pyro_wind.png"),
        RetaliatingTidePower => KleePck.Path("varka/powers/hydro_wind.png"),
        AbsoluteZeroPower => KleePck.Path("varka/powers/cryo_wind.png"),
        OathUntoDeathPower =>
            KleePck.Path("varka/powers/stormward_stance.png"),
        WolfpackPower => KleePck.Path("varka/powers/boreas_unbound.png"),
        OathboundAegisPower =>
            KleePck.Path("varka/powers/stormward_stance.png"),
        WeathervanePower => KleePck.Path("varka/powers/boreas_unbound.png"),
        TwinGalesPower => KleePck.Path("varka/powers/converging_winds.png"),
        EyeOfStormterrorPower =>
            KleePck.Path("varka/powers/converging_winds.png"),
        TheOrderAnswersPower => KleePck.Path("klee/powers/study_buddy.png"),
        // Companion summons/auras. These four had NO case at all and fell to
        // `_ => null`, i.e. the base-game placeholder -- the gap the 2026-07-24
        // sweep found from Oz and Solar Isotoma. Wiring the paths ahead of the
        // assets is deliberate: KleePck.Path returns null while a file is
        // absent, so behaviour is unchanged until the PNG lands, and the miss
        // is logged ONCE by name instead of failing silently forever.

        // The six powers the 2026-07-24 companion sweep MISSED, because that
        // sweep framed itself as "summons" and these are not summons. They had
        // no case at all and rendered the base-game placeholder.
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

        // Curtain Call's activity-triggered set (R85), shipped by the "Take a
        // Bow" consolidation sprint. Paths are wired AHEAD of the art, which
        // is this file's established policy (see the companion-summon block
        // above): KleePck.Path returns null while a file is absent, so each of
        // these behaves exactly like today's placeholder until its PNG lands,
        // and the miss is logged ONCE by name instead of being invisible.
        // Named individually rather than grouped -- the two Stagehands halves
        // are separate powers and a shared icon would read as intentional.
        CrossExaminationPower => KleePck.Path("furina/powers/courtroom_drama.png"),
        FirstAttackDrawPower => KleePck.Path("furina/powers/quick_change.png"),

        // A7 (2026-07-29), the last sheet card to reach C#. Same path-ahead-of-
        // art policy as the block above: null until the PNG lands, and R13
        // stops it from being an invisible omission in the meantime.

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

        AuraPower aura => KleePck.Path(
            "klee/powers/aura_" + aura.Element.ToString().ToLowerInvariant() + ".png"),

        _ => null,
    };

    /// <summary>
    /// Powers that are allowed to have no icon, with the reason. R13 fails on
    /// any other iconless PowerModel in this assembly.
    /// </summary>
    internal static readonly Dictionary<Type, string> IconExempt = new()
    {
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
