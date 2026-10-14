using System;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// MODEL FACING (2026-10-14, the Kaiser Crab fight: Furina never turned to the
/// claw she was fighting). The decision is a pure function read off the real
/// assembly; the scene side needs Godot nodes, which is process death in this
/// host, so the patches are structural pins: each names a method that exists
/// on the real game, or the mod fails to load.
/// </summary>
public class CreatureFacingTests
{
    private const BindingFlags All = HeadlessGame.All;

    private static Type Facing() =>
        Il.Method("CreatureFacing", "DecideSign").DeclaringType!;

    private static float? Decide(float self, float current, float[] aimed,
                                 float[] opponents, bool onlyIfEmpty)
        => (float?)Facing().GetMethod("DecideSign", All)!
            .Invoke(null, new object[] { self, current, aimed, opponents, onlyIfEmpty });

    private static readonly float[] None = Array.Empty<float>();

    [Fact]
    public void An_explicit_aim_turns_toward_it_either_way()
    {
        Assert.Equal(-1f, Decide(500, 1, new[] { 200f }, None, false));
        Assert.Equal(1f, Decide(500, -1, new[] { 800f }, None, false));
    }

    [Fact]
    public void A_live_aim_wins_over_the_centre_of_the_living()
    {
        // Crusher on the left is the target; three enemies on the right pull
        // the centre right. The aim holds until Crusher dies.
        Assert.Equal(-1f, Decide(500, -1, new[] { 200f },
            new[] { 200f, 800f, 850f, 900f }, false));
    }

    [Fact]
    public void With_no_live_aim_the_turn_start_faces_the_centre_of_the_living()
    {
        Assert.Equal(1f, Decide(500, -1, None, new[] { 800f }, false));
        // Spread evenly about her: inside the dead zone, so she stays.
        Assert.Null(Decide(500, -1, None, new[] { 200f, 800f }, false));
        Assert.Null(Decide(500, 1, None, None, false));
    }

    [Fact]
    public void A_death_turns_her_only_when_the_side_she_faces_empties()
    {
        // Facing left, someone still lives on the left: she keeps facing it.
        Assert.Null(Decide(500, -1, None, new[] { 200f, 800f, 900f }, true));
        // The left emptied: she turns to the right.
        Assert.Equal(1f, Decide(500, -1, None, new[] { 800f, 900f }, true));
    }

    [Fact]
    public void A_target_on_top_of_her_is_inside_the_dead_zone()
    {
        Assert.Null(Decide(500, 1, new[] { 490f }, None, false));
        Assert.Null(Decide(500, 1, new[] { 520f }, None, false));
    }

    [Theory]
    [InlineData("AttackCommand_Execute_Facing", "Execute")]
    [InlineData("Hook_BeforeCardPlayed_Facing", "BeforeCardPlayed")]
    [InlineData("Hook_AfterDeath_Facing", "AfterDeath")]
    [InlineData("Hook_AfterPlayerTurnStart_Facing", "AfterPlayerTurnStart")]
    [InlineData("CreatureCmd_Damage_Facing", "Damage")]
    public void Every_facing_patch_is_a_prefix_on_a_real_method(string patchName, string method)
    {
        var patch = Facing().Assembly.GetTypes().Single(t => t.Name == patchName);
        var info = patch.GetCustomAttribute<HarmonyPatch>()!.info;
        Assert.Equal(method, info.methodName);
        var target = info.argumentTypes == null
            ? AccessTools.Method(info.declaringType, info.methodName)
            : AccessTools.Method(info.declaringType, info.methodName, info.argumentTypes);
        Assert.NotNull(target);

        var prefix = patch.GetMethod("Prefix", All)!;
        Assert.NotNull(prefix.GetCustomAttribute<HarmonyPrefix>());
        // Harmony binds a prefix's parameters by name: each must be one the
        // target declares (or __instance).
        var names = target!.GetParameters().Select(p => p.Name).ToHashSet();
        foreach (var p in prefix.GetParameters())
        {
            Assert.True(p.Name == "__instance" || names.Contains(p.Name),
                $"{patchName}.Prefix binds '{p.Name}', which {method} does not declare");
        }
    }

    [Fact]
    public void The_damage_patch_sits_on_the_funnel_every_overload_reaches()
    {
        // The overload with targets, dealer, card and play is the one the
        // others call (decompile, v0.111.0); patching another would miss hits.
        var patch = Facing().Assembly.GetTypes()
            .Single(t => t.Name == "CreatureCmd_Damage_Facing");
        var args = patch.GetCustomAttribute<HarmonyPatch>()!.info.argumentTypes!;
        Assert.Equal(7, args.Length);
        Assert.Contains(args, a => a.Name.StartsWith("IEnumerable", StringComparison.Ordinal));
    }
}
