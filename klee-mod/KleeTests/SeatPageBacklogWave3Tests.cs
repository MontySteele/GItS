using System.Collections.Generic;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// BACKLOG WAVE 3 (2026-10-19), the mod's half. Block a card gives is filed
/// on its row (Klee Can Explain! printed "Nothing this page can count landed
/// off it"); a row still resolving says so on the wire (a free Bravura's
/// page listed one hit of four); and the Bake-Kurage stands clear of any
/// owner (it sat on the Defect's front leg). The page half is
/// <c>tier0/tests/test_seat_page_backlog_2026_10_19_wave3.py</c>.
/// </summary>
public class SeatPageBacklogWave3Tests
{
    [Fact]
    public void Block_a_card_gives_is_filed_on_its_row()
    {
        ResolutionLedger.ResetFight();
        ResolutionLedger.OpenPlay("klee_can_explain", "Klee Can Explain!", false);
        ResolutionLedger.NoteBlock("Klee", 6, "1", self: true);
        ResolutionLedger.NoteBlock("Klee", 0, "1", self: true);

        var block = (List<Dictionary<string, object?>>)
            ResolutionLedger.Snapshot()[0]["block"]!;
        Assert.Single(block);
        Assert.Equal(6, block[0]["amount"]);
        Assert.Equal(true, block[0]["self"]);
    }

    [Fact]
    public void Block_outside_a_play_is_not_filed()
    {
        ResolutionLedger.ResetFight();
        ResolutionLedger.NoteBlock("Klee", 6, "1", self: true);
        Assert.Empty(ResolutionLedger.Snapshot());
    }

    [Fact]
    public void The_block_hook_feeds_the_ledger()
    {
        var calls = Il.Calls(Il.Method("PlayTelemetryHooks", "AfterBlockGained"));
        Assert.Contains("ResolutionLedger.get_PlayOpen", calls);
    }

    [Fact]
    public void A_row_is_open_until_its_play_closes()
    {
        ResolutionLedger.ResetFight();
        ResolutionLedger.OpenPlay("bravura", "Bravura", false);
        Assert.Equal(true, ResolutionLedger.Snapshot()[0]["open"]);
        ResolutionLedger.ClosePlay();
        Assert.Equal(false, ResolutionLedger.Snapshot()[0]["open"]);
    }

    [Theory]
    [InlineData(-550f, 60f)]   // a narrow body
    [InlineData(-550f, 120f)]  // Klee- or Furina-wide
    [InlineData(-550f, 200f)]  // a wide one
    public void The_kurage_stands_clear_in_front_of_its_owner(
        float ownerX, float ownerHalf)
    {
        const float width = 120f; // the scene's Bounds box
        var centre = BakeKuragePlacement.Centre(ownerX, ownerHalf, width);
        // Its left edge is a floor gap past the owner's right edge.
        Assert.Equal(ownerX + ownerHalf + FurinaStagePlacement.Gap,
                     centre - width * 0.5f, 3);
    }

    [Fact]
    public void The_defect_frame_no_longer_overlaps()
    {
        // The engine's mid-combat slot: owner.X - 20 + 60, a left edge 20
        // left of the owner's centre -- on the body.
        const float half = 100f;
        var engine = 0f - 20f + 60f;
        Assert.True(engine - 60f < half);
        var centre = BakeKuragePlacement.Centre(0f, half, 120f);
        Assert.True(centre - 60f >= half, $"left edge {centre - 60f}");
    }
}
