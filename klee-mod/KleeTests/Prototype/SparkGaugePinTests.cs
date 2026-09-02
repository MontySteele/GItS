using System;
using System.Collections;
using System.Linq;
using System.Reflection;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-281`: the Spark bank as a DEDICATED RESOURCE DISPLAY under the Klee
/// overhaul arm, and as the status-strip badge everywhere else.
///
/// WHAT IS REAL HERE. Every DECISION the change takes is a pure read off a
/// creature or a power and runs for real: who gets the gauge, what number it
/// draws, whose badge is suppressed, and -- the acceptance condition -- that
/// with the arm off nothing at all moves. The Klee Burst gauge's new predicate
/// is exercised on both sides of the same switch.
///
/// WHAT IS STRUCTURAL, and labelled: the gauge's own SPEC is read out of
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
    private static void WithArm(bool enabled, Action body)
    {
        var was = KleeOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = enabled;
            body();
        }
        finally
        {
            KleeOverhaul.Enabled = was;
        }
    }

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

        WithArm(true, () =>
        {
            Assert.True(SparkGauge.AppliesTo(klee.Creature));
            // The other two are on the same table in co-op and must not sprout
            // a Klee meter over their heads.
            Assert.False(SparkGauge.AppliesTo(furina.Creature));
            Assert.False(SparkGauge.AppliesTo(kokomi.Creature));
        });

        // THE ACCEPTANCE CONDITION. Off the arm the gauge does not exist, so
        // the shipped display is exactly the shipped display.
        WithArm(false, () =>
        {
            Assert.False(SparkGauge.AppliesTo(klee.Creature));
            Assert.False(SparkGauge.AppliesTo(furina.Creature));
            Assert.False(SparkGauge.AppliesTo(kokomi.Creature));
        });
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

    [Fact]
    public void The_arm_hides_the_spark_badge_and_leaves_every_other_badge_alone()
    {
        var klee = Seat.Klee().WithPower<SparkPower>(2)
                              .WithPower<SparkThresholdDownPower>(1)
                              .WithPower<BombPower>(3);
        var spark = klee.Creature.Powers.OfType<SparkPower>().Single();

        WithArm(true, () =>
        {
            Assert.True(SparkGauge.HidesBadge(spark));

            // Klee's STATUSES keep their badges. The finding was about a
            // RESOURCE sitting among the statuses, not about the strip.
            foreach (var other in klee.Creature.Powers.Where(p => p != spark))
            {
                Assert.False(SparkGauge.HidesBadge(other));
            }
        });

        // THE MUTATION GUARD, and the acceptance condition again: off the arm
        // the very same power on the very same seat keeps its badge.
        WithArm(false, () => Assert.False(SparkGauge.HidesBadge(spark)));
    }

    [Fact]
    public void A_second_seats_spark_badge_is_judged_by_its_own_owner()
    {
        // Co-op. `HidesBadge` asks the POWER's owner, so a Spark counter on a
        // creature that is not a Klee is not this arm's business -- and a Klee's
        // is hidden on both screens, because the gauge replacing it is drawn on
        // her creature and both seats see it.
        var furina = Seat.Furina().WithPower<SparkPower>(3);
        var stray = furina.Creature.Powers.OfType<SparkPower>().Single();

        WithArm(true, () => Assert.False(SparkGauge.HidesBadge(stray)));
    }

    [Fact]
    public void A_canonical_spark_power_is_asked_without_throwing()
    {
        // `EB-94` from the other side. The prefix runs inside the game's badge
        // container; `PowerModel.Owner`'s getter asserts mutability and THROWS
        // on a canonical model, and a throw there would take the whole status
        // strip with it. An ownerless power simply has no badge to suppress.
        var canonical = new SparkPower();
        WithArm(true, () => Assert.False(SparkGauge.HidesBadge(canonical)));
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

    /// <summary>The `GaugeBridge` spec table, by reflection: `GaugeSpec` is a
    /// private nested type and the array is private. STRUCTURAL by necessity --
    /// the alternative is drawing one, which is Godot.</summary>
    private static object Spec(string key) =>
        ((IEnumerable)typeof(GaugeBridge).GetField("Specs", All)!.GetValue(null)!)
        .Cast<object>()
        .Single(s => (string)s.GetType().GetProperty("Key", All)!.GetValue(s)! == key);

    private static object? Prop(object spec, string name) =>
        spec.GetType().GetProperty(name, All)!.GetValue(spec);

    [Fact]
    public void The_spark_spec_is_a_bar_less_counter_with_the_spark_glyph()
    {
        var spark = Spec("klee_spark");

        // BAR-LESS. Sparks are uncapped, so there is no honest span to draw;
        // `GaugeBridge.RefreshDisplay` hides the track and the fill on a null
        // span and the label falls back to the bare count. Same shape as
        // Kokomi's Charge, and the same shape as the Regent's star counter.
        Assert.Null(Prop(spark, "VisualSpan"));
        Assert.Null(Prop(spark, "LabelMax"));

        // A GLYPH, which is the half a bare counter does not have. It is Klee's
        // own Spark icon -- the one the suppressed badge wore and the one the
        // meter cost badge paints on a priced card -- so the resource looks the
        // same everywhere it appears.
        var skin = Prop(spark, "Skin")!;
        Assert.Equal(SparkGauge.GlyphPath,
                     skin.GetType().GetProperty("CapIconPath", All)!.GetValue(skin));
        Assert.Equal("klee/powers/spark.png", SparkGauge.GlyphPath);

        // No flash: the shared scene's flash overlay is bar-shaped, and a bar
        // that is not drawn must not strobe.
        var flash = (Func<int, int, bool>)Prop(spark, "ShouldFlash")!;
        Assert.False(flash(0, 1));
        Assert.False(flash(3, 0));
    }

    [Fact]
    public void The_spark_gauge_reads_and_gates_through_SparkGauge()
    {
        // The spec must not carry its own copy of either decision: the number
        // it draws is the bank the rules charge, and the creature it draws on
        // is the arm's own predicate.
        var spark = Spec("klee_spark");

        var applies = (Func<Creature, bool>)Prop(spark, "AppliesTo")!;
        Assert.Equal(typeof(SparkGauge), applies.Method.DeclaringType);
        Assert.Equal(nameof(SparkGauge.AppliesTo), applies.Method.Name);

        var read = (Func<Creature, int>)Prop(spark, "ReadValue")!;
        Assert.Equal(typeof(SparkGauge), read.Method.DeclaringType);
        Assert.Equal(nameof(SparkGauge.Read), read.Method.Name);
    }

    [Fact]
    public void The_spark_gauge_takes_the_overhead_slot_the_arm_frees()
    {
        // The overhead slot is the C1 convention for "this creature's primary
        // meter" and has meant Burst for everybody because Burst was
        // everybody's. Under this arm Klee has none, so her one meter goes
        // where the eye already looks rather than into the second row above it.
        var overhead = typeof(GaugeBridge)
            .GetField("OverheadBurstAnchor", All)!.GetValue(null);
        var secondRow = typeof(GaugeBridge)
            .GetField("SecondRowAnchor", All)!.GetValue(null);

        Assert.Equal(overhead, Prop(Spec("klee_spark"), "AnchorOffset"));
        Assert.Equal(overhead, Prop(Spec("burst"), "AnchorOffset"));
        Assert.NotEqual(secondRow, Prop(Spec("klee_spark"), "AnchorOffset"));
    }

    // --- Burst stands down under the arm ---------------------------------

    [Fact]
    public void The_burst_gauge_stands_down_for_klee_under_the_arm()
    {
        // `EB-266`'s DISPLAY half. Nothing feeds Klee's Burst under the arm
        // (`KleeBurstResource.Find` returns null), but the gauge's predicate was
        // a bare `is Klee`, so the bar built itself anyway and sat at 0/40 with
        // a bomb on the end of it for the whole run -- the same "no idea what it
        // was" the meter itself earned.
        var klee = Seat.Klee();

        WithArm(true, () =>
        {
            Assert.False(KleeBurstResource.GaugeApplies(klee.Creature));
            Assert.Equal(0, KleeBurstResource.AmountFor(klee.Creature));
        });

        // THE MUTATION GUARD: off the arm the same seat still gets it, so what
        // the assertion above measured is the arm and not the harness.
        WithArm(false, () => Assert.True(KleeBurstResource.GaugeApplies(klee.Creature)));

        // And it was never anybody else's.
        Assert.False(KleeBurstResource.GaugeApplies(Seat.Furina().Creature));
    }

    [Fact]
    public void The_burst_spec_asks_the_resource_rather_than_the_character()
    {
        // STRUCTURAL. The guard has to be the one on `KleeBurstResource`, not a
        // second character test written out in the bridge, or the feed and the
        // display can be retired by halves -- which is exactly how they came
        // apart in the first place.
        var applies = (Func<Creature, bool>)Prop(Spec("burst"), "AppliesTo")!;
        Assert.Equal(typeof(KleeBurstResource), applies.Method.DeclaringType);
        Assert.Equal(nameof(KleeBurstResource.GaugeApplies), applies.Method.Name);
    }

    // --- the refresh funnels ----------------------------------------------

    [Fact]
    public void Every_funnel_that_moves_the_bank_redraws_the_gauge()
    {
        // STRUCTURAL: a Spark gain or spend needs a live `CombatState`, and the
        // sync reaches Godot on the far side. What is pinned is the property
        // that keeps the display honest -- the gauge is refreshed at exactly the
        // three chokepoints the `spark` meter ledger rides, so the number on
        // screen and the number in the ledger cannot come from different reads.
        foreach (var funnel in new[] { "Gain", "Spend", "AfterCardPlayed" })
        {
            var calls = Il.Calls(typeof(SparkPower).GetMethod(funnel, All)!);
            Assert.Contains("SparkPower.SyncGauge", calls);
            Assert.Contains("MeterLedger.Note", calls);
        }

        // And the sync itself goes to the gauge rather than carrying its own
        // arm test: `SparkGauge.Refresh` is where the arm is read.
        var sync = Il.Calls(typeof(SparkPower).GetMethod("SyncGauge", All)!);
        Assert.Contains("SparkGauge.Refresh", sync);

        // The catch-all for a bank moved by something that is not this mod (the
        // understudy's `set_power` door): the game's own fanned hook.
        var hook = Il.Calls(
            typeof(SparkPower).GetMethod(nameof(SparkPower.AfterPowerAmountChanged), All)!);
        Assert.Contains("SparkPower.SyncGauge", hook);
    }

    [Fact]
    public void The_refresh_declines_off_the_arm_and_for_everyone_else()
    {
        // REAL, and it is the one call into the gauge that is safe to make
        // headlessly BECAUSE it declines: every path below returns before
        // `GaugeBridge.Refresh`, which would reach Godot nodes. That is also the
        // acceptance condition for the release build -- a shipped Spark gain
        // gains no gauge work.
        var klee = Seat.Klee();
        WithArm(false, () =>
        {
            SparkGauge.Refresh(klee.Creature);
            SparkGauge.Refresh(null);
        });
        WithArm(true, () =>
        {
            SparkGauge.Refresh(Seat.Kokomi().Creature);
            SparkGauge.Refresh(null);
        });
    }
}
