using MegaCrit.Sts2.Core.Localization;

namespace KleeMod.Powers;

/// <summary>
/// The screen the `scry_bottom` op renders (`EB-655`, Read the Field): "look
/// at the top N cards of your draw pile and put one of them on the bottom".
///
/// A CLASS FOR ONE STRING, on exactly <see cref="RecallFromDiscard"/>'s terms
/// and for its reason: a <c>LocString</c> is a table plus a key with no
/// raw-text constructor, so ruled copy can only reach a selection screen as a
/// row, and one screen gets one string however many carriers eventually print
/// it. <c>KleeMod.InjectLocStrings</c> merges the row into the same
/// <c>cards</c> table the base game's own prompts live in, so a code-only
/// rebuild never renders the raw key.
///
/// NOT KEYED ON A CARD ID. Read the Field is the first carrier and will not be
/// the last; the verb owns the sentence, the way
/// <c>CardSelectorPrefs.DiscardSelectionPrompt</c> owns the sibling verb's.
///
/// THE MOVE ITSELF IS EMITTED, not written here: <c>gen_klee_cards</c>'s
/// `scry_bottom` arm builds the <c>CardSelectCmd.FromSimpleGrid</c> over the
/// top N and the <c>CardPileCmd.Add(..., PileType.Draw,
/// CardPilePosition.Bottom)</c> that lands the pick, so the op has one
/// implementation and this file has one sentence. The sim's twin has no
/// screen and bottoms the highest-cost card of the N -- stated at
/// <c>tier0.engine.effects._op_scry_bottom</c> as the stand-in for player
/// choice it is.
/// </summary>
public static class ScryBottom
{
    /// <summary>The loc table the prompt lives in, and it is the base game's
    /// own -- every <c>selectionScreenPrompt</c> row is a <c>cards</c>
    /// row.</summary>
    private const string Table = "cards";

    /// <summary>Key for <see cref="Prompt"/>, keyed on the VERB.</summary>
    public const string PromptKey =
        "KLEEMOD-SCRY_BOTTOM.selectionScreenPrompt";

    /// <summary>The prompt text. Merged into the `cards` table by
    /// <c>KleeMod.InjectLocStrings</c>, which is its only source. One
    /// sentence, because the screen does one thing and the cards on it are
    /// already the ones the player was shown.</summary>
    public const string PromptText =
        "Choose a card. Put it on the bottom of your Draw Pile.";

    /// <summary>The selection prompt. One member, so the copy lands in one
    /// place.</summary>
    public static LocString Prompt => new LocString(Table, PromptKey);
}
