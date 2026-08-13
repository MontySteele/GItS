using System;
using System.IO;
using System.Reflection;
using HarmonyLib;

namespace KleeMod.BiteCheck;

/// <summary>
/// F2 bite-check: run the mod's Harmony bootstrap OUTSIDE Godot and print what
/// armed.
///
/// WHY THIS EXISTS. `KleePatchBootstrap` decides what happens when a reflection
/// lookup dies, and that decision is only observable at boot. There is no C#
/// test project, the Python suite cannot import a Godot assembly, and the
/// alternative gate is "launch the game and read godot.log", which is slow
/// enough that nobody does it for a one-line change. The suite pins the SHAPE
/// (tier0/tests/test_harmony_bootstrap_contract.py); this runs the BEHAVIOUR.
///
/// IT WORKS BECAUSE PATCHING DOES NOT NEED GODOT. sts2.dll is a plain net9.0
/// assembly. Loading it and applying Harmony patches to its methods needs no
/// scene tree and no native Godot runtime -- verified: all 17 patch classes arm
/// here exactly as they do in game. What does NOT work is calling anything that
/// touches Godot objects, so this harness only ever patches and reports.
///
/// The game's logger writes somewhere this process cannot see, so the first
/// thing we do is Harmony-patch Log.Info/Warn/Error to stdout -- using the very
/// mechanism under test to observe the mechanism under test.
///
/// HOW TO USE IT. See README.md. The short version: run it once unmodified and
/// note the armed count, break exactly one lookup in KleeCode, rebuild, run it
/// again, and confirm the count drops by one and the report NAMES the casualty.
/// </summary>
internal static class Program
{
    private static int Main(string[] args)
    {
        var kleeDll = args.Length > 0
            ? args[0]
            : Path.GetFullPath(Path.Combine(
                AppContext.BaseDirectory, "..", "..", "..", "..",
                "KleeCode", "bin", "Debug", "klee.dll"));

        if (!File.Exists(kleeDll))
        {
            Console.Error.WriteLine($"klee.dll not found at {kleeDll}");
            Console.Error.WriteLine("Build it first, or pass the path as argument 1.");
            return 2;
        }

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

        var sts2 = Assembly.LoadFrom(Path.Combine(LocalPaths.GameDataDir, "sts2.dll"));

        // Redirect the game's log to stdout before anything can log.
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
                Console.Error.WriteLine($"Log.{level} not found -- game version changed?");
                return 2;
            }

            redirect.Patch(target, prefix: capture);
        }

        var klee = Assembly.LoadFrom(kleeDll);
        var bootstrap = klee.GetType("KleeMod.KleePatchBootstrap", throwOnError: true);
        var applyAll = bootstrap.GetMethod("ApplyAll",
            BindingFlags.Public | BindingFlags.Static);

        if (applyAll == null)
        {
            Console.Error.WriteLine("KleePatchBootstrap.ApplyAll not found.");
            return 2;
        }

        Console.WriteLine($"--- KleePatchBootstrap.ApplyAll on {kleeDll} ---");
        try
        {
            applyAll.Invoke(null, new object[] { new Harmony("bitecheck.klee"), klee });
        }
        catch (Exception e)
        {
            var inner = e.InnerException ?? e;
            Console.Error.WriteLine($"ApplyAll THREW {inner.GetType().Name}: {inner.Message}");
            Console.Error.WriteLine("That is itself a finding: ApplyAll must never throw. "
                                  + "It exists to contain failures, not to propagate them.");
            return 1;
        }

        return 0;
    }

    /// <summary>Prefix on the game's logger: print, and skip the original.</summary>
    private static bool Capture(string text)
    {
        Console.WriteLine(text);
        return false;
    }
}
