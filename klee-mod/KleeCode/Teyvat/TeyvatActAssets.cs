using System;
using System.Collections.Concurrent;
using BaseLib.Extensions;
using Godot;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Teyvat;

/// <summary>
/// THE DRESSED ASSET SET, AND THE ONE QUESTION THE ALIAS PATCH ASKS.
///
/// `ActModel.FilePathIdentifier` is <c>Id.Entry.ToLowerInvariant()</c> and
/// five NON-VIRTUAL expression-bodied properties derive every dressing path
/// from it -- `RestSiteBackgroundPath`, the three `Map*BgPath`s and
/// `BackgroundScenePath` (`ActModel.cs:52-64`, `:248`). A subclass cannot
/// override one, so the spike aliased the identifier itself and a dressing
/// wore the base zone's clothes
/// (`review/records/teyvat-spike-build-2026-09-15.md` item 1).
///
/// THIS CLASS IS HOW THAT ALIAS RETIRES. `tools/gen_act_placeholders.py`
/// writes a complete placeholder set per dressing -- five `_bg_NN_a` layer
/// scenes, one `_fg_a`, a background root, a rest site and three map PNGs --
/// and <see cref="HasDressedAssets"/> is the single boolean that decides
/// whether the identifier is left alone (our files are there) or aliased
/// (they are not). `docs/current/operations/act-assets.md` is the shape.
///
/// ALL-OR-NOTHING, DELIBERATELY. `Rooms/BackgroundAssets`'s constructor throws
/// `InvalidOperationException` on a missing `layers` directory AND on a layer
/// file matching neither `_bg_NN` nor `_fg_`; the map PNGs and the rest-site
/// scene have no fallback at all. So a HALF-landed set must still take the
/// alias rather than half of each -- which is why the probe below asks three
/// questions and ands them, and why it asks the questions a broken set fails:
/// the first LAYER scene (the file `BackgroundAssets` scans for), the
/// background ROOT (the scene `NCombatBackground.Create` casts) and the REST
/// SITE (the scene `CreateRestSiteBackground` instantiates).
///
/// WHY NOT THE LAYERS DIRECTORY ITSELF. `ResourceLoader.Exists` answers for
/// RESOURCES, not directories -- `res://scenes/backgrounds/mondstadt/layers`
/// is not a resource and the call returns false for a tree that is perfectly
/// present. The first layer scene inside it is the cheapest true proxy, and it
/// is the exact file whose absence makes the constructor throw.
/// </summary>
public static class TeyvatActAssets
{
    /// <summary>
    /// `ActModel.BackgroundScenePath`'s own spelling
    /// (`SceneHelper.GetScenePath($"backgrounds/{id}/{id}_background")`),
    /// written out rather than asked of an act, because the alias patch runs
    /// INSIDE that property's getter.
    /// </summary>
    public static string BackgroundScenePath(string id) =>
        $"res://scenes/backgrounds/{id}/{id}_background.tscn";

    /// <summary>
    /// The first layer scene, which is `BackgroundAssets`'s own naming rule
    /// (`ActModel.GetFullLayerPath`, `:302`) at group 00 variant `a`.
    /// </summary>
    public static string FirstLayerPath(string id) =>
        $"res://scenes/backgrounds/{id}/layers/{id}_bg_00_a.tscn";

    /// <summary>`ActModel.RestSiteBackgroundPath`'s spelling.</summary>
    public static string RestSiteScenePath(string id) =>
        $"res://scenes/rest_site/{id}_rest_site.tscn";

    /// <summary>
    /// THE DECISION, as a pure function over a predicate so it can be pinned
    /// headlessly. `exists` is `ResourceLoader.Exists` in the game and a
    /// dictionary in the tests; `dressing` is the `Id.Entry` (`MONDSTADT`),
    /// lowercased here exactly as `FilePathIdentifier` lowercases it.
    ///
    /// A null predicate answers FALSE rather than throwing: "we could not ask"
    /// and "the set is not there" both mean keep the alias, which is the safe
    /// direction -- the alias points at a tree that is certainly present.
    /// </summary>
    public static bool HasDressedAssets(string dressing, Func<string, bool>? exists)
    {
        if (dressing == null || exists == null)
        {
            return false;
        }

        var id = dressing.ToLowerInvariant();
        return exists(FirstLayerPath(id))
            && exists(BackgroundScenePath(id))
            && exists(RestSiteScenePath(id));
    }

    /// <summary>
    /// The same question against the real pack, answered ONCE per dressing.
    ///
    /// `get_FilePathIdentifier` is read by the map screen, by
    /// `PreloadManager.LoadActAssets` and by every background and chest path,
    /// so the postfix over it must not do three `ResourceLoader.Exists` calls
    /// each time. The pack is merged by `ModManager` before any
    /// `[ModInitializer]` runs, so the answer cannot change inside a session.
    /// </summary>
    public static bool HasDressedAssetsCached(string dressing) =>
        _cache.GetOrAdd(dressing, d => HasDressedAssets(d, p => ResourceLoader.Exists(p)));

    private static readonly ConcurrentDictionary<string, bool> _cache = new();

    private static bool _registered;

    /// <summary>
    /// TEACH BaseLib TO CONVERT OUR BACKGROUND ROOTS, and build the factory
    /// that does it. Called once from <c>KleeMod.Initialize</c>, beside
    /// <see cref="TeyvatVisuals.RegisterStillPortraits"/>, and for the same
    /// reason at the same time: a registration is a write into a dictionary
    /// BaseLib owns from the moment it loads, and only has to precede the
    /// scene's first INSTANTIATION.
    ///
    /// THIS IS EB-760 A SECOND TIME, A SECOND TYPE.
    /// `NCombatBackground.Create` does
    /// `GetScene(path).Instantiate&lt;NCombatBackground&gt;()` -- it CASTS --
    /// and our background root is a script-less `Control`, because
    /// `NCombatBackground`'s script lives in the GAME's pack at
    /// `res://src/Core/Nodes/Rooms/NCombatBackground.cs` and a mod pck may not
    /// carry an `ext_resource type="Script"` row. The difference from the still
    /// portrait is that BaseLib ships six factories and NONE of them is for
    /// this type (`NodeFactory.Init`), so the registration alone would log
    /// "no factory exists for that type" and fall through to the same failed
    /// cast. <see cref="NCombatBackgroundFactory"/> is that missing factory.
    ///
    /// SKIPPING IS LOUD. A build whose pck predates the asset set has no such
    /// scene; registering a dead path would only put a misleading line in the
    /// boot log, and the alias patch is meanwhile keeping that dressing on the
    /// base zone's art, which is the correct behaviour and the message says so.
    /// </summary>
    public static void RegisterActBackgrounds()
    {
        if (!TeyvatFrame.Enabled || _registered)
        {
            return;
        }

        _registered = true;

        try
        {
            NCombatBackgroundFactory.Ensure();

            foreach (var dressing in TeyvatFrame.AssetAlias.Keys)
            {
                var id = dressing.ToLowerInvariant();
                if (!HasDressedAssetsCached(dressing))
                {
                    Log.Warn($"[{KleeMod.ModId}] teyvat: {dressing} has no complete asset set in "
                           + $"the pck ({FirstLayerPath(id)}); it keeps the "
                           + "get_FilePathIdentifier alias and draws the base zone's art "
                           + "(run tools/gen_act_placeholders.py, then tools/build_pck.ps1).");
                    continue;
                }

                BackgroundScenePath(id).RegisterSceneForConversion<NCombatBackground>();
            }
        }
        catch (Exception e)
        {
            // `TeyvatLoc.Inject`'s discipline: the arm losing a picture must
            // never cost the mod its boot.
            Log.Error($"[{KleeMod.ModId}] teyvat: act-background registration failed, a dressed "
                    + $"act will throw out of NCombatBackground.Create on its first combat: {e}");
        }
    }
}
