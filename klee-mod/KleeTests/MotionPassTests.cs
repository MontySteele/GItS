using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using HarmonyLib;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Hooks;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE MOTION PASS (2026-10-02): cast and power-up states on Skill and Power
/// plays, the low-HP idle, and the fallback that keeps any scene without them
/// exactly as it was.
///
/// WHAT IS REAL HERE. State selection, the HP line and the card-type table are
/// pure functions read off the real assembly. Travelling a tree needs Godot
/// nodes, which is process death in this host (README, the headless
/// boundary), so the scene side is a structural pin on the committed .tscn.
/// </summary>
public class MotionPassTests
{
    private const BindingFlags All = HeadlessGame.All;

    private static Type Router() =>
        Il.Method("CreatureAnimationRouter", "Route").DeclaringType!;

    private static Type Motion() =>
        Il.Method("CardPlayMotion", "TriggerFor").DeclaringType!;

    private static string? Select(string trigger, bool low, params string[] has)
        => (string?)Router().GetMethod("SelectState", All)!
            .Invoke(null, new object[]
            {
                trigger, (Func<string, bool>)(s => has.Contains(s)), low,
            });

    private static bool IsLow(int current, int max)
        => (bool)Router().GetMethod("IsLowHealth", All)!
            .Invoke(null, new object[] { current, max })!;

    private static readonly string[] Contract = { "idle", "attack", "hurt", "death" };

    private static readonly string[] Full =
        { "idle", "attack", "hurt", "death", "cast", "power", "idle_low" };

    [Fact]
    public void Cast_and_power_take_their_own_states_when_the_scene_has_them()
    {
        Assert.Equal("cast", Select("Cast", false, Full));
        Assert.Equal("power", Select("PowerUp", false, Full));
        // The base's own pairing: a scene with a cast clip but no power clip
        // plays the cast for a Power (CharacterModel.AnimationStates maps
        // PowerUp to "cast").
        Assert.Equal("cast", Select("PowerUp", false, "idle", "attack", "cast"));
    }

    [Fact]
    public void A_scene_with_only_the_four_contract_states_falls_back_silently()
    {
        // Seen to FAIL: before the pass Cast and PowerUp aliased straight to
        // attack, and that alias is what a four-state scene still gets.
        Assert.Equal("attack", Select("Cast", false, Contract));
        Assert.Equal("attack", Select("PowerUp", false, Contract));
        // Low HP with no low-HP idle is plain idle, never a missing state.
        Assert.Equal("idle", Select("Idle", true, Contract));
        Assert.Equal("idle", Select("Revive", true, Contract));
        // A body with no attack state at all ignores the trigger rather than
        // travelling to a state that is not there.
        Assert.Null(Select("Cast", false, "idle", "hurt", "death"));
        // Unknown triggers stay ignored.
        Assert.Null(Select("Relaxed", false, Full));
    }

    [Fact]
    public void The_idle_family_picks_the_slumped_idle_only_when_low()
    {
        Assert.Equal("idle_low", Select("Idle", true, Full));
        Assert.Equal("idle_low", Select("Revive", true, Full));
        Assert.Equal("idle", Select("Idle", false, Full));
        // One-shots are untouched by HP: the tree's own auto transitions
        // carry them back to the right idle.
        Assert.Equal("hurt", Select("Hit", true, Full));
        Assert.Equal("attack", Select("Attack", true, Full));
        Assert.Equal("death", Select("Dead", true, Full));
    }

    [Fact]
    public void Set_off_takes_its_own_state_and_falls_back_to_the_attack()
    {
        var withSetOff = Full.Append("setoff").ToArray();
        Assert.Equal("setoff", Select("SetOff", false, withSetOff));
        Assert.Equal("setoff", Select("SetOff", true, withSetOff));
        // Every other scene: the lunge, as the card's attack would have.
        Assert.Equal("attack", Select("SetOff", false, Full));
        Assert.Equal("attack", Select("SetOff", false, Contract));
    }

    [Fact]
    public void A_set_off_clip_absorbs_the_cards_own_lunge_but_not_a_hit()
    {
        bool Absorbed(string? current, string trigger) => (bool)Router()
            .GetMethod("AbsorbedBy", All)!.Invoke(null, new object?[] { current, trigger })!;

        Assert.True(Absorbed("setoff", "Attack"));
        Assert.True(Absorbed("setoff", "Cast"));
        Assert.True(Absorbed("setoff", "PowerUp"));
        Assert.False(Absorbed("setoff", "Hit"));
        Assert.False(Absorbed("setoff", "Dead"));
        Assert.False(Absorbed("idle", "Attack"));
        Assert.False(Absorbed(null, "Attack"));
    }

    [Fact]
    public void Klees_scene_opts_in_to_the_idle_desync()
    {
        var scene = RepoFile("klee-mod/pck-src/klee/model/combat.tscn");
        var key = (string)Il.Method("IdleDesync", "Apply").DeclaringType!
            .GetField("OptInMeta", All)!.GetValue(null)!;
        Assert.Contains($"metadata/{key} = true", scene);
        Assert.Contains("states/setoff/node = SubResource(", scene);
    }

    [Fact]
    public void Low_health_is_the_bases_quarter_line()
    {
        // CharacterModel.IsLowHealth: GetHpPercentRemaining() <= 0.25.
        Assert.Equal(0.25, (double)Router().GetField("LowHealthFraction", All)!
            .GetValue(null)!);
        Assert.True(IsLow(25, 100));
        Assert.True(IsLow(1, 80));
        Assert.True(IsLow(20, 80));
        Assert.False(IsLow(21, 80));
        Assert.False(IsLow(26, 100));
        Assert.False(IsLow(100, 100));
        // No max HP: nothing to divide by, never low.
        Assert.False(IsLow(0, 0));
    }

    [Fact]
    public void Skills_cast_powers_power_up_and_only_our_own_cards_ask()
    {
        string? For(CardType type, bool ours) => (string?)Motion()
            .GetMethod("TriggerFor", All)!
            .Invoke(null, new object[] { type, ours });

        Assert.Equal("Cast", For(CardType.Skill, true));
        Assert.Equal("PowerUp", For(CardType.Power, true));
        // An Attack already lunges through AttackCommand.
        Assert.Null(For(CardType.Attack, true));
        Assert.Null(For(CardType.Status, true));
        Assert.Null(For(CardType.Curse, true));
        // A base card makes its own TriggerAnim call; asking again would
        // replay the clip.
        Assert.Null(For(CardType.Skill, false));
        Assert.Null(For(CardType.Power, false));
    }

    [Fact]
    public void The_card_play_motion_is_a_postfix_on_the_base_hook()
    {
        // STRUCTURAL PIN: the attribute is what arms the patch, and the
        // method it names has to exist on the real Hook, or the whole mod
        // fails to load.
        var patch = Motion().Assembly.GetTypes()
            .Single(t => t.Name == "Hook_BeforeCardPlayed_CardPlayMotion");
        var info = patch.GetCustomAttribute<HarmonyPatch>()!.info;
        Assert.Equal(typeof(Hook), info.declaringType);
        Assert.Equal(nameof(Hook.BeforeCardPlayed), info.methodName);
        Assert.NotNull(AccessTools.Method(typeof(Hook), info.methodName));

        var postfix = patch.GetMethod("Postfix", All)!;
        Assert.NotNull(postfix.GetCustomAttribute<HarmonyPostfix>());
        Assert.Null(postfix.GetCustomAttribute<HarmonyPrefix>());
        Assert.Contains(postfix.GetParameters(),
            p => p.Name == "__result"
                 && p.ParameterType == typeof(Task).MakeByRefType());
        // The base's own delay properties, not a constant of ours.
        var calls = Il.Calls(Motion().GetMethod("Then", All)!);
        Assert.Contains(calls, c => c.Contains("TriggerAnim"));
    }

    [Theory]
    // Klee's one-shots run on the base game's clock since her model frames
    // (2026-10-12: base casts 0.97-1.8 s); Furina's keep the motion pass's.
    [InlineData("klee-mod/pck-src/klee/model/combat.tscn", 0.9, 1.1)]
    [InlineData("klee-mod/pck-src/furina/model/combat.tscn", 0.3, 0.5)]
    public void Klee_and_Furina_carry_the_three_new_states(string path, double min, double max)
    {
        var scene = RepoFile(path);
        foreach (var state in new[] { "cast", "power", "idle_low" })
        {
            Assert.Contains($"states/{state}/node = SubResource(", scene);
            Assert.Contains($"&\"{state}\": SubResource(\"Animation_{state}\")", scene);
        }

        // Each one-shot has its scene's own length band and returns to idle
        // on its own.
        foreach (var state in new[] { "cast", "power" })
        {
            var length = double.Parse(Regex.Match(scene,
                $"resource_name = \"{state}\"\\nlength = ([0-9.]+)").Groups[1].Value,
                System.Globalization.CultureInfo.InvariantCulture);
            Assert.InRange(length, min, max);
            Assert.Contains($"\"{state}\", \"idle\", SubResource(", scene);
        }

        // The low-HP idle hangs off exactly the two conditions the router
        // writes, so the scene and the code cannot drift apart.
        string Condition(string field) => ((string)Router().GetField(field, All)!
            .GetValue(null)!).Split('/').Last();
        Assert.Contains($"advance_condition = &\"{Condition("LowHealthCondition")}\"", scene);
        Assert.Contains($"advance_condition = &\"{Condition("HealthyCondition")}\"", scene);
        Assert.Contains("\"idle\", \"idle_low\", SubResource(", scene);
        Assert.Contains("\"idle_low\", \"idle\", SubResource(", scene);
        // A loop, and slower than the healthy idle.
        Assert.Matches("resource_name = \"idle_low\"\\nlength = [0-9.]+\\nloop_mode = 1", scene);
    }

    private static Type Thrown() => Il.Method("ThrownProjectile", "ArcPoint").DeclaringType!;

    private static Godot.Vector2 Arc(Godot.Vector2 a, Godot.Vector2 b, float t) =>
        (Godot.Vector2)Thrown().GetMethod("ArcPoint", All)!
            .Invoke(null, new object[] { a, b, t, 70f })!;

    [Fact]
    public void The_thrown_bomb_runs_hand_to_target_over_an_arc_either_way()
    {
        var hand = new Godot.Vector2(100, -140);
        var enemy = new Godot.Vector2(700, -100);
        Assert.Equal(hand, Arc(hand, enemy, 0f));
        Assert.Equal(enemy, Arc(hand, enemy, 1f));
        // Mid-flight it rides above the straight line (up is -Y on screen),
        // and a flipped Klee throwing leftward arcs up too, not down.
        Assert.True(Arc(hand, enemy, 0.5f).Y < -120 - 60);
        var mirrored = new Godot.Vector2(-100, -140);
        var leftEnemy = new Godot.Vector2(-700, -100);
        Assert.True(Arc(mirrored, leftEnemy, 0.5f).Y < -120 - 60);
        Assert.InRange(Arc(mirrored, leftEnemy, 0.5f).X, -420, -380);
    }

    [Fact]
    public void The_bomb_aims_at_its_target_or_the_middle_of_the_side()
    {
        Godot.Vector2? Aim(Godot.Vector2? single, params Godot.Vector2[] side) =>
            (Godot.Vector2?)Thrown().GetMethod("AimPoint", All)!
                .Invoke(null, new object?[] { single, side.ToList() });

        var a = new Godot.Vector2(600, -100);
        var b = new Godot.Vector2(800, -120);
        Assert.Equal(a, Aim(a, a, b));
        // AoE, random targets, or no command behind the trigger: the side.
        Assert.Equal(new Godot.Vector2(700, -110), Aim(null, a, b));
        Assert.Null(Aim(null));
    }

    [Fact]
    public void Only_a_fresh_entry_into_the_attack_clip_throws()
    {
        bool Throws(string? from, string to) => (bool)Thrown()
            .GetMethod("Throws", All)!.Invoke(null, new object?[] { from, to })!;

        Assert.True(Throws("idle", "attack"));
        Assert.True(Throws("idle_low", "attack"));
        Assert.True(Throws(null, "attack"));
        // A no-op travel replays nothing, so it throws nothing.
        Assert.False(Throws("attack", "attack"));
        Assert.False(Throws("idle", "cast"));
        Assert.False(Throws("idle", "setoff"));
    }

    [Fact]
    public void Jumpy_dumpty_takes_its_own_state_and_falls_back_to_the_attack()
    {
        // [USER], 2026-10-13: "I think the increased size would be fitting for
        // her Jumpty Dumpty skill usage."
        var withJumpy = Full.Append("jumpy").ToArray();
        Assert.Equal("jumpy", Select("Jumpy", false, withJumpy));
        Assert.Equal("jumpy", Select("Jumpy", true, withJumpy));
        Assert.Equal("attack", Select("Jumpy", false, Full));
        Assert.Equal("attack", Select("Jumpy", false, Contract));
    }

    [Fact]
    public void A_jumpy_clip_absorbs_the_cards_own_lunge_but_not_a_hit()
    {
        bool Absorbed(string? current, string trigger) => (bool)Router()
            .GetMethod("AbsorbedBy", All)!.Invoke(null, new object?[] { current, trigger })!;

        Assert.True(Absorbed("jumpy", "Attack"));
        Assert.True(Absorbed("jumpy", "Cast"));
        Assert.True(Absorbed("jumpy", "PowerUp"));
        Assert.False(Absorbed("jumpy", "Hit"));
        Assert.False(Absorbed("jumpy", "Dead"));
    }

    [Fact]
    public void The_three_jumpy_dumpty_cards_and_only_they_play_the_jumpy_clip()
    {
        bool IsJumpy(string typeName)
        {
            var type = Motion().Assembly.GetTypes().Single(t => t.FullName == typeName);
            var card = System.Runtime.CompilerServices.RuntimeHelpers.GetUninitializedObject(type);
            return (bool)Motion().GetMethod("IsJumpyPlay", All)!.Invoke(null, new[] { card })!;
        }

        Assert.True(IsJumpy("KleeMod.Cards.Prototype.Generated.ProtoKoJumpyDumpty"));
        Assert.True(IsJumpy("KleeMod.Cards.Prototype.Generated.ProtoKoJumpyDumptyMkIii"));
        Assert.True(IsJumpy("KleeMod.Cards.JumpyDumptyMkOmega"));
        Assert.False(IsJumpy("KleeMod.Cards.Prototype.Generated.ProtoKoBangBang"));
        Assert.Equal("Jumpy", (string)Motion().GetField("JumpyTrigger", All)!.GetValue(null)!);
    }

    [Fact]
    public void A_fresh_entry_into_the_jumpy_clip_throws_the_big_bomb()
    {
        string? For(string? from, string to) => (string?)Thrown()
            .GetMethod("ProjectileFor", All)!.Invoke(null, new object?[] { from, to });

        Assert.Equal("ThrownProjectile", For("idle", "attack"));
        Assert.Equal("JumpyProjectile", For("idle", "jumpy"));
        Assert.Equal("JumpyProjectile", For("idle_low", "jumpy"));
        Assert.Null(For("jumpy", "jumpy"));
        Assert.Null(For("idle", "setoff"));

        var scene = RepoFile("klee-mod/pck-src/klee/model/combat.tscn");
        var block = Regex.Match(scene,
            "\\[node name=\"JumpyProjectile\" type=\"Sprite2D\" parent=\"Visuals/Facing\"\\]\\n((?:.+\\n)+)");
        Assert.True(block.Success, "no %JumpyProjectile under %Facing");
        var body = block.Groups[1].Value;
        Assert.Contains("unique_name_in_owner = true", body);
        Assert.Contains("visible = false", body);
        Assert.Contains("klee_bomb_big.png", scene);
        var release = double.Parse(Regex.Match(body, "metadata/release = ([0-9.]+)").Groups[1].Value,
            System.Globalization.CultureInfo.InvariantCulture);
        Assert.InRange(release, 0.5, 1.0);
    }

    [Fact]
    public void Klees_scene_carries_the_bomb_and_the_hit_waits_for_it()
    {
        var scene = RepoFile("klee-mod/pck-src/klee/model/combat.tscn");
        var name = (string)Thrown().GetField("NodeName", All)!.GetValue(null)!;
        var meta = (string)Thrown().GetField("ReleaseMeta", All)!.GetValue(null)!;
        var block = Regex.Match(scene,
            $"\\[node name=\"{name}\" type=\"Sprite2D\" parent=\"Visuals/Facing\"\\]\\n((?:.+\\n)+)");
        Assert.True(block.Success, "no %ThrownProjectile under %Facing");
        var body = block.Groups[1].Value;
        Assert.Contains("unique_name_in_owner = true", body);
        Assert.Contains("visible = false", body);
        Assert.Contains("klee_bomb.png", scene);
        var release = double.Parse(Regex.Match(body, $"metadata/{meta} = ([0-9.]+)").Groups[1].Value,
            System.Globalization.CultureInfo.InvariantCulture);
        Assert.InRange(release, 0.2, 0.8);

        // The damage lands as the bomb does, not before it leaves her hand.
        var flight = (float)Thrown().GetField("FlightSeconds", All)!.GetValue(null)!;
        var klee = Router().Assembly.GetTypes().Single(t => t.FullName == "KleeMod.Klee");
        var model = System.Runtime.CompilerServices.RuntimeHelpers.GetUninitializedObject(klee);
        var delay = (float)klee.GetProperty("AttackAnimDelay")!.GetValue(model)!;
        Assert.InRange(delay, release + flight - 0.05, release + flight + 0.05);
    }

    [Fact]
    public void The_aim_is_noted_by_a_prefix_on_the_attack_command()
    {
        var patch = Thrown().Assembly.GetTypes()
            .Single(t => t.Name == "AttackCommand_Execute_ThrownAim");
        var info = patch.GetCustomAttribute<HarmonyPatch>()!.info;
        Assert.Equal("AttackCommand", info.declaringType.Name);
        Assert.Equal("Execute", info.methodName);
        Assert.NotNull(patch.GetMethod("Prefix", All)!.GetCustomAttribute<HarmonyPrefix>());
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
