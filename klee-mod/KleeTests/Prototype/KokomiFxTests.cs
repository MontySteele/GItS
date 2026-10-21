using System.Linq;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// Kokomi's art polish (2026-10-21; Kokomi taste and art paper, pick 5 (a)):
/// the Plan carry-out effect, the visible swarm, the Hydro sigil and the
/// Casket's pearl flash. The arithmetic is pinned for real
/// (<see cref="KokomiFxMath"/>); the wiring structurally, since nothing
/// headless has a scene tree.
/// </summary>
public class KokomiFxTests
{
    // ---- timing -------------------------------------------------------------

    [Fact]
    public void Every_effect_ends_by_six_tenths_of_a_second()
    {
        foreach (var end in KokomiFxMath.Ends())
        {
            Assert.True(end <= KokomiFxMath.LongestEffect + 1e-4f,
                        $"an effect runs {end} s, past {KokomiFxMath.LongestEffect} s");
        }
    }

    [Fact]
    public void The_bolt_lands_as_the_lunge_hold_ends()
    {
        // KurageBeat.ActSeconds is 0.35: the damage number follows it, so
        // the bolt's arrival must not be later than that.
        Assert.True(KokomiFxMath.BoltAt + KokomiFxMath.BoltFlight <= 0.35f + 1e-4f);
        Assert.True(KokomiFxMath.DartAt + KokomiFxMath.DartFlight <= 0.35f + 1e-4f);
    }

    [Theory]
    [InlineData("Normal", 1f)]
    [InlineData("Fast", 0.5f)]
    [InlineData("None", 1f)]
    public void Effects_follow_the_game_speed(string mode, float factor)
    {
        Assert.Equal(factor, KokomiFxMath.SpeedFactor(mode));
    }

    [Fact]
    public void Instant_mode_plays_no_effect()
    {
        Assert.Null(KokomiFxMath.SpeedFactor("Instant"));
    }

    // ---- the look -----------------------------------------------------------

    [Theory]
    [InlineData(0, false, PlanBeatLook.Pulse)]
    [InlineData(0, true, PlanBeatLook.Pulse)]
    [InlineData(1, false, PlanBeatLook.Bolt)]
    [InlineData(1, true, PlanBeatLook.Ripple)]
    [InlineData(3, false, PlanBeatLook.Ripple)]
    public void A_plan_picks_its_look_from_what_it_hits(int targets, bool all,
                                                        PlanBeatLook look)
    {
        Assert.Equal(look, KokomiFxMath.LookFor(targets, all));
    }

    [Fact]
    public void The_caption_names_the_card_and_its_number()
    {
        Assert.Equal("Ambush  12", KokomiFxMath.Caption("Ambush", 12));
        Assert.Equal("Stolen Chapter", KokomiFxMath.Caption("Stolen Chapter", null));
    }

    [Fact]
    public void The_arc_starts_and_ends_on_its_points_and_lifts_between()
    {
        Assert.Equal((0f, 0f), KokomiFxMath.Arc(0, 0, 100, 0, 50, 0f));
        Assert.Equal((100f, 0f), KokomiFxMath.Arc(0, 0, 100, 0, 50, 1f));
        var (_, y) = KokomiFxMath.Arc(0, 0, 100, 0, 50, 0.5f);
        Assert.Equal(-50f, y, 3);
    }

    // ---- the swarm ----------------------------------------------------------

    [Theory]
    [InlineData(0, 0, null)]
    [InlineData(5, 5, null)]
    [InlineData(8, 8, null)]
    [InlineData(11, 8, "+3")]
    public void The_swarm_draws_at_most_eight(int count, int drawn, string more)
    {
        Assert.Equal((drawn, more), KokomiFxMath.SwarmShown(count));
    }

    [Theory]
    [InlineData(3, 2, 3, 2)]
    [InlineData(10, 2, 7, 1)]
    [InlineData(2, 10, 1, 7)]
    [InlineData(12, 0, 8, 0)]
    [InlineData(0, 12, 0, 8)]
    [InlineData(7, 1, 7, 1)]
    public void The_cap_is_shared_and_each_kind_shows(int stings, int wards,
                                                     int s, int w)
    {
        Assert.Equal((s, w), KokomiFxMath.SwarmSplit(stings, wards));
    }

    [Theory]
    // (visible, hidden, wanted) -> (unhide, add, removeHidden, removeVisible)
    [InlineData(3, 0, 3, 0, 0, 0, 0)]
    [InlineData(3, 0, 5, 0, 2, 0, 0)]
    [InlineData(3, 0, 1, 0, 0, 0, 2)]
    // a dart hid one, then the queue moved by one: the hidden one goes
    [InlineData(2, 1, 2, 0, 0, 1, 0)]
    // a Plan carried out twice hid two, the queue moved by one: one comes back
    [InlineData(1, 2, 2, 1, 0, 1, 0)]
    // a reload or a cleared queue: nothing wanted
    [InlineData(4, 1, 0, 0, 0, 1, 4)]
    public void The_swarm_reconciles_to_the_queue(int visible, int hidden, int wanted,
                                                  int unhide, int add, int rmHidden,
                                                  int rmVisible)
    {
        Assert.Equal((unhide, add, rmHidden, rmVisible),
                     KokomiFxMath.Reconcile(visible, hidden, wanted));
    }

    // ---- the wiring, structural ---------------------------------------------

    [Fact]
    public void The_carry_out_picture_starts_before_the_lunge_and_is_not_awaited()
    {
        var calls = Il.CallSequence(Il.Method("KokomiPlan", "ResolveEntry"));
        var beat = calls.ToList().IndexOf("KokomiPlan.PlayBeat");
        var act = calls.ToList().IndexOf("KurageBeat.Act");
        Assert.True(beat >= 0, "the carry-out picture is gone");
        Assert.True(beat < act, "the picture starts with the lunge, not after it");
        Assert.Contains("KokomiPlanFx.CarryOut",
                        Il.Calls(Il.Method("KokomiPlan", "PlayBeat")));
    }

    [Fact]
    public void The_swarm_rides_the_strip_funnel_and_the_combat_setup()
    {
        Assert.Contains("KokomiSwarm.Refresh",
                        Il.Calls(Il.Method("KokomiPlanStrip", "Refresh")));
        Assert.Contains("KokomiSwarm.SetupAll",
                        Il.Calls(Il.Method("NCombatUi_Activate_GaugeSetup", "Postfix")));
        Assert.Contains("KokomiPlan.Showing",
                        Il.Calls(Il.Method("KokomiSwarm", "Refresh")));
    }

    [Fact]
    public void The_sigil_and_the_casket_pearl_are_wired()
    {
        Assert.Contains("KokomiPlanFx.OnTravel",
                        Il.Calls(Il.Method("CreatureAnimationRouter", "Route")));
        Assert.Contains("KokomiPlanFx.CasketPearl",
                        Il.CallSequence(Il.Method("TamakushiCasket", "AfterCardPlayed")));
    }

    [Fact]
    public void The_sigil_is_hers_alone()
    {
        Assert.Contains("KokomiResources.IsKokomi",
                        Il.Calls(Il.Method("KokomiPlanFx", "OnTravel")));
    }
}
