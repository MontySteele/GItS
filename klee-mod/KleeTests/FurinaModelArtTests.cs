using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// FURINA'S MODEL ART, PHASE B (2026-10-13): her frame-sheet scene, the
/// Rejoice clip for Let the People Rejoice, the rapier's Hydro trail, the
/// guests' rendered stills and the Spend, Drain and Repay effects. [USER]:
/// "Furina looks good!"
///
/// WHAT IS REAL HERE. State selection, the absorb rule, the card selection,
/// the element-to-colour table with her Hydro rest, the hit timing and the
/// stage effects' names and stretch are pure functions read off the real
/// assembly. Placing a node needs a live scene tree, which is process death
/// in this host (README, the headless boundary), so the scene side is a
/// structural pin on the generated .tscn and the committed manifest
/// (tier0/tests/test_furina_rig.py holds the rest).
/// </summary>
public class FurinaModelArtTests
{
    private const BindingFlags All = HeadlessGame.All;

    private static Type Router() =>
        Il.Method("CreatureAnimationRouter", "Route").DeclaringType!;

    private static Type Motion() =>
        Il.Method("CardPlayMotion", "TriggerFor").DeclaringType!;

    private static Type Trail() =>
        Il.Method("ElementTrail", "OnTravel").DeclaringType!;

    private static Type StageFx() =>
        Router().Assembly.GetTypes().Single(t => t.FullName == "KleeMod.Vfx.FurinaStageFx");

    private static string? Select(string trigger, params string[] has)
        => (string?)Router().GetMethod("SelectState", All)!
            .Invoke(null, new object[]
            {
                trigger, (Func<string, bool>)(s => has.Contains(s)), false,
            });

    private static readonly string[] Contract = { "idle", "attack", "hurt", "death" };

    private static readonly string[] Furina =
        { "idle", "attack", "hurt", "death", "cast", "power", "idle_low", "rejoice" };

    [Fact]
    public void Rejoice_takes_its_own_state_and_falls_back_to_the_attack()
    {
        Assert.Equal("rejoice", Select("Rejoice", Furina));
        Assert.Equal("attack", Select("Rejoice", Contract));
        Assert.Equal("Rejoice", (string)Motion().GetField("RejoiceTrigger", All)!.GetValue(null)!);
    }

    [Fact]
    public void The_rejoice_clip_absorbs_the_cards_own_lunge_but_not_a_hit()
    {
        bool Absorbed(string? current, string trigger) => (bool)Router()
            .GetMethod("AbsorbedBy", All)!.Invoke(null, new object?[] { current, trigger })!;

        Assert.True(Absorbed("rejoice", "Attack"));
        Assert.True(Absorbed("rejoice", "Cast"));
        Assert.True(Absorbed("rejoice", "PowerUp"));
        Assert.False(Absorbed("rejoice", "Hit"));
        Assert.False(Absorbed("rejoice", "Dead"));
    }

    [Fact]
    public void Only_let_the_people_rejoice_plays_the_rejoice_clip()
    {
        bool IsRejoice(string typeName)
        {
            var type = Motion().Assembly.GetTypes().Single(t => t.FullName == typeName);
            var card = System.Runtime.CompilerServices.RuntimeHelpers.GetUninitializedObject(type);
            return (bool)Motion().GetMethod("IsRejoicePlay", All)!.Invoke(null, new[] { card })!;
        }

        Assert.True(IsRejoice("KleeMod.Cards.Prototype.Generated.ProtoFsLetThePeopleRejoice"));
        Assert.False(IsRejoice("KleeMod.Cards.Prototype.Generated.ProtoVkFourWindsAscension"));
        Assert.False(IsRejoice("KleeMod.Cards.Prototype.Generated.ProtoKoJumpyDumpty"));
    }

    [Fact]
    public void Her_hits_land_on_the_thrust_and_on_the_flourish()
    {
        using var manifest = JsonDocument.Parse(RepoFile("tools/char_render/furina_frames.json"));
        var sheets = manifest.RootElement.GetProperty("sheets");
        var thrust = sheets.GetProperty("attack").GetProperty("events").GetProperty("main").GetDouble();
        var flourish = sheets.GetProperty("rejoice").GetProperty("events").GetProperty("main").GetDouble();
        var furina = Router().Assembly.GetTypes().Single(t => t.FullName == "KleeMod.Furina");
        var model = System.Runtime.CompilerServices.RuntimeHelpers.GetUninitializedObject(furina);
        var delay = (float)furina.GetProperty("AttackAnimDelay")!.GetValue(model)!;
        var rejoice = (float)Motion().GetField("RejoiceDelay", All)!.GetValue(null)!;
        Assert.Equal(thrust, delay, 3);
        Assert.Equal(flourish, rejoice + delay, 3);
    }

    [Theory]
    [InlineData(Element.None, "hydro", "#5cb8ff")]
    [InlineData(Element.Pyro, "hydro", "#ff9a5c")]
    [InlineData(Element.Cryo, "hydro", "#a8f0ff")]
    [InlineData(Element.None, null, "#8fffd6")]
    [InlineData(Element.None, "nonsense", "#8fffd6")]
    public void Her_rapier_trail_rests_at_hydro_and_takes_a_played_element(
        Element element, string? meta, string hex)
    {
        var rest = (Element)Trail().GetMethod("RestElementOf", All)!.Invoke(null, new object?[] { meta })!;
        var tint = (string)Trail().GetMethod("TintHexResting", All)!
            .Invoke(null, new object[] { element, rest })!;
        Assert.Equal(hex, tint);
    }

    [Fact]
    public void Her_scene_names_the_rest_element_and_the_stage_effect_nodes()
    {
        var scene = RepoFile("klee-mod/pck-src/furina/model/combat.tscn");
        Assert.Contains("metadata/rest_element = \"hydro\"", scene);
        Assert.Equal("rest_element", (string)Trail().GetField("RestElementMeta", All)!.GetValue(null)!);
        foreach (var effect in new[] { StageEffect.Spend, StageEffect.Drain, StageEffect.Repay })
        {
            string Name(string method) =>
                (string)StageFx().GetMethod(method, All)!.Invoke(null, new object[] { effect })!;
            Assert.Contains($"[node name=\"{Name("SpriteFor")}\" type=\"Sprite2D\" parent=\"Visuals/Facing/StageFx\"]", scene);
            Assert.Contains($"[node name=\"{Name("PlayerFor")}\" type=\"AnimationPlayer\" parent=\".\"]", scene);
            Assert.Contains($"resource_name = \"{Name("AnimationFor")}\"", scene);
        }
        Assert.Contains("[node name=\"AttackFx\" type=\"Sprite2D\" parent=\"Visuals/Facing/Model\"]", scene);
        Assert.Contains("states/rejoice/node = SubResource(", scene);
    }

    [Theory]
    [InlineData(192f, 192f, 1f)]
    [InlineData(288f, 192f, 1.5f)]
    [InlineData(40f, 192f, 0.6f)]
    [InlineData(2000f, 192f, 2.5f)]
    [InlineData(0f, 192f, 1f)]
    [InlineData(-50f, 192f, 1f)]
    [InlineData(150f, 0f, 1f)]
    public void Drain_and_repay_stretch_to_the_nearest_guest_within_bounds(float run, float reach, float want)
    {
        var got = (float)StageFx().GetMethod("StretchFor", All)!.Invoke(null, new object[] { run, reach })!;
        Assert.Equal(want, got, 3);
        bool Reaches(StageEffect e) => (bool)StageFx().GetMethod("Reaches", All)!.Invoke(null, new object[] { e })!;
        Assert.True(Reaches(StageEffect.Drain));
        Assert.True(Reaches(StageEffect.Repay));
        Assert.False(Reaches(StageEffect.Spend));
    }

    [Fact]
    public void Freminet_stands_in_his_own_scene_not_the_osty_rig()
    {
        var pets = Router().Assembly.GetTypes().Single(t => t.FullName == "KleeMod.Powers.StagePerformerMonster");
        var path = pets.GetMethod("ModVisualsPathFor", All)!;
        // headless the pack is absent, so the funnel answers null for every
        // guest alike; the literal is what the scene registration reads
        var source = RepoFile("klee-mod/KleeCode/Powers/Prototype/FurinaStagePets.cs");
        Assert.Contains("StagePerformer.Freminet => KleePck.Path(\"furina/model/guest_freminet.tscn\"),", source);
        foreach (var who in Enum.GetValues<StagePerformer>())
        {
            Assert.Matches($"StagePerformer\\.{who} => KleePck\\.Path\\(\"furina/model/guest_{who.ToString().ToLowerInvariant()}\\.tscn\"\\)", source);
        }
        Assert.NotNull(path);
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
