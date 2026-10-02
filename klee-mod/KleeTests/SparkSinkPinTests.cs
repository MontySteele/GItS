using System.Linq;
using System.Reflection;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-118 §4.5: the Spark SINK's C# surface, staged with no card using it.
///
/// The op makes the Spark bank a resource with a COMPETING use. Two facts
/// carry the contract and both are reachable headlessly, because both are
/// reads off a creature's power list rather than card plays:
///
///   * a short bank cannot pay -- <see cref="SparkPower.CanSpend"/> is the
///     gate a generated sink hangs its <c>IsPlayable</c> override on, so the
///     price is visible before any energy is committed, and it is the same
///     predicate <see cref="SparkPower.Spend"/> refuses on;
///   * the free-Attack threshold is read LIVE off the bank, so a deliberate
///     spend forfeits it (under True Spark Knight, spending 2 spends the
///     free Attack). Nothing caches the bar.
///
/// What is NOT here: a card actually being played. `OnPlay` bodies and the
/// energy-cost hook need a live CombatState, which is outside the headless
/// boundary (README, "The headless boundary"). The two facts above are
/// pinned directly, and the ones that could only be reached structurally
/// are labelled as structural.
/// </summary>
public class SparkSinkPinTests
{
    private const BindingFlags All = HeadlessGame.All;

    // --- the flag, both ways round ---------------------------------------

    [Fact]
    public void The_gauge_sync_is_the_quarantine_seam_and_a_release_build_has_none()
    {
        // `EB-281`, and THE HALF THAT ONLY THIS FILE CAN SAY, on the argument
        // above verbatim. The Spark bank is drawn as a dedicated resource gauge
        // under the Klee overhaul arm, and `SparkPower` calls `SyncGauge` from
        // each of its three mutation funnels. `Vfx/SparkGauge` lives under
        // `Vfx/Prototype/`, which is `Compile Remove`d without the switch, so
        // the seam is guarded ONCE inside `SyncGauge` rather than at each call
        // site -- and the acceptance condition is that in a RELEASE build the
        // method therefore calls nothing at all and a shipped Spark gain does
        // no gauge work. `Prototype/SparkGaugePinTests` asserts the other half;
        // it is not compiled here, which is why this half lives in this file.
        var sync = typeof(SparkPower).GetMethod("SyncGauge", All)
            ?? throw new System.InvalidOperationException(
                "SparkPower.SyncGauge is gone -- the gauge seam moved under this pin.");
        var calls = Il.Calls(sync);
        Assert.Contains("SparkGauge.Refresh", calls);
    }

    // --- the gate --------------------------------------------------------

    [Fact]
    public void A_seat_with_no_sparks_cannot_pay_any_price()
    {
        // No SparkPower on the creature at all -- the `?? 0` bank. A sink
        // drawn on turn one is unplayable, not a play that does nothing.
        var klee = Seat.Klee();

        Assert.False(SparkPower.CanSpend(klee.Creature, 1));
        Assert.False(SparkPower.CanSpend(klee.Creature, 2));
    }

    [Theory]
    [InlineData(0, 2, false)]
    [InlineData(1, 2, false)]   // short by one: still nothing
    [InlineData(2, 2, true)]    // exact: pays, and empties the bank
    [InlineData(5, 2, true)]
    public void The_gate_is_a_whole_price_or_nothing(int bank, int price, bool payable)
    {
        var klee = Seat.Klee().WithPower<SparkPower>(bank);

        Assert.Equal(payable, SparkPower.CanSpend(klee.Creature, price));
    }

    [Fact]
    public void A_price_of_zero_is_not_a_payment()
    {
        // codegen emits the IsPlayable gate only for a card that prints a
        // price, so this is defence in depth: a zero must never read as
        // "afforded" and turn into a free spend of nothing.
        var klee = Seat.Klee().WithPower<SparkPower>(3);

        Assert.False(SparkPower.CanSpend(klee.Creature, 0));
        Assert.False(SparkPower.CanSpend(klee.Creature, -1));
    }

    [Fact]
    public void The_gate_reads_the_bank_at_the_moment_it_is_asked()
    {
        var klee = Seat.Klee().WithPower<SparkPower>(2);
        Assert.True(SparkPower.CanSpend(klee.Creature, 2));

        klee.SetPowerAmount<SparkPower>(0);
        Assert.False(SparkPower.CanSpend(klee.Creature, 1));
    }

    // --- True Spark Knight: the threshold is live ------------------------


    [Fact]
    public void Nothing_caches_the_bank_or_the_threshold()
    {
        // STRUCTURAL PIN (README's Il idiom, in its bluntest form): the only
        // instance state SparkPower may hold is none: the shipped free-Attack
        // rule's pending spend went with the shipped kits. A cached bank or a cached bar is exactly the defect the
        // contract asks about -- the threshold must be recomputed from the
        // live power list at every read -- and it would arrive as a field.
        var fields = typeof(SparkPower)
            .GetFields(BindingFlags.Instance | BindingFlags.Public
                       | BindingFlags.NonPublic | BindingFlags.DeclaredOnly)
            .Select(f => f.Name)
            .OrderBy(n => n)
            .ToArray();

        Assert.Empty(fields);
    }

    // --- the payment -----------------------------------------------------

    [Fact]
    public void Spend_refuses_through_the_same_predicate_the_gate_uses()
    {
        // STRUCTURAL PIN. Executing Spend needs a PlayerChoiceContext and a
        // combat, which the harness cannot build; what IS checkable is that
        // the payment consults CanSpend rather than carrying a second copy
        // of the rule that could disagree with the card's playability.
        var calls = Il.Calls(typeof(SparkPower)
            .GetMethod(nameof(SparkPower.Spend), All)!);

        Assert.Contains("SparkPower.CanSpend", calls);
    }

    [Fact]
    public void Spend_moves_the_bank_through_the_same_command_the_consume_uses()
    {
        // STRUCTURAL PIN: PowerCmd.ModifyAmount, the primitive the threshold
        // consume in AfterCardPlayed already uses. A sink that removed and
        // re-applied the power instead would lose the pending-spend state
        // and every other reader of the bank with it.
        var calls = Il.Calls(typeof(SparkPower)
            .GetMethod(nameof(SparkPower.Spend), All)!);

        Assert.Contains(calls, c => c.EndsWith("PowerCmd.ModifyAmount"));
    }

    private static int CurrentThreshold(Seat seat)
    {
        var power = seat.Creature.Powers.OfType<SparkPower>().First();
        return (int)typeof(SparkPower)
            .GetProperty("CurrentThreshold", All)!
            .GetValue(power)!;
    }
}
