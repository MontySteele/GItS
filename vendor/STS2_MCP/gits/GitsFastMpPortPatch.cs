// GItS LOCAL ADDITION -- parallel co-op pairs (2026-10-08).
//
// The Harmony half of `GitsFastMpPort.cs`, which holds the rules and says why.
// Two prefixes, each rewriting a `ushort port` argument on its way in:
//
//   ENetHost.StartHost(ushort port, int maxClients)          -- the host's bind
//   ENetClientConnectionInitializer(ulong, string, ushort port) -- the client's
//                                                                  dial target
//
// Both are the CONSUMERS of the game's literal 33771; the call sites pass a
// constant, so there is no field or method upstream of them to patch.
//
// APPLIED BY HAND, NOT BY `PatchAll`. `McpMod.TryApplyHarmonyPatches` calls
// `Apply` in its own try before the attribute scan, so a failure in an
// unrelated settings-UI patch cannot skip these two, and a failure here is
// logged by name. The class carries no `[HarmonyPatch]`, so `PatchAll` never
// applies it a second time.
//
// `BoundPort` is the port last handed to ENet in this process (null until a
// fastmp host starts or a client dials). The lobby state serves it as
// `fastmp_port`, and `understudy/embark_coop.py` refuses a pair whose lobby
// does not read back the port it launched that pair on -- the check that
// turns "the patch did not apply" into a refusal instead of a client joining
// another pair's host.

#nullable enable

using System;
using HarmonyLib;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Multiplayer.Connection;
using MegaCrit.Sts2.Core.Multiplayer.Transport.ENet;

namespace STS2_MCP;

public static class GitsFastMpPortPatch
{
    public static int? BoundPort { get; private set; }

    public static void Apply(Harmony harmony)
    {
        var host = AccessTools.Method(typeof(ENetHost), nameof(ENetHost.StartHost),
            new[] { typeof(ushort), typeof(int) });
        if (host == null)
            throw new MissingMethodException("ENetHost", "StartHost(ushort, int)");
        harmony.Patch(host, prefix: new HarmonyMethod(typeof(GitsFastMpPortPatch),
            nameof(HostPrefix)));

        var client = AccessTools.Constructor(typeof(ENetClientConnectionInitializer),
            new[] { typeof(ulong), typeof(string), typeof(ushort) });
        if (client == null)
            throw new MissingMethodException("ENetClientConnectionInitializer",
                ".ctor(ulong, string, ushort)");
        harmony.Patch(client, prefix: new HarmonyMethod(typeof(GitsFastMpPortPatch),
            nameof(ClientPrefix)));

        Godot.GD.Print("[STS2 MCP] fastmp port patch applied (host bind + client dial)");
    }

    private static void HostPrefix(ref ushort port) => port = Rewrite(port, "host");

    private static void ClientPrefix(ref ushort port) => port = Rewrite(port, "client");

    private static ushort Rewrite(ushort requested, string role)
    {
        bool has = CommandLineHelper.TryGetValue(GitsFastMpPort.ArgName, out string? value);
        var choice = GitsFastMpPort.Resolve(requested, has, value);
        BoundPort = choice.Port;
        Godot.GD.Print($"[STS2 MCP] fastmp {role} port {choice.Port} from {choice.Source}: {choice.Note}");
        return (ushort)choice.Port;
    }
}
