#nullable enable
using System;
using MegaCrit.Sts2.Core.Saves;

namespace KleeMod.RunStats;

/// <summary>
/// THE DECISION, kept apart from the game and the network so the test
/// project can drive it with fakes.
///
/// TWO SWITCHES, BOTH ON, OR NOTHING. (1) The game's own "Upload data"
/// setting: the game calls <c>ModManager.OnMetricsUpload</c> only with it on,
/// and never for an abandoned run, a debug build or a first-ever run
/// (0.111.0 <c>MetricUtilities.UploadRunMetricsInternal</c>). The mod does not
/// re-implement that gate; it reads the setting once more here as a second
/// belt, so a future game build that fires the hook more widely still sends
/// nothing with it off. (2) The mod's own setting, "Share anonymous run stats
/// with the Teyvat Spire developers", default ON since 2026-10-18 ([USER]:
/// "Let's go default on."; <c>RunStatsConfig.ShareAnonymousRunStats</c>).
///
/// Nothing is made unless both are on: the install id is asked for only
/// after the check, so a player who turns the setting off never gets one.
/// </summary>
public static class RunStatsUpload
{
    /// <summary>
    /// The default-on generation. A config whose saved
    /// <c>RunStatsDefaultVersion</c> is below this was written while the
    /// default was off.
    /// </summary>
    public const int DefaultOnVersion = 1;

    /// <summary>
    /// PURE: the one-time move to default on (2026-10-18). BaseLib keeps a
    /// saved value over a changed default (<c>ModConfig.Init</c> captures the
    /// code default, then <c>Load</c> applies the file), and every install
    /// that ran the old beta has <c>"ShareAnonymousRunStats": "False"</c>
    /// written, whether the player chose it or not: the file stores no
    /// "touched" flag, so the two cannot be told apart. So a config from
    /// before default-on is switched on once, and the version is stamped so
    /// a player who turns it off afterwards stays off. Returns the setting,
    /// the version to store, and whether the file must be saved.
    /// </summary>
    public static (bool Share, int Version, bool Save) MigrateDefault(bool share, int savedVersion) =>
        savedVersion >= DefaultOnVersion
            ? (share, savedVersion, false)
            : (true, DefaultOnVersion, true);

    /// <summary>PURE: may this run go up?</summary>
    public static bool ShouldSend(bool gameUploadData, bool modOptIn, string? endpoint) =>
        gameUploadData && modOptIn && !string.IsNullOrWhiteSpace(endpoint);

    /// <summary>
    /// Trim and hand the record to <paramref name="send"/> when both
    /// switches are on. Returns the JSON it sent, or null when it sent
    /// nothing. Throws nothing: a failure is logged by the caller's
    /// <paramref name="log"/> and dropped.
    /// </summary>
    public static string? Handle(SerializableRun run, bool isVictory, ulong localPlayerId,
                                 bool gameUploadData, bool modOptIn, string? endpoint,
                                 Func<string> installId, string modVersion, string variant,
                                 string buildId, Action<string> send, Action<string>? log = null)
    {
        try
        {
            if (!ShouldSend(gameUploadData, modOptIn, endpoint)) return null;
            var ctx = new RunRecordContext(RunRecord.NewUuid4(), installId(), modVersion,
                                           variant, buildId);
            var json = RunRecord.ToJson(RunRecord.Trim(run, isVictory, localPlayerId, ctx));
            send(json);
            return json;
        }
        catch (Exception e)
        {
            log?.Invoke($"run stats: not sent ({e.GetType().Name}: {e.Message})");
            return null;
        }
    }
}
