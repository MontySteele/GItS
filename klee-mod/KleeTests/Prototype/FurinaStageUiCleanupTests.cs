using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE: two notes from a full run on 0.2.3820+proto.
///
///   1. "We still have some Stage elements from the previous builds that
///      crowd out the UI, such as the unused boxes to her left." The boxes
///      are the shipped Salon stage (<see cref="SalonVisualsBridge"/>): three
///      ghost member slots and an Encore ribbon at 0. The reframe stood it
///      down and `EB-726` took that guard out with the reframe, so under the
///      Stage arm it mounted every combat. It does not mount under the arm
///      now, and still mounts with the arm off.
///   2. "I didn't notice any Fanfare decaying." Rule 12 ran, but a
///      performer's bar is written with no number, so the fade (and every
///      hit on the lead) was invisible. Each loss now pops the engine's own
///      damage number over the performer that lost it
///      (<see cref="FurinaStageLossPop"/>).
///
/// WHAT IS REAL HERE: the mount decision, and every pop REQUESTED with its
/// performer and number (<see cref="FurinaStageLossPop.Requested"/> is raised
/// before anything touches Godot). The drawing itself is outside the headless
/// boundary (KleeTests/README.md): no combat room exists in `dotnet test`.
/// </summary>
public class FurinaStageUiCleanupTests
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

    /// <summary>Every pop asked for while this is alive, in order.</summary>
    private sealed class Pops : IDisposable
    {
        internal readonly List<(StagePerformer Who, int Loss)> Seen = new();

        internal Pops() => FurinaStageLossPop.Requested += Note;

        private void Note(StagePerformer who, int loss) => Seen.Add((who, loss));

        public void Dispose() => FurinaStageLossPop.Requested -= Note;
    }

    /// <summary>A Furina seat whose stage holds exactly these bars, built
    /// through the ledger's own verbs.</summary>
    private static Seat Staged(params (StagePerformer Who, int Fanfare)[] seats)
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
        return seat;
    }

    // ==================================================================
    // 1. The shipped Salon stage does not mount under the arm.
    // ==================================================================

    [Fact]
    public void Under_the_stage_arm_the_salon_stage_does_not_mount()
    {
        using var _ = new Arm();
        Assert.False(SalonVisualsBridge.AppliesTo(Seat.Furina().Creature));
    }

    [Fact]
    public void With_the_arm_off_the_salon_stage_still_mounts_for_furina()
    {
        using var _ = new Arm(on: false);
        Assert.True(SalonVisualsBridge.AppliesTo(Seat.Furina().Creature));
    }

    [Fact]
    public void The_salon_stage_is_never_anyone_elses()
    {
        using (new Arm())
        {
            Assert.False(SalonVisualsBridge.AppliesTo(Seat.Klee().Creature));
            Assert.False(SalonVisualsBridge.AppliesTo(null));
        }
        using (new Arm(on: false))
        {
            Assert.False(SalonVisualsBridge.AppliesTo(Seat.Klee().Creature));
        }
    }

    /// <summary>Both doors ask the gate: the combat-open mount and the lazy
    /// rebuild inside Refresh, which every Encore and Salon funnel calls. A
    /// Refresh that skipped it would rebuild the stage the mount refused.
    /// </summary>
    [Theory]
    [InlineData("Setup")]
    [InlineData("Refresh")]
    public void Both_doors_ask_the_gate(string door)
    {
        Assert.Contains("SalonVisualsBridge.AppliesTo",
                        Il.Calls(Il.Method("SalonVisualsBridge", door)));
    }

    // ==================================================================
    // 2. The fade shows, one number per fading performer.
    // ==================================================================

    [Fact]
    public void Each_fading_performer_pops_what_it_lost_and_the_front_pops_nothing()
    {
        using var _ = new Arm();
        using var pops = new Pops();
        var seat = Staged((StagePerformer.Usher, 25),
                          (StagePerformer.Chevalmarin, 9),
                          (StagePerformer.Crabaletta, 15));

        var faded = FurinaStage.FadeAndShow(seat.Creature);

        // The ledger's own table: 9 -> 7 and 15 -> 10; the front never fades.
        Assert.Equal(
            new[] { (StagePerformer.Chevalmarin, 2), (StagePerformer.Crabaletta, 5) },
            pops.Seen.ToArray());
        Assert.Equal(new[] { 2, 5 }, faded.Select(f => f.Loss).ToArray());
        Assert.Equal(new[] { 25, 7, 10 },
                     FurinaStageLedger.For(seat.Creature).Seats
                         .Select(s => s.Fanfare).ToArray());
    }

    [Fact]
    public void A_stage_that_does_not_fade_pops_nothing()
    {
        using var _ = new Arm();
        using var pops = new Pops();
        // A lone performer is the front; bars at or under 5 never fade.
        var lone = Staged((StagePerformer.Crabaletta, 25));
        Assert.Empty(FurinaStage.FadeAndShow(lone.Creature));
        var low = Staged((StagePerformer.Usher, 9),
                         (StagePerformer.Chevalmarin, 5),
                         (StagePerformer.Crabaletta, 1));
        Assert.Empty(FurinaStage.FadeAndShow(low.Creature));
        Assert.Empty(pops.Seen);
    }

    [Fact]
    public void With_the_arm_off_nothing_fades_and_nothing_pops()
    {
        using var _ = new Arm(on: false);
        using var pops = new Pops();
        var seat = Seat.Furina().WithCombatState();
        Assert.Empty(FurinaStage.FadeAndShow(seat.Creature));
        Assert.Empty(pops.Seen);
    }

    // ==================================================================
    // 2b. A hit on the lead shows too (the pets had no number for it).
    // ==================================================================

    [Fact]
    public void A_hit_on_the_lead_pops_the_fanfare_it_took()
    {
        using var _ = new Arm();
        using var pops = new Pops();
        var seat = Staged((StagePerformer.Usher, 6),
                          (StagePerformer.Chevalmarin, 3));

        var reached = FurinaStage.AbsorbHit(seat.Creature, 4, dealer: null);

        Assert.Equal(0, reached);
        Assert.Equal(new[] { (StagePerformer.Usher, 4) }, pops.Seen.ToArray());
    }

    [Fact]
    public void A_hit_that_empties_the_lead_pops_its_whole_bar()
    {
        using var _ = new Arm();
        using var pops = new Pops();
        var seat = Staged((StagePerformer.Crabaletta, 3));

        FurinaStage.AbsorbHit(seat.Creature, 10, dealer: null);

        Assert.Equal(new[] { (StagePerformer.Crabaletta, 3) }, pops.Seen.ToArray());
    }

    // ==================================================================
    // 3. The Stage retires the shipped Burst (EB-726 dropped the guards).
    // ==================================================================

    /// <summary>A reaction's Burst credit lands in <c>GainBurst</c>
    /// (<c>ReactionEffects.Resolve</c>, pinned below); the reaction itself is
    /// a live path outside the headless boundary, so the funnel's decision is
    /// what is asked, as Kokomi's `EB-327` pin asks it.</summary>
    [Fact]
    public void A_reaction_pays_no_burst_under_the_stage()
    {
        using var _ = new Arm();
        var furina = Seat.Furina().WithCombatState().Creature;
        FurinaResources.GainBurst(furina, FurinaResourceConstants.BurstPerReaction);
        Assert.Equal(0, FurinaResources.Burst(furina));
    }

    [Fact]
    public void With_the_arm_off_a_reaction_pays_burst_as_it_ships()
    {
        using var _ = new Arm(on: false);
        var furina = Seat.Furina().WithCombatState().Creature;
        FurinaResources.GainBurst(furina, FurinaResourceConstants.BurstPerReaction);
        Assert.Equal(FurinaResourceConstants.BurstPerReaction,
                     FurinaResources.Burst(furina));
    }

    [Fact]
    public void The_reaction_credit_still_goes_through_the_guarded_funnel()
    {
        Assert.Contains("FurinaResources.GainBurst",
                        Il.Calls(Il.Method("ReactionEffects", "Resolve")));
    }

    /// <summary>
    /// The shipped <i>Let the People Rejoice</i> is never granted under the
    /// arm, even from a meter already at its max (a save, or any write
    /// outside the funnel). The grant asks the arm before it reads the meter
    /// or touches the hand, so a full meter returns without creating a card.
    /// </summary>
    [Fact]
    public void The_kit_card_is_never_granted_under_the_stage()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        CustomResources<FurinaBurstResource>
            .Get(seat.Player.PlayerCombatState!).Amount =
            FurinaResourceConstants.BurstMax;

        var grant = FurinaKitGrant.GrantIfCharged(
            new ThrowingPlayerChoiceContext(), seat.Player);
        Assert.True(grant.IsCompletedSuccessfully);

        var calls = Il.CallSequence(Il.Method("FurinaKitGrant", "GrantIfCharged"))
            .ToList();
        var gate = calls.IndexOf("FurinaResources.StageRetiresTheShippedMeters");
        var hand = calls.IndexOf("CardPile.Get");
        Assert.True(gate >= 0 && hand > gate, string.Join(", ", calls));
    }

    [Fact]
    public void A_hit_with_nothing_through_block_or_no_stage_pops_nothing()
    {
        using var _ = new Arm();
        using var pops = new Pops();
        var staged = Staged((StagePerformer.Usher, 6));
        FurinaStage.AbsorbHit(staged.Creature, 0, dealer: null);
        var empty = Staged();
        FurinaStage.AbsorbHit(empty.Creature, 5, dealer: null);
        Assert.Empty(pops.Seen);
    }
}
