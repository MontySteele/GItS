using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI TO-DO PASS (2026-10-22; [USER]: "Do you want to go ahead and
/// take those to-do items now?"). Flank's Plan hits each enemy that does NOT
/// intend to attack (Coral Crash prints the attacker version); Steady Tide's
/// Plan puts up to 2 [3] cards from the Discard Pile into the Hand (Tidal
/// Screen prints Block + a planned draw). The resolution needs a live
/// combat, so the carry-out is pinned off the compiled methods; the
/// arithmetic is the sim twin's,
/// <c>tier0/tests/test_kokomi_todo_2026_10_22.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiTodoPassTests
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

    private static List<string> Calls(string type, string method) =>
        Il.Calls(Il.Method(type, method)).ToList();

    [Fact]
    public void Flank_prints_and_plans_the_enemies_that_do_not_intend_to_attack()
    {
        var clause = Assert.Single(new ProtoKkFlank().PlanClauses);
        Assert.Equal(KokomiPlan.Kind.Damage, clause.Kind);
        Assert.Equal(KokomiPlan.Aim.EnemiesNotIntendingAttack, clause.Aim);
        Assert.Equal((11, 14),
                     (clause.Amount,
                      Assert.Single(Upgraded<ProtoKkFlank>().PlanClauses).Amount));
        Assert.EndsWith("to each enemy that does not intend to attack.",
                        Face(new ProtoKkFlank()));
    }

    [Fact]
    public void Steady_tide_plans_up_to_two_three_from_the_discard_pile()
    {
        var clause = Assert.Single(new ProtoKkSteadyTide().PlanClauses);
        Assert.Equal(KokomiPlan.Kind.DiscardPileToHand, clause.Kind);
        Assert.Equal(KokomiPlan.Aim.Self, clause.Aim);
        Assert.Equal(2, clause.Amount);
        Assert.Equal(3, Assert.Single(
            Upgraded<ProtoKkSteadyTide>().PlanClauses).Amount);
        Assert.Equal((9, 12),
                     (new ProtoKkSteadyTide().DynamicVars.Block.IntValue,
                      Upgraded<ProtoKkSteadyTide>().DynamicVars.Block.IntValue));
        Assert.EndsWith("Put up to {PlanCards:diff()} card{PlanCards:plural:|s} "
                        + "from your [gold]Discard Pile[/gold] into your "
                        + "[gold]Hand[/gold].",
                        Face(new ProtoKkSteadyTide()));
    }

    [Fact]
    public void The_fetch_is_a_pick_of_up_to_n_from_the_discard_pile_into_the_hand()
    {
        // Structural: the carry-out dispatches the kind to the fetch, and the
        // fetch is the base game's grid (zero to N, confirmed by hand) and a
        // move into the Hand.
        Assert.Contains(Calls("KokomiPlan", "ResolveOne"),
                        c => c.Contains("KokomiPlan.DiscardPileToHand"));
        var fetch = Calls("KokomiPlan", "DiscardPileToHand");
        Assert.Contains(fetch, c => c.Contains("CardSelectCmd.FromSimpleGrid"));
        Assert.Contains(fetch, c => c.Contains("CardPileCmd.Add"));
        Assert.Contains(fetch, c => c.Contains("KokomiPlan.DiscardPileTake"));
    }

    [Fact]
    public void The_fetch_takes_what_the_pile_has_and_nothing_from_an_empty_one()
    {
        Assert.Equal(2, KokomiPlan.DiscardPileTake(2, 5));
        Assert.Equal(1, KokomiPlan.DiscardPileTake(3, 1));
        Assert.Equal(0, KokomiPlan.DiscardPileTake(2, 0));
    }
}
