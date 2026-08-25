using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-138 / R211 — THE DEATH-TEARDOWN COMPENSATION.
///
/// `EB-130` made a bombed enemy carry one pile per placing creature, and the
/// base game's own machinery then took something away that the merged pile had:
/// a turn-start detonation that KILLS runs its kill inline, the kill detaches
/// the corpse and strips its powers, and the hook broadcast re-tests each
/// listener against the combat before handing it the hook — so every later
/// placer's pile was torn down before its slot arrived and never detonated.
/// That placer lost the bombs, their Big One credit and their detonation
/// listeners. A CO-OP REGRESSION, not a new rule: in the old merged-payload
/// world those bombs were trailing entries in one already-spent list, so they
/// were consumed, credited and fed to listeners after a kill.
///
/// THE REPAIR IS ONE MOVE: take every pile BEFORE any damage begins, and
/// resolve from the snapshot. `BombInstancingTests` pins the three base-game
/// links that make the teardown happen; this file pins what the mod now does
/// about them.
///
/// WHAT THIS SUITE CAN AND CANNOT REACH. The take is PURE — no commands — so
/// every assertion about it is real. Everything past it is not: `PowerCmd`
/// and `ElementalHit.Deal` need a live `CombatState` (README, "The headless
/// boundary"), so the detach and the damage are pinned structurally and said
/// so. The two things the row's acceptance names beyond consumption — the
/// placer's counter and the placer's listeners — ARE reachable, because both
/// are driven by the snapshot's applier rather than by the power, and both are
/// exercised below through the shipped private statics.
///
/// STILL PLAY-DERIVED, and narrowed rather than closed: two seats actually
/// DETONATING on one enemy, and the fizzle itself — the engine clamping a hit
/// that lands on a corpse, which tier0 does by clamping to remaining HP
/// (`effects.detonate_bombs` / `deal_damage_to_enemy`) and which the mod
/// inherits from the same damage pipeline. Neither needs a decision; both need
/// a combat.
/// </summary>
public class BombDeathTeardownTests
{
    private const int Round = 3;

    /// <summary>A test-only detonation listener — the shape Pounding Surprise,
    /// Blazing Delight, Explosive Frags and Touch of Orobas all wear. Allocated
    /// uninitialised for the reason <see cref="Seat.WithPower{T}"/> gives: a
    /// CustomPowerModel's constructor registers with BaseLib's model tables,
    /// which is state a test has no business mutating.</summary>
    private sealed class RecordingListener : PowerModel, IBombDetonationListener
    {
        internal List<int> Heard = new();

        public override PowerType Type => PowerType.Buff;

        public override PowerStackType StackType => PowerStackType.Counter;

        public Task OnBombDetonated(
            PlayerChoiceContext choiceContext, Creature applier, Creature target,
            int damage)
        {
            Heard.Add(damage);
            return Task.CompletedTask;
        }
    }

    // ------------------------------------------------------- the take

    /// <summary>
    /// The whole compensation in one assertion: ONE instance's turn-start work
    /// reaches EVERY pile on the enemy, each pile keeps its own placer and its
    /// own payload, and every pile is empty before anything that can kill has
    /// run.
    /// </summary>
    [Fact]
    public void Every_pile_is_taken_before_any_damage_can_begin()
    {
        var enemy = Bombed();
        var hers = Seat.Klee().Creature;
        var theirs = Seat.Klee().Creature;
        var herPile = Bombs.Place(enemy, hers, Round, 12);
        var theirPile = Bombs.Place(enemy, theirs, Round, 5, 6);

        var taken = BombPower.TakeTurnStartPiles(enemy);

        Assert.Equal(2, taken.Count);
        // Application order, which is the enemy's own power list order.
        Assert.Same(hers, taken[0].Applier);
        Assert.Same(theirs, taken[1].Applier);
        Assert.Equal(new[] { 12 }, taken[0].Payload);
        Assert.Equal(new[] { 5, 6 }, taken[1].Payload);
        // Spent on both piles, badges included -- the recursion guard.
        Assert.Equal(0, herPile.PendingDamage);
        Assert.Equal(0, theirPile.PendingDamage);
        Assert.Equal(0, theirPile.DisplayAmount);
    }

    /// <summary>SOLO IS THE ORDER IT ALWAYS WAS: one placer, one pile, one
    /// take, and the payload is the same list the single-pile path spent.
    /// </summary>
    [Fact]
    public void Solo_one_pile_is_taken_exactly_as_before()
    {
        var enemy = Bombed();
        var pile = Bombs.Place(enemy, Seat.Klee().Creature, Round, 5, 6, 7);

        var taken = Assert.Single(BombPower.TakeTurnStartPiles(enemy));

        Assert.Equal(new[] { 5, 6, 7 }, taken.Payload);
        Assert.Equal(0, pile.PendingDamage);
    }

    /// <summary>
    /// IDEMPOTENT BY CONSTRUCTION, which is what lets any instance be the one
    /// that runs it. The hook fires once per instance; the first one to arrive
    /// takes everything, so every later slot finds nothing and no-ops.
    /// </summary>
    [Fact]
    public void A_second_instances_hook_slot_finds_nothing_left_to_take()
    {
        var enemy = Bombed();
        Bombs.Place(enemy, Seat.Klee().Creature, Round, 12);
        Bombs.Place(enemy, Seat.Klee().Creature, Round, 5, 6);

        Assert.Equal(2, BombPower.TakeTurnStartPiles(enemy).Count);
        Assert.Empty(BombPower.TakeTurnStartPiles(enemy));
    }

    /// <summary>An already-empty instance is not a pile. It contributes no
    /// entry, so nothing downstream lobs a VFX or rings a listener for it.
    /// </summary>
    [Fact]
    public void An_emptied_instance_contributes_no_pile()
    {
        var enemy = Bombed();
        Bombs.Place(enemy, Seat.Klee().Creature, Round);
        Bombs.Place(enemy, Seat.Klee().Creature, Round, 6);

        var taken = Assert.Single(BombPower.TakeTurnStartPiles(enemy));

        Assert.Equal(new[] { 6 }, taken.Payload);
    }

    // ------------------------------------------- surviving the teardown

    /// <summary>
    /// THE ROW'S ACCEPTANCE SHAPE. Pile 1's payload kills; the game's own kill
    /// path then detaches the corpse and strips every power off it. Before this
    /// row that took pile 2 with it. Now pile 2's bombs are already spent and
    /// its payload and placer are held in the snapshot, so the teardown has
    /// nothing left to remove — which is the entire mechanism.
    ///
    /// The kill is reproduced with the two steps `CreatureCmd` performs and
    /// `BombInstancingTests` pins on the base game: the creature is dead, and
    /// `RemoveAllPowersAfterDeath` strips it.
    /// </summary>
    [Fact]
    public void A_later_placers_pile_survives_the_teardown_that_used_to_lose_it()
    {
        var enemy = Bombed();
        var hers = Seat.Klee().Creature;
        var theirs = Seat.Klee().Creature;
        Bombs.Place(enemy, hers, Round, 12);
        Bombs.Place(enemy, theirs, Round, 5, 6);

        var taken = BombPower.TakeTurnStartPiles(enemy);
        Kill(enemy);

        Assert.True(enemy.IsDead);
        Assert.Empty(enemy.Powers);           // the teardown really ran
        Assert.Equal(new[] { 5, 6 }, taken[1].Payload);
        Assert.Same(theirs, taken[1].Applier);
        Assert.NotSame(hers, taken[1].Applier);
    }

    /// <summary>
    /// STRUCTURAL, and labelled: resolving a payload deals damage, which needs
    /// a live combat. What is readable is the property that makes the snapshot
    /// worth taking — `ResolvePayload` is static and reads its applier and its
    /// combat off the pile it was handed, never off a power. A resolution that
    /// asked the power would be asking a corpse.
    /// </summary>
    [Fact]
    public void Resolution_reads_the_snapshot_rather_than_the_power()
    {
        var calls = Il.Calls(Il.Method("BombPower", "ResolvePayload"));

        Assert.Contains("TurnStartPile.get_Applier", calls);
        Assert.Contains("TurnStartPile.get_Combat", calls);
        Assert.DoesNotContain("PowerModel.get_Applier", calls);
        Assert.DoesNotContain("PowerModel.get_CombatState", calls);
    }

    // -------------------------------------------- credit and listeners

    /// <summary>
    /// The counters the lost piles used to cost their placer. Resolved AFTER
    /// the kill, with the corpse flag the per-bomb test sets, both of pile 2's
    /// bombs credit pile 2's placer — and none of them touch pile 1's, which is
    /// the per-player scoping `EPOCH 2 / D2` put on the ledger.
    ///
    /// Reaches the shipped private static by reflection, the same way the rest
    /// of this project reaches non-public game state (`Harness/Bombs.cs`).
    /// </summary>
    [Fact]
    public void A_pile_resolved_after_the_kill_still_credits_its_own_placer()
    {
        var enemy = Bombed();
        var hers = Seat.Klee();
        var theirs = Seat.Klee();
        Bombs.Place(enemy, hers.Creature, Round, 12);
        Bombs.Place(enemy, theirs.Creature, Round, 5, 6);

        var taken = BombPower.TakeTurnStartPiles(enemy);
        Kill(enemy);

        var combat = Combat();
        foreach (var _ in taken[1].Payload)
        {
            Record(combat, taken[1].Applier!, onCorpse: enemy.IsDead);
        }

        Assert.Equal(2, BombPower.DetonationsThisCombat(combat, theirs.Player));
        // Every one of them landed on a corpse, which is what the EB-18 ledger
        // is FOR -- and is the reading under which "no damage landed" is
        // recorded rather than asserted about HP.
        Assert.Equal(2, BombPower.CorpseDetonationsThisCombat(combat, theirs.Player));
        Assert.Equal(0, BombPower.DetonationsThisCombat(combat, hers.Player));
    }

    /// <summary>
    /// The listener grants the lost piles used to cost their placer — Pounding
    /// Surprise, Blazing Delight, Explosive Frags, Touch of Orobas. The bus is
    /// keyed on the SNAPSHOT's applier, so it rings the second placer's own
    /// powers after the kill and rings nothing of the first placer's.
    /// </summary>
    [Fact]
    public async Task A_pile_resolved_after_the_kill_still_rings_its_own_listeners()
    {
        var enemy = Bombed();
        var hers = Seat.Klee();
        var theirs = Seat.Klee();
        var herEar = Listening(hers.Creature);
        var theirEar = Listening(theirs.Creature);
        Bombs.Place(enemy, hers.Creature, Round, 12);
        Bombs.Place(enemy, theirs.Creature, Round, 5, 6);

        var taken = BombPower.TakeTurnStartPiles(enemy);
        Kill(enemy);

        foreach (var damage in taken[1].Payload)
        {
            await Notify(taken[1].Applier!, enemy, damage);
        }

        Assert.Equal(new[] { 5, 6 }, theirEar.Heard);
        Assert.Empty(herEar.Heard);
    }

    // ------------------------------------------------------ the seam

    /// <summary>
    /// THE MUTATION CHECK. Reverting the compensation means putting
    /// `await Detonate(choiceContext);` back in the turn-start hook, and this
    /// is the test that fails when someone does: the hook resolves the ENEMY,
    /// not its own instance.
    ///
    /// Structural, and labelled — a real turn start needs a combat — but the
    /// thing it reads is exactly the thing the row changed.
    /// </summary>
    [Fact]
    public void The_turn_start_hook_resolves_every_pile_not_only_its_own()
    {
        var calls = Il.Calls(Il.Method("BombPower", "BeforeSideTurnStart"));

        Assert.Contains("BombPower.ResolveTurnStartPiles", calls);
        Assert.DoesNotContain("BombPower.Detonate", calls);
    }

    /// <summary>
    /// And the compensation stops at the turn-start seam, which is where the
    /// finding is. EARLY detonation stays per instance because the base game
    /// does not broadcast `AfterDamageReceived` at all for a blow that killed
    /// (`CreatureCmd.Damage`), so no pile — first or later — ever sees that
    /// hook on a killing hit and there is nothing there to compensate for.
    /// </summary>
    [Fact]
    public void Early_detonation_still_pops_this_instances_pile()
    {
        var calls = Il.Calls(Il.Method("BombPower", "AfterDamageReceived"));

        Assert.Contains("BombPower.Detonate", calls);
        Assert.DoesNotContain("BombPower.ResolveTurnStartPiles", calls);
    }

    // ------------------------------------------------------------ helpers

    private static Creature Bombed() => Seat.Klee().Creature;

    /// <summary>The two steps the game's kill path performs that this row is
    /// about, and the two `BombInstancingTests` pins on `CreatureCmd`: the
    /// creature is dead, and its powers are stripped.</summary>
    private static void Kill(Creature creature)
    {
        Seat.Set(creature, "CurrentHp", 0);
        typeof(Creature).GetMethod("RemoveAllPowersAfterDeath", HeadlessGame.All)!
            .Invoke(creature, null);
    }

    /// <summary>A combat to key the per-player ledgers on. Only its IDENTITY is
    /// read (`ReferenceEquals` against the counter's own combat), so it is
    /// allocated uninitialised rather than booted.</summary>
    private static ICombatState Combat() =>
        (ICombatState)RuntimeHelpers.GetUninitializedObject(typeof(CombatState));

    private static void Record(ICombatState combat, Creature applier, bool onCorpse) =>
        typeof(BombPower).GetMethod("RecordDetonation", HeadlessGame.All)!
            .Invoke(null, new object[] { combat, applier, onCorpse });

    private static Task Notify(Creature applier, Creature target, int damage) =>
        (Task)typeof(BombPower)
            .GetMethod("NotifyDetonationListeners", HeadlessGame.All)!
            .Invoke(null, new object[]
            {
                new ThrowingPlayerChoiceContext(), applier, target, damage,
            })!;

    private static RecordingListener Listening(Creature creature)
    {
        var listener = (RecordingListener)RuntimeHelpers
            .GetUninitializedObject(typeof(RecordingListener));
        typeof(RecordingListener).GetField("Heard", HeadlessGame.All)!
            .SetValue(listener, new List<int>());

        var powers = (List<PowerModel>)typeof(Creature)
            .GetField("_powers", HeadlessGame.All)!
            .GetValue(creature)!;
        powers.Add(listener);
        return listener;
    }
}
