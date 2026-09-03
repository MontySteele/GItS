using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
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
/// <see cref="CompanionSlot"/> (the fourth reward slot),
/// <see cref="CompanionBanner"/> (the Featured Banner's five-star roster) and
/// the shop channel all read. Redirecting that one property moves all three at
/// once, which is the point of putting the seam at the source rather than at
/// the three mouths.
///
/// A REPLACEMENT OF ONE NATION, NOT OF THE ROSTER. The workshop is a Mondstadt
/// document (its sec.6: "It does not ... decide Inazuma (its own document, same
/// rules)"), so Inazuma and Fontaine come through untouched and the seventeen
/// shipped Mondstadt rows do not come through at all.
///
/// THE KEPT HALF IS FILTERED BY NATION and the ADDED HALF IS LISTED BY TYPE,
/// and the asymmetry is deliberate. The arm's rule about the other two nations
/// is literally "not Mondstadt", so a hand-copied list of thirty Inazuma and
/// Fontaine rows would be a second, staler statement of a rule the sheet
/// already carries -- it would silently drop the next Fontaine row somebody
/// ships. The arm's rule about Mondstadt is "these rows and nothing else", and
/// there a prefix match would be a second, softer definition of which rows are
/// the slice: it would fail silently the day a row is renamed. Listing types
/// puts the correspondence in the compiler's hands, because a deleted row takes
/// its class with it and this file stops building.
/// </summary>
internal static class CompanionOverhaulRoster
{
    /// <summary>tier0 <c>C.COMPANION_OVERHAUL_NATION</c>. The FIRST nation the
    /// arm replaces, named once so the line that decides it is greppable.</summary>
    internal const string Nation = "mondstadt";

    /// <summary>tier0 <c>C.INAZUMA_OVERHAUL_NATION</c>. The second, added when
    /// the Inazuma workshop was approved and built (2026-09-02).</summary>
    internal const string InazumaNation = "inazuma";

    /// <summary>tier0 <c>C.COMPANION_OVERHAUL_NATIONS</c>: the nations this arm
    /// replaces, and the one list the kept half is filtered against. Fontaine
    /// is deliberately absent -- its workshop does not exist yet, and both
    /// approved documents say so in their own sec.6.</summary>
    private static readonly string[] Nations = { Nation, InazumaNation };

    private static IReadOnlyList<CardModel>? _roster;

    /// <summary>
    /// Every companion an offer surface may see while the arm is on: the other
    /// nations' shipped rows, then Mondstadt's rewritten Universals.
    ///
    /// CACHED, and lazily. <c>ModelDb.Card&lt;T&gt;()</c> throws
    /// KeyNotFoundException until the models are built (they are
    /// <c>autoAdd: false</c> and constructed at pool-build time), and a static
    /// constructor that throws POISONS ITS TYPE for the life of the process --
    /// the EB-194 lesson, applied here before it can be learned twice.
    /// </summary>
    internal static IReadOnlyList<CardModel> Roster() =>
        _roster ??= CompanionRoster.All
            .Where(c => !Nations.Contains((c as ICompanionCard)?.Nation))
            .Concat(Universals())
            .Concat(InazumaUniversals())
            // AND KLEE'S COVEN PERSONALS (R236). They are on this list for the
            // reason the Universals are -- one roster, three offer surfaces --
            // and it is the `PersonalPool` filter at each offer site
            // (`CompanionPool.IsOfferable`) that keeps them Klee's, not a
            // second roster. `CompanionCovenRoster` says why Prune's shipped
            // row needs no exclusion of its own.
            .Concat(CompanionCovenRoster.Personals())
            .Concat(InazumaPersonals())
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
        ModelDb.Card<ProtoMcRazorClawAndThunder>(),
        ModelDb.Card<ProtoMcRazorLightningFang>(),
        ModelDb.Card<ProtoMcVarkaSturmUndDrang>(),
        ModelDb.Card<ProtoMcAmberExplosivePuppet>(),
        ModelDb.Card<ProtoMcEulaGlacialIllumination>(),
        ModelDb.Card<ProtoMcMikaStarfrostSwirl>(),
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
    /// NOTHING WAS DROPPED. Every one of the twenty-four prints inside the
    /// grammar the emitter speaks once this arm's fifteen powers exist -- which
    /// is what most of <c>CompanionOverhaulInazuma.cs</c> is -- so the rule the
    /// Mondstadt waves kept ("a card that cannot be printed as written is left
    /// OUT rather than replaced by a simpler card") bit on nothing here.
    /// </summary>
    private static IEnumerable<CardModel> InazumaUniversals() => new CardModel[]
    {
        ModelDb.Card<ProtoMiGorouInuzaka>(),
        ModelDb.Card<ProtoMiGorouWarBanner>(),
        ModelDb.Card<ProtoMiGorouJuuga>(),
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
        ModelDb.Card<ProtoMiIttoSuperlativeSuperstrength>(),
        ModelDb.Card<ProtoMiRaidenMusouNoHitotachi>(),
        ModelDb.Card<ProtoMiKazuhaSlash>(),
        ModelDb.Card<ProtoMiYaeSesshouSakura>(),
        ModelDb.Card<ProtoMiYoimiyaAurousBlaze>(),
        ModelDb.Card<ProtoMiAyakaSoumetsu>(),
        ModelDb.Card<ProtoMiAyatoKyouka>(),
        ModelDb.Card<ProtoMiHeizouHeartstopper>(),
        ModelDb.Card<ProtoMiKiraraSurpriseDispatch>(),
        ModelDb.Card<ProtoMiMizukiAnraku>(),
        ModelDb.Card<ProtoMiChioriHasode>(),
    };

    /// <summary>
    /// The Inazuma workshop's ONE Personal (R236, its sec.3 Gorou), and it is
    /// a separate list because it is a different kind of row.
    ///
    /// A PERSONAL IS IN THE ROSTER AND NOT IN THE POOL. The roster is what an
    /// offer surface may SEE; which of those rows a given character may be
    /// OFFERED is <see cref="CompanionPool"/>'s question, and it already
    /// answers it -- a row's <c>PersonalPool</c> gates it to its own character,
    /// the door Prune has come through since the shipped Mondstadt sheet. A
    /// Personal left out of the roster entirely could not be offered to its
    /// own character either, which is why it is here rather than nowhere.
    ///
    /// tier0 twin: <c>C.INAZUMA_OVERHAUL_PERSONAL_IDS</c>, added to
    /// <c>companion_roster_replacement</c> beside the two pool lists and kept
    /// out of both.
    /// </summary>
    private static IEnumerable<CardModel> InazumaPersonals() => new CardModel[]
    {
        ModelDb.Card<ProtoMiGorouCrystalCollapse>(),
    };
}
