using System.Collections.Generic;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Nodes.Combat;

namespace KleeMod.Vfx;

/// <summary>
/// Routes the game's creature animation triggers into an AnimationTree that
/// lives INSIDE a convention combat scene (animation sprint 1, Track A
/// plumbing; Track B ships the first tree).
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
internal static class KleeAnimationRouter
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
        => KleeAnimationRouter.Route(__instance, trigger);
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
        => KleeAnimationRouter.Route(__instance, "Dead");
}
