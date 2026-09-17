using System;
using System.Runtime.CompilerServices;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Nodes.Combat;

namespace KleeMod.Vfx;

/// <summary>
/// `EB-797`, THE FOURTH SPINE-LESS SEAM, AND THE ONE `EB-159` LEFT OPEN.
///
/// WHAT THE BASE DOES. The private <c>NCreature.AnimDie(bool,
/// CancellationToken)</c> (0.111.0 decompile,
/// <c>Nodes.Combat/NCreature.cs:1002-1018</c>) waits
/// <c>Math.Min(GetCurrentAnimationTimeRemaining() + 0.5f, 20f)</c> before it
/// spawns <c>NMonsterDeathVfx</c> and frees the node -- and that wait sits
/// behind the SAME <c>_spineAnimator != null</c> gate that
/// <c>StartDeathAnim</c>'s SFX and clip measurement sat behind
/// (<c>:933-946</c>; `review/dispatch3/s13-engine-sockets.md` row "No animator,
/// at death", and `s16-animation/s16-body-base-simple-player-character.md`
/// §Q5). <c>ModdedPlayerDeathSeam</c> repaired the RETURNED length, which is
/// what <c>Hook.AfterDeath</c> waits on (<c>Commands/CreatureCmd.cs:513</c>);
/// the engine's own internal wait was reported as still open in that file's
/// "STILL OPEN" paragraph and in PR #582. This is that row.
///
/// WHAT THIS DOES, AND WHAT IT DELIBERATELY DOES NOT. It is a POSTFIX on
/// <c>NCreature.GetCurrentAnimationTimeRemaining</c> -- the one input
/// <c>AnimDie</c>'s wait is computed from -- that substitutes the body's own
/// death-clip remaining. Nothing here transpiles <c>AnimDie</c>, re-implements
/// its wait, or touches the removal path: the arithmetic, the <c>+ 0.5f</c>
/// pad and the 20 s ceiling all stay the engine's.
///
/// `GetCurrentAnimationTimeRemaining` HAS OTHER CALLERS, so the answer is
/// changed on the DEATH PATH ONLY, and the path is proved four ways at once
/// (<see cref="Covers"/>): this creature's death was started by the seam that
/// already covers it (<see cref="NoteDeathStarted"/> is called from
/// <c>ModdedPlayerDeathSeam.Cover</c>'s two covered branches and nowhere
/// else), the body is spine-less, the base answered nothing, and the body's
/// %AnimationTree is standing in its "death" state right now. Any other
/// caller, any other creature and any other moment reads the base's own
/// answer, byte for byte.
///
/// SCOPE IS THE EXISTING SEAM'S SCOPE, EXACTLY. Modded players, and dressed
/// Teyvat bodies under the <c>TeyvatFrame</c> arm. It cannot be wider, because
/// the mark is only ever set by the branches of <c>ModdedPlayerDeathSeam.Cover</c>
/// that already covered the body -- so R213's freeze on base-enemy behaviour is
/// kept by construction, and with the arm OFF no enemy is ever marked and this
/// file's postfix returns its argument.
///
/// WHAT A DEPLOY STILL HAS TO PROVE, and it is written here rather than
/// claimed: whether the engine's gate lets the wait run at all for a
/// spine-less body on THIS install. BaseLib 3.4.7 ships an async transpiler on
/// <c>AnimDie</c> (`review/dispatch3/s16-animation/s16-sidecar-public-mods.md`
/// §4.1, <c>BaseLib@4a97642:Patches/UI/CustomAnimationPatch.cs:30-47</c>) whose
/// death-wait name probe is <c>Dead</c> / <c>Die</c> / <c>die</c> -- and our
/// scenes name the state <c>death</c>, which is not in that list (§4.2). So the
/// wait's gate is the deploy's question; what this row owns is that when the
/// wait DOES run it is handed the body's real remaining instead of a zero.
/// </summary>
internal static class ModdedDeathWaitSeam
{
    /// <summary><c>AnimDie</c>'s own ceiling on the wait
    /// (<c>NCreature.cs:1006-1010</c>, <c>Math.Min(x + 0.5f, 20f)</c>). Kept
    /// rather than re-argued, and applied here only so a nonsense clip length
    /// can never become a twenty-second stall on some other path.</summary>
    internal const float MaxDeathWait = 20f;

    /// <summary>The death state's name in our convention combat scenes -- the
    /// state <c>CreatureAnimationRouter</c>'s "Dead" route travels to, and the
    /// clip <c>ModdedPlayerDeathSeam</c> measures.</summary>
    internal const string DeathStateName = ModdedPlayerDeathSeam.DeathClipName;

    /// <summary>The unique %AnimationTree the router drives, same lookup.</summary>
    internal const string AnimationTreePath = "%AnimationTree";

    /// <summary>The playback parameter an <c>AnimationNodeStateMachine</c>
    /// exposes, same spelling <c>CreatureAnimationRouter.Route</c> reads.</summary>
    internal const string PlaybackParameter = "parameters/playback";

    /// <summary>
    /// WHOSE DEATH IS IN FLIGHT. A weak table rather than a set of ids: the
    /// key is the node itself and the entry disappears with it, so a fight
    /// that kills forty bodies leaves nothing behind and no freed node is ever
    /// looked up.
    /// </summary>
    private static readonly ConditionalWeakTable<NCreature, object> Dying = new();

    private static readonly object Mark = new();

    /// <summary>
    /// Called by <c>ModdedPlayerDeathSeam.Cover</c> from the two branches that
    /// covered the body, with the clip it measured. A body with NO clip is not
    /// marked: there is nothing for the engine to wait for, and an unmarked
    /// body reads the base's own answer everywhere.
    /// </summary>
    internal static void NoteDeathStarted(NCreature creature, float clipLength)
    {
        if (creature == null || clipLength <= 0f)
        {
            return;
        }

        Dying.Remove(creature);
        Dying.Add(creature, Mark);
    }

    /// <summary>Drop the mark. The revive door calls it, so a body that came
    /// back cannot be read as mid-death by anything later in the fight.</summary>
    internal static void Forget(NCreature creature)
    {
        if (creature != null)
        {
            Dying.Remove(creature);
        }
    }

    internal static bool IsDying(NCreature creature)
        => creature != null && Dying.TryGetValue(creature, out _);

    /// <summary>
    /// Does this reading of the remaining time belong to a death this seam
    /// owns? Pure, so it is the part a headless test can hold -- the four
    /// conditions in one place: the death path, a spine-less body (the base's
    /// gate was false), a base answer that measured nothing (so a real spine
    /// remaining is never overwritten), and a tree actually standing in the
    /// death state.
    /// </summary>
    internal static bool Covers(
        bool deathInFlight, bool hasSpineAnimation, float baseRemaining,
        string? currentState)
        => deathInFlight
            && !hasSpineAnimation
            && baseRemaining <= 0f
            && string.Equals(currentState, DeathStateName, StringComparison.Ordinal);

    /// <summary>
    /// What is left of the death clip, given its length and how far the tree
    /// has played it. Pure, for the same reason.
    ///
    /// A clip that cannot be measured, and a clip already finished, both hand
    /// back the BASE's own answer rather than a number of this file's
    /// invention: past the end there is nothing left to wait for, and the
    /// quietest thing to do with a body this pass cannot measure is nothing.
    /// The engine adds its own <c>+ 0.5f</c> pad and its own ceiling on top.
    /// </summary>
    internal static float RemainingFor(
        float clipLength, float playPosition, float baseRemaining)
    {
        if (clipLength <= 0f)
        {
            return baseRemaining;
        }

        var left = clipLength - MathF.Max(playPosition, 0f);
        return left <= 0f ? baseRemaining : MathF.Min(left, MaxDeathWait);
    }

    /// <summary>
    /// The seam itself. Returns <paramref name="baseRemaining"/> untouched for
    /// every creature, caller and moment this does not cover.
    /// </summary>
    internal static float Cover(NCreature creature, float baseRemaining)
    {
        if (creature == null || !IsDying(creature))
        {
            // THE CHEAP EXIT FIRST, and it is the one every other caller of
            // `GetCurrentAnimationTimeRemaining` takes: no mark, no lookup, no
            // change to the answer.
            return baseRemaining;
        }

        var visuals = creature.Visuals;
        if (visuals == null || !GodotObject.IsInstanceValid(visuals))
        {
            return baseRemaining;
        }

        var tree = visuals.GetNodeOrNull<AnimationTree>(AnimationTreePath);
        if (tree == null)
        {
            return baseRemaining;
        }

        if (tree.Get(PlaybackParameter).Obj is not AnimationNodeStateMachinePlayback playback)
        {
            return baseRemaining;
        }

        if (!Covers(true, creature.HasSpineAnimation, baseRemaining,
                    playback.GetCurrentNode().ToString()))
        {
            return baseRemaining;
        }

        return RemainingFor(
            (float)playback.GetCurrentLength(),
            (float)playback.GetCurrentPlayPosition(),
            baseRemaining);
    }
}

/// <summary>
/// Postfixed, like every other door this layer owns: the base answers first
/// and this substitutes only where its spine gate left a zero on a death this
/// mod is already animating.
/// </summary>
[HarmonyPatch(typeof(NCreature), "GetCurrentAnimationTimeRemaining")]
internal static class NCreature_GetCurrentAnimationTimeRemaining_DeathWaitSeam
{
    [HarmonyPostfix]
    public static void Postfix(NCreature __instance, ref float __result)
        => __result = ModdedDeathWaitSeam.Cover(__instance, __result);
}

/// <summary>
/// A body that came back is not mid-death. <c>StartReviveAnim</c> is where the
/// router already returns the tree to idle, so it is where the mark is
/// dropped -- one door, not two.
/// </summary>
[HarmonyPatch(typeof(NCreature), nameof(NCreature.StartReviveAnim))]
internal static class NCreature_StartReviveAnim_DeathWaitSeam
{
    [HarmonyPostfix]
    public static void Postfix(NCreature __instance)
        => ModdedDeathWaitSeam.Forget(__instance);
}
