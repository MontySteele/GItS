using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Patches.Features;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Patches;

/// <summary>
/// `EB-296`. A CARD THAT MAY AIM AT A PET CANNOT REACH THE PET -- not by
/// D-pad, and not by mouse. Read out of the 0.111.0 decompile rather than
/// guessed, because `PR #271`'s theory (that this was `EB-300` downstream) was
/// wrong: restoring navigation AFTER a play cannot fix the FIRST play of a
/// fresh combat, and the owner's 0.2.2046 session proves it did not.
///
/// THE ONE LINE THAT CAUSES BOTH HALVES is in the base game, in
/// <c>NCombatRoom.AddCreature</c>: every pet that is not the local
/// Necrobinder's Osty is laid out beside its owner and then
/// <c>ToggleIsInteractable(on: false)</c>. <c>NCreature._Ready</c> reaches the
/// same call from the other side -- <c>ToggleIsInteractable(Entity.Monster
/// .IsHealthBarVisible)</c>, and a pet's model answers false so it gets no HP
/// bar. That one method sets THREE things at once:
///
///     IsInteractable   = false      // drops it from the navigation ring
///     Hitbox.MouseFilter = Ignore   // the hitbox stops seeing the mouse
///     Hitbox.FocusMode   = None     // the hitbox stops taking focus
///
/// **CONTROLLER.** BaseLib's <c>ControllerSingleCreatureTargetingPatch
/// .FilteredControllerTargeting</c> is NOT the culprit -- it builds its
/// candidate list from the REGISTERED predicate
/// (<c>CustomTargetType.SingleTargeting</c>), so the pet is in the list and
/// <c>RestrictControllerNavigation(whitelist)</c> hands its hitbox
/// <c>FocusMode = All</c> back. What nothing does is LINK it.
/// <c>NCombatRoom.UpdateCreatureNavigation</c> is the only builder of the
/// left/right focus ring and its first clause is <c>where c.IsInteractable</c>,
/// so no creature's <c>FocusNeighborLeft/Right</c> has ever pointed at the pet.
/// Targeting then opens on <c>list.First()</c>, which is the first entry of
/// <c>CreatureNodes</c> the filter admits -- the enemies are added at combat
/// start and the pet after, so focus lands on an enemy and the D-pad walks an
/// enemy-only ring for ever. That is "only the enemy is offered", exactly.
/// A one-candidate type (`Pet`, Kurage's Oath) never notices, because
/// <c>TryGrabFocus</c> puts the player straight onto the pet.
///
/// **MOUSE.** <c>Hitbox.MouseFilter = Ignore</c> means the pet's hitbox never
/// emits <c>MouseEntered</c>; <c>NCreature.OnFocus</c> never runs;
/// <c>NTargetManager.OnNodeHovered</c> is never called; <c>HoveredNode</c>
/// stays null and <c>FinishTargeting</c> resolves to a cancel. BaseLib's
/// <c>AllowedToTargetCreaturePatch</c> -- the predicate gate that WOULD say yes
/// -- is never even asked. <c>RestrictControllerNavigation</c> puts
/// <c>FocusMode</c> back and never touches <c>MouseFilter</c>, which is why the
/// controller had a partial escape and the mouse has none: dragging onto the
/// jellyfish fails today for `PetOrEnemy` AND for `PetOnly`. It is not a
/// regression from the jellyfish scene: <c>%Hitbox</c> lives on the game's own
/// <c>NCreature</c> scene and no visuals scene can set its mouse filter.
///
/// THE REPAIR IS TWO POSTFIXES ON THE GAME'S OWN SEAMS, both scoped so that a
/// board with no custom target type on it is byte-identical to vanilla.
/// SHIPPED, NOT QUARANTINED, on <c>CustomTargetControllerNavigationPatch</c>'s
/// precedent and for its reason: the unreachable pet belongs to the base game
/// and the base LIBRARY's own <c>Pet</c> / <c>PetOrSelf</c> types hit it too,
/// so scoping the repair to one prototype arm would leave the trap armed for
/// everyone else. Both are inert in a release build by construction -- no
/// shipped row declares a custom target type, so no shipped play ever restricts
/// navigation to a non-interactable creature or starts a custom-typed
/// targeting session.
/// </summary>
internal static class CustomTargetReach
{
    /// <summary>
    /// Does this whitelist need a ring built for it?
    ///
    /// ONLY when it holds a creature the game's own ring cannot reach, which
    /// is exactly a non-interactable one. On every vanilla whitelist (enemies
    /// for `AnyEnemy`, allies for `AnyAlly`) each entry is interactable and
    /// already linked by <c>UpdateCreatureNavigation</c>, so this answers false
    /// and the postfix writes nothing. Pure and static so the condition is
    /// assertable headlessly, which is as far into this file as a test without
    /// Godot can reach.
    /// </summary>
    internal static bool NeedsWhitelistRing(IReadOnlyList<bool> interactable) =>
        interactable != null
        && interactable.Count > 1
        && interactable.Any(i => !i);

    /// <summary>
    /// The cyclic left/right neighbours of position <paramref name="index"/>
    /// in a ring of <paramref name="count"/>. Deliberately the arithmetic
    /// <c>UpdateCreatureNavigation</c> performs, not a re-derivation: first
    /// wraps left to last, last wraps right to first.
    /// </summary>
    internal static (int Left, int Right) Ring(int index, int count) =>
        (index <= 0 ? count - 1 : index - 1,
         index < count - 1 ? index + 1 : 0);

    /// <summary>
    /// Should this creature's hitbox be opened to the mouse for the targeting
    /// session now starting?
    ///
    /// Three clauses, and each one is a scope: the session must belong to a
    /// MOD-registered single-target type (a vanilla session is untouched), the
    /// creature must be one the game has closed (an ordinary enemy is already
    /// open and is not written to), and the session's own predicate must admit
    /// it (a `Pet` card does not open an enemy, an `AnyEnemy` card opens
    /// nothing).
    /// </summary>
    internal static bool ShouldOpenToTheMouse(
        bool customSingleTargetType, bool interactable, bool allowedToTarget) =>
        customSingleTargetType && !interactable && allowedToTarget;
}

/// <summary>
/// `EB-296`, the CONTROLLER half: link the targeting whitelist into a ring, so
/// the D-pad can walk from the enemy to the pet and back.
///
/// The postfix runs after <c>RestrictControllerNavigation</c> has set
/// <c>FocusMode</c> and before BaseLib's <c>TryGrabFocus</c>, which is the one
/// window in which the links are read. Bottom is left where the original put it
/// (each hitbox pointing at itself) so the player still cannot fall out of
/// targeting into the disabled hand; only left/right are written, plus top for
/// a creature the ordinary ring has never touched -- an unset
/// <c>FocusNeighborTop</c> falls through to Godot's geometric search, which
/// from a pet can land anywhere.
/// </summary>
[HarmonyPatch(typeof(NCombatRoom), nameof(NCombatRoom.RestrictControllerNavigation),
    new[] { typeof(IEnumerable<Control>) })]
internal static class NCombatRoom_RestrictControllerNavigation_RingTheWhitelist_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCombatRoom __instance, IEnumerable<Control> whitelist)
    {
        try
        {
            var hitboxes = whitelist?.Where(GodotObject.IsInstanceValid).ToList();
            if (hitboxes == null || hitboxes.Count < 2) return;

            // Creature hitboxes only. A whitelist can carry a multiplayer
            // player-state hitbox, which has no NCreature and no place in a
            // creature ring; if any entry is not a creature's, leave the whole
            // thing to the game rather than building a partial ring.
            var nodes = __instance.CreatureNodes
                .Where(n => GodotObject.IsInstanceValid(n) && hitboxes.Contains(n.Hitbox))
                .ToList();
            if (nodes.Count != hitboxes.Count) return;

            if (!CustomTargetReach.NeedsWhitelistRing(
                    nodes.Select(n => n.IsInteractable).ToList())) return;

            var ordered = nodes.OrderBy(n => n.Hitbox.GlobalPosition.X).ToList();
            for (var i = 0; i < ordered.Count; i++)
            {
                var (left, right) = CustomTargetReach.Ring(i, ordered.Count);
                ordered[i].Hitbox.FocusNeighborLeft = ordered[left].Hitbox.GetPath();
                ordered[i].Hitbox.FocusNeighborRight = ordered[right].Hitbox.GetPath();
                if (!ordered[i].IsInteractable)
                {
                    ordered[i].Hitbox.FocusNeighborTop = ordered[i].Hitbox.GetPath();
                }
            }
        }
        catch (Exception e)
        {
            // A missing link costs a target, not a run: the pre-patch
            // behaviour is "the ring is whatever the game built", which is
            // what a swallowed throw leaves.
            Log.Warn($"[{KleeMod.ModId}] EB-296: could not ring the targeting "
                   + $"whitelist: {e}");
        }
    }
}

/// <summary>
/// `EB-296`, the MOUSE half: open a closed creature's hitbox for the duration
/// of a targeting session that admits it, and close it again afterwards.
///
/// SCOPED TO THE SESSION rather than left open, so that outside targeting the
/// pet behaves exactly as the base game intends -- no nameplate on hover, no
/// hover tips, no HP bar. <c>NTargetManager.StartTargeting</c> and
/// <c>FinishTargeting</c> are the pair every input path passes through (the
/// mouse path never calls <c>RestrictControllerNavigation</c> at all, which is
/// why the controller seam cannot carry this half).
/// </summary>
internal static class PetMouseReach
{
    /// <summary>
    /// The hitboxes this opened, so the close puts back exactly what it
    /// changed. Static because <c>NTargetManager</c> is a singleton and a
    /// session cannot overlap another.
    /// </summary>
    private static readonly List<NCreature> Opened = new();

    internal static void Open(TargetType targetType)
    {
        try
        {
            Close();
            if (!CustomTargetType.IsCustomSingleTargetType(targetType)) return;

            var room = NCombatRoom.Instance;
            var manager = NTargetManager.Instance;
            if (room == null || manager == null) return;

            foreach (var node in room.CreatureNodes)
            {
                if (!GodotObject.IsInstanceValid(node) || node.Hitbox == null) continue;
                if (!CustomTargetReach.ShouldOpenToTheMouse(
                        customSingleTargetType: true,
                        interactable: node.IsInteractable,
                        allowedToTarget: manager.AllowedToTargetNode(node))) continue;

                node.Hitbox.MouseFilter = Control.MouseFilterEnum.Stop;
                Opened.Add(node);
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] EB-296: could not open the pet hitbox for "
                   + $"targeting: {e}");
        }
    }

    internal static void Close()
    {
        try
        {
            foreach (var node in Opened)
            {
                // `IsInteractable` is re-read rather than assumed: if the game
                // opened this creature up while the session ran, closing it
                // here would take away something we did not grant.
                if (!GodotObject.IsInstanceValid(node) || node.Hitbox == null) continue;
                if (node.IsInteractable) continue;
                node.Hitbox.MouseFilter = Control.MouseFilterEnum.Ignore;
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] EB-296: could not close the pet hitbox after "
                   + $"targeting: {e}");
        }
        finally
        {
            Opened.Clear();
        }
    }
}

/// <summary>`EB-296`: the mouse-path open, on the overload the card play uses.</summary>
[HarmonyPatch(typeof(NTargetManager), nameof(NTargetManager.StartTargeting),
    new[] { typeof(TargetType), typeof(Control), typeof(TargetMode),
            typeof(Func<bool>), typeof(Func<Node, bool>) })]
internal static class NTargetManager_StartTargeting_Control_OpenPet_Patch
{
    [HarmonyPostfix]
    public static void Postfix(TargetType validTargetsType) =>
        PetMouseReach.Open(validTargetsType);
}

/// <summary>`EB-296`: the same, on the position overload, so no path is missed.</summary>
[HarmonyPatch(typeof(NTargetManager), nameof(NTargetManager.StartTargeting),
    new[] { typeof(TargetType), typeof(Vector2), typeof(TargetMode),
            typeof(Func<bool>), typeof(Func<Node, bool>) })]
internal static class NTargetManager_StartTargeting_Position_OpenPet_Patch
{
    [HarmonyPostfix]
    public static void Postfix(TargetType validTargetsType) =>
        PetMouseReach.Open(validTargetsType);
}

/// <summary>
/// `EB-296`: the close. <c>FinishTargeting</c> is the single exit of every
/// session -- play, cancel and early-exit alike all resolve the completion
/// source through it -- so one postfix cannot leave a hitbox open.
/// </summary>
[HarmonyPatch(typeof(NTargetManager), "FinishTargeting")]
internal static class NTargetManager_FinishTargeting_ClosePet_Patch
{
    [HarmonyPostfix]
    public static void Postfix() => PetMouseReach.Close();
}
