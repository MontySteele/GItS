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
/// THIS CLASS IS HOW THAT ALIAS RETIRES -- FOR THE COMBAT BACKGROUND AND THE
/// MAP, AND FOR NOTHING ELSE. `tools/gen_act_placeholders.py`
/// writes a complete placeholder set per dressing, for all six of them --
/// five `_bg_NN_a` layer scenes, one `_fg_a`, a background root
/// and three map PNGs each --
/// and <see cref="HasDressedAssets"/> is the single boolean that decides
/// whether the identifier is left alone (our files are there) or aliased
/// (they are not). `docs/current/operations/act-assets.md` is the shape.
///
/// THE REST SITE IS NO LONGER PART OF THAT QUESTION (2026-09-17). We shipped
/// our own rest-site scene until then: a `RestSiteBG` `TextureRect` over our
/// plate plus an EMPTY `%RestSiteLighting` `Control`, which is all
/// `NRestSiteRoom._Ready`'s `GetNode&lt;Control&gt;("%RestSiteLighting")` asks
/// for. The base game keeps its WHOLE campfire inside that node -- ground
/// lighting particles, seven wall lights, `SteppedFire`, sparks, the log
/// highlights -- and a BASE character's campfire figure
/// (`Nodes.RestSite/NRestSiteCharacter._Ready`, which plays
/// `"&lt;zone&gt;_loop"` on a Spine rig by act index) evidently reaches into it.
/// Against our empty node the game HARD-CRASHED: native, no managed trace,
/// the log ending at "Preloading 'RestSite Room' Complete". [USER] reproduced
/// it twice on 2026-09-17 with the Silent at her first campfire; Klee never
/// crashed there, which is why it survived every proof we ran.
///
/// So a dressing now wears the base zone's ENTIRE rest scene
/// (`Patches/TeyvatRestSitePatch` aliases `RestSiteBackgroundPath`
/// unconditionally, whatever the rest of the set looks like) and only the
/// PLATE is ours, swapped into that scene's own `RestSiteBG` by a postfix on
/// `ActModel.CreateRestSiteBackground`. The plate is a texture, not a
/// completeness question: a missing one costs a picture, not a boot, so
/// <see cref="HasDressedAssets"/> does not ask about it either.
///
/// ALL-OR-NOTHING, DELIBERATELY. `Rooms/BackgroundAssets`'s constructor throws
/// `InvalidOperationException` on a missing `layers` directory AND on a layer
/// file matching neither `_bg_NN` nor `_fg_`; the map PNGs have no fallback at
/// all. So a HALF-landed set must still take the
/// alias rather than half of each -- which is why the probe below ands its
/// questions, and why it asks the questions a broken set fails: the first
/// LAYER scene (the file `BackgroundAssets` scans for), the background ROOT
/// (the scene `NCombatBackground.Create` casts), and -- as a belt, see
/// <see cref="FirstLayerRemapPath"/> -- that the pack carries no `.tscn.remap`
/// stub where that first layer should be.
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

    /// <summary>
    /// `ActModel.RestSiteBackgroundPath`'s spelling. NOTHING WE SHIP LIVES AT
    /// THIS PATH FOR A DRESSING any more -- it is here so the alias postfix
    /// can build the BASE zone's spelling (`overgrowth`, `hive`, `glory`), and
    /// so the tests can say in one line which scene a face gets.
    /// </summary>
    public static string RestSiteScenePath(string id) =>
        $"res://scenes/rest_site/{id}_rest_site.tscn";

    /// <summary>
    /// THE REST SCENE A FACE ACTUALLY GETS: always the base zone's, for every
    /// dressing, regardless of what else is in the pack.
    ///
    /// Returns null for anything that is not a dressing (every base zone,
    /// always), which is the postfix's "leave it alone". Pure, so both
    /// directions are pinned headlessly.
    /// </summary>
    public static string? BaseRestSiteScenePath(string? dressingEntry)
    {
        if (dressingEntry == null
            || !TeyvatFrame.AssetAlias.TryGetValue(dressingEntry, out var zone))
        {
            return null;
        }

        return RestSiteScenePath(zone);
    }

    /// <summary>
    /// OUR PLATE, the one thing a face still owns at a rest site. Written by
    /// `art/plan.tsv` (or `tools/gen_act_placeholders.py` as a gradient) at
    /// 1382x648, and swapped into the base scene's `RestSiteBG` whose rect is
    /// 2764.8 x 1296 with `expand_mode = 1` -- exactly the scaling our own
    /// scene did before it was deleted.
    /// </summary>
    public static string RestSitePlatePath(string id) =>
        $"res://teyvat/rest_site/{id}_rest_site_bg.png";

    /// <summary>
    /// THE NODE NAME THE PLATE GOES INTO, in the base game's own rest scenes.
    /// A direct child of the scene root in Overgrowth, Underdocks, the Hive
    /// and Glory alike. Reached with `GetNodeOrNull`: a zone that ever renames
    /// it costs us a picture, never a room.
    /// </summary>
    public const string RestSiteBgNode = "RestSiteBG";

    /// <summary>
    /// ROOT-LEVEL DECORATION THAT FIGHTS A FOREIGN PLATE, by name prefix.
    ///
    /// Overgrowth hangs six `Foliage*` `TextureRect`s and two
    /// `RestSiteForeground*` layers in front of its own background; Glory adds
    /// `stars*` particles and a `water_reflection*` sprite keyed to ITS
    /// horizon. Over a Mondstadt plate they are somebody else's trees.
    ///
    /// WHAT IS NOT ON THIS LIST IS THE POINT. `%RestSiteLighting` and
    /// everything under it stays -- that subtree IS the campfire and the thing
    /// the base character's Spine rig reaches into, which is the whole defect
    /// this file was rewritten for -- and so do `RestSiteLLog`, `RestSiteRLog`
    /// and `RestSiteFireLogs`, the logs the fire sits on. The hide pass walks
    /// the root's DIRECT children only, so it cannot reach into the lighting
    /// tree even by accident.
    /// </summary>
    public static readonly string[] PlateHidePrefixes =
    {
        "Foliage",
        "RestSiteForeground",
        "stars",
        "water_reflection",
    };

    /// <summary>
    /// THE HIDE DECISION as a pure function of a node name, so the list above
    /// and the thing it must never match are one assertion in
    /// `KleeTests/TeyvatFrameTests`.
    ///
    /// Ordinal and case-sensitive: these are scene node names dumped from the
    /// game's own pck, not user input, and a loose match here would put the
    /// campfire out.
    /// </summary>
    public static bool HiddenForPlate(string? nodeName)
    {
        if (string.IsNullOrEmpty(nodeName))
        {
            return false;
        }

        foreach (var prefix in PlateHidePrefixes)
        {
            if (nodeName!.StartsWith(prefix, StringComparison.Ordinal))
            {
                return true;
            }
        }

        return false;
    }

    /// <summary>
    /// THE REMAP STUB, whose PRESENCE is a disqualification.
    ///
    /// A Godot export with `editor/export/convert_text_resources_to_binary`
    /// left at its default packs each `.tscn` as a binary `.scn` plus a
    /// `<name>.tscn.remap` stub at the original path. `ResourceLoader.Exists`
    /// and `ResourceLoader.Load` both follow a remap transparently, so every
    /// question <see cref="HasDressedAssets"/> asks answers TRUE on such a
    /// pack -- and the set is still unusable, because `Rooms/BackgroundAssets`
    /// does not ask `ResourceLoader` anything. It `DirAccess.Open`s the layers
    /// directory and takes each `GetNext()` filename VERBATIM, so it builds
    /// `.../{id}_bg_00_a.tscn.remap`, a path with no loader. The preload marks
    /// it failed (`AssetLoadingSession.cs:235`) and
    /// `NCombatBackground.AddLayer`'s `GetScene` throws inside
    /// `CombatManager.SetUpCombat` -- combat never starts, which is a worse
    /// outcome than any missing picture. That is the blocking defect of
    /// `git show ecfa839d:review/records/teyvat-proofs-3-2026-09-15.md`.
    ///
    /// `tools/build_pck.ps1` now sets that project setting to false, matching
    /// the base game's own pack (173 raw `scenes/backgrounds/*/layers/*.tscn`
    /// entries, zero `.tscn.remap`), so on a correctly built pack this probe is
    /// false and costs one `Exists` call per dressing per session. It is kept
    /// as the BELT: if the export ever regains remaps, the dressing falls back
    /// to the base zone's art and the run is playable, instead of aborting on
    /// its first combat. Same safe direction as the null-predicate case above.
    /// </summary>
    public static string FirstLayerRemapPath(string id) =>
        FirstLayerPath(id) + ".remap";

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
    public static bool HasDressedAssets(string dressing, Func<string, bool>? exists,
                                        Func<string, bool>? fileExists = null)
    {
        if (dressing == null || exists == null)
        {
            return false;
        }

        var id = dressing.ToLowerInvariant();

        // ASKED WITH FileAccess, NOT ResourceLoader, and that is not a style
        // choice. `ResourceLoader.Exists` answers only for paths some loader
        // RECOGNIZES, and nothing recognizes `.remap` -- that is the engine's
        // own "No loader found for resource: ...tscn.remap (expected type:
        // unknown)". So the resource predicate would answer false for a stub
        // that is plainly in the pack. `FileAccess.FileExists` consults the
        // packed filesystem by literal path, which is the same view
        // `BackgroundAssets`'s `DirAccess` scan gets.
        //
        // A null `fileExists` means NOT ASKED rather than "no remap": the
        // remap stub is a belt against a mis-built pack, not part of the
        // completeness question, so a caller asking only about completeness
        // gets the answer it asked for. Every runtime caller supplies it.
        if (fileExists != null && fileExists(FirstLayerRemapPath(id)))
        {
            return false;
        }

        // THE REST SITE IS NOT ASKED ABOUT. It was, until 2026-09-17; the
        // scene it asked for is deleted and a face wears the base zone's
        // campfire whatever this answers. See the class remarks.
        return exists(FirstLayerPath(id))
            && exists(BackgroundScenePath(id));
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
        _cache.GetOrAdd(dressing, d => HasDressedAssets(
            d, p => ResourceLoader.Exists(p), p => FileAccess.FileExists(p)));

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
