using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using Log = MegaCrit.Sts2.Core.Logging.Log;

namespace LaneD.EnemySeam;

/// <summary>
/// Per-type Harmony application for the Lane D spike, deliberately the same
/// shape as klee-mod/KleeCode/KleePatchBootstrap.cs.
///
/// WHY NOT PatchAll. PatchAll walks the assembly in reflection order inside
/// ONE try/catch: the first class that throws aborts the walk and every class
/// after it is silently never applied. Per-class processing means one dead
/// lookup disarms one patch and names itself.
///
/// WHY A CLASS THAT ARMED ZERO IS A FAILURE. Harmony returns an empty list,
/// not an exception, when a class matches no method. For a presentation seam
/// that is the worst outcome available: the game looks completely normal and
/// the spike is simply absent. It is reported as an error for that reason.
///
/// This is a SPIKE bootstrap. It has no softlock-guard escalation because it
/// guards nothing: every patch here falls through to base behaviour, so the
/// consequence of a failure is "the enemy keeps its own art", never a lost
/// run.
/// </summary>
public static class SeamBootstrap
{
    /// <summary>
    /// Apply every Harmony patch class in <paramref name="assembly"/>, one at
    /// a time, and return the armed count so a harness can assert on it
    /// instead of scraping the log.
    /// </summary>
    public static int ApplyAll(Harmony harmony, Assembly assembly)
    {
        var armed = new List<string>();
        var failed = new List<string>();

        List<Type> patchClasses;
        try
        {
            patchClasses = PatchClasses(assembly);
        }
        catch (Exception e)
        {
            Log.Error($"[{NeutralEnemySeam.Tag}] BOOTSTRAP ABORTED before any patch "
                    + $"was applied: {e}");
            return 0;
        }

        foreach (var type in patchClasses)
        {
            try
            {
                var patched = harmony.CreateClassProcessor(type).Patch();
                if (patched == null || patched.Count == 0)
                {
                    failed.Add($"{type.Name}{Target(type)}: armed NO methods");
                }
                else
                {
                    armed.Add(type.Name);
                }
            }
            catch (Exception e)
            {
                failed.Add($"{type.Name}{Target(type)}: {e.GetType().Name}: {e.Message}");
            }
        }

        Log.Info($"[{NeutralEnemySeam.Tag}] harmony: {armed.Count} patch class(es) armed"
               + (armed.Count == 0 ? "." : $": {string.Join(", ", armed)}."));

        foreach (var line in failed)
        {
            Log.Error($"[{NeutralEnemySeam.Tag}]   FAILED  {line}");
        }

        if (failed.Count > 0)
        {
            Log.Error($"[{NeutralEnemySeam.Tag}] {failed.Count} patch class(es) did not arm. "
                    + "The spike is partly or wholly absent; the enemy keeps base art.");
        }

        return armed.Count;
    }

    /// <summary>
    /// Register the scene conversion, then arm the patches. Order matters:
    /// registration is cheap and must be in place before any instantiation the
    /// patches could cause.
    /// </summary>
    public static int Initialize(Harmony harmony, Assembly assembly)
    {
        NeutralEnemySeam.Install();
        return ApplyAll(harmony, assembly);
    }

    /// <summary>
    /// The declared patch target read back off the attribute. Harmony's own
    /// exception says "Patching exception in method null" when a class-level
    /// target stops resolving -- it cannot name what it failed to find. The
    /// attribute still holds the name we asked for.
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
            return string.Empty;
        }

        return $" (target: {declared.Owner ?? "?"}.{declared.Member ?? "?"})";
    }

    /// <summary>
    /// Every type carrying a class-level [HarmonyPatch], plus the mistake
    /// PatchAll also swallows: a class with patch METHODS but no class-level
    /// [HarmonyPatch] is skipped entirely and in silence.
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

            var orphanMethods = type
                .GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static)
                .Any(m => m.GetCustomAttributes(inherit: true).Any(
                    a => a is HarmonyPrefix or HarmonyPostfix or HarmonyTranspiler));

            if (orphanMethods)
            {
                Log.Error($"[{NeutralEnemySeam.Tag}] {type.Name} has patch methods but no "
                        + "class-level [HarmonyPatch]; it patches NOTHING and would be "
                        + "skipped in silence.");
            }
        }

        return patchClasses;
    }
}
