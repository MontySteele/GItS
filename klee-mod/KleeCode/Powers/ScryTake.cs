using MegaCrit.Sts2.Core.Localization;

namespace KleeMod.Powers;

/// <summary>
/// The screen the `scry_take` op renders (`EB-679`, Read the Field, pool pass
/// four): "look at the top N cards of your draw pile; put one into your hand
/// and the rest on the bottom".
///
/// A SECOND CLASS AND NOT A SECOND MEMBER ON <see cref="ScryBottom"/>, on that
/// file's own terms: a screen is keyed on the VERB, and these are two verbs.
/// Burying the card you want least and taking the card you want most ask the
/// player different questions, and r26's lane answered only one of them --
/// which is the whole reason this op exists.
///
/// A CLASS FOR ONE STRING, for <see cref="ScryBottom"/>'s reason: a
/// <c>LocString</c> is a table plus a key with no raw-text constructor, so
/// ruled copy can only reach a selection screen as a row, and one screen gets
/// one string however many carriers eventually print it.
/// <c>KleeMod.InjectLocStrings</c> merges the row into the same <c>cards</c>
/// table the base game's own prompts live in, so a code-only rebuild never
/// renders the raw key.
///
/// THE MOVE ITSELF IS EMITTED, not written here: <c>gen_klee_cards</c>'s
/// `scry_take` arm builds the <c>CardSelectCmd.FromSimpleGrid</c> over the top
/// N, the <c>CardPileCmd.Add(..., PileType.Hand)</c> that lands the pick and
/// the loop that bottoms everything else the player was shown. The sim's twin
/// has no screen and takes the lowest-cost card of the N -- stated at
/// <c>tier0.engine.effects._op_scry_take</c> as the stand-in for player choice
/// it is.
/// </summary>
public static class ScryTake
{
    /// <summary>The loc table the prompt lives in, and it is the base game's
    /// own -- every <c>selectionScreenPrompt</c> row is a <c>cards</c>
    /// row.</summary>
    private const string Table = "cards";

    /// <summary>Key for <see cref="Prompt"/>, keyed on the VERB.</summary>
    public const string PromptKey =
        "KLEEMOD-SCRY_TAKE.selectionScreenPrompt";

    /// <summary>The prompt text. Merged into the `cards` table by
    /// <c>KleeMod.InjectLocStrings</c>, which is its only source. It names
    /// both halves, because the second one is what the player is giving up:
    /// the cards not chosen do not stay where they were.</summary>
    public const string PromptText =
        "Choose a card. The rest go to the bottom of your Draw Pile.";

    /// <summary>The selection prompt. One member, so the copy lands in one
    /// place.</summary>
    public static LocString Prompt => new LocString(Table, PromptKey);
}
