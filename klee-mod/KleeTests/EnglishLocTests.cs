using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using HarmonyLib;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// LOCALIZATION ROUTE B (2026-10-19): our English goes to the English table.
///
/// WHAT IS TESTED HERE. <c>LocManager</c> itself is outside the headless
/// boundary (README), but <c>LocTable</c> is a plain class, and the English
/// fallback the game relies on is <c>LocTable</c>'s own (a table holds a
/// fallback and answers a missing key from it). So these tests build table
/// sets the way <c>LoadTablesFromPath</c> does -- an English set, and a
/// local set whose every table falls back to its English twin -- run the
/// mod's real pass over them, and read the result through the game's own
/// <c>GetRawText</c> / <c>IsLocalKey</c>, which is exactly what
/// <c>LocManager.SmartFormat</c> asks to pick the culture.
///
/// WHAT ONLY A LIVE BOOT CAN SAY: that the Harmony seams fire in the order
/// argued in <c>EnglishLoc.cs</c> (the patch targets are pinned to exist
/// below, not to run), and what the screen shows.
/// </summary>
public class EnglishLocTests
{
    /// <summary>An English set and a Simplified Chinese set over it, built
    /// on demand per table name, the way the game pairs them.</summary>
    private sealed class TableSets
    {
        public readonly Dictionary<string, LocTable> English = new(StringComparer.Ordinal);
        public readonly Dictionary<string, LocTable> Local = new(StringComparer.Ordinal);
        public readonly Dictionary<string, Dictionary<string, string>> LocalSeed = new(StringComparer.Ordinal);
        public readonly Dictionary<string, Dictionary<string, string>> EnglishSeed = new(StringComparer.Ordinal);

        public LocTable En(string name)
        {
            if (!English.TryGetValue(name, out var table))
            {
                var data = EnglishSeed.TryGetValue(name, out var seed)
                    ? new Dictionary<string, string>(seed)
                    : new Dictionary<string, string>();
                English[name] = table = new LocTable(name, data);
            }
            return table;
        }

        public LocTable Zh(string name)
        {
            if (!Local.TryGetValue(name, out var table))
            {
                var data = LocalSeed.TryGetValue(name, out var seed)
                    ? new Dictionary<string, string>(seed)
                    : new Dictionary<string, string>();
                Local[name] = table = new LocTable(name, data, En(name));
            }
            return table;
        }

        public void Apply() => EnglishLoc.Apply(En, Zh);
    }

    /// <summary>The Sea Glass rows are the LAST merge in
    /// <c>InjectLocStrings</c>, so their presence says the whole method ran
    /// rather than dying in its own catch.</summary>
    private static Dictionary<string, string> SeaGlassRows() =>
        global::KleeMod.Relics.SeaGlassTitles.LocRows(t => ModelDb.GetId(t).Entry);

    [Fact]
    public void Our_rows_land_in_the_English_table_and_the_local_table_reads_them_through_its_fallback()
    {
        var sets = new TableSets();
        sets.Apply();

        var relicsEn = sets.En("relics");
        var relicsZh = sets.Zh("relics");
        Assert.NotEmpty(SeaGlassRows());
        foreach (var (key, value) in SeaGlassRows())
        {
            Assert.Equal(value, relicsEn.GetRawText(key));
            // Not a LOCAL row: SmartFormat formats it with English culture,
            // which is the "Draw 2 card." fix.
            Assert.False(relicsZh.IsLocalKey(key), key);
            Assert.Equal(value, relicsZh.GetRawText(key));
        }

        // No table in the local set holds a row the pass wrote, except what
        // a derivation found in the local language (none here: the base
        // tables are empty).
        foreach (var (name, table) in sets.Local)
        {
            Assert.Empty(table.Keys);
        }
        Assert.Contains(sets.English.Values, t => t.Keys.Any());
    }

    [Fact]
    public void A_shipped_translation_wins_per_key_and_the_rest_falls_back()
    {
        var rows = SeaGlassRows().OrderBy(r => r.Key, StringComparer.Ordinal).ToList();
        var translated = rows[0].Key;
        var sets = new TableSets();
        sets.LocalSeed["relics"] = new Dictionary<string, string> { [translated] = "海玻璃" };
        sets.Apply();

        var relicsZh = sets.Zh("relics");
        Assert.True(relicsZh.IsLocalKey(translated));
        Assert.Equal("海玻璃", relicsZh.GetRawText(translated));
        Assert.Equal(rows[0].Value, sets.En("relics").GetRawText(translated));
        foreach (var (key, value) in rows.Skip(1))
        {
            Assert.Equal(value, relicsZh.GetRawText(key));
        }
    }

    [Fact]
    public void A_rebuilt_table_set_gets_every_row_again()
    {
        // SetLanguage builds a new set from files; the seam runs the pass on
        // each new set, so a second pass over fresh tables must reproduce the
        // first exactly.
        var first = new TableSets();
        first.Apply();
        var second = new TableSets();
        second.Apply();

        Assert.Equal(first.English.Keys.OrderBy(k => k), second.English.Keys.OrderBy(k => k));
        foreach (var (name, table) in first.English)
        {
            var other = second.English[name];
            Assert.Equal(table.Keys.OrderBy(k => k, StringComparer.Ordinal),
                         other.Keys.OrderBy(k => k, StringComparer.Ordinal));
            foreach (var key in table.Keys)
            {
                Assert.Equal(table.GetRawText(key), other.GetRawText(key));
            }
        }
    }

    [Fact]
    public void A_derived_row_copies_each_language_from_its_own_table()
    {
        var sets = new TableSets();
        sets.EnglishSeed["ancients"] = new Dictionary<string, string>
        {
            ["BASE.next"] = "Continue",
            ["BASE.other"] = "Other",
        };
        sets.LocalSeed["ancients"] = new Dictionary<string, string>
        {
            ["BASE.next"] = "继续",
            ["OURS.kept"] = "已翻译",
        };

        EnglishLoc.Within(sets.En, sets.Zh, () =>
            EnglishLoc.MergeDerived("ancients", table => new Dictionary<string, string>
            {
                ["OURS.next"] = table.GetRawText("BASE.next"),
                ["OURS.other"] = table.GetRawText("BASE.other"),
                ["OURS.kept"] = table.GetRawText("BASE.next"),
            }));

        var en = sets.En("ancients");
        var zh = sets.Zh("ancients");
        Assert.Equal("Continue", en.GetRawText("OURS.next"));
        // The local language has its own word: it is copied, as a local row.
        Assert.True(zh.IsLocalKey("OURS.next"));
        Assert.Equal("继续", zh.GetRawText("OURS.next"));
        // The local language falls back for the source: so does the copy.
        Assert.False(zh.IsLocalKey("OURS.other"));
        Assert.Equal("Other", zh.GetRawText("OURS.other"));
        // A shipped translation is never overwritten.
        Assert.Equal("已翻译", zh.GetRawText("OURS.kept"));
    }

    [Fact]
    public void Model_rows_are_kept_out_of_BaseLib_and_written_as_BaseLib_would()
    {
        var ours = new ProtoKoKapow();
        var baseCard = (AbstractModel)RuntimeHelpers.GetUninitializedObject(
            typeof(MegaCrit.Sts2.Core.Models.Cards.StrikeIronclad));
        var oursId = new ModelId(ModelDb.GetCategory(typeof(ProtoKoKapow)), "KLEEMOD-PROTO_KO_KAPOW");
        var baseId = ModelDb.GetId(typeof(MegaCrit.Sts2.Core.Models.Cards.StrikeIronclad));
        var content = new Dictionary<ModelId, AbstractModel> { [oursId] = ours, [baseId] = baseCard };

        var forBaseLib = EnglishLoc.WithoutOurs(content);
        Assert.Single(forBaseLib);
        Assert.True(forBaseLib.ContainsKey(baseId));

        EnglishLoc.RecordModelRows(content);
        var cards = EnglishLoc.CapturedModelRows["cards"];
        Assert.Equal("Kaboom!", cards["KLEEMOD-PROTO_KO_KAPOW.title"]);

        var sets = new TableSets();
        sets.Apply();
        Assert.Equal("Kaboom!", sets.En("cards").GetRawText("KLEEMOD-PROTO_KO_KAPOW.title"));
        Assert.False(sets.Zh("cards").IsLocalKey("KLEEMOD-PROTO_KO_KAPOW.title"));
    }

    [Fact]
    public void Every_patch_target_and_private_field_still_resolves()
    {
        // The seams (EnglishLoc.cs). A game or BaseLib update that moves one
        // of these breaks the route silently at boot; here it is loud.
        var load = AccessTools.Method(typeof(LocManager), "LoadTablesFromPath",
            new[] { typeof(string), typeof(bool) });
        Assert.NotNull(load);
        Assert.Equal(
            typeof(ValueTuple<Dictionary<string, LocTable>, bool, List<LocValidationError>>),
            load!.ReturnType);
        Assert.True(load.IsStatic);

        var baseLib = typeof(BaseLib.Patches.Localization.SimpleLoc).Assembly
            .GetType("BaseLib.Patches.Localization.ModelLocPatch");
        Assert.NotNull(baseLib);
        var addModelLoc = AccessTools.Method(baseLib, "AddModelLoc");
        Assert.NotNull(addModelLoc);
        Assert.Equal(typeof(Dictionary<ModelId, AbstractModel>),
                     addModelLoc!.GetParameters()[0].ParameterType);
        Assert.NotNull(AccessTools.Field(baseLib, "CategoryToLocTable"));

        Assert.NotNull(AccessTools.Field(typeof(LocTable), "_fallback"));
        Assert.NotNull(AccessTools.Field(typeof(LocManager), "_tables"));
        Assert.NotNull(AccessTools.Field(typeof(ModelDb), "_contentById"));
        Assert.NotNull(AccessTools.Method(typeof(ModelDb), nameof(ModelDb.Init)));
        Assert.Equal("cards", EnglishLoc.TableForCategory(ModelDb.GetCategory(typeof(ProtoKoKapow))));
    }

    [Fact]
    public void No_injector_reaches_the_current_language_table()
    {
        // Every merge goes through EnglishLoc.Table / MergeDerived. A direct
        // `LocManager.Instance.GetTable(..).MergeWith` would put English back
        // into the local table.
        var injectors = new[]
        {
            Il.Method("KleeMod", "InjectLocStrings"),
            Il.Method("TeyvatLoc", "Inject"),
            Il.Method("StoryLoc", "Inject"),
            Il.Method("AbyssLoc", "Inject"),
        };
        foreach (var method in injectors)
        {
            Assert.DoesNotContain("LocManager.GetTable", Il.Calls(method));
        }
    }

    // ==================================================================
    // `EB-733` -- SetsOffFirst reads a flag, not the English row
    // ==================================================================

    /// <summary>The rule the method used to apply to the authored English
    /// row, kept here as the oracle the flag must agree with.</summary>
    private static bool LegacySetsOffFirst(CustomCardModel card)
    {
        var rows = card.Localization;
        if (rows == null) return false;
        foreach (var row in rows)
        {
            if (row.Item1 != "description" || row.Item2 == null) continue;
            return row.Item2.StartsWith("[gold]Set off[/gold] the enemy.", StringComparison.Ordinal)
                || row.Item2.StartsWith("[gold]Set off[/gold].", StringComparison.Ordinal)
                || row.Item2.StartsWith("[gold]Set off[/gold] only your largest ", StringComparison.Ordinal);
        }
        return false;
    }

    [Fact]
    public void The_set_off_first_flag_matches_the_old_text_read_on_every_card()
    {
        var cards = typeof(EnglishLoc).Assembly.GetTypes()
            .Where(t => !t.IsAbstract && typeof(CustomCardModel).IsAssignableFrom(t))
            .ToList();
        Assert.NotEmpty(cards);
        var flagged = 0;
        foreach (var type in cards)
        {
            var card = (CustomCardModel)RuntimeHelpers.GetUninitializedObject(type);
            bool legacy;
            try
            {
                legacy = LegacySetsOffFirst(card);
            }
            catch
            {
                // A hand-written row that needs a constructed model: the old
                // read could not have answered for it headlessly either; the
                // flag is a compile-time fact and is still checked below.
                Assert.False(card is ISetsOffFirstCard, type.Name);
                continue;
            }
            Assert.True(legacy == KleeCardTooltips.SetsOffFirst(card),
                $"{type.Name}: text read says {legacy}, flag says {!legacy}");
            if (legacy) flagged++;
        }
        Assert.True(flagged >= 10, $"only {flagged} Set-off-first cards found");
    }
}
