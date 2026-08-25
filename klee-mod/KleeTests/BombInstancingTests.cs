using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-130 / R205: ONE BOMB BADGE PER PLACER.
///
/// `BombPower` now declares `PowerInstanceType.InstancedPerApplier`, so a
/// bombed enemy carries one pile per placing creature instead of one merged
/// pile carrying whoever bombed it first. This file pins the four things that
/// ruling forces, in the order the row names them.
///
/// WHAT THIS SUITE CAN AND CANNOT REACH. Placing and detonating a bomb both
/// route through `PowerCmd` and deal damage, which needs a live `CombatState`
/// -- outside the headless boundary (README). So the piles are built by
/// `Harness/Bombs.cs` and the pins land on everything downstream: the
/// suppression arbiter, the `ModifyAll` totals, and the base game's OWN
/// `PowerCmd.FindExistingInstanceForStacking`, which is the pure function
/// `InstancedPerApplier` actually acts through. Where a fact needed a live
/// combat it is pinned structurally and SAID SO.
///
/// THE CO-OP TEST GAP IS REAL AND NARROWED, NOT CLOSED. Two seats placing two
/// piles is expressible here and is tested below. Two seats DETONATING on one
/// enemy is not: it needs damage, death and the hook broadcast. That half stays
/// play-derived, as the repo has recorded since EPOCH 2.
/// </summary>
public class BombInstancingTests
{
    private const int Round = 3;

    private static ValueProp Attack => ValueProp.Move; // IsPoweredAttack()

    // ---------------------------------------------------------------- shape

    [Fact]
    public void Bomb_power_declares_the_ruled_per_placer_instance_type()
    {
        var bomb = (BombPower)RuntimeHelpers.GetUninitializedObject(typeof(BombPower));

        Assert.Equal(PowerInstanceType.InstancedPerApplier, bomb.InstanceType);
    }

    // ------------------------------------------------- per-placer instances

    /// <summary>
    /// Through the GAME's own stacking search, which is the whole mechanism:
    /// `PowerCmd.Apply` asks it which instance to stack into, and under
    /// `InstancedPerApplier` it answers "the one this applier already owns".
    /// </summary>
    [Fact]
    public void Two_placers_get_two_piles_on_the_same_enemy()
    {
        var enemy = Bombed();
        var klee = Seat.Klee().Creature;
        var otherKlee = Seat.Klee().Creature;

        var hers = Bombs.Place(enemy, klee, Round, 5);
        var theirs = Bombs.Place(enemy, otherKlee, Round, 6);

        Assert.Same(hers, PowerCmd.FindExistingInstanceForStacking(hers, enemy, klee));
        Assert.Same(theirs, PowerCmd.FindExistingInstanceForStacking(hers, enemy, otherKlee));
        Assert.Equal(2, enemy.Powers.OfType<BombPower>().Count());
    }

    /// <summary>
    /// SOLO IS BIT-IDENTICAL. One player is one applier is one instance, and
    /// the per-applier search finds exactly what the unscoped search found.
    /// </summary>
    [Fact]
    public void Solo_one_placer_still_stacks_into_the_single_pile()
    {
        var enemy = Bombed();
        var klee = Seat.Klee().Creature;

        var pile = Bombs.Place(enemy, klee, Round, 5, 6);

        Assert.Same(pile, PowerCmd.FindExistingInstanceForStacking(pile, enemy, klee));
        Assert.Single(enemy.Powers.OfType<BombPower>());
        Assert.Equal(11, pile.PendingDamage);
    }

    /// <summary>
    /// GATHER-TRANSFER, destination half. `MoveAllTo` re-applies the gathered
    /// charges with the MOVER as applier and skips the destination as a source,
    /// so a pile the OTHER Klee already had on that destination is neither
    /// absorbed nor overwritten -- it keeps its own instance and its own badge.
    /// The search says so: asking on behalf of the gatherer does not find the
    /// other placer's pile, so a fresh instance is what `PowerCmd.Apply` makes.
    /// </summary>
    [Fact]
    public void A_gather_does_not_land_in_another_placer_s_pile_on_the_destination()
    {
        var dest = Bombed();
        var gatherer = Seat.Klee().Creature;
        var otherKlee = Seat.Klee().Creature;

        var sittingThere = Bombs.Place(dest, otherKlee, Round, 9);

        Assert.Null(PowerCmd.FindExistingInstanceForStacking(sittingThere, dest, gatherer));
        Assert.Same(
            sittingThere,
            PowerCmd.FindExistingInstanceForStacking(sittingThere, dest, otherKlee));
        Assert.Equal(9, sittingThere.PendingDamage);
    }

    // ------------------------------------------------- suppression arbiter

    /// <summary>
    /// THE ARBITER. `ModifyDamageMultiplicative` is per-instance and the engine
    /// folds it (`Hook.ModifyDamageInternal`: `num *= num3` per listener), so
    /// two unarbitrated piles would land the enemy's first attack at 0.5625.
    /// Exactly one 0.75 per enemy per combat is the printed rule.
    /// </summary>
    [Fact]
    public void Two_piles_suppress_the_first_attack_once_not_twice()
    {
        var enemy = Bombed();
        var hers = Bombs.Place(enemy, Seat.Klee().Creature, Round, 5);
        var theirs = Bombs.Place(enemy, Seat.Klee().Creature, Round, 6);

        var first = Multiplier(hers, enemy);
        var second = Multiplier(theirs, enemy);

        Assert.Equal(0.75m, first);
        Assert.Equal(1m, second);
        // The fold the engine actually performs over both listeners.
        Assert.Equal(0.75m, first * second);
        Assert.NotEqual(0.5625m, first * second);
    }

    [Fact]
    public void Solo_suppression_is_the_unchanged_three_quarters()
    {
        var enemy = Bombed();
        var pile = Bombs.Place(enemy, Seat.Klee().Creature, Round, 5);

        Assert.Equal(0.75m, Multiplier(pile, enemy));
    }

    /// <summary>
    /// The seat goes to the first pile WITH LIVE CHARGES, not the first pile.
    /// An emptied instance that has not been removed yet must not hold the
    /// election and silently swallow the reduction.
    /// </summary>
    [Fact]
    public void An_emptied_pile_does_not_hold_the_arbiter_seat()
    {
        var enemy = Bombed();
        var spent = Bombs.Place(enemy, Seat.Klee().Creature, Round);
        var live = Bombs.Place(enemy, Seat.Klee().Creature, Round, 6);

        Assert.Equal(1m, Multiplier(spent, enemy));
        Assert.Equal(0.75m, Multiplier(live, enemy));
    }

    /// <summary>
    /// The intent PREVIEW and the HIT must elect the same pile, or a two-Klee
    /// enemy's intent number disagrees with the damage it deals. The preview
    /// branch evaluates the arbiter live; the in-action branch reads the
    /// snapshot `BeforeAttack` latched. Same answer both ways.
    /// </summary>
    [Fact]
    public void The_preview_and_the_hit_elect_the_same_pile()
    {
        var enemy = Bombed();
        var hers = Bombs.Place(enemy, Seat.Klee().Creature, Round, 5);
        var theirs = Bombs.Place(enemy, Seat.Klee().Creature, Round, 6);

        var previewHers = Multiplier(hers, enemy);
        var previewTheirs = Multiplier(theirs, enemy);

        var attack = Swing(enemy);
        hers.BeforeAttack(attack);
        theirs.BeforeAttack(attack);

        Assert.Equal(previewHers, Multiplier(hers, enemy));
        Assert.Equal(previewTheirs, Multiplier(theirs, enemy));
        Assert.Equal(0.75m, Multiplier(hers, enemy) * Multiplier(theirs, enemy));
    }

    /// <summary>
    /// The creature-keyed spent latch is written by the arbiter alone, so two
    /// piles spend it exactly once -- and the enemy's SECOND attack is at full
    /// damage, which is what "the first attack ... each combat" means.
    /// </summary>
    [Fact]
    public void Two_piles_spend_the_creature_keyed_latch_exactly_once()
    {
        var enemy = Bombed();
        var hers = Bombs.Place(enemy, Seat.Klee().Creature, Round, 5);
        var theirs = Bombs.Place(enemy, Seat.Klee().Creature, Round, 6);
        var context = new ThrowingPlayerChoiceContext();

        var attack = Swing(enemy);
        hers.BeforeAttack(attack);
        theirs.BeforeAttack(attack);
        Assert.Equal(0.75m, Multiplier(hers, enemy) * Multiplier(theirs, enemy));

        hers.AfterAttack(context, attack);
        theirs.AfterAttack(context, attack);

        // Second swing: the latch is spent, so neither pile reduces anything.
        Assert.Equal(1m, Multiplier(hers, enemy));
        Assert.Equal(1m, Multiplier(theirs, enemy));
    }

    // ------------------------------------------------------ iterate-all

    /// <summary>
    /// Chain Fuse buffs "every live bomb". Under instancing the other placer's
    /// bombs are live bombs on the same enemy, so taking the first instance
    /// would silently halve the card on a co-op board.
    /// </summary>
    [Fact]
    public void Chain_fuse_buffs_every_placer_s_pile()
    {
        var enemy = Bombed();
        var hers = Bombs.Place(enemy, Seat.Klee().Creature, Round, 5);
        var theirs = Bombs.Place(enemy, Seat.Klee().Creature, Round, 6, 7);

        BombPower.ModifyAll(
            new[] { enemy }, bonus: 2, placedThisRoundOnly: true, currentRound: Round);

        Assert.Equal(7, hers.PendingDamage);
        Assert.Equal(17, theirs.PendingDamage);
    }

    /// <summary>SOLO TOTAL UNCHANGED: 5+6+7 at +2 each is still 24.</summary>
    [Fact]
    public void Solo_chain_fuse_moves_the_same_total_it_always_did()
    {
        var enemy = Bombed();
        var pile = Bombs.Place(enemy, Seat.Klee().Creature, Round, 5, 6, 7);

        BombPower.ModifyAll(
            new[] { enemy }, bonus: 2, placedThisRoundOnly: true, currentRound: Round);

        Assert.Equal(24, pile.PendingDamage);
        Assert.Equal(24, pile.DisplayAmount);
    }

    /// <summary>
    /// The `placed_this_turn` scope survives the rewrite on EVERY pile: a bomb
    /// stamped with an older round is skipped wherever it sits.
    /// </summary>
    [Fact]
    public void Chain_fuse_s_placed_this_round_scope_holds_on_every_pile()
    {
        var enemy = Bombed();
        var stale = Bombs.Place(enemy, Seat.Klee().Creature, Round - 1, 5);
        var fresh = Bombs.Place(enemy, Seat.Klee().Creature, Round, 6);

        BombPower.ModifyAll(
            new[] { enemy }, bonus: 2, placedThisRoundOnly: true, currentRound: Round);

        Assert.Equal(5, stale.PendingDamage);
        Assert.Equal(8, fresh.PendingDamage);
    }

    /// <summary>
    /// `DetonateOn` now loops instances rather than taking the first. With every
    /// pile already spent the loop short-circuits on each and never reaches a
    /// command, which is the one arm of the new loop a headless test can run.
    /// </summary>
    [Fact]
    public async Task Detonating_an_enemy_whose_piles_are_all_empty_is_a_no_op()
    {
        var enemy = Bombed();
        Bombs.Place(enemy, Seat.Klee().Creature, Round);
        Bombs.Place(enemy, Seat.Klee().Creature, Round);

        var detonated = await BombPower.DetonateOn(
            new ThrowingPlayerChoiceContext(), enemy);

        Assert.Equal(0, detonated);
        Assert.Equal(2, enemy.Powers.OfType<BombPower>().Count());
    }

    /// <summary>
    /// STRUCTURAL PIN, and labelled as one: a real detonation deals damage, so
    /// the loaded arm needs a live combat. What is readable is that neither
    /// "reach every pile" verb takes a `FirstOrDefault` any more, and that both
    /// snapshot with `ToList` before mutating the power list under themselves.
    /// </summary>
    [Theory]
    [InlineData("DetonateOn")]
    [InlineData("MoveAllTo")]
    public void The_reach_every_pile_verbs_no_longer_take_the_first_instance(string verb)
    {
        var calls = Il.Calls(Il.Method("BombPower", verb));

        Assert.Contains("Enumerable.OfType", calls);
        Assert.Contains("Enumerable.ToList", calls);
        Assert.DoesNotContain("Enumerable.FirstOrDefault", calls);
    }

    // --------------------------------------------------- death teardown

    /// <summary>
    /// DEATH TEARDOWN, pinned on the BASE GAME because that is whose machinery
    /// decides it. STRUCTURAL, and labelled: reproducing it needs a live
    /// combat, a kill and a hook broadcast.
    ///
    /// The finding this pins (sts2.dll v0.107.1): if one pile's turn-start
    /// detonation kills the enemy, the OTHER placer's instances never detonate.
    /// Three links make that so, one per assertion below --
    ///   1. death runs INLINE inside the damage command;
    ///   2. the kill detaches the corpse from the combat AND strips its powers;
    ///   3. the hook broadcast re-tests every listener against the combat
    ///      before handing it the hook, and for a power that test reads the
    ///      owner's `CombatState`.
    ///
    /// Solo it is unreachable -- one player is one pile, so there is never a
    /// second instance to skip. If a game update moves any of these three, the
    /// finding is stale and this test is the notice.
    /// </summary>
    [Fact]
    public void Death_resolves_inside_the_damage_command()
    {
        var damage = Game("CreatureCmd")
            .GetMethods(HeadlessGame.All)
            .Where(m => m.Name == "Damage")
            .Select(Il.Calls)
            .ToList();

        Assert.Contains(
            damage,
            calls => calls.Contains("CreatureCmd.Kill")
                     && calls.Contains("Hook.AfterDamageReceived"));
    }

    [Fact]
    public void A_kill_detaches_the_corpse_and_strips_its_powers()
    {
        var calls = Il.Calls(
            Game("CreatureCmd")
                .GetMethod("KillWithoutCheckingWinCondition", HeadlessGame.All)!);

        Assert.Contains("ICombatState.RemoveCreature", calls);
        Assert.Contains("Creature.RemoveAllPowersAfterDeath", calls);
    }

    [Fact]
    public void The_hook_broadcast_retests_every_listener_against_the_combat()
    {
        var iterator = Il.Calls(
            Game("CombatState").GetMethod("IterateHookListeners", HeadlessGame.All)!);
        var contains = Il.Calls(
            Game("CombatState").GetMethod("Contains", HeadlessGame.All)!);

        Assert.Contains("Creature.get_Powers", iterator);
        Assert.Contains("CombatState.Contains", iterator);
        Assert.Contains("Creature.get_CombatState", contains);
    }

    // ------------------------------------------------------------ helpers

    /// <summary>
    /// The creature carrying the piles. A real monster resolves through
    /// `ModelDb`, which only the game's boot populates (README, the headless
    /// boundary) -- so this is a harness seat's Creature. Nothing under test
    /// reads `Monster`: the arbiter reads the owner's power list, and the
    /// stacking search reads power ids and appliers.
    /// </summary>
    private static Creature Bombed() => Seat.Klee().Creature;

    /// <summary>The enemy swinging at the party -- what the -25% applies to.</summary>
    private static decimal Multiplier(BombPower pile, Creature enemy) =>
        pile.ModifyDamageMultiplicative(
            target: null, amount: 10m, props: Attack, dealer: enemy, cardSource: null);

    private static AttackCommand Swing(Creature enemy)
    {
        var attack = new AttackCommand(10m);
        Seat.Set(attack, "Attacker", enemy);
        return attack;
    }

    private static System.Type Game(string typeName) =>
        typeof(Creature).Assembly.GetTypes().First(t => t.Name == typeName);
}
