// GItS LOCAL ADDITION -- funnel two-instances (2026-08-29).
//
// WHERE THE BRIDGE'S PORT COMES FROM, AND WHY IT IS NOT ONLY THE CONF FILE.
//
// Upstream reads the listener port from `STS2_MCP.conf`, which lives beside
// the mod dll -- i.e. inside the GAME directory. Two game processes launched
// from ONE install therefore read ONE conf and try to bind ONE port; the
// second listener loses. A live experiment proved the rest of the two-instance
// story works off a single install (Steam initialises twice on one account,
// and a per-process `APPDATA` gives each a wholly separate user:// tree), so
// the port was the only thing left needing a per-PROCESS source.
//
// An environment variable is that source: it is set by whoever launches the
// process, it cannot collide between two processes sharing a directory, and
// it needs no second copy of the game.
//
// PRECEDENCE IS env > conf > default, and the CHOICE IS LOGGED. A bridge that
// silently listened somewhere other than where its operator thought is the
// failure this whole file exists to make impossible to have quietly.
//
// This type is deliberately free of Godot, Harmony and game types: it is the
// one piece of the port decision that can be unit-tested headlessly, and
// `McpMod.LoadPort` is a thin wrapper over it.

#nullable enable

using System;
using System.Text.Json;

namespace STS2_MCP;

public readonly struct PortChoice
{
    public PortChoice(int port, string source, string note)
    {
        Port = port;
        Source = source;
        Note = note;
    }

    public int Port { get; }

    /// <summary>"env", "conf" or "default" -- which of the three won.</summary>
    public string Source { get; }

    /// <summary>Human-readable reason, printed to the game log.</summary>
    public string Note { get; }
}

public static class GitsPort
{
    public const int DefaultPort = 15526;
    public const string EnvVar = "STS2_MCP_PORT";

    /// <summary>
    /// Resolve the listener port from the environment value and the conf
    /// file's text. Both arguments may be null or empty; neither is read from
    /// disk here, so this is testable with no game and no file system.
    /// </summary>
    public static PortChoice Resolve(string? envValue, string? confText)
    {
        // 1. THE ENVIRONMENT, first and unconditionally. An UNPARSEABLE or
        //    out-of-range value is a refusal that falls through to the conf
        //    rather than a silent bind on the default: the operator asked for
        //    something specific and got something else either way, so the log
        //    line is the whole point.
        string env = (envValue ?? string.Empty).Trim();
        if (env.Length > 0)
        {
            if (TryPort(env, out int envPort))
            {
                return new PortChoice(envPort, "env",
                    $"{EnvVar}={envPort}");
            }
            // Fall through, but say so.
            var fallback = FromConf(confText);
            return new PortChoice(fallback.Port, fallback.Source,
                $"{EnvVar}='{env}' is not a port in 1..65535; " +
                $"fell back to {fallback.Source} ({fallback.Note})");
        }

        return FromConf(confText);
    }

    private static PortChoice FromConf(string? confText)
    {
        string text = confText ?? string.Empty;
        if (text.Trim().Length == 0)
        {
            return new PortChoice(DefaultPort, "default",
                $"no {EnvVar} and no readable config; using {DefaultPort}");
        }

        try
        {
            using var doc = JsonDocument.Parse(text);
            if (doc.RootElement.TryGetProperty("port", out var portElem)
                && portElem.TryGetInt32(out int port)
                && port is > 0 and <= 65535)
            {
                return new PortChoice(port, "conf",
                    $"port {port} from STS2_MCP.conf");
            }
        }
        catch (JsonException)
        {
            return new PortChoice(DefaultPort, "default",
                $"STS2_MCP.conf is not valid JSON; using {DefaultPort}");
        }

        return new PortChoice(DefaultPort, "default",
            $"no usable 'port' in STS2_MCP.conf; using {DefaultPort}");
    }

    private static bool TryPort(string raw, out int port)
    {
        return int.TryParse(raw, out port) && port > 0 && port <= 65535;
    }
}
