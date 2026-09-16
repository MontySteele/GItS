using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Nodes.Combat;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE CREATURE ANIMATION ROUTER'S THREE DOORS (`EB-159`).
///
/// The router drives an %AnimationTree inside a convention combat scene, which
/// is how every spine-less character in this mod animates: the game only ever
/// animates through <c>_spineAnimator</c>, and <c>NCreature</c> builds one
/// solely when <c>Visuals.HasSpineAnimation</c>. So each place the base game
/// gates an animation on that animator is a place a MODDED PLAYER hears
/// nothing, and each one needs its own door.
///
/// TWO WERE OPEN AND ONE WAS NOT. <c>SetAnimationTrigger</c> is the general
/// door and <c>StartDeathAnim</c> was already special-cased beside it;
/// <c>StartReviveAnim</c> was not, and its spine-less arm
/// (<c>AnimTempRevive</c> -> <c>ImmediatelySetIdle</c>) writes the animator
/// DIRECTLY, so it bypassed both. A revived Klee stayed in the tree's death
/// state for the rest of the fight.
///
/// WHAT IS REAL HERE. The patch attributes and the trigger table are plain
/// reflection reads off the real assembly; ROUTING itself needs Godot nodes,
/// which is process death in this host (README, the headless boundary), so
/// the pin is structural and says so.
/// </summary>
public class CreatureAnimationRouterTests
{
    private const BindingFlags All = HeadlessGame.All;

    /// <summary>One of our patch classes, by name, off the mod assembly --
    /// `Il.Method`'s own lookup, which is where "the real assembly" is
    /// defined for this suite.</summary>
    private static Type Patch(string name) =>
        Il.Method("CreatureAnimationRouter", "Route").DeclaringType!.Assembly
            .GetTypes()
            .FirstOrDefault(t => t.Name == name)
        ?? throw new InvalidOperationException($"no patch class {name}");

    /// <summary>`(patched type, patched method name)`, read off the attribute
    /// the loader itself reads.</summary>
    private static (Type, string) Target(string name)
    {
        var info = Patch(name).GetCustomAttribute<HarmonyPatch>()!.info;
        return (info.declaringType!, info.methodName!);
    }

    [Fact]
    public void The_revive_seam_has_a_door_of_its_own()
    {
        // `EB-159`. `StartReviveAnim` emits "Revive" only when a spine
        // animator has the trigger, and ours never do -- the spine-less arm
        // is `AnimTempRevive`, whose `ImmediatelySetIdle` writes
        // `_spineAnimator` directly and so misses the general postfix as well.
        // STRUCTURAL PIN: the attribute is what arms the patch, so the
        // attribute is what is read.
        //
        // Seen to FAIL: there was no such patch class.
        var (type, method) = Target(
            "NCreature_StartReviveAnim_AnimationTreeRoute");

        Assert.Equal(typeof(NCreature), type);
        Assert.Equal(nameof(NCreature.StartReviveAnim), method);
    }

    [Fact]
    public void Every_seam_the_router_serves_is_a_postfix_on_NCreature()
    {
        // The three doors, and each is a POSTFIX: a prefix here would change
        // base behaviour, which this layer never does -- it draws after the
        // game has drawn, on creatures whose visuals opt in by carrying a
        // tree.
        foreach (var name in new[]
                 {
                     "NCreature_SetAnimationTrigger_AnimationTreeRoute",
                     "NCreature_StartDeathAnim_AnimationTreeRoute",
                     "NCreature_StartReviveAnim_AnimationTreeRoute",
                 })
        {
            var (type, _) = Target(name);
            Assert.Equal(typeof(NCreature), type);

            var postfix = Patch(name).GetMethod("Postfix", All);
            Assert.NotNull(postfix);
            Assert.NotNull(postfix!.GetCustomAttribute<HarmonyPostfix>());
            Assert.Null(postfix.GetCustomAttribute<HarmonyPrefix>());
        }
    }

    [Fact]
    public void Revive_returns_the_tree_to_idle_and_death_stays_death()
    {
        // The word the new door carries has to be one the table knows, and it
        // has to land on idle: that is what a base-game spine rig does with
        // the trigger and what `ImmediatelySetIdle` does with the animator.
        var table = (Dictionary<string, string>)
            Il.Method("CreatureAnimationRouter", "Route").DeclaringType!
                .GetField("TriggerToState", All)!
                .GetValue(null)!;

        Assert.Equal("idle", table["Revive"]);
        Assert.Equal("death", table["Dead"]);
        // Unknown triggers are IGNORED rather than forced to idle, so a future
        // game trigger cannot yank a mid-flight animation. The table is the
        // whole allowlist.
        Assert.DoesNotContain("Revived", table.Keys);
    }
}
