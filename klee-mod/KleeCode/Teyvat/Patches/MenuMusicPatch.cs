using HarmonyLib;
using MegaCrit.Sts2.Core.Nodes.Audio;

namespace KleeMod.Teyvat.Patches;

/// <summary>
/// THE MENU SEAM -- `MegaCrit.Sts2.Core.Nodes.Audio.NAudioManager.PlayMusic`
/// and `.StopMusic` (`EB-814`).
///
/// WHY THIS IS A SECOND PATCH CLASS AND NOT A ROW IN `RunMusicPatch`. The main
/// menu is not a run. `NRunMusicController` does not exist there --
/// `NRunMusicController.Instance` is `NRun.Instance?.RunMusicController`, and
/// `NRun` is instantiated when a run starts -- so nothing in the run patch can
/// ever fire on the menu. The menu's music goes out through the GLOBAL audio
/// manager instead: `NMainMenu._Ready` calls
/// `NAudioManager.Instance?.PlayMusic("event:/music/menu_update")`, and a
/// `menu_progress` string parameter moves between `"main"` and `"timeline"`
/// inside that one event (`research/sts2-music-map-2026-09-17.md` sec.2).
///
/// KEYED ON THE EXACT EVENT STRING, AND THAT IS A SAFETY PROPERTY RATHER THAN
/// A SHORTCUT. `PlayMusic` has exactly two callers outside its own class: the
/// menu, and `CreatureCmd` playing `event:/temp/sfx/game_over` when every
/// player is dead. A patch that fired on "any PlayMusic" would swallow the
/// death stinger, which the run frame has no counterpart for and no reason to
/// own (media.md sec.7). So the string is compared, not the call site.
///
/// THE HOST IS THE AUDIO MANAGER ITSELF, which outlives the menu and every
/// screen, and the node is `TeyvatMusic.PlayerNodeName` exactly as it is under
/// the run controller -- so `Stop` finds it by the same name and an operator
/// reading the remote scene tree sees one convention, not two.
///
/// AND `menu` IS A GLOBAL SLOT, so it resolves with no dressing at all:
/// `TeyvatFrame.MediaScene` answers the bare name before it ever asks which
/// face the run is standing in, because on this path there is no run. It also
/// has no fallback -- nothing filed under `menu` means the game's own theme
/// plays, untouched.
/// </summary>
[HarmonyPatch(typeof(NAudioManager))]
internal static class NAudioManager_TeyvatMenu_Patch
{
    /// <summary>
    /// The one event this patch answers to. A literal rather than a reference
    /// to the game's own constant because there is no constant: `NMainMenu`
    /// spells it inline at its single call site, and `Core.Audio/FmodSfx.cs`
    /// carries sfx paths only.
    /// </summary>
    internal const string MenuEvent = "event:/music/menu_update";

    /// <summary>
    /// Re-entrancy guard, and it is `RunMusicPatch`'s for the same reason: the
    /// `PlayMusic` postfix calls `StopMusic` itself, which fires the `StopMusic`
    /// postfix below, whose job is to tear down the player `PlayMusic` just
    /// built. A plain static, not `[ThreadStatic]` -- the whole audio path is
    /// Godot's main thread.
    /// </summary>
    private static bool _inArmedStop;

    [HarmonyPostfix]
    [HarmonyPatch(nameof(NAudioManager.PlayMusic))]
    private static void PlayMusicPostfix(NAudioManager __instance, string music)
    {
        if (!TeyvatFrame.Enabled || __instance == null || music != MenuEvent)
        {
            return;
        }

        // No act entry: the menu has none, and a global slot never asks for one.
        if (!TeyvatMusic.Play(__instance, null, TeyvatMusic.SlotMenu))
        {
            return;
        }

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
    /// NOT gated on <see cref="TeyvatFrame.Enabled"/>, deliberately, exactly as
    /// the run patch's teardown is not: a session that turns the arm off must
    /// still get our node torn down the next time the game stops its music.
    /// Cleanup never sits behind the flag that created the thing being cleaned
    /// up. Every screen that leaves the menu into a run calls this
    /// (`NCharacterSelectScreen`, the four load screens, `NMainMenu`'s own
    /// continue path), so the menu track dies where the menu track dies.
    /// </summary>
    [HarmonyPostfix]
    [HarmonyPatch(nameof(NAudioManager.StopMusic))]
    private static void StopMusicPostfix(NAudioManager __instance)
    {
        if (_inArmedStop)
        {
            return;
        }

        TeyvatMusic.Stop(__instance);
    }
}
