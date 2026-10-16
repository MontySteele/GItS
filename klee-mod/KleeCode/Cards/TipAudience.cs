namespace KleeMod.Cards;

/// <summary>
/// THE TOOLTIP TRIM (2026-10-14, review/active/tooltip-trim-2026-10-14.md).
/// WHO IS READING THIS HOVER: a player, or a blind seat through the bridge.
///
/// [USER], during the 2026-10-14 Furina run: "her cards still make a million
/// words of tooltips come up". The player hover now follows a house rule (at
/// most 3 boxes, about 90 characters a box, no restated base word, a reaction
/// preview only for the enemy being aimed at), and the sentences it drops are
/// the riders blind seats asked for. The seats read the SAME hover tips off
/// the bridge (<c>McpMod.BuildHoverTips(card.HoverTips)</c>), so cutting them
/// from the hover would cut them from the seat page too. This is the seat-only
/// channel: the bridge enters <see cref="EnterSeat"/> around every main-thread
/// job it runs (<c>GitsSeatTips.cs</c>), and every tip surface that differs
/// between the two readers asks <see cref="Seat"/>. A seat's page therefore
/// reads exactly what it read before the trim, word for word.
///
/// THREAD-STATIC AND COUNTED, because the bridge's jobs run on the game's
/// main thread between frames: a scope is entered and left inside one job,
/// never across a player's hover, and a nested job cannot unset an outer one.
///
/// Display only: nothing here changes a number or a rule.
/// </summary>
public static class TipAudience
{
    [System.ThreadStatic] private static int _seatDepth;

    /// <summary>True while a blind seat's bridge is reading. A player's
    /// hover is never inside a seat scope.</summary>
    public static bool Seat => _seatDepth > 0;

    /// <summary>Called by the bridge (by reflection) before a main-thread
    /// read. Pairs with <see cref="ExitSeat"/>.</summary>
    public static void EnterSeat() => _seatDepth++;

    /// <summary>Called by the bridge after the read, in a finally.</summary>
    public static void ExitSeat()
    {
        if (_seatDepth > 0) _seatDepth--;
    }

    /// <summary>Test seam: read as a seat for the length of a using block.
    /// </summary>
    public static System.IDisposable AsSeat()
    {
        EnterSeat();
        return new Leave();
    }

    private sealed class Leave : System.IDisposable
    {
        private bool _done;
        public void Dispose()
        {
            if (_done) return;
            _done = true;
            ExitSeat();
        }
    }
}
