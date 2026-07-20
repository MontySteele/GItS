using System.Collections.Generic;
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
    /// AMPLIFIER ONLY. Vaporize/Melt multiply the hit that triggers them, so
    /// they must land here in the multiplicative phase -- after Strength (which
    /// is additive) and alongside Vulnerable. Because that phase is a plain
    /// product accumulation, this commutes with Vulnerable regardless of
    /// listener order, giving (base + Strength) * vuln * amp.
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
        var mult = ReactionTable.AmplifierMultiplier(reaction);

        if (mult > ReactionConstants.AmpStackLimit)
        {
            Log.Warn($"[{KleeMod.ModId}] AMP_STACK guard: multiplier {mult} exceeds " +
                     $"{ReactionConstants.AmpStackLimit} on {reaction} " +
                     $"({Element} aura x {trigger} trigger).");
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
    /// Auras persist AURA_DURATION_TURNS unconsumed, then expire. Mirrors
    /// VulnerablePower's duration tick.
    /// </summary>
    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side, System.Collections.Generic.IEnumerable<Creature> participants)
    {
        if (side == CombatSide.Enemy)
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
