using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI GROWTH POWERS (2026-10-10). Brief
/// <c>review/active/kokomi-growth-powers-2026-10-10.md</c> (archived), ruled ("Agreed on
/// both"): Flood Tide replaces The General's Banner, Grand Design keeps the
/// Casket's count, and Brine Sting's Plan deals 3 before its Weak. Readers
/// that run synchronously run for real on a headless seat; anything that
/// awaits a command is pinned off the compiled methods. Sim twin:
/// <c>tier0/tests/test_kokomi_growth_powers.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiGrowthPowersTests
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

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    private static List<string> Slice() =>
        Il.CallSequence(Il.Method("KokomiOverhaulRoster", "Slice"))
            .Where(c => c.StartsWith("ModelDb.Card", StringComparison.Ordinal))
            .Select(c => c.Substring(c.IndexOf('<') + 1).TrimEnd('>'))
            .ToList();

    [Fact]
    public void Change_of_plans_draws_two_after_the_carry_out()
    {
        // The Kokomi card pass (2026-10-11): draws 2; Exhaust stays. [USER]'s
        // run (2026-10-11): the upgrade keeps Exhaust and draws 3.
        var card = new ProtoKkChangeOfPlans();
        Assert.Equal(0, card.EnergyCost.Canonical);
        Assert.Contains(CardKeyword.Exhaust, card.CanonicalKeywords);
        Assert.Equal(2m, card.DynamicVars.Cards.BaseValue);
        Assert.Equal("The [gold]Bake-Kurage[/gold] carries out your first "
                   + "[gold]Plan[/gold] now. Draw {Cards:diff()} cards.", Face(card));
        var play = Seq("ProtoKkChangeOfPlans", "OnPlay");
        var carry = play.FindIndex(c => c.Contains("KokomiPlan.ResolveFront"));
        var draw = play.FindIndex(c => c.Contains("CardPileCmd.Draw"));
        Assert.True(carry >= 0 && carry < draw);
        // It draws on an empty jellyfish too, so the `EB-455` gate is gone.
        Assert.False(typeof(IUnplayableReasonCard).IsAssignableFrom(card.GetType()));
        var up = Upgraded<ProtoKkChangeOfPlans>();
        Assert.Contains(CardKeyword.Exhaust, up.Keywords);
        Assert.Equal(3m, up.DynamicVars.Cards.BaseValue);
        Assert.Equal(0, up.EnergyCost.Canonical);
    }

    [Fact]
    public void A_queue_row_says_when_vulnerable_raised_its_number()
    {
        // Kokomi whole-run round 2 (2026-10-10): the wire key the page reads
        // to print "(after Vulnerable)" (`blindplay_board.kokomi_plans`).
        var row = typeof(KokomiPlan).GetMethod("QueueRow", HeadlessGame.All)!;
        Assert.Contains("after_vulnerable", Il.Strings(row));
        Assert.Contains("KokomiPlan.RaisedByVulnerable", Il.Calls(row));
        var raised = Seq("KokomiPlan", "RaisedByVulnerable");
        Assert.Contains(raised, c => c.Contains("KokomiPlan.FrontEnemy"));
        Assert.Contains(raised, c => c.Contains("KokomiPlan.PlannedDamage"));
        // No front damage written: never raised.
        Assert.False(KokomiPlan.RaisedByVulnerable(
            new KokomiPlan.Entry(null, System.Array.Empty<KokomiPlan.Planned>()),
            null));
    }

    [Fact]
    public void Grand_design_left_the_plan_bus()
    {
        Assert.DoesNotContain(Seq("KokomiPlan", "ResolveEntry"),
                              c => c.Contains("GrandDesignPower"));
    }

}
