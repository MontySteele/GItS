using System;
using System.Linq;
using System.Reflection;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI FOLLOW-UPS, 2026-10-01 (after PR #777's co-op playtest fixes).
///
/// 1. A CANCEL IS AN UNDO (main session): a cancelled Plan's card returns to
///    the hand even if it has Exhaust. Second Thoughts and All Streams Flow to
///    the Sea both give back through <c>KokomiPlan.GiveBack</c>, which looks in
///    the exhaust pile too; a Moon's Reflection Plan gives back Moon's
///    Reflection, not the card it found.
/// 2. A card Moon's Reflection replays at the morning keeps its Hydro whole:
///    the morning window (<c>AuraPower.MorningWindow</c>) spares every aura
///    applied or refreshed inside the drain, not only a Plan's own hit.
///
/// Headless, so these are call-graph pins (`Il`) plus the pure parts; the
/// numbers live in the sim twin, <c>tier0/tests/test_kokomi_coop_playtest_fixes.py</c>
/// and <c>test_kokomi_plan.py</c>. NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiFollowUpsTests : IDisposable
{
    private readonly bool _kokomi = KokomiOverhaul.Enabled;

    public KokomiFollowUpsTests() => KokomiOverhaul.Enabled = true;

    public void Dispose() => KokomiOverhaul.Enabled = _kokomi;

    [Fact]
    public void Both_cancels_give_the_card_back()
    {
        Assert.Contains("KokomiPlan.GiveBack",
                        Il.Calls(Il.Method("KokomiPlan", "CancelLast")));
        Assert.Contains("KokomiPlan.GiveBack",
                        Il.Calls(Il.Method("KokomiPlan", "CancelAllForNext")));
        Assert.Contains("CardPileCmd.Add",
                        Il.Calls(Il.Method("KokomiPlan", "GiveBack")));
    }

    [Fact]
    public void A_cancel_looks_in_the_exhaust_pile_too()
    {
        var piles = (PileType[])typeof(KokomiPlan)
            .GetField("ReturnPiles", HeadlessGame.All)!.GetValue(null)!;
        Assert.Equal(new[] { PileType.Discard, PileType.Exhaust, PileType.Draw },
                     piles);
    }

    [Fact]
    public void A_moons_reflection_plan_gives_back_moons_reflection()
    {
        var found = new ProtoKkVanguard();
        var moon = new ProtoKkMoonsReflection();
        var clauses = Array.Empty<KokomiPlan.Planned>();
        Assert.Same(moon,
            new KokomiPlan.Entry(found, clauses, Writer: moon).Returns);
        Assert.Same(found, new KokomiPlan.Entry(found, clauses).Returns);
    }

    [Fact]
    public void The_morning_drain_opens_the_aura_window()
    {
        Assert.Contains("MorningWindow",
                        Il.FieldsWritten(Il.Method("KokomiPlan", "ResolveAll")));
    }

    [Fact]
    public void Every_aura_door_notes_the_window()
    {
        Assert.Contains("AuraPower.NoteTouched",
                        Il.Calls(Il.Method("AuraCmd", "Apply")));
        Assert.Contains("AuraPower.NoteTouched",
                        Il.Calls(Il.Method("AuraCmd", "Refresh")));
        Assert.Contains("AuraPower.NoteTouched",
                        Il.Calls(Il.Method("AuraPower", "ResolveLifecycle")));
    }

    [Fact]
    public void A_touched_aura_is_spared_only_inside_the_window()
    {
        var note = typeof(AuraPower).GetMethod("NoteTouched", HeadlessGame.All)!;
        var take = typeof(AuraPower).GetMethod("TakeSparedTick", HeadlessGame.All)!;
        var window = typeof(AuraPower).GetField("MorningWindow", HeadlessGame.All)!;
        var aura = new HydroAuraPower();

        note.Invoke(null, new object[] { aura });
        Assert.False((bool)take.Invoke(aura, null)!);

        window.SetValue(null, 1);
        try
        {
            note.Invoke(null, new object[] { aura });
        }
        finally
        {
            window.SetValue(null, 0);
        }
        Assert.True((bool)take.Invoke(aura, null)!);
        Assert.False((bool)take.Invoke(aura, null)!);   // spent by one tick
    }
}
