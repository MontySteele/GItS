// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// A HAND CARD'S PRINTED NUMBER WAS THE LAST ONE THE GAME HAD DRAWN, NOT THE
// ONE IT WOULD PAY.
//
// THE FIND (seat round, 2026-10-10). Under Frail, Hold the Stage printed
// 18 Block on the page and gained 13. `SafeGetCardDescription` reads
// `CardModel.GetDescriptionForPile(PileType.Hand)`, and in the 0.111.0
// decompile that getter formats the dynamic vars' CURRENT `PreviewValue`; it
// never computes one. The only thing that computes one is
// `CardModel.UpdateDynamicVarPreview`, and the game calls it from
// `NCard.UpdateVisuals` -- i.e. when the card NODE redraws. So the page
// printed whatever the node last drew, which can predate the power that
// changed the number.
//
// WHAT THIS DOES. Exactly what `NCard.UpdateVisuals` does before it asks for
// the same description: clear the preview, recompute it with
// `CardPreviewMode.Normal` and NO target (the face a card shows in hand before
// anyone aims it), and the same again for the enchantment's vars.
//
// HOOKS ON, BY THE GAME'S OWN GATE. `UpdateDynamicVarPreview` runs the global
// hooks (Frail, Weak, Strength, Dexterity ...) when `CombatState != null` and
// the card is in the Hand or Play pile. A card in hand meets both, so no flag
// is needed -- and `ModalChoice.cs`'s door (`UpgradePreviewType = Combat`) is
// NOT used here: that is for an option in no pile, and its setter is one-way
// (the card can never leave the preview state), which a real hand card must
// never be put into.
//
// SAFE. Only in a live combat, only for a card whose pile is the Hand, and
// wrapped: a refresh that throws is swallowed and the description is read as
// before (at worst off the base values `ClearPreview` reset to). It writes
// display-only `PreviewValue`s the card node overwrites on its own next
// redraw, with the same answer.

using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;

namespace STS2_MCP;

public static partial class McpMod
{
    /// <summary>
    /// Recompute a hand card's dynamic-var previews against the board as it
    /// is now, as the game's card node does before it draws its text.
    /// </summary>
    private static void GitsRefreshHandPreview(CardModel card)
    {
        try
        {
            if (CombatManager.Instance is not { IsInProgress: true }) return;
            if (card.Pile?.Type != PileType.Hand) return;

            card.DynamicVars.ClearPreview();
            card.UpdateDynamicVarPreview(CardPreviewMode.Normal, null, card.DynamicVars);
            if (card.Enchantment != null)
            {
                card.Enchantment.DynamicVars.ClearPreview();
                card.UpdateDynamicVarPreview(CardPreviewMode.Normal, null,
                                             card.Enchantment.DynamicVars);
            }
        }
        catch
        {
            // A failed refresh is not a failed page.
        }
    }
}
