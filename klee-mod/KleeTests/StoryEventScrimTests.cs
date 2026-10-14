using System.Linq;
using System.Reflection;
using KleeMod.Story;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Events;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE STORY PAGE'S TEXT SCRIM (owner, 2026-10-13: "the event has a yellow
/// title and the text is in white, over a white-blue background that's hard
/// to make out").
///
/// On the suite's headless terms: the numbers are held against the base
/// layout and the measured portraits; the Harmony seam and the node it adds
/// are STRUCTURAL pins, because a layout needs the game. The look is the
/// live check (any Klee or Varka story event).
/// </summary>
public class StoryEventScrimTests
{
    /// <summary>Base text column's left edge: centre minus 38 px of 2560.</summary>
    private const float TextColumnStart = (1280f - 38f) / 2560f;

    [Fact]
    public void The_scrim_is_clear_on_the_left_and_full_before_the_text_column()
    {
        var stops = StoryEventScrim.Stops;
        Assert.Equal(0f, stops[0].Offset);
        Assert.Equal(1f, stops[^1].Offset);
        Assert.True(stops.Zip(stops.Skip(1)).All(p => p.First.Offset < p.Second.Offset));

        // The picture's subject (left third) stays as painted.
        Assert.All(stops.Where(s => s.Offset <= 0.28f), s => Assert.Equal(0f, s.Alpha));

        // Every stop from the column's start rightwards is at full alpha.
        var full = stops.Max(s => s.Alpha);
        var reached = stops.First(s => s.Alpha == full).Offset;
        Assert.True(reached < TextColumnStart, $"full alpha at {reached}, text starts at {TextColumnStart}");
        Assert.All(stops.Where(s => s.Offset >= reached), s => Assert.Equal(full, s.Alpha));
    }

    [Fact]
    public void Under_the_scrim_the_brightest_story_portrait_reads_like_base_event_art()
    {
        // Measured text-column luminance: base event art 0.00-0.13; the
        // brightest story portrait (Klee's proto_ko_fish_fry) 0.81, a pure
        // white field 1.0.
        Assert.True(StoryEventScrim.Dimmed(0.81f) <= 0.15f);
        Assert.True(StoryEventScrim.Dimmed(1.0f) <= 0.20f);
        // Dark, never coloured: no channel above 0.06.
        Assert.All(StoryEventScrim.Rgb, c => Assert.InRange(c, 0f, 0.06f));
    }

    [Fact]
    public void The_patch_adds_the_scrim_after_the_layout_draws_its_portrait()
    {
        var patch = typeof(StoryEventScrim).Assembly.GetTypes()
            .Single(t => t.Name == "NEventLayout_InitializeVisuals_StoryScrim_Patch");
        var info = patch.GetCustomAttribute<HarmonyLib.HarmonyPatch>()!.info;
        Assert.Equal(typeof(NEventLayout), info.declaringType);
        Assert.Equal("InitializeVisuals", info.methodName);
        Assert.NotNull(typeof(NEventLayout).GetMethod("InitializeVisuals", HeadlessGame.All));

        // The fields the postfix injects (____event, ____portrait) exist on
        // the real layout with the types it asks for.
        var ev = typeof(NEventLayout).GetField("_event", HeadlessGame.All);
        Assert.NotNull(ev);
        Assert.Equal(typeof(EventModel), ev!.FieldType);
        var portrait = typeof(NEventLayout).GetField("_portrait", HeadlessGame.All);
        Assert.NotNull(portrait);
        Assert.Equal(typeof(Godot.TextureRect), portrait!.FieldType);

        var postfix = patch.GetMethod("Postfix", HeadlessGame.All)!;
        Assert.Equal(new[] { "__instance", "____event", "____portrait" },
            postfix.GetParameters().Select(p => p.Name));
        var calls = Il.Calls(postfix);
        Assert.Contains("NEventLayout_InitializeVisuals_StoryScrim_Patch.Build", calls);
        Assert.Contains(calls, c => c.EndsWith(".MoveChild"));
    }
}
