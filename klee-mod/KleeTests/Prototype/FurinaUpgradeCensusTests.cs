using System;
using System.IO;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;
using static KleeMod.Tests.Prototype.StageKit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA'S UPGRADE CENSUS (2026-10-23, [USER]: "Otherwise I agreed on all the
/// cards!"; <c>review/active/furina-next-3-2026-10-16.md</c>, "Upgrade census
/// (2026-10-23)"). Eight cost-only upgrades became real ones and every cost
/// stays: Let the People Rejoice 2 [3] a point, The Show Must Go On [Retain],
/// Tutti! draws 1 [2], Rainfall Overture [draws 1], The Masquerade [plus 2],
/// Critics' Darling [plus 1], Showstopper Spend 5 [3], Ensemble Cast [2
/// random guests]. The three Powers are one badge for both versions
/// (<see cref="UpgradeTwinPower"/>). Sim twin:
/// <c>tier0/tests/test_furina_upgrade_census_2026_10_23.py</c>.
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class FurinaUpgradeCensusTests : IDisposable
{
    public FurinaUpgradeCensusTests() => FurinaStageLedger.ResetAll();

    public void Dispose() => FurinaStageLedger.ResetAll();

    private static string Generated(string type) => File.ReadAllText(
        Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode", "Cards",
                     "Prototype", "Generated", type + ".cs"));

    private static CardModel Upgraded(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        card.UpgradeInternal();
        return card;
    }

    private static int Cost(CardModel card) =>
        card.EnergyCost.GetWithModifiers(CostModifiers.None);

    [Fact]
    public void No_census_card_cuts_its_cost_any_more()
    {
        foreach (var make in new Func<CardModel>[]
                 {
                     () => new ProtoFsLetThePeopleRejoice(),
                     () => new ProtoFsTheShowMustGoOn(),
                     () => new ProtoFsTutti(),
                     () => new ProtoFsRainfallOverture(),
                     () => new ProtoFsTheMasquerade(),
                     () => new ProtoFsCriticsDarling(),
                     () => new ProtoFsShowstopper(),
                     () => new ProtoFsEnsembleCast(),
                 })
        {
            var plain = make();
            Assert.Equal(Cost(plain), Cost(Upgraded(make())));
            Assert.DoesNotContain("EnergyCost.UpgradeBy",
                                  Generated(plain.GetType().Name));
        }
    }

    [Fact]
    public void The_numbers_and_keywords_move_as_ruled()
    {
        Assert.Equal(2m, new ProtoFsLetThePeopleRejoice().DynamicVars.ExtraDamage.BaseValue);
        Assert.Equal(3m, Upgraded(new ProtoFsLetThePeopleRejoice()).DynamicVars.ExtraDamage.BaseValue);
        Assert.DoesNotContain(CardKeyword.Retain, new ProtoFsTheShowMustGoOn().Keywords);
        Assert.Contains(CardKeyword.Retain, Upgraded(new ProtoFsTheShowMustGoOn()).Keywords);
        Assert.Equal(2, Upgraded(new ProtoFsTutti()).DynamicVars.Cards.IntValue);
        Assert.Equal(1, Upgraded(new ProtoFsRainfallOverture()).DynamicVars.Cards.IntValue);
        Assert.Equal(2, Upgraded(new ProtoFsEnsembleCast()).DynamicVars["FsAmount"].IntValue);
        foreach (var (type, power) in new[]
                 {
                     ("ProtoFsTheMasquerade", "TheMasqueradePower"),
                     ("ProtoFsCriticsDarling", "CriticsDarlingPower"),
                     ("ProtoFsShowstopper", "ShowstopperPower"),
                 })
        {
            Assert.Contains($"UpgradeTwinPower.Install<{power}>", Generated(type));
        }
    }

    [Fact]
    public void The_masquerade_upgraded_gains_2_more_a_drain()
    {
        Assert.Equal(3, StageDirector.MasqueradeBlock(3, 1, 0));
        Assert.Equal(5, StageDirector.MasqueradeBlock(3, 1, 1));
        Assert.Equal(8, StageDirector.MasqueradeBlock(3, 2, 1));
        Assert.Equal(0, StageDirector.MasqueradeBlock(0, 1, 1));
        var kit = new StageKit(new StageMods { Masquerade = 1, MasqueradeUpgraded = 1 },
                               0, 78, 78);
        Assert.True(Run(kit.Director.Drain(3)));
        Assert.Contains("block 5", kit.Board.Log);
        Assert.Equal("\n(+5 Block: The Masquerade)",
                     FurinaStageFacePreview.DrainBlock(3, 1, false, 1));
    }

    [Fact]
    public void Critics_darling_upgraded_deals_1_more_and_nothing_for_nothing()
    {
        Assert.Equal(5, StageDirector.CriticsDarlingHit(4, 1, 1));
        Assert.Equal(0, StageDirector.CriticsDarlingHit(0, 1, 1));
        var kit = StageKit.With(new StageMods { CriticsDarling = 1, CriticsDarlingUpgraded = 1 }, 0);
        Run(kit.Director.Drain(4));
        Assert.Contains("power Critics' Darling Random 5", kit.Board.Log);
    }

    [Fact]
    public void Showstopper_upgraded_spends_3_and_pays_first()
    {
        Assert.Equal(new[] { 3, 5 }, StageDirector.ShowstopperPrices(2, 1).ToArray());
        Assert.Equal(new[] { 5 }, StageDirector.ShowstopperPrices(1, 0).ToArray());
        Assert.Empty(StageDirector.ShowstopperPrices(0, 0));
        // A bank of 3 buys the upgraded round, where 5 was the price before.
        var kit = StageKit.With(new StageMods { Showstopper = 1, ShowstopperUpgraded = 1 },
                                3, StagePerformer.Clorinde);
        Run(kit.Director.EndOfTurn(0));
        Assert.Equal(0, kit.Stage.Fanfare);
        Assert.Equal(2, kit.Board.Log.Count(l => l == "damage Clorinde Random 6 Electro"));
        // A bank of 2 buys nothing.
        var poor = StageKit.With(new StageMods { Showstopper = 1, ShowstopperUpgraded = 1 },
                                 2, StagePerformer.Clorinde);
        Run(poor.Director.EndOfTurn(0));
        Assert.Equal(2, poor.Stage.Fanfare);
    }

    // ---- Bring the House Down, reflavoured (a separate commit) ---------------

    [Fact]
    public void Bring_the_house_down_hits_then_spends_5_a_guest_for_two_acts_each()
    {
        Assert.Equal(15, FurinaStage.HouseDownPrice(3));
        Assert.Equal(0, FurinaStage.HouseDownPrice(0));
        var card = new ProtoFsBringTheHouseDown();
        Assert.Equal(8m, card.DynamicVars.Damage.BaseValue);
        Assert.Equal(11m, Upgraded(new ProtoFsBringTheHouseDown()).DynamicVars.Damage.BaseValue);
        Assert.Equal(2, Cost(Upgraded(new ProtoFsBringTheHouseDown())));
        Assert.IsAssignableFrom<IStageSpendCard>(card);
        var src = Generated("ProtoFsBringTheHouseDown");
        Assert.True(src.IndexOf("DamageCmd.Attack", StringComparison.Ordinal)
                    < src.IndexOf("FurinaCards.HouseDown", StringComparison.Ordinal));
        Assert.Contains("StageDirector.ActEachTwice",
            Il.Calls(Il.Method("FurinaStage", "HouseDown")));
    }
}
