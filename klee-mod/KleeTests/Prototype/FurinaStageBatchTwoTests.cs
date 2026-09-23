using System;
using System.Linq;
using System.Reflection;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- BATCH TWO (R276 pick 3), the rules its fifteen rows
/// add, pinned headlessly where the ledger answers and structurally where the
/// verb needs a live combat (a bow's draw, an act's Block).
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype arm's arithmetic.
/// </summary>
public class FurinaStageBatchTwoTests
{
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaStage.Enabled;

        internal Arm(bool on = true)
        {
            FurinaStageLedger.ResetAll();
            FurinaStage.Enabled = on;
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
        return (seat, stage);
    }

    private static T Held<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    // ---- Step Forward, Hold Your Places, Gala Dinner -----------------------

    [Fact]
    public void Step_forward_brings_the_back_performer_to_the_front()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(
            (StagePerformer.Usher, 2),
            (StagePerformer.Chevalmarin, 4),
            (StagePerformer.Crabaletta, 9));

        stage.StepForward();

        Assert.Equal(
            new[] { StagePerformer.Crabaletta, StagePerformer.Usher,
                    StagePerformer.Chevalmarin },
            stage.Seats.Select(s => s.Who).ToArray());
        Assert.Equal(9, stage.Lead!.Fanfare);
    }

    [Fact]
    public void Step_forward_with_one_performer_moves_nothing()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 3));

        stage.StepForward();

        Assert.Single(stage.Seats);
        Assert.Equal(3, stage.Lead!.Fanfare);
    }

    [Fact]
    public void A_raise_can_land_on_the_lead_or_on_every_performer()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(
            (StagePerformer.Usher, 2), (StagePerformer.Crabaletta, 4));

        Assert.Equal(2, stage.RaiseLead(2));
        Assert.Equal(4, stage.Lead!.Fanfare);
        Assert.Equal(4, stage.Back!.Fanfare);

        Assert.Equal(6, stage.RaiseAll(3));
        Assert.Equal(7, stage.Lead!.Fanfare);
        Assert.Equal(7, stage.Back!.Fanfare);
    }

    // ---- Bravura ------------------------------------------------------------

    [Fact]
    public void Bravura_spends_the_whole_back_bar_and_the_performer_bows()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(
            (StagePerformer.Chevalmarin, 4), (StagePerformer.Usher, 6));

        var result = stage.SpendAllOfBack();

        Assert.True(result.Fired);
        Assert.Equal(6, result.Paid);
        Assert.Equal(6, stage.SpentThisPlay);
        Assert.Equal(StagePerformer.Usher, result.Exit!.Value.Who);
        Assert.True(result.Exit!.Value.Bows);
        Assert.Single(stage.Seats);
    }

    [Fact]
    public void Bravura_on_an_empty_stage_spends_nothing()
    {
        using var _ = new Arm();
        var (_, stage) = Stage();

        var result = stage.SpendAllOfBack();

        Assert.False(result.Fired);
        Assert.Equal(0, result.Paid);
    }

    // ---- Ensemble Piece -----------------------------------------------------

    [Fact]
    public void Ensemble_piece_reads_how_many_performers_are_on_stage()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(
            (StagePerformer.Usher, 1), (StagePerformer.Chevalmarin, 1));
        var card = Held<ProtoFsEnsemblePiece>(seat);

        Assert.Equal(2, FurinaStage.Count(card));
    }

    // ---- A Five-Century Act -------------------------------------------------

    [Fact]
    public void A_returnee_takes_the_back_seat_at_one_and_rests()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Chevalmarin, 4));

        Assert.True(stage.ReturnToBack(StagePerformer.Usher));

        Assert.Equal(StagePerformer.Usher, stage.Back!.Who);
        Assert.Equal(FurinaStageLaw.SummonFanfare, stage.Back!.Fanfare);
        Assert.True(stage.Back!.Resting);
        stage.EndRest();
        Assert.False(stage.Back!.Resting);
    }

    [Fact]
    public void A_full_stage_has_no_seat_to_return_to()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(
            (StagePerformer.Usher, 1), (StagePerformer.Chevalmarin, 1),
            (StagePerformer.Crabaletta, 1));

        Assert.False(stage.ReturnToBack(StagePerformer.Usher));
        Assert.Equal(3, stage.Seats.Count);
    }

    // ---- Arkhe Alignment ----------------------------------------------------

    [Fact]
    public void Ousia_doubles_this_turns_act_damage()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Usher, 3));

        ArkheAlignmentPower.Choose(seat.Creature, pneuma: false);

        Assert.Equal(2, stage.ActDamageMultiplier);
        Assert.Equal(1, stage.ActBlockMultiplier);
        Assert.Equal(3, stage.Lead!.Fanfare);
    }

    [Fact]
    public void Pneuma_doubles_this_turns_act_block_and_the_lead_regains_two()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(
            (StagePerformer.Usher, 3), (StagePerformer.Crabaletta, 1));

        ArkheAlignmentPower.Choose(seat.Creature, pneuma: true);

        Assert.Equal(1, stage.ActDamageMultiplier);
        Assert.Equal(2, stage.ActBlockMultiplier);
        Assert.Equal(3 + ArkheAlignmentPower.PneumaLeadRegain,
                     stage.Lead!.Fanfare);
        Assert.Equal(1, stage.Back!.Fanfare);

        stage.ResetActMultipliers();
        Assert.Equal(1, stage.ActBlockMultiplier);
    }

    [Fact]
    public void Two_copies_add_to_times_three_and_regain_two_each()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Usher, 3));

        ArkheAlignmentPower.Choose(seat.Creature, pneuma: true, copies: 2);

        Assert.Equal(3, stage.ActBlockMultiplier);
        Assert.Equal(3 + 2 * ArkheAlignmentPower.PneumaLeadRegain,
                     stage.Lead!.Fanfare);

        stage.ResetActMultipliers();
        ArkheAlignmentPower.Choose(seat.Creature, pneuma: false, copies: 2);
        Assert.Equal(3, stage.ActDamageMultiplier);
    }

    [Fact]
    public void Arkhe_asks_one_question_a_turn()
    {
        // Not instanced: a second copy stacks onto the first, so the power
        // has ONE turn-start hook and asks once, with Amount as the copies.
        Assert.Equal(MegaCrit.Sts2.Core.Entities.Powers.PowerInstanceType.None,
                     new ArkheAlignmentPower().InstanceType);
        var calls = Il.Calls(
            Il.Method("ArkheAlignmentPower", "AfterPlayerTurnStart"));
        Assert.Contains("PowerModel.get_Amount", calls);
    }

    // ---- the seat page's forecast ------------------------------------------

    [Fact]
    public void The_act_block_forecast_reads_arkhe_full_house_and_rest()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(
            (StagePerformer.Usher, 3), (StagePerformer.Chevalmarin, 1));

        Assert.Equal(FurinaStageLaw.ActUsherBlock,
                     FurinaStage.ForecastActBlock(seat.Creature));

        ArkheAlignmentPower.Choose(seat.Creature, pneuma: true);
        Assert.Equal(2 * FurinaStageLaw.ActUsherBlock,
                     FurinaStage.ForecastActBlock(seat.Creature));

        // A full stage with Full House: each act twice.
        seat.WithPower<FullHousePower>(1);
        stage.Summon(StagePerformer.Crabaletta);
        Assert.Equal(2 * 2 * FurinaStageLaw.ActUsherBlock,
                     FurinaStage.ForecastActBlock(seat.Creature));

        // A resting Usher pays nothing this turn.
        Seat.Set(stage.Lead!, "Resting", true);
        Assert.Equal(0, FurinaStage.ForecastActBlock(seat.Creature));
    }

    [Fact]
    public void The_wire_snapshot_carries_the_forecast()
    {
        using var _ = new Arm();
        var (seat, _) = Stage((StagePerformer.Usher, 3));

        var snapshot = FurinaStageLedger.Snapshot(seat.Player);

        Assert.Equal(FurinaStageLaw.ActUsherBlock, snapshot["act_block"]);
    }

    // ---- Full House ---------------------------------------------------------

    [Fact]
    public void Full_house_counts_one_extra_act_per_copy()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithPower<FullHousePower>(2);
        var acts = typeof(FurinaStage).GetMethod(
            "FullHouseActs", BindingFlags.NonPublic | BindingFlags.Static)!;

        Assert.Equal(2, (int)acts.Invoke(null, new object[] { seat.Creature })!);
    }

    // ---- The structural half: what needs a live combat ----------------------

    [Fact]
    public void The_sweep_reads_full_house_skips_the_resting_and_resets()
    {
        var calls = Il.Calls(Il.Method("FurinaStage", "EndOfTurnActs"));
        Assert.Contains("FurinaStageLedger.get_IsFull", calls);
        Assert.Contains("StageSeat.get_Resting", calls);
        Assert.Contains("FurinaStageLedger.EndRest", calls);
        Assert.Contains("FurinaStageLedger.ResetActMultipliers", calls);
    }

    [Fact]
    public void An_act_reads_the_arkhe_multipliers()
    {
        var calls = Il.Calls(Il.Method("FurinaStage", "Perform"));
        Assert.Contains("FurinaStageLedger.get_ActDamageMultiplier", calls);
        Assert.Contains("FurinaStageLedger.get_ActBlockMultiplier", calls);
    }

    [Fact]
    public void A_bow_draws_raises_and_returns_after_it_has_left()
    {
        var bow = Il.Calls(Il.Method("FurinaStage", "Bow"));
        Assert.Contains("FurinaStage.AfterBow", bow);
        var after = Il.Calls(Il.Method("FurinaStage", "AfterBow"));
        Assert.Contains("CardPileCmd.Draw", after);
        Assert.Contains("FurinaStage.Raise", after);
        Assert.Contains("FurinaStageLedger.ReturnToBack", after);
    }

    [Fact]
    public void A_rapt_audience_answers_only_an_enemys_hit()
    {
        var calls = Il.Calls(Il.Method("FurinaStage", "AbsorbHit"));
        Assert.Contains("FurinaStageLedger.Absorb", calls);
        Assert.Contains("Creature.get_IsEnemy", calls);
        Assert.Contains("FurinaStageLedger.Raise", calls);
    }

    [Fact]
    public void A_rapt_audience_with_no_enemy_behind_the_hit_raises_nothing()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(
            (StagePerformer.Usher, 9), (StagePerformer.Crabaletta, 1));
        seat.WithPower<RaptAudiencePower>(50);

        var reached = FurinaStage.AbsorbHit(seat.Creature, 5, dealer: null);

        Assert.Equal(0, reached);
        Assert.Equal(4, stage.Lead!.Fanfare);
        Assert.Equal(1, stage.Back!.Fanfare);
    }
}
