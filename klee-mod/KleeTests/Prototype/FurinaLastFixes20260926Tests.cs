#nullable enable

using System;
using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- the last fixes from the 2026-09-26 wave-3 seat round
/// (lane 3, seat b). The sim's pins are
/// <c>tier0/tests/test_furina_last_fixes_2026_09_26.py</c>.
///
/// NAVIA'S BOW READS THE BAR SHE HAD. The seat: "Navia's bow is always worth
/// nothing when she dies to a hit or a Spend." The designer's ruling: her Bow
/// deals damage equal to the Fanfare she had before whatever emptied her --
/// the hit that took her down, the Spend, the payment, Let the People
/// Rejoice. Every exit at 0 Fanfare carries that bar as
/// <see cref="StageExit.Held"/>, which is what her Bow reads.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class FurinaLastFixes20260926Tests
{
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaStage.Enabled;

        internal Arm()
        {
            FurinaStageLedger.ResetAll();
            FurinaStage.Enabled = true;
        }

        public void Dispose()
        {
            FurinaStage.Enabled = _enabled;
            FurinaStageLedger.ResetAll();
        }
    }

    private static readonly StageForecastEnemy[] OneEnemy =
        { new("Shrinker Beetle", false) };

    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        params (string Member, int Fanfare)[] seats)
    {
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        foreach (var (member, fanfare) in seats)
        {
            var who = FurinaStage.Parse(member);
            if (FurinaStage.IsGuest(who))
            {
                stage.GuestArrives(who, fanfare);
            }
            else
            {
                stage.Summon(who);
                stage.Raise(fanfare - FurinaStageLaw.SummonFanfare);
            }
        }
        stage.ClearBeats();
        return (seat, stage);
    }

    [Fact]
    public void A_hit_that_empties_navia_leaves_her_bar_for_her_bow()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("navia", 6), ("usher", 3));
        var hit = stage.Absorb(9);
        var exit = Assert.IsType<StageExit>(hit.Exit);
        Assert.Equal(StagePerformer.Navia, exit.Who);
        Assert.Equal(StageDeparture.Struck, exit.Cause);
        Assert.Equal(6, exit.Held);
    }

    [Fact]
    public void A_spend_that_empties_navia_leaves_her_bar_for_her_bow()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 3), ("navia", 4));
        var spend = stage.Spend(4);
        Assert.True(spend.Fired);
        Assert.Equal(4, Assert.IsType<StageExit>(spend.Exit).Held);
    }

    [Fact]
    public void Every_cash_out_leaves_her_bar_for_her_bow()
    {
        using var _ = new Arm();
        var (_, back) = Stage(("usher", 3), ("navia", 7));
        Assert.Equal(7, Assert.IsType<StageExit>(back.SpendAllOfBack().Exit)
                            .Held);

        var (_, front) = Stage(("navia", 8), ("usher", 3));
        Assert.Equal(8, Assert.IsType<StageExit>(front.SpendAllOfFront().Exit)
                            .Held);

        var (_, final) = Stage(("usher", 3), ("navia", 5));
        var exit = final.FinalBow(out var bar);
        Assert.Equal(5, bar);
        Assert.Equal(5, Assert.IsType<StageExit>(exit).Held);
    }

    [Fact]
    public void Let_the_people_rejoice_leaves_each_bar_for_its_bow()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 3), ("navia", 11));
        Assert.Equal(14, stage.CollectAll());
        var exits = stage.TakePendingCurtainExits();
        Assert.Equal(new[] { 3, 11 }, exits.Select(e => e.Held).ToArray());
    }

    [Fact]
    public void A_payment_that_empties_navia_leaves_what_she_paid()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("clorinde", 4), ("navia", 1));
        var owed = new System.Collections.Generic.List<StageExit>();
        Assert.True(stage.ActFanfare(StagePerformer.Clorinde, stage.Seats[0],
                                     null, owed));
        var exit = Assert.Single(owed);
        Assert.Equal(StagePerformer.Navia, exit.Who);
        Assert.Equal(1, exit.Held);
    }

    [Fact]
    public void The_forecast_prints_the_bow_of_a_navia_taxed_empty()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("clorinde", 4), ("navia", 1));

        var forecast = FurinaStage.Forecast(seat.Creature, null, OneEnemy);

        var bow = Assert.Single(forecast.Acts,
                                a => a.Who == StagePerformer.Navia);
        Assert.True(bow.Bow);
        Assert.Equal(1, bow.Amount);
        Assert.Equal("Geo", bow.Element);
    }

    [Fact]
    public void Her_bow_reads_the_exits_bar()
    {
        var calls = Il.Calls(Il.Method("FurinaStage", "GuestAct"));
        Assert.Contains("StageExit.get_Held", calls);
    }
}
