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
    /// decode.
    ///
    /// BOUNDED (`EB-158`). This was one plain Dictionary that only ever grew:
    /// every portrait a session had drawn stayed resident for as long as the
    /// process lived. A decoded portrait is 500x380 RGBA8 =
    /// <see cref="PortraitBytes"/> ~= 0.73 MB and `art/plan.tsv` carries 887
    /// card rows, so a long sitting that browsed the pools could pin ~645 MB
    /// of texture memory nothing was going to ask for again.
    ///
    /// LRU with capacity <see cref="CacheCapacity"/>, and the capacity is
    /// chosen off what the UI can want AT ONCE rather than off a memory
    /// target: the largest simultaneous demand is a browsed end-of-run deck
    /// (~40-60) alongside a combat hand, a shop row and a reward screen. 128
    /// clears that with headroom and bounds the cache at ~93 MB. Past it, an
    /// eviction costs ONE PNG decode the next time that card is shown -- which
    /// is the cost this cache exists to avoid per FRAME, not per re-show.
    /// </summary>
    private const int CacheCapacity = 128;

    /// <summary>Decoded size of one portrait: <see cref="PortraitWidth"/> x
    /// <see cref="PortraitHeight"/> x 4 bytes (RGBA8). It records the
    /// arithmetic behind <see cref="CacheCapacity"/>; no code reads it.
    /// </summary>
    private const int PortraitBytes = PortraitWidth * PortraitHeight * 4;

    private static readonly Dictionary<string, LinkedListNode<KeyValuePair<string, Texture2D>>>
        Cache = new();

    /// <summary>Most-recently-used first. The node IS the dictionary's value,
    /// so a hit is O(1) to find and O(1) to re-order.</summary>
    private static readonly LinkedList<KeyValuePair<string, Texture2D>> Recency = new();

    /// <summary>
    /// Rows that resolved to the blank -- or, with no engine behind the native
    /// calls, to null -- and they are kept OUT of the bounded cache on
    /// purpose. `EB-275`'s guarantee is that an uncovered row says so ONCE; an
    /// id evicted from the LRU and re-resolved would say it again, which would
    /// make a bounded cache a way to re-open a closed defect. These entries
    /// are a string each, bounded by the roster, and hold no texture: the
    /// blank is one shared instance.
    /// </summary>
    private static readonly HashSet<string> Unresolved = new();

    /// <summary>
    /// The card-art window's authored size. `tools/art_lint.py` bills every
    /// portrait against 500x380 and `tools/art_coverage.py` reads the same
    /// shape off disk, so the blank stands in at the size a real portrait
    /// would have occupied and the frame's layout cannot move under it.
    /// </summary>
    internal const int PortraitWidth = 500;
    internal const int PortraitHeight = 380;

    /// <summary>
    /// THE BLANK, and it is a colour rather than a picture -- `EB-275`.
    ///
    /// THE DEFECT. A card whose portrait resolved to null did not draw nothing;
    /// it sent the game to its OWN atlas for the card's id, which cannot
    /// contain a modded row, and the loader said so on EVERY DRAW:
    ///
    ///     [WARN] AtlasResourceLoader: Missing sprite 'kokomi/kleemod-proto_..'
    ///       in ... (requested: res://images/atlases/....tres)
    ///
    /// Dozens of lines per fight on `0.2.1921+proto.dirty`, for every prototype
    /// row with no staged image -- which the seat reported as reading "like a
    /// fault in the console" while the card itself looked merely blank. The
    /// per-frame half is the defect: nothing about the missing art changes
    /// between two frames, so nothing about it should be said twice.
    ///
    /// RETURNING A TEXTURE IS WHAT STOPS IT. BaseLib's portrait patch is
    /// `if (CustomPortrait != null) __result = CustomPortrait;` -- so a
    /// non-null answer is the only thing that keeps the game from falling
    /// through to its atlas. The blank is therefore not decoration: it is the
    /// answer that says "this row's portrait is resolved, and it is empty".
    ///
    /// IT AUTHORS NO ART, deliberately. One flat neutral field, allocated once
    /// and shared by every uncovered row -- no glyph, no label, no borrowed
    /// crop, nothing that could be mistaken for a portrait or reach
    /// `SOURCES.tsv`. The art bill is unchanged and is still read from
    /// `tools/art_coverage.py`; what this removes is the log, not the debt.
    /// The one-per-row line below is what keeps the debt audible.
    /// </summary>
    private static Texture2D? _blank;

    private static Texture2D? Blank()
    {
        if (_blank != null) return _blank;
        try
        {
            var image = Image.CreateEmpty(
                PortraitWidth, PortraitHeight, false, Image.Format.Rgba8);
            image.Fill(new Color(0.13f, 0.14f, 0.17f));
            _blank = ImageTexture.CreateFromImage(image);
        }
        catch (System.Exception e)
        {
            // A portrait getter runs inside card construction, and a card that
            // throws while being built is a lost run rather than a lost
            // picture. With no engine behind the native calls the honest
            // answer is the pre-EB-275 one -- null, and the game's atlas miss
            // back -- so this degrades rather than escalating.
            Log.Warn($"[{KleeMod.ModId}] could not build the blank card "
                   + $"portrait: {e.Message}");
        }
        return _blank;
    }

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
    /// Loads images/cards/&lt;cardId&gt;.png. cardId is the YAML sheet id
    /// (snake_case), which is what the art pipeline names files.
    ///
    /// NEVER NULL WHEN THE ENGINE IS UP (`EB-275`): a row with no staged image
    /// resolves to <see cref="Blank"/> ONCE, says so ONCE, and is cached, so
    /// the game's atlas is never asked for an id it cannot hold. See the
    /// blank's own comment for why a texture rather than a null is the fix.
    /// Null survives as the answer for the one case a texture cannot be made
    /// at all -- no Godot, or an image the engine refused to build from -- and
    /// that case is the pre-`EB-275` behaviour, unchanged.
    /// </summary>
    public static Texture2D? CardPortrait(string cardId)
    {
        if (Cache.TryGetValue(cardId, out var node))
        {
            Recency.Remove(node);
            Recency.AddFirst(node);
            return node.Value.Value;
        }
        // Resolved-to-blank rows never reach the LRU -- see Unresolved.
        if (Unresolved.Contains(cardId)) return Blank();

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

        // ONCE PER ROW, which is the whole of `EB-275`. The two Log.Warn lines
        // above are once-per-row because `Unresolved` below remembers the id
        // FOREVER -- the bounded LRU holds decoded textures only, so no
        // eviction can make an uncovered row warn a second time. What the
        // texture stops is the game's own per-frame atlas miss, and any
        // texture does it. The bill this leaves is `tools/art_coverage.py`'s
        // to state.
        if (texture != null)
        {
            Remember(cardId, texture);
            return texture;
        }

        Unresolved.Add(cardId);
        return Blank();
    }

    /// <summary>
    /// Insert at the head and drop the tail past <see cref="CacheCapacity"/>.
    /// The evicted entry is simply forgotten: the Texture2D is a managed
    /// RefCounted, so once the UI has let go of it Godot frees it -- there is
    /// nothing here to Dispose, and disposing a texture a card is still
    /// holding is how you get a blank card rather than a smaller heap.
    /// </summary>
    private static void Remember(string cardId, Texture2D texture)
    {
        Cache[cardId] = Recency.AddFirst(
            new KeyValuePair<string, Texture2D>(cardId, texture));
        while (Cache.Count > CacheCapacity)
        {
            var oldest = Recency.Last!;   // Count > capacity >= 1, so non-null
            Recency.RemoveLast();
            Cache.Remove(oldest.Value.Key);
        }
    }

    /// <summary>Test seam: forget the cache and the blank. The mod never calls
    /// it.</summary>
    internal static void ResetAll()
    {
        Cache.Clear();
        Recency.Clear();
        Unresolved.Clear();
        _blank = null;
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
