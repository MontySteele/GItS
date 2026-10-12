using System;
using System.IO;
using System.Runtime.CompilerServices;
using STS2_MCP;
using Xunit;

namespace KleeTests;

/// <summary>
/// The bridge's event `body` (2026-10-12). It was read off the room's
/// canonical event, which never has a page, so every event sent
/// `"body": null` and no seat read an event's story text. The rules live in
/// `vendor/STS2_MCP/gits/GitsEventBody.cs` (compiled here, one file, no fork);
/// the game-side read in `gits/GitsEventPage.cs` is pinned by source.
/// </summary>
public class GitsEventBodyTests
{
    private const string Starsnatch =
        "The pond at the foot of the cliff is full of fat, silver fish. Klee has "
      + "three bombs left and nobody is watching. She remembers Jean's face the "
      + "last time.";

    [Fact]
    public void A_story_events_paragraph_is_the_body()
    {
        // The local copy's INITIAL page, the canonical event's null page.
        Assert.Equal(Starsnatch, GitsEventBody.Choose(() => Starsnatch, () => null));
    }

    [Fact]
    public void A_base_events_formatted_page_comes_out_plain()
    {
        var formatted =
            "You find a [gold]Golden Idol[/gold] on a [color=#ff4040]pedestal[/color].\r\n"
          + "[i]It is very shiny.[/i]   \n\n\n\n"
          + "Take it for [b]{0}[/b] HP? [img]res://images/ui/energy_icon.png[/img]";
        Assert.Equal(
            "You find a Golden Idol on a pedestal.\nIt is very shiny.\n\n"
          + "Take it for {0} HP? [energy_icon.png]",
            GitsEventBody.Plain(formatted));
    }

    [Fact]
    public void The_Abyss_choice_page_still_prints_its_sentence()
    {
        var page = "The Spiral Abyss stirs before the Ancient. Take one Blessing. "
                 + "The enemies take one of the two Shadows you pass, at random.";
        Assert.Equal(page, GitsEventBody.Choose(() => page, () => null));
    }

    [Fact]
    public void The_local_page_wins_and_the_canonical_one_is_the_fallback()
    {
        Assert.Equal("Local.", GitsEventBody.Choose(() => "Local.", () => "Canonical."));
        Assert.Equal("Canonical.", GitsEventBody.Choose(() => null, () => "Canonical."));
        Assert.Equal("Canonical.", GitsEventBody.Choose(() => "  [b][/b] \n", () => "Canonical."));
        Assert.Equal("Canonical.",
            GitsEventBody.Choose(() => throw new ArgumentOutOfRangeException(), () => "Canonical."));
        Assert.Null(GitsEventBody.Choose(() => null, () => null));
    }

    [Fact]
    public void A_bracket_that_is_no_tag_stays()
    {
        Assert.Equal("Lose [3] HP.", GitsEventBody.Plain("Lose [3] HP."));
    }

    [Fact]
    public void The_state_builder_reads_the_page_for_every_event()
    {
        var builder = Source(Path.Combine("vendor", "STS2_MCP", "McpMod.StateBuilder.cs"));
        Assert.Contains("state[\"body\"] = GitsEventPageBody(eventRoom, eventModel);", builder);
        Assert.DoesNotContain("GitsAbyssPageBody", builder);

        var page = Source(Path.Combine("vendor", "STS2_MCP", "gits", "GitsEventPage.cs"));
        // The local copy first (guarded), the canonical event second.
        Assert.Contains("GitsLocalEvent.OrNothing(() => eventRoom.LocalMutableEvent)", page);
        Assert.Contains("GitsFormattedPage(canonical)", page);
        // The game's own dressing of the page (NEventRoom.SetDescription).
        Assert.Contains("AddDetailsTo(page)", page);
        Assert.Contains("ev.DynamicVars.AddTo(page)", page);
        Assert.Contains("page.GetFormattedText()", page);
    }

    private static string Source(string relativePath, [CallerFilePath] string here = "")
    {
        var dir = Path.GetDirectoryName(here);
        while (dir != null)
        {
            var candidate = Path.Combine(dir, relativePath);
            if (File.Exists(candidate)) return File.ReadAllText(candidate);
            dir = Path.GetDirectoryName(dir);
        }
        throw new FileNotFoundException(relativePath);
    }
}
