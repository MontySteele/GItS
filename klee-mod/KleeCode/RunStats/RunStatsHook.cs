using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;
using BaseLib.Config;
using MegaCrit.Sts2.Core.Debug;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Modding;
using MegaCrit.Sts2.Core.Saves;

namespace KleeMod.RunStats;

/// <summary>
/// THE MOD'S OWN SWITCH AND THE INSTALL ID, in BaseLib's mod config
/// (<c>%APPDATA%/SlayTheSpire2/mod_configs/KleeMod.cfg</c>). The player sees
/// one tickbox under Settings, Mod Configuration (BaseLib), Open Config,
/// Teyvat Spire Roster:
/// "Share anonymous run stats with the Teyvat Spire developers", on by
/// default since 2026-10-18 ([USER]: "Let's go default on."), and the player
/// can untick it there. The install id is hidden, survives Restore Defaults,
/// and is made the first time a run is actually sent. The default reaches
/// new installs only: BaseLib keeps a saved value, so an install that ran
/// the opt-in beta keeps its saved choice ([USER]: "2) is fine on the
/// telemetry flip - we currently only have 2 people testing it.").
/// </summary>
public sealed class RunStatsConfig : SimpleModConfig
{
    [ConfigHoverTip]
    public static bool ShareAnonymousRunStats { get; set; } = true;

    [ConfigHideInUI]
    [ConfigIgnoreRestoreDefaults]
    public static string InstallId { get; set; } = "";

    internal static RunStatsConfig? Instance { get; set; }

    /// <summary>The install id, made and saved on first use.</summary>
    public static string EnsureInstallId()
    {
        if (!RunRecord.IsUuid4(InstallId))
        {
            InstallId = RunRecord.NewUuid4();
            Instance?.Save();
        }
        return InstallId;
    }
}

/// <summary>
/// OPT-IN RUN STATS, THE GAME SIDE (2026-10-16, [USER]: "go ahead and try
/// to build the opt-in upload now in the beta release"). Compiled only into a
/// build with <c>-p:GitsTelemetryEndpoint</c> (a beta or public package made
/// with <c>--telemetry-endpoint</c>; the public one since 2026-10-21, [USER]:
/// "Include the telemetry as opt-out."); every other build has no file of
/// this folder. The Worker is <c>telemetry-worker/</c>; what is sent is its
/// schema, <c>schema/run-v1.json</c>.
///
/// It subscribes to <c>ModManager.OnMetricsUpload</c>, the game's own
/// end-of-run hook for modded play, and adds nothing to when it fires. The
/// record is trimmed on the game thread (a walk over the finished run), then
/// posted on a pool thread: one try, ten seconds, a failure logged and
/// dropped. No queue, no retry, nothing written to disk but the install id.
/// </summary>
internal static class RunStatsHook
{
    public const string EndpointKey = "GitsTelemetryEndpoint";

    private static readonly HttpClient Http = new() { Timeout = TimeSpan.FromSeconds(10) };

    /// <summary>"TeyvatSpire/0.3.0 (+telemetry)".</summary>
    public static string UserAgent => $"TeyvatSpire/{WorkshopRelease.ModVersion} (+telemetry)";

    public static string? Endpoint =>
        typeof(RunStatsHook).Assembly.GetCustomAttributes<AssemblyMetadataAttribute>()
            .FirstOrDefault(a => a.Key == EndpointKey)?.Value;

    public static void Install()
    {
        try
        {
            var config = new RunStatsConfig();
            RunStatsConfig.Instance = config;
            ModConfigRegistry.Register(OwnModId(), config);
            ModManager.OnMetricsUpload += OnMetricsUpload;
            Log.Info($"[{KleeMod.ModId}] run stats: compiled in (endpoint set); "
                   + $"sharing is {(RunStatsConfig.ShareAnonymousRunStats ? "ON" : "off")} in the mod's settings");
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] run stats: setup failed, nothing will be sent ({e.Message})");
        }
    }

    /// <summary>The setting's label, hover tip and the mod's title in BaseLib's list.</summary>
    public static void InjectLoc()
    {
        try
        {
            var prefix = "KLEEMOD-" + StringHelper.Slugify(nameof(RunStatsConfig.ShareAnonymousRunStats));
            EnglishLoc.Table("settings_ui").MergeWith(new Dictionary<string, string>
            {
                ["KLEEMOD.mod_title"] = "Teyvat Spire Roster",
                [prefix + ".title"] = "Share anonymous run stats with the Teyvat Spire developers",
                [prefix + ".hover.title"] = "Anonymous run stats",
                [prefix + ".hover.desc"] =
                    "Needs the game's Upload data setting on too. After each run, sends your character, "
                    + "ascension, result, cards, relics and HP by floor. No Steam id or name.",
            });
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] run stats: settings text not merged ({e.Message})");
        }
    }

    private static void OnMetricsUpload(MegaCrit.Sts2.Core.Saves.SerializableRun run,
                                        bool isVictory, ulong localPlayerId)
    {
        try
        {
            RunStatsUpload.Handle(
                run, isVictory, localPlayerId,
                gameUploadData: SaveManager.Instance.PrefsSave.UploadData,
                modOptIn: RunStatsConfig.ShareAnonymousRunStats,
                endpoint: Endpoint,
                installId: RunStatsConfig.EnsureInstallId,
                modVersion: WorkshopRelease.ModVersion,
                variant: WorkshopRelease.Variant == "public" ? "public" : "beta",
                buildId: ReleaseInfoManager.Instance.ReleaseInfo?.Version ?? "unknown",
                send: Post,
                log: m => Log.Warn($"[{KleeMod.ModId}] {m}"));
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] run stats: not sent ({e.Message})");
        }
    }

    private static void Post(string json)
    {
        var endpoint = Endpoint;
        if (string.IsNullOrWhiteSpace(endpoint)) return;
        _ = Task.Run(async () =>
        {
            try
            {
                using var request = new HttpRequestMessage(HttpMethod.Post, endpoint)
                {
                    Content = new StringContent(json, Encoding.UTF8, "application/json"),
                };
                // An explicit, honest agent: Cloudflare's bot screen in front of
                // the Worker answers 403 to some library defaults
                // (Python-urllib), 204 to a named client.
                request.Headers.TryAddWithoutValidation("User-Agent", UserAgent);
                using var response = await Http.SendAsync(request).ConfigureAwait(false);
                if (response.IsSuccessStatusCode)
                    Log.Info($"[{KleeMod.ModId}] run stats: sent ({(int)response.StatusCode}, {json.Length} bytes)");
                else
                    Log.Warn($"[{KleeMod.ModId}] run stats: refused ({(int)response.StatusCode}), dropped");
            }
            catch (Exception e)
            {
                Log.Warn($"[{KleeMod.ModId}] run stats: upload failed, dropped ({e.GetType().Name})");
            }
        });
    }

    /// <summary>The manifest id the game loaded this dll under (klee or klee-beta).</summary>
    private static string OwnModId()
    {
        try
        {
            var asm = typeof(RunStatsHook).Assembly;
            var id = ModManager.Mods.FirstOrDefault(m => m.assemblies.Contains(asm))?.manifest?.id;
            return string.IsNullOrWhiteSpace(id) ? KleeMod.ModId : id;
        }
        catch
        {
            return KleeMod.ModId;
        }
    }
}
