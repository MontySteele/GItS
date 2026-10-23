using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using BaseLib.Patches.Localization;
using HarmonyLib;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// OUR ENGLISH GOES TO THE ENGLISH TABLE, ALWAYS (localization route b,
/// 2026-10-19).
///
/// THE BUG. Every row this mod authors used to be written into the CURRENT
/// language's table: BaseLib's <c>ModelLocPatch</c> writes model rows into
/// <c>LocManager.Instance.GetTable(..)</c>, and every hand-written merge did
/// the same. In English that is the English table. In any other language it
/// is that language's table, so <c>LocManager.SmartFormat</c> took our
/// English for a local row and formatted it with the local culture: booted in
/// Simplified Chinese, Countdown printed "Draw 2 card." (English text, Chinese
/// plural rules). And <c>LocManager.SetLanguage</c> rebuilds every table from
/// files, so an in-game language switch dropped every row we had merged.
///
/// THE RULE NOW. Our English rows land in the ENGLISH table, which the game
/// already keeps as the per-key fallback of every other language's table
/// (<c>LocManager.LoadTablesFromPath</c>). A non-English player reads our
/// English through that fallback, formatted with English culture, and a
/// translated row shipped as <c>klee/localization/&lt;lang&gt;/&lt;table&gt;.json</c>
/// in the pck sits in the local table and wins per key. The rows are applied
/// again every time the game builds a set of tables, so a language switch
/// keeps them.
///
/// ROWS COPIED FROM BASE-GAME TEXT (a dressed Ancient's alias of the base
/// Ancient's lines, a story Ancient's "next" button) are not ours to
/// translate: <see cref="MergeDerived"/> builds them once from the English
/// table into the English table, and once from the local table into the local
/// table, keeping only what the local language really has.
/// </summary>
public static class EnglishLoc
{
    private const string English = "eng";

    private static readonly FieldInfo? FallbackField =
        AccessTools.Field(typeof(LocTable), "_fallback");

    private static readonly FieldInfo? TablesField =
        AccessTools.Field(typeof(LocManager), "_tables");

    /// <summary>Where <see cref="Table"/> resolves during a pass.</summary>
    private static Func<string, LocTable>? _english;

    /// <summary>The non-English table set a pass also writes derived rows
    /// into, or null for an English pass.</summary>
    private static Func<string, LocTable?>? _local;

    /// <summary>Our models' rows, by table then key, captured once at
    /// <c>ModelDb.Init</c> and re-applied with every table set.</summary>
    private static readonly Dictionary<string, Dictionary<string, string>> ModelRows =
        new(StringComparer.Ordinal);

    /// <summary>
    /// Every hand-written merge, in boot order. The model rows go last, as
    /// they did when BaseLib wrote them at <c>ModelDb.Init</c> after these.
    /// </summary>
    public static void RunInjectors()
    {
        KleeMod.InjectLocStrings();

        // Player English that code builds (tip bodies, the reaction guide,
        // element names): `CodeText`'s rows. Its own try/catch.
        CodeText.Inject();

        // THE TEYVAT RUN FRAME ARM's rows (spike, -p:TeyvatFrame=true). A
        // no-op with the arm off — `TeyvatLoc.Inject`'s first line is the
        // flag — so a release build merges not one row.
        Teyvat.TeyvatLoc.Inject();

        // The story tables' rows (Klee story batches 1 and 2): event pages,
        // Ancient exchanges and spoken lines. Its own try/catch.
        Story.StoryLoc.Inject();

        // The Spiral Abyss's page and menu rows. Its own try/catch.
        Abyss.AbyssLoc.Inject();

#if GITS_RUN_STATS
        // The run-stats setting's label (settings_ui), its own try/catch.
        RunStats.RunStatsHook.InjectLoc();
#endif
    }

    /// <summary>
    /// The ENGLISH table of this name: the table an injector merges our rows
    /// into. During a pass it is the pass's English set; otherwise it is the
    /// live manager's English table (the current table in English, the current
    /// table's fallback in any other language).
    /// </summary>
    public static LocTable Table(string name)
    {
        if (_english != null) return _english(name);
        var manager = LocManager.Instance;
        return EnglishOf(manager.GetTable(name), manager.Language);
    }

    /// <summary>
    /// Rows COPIED from base-game text. Built from the English table into the
    /// English table; then, in a non-English pass, built again from the local
    /// table into the local table, keeping only rows whose text differs from
    /// the English build (the local language really has them) and never
    /// overwriting a row the local table already holds (a shipped
    /// translation).
    /// </summary>
    public static void MergeDerived(string name, Func<LocTable, Dictionary<string, string>> derive)
    {
        var english = Table(name);
        var englishRows = derive(english);
        english.MergeWith(englishRows);

        var local = _local?.Invoke(name);
        if (local == null || ReferenceEquals(local, english)) return;
        var localRows = derive(local)
            .Where(row => !local.IsLocalKey(row.Key)
                          && !(englishRows.TryGetValue(row.Key, out var en)
                               && string.Equals(en, row.Value, StringComparison.Ordinal)))
            .ToDictionary(row => row.Key, row => row.Value, StringComparer.Ordinal);
        local.MergeWith(localRows);
    }

    /// <summary>
    /// One full pass: every injector and every captured model row into
    /// <paramref name="english"/>, and derived rows into
    /// <paramref name="local"/> when it is given.
    /// </summary>
    public static void Apply(Func<string, LocTable> english, Func<string, LocTable?>? local) =>
        Within(english, local, () =>
        {
            RunInjectors();
            ApplyModelRows();
        });

    /// <summary>Run <paramref name="body"/> with <see cref="Table"/> and
    /// <see cref="MergeDerived"/> pointed at the given table sets.</summary>
    public static void Within(Func<string, LocTable> english, Func<string, LocTable?>? local, Action body)
    {
        var (previousEnglish, previousLocal) = (_english, _local);
        _english = english;
        _local = local;
        try
        {
            body();
        }
        finally
        {
            _english = previousEnglish;
            _local = previousLocal;
        }
    }

    /// <summary>A pass over a table set the game just built for
    /// <paramref name="language"/>.</summary>
    public static void ApplyToTables(string language, IReadOnlyDictionary<string, LocTable> tables)
    {
        Apply(name => EnglishOf(Lookup(tables, name), language),
              language == English
                  ? null
                  : name => tables.TryGetValue(name, out var t) ? t : null);
    }

    /// <summary>A pass over the live manager's tables (boot).</summary>
    public static void ApplyToCurrent()
    {
        var manager = LocManager.Instance;
        if (TablesField?.GetValue(manager) is Dictionary<string, LocTable> tables)
        {
            ApplyToTables(manager.Language, tables);
            return;
        }
        // The private field moved: resolve table by table instead.
        Apply(name => EnglishOf(manager.GetTable(name), manager.Language),
              manager.Language == English ? null : name => manager.GetTable(name));
    }

    /// <summary>The English table behind <paramref name="table"/>: itself in
    /// English, else its fallback (itself when it has none).</summary>
    public static LocTable EnglishOf(LocTable table, string language)
    {
        if (language == English) return table;
        return FallbackField?.GetValue(table) as LocTable ?? table;
    }

    private static LocTable Lookup(IReadOnlyDictionary<string, LocTable> tables, string name) =>
        tables.TryGetValue(name, out var table)
            ? table
            : throw new LocException("The loc table='" + name + "' does not exist!");

    // ------------------------------------------------------------------
    //  Model rows (BaseLib's ILocalizationProvider), redirected
    // ------------------------------------------------------------------

    /// <summary>True for a model this mod defines.</summary>
    public static bool IsOurs(AbstractModel model) =>
        model.GetType().Assembly == typeof(EnglishLoc).Assembly;

    /// <summary>The content dictionary minus our models, for BaseLib's own
    /// writer: our rows go to the English table instead.</summary>
    public static Dictionary<ModelId, AbstractModel> WithoutOurs(Dictionary<ModelId, AbstractModel> content) =>
        content.Where(pair => !IsOurs(pair.Value))
            .ToDictionary(pair => pair.Key, pair => pair.Value);

    /// <summary>
    /// Capture our models' rows exactly as BaseLib's <c>ModelLocPatch</c>
    /// would write them (table, <c>Entry.key</c>, <c>SimpleLoc.TrySimplify</c>)
    /// and apply them to the live English tables.
    /// </summary>
    public static void RecordModelRows(IEnumerable<KeyValuePair<ModelId, AbstractModel>> content)
    {
        foreach (var (id, model) in content)
        {
            if (!IsOurs(model) || model is not ILocalizationProvider provider) continue;
            var rows = provider.Localization;
            if (rows == null) continue;
            var table = provider.LocTable ?? TableForCategory(id.Category)
                ?? throw new InvalidOperationException($"No loc table for {id}.");
            if (!ModelRows.TryGetValue(table, out var bucket))
            {
                ModelRows[table] = bucket = new Dictionary<string, string>(StringComparer.Ordinal);
            }
            foreach (var (key, value) in rows)
            {
                var text = ModelRowText(model, key, value);
                bucket[id.Entry + "." + key] = text;
                if (text != SimpleLoc.TrySimplify(value))
                {
                    // A face with element tokens: its formatting is handed
                    // the names (`OverriddenElementFace_Format_Patch`).
                    Cards.OverriddenElementFace.TokenRows.Add(id.Entry + "." + key);
                }
            }
        }
    }

    /// <summary>
    /// One of our model rows as it is written to the English table: BaseLib's
    /// <c>SimpleLoc.TrySimplify</c>, then, on a card's face, its hit-element
    /// words as tokens (<see cref="Cards.OverriddenElementFace.Templatize"/>).
    /// The English reference is built through this too.
    /// </summary>
    public static string ModelRowText(AbstractModel model, string key, string value)
    {
        var text = SimpleLoc.TrySimplify(value);
        return model is CardModel && key == "description"
            ? Cards.OverriddenElementFace.Templatize(text)
            : text;
    }

    /// <summary>The captured model rows, table by table (read-only view).</summary>
    public static IReadOnlyDictionary<string, Dictionary<string, string>> CapturedModelRows => ModelRows;

    private static void ApplyModelRows()
    {
        foreach (var (table, rows) in ModelRows)
        {
            try
            {
                Table(table).MergeWith(rows);
            }
            catch (Exception e)
            {
                Log.Error($"[{KleeMod.ModId}] model loc rows for '{table}' failed to merge: {e}");
            }
        }
    }

    /// <summary>BaseLib's category → table map, read off BaseLib so the two
    /// cannot disagree; the local copy is used only if the field moved.</summary>
    public static string? TableForCategory(string category)
    {
        var baseLib = typeof(SimpleLoc).Assembly
            .GetType("BaseLib.Patches.Localization.ModelLocPatch");
        if (AccessTools.Field(baseLib, "CategoryToLocTable")?.GetValue(null)
            is IDictionary<string, string?> map)
        {
            return map.TryGetValue(category, out var t) ? t : null;
        }
        return LocalCategoryMap.TryGetValue(category, out var local) ? local : null;
    }

    private static readonly Dictionary<string, string> LocalCategoryMap = new(StringComparer.Ordinal)
    {
        [ModelId.SlugifyCategory("ActModel")] = "acts",
        [ModelId.SlugifyCategory("AfflictionModel")] = "afflictions",
        [ModelId.SlugifyCategory("CardModel")] = "cards",
        [ModelId.SlugifyCategory("CharacterModel")] = "characters",
        [ModelId.SlugifyCategory("EnchantmentModel")] = "enchantments",
        [ModelId.SlugifyCategory("EncounterModel")] = "encounters",
        [ModelId.SlugifyCategory("EpochModel")] = "epochs",
        [ModelId.SlugifyCategory("ModifierModel")] = "modifiers",
        [ModelId.SlugifyCategory("MonsterModel")] = "monsters",
        [ModelId.SlugifyCategory("OrbModel")] = "orbs",
        [ModelId.SlugifyCategory("PotionModel")] = "potions",
        [ModelId.SlugifyCategory("PowerModel")] = "powers",
        [ModelId.SlugifyCategory("RelicModel")] = "relics",
        [ModelId.SlugifyCategory("DynamicVar")] = "static_hover_tips",
    };
}

// ---------------------------------------------------------------------------
//  The seams
// ---------------------------------------------------------------------------

/// <summary>
/// Boot: the first table set is built inside the <c>LocManager</c>
/// constructor, before <c>LocManager.Instance</c> exists, so the boot pass
/// runs here, once the tables do (EB-759's seam, kept).
/// </summary>
[HarmonyPatch(typeof(LocManager), nameof(LocManager.Initialize))]
internal static class LocManager_Initialize_Patch
{
    [HarmonyPostfix]
    public static void Postfix()
    {
        EnglishLoc.ApplyToCurrent();
    }
}

/// <summary>
/// Every later table set: <c>SetLanguage</c> and the game's English override
/// both build tables through <c>LoadTablesFromPath</c>, which a non-English
/// language calls for English first (its fallback). The postfix runs before
/// the new set is installed and before the game's locale-change callbacks
/// fire, so no screen redraws without our rows.
/// </summary>
[HarmonyPatch(typeof(LocManager), "LoadTablesFromPath", new[] { typeof(string), typeof(bool) })]
internal static class LocManager_LoadTablesFromPath_Patch
{
    [HarmonyPostfix]
    public static void Postfix(
        string language,
        (Dictionary<string, LocTable> tables, bool overridesActive, List<LocValidationError> validationErrors) __result)
    {
        // At boot the boot pass above does this, once LocManager.Instance
        // exists; our injectors were written for that moment.
        if (LocManager.Instance == null) return;
        try
        {
            EnglishLoc.ApplyToTables(language, __result.tables);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] loc rows failed to re-apply for '{language}': {e}");
        }
    }
}

/// <summary>
/// BaseLib writes every <c>ILocalizationProvider</c>'s rows into the CURRENT
/// table at <c>ModelDb.Init</c>. Ours are taken out of its view here and go
/// to the English table instead (<see cref="ModelDb_Init_EnglishRows_Patch"/>).
/// If this patch fails to arm, the only cost is the old behaviour: our rows
/// sit in the current table as well.
/// </summary>
[HarmonyPatch]
internal static class BaseLib_ModelLocPatch_SkipOurs_Patch
{
    private static MethodBase? TargetMethod() =>
        AccessTools.Method(
            typeof(SimpleLoc).Assembly.GetType("BaseLib.Patches.Localization.ModelLocPatch"),
            "AddModelLoc");

    [HarmonyPrefix]
    private static void Prefix(ref Dictionary<ModelId, AbstractModel> __0)
    {
        __0 = EnglishLoc.WithoutOurs(__0);
    }
}

/// <summary>Our model rows, captured once and written to the English table.</summary>
[HarmonyPatch(typeof(ModelDb), nameof(ModelDb.Init))]
internal static class ModelDb_Init_EnglishRows_Patch
{
    // FIRST among the postfixes, so any other reader of the tables at the end
    // of ModelDb.Init finds our rows, as it did when BaseLib wrote them.
    [HarmonyPostfix]
    [HarmonyPriority(Priority.First)]
    private static void Postfix(Dictionary<ModelId, AbstractModel> ____contentById)
    {
        try
        {
            EnglishLoc.RecordModelRows(____contentById);
            foreach (var (table, rows) in EnglishLoc.CapturedModelRows)
            {
                EnglishLoc.Table(table).MergeWith(rows);
            }
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] model loc rows failed to reach the English table: {e}");
        }
    }
}
