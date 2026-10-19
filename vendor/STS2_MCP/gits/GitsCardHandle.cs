// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// A HAND CARD'S OWN HANDLE (seat page backlog wave 2, 2026-10-19).
//
// The wire carried no card instance id, so the blind page numbered repeated
// titles ("Sting (1)", "Sting (2)") and found each copy again after a play by
// aligning the old hand to the new one, title by title. That guess slips when
// a play reorders or rewrites the hand: a Kokomi seat spent The Shape of
// Water on a renumbered Sting, and another read "Frantic Escape (2)" as a
// different copy after a play.
//
// The game keeps one `CardModel` object per card while it moves between
// piles, so the object itself is the identity. This hands each one a small
// number the first time the bridge sees it, held in a weak table so a card
// the game drops is not kept alive. The number means nothing outside this
// game session; the page uses it only to keep a copy's label for the turn.
//
// READ-ONLY. Nothing here changes a card.

using System.Runtime.CompilerServices;
using System.Threading;
using MegaCrit.Sts2.Core.Models;

namespace STS2_MCP;

public static class GitsCardHandle
{
    /// <summary>The wire key on a hand card.</summary>
    public const string Key = "handle";

    private sealed class Box
    {
        public Box(int value) => Value = value;
        public int Value { get; }
    }

    private static readonly ConditionalWeakTable<CardModel, Box> Handles = new();
    private static int _next;

    /// <summary>This card object's handle, minted on first sight.</summary>
    public static int Of(CardModel card) =>
        Handles.GetValue(card, _ => new Box(Interlocked.Increment(ref _next))).Value;
}
