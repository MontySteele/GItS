using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Models.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI BALANCE SUITE 4 (2026-10-21,
/// <c>review/records/kokomi-balance-suite-4-2026-10-21.md</c>, "Defects and
/// legibility"). Defect fixes, no number moves. Structural and pure pins (the
/// headless boundary); sim twin
/// <c>tier0/tests/test_kokomi_suite4_fixes_2026_10_21.py</c>. Crystal
/// Collapse's gate is pinned in <see cref="KokomiWordingPassTests"/>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiSuite4FixesTests
{
    private static KokomiPlan.Entry Gambit() => new(null, new[]
    {
        new KokomiPlan.Planned(KokomiPlan.Kind.NextPlanDoubleDamage, 0,
                               KokomiPlan.Aim.Self),
    });

    private static KokomiPlan.Entry TwoLine(bool flipped) =>
        new(new ProtoKkKuragesOath(),
            new ProtoKkKuragesOath().PlanClauses, Label: "Kurage's Oath",
            Now: flipped);

    // ---- Opening Gambit and a flipped Plan -----------------------------------

    [Fact]
    public void A_flipped_plan_behind_opening_gambit_says_it_loses_the_double()
    {
        // The rule stands (Kokomi review r9, item 4): a now-line lands at
        // printed size, so the double does not reach it. The screen now says
        // so where it said only "Now-line".
        var flipped = TwoLine(flipped: true);
        Assert.True(flipped.TwoLine);
        Assert.False(KokomiPlan.DoubledBy(Gambit(), flipped));
        Assert.True(KokomiPlan.LosesDouble(Gambit(), flipped));
        Assert.False(KokomiPlan.LosesDouble(Gambit(), TwoLine(false)));
        Assert.False(KokomiPlan.LosesDouble(null, flipped));
        var queue = new[] { Gambit(), flipped };
        Assert.True(KokomiPlan.LosesDoubleAt(queue, 1));
        Assert.False(KokomiPlan.LosesDoubleAt(queue, 0));
        Assert.Equal("Now, not doubled", KokomiPlan.StripCaption(
            true, true, null, 0, false, null, doubleLost: true));
        Assert.Equal("Now-line", KokomiPlan.StripCaption(
            true, true, null, 0, false));
        Assert.Contains(KokomiPlanViewRows.NowLineLosesDouble,
            KokomiPlanViewRows.FlipSent(TwoLine(false), behindGambit: true));
        Assert.DoesNotContain("Gambit",
            KokomiPlanViewRows.FlipSent(TwoLine(true), behindGambit: true));
        Assert.DoesNotContain("Gambit",
            KokomiPlanViewRows.FlipSent(TwoLine(false)));
    }

    [Fact]
    public void The_wire_and_the_strip_read_the_lost_double()
    {
        Assert.Contains("double_lost",
            Il.Strings(typeof(KokomiPlan).GetMethod("QueueRow",
                                                    HeadlessGame.All)!));
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "Snapshot")),
            c => c.Contains("KokomiPlan.LosesDoubleAt"));
        Assert.Contains(Il.Calls(Il.Method("KokomiPlanStrip", "Paint")),
            c => c.Contains("KokomiPlan.LosesDoubleAt"));
    }

    // ---- Grand Design and the Tamakushi Casket -------------------------------

    [Fact]
    public void Grand_design_pays_the_casket_for_each_card_it_plans()
    {
        // A Basic planned as itself counts when planned, never face up.
        Assert.True(TamakushiCasket.CountsPlanned(new StrikeSilent()));
        Assert.True(TamakushiCasket.CountsPlanned(new ProtoKkKuragesOath()));
        Assert.False(TamakushiCasket.CountsCard(new StrikeSilent(), planned: false));
        Assert.False(TamakushiCasket.CountsPlanned(new ProtoKkShoalCall()));
        // Both of Grand Design's writes pay through the one door.
        Assert.Contains(Il.Calls(Il.Method("KokomiRefounding", "WriteAsItself")),
            c => c.Contains("TamakushiCasket.PayForPlanned"));
        var free = Il.CallSequence(Il.Method("KokomiRefounding", "WriteFree")).ToList();
        var play = free.FindIndex(c => c.Contains("CardCmd.AutoPlay"));
        var pay = free.FindIndex(c => c.Contains("TamakushiCasket.PayForPlanned"));
        Assert.True(play >= 0 && pay > play, string.Join(" ", free));
        // And the free write's own card play does not pay a second time.
        Assert.Contains(Il.Calls(Il.Method("TamakushiCasket", "Counts")),
            c => c.Contains("KokomiRefounding.IsFreeWrite"));
        Assert.Contains(Il.Calls(Il.Method("TamakushiCasket", "PayForPlanned")),
            c => c.Contains("TamakushiCasket.CountsPlanned"));
    }

    // ---- Press the Advantage's reaction preview ------------------------------

    [Fact]
    public void Press_the_advantage_previews_its_live_number_not_no_damage()
    {
        var card = new ProtoKkPressTheAdvantage();
        Assert.IsAssignableFrom<IBranchDamageFace>(card);
        // Off a board the plain arm, never "no damage".
        Assert.Equal("PlainDamage", KleeCardTooltips.PrintedVar(card)?.Name);
        Assert.Contains(Il.Calls(Il.Method("ProtoKkPressTheAdvantage",
                                           "get_BranchDamageLive")),
            c => c.Contains("KokomiPlan.PlansHeld"));
        // A card with its own damage var reads it, as before.
        Assert.Equal("Damage",
            KleeCardTooltips.PrintedVar(new StrikeSilent())?.Name);
    }

    // ---- Resolve of Watatsumi in the previews --------------------------------

    [Fact]
    public void Resolve_of_watatsumi_is_in_every_plan_preview()
    {
        Assert.Equal(0, KokomiPlan.ResolveHitsBonus(Gambit(), null));
        foreach (var (type, method) in new[]
                 {
                     ("PlanDamageVar", "UpdateCardPreview"),
                     ("KokomiPlan", "ShowQueuedPlanDamage"),
                     ("KokomiPlan", "LiveBlock"),
                     ("KokomiPlan", "ResolveBonusOver"),
                     ("KokomiPlan", "WithResolve"),
                 })
        {
            Assert.Contains(Il.Calls(Il.Method(type, method)),
                c => c.Contains("ResolveOfWatatsumiPower.Bonus"));
        }
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "ForecastFrontDamage")),
            c => c.Contains("KokomiPlan.ResolveFrontBonus"));
        Assert.Contains(Il.Calls(typeof(KokomiPlan).GetMethod("QueueRow",
                                                              HeadlessGame.All)!),
            c => c.Contains("KokomiPlan.ResolveHitsBonus"));
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "LiveLine")),
            c => c.Contains("KokomiPlan.WithResolve"));
    }

    // ---- Shoal Call is not offered for the Bake-Kurage -----------------------

    [Fact]
    public void Shoal_call_prints_no_plan_line()
    {
        // The bridge offers a card for the jellyfish only where it prints a
        // Plan line (`GitsPrintsPlanLine` reads `PlanClauses` by name).
        Assert.False(new ProtoKkShoalCall() is IPlannedCard);
        Assert.Null(typeof(ProtoKkShoalCall).GetProperty("PlanClauses"));
        Assert.NotEmpty(new ProtoKkKuragesOath().PlanClauses);
    }
}
