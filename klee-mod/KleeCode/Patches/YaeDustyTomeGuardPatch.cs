using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Events;
using MegaCrit.Sts2.Core.Models.Relics;

namespace KleeMod.Patches;

/// <summary>
/// THE DARV DOOR FOR A KIT WITH NO ANCIENT YET (Yae Miko, batch one).
///
/// THE SOFTLOCK (<c>tools/lint_ancient_coverage.py</c>, 2026-07-23): Darv
/// offers Dusty Tome half the time, and <c>DustyTome.SetupForPlayer</c>
/// draws a random Ancient card from the character's pool (0.111.0
/// decompile: <c>NextItem(...).Id</c>), so an empty draw throws inside
/// <c>Darv.GenerateInitialOptions</c> and the event never builds its
/// buttons. Yae's two Ancients are the paper's next batch ("Not in this
/// batch, said so"), so her pool holds none.
///
/// THE ANSWER IS SCOPED AND TEMPORARY: for a Yae player whose pool holds no
/// Tome-eligible Ancient, the Tome is set up with no card (the prefix skips
/// the draw) and Darv offers his two relics without it. Every other player
/// is untouched, and the guard goes inert the day her Ancients land (the
/// pool then holds one). Darv's own rolls are made exactly as before.
/// </summary>
internal static class YaeDustyTomeGuard
{
    /// <summary>Does this player's Tome have nothing to draw? Only ever true
    /// for Yae.</summary>
    internal static bool TomeIsEmpty(Player? player)
    {
        if (player?.Character is not IYaeCharacter) return false;
        try
        {
            return !player.Character.CardPool
                .GetUnlockedCards(player.UnlockState, player.RunState.CardMultiplayerConstraint)
                .Any(c => c.Rarity == CardRarity.Ancient
                          && !ArchaicTooth.TranscendenceCards.Contains(c));
        }
        catch (System.Exception)
        {
            return false;
        }
    }
}

[HarmonyPatch(typeof(DustyTome), nameof(DustyTome.SetupForPlayer))]
internal static class DustyTome_SetupForPlayer_YaeGuard_Patch
{
    [HarmonyPrefix]
    [HarmonyPriority(Priority.First)]
    public static bool Prefix(Player player) => !YaeDustyTomeGuard.TomeIsEmpty(player);
}

[HarmonyPatch(typeof(Darv), "GenerateInitialOptions")]
internal static class Darv_GenerateInitialOptions_YaeGuard_Patch
{
    [HarmonyPostfix]
    public static void Postfix(Darv __instance, ref IReadOnlyList<EventOption> __result)
    {
        if (!YaeDustyTomeGuard.TomeIsEmpty(__instance.Owner)) return;
        __result = __result
            .Where(o => o.Relic is not DustyTome { AncientCard: null })
            .ToList();
    }
}
