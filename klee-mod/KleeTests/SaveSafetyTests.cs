using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using KleeMod.Saves;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Saves.Managers;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// GO-LIVE SAVE SAFETY (Saves/SaveSafety.cs, 2026-10-22): the beta's own
/// save folder and the Teyvat run backup. The rules are PURE and pinned
/// here; the game-facing hooks are pinned by name against the game they
/// patch, so a game update that moves one fails here and not in a player's
/// save folder.
/// </summary>
public class SaveSafetyTests
{
    private const string Klee = "CHARACTER.KLEEMOD-KLEE";
    private const string Yae = "CHARACTER.KLEEMOD-YAE";
    private const string Ironclad = "CHARACTER.IRONCLAD";

    private static readonly HashSet<string> Ours = new() { Klee, Yae };
    private static readonly HashSet<string> RegisteredAll = new() { Klee, Yae, Ironclad };
    private static readonly HashSet<string> RegisteredNoYae = new() { Klee, Ironclad };

    private static string Run(long start, params string[] chars) =>
        "{\"schema_version\":1,\"start_time\":" + start + ",\"players\":["
        + string.Join(",", chars.Select(c => "{\"character_id\":\"" + c + "\",\"current_hp\":70}"))
        + "]}";

    // ------------------------------------------------------ the folder ---

    [Fact]
    public void Only_the_beta_moves_and_only_the_modded_folder()
    {
        Assert.Equal("modded-teyvat-beta", SaveSafety.Redirect("modded", "beta"));
        Assert.Equal("modded", SaveSafety.Redirect("modded", "public"));
        Assert.Equal("modded", SaveSafety.Redirect("modded", null));      // dev and seat builds
        Assert.Equal("", SaveSafety.Redirect("", "beta"));                // vanilla root never moves
    }

    [Fact]
    public void Dev_build_has_no_variant_so_its_saves_stay_put()
    {
        Assert.Null(WorkshopRelease.Variant);
        Assert.Equal("modded", SaveSafety.Redirect("modded", WorkshopRelease.Variant));
    }

    [Fact]
    public void The_game_still_names_its_modded_folder_as_we_expect()
    {
        bool was = UserDataPathProvider.IsRunningModded;
        try
        {
            UserDataPathProvider.IsRunningModded = true;
            // Through the live (possibly patched) method: a dev build leaves it alone.
            Assert.Equal(SaveSafety.ModdedAccountDir, UserDataPathProvider.GetAccountDir());
            Assert.Equal("", UserDataPathProvider.GetAccountDir(false));
            Assert.Equal("modded/profile1/saves/current_run.save",
                         RunSaveManager.GetRunSavePath(1, SaveSafety.RunSave));
            Assert.Equal("modded/profile2/saves/history",
                         RunHistorySaveManager.GetHistoryPath(2));
        }
        finally
        {
            UserDataPathProvider.IsRunningModded = was;
        }
    }

    [Fact]
    public void Migration_runs_once_only_when_the_beta_folder_is_new()
    {
        Assert.True(SaveSafety.NeedsMigration(p => p == "modded/profile.save"));
        Assert.False(SaveSafety.NeedsMigration(p => true));               // beta already has one
        Assert.False(SaveSafety.NeedsMigration(p => false));              // nothing to copy
    }

    [Fact]
    public void Migration_copies_the_games_files_and_never_overwrites()
    {
        var files = new HashSet<string>
        {
            "modded/profile.save",
            "modded/profile1/saves/progress.save",
            "modded/profile1/saves/prefs.save",
            "modded/profile1/saves/current_run.save",
            "modded/profile1/saves/current_run.teyvat.save",
            "modded/profile1/saves/history/1700000000.run",
            "modded/profile1/saves/history/999.run",
            "modded/profile2/saves/progress.save",
            "modded-teyvat-beta/profile2/saves/progress.save",   // already there: kept
        };
        var history = new Dictionary<string, string[]>
        {
            ["modded/profile1/saves/history"] = new[] { "1700000000.run", "999.run", "notes.txt" },
        };
        var plan = SaveSafety.MigrationPlan(files.Contains,
            d => history.TryGetValue(d, out var f) ? f : Array.Empty<string>());

        var to = plan.Select(p => p.To).ToList();
        Assert.Equal(new[]
        {
            "modded-teyvat-beta/profile.save",
            "modded-teyvat-beta/profile1/saves/progress.save",
            "modded-teyvat-beta/profile1/saves/prefs.save",
            "modded-teyvat-beta/profile1/saves/current_run.save",
            "modded-teyvat-beta/profile1/saves/current_run.teyvat.save",
            "modded-teyvat-beta/profile1/saves/history/999.run",          // oldest first
            "modded-teyvat-beta/profile1/saves/history/1700000000.run",
        }, to);
        Assert.All(plan, p => Assert.StartsWith("modded/", p.From));
        Assert.Equal(plan.Select(p => p.From.Substring("modded/".Length)),
                     plan.Select(p => p.To.Substring("modded-teyvat-beta/".Length)));
    }

    // ------------------------------------------------------ the backup ---

    [Fact]
    public void Backup_sits_beside_the_run_save()
    {
        Assert.Equal("current_run.teyvat.save", SaveSafety.BackupName("current_run.save"));
        Assert.Equal("current_run_mp.teyvat.save", SaveSafety.BackupName("current_run_mp.save"));
        Assert.Equal("modded/profile1/saves/current_run.teyvat.save",
                     SaveSafety.BackupPathFor("modded/profile1/saves/current_run.save"));
    }

    [Fact]
    public void Header_reads_start_time_and_characters()
    {
        var h = SaveSafety.ReadHeader(Run(42, Klee, Ironclad));
        Assert.NotNull(h);
        Assert.Equal(42, h!.StartTime);
        Assert.Equal(new[] { Klee, Ironclad }, h.CharacterIds);
        Assert.Null(SaveSafety.ReadHeader("not json"));
        Assert.Null(SaveSafety.ReadHeader(""));
        Assert.Null(SaveSafety.ReadHeader(null));
    }

    [Fact]
    public void Only_a_run_with_one_of_ours_is_backed_up()
    {
        Assert.True(SaveSafety.IsTeyvatRun(new[] { Klee }, Ours));
        Assert.True(SaveSafety.IsTeyvatRun(new[] { Ironclad, Klee }, Ours));   // co-op
        Assert.False(SaveSafety.IsTeyvatRun(new[] { Ironclad }, Ours));
        Assert.False(SaveSafety.IsTeyvatRun(new string?[] { null }, Ours));
    }

    private static SaveSafety.Verdict D(bool run, bool runBak, string? backup,
                                        Func<long, bool>? hist = null, HashSet<string>? reg = null) =>
        SaveSafety.Decide(run, runBak, backup, hist ?? (_ => false), reg ?? RegisteredAll, Ours);

    [Fact]
    public void Restores_only_when_no_run_is_open()
    {
        string teyvat = Run(100, Klee);
        Assert.Equal(SaveSafety.Verdict.Restore, D(false, false, teyvat));
        // A live run (a vanilla run in progress, or the game's own .backup of one) is never clobbered.
        Assert.Equal(SaveSafety.Verdict.LiveRunPresent, D(true, false, teyvat));
        Assert.Equal(SaveSafety.Verdict.LiveRunPresent, D(false, true, teyvat));
        Assert.Equal(SaveSafety.Verdict.NoBackup, D(false, false, null));
    }

    [Fact]
    public void Never_resurrects_a_finished_run_or_an_unknown_character()
    {
        Assert.Equal(SaveSafety.Verdict.Finished, D(false, false, Run(100, Klee), hist: s => s == 100));
        Assert.Equal(SaveSafety.Verdict.Restore, D(false, false, Run(100, Klee), hist: s => s == 7));
        // A beta Yae run under a build that does not register Yae stays in its backup.
        Assert.Equal(SaveSafety.Verdict.UnknownCharacter,
                     D(false, false, Run(5, Klee, Yae), reg: RegisteredNoYae));
        Assert.Equal(SaveSafety.Verdict.NotTeyvat, D(false, false, Run(5, Ironclad)));
        Assert.Equal(SaveSafety.Verdict.Unreadable, D(false, false, "{}"));
        Assert.Equal(SaveSafety.Verdict.Unreadable, D(false, false, "garbage"));
    }

    [Fact]
    public void Backup_goes_only_with_its_own_run()
    {
        Assert.True(SaveSafety.SameRun(Run(100, Klee), Run(100, Klee)));
        Assert.False(SaveSafety.SameRun(Run(200, Ironclad), Run(100, Klee)));   // a vanilla run ended
        Assert.False(SaveSafety.SameRun(null, Run(100, Klee)));                 // unreadable: keep it
    }

    // ------------------------------------------- the hooks, pinned by name ---

    [Fact]
    public void Every_hooked_game_member_still_exists()
    {
        Assert.NotNull(AccessTools.Method(typeof(UserDataPathProvider), nameof(UserDataPathProvider.GetAccountDir)));
        Assert.NotNull(AccessTools.Method(typeof(SaveManager), nameof(SaveManager.InitProfileId)));
        Assert.NotNull(AccessTools.Method(typeof(SaveManager), nameof(SaveManager.SwitchProfileId)));
        Assert.NotNull(AccessTools.Method(typeof(RunSaveManager), nameof(RunSaveManager.SaveRun),
                                          new[] { typeof(SerializableRun), typeof(bool) }));
        Assert.NotNull(AccessTools.Method(typeof(RunSaveManager), nameof(RunSaveManager.DeleteCurrentRun)));
        Assert.NotNull(AccessTools.Method(typeof(RunSaveManager), nameof(RunSaveManager.DeleteCurrentMultiplayerRun)));
        Assert.NotNull(AccessTools.Field(typeof(SaveManager), "_saveStore"));
        Assert.NotNull(AccessTools.Field(typeof(RunSaveManager), "_saveStore"));
        Assert.NotNull(AccessTools.Field(typeof(RunSaveManager), "_profileIdProvider"));
    }
}
