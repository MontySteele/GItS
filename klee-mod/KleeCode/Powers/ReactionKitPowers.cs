using System.Collections.Generic;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// Reaction-archetype player powers (power-card pass). Reference
/// implementation tier0/engine/reactions.py. Numbers are LAW from tier0.
/// </summary>
public static class ReactionKitConstants
{
    /// <summary>tier0 constants.py CATALYTIC_BURST_PER_REACTION = 5.</summary>
    public const int CatalyticBurstPerReaction = 5;
}

/// <summary>
/// Catalytic Converter (renamed from "Catalytic Conversion" per R120,
/// 2026-08-06 -- separation from Sucrose's canon "Catalyst Conversion"; the
/// id and this class name are unchanged, a string pass only): every
/// Elemental Reaction additionally grants Amount
/// Sparks and Amount x 5 Burst Energy (sim: reactions.py _react, the
/// `reaction_bonus_spark_energy` block right after the flat +5). Read in the
/// <see cref="ReactionEffects.Resolve"/> funnel -- the same single funnel as
/// the base reaction grant, so it can neither miss a reaction nor
/// double-count one.
///
/// UPGRADE: {innate: true} (klee-upgrades.yaml, R37 2026-07-20) -- the card
/// starts in the opening hand; the per-reaction magnitude does NOT move,
/// because CATALYTIC_BURST_PER_REACTION is a constant rather than a card
/// field. catalytic_conversion LEFT tier0 upgrades.UNAPPLIABLE with that
/// ruling (the set is empty today), so the delta is sim-expressible and
/// measured. hot_hands settled the same way, at {retain: true} (playtest
/// 2026-07-22). Neither is "awaiting a ruling" any more; still do not
/// invent an upgrade game-side -- the sheet is the source of truth.
/// </summary>
public sealed class ReactionBonusSparkEnergyPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Catalytic Converter"),
        ("description",
            "[gold]Elemental Reactions[/gold] grant {Amount} extra "
          + "[gold]Spark[/gold]{Amount:plural:|s} and 5 extra "
          + "[gold]Burst Energy[/gold] per stack."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// Vermillion Pact: Amount is a PERCENT boost to amplifier multipliers
/// (Vaporize/Melt). Sim law (reactions.py _amp_mult): multiplicative on the
/// base -- `base * (1 + pct / 100)`. Read in
/// <see cref="KleeMod.Elements.ReactionTable"/>'s dealer-aware multiplier,
/// which also owns the 4x amp-cap detector the sheet note warns about.
/// </summary>
public sealed class AmpReactionUpPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Vermillion Pact"),
        ("description",
            "[gold]Vaporize[/gold] and [gold]Melt[/gold] amplify "
          + "{Amount}% more."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}
