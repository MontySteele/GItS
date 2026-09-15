using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using KleeMod.Teyvat.Acts;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Acts;

namespace KleeMod.Teyvat.Patches;

/// <summary>
/// PUBLISHING THE DRESSINGS -- `MegaCrit.Sts2.Core.Models.ModelDb.get_Acts`.
///
/// `ModelDb.Acts` is a hand-written four-element list (`ModelDb.cs:299`).
/// Unlike cards and relics it does NOT consult
/// `ModelDb.AllAbstractModelSubtypes`, which is the seam
/// `ReflectionHelper.GetSubtypesInMods&lt;AbstractModel&gt;` brings mod content in
/// by -- so a mod act is constructed at boot, holds a `ModelId`, is
/// retrievable through `ModelDb.GetById`, and is nonetheless invisible to
/// every run. This postfix is the one line that changes that.
///
/// REPLACEMENT, NOT APPENDING, AND THAT IS THE WHOLE SHAPE OF THE ARM.
/// `ActModel.GetRandomList` (`ActModel.cs:551`) walks `ModelDb.ActsByIndex`,
/// keeps the unlocked acts at each index and calls `rng.NextItem` once per
/// index. Overgrowth and Underdocks both stand at index 0, so appending two
/// dressings there would make act 1 a four-way roll: a run could open in
/// Overgrowth *or* Mondstadt, which are the same zone in two coats, and the
/// pair would stop being a pair.
///
/// So with the arm on, `Overgrowth` and `Underdocks` are REMOVED and
/// `Mondstadt` and `Liyue` stand in their places, in their order. Act 1 is
/// still exactly two candidates and still exactly one `rng.NextItem` draw
/// against a two-element list -- the same draw, off the same rng, consuming
/// the same amount of it. What the coin decides is which NATION act 1 is,
/// and the base zones are reachable only by turning the arm off.
///
/// THE CACHE IS THE RISK, and it is the first thing a deploy must prove.
/// `_acts` and `_actsByIndex` are lazily-cached statics and `ActsByIndex` is
/// built FROM `Acts`. A postfix applied after the first read of either would
/// be invisible; a postfix applied before the first read (which is where
/// `[ModInitializer]` sits, well before a run starts) is seen by both. The
/// pin for it is `ActsByIndex[0]` containing the two dressings after a full
/// boot -- a deploy question, not a build one.
///
/// WHY `get_Acts` AND NOT `get_ActsByIndex`: `Acts` is the upstream of
/// `ActsByIndex`, `AllEvents`, `AllAncients` and `AllEncounters`, so one
/// postfix here dresses all five. `get_Acts` also has a real method body,
/// which matters -- a trivial expression-bodied getter is a JIT inline
/// candidate and may not take a patch at all.
/// </summary>
[HarmonyPatch(typeof(ModelDb), "get_Acts")]
public static class ModelDb_Acts_TeyvatDressings_Patch
{
    /// <summary>
    /// The two swaps, stated once: base act type -> the dressing that stands
    /// in its place. Ordered, and the order is the base game's own
    /// (Overgrowth then Underdocks), so the list this postfix hands back has
    /// the same shape and the same indices as the one it was given.
    /// </summary>
    public static readonly IReadOnlyList<(System.Type BaseAct, System.Type Dressing, System.Func<ActModel> Resolve)> Swaps =
        new (System.Type, System.Type, System.Func<ActModel>)[]
        {
            (typeof(Overgrowth), typeof(Mondstadt), () => ModelDb.Act<Mondstadt>()),
            (typeof(Underdocks), typeof(Liyue), () => ModelDb.Act<Liyue>()),
        };

    /// <summary>
    /// THE DECISION, over TYPES rather than over instances, so it can be
    /// exercised headlessly.
    ///
    /// `ModelDb` is outside the headless boundary -- it is populated only by
    /// the game's boot, and `ReflectionHelper.GetSubtypesInMods` throws
    /// outright before `ModManager` has initialised -- so no `dotnet test` can
    /// call `ModelDb.Acts` or construct an `ActModel`. What it CAN do is ask
    /// this method what the postfix would have produced, which is the same
    /// decision with the instances left out: the same flag read, the same
    /// table, the same in-place replacement, the same stand-down when a base
    /// act is absent.
    ///
    /// The postfix below is then three lines over this, and the pin and the
    /// shipped path cannot disagree about what a swap is.
    /// </summary>
    public static IReadOnlyList<System.Type> Plan(IReadOnlyList<System.Type> actTypes)
    {
        if (!TeyvatFrame.Enabled || actTypes == null)
        {
            return actTypes ?? new List<System.Type>();
        }

        var planned = actTypes.ToList();
        foreach (var (baseAct, dressing, _) in Swaps)
        {
            var index = planned.IndexOf(baseAct);
            if (index >= 0)
            {
                planned[index] = dressing;
            }
        }

        return planned;
    }

    /// <summary>
    /// ALLOCATES A NEW LIST rather than mutating `__result`. The value behind
    /// `__result` is `ModelDb._acts`, the cached backing field itself; writing
    /// through it would make the arm's flag one-way -- flipping
    /// `TeyvatFrame.Enabled` back to false in a test would leave the base
    /// acts permanently gone from a static the whole assembly reads. A fresh
    /// list means the flag is answerable in both directions on one build,
    /// which is what `TeyvatFrameTests` needs to say anything at all.
    /// </summary>
    private static void Postfix(ref IEnumerable<ActModel> __result)
    {
        if (!TeyvatFrame.Enabled || __result == null)
        {
            return;
        }

        var acts = __result.ToList();

        foreach (var (baseAct, _, resolve) in Swaps)
        {
            var index = acts.FindIndex(a => a != null && a.GetType() == baseAct);
            if (index < 0)
            {
                // The base act is not in the list: a game patch moved it, or a
                // second mod already replaced it. Standing down beats
                // appending -- a dressing appended to a list that no longer
                // holds the zone it dresses would be a THIRD candidate at
                // index 0, which is the one outcome this patch exists to
                // prevent. `Plan` makes the same choice.
                continue;
            }

            acts[index] = resolve();
        }

        __result = acts;
    }
}
