using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// RULE 3's TWO MISSING MOMENTS (<c>EB-279</c>).
///
/// WHAT [USER] SAW. A Bombed enemy died to something that was not a Set off --
/// a companion's Attack, a plain hit, a poison -- and its Bombs did not move.
/// They were not lost: <see cref="ProtoBombPower.Register"/> still held them,
/// and the next Set off or the next turn start swept them onto a living enemy.
/// But between those two moments they were off the board and invisible, and a
/// rule the player cannot see happen is a rule the player does not have.
///
/// WHY THE EXISTING SWEEPS WERE NOT ENOUGH. <see cref="ProtoBombPower.SweepJumps"/>
/// runs at the start of Klee's turn, at the end of every Set off and after a
/// Mine fires. Every one of those is a moment the ARM caused. A kill by any
/// other source is exactly the case rule 3 spells out ("A partner or a poison
/// killed the enemy: all of them jump") and it is the one the arm was not
/// watching for.
///
/// THE TWO MOMENTS ADDED HERE, and both are broadcast hooks on a STANDING
/// listener rather than hooks on the dying enemy's own power:
///
///   * <see cref="AfterDeath"/> -- the moment itself. `ProtoBombPower`'s own
///     comment says there is no hook ON THE DYING ENEMY'S POWER that can be
///     trusted, and that is still true: the base game does not broadcast
///     `AfterDamageReceived` for a killing blow, and `RemoveAllPowersAfterDeath`
///     strips the corpse's powers before control returns. This is a different
///     hook. `Hook.AfterDeath` walks `runState.IterateHookListeners`, which is
///     the enumeration a mod's `SubscribeForCombatStateHooks` model rides, and
///     `CreatureCmd.KillWithoutCheckingWinCondition` fires it BEFORE
///     `CombatManager.RemoveCreature` and BEFORE `RemoveAllPowersAfterDeath` --
///     so a listener that is not the corpse sees the death while the register
///     still points at a real pile, and it is handed a
///     <c>PlayerChoiceContext</c>, which a jump needs because placing a charge
///     applies a power.
///
///   * <see cref="AfterCardPlayed"/> -- the backstop, for ANY card and ANY
///     owner, companion cards included. A death is not the only way a pile can
///     be orphaned (an enemy that escapes, a corpse a hook keeps around), and
///     the guarantee the row asks for is that the Bombs are on a living enemy
///     "before the next card is played". Asking after every play is the
///     cheapest way to mean that literally.
///
/// WHY NOT `BeforeDeath`: it fires even when the death is about to be
/// PREVENTED, so a Fairy-in-a-Bottle enemy would have its Bombs jumped off a
/// creature that then survives. <see cref="AfterDeath"/> is told which case it
/// is and declines the prevented one, which is the same distinction
/// <c>Register.Claim</c> would otherwise have to guess at.
///
/// IDEMPOTENT BY CONSTRUCTION. <c>Register.Claim</c> empties itself as it is
/// claimed, so the extra calls cost a list walk on a board with nothing owed
/// and the existing sweeps are untouched -- they are kept, not replaced,
/// because each of them is the earliest moment for the death IT is about.
///
/// INERT WITH THE ARM OFF, and it says so rather than relying on it: with
/// <c>KleeOverhaul.Enabled</c> false no card places a
/// <see cref="ProtoBombPower"/>, so the register is empty and the sweep is a
/// no-op -- but the flag is read anyway, for the reason
/// <c>PoundingSurprise.OnBombExploded</c> reads it.
/// </summary>
public sealed class KleeOverhaulSweepHooks : AbstractModel
{
    /// <summary>This model exists solely to listen to combat.</summary>
    public override bool ShouldReceiveCombatHooks => true;

    /// <summary>
    /// The canonical instance, resolved lazily. Same shape and same reason as
    /// <c>KleeElementalHooks.Subscribe</c>: ModelDb constructs one canonical of
    /// every <c>AbstractModel</c> subclass itself, so `new()` here would throw
    /// <c>DuplicateModelException</c> inside every hook broadcast, and mod
    /// Initialize can run before the ModelDb scan.
    /// </summary>
    private static KleeOverhaulSweepHooks? _instance;

    /// <summary>The CombatHookSubscriptionDelegate KleeMod.Initialize registers.</summary>
    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<KleeOverhaulSweepHooks>(
            ModelDb.GetId<KleeOverhaulSweepHooks>());
        yield return _instance;
    }

    /// <summary>
    /// RULE 3 at the moment the rule is about. <paramref name="wasRemovalPrevented"/>
    /// is the revive case and is declined: nothing has died there, so nothing
    /// is owed a jump.
    /// </summary>
    public override async Task AfterDeath(
        PlayerChoiceContext choiceContext, Creature creature,
        bool wasRemovalPrevented, float deathAnimLength)
    {
        if (!KleeOverhaul.Enabled || wasRemovalPrevented) return;
        await ProtoBombPower.SweepJumps(choiceContext, creature.CombatState);
    }

    /// <summary>
    /// The backstop the acceptance is worded on: whatever else happened, the
    /// Bombs are on a living enemy before the next card is played. Any card,
    /// any owner -- a companion card is played by the same player and reaches
    /// this hook exactly as her own cards do.
    /// </summary>
    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!KleeOverhaul.Enabled) return;
        await ProtoBombPower.SweepJumps(
            choiceContext, cardPlay.Card?.CombatState);
    }

    /// <summary>
    /// `EB-336`. THE HIT A LETHAL MINE ALREADY ANSWERED COSTS NO HP.
    ///
    /// <c>ModifyHpLostBeforeOsty</c> is the FIRST hook after
    /// <c>Hook.BeforeDamageReceived</c> that can move the number
    /// (<c>CreatureCmd.Damage</c>: modify -> before-received -> block -> THIS
    /// -> osty -> <c>LoseHpInternal</c>), so it is where the Mine's
    /// pre-emption is spent. <see cref="ProtoBombPower.Preempted"/> carries the
    /// whole argument for why the kill alone was not enough and for what Block
    /// still does.
    ///
    /// IT IS HERE AND NOT ON THE PILE because the pile is GONE by then: the
    /// kill runs inline and <c>RemoveAllPowersAfterDeath</c> strips the
    /// corpse's powers before control returns, so the dead enemy's own power is
    /// not in <c>IterateHookListeners</c> any more. This model is, for the same
    /// reason <see cref="AfterDeath"/> is here.
    ///
    /// PURE, and it has to be: the engine calls modifier hooks to answer
    /// PREVIEWS as well as real hits (the Vigil's note in
    /// <c>KuragePowers.cs</c>), so this reads three references and one flag and
    /// writes nothing. A preview asks about a LIVE attacker, so the predicate
    /// is false and no preview moves.
    /// </summary>
    public override decimal ModifyHpLostBeforeOsty(
        Creature target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (!KleeOverhaul.Enabled || amount <= 0m) return amount;
        if (!props.IsPoweredAttack()) return amount;
        return ProtoBombPower.Preempted.Covers(target, dealer) ? 0m : amount;
    }
}
