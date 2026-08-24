using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// The turn-scoped Sly grant: the C# leg of tier0's `grant_sly_this_turn`
/// (EB-122, for EB-69's `the_gunbai_turns` and `raise_the_sashimono`).
///
/// NOTHING HERE IS INVENTED. Hand Trick is the base game's own carrier of this
/// verb and every part of the shape is transcribed from it (sts2.dll v0.107.1,
/// MegaCrit.Sts2.Core.Models.Cards.HandTrick.OnPlay): a one-card hand selection
/// filtered to Skills that are not already Sly this turn, then
/// <c>CardCmd.ApplySingleTurnSly</c>, which sets the flag the game itself
/// clears at end of turn. The mod owns no timer and no power of its own --
/// inventing one is what would have made this a different mechanic wearing the
/// same name.
///
/// One C# home for the whole verb, the <see cref="RecallFromExhaust"/>
/// discipline: two cards print it, and a per-card re-spelling is how two
/// copies of one rule drift.
///
/// SIM TWIN: tier0 effects._op_grant_sly_this_turn. It picks through
/// `_best_card` rather than a screen, which is the sim's standing stand-in for
/// player choice (the same relationship `_worst_card` has with the chosen
/// discard's selector), so the SELECTOR is the parity match, not a divergence.
///
/// ONE DECLARED, CURRENTLY UNREACHABLE DIVERGENCE, recorded rather than
/// papered over. The sim's target filter asks the NARROW question -- "did a
/// grant already land on this card this turn" -- and deliberately leaves a
/// PRINTED-Sly Skill a legal target (state.sly_granted_this_turn's docstring
/// says so and says why). The game's own filter asks the wide one,
/// <c>!IsSlyThisTurn</c>, which a printed keyword also answers true; the
/// narrow half of it, <c>HasSingleTurnSly</c>, is PRIVATE on CardModel, so the
/// wide question is the only one this side of the wall can ask without
/// reflection. The two coincide on every card that can reach this screen,
/// because no committed Kokomi row prints the base-game Sly keyword -- and
/// that premise is a test, not an assumption
/// (tier0/tests/test_eb122_csharp_grammar.py), so the day a row prints it the
/// suite asks the question again instead of the pools silently disagreeing.
/// </summary>
public static class SlyGrant
{
    /// <summary>
    /// The selection prompt. OWED, exactly as <see cref="RecallFromExhaust"/>'s
    /// is: Hand Trick renders this screen from its own per-card
    /// <c>cards/&lt;id&gt;.selectionScreenPrompt</c> row, no generated card has
    /// ever carried one, and authoring the string is a player-facing TEXT call
    /// rather than an engineering one. It stands at the closest shipped string
    /// meanwhile. One member, so the ruled copy lands in one place.
    /// </summary>
    public static LocString Prompt => CardSelectorPrefs.DiscardSelectionPrompt;

    /// <summary>
    /// Eligible targets. Skills only (the game's filter and the sheet's only
    /// `card_type`), never already Sly this turn -- so a second grant in one
    /// turn picks a different card instead of wasting itself, which is the
    /// whole reason the game's filter carries that clause -- and never a kit
    /// card: the v1.9 invariant that the Burst is never fodder, which the sim
    /// spells as `not c.kit_card` on this same pool.
    /// </summary>
    public static bool Eligible(CardModel card) =>
        card.Type == CardType.Skill
            && !card.IsSlyThisTurn
            && KitGrant.NotKitCard(card);

    /// <summary>
    /// Give one chosen Skill in hand Sly for this turn. No-op when nothing in
    /// hand is eligible -- the sim's empty-pool return, and the selector's own
    /// behaviour, so neither engine asks for a choice it cannot offer.
    /// </summary>
    public static async Task Grant(
        PlayerChoiceContext choiceContext, Player? owner, CardModel source)
    {
        if (owner == null) return;

        var pick = (await CardSelectCmd.FromHand(
            choiceContext, owner,
            new CardSelectorPrefs(Prompt, 1),
            Eligible, source)).FirstOrDefault();

        if (pick != null)
        {
            CardCmd.ApplySingleTurnSly(pick);
        }
    }
}
