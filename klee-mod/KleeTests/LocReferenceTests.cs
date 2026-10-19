using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.RegularExpressions;
using BaseLib.Abstracts;
using BaseLib.Extensions;
using BaseLib.Utils.Attributes;
using KleeMod.Teyvat;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE ENGLISH REFERENCE FOR TRANSLATORS:
/// <c>klee-mod/localization/reference/eng.json</c>, every row this mod
/// authors as <c>{ table: { key: English } }</c>. It is NOT how English
/// ships (English ships from the DLL, <c>EnglishLoc</c>); it is what a
/// translation file is written against and what
/// <c>tools/lint_loc_translations.py</c> checks placeholders and staleness
/// against.
///
/// THIS TEST IS THE STALENESS GATE. It rebuilds the reference from the real
/// assembly and fails if the committed file differs. To rewrite it:
/// <code>GITS_WRITE_LOC_REFERENCE=1 dotnet test --filter LocReferenceTests</code>
///
/// HOW THE ROWS ARE GATHERED. The model rows are read off every model type the
/// way BaseLib's <c>ModelLocPatch</c> writes them. The hand-written merges run
/// for real through <c>EnglishLoc.Apply</c> over empty English tables (so a
/// row copied from base-game text, which an empty table cannot supply, is
/// left out: it is the base game's to translate). The Teyvat frame arm is
/// switched on for the pass, so its rows are in. The English the pck ships
/// as a file (<c>klee-mod/pck-src/klee/localization/eng/</c>) is loaded under
/// the merges first, as the game loads it.
///
/// ONE HEADLESS GAP, CLOSED HERE. At runtime BaseLib prefixes a custom model's
/// entry (<c>KLEEMOD-KLEE</c>); headless there is no BaseLib patch, so an
/// entry a merge builds through <c>ModelDb.GetEntry</c> comes out bare. Each
/// bare entry of one of our custom models is replaced, as a whole key token,
/// by its runtime form. A bare entry a base-game model also has (our Sea
/// Glass card against the base Sea Glass relic) is renamed only inside our
/// model's own table, and a merge that puts such a token there fails the test
/// rather than being guessed at.
/// </summary>
public class LocReferenceTests
{
    private const string WriteVariable = "GITS_WRITE_LOC_REFERENCE";

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null && !Directory.Exists(Path.Combine(dir.FullName, "review")))
        {
            dir = dir.Parent;
        }
        return dir?.FullName ?? throw new InvalidOperationException("repo root not found");
    }

    public static string ReferencePath() =>
        Path.Combine(RepoRoot(), "klee-mod", "localization", "reference", "eng.json");

    private static readonly Assembly Mod = typeof(EnglishLoc).Assembly;

    /// <summary>The entry BaseLib gives a type at runtime (PrefixIdPatch).</summary>
    private static string RuntimeEntry(Type type)
    {
        var custom = type.GetCustomAttribute<CustomIDAttribute>();
        if (custom != null) return custom.ID;
        var bare = ModelDb.GetEntry(type);
        return typeof(ICustomModel).IsAssignableFrom(type) ? type.GetPrefix() + bare : bare;
    }

    private static IEnumerable<Type> OurModelTypes() =>
        Mod.GetTypes().Where(t => !t.IsAbstract && typeof(AbstractModel).IsAssignableFrom(t));

    /// <summary>Bare entry → (runtime entry, our model's own table), for our
    /// models whose entry BaseLib changes.</summary>
    private static Dictionary<string, (string Real, string? Table)> EntryRenames()
    {
        var renames = new Dictionary<string, (string, string?)>(StringComparer.Ordinal);
        foreach (var type in OurModelTypes())
        {
            var bare = ModelDb.GetEntry(type);
            var real = RuntimeEntry(type);
            if (bare != real)
            {
                renames[bare] = (real, EnglishLoc.TableForCategory(ModelDb.GetCategory(type)));
            }
        }
        return renames;
    }

    private static HashSet<string> BaseGameEntries() =>
        typeof(ModelDb).Assembly.GetTypes()
            .Where(t => !t.IsAbstract && typeof(AbstractModel).IsAssignableFrom(t))
            .Select(ModelDb.GetEntry)
            .ToHashSet(StringComparer.Ordinal);

    public static SortedDictionary<string, SortedDictionary<string, string>> Build()
    {
        var reference = new SortedDictionary<string, SortedDictionary<string, string>>(StringComparer.Ordinal);
        void Add(string table, string key, string value)
        {
            if (!reference.TryGetValue(table, out var rows))
            {
                reference[table] = rows = new SortedDictionary<string, string>(StringComparer.Ordinal);
            }
            rows[key] = value;
        }

        // The hand-written merges, run for real.
        var tables = new Dictionary<string, LocTable>(StringComparer.Ordinal);
        LocTable Table(string name)
        {
            if (!tables.TryGetValue(name, out var t))
            {
                // The English the pck ships as a file loads first, as the
                // game loads it (`ModManager.GetModdedLocTables`), and our
                // merges go over it.
                var file = Path.Combine(RepoRoot(), "klee-mod", "pck-src", "klee",
                                        "localization", "eng", name + ".json");
                var data = File.Exists(file)
                    ? JsonSerializer.Deserialize<Dictionary<string, string>>(File.ReadAllText(file))!
                    : new Dictionary<string, string>();
                tables[name] = t = new LocTable(name, data);
            }
            return t;
        }
        foreach (var file in Directory.EnumerateFiles(
                     Path.Combine(RepoRoot(), "klee-mod", "pck-src", "klee", "localization", "eng"), "*.json"))
        {
            Table(Path.GetFileNameWithoutExtension(file));
        }
        var wasEnabled = TeyvatFrame.Enabled;
        TeyvatFrame.Enabled = true;
        try
        {
            EnglishLoc.Within(Table, null, EnglishLoc.RunInjectors);
        }
        finally
        {
            TeyvatFrame.Enabled = wasEnabled;
        }

        var renames = EntryRenames();
        var baseEntries = BaseGameEntries();
        var token = new Regex(@"(?<![A-Za-z0-9_\-])[A-Z0-9_]+(?![A-Za-z0-9_])");
        foreach (var (name, table) in tables)
        {
            foreach (var key in table.Keys)
            {
                var real = token.Replace(key, m =>
                {
                    if (!renames.TryGetValue(m.Value, out var r)) return m.Value;
                    if (!baseEntries.Contains(m.Value)) return r.Real;
                    if (r.Table == name)
                    {
                        throw new InvalidOperationException(
                            $"'{key}' in '{name}': {m.Value} is both ours and the base game's");
                    }
                    return m.Value;
                });
                Add(name, real, table.GetRawText(key));
            }
        }

        // The model rows, as BaseLib's ModelLocPatch writes them.
        foreach (var type in OurModelTypes())
        {
            var model = (AbstractModel)RuntimeHelpers.GetUninitializedObject(type);
            if (model is not ILocalizationProvider provider) continue;
            var rows = provider.Localization;
            if (rows == null) continue;
            var table = provider.LocTable ?? EnglishLoc.TableForCategory(ModelDb.GetCategory(type))
                ?? throw new InvalidOperationException($"no loc table for {type.Name}");
            var entry = RuntimeEntry(type);
            foreach (var (key, value) in rows)
            {
                Add(table, entry + "." + key, BaseLib.Patches.Localization.SimpleLoc.TrySimplify(value));
            }
        }
        return reference;
    }

    public static string Serialize(SortedDictionary<string, SortedDictionary<string, string>> reference)
    {
        var json = JsonSerializer.Serialize(reference, new JsonSerializerOptions
        {
            WriteIndented = true,
            Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
        });
        return json.Replace("\r\n", "\n") + "\n";
    }

    [Fact]
    public void The_committed_English_reference_is_current()
    {
        var built = Serialize(Build());
        var path = ReferencePath();
        if (Environment.GetEnvironmentVariable(WriteVariable) == "1")
        {
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllText(path, built, new UTF8Encoding(false));
        }
        Assert.True(File.Exists(path), $"{path} is missing. Write it with {WriteVariable}=1 dotnet test --filter LocReferenceTests");
        var committed = File.ReadAllText(path, Encoding.UTF8).Replace("\r\n", "\n");
        Assert.True(committed == built,
            $"{path} is stale: the mod's English changed. Rewrite it with "
            + $"{WriteVariable}=1 dotnet test --filter LocReferenceTests and commit it.");
    }

    [Fact]
    public void The_reference_carries_every_kind_of_row()
    {
        var reference = Build();
        // Model rows, a hand-written merge, a story row and a Teyvat row.
        Assert.Contains("KLEEMOD-PROTO_KO_KAPOW.title", reference["cards"].Keys);
        Assert.Contains(reference["relics"].Keys, k => k.StartsWith("SEA_GLASS.KLEEMOD-", StringComparison.Ordinal));
        Assert.True(reference.ContainsKey("acts"));
        Assert.DoesNotContain(reference.Values.SelectMany(r => r.Keys), k => k.Contains("SEA_GLASS.VARKA", StringComparison.Ordinal));
    }
}
