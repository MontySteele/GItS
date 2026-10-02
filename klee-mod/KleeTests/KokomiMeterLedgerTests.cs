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

}
