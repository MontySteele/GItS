using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Entities.Creatures;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-628`, `EB-633`, `EB-634`, `EB-635`: THE PANEL'S RESOURCE LINE, ITS
/// DRY-STAGE NOTICE, AND THE SCALE TABLE UNDER BOTH.
///
/// THE FIND. [USER]'s own Furina act-1 run, 2026-09-07 ("the Encore 'how many
/// ticks of the stage do you have available' idea is not bad" -- the reading is
/// liked, the drawing is not; overhead sat a bar reading "10/70"), and then the
/// `0.2.2917+proto` frame: "I don't see Encore anywhere", a Fanfare badge in
/// the energy corner the size of the energy orb, and the board's sizes chosen
/// ad hoc.
///
/// WHAT IS REAL HERE. The counts, the words and the scale rule: what the line
/// says at every meter value, one pip per FULL-STRENGTH performance, the
/// reduced-performance notice firing exactly when the chips go dry, and the
/// tier table's ordering and its clamp under the energy orb's number.
///
/// WHAT IS STRUCTURAL, and labelled. The panel is a Godot node tree and Godot
/// nodes are process death in this host (KleeTests README, the headless
/// boundary), so the DRAWING is pinned as source text and call sets.
///
/// WHAT NOTHING HERE CAN VERIFY: whether the line reads beside the chips and
/// whether the tiers land as a hierarchy. That is a frame on the next `+proto`
/// deploy.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class SalonPanelResourceLineTests
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
    /// <see cref="SalonPanelPinTests"/>' helper without the opening grant,
    /// because the meter values ARE the thing under test.</summary>
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

    // === 1. the line leads with a name and a number ======================

    [Fact]
    public void Encore_has_a_name_and_a_number_before_any_pips()
    {
        // `EB-635`, AND IT IS THE WHOLE ROW. "I don't see Encore anywhere" was
        // true twice over on the frame: the meter was 0, so every pip was
        // drawn in the empty colour, and a row of dim pips is
        // indistinguishable from no row at all. So the line leads with the
        // WORD and the NUMBER, and the pips are a second reading of it.
        using var _ = new Arm();

        foreach (var encore in new[] { 0, 1, 2, 7 })
        {
            var seat = Stage(encore, SalonMember.Usher);
            Assert.Equal($"Encore {encore}",
                         SalonPanel.EncoreText(seat.Creature));
        }
    }

    [Fact]
    public void The_line_says_the_meter_and_what_the_meter_is_buying()
    {
        using var _ = new Arm();
        var step = SalonConstants.FocusPerFanfare;
        var seat = Stage(0, SalonMember.Crabaletta);

        Assert.Equal("- Fanfare 0 - Member bonus +0",
                     SalonPanel.MeterText(seat.Creature));

        FurinaResources.GainFanfare(seat.Creature, 2 * step);
        Assert.Equal($"- Fanfare {2 * step} - Member bonus +2",
                     SalonPanel.MeterText(seat.Creature));

        // THE BONUS IS THE ONE THING FANFARE DOES under the arm, and the panel
        // says it in the same breath as the meter -- and it is the number the
        // chips above are already folding, not a second arithmetic.
        var before = SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Crabaletta, paid: true);
        FurinaResources.GainFanfare(seat.Creature, step);
        Assert.Equal(3, SalonPanel.MemberBonus(seat.Creature));
        Assert.Equal(before + 1, SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Crabaletta, paid: true));
    }

    [Fact]
    public void The_meter_is_read_through_the_kits_own_accessor()
    {
        using var _ = new Arm();
        var seat = Stage(0, SalonMember.Crabaletta);

        FurinaResources.GainFanfare(seat.Creature, 6);
        // The same read every card in the kit takes, and the same one the
        // member bonus divides -- not a display copy.
        Assert.Equal(FurinaResources.ReadableFanfare(seat.Creature),
                     SalonPanel.Fanfare(seat.Creature));
    }

    [Fact]
    public void The_threshold_is_a_hover_footnote_and_not_a_line()
    {
        // It was a second number under a badge the size of the energy orb.
        // "+1 at 20" is a footnote to the Fanfare number, so it hangs off the
        // resource row's hover and the line stays one sentence.
        using var _ = new Arm();
        var step = SalonConstants.FocusPerFanfare;
        var seat = Stage(0, SalonMember.Crabaletta);

        Assert.Equal(step, SalonPanel.NextThreshold(seat.Creature));
        Assert.Equal($"+1 at {step}", SalonPanel.StepText(seat.Creature));

        // STANDING EXACTLY ON ONE points at the NEXT, not at itself: a badge
        // that says "+1 at 10" while holding 10 is telling the player about a
        // bonus they already have.
        FurinaResources.GainFanfare(seat.Creature, step);
        Assert.Equal(2 * step, SalonPanel.NextThreshold(seat.Creature));

        // And it is off the line itself.
        Assert.DoesNotContain("+1 at", SalonPanel.MeterText(seat.Creature));

        var source = Source("Vfx/Prototype/SalonPanel.cs")
            .Replace("\r\n", "\n");
        Assert.Contains("row.TooltipText = StepText(owner);", source);
        // A control that IGNORES the mouse shows no tooltip; `Pass` shows one
        // and still hands the event on.
        Assert.Contains("MouseFilter = Control.MouseFilterEnum.Pass", source);
    }

    // === 2. the pips, and what they count ================================

    [Fact]
    public void One_pip_is_one_full_strength_performance()
    {
        // A performance costs `TickEncoreCost`, so the honest unit is the
        // performance -- the ribbon's old segment was one TURN of upkeep, a
        // shipped-engine unit the manual leg deleted.
        using var _ = new Arm();
        foreach (var encore in new[] { 0, 1, 2, 5, 9 })
        {
            var seat = Stage(encore, SalonMember.Usher);
            Assert.Equal(encore / SalonConstants.TickEncoreCost,
                         SalonPanel.Pips(seat.Creature));
        }
    }

    [Fact]
    public void Every_pip_slot_is_drawn_at_zero_rather_than_the_row_vanishing()
    {
        // `EB-635`'s other half: a strip that shrank at zero would make an
        // empty meter look like a missing row, which is what was filed.
        var source = Source("Vfx/Prototype/SalonPanel.cs")
            .Replace("\r\n", "\n");
        Assert.Contains("pip.Visible = true;", source);
        Assert.Contains("pip.Color = i < drawn ? PipFull : PipEmpty;", source);

        // And the Spotlight's price is NOT permanently coloured into them any
        // more: two marked pips were a standing claim about one card, in a
        // hand that may not be holding it. `EB-637` takes the hover instead.
        Assert.DoesNotContain("SpotlightPips", source);
    }

    // === 3. the dry stage says so ========================================

    [Fact]
    public void An_empty_meter_says_the_stage_is_reduced_not_stopped()
    {
        // `EB-633`. The pips count FULL-STRENGTH performances; a member with
        // nothing to spend still performs, at three-quarters. So an empty
        // meter must not read as an idle stage.
        using var _ = new Arm();

        var dry = Stage(0, SalonMember.Crabaletta);
        Assert.False(SalonPanel.Paid(dry.Creature));

        var wet = Stage(SalonConstants.TickEncoreCost, SalonMember.Crabaletta);
        Assert.True(SalonPanel.Paid(wet.Creature));

        var source = Source("Vfx/Prototype/SalonPanel.cs")
            .Replace("\r\n", "\n");
        // ONE condition for the notice, the chips and the pips, so the note
        // and the numbers cannot disagree about whether the buffer is dry.
        Assert.Contains("notice.Visible = !paid;", source);
        Assert.Contains("var paid = Paid(owner);", source);
        Assert.Equal("Reduced performance", SalonPanel.ReducedNotice);
    }

    [Fact]
    public void At_zero_encore_the_chip_number_is_already_the_dry_one()
    {
        // `EB-633`'s second half, and it needed no new arithmetic: `TickValue`
        // is where the dry three-quarters lives, so the chip prints the number
        // the member will actually deal rather than the one it would like to.
        using var _ = new Arm();
        var seat = Stage(0, SalonMember.Crabaletta);

        var paid = SalonPanel.Paid(seat.Creature);
        Assert.False(paid);

        var dry = SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Crabaletta, paid: false);
        var wet = SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Crabaletta, paid: true);
        Assert.True(dry < wet);
        Assert.Equal($"{dry} Hydro",
            SalonPanel.NextAct(seat.Creature, SalonMember.Crabaletta, paid));
    }

    // === 4. the scale table ==============================================

    [Fact]
    public void The_table_is_a_hierarchy_and_not_a_list_of_pixels()
    {
        // `EB-634`. A flat table would have fixed the drift and not the
        // reading: it would still be possible to give the Evoke footnote the
        // same size as the number it qualifies and break no rule.
        Assert.True(FurinaBoardScale.Tier1FontSize
                    > FurinaBoardScale.Tier2FontSize);
        Assert.True(FurinaBoardScale.Tier2FontSize
                    > FurinaBoardScale.Tier3FontSize);
    }

    [Fact]
    public void Every_size_on_the_panel_reads_off_the_table()
    {
        // The acceptance condition: no element sizes itself. The panel's own
        // source carries no bare font size and no bare chip or pip dimension.
        var source = Source("Vfx/Prototype/SalonPanel.cs")
            .Replace("\r\n", "\n");

        foreach (var name in new[]
                 {
                     "Tier1FontSize", "Tier2FontSize", "Tier3FontSize",
                     "PanelWidth", "PanelHeight", "ChipWidth", "ChipHeight",
                     "FaceHeight", "ChipPitchMax", "PipWidth", "PipHeight",
                     "PipGap", "ResourceFontSize",
                 })
        {
            Assert.Contains($"FurinaBoardScale.{name}", source);
        }
    }

    [Fact]
    public void The_fanfare_number_is_tier_two_and_under_the_energy_orbs()
    {
        // `EB-634`'s named condition, and it is ENFORCED rather than asserted:
        // the resource line's size is clamped under the orb's own number,
        // whatever the orb turns out to be.
        Assert.Equal(FurinaBoardScale.Tier2FontSize,
                     FurinaBoardScale.ResourceFontSize(
                         FurinaBoardScale.EnergyOrbFontSizeFallback));
        Assert.True(FurinaBoardScale.Tier2FontSize
                    < FurinaBoardScale.EnergyOrbFontSizeFallback);

        // A live orb SMALLER than tier 2 pulls the line down under it rather
        // than leaving the panel shouting over the energy area.
        Assert.Equal(7, FurinaBoardScale.ResourceFontSize(8));
        // And an unreadable one takes the documented fallback.
        Assert.Equal(FurinaBoardScale.Tier2FontSize,
                     FurinaBoardScale.ResourceFontSize(null));
        Assert.Equal(FurinaBoardScale.Tier2FontSize,
                     FurinaBoardScale.ResourceFontSize(0));
    }

    [Fact]
    public void The_orbs_size_is_read_off_the_live_scene_and_not_guessed()
    {
        var source = Source("Vfx/Prototype/FurinaBoardScale.cs")
            .Replace("\r\n", "\n");

        // BY SEARCH AND NOT BY PATH: naming a child of the container would be
        // a claim about a scene we do not ship, which `EB-621` already
        // declined to make for the star counter's rect.
        Assert.Contains("ui?.EnergyCounterContainer", source);
        Assert.Contains("GetThemeFontSize(ThemeConstants.Label.FontSize)",
                        source);
        // And a read on a live scene from a display path costs a font size,
        // never a run.
        Assert.Contains("catch (Exception)", source);
    }

    // === 5. the overhead bar, and the corner the panel gave back =========

    [Fact]
    public void No_overhead_bar_draws_for_furina_under_the_arm()
    {
        // "of 70" is a denominator nobody reaches: the shipped Burst engine is
        // retired here (`EB-365`), and Fanfare's own cap is a demoted safety
        // rail F-A5 measured as never binding. So the overhead slot stands
        // down whenever the MASTER is live -- which is also what frees the
        // space the panel now sits above.
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

    [Fact]
    public void Nothing_of_furinas_draws_beside_the_energy_orb_any_more()
    {
        // The Fanfare badge in the energy corner is GONE, folded into the
        // panel's resource line: one element for the whole board. Klee's Spark
        // badge keeps that corner under her own arm, and the energy orb is
        // displaced by her alone.
        Assert.Null(typeof(SparkCounter).Assembly
            .GetType("KleeMod.Vfx.FanfareCounter"));

        var gauge = Source("Vfx/GaugeBridge.cs");
        Assert.DoesNotContain("FanfareCounter", gauge);
        Assert.Contains("SparkCounter.Setup(state);", gauge);

        var resources = Source("Powers/FurinaResources.cs");
        Assert.DoesNotContain("FanfareCounter", resources);
        // And the one funnel the panel does ride is still there.
        Assert.Contains("Vfx.SalonVisualsBridge.Refresh(creature);",
                        resources);
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
