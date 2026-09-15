using HarmonyLib;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;

namespace KleeMod.Teyvat.Patches;

/// <summary>
/// ENEMY NAMES -- `MegaCrit.Sts2.Core.Models.MonsterModel.L10NMonsterLookup`.
///
/// Text is a `LocString`, which is a TABLE plus a KEY and has no raw-text
/// constructor. Mods merge loc tables (`LocManager.LoadTablesFromPath` calls
/// `locTable.MergeWith` for every modded table), but a merge is GLOBAL: it
/// cannot hold two values for one key, so per-dressing names have to be key
/// REWRITING rather than merging.
///
/// There is exactly one place to rewrite them. `L10NMonsterLookup(string)` is
/// a public static returning `new LocString("monsters", entryName)`, and a
/// grep across the decompile finds it is the ONLY constructor of monster loc
/// strings in the game: `MonsterModel.Title` goes through it
/// (`MonsterModel.cs:196`), every hand-written override does
/// (`BigDummy.cs:13`, `DecimillipedeSegment.cs:49`), and so does every banter
/// and speak line (`BygoneEffigy.cs:60,77`, `Chomper.cs:78`, `KinPriest.cs:27`,
/// `Queen.cs:173,228`). Bestiary move names reach the same table through
/// `MonsterModel.GetBestiaryMoveName`. One postfix covers all of it.
///
/// THE DRESSED KEY IS `&lt;key&gt;@&lt;dressing&gt;`, e.g. `NIBBIT.name@MONDSTADT`, and
/// `TeyvatLoc` merges the arm's rows under exactly those keys at boot. The
/// postfix only rewrites when `TeyvatFrame.MonsterNames` has the pair, so an
/// entry with no dressed row -- which is every monster in the game but one --
/// takes the base key and reads exactly as it read before.
///
/// SPIKE ITEM 4.3's NAME HALF IS ONE TABLE ROW. Nibbit is the Wooden Shield
/// Hilichurl Guard in Mondstadt, and is Nibbit in Overgrowth, in Liyue, in the
/// compendium outside a run, and with the arm off.
/// </summary>
[HarmonyPatch(typeof(MonsterModel), nameof(MonsterModel.L10NMonsterLookup))]
internal static class MonsterModel_L10NMonsterLookup_TeyvatNames_Patch
{
    /// <summary>The separator between a base key and its dressing. A
    /// character the base game's own keys never contain, so a dressed key
    /// cannot collide with a shipped one.</summary>
    internal const char DressingSeparator = '@';

    /// <summary>The dressed key for a base key, or the base key unchanged.
    /// PURE and internal so the pin can ask it without a run.</summary>
    internal static string Dressed(string key, string? dressing) =>
        dressing == null ? key : key + DressingSeparator + dressing;

    private static void Postfix(string entryName, ref LocString __result)
    {
        var dressing = TeyvatFrame.CurrentActEntry;
        if (dressing == null || entryName == null)
        {
            return;
        }

        if (TeyvatFrame.MonsterNames.ContainsKey((dressing, entryName)))
        {
            __result = new LocString("monsters", Dressed(entryName, dressing));
        }
    }
}

/// <summary>
/// INTENT WORDS -- `AbstractIntent.get_IntentTitle` and
/// `AbstractIntent.GetIntentDescription`, the read's optional fourth and fifth
/// patches.
///
/// THEY ARE CHEAP, AND THAT IS THE FINDING. Generic intent words are a
/// DIFFERENT table from monster names and are not per-monster:
/// `AbstractIntent.cs:45` builds `new LocString("intents", IntentPrefix +
/// ".title")` and line 75 does the same for `.description`, with no monster in
/// scope at all. So an intent word is per-ZONE or it is nothing -- "Attack" is
/// "Attack" for every body in a dressing, or it is "Attack" everywhere.
///
/// The frame packet's sec.7.1 design view is that the per-monster MOVE titles
/// carry the nation and the generic verbs do not. So this patch is armed and
/// `TeyvatFrame.IntentWords` ships EMPTY: the mechanism is proved to compile
/// and to key correctly, the cost of using it is one table row, and the taste
/// call about whether to use it at all stays [USER]'s.
///
/// THE COST LINE, since the spike was asked for one: two postfixes, about
/// thirty lines, one loc row per dressed verb, and no per-monster reach. It is
/// the same shape as the name patch and none of its subtlety.
/// </summary>
[HarmonyPatch(typeof(AbstractIntent))]
internal static class AbstractIntent_TeyvatIntentWords_Patch
{
    [HarmonyPostfix]
    [HarmonyPatch("get_IntentTitle")]
    private static void TitlePostfix(ref LocString __result) => Dress(ref __result);

    [HarmonyPostfix]
    [HarmonyPatch("GetIntentDescription")]
    private static void DescriptionPostfix(ref LocString __result) => Dress(ref __result);

    /// <summary>
    /// One body for both, because both build a `LocString` in the `intents`
    /// table and both are dressed the same way. The `LocEntryKey` read is what
    /// makes this work without knowing which verb we were handed.
    ///
    /// `AddVariablesFrom` is load-bearing on the description half:
    /// `AbstractIntent.GetIntentDescription` attaches an `IsMultiplayer`
    /// variable to the string it returns, and a replacement built from the key
    /// alone would render the SmartFormat template with that placeholder
    /// unbound. The game's own copy helper carries them across.
    /// </summary>
    private static void Dress(ref LocString __result)
    {
        var dressing = TeyvatFrame.CurrentActEntry;
        if (dressing == null || __result == null)
        {
            return;
        }

        var key = __result.LocEntryKey;
        if (key == null || !TeyvatFrame.IntentWords.ContainsKey((dressing, key)))
        {
            return;
        }

        var dressed = new LocString(
            __result.LocTable,
            MonsterModel_L10NMonsterLookup_TeyvatNames_Patch.Dressed(key, dressing));
        dressed.AddVariablesFrom(__result);
        __result = dressed;
    }
}
