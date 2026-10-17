using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// THE WORKSHOP RELEASE BUILD (2026-10-16,
/// <c>review/active/workshop-readiness-2026-10-14.md</c>, checklist items 4
/// and 12). Two build properties, both off in every build that names
/// neither, so a dev deploy, a seat deploy and <c>dotnet test</c> are
/// unchanged:
///
///   -p:WorkshopRelease=true   defines WORKSHOP_RELEASE: play telemetry
///                             writes only when GITS_TELEMETRY_FEED is set
///                             (the seat lanes set it; a player never does).
///   -p:GitsKits=klee+varka    the kits that ship, by character id. Empty
///                             (the default) ships every kit. A kit left out
///                             registers no character (see
///                             <see cref="ReleaseKits"/>).
///
/// <c>tools/package_workshop.py</c> is the one caller that sets them;
/// <c>docs/current/operations/workshop.md</c> is the procedure.
/// </summary>
public static class WorkshopRelease
{
    /// <summary>True only in a <c>-p:WorkshopRelease=true</c> build.</summary>
    public static readonly bool IsRelease =
#if WORKSHOP_RELEASE
        true;
#else
        false;
#endif

    /// <summary>
    /// Does play telemetry write a fight record? A dev build always does
    /// ([USER]'s own play is the human feed `tools/telemetry_report.py
    /// --feed human` reads); a release build only when a harness declared a
    /// feed. PURE: the test pins both builds' answers off this one line.
    /// </summary>
    public static bool TelemetryWrites(bool release, string? declaredFeed) =>
        !release || !string.IsNullOrWhiteSpace(declaredFeed);

    /// <summary>The assembly metadata key the csproj writes $(GitsVariant) to.</summary>
    public const string VariantKey = "GitsVariant";

    /// <summary>
    /// The Workshop package this dll was built for (<c>beta</c> or
    /// <c>public</c>, <c>-p:GitsVariant=...</c>, set by
    /// <c>tools/package_workshop.py</c>), or null in a dev build.
    /// </summary>
    public static string? Variant =>
        typeof(WorkshopRelease).Assembly
            .GetCustomAttributes<AssemblyMetadataAttribute>()
            .FirstOrDefault(a => a.Key == VariantKey)?.Value;

    /// <summary>
    /// The mod's plain version (<c>0.3.0</c>): the informational version up
    /// to its <c>+</c> mark, which a Workshop build sets from
    /// <c>--version</c>. "0.0.0" when the assembly carries none.
    /// </summary>
    public static string ModVersion
    {
        get
        {
            var info = typeof(WorkshopRelease).Assembly
                .GetCustomAttribute<AssemblyInformationalVersionAttribute>()?
                .InformationalVersion;
            return PlainVersion(info);
        }
    }

    /// <summary>PURE: "0.3.0+workshop.beta" -> "0.3.0".</summary>
    public static string PlainVersion(string? informational)
    {
        if (string.IsNullOrWhiteSpace(informational)) return "0.0.0";
        var plain = informational.Split('+')[0].Trim();
        var clean = new string(plain.Where(c => char.IsAsciiLetterOrDigit(c)
                                                || c == '.' || c == '-' || c == '_')
                                    .Take(32).ToArray());
        return clean.Length == 0 ? "0.0.0" : clean;
    }
}

/// <summary>
/// WHICH KITS THIS BUILD SHIPS (checklist item 12: a public package without
/// Yae, a beta package with everything).
///
/// HOW A KIT IS LEFT OUT. Every kit still COMPILES, so nothing that names
/// one of its types breaks and a save that holds one of its card ids still
/// resolves the model. What goes is the CHARACTER: BaseLib registers a
/// <c>CustomCharacterModel</c> from its constructor into
/// <c>CustomContentDictionary.CustomCharacters</c>, and every list a player
/// can reach is read off that list or off <c>ModelDb.AllCharacters</c>,
/// which BaseLib builds from it: character select, the random pick, the
/// compendium filters, the stats screen, and the base game's
/// <c>AllCharacterCardPools</c>, <c>AllCharacterRelicPools</c>,
/// <c>AllCharacterPotionPools</c>, <c>AllCards</c> and <c>AllRelics</c>
/// (0.111.0 <c>ModelDb</c>). <c>Patches/ReleaseKitsPatch.cs</c> takes the
/// left-out character back off that list the moment it is added, so its card
/// pool, relic pool, starter deck and relics, its Ancient cards and its
/// personal-pool Companions have no door. Universal Companions stay: the
/// Inazuma roster's "Yae Miko -- Sesshou Sakura" is a Companion every kit can
/// draft, built on <c>SesshouSakuraPower</c>, not on her shrine.
/// </summary>
public static class ReleaseKits
{
    /// <summary>The assembly metadata key the csproj writes $(GitsKits) to.</summary>
    public const string MetadataKey = "GitsKits";

    /// <summary>Every kit id, in roster order.</summary>
    public static readonly IReadOnlyList<string> Known =
        new[] { "klee", "kokomi", "furina", "varka", "yae" };

    private static IReadOnlyList<string>? _shipped;
    private static bool _read;

    /// <summary>
    /// The kits that ship, or null for every kit. Separators: '+', ',', ';'
    /// or whitespace ('+' is the one an MSBuild command line passes intact).
    /// Unknown ids are dropped. PURE.
    /// </summary>
    public static IReadOnlyList<string>? Parse(string? value)
    {
        if (string.IsNullOrWhiteSpace(value)) return null;
        return value
            .Split(new[] { '+', ',', ';', ' ', '\t' },
                   StringSplitOptions.RemoveEmptyEntries)
            .Select(s => s.Trim().ToLowerInvariant())
            .Where(s => Known.Contains(s))
            .Distinct()
            .ToList();
    }

    /// <summary>This build's list, read once from the assembly metadata.</summary>
    public static IReadOnlyList<string>? Shipped
    {
        get
        {
            if (_read) return _shipped;
            _read = true;
            var value = typeof(ReleaseKits).Assembly
                .GetCustomAttributes<AssemblyMetadataAttribute>()
                .FirstOrDefault(a => a.Key == MetadataKey)?.Value;
            _shipped = Parse(value);
            return _shipped;
        }
    }

    /// <summary>Does <paramref name="shipped"/> carry this kit? PURE.</summary>
    public static bool Ships(string? kitId, IReadOnlyList<string>? shipped) =>
        kitId == null || shipped == null || shipped.Contains(kitId);

    /// <summary>Does this build ship this kit?</summary>
    public static bool Ships(string? kitId) => Ships(kitId, Shipped);

    /// <summary>Does this build ship this character? A character that is
    /// not one of ours always ships.</summary>
    public static bool Ships(CharacterModel? character) => Ships(KitOf(character));

    /// <summary>
    /// Take a left-out kit's character off BaseLib's registered list
    /// (<c>Patches/ReleaseKitsPatch.cs</c> passes
    /// <c>CustomContentDictionary.CustomCharacters</c>). True when it was
    /// removed. With every kit shipping it touches nothing.
    /// </summary>
    public static bool Unregister(IList<BaseLib.Abstracts.CustomCharacterModel> registered,
                                  BaseLib.Abstracts.CustomCharacterModel character,
                                  IReadOnlyList<string>? shipped)
    {
        if (shipped == null || Ships(KitOf(character), shipped)) return false;
        return registered.Remove(character);
    }

    /// <summary>The kit id of one of our characters, or null. PURE.</summary>
    public static string? KitOf(CharacterModel? character) =>
        character switch
        {
            Klee => "klee",
            Kokomi => "kokomi",
            Furina => "furina",
            Powers.IVarkaCharacter => Powers.VarkaPrototype.CharacterId,
            Powers.IYaeCharacter => Powers.YaePrototype.CharacterId,
            _ => null,
        };
}
