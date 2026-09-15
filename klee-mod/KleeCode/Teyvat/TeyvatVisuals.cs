using System;
using BaseLib.Extensions;
using Godot;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Combat;

namespace KleeMod.Teyvat;

/// <summary>
/// THE ARM'S STILL BODIES, TAUGHT TO BaseLib (EB-760).
///
/// WHAT WENT WRONG. `MonsterModel.CreateVisuals` does
/// `GetScene(VisualsPath).Instantiate&lt;NCreatureVisuals&gt;()` -- it CASTS
/// the instantiated root, it does not adapt it. `pck-src/teyvat/
/// creature_visuals/hilichurl_guard.tscn` is a script-less scene whose root is
/// a plain `Node2D` (the pck-src standing rule: behaviour attaches from C#,
/// never from an `ext_resource type="Script"` line), so the cast threw
/// `InvalidCastException`, `CreateVisuals`'s own catch swallowed it, and the
/// game drew the pink error creature -- which "works" and looks like a bug
/// (`review/records/teyvat-spike-proofs-2026-09-15.md` item 3).
///
/// WHAT MAKES THE CAST SUCCEED. BaseLib's `SceneConversionPatch` is a postfix
/// on `PackedScene.Instantiate(GenEditState)` that calls
/// `NodeFactory.TryAutoConvert`, and `TryAutoConvert` converts ONLY scenes
/// whose `res://` path is in `NodeFactory`'s `_registeredScenes` dictionary.
/// `RegisterSceneForConversion&lt;NCreatureVisuals&gt;()` is the one line that
/// puts a path in it (BaseLib 3.4.7, `BaseLib.Extensions.StringExtensions`
/// -> `NodeFactory.RegisterSceneType`); it logs
/// `Registered scene '...' for auto-conversion to NCreatureVisuals` at boot
/// and `Auto-converted '...' from Node2D to NCreatureVisuals` the first time
/// the scene is instantiated. Those two lines are the re-proof's evidence.
///
/// THE CONVERSION IS A REPARENT, NOT A RESHAPE. `NCreatureVisualsFactory`
/// constructs a bare `NCreatureVisuals`, moves every child of our `Node2D`
/// root onto it, copies the root's `CanvasItem`/`Node2D` properties, and then
/// generates only the named nodes the scene does not already carry. Our scene
/// carries `%Visuals`, `Bounds`, `%IntentPos` and `%CenterPos` -- the four
/// `NCreatureVisuals._Ready` fetches with `GetNode` rather than
/// `GetNodeOrNull` -- so the factory generates just `%FormVfx`; `%OrbPos`,
/// `%TalkPos` and `%PhobiaModeVisuals` fall through its switch as no-ops and
/// stay absent, which is exactly what `_Ready` tolerates.
///
/// AND `%Visuals` IS STILL NOT A SpineSprite. That is the whole point of the
/// item: `NCreatureVisuals._Ready` binds `SpineBody` only when `%Visuals`'s
/// `GetClass()` is literally `"SpineSprite"`, and the conversion does not
/// touch `%Visuals` -- it stays the `Node2D` holding a `Sprite2D`, so
/// `HasSpineAnimation` stays false and `NCreature.cs:509` never builds an
/// animator. What the still body draws it draws as a picture.
///
/// WHY HERE AND NOT FREE. Klee's, Kokomi's and Furina's combat scenes are
/// registered for us: `BaseLib.Patches.PostModInitPatch.RegisterSceneConversions`
/// runs on `ModelDb.Preload` and asks each model `as ISceneConversions`, which
/// a `CustomCharacterModel` implements. A DRESSED BASE-GAME MONSTER is not our
/// model at all -- `Patches/MonsterVisualsPathPatch` only rewrites the path a
/// shipped `MonsterModel` returns -- so nothing in that pass knows about this
/// scene and the registration has to be made by hand, exactly as
/// <c>BakeKuragePet.EnsureVisualsConverted</c> and
/// <c>FurinaStagePets.EnsureVisualsConverted</c> already do for an injected
/// pet model.
/// </summary>
public static class TeyvatVisuals
{
    private static bool _registered;

    /// <summary>
    /// Register every scene in <see cref="TeyvatFrame.StillPortraits"/> for
    /// auto-conversion. Called once from <c>KleeMod.Initialize</c>.
    ///
    /// AT `[ModInitializer]` TIME ON PURPOSE, and it is the opposite call from
    /// the loc merge next to it (EB-759): a registration is a write into a
    /// dictionary BaseLib owns from the moment it loads -- and BaseLib is a
    /// manifest dependency, so it loads before us -- and it only has to be in
    /// place before the scene is INSTANTIATED, which is first combat at the
    /// earliest. No table has to exist for this to be correct.
    ///
    /// THE `ResourceLoader.Exists` GUARD MIRRORS THE PATH PATCH'S. A build
    /// whose pck was not rebuilt has no such scene, `MonsterVisualsPathPatch`
    /// declines to swap the path for exactly that reason, and registering a
    /// dead path would only put a misleading line in the boot log. Skipping is
    /// loud rather than silent, because a missing still body is the single
    /// most likely cause of "the dressing did nothing".
    /// </summary>
    public static void RegisterStillPortraits()
    {
        if (!TeyvatFrame.Enabled || _registered)
        {
            return;
        }

        _registered = true;

        try
        {
            foreach (var scene in TeyvatFrame.StillPortraits.Values)
            {
                if (!ResourceLoader.Exists(scene))
                {
                    Log.Warn($"[{KleeMod.ModId}] teyvat: still portrait {scene} is not in the "
                           + "pck; the dressed monster will draw its base rig (rebuild with "
                           + "tools/build_pck.ps1).");
                    continue;
                }

                scene.RegisterSceneForConversion<NCreatureVisuals>();
            }
        }
        catch (Exception e)
        {
            // Same discipline as `TeyvatLoc.Inject`: the arm losing a picture
            // must never cost the mod its boot.
            Log.Error($"[{KleeMod.ModId}] teyvat: still-portrait registration failed, dressed "
                    + $"monsters will draw the error scene: {e}");
        }
    }
}
