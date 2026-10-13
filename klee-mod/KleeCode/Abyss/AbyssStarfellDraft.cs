using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Abyss;

/// <summary>
/// STARFELL DRAFT (<c>review/ruled/abyss-pools-2-2026-10-12.md</c>, whole
/// run): "Card rewards show 1 additional card."
///
/// THE SEAM. Every card reward the game rolls -- a combat's, an event's, a
/// relic's -- draws its cards through <c>CardFactory.CreateForReward(player,
/// cardCount, options)</c> with <c>CardCreationFlags.IsCardReward</c> set
/// (<c>CardReward</c>'s constructor adds it), and the base game has no
/// "how many cards" hook. So the count is raised here, in a prefix that runs
/// AHEAD of the mod's reward clamp (<c>CardFactory_CreateForReward_Clamp_Patch</c>,
/// default priority), so a pool too small for the larger draw is still
/// clamped rather than thrown on. A draw without the flag (a transform, a
/// Neow pack) is left alone.
///
/// RELOAD-STABLE. The reward keeps the count it was built with; a reward
/// rolled again on a reload passes this prefix again and draws the same
/// number. In co-op each player's reward is rolled by the same code on every
/// machine.
///
/// Gated by presence: outside an Abyss run, or before the Blessing is taken,
/// the count is untouched.
/// </summary>
[HarmonyPatch(typeof(CardFactory), nameof(CardFactory.CreateForReward),
    new[] { typeof(Player), typeof(int), typeof(CardCreationOptions) })]
[HarmonyPriority(Priority.High)]
internal static class CardFactory_CreateForReward_StarfellDraft_Patch
{
    [HarmonyPrefix]
    public static void Prefix(Player player, ref int cardCount, CardCreationOptions options)
    {
        var abyss = SpiralAbyss.In(player?.RunState);
        if (abyss == null || !abyss.Has(AbyssBlessing.StarfellDraft)) return;
        cardCount = AbyssRules.StarfellDraftCount(
            cardCount, options.Flags.HasFlag(CardCreationFlags.IsCardReward));
    }
}
