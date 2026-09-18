using System;
using System.Collections.Generic;
using Godot;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Rooms;

namespace KleeMod.Teyvat;

/// <summary>
/// SPIKE ITEM 4.4 -- A PACKAGED TRACK IN PLACE OF THE ACT'S FMOD MUSIC.
///
/// THE FINDING FIRST, BECAUSE IT DECIDES THE SHAPE: **there is no FMOD bus and
/// no duck call in the managed assembly.** A grep of the whole decompile for
/// `Bus`, `Snapshot`, `Duck`, `setVolume` finds nothing; the audio namespaces
/// are three files (`Core.Audio/FmodSfx.cs` -- a bag of `const string` event
/// paths -- `Core.Audio/DamageSfxType.cs`, and
/// `Core.Nodes.Audio/NAudioManager.cs`), and every FMOD call in the game goes
/// out through a Godot node with `Node.Call("play_music", ...)` /
/// `Call("update_music", ...)` -- a GDExtension surface Harmony cannot reach.
///
/// The only volume lever in managed code is `NAudioManager.SetMasterVol` and
/// its three siblings (`SetSfxVol`, `SetAmbienceVol`, `SetBgmVol`), each of
/// which is `_audioNode.Call("set_bgm_volume", Mathf.Pow(volume, 2f))`. Those
/// are the OPTIONS-SCREEN SLIDERS: global, persistent, and with no paired
/// fade-and-restore helper. Writing one from a patch would leave a player's
/// music slider at zero after the arm was turned off, which is a defect and
/// not a duck.
///
/// SO THE DUCK IS `NRunMusicController.StopMusic()`, the game's own stop, and
/// it is total rather than partial: the act's FMOD track stops and the Godot
/// `AudioStreamPlayer` below is the only thing playing. Ambience is
/// deliberately LEFT ALONE -- `UpdateAmbience` runs on its own path off
/// `AmbientSfx`, and a nation reading as the same place with a different tune
/// over it is the better default. If a partial duck is ever wanted, it needs
/// either an FMOD bank of our own or a GDScript-side helper in the pck; both
/// are out of a spike's scope and both are named in the report.
///
/// AND IT DOES NOTHING WHEN THERE IS NO TRACK. `TrackFor` returns null unless
/// a file is actually in the pack under `res://teyvat/music/&lt;act&gt;/`, and every
/// entry point below leads with that question. No audio file is added by this
/// commit, so on today's tree the whole arm is a pair of postfixes that
/// return immediately -- which is exactly what a skeleton has to be able to
/// prove.
///
/// AND IT RETURNS SILENTLY NOW (`EB-758`). The first cut asked the absence
/// question with `DirAccess.GetFilesAt`, which is an `ERR_FAIL_*_MSG` on a
/// missing directory: the arm's control flow fell through as designed and the
/// engine logged an ERROR with a 31-frame backtrace anyway. The lookup leads
/// with `DirAccess.DirExistsAbsolute` instead, which answers false without
/// printing, so no Godot node and no logging engine call is reached at all on
/// the no-track path. `DirectoryExists` carries the reasoning and the Godot
/// source both claims rest on.
///
/// WHERE THE FILE COMES FROM: `docs/current/operations/media.md` sec.1 puts
/// [USER]'s tracks at `media/out/music/&lt;act-or-scene&gt;/&lt;track&gt;.ogg`, gitignored,
/// one ledger row each in `media/MUSIC.tsv`. Its sec.7 leaves the pck path to
/// this spike; the answer is `res://teyvat/music/&lt;act-or-scene&gt;/`, a namespace
/// of its own rather than `res://klee/`, because the frame's media is not one
/// character's. `&lt;act-or-scene&gt;` is the act's `Id.Entry` lowercased, which is
/// `mondstadt` and `liyue` -- the ledger's own `act1_mondstadt` naming is one
/// packager-side rename away and is the packager's business, not this file's.
/// </summary>
public static class TeyvatMusic
{
    /// <summary>The pck namespace the packager writes into. One producer, one
    /// out-path (`operations/media.md` sec.1's rule).</summary>
    public const string Root = "res://teyvat/music/";

    /// <summary>The name of the node this arm adds under the run's music
    /// controller. Named, not anonymous, so a second call recognises its own
    /// work and an operator reading the remote scene tree knows whose node it
    /// is -- `Vfx/StaticPortraitIdle.PivotName`'s reason exactly.</summary>
    public const string PlayerNodeName = "TeyvatTrack";

    /// <summary>
    /// IS ONE OF OUR PLAYERS RUNNING RIGHT NOW? The single gate every crash
    /// guard in `Patches/RunMusicPatch` reads.
    ///
    /// It means exactly one thing: **the arm has stopped the game's FMOD music
    /// event and is playing a packaged track over the silence, so the game's
    /// music event instance has been RELEASED, and any later call that
    /// forwards a parameter to that instance is a native crash.** The patch's
    /// header carries the measured proxy surface and the three methods that
    /// forward one.
    ///
    /// NOT the same question as <see cref="TeyvatFrame.Enabled"/>, and the
    /// guards must never be gated on the arm instead: a session that turns the
    /// arm off mid-run still has our player in the tree and the game's event
    /// still released until the next teardown. A crash guard never sits behind
    /// the flag that created the thing being guarded -- the rule the
    /// `StopMusic` postfix already follows.
    ///
    /// Set by <see cref="Play"/> on a true return and cleared by
    /// <see cref="Stop"/>. A plain static because the whole audio path is
    /// Godot's main thread.
    /// </summary>
    public static bool IsArmedPlaying { get; private set; }

    /// <summary>Put <see cref="IsArmedPlaying"/> back to false without a tree.
    /// For tests only, beside <see cref="ResetProbes"/>; the mod reaches it
    /// through <see cref="Stop"/>.</summary>
    public static void ClearArmedPlaying() => IsArmedPlaying = false;

    /// <summary>
    /// The extensions the packager may produce, in preference order.
    /// `operations/media.md` sec.3: OGG Vorbis is the default, MP3 is
    /// accepted, WAV is never placed.
    /// </summary>
    public static readonly string[] Extensions = { ".ogg", ".mp3" };

    // ---------------------------------------------------------------
    // EB-814: THE SLOT VOCABULARY, AND IT IS CLOSED.
    // ---------------------------------------------------------------

    /// <summary>A face-scoped slot, as a `&lt;face&gt;/&lt;slot&gt;` directory.
    /// `combat` is also the FALLBACK for the other three -- see
    /// <see cref="TrackFor(string?, string)"/>.</summary>
    public const string SlotCombat = "combat";

    /// <inheritdoc cref="SlotCombat"/>
    public const string SlotElite = "elite";

    /// <inheritdoc cref="SlotCombat"/>
    public const string SlotBoss = "boss";

    /// <summary>The out-of-combat face slot: the map screen, an event room, a
    /// treasure room, and a combat room whose fight is over.</summary>
    public const string SlotMap = "map";

    /// <summary>The main menu. GLOBAL: there is no run and no act there, so it
    /// is the slot that proves the grammar needs two shapes.</summary>
    public const string SlotMenu = "menu";

    /// <summary>The merchant. GLOBAL by choice, not by necessity: a shop
    /// reading the same in every nation is the better default, and one row is
    /// cheaper to veto than six.</summary>
    public const string SlotShop = "shop";

    /// <summary>The rest site. GLOBAL, for <see cref="SlotShop"/>'s reason.</summary>
    public const string SlotRest = "rest";

    /// <summary>
    /// The four slots that hang under a face. Ordered as they are read rather
    /// than alphabetically: the combat slot first because it is the fallback.
    /// </summary>
    public static readonly string[] FaceSlots = { SlotCombat, SlotElite, SlotBoss, SlotMap };

    /// <summary>The three slots that resolve to a bare directory with no
    /// dressing at all.</summary>
    public static readonly string[] GlobalSlots = { SlotMenu, SlotShop, SlotRest };

    /// <summary>Is this one of the bare-name slots? Asked by
    /// <see cref="TeyvatFrame.MediaScene(string?, string?)"/> BEFORE it looks
    /// for a face, which is how `menu` answers outside a run.</summary>
    public static bool IsGlobalSlot(string? slot) =>
        slot != null && Array.IndexOf(GlobalSlots, slot) >= 0;

    /// <summary>Is this one of the `&lt;face&gt;/&lt;slot&gt;` slots?</summary>
    public static bool IsFaceSlot(string? slot) =>
        slot != null && Array.IndexOf(FaceSlots, slot) >= 0;

    /// <summary>
    /// WHICH SLOT A ROOM ASKS FOR, and this table is the arm's one room
    /// decision (`research/sts2-music-map-2026-09-17.md` sec.4).
    ///
    /// IT IS DELIBERATELY NOT `NRunMusicController.GetTrack`. The game's table
    /// has ten values because they are positions of ONE FMOD parameter on one
    /// event -- a crossfade inside a track. Ours are seven separate files, so
    /// the only distinctions worth making are the ones worth a different piece
    /// of music.
    ///
    /// THE ONE PLACE THE TWO DELIBERATELY DISAGREE is a won fight. `GetTrack`
    /// tests `IsCombatRoom() &amp;&amp; !CombatManager.IsInProgress` FIRST and
    /// moves to `CombatEnd`; we hold the room's combat slot until the room
    /// changes, because a parameter move is a crossfade and a slot move is a
    /// file swap, and restarting the music under a player reading their card
    /// rewards is worse than letting the loop run.
    ///
    /// A null room -- outside a run, mid-transition, or a reflection getter a
    /// game patch renamed -- answers the out-of-combat slot, which is the safe
    /// direction: the map loop under a boss is a shrug, the boss theme on the
    /// map screen is a bug report.
    /// </summary>
    public static string SlotFor(RoomType? room) => room switch
    {
        RoomType.Boss => SlotBoss,
        RoomType.Elite => SlotElite,
        RoomType.Monster => SlotCombat,
        RoomType.Shop => SlotShop,
        RoomType.RestSite => SlotRest,
        _ => SlotMap,
    };

    /// <summary>
    /// THE SUFFIX AN EXPORTED PACK ACTUALLY CARRIES, and the only thing a
    /// `DirAccess` listing of a packed music directory shows.
    ///
    /// MEASURED, NOT ASSUMED (MegaDot 4.5.1 headless, with
    /// `tools/build_pck.ps1`'s own `project.godot` and export preset).
    /// Importing `teyvat/music/act1_mondstadt/tone.ogg` and exporting packs
    /// exactly two entries for it --
    /// `.godot/imported/tone.ogg-65b6e61f5da027ff5c3e1a48630c2f25.oggvorbisstr`
    /// and `teyvat/music/act1_mondstadt/tone.ogg.import` -- and NOT the `.ogg`
    /// itself. With that pack mounted:
    /// <list type="bullet">
    /// <item>`DirAccess.get_files_at(".../act1_mondstadt")` returns
    /// `["tone.ogg.import"]`;</item>
    /// <item>`ResourceLoader.exists(".../tone.ogg")` is TRUE and the load
    /// returns an `AudioStreamOggVorbis`;</item>
    /// <item>`ResourceLoader.exists(".../tone.ogg.import")` is FALSE.</item>
    /// </list>
    ///
    /// So the name the enumeration hands back is never the name that loads, and
    /// the first cut of <see cref="TrackFor"/> -- which tested the LISTED name's
    /// extension against <see cref="Extensions"/> -- could not have matched a
    /// packaged track at all. The packager solves the same class of problem for
    /// `.tscn` with `export/convert_text_resources_to_binary=false`; the audio
    /// importers have no equivalent "ship it as source" switch, so this half of
    /// the repair belongs to the reader.
    ///
    /// Stripping is unconditional rather than guarded on "is this a pack",
    /// because a file whose name really ends in `.import` is not a track under
    /// any arrangement, and a loose `.ogg` (an editor run, or any future
    /// loose-file route) passes through untouched.
    /// </summary>
    public const string ImportSuffix = ".import";

    /// <summary>Directory lookups are cached: these sit on a path the run
    /// music controller reaches on every room change, and a `DirAccess` walk
    /// per room would be a real cost for an answer that cannot change inside a
    /// session.</summary>
    private static readonly Dictionary<string, string?> Cache = new(StringComparer.Ordinal);

    // ---------------------------------------------------------------
    // EB-758: THE THREE ENGINE QUESTIONS, BEHIND DELEGATES.
    // ---------------------------------------------------------------

    /// <summary>
    /// EB-758. **`DirAccess.GetFilesAt` PRINTS when the directory is absent**,
    /// and absent is the normal case on a tree with no track packaged. Godot 4's
    /// `DirAccess::get_files_at` is
    /// `Ref&lt;DirAccess&gt; da = DirAccess::open(p_path);`
    /// `ERR_FAIL_COND_V_MSG(da.is_null(), PackedStringArray(), vformat("Couldn't open directory at path \"%s\".", p_path));`
    /// — an `ERR_FAIL_*_MSG` macro, so a miss is an engine ERROR with a full
    /// backtrace. That is exactly the line the spike proof recorded
    /// (`review/records/teyvat-spike-proofs-2026-09-15.md`, item 4):
    /// `ERROR: Couldn't open directory at path "res://teyvat/music/mondstadt"`,
    /// 31 frames through `TrackFor` → `Play` → `UpdateMusicPostfix`.
    ///
    /// **`DirAccess.DirExistsAbsolute` is the silent question.** Its body is
    /// `Ref&lt;DirAccess&gt; d = DirAccess::create_for_path(p_dir); return d->dir_exists(p_dir);`
    /// — no `ERR_*` macro on the path, so a false answer costs a bool and no
    /// log line. It was chosen over the other candidate, `ResourceLoader.Exists`
    /// on a probe path, for two reasons: `Exists` needs a FILE NAME and the
    /// ledger owns the track's name (this file may not guess it — see
    /// `TrackFor`'s header), so a probe path would be a guess dressed as a
    /// check; and `DirExistsAbsolute` asks the question the code actually has,
    /// "is there a directory here to enumerate". The class reference documents
    /// neither method's absent-directory behaviour, so the answer is read off
    /// `core/io/dir_access.cpp` rather than off the docs page.
    ///
    /// **The cache was already in front of this and was not enough.** It bounds
    /// the noise to one ERROR per act id per boot rather than one per
    /// `UpdateMusic`; the guard takes it to zero, which is what the row's
    /// acceptance line ("logs nothing from the music patches across a
    /// three-fight soak") asks for.
    ///
    /// The delegates exist so the decision can be pinned HEADLESSLY. `DirAccess`
    /// and `ResourceLoader` are outside `KleeTests`' headless boundary
    /// (`KleeTests.csproj`: GodotSharp is copied so `sts2` resolves and nothing
    /// there may CALL it), so the only way a suite can assert "the no-track path
    /// returns before touching any Godot node" is to hand `TrackFor` a probe it
    /// can watch. Default-wired to the engine; a test that moves them restores
    /// them with <see cref="ResetProbes"/>.
    /// </summary>
    public static Func<string, bool> DirectoryExists { get; set; } = GodotDirectoryExists;

    /// <summary>The enumeration, reached only once <see cref="DirectoryExists"/>
    /// has said yes. See that member for why the guard sits in front of it.</summary>
    public static Func<string, string[]> ListFiles { get; set; } = GodotListFiles;

    /// <summary>Whether a named resource will actually load. Silent on absence
    /// by construction — `ResourceLoader::exists` returns a bool and prints
    /// nothing — so this one needed no repair; it is a delegate only so one
    /// headless pin can reach the whole lookup.</summary>
    public static Func<string, bool> ResourceExists { get; set; } = GodotResourceExists;

    // Static methods rather than lambdas assigned inline, so the three defaults
    // are named things a stack trace can show.
    private static bool GodotDirectoryExists(string path) => DirAccess.DirExistsAbsolute(path);

    private static string[] GodotListFiles(string path) => DirAccess.GetFilesAt(path);

    private static bool GodotResourceExists(string path) => ResourceLoader.Exists(path);

    /// <summary>Put the three probes back on the engine. For tests only; the
    /// mod never calls it.</summary>
    public static void ResetProbes()
    {
        DirectoryExists = GodotDirectoryExists;
        ListFiles = GodotListFiles;
        ResourceExists = GodotResourceExists;
    }

    /// <summary>Drop the memoised per-directory answers. For tests only: inside
    /// a session the answer cannot change, which is the whole point of the
    /// cache.</summary>
    public static void ClearCache() => Cache.Clear();

    /// <summary>
    /// The packaged track for an act entry, or null if the pack has none.
    ///
    /// PURE AND NULL-RETURNING, never throwing: it is called from inside two
    /// Harmony postfixes on the audio path, and an exception there would take
    /// the run's music controller down with it.
    ///
    /// The directory is ENUMERATED rather than a filename being guessed,
    /// because the ledger owns the track's name and this code must not.
    /// Sorted, so a directory that somehow holds two tracks picks the same one
    /// every boot instead of whichever the filesystem offered first.
    ///
    /// AND THE DIRECTORY IS THE LEDGER'S NAME, NOT THE ACT ID'S.
    /// `operations/media.md` sec.1 files a track under `act1_mondstadt`;
    /// `tools/build_pck.ps1` copies that `scene` column through VERBATIM, one
    /// producer and one out-path, so the resolution is the reader's job. See
    /// <see cref="TeyvatFrame.MediaScene"/> for the derivation and for why the
    /// rename does not belong in the packager.
    /// </summary>
    public static string? TrackFor(string? actEntry) => TrackFor(actEntry, SlotCombat);

    /// <summary>
    /// The packaged track for a face's slot, or null if the pack has none.
    ///
    /// THE FALLBACK CHAIN IS THE POINT, and it has exactly three links
    /// (`EB-814`, media.md sec.1):
    ///
    ///   1. `&lt;face&gt;/&lt;slot&gt;` -- the filed track.
    ///   2. `&lt;face&gt;/combat` -- for an elite or boss slot with nothing filed.
    ///      Same nation, always.
    ///   3. null -- so <see cref="Play"/> returns false, the patch never calls
    ///      `StopMusic`, and THE GAME'S OWN FMOD TRACK PLAYS ON. Silence is
    ///      never an outcome here; the base game's music is.
    ///
    /// **A GLOBAL SLOT HAS NO LINK 2.** `menu`, `shop` and `rest` are not a
    /// nation's, and there is no face to fall back into -- `menu` has no run at
    /// all. Nothing filed means the game's own merchant or campfire progress
    /// plays, which is the right answer and not a gap.
    ///
    /// **NOTHING EVER FALLS ACROSS TO ANOTHER NATION.** That is the rule the
    /// chain exists to state: link 2 is the SAME face's combat loop or it is
    /// nothing.
    /// </summary>
    public static string? TrackFor(string? actEntry, string slot)
    {
        var found = Lookup(TeyvatFrame.MediaScene(actEntry, slot));
        if (found != null || IsGlobalSlot(slot) || slot == SlotCombat)
        {
            return found;
        }

        // Link 2. `MediaScene` is asked again rather than the string being
        // sliced, so the face's spelling has exactly one producer.
        return Lookup(TeyvatFrame.MediaScene(actEntry, SlotCombat));
    }

    /// <summary>
    /// One cached directory walk. Split out of <see cref="TrackFor"/> when the
    /// fallback chain arrived, because the chain asks the same question of two
    /// directories and the cache has to cover both.
    /// </summary>
    private static string? Lookup(string? scene)
    {
        // A base zone -- Overgrowth, or anything else that is not one of this
        // arm's faces -- answers null and returns HERE, before any Godot call:
        // an undressed run has no ledger scene and plays its own music. So does
        // a null or empty entry, which is `CurrentActEntry` outside a run, and
        // so does a slot outside the closed vocabulary.
        if (scene == null)
        {
            return null;
        }

        var dir = Root + scene;
        if (Cache.TryGetValue(dir, out var cached))
        {
            return cached;
        }

        string? found = null;
        try
        {
            // EB-758. THE GUARD, AND IT IS THE WHOLE FIX. `GetFilesAt` on a
            // missing directory is a logged engine ERROR with a backtrace, and
            // a missing directory is the normal case until a track is packaged.
            // `DirExistsAbsolute` asks the same question silently; see the
            // member's header for the Godot source both claims rest on.
            var names = DirectoryExists(dir) ? ListFiles(dir) : null;
            if (names != null)
            {
                Array.Sort(names, StringComparer.Ordinal);
                foreach (var ext in Extensions)
                {
                    foreach (var name in names)
                    {
                        // An exported pck presents an imported audio file ONLY
                        // as its `.import` sidecar -- measured; see
                        // ImportSuffix for the pack listing and the three
                        // ResourceLoader answers. Strip it, then ask
                        // `ResourceLoader.Exists`, which follows the import
                        // remap and is the only trustworthy question about what
                        // will actually load.
                        var resource = name.EndsWith(ImportSuffix, StringComparison.OrdinalIgnoreCase)
                            ? name.Substring(0, name.Length - ImportSuffix.Length)
                            : name;
                        var candidate = dir + "/" + resource;
                        if (resource.EndsWith(ext, StringComparison.OrdinalIgnoreCase)
                            && ResourceExists(candidate))
                        {
                            found = candidate;
                            break;
                        }
                    }

                    if (found != null)
                    {
                        break;
                    }
                }
            }
        }
        catch (Exception e)
        {
            // A missing directory is the NORMAL case today and must be silent
            // at INFO. Anything else is worth one line.
            Log.Warn($"[{KleeMod.ModId}] teyvat: music lookup failed for {dir}: {e.Message}");
        }

        Cache[dir] = found;
        return found;
    }

    /// <summary>
    /// Start (or leave running) the packaged track for <paramref name="actEntry"/>
    /// under <paramref name="host"/>, and answer whether the FMOD track should
    /// now be stopped.
    ///
    /// RETURNS FALSE AND TOUCHES NOTHING when there is no track. That is the
    /// acceptance condition of this item: with no file placed, the arm on, and
    /// the patches armed, the game's audio behaves exactly as it does today.
    ///
    /// IDEMPOTENT, AND THAT IS WHAT MAKES THE SLOTS AFFORDABLE. Five separate
    /// postfixes now call this (`Patches/RunMusicPatch`), several of them on
    /// the same room change, and a sixth calls it for the menu. If the node is
    /// already there playing the same stream, this does nothing at all -- so a
    /// room that resolves to the slot already playing is free, and only a slot
    /// CHANGE costs a new player.
    /// </summary>
    public static bool Play(Node? host, string? actEntry, string slot)
    {
        var track = TrackFor(actEntry, slot);
        if (host == null || track == null)
        {
            return false;
        }

        try
        {
            // Every player we ever made under this host, by name prefix rather
            // than exact name: a `QueueFree` on a slot change used to leave the
            // old node IN the tree until the end of the frame, so the new node
            // added under the same name was renamed by Godot (`TeyvatTrack2`),
            // the next lookup by exact name missed it, a third player was
            // added, and the renamed one kept playing underneath -- the map
            // track and the combat track together, from the second slot change
            // on (user look, 2026-09-17). Detaching synchronously keeps the
            // name free, and the prefix sweep reaps anything already leaked.
            AudioStreamPlayer? keep = null;
            foreach (var ours in OurPlayers(host))
            {
                if (keep == null && ours.Stream?.ResourcePath == track)
                {
                    keep = ours;
                    continue;
                }

                Detach(host, ours);
            }

            if (keep != null)
            {
                if (!keep.Playing)
                {
                    keep.Play();
                }

                IsArmedPlaying = true;
                return true;
            }

            var stream = ResourceLoader.Load<AudioStream>(track);
            if (stream == null)
            {
                return false;
            }

            var player = new AudioStreamPlayer
            {
                Name = PlayerNodeName,
                Stream = stream,
                // The mod's own tracks go out on Godot's music bus if the
                // project defines one and on Master otherwise; the FMOD buses
                // are not Godot buses and are unreachable from here either way.
                Bus = AudioServer.GetBusIndex("Music") >= 0 ? "Music" : "Master",
            };

            host.AddChild(player);
            player.Play();
            IsArmedPlaying = true;
            // The slot is in the line because `EB-814`'s acceptance is read off
            // this log: "a boss track plays in a boss fight and godot.log names
            // it". The resolved path alone would not say WHICH slot asked, and
            // a fallback to the face's combat loop would read as a correct boss
            // pick.
            Log.Info($"[{KleeMod.ModId}] teyvat: slot '{slot}' -> playing packaged track "
                   + $"{track}; the act's FMOD music is stopped for its duration.");
            return true;
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] teyvat: could not play {track}: {e}");
            return false;
        }
    }

    /// <summary>
    /// Stop and drop our player, if we made one. Called from the postfix on
    /// the game's own `StopMusic`, so the arm's track dies exactly where the
    /// act's track dies -- a run ending, a quit to menu.
    /// </summary>
    public static void Stop(Node? host)
    {
        // CLEARED FIRST AND UNCONDITIONALLY, ahead of the null check and ahead
        // of the sweep. The flag says "the game's music event is released
        // because ours is playing over it"; the moment the arm gives up that
        // claim -- even on a host it cannot reach to tidy -- the guards must
        // stop biting, or a session would silently lose the campfire ambience
        // and every boss parameter for good.
        IsArmedPlaying = false;

        if (host == null)
        {
            return;
        }

        try
        {
            foreach (var ours in OurPlayers(host))
            {
                Detach(host, ours);
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] teyvat: could not stop the packaged track: {e.Message}");
        }
    }

    /// <summary>Is this node one of ours? By NAME PREFIX, because Godot
    /// renames a child added under a name that is still taken
    /// (`TeyvatTrack` -> `TeyvatTrack2`), and an exact match would lose it.
    /// Pure, so the pin can run without a tree.</summary>
    public static bool IsOurPlayerName(string name) =>
        name.StartsWith(PlayerNodeName, StringComparison.Ordinal);

    /// <summary>Every `AudioStreamPlayer` under the host whose name is ours,
    /// snapshotted so the caller may detach while iterating.</summary>
    private static List<AudioStreamPlayer> OurPlayers(Node host)
    {
        var found = new List<AudioStreamPlayer>();
        foreach (var child in host.GetChildren())
        {
            if (child is AudioStreamPlayer player && IsOurPlayerName(player.Name))
            {
                found.Add(player);
            }
        }

        return found;
    }

    /// <summary>Stop it, take it out of the tree NOW so its name is free, then
    /// free it. `QueueFree` alone leaves the node in the tree until the end of
    /// the frame, which is the leak this file's history records.</summary>
    private static void Detach(Node host, AudioStreamPlayer player)
    {
        player.Stop();
        host.RemoveChild(player);
        player.QueueFree();
    }
}
