using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Teyvat.Patches;

/// <summary>
/// THE CONVERTED EVENT'S PICTURE -- `MegaCrit.Sts2.Core.Models.EventModel`'s
/// `get_InitialPortraitPath` (EB-764).
///
/// THE PATH IS DERIVED FROM THE ID AND THERE IS NO OTHER SEAM.
/// `InitialPortraitPath` is `ImageHelper.GetImagePath("events/" +
/// Id.Entry.ToLowerInvariant() + ".png")` (`EventModel.cs:198`) and it is
/// `private`, not `protected virtual` -- unlike `MonsterModel.VisualsPath`,
/// which the still-portrait patch next door can override. So a converted event
/// asks the pack for `res://images/events/springvale_cheese_cellar.png`, which
/// nothing produces, and the read is:
///
///   `AssetLoadException` <- `PreloadManager.Cache.GetTexture2D` <-
///   `EventModel.CreateInitialPortrait` <- `NEventLayout.InitializeVisuals`
///
/// with `Asset previously failed to load` in front of it, because the path was
/// already handed to the preloader: `EventModel.GetAssetPaths` (`:431`) adds
/// `InitialPortraitPath` to the act's preload list for every `Default` layout,
/// and a failure there is cached.
///
/// WHICH IS WHY THE GETTER IS THE TARGET AND `CreateInitialPortrait` IS NOT.
/// Patching the create call would fix the draw and leave the PRELOAD still
/// asking for a dead path -- the same failure, one screen earlier, and still
/// cached. One postfix on the getter fixes both readers at once and leaves no
/// second registration to remember. It is the same argument
/// `MonsterVisualsPathPatch` makes for `get_VisualsPath` feeding
/// `MonsterModel.AssetPaths`.
///
/// THE FALL-THROUGH IS THE POINT, again. `ResourceLoader.Exists` is asked of
/// the DRESSED path first and the borrow happens only when it is absent -- the
/// game's own `HasPhobiaModePortrait` (`:202`) asks exactly this question of
/// exactly this kind of path, so it is the sanctioned check. The day a real
/// `springvale_cheese_cellar.png` is in the pack, this patch stands down on its
/// own and the table row in `TeyvatFrame.EventPortraits` can be deleted
/// without touching any code.
///
/// SCOPED TO THE TABLE, AND TO THE ARM. An event with no row -- every base
/// event, always -- gets its own path back unchanged, and with
/// `TeyvatFrame.Enabled` false the postfix returns on its first line. It does
/// NOT consult `CurrentActEntry`: the portrait is asked during act preloading
/// and from the compendium, where there may be no current act at all, and the
/// converted event's id is already unique to the arm.
///
/// NEVER THROWS. `ResourceLoader.Exists` on a malformed path answers false
/// rather than raising, and the postfix has no other statement that can --
/// which matters because this getter is reached while an event page is being
/// built and a throw inside a Harmony postfix would take the page with it,
/// exactly as the null option did.
/// </summary>
[HarmonyPatch(typeof(EventModel), "get_InitialPortraitPath")]
internal static class EventModel_InitialPortraitPath_TeyvatConversions_Patch
{
    private static void Postfix(EventModel __instance, ref string __result)
    {
        if (!TeyvatFrame.Enabled || __instance == null)
        {
            return;
        }

        if (!TeyvatFrame.EventPortraits.TryGetValue(__instance.Id.Entry, out var fallback))
        {
            return;
        }

        // The event's OWN portrait wins whenever it exists; the borrow is only
        // for the interval before one is drawn.
        if (!ResourceLoader.Exists(__result))
        {
            __result = fallback;
        }
    }
}
