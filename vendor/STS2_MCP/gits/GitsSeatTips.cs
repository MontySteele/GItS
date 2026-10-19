// GItS LOCAL ADDITION - not upstream STS2MCP.
// GItS addition (the tooltip trim, 2026-10-14,
// review/active/tooltip-trim-2026-10-14.md). The blind seat's hover tips.
//
// The klee mod trims a PLAYER's card hover (at most 3 boxes, about 90
// characters a box, no restated base word, a reaction preview only for the
// enemy being aimed at). The sentences it drops are riders blind seats asked
// for, and the seats read the same `card.HoverTips` this bridge serialises
// (`BuildHoverTips`). So every main-thread job (`McpMod.RunOnMainThread`, both
// overloads) runs inside the mod's seat scope,
// `KleeMod.Cards.TipAudience.EnterSeat()` / `ExitSeat()`, and the page reads
// every sentence it read before the trim, word for word.
//
// THE NEWCOMER SEAT (2026-10-19). A state read asked with `?audience=player`
// runs its builder OUTSIDE the seat scope (`GitsAsPlayer`), so the page reads
// the player's trimmed hovers, and the state carries `tip_audience: "player"`
// so the page can tell this bridge from an older one that ignored the ask.
//
// REFLECTION, on `GitsFurinaStage.cs`'s terms: no compile-time reference to
// the klee mod, so "no klee mod" means "no seat scope", which is the truth (a
// card with no trim needs none). A hit is cached; a miss is probed again
// every `GitsSeatTipsRetry` jobs, because a job that runs before the klee
// assembly has loaded must not leave the seats on trimmed tips for the rest
// of the process. Every failure is swallowed: a state read must never throw.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Godot;

namespace STS2_MCP;

public static partial class McpMod
{
    private const string GitsTipAudienceType = "KleeMod.Cards.TipAudience";

    private const int GitsSeatTipsRetry = 200;

    private static int _gitsSeatTipsWait;
    private static MethodInfo? _gitsSeatEnter;
    private static MethodInfo? _gitsSeatExit;

    private static void GitsSeatTipsProbe()
    {
        if (_gitsSeatEnter != null && _gitsSeatExit != null) return;
        if (_gitsSeatTipsWait-- > 0) return;
        _gitsSeatTipsWait = GitsSeatTipsRetry;
        try
        {
            var type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(a =>
                {
                    try { return a.GetType(GitsTipAudienceType, false); }
                    catch { return null; }
                })
                .FirstOrDefault(t => t != null);
            _gitsSeatEnter = type?.GetMethod(
                "EnterSeat", BindingFlags.Static | BindingFlags.Public);
            _gitsSeatExit = type?.GetMethod(
                "ExitSeat", BindingFlags.Static | BindingFlags.Public);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] seat tips probe failed: {ex.Message}");
            _gitsSeatEnter = null;
            _gitsSeatExit = null;
        }
    }

    /// <summary>Read hover tips as a blind seat until
    /// <see cref="GitsSeatTipsExit"/>.</summary>
    internal static void GitsSeatTipsEnter()
    {
        GitsSeatTipsProbe();
        try { _gitsSeatEnter?.Invoke(null, null); }
        catch (Exception) { /* a state read must never throw */ }
    }

    /// <summary>Leave the seat scope <see cref="GitsSeatTipsEnter"/> opened.
    /// </summary>
    internal static void GitsSeatTipsExit()
    {
        try { _gitsSeatExit?.Invoke(null, null); }
        catch (Exception) { /* a state read must never throw */ }
    }

    /// <summary>The newcomer seat: whether a state read asked for the
    /// player's hover tips (`?audience=player`).</summary>
    internal static bool GitsAudienceIsPlayer(System.Net.HttpListenerRequest request)
    {
        try { return request.QueryString["audience"] == "player"; }
        catch (Exception) { return false; }
    }

    /// <summary>Run a state builder as the PLAYER reads it: the seat scope
    /// <see cref="McpMod.RunOnMainThread{T}"/> opened is left for the length
    /// of the build and entered again after, and the state is marked
    /// <c>tip_audience: "player"</c>. Called on the main thread only.</summary>
    internal static Dictionary<string, object?> GitsAsPlayer(
        Func<Dictionary<string, object?>> build)
    {
        GitsSeatTipsExit();
        // Swirl legibility (2026-10-19): the hand rows carry the aim previews
        // on this read only (`GitsAimPreview.cs`).
        GitsSetPlayerAudience(true);
        Dictionary<string, object?> state;
        try { state = build(); }
        finally
        {
            GitsSetPlayerAudience(false);
            GitsSeatTipsEnter();
        }
        state["tip_audience"] = "player";
        return state;
    }
}
