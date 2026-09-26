using System;
using System.Collections.Generic;
using System.Linq;
using Godot;
using HarmonyLib;
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
///   3. THE ENGINE'S LINE STARTS INSIDE THE OWNER. Slot 0 sits at
///      <c>owner.X - 20 + petHalfWidth</c>, which for a 121-wide Usher is
///      <c>owner.X + 40</c>: squarely inside Furina's 240-wide box, so a lone
///      performer (and the back one of any line) stood on her legs from the
///      first build of the stage (`EB-721`, 39352a3f) to the 2026-09-26 smoke.
///      That formula is right for a Byrdpip at its owner's feet and wrong for
///      a person on a stage. The base game's own answer for a pet that must
///      stand clear is Osty's (<c>NCreature.GetOstyOffsetFromPlayer</c>):
///      start from the owner's hitbox EDGE, <c>owner.X + Hitbox.X * 0.5</c>,
///      and step out from there (Osty by 150 to 250 more, and the Necrobinder
///      is walked 150 left at combat start to make the room). The line here
///      starts at that same edge, one <see cref="Gap"/> of floor clear of it,
///      and packs each body a <see cref="Gap"/> from the next; Furina is not
///      moved.
///
/// AND ONE THING IT HIDES: THE BARS. <c>NCombatRoom.AddCreature</c> ends
/// every mid-fight add by walking the owner's non-Osty pets and calling
/// <c>ToggleIsInteractable(on: false)</c> on each (0.111.0 decompile), and
/// that one method also writes <c>_stateDisplay.Visible = false</c> -- the
/// HP bar. <c>NCreature._Ready</c> had just shown it off
/// <c>IsHealthBarVisible</c> (true here: <c>CustomPetModel(visibleHp:
/// true)</c>); the add's own loop hides it again a line later, and hides
/// every OTHER performer's with it. Osty alone is exempt, by type. So a
/// performer's Fanfare bar has NEVER been on screen, since `EB-721`; the
/// 2026-09-26 smoke is the first frame anyone looked for it. The repair is
/// <see cref="ShowBars"/>, run by a postfix on that same
/// <c>AddCreature</c>, and it shows the BAR ONLY: the body's hitbox stays
/// closed (mouse and focus, as `EB-296` found them), so no targeting ring and
/// no navigation changes. The bar carries its own hover hitbox
/// (<c>%HpBarHitbox</c>), which is what shows the nameplate and the badge tips
/// on hover, as Osty's does.
///
/// SO: A SMALL PLACEMENT PASS, AND NOT A HARMONY PATCH. This lays the line
/// out in SEAT order after every change to the stage. It patches nothing,
/// overrides nothing and is called only by the stage's own verbs
/// (<c>FurinaStagePets.Sync</c> and <c>FurinaStage</c>), so with the arm off
/// it does not run and a board with no stage is laid out by the engine exactly
/// as it always was. (The bars below DO need a patch, because the engine hides
/// them inside its own add; that postfix is scoped to Furina's pets.)
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
    /// <summary>The engine's own Y offset, lifted rather than chosen:
    /// <c>NCombatRoom.AddCreature</c> stands a pet at <c>owner.Y + 10</c>.
    /// </summary>
    private const float OwnerYOffset = 10f;

    /// <summary>Floor between Furina's box and the first body, and between
    /// every two bodies. The engine's own pet margin (the 20 in
    /// <c>owner.X - 20</c>), turned outward.</summary>
    public const float Gap = 20f;

    /// <summary>
    /// The line's centres, BACK FIRST, off the owner's centre and half-width
    /// and each body's width in the same order. PURE, so the headless suite
    /// can hold the one property the smoke caught: no body starts inside her
    /// box, and no two bodies overlap.
    /// </summary>
    public static float[] LineCentres(float ownerX, float ownerHalfWidth,
                                      IReadOnlyList<float> widthsBackFirst)
    {
        var centres = new float[widthsBackFirst.Count];
        var edge = ownerX + ownerHalfWidth + Gap;
        for (var i = 0; i < widthsBackFirst.Count; i++)
        {
            centres[i] = edge + widthsBackFirst[i] * 0.5f;
            edge += widthsBackFirst[i] + Gap;
        }
        return centres;
    }

    /// <summary>Should this body wear its bar? Every live performer, off the
    /// model's own <c>IsHealthBarVisible</c> -- the hook the engine asks in
    /// <c>NCreature._Ready</c> and the one Osty answers the same way.</summary>
    public static bool ShowsBar(Creature? body) =>
        body is { IsAlive: true, Monster: StagePerformerMonster model }
        && model.IsHealthBarVisible;

    /// <summary>
    /// Put every live performer's Fanfare bar back on screen after the
    /// engine's add hid it (see the header). Writes exactly what
    /// <c>NCreature.ToggleIsInteractable</c> writes for the bar and nothing
    /// else: <c>Visible = !IsDebugHidingHpBar</c>. A remote seat's bar keeps
    /// the engine's transparent-until-hovered state, because only
    /// <c>Visible</c> is touched and never <c>Modulate</c>.
    /// </summary>
    public static void ShowBars(Creature? furina)
    {
        if (!FurinaStage.LiveFor(furina)) return;
        try
        {
            var room = NCombatRoom.Instance;
            if (room == null) return;
            foreach (var node in room.CreatureNodes)
            {
                if (!GodotObject.IsInstanceValid(node)) continue;
                var body = node.Entity;
                if (body?.PetOwner?.Creature != furina) continue;
                if (!ShowsBar(body)) continue;
                // `%HealthBar` on the creature is its NCreatureStateDisplay,
                // the node `_stateDisplay` holds (NCreature._Ready's own
                // lookup, and the cue chips' in FurinaStageCueNodes.FillOf).
                if (node.GetNodeOrNull<Control>("%HealthBar") is not { } display)
                    continue;
                display.Visible = !NCombatUi.IsDebugHidingHpBar;
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] stage: bars not shown: {e}");
        }
    }

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
            // Slot 0 is the LEFT-most (furthest from the enemy) and takes the
            // BACK performer, so the walk is over the seats in reverse.
            var line = new List<NCreature>();
            for (var i = nodes.Count - 1; i >= 0; i--)
            {
                if (nodes[i] is { } node) line.Add(node);
            }
            if (line.Count == 0) return;

            // From Furina's hitbox EDGE outward, Osty's reference point
            // (`GetOstyOffsetFromPlayer`: owner.X + Hitbox.X * 0.5); each
            // body's width is the engine's own pet measure, its Bounds.
            var centres = LineCentres(
                owner.Position.X,
                owner.Hitbox.Size.X * 0.5f,
                line.Select(n => n.Visuals.Bounds.Size.X).ToList());
            for (var slot = 0; slot < line.Count; slot++)
            {
                line[slot].Position = new Vector2(
                    centres[slot], owner.Position.Y + OwnerYOffset);
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] stage: placement pass skipped: {e}");
        }
    }
}

/// <summary>
/// The bars back on after every add. <c>NCombatRoom.AddCreature</c> hides
/// every non-Osty pet's bar of the owner it adds to (see
/// <see cref="FurinaStagePlacement"/>'s header), so this runs on EVERY add to
/// Furina's side, not only a performer's: any pet she gains mid-fight would
/// otherwise take the stage's bars down with it.
/// </summary>
[HarmonyPatch(typeof(NCombatRoom), nameof(NCombatRoom.AddCreature))]
internal static class NCombatRoom_AddCreature_StageBars_Patch
{
    [HarmonyPostfix]
    public static void Postfix(Creature creature)
    {
        var owner = creature?.PetOwner?.Creature;
        if (!FurinaResources.IsFurina(owner)) return;
        FurinaStagePlacement.ShowBars(owner);
    }
}
