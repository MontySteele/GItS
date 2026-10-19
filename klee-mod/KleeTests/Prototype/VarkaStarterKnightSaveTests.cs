#nullable enable

using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text.Json;
using BaseLib.Utils;
using KleeMod.Elements;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Saves.Runs;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// BOREAS'S FANG'S SAVED STARTER ELEMENT SURVIVES A SAVE AND A LOAD
/// (<c>Relics/VarkaStarterKnight.cs</c>, a BaseLib <c>SavedSpireField</c>).
///
/// The real path, end to end, minus the Harmony attachment: BaseLib's own
/// <c>SavedSpireFieldPatch</c> postfixes on <c>SavedProperties.FromInternal</c>
/// (the save) and <c>SavedProperties.FillInternal</c> (the load) are invoked
/// as they are on a save, and the properties in between go through the run
/// save's own JSON options (<c>JsonSerializationUtility.Options</c>), not a
/// hand-built copy. The headless harness does not run BaseLib's PatchAll, so
/// the postfix bodies are called by reflection rather than through the
/// patched methods.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaStarterKnightSaveTests
{
    private const BindingFlags Static =
        BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.Public;

    public VarkaStarterKnightSaveTests()
    {
        HeadlessGame.Arm();
    }

    private static MethodInfo Postfix(string name) =>
        typeof(SavedSpireField<,>).Assembly
            .GetType("BaseLib.Patches.Utils.SavedSpireFieldPatch", throwOnError: true)!
            .GetMethod(name, Static)!;

    private static BoreasFang NewFang() =>
        (BoreasFang)RuntimeHelpers.GetUninitializedObject(typeof(BoreasFang));

    [Theory]
    [InlineData(Element.Pyro)]
    [InlineData(Element.Hydro)]
    [InlineData(Element.Cryo)]
    [InlineData(Element.Electro)]
    public void The_fangs_starter_element_survives_a_save_and_a_load(Element rolled)
    {
        var fang = NewFang();
        VarkaStarterKnight.Record(fang, rolled);

        // The save: BaseLib's postfix on SavedProperties.FromInternal, handed
        // a null result as for a model with no [SavedProperty] of its own.
        var args = new object?[] { null, fang };
        Postfix("PostfixFromInternal").Invoke(null, args);
        var saved = Assert.IsType<SavedProperties>(args[0]);

        var json = JsonSerializer.Serialize(saved, JsonSerializationUtility.Options);
        Assert.Contains("BoreasFang_KleeMod_VarkaStarterKnightElement", json);
        var loaded = JsonSerializer.Deserialize<SavedProperties>(
            json, JsonSerializationUtility.Options);
        Assert.NotNull(loaded);

        // The load: a fresh Fang reads None until its properties are filled.
        var reloaded = NewFang();
        Assert.Equal(Element.None, VarkaStarterKnight.Of(reloaded));
        Postfix("PostfixFillInternal").Invoke(null, new object?[] { loaded, reloaded });
        Assert.Equal(rolled, VarkaStarterKnight.Of(reloaded));
    }

    [Fact]
    public void The_field_rides_the_base_games_saved_properties_not_a_custom_save()
    {
        // An int on a relic is a type the base SavedProperties carries, so
        // BaseLib injects the name into the base cache instead of registering
        // an extended save (SavedSpireFieldPatch.AddFieldsSorted).
        var field = typeof(VarkaStarterKnight)
            .GetField("Saved", Static)!.GetValue(null)!;
        Assert.True((bool)field.GetType().GetProperty("IsBasegameSupported")!
            .GetValue(field)!);
        Assert.Equal("BoreasFang_KleeMod_VarkaStarterKnightElement",
            (string)field.GetType().GetProperty("Name")!.GetValue(field)!);
    }

    [Fact]
    public void A_save_from_before_the_field_loads_as_none()
    {
        // A run begun before the record existed: no property, so the Fang
        // reads None and Knight's Commission falls back to the deck.
        var reloaded = NewFang();
        Postfix("PostfixFillInternal").Invoke(
            null, new object?[] { new SavedProperties(), reloaded });
        Assert.Equal(Element.None, VarkaStarterKnight.Of(reloaded));
    }
}
