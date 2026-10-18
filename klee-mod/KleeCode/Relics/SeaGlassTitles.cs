using System;
using System.Collections.Generic;
using System.Linq;

namespace KleeMod.Relics;

/// <summary>
/// SEA GLASS'S TITLE FOR EACH OF OUR CHARACTERS (the off-character fix,
/// 2026-10-18). Orobas offers Sea Glass for one random other character, ours
/// included, and the relic's title is the row
/// <c>relics/SEA_GLASS.&lt;character entry&gt;.title</c> (decomp:
/// <c>Models.Relics/SeaGlass.cs</c>, <c>Title</c>). The base game ships a row
/// for its five ("Demon Glass", "Gear Glass", ...) and none for a modded
/// character, and a missing row throws <c>LocException</c> when the title is
/// read. <c>KleeMod.InjectLocStrings</c> merges these rows into the
/// <c>relics</c> table; <c>SeaGlassTitleTests</c> pins one row per character.
/// </summary>
public static class SeaGlassTitles
{
    /// <summary>One title per character this mod ships, in the base game's
    /// "&lt;word&gt; Glass" form.</summary>
    public static readonly IReadOnlyList<(Type Character, string Title)> Rows =
        new[]
        {
            (typeof(global::KleeMod.Klee), "Spark Glass"),
            (typeof(global::KleeMod.Kokomi), "Coral Glass"),
            (typeof(global::KleeMod.Furina), "Tide Glass"),
            (typeof(global::KleeMod.Varka), "Gale Glass"),
            (typeof(global::KleeMod.Yae), "Sakura Glass"),
        };

    /// <summary>The <c>relics</c> rows, keyed by each character's model
    /// entry as <paramref name="entryOf"/> names it (in the game,
    /// <c>ModelDb.GetId(type).Entry</c>, which BaseLib prefixes). PURE.
    /// </summary>
    public static Dictionary<string, string> LocRows(Func<Type, string> entryOf) =>
        Rows.ToDictionary(r => Key(entryOf(r.Character)), r => r.Title,
                          StringComparer.Ordinal);

    /// <summary>The row Sea Glass reads for a character entry.</summary>
    public static string Key(string characterEntry) =>
        "SEA_GLASS." + characterEntry + ".title";
}
