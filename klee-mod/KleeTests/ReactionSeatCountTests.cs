using System;
using System.Collections;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using MegaCrit.Sts2.Core.Combat;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-156`: a two-seat telemetry row reports its OWN seat's reactions.
///
/// THE DEFECT, AND WHAT IT WAS NOT. `PlayTelemetry.OpenTurn` sampled
/// `ReactionEffects.TotalResolved` into each seat's per-fight row. That
/// counter is GLOBAL on purpose and it is a SEALED RULING (red-pen
/// 2026-07-26 R1): in co-op your partner's Overload satisfies your Chevreuse,
/// because a Reaction is a fact about the board both players stand on. So the
/// counter is not the bug -- putting it in a PER-SEAT row is. Both seats'
/// reactions landed in every seat's row and a reader dividing by that seat's
/// turns, cards or damage used the wrong denominator.
///
/// THE FIX is the pattern already pinned next door: a second counter keyed by
/// `Player` and cleared when the combat instance changes, exactly like
/// `BombPower.DetonationsThisCombat` (`BombInstancingTests` covers that one).
///
/// THE BOUNDARY. `ReactionEffects.Resolve` is an async game path that needs a
/// live `PlayerChoiceContext`, so it cannot run here (README). What CAN run is
/// the counter's own keying, which is the whole of the divergence: the record
/// site is invoked directly, and the read is the shipped public one.
/// </summary>
public class ReactionSeatCountTests
{
    private static readonly Type Reactions = typeof(BombPower).Assembly
        .GetTypes().First(t => t.Name == "ReactionEffects");

    private static void Record(object combat, Seat seat)
        => Reactions.GetMethod("RecordResolved", HeadlessGame.All)!
                    .Invoke(null, new[] { combat, (object)seat.Creature });

    private static int Mine(object combat, Seat seat)
        => (int)Reactions.GetMethod("ResolvedThisCombat", HeadlessGame.All)!
                         .Invoke(null, new[] { combat, (object)seat.Player })!;

    /// <summary>A real `CombatState`, allocated uninitialised -- the same
    /// move `BombDeathTeardownTests` makes for the counter next door. The
    /// counter only ever compares it by REFERENCE (`ReferenceEquals`), which
    /// is the whole of its contract.</summary>
    private static object Combat() =>
        RuntimeHelpers.GetUninitializedObject(typeof(CombatState));

    [Fact]
    public void A_two_seat_row_reports_its_own_seat_s_reactions()
    {
        // THE ACCEPTANCE. Seat A causes three reactions, seat B one.
        var combat = Combat();
        var a = Seat.Klee();
        var b = Seat.Furina();

        Record(combat, a);
        Record(combat, a);
        Record(combat, a);
        Record(combat, b);

        Assert.Equal(3, Mine(combat, a));
        Assert.Equal(1, Mine(combat, b));
    }

    [Fact]
    public void The_old_reading_would_have_given_both_seats_four()
    {
        // SEEN TO FAIL, stated as the defect: the team-wide number the row
        // used to carry is the SUM, and it is the same for both seats.
        var combat = Combat();
        var a = Seat.Klee();
        var b = Seat.Furina();

        Record(combat, a);
        Record(combat, a);
        Record(combat, a);
        Record(combat, b);

        Assert.NotEqual(Mine(combat, a) + Mine(combat, b), Mine(combat, a));
        Assert.NotEqual(Mine(combat, a) + Mine(combat, b), Mine(combat, b));
    }

    [Fact]
    public void A_new_combat_resets_the_count()
    {
        var first = Combat();
        var seat = Seat.Klee();
        Record(first, seat);
        Assert.Equal(1, Mine(first, seat));

        var second = Combat();
        Record(second, seat);

        Assert.Equal(1, Mine(second, seat));
        // And the stale combat reads zero rather than a number from the last
        // fight -- the reason the read takes the combat as well as the seat.
        Assert.Equal(0, Mine(first, seat));
    }

    [Fact]
    public void A_dealer_less_reaction_belongs_to_no_seat()
    {
        // The named consequence: a corpse detonation or an orphaned
        // application increments the GLOBAL counter and no seat's, so the
        // seats sum to at most the team-wide number. Recorded here so the
        // asymmetry is a pinned fact rather than a surprise to a reader.
        var combat = Combat();
        var seat = Seat.Klee();

        Reactions.GetMethod("RecordResolved", HeadlessGame.All)!
                 .Invoke(null, new object?[] { combat, null });

        Assert.Equal(0, Mine(combat, seat));
    }

    [Fact]
    public void The_global_counter_is_untouched_and_still_global()
    {
        // The sealed half. Nothing above may narrow TotalResolved: it is the
        // board-wide fact Chevreuse and Boom Goes the Dynamite read.
        var total = Reactions.GetProperty("TotalResolved", HeadlessGame.All)!;

        Assert.Equal(typeof(int), total.PropertyType);
        Assert.True(total.GetGetMethod(nonPublic: true)!.IsStatic);
        Assert.Empty(total.GetIndexParameters());
    }

    [Fact]
    public void The_telemetry_row_reads_the_per_seat_counter_and_not_the_global()
    {
        // The call site, structurally: OpenTurn writes the per-seat row.
        var openTurn = typeof(BombPower).Assembly.GetTypes()
            .First(t => t.Name == "PlayTelemetry")
            .GetMethod("OpenTurn", HeadlessGame.All)!;

        var calls = Il.Calls(openTurn);

        Assert.Contains(calls, c => c.EndsWith("ResolvedThisCombat", StringComparison.Ordinal));
        Assert.DoesNotContain(calls, c => c.EndsWith("get_TotalResolved", StringComparison.Ordinal));
    }
}
