// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// `EB-349` and `EB-611`. NO RECORD OF A CARD RESOLVING IS ON THE WIRE.
//
// THE STANDING FACT this closes is written on the page itself, in
// `understudy/blindplay_notes.AUTO_TURN_NOTE`: "What it played, what it aimed
// at and what each card did are not on this page's data feed -- THERE IS NO
// RECORD OF A CARD RESOLVING ON THE WIRE AT ALL." Every screen this bridge
// sends is an AFTER-STATE. A reader gets the board a turn left behind and
// never the turn.
//
// THE TWO FINDS THAT SHARE ONE LEDGER.
//
//   `EB-349` (Kokomi r4d act 3, 1). A relic that plays a turn FOR you --
//   Vakuu -- took six openings, five of them from an empty hand, and nothing
//   printed anywhere said a turn had happened. The page can name the relic
//   off its own printed sentence (it does), and it can state the gap (it
//   does), and that is the whole of what a page with no feed can do.
//
//   `EB-611` (Klee r23 lane 2 (c) 3). A multi-hit random `Set off` prints
//   only the after-state, so a seat could confirm WHICH bodies were hit and
//   never the ORDER -- and a random-target multi-hit is exactly the card
//   whose order decides whether the beat made sense. "Rapid Fire on a hallway
//   prints four ordered lines" is the row's acceptance and it is one ledger's
//   worth of work away from the first.
//
// SO: ONE ROW PER RESOLVED CARD, with the hits under it in hit order. The
// card's id and printed name, whether the GAME played it rather than the
// player (`CardPlay.IsAutoPlay`, the game's own flag -- not a guess about
// which relic is holding the controller), and per hit the body and the
// number that landed on it.
//
// `MeterLedger` IS A DIFFERENT ROUTE AND WAS ALREADY CHECKED. It files a row
// per METER MOVEMENT with no bodies on it (`EB-611`'s read of 2026-09-07 says
// so), so it can say a Spark was spent and never what was hit.
//
// WHAT THIS READS, AND WHY IT IS REFLECTION -- `GitsReactionLog.cs`'s posture
// and reasons exactly, down to the sentence. The ledger lives in the klee mod
// (`KleeCode/Powers/ResolutionLedger.cs`), the bridge cannot reference that
// assembly, and a compile-time reference would make this bridge refuse to
// load without it. Reflection makes "no klee mod" mean "no resolution
// ledger", which is the truth. Probed once, cached including the null, and
// every failure swallowed, because a state read must never throw.
//
// THE COUNTERS' OWN TURN WINDOW, like `ReactionLog` and `RelicAnswerLog` and
// for their reason: the rows are about the turn the reader is looking at, and
// a row that resolved after the player ended their turn carries exactly one
// turn rather than being dropped before a page could print it (`EB-710`).
//
// THE CONTRACT. `KleeMod.Powers.ResolutionLedger.Snapshot()` returns a
// List<Dictionary<string, object?>> of primitives -- `card_id`, `card`,
// `auto_played`, `carried`, `hits` (itself a list of `{target, amount,
// blocked, combat_id, killed}` dictionaries) -- and this file hands it
// straight to the wire under `player.resolutions`. An ABSENT key means "no resolution ledger in
// this build"; an EMPTY list means "the ledger is here and nothing resolved
// this turn". Those are different facts and
// `understudy/blindplay_board.resolutions` tells them apart.
//
// READ-ONLY. Nothing here plays, resolves or clears anything. It is a
// serialiser.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Godot;

namespace STS2_MCP;

public static partial class McpMod
{
    /// <summary>The wire key. Spelled once so the bridge and the blind page
    /// cannot drift apart.</summary>
    internal const string GitsResolutionsKey = "resolutions";

    private const string GitsResolutionLedgerType =
        "KleeMod.Powers.ResolutionLedger";
    private const string GitsResolutionLedgerMethod = "Snapshot";

    private static bool _gitsResolutionsProbed;
    private static MethodInfo? _gitsResolutionsSnapshot;

    /// <summary>
    /// Locate the mod's resolution-ledger snapshot once, on
    /// <see cref="GitsReactionLogSnapshot"/>'s own terms and for its reasons:
    /// a build without the type will not grow one mid-session, and a state
    /// read should not pay for an assembly walk on every poll.
    /// </summary>
    private static MethodInfo? GitsResolutionLedgerSnapshot()
    {
        if (_gitsResolutionsProbed) return _gitsResolutionsSnapshot;
        _gitsResolutionsProbed = true;
        try
        {
            var type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(a =>
                {
                    try { return a.GetType(GitsResolutionLedgerType, false); }
                    catch { return null; }
                })
                .FirstOrDefault(t => t != null);
            _gitsResolutionsSnapshot = type?.GetMethod(
                GitsResolutionLedgerMethod,
                BindingFlags.Static | BindingFlags.Public);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] resolution ledger probe failed: "
                        + $"{ex.Message}");
            _gitsResolutionsSnapshot = null;
        }
        return _gitsResolutionsSnapshot;
    }

    /// <summary>
    /// This turn's card resolutions, in the order they resolved, or NULL when
    /// this build carries no ledger. Null keeps the wire key ABSENT rather
    /// than present-and-empty, which is the distinction the header names.
    /// </summary>
    internal static List<Dictionary<string, object?>>? GitsResolutionState()
    {
        var snapshot = GitsResolutionLedgerSnapshot();
        if (snapshot == null) return null;
        try
        {
            return snapshot.Invoke(null, Array.Empty<object>())
                   as List<Dictionary<string, object?>>;
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] resolution ledger snapshot failed: "
                        + $"{ex.Message}");
            return null;
        }
    }
}
