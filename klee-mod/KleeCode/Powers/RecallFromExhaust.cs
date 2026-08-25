using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// Marker for a card that retrieves from the Exhaust pile (EB-118 §6.4
/// constraint 3).
///
/// The sim reads the same fact off the printed effect tree
/// (tier0 effects.retrieves_from_exhaust); a CardModel has no effect tree at
/// runtime, so the generator stamps this interface from the SHEET row. One
/// source, two spellings -- not two judgements.
/// </summary>
public interface IExhaustRetriever
{
}

/// <summary>
/// Exhaust-pile retrieval: the C# leg of EB-118.
///
/// It is the SAME verb as tier0's recall_to_draw, reading a different pile --
/// not a parallel op family. The retrieval card and a draw slot are the
/// immediate price; the card that comes back is on LOAN for one more use,
/// gains Exhaust, and rotates out again on that use -- paying Charge again at
/// the ordinary funnel (KokomiResources' exhaust accrual; a retrieved
/// PERSONAL card is not junk, so C11 pays it). Taking it out of the pile
/// weakens only pile READERS while it is gone; banked Charge does not fall,
/// because Charge is never spent (LAW).
///
/// All six constraints are enforced HERE or by the generator, never by card
/// authors: 1 and 2 (Uncommon-or-Rare, self-Exhaust) are card shape and are
/// checked at generation time (gen_klee_cards.blocked_reason) and at sim load
/// (loader._validate_recall_shape); 3-6 are the runtime pool filter below.
/// </summary>
public static class RecallFromExhaust
{
    /// <summary>Source pile. Pinned as a member so the parity tests can read
    /// the choice without a live combat.</summary>
    public const PileType Source = PileType.Exhaust;

    /// <summary>Destination pile -- the DRAW pile, never the hand
    /// (constraint 4).</summary>
    public const PileType Destination = PileType.Draw;

    /// <summary>Top of the draw pile, the sim's `insert(0, ...)`
    /// (constraint 4).</summary>
    public const CardPilePosition Placement = CardPilePosition.Top;

    /// <summary>The keyword the returned card gains for the rest of combat
    /// (constraint 5). Instance-local: a twin of the same card elsewhere in
    /// the deck is untouched, matching the sim's per-instance flag.</summary>
    public const CardKeyword Loan = CardKeyword.Exhaust;

    /// <summary>
    /// The loc table the prompt lives in -- the base game's own, under its own
    /// <c>&lt;ENTRY&gt;.selectionScreenPrompt</c> suffix.
    /// <c>KleeMod.InjectLocStrings</c> merges the mod's row at boot.
    /// </summary>
    private const string Table = "cards";

    /// <summary>Key for <see cref="Prompt"/>, keyed on the VERB. No card
    /// prints this screen yet -- the retrieval cards are still ahead -- and
    /// the copy being ruled now is what keeps the first one from inventing
    /// its own.</summary>
    public const string PromptKey =
        "KLEEMOD-RECALL_FROM_EXHAUST.selectionScreenPrompt";

    /// <summary>
    /// RULED COPY ([USER], 2026-08-25) -- the OWED note this replaces is
    /// DISCHARGED. It says all three things the exhaust branch does that its
    /// discard twin does not: which pile is being read, where the card lands,
    /// and the LOAN. Constraint 5's Exhaust is the price of the retrieval and
    /// the player is told before choosing, not after.
    ///
    /// [gold]Exhaust[/gold] is gilded because the base game gilds a keyword it
    /// grants on this screen and gilds this one by name -- PURITY's row reads
    /// "Choose up to {Cards:diff()} cards to [gold]Exhaust[/gold]."
    /// (SlayTheSpire2.pck, v0.107.1, English rows read 2026-08-25), which also
    /// settles that the selection screen renders BBCode at all. Reaching the
    /// live mod at the next deploy; the rendered look is an eyes-on item.
    /// </summary>
    public const string PromptText =
        "Choose a card to return from your Exhaust Pile. It goes on top of "
        + "your Draw Pile and gains [gold]Exhaust[/gold].";

    /// <summary>The selection prompt. One member, so the first shipped
    /// retrieval card reads the ruled copy instead of writing its own.</summary>
    public static LocString Prompt => new LocString(Table, PromptKey);

    /// <summary>
    /// Eligible targets (EB-118 §6.4 constraints 3 and 6). Sim twin:
    /// effects.recall_exhaust_pool.
    ///
    /// Kit cards are never fodder and never loot (the v1.9 invariant every
    /// other pile pool rides). A retriever is ineligible -- that exclusion is
    /// what stops the pile closing into a cycle, and it covers the retrieval
    /// card ITSELF, which by then has Exhausted into this very pile.
    /// Status and Curse are out (KokomiResources.IsJunk, the C11 predicate);
    /// ordinary personal and Companion cards stay in.
    /// </summary>
    public static bool Recallable(CardModel card) =>
        KitGrant.NotKitCard(card)
            && !KokomiResources.IsJunk(card)
            && card is not IExhaustRetriever;

    /// <summary>
    /// Move up to <paramref name="amount"/> chosen cards from the Exhaust
    /// pile to the TOP of the draw pile, each gaining Exhaust. No-op when
    /// nothing in the pile is eligible (the sim's empty-pool return).
    /// </summary>
    public static async Task Recall(
        PlayerChoiceContext choiceContext, Player? owner, CardModel source,
        int amount)
    {
        if (owner == null || amount <= 0) return;
        var pile = CardPile.Get(Source, owner);
        if (pile == null) return;

        // `source` is excluded by type through Recallable -- a retrieval card
        // is an IExhaustRetriever. The reference is kept in the signature so
        // the selector has a source model and so the exclusion is legible at
        // the call site rather than only in the predicate.
        var eligible = pile.Cards.Where(Recallable).ToList();
        if (eligible.Count == 0) return;

        var picks = (await CardSelectCmd.FromCombatPile(
            choiceContext, pile, owner,
            new CardSelectorPrefs(Prompt, System.Math.Min(amount, eligible.Count)),
            Recallable)).ToList();

        foreach (var pick in picks)
        {
            pick.AddKeyword(Loan);
            await CardPileCmd.Add(pick, Destination, Placement);
        }
    }

    /// <summary>Read-only view of the eligible pool, for the parity tests and
    /// for any future surface that wants to show the count.</summary>
    public static IReadOnlyList<CardModel> Eligible(Player? owner)
    {
        var pile = owner == null ? null : CardPile.Get(Source, owner);
        return pile == null
            ? new List<CardModel>()
            : pile.Cards.Where(Recallable).ToList();
    }
}
