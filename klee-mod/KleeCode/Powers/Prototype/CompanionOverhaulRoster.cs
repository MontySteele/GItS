using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// THE ONE WIRING SEAM, and there is exactly one: which companions may be
/// OFFERED. Sim twin: <c>tier0.content.loader.companion_roster_replacement</c>,
/// which exists for the same reason -- every offer surface in each engine goes
/// through one door, so the two cannot disagree about what a companion pool is.
///
/// The C# door is <see cref="CompanionPool.All"/>, which
/// <see cref="CompanionSlot"/> (the fourth reward slot) and the shop channel
/// both read. Redirecting that one property moves both at once, which is the
/// point of putting the seam at the source rather than at the mouths.
///
/// A REPLACEMENT OF EVERY NATION, LISTED BY TYPE. Mondstadt's and Inazuma's
/// approved workshops rewrote their Universals; Fontaine's rows were ported as
/// they are (legacy cleanup pick 4). No shipped companion row comes through.
/// Listing types puts the correspondence in the compiler's hands, because a
/// deleted row takes its class with it and this file stops building.
/// </summary>
internal static class CompanionOverhaulRoster
{
    private static IReadOnlyList<CardModel>? _roster;

    /// <summary>
    /// Every companion an offer surface may see: the three nations'
    /// Universals, all prototype rows.
    ///
    /// NO SHIPPED ROW SINCE LEGACY CLEANUP STAGE 4 (2026-10-01). Fontaine had
    /// no workshop, so its shipped rows used to come through a nation filter
    /// over <c>CompanionRoster.All</c>; pick 4 ported them to the prototype
    /// surface as they are (<see cref="FontaineUniversals"/>), so the roster
    /// is listed by type, whole.
    ///
    /// CACHED, and lazily. <c>ModelDb.Card&lt;T&gt;()</c> throws
    /// KeyNotFoundException until the models are built (they are
    /// <c>autoAdd: false</c> and constructed at pool-build time), and a static
    /// constructor that throws POISONS ITS TYPE for the life of the process --
    /// the EB-194 lesson, applied here before it can be learned twice.
    /// </summary>
    internal static IReadOnlyList<CardModel> Roster() =>
        _roster ??= Universals()
            .Concat(InazumaUniversals())
            .Concat(FontaineUniversals())
            .ToList();

    /// <summary>
    /// Mondstadt's thirty-four rewritten Universals, in the workshop's sec.3
    /// character order. Coven Personals (its sec.4) and Klee-only stand-ins are
    /// NOT here: this arm rewrites the Universal pool and nothing else, and a
    /// Personal is Klee's kit rather than a companion offer.
    ///
    /// THIRTY-FOUR OF THIRTY-FOUR, in two waves. Twenty-one landed first; the
    /// other thirteen were held back because their printed text wanted an
    /// engine hook that existed in NEITHER engine -- a Block-absorption
    /// trigger, a pre-enemy-attack trap, a next-Attack element override, a
    /// Swirl event that remembers its element, an Attack counter, a next-Attack
    /// cost discount, a Block-reading damage formula, a power on a chosen body,
    /// a counting delayed blade, and two damage-pipeline modifiers behind a
    /// modal Power. Those hooks are
    /// <c>Powers/Prototype/CompanionOverhaulHooks.cs</c> and the sim's
    /// `companion_overhaul_*` block; which row spends which is in
    /// <c>docs/notes/prototype-surface-provenance.md</c>. The rule that held
    /// them out still binds anything later: a card that cannot be printed as
    /// written is left OUT rather than replaced by a simpler card, the same
    /// rule the Klee overhaul applied to Vermillion Pact.
    /// </summary>
    private static IEnumerable<CardModel> Universals() => new CardModel[]
    {
        ModelDb.Card<ProtoMcDionaSignatureMix>(),
        ModelDb.Card<ProtoMcNoelleBreastplate>(),
        ModelDb.Card<ProtoMcKaeyaFrostgnaw>(),
        ModelDb.Card<ProtoMcKaeyaGlacialWaltz>(),
        ModelDb.Card<ProtoMcBarbaraShowBegin>(),
        ModelDb.Card<ProtoMcAlbedoSolarIsotoma>(),
        ModelDb.Card<ProtoMcJeanGaleBlade>(),
        ModelDb.Card<ProtoMcJeanDandelionBreeze>(),
        ModelDb.Card<ProtoMcFischlNightrider>(),
        ModelDb.Card<ProtoMcFischlOz>(),
        ModelDb.Card<ProtoMcSucroseGust>(),
        ModelDb.Card<ProtoMcSucroseAstable>(),
        ModelDb.Card<ProtoMcSucroseCatalystConversion>(),
        ModelDb.Card<ProtoMcBennettFantasticVoyage>(),
        ModelDb.Card<ProtoMcNicoleRevelation>(),
        ModelDb.Card<ProtoMcMonaStellarisPhantasm>(),
        ModelDb.Card<ProtoMcVentiGrandOde>(),
        ModelDb.Card<ProtoMcAmberFieryRain>(),
        ModelDb.Card<ProtoMcLisaVioletArc>(),
        ModelDb.Card<ProtoMcLisaLightningRose>(),
        ModelDb.Card<ProtoMcRosariaRavagingConfession>(),
        // The thirteen the engine hooks unblocked, in the same sec.3 order.
        ModelDb.Card<ProtoMcDionaIcyPaws>(),
        ModelDb.Card<ProtoMcNoelleSweepingTime>(),
        ModelDb.Card<ProtoMcBarbaraMelodyLoop>(),
        ModelDb.Card<ProtoMcBennettPassionOverload>(),
        ModelDb.Card<ProtoMcDahliaSacramentalShower>(),
        ModelDb.Card<ProtoMcDahliaFavonianFavor>(),
        ModelDb.Card<ProtoMcDurinBinaryForm>(),
        // The AoE trim (2026-10-03) split Durin in two: the burst.
        ModelDb.Card<ProtoMcDurinPrincipleOfPurity>(),
        ModelDb.Card<ProtoMcRazorClawAndThunder>(),
        ModelDb.Card<ProtoMcRazorLightningFang>(),
        ModelDb.Card<ProtoMcVarkaSturmUndDrang>(),
        ModelDb.Card<ProtoMcAmberExplosivePuppet>(),
        ModelDb.Card<ProtoMcEulaGlacialIllumination>(),
        ModelDb.Card<ProtoMcMikaStarfrostSwirl>(),
        // THE KLEE-ONLY COMPANIONS (2026-10-03, sec.4): four rows that read
        // nothing of Klee's join the shared pool. Fischl's, Sucrose's and
        // Nicole's were her stand-ins; Qiqi's was her coven Personal.
        ModelDb.Card<ProtoMcFischlSinfulHex>(),
        ModelDb.Card<ProtoMcSucroseMollisFavonius>(),
        ModelDb.Card<ProtoMcNicoleLadderOfAscent>(),
        ModelDb.Card<ProtoMcQiqiHeraldOfFrost>(),
    };

    /// <summary>
    /// Inazuma's twenty-four rewritten Universals, in the approved workshop's
    /// sec.3 character order (<c>companion-workshop-inazuma-2026-09-01.md</c>,
    /// approved 2026-09-01 at its four default picks). Fifteen re-author a
    /// shipped row and nine give a character with no row today its first.
    ///
    /// TWENTY-FOUR AND NOT TWENTY-FIVE, and the number is worth writing down:
    /// the document's sec.4 counts "25 Universals, 1 Personal" while its sec.3
    /// enumerates 24 Universals plus Gorou's Kokomi-side Personal, and the
    /// rarity split it prints (9 Common, 12 Uncommon, 4 Rare) only closes when
    /// the Personal is counted among the Uncommons. The ENUMERATION is what is
    /// built. A Personal is Kokomi's kit rather than a companion offer, and no
    /// stand-in is a Universal either, so neither is here.
    ///
    /// TWENTY-ONE SINCE THE KOKOMI RE-FOUNDING (2026-10-12): Gorou's three
    /// are Kokomi's own cards (<c>C.KOKOMI_OWN_COMPANION_IDS</c>), in her
    /// pool and not in the shared roster.
    ///
    /// THIRTY-FOUR SINCE THE INAZUMA POOL REWORK (2026-10-18,
    /// <c>review/active/inazuma-companions-2026-10-18.md</c>): Aurous Blaze,
    /// Musou no Hitotachi and Superlative Superstrength cut, eleven new, then
    /// five more and Hyouka moved to Uncommon when the pool grew to two cards
    /// a character (8 / 16 / 10). tier0 twin: <c>C.INAZUMA_OVERHAUL_POOL_IDS</c>.
    ///
    /// NOTHING WAS DROPPED. Every one of the twenty-four prints inside the
    /// grammar the emitter speaks once this arm's fifteen powers exist -- which
    /// is what most of <c>CompanionOverhaulInazuma.cs</c> is -- so the rule the
    /// Mondstadt waves kept ("a card that cannot be printed as written is left
    /// OUT rather than replaced by a simpler card") bit on nothing here.
    /// </summary>
    private static IEnumerable<CardModel> InazumaUniversals() => new CardModel[]
    {
        ModelDb.Card<ProtoMiSayuFuuinDash>(),
        ModelDb.Card<ProtoMiSayuDaruma>(),
        ModelDb.Card<ProtoMiSayuNaptime>(),
        ModelDb.Card<ProtoMiShinobuSanctifyingRing>(),
        ModelDb.Card<ProtoMiShinobuGrassRing>(),
        ModelDb.Card<ProtoMiShinobuThundergrust>(),
        ModelDb.Card<ProtoMiThomaBlazingBarrier>(),
        ModelDb.Card<ProtoMiThomaCrimsonOoyoroi>(),
        ModelDb.Card<ProtoMiSaraCrowfeatherCover>(),
        ModelDb.Card<ProtoMiSaraTenguStormcall>(),
        ModelDb.Card<ProtoMiKazuhaSlash>(),
        ModelDb.Card<ProtoMiYaeSesshouSakura>(),
        ModelDb.Card<ProtoMiAyakaSoumetsu>(),
        ModelDb.Card<ProtoMiAyakaHyouka>(),
        ModelDb.Card<ProtoMiAyatoKyouka>(),
        ModelDb.Card<ProtoMiHeizouHeartstopper>(),
        ModelDb.Card<ProtoMiHeizouWindmusterKick>(),
        ModelDb.Card<ProtoMiKiraraSurpriseDispatch>(),
        ModelDb.Card<ProtoMiMizukiAnraku>(),
        ModelDb.Card<ProtoMiMizukiAisaUtamakura>(),
        ModelDb.Card<ProtoMiChioriHasode>(),
        ModelDb.Card<ProtoMiIttoUshi>(),
        ModelDb.Card<ProtoMiRaidenEuthymia>(),
        ModelDb.Card<ProtoMiRaidenMusouNoHitotachi>(),
        ModelDb.Card<ProtoMiIttoRoyalDescent>(),
        ModelDb.Card<ProtoMiYoimiyaNiwabi>(),
        ModelDb.Card<ProtoMiKazuhaChihayaburu>(),
        ModelDb.Card<ProtoMiWandererHanega>(),
        ModelDb.Card<ProtoMiAyatoKyoukaFuushi>(),
        ModelDb.Card<ProtoMiKiraraMeowteorKick>(),
        ModelDb.Card<ProtoMiYoimiyaRyuukinSaxifrage>(),
        ModelDb.Card<ProtoMiWandererKyougen>(),
        ModelDb.Card<ProtoMiChioriTwinBlades>(),
        ModelDb.Card<ProtoMiYaeSacredSakurasFavor>(),
    };

    /// <summary>
    /// Fontaine's sixteen, ported as they are (legacy cleanup pick 4,
    /// 2026-10-01): the shipped rows' bodies and upgrades on `proto_mf_` ids,
    /// in the sheet's order. A Fontaine rework is its own paper. tier0 twin:
    /// <c>C.FONTAINE_OVERHAUL_POOL_IDS</c>.
    /// </summary>
    private static IEnumerable<CardModel> FontaineUniversals() => new CardModel[]
    {
        ModelDb.Card<ProtoMfChevreuseInterdictionFire>(),
        ModelDb.Card<ProtoMfChevreuseVanguardsValor>(),
        ModelDb.Card<ProtoMfChevreuseBurstingGrenades>(),
        ModelDb.Card<ProtoMfLynetteEnigmaticFeint>(),
        ModelDb.Card<ProtoMfLynetteBoxTrick>(),
        ModelDb.Card<ProtoMfLynetteAstonishingShift>(),
        ModelDb.Card<ProtoMfCharlotteFreezingPoint>(),
        ModelDb.Card<ProtoMfCharlotteEnduringFrosthelm>(),
        ModelDb.Card<ProtoMfCharlotteSnappySilhouette>(),
        ModelDb.Card<ProtoMfFreminetPersDeploy>(),
        ModelDb.Card<ProtoMfFreminetPressurizedFloe>(),
        ModelDb.Card<ProtoMfFreminetShatteringPressure>(),
        ModelDb.Card<ProtoMfNaviaCannonFireSupport>(),
        ModelDb.Card<ProtoMfClorindeImpaleTheNight>(),
        ModelDb.Card<ProtoMfNeuvilletteAncientSeaAuthority>(),
        ModelDb.Card<ProtoMfArlecchinoMasqueRedDeath>(),
    };
}
