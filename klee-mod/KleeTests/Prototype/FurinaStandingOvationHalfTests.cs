using System.IO;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// STANDING OVATION, COMMON AGAIN, SPEND HALF (2026-10-11, Furina round 3
/// record, pick 1). [USER]: "On Furina - let's try standing ovation at Common
/// but only for half your Fanfare and see how that goes." "Spend half your
/// Fanfare. Deal that much damage to ALL enemies.": a "Spend up to" half the
/// bank, rounded down, so it is not a spend-all and Bis! ignores it. Sim
/// twin: <c>tier0/tests/test_furina_standing_ovation_half.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaStandingOvationHalfTests
{
    private static string Generated(string type) => File.ReadAllText(
        Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode", "Cards",
                     "Prototype", "Generated", type + ".cs"));

    [Fact]
    public void Standing_ovation_is_a_common_that_spends_half()
    {
        Assert.Equal(CardRarity.Common, new ProtoFsStandingOvationAll().Rarity);
        var src = Generated("ProtoFsStandingOvationAll");
        Assert.Contains(
            "await FurinaStage.SpendHalf(choiceContext, Owner.Creature);", src);
        Assert.Contains("FurinaStage.SpentOrHalf(card)", src);
        Assert.DoesNotContain("SpendAll", src);
        Assert.DoesNotContain("SpentOrFanfare", src);
    }

    [Fact]
    public void Half_of_21_spends_10_leaves_11_and_bis_keeps_nothing()
    {
        var kit = StageKit.With(new StageMods { Bis = 1 }, 21);
        Assert.Equal(10, StageKit.Run(
            kit.Director.SpendUpTo(kit.Stage.Fanfare / 2)));
        Assert.Equal(11, kit.Stage.Fanfare);               // no half back
        var one = StageKit.With(1);
        Assert.Equal(0, StageKit.Run(
            one.Director.SpendUpTo(one.Stage.Fanfare / 2)));
        Assert.Equal(1, one.Stage.Fanfare);
    }
}
