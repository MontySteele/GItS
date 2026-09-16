using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Hooks;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// `EB-787`. A CARD'S PRINTED BLOCK THAT IS PAID WITHOUT A CARD SOURCE: it
/// folds everything the payout folds, and nothing the payout does not --
/// which means Frail, Dexterity and No Block, but NOT the card's enchantment.
///
/// THE FIND (live-looks-8c, #575). A <c>Nimble</c> on <i>Barbara - Front Row
/// Seat</i> moved BOTH of the card's numbers: the printed Block 5 to 7, which
/// is right, and the rider "whenever a Bomb goes off this turn, gain 3 Block"
/// to 5, which is a number the card never gains. The rider was a plain
/// <c>BlockVar</c>, declared that way under `EB-513` so that the FACE takes
/// the same Frail fold the payout takes -- and the game's own
/// <c>BlockVar.UpdateCardPreview</c> reads <c>card.Enchantment</c> directly,
/// so one declaration bought both folds at once.
///
/// WHY THE PAYOUT DOES NOT TAKE THE ENCHANTMENT, and why that is correct
/// rather than the other half of the defect. The rider is paid by a power:
///
///     await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Move, null);
///
/// The trailing <c>null</c> is the <c>CardPlay</c>, and <c>GainBlock</c> hands
/// <c>cardPlay?.Card</c> to <c>Hook.ModifyBlock</c> as the card source. An
/// enchantment is read off that source (<c>if (cardSource != null &amp;&amp;
/// cardSource.Enchantment != null)</c>), so a sourceless gain never consults
/// one -- the same reason the base game's <c>Prolong</c> and this repo's
/// <c>block_next_turn</c> note give, and the reason tier0's
/// <c>companion_standins._pay_block</c> never adds <c>card.enchant_block</c>.
/// The sim and the mod's payout have always agreed; only the mod's FACE lied.
///
/// SO THE PREVIEW MAKES THE PAYOUT'S OWN CALL. Rather than subtracting the
/// enchantment back out -- which would restate <c>EnchantBlockAdditive</c> and
/// <c>EnchantBlockMultiplicative</c> here and go stale the day a third
/// enchantment does something else to Block -- this var runs
/// <c>Hook.ModifyBlock</c> with the SAME arguments the payout passes:
/// <c>cardSource: null</c>, <c>cardPlay: null</c>. Every listener therefore
/// answers the preview exactly as it will answer the gain. Frail and
/// Dexterity bite (they read <c>props</c> and the target, never the source);
/// Pael's Legion, Vambrace, Vitruvian Minion and No Block stand down on a
/// null source, and they stand down at the payout too.
///
/// <c>EnchantedValue</c> IS LEFT AT THE BASE, which is what makes the face
/// print honestly for the right reason: <c>DynamicVar.ToHighlightedString</c>
/// colours the number by comparing the preview against it, so an enchanted
/// card shows this rider unchanged and unmarked, exactly as an unenchanted one
/// does.
///
/// IT STILL SUBCLASSES <c>BlockVar</c> AND THAT IS DELIBERATE
/// (<see cref="FoldedBlockVar"/>'s own note): <c>DynamicVarSet</c> casts, and
/// BaseLib's <c>GainsBlock</c> auto-detect counts a <c>BlockVar</c> -- so
/// Nimble ELIGIBILITY is exactly what it was before this class existed, in
/// both engines and under `tools/lint_enchant_parity.py`. This row moved one
/// printed number and no rule.
///
/// QUARANTINED, in this directory and by this file's csproj rule.
/// </summary>
public sealed class UnsourcedBlockVar : BlockVar
{
    public UnsourcedBlockVar(string name, decimal amount, ValueProp props)
        : base(name, amount, props)
    {
    }

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        // NOT `base.UpdateCardPreview` first: the base class writes the
        // enchanted number into BOTH EnchantedValue and PreviewValue, and the
        // whole point here is that neither ever carries it.
        var num = BaseValue;
        if (runGlobalHooks && card.CombatState != null
                && card.Owner?.Creature != null)
        {
            // The two nulls are the whole fix: they are the card source and
            // the card play, and they are null in the payout's own call.
            num = Hook.ModifyBlock(
                card.CombatState, card.Owner.Creature, BaseValue, Props,
                null, null, out IEnumerable<AbstractModel> _);
        }
        EnchantedValue = BaseValue;
        PreviewValue = num;
    }
}
