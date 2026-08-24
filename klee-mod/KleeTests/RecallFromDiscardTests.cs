using System.Linq;
using KleeMod.Cards.Kokomi.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Entities.Cards;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-122: `recall_to_draw` reading its DEFAULT source, the discard pile --
/// the C# leg of EB-69's `what_the_tokoyo_returns`.
///
/// THE WHOLE POINT OF THIS FILE IS AN ASYMMETRY, and it is deliberate on both
/// sides. <see cref="RecallFromExhaust"/> filters its pool four ways and hands
/// the returned card an Exhaust, because EB-118 §6.4 required it.
/// <see cref="RecallFromDiscard"/> filters NOTHING and grants NOTHING, because
/// [USER] ruled the unfiltered discard branch DELIBERATE (EB-69 / D3, R198):
/// a card thrown away by an effect can have its own Sly rider recall ITSELF.
/// `tier0/tests/test_eb69_tokoyo_returns_selfrecall.py` is the sim pin and
/// this leg's spec. A future change that tidies the two into one filtered
/// implementation breaks a shipped card on purpose and must say so.
///
/// The move needs a live CombatState, so it is pinned STRUCTURALLY -- the call
/// set of the one method both faces route through, plus the pile and placement
/// choices, which are members precisely so a test can read them without a
/// combat (README.md, the headless boundary).
/// </summary>
public class RecallFromDiscardTests
{
    // --- where it reads, where it lands ---------------------------------

    [Fact]
    public void The_source_is_the_discard_pile_and_the_destination_is_the_draw_pile()
    {
        Assert.Equal(PileType.Discard, RecallFromDiscard.Source);
        Assert.Equal(PileType.Draw, RecallFromDiscard.Destination);
        // Never the hand. The sim's twin is `p.draw_pile.insert(0, pick)`
        // with no hand branch to get wrong, on BOTH sources.
        Assert.NotEqual(PileType.Hand, RecallFromDiscard.Destination);
    }

    [Fact]
    public void The_card_lands_on_TOP_of_the_draw_pile()
    {
        Assert.Equal(CardPilePosition.Top, RecallFromDiscard.Placement);
    }

    [Fact]
    public void The_two_sources_agree_about_the_destination_and_disagree_about_nothing_else()
    {
        // One verb, two piles: the sim has a single `_op_recall_to_draw` whose
        // destination is outside the `if from_exhaust` branch. If these ever
        // differ, the mod has two verbs where the sim has one.
        Assert.Equal(RecallFromExhaust.Destination, RecallFromDiscard.Destination);
        Assert.Equal(RecallFromExhaust.Placement, RecallFromDiscard.Placement);
        Assert.NotEqual(RecallFromExhaust.Source, RecallFromDiscard.Source);
    }

    // --- the unfiltered claim, which IS the contract ---------------------

    [Fact]
    public void The_discard_branch_applies_no_pool_filter()
    {
        // Stated as an absence, because that is what the ruling is. The
        // exhaust branch's four exclusions are its own; asserting them here
        // would be asserting the bug.
        var calls = Il.Calls(Il.Method("RecallFromDiscard", "Recall"));

        Assert.Contains("CardSelectCmd.FromCombatPile", calls);
        Assert.Contains("CardPileCmd.Add", calls);
        Assert.DoesNotContain("RecallFromExhaust.Recallable", calls);
        Assert.DoesNotContain("KitGrant.NotKitCard", calls);
        Assert.DoesNotContain("KokomiResources.IsJunk", calls);
    }

    [Fact]
    public void Nothing_comes_back_on_loan()
    {
        // The exhaust branch's price. A discard-pile card was coming back on
        // the next reshuffle regardless, so there is nothing to price -- and
        // tier0 sets `pick.exhaust = True` inside `if from_exhaust:` only.
        var calls = Il.Calls(Il.Method("RecallFromDiscard", "Recall"));

        Assert.DoesNotContain("CardModel.AddKeyword", calls);
    }

    [Fact]
    public void The_recall_never_draws_and_never_adds_to_the_hand()
    {
        var calls = Il.Calls(Il.Method("RecallFromDiscard", "Recall"));

        Assert.DoesNotContain("CardPileCmd.Draw", calls);
        Assert.DoesNotContain("CardPileCmd.AddGeneratedCardToCombat", calls);
    }

    // --- the self-recall, which is what D3 ruled -------------------------

    [Fact]
    public void The_carrier_is_not_an_exhaust_retriever()
    {
        // Constraint 3's marker is the EXHAUST pool's cycle exclusion, and a
        // discard reader is not in that cycle. Stamping it would have quietly
        // removed this card from a pool it belongs in -- and the sim reads the
        // same distinction off `from` (`effects.retrieves_from_exhaust`).
        // `is` would be a COMPILE-time answer here (and a warning); the type
        // test is the runtime question the pool filter actually asks.
        Assert.False(typeof(IExhaustRetriever)
            .IsInstanceOfType(new WhatTheTokoyoReturns()));
        // ... while the pool that DOES exclude retrievers still accepts it,
        // which is the other half of the same fact.
        Assert.True(RecallFromExhaust.Recallable(new WhatTheTokoyoReturns()));
    }

    [Fact]
    public void Both_faces_route_through_the_same_call()
    {
        // THE SELF-RECALL, as close as the headless boundary allows. The
        // played face is resolving and so is not in a pile; the Sly face IS in
        // the discard pile when its rider fires, because
        // CardCmd.DiscardAndDraw adds the victim to the pile BEFORE firing
        // Hook.AfterCardDiscarded (verified against sts2.dll v0.107.1). The
        // two faces therefore differ by WHERE THE CARD IS, not by what the
        // call does -- which is exactly the sim's story, and is why the same
        // call has to appear on both.
        Assert.Contains("RecallFromDiscard.Recall",
            Il.Calls(Il.Method("WhatTheTokoyoReturns", "OnPlay")));
        Assert.Contains("RecallFromDiscard.Recall",
            Il.Calls(Il.Method("WhatTheTokoyoReturns", "AfterCardDiscarded")));
    }

    [Fact]
    public void The_prompt_is_an_owed_stand_in_and_not_invented_copy()
    {
        // The base game ships no "retrieve" prompt -- Headbutt renders this
        // screen from its own per-card `cards/<id>.selectionScreenPrompt` row
        // -- and authoring that string is a player-facing TEXT call. It stands
        // at the prompt naming the PILE the screen is showing, in ONE member,
        // the same way RecallFromExhaust's does. A recorded decision, not a
        // silent one.
        Assert.Equal(CardSelectorPrefs.DiscardSelectionPrompt.ToString(),
                     RecallFromDiscard.Prompt.ToString());
    }
}
