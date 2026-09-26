// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// 2026-09-26 (wave-3 seat round, Furina lane 3 seat b): HAS THIS CHOOSER
// ALREADY TAKEN ITS PICK?
//
// THE FIND. "Arkhe Alignment's chooser appeared twice at the start of several
// turns, with only one Arkhe played. I answered Ousia both times." The lane's
// game log has exactly ONE `chose cards [KLEEMOD-ARKHE_OUSIA_OPTION]` per
// turn: the game asked once, and the page drew the chooser twice.
//
// THE CAUSE, off the 0.111.0 decompile of `NChooseACardSelectionScreen`:
//
//     private void SelectHolder(NCardHolder cardHolder)
//     { if (Time.GetTicksMsec() - _openedTicks > 350) {
//           _screenComplete = true; ... _completionSource.SetResult(...); } }
//     public async Task<IEnumerable<CardModel>> CardsSelected()
//     { var result = await _completionSource.Task;
//       NOverlayStack.Instance.Remove(this); return result; }
//
// So the pick completes at once, but the screen leaves the overlay stack a
// continuation later; a read in between finds the answered chooser still on
// top. And a press in the screen's first 350 ms is dropped with no word.
//
// WHAT CROSSES: `card_select.answered` (true once the pick is taken, false
// while it is open, absent where the field could not be read). The read
// treats an answered chooser as a transition (`blindplay_read.transient`),
// and `select_card` refuses a press on one and says so when the screen
// ignored a press. Read by reflection off the private `_screenComplete`
// field, by name, so a renamed field leaves the key absent. Never throws.
//
// READ-ONLY.

using System;
using System.Reflection;
using Godot;

namespace STS2_MCP;

public static partial class McpMod
{
    /// <summary>
    /// Whether <paramref name="screen"/> has already taken its pick: true
    /// once it has, false while it is open, null where it cannot be read.
    /// </summary>
    internal static bool? GitsChooserAnswered(Node screen)
    {
        try
        {
            var field = screen.GetType().GetField(
                "_screenComplete",
                BindingFlags.Instance | BindingFlags.NonPublic
                | BindingFlags.Public);
            return field?.GetValue(screen) is bool done ? done : null;
        }
        catch (Exception)
        {
            return null;
        }
    }
}
