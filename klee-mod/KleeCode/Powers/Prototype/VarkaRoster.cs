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
    /// The pool: SEVENTY-EIGHT cards since the expansion (2026-10-01,
    /// review/active/varka-expansion-2026-10-01.md sec.3): twenty Commons,
    /// thirty-five Uncommons and twenty-three Rares, the thirteen pool
    /// Knights among them. It was forty-one (fifteen, eighteen and eight;
    /// the groups below keep the sheet's order, and each card's own rarity
    /// is what the game reads).
    ///
    /// NO ANCIENT CARD, because the paper designs none. Darv's Dusty Tome
    /// draws an Ancient from this set and softlocks on an empty draw, so Four
    /// Winds' Ascension carries BaseLib's <c>ITomeCard</c> mark instead
    /// (the row's <c>dusty_tome</c> tag): the Tome hands him that, upgraded.
    /// </summary>
    internal static IReadOnlyList<CardModel> Pool() => new CardModel[]
    {
        // The Oath rework's forty-one.
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
        ModelDb.Card<ProtoVkConvergingWinds>(),
        ModelDb.Card<ProtoVkBoreasUnbound>(),
        ModelDb.Card<ProtoVkWallOfGales>(),
        ModelDb.Card<ProtoVkFourWindsAccord>(),
        ModelDb.Card<ProtoVkSwornBrotherhood>(),
        ModelDb.Card<ProtoVkNorthwindAvatar>(),
        ModelDb.Card<ProtoVkDawnWindsMarch>(),
        ModelDb.Card<ProtoVkAzureDevour>(),
        // THE EXPANSION (2026-10-01): thirty-seven, in the sheet's order.
        // Common (5)
        ModelDb.Card<ProtoVkPathfindersMark>(),
        ModelDb.Card<ProtoVkCavalryCharge>(),
        ModelDb.Card<ProtoVkWestWindShield>(),
        ModelDb.Card<ProtoVkKnightlyStrike>(),
        ModelDb.Card<ProtoVkAmberSharpshooter>(),
        // Uncommon (17)
        ModelDb.Card<ProtoVkBlazingCharge>(),
        ModelDb.Card<ProtoVkTidalBulwark>(),
        ModelDb.Card<ProtoVkGlacialEdict>(),
        ModelDb.Card<ProtoVkStaticField>(),
        ModelDb.Card<ProtoVkBarbaraWellspringHymn>(),
        ModelDb.Card<ProtoVkLisaPulsatingWitch>(),
        ModelDb.Card<ProtoVkNoelleSteadfastMaid>(),
        ModelDb.Card<ProtoVkVowOfTheBlade>(),
        ModelDb.Card<ProtoVkUnwaveringBanner>(),
        ModelDb.Card<ProtoVkShiftingGale>(),
        ModelDb.Card<ProtoVkCycleOfSeasons>(),
        ModelDb.Card<ProtoVkFourBanners>(),
        ModelDb.Card<ProtoVkEyeWall>(),
        ModelDb.Card<ProtoVkPressureFront>(),
        ModelDb.Card<ProtoVkCrosscurrent>(),
        ModelDb.Card<ProtoVkAssemblyAtTheCathedral>(),
        ModelDb.Card<ProtoVkDawnPatrol>(),
        // Rare (15)
        ModelDb.Card<ProtoVkWildfireOath>(),
        ModelDb.Card<ProtoVkUnbrokenTide>(),
        ModelDb.Card<ProtoVkAbsoluteZero>(),
        ModelDb.Card<ProtoVkThunderingVerdict>(),
        ModelDb.Card<ProtoVkOathUntoDeath>(),
        ModelDb.Card<ProtoVkGrandMastersVerdict>(),
        ModelDb.Card<ProtoVkWolfpack>(),
        ModelDb.Card<ProtoVkOathboundAegis>(),
        ModelDb.Card<ProtoVkWeathervane>(),
        ModelDb.Card<ProtoVkTempestOfTheFourWinds>(),
        ModelDb.Card<ProtoVkTwinGales>(),
        ModelDb.Card<ProtoVkDownburst>(),
        ModelDb.Card<ProtoVkEyeOfStormterror>(),
        ModelDb.Card<ProtoVkChargeOfTheKnights>(),
        ModelDb.Card<ProtoVkTheOrderAnswers>(),
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
