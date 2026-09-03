using System;
using System.Collections;
using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Entities.Creatures;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE FURINA REFRAME, R251 / <c>EB-365</c> -- the SHIPPED Burst meter retires
/// under the arm, and only under the arm.
///
/// The pick is <c>review/ruled/furina-reframe-round-1-2026-09-04.md</c> §6
/// pick 1, option (1). The round-one seat's meter read <c>78/70</c>, over its
/// own cap, and <i>Let the People Rejoice</i> arrived off that overflow to take
/// the boss from 28 to 14 -- so the run's clutch turn was the shipped kit's and
/// not the reframe's. R220 B had sequenced the Burst fold last; the new fact is
/// that the shipped meter sits inside every Furina read until it goes.
///
/// ARM-ONLY. The shared retirement (<c>EB-199</c>, <c>EB-200</c>) still owns
/// the shipped engines, so every pin below comes in a pair: the same board with
/// the leg on and with it off, and the OFF half is the only assertion that can
/// catch the leg leaking into the engine that is being played tonight.
///
/// The sim's twin is <c>tier0/tests/test_furina_reframe_burst.py</c>, in the
/// same order.
/// </summary>
public class FurinaReframeBurstTests
{
    /// <summary>
    /// Turn the retirement on for the length of one test and put every flag
    /// back after it, whatever it does. All six are saved: the seams that read
    /// them are static, so a fixture that restored five would arm the next
    /// test.
    /// </summary>
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;
        private readonly bool _evoke = FurinaReframe.EvokeEnabled;
        private readonly bool _meter = FurinaReframe.MeterEnabled;
        private readonly bool _spotlight = FurinaReframe.SpotlightEnabled;
        private readonly bool _burst = FurinaReframe.BurstEnabled;

        internal Arm(bool burst = true, bool master = true)
        {
            FurinaReframe.Enabled = master;
            FurinaReframe.ManualEnabled = false;
            FurinaReframe.EvokeEnabled = false;
            FurinaReframe.MeterEnabled = false;
            FurinaReframe.SpotlightEnabled = false;
            FurinaReframe.BurstEnabled = burst;
        }

        public void Dispose()
        {
            FurinaReframe.Enabled = _enabled;
            FurinaReframe.ManualEnabled = _manual;
            FurinaReframe.EvokeEnabled = _evoke;
            FurinaReframe.MeterEnabled = _meter;
            FurinaReframe.SpotlightEnabled = _spotlight;
            FurinaReframe.BurstEnabled = _burst;
        }
    }

    // ==================================================================
    // 1. THE FEED -- nothing fills the meter under the arm
    // ==================================================================

    [Fact]
    public void The_meter_fills_with_the_flag_off()
    {
        var seat = Seat.Furina().WithCombatState();

        FurinaResources.GainBurst(seat.Creature, 5);

        Assert.Equal(5, FurinaResources.Burst(seat.Creature));
    }

    [Fact]
    public void Nothing_feeds_the_meter_under_the_arm()
    {
        // Klee's `EB-266` and Kokomi's `EB-327` one character over, fixed at
        // the same place: the funnel every source lands in -- the skill-tag
        // particle, the Salon tick, the Encore-spend particle and the reaction
        // credit -- because the arm's answer is "she has no Burst meter" and
        // not "reactions in particular do not feed it".
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();

        FurinaResources.GainBurst(seat.Creature, 5);
        FurinaResources.GainBurst(seat.Creature, FurinaResourceConstants.BurstMax);

        Assert.Equal(0, FurinaResources.Burst(seat.Creature));
    }

    [Fact]
    public void The_reaction_funnel_is_the_one_that_was_missed_elsewhere()
    {
        // STRUCTURAL, and it is the pin `EB-327` wished it had had: the
        // reaction credit reaches Furina's meter through the shared funnel, so
        // the guard inside `GainBurst` covers it without a second branch at the
        // call site. If somebody ever moves the reaction credit off the funnel,
        // this fails rather than the arm quietly filling again.
        Assert.Contains("FurinaResources.GainBurst",
                        Il.Calls(Il.Method("ReactionEffects", "Resolve")));
        Assert.Contains("FurinaReframe.BurstRetiredFor",
                        Il.Calls(Il.Method("FurinaResources", "GainBurst")));
    }

    [Fact]
    public void The_other_two_arms_keep_their_own_guards()
    {
        // The Furina guard is an ADDITIONAL early return at Furina's own
        // funnel, not a replacement: in co-op the other seat may be Kokomi,
        // whose meter this flag has no business touching.
        using var _ = new Arm();
        var kokomi = Seat.Kokomi().WithCombatState();

        KokomiResources.GainBurst(kokomi.Creature, 5);

        Assert.Equal(5, KokomiResources.GetBurst(kokomi.Creature));
    }

    // ==================================================================
    // 2. THE DRAW -- the overhead ribbon stands down
    // ==================================================================

    [Fact]
    public void The_gauge_applies_with_the_flag_off()
    {
        Assert.True(FurinaResources.BurstGaugeApplies(Seat.Furina().Creature));
    }

    [Fact]
    public void The_gauge_does_not_apply_under_the_arm()
    {
        // `EB-281`'s and `EB-297`'s fact one character further over: a spec
        // that still APPLIED would draw an overhead ribbon pinned at 0/70 for
        // the whole run.
        using var _ = new Arm();

        Assert.False(FurinaResources.BurstGaugeApplies(Seat.Furina().Creature));
        // Everyone else's gauge is unchanged; this asks only Furina's question.
        Assert.False(FurinaResources.BurstGaugeApplies(Seat.Kokomi().Creature));
    }

    [Fact]
    public void The_bridge_spec_reads_the_guard_and_not_a_bare_character_test()
    {
        // STRUCTURAL by necessity -- the alternative is drawing a gauge, which
        // is Godot. `GaugeSpec` is a private nested type and `Specs` a private
        // array, so the spec is read the way `SparkGaugePinTests` reads one and
        // its `AppliesTo` predicate is CALLED. The guard lives beside the
        // resource, as Klee's and Kokomi's do, so "who has this meter" is one
        // question with one answer instead of two that can drift.
        var applies = (Func<Creature, bool>)Prop(Spec("furina_burst"), "AppliesTo")!;
        var furina = Seat.Furina().Creature;

        Assert.True(applies(furina));
        using var _ = new Arm();
        Assert.False(applies(furina));
    }

    /// <summary>The `GaugeBridge` spec table, by reflection: `GaugeSpec` is a
    /// private nested type and the array is private.
    /// `SparkGaugePinTests.Spec`'s reasoning, verbatim.</summary>
    private static object Spec(string key) =>
        ((IEnumerable)typeof(GaugeBridge).GetField("Specs", HeadlessGame.All)!
            .GetValue(null)!)
        .Cast<object>()
        .Single(s => (string)s.GetType()
            .GetProperty("Key", HeadlessGame.All)!.GetValue(s)! == key);

    private static object? Prop(object spec, string name) =>
        spec.GetType().GetProperty(name, HeadlessGame.All)!.GetValue(spec);

    // ==================================================================
    // 3. THE GRANT -- Let the People Rejoice is never handed over
    // ==================================================================

    [Fact]
    public void The_kit_grant_reads_the_guard()
    {
        // Unreachable in play -- nothing fills the meter under the arm -- and
        // written anyway, because "Let the People Rejoice is not part of the
        // reframe" is a rule of the arm rather than a consequence of one guard
        // sitting upstream. STRUCTURAL: the grant itself needs a live combat.
        Assert.Contains("FurinaReframe.BurstRetiredFor",
                        Il.Calls(Il.Method("FurinaKitGrant", "GrantIfCharged")));
    }
}
