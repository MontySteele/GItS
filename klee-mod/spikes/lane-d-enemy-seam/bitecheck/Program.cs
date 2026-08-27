using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using LaneD.EnemySeam;

namespace LaneD.EnemySeam.BiteCheck;

/// <summary>
/// Lane D bite-check: prove the neutral enemy presentation seam OUTSIDE Godot.
///
/// WHY THIS EXISTS. [USER] is playtesting; the game may not be launched,
/// deployed to, or packed tonight. The three things Lane D has to establish are
/// nonetheless all decidable from a bare .NET process, because sts2.dll is a
/// plain net9.0 assembly and Harmony patching needs no scene tree:
///
///   (i)   the seam REPLACES the subject enemy's presentation;
///   (ii)  it does so WITHOUT a global overwrite -- every other monster still
///         resolves to its own base scene, and the replacement string never
///         points into the base res://scenes/ namespace;
///   (iii) it touches NO mechanics -- checked here by what the seam patches,
///         and by the source-contract test in tier0/tests.
///
/// It also answers S13's open question 1 (does a second prefix on
/// MonsterModel.get_VisualsPath compose with BaseLib's own?) by arming
/// BaseLib's real patch class first and then reading the value back.
///
/// WHAT IT CANNOT DO. Nothing here renders. The proof scene is never parsed,
/// no PackedScene is instantiated, and no NCreatureVisuals is built -- all
/// three need the Godot runtime. Those belong to the morning live procedure in
/// review/dispatch3/tooling-laned-handoff.md.
/// </summary>
internal static class Program
{
    private static int Main(string[] args)
    {
        // Install the resolver BEFORE any method that references sts2 /
        // GodotSharp / BaseLib is JITted. Run() is a separate, non-inlined
        // method for exactly that reason: method bodies are JITted lazily, so
        // by the time Run's body needs those assemblies the handler is live.
        AppDomain.CurrentDomain.AssemblyResolve += (_, e) =>
        {
            var name = new AssemblyName(e.Name).Name;
            if (name == "BaseLib" && File.Exists(LocalPaths.BaseLibDll))
            {
                return Assembly.LoadFrom(LocalPaths.BaseLibDll);
            }

            var probe = Path.Combine(LocalPaths.GameDataDir, name + ".dll");
            return File.Exists(probe) ? Assembly.LoadFrom(probe) : null;
        };

        try
        {
            return Run();
        }
        catch (Exception e)
        {
            var inner = e is TargetInvocationException t ? t.InnerException ?? e : e;
            Console.Error.WriteLine($"HARNESS THREW {inner.GetType().Name}: {inner.Message}");
            Console.Error.WriteLine(inner.StackTrace);
            return 2;
        }
    }

    private const string MonsterModelName = "MegaCrit.Sts2.Core.Models.MonsterModel";
    private const string AbstractModelName = "MegaCrit.Sts2.Core.Models.AbstractModel";
    private const string ModelDbName = "MegaCrit.Sts2.Core.Models.ModelDb";
    private const string BaseVisualsPrefix = "res://scenes/creature_visuals/";

    private static readonly List<string> Failures = new();

    [MethodImpl(MethodImplOptions.NoInlining)]
    private static int Run()
    {
        var sts2 = Assembly.LoadFrom(Path.Combine(LocalPaths.GameDataDir, "sts2.dll"));
        var baseLib = Assembly.LoadFrom(LocalPaths.BaseLibDll);

        Console.WriteLine("--- Lane D neutral enemy seam bite-check ---");
        Console.WriteLine($"sts2      {Path.Combine(LocalPaths.GameDataDir, "sts2.dll")}");
        Console.WriteLine($"BaseLib   {LocalPaths.BaseLibDll}");
        Console.WriteLine($"spike     {typeof(NeutralEnemySeam).Assembly.Location}");
        Console.WriteLine($"subject   MONSTER.{NeutralEnemySeam.TargetEntry}");
        Console.WriteLine($"proof     {NeutralEnemySeam.ProofScenePath}");
        Console.WriteLine();

        RedirectGameLog(sts2);

        // ---- 1. BaseLib's OWN patches on the same two members, armed first.
        // Priority ordering is the whole answer to "do they compose": BaseLib
        // patches at default priority, the spike at Priority.Low, so BaseLib's
        // prefix runs first and falls through for a base monster.
        var harmonyBaseLib = new Harmony("bitecheck.baselib");
        ArmBaseLibClass(harmonyBaseLib, baseLib, "BaseLib.Abstracts.VisualsPath");
        ArmBaseLibClass(harmonyBaseLib, baseLib, "BaseLib.Abstracts.CreateVisuals");

        // ---- 2. The spike. ResourceLoader.Exists is a native Godot call, so
        // the probe is stubbed: "the proof scene exists, nothing else does".
        NeutralEnemySeam.SceneExistsProbe =
            path => path == NeutralEnemySeam.ProofScenePath;

        var armed = SeamBootstrap.ApplyAll(
            new Harmony("bitecheck.laned"), typeof(NeutralEnemySeam).Assembly);

        Console.WriteLine();
        Check("spike armed both patch classes", armed == 2, $"armed {armed}, expected 2");

        var monsterModel = sts2.GetType(MonsterModelName, throwOnError: true);
        var getter = AccessTools.PropertyGetter(monsterModel, "VisualsPath");
        Check("MonsterModel.VisualsPath getter resolves", getter != null, "lookup returned null");
        if (getter == null)
        {
            return Verdict();
        }

        // ---- 3. Coexistence, read off Harmony's own patch record.
        var info = Harmony.GetPatchInfo(getter);
        var owners = info?.Prefixes.Select(p => p.owner).OrderBy(o => o).ToList()
                     ?? new List<string>();
        Console.WriteLine($"prefixes on MonsterModel.get_VisualsPath: "
                        + $"{owners.Count} ({string.Join(", ", owners)})");
        Check("BaseLib and the spike coexist on the getter",
              owners.Contains("bitecheck.baselib") && owners.Contains("bitecheck.laned"),
              $"owners = {string.Join(", ", owners)}");

        // ---- 4. The sweep. Every concrete monster in the base game, read
        // through the patched getter.
        var sweep = Sweep(sts2, monsterModel, getter);
        Report(sweep);

        // ---- 5. Degradation: with no pack, the subject must look base again.
        NeutralEnemySeam.SceneExistsProbe = _ => false;
        var degraded = sweep.Claimed
            .Select(r => (string)getter.Invoke(r.Instance, null))
            .ToList();
        Check("with the pack absent the subject falls back to its base scene",
              degraded.All(v => v != null && v.StartsWith(BaseVisualsPrefix, StringComparison.Ordinal)),
              $"got {string.Join(", ", degraded)}");

        return Verdict();
    }

    private sealed record MonsterRow(Type Type, object Instance, string Entry, string Value);

    private sealed record SweepResult(
        List<MonsterRow> Claimed,
        List<MonsterRow> Untouched,
        List<MonsterRow> Diverged,
        List<Type> Overriders,
        List<string> Uninstantiable);

    /// <summary>
    /// Read VisualsPath on every concrete MonsterModel subclass in sts2.dll.
    ///
    /// Instances come from GetUninitializedObject, not a constructor: the base
    /// AbstractModel constructor registers with ModelDb and would throw
    /// DuplicateModelException on a second instance, and no constructor is
    /// needed anyway -- the getter reads exactly one thing, the model's Id,
    /// which is set here from the same derivation the game uses
    /// (ModelDb.GetId, i.e. the slugified type name).
    /// </summary>
    private static SweepResult Sweep(Assembly sts2, Type monsterModel, MethodBase getter)
    {
        var abstractModel = sts2.GetType(AbstractModelName, throwOnError: true);
        var modelDb = sts2.GetType(ModelDbName, throwOnError: true);
        var getId = modelDb.GetMethod("GetId", new[] { typeof(Type) });
        var idBackingField = AccessTools.Field(abstractModel, "<Id>k__BackingField");

        if (getId == null || idBackingField == null)
        {
            Failures.Add("ModelDb.GetId(Type) or AbstractModel's Id backing field "
                       + "did not resolve; the game's id derivation changed.");
            return new SweepResult(new(), new(), new(), new(), new());
        }

        var claimed = new List<MonsterRow>();
        var untouched = new List<MonsterRow>();
        var diverged = new List<MonsterRow>();
        var overriders = new List<Type>();
        var uninstantiable = new List<string>();

        foreach (var type in AccessTools.GetTypesFromAssembly(sts2)
                     .Where(t => !t.IsAbstract && monsterModel.IsAssignableFrom(t))
                     .OrderBy(t => t.Name))
        {
            // A subclass that redeclares the getter is NOT reachable from a
            // patch on the base getter: virtual dispatch runs its override and
            // Harmony patched a different method body. Recorded, not fixed.
            var ownGetter = AccessTools.PropertyGetter(type, "VisualsPath");
            if (ownGetter != null && ownGetter.DeclaringType != monsterModel)
            {
                overriders.Add(type);
                continue;
            }

            object instance;
            object id;
            try
            {
                instance = RuntimeHelpers.GetUninitializedObject(type);
                id = getId.Invoke(null, new object[] { type });
                idBackingField.SetValue(instance, id);
            }
            catch (Exception e)
            {
                uninstantiable.Add($"{type.Name}: {e.GetType().Name}");
                continue;
            }

            var entry = (string)id.GetType().GetProperty("Entry")!.GetValue(id);
            var value = (string)getter.Invoke(instance, null);
            var row = new MonsterRow(type, instance, entry, value);

            if (entry == NeutralEnemySeam.TargetEntry)
            {
                claimed.Add(row);
            }
            else if (value == BaseVisualsPrefix + entry.ToLowerInvariant() + ".tscn")
            {
                untouched.Add(row);
            }
            else
            {
                diverged.Add(row);
            }
        }

        return new SweepResult(claimed, untouched, diverged, overriders, uninstantiable);
    }

    private static void Report(SweepResult s)
    {
        Console.WriteLine();
        Console.WriteLine($"monsters swept        {s.Claimed.Count + s.Untouched.Count + s.Diverged.Count}");
        Console.WriteLine($"  claimed by seam     {s.Claimed.Count}");
        Console.WriteLine($"  base path intact    {s.Untouched.Count}");
        Console.WriteLine($"  UNEXPECTED value    {s.Diverged.Count}");
        Console.WriteLine($"declare own getter    {s.Overriders.Count} "
                        + $"({string.Join(", ", s.Overriders.Select(t => t.Name))})");
        if (s.Uninstantiable.Count > 0)
        {
            Console.WriteLine($"not readable          {s.Uninstantiable.Count} "
                            + $"({string.Join("; ", s.Uninstantiable)})");
        }

        Console.WriteLine();
        foreach (var row in s.Claimed)
        {
            Console.WriteLine($"  CLAIMED  {row.Entry} -> {row.Value}");
        }

        foreach (var row in s.Diverged)
        {
            Console.WriteLine($"  DIVERGED {row.Entry} -> {row.Value}");
        }

        Console.WriteLine();

        Check("exactly one monster is claimed", s.Claimed.Count == 1,
              $"{s.Claimed.Count} claimed");
        Check("the claimed monster serves the proof scene",
              s.Claimed.All(r => r.Value == NeutralEnemySeam.ProofScenePath),
              string.Join(", ", s.Claimed.Select(r => r.Value)));
        Check("the replacement stays out of the base res://scenes namespace",
              s.Claimed.All(r => NeutralEnemySeam.RejectsBaseNamespace(r.Value)),
              "a replacement pointed into res://scenes/, which a pack would overwrite");
        Check("no other monster's path moved", s.Diverged.Count == 0,
              $"{s.Diverged.Count} diverged: "
              + string.Join(", ", s.Diverged.Select(r => $"{r.Entry}={r.Value}")));
        Check("the sweep actually covered the roster", s.Untouched.Count >= 100,
              $"only {s.Untouched.Count} monsters read back a base path");
    }

    private static void ArmBaseLibClass(Harmony harmony, Assembly baseLib, string typeName)
    {
        var type = baseLib.GetType(typeName, throwOnError: false);
        if (type == null)
        {
            Failures.Add($"{typeName} not found in BaseLib; its own patch class was "
                       + "renamed or removed, so the coexistence check is void.");
            return;
        }

        var patched = harmony.CreateClassProcessor(type).Patch();
        Console.WriteLine($"BaseLib {typeName}: armed {patched?.Count ?? 0} method(s)");
        if (patched == null || patched.Count == 0)
        {
            Failures.Add($"{typeName} armed nothing.");
        }
    }

    /// <summary>
    /// The game's logger writes where this process cannot see, so patch it to
    /// stdout before anything can log -- using the mechanism under test to
    /// observe the mechanism under test (same trick as klee-mod/build/bitecheck).
    /// </summary>
    private static void RedirectGameLog(Assembly sts2)
    {
        var log = sts2.GetType("MegaCrit.Sts2.Core.Logging.Log", throwOnError: true);
        var redirect = new Harmony("bitecheck.logredirect");
        var capture = new HarmonyMethod(
            typeof(Program).GetMethod(nameof(Capture),
                BindingFlags.NonPublic | BindingFlags.Static));

        foreach (var level in new[] { "Info", "Warn", "Error" })
        {
            var target = log.GetMethod(level,
                BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static);
            if (target == null)
            {
                Failures.Add($"Log.{level} not found -- game version changed?");
                continue;
            }

            redirect.Patch(target, prefix: capture);
        }
    }

    private static bool Capture(string text)
    {
        Console.WriteLine(text);
        return false;
    }

    private static void Check(string what, bool ok, string detail)
    {
        Console.WriteLine($"[{(ok ? "PASS" : "FAIL")}] {what}");
        if (!ok)
        {
            Failures.Add($"{what} -- {detail}");
        }
    }

    private static int Verdict()
    {
        Console.WriteLine();
        if (Failures.Count == 0)
        {
            Console.WriteLine("RESULT: all checks passed.");
            Console.WriteLine("This proves the seam's STRING and DISPATCH behaviour only. "
                            + "Nothing was rendered, packed, or launched.");
            return 0;
        }

        Console.Error.WriteLine($"RESULT: {Failures.Count} failure(s).");
        foreach (var f in Failures)
        {
            Console.Error.WriteLine($"  {f}");
        }

        return 1;
    }
}
