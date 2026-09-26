#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA'S TURN PREDICTOR AS CUES (the Furina balance review, 2026-09-26,
/// pick 2a): "each performer shows its act over its head the way an enemy
/// shows its intent; the fade and incoming hits show as chips on its bar; the
/// text box goes."
///
/// WHAT IS REAL HERE: the cue and chip for every performer on a scripted
/// board (<see cref="FurinaStageCues.From"/> over
/// <see cref="FurinaStage.Forecast"/>), each number checked against the
/// forecast it came from and, for the Fanfare, against the ledger's own
/// end-of-turn moves run for real on the same stage. The acts' damage and
/// Block need a live combat this harness does not have; the drawing needs a
/// combat room (KleeTests/README.md, the headless boundary).
/// </summary>
public class FurinaStageCueTests
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

    private static StagePerformer P(string member) => FurinaStage.Parse(member);

    /// <summary>A stage of these seats, front first. Guests arrive holding
    /// their bar; the trio are summoned and raised.</summary>
    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        Seat seat, params (string Member, int Fanfare)[] seats)
    {
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        foreach (var (member, fanfare) in seats)
        {
            var who = P(member);
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

    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        params (string Member, int Fanfare)[] seats) =>
        Stage(Seat.Furina().WithCombatState(), seats);

    private static (StageForecast Forecast, StageCueBoard Board) Read(
        Seat seat, params int[] hits)
    {
        var forecast = FurinaStage.Forecast(seat.Creature, hits);
        return (forecast, FurinaStageCues.From(forecast));
    }

    /// <summary>
    /// THE REAL END OF TURN, Fanfare half: every seat's act payment through
    /// the ledger's own <see cref="FurinaStageLedger.ActFanfare"/> (the move
    /// <c>EndOfTurnActs</c> makes, once per act), then the fade. The bars it
    /// leaves are what the chips promised.
    /// </summary>
    private static int[] RealEndOfTurn(FurinaStageLedger stage, int times = 1)
    {
        foreach (var seat in stage.Seats.ToList())
        {
            for (var i = 0; i < times; i++)
            {
                if (!stage.Holds(seat)) break;
                stage.ActFanfare(seat.Who, seat, null, new List<StageExit>());
            }
        }
        stage.Fade();
        return stage.Seats.Select(s => s.Fanfare).ToArray();
    }

    // ==================================================================
    // 1. The cue, per kind of act.
    // ==================================================================

    [Fact]
    public void Usher_shows_a_block_cue_of_his_block()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("usher", 3));
        var (forecast, board) = Read(seat);

        var cue = Assert.Single(board.Cues);
        Assert.Equal(StageCueIcon.Block, cue.Icon);
        Assert.Equal(FurinaStageLaw.ActUsherBlock, cue.Number);
        Assert.Equal(forecast.BlockAfterActs, cue.Number);
        Assert.Equal(1, cue.Times);
        Assert.False(cue.Greyed);
        Assert.Equal(0, cue.Price);
        Assert.Equal("", cue.Element);
    }

    [Fact]
    public void Chevalmarin_shows_per_enemy_damage_to_all_and_crabaletta_one_target()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("chevalmarin", 3), ("crabaletta", 3));
        var (forecast, board) = Read(seat);

        Assert.Equal(new[] { StageCueIcon.Attack, StageCueIcon.Attack },
                     board.Cues.Select(c => c.Icon).ToArray());
        Assert.Equal(forecast.Acts.Select(a => a.Amount).ToArray(),
                     board.Cues.Select(c => c.Number).ToArray());
        Assert.Equal(new[] { FurinaStageLaw.ActChevalmarinDamage,
                             FurinaStageLaw.ActCrabalettaDamage },
                     board.Cues.Select(c => c.Number).ToArray());
        Assert.Equal(new[] { true, false },
                     board.Cues.Select(c => c.All).ToArray());
        // The trio's damage carries no element.
        Assert.All(board.Cues, c => Assert.Equal("", c.Element));
    }

    [Fact]
    public void Neuvillette_shows_hydro_to_all_with_his_price_and_his_bar_a_gold_chip()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("neuvillette", 6), ("usher", 3));
        var (forecast, board) = Read(seat);

        var neuv = board.Cues[0];
        Assert.Equal(StageCueIcon.Attack, neuv.Icon);
        Assert.Equal(FurinaStageLaw.ActNeuvilletteDamage, neuv.Number);
        Assert.Equal("Hydro", neuv.Element);
        Assert.True(neuv.All);
        Assert.Equal(FurinaStageLaw.ActNeuvillettePrice, neuv.Price);
        Assert.False(neuv.Greyed);
        Assert.Equal("Pays 3 of his Fanfare: 6 → 3.", neuv.Forecast);

        // The price, on his bar, in gold.
        Assert.Equal(FurinaStageLaw.ActNeuvillettePrice, board.Bars[0].Paid);
        Assert.Equal(0, board.Bars[1].Paid);

        // And the real end of turn takes exactly that.
        Assert.Equal(forecast.Seats.Select(r => r.After).ToArray(),
                     RealEndOfTurn(stage));
    }

    [Fact]
    public void Each_guest_damage_cue_carries_its_element()
    {
        using var _ = new Arm();
        var cases = new (string Member, string Element)[]
        {
            ("neuvillette", "Hydro"), ("clorinde", "Electro"),
            ("navia", "Geo"), ("lynette", "Anemo"),
        };
        foreach (var (member, element) in cases)
        {
            var (seat, _) = Stage((member, 6), ("usher", 3));
            var (_, board) = Read(seat);
            Assert.Equal(element, board.Cues[0].Element);
            Assert.Equal(StageCueIcon.Attack, board.Cues[0].Icon);
        }
    }

    [Fact]
    public void Navia_shows_her_bar_as_her_damage()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("navia", 7), ("usher", 3));
        var (forecast, board) = Read(seat);
        Assert.Equal(7, board.Cues[0].Number);
        Assert.Equal(forecast.Acts[0].Amount, board.Cues[0].Number);
        Assert.False(board.Cues[0].All);
    }

    [Fact]
    public void Clorindes_tax_is_a_gold_chip_on_each_other_bar_and_not_her_price()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("clorinde", 4), ("usher", 3),
                                  ("crabaletta", 2));
        var (forecast, board) = Read(seat);

        Assert.Equal(0, board.Cues[0].Price);
        Assert.Equal(FurinaStageLaw.ActClorindeDamage, board.Cues[0].Number);
        Assert.Equal(new[] { 0, FurinaStageLaw.ActClorindeTax,
                             FurinaStageLaw.ActClorindeTax },
                     board.Bars.Select(b => b.Paid).ToArray());
        Assert.Equal(forecast.Seats.Select(r => r.After).ToArray(),
                     RealEndOfTurn(stage));
    }

    [Fact]
    public void Chevreuse_shows_energy_and_her_price_paid_by_the_back_performer()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("chevreuse", 4), ("usher", 5));
        var (forecast, board) = Read(seat);

        var cue = board.Cues[0];
        Assert.Equal(StageCueIcon.Energy, cue.Icon);
        Assert.Equal(FurinaStageLaw.ActChevreuseEnergy, cue.Number);
        Assert.Equal(FurinaStageLaw.ActChevreusePrice, cue.Price);
        Assert.False(cue.Greyed);
        // The bank pays: the gold chip is on the back performer's bar.
        Assert.Equal(new[] { 0, FurinaStageLaw.ActChevreusePrice },
                     board.Bars.Select(b => b.Paid).ToArray());
        Assert.StartsWith("Your back performer pays 2: 5 → ", cue.Forecast);
        Assert.Equal(forecast.Seats.Select(r => r.After).ToArray(),
                     RealEndOfTurn(stage));
    }

    [Fact]
    public void An_act_that_cannot_pay_shows_greyed_with_what_it_would_do()
    {
        using var _ = new Arm();
        // The back performer holds 1: Chevreuse's Spend 2 cannot be paid.
        var (seat, stage) = Stage(("chevreuse", 4), ("usher", 1));
        var (forecast, board) = Read(seat);

        var cue = board.Cues[0];
        Assert.True(cue.Greyed);
        Assert.Equal(0, cue.Times);
        Assert.Equal(FurinaStageLaw.ActChevreuseEnergy, cue.Number);
        Assert.Equal(FurinaStageLaw.ActChevreusePrice, cue.Price);
        Assert.Equal("Your back performer cannot pay 2: does nothing.",
                     cue.Forecast);
        Assert.True(forecast.Cues[0].Unpaid);
        // Nothing is paid, by the forecast or by the real end of turn.
        Assert.All(board.Bars, b => Assert.Equal(0, b.Paid));
        Assert.Equal(new[] { 4, 1 }, RealEndOfTurn(stage));

        // Neuvillette short of his 3, greyed with his 8.
        var (short2, _) = Stage(("neuvillette", 2), ("usher", 3));
        var neuv = Read(short2).Board.Cues[0];
        Assert.True(neuv.Greyed);
        Assert.Equal(FurinaStageLaw.ActNeuvilletteDamage, neuv.Number);
        Assert.Equal(FurinaStageLaw.ActNeuvillettePrice, neuv.Price);
    }

    [Fact]
    public void Clorinde_alone_cannot_pay_and_is_greyed()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("clorinde", 4));
        var cue = Read(seat).Board.Cues[0];
        Assert.True(cue.Greyed);
        Assert.Equal(FurinaStageLaw.ActClorindeDamage, cue.Number);
    }

    [Fact]
    public void Wriothesley_untouched_shows_a_greyed_zero()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("usher", 3), ("wriothesley", 10));
        var (forecast, board) = Read(seat);

        var cue = board.Cues[1];
        Assert.Equal(StageCueIcon.Attack, cue.Icon);
        Assert.Equal(0, cue.Number);
        Assert.True(cue.Greyed);
        Assert.DoesNotContain(forecast.Acts,
                              a => a.Who == StagePerformer.Wriothesley);
    }

    [Fact]
    public void Wriothesley_hit_shows_twice_what_he_lost()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("wriothesley", 10), ("usher", 3));
        stage.Absorb(4);
        stage.ClearBeats();
        var (forecast, board) = Read(seat);
        Assert.Equal(FurinaStageLaw.ActWriothesleyRate * 4, board.Cues[0].Number);
        Assert.Equal(forecast.Acts[0].Amount, board.Cues[0].Number);
        Assert.Equal("Cryo", board.Cues[0].Element);
        Assert.False(board.Cues[0].Greyed);
    }

    [Fact]
    public void A_gift_shows_the_support_glyph_and_its_amount()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("sigewinne", 5), ("usher", 2));
        var (forecast, board) = Read(seat);
        var cue = board.Cues[0];
        Assert.Equal(StageCueIcon.Support, cue.Icon);
        Assert.Equal(FurinaStageLaw.ActSigewinneGift, cue.Number);
        Assert.Equal(0, cue.Price);
        // Her gift leaves her bar: a gold chip on it.
        Assert.Equal(FurinaStageLaw.ActSigewinneGift, board.Bars[0].Paid);
        Assert.Equal(forecast.Seats.Select(r => r.After).ToArray(),
                     RealEndOfTurn(stage));

        var (both, _) = Stage(("charlotte", 3), ("usher", 2));
        var gift = Read(both).Board.Cues[0];
        Assert.Equal(StageCueIcon.Support, gift.Icon);
        Assert.Equal(FurinaStageLaw.ActCharlotteGift, gift.Number);
    }

    [Fact]
    public void Full_house_shows_times_n_beside_the_cue()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        seat.WithPower<FullHousePower>(1);
        var (_, stage) = Stage(seat, ("usher", 3), ("chevalmarin", 4),
                               ("crabaletta", 4));
        var (forecast, board) = Read(seat);

        Assert.Equal(new[] { 2, 2, 2 },
                     board.Cues.Select(c => c.Times).ToArray());
        // The number is ONE act's: the multiplier is beside it.
        Assert.Equal(FurinaStageLaw.ActUsherBlock, board.Cues[0].Number);
        Assert.Equal(2 * FurinaStageLaw.ActUsherBlock, forecast.BlockAfterActs);
        Assert.Contains("Acts 2 times.", board.Cues[0].Forecast);
    }

    [Fact]
    public void A_payment_that_empties_a_guest_counts_its_bow_as_one_more_act()
    {
        using var _ = new Arm();
        // Neuvillette at exactly 3: he pays, deals 8, leaves, and his Bow
        // (free) deals 8 more before the turn ends.
        var (seat, stage) = Stage(("neuvillette", 3), ("usher", 3));
        var (forecast, board) = Read(seat);
        var cue = board.Cues[0];
        Assert.Equal(FurinaStageLaw.ActNeuvilletteDamage, cue.Number);
        Assert.Equal(2, cue.Times);
        Assert.Equal(2, forecast.Acts.Count(a => a.Who == StagePerformer.Neuvillette));
        Assert.True(board.Bars[0].Empties);
        Assert.Contains("Then leaves and takes a Bow.", cue.Forecast);
        RealEndOfTurn(stage);
        Assert.Null(stage.SeatOf(StagePerformer.Neuvillette));
    }

    [Fact]
    public void Ousia_is_already_in_the_cue_number()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("crabaletta", 3));
        stage.ActDamageMultiplier = 2;
        var cue = Read(seat).Board.Cues[0];
        Assert.Equal(2 * FurinaStageLaw.ActCrabalettaDamage, cue.Number);
        Assert.Equal(1, cue.Times);
    }

    [Fact]
    public void A_resting_returnee_shows_a_greyed_cue_with_no_number()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 3), ("crabaletta", 2));
        Seat.Set(stage.Back!, "Resting", true);
        var cue = Read(seat).Board.Cues[1];
        Assert.True(cue.Greyed);
        Assert.Equal(-1, cue.Number);
        Assert.Equal("Came back this turn: does not act.", cue.Forecast);
    }

    [Fact]
    public void Two_ushers_are_two_cues_by_seat_key()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 3), ("usher", 2));
        var board = Read(seat).Board;
        Assert.Equal(stage.Seats.Select(s => s.Key).ToArray(),
                     board.Cues.Select(c => c.Key).ToArray());
        Assert.Equal(stage.Seats.Select(s => s.Key).ToArray(),
                     board.Bars.Select(b => b.Key).ToArray());
    }

    // ==================================================================
    // 2. The chips.
    // ==================================================================

    [Fact]
    public void The_fade_is_a_grey_chip_on_each_fading_bar_and_matches_the_real_fade()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 25), ("chevalmarin", 9),
                                  ("crabaletta", 15));
        var (forecast, board) = Read(seat);

        // The front never fades; 9 -> 7 and 15 -> 10.
        Assert.Equal(new[] { 0, 2, 5 },
                     board.Bars.Select(b => b.Faded).ToArray());
        Assert.Equal(forecast.Seats.Select(r => r.Faded).ToArray(),
                     board.Bars.Select(b => b.Faded).ToArray());
        Assert.Equal(forecast.Seats.Select(r => r.After).ToArray(),
                     RealEndOfTurn(stage));
    }

    [Fact]
    public void Incoming_hits_shade_the_front_after_her_block()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("usher", 9), ("crabaletta", 4));
        // Usher's act gives 3 Block: a 7 puts 4 on his bar.
        var (forecast, board) = Read(seat, 7);

        Assert.Equal(new[] { 4, 0 }, board.Bars.Select(b => b.Hits).ToArray());
        Assert.False(board.Bars[0].Empties);
        Assert.Equal(forecast.FrontTakes, board.Bars.Sum(b => b.Hits));
        Assert.Equal(0, board.Furina.Hits);
    }

    [Fact]
    public void A_front_that_empties_is_marked_and_the_next_performer_takes_the_later_hits()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("crabaletta", 3), ("chevalmarin", 6));
        // No Block from these acts: the first 4 empties Crabaletta (3) and
        // 1 reaches her; Chevalmarin steps up and takes the second 4.
        var (forecast, board) = Read(seat, 4, 4);

        Assert.Equal(new[] { 3, 4 }, board.Bars.Select(b => b.Hits).ToArray());
        Assert.Equal(new[] { true, false },
                     board.Bars.Select(b => b.Empties).ToArray());
        Assert.Equal(forecast.ReachesFurina, board.Furina.Hits);
        Assert.Equal(1, board.Furina.Hits);

        // The real hits, through the ledger's own Absorb, after the real end
        // of turn: the same split.
        RealEndOfTurn(stage);
        var first = stage.Absorb(4);
        Assert.Equal((3, 1), (first.Absorbed, first.ReachedFurina));
        var second = stage.Absorb(4);
        Assert.Equal((4, 0), (second.Absorbed, second.ReachedFurina));
    }

    [Fact]
    public void Hits_that_pass_the_whole_stage_shade_her_own_bar()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("crabaletta", 2));
        var (forecast, board) = Read(seat, 12);
        Assert.Equal(2, board.Bars[0].Hits);
        Assert.True(board.Bars[0].Empties);
        Assert.Equal(10, board.Furina.Hits);
        Assert.Equal(forecast.ReachesFurina, board.Furina.Hits);
        Assert.Equal(-1, board.Furina.Key);
    }

    [Fact]
    public void Payment_fade_and_hits_stack_on_one_bar_in_that_order()
    {
        using var _ = new Arm();
        // Neuvillette at the back: he pays 3 (13 -> 10), then fades (10 ->
        // 8). Usher in front takes the hit.
        var (seat, _) = Stage(("usher", 4), ("neuvillette", 13));
        var (forecast, board) = Read(seat, 5);
        var bar = board.Bars[1];
        Assert.Equal((3, 2, 0), (bar.Paid, bar.Faded, bar.Hits));
        Assert.Equal(8, forecast.Seats[1].After);
        Assert.Equal(2, board.Bars[0].Hits);
    }

    [Fact]
    public void With_no_intent_known_no_hit_is_shaded()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("usher", 3));
        var forecast = FurinaStage.Forecast(seat.Creature, null);
        var board = FurinaStageCues.From(forecast);
        Assert.All(board.Bars, b => Assert.Equal(0, b.Hits));
        Assert.Equal(0, board.Furina.Hits);
    }

    // ==================================================================
    // 3. When the cues draw, and the text box that does not.
    // ==================================================================

    [Fact]
    public void The_cues_draw_for_her_alone_and_only_on_the_arm()
    {
        using (new Arm())
        {
            Assert.True(FurinaStageCues.AppliesTo(Seat.Furina().Creature));
            Assert.False(FurinaStageCues.AppliesTo(Seat.Klee().Creature));
        }
        using (new Arm(on: false))
        {
            var seat = Seat.Furina().WithCombatState();
            Assert.False(FurinaStageCues.AppliesTo(seat.Creature));
            Assert.Null(FurinaStageCues.Read(seat.Creature));
        }
    }

    [Fact]
    public void The_cues_come_down_at_the_end_of_her_turn_and_up_at_its_start()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("usher", 3));
        Assert.True(FurinaStageCues.Showing(seat.Creature));
        Assert.NotNull(FurinaStageCues.Read(seat.Creature));

        FurinaStageCues.CurtainDown(seat.Creature);
        Assert.False(FurinaStageCues.Showing(seat.Creature));
        Assert.Null(FurinaStageCues.Read(seat.Creature));

        FurinaStageCues.CurtainUp(seat.Creature);
        Assert.True(FurinaStageCues.Showing(seat.Creature));
    }

    [Fact]
    public void The_hooks_bring_the_cues_down_before_the_acts_and_up_at_turn_start()
    {
        var end = Il.CallSequence(Il.Method("FurinaStageHooks",
                                            "BeforeSideTurnEnd"));
        var down = end.ToList().IndexOf("FurinaStageCues.CurtainDown");
        var acts = end.ToList().IndexOf("FurinaStage.EndOfTurnActs");
        Assert.True(down >= 0 && acts > down, string.Join(", ", end));
        Assert.Contains("FurinaStageCues.CurtainUp",
                        Il.Calls(Il.Method("FurinaStageHooks",
                                           "AfterPlayerTurnStart")));
    }

    [Fact]
    public void The_text_box_does_not_mount_under_the_arm()
    {
        // The gauge spec is gone: no `furina_stage` key in the table.
        var table = typeof(GaugeBridge).TypeInitializer!;
        Assert.DoesNotContain("furina_stage", Il.Strings(table));
        // And the strip has nothing left to mount with.
        Assert.Null(typeof(FurinaStageStrip).GetMethod("AppliesTo"));
        Assert.Null(typeof(FurinaStageStrip).GetMethod("Refresh"));
    }

    [Fact]
    public void The_seat_pages_text_forecast_is_unchanged()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("neuvillette", 6), ("usher", 3));
        var lines = FurinaStageStrip.Label(seat.Creature).Split('\n');
        Assert.Contains("End: Neuvillette 6 → 3  Usher 3 → 3", lines);
    }
}
