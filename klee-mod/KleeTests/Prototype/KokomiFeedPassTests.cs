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
/// THE FEED PASS (2026-09-29). [USER], after an act-1 death: "some Plan cards
/// need to go to 0 cost so there's some way to draft lower-impact feed for the
/// Plan mechanism. Let's not make too many 'do a thing now AND get a plan
/// going' cards - those should be higher rarity at least." Five 0-cost
/// Plan-only Commons join the offer; eight now-and-Plan Commons move to
/// Uncommon; Coral Bulwark loses its Plan line and blocks 8; Exposed Flank is
/// cut. Sim twin: <c>tier0/tests/test_kokomi_feed_pass.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiFeedPassTests : IDisposable
{

    public KokomiFeedPassTests() { }

    public void Dispose() { }

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

    private static void AssertFeedShape(CardModel card)
    {
        Assert.Equal((CardType.Skill, CardRarity.Common, 0),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        // Plan-only: "Plan:", no "or" (2026-10-01).
        Assert.StartsWith("Play on the [gold]Bake-Kurage[/gold].\n[gold]Plan[/gold]: ",
                          Face(card));
    }

    [Fact]
    public void Bubble_ward_plans_four_block_six_upgraded()
    {
        var card = new ProtoKkBubbleWard();
        AssertFeedShape(card);
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal((KokomiPlan.Kind.Block, 4, KokomiPlan.Aim.Self),
                     (clause.Kind, clause.Amount, clause.Aim));
        Assert.Equal(6, Upgraded<ProtoKkBubbleWard>().PlanClauses.Single().Amount);
    }

    [Fact]
    public void Nip_plans_five_damage_to_the_front_enemy_seven_upgraded()
    {
        var card = new ProtoKkNip();
        AssertFeedShape(card);
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal((KokomiPlan.Kind.Damage, 5, KokomiPlan.Aim.FrontEnemy),
                     (clause.Kind, clause.Amount, clause.Aim));
        Assert.Equal(7, Upgraded<ProtoKkNip>().PlanClauses.Single().Amount);
    }

    [Fact]
    public void Jellyfish_drift_plans_two_to_all_three_upgraded()
    {
        var card = new ProtoKkJellyfishDrift();
        AssertFeedShape(card);
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal((KokomiPlan.Kind.Damage, 2, KokomiPlan.Aim.AllEnemies),
                     (clause.Kind, clause.Amount, clause.Aim));
        Assert.Equal(3, Upgraded<ProtoKkJellyfishDrift>().PlanClauses.Single().Amount);
    }

    [Fact]
    public void Current_read_plans_a_draw_and_its_upgrade_adds_two_block()
    {
        // No upgrade key adds a Plan clause, so the Block clause is written at
        // 0 and printed only upgraded; `KokomiPlan` carries a 0 flat Block out
        // as nothing, never a Dexterity-sized Block.
        var card = new ProtoKkCurrentRead();
        AssertFeedShape(card);
        Assert.Equal(new[] { (KokomiPlan.Kind.Draw, 1), (KokomiPlan.Kind.Block, 0) },
                     card.PlanClauses.Select(c => (c.Kind, c.Amount)).ToArray());
        Assert.Equal(new[] { (KokomiPlan.Kind.Draw, 1), (KokomiPlan.Kind.Block, 2) },
                     Upgraded<ProtoKkCurrentRead>().PlanClauses
                         .Select(c => (c.Kind, c.Amount)).ToArray());
        Assert.Contains("{IfUpgraded:show: Gain 2 [gold]Block[/gold].|}", Face(card));
    }

    [Fact]
    public void Brine_sting_plans_one_weak_on_the_front_enemy_two_upgraded()
    {
        var card = new ProtoKkBrineSting();
        AssertFeedShape(card);
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal((KokomiPlan.Kind.ApplyWeak, 1, KokomiPlan.Aim.FrontEnemy),
                     (clause.Kind, clause.Amount, clause.Aim));
        Assert.Equal(2, Upgraded<ProtoKkBrineSting>().PlanClauses.Single().Amount);
    }

    [Fact]
    public void Coral_bulwark_blocks_eight_and_writes_no_plan()
    {
        var card = new ProtoKkCoralBulwark();
        Assert.Equal(CardRarity.Common, card.Rarity);
        Assert.Equal(8m, card.DynamicVars.Block.BaseValue);
        Assert.Equal(11m, Upgraded<ProtoKkCoralBulwark>().DynamicVars.Block.BaseValue);
        Assert.False(typeof(IPlannedCard).IsAssignableFrom(card.GetType()));
        Assert.DoesNotContain("Plan", Face(card));
    }

    [Fact]
    public void The_eight_now_and_plan_commons_are_uncommon()
    {
        foreach (var card in new CardModel[]
                 {
                     new ProtoKkAmbush(), new ProtoKkReadTheField(),
                     new ProtoKkStolenChapter(), new ProtoKkRiptide(),
                     new ProtoKkPincer(),
                     new ProtoKkSignalArrow(), new ProtoKkSurgingShoal(),
                 })
        {
            Assert.Equal(CardRarity.Uncommon, card.Rarity);
        }
    }

    [Fact]
    public void The_offer_ends_with_the_five_and_holds_no_exposed_flank()
    {
        var slice = Il.CallSequence(Il.Method("KokomiOverhaulRoster", "Slice"))
            .Where(c => c.StartsWith("ModelDb.Card", StringComparison.Ordinal))
            .ToList();
        // SIXTY-NINE since expansion batch one (2026-09-29), whose 22 rows
        // follow the five; SEVENTY since the payoff pass (2026-10-01);
        // SEVENTY-EIGHT since pool completion and since the status batch
        // (2026-10-01), which cut six rows ahead of the five.
        Assert.Equal(78, slice.Count);
        Assert.Equal(new[] { "ProtoKkBubbleWard", "ProtoKkNip", "ProtoKkJellyfishDrift",
                             "ProtoKkCurrentRead", "ProtoKkBrineSting" },
                     slice.Skip(35).Take(5).Select(c => c.Substring(c.IndexOf('<') + 1).TrimEnd('>'))
                          .ToArray());
        Assert.DoesNotContain(slice, c => c.Contains("ProtoKkExposedFlank"));
    }
}
