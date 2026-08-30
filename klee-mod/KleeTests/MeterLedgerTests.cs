using System.Collections.Generic;
using System.Linq;
using KleeMod.Diagnostics;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-216` / R225's clause. THE LEDGER'S ARITHMETIC, headless.
///
/// Every downstream count -- a grader rebuilding a play's bank, an erratum
/// reader asking where three Sparks went -- rests on the four fields this file
/// computes, and none of them needs a scene tree, a combat or a game type to
/// exercise. `MeterLedger` is deliberately free of all three so this can
/// assert the arithmetic itself rather than an IL shape standing in for it.
///
/// The ledger is static state, so every test opens with `ResetFight()` -- the
/// same call the combat hook makes, and asserting it works is one of the
/// tests below rather than an assumption the others rest on.
/// </summary>
public class MeterLedgerTests
{
    private static Dictionary<string, object?> Row(int index) =>
        MeterLedger.Snapshot().Single(r => (int)r["index"]! == index);

    private static Dictionary<string, int> Gains(Dictionary<string, object?> row)
        => (Dictionary<string, int>)row["gains"]!;

    [Fact]
    public void A_play_carries_before_price_paid_gains_by_source_and_after()
    {
        MeterLedger.ResetFight();
        MeterLedger.OpenPlay(MeterLedger.Spark, "KLEEMOD-KAPOW", "Ka-pow!",
                             turn: 3, before: 4);
        MeterLedger.Note(MeterLedger.Spark, "card:KLEEMOD-KAPOW", -1, 4);
        MeterLedger.Note(MeterLedger.Spark,
                         "relic:pounding_surprise/detonation", 1, 3);
        MeterLedger.Note(MeterLedger.Spark,
                         "relic:pounding_surprise/detonation", 1, 4);

        var row = Row(1);
        Assert.Equal("spark", row["meter"]);
        Assert.Equal(3, row["turn"]);
        Assert.Equal("KLEEMOD-KAPOW", row["card"]);
        Assert.Equal("Ka-pow!", row["card_name"]);
        Assert.Equal(4, row["before"]);
        Assert.Equal(1, row["price_paid"]);
        Assert.Equal(2, Gains(row)["relic:pounding_surprise/detonation"]);
        // 4 - 1 + 2. DERIVED, never a second read of the bank.
        Assert.Equal(5, row["after"]);
    }

    [Fact]
    public void Gains_are_summed_per_source_and_never_pooled()
    {
        MeterLedger.ResetFight();
        MeterLedger.OpenPlay(MeterLedger.Spark, "C", "C", turn: 1, before: 0);
        MeterLedger.Note(MeterLedger.Spark, "card:C", 2, 0);
        MeterLedger.Note(MeterLedger.Spark, "companion:prune/play", 1, 2);
        MeterLedger.Note(MeterLedger.Spark, "card:C", 1, 3);

        var gains = Gains(Row(1));
        Assert.Equal(3, gains["card:C"]);
        Assert.Equal(1, gains["companion:prune/play"]);
        Assert.Equal(4, Row(1)["after"]);
    }

    [Fact]
    public void Every_spend_counts_as_price_however_it_was_named()
    {
        // The threshold consume is charged by the RULE and not printed on the
        // card; it is still a price, and a grader asking what a play cost must
        // not have to know which spends were printed.
        MeterLedger.ResetFight();
        MeterLedger.OpenPlay(MeterLedger.Spark, "S", "Strike", turn: 2,
                             before: 5);
        MeterLedger.Note(MeterLedger.Spark, "card:S", -2, 5);
        MeterLedger.Note(MeterLedger.Spark, "rule:threshold_consume", -3, 3);

        Assert.Equal(5, Row(1)["price_paid"]);
        Assert.Empty(Gains(Row(1)));
        Assert.Equal(0, Row(1)["after"]);
    }

    [Fact]
    public void A_delta_with_no_play_open_still_lands_and_still_adds_up()
    {
        // A turn-start kit response and the combat-start windfall are not
        // plays. A ledger that dropped them would not reconcile against the
        // bank the wire reports.
        MeterLedger.ResetFight();
        MeterLedger.OpenTurn(1);
        MeterLedger.Note(MeterLedger.Spark,
                         "relic:explosive_frags/combat_start", 3, 0);

        var row = Row(1);
        Assert.Equal("", row["card"]);
        Assert.Equal(1, row["turn"]);
        Assert.Equal(0, row["before"]);
        Assert.Equal(3, row["after"]);
    }

    [Fact]
    public void Deltas_land_on_the_play_that_is_open_and_not_on_the_last_one()
    {
        MeterLedger.ResetFight();
        MeterLedger.OpenPlay(MeterLedger.Spark, "A", "A", turn: 1, before: 2);
        MeterLedger.Note(MeterLedger.Spark, "card:A", -2, 2);
        MeterLedger.OpenPlay(MeterLedger.Spark, "B", "B", turn: 1, before: 0);
        MeterLedger.Note(MeterLedger.Spark, "card:B", 1, 0);

        Assert.Equal(2, Row(1)["price_paid"]);
        Assert.Equal(0, Row(1)["after"]);
        Assert.Equal(0, Row(2)["price_paid"]);
        Assert.Equal(1, Row(2)["after"]);
    }

    [Fact]
    public void A_row_stays_open_so_a_refund_after_resolution_is_that_plays()
    {
        // Point 3 of the header. A detonation refund resolving after the
        // card's own effects belongs to that card's play, and a poll taken
        // between the two reports what has happened so far -- which is the
        // truth at the moment of the read, not a wrong answer.
        MeterLedger.ResetFight();
        MeterLedger.OpenPlay(MeterLedger.Spark, "A", "A", turn: 1, before: 3);
        MeterLedger.Note(MeterLedger.Spark, "card:A", -3, 3);
        Assert.Equal(0, Row(1)["after"]);

        MeterLedger.Note(MeterLedger.Spark,
                         "relic:pounding_surprise/detonation", 1, 0);
        Assert.Equal(1, Row(1)["after"]);
    }

    [Fact]
    public void A_zero_delta_is_not_a_row_and_not_an_entry()
    {
        // A refused spend mutates nothing. "Paid 0" would read as a free play
        // rather than as a play that never happened.
        MeterLedger.ResetFight();
        MeterLedger.Note(MeterLedger.Spark, "card:X", 0, 7);
        Assert.Empty(MeterLedger.Snapshot());
    }

    [Fact]
    public void Each_entry_carries_the_bank_it_saw_so_a_reader_can_compare()
    {
        MeterLedger.ResetFight();
        MeterLedger.OpenPlay(MeterLedger.Spark, "A", "A", turn: 1, before: 4);
        MeterLedger.Note(MeterLedger.Spark, "card:A", -1, 4);

        var entries = (List<Dictionary<string, object?>>)Row(1)["entries"]!;
        Assert.Single(entries);
        Assert.Equal("card:A", entries[0]["source"]);
        Assert.Equal(-1, entries[0]["delta"]);
        Assert.Equal(4, entries[0]["bank_before"]);
    }

    [Fact]
    public void A_fight_reset_forgets_the_previous_fights_rows()
    {
        MeterLedger.ResetFight();
        MeterLedger.OpenPlay(MeterLedger.Spark, "A", "A", turn: 9, before: 1);
        MeterLedger.Note(MeterLedger.Spark, "card:A", -1, 1);
        Assert.NotEmpty(MeterLedger.Snapshot());

        MeterLedger.ResetFight();
        Assert.Empty(MeterLedger.Snapshot());
        // And the index restarts, so row 1 of a fight is row 1 of that fight.
        MeterLedger.OpenPlay(MeterLedger.Spark, "B", "B", turn: 1, before: 0);
        Assert.Equal(1, MeterLedger.Snapshot()[0]["index"]);
    }

    [Fact]
    public void The_row_cap_drops_the_oldest_and_never_grows_without_bound()
    {
        MeterLedger.ResetFight();
        for (var i = 0; i < MeterLedger.MaxRows + 5; i++)
        {
            MeterLedger.OpenPlay(MeterLedger.Spark, "A", "A", turn: 1,
                                 before: 0);
        }
        var rows = MeterLedger.Snapshot();
        Assert.Equal(MeterLedger.MaxRows, rows.Count);
        // The survivors are the NEWEST rows, oldest first.
        Assert.Equal(6, rows[0]["index"]);
        Assert.Equal(MeterLedger.MaxRows + 5, rows[^1]["index"]);
    }

    [Fact]
    public void The_meter_is_a_field_so_a_second_meter_keeps_its_own_rows()
    {
        // Charge and Encore are the same shape and will want these rows. The
        // ledger knows the word "spark" only as a caller's string.
        MeterLedger.ResetFight();
        MeterLedger.OpenPlay(MeterLedger.Spark, "A", "A", turn: 1, before: 2);
        MeterLedger.OpenPlay("charge", "B", "B", turn: 1, before: 8);
        MeterLedger.Note("charge", "card:B", -8, 8);
        MeterLedger.Note(MeterLedger.Spark, "card:A", 1, 2);

        Assert.Equal("spark", Row(1)["meter"]);
        Assert.Equal(3, Row(1)["after"]);
        Assert.Equal("charge", Row(2)["meter"]);
        Assert.Equal(0, Row(2)["after"]);
    }
}
