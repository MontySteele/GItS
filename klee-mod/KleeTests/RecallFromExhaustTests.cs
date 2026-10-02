using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Kokomi;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-118, the mod's leg: exhaust-pile retrieval as a SOURCE on the recall
/// verb. The six constraints of §6.4 are enforced by the op and the
/// generator, never by card authors, and the four runtime ones live in
/// <see cref="RecallFromExhaust"/>.
///
/// Two kinds of test here, and the difference is the headless boundary
/// (KleeTests/README.md). The pool filter is a pure predicate over a
/// CardModel, so it RUNS -- these are real assertions about the shipped
/// behaviour. The move itself (select, place on top, grant the keyword)
/// needs a live CombatState, so it is pinned STRUCTURALLY: the call set of
/// the one method both engines route through, plus the pile and placement
/// choices, which are members precisely so a test can read them without a
/// combat.
///
/// Sim twin for everything below: tier0 effects.recall_exhaust_pool and
/// _op_recall_to_draw, pinned in tier0/tests/test_eb118_recall_exhaust.py.
/// </summary>
public class RecallFromExhaustTests
{
    /// <summary>Stands in for the card no sheet ships yet. EB-118 is staged:
    /// the capability exists and nothing is built on it, so the retriever
    /// exclusion would have nothing to exclude without this.</summary>
    private sealed class ProbeRetriever : CustomCardModel, IExhaustRetriever
    {
        public ProbeRetriever()
            : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.Self,
                   autoAdd: false)
        {
        }

        protected override Task OnPlay(
            PlayerChoiceContext choiceContext, CardPlay cardPlay)
            => Task.CompletedTask;
    }

    // --- constraints 3 and 6: the runtime pool ---------------------------

    [Fact]
    public void A_status_is_never_recallable()
    {
        // Constraint 6, which is the C11 rotation law from the other end.
        Assert.False(RecallFromExhaust.Recallable(new Confiscated()));
    }

    [Fact]
    public void A_card_that_retrieves_from_exhaust_is_never_recallable()
    {
        // Constraint 3, the cycle exclusion -- and the self case with it: a
        // retrieval card Exhausts, so the pile it reads contains itself, and
        // it is excluded by the same clause that excludes any other
        // retriever.
        Assert.False(RecallFromExhaust.Recallable(new ProbeRetriever()));
    }

    // --- constraints 4 and 5: where it lands, and on what terms ----------

    [Fact]
    public void The_source_is_the_exhaust_pile_and_the_destination_is_the_draw_pile()
    {
        Assert.Equal(PileType.Exhaust, RecallFromExhaust.Source);
        Assert.Equal(PileType.Draw, RecallFromExhaust.Destination);
        // Never the hand. The sim's twin is `p.draw_pile.insert(0, pick)`
        // with no hand branch to get wrong.
        Assert.NotEqual(PileType.Hand, RecallFromExhaust.Destination);
    }

    [Fact]
    public void The_card_lands_on_TOP_of_the_draw_pile()
    {
        Assert.Equal(CardPilePosition.Top, RecallFromExhaust.Placement);
    }

    [Fact]
    public void What_comes_back_gains_Exhaust()
    {
        Assert.Equal(CardKeyword.Exhaust, RecallFromExhaust.Loan);
    }

    // --- the move itself: STRUCTURAL pin (see the class doc) -------------

    [Fact]
    public void The_recall_selects_from_a_pile_places_the_card_and_grants_the_keyword()
    {
        var calls = Il.Calls(Il.Method("RecallFromExhaust", "Recall"));

        Assert.Contains("CardSelectCmd.FromCombatPile", calls);
        Assert.Contains("CardPileCmd.Add", calls);
        Assert.Contains("CardModel.AddKeyword", calls);
        // The filter is the shared predicate, not a re-spelling of it.
        Assert.Contains("RecallFromExhaust.Recallable", calls);
    }

    [Fact]
    public void The_recall_never_draws_and_never_adds_to_the_hand()
    {
        // Constraint 4 from the other side: the two verbs that would put the
        // card anywhere but the draw pile are absent.
        var calls = Il.Calls(Il.Method("RecallFromExhaust", "Recall"));

        Assert.DoesNotContain("CardPileCmd.Draw", calls);
        Assert.DoesNotContain("CardPileCmd.AddGeneratedCardToCombat", calls);
    }
}
