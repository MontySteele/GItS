using System;
using System.Collections.Generic;
using HarmonyLib;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Screens.CardLibrary;

namespace KleeMod.Patches;

/// <summary>
/// THE CARD LIBRARY'S COLORLESS TAB SHOWS THE SHARED COMPANIONS.
///
/// <c>NCardLibrary._Ready</c> (0.111.0 decompile) keys each pool tab to a
/// predicate in <c>_poolFilters</c>, and the Colorless tab's is the type test
/// <c>c.Pool is ColorlessCardPool</c>. The shared companions sit in
/// <see cref="CompanionCardPool"/>, which no tab names, so they showed only
/// with every tab off. Shared cards sit under Colorless in the base game, so
/// this postfix widens that one predicate by the companion pool and changes
/// nothing else: the base characters' tabs, Ancients and Misc keep their
/// predicates, and BaseLib's character tabs test their own pool's
/// <c>AllCardIds</c>, so Klee's tab holds only Klee's pool (her three kit-own
/// companions included, the shared ones not).
/// </summary>
public static class CompanionLibraryFilter
{
    /// <summary>The base predicate, or a card of the companion pool.
    /// PURE given <paramref name="isCompanionPool"/>.</summary>
    public static Func<CardModel, bool> Widen(
        Func<CardModel, bool> basePredicate, Func<CardModel, bool> isCompanionPool) =>
        c => basePredicate(c) || isCompanionPool(c);

    /// <summary>Does <paramref name="card"/> belong to the shared companions'
    /// pool? The same type test the base tab makes of its own pool.</summary>
    public static bool InCompanionPool(CardModel card) => card.Pool is CompanionCardPool;
}

[HarmonyPatch(typeof(NCardLibrary), "_Ready")]
internal static class NCardLibrary_CompanionLibraryFilter_Patch
{
    [HarmonyPostfix]
    private static void Postfix(
        Dictionary<NCardPoolFilter, Func<CardModel, bool>> ____poolFilters,
        NCardPoolFilter ____colorlessFilter)
    {
        if (____poolFilters == null || ____colorlessFilter == null) return;
        if (!____poolFilters.TryGetValue(____colorlessFilter, out var colorless)) return;
        ____poolFilters[____colorlessFilter] = CompanionLibraryFilter.Widen(
            colorless, CompanionLibraryFilter.InCompanionPool);
    }
}
