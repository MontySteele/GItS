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
/// keeps the unlocked acts at each index and calls `rng.NextItem` ONCE per
/// index. Appending a dressing beside the zone it dresses would put the base
/// zone and its own coat in the same coin -- a run could open in Overgrowth
/// *or* Mondstadt, which are the same zone twice -- so with the arm on a base
/// act is REMOVED and its dressing or dressings stand in its place, in order.
///
/// ONE ZONE, TWO FACES, FOR ACTS 2 AND 3. The base game ships TWO zones at
/// index 0 (Overgrowth, Underdocks) and exactly ONE at each of index 1 and 2
/// (Hive, Glory). So act 1's pair is a one-for-one swap that leaves the
/// bucket's SIZE alone, while acts 2 and 3 each replace one base act with a
/// PAIR of siblings (`review/ruled/teyvat-nation-mapping-2026-09-14.md`
/// sec.1): the Hive becomes Natlan and Inazuma, Glory becomes Fontaine and
/// Sumeru, and a one-candidate bucket becomes a two-candidate bucket.
///
/// WHAT THAT COSTS ON THE RNG, STATED PRECISELY, because it is the one place
/// this arm is not rng-neutral by construction. `GetRandomList` makes exactly
/// one `rng.NextItem` call per index whatever the bucket holds -- the loop is
/// over `actsByIndex`, not over candidates -- so the NUMBER of draws on the
/// act rng is three before and three after. What changes is what a draw
/// against a two-element list consumes versus a one-element list, which is a
/// property of `Rng.NextItem` and not of this patch, and that rng
/// (`StartRunLobby`'s own, `StartRunLobby.cs:469`) is read for the act list
/// and nothing else. No pool shuffle, boss order or map roll rides it.
///
/// AFTER THE PATCH THE LIST IS SIX, TWO PER INDEX -- Mondstadt, Liyue,
/// Natlan, Inazuma, Fontaine, Sumeru -- and `ModelDb.Acts`'s documented
/// ordering invariant ("sorted by act index, then by default/non-default",
/// `ModelDb.cs:297`) still holds, because every dressing is `IsDefault` and
/// each pair is spliced in at the position its base act occupied.
///
/// THE CACHE IS THE RISK, and it is the first thing a deploy must prove.
/// `_acts` and `_actsByIndex` are lazily-cached statics and `ActsByIndex` is
/// built FROM `Acts`. A postfix applied after the first read of either would
/// be invisible; a postfix applied before the first read (which is where
/// `[ModInitializer]` sits, well before a run starts) is seen by both. The
/// pin for it is `ActsByIndex[0]`, `[1]` and `[2]` each holding two dressings
/// after a full boot -- a deploy question, not a build one.
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
    /// One base act and the faces that stand in its place, stated once.
    ///
    /// A LIST OF DRESSINGS RATHER THAN ONE, because the base game does not
    /// ship the same number of zones at every index: act 1's entries carry one
    /// face each (the pair was already two zones) and acts 2 and 3 carry two
    /// (one zone, two faces). The order inside an entry is the order the pair
    /// appears in `ModelDb.Acts`, and the order of the entries is the base
    /// game's own, so the list this postfix hands back is still sorted by act
    /// index.
    /// </summary>
    public static readonly IReadOnlyList<(System.Type BaseAct,
                                          IReadOnlyList<System.Type> Dressings,
                                          System.Func<IReadOnlyList<ActModel>> Resolve)> Swaps =
        new (System.Type, IReadOnlyList<System.Type>, System.Func<IReadOnlyList<ActModel>>)[]
        {
            (typeof(Overgrowth), new[] { typeof(Mondstadt) },
                () => new ActModel[] { ModelDb.Act<Mondstadt>() }),
            (typeof(Underdocks), new[] { typeof(Liyue) },
                () => new ActModel[] { ModelDb.Act<Liyue>() }),
            (typeof(Hive), new[] { typeof(Natlan), typeof(Inazuma) },
                () => new ActModel[] { ModelDb.Act<Natlan>(), ModelDb.Act<Inazuma>() }),
            (typeof(Glory), new[] { typeof(Fontaine), typeof(Sumeru) },
                () => new ActModel[] { ModelDb.Act<Fontaine>(), ModelDb.Act<Sumeru>() }),
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
    /// table, the same in-place splice, the same stand-down when a base act is
    /// absent.
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
        foreach (var (baseAct, dressings, _) in Swaps)
        {
            var index = planned.IndexOf(baseAct);
            if (index >= 0)
            {
                planned.RemoveAt(index);
                planned.InsertRange(index, dressings);
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
                // splicing -- faces inserted beside a zone that is no longer
                // there would be EXTRA candidates at that index, which is the
                // one outcome this patch exists to prevent. `Plan` makes the
                // same choice.
                continue;
            }

            acts.RemoveAt(index);
            acts.InsertRange(index, resolve());
        }

        __result = acts;
    }
}
