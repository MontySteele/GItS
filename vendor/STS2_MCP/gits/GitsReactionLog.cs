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
// `target`, `combat_id`, `carried` -- and this file hands it straight to the
// wire under `player.reactions`. An ABSENT key means "no reaction log in this
// build"; an EMPTY list means "the log is here and nothing reacted this turn".
// Those are different facts and `understudy/blindplay_board.reaction_log`
// tells them apart.
//
// `EB-710` ADDED `carried`, and this file needed no edit for it, which is what
// handing the rows straight through buys. A carried row is one whose reaction
// resolved after the player ended their last turn -- their own end-of-turn
// tenants, or the enemy side -- and which no page has printed: the log used to
// be cleared at the top of the next turn, so "What reacted this turn" read
// Nothing through a run with six Electro-Charged in it. The mod carries such a
// row exactly one turn and the page prints it with its window on the line.
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

    // `EB-695`. THE RELIC-ANSWER LOG, on this file's seam and by the same
    // reflection, because it is the same kind of fact one step over: what
    // LANDED inside a beat that the beat's own number does not account for.
    // Kokomi r30 lane 2 met the Tamakushi Casket's answering 2 named inside a
    // Plan carry-out and named nowhere at all when the debuff card was played
    // from hand -- "the seat subtracted it from HP on every such play".
    private const string GitsRelicAnswerLogType =
        "KleeMod.Powers.RelicAnswerLog";

    private static bool _gitsReactionsProbed;
    private static MethodInfo? _gitsReactionsSnapshot;

    private static bool _gitsRelicAnswersProbed;
    private static MethodInfo? _gitsRelicAnswersSnapshot;

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

    /// <summary>
    /// Locate the mod's relic-answer snapshot once, on
    /// <see cref="GitsReactionLogSnapshot"/>'s own terms and for its reasons.
    /// `EB-695`.
    /// </summary>
    private static MethodInfo? GitsRelicAnswerLogSnapshot()
    {
        if (_gitsRelicAnswersProbed) return _gitsRelicAnswersSnapshot;
        _gitsRelicAnswersProbed = true;
        try
        {
            var type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(a =>
                {
                    try { return a.GetType(GitsRelicAnswerLogType, false); }
                    catch { return null; }
                })
                .FirstOrDefault(t => t != null);
            _gitsRelicAnswersSnapshot = type?.GetMethod(
                GitsReactionLogMethod,
                BindingFlags.Static | BindingFlags.Public);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] relic answer log probe failed: "
                        + $"{ex.Message}");
            _gitsRelicAnswersSnapshot = null;
        }
        return _gitsRelicAnswersSnapshot;
    }

    /// <summary>
    /// This turn's relic answers, in the order they landed, or NULL when this
    /// build carries no log. `EB-695`, and the same absent / empty /
    /// populated contract the reactions above keep: a relic that answered
    /// nothing this turn is a fact, and no log at all is a different one.
    /// </summary>
    internal static List<Dictionary<string, object?>>? GitsRelicAnswerState()
    {
        var snapshot = GitsRelicAnswerLogSnapshot();
        if (snapshot == null) return null;
        try
        {
            return snapshot.Invoke(null, Array.Empty<object>())
                   as List<Dictionary<string, object?>>;
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] relic answer snapshot failed: "
                        + $"{ex.Message}");
            return null;
        }
    }
}
