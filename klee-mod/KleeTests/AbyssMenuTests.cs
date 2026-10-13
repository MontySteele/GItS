using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using KleeMod.Abyss;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE ABYSS MENU BUTTON (<see cref="AbyssMenu"/>): it opens the ordinary
/// character select armed, the armed flag puts the Spiral Abyss into that one
/// lobby's own list, and the run is carried through <see cref="AbyssLane"/>'s
/// hold and release as a Standard run. Pinned headlessly: one press arms one
/// lobby, who gets armed, the list is armed once, the main menu disarms, and
/// the button's run reaches the run's creation while the next plain run does
/// not. The screen itself (the banner, the co-op client) is the PR's live
/// check.
/// </summary>
public class AbyssMenuTests
{
    private static SpiralAbyss NewAbyss() =>
        (SpiralAbyss)RuntimeHelpers.GetUninitializedObject(typeof(SpiralAbyss));

    [Fact]
    public void One_press_arms_one_lobby()
    {
        AbyssMenu.Disarm();
        Assert.False(AbyssMenu.Armed);
        AbyssMenu.Arm();
        Assert.True(AbyssMenu.Armed);
        Assert.True(AbyssMenu.TakeArmed());
        Assert.False(AbyssMenu.Armed);
        Assert.False(AbyssMenu.TakeArmed());
    }

    [Fact]
    public void Only_an_armed_standard_host_without_the_abyss_is_armed()
    {
        Assert.True(AbyssMenu.ShouldArmLobby(true, GameMode.Standard, isClient: false, alreadyHas: false));
        Assert.False(AbyssMenu.ShouldArmLobby(false, GameMode.Standard, false, false));
        Assert.False(AbyssMenu.ShouldArmLobby(true, GameMode.Custom, false, false));
        Assert.False(AbyssMenu.ShouldArmLobby(true, GameMode.Daily, false, false));
        Assert.False(AbyssMenu.ShouldArmLobby(true, GameMode.Standard, isClient: true, alreadyHas: false));
        Assert.False(AbyssMenu.ShouldArmLobby(true, GameMode.Standard, isClient: false, alreadyHas: true));
    }

    [Fact]
    public void The_lobbys_list_takes_the_abyss_once()
    {
        var lobby = new List<ModifierModel>();
        var abyss = NewAbyss();
        Assert.True(AbyssMenu.ArmList(lobby, abyss));
        Assert.Same(abyss, Assert.Single(lobby));
        Assert.False(AbyssMenu.ArmList(lobby, NewAbyss()));
        Assert.Single(lobby);
    }

    [Fact]
    public void The_main_menu_disarms_the_flag_and_drops_a_held_list()
    {
        AbyssMenu.Arm();
        AbyssLane.Hold(new List<ModifierModel> { NewAbyss() });
        Assert.True(AbyssLane.Holding);

        AbyssMenu.Disarm();
        Assert.False(AbyssMenu.Armed);
        Assert.False(AbyssLane.Holding);

        IReadOnlyList<ModifierModel> modifiers = Array.Empty<ModifierModel>();
        AbyssLane.Release(ref modifiers, GameMode.Standard);
        Assert.Empty(modifiers);
    }

    [Fact]
    public void The_buttons_run_is_a_standard_abyss_run_and_the_next_run_is_plain()
    {
        AbyssMenu.Disarm();

        // The press, then the character select's initialiser.
        AbyssMenu.Arm();
        var lobby = new List<ModifierModel>();
        if (AbyssMenu.ShouldArmLobby(AbyssMenu.TakeArmed(), GameMode.Standard, false, AbyssLane.Carries(lobby)))
            AbyssMenu.ArmList(lobby, NewAbyss());
        Assert.True(AbyssLane.Carries(lobby));

        // The Standard screen's BeginRun sees an empty list; the run gets the Abyss.
        Assert.Empty(AbyssLane.Hold(lobby));
        IReadOnlyList<ModifierModel> modifiers = Array.Empty<ModifierModel>();
        AbyssLane.Release(ref modifiers, GameMode.Standard);
        Assert.True(AbyssLane.Carries(modifiers));
        Assert.False(AbyssLane.Holding);

        // Back out, press Standard: a new lobby, nothing armed, a plain run.
        var plainLobby = new List<ModifierModel>();
        if (AbyssMenu.ShouldArmLobby(AbyssMenu.TakeArmed(), GameMode.Standard, false, AbyssLane.Carries(plainLobby)))
            AbyssMenu.ArmList(plainLobby, NewAbyss());
        Assert.Empty(plainLobby);
        Assert.Empty(AbyssLane.Hold(plainLobby));
        IReadOnlyList<ModifierModel> next = Array.Empty<ModifierModel>();
        AbyssLane.Release(ref next, GameMode.Standard);
        Assert.Empty(next);
    }
}
