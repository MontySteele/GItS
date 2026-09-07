using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Nodes.Combat;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-628`: ENCORE AS PIPS, FANFARE AS A BADGE, AND THE OVERHEAD BAR OFF.
///
/// THE FIND. [USER]'s own Furina act-1 run, 2026-09-07: "the Encore 'how many
/// ticks of the stage do you have available' idea is not bad" -- the reading is
/// liked, the drawing is not -- and overhead sat a bar reading "10/70", a value
/// over a ceiling in the shipped Burst meter's shape.
///
/// WHAT IS REAL HERE. The counts and the scopes: one pip per performance the
/// stage can still pay for, the Spotlight's price as the marked prefix, the
/// badge's number and its next threshold, and who gets each.
///
/// WHAT IS STRUCTURAL, and labelled. The elements are Godot node trees and
/// Godot nodes are process death in this host (KleeTests README, the headless
/// boundary), so the DRAWING is pinned as source text and call sets.
///
/// WHAT NOTHING HERE CAN VERIFY: whether the pips read as ticks and whether the
/// badge lands beside the orb. That is a frame on the next `+proto` deploy.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class FanfareBadgeAndPipTests
{
    private const BindingFlags All = HeadlessGame.All;

    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;
        private readonly bool _evoke = FurinaReframe.EvokeEnabled;
        private readonly bool _meter = FurinaReframe.MeterEnabled;
        private readonly bool _spotlight = FurinaReframe.SpotlightEnabled;
        private readonly bool _burst = FurinaReframe.BurstEnabled;

        internal Arm(bool master = true, bool? burst = null)
        {
            FurinaReframe.Enabled = master;
            FurinaReframe.ManualEnabled = master;
            FurinaReframe.EvokeEnabled = master;
            FurinaReframe.MeterEnabled = master;
            FurinaReframe.SpotlightEnabled = master;
            FurinaReframe.BurstEnabled = burst ?? master;
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

    /// <summary>A Furina with a company and no Encore of her own yet.
    /// <see cref="SalonMemberStripPinTests"/>' helper without the opening
    /// grant, because the pip count IS the thing under test.</summary>
    private static Seat Stage(int encore, params SalonMember[] members)
    {
        FurinaReframeLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();

        var power = (SalonMemberPower)RuntimeHelpers
            .GetUninitializedObject(typeof(SalonMemberPower));
        Seat.Force(power, "Amount", members.Length);
        ((System.Collections.IList)seat.Creature.Powers).Add(power);
        Seat.Force(power, "IsMutable", true);
        Seat.Force(power, "Owner", seat.Creature);

        Company()[seat.Creature] = members.ToList();
        if (encore > 0) FurinaResources.GainEncore(seat.Creature, encore);
        return seat;
    }

    private static IDictionary<Creature, List<SalonMember>> Company() =>
        (IDictionary<Creature, List<SalonMember>>)typeof(SalonMemberPower)
            .GetField("Company", All)!
            .GetValue(null)!;

    // === 1. the pips =====================================================

    [Fact]
    public void One_pip_is_one_performance()
    {
        // THE READING [USER] LIKED, DRAWN AS TICKS. The ribbon's segment was
        // one TURN of upkeep -- a shipped-engine unit the manual leg deleted,
        // because under the arm nothing acts on its own. A performance costs
        // `TickEncoreCost`, so the honest unit is the performance.
        using var _ = new Arm();
        foreach (var encore in new[] { 0, 1, 2, 5, 9 })
        {
            var seat = Stage(encore, SalonMember.Usher);
            Assert.Equal(encore / SalonConstants.TickEncoreCost,
                         SalonMemberStrip.Pips(seat.Creature));
        }
    }

    [Fact]
    public void The_marked_pips_are_the_spotlights_price()
    {
        // The designation costs `SpotlightDesignateEncoreCost` of the Encore
        // she opens with, and a price is easier to count than to remember. The
        // number is read off the law rather than restated here.
        Assert.Equal(FurinaReframeLaw.SpotlightDesignateEncoreCost,
                     SalonMemberStrip.SpotlightPips);
        Assert.True(SalonMemberStrip.SpotlightPips > 0);
        // It must fit inside the opening hand's Encore, or the mark points at
        // pips a turn-one player has never had.
        Assert.True(SalonMemberStrip.SpotlightPips
                    <= FurinaReframeLaw.OpeningEncore);

        var source = Source("Vfx/Prototype/SalonMemberStrip.cs")
            .Replace("\r\n", "\n");
        Assert.Contains("i < SpotlightPips ? PipSpotlight : PipFull", source);
    }

    [Fact]
    public void A_runway_past_the_row_overflows_rather_than_running_off()
    {
        using var _ = new Arm();
        var seat = Stage(SalonMemberStrip.MaxPips + 4, SalonMember.Usher);

        Assert.Equal(SalonMemberStrip.MaxPips + 4,
                     SalonMemberStrip.Pips(seat.Creature));

        var source = Source("Vfx/Prototype/SalonMemberStrip.cs")
            .Replace("\r\n", "\n");
        Assert.Contains("overflow.Visible = pips > MaxPips;", source);
        Assert.Contains("$\"+{pips - MaxPips}\"", source);
    }

    // === 2. the badge ====================================================

    [Fact]
    public void The_badge_is_compiled_only_under_the_prototype_arm()
    {
        Assert.Contains("<Compile Remove=\"Vfx/Prototype/**/*.cs\" />",
                        Source("KleeCode.csproj"));
        Assert.NotNull(Source("Vfx/Prototype/FanfareCounter.cs"));
        Assert.Equal("KleeMod.Vfx", typeof(FanfareCounter).Namespace);
    }

    [Fact]
    public void Furina_gets_the_badge_under_the_meter_leg_and_nobody_else()
    {
        var furina = Seat.Furina();
        var klee = Seat.Klee();
        var kokomi = Seat.Kokomi();

        using (new Arm())
        {
            Assert.True(FanfareCounter.AppliesTo(furina.Creature));
            // Klee's Spark badge takes the same corner under HER arm; the two
            // are never the same seat, which is why neither offsets around the
            // other.
            Assert.False(FanfareCounter.AppliesTo(klee.Creature));
            Assert.False(FanfareCounter.AppliesTo(kokomi.Creature));
            Assert.False(SparkCounter.AppliesTo(furina.Creature));
        }

        using (new Arm(master: false))
        {
            Assert.False(FanfareCounter.AppliesTo(furina.Creature));
        }

        Assert.False(FanfareCounter.AppliesTo(null));
    }

    [Fact]
    public void The_badge_reads_the_live_fanfare_through_the_kits_accessor()
    {
        using var _ = new Arm();
        var seat = Stage(0, SalonMember.Crabaletta);

        Assert.Equal(0, FanfareCounter.Read(seat.Creature));

        FurinaResources.GainFanfare(seat.Creature, 6);
        Assert.Equal(6, FanfareCounter.Read(seat.Creature));
        // The same read every card in the kit takes, and the same one the
        // member bonus divides -- not a display copy.
        Assert.Equal(FurinaResources.ReadableFanfare(seat.Creature),
                     FanfareCounter.Read(seat.Creature));
    }

    [Fact]
    public void The_threshold_is_the_next_step_of_the_member_bonus()
    {
        using var _ = new Arm();
        var step = SalonConstants.FocusPerFanfare;
        var seat = Stage(0, SalonMember.Crabaletta);

        // Nothing held: the first step.
        Assert.Equal(step, FanfareCounter.NextThreshold(seat.Creature));
        Assert.Equal($"+1 at {step}", FanfareCounter.StepText(seat.Creature));

        // Part way: still the first step.
        FurinaResources.GainFanfare(seat.Creature, step - 4);
        Assert.Equal(step, FanfareCounter.NextThreshold(seat.Creature));

        // STANDING EXACTLY ON ONE points at the NEXT, not at itself: a badge
        // that says "+1 at 10" while holding 10 is telling the player about a
        // bonus they already have.
        FurinaResources.GainFanfare(seat.Creature, 4);
        Assert.Equal(step, FurinaResources.ReadableFanfare(seat.Creature));
        Assert.Equal(2 * step, FanfareCounter.NextThreshold(seat.Creature));

        // And the step it names is the one the member numbers actually move
        // on, which is the only thing Fanfare does under the arm.
        var before = SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Crabaletta, paid: true);
        FurinaResources.GainFanfare(seat.Creature, step);
        Assert.Equal(before + 1, SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Crabaletta, paid: true));
    }

    [Fact]
    public void The_badge_rides_the_funnel_the_meter_already_has()
    {
        // `FurinaResources.SyncMeters` is where the Fanfare badge power, the
        // Spotlight display and the Salon display are all refreshed. One
        // funnel, so the badge and the strip cannot come from different reads.
        var calls = Il.Calls(typeof(FurinaResources)
            .GetMethod(nameof(FurinaResources.SyncMeters), All)!);
        Assert.Contains(calls,
            c => c.EndsWith("FanfareCounter.Refresh", StringComparison.Ordinal));

        // Built at the one combat-lifecycle door.
        var postfix = typeof(GaugeBridge).Assembly
            .GetType("KleeMod.Vfx.NCombatUi_Activate_GaugeSetup")!
            .GetMethod("Postfix", All)!;
        Assert.Contains(Il.Calls(postfix),
            c => c.EndsWith("FanfareCounter.Setup", StringComparison.Ordinal));

        // NO POLLING. A per-frame `_Process` would be a second cadence.
        Assert.DoesNotContain("void _Process",
                              Source("Vfx/Prototype/FanfareCounter.cs"));
    }

    [Fact]
    public void The_rect_is_read_off_the_live_star_counter_and_not_guessed()
    {
        var source = Source("Vfx/Prototype/FanfareCounter.cs")
            .Replace("\r\n", "\n");

        Assert.Contains("GetNodeOrNull<Control>(\"%StarCounter\")", source);
        foreach (var edge in new[] { "Left", "Top", "Right", "Bottom" })
        {
            Assert.Contains($"root.Anchor{edge} = star.Anchor{edge};", source);
            Assert.Contains($"root.Offset{edge} = star.Offset{edge};", source);
        }

        // The energy orb takes the base game's own displacement -- and it is
        // the SAME literal the Spark badge moved it by, not a second copy.
        Assert.Contains("EnergyCounterContainer?.SetPosition(EnergyCounterOffset",
                        source);
        Assert.Equal(
            (Godot.Vector2)typeof(SparkCounter)
                .GetField("EnergyCounterOffset", All)!.GetValue(null)!,
            (Godot.Vector2)typeof(FanfareCounter)
                .GetField("EnergyCounterOffset", All)!.GetValue(null)!);

        // `EB-222`: no texture is held across a scene.
        Assert.Contains("ResourceLoader.Load<Texture2D>(path)", source);
        Assert.DoesNotContain("static Texture2D", source);
        Assert.Equal("furina/powers/fanfare.png", FanfareCounter.GlyphPath);
    }

    [Fact]
    public void The_teardown_is_on_the_games_hook_and_names_no_seat()
    {
        var patch = typeof(GaugeBridge).Assembly
            .GetType("KleeMod.Vfx.NCombatUi_Deactivate_KleeFanfareCounter_Patch")!;

        var attribute = patch.GetCustomAttribute<HarmonyPatch>()!;
        Assert.Equal(typeof(NCombatUi), attribute.info.declaringType);
        Assert.Equal(nameof(NCombatUi.Deactivate), attribute.info.methodName);

        var hide = typeof(FanfareCounter).GetMethod("Hide", All)!;
        Assert.Equal(typeof(NCombatUi),
                     hide.GetParameters().Single().ParameterType);

        // The exemption is DECLARED rather than inferred (`EB-225`).
        var source = Source("Vfx/Prototype/FanfareCounter.cs")
            .Replace("\r\n", "\n");
        var marker = source.Split('\n')
            .First(line => line.Contains("lint: no-seat:"));
        Assert.True(marker.Trim().Length > "// lint: no-seat:".Length + 10,
                    "the no-seat exemption must carry a reason");
    }

    // === 3. the overhead bar =============================================

    [Fact]
    public void No_overhead_bar_draws_for_furina_under_the_arm()
    {
        // "of 70" is a denominator nobody reaches: the shipped Burst engine is
        // retired here (`EB-365`), and Fanfare's own cap is a demoted safety
        // rail F-A5 measured as never binding. So the overhead slot stands
        // down whenever the MASTER is live -- including a build running the
        // arm with the Burst leg deliberately off, which is the case a guard
        // on `BurstRetiredFor` alone would still draw a bar for.
        var furina = Seat.Furina();

        using (new Arm())
        {
            Assert.False(FurinaResources.BurstGaugeApplies(furina.Creature));
        }
        using (new Arm(master: true, burst: false))
        {
            Assert.False(FurinaResources.BurstGaugeApplies(furina.Creature));
        }

        // OFF THE ARM THE SHIPPED METER IS EXACTLY THE SHIPPED METER: this is
        // a display retirement inside one arm, not a roster change.
        using (new Arm(master: false))
        {
            Assert.True(FurinaResources.BurstGaugeApplies(furina.Creature));
        }
    }

    [Fact]
    public void The_rules_half_of_the_burst_retirement_is_unmoved()
    {
        // The DISPLAY guard widened; the RULES guard did not. The income
        // funnel, the kit grant and the sim's `burst_retired` all still ask
        // the Burst leg, so a build with that leg off still feeds and grants
        // the shipped meter -- it just does not hang a bar overhead.
        var furina = Seat.Furina();
        using var _ = new Arm(master: true, burst: false);
        Assert.False(FurinaReframe.BurstRetiredFor(furina.Creature));
    }

    // --- source access ----------------------------------------------------

    private static string Source(string relativePath) =>
        Read(System.IO.Path.Combine("klee-mod", "KleeCode",
            relativePath.Replace('/', System.IO.Path.DirectorySeparatorChar)));

    private static string Read(string relative)
    {
        var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = System.IO.Path.Combine(dir.FullName, relative);
            if (System.IO.File.Exists(candidate))
            {
                return System.IO.File.ReadAllText(candidate);
            }

            dir = dir.Parent;
        }

        throw new System.IO.FileNotFoundException(relative);
    }
}
