#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- the draft-3 seat round (two Opus seats, 0.2.3778),
/// the mod's halves of the page fixes: a Spend is a beat on the stage log,
/// Chevalmarin's act says what each enemy was dealt and how many it struck,
/// and a random summon names who it rolled on the card's own resolution row.
/// The waiting Bow is <c>FurinaStageHitBowTests</c>'. The page's halves are
/// <c>tier0/tests/test_furina_draft3_seat_fixes.py</c>.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype arm's arithmetic.
/// </summary>
public class FurinaStageDraft3SeatFixTests
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

    // ---- the Spend beat ----------------------------------------------------

    [Fact]
    public void A_spend_files_its_seat_its_amount_and_the_bar_after()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 8));

        stage.Spend(3);

        var beat = Assert.Single(stage.Beats);
        Assert.Equal(FurinaStageLedger.SpendEvent, beat.Event);
        Assert.Equal(StagePerformer.Usher, beat.Who);
        Assert.Equal(0, beat.Seat);
        Assert.Equal(3, beat.Moved);
        Assert.Equal(5, beat.Fanfare);
    }

    [Fact]
    public void A_spend_that_empties_the_bar_is_filed_before_the_leave()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 5),
                               (StagePerformer.Crabaletta, 3));

        stage.Spend(3);

        Assert.Equal(new[] { "spend", "leave" },
                     stage.Beats.Select(b => b.Event).ToArray());
        Assert.Equal(1, stage.Beats[0].Seat);
        Assert.Equal(0, stage.Beats[0].Fanfare);
    }

    [Fact]
    public void Spending_all_of_the_back_is_filed_too()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 5),
                               (StagePerformer.Chevalmarin, 7));

        stage.SpendAllOfBack();

        Assert.Equal(new[] { "spend", "leave" },
                     stage.Beats.Select(b => b.Event).ToArray());
        Assert.Equal(7, stage.Beats[0].Moved);
    }

    [Fact]
    public void A_short_bar_files_no_spend()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 1));

        stage.Spend(3);

        Assert.Empty(stage.Beats);
    }

    [Fact]
    public void The_spend_event_is_one_plain_word()
    {
        // #674's leak test refuses a snake_case event on the packet.
        Assert.Matches("^[a-z]+$", FurinaStageLedger.SpendEvent);
    }

    // ---- Chevalmarin's act ---------------------------------------------------

    [Fact]
    public void Chevalmarins_act_files_what_each_enemy_was_dealt_and_how_many()
    {
        // THE FINDING (lane 2, the floor-8 elite): "6 in total, split across
        // the enemies" against four Phantasmal Gardeners. The act is right --
        // it deals 2 to every hittable enemy -- and one Gardener's Skittish
        // Block, gained on its first hit that turn, ate its 2. The beat now
        // files the figure each hit carried (DealUnelemented's return, before
        // Block) and the count it struck; `Moved` is still what HP lost.
        var act = Il.Calls(Il.Method("FurinaStage", "Act"));
        Assert.Contains("FurinaStage.Even", act);
        Assert.Contains("ElementalHit.DealUnelemented", act);
        Assert.Equal(2, FurinaStage.Even(new[] { 2, 2, 2, 2 }));

        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Chevalmarin, 3));
        stage.Note(new StageBeat("act", StagePerformer.Chevalmarin, 0, 3, 6,
                                 "", Each: 2, Struck: 4));
        var log = (List<object?>)FurinaStageLedger.Snapshot(
            seat.Player)["log"]!;
        var row = (Dictionary<string, object?>)log[^1]!;
        Assert.Equal(2, row["each"]);
        Assert.Equal(4, row["struck"]);
        Assert.Equal(6, row["moved"]);
    }

    // ---- random summons name who they rolled ---------------------------------

    [Fact]
    public void Every_random_roll_names_its_performer_on_the_resolution_row()
    {
        Assert.Contains("FurinaStage.NoteSummoned",
                        Il.Calls(Il.Method("FurinaStage", "Summon")));
        Assert.Contains("FurinaStage.NoteSummoned",
                        Il.Calls(Il.Method("FurinaStage", "RecastFromFront")));
        Assert.Contains("FurinaStage.NoteSummoned",
                        Il.Calls(Il.Method("FurinaStage", "SummonForRaise")));
        Assert.Contains("ResolutionLedger.NoteSummon",
                        Il.Calls(Il.Method("FurinaStage", "NoteSummoned")));
    }
}
