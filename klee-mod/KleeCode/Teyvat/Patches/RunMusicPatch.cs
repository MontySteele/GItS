using System;
using System.Reflection;
using HarmonyLib;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Audio;

namespace KleeMod.Teyvat.Patches;

/// <summary>
/// THE MUSIC SEAM -- `MegaCrit.Sts2.Core.Nodes.Audio.NRunMusicController.UpdateMusic`
/// and `.StopMusic`.
///
/// ===================================================================
/// `EB-821` -- THE DECISION, AND IT IS ROUTE (b): KEEP THE STOP, GUARD
/// THE PARAMETER CALLS. It sits at the top because the whole file turns on it.
///
/// THE DEFECT ([USER], 2026-09-17, bisected the same day). With the Teyvat arm
/// on, ANY character entering a REST SITE hard-crashed the game -- native, no
/// managed trace, `godot.log` ending at "Preloading 'RestSite Room' Complete".
/// Our rest scene, the rest track and the character were each ruled out by
/// deploy experiments; the arm's music half was what remained.
///
/// THE MECHANISM, MEASURED. `Reassert` starts our packaged player and then
/// calls the game's `StopMusic()` to silence the act. The controller's whole
/// FMOD surface is one child node, `GetNode&lt;Node&gt;("Proxy")`, whose script is
/// `res://src/gdscript/music_controller_proxy.gdc` in the game pck -- read
/// 2026-09-17 by decompressing that GDScript token buffer (zstd; buffer format
/// version 101) and reading its identifier table. `MusicControllerProxy
/// extends Node` holds `_musicEv: FmodEvent`, `_ambienceEv: FmodEvent` and a
/// `_bank_loader: FmodBankLoader`, and its ONLY FMOD verbs are
/// `check_event_path`, `create_event_instance`, `start`,
/// `set_parameter_by_name`, `set_global_parameter_by_name`, `stop` and
/// `release`. `stop_music` and `stop_ambience` RELEASE the two instances.
/// After that:
///
/// <list type="bullet">
/// <item>anything reaching `set_global_parameter_by_name` is a SERVER call and
/// stays legal. That is `update_global_parameter` -- so `UpdateTrack(string,
/// float)`, `ToggleMerchantTrack`, `TriggerEliteSecondPhase` and `StopMusic`
/// itself are all safe and are deliberately NOT guarded below;</item>
/// <item>anything reaching `set_parameter_by_name` touches the RELEASED
/// instance and takes the FMOD layer down natively. That is exactly two proxy
/// verbs -- `update_music_parameter`, and `update_campfire_ambience` (the
/// "Campfire" parameter) -- behind three managed doors.</item>
/// </list>
///
/// TWO MORE THAT ARE DELIBERATELY LEFT ALONE. `UpdateAmbience` reaches
/// `update_ambience`, which CREATES an instance rather than parameterising one,
/// and its `_currentAmbience != ambientSfx` test makes it a no-op on every path
/// but an act change -- a path already walked with the arm on, on all six
/// dressings (`review/records/teyvat-proofs-7-2026-09-16.md`), so the evidence
/// says it does not bite and a guard there would only make the ambience deader
/// than the arm already leaves it. `UpdateCustomTrack(track, label)` forwards
/// `update_custom_track`, a verb the proxy's identifier table does not contain
/// at all, and it has no managed caller; it is a dead door either way.
///
/// THE THREE DOORS, and why the rest site was the one that bit.
/// `RunManager` calls `NRunMusicController.UpdateTrack()` immediately after
/// `room.Enter(...)` for EVERY room, and again in `ResumePreviousRoom` -- not
/// only from `CombatManager`, which is what
/// `research/sts2-music-map-2026-09-17.md` sec.1 recorded and is the one thing
/// that read has to be corrected on. `UpdateTrack()`'s body sets `Progress`
/// (safe) and then, `if (_runState.CurrentRoom is RestSiteRoom)`, calls
/// `_proxy.Call("update_campfire_ambience", 0)`: the rest site is the single
/// room type that reaches a released instance on ENTRY, which is exactly the
/// bisect's shape. `TriggerCampfireGoingOut()` is the same verb with 1, from
/// `NRestSiteRoom.ExtinguishFireIfAble` once the last rest option is spent.
/// `UpdateMusicParameter(label, n)` is the boss phase call -- eleven monster
/// scripts, `queen_progress` through `waterfall_giant_progress` plus `beckon`
/// -- unreached with the arm on so far, and the same crash waiting.
///
/// WHY NOT ROUTE (a), SILENCE WITHOUT RELEASING. There is no pause, no mute and
/// no per-event volume anywhere on `MusicControllerProxy`: its entire method
/// surface is `update_music`, `stop_music`, `update_music_parameter`,
/// `update_global_parameter`, `update_ambience`, `stop_ambience`,
/// `update_campfire_ambience`, `load_act_bank`, `unload_act_banks`. The only
/// volume lever in the whole GDScript layer is the SIBLING proxy's
/// `set_bgm_volume`, which is
/// `FmodServer.get_bus("bus:/master/music").set_volume(v)` -- the options
/// screen's own BGM bus (`AudioManagerProxy` declares four: master, sfx,
/// ambience, music). Rejected on three measured grounds: nothing anywhere
/// exposes a GETTER for that bus's volume, so a player's slider value cannot be
/// read and therefore cannot be restored; it is global and persistent-looking,
/// so a failure to restore leaves their music slider silently at zero after the
/// arm is off; and it would also swallow the game-over stinger, which goes out
/// on the same bus through `NAudioManager.PlayMusic`. `TeyvatMusic`'s header
/// inferred all three from the managed assembly alone -- they are now read off
/// the proxy scripts, and they stand.
///
/// SO: `StopMusic()` stays, and the three doors get PREFIXES gated on
/// <see cref="TeyvatMusic.IsArmedPlaying"/>. A prefix returning false skips the
/// original and Harmony still runs our postfixes, so `UpdateTrack`'s room-aware
/// seam is not lost -- only the parameter forward is. And the stop itself is
/// made idempotent (see <see cref="ShouldStop"/>), so the two postfixes that
/// fire on one room change issue at most one.
/// ===================================================================
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

    /// <summary>
    /// THE ONE BODY ALL FOUR ENTRY POINTS SHARE (`EB-814`): resolve the slot
    /// the current room asks for, play it if it is filed, and stop the game's
    /// music only once ours is actually running.
    ///
    /// Idempotent through <see cref="TeyvatMusic.Play"/>, which is what makes
    /// four postfixes on one room change cost one track change and not four.
    /// </summary>
    private static void Reassert(NRunMusicController __instance, bool forceStop = false)
    {
        if (!TeyvatFrame.Enabled || __instance == null)
        {
            return;
        }

        var slot = TeyvatMusic.SlotFor(TeyvatFrame.CurrentRoomType);
        if (!TeyvatMusic.Play(__instance, TeyvatFrame.CurrentActEntry, slot))
        {
            return;
        }

        // `EB-821`: AT MOST ONE STOP PER THING TO STOP. `UpdateMusic` and
        // `UpdateTrack` both fire on one room change, and before this each one
        // issued its own `StopMusic` -- a second `stop_music` on an instance
        // the first already released. It has never been the crash (the proxy's
        // stop is evidently null-safe, or a hundred room changes would have
        // said otherwise), but a released handle touched twice is not
        // something to keep doing on purpose.
        if (!forceStop && !ShouldStop(__instance))
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

    /// <summary>
    /// Is there anything left to stop? `EB-821`'s idempotence, and it is asked
    /// of the game's own bookkeeping rather than of ours.
    ///
    /// `NRunMusicController._currentTrack` is the controller's record of the
    /// FMOD event it has running: `UpdateMusic` sets it when it creates one,
    /// `StopMusic` nulls it. So "non-null" IS "there is a live event instance
    /// to release", exactly, including the case this needs most -- the game
    /// re-created its music between our two postfixes and the second stop is
    /// therefore a real one, not a repeat.
    ///
    /// A remembered slot name was the other candidate and is wrong: the common
    /// room change keeps the same slot while the game re-creates its event
    /// underneath, and a slot-keyed guard would leave the base track audible.
    ///
    /// FAILS OPEN. If a game patch renames the field the reflection returns
    /// null, this answers true, and the arm behaves exactly as it did before
    /// this row -- one redundant stop, never a missing one. The miss is logged
    /// once; `KleeTests` pins the field so a rename is a red test rather than a
    /// quiet regression.
    /// </summary>
    private static bool ShouldStop(NRunMusicController instance)
    {
        if (CurrentTrackField == null)
        {
            return true;
        }

        try
        {
            return CurrentTrackField.GetValue(instance) != null;
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] teyvat: could not read _currentTrack: {e.Message}");
            return true;
        }
    }

    /// <summary>The field <see cref="ShouldStop"/> reads, resolved once. Named
    /// `internal` so the pin can assert the seam resolved rather than assert
    /// the string.</summary>
    internal static readonly FieldInfo? CurrentTrackField =
        AccessTools.Field(typeof(NRunMusicController), "_currentTrack");

    // -------------------------------------------------------------------
    // `EB-821`: THE CRASH GUARDS. Three prefixes, one gate.
    // -------------------------------------------------------------------

    /// <summary>
    /// The gate every guard below reads, and the ONE place the rule is stated:
    /// skip the original exactly while our packaged track is playing, because
    /// that is exactly while the game's FMOD event instance is released.
    ///
    /// NOT gated on <see cref="TeyvatFrame.Enabled"/>, for the teardown
    /// postfix's reason: a session that turns the arm off mid-run still has our
    /// player in the tree and the game's instance still released, and a guard
    /// that stopped biting the moment the flag flipped would put the crash
    /// straight back. With the arm off from boot nothing of ours ever plays,
    /// <see cref="TeyvatMusic.IsArmedPlaying"/> is false, and every one of these
    /// is a branch and a return.
    /// </summary>
    private static bool RunOriginal() => !TeyvatMusic.IsArmedPlaying;

    /// <summary>
    /// THE ROOM-ENTRY CRASH ITSELF. `UpdateTrack()` sets `Progress` -- a
    /// SERVER-level parameter, harmless -- and then, for a rest site only,
    /// forwards `update_campfire_ambience` 0 to the released music instance.
    /// `RunManager` calls it after `room.Enter(...)` for every room, so this is
    /// the prefix [USER]'s 2026-09-17 report is about.
    ///
    /// SKIPPING THE WHOLE METHOD COSTS NOTHING WE WANT. The `Progress` write it
    /// also skips is a crossfade position inside an event that is not playing;
    /// the arm's own room answer is a file, resolved by
    /// `TeyvatMusic.SlotFor` in <see cref="UpdateTrackPostfix"/>, which Harmony
    /// still runs after a skipping prefix. When the arm's track later stops,
    /// `StopMusic` resets `Progress` to 0 and `UpdateMusic` re-establishes it.
    ///
    /// THE ZERO-ARG OVERLOAD ONLY, exactly as the postfix: the private
    /// `(string, float)` sibling reaches `update_global_parameter` and is safe,
    /// and the empty `Type[]` is what tells Harmony which is meant.
    /// </summary>
    [HarmonyPrefix]
    [HarmonyPatch(nameof(NRunMusicController.UpdateTrack), new Type[0])]
    private static bool UpdateTrackPrefix() => RunOriginal();

    /// <summary>
    /// The same proxy verb with 1, from `NRestSiteRoom.ExtinguishFireIfAble`
    /// when the last rest option is spent -- so it is the SECOND rest-site
    /// crash, the one a player reaches a few seconds after the first if the
    /// first is fixed alone. Its whole body is that forward, so there is
    /// nothing else to lose by skipping it.
    /// </summary>
    [HarmonyPrefix]
    [HarmonyPatch(nameof(NRunMusicController.TriggerCampfireGoingOut))]
    private static bool TriggerCampfireGoingOutPrefix() => RunOriginal();

    /// <summary>
    /// THE BOSS PHASE CALL, and the one this row fixes UNPROVEN: no boss has
    /// been reached with the arm on. Eleven monster scripts forward a named
    /// parameter here at their phase changes -- `queen_progress`,
    /// `kaiser_crab_progress`, `the_kin_progress`, `knowledge_demon_progress`,
    /// `soulfysh_progress`, `test_subject_progress`, `vantom_progress`,
    /// `waterfall_giant_progress`, the Insatiable's own, plus `beckon` -- and
    /// every one of them lands on `set_parameter_by_name` against the released
    /// instance. The parameter shapes a track the arm has replaced, so skipping
    /// it loses nothing the player can hear.
    /// </summary>
    [HarmonyPrefix]
    [HarmonyPatch(nameof(NRunMusicController.UpdateMusicParameter))]
    private static bool UpdateMusicParameterPrefix() => RunOriginal();

    [HarmonyPostfix]
    [HarmonyPatch(nameof(NRunMusicController.UpdateMusic))]
    private static void UpdateMusicPostfix(NRunMusicController __instance) => Reassert(__instance);

    /// <summary>
    /// THE ROOM-AWARE SEAM, and the whole reason `EB-814` was a row rather than
    /// a ledger edit. `UpdateMusic` reads the act, the act's bank list and the
    /// run seed, and NOTHING about the room
    /// (`research/sts2-music-map-2026-09-17.md` sec.1) -- so a postfix there can
    /// answer "which nation" and can never answer "which room".
    ///
    /// `UpdateTrack()` is where the game asks. Its body is
    /// `UpdateTrack("Progress", (float)GetTrack(_runState.CurrentRoom.RoomType))`,
    /// and `CombatManager` calls it in exactly two places: `StartCombatInternal`
    /// right after `CombatBegan`, and the combat-won path. Those are the two
    /// moments a room's music character changes in the base game, so they are
    /// the two moments ours has to.
    ///
    /// THE ZERO-ARG OVERLOAD ONLY. `UpdateTrack` is overloaded -- there is a
    /// private `(string, float)` sibling that this one ends up calling -- so
    /// the empty `Type[]` is load-bearing: without it Harmony cannot tell which
    /// method is meant.
    /// </summary>
    [HarmonyPostfix]
    [HarmonyPatch(nameof(NRunMusicController.UpdateTrack), new Type[0])]
    private static void UpdateTrackPostfix(NRunMusicController __instance) => Reassert(__instance);

    /// <summary>
    /// A boss encounter's own event starting. `CombatManager.StartCombatInternal`
    /// calls this when `EncounterModel.HasBgm`, which is the ONLY place the base
    /// game swaps the whole FMOD event rather than moving a parameter -- ten
    /// encounters ship a `CustomBgm` (`act3_boss_queen` serves both Queen and
    /// Aeonglass). It fires BEFORE `UpdateTrack` in that method, so without this
    /// postfix the base game's boss theme would play for the gap between them.
    /// </summary>
    [HarmonyPostfix]
    [HarmonyPatch(nameof(NRunMusicController.PlayCustomMusic))]
    private static void PlayCustomMusicPostfix(NRunMusicController __instance) =>
        // FORCED, and this is the one exception `ShouldStop` needs. A boss's
        // own event is created WITHOUT `_currentTrack` being written -- the
        // method's whole body is `stop_music` then `update_music(customMusic)`
        // -- so the field-based idempotence would read "nothing to stop" and
        // leave the base game's boss theme playing under ours. Here we know a
        // live instance exists, because the method we are postfixing just made
        // one.
        Reassert(__instance, forceStop: true);

    /// <summary>
    /// The same event ending. Nothing in the managed assembly calls it today,
    /// which is exactly why it is patched: it is public, it restores the act
    /// track at `Progress` 7, and a game version that starts calling it would
    /// otherwise put the base music back underneath ours with nothing in any
    /// log to say so.
    /// </summary>
    [HarmonyPostfix]
    [HarmonyPatch(nameof(NRunMusicController.StopCustomMusic))]
    private static void StopCustomMusicPostfix(NRunMusicController __instance) => Reassert(__instance);

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
