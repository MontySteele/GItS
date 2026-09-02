using System.Linq;
using System.Reflection;
using KleeMod.Diagnostics;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-273`, the Plan half: A PLAN WRITE MINTS A LEDGER ROW.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, the split
/// `KokomiOverhaulRuleTests` makes and for the same reason. The queue's
/// ARITHMETIC is real -- `MeterLedger` holds no game type, so the rows a write
/// and a morning drain produce are computed here, not asserted about a mock.
/// The SEAM is structural: `KokomiPlan.Sync` awaits `PowerCmd.Apply` /
/// `ModifyAmount` to keep the pending-Plans badge in step, and a live
/// `CombatState` is outside the headless boundary (README), so what is pinned
/// is that the one funnel every queue mutation goes through does note the
/// ledger -- which IS the fact the row was open on.
///
/// WHY THE FUNNEL AND NOT THE THREE CALLERS. `Sync` is already the single site
/// that keeps the badge, the strip and the list-that-will-resolve three views
/// of one number; a note written anywhere else could be skipped by a future
/// site that moved the queue and only refreshed the badge. Pinning the funnel
/// pins every caller at once, and the fourth caller nobody has written yet.
/// </summary>
public class KokomiPlanLedgerTests
{
    private static MethodBase Sync() =>
        typeof(KokomiPlan).GetMethod("Sync", HeadlessGame.All)
        ?? throw new System.InvalidOperationException(
            "KokomiPlan.Sync is gone -- the queue's one funnel moved under "
          + "this pin, and the ledger note moved with it.");

    // ---- THE SEAM, structural -------------------------------------------

    [Fact]
    public void The_one_queue_funnel_notes_the_ledger()
    {
        // STRUCTURAL PIN (Il): the call set of the async state machine.
        var calls = Il.Calls(Sync());
        Assert.Contains("MeterLedger.Note", calls);
    }

    [Fact]
    public void The_funnel_is_handed_the_depth_it_started_from()
    {
        // By the time `Sync` runs the queue has already moved, and the badge's
        // own amount is a DISPLAY value the engine's modifier chain may resize.
        // Each caller knows the depth it started from exactly, so it hands it
        // over -- which is why the signature carries it rather than reading it.
        var parameters = Sync().GetParameters();
        Assert.Contains(parameters, p => p.Name == "before"
                                      && p.ParameterType == typeof(int));
        Assert.Contains(parameters, p => p.Name == "source"
                                      && p.ParameterType == typeof(string));
    }

    [Fact]
    public void Every_site_that_moves_the_queue_goes_through_the_funnel()
    {
        // The three today: a write, the morning drain and Change of Plans.
        // A fourth that skipped the funnel would lose its row, so the pin is
        // on the callers rather than on a count of `Note` calls.
        foreach (var name in new[] { "Schedule", "ResolveAll", "ResolveFront" })
        {
            var method = typeof(KokomiPlan).GetMethod(name, HeadlessGame.All)
                ?? throw new System.InvalidOperationException(
                    $"KokomiPlan.{name} is gone.");
            Assert.Contains("KokomiPlan.Sync", Il.Calls(method));
        }
    }

    // ---- THE ARITHMETIC, real -------------------------------------------

    [Fact]
    public void A_plan_write_reads_as_a_gain_on_the_plan_meter()
    {
        MeterLedger.ResetFight();
        MeterLedger.OpenPlay(MeterLedger.Plan, "KLEEMOD-KO_TIDAL_ORDER",
                             "Tidal Order", turn: 2, before: 1);
        // What `Schedule` hands over: the card that wrote it, and the depth
        // before the write.
        MeterLedger.Note(MeterLedger.Plan, "card:KLEEMOD-KO_TIDAL_ORDER", 1, 1);

        var row = MeterLedger.Snapshot().Single();
        Assert.Equal("plan", row["meter"]);
        Assert.Equal("KLEEMOD-KO_TIDAL_ORDER", row["card"]);
        Assert.Equal(1, row["before"]);
        Assert.Equal(0, row["price_paid"]);
        Assert.Equal(2, row["after"]);
    }

    [Fact]
    public void The_morning_drain_is_a_price_and_empties_the_queue()
    {
        // `ResolveAll` clears the whole queue in one move, so the drain is a
        // single entry of -depth, named as the RULE: nothing was printed on a
        // card, and a grader reading `card:` there would count a price no face
        // ever showed (`SparkPower`'s threshold consume makes the same call).
        MeterLedger.ResetFight();
        MeterLedger.OpenTurn(4);
        MeterLedger.Note(MeterLedger.Plan, "rule:morning_drain", -3, 3);

        var row = MeterLedger.Snapshot().Single();
        Assert.Equal("", row["card"]);
        Assert.Equal(4, row["turn"]);
        Assert.Equal(3, row["before"]);
        Assert.Equal(3, row["price_paid"]);
        Assert.Equal(0, row["after"]);
    }

    [Fact]
    public void The_two_kokomi_meters_keep_their_own_rows()
    {
        // Point 1 of the ledger's header, exercised on the pair that made it
        // true: a Plan write and a Charge spend in one play are two rows, not
        // one row with a confused bank.
        MeterLedger.ResetFight();
        MeterLedger.OpenPlay(MeterLedger.Charge, "A", "A", turn: 1, before: 6);
        MeterLedger.OpenPlay(MeterLedger.Plan, "A", "A", turn: 1, before: 0);
        MeterLedger.Note(MeterLedger.Charge, "card:A", -2, 6);
        MeterLedger.Note(MeterLedger.Plan, "card:A", 1, 0);

        var rows = MeterLedger.Snapshot();
        Assert.Equal(2, rows.Count);
        Assert.Equal(4, rows.Single(r => (string)r["meter"]! == "charge")["after"]);
        Assert.Equal(1, rows.Single(r => (string)r["meter"]! == "plan")["after"]);
    }
}
