using System;
using System.Linq;
using Godot;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Powers;

/// <summary>
/// THE LINE, AND THE FINDING BEHIND IT.
///
/// THE QUESTION the row asked: can three pets be placed in a front/middle/back
/// line beside Furina by <c>Bounds</c> alone, or does it need a placement
/// patch? The jellyfish's header records that the engine's generic branch
/// "lays every other pet out beside its owner" and that the box's WIDTH is the
/// only dial it reads -- which reads, on one pet, as though the branch places
/// ONE pet and a second would land on top of it.
///
/// THE ANSWER, off the 0.111.0 decompile (<c>NCombatRoom</c>, both sites):
/// <b>the line is free, the ORDER and the GAP are not.</b>
///
///   * <c>PositionPlayersAndPets</c>'s generic branch already spreads N pets:
///     <c>num12 = pets.Count &gt; 1 ? player.Bounds.Size.X / (pets.Count - 1) : 0</c>,
///     then <c>pets[l].Position = (-targetX + 20 - l * num12 - petBounds.X * 0.5,
///     player.Y + 10)</c>. Three pets get three distinct X positions, spaced by
///     half the owner's box each. No patch is needed for a line to exist.
///   * <c>AddCreature</c> RE-LAYS THE WHOLE PET SET OUT on every mid-combat
///     add, by the same formula mirrored (<c>owner.X - 20 + i * num +
///     petBounds.X * 0.5</c>). So a summon during a fight re-flows the line by
///     itself, and it does so in <c>_creatureNodes</c> order, which is SPAWN
///     order.
///
/// TWO THINGS THE ENGINE THEREFORE GETS WRONG FOR THIS ARM, and both are the
/// arm's own fault rather than the engine's:
///
///   1. SPAWN ORDER IS NOT SEAT ORDER. Rule 3 rotates the cast -- the front
///      leaves, the others step forward, the newcomer takes the back seat --
///      and after one rotation the body that spawned first is no longer the
///      one in front. A player reading rule 6 ("the LEAD absorbs") off a line
///      whose order is the order the bodies happened to arrive in is reading a
///      lie, and sec.8's last failure mode is exactly this: "the panel must
///      show the lead's bar beside her Block, in the damage order".
///   2. A DEPARTURE RE-LAYS NOTHING OUT. The engine re-flows on ADD only, so a
///      lead emptied by a hit leaves a hole in the line until the next summon.
///
/// SO: A SMALL PLACEMENT PASS, AND NOT A HARMONY PATCH. This re-applies the
/// engine's own arithmetic in SEAT order after every change to the stage. It
/// patches nothing, overrides nothing and is called from one place
/// (<c>FurinaStagePets.Sync</c>), so with the arm off it does not run and a
/// board with no stage is laid out by the engine exactly as it always was.
///
/// THE LEAD IS THE RIGHT-MOST SLOT. Allies sit at negative X and the enemies'
/// container is to their right, so "toward the enemy" is +X: the front seat is
/// the one nearest the fight, which is where a player looks for the thing
/// standing between them and the intent.
///
/// DISPLAY ONLY, AND INERT WITHOUT A SCENE TREE -- the rule every bridge in
/// this mod is written to (<c>Vfx/GaugeBridge.cs</c>): it reads state and
/// writes none, every lookup is null-guarded, and the whole body is inside a
/// catch so a room that is mid-build cannot take a fight down over a
/// position.
/// </summary>
public static class FurinaStagePlacement
{
    /// <summary>The engine's own two magic numbers, lifted rather than chosen:
    /// <c>NCombatRoom.AddCreature</c> places a pet at <c>owner.X - 20</c> and
    /// <c>owner.Y + 10</c>.</summary>
    private const float OwnerXOffset = 20f;

    private const float OwnerYOffset = 10f;

    /// <summary>
    /// Lay the stage out front-to-back. A no-op with no room, no node or no
    /// stage.
    /// </summary>
    public static void Reflow(Creature? furina)
    {
        if (!FurinaStage.LiveFor(furina)) return;
        try
        {
            var room = NCombatRoom.Instance;
            if (room == null) return;
            var owner = room.GetCreatureNode(furina);
            if (owner == null) return;

            var seats = FurinaStageLedger.For(furina!).Seats;
            var nodes = seats
                .Select(seat => seat.Pet == null ? null : room.GetCreatureNode(seat.Pet))
                .ToList();
            var placed = nodes.Count(n => n != null);
            if (placed == 0) return;

            // The engine's spacing, its formula: the owner's own box width
            // divided among the gaps. One body sits in the single slot and
            // needs no step, which is the `pets.Count > 1` guard at both
            // engine sites.
            var step = placed > 1
                ? owner.Visuals.Bounds.Size.X / (placed - 1)
                : 0f;

            // Slot 0 is the LEFT-most (furthest from the enemy) and takes the
            // BACK performer, so the walk is over the seats in reverse.
            var slot = 0;
            for (var i = nodes.Count - 1; i >= 0; i--)
            {
                var node = nodes[i];
                if (node == null) continue;
                node.Position = new Vector2(
                    owner.Position.X - OwnerXOffset + slot * step
                        + node.Visuals.Bounds.Size.X * 0.5f,
                    owner.Position.Y + OwnerYOffset);
                slot++;
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] stage: placement pass skipped: {e}");
        }
    }
}
