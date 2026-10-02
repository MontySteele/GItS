using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Characters;
using MegaCrit.Sts2.Core.Runs;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE COMPANION SLOT IS ONE PER REWARD, AND ONLY ON THE OWNER'S REWARD.
///
/// The base game's <c>Hook.TryModifyCardRewardOptions</c> runs every hook
/// listener in the run over the reward being built, passing that reward's
/// player; <c>RunState.IterateHookListeners</c> gathers the relics of EVERY
/// active player (read off the 0.111.0 decompile). The six slot hosts used to
/// gate on the player's character alone, so two players on the same mod
/// character each had both starter relics answer their reward: five options,
/// two of them companions. The gate now also asks that the reward's player be
/// the relic's owner.
///
/// What is exercised: the real gate each host's override runs first, and the
/// real override on the refusing path (the reward list is left alone). The
/// accepting path ends in <see cref="CompanionSlot.Roll"/>, which needs a live
/// RunState -- outside the headless boundary (README.md).
/// </summary>
public class CompanionSlotOwnerTests
{
    public static IEnumerable<object[]> Hosts() => new[]
    {
        new object[] { "Klee", typeof(PoundingSurprise) },
        new object[] { "Klee", typeof(ExplosiveFrags) },
        new object[] { "Furina", typeof(SalonSolitaire) },
        new object[] { "Furina", typeof(CurtainNeverFalls) },
        new object[] { "Kokomi", typeof(TamakushiCasket) },
        new object[] { "Varka", typeof(BoreasFang) },
    };

    private static Seat SeatFor(string character) => character switch
    {
        "Klee" => Seat.Klee(),
        "Furina" => Seat.Furina(),
        "Kokomi" => Seat.Kokomi(),
        "Varka" => Seat.Varka(),
        _ => throw new ArgumentException(character),
    };

    private static RelicModel Own(Seat seat, Type relic) =>
        (RelicModel)typeof(Seat).GetMethod("OwnRelic", HeadlessGame.All)!
            .MakeGenericMethod(relic).Invoke(seat, null)!;

    private static bool Offers(RelicModel relic, Player player, CardCreationOptions options) =>
        (bool)relic.GetType().GetMethod("OffersCompanionTo")!
            .Invoke(relic, new object[] { player, options })!;

    private static CardCreationOptions FightReward() =>
        new(Array.Empty<CardPoolModel>(), CardCreationSource.Encounter,
            CardRarityOddsType.RegularEncounter);

    [Theory]
    [MemberData(nameof(Hosts))]
    public void Two_players_on_the_same_character_each_get_exactly_one_companion(
        string character, Type host)
    {
        var a = SeatFor(character);
        var b = SeatFor(character);
        var relicA = Own(a, host);
        var relicB = Own(b, host);
        var everyListener = new[] { relicA, relicB };
        var options = FightReward();

        foreach (var (seat, own) in new[] { (a, relicA), (b, relicB) })
        {
            var offering = everyListener
                .Where(r => Offers(r, seat.Player, options)).ToList();
            Assert.Single(offering);
            Assert.Same(own, offering[0]);
        }

        // The other player's relic, run through its real override, leaves
        // this player's reward untouched.
        var rewardA = new List<CardCreationResult>();
        Assert.False(relicB.TryModifyCardRewardOptions(a.Player, rewardA, options));
        Assert.Empty(rewardA);
        var rewardB = new List<CardCreationResult>();
        Assert.False(relicA.TryModifyCardRewardOptions(b.Player, rewardB, options));
        Assert.Empty(rewardB);
    }

    [Theory]
    [MemberData(nameof(Hosts))]
    public void A_base_character_gets_no_companion_from_a_partners_relic(
        string character, Type host)
    {
        var modded = SeatFor(character);
        var ironclad = Seat.Of(new Ironclad());
        var relic = Own(modded, host);
        var options = FightReward();

        Assert.False(Offers(relic, ironclad.Player, options));
        var reward = new List<CardCreationResult>();
        Assert.False(relic.TryModifyCardRewardOptions(ironclad.Player, reward, options));
        Assert.Empty(reward);

        // And the owner's own fight reward is still answered.
        Assert.True(Offers(relic, modded.Player, options));
    }

    [Theory]
    [MemberData(nameof(Hosts))]
    public void Shops_and_events_still_get_no_companion(string character, Type host)
    {
        var seat = SeatFor(character);
        var relic = Own(seat, host);
        var shop = new CardCreationOptions(Array.Empty<CardPoolModel>(),
            CardCreationSource.Shop, CardRarityOddsType.Shop);
        Assert.False(Offers(relic, seat.Player, shop));
    }
}
