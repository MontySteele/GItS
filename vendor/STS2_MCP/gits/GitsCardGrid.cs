// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// `EB-350`. THE GRID PRINTED TWENTY-FIVE ROWS WHATEVER THE DECK WAS.
//
// THE FIND (Kokomi r4d act 2, 10; act 3, 4 and 5). The shop's Card Removal
// grid printed exactly 25 rows against a 38-card deck and again against a
// 29-card deck, and a Klee seat routed into an Elite at 2/62 unseen because
// the screen it was planning on was not the deck.
//
// IT IS THE BRIDGE'S CAP AND NOT THE GAME'S, and the twenty-five is not a
// constant anywhere -- it is a window. `BuildCardSelectState` walks
// `NGridCardHolder`s, and `NCardGrid` is VIRTUALISED: it holds every card in
// its own `_cards` list and allocates holders only for the rows currently on
// screen (`AllocateCardHolders`, `ReallocateAbove`, `ReallocateBelow`,
// decompiled from sts2.dll 0.111.0 `41cef1ea`). A holder walk is therefore a
// screenshot of the viewport, and the number it returns is whatever happens
// to fit. `NCardGrid.CurrentlyDisplayedCards` is the game's own name for
// exactly that set, which is the confirmation that the full list is the OTHER
// one.
//
// SO THIS FILE READS `_cards`. The screen holds `_grid` (a protected field on
// `NCardGridSelectionScreen`) and the grid holds `_cards` (a protected field
// on `NCardGrid`), which is the SORTED, DISPLAY-ORDER list the grid lays its
// rows out from -- `SetCards` sorts into `_cardsCache` and copies it into
// `_cards`, and `InitGrid` walks `_cards` by index. So `_cards[i]` is the
// i-th row of the grid whether or not a holder is standing on it, and the
// indices a page already printed do not move: the visible window starts at
// row 0 when a screen opens, so today's 0..24 are `_cards[0..24]` exactly.
//
// WHY REFLECTION AND NOT A GAME TYPE. Both fields are protected, so no call
// site can reach them without it; and the two names are undocumented in
// `vendor/STS2_MCP/docs/`, so this file answers NULL whenever it cannot read
// them and `McpMod.StateBuilder.cs` falls back to the holder walk it has
// always done. A wire key says which of the two answered, because "these are
// all the cards" and "these are the cards that fit" are different claims and
// a page that could not tell them apart would print the second under the
// first's heading -- which is the r4d defect exactly.
//
// PROBED ONCE PER TYPE AND CACHED INCLUDING THE NULL, `GitsReactionLog.cs`'s
// bargain: the field is either there or it is not, and a state read should
// not pay for a reflection walk on every poll.
//
// READ-ONLY. Nothing here scrolls, selects or lays out anything. It is a
// serialiser.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using Godot;

namespace STS2_MCP;

public static partial class McpMod
{
    /// <summary>Whether the card list on this screen's feed is the whole grid
    /// or only the rows that fit. Always emitted on a grid screen, so a
    /// MISSING key means "bridge predates `EB-350`".</summary>
    internal const string GitsGridCompleteKey = "grid_complete";

    /// <summary>How many cards the grid holds, whatever reached the list.
    /// </summary>
    internal const string GitsGridTotalKey = "grid_total";

    private const BindingFlags GitsGridFlags =
        BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public;

    private static readonly Dictionary<Type, FieldInfo?> _gitsGridField = new();
    private static readonly Dictionary<Type, FieldInfo?> _gitsCardsField = new();

    /// <summary>
    /// Every card the grid on this screen holds, in the grid's own row order,
    /// or NULL when the two protected fields could not be read.
    ///
    /// NULL IS THE SAFE ANSWER and the caller falls back to the holder walk,
    /// which is what this bridge has always sent.
    /// </summary>
    internal static List<object>? GitsGridCards(object? screen)
    {
        if (screen == null) return null;
        try
        {
            var grid = GitsFieldValue(screen, "_grid", _gitsGridField);
            if (grid == null) return null;
            if (GitsFieldValue(grid, "_cards", _gitsCardsField)
                is not IEnumerable cards)
            {
                return null;
            }
            var out_ = new List<object>();
            foreach (var card in cards)
            {
                if (card != null) out_.Add(card);
            }
            return out_;
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] grid card read failed: "
                        + $"{ex.Message}");
            return null;
        }
    }

    /// <summary>
    /// Press one card in the grid that no holder is standing on, through the
    /// screen's own `OnCardClicked(CardModel)`. True when the call was made.
    ///
    /// WHY THIS IS THE RIGHT METHOD AND NOT A SCROLL. `NCardGridSelectionScreen`
    /// declares `protected abstract void OnCardClicked(CardModel card)` and
    /// every subclass -- transform, upgrade, select, enchant -- implements the
    /// screen's whole response to a click there; the grid's `HolderPressed`
    /// signal is wired to it and carries no state of its own
    /// (`ConnectSignalsAndInitGrid`, decompiled from sts2.dll 0.111.0
    /// `41cef1ea`). So this is the same press, minus a viewport.
    ///
    /// FALSE IS THE SAFE ANSWER and the caller says so in words rather than
    /// pretending a card was toggled. Nothing here scrolls the grid, because
    /// a scroll is a second thing that can go wrong and the click does not
    /// need one.
    /// </summary>
    internal static bool GitsClickGridCard(object? screen, object? card)
    {
        if (screen == null || card == null) return false;
        try
        {
            MethodInfo? click = null;
            for (var t = screen.GetType(); t != null && click == null;
                 t = t.BaseType)
            {
                click = t.GetMethod("OnCardClicked", GitsGridFlags, null,
                                    new[] { card.GetType() }, null)
                        ?? t.GetMethod("OnCardClicked", GitsGridFlags);
            }
            if (click == null) return false;
            click.Invoke(screen, new[] { card });
            return true;
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] off-screen grid click failed: "
                        + $"{ex.Message}");
            return false;
        }
    }

    /// <summary>One cached protected-field read. The cache is keyed on the
    /// RUNTIME type because the screens are a family -- transform, upgrade,
    /// select, enchant -- and each declares the field on the same base.
    /// </summary>
    private static object? GitsFieldValue(object owner, string name,
                                          Dictionary<Type, FieldInfo?> cache)
    {
        var type = owner.GetType();
        if (!cache.TryGetValue(type, out var field))
        {
            field = null;
            for (var t = type; t != null && field == null; t = t.BaseType)
            {
                field = t.GetField(name, GitsGridFlags);
            }
            cache[type] = field;
        }
        return field?.GetValue(owner);
    }
}
