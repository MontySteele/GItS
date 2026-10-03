using System;
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
/// THE SCENE CONTRACT is the four states idle/attack/hurt/death (+ RESET),
/// plus three OPTIONAL ones a scene may add (motion pass, 2026-10-02):
/// <c>cast</c> (Skill plays), <c>power</c> (Power plays) and <c>idle_low</c>
/// (HP at or under 25%). Each optional state is looked up on the scene's own
/// state machine and falls back silently when absent (see
/// <see cref="SelectState"/>).
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
    /// Game trigger -> the AnimationTree states that may answer it, in order
    /// of preference. The FIRST state the scene's state machine actually has
    /// wins, so a scene opts in to a richer state by carrying it and a scene
    /// without it falls back silently -- which is how Kokomi's and Varka's
    /// scenes, or any future one, work with no code change.
    ///
    /// Cast and PowerUp have states of their own since the motion pass
    /// (2026-10-02): the base game plays a separate cast clip for both
    /// (<c>CharacterModel.AnimationStates</c>: Cast and PowerUp both map to
    /// "cast"), and our scenes may also carry a distinct "power" state. A
    /// scene with neither keeps the old attack-lunge alias. Revive returns to
    /// idle. Unknown triggers are ignored -- never forced to idle -- so a
    /// future game trigger cannot yank a mid-flight animation.
    ///
    /// THE LAST ENTRY OF EACH ROW IS THE REQUIRED CONTRACT (idle, attack,
    /// hurt, death); everything before it is optional. Literals on purpose:
    /// `tools/visual_qa/scene_deps.py` and `tools/animation_bakeoff/spec.py`
    /// copy this table and their pins parse it.
    /// </summary>
    private static readonly Dictionary<string, string[]> TriggerToStates = new()
    {
        ["Idle"] = new[] { "idle" },
        ["Revive"] = new[] { "idle" },
        ["Attack"] = new[] { "attack" },
        ["Cast"] = new[] { "cast", "attack" },
        ["PowerUp"] = new[] { "power", "cast", "attack" },
        ["Hit"] = new[] { "hurt" },
        ["Dead"] = new[] { "death" },
    };

    internal const string IdleState = "idle";
    internal const string LowHealthIdleState = "idle_low";
    internal const string CastState = "cast";
    internal const string PowerState = "power";

    /// <summary>
    /// The two AnimationTree conditions the low-HP idle hangs off. A scene
    /// that carries <see cref="LowHealthIdleState"/> wires
    /// <c>idle -> idle_low</c> on <c>low_hp</c> and <c>idle_low -> idle</c>
    /// on <c>healthy</c> (both auto, cross-faded), so every one-shot that
    /// returns to idle lands on the right one with no extra code -- the shape
    /// of the base's own <c>AddNextState(idle, !IsLowHealth)</c> /
    /// <c>AddNextState(low_health_loop, IsLowHealth)</c> pair.
    /// </summary>
    internal const string LowHealthCondition = "parameters/conditions/low_hp";
    internal const string HealthyCondition = "parameters/conditions/healthy";

    /// <summary>The base's own line: <c>CharacterModel.IsLowHealth</c> is
    /// <c>GetHpPercentRemaining() &lt;= 0.25</c>.</summary>
    internal const double LowHealthFraction = 0.25;

    /// <summary>
    /// THE ONE CONDITION for the low-HP idle, in the base's terms: current
    /// over max at or under a quarter. A creature with no max HP is never
    /// "low" (nothing to divide by).
    /// </summary>
    internal static bool IsLowHealth(int currentHp, int maxHp)
        => maxHp > 0 && (double)currentHp / maxHp <= LowHealthFraction;

    /// <summary>
    /// Which state a trigger travels to, given which states this scene has.
    /// Pure, so the whole fallback table is testable headless: null means
    /// "ignore", and the idle family resolves to the low-HP variant only when
    /// the scene carries one.
    /// </summary>
    internal static string? SelectState(
        string trigger, Func<string, bool> hasState, bool lowHealth)
    {
        if (!TriggerToStates.TryGetValue(trigger, out var candidates))
        {
            return null;
        }
        foreach (var state in candidates)
        {
            if (state == IdleState && lowHealth && hasState(LowHealthIdleState))
            {
                return LowHealthIdleState;
            }
            if (hasState(state))
            {
                return state;
            }
        }
        return null;
    }

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

        // `EB-816`. THE FIRST SIGHT OF THIS CREATURE IS THE ATTACH POINT for
        // the per-instance idle offset, and it sits ABOVE the trigger lookup
        // on purpose: an unknown trigger is ignored below, and a body that
        // only ever heard unknown triggers would otherwise stay in lockstep
        // with its neighbours. Gated on the Teyvat arm and on a dressed scene
        // inside `IdleDesync.Apply`, and marked per instance there, so this
        // is once per creature rather than once per trigger and is inert for
        // every body the arm does not cover.
        IdleDesync.Apply(creature, tree);

        var hasState = StatesOf(tree);
        var low = RefreshLowHealth(creature, tree, hasState);

        var target = SelectState(trigger, hasState, low);
        if (target == null)
        {
            return;
        }

        if (tree.Get("parameters/playback").Obj is AnimationNodeStateMachinePlayback playback)
        {
            // Travel to the current state is a no-op, so a double "Dead"
            // (StartDeathAnim re-entry) cannot restart the death animation.
            playback.Travel(target);
        }
    }

    /// <summary>
    /// What this tree's state machine carries. A tree whose root is not a
    /// state machine cannot be asked; it keeps the pre-motion-pass behaviour
    /// for the four contract states and has none of the optional ones.
    /// </summary>
    private static Func<string, bool> StatesOf(AnimationTree tree)
    {
        if (tree.TreeRoot is AnimationNodeStateMachine machine)
        {
            return state => machine.HasNode(state);
        }
        return state => state is not (CastState or PowerState or LowHealthIdleState);
    }

    /// <summary>
    /// Re-reads the creature's HP into the tree's two idle conditions, and
    /// returns whether it is low. Called on every trigger (the base also only
    /// re-asks at a state change, and a hit's "Hit" arrives after the HP has
    /// moved) and on every card play (<see cref="CardPlayMotion"/>), so a
    /// fight that starts low slumps by the first play. Writes nothing for a
    /// scene with no low-HP idle: its tree has no such parameters.
    /// </summary>
    private static bool RefreshLowHealth(
        NCreature creature, AnimationTree tree, Func<string, bool> hasState)
    {
        var entity = creature.Entity;
        var low = entity != null && entity.IsAlive
            && IsLowHealth(entity.CurrentHp, entity.MaxHp);
        if (hasState(LowHealthIdleState))
        {
            tree.Set(LowHealthCondition, low);
            tree.Set(HealthyCondition, !low);
        }
        return low;
    }

    /// <summary>The low-HP refresh from outside a trigger, for a creature
    /// node that may not carry a tree at all.</summary>
    public static void RefreshLowHealth(NCreature? creature)
    {
        if (creature == null || !GodotObject.IsInstanceValid(creature)) return;
        var visuals = creature.Visuals;
        if (visuals == null || !GodotObject.IsInstanceValid(visuals)) return;
        if (visuals.GetNodeOrNull<AnimationTree>("%AnimationTree") is not { } tree) return;
        RefreshLowHealth(creature, tree, StatesOf(tree));
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
