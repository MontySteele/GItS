using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Entities.Creatures;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-639`, `EB-640`, `EB-641`, `EB-644`: THE PANEL FITS ITS OWN WORDS, SAYS
/// THEM UNAMBIGUOUSLY, IS ONE OBJECT, AND LEAVES WITH THE FIGHT.
///
/// THE FIND. The first live frames of the panel, `0.2.2927+proto`, 2026-09-07.
/// Beat 1 drew "5 Hydro3 Block5 Hydro" -- three chips 70 pixels wide carrying
/// text wider than that, so neighbouring numbers ran together across the gaps
/// and the front chip's Evoke line landed on top of the reduced-performance
/// note. Beat 3 drew the whole panel again, dimmed, BEHIND the Loot dialog: the
/// Evoke had killed the last enemy and the stage was still being described for
/// a combat that no longer existed. [USER]'s own instruction on the placement
/// was "keep this placement and refine the panel", so nothing here moves the
/// group; what changes is that the box is measured, the words are shorter and
/// unambiguous, and the node has a teardown.
///
/// WHAT IS REAL HERE. The FIT, exhaustively: every member, every effect string
/// a stage can reach, at every chip count the panel will ever draw, measured
/// through the same expression the paint lays out with. The row geometry, which
/// is the vertical half of the same rule. The words themselves. And the
/// teardown's wiring, by call set.
///
/// WHAT IS STRUCTURAL, and labelled. Godot nodes are process death in this host
/// (KleeTests README, the headless boundary), so the drawing is pinned as
/// source text and call sets rather than by building the tree.
///
/// WHAT NOTHING HERE CAN VERIFY: the look. Whether the chips read at combat
/// scale, whether the portraits carry "seahorse, crab, seahorse" at a glance,
/// whether the contrast holds against a lit forest. That is a frame on the next
/// `+proto` deploy and no assertion in this file claims it.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class SalonPanelFitTests
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

        internal Arm()
        {
            FurinaReframe.Enabled = true;
            FurinaReframe.ManualEnabled = true;
            FurinaReframe.EvokeEnabled = true;
            FurinaReframe.MeterEnabled = true;
            FurinaReframe.SpotlightEnabled = true;
            FurinaReframe.BurstEnabled = true;
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

    private static IEnumerable<SalonMember> Members() =>
        Enum.GetValues(typeof(SalonMember)).Cast<SalonMember>();

    // === 1. the ruler ====================================================

    [Fact]
    public void The_width_table_over_estimates_and_never_under_estimates()
    {
        // THE ERROR RUNS ONE WAY ON PURPOSE. There is no live font in this host
        // and none at the moment the panel is built, so the fit is computed
        // from a documented character table -- and a table that is too generous
        // can only make a box too wide or a font one point too small, while one
        // that is too mean is the collision `EB-639` filed.
        Assert.True(FurinaBoardScale.WideCharEm
                    > FurinaBoardScale.NarrowCharEm);
        Assert.True(FurinaBoardScale.NarrowCharEm > FurinaBoardScale.PunctEm);
        Assert.True(FurinaBoardScale.PunctEm > FurinaBoardScale.SpaceEm);

        // Every unknown character is charged the WIDE rate, so an unfamiliar
        // glyph cannot smuggle a collision in.
        Assert.Equal(FurinaBoardScale.WideCharEm * 10f,
                     FurinaBoardScale.TextWidth("·", 10), 3);
        Assert.Equal(FurinaBoardScale.WideCharEm * 10f,
                     FurinaBoardScale.TextWidth("8", 10), 3);
        Assert.Equal(FurinaBoardScale.NarrowCharEm * 10f,
                     FurinaBoardScale.TextWidth("a", 10), 3);

        // Empty, null and a dead font size are zero rather than a throw: this
        // runs on a display path.
        Assert.Equal(0f, FurinaBoardScale.TextWidth(null, 13));
        Assert.Equal(0f, FurinaBoardScale.TextWidth("", 13));
        Assert.Equal(0f, FurinaBoardScale.TextWidth("Encore", 0));

        // And it is monotone in the size, which is what makes the step-down
        // terminate at a fitting size rather than oscillate.
        Assert.True(FurinaBoardScale.TextWidth("Chevalmarin", 13)
                    > FurinaBoardScale.TextWidth("Chevalmarin", 12));
    }

    [Fact]
    public void A_string_is_stepped_down_until_it_fits_and_never_below_one()
    {
        Assert.Equal(13, FurinaBoardScale.FitFontSize("Encore 4", 13, 1000f));
        Assert.True(FurinaBoardScale.FitFontSize("Encore 4", 13, 40f) < 13);
        Assert.True(FurinaBoardScale.TextWidth(
            "Encore 4", FurinaBoardScale.FitFontSize("Encore 4", 13, 40f))
            <= 40f);
        // A box of nothing still terminates, at 1.
        Assert.Equal(1, FurinaBoardScale.FitFontSize("Encore 4", 13, 0f));
    }

    // === 2. nothing overlaps, horizontally ===============================

    [Fact]
    public void Every_reachable_effect_string_fits_the_chip_it_is_drawn_in()
    {
        // `EB-639`'s pin, and it is EXHAUSTIVE rather than a sample: every
        // member, every performance number a Fanfare-fed stage can reach up to
        // three digits, at every chip count the panel will ever draw -- from a
        // stage of one to the five an upgraded Box Seats reaches, where each
        // chip is a fifth of the same box. The measurement is the expression
        // the paint lays out with, so a passing pin is a fitting drawing.
        for (var slots = 1; slots <= SalonPanel.MaxChips; slots++)
        {
            var inner = SalonPanel.ChipInnerWidth(slots);
            Assert.True(inner > 0f, $"a chip of {slots} has no room at all");

            foreach (var member in Members())
            {
                foreach (var value in new[] { 0, 3, 9, 14, 88, 128, 999 })
                {
                    var digits = value.ToString();
                    var (number, unit) =
                        SalonPanel.EffectSizes(digits, member, inner);
                    var width = SalonPanel.EffectRowWidth(
                        digits, member, number, unit);

                    Assert.True(
                        width <= inner,
                        $"{member} '{digits} {SalonPanel.EffectUnit(member)}' "
                      + $"is {width} wide in a {inner} chip at {slots} slots");
                    Assert.True(number >= unit,
                        "the tiers are a hierarchy and stay one when they "
                      + "shrink");
                }
            }
        }
    }

    [Fact]
    public void Every_name_and_the_front_word_fit_the_chip_too()
    {
        var inner = SalonPanel.ChipInnerWidth(SalonConstants.MemberSlots);

        foreach (var member in Members())
        {
            var name = SalonPanel.ShortName(member);
            Assert.True(
                FurinaBoardScale.TextWidth(
                    name, FurinaBoardScale.Tier2FontSize) <= inner,
                $"{name} does not fit its chip");
        }

        Assert.True(
            FurinaBoardScale.TextWidth(
                SalonPanel.FrontWord, FurinaBoardScale.Tier3FontSize) <= inner);
    }

    [Fact]
    public void Every_header_and_footer_string_fits_the_slot_row()
    {
        // `EB-644`. THE SLOT ROW IS THE BOX, and no message may widen it: the
        // third pass let the widest footer set the panel's width, which is the
        // "uncontrolled expansion" GPT's review named. So the width is a
        // function of the chip count alone, and every header and footer string
        // is measured against it AT ITS OWN TIER -- no step-down -- and would
        // be shortened here, at design time, rather than move the panel.
        using var _ = new Arm();
        var inner = SalonPanel.InnerWidth;
        var size = FurinaBoardScale.Tier2FontSize;

        Assert.Equal(
            FurinaBoardScale.PanelWidthFor(SalonConstants.MemberSlots,
                                           SalonPanel.ChipContentWidth),
            SalonPanel.PanelWidth);
        Assert.Equal(SalonPanel.PanelWidth - 2f * FurinaBoardScale.PanelPad,
                     inner);
        // The width function takes the chip count and the chip content and
        // NOTHING about the header or the footer.
        Assert.Equal(2, typeof(FurinaBoardScale)
            .GetMethod("PanelWidthFor")!.GetParameters().Length);

        foreach (var member in Members())
        {
            var text = SalonPanel.ReplaceText(member);
            Assert.True(
                FurinaBoardScale.TextWidth(text, size) <= inner,
                $"'{text}' does not fit the slot row at tier 2");
        }

        foreach (var encore in new[] { 0, 1, 99 })
        {
            var seat = Stage(encore, SalonMember.Crabaletta);
            FurinaResources.GainFanfare(seat.Creature, 999);
            foreach (var text in new[]
                     {
                         SalonPanel.EncoreText(seat.Creature),
                         SalonPanel.MeterText(seat.Creature),
                         SalonPanel.StepText(seat.Creature),
                     })
            {
                Assert.True(
                    FurinaBoardScale.TextWidth(text, size) <= inner,
                    $"'{text}' does not fit the slot row at tier 2");
            }
        }

        // And the footer is drawn at the row's width, on the panel's ground,
        // never sized to its own text or given a strip of its own.
        var source = Source("Vfx/Prototype/SalonPanel.cs");
        Assert.DoesNotContain("FootBack", source);
        Assert.DoesNotContain("FooterContentWidth", source);
        Assert.Contains("InnerWidth, FurinaBoardScale.FooterRowHeight", source);
    }

    [Fact]
    public void The_two_header_lines_fit_the_panel_at_reachable_values()
    {
        using var _ = new Arm();
        var inner = SalonPanel.PanelWidth - 2f * FurinaBoardScale.PanelPad;
        var size = FurinaBoardScale.Tier2FontSize;

        foreach (var encore in new[] { 0, 1, 9, 99 })
        {
            var seat = Stage(encore, SalonMember.Crabaletta);
            FurinaResources.GainFanfare(seat.Creature, 990);

            var pips = FurinaBoardScale.TextWidth(
                          SalonPanel.EncoreText(seat.Creature), size)
                     + FurinaBoardScale.PipStripGap
                     + SalonPanel.MaxPips * (FurinaBoardScale.PipWidth
                                             + FurinaBoardScale.PipGap)
                     + FurinaBoardScale.TextWidth(
                         SalonPanel.OverflowText(seat.Creature),
                         FurinaBoardScale.Tier3FontSize);

            Assert.True(pips <= inner,
                $"line 1 at Encore {encore} is {pips} wide in {inner}");
            Assert.True(
                FurinaBoardScale.TextWidth(
                    SalonPanel.MeterText(seat.Creature), size) <= inner);
        }
    }

    // === 3. nothing overlaps, vertically =================================

    [Fact]
    public void Every_row_starts_at_or_below_the_previous_ones_bottom_edge()
    {
        // The vertical half of `EB-639`. The frame showed the Evoke line and
        // the reduced-performance note sharing a band; every row now has its
        // own Y and its own height, and this is the arithmetic that says so.
        Assert.True(FurinaBoardScale.MeterRowY
                    >= FurinaBoardScale.ResourceRowY
                     + FurinaBoardScale.ResourceRowHeight);
        Assert.True(FurinaBoardScale.ChipsRowY
                    >= FurinaBoardScale.MeterRowY
                     + FurinaBoardScale.MeterRowHeight);
        Assert.True(FurinaBoardScale.FooterRowY
                    >= FurinaBoardScale.ChipsRowY
                     + FurinaBoardScale.ChipHeight);
        // And the box holds the last row.
        Assert.True(FurinaBoardScale.PanelHeight
                    >= FurinaBoardScale.FooterRowY
                     + FurinaBoardScale.FooterRowHeight);

        // ONE RHYTHM (`EB-644`): the same gap above the chips as below them,
        // the same inset on every row, and the footer is the last row -- no
        // notice hangs under it.
        Assert.Equal(FurinaBoardScale.MeterRowY + FurinaBoardScale.MeterRowHeight
                         + FurinaBoardScale.RowGap,
                     FurinaBoardScale.ChipsRowY);
        Assert.Equal(FurinaBoardScale.ChipsRowY + FurinaBoardScale.ChipHeight
                         + FurinaBoardScale.RowGap,
                     FurinaBoardScale.FooterRowY);
        Assert.Equal(FurinaBoardScale.PanelPad, FurinaBoardScale.ResourceRowY);
        Assert.Equal(FurinaBoardScale.FooterRowY + FurinaBoardScale.FooterRowHeight
                         + FurinaBoardScale.PanelPad,
                     FurinaBoardScale.PanelHeight);
        Assert.Null(typeof(FurinaBoardScale).GetField("NoticeRowY"));

        // The chip's own rows are the chip's height, exactly.
        Assert.Equal(
            FurinaBoardScale.FaceHeight + 2f + FurinaBoardScale.NameRowHeight
                + FurinaBoardScale.ActRowHeight
                + FurinaBoardScale.FrontRowHeight,
            FurinaBoardScale.ChipHeight);
    }

    [Fact]
    public void The_chips_tile_with_a_gap_and_never_into_each_other()
    {
        for (var slots = 1; slots <= SalonPanel.MaxChips; slots++)
        {
            var chip = FurinaBoardScale.ChipWidthFor(
                SalonPanel.PanelWidth, slots, SalonPanel.ChipContentWidth);
            var group = slots * chip + (slots - 1) * FurinaBoardScale.ChipGap;

            Assert.True(chip > 0f);
            Assert.True(
                group <= SalonPanel.PanelWidth - 2f * FurinaBoardScale.PanelPad
                       + 0.01f,
                $"{slots} chips overflow the box");
        }
    }

    [Fact]
    public void The_reduced_word_sits_beside_the_encore_number()
    {
        // `EB-644`. "Reduced performance" hung under the footer on a row of
        // its own -- a fourth widget. The condition now sits beside its cause:
        // the Encore line says "Encore 0 · Reduced", in the reduced tint, and
        // there is no notice row at all.
        using var _ = new Arm();

        Assert.Equal("Encore 0 · Reduced",
                     SalonPanel.EncoreText(Stage(0, SalonMember.Usher).Creature));
        Assert.Equal("Encore 1",
                     SalonPanel.EncoreText(Stage(1, SalonMember.Usher).Creature));

        var source = Source("Vfx/Prototype/SalonPanel.cs");
        Assert.DoesNotContain("Notice", source);
        Assert.Contains("paid ? StsColors.cream : ReducedText", source);
    }

    [Fact]
    public void The_three_bands_start_at_one_inset_and_stand_on_one_ground()
    {
        // `EB-644`'s composition, as the drawing declares it: the chip group
        // starts at the panel's inset like every other row (it was centred in
        // a box the footer could widen), the header and the footer have no
        // ground of their own, and a hairline sits in each row gap so the
        // bands read as sections of one object.
        var source = Source("Vfx/Prototype/SalonPanel.cs");
        Assert.Contains("var left = FurinaBoardScale.PanelPad;", source);
        Assert.Contains("Hairline(\"RuleTop\"", source);
        Assert.Contains("Hairline(\"RuleBottom\"", source);
        Assert.Contains("root.AddChildSafely(BuildFooter());", source);
        // TWO `Back` rects in the whole file: the panel's and the chip's. The
        // header and the footer add none.
        Assert.Equal(2, source.Split("Name = \"Back\"").Length - 1);
    }

    // === 4. the words ====================================================

    [Fact]
    public void The_element_is_a_glyph_and_the_unit_is_a_word()
    {
        // `EB-641` point 2, and the glyph is the one the cards already wear --
        // no new asset, no second spelling of "Hydro".
        Assert.Equal(Element.Hydro,
                     SalonPanel.ElementOf(SalonMember.Crabaletta));
        Assert.Equal(Element.Hydro,
                     SalonPanel.ElementOf(SalonMember.Chevalmarin));
        Assert.Equal(Element.None, SalonPanel.ElementOf(SalonMember.Usher));

        // The card face's own table, by reflection because it is internal to
        // the mod: one glyph, declared once.
        var iconPathFor = typeof(SalonPanel).Assembly
            .GetType("KleeMod.Vfx.ElementBadge")!
            .GetMethod("IconPathFor", All)!;
        Assert.Equal("klee/powers/aura_hydro.png",
                     iconPathFor.Invoke(null, new object?[] { Element.Hydro }));
        Assert.Null(iconPathFor.Invoke(null, new object?[] { Element.None }));

        var source = Source("Vfx/Prototype/SalonPanel.cs")
            .Replace("\r\n", "\n");
        Assert.Contains("ElementBadge.IconPathFor(element)", source);
        // The Usher gets no glyph, because Block is not elemental.
        Assert.Contains("element == Element.None ? 0f : unitSize", source);
    }

    [Fact]
    public void No_string_on_the_panel_is_a_sentence()
    {
        // [USER]'s worry, in the row: too many words on the panel. Every string
        // is a label, a number and a unit, or a clause -- never a sentence, and
        // nothing carries a full stop.
        using var _ = new Arm();
        var seat = Stage(4, SalonMember.Chevalmarin, SalonMember.Crabaletta,
                         SalonMember.Usher);
        FurinaResources.GainFanfare(seat.Creature, 15);

        var dry = Stage(0, SalonMember.Usher);
        var strings = new List<string>
        {
            SalonPanel.EncoreText(seat.Creature),
            SalonPanel.EncoreText(dry.Creature),
            SalonPanel.MeterText(seat.Creature),
            SalonPanel.StepText(seat.Creature),
            SalonPanel.FrontTip,
        };
        strings.AddRange(SalonPanel.SlotWords);
        foreach (var member in Members())
        {
            strings.Add(SalonPanel.ShortName(member));
            strings.Add(SalonPanel.EffectText(seat.Creature, member, true));
            strings.Add(SalonPanel.ReplaceText(member));
        }

        foreach (var text in strings)
        {
            Assert.DoesNotContain(".", text);
            // SEVEN, and the only string that reaches it is Chevalmarin's
            // footer -- a price with two halves, both of which are the
            // decision. Everything else is four words or fewer.
            Assert.True(text.Split(' ').Length <= 7, text);
        }

        // And the two header lines are the shapes the row asked for.
        Assert.Equal("Encore 4", SalonPanel.EncoreText(seat.Creature));
        Assert.Equal("Fanfare 15 · Bonus +1",
                     SalonPanel.MeterText(seat.Creature));
        // And the footnote names the bonus the NEXT threshold buys
        // (`EB-644`): "+1 at 20" beside 15 read as the bonus already held.
        Assert.Equal("Bonus +2 at 20", SalonPanel.StepText(seat.Creature));
    }

    [Fact]
    public void The_overflow_only_speaks_when_the_strip_runs_out()
    {
        using var _ = new Arm();
        var cost = SalonConstants.TickEncoreCost;

        Assert.Equal(string.Empty, SalonPanel.OverflowText(
            Stage(0, SalonMember.Usher).Creature));
        Assert.Equal(string.Empty, SalonPanel.OverflowText(
            Stage(SalonPanel.MaxPips * cost, SalonMember.Usher).Creature));
        // Past the strip the count carries on in a "+n" rather than the strip
        // quietly claiming to be the number.
        Assert.Equal("+2", SalonPanel.OverflowText(
            Stage((SalonPanel.MaxPips + 2) * cost, SalonMember.Usher)
                .Creature));
    }

    [Fact]
    public void The_portraits_are_bigger_inside_the_wider_chips()
    {
        // `EB-641` point 5. "Seahorse, crab, seahorse" has to read at a glance,
        // and the first draw gave the face a 30-pixel band inside a 70-pixel
        // chip. The face is now the widest thing in the chip and half its
        // height; the name under it is the other half of recognition.
        Assert.True(FurinaBoardScale.FaceHeight >= 46f);
        Assert.True(SalonPanel.ChipContentWidth > 70f);

        var source = Source("Vfx/Prototype/SalonPanel.cs")
            .Replace("\r\n", "\n");
        Assert.Contains(
            "face.Size = new Vector2(width, FurinaBoardScale.FaceHeight);",
            source);
        Assert.Contains("name.Text = ShortName(who);", source);
    }

    // === 5. the panel does not outlive the fight =========================

    [Fact]
    public void The_panel_is_torn_down_by_node_at_the_combat_ui_hook()
    {
        // `EB-640`. The room's VFX container survives into the reward screen by
        // design -- the creature is still drawn behind the Loot dialog -- so
        // the panel has to free ITSELF, and it does it the way every other HUD
        // element in this tree does: by asking for a child this file named.
        // Naming a seat here is the shape that ended two blind sessions
        // (`EB-225`), which is why the teardown takes no arguments at all.
        var hide = typeof(SalonPanel).GetMethod("Hide", All);
        Assert.NotNull(hide);
        Assert.Empty(hide!.GetParameters());

        var source = Source("Vfx/Prototype/SalonPanel.cs")
            .Replace("\r\n", "\n");
        Assert.Contains(
            "container.FindChild(RootName, recursive: true, owned: false)",
            source);
        Assert.Contains("node.QueueFree();", source);
        // On the game's own hook, the one `SparkCounter` uses.
        Assert.Contains(
            "[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Deactivate))]",
            source);
        Assert.Contains("SalonPanel.Hide();", source);
        // And the exemption from the patch-scope lint carries its reason.
        var marker = source.Split('\n')
            .First(line => line.Contains("lint: no-seat:"));
        Assert.True(marker.Trim().Length > "// lint: no-seat:".Length + 10,
                    "the no-seat exemption must carry a reason");
    }

    [Fact]
    public void And_at_furinas_own_combat_end_hooks_before_the_reward_screen()
    {
        // The second door, and the one the filed frame needs: `NCombatUi`
        // stands down on a room change, but a VICTORY opens the reward screen
        // from inside `EndCombatInternal`, and both of the base game's end
        // hooks reach the same teardown from there.
        foreach (var name in new[] { "AfterCombatEnd", "AfterCombatVictory" })
        {
            var hook = typeof(FurinaResourceHooks).GetMethod(name, All);
            Assert.NotNull(hook);
            Assert.Contains(
                Il.Calls(hook!),
                c => c.EndsWith("SalonVisualsBridge.Teardown",
                                StringComparison.Ordinal));
        }

        // The bridge is the one door, on the arm's own switch: off the arm
        // there is no panel and the shipped stage is untouched.
        var bridge = Source("Vfx/SalonVisualsBridge.cs").Replace("\r\n", "\n");
        Assert.Contains("public static void Teardown()", bridge);
        Assert.Contains("#if PROTOTYPE_CARDS\n        SalonPanel.Hide();",
                        bridge);
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
