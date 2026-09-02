using System;
using System.Collections.Generic;
using System.Linq;

namespace KleeMod.Diagnostics;

/// <summary>
/// `EB-216`, R225's clause. THE PER-PLAY METER LEDGER: for every card played,
/// <c>before / price paid / gains by source / after</c>.
///
/// THE GAP THIS FILLS. The wire reports a meter as an ID and an AMOUNT. That
/// says what the bank IS and never how it got there, so a blind run's record
/// could not rebuild a single play's arithmetic: a bank that reads 2 after a
/// play might have paid 3 and been refunded 3 by two detonations, or paid
/// nothing at all. The blind tester on the Klee Sparks run reported exactly
/// that confusion ("the screen still showed Spark 1 and allowed Ka-pow! to be
/// played, but the Spark disappeared afterward") and nothing in the record
/// could adjudicate it. R225 ruled the four-field ledger; this is it.
///
/// INSTRUMENT WORK. It does not gate an arm, it changes no number, and no
/// published record is re-graded on it (R101b).
///
/// FIVE THINGS ABOUT THE SHAPE, each of which is a decision:
///
/// 1. **`meter` is a field, not a class.** Sparks is the meter that needs it
///    today; Charge and Encore are the same shape (a bank, a price, gains
///    from more than one engine event) and will want the same rows. Nothing
///    here knows the word "spark" except as a caller's string.
///
/// 2. **`after` is DERIVED — <c>before - price_paid + sum(gains)</c> — and not
///    a second read of the bank.** Hook ordering among power subscribers is
///    not guaranteed: <c>SparkPower.AfterCardPlayed</c>'s threshold consume
///    and the diagnostics hook that closes a row are two subscribers to one
///    event, and a re-read taken on the wrong side of that ordering would
///    disagree with the deltas printed beside it. Deriving it means the row is
///    internally consistent by construction, whenever it is read. Each entry
///    ALSO carries the bank it saw before its own mutation, so a reader who
///    wants the observed value has it and can compare.
///
/// 3. **A row stays OPEN until the next play opens.** Deltas keep landing on
///    it — a detonation refund resolving after the card's own effects belongs
///    to that card's play, and a snapshot polled between the two would
///    otherwise report a play that paid and never gained. The API reads open
///    rows as they stand, which is the truth at the moment of the read.
///
/// 4. **A delta with no play open still lands.** Turn-start kit responses and
///    the combat-start windfall are not plays; they open an implicit row whose
///    card is empty and whose `before` is the bank the first entry saw. A
///    ledger that dropped them would not add up.
///
/// 5. **No game types, deliberately** — same posture as
///    <c>vendor/STS2_MCP/gits/GitsPort.cs</c>, and for the same reason: the
///    arithmetic every downstream count rests on must be exercisable
///    headlessly, and <c>klee-mod/KleeTests/MeterLedgerTests.cs</c> exercises
///    THIS file rather than a fork of it.
///
/// THE THREE TELEMETRY RULES APPLY (PlayTelemetry.cs): it never touches game
/// state, never consumes RNG, and every public entry point swallows its own
/// exceptions — a measurement that can lose a run is worse than no
/// measurement.
///
/// PUBLIC, unlike its neighbours in this directory, for the reason point 5
/// gives: <c>klee-mod/KleeTests/MeterLedgerTests.cs</c> is a separate assembly
/// and the arithmetic here is what every downstream count rests on. The
/// alternative was an `InternalsVisibleTo` attribute nothing else in this mod
/// needs, or an IL-shape assertion standing in for the arithmetic itself.
/// </summary>
public static class MeterLedger
{
    /// <summary>The meter name the Spark sites pass. A string, not a type.</summary>
    public const string Spark = "spark";

    /// <summary>
    /// Kokomi's Charge bank (`EB-273`). Point 1 above promised this: "Charge
    /// and Encore are the same shape and will want the same rows", and the
    /// Python reader took the meter as a PARAMETER for the same reason
    /// (<c>understudy/blindplay.meter_plays(meter=...)</c>), so naming it here
    /// is the whole of the wiring on that side -- no shape moves.
    /// </summary>
    public const string Charge = "charge";

    /// <summary>
    /// The Kokomi overhaul's Plan queue (`EB-273`), whose BANK is the number of
    /// Plans waiting on the jellyfish.
    ///
    /// A QUEUE IS A METER, and that is a reading rather than a stretch: the
    /// arm's brief prices cards in Plans ("the jellyfish carries out your front
    /// Plan now"), the queue depth is what the strip draws and what
    /// <c>player.kokomi_plans</c> already carries on the wire, and R240/R241
    /// retired the Tide that used to be her number. The four fields say exactly
    /// what a grader needs of it -- the depth before a play, what the play
    /// spent, what it wrote, the depth after.
    /// </summary>
    public const string Plan = "plan";

    /// <summary>
    /// How many rows are kept. A whole fight is tens of plays; the cap exists
    /// so a long unattended session cannot grow this without bound, and the
    /// OLDEST rows are the ones a grader has already read.
    /// </summary>
    public const int MaxRows = 400;

    private sealed class Entry
    {
        internal string Source = "";
        internal int Delta;
        internal int BankBefore;
    }

    private sealed class Row
    {
        internal int Index;
        internal string Meter = "";
        internal int Turn;
        internal string CardId = "";
        internal string CardName = "";
        internal int Before;
        internal readonly List<Entry> Entries = new();
    }

    private static readonly object Lock = new();
    private static readonly List<Row> Rows = new();
    private static readonly Dictionary<string, Row> OpenRows = new();
    private static int _next;
    private static int _turn;

    /// <summary>
    /// Forget everything. Called at the start of a combat: a ledger that
    /// carried one fight's rows into the next would let a grader attribute a
    /// spend to the wrong fight.
    /// </summary>
    public static void ResetFight()
    {
        try
        {
            lock (Lock)
            {
                Rows.Clear();
                OpenRows.Clear();
                _next = 0;
                _turn = 0;
            }
        }
        catch (Exception)
        {
            // Telemetry never throws into a combat hook.
        }
    }

    /// <summary>The turn implicit rows are stamped with.</summary>
    public static void OpenTurn(int turn)
    {
        try
        {
            lock (Lock) { _turn = turn; }
        }
        catch (Exception)
        {
        }
    }

    /// <summary>
    /// Open the row a play's deltas land on. Called once per play (the
    /// caller's <c>IsFirstInSeries</c> gate), with the bank as it stood before
    /// anything the card does.
    /// </summary>
    public static void OpenPlay(string meter, string cardId, string cardName,
                                  int turn, int before)
    {
        try
        {
            if (string.IsNullOrEmpty(meter)) return;
            lock (Lock)
            {
                _turn = turn;
                var row = new Row
                {
                    Index = ++_next,
                    Meter = meter,
                    Turn = turn,
                    CardId = cardId ?? "",
                    CardName = cardName ?? "",
                    Before = before,
                };
                OpenRows[meter] = row;
                Rows.Add(row);
                Trim();
            }
        }
        catch (Exception)
        {
        }
    }

    /// <summary>
    /// One mutation of one meter, named by the ENGINE EVENT that made it.
    /// <paramref name="delta"/> is signed and is the OBSERVED change (the
    /// caller reads the bank either side of its own mutation), so a grant the
    /// game's own modifier chain resized is recorded at the size it landed.
    /// <paramref name="bankBefore"/> is what that mutation saw.
    /// </summary>
    public static void Note(string meter, string source, int delta,
                              int bankBefore)
    {
        try
        {
            if (string.IsNullOrEmpty(meter) || delta == 0) return;
            lock (Lock)
            {
                if (!OpenRows.TryGetValue(meter, out var row))
                {
                    // NOT A PLAY. A turn-start kit response or a combat-start
                    // windfall still has to add up, so it gets a row of its
                    // own whose `before` is the bank this entry saw.
                    row = new Row
                    {
                        Index = ++_next,
                        Meter = meter,
                        Turn = _turn,
                        CardId = "",
                        CardName = "",
                        Before = bankBefore,
                    };
                    OpenRows[meter] = row;
                    Rows.Add(row);
                    Trim();
                }
                row.Entries.Add(new Entry
                {
                    Source = string.IsNullOrEmpty(source) ? "unknown" : source,
                    Delta = delta,
                    BankBefore = bankBefore,
                });
            }
        }
        catch (Exception)
        {
        }
    }

    /// <summary>
    /// The ledger as primitives, oldest first, for
    /// <c>vendor/STS2_MCP/gits/GitsMeterLedger.cs</c> to hand to the wire.
    /// Every value is an int, a string, or a map of those; nothing here is a
    /// game type, so the serialiser has nothing to interpret.
    ///
    /// Per row: <c>index, meter, turn, card, card_name, before, price_paid,
    /// gains {source: n}, after, entries [{source, delta, bank_before}]</c>.
    /// </summary>
    public static List<Dictionary<string, object?>> Snapshot()
    {
        try
        {
            lock (Lock)
            {
                return Rows.Select(RowToMap).ToList();
            }
        }
        catch (Exception)
        {
            return new List<Dictionary<string, object?>>();
        }
    }

    private static Dictionary<string, object?> RowToMap(Row row)
    {
        var gains = new Dictionary<string, int>();
        var price = 0;
        foreach (var e in row.Entries)
        {
            if (e.Delta < 0)
            {
                price += -e.Delta;
            }
            else
            {
                gains.TryGetValue(e.Source, out var had);
                gains[e.Source] = had + e.Delta;
            }
        }

        return new Dictionary<string, object?>
        {
            ["index"] = row.Index,
            ["meter"] = row.Meter,
            ["turn"] = row.Turn,
            ["card"] = row.CardId,
            ["card_name"] = row.CardName,
            ["before"] = row.Before,
            ["price_paid"] = price,
            ["gains"] = gains,
            // DERIVED, per the header's point 2.
            ["after"] = row.Before - price + gains.Values.Sum(),
            ["entries"] = row.Entries.Select(e => new Dictionary<string, object?>
            {
                ["source"] = e.Source,
                ["delta"] = e.Delta,
                ["bank_before"] = e.BankBefore,
            }).ToList(),
        };
    }

    /// <summary>Drop the oldest rows past the cap, open ones included -- an
    /// open row that old is a row nothing is going to add to.</summary>
    private static void Trim()
    {
        while (Rows.Count > MaxRows)
        {
            var dropped = Rows[0];
            Rows.RemoveAt(0);
            if (OpenRows.TryGetValue(dropped.Meter, out var open)
                && ReferenceEquals(open, dropped))
            {
                OpenRows.Remove(dropped.Meter);
            }
        }
    }
}
