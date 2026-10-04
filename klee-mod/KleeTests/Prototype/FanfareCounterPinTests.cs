using System;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// Furina's Fanfare gauge in the energy area (<see cref="FanfareCounter"/>),
/// built on Klee's Spark counter. Godot nodes cannot be built in this host
/// (README, the headless boundary), so what is pinned here is every DECISION:
/// who gets the gauge, what number it draws, what its hover says, whose old
/// badge is suppressed, and that it rides the funnel and the geometry that
/// already exist. Where it lands and how it looks is a frame on the next
/// deploy.
///
/// Shares <see cref="KleeOverhaulArm"/>'s collection with the Spark pins
/// because both move <c>LocalContext.NetId</c>, one process-wide static.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FanfareCounterPinTests
{
    private const BindingFlags All = HeadlessGame.All;

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
    public void Furina_gets_the_gauge_and_nobody_else_does()
    {
        Assert.True(FanfareCounter.AppliesTo(Seat.Furina().Creature));
        Assert.False(FanfareCounter.AppliesTo(Seat.Klee().Creature));
        Assert.False(FanfareCounter.AppliesTo(Seat.Kokomi().Creature));
        Assert.False(FanfareCounter.AppliesTo(null));
    }

    [Fact]
    public void The_face_is_her_fanfare_off_the_ledger_and_zero_is_drawn()
    {
        FurinaStageLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();
        Assert.Equal(0, FanfareCounter.Read(seat.Creature));

        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Gain(7);
        Assert.Equal(7, FanfareCounter.Read(seat.Creature));
        stage.Spend(2);
        Assert.Equal(5, FanfareCounter.Read(seat.Creature));
        // The same number the rules read, not a display copy.
        Assert.Equal(FurinaStage.FanfareOf(seat.Creature),
                     FanfareCounter.Read(seat.Creature));

        Assert.Equal(0, FanfareCounter.Read(Seat.Klee().Creature));
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void The_hover_carries_this_turns_gained_and_spent()
    {
        FurinaStageLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Gain(5);
        stage.Spend(2);

        var body = FanfareCounter.HoverBody(seat.Creature);
        Assert.Contains("gained [blue]5[/blue]", body);
        Assert.Contains("spent [blue]2[/blue]", body);
        // Under the keyword's own definition, one sentence and not a fork.
        var definition = (string)typeof(ArmKeywordTips)
            .GetField("FanfareBody", All)!.GetRawConstantValue()!;
        Assert.EndsWith(definition, body);
        // The face keeps the number alone: the flow is the hover's.
        Assert.Equal(3, FanfareCounter.Read(seat.Creature));

        Assert.Equal(FanfareCounter.HoverBody(0, 0),
                     FanfareCounter.HoverBody(null));
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void The_old_badge_hides_on_her_screen_and_shows_to_a_partner()
    {
        var furina = WithNetId(Seat.Furina(), 1UL).WithPower<FanfarePower>(1);
        var badge = furina.Creature.Powers.OfType<FanfarePower>().Single();

        AsLocalSeat(1UL, () => Assert.True(FanfareCounter.HidesBadge(badge)));
        AsLocalSeat(2UL, () => Assert.False(FanfareCounter.HidesBadge(badge)));

        // Rehearsal keeps its Power badge.
        var rehearsed = WithNetId(Seat.Furina(), 1UL)
            .WithPower<RehearsalPower>(2);
        var rehearsal = rehearsed.Creature.Powers.OfType<RehearsalPower>()
            .Single();
        AsLocalSeat(1UL,
            () => Assert.False(FanfareCounter.HidesBadge(rehearsal)));

        // A canonical model has no owner to ask, and must not throw.
        Assert.False(FanfareCounter.HidesBadge(new FanfarePower()));
    }

    [Fact]
    public void The_badge_stays_visible_to_the_model_so_the_wire_keeps_it()
    {
        // Suppressed at the container, never through IsVisibleInternal: the
        // bridge's power list skips an invisible power.
        var declared = typeof(FanfarePower)
            .GetProperty("IsVisibleInternal", All)
            ?.GetGetMethod(nonPublic: true)
            ?.DeclaringType;
        Assert.Equal(typeof(PowerModel), declared);
    }

    [Fact]
    public void The_refresh_is_headless_safe()
    {
        // No combat room in this host: every path returns before node work.
        FurinaStageLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();
        FanfareCounter.Refresh(seat.Creature);
        FanfareCounter.Refresh(Seat.Klee().Creature);
        FanfareCounter.Refresh(null);
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void The_gauge_rides_the_existing_funnel_setup_and_geometry()
    {
        var refresh = Il.Calls(typeof(FurinaStage)
            .GetMethod(nameof(FurinaStage.RefreshBadges), All)!);
        Assert.Contains(refresh,
            c => c.EndsWith("FanfareCounter.Refresh", StringComparison.Ordinal));

        var activate = Il.Calls(typeof(FanfareCounter).Assembly
            .GetType("KleeMod.Vfx.NCombatUi_Activate_GaugeSetup")!
            .GetMethod("Postfix", All)!);
        Assert.Contains(activate,
            c => c.EndsWith("FanfareCounter.Setup", StringComparison.Ordinal));

        // One placement rule and one node shape with Klee's Spark counter.
        var setup = Il.Calls(typeof(FanfareCounter)
            .GetMethod(nameof(FanfareCounter.Setup), All)!);
        Assert.Contains(setup,
            c => c.EndsWith("SparkCounter.Build", StringComparison.Ordinal));
        Assert.Contains(setup,
            c => c.EndsWith("SparkCounter.Apply", StringComparison.Ordinal));
        Assert.Contains(setup,
            c => c.EndsWith("SparkCounter.SideOf", StringComparison.Ordinal));
    }

    [Fact]
    public void The_glyph_is_the_one_her_fanfare_badge_wears()
    {
        Assert.Equal("furina/powers/center_stage.png", FanfareCounter.GlyphPath);
    }
}
