using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using HarmonyLib;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Saves.Managers;

namespace KleeMod.Saves;

/// <summary>
/// The game-facing half of <see cref="SaveSafety"/> (read that first). Every
/// hook is wrapped so a failure logs one line and leaves the game's own save
/// path exactly as it was.
/// </summary>
internal static class SaveSafetyRuntime
{
    internal const string Tag = "[klee] save safety:";

    /// <summary>This build's variant, read once (GetAccountDir runs often).</summary>
    internal static readonly string? Variant = WorkshopRelease.Variant;

    internal static readonly AccessTools.FieldRef<SaveManager, ISaveStore> SaveManagerStore =
        AccessTools.FieldRefAccess<SaveManager, ISaveStore>("_saveStore");

    internal static readonly AccessTools.FieldRef<RunSaveManager, ISaveStore> RunStore =
        AccessTools.FieldRefAccess<RunSaveManager, ISaveStore>("_saveStore");

    internal static readonly AccessTools.FieldRef<RunSaveManager, IProfileIdProvider> RunProfile =
        AccessTools.FieldRefAccess<RunSaveManager, IProfileIdProvider>("_profileIdProvider");

    /// <summary>The local half of a store: reads and our backups never touch the cloud.</summary>
    internal static ISaveStore Local(ISaveStore store) =>
        store is CloudSaveStore cloud ? cloud.LocalStore : store;

    internal static HashSet<string> Registered() =>
        ModelDb.AllCharacters.Select(c => c.Id.ToString()).ToHashSet(StringComparer.Ordinal);

    internal static HashSet<string> Ours() =>
        ModelDb.AllCharacters.Where(c => ReleaseKits.KitOf(c) != null)
            .Select(c => c.Id.ToString()).ToHashSet(StringComparer.Ordinal);

    internal static string? ReadOrNull(ISaveStore store, string path)
    {
        try { return store.FileExists(path) ? store.ReadFile(path) : null; }
        catch (Exception e)
        {
            Log.Warn($"{Tag} could not read {path}: {e.Message}");
            return null;
        }
    }

    /// <summary>
    /// Put a profile's Teyvat backup back as its run save when
    /// <see cref="SaveSafety.Decide"/> says so. The restore is written through
    /// the game's own store, so a cloud-synced profile keeps it.
    /// </summary>
    internal static void TryRestore(ISaveStore store, int profileId, string runSaveName)
    {
        try
        {
            var local = Local(store);
            string runPath = RunSaveManager.GetRunSavePath(profileId, runSaveName);
            string backupPath = SaveSafety.BackupPathFor(runPath);
            string? backup = ReadOrNull(local, backupPath);
            string history = RunHistorySaveManager.GetHistoryPath(profileId);
            var verdict = SaveSafety.Decide(
                local.FileExists(runPath), local.FileExists(runPath + ".backup"), backup,
                start => local.FileExists($"{history}/{start}.run"),
                Registered(), Ours());
            if (verdict == SaveSafety.Verdict.NoBackup) return;
            if (verdict != SaveSafety.Verdict.Restore)
            {
                Log.Info($"{Tag} profile {profileId} {runSaveName}: backup kept, not restored ({verdict})");
                return;
            }
            store.WriteFile(runPath, Encoding.UTF8.GetBytes(backup!));
            Log.Info($"{Tag} profile {profileId}: restored the Teyvat run from {backupPath}");
        }
        catch (Exception e)
        {
            Log.Warn($"{Tag} restore check failed for profile {profileId} {runSaveName}: {e.Message}");
        }
    }

    internal static void TryRestoreBoth(SaveManager manager)
    {
        var store = SaveManagerStore(manager);
        int profile = manager.CurrentProfileId;
        TryRestore(store, profile, SaveSafety.RunSave);
        TryRestore(store, profile, SaveSafety.MultiplayerRunSave);
    }

    /// <summary>
    /// The beta's one-time copy of the normal modded saves (the plan is
    /// <see cref="SaveSafety.MigrationPlan"/>). Runs after the game's cloud
    /// sync and before it reads profile.save. Files go through the game's
    /// store when Steam cloud is on, so the next boot's sync finds them in the
    /// cloud and keeps them (a local-only file is deleted by that sync), with
    /// the run history under the game's own cloud quota.
    /// </summary>
    internal static void MigrateBetaFolder(SaveManager manager)
    {
        if (!string.Equals(Variant, SaveSafety.BetaVariant, StringComparison.Ordinal)) return;
        if (!UserDataPathProvider.IsRunningModded) return;
        try
        {
            var store = SaveManagerStore(manager);
            var local = Local(store);
            if (!SaveSafety.NeedsMigration(local.FileExists)) return;
            var cloud = store as CloudSaveStore;
            bool toCloud = cloud != null && cloud.HasUserEnabledCloudSync();
            var target = toCloud ? store : local;
            var plan = SaveSafety.MigrationPlan(local.FileExists,
                dir => local.DirectoryExists(dir) ? local.GetFilesInDirectory(dir) : Array.Empty<string>());
            Log.Info($"{Tag} first beta boot: copying {plan.Count} files from "
                   + $"{SaveSafety.ModdedAccountDir}/ to {SaveSafety.BetaAccountDir}/ (cloud: {toCloud})");
            int copied = 0;
            foreach (var (from, to) in plan)
            {
                string? content = local.ReadFile(from);
                if (string.IsNullOrWhiteSpace(content)) continue;
                bool isHistory = to.Contains("/history/", StringComparison.Ordinal);
                // Our backups are local-only files; everything else is a file the game syncs.
                bool synced = !to.EndsWith(".teyvat.save", StringComparison.Ordinal);
                if (toCloud && synced && isHistory)
                    cloud!.ForgetFilesInDirectoryBeforeWritingIfNecessary(
                        to[..to.LastIndexOf('/')], Encoding.UTF8.GetByteCount(content),
                        RunHistorySaveManager.maxCloudBytes, RunHistorySaveManager.maxCloudFileCount);
                (synced ? target : local).WriteFile(to, content);
                copied++;
            }
            Log.Info($"{Tag} copied {copied} files; the normal modded folder is untouched");
        }
        catch (Exception e)
        {
            Log.Warn($"{Tag} beta folder copy failed (the beta starts from what it has): {e.Message}");
        }
    }
}

/// <summary>THE BETA'S OWN SAVE FOLDER: every save path the game builds.</summary>
[HarmonyPatch(typeof(UserDataPathProvider), nameof(UserDataPathProvider.GetAccountDir))]
internal static class UserDataPathProvider_GetAccountDir_BetaFolder_Patch
{
    [HarmonyPostfix]
    public static void Postfix(ref string __result) =>
        __result = SaveSafety.Redirect(__result, SaveSafetyRuntime.Variant);
}

/// <summary>
/// Boot: after the cloud sync, before profile.save is read. The beta's copy
/// first, then the Teyvat run restore for the profile the game opens.
/// </summary>
[HarmonyPatch(typeof(SaveManager), nameof(SaveManager.InitProfileId))]
internal static class SaveManager_InitProfileId_SaveSafety_Patch
{
    [HarmonyPrefix]
    public static void Prefix(SaveManager __instance) =>
        SaveSafetyRuntime.MigrateBetaFolder(__instance);

    [HarmonyPostfix]
    public static void Postfix(SaveManager __instance)
    {
        try { SaveSafetyRuntime.TryRestoreBoth(__instance); }
        catch (Exception e) { Log.Warn($"{SaveSafetyRuntime.Tag} {e.Message}"); }
    }
}

/// <summary>A profile switch opens another profile's saves: same restore check.</summary>
[HarmonyPatch(typeof(SaveManager), nameof(SaveManager.SwitchProfileId))]
internal static class SaveManager_SwitchProfileId_SaveSafety_Patch
{
    [HarmonyPostfix]
    public static void Postfix(SaveManager __instance)
    {
        try { SaveSafetyRuntime.TryRestoreBoth(__instance); }
        catch (Exception e) { Log.Warn($"{SaveSafetyRuntime.Tag} {e.Message}"); }
    }
}

/// <summary>
/// THE TEYVAT RUN BACKUP: after the game finishes writing a run save that
/// holds one of our characters, keep the same text beside it (local only).
/// </summary>
[HarmonyPatch(typeof(RunSaveManager), nameof(RunSaveManager.SaveRun),
              new[] { typeof(SerializableRun), typeof(bool) })]
internal static class RunSaveManager_SaveRun_TeyvatBackup_Patch
{
    [HarmonyPostfix]
    public static void Postfix(RunSaveManager __instance, SerializableRun save,
                               bool isMultiplayer, ref Task __result)
    {
        try
        {
            var ids = save?.Players?.Select(p => p.CharacterId?.ToString()) ?? Enumerable.Empty<string?>();
            if (!SaveSafety.IsTeyvatRun(ids, SaveSafetyRuntime.Ours())) return;
            var local = SaveSafetyRuntime.Local(SaveSafetyRuntime.RunStore(__instance));
            int profile = SaveSafetyRuntime.RunProfile(__instance).CurrentProfileId;
            string runPath = RunSaveManager.GetRunSavePath(profile,
                isMultiplayer ? SaveSafety.MultiplayerRunSave : SaveSafety.RunSave);
            __result = KeepCopy(__result, local, runPath);
        }
        catch (Exception e)
        {
            Log.Warn($"{SaveSafetyRuntime.Tag} backup not armed for this save: {e.Message}");
        }
    }

    private static async Task KeepCopy(Task original, ISaveStore local, string runPath)
    {
        await original;   // the game's own write first; its failure stays its own
        try
        {
            string? content = local.ReadFile(runPath);
            if (string.IsNullOrWhiteSpace(content)) return;
            local.WriteFile(SaveSafety.BackupPathFor(runPath), content);
        }
        catch (Exception e)
        {
            Log.Warn($"{SaveSafetyRuntime.Tag} could not keep the Teyvat run backup: {e.Message}");
        }
    }
}

/// <summary>
/// The game deletes a run save when a run ends or is abandoned (after writing
/// its history entry). If that run is the one our backup holds, the backup
/// goes too. If it was another run (a vanilla run played while our run was
/// hidden), our run comes back now that no run is open.
/// </summary>
[HarmonyPatch]
internal static class RunSaveManager_DeleteRun_TeyvatBackup_Patch
{
    [HarmonyTargetMethods]
    public static IEnumerable<System.Reflection.MethodBase> TargetMethods() =>
        new[]
        {
            KleePatchBootstrap.ResolveMethod(typeof(RunSaveManager), nameof(RunSaveManager.DeleteCurrentRun)),
            KleePatchBootstrap.ResolveMethod(typeof(RunSaveManager), nameof(RunSaveManager.DeleteCurrentMultiplayerRun)),
        }.Where(m => m != null)!;

    private static string NameFor(System.Reflection.MethodBase m) =>
        m.Name == nameof(RunSaveManager.DeleteCurrentMultiplayerRun)
            ? SaveSafety.MultiplayerRunSave : SaveSafety.RunSave;

    [HarmonyPrefix]
    public static void Prefix(RunSaveManager __instance, System.Reflection.MethodBase __originalMethod,
                              out string? __state)
    {
        __state = null;
        try
        {
            var local = SaveSafetyRuntime.Local(SaveSafetyRuntime.RunStore(__instance));
            int profile = SaveSafetyRuntime.RunProfile(__instance).CurrentProfileId;
            string runPath = RunSaveManager.GetRunSavePath(profile, NameFor(__originalMethod));
            __state = SaveSafetyRuntime.ReadOrNull(local, runPath)
                      ?? SaveSafetyRuntime.ReadOrNull(local, runPath + ".backup");
        }
        catch (Exception e)
        {
            Log.Warn($"{SaveSafetyRuntime.Tag} {e.Message}");
        }
    }

    [HarmonyPostfix]
    public static void Postfix(RunSaveManager __instance, System.Reflection.MethodBase __originalMethod,
                               string? __state)
    {
        try
        {
            var store = SaveSafetyRuntime.RunStore(__instance);
            var local = SaveSafetyRuntime.Local(store);
            int profile = SaveSafetyRuntime.RunProfile(__instance).CurrentProfileId;
            string name = NameFor(__originalMethod);
            string backupPath = SaveSafety.BackupPathFor(RunSaveManager.GetRunSavePath(profile, name));
            string? backup = SaveSafetyRuntime.ReadOrNull(local, backupPath);
            if (backup == null) return;
            if (SaveSafety.SameRun(__state, backup))
            {
                local.DeleteFile(backupPath);
                local.DeleteFile(backupPath + ".backup");
                return;
            }
            SaveSafetyRuntime.TryRestore(store, profile, name);
        }
        catch (Exception e)
        {
            Log.Warn($"{SaveSafetyRuntime.Tag} {e.Message}");
        }
    }
}
