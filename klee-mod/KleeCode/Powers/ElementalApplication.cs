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
        // Sim order (combat.py play_card): the requires-full drain happens
        // FIRST, then the skill-tag bonus. Once per play, never per replay.
        if (cardPlay.IsFirstInSeries)
        {
            KleeBurstResource.DrainOnPlay(cardPlay.Card);
        }
        // Owner is null on autoplay/token paths. This hook fires for every
        // card every player plays, inside CombatManager's async continuation,
        // so an NRE here reaches the player as a black screen rather than an
        // error -- guarded for the same reason DrainOnPlay guards internally.
        if (cardPlay.Card is ISkillTagCard && cardPlay.IsFirstInSeries
            && cardPlay.Card.Owner?.Creature is { } skillTagOwner)
        {
            KleeBurstResource.GainPreResolution(
                skillTagOwner, BurstConstants.PerSkillTag);
        }
        // Best Friends Forever's ledger (tier0 _finish_play records
        // companions_played before resolution; once per play, deduped on the
        // base id -- BFF-dedupe, ruled 2026-08-06).
        if (cardPlay.Card is ICompanionCard && cardPlay.IsFirstInSeries)
        {
            CompanionPlays.Record(cardPlay.Card.CombatState, cardPlay.Card);
            // "Little Hexenzirkul" (EB-219 / LAW:145): Klee's kit answering a
            // PERSONAL Companion play, armed here and settled in
            // AfterCardPlayed. Same IsFirstInSeries gate as the ledger above,
            // and for the same reason -- once per play_card call, never once
            // per replay. The sim's twin brackets the same span
            // (effects.klee_personal_companion_spark, called from
            // combat._finish_play after the FIRST resolution).
            KleeCompanionSpark.Arm(cardPlay);
        }
        return Task.CompletedTask;
    }

    /// <summary>
    /// Display half of the burst economy: gauge catch-up after EVERY card
    /// play. Unconditional because one writer moves the resource outside the
    /// refresh funnels -- the full-meter drain when the Burst itself is cast
    /// (the cost machinery's Spend, outside our call sites entirely).
    /// Redundant refreshes redraw the same value, so the common case costs
    /// nothing.
    ///
    /// Also a kit-grant check site: the sim calls grant_charged_kit at the
    /// end of every play_card (mid-turn gains -- reactions, splash, the
    /// skill tag itself -- fill the meter during plays).
    /// </summary>
    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // Same ownerless-play guard as BeforeCardPlayed above.
        var owner = cardPlay.Card?.Owner;
        if (owner?.Creature is not { } creature) return;
        // The Personal-Companion Spark mint, settled BEFORE the gauge sync and
        // the kit-grant check: a Spark is not Burst Energy, but a reader of
        // this method should see the resource writes finish before the display
        // and the grant read them. Settle is a no-op unless BeforeCardPlayed
        // armed it, and it disarms itself either way.
        if (cardPlay.IsFirstInSeries)
        {
            await KleeCompanionSpark.Settle(choiceContext, cardPlay);
        }
        KleeBurstResource.SyncGauge(creature);
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
#if PROTOTYPE_CARDS
        await KleeOverhaulOpening.GrantSpark(choiceContext, player);
        // `EB-479` (R258): the reframe's opening Encore, at the same site and
        // for the same reason as the opening Spark above it. Synchronous
        // because `FurinaResources.GainEncore` is -- Encore needs no
        // `PlayerChoiceContext`, and the funnel it goes through is the one the
        // gauge and the stage ribbon already read.
        FurinaReframeOpening.GrantEncore(player);
        // `EB-553` (R260): and the member the stage opens with, AFTER the
        // grant. She performs on arrival -- a deploy performs -- and that
        // performance spends Encore, so a fielding that ran before the line
        // above would leave her acting dry at three-quarters on the one turn
        // the player could not have paid for her.
        await FurinaReframeOpening.FieldOpeningMember(choiceContext, player);
#endif
        await KitGrant.GrantIfCharged(choiceContext, player);
    }

    /// <summary>
    /// Kit-grant check, turn-end site: the sim checks after
    /// player_turn_end_triggers (the Sparks 'n' Splash volley can react and
    /// fill the meter) and before the discard filter. This hook maps to
    /// Hook.BeforeTurnEnd -- before the flush -- and mod models run after
    /// power hooks in the same broadcast, so the volley has already fired.
    /// Durin resolves later in AfterSideTurnEnd to guarantee it consumes the
    /// volley's Pyro; its Burst Energy is granted at the next turn-start check.
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
    /// An EXTRA player turn has no preceding enemy turn either, so
    /// AfterSideTurnEnd above never fires and the window would carry across
    /// two player turns. This is the other end of the same problem
    /// BeforeCombatStart below solves, and it is sited here rather than at
    /// BeforeSideTurnStart because bombs detonate inside that broadcast --
    /// see ReactionEffects.MarkExtraTurnStart for the full argument and for
    /// why only the extra-turn player's per-dealer key is dropped.
    /// </summary>
    public override Task AfterTakingExtraTurn(Player player)
    {
        ReactionEffects.MarkExtraTurnStart(player.Creature);
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
        // `EB-423`. THE DAMAGE-EVENT BOUNDARY for the Shatter mark, and it is
        // FIRST, above every guard below: this hook is the one thing that runs
        // for EVERY hit -- powered or not, on a monster or a player -- in the
        // broadcast BEFORE any power's `AfterDamageReceived`, which is exactly
        // the lifetime the mark needs. Unconditional, so the nested Unpowered
        // hit the Shatter itself deals clears it too (the mark is set after
        // that hit lands, at `FrozenPower`), and so no mark can outlive the
        // one broadcast it is about. The whole argument is at
        // `ReactionEffects.MarkShattered`.
        ReactionEffects.ClearShatterMark();

        // Same predicate the rest of the stack uses: unpowered damage (bombs,
        // reaction splash, HP costs) is never element-tagged.
        if (!props.IsPoweredAttack()) return;

        // Only player-side elemental hits on enemies apply auras (sim: the
        // reaction system models the player's elements; enemies have none).
        if (dealer?.Player == null || target.Player != null) return;
        if (target.IsDead) return;

        // Through the one funnel (AuraCmd.ElementOfPlay), so the aura applied
        // here and the reaction AuraPower reads later cannot be different
        // elements. Identical to the old inline read with no rider standing.
        var element = AuraCmd.ElementOfPlay(cardSource, dealer);
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
    /// WHICH ELEMENT THIS PLAY APPLIES. The one answer, for the application
    /// listener and for <see cref="AuraPower"/>'s two reaction reads alike.
    ///
    /// It used to be <c>cardSource is IElementalCard</c> written out at each of
    /// those three sites, which was correct while the element was a property of
    /// the CARD alone. The quarantined Mondstadt companion overhaul prints
    /// three cards that change what an Attack applies -- "your next Attack ...
    /// applies Pyro", "for 2 turns, your Attacks apply Electro", "6 more damage
    /// of the swirled element" -- so the answer now depends on the DEALER too,
    /// and a site that applied one aura while another reacted with a different
    /// element would be the worst kind of bug to find in play. One funnel.
    ///
    /// PURE, because every caller is reached from a preview path.
    ///
    /// WITHOUT the prototype switch this is character for character the
    /// expression the three sites carried before, so a release build is
    /// unchanged and the arm's classes are not compiled at all.
    /// </summary>
    public static Element ElementOfPlay(CardModel? cardSource, Creature? dealer)
    {
#if PROTOTYPE_CARDS
        return CompanionOverhaulRiders.ElementFor(cardSource, dealer);
#else
        return cardSource is IElementalCard elemental
            ? elemental.Element : Element.None;
#endif
    }

    /// <summary>
    /// How long an aura applied or refreshed by <paramref name="applier"/>
    /// lasts. Port of tier0 reactions.aura_duration(state).
    ///
    /// A function rather than the constant read at each site, for the reason
    /// the sim gives: application and refresh must never disagree about how
    /// long an aura lives, which they would the first time someone extended
    /// only one of them. Neuvillette's Heir to the Ancient Sea's Authority is
    /// the first thing that extends it.
    /// </summary>
    public static int Duration(Creature? applier) =>
        ReactionConstants.AuraDurationTurns
        + AncientSeaAuthorityPower.ExtraTurnsFrom(applier);

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
                    choiceContext, target, Duration(applier),
                    applier: applier, cardSource: cardSource);
                break;
            case Element.Hydro:
                await PowerCmd.Apply<HydroAuraPower>(
                    choiceContext, target, Duration(applier),
                    applier: applier, cardSource: cardSource);
                break;
            case Element.Electro:
                await PowerCmd.Apply<ElectroAuraPower>(
                    choiceContext, target, Duration(applier),
                    applier: applier, cardSource: cardSource);
                break;
            case Element.Cryo:
                await PowerCmd.Apply<CryoAuraPower>(
                    choiceContext, target, Duration(applier),
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
            Duration(applier) - aura.Amount,
            applier: applier, cardSource: cardSource, silent: true);
    }
}
