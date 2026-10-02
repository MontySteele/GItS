using System;
using System.Collections;
using System.Linq;
using System.Reflection;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-281`: the Spark bank as a DEDICATED RESOURCE DISPLAY under the Klee
/// overhaul arm, and as the status-strip badge everywhere else. Since the
/// 2026-09-24 playtest that display is the energy-area counter alone
/// (<c>SparkCounterPinTests</c>); the overhead gauge is gone, and
/// <see cref="Klee_has_no_overhead_spark_gauge"/> pins the absence.
///
/// WHAT IS REAL HERE. Every DECISION the change takes is a pure read off a
/// creature or a power and runs for real: who gets the gauge, what number it
/// draws, whose badge is suppressed, and -- the acceptance condition -- that
/// with the arm off nothing at all moves. The Klee Burst gauge's new predicate
/// is exercised on both sides of the same switch.
///
/// WHAT IS STRUCTURAL, and labelled: the gauge SPEC TABLE is read out of
/// <c>GaugeBridge</c> by reflection rather than drawn (drawing is Godot nodes,
/// which are process death in this host -- README, the headless boundary), and
/// the refresh funnels are pinned as call sets for the same reason: calling
/// <c>SparkPower.Gain</c> needs a live <c>CombatState</c>, and its gauge sync
/// reaches Godot on the far side.
///
/// WHAT IS NOT HERE AT ALL. That the wire still carries the bank cannot be
/// asserted from this assembly -- the bridge is a different mod and the wire is
/// a live game. What CAN be asserted is the property the wire's own filter reads
/// (<c>BuildPowersState</c>: <c>if (!power.IsVisible) continue;</c>), which is
/// that <see cref="SparkPower"/> still takes <c>PowerModel</c>'s visibility and
/// never overrides it. That pin is below and it is the reason the badge is
/// suppressed at the container instead.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class SparkGaugePinTests
{
    private const BindingFlags All = HeadlessGame.All;

    /// <summary>Run <paramref name="body"/> with the arm forced one way, and
    /// put it back. The arm is one process-wide static (see
    /// <see cref="KleeOverhaulArm"/>), which is why this file is in that
    /// collection.</summary>
    private static void WithArm(Action body) => body();

    // --- who gets the gauge ----------------------------------------------

    [Fact]
    public void Klee_gets_the_spark_gauge_under_the_arm_and_nobody_else_ever_does()
    {
        var klee = Seat.Klee();
        var furina = Seat.Furina();
        var kokomi = Seat.Kokomi();

        // The identity half is the marker interface, which is the idiom
        // `tools/lint_prototype_patch_scope.py` requires of a quarantined patch
        // and the one Furina and Kokomi already carry. If it ever comes off the
        // character, the arm's whole scope test silently starts answering false.
        Assert.IsAssignableFrom<IKleeCharacter>(klee.Player.Character);
        Assert.False(furina.Player.Character is IKleeCharacter);
        Assert.False(kokomi.Player.Character is IKleeCharacter);

        WithArm(() =>
        {
            Assert.True(SparkGauge.AppliesTo(klee.Creature));
            // The other two are on the same table in co-op and must not sprout
            // a Klee meter over their heads.
            Assert.False(SparkGauge.AppliesTo(furina.Creature));
            Assert.False(SparkGauge.AppliesTo(kokomi.Creature));
        });

        // THE ACCEPTANCE CONDITION. Off the arm the gauge does not exist, so
        // the shipped display is exactly the shipped display.
    }

    [Fact]
    public void The_gauge_draws_the_bank_and_zero_before_the_first_spark()
    {
        // A resource display shows 0 rather than disappearing -- the Regent's
        // star counter's own posture (`ShouldAlwaysShowStarCounter`), and the
        // reason the read has to answer for a creature carrying no counter yet.
        var empty = Seat.Klee();
        Assert.Equal(0, SparkGauge.Read(empty.Creature));

        var banked = Seat.Klee().WithPower<SparkPower>(4);
        Assert.Equal(4, SparkGauge.Read(banked.Creature));

        // And it is the SAME number the rules read, not a display copy: move
        // the bank the way a spend does and the gauge follows.
        banked.SetPowerAmount<SparkPower>(1);
        Assert.Equal(1, SparkGauge.Read(banked.Creature));
        Assert.Equal(SparkPower.SparksAtPlay(banked.Creature),
                     SparkGauge.Read(banked.Creature));
    }

    // --- whose badge is suppressed ---------------------------------------

    /// <summary>Run <paramref name="body"/> as the seat whose NetId is
    /// <paramref name="me"/> -- `LocalContext.NetId`, the one static the
    /// game's own "is this my screen" reads -- and put it back.</summary>
    private static void AsLocalSeat(ulong me, Action body)
    {
        var was = LocalContext.NetId;
        try
        {
            LocalContext.NetId = me;
            body();
        }
        finally
        {
            LocalContext.NetId = was;
        }
    }

    private static Seat WithNetId(Seat seat, ulong netId)
    {
        Seat.Set(seat.Player, "NetId", netId);
        return seat;
    }

    [Fact]
    public void A_second_seats_spark_badge_is_judged_by_its_own_owner()
    {
        // Co-op. `HidesBadge` asks the POWER's owner, so a Spark counter on a
        // creature that is not a Klee is not this arm's business.
        var furina = WithNetId(Seat.Furina(), 1UL).WithPower<SparkPower>(3);
        var stray = furina.Creature.Powers.OfType<SparkPower>().Single();

        WithArm(() => AsLocalSeat(1UL,
            () => Assert.False(SparkGauge.HidesBadge(stray))));
    }

    [Fact]
    public void A_coop_partner_sees_klees_spark_badge_on_her_creature()
    {
        // CO-OP, 2026-09-26: "a co-op partner cannot see Klee's Spark count".
        // The energy-area counter is drawn for the LOCAL seat only, and the
        // overhead gauge is gone, so the badge is hidden only on Klee's own
        // screen -- where the counter shows the same bank -- and a partner sees
        // it in her power row. Two seats, two screens, one power.
        var klee = WithNetId(Seat.Klee(), 1UL).WithPower<SparkPower>(4);
        var spark = klee.Creature.Powers.OfType<SparkPower>().Single();

        WithArm(() =>
        {
            // Klee's own screen: the counter draws the bank, the badge hides.
            AsLocalSeat(1UL, () => Assert.True(SparkGauge.HidesBadge(spark)));
            // Her partner's screen (seat 2): the badge shows, with its count.
            AsLocalSeat(2UL, () => Assert.False(SparkGauge.HidesBadge(spark)));
        });
        Assert.Equal(4, spark.Amount);
    }

    [Fact]
    public void A_canonical_spark_power_is_asked_without_throwing()
    {
        // `EB-94` from the other side. The prefix runs inside the game's badge
        // container; `PowerModel.Owner`'s getter asserts mutability and THROWS
        // on a canonical model, and a throw there would take the whole status
        // strip with it. An ownerless power simply has no badge to suppress.
        var canonical = new SparkPower();
        WithArm(() => Assert.False(SparkGauge.HidesBadge(canonical)));
    }

    // --- the wire's own precondition -------------------------------------

    [Fact]
    public void The_spark_bank_stays_VISIBLE_to_the_model_so_the_wire_keeps_it()
    {
        // THE REASON THE BADGE IS SUPPRESSED AT THE CONTAINER. The game ships a
        // designed way to hide a power -- `PowerModel.IsVisibleInternal`, which
        // `AmbergrisPower` overrides to false -- and it could not be used here:
        // the understudy bridge's `BuildPowersState` opens with
        // `if (!power.IsVisible) continue;`, so an invisible power leaves the
        // observed board entirely. `understudy/qa_packet.spark_note` finds the
        // bank by the printed name "Spark" in that list and
        // `understudy/adapter.STATUS_FIELDS` maps the same row onto
        // `Player.sparks`; both would have gone silently blind.
        //
        // So this pin is the acceptance condition for the wire half: the bank's
        // visibility is still `PowerModel`'s, inherited and never overridden.
        var declared = typeof(SparkPower)
            .GetProperty("IsVisibleInternal", All)
            ?.GetGetMethod(nonPublic: true)
            ?.DeclaringType;
        Assert.Equal(typeof(PowerModel), declared);

        // And its printed title is still the string the page matches on.
        var title = new SparkPower().Localization!
            .Single(entry => entry.Item1 == "title").Item2;
        Assert.Equal("Spark", title);
    }

    // --- the gauge spec ---------------------------------------------------

    private static object? Prop(object spec, string name) =>
        spec.GetType().GetProperty(name, All)!.GetValue(spec);

    // --- Burst stands down under the arm ---------------------------------

    // --- the refresh funnels ----------------------------------------------

    [Fact]
    public void The_refresh_declines_off_the_arm_and_for_everyone_else()
    {
        // REAL, and it is the one call into the gauge that is safe to make
        // headlessly BECAUSE it declines: every path below returns before
        // `SparkCounter.Refresh`, which would reach Godot nodes. That is also the
        // acceptance condition for the release build -- a shipped Spark gain
        // gains no gauge work.
        var klee = Seat.Klee();
        WithArm(() =>
        {
            SparkGauge.Refresh(Seat.Kokomi().Creature);
            SparkGauge.Refresh(null);
        });
    }
}
