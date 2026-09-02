using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Diagnostics;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-273`, THE C# HALF: Kokomi's meters mint ledger rows.
///
/// THE GAP THIS CLOSES. `MeterLedger` was noted from `SparkPower` alone, so a
/// blind run's record could rebuild the arithmetic of every Klee play and none
/// of Kokomi's: a Charge bank that read 6 after a play might have been paid
/// down by a memory and refilled by an exhaust, or never moved at all. The
/// Python half landed first (the grader's snapshot now carries the raw Plan
/// map); this is the mod side of the same row.
///
/// WHAT IS REAL HERE. Charge is inside the headless boundary -- `Seat` builds a
/// real `Player`, a real `Creature` and a real `PlayerCombatState`, and
/// `ChargeResource` is a plain `BasicCustomResource` -- so every Charge
/// assertion below is a real call on a real object whose bank really moves. The
/// Plan queue is NOT: `KokomiPlan.Sync` awaits `PowerCmd`, which needs a live
/// combat, so its seam is pinned structurally in
/// `Prototype/KokomiPlanLedgerTests` and labelled there.
///
/// The ledger is static state, so every test opens with `ResetFight()`, exactly
/// as `MeterLedgerTests` does.
/// </summary>
public class KokomiMeterLedgerTests
{
    private static Dictionary<string, object?> Row(int index) =>
        MeterLedger.Snapshot().Single(r => (int)r["index"]! == index);

    private static Dictionary<string, int> Gains(Dictionary<string, object?> row)
        => (Dictionary<string, int>)row["gains"]!;

    private static Seat Kokomi() => Seat.Kokomi().WithCombatState();

    [Fact]
    public void The_two_kokomi_meters_are_named_on_the_ledger()
    {
        // A meter is a FIELD, not a type (MeterLedger's header, point 1), and
        // these two strings are the whole of the wiring on the Python side:
        // `understudy.blindplay.meter_plays` already takes the meter as a
        // parameter, so nothing over there had to move to read them.
        Assert.Equal("charge", MeterLedger.Charge);
        Assert.Equal("plan", MeterLedger.Plan);
        Assert.NotEqual(MeterLedger.Spark, MeterLedger.Charge);
        Assert.NotEqual(MeterLedger.Spark, MeterLedger.Plan);
    }

    [Fact]
    public void A_charge_gain_mints_a_row_on_its_own_meter()
    {
        MeterLedger.ResetFight();
        var seat = Kokomi();
        MeterLedger.OpenTurn(2);

        KokomiResources.GainCharge(seat.Creature, 4, "rule:exhaust");

        var row = Row(1);
        Assert.Equal("charge", row["meter"]);
        Assert.Equal(2, row["turn"]);
        Assert.Equal(0, row["before"]);
        Assert.Equal(4, Gains(row)["rule:exhaust"]);
        Assert.Equal(4, row["after"]);
        // And the ledger agrees with the bank it was read off.
        Assert.Equal(4, KokomiResources.GetCharge(seat.Creature));
    }

    [Fact]
    public void An_unnamed_gain_is_the_card_because_the_row_carries_which_card()
    {
        // A generated `gain_charge` line calls the funnel with no context of
        // its own. It does not need one: the ROW names the card, opened at the
        // play boundary. The named sources exist for the gains that are NOT a
        // card and would otherwise be indistinguishable from the card's own.
        MeterLedger.ResetFight();
        var seat = Kokomi();
        MeterLedger.OpenPlay(MeterLedger.Charge, "KLEEMOD-PEARL_DIVER",
                             "Pearl Diver", turn: 1, before: 0);

        KokomiResources.GainCharge(seat.Creature, 2);
        KokomiResources.GainCharge(seat.Creature, 1, "rule:exhaust");

        var row = Row(1);
        Assert.Equal("KLEEMOD-PEARL_DIVER", row["card"]);
        Assert.Equal(2, Gains(row)["card"]);
        Assert.Equal(1, Gains(row)["rule:exhaust"]);
        Assert.Equal(3, row["after"]);
    }

    [Fact]
    public async Task A_charge_spend_is_a_price_and_names_the_card_that_paid()
    {
        MeterLedger.ResetFight();
        var seat = Kokomi();
        KokomiResources.GainCharge(seat.Creature, 5, "rule:exhaust");
        MeterLedger.OpenPlay(MeterLedger.Charge, "KLEEMOD-X", "X",
                             turn: 3, before: 5);

        Assert.True(await KokomiResources.SpendCharge(
            null, seat.Creature, 3, cardSource: null));

        var row = Row(2);
        Assert.Equal("charge", row["meter"]);
        Assert.Equal(5, row["before"]);
        Assert.Equal(3, row["price_paid"]);
        Assert.Empty(Gains(row));
        Assert.Equal(2, row["after"]);
        Assert.Equal(2, KokomiResources.GetCharge(seat.Creature));
    }

    [Fact]
    public async Task A_refused_charge_spend_writes_nothing_at_all()
    {
        // `SparkPower.Spend`'s rule verbatim, and the reason is the reader: a
        // row saying "paid 0" reads as a free play rather than as a play that
        // never happened. The bank is short, so the spend mutates nothing.
        MeterLedger.ResetFight();
        var seat = Kokomi();
        KokomiResources.GainCharge(seat.Creature, 1, "rule:exhaust");
        var before = MeterLedger.Snapshot().Count;

        Assert.False(await KokomiResources.SpendCharge(
            null, seat.Creature, 9, cardSource: null));

        Assert.Equal(before, MeterLedger.Snapshot().Count);
        Assert.Equal(1, KokomiResources.GetCharge(seat.Creature));
    }

    [Fact]
    public void A_non_kokomi_seat_moves_no_charge_and_writes_no_row()
    {
        // `Find` gates on identity, so the funnel returns before it mutates
        // anything -- and the ledger must not gain a row for a bank that does
        // not exist. Klee under co-op is the live case.
        MeterLedger.ResetFight();
        var klee = Seat.Klee().WithCombatState();

        KokomiResources.GainCharge(klee.Creature, 3, "rule:exhaust");

        Assert.Empty(MeterLedger.Snapshot());
    }

    [Fact]
    public void The_delta_recorded_is_the_one_that_landed_not_the_one_asked_for()
    {
        // The header's point on `SparkPower.Gain`: the bank is read either side
        // of the mutation. A non-positive request is refused by the funnel, so
        // nothing lands and nothing is written.
        MeterLedger.ResetFight();
        var seat = Kokomi();

        KokomiResources.GainCharge(seat.Creature, 0, "rule:exhaust");
        KokomiResources.GainCharge(seat.Creature, -2, "rule:exhaust");

        Assert.Empty(MeterLedger.Snapshot());
        Assert.Equal(0, KokomiResources.GetCharge(seat.Creature));
    }
}
