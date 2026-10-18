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
///    the morning window (<c>AuraPower.OpenMorning</c>) spares every aura
///    she applies or refreshes inside the drain, not only a Plan's own hit.
///
/// Headless, so these are call-graph pins (`Il`) plus the pure parts; the
/// numbers live in the sim twin, <c>tier0/tests/test_kokomi_coop_playtest_fixes.py</c>
/// and <c>test_kokomi_plan.py</c>. NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiFollowUpsTests : IDisposable
{

    public KokomiFollowUpsTests() { }

    public void Dispose() { }

    [Fact]
    public void A_moons_reflection_plan_gives_back_moons_reflection()
    {
        var found = new ProtoKkAmbush();
        // Moon's Reflection left with the Kokomi pool overhaul (2026-10-13);
        // the writer rule stands, read here off any other card.
        var moon = new ProtoKkTidecleanse();
        var clauses = Array.Empty<KokomiPlan.Planned>();
        Assert.Same(moon,
            new KokomiPlan.Entry(found, clauses, Writer: moon).Returns);
        Assert.Same(found, new KokomiPlan.Entry(found, clauses).Returns);
    }

    [Fact]
    public void The_morning_drain_opens_the_aura_window()
    {
        var calls = Il.Calls(Il.Method("KokomiPlan", "ResolveAll"));
        Assert.Contains("AuraPower.OpenMorning", calls);
        Assert.Contains("AuraPower.CloseMorning", calls);
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

    private static readonly MethodInfo Note =
        typeof(AuraPower).GetMethod("NoteTouched", HeadlessGame.All)!;
    private static readonly MethodInfo Take =
        typeof(AuraPower).GetMethod("TakeSparedTick", HeadlessGame.All)!;
    private static readonly MethodInfo Open =
        typeof(AuraPower).GetMethod("OpenMorning", HeadlessGame.All)!;
    private static readonly MethodInfo Close =
        typeof(AuraPower).GetMethod("CloseMorning", HeadlessGame.All)!;
    private static readonly MethodInfo Reset =
        typeof(AuraPower).GetMethod("ResetMornings", HeadlessGame.All)!;

    private static bool TouchAndTake(AuraPower aura, Seat applier)
    {
        Note.Invoke(null, new object[] { aura, applier.Creature });
        return (bool)Take.Invoke(aura, null)!;
    }

    [Fact]
    public void A_touched_aura_is_spared_only_inside_the_window()
    {
        var kokomi = Seat.Kokomi();
        var aura = new HydroAuraPower();
        Reset.Invoke(null, null);

        Assert.False(TouchAndTake(aura, kokomi));

        Open.Invoke(null, new object[] { kokomi.Creature });
        try
        {
            Note.Invoke(null, new object[] { aura, kokomi.Creature });
        }
        finally
        {
            Close.Invoke(null, new object[] { kokomi.Creature });
        }
        Assert.True((bool)Take.Invoke(aura, null)!);
        Assert.False((bool)Take.Invoke(aura, null)!);   // spent by one tick
        Assert.False(TouchAndTake(aura, kokomi));       // and closed again
    }

    /// <summary>CO-OP STATE DIVERGENCE (2026-10-17): while her drain waits on
    /// a choice the partner's queue keeps running, in an order the two
    /// machines need not share. The window is hers alone, so a partner's hit
    /// inside it ticks like any other.</summary>
    [Fact]
    public void A_partners_aura_inside_her_morning_is_not_spared()
    {
        var kokomi = Seat.Kokomi();
        var yae = Seat.Yae();
        var aura = new ElectroAuraPower();
        Reset.Invoke(null, null);
        Open.Invoke(null, new object[] { kokomi.Creature });
        try
        {
            Assert.False(TouchAndTake(aura, yae));
            Assert.True(TouchAndTake(aura, kokomi));
        }
        finally
        {
            Close.Invoke(null, new object[] { kokomi.Creature });
        }
    }

    /// <summary>CO-OP STATE DIVERGENCE (2026-10-17): "we just got a
    /// multiplayer state divergence and had to restart the fight again." A
    /// drain abandoned while paused on a choice never reaches its
    /// <c>finally</c>; the window it opened must not outlive the fight.</summary>
    [Fact]
    public void A_drain_the_last_fight_never_finished_leaves_no_window()
    {
        var kokomi = Seat.Kokomi();
        var aura = new ElectroAuraPower();
        Reset.Invoke(null, null);
        Open.Invoke(null, new object[] { kokomi.Creature });   // never closed
        Assert.True(TouchAndTake(aura, kokomi));

        Reset.Invoke(null, null);   // what combat start runs
        Assert.False(TouchAndTake(aura, kokomi));
    }

    [Fact]
    public void Combat_start_closes_every_morning_window()
    {
        Assert.Contains("AuraPower.ResetMornings",
                        Il.Calls(Il.Method("KleeElementalHooks", "BeforeCombatStart")));
        Assert.Contains("KokomiPlan.ResetFight",
                        Il.Calls(Il.Method("KleeElementalHooks", "BeforeCombatStart")));
    }

    [Fact]
    public void A_new_fight_forgets_a_suspended_morning_and_carry_out()
    {
        var kokomi = Seat.Kokomi();
        var plan = typeof(KokomiPlan);
        var morning = (System.Collections.Generic.HashSet<MegaCrit.Sts2.Core.Entities.Players.Player>)
            plan.GetField("_morning", HeadlessGame.All)!.GetValue(null)!;
        var carrying = (System.Collections.Generic.HashSet<MegaCrit.Sts2.Core.Entities.Players.Player>)
            plan.GetField("_carrying", HeadlessGame.All)!.GetValue(null)!;
        morning.Add(kokomi.Player);
        carrying.Add(kokomi.Player);
        Assert.True(KokomiPlan.InMorning(kokomi.Creature));
        Assert.True(KokomiPlan.IsCarryingOut(kokomi.Player));

        KokomiPlan.ResetFight();

        Assert.False(KokomiPlan.InMorning(kokomi.Creature));
        Assert.False(KokomiPlan.IsCarryingOut(kokomi.Player));
    }
}
