using System;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE FURINA STAGE'S RULES, pinned one by one against the brief that ruled
/// them (<c>review/active/furina-stage-brief-2026-09-08.md</c> sec.3).
///
/// WHY THESE ARE REAL AND NOT STRUCTURAL. The whole arm was built so that the
/// arithmetic lives in <c>FurinaStageLedger</c>, which needs no combat, no
/// scene tree and no <c>PlayerChoiceContext</c> -- so every rule below is
/// EXERCISED rather than read off IL. That was the point of the split (see the
/// ledger's header): a kit whose damage order runs through a creature the
/// player does not own is a kit whose rules have to be askable outside a game.
///
/// THE FOUR ACCEPTANCE QUESTIONS the row names are the four in section 2, and
/// they are the numbers a later live deploy has to reproduce on screen:
/// a 12 through Block 6 kills a 3-bar lead and lands 3 on her; a 3x2 flurry
/// kills a 6-bar lead and leaves her whole; a Spend 3 from a 1-bar lead pays
/// in full and bows; and three bars stand on the stage at once.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype arm's arithmetic,
/// not a number about a game.
/// </summary>
public class FurinaStageRuleTests
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

    /// <summary>A Furina seat with a stage carrying the given performers at
    /// the given bars, front first. The ledger is the whole board -- no pet is
    /// fielded, because a pet needs a live combat and the RULES do not.
    /// </summary>
    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        params (StagePerformer Who, int Fanfare)[] seats)
    {
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        foreach (var (who, fanfare) in seats)
        {
            // Through the ledger's own verbs, never by writing the bar: a
            // fixture that could set a number the rules cannot reach would be
            // testing a state no game can produce. A summon lands at 1 and a
            // Raise lands at the BACK, which is the seat just added.
            stage.Summon(who);
            stage.Raise(fanfare - FurinaStageLaw.SummonFanfare);
        }
        return (seat, stage);
    }

    // ==================================================================
    // 0. THE ARM SHIPS OFF.
    // ==================================================================

#if !FURINA_STAGE
    /// <summary>
    /// The acceptance condition the whole quarantine rests on. SKIPPED by an
    /// `#if` rather than left to fail under `-p:FurinaStage=true`, which is
    /// `docs/current/operations/prototype.md`'s standing rule: under the
    /// property this pin cannot say anything true -- green would mean the
    /// property did nothing -- and a red that means "the switch works" teaches
    /// everyone to ignore reds.
    /// </summary>
    [Fact]
    public void The_arm_ships_off()
    {
        Assert.False(FurinaStage.DefaultEnabled);
    }
#endif

    [Fact]
    public void The_arm_is_hers_alone()
    {
        using var _ = new Arm();
        // Everything compiled under the one prototype switch is fanned to
        // every seat at the table, so an arm that could not name whose
        // creature it is about is the shape of `EB-194` and `EB-221`.
        Assert.True(FurinaStage.LiveFor(Seat.Furina().Creature));
        Assert.False(FurinaStage.LiveFor(Seat.Klee().Creature));
        Assert.False(FurinaStage.LiveFor(Seat.Kokomi().Creature));
        Assert.False(FurinaStage.LiveFor(null));
    }

    [Fact]
    public void Flag_off_there_is_no_stage_at_all()
    {
        using var _ = new Arm(on: false);
        Assert.False(FurinaStage.LiveFor(Seat.Furina().Creature));
    }

    // ==================================================================
    // 1. RULE 6 -- THE DAMAGE ORDER, and the four acceptance numbers.
    // ==================================================================

    /// <summary>
    /// ACCEPTANCE 1. "A 12 through Block 6 kills a 3-bar lead and lands 3 on
    /// Furina."
    ///
    /// THE BLOCK HALF IS THE ENGINE'S AND IS NOT ASSERTED HERE, deliberately:
    /// <c>ModifyHpLostBeforeOsty</c> is handed what is LEFT after Block, which
    /// is the shipped Encore buffer's own contract one branch below the stage's
    /// (see <c>FurinaResources.AbsorbDamage</c>'s header, "damage remaining
    /// after Block"). So a 12 against Block 6 arrives here as a 6, the 3-bar
    /// lead eats 3 of it and dies, and 3 reaches her.
    /// </summary>
    [Fact]
    public void A_big_hit_rips_through_the_lead_and_lands_on_her()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Usher, 3));

        var result = stage.Absorb(12 - 6);

        Assert.Equal(3, result.Absorbed);
        Assert.Equal(3, result.ReachedFurina);
        Assert.True(stage.IsEmpty);
        Assert.Equal(StagePerformer.Usher, result.Exit!.Value.Who);
        Assert.Equal(StageDeparture.Struck, result.Exit!.Value.Cause);
        // Rule 7, first clause: death by a hit earns no bow.
        Assert.False(result.Exit!.Value.Bows);
        Assert.Equal(seat.Creature.MaxHp, seat.Creature.CurrentHp);
    }

    /// <summary>
    /// ACCEPTANCE 2. "A 3x2 flurry kills the lead and leaves Furina whole."
    ///
    /// THE RULE IS THAT NOTHING LOOPS. Each hit of the flurry is its own call,
    /// each is capped at the lead's bar, and the remainder of one hit never
    /// reaches the next performer -- so six points arriving as three twos are
    /// answered completely by a 6-bar lead, while the same six arriving as one
    /// hit against a 3-bar lead (the test above) puts three on her. That
    /// difference is the kit's whole read-the-intent decision.
    /// </summary>
    [Fact]
    public void A_flurry_is_resolved_hit_by_hit_and_she_is_untouched()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Crabaletta, 6));

        var reached = 0;
        StageExit? last = null;
        for (var hit = 0; hit < 3; hit++)
        {
            var result = stage.Absorb(2);
            reached += result.ReachedFurina;
            last ??= result.Exit;
            if (result.Exit != null) last = result.Exit;
        }

        Assert.Equal(0, reached);
        Assert.True(stage.IsEmpty);
        Assert.Equal(StageDeparture.Struck, last!.Value.Cause);
        Assert.Equal(seat.Creature.MaxHp, seat.Creature.CurrentHp);
    }

    [Fact]
    public void Absorption_never_runs_on_to_the_middle_seat()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(
            (StagePerformer.Usher, 2),
            (StagePerformer.Chevalmarin, 9),
            (StagePerformer.Crabaletta, 9));

        // Ten points at a 2-bar lead: the lead eats 2, EIGHT reach her, and
        // the eighteen sitting behind it are untouched. A rule that ran on
        // would have answered the whole hit and made the middle seat a second
        // life bar (sec.8's second failure mode).
        var result = stage.Absorb(10);

        Assert.Equal(2, result.Absorbed);
        Assert.Equal(8, result.ReachedFurina);
        Assert.Equal(2, stage.Seats.Count);
        Assert.Equal(9, stage.Lead!.Fanfare);
        Assert.Equal(9, stage.Back!.Fanfare);
    }

    [Fact]
    public void With_no_performer_every_point_reaches_her()
    {
        using var _ = new Arm();
        var (_, stage) = Stage();

        var result = stage.Absorb(7);

        Assert.Equal(0, result.Absorbed);
        Assert.Equal(7, result.ReachedFurina);
        Assert.Null(result.Exit);
    }

    /// <summary>
    /// THE SEAM, read off the shipped hook: the stage's absorption runs BEFORE
    /// the shipped Encore buffer and returns, because under this arm Encore is
    /// retired (brief sec.2) and a board that fell through would charge one hit
    /// to two buffers.
    ///
    /// STRUCTURAL, and it is the ONE fact in this file that has to be: the hook
    /// is an instance override the engine calls, and what is being asserted is
    /// the ORDER of two calls inside it rather than a number either produces.
    /// </summary>
    [Fact]
    public void The_stage_is_asked_before_the_shipped_buffer()
    {
        var calls = Il.CallSequence(
            Il.Method("FurinaResourceHooks", "ModifyHpLostBeforeOsty"));

        var stage = calls.ToList().FindIndex(
            c => c.EndsWith("FurinaStageLedger.Absorb", StringComparison.Ordinal));
        var encore = calls.ToList().FindIndex(
            c => c.EndsWith("FurinaResources.AbsorbDamage",
                            StringComparison.Ordinal));

        Assert.True(stage >= 0, "the stage's absorption left the damage hook");
        Assert.True(encore >= 0, "the shipped Encore buffer left the damage hook");
        Assert.True(stage < encore);
        // And it is gated: a Klee seat, a Kokomi seat or a flag-off Furina
        // must never reach the stage branch at all.
        Assert.Contains(calls, c => c.EndsWith("FurinaStage.LiveFor",
                                               StringComparison.Ordinal));
    }

    // ==================================================================
    // 2. RULE 8 and RULE 9 -- Spend, and the bow it buys.
    // ==================================================================

    /// <summary>
    /// ACCEPTANCE 3. "Spend 3 from a 1-bar lead pays in full and bows."
    ///
    /// IN FULL means the RIDER, not the payment: sec.10 default 4, "as [USER]
    /// said". The lead pays the 1 it has, the card's bigger number still
    /// happens, and the lead leaves with a bow.
    /// </summary>
    [Fact]
    public void A_short_lead_still_fires_the_rider_in_full_and_bows()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 1));

        var result = stage.Spend(3);

        Assert.True(result.Fired);
        Assert.Equal(1, result.Paid);
        Assert.True(stage.IsEmpty);
        Assert.Equal(StageDeparture.Spent, result.Exit!.Value.Cause);
        Assert.True(result.Exit!.Value.Bows);
    }

    [Fact]
    public void A_lead_that_can_afford_it_pays_and_stays()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Crabaletta, 8));

        var result = stage.Spend(3);

        Assert.True(result.Fired);
        Assert.Equal(3, result.Paid);
        Assert.Equal(5, stage.Lead!.Fanfare);
        Assert.Null(result.Exit);
    }

    [Fact]
    public void A_lead_emptied_exactly_by_a_spend_still_bows()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 3));

        var result = stage.Spend(3);

        Assert.Equal(3, result.Paid);
        Assert.True(result.Exit!.Value.Bows);
    }

    [Fact]
    public void On_an_empty_stage_the_rider_cannot_fire()
    {
        using var _ = new Arm();
        var (_, stage) = Stage();

        var result = stage.Spend(3);

        // NOT a refusal and NOT a whiff: the card is fine and plays at its
        // base number (rule 8's third clause). `Fired` false is how a card
        // asks that question, and `Paid` is not the question.
        Assert.False(result.Fired);
        Assert.Equal(0, result.Paid);
        Assert.Null(result.Exit);
    }

    [Fact]
    public void Spend_pays_from_the_lead_and_never_from_the_reserve()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(
            (StagePerformer.Usher, 1),
            (StagePerformer.Chevalmarin, 9));

        stage.Spend(5);

        // The lead paid its 1 and left. The reserve is untouched and is now
        // the lead -- which is the turn-after-a-rotation weakness sec.6 names.
        Assert.Single(stage.Seats);
        Assert.Equal(StagePerformer.Chevalmarin, stage.Lead!.Who);
        Assert.Equal(9, stage.Lead!.Fanfare);
    }

    // ==================================================================
    // 3. RULE 3 -- the seats, the summon and the rotation.
    // ==================================================================

    /// <summary>ACCEPTANCE 4, the ledger half: three performers stand on the
    /// stage at once, in seat order, each with its own bar. (The three BARS on
    /// screen are the pets' own, which needs a live combat -- the scenario is
    /// what proves that half.)</summary>
    [Fact]
    public void Three_performers_stand_in_a_line_front_to_back()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(
            (StagePerformer.Usher, 3),
            (StagePerformer.Chevalmarin, 5),
            (StagePerformer.Crabaletta, 1));

        Assert.Equal(3, stage.Seats.Count);
        Assert.True(stage.IsFull);
        Assert.Equal(StagePerformer.Usher, stage.Lead!.Who);
        Assert.Equal(StagePerformer.Crabaletta, stage.Back!.Who);
        Assert.Equal(
            new[]
            {
                StagePerformer.Usher, StagePerformer.Chevalmarin,
                StagePerformer.Crabaletta,
            },
            stage.Company.ToArray());
    }

    [Fact]
    public void A_summon_fills_the_back_most_empty_seat_at_one()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 4));

        var result = stage.Summon(StagePerformer.Crabaletta);

        Assert.Equal(FurinaStageLaw.SummonFanfare, result.AtFanfare);
        Assert.Null(result.Exit);
        Assert.Equal(StagePerformer.Usher, stage.Lead!.Who);
        Assert.Equal(StagePerformer.Crabaletta, stage.Back!.Who);
        Assert.Equal(1, stage.Back!.Fanfare);
    }

    /// <summary>
    /// RULE 3's rotation, and its clause "pools are never lost to rotation" --
    /// the one that makes a full stage a play rather than a punishment.
    /// </summary>
    [Fact]
    public void A_full_stage_rotates_and_the_newcomer_inherits_the_bar()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(
            (StagePerformer.Usher, 8),
            (StagePerformer.Chevalmarin, 2),
            (StagePerformer.Crabaletta, 1));

        var result = stage.Summon(StagePerformer.Usher);

        Assert.Equal(8, result.AtFanfare);
        Assert.Equal(StagePerformer.Usher, result.Exit!.Value.Who);
        Assert.Equal(StageDeparture.Rotated, result.Exit!.Value.Cause);
        // Sec.10 default 5: a bow is earned by Spend alone.
        Assert.False(result.Exit!.Value.Bows);
        Assert.Equal(3, stage.Seats.Count);
        Assert.Equal(StagePerformer.Chevalmarin, stage.Lead!.Who);
        Assert.Equal(8, stage.Back!.Fanfare);
    }

    // ==================================================================
    // 4. RULE 5 -- Raise lands at the back.
    // ==================================================================

    [Fact]
    public void A_raise_lands_on_the_back_performer_and_not_the_lead()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(
            (StagePerformer.Usher, 3),
            (StagePerformer.Crabaletta, 1));

        Assert.Equal(FurinaStageLaw.RefillAmount,
                     stage.Raise(FurinaStageLaw.RefillAmount));

        Assert.Equal(3, stage.Lead!.Fanfare);
        Assert.Equal(1 + FurinaStageLaw.RefillAmount, stage.Back!.Fanfare);
    }

    [Fact]
    public void With_one_performer_the_back_is_the_lead()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 3));

        stage.Raise(FurinaStageLaw.RefillAmount);

        Assert.Equal(3 + FurinaStageLaw.RefillAmount, stage.Lead!.Fanfare);
    }

    [Fact]
    public void A_raise_onto_an_empty_stage_raises_nothing()
    {
        using var _ = new Arm();
        var (_, stage) = Stage();

        Assert.Equal(0, stage.Raise(FurinaStageLaw.RefillAmount));
    }

    [Fact]
    public void Bars_have_no_cap()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Chevalmarin, 40));

        stage.Raise(40);

        Assert.Equal(80, stage.Lead!.Fanfare);
    }

    // ==================================================================
    // 5. RULE 4 -- the lead's regen, from her SECOND turn.
    // ==================================================================

    [Fact]
    public void The_lead_does_not_regenerate_on_turn_one()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, FurinaStageLaw.OpeningFanfare));

        Assert.Equal(0, stage.Regen(1));
        // The relic's opening bar is what the fight is posted against; a regen
        // on turn one would make it a 4 the relic never printed.
        Assert.Equal(FurinaStageLaw.OpeningFanfare, stage.Lead!.Fanfare);
    }

    [Fact]
    public void The_lead_alone_regenerates_from_turn_two()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(
            (StagePerformer.Usher, 3),
            (StagePerformer.Crabaletta, 1));

        Assert.Equal(FurinaStageLaw.LeadRegen, stage.Regen(2));

        Assert.Equal(3 + FurinaStageLaw.LeadRegen, stage.Lead!.Fanfare);
        Assert.Equal(1, stage.Back!.Fanfare);
    }

    [Fact]
    public void An_empty_stage_regenerates_nothing()
    {
        using var _ = new Arm();
        var (_, stage) = Stage();

        Assert.Equal(0, stage.Regen(9));
    }

    // ==================================================================
    // 6. RULE 2 -- the relic's opening.
    // ==================================================================

    [Fact]
    public void The_relic_opens_with_the_usher_in_front_at_three()
    {
        using var _ = new Arm();
        var (_, stage) = Stage();

        var seat = stage.OpenWith(StagePerformer.Usher);

        Assert.NotNull(seat);
        Assert.Equal(StagePerformer.Usher, stage.Lead!.Who);
        Assert.Equal(FurinaStageLaw.OpeningFanfare, stage.Lead!.Fanfare);
    }

    [Fact]
    public void The_opening_is_idempotent_on_a_stage_that_is_already_lit()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Crabaletta, 1));

        Assert.Null(stage.OpenWith(StagePerformer.Usher));
        Assert.Single(stage.Seats);
        Assert.Equal(StagePerformer.Crabaletta, stage.Lead!.Who);
    }

    // ==================================================================
    // 7. RULE 11 -- her own HP is touched by nothing in the kit.
    // ==================================================================

    [Fact]
    public void Nothing_in_the_arm_moves_her_own_bar()
    {
        // A DENOMINATOR PIN rather than an example: rule 11 is a claim about
        // the WHOLE kit ("no Restore, no Spend from it, no reader on it"), so
        // what is asserted is that no verb in the arm calls any of the engine's
        // HP movers on HER. The performers' own bars are pets' HP and are moved
        // by `SetMaxAndCurrentHp` inside `FurinaStagePets`, which is a
        // different file and a different creature.
        var verbs = new[]
        {
            "OpenCombat", "Summon", "Raise", "Spend", "Bow", "EndOfTurnActs",
            "RegenLead", "Flush", "SceneChange", "CollectAll", "CurtainCall",
            "FinalBow", "Perform", "PerformLead",
        };
        foreach (var verb in verbs)
        {
            var calls = Il.Calls(Il.Method("FurinaStage", verb));
            Assert.DoesNotContain(calls, c => c.Contains("CreatureCmd.Heal"));
            Assert.DoesNotContain(calls, c => c.Contains("CreatureCmd.SetCurrentHp"));
            Assert.DoesNotContain(calls, c => c.Contains("CreatureCmd.GainMaxHp"));
            Assert.DoesNotContain(calls, c => c.Contains("CreatureCmd.LoseMaxHp"));
        }
    }

    // ==================================================================
    // 8. RULE 10 -- the acts are FLAT.
    // ==================================================================

    [Fact]
    public void The_acts_read_no_bar()
    {
        // Sec.3 rule 10's last sentence: "scaling on Fanfare lives in payoff
        // cards, never in the performer". An act that read a bar would delete
        // sec.5.2's whole card slot, so the pin is that the three payouts are
        // the LAW's constants and nothing computed from a seat.
        var strings = Il.Calls(Il.Method("FurinaStage", "Perform"));
        Assert.DoesNotContain(strings, c => c.Contains("StageSeat.get_Fanfare"));
    }

    [Fact]
    public void The_law_is_the_briefs_numbers()
    {
        // Sec.3 and sec.10 default 3, in one place so a retune moves one
        // file -- and that file is the SIM LEG's `FurinaStageLaw`, mirrored by
        // value against `tier0/engine/furina_stage.py`
        // (`tools/lint_constant_parity.py`). This branch's own copy of the
        // eleven was deleted in the `EB-723` reconciliation: two declarations
        // of one number is the drift that gate refuses.
        //
        // TEN AND NOT ELEVEN. "From her SECOND turn on" left with the copy,
        // because the sim states it as a RULE and not a constant
        // (`turn_start_regen`: `state.turn < 2`), and a `RegenFromTurn` here
        // would be a number this side of the wire invented.
        Assert.Equal(3, FurinaStageLaw.Seats);
        Assert.Equal(3, FurinaStageLaw.OpeningFanfare);
        Assert.Equal(1, FurinaStageLaw.SummonFanfare);
        Assert.Equal(1, FurinaStageLaw.LeadRegen);
        Assert.Equal(5, FurinaStageLaw.RefillAmount);
        Assert.Equal(3, FurinaStageLaw.ActUsherBlock);
        Assert.Equal(2, FurinaStageLaw.ActChevalmarinDamage);
        Assert.Equal(5, FurinaStageLaw.ActCrabalettaDamage);
        Assert.Equal(4, FurinaStageLaw.BowUsherBlock);
        Assert.Equal(8, FurinaStageLaw.BowCrabalettaDamage);
    }

    // ==================================================================
    // 9. THE STRIP -- the damage order, in three terms.
    // ==================================================================

    [Fact]
    public void The_strip_is_the_damage_order_in_three_terms()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(
            (StagePerformer.Usher, 3),
            (StagePerformer.Chevalmarin, 5));
        Seat.Set(seat.Creature, "Block", 6);

        var label = Vfx.FurinaStageStrip.Label(seat.Creature);
        var lines = label.Split('\n');

        // Block, then the LEAD's bar, then her HP -- sec.8's last failure mode
        // answered in the order it names.
        Assert.Equal("6 > Usher 3 > 60", lines[0]);
        // The reserve is behind it, because absorption never runs on to it.
        Assert.Equal("Cheval 5", lines[1]);
    }

    [Fact]
    public void An_empty_stage_still_prints_three_terms()
    {
        using var _ = new Arm();
        var (seat, _) = Stage();
        Seat.Set(seat.Creature, "Block", 0);

        // "Nobody is standing there" is exactly the fact a player about to eat
        // a posted intent needs, so the middle term is a dash and not a gap.
        Assert.Equal("0 > -- > 60",
                     Vfx.FurinaStageStrip.Label(seat.Creature));
    }

    [Fact]
    public void The_strip_draws_for_her_alone_and_only_on_the_arm()
    {
        using (new Arm())
        {
            Assert.True(Vfx.FurinaStageStrip.AppliesTo(Seat.Furina().Creature));
            Assert.False(Vfx.FurinaStageStrip.AppliesTo(Seat.Klee().Creature));
        }
        using (new Arm(on: false))
        {
            Assert.False(Vfx.FurinaStageStrip.AppliesTo(Seat.Furina().Creature));
        }
    }
}
