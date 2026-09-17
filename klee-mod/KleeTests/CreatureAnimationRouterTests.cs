using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;
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

    /// <summary>One member off `ModdedPlayerDeathSeam`, the same
    /// "off the real assembly" lookup <see cref="Patch"/> uses.</summary>
    private static Type Seam() => Patch("ModdedPlayerDeathSeam");

    private static bool Covers(
        bool hasSpine, bool isPlayer, bool isPet, float baseLength)
        => (bool)Seam().GetMethod("Covers", All)!
            .Invoke(null, new object[] { hasSpine, isPlayer, isPet, baseLength })!;

    private static float LengthFor(float clipLength)
        => (float)Seam().GetMethod("LengthFor", All)!
            .Invoke(null, new object[] { clipLength })!;

    private static bool CoversDressedBody(
        bool armEnabled, bool hasSpine, string? visualsScene, float baseLength)
        => (bool)Seam().GetMethod("CoversDressedBody", All)!
            .Invoke(null, new object?[]
                { armEnabled, hasSpine, visualsScene, baseLength })!;

    private static float DressedLengthFor(float clipLength, float baseLength)
        => (float)Seam().GetMethod("DressedLengthFor", All)!
            .Invoke(null, new object[] { clipLength, baseLength })!;

    [Fact]
    public void The_death_seam_has_a_door_of_its_own()
    {
        // `EB-159`, the remaining third. `StartDeathAnim` puts the death SFX
        // and the clip measurement inside `if (_spineAnimator != null)`
        // (NCreature.cs:933-946), so a spine-less player died silently and
        // returned length 0 to `Hook.AfterDeath`.
        //
        // Seen to FAIL: there was no such patch class.
        var (type, method) = Target("NCreature_StartDeathAnim_ModdedPlayerSeam");

        Assert.Equal(typeof(NCreature), type);
        Assert.Equal(nameof(NCreature.StartDeathAnim), method);

        // A POSTFIX taking `ref float __result`: the base runs first and this
        // fills in only what its gate skipped. A prefix here would change base
        // behaviour, which this layer never does.
        var postfix = Patch("NCreature_StartDeathAnim_ModdedPlayerSeam")
            .GetMethod("Postfix", All);
        Assert.NotNull(postfix);
        Assert.NotNull(postfix!.GetCustomAttribute<HarmonyPostfix>());
        Assert.Null(postfix.GetCustomAttribute<HarmonyPrefix>());
        Assert.Contains(
            postfix.GetParameters(),
            p => p.Name == "__result" && p.ParameterType == typeof(float).MakeByRefType());
    }

    [Fact]
    public void The_death_sound_is_the_games_own_and_plays_only_for_us()
    {
        // The sound has to be the base's, not a substitute: `SfxCmd.PlayDeath`
        // is the exact call the spine gate skipped (NCreature.cs:942).
        // STRUCTURAL PIN -- playing it needs a live FMOD, which is outside the
        // headless boundary, so the call site is what is read.
        var calls = Il.Calls(Seam().GetMethod("Cover", All)!);
        Assert.Contains("SfxCmd.PlayDeath", calls);

        // SCOPE. Only a spine-less PLAYER, never a pet and never an enemy, and
        // only where the base measured nothing -- so this can fill a zero in
        // and can never shorten a real animation.
        Assert.True(Covers(hasSpine: false, isPlayer: true, isPet: false, baseLength: 0f));
        Assert.False(Covers(hasSpine: true, isPlayer: true, isPet: false, baseLength: 0f));
        Assert.False(Covers(hasSpine: false, isPlayer: false, isPet: false, baseLength: 0f));
        Assert.False(Covers(hasSpine: false, isPlayer: true, isPet: true, baseLength: 0f));
        Assert.False(Covers(hasSpine: false, isPlayer: true, isPet: false, baseLength: 1.4f));
    }

    [Fact]
    public void The_death_length_is_the_bodys_own_clip_under_the_bases_ceiling()
    {
        // The base's rule is that the death animation's own length is the
        // timing authority, so a measured clip is reported as-is (Klee 1.0 s,
        // Furina 1.2 s in pck-src/*/model/combat.tscn) ...
        Assert.Equal(1.0f, LengthFor(1.0f));
        Assert.Equal(1.2f, LengthFor(1.2f));

        // ... under the base's own 30 s ceiling (NCreature.cs:945) ...
        Assert.Equal(30f, LengthFor(90f));

        // ... and a body with no clip to measure -- a flat portrait with no
        // tree -- gets the named fallback rather than the zero that started
        // this row.
        var fallback = (float)Seam()
            .GetField("FallbackDeathAnimLength", All)!.GetValue(null)!;
        Assert.Equal(1.0f, fallback);
        Assert.Equal(fallback, LengthFor(0f));
        Assert.True(LengthFor(0f) > 0f);
    }

    // -----------------------------------------------------------------------
    // THE MOTION PASS: a dressed Teyvat body is the seam's second arm
    // -----------------------------------------------------------------------

    [Fact]
    public void The_dressed_body_arm_is_shut_unless_the_arm_is_on_and_the_scene_is_ours()
    {
        const string ours = "res://teyvat/creature_visuals/anemo_slime.tscn";

        // The one case it covers: arm on, spine-less (the base's gate was
        // false), the base measured nothing, and this body draws through a
        // Teyvat scene.
        Assert.True(CoversDressedBody(
            armEnabled: true, hasSpine: false, visualsScene: ours, baseLength: 0f));

        // ARM OFF IS THE ACCEPTANCE CONDITION. Every calibration deploy and
        // every release package ships TeyvatFrame.Enabled false, and on that
        // side the seam must be byte-for-byte what it was before this pass.
        Assert.False(CoversDressedBody(
            armEnabled: false, hasSpine: false, visualsScene: ours, baseLength: 0f));

        // An UNDRESSED enemy, even with the arm on: the registry has no row
        // for it, so DressedVisualsScene hands back null.
        Assert.False(CoversDressedBody(
            armEnabled: true, hasSpine: false, visualsScene: null, baseLength: 0f));

        // A scene outside our namespace is not ours to animate.
        Assert.False(CoversDressedBody(
            armEnabled: true, hasSpine: false,
            visualsScene: "res://scenes/creature_visuals/nibbit.tscn", baseLength: 0f));

        // A spine body's own animator already answered, and a base result that
        // measured something is never overwritten -- both the same refusals
        // the player arm makes.
        Assert.False(CoversDressedBody(
            armEnabled: true, hasSpine: true, visualsScene: ours, baseLength: 0f));
        Assert.False(CoversDressedBody(
            armEnabled: true, hasSpine: false, visualsScene: ours, baseLength: 1.4f));
    }

    [Fact]
    public void A_dressed_body_with_no_clip_to_measure_is_left_exactly_as_it_was()
    {
        // A measured clip is reported under the base's ceiling, as for a
        // player. The five motion sets' death clips are 1.2 s (stand, bounce,
        // hover, mech) and 1.6 s (loom) --
        // tools/gen_teyvat_creature_scenes.py MOTIONS.
        Assert.Equal(1.2f, DressedLengthFor(1.2f, 0f));
        Assert.Equal(1.6f, DressedLengthFor(1.6f, 0f));
        Assert.Equal(30f, DressedLengthFor(90f, 0f));

        // But with NO clip it hands back the BASE's own answer rather than the
        // player fallback: an enemy with no motion is an enemy this pass never
        // touched, and R213 says leave it alone.
        Assert.Equal(0f, DressedLengthFor(0f, 0f));
        Assert.Equal(0.8f, DressedLengthFor(0f, 0.8f));
    }

    [Fact]
    public void The_death_sting_stays_on_the_player_arm_only()
    {
        // `SfxCmd.PlayDeath` takes a Player and is the PLAYER's death sting;
        // a monster's death audio is the base game's and is not on this path.
        // ONE call site, so the dressed arm cannot have grown one.
        var calls = Il.CallSequence(Seam().GetMethod("Cover", All)!);
        Assert.Equal(1, calls.Count(c => c.Contains("PlayDeath")));

        // And the dressed arm reads the arm switch itself, rather than
        // trusting a caller to have checked.
        Assert.Contains(calls, c => c.Contains("TeyvatFrame") && c.Contains("Enabled"));
    }

    [Fact]
    public void The_router_finds_its_tree_on_a_generated_teyvat_scene()
    {
        // THE SHAPE THE ROUTER LOOKS FOR, read off a committed scene rather
        // than described. `CreatureAnimationRouter.Route` does
        // `visuals.GetNodeOrNull<AnimationTree>("%AnimationTree")`, so a
        // generated body animates if and only if it declares a node called
        // AnimationTree with unique_name_in_owner set.
        //
        // STRUCTURAL PIN, and it says so: resolving the lookup needs a live
        // scene tree, which is process death in this host (README, the
        // headless boundary). What the deploy still has to prove is that the
        // unique name SURVIVES BaseLib's NCreatureVisualsFactory reparenting
        // our children onto a fresh NCreatureVisuals.
        var scene = RepoFile(
            "klee-mod/pck-src/teyvat/creature_visuals/anemo_slime.tscn");

        Assert.Contains(
            "[node name=\"AnimationTree\" type=\"AnimationTree\" parent=\".\"]", scene);
        Assert.Contains(
            "[node name=\"AnimationPlayer\" type=\"AnimationPlayer\" parent=\".\"]",
            scene);
        // The tree reaches the player as a SIBLING, which is what keeps
        // working after the reparent.
        Assert.Contains("anim_player = NodePath(\"../AnimationPlayer\")", scene);
        // Six unique names: the four NCreatureVisuals._Ready fetches, plus
        // the two this layer fetches.
        Assert.Equal(6, Regex.Matches(scene, "unique_name_in_owner = true").Count);

        // The library is EXTERNAL and under the namespace the death seam gates
        // on, and the four router states are the tree's four states.
        Assert.Contains("[ext_resource type=\"AnimationLibrary\" "
                        + "path=\"res://teyvat/motion/", scene);
        foreach (var state in new[] { "idle", "attack", "hurt", "death" })
        {
            Assert.Contains($"states/{state}/node = SubResource(", scene);
        }

        // And the seam's own constant is the directory those scenes live in,
        // so the gate and the generator cannot drift apart.
        var root = (string)Seam().GetField("TeyvatVisualsRoot", All)!.GetValue(null)!;
        Assert.Equal("res://teyvat/creature_visuals/", root);
    }

    /// <summary>A repo-root-relative file, found by walking up from the test
    /// binary (the same walk `ResourceTexturePathTests.RepoFile` uses).</summary>
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
