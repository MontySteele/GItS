using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// SEA GLASS NAMES EVERY CHARACTER WE SHIP (the off-character fix,
/// 2026-10-18). Orobas offers Sea Glass for one random other character, ours
/// included, and its title is <c>relics/SEA_GLASS.&lt;entry&gt;.title</c>,
/// which the base game defines only for its own five; a missing row throws
/// when the title is read. Characters are found by reflection, so a sixth is
/// covered the day it compiles.
/// </summary>
public class SeaGlassTitleTests
{
    [Fact]
    public void Every_character_we_ship_has_one_sea_glass_title()
    {
        var characters = typeof(Varka).Assembly.GetTypes()
            .Where(t => !t.IsAbstract && typeof(CustomCharacterModel).IsAssignableFrom(t))
            .ToList();
        Assert.True(characters.Count >= 5, $"only {characters.Count} characters found");

        var rowed = SeaGlassTitles.Rows.Select(r => r.Character).ToList();
        foreach (var character in characters)
        {
            Assert.Equal(1, rowed.Count(t => t == character));
        }
        Assert.All(SeaGlassTitles.Rows, r => Assert.False(string.IsNullOrWhiteSpace(r.Title)));
        Assert.Equal(SeaGlassTitles.Rows.Count,
                     SeaGlassTitles.Rows.Select(r => r.Title).Distinct().Count());
    }

    [Fact]
    public void The_rows_are_keyed_as_sea_glass_reads_them()
    {
        var rows = SeaGlassTitles.LocRows(t => "KLEEMOD-" + t.Name.ToUpperInvariant());
        Assert.Equal("Gale Glass", rows["SEA_GLASS.KLEEMOD-VARKA.title"]);
        Assert.Equal("Tide Glass", rows["SEA_GLASS.KLEEMOD-FURINA.title"]);
        Assert.Equal(SeaGlassTitles.Rows.Count, rows.Count);
    }

    [Fact]
    public void The_loc_injection_merges_them()
    {
        var calls = Il.Calls(typeof(Varka).Assembly.GetType("KleeMod.KleeMod")!
            .GetMethod("InjectLocStrings", HeadlessGame.All)!);
        Assert.Contains("SeaGlassTitles.LocRows", calls);
    }
}
