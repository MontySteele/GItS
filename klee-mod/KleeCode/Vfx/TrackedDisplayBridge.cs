using System.Collections.Generic;
using Godot;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// The shared skeleton behind every creature-tracked display — the deferred
/// extraction from animation sprint 1 (D2's named cleanup, scheduled as sprint
/// 2's G1). The rule that governed the timing was "refactor after the second
/// concrete bridge SURVIVES A PLAYTEST, not before": that happened on
/// 2026-07-24, when the Salon display's styling failed its look pass but its
/// plumbing — tracking, staleness, spawn guards — held. The extraction was
/// then deliberately held until AFTER the D-track rework landed, so it covers
/// the shape that ships rather than the one that was being replaced.
///
/// What is common to <see cref="GaugeBridge"/> and
/// <see cref="SalonVisualsBridge"/>, and therefore lives here:
/// - a keyed registry of live displays with IsInstanceValid staleness, so a
///   node freed by a room teardown is never handed back;
/// - instantiate-into-CombatVfxContainer with a single loud warning per
///   missing scene (loud once, not once per frame);
/// - RemoteTransform2D tracking. The Downfall reference re-anchors from a
///   scene script's _Process every frame; our scenes are script-less AND the
///   sprint plan bans _Process polling, so the creature node drives the
///   display's global position through engine transform propagation instead.
///
/// What is NOT common, and stays in the concrete bridges: what to read, what
/// to draw, and when to animate. This is a skeleton, not a framework.
/// </summary>
internal static class TrackedDisplayBridge
{
    /// <summary>
    /// Live displays for one bridge, keyed however that bridge needs (a Player
    /// for the Salon stage, a (Player, meter) pair for gauges).
    /// </summary>
    internal sealed class Registry<TKey> where TKey : notnull
    {
        private readonly Dictionary<TKey, Node2D> _displays = new();

        /// <summary>The live display for this key, or null if absent/stale.</summary>
        public Node2D? Get(TKey key)
        {
            var display = _displays.GetValueOrDefault(key);
            if (display != null && GodotObject.IsInstanceValid(display))
            {
                return display;
            }

            _displays.Remove(key);
            return null;
        }

        public void Set(TKey key, Node2D display) => _displays[key] = display;

        public void Discard(TKey key)
        {
            if (_displays.TryGetValue(key, out var old)
                && GodotObject.IsInstanceValid(old))
            {
                old.QueueFree();
            }
            _displays.Remove(key);
        }
    }

    /// <summary>
    /// Instantiate a pck scene into the room's VFX container, or return null
    /// after warning exactly once. A missing scene degrades to "no display"
    /// rather than throwing — the visual layer never takes the run down.
    /// </summary>
    public static Node2D? Spawn(
        NCombatRoom combatRoom, string relativePath, ref bool warned,
        string disabledMessage)
    {
        string? scenePath = KleePck.Path(relativePath);
        if (scenePath == null)
        {
            if (!warned)
            {
                warned = true;
                MegaCrit.Sts2.Core.Logging.Log.Warn(
                    $"[{KleeMod.ModId}] {relativePath} missing from pck; "
                    + $"{disabledMessage} (pck stale? rebuild with "
                    + "tools/build_pck.ps1)");
            }
            return null;
        }

        var display = ResourceLoader
            .Load<PackedScene>(scenePath)
            .Instantiate<Node2D>();
        combatRoom.CombatVfxContainer.AddChildSafely(display);
        return display;
    }

    /// <summary>
    /// Pin a display to a creature at a fixed offset in creature space. The
    /// RemoteTransform2D is a child of the CREATURE, so it dies with the
    /// creature's node and cannot outlive what it was tracking.
    /// </summary>
    public static void Track(
        NCombatRoom combatRoom, Creature creature, Node2D display,
        Vector2 anchorOffset)
    {
        var creatureNode = combatRoom.GetCreatureNode(creature);
        if (creatureNode == null)
        {
            return;
        }

        var anchor = new RemoteTransform2D
        {
            Position = anchorOffset,
            UpdateRotation = false,
            UpdateScale = false,
            UseGlobalCoordinates = true,
        };
        creatureNode.AddChildSafely(anchor);
        anchor.RemotePath = anchor.GetPathTo(display);
    }
}
