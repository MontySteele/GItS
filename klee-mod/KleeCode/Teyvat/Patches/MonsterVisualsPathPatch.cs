using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Teyvat.Patches;

/// <summary>
/// THE STILL PORTRAIT -- `MegaCrit.Sts2.Core.Models.MonsterModel.get_VisualsPath`.
///
/// `VisualsPath` is `protected virtual` and is
/// `SceneHelper.GetScenePath("creature_visuals/" + Id.Entry.ToLowerInvariant())`
/// (`MonsterModel.cs:217`). It is overridden in exactly six places in the
/// whole game, all of them `BigDummy` and mocks, so no shipped act monster
/// forks it and this is a clean target. `MonsterModel.AssetPaths` is built
/// FROM it (`:219`), and `PreloadManager.LoadActAssets` /
/// `LoadRoomCombatAssets` consume `AssetPaths` -- so patching the getter fixes
/// preloading for free and there is no second registration to remember.
///
/// THE FALL-THROUGH IS THE POINT. `ResourceLoader.Exists` is asked before the
/// path is swapped, so a build whose pck was not rebuilt, or a dressing whose
/// portrait has not been drawn yet, draws the base rig rather than handing
/// `PreloadManager.Cache.GetScene` a dead path. `MonsterModel.CreateVisuals`
/// does have a `try`/`catch` that falls back to `creature_visuals/fallback`
/// (`:425-437`), but that fallback is the game's pink error body: it would
/// "work" and look like a bug.
///
/// WHAT THE STILL ACTUALLY IS: a `Sprite2D` under the `%Visuals` node of a
/// scene whose root BECOMES an `NCreatureVisuals` -- the same route
/// `pck-src/kokomi/model/bake_kurage.tscn` takes for a pet, and the same route
/// `Vfx/StaticPortraitIdle` documents for our characters out of combat. The
/// scene is `pck-src/teyvat/creature_visuals/hilichurl_guard.tscn` and its
/// texture is a placeholder PNG.
///
/// SWAPPING THE PATH IS ONLY HALF OF IT, and the missing half was EB-760.
/// `MonsterModel.CreateVisuals` CASTS the instantiated root to
/// `NCreatureVisuals`; a script-less scene's root is a plain `Node2D` and the
/// cast throws, which `CreateVisuals`'s catch turns into the pink error body.
/// `Teyvat/TeyvatVisuals.RegisterStillPortraits` is what makes the cast
/// succeed -- it registers every scene named in `TeyvatFrame.StillPortraits`
/// with BaseLib's auto-conversion, and the argument is written out in full
/// there. A path swapped without that registration draws the error scene.
///
/// THE SPINE DOORS IT TRIPS ARE IN THE REPORT, NOT IN THIS COMMENT, because
/// they are a decompile finding and not a decision this file makes. The short
/// version: `NCreatureVisuals._Ready` sets `SpineBody` only when the `%Visuals`
/// node's `GetClass()` is `"SpineSprite"`, so a `Sprite2D` leaves
/// `HasSpineAnimation` false, and `NCreature.cs:509` gates the whole animator
/// build on that flag -- which means `MonsterModel.GenerateAnimator(MegaSprite)`
/// and `SetupSkins(MegaSprite, MegaSkeleton)`, whose signatures demand a spine
/// object, are never called for a still body at all. The two doors with no
/// such gate are `NCreature.GetCurrentAnimationLength` and
/// `GetCurrentAnimationTimeRemaining`, which reach `SpineAnimation` with no
/// `HasSpineAnimation` check at the call site. Only a deploy can say whether
/// they bite.
/// </summary>
[HarmonyPatch(typeof(MonsterModel), "get_VisualsPath")]
internal static class MonsterModel_VisualsPath_TeyvatStill_Patch
{
    private static void Postfix(MonsterModel __instance, ref string __result)
    {
        var dressing = TeyvatFrame.CurrentActEntry;
        if (dressing == null || __instance == null)
        {
            return;
        }

        if (!TeyvatFrame.StillPortraits.TryGetValue((dressing, __instance.Id.Entry), out var scene))
        {
            return;
        }

        // The pck is merged by the game before [ModInitializer] runs
        // (KleePck's header), so this question has a true answer by the time
        // any monster is built.
        if (ResourceLoader.Exists(scene))
        {
            __result = scene;
        }
    }
}
