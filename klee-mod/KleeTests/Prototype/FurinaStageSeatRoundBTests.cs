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
/// 0.2.3768), the mod's halves. Usher's Bow was Fanfare for the front
/// performer until draft 3 (2026-09-25) made every Bow the performer's act
/// once more; a hit is counted the way the engine counts it (the Weak
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

    // ---- 1. Usher's Bow: since draft 3, his act once more ------------------

    [Fact]
    public void Ushers_bow_is_his_act_and_raises_nobody()
    {
        // Draft 3 (2026-09-25) superseded round B's Fanfare Bow. The payout
        // awaits the pets, so it is read off IL; the sim twin runs the cases
        // (hit-bow, lone Usher, Spend-bow, recast) for real.
        var bow = Il.CallSequence(Il.Method("FurinaStage", "Bow")).ToList();
        Assert.Contains("FurinaStage.Act", bow);
        Assert.DoesNotContain("FurinaStage.RaiseLead", bow);
        // The act, then the readers.
        var act = bow.IndexOf("FurinaStage.Act");
        var after = bow.IndexOf("FurinaStage.AfterBow");
        Assert.True(act >= 0 && after > act, string.Join(", ", bow));
    }

    [Fact]
    public void The_raise_lead_door_still_summons_on_an_empty_stage()
    {
        // Rule 5's empty-stage summon, the door Hold Your Places uses.
        var raiseLead = Il.Calls(Il.Method("FurinaStage", "RaiseLead"));
        Assert.Contains("FurinaStage.SummonForRaise", raiseLead);
    }

    // ---- 1b. Let the People Rejoice never leaves two of one performer -------

    [Theory]
    [InlineData(StagePerformer.Usher)]
    [InlineData(StagePerformer.Chevalmarin)]
    [InlineData(StagePerformer.Crabaletta)]
    public void The_rares_return_never_brings_back_one_already_standing(
        StagePerformer picked)
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 5),
                               (StagePerformer.Chevalmarin, 2),
                               (StagePerformer.Crabaletta, 2));
        stage.CollectAll();
        var company = stage.TakePendingCurtainCall();
        // A Thunderous Applause Raise on the stage the card emptied: a random
        // arrival holding it (Usher's own Bow is Block since draft 3).
        const int applause = 2;
        stage.SummonOnEmpty(picked, applause);

        Assert.Equal(2, stage.ReturnCompany(company));

        var standing = stage.Seats.Select(s => s.Who).ToList();
        Assert.Equal(standing.Count, standing.Distinct().Count());
        Assert.Equal(FurinaStageLaw.Seats, standing.Count);
        Assert.Equal(picked, standing[0]);
        Assert.Equal(applause, stage.Seats[0].Fanfare);
        Assert.All(stage.Seats.Skip(1),
                   s => Assert.Equal(FurinaStageLaw.SummonFanfare, s.Fanfare));
    }

    [Fact]
    public void The_curtain_call_returns_through_the_one_guarded_door()
    {
        var calls = Il.Calls(Il.Method("FurinaStage", "CurtainCall"));
        Assert.Contains("FurinaStageLedger.ReturnCompany", calls);
        Assert.DoesNotContain("FurinaStageLedger.Summon", calls);
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
