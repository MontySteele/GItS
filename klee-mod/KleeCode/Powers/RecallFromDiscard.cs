using System;
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
/// Discard-pile retrieval: the C# leg of `recall_to_draw` reading its DEFAULT
/// source (EB-122, for EB-69's `what_the_tokoyo_returns`).
///
/// It is the SAME verb as <see cref="RecallFromExhaust"/> reading a different
/// pile, and the shape is the base game's own: Headbutt selects one card from
/// <c>PileType.Discard</c> and calls <c>CardPileCmd.Add(card, PileType.Draw,
/// CardPilePosition.Top)</c> (sts2.dll v0.107.1,
/// MegaCrit.Sts2.Core.Models.Cards.Headbutt.OnPlay). Nothing here is invented.
///
/// THE POOL IS UNFILTERED, AND THAT IS THE CONTRACT -- NOT AN OMISSION.
/// tier0's discard branch is the raw pile: no self clause, no kit filter, no
/// junk filter, so a card thrown away by an effect can have its own Sly rider
/// recall ITSELF. [USER] ruled that behaviour DELIBERATE (EB-69 / D3, R198),
/// and `tier0/tests/test_eb69_tokoyo_returns_selfrecall.py` is its pin and
/// this leg's SPEC. The asymmetry with the exhaust branch beside it -- which
/// excludes self, kit cards, junk and other retrievers because EB-118 §6.4
/// required it -- is now intentional on both sides and in both engines.
/// Tidying the two into one filtered implementation breaks a shipped card on
/// purpose and must say so.
///
/// Three things this branch deliberately does NOT do, each of which the
/// exhaust branch does:
///   * it grants no keyword. The exhaust loan costs the returned card an
///     Exhaust; a discard-pile card was always coming back on a reshuffle, so
///     there is no loan to price. tier0 sets `pick.exhaust = True` inside
///     `if from_exhaust:` and nowhere else.
///   * it stamps no <see cref="IExhaustRetriever"/> on its carriers. That
///     marker is the cycle exclusion for the EXHAUST pool, and a card that
///     reads the discard pile is not part of that cycle -- the sim reads the
///     same distinction off `from == "exhaust"`.
///   * it enforces no §6.4 card shape (Uncommon-or-Rare, self-Exhaust). Those
///     constraints were written for the exhaust side; `what_the_tokoyo_returns`
///     is an Uncommon that does not Exhaust, and it is legal.
/// </summary>
public static class RecallFromDiscard
{
    /// <summary>Source pile. A member so the parity tests can read the choice
    /// without a live combat.</summary>
    public const PileType Source = PileType.Discard;

    /// <summary>Destination pile -- the DRAW pile, never the hand. Shared with
    /// the exhaust branch: tier0 has one destination for both.</summary>
    public const PileType Destination = PileType.Draw;

    /// <summary>Top of the draw pile, the sim's `insert(0, ...)`.</summary>
    public const CardPilePosition Placement = CardPilePosition.Top;

    /// <summary>
    /// The selection prompt. OWED, the same way <see cref="RecallFromExhaust"/>'s
    /// is: the base game ships no "retrieve" prompt -- Headbutt renders this
    /// screen from its own per-card <c>cards/&lt;id&gt;.selectionScreenPrompt</c>
    /// row -- and authoring that string is a player-facing TEXT call, not an
    /// engineering one. It stands at the prompt naming the PILE the screen is
    /// showing. One member, so the ruled copy lands in one place.
    /// </summary>
    public static LocString Prompt => CardSelectorPrefs.DiscardSelectionPrompt;

    /// <summary>
    /// Move up to <paramref name="amount"/> chosen cards from the discard pile
    /// to the TOP of the draw pile. No-op on an empty pile (the sim's empty-pool
    /// return).
    ///
    /// ONE SELECTION FOR THE WHOLE BATCH, matching `_op_discard`'s chosen
    /// branch rather than looping the screen: the sim's loop re-reads a pile it
    /// has already removed each pick from, so its picks are distinct, and a
    /// single N-card selection from the same pile has exactly that membership.
    /// The picks are placed in order, so the LAST one chosen ends up on top --
    /// which is where the sim's repeated `insert(0, ...)` leaves it too.
    ///
    /// `source` is passed for attribution only and is NOT excluded. On the
    /// played face it is resolving and so is not in the pile at all; on the Sly
    /// face it IS in the pile -- <c>CardCmd.DiscardAndDraw</c> adds the victim
    /// to the discard pile BEFORE firing <c>Hook.AfterCardDiscarded</c>
    /// (verified, sts2.dll v0.107.1) -- and the self-recall it can then make is
    /// the ruled behaviour, not an escape.
    /// </summary>
    public static async Task Recall(
        PlayerChoiceContext choiceContext, Player? owner, CardModel source,
        int amount)
    {
        if (owner == null || amount <= 0) return;
        var pile = CardPile.Get(Source, owner);
        if (pile == null || pile.Cards.Count == 0) return;

        var picks = (await CardSelectCmd.FromCombatPile(
            choiceContext, pile, owner,
            new CardSelectorPrefs(
                Prompt, Math.Min(amount, pile.Cards.Count)))).ToList();

        foreach (var pick in picks)
        {
            await CardPileCmd.Add(pick, Destination, Placement);
        }
    }

    /// <summary>Read-only view of the eligible pool -- the whole pile, which is
    /// the point. Present so a test and any future count surface read the
    /// unfiltered claim rather than restating it.</summary>
    public static IReadOnlyList<CardModel> Eligible(Player? owner)
    {
        var pile = owner == null ? null : CardPile.Get(Source, owner);
        return pile == null
            ? new List<CardModel>()
            : pile.Cards.ToList();
    }
}
