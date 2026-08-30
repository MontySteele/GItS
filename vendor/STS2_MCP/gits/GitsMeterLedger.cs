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
