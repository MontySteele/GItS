using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Assets;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Map;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Rooms;

namespace KleeMod.Teyvat.Patches;

/// <summary>
/// THE DRESSED ANCIENT'S PICTURE -- and its two map icons and its two
/// run-history icons, which are the same problem four more times.
///
/// THE PATHS ARE DERIVED FROM THE ID AND THERE IS NO OTHER SEAM, exactly as
/// `EventPortraitPatch` found for a converted event. An Ancient draws from
/// five derived paths and not one of them is `virtual`:
///
///   `EventModel.BackgroundScenePath`              -- THE PICTURE. `private`,
///       `SceneHelper.GetScenePath("events/background_scenes/" +
///       Id.Entry.ToLowerInvariant())`. `NAncientEventLayout` instantiates it
///       into `%AncientBgContainer`, and `EventModel.GetAssetPaths` adds it to
///       the act's PRELOAD list for every `EventLayoutType.Ancient` -- so, as
///       with the portrait, the getter is the target and `CreateBackgroundScene`
///       is not: patching the create call would leave the preload asking for a
///       dead path and cache the failure.
///   `AncientEventModel.MapIconPath` / `MapIconOutlinePath` -- both `private`,
///       both `"packed/map/ancients/ancient_node_" + entry.ToLower()`, both
///       reached through `MapNodeAssetPaths`, which `ActModel` preloads.
///   `AncientEventModel.RunHistoryIconOutlinePath` -- `private`,
///       `"ui/run_history/" + entry.ToLower() + "_outline.png"`.
///   `ImageHelper.GetRoomIconPath(..., Id)` -- a STATIC, not a getter, which is
///       why it is patched by name below rather than as a property. Its suffix
///       is `GetRoomIconSuffix`'s `modelId.Entry.ToLowerInvariant()`.
///
/// R275 COMMISSIONS NO ART, so every one of the five is sent back to the BASE
/// Ancient's own file. A dressed Neow draws Neow.
///
/// THE FALL-THROUGH IS THE POINT, again. `ResourceLoader.Exists` is asked of
/// the DRESSED path first and the borrow happens only when it is absent, so
/// the day `dvalin_mondstadt.tscn` is in the pack this patch stands down for
/// that one entry on its own, with no table edit and no code change. That is
/// the art bill R275 defers, and this is the seam it lands on.
///
/// SCOPED TO THE TABLE AND TO THE ARM, and the table is the generator's --
/// `TeyvatGeneratedAncients.BaseEntries`, dressed entry to base entry, the
/// same dictionary the loc alias pass reads. An Ancient with no row (every
/// base Ancient, always) gets its own path back untouched, and with
/// `TeyvatFrame.Enabled` false every postfix returns on its first line.
///
/// NEVER THROWS. `ResourceLoader.Exists` answers false for a malformed path
/// rather than raising, and no postfix here has another statement that can --
/// which matters because these getters are reached while a room is being built
/// and a throw inside a Harmony postfix would take the room with it.
/// </summary>
public static class AncientPicture
{
    /// <summary>The base Ancient's entry for a dressed one, or null. One
    /// lookup, shared by all five postfixes.</summary>
    public static string? BaseEntry(string? dressedEntry)
    {
        if (!TeyvatFrame.Enabled || dressedEntry == null)
        {
            return null;
        }

        return TeyvatGeneratedAncients.BaseEntries.TryGetValue(dressedEntry,
                                                               out var baseEntry)
            ? baseEntry
            : null;
    }

    /// <summary>The dressed path wins whenever it exists; the borrow is only
    /// for the interval before the art is drawn.</summary>
    public static void Borrow(ref string result, string fallback)
    {
        if (!ResourceLoader.Exists(result))
        {
            result = fallback;
        }
    }
}

[HarmonyPatch(typeof(EventModel), "get_BackgroundScenePath")]
internal static class EventModel_BackgroundScenePath_TeyvatAncients_Patch
{
    private static void Postfix(EventModel __instance, ref string __result)
    {
        if (__instance is not AncientEventModel)
        {
            return;
        }

        var baseEntry = AncientPicture.BaseEntry(__instance.Id?.Entry);
        if (baseEntry == null)
        {
            return;
        }

        AncientPicture.Borrow(ref __result, SceneHelper.GetScenePath(
            "events/background_scenes/" + baseEntry.ToLowerInvariant()));
    }
}

[HarmonyPatch(typeof(AncientEventModel), "get_MapIconPath")]
internal static class AncientEventModel_MapIconPath_TeyvatAncients_Patch
{
    private static void Postfix(AncientEventModel __instance, ref string __result)
    {
        var baseEntry = AncientPicture.BaseEntry(__instance?.Id?.Entry);
        if (baseEntry == null)
        {
            return;
        }

        AncientPicture.Borrow(ref __result, ImageHelper.GetImagePath(
            "packed/map/ancients/ancient_node_" + baseEntry.ToLowerInvariant()
            + ".png"));
    }
}

[HarmonyPatch(typeof(AncientEventModel), "get_MapIconOutlinePath")]
internal static class AncientEventModel_MapIconOutlinePath_TeyvatAncients_Patch
{
    private static void Postfix(AncientEventModel __instance, ref string __result)
    {
        var baseEntry = AncientPicture.BaseEntry(__instance?.Id?.Entry);
        if (baseEntry == null)
        {
            return;
        }

        AncientPicture.Borrow(ref __result, ImageHelper.GetImagePath(
            "packed/map/ancients/ancient_node_" + baseEntry.ToLowerInvariant()
            + "_outline.png"));
    }
}

[HarmonyPatch(typeof(AncientEventModel), "get_RunHistoryIconOutlinePath")]
internal static class AncientEventModel_RunHistoryIconOutline_TeyvatAncients_Patch
{
    private static void Postfix(AncientEventModel __instance, ref string __result)
    {
        var baseEntry = AncientPicture.BaseEntry(__instance?.Id?.Entry);
        if (baseEntry == null)
        {
            return;
        }

        AncientPicture.Borrow(ref __result, ImageHelper.GetImagePath(
            "ui/run_history/" + baseEntry.ToLowerInvariant() + "_outline.png"));
    }
}

/// <summary>
/// The run-history icon proper. `AncientEventModel.RunHistoryIcon` asks
/// `ImageHelper.GetRoomIconPath(MapPointType.Ancient, RoomType.Event, Id)`,
/// whose suffix is `GetRoomIconSuffix`'s `modelId.Entry.ToLowerInvariant()` --
/// so the model id is the thing to read, and the same postfix serves
/// `GetRoomIconOutlinePath` next door.
/// </summary>
[HarmonyPatch(typeof(ImageHelper), nameof(ImageHelper.GetRoomIconPath))]
internal static class ImageHelper_GetRoomIconPath_TeyvatAncients_Patch
{
    private static void Postfix(MapPointType mapPointType, ModelId? modelId,
                                ref string? __result)
    {
        if (__result == null || mapPointType != MapPointType.Ancient)
        {
            return;
        }

        var baseEntry = AncientPicture.BaseEntry(modelId?.Entry);
        if (baseEntry == null)
        {
            return;
        }

        var fallback = ImageHelper.GetImagePath(
            "ui/run_history/" + baseEntry.ToLowerInvariant() + ".png");
        var result = __result;
        AncientPicture.Borrow(ref result, fallback);
        __result = result;
    }
}

/// <inheritdoc cref="ImageHelper_GetRoomIconPath_TeyvatAncients_Patch"/>
[HarmonyPatch(typeof(ImageHelper), nameof(ImageHelper.GetRoomIconOutlinePath))]
internal static class ImageHelper_GetRoomIconOutlinePath_TeyvatAncients_Patch
{
    private static void Postfix(MapPointType mapPointType, ModelId? modelId,
                                ref string? __result)
    {
        if (__result == null || mapPointType != MapPointType.Ancient)
        {
            return;
        }

        var baseEntry = AncientPicture.BaseEntry(modelId?.Entry);
        if (baseEntry == null)
        {
            return;
        }

        var fallback = ImageHelper.GetImagePath(
            "ui/run_history/" + baseEntry.ToLowerInvariant() + "_outline.png");
        var result = __result;
        AncientPicture.Borrow(ref result, fallback);
        __result = result;
    }
}
