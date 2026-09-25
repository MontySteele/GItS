#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- the 2026-09-25 afternoon seat round (build
/// 0.2.3768), the mod's halves. Usher's Bow is Fanfare for the front
/// performer; a hit is counted the way the engine counts it (the Weak
/// off-by-one); and the part of a hit that reaches Furina is a beat on the
/// stage log. The sim twin is <c>tier0/tests/test_furina_stage.py</c> and the
/// page's halves are <c>tier0/tests/test_furina_seat_round_b_2026_09_25.py</c>.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype arm's arithmetic.
/// </summary>
public class FurinaStageSeatRoundBTests
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

    // ---- 1. Usher's Bow: 4 Fanfare to the front performer --------------------

    [Fact]
    public void Ushers_bow_raises_the_front_performer_and_gives_no_block()
    {
        // The payout awaits the pets, so it is read off IL; the sim twin runs
        // the four cases (hit-bow, lone Usher, Spend-bow, recast) for real.
        var bow = Il.CallSequence(Il.Method("FurinaStage", "Bow")).ToList();
        Assert.Contains("FurinaStage.RaiseLead", bow);
        Assert.DoesNotContain("CreatureCmd.GainBlock", bow);
        // The bow beat is filed BEFORE the Raise it pays, so the log reads
        // "Usher took a Bow" and then the gain.
        var note = bow.IndexOf("FurinaStage.NoteBeat");
        var raise = bow.IndexOf("FurinaStage.RaiseLead");
        Assert.True(note >= 0 && raise > note, string.Join(", ", bow));
        Assert.Equal(4, FurinaStageLaw.BowUsherFanfare);
    }

    [Fact]
    public void The_raise_his_bow_takes_summons_on_an_empty_stage()
    {
        // Rule 5's empty-stage summon, the door Thunderous Applause uses.
        var raiseLead = Il.Calls(Il.Method("FurinaStage", "RaiseLead"));
        Assert.Contains("FurinaStage.SummonForRaise", raiseLead);
    }

    [Fact]
    public void On_a_stage_he_left_the_front_is_whoever_stands_there_now()
    {
        using var _ = new Arm();
        // A hit emptied Usher at the front; Chevalmarin stepped up.
        var (_, stage) = Stage((StagePerformer.Usher, 2),
                               (StagePerformer.Chevalmarin, 3));
        stage.Absorb(2);
        Assert.Equal(StagePerformer.Chevalmarin, stage.Lead!.Who);

        Assert.Equal(4, stage.RaiseLead(FurinaStageLaw.BowUsherFanfare));
        Assert.Equal(7, stage.Lead!.Fanfare);
    }

    // ---- 2. The Weak off-by-one ----------------------------------------------

    [Fact]
    public void A_weakened_hit_is_counted_the_way_the_engine_counts_it()
    {
        // Fight 4 turn 1: a Weakened 11 against 6 Block. The engine hands
        // the hook 11 x 0.75 - 6 = 2.25 and would take 2 of her HP
        // (`Creature.LoseHpInternal` truncates); the seam rounded it up to 3.
        Assert.Equal(2, FurinaStage.HpLossThroughBlock(11m * 0.75m - 6m));
        Assert.Equal(0, FurinaStage.HpLossThroughBlock(0.75m));
        Assert.Equal(0, FurinaStage.HpLossThroughBlock(-1m));
        Assert.Equal(7, FurinaStage.HpLossThroughBlock(7m));

        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 3));
        var result = stage.Absorb(
            FurinaStage.HpLossThroughBlock(11m * 0.75m - 6m));
        Assert.Equal(2, result.Absorbed);
        Assert.Equal(0, result.ReachedFurina);
        Assert.Equal(1, stage.Lead!.Fanfare);
    }

    [Fact]
    public void The_damage_hook_truncates_through_the_one_helper()
    {
        var calls = Il.Calls(Il.Method("FurinaResourceHooks",
                                       "ModifyHpLostBeforeOsty"));
        Assert.Contains("FurinaStage.HpLossThroughBlock", calls);
        Assert.DoesNotContain("Math.Ceiling", calls);
    }

    // ---- 3. The part of a hit that reached her -------------------------------

    [Fact]
    public void A_hit_that_reached_her_is_a_beat_with_her_hp()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Usher, 3));
        stage.Absorb(9, "Seapunk", "2");       // 3 on Usher, 6 through
        stage.NoteHitOnFurina(6, 55, "Seapunk", "2");

        Assert.Equal(new[] { "hit", "leave", FurinaStageLedger.HitFurinaEvent },
                     stage.Beats.Select(b => b.Event).ToArray());
        var beat = stage.Beats[^1];
        Assert.Equal(6, beat.Moved);
        Assert.Equal(55, beat.Hp);
        Assert.Equal("Seapunk", beat.Target);

        var log = (List<object?>)FurinaStageLedger.Snapshot(seat.Player)["log"]!;
        var row = (Dictionary<string, object?>)log[^1]!;
        Assert.Equal("hit_furina", row["event"]);
        Assert.Equal("furina", row["member"]);
        Assert.Equal("Furina", row["name"]);
        Assert.Equal(6, row["moved"]);
        Assert.Equal(55, row["hp"]);
        Assert.Equal("2", row["target_id"]);
        // Every other beat carries no HP.
        Assert.Equal(-1, ((Dictionary<string, object?>)log[0]!)["hp"]);
    }

    [Fact]
    public void A_hit_that_took_no_hp_files_nothing()
    {
        using var _ = new Arm();
        var (_, stage) = Stage();
        stage.NoteHitOnFurina(0, 60, "Seapunk", "2");
        Assert.Empty(stage.Beats);
    }

    [Fact]
    public void The_beat_is_filed_after_the_hit_and_before_its_bow()
    {
        var received = Il.CallSequence(Il.Method("FurinaResourceHooks",
                                                 "AfterDamageReceived"))
            .ToList();
        var note = received.IndexOf("FurinaStage.NoteHitOnFurina");
        var flush = received.IndexOf("FurinaStage.Flush");
        Assert.True(note >= 0 && flush > note, string.Join(", ", received));
    }
}
