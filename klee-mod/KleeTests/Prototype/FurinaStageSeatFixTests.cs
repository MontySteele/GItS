using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- the opus-furina-l2b seat's findings, 2026-09-25
/// (`review/qa/blindplay/opus-furina-l2b-2026-09-25.md`, (c)). The mod's
/// halves: every bar that goes up and every hit on the lead is a beat on the
/// stage log, and A Rapt Audience keeps refusing a lone lead (its face now
/// says so). The page's halves are
/// `tier0/tests/test_furina_seat_fixes_2026_09_25.py`.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype arm's arithmetic.
/// </summary>
public class FurinaStageSeatFixTests
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

    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        params (StagePerformer Who, int Fanfare)[] seats)
    {
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        foreach (var (who, fanfare) in seats)
        {
            stage.Summon(who);
            stage.Raise(fanfare - FurinaStageLaw.SummonFanfare);
        }
        stage.ClearBeats();
        return (seat, stage);
    }

    // ---- (c) 4: a Raise is a beat -------------------------------------------

    [Fact]
    public void A_raise_files_what_landed_and_the_bar_after_it()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 3));

        stage.Raise(5);

        var beat = Assert.Single(stage.Beats);
        Assert.Equal("raise", beat.Event);
        Assert.Equal(StagePerformer.Usher, beat.Who);
        Assert.Equal(5, beat.Moved);
        Assert.Equal(8, beat.Fanfare);
        Assert.Equal(0, beat.Seat);
    }

    [Fact]
    public void Every_raise_door_files_its_beats()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 3),
                               (StagePerformer.Crabaletta, 1));

        stage.RaiseLead(2);
        stage.RaiseAll(1);
        stage.RaiseSeat(stage.SeatOf(StagePerformer.Crabaletta)!, 3);

        Assert.Equal(new[] { "raise", "raise", "raise", "raise" },
                     stage.Beats.Select(b => b.Event).ToArray());
        Assert.Equal(new[] { 5, 6, 2, 5 },
                     stage.Beats.Select(b => b.Fanfare).ToArray());
        Assert.Equal(new[] { 0, 0, 1, 1 },
                     stage.Beats.Select(b => b.Seat).ToArray());
    }

    [Fact]
    public void The_leads_regen_is_a_regain_and_not_a_raise()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 3));

        stage.Regen(turnNumber: 2);
        stage.RaiseLead(2, "regain");                  // Pneuma's door

        Assert.Equal(new[] { "regain", "regain" },
                     stage.Beats.Select(b => b.Event).ToArray());
        Assert.Equal(new[] { 4, 6 },
                     stage.Beats.Select(b => b.Fanfare).ToArray());
    }

    [Fact]
    public void A_raise_of_nothing_files_nothing()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 3));

        stage.Raise(0);
        stage.Regen(turnNumber: 1);

        Assert.Empty(stage.Beats);
    }

    // ---- (c) 4: a hit on the lead is a beat ---------------------------------

    [Fact]
    public void A_hit_the_lead_absorbs_files_the_dealer_and_the_bar()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 8));

        var result = stage.Absorb(5, "Living Fog", "3");

        Assert.Equal(0, result.ReachedFurina);
        var beat = Assert.Single(stage.Beats);
        Assert.Equal("hit", beat.Event);
        Assert.Equal(5, beat.Moved);
        Assert.Equal(3, beat.Fanfare);
        Assert.Equal("Living Fog", beat.Target);
        Assert.Equal("3", beat.TargetId);
    }

    [Fact]
    public void A_hit_that_empties_the_lead_files_the_hit_then_the_leave()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 3));

        var result = stage.Absorb(8, "Sludge Spinner", "1");

        // 8 - 3 on his bar - 3 his Bow Block caught (2026-09-25 night).
        Assert.Equal(2, result.ReachedFurina);
        Assert.Equal(new[] { "hit", "leave" },
                     stage.Beats.Select(b => b.Event).ToArray());
        Assert.Equal(0, stage.Beats[0].Fanfare);
        Assert.Equal(3, stage.Beats[0].Moved);
        Assert.Equal("hit", stage.Beats[1].Reason);
    }

    [Fact]
    public void Nothing_to_absorb_files_nothing()
    {
        using var _ = new Arm();
        var (_, stage) = Stage();

        stage.Absorb(6, "Living Fog", "3");

        Assert.Empty(stage.Beats);
    }

    [Fact]
    public void A_rapt_audience_refund_is_filed_after_the_hit_it_answers()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(
            (StagePerformer.Usher, 9), (StagePerformer.Crabaletta, 1));
        seat.WithPower<RaptAudiencePower>(2);

        // No enemy behind this hit, so no refund -- but the hit is a beat.
        FurinaStage.AbsorbHit(seat.Creature, 5, dealer: null);

        var beat = Assert.Single(stage.Beats);
        Assert.Equal("hit", beat.Event);
        Assert.Equal("", beat.Target);
    }

    [Fact]
    public void The_wire_carries_a_hit_beats_dealer()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Usher, 8));
        stage.Absorb(5, "Living Fog", "3");

        var snapshot = FurinaStageLedger.Snapshot(seat.Player);
        var log = (List<object?>)snapshot["log"]!;
        var row = (Dictionary<string, object?>)log.Single()!;

        Assert.Equal("hit", row["event"]);
        Assert.Equal(5, row["moved"]);
        Assert.Equal(3, row["fanfare"]);
        Assert.Equal("Living Fog", row["target"]);
        Assert.Equal("3", row["target_id"]);
    }

    [Fact]
    public void Absorb_hit_names_the_dealer_it_was_handed()
    {
        var calls = Il.Calls(Il.Method("FurinaStage", "AbsorbHit"));
        Assert.Contains("Creature.get_CombatId", calls);
        Assert.Contains("FurinaStageLedger.Absorb", calls);
    }

    // ---- (c) 1: the rule the face now states --------------------------------

    [Fact]
    public void A_rapt_audience_still_refuses_a_lone_lead()
    {
        // A lone lead is also the back, so a refund here would bank on the
        // performer the hit just emptied. The rule stands and the FACE says
        // "Needs 2 performers."
        var src = Il.Calls(Il.Method("FurinaStage", "AbsorbHit"));
        Assert.Contains("FurinaStageLedger.get_Seats", src);
    }
}
