using HarmonyLib;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Teyvat.Patches;

/// <summary>
/// THE ASSET ALIAS -- `MegaCrit.Sts2.Core.Models.ActModel.get_FilePathIdentifier`.
///
/// A FOURTH PATCH THE DECOMPILE READ DID NOT COST, and it is the spike's one
/// real surprise. The read listed the combat background, the rest site, the
/// map art and the chest rig as things that "follow the id" and costed each at
/// an asset directory. What it did not say is that the five properties which
/// derive those paths -- `RestSiteBackgroundPath`, `MapTopBgPath`,
/// `MapMidBgPath`, `MapBotBgPath` and `BackgroundScenePath` -- are
/// NON-VIRTUAL expression-bodied properties on `ActModel`
/// (`ActModel.cs:52-64`, `:248`). A subclass cannot override one of them. The
/// only seam under all five is `FilePathIdentifier` itself, which is
/// `protected` and also non-virtual, so the only way to alias a dressing's
/// assets to the base zone's is a Harmony postfix here.
///
/// `GenerateBackgroundAssets` (`ActModel.cs:474`) passes the same identifier
/// into `BackgroundAssets`'s constructor, so this one postfix also keeps that
/// constructor -- which THROWS on a missing `layers` directory -- pointed at a
/// directory that exists.
///
/// WHAT IT DOES NOT TOUCH: `Id.Entry`. `ActModel.Title` is `new
/// LocString("acts", Id.Entry + ".title")` and `RunManager.UpdateRichPresence`
/// sends `Id.Entry`, so the act is NAMED Mondstadt while it is DRAWN as
/// Overgrowth. That split is the spike: the dressing proves the identity can
/// fork before any art is commissioned for it.
///
/// THE INLINE RISK IS REAL HERE, more than anywhere else in this arm. This is
/// a one-expression getter over a one-expression getter, which is the textbook
/// JIT inline candidate, and the decompile read flags the same hazard for
/// `MonsterModel.get_VisualsPath`. A BUILD CANNOT ANSWER IT. If it does not
/// take, the symptom is loud and immediate rather than subtle -- a run that
/// rolls Mondstadt throws `InvalidOperationException` out of
/// `BackgroundAssets`'s constructor on the first combat, because
/// `res://scenes/backgrounds/mondstadt/layers` does not exist -- and the
/// fallback is to ship the placeholder asset tree instead of aliasing.
///
/// THE ALIAS IS NOW CONDITIONAL, AND EVERY DRESSING HAS RETIRED IT IN
/// PRACTICE. `tools/gen_act_placeholders.py` ships a complete placeholder set
/// for all six faces -- five `_bg_NN_a` layer scenes, one `_fg_a`, a
/// background root, a rest site and three map PNGs each -- so
/// `TeyvatActAssets.HasDressedAssetsCached` answers TRUE for them in any build
/// whose pck was rebuilt, the postfix stands down, and the act is drawn from
/// OUR OWN FILES at the engine's own paths.
///
/// What is left here is the FALLBACK, and it is why the file is kept rather
/// than deleted: a dressing with no set of its own, or a build whose pck
/// predates one, still borrows the base zone's art rather than throwing out of
/// `BackgroundAssets`'s constructor on its first combat. The condition is a
/// pure function over a predicate (`TeyvatActAssets.HasDressedAssets`) so both
/// of its directions are pinned headlessly; the cached form below asks the
/// real `ResourceLoader` once per dressing, because this getter is read many
/// times a frame. `docs/current/operations/act-assets.md` states the set.
/// </summary>
[HarmonyPatch(typeof(ActModel), "get_FilePathIdentifier")]
internal static class ActModel_FilePathIdentifier_TeyvatAlias_Patch
{
    /// <summary>
    /// Keyed on the INSTANCE's own id, not on the run's current act. A
    /// dressing's asset paths must alias wherever they are read -- the map
    /// screen, `PreloadManager.LoadActAssets`, a run-history row -- and some
    /// of those read an act that is not the current one.
    /// </summary>
    private static void Postfix(ActModel __instance, ref string __result)
    {
        if (!TeyvatFrame.Enabled || __instance == null)
        {
            return;
        }

        var entry = __instance.Id.Entry;
        if (!TeyvatFrame.AssetAlias.TryGetValue(entry, out var aliased))
        {
            return;
        }

        // THE SET WINS WHEN IT IS THERE. Asked of the pack rather than of a
        // table, because "did the pck get rebuilt" is a fact about the
        // installed build and not about this source tree -- a dressing whose
        // scenes are committed but whose pck is stale must fall back, not
        // throw.
        if (TeyvatActAssets.HasDressedAssetsCached(entry))
        {
            return;
        }

        __result = aliased;
    }
}
