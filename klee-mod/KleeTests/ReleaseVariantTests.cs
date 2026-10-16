using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using BaseLib.Patches.Content;
using HarmonyLib;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Modding;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE WORKSHOP RELEASE BUILD (ReleaseVariant.cs, 2026-10-16): telemetry
/// off for players, and a package that can leave a kit out. This test
/// project builds the dev configuration (no WorkshopRelease, no GitsKits),
/// so the release answers are pinned off the PURE rules both builds share,
/// and the dev build's own answers are pinned as they are.
/// </summary>
public class ReleaseVariantTests
{
    private static T Uninit<T>() => (T)RuntimeHelpers.GetUninitializedObject(typeof(T));

    // ------------------------------------------------------- telemetry ---

    [Fact]
    public void Dev_build_is_not_a_release_and_writes_for_a_human()
    {
        Assert.False(WorkshopRelease.IsRelease);
        Assert.True(WorkshopRelease.TelemetryWrites(release: false, declaredFeed: null));
        Assert.True(WorkshopRelease.TelemetryWrites(release: false, declaredFeed: ""));
        Assert.True(WorkshopRelease.TelemetryWrites(release: false, declaredFeed: "bot"));
    }

    [Fact]
    public void Release_build_writes_only_when_a_harness_declared_a_feed()
    {
        Assert.False(WorkshopRelease.TelemetryWrites(release: true, declaredFeed: null));
        Assert.False(WorkshopRelease.TelemetryWrites(release: true, declaredFeed: ""));
        Assert.False(WorkshopRelease.TelemetryWrites(release: true, declaredFeed: "  "));
        Assert.True(WorkshopRelease.TelemetryWrites(release: true, declaredFeed: "bot"));
    }

    private static readonly Type Telemetry = typeof(KleeMod).Assembly
        .GetTypes().First(t => t.Name == "PlayTelemetry");

    [Fact]
    public void Play_telemetry_reads_the_gate_on_open_and_on_write()
    {
        var enabled = Telemetry.GetProperty("Enabled",
            BindingFlags.Static | BindingFlags.NonPublic);
        Assert.NotNull(enabled);
        // The dev build: on whatever the environment says.
        Assert.True((bool)enabled!.GetValue(null)!);
        Assert.Contains("PlayTelemetry.get_Enabled",
            Il.Calls(Il.Method("PlayTelemetry", "OpenFight")));
        Assert.Contains("PlayTelemetry.get_Enabled",
            Il.Calls(Il.Method("PlayTelemetry", "Write")));
    }

    // ------------------------------------------------------------ kits ---

    [Fact]
    public void Dev_build_ships_every_kit()
    {
        Assert.Null(ReleaseKits.Shipped);
        foreach (var kit in ReleaseKits.Known) Assert.True(ReleaseKits.Ships(kit));
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void An_empty_list_ships_everything(string value) =>
        Assert.Null(ReleaseKits.Parse(value));

    [Theory]
    [InlineData("klee+kokomi+furina+varka")]
    [InlineData("klee,kokomi,furina,varka")]
    [InlineData("klee;kokomi;furina;varka")]
    [InlineData(" Klee kokomi  FURINA+varka ")]
    public void The_public_list_leaves_Yae_out(string value)
    {
        var shipped = ReleaseKits.Parse(value);
        Assert.Equal(new[] { "klee", "kokomi", "furina", "varka" }, shipped);
        Assert.False(ReleaseKits.Ships("yae", shipped));
        Assert.True(ReleaseKits.Ships("klee", shipped));
        // Not one of ours (a base character): always ships.
        Assert.True(ReleaseKits.Ships((string)null, shipped));
    }

    [Fact]
    public void Unknown_ids_are_dropped() =>
        Assert.Equal(new[] { "klee" }, ReleaseKits.Parse("klee+nahida"));

    [Fact]
    public void Every_character_maps_to_its_kit()
    {
        Assert.Equal("klee", ReleaseKits.KitOf(Uninit<Klee>()));
        Assert.Equal("kokomi", ReleaseKits.KitOf(Uninit<Kokomi>()));
        Assert.Equal("furina", ReleaseKits.KitOf(Uninit<Furina>()));
        Assert.Equal("varka", ReleaseKits.KitOf(Uninit<Varka>()));
        Assert.Equal("yae", ReleaseKits.KitOf(Uninit<Yae>()));
        // Every CustomCharacterModel in the mod has a kit, so a sixth one
        // cannot slip past the list unnoticed.
        var characters = typeof(KleeMod).Assembly.GetTypes()
            .Where(t => !t.IsAbstract && typeof(CustomCharacterModel).IsAssignableFrom(t));
        foreach (var t in characters)
        {
            var kit = ReleaseKits.KitOf(
                (CustomCharacterModel)RuntimeHelpers.GetUninitializedObject(t));
            Assert.Contains(kit, ReleaseKits.Known);
        }
    }

    [Fact]
    public void A_left_out_kit_is_taken_off_the_registered_list()
    {
        var klee = Uninit<Klee>();
        var yae = Uninit<Yae>();
        var shipped = ReleaseKits.Parse("klee+kokomi+furina+varka");

        var registered = new List<CustomCharacterModel> { klee, yae };
        Assert.True(ReleaseKits.Unregister(registered, yae, shipped));
        Assert.False(ReleaseKits.Unregister(registered, klee, shipped));
        Assert.Equal(new CustomCharacterModel[] { klee }, registered);

        // Every kit shipping (the dev build): the list is not touched.
        var all = new List<CustomCharacterModel> { klee, yae };
        Assert.False(ReleaseKits.Unregister(all, yae, null));
        Assert.Equal(2, all.Count);
    }

    [Fact]
    public void The_registration_patch_targets_BaseLibs_AddCharacter()
    {
        var patch = typeof(KleeMod).Assembly.GetTypes()
            .Single(t => t.Name == "CustomContentDictionary_AddCharacter_ReleaseKits_Patch");
        var info = patch.GetCustomAttribute<HarmonyPatch>()!.info;
        Assert.Equal(typeof(CustomContentDictionary), info.declaringType);
        Assert.Equal(nameof(CustomContentDictionary.AddCharacter), info.methodName);
        Assert.NotNull(AccessTools.Method(info.declaringType, info.methodName));
        // The list it edits is the one BaseLib's AllCharacters postfix reads.
        Assert.NotNull(typeof(CustomContentDictionary).GetField(
            nameof(CustomContentDictionary.CustomCharacters)));
    }

    [Fact]
    public void The_own_loc_table_patch_targets_the_games_lookup()
    {
        var patch = typeof(KleeMod).Assembly.GetTypes()
            .Single(t => t.Name == "ModManager_GetModdedLocTables_OwnTable_Patch");
        var info = patch.GetCustomAttribute<HarmonyPatch>()!.info;
        Assert.Equal(typeof(ModManager), info.declaringType);
        Assert.NotNull(AccessTools.Method(info.declaringType, info.methodName));
        var own = (string)patch.GetMethod("OwnTable",
                BindingFlags.Static | BindingFlags.NonPublic)!
            .Invoke(null, new object[] { "eng", "card_keywords.json" })!;
        // The pck's path (tools/build_pck.ps1), whatever the manifest id is.
        Assert.Equal("res://klee/localization/eng/card_keywords.json", own);
    }
}
