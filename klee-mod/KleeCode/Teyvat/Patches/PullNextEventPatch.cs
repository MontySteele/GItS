using System;
using System.Collections.Generic;
using HarmonyLib;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Teyvat.Patches;

/// <summary>
/// THE CONVERTED EVENT'S ONE SEAM --
/// `MegaCrit.Sts2.Core.Models.ActModel.PullNextEvent`.
///
/// THE OBVIOUS ROUTE IS THE WRONG ONE, and finding that out is most of what
/// spike item 4.2 proves.
///
/// The obvious route is to declare the converted event in the dressing's
/// `AllEvents` in place of the base one. It cannot be done here, because
/// **Room Full of Cheese is not an act event at all** -- it is one of the
/// eighteen in `ModelDb.AllSharedEvents` (`ModelDb.cs:157-176`), shared by
/// every act, and its own `IsAllowed` is `runState.CurrentActIndex &lt; 2`. An
/// act's `AllEvents` cannot remove a shared event, so swapping inside
/// Mondstadt's pool would have ADDED a fourteenth act event beside the shared
/// thirteenth.
///
/// AND THE COUNT IS A HARD RULE. `ActModel.GenerateRooms` (`:292`)
/// concatenates `AllEvents` with `ModelDb.AllSharedEvents`, strips events
/// behind unrevealed epochs, and `UnstableShuffle(rng)`s the whole thing on
/// the run's `UpFront` rng -- once, at run start, for EVERY act
/// (`RunManager.cs:764`). A pool one element longer consumes a different
/// number of draws from that rng and moves every later roll on it: bosses,
/// Ancients, encounter order. The Klee fun calibration rides a fixed seed on
/// the next three builds, so a pool-length change is not a cosmetic risk.
///
/// SO THE SUBSTITUTION HAPPENS DOWNSTREAM OF THE SHUFFLE, at the moment the
/// map hands the player an event. `PullNextEvent` is a four-line method with a
/// real body (`ActModel.cs:450`), called once per event room; a postfix here
/// consumes no rng at all, so the two zones' room sets stay byte-identical on
/// a fixed seed and the converted event still appears exactly as often as the
/// one it replaces -- because it appears exactly WHEN it does.
///
/// WHY NOT THE READ'S OTHER TWO LEVERS. `EventModel.IsAllowed` is consulted at
/// pull time by `RoomSet.EnsureNextEventIsValid`, which SKIPS FORWARD through
/// the pre-shuffled list -- it would remove Room Full of Cheese from a
/// Mondstadt run and put nothing in its place, and the skip itself changes
/// which event lands. `Hook.ModifyNextEvent` (called on the line below the one
/// patched here) is the game's own substitution seam and is the right long-term
/// home, but it is a hook subscription with a lifetime, and a postfix on the
/// method that CALLS it is the smaller thing to prove in a spike.
///
/// ONE-FOR-ONE, AND ONLY IN THE DRESSING. In Overgrowth, in Liyue and with the
/// arm off, `PullNextEvent` returns exactly what it returned before.
/// </summary>
[HarmonyPatch(typeof(ActModel), nameof(ActModel.PullNextEvent))]
public static class ActModel_PullNextEvent_TeyvatConversions_Patch
{
    /// <summary>
    /// (dressing, base event type) -> the dressed event that stands in for it.
    ///
    /// A TABLE AND NOT AN `if`, because the whole face gallery lands here one
    /// row at a time and the row is the only thing a dressing should cost --
    /// and the rows are now GENERATED. `TeyvatGeneratedEvents.Substitutions`
    /// is emitted by `tools/gen_teyvat_events.py` from the same curated face
    /// files as the dressed classes and their loc rows, so a dressing cannot
    /// have a class the table does not name or a row the class does not ask
    /// for. This alias exists so the postfix below reads the same as it did
    /// when the table was hand-written, and so the pins have one name to hold.
    /// </summary>
    private static IReadOnlyDictionary<(string Dressing, Type BaseEvent), Func<EventModel>> Conversions =>
        TeyvatGeneratedEvents.Substitutions;

    private static void Postfix(ActModel __instance, ref EventModel __result)
    {
        if (!TeyvatFrame.Enabled || __instance == null || __result == null)
        {
            return;
        }

        // The act's OWN entry, not `RunManager`'s. `PullNextEvent` is an
        // instance method on the act being pulled from, so this is the one
        // patch in the arm that does not need the run at all -- which also
        // makes it the one the pin can exercise headlessly.
        var dressing = __instance.Id.Entry;

        // `__result` is a mutable clone in a live run, so the type is the
        // identity, never the reference.
        if (Conversions.TryGetValue((dressing, __result.GetType()), out var conversion))
        {
            __result = conversion();
        }
    }
}
