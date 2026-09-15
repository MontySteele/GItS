using HarmonyLib;
using MegaCrit.Sts2.Core.Nodes.Audio;

namespace KleeMod.Teyvat.Patches;

/// <summary>
/// THE MUSIC SEAM -- `MegaCrit.Sts2.Core.Nodes.Audio.NRunMusicController.UpdateMusic`
/// and `.StopMusic`.
///
/// `UpdateMusic` is the game's one run-scoped music decision. It resolves a
/// track from `_runState.Act.BgMusicOptions` and `MusicBankPaths` against the
/// run seed, loads the act's FMOD bank, and calls `_proxy.Call("update_music",
/// ...)` -- and it is called on every room change, so it is also where a
/// replacement has to re-assert itself. `NRun.Instance.RunMusicController` is
/// the node, which makes `__instance` both the patch target and the parent our
/// `AudioStreamPlayer` hangs under: same lifetime as the run's music, so
/// nothing has to remember to clean up.
///
/// A POSTFIX AND NOT A PREFIX, deliberately. The base game's own work runs
/// first and completes -- the bank loads, `_currentTrack` is set, ambience
/// updates -- and only then does the arm stop it. A prefix that skipped
/// `UpdateMusic` would leave `_currentTrack` stale, so the moment a track file
/// went missing or the arm was turned off mid-session the controller would
/// believe it was already playing the right thing and never recover.
///
/// THE DUCK IS A STOP, because there is nothing to lower: a grep of the whole
/// decompile finds no FMOD bus, snapshot or duck call in managed code
/// (`TeyvatMusic`'s header carries the finding and the three audio files it
/// rests on). So the arm calls the game's own `StopMusic` and plays its track
/// over the silence.
///
/// AND IT IS A NO-OP WITH NO FILE. `TeyvatMusic.Play` returns false without
/// touching anything unless a track is actually in the pack for the current
/// act, and only a true return reaches `StopMusic`. On today's tree -- no
/// audio file committed, none packaged -- both postfixes below fall straight
/// through, which is the acceptance condition item 4.4 was given.
///
/// WHAT A DEPLOY MUST STILL PROVE, since a build cannot: that `StopMusic`
/// called from inside a postfix of `UpdateMusic` does not re-enter
/// `UpdateMusic` (nothing in the decompiled body suggests it does, but the
/// `_proxy` side is GDExtension and unread); that the four surfaces item 4.4
/// names -- combat start, rest site, map screen, boss intro -- each route
/// through `UpdateMusic` rather than through `PlayCustomMusic`,
/// `ToggleMerchantTrack`, `TriggerEliteSecondPhase` or
/// `TriggerCampfireGoingOut`, which are four SEPARATE public methods on this
/// controller and would each need their own row; and that a Godot
/// `AudioStreamPlayer` is audible at all while FMOD holds the device.
/// </summary>
[HarmonyPatch(typeof(NRunMusicController))]
internal static class NRunMusicController_TeyvatTrack_Patch
{
    /// <summary>
    /// Re-entrancy guard. The `UpdateMusic` postfix calls `StopMusic` itself,
    /// which fires the `StopMusic` postfix below -- and that postfix's job is
    /// to tear down the very player `UpdateMusic` just built. This flag is how
    /// the second postfix tells "the game stopped its music" (tear down) from
    /// "the arm stopped the FMOD track so ours could play" (leave it alone).
    ///
    /// A plain static, not `[ThreadStatic]`: `NRunMusicController` is
    /// single-instance and the whole audio path is Godot's main thread, so a
    /// thread-local here would be dressing up a guarantee the engine already
    /// gives.
    /// </summary>
    private static bool _inArmedStop;

    [HarmonyPostfix]
    [HarmonyPatch(nameof(NRunMusicController.UpdateMusic))]
    private static void UpdateMusicPostfix(NRunMusicController __instance)
    {
        if (!TeyvatFrame.Enabled || __instance == null)
        {
            return;
        }

        if (!TeyvatMusic.Play(__instance, TeyvatFrame.CurrentActEntry))
        {
            return;
        }

        // `try`/`finally` and not a bare pair of assignments: an exception out
        // of the game's own `StopMusic` must not leave the guard set, or every
        // later teardown in the session would silently decline to run.
        _inArmedStop = true;
        try
        {
            __instance.StopMusic();
        }
        finally
        {
            _inArmedStop = false;
        }
    }

    [HarmonyPostfix]
    [HarmonyPatch(nameof(NRunMusicController.StopMusic))]
    private static void StopMusicPostfix(NRunMusicController __instance)
    {
        // NOT gated on `TeyvatFrame.Enabled`, and that is deliberate: a
        // session that turns the arm off must still get our node torn down the
        // next time the game stops its music. Cleanup never sits behind the
        // flag that created the thing being cleaned up.
        if (_inArmedStop)
        {
            return;
        }

        TeyvatMusic.Stop(__instance);
    }
}
