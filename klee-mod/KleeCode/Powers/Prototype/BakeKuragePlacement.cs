using System;
using System.Collections.Generic;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Powers;

/// <summary>
/// WHERE THE BAKE-KURAGE STANDS, on any character (backlog wave 3,
/// 2026-10-19; frame `frame-20261019-152138-defect-kurage-plan.png`).
///
/// THE FIND. On the Defect the jellyfish sat on the front leg, over the
/// body. Off Kokomi it is summoned mid-combat (a Plan card drawn or played),
/// and <c>NCombatRoom.AddCreature</c> lays a mid-combat pet at
/// <c>owner.X - 20 + petHalfWidth</c>: 40 px from the owner's centre, inside
/// any body wider than that. The combat-start layout
/// (<c>PositionPlayersAndPets</c>) happened to clear Kokomi's wide box.
///
/// THE RULE is Furina's stage line's (<see cref="FurinaStagePlacement"/>),
/// one body long: from the owner's hitbox EDGE, one
/// <see cref="FurinaStagePlacement.Gap"/> of floor, then the jellyfish's own
/// half-width. So it stands clear in front of whoever owns it, whatever their
/// size. Applied after both engine layouts, display only, and never thrown
/// out of.
/// </summary>
public static class BakeKuragePlacement
{
    /// <summary>The engine's pet Y offset (<c>owner.Y + 10</c>).</summary>
    private const float OwnerYOffset = 10f;

    /// <summary>The jellyfish's centre X: clear of the owner's hitbox, on
    /// the enemy side. PURE, so the headless suite can hold it.</summary>
    public static float Centre(float ownerX, float ownerHalfWidth,
                               float kurageWidth) =>
        FurinaStagePlacement.LineCentres(
            ownerX, ownerHalfWidth, new[] { kurageWidth })[0];

    /// <summary>Stand this owner's jellyfish clear of them. A no-op with no
    /// room, no jellyfish or no node.</summary>
    public static void Place(Creature? owner)
    {
        try
        {
            var kurage = BakeKuragePet.Of(owner);
            var room = NCombatRoom.Instance;
            if (kurage == null || room == null) return;
            var ownerNode = room.GetCreatureNode(owner);
            var node = room.GetCreatureNode(kurage);
            if (ownerNode == null || node == null) return;
            node.Position = new Vector2(
                Centre(ownerNode.Position.X, ownerNode.Hitbox.Size.X * 0.5f,
                       node.Visuals.Bounds.Size.X),
                ownerNode.Position.Y + OwnerYOffset);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] Bake-Kurage placement skipped: {e}");
        }
    }
}

/// <summary>After a mid-combat add re-lays an owner's pets.</summary>
[HarmonyPatch(typeof(NCombatRoom), nameof(NCombatRoom.AddCreature))]
internal static class BakeKurage_AddCreature_Placement_Patch
{
    [HarmonyPostfix]
    private static void Postfix(Creature creature)
    {
        // Scoped to a seat whose Kokomi kit is up: only those own a
        // jellyfish.
        if (creature?.PetOwner is { } player
            && KokomiOverhaul.LiveFor(player.Creature))
        {
            BakeKuragePlacement.Place(player.Creature);
        }
    }
}

/// <summary>After the combat-start layout.</summary>
[HarmonyPatch(typeof(NCombatRoom), nameof(NCombatRoom.PositionPlayersAndPets))]
internal static class BakeKurage_PositionPlayersAndPets_Placement_Patch
{
    [HarmonyPostfix]
    private static void Postfix(List<NCreature> creatureNodes)
    {
        if (creatureNodes == null) return;
        foreach (var node in creatureNodes)
        {
            if (node?.Entity is { IsPlayer: true } player
                && KokomiOverhaul.LiveFor(player))
            {
                BakeKuragePlacement.Place(player);
            }
        }
    }
}
