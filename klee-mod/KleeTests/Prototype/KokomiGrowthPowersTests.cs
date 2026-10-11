using System;
using System.Collections.Generic;
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
/// KOKOMI GROWTH POWERS (2026-10-10). Brief
/// <c>review/active/kokomi-growth-powers-2026-10-10.md</c>, ruled ("Agreed on
/// both"): Rising Tide replaces The General's Banner, Grand Design keeps the
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
    public void Rising_tide_replaces_the_generals_banner_last_in_the_pool()
    {
        var slice = Slice();
        Assert.Equal(78, slice.Count);
        Assert.Equal("ProtoKkRisingTide", slice.Last());
        Assert.DoesNotContain("ProtoKkTheGeneralsBanner", slice);
    }

    [Fact]
    public void Rising_tide_is_a_one_cost_uncommon_power_innate_upgraded()
    {
        var card = new ProtoKkRisingTide();
        Assert.Equal((CardType.Power, CardRarity.Uncommon, 1),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal(
            "At the start of your turn, the [gold]Casket[/gold] gains 1.",
            Face(card));
        Assert.DoesNotContain(CardKeyword.Innate, card.CanonicalKeywords);
        Assert.Contains(CardKeyword.Innate,
                        Upgraded<ProtoKkRisingTide>().Keywords);
        Assert.Contains(Seq("ProtoKkRisingTide", "OnPlay"),
                        c => c.Contains("RisingTidePower"));
    }

    [Fact]
    public void Rising_tide_adds_one_per_copy_at_the_long_game_site()
    {
        var morning = Seq("ProtoBakeKuragePower", "AfterPlayerTurnStart");
        var longGame = morning.FindIndex(c => c.Contains("TheLongGamePower.Signal"));
        var rising = morning.FindIndex(c => c.Contains("RisingTidePower.Signal"));
        var drain = morning.FindIndex(c => c.Contains("KokomiPlan.ResolveAll"));
        Assert.True(longGame >= 0 && longGame < rising && rising < drain);

        KokomiOverhaulLedger.ResetAll();
        var bare = Seat.Kokomi();
        RisingTidePower.Signal(bare.Creature);
        Assert.Equal(0, KokomiOverhaulLedger.For(bare.Creature).CasketCount);

        KokomiOverhaulLedger.ResetAll();
        var seat = Seat.Kokomi().WithPower<RisingTidePower>(2);
        RisingTidePower.Signal(seat.Creature);
        Assert.Equal(2, KokomiOverhaulLedger.For(seat.Creature).CasketCount);
        RisingTidePower.Signal(seat.Creature);
        Assert.Equal(4, KokomiOverhaulLedger.For(seat.Creature).CasketCount);
    }

    [Fact]
    public void Grand_design_costs_two_one_upgraded_and_keeps_the_count()
    {
        var card = new ProtoKkGrandDesign();
        Assert.Equal((CardType.Power, CardRarity.Rare, 2),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal(
            "[gold]Open the Casket[/gold] no longer empties the [gold]Casket[/gold].",
            Face(card));
        Assert.Equal(1, Upgraded<ProtoKkGrandDesign>().EnergyCost
            .GetWithModifiers(CostModifiers.None));
        Assert.DoesNotContain(CardKeyword.Innate,
                              Upgraded<ProtoKkGrandDesign>().Keywords);

        // The Open asks whether Grand Design is worn before it empties.
        var open = Seq("KokomiOverhaulKit", "OpenCasket");
        Assert.Contains(open, c => c.Contains("GrandDesignPower.Keeps"));
        Assert.Contains(open, c => c.Contains("EmptyCasket"));

        KokomiOverhaulLedger.ResetAll();
        Assert.False(GrandDesignPower.Keeps(Seat.Kokomi().Creature));
        Assert.True(GrandDesignPower.Keeps(
            Seat.Kokomi().WithPower<GrandDesignPower>(1).Creature));
        Assert.False(GrandDesignPower.Keeps(null));
    }

    [Fact]
    public void Grand_design_left_the_plan_bus()
    {
        Assert.DoesNotContain(Seq("KokomiPlan", "ResolveEntry"),
                              c => c.Contains("GrandDesignPower"));
    }

    [Fact]
    public void Brine_sting_deals_three_before_its_weak()
    {
        var card = new ProtoKkBrineSting();
        Assert.Contains("[gold]Plan[/gold]: Deal 3 [gold]Hydro[/gold] damage. Apply ",
                        Face(card));
        Assert.Equal((KokomiPlan.Kind.Damage, 3, KokomiPlan.Aim.FrontEnemy),
                     (card.PlanClauses[0].Kind, card.PlanClauses[0].Amount,
                      card.PlanClauses[0].Aim));
    }
}
