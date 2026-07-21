using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// An elemental aura clinging to an enemy. One aura per enemy; a same-element
/// hit refreshes it, a different-element hit consumes it and triggers a
/// reaction.
///
/// ARCHITECTURE (spike S1): this is a self-managing enemy-side power, which the
/// spec framed as the "fallback" but which turns out to be exactly how MegaCrit
/// ships VulnerablePower -- a power owned by the target that scales incoming
/// damage, guarded by <c>target != Owner</c>. No Harmony patching is involved.
/// Binding to these AbstractModel virtuals also dodges the version-drift trap
/// that forced Downfall to write a two-signature reflective shim for
/// Hook.ModifyDamage.
///
/// This is a direct port of resolve_hit() in tier0/engine/reactions.py, which
/// is the ratified behavior.
/// </summary>
public abstract class AuraPower : PowerModel, ILocalizationProvider
{
    /// <summary>Which element this aura is.</summary>
    public abstract Element Element { get; }

    /// <summary>
    /// BaseLib's AddModelLoc keys off Id.Entry for any model implementing this
    /// interface (see BombPower.Localization). Declared once here, specialized
    /// per element -- BaseLib reads it off each concrete canonical, so every
    /// subclass gets its own PYRO/HYDRO/... entry. Playtest 2026-07-20: these
    /// powers shipped without loc and tooltips rendered the raw keys; self-check
    /// R8 now sweeps every mod power for exactly this.
    /// </summary>
    public List<(string, string)>? Localization => new()
    {
        ("title", $"{Element} Aura"),
        ("description",
            $"{Element} clings to this enemy. A hit of a different element consumes "
          + "the aura and triggers an [gold]Elemental Reaction[/gold]; "
          + $"a {Element} hit refreshes its duration."),
        // Smart (in-combat) tooltip adds the live duration; {Amount} is the
        // turns remaining, same var the badge shows.
        ("smartDescription",
            $"{Element} clings to this enemy for {{Amount}} more turn{{Amount:plural:|s}}. "
          + "A hit of a different element consumes the aura and triggers an "
          + $"[gold]Elemental Reaction[/gold]; a {Element} hit refreshes its duration."),
    };

    public override PowerType Type => PowerType.Debuff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// Reads the element off the incoming card. Returns None for untagged
    /// damage, which never reacts.
    /// </summary>
    protected static Element ElementOf(CardModel? cardSource) =>
        cardSource is IElementalCard elemental ? elemental.Element : Element.None;

    /// <summary>
    /// The multiplicative phase of the triggering hit. Vaporize/Melt multiply
    /// the hit that triggers them, so they must land here -- after Strength
    /// (which is additive) and alongside Vulnerable. Because that phase is a
    /// plain product accumulation, this commutes with Vulnerable regardless of
    /// listener order, giving (base + Strength) * vuln * amp.
    ///
    /// SUPERCONDUCT (bug hunt 2026-07-21): the sim applies Superconduct's
    /// Vulnerable INSIDE resolve_hit (reactions.py _react) and only then runs
    /// modify_damage_taken, so the triggering hit is itself x1.5. The C# power
    /// cannot be applied that early -- by the time any hook can apply it the
    /// damage number is already final -- so the triggering hit's share is
    /// mirrored here, in the same multiplicative phase the sim uses, and
    /// ReactionEffects still applies the real VulnerablePower for later hits.
    /// Shipped without this, a card-triggered Superconduct dealt 10 where the
    /// sim dealt 15, while the SAME reaction off a bomb correctly dealt 15
    /// (ElementalHit resolves the reaction before its TargetMods) -- one
    /// reaction, two payouts.
    ///
    /// The already-Vulnerable guard is what keeps that faithful: the sim's
    /// modify_damage_taken is a flat x1.5 on any nonzero vulnerable stack, not
    /// per stack, so when the target is already Vulnerable the native pipeline
    /// has applied the 1.5 and adding it again would double-count.
    ///
    /// This runs in preview/tooltip paths too, so it MUST stay pure -- no aura
    /// consumption, no side effects. Consumption happens in AfterDamageReceived.
    /// </summary>
    public override decimal ModifyDamageMultiplicative(
        Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (target != base.Owner) return 1m;
        if (!props.IsPoweredAttack()) return 1m;

        var trigger = ElementOf(cardSource);
        if (trigger == Element.None) return 1m;

        var reaction = ReactionTable.Lookup(Element, trigger);

        // Dealer-aware: Vermillion Pact's percent boost rides the multiplier
        // (sim _amp_mult). The amp-cap detector lives inside the overload.
        var mult = ReactionTable.AmplifierMultiplier(reaction, dealer);

        if (reaction == Reaction.Superconduct
            && !target.Powers.OfType<VulnerablePower>().Any())
        {
            mult *= ReactionConstants.VulnerableTakenMult;
        }

        return mult;
    }

    /// <summary>
    /// Aura lifecycle + reaction side effects. Runs once per hit after the
    /// damage resolves, which is where the sim consumes the aura.
    /// </summary>
    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, DamageResult result,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (target != base.Owner) return;
        if (!props.IsPoweredAttack()) return;

        var trigger = ElementOf(cardSource);
        if (trigger == Element.None) return;

        if (trigger == Element)
        {
            // Same element refreshes duration rather than reacting.
            await PowerCmd.ModifyAmount(
                choiceContext, this,
                ReactionConstants.AuraDurationTurns - Amount,
                applier: dealer, cardSource: cardSource, silent: true);
            return;
        }

        var reaction = ReactionTable.Lookup(Element, trigger);
        if (reaction == Reaction.None) return;

        // Consume the aura BEFORE resolving effects: Swirl re-applies this
        // element to other enemies and must not immediately re-trigger here.
        var consumedElement = Element;
        await PowerCmd.Remove(this);

        await ReactionEffects.Resolve(
            choiceContext, reaction, target, dealer, cardSource, consumedElement);
    }

    /// <summary>
    /// Auras persist AURA_DURATION_TURNS unconsumed, then expire.
    ///
    /// PHASE CORRECTION (bug hunt 2026-07-21). This ticked in
    /// AfterSideTurnEnd(Enemy) -- the phase immediately BEFORE
    /// BombPower.BeforeSideTurnStart(Player). tier0's player turn is ordered
    /// "bombs detonate -> auras tick" (combat.py: detonate every bombed enemy,
    /// then reactions.tick_auras), which is also what BombPower's own doc
    /// claims the contract is, so the mod had it exactly backwards: an aura on
    /// its last turn expired before the start-of-turn detonation could react
    /// with it. A Hydro aura + a bomb lost its Vaporize -- no x1.5, no +5 Burst
    /// -- and the detonation then left a fresh Pyro aura the sim never creates.
    ///
    /// AfterSideTurnStart is the right slot and needs no ordering assumption
    /// between two enemy-owned powers: CombatManager awaits
    /// Hook.BeforeSideTurnStart (where bombs detonate) to completion, then
    /// AfterBlockCleared, then Hook.AfterSideTurnStart -- all strictly before
    /// energy reset and the hand draw. Separate broadcasts, guaranteed order.
    /// </summary>
    public override async Task AfterSideTurnStart(
        CombatSide side, IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side == CombatSide.Player)
        {
            await PowerCmd.TickDownDuration(this);
        }
    }
}

public sealed class PyroAuraPower : AuraPower
{
    public override Element Element => Element.Pyro;
}

public sealed class HydroAuraPower : AuraPower
{
    public override Element Element => Element.Hydro;
}

public sealed class ElectroAuraPower : AuraPower
{
    public override Element Element => Element.Electro;
}

public sealed class CryoAuraPower : AuraPower
{
    public override Element Element => Element.Cryo;
}
