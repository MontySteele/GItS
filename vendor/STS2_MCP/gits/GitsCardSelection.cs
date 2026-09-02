// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// `EB-263`: WHICH CARD DID I JUST PICK?
//
// THE GAP, EXACTLY
//
// `BuildCardSelectState` serialises every card in the grid through
// `BuildCardInfo`, which has no selection field, and there is nothing else on
// the wire that moves when a pick lands except `can_confirm`. So a blind
// tester who chose a card on the upgrade, transform, select or enchant screen
// got the same page back, and the render had to say so in words:
//
//     "This screen's data feed carries no per-card selection state, so
//      nothing in the list above can be marked as the one you picked."
//
// (`understudy/blindplay.py`, `SELECTION_NOTE`.) This closes that.
//
// WHERE THE SELECTION ACTUALLY LIVES, AND WHY IT IS ONE PLACE
//
// Each screen keeps its own set -- `NDeckEnchantSelectScreen._selectedCards`,
// and a differently-named field on each of the other four -- so reading the
// screen would mean five contracts that drift apart. But every one of the
// five calls the SAME pair on the grid it shares:
//
//     NCardGrid.HighlightCard(CardModel)      -> _highlightedCards.Add(card)
//     NCardGrid.UnhighlightCard(CardModel)    -> _highlightedCards.Remove(card)
//
// verified in the decompiled `OnCardClicked` of `NDeckUpgradeSelectScreen`,
// `NDeckTransformSelectScreen`, `NDeckCardSelectScreen`,
// `NSimpleCardSelectScreen` and `NDeckEnchantSelectScreen` against game
// v0.111.0. `_highlightedCards` is therefore the one list that answers the
// question for every grid screen there is, including any the game adds next,
// and it is also exactly what the screen PAINTS -- `AssignCardsToRow` shows or
// hides each holder's highlight from this list -- so the flag on the wire and
// the glow on the card cannot disagree.
//
// REFLECTION, NOT A REFERENCE, because the field is private. A private field
// is a pin-fragile read, so every failure is swallowed into NULL rather than
// FALSE: null means "could not ask", false means "asked, and this card is not
// selected", and `BuildCardSelectState` puts that difference on the wire as
// `selection_known` so a page can never print the first while meaning the
// second. This is the same discipline as `GitsResources` and
// `GitsSparkPrice`; a state read must never throw and must never guess.
//
// READ-ONLY. Nothing here highlights, clears or presses anything.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using Godot;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Cards;

namespace STS2_MCP;

public static partial class McpMod
{
    private const string GitsHighlightedField = "_highlightedCards";

    private static bool _gitsSelectionProbed;
    private static FieldInfo? _gitsHighlightedCards;

    /// <summary>
    /// Locate `NCardGrid._highlightedCards` once. A null result is cached too:
    /// the field does not appear mid-session, and a state read should not pay
    /// for a reflection walk on every poll of every selection screen.
    /// </summary>
    private static FieldInfo? GitsHighlightedCardsField()
    {
        if (_gitsSelectionProbed) return _gitsHighlightedCards;
        _gitsSelectionProbed = true;
        try
        {
            _gitsHighlightedCards = typeof(NCardGrid).GetField(
                GitsHighlightedField,
                BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
            if (_gitsHighlightedCards == null)
            {
                GD.Print("[STS2 MCP][GItS] no NCardGrid." + GitsHighlightedField
                         + "; card selection will report as unknown");
            }
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] selection probe failed: {ex.Message}");
            _gitsHighlightedCards = null;
        }
        return _gitsHighlightedCards;
    }

    /// <summary>
    /// The cards currently picked on <paramref name="screen"/>, or NULL when
    /// the grid could not be asked. Never throws.
    ///
    /// A `HashSet` on reference identity, which is what the game's own
    /// membership test uses: the grid holds the very `CardModel` instances the
    /// holders hold, so two copies of one card are told apart correctly and a
    /// clone of a selected card is not mistaken for it.
    /// </summary>
    internal static HashSet<CardModel>? GitsSelectedCards(Node? screen)
    {
        if (screen == null) return null;
        var field = GitsHighlightedCardsField();
        if (field == null) return null;
        try
        {
            var grid = FindFirst<NCardGrid>(screen);
            if (grid == null) return null;
            if (field.GetValue(grid) is not IEnumerable highlighted) return null;
            var selected = new HashSet<CardModel>();
            foreach (var entry in highlighted)
            {
                if (entry is CardModel card) selected.Add(card);
            }
            return selected;
        }
        catch (Exception)
        {
            return null;
        }
    }
}
