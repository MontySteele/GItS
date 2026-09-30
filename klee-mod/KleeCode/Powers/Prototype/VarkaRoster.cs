using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;

namespace KleeMod.Powers;

/// <summary>
/// VARKA'S DECK, RELIC AND POOL (the Oath rework, sec.5 and sec.6).
/// LISTED BY TYPE, not filtered by id prefix, for
/// <c>KokomiOverhaulRoster.OfferablePool</c>'s reason: a deleted row takes its
/// type with it and this file stops building.
/// </summary>
internal static class VarkaRoster
{
    /// <summary>
    /// The starter (sec.5): "Strike x4, Defend x4 (base game), and: One
    /// starting Knight, at random each run ... Windbound Execution". The deck
    /// lists Amber: Precise Shot; Boreas's Fang rolls the run's Knight when the
    /// run begins (<c>BoreasFang.AfterObtained</c>). The base pair is the
    /// Silent's, because his pool borrows her green frame.
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
        ModelDb.Card<ProtoVkWindboundExecution>(),
        ModelDb.Card<ProtoVkAmberFieryRain>(),
    };

    /// <summary>The Strike a base-game effect is handed when it asks the
    /// character for one (Large Capsule, <see cref="ArmStarterBasics"/>).
    /// </summary>
    internal static CardModel StarterStrike() => ModelDb.Card<StrikeSilent>();

    /// <summary>The Defend half of <see cref="StarterStrike"/>'s pair.</summary>
    internal static CardModel StarterDefend() => ModelDb.Card<DefendSilent>();

    /// <summary>His starting relic, Boreas's Fang (sec.4).</summary>
    internal static IReadOnlyList<RelicModel> StartingRelics() =>
        new RelicModel[]
        {
            ModelDb.Relic<Relics.BoreasFang>(),
        };

    /// <summary>
    /// The pool: forty-one cards (sec.6), sixteen Commons, seventeen
    /// Uncommons and eight Rares, the nine pool Knights among them. "Pool
    /// target 78 comes after the prototype."
    ///
    /// NO ANCIENT CARD, because the paper designs none. Darv's Dusty Tome
    /// draws an Ancient from this set and softlocks on an empty draw, so Four
    /// Winds' Ascension carries BaseLib's <c>ITomeCard</c> mark instead
    /// (the row's <c>dusty_tome</c> tag): the Tome hands him that, upgraded.
    /// </summary>
    internal static IReadOnlyList<CardModel> Pool() => new CardModel[]
    {
        // Common (16)
        ModelDb.Card<ProtoVkSquall>(),
        ModelDb.Card<ProtoVkUpdraft>(),
        ModelDb.Card<ProtoVkGaleSweep>(),
        ModelDb.Card<ProtoVkWindWall>(),
        ModelDb.Card<ProtoVkFavoniusDrill>(),
        ModelDb.Card<ProtoVkAmberBaronBunny>(),
        ModelDb.Card<ProtoVkBarbaraShowBegin>(),
        ModelDb.Card<ProtoVkLisaVioletArc>(),
        ModelDb.Card<ProtoVkKaeyaFrostgnaw>(),
        ModelDb.Card<ProtoVkRazorClawAndThunder>(),
        ModelDb.Card<ProtoVkMikaStarfrostSwirl>(),
        ModelDb.Card<ProtoVkJeanDandelionBreeze>(),
        ModelDb.Card<ProtoVkKnightlyGuard>(),
        ModelDb.Card<ProtoVkOathswornStrike>(),
        ModelDb.Card<ProtoVkCrosswind>(),
        ModelDb.Card<ProtoVkRisingGale>(),
        // Uncommon (17)
        ModelDb.Card<ProtoVkTempestCharge>(),
        ModelDb.Card<ProtoVkFavoniusCut>(),
        ModelDb.Card<ProtoVkGrandMastersOrder>(),
        ModelDb.Card<ProtoVkKnightsRollCall>(),
        ModelDb.Card<ProtoVkTailwindStride>(),
        ModelDb.Card<ProtoVkEyeOfTheStorm>(),
        ModelDb.Card<ProtoVkStormwardStance>(),
        ModelDb.Card<ProtoVkOathOfTheKnights>(),
        ModelDb.Card<ProtoVkRallyToTheBanner>(),
        ModelDb.Card<ProtoVkDilucSearingOnslaught>(),
        ModelDb.Card<ProtoVkEulaIcetideVortex>(),
        ModelDb.Card<ProtoVkBarbaraWhisperOfWater>(),
        ModelDb.Card<ProtoVkFavonianStandard>(),
        ModelDb.Card<ProtoVkChangeOfGuard>(),
        ModelDb.Card<ProtoVkStormSurge>(),
        ModelDb.Card<ProtoVkTailwindGuard>(),
        ModelDb.Card<ProtoVkUnfurledBanner>(),
        // Rare (8)
        ModelDb.Card<ProtoVkConvergingWinds>(),
        ModelDb.Card<ProtoVkBoreasUnbound>(),
        ModelDb.Card<ProtoVkWallOfGales>(),
        ModelDb.Card<ProtoVkFourWindsAccord>(),
        ModelDb.Card<ProtoVkSwornBrotherhood>(),
        ModelDb.Card<ProtoVkNorthwindAvatar>(),
        ModelDb.Card<ProtoVkDawnWindsMarch>(),
        ModelDb.Card<ProtoVkAzureDevour>(),
    };

    /// <summary>
    /// Every card of his that must resolve <c>CardModel.Pool</c> to his pool:
    /// his generated rows (the pool's among them, harmless -- membership is
    /// not the offer). Change of Guard's four element faces ride
    /// <c>VarkaModalOptions.All</c> beside this.
    /// </summary>
    internal static IReadOnlyList<CardModel> Members() =>
        PrototypeCards.For(VarkaPrototype.CharacterId).ToList();
}
