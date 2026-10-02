using System;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- three fixes, 2026-09-27. [USER]: "For the furina Fix
/// items - I like your default," and "I think that Wriothesley needs a buff.
/// Perhaps he also reflects the Blocked damage. so 2."
///
///   1. A Five-Century Act returns a performer once a turn, however many
///      copies; the latch clears at the start of her turn.
///   2. Echoing Hall moved HALF the fade's loss to the front, rounded down.
///      (The 2026-09-29 fade pass cut the card; its pins left with it.)
///   3. Wriothesley always attacks: 4, plus 2 per Fanfare hits took from him,
///      plus 1 per damage her Block stopped while he stood in front.
///
/// THE HEADLESS BOUNDARY. The ledger, the forecast and the two damage hooks
/// run here for real; the act's hit itself (<c>ElementalHit.Deal</c>) needs
/// a live combat, so the end-to-end test drives a real hit through
/// <c>BeforeDamageReceived</c> and <c>ModifyHpLostBeforeOsty</c> to the Bow
/// it queues and reads the number that Bow's act deals, and the act's wiring
/// is read off IL. The sim twin runs the same cases whole
/// (<c>tier0/tests/test_furina_loop_fixes_2026_09_27.py</c>).
/// </summary>
public class FurinaLoopFixes20260927Tests
{
    private sealed class Arm : IDisposable
    {

        internal Arm()
        {
            FurinaStageLedger.ResetAll();
        }

        public void Dispose()
        {
            FurinaStageLedger.ResetAll();
        }
    }

    private static ValueProp Attack => ValueProp.Move;

    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        Seat seat, params (StagePerformer Who, int Fanfare)[] seats)
    {
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        foreach (var (who, fanfare) in seats)
        {
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
        params (StagePerformer Who, int Fanfare)[] seats) =>
        Stage(Seat.Furina().WithCombatState(), seats);

    private static Creature Enemy()
    {
        var body = Seat.Klee(40).Creature;
        Seat.Force(body, "Side", CombatSide.Enemy);
        return body;
    }

    private static FurinaResourceHooks Hooks() =>
        (FurinaResourceHooks)RuntimeHelpers.GetUninitializedObject(
            typeof(FurinaResourceHooks));

    /// <summary>One real hit on Furina through the engine's two hooks, in
    /// the engine's order: <c>BeforeDamageReceived</c> sees the hit and her
    /// Block, the engine spends the Block, <c>ModifyHpLostBeforeOsty</c> is
    /// handed the rest. Returns what reaches her HP.</summary>
    private static decimal Hit(Creature furina, int hit, Creature? dealer)
    {
        var hooks = Hooks();
        hooks.BeforeDamageReceived(null!, furina, hit, Attack, dealer, null)
            .GetAwaiter().GetResult();
        var blocked = Math.Min(hit, furina.Block);
        Seat.Set(furina, "Block", furina.Block - blocked);
        return hooks.ModifyHpLostBeforeOsty(furina, hit - blocked, Attack,
                                            dealer, null);
    }

    // ==================================================================
    // 1. A Five-Century Act, once a turn.
    // ==================================================================

    [Fact]
    public void A_five_century_act_returns_once_a_turn_and_clears_at_her_turn()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Usher, 3),
                                  (StagePerformer.Crabaletta, 4));

        Assert.True(stage.ReturnOnce(StagePerformer.Chevalmarin));
        Assert.True(stage.ReturnedThisTurn);
        // The second Bow this turn finds a free seat and still does not.
        Assert.False(stage.ReturnOnce(StagePerformer.Chevalmarin));
        Assert.Equal(3, stage.Seats.Count);

        FurinaStage.BeginTurn(seat.Creature);
        Assert.False(stage.ReturnedThisTurn);
    }

    [Fact]
    public void A_full_stage_does_not_use_the_turns_return()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 3),
                               (StagePerformer.Crabaletta, 4),
                               (StagePerformer.Chevalmarin, 5));

        Assert.False(stage.ReturnOnce(StagePerformer.Usher));
        Assert.False(stage.ReturnedThisTurn);
    }

    [Fact]
    public void Two_copies_return_one_performer_in_the_forecast()
    {
        // Neuvillette at 3 and Lyney at 2 each pay their last Fanfare in the
        // sweep and Bow; with two copies in play only the first comes back.
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState()
            .WithPower<FiveCenturyActPower>(1)
            .WithPower<FiveCenturyActPower>(1);
        var (_, stage) = Stage(seat, (StagePerformer.Neuvillette, 3),
                               (StagePerformer.Lyney, 2));

        var forecast = FurinaStage.Forecast(seat.Creature, null);

        var back = Assert.Single(forecast.Arrivals);
        Assert.Equal(StagePerformer.Neuvillette, back.Who);
        Assert.False(stage.ReturnedThisTurn);         // the real stage untouched
    }

    [Fact]
    public void The_return_is_asked_once_a_turn_where_the_bow_pays_it()
    {
        var after = Il.Calls(Il.Method("FurinaStage", "AfterBow"));
        Assert.Contains("FurinaStageLedger.ReturnOnce", after);
        Assert.DoesNotContain("FurinaStageLedger.ReturnToBack", after);
        var begin = Il.Calls(Il.Method("FurinaStage", "BeginTurn"));
        Assert.Contains("FurinaStageLedger.set_ReturnedThisTurn", begin);
    }

    // ==================================================================
    // 3. Wriothesley always attacks.
    // ==================================================================

    [Fact]
    public void Wriothesley_with_nothing_hit_deals_his_floor()
    {
        using var _ = new Arm();
        var (seat, _) = Stage((StagePerformer.Wriothesley, 8),
                              (StagePerformer.Usher, 3));

        var forecast = FurinaStage.Forecast(seat.Creature, null);

        var act = Assert.Single(forecast.Acts,
                                a => a.Who == StagePerformer.Wriothesley);
        Assert.Equal(FurinaStageLaw.ActWriothesleyBase, act.Amount);
        Assert.Equal(4, FurinaStageLaw.WriothesleyAct(0, 0));
    }

    [Fact]
    public void Her_block_counts_for_him_only_while_he_is_in_front()
    {
        using var _ = new Arm();
        var enemy = Enemy();

        // In front: a 10 into her 6 Block. The Block stopped 6, the 4 left
        // comes off his bar.
        var (front, inFront) = Stage((StagePerformer.Wriothesley, 8),
                                     (StagePerformer.Usher, 3));
        Seat.Set(front.Creature, "Block", 6);
        Assert.Equal(0m, Hit(front.Creature, 10, enemy));
        var him = inFront.Seats[0];
        Assert.Equal(6, him.BlockedSinceAct);
        Assert.Equal(4, him.LostSinceAct);

        // Behind the front: the same hit is not his.
        var (behind, back) = Stage((StagePerformer.Usher, 8),
                                   (StagePerformer.Wriothesley, 8));
        Seat.Set(behind.Creature, "Block", 6);
        Hit(behind.Creature, 10, enemy);
        Assert.Equal(0, back.Seats[1].BlockedSinceAct);
        Assert.Equal(0, back.Seats[1].LostSinceAct);
    }

    [Fact]
    public void Only_an_enemys_hit_counts_and_a_fully_blocked_one_does()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Wriothesley, 8));

        // No dealer (a Burn in her hand): her Block stops it, it is not his.
        Seat.Set(seat.Creature, "Block", 5);
        Hit(seat.Creature, 3, null);
        Assert.Equal(0, stage.Seats[0].BlockedSinceAct);

        // An enemy's hit her Block takes whole still counts.
        Seat.Set(seat.Creature, "Block", 5);
        Assert.Equal(0m, Hit(seat.Creature, 3, Enemy()));
        Assert.Equal(3, stage.Seats[0].BlockedSinceAct);
        Assert.Equal(8, stage.Seats[0].Fanfare);
    }

    [Fact]
    public void His_act_resets_both_readings()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Wriothesley, 8),
                                  (StagePerformer.Usher, 3));
        stage.CreditBlocked(5);
        stage.Absorb(2);
        var clone = FurinaStage.Forecast(seat.Creature, null);
        Assert.Equal(4 + 2 * 2 + 5, clone.Acts[0].Amount);
        // The forecast ran on a clone: the real seat still holds both.
        Assert.Equal(5, stage.Seats[0].BlockedSinceAct);

        var act = Il.Calls(Il.Method("FurinaStage", "GuestAct"));
        Assert.Contains("StageSeat.set_BlockedSinceAct", act);
        Assert.Contains("StageSeat.set_LostSinceAct", act);
        Assert.Contains("FurinaStageLaw.WriothesleyAct", act);
        Assert.Contains("StageExit.get_Blocked", act);
    }

    /// <summary>
    /// END TO END, as far as the headless harness reaches: a real enemy hit
    /// through both damage hooks empties him in front; the Bow it queues
    /// carries both readings, and his Bow's act reads them into its number.
    /// The Bow itself is paid at <c>AfterDamageReceived</c> and deals its
    /// damage through <c>CreatureCmd</c>, which needs a live combat.
    /// </summary>
    [Fact]
    public void A_real_hit_that_empties_him_queues_a_bow_reading_both_counts()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Wriothesley, 3),
                                  (StagePerformer.Usher, 3));
        // An earlier hit, fully blocked, while he stood in front.
        Seat.Set(seat.Creature, "Block", 4);
        Hit(seat.Creature, 4, Enemy());
        // Then a 9 into 2 Block: 2 blocked, his 3 taken, 4 reach her.
        Seat.Set(seat.Creature, "Block", 2);
        Assert.Equal(4m, Hit(seat.Creature, 9, Enemy()));

        var exit = Assert.Single(stage.TakePendingHitBows());
        Assert.Equal(StagePerformer.Wriothesley, exit.Who);
        Assert.Equal(3, exit.Lost);
        Assert.Equal(4 + 2, exit.Blocked);
        Assert.Equal(4 + 2 * 3 + 1 * (4 + 2),
                     FurinaStageLaw.WriothesleyAct(exit.Lost, exit.Blocked));
        // The Block of the hit that emptied him was his, not the next front's.
        Assert.Equal(StagePerformer.Usher, stage.Lead!.Who);
        Assert.Equal(0, stage.Lead.BlockedSinceAct);
    }

    [Fact]
    public void His_tip_says_he_always_attacks()
    {
        const string tip =
            "End of your turn: deal 4 [gold]Cryo[/gold] damage to a random "
          + "enemy, plus 2 per [gold]Fanfare[/gold] he lost to hits and 1 "
          + "per damage [gold]Block[/gold] saved him.";
        var badge = new WriothesleyBadgePower().Localization!
            .Single(row => row.Item1 == "description").Item2;
        Assert.Equal(tip, badge);
    }
}
