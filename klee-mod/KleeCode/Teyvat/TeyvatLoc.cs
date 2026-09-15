using System;
using System.Collections.Generic;
using KleeMod.Teyvat.Patches;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;

namespace KleeMod.Teyvat;

/// <summary>
/// THE ARM'S LOC ROWS, merged at boot into the three tables it dresses.
///
/// `LocManager.LoadTablesFromPath` iterates `ModManager.GetModdedLocTables`
/// and calls `locTable.MergeWith(...)` for each, and `LocTable.MergeWith` is
/// public -- so a runtime merge is the supported route for ADDING keys, and it
/// is the route `KleeMod.InjectLocStrings` already rides for cards.
///
/// A MERGE IS GLOBAL, which is why the per-dressing rows below are written
/// under DRESSED keys (`NIBBIT.name@MONDSTADT`) rather than overwriting the
/// base key. `Patches/MonsterNamePatch` rewrites the key when -- and only when
/// -- the arm's table has a row for the current dressing; every other lookup
/// takes the base key and reads exactly as it read before. One merged table,
/// two values for one enemy, no conflict.
///
/// EVERYTHING HERE IS GATED ON THE ARM. With `TeyvatFrame.Enabled` false not a
/// single row is merged, so a release build's loc tables are byte-identical.
/// </summary>
internal static class TeyvatLoc
{
    /// <summary>
    /// Merge the arm's rows. Called from `KleeMod.Initialize` after the
    /// patches are applied, and a no-op with the arm off.
    ///
    /// ONE TRY/CATCH AROUND THE WHOLE THING, on `InjectLocStrings`'s
    /// precedent: a missing table or a `LocManager` that is not up yet must
    /// cost the arm its text, never the mod its boot.
    /// </summary>
    public static void Inject()
    {
        if (!TeyvatFrame.Enabled)
        {
            return;
        }

        try
        {
            // The two act titles. `ActModel.Title` is `new LocString("acts",
            // Id.Entry + ".title")`, so these are the names the map screen and
            // the run-history row print.
            LocManager.Instance.GetTable("acts").MergeWith(new Dictionary<string, string>
            {
                [TeyvatFrame.Mondstadt + ".title"] = "Mondstadt",
                [TeyvatFrame.Liyue + ".title"] = "Liyue",
            });

            // The dressed enemy names, derived from the same table the patch
            // reads so a row cannot exist in one and not the other.
            var monsters = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (var ((dressing, key), value) in TeyvatFrame.MonsterNames)
            {
                monsters[MonsterModel_L10NMonsterLookup_TeyvatNames_Patch.Dressed(key, dressing)] = value;
            }

            // The dressed intent words, on the same terms. Empty today by
            // design (`TeyvatFrame.IntentWords`), and `MergeWith` of an empty
            // dictionary is a no-op rather than an error.
            var intents = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (var ((dressing, key), value) in TeyvatFrame.IntentWords)
            {
                intents[MonsterModel_L10NMonsterLookup_TeyvatNames_Patch.Dressed(key, dressing)] = value;
            }

            LocManager.Instance.GetTable("monsters").MergeWith(monsters);
            LocManager.Instance.GetTable("intents").MergeWith(intents);

            // The converted event's own rows. Its table is `EventModel.LocTable`,
            // which is "events"; the keys are `Id.Entry`-derived exactly as the
            // base game's are. Text is
            // `docs/current/dossiers/content/event-conversion-gallery.md`
            // variant 1, verbatim.
            LocManager.Instance.GetTable("events").MergeWith(new Dictionary<string, string>
            {
                ["SPRINGVALE_CHEESE_CELLAR.title"] = "The Springvale Cheese Cellar",
                ["SPRINGVALE_CHEESE_CELLAR.pages.INITIAL.description"] =
                    "A collapsed stair below Springvale opens onto a dairy cellar the "
                  + "Guild's commission board never got around to delisting. Wheels of "
                  + "Mondstadt cheese sit rack on rack, gold-rinded and humming with "
                  + "age, and the slip in your hand says only: inventory it. Behind the "
                  + "furthest rack, something older than the racks is sweating brine.",
                ["SPRINGVALE_CHEESE_CELLAR.pages.INITIAL.options.TASTE_THE_RACKS"] =
                    "Taste the Racks",
                ["SPRINGVALE_CHEESE_CELLAR.pages.INITIAL.options.HAUL_OUT_THE_BACK_WALL"] =
                    "Haul Out the Back Wall",
                ["SPRINGVALE_CHEESE_CELLAR.pages.TASTE_THE_RACKS.selectionScreenPrompt"] =
                    "Choose 2 wheels",
                ["SPRINGVALE_CHEESE_CELLAR.pages.TASTE_THE_RACKS.description"] =
                    "You eat your way along the racks and carry off the two that were "
                    + "worth the trip.",
                ["SPRINGVALE_CHEESE_CELLAR.pages.HAUL_OUT_THE_BACK_WALL.description"] =
                    "The back wall comes down on your shoulders and the spore-thick air "
                    + "goes into your lungs. Behind it, gold-rinded and perfect, waits "
                    + "the wheel the Guild never listed.",
            });

            Log.Info($"[{KleeMod.ModId}] teyvat: loc merged ({monsters.Count} dressed enemy "
                   + $"name(s), {intents.Count} dressed intent word(s)).");
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] teyvat: loc merge failed, the arm's text will render "
                    + $"as raw keys: {e}");
        }
    }
}
