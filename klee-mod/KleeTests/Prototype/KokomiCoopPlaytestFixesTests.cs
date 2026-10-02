using System;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE CO-OP PLAYTEST, 2026-09-30 (a guest played Kokomi). Four rows:
///
/// 1. "Hydro doesn't always seem to apply -- possibly Plans." A Plan's hit
///    applies Hydro (<c>ElementalHit.Deal</c>, pinned in
///    <c>KokomiQuarterHitTests</c>), but the morning runs in
///    <c>AfterPlayerTurnStart</c> and the aura tick in the later
///    <c>AfterSideTurnStart</c>, so a morning Hydro read 1 turn the moment it
///    landed. The morning hit now spares that one tick; the sim already ticks
///    before the morning (`test_kokomi_plan`'s twin pin).
/// 2. "Riptide and Vanguard on the Plan gave 2 Energy, not 3." The game log
///    shows Second Thoughts played after both: it cancelled Vanguard, the
///    newest Plan, and Vanguard Exhausts, so no card came back to say so. The
///    jellyfish now says which Plan a cancel took.
/// 3. The Plan strip's thumbnails show the whole card on hover.
/// 4. [USER]: "Riptide - buff the Draw from 1 to 2, and upgrades to 3".
///
/// Headless, so rows 1 to 3 are call-graph pins (`Il`); the numbers live in
/// the sim twin, <c>tier0/tests/test_kokomi_coop_playtest_fixes.py</c>.
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiCoopPlaytestFixesTests : IDisposable
{

    public KokomiCoopPlaytestFixesTests() { }

    public void Dispose() { }

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    [Fact]
    public void A_plan_hit_spares_its_hydro_the_morning_tick()
    {
        Assert.Contains("AuraPower.SpareThisTurnStartTick",
                        Il.Calls(Il.Method("KokomiPlan", "Hit")));
    }

    [Fact]
    public void The_aura_tick_asks_for_a_spared_tick_first()
    {
        var tick = Il.CallSequence(Il.Method("AuraPower", "AfterSideTurnStart"));
        var asks = tick.ToList().IndexOf("AuraPower.TakeSparedTick");
        var ticks = tick.ToList().IndexOf("PowerCmd.TickDownDuration");
        Assert.True(asks >= 0, "the tick never reads the spare");
        Assert.True(ticks > asks, "the spare is read after the tick");
    }

    [Fact]
    public void A_plan_thumbnail_previews_the_whole_card_on_hover()
    {
        Assert.Contains("KokomiPlanStrip.WireHover",
                        Il.Calls(Il.Method("KokomiPlanStrip", "Build")));
        Assert.Contains("KokomiPlanStrip.SetCard",
                        Il.Calls(Il.Method("KokomiPlanStrip", "Paint")));
        var show = Il.Calls(Il.Method("KokomiPlanStrip", "ShowHover"));
        Assert.Contains("HoverTipFactory.FromCard", show);
        Assert.Contains("NHoverTipSet.CreateAndShow", show);
    }

    [Fact]
    public void Riptide_plans_two_energy_and_two_cards_three_upgraded()
    {
        var plan = new ProtoKkRiptide().PlanClauses;
        Assert.Equal(
            new[] { (KokomiPlan.Kind.Energy, 2), (KokomiPlan.Kind.Draw, 2) },
            plan.Select(c => (c.Kind, c.Amount)).ToArray());
        var up = Upgraded<ProtoKkRiptide>().PlanClauses;
        Assert.Equal(
            new[] { (KokomiPlan.Kind.Energy, 2), (KokomiPlan.Kind.Draw, 3) },
            up.Select(c => (c.Kind, c.Amount)).ToArray());
    }
}
