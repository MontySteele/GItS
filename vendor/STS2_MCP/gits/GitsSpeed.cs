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

    private static bool _gitsSpeedEnabled;
    private static bool _gitsSpeedCaptured;
    private static FastModeType _gitsSpeedOriginalFastMode = FastModeType.Normal;
    private static double _gitsSpeedOriginalTimeScale = 1.0;

    private static Dictionary<string, object?> GitsSpeedReport(string message)
    {
        return new Dictionary<string, object?>
        {
            ["status"] = "ok",
            ["message"] = message,
            ["enabled"] = _gitsSpeedEnabled,
            ["fast_mode"] = SaveManager.Instance.PrefsSave.FastMode.ToString(),
            ["time_scale"] = Engine.TimeScale,
            ["original_fast_mode"] = _gitsSpeedCaptured
                ? _gitsSpeedOriginalFastMode.ToString()
                : null,
            ["original_time_scale"] = _gitsSpeedCaptured
                ? (object?)_gitsSpeedOriginalTimeScale
                : null
        };
    }

    private static Dictionary<string, object?> GitsSpeedApply(bool enabled, double? timeScale)
    {
        if (!_gitsSpeedCaptured)
        {
            _gitsSpeedOriginalFastMode = SaveManager.Instance.PrefsSave.FastMode;
            _gitsSpeedOriginalTimeScale = Engine.TimeScale;
            _gitsSpeedCaptured = true;
        }

        if (enabled)
        {
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
        return GitsSpeedReport("understudy speed OFF (originals restored)");
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
