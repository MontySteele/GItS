using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
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

    // -----------------------------------------------------------------------
    // EB-797: THE ENGINE'S OWN DEATH WAIT
    // -----------------------------------------------------------------------
    //
    // `NCreature.AnimDie` (NCreature.cs:1002-1018) waits
    // `min(GetCurrentAnimationTimeRemaining() + 0.5, 20)` behind the SAME
    // spine gate `StartDeathAnim` put the SFX and the clip measurement behind,
    // so for a spine-less body the engine's own wait was handed a zero and
    // only the mod's `AfterDeath` length waited at all. `ModdedDeathWaitSeam`
    // reports the body's own remaining -- on the death path and nowhere else,
    // because `GetCurrentAnimationTimeRemaining` has other callers.

    private static Type WaitSeam() => Patch("ModdedDeathWaitSeam");

    private static bool WaitCovers(
        bool deathInFlight, bool hasSpine, float baseRemaining, string? state)
        => (bool)WaitSeam().GetMethod("Covers", All)!
            .Invoke(null, new object?[]
                { deathInFlight, hasSpine, baseRemaining, state })!;

    private static float RemainingFor(
        float clipLength, float playPosition, float baseRemaining)
        => (float)WaitSeam().GetMethod("RemainingFor", All)!
            .Invoke(null, new object[]
                { clipLength, playPosition, baseRemaining })!;

    [Fact]
    public void The_engine_death_wait_has_a_door_of_its_own()
    {
        // STRUCTURAL PIN: the attribute is what arms the patch, and the method
        // it names has to EXIST on the real NCreature -- a Harmony patch on a
        // method that is not there takes the whole mod down at load.
        //
        // Seen to FAIL: there was no such patch class.
        var (type, method) = Target(
            "NCreature_GetCurrentAnimationTimeRemaining_DeathWaitSeam");

        Assert.Equal(typeof(NCreature), type);
        Assert.Equal("GetCurrentAnimationTimeRemaining", method);
        Assert.NotNull(AccessTools.Method(typeof(NCreature), method));

        // A POSTFIX taking `ref float __result`: the base answers first and
        // this substitutes only where its gate left a zero.
        var postfix = Patch("NCreature_GetCurrentAnimationTimeRemaining_DeathWaitSeam")
            .GetMethod("Postfix", All);
        Assert.NotNull(postfix);
        Assert.NotNull(postfix!.GetCustomAttribute<HarmonyPostfix>());
        Assert.Null(postfix.GetCustomAttribute<HarmonyPrefix>());
        Assert.Contains(
            postfix.GetParameters(),
            p => p.Name == "__result" && p.ParameterType == typeof(float).MakeByRefType());
    }

    [Fact]
    public void The_wait_seam_answers_on_the_death_path_and_nowhere_else()
    {
        // The one case it covers: this creature's death is in flight, the body
        // is spine-less (the base's gate was false), the base measured
        // nothing, and the tree is standing in the death state right now.
        Assert.True(WaitCovers(
            deathInFlight: true, hasSpine: false, baseRemaining: 0f, state: "death"));

        // NOT MID-DEATH, and this is the whole answer to
        // "GetCurrentAnimationTimeRemaining has other callers": an unmarked
        // creature reads the base's own answer, so an idle body, a hurt body
        // and every other caller are untouched.
        Assert.False(WaitCovers(
            deathInFlight: false, hasSpine: false, baseRemaining: 0f, state: "death"));

        // A spine body's own animator already answered, and a base result that
        // measured something is never overwritten -- the same two refusals the
        // length seam makes.
        Assert.False(WaitCovers(
            deathInFlight: true, hasSpine: true, baseRemaining: 0f, state: "death"));
        Assert.False(WaitCovers(
            deathInFlight: true, hasSpine: false, baseRemaining: 1.4f, state: "death"));

        // And the tree has to be playing the death state: a body that was
        // revived travels back to "idle", and a tree standing nowhere answers
        // nothing.
        Assert.False(WaitCovers(
            deathInFlight: true, hasSpine: false, baseRemaining: 0f, state: "idle"));
        Assert.False(WaitCovers(
            deathInFlight: true, hasSpine: false, baseRemaining: 0f, state: null));
    }

    [Fact]
    public void The_remaining_wait_is_what_is_left_of_the_bodys_own_clip()
    {
        // Half of Klee's 1.0 s death clip played is half a second left.
        Assert.Equal(0.5f, RemainingFor(clipLength: 1.0f, playPosition: 0.5f,
                                        baseRemaining: 0f));
        // Nothing played yet is the whole clip -- Furina 1.2 s, loom 1.6 s.
        Assert.Equal(1.2f, RemainingFor(1.2f, 0f, 0f));
        Assert.Equal(1.6f, RemainingFor(1.6f, 0f, 0f));

        // AnimDie's own 20 s ceiling, kept rather than re-argued
        // (NCreature.cs:1006-1010). The engine adds its own +0.5 pad on top of
        // whatever this hands back, so the pad is not applied here.
        var ceiling = (float)WaitSeam().GetField("MaxDeathWait", All)!.GetValue(null)!;
        Assert.Equal(20f, ceiling);
        Assert.Equal(ceiling, RemainingFor(90f, 0f, 0f));

        // NO CLIP TO MEASURE, and a clip already finished, both hand back the
        // BASE's own answer rather than a number of our invention: past the
        // end there is nothing left to wait for.
        Assert.Equal(0f, RemainingFor(0f, 0f, 0f));
        Assert.Equal(0.3f, RemainingFor(0f, 0f, 0.3f));
        Assert.Equal(0f, RemainingFor(1.0f, 1.0f, 0f));
        Assert.Equal(0.3f, RemainingFor(1.0f, 4.0f, 0.3f));
    }

    [Fact]
    public void Only_the_covered_branches_of_the_length_seam_arm_the_wait()
    {
        // SCOPE, AND IT IS THE POINT OF THE ROW. R213 froze base-enemy
        // behaviour, so the engine's wait may reach modded players and dressed
        // Teyvat bodies and NOTHING else. That is guaranteed by the mark being
        // set in exactly the two covered branches of the length seam -- the
        // player arm and the dressed arm -- and in no other method anywhere in
        // the mod. Assembly-wide, so a third caller cannot appear quietly.
        var armed = WaitSeam().Assembly.GetTypes()
            .SelectMany(t => t.GetMethods(All))
            .Where(m =>
            {
                try
                {
                    return !m.IsAbstract
                        && Il.Calls(m).Any(
                            c => c.EndsWith(".NoteDeathStarted", StringComparison.Ordinal));
                }
                catch
                {
                    return false;
                }
            })
            .Select(m => $"{m.DeclaringType!.Name}.{m.Name}")
            .Distinct()
            .ToList();

        Assert.Equal(new[] { "ModdedPlayerDeathSeam.Cover" }, armed);

        // TWICE inside it: once on the player arm, once on the dressed arm.
        var sequence = Il.CallSequence(Seam().GetMethod("Cover", All)!);
        Assert.Equal(2, sequence.Count(c => c.Contains("NoteDeathStarted")));
    }

    [Fact]
    public void A_revived_body_is_not_read_as_mid_death()
    {
        // `AnimTempRevive` brings a spine-less player back, and the router
        // already returns its tree to idle there -- so that is where the mark
        // is dropped. One door, not two.
        var (type, method) = Target("NCreature_StartReviveAnim_DeathWaitSeam");
        Assert.Equal(typeof(NCreature), type);
        Assert.Equal(nameof(NCreature.StartReviveAnim), method);
        Assert.Contains(
            "ModdedDeathWaitSeam.Forget",
            Il.Calls(Patch("NCreature_StartReviveAnim_DeathWaitSeam")
                .GetMethod("Postfix", All)!));
    }

    // -----------------------------------------------------------------------
    // EB-816: THE IDLE DESYNC
    // -----------------------------------------------------------------------
    //
    // [USER] on `0.2.3656` (2026-09-17): a pack of slimes "all bobbing at the
    // exact same time at high speed". *High speed* was the clip and lives in
    // `tools/gen_teyvat_creature_scenes.py`; *the exact same time* is this --
    // every dressed body is a fresh instance of the same scene playing the
    // same shared library from the same zero at the same frame.

    private static Type Desync() => Patch("IdleDesync");

    private static (float Phase, float Speed) DesyncFor(int seed)
    {
        var tuple = (ValueTuple<float, float>)
            Desync().GetMethod("For", All)!.Invoke(null, new object[] { seed })!;
        return (tuple.Item1, tuple.Item2);
    }

    private static bool DesyncCovers(bool armEnabled, string? visualsScene)
        => (bool)Desync().GetMethod("Covers", All)!
            .Invoke(null, new object?[] { armEnabled, visualsScene })!;

    private static float PhaseSecondsFor(float idleLength, float phaseFraction)
        => (float)Desync().GetMethod("PhaseSecondsFor", All)!
            .Invoke(null, new object[] { idleLength, phaseFraction })!;

    [Fact]
    public void The_offset_and_the_speed_stay_inside_the_band_the_row_claims()
    {
        // A phase is a FRACTION of the idle, so it is in [0, 1) by contract --
        // the caller multiplies by the clip's own length, and a fraction of 1
        // or more would be a wrap nobody asked for.
        //
        // The speed band is the row's whole timing claim: +/-10% on every clip
        // the player drives, idle and attack and hurt and death alike
        // (AnimationPlayer.SpeedScale is a global multiplier, not a per-state
        // one). A wider band would start to read as a wrong animation.
        for (var seed = -500; seed < 2000; seed++)
        {
            var (phase, speed) = DesyncFor(seed);
            Assert.InRange(phase, 0f, 0.9999999f);
            Assert.InRange(speed, 0.90f, 1.10f);
        }

        // The band's two ends are the file's own constants, so a widened band
        // is a decision rather than a diff nobody reads.
        Assert.Equal(0.90f, (float)Desync().GetField("MinSpeedScale", All)!.GetValue(null)!);
        Assert.Equal(1.10f, (float)Desync().GetField("MaxSpeedScale", All)!.GetValue(null)!);
    }

    [Fact]
    public void The_same_slot_draws_the_same_offset_every_time()
    {
        // DETERMINISM IS THE POINT OF A PURE FUNCTION HERE. A random draw
        // would do the visual job just as well and would make every [USER]
        // look unrepeatable: "the middle one is wrong" has to be a claim
        // somebody can go back and see.
        foreach (var seed in new[] { 0, 1, 7, 42, -3 })
        {
            Assert.Equal(DesyncFor(seed), DesyncFor(seed));
        }
    }

    [Fact]
    public void Two_bodies_side_by_side_are_never_the_same_body_twice()
    {
        // THE CASE THE ROW EXISTS FOR: slots 0, 1 and 2 of one slime pack.
        // The golden-ratio sequence puts ADJACENT seeds 0.382 or 0.618 of a
        // cycle apart, always -- the three-distance theorem -- so a third of
        // the cycle is a floor this cannot fall under.
        for (var seed = -200; seed < 200; seed++)
        {
            var (a, _) = DesyncFor(seed);
            var (b, _) = DesyncFor(seed + 1);
            Assert.True(Math.Abs(a - b) > 0.33f, $"seeds {seed}/{seed + 1}: {a} vs {b}");
        }

        // AND NO TWO OF EIGHT ARE CLOSE, which a uniform hash could not
        // promise: eight uniform draws land a pair within a fiftieth of each
        // other about as often as not, and two slimes a fiftieth of a cycle
        // apart are two slimes in lockstep. Measured floor 0.090.
        foreach (var start in new[] { -4, 0, 1, 100 })
        {
            var window = Enumerable.Range(start, 8)
                .Select(s => DesyncFor(s).Phase).ToList();
            for (var i = 0; i < window.Count; i++)
            {
                for (var j = i + 1; j < window.Count; j++)
                {
                    Assert.True(Math.Abs(window[i] - window[j]) > 0.08f,
                        $"{start}: slots {i}/{j} at {window[i]} / {window[j]}");
                }
            }
        }
    }

    [Fact]
    public void Eight_bodies_cover_most_of_the_cycle_rather_than_one_corner_of_it()
    {
        // A fight tops out at a handful of bodies, so the distribution that
        // matters is the one over the FIRST FEW seeds, not the asymptotic one.
        // Eight slots have to land spread across the cycle; all eight in the
        // first third would still read as a group.
        var phases = Enumerable.Range(0, 8).Select(s => DesyncFor(s).Phase).ToList();
        Assert.True(phases.Max() - phases.Min() > 0.60f,
            $"span {phases.Max() - phases.Min()}: {string.Join(", ", phases)}");

        // Speeds too: eight bodies must not all be fast or all be slow.
        var speeds = Enumerable.Range(0, 8).Select(s => DesyncFor(s).Speed).ToList();
        Assert.Contains(speeds, s => s < 1.0f);
        Assert.Contains(speeds, s => s > 1.0f);

        // AND PHASE AND SPEED ARE INDEPENDENT DRAWS. If they moved together
        // the slowest body would always be the least advanced one, which is a
        // pattern an eye finds.
        Assert.NotEqual(phases.IndexOf(phases.Max()), speeds.IndexOf(speeds.Max()));
    }

    [Fact]
    public void The_phase_is_read_in_the_clips_own_seconds()
    {
        // Half of a 2 s bounce idle is one second in; the same fraction of the
        // Everlasting Lord's 12 s halo is six. The function never knows either
        // number -- that is why it returns a fraction.
        Assert.Equal(1.0f, PhaseSecondsFor(2.0f, 0.5f));
        Assert.Equal(6.0f, PhaseSecondsFor(12.0f, 0.5f));
        Assert.Equal(0f, PhaseSecondsFor(3.0f, 0f));

        // A clip that could not be measured gets NO advance rather than a
        // guessed one -- the same discipline the death seams keep.
        Assert.Equal(0f, PhaseSecondsFor(0f, 0.9f));
        Assert.Equal(0f, PhaseSecondsFor(-1f, 0.9f));
    }

    [Fact]
    public void The_desync_is_shut_unless_the_arm_is_on_and_the_scene_is_ours()
    {
        const string ours = "res://teyvat/creature_visuals/anemo_slime.tscn";

        Assert.True(DesyncCovers(armEnabled: true, visualsScene: ours));

        // ARM OFF IS THE ACCEPTANCE CONDITION, exactly as it is for the death
        // seam: every calibration deploy and every release package ships
        // TeyvatFrame.Enabled false, and on that side no node is touched at
        // all -- base enemies, the three player bodies and Furina's performers
        // are what they are today.
        Assert.False(DesyncCovers(armEnabled: false, visualsScene: ours));

        // An UNDRESSED enemy with the arm on: the registry has no row for it.
        Assert.False(DesyncCovers(armEnabled: true, visualsScene: null));

        // A scene outside our namespace is not ours to offset.
        Assert.False(DesyncCovers(
            armEnabled: true,
            visualsScene: "res://scenes/creature_visuals/nibbit.tscn"));

        // The gate reads the death seam's OWN constant, so the two cannot
        // drift apart.
        var root = (string)Seam().GetField("TeyvatVisualsRoot", All)!.GetValue(null)!;
        Assert.Equal("res://teyvat/creature_visuals/", root);
        Assert.False(DesyncCovers(armEnabled: true, visualsScene: root.TrimEnd('/')));
    }

    [Fact]
    public void The_attach_runs_once_per_instance_off_the_routers_first_trigger()
    {
        // WHY THE ROUTER. The mod never sees a dressed body instantiated --
        // MonsterVisualsPathPatch rewrites a path STRING and BaseLib's
        // NCreatureVisualsFactory does the instantiate and the reparent -- so
        // the router's first trigger is the earliest moment both the creature
        // and its %AnimationTree are in our hands.
        //
        // STRUCTURAL PIN: calling it needs a live scene tree, which is process
        // death in this host (README, the headless boundary).
        var route = Il.Method("CreatureAnimationRouter", "Route");
        var calls = Il.CallSequence(route).ToList();
        Assert.Equal(1, calls.Count(c => c.Contains("IdleDesync") && c.Contains("Apply")));

        // ONCE PER INSTANCE, not once per trigger: the mark is a weak table
        // keyed on the node, so it dies with the body and a fight that spawns
        // forty leaves nothing behind.
        var offset = Desync().GetField("Offset", All)!;
        Assert.Equal(
            typeof(ConditionalWeakTable<NCreature, object>), offset.FieldType);

        // ABOVE THE TRIGGER LOOKUP: an unknown trigger returns early, and a
        // body that only ever heard unknown triggers would otherwise stay in
        // lockstep with its neighbours.
        var lookup = calls.FindIndex(c => c.Contains("TryGetValue"));
        var apply = calls.FindIndex(c => c.Contains("IdleDesync"));
        Assert.True(apply >= 0 && apply < lookup, $"{apply} vs {lookup}");
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
