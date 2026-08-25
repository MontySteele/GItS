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
    /// The loc table the prompt lives in, and it is the base game's own. Hand
    /// Trick renders this screen from <c>cards/HAND_TRICK.selectionScreenPrompt</c>
    /// -- "Choose a card to add [gold]Sly[/gold] to." -- so a mod row in the
    /// same table under the same suffix is the shipped shape rather than a new
    /// mechanism. <c>KleeMod.InjectLocStrings</c> merges it at boot, which is
    /// what keeps a code-only rebuild from rendering the raw key.
    /// </summary>
    private const string Table = "cards";

    /// <summary>
    /// Key for <see cref="Prompt"/>. Keyed on the VERB, not on a card id: two
    /// cards print this screen and the ruled copy is ONE string. The base game
    /// keys per card because each of its prompts is written for one card.
    /// </summary>
    public const string PromptKey = "KLEEMOD-SLY_GRANT.selectionScreenPrompt";

    /// <summary>
    /// RULED COPY ([USER], 2026-08-25) -- the OWED note this replaces is
    /// DISCHARGED. It names the filter the screen is actually applying
    /// (Skills, in hand) and the duration, because <see cref="Eligible"/>
    /// enforces both and a prompt that said only "a card" would describe a
    /// pool the player cannot pick from.
    ///
    /// The gilding is not decoration and it is not invented: every base-game
    /// prompt that grants a keyword gilds it -- HAND_TRICK's own row wraps
    /// [gold]Sly[/gold], SCULPTING_STRIKE wraps [gold]Ethereal[/gold], SNAP
    /// wraps [gold]Retain[/gold] -- so this screen demonstrably renders BBCode
    /// and demonstrably gilds this exact keyword (SlayTheSpire2.pck, v0.107.1,
    /// English rows read 2026-08-25). Reaching the live mod at the next
    /// deploy; the rendered look is still an eyes-on item.
    /// </summary>
    public const string PromptText =
        "Choose a Skill in your hand. It gains [gold]Sly[/gold] this turn.";

    /// <summary>The selection prompt. One member, so the ruled copy lives in
    /// one place for both carriers.</summary>
    public static LocString Prompt => new LocString(Table, PromptKey);

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
