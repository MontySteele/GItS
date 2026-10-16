using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using BaseLib.Patches.Content;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Modding;

namespace KleeMod.Patches;

/// <summary>
/// A KIT LEFT OUT OF THIS BUILD REGISTERS NO CHARACTER
/// (<see cref="ReleaseKits"/>, <c>-p:GitsKits=...</c>). BaseLib's
/// <c>CustomCharacterModel</c> constructor calls
/// <c>CustomContentDictionary.AddCharacter(this)</c>, which inserts it into
/// <c>CustomCharacters</c>; this postfix takes a left-out kit's character
/// straight back off that list, before anything reads it (ModelDb builds its
/// content after every mod initializer has run). With every kit shipping
/// (the default, and every dev build) it returns on its first line.
/// </summary>
[HarmonyPatch(typeof(CustomContentDictionary), nameof(CustomContentDictionary.AddCharacter))]
internal static class CustomContentDictionary_AddCharacter_ReleaseKits_Patch
{
    [HarmonyPostfix]
    public static void Postfix(CustomCharacterModel character)
    {
        if (ReleaseKits.Unregister(CustomContentDictionary.CustomCharacters,
                                   character, ReleaseKits.Shipped))
        {
            Log.Info($"[{KleeMod.ModId}] kit '{ReleaseKits.KitOf(character)}' "
                   + "is not in this build (GitsKits); its character is not registered");
        }
    }
}

/// <summary>
/// THE BETA PACKAGE'S LOC TABLE (<c>tools/package_workshop.py --variant
/// beta</c>). The game merges <c>res://&lt;manifest id&gt;/localization/&lt;lang&gt;/&lt;file&gt;</c>
/// for each loaded mod (0.111.0 <c>ModManager.GetModdedLocTables</c>), and
/// the pck keeps its tables at <c>res://klee/</c> whatever the manifest id
/// is. So a package whose manifest id is not <c>klee</c> (the beta's
/// <c>klee-beta</c>) would lose <c>card_keywords.json</c> and print raw
/// keyword keys. This adds our own table path when the game did not list
/// it. Under the id <c>klee</c> the game lists it itself and this adds
/// nothing.
/// </summary>
[HarmonyPatch(typeof(ModManager), nameof(ModManager.GetModdedLocTables))]
internal static class ModManager_GetModdedLocTables_OwnTable_Patch
{
    [HarmonyPostfix]
    public static IEnumerable<string> Postfix(IEnumerable<string> __result,
                                              string language, string file)
    {
        var list = __result.ToList();
        try
        {
            var own = OwnTable(language, file);
            if (!list.Contains(own) && ResourceLoader.Exists(own)) list.Add(own);
        }
        catch (System.Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] own loc table lookup failed: {e.Message}");
        }
        return list;
    }

    /// <summary>PURE: where the pck keeps a table.</summary>
    internal static string OwnTable(string language, string file) =>
        $"res://{KleeMod.ModId}/localization/{language}/{file}";
}
