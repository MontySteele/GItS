using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using MegaCrit.Sts2.Core.Logging;

namespace KleeMod;

/// <summary>
/// F2 — the Harmony bootstrap, patching PER TYPE.
///
/// WHAT THIS REPLACES. `harmony.PatchAll(assembly)` is one call in one
/// try/catch. Harmony walks the assembly's types in reflection order and
/// applies each patch class in turn, so the FIRST one that throws aborts the
/// walk — and every patch class after it is never applied. The catch logged a
/// single line ("Harmony patching failed: ...") and initialization carried on.
///
/// That is the worst available shape for this mod specifically, because two of
/// our patches are softlock guards: `CardFactory_CreateForMerchant_TypeFallback`
/// (finding 24 — entering ANY shop black-screens the run) and
/// `CardFactory_CreateForReward_Clamp` (finding 22). Reflection order is not
/// source order and is not stable across builds, so an unrelated dead lookup in
/// some cosmetic VFX patch could silently disarm the shop guard, and the only
/// evidence would be one log line that named the VFX patch. The run would then
/// die in a shop, hours later, for a reason nothing pointed at.
///
/// The fix is not cleverness, it is granularity: each patch class gets its own
/// CreateClassProcessor call inside its own try/catch. One dead lookup disarms
/// ONE patch, names itself at boot, and leaves every other patch armed.
///
/// LOUD MEANS LOUD. A failure prints a banner, one line per failed class, and
/// the consequence — not a line that scrolls past between two INFO lines. If a
/// softlock guard is among the casualties it says so in those words, because
/// the operator reading godot.log after a black screen is the person this text
/// is for. (Playtest practice here is to read godot.log first; see the
/// crash-log discipline.)
///
/// DEGRADED IS NOT FAILED. A class whose TargetMethods resolves 20 of 22
/// getters armed 20 real patches; that is a WARN naming the two misses, not an
/// ERROR. A class that armed ZERO methods is a failure even though nothing
/// threw — silently patching nothing is exactly the outcome F2 exists to stop.
/// </summary>
internal static class KleePatchBootstrap
{
    /// <summary>
    /// Patch classes whose absence loses the run rather than a visual flourish.
    /// Named here so the boot report can escalate instead of leaving an
    /// operator to work out which of a list of type names is the dangerous one.
    ///
    /// EVERY ENTRY IS `nameof`, never a string literal. A literal here would
    /// survive the deletion or rename of the class it guards and quietly guard
    /// nothing -- an exemption outliving its reason, which is the B6 ledger
    /// lesson. `nameof` makes that a compile error instead.
    /// </summary>
    private static readonly HashSet<string> SoftlockGuards = new(StringComparer.Ordinal)
    {
        nameof(CardFactory_CreateForReward_Clamp_Patch),
        nameof(CardFactory_CreateForMerchant_TypeFallback_Patch),
        nameof(ProgressSaveManager_EpochCheck_Patch),
        nameof(Patches.MerchantInventory_CompanionColorlessSlots_Patch),
    };

    /// <summary>
    /// Reflection misses recorded by the Resolve* helpers below. Appended to
    /// during a class's Patch() call — TargetMethods runs inside it — so
    /// ApplyAll can attribute each miss to the class that caused it by taking
    /// a count before and after.
    /// </summary>
    private static readonly List<string> Misses = new();

    /// <summary>
    /// `AccessTools.Method` returns null for a lookup that no longer resolves,
    /// and a null in a TargetMethods sequence makes Harmony throw with a
    /// message about a null element rather than about the name that died.
    /// Route lookups through here: the miss is recorded with the name in it,
    /// and the caller filters the null out.
    /// </summary>
    internal static MethodBase? ResolveMethod(Type type, string name)
    {
        var method = AccessTools.Method(type, name);
        if (method == null)
        {
            Misses.Add($"{type.Name}.{name}() did not resolve");
        }

        return method;
    }

    /// <summary>Property-getter twin of <see cref="ResolveMethod"/>.</summary>
    internal static MethodBase? ResolvePropertyGetter(Type type, string name)
    {
        var getter = AccessTools.PropertyGetter(type, name);
        if (getter == null)
        {
            Misses.Add($"{type.Name}.{name} getter did not resolve");
        }

        return getter;
    }

    /// <summary>
    /// Apply every Harmony patch class in <paramref name="assembly"/>, one at a
    /// time, and report what armed.
    /// </summary>
    public static void ApplyAll(Harmony harmony, Assembly assembly)
    {
        var armed = new List<string>();
        var degraded = new List<string>();

        // (type name, rendered line). The NAME is kept separately rather than
        // parsed back out of the line: the first cut of this carried the name
        // by string-splitting the report on ':', and adding the patch target to
        // that line silently broke softlock-guard escalation. The bite-check
        // caught it, which is the argument for keeping the two apart.
        var failed = new List<(string Name, string Line)>();

        List<Type> patchClasses;
        try
        {
            patchClasses = PatchClasses(assembly);
        }
        catch (Exception e)
        {
            // Only reachable if the assembly itself will not enumerate, which
            // is a load problem rather than a patch problem. Nothing is armed.
            Log.Error($"[{KleeMod.ModId}] HARMONY BOOTSTRAP ABORTED before any patch "
                    + $"was applied: {e}");
            return;
        }

        foreach (var type in patchClasses)
        {
            var missesBefore = Misses.Count;

            try
            {
                var patched = harmony.CreateClassProcessor(type).Patch();
                var misses = Misses.Skip(missesBefore).ToList();

                if (patched == null || patched.Count == 0)
                {
                    // Nothing threw and nothing was patched. For a class whose
                    // targets come from TargetMethods this is what a fully dead
                    // lookup set looks like, and it is silent by default.
                    failed.Add((type.Name, Describe(type, "armed NO methods", misses)));
                }
                else if (misses.Count > 0)
                {
                    degraded.Add(Describe(type, $"armed {patched.Count} method(s)", misses));
                    armed.Add(type.Name);
                }
                else
                {
                    armed.Add(type.Name);
                }
            }
            catch (Exception e)
            {
                var misses = Misses.Skip(missesBefore).ToList();
                failed.Add((type.Name, Describe(type, $"{e.GetType().Name}: {e.Message}", misses)));
            }
        }

        Report(armed, degraded, failed);
    }

    private static string Describe(Type type, string headline, List<string> misses)
    {
        var line = $"{type.Name}{Target(type)}: {headline}";
        return misses.Count == 0 ? line : $"{line} [{string.Join("; ", misses)}]";
    }

    /// <summary>
    /// The declared patch target, read back off the [HarmonyPatch] attribute.
    ///
    /// Worth the reflection: when a class-level target name stops resolving,
    /// Harmony's own exception reads "Patching exception in method null" -- it
    /// cannot name what it failed to find, because not finding it is the
    /// failure. The attribute still holds the name we asked for, so the report
    /// can say `MerchantInventory.PopulateColorlessCardEntries` and turn a line
    /// an operator would have to bisect into one they can act on.
    /// </summary>
    private static string Target(Type type)
    {
        var declared = type.GetCustomAttributes(inherit: true)
            .OfType<HarmonyPatch>()
            .Select(a => a.info)
            .Where(i => i != null)
            .Select(i => (Owner: i.declaringType?.Name, Member: i.methodName))
            .FirstOrDefault(i => i.Owner != null || i.Member != null);

        if (declared.Owner == null && declared.Member == null)
        {
            // No class-level target: the class supplies its own via
            // [HarmonyTargetMethods], and any miss is already in `misses`.
            return string.Empty;
        }

        return $" (target: {declared.Owner ?? "?"}.{declared.Member ?? "?"})";
    }

    private static void Report(List<string> armed, List<string> degraded,
                               List<(string Name, string Line)> failed)
    {
        Log.Info($"[{KleeMod.ModId}] harmony: {armed.Count} patch class(es) armed.");

        foreach (var line in degraded)
        {
            Log.Warn($"[{KleeMod.ModId}] harmony DEGRADED: {line}. The class is armed; "
                   + "the named lookups are not, so that much behaviour is absent.");
        }

        if (failed.Count == 0)
        {
            return;
        }

        var casualties = failed
            .Select(f => f.Name)
            .Where(SoftlockGuards.Contains)
            .ToList();

        Log.Error($"[{KleeMod.ModId}] ===================================================");
        Log.Error($"[{KleeMod.ModId}] HARMONY BOOTSTRAP: {failed.Count} PATCH CLASS(ES) DID NOT ARM");
        foreach (var (_, line) in failed)
        {
            Log.Error($"[{KleeMod.ModId}]   FAILED  {line}");
        }

        Log.Error($"[{KleeMod.ModId}] Every OTHER patch in this assembly is armed -- these "
                + "failed in isolation, which is what per-type patching buys.");

        if (casualties.Count > 0)
        {
            Log.Error($"[{KleeMod.ModId}] *** {casualties.Count} of these is a SOFTLOCK GUARD: "
                    + $"{string.Join(", ", casualties)}. This session can lose a run to a "
                    + "black screen (shop entry, reward draw, or the end of an elite/boss "
                    + "fight). Do not playtest on this build; fix the lookup. ***");
        }

        Log.Error($"[{KleeMod.ModId}] ===================================================");
    }

    /// <summary>
    /// Every type carrying a class-level [HarmonyPatch], plus a check for the
    /// mistake PatchAll also swallows: a class with patch METHODS
    /// ([HarmonyPostfix] and friends) but no class-level [HarmonyPatch] is
    /// skipped entirely and in total silence, by Harmony and by us. Reporting
    /// it costs one pass and closes the one gap per-type patching would
    /// otherwise share with PatchAll.
    /// </summary>
    private static List<Type> PatchClasses(Assembly assembly)
    {
        var patchClasses = new List<Type>();

        foreach (var type in AccessTools.GetTypesFromAssembly(assembly))
        {
            if (type.GetCustomAttributes(inherit: true).Any(a => a is HarmonyPatch))
            {
                patchClasses.Add(type);
                continue;
            }

            var strays = type
                .GetMethods(AccessTools.all)
                .Where(m => m.GetCustomAttributes(inherit: true).Any(a =>
                    a is HarmonyPrefix or HarmonyPostfix or HarmonyTranspiler
                      or HarmonyFinalizer or HarmonyTargetMethods or HarmonyTargetMethod))
                .Select(m => m.Name)
                .ToList();

            if (strays.Count > 0)
            {
                Log.Error($"[{KleeMod.ModId}] harmony: {type.Name} declares patch method(s) "
                        + $"({string.Join(", ", strays)}) but carries no class-level "
                        + "[HarmonyPatch], so NOTHING in it is applied. This is silent in "
                        + "Harmony's own PatchAll too -- add the attribute or delete the "
                        + "methods.");
            }
        }

        return patchClasses;
    }
}
