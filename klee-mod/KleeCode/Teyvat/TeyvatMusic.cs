using System;
using System.Collections.Generic;
using Godot;
using MegaCrit.Sts2.Core.Logging;

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
    /// The extensions the packager may produce, in preference order.
    /// `operations/media.md` sec.3: OGG Vorbis is the default, MP3 is
    /// accepted, WAV is never placed.
    /// </summary>
    public static readonly string[] Extensions = { ".ogg", ".mp3" };

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
    /// </summary>
    public static string? TrackFor(string? actEntry)
    {
        if (string.IsNullOrEmpty(actEntry))
        {
            return null;
        }

        var dir = Root + actEntry!.ToLowerInvariant();
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
                        // An exported pck can present an imported audio file
                        // under its source name or with a `.remap`/`.import`
                        // sidecar; `ResourceLoader.Exists` is the only
                        // trustworthy question about what will actually load.
                        var candidate = dir + "/" + name;
                        if (name.EndsWith(ext, StringComparison.OrdinalIgnoreCase)
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
    /// IDEMPOTENT. `UpdateMusic` runs on every room change, and re-creating
    /// the player each time would restart the track at every campfire. If the
    /// node is already there playing the same stream, this does nothing at
    /// all, which is also the answer to "surviving a combat start, a rest site
    /// and the map screen" -- those are room changes, not scene changes.
    /// </summary>
    public static bool Play(Node? host, string? actEntry)
    {
        var track = TrackFor(actEntry);
        if (host == null || track == null)
        {
            return false;
        }

        try
        {
            var existing = host.GetNodeOrNull<AudioStreamPlayer>(PlayerNodeName);
            if (existing != null)
            {
                if (existing.Stream?.ResourcePath == track)
                {
                    if (!existing.Playing)
                    {
                        existing.Play();
                    }

                    return true;
                }

                existing.QueueFree();
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
            Log.Info($"[{KleeMod.ModId}] teyvat: playing packaged track {track}; "
                   + "the act's FMOD music is stopped for its duration.");
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
        if (host == null)
        {
            return;
        }

        try
        {
            host.GetNodeOrNull<AudioStreamPlayer>(PlayerNodeName)?.QueueFree();
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] teyvat: could not stop the packaged track: {e.Message}");
        }
    }
}
