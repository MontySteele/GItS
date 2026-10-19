using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI REVIEW, ROUND 5 (2026-10-14,
/// <c>review/active/kokomi-review-r5-2026-10-14.md</c>, section A). The
/// mod's halves of the A-list: the wire carries what a waiting Plan will
/// land and her Strength when it was written (A2); a Counter Plan's running
/// count in its own words (A3); the Watchful Shoal badge defines the Sting
/// and the Ward it names (A9). Sea Glass Harvest's hand is pinned in
/// <c>KokomiRound1FixesTests</c>; the page's halves in
/// <c>tier0/tests/test_kokomi_review_r5_2026_10_14.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiReviewR5Tests
{
    [Fact]
    public void The_queue_row_carries_what_a_plan_lands_and_the_written_strength()
    {
        var keys = Il.Strings(Il.Method("KokomiPlan", "QueueRow"));
        Assert.Contains("written", keys);
        Assert.Contains("written_strength", keys);
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "QueueRow")),
                        c => c.Contains("KokomiPlan.WrittenDamage"));
    }

    [Fact]
    public void A_counter_plans_running_count_is_said_in_its_own_words()
    {
        Assert.Equal("7 blocked so far", KokomiPlan.LiveBlocked(7));
        Assert.Equal("12 taken so far", KokomiPlan.LiveTaken(12));
        var calls = Il.Calls(Il.Method("KokomiPlan", "LiveLine"));
        Assert.Contains(calls, c => c.Contains("KokomiPlan.LiveBlocked"));
        Assert.Contains(calls, c => c.Contains("KokomiPlan.LiveTaken"));
        // The Chain's caption is unchanged.
        Assert.Equal("Deals 14", KokomiPlan.LiveDeals(14));
    }

    [Fact]
    public void The_watchful_shoal_badge_previews_the_sting()
    {
        // Its Ward half left with the Ward's Block (2026-10-18).
        var calls = Il.Calls(Il.Method("WatchfulShoalPower",
                                       "get_ExtraHoverTips"));
        Assert.Contains(calls, c => c.Contains("WithStingPreview"));
        Assert.DoesNotContain(calls, c => c.Contains("WithWardPreview"));
    }
}
