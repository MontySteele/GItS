using System;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using Xunit;

// Static game state is shared across every test in this assembly
// (SpotlightSystem.PendingDraws, SalonMemberPower.Company, BaseLib's resource
// tables). xunit parallelises across collections by default, which would race
// them. One process, one thread, no theatre.
[assembly: CollectionBehavior(DisableTestParallelization = true)]

namespace KleeMod.Tests.Harness;

/// <summary>
/// The one thing that makes a headless C# test project possible at all.
///
/// THE PROBLEM. sts2.dll is a plain net9.0 assembly, so its logic types load
/// and run outside Godot -- that is the F2 bite-check's whole finding. But the
/// first call into <c>MegaCrit.Sts2.Core.Logging.Logger</c> runs a static
/// constructor that asks <c>Godot.OS.GetCmdlineArgs()</c> whether it is running
/// in the editor, and Godot's native interop is not loaded in a test host. The
/// result is not an exception a test can catch: it is a 0xC0000005 access
/// violation that kills the whole process mid-run.
///
/// BaseLib reaches that logger on the FIRST read of any
/// <c>CustomResources&lt;T&gt;</c>, which is every Fanfare, Encore, Charge and
/// Burst accessor in the mod. Without this class, the reachable surface is
/// consts and pure string builders. With it, per-seat resources are reachable,
/// which is where the co-op tests live.
///
/// THE FIX, and it is the bite-check's own idiom. Harmony-patch
/// <c>Logger.GetIsRunningFromGodotEditor</c> to return false BEFORE anything
/// touches it, so the static constructor never calls into Godot, and silence
/// the log sinks. A module initializer runs on assembly load, ahead of the
/// first test, which is early enough.
///
/// WHAT THIS DOES NOT DO. It does not stub the game. Every type below is the
/// real shipped type and every method under test is the real shipped method.
/// The patch is confined to the game's LOGGER; nothing in the mod's own code
/// is patched, replaced or mocked. See README.md for the boundary this leaves
/// standing.
/// </summary>
internal static class HeadlessGame
{
    internal const BindingFlags All =
        BindingFlags.Public | BindingFlags.NonPublic
        | BindingFlags.Instance | BindingFlags.Static;

    private static bool _armed;

    [ModuleInitializer]
    internal static void Arm()
    {
        if (_armed) return;
        _armed = true;

        var harmony = new Harmony("kleetests.headless");
        var logger = typeof(MegaCrit.Sts2.Core.Logging.Logger);

        var editorProbe = logger.GetMethod("GetIsRunningFromGodotEditor", All)
            ?? throw new InvalidOperationException(
                "Logger.GetIsRunningFromGodotEditor is gone -- the game version "
                + "changed and the headless harness needs re-deriving. See "
                + "KleeTests/README.md.");
        harmony.Patch(
            editorProbe,
            prefix: new HarmonyMethod(typeof(HeadlessGame)
                .GetMethod(nameof(NotTheEditor), All)));

        // Log sinks write through Godot too. Swallow rather than redirect: a
        // test run is not a boot report, and the bite-check already owns the
        // job of reading one.
        foreach (var sink in logger.GetMethods(All)
                     .Where(m => m.Name is "Info" or "Warn" or "Error" or "Debug"))
        {
            try
            {
                harmony.Patch(
                    sink,
                    prefix: new HarmonyMethod(typeof(HeadlessGame)
                        .GetMethod(nameof(Swallow), All)));
            }
            catch
            {
                // An overload Harmony cannot patch (generic, inlined) is not
                // fatal: the editor probe above is the leg that matters.
            }
        }
    }

    private static bool NotTheEditor(ref bool __result)
    {
        __result = false;
        return false;
    }

    private static bool Swallow() => false;
}
