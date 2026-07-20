using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// C1 PLACEHOLDER ART — Klee borrows Ironclad's assets.
///
/// Every asset path on CharacterModel is computed as
/// <c>"prefix_" + Id.Entry.ToLowerInvariant()</c>, so Klee resolves to
/// char_select_bg_klee, character_icon_klee.png, klee_transition_mat.tres and
/// friends. We ship no .pck (has_pck: false), so none of those resources exist
/// and the character-select screen throws on the first
/// PreloadManager.Cache.GetScene() call.
///
/// Most of these properties are NOT virtual, so they can't be overridden on
/// Klee — hence a Harmony postfix over the whole set, rewriting "klee" to
/// "ironclad" in the returned path. Red-themed, so it reads acceptably as a
/// stand-in, and it satisfies spec C1.4's "placeholder select art".
///
/// This entire file is deleted when the art pass lands a real Klee .pck.
/// </summary>
[HarmonyPatch]
internal static class KleePlaceholderArt
{
    private const string Placeholder = "ironclad";

    /// <summary>
    /// Path-valued members of CharacterModel. Includes private ones (the icon
    /// textures and VisualsPath), which is why we go through AccessTools
    /// rather than a plain [HarmonyPatch(typeof(...), "Name")] per property.
    /// </summary>
    private static readonly string[] PathProperties =
    {
        "CharacterSelectBg",
        "CharacterSelectIconPath",
        "CharacterSelectLockedIconPath",
        "CharacterSelectTransitionPath",
        "IconPath",
        "IconTexturePath",
        "IconOutlineTexturePath",
        "EnergyCounterPath",
        "VisualsPath",
        "MerchantAnimPath",
        "RestSiteAnimPath",
        "MapMarkerPath",
        "TrailPath",
        "ArmPointingTexturePath",
        "ArmRockTexturePath",
        "ArmPaperTexturePath",
        "ArmScissorsTexturePath",

        // FMOD event paths. Missing events only warn ("cannot find sfx path")
        // rather than throw, but they spam the log we debug from.
        "CharacterSelectSfx",
        "CharacterTransitionSfx",
        "AttackSfx",
        "CastSfx",
        "DeathSfx",
    };

    [HarmonyTargetMethods]
    private static IEnumerable<MethodBase> TargetMethods()
    {
        foreach (var name in PathProperties)
        {
            var getter = AccessTools.PropertyGetter(typeof(CharacterModel), name);
            if (getter != null)
            {
                yield return getter;
            }
        }
    }

    [HarmonyPostfix]
    private static void RedirectToPlaceholder(CharacterModel __instance, ref string __result)
    {
        if (__instance is Klee klee && !string.IsNullOrEmpty(__result))
        {
            // The paths embed Id.Entry lowercased, NOT the mod id. BaseLib
            // prefixes custom model ids (KLEE -> KLEEMOD-KLEE), so replacing
            // the bare mod id produced "char_select_ironcladmod-ironclad.png"
            // -- a black box where the select icon should be (finding 23).
            // Read the entry off the live model so the substring we replace is
            // by construction the one the paths contain.
            __result = __result.Replace(klee.Id.Entry.ToLowerInvariant(), Placeholder);
        }
    }
}
