using System.Collections.Generic;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Nodes.Combat;

namespace KleeMod.Vfx;

/// <summary>
/// Routes the game's creature animation triggers into an AnimationTree that
/// lives INSIDE a convention combat scene.
///
/// SCOPE: this serves EVERY modded creature whose visuals carry an
/// %AnimationTree — it has never been Klee-specific, and it was renamed from
/// KleeAnimationRouter in animation sprint 2 (G2) once Furina's rig became the
/// second one it drives with zero code changes. Nothing here knows or cares
/// which character it is routing for; a third character needs only a scene.
/// (Introduced as animation sprint 1 Track A plumbing; Track B shipped the
/// first tree.)
///
/// Why a Harmony postfix pair and not a scene script: the game only animates
/// through <c>_spineAnimator</c>, which NCreature builds solely when
/// <c>Visuals.HasSpineAnimation</c> — for spine-less visuals,
/// <c>SetAnimationTrigger</c> is <c>_spineAnimator?.SetTrigger(...)</c>, a
/// guaranteed no-op. Downfall proves this exact patch shape in production
/// (their NCreature postfixes; pattern mirrored, not copied). Our scenes are
/// script-less by pipeline rule (see pck-src/README.md), so the routing target
/// is found by node lookup instead of an interface on a scene script.
///
/// Inert by construction for every creature whose visuals carry no
/// %AnimationTree — which today is everything, including the static Track-A
/// Klee scene. The lookup is per-trigger, not per-frame: triggers fire a
/// handful of times per action, so there is nothing to cache and no
/// staleness class to manage.
/// </summary>
internal static class CreatureAnimationRouter
{
    /// <summary>
    /// Game trigger -> AnimationTree state. The scene contract is exactly the
    /// four states idle/attack/hurt/death (+ RESET), per the sprint plan (B2).
    /// Cast and PowerUp share the attack lunge until the [USER] look pass says
    /// otherwise; Revive returns to idle. Unknown triggers are ignored —
    /// never forced to idle — so a future game trigger cannot yank a
    /// mid-flight animation.
    /// </summary>
    private static readonly Dictionary<string, string> TriggerToState = new()
    {
        ["Idle"] = "idle",
        ["Revive"] = "idle",
        ["Attack"] = "attack",
        ["Cast"] = "attack",
        ["PowerUp"] = "attack",
        ["Hit"] = "hurt",
        ["Dead"] = "death",
    };

    public static void Route(NCreature creature, string trigger)
    {
        var visuals = creature.Visuals;
        if (visuals == null || !GodotObject.IsInstanceValid(visuals))
        {
            return;
        }

        var tree = visuals.GetNodeOrNull<AnimationTree>("%AnimationTree");
        if (tree == null)
        {
            return;
        }

        if (!TriggerToState.TryGetValue(trigger, out var state))
        {
            return;
        }

        if (tree.Get("parameters/playback").Obj is AnimationNodeStateMachinePlayback playback)
        {
            // Travel to the current state is a no-op, so a double "Dead"
            // (StartDeathAnim re-entry) cannot restart the death animation.
            playback.Travel(state);
        }
    }
}

[HarmonyPatch(typeof(NCreature), nameof(NCreature.SetAnimationTrigger))]
internal static class NCreature_SetAnimationTrigger_AnimationTreeRoute
{
    [HarmonyPostfix]
    public static void Postfix(NCreature __instance, string trigger)
        => CreatureAnimationRouter.Route(__instance, trigger);
}

/// <summary>
/// Death is special-cased upstream: StartDeathAnim only emits the "Dead"
/// trigger when a spine animator exists, so spine-less visuals would never
/// hear about death through SetAnimationTrigger alone.
/// </summary>
[HarmonyPatch(typeof(NCreature), nameof(NCreature.StartDeathAnim))]
internal static class NCreature_StartDeathAnim_AnimationTreeRoute
{
    [HarmonyPostfix]
    public static void Postfix(NCreature __instance)
        => CreatureAnimationRouter.Route(__instance, "Dead");
}

/// <summary>
/// `EB-159`, THE ONE SEAM OF THE THREE THAT BITES A MODDED PLAYER TODAY.
///
/// REVIVE IS SPECIAL-CASED UPSTREAM THE SAME WAY DEATH IS, and one step
/// further. <c>NCreature.StartReviveAnim</c> emits the "Revive" trigger only
/// when <c>_spineAnimator != null</c> and that animator has the trigger
/// (0.111.0 decompile, <c>Nodes.Combat/NCreature.cs:971</c>), and every
/// character of ours is spine-less -- so the postfix above never hears about a
/// revive. The arm a spine-less PLAYER takes instead is
/// <c>else if (Entity.IsPlayer) AnimTempRevive()</c> (NCreature.cs:987), a
/// tween that fades <c>Visuals</c> out and back and, between the two, calls
/// <c>ImmediatelySetIdle</c> (NCreature.cs:997) -- which sets the trigger on
/// <c>_spineAnimator</c> DIRECTLY rather than through
/// <c>SetAnimationTrigger</c>, so it bypasses the router's other postfix too.
///
/// WHAT THAT COSTS, concretely. The state machine was driven to "death" by
/// <c>StartDeathAnim</c>'s postfix, the player is brought back
/// (<c>CreatureCmd.Heal</c>'s <c>wasDead</c> arm, CreatureCmd.cs:775;
/// <c>SetCurrentHp</c> dead-to-alive, CreatureCmd.cs:827), and nothing ever
/// tells the tree to leave that state: the character stands back up as her own
/// corpse, faded to full alpha by the tween. Furina's graph has no
/// death-to-idle transition at all (`pck-src/furina/model/combat.tscn`: death
/// goes only to End), which is survivable -- Godot's <c>Travel</c> teleports
/// where no path exists -- and is also why nothing recovers on its own.
///
/// SO IT IS ROUTED HERE, in the shape the death seam already uses, and it
/// carries the game's own word: <c>TriggerToState</c> maps "Revive" to idle,
/// which is what a base-game spine rig does with the trigger and what
/// <c>ImmediatelySetIdle</c> does with the animator. Inert for every creature
/// with no %AnimationTree, which is the whole base cast.
///
/// THE OTHER TWO SEAMS ARE CLOSED TOO, NOW. <c>ImmediatelySetIdle</c> is
/// reachable only through this same tween in the 0.111.0 decompile, so this
/// postfix covers it. <c>StartDeathAnim</c>'s own <c>_spineAnimator != null</c>
/// gate (NCreature.cs:944) also skips <c>SfxCmd.PlayDeath(Entity.Player)</c> and
/// leaves the returned anim length at 0, so a modded player died silently and
/// <c>Hook.AfterDeath</c> waited zero seconds for an animation the tree was
/// playing; that SOUND and that WAIT are filled in beside this file by
/// <see cref="ModdedPlayerDeathSeam"/>, which is the row's remaining third.
/// </summary>
[HarmonyPatch(typeof(NCreature), nameof(NCreature.StartReviveAnim))]
internal static class NCreature_StartReviveAnim_AnimationTreeRoute
{
    [HarmonyPostfix]
    public static void Postfix(NCreature __instance)
        => CreatureAnimationRouter.Route(__instance, "Revive");
}
