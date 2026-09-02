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
    /// <summary>tier0 <c>C.COMPANION_OVERHAUL_NATION</c>. The one nation this
    /// arm replaces, named once so the line that decides it is greppable.</summary>
    internal const string Nation = "mondstadt";

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
            .Where(c => (c as ICompanionCard)?.Nation != Nation)
            .Concat(Universals())
            .ToList();

    /// <summary>
    /// Mondstadt's twenty-one rewritten Universals, in the workshop's sec.3
    /// character order. Coven Personals (its sec.4) and Klee-only stand-ins are
    /// NOT here: this arm rewrites the Universal pool and nothing else, and a
    /// Personal is Klee's kit rather than a companion offer.
    ///
    /// TWENTY-ONE OF THE WORKSHOP'S THIRTY-FOUR. The thirteen that are missing
    /// are missing because their printed text wants an engine hook that does
    /// not exist in either engine -- a Block-absorption trigger, a
    /// pre-enemy-attack trap, a next-Attack element override, a Swirl event, an
    /// Attack counter, a next-Attack discount. Each one is named, with the hook
    /// it wanted, in <c>docs/notes/prototype-surface-provenance.md</c>. A card
    /// that cannot be printed as written is left OUT rather than replaced by a
    /// simpler card, which is the same rule the Klee overhaul applied to
    /// Vermillion Pact.
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
    };
}
