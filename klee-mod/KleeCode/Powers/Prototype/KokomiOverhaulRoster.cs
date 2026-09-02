using System.Collections.Generic;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Relics;

namespace KleeMod.Powers;

/// <summary>
/// THE THREE WIRING SEAMS, and there are exactly three: what Kokomi OPENS
/// with, what she OPENS HOLDING, and what she can be OFFERED. Sim twins:
/// <c>tier0.content.loader._starter_ids</c> and
/// <c>tier0.content.loader.pool_replacement</c>, which exist for the same
/// reason -- both readers of a starter and all five offer surfaces go through
/// one door each, so the two engines cannot disagree about what a run is. (The
/// relic has no sim twin, because tier 0.5 gives no character a starting relic
/// it did not draft.)
///
/// WHY THE STARTER IS A REPLACEMENT AND NOT A SUBSTITUTION. The Kurage's-memory
/// arm swaps one of the twelve slots and leaves eleven standing, because its
/// rule is an addition. This arm's rule change is total: the shipped Water's
/// Edge and Coral Guard are priced inside an exhaust-for-Charge economy the
/// brief retires, the shipped Kurage's Oath is a Power that wards per jellyfish
/// pulse rather than a Skill that Exerts for Tide, and the shipped Bake-Kurage
/// summons a jellyfish that is now always out. All ten move, and the deck
/// shrinks from TWELVE to TEN -- which is the slice packet's own sec.3 count,
/// and is a real consequence rather than an oversight: the twelve-card shape
/// was ruled for a deck that mills itself, and nothing in this arm exhausts.
///
/// WHY THE RELIC MOVES TOO. The Pearl of Wisdom's printed body IS the exhaust
/// funnel ("Whenever a card is Exhausted, gain Charge and Burst Energy"), which
/// is the first thing the brief's sec.4 retires, so a run holding it would
/// print a rule the arm has turned off. Tamanooya's Casket takes the slot and
/// carries rule 4 instead. THE COMPANION REWARD SLOT SURVIVES THE SWAP, because
/// it rides the relic in this mod purely for lifetime reasons and the slice's
/// Commander loop draws its whole army from it.
///
/// WHY THE POOL IS A REPLACEMENT TOO. Same argument, one screen over: a reward
/// screen that could still offer the shipped 76 would be offering cards written
/// against rules the run is no longer playing -- an Exhaust that pays Charge, a
/// Muster that transforms, a Burst that gates. Slice one's own scope statement
/// is that the 28 rows are her only reward pool for the prototype run.
///
/// THE OVERHAUL WINS WHERE IT MEETS THE KURAGE'S MEMORY. A dev build compiles
/// this arm AND that one, and both want her starter. They are alternatives, not
/// layers -- the memory is priced inside the Charge bank this arm retires -- so
/// with <c>KokomiOverhaul.Enabled</c> the memory's starter substitution is not
/// reached and its rules are switched off at the funnel. With it off, nothing
/// here runs and the memory arm owns the starter exactly as before, which is
/// the acceptance condition.
/// </summary>
internal static class KokomiOverhaulRoster
{
    /// <summary>
    /// Kokomi's ten opening cards under the arm: Water's Edge x3, Coral Guard
    /// x3, Kurage's Oath x2, Rising Tide, Stolen Chapter (slice packet sec.3,
    /// in its order).
    ///
    /// THE COMPANION ROLL FINDS NO SLOT, by construction and reported rather
    /// than hidden. <c>KokomiStartingCompanionsPatch</c> matches on the shipped
    /// <c>SayuDarumaGift</c> type to roll Sayu-or-Shinobu, and none of these ten
    /// is that type -- so under this arm she opens with NO companions at all.
    /// That is a real consequence: the slice's Commander loop draws its whole
    /// army from the reward slot instead, which is what its sec.4 says it does
    /// ("Companions come from the Inazuma Universals already in the pool").
    /// </summary>
    internal static IEnumerable<CardModel> StartingDeck() => new CardModel[]
    {
        ModelDb.Card<ProtoKkWatersEdge>(),
        ModelDb.Card<ProtoKkWatersEdge>(),
        ModelDb.Card<ProtoKkWatersEdge>(),
        ModelDb.Card<ProtoKkCoralGuard>(),
        ModelDb.Card<ProtoKkCoralGuard>(),
        ModelDb.Card<ProtoKkCoralGuard>(),
        ModelDb.Card<ProtoKkKuragesOath>(),
        ModelDb.Card<ProtoKkKuragesOath>(),
        ModelDb.Card<ProtoKkRisingTide>(),
        ModelDb.Card<ProtoKkStolenChapter>(),
    };

    /// <summary>
    /// Kokomi's WHOLE offerable pool under the arm: the slice's 28 rows and
    /// nothing else.
    ///
    /// LISTED BY TYPE, not filtered by id prefix. A prefix match would be a
    /// second, softer definition of "which rows are the slice" living next to
    /// the sheet's own, and it would fail silently the day a row is renamed.
    /// These are the same 28 ids as <c>C.KOKOMI_OVERHAUL_POOL_IDS</c>, in the
    /// same order; the compiler holds the correspondence, because a deleted row
    /// takes its type with it and this file stops building.
    ///
    /// ANCIENTS ARE NOT HERE, matching the Klee arm's own default and for the
    /// same reason: the design is silent, and "her only reward pool" read
    /// literally means Dusty Tome and its kin see the slice and nothing else.
    /// </summary>
    internal static IEnumerable<CardModel> OfferablePool() => new CardModel[]
    {
        // Priestess -- feed, hold, surge (9)
        ModelDb.Card<ProtoKkTidalPrayer>(),
        ModelDb.Card<ProtoKkSeaSpray>(),
        ModelDb.Card<ProtoKkDeepCurrent>(),
        ModelDb.Card<ProtoKkBreaker>(),
        ModelDb.Card<ProtoKkHighTide>(),
        ModelDb.Card<ProtoKkUndertow>(),
        ModelDb.Card<ProtoKkSongOfPearls>(),
        ModelDb.Card<ProtoKkNereidsAscension>(),
        ModelDb.Card<ProtoKkSangoIsshin>(),
        // Strategist -- the plan was written last turn (8)
        ModelDb.Card<ProtoKkBattlePlan>(),
        ModelDb.Card<ProtoKkAmbush>(),
        ModelDb.Card<ProtoKkReadTheField>(),
        ModelDb.Card<ProtoKkFeint>(),
        ModelDb.Card<ProtoKkContingency>(),
        ModelDb.Card<ProtoKkTreatise>(),
        ModelDb.Card<ProtoKkWarCouncil>(),
        ModelDb.Card<ProtoKkTheArtOfWar>(),
        // Commander -- Gorou, go (4)
        ModelDb.Card<ProtoKkRally>(),
        ModelDb.Card<ProtoKkVanguard>(),
        ModelDb.Card<ProtoKkOrders>(),
        ModelDb.Card<ProtoKkTheGeneralsBanner>(),
        // Currencies and defence (7)
        ModelDb.Card<ProtoKkQuietStudy>(),
        ModelDb.Card<ProtoKkSaltLine>(),
        ModelDb.Card<ProtoKkCleansingTide>(),
        ModelDb.Card<ProtoKkTheCloudsLikeWaves>(),
        ModelDb.Card<ProtoKkReadingTheTide>(),
        ModelDb.Card<ProtoKkCoralBulwark>(),
        ModelDb.Card<ProtoKkWatatsumisBlessing>(),
    };

    /// <summary>Her one starting relic under the arm. A list of one, so the
    /// seam in <c>Kokomi.StartingRelics</c> is one return rather than a
    /// conditional inside a collection initializer.</summary>
    internal static IReadOnlyList<RelicModel> StartingRelics() =>
        new RelicModel[]
        {
            ModelDb.Relic<Relics.TamanooyasCasket>(),
        };
}
