using System;
using System.Collections.Generic;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-296`, pinned on the three decisions the repair is made of.
///
/// WHAT CANNOT BE TESTED HERE, said first so the pins are not read as more
/// than they are. The defect is a Godot focus ring and a Godot mouse filter,
/// and this host may not touch a Godot object at all (README, the headless
/// boundary) -- so the WRITES are live-only and named as such in the PR. What
/// IS reachable is every decision that precedes a write: whether a whitelist
/// needs a ring at all, what the ring's neighbours are, and whether a given
/// creature is opened to the mouse for a given session. Each of those was a
/// place the shipped code could have been wrong, and two of them are where the
/// scoping that keeps vanilla untouched lives.
///
/// The pure statics are reached by reflection rather than by making them
/// public, on `NonFiniteCardGuardTests`'s precedent: the alternative was
/// widening a patch class's surface for a test, and the mod has never done
/// that.
/// </summary>
public class PetTargetReachTests
{
    private static bool NeedsRing(IReadOnlyList<bool> interactable) =>
        (bool)Il.Method("CustomTargetReach", "NeedsWhitelistRing")
                .Invoke(null, new object?[] { interactable })!;

    private static (int Left, int Right) Ring(int index, int count) =>
        ((int Left, int Right))Il.Method("CustomTargetReach", "Ring")
                .Invoke(null, new object[] { index, count })!;

    private static bool ShouldOpen(bool custom, bool interactable, bool allowed) =>
        (bool)Il.Method("CustomTargetReach", "ShouldOpenToTheMouse")
                .Invoke(null, new object[] { custom, interactable, allowed })!;

    [Fact]
    public void A_vanilla_whitelist_is_left_exactly_as_the_game_built_it()
    {
        // The scoping clause, and the whole of why this patch may ship. Every
        // vanilla targeting whitelist -- enemies for `AnyEnemy`, allies for
        // `AnyAlly` -- holds only interactable creatures, and those are
        // already linked by `NCombatRoom.UpdateCreatureNavigation`. On such a
        // whitelist the postfix must write NOTHING, so a release build's focus
        // ring is byte-identical to the one the game shipped.
        Assert.False(NeedsRing(new[] { true, true, true }));
        Assert.False(NeedsRing(new[] { true, true }));

        // Nothing to ring, whatever it is made of.
        Assert.False(NeedsRing(new bool[0]));
        Assert.False(NeedsRing(new[] { false }));
        Assert.False(NeedsRing(null!));
    }

    [Fact]
    public void A_whitelist_holding_a_closed_creature_is_ringed()
    {
        // `NCombatRoom.AddCreature` ends every non-Osty pet's setup with
        // `ToggleIsInteractable(on: false)`, and `UpdateCreatureNavigation`'s
        // first clause is `where c.IsInteractable` -- so a pet has never been
        // in any creature's left/right links. This is the case that produced
        // "Slack Water offers only the enemy": one enemy, one pet, and no way
        // to walk between them.
        Assert.True(NeedsRing(new[] { true, false }));
        Assert.True(NeedsRing(new[] { true, true, false }));
    }

    [Fact]
    public void The_ring_wraps_the_way_the_games_own_ring_wraps()
    {
        // Deliberately `UpdateCreatureNavigation`'s arithmetic and not a
        // re-derivation: first wraps left to last, last wraps right to first.
        Assert.Equal((2, 1), Ring(0, 3));
        Assert.Equal((0, 2), Ring(1, 3));
        Assert.Equal((1, 0), Ring(2, 3));

        // The live shape: one enemy and the jellyfish. Each is both the other's
        // left and its right, so ONE press in either direction crosses -- which
        // is what the owner's controller check has to show.
        Assert.Equal((1, 1), Ring(0, 2));
        Assert.Equal((0, 0), Ring(1, 2));
    }

    [Fact]
    public void The_mouse_is_opened_for_a_closed_creature_and_only_then()
    {
        // The one case that needs it: a mod-registered single-target session,
        // a creature the game closed, and a predicate that admits it.
        Assert.True(ShouldOpen(custom: true, interactable: false, allowed: true));

        // A vanilla session opens nothing, whatever is on the board -- this is
        // the clause that makes the patch inert in a release build, where no
        // shipped row declares a custom target type.
        Assert.False(ShouldOpen(custom: false, interactable: false, allowed: true));

        // An ordinary enemy is already open; writing to it would be the patch
        // taking ownership of a filter it did not set.
        Assert.False(ShouldOpen(custom: true, interactable: true, allowed: true));

        // And the session's own predicate still decides: a `Pet` card does not
        // open anything the predicate refuses.
        Assert.False(ShouldOpen(custom: true, interactable: false, allowed: false));
    }

    [Fact]
    public void The_navigation_restore_hangs_off_the_end_of_targeting_and_is_deferred()
    {
        // `EB-300`'s 2026-09-02 correction, pinned STRUCTURALLY because the
        // thing that was wrong is a call graph and a frame, neither of which
        // this host can execute.
        //
        // The owner's soft-lock stack showed the whole card play nested INSIDE
        // `NTargetManager.FinishTargeting` -- the completion source runs its
        // continuation synchronously -- so a `TryPlayCard` postfix is one of
        // the innermost frames and everything that unwinds after it puts the
        // hand back at `FocusMode.None`. Two facts have to hold, and both are
        // readable off the compiled bodies:
        //
        //   1. the end of EVERY targeting session asks for a restore, so a
        //      cancel and an early exit are covered as well as a play;
        //   2. the restore SCHEDULES rather than running, so it lands after
        //      the coroutine tail and the screen-context change.
        var exit = Il.Method("NTargetManager_FinishTargeting_ClosePet_Patch", "Postfix");
        Assert.Contains(Il.Calls(exit),
            c => c.EndsWith("CustomTargetNavigationRestore.Schedule", StringComparison.Ordinal));

        // The old seam still delegates to the same scheduler rather than
        // restoring inline -- it may not re-introduce the innermost-frame
        // restore by another route.
        var play = Il.Method(
            "NCardPlay_TryPlayCard_RestoreControllerNavigation_Patch", "Postfix");
        Assert.Contains(Il.Calls(play),
            c => c.EndsWith("CustomTargetNavigationRestore.Schedule", StringComparison.Ordinal));
        Assert.DoesNotContain(Il.Calls(play),
            c => c.EndsWith("NCombatRoom.EnableControllerNavigation", StringComparison.Ordinal));

        // And the scheduler waits on a frame before it touches focus.
        var schedule = Il.Method("CustomTargetNavigationRestore", "Schedule");
        Assert.Contains(Il.Calls(schedule),
            c => c.EndsWith("SceneTree.Connect", StringComparison.Ordinal)
              || c.EndsWith("GodotObject.Connect", StringComparison.Ordinal));
    }
}
