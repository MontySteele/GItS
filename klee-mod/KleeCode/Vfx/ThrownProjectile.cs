using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Vfx;

namespace KleeMod.Vfx;

/// <summary>
/// THE THROWN BOMB (2026-10-13). Klee's attack cells used to carry the bomb in
/// flight, baked in, so it was clipped at the cell edge a fifth of the way to
/// the enemy ("it doesn't actually reach the enemy"). The bomb is now cut out
/// of the cells (tools/klee_render/pack.py <c>split_thrown</c>) and flown by
/// the game, the way the base flies its projectiles:
/// <c>NVfxProjectileHandler.PlaySequence</c> lerps the projectile from source
/// to destination with a height curve along the path's normal, then spawns its
/// impact VFX into <c>NCombatRoom.CombatVfxContainer</c> at the destination.
///
/// THE SCENE CONTRACT: a hidden <c>%ThrownProjectile</c> Sprite2D under
/// <c>%Facing</c>, sitting where the bomb leaves her hand, with the attack
/// clip's release time as <c>metadata/release</c>. Being under %Facing, a
/// flipped Klee throws from the mirrored hand with no code here. Inert for
/// every scene without the node.
///
/// THE AIM is the attack's own: <see cref="AttackCommand_Execute_ThrownAim"/>
/// notes the command's single target before the wind-up (the same prefix
/// point <see cref="CreatureFacing"/> turns at), and the throw resolves it
/// when the clip starts, before the hit can kill. An AoE, a random-target
/// attack or an attack trigger with no command behind it aims at the centre
/// of the target side. Every client runs the attack command, so a co-op
/// partner sees the same throw.
/// </summary>
internal static class ThrownProjectile
{
    internal const string NodeName = "ThrownProjectile";
    internal const string ReleaseMeta = "release";
    internal const string AttackState = "attack";

    /// <summary>Hand to target. The base's shiv throw lands its impact
    /// 0.15 s after it spawns (<c>NShivThrowVfx.PlaySequence</c>).</summary>
    internal const float FlightSeconds = 0.15f;

    /// <summary>Apex of the arc above the straight line, in screen px.</summary>
    internal const float ArcLift = 70f;

    internal const float SpinDegrees = 360f;

    /// <summary><c>NFireBurstVfx</c> scale for the arrival pop; the base's
    /// Cinder hits at 0.75.</summary>
    internal const float PopScale = 0.4f;

    /// <summary>A noted aim older than this belongs to an attack that played
    /// no animation, not to the trigger now asking.</summary>
    private const ulong AimStaleMs = 1500;

    private sealed class Aim
    {
        public Creature? Single;
        public CombatSide Side;
        public ulong AtMs;
    }

    private static readonly ConditionalWeakTable<Creature, Aim> Pending = new();

    /// <summary>
    /// A point on the throw at <paramref name="t"/> in [0, 1]: the straight
    /// line plus a parabolic lift along the line's normal, the normal turned
    /// to point up the screen. The base's handler shape with its curves
    /// fixed. Pure.
    /// </summary>
    internal static Vector2 ArcPoint(Vector2 start, Vector2 end, float t, float lift)
    {
        var along = start.Lerp(end, t);
        var dir = end - start;
        if (dir.LengthSquared() < 1e-6f)
        {
            return along + new Vector2(0f, -lift * 4f * t * (1f - t));
        }
        dir = dir.Normalized();
        var normal = new Vector2(dir.Y, -dir.X);
        if (normal.Y > 0f)
        {
            normal = -normal;
        }
        return along + normal * (lift * 4f * t * (1f - t));
    }

    /// <summary>
    /// Where the bomb lands: the single target's centre when there is one,
    /// else the mean of the target side's centres, else nowhere. Pure.
    /// </summary>
    internal static Vector2? AimPoint(Vector2? single, IReadOnlyList<Vector2> side)
    {
        if (single.HasValue)
        {
            return single.Value;
        }
        if (side.Count == 0)
        {
            return null;
        }
        var sum = Vector2.Zero;
        foreach (var p in side)
        {
            sum += p;
        }
        return sum / side.Count;
    }

    /// <summary>
    /// Whether a travel throws: only a fresh entry into the attack clip. A
    /// second attack trigger while the clip still runs is a no-op travel and
    /// replays nothing, so it throws nothing either. Pure.
    /// </summary>
    internal static bool Throws(string? fromState, string toState)
        => toState == AttackState && fromState != AttackState;

    public static void NoteAim(AttackCommand command)
    {
        if (command.Attacker is not { } attacker)
        {
            return;
        }
        Creature? single = null;
        if (command.IsSingleTargeted && !command.IsRandomlyTargeted)
        {
            single = CreatureFacing.TargetsOf(command)?.FirstOrDefault();
        }
        Pending.AddOrUpdate(attacker, new Aim
        {
            Single = single,
            Side = command.TargetSide,
            AtMs = Time.GetTicksMsec(),
        });
    }

    /// <summary>
    /// Called by <see cref="CreatureAnimationRouter"/> as the tree enters
    /// the attack clip. Schedules the throw at the clip's release frame.
    /// </summary>
    public static void Schedule(NCreature creature, AnimationTree tree)
    {
        var visuals = creature.Visuals;
        if (visuals?.GetNodeOrNull<Sprite2D>("%" + NodeName) is not { } template
            || NCombatRoom.Instance is not { } room)
        {
            return;
        }
        var end = ResolveAim(creature, room);
        if (end == null)
        {
            return;
        }
        double release = template.HasMeta(ReleaseMeta) ? template.GetMeta(ReleaseMeta).AsDouble() : 0.0;
        var landing = end.Value;
        template.GetTree().CreateTimer(release).Timeout += () => Launch(template, tree, room, landing);
    }

    private static Vector2? ResolveAim(NCreature creature, NCombatRoom room)
    {
        var entity = creature.Entity;
        if (entity == null)
        {
            return null;
        }
        Aim? aim = null;
        if (Pending.TryGetValue(entity, out var noted))
        {
            Pending.Remove(entity);
            if (Time.GetTicksMsec() - noted.AtMs <= AimStaleMs)
            {
                aim = noted;
            }
        }

        Vector2? single = null;
        if (aim?.Single is { IsAlive: true } target
            && room.GetCreatureNode(target) is { } targetNode
            && GodotObject.IsInstanceValid(targetNode))
        {
            single = targetNode.VfxSpawnPosition;
        }
        var side = aim?.Side
            ?? (entity.Side == CombatSide.Enemy ? CombatSide.Player : CombatSide.Enemy);
        var sideCentres = room.CreatureNodes
            .Where(n => GodotObject.IsInstanceValid(n)
                        && n.Entity is { IsAlive: true } e && e.Side == side && e != entity)
            .Select(n => n.VfxSpawnPosition)
            .ToList();
        return AimPoint(single, sideCentres);
    }

    private static void Launch(Sprite2D template, AnimationTree tree, NCombatRoom room, Vector2 end)
    {
        // A hurt or a death that cut the wind-up short means no bomb left her
        // hand; a room torn down mid-wind-up has nowhere to draw one.
        if (!GodotObject.IsInstanceValid(template) || !GodotObject.IsInstanceValid(tree)
            || !GodotObject.IsInstanceValid(room) || NCombatRoom.Instance != room
            || tree.Get("parameters/playback").Obj is not AnimationNodeStateMachinePlayback playback
            || (string)playback.GetCurrentNode() != AttackState)
        {
            return;
        }

        var start = template.GlobalPosition;
        var bomb = new Sprite2D
        {
            Texture = template.Texture,
            Centered = true,
        };
        room.CombatVfxContainer.AddChildSafely(bomb);
        bomb.GlobalPosition = start;
        bomb.GlobalScale = template.GlobalScale;

        float spin = end.X >= start.X ? SpinDegrees : -SpinDegrees;
        var tween = bomb.CreateTween();
        tween.TweenMethod(Callable.From<float>(t =>
        {
            if (!GodotObject.IsInstanceValid(bomb)) return;
            bomb.GlobalPosition = ArcPoint(start, end, t, ArcLift);
            bomb.RotationDegrees = spin * t;
        }), 0f, 1f, FlightSeconds);
        tween.Finished += () =>
        {
            if (GodotObject.IsInstanceValid(room) && NCombatRoom.Instance == room
                && NFireBurstVfx.Create(end, PopScale) is { } pop)
            {
                room.CombatVfxContainer.AddChildSafely(pop);
                pop.GlobalPosition = end;
            }
            if (GodotObject.IsInstanceValid(bomb)) bomb.QueueFree();
        };

        // Leak guard: a tween orphaned by a room change never finishes.
        bomb.GetTree().CreateTimer(2.0).Timeout += () =>
        {
            if (GodotObject.IsInstanceValid(bomb)) bomb.QueueFree();
        };
    }
}

/// <summary>
/// Note the attack's aim before the wind-up, beside the facing turn
/// (<see cref="AttackCommand_Execute_Facing"/>); the throw reads it when the
/// clip starts.
/// </summary>
[HarmonyPatch(typeof(AttackCommand), nameof(AttackCommand.Execute))]
internal static class AttackCommand_Execute_ThrownAim
{
    [HarmonyPrefix]
    public static void Prefix(AttackCommand __instance)
        => ThrownProjectile.NoteAim(__instance);
}
