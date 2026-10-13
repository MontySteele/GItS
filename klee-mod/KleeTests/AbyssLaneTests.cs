using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using KleeMod.Abyss;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE SEAT LANES' SPIRAL ABYSS (<see cref="AbyssLane"/>): `understudy.embark
/// --abyss` sets GITS_ABYSS on the launched game, and the Standard lobby's run
/// then carries the modifier. Pinned here headlessly: the variable's words,
/// who adds the modifier, that the lobby's own list is never touched, and the
/// hold-and-release across the character select. The live run (the page over
/// Neow, the co-op client building the same run) is the PR's live check.
/// </summary>
public class AbyssLaneTests
{
    private static SpiralAbyss NewAbyss() =>
        (SpiralAbyss)RuntimeHelpers.GetUninitializedObject(typeof(SpiralAbyss));

    [Fact]
    public void The_variable_is_the_one_embark_sets()
    {
        // tier0/tests/test_embark_abyss.py pins embark.py's side.
        Assert.Equal("GITS_ABYSS", AbyssLane.EnvVar);
    }

    [Theory]
    [InlineData("1", true)]
    [InlineData(" TRUE ", true)]
    [InlineData("yes", true)]
    [InlineData("on", true)]
    [InlineData("", false)]
    [InlineData(null, false)]
    [InlineData("0", false)]
    [InlineData("false", false)]
    [InlineData("abyss", false)]
    public void The_words_it_takes(string? raw, bool expected)
    {
        Assert.Equal(expected, AbyssLane.ParseFlag(raw));
    }

    [Fact]
    public void Only_an_asking_standard_host_without_the_abyss_adds_it()
    {
        Assert.True(AbyssLane.ShouldAdd(true, GameMode.Standard, isClient: false, alreadyHas: false));
        Assert.False(AbyssLane.ShouldAdd(false, GameMode.Standard, false, false));
        Assert.False(AbyssLane.ShouldAdd(true, GameMode.Custom, false, false));
        Assert.False(AbyssLane.ShouldAdd(true, GameMode.Daily, false, false));
        Assert.False(AbyssLane.ShouldAdd(true, GameMode.Standard, isClient: true, alreadyHas: false));
        Assert.False(AbyssLane.ShouldAdd(true, GameMode.Standard, isClient: false, alreadyHas: true));
    }

    [Fact]
    public void The_lobbys_own_list_is_never_touched()
    {
        var lobby = new List<ModifierModel>();
        var abyss = NewAbyss();
        var handed = AbyssLane.With(lobby, abyss);
        Assert.Empty(lobby);
        Assert.Same(abyss, Assert.Single(handed));
        Assert.True(AbyssLane.Carries(handed));
        Assert.False(AbyssLane.Carries(lobby));
        Assert.False(AbyssLane.Carries(null));
    }

    [Fact]
    public void The_abyss_is_carried_past_the_character_select_into_the_run()
    {
        var abyss = NewAbyss();
        var seen = AbyssLane.Hold(new List<ModifierModel> { abyss });
        Assert.Empty(seen);

        IReadOnlyList<ModifierModel> modifiers = Array.Empty<ModifierModel>();
        var mode = GameMode.Standard;
        AbyssLane.Release(ref modifiers, mode);
        Assert.Same(abyss, Assert.Single(modifiers));
        // The run stays a Standard run: it counts for ascension (2026-10-12).
        Assert.Equal(GameMode.Standard, mode);

        // Spent: the next Standard run is a Standard run.
        IReadOnlyList<ModifierModel> next = Array.Empty<ModifierModel>();
        var nextMode = GameMode.Standard;
        AbyssLane.Release(ref next, nextMode);
        Assert.Empty(next);
        Assert.Equal(GameMode.Standard, nextMode);
    }

    [Fact]
    public void A_run_without_the_abyss_passes_untouched_and_clears_the_hold()
    {
        AbyssLane.Hold(new List<ModifierModel> { NewAbyss() });
        var plain = Array.Empty<ModifierModel>();
        Assert.Same(plain, AbyssLane.Hold(plain));

        IReadOnlyList<ModifierModel> modifiers = Array.Empty<ModifierModel>();
        var mode = GameMode.Standard;
        AbyssLane.Release(ref modifiers, mode);
        Assert.Empty(modifiers);
        Assert.Equal(GameMode.Standard, mode);
    }

    [Fact]
    public void A_held_list_never_lands_on_a_custom_or_daily_run()
    {
        var abyss = NewAbyss();
        AbyssLane.Hold(new List<ModifierModel> { abyss });
        IReadOnlyList<ModifierModel> modifiers = Array.Empty<ModifierModel>();
        var mode = GameMode.Daily;
        AbyssLane.Release(ref modifiers, mode);
        Assert.Empty(modifiers);
        Assert.Equal(GameMode.Daily, mode);
        // Clear the hold for any test after this one.
        AbyssLane.Hold(Array.Empty<ModifierModel>());
    }
}
