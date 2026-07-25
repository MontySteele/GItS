using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// Turns a modded creature to face whatever it is about to attack.
///
/// WHY THIS EXISTS: the base game never mirrors a creature. Every base
/// character is a Spine skeleton whose art is drawn facing the enemy side, and
/// with the enemies always to the right that is enough — nothing in NCreature,
/// NCreatureVisuals or CreatureAnimator carries a facing/flip concept at all
/// (checked by decompile, v0.107.1). The Act 2 Kaiser Crab is the encounter
/// where that assumption breaks: it is the one boss with
/// <c>FullyCenterPlayers = true</c>, and it puts Crusher and Rocket in slots on
/// BOTH sides of the party. Attacking the left one, the whole party lunges
/// right — reported from playtest as "can't tell which way you're facing".
///
/// So this is a gap we fill rather than a signal we forgot to consume. It is
/// scoped by construction: the mirror is applied to a %Facing node that only
/// our own convention combat scenes carry, so every base creature — and every
/// other mod's — is untouched and the lookup simply returns null.
///
/// WHY %Facing AND NOT %Rig: the rig is animated. `Visuals/Facing/Rig:position`
/// carries the attack lunge, and a node's own position track is expressed in
/// its PARENT's space, so mirroring the rig itself would flip the art while
/// leaving the lunge travelling right — a moonwalk. The mirror therefore sits
/// on a parent of the animated node, where it mirrors the travel too. Nothing
/// animates %Facing, so the two never fight.
///
/// WHY NOT Visuals.Scale: NCreature owns that one — ScaleTo, SetDefaultScaleTo
/// and OstyScaleToSize all write it, and UpdateBounds reads it back to place
/// the hitbox and the intent. A sign flip there would invert the hitbox.
/// </summary>
internal static class CreatureFacing
{
    /// <summary>
    /// The rigs are authored facing right, which is where the enemies are in
    /// every encounter except the centered ones.
    /// </summary>
    private const float AuthoredFacing = 1f;

    /// <summary>
    /// Below this, "left" and "right" are not a meaningful distinction and
    /// flipping would just be noise — a self-target, or an attacker standing
    /// on top of its target.
    /// </summary>
    private const float DeadZonePx = 24f;

    /// <summary>
    /// AttackCommand's target list is private and there is no public
    /// equivalent (Results is empty until after the hits land). Reflection is
    /// the honest cost of turning BEFORE the wind-up instead of at impact —
    /// see the patch below for why impact is too late. Cached once; a null
    /// here degrades to no facing rather than to an exception.
    /// </summary>
    private static readonly MethodInfo? PossibleTargets =
        AccessTools.Method(typeof(AttackCommand), "GetPossibleTargets");

    private static bool _warnedNoTargetAccessor;

    /// <summary>
    /// Point <paramref name="attacker"/> at the mean position of its targets.
    /// Inert for any creature whose visuals carry no %Facing node.
    /// </summary>
    public static void FaceToward(Creature? attacker, IEnumerable<Creature>? targets)
    {
        if (attacker == null || targets == null)
        {
            return;
        }

        if (NCombatRoom.Instance is not { } room)
        {
            return;
        }

        var attackerNode = room.GetCreatureNode(attacker);
        if (attackerNode?.Visuals is not { } visuals
            || !GodotObject.IsInstanceValid(visuals))
        {
            return;
        }

        var facing = visuals.GetNodeOrNull<Node2D>("%Facing");
        if (facing == null)
        {
            return;
        }

        var targetXs = targets
            .Where(target => target != attacker && target.IsAlive)
            .Select(target => room.GetCreatureNode(target))
            .Where(node => node != null && GodotObject.IsInstanceValid(node))
            .Select(node => node!.GlobalPosition.X)
            .ToList();
        if (targetXs.Count == 0)
        {
            return;
        }

        // The MEAN, not the first: a fully-centered encounter is exactly where
        // an AoE can span both sides, and picking targets[0] there would make
        // the turn depend on iteration order rather than on where the damage
        // is going.
        float delta = targetXs.Average() - attackerNode.GlobalPosition.X;
        if (Mathf.Abs(delta) < DeadZonePx)
        {
            return;
        }

        float sign = delta < 0f ? -AuthoredFacing : AuthoredFacing;
        if (Mathf.IsEqualApprox(facing.Scale.X, sign))
        {
            return;
        }

        facing.Scale = new Vector2(sign, facing.Scale.Y);
    }

    /// <summary>
    /// Read an AttackCommand's targets without throwing. Execute itself
    /// validates that targets were set; this runs before that validation, so a
    /// half-built command is a normal state here, not an error.
    /// </summary>
    public static IEnumerable<Creature>? TargetsOf(AttackCommand command)
    {
        if (PossibleTargets == null)
        {
            if (!_warnedNoTargetAccessor)
            {
                _warnedNoTargetAccessor = true;
                Log.Warn($"[{KleeMod.ModId}] AttackCommand.GetPossibleTargets is gone "
                       + "(game update?); modded creatures will not turn to face "
                       + "their target. Harmless — everything else is unaffected.");
            }
            return null;
        }

        try
        {
            return PossibleTargets.Invoke(command, null) as IEnumerable<Creature>;
        }
        catch (Exception)
        {
            return null;
        }
    }
}

/// <summary>
/// Turn at the START of the attack, not when the damage lands.
///
/// AttackCommand.Execute awaits CreatureCmd.TriggerAnim before it deals any
/// damage, so hooking the damage funnel (CreatureCmd.Damage, which every
/// overload does funnel into) would flip the sprite at the moment of impact —
/// after the character had already lunged the wrong way. Prefixing Execute
/// puts the turn ahead of the wind-up, which is where a turn reads as
/// intention rather than as a glitch.
/// </summary>
[HarmonyPatch(typeof(AttackCommand), nameof(AttackCommand.Execute))]
internal static class AttackCommand_Execute_Facing
{
    [HarmonyPrefix]
    public static void Prefix(AttackCommand __instance)
        => CreatureFacing.FaceToward(
            __instance.Attacker, CreatureFacing.TargetsOf(__instance));
}
