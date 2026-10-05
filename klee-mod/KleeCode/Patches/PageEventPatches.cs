using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Patches;

/// <summary>
/// 2026-10-05, THE SEAT PAGE'S "SINCE LAST PAGE" LINE: two base-game moments
/// the after-state never shows, filed on <see cref="ResolutionLedger"/>.
///
/// AN ARTIFACT NEGATING A DEBUFF. The game asks every listener whether it
/// modifies a power about to land; Artifact answers by zeroing a visible
/// debuff on its owner, and only the modifiers that answered are then handed
/// <c>AfterModifyingPowerAmountReceived</c> with the power they changed
/// (0.111.0 decompile of <c>PowerCmd.Apply</c> / <c>ArtifactPower</c>). So
/// that override running IS the negation: the page then shows one less
/// Artifact and no debuff, and nothing saying which debuff it ate.
///
/// A STOLEN CARD GIVEN BACK. <c>SwipePower.BeforeDeath</c> puts the card
/// back in the deck and adds a card reward when its owner dies; the power's
/// row ("It holds your X") vanishes with the body and nothing says where the
/// card went.
///
/// PREFIXES THAT ONLY READ. Both return nothing and change nothing, and
/// every read is guarded: a log must never be the thing that ends a beat.
/// </summary>
[HarmonyPatch(typeof(ArtifactPower),
              nameof(ArtifactPower.AfterModifyingPowerAmountReceived))]
internal static class ArtifactPower_NegationEvent_Patch
{
    [HarmonyPrefix]
    public static void Prefix(ArtifactPower __instance, PowerModel power)
    {
        try
        {
            ResolutionLedger.NoteEvent(ResolutionLedger.Negated, string.Empty,
                                       __instance.Owner,
                                       power?.Title.GetFormattedText() ?? "");
        }
        catch (System.Exception)
        {
            // read-only log; nothing to undo
        }
    }
}

[HarmonyPatch(typeof(SwipePower), nameof(SwipePower.BeforeDeath))]
internal static class SwipePower_ReturnedEvent_Patch
{
    [HarmonyPrefix]
    public static void Prefix(SwipePower __instance, Creature target)
    {
        try
        {
            if (!ReferenceEquals(__instance.Owner, target)) return;
            var card = __instance.StolenCard;
            if (card?.DeckVersion == null) return;
            ResolutionLedger.NoteEvent(ResolutionLedger.Returned,
                                       card.Title?.ToString() ?? "",
                                       __instance.Owner, string.Empty);
        }
        catch (System.Exception)
        {
            // read-only log; nothing to undo
        }
    }
}
