using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Hooks;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.ValueProps;

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
///
/// WHY MORE THAN THE ATTACK (2026-10-14, [USER]'s Kaiser Crab fight: "we need
/// to make sure that the new models can flip to face the crab hand they're
/// currently fighting (Furina's at least does not)"): Furina mostly plays
/// targeted Skills and guests, and her guests' hits never pass through an
/// AttackCommand of hers, so she almost never turned and nothing turned her
/// back. A creature now also turns on any card play aimed at an enemy and on
/// a hit its own pet or guest lands, and re-faces at its player's turn start
/// and when the side it faces empties. The latest explicit aim is remembered
/// per creature and wins over the living-enemies centre until it dies, so a
/// re-face never undoes a turn the player just asked for; per creature also
/// means each co-op seat faces its own fight.
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
    /// The latest opponents each creature was explicitly aimed at. Weak keys,
    /// so a creature from a finished combat holds nothing alive.
    /// </summary>
    private static readonly ConditionalWeakTable<Creature, Creature[]> LastAimed = new();

    /// <summary>
    /// Point <paramref name="attacker"/> at the mean position of its targets
    /// and remember them as its explicit aim. Inert for any creature whose
    /// visuals carry no %Facing node.
    /// </summary>
    public static void FaceToward(Creature? attacker, IEnumerable<Creature>? targets)
    {
        if (attacker == null || targets == null)
        {
            return;
        }

        // Only an opponent is something to face: a self-target or an ally
        // (a heal, a Block on a teammate) is not where the fight is.
        var aimed = targets
            .Where(target => target != null && target != attacker
                          && target.Side != attacker.Side && target.IsAlive)
            .ToArray();
        if (aimed.Length == 0)
        {
            return;
        }

        LastAimed.AddOrUpdate(attacker, aimed);
        if (Resolve(attacker) is not { } resolved)
        {
            return;
        }
        var (room, selfX, facing) = resolved;

        Apply(facing, DecideSign(selfX, CurrentSign(facing),
            XsOf(room, aimed), Array.Empty<float>(), onlyIfFacedSideEmpty: false));
    }

    /// <summary>
    /// Re-face <paramref name="creature"/> without a new aim: toward its last
    /// explicit aim while that lives, else toward the centre of its living
    /// opponents. With <paramref name="onlyIfFacedSideEmpty"/> (a death), a
    /// creature that still has a living opponent on the side it faces stays
    /// put, so one kill in a crowd does not swing it about.
    /// </summary>
    public static void Refresh(Creature? creature, bool onlyIfFacedSideEmpty)
    {
        if (creature == null || creature.IsDead || creature.CombatState is not { } combat)
        {
            return;
        }

        if (Resolve(creature) is not { } resolved)
        {
            return;
        }
        var (room, selfX, facing) = resolved;

        var aimed = LastAimed.TryGetValue(creature, out var last)
            ? last.Where(target => target.IsAlive && target.CombatState == combat).ToArray()
            : Array.Empty<Creature>();
        var opponents = combat.GetOpponentsOf(creature).Where(target => target.IsAlive);
        Apply(facing, DecideSign(selfX, CurrentSign(facing),
            XsOf(room, aimed), XsOf(room, opponents), onlyIfFacedSideEmpty));
    }

    /// <summary>Re-face every player creature in the fight: a death can empty
    /// the side any of them faces.</summary>
    public static void RefreshPlayers(ICombatState? combat, bool onlyIfFacedSideEmpty)
    {
        if (combat == null)
        {
            return;
        }

        foreach (var creature in combat.PlayerCreatures.ToList())
        {
            Refresh(creature, onlyIfFacedSideEmpty);
        }
    }

    /// <summary>
    /// The pure decision: the sign to take, or null to stay as is. A live
    /// explicit aim wins; with none, the centre of the living opponents. The
    /// MEAN, not the first: a fully-centered encounter is exactly where an AoE
    /// can span both sides, and picking targets[0] there would make the turn
    /// depend on iteration order rather than on where the damage is going.
    /// </summary>
    internal static float? DecideSign(float selfX, float currentSign,
        IReadOnlyList<float> aimedXs, IReadOnlyList<float> opponentXs,
        bool onlyIfFacedSideEmpty)
    {
        IReadOnlyList<float> toward;
        if (aimedXs.Count > 0)
        {
            toward = aimedXs;
        }
        else
        {
            if (opponentXs.Count == 0)
            {
                return null;
            }

            if (onlyIfFacedSideEmpty
                && opponentXs.Any(x => (x - selfX) * currentSign >= DeadZonePx))
            {
                return null;
            }

            toward = opponentXs;
        }

        float delta = toward.Average() - selfX;
        if (Mathf.Abs(delta) < DeadZonePx)
        {
            return null;
        }

        return delta < 0f ? -AuthoredFacing : AuthoredFacing;
    }

    private static (NCombatRoom Room, float SelfX, Node2D Facing)? Resolve(Creature creature)
    {
        if (NCombatRoom.Instance is not { } room)
        {
            return null;
        }

        var node = room.GetCreatureNode(creature);
        if (node?.Visuals is not { } visuals
            || !GodotObject.IsInstanceValid(visuals))
        {
            return null;
        }

        var facing = visuals.GetNodeOrNull<Node2D>("%Facing");
        return facing == null ? null : (room, node.GlobalPosition.X, facing);
    }

    private static float[] XsOf(NCombatRoom room, IEnumerable<Creature> creatures)
        => creatures
            .Select(target => room.GetCreatureNode(target))
            .Where(node => node != null && GodotObject.IsInstanceValid(node))
            .Select(node => node!.GlobalPosition.X)
            .ToArray();

    private static float CurrentSign(Node2D facing)
        => facing.Scale.X < 0f ? -AuthoredFacing : AuthoredFacing;

    private static void Apply(Node2D facing, float? sign)
    {
        if (sign is not { } s || Mathf.IsEqualApprox(facing.Scale.X, s))
        {
            return;
        }

        facing.Scale = new Vector2(s, facing.Scale.Y);
    }

    /// <summary>
    /// Whose model a hit should turn: its dealer's owner when the dealer is a
    /// pet, else the seat of an open pet scope (a Furina guest's act, a
    /// Bake-Kurage hit: those pass dealer null and name their seat only
    /// through <see cref="Diagnostics.DamageCredit"/>). Null for every other
    /// hit; a player's own hits are already turned at the card or the attack.
    /// </summary>
    internal static Creature? PetHitOwner(Creature? dealer)
    {
        if (dealer?.PetOwner?.Creature is { } owner)
        {
            return owner;
        }

        var frame = Diagnostics.DamageCredit.Current;
        return frame?.Kind == Diagnostics.DamageCredit.Pet ? frame.Owner?.Creature : null;
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
    {
        var targets = CreatureFacing.TargetsOf(__instance)?.ToList();
        CreatureFacing.FaceToward(__instance.Attacker, targets);
        // A pet's attack turns its owner too (Osty's base owner carries no
        // %Facing and stays inert).
        CreatureFacing.FaceToward(__instance.Attacker?.PetOwner?.Creature, targets);
    }
}

/// <summary>
/// Turn on ANY card play aimed at an enemy: a Skill or a Power runs no
/// AttackCommand. A prefix on the hook, so the turn lands before every
/// listener and before <see cref="CardPlayMotion"/>'s cast clip (chained after
/// the hook). An untargeted play leaves the facing alone. Base cards count
/// too: their owner turns only if its model carries %Facing.
/// </summary>
[HarmonyPatch(typeof(Hook), nameof(Hook.BeforeCardPlayed))]
internal static class Hook_BeforeCardPlayed_Facing
{
    [HarmonyPrefix]
    public static void Prefix(CardPlay cardPlay)
    {
        if (cardPlay?.Target is not { } target) return;
        CreatureFacing.FaceToward(cardPlay.Card?.Owner?.Creature, new[] { target });
    }
}

/// <summary>
/// Turn toward a hit a pet or guest of ours lands. Every Damage overload
/// funnels into this one. A hit is the only signal a guest's act gives, so the
/// owner turns at impact; she does not lunge, so impact is not too late here
/// as it is for an attack.
/// </summary>
[HarmonyPatch(typeof(CreatureCmd), nameof(CreatureCmd.Damage), new[]
{
    typeof(PlayerChoiceContext), typeof(IEnumerable<Creature>), typeof(decimal),
    typeof(ValueProp), typeof(Creature), typeof(CardModel), typeof(CardPlay),
})]
internal static class CreatureCmd_Damage_Facing
{
    [HarmonyPrefix]
    public static void Prefix(IEnumerable<Creature>? targets, Creature? dealer)
    {
        if (targets == null) return;
        try
        {
            if (CreatureFacing.PetHitOwner(dealer) is { } owner)
            {
                CreatureFacing.FaceToward(owner, targets.ToList());
            }
        }
        catch (Exception)
        {
            // A turn must never cost a hit.
        }
    }
}

/// <summary>
/// An enemy died: a model facing the side it just emptied turns to the
/// living. A prefix, so the turn starts with the death animation.
/// </summary>
[HarmonyPatch(typeof(Hook), nameof(Hook.AfterDeath))]
internal static class Hook_AfterDeath_Facing
{
    [HarmonyPrefix]
    public static void Prefix(Creature creature)
    {
        if (creature == null || creature.IsPlayer) return;
        CreatureFacing.RefreshPlayers(creature.CombatState, onlyIfFacedSideEmpty: true);
    }
}

/// <summary>
/// The player's turn starts: face the last aim if it lives, else the centre
/// of the living enemies. Per player, so co-op seats re-face apart.
/// </summary>
[HarmonyPatch(typeof(Hook), nameof(Hook.AfterPlayerTurnStart))]
internal static class Hook_AfterPlayerTurnStart_Facing
{
    [HarmonyPrefix]
    public static void Prefix(Player player)
        => CreatureFacing.Refresh(player?.Creature, onlyIfFacedSideEmpty: false);
}
