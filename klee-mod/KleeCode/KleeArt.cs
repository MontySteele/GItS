using System.Collections.Generic;
using System.IO;
using System.Reflection;
using Godot;
using MegaCrit.Sts2.Core.Logging;

namespace KleeMod;

/// <summary>
/// Loads card art from loose PNGs shipped alongside the mod dll, with no .pck.
///
/// WHY THIS WORKS: BaseLib's card-portrait patch prefers an object over a path
/// (<c>if (customCardModel.CustomPortrait != null) __result = ...CustomPortrait;</c>),
/// so any Texture2D will do -- including one built at runtime. Downfall ships
/// this exact technique in production (Image.Load on an absolute OS path, then
/// ImageTexture.CreateFromImage), which is what proves non-res:// paths load.
///
/// SCOPE: card portraits only. The character-select surface is path-bound to
/// res:// and CharacterSelectIcon returns CompressedTexture2D, which an
/// ImageTexture cannot satisfy even via Harmony. Character art still needs a
/// real .pck; see DECISIONS.md.
/// </summary>
internal static class RosterArt
{
    /// <summary>
    /// Cached because CustomPortrait is a property getter the UI hits
    /// repeatedly -- rebuilding a texture per access would be a per-frame
    /// decode. Null is cached too, so a missing file is not retried forever.
    /// </summary>
    private static readonly Dictionary<string, Texture2D?> Cache = new();

    private static string? _imageRoot;

    /// <summary>
    /// Absolute path to the images folder next to our dll. deploy.ps1 stages
    /// images/cards/*.png into the deployed mod directory.
    /// </summary>
    private static string ImageRoot
    {
        get
        {
            if (_imageRoot != null) return _imageRoot;

            var dllPath = Assembly.GetExecutingAssembly().Location;
            var modDir = Path.GetDirectoryName(dllPath) ?? string.Empty;
            _imageRoot = Path.Combine(modDir, "images");
            return _imageRoot;
        }
    }

    /// <summary>
    /// Loads images/cards/&lt;cardId&gt;.png, or null if absent. cardId is the
    /// YAML sheet id (snake_case), which is what the art pipeline names files.
    /// </summary>
    public static Texture2D? CardPortrait(string cardId)
    {
        if (Cache.TryGetValue(cardId, out var cached)) return cached;

        var path = Path.Combine(ImageRoot, "cards", cardId + ".png");
        Texture2D? texture = null;

        // Guard with FileAccess.FileExists exactly as Downfall does, so a
        // missing file is a null rather than a Godot error spew.
        if (Godot.FileAccess.FileExists(path))
        {
            var image = new Image();
            if (image.Load(path) == Error.Ok)
            {
                texture = ImageTexture.CreateFromImage(image);
            }
            else
            {
                Log.Warn($"[{KleeMod.ModId}] Image.Load failed for {path}");
            }
        }
        else
        {
            Log.Warn($"[{KleeMod.ModId}] No card art at {path}");
        }

        Cache[cardId] = texture;
        return texture;
    }
}

/// <summary>
/// Compatibility name for Klee's already-generated and hand-written cards.
/// New character profiles use <see cref="RosterArt"/> directly.
/// </summary>
internal static class KleeArt
{
    public static Texture2D? CardPortrait(string cardId) =>
        RosterArt.CardPortrait(cardId);
}
