using System;
using BaseLib.Abstracts;
using BaseLib.Utils.NodeFactories;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;
using Log = MegaCrit.Sts2.Core.Logging.Log;

namespace LaneD.EnemySeam;

/// <summary>
/// Lane D spike: replace ONE ordinary base enemy's PRESENTATION with original
/// geometric proof art, changing no mechanics and overwriting no base
/// resource.
///
/// THIS DECIDES NOTHING. Which enemy (if any) should ever be re-presented, and
/// what it should look like, are [USER]'s calls. <see cref="TargetEntry"/>
/// below names a subject for the PROOF only; it is not a mapping, and the
/// handoff note carries it as a numbered question.
///
/// WHY THIS IS A HARMONY PATCH AND NOT AN API. There is no
/// "ReplaceMonsterVisuals(id, path)" in sts2.dll or in BaseLib (S13 non-finding
/// 4). BaseLib's own <c>CustomMonsterModel</c> route only serves monsters the
/// mod itself declares -- a BASE monster is not one, so the only seam is the
/// engine member the base monster reads.
///
/// THE SEAM. <c>MonsterModel.VisualsPath</c> (protected virtual) is the sole
/// source of the creature scene string and is read at exactly two sites: the
/// combat preloader and <c>CreateVisuals</c>. BaseLib already proves it is
/// patchable -- <c>BaseLib.Abstracts.VisualsPath</c> is
/// <c>[HarmonyPatch(typeof(MonsterModel), "VisualsPath", MethodType.Getter)]</c>
/// with a prefix that sets <c>__result</c> and returns false. Its prefix gates
/// on <c>__instance is CustomMonsterModel</c> and returns TRUE (falls through)
/// for base monsters, so base instances are unclaimed and this prefix takes
/// one of them uncontested.
///
/// WHY BOTH PATCHES. <see cref="VisualsPathPatch"/> alone would leave the base
/// <c>CreateVisuals</c> calling <c>GetScene(path).Instantiate&lt;NCreatureVisuals&gt;()</c>
/// on a SCRIPT-LESS scene, which only becomes an NCreatureVisuals if BaseLib's
/// scene-conversion registry has been told about the path.
/// <see cref="CreateVisualsPatch"/> removes that dependency by calling
/// BaseLib's factory directly -- the same call Klee.cs:238 already ships for
/// the player-character scene. The path patch is still wanted, because it is
/// the one the PRELOADER reads: without it the proof scene is a cache miss
/// ("Asset not cached") while the unused base scene is warmed instead.
/// <see cref="Install"/> also registers the path for auto-conversion, so the
/// two routes agree.
///
/// FAILURE IS SOFT BY CONSTRUCTION. Every entry point falls through to base
/// behaviour when anything is missing or throws, and the engine's own
/// <c>CreateVisuals</c> try/catch degrades a bad scene to
/// res://scenes/creature_visuals/fallback.tscn -- a visible error scene plus a
/// Log.Error, not a crash.
/// </summary>
public static class NeutralEnemySeam
{
    /// <summary>Log prefix. Not a mod id: this spike is not a shipped mod.</summary>
    public const string Tag = "laneD-seam";

    /// <summary>
    /// The <c>ModelId.Entry</c> of the base monster this spike re-presents.
    ///
    /// "NIBBIT" is here because it is the simplest base enemy the engine trace
    /// followed end to end (single slot, three moves, no gimmick, first fight
    /// of the game), NOT because anything says this enemy should be replaced.
    /// One string, one place: changing the subject is a one-line edit and
    /// nothing else in this file knows the name.
    ///
    /// Entries are derived from the C# TYPE NAME
    /// (ModelDb.GetEntry -> StringHelper.Slugify), so this is also the save
    /// key -- which is why the seam only READS it and never writes one.
    /// </summary>
    public const string TargetEntry = "NIBBIT";

    /// <summary>
    /// The replacement scene, inside the mod's OWN res:// namespace.
    ///
    /// THIS PREFIX IS THE WHOLE OF "no global overwrite". Godot's
    /// ProjectSettings.LoadResourcePack replaces colliding res:// paths, so a
    /// pack that carried res://scenes/creature_visuals/&lt;id&gt;.tscn would
    /// overwrite the base scene for every player of every mod that loaded it.
    /// Serving a DIFFERENT string out of a namespaced pack leaves every base
    /// file untouched and every other monster resolving to base art.
    /// <see cref="RejectsBaseNamespace"/> is the machine check for that.
    /// </summary>
    public const string ProofScenePath = "res://laned/creature_visuals/proof_prism.tscn";

    /// <summary>Base scene root that a replacement must never be written to.</summary>
    public const string BaseCreatureVisualsRoot = "res://scenes/creature_visuals/";

    private static bool _registered;

    /// <summary>
    /// True when <paramref name="path"/> stays out of the base game's own
    /// scene namespace. Public so the harness and the source-contract test can
    /// assert the rule rather than trust the constant.
    /// </summary>
    public static bool RejectsBaseNamespace(string? path) =>
        path != null
        && !path.StartsWith(BaseCreatureVisualsRoot, StringComparison.Ordinal)
        && !path.StartsWith("res://scenes/", StringComparison.Ordinal);

    /// <summary>
    /// Does this seam claim <paramref name="model"/>?
    ///
    /// Three conditions, all necessary:
    /// 1. it is a monster with a resolved id;
    /// 2. its entry is exactly the one subject named above -- so every other
    ///    monster in the game is untouched, which is requirement (ii);
    /// 3. it is NOT a BaseLib CustomMonsterModel. Those belong to whichever mod
    ///    declared them and already have their own supported override
    ///    (CustomVisualPath). BaseLib prefixes id-derived entries with the
    ///    owning mod's prefix, so a collision is unlikely -- but "unlikely"
    ///    is not a reason to leave another mod's monster reachable from here.
    /// </summary>
    public static bool Claims(MonsterModel? model) =>
        model != null
        && model is not CustomMonsterModel
        && model.Id != null
        && string.Equals(model.Id.Entry, TargetEntry, StringComparison.Ordinal);

    /// <summary>
    /// How the seam asks whether a resource exists.
    ///
    /// THE ONE INJECTION POINT, and it exists for exactly one reason:
    /// <c>ResourceLoader.Exists</c> is a native Godot call, so the offline
    /// bite-check harness -- which loads sts2.dll in a bare .NET process with
    /// no Godot runtime -- cannot invoke it. The harness substitutes a stub
    /// before arming anything; the game never touches this field, and the
    /// default below is the real call.
    ///
    /// It is a LAMBDA, not a method group, deliberately: a method group would
    /// force the ResourceLoader type (and its native singleton lookup) to be
    /// resolved when this class is initialized, which is precisely what fails
    /// outside Godot. Inside a lambda the reference is resolved on first
    /// invocation, which in the harness never happens.
    /// </summary>
    public static Func<string, bool> SceneExistsProbe { get; set; } =
        path => ResourceLoader.Exists(path);

    /// <summary>
    /// The proof scene path if it actually resolves, else null.
    ///
    /// Null means "do nothing" everywhere it is consumed: a stale or missing
    /// pack must leave the base enemy looking exactly like a base enemy, not
    /// hand the engine a dead path. Mirrors KleePck.Path's contract
    /// (klee-mod/KleeCode/KleePck.cs:30-45), including logging the miss once.
    /// </summary>
    public static string? ResolveProofScene()
    {
        if (!SceneExistsProbe(ProofScenePath))
        {
            if (!_missLogged)
            {
                _missLogged = true;
                Log.Warn($"[{Tag}] proof scene missing: {ProofScenePath}. "
                       + "Pack not built or not deployed; the base enemy keeps its "
                       + "own art and this spike does nothing.");
            }

            return null;
        }

        return ProofScenePath;
    }

    private static bool _missLogged;

    /// <summary>
    /// One-time wiring that is NOT a Harmony patch: tell BaseLib's path-keyed
    /// conversion registry that this scene becomes an NCreatureVisuals. With
    /// it, even the engine's own Instantiate route yields the right node type;
    /// without it, only <see cref="CreateVisualsPatch"/> does.
    ///
    /// Registration is per PATH and a second registration for the same path
    /// overwrites the first (the first-campfire softlock, DECISIONS
    /// 2026-07-20), so this path is used by exactly one conversion target and
    /// registration happens once.
    /// </summary>
    public static void Install()
    {
        if (_registered)
        {
            return;
        }

        _registered = true;
        NodeFactory.RegisterSceneType<NCreatureVisuals>(ProofScenePath);
        Log.Info($"[{Tag}] registered {ProofScenePath} for NCreatureVisuals conversion; "
               + $"claiming MONSTER.{TargetEntry} presentation only.");
    }

    /// <summary>
    /// S13-a4. The path the PRELOADER and CreateVisuals both read.
    ///
    /// Priority.Low so BaseLib's prefix (default priority) runs first: a
    /// CustomMonsterModel is claimed and skipped there before this ever sees
    /// it, and a base monster falls through to here. Harmony skips remaining
    /// prefixes once one returns false, so the ordering is what makes the two
    /// compose rather than race.
    /// </summary>
    [HarmonyPatch(typeof(MonsterModel), "VisualsPath", MethodType.Getter)]
    internal static class VisualsPathPatch
    {
        [HarmonyPrefix]
        [HarmonyPriority(Priority.Low)]
        private static bool Prefix(MonsterModel __instance, ref string? __result)
        {
            if (!Claims(__instance))
            {
                return true;
            }

            var path = ResolveProofScene();
            if (path == null)
            {
                return true;
            }

            __result = path;
            return false;
        }
    }

    /// <summary>
    /// S13-a5. Build the node from the script-less proof scene through
    /// BaseLib's factory, which fills any named node the scene omits and
    /// returns a real NCreatureVisuals.
    ///
    /// A throw here returns TRUE rather than propagating: the base method then
    /// runs, and its own try/catch produces the engine's visible fallback
    /// scene. A spike must never be the reason a combat cannot start.
    /// </summary>
    [HarmonyPatch(typeof(MonsterModel), "CreateVisuals")]
    internal static class CreateVisualsPatch
    {
        [HarmonyPrefix]
        [HarmonyPriority(Priority.Low)]
        private static bool Prefix(MonsterModel __instance, ref NCreatureVisuals? __result)
        {
            if (!Claims(__instance))
            {
                return true;
            }

            var path = ResolveProofScene();
            if (path == null)
            {
                return true;
            }

            try
            {
                __result = NodeFactory<NCreatureVisuals>.CreateFromScene(path);
                Log.Info($"[{Tag}] MONSTER.{TargetEntry} visuals from {path}: "
                       + $"{__result?.GetType().Name ?? "null"}");
                return __result == null;
            }
            catch (Exception e)
            {
                Log.Error($"[{Tag}] proof scene {path} failed to build "
                        + $"({e.GetType().Name}: {e.Message}); falling through to base "
                        + "CreateVisuals, which has its own error-scene fallback.");
                return true;
            }
        }
    }
}
