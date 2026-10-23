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
        Assert.Equal(new[] { 0, -1, -1 }, slots.Select(s => s.Index));
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
        ledger.LevelMostTurnsLeft(2);
        var slots = YaeSakuraSlots.Slots(ledger.Standing, YaeLaw.SakuraCap, false);
        // Most turns left first, the newest on the tie: the Foxfire.
        Assert.Equal(YaeSakuraKind.Foxfire, slots[0].Kind);
        Assert.Equal(3, slots[0].Level);
        Assert.Equal(YaeSakuraKind.Kitsune, slots[1].Kind);
        Assert.Equal(1, slots[1].Level);
        // The outline follows the oldest, which acts first, wherever it stands.
        Assert.Equal(new[] { false, true, false }, slots.Select(s => s.Oldest));
        // An empty shrine outlines nothing.
        Assert.DoesNotContain(YaeSakuraSlots.Slots(Array.Empty<YaeSakura>(), 3, false),
                              s => s.Oldest);
    }

    // ---- the order (the user, 2026-10-23) ---------------------------------

    [Fact]
    public void The_row_puts_the_most_turns_left_first_and_the_closest_to_withering_last()
    {
        var ledger = Fresh();
        Plant(ledger, YaeSakuraKind.Thunder);   // A, oldest
        Plant(ledger, YaeSakuraKind.Foxfire);   // B
        Plant(ledger, YaeSakuraKind.Kitsune);   // C, newest
        var a = ledger.Standing[0];
        var b = ledger.Standing[1];
        var c = ledger.Standing[2];
        Assert.True(ledger.EditOne(a, YaeAnnotation.DeadlineExtension));

        // The wither order read backwards: A (never withers), then C and B
        // tied on turns, the newest first.
        Assert.Equal(new[] { 0, 2, 1 }, YaeSakuraSlots.DisplayOrder(ledger.Standing));
        var slots = YaeSakuraSlots.Slots(ledger.Standing, 3, false);
        Assert.Equal(new[] { 0, 2, 1 }, slots.Select(s => s.Index));
        Assert.Equal(new[] { YaeSakuraKind.Thunder, YaeSakuraKind.Kitsune, YaeSakuraKind.Foxfire },
                     slots.Select(s => s.Kind));
        Assert.Same(a, ledger.LastToWither());
        Assert.Same(b, ledger.NextToWither());
        Assert.Equal(ledger.WitherOrder().Reverse().Select(s => ledger.Standing.ToList().IndexOf(s)),
                     slots.Select(s => s.Index));
        // Display only: the planting order (the order they act) is untouched.
        Assert.Equal(new[] { a, b, c }, ledger.Standing);
    }

    [Fact]
    public void Dawn_prayers_sakura_is_always_the_first_slot_twin_sakuras_kitsune_on_the_tie()
    {
        // Twin Sakura plants a Sakura then a Kitsune Sakura, both 3 turns:
        // the "newest" on the tie is the Kitsune, and the row now shows it.
        var ledger = Fresh();
        Plant(ledger, YaeSakuraKind.Thunder);
        Plant(ledger, YaeSakuraKind.Kitsune);
        var slots = YaeSakuraSlots.Slots(ledger.Standing, 3, false);
        Assert.Equal(YaeSakuraKind.Kitsune, slots[0].Kind);
        Assert.Same(ledger.LastToWither(), ledger.Standing[slots[0].Index]);
        Assert.Equal(YaeSakuraKind.Thunder, slots[1].Kind);
        Assert.True(slots[1].Oldest);

        // A fresh plant has the most turns left: it takes the first slot.
        ledger.Tick();
        Plant(ledger, YaeSakuraKind.Foxfire);
        Assert.Equal(new[] { 2, 1, 0 }, YaeSakuraSlots.DisplayOrder(ledger.Standing));
    }

    [Fact]
    public void A_preview_lands_on_the_slot_that_draws_its_sakura()
    {
        var ledger = Fresh();
        Plant(ledger, YaeSakuraKind.Thunder);   // A
        Plant(ledger, YaeSakuraKind.Thunder);   // B
        Plant(ledger, YaeSakuraKind.Thunder);   // C
        Assert.True(ledger.EditOne(ledger.Standing[0], YaeAnnotation.DeadlineExtension));
        // A Kitsune into the full shrine replaces B: no Deadline Extension,
        // the fewest turns, the older on the tie.
        var preview = YaeSakuraSlots.Preview(ledger.Standing, 3, YaePlantShape.Plant,
                                             new[] { YaeSakuraKind.Kitsune });
        Assert.Equal(YaeSlotPreview.Replaces, preview[1]);
        var slots = YaeSakuraSlots.Slots(ledger.Standing, 3, false, preview);
        var shown = Assert.Single(slots, s => s.Preview == YaeSlotPreview.Replaces);
        Assert.Equal(1, shown.Index);
        Assert.Equal(2, shown.Slot);   // the end of the row: closest to withering
        Assert.Same(ledger.NextToWither(), ledger.Standing[shown.Index]);
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
        // Deadline Extension never withers: it leads the row.
        Assert.True(plain[0].Infinite);
        Assert.Equal(1, plain[0].Index);
        Assert.Equal("5", plain[1].TurnsText);
        Assert.Equal(0, plain[1].Pips);

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
        ledger.ExtendMostTurnsLeft(2);   // the oldest now lasts longest: slot 2 is next to wither
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
        // The oldest, closest to withering on the tie, is the row's last slot.
        Assert.Equal(YaeSlotPreview.Replaces, slots[2].Preview);
        Assert.True(slots[2].Oldest);
        Assert.Equal(1, slots.Count(s => s.Preview == YaeSlotPreview.Replaces));

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
