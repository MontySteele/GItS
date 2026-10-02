using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// A PLAN STAYS OPEN (2026-10-01, ruled). Paper
/// <c>review/active/kokomi-delay-pays-2026-10-01.md</c>; [USER]: "Interesting
/// idea! Yes, I think this makes sense. We'd want to make sure that the UX is
/// reasonably snappy so players don't have to spend forever on their turns,
/// but it sounds doable." When the Bake-Kurage carries out a Plan written from
/// a TWO-LINE card, the player picks its Plan line (the default) or its
/// now-line at printed size, on one grid a turn. Pinned off the compiled
/// methods, as the rest of the arm is. Sim twin:
/// <c>tier0/tests/test_kokomi_open_plan.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiOpenPlanTests : IDisposable
{
    private readonly bool _kokomi = KokomiOverhaul.Enabled;

    public KokomiOpenPlanTests() => KokomiOverhaul.Enabled = true;

    public void Dispose() => KokomiOverhaul.Enabled = _kokomi;

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    private static readonly KokomiPlan.Planned[] OneHit =
    {
        new(KokomiPlan.Kind.Damage, 7, KokomiPlan.Aim.AllEnemies),
    };

    [Fact]
    public void Every_two_line_row_carries_its_now_line_and_a_plan_only_row_does_not()
    {
        var types = typeof(ProtoKkNip).Assembly.GetTypes()
            .Where(t => t.Name.StartsWith("ProtoKk", StringComparison.Ordinal)
                        && typeof(IPlannedCard).IsAssignableFrom(t))
            .ToList();
        Assert.NotEmpty(types);
        Assert.Contains(typeof(ProtoKkKuragesOath), types);
        Assert.True(typeof(INowLineCard).IsAssignableFrom(
            typeof(ProtoKkKuragesOath)));
        Assert.False(typeof(INowLineCard).IsAssignableFrom(typeof(ProtoKkNip)));
        // Thirty two-line rows on the 78 (the sim's census agrees).
        Assert.Equal(30, types.Count(t =>
            typeof(INowLineCard).IsAssignableFrom(t)));
    }

    [Fact]
    public void A_face_up_play_and_a_carry_out_run_the_same_now_line()
    {
        Assert.Contains("ProtoKkKuragesOath.PlayNowLine",
                        Seq("ProtoKkKuragesOath", "OnPlay"));
        Assert.Contains("CreatureCmd.GainBlock",
                        Seq("ProtoKkKuragesOath", "PlayNowLine"));
        Assert.Contains("INowLineCard.PlayNowLine",
                        Seq("KokomiPlan", "CarryOutNowLine"));
    }

    [Fact]
    public void The_now_line_aims_where_divine_strategy_aims_it()
    {
        Assert.Equal(DivineStrategyPower.Aim.None,
                     new ProtoKkKuragesOath().NowLineAim);
        Assert.Equal(DivineStrategyPower.Aim.FrontEnemy,
                     new ProtoKkSlackWater().NowLineAim);
        Assert.Equal(DivineStrategyPower.Aim.Ally,
                     new ProtoKkJointOrders().NowLineAim);
    }

    [Fact]
    public void Only_a_two_line_plan_that_is_not_dusk_offers_the_choice()
    {
        Assert.True(new KokomiPlan.Entry(new ProtoKkKuragesOath(), OneHit)
            .TwoLine);
        Assert.False(new KokomiPlan.Entry(new ProtoKkKuragesOath(), OneHit,
                                          Dusk: true).TwoLine);
        Assert.False(new KokomiPlan.Entry(new ProtoKkNip(), OneHit).TwoLine);
        Assert.False(new KokomiPlan.Entry(null, OneHit).TwoLine);
    }

    [Fact]
    public void The_chooser_is_one_grid_a_turn_with_a_manual_confirm()
    {
        var seq = Seq("KokomiPlan", "ChooseLines");
        Assert.Contains("KokomiOverhaulLedger.ClaimOncePerTurn", seq);
        Assert.Contains("CardSelectCmd.FromSimpleGrid", seq);
        Assert.Contains("CardSelectorPrefs.set_RequireManualConfirmation", seq);
        Assert.True(seq.IndexOf("KokomiOverhaulLedger.ClaimOncePerTurn")
                    < seq.IndexOf("CardSelectCmd.FromSimpleGrid"));
    }

    [Fact]
    public void Every_door_that_carries_plans_out_asks_the_chooser_but_dusk()
    {
        Assert.Contains("KokomiPlan.ChooseLines", Seq("KokomiPlan", "ResolveAll"));
        Assert.Contains("KokomiPlan.ChooseLines",
                        Seq("KokomiPlan", "ResolveFront"));
        Assert.Contains("KokomiPlan.ChooseLines",
                        Seq("KokomiPlan", "ResolveAllNow"));
        Assert.DoesNotContain("KokomiPlan.ChooseLines",
                              Seq("KokomiPlan", "ResolveDusk"));
        Assert.Contains("KokomiPlan.CarryOutNowLine",
                        Seq("KokomiPlan", "ResolveEntry"));
    }

    [Fact]
    public void The_prompt_and_the_rule_are_short_and_plain()
    {
        Assert.Equal("Your Plans are due. Click one to use its other line "
                     + "instead.", KokomiPlan.ChooserPromptText);
        var body = ((ProtoBakeKuragePower)Activator.CreateInstance(
                typeof(ProtoBakeKuragePower))!).Localization!
            .First(r => r.Item1 == "description").Item2;
        Assert.Contains(" Then you choose each [gold]Plan[/gold]'s line.",
                        body);
        Assert.Equal("Kurage's Oath (now-line)",
                     KokomiPlan.NowLineTitle("Kurage's Oath"));
    }
}
