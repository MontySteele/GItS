using System;
using BaseLib.Patches.Features;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.GodotExtensions;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Screens.ScreenContext;

namespace KleeMod.Patches;

/// <summary>
/// `EB-300` (and, through it, `EB-296`). AFTER A CARD WITH A CUSTOM TARGET
/// TYPE IS PLAYED, THE CONTROLLER CANNOT GET BACK TO THE HAND.
///
/// [USER], playing the Kokomi overhaul arm on a controller: "When there is a
/// Plan card loaded, I cannot get back to my hand on controller navigation" --
/// and then, decisively, "it happens when I play Slack Water directly (not as
/// a plan card) as well". The two plays share one thing: both cards declare a
/// CUSTOM target type (`KokomiTargets.PetOnly` and `PetOrEnemy`), so both take
/// the base library's replacement targeting path instead of the game's.
///
/// THE DEFECT IS ONE MISSING LINE, and `godot.log` from that very session
/// prints its consequence in the clear:
///
///     WARNING: This control can't grab focus...
///       [1] NodeUtil.TryGrabFocus(Control)
///       [2] BaseLib...TryPlayCardPatch.StopPlayIfCustomTargetInvalid
///       [3] NCardPlay.TryPlayCard_Patch2
///       [4] BaseLib...ControllerSingleCreatureTargetingPatch+
///           &lt;FilteredControllerTargeting&gt;d__1.MoveNext()
///
/// The game's own <c>NControllerCardPlay.SingleCreatureTargeting</c> ends
/// targeting with <c>NCombatRoom.Instance.EnableControllerNavigation()</c>, one
/// line after <c>SelectionFinished()</c> and BEFORE <c>TryPlayCard</c>. The
/// library's replacement for that method never calls it. So the state
/// <c>RestrictControllerNavigation</c> put the room in survives the play:
/// every hand holder is left at <c>FocusMode.None</c>
/// (<c>NPlayerHand.DisableControllerNavigation</c>), every creature hitbox is
/// left on the targeting whitelist with <c>FocusNeighborBottom</c> pointing at
/// itself, and <c>UpdateCreatureNavigation</c> -- the only thing that rebuilds
/// the left/right/bottom links -- never runs. The library's own
/// <c>Ui.Hand.TryGrabFocus()</c> then fails, because the thing it is asking to
/// take focus is the thing it just made unfocusable. That is the warning above.
///
/// WHY IT ALSO EXPLAINS `EB-296`. With the creature ring left unlinked, the
/// next targeting walk can reach only whichever hitbox grabbed focus first:
/// a one-candidate type (`Pet`) is unaffected and Kurage's Oath worked, while
/// a two-candidate type (`PetOrEnemy`) strands the player on the first
/// candidate -- "dragging it offers only the enemy" -- and a hand nobody can
/// return to reads as "no valid selector at all". The `PetOrEnemy` predicate
/// itself admits the pet (it is `CustomTargetType.Pet`'s clause verbatim), and
/// the wire path, which supplies its target explicitly, has never been able to
/// see any of this.
///
/// THE FIX IS THE GAME'S OWN LINE, PUT BACK, at the one moment every path
/// passes through. A postfix runs even when a prefix skipped the original, so
/// this fires on the library's arm as well as the game's. It is idempotent:
/// on the vanilla arm navigation is already enabled and this re-enables it,
/// which is exactly what <c>OnCancelPlayCard</c> does unconditionally on every
/// cancel.
///
/// SHIPPED, NOT QUARANTINED, on `Vfx/NonFiniteCardGuard.cs`'s precedent and
/// for the same reason: the broken code is the base LIBRARY's, reached by any
/// card of any character declaring any custom target type, and scoping the
/// repair to one prototype arm would leave the trap armed everywhere else. It
/// is inert in a release build by construction -- no shipped row declares a
/// custom target type, so <see cref="ShouldRestore"/> answers false.
/// </summary>
[HarmonyPatch(typeof(NCardPlay), "TryPlayCard")]
internal static class NCardPlay_TryPlayCard_RestoreControllerNavigation_Patch
{
    /// <summary>
    /// Did this play go through the library's custom-target path?
    ///
    /// Asked of the HOLDER's model and not of <c>NCardPlay.Card</c>, for two
    /// reasons and either would be enough: <c>Card</c> is protected (the
    /// library reaches it from inside its own patch), and a successful play has
    /// already run <c>Cleanup</c> by the time a postfix sees it, while the
    /// holder outlives the play. It is the same read
    /// <c>TryPlayCardPatch</c> itself makes.
    ///
    /// Pure and static so the condition is assertable headlessly, which is as
    /// far into this file as a test without Godot can reach.
    /// </summary>
    internal static bool ShouldRestore(MegaCrit.Sts2.Core.Models.CardModel? card) =>
        card != null && CustomTargetType.IsCustomSingleTargetType(card.TargetType);

    [HarmonyPostfix]
    public static void Postfix(NCardPlay __instance, Creature? target)
    {
        try
        {
            if (!ShouldRestore(__instance.Holder?.CardModel)) return;

            // SCHEDULED, NOT RUN, AND THAT IS THE 2026-09-02 CORRECTION. This
            // postfix is one of the INNERMOST frames of the play, not one of
            // the last: the completion source runs its continuation
            // synchronously, so `TryPlayCard` is nested inside
            // `NTargetManager.FinishTargeting` and the library's coroutine tail
            // and the screen-context change both run after this returns and put
            // the hand back at `FocusMode.None`. The restore has to land a
            // frame later, which is what `Schedule` buys.
            //
            // This seam is also no longer load-bearing: `ShouldRestore` reads
            // the HOLDER's model, and a played card's holder no longer carries
            // one by the time BaseLib's `Cleanup(true)` has run -- which is why
            // `PR #271` never fired on the path it was written for. The
            // `FinishTargeting` postfix is the seam that actually covers every
            // exit; this one is kept because it is free, it is idempotent
            // within a frame, and it is the record of what EB-300 was.
            CustomTargetNavigationRestore.Schedule();
        }
        catch (Exception e)
        {
            // A focus restore may not cost a run. Naming it is the whole of
            // what this catch buys, and the pre-patch behaviour is "focus is
            // wherever it was", which is what a swallowed throw leaves.
            Log.Warn($"[{KleeMod.ModId}] EB-300: could not restore controller "
                   + $"navigation after a custom-target play: {e}");
        }
    }
}
