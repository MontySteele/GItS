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
    [InlineData("klee-mod/pck-src/klee/model/combat.tscn")]
    [InlineData("klee-mod/pck-src/furina/model/combat.tscn")]
    public void Klee_and_Furina_carry_the_three_new_states(string path)
    {
        var scene = RepoFile(path);
        foreach (var state in new[] { "cast", "power", "idle_low" })
        {
            Assert.Contains($"states/{state}/node = SubResource(", scene);
            Assert.Contains($"&\"{state}\": SubResource(\"Animation_{state}\")", scene);
        }

        // Each one-shot is short (the base's own cast windows are 0.25-0.5 s)
        // and returns to idle on its own.
        foreach (var state in new[] { "cast", "power" })
        {
            var length = double.Parse(Regex.Match(scene,
                $"resource_name = \"{state}\"\\nlength = ([0-9.]+)").Groups[1].Value,
                System.Globalization.CultureInfo.InvariantCulture);
            Assert.InRange(length, 0.3, 0.5);
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
