using System;
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
/// YAE UPGRADE CENSUS (2026-10-23). [USER], on the census (Yae had 10
/// cost-only and 6 Innate-only upgrades, against base Ironclad 6/2 and Silent
/// 9/3): "Otherwise I agreed on all the cards!" Kitsune Rite draws 1 [2],
/// Royalties Edits up to 2 [3], Scattered Blossoms draws 2 [3] per wither, and
/// Saiguu's Lesson+ applies 1 Weak to ALL enemies after its power is in. Sim
/// twin: <c>tier0/tests/test_yae_upgrade_census_2026_10_23.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeUpgradeCensusTests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var plus = new T();
        Seat.Set(plus, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(plus, Array.Empty<object>());
        return plus;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    [Fact]
    public void No_census_card_cuts_cost_or_gains_innate()
    {
        foreach (var plus in new CardModel[]
                 {
                     Upgraded<ProtoYmKitsuneRite>(), Upgraded<ProtoYmRoyalties>(),
                     Upgraded<ProtoYmEnlightenedBlessing>(), Upgraded<ProtoYmSaiguusLesson>(),
                 })
        {
            Assert.Equal(1, plus.EnergyCost.Canonical);
            Assert.DoesNotContain(CardKeyword.Innate, plus.Keywords);
        }
    }

    [Fact]
    public void The_amounts_go_up_by_one()
    {
        Assert.Equal((1m, 2m), (new ProtoYmKitsuneRite().DynamicVars.Cards.BaseValue,
                                Upgraded<ProtoYmKitsuneRite>().DynamicVars.Cards.BaseValue));
        Assert.Equal((2m, 3m), (new ProtoYmRoyalties().DynamicVars["YmAmount"].BaseValue,
                                Upgraded<ProtoYmRoyalties>().DynamicVars["YmAmount"].BaseValue));
        Assert.Equal((2m, 3m),
                     (new ProtoYmEnlightenedBlessing().DynamicVars["PowerAmount"].BaseValue,
                      Upgraded<ProtoYmEnlightenedBlessing>().DynamicVars["PowerAmount"].BaseValue));
        Assert.Equal("Whenever a [gold]Sakura[/gold] withers, draw {PowerAmount:diff()} cards.",
                     Face(new ProtoYmEnlightenedBlessing()));
    }

    [Fact]
    public void Saiguus_lesson_plus_weakens_all_after_its_power_is_in()
    {
        Assert.EndsWith("strikes it.{IfUpgraded:show: Apply 1 [gold]Weak[/gold] to ALL enemies.|}",
                        Face(new ProtoYmSaiguusLesson()));
        var play = Il.CallSequence(Il.Method(nameof(ProtoYmSaiguusLesson), "OnPlay")).ToList();
        var power = play.FindIndex(c => c.Contains("SaiguusLessonPower"));
        var weak = play.FindIndex(c => c.Contains("YaeCards.WeakAllIfUpgraded"));
        Assert.True(power >= 0 && weak > power, string.Join(" | ", play));
        var body = Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.WeakAllIfUpgraded))!)
            .ToList();
        Assert.Contains(body, c => c.Contains("get_IsUpgraded"));
        Assert.Contains(body, c => c.Contains("PowerCmd.Apply") && c.Contains("WeakPower"));
    }
}
