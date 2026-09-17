using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Teyvat.Patches;

/// <summary>
/// DARV IS ALICE ON EVERY FACE (R275 pick 2) -- and a face act cannot say so
/// through `AllAncients`, which is why this patch exists.
///
/// DARV BELONGS TO NO ACT. `ModelDb.AllSharedAncients` is a hand-written
/// single-element list holding him (`ModelDb.cs:189`), `UnlockState`
/// `SharedAncients` filters it behind `DarvEpoch`, and
/// `RunManager.GenerateRooms` DEALS the survivors out: it shuffles them on
/// `State.Rng.UpFront`, then walks `State.Acts.Skip(1)` spending one
/// `NextInt(count + 1)` per act to decide how many that act takes, and hands
/// the slice to `ActModel.SetSharedAncientSubset`. `ActModel.GenerateRooms`
/// then rolls the act's own Ancient out of
/// `GetUnlockedAncients(...).Concat(_sharedAncientSubset)`.
///
/// SO THE SEAM IS THE HAND-OFF, NOT THE POOL. Putting a dressed Darv into a
/// face act's `AllAncients` would give a run TWO chances at him in one act --
/// the act's copy and the dealt one -- and would change the act pool's length,
/// which is the one thing the six face acts are pinned not to do. Rewriting
/// `ModelDb.AllSharedAncients` instead would dress him globally, with no face
/// to ask, and would do it before any act exists to ask about.
///
/// `SetSharedAncientSubset` is the one call that knows BOTH things at once:
/// which Ancients were dealt, and which act they were dealt TO. A prefix there
/// swaps each one for that act's face's dressing and lets the rest of the
/// sequence run untouched -- every rng draw `GenerateRooms` spends is spent on
/// the BASE list, before this patch is reached, so the deal is bit-identical
/// to an undressed run's.
///
/// SCOPED TO THE ARM AND TO THE SIX FACES. `__instance.Id.Entry` is the face
/// name for a dressing (`MONDSTADT`, `NATLAN`, ...) and the base zone's name
/// for anything else; an act that is not in `FacePools` is left alone, as is
/// every act when `TeyvatFrame.Enabled` is false. `Dress` is the identity in
/// both cases, so this is a prefix that usually writes nothing.
///
/// A PREFIX, NOT A POSTFIX, because `SetSharedAncientSubset` COPIES what it is
/// handed into `_sharedAncientSubset`; a postfix would have nothing left to
/// edit but a private field.
/// </summary>
[HarmonyPatch(typeof(ActModel), nameof(ActModel.SetSharedAncientSubset))]
public static class ActModel_SetSharedAncientSubset_TeyvatAncients_Patch
{
    private static void Prefix(ActModel __instance,
                               ref List<AncientEventModel> sharedAncientSubset)
    {
        if (!TeyvatFrame.Enabled || __instance == null
            || sharedAncientSubset == null || sharedAncientSubset.Count == 0)
        {
            return;
        }

        var face = __instance.Id?.Entry;
        if (face == null || !TeyvatGeneratedAncients.FacePools.ContainsKey(face))
        {
            return;
        }

        sharedAncientSubset =
            TeyvatGeneratedAncients.Dress(face, sharedAncientSubset).ToList();
    }
}
