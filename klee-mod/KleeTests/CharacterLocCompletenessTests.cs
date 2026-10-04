using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// Every character this mod ships carries every per-character row the base
/// game reads off the "characters" table.
///
/// WHY. The game builds these keys from <c>Character.Id.Entry</c> at the
/// moment it needs them -- the co-op end-turn ping bubble is
/// <c>&lt;entry&gt;.banter.alive.endTurnPing</c> -- and a key with no row
/// renders as the raw key. All four characters shipped with only title,
/// description and pronouns, so the ping bubble printed
/// "KLEEMOD-VARKA.banter.alive.endTurnPing" in the 2026-10-03 co-op playtest.
/// KleeSelfCheck R5 only ever checked title and description.
///
/// The set is BaseLib's <c>CharacterLoc</c> record (the rows a modded
/// character is expected to supply) plus <c>bestiaryQuote</c>, which every
/// base character has. Characters are found by reflection, so a fifth one is
/// covered the day it compiles. The models are allocated uninitialised: their
/// constructors register with the game's tables, and <c>Localization</c> is a
/// pure list builder.
/// </summary>
public class CharacterLocCompletenessTests
{
    public static readonly string[] RequiredKeys =
    {
        "title", "titleObject", "description",
        "pronounSubject", "pronounObject", "pronounPossessive", "possessiveAdjective",
        "aromaPrinciple",
        "banter.alive.endTurnPing", "banter.dead.endTurnPing",
        "bestiaryQuote", "eventDeathPrevention", "goldMonologue",
        "cardsModifierTitle", "cardsModifierDescription",
    };

    public static IEnumerable<object[]> Characters() =>
        typeof(Varka).Assembly.GetTypes()
            .Where(t => !t.IsAbstract && typeof(CustomCharacterModel).IsAssignableFrom(t))
            .OrderBy(t => t.Name, StringComparer.Ordinal)
            .Select(t => new object[] { t });

    [Fact]
    public void All_four_characters_are_found()
    {
        var names = Characters().Select(row => ((Type)row[0]).Name).ToList();
        foreach (var expected in new[] { "Furina", "Klee", "Kokomi", "Varka" })
        {
            Assert.Contains(expected, names);
        }
    }

    [Theory]
    [MemberData(nameof(Characters))]
    public void Every_base_character_row_is_present_and_non_empty(Type type)
    {
        var model = (CustomCharacterModel)RuntimeHelpers.GetUninitializedObject(type);
        var rows = model.Localization ?? new List<(string, string)>();
        var byKey = rows.GroupBy(r => r.Item1, StringComparer.Ordinal)
            .ToDictionary(g => g.Key, g => g.Last().Item2, StringComparer.Ordinal);

        var missing = RequiredKeys
            .Where(k => !byKey.TryGetValue(k, out var v) || string.IsNullOrWhiteSpace(v))
            .ToList();
        Assert.True(missing.Count == 0,
            $"{type.Name} is missing characters-table rows: {string.Join(", ", missing)}. "
            + "The game renders a missing row as its raw key.");

        var duplicates = rows.GroupBy(r => r.Item1, StringComparer.Ordinal)
            .Where(g => g.Count() > 1).Select(g => g.Key).ToList();
        Assert.True(duplicates.Count == 0,
            $"{type.Name} repeats rows: {string.Join(", ", duplicates)}");
    }
}
