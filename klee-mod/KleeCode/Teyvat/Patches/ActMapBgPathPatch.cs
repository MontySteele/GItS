using HarmonyLib;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Teyvat.Patches;

/// <summary>
/// THE MAP GROUND GOES BACK TO THE GAME'S OWN (2026-09-17, [USER]'s read of
/// the shipped frame: *"the map is harder to read than the normal Slay the
/// Spire 2 map ... perhaps we went off the rails replacing the map background
/// with Genshin images"*).
///
/// WHAT WAS BUILT AND WHY IT HAD TO COME OUT. `ActModel.MapTopBgPath`,
/// `MapMidBgPath` and `MapBotBgPath` are non-virtual expression-bodied
/// properties over `FilePathIdentifier`
/// (`ActModel.cs:52-64`; `Patches/ActFilePathIdentifierPatch` is the standing
/// note on that), so a face's map ground is read from
/// `packed/map/map_bgs/&lt;face&gt;/map_{top,middle,bottom}_&lt;face&gt;.png`
/// the moment its own asset set exists and the alias postfix stands down. The
/// 2026-09-17 act-plate bill filled those eighteen paths with real location
/// stills. They are beautiful and they are unreadable: the map's node icons,
/// its travelled/untravelled path lines and its legend are drawn for the base
/// game's low-contrast painted ground, and a bright city plate underneath them
/// takes the contrast away everywhere at once.
///
/// THE REVERT IS THIS FILE AND NOT A DELETION. Removing the eighteen plan rows
/// only empties the directory; the getters still derive the face's own path,
/// `PreloadManager.LoadActAssets` still asks for it, and the map screen then
/// draws nothing at all. So the three getters are sent back to the BASE ZONE's
/// files -- `mondstadt` -> `overgrowth`, `natlan` -> `hive` -- which is exactly
/// what <see cref="TeyvatFrame.AssetAlias"/> already says and what the face saw
/// before the bill landed.
///
/// A STRING SWAP, NOT A REBUILT PATH, and that is deliberate. The prefix, the
/// extension and whatever `ImageHelper` does around them are the game's, read
/// from a decompile this file does not want to depend on; the ONLY thing in the
/// string that is ours is the identifier, and it appears in both the directory
/// and the file name. Replacing every occurrence of the face id with the zone
/// id therefore produces the base zone's path whatever the surrounding format
/// is, and produces it identically for all three getters.
///
/// THE DRESSED PATH STILL WINS WHERE IT EXISTS, the
/// <see cref="AncientPicture.Borrow"/> shape: if a build ever does ship a
/// readable face-specific map ground, it is in the pack, `ResourceLoader.Exists`
/// answers true, and this postfix stands down for that face with no code change.
/// What replaces the plates today is an OVERLAY drawn on top of the game's own
/// ground -- <see cref="KleeMod.Teyvat.MapOverlay"/> -- which keeps the map the
/// player already reads and dresses its margins.
///
/// NEVER THROWS, and with `TeyvatFrame.Enabled` false every postfix returns on
/// its first line, so an arm-off build is byte-identical.
/// </summary>
public static class ActMapBgPath
{
    /// <summary>
    /// The base zone's spelling of <paramref name="path"/>, or null when this
    /// act is not one of the arm's faces.
    ///
    /// PURE, so both directions are pinned headlessly: `KleeTests` cannot
    /// construct an `ActModel`, but it can ask this function what it does to a
    /// string.
    /// </summary>
    public static string? BaseZonePath(string? entry, string? path)
    {
        if (!TeyvatFrame.Enabled || entry == null || path == null)
        {
            return null;
        }

        if (!TeyvatFrame.AssetAlias.TryGetValue(entry, out var zone))
        {
            return null;
        }

        var face = entry.ToLowerInvariant();
        if (face == zone || !path.Contains(face))
        {
            // Either the alias postfix already rewrote the identifier (so the
            // path is the zone's), or a game patch moved the format out from
            // under us. Both are "leave it alone", never "guess".
            return null;
        }

        return path.Replace(face, zone);
    }
}

/// <summary>The top third of the map wall.</summary>
[HarmonyPatch(typeof(ActModel), "get_MapTopBgPath")]
internal static class ActModel_MapTopBgPath_TeyvatGround_Patch
{
    private static void Postfix(ActModel __instance, ref string __result) =>
        MapGroundPostfix.Apply(__instance, ref __result);
}

/// <summary>The middle third.</summary>
[HarmonyPatch(typeof(ActModel), "get_MapMidBgPath")]
internal static class ActModel_MapMidBgPath_TeyvatGround_Patch
{
    private static void Postfix(ActModel __instance, ref string __result) =>
        MapGroundPostfix.Apply(__instance, ref __result);
}

/// <summary>The bottom third.</summary>
[HarmonyPatch(typeof(ActModel), "get_MapBotBgPath")]
internal static class ActModel_MapBotBgPath_TeyvatGround_Patch
{
    private static void Postfix(ActModel __instance, ref string __result) =>
        MapGroundPostfix.Apply(__instance, ref __result);
}

/// <summary>
/// The one body the three postfixes share. Keyed on the INSTANCE's id and not
/// on the run's current act, for the reason
/// `Patches/ActFilePathIdentifierPatch` states: the map screen, the preload and
/// a run-history row all read an act that need not be the current one.
/// </summary>
internal static class MapGroundPostfix
{
    internal static void Apply(ActModel? instance, ref string result)
    {
        if (instance == null)
        {
            return;
        }

        var fallback = ActMapBgPath.BaseZonePath(instance.Id.Entry, result);
        if (fallback == null)
        {
            return;
        }

        AncientPicture.Borrow(ref result, fallback);
    }
}
