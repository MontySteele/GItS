using System.Linq;
using System.Threading.Tasks;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// The two Commander verbs that belong to no rule -- Rally's search and
/// Vanguard's grant -- kept out of <see cref="KokomiTide"/> because that file
/// is the RULES and these are two cards.
/// </summary>
public static class KokomiOverhaulKit
{
    /// <summary>
    /// The loc table the prompt lives in, and it is the base game's own. Same
    /// shape and the same reason as <see cref="RecallFromDiscard"/>'s:
    /// <c>&lt;ENTRY&gt;.selectionScreenPrompt</c> in the <c>cards</c> table is
    /// how the base game names a selection screen, and a <c>LocString</c> is a
    /// table plus a key with no raw-text constructor, so copy can only reach
    /// the screen as a row.
    /// </summary>
    private const string Table = "cards";

    /// <summary>Keyed on the VERB rather than on a card id -- one screen, one
    /// string, however many carriers eventually print it.</summary>
    public const string CompanionSearchPromptKey =
        "KLEEMOD-KOKOMI_COMPANION_SEARCH.selectionScreenPrompt";

    /// <summary>The prompt text. Merged into the table by
    /// <c>KleeMod.InjectLocStrings</c>, which is its only source.</summary>
    public const string CompanionSearchPromptText =
        "Choose a Companion card from your Draw Pile. Draw it.";

    /// <summary>The selection prompt. One member, so the copy lands in one
    /// place.</summary>
    public static LocString CompanionSearchPrompt =>
        new LocString(Table, CompanionSearchPromptKey);

    /// <summary>Which cards Rally can find. Read-only, and present so a pin and
    /// any future count surface read the claim rather than restating it.</summary>
    public static bool IsCompanion(CardModel card) => card is ICompanionCard;

    /// <summary>
    /// Rally: "Draw a Companion card from your draw pile."
    ///
    /// THE PLAYER CHOOSES, through the game's own pile-selection screen -- the
    /// same door <c>RecallFromExhaust</c> uses, filtered by predicate. The card
    /// says "a Companion", not "a random Companion", and this is the Commander
    /// loop's one search: a coin flip would make the card find the army rather
    /// than let her pick which part of it arrives.
    ///
    /// AN EMPTY POOL IS A NO-OP and not a screen. A selection over nothing is
    /// a click the player cannot answer.
    /// </summary>
    public static async Task DrawCompanionFromDraw(
        PlayerChoiceContext choiceContext, Player? owner, CardModel source)
    {
        if (owner == null) return;
        var pile = CardPile.Get(PileType.Draw, owner);
        if (pile == null) return;
        if (!pile.Cards.Any(IsCompanion)) return;

        var pick = (await CardSelectCmd.FromCombatPile(
            choiceContext, pile, owner,
            new CardSelectorPrefs(CompanionSearchPrompt, 1),
            IsCompanion)).FirstOrDefault();
        if (pick == null) return;

        // "DRAW IT" IS A MOVE TO HAND, which is what the base game's own
        // search cards do: the card leaves the draw pile and arrives in hand,
        // and nothing else about the turn's draw changes.
        await CardPileCmd.Add(pick, PileType.Hand, CardPilePosition.Top);
    }

    /// <summary>
    /// Vanguard: "The next Companion you play this turn costs 0."
    ///
    /// ONE STACK, ALWAYS. The grant is a switch, not a counter -- a second
    /// Vanguard in one turn cannot make the next Companion cost less than 0 --
    /// so this applies at 1 whether or not the power is already there, and
    /// <see cref="NextCompanionFreePower"/> removes itself on the play that
    /// spends it.
    /// </summary>
    public static async Task NextCompanionFree(
        PlayerChoiceContext choiceContext, Creature? kokomi, CardModel? cardSource)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (kokomi!.Powers.OfType<NextCompanionFreePower>().Any()) return;
        await PowerCmd.Apply<NextCompanionFreePower>(
            choiceContext, kokomi, 1, applier: kokomi, cardSource: cardSource);
    }
}
