#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- THE SUPPORTING POOL (2026-09-26), the mod's pins.
///
/// The design is <c>review/active/furina-supporting-pool-2026-09-26.md</c>,
/// ruled with all four defaults and swept before the build: 28 of its 29
/// cards (Sold Out is <c>FurinaStageSoldOutTests</c>). The sim's pins are
/// <c>tier0/tests/test_furina_supporting_pool.py</c>, on the same boards.
///
/// Pinned headlessly on the LEDGER, where every seat and bar rule lives (the
/// reorders, Stage Whisper, the fade's benders, the front cash-out, the two
/// guests' Fanfare halves, the Grand Finale's stay-Bow), on the FORECAST,
/// which runs those same moves, and -- for what needs a live combat (the
/// turn-start order, the reaction broadcast, the draws) -- on the IL.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class FurinaSupportingPoolTests
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

    private static StagePerformer P(string member) => FurinaStage.Parse(member);

    /// <summary>A stage of these seats, front first, with an empty log --
    /// `FurinaGuestCastTests`' helper.</summary>
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

    private static int[] Bars(FurinaStageLedger stage) =>
        stage.Seats.Select(s => s.Fanfare).ToArray();

    private static StagePerformer[] Cast(FurinaStageLedger stage) =>
        stage.Seats.Select(s => s.Who).ToArray();

    private static Creature EnemyBody()
    {
        var body = Seat.Klee(40).Creature;
        Seat.Force(body, "Side", MegaCrit.Sts2.Core.Combat.CombatSide.Enemy);
        return body;
    }

    // ---- 1. arranging the stage ---------------------------------------------

    [Fact]
    public void Plot_twist_reverses_three_and_swaps_two()
    {
        using var _ = new Arm();
        var (_, three) = Stage(("usher", 3), ("chevalmarin", 4),
                               ("crabaletta", 5));
        Assert.True(three.Reverse());
        Assert.Equal(new[] { StagePerformer.Crabaletta,
                             StagePerformer.Chevalmarin, StagePerformer.Usher },
                     Cast(three));
        Assert.Equal(new[] { 5, 4, 3 }, Bars(three));
        Assert.Equal(FurinaStageLedger.ReorderEvent, three.Beats[^1].Event);

        var (_, two) = Stage(("usher", 3), ("crabaletta", 5));
        Assert.True(two.Reverse());
        Assert.Equal(new[] { 5, 3 }, Bars(two));

        var (_, one) = Stage(("usher", 3));
        Assert.False(one.Reverse());
    }

    [Fact]
    public void Revolving_stage_runs_after_the_regen()
    {
        // The recommendation taken: the lead's 1 goes to the performer that
        // led last turn, THEN the back moves to the front.
        var calls = Il.CallSequence(
            Il.Method("FurinaStageHooks", "AfterPlayerTurnStart")).ToList();
        var regen = calls.IndexOf("FurinaStage.RegenLead");
        var powers = calls.IndexOf("FurinaStage.TurnStartPowers");
        Assert.True(regen >= 0 && powers > regen, string.Join(", ", calls));
        var start = Il.Calls(Il.Method("FurinaStage", "TurnStartPowers"));
        Assert.Contains("FurinaStage.StepForward", start);
    }

    [Fact]
    public void The_turn_start_powers_run_show_revolve_tickets_regina()
    {
        var calls = Il.CallSequence(
            Il.Method("FurinaStage", "TurnStartPowers")).ToList();
        int At(string call)
        {
            var i = calls.IndexOf(call);
            Assert.True(i >= 0, call + " in " + string.Join(", ", calls));
            return i;
        }
        // One-Woman Show first, on the stage the turn found; then Revolving
        // Stage; then Season Tickets' Raise (which summons on empty); then
        // Regina's Hydro.
        Assert.True(At("PlayerCmd.GainEnergy") < At("FurinaStage.StepForward"));
        Assert.True(At("FurinaStage.StepForward") < At("FurinaStage.Raise"));
        Assert.True(At("FurinaStage.Raise") < At("ElementalHit.ApplyOnly"));
    }

    [Fact]
    public void Oratrices_verdict_points_a_random_pick_at_its_enemy_while_it_lives()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("crabaletta", 3));
        var a = EnemyBody();
        var b = EnemyBody();
        var pool = new List<Creature> { a, b };
        stage.VerdictTarget = b;
        Assert.Same(b, FurinaStage.ActTarget(seat.Creature, pool));
        // Not in the pool (Lynette's aura pool, say): a random one of it.
        Assert.Same(a, FurinaStage.ActTarget(seat.Creature,
                                             new List<Creature> { a }));
        // Every random pick an act makes comes through the one door.
        Assert.Contains("FurinaStage.ActTarget",
                        Il.Calls(Il.Method("FurinaStage", "RandomEnemy")));
        Assert.Contains("FurinaStage.ActTarget",
                        Il.Calls(Il.Method("FurinaStage", "GuestAct")));
        // "This turn": the sweep clears it.
        Assert.Contains("FurinaStageLedger.set_VerdictTarget",
                        Il.Calls(Il.Method("FurinaStage", "EndOfTurnActs")));
    }

    [Fact]
    public void Lyney_pays_two_of_his_own_or_does_not_act()
    {
        using var _ = new Arm();
        var owed = new List<StageExit>();
        var (_, stage) = Stage(("usher", 3), ("chevalmarin", 2), ("lyney", 5));
        Assert.True(stage.ActFanfare(StagePerformer.Lyney, stage.Seats[2],
                                     null, owed));
        Assert.Equal(new[] { 3, 2, 3 }, Bars(stage));
        // The swap is the ledger's own move, after the hit.
        Assert.True(stage.SwapEnds());
        Assert.Equal(new[] { StagePerformer.Lyney, StagePerformer.Chevalmarin,
                             StagePerformer.Usher }, Cast(stage));

        var (_, poor) = Stage(("usher", 3), ("lyney", 1));
        Assert.False(poor.ActFanfare(StagePerformer.Lyney, poor.Seats[1],
                                     null, owed));
        Assert.Equal(new[] { 3, 1 }, Bars(poor));

        var (_, alone) = Stage(("lyney", 5));
        Assert.False(alone.SwapEnds());

        var act = Il.Calls(Il.Method("FurinaStage", "GuestAct"));
        Assert.Contains("FurinaStageLedger.SwapEnds", act);
    }

    [Fact]
    public void Stage_whisper_moves_up_to_n_and_the_back_keeps_one()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 2), ("crabaletta", 7));
        Assert.Equal(3, stage.Whisper(3));
        Assert.Equal(new[] { 5, 4 }, Bars(stage));

        var (_, thin) = Stage(("usher", 2), ("crabaletta", 3));
        Assert.Equal(2, thin.Whisper(3));
        Assert.Equal(new[] { 4, 1 }, Bars(thin));

        // Never empties the back, so never Bows it.
        var (_, one) = Stage(("usher", 2), ("crabaletta", 1));
        Assert.Equal(0, one.Whisper(3));
        Assert.Equal(new[] { 2, 1 }, Bars(one));

        var (_, alone) = Stage(("usher", 6));
        Assert.Equal(0, alone.Whisper(3));

        var card = new ProtoFsStageWhisper();
        Assert.Equal(3, card.DynamicVars["Whisper"].IntValue);
    }

    // ---- 2. feeding -----------------------------------------------------------

    [Fact]
    public void Escoffier_pays_three_and_feeds_each_other_performer_two()
    {
        using var _ = new Arm();
        var owed = new List<StageExit>();
        var (_, stage) = Stage(("usher", 2), ("escoffier", 6),
                               ("crabaletta", 1));
        Assert.True(stage.ActFanfare(StagePerformer.Escoffier, stage.Seats[1],
                                     null, owed));
        Assert.Equal(new[] { 4, 3, 3 }, Bars(stage));

        // Her Bow is free and still feeds.
        var (_, bowed) = Stage(("usher", 2), ("crabaletta", 1));
        Assert.True(bowed.ActFanfare(
            StagePerformer.Escoffier, null,
            new StageExit(StagePerformer.Escoffier, StageDeparture.Spent),
            owed));
        Assert.Equal(new[] { 4, 3 }, Bars(bowed));

        var (_, poor) = Stage(("usher", 2), ("escoffier", 2));
        Assert.False(poor.ActFanfare(StagePerformer.Escoffier, poor.Seats[1],
                                     null, owed));
        Assert.Equal(new[] { 2, 2 }, Bars(poor));
    }

    [Fact]
    public void Star_billing_draws_after_every_guest_arrival()
    {
        var calls = Il.CallSequence(Il.Method("FurinaStage", "GuestStar"))
            .ToList();
        var billing = calls.LastIndexOf("FurinaStage.StarBilling");
        Assert.True(billing > calls.IndexOf("FurinaStageLedger.GuestArrives"));
        Assert.True(billing > calls.IndexOf("FurinaStage.RecastFromFront"));
        Assert.True(billing > calls.IndexOf("FurinaStageLedger.GuestReturns"));
        Assert.Contains("CardPileCmd.Draw",
                        Il.Calls(Il.Method("FurinaStage", "StarBilling")));
    }

    [Fact]
    public void The_two_new_guests_have_bodies_badges_and_tips()
    {
        foreach (var who in new[] { StagePerformer.Lyney,
                                    StagePerformer.Escoffier })
        {
            Assert.True(FurinaStage.IsGuest(who));
            Assert.Equal(who.ToString(), FurinaStageLedger.DisplayName(who));
        }
        Assert.Equal(StagePerformer.Lyney, P("lyney"));
        Assert.Equal(StagePerformer.Escoffier, P("escoffier"));
        Assert.True(StageForecastCue.Priced(StagePerformer.Lyney));
        Assert.Equal(FurinaStageLaw.ActEscoffierPrice,
                     StageForecastCue.PriceOf(StagePerformer.Escoffier));
    }

    // ---- 3. bending the fade --------------------------------------------------

    [Fact]
    public void Held_applause_skips_one_fade()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 3), ("crabaletta", 11));
        stage.FadeHeld = true;
        Assert.Equal(0, stage.Fade());
        Assert.Equal(new[] { 3, 11 }, Bars(stage));
        Assert.False(stage.FadeHeld);
        Assert.Equal(FurinaStageLaw.FadeLoss(11), stage.Fade());
    }

    [Fact]
    public void Echoing_hall_moves_the_fades_loss_to_the_front()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 3), ("chevalmarin", 9),
                               ("crabaletta", 11));
        var lost = stage.Fade(FurinaStageLaw.FadeThreshold, echo: true);
        Assert.Equal(FurinaStageLaw.FadeLoss(9) + FurinaStageLaw.FadeLoss(11),
                     lost);
        Assert.Equal(new[] { 3 + lost, 9 - FurinaStageLaw.FadeLoss(9),
                             11 - FurinaStageLaw.FadeLoss(11) }, Bars(stage));
        Assert.Equal(3 + 9 + 11, Bars(stage).Sum());
    }

    [Fact]
    public void Eternal_applause_moves_the_line_to_ten_and_copies_do_not_stack()
    {
        using var _ = new Arm();
        Assert.Equal(2, FurinaStageLaw.FadeLoss(14,
                                                FurinaStageLaw.EternalFadeThreshold));
        var seat = Seat.Furina().WithCombatState()
            .WithPower<EternalApplausePower>(1)
            .WithPower<EternalApplausePower>(1)
            .WithPower<EchoingHallPower>(1);
        var rules = FurinaStage.FadeRules(seat.Creature);
        Assert.Equal((FurinaStageLaw.EternalFadeThreshold, true), rules);
        Assert.Equal((FurinaStageLaw.FadeThreshold, false),
                     FurinaStage.FadeRules(Seat.Furina().Creature));
    }

    [Fact]
    public void The_forecast_reads_the_fades_benders_and_lyneys_swap()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 3), ("chevalmarin", 9),
                                  ("crabaletta", 11));
        stage.FadeHeld = true;
        var held = FurinaStage.Forecast(seat.Creature, null);
        Assert.Equal(new[] { 3, 9, 11 }, held.Seats.Select(s => s.After));
        Assert.True(stage.FadeHeld);            // the forecast is pure

        stage.FadeHeld = false;
        seat.WithPower<EternalApplausePower>(1);
        var eternal = FurinaStage.Forecast(seat.Creature, null);
        Assert.Equal(new[] { 3, 9, 11 }, eternal.Seats.Select(s => s.After));

        var (lyneySeat, _) = Stage(("usher", 3), ("chevalmarin", 2),
                                   ("lyney", 5));
        var swap = FurinaStage.Forecast(lyneySeat.Creature, new[] { 4 });
        // Lyney pays 2 and swaps to the front before the enemy's turn: the
        // hit lands on him (after Usher's 3 Block, 1 of it).
        Assert.Equal(1, swap.FrontTakes);
        Assert.Equal(StagePerformer.Lyney,
                     Assert.Single(swap.Takers).Who);
    }

    // ---- 4. cashing out -------------------------------------------------------

    [Fact]
    public void Intermission_is_a_final_bow_that_draws_per_every()
    {
        var calls = Il.CallSequence(Il.Method("FurinaStage", "Intermission"))
            .ToList();
        Assert.Contains("FurinaStageLedger.FinalBow", calls);
        Assert.True(calls.IndexOf("FurinaStage.Bow")
                    < calls.IndexOf("CardPileCmd.Draw"));
        var card = new ProtoFsIntermission();
        Assert.Equal(3, card.DynamicVars["Every"].IntValue);
    }

    [Fact]
    public void Counterclaim_reads_an_enemy_hit_on_the_front_since_her_last_turn()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 9), ("crabaletta", 1));
        Assert.False(FurinaStage.FrontHitSinceLastTurn(seat.Creature));
        // No enemy behind the hit: not the notion A Rapt Audience pays on.
        FurinaStage.AbsorbHit(seat.Creature, 3, dealer: null);
        Assert.False(stage.FrontHitSinceLastTurn);
        FurinaStage.AbsorbHit(seat.Creature, 3, EnemyBody());
        Assert.True(FurinaStage.FrontHitSinceLastTurn(seat.Creature));
        // The window opens as her turn ends.
        Assert.Contains("FurinaStageLedger.set_FrontHitSinceLastTurn",
                        Il.Calls(Il.Method("FurinaStage", "EndOfTurnActs")));
    }

    [Fact]
    public void Bring_the_house_down_cashes_the_front_and_it_bows()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 6), ("crabaletta", 2));
        var result = stage.SpendAllOfFront();
        Assert.True(result.Fired);
        Assert.Equal(6, result.Paid);
        Assert.Equal(6, stage.SpentThisPlay);
        Assert.Equal(StagePerformer.Usher, result.Exit!.Value.Who);
        Assert.True(result.Exit.Value.Bows);
        Assert.Equal(new[] { StagePerformer.Crabaletta }, Cast(stage));

        var (_, empty) = Stage();
        Assert.False(empty.SpendAllOfFront().Fired);
    }

    // ---- 5. bows and encores --------------------------------------------------

    [Fact]
    public void Every_bow_counts_for_da_capo()
    {
        Assert.Contains("FurinaStageLedger.set_BowsThisCombat",
                        Il.Calls(Il.Method("FurinaStage", "Bow")));
        var card = new ProtoFsDaCapo();
        Assert.Equal(5, card.DynamicVars.CalculationBase.IntValue);
        Assert.Equal(2, card.DynamicVars.ExtraDamage.IntValue);
    }

    [Fact]
    public void A_grand_finale_bow_keeps_its_seat_and_its_gifts_skip_the_giver()
    {
        using var _ = new Arm();
        var owed = new List<StageExit>();
        var (_, stage) = Stage(("usher", 2), ("charlotte", 4),
                               ("sigewinne", 5));
        var charlotte = stage.Seats[1];
        Assert.True(stage.ActFanfare(
            StagePerformer.Charlotte, null,
            new StageExit(StagePerformer.Charlotte, StageDeparture.Spent, 4, 1)
            {
                Stayer = charlotte,
            }, owed));
        Assert.Equal(new[] { 3, 4, 6 }, Bars(stage));
        var sigewinne = stage.Seats[2];
        Assert.True(stage.ActFanfare(
            StagePerformer.Sigewinne, null,
            new StageExit(StagePerformer.Sigewinne, StageDeparture.Spent, 6, 2)
            {
                Stayer = sigewinne,
            }, owed));
        // At the back, her gift wraps to the front, free.
        Assert.Equal(new[] { 6, 4, 6 }, Bars(stage));
        Assert.Empty(owed);

        var finale = Il.Calls(Il.Method("FurinaStage", "GrandFinale"));
        Assert.Contains("FurinaStage.Bow", finale);
        Assert.DoesNotContain("FurinaStageLedger.ReturnToBack", finale);
    }

    [Fact]
    public void Gala_premiere_summons_the_trio_at_three()
    {
        using var _ = new Arm();
        var (_, stage) = Stage();
        foreach (var who in new[] { StagePerformer.Usher,
                                    StagePerformer.Chevalmarin,
                                    StagePerformer.Crabaletta })
        {
            stage.Summon(who, 3);
        }
        Assert.Equal(new[] { 3, 3, 3 }, Bars(stage));
        // On a full stage each is a recast carrying its own 3.
        var summon = Il.Calls(Il.Method("FurinaStage", "Summon"));
        Assert.Contains("FurinaStage.RecastFromFront", summon);
    }

    // ---- 6. Hydro and reactions -----------------------------------------------

    [Fact]
    public void Tide_of_applause_rides_the_one_reaction_site()
    {
        Assert.Contains("FurinaStage.OnReaction",
                        Il.Calls(Il.Method("ReactionEffects", "Resolve")));
        Assert.Contains("FurinaStage.Raise",
                        Il.Calls(Il.Method("FurinaStage", "OnReaction")));
    }

    // ---- 7. Furina's side paths -----------------------------------------------

    [Fact]
    public void Soliloquy_adds_to_each_attack_hit_only_on_an_empty_stage()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState().WithPower<SoliloquyPower>(3);
        var power = seat.Creature.Powers.OfType<SoliloquyPower>().Single();
        var attack = new ProtoFsBubbleAria();
        var skill = new ProtoFsPlotTwist();
        var target = EnemyBody();
        Assert.Equal(3m, power.ModifyDamageAdditive(
            target, 4m, ValueProp.Move, seat.Creature, attack, null));
        Assert.Equal(0m, power.ModifyDamageAdditive(
            target, 4m, ValueProp.Move, seat.Creature, skill, null));
        Assert.Equal(0m, power.ModifyDamageAdditive(
            target, 4m, ValueProp.Move, EnemyBody(), attack, null));
        FurinaStageLedger.For(seat.Creature).Summon(StagePerformer.Usher);
        Assert.Equal(0m, power.ModifyDamageAdditive(
            target, 4m, ValueProp.Move, seat.Creature, attack, null));
    }

    [Fact]
    public void Dual_nature_takes_the_larger_multiple_and_pneuma_regains()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 3));
        ArkheAlignmentPower.ChooseForTurn(seat.Creature, pneuma: false);
        Assert.Equal(2, stage.ActDamageMultiplier);
        stage.ActDamageMultiplier = 3;          // Arkhe Alignment, two copies
        ArkheAlignmentPower.ChooseForTurn(seat.Creature, pneuma: false);
        Assert.Equal(3, stage.ActDamageMultiplier);
        ArkheAlignmentPower.ChooseForTurn(seat.Creature, pneuma: true);
        Assert.Equal(2, stage.ActBlockMultiplier);
        Assert.Equal(3 + ArkheAlignmentPower.PneumaLeadRegain,
                     stage.Lead!.Fanfare);
    }

    [Fact]
    public void The_twenty_eight_rows_join_the_arms_pool()
    {
        var offered = ArmPools.Offerable("furina-stage")
            .Select(c => c.GetType().Name).ToHashSet();
        foreach (var name in new[]
                 {
                     "ProtoFsPlotTwist", "ProtoFsRevolvingStage",
                     "ProtoFsOratricesVerdict", "ProtoFsGuestStarLyney",
                     "ProtoFsStageWhisper", "ProtoFsCheeredOn",
                     "ProtoFsSeasonTickets", "ProtoFsGuestStarEscoffier",
                     "ProtoFsStarBilling", "ProtoFsHeldApplause",
                     "ProtoFsEchoingHall", "ProtoFsEternalApplause",
                     "ProtoFsSpiritedAria", "ProtoFsIntermission",
                     "ProtoFsCounterclaim", "ProtoFsBringTheHouseDown",
                     "ProtoFsDaCapo", "ProtoFsGrandFinale",
                     "ProtoFsGalaPremiere", "ProtoFsBubbleAria",
                     "ProtoFsGroundswell", "ProtoFsTideOfApplause",
                     "ProtoFsGrandDeluge", "ProtoFsReginaOfAllWaters",
                     "ProtoFsSoloVerse", "ProtoFsSoliloquy",
                     "ProtoFsOneWomanShow", "ProtoFsDualNature",
                 })
        {
            Assert.Contains(name, offered);
        }
    }
}
