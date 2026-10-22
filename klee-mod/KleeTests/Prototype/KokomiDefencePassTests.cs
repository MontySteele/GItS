using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI DEFENCE PASS (2026-10-22, <c>review/active/kokomi-next-2026-10-19.md</c>,
/// "Defence pass, 2026-10-22"; [USER]: "I think it's fine for the Casket to
/// pay on 0-cost cards as an intended loop, but I think 2 block per plan is
/// making them too strong. Let's try 1a, 3a, and reducing the Casket to 1
/// again", and on Watatsumi's Grace, "Otherwise agreed").
///   1. The Tamakushi Casket pays 1 Block a counted play; the Watatsumi
///      Casket 2. Stings, Wards and Companions still count.
///   2. Watatsumi's Grace: "... for each Plan waiting. Stings and Wards don't
///      count." (<c>KokomiPlan.ChainPlansHeld</c>.)
///   3. Kurage Canopy: "At the start of your turn, if 2 or more of your Plans
///      were carried out, add a Ward to your Hand. Stings and Wards don't
///      count." Battle Formation's read.
///   4. Tide Wall's Plan: "Gain 4 [6] Block, plus the biggest attack an
///      enemy intends when this is carried out."
/// Structural and pure pins (the headless boundary); sim twin
/// <c>tier0/tests/test_kokomi_defence_pass_2026_10_22.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiDefencePassTests
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

    private static string PowerText(PowerModel power) =>
        ((ILocalizationProvider)power).Localization!
            .First(r => r.Item1 == "description").Item2;

    // ---- 1. the Casket --------------------------------------------------------

    [Fact]
    public void The_casket_pays_1_and_the_watatsumi_casket_2()
    {
        Assert.Equal(1, KokomiOverhaulLaw.CasketBlock);
        Assert.Equal(1, new TamakushiCasket().Block);
        Assert.Equal(2, new WatatsumiCasket().Block);
    }

    [Fact]
    public void The_casket_still_pays_for_a_planned_sting_or_ward()
    {
        // "fine for the Casket to pay on 0-cost cards as an intended loop":
        // what counts is unchanged, a Sting or Ward Planned included.
        Assert.True(TamakushiCasket.CountsPlanned(new ProtoKkSting()));
        Assert.True(TamakushiCasket.CountsPlanned(new ProtoKkWard()));
    }

    // ---- 2. Watatsumi's Grace -------------------------------------------------

    [Fact]
    public void Grace_counts_plans_waiting_less_stings_and_wards()
    {
        var end = Il.CallSequence(Il.Method("KokomiTasteAudit", "TurnEnd")).ToList();
        Assert.Contains(end, c => c.Contains("KokomiPlan.ChainPlansHeld"));
        Assert.DoesNotContain(end, c => c.EndsWith("KokomiPlan.PlansHeld"));
        Assert.EndsWith(" Stings and Wards don't count.",
                        Face(new ProtoKkWatatsumisGrace()));
        Assert.EndsWith(" Stings and Wards don't count.",
                        PowerText(new WatatsumisGracePower()));
    }

    // ---- 3. Kurage Canopy -----------------------------------------------------

    [Fact]
    public void Canopy_pays_at_two_plans_like_battle_formation()
    {
        Assert.Equal(BattleFormationPower.Threshold, KurageCanopyPower.Threshold);
        Assert.False(KurageCanopyPower.Pays(0));
        Assert.False(KurageCanopyPower.Pays(1));
        Assert.True(KurageCanopyPower.Pays(2));
        Assert.True(KurageCanopyPower.Pays(5));
        var reads = Il.Calls(Il.Method(nameof(KurageCanopyPower), "Signal"));
        Assert.Contains(reads, c => c.Contains("get_ChainPlansThisTurn"));
        Assert.Contains(reads, c => c.Contains("KokomiCards.AddJellyfish"));
        Assert.False(typeof(IKokomiPlanListener)
            .IsAssignableFrom(typeof(KurageCanopyPower)));
    }

    [Fact]
    public void Canopy_reads_the_morning_once_right_after_battle_formation()
    {
        var morning = Il.CallSequence(
            Il.Method(nameof(ProtoBakeKuragePower), "AfterPlayerTurnStart")).ToList();
        var resolve = morning.FindIndex(c => c.Contains("KokomiPlan.ResolveAll"));
        var formation = morning.FindIndex(c => c.Contains("BattleFormationPower.Signal"));
        var canopy = morning.FindIndex(c => c.Contains("KurageCanopyPower.Signal"));
        Assert.True(resolve >= 0 && formation > resolve && canopy > formation,
                    string.Join(" ", morning));
        Assert.Single(morning, c => c.Contains("KurageCanopyPower.Signal"));
    }

    [Fact]
    public void Canopy_face_mirrors_battle_formation()
    {
        Assert.Equal("At the start of your turn, if 2 or more of your "
                   + "[gold]Plans[/gold] were carried out, add "
                   + "{IfUpgraded:show:an upgraded|a} [gold]Ward[/gold]. "
                   + "Stings and Wards don't count.",
                     Face(new ProtoKkKurageCanopy()));
        Assert.StartsWith("At the start of your turn, if 2 or more of your "
                        + "[gold]Plans[/gold] were carried out, ",
                          PowerText(new KurageCanopyPower()));
    }

    // ---- 4. Tide Wall ---------------------------------------------------------

    [Fact]
    public void Tide_wall_plans_the_face_up_block_plus_the_intent()
    {
        var card = new ProtoKkTideWall();
        Assert.Equal(4m, card.DynamicVars.Block.BaseValue);
        Assert.Equal((KokomiPlan.Kind.BlockMaxIntent, 4),
                     card.PlanClauses.Select(c => (c.Kind, c.Amount)).Single());
        var up = Upgraded<ProtoKkTideWall>();
        Assert.Equal(6m, up.DynamicVars.Block.BaseValue);
        Assert.Equal(6, up.PlanClauses.Single().Amount);
    }
}
