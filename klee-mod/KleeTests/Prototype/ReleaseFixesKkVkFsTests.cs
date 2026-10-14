using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE RELEASE FIXES (2026-10-14). Three display fixes, no rule changes:
///
/// 1. Kokomi's Plan strip pages. Past four Plans it said "+N" and a human
///    could neither inspect nor flip the rest; "+N" now turns to the next
///    four, and every page's pictures hover and flip their own Plan.
/// 2. (Varka's signature bark: <c>VarkaStoryTests</c>.)
/// 3. Furina's "below half" prints its number in combat, "below half (39
///    HP)", and every "Spend up to X" says it spends all it can.
///
/// Headless: the strip's paging is pure arithmetic plus call-graph pins
/// (<c>Il</c>); how it looks at 1280x720 is a live question.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class ReleaseFixesKkVkFsTests
{
    private static string Face(CardModel card) =>
        ((BaseLib.Abstracts.CustomCardModel)card).Localization!
            .Single(r => r.Item1 == "description").Item2;

    // ---- 1. the Plan strip pages ----------------------------------------------

    [Theory]
    [InlineData(0, 1)]
    [InlineData(4, 1)]
    [InlineData(5, 2)]
    [InlineData(8, 2)]
    [InlineData(9, 3)]
    public void The_strip_needs_a_page_per_four_plans(int count, int pages)
    {
        Assert.Equal(4, KokomiPlanPages.PerPage);
        Assert.Equal(pages, KokomiPlanPages.PageCount(count));
    }

    [Fact]
    public void The_pager_says_plus_n_then_back()
    {
        // Eight Plans, the seat case: "+4", then "Back" on the second page.
        Assert.Equal("+4", KokomiPlanPages.PagerCaption(0, 8));
        Assert.Equal("Back", KokomiPlanPages.PagerCaption(1, 8));
        // Nine: "+5", "+1", "Back".
        Assert.Equal("+5", KokomiPlanPages.PagerCaption(0, 9));
        Assert.Equal("+1", KokomiPlanPages.PagerCaption(1, 9));
        Assert.Equal("Back", KokomiPlanPages.PagerCaption(2, 9));
        // Four or fewer: no pager at all.
        Assert.Equal("", KokomiPlanPages.PagerCaption(0, 4));
        Assert.Equal("", KokomiPlanPages.PagerCaption(0, 0));
    }

    [Fact]
    public void A_click_on_the_pager_turns_to_the_next_page_and_wraps()
    {
        Assert.Equal(1, KokomiPlanPages.NextPage(0, 8));
        Assert.Equal(0, KokomiPlanPages.NextPage(1, 8));
        Assert.Equal(2, KokomiPlanPages.NextPage(1, 9));
        Assert.Equal(0, KokomiPlanPages.NextPage(0, 3));
        Assert.Equal(4, KokomiPlanPages.PageStart(1, 8));
        Assert.Equal(8, KokomiPlanPages.PageStart(2, 9));
    }

    [Fact]
    public void A_page_past_a_shortened_queue_falls_back_to_the_front()
    {
        // The morning drain carries Plans out under an open second page.
        Assert.Equal(0, KokomiPlanPages.ClampPage(1, 4));
        Assert.Equal(0, KokomiPlanPages.PageStart(2, 5));
        Assert.Equal(1, KokomiPlanPages.ClampPage(1, 5));
    }

    [Fact]
    public void A_later_page_names_each_plans_place()
    {
        Assert.Equal("First", KokomiPlanPages.PositionCaption(0, 0, 8));
        Assert.Null(KokomiPlanPages.PositionCaption(0, 0, 1));
        Assert.Null(KokomiPlanPages.PositionCaption(2, 0, 8));
        Assert.Equal("Plan 5", KokomiPlanPages.PositionCaption(4, 1, 8));
        Assert.Equal("Plan 8", KokomiPlanPages.PositionCaption(7, 1, 8));
    }

    [Fact]
    public void Every_page_hovers_and_flips_its_own_plan()
    {
        // The pager is wired, and painting reads the page.
        Assert.Contains("KokomiPlanStrip.WirePager",
                        Il.Calls(Il.Method("KokomiPlanStrip", "Build")));
        var paint = Il.Calls(Il.Method("KokomiPlanStrip", "Paint"));
        Assert.Contains("KokomiPlanPages.PageStart", paint);
        Assert.Contains("KokomiPlanPages.PagerCaption", paint);
        Assert.Contains("KokomiPlanStrip.SetCard", paint);
        // The pager repaints; it moves no Plan, so it asks no flip.
        var pager = Il.Calls(Il.Method("KokomiPlanStrip", "WirePager"));
        Assert.Contains(pager, c => c.Contains("KokomiPlanStrip.Paint"));
        Assert.DoesNotContain(pager, c => c.Contains("RequestFlip"));
        // A picture's click still goes through the co-op-safe request.
        var click = Il.Calls(Il.Method("KokomiPlanStrip", "WireClick"));
        Assert.Contains(click, c => c.Contains("KokomiPlan.RequestFlip"));
    }

    // ---- 3. Furina's faces ----------------------------------------------------

    [Theory]
    [InlineData(78, 39)]
    [InlineData(79, 40)]
    [InlineData(80, 40)]
    [InlineData(1, 1)]
    public void Below_half_means_below_half_of_max_hp_rounded_up(
        int max, int threshold)
    {
        Assert.Equal(threshold, HalfHpFace.Threshold(max));
        // The rule the cards and Crowd Favorite check: hp * 2 < max.
        Assert.True((threshold - 1) * 2 < max);
        Assert.False(threshold * 2 < max);
        Assert.Equal($" ({threshold} HP)", HalfHpFace.Words(max));
    }

    [Fact]
    public void A_below_half_face_prints_its_number_in_combat()
    {
        foreach (var card in new CardModel[]
                 {
                     new ProtoFsUnderstudysDebut(), new ProtoFsCrowdFavorite(),
                 })
        {
            Assert.Contains("below half{InCombat:{HalfHp}|}", Face(card));
        }
        // "below half HP" keeps its word out of combat.
        Assert.Contains("below half{InCombat:{HalfHp}| HP}",
                        Face(new ProtoMcNoelleBreastplate()));
        // A card with no owner prints nothing.
        Assert.Equal("", HalfHpFace.Line(new ProtoFsUnderstudysDebut()));
        Assert.Contains("HalfHpFace.Line",
                        Il.Calls(Il.Method("ProtoFsUnderstudysDebut",
                                           "AddExtraArgsToDescription")));
    }

    [Fact]
    public void Crowd_favorite_tip_prints_the_number()
    {
        var loc = new global::KleeMod.Powers.CrowdFavoritePower().Localization!;
        Assert.Contains(loc, r => r.Item1 == "smartDescription"
                                  && r.Item2.Contains("if your HP is below {HalfHp}, gain"));
    }

    [Fact]
    public void Every_spend_up_to_says_it_spends_all_it_can()
    {
        foreach (var card in new CardModel[]
                 {
                     new ProtoFsTidalFlourish(), new ProtoFsHoldTheStage(),
                     new ProtoFsCrashingWaves(), new ProtoFsTheFullHouse(),
                 })
        {
            var face = Face(card);
            Assert.Contains("up to", face);
            Assert.Contains(", all you can:", face);
        }
    }
}
