using Godot;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-292, pinned: the arithmetic that decides whether the card trail is asked
/// for bounded work.
///
/// THE HANG IS ARITHMETIC, WHICH IS WHY IT IS TESTABLE HERE. Nothing in the
/// scene can be built in this host (README, the headless boundary) -- but the
/// question the guard answers is not about nodes: `NCardTrail.CreatePoint`
/// walks the gap between two positions at a fixed 48 px spacing, so "is this
/// pair of positions drawable" is a pure predicate over two `Vector2`s and the
/// difference between a frame of missing trail and a 41 GB process is entirely
/// inside it.
///
/// BOTH FAILURE SHAPES ARE PINNED, and they are NOT the same bug. An INFINITE
/// position makes the loop's bound infinite and it never terminates -- that is
/// the out-of-memory. A NaN position terminates immediately (every comparison
/// against NaN is false) but poisons the `Line2D`'s width-curve offsets, which
/// is the `sample_baked` error the recorded session printed 286 times. A guard
/// that caught only one of them would leave half the session's log in place.
/// </summary>
public class NonFiniteCardGuardTests
{
    private static bool IsFinite(Vector2 v) =>
        (bool)Il.Method("NonFiniteCardGuard", "IsFinite")
                .Invoke(null, new object[] { v })!;

    private static bool IsDrawable(Vector2 from, Vector2 to) =>
        (bool)Il.Method("NonFiniteCardGuard", "IsDrawableTravel")
                .Invoke(null, new object[] { from, to })!;

    [Fact]
    public void An_ordinary_card_position_is_finite()
    {
        // The no-op case, and it is the one that matters most: every card play
        // in the game goes through this predicate, so a guard that answered
        // `false` here would delete the trail for everybody.
        Assert.True(IsFinite(new Vector2(960f, 540f)));
        Assert.True(IsFinite(Vector2.Zero));
        Assert.True(IsFinite(new Vector2(-1920f, 2160f)));
    }

    [Fact]
    public void Neither_nan_nor_either_infinity_is_finite()
    {
        // `float.IsFinite` is false for all five, and the guard needs all five:
        // the recorded log carries a NaN shape (`sample_baked`) and an infinite
        // shape (the unbounded loop) in the same session.
        Assert.False(IsFinite(new Vector2(float.NaN, 0f)));
        Assert.False(IsFinite(new Vector2(0f, float.NaN)));
        Assert.False(IsFinite(new Vector2(float.PositiveInfinity, 0f)));
        Assert.False(IsFinite(new Vector2(0f, float.NegativeInfinity)));
        Assert.False(IsFinite(new Vector2(float.NaN, float.PositiveInfinity)));
    }

    [Fact]
    public void A_normal_frames_travel_is_drawable()
    {
        // A card crossing the whole design resolution in one frame is still
        // 40 points of gap-filling, which is what the loop is for.
        Assert.True(IsDrawable(Vector2.Zero, new Vector2(1920f, 1080f)));
        Assert.True(IsDrawable(new Vector2(100f, 100f), new Vector2(112f, 100f)));
    }

    [Fact]
    public void An_infinite_destination_is_refused_because_the_loop_never_ends()
    {
        // THE HANG, in one line. `for (d = 48; d < distance - 12; d += 48)`
        // with an infinite `distance` is an infinite loop that appends a point
        // and a float per iteration. This is the assertion that fails on a
        // build with the guard removed.
        Assert.False(IsDrawable(Vector2.Zero,
                                new Vector2(float.PositiveInfinity, 0f)));
        Assert.False(IsDrawable(new Vector2(float.NegativeInfinity, 0f),
                                Vector2.Zero));
    }

    [Fact]
    public void A_nan_destination_is_refused_even_though_it_would_not_hang()
    {
        // It terminates and still has to be refused: a NaN point makes the
        // Line2D's total length NaN, and the width curve is then sampled at a
        // non-finite offset once per point per frame for as long as the trail
        // lives.
        Assert.False(IsDrawable(Vector2.Zero, new Vector2(float.NaN, 0f)));
    }

    [Fact]
    public void An_enormous_but_finite_travel_is_refused_too()
    {
        // The second bound, and it is not redundant: a transform inverted
        // through a zero scale lands on a number that is finite, passes every
        // check above, and still asks the loop for distance/48 points. 1e12 px
        // is ~2e10 iterations -- not infinite, and not survivable either.
        Assert.False(IsDrawable(Vector2.Zero, new Vector2(1e12f, 0f)));

        // ...and the bound is above anything a real play produces, so the
        // clamp cannot bite a legitimate flight.
        Assert.True(IsDrawable(Vector2.Zero, new Vector2(50_000f, 0f)));
    }

    [Fact]
    public void The_trail_prefix_asks_this_predicate_and_no_other()
    {
        // The structural half: the patch that stands between the engine and
        // the unbounded loop must be reading the predicate above, not a copy
        // of it. A second spelling is how the pin and the ship drift apart.
        var calls = Il.Calls(
            Il.Method("NCardTrail_CreatePoint_NonFiniteGuard_Patch", "Prefix"));

        Assert.Contains("NonFiniteCardGuard.IsFinite", calls);
        Assert.Contains("NonFiniteCardGuard.ReportOnce", calls);
    }

    [Fact]
    public void The_trail_prefix_bounds_the_travel_and_not_only_the_point()
    {
        // Both halves, or the second bound is a predicate nothing asks. The
        // enormous-but-finite position passes `IsFinite` and still hangs, so
        // the prefix has to read the trail's own last point and put the pair
        // through `IsDrawableTravel`.
        var calls = Il.Calls(
            Il.Method("NCardTrail_CreatePoint_NonFiniteGuard_Patch", "Prefix"));

        Assert.Contains("NonFiniteCardGuard.IsDrawableTravel", calls);
    }

    [Fact]
    public void The_flight_destination_postfix_falls_back_to_the_games_own_nowhere()
    {
        // `Vector2.Zero` is not invented: `PileTypeExtensions.GetTargetPosition`
        // already returns it for a combat pile outside combat, so a caller that
        // gets it is getting a value the method's own vocabulary contains.
        var calls = Il.Calls(
            Il.Method("PileType_GetTargetPosition_NonFiniteGuard_Patch",
                      "Postfix"));

        Assert.Contains("NonFiniteCardGuard.IsFinite", calls);
        Assert.Contains("NonFiniteCardGuard.ReportOnce", calls);
    }
}
