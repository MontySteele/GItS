using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;

namespace KleeMod.Powers;

/// <summary>
/// VARKA'S DECK, RELIC AND POOL, prototype batch one (sec.10.2, sec.10.3).
/// LISTED BY TYPE, not filtered by id prefix, for
/// <c>KokomiOverhaulRoster.OfferablePool</c>'s reason: a deleted row takes its
/// type with it and this file stops building.
/// </summary>
internal static class VarkaRoster
{
    /// <summary>
    /// The starter (sec.10.2): "Strike x4, Defend x4 (base game), and"
    /// Knights' Muster and Four Winds' Ascension. The base pair is Silent's,
    /// because his pool borrows her green frame (the rule every kit follows:
    /// the base pair of the borrowed frame).
    /// </summary>
    internal static IEnumerable<CardModel> StartingDeck() => new CardModel[]
    {
        ModelDb.Card<StrikeSilent>(),
        ModelDb.Card<StrikeSilent>(),
        ModelDb.Card<StrikeSilent>(),
        ModelDb.Card<StrikeSilent>(),
        ModelDb.Card<DefendSilent>(),
        ModelDb.Card<DefendSilent>(),
        ModelDb.Card<DefendSilent>(),
        ModelDb.Card<DefendSilent>(),
        ModelDb.Card<ProtoVkKnightsMuster>(),
        ModelDb.Card<ProtoVkFourWindsAscension>(),
    };

    /// <summary>The Strike a base-game effect is handed when it asks the
    /// character for one (Large Capsule, <see cref="ArmStarterBasics"/>).
    /// </summary>
    internal static CardModel StarterStrike() => ModelDb.Card<StrikeSilent>();

    /// <summary>The Defend half of <see cref="StarterStrike"/>'s pair.</summary>
    internal static CardModel StarterDefend() => ModelDb.Card<DefendSilent>();

    /// <summary>His starting relic, Boreas's Fang (sec.10.1).</summary>
    internal static IReadOnlyList<RelicModel> StartingRelics() =>
        new RelicModel[]
        {
            ModelDb.Relic<Relics.BoreasFang>(),
        };

    /// <summary>
    /// The pool, batch one: nineteen cards (sec.10.3), ten Commons (the four
    /// Knights among them), seven Uncommons and two Rares. "Pool target 78
    /// comes later."
    ///
    /// NO ANCIENT CARD, because sec.10 designs none. Darv's Dusty Tome draws
    /// an Ancient from this set and softlocks on an empty draw, so Four
    /// Winds' Ascension carries BaseLib's <c>ITomeCard</c> mark instead
    /// (the row's <c>dusty_tome</c> tag): the Tome hands him that, upgraded.
    /// </summary>
    internal static IReadOnlyList<CardModel> Pool() => new CardModel[]
    {
        // Common (10)
        ModelDb.Card<ProtoVkWindboundExecution>(),
        ModelDb.Card<ProtoVkSquall>(),
        ModelDb.Card<ProtoVkUpdraft>(),
        ModelDb.Card<ProtoVkGaleSweep>(),
        ModelDb.Card<ProtoVkWindWall>(),
        ModelDb.Card<ProtoVkFavoniusDrill>(),
        ModelDb.Card<ProtoVkAmberBaronBunny>(),
        ModelDb.Card<ProtoVkBarbaraShowBegin>(),
        ModelDb.Card<ProtoVkLisaVioletArc>(),
        ModelDb.Card<ProtoVkKaeyaFrostgnaw>(),
        // Uncommon (7)
        ModelDb.Card<ProtoVkTempestCharge>(),
        ModelDb.Card<ProtoVkFavoniusCut>(),
        ModelDb.Card<ProtoVkGrandMastersOrder>(),
        ModelDb.Card<ProtoVkKnightsRollCall>(),
        ModelDb.Card<ProtoVkEyeOfTheStorm>(),
        ModelDb.Card<ProtoVkStormwardStance>(),
        ModelDb.Card<ProtoVkTailwindStride>(),
        // Rare (2)
        ModelDb.Card<ProtoVkConvergingWinds>(),
        ModelDb.Card<ProtoVkBoreasUnbound>(),
    };

    /// <summary>
    /// Every card of his that must resolve <c>CardModel.Pool</c> to his pool:
    /// his generated rows (the pool's among them, harmless -- membership is
    /// not the offer) and the hand-written Knights' Muster. The four
    /// choose-a-Knight faces ride <c>VarkaModalOptions.All</c> beside this.
    /// </summary>
    internal static IReadOnlyList<CardModel> Members() =>
        PrototypeCards.For(VarkaPrototype.CharacterId)
            .Append(ModelDb.Card<ProtoVkKnightsMuster>())
            .ToList();
}
