using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI SEAT TRIAGE (2026-10-23). Kelp Wall+'s Plan preview said "No enemy
/// intends to attack" and the page "deals 0", then the carry-out dealt 4:
/// <c>AskedFor</c> adds the upgrade's flat bonus (and <c>Hit</c> Resolve of
/// Watatsumi's) to the blocked count, and the caption left both out. The
/// caption and the wire's <c>counter_deals</c> now say what lands. The
/// page's half is in
/// <c>tier0/tests/test_kokomi_seat_triage_2026_10_23.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiSeatTriageTests
{
    [Fact]
    public void A_counter_plan_deals_its_count_plus_its_flat_bonus()
    {
        // Kelp Wall+ with nothing blocked: the flat 4.
        Assert.Equal(4, KokomiPlan.CounterDealsOf(0, 4, 0));
        // And Resolve of Watatsumi's bonus on a hit above 0.
        Assert.Equal(6, KokomiPlan.CounterDealsOf(0, 4, 2));
        Assert.Equal(13, KokomiPlan.CounterDealsOf(7, 4, 2));
        // Base Kelp Wall with nothing blocked lands nothing, Resolve or not
        // (`Hit` returns before adding it to a 0).
        Assert.Equal(0, KokomiPlan.CounterDealsOf(0, 0, 2));
    }

    [Fact]
    public void The_caption_says_what_lands_where_it_differs_from_the_count()
    {
        Assert.Equal("7 blocked so far", KokomiPlan.LiveBlocked(7, 7));
        Assert.Equal("7 blocked, deals 11", KokomiPlan.LiveBlocked(7, 11));
        Assert.Equal("12 taken so far", KokomiPlan.LiveTaken(12, 12));
        Assert.Equal("12 taken, deals 17", KokomiPlan.LiveTaken(12, 17));
        Assert.Equal("No enemy intends to attack", KokomiPlan.NoAttackDeals(0));
        Assert.Equal("No enemy intends to attack: deals 4",
                     KokomiPlan.NoAttackDeals(4));
    }

    [Fact]
    public void The_live_line_and_the_wire_read_the_counter_total()
    {
        var calls = Il.Calls(Il.Method("KokomiPlan", "LiveLine"));
        Assert.Contains(calls, c => c.Contains("KokomiPlan.CounterDeals"));
        Assert.Contains(calls, c => c.Contains("KokomiPlan.NoAttackDeals"));
        Assert.Contains("counter_deals",
                        Il.Strings(Il.Method("KokomiPlan", "QueueRow")));
    }
}
