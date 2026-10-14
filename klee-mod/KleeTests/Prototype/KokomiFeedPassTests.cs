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

    [Fact]
    public void Brine_sting_is_a_one_cost_attack_with_a_vulnerable_plan()
    {
        // The re-founding (2026-10-12): "Deal 8 Hydro damage. Or plan: Apply
        // 1 Vulnerable to ALL enemies." [11].
        var card = new ProtoKkBrineSting();
        // Uncommon since the Kokomi review (2026-10-13).
        Assert.Equal((CardType.Attack, CardRarity.Uncommon, 1),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        // The numbers pass (kokomi-review-r5-2026-10-14): 10 [13], Plan 10 [13].
        Assert.Equal(10m, card.DynamicVars.Damage.BaseValue);
        Assert.Equal(13m, Upgraded<ProtoKkBrineSting>().DynamicVars.Damage.BaseValue);
        // The pool overhaul (2026-10-13): a Counter line, 8 [11] to each
        // enemy that attacked her since she planned it.
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal((KokomiPlan.Kind.Damage, 10, KokomiPlan.Aim.EnemiesAttackedSince),
                     (clause.Kind, clause.Amount, clause.Aim));
        Assert.Equal(13, Assert.Single(
            Upgraded<ProtoKkBrineSting>().PlanClauses).Amount);
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
                     new ProtoKkRiptide(),
                     new ProtoKkPincer(),
                     new ProtoKkSurgingShoal(),
                 })
        {
            Assert.Equal(CardRarity.Uncommon, card.Rarity);
        }
    }

}
