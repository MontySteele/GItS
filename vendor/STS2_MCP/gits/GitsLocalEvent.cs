// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// THE EVENT ROOM'S LOCAL MODEL, READ WITHOUT TAKING THE STATE CALL DOWN.
//
// THE FIND (live look 8b, 2026-09-16, Furina run `R9RDN1FJJ5YZ`). `get_state`
// answered twice with
//
//     [STS2 MCP] HandleGetState: System.ArgumentOutOfRangeException
//       at EventSynchronizer.GetEventForPlayer
//       at McpMod.BuildEventState
//
// on the Event Room path. The whole screen was lost both times -- not the
// options, the STATE call -- so a seat standing in an event room was handed an
// error instead of a room.
//
// THE CALL SITE IS OURS. `EB-682`'s fallback reads `eventRoom
// .LocalMutableEvent` when the UI read found no buttons, and that property is
// `RunManager.Instance.EventSynchronizer.GetLocalEvent()`, whose whole body
// (decompiled, sts2.dll 0.111.0 `41cef1ea`) is
//
//     public EventModel GetEventForPlayer(Player player)
//     {
//         int playerSlotIndex = _playerCollection.GetPlayerSlotIndex(player);
//         return _events[playerSlotIndex];
//     }
//
// -- an unguarded index into a private array. A slot index the collection
// cannot name answers -1, and an `_events` array that has not been sized for
// this room yet is shorter than the index; either one is the
// `ArgumentOutOfRangeException` above. The game never notices because every
// one of ITS callers is inside an event whose synchronizer has already begun;
// the bridge polls, so the bridge meets the moment before that.
//
// SO THE GUARD GOES HERE AND NOT UPSTREAM. Nothing about the game is wrong:
// what is wrong is a state read that can throw, which is
// `GitsRefusalSource.cs`'s standing rule for this bridge in one line -- "a
// state read must never throw". A room whose local model cannot be read falls
// back to the CANONICAL event, which is the same room's own model and is what
// `BuildEventState` reads every other field off, so the screen still answers
// with a heading, a body and whatever options the UI read found -- the empty-
// options shape at worst, rather than no shape at all.
//
// LOGGED ONCE PER PROCESS, deliberately. A poller asks for the state several
// times a second and a line per poll would bury the run; a line per process
// says the thing happened and names it, and the wire's own `from_model` key
// is absent on exactly the rows this fallback cost, which is the readable
// half of the same fact.
//
// NAMES NO GAME TYPE, `GitsSettledHp.cs`'s rule: the read is handed in as a
// callback from `McpMod.StateBuilder.cs`, so this file compiles against
// nothing that can move under it.

using System;
using Godot;

namespace STS2_MCP;

public static class GitsLocalEvent
{
    private static bool _reported;

    /// <summary>
    /// Run <paramref name="read"/>, or answer <c>default</c> where it throws.
    /// </summary>
    public static T? OrNothing<T>(Func<T?> read) where T : class
    {
        try
        {
            return read();
        }
        catch (Exception e)
        {
            if (!_reported)
            {
                _reported = true;
                GD.PrintErr(
                    "[STS2 MCP] GItS: the event room's local model could not "
                  + $"be read ({e.GetType().Name}: {e.Message}); falling back "
                  + "to the room's canonical event for the rest of this "
                  + "process. This message is printed once.");
            }
            return null;
        }
    }

    /// <summary>Test seam: forget that the line has been printed.</summary>
    public static void ResetForTests() => _reported = false;
}
