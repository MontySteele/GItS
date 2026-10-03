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
/// 1. **The 5 paths nothing overrides.** Klee, Furina and Kokomi each override
///    the SAME 13 `Custom*Path` properties (BaseLib's mechanism). The five FMOD
///    events below are overridden by nobody, on any character. For Klee this
///    postfix is their ONLY source of a valid path.
///    (The 2026-07-26 audit and the Sweep-II brief both said "8 asset paths";
///    it was 4 arms + 5 sfx = 9 until 2026-09-27, when the four arm textures
///    left this list: see "THE HANDS" below.)
///
/// 2. **Stale-pck safety net for the other 13.** `KleePck.Path` returns null
///    when a resource is absent, and BaseLib then falls back to the base
///    id-derived getter — the exact path that does not exist. So a stale or
///    missing klee.pck lands right back on this postfix instead of on a
///    missing-resource throw at character select. That is the crash O6 records.
///
/// SCOPE. The postfix is patched onto CharacterModel, so it RUNS for every
/// character in the game. For Klee it rewrites the whole set to Ironclad's, as
/// it always has. For the other three it rewrites ONLY the five FMOD events,
/// each to a base character whose sounds fit (2026-10-02, the combat visual
/// audit, gap 4: "Furina, Kokomi and Varka make no character sounds"):
///
///   * Furina  -> the Silent's      (lighter; Hydro duelist)
///   * Kokomi  -> the Necrobinder's (lighter; a caster, distinct from Furina's
///                in a two-Hydro co-op)
///   * Varka   -> the Regent's      (heavier; a knight, distinct from Klee's
///                Ironclad borrow in a Mondstadt co-op)
///
/// Their 13 art paths are NOT redirected: each ships its own art, and sending
/// a stale pck to another character's art would mask the warning `KleePck.Path`
/// logs. Real voices are new audio, a money pick for [USER]; this is a borrow.
/// The pure mapping is <see cref="SfxDonorFor"/> and <see cref="RedirectSfx"/>,
/// pinned headlessly in `KleeTests/AssetPathFallbackTests.cs`.
///
/// THE HANDS (2026-09-27). The four `Arm*TexturePath` getters (the co-op
/// treasure room's hands) used to be redirected here too, so Klee drew the
/// Ironclad's arm while Furina and Kokomi drew none. All four (Varka since
/// 2026-09-30, wearing the Ironclad's arm unchanged) now ship their own at the
/// exact path the getter derives,
/// res://images/ui/hands/multiplayer_hand_kleemod-&lt;name&gt;_&lt;pose&gt;.png
/// (tools/gen_multiplayer_hands.py, packed by tools/build_pck.ps1), so Klee's
/// arm paths are left alone. A pck without the hands shows no hand for Klee,
/// as it always did for the other two.
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
    /// header). The last 5 -- the FMOD events -- have no override anywhere in
    /// the mod, so for Klee this is their only source. The four arm textures
    /// are NOT here: Klee ships her own (see "THE HANDS" in the class header).
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

        // --- Overridden by NOBODY. Klee's only source, and since 2026-10-02
        //     Furina's, Kokomi's and Varka's too (SfxProperties below). ---
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
    // the boot report. Skipping the null is still right: 17 redirected paths
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

    /// <summary>The five FMOD-event members: the only ones redirected for
    /// the three characters who are not Klee.</summary>
    internal static readonly HashSet<string> SfxProperties = new()
    {
        "CharacterSelectSfx",
        "CharacterTransitionSfx",
        "AttackSfx",
        "CastSfx",
        "DeathSfx",
    };

    /// <summary>The base character whose sounds a mod character borrows, by
    /// its lower-cased id entry's name part; null for none.</summary>
    internal static string? SfxDonorFor(string characterName) => characterName switch
    {
        "klee" => Placeholder,
        "furina" => "silent",
        "kokomi" => "necrobinder",
        "varka" => "regent",
        _ => null,
    };

    /// <summary>
    /// One FMOD event path rewritten onto <paramref name="donor"/>'s. The four
    /// id-derived events swap the id; the transition wipe is the donor's REAL
    /// one, because Defect, Necrobinder and Regent override
    /// <c>CharacterTransitionSfx</c> to <c>wipe_ironclad</c> (0.111.0
    /// decompile): there is no <c>wipe_regent</c> event to swap into.
    /// </summary>
    internal static string RedirectSfx(
        string property, string path, string idEntryLower, string donor)
    {
        if (property == "CharacterTransitionSfx")
        {
            return donor is "ironclad" or "silent"
                ? "event:/sfx/ui/wipe_" + donor
                : "event:/sfx/ui/wipe_ironclad";
        }
        return path.Replace(idEntryLower, donor);
    }

    [HarmonyPostfix]
    private static void RedirectToPlaceholder(
        CharacterModel __instance, MethodBase __originalMethod, ref string __result)
    {
        if (string.IsNullOrEmpty(__result))
        {
            return;
        }
        if (__instance is Klee klee)
        {
            // The paths embed Id.Entry lowercased, NOT the mod id. BaseLib
            // prefixes custom model ids (KLEE -> KLEEMOD-KLEE), so replacing
            // the bare mod id produced "char_select_ironcladmod-ironclad.png"
            // -- a black box where the select icon should be (finding 23).
            // Read the entry off the live model so the substring we replace is
            // by construction the one the paths contain.
            __result = __result.Replace(klee.Id.Entry.ToLowerInvariant(), Placeholder);
            return;
        }

        // Furina, Kokomi, Varka: the five sound events only.
        var donor = __instance switch
        {
            Furina => SfxDonorFor("furina"),
            Kokomi => SfxDonorFor("kokomi"),
            Varka => SfxDonorFor("varka"),
            _ => null,
        };
        var property = __originalMethod.Name.StartsWith("get_")
            ? __originalMethod.Name.Substring(4)
            : __originalMethod.Name;
        if (donor != null && SfxProperties.Contains(property))
        {
            __result = RedirectSfx(
                property, __result, __instance.Id.Entry.ToLowerInvariant(), donor);
        }
    }
}
