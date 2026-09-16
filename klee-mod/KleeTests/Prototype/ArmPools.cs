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

        // The Stage is a SUBSTITUTION on top of the whole shipped sheet, not a
        // replacement, so its pool is the shipped roster with fourteen rows
        // lifted out and fourteen `proto_fs_` rows put in their place -- and
        // then `DropRetiredRows`, which is the arm's own TEXT filter and drops
        // any remaining shipped row that still prints a word the brief retired.
        // That last step is run for real here: it is a pure predicate over a
        // card's printed text and needs no registration.
        "furina-stage" => FurinaStageRows(),

        _ => throw new InvalidOperationException($"no such arm: {arm}"),
    };

    private static IReadOnlyList<CardModel> FurinaStageRows()
    {
        var swap = Method("KleeMod.Powers.FurinaStageRoster", "SwapOfferedRows");
        var dropped = TestedTypes(swap).ToHashSet();
        var added = TypesFrom(swap);

        var shipped = TypesFrom(
                Getter("KleeMod.Cards.Furina.Generated.FurinaCardRoster", "All"))
            .Concat(TypesFrom(Getter("KleeMod.RosterAncientCards", "Furina")))
            .Where(t => !dropped.Contains(t));

        var rows = Instantiate(shipped.Concat(added));

        // The arm's own filter, run rather than reimplemented. It is public
        // for exactly this reason and `FurinaStageRoundTwoTests` already calls
        // it headlessly.
        var drop = Mod
            .GetType("KleeMod.Powers.FurinaStageRoster", throwOnError: true)!
            .GetMethod("DropRetiredRows", HeadlessGame.All)!;

        return ((IEnumerable<CardModel>)drop.Invoke(null, new object?[] { rows })!)
            .ToList();
    }

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

    /// <summary>
    /// Every type named by an `isinst` in the body -- which is how a
    /// `card is not FurinaGen.TakeYourBow` chain compiles, and therefore the
    /// only way to read the Stage's fourteen lifted rows off the seam that
    /// lifts them.
    /// </summary>
    private static List<Type> TestedTypes(MethodBase method)
    {
        var found = new List<Type>();
        var il = method.GetMethodBody()?.GetILAsByteArray();
        if (il == null) return found;

        foreach (var body in Lambdas(method, method.Name).Prepend(method))
        {
            var bytes = body.GetMethodBody()?.GetILAsByteArray();
            if (bytes == null) continue;
            for (var i = 0; i < bytes.Length - 4; i++)
            {
                if (bytes[i] != 0x75) continue; // isinst
                try
                {
                    var t = body.Module.ResolveType(BitConverter.ToInt32(bytes, i + 1));
                    if (typeof(CardModel).IsAssignableFrom(t)) found.Add(t);
                }
                catch
                {
                    // Not a type token. Expected while byte-scanning.
                }
            }
        }

        return found;
    }

    /// <summary>
    /// The compiler moves a `.Where(card =&gt; ...)` body out of the method
    /// entirely, onto a `&lt;&gt;c` display class nested in the declaring type.
    /// `Harness/Il.cs` walks these for the same reason: a pin that stops seeing
    /// a call the moment it is wrapped in a lambda passes for the wrong reason.
    /// </summary>
    private static IEnumerable<MethodBase> Lambdas(MethodBase method, string owner) =>
        method.DeclaringType?
            .GetNestedTypes(HeadlessGame.All)
            .Where(t => t.Name.StartsWith("<>c", StringComparison.Ordinal))
            .SelectMany(t => t.GetMethods(HeadlessGame.All))
            // `<SwapOfferedRows>b__7_0` -- Roslyn spells a lambda with the
            // method it came from, so a sibling method's lambdas stay out.
            .Where(m => m.Name.StartsWith($"<{owner}>", StringComparison.Ordinal))
            .Cast<MethodBase>()
        ?? Enumerable.Empty<MethodBase>();

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
