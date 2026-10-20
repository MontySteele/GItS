using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// GRAND DESIGN TAKES BASICS (2026-10-18, review/active/open-design-items-
/// 2026-10-18.md, ruled; [USER]: "Ok, agreed on all defaults for both the PR
/// and inazuma companions"). "Plan up to 3 cards from your Hand, Basic cards
/// included. They cost 0." A Basic Attack or Skill with no Plan line is
/// offered, and its Plan plays a free copy of it at the carry-out
/// (<see cref="KokomiPlan.Kind.PlayAsItself"/>). Only Grand Design opens the
/// door. Sim twin: <c>tier0/tests/test_grand_design_basics_2026_10_18.py</c>,
/// which drives the write and the carry-out; the C# write goes through the
/// game's pile and play commands and is pinned structurally here.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiGrandDesignBasicsTests
{
    [Fact]
    public void Her_strike_and_defend_are_planned_as_themselves()
    {
        Assert.True(KokomiRefounding.PlansAsItself(new StrikeSilent()));
        Assert.True(KokomiRefounding.PlansAsItself(new DefendSilent()));
        Assert.True(KokomiRefounding.GrandDesignTakes(new StrikeSilent()));
        // The Bake-Kurage itself still refuses them.
        Assert.False(KokomiRefounding.CanBeWritten(new StrikeSilent()));
    }

    [Fact]
    public void Plan_cards_are_written_and_other_cards_stay_out()
    {
        // A card with a Plan line is written as before, not as itself.
        Assert.False(KokomiRefounding.PlansAsItself(new ProtoKkKuragesOath()));
        Assert.True(KokomiRefounding.GrandDesignTakes(new ProtoKkKuragesOath()));
        // A non-Basic card with no Plan line is still out.
        Assert.False(KokomiRefounding.GrandDesignTakes(new ProtoKkShoalCall()));
        Assert.False(KokomiRefounding.GrandDesignTakes(null));
    }

    [Fact]
    public void A_hand_of_basics_makes_grand_design_playable()
    {
        var self = new ProtoKkGrandDesign();
        Assert.True(KokomiRefounding.AnyOtherToPlan(
            new CardModel[] { self, new StrikeSilent() }, self));
        Assert.False(KokomiRefounding.AnyOtherToPlan(
            new CardModel[] { self, new ProtoKkShoalCall() }, self));
    }

    [Fact]
    public void The_hand_screen_offers_basics_and_routes_each_pick()
    {
        var calls = Il.Calls(Il.Method("KokomiCards", "GrandDesign"));
        // (The screen's filter is a method group, `GrandDesignTakes`, which
        // a call scan cannot see; the gate tests above read it.)
        Assert.Contains(calls, c => c.Contains("WriteFree"));
        Assert.Contains(calls, c => c.Contains("WriteAsItself"));
    }

    [Fact]
    public void The_write_moves_the_card_and_schedules_one_play_as_itself_clause()
    {
        var calls = Il.Calls(Il.Method("KokomiRefounding", "WriteAsItself"));
        Assert.Contains(calls, c => c.Contains("CardPileCmd.Add"));
        Assert.Contains(calls, c => c.Contains("KokomiPlan.Schedule"));
        // Moved, not played: no auto-play at the write.
        Assert.DoesNotContain(calls, c => c.Contains("CardCmd.AutoPlay"));
    }

    [Fact]
    public void The_carry_out_plays_an_exhausted_copy()
    {
        var calls = Il.Calls(Il.Method("KokomiPlan", "PlayAsItself"));
        Assert.Contains(calls, c => c.Contains("CloneCard"));
        Assert.Contains(calls, c => c.Contains("set_ExhaustOnNextPlay"));
        Assert.Contains(calls, c => c.Contains("CardCmd.AutoPlay"));
    }

    [Fact]
    public void A_basic_plan_has_one_line_plays_a_card_and_is_not_an_attack_played()
    {
        var strike = new StrikeSilent();
        var entry = new KokomiPlan.Entry(strike, new[]
        {
            new KokomiPlan.Planned(KokomiPlan.Kind.PlayAsItself, 1,
                                   KokomiPlan.Aim.FrontEnemy, strike),
        });
        Assert.False(entry.TwoLine);
        Assert.True(KokomiPlan.PlaysAsItself(entry));
        Assert.True(KokomiPlan.PlaysACard(entry));
        // A one-line Plan cannot be flipped.
        var queue = new List<KokomiPlan.Entry> { entry };
        Assert.False(KokomiPlan.FlipAt(queue, 0));
        Assert.False(queue[0].Now);
        // No caption under its picture: the picture is the card's own face.
        Assert.Null(KokomiPlan.StripCaption(entry.TwoLine, false, null, 0,
                                            false));
    }

    private static KokomiPlan.Entry AsItself(CardModel card) =>
        new(card, new[]
        {
            new KokomiPlan.Planned(KokomiPlan.Kind.PlayAsItself, 1,
                                   KokomiPlan.Aim.FrontEnemy, card),
        });

    private static string WrittenAim(KokomiPlan.Entry entry) =>
        (string)typeof(KokomiPlan).GetMethod("WrittenAim",
                System.Reflection.BindingFlags.NonPublic
                | System.Reflection.BindingFlags.Static)!
            .Invoke(null, new object[] { entry })!;

    [Fact]
    public void A_planned_strike_forecasts_its_own_damage_at_the_front()
    {
        // The Plan list read 0 for a planned Strike: the forecast counted
        // Plan-line damage only (2026-10-18).
        var strike = AsItself(new StrikeSilent());
        Assert.Equal(6, KokomiPlan.AsItselfDamage(strike, null));
        Assert.Equal(6, KokomiPlan.ForecastFrontDamage(strike, null));
        // Nereid's Ascension's double, as any planned hit.
        Assert.Equal(12, KokomiPlan.ForecastFrontDamage(strike, null, true));
        Assert.Equal("front", WrittenAim(strike));
        // Converging Tide's stamp lands it elsewhere, as any planned hit.
        Assert.Equal("other", WrittenAim(strike with { AimOverride = "1" }));
    }

    [Fact]
    public void A_planned_defend_forecasts_no_damage_and_its_block_only_in_combat()
    {
        var defend = AsItself(new DefendSilent());
        Assert.Equal(0, KokomiPlan.AsItselfDamage(defend, null));
        Assert.Equal(0, KokomiPlan.ForecastFrontDamage(defend, null));
        Assert.Equal("", WrittenAim(defend));
        // No combat to fold Dexterity and Frail against: no number.
        Assert.Null(KokomiPlan.AsItselfBlock(defend, null));
        Assert.Null(KokomiPlan.AsItselfBlock(AsItself(new StrikeSilent()), null));
    }

    [Fact]
    public void The_queue_row_reads_the_as_itself_forecast()
    {
        var calls = Il.Calls(Il.Method("KokomiPlan", "QueueRow"));
        Assert.Contains(calls, c => c.Contains("AsItselfBlock"));
        Assert.Contains(calls, c => c.Contains("AsItselfDamage"));
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "ForecastFrontDamage")),
                        c => c.Contains("AsItselfDamage"));
    }

    [Fact]
    public void Grand_designs_face_no_longer_says_basic_cards_included()
    {
        // The Kokomi finish pass (2026-10-19): the words are cut, the rule
        // stays (the pins above).
        var face = new ProtoKkGrandDesign().Localization!
            .Single(kv => kv.Item1 == "description").Item2;
        Assert.Equal("Plan up to {KkAmount:diff()} cards from your "
                   + "[gold]Hand[/gold]. They cost 0. Draw 1 card for each.",
                     face);
    }
}
