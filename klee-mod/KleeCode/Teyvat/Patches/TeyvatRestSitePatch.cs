using System;
using System.Collections.Concurrent;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Teyvat.Patches;

/// <summary>
/// THE REST SITE: THE GAME'S OWN CAMPFIRE, WEARING OUR PLATE.
///
/// THE DEFECT THIS FILE IS (2026-09-17, [USER], reproduced twice). A BASE
/// character -- the Silent -- entering a rest site on a Teyvat face act
/// HARD-CRASHED the game. Native, no managed trace, no exception anywhere: the
/// log simply ended at `Preloading 'RestSite Room' Complete`. Klee never
/// crashed there, which is why fourteen deploy proofs missed it.
///
/// WHY. We shipped our own rest-site scene per face -- a `Control` root with a
/// `RestSiteBG` `TextureRect` over our 1382x648 plate and an EMPTY
/// `%RestSiteLighting` `Control`. Empty satisfied the only thing we knew to
/// satisfy: `NRestSiteRoom._Ready` does
/// `control.GetNode&lt;Control&gt;("%RestSiteLighting")` -- `GetNode`, not
/// `GetNodeOrNull` -- and then writes `Visible` on it. But the base game keeps
/// the WHOLE campfire inside that node: `RestSiteGroundLighting`
/// (`NParticleSystemUpscaler`), seven `WallLight` sprites, the log shadows and
/// log sprites, `FireLight`, `little_light` particles, `SteppedFire` (a
/// `Node2D` running `NRestSiteFireVfx` over smoke and the `SteppedFireMix`
/// / `Add` sprites), `sparks big`, `light_front`, the log highlights. A base
/// character's campfire figure is a Spine rig whose `_Ready`
/// (`Nodes.RestSite/NRestSiteCharacter`) plays `"&lt;zone&gt;_loop"` by act
/// index and evidently reaches into that tree. Ours gave it nothing and the
/// engine died below the managed layer, where nothing we can patch runs.
///
/// THE FIX IS TO STOP AUTHORING A REST SCENE AT ALL. The six
/// `klee-mod/pck-src/scenes/rest_site/*.tscn` are deleted.
/// <see cref="ActModel_RestSiteBackgroundPath_TeyvatAlias_Patch"/> below sends
/// every face to its BASE zone's scene -- unconditionally, not behind
/// `HasDressedAssets` like the combat background and the map, because there is
/// no longer any state of the pack in which we would rather have our own --
/// and <see cref="ActModel_CreateRestSiteBackground_TeyvatPlate_Patch"/> then
/// swaps our plate into that scene's own `RestSiteBG`. The campfire, the logs
/// and every particle in `%RestSiteLighting` are the game's, untouched, exactly
/// as a base character's rig expects to find them.
///
/// `docs/current/operations/act-assets.md` carries the row; the proof the lane
/// owes is a Silent at a Mondstadt campfire.
/// </summary>
internal static class TeyvatRestSite
{
    /// <summary>
    /// Log a given line ONCE per session. These postfixes run every time a
    /// rest site is built, and a miss here is a picture rather than a defect
    /// -- worth one line, never worth a line a floor.
    /// </summary>
    private static readonly ConcurrentDictionary<string, bool> _said = new();

    private static void SayOnce(string key, string message)
    {
        if (_said.TryAdd(key, true))
        {
            Log.Warn($"[{KleeMod.ModId}] teyvat: {message}");
        }
    }

    /// <summary>
    /// DRESS THE BASE ZONE'S REST SCENE, and dress nothing that moves.
    ///
    /// Three writes and a visibility pass, in that order:
    ///
    ///   * the plate into `RestSiteBG.Texture`, only when the resource is
    ///     really in the pack;
    ///   * `ExpandMode = IgnoreSize` and `StretchMode = Scale`, which is what
    ///     our deleted scene's `expand_mode = 1` meant -- the base rect is
    ///     2764.8 x 1296 and the plate 1382x648, the same exact-aspect halving
    ///     every act plate in this arm uses. The node's ANCHORS AND OFFSETS
    ///     are not touched: the plate fills the rect the base art filled.
    ///   * the zone-specific decoration in front of it hidden, by
    ///     <see cref="TeyvatActAssets.HiddenForPlate"/>, over the root's
    ///     DIRECT children only.
    ///
    /// NOTHING UNDER `%RestSiteLighting` IS REACHED, by construction: the walk
    /// does not recurse. The logs (`RestSiteLLog`, `RestSiteRLog`,
    /// `RestSiteFireLogs`) are root-level and deliberately not on the list --
    /// they are where the fire sits.
    ///
    /// NEVER THROWS. This runs while the room is being built, and a throw in a
    /// Harmony postfix would take the room with it -- which is the failure
    /// mode this whole file exists to remove.
    /// </summary>
    internal static void Dress(string entry, Control scene)
    {
        try
        {
            var id = entry.ToLowerInvariant();
            var bg = scene.GetNodeOrNull<TextureRect>(TeyvatActAssets.RestSiteBgNode);
            if (bg == null)
            {
                SayOnce($"nobg:{id}",
                        $"{entry}'s base rest scene has no "
                      + $"{TeyvatActAssets.RestSiteBgNode} TextureRect; the campfire is "
                      + "drawn untouched and the face keeps the base zone's plate.");
                return;
            }

            var plate = TeyvatActAssets.RestSitePlatePath(id);
            if (!ResourceLoader.Exists(plate))
            {
                SayOnce($"noplate:{id}",
                        $"{entry} has no rest-site plate at {plate}; the base zone's own "
                      + "art is drawn (run tools/gen_act_placeholders.py, then "
                      + "tools/build_pck.ps1).");
                return;
            }

            if (ResourceLoader.Load<Texture2D>(plate) is not { } texture)
            {
                SayOnce($"badplate:{id}", $"{entry}'s rest-site plate {plate} did not load.");
                return;
            }

            bg.Texture = texture;
            bg.ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize;
            bg.StretchMode = TextureRect.StretchModeEnum.Scale;

            foreach (var child in scene.GetChildren())
            {
                if (child is CanvasItem item
                    && TeyvatActAssets.HiddenForPlate(child.Name.ToString()))
                {
                    item.Visible = false;
                }
            }
        }
        catch (Exception e)
        {
            // `TeyvatLoc.Inject`'s discipline: the arm losing a picture must
            // never cost the room.
            SayOnce($"threw:{entry}", $"{entry}'s rest-site plate pass failed: {e}");
        }
    }
}

/// <summary>
/// `ActModel.get_RestSiteBackgroundPath` -- the alias, and it is
/// UNCONDITIONAL.
///
/// The property is `public string RestSiteBackgroundPath` over
/// `FilePathIdentifier`, non-virtual like the other four
/// (`ActModel.cs:52-64`), so a postfix on its getter is the only seam. It runs
/// AFTER `ActFilePathIdentifierPatch` has had its say and overwrites whatever
/// that produced, which is what "always the base zone" means: a face with a
/// complete asset set of its own still gets `overgrowth` / `hive` / `glory`
/// here, while its combat background and map keep pointing at our files.
///
/// `ActModel.AssetPaths` reads this getter for the act's preload as well as
/// the room that draws it, so one postfix covers both and the preload can
/// never cache a failure for a scene we no longer ship.
/// </summary>
[HarmonyPatch(typeof(ActModel), "get_RestSiteBackgroundPath")]
internal static class ActModel_RestSiteBackgroundPath_TeyvatAlias_Patch
{
    private static void Postfix(ActModel __instance, ref string __result)
    {
        if (!TeyvatFrame.Enabled || __instance == null)
        {
            return;
        }

        if (TeyvatActAssets.BaseRestSiteScenePath(__instance.Id.Entry) is { } path)
        {
            __result = path;
        }
    }
}

/// <summary>
/// `ActModel.CreateRestSiteBackground` -- our plate into the game's campfire.
///
/// SIGNATURE, verified against the installed `sts2.dll` rather than assumed:
/// `public Godot.Control CreateRestSiteBackground()`, instance, no parameters,
/// non-virtual. `KleeTests.TeyvatFrameTests` pins that with `AccessTools` so a
/// game patch that moves it fails a test instead of silently un-arming the
/// postfix.
///
/// Patched at the CREATE rather than at the path getter because the path is
/// already the base zone's by then -- what is wanted is the instantiated node,
/// after the engine has built it and before the room adds it.
/// </summary>
[HarmonyPatch(typeof(ActModel), "CreateRestSiteBackground")]
internal static class ActModel_CreateRestSiteBackground_TeyvatPlate_Patch
{
    private static void Postfix(ActModel __instance, Control __result)
    {
        if (!TeyvatFrame.Enabled || __instance == null || __result == null)
        {
            return;
        }

        var entry = __instance.Id.Entry;
        if (!TeyvatFrame.IsDressing(entry))
        {
            return;
        }

        TeyvatRestSite.Dress(entry, __result);
    }
}
