using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;

namespace KleeMod.Powers;

/// <summary>
/// YAE'S DECK, RELIC AND POOL (<c>review/active/yae-card-paper-2026-10-13.md</c>
/// sec.3 and sec.5). LISTED BY TYPE, not filtered by id prefix, for
/// <c>VarkaRoster</c>'s reason: a deleted row takes its type with it and this
/// file stops building.
/// </summary>
internal static class YaeRoster
{
    /// <summary>
    /// The starter (sec.3): "Strike x4, Defend x4 (base game), and: Yakan
    /// Evocation, Proofread". The base pair is the Defect's, because her pool
    /// borrows his blue frame (the arrangement every kit makes with the
    /// character whose frame it wears).
    /// </summary>
    internal static IEnumerable<CardModel> StartingDeck() => new CardModel[]
    {
        ModelDb.Card<StrikeDefect>(),
        ModelDb.Card<StrikeDefect>(),
        ModelDb.Card<StrikeDefect>(),
        ModelDb.Card<StrikeDefect>(),
        ModelDb.Card<DefendDefect>(),
        ModelDb.Card<DefendDefect>(),
        ModelDb.Card<DefendDefect>(),
        ModelDb.Card<DefendDefect>(),
        ModelDb.Card<ProtoYmYakanEvocation>(),
        ModelDb.Card<ProtoYmProofread>(),
    };

    /// <summary>The Strike a base-game effect is handed when it asks the
    /// character for one (Large Capsule, <see cref="ArmStarterBasics"/>).
    /// </summary>
    internal static CardModel StarterStrike() => ModelDb.Card<StrikeDefect>();

    /// <summary>The Defend half of <see cref="StarterStrike"/>'s pair.</summary>
    internal static CardModel StarterDefend() => ModelDb.Card<DefendDefect>();

    /// <summary>Her starting relic, Meditations of a Yako (sec.3).</summary>
    internal static IReadOnlyList<RelicModel> StartingRelics() =>
        new RelicModel[]
        {
            ModelDb.Relic<Relics.MeditationsOfAYako>(),
        };

    /// <summary>
    /// The pool: batch one's THIRTY (sec.5), nine Commons, thirteen
    /// Uncommons and eight Rares, in the sheet's order. A STAGED KIT BELOW 78:
    /// the second half of the pool waits on [USER]'s first play and the audit
    /// that follows it (the paper's "Not in this batch, said so"), as
    /// Furina's 24-row slice and Varka's 41 waited before theirs.
    /// </summary>
    internal static IReadOnlyList<CardModel> Pool() => new CardModel[]
    {
        // Common (9)
        ModelDb.Card<ProtoYmKitsuneFlash>(),
        ModelDb.Card<ProtoYmThunderRite>(),
        ModelDb.Card<ProtoYmShrineOffering>(),
        ModelDb.Card<ProtoYmTwinSakura>(),
        ModelDb.Card<ProtoYmDeadline>(),
        ModelDb.Card<ProtoYmFoxFireDraft>(),
        ModelDb.Card<ProtoYmSlyStrike>(),
        ModelDb.Card<ProtoYmFoxTrick>(),
        ModelDb.Card<ProtoYmShrineMaidensGuard>(),
        // Uncommon (13)
        ModelDb.Card<ProtoYmSakuraGrove>(),
        ModelDb.Card<ProtoYmKitsuneRite>(),
        ModelDb.Card<ProtoYmThunderboltTithe>(),
        ModelDb.Card<ProtoYmRootedShrine>(),
        ModelDb.Card<ProtoYmEdictOfCleansing>(),
        ModelDb.Card<ProtoYmBestseller>(),
        ModelDb.Card<ProtoYmPrintRun>(),
        ModelDb.Card<ProtoYmFootnote>(),
        ModelDb.Card<ProtoYmSakuraSeal>(),
        ModelDb.Card<ProtoYmSerialization>(),
        ModelDb.Card<ProtoYmManuscriptPile>(),
        ModelDb.Card<ProtoYmKitsuneGuile>(),
        ModelDb.Card<ProtoYmFoxfireLure>(),
        // Rare (8)
        ModelDb.Card<ProtoYmTenkoKenshin>(),
        ModelDb.Card<ProtoYmFoxsMooncall>(),
        ModelDb.Card<ProtoYmYakanOffering>(),
        ModelDb.Card<ProtoYmTheSevenGlamours>(),
        ModelDb.Card<ProtoYmSakuraChanneling>(),
        ModelDb.Card<ProtoYmMischievousTeasing>(),
        ModelDb.Card<ProtoYmRebornAsGuujiYae>(),
        ModelDb.Card<ProtoYmEditorInChief>(),
    };

    /// <summary>THE OFFER (<c>YaeCardPool.FilterThroughEpochs</c>): the pool.
    /// No Ancients and no co-op tier yet (the paper's "next batch").</summary>
    internal static IEnumerable<CardModel> OfferablePool() => Pool();

    /// <summary>Every card of hers that must resolve <c>CardModel.Pool</c> to
    /// her pool: her generated rows. The five Annotation faces ride
    /// <see cref="YaeModalOptions.All"/> beside this.</summary>
    internal static IReadOnlyList<CardModel> Members() =>
        PrototypeCards.For(YaePrototype.CharacterId).ToList();
}
