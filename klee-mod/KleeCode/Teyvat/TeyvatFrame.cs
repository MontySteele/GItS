using System;
using System.Collections.Generic;
using System.Reflection;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat;

/// <summary>
/// THE TEYVAT RUN FRAME ARM'S ONE FLAG AND ONE TABLE (R272, the frame packet
/// `review/active/teyvat-run-frame-2026-09-14.md` sec.4; the decompile read
/// `review/records/teyvat-spike-zone-read-2026-09-14.md` sec.7 is the design).
///
/// A SPIKE, AND IT SAYS SO. Nothing in this directory is a shipped surface, no
/// number here is measured, and the whole arm is behind
/// `-p:TeyvatFrame=true`, which no release or calibration deploy passes.
///
/// WHAT A DRESSING IS. One <see cref="ActModel"/> subclass standing at the
/// same <c>Index</c> as a base zone, whose <c>GenerateAllEncounters</c>
/// returns the base zone's OWN <c>EncounterModel</c> instances. Mechanics
/// cannot drift, because they are literally the same objects; what changes is
/// the act's <c>Id.Entry</c>, and every piece of dressing the engine derives
/// from that -- title, map colours, event pool, music -- follows for free.
///
/// THE THREE TABLES BELOW ARE THE WHOLE OF THE DRESSING. Every patch in
/// `Teyvat/Patches/` is a NO-OP unless the current act has an entry in one of
/// them, which is what keeps the base cast byte-identical when the flag is on
/// and a base zone happens to be current -- and, with the flag off, always.
/// </summary>
public static class TeyvatFrame
{
    /// <summary>
    /// The arm's default: <c>-p:TeyvatFrame=true</c> turns it on, and a
    /// release package never passes it.
    /// </summary>
    public const bool DefaultEnabled =
#if TEYVAT_FRAME
        true;
#else
        false;
#endif

    /// <summary>The master, and the only flag. Settable so one build can pin
    /// both sides of it.</summary>
    public static bool Enabled { get; set; } = DefaultEnabled;

    /// <summary>
    /// `Mondstadt` -- the <c>Id.Entry</c> of the dressing that stands where
    /// Overgrowth stands. Held as constants because four separate tables and
    /// three patches key on them, and a typo in any one of them would be a
    /// silent no-op rather than a compile error.
    /// </summary>
    public const string Mondstadt = "MONDSTADT";

    /// <summary>`Liyue` -- the dressing that stands where Underdocks stands.</summary>
    public const string Liyue = "LIYUE";

    /// <summary>
    /// `Natlan` -- act 2's first face (R273 pick 1 at its default, layout 1).
    ///
    /// ACTS 2 AND 3 ARE ONE ZONE WITH TWO FACES EACH. The base game ships
    /// exactly one zone at index 1 and one at index 2, so both act-2 dressings
    /// stand on the Hive and both act-3 dressings on Glory
    /// (`review/ruled/teyvat-nation-mapping-2026-09-14.md` sec.1). That is
    /// invisible from here -- a dressing is an `Id.Entry` and a row in the
    /// tables below, whatever it dresses -- and visible only in
    /// `Patches/ModelDbActsPatch`, which splices a pair in where one act was.
    /// </summary>
    public const string Natlan = "NATLAN";

    /// <summary>`Inazuma` -- act 2's second face, the Hive's other coat.</summary>
    public const string Inazuma = "INAZUMA";

    /// <summary>`Fontaine` -- act 3's first face, standing on Glory.</summary>
    public const string Fontaine = "FONTAINE";

    /// <summary>`Sumeru` -- act 3's second face, Glory's other coat.</summary>
    public const string Sumeru = "SUMERU";

    /// <summary>
    /// THE ASSET ALIAS, and it is a spike shortcut stated as one.
    ///
    /// `ActModel.FilePathIdentifier` is <c>Id.Entry.ToLowerInvariant()</c>,
    /// and it is the root of the combat background scene, the rest-site
    /// scene, the three map background PNGs and the chest rig. Two of those
    /// constructors THROW rather than fall back when their directory is
    /// missing (`Rooms/BackgroundAssets`'s ctor, and
    /// `PreloadManager.Cache.GetScene` on the rest site), so a dressing with
    /// no asset tree of its own cannot boot.
    ///
    /// For the spike a dressing therefore borrows the base zone's asset set
    /// whole: `Patches/ActFilePathIdentifierPatch` rewrites the identifier,
    /// and nothing else changes. A REAL dressing needs its own complete set
    /// -- a `scenes/backgrounds/mondstadt/layers` tree, a rest-site scene and
    /// three map PNGs -- and the alias row is deleted in the same commit that
    /// lands it. This is the one place where the spike is knowingly wearing
    /// the base zone's clothes.
    ///
    /// The identifier is aliased and the `Id.Entry` is NOT, deliberately:
    /// `ActModel.Title` reads `Id.Entry`, so the act's name on the map screen
    /// is the dressing's ("MONDSTADT.title" in the `acts` loc table) while its
    /// pictures are Overgrowth's.
    ///
    /// IT IS ALSO THE ARM'S DRESSING REGISTRY, and that is why every face is
    /// in here whether or not it needs the fallback. <see cref="IsDressing"/>
    /// is `AssetAlias.ContainsKey`, and it is what
    /// `Patches/MonsterNamePatch` and `Patches/PullNextEventPatch` ask before
    /// they dress anything -- so a face missing from this table would be
    /// published as an act, named by its loc row, and then silently unable to
    /// carry a monster name or an event substitution. The four act-2 and
    /// act-3 faces land here with no monster or event rows of their own yet;
    /// that is content and comes later.
    /// </summary>
    public static readonly IReadOnlyDictionary<string, string> AssetAlias =
        new Dictionary<string, string>(StringComparer.Ordinal)
        {
            [Mondstadt] = "overgrowth",
            [Liyue] = "underdocks",
            [Natlan] = "hive",
            [Inazuma] = "hive",
            [Fontaine] = "glory",
            [Sumeru] = "glory",
        };

    /// <summary>
    /// THE NAME TABLE: (dressing, monster loc key) -> the dressed string.
    ///
    /// The key is the argument `MonsterModel.L10NMonsterLookup` is called
    /// with, which for a monster's display name is `<c>Id.Entry + ".name"</c>`
    /// and for its banter is whatever that monster's own class passes. One
    /// table serves both, because the read established that this static is
    /// the ONLY constructor of monster loc strings in the game.
    ///
    /// SPIKE ITEM 3 IS ONE ROW. Nibbit becomes the Wooden Shield Hilichurl
    /// Guard in Mondstadt and nowhere else; in Overgrowth, in Liyue, and with
    /// the flag off, `L10NMonsterLookup` returns exactly what it returned
    /// before.
    /// </summary>
    public static readonly IReadOnlyDictionary<(string Dressing, string Key), string> MonsterNames =
        new Dictionary<(string, string), string>
        {
            [(Mondstadt, "NIBBIT.name")] = "Wooden Shield Hilichurl Guard",
        };

    /// <summary>
    /// THE INTENT TABLE: (dressing, the intent's loc key) -> the dressed
    /// string. Same shape as <see cref="MonsterNames"/> and the same
    /// discipline: an intent whose key is not in here reads exactly as it
    /// reads in the base game.
    ///
    /// SCOPED TO THE VERB AND NOT TO THE MONSTER, because the engine is:
    /// `AbstractIntent` builds `new LocString("intents", IntentPrefix +
    /// ".title")` with no monster in scope at all, so an intent word is
    /// per-ZONE or it is nothing. The frame packet sec.7.1's design view is
    /// that the per-monster MOVE titles carry the nation and the generic verbs
    /// do not -- so this table ships EMPTY, the patch that reads it is armed
    /// and inert, and the cost of turning it on is one row.
    /// </summary>
    public static readonly IReadOnlyDictionary<(string Dressing, string Key), string> IntentWords =
        new Dictionary<(string, string), string>();

    /// <summary>
    /// THE EVENT-PORTRAIT TABLE: a dressed event's `Id.Entry` -> the image the
    /// default event layout draws for it until one of its own is supplied.
    ///
    /// GENERATED (`TeyvatEventsGenerated.cs`'s `Portraits`), which is what
    /// closes EB-764's shape rather than its instance: a dressed event and its
    /// portrait row are emitted by the same run of
    /// `tools/gen_teyvat_events.py` from the same face file, so an event
    /// cannot reach the map without one. This alias is what the patch and the
    /// pins read.
    ///
    /// A REAL PORTRAIT IS A MEDIA-LEDGER ITEM and not a code change --
    /// `docs/current/operations/media.md` is the convention it lands under
    /// (one producer per out-path, declared encoding, `build_pck` before any
    /// deploy). `Patches/EventPortraitPatch` asks `ResourceLoader.Exists` of
    /// the DRESSED path first, so the day one is packaged it wins and the
    /// borrow stands down on its own.
    /// </summary>
    public static IReadOnlyDictionary<string, string> EventPortraits =>
        TeyvatGeneratedEvents.Portraits;

    /// <summary>
    /// THE STILL-PORTRAIT TABLE: (dressing, monster `Id.Entry`) -> the pck
    /// scene path that draws it, in place of the monster's Spine rig.
    ///
    /// Read by `Patches/MonsterVisualsPathPatch`, which falls through when the
    /// scene is not in the pack -- so a build whose pck was not rebuilt shows
    /// the base rig rather than a missing-resource crash.
    /// </summary>
    public static readonly IReadOnlyDictionary<(string Dressing, string Entry), string> StillPortraits =
        new Dictionary<(string, string), string>
        {
            [(Mondstadt, "NIBBIT")] = "res://teyvat/creature_visuals/hilichurl_guard.tscn",
        };

    /// <summary>
    /// The `Id.Entry` of the act the run is standing in, or null.
    ///
    /// EVERY patch in this directory asks exactly this and stores nothing:
    /// the dressing is never persisted, so it cannot desync, cannot need a
    /// save migration, and is identical on every peer in multiplayer because
    /// `StartRunLobby` rolls the act list once and ships the run state.
    ///
    /// DEFENSIVE TO THE POINT OF PARANOIA on purpose. These patches run on
    /// getters the compendium, the bestiary, the card-reward screen and a
    /// board being torn down all reach, and `RunManager.Instance` is null on
    /// every one of those paths outside a run. A throw inside a Harmony
    /// postfix on `get_VisualsPath` would take the whole creature with it.
    /// </summary>
    public static string? CurrentActEntry
    {
        get
        {
            if (!Enabled)
            {
                return null;
            }

            try
            {
                var manager = RunManager.Instance;
                if (manager == null || !manager.IsInProgress)
                {
                    return null;
                }

                return (RunStateGetter?.Invoke(manager, null) as RunState)?.Act?.Id.Entry;
            }
            catch (Exception)
            {
                return null;
            }
        }
    }

    /// <summary>
    /// `RunManager.State`'s getter, resolved once by reflection.
    ///
    /// THE READ'S DESIGN SAID `RunManager.Instance.State.Act.Id.Entry` AND
    /// THAT MEMBER IS PRIVATE (`Runs/RunManager.cs:265`,
    /// `private RunState? State { get; set; }`). The decompile prints private
    /// members like public ones, so the design read as free and is not; the
    /// whole public surface of `RunManager` exposes no act
    /// (`IsInProgress` is the only thing that even admits a run exists).
    ///
    /// A cached getter rather than a `Traverse` per call, because these
    /// patches sit on `get_VisualsPath` and `L10NMonsterLookup`, which the
    /// combat UI reaches many times a frame.
    ///
    /// NULL IS A SUPPORTED ANSWER. `ResolvePropertyGetter` records a miss and
    /// returns null when the member is renamed by a game patch, and the
    /// property above then reports "no dressing" -- every patch in this arm
    /// stands down and the base game plays through. The miss is named in the
    /// Harmony boot report rather than swallowed.
    /// </summary>
    private static readonly MethodInfo? RunStateGetter =
        typeof(RunManager).GetProperty(
            "State", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public)
        ?.GetGetMethod(nonPublic: true);

    /// <summary>
    /// Is <paramref name="entry"/> one of this arm's dressings? Asked by the
    /// two patches that must stand down for a BASE act reached while the flag
    /// is on -- a coin that came up Overgrowth dresses nothing.
    /// </summary>
    public static bool IsDressing(string? entry) =>
        entry != null && AssetAlias.ContainsKey(entry);
}
