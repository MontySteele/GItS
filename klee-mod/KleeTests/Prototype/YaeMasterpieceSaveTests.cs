using System;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Multiplayer.Serialization;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Saves.Runs;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// PAUSE AND RESUME ON THE SAME BUILD. A deck card's Masterpiece rides the
/// run save as a <c>SerializableEnchantment</c> whose <c>props</c> are the
/// game's own <c>SavedProperties</c>: <c>EnchantmentModel.ToSerializable</c>
/// calls <c>SavedProperties.From</c>, the run save writes it through
/// <c>JsonSerializationUtility.Options</c>, and
/// <c>EnchantmentModel.FromSerializable</c> builds a fresh model and calls
/// <c>SavedProperties.Fill</c>. This test runs that path with the real types:
/// <c>FromInternal</c> (what <c>From</c> calls), a JSON write and read
/// through the game's own options, then <c>FillInternal</c> (what
/// <c>Fill</c> calls) into a fresh Masterpiece.
///
/// SAVED: <see cref="YaeMasterpiece.Published"/> only (the permanent stack).
/// NOT SAVED: <see cref="YaeMasterpiece.Temporary"/>,
/// <see cref="YaeMasterpiece.PlayedOnce"/>, <see cref="YaeMasterpiece.Armed"/>
/// -- combat state, which a deck card never carries.
///
/// THE GAP. The headless host has no <c>ModelDb</c>, so the two ends that
/// look the model up by id (<c>SaveUtil.EnchantmentOrDeprecated</c> in
/// <c>FromSerializable</c>, and <c>ModelIdSerializationCache.Init</c>
/// walking <c>ModelDb.All</c>) are not run. The cache is primed for this
/// one type with the game's own debug hook, as the Confinement and Abyss
/// save tests do; in the game the type is cached because BaseLib registers
/// every <c>CustomEnchantmentModel</c> into <c>ModelDb</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeMasterpieceSaveTests
{
    public YaeMasterpieceSaveTests()
    {
        HeadlessGame.Arm();
    }

    private static YaeMasterpiece Fresh()
    {
        var m = new YaeMasterpiece();
        Seat.Set(m, "IsMutable", true);
        return m;
    }

    private static void SetField(YaeMasterpiece m, string field, object value) =>
        typeof(YaeMasterpiece).GetField(field, BindingFlags.Instance | BindingFlags.NonPublic)!
            .SetValue(m, value);

    private static T WithCache<T>(Func<T> body)
    {
        var initialized = typeof(ModelIdSerializationCache)
            .GetField("_initialized", BindingFlags.Static | BindingFlags.NonPublic);
        Assert.NotNull(initialized);
        var was = (bool)initialized!.GetValue(null)!;
        try
        {
            ModelIdSerializationCache.CacheSavedPropertiesForTypeDebug(typeof(YaeMasterpiece));
            initialized.SetValue(null, true);
            return body();
        }
        finally
        {
            initialized.SetValue(null, was);
        }
    }

    /// <summary>Save one Masterpiece and load it into a fresh one, through
    /// the game's JSON options.</summary>
    private static (YaeMasterpiece loaded, string json) RoundTrip(YaeMasterpiece saved) =>
        WithCache(() =>
        {
            var props = SavedProperties.FromInternal(saved, null);
            Assert.NotNull(props);
            var json = JsonSerializer.Serialize(props!, JsonSerializationUtility.Options);
            var read = JsonSerializer.Deserialize<SavedProperties>(json, JsonSerializationUtility.Options);
            Assert.NotNull(read);
            var loaded = Fresh();
            read!.FillInternal(loaded);
            return (loaded, json);
        });

    [Fact]
    public void Only_the_published_stack_is_a_saved_property()
    {
        var saved = typeof(YaeMasterpiece)
            .GetProperties(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
            .Where(p => p.GetCustomAttribute<SavedPropertyAttribute>() != null)
            .Select(p => p.Name).ToArray();
        Assert.Equal(new[] { nameof(YaeMasterpiece.Published) }, saved);
    }

    [Fact]
    public void Every_published_layer_survives_a_save_and_load_in_order()
    {
        var stack = new[]
        {
            YaeAnnotation.RedInk, YaeAnnotation.Reprint, YaeAnnotation.Footnote,
            YaeAnnotation.RedInk, YaeAnnotation.DeadlineExtension, YaeAnnotation.FoxFire,
            YaeAnnotation.SakuraSeal, YaeAnnotation.Royalties, YaeAnnotation.Reprint,
        };
        var card = Fresh();
        card.Published = stack.Select(a => (int)a).ToArray();

        var (loaded, json) = RoundTrip(card);

        Assert.Contains("int_arrays", json);
        Assert.Contains(nameof(YaeMasterpiece.Published), json);
        Assert.Equal(card.Published, loaded.Published);
        Assert.Equal(stack, loaded.Stack);
        Assert.Equal(2, loaded.Count(YaeAnnotation.RedInk));
        Assert.Equal(2, loaded.Count(YaeAnnotation.Reprint));
        Assert.Equal(card.SummaryText, loaded.SummaryText);
    }

    [Fact]
    public void The_temporary_slot_and_reprint_state_are_not_saved()
    {
        var card = Fresh();
        card.Published = new[] { (int)YaeAnnotation.Reprint };
        SetField(card, "_temporary", YaeAnnotation.Footnote);
        SetField(card, "_playedOnce", true);
        SetField(card, "_armed", 1);
        Assert.Equal(YaeAnnotation.Footnote, card.Temporary);

        var (loaded, _) = RoundTrip(card);

        Assert.Equal(new[] { YaeAnnotation.Reprint }, loaded.Stack);
        Assert.Equal(YaeAnnotation.None, loaded.Temporary);
        Assert.False(loaded.PlayedOnce);
        Assert.Equal(0, loaded.Armed);
    }

    [Fact]
    public void An_empty_stack_loads_as_an_empty_stack()
    {
        var (loaded, _) = RoundTrip(Fresh());
        Assert.Empty(loaded.Published);
        Assert.Empty(loaded.Stack);
    }
}
