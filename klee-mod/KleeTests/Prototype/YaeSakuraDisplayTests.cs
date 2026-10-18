#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Cards.Yae;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// YAE'S SAKURA DISPLAY (pick 3 (a) of
/// <c>review/active/yae-pool-to-78-2026-10-15.md</c>, ruled 2026-10-15): the
/// view model, <see cref="YaeSakuraSlots"/>. Godot nodes cannot be built in
/// this host, so what is pinned is every decision the row draws: one slot per
/// shrine slot with the empty ones shown, kind and Level, turns as pips, a
/// number past three and an infinity mark when it never withers, a mark per
/// Annotation, the oldest outlined, and what hovering a planting card says on
/// the slot it touches. How it looks is a frame on the next deploy.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeSakuraDisplayTests : IDisposable
{
    public YaeSakuraDisplayTests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose() => YaeShrineLedger.ResetAll();

    private static YaeShrineLedger Fresh() => YaeShrineLedger.For(Seat.Yae().Creature);

    private static void Plant(YaeShrineLedger ledger, YaeSakuraKind kind,
                              int cap = YaeLaw.SakuraCap) =>
        ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.None, cap, kind);

    // ---- the row ----------------------------------------------------------

    [Fact]
    public void One_slot_per_shrine_slot_with_the_empty_ones_shown()
    {
        var ledger = Fresh();
        Plant(ledger, YaeSakuraKind.Thunder);
        var slots = YaeSakuraSlots.Slots(ledger.Standing, YaeLaw.SakuraCap, false);
        Assert.Equal(3, slots.Count);
        Assert.False(slots[0].Empty);
        Assert.True(slots[1].Empty);
        Assert.True(slots[2].Empty);
        Assert.Equal(new[] { 0, 1, 2 }, slots.Select(s => s.Slot));
    }

    [Fact]
    public void Sakura_channeling_widens_the_row_and_it_never_hides_a_standing_sakura()
    {
        Assert.Equal(5, YaeSakuraSlots.SlotCount(2, YaeLaw.SakuraCap + 2));
        Assert.Equal(3, YaeSakuraSlots.SlotCount(0, YaeLaw.SakuraCap));
        Assert.Equal(4, YaeSakuraSlots.SlotCount(4, YaeLaw.SakuraCap));
        var ledger = Fresh();
        Assert.Equal(5, YaeSakuraSlots.Slots(ledger.Standing, 5, false).Count);
    }

    [Fact]
    public void Each_sakura_shows_its_kind_and_level_and_the_oldest_alone_is_outlined()
    {
        var ledger = Fresh();
        Plant(ledger, YaeSakuraKind.Kitsune);
        Plant(ledger, YaeSakuraKind.Foxfire);
        ledger.LevelNewest(2);
        var slots = YaeSakuraSlots.Slots(ledger.Standing, YaeLaw.SakuraCap, false);
        Assert.Equal(YaeSakuraKind.Kitsune, slots[0].Kind);
        Assert.Equal(1, slots[0].Level);
        Assert.Equal(YaeSakuraKind.Foxfire, slots[1].Kind);
        Assert.Equal(3, slots[1].Level);
        Assert.Equal(new[] { true, false, false }, slots.Select(s => s.Oldest));
        // An empty shrine outlines nothing.
        Assert.DoesNotContain(YaeSakuraSlots.Slots(Array.Empty<YaeSakura>(), 3, false),
                              s => s.Oldest);
    }

    // ---- turns ------------------------------------------------------------

    [Fact]
    public void Turns_are_pips_up_to_three_then_a_number_then_infinity()
    {
        Assert.Equal((3, (string?)null, false), YaeSakuraSlots.Turns(3, false));
        Assert.Equal((1, (string?)null, false), YaeSakuraSlots.Turns(1, false));
        Assert.Equal((0, (string?)"5", false), YaeSakuraSlots.Turns(5, false));
        Assert.Equal((0, (string?)YaeSakuraSlots.InfinityMark, true),
                     YaeSakuraSlots.Turns(2, true));
        Assert.Equal("∞", YaeSakuraSlots.InfinityMark);
    }

    [Fact]
    public void Eternity_and_deadline_extension_draw_the_infinity_mark()
    {
        var ledger = Fresh();
        Plant(ledger, YaeSakuraKind.Thunder);
        Plant(ledger, YaeSakuraKind.Thunder);
        ledger.Extend(2);   // 5 turns each
        Assert.True(ledger.EditOne(ledger.Standing[1], YaeAnnotation.DeadlineExtension));

        var plain = YaeSakuraSlots.Slots(ledger.Standing, 3, eternal: false);
        Assert.Equal("5", plain[0].TurnsText);
        Assert.Equal(0, plain[0].Pips);
        Assert.True(plain[1].Infinite);

        var eternal = YaeSakuraSlots.Slots(ledger.Standing, 3, eternal: true);
        Assert.All(eternal.Take(2), s => Assert.Equal(YaeSakuraSlots.InfinityMark, s.TurnsText));
        Assert.False(eternal[2].Infinite);   // the empty slot draws no timer
    }

    // ---- annotations ------------------------------------------------------

    [Fact]
    public void A_mark_per_annotation_in_the_order_written()
    {
        var ledger = Fresh();
        Plant(ledger, YaeSakuraKind.Thunder);
        var s = ledger.Standing[0];
        Assert.True(ledger.EditOne(s, YaeAnnotation.FoxFire));
        Assert.True(ledger.EditOne(s, YaeAnnotation.RedInk));
        Assert.False(ledger.EditOne(s, YaeAnnotation.RedInk));   // a second copy adds nothing
        var view = YaeSakuraSlots.Slots(ledger.Standing, 3, false)[0];
        Assert.Equal(new[] { YaeAnnotation.FoxFire, YaeAnnotation.RedInk }, view.Marks);
        Assert.Equal(new[] { "F", "R" }, view.Marks.Select(YaeSakuraSlots.MarkLetter));
        Assert.Equal("D", YaeSakuraSlots.MarkLetter(YaeAnnotation.DeadlineExtension));
    }

    // ---- the planting card's preview --------------------------------------

    [Fact]
    public void Into_room_a_plant_marks_the_next_empty_slot()
    {
        var ledger = Fresh();
        Plant(ledger, YaeSakuraKind.Thunder);
        var preview = YaeSakuraSlots.Preview(ledger.Standing, 3, YaePlantShape.Plant,
                                             new[] { YaeSakuraKind.Thunder });
        Assert.Equal(new[] { YaeSlotPreview.None, YaeSlotPreview.Plants, YaeSlotPreview.None },
                     preview);
        Assert.Equal("Plants here", YaeSakuraSlots.PreviewText(preview[1]));
    }

    [Fact]
    public void Into_a_full_shrine_the_same_kind_refreshes_the_sakura_closest_to_withering()
    {
        var ledger = Fresh();
        Plant(ledger, YaeSakuraKind.Thunder);
        Plant(ledger, YaeSakuraKind.Thunder);
        Plant(ledger, YaeSakuraKind.Thunder);
        ledger.ExtendOldest(2);   // the oldest now lasts longest: slot 2 is next to wither
        var target = ledger.NextToWither();
        var preview = YaeSakuraSlots.Preview(ledger.Standing, 3, YaePlantShape.Plant,
                                             new[] { YaeSakuraKind.Thunder });
        Assert.Equal(YaeSlotPreview.Refreshes,
                     preview[ledger.Standing.ToList().IndexOf(target!)]);
        Assert.Equal(1, preview.Count(p => p == YaeSlotPreview.Refreshes));
        Assert.Equal("Refreshes this Sakura",
                     YaeSakuraSlots.PreviewText(YaeSlotPreview.Refreshes));
    }

    [Fact]
    public void Into_a_full_shrine_another_kind_replaces_it()
    {
        var ledger = Fresh();
        Plant(ledger, YaeSakuraKind.Thunder);
        Plant(ledger, YaeSakuraKind.Thunder);
        Plant(ledger, YaeSakuraKind.Thunder);
        var preview = YaeSakuraSlots.Preview(ledger.Standing, 3, YaePlantShape.Plant,
                                             new[] { YaeSakuraKind.Kitsune });
        Assert.Equal(new[] { YaeSlotPreview.Replaces, YaeSlotPreview.None, YaeSlotPreview.None },
                     preview);
        Assert.Equal("Replaces this Sakura", YaeSakuraSlots.PreviewText(preview[0]));
        // The rule the preview walks is the ledger's: the plant replaces slot 1.
        var first = ledger.Standing[0];
        Plant(ledger, YaeSakuraKind.Kitsune);
        Assert.DoesNotContain(first, ledger.Standing);
    }

    [Fact]
    public void Two_plants_walk_one_at_a_time()
    {
        var ledger = Fresh();
        Plant(ledger, YaeSakuraKind.Thunder);
        Plant(ledger, YaeSakuraKind.Kitsune);
        // Twin Sakura into one empty slot: the first fills it, the second
        // meets a full shrine whose oldest (closest to withering on the tie)
        // is a Sakura and refreshes it.
        var preview = YaeSakuraSlots.Preview(ledger.Standing, 3, YaePlantShape.Plant,
                                             YaeSakuraSlots.PlantsOf(YaePlantShape.Plant,
                                                 YaeSakuraKind.Thunder, 2, ledger.Standing, 3));
        Assert.Equal(new[] { YaeSlotPreview.Refreshes, YaeSlotPreview.None, YaeSlotPreview.Plants },
                     preview);
    }

    [Fact]
    public void Replanting_replaces_the_oldest_and_genre_shift_fills_the_missing_kinds()
    {
        var ledger = Fresh();
        Plant(ledger, YaeSakuraKind.Foxfire);
        Plant(ledger, YaeSakuraKind.Thunder);
        var replant = YaeSakuraSlots.Preview(ledger.Standing, 3, YaePlantShape.Replant,
            YaeSakuraSlots.PlantsOf(YaePlantShape.Replant, YaeSakuraKind.Thunder, 1,
                                    ledger.Standing, 3));
        Assert.Equal(new[] { YaeSlotPreview.Replaces, YaeSlotPreview.None, YaeSlotPreview.None },
                     replant);

        Assert.Equal(new[] { YaeSakuraKind.Kitsune },
                     YaeSakuraSlots.PlantsOf(YaePlantShape.PlantMissing, YaeSakuraKind.Thunder,
                                             1, ledger.Standing, 3));
        Assert.Equal(new[] { YaeSakuraKind.Thunder },
                     YaeSakuraSlots.PlantsOf(YaePlantShape.PlantUntilFull, YaeSakuraKind.Thunder,
                                             1, ledger.Standing, 3));
        Assert.Empty(YaeSakuraSlots.PlantsOf(YaePlantShape.Replant, YaeSakuraKind.Thunder, 1,
                                             Array.Empty<YaeSakura>(), 3));
    }

    [Fact]
    public void The_preview_lands_on_the_row_and_a_card_that_plants_nothing_previews_nothing()
    {
        var yae = Seat.Yae().Creature;
        var ledger = YaeShrineLedger.For(yae);
        Plant(ledger, YaeSakuraKind.Thunder);
        Plant(ledger, YaeSakuraKind.Thunder);
        Plant(ledger, YaeSakuraKind.Thunder);

        // Guardian of Narukami plants a Kitsune Sakura at Level 3: into a
        // full shrine of Sakura it replaces the one closest to withering.
        var guardian = new ProtoYmGuardianOfNarukami();
        Assert.Equal(YaePlantShape.PlantLevel, guardian.SakuraPlantShape);
        Assert.Equal(YaeSakuraKind.Kitsune, guardian.SakuraPlantKind);
        var preview = YaeSakuraSlots.PreviewFor(guardian, yae);
        Assert.NotNull(preview);
        var slots = YaeSakuraSlots.Slots(ledger.Standing, 3, false, preview);
        Assert.Equal(YaeSlotPreview.Replaces, slots[0].Preview);

        Assert.Null(YaeSakuraSlots.PreviewFor(new ProtoYmSakuraChanneling(), yae));
    }

    [Fact]
    public void Every_planting_card_says_how_it_plants()
    {
        foreach (var card in new ISakuraPlanterCard[]
                 {
                     new ProtoYmThunderPetal(), new ProtoYmTwinSakura(),
                     new ProtoYmReplanting(), new ProtoYmGenreShift(),
                     new ProtoYmNarukamiBloom(), new YakanEvocationSesshouSakura(),
                 })
        {
            Assert.IsAssignableFrom<ISakuraPlantShapeCard>(card);
        }
        Assert.Equal(YaePlantShape.Replant, new ProtoYmReplanting().SakuraPlantShape);
        Assert.Equal(YaePlantShape.PlantMissing, new ProtoYmGenreShift().SakuraPlantShape);
        Assert.Equal(YaePlantShape.PlantUntilFull, new ProtoYmNarukamiBloom().SakuraPlantShape);
        Assert.Equal(YaeSakuraKind.Foxfire, new YakanEvocationSesshouSakura().SakuraPlantKind);
    }

    // ---- the hover --------------------------------------------------------

    [Fact]
    public void A_slot_hover_gives_one_line_rules()
    {
        foreach (var line in new[] { YaeSakuraSlots.RulesLine, YaeSakuraSlots.EmptyLine })
        {
            Assert.DoesNotContain("\n", line);
            Assert.True(line.Length <= 120, line);
        }
        Assert.Contains("oldest first", YaeSakuraSlots.RulesLine);
    }

    [Fact]
    public void Each_kind_has_its_own_glyph()
    {
        var glyphs = new[] { YaeSakuraKind.Thunder, YaeSakuraKind.Foxfire, YaeSakuraKind.Kitsune }
            .Select(YaeSakuraSlots.GlyphPathFor).ToList();
        Assert.Equal(3, glyphs.Distinct().Count());
        Assert.Equal("yae/powers/sakura.png", glyphs[0]);
    }
}
