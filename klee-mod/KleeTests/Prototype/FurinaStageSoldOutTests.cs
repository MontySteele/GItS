using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- SOLD OUT, THE FOURTH SEAT (the supporting pool,
/// 2026-09-26, family 7 of
/// <c>review/active/furina-supporting-pool-2026-09-26.md</c>): "Your stage
/// has a fourth seat." Front, two middles, back, for the rest of the combat.
///
/// Pinned headlessly on the ledger, which is where every seat rule lives:
/// the capacity, rule 3's recast at four, Wriothesley's front-join at four,
/// Full House needing four, the fade on both middles, and the line's x
/// positions for four bodies. Sim twin:
/// <c>tier0/tests/test_furina_sold_out.py</c>.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype arm's arithmetic.
/// </summary>
public class FurinaStageSoldOutTests
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

    /// <summary>A Furina with Sold Out on her (or not), and her stage filled
    /// front first with these bars.</summary>
    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        bool soldOut, params (StagePerformer Who, int Fanfare)[] seats)
    {
        var seat = Seat.Furina().WithCombatState();
        if (soldOut) seat.WithPower<SoldOutPower>(1);
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        foreach (var (who, fanfare) in seats)
        {
            stage.Summon(who);
            stage.Raise(fanfare - FurinaStageLaw.SummonFanfare);
        }
        return (seat, stage);
    }

    private static StagePerformer[] Cast(FurinaStageLedger stage) =>
        stage.Seats.Select(s => s.Who).ToArray();

    private static int[] Bars(FurinaStageLedger stage) =>
        stage.Seats.Select(s => s.Fanfare).ToArray();

    // ---- the capacity ------------------------------------------------------

    [Fact]
    public void The_stage_has_three_seats_and_four_after_the_power()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        Assert.Equal(FurinaStageLaw.Seats, stage.Capacity);
        Assert.Equal(3, FurinaStageLaw.Seats);

        // Read live off her powers: the SAME ledger object sees the power
        // the moment it is on her, with no second writer to keep in step.
        seat.WithPower<SoldOutPower>(1);
        Assert.Equal(FurinaStageLaw.SoldOutSeats, stage.Capacity);
        Assert.Equal(4, FurinaStageLaw.SoldOutSeats);
        Assert.Equal(4, FurinaStage.CapacityOf(seat.Creature));
    }

    [Fact]
    public void A_second_copy_opens_no_fifth_seat()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState()
            .WithPower<SoldOutPower>(1).WithPower<SoldOutPower>(1);
        Assert.Equal(4, FurinaStageLedger.For(seat.Creature).Capacity);

        var stacked = Seat.Furina().WithCombatState().WithPower<SoldOutPower>(2);
        Assert.Equal(4, FurinaStageLedger.For(stacked.Creature).Capacity);
    }

    [Fact]
    public void Nobody_is_three_seats_without_a_furina()
    {
        Assert.Equal(FurinaStageLaw.Seats, FurinaStage.CapacityOf(null));
    }

    [Fact]
    public void Three_performers_are_not_a_full_stage_under_sold_out()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(true,
            (StagePerformer.Usher, 3), (StagePerformer.Chevalmarin, 1),
            (StagePerformer.Crabaletta, 1));
        Assert.False(stage.IsFull);

        // Rule 3: the fourth summon fills the fourth seat, at the back, at 1.
        stage.Summon(StagePerformer.Usher);
        Assert.True(stage.IsFull);
        Assert.Equal(
            new[] { StagePerformer.Usher, StagePerformer.Chevalmarin,
                    StagePerformer.Crabaletta, StagePerformer.Usher },
            Cast(stage));
        Assert.Equal(new[] { 3, 1, 1, 1 }, Bars(stage));
    }

    // ---- rule 3 at four ----------------------------------------------------

    [Fact]
    public void A_summon_on_a_full_four_stage_recasts_the_front()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(true,
            (StagePerformer.Usher, 6), (StagePerformer.Chevalmarin, 2),
            (StagePerformer.Crabaletta, 3), (StagePerformer.Usher, 4));

        // On three seats this stage would be full already; with four it is
        // only full now, and the recast takes the lead off.
        var leaver = stage.BowFromFront();
        Assert.NotNull(leaver);
        Assert.Equal(StagePerformer.Usher, leaver!.Who);
        Assert.Equal(6, leaver.Fanfare);
        Assert.Equal(
            new[] { StagePerformer.Chevalmarin, StagePerformer.Crabaletta,
                    StagePerformer.Usher },
            Cast(stage));

        // The newcomer takes the fourth seat, the back one, holding the
        // leaver's bar plus its own 1.
        Assert.True(stage.ArriveAtBack(StagePerformer.Crabaletta,
                                       leaver.Fanfare + FurinaStageLaw.SummonFanfare));
        Assert.Equal(
            new[] { StagePerformer.Chevalmarin, StagePerformer.Crabaletta,
                    StagePerformer.Usher, StagePerformer.Crabaletta },
            Cast(stage));
        Assert.Equal(new[] { 2, 3, 4, 7 }, Bars(stage));
        Assert.True(stage.IsFull);
    }

    [Fact]
    public void Three_seated_under_sold_out_do_not_recast()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(true,
            (StagePerformer.Usher, 3), (StagePerformer.Chevalmarin, 1),
            (StagePerformer.Crabaletta, 1));
        Assert.Null(stage.BowFromFront());
        Assert.Null(stage.BowFromBack());
        Assert.Equal(3, stage.Seats.Count);
    }

    [Fact]
    public void The_ledger_summon_rotates_only_at_four()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(true,
            (StagePerformer.Usher, 5), (StagePerformer.Chevalmarin, 1),
            (StagePerformer.Crabaletta, 1));

        var fourth = stage.Summon(StagePerformer.Chevalmarin);
        Assert.Null(fourth.Exit);
        var fifth = stage.Summon(StagePerformer.Crabaletta);
        Assert.NotNull(fifth.Exit);
        Assert.Equal(StagePerformer.Usher, fifth.Exit!.Value.Who);
        Assert.Equal(4, stage.Seats.Count);
        Assert.Equal(5, stage.Back!.Fanfare);
    }

    // ---- Wriothesley's front-join at four -----------------------------------

    [Fact]
    public void Wriothesley_joins_a_full_four_stage_and_the_back_performer_leaves()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(true,
            (StagePerformer.Usher, 3), (StagePerformer.Chevalmarin, 2),
            (StagePerformer.Crabaletta, 2), (StagePerformer.Usher, 5));

        var leaver = stage.BowFromBack();
        Assert.NotNull(leaver);
        Assert.Equal(StagePerformer.Usher, leaver!.Who);
        Assert.Equal(5, leaver.Fanfare);
        // The seat it left is the back one of FOUR: its index is the count
        // left standing, which `RecastFromBack` reads for the Bow.
        Assert.Equal(3, stage.Seats.Count);

        Assert.True(stage.ArriveAtFront(StagePerformer.Wriothesley,
                                        8 + leaver.Fanfare));
        Assert.Equal(
            new[] { StagePerformer.Wriothesley, StagePerformer.Usher,
                    StagePerformer.Chevalmarin, StagePerformer.Crabaletta },
            Cast(stage));
        Assert.Equal(new[] { 13, 3, 2, 2 }, Bars(stage));
    }

    [Fact]
    public void Wriothesley_joins_a_stage_of_three_under_sold_out_without_a_recast()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(true,
            (StagePerformer.Usher, 3), (StagePerformer.Chevalmarin, 2),
            (StagePerformer.Crabaletta, 2));

        Assert.True(stage.GuestArrives(StagePerformer.Wriothesley, 8,
                                       atFront: true));
        Assert.Equal(
            new[] { StagePerformer.Wriothesley, StagePerformer.Usher,
                    StagePerformer.Chevalmarin, StagePerformer.Crabaletta },
            Cast(stage));
    }

    [Fact]
    public void The_front_join_recast_reads_the_seat_it_left_off_the_stage()
    {
        // Not the law's `Seats - 1`, which is the back seat of THREE.
        var calls = Il.Calls(Il.Method("FurinaStage", "RecastFromBack"));
        Assert.Contains("FurinaStageLedger.get_Seats", calls);
    }

    // ---- Full House needs every seat ---------------------------------------

    [Fact]
    public void Full_house_needs_four_under_sold_out()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(true,
            (StagePerformer.Usher, 3), (StagePerformer.Chevalmarin, 1),
            (StagePerformer.Crabaletta, 1));
        seat.WithPower<FullHousePower>(1);

        // Three seated of four: Usher acts once.
        Assert.Equal(FurinaStageLaw.ActUsherBlock,
                     FurinaStage.ForecastActBlock(seat.Creature));

        // Every seat filled: each act twice.
        stage.Summon(StagePerformer.Crabaletta);
        Assert.Equal(2 * FurinaStageLaw.ActUsherBlock,
                     FurinaStage.ForecastActBlock(seat.Creature));
    }

    [Fact]
    public void Full_house_at_three_without_sold_out_is_unchanged()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(false,
            (StagePerformer.Usher, 3), (StagePerformer.Chevalmarin, 1),
            (StagePerformer.Crabaletta, 1));
        seat.WithPower<FullHousePower>(1);
        Assert.Equal(2 * FurinaStageLaw.ActUsherBlock,
                     FurinaStage.ForecastActBlock(seat.Creature));
    }

    [Fact]
    public void The_forecast_clone_keeps_the_fourth_seat()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(true,
            (StagePerformer.Usher, 3), (StagePerformer.Chevalmarin, 1),
            (StagePerformer.Crabaletta, 1));
        var clone = (FurinaStageLedger)typeof(FurinaStageLedger)
            .GetMethod("CloneForForecast", HeadlessGame.All)!
            .Invoke(stage, Array.Empty<object>())!;
        Assert.Equal(4, clone.Capacity);
        Assert.False(clone.IsFull);
    }

    [Fact]
    public void Full_house_says_every_seat()
    {
        Assert.Equal(
            "If every seat is filled at the end of your turn, your performers "
          + "act [blue]{Amount}[/blue] more {Amount:plural:time|times}.",
            Loc<FullHousePower>("description"));
        Assert.Equal(
            "If every seat is filled at the end of your turn, your performers "
          + "act twice.",
            Loc<ProtoFsFullHouse>("description"));
    }

    // ---- the fade reaches both middles --------------------------------------

    [Fact]
    public void Both_middle_seats_and_the_back_fade_and_the_front_does_not()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(true,
            (StagePerformer.Usher, 9), (StagePerformer.Chevalmarin, 9),
            (StagePerformer.Crabaletta, 11), (StagePerformer.Usher, 7));

        // Half of each bar above 5, rounded down: 9 -> 7, 11 -> 8, 7 -> 6.
        Assert.Equal(2 + 3 + 1, stage.Fade());
        Assert.Equal(new[] { 9, 7, 8, 6 }, Bars(stage));
    }

    // ---- the line: four bodies, the same gap --------------------------------

    /// <summary>
    /// THE NUMBERS, off the 0.111.0 decompile (<c>NCombatRoom</c>). A solo
    /// Furina at the default camera scaling (1) stands at
    /// <c>-(960 - 240) / 2 - 240 / 2 = -480</c>, so her box runs -600 to
    /// -360. The enemies' line starts at <c>max((960 - width) / 2, 150)</c>,
    /// and the screen's right edge is +960.
    /// </summary>
    private const float FurinaX = -480f;

    private const float FurinaHalf = 120f;

    [Fact]
    public void A_fourth_performer_stands_in_line_with_the_same_gap()
    {
        // The trio plus a second Usher, back first: 121 / 120 / 129 / 121.
        var widths = new[] { 121f, 120f, 129f, 121f };
        var centres = FurinaStagePlacement.LineCentres(FurinaX, FurinaHalf,
                                                       widths);

        Assert.Equal(new[] { -279.5f, -139f, 5.5f, 150.5f }, centres);
        for (var i = 1; i < widths.Length; i++)
        {
            var gap = (centres[i] - widths[i] * 0.5f)
                    - (centres[i - 1] + widths[i - 1] * 0.5f);
            Assert.Equal(FurinaStagePlacement.Gap, gap, 3);
        }
        // The lead's right edge, 211, is on screen by a long way (the right
        // edge is 960), and past the 150 floor where the widest enemy
        // formations start: see the report for the overlap this implies.
        var frontRight = centres[^1] + widths[^1] * 0.5f;
        Assert.Equal(211f, frontRight, 3);
        Assert.True(frontRight < 960f);
    }

    [Fact]
    public void The_widest_four_stay_on_screen()
    {
        // Four Chevalmarins, the widest body (129): the longest line a Sold
        // Out stage can stand.
        var widths = new[] { 129f, 129f, 129f, 129f };
        var centres = FurinaStagePlacement.LineCentres(FurinaX, FurinaHalf,
                                                       widths);
        var frontRight = centres[^1] + widths[^1] * 0.5f;
        Assert.Equal(-360f + 4 * 129f + 4 * FurinaStagePlacement.Gap,
                     frontRight, 3);
        Assert.True(frontRight < 960f);
    }

    // ---- the card, the power, the badge, the pool ---------------------------

    [Fact]
    public void The_card_is_the_papers_row()
    {
        Assert.Equal("Sold Out", Loc<ProtoFsSoldOut>("title"));
        Assert.Equal("Your stage has a fourth seat.",
                     Loc<ProtoFsSoldOut>("description"));
        Assert.Equal("Your stage has a fourth seat.",
                     Loc<SoldOutPower>("description"));
        Assert.Contains("PowerCmd.Apply<SoldOutPower>",
                        Il.CallSequence(Il.Method("ProtoFsSoldOut", "OnPlay")));
    }

    [Fact]
    public void The_stage_badge_prints_the_live_seat_count()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState()
            .WithPower<StageSummaryPower>(1);
        var badge = seat.Creature.Powers.OfType<StageSummaryPower>().Single();
        Assert.StartsWith("Up to {Seats} performers.",
                          Loc<StageSummaryPower>("smartDescription"));
        Assert.Equal(3, LiveSeats(badge));

        seat.WithPower<SoldOutPower>(1);
        Assert.Equal(4, LiveSeats(badge));
    }

    [Fact]
    public void The_arm_offers_sold_out_in_place_of_unheard_confession()
    {
        var pool = ArmPools.Offerable("furina-stage");
        Assert.Contains(pool, c => c is ProtoFsSoldOut);
        Assert.DoesNotContain(
            pool, c => c is global::KleeMod.Cards.Furina.Generated.UnheardConfession);
    }

    private static string Loc<T>(string key)
    {
        var model = RuntimeHelpers.GetUninitializedObject(typeof(T));
        var rows = (List<(string, string)>)typeof(T)
            .GetProperty("Localization")!.GetValue(model)!;
        return rows.Single(r => r.Item1 == key).Item2;
    }

    private static int LiveSeats(StageSummaryPower badge) =>
        (int)typeof(StageSummaryPower)
            .GetMethod("LiveSeats", HeadlessGame.All)!
            .Invoke(badge, Array.Empty<object>())!;
}
