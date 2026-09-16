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
// v0.111.0. `_highlightedCards` is also exactly what the screen PAINTS --
// `AssignCardsToRow` shows or hides each holder's highlight from this list --
// so the flag on the wire and the glow on the card cannot disagree.
//
// It was read here as the ONE list that answers the question for every grid
// screen there is. The live look below found that reading one screen too
// broad; the list is still the right first source and is no longer the only
// one.
//
// REFLECTION, NOT A REFERENCE, because the field is private. A private field
// is a pin-fragile read, so every failure is swallowed into NULL rather than
// FALSE: null means "could not ask", false means "asked, and this card is not
// selected", and `BuildCardSelectState` puts that difference on the wire as
// `selection_known` so a page can never print the first while meaning the
// second. This is the same discipline as `GitsResources` and
// `GitsSparkPrice`; a state read must never throw and must never guess.
//
// `EB-794` (proofs-9 lane 1, defect 4): AND ONE GRID ANSWERS SOMEWHERE ELSE.
//
// THE FIND, live. On the Smith's UPGRADE grid `select_card index=38` came back
// with that row `selected: true` and `can_confirm: true`, which is `EB-263`'s
// acceptance. On the shop's REMOVAL grid `select_card index=36` answered
// *"Toggling card selection: Kurage's Oath"*, `can_confirm` flipped to true,
// the confirm then removed exactly that card -- and NO row in
// `card_select.cards` carried `selected: true`, and no preview came through
// either. The pick was armed, correct, and invisible on the wire.
//
// SO THE "ONE LIST FOR EVERY SCREEN" CLAIM ABOVE IS TRUE OF FOUR SCREENS AND
// NOT OF FIVE. `_highlightedCards` is the grid's own paint list and the four
// screens that glow a row write through it; the removal screen
// (`NDeckCardSelectScreen`) arms its pick on the SCREEN instead -- it is the
// one whose confirm lives in `%PreviewContainer` / `%PreviewConfirm`, which
// `McpMod.Actions.cs` has had to special-case since before this row -- so the
// grid was asked a question the screen was holding the answer to.
//
// THE SECOND SOURCE IS THE SCREEN'S OWN SELECTION FIELD, matched BY NAME
// (`_selectedCard`, `_selectedCards`, and anything else whose field name says
// "select" or "chosen"), and unioned with the grid's list. Named rather than
// typed, because a screen holds several `CardModel`s that are not a pick --
// a hovered row, a preview clone -- and a type-only walk would report the one
// under the cursor as armed, which is a worse answer than the silence this
// replaces. A single `CardModel` field and an `IEnumerable` of them are both
// taken, because the screens spell it both ways.
//
// STILL NULL-ON-FAILURE, and the union does not change what `selection_known`
// means: where the GRID could not be asked the answer is still "could not
// ask", because an empty screen field is not evidence that nothing is picked.
// Cached per screen type, `GitsCardGrid.cs`'s bargain.
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

    /// <summary>`EB-794`: the screen's own selection fields, per screen type.
    /// An empty array is cached too -- four of the five screens have none and
    /// a state read should not pay for a field walk on every poll.</summary>
    private static readonly Dictionary<Type, FieldInfo[]>
        _gitsScreenSelectionFields = new();

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
    ///
    /// `EB-794`: the grid's paint list UNIONED with the screen's own selection
    /// field, because the removal grid arms its pick on the screen and left
    /// every row unmarked on the wire.
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
            GitsAddScreenSelection(screen, selected);
            return selected;
        }
        catch (Exception)
        {
            return null;
        }
    }

    /// <summary>
    /// Add whatever <paramref name="screen"/> is holding as its own pick
    /// (`EB-794`). Adds nothing it cannot read; never throws.
    /// </summary>
    private static void GitsAddScreenSelection(
        Node screen, HashSet<CardModel> selected)
    {
        try
        {
            foreach (var field in GitsScreenSelectionFields(screen.GetType()))
            {
                var value = field.GetValue(screen);
                if (value is CardModel card)
                {
                    selected.Add(card);
                }
                else if (value is IEnumerable many and not string)
                {
                    foreach (var entry in many)
                    {
                        if (entry is CardModel one) selected.Add(one);
                    }
                }
            }
        }
        catch (Exception)
        {
            // The grid's own answer stands; a screen field that cannot be read
            // adds nothing rather than taking the whole read down.
        }
    }

    /// <summary>
    /// The fields on a selection screen whose NAME says they hold a pick,
    /// walked once per screen type and cached (`EB-794`).
    ///
    /// BY NAME AND NOT BY TYPE: a screen holds `CardModel`s that are not a
    /// pick -- the row under the cursor, a preview clone -- and reporting one
    /// of those as armed is a worse answer than the silence this replaces.
    /// </summary>
    private static FieldInfo[] GitsScreenSelectionFields(Type type)
    {
        if (_gitsScreenSelectionFields.TryGetValue(type, out var cached))
        {
            return cached;
        }
        var found = new List<FieldInfo>();
        try
        {
            for (var t = type; t != null; t = t.BaseType)
            {
                foreach (var field in t.GetFields(
                             BindingFlags.Instance | BindingFlags.NonPublic
                             | BindingFlags.Public | BindingFlags.DeclaredOnly))
                {
                    if (GitsNamesASelection(field.Name)) found.Add(field);
                }
            }
        }
        catch (Exception ex)
        {
            GD.PrintErr("[STS2 MCP][GItS] screen selection probe failed: "
                        + ex.Message);
            found.Clear();
        }
        var fields = found.ToArray();
        _gitsScreenSelectionFields[type] = fields;
        return fields;
    }

    /// <summary>Does this field name say "this is the pick"?</summary>
    private static bool GitsNamesASelection(string name) =>
        name.IndexOf("select", StringComparison.OrdinalIgnoreCase) >= 0
        || name.IndexOf("chosen", StringComparison.OrdinalIgnoreCase) >= 0;
}
