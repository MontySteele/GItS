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
internal static partial class TeyvatLoc
{
    /// <summary>
    /// THE DRESSED EVENTS' ROWS, in the `events` table (`EventModel.LocTable`),
    /// under `Id.Entry`-derived keys exactly as the base game's are.
    ///
    /// GENERATED, AND THAT IS THE POINT OF THIS SURFACE. The rows themselves
    /// are `TeyvatEventsGenerated.cs`'s `GeneratedEventRows`, emitted by
    /// `tools/gen_teyvat_events.py` from the curated face files; this alias is
    /// what the arm and its pins read, so a reader does not have to know which
    /// file a row was born in. The spike's hand-written block is retired: the
    /// Springvale Cheese Cellar is now one of six generated dressings and its
    /// rows are word for word the face file's.
    ///
    /// AN OPTION KEY IS A PREFIX, NOT A STRING, and getting that wrong was
    /// EB-765. `EventOption`'s `(eventModel, onChosen, textKey, hoverTips)`
    /// constructor does NOT read the key it is handed -- it reads
    /// `eventModel.GetOptionTitle(textKey)` and `GetOptionDescription(textKey)`,
    /// which are `LocString.GetIfExists(LocTable, textKey + ".title")` and
    /// `... + ".description"` (`EventModel.cs:216-224`). `GetIfExists` returns
    /// NULL for a key that is not in the table, and the constructor's last act
    /// is `AddLocVars`, whose first line is
    /// `eventModel.Owner?.Character.AddDetailsTo(Description)` --
    /// `CharacterModel.AddDetailsTo` then calls `str.Add(...)` on that null and
    /// throws. The spike wrote ONE flat row per option, so both descriptions
    /// were null, the first `new EventOption(...)` threw,
    /// `GenerateInitialOptions` never returned, and the page opened with
    /// `body: null` and `options: []`
    /// (`review/records/teyvat-spike-reproof-2026-09-15.md` item 2). The
    /// generator writes BOTH rows for every option and cannot write one.
    ///
    /// `.loss` is optional to the engine -- `NRunHistory` asks
    /// `LocString.GetIfExists` and falls back to `DEFAULT_EVENT_LOSS_MESSAGE`
    /// -- so the generator writes one only where the base event can kill AND
    /// the face supplies a `Loss:` line. Today that is the Springvale Cheese
    /// Cellar alone, carrying the spike's shipped sentence; the other five
    /// dressings take the engine's fallback rather than have a machine invent
    /// a death line.
    /// </summary>
    internal static IReadOnlyDictionary<string, string> EventRows => GeneratedEventRows;

    /// <summary>
    /// Merge the arm's rows. A no-op with the arm off.
    ///
    /// CALLED FROM THE `LocManager.Initialize` POSTFIX (`KleeMod.cs`'s
    /// `LocManager_Initialize_Patch`), beside the card rows -- and NOT from
    /// `KleeMod.Initialize`, which is where it was and is EB-759. A
    /// `[ModInitializer]` runs before `LocManager` has built a single table,
    /// so `LocManager.Instance.GetTable(...)` threw an NRE on every boot, the
    /// catch below turned it into one ERROR line, and zero rows merged: every
    /// dressed string rendered as its raw key
    /// (`review/records/teyvat-spike-proofs-2026-09-15.md`). The rule the card
    /// rows already followed is the right one -- merge once the tables EXIST,
    /// not merely before they are read.
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

            // The converted event's own rows (see `EventRows`). Copied rather
            // than passed, because `MergeWith` takes a concrete `Dictionary`
            // and the table itself stays read-only to everything else.
            LocManager.Instance.GetTable("events")
                .MergeWith(new Dictionary<string, string>(EventRows, StringComparer.Ordinal));

            Log.Info($"[{KleeMod.ModId}] teyvat: loc merged ({monsters.Count} dressed enemy "
                   + $"name(s), {intents.Count} dressed intent word(s), {EventRows.Count} "
                   + $"converted-event row(s)).");
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] teyvat: loc merge failed, the arm's text will render "
                    + $"as raw keys: {e}");
        }
    }
}
