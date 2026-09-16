// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// `EB-216` / R225's clause. THE PER-PLAY METER LEDGER, ON THE WIRE.
//
// THE GAP, EXACTLY. The bridge serialises a meter as an ID and an AMOUNT --
// `player.resources` for BaseLib's registered ones, `player.status` for the
// power-shaped ones, which is where the Spark bank rides. That says what the
// bank IS and never how it got there, so a blind run's record cannot rebuild
// a single play's arithmetic: a bank reading 2 after a play might have paid 3
// and been refunded 3 by two detonations, or paid nothing at all. The blind
// tester on the Klee Sparks run reported that confusion in as many words and
// nothing in the record could adjudicate it.
//
// R225 ruled the four fields -- bank before, price paid, gains BY SOURCE, bank
// after. The mod keeps them (`KleeMod.Diagnostics.MeterLedger`); this file is
// the read.
//
// A SEPARATE ROUTE AND NOT A KEY ON `player`, deliberately. The state payload
// is what `understudy/blindplay.py` builds the TESTER'S PAGE out of, and the
// ledger names engine events in a developer's vocabulary
// (`relic:pounding_surprise/detonation`, `rule:threshold_consume`). A page is
// a grading surface (R101b) and the shortest way to keep the ledger off it is
// for it never to arrive on the same payload. The driver GETs this route on
// the frames it snapshots and files it beside the board.
//
// WHY IT IS REFLECTION. Same posture as `GitsResources.cs` toward BaseLib,
// `GitsSparkPrice.cs` toward the Spark price and `GitsKurageMemory.cs` toward
// the memory rule, for the same reason: a compile-time reference would make
// this bridge refuse to load with no klee mod present. Reflection makes "no
// klee mod" mean "no ledger", which is the truth. Probed once, the null cached
// with the hit, every failure swallowed -- a state read must never throw.
//
// THE CONTRACT. `KleeMod.Diagnostics.MeterLedger.Snapshot()` returns a
// `List<Dictionary<string, object?>>` of primitives, oldest row first. Per
// row: `index, meter, turn, card, card_name, before, price_paid,
// gains {source: n}, after, entries [{source, delta, bank_before}]`. `after`
// is DERIVED from before/price/gains rather than re-read off the bank, which
// is the mod-side header's point 2 and is why a row is internally consistent
// whenever it is polled. `meter` is a FIELD: Sparks is the meter that needs it
// today and Charge and Encore are the same shape.
//
// AN ABSENT LEDGER IS `available: false` AND AN EMPTY LIST -- "this build has
// no klee mod" is a different fact from "nothing has moved a meter yet", and a
// reader is entitled to tell them apart.
//
// READ-ONLY. Nothing here opens a row, moves a bank or plays a card.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Reflection;
using Godot;

namespace STS2_MCP;

public static partial class McpMod
{
    private const string GitsMeterLedgerType = "KleeMod.Diagnostics.MeterLedger";
    private const string GitsMeterLedgerMethod = "Snapshot";

    private static bool _gitsLedgerProbed;
    private static MethodInfo? _gitsLedgerSnapshot;

    /// <summary>
    /// Locate the snapshot method once. The null is cached too: a game with no
    /// klee mod will not grow one mid-session, and a poll should not pay for a
    /// full assembly walk. The type is `internal`, so the lookup asks for
    /// non-public statics as well -- it is a diagnostics surface and not part
    /// of the mod's public shape.
    /// </summary>
    private static MethodInfo? GitsMeterLedgerSnapshot()
    {
        if (_gitsLedgerProbed) return _gitsLedgerSnapshot;
        _gitsLedgerProbed = true;
        try
        {
            Type? type = null;
            foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
            {
                try { type = asm.GetType(GitsMeterLedgerType, false); }
                catch { type = null; }
                if (type != null) break;
            }

            _gitsLedgerSnapshot = type?.GetMethod(
                GitsMeterLedgerMethod,
                BindingFlags.Static | BindingFlags.Public
                | BindingFlags.NonPublic);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] meter ledger probe failed: {ex.Message}");
            _gitsLedgerSnapshot = null;
        }
        return _gitsLedgerSnapshot;
    }

    /// <summary>
    /// The ledger's rows, or null when this build has no klee mod to ask.
    /// </summary>
    private static List<Dictionary<string, object?>>? GitsMeterLedgerRows()
    {
        var snapshot = GitsMeterLedgerSnapshot();
        if (snapshot == null) return null;
        try
        {
            return snapshot.Invoke(null, Array.Empty<object>())
                   as List<Dictionary<string, object?>>;
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] meter ledger read failed: "
                        + $"{ex.Message}");
            return null;
        }
    }

    /// <summary>
    /// `EB-610`. WHERE THIS TURN'S SPARKS CAME FROM, on the PLAYER's payload.
    ///
    /// THE FIND (Klee r23 lane 2, fight 5, turn 4). "A Spark appeared with no
    /// Bomb on the field": the bank went 2 to 3 across Kaeya and Rapid Fire on
    /// a bare board, and the only sentence on any screen naming a Spark source
    /// is the relic's, which says "whenever a Bomb goes off". The page's Spark
    /// row says what the word MEANS and never where the number came from, so
    /// the reader's whole model of the meter was the one line that happened to
    /// be printed -- and the meter contradicted it.
    ///
    /// AND WHY THIS IS NOT THE LEDGER ROUTE BELOW. This file's own header
    /// argues the ledger must never arrive on the same payload as the board,
    /// because its rows name ENGINE EVENTS in a developer's vocabulary
    /// (`relic:pounding_surprise/detonation`) and a page is a grading surface
    /// (R101b). That argument is about the ROWS, not about the fact, and it
    /// still stands: what goes out here is the narrow read the page needs --
    /// the GAINS of the SPARK meter on the CURRENT turn, positive entries
    /// only, each with the card its row was opened on -- and
    /// `understudy/blindplay_board.spark_sources` turns the event name into a
    /// printed word before any page sees it. No price, no bank, no other
    /// meter, no other turn.
    ///
    /// THE TURN IS THE LARGEST ONE THE SPARK ROWS CARRY, which needs no game
    /// type: the ledger is reset per fight (`MeterLedger.ResetFight`) and its
    /// turn numbers only climb, so the newest turn present IS this turn.
    ///
    /// ABSENT WHERE THE LEDGER IS ABSENT, EMPTY where this turn moved no
    /// Spark -- the same two facts the route below keeps apart, kept apart
    /// here for the same reason.
    /// </summary>
    internal static List<Dictionary<string, object?>>? GitsSparkSourcesState()
    {
        var rows = GitsMeterLedgerRows();
        if (rows == null) return null;
        var sources = new List<Dictionary<string, object?>>();
        try
        {
            var turn = int.MinValue;
            foreach (var row in rows)
            {
                if (!GitsIsSparkRow(row)) continue;
                var rowTurn = GitsLedgerInt(row, "turn");
                if (rowTurn > turn) turn = rowTurn;
            }
            if (turn == int.MinValue) return sources;

            foreach (var row in rows)
            {
                if (!GitsIsSparkRow(row)) continue;
                if (GitsLedgerInt(row, "turn") != turn) continue;
                var card = row.TryGetValue("card_name", out var name)
                    ? name as string ?? string.Empty
                    : string.Empty;
                if (!row.TryGetValue("entries", out var raw)
                    || raw is not IEnumerable<object?> entries) continue;
                foreach (var entry in entries)
                {
                    if (entry is not Dictionary<string, object?> e) continue;
                    var delta = GitsLedgerInt(e, "delta");
                    if (delta <= 0) continue;
                    sources.Add(new Dictionary<string, object?>
                    {
                        ["source"] = e.TryGetValue("source", out var s)
                            ? s as string ?? string.Empty : string.Empty,
                        ["amount"] = delta,
                        // The card the ROW was opened on, which is what names
                        // a gain whose event word is the rule that paid rather
                        // than the thing the player did: a Companion play
                        // reads `companion:personal/play`, and what the player
                        // saw was Kaeya.
                        ["card"] = card,
                    });
                }
            }
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] spark sources read failed: "
                        + $"{ex.Message}");
            return sources;
        }
        return sources;
    }

    private static bool GitsIsSparkRow(Dictionary<string, object?> row) =>
        row.TryGetValue("meter", out var meter) && (meter as string) == "spark";

    /// <summary>An int off a ledger map, and never a throw. The values are
    /// boxed ints today and no reader may depend on that staying true.</summary>
    private static int GitsLedgerInt(Dictionary<string, object?> map, string key)
    {
        try
        {
            return map.TryGetValue(key, out var value) && value != null
                ? Convert.ToInt32(value)
                : 0;
        }
        catch (Exception)
        {
            return 0;
        }
    }

    /// <summary>
    /// GET only. The ledger is a read; there is no op that writes one, and a
    /// POST arm would be a door nothing needs.
    /// </summary>
    private static void HandleGitsMeterLedger(
        HttpListenerRequest request, HttpListenerResponse response)
    {
        try
        {
            if (request.HttpMethod != "GET")
            {
                SendError(response, 405, "Method not allowed");
                return;
            }

            var rows = GitsMeterLedgerRows();
            SendJson(response, new Dictionary<string, object?>
            {
                ["status"] = "ok",
                ["available"] = rows != null,
                ["rows"] = rows ?? new List<Dictionary<string, object?>>(),
                ["count"] = rows?.Count ?? 0,
            });
        }
        catch (Exception ex)
        {
            SendError(response, 500, $"meter ledger failed: {ex.Message}");
        }
    }
}
