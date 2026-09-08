// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// `EB-681`. WHAT REACTED THIS TURN, ON THE WIRE.
//
// THE GAP. A reaction is the whole of what several kits are ABOUT and the
// state feed carried no trace of one: the aura is consumed, the effect lands
// on the board, and a reader is left with a number to work backwards from.
// Kokomi r27 lane 2 met a beat with TWO Electro-Charged procs in it -- Slack
// Water's Hydro, Shinobu's Electro, then the Tamakushi Casket's answering
// Hydro ping onto the fresh Electro aura -- and reconstructed both of them
// from a Poison count that was twice what the keyword prints. Lane 1 could not
// settle whether a Crystallize had fired at all.
//
// WHAT THIS READS, AND WHY IT IS REFLECTION -- `GitsKokomiPlan.cs`'s posture
// and reasons exactly. The log lives in the klee mod
// (`KleeCode/Powers/ReactionLog.cs`), the bridge cannot reference that
// assembly, and a compile-time reference would make this bridge refuse to load
// without it. Reflection makes "no klee mod" mean "no reaction log", which is
// the truth. Probed once, cached including the null, and every failure
// swallowed, because a state read must never throw.
//
// SHIPPED AND NOT ARM-GATED, which is the one place this differs from the Plan
// queue beside it: `ReactionLog` is in the mod's shipped code because every
// arm reacts, so a release klee.dll answers this and a Klee lane gets its
// Overloaded named as a Kokomi lane gets its Electro-Charged.
//
// THE CONTRACT. `KleeMod.Powers.ReactionLog.Snapshot()` returns a
// List<Dictionary<string, object?>> of primitives -- `reaction`, `source`,
// `target`, `combat_id` -- and this file hands it straight to the wire under
// `player.reactions`. An ABSENT key means "no reaction log in this build"; an
// EMPTY list means "the log is here and nothing reacted this turn". Those are
// different facts and `understudy/blindplay_board.reaction_log` tells them
// apart.
//
// READ-ONLY. Nothing here resolves a reaction or clears a log. It is a
// serialiser.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Godot;

namespace STS2_MCP;

public static partial class McpMod
{
    private const string GitsReactionLogType = "KleeMod.Powers.ReactionLog";
    private const string GitsReactionLogMethod = "Snapshot";

    private static bool _gitsReactionsProbed;
    private static MethodInfo? _gitsReactionsSnapshot;

    /// <summary>
    /// Locate the mod's reaction-log snapshot once. A null result is cached
    /// too, `GitsKokomiPlanSnapshot`'s own bargain: a build without the type
    /// will not grow one mid-session and a state read should not pay for an
    /// assembly walk on every poll.
    /// </summary>
    private static MethodInfo? GitsReactionLogSnapshot()
    {
        if (_gitsReactionsProbed) return _gitsReactionsSnapshot;
        _gitsReactionsProbed = true;
        try
        {
            var type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(a =>
                {
                    try { return a.GetType(GitsReactionLogType, false); }
                    catch { return null; }
                })
                .FirstOrDefault(t => t != null);
            _gitsReactionsSnapshot = type?.GetMethod(
                GitsReactionLogMethod,
                BindingFlags.Static | BindingFlags.Public);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] reaction log probe failed: {ex.Message}");
            _gitsReactionsSnapshot = null;
        }
        return _gitsReactionsSnapshot;
    }

    /// <summary>
    /// This turn's reactions, in the order they resolved, or NULL when this
    /// build carries no log. Null keeps the wire key ABSENT rather than
    /// present-and-empty, which is the distinction the header names.
    /// </summary>
    internal static List<Dictionary<string, object?>>? GitsReactionLogState()
    {
        var snapshot = GitsReactionLogSnapshot();
        if (snapshot == null) return null;
        try
        {
            return snapshot.Invoke(null, Array.Empty<object>())
                   as List<Dictionary<string, object?>>;
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] reaction log snapshot failed: "
                        + $"{ex.Message}");
            return null;
        }
    }
}
