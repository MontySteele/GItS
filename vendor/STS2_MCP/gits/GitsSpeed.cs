// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// Understudy sprint, work item W2. [USER]-ratified 2026-08-04, ruling 3:
// BUILD the speed affordance ourselves. The game's own FastModeType.Instant
// is unreachable through the settings UI (the UI offers Normal/Fast only),
// and Godot.Engine.TimeScale is not exposed at all. Both are ours to set.
//
// Contract, and the part that matters for the ledger:
//
//   * OFF BY DEFAULT. Loading this file changes nothing. The mod does not
//     touch FastMode or TimeScale until something POSTs to the endpoint.
//   * NO GAMEPLAY EFFECT. FastMode is an animation-pacing enum the game
//     already ships and already exposes two thirds of; TimeScale is a Godot
//     frame-delta multiplier. Neither is read by any rules code. Nothing
//     here touches damage, RNG, energy, draw, or any balance surface.
//   * REVERSIBLE. The pre-change FastMode and TimeScale are captured on the
//     first enable and restored by a disable. PrefsSave.FastMode is
//     user-visible state that persists to settings.save, so the harness is
//     expected to disable in teardown; `restore_on_disable` is the whole
//     reason the original values are remembered rather than assumed.
//   * THE CAPTURED FastMode OUTLIVES THE PROCESS (EB-87). The capture used to
//     be per-process static only, and PrefsSave.FastMode persists to
//     settings.save: an unattended soak that restarts the game had its second
//     process read back `Instant`, record THAT as the original, and "restore"
//     to it on teardown -- leaving the game on Instant while the ledger said
//     REVERTED. The first capture is therefore written to a sidecar file next
//     to the mod's own STS2_MCP.conf, a later process restores from the
//     sidecar instead of re-capturing, and a successful disable deletes it.
//     TimeScale is NOT persisted and must not be: Engine.TimeScale is a live
//     Godot property that starts at its default in every new process, so the
//     per-process capture is already the right original for it.
//
// Enablement channel: HTTP, on the bridge this file lives in.
//
//   GET  /api/v1/gits/speed
//        -> { status, enabled, fast_mode, time_scale, original_* }
//   POST /api/v1/gits/speed   { "enabled": true, "time_scale": 4.0 }
//        -> same shape. `time_scale` is optional and clamped to [0.1, 20].
//        Omitting it on enable leaves TimeScale alone and uses Instant only.
//        { "enabled": false } restores both captured originals.
//
// Routed from McpMod.HandleRequest - see PROVENANCE.md, which records the
// three route arms in McpMod.cs and the one StateBuilder.cs line as the whole
// edit surface on upstream files.

using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text.Json;
using Godot;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Settings;

namespace STS2_MCP;

public static partial class McpMod
{
    private const double GitsSpeedMinTimeScale = 0.1;
    private const double GitsSpeedMaxTimeScale = 20.0;

    private const string GitsSpeedSidecarFileName = "GitsSpeed.original.json";

    private static bool _gitsSpeedEnabled;
    private static bool _gitsSpeedCaptured;
    private static FastModeType _gitsSpeedOriginalFastMode = FastModeType.Normal;
    private static double _gitsSpeedOriginalTimeScale = 1.0;
    // "process" (this process read it off PrefsSave) or "sidecar" (an earlier
    // process's capture was restored from disk). Reported so the harness ledger
    // can say which, and so a restart is visible rather than silent.
    private static string? _gitsSpeedOriginalSource;

    private static string? GitsSpeedSidecarPath()
    {
        try
        {
            string? modDir = Path.GetDirectoryName(
                System.Reflection.Assembly.GetExecutingAssembly().Location);
            return modDir == null
                ? null
                : Path.Combine(modDir, GitsSpeedSidecarFileName);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] speed sidecar path unavailable: {ex.Message}");
            return null;
        }
    }

    private static FastModeType? GitsSpeedReadSidecar()
    {
        string? path = GitsSpeedSidecarPath();
        if (path == null || !File.Exists(path))
            return null;
        try
        {
            using var doc = JsonDocument.Parse(File.ReadAllText(path));
            if (doc.RootElement.TryGetProperty("original_fast_mode", out var elem)
                && elem.ValueKind == JsonValueKind.String
                && Enum.TryParse(elem.GetString(), out FastModeType parsed))
            {
                return parsed;
            }
            GD.PrintErr($"[STS2 MCP][GItS] speed sidecar {path} has no usable "
                        + "'original_fast_mode'; capturing live instead");
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] speed sidecar unreadable ({ex.Message}); "
                        + "capturing live instead");
        }
        return null;
    }

    private static void GitsSpeedWriteSidecar(FastModeType original)
    {
        string? path = GitsSpeedSidecarPath();
        if (path == null)
            return;
        try
        {
            var payload = new Dictionary<string, object>
            {
                ["original_fast_mode"] = original.ToString(),
                ["captured_utc"] = DateTime.UtcNow.ToString("o")
            };
            File.WriteAllText(path, JsonSerializer.Serialize(payload, _jsonOptions));
        }
        catch (Exception ex)
        {
            // A sidecar we cannot write is a restart we cannot survive, but it
            // is not a reason to fail the enable: this process's own capture is
            // still correct for this process.
            GD.PrintErr($"[STS2 MCP][GItS] could not write speed sidecar: {ex.Message}");
        }
    }

    private static void GitsSpeedDeleteSidecar()
    {
        string? path = GitsSpeedSidecarPath();
        if (path == null)
            return;
        try
        {
            if (File.Exists(path))
                File.Delete(path);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] could not delete speed sidecar: {ex.Message}");
        }
    }

    private static Dictionary<string, object?> GitsSpeedReport(string message)
    {
        // Before the first capture, the sidecar (if any) IS the answer to
        // "what was this set to before the harness touched it" -- a GET taken
        // by a freshly restarted process must not report `null` and let the
        // caller conclude nothing is outstanding.
        FastModeType? original = _gitsSpeedCaptured
            ? _gitsSpeedOriginalFastMode
            : GitsSpeedReadSidecar();
        string? source = _gitsSpeedCaptured
            ? _gitsSpeedOriginalSource
            : (original.HasValue ? "sidecar" : null);

        return new Dictionary<string, object?>
        {
            ["status"] = "ok",
            ["message"] = message,
            ["enabled"] = _gitsSpeedEnabled,
            ["fast_mode"] = SaveManager.Instance.PrefsSave.FastMode.ToString(),
            ["time_scale"] = Engine.TimeScale,
            ["original_fast_mode"] = original?.ToString(),
            ["original_fast_mode_source"] = source,
            ["original_time_scale"] = _gitsSpeedCaptured
                ? (object?)_gitsSpeedOriginalTimeScale
                : null
        };
    }

    private static Dictionary<string, object?> GitsSpeedApply(bool enabled, double? timeScale)
    {
        if (!_gitsSpeedCaptured)
        {
            // The sidecar wins over the live read. After a restart the live
            // read IS the value we set last process (FastMode persists to
            // settings.save), so re-capturing would launder our own change
            // into the baseline -- EB-87.
            FastModeType? persisted = GitsSpeedReadSidecar();
            if (persisted.HasValue)
            {
                _gitsSpeedOriginalFastMode = persisted.Value;
                _gitsSpeedOriginalSource = "sidecar";
            }
            else
            {
                _gitsSpeedOriginalFastMode = SaveManager.Instance.PrefsSave.FastMode;
                _gitsSpeedOriginalSource = "process";
            }
            _gitsSpeedOriginalTimeScale = Engine.TimeScale;
            _gitsSpeedCaptured = true;
        }

        if (enabled)
        {
            // Written on every ENABLE, not at capture: the sidecar exists to
            // record an OUTSTANDING change, so a disable-first call leaves no
            // file behind, and an enable that follows a disable in the same
            // process re-arms the one the disable deleted.
            GitsSpeedWriteSidecar(_gitsSpeedOriginalFastMode);
            SaveManager.Instance.PrefsSave.FastMode = FastModeType.Instant;
            if (timeScale.HasValue)
            {
                Engine.TimeScale = Math.Clamp(
                    timeScale.Value, GitsSpeedMinTimeScale, GitsSpeedMaxTimeScale);
            }
            _gitsSpeedEnabled = true;
            return GitsSpeedReport("understudy speed ON (animation pacing only)");
        }

        SaveManager.Instance.PrefsSave.FastMode = _gitsSpeedOriginalFastMode;
        Engine.TimeScale = _gitsSpeedOriginalTimeScale;
        _gitsSpeedEnabled = false;
        // The change is undone, so the record of it goes. The in-memory
        // capture is deliberately KEPT: a later enable in this same process
        // re-arms from it, and a GET can still say what was restored.
        GitsSpeedDeleteSidecar();
        return GitsSpeedReport(
            $"understudy speed OFF (originals restored; FastMode original from "
            + $"{_gitsSpeedOriginalSource ?? "process"})");
    }

    private static void HandleGitsSpeed(HttpListenerRequest request, HttpListenerResponse response)
    {
        try
        {
            if (request.HttpMethod == "GET")
            {
                var readTask = RunOnMainThread(() => GitsSpeedReport("current"));
                SendJson(response, readTask.GetAwaiter().GetResult());
                return;
            }

            if (request.HttpMethod != "POST")
            {
                SendError(response, 405, "Method not allowed");
                return;
            }

            string body;
            using (var reader = new StreamReader(request.InputStream, request.ContentEncoding))
                body = reader.ReadToEnd();

            Dictionary<string, JsonElement>? parsed;
            try
            {
                parsed = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(body);
            }
            catch
            {
                SendError(response, 400, "Invalid JSON");
                return;
            }

            if (parsed == null || !parsed.TryGetValue("enabled", out var enabledElem))
            {
                SendError(response, 400, "Missing 'enabled' field");
                return;
            }

            bool enabled = enabledElem.ValueKind == JsonValueKind.True;
            double? timeScale = null;
            if (parsed.TryGetValue("time_scale", out var tsElem)
                && tsElem.TryGetDouble(out double ts))
            {
                timeScale = ts;
            }

            var applyTask = RunOnMainThread(() => GitsSpeedApply(enabled, timeScale));
            SendJson(response, applyTask.GetAwaiter().GetResult());
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] speed endpoint failed: {ex}");
            try { SendError(response, 500, $"Speed control failed: {ex.Message}"); }
            catch { /* response may already be closed */ }
        }
    }
}
