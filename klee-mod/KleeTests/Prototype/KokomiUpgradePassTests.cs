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
/// THE KOKOMI UPGRADE PASS (2026-10-19, <c>review/active/kokomi-next-2026-10-19.md</c>,
/// "The weak-card and upgrade pass"; [USER]: "This table looks good. Ship
/// it", and "can we make sure that if you upgrade a Plan card, both the Plan
/// and non-Plan sides get upgrades where possible?"). Structural and pure
/// pins (the headless boundary); sim twin
/// <c>tier0/tests/test_kokomi_upgrade_pass_2026_10_19.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiUpgradePassTests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static (KokomiPlan.Kind, int)[] Plan(IPlannedCard card) =>
        card.PlanClauses.Select(c => (c.Kind, c.Amount)).ToArray();

    [Fact]
    public void War_council_is_weak_two_three_and_the_upgrade_adds_a_draw()
    {
        var plain = new ProtoKkWarCouncil();
        Assert.Equal(2, plain.DynamicVars["PowerAmount"].IntValue);
        Assert.Equal(new[] { (KokomiPlan.Kind.Energy, 2), (KokomiPlan.Kind.Draw, 0) },
                     Plan(plain));
        var up = Upgraded<ProtoKkWarCouncil>();
        Assert.Equal(3, up.DynamicVars["PowerAmount"].IntValue);
        Assert.Equal(new[] { (KokomiPlan.Kind.Energy, 2), (KokomiPlan.Kind.Draw, 1) },
                     Plan(up));
        Assert.EndsWith("{IfUpgraded:show: and draw 1 card|}.", Face(plain));
    }

    [Fact]
    public void A_zero_draw_clause_draws_nothing()
    {
        // The carry-out returns before the draw when the amount is 0.
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "ResolveOne")),
                        c => c.Contains("CardPileCmd.Draw"));
    }

    [Theory]
    [InlineData(typeof(ProtoKkPincer))]
    [InlineData(typeof(ProtoKkSecondWave))]
    public void Pincer_and_second_wave_plans_draw_one_upgraded(Type type)
    {
        var plain = (IPlannedCard)Activator.CreateInstance(type)!;
        Assert.Equal((KokomiPlan.Kind.Draw, 0), Plan(plain).Last());
        var card = (CardModel)Activator.CreateInstance(type)!;
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        Assert.Equal((KokomiPlan.Kind.Draw, 1), Plan((IPlannedCard)card).Last());
        Assert.EndsWith("{IfUpgraded:show: Draw 1 card.|}", Face(card));
    }

    [Fact]
    public void Both_sides_upgrade_on_the_plan_cards()
    {
        Assert.Equal(2, Upgraded<ProtoKkOpeningGambit>().PlanClauses[0].Amount);
        Assert.Equal(3, Upgraded<ProtoKkTidalScreen>().PlanClauses[0].Amount);
        Assert.Equal(4, Upgraded<ProtoKkKelpWall>().PlanClauses[0].Amount);
        Assert.Equal(0, new ProtoKkKelpWall().PlanClauses[0].Amount);
        Assert.Equal(4, Upgraded<ProtoKkKuragesWake>().PlanClauses[0].Amount);
        Assert.Equal(3, Upgraded<ProtoKkSpearhead>().PlanClauses[0].Amount);
        Assert.Equal(3, Upgraded<ProtoKkJointOrders>().PlanClauses[0].Amount);
        Assert.Equal(4, Upgraded<ProtoKkCoordinatedStrike>().PlanClauses[0].Amount);
        Assert.Equal(4, Upgraded<ProtoKkSteadyTide>().PlanClauses[0].Amount);
        Assert.Equal(12, Upgraded<ProtoKkSteadyTide>().DynamicVars.Block.IntValue);
        Assert.Equal(9, new ProtoKkSteadyTide().DynamicVars.Block.IntValue);
    }

    [Fact]
    public void Turnabout_keeps_its_cost_and_adds_five()
    {
        var up = Upgraded<ProtoKkTurnabout>();
        Assert.Equal(2, up.EnergyCost.Canonical);
        Assert.Equal((KokomiPlan.Kind.DamageTakenSince, 5), Plan(up).Single());
        Assert.Equal((KokomiPlan.Kind.DamageTakenSince, 0),
                     Plan(new ProtoKkTurnabout()).Single());
    }

    [Fact]
    public void Juuga_reaches_four_turns_on_both_sides()
    {
        var up = Upgraded<ProtoMiGorouJuuga>();
        Assert.Equal(4, up.DynamicVars["PowerAmount"].IntValue);
        Assert.Equal((KokomiPlan.Kind.JuugaGuard, 4), Plan(up).Single());
        Assert.Equal((KokomiPlan.Kind.JuugaGuard, 3),
                     Plan(new ProtoMiGorouJuuga()).Single());
    }

    [Fact]
    public void Inuzaka_takes_the_default_upgrade_on_both_sides()
    {
        var up = Upgraded<ProtoMiGorouInuzaka>();
        Assert.Equal(11m, up.DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(14, up.PlanClauses.Single().Amount);
    }

    [Fact]
    public void Sangonomiyas_orders_upgrade_makes_the_companion_upgraded()
    {
        Assert.True(typeof(UpgradeTwinPower)
            .IsAssignableFrom(typeof(SangonomiyasOrdersPower)));
        Assert.Contains(Il.Calls(Il.Method(nameof(ProtoKkSangonomiyasOrders), "OnPlay")),
                        c => c.Contains("UpgradeTwinPower.Install"));
        var up = Upgraded<ProtoKkSangonomiyasOrders>();
        Assert.DoesNotContain(CardKeyword.Innate, up.Keywords);
        Assert.Contains("add a random{IfUpgraded:show: upgraded|} Common Inazuma",
                        Face(up));
        Assert.Contains(Il.Calls(Il.Method(nameof(SangonomiyasOrdersPower),
                                           "AfterPlayerTurnStartLate")),
                        c => c.Contains("UpgradeInternal"));
    }

    [Fact]
    public void Crystal_collapse_plays_a_random_common_companion_when_none_was_played()
    {
        Assert.EndsWith("If none, play a random Common one.",
                        Face(new ProtoMiGorouCrystalCollapse()));
        var calls = Il.Calls(Il.Method("KokomiPlan", "PlayCopy"));
        Assert.Contains(calls, c => c.Contains("KokomiCompanionPlan.Generated"));
        Assert.Contains(calls, c => c.Contains("CardCmd.AutoPlay"));
        Assert.Equal("Random Companion", KokomiPlan.CopiesCaption(null));
    }

    [Fact]
    public void Read_the_field_discounts_only_when_upgraded()
    {
        Assert.EndsWith("{IfUpgraded:show: It costs 1 less.|}",
                        Face(new ProtoKkReadTheField()));
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "DrawPileToHand")),
                        c => c.Contains("AddThisTurn"));
    }

    [Fact]
    public void Sea_glass_harvest_previews_sea_glass()
    {
        Assert.Equal(8m, new ProtoKkSeaGlassHarvest().DynamicVars.Block.BaseValue);
        Assert.Equal(11m, Upgraded<ProtoKkSeaGlassHarvest>().DynamicVars.Block.BaseValue);
        Assert.Contains(Il.Calls(Il.Method(nameof(ProtoKkSeaGlassHarvest),
                                           "get_ExtraHoverTips")),
                        c => c.Contains("WithSeaGlassPreview"));
        // Kurage Canopy's upgraded card previews the upgraded Ward it adds.
        Assert.Contains(Il.Calls(Il.Method(nameof(ProtoKkKurageCanopy),
                                           "get_ExtraHoverTips")),
                        c => c.Contains("get_IsUpgraded"));
    }

    [Fact]
    public void Brine_sting_counts_as_a_sting_played()
    {
        Assert.Contains(typeof(ProtoKkBrineSting),
                        Il.TypesTested(Il.Method(nameof(ProtoBakeKuragePower),
                                                 "AfterCardPlayed")));
    }

    [Fact]
    public void At_waters_edge_shows_when_it_is_spent()
    {
        var text = ((ILocalizationProvider)new AtWatersEdgePower()).Localization!
            .First(r => r.Item1 == "smartDescription").Item2;
        Assert.EndsWith("{Spent:cond:>0? (Used this turn.)|}", text);
        Assert.Contains(Il.Calls(Il.Method("KokomiExpansion", "OnHydroDamage")),
                        c => c.Contains("ShowSpent"));
    }
}
