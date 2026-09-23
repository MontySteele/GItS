using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

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

    /// <summary>
    /// `EB-686`. THE PICK WITH NOTHING TO PICK BETWEEN.
    ///
    /// THE FIND (Kokomi r28 lane 1, fight 3 turn 3). Read the Field with one
    /// card left in the draw pile "showed no selection, put that card in hand,
    /// charged the energy and printed nothing; the seat spent a turn unsure it
    /// had whiffed." A grid of one holds no decision, so the game opens no
    /// screen -- which is right, and silent.
    ///
    /// THE RULE DOES NOT MOVE, only what is said: the one card was always
    /// taken and still is. What is added is the LINE, and it names both halves
    /// -- what was taken, and why there was no screen -- because "it took
    /// something" and "it did nothing" are the same silence to a player who
    /// did not count the pile.
    ///
    /// AN EMPTY PILE IS STILL NOTHING and says so. The emitted arm only
    /// reaches here with at least one card, but a branch that indexed off the
    /// end the day that changed would be a crash in a play, not a red test.
    ///
    /// THE MOVE ITSELF IS STILL EMITTED. This owns the CHOICE alone, so where
    /// the taken card lands and where the rest are bottomed stays in one
    /// place, exactly as it was.
    ///
    /// <paramref name="setOffOnly"/> IS R276's (Where Did I Put It?) and it
    /// narrows what may be TAKEN, never what was seen: the grid holds only the
    /// Set off cards among <paramref name="top"/>, one of them is taken without
    /// a screen and said out loud, and none means nothing is taken -- the
    /// emitted arm then bottoms every card it looked at. Prototype builds only,
    /// because the Set off mark (<c>ISetOffCard</c>) is the Klee arm's.
    /// </summary>
    public static async Task<List<CardModel>> Choose(
        PlayerChoiceContext choiceContext, List<CardModel> top, Player owner,
        bool setOffOnly = false)
    {
        var offer = top;
#if PROTOTYPE_CARDS
        if (setOffOnly)
        {
            offer = top.Where(card => card is ISetOffCard).ToList();
            if (offer.Count == 0)
            {
                Say(owner, NoSetOffLine);
                return new List<CardModel>();
            }
            if (offer.Count == 1 && top.Count > 1)
            {
                Say(owner, OneSetOffLine(Named(offer[0])));
                return new List<CardModel> { offer[0] };
            }
        }
#endif
        if (offer.Count == 0) return new List<CardModel>();
        if (offer.Count == 1)
        {
            Announce(owner, offer[0]);
            return new List<CardModel> { offer[0] };
        }
        return (await CardSelectCmd.FromSimpleGrid(
            choiceContext, offer, owner,
            new CardSelectorPrefs(Prompt, 1))).ToList();
    }

    /// <summary>R276: the filtered look found no Set off card, so everything
    /// it saw goes to the bottom. Said, for `EB-686`'s reason: a look that
    /// takes nothing and one that took something are the same silence.</summary>
    public const string NoSetOffLine =
        "No Set off card on top: all of them go to the bottom.";

    /// <summary>R276: exactly one Set off card among several seen, taken with
    /// no screen.</summary>
    public static string OneSetOffLine(string title) =>
        $"The only Set off card on top: {title} taken.";

    /// <summary>The line the auto-take says, built in ONE place so the pin and
    /// the screen read the same words. <c>KurageBeat.Line</c>'s bargain and
    /// its reason: a <c>LocString</c> is a table plus a key with no raw-text
    /// constructor, and this sentence is built per play out of a card
    /// title.</summary>
    public static string AutoTakeLine(string title) =>
        $"Only one card left to look at: {title} taken.";

    /// <summary>Over the player's head, and silent headless -- by the engine's
    /// own guards rather than ours (<c>KurageBeat.Say</c>).</summary>
    private static void Announce(Player owner, CardModel card) =>
        Say(owner, AutoTakeLine(Named(card)));

    /// <summary>One line over the player's head; silent headless and in a
    /// release build.</summary>
    private static void Say(Player owner, string line)
    {
#if PROTOTYPE_CARDS
        Vfx.KurageBeat.Say(owner.Creature, line);
#endif
    }

    /// <summary>A printed title, or `""`, and never a throw --
    /// <c>ReactionLog.Named</c>'s bargain: a display read is a read of live
    /// game objects, and a receipt must never be the thing that ends a
    /// play.</summary>
    private static string Named(CardModel card)
    {
        try
        {
            return card.Title.ToString() ?? string.Empty;
        }
        catch (System.Exception)
        {
            return string.Empty;
        }
    }
}
