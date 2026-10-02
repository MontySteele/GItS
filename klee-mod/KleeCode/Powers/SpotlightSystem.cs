using System;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// The printed-number fold the card generator wraps a companion's and
/// Furina's damage and Block in. The Spotlight it folded (Center Stage and
/// Guest Cast, the Ethereal Spotlight, its powers and its resources) went
/// with the shipped kits (legacy cleanup stage 5), so every fold is the
/// identity; the generated cards still call through here, and the codegen's
/// spotlight wrap is a stage 6 item.
/// </summary>
public static class SpotlightSystem
{
    /// <summary>
    /// The deferred Block clause's own var (`EB-438`). <c>IntValue</c> stays
    /// <c>BaseValue</c>, so the play's own <see cref="PrintedBlock"/> wrap
    /// applies the fold exactly once.
    /// </summary>
    public sealed class DeferredBlockVar : DynamicVar
    {
        public const string Token = "BlockNextTurn";

        public DeferredBlockVar(decimal amount) : base(Token, amount)
        {
        }

        public override void UpdateCardPreview(
            CardModel card, CardPreviewMode previewMode, Creature? target,
            bool runGlobalHooks)
        {
            PreviewValue = BaseValue;
            if (!runGlobalHooks) return;
            // A canonical (compendium) copy has no owner and the getter
            // ASSERTS rather than returning null.
            if (!card.IsMutable) return;
            if (card.Owner?.Creature == null) return;
            PreviewValue = PrintedBlock(card, BaseValue);
        }
    }

    /// <summary>
    /// `EB-486`: the immediate Block clause of a card whose damage already
    /// claims <c>CalculationBase</c>. It subclasses <c>BlockVar</c> because
    /// <c>DynamicVarSet.Block</c> casts to it.
    /// </summary>
    public sealed class SpotlitBlockVar : BlockVar
    {
        public const string Token = "Block";

        public SpotlitBlockVar(decimal amount)
            : base(amount, ValueProp.Move)
        {
        }

        public override void UpdateCardPreview(
            CardModel card, CardPreviewMode previewMode, Creature? target,
            bool runGlobalHooks)
        {
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            if (!runGlobalHooks) return;
            if (!card.IsMutable) return;
            if (card.Owner?.Creature == null) return;
            var folded = new BlockVar(
                PrintedBlock(card, BaseValue), ValueProp.Move);
            folded.UpdateCardPreview(
                card, previewMode, target, runGlobalHooks);
            PreviewValue = folded.PreviewValue;
        }
    }

    public static decimal PrintedDamage(CardModel card, decimal amount) =>
        Math.Truncate(amount);

    public static decimal PrintedDamageDelta(CardModel card)
    {
        var printed = card.DynamicVars.CalculationBase.BaseValue;
        return PrintedDamage(card, printed) - printed;
    }

    public static decimal PrintedBlockDelta(CardModel card)
    {
        var printed = card.DynamicVars.CalculationBase.BaseValue;
        return PrintedBlock(card, printed) - printed;
    }

    public static decimal PrintedBlock(CardModel card, decimal amount) =>
        Math.Truncate(amount);
}
