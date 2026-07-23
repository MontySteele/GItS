using System.Collections.Generic;
using Godot;
using MegaCrit.Sts2.Core.Logging;

namespace KleeMod;

/// <summary>
/// Resolves res:// paths inside klee.pck. The GAME loads the pack for us:
/// ModManager calls ProjectSettings.LoadResourcePack on mods/klee/klee.pck
/// whenever the manifest says has_pck ("Loading Godot PCK" in ModManager),
/// and it does so while reading the mod -- before [ModInitializer] runs --
/// so by the time any code here executes the pack is merged into res://.
///
/// The pack is built by tools/build_pck.ps1 with the MegaDot editor (the
/// game's own Godot fork, so the pack format and .ctex import format match
/// the runtime). Editor-imported PNGs load as CompressedTexture2D, which is
/// what the character-select surfaces demand and what a runtime-built
/// ImageTexture can never satisfy (see KleeArt's SCOPE note).
///
/// Everything funnels through Path(), which returns null when the resource
/// is missing (pck not built, pck not deployed, typo) so callers fall back
/// to base-game behavior instead of handing the engine a dead path. Lookups
/// are cached because these getters sit on per-frame UI paths; the miss is
/// logged once, not per frame.
/// </summary>
internal static class KleePck
{
    private static readonly Dictionary<string, bool> Known = new();

    /// <summary>"klee/ui/foo.png" -> "res://klee/ui/foo.png", or null if absent.</summary>
    public static string? Path(string relative)
    {
        var path = "res://" + relative;
        if (!Known.TryGetValue(path, out var exists))
        {
            exists = ResourceLoader.Exists(path);
            Known[path] = exists;
            if (!exists)
            {
                Log.Warn($"[{KleeMod.ModId}] pck resource missing: {path} "
                       + "(klee.pck absent or stale? build with tools/build_pck.ps1)");
            }
        }
        return exists ? path : null;
    }

    /// <summary>
    /// Boot telemetry: one godot.log line proving whether the pack merged and
    /// that its textures come back as the type the select screen casts to.
    /// </summary>
    public static void LogStatus()
    {
        const string probe = "res://klee/ui/select_portrait.png";
        if (ResourceLoader.Exists(probe))
        {
            var type = ResourceLoader.Load<Resource>(probe)?.GetType().Name ?? "null";
            Log.Info($"[{KleeMod.ModId}] klee.pck merged: {probe} loads as {type}");
        }
        else
        {
            Log.Warn($"[{KleeMod.ModId}] klee.pck NOT merged ({probe} unresolvable); "
                   + "select/power/relic art will use base-game fallbacks.");
        }
    }
}
