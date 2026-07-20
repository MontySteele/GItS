using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Modding;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Characters;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod;

/// <summary>
/// Mod entry point. The game looks for a class carrying [ModInitializer] and
/// invokes the named method during ModManager initialization.
/// </summary>
[ModInitializer(nameof(Initialize))]
public static class KleeMod
{
    public const string ModId = "klee";

    public static void Initialize()
    {
        Log.Info($"[{ModId}] Initializing Klee (C1 boots)...");

        try
        {
            var harmony = new Harmony(ModId);
            harmony.PatchAll(typeof(KleeMod).Assembly);
        }
        catch (Exception e)
        {
            Log.Error($"[{ModId}] Harmony patching failed: {e}");
        }

        Log.Info($"[{ModId}] Klee registered.");
    }

    /// <summary>English strings for the character and the four starter stubs.</summary>
    internal static void InjectLocStrings()
    {
        try
        {
            // Keys are ModelId.Entry, which is UPPER_SNAKE_CASE derived from the
            // class name (DuckAndCover -> DUCK_AND_COVER), NOT lowercase.
            // CardModel.Description reads "cards" -> "<ENTRY>.description".
            LocManager.Instance.GetTable("cards").MergeWith(new Dictionary<string, string>
            {
                // Two separate syntaxes are in play here, and both bit us:
                //
                // 1. Values are SmartFormat templates over DynamicVarSet, whose
                //    keys are "Damage" / "Block" (see BlockVar.defaultName).
                //    SmartFormat uses SINGLE braces - "{{Damage}}" is not a
                //    placeholder and is emitted literally.
                //
                // 2. Square brackets are BBCode, NOT keyword markup. The game
                //    wraps descriptions in [center]...[/center], so a stray
                //    "[Block]" parses as an unclosed tag and throws
                //    "Found end tag center, expected Block". Keyword tooltips
                //    are declared per-mod via a card_keywords.json (the Downfall
                //    pattern, see docs/card_keywords.json); we ship none yet, so
                //    C1 uses plain text and keywords land with the C2 text pass.
                // ONLY plain CardModel stubs belong here. Cards that derive from
                // BaseLib's CustomCardModel get a prefixed id (KLEEMOD-KABOOM),
                // so they declare loc via an ILocalizationProvider.Localization
                // override on the model instead -- see Kaboom.Localization.
                // KleeSelfCheck.Run() enforces that split at boot.
                ["JUMPY_DUMPTY.title"] = "Jumpy Dumpty",
                ["JUMPY_DUMPTY.description"] = "Deal {Damage:diff()} damage twice.",

                // Pop is now a CustomCardModel and declares its own loc.
            });

            ProbeBaseGameLocSyntax();

            LocManager.Instance.GetTable("characters").MergeWith(new Dictionary<string, string>
            {
                // Same UPPER_SNAKE_CASE Entry convention as cards.
                ["KLEE.title"] = "Klee",
                ["KLEE.description"] = "The Spark Knight of Mondstadt.",
                ["KLEE.titleObject"] = "Klee",
                ["KLEE.pronounSubject"] = "she",
                ["KLEE.pronounObject"] = "her",
                ["KLEE.pronounPossessive"] = "hers",
                ["KLEE.possessiveAdjective"] = "her",
            });

            Log.Info($"[{ModId}] Localization strings injected.");
        }
        catch (Exception e)
        {
            Log.Error($"[{ModId}] Failed to inject loc strings: {e}");
        }
    }

    /// <summary>
    /// TEMPORARY DIAGNOSTIC. Dumps the raw text of a few base-game card
    /// descriptions so the real SmartFormat placeholder syntax is observed
    /// rather than inferred. The loc tables ship compressed inside the .pck, so
    /// reading them at runtime is the only way to see ground truth short of
    /// extracting assets with GDRE.
    ///
    /// Delete once the card text renders correctly.
    /// </summary>
    private static void ProbeBaseGameLocSyntax()
    {
        try
        {
            var cards = LocManager.Instance.GetTable("cards");

            foreach (var key in new[]
                     {
                         "STRIKE_SILENT.description",
                         "DEFEND_SILENT.description",
                         "STRIKE_IRONCLAD.description",
                         "DEFEND_IRONCLAD.description",
                     })
            {
                if (cards.HasEntry(key))
                {
                    Log.Info($"[{ModId}] LOCPROBE {key} => {cards.GetRawText(key)}");
                }
                else
                {
                    Log.Info($"[{ModId}] LOCPROBE {key} => (no such entry)");
                }
            }

            // Fallback: if none of the guessed keys exist, show real ones so we
            // can read both the key convention and the template syntax.
            var sample = cards.Keys
                .Where(k => k.EndsWith(".description", StringComparison.Ordinal))
                .Take(8)
                .ToList();

            foreach (var key in sample)
            {
                Log.Info($"[{ModId}] LOCPROBE sample {key} => {cards.GetRawText(key)}");
            }
        }
        catch (Exception e)
        {
            Log.Error($"[{ModId}] LOCPROBE failed: {e}");
        }
    }
}

// ---------------------------------------------------------------------------
//  Harmony patches
// ---------------------------------------------------------------------------

/// <summary>Injects our loc strings once LocManager has built its tables.</summary>
[HarmonyPatch(typeof(LocManager), nameof(LocManager.Initialize))]
internal static class LocManager_Initialize_Patch
{
    [HarmonyPostfix]
    public static void Postfix() => KleeMod.InjectLocStrings();
}

/// <summary>
/// C1: make Klee selectable.
///
/// ModelDb.AllCharacters is a HARDCODED five-element array, not a registry
/// scan — defining a CharacterModel subclass registers it with ModelDb.Get&lt;T&gt;()
/// but never puts it in that array. The character-select screen iterates
/// AllCharacters and uses UnlockState.Characters only as a lock filter, so
/// appending here is what actually makes Klee appear.
///
/// It also feeds every downstream consumer for free: UnlockState.Characters
/// derives from AllCharacters (removing only locked characters), as do
/// AllCards, AllRelics, and the pool collections. This is the single correct
/// injection point; patching UnlockState instead — as this mod originally did
/// — moves nothing, because the screen never consults it for membership.
/// </summary>
[HarmonyPatch(typeof(ModelDb), nameof(ModelDb.AllCharacters), MethodType.Getter)]
internal static class ModelDb_AllCharacters_Patch
{
    [HarmonyPostfix]
    public static void Postfix(ref IEnumerable<CharacterModel> __result)
    {
        var klee = ModelDb.Character<Klee>();
        if (!__result.Contains(klee))
        {
            __result = __result.Append(klee);
        }
    }
}
