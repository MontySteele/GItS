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
        "furina/model/combat.tscn",
        "furina/model/combat_visuals.tscn",
        "furina/model/rest_character.tscn",
        "furina/model/merchant_character.tscn",
        "furina/ui/character_icon.tscn",
        "furina/ui/char_select_bg_furina.tscn",
        "furina/ui/salon_stage.tscn",
        // EB-40: her own Hydro energy orb. Klee and Kokomi still return the
        // base game's ironclad counter, so a miss here is Furina-only and
        // otherwise silent -- she just keeps wearing the red orb.
        "furina/ui/energy_counter.tscn",
        // Kokomi. combat.tscn is EXPECTED MISSING until her art pass lands --
        // she runs on the combat_visuals.tscn fallback, which the pck builder
        // fills from Klee. Listed anyway, because "expected missing" and
        // "silently missing" are the same thing at 2am and only one of them
        // says so in the log.
        "kokomi/model/combat.tscn",
        "kokomi/model/combat_visuals.tscn",
        "kokomi/model/rest_character.tscn",
        "kokomi/model/merchant_character.tscn",
        "kokomi/ui/character_icon.tscn",
        "kokomi/ui/char_select_bg_kokomi.tscn",
        "shared/gauge.tscn",
        // EB-53/N1: the end-of-turn attribution docket, shared across seats.
        "shared/turn_end_docket.tscn",
        "klee/vfx/bomb_lob.tscn",
        "klee/vfx/dodoco_pop.tscn",
        "furina/vfx/spotlight_shine.tscn",
    };

    /// <summary>
    /// Node names a scene MUST carry for a C# bridge to find anything, checked
    /// from SceneState so this stays side-effect free.
    ///
    /// These are the silent failures: every bridge here is written to be inert
    /// when its node is absent (GetNodeOrNull, no throw), which is the right
    /// runtime posture and the wrong debugging one — a renamed or dropped node
    /// turns the feature off and looks exactly like "the feature does nothing".
    /// %Facing is the live example: without it CreatureFacing no-ops and the
    /// character simply never turns, with nothing in the log to say why.
    /// </summary>
    private static readonly (string Scene, string Node)[] RequiredNodes =
    {
        ("klee/model/combat.tscn", "Facing"),
        ("furina/model/combat.tscn", "Facing"),
        ("klee/model/combat.tscn", "AnimationTree"),
        ("furina/model/combat.tscn", "AnimationTree"),
        ("furina/ui/salon_stage.tscn", "RibbonLabel"),
        ("shared/gauge.tscn", "ValueLabel"),
        // Without ChipLabel1 the docket renders slots with no numbers, which
        // is the exact silent failure this table exists to make loud.
        ("shared/turn_end_docket.tscn", "ChipLabel1"),
        // EB-40, and NOT of the inert kind the paragraph above describes:
        // NEnergyCounter._Ready GetNodes all five non-null, so a rename here
        // does not quietly turn a feature off -- it throws while the combat
        // HUD is being built. Listed so the boot log names the missing node
        // before a combat does.
        ("furina/ui/energy_counter.tscn", "Label"),
        ("furina/ui/energy_counter.tscn", "Layers"),
        ("furina/ui/energy_counter.tscn", "RotationLayers"),
        ("furina/ui/energy_counter.tscn", "EnergyVfxBack"),
        ("furina/ui/energy_counter.tscn", "EnergyVfxFront"),
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

        foreach (var (relative, node) in RequiredNodes)
        {
            var path = "res://" + relative;
            if (!ResourceLoader.Exists(path))
            {
                continue;   // already reported MISSING above; don't say it twice
            }

            if (ResourceLoader.Load<PackedScene>(path)?.GetState() is not { } state)
            {
                continue;
            }

            var found = false;
            for (var i = 0; i < state.GetNodeCount() && !found; i++)
            {
                found = state.GetNodeName(i) == node;
            }

            if (!found)
            {
                Log.Warn($"[{KleeMod.ModId}] {path} has no node named \"{node}\" — "
                       + "the bridge that looks for it will silently do nothing. "
                       + "Rebuild the pck, or the scene lost the node.");
            }
        }
    }
}
