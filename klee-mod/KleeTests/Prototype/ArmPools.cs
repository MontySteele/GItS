using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-363`. THE THREE ARM OFFER POOLS, built headlessly from the rosters that
/// declare them rather than from a list kept here.
///
/// WHY IT IS READ OFF THE COMPILED ROSTER. A hand list in a test file is a
/// second copy of the pool and it goes stale the day a row lands -- which is
/// exactly the failure `tools/lint_arm_pool_parity.py` exists for one seam
/// over. These walk the `ModelDb.Card&lt;T&gt;()` calls in the roster methods
/// themselves, so a row added tomorrow is in tomorrow's matrix with nobody
/// remembering anything.
///
/// WHY THE CARDS ARE BUILT WITH `new` AND NOT FETCHED. `ModelDb` is populated
/// by the game's boot and every lookup throws in a test host (README.md, the
/// headless boundary) -- so the roster methods themselves cannot be CALLED.
/// What can be read is the TYPE ARGUMENT of each call, off the method's IL, and
/// a card model's rarity, type and cost are constructor arguments
/// (`CardModel(canonicalEnergyCost, type, rarity, targetType)`), so `new` gives
/// the same three facts the fetched model would have.
/// </summary>
internal static class ArmPools
{
    internal static readonly IReadOnlyList<string> Names = new[]
    {
        "klee-overhaul", "kokomi-overhaul", "furina-stage",
    };

    private static readonly Dictionary<string, IReadOnlyList<CardModel>> Cache = new();

    private static Assembly Mod => typeof(global::KleeMod.KleeMod).Assembly;

    internal static IReadOnlyList<CardModel> Offerable(string arm)
    {
        if (Cache.TryGetValue(arm, out var cached)) return cached;
        var built = Build(arm);
        Cache[arm] = built;
        return built;
    }

    private static IReadOnlyList<CardModel> Build(string arm) => arm switch
    {
        "klee-overhaul" => Instantiate(
            TypesFrom(Method("KleeMod.Powers.KleeOverhaulRoster", "Slice"))
                .Concat(TypesFrom(Getter("KleeMod.RosterAncientCards", "Klee")))),

        "kokomi-overhaul" => Instantiate(
            TypesFrom(Method("KleeMod.Powers.KokomiOverhaulRoster", "Slice"))
                .Concat(TypesFrom(Getter("KleeMod.RosterAncientCards", "Kokomi")))),

        // The Stage's pool is a LIST since legacy cleanup stage 4, as the
        // other two arms' are.
        "furina-stage" => Instantiate(
            TypesFrom(Method("KleeMod.Powers.FurinaStageRoster", "Pool"))
                .Concat(TypesFrom(Getter("KleeMod.RosterAncientCards", "Furina")))),

        _ => throw new InvalidOperationException($"no such arm: {arm}"),
    };

    // ---- Reading the roster ----------------------------------------------

    private static MethodBase Method(string type, string name) =>
        Mod.GetType(type, throwOnError: true)!.GetMethod(name, HeadlessGame.All)
        ?? throw new InvalidOperationException($"{type}.{name}() is gone");

    private static MethodBase Getter(string type, string name) =>
        Mod.GetType(type, throwOnError: true)!
           .GetProperty(name, HeadlessGame.All)?.GetGetMethod(nonPublic: true)
        ?? throw new InvalidOperationException($"{type}.{name} getter is gone");

    /// <summary>
    /// The type argument of every `ModelDb.Card&lt;T&gt;()` call in the body,
    /// in order and with duplicates kept.
    ///
    /// The byte scan and its false-positive caveat are `Harness/Il.cs`'s, and
    /// the caveat is weaker here than it is there: a stray byte would have to
    /// resolve to a generic method whose single type argument is a
    /// `CardModel`, and the assertions built on this are all "this pool holds
    /// enough cards", which a spurious EXTRA card could in principle satisfy --
    /// so the ledger test above asserts the short-cell SET rather than a
    /// threshold, and a phantom row would move that set and go red.
    /// </summary>
    private static List<Type> TypesFrom(MethodBase method)
    {
        var found = new List<Type>();
        var il = method.GetMethodBody()?.GetILAsByteArray();
        if (il == null) return found;

        for (var i = 0; i < il.Length - 4; i++)
        {
            if (il[i] != 0x28 && il[i] != 0x6F) continue; // call, callvirt
            try
            {
                var target = method.Module.ResolveMethod(
                    BitConverter.ToInt32(il, i + 1),
                    method.DeclaringType?.GetGenericArguments(),
                    null);
                if (target is not { IsGenericMethod: true }) continue;
                if (target.Name != "Card") continue;
                var args = target.GetGenericArguments();
                if (args.Length == 1 && typeof(CardModel).IsAssignableFrom(args[0]))
                {
                    found.Add(args[0]);
                }
            }
            catch
            {
                // Not a method token. Expected while byte-scanning.
            }
        }

        return found;
    }

    /// <summary>The cards one roster method names, built headlessly, in
    /// order and with duplicates kept -- what <c>PoolCountTests</c> counts.</summary>
    internal static IReadOnlyList<CardModel> Named(string type, string method) =>
        TypesFrom(Method(type, method))
            .Select(t => (CardModel)Activator.CreateInstance(t)!)
            .ToList();

    /// <summary>The same for a property getter (<c>RosterAncientCards</c>).</summary>
    internal static IReadOnlyList<CardModel> NamedByGetter(string type, string property) =>
        TypesFrom(Getter(type, property))
            .Select(t => (CardModel)Activator.CreateInstance(t)!)
            .ToList();

    private static IReadOnlyList<CardModel> Instantiate(IEnumerable<Type> types) =>
        types.Distinct()
             .Select(t => (CardModel)Activator.CreateInstance(t)!)
             .ToList();
}

/// <summary>
/// `EB-363`'s widening ladder, reached the way this project reaches every mod
/// internal: by reflection, because the mod carries no <c>InternalsVisibleTo</c>
/// and one pin is not a reason to add one (the standing call, recorded in
/// `SelfCheckBbcodeTests`).
///
/// The method behind this is the ladder and NOTHING else -- no options object,
/// no <c>Player</c>, no pool -- precisely so it can be pinned for real here
/// rather than structurally. The plumbing around it is pinned structurally, and
/// said to be.
/// </summary>
internal static class Seam
{
    private static readonly MethodInfo Widen =
        typeof(global::KleeMod.KleeMod).Assembly
            .GetType("KleeMod.CardFactory_CreateForReward_Clamp_Patch",
                     throwOnError: true)!
            .GetMethod("WidenedAdmissions", HeadlessGame.All)
        ?? throw new InvalidOperationException(
            "CardFactory_CreateForReward_Clamp_Patch.WidenedAdmissions is gone -- "
            + "EB-363's seam has moved and this ledger needs re-pointing.");

    internal static List<CardModel>? WidenedAdmissions(
        int wanted, IReadOnlyList<CardModel> cell, IReadOnlyList<CardModel> whole) =>
        (List<CardModel>?)Widen.Invoke(null, new object[] { wanted, cell, whole });
}
