#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Furina;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- THE SUPPORTING-POOL SEAT ROUND (2026-09-26,
/// 0.2.3859+proto), the mod's pins. The sim's are
/// <c>tier0/tests/test_furina_seat_defects_2026_09_26.py</c>, which also pins
/// the page halves.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class FurinaSeatDefects20260926Tests
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
        Seat seat, params (string Member, int Fanfare)[] seats)
    {
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        foreach (var (member, fanfare) in seats)
        {
            stage.Summon(FurinaStage.Parse(member));
            stage.Raise(fanfare - FurinaStageLaw.SummonFanfare);
        }
        stage.ClearBeats();
        return (seat, stage);
    }

    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        params (string Member, int Fanfare)[] seats) =>
        Stage(Seat.Furina().WithCombatState(), seats);

    // ---- 1. Intermission reads F before the Bow ---------------------------

    /// <summary>Lane 3: "its draw is always 0". It reads the back's bar
    /// before the cash-out empties it, as Final Bow's Block does; a back at 1
    /// Fanfare draws floor(1 / 3) = 0, which is the card as written.</summary>
    [Fact]
    public void Intermission_counts_the_bar_the_back_held_before_its_bow()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 3), ("crabaletta", 7));
        stage.FinalBow(out var bar);
        Assert.Equal(7, bar);
        Assert.Single(stage.Seats);
        var calls = Il.CallSequence(Il.Method("FurinaStage", "Intermission"))
            .ToList();
        Assert.True(calls.IndexOf("FurinaStageLedger.FinalBow")
                    < calls.IndexOf("FurinaStage.Bow"));
    }

    // ---- 2. A Five-Century Act's returnee from the enemies' turn --------

    /// <summary>Lane 3: returnees "sometimes did not act". One that Bowed to
    /// a hit on the enemies' turn came back in THEIR turn; its rest ends when
    /// hers begins, so it acts at the end of hers and the forecast counts its
    /// Block.</summary>
    [Fact]
    public void A_returnee_from_the_enemies_turn_acts_at_the_end_of_hers()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage();
        Assert.True(stage.ReturnToBack(StagePerformer.Usher));
        Assert.True(stage.Seats[0].Resting);
        Assert.Equal(0, FurinaStage.Forecast(seat.Creature, new int[0])
                            .BlockAfterActs);

        FurinaStage.BeginTurn(seat.Creature);

        Assert.False(stage.Seats[0].Resting);
        Assert.Equal(FurinaStageLaw.ActUsherBlock,
                     FurinaStage.Forecast(seat.Creature, new int[0])
                         .BlockAfterActs);
    }

    [Fact]
    public void A_return_during_her_own_turn_still_rests_through_its_acts()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 3));
        FurinaStage.BeginTurn(seat.Creature);
        Assert.True(stage.ReturnToBack(StagePerformer.Crabaletta));
        Assert.True(stage.Seats[1].Resting);
        Assert.Equal(FurinaStageLaw.ActUsherBlock,
                     FurinaStage.Forecast(seat.Creature, new int[0])
                         .BlockAfterActs);
    }

    [Fact]
    public void Her_turn_start_ends_the_rest_before_the_regen_and_the_powers()
    {
        var start = Il.CallSequence(Il.Method("FurinaStageHooks",
                                              "AfterPlayerTurnStart")).ToList();
        var begin = start.IndexOf("FurinaStage.BeginTurn");
        Assert.True(begin >= 0, string.Join(", ", start));
        Assert.True(begin < start.IndexOf("FurinaStage.RegenLead"));
        Assert.True(begin < start.IndexOf("FurinaStage.TurnStartPowers"));
    }

    [Fact]
    public void The_wire_says_which_performer_sits_out_this_turns_acts()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 3));
        stage.ReturnToBack(StagePerformer.Crabaletta);
        var rows = (List<object?>)FurinaStageLedger.Snapshot(
            seat.Player)["seats"]!;
        Assert.Equal(false, ((Dictionary<string, object?>)rows[0]!)["resting"]);
        Assert.Equal(true, ((Dictionary<string, object?>)rows[1]!)["resting"]);
    }

    // ---- 3. Revolving Stage's rotate is filed at the front ---------------

    /// <summary>Lane 3: "Usher moved from the front seat to the back" while
    /// he stood in front. The two moves file one `rotate` beat; the page reads
    /// the direction off the seat it names -- 0 for back-to-front, the back
    /// seat for Scene Change.</summary>
    [Fact]
    public void Step_forward_and_scene_change_file_their_rotate_at_opposite_ends()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("chevalmarin", 2), ("usher", 4));
        stage.StepForward();
        var forward = stage.Beats.Last();
        Assert.Equal("rotate", forward.Event);
        Assert.Equal(StagePerformer.Usher, forward.Who);
        Assert.Equal(0, forward.Seat);
        Assert.Equal(2, forward.Standing);

        stage.SceneChange();
        var back = stage.Beats.Last();
        Assert.Equal(StagePerformer.Usher, back.Who);
        Assert.Equal(1, back.Seat);
    }

    // ---- 9c. The power behind a move no card made -------------------------

    [Fact]
    public void A_move_inside_a_power_s_scope_names_the_power_and_only_there()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 3));
        using (stage.CausedBy(FurinaStage.SeasonTicketsTitle))
        {
            stage.Raise(2);
        }
        stage.Raise(1);
        Assert.Equal(FurinaStage.SeasonTicketsTitle, stage.Beats[0].Source);
        Assert.Equal("", stage.Beats[1].Source);
        var log = (List<object?>)FurinaStageLedger.Snapshot(
            seat.Player)["log"]!;
        Assert.Equal("Season Tickets",
                     ((Dictionary<string, object?>)log[0]!)["source"]);
    }

    [Fact]
    public void The_turn_start_powers_and_the_applause_open_their_scopes()
    {
        Assert.Contains("FurinaStageLedger.CausedBy",
                        Il.Calls(Il.Method("FurinaStage", "TurnStartPowers")));
        Assert.Contains("FurinaStageLedger.CausedBy",
                        Il.Calls(Il.Method("StageRaisePerTurnPower",
                                           "AfterPlayerTurnStart")));
        Assert.Contains("FurinaStageLedger.CausedBy",
                        Il.Calls(Il.Method("FurinaStage", "AfterBow")));
    }

    [Theory]
    [InlineData(typeof(ProtoFsSeasonTickets), FurinaStage.SeasonTicketsTitle)]
    [InlineData(typeof(ProtoFsRevolvingStage), FurinaStage.RevolvingStageTitle)]
    [InlineData(typeof(ProtoFsThunderousApplause),
                FurinaStage.ThunderousApplauseTitle)]
    [InlineData(typeof(AllTheWorldsAStage),
                FurinaStage.AllTheWorldsAStageTitle)]
    public void Each_source_is_the_title_its_card_prints(Type card, string title)
    {
        var model = Activator.CreateInstance(card)!;
        var rows = (List<(string, string)>)card.GetProperty("Localization")!
            .GetValue(model)!;
        Assert.Contains(("title", title), rows);
    }

    // ---- 6. Star Billing names the keyword and carries its tip -----------

    [Fact]
    public void Star_billing_carries_the_guest_star_tip()
    {
        Assert.Contains("ArmKeywordTips.ForGuestStar",
                        Il.Calls(Il.Method("ProtoFsStarBilling",
                                           "get_ExtraHoverTips")));
    }

    // ---- 5. Bring the House Down carries no back-performer Spend tip ------

    [Fact]
    public void Bring_the_house_down_carries_no_spend_tip()
    {
        var tips = Il.Calls(Il.Method("ProtoFsBringTheHouseDown",
                                      "get_ExtraHoverTips"));
        Assert.DoesNotContain("ArmKeywordTips.ForSpend", tips);
        Assert.Contains("ArmKeywordTips.ForFrontPerformer", tips);
    }

    // ---- 14. Buffer in the forecast -----------------------------------------

    /// <summary>Lane 2: "The Buffer ate the 30. The preview still said 'you
    /// take 21'." A stack stops one hit's HP loss.</summary>
    [Fact]
    public void The_forecast_lets_buffer_stop_one_hits_hp_loss()
    {
        using var _ = new Arm();
        var (seat, _) = Stage();
        Assert.Equal(20, FurinaStage.Forecast(seat.Creature, new[] { 10, 10 },
                                              null, bufferStacks: 0)
                             .ReachesFurina);
        Assert.Equal(10, FurinaStage.Forecast(seat.Creature, new[] { 10, 10 },
                                              null, bufferStacks: 1)
                             .ReachesFurina);
    }

    [Fact]
    public void The_forecast_reads_her_buffer_off_her_powers()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState().WithPower<BufferPower>(1);
        Stage(seat);
        Assert.Equal(10, FurinaStage.Forecast(seat.Creature, new[] { 10, 10 })
                             .ReachesFurina);
    }

    /// <summary>A hit the front performer takes whole costs no Buffer.
    /// </summary>
    [Fact]
    public void A_hit_the_front_takes_whole_spends_no_buffer()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("crabaletta", 9));
        var forecast = FurinaStage.Forecast(seat.Creature, new[] { 5, 10 },
                                            null, bufferStacks: 1);
        // 5 into Crabaletta (9 -> 4); the 10 empties her (4) and 6 reaches
        // Furina, which the one Buffer stops.
        Assert.Equal(0, forecast.ReachesFurina);
    }

    // ---- 22. The cards in her hand that hurt her as her turn ends --------

    /// <summary>The full-run seat died on "you take 13" at 15 HP. The cards
    /// in her hand that hurt her at the turn's end resolve after the acts and
    /// before the enemies, through her Block and the front performer.</summary>
    [Fact]
    public void The_forecast_counts_burns_and_withers_in_her_hand()
    {
        using var _ = new Arm();
        var (seat, _) = Stage();
        var hand = new[] { new HandHit(2, true), new HandHit(3, true) };
        var forecast = FurinaStage.Forecast(seat.Creature, new[] { 10 }, null,
                                            bufferStacks: 0, handHits: hand);
        Assert.Equal(15, forecast.ReachesFurina);
        Assert.Equal(5, forecast.HandDamage);
    }

    [Fact]
    public void A_burn_meets_the_acts_block_and_the_front_performer_first()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("usher", 6));
        // Usher's act: 3 Block, then the fade takes a quarter of his 6 (the
        // fade pass, 2026-09-29: the front fades too), so he stands at 5.
        // The Burn's 2 is Blocked, the Wither's 3 takes the last 1 and puts 2
        // on Usher (5 -> 3); the 10 then empties him (3) and his Bow's 3
        // Block meets the rest: 4 reaches her.
        var forecast = FurinaStage.Forecast(
            seat.Creature, new[] { 10 }, null, bufferStacks: 0,
            handHits: new[] { new HandHit(2, true), new HandHit(3, true) });
        Assert.Equal(4, forecast.ReachesFurina);
        Assert.Equal(0, forecast.HandDamage);
    }

    [Fact]
    public void Hp_loss_in_hand_goes_past_block_and_stage()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("usher", 5));
        var forecast = FurinaStage.Forecast(
            seat.Creature, new int[0], null, bufferStacks: 0,
            handHits: new[] { new HandHit(6, false) });
        Assert.Equal(6, forecast.ReachesFurina);
        Assert.Equal(6, forecast.HandDamage);
    }

    [Theory]
    [InlineData(typeof(MegaCrit.Sts2.Core.Models.Cards.Burn), 2, true)]
    [InlineData(typeof(MegaCrit.Sts2.Core.Models.Cards.Wither), 3, true)]
    [InlineData(typeof(MegaCrit.Sts2.Core.Models.Cards.Beckon), 6, false)]
    public void Each_hurting_card_reads_its_own_number(Type card, int amount,
                                                       bool blockable)
    {
        var model = (MegaCrit.Sts2.Core.Models.CardModel)
            Activator.CreateInstance(card, true)!;
        Assert.Equal(new HandHit(amount, blockable),
                     FurinaStage.HandHitOf(model, 5));
    }

    [Fact]
    public void The_live_forecast_reads_her_hand()
    {
        var forecast = typeof(FurinaStage)
            .GetMethods(System.Reflection.BindingFlags.Public
                        | System.Reflection.BindingFlags.Static)
            .Single(m => m.Name == "Forecast"
                         && m.GetParameters().Length == 5);
        Assert.Contains("FurinaStage.HandTurnEndHits", Il.Calls(forecast));
    }

    [Fact]
    public void The_wire_carries_the_hand_damage()
    {
        Assert.Contains("hand_damage",
                        Il.Strings(Il.Method("FurinaStageLedger",
                                             "ForecastSnapshot")));
    }

    // ---- 23. A Five-Century Act re-projects the forecast ---------------

    [Fact]
    public void A_five_century_act_changes_the_forecast_where_a_bow_returns()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("crabaletta", 2));
        var without = FurinaStage.Forecast(seat.Creature, new[] { 5, 5 }, null,
                                           bufferStacks: 0,
                                           handHits: new HandHit[0]);
        seat.WithPower<FiveCenturyActPower>(1);
        var with = FurinaStage.Forecast(seat.Creature, new[] { 5, 5 }, null,
                                        bufferStacks: 0,
                                        handHits: new HandHit[0]);
        // She returns at 1 after the first hit's Bow and takes 1 of the next.
        Assert.Equal(without.ReachesFurina - 1, with.ReachesFurina);
    }

    // ---- 29 and 30. The designer's two card changes ----------------------

    [Fact]
    public void Lyney_in_front_stays_there_in_the_forecast()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 3));
        stage.GuestArrives(StagePerformer.Lyney, 5, atFront: true);
        var forecast = FurinaStage.Forecast(seat.Creature, new[] { 4 }, null,
                                            bufferStacks: 0,
                                            handHits: new HandHit[0]);
        // He paid 2 (5 -> 3) and stays in front: the hit lands on him.
        Assert.Equal(StagePerformer.Lyney, Assert.Single(forecast.Takers).Who);
    }

    [Fact]
    public void Stage_whisper_draws_a_card()
    {
        var calls = Il.Calls(Il.Method("ProtoFsStageWhisper", "OnPlay"));
        Assert.Contains("FurinaStage.Whisper", calls);
        Assert.Contains("CardPileCmd.Draw", calls);
    }
}
