using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
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
    /// One canonical, stateless instance for the whole session. AbstractModel's
    /// ctor derives an Id from the type and asserts uniqueness, so this must
    /// only ever be constructed once.
    /// </summary>
    private static readonly KleeElementalHooks Instance = new();

    /// <summary>The CombatHookSubscriptionDelegate KleeMod.Initialize registers.</summary>
    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        yield return Instance;
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
