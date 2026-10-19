using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// VARKA, THE POWER UPGRADE PASS (2026-10-19). [USER]: "You do have a habit
/// of making too many powers just decrease their cost by 1 on upgrade
/// though." Seven upgrades that were Innate now install a Plus power, and
/// Comrades of the Expedition's cost cut became 1 [2] Oath. The sim twin is
/// <c>tier0/tests/test_varka_power_upgrades.py</c>; the staging paper is
/// <c>review/active/varka-fang-next-2026-10-19.md</c>.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaPowerUpgradeTests : IDisposable
{
    public VarkaPowerUpgradeTests()
    {
        HeadlessGame.Arm();
        VarkaOathLedger.ResetAll();
    }

    public void Dispose()
    {
        VarkaOathLedger.ResetAll();
    }

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    public static IEnumerable<object[]> Swaps => new[]
    {
        new object[] { typeof(ProtoVkUnwaveringBanner), "UnwaveringBannerPower", "{IfUpgraded:show:2|1}" },
        new object[] { typeof(ProtoVkWildfireOath), "WildfireOathPower", "{IfUpgraded:show: plus 3|}" },
        new object[] { typeof(ProtoVkAbsoluteZero), "AbsoluteZeroPower", "{IfUpgraded:show: plus 3|}" },
        new object[] { typeof(ProtoVkWolfpack), "WolfpackPower", "{IfUpgraded:show:an upgraded|a}" },
        new object[] { typeof(ProtoVkWeathervane), "WeathervanePower", "{IfUpgraded:show: Gain 1 [gold]Oath[/gold] of it.|}" },
        new object[] { typeof(ProtoVkEyeOfStormterror), "EyeOfStormterrorPower", "{IfUpgraded:show:4|3}" },
        new object[] { typeof(ProtoVkWestWindsBlessing), "WestWindsBlessingPower", "{IfUpgraded:show: and draws 1 card|}" },
    };

    [Theory]
    [MemberData(nameof(Swaps))]
    public void The_upgraded_card_installs_the_plus_power_and_is_not_innate(
        Type cardType, string power, string swap)
    {
        var card = (CardModel)Activator.CreateInstance(cardType)!;
        Assert.Contains(swap, Face(card));
        Assert.DoesNotContain(CardKeyword.Innate, card.Keywords);
        var play = Seq(cardType.Name, "OnPlay");
        Assert.Contains(play, c => c.Contains(power));
        Assert.Contains(play, c => c.Contains(power.Replace("Power", "PlusPower")));
        Assert.Contains(play, c => c.Contains("get_IsUpgraded"));
    }

    [Fact]
    public void The_upgraded_faces_keep_their_cost_and_lose_innate()
    {
        foreach (var up in new CardModel[]
                 {
                     Upgraded<ProtoVkUnwaveringBanner>(), Upgraded<ProtoVkWildfireOath>(),
                     Upgraded<ProtoVkAbsoluteZero>(), Upgraded<ProtoVkWolfpack>(),
                     Upgraded<ProtoVkWeathervane>(), Upgraded<ProtoVkEyeOfStormterror>(),
                     Upgraded<ProtoVkWestWindsBlessing>(),
                 })
        {
            Assert.DoesNotContain(CardKeyword.Innate, up.Keywords);
            Assert.Equal(up.EnergyCost.Canonical,
                up.EnergyCost.GetWithModifiers(CostModifiers.None));
        }
    }

    [Fact]
    public void Comrades_gains_one_more_oath_upgraded_at_the_same_cost()
    {
        var card = new ProtoVkComradesOfTheExpedition();
        Assert.Equal(1m, card.DynamicVars["PowerAmount"].BaseValue);
        var up = Upgraded<ProtoVkComradesOfTheExpedition>();
        Assert.Equal(2m, up.DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal(2, up.EnergyCost.GetWithModifiers(CostModifiers.None));
    }

    [Fact]
    public void The_plus_numbers()
    {
        Assert.Equal(1, new UnwaveringBannerPower().OathPaid);
        Assert.Equal(2, new UnwaveringBannerPlusPower().OathPaid);
        Assert.Equal(0, new WildfireOathPower().Bonus);
        Assert.Equal(3, new WildfireOathPlusPower().Bonus);
        Assert.Equal(0, new AbsoluteZeroPower().Bonus);
        Assert.Equal(3, new AbsoluteZeroPlusPower().Bonus);
        Assert.False(new WolfpackPower().UpgradedCopy);
        Assert.True(new WolfpackPlusPower().UpgradedCopy);
        Assert.Equal(0, new WeathervanePower().OathGained);
        Assert.Equal(1, new WeathervanePlusPower().OathGained);
        Assert.Equal(3, new EyeOfStormterrorPower().Swirls);
        Assert.Equal(4, new EyeOfStormterrorPlusPower().Swirls);
        Assert.Equal(0, new WestWindsBlessingPower().Draws);
        Assert.Equal(1, new WestWindsBlessingPlusPower().Draws);
        // "Your Pyro [Cryo] Oath plus 3", per stack.
        Assert.Equal(7, WildfireOathBasePower.DamageFor(4, 1, 3));
        Assert.Equal(4, WildfireOathBasePower.DamageFor(4, 1));
        Assert.Equal(10, AbsoluteZeroBasePower.DamageFor(2, 2, 3));
    }

    [Fact]
    public void The_live_sites_read_either_form()
    {
        Assert.Contains(Seq("VarkaOath", "BannerHolds"),
            c => c.Contains("UnwaveringBannerBasePower"));
        Assert.Contains(Seq("VarkaOath", "Weathervane"),
            c => c.Contains("WeathervaneBasePower"));
        Assert.Contains(Seq("VarkaOath", "OnSwirl"),
            c => c.Contains("EyeOfStormterrorBasePower"));
    }
}
