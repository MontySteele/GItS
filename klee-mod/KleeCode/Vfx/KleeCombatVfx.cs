using System.Collections.Generic;
using Godot;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// Fire-and-forget per-card VFX (animation sprint 1, Track E) — the
/// GhostflameModel.SpawnVfx recipe, mirrored not copied: instantiate a small
/// PackedScene, AddChildSafely into NCombatRoom.CombatVfxContainer, position
/// at the actor, let the scene free itself. No bridge, no registry: both
/// scenes carry a method-call track that queue_free()s their root when their
/// animation ends, so cleanup is scene-contained and cannot leak even if the
/// C# side never looks at the node again. A belt-and-braces SceneTreeTimer
/// frees any straggler (e.g. a tween orphaned by a mid-flight room change).
///
/// Spam guards, per plan E2/E3: the bomb lob fires once per detonation EVENT
/// (its caller, BombPower.Detonate, is the per-event funnel — one call
/// covers the whole stack), and dodoco pops are capped at
/// <see cref="MaxConcurrentPops"/> live instances so a spark-dump turn does
/// not particle-storm the screen.
/// </summary>
public static class KleeCombatVfx
{
    private const string BombLobScene = "klee/vfx/bomb_lob.tscn";
    private const string DodocoPopScene = "klee/vfx/dodoco_pop.tscn";

    private const float LobDuration = 0.45f;
    private const float LobApexLift = 130f;
    private const int MaxConcurrentPops = 3;

    /// <summary>Live pop instances, pruned on each spawn (E3 spam guard).</summary>
    private static readonly List<Node2D> LivePops = new();

    private static bool _warnedMissingScene;

    /// <summary>
    /// Arc a bomb from the applier to the detonating enemy and burst on
    /// arrival. Damage is NOT gated on the visual — the arc is the payoff
    /// frame for the pending-damage badge, resolving alongside the numbers.
    /// </summary>
    public static void SpawnBombLob(Creature? applier, Creature target)
    {
        if (NCombatRoom.Instance is not { } room)
        {
            return;
        }

        var fromNode = room.GetCreatureNode(applier);
        var toNode = room.GetCreatureNode(target);
        if (fromNode == null || toNode == null)
        {
            return;
        }

        var vfx = Instantiate(BombLobScene, room);
        if (vfx == null)
        {
            return;
        }

        var start = fromNode.GlobalPosition + new Vector2(20f, -150f);
        var end = toNode.GlobalPosition + new Vector2(0f, -90f);
        vfx.GlobalPosition = start;

        float apexY = Mathf.Min(start.Y, end.Y) - LobApexLift;

        var horizontal = vfx.CreateTween();
        horizontal.TweenProperty(vfx, "global_position:x", end.X, LobDuration);

        var vertical = vfx.CreateTween();
        vertical.TweenProperty(vfx, "global_position:y", apexY, LobDuration * 0.5f)
            .SetTrans(Tween.TransitionType.Quad)
            .SetEase(Tween.EaseType.Out);
        vertical.TweenProperty(vfx, "global_position:y", end.Y, LobDuration * 0.5f)
            .SetTrans(Tween.TransitionType.Quad)
            .SetEase(Tween.EaseType.In);
        vertical.Finished += () =>
        {
            if (GodotObject.IsInstanceValid(vfx)
                && vfx.GetNodeOrNull<AnimationPlayer>("%AnimationPlayer") is { } anim)
            {
                anim.Play("explode");
            }
        };
    }

    /// <summary>Short pop/sparkle over the owner on a Sparks-spend event.</summary>
    public static void SpawnDodocoPop(Creature owner)
    {
        if (NCombatRoom.Instance is not { } room)
        {
            return;
        }

        LivePops.RemoveAll(pop => !GodotObject.IsInstanceValid(pop));
        if (LivePops.Count >= MaxConcurrentPops)
        {
            return;
        }

        var ownerNode = room.GetCreatureNode(owner);
        if (ownerNode == null)
        {
            return;
        }

        var vfx = Instantiate(DodocoPopScene, room);
        if (vfx == null)
        {
            return;
        }

        // Slight horizontal scatter so overlapping pops read as separate.
        float scatter = (LivePops.Count - 1) * 34f;
        vfx.GlobalPosition = ownerNode.GlobalPosition + new Vector2(38f + scatter, -190f);
        LivePops.Add(vfx);
        // The scene autoplays "pop" and frees itself from a method track.
    }

    private static Node2D? Instantiate(string relativePath, NCombatRoom room)
    {
        string? scenePath = KleePck.Path(relativePath);
        if (scenePath == null)
        {
            if (!_warnedMissingScene)
            {
                _warnedMissingScene = true;
                MegaCrit.Sts2.Core.Logging.Log.Warn(
                    $"[{KleeMod.ModId}] {relativePath} missing from pck; "
                    + "per-card VFX disabled");
            }
            return null;
        }

        var vfx = ResourceLoader
            .Load<PackedScene>(scenePath)
            .Instantiate<Node2D>();
        room.CombatVfxContainer.AddChildSafely(vfx);

        // Leak guard (plan E4): the scene's own method track is the normal
        // cleanup; this timer only catches a node whose animation never ran.
        vfx.GetTree().CreateTimer(4.0).Timeout += () =>
        {
            if (GodotObject.IsInstanceValid(vfx))
            {
                vfx.QueueFree();
            }
        };

        return vfx;
    }
}
