using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace KleeMod.Saves;

/// <summary>
/// GO-LIVE SAVE SAFETY (2026-10-22). [USER]: "1) I think it's the user's
/// responsibility to know you can't turn a mod off and still play the game.
/// If we can back up the run save, that would be ideal (the same way the
/// public vs beta branches of the game would do it). 2) As above, can we
/// separate the save files somehow? 3) Beta testers need to just be careful
/// about this and we can put a reminder on the beta page; public users
/// shouldn't need a warning."
///
/// Two mechanisms, both PURE here and armed in <c>SaveSafetyPatches.cs</c>:
///
/// 1. THE BETA'S OWN SAVE FOLDER. The game keeps modded play in
///    <c>steam/&lt;id&gt;/modded/</c> (0.111.0
///    <c>UserDataPathProvider.GetAccountDir</c>; vanilla play uses the account
///    root). The beta package (<c>WorkshopRelease.Variant == "beta"</c>)
///    renames that one segment to <see cref="BetaAccountDir"/>, so a beta run
///    (a Yae run above all, which the public package cannot load) and the
///    beta's progress never share a file with the public or dev mod. Every
///    save path the game builds, the Steam cloud paths included, goes through
///    that one method. The first beta boot copies the normal modded saves
///    across once (<see cref="MigrationPlan"/>), so a tester keeps progress.
///    With the beta off the game is back on <c>modded/</c>, untouched.
///
/// 2. THE TEYVAT RUN BACKUP. Every time the game writes a run save holding
///    one of our characters, the same bytes are kept beside it as
///    <c>current_run.teyvat.save</c> (local only). With the mod off, BaseLib
///    hides that run and a new vanilla run overwrites <c>current_run.save</c>;
///    once the mod is back on and NO run is open, the backup is put back
///    (<see cref="Decide"/>). It never writes over a live run, never brings
///    back a run that is in the run history (finished or abandoned), and never
///    restores a character this build does not register.
///
/// Known limit: the mod-off vanilla run still rewrites <c>progress.save</c>,
/// dropping our characters' rows in ancient, encounter and enemy stats. Run
/// stats come back with the run; those three tables do not.
/// </summary>
public static class SaveSafety
{
    /// <summary>The game's modded account folder (0.111.0).</summary>
    public const string ModdedAccountDir = "modded";

    /// <summary>The beta package's own account folder.</summary>
    public const string BetaAccountDir = "modded-teyvat-beta";

    /// <summary>The variant name whose saves move.</summary>
    public const string BetaVariant = "beta";


    /// <summary>Profiles the game keeps (0.111.0 loops 1..3); a save-file count, not a rule constant.</summary>
    private const int ProfileCount = 3;

    /// <summary>Run save names (0.111.0 <c>RunSaveManager</c>).</summary>
    public const string RunSave = "current_run.save";
    public const string MultiplayerRunSave = "current_run_mp.save";

    /// <summary>
    /// The account folder a path should use. Only the modded folder moves,
    /// and only in the beta; the vanilla root ("") never moves. PURE.
    /// </summary>
    public static string Redirect(string accountDir, string? variant) =>
        string.Equals(variant, BetaVariant, StringComparison.Ordinal)
        && string.Equals(accountDir, ModdedAccountDir, StringComparison.Ordinal)
            ? BetaAccountDir
            : accountDir;

    /// <summary>"current_run.save" -> "current_run.teyvat.save". PURE.</summary>
    public static string BackupName(string runSaveName)
    {
        const string ext = ".save";
        return runSaveName.EndsWith(ext, StringComparison.Ordinal)
            ? runSaveName[..^ext.Length] + ".teyvat" + ext
            : runSaveName + ".teyvat";
    }

    /// <summary>The backup path beside a run save path. PURE.</summary>
    public static string BackupPathFor(string runSavePath)
    {
        int slash = runSavePath.LastIndexOf('/');
        return slash < 0
            ? BackupName(runSavePath)
            : runSavePath[..(slash + 1)] + BackupName(runSavePath[(slash + 1)..]);
    }

    // ------------------------------------------------------- migration ---

    /// <summary>
    /// Does the beta folder need its one-time copy? Only when the beta has no
    /// profile.save yet and the normal modded folder has one. PURE.
    /// </summary>
    public static bool NeedsMigration(Func<string, bool> fileExists) =>
        !fileExists($"{BetaAccountDir}/profile.save")
        && fileExists($"{ModdedAccountDir}/profile.save");

    /// <summary>
    /// The files the one-time copy moves, account-relative, mirroring the
    /// game's own unmodded-to-modded copy (0.111.0
    /// <c>ModManager.CopyUnmoddedSaveFilesIfNeeded</c>) plus our run backups:
    /// profile.save, and per profile progress, prefs, both run saves, both
    /// Teyvat backups and the run history (oldest first, as the cloud quota
    /// expects). A file already in the beta folder is never overwritten.
    /// PURE.
    /// </summary>
    public static IReadOnlyList<(string From, string To)> MigrationPlan(
        Func<string, bool> fileExists, Func<string, IEnumerable<string>> historyFiles)
    {
        var plan = new List<(string, string)>();
        void Add(string rel)
        {
            string from = $"{ModdedAccountDir}/{rel}", to = $"{BetaAccountDir}/{rel}";
            if (fileExists(from) && !fileExists(to)) plan.Add((from, to));
        }

        Add("profile.save");
        for (int i = 1; i <= ProfileCount; i++)
        {
            string saves = $"profile{i}/saves";
            Add($"{saves}/progress.save");
            Add($"{saves}/prefs.save");
            Add($"{saves}/{RunSave}");
            Add($"{saves}/{MultiplayerRunSave}");
            Add($"{saves}/{BackupName(RunSave)}");
            Add($"{saves}/{BackupName(MultiplayerRunSave)}");
            foreach (var f in historyFiles($"{ModdedAccountDir}/{saves}/history")
                         .Where(f => f.EndsWith(".run", StringComparison.Ordinal))
                         .OrderBy(f => f.Length).ThenBy(f => f, StringComparer.Ordinal))
                Add($"{saves}/history/{f}");
        }
        return plan;
    }

    // ---------------------------------------------------------- backup ---

    /// <summary>A run save's identity: its start time and its characters.</summary>
    public sealed record RunHeader(long? StartTime, IReadOnlyList<string> CharacterIds);

    /// <summary>
    /// Read <c>start_time</c> and <c>players[].character_id</c> off a run
    /// save's JSON without the game's deserializer. Null when the text is not
    /// a run save. PURE.
    /// </summary>
    public static RunHeader? ReadHeader(string? json)
    {
        if (string.IsNullOrWhiteSpace(json)) return null;
        try
        {
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;
            if (root.ValueKind != JsonValueKind.Object) return null;
            long? start = root.TryGetProperty("start_time", out var st)
                          && st.ValueKind == JsonValueKind.Number
                          && st.TryGetInt64(out var v) ? v : null;
            var ids = new List<string>();
            if (root.TryGetProperty("players", out var players)
                && players.ValueKind == JsonValueKind.Array)
            {
                foreach (var p in players.EnumerateArray())
                {
                    if (p.ValueKind == JsonValueKind.Object
                        && p.TryGetProperty("character_id", out var c)
                        && c.ValueKind == JsonValueKind.String)
                        ids.Add(c.GetString()!);
                }
            }
            return new RunHeader(start, ids);
        }
        catch (JsonException)
        {
            return null;
        }
    }

    /// <summary>Does a run hold at least one of our characters? PURE.</summary>
    public static bool IsTeyvatRun(IEnumerable<string?> characterIds, ISet<string> ours) =>
        characterIds.Any(id => id != null && ours.Contains(id));

    /// <summary>Why a backup was or was not put back.</summary>
    public enum Verdict
    {
        Restore,
        NoBackup,
        LiveRunPresent,
        Unreadable,
        NotTeyvat,
        Finished,
        UnknownCharacter,
    }

    /// <summary>
    /// Put the Teyvat backup back as the run save? Only when no run save (nor
    /// the game's own .backup of one) exists, the backup reads, holds one of
    /// our characters, is not in the run history, and every character in it
    /// is registered in this build. PURE.
    /// </summary>
    public static Verdict Decide(bool runSaveExists, bool runSaveBackupExists,
                                 string? backupJson, Func<long, bool> inHistory,
                                 ISet<string> registered, ISet<string> ours)
    {
        if (backupJson == null) return Verdict.NoBackup;
        if (runSaveExists || runSaveBackupExists) return Verdict.LiveRunPresent;
        var header = ReadHeader(backupJson);
        if (header?.StartTime == null || header.CharacterIds.Count == 0) return Verdict.Unreadable;
        if (!IsTeyvatRun(header.CharacterIds, ours)) return Verdict.NotTeyvat;
        if (inHistory(header.StartTime.Value)) return Verdict.Finished;
        if (!header.CharacterIds.All(registered.Contains)) return Verdict.UnknownCharacter;
        return Verdict.Restore;
    }

    /// <summary>
    /// The game is deleting a run save; is it the run our backup holds (so the
    /// backup goes too)? Compared by start time. When the run being deleted
    /// cannot be read, the backup is kept: the history check still stops a
    /// finished run from coming back. PURE.
    /// </summary>
    public static bool SameRun(string? deletedJson, string? backupJson)
    {
        var a = ReadHeader(deletedJson);
        var b = ReadHeader(backupJson);
        return a?.StartTime != null && a.StartTime == b?.StartTime;
    }
}
