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
/// though." Seven upgrades that were Innate now carry their upgrade on ONE
/// power per card (<see cref="UpgradeTwinPower"/>: Amount is every copy,
/// UpgradedCopies the upgraded ones), and Comrades of the Expedition's cost
/// cut became 1 [2] Oath. The sim twin is
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
    public void The_card_installs_one_power_that_counts_its_upgraded_copies(
        Type cardType, string power, string swap)
    {
        var card = (CardModel)Activator.CreateInstance(cardType)!;
        Assert.Contains(swap, Face(card));
        Assert.DoesNotContain(CardKeyword.Innate, card.Keywords);
        var play = Seq(cardType.Name, "OnPlay");
        Assert.Contains(play, c => c.Contains("UpgradeTwinPower.Install"));
        Assert.Contains(play, c => c.Contains("get_IsUpgraded"));
        Assert.DoesNotContain(play, c => c.Contains("PlusPower"));
        var cls = typeof(UpgradeTwinPower).Assembly.GetTypes()
            .Single(t => t.Name == power);
        Assert.True(typeof(UpgradeTwinPower).IsAssignableFrom(cls), power);
        Assert.Null(typeof(UpgradeTwinPower).Assembly.GetTypes()
            .FirstOrDefault(t => t.Name == power.Replace("Power", "PlusPower")));
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
    public void The_stacking_rules()
    {
        // Banner: each copy adds its own, 1 plain, 2 upgraded, at least 1.
        Assert.Equal(1, UnwaveringBannerPower.OathFor(1, 0));
        Assert.Equal(2, UnwaveringBannerPower.OathFor(0, 1));
        Assert.Equal(3, UnwaveringBannerPower.OathFor(1, 1));
        Assert.Equal(1, UnwaveringBannerPower.OathFor(0, 0));
        // Wildfire / Absolute Zero: one hit, the Oath per copy plus 3 per
        // upgraded copy (a second plain copy doubles, as before).
        Assert.Equal(4, WildfireOathPower.DamageFor(4, 1));
        Assert.Equal(7, WildfireOathPower.DamageFor(4, 1, 1));
        Assert.Equal(11, WildfireOathPower.DamageFor(4, 2, 1));
        Assert.Equal(10, AbsoluteZeroPower.DamageFor(2, 2, 2));
        // Eye: every copy draws through the 3rd Swirl, upgraded ones the 4th.
        Assert.Equal(2, EyeOfStormterrorPower.DrawsFor(3, 2, 1));
        Assert.Equal(1, EyeOfStormterrorPower.DrawsFor(4, 2, 1));
        Assert.Equal(0, EyeOfStormterrorPower.DrawsFor(4, 2, 0));
        Assert.Equal(0, EyeOfStormterrorPower.DrawsFor(5, 2, 2));
        Assert.Equal(4, VarkaLaw.EyeOfStormterrorSwirlsUpgraded);
        // Lupical: plain and upgraded batches, in the order they landed.
        Assert.Equal(new[] { (1, false), (1, true) },
                     UpgradeTwinPower.Batches(1, 1, upgradedFirst: false));
    }

    [Fact]
    public void The_live_sites_read_the_upgraded_copies()
    {
        Assert.Contains(Seq("UnwaveringBannerPower", "get_OathPaid"),
            c => c.Contains("UpgradeTwinPower.get_UpgradedCopies"));
        Assert.Contains(Seq("VarkaOath", "BannerHolds"),
            c => c.Contains("UnwaveringBannerPower.get_OathPaid"));
        Assert.Contains(Seq("VarkaOath", "Weathervane"),
            c => c.Contains("WeathervanePower"));
        Assert.Contains(Seq("WestWindsBlessingPower", "OnSwirl"),
            c => c.Contains("CardPileCmd.Draw"));
    }
}
