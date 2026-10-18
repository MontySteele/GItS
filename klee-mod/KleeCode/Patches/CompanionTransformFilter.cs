using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Patches;

/// <summary>
/// A TRANSFORM OFFERS ONLY THE COMPANIONS THIS PLAYER COULD BE OFFERED.
///
/// The base game draws a transform's replacement from the ORIGINAL card's
/// pool (<c>CardFactory.GetDefaultTransformationOptions</c>, 0.111.0
/// decompile). A shared companion's pool is <see cref="CompanionCardPool"/>,
/// whose unlocked set is the whole roster, <see cref="CompanionPool.All"/>:
/// so transforming a companion in Yae's deck could hand her "Yae Miko --
/// Sesshou Sakura", which <see cref="CompanionPool.IsHiddenFrom"/> keeps out
/// of every offer she sees, and could hand anyone another character's
/// personal-pool companion. This postfix runs the same offer rule the reward
/// slot and the shop use (<see cref="CompanionPool.IsOfferable"/>) over the
/// companions among the options. Non-companion options are never touched, and
/// a filter that would leave nothing keeps the base answer (the base method
/// throws on an empty set, and an empty set is not a reachable roster).
///
/// A POSTFIX, so it also filters what <c>ArmTransformPool</c>'s prefix
/// answers; that answer is a character's own pool, and a kit-own companion in
/// it is offerable to its own character by construction. Pandora's Box, Kill
/// with Fire and the transform preview all reach this one method.
/// </summary>
public static class CompanionTransformFilter
{
    /// <summary>The options with every companion <paramref name="owner"/>
    /// could not be offered removed, or the options unchanged when nothing is
    /// removed or nothing would be left. PURE.</summary>
    public static IEnumerable<CardModel> Filter(
        IEnumerable<CardModel> options, Player owner)
    {
        var all = options as IReadOnlyCollection<CardModel> ?? options.ToArray();
        var kept = all
            .Where(c => c is not ICompanionCard || CompanionPool.IsOfferable(c, owner))
            .ToArray();
        return kept.Length == 0 || kept.Length == all.Count ? all : kept;
    }
}

[HarmonyPatch(typeof(CardFactory), nameof(CardFactory.GetDefaultTransformationOptions))]
internal static class CardFactory_CompanionTransformFilter_Patch
{
    [HarmonyPostfix]
    private static void Postfix(CardModel original, ref IEnumerable<CardModel> __result)
    {
        // IsMutable first: a canonical card's Owner asserts.
        if (__result == null || !original.IsMutable) return;
        var owner = original.Owner;
        if (owner == null) return;
        __result = CompanionTransformFilter.Filter(__result, owner);
    }
}
