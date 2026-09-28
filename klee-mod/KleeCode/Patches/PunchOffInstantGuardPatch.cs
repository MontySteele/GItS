using System.Threading.Tasks;
using HarmonyLib;
using KleeMod.Teyvat.Events.Mirrors;
using MegaCrit.Sts2.Core.Models.Events;
using MegaCrit.Sts2.Core.Settings;

namespace KleeMod.Patches;

/// <summary>
/// `EB-1`, THE PUNCH OFF SOFT-LOCK, FOR THE BASE EVENT.
///
/// `PunchOffMirror` (`EB-769`) bounds the punching loop, but it only stands in
/// for <c>PunchOff</c> in the Liyue Teyvat frame. Everywhere else -- base
/// characters, the other frames, the arm off -- the base game's
/// <c>PunchOff.PunchEachOther</c> runs, and under <c>FastModeType.Instant</c>
/// (what the blind-play harness sets on every lane) its <c>Cmd.Wait</c>s are
/// no-ops, so the loop never yields and instantiates VFX every pass until the
/// RID allocator runs out. An Ironclad run hit it on floor 7 on 2026-09-28.
///
/// UNDER INSTANT THE LOOP IS SKIPPED, NOT BOUNDED, because it is purely
/// decorative and nothing waits on it (0.111.0 decompile of
/// <c>PunchOff</c>): <c>AfterEventStarted</c> subscribes <c>OnRoomExited</c>,
/// creates <c>_punchCts</c>, and hands the loop's task to
/// <c>TaskHelper.RunSafely</c> fire-and-forget; no option awaits it.
/// <c>TakeThem</c> and <c>OnRoomExited</c> each call <c>_punchCts?.Cancel()</c>
/// on a source that is still there, and <c>OnRoomExited</c> still
/// unsubscribes itself, so nothing dangles -- the base event never disposes
/// the source either. The only difference is that the loop's own tail (null
/// the source, restore the left construct's flipped scale) never runs, and
/// its head (the flip) never ran. The options, the gold roll, Nab's curse and
/// relic, and the fight with its two extra rewards are untouched.
///
/// AT EVERY OTHER SPEED THE PREFIX RETURNS TRUE AND THE BASE LOOP RUNS
/// BYTE FOR BYTE. The mirror's own class is not a <c>PunchOff</c>, so this
/// patch never reaches it.
/// </summary>
[HarmonyPatch(typeof(PunchOff), "PunchEachOther")]
internal static class PunchOff_PunchEachOther_InstantGuard_Patch
{
    /// <summary>
    /// Skip the cosmetic loop? Pure, so a headless test can pin it: only
    /// under <c>Instant</c>.
    /// </summary>
    internal static bool ShouldSkipLoop(FastModeType fastMode)
        => fastMode == FastModeType.Instant;

    [HarmonyPrefix]
    public static bool Prefix(ref Task __result)
    {
        if (!ShouldSkipLoop(PunchOffMirror.CurrentFastMode()))
        {
            return true;
        }

        __result = Task.CompletedTask;
        return false;
    }
}
