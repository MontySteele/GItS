using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Cards;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// Aura application -- the missing half of the reaction system (R23).
///
/// AuraPower is a self-managing enemy-side power: once an aura EXISTS it
/// handles refresh (same element), amplification and consumption (different
/// element) entirely on its own. But a power that does not exist cannot hear
/// the hit that should create it, so application needs a standing listener.
///
/// That listener is <see cref="KleeElementalHooks"/>, registered through
/// ModHelper.SubscribeForCombatStateHooks -- the game's first-party extension
/// point for exactly this (CombatState.IterateHookListeners ends by yielding
/// every subscribed mod model). No Harmony involved, same as AuraPower itself.
///
/// Application happens in BeforeDamageReceived, i.e. BEFORE the hit resolves.
/// This mirrors tier0's resolve_hit(), where application happens mid-pipeline
/// (a blocked hit still applies its element), and it is what makes ordering
/// safe: AuraPower consumes auras in AfterDamageReceived, a later phase, so
/// this listener can never observe a mid-hit "aura just consumed" state and
/// wrongly stick the trigger element -- after a reaction, nothing sticks.
/// A freshly applied aura then sees the same hit as a same-element trigger:
/// multiplier 1, refresh to full duration. Identical outcomes to the sim.
/// </summary>
public sealed class KleeElementalHooks : AbstractModel
{
    /// <summary>This model exists solely to listen to combat.</summary>
    public override bool ShouldReceiveCombatHooks => true;

    /// <summary>
    /// The canonical instance. ModelDb auto-scans the mod assembly and
    /// constructs one canonical of every AbstractModel subclass itself --
    /// calling `new()` here threw DuplicateModelException at first combat
    /// (playtest 2026-07-20 softlock: the throw re-fired inside every hook
    /// broadcast). Resolved lazily because mod Initialize can run before the
    /// ModelDb scan.
    /// </summary>
    private static KleeElementalHooks? _instance;

    /// <summary>The CombatHookSubscriptionDelegate KleeMod.Initialize registers.</summary>
    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<KleeElementalHooks>(ModelDb.GetId<KleeElementalHooks>());
        yield return _instance;
    }

    /// <summary>
    /// Burst economy, skill-tag half: +5 BEFORE a skill-tagged card resolves,
    /// once per play. The sim's play_card adds BURST_PER_SKILL_TAG ahead of
    /// its effect/replay loop (combat.py, right before resolve_card), so any
    /// effect that rules on the meter mid-card must already see the tag
    /// bonus. The game fires this hook once per replay in a series, so the
    /// IsFirstInSeries gate is what reproduces "once per play_card call".
    /// Resource only -- this hook carries no PlayerChoiceContext.
    /// </summary>
    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        if (cardPlay.Card is ISkillTagCard && cardPlay.IsFirstInSeries)
        {
            KleeBurstResource.GainPreResolution(
                cardPlay.Card.Owner.Creature, BurstConstants.PerSkillTag);
        }
        // Best Friends Forever's ledger (tier0 play_card appends
        // companions_played before resolution; once per play).
        if (cardPlay.Card is ICompanionCard && cardPlay.IsFirstInSeries)
        {
            CompanionPlays.Record(cardPlay.Card.CombatState, cardPlay.Card);
        }
        return Task.CompletedTask;
    }

    /// <summary>
    /// Display half of the burst economy: sync-to-truth after EVERY card
    /// play. Unconditional because two writers move the resource without the
    /// badge -- the skill-tag gain in BeforeCardPlayed (no context there) and
    /// the full-meter drain when the Burst itself is cast (the cost
    /// machinery's Spend, outside our call sites entirely). Delta-zero syncs
    /// are no-ops, so the common case costs nothing.
    ///
    /// Also a kit-grant check site: the sim calls grant_charged_kit at the
    /// end of every play_card (mid-turn gains -- reactions, splash, the
    /// skill tag itself -- fill the meter during plays).
    /// </summary>
    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var owner = cardPlay.Card.Owner;
        await KleeBurstResource.SyncBadge(
            choiceContext, owner.Creature, cardPlay.Card);
        await KitGrant.GrantIfCharged(choiceContext, owner);
    }

    /// <summary>
    /// Kit-grant check, turn-start site: fires AFTER the hand draw
    /// (CombatManager: draw, then this hook), the sim's exact phase -- so
    /// turn-start meter gains (bomb detonations with Blazing Delight splash
    /// land in BeforeSideTurnStart, earlier) grant before the player acts,
    /// and the full-hand deferral sees the drawn hand.
    /// </summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        await KitGrant.GrantIfCharged(choiceContext, player);
    }

    /// <summary>
    /// Kit-grant check, turn-end site: the sim checks after
    /// player_turn_end_triggers (the Sparks 'n' Splash volley can react and
    /// fill the meter) and before the discard filter. This hook maps to
    /// Hook.BeforeTurnEnd -- before the flush -- and mod models run after
    /// power hooks in the same broadcast, so the volley has already fired.
    /// The granted card's Retain then carries it through the flush.
    /// </summary>
    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        foreach (var creature in participants)
        {
            if (creature.Player != null)
            {
                await KitGrant.GrantIfCharged(choiceContext, creature.Player);
            }
        }
    }

    /// <summary>
    /// Opens the reaction_triggered_this_turn window. tier0 zeroes
    /// reactions_this_turn at the top of the player turn, before start-of-turn
    /// bomb detonation -- so this fires one broadcast EARLIER, at the end of
    /// the enemy turn, which reaches the same state without depending on hook
    /// order inside BeforeSideTurnStart.
    /// </summary>
    public override Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side == CombatSide.Enemy) ReactionEffects.MarkTurnStart();
        return Task.CompletedTask;
    }

    /// <summary>
    /// The first player turn has no preceding enemy turn, and TotalResolved is
    /// monotonic across combats -- without this, turn 1 of every combat after
    /// the first would inherit a stale window and read "a reaction already
    /// happened this turn".
    /// </summary>
    public override Task BeforeCombatStart()
    {
        ReactionEffects.MarkTurnStart();
        return Task.CompletedTask;
    }

    public override async Task BeforeDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, decimal amount,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        // Same predicate the rest of the stack uses: unpowered damage (bombs,
        // reaction splash, HP costs) is never element-tagged.
        if (!props.IsPoweredAttack()) return;

        // Only player-side elemental hits on enemies apply auras (sim: the
        // reaction system models the player's elements; enemies have none).
        if (dealer?.Player == null || target.Player != null) return;
        if (target.IsDead) return;

        var element = cardSource is IElementalCard elemental ? elemental.Element : Element.None;
        if (!element.LeavesAura()) return;   // None, and trigger-only Anemo/Geo

        // An existing aura owns this hit (refresh or reaction); one aura per
        // enemy is the invariant.
        if (AuraCmd.Find(target) != null) return;

        await AuraCmd.Apply(choiceContext, target, element, dealer, cardSource);
    }
}

/// <summary>
/// Shared aura plumbing for the application listener and for bomb detonation
/// (which is elemental damage with no card source -- the "own answer"
/// foreshadowed in IElementalCard's doc).
/// </summary>
public static class AuraCmd
{
    /// <summary>The creature's aura, or null. One aura per enemy.</summary>
    public static AuraPower? Find(Creature creature) =>
        creature.Powers.OfType<AuraPower>().FirstOrDefault();

    /// <summary>
    /// Pure application, the port of tier0 apply_aura(): trigger-only elements
    /// never stick. Amount is the aura's remaining duration in turns.
    /// Callers must have checked Find() == null -- applying a second aura type
    /// would break the one-aura invariant.
    /// </summary>
    public static async Task Apply(
        PlayerChoiceContext choiceContext, Creature target, Element element,
        Creature? applier, CardModel? cardSource)
    {
        switch (element)
        {
            case Element.Pyro:
                await PowerCmd.Apply<PyroAuraPower>(
                    choiceContext, target, ReactionConstants.AuraDurationTurns,
                    applier: applier, cardSource: cardSource);
                break;
            case Element.Hydro:
                await PowerCmd.Apply<HydroAuraPower>(
                    choiceContext, target, ReactionConstants.AuraDurationTurns,
                    applier: applier, cardSource: cardSource);
                break;
            case Element.Electro:
                await PowerCmd.Apply<ElectroAuraPower>(
                    choiceContext, target, ReactionConstants.AuraDurationTurns,
                    applier: applier, cardSource: cardSource);
                break;
            case Element.Cryo:
                await PowerCmd.Apply<CryoAuraPower>(
                    choiceContext, target, ReactionConstants.AuraDurationTurns,
                    applier: applier, cardSource: cardSource);
                break;
            default:
                break;   // None / Anemo / Geo: nothing sticks.
        }
    }

    /// <summary>
    /// Reset an aura to full duration -- same ModifyAmount idiom AuraPower's
    /// own same-element branch uses (silent: refreshes are not new debuffs).
    /// </summary>
    public static async Task Refresh(
        PlayerChoiceContext choiceContext, AuraPower aura,
        Creature? applier, CardModel? cardSource)
    {
        await PowerCmd.ModifyAmount(
            choiceContext, aura,
            ReactionConstants.AuraDurationTurns - aura.Amount,
            applier: applier, cardSource: cardSource, silent: true);
    }
}
