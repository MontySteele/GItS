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
/// `EB-627`: THE SALON AS ONE PANEL, under the reframe's manual leg.
///
/// WHAT IS REAL HERE. Every DECISION the panel takes runs on live objects: who
/// gets it, how many chips, which member is in which chip, what each chip's
/// next act says, and that the Fanfare bonus is folded into the number by the
/// same call the performance resolves through.
///
/// WHAT IS STRUCTURAL, and labelled. The element is a Godot node tree and Godot
/// nodes are process death in this host (KleeTests README, the headless
/// boundary), so the DRAWING is pinned as source text and call sets: that the
/// chips read the company by index, that chip 0 is the front and says so in a
/// word, that everything sits inside ONE backing rectangle above the creature,
/// that the panel is built at the stage's own door, that no texture is cached
/// across a scene and that nothing polls.
///
/// WHAT NOTHING HERE CAN VERIFY: the look. Whether the panel reads at combat
/// scale, whether the anchor clears the hand's expansion and the targeting
/// arrows, whether the face crops are legible. That is a frame on the next
/// `+proto` deploy and no assertion in this file claims it.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class SalonPanelPinTests
{
    private const BindingFlags All = HeadlessGame.All;

    /// <summary>The manual leg on for one test and every flag back after it --
    /// <see cref="FurinaReframeRoundSevenTests"/>' fixture, and all six flags
    /// for its reason.</summary>
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;
        private readonly bool _evoke = FurinaReframe.EvokeEnabled;
        private readonly bool _meter = FurinaReframe.MeterEnabled;
        private readonly bool _spotlight = FurinaReframe.SpotlightEnabled;
        private readonly bool _burst = FurinaReframe.BurstEnabled;

        internal Arm(bool master = true)
        {
            FurinaReframe.Enabled = master;
            FurinaReframe.ManualEnabled = master;
            FurinaReframe.EvokeEnabled = master;
            FurinaReframe.MeterEnabled = master;
            FurinaReframe.SpotlightEnabled = master;
            FurinaReframe.BurstEnabled = master;
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

    /// <summary>A Furina with a company on the stage.
    /// <see cref="FurinaReframeRuleTests"/>' helper, verbatim.</summary>
    private static Seat Stage(params SalonMember[] members)
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
        FurinaResources.GainEncore(seat.Creature, 9);
        return seat;
    }

    private static IDictionary<Creature, List<SalonMember>> Company() =>
        (IDictionary<Creature, List<SalonMember>>)typeof(SalonMemberPower)
            .GetField("Company", All)!
            .GetValue(null)!;

    // --- the quarantine ---------------------------------------------------

    [Fact]
    public void The_panel_is_compiled_only_under_the_prototype_arm()
    {
        // THE QUARANTINE IS THE FILE'S LOCATION, not an `#if` inside it:
        // `KleeCode.csproj` `Compile Remove`s `Vfx/Prototype/**/*.cs` without
        // `-p:PrototypeCards=true`. This test file is itself removed off the
        // arm, so its mere compilation is the other half.
        Assert.Contains("<Compile Remove=\"Vfx/Prototype/**/*.cs\" />",
                        Source("KleeCode.csproj"));
        Assert.NotNull(Source("Vfx/Prototype/SalonPanel.cs"));
        Assert.Equal("KleeMod.Vfx", typeof(SalonPanel).Namespace);
    }

    // --- who gets it ------------------------------------------------------

    [Fact]
    public void Furina_gets_the_panel_under_the_manual_leg_and_nobody_else()
    {
        var furina = Seat.Furina();
        var klee = Seat.Klee();
        var kokomi = Seat.Kokomi();

        using (new Arm())
        {
            Assert.True(SalonPanel.AppliesTo(furina.Creature));
            // Both are at the same table in co-op and neither has a Salon.
            Assert.False(SalonPanel.AppliesTo(klee.Creature));
            Assert.False(SalonPanel.AppliesTo(kokomi.Creature));
        }

        // THE ACCEPTANCE CONDITION. Off the arm there is no strip at all, so
        // the shipped stage is exactly the shipped stage.
        using (new Arm(master: false))
        {
            Assert.False(SalonPanel.AppliesTo(furina.Creature));
        }

        // And a creature it is never asked about answers false rather than
        // throwing: `Refresh` is called from the stage's own funnel.
        Assert.False(SalonPanel.AppliesTo(null));
    }

    [Fact]
    public void The_scope_is_the_manual_leg_and_not_a_second_copy_of_it()
    {
        // The member tips branch on `ManualLiveFor` too. Two predicates would
        // be two things to keep true, and the strip draws exactly the rules
        // that leg makes true.
        var calls = Il.Calls(typeof(SalonPanel)
            .GetMethod(nameof(SalonPanel.AppliesTo), All)!);
        Assert.Contains(calls,
            c => c.EndsWith("FurinaReframe.ManualLiveFor",
                            StringComparison.Ordinal));
    }

    // --- what is in which chip -------------------------------------------

    [Fact]
    public void The_chips_are_the_company_in_slot_order()
    {
        using var _ = new Arm();
        var seat = Stage(SalonMember.Usher, SalonMember.Chevalmarin,
                         SalonMember.Crabaletta);

        Assert.Equal(
            new[] { SalonMember.Usher, SalonMember.Chevalmarin,
                    SalonMember.Crabaletta },
            SalonPanel.Company(seat.Creature));
    }

    [Fact]
    public void Duplicates_render_as_duplicates()
    {
        // Funnel Contract sec.1: deploy is by card and three of the same
        // member is a legal stage. This is the assumption sprint 1's fixed
        // member-to-slot portrait table silently made and got wrong.
        using var _ = new Arm();
        var seat = Stage(SalonMember.Usher, SalonMember.Usher,
                         SalonMember.Usher);

        Assert.Equal(3, SalonPanel.Company(seat.Creature).Count);
        Assert.All(SalonPanel.Company(seat.Creature),
                   m => Assert.Equal(SalonMember.Usher, m));
    }

    [Fact]
    public void The_chip_count_is_the_live_cap_clamped_to_what_can_be_drawn()
    {
        using var _ = new Arm();
        var seat = Stage(SalonMember.Usher);

        Assert.Equal(SalonConstants.MemberSlots,
                     SalonPanel.Slots(seat.Creature));
        Assert.Equal(SalonMemberPower.SlotsFor(seat.Creature),
                     SalonPanel.Slots(seat.Creature));

        // A cap past what the row can hold is clamped rather than silently
        // invisible -- the sprint-2 gap where a fourth member ticked, bowed and
        // counted for every rider while nothing on screen said so.
        var wide = Stage(SalonMember.Usher).WithPower<SalonCapUpPower>(9);
        Assert.Equal(SalonPanel.MaxChips,
                     SalonPanel.Slots(wide.Creature));
    }

    [Fact]
    public void Chip_zero_is_the_front_and_the_front_is_what_is_marked()
    {
        // STRUCTURAL. The rule "a Companion card performs the front member" is
        // only actionable if the player can see which one it is, and the strip
        // is now the only surface that says so -- `EB-629` drops the sentence
        // from the rules paragraph on the strength of this mark.
        var source = Source("Vfx/Prototype/SalonPanel.cs")
            .Replace("\r\n", "\n");
        Assert.Contains("front: i == 0", source);
        Assert.Contains("frame.Visible = occupied && front;", source);
    }

    // --- what a chip says -------------------------------------------------

    [Theory]
    [InlineData(SalonMember.Crabaletta, "Hydro")]
    [InlineData(SalonMember.Chevalmarin, "Hydro")]
    [InlineData(SalonMember.Usher, "Block")]
    public void The_act_word_is_the_one_the_member_tip_prints(
        SalonMember member, string word)
    {
        Assert.Equal(word, SalonPanel.ActWord(member));
    }

    [Fact]
    public void The_next_act_is_the_performance_number_and_its_word()
    {
        using var _ = new Arm();
        var seat = Stage(SalonMember.Crabaletta, SalonMember.Usher,
                         SalonMember.Chevalmarin);

        // The printed ticks, from the constants the member tips interpolate:
        // a repricing moves both surfaces or neither.
        Assert.Equal($"{SalonConstants.CrabalettaTick} Hydro",
            SalonPanel.NextAct(seat.Creature, SalonMember.Crabaletta,
                                     paid: true));
        Assert.Equal($"{SalonConstants.UsherTick} Block",
            SalonPanel.NextAct(seat.Creature, SalonMember.Usher,
                                     paid: true));
        Assert.Equal($"{SalonConstants.ChevalmarinTick} Hydro",
            SalonPanel.NextAct(seat.Creature, SalonMember.Chevalmarin,
                                     paid: true));
    }

    [Fact]
    public void The_number_is_the_one_the_performance_resolves_through()
    {
        // THE ACCEPTANCE CONDITION FROM THE ROW: the live Fanfare bonus is
        // folded into the number the way the member tips fold it. It is folded
        // because it is the SAME CALL -- `TickValue` is where the Focus term,
        // Grand Salon and the dry three-quarters all live -- not because the
        // chip repeats the arithmetic.
        using var _ = new Arm();
        var seat = Stage(SalonMember.Crabaletta);
        FurinaResources.GainFanfare(seat.Creature,
                                    SalonConstants.FocusPerFanfare);

        var folded = SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Crabaletta, paid: true);
        Assert.Equal(SalonConstants.CrabalettaTick + 1, folded);
        Assert.Equal($"{folded} Hydro",
            SalonPanel.NextAct(seat.Creature, SalonMember.Crabaletta,
                                     paid: true));

        // And the dry cut is the same one expression too: a member that cannot
        // pay acts at three-quarters, and the chip says the number it will
        // actually deal rather than the one it would like to.
        var dry = SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Crabaletta, paid: false);
        Assert.Equal($"{dry} Hydro",
            SalonPanel.NextAct(seat.Creature, SalonMember.Crabaletta,
                                     paid: false));

        var calls = Il.Calls(typeof(SalonPanel)
            .GetMethod(nameof(SalonPanel.NextAct), All)!);
        Assert.Contains(calls,
            c => c.EndsWith("SalonMemberPower.TickValue",
                            StringComparison.Ordinal));
    }

    [Fact]
    public void The_evoke_line_is_the_members_own_bow_in_the_tips_words()
    {
        // "Hydro to ALL" is CHEVALMARIN'S EVOKE and not her performance -- she
        // performs for 2 Hydro at one body -- so the strip prints it on the
        // front chip and only while the stage is full, which is the one board
        // state a deploy reaches it from.
        Assert.Equal($"Evoke {SalonConstants.CrabalettaBow} Hydro",
                     SalonPanel.EvokeAct(SalonMember.Crabaletta));
        Assert.Equal($"Evoke {SalonConstants.UsherBow} Block",
                     SalonPanel.EvokeAct(SalonMember.Usher));
        // `EB-630`: and her REFUND rides the same line. "Hydro to ALL" alone
        // was half her Evoke, and the half it dropped -- the Encore she gives
        // back -- is the number that makes replacing her a decision rather
        // than a loss. Interpolated from the constant, like the other two.
        Assert.Equal(
            $"Evoke Hydro to ALL, +{SalonConstants.ChevalmarinBowEncore} "
          + "Encore",
            SalonPanel.EvokeAct(SalonMember.Chevalmarin));

        var source = Source("Vfx/Prototype/SalonPanel.cs")
            .Replace("\r\n", "\n");
        Assert.Contains("evoke.Visible = front && full;", source);
    }

    [Fact]
    public void Every_member_has_a_short_name_and_a_face()
    {
        var faces = (IDictionary<SalonMember, string>)
            typeof(SalonPanel).GetField("Faces", All)!.GetValue(null)!;

        foreach (SalonMember member in Enum.GetValues(typeof(SalonMember)))
        {
            Assert.False(string.IsNullOrWhiteSpace(
                SalonPanel.ShortName(member)));
            // The pck art the stage's silhouettes are cut from, reused rather
            // than re-cut: no new asset and no new generator.
            Assert.True(faces.ContainsKey(member));
            Assert.StartsWith("furina/salon/member_", faces[member]);
        }
    }

    // --- the door and the funnel -----------------------------------------

    [Fact]
    public void It_is_built_and_refreshed_at_the_stages_own_door()
    {
        // ONE ELEMENT OR THE OTHER, at one door. The stage's `Setup` is the
        // `NCombatUi.Activate` postfix and its `Refresh` is the Funnel
        // Contract's own funnels; hanging the strip anywhere else would be a
        // second opinion about when a room is live.
        Assert.Contains(
            Il.Calls(typeof(SalonVisualsBridge)
                .GetMethod(nameof(SalonVisualsBridge.Setup), All)!),
            c => c.EndsWith("SalonPanel.Setup", StringComparison.Ordinal));
        Assert.Contains(
            Il.Calls(typeof(SalonVisualsBridge)
                .GetMethod(nameof(SalonVisualsBridge.Refresh), All)!),
            c => c.EndsWith("SalonPanel.Refresh",
                            StringComparison.Ordinal));
        Assert.Contains(
            Il.Calls(typeof(SalonVisualsBridge)
                .GetMethod(nameof(SalonVisualsBridge.DiscardDisplay), All)!),
            c => c.EndsWith("SalonPanel.Discard",
                            StringComparison.Ordinal));
    }

    [Fact]
    public void Nothing_polls_and_no_texture_is_held_across_a_scene()
    {
        var source = Source("Vfx/Prototype/SalonPanel.cs")
            .Replace("\r\n", "\n");

        // A per-frame `_Process` would be a second cadence, and two cadences
        // is how a display and a queue drift.
        Assert.DoesNotContain("void _Process", source);

        // `EB-222`: the engine frees a room's assets with the room, and a
        // cached `Texture2D` handed to a `TextureRect` the next combat is what
        // stuck a room and ended a run.
        Assert.Contains("ResourceLoader.Load<Texture2D>(path)", source);
        Assert.DoesNotContain("static Texture2D", source);
    }

    // --- one panel --------------------------------------------------------

    [Fact]
    public void Everything_is_inside_one_backing_rectangle()
    {
        // `EB-627`'s revision, and the reason the four widgets became one. The
        // frame showed the state a player prices a Companion play against --
        // who is in front, what it pays, whether the stage can pay -- split
        // across the creature's feet, the bottom-left corner and the status
        // strip, with the piece answering "can she pay" invisible. One group,
        // one ground: everything about the Salon is in this rectangle and
        // nothing about the Salon is anywhere else.
        var source = Source("Vfx/Prototype/SalonPanel.cs");

        Assert.Contains("Name = \"Back\"", source);
        Assert.Contains("Color = PanelBack", source);
        Assert.Contains("root.AddChildSafely(BuildResourceRow", source);
        Assert.Contains("root.AddChildSafely(BuildChip(i))", source);
        // The chips, the line and the notice are all children of the one root.
        Assert.Contains("Text(\"Notice\"", source);
    }

    [Fact]
    public void The_panel_sits_above_the_rig_and_clear_of_the_hp_band()
    {
        // THE BAND UNDER HER FEET IS NOT OURS. `NCreatureStateDisplay` draws
        // the HP bar and the block badge there, and both earlier layouts lost
        // a row to it -- the 2026-07-25 ribbon's number, then `EB-635`'s pip
        // row. The overhead region is the one MEASURED clear space on this rig
        // (`GaugeBridge`: Furina's box tops out at -280, the Burst slot is
        // -300 and draws nothing under this arm), so the panel's bottom edge
        // is that slot.
        var anchor = (Godot.Vector2)typeof(SalonPanel)
            .GetField("AnchorOffset", All)!.GetValue(null)!;

        Assert.Equal(-300f, anchor.Y + FurinaBoardScale.PanelHeight);
        Assert.True(anchor.Y < -300f);

        // AND INSIDE THE CREATURE'S OWN BOUNDS, centred: 240 is the bounds
        // width, so the panel cannot overhang into the enemy intent or the
        // targeting lanes on either side.
        Assert.Equal(-FurinaBoardScale.PanelWidth / 2f, anchor.X);
        Assert.Equal(240f, FurinaBoardScale.PanelWidth);
    }

    [Fact]
    public void Chip_zero_says_FRONT_in_a_word_and_not_only_in_a_border()
    {
        // A gold border says "this one is special" and does not say WHAT is
        // special about it -- and what is special about it is the rule a
        // Companion play acts on. `EB-629` drops "the leftmost member is the
        // front" from the rules paragraph on the strength of this, so the mark
        // has to teach the rule rather than merely point at it.
        var source = Source("Vfx/Prototype/SalonPanel.cs");

        Assert.Equal("FRONT", SalonPanel.FrontWord);
        Assert.Contains("frontLabel.Visible = front;", source);
        Assert.Contains("frontLabel.Text = FrontWord;", source);
        // And the frame is still there beside it: two channels, because the
        // dry grey eats one of them.
        Assert.Contains("frame.Visible = occupied && front;", source);
    }

    // --- source access ----------------------------------------------------

    /// <summary>A source file under `klee-mod/KleeCode`.
    /// <see cref="SparkCounterPinTests"/>' helper, verbatim.</summary>
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
