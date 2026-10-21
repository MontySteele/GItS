using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using System.Text.RegularExpressions;
using KleeMod.Elements;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// VARKA'S MODEL ART, PHASE B (2026-10-13): his frame-sheet scene, the
/// Ascension clip for Four Winds' Ascension, and the element layer coloured by
/// the played card's element. [USER]: "Ok, the Varka one looks good! I think
/// doing more requires I see it in-game; let's ship it! (a)"
///
/// WHAT IS REAL HERE. State selection, the absorb rule, the card selection,
/// the travel rules and the element-to-colour table are pure functions read
/// off the real assembly. Placing a node needs a live scene tree, which is
/// process death in this host (README, the headless boundary), so the scene
/// side is a structural pin on the generated .tscn and the committed manifest.
/// </summary>
public class VarkaModelArtTests
{
    private const BindingFlags All = HeadlessGame.All;

    private static Type Router() =>
        Il.Method("CreatureAnimationRouter", "Route").DeclaringType!;

    private static Type Motion() =>
        Il.Method("CardPlayMotion", "TriggerFor").DeclaringType!;

    private static Type Trail() =>
        Il.Method("ElementTrail", "OnTravel").DeclaringType!;

    private static string? Select(string trigger, params string[] has)
        => (string?)Router().GetMethod("SelectState", All)!
            .Invoke(null, new object[]
            {
                trigger, (Func<string, bool>)(s => has.Contains(s)), false,
            });

    private static readonly string[] Contract = { "idle", "attack", "hurt", "death" };

    private static readonly string[] Varka =
        { "idle", "attack", "hurt", "death", "cast", "power", "idle_low", "ascension" };

    [Fact]
    public void Ascension_takes_its_own_state_and_falls_back_to_the_attack()
    {
        Assert.Equal("ascension", Select("Ascension", Varka));
        Assert.Equal("attack", Select("Ascension", Contract));
        Assert.Equal("Ascension", (string)Motion().GetField("AscensionTrigger", All)!.GetValue(null)!);
    }

    [Fact]
    public void The_ascension_clip_absorbs_the_cards_own_lunge_but_not_a_hit()
    {
        bool Absorbed(string? current, string trigger) => (bool)Router()
            .GetMethod("AbsorbedBy", All)!.Invoke(null, new object?[] { current, trigger })!;

        Assert.True(Absorbed("ascension", "Attack"));
        Assert.True(Absorbed("ascension", "Cast"));
        Assert.True(Absorbed("ascension", "PowerUp"));
        Assert.False(Absorbed("ascension", "Hit"));
        Assert.False(Absorbed("ascension", "Dead"));
        Assert.False(Absorbed("attack", "Attack"));
    }

    [Fact]
    public void Only_the_two_ascensions_play_the_ascension_clip()
    {
        object Card(string typeName)
        {
            var type = Motion().Assembly.GetTypes().Single(t => t.FullName == typeName);
            return System.Runtime.CompilerServices.RuntimeHelpers.GetUninitializedObject(type);
        }
        bool IsAscension(string typeName)
            => (bool)Motion().GetMethod("IsAscensionPlay", All)!.Invoke(null, new[] { Card(typeName) })!;
        bool IsCarryOut(string typeName)
            => (bool)Motion().GetMethod("IsAscensionCarryOut", All)!.Invoke(null, new[] { Card(typeName) })!;

        Assert.True(IsAscension("KleeMod.Cards.Prototype.Generated.ProtoVkFourWindsAscension"));
        // Kokomi's signature clip (art polish, 2026-10-21)
        Assert.True(IsAscension("KleeMod.Cards.Prototype.Generated.ProtoKkNereidsAscension"));
        Assert.False(IsAscension("KleeMod.Cards.Prototype.Generated.ProtoVkTempestOfTheFourWinds"));
        Assert.False(IsAscension("KleeMod.Cards.Prototype.Generated.ProtoKoJumpyDumpty"));
        Assert.False(IsAscension("KleeMod.Cards.Prototype.Generated.ProtoKkKuragesOath"));
        // ... and Kurage's Oath plays it when carried out as a Plan, nothing else
        Assert.True(IsCarryOut("KleeMod.Cards.Prototype.Generated.ProtoKkKuragesOath"));
        Assert.False(IsCarryOut("KleeMod.Cards.Prototype.Generated.ProtoKkNereidsAscension"));
    }

    [Theory]
    [InlineData(Element.Anemo, "#8fffd6")]
    [InlineData(Element.Pyro, "#ff9a5c")]
    [InlineData(Element.Hydro, "#5cb8ff")]
    [InlineData(Element.Electro, "#c08cff")]
    [InlineData(Element.Cryo, "#a8f0ff")]
    [InlineData(Element.None, "#8fffd6")]
    public void The_layer_takes_the_played_elements_colour_and_anemo_by_default(Element element, string hex)
    {
        var tint = (string)Trail().GetMethod("TintHex", All)!.Invoke(null, new object[] { element })!;
        Assert.Equal(hex, tint);
    }

    /// <summary>In-game check 2026-10-16: Tidal Bulwark (Hydro) and Razor:
    /// Awakening (Electro) print no element, so the trail drew Anemo teal.
    /// The trail reads the element the play makes current, then a
    /// companion's own.</summary>
    [Theory]
    [InlineData("ProtoVkTidalBulwark", Element.None, Element.Hydro)]
    [InlineData("ProtoVkRazorClawAndThunder", Element.None, Element.Electro)]
    [InlineData("ProtoVkKindledEdge", Element.None, Element.Pyro)]
    [InlineData("ProtoVkTidalBulwark", Element.Cryo, Element.Cryo)]
    [InlineData("ProtoVkKnightlyStrike", Element.Anemo, Element.Anemo)]
    public void The_trail_shows_the_element_a_switch_or_companion_card_makes_current(
        string card, Element hit, Element expected)
    {
        var type = Trail().Assembly.GetTypes()
            .Single(t => t.FullName == "KleeMod.Cards.Prototype.Generated." + card);
        var model = System.Runtime.CompilerServices.RuntimeHelpers.GetUninitializedObject(type);
        var got = (Element)Trail().GetMethod("TrailElementOf", All)!
            .Invoke(null, new object?[] { hit, model })!;
        Assert.Equal(expected, got);
    }

    [Theory]
    [InlineData("Varka")]
    [InlineData("Furina")]
    [InlineData("Kokomi")]
    public void His_card_trail_is_not_the_ironclads_orange(string character)
    {
        var src = RepoFile($"klee-mod/KleeCode/{character}.cs");
        Assert.Contains("\"res://scenes/vfx/card_trail_defect.tscn\"", src);
    }

    [Fact]
    public void A_fresh_entry_into_a_strike_colours_it_and_only_the_ascension_places_the_target_burst()
    {
        bool Tints(string? from, string to) => (bool)Trail()
            .GetMethod("Tints", All)!.Invoke(null, new object?[] { from, to })!;
        bool Places(string? from, string to) => (bool)Trail()
            .GetMethod("PlacesTargetBurst", All)!.Invoke(null, new object?[] { from, to })!;
        string[] Nodes(string state) => (string[])Trail()
            .GetMethod("NodesFor", All)!.Invoke(null, new object[] { state })!;

        Assert.True(Tints("idle", "attack"));
        Assert.True(Tints("idle_low", "ascension"));
        Assert.False(Tints("attack", "attack"));
        Assert.False(Tints("idle", "cast"));
        Assert.True(Places("idle", "ascension"));
        Assert.False(Places("ascension", "ascension"));
        Assert.False(Places("idle", "attack"));
        Assert.Equal(new[] { "AttackFx" }, Nodes("attack"));
        Assert.Equal(new[] { "AscensionFx", "GroundBurst", "TargetBurst" }, Nodes("ascension"));
        Assert.Empty(Nodes("hurt"));
    }

    [Fact]
    public void His_scene_carries_the_layer_nodes_on_one_element_material()
    {
        var scene = RepoFile("klee-mod/pck-src/varka/model/combat.tscn");
        foreach (var node in new[] { "AttackFx", "AscensionFx" })
        {
            var body = NodeBody(scene, node, "Visuals/Facing/Model");
            Assert.Contains("unique_name_in_owner = true", body);
            Assert.Contains("material = SubResource(\"ShaderMaterial_element\")", body);
        }
        var blade = NodeBody(scene, "GroundBurst", "Visuals/Facing");
        var target = NodeBody(scene, "TargetBurst", "Visuals/Facing");
        foreach (var body in new[] { blade, target })
        {
            Assert.Contains("unique_name_in_owner = true", body);
            Assert.Contains("material = SubResource(\"ShaderMaterial_element\")", body);
        }
        // the mirrored copy is a negative x scale, so it turns about the ground point
        Assert.Contains("scale = Vector2(0.5, 0.5)", blade);
        Assert.Contains("scale = Vector2(-0.5, 0.5)", target);
        Assert.Contains("resource_local_to_scene = true", scene);
        Assert.Contains("shader_parameter/element = Color(0.5608, 1, 0.8392, 1)", scene);
        Assert.Contains("[node name=\"AnimationTree\" type=\"AnimationTree\" parent=\".\"]", scene);
        Assert.Contains("states/ascension/node = SubResource(", scene);
    }

    [Fact]
    public void Both_bursts_start_on_the_ascensions_impact_frame_and_the_blade_copy_sits_at_the_point()
    {
        using var manifest = JsonDocument.Parse(RepoFile("tools/char_render/varka_frames.json"));
        var root = manifest.RootElement;
        var use = root.GetProperty("effects").GetProperty("ground_burst").GetProperty("uses")[0];
        var start = use.GetProperty("start_frame").GetInt32();
        var t0 = root.GetProperty("sheets").GetProperty("ascension").GetProperty("times")[start].GetDouble();
        var scale = root.GetProperty("combat_scale").GetDouble();
        var tip = use.GetProperty("places").EnumerateArray()
            .Single(p => p.GetProperty("at").GetString() == "blade_tip").GetProperty("offset_px");

        var scene = RepoFile("klee-mod/pck-src/varka/model/combat.tscn");
        foreach (var node in new[] { "GroundBurst", "TargetBurst" })
        {
            var body = NodeBody(scene, node, "Visuals/Facing");
            var meta = double.Parse(Regex.Match(body, "metadata/start = ([0-9.]+)").Groups[1].Value,
                CultureInfo.InvariantCulture);
            Assert.Equal(t0, meta, 3);
        }
        var pos = Regex.Match(NodeBody(scene, "GroundBurst", "Visuals/Facing"),
            "position = Vector2\\(([-0-9.]+), ([-0-9.]+)\\)");
        Assert.Equal(tip[0].GetDouble() * scale, double.Parse(pos.Groups[1].Value, CultureInfo.InvariantCulture), 3);
        Assert.Equal(tip[1].GetDouble() * scale, double.Parse(pos.Groups[2].Value, CultureInfo.InvariantCulture), 3);
    }

    [Fact]
    public void His_hit_lands_on_the_attacks_main_impact()
    {
        using var manifest = JsonDocument.Parse(RepoFile("tools/char_render/varka_frames.json"));
        var main = manifest.RootElement.GetProperty("sheets").GetProperty("attack")
            .GetProperty("events").GetProperty("main").GetDouble();
        var varka = Router().Assembly.GetTypes().Single(t => t.FullName == "KleeMod.Varka");
        var model = System.Runtime.CompilerServices.RuntimeHelpers.GetUninitializedObject(varka);
        var delay = (float)varka.GetProperty("AttackAnimDelay")!.GetValue(model)!;
        Assert.Equal(main, delay, 3);
    }

    private static string NodeBody(string scene, string name, string parent)
    {
        var block = Regex.Match(scene,
            $"\\[node name=\"{name}\" type=\"Sprite2D\" parent=\"{Regex.Escape(parent)}\"\\]\\n((?:.+\\n)+)");
        Assert.True(block.Success, $"no {name} under {parent}");
        return block.Groups[1].Value;
    }

    private static string RepoFile(string relativePath)
    {
        var relative = relativePath.Replace('/', Path.DirectorySeparatorChar);
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = Path.Combine(dir.FullName, relative);
            if (File.Exists(candidate)) return File.ReadAllText(candidate);
            dir = dir.Parent;
        }

        throw new FileNotFoundException(relative);
    }
}
