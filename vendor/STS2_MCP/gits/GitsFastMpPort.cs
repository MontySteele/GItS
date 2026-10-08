// GItS LOCAL ADDITION -- parallel co-op pairs (2026-10-08).
//
// WHICH UDP PORT A `--fastmp` GAME HOSTS ON OR JOINS, AND WHY IT IS NOT
// ALWAYS THE GAME'S 33771.
//
// `--fastmp` co-op runs over ENet on localhost. The game writes the port as a
// literal at every call site (0.111.0 decompile): `NMultiplayerHostSubmenu.
// StartHostAsync` and `NMultiplayerSubmenu.StartHostAsync` call
// `netService.StartENetHost(33771, 4)`, and `NJoinFriendScreen.FastMpJoin`
// builds `new ENetClientConnectionInitializer(netId, "127.0.0.1", 33771)`.
// No argument, setting or environment variable moves it, so one machine held
// one co-op pair: a second host could not bind, and a second client would
// have dialled the first pair's host.
//
// The fix is a per-PROCESS port, chosen by whoever launches the game, on the
// command line: `--gitsFastmpPort N`, read through the game's own
// `CommandLineHelper` (the parser `--clientId` already goes through). The
// two Harmony prefixes in `GitsFastMpPortPatch.cs` rewrite the port on its
// way into `ENetHost.StartHost` and the `ENetClientConnectionInitializer`
// constructor -- the consuming methods, because the call sites pass a
// literal there is nothing else to patch.
//
// THE RULES, which this file is the one testable copy of:
//   * NO ARGUMENT -> the game's own port, untouched. A lane launched the way
//     every lane was launched before this file behaves exactly as before.
//   * ONLY 33771 IS REWRITTEN. A caller asking for any other port (none in
//     0.111.0, but a future one might) is not a fastmp caller and is left
//     alone.
//   * AN UNUSABLE VALUE IS REFUSED OUT LOUD and the game's port stands. The
//     harness reads the bound port back off the lobby (`fastmp_port`) and
//     refuses a pair whose port is not the one it asked for, so a silent
//     fallback cannot put two pairs on one port unnoticed.
//
// Deliberately free of Godot, Harmony and game types, so the decision is
// unit-tested headlessly (`klee-mod/KleeTests/GitsFastMpPortTests.cs`).

#nullable enable

namespace STS2_MCP;

public readonly struct FastMpPortChoice
{
    public FastMpPortChoice(int port, string source, string note)
    {
        Port = port;
        Source = source;
        Note = note;
    }

    public int Port { get; }

    /// <summary>"arg" when the command line moved the port, "game" when the
    /// game's own value stands.</summary>
    public string Source { get; }

    /// <summary>Human-readable reason, printed to the game log.</summary>
    public string Note { get; }
}

public static class GitsFastMpPort
{
    /// <summary>The literal the 0.111.0 game passes at every fastmp call site.</summary>
    public const int GameDefault = 33771;

    /// <summary>`--gitsFastmpPort N` (CommandLineHelper strips the dashes).</summary>
    public const string ArgName = "gitsFastmpPort";

    public static FastMpPortChoice Resolve(int requested, bool hasArg, string? argValue)
    {
        if (!hasArg)
        {
            return new FastMpPortChoice(requested, "game",
                $"no --{ArgName}; the game's port {requested} stands");
        }
        string raw = (argValue ?? string.Empty).Trim();
        if (!int.TryParse(raw, out int port) || port <= 0 || port > 65535)
        {
            return new FastMpPortChoice(requested, "game",
                $"--{ArgName} '{raw}' is not a port in 1..65535; REFUSED, " +
                $"the game's port {requested} stands");
        }
        if (requested != GameDefault)
        {
            return new FastMpPortChoice(requested, "game",
                $"the game asked for {requested}, not the fastmp " +
                $"{GameDefault}; --{ArgName} {port} only moves {GameDefault}");
        }
        return new FastMpPortChoice(port, "arg", $"--{ArgName} {port}");
    }
}
