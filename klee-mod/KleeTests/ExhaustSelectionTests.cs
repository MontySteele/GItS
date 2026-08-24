using System.Linq;
using KleeMod.Cards.Generated;
using KleeMod.Cards.Kokomi.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-118 — the Exhaust identity context, mod side.
///
/// Sim twin: `tier0/tests/test_exhaust_context.py`. Both suites ask the same
/// questions of the same six descriptors, and the COLUMN NAMES the two emit
/// are pinned against each other by `test_exhaust_context_parity.py`, which
/// reads `ExhaustSelection.RowKeys` out of the source.
///
/// WHAT IS REACHABLE HERE. `ExhaustSelection` is deliberately free of live
/// combat state — it records printed identity and derives integers — so every
/// behavioural fact below is tested for real, not structurally. The one thing
/// that is NOT reachable is a card actually being PLAYED (README, "The
/// headless boundary"), so the codegen's wiring of Open/Record/Close into a
/// generated `OnPlay` is pinned by its IL call set and labelled as structural.
/// </summary>
public class ExhaustSelectionTests
{
    /// <summary>A playable copy of a generated card, owned by one seat — the
    /// `PlayableCopyOfEncorePerformance` idiom (ParityAuthorityPinTests): a
    /// freshly constructed CardModel is the canonical prototype and its Owner
    /// accessors call AssertMutable, so IsMutable is set directly.</summary>
    private static T Owned<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    // --- the descriptors --------------------------------------------------

    [Fact]
    public void A_victim_is_recorded_by_its_printed_identity()
    {
        var seat = Seat.Kokomi();
        var resolving = Owned<PearlDiver>(seat);
        var victim = Owned<CleansingTide>(seat);

        ExhaustSelection.Open(resolving);
        ExhaustSelection.Record(resolving, victim);

        var recorded = Assert.Single(ExhaustSelection.Current(resolving));
        Assert.Equal(victim.Id.Entry, recorded.Id);
        Assert.Equal(victim.EnergyCost.Canonical, recorded.Cost);
        Assert.Equal(victim.Type, recorded.Type);
        Assert.Equal(victim.Rarity, recorded.Rarity);
        Assert.False(recorded.Companion);
        Assert.False(recorded.Upgraded);
    }

    [Fact]
    public void The_cost_recorded_is_the_printed_one()
    {
        // `Canonical` is the printed cost -- the sim's `card.cost` -- not
        // GetAmountToSpend(), which is that cost after this instance's
        // modifiers and would make one card record two numbers in two runs.
        var seat = Seat.Kokomi();
        var resolving = Owned<PearlDiver>(seat);
        var victim = Owned<EbbTide>(seat);
        victim.EnergyCost.AddThisCombat(2, reduceOnly: false);

        ExhaustSelection.Open(resolving);
        ExhaustSelection.Record(resolving, victim);

        Assert.Equal(victim.EnergyCost.Canonical,
                     ExhaustSelection.Current(resolving).Single().Cost);
    }

    // --- the derived reads ------------------------------------------------

    [Fact]
    public void The_derived_reads_answer_off_the_recorded_descriptors()
    {
        var seat = Seat.Kokomi();
        var resolving = Owned<PearlDiver>(seat);
        var a = Owned<CleansingTide>(seat);
        var b = Owned<EbbTide>(seat);

        ExhaustSelection.Open(resolving);
        ExhaustSelection.Record(resolving, a);
        ExhaustSelection.Record(resolving, b);

        Assert.Equal(2, ExhaustSelection.Size(resolving));
        Assert.Equal(a.EnergyCost.Canonical + b.EnergyCost.Canonical,
                     ExhaustSelection.Cost(resolving));
        Assert.Equal(2, ExhaustSelection.Skills(resolving)
                        + ExhaustSelection.Attacks(resolving)
                        + ExhaustSelection.Powers(resolving));
        Assert.Equal(2, ExhaustSelection.Personal(resolving));
        Assert.Equal(0, ExhaustSelection.Companions(resolving));
        Assert.Equal(0, ExhaustSelection.Upgraded(resolving));
    }

    [Fact]
    public void Personal_and_companions_partition_the_selection()
    {
        var seat = Seat.Kokomi();
        var resolving = Owned<PearlDiver>(seat);

        ExhaustSelection.Open(resolving);
        ExhaustSelection.Record(resolving, Owned<CleansingTide>(seat));

        Assert.Equal(ExhaustSelection.Size(resolving),
                     ExhaustSelection.Personal(resolving)
                     + ExhaustSelection.Companions(resolving));
    }

    // --- THE SCOPING ------------------------------------------------------

    [Fact]
    public void Another_card_reads_nothing()
    {
        // The whole reason this is a context and not a combat-global
        // `last_exhausted`: the next card played cannot see these victims.
        var seat = Seat.Kokomi();
        var resolving = Owned<PearlDiver>(seat);
        var next = Owned<TidelineWatch>(seat);

        ExhaustSelection.Open(resolving);
        ExhaustSelection.Record(resolving, Owned<CleansingTide>(seat));

        Assert.Empty(ExhaustSelection.Current(next));
        Assert.Equal(0, ExhaustSelection.Cost(next));
        Assert.Equal(0, ExhaustSelection.Size(next));
    }

    [Fact]
    public void A_second_open_replaces_the_first_selection()
    {
        var seat = Seat.Kokomi();
        var resolving = Owned<PearlDiver>(seat);
        var first = Owned<CleansingTide>(seat);
        var second = Owned<EbbTide>(seat);

        ExhaustSelection.Open(resolving);
        ExhaustSelection.Record(resolving, first);
        ExhaustSelection.Open(resolving);
        ExhaustSelection.Record(resolving, second);

        Assert.Equal(second.Id.Entry,
                     ExhaustSelection.Current(resolving).Single().Id);
    }

    [Fact]
    public void A_second_open_that_records_nothing_leaves_an_empty_selection()
    {
        // The replace is unconditional. A second selector that offers nothing
        // must not leave the first one's victims standing for the reader
        // after it -- the leak this shape exists to prevent.
        var seat = Seat.Kokomi();
        var resolving = Owned<PearlDiver>(seat);

        ExhaustSelection.Open(resolving);
        ExhaustSelection.Record(resolving, Owned<CleansingTide>(seat));
        ExhaustSelection.Open(resolving);

        Assert.Empty(ExhaustSelection.Current(resolving));
    }

    [Fact]
    public void Recording_against_a_card_that_did_not_open_is_dropped()
    {
        var seat = Seat.Kokomi();
        var resolving = Owned<PearlDiver>(seat);
        var impostor = Owned<TidelineWatch>(seat);

        ExhaustSelection.Open(resolving);
        ExhaustSelection.Record(impostor, Owned<CleansingTide>(seat));

        Assert.Empty(ExhaustSelection.Current(resolving));
        Assert.Empty(ExhaustSelection.Current(impostor));
    }

    [Fact]
    public void The_seat_is_part_of_the_scope_key()
    {
        // G-B1's lesson: a per-resolution tracker keyed on anything shared is
        // correct in solo and wrong in co-op, and solo is the only
        // configuration tier 0.5 can see. The same card instance re-owned by
        // the other seat is not the entry that was opened.
        var kokomi = Seat.Kokomi();
        var partner = Seat.Kokomi();
        var resolving = Owned<PearlDiver>(kokomi);

        ExhaustSelection.Open(resolving);
        ExhaustSelection.Record(resolving, Owned<CleansingTide>(kokomi));
        Assert.Single(ExhaustSelection.Current(resolving));

        // Forced through the backing field: the real setter refuses a second
        // owner ("already has an owner"), which is the game protecting the
        // very invariant this test is standing in for.
        Seat.Force(resolving, "Owner", partner.Player);
        Assert.Empty(ExhaustSelection.Current(resolving));
    }

    [Fact]
    public void A_null_card_reads_nothing()
    {
        // CalculatedVar previews call the multiplier with nothing hovered.
        var seat = Seat.Kokomi();
        var resolving = Owned<PearlDiver>(seat);
        ExhaustSelection.Open(resolving);
        ExhaustSelection.Record(resolving, Owned<CleansingTide>(seat));

        Assert.Empty(ExhaustSelection.Current(null));
        Assert.Equal(0, ExhaustSelection.Cost(null));
    }

    // --- the parity row ---------------------------------------------------

    [Fact]
    public void The_parity_row_carries_every_column_in_order()
    {
        var seat = Seat.Kokomi();
        var resolving = Owned<PearlDiver>(seat);
        var victim = Owned<CleansingTide>(seat);

        ExhaustSelection.Open(resolving);
        ExhaustSelection.Record(resolving, victim);
        var row = ExhaustSelection.ParityRow(resolving);

        var at = -1;
        foreach (var key in ExhaustSelection.RowKeys)
        {
            var next = row.IndexOf("\"" + key + "\":", System.StringComparison.Ordinal);
            Assert.True(next > at, $"column '{key}' missing or out of order");
            at = next;
        }

        Assert.Contains($"\"card\":\"{resolving.Id.Entry}\"", row);
        Assert.Contains($"\"victims\":[\"{victim.Id.Entry}\"]", row);
        Assert.Contains("\"size\":1", row);
    }

    [Fact]
    public void An_empty_selection_still_renders_a_row()
    {
        // "Nothing was there to take" is a reading, not a gap: a parity test
        // comparing streams must see the same number of rows on both sides.
        var resolving = Owned<PearlDiver>(Seat.Kokomi());
        ExhaustSelection.Open(resolving);

        var row = ExhaustSelection.ParityRow(resolving);
        Assert.Contains("\"victims\":[]", row);
        Assert.Contains("\"size\":0", row);
    }

    [Fact]
    public void Every_derived_column_is_answerable_by_name()
    {
        // RowKeys is a promise; Derived is what keeps it. A column listed
        // there but unimplemented throws HERE rather than writing a silent
        // zero into a parity comparison.
        var resolving = Owned<PearlDiver>(Seat.Kokomi());
        ExhaustSelection.Open(resolving);

        foreach (var key in ExhaustSelection.RowKeys)
        {
            if (key == "card" || key == "victims") continue;
            Assert.Equal(0, ExhaustSelection.Derived(key, resolving));
        }
    }

    // --- the codegen wiring (STRUCTURAL) ----------------------------------

    [Fact]
    public void A_generated_chosen_exhaust_card_opens_records_and_closes()
    {
        // STRUCTURAL PIN. A card play is outside the headless boundary, so
        // what is checked is that codegen put all three beats in the selector
        // block -- Record without Open would record into another card's
        // context, and Open without Close would never emit the parity row.
        var calls = Il.Calls(typeof(PearlDiver)
            .GetMethod("OnPlay", HeadlessGame.All)!);

        Assert.Contains("ExhaustSelection.Open", calls);
        Assert.Contains("ExhaustSelection.Record", calls);
        Assert.Contains("ExhaustSelection.Close", calls);
    }

    [Fact]
    public void A_generated_status_filtered_card_records_its_victims_too()
    {
        // Dodge Roll. The context is the OP's, not Kokomi's: a junk-eater's
        // selection is recorded like anyone else's. Recording it is NOT a
        // reward grammar -- no card reads it, and none may.
        var calls = Il.Calls(typeof(DodgeRoll)
            .GetMethod("OnPlay", HeadlessGame.All)!);

        Assert.Contains("ExhaustSelection.Open", calls);
        Assert.Contains("ExhaustSelection.Record", calls);
        Assert.Contains("ExhaustSelection.Close", calls);
    }
}
