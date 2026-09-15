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
/// A REAL DRESSING DELETES THIS FILE. It is a scaffold that exists because the
/// spike commissions no art, and `TeyvatFrame.AssetAlias`'s table is the thing
/// that gets emptied, one row at a time, as each nation's asset set lands.
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

        if (TeyvatFrame.AssetAlias.TryGetValue(__instance.Id.Entry, out var aliased))
        {
            __result = aliased;
        }
    }
}
