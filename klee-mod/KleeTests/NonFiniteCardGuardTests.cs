using System;
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

    private static bool MayReport(ulong node, long nowMsec) =>
        (bool)Il.Method("NonFiniteCardGuard", "MayReport")
                .Invoke(null, new object[] { node, nowMsec })!;

    private static void ForgetReports() =>
        Il.Method("NonFiniteCardGuard", "ResetForTests").Invoke(null, null);

    private static Vector2 Bezier(Vector2 v0, Vector2 v1, Vector2 c0, float t) =>
        (Vector2)Il.Method("NonFiniteCardGuard", "Bezier")
                   .Invoke(null, new object[] { v0, v1, c0, t })!;

    private static float RecoverT(Vector2 v0, Vector2 v1, Vector2 c0,
                                  Vector2 position) =>
        (float)Il.Method("NonFiniteCardGuard", "RecoverBezierT")
                 .Invoke(null, new object[] { v0, v1, c0, position })!;

    private static Vector2 ControlPoint(Vector2 start, Vector2 end,
                                        float arcDir) =>
        (Vector2)Il.Method("NonFiniteCardGuard", "FlightControlPoint")
                   .Invoke(null, new object[] { start, end, arcDir })!;

    private static float OvershootPerFrame(float speed, float delta,
                                           float duration) =>
        (float)Il.Method("NonFiniteCardGuard", "OvershootPerFrame")
                 .Invoke(null, new object[] { speed, delta, duration })!;

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
        Assert.Contains("NonFiniteCardGuard.Report", calls);
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
        Assert.Contains("NonFiniteCardGuard.Report", calls);
    }

    [Fact]
    public void The_reporter_prints_once_a_second_per_node()
    {
        // THE RATE LIMIT, and why it is per NODE. The recorded session printed
        // the condition every frame; the first pass answered that with a
        // once-per-process latch, which also silenced every LATER catch --
        // including one on a different node, which is exactly the reading the
        // open row wants. A second bucket must not be closed by the first.
        ForgetReports();

        Assert.True(MayReport(node: 7UL, nowMsec: 0L));
        Assert.False(MayReport(node: 7UL, nowMsec: 1L));
        Assert.False(MayReport(node: 7UL, nowMsec: 999L));
        Assert.True(MayReport(node: 7UL, nowMsec: 1000L));

        // A different node is a different bucket, at the same instant.
        Assert.True(MayReport(node: 8UL, nowMsec: 1000L));
        Assert.False(MayReport(node: 8UL, nowMsec: 1500L));
    }

    [Fact]
    public void The_limiter_forgets_rather_than_growing_without_a_bound()
    {
        // Every card play builds a FRESH trail node, so the map's keys are
        // transient: a limiter that only ever inserted would be a slow leak in
        // the file whose whole subject is an unbounded allocation.
        ForgetReports();
        for (var node = 0UL; node < 200UL; node++)
        {
            Assert.True(MayReport(node, nowMsec: 0L));
        }

        // The cost of forgetting is one extra line, never a missed catch.
        Assert.True(MayReport(node: 0UL, nowMsec: 10L));
    }

    [Fact]
    public void One_frames_overshoot_is_the_flights_own_arithmetic()
    {
        // `PlayAnim` advances `time += _speed * GetProcessDeltaTime()` and
        // evaluates the curve at `time / _duration`, so ONE frame moves t by
        // this much. The two numbers below are the row's whole question: an
        // ordinary frame is a fiftieth of the curve, and a stalled one is
        // hundreds of curves.
        Assert.Equal(0.0128f, OvershootPerFrame(1.2f, 0.016f, 1.5f), 4);

        // 20 minutes of stalled frame at TimeScale 3, which is the shape the
        // recorded 1e9 magnitude needs.
        Assert.True(OvershootPerFrame(1.2f, 3600f, 1.5f) > 2800f);

        // A duration of zero cannot happen (`_duration` is drawn from
        // [1, 1.75]) and must not divide anyway.
        Assert.True(float.IsNaN(OvershootPerFrame(1.2f, 0.016f, 0f)));
    }

    [Fact]
    public void The_control_point_is_the_flights_own()
    {
        // `PlayAnim` spells it `c = _startPos + (_endPos - _startPos) * 0.5f;
        // c.Y -= _arcDir;`. If this drifts, every recovered t below is a
        // number about a curve the game never drew.
        var control = ControlPoint(new Vector2(100f, 900f),
                                   new Vector2(1500f, 300f),
                                   arcDir: -500f);

        Assert.Equal(800f, control.X, 3);
        Assert.Equal(1100f, control.Y, 3);
    }

    [Fact]
    public void The_curves_t_is_recovered_from_the_position_it_produced()
    {
        // THE HYPOTHESIS'S OWN NUMBER. `time` is a local of an async method
        // and unreachable from the trail, so the log recovers t by inverting
        // the quadratic. Round-tripping it is what makes the recovered number
        // evidence: mid-flight, at the endpoint, one frame past it, and out at
        // the magnitude the live catch recorded.
        var start = new Vector2(100f, 900f);
        var end = new Vector2(1500f, 300f);
        var control = ControlPoint(start, end, arcDir: -500f);

        foreach (var t in new[] { 0.25f, 0.75f, 1f, 1.02f, 8f, 2900f })
        {
            var position = Bezier(start, end, control, t);
            var recovered = RecoverT(start, end, control, position);
            Assert.True(Math.Abs(recovered - t) <= 1e-3f * Math.Abs(t) + 1e-3f,
                        $"t={t} recovered as {recovered}");
        }
    }

    [Fact]
    public void The_recovered_t_reaches_the_magnitude_the_live_catch_recorded()
    {
        // The row's arithmetic, end to end: a t in the thousands puts the card
        // at ~1e9 px, which is the order of the position the first live catch
        // printed (-8.8e9, -4.9e8). If this ever stops holding, the hypothesis
        // in the row's own text is wrong about the mechanism and not just the
        // trigger.
        var start = new Vector2(960f, 540f);
        var end = new Vector2(1500f, 200f);
        var control = ControlPoint(start, end, arcDir: 900f);

        var position = Bezier(start, end, control, 2900f);

        Assert.True(position.Length() > 1e8f, $"|pos|={position.Length()}");
        Assert.Equal(2900f, RecoverT(start, end, control, position), 0);
    }

    [Fact]
    public void A_position_that_is_not_on_the_curve_recovers_no_t()
    {
        // Solving ONE axis always yields some t, so the answer is checked
        // against the curve before it is returned. Without that, a card moved
        // by something OTHER than its flight would still be reported with a
        // confident t, and the log would confirm the hypothesis it exists to
        // test.
        var start = new Vector2(100f, 900f);
        var end = new Vector2(1500f, 300f);
        var control = ControlPoint(start, end, arcDir: -500f);

        Assert.True(float.IsNaN(
            RecoverT(start, end, control, new Vector2(800f, -40_000f))));
        Assert.True(float.IsNaN(
            RecoverT(start, end, control,
                     new Vector2(float.PositiveInfinity, 0f))));
    }
}
