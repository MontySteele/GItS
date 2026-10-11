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
/// <c>review/active/kokomi-growth-powers-2026-10-10.md</c>, ruled ("Agreed on
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
    public void Flood_tide_replaces_the_generals_banner_last_in_the_pool()
    {
        var slice = Slice();
        Assert.Equal(78, slice.Count);
        Assert.Equal("ProtoKkFloodTide", slice.Last());
        Assert.DoesNotContain("ProtoKkTheGeneralsBanner", slice);
    }

    [Fact]
    public void Flood_tide_is_a_one_cost_uncommon_power_innate_upgraded()
    {
        var card = new ProtoKkFloodTide();
        Assert.Equal((CardType.Power, CardRarity.Uncommon, 1),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal(
            "At the start of your turn, the [gold]Casket[/gold] gains 1.",
            Face(card));
        Assert.DoesNotContain(CardKeyword.Innate, card.CanonicalKeywords);
        Assert.Contains(CardKeyword.Innate,
                        Upgraded<ProtoKkFloodTide>().Keywords);
        Assert.Contains(Seq("ProtoKkFloodTide", "OnPlay"),
                        c => c.Contains("FloodTidePower"));
    }

    [Fact]
    public void Flood_tide_adds_one_per_copy_at_the_long_game_site()
    {
        var morning = Seq("ProtoBakeKuragePower", "AfterPlayerTurnStart");
        var longGame = morning.FindIndex(c => c.Contains("TheLongGamePower.Signal"));
        var rising = morning.FindIndex(c => c.Contains("FloodTidePower.Signal"));
        var drain = morning.FindIndex(c => c.Contains("KokomiPlan.ResolveAll"));
        Assert.True(longGame >= 0 && longGame < rising && rising < drain);

        KokomiOverhaulLedger.ResetAll();
        var bare = Seat.Kokomi();
        FloodTidePower.Signal(bare.Creature);
        Assert.Equal(0, KokomiOverhaulLedger.For(bare.Creature).CasketCount);

        KokomiOverhaulLedger.ResetAll();
        var seat = Seat.Kokomi().WithPower<FloodTidePower>(2);
        FloodTidePower.Signal(seat.Creature);
        Assert.Equal(2, KokomiOverhaulLedger.For(seat.Creature).CasketCount);
        FloodTidePower.Signal(seat.Creature);
        Assert.Equal(4, KokomiOverhaulLedger.For(seat.Creature).CasketCount);
    }

    [Fact]
    public void Grand_design_costs_two_one_upgraded_and_keeps_the_count()
    {
        var card = new ProtoKkGrandDesign();
        Assert.Equal((CardType.Power, CardRarity.Rare, 2),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal(
            "[gold]Open the Casket[/gold] no longer empties the [gold]Casket[/gold]."
          + " At the start of your turn, put it into your hand.",
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
    public void Grand_design_fetches_open_at_flood_tides_site_never_a_second()
    {
        // Kokomi whole-run round 2 (2026-10-10): "At the start of your turn,
        // put it into your hand." Sim twin: `kokomi_plan.grand_design_fetch`.
        var morning = Seq("ProtoBakeKuragePower", "AfterPlayerTurnStart");
        var rising = morning.FindIndex(c => c.Contains("FloodTidePower.Signal"));
        var fetch = morning.FindIndex(c => c.Contains("GrandDesignPower.Signal"));
        var drain = morning.FindIndex(c => c.Contains("KokomiPlan.ResolveAll"));
        Assert.True(rising >= 0 && rising < fetch && fetch < drain);

        // The Signal asks whether it is worn, then whether one is already in
        // hand, and only then fetches (draw pile, then discard pile).
        var signal = Seq("GrandDesignPower", "Signal");
        var keeps = signal.FindIndex(c => c.Contains("GrandDesignPower.Keeps"));
        var holds = signal.FindIndex(c => c.Contains("GrandDesignPower.HoldsOpen"));
        var take = signal.FindIndex(c => c.Contains("KokomiOverhaulKit.FetchOpenCasket"));
        Assert.True(keeps >= 0 && keeps < holds && holds < take);

        Assert.True(GrandDesignPower.HoldsOpen(
            new CardModel[] { new ProtoKkNip(), new OpenTheCasket() }));
        Assert.False(GrandDesignPower.HoldsOpen(new CardModel[] { new ProtoKkNip() }));
        Assert.False(GrandDesignPower.HoldsOpen(null));
    }

    [Fact]
    public void Open_the_casket_prints_its_count_in_combat()
    {
        // Kokomi whole-run round 2 (2026-10-10): Driftglass's pattern.
        Assert.Equal("\n(Gains 7 [gold]Strength[/gold])",
                     OpenTheCasket.Line(7));
        // Out of combat (no owner) the line is empty.
        Assert.Equal("", OpenTheCasket.StrengthLine(
            new OpenTheCasket()));
        var line = Seq("OpenTheCasket", "StrengthLine");
        Assert.Contains(line, c => c.Contains("get_CasketCount"));
        Assert.Contains(line, c => c.Contains("OpenTheCasket.Line"));
    }

    [Fact]
    public void Change_of_plans_draws_one_after_the_carry_out()
    {
        var card = new ProtoKkChangeOfPlans();
        Assert.Equal(0, card.EnergyCost.Canonical);
        Assert.Contains(CardKeyword.Exhaust, card.CanonicalKeywords);
        Assert.Equal("The [gold]Bake-Kurage[/gold] carries out your first "
                   + "[gold]Plan[/gold] now. Draw 1 card.", Face(card));
        var play = Seq("ProtoKkChangeOfPlans", "OnPlay");
        var carry = play.FindIndex(c => c.Contains("KokomiPlan.ResolveFront"));
        var draw = play.FindIndex(c => c.Contains("CardPileCmd.Draw"));
        Assert.True(carry >= 0 && carry < draw);
        // It draws on an empty jellyfish too, so the `EB-455` gate is gone.
        Assert.False(typeof(IUnplayableReasonCard).IsAssignableFrom(card.GetType()));
        Assert.DoesNotContain(CardKeyword.Exhaust,
                              Upgraded<ProtoKkChangeOfPlans>().Keywords);
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

    [Fact]
    public void Brine_sting_deals_four_before_its_weak()
    {
        var card = new ProtoKkBrineSting();
        Assert.Contains("[gold]Plan[/gold]: Deal 4 [gold]Hydro[/gold] damage. Apply ",
                        Face(card));
        Assert.Equal((KokomiPlan.Kind.Damage, 4, KokomiPlan.Aim.FrontEnemy),
                     (card.PlanClauses[0].Kind, card.PlanClauses[0].Amount,
                      card.PlanClauses[0].Aim));
    }
}
