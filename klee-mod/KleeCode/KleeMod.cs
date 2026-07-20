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
                ["KABOOM.title"] = "Kaboom!",
                ["KABOOM.description"] = "Deal {{Damage}} damage.",

                ["DUCK_AND_COVER.title"] = "Duck and Cover",
                ["DUCK_AND_COVER.description"] = "Gain {{Block}} [Block].",

                ["JUMPY_DUMPTY.title"] = "Jumpy Dumpty",
                ["JUMPY_DUMPTY.description"] = "Deal {{Damage}} damage twice.",

                ["POP.title"] = "Pop!",
                ["POP.description"] = "Deal {{Damage}} damage.",
            });

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
