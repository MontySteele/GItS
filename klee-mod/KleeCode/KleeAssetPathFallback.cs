using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// Klee's asset-path fallback: rewrites id-derived CharacterModel paths from
/// "klee" to "ironclad" so they resolve to a real base-game asset.
///
/// RENAMED FROM `KleePlaceholderArt` (C4, Serenitea Sweep II, 2026-07-27).
/// `klee-mod/DECISIONS.md` O6 and the 2026-07-26 tech-debt audit refer to it
/// under the old name. The old name said "temporary"; the header said the file
/// would be deleted when the art pass landed. The art pass landed, `has_pck` is
/// **true**, and the file is still load-bearing. A name that predicts its own
/// deletion is how a live safety net gets deleted by someone tidying up.
///
/// WHAT IT ACTUALLY DOES, verified 2026-07-27:
///
/// Every asset path on CharacterModel is computed as
/// <c>"prefix_" + Id.Entry.ToLowerInvariant()</c>, so Klee resolves to
/// char_select_bg_klee, character_icon_klee.png, klee_transition_mat.tres and
/// friends. These properties are NOT virtual, so they cannot be overridden on
/// Klee — hence a Harmony postfix over the whole set.
///
/// It is load-bearing in two distinct ways, and neither is "placeholder":
///
/// 1. **The 9 paths nothing overrides.** Klee, Furina and Kokomi each override
///    the SAME 13 `Custom*Path` properties (BaseLib's mechanism). The four arm
///    textures and the five FMOD events below are overridden by nobody, on any
///    character. For Klee this postfix is their ONLY source of a valid path.
///    (The 2026-07-26 audit and the Sweep-II brief both say "8 asset paths".
///    Counted here: 4 arms + 5 sfx = **9**. Corrected rather than repeated.)
///
/// 2. **Stale-pck safety net for the other 13.** `KleePck.Path` returns null
///    when a resource is absent, and BaseLib then falls back to the base
///    id-derived getter — the exact path that does not exist. So a stale or
///    missing klee.pck lands right back on this postfix instead of on a
///    missing-resource throw at character select. That is the crash O6 records.
///
/// SCOPE, AND THE OPEN ASYMMETRY. The postfix is patched onto CharacterModel,
/// so it RUNS for every character in the game, but it rewrites only when the
/// instance is Klee — base characters and our other two return unchanged. The
/// gap in (1) is roster-wide, so **Furina and Kokomi have no fallback for those
/// 9 paths at all.**
///
/// Deliberately NOT extended to them in this sprint. Redirecting a shipped
/// character's arm textures and combat SFX to Ironclad's is an audible and
/// visible change to two characters, and it would also mask the stale-pck
/// warning `KleePck.Path` already logs. Whether the gap manifests in play is
/// **UNMEASURED** — no play session has been run against it either way, and
/// D4 forbids spending an unmeasured claim as a reason to act. Registered for
/// [USER]: extend, leave, or rule the 9 paths out of scope.
/// </summary>
[HarmonyPatch]
internal static class KleeAssetPathFallback
{
    /// <summary>
    /// The stand-in character whose assets exist. Red-themed, so it reads
    /// acceptably behind Klee (spec C1.4's "placeholder select art"), and it
    /// is also simply the safest choice: Ironclad ships every path below.
    /// </summary>
    private const string Placeholder = "ironclad";

    /// <summary>
    /// Path-valued members of CharacterModel. Includes private ones (the icon
    /// textures and VisualsPath), which is why we go through AccessTools
    /// rather than a plain [HarmonyPatch(typeof(...), "Name")] per property.
    ///
    /// The first 13 are also covered by a `Custom*Path` override on each
    /// character, so for them this is the stale-pck net (reason 2 in the class
    /// header). The last 9 -- four arm textures and five FMOD events -- have no
    /// override anywhere in the mod, so for Klee this is their only source.
    /// </summary>
    private static readonly string[] PathProperties =
    {
        // --- Covered by Custom*Path on all three characters (net only) ---
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

        // --- Overridden by NOBODY. Klee's only source; Furina and Kokomi have
        //     no equivalent (see the asymmetry note in the class header). ---
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

    // F2: this loop was already null-tolerant, but silently so -- a renamed
    // property just stopped being redirected and nothing said which one. It now
    // resolves through KleePatchBootstrap, which records each miss by name for
    // the boot report. Skipping the null is still right: 21 redirected paths
    // and one missing is a DEGRADED patch, not a failed one. Only a fully dead
    // set arms nothing, and the bootstrap treats that as a failure.
    [HarmonyTargetMethods]
    private static IEnumerable<MethodBase> TargetMethods()
    {
        foreach (var name in PathProperties)
        {
            var getter = KleePatchBootstrap.ResolvePropertyGetter(
                typeof(CharacterModel), name);
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
