using Godot;
using MegaCrit.Sts2.Core.Logging;

namespace KleeMod.Diagnostics;

/// <summary>
/// Boot telemetry for every convention scene the roster ships in klee.pck
/// (animation sprint 1, A3 — PERMANENT, not scaffolding). A scene that misses
/// its res:// path falls back to base behavior and "looks like nothing
/// happened"; this makes the miss loud at boot instead of invisible mid-run.
///
/// One line per scene: path, found/missing, and the ROOT NODE TYPE read from
/// SceneState — deliberately without instantiating, because instantiation is
/// what triggers BaseLib's conversion postfix and this logger must never have
/// side effects. The root type printed here is the pre-conversion type (e.g.
/// Node2D for combat.tscn); BaseLib's own "Auto-converted ..." log line is
/// the post-conversion half of the story.
///
/// Also logs the pck build id stamped by tools/build_pck.ps1, so a stale pack
/// (editor re-export forgotten after a scene edit) announces itself.
/// </summary>
internal static class KleeSceneTelemetry
{
    private static readonly string[] ConventionScenes =
    {
        "klee/model/combat.tscn",
        "klee/model/combat_visuals.tscn",
        "klee/model/rest_character.tscn",
        "klee/model/character_sprite.tscn",
        "klee/ui/character_icon.tscn",
        "klee/ui/char_select_bg_klee.tscn",
        "furina/model/combat_visuals.tscn",
        "furina/model/rest_character.tscn",
        "furina/model/merchant_character.tscn",
        "furina/ui/character_icon.tscn",
        "furina/ui/char_select_bg_furina.tscn",
    };

    public static void LogStatus()
    {
        const string idPath = "res://klee/build_id.tres";
        if (ResourceLoader.Exists(idPath))
        {
            var id = ResourceLoader.Load<Resource>(idPath)?.ResourceName ?? "unreadable";
            Log.Info($"[{KleeMod.ModId}] pck build id: {id}");
        }
        else
        {
            Log.Warn($"[{KleeMod.ModId}] pck has no build id "
                   + "(pre-animation-sprint pack? rebuild with tools/build_pck.ps1)");
        }

        foreach (var relative in ConventionScenes)
        {
            var path = "res://" + relative;
            if (!ResourceLoader.Exists(path))
            {
                Log.Warn($"[{KleeMod.ModId}] convention scene MISSING: {path} "
                       + "(falls back to base behavior — rebuild/redeploy the pck)");
                continue;
            }

            var scene = ResourceLoader.Load<PackedScene>(path);
            var root = scene?.GetState() is { } state && state.GetNodeCount() > 0
                ? state.GetNodeType(0).ToString()
                : "unreadable";
            Log.Info($"[{KleeMod.ModId}] convention scene ok: {path} root={root}");
        }
    }
}
