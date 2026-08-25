using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Kokomi;
using KleeMod.Cards.Kokomi.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-122: the turn-scoped Sly grant (`grant_sly_this_turn`), the C# leg of
/// EB-69's `the_gunbai_turns` and `raise_the_sashimono`.
///
/// Two kinds of test here, and the split is the headless boundary
/// (KleeTests/README.md). <see cref="SlyGrant.Eligible"/> is a pure predicate
/// over a CardModel, so it RUNS -- those are real assertions about shipped
/// behaviour. The grant itself needs a live CombatState (a selection screen
/// and a card in a hand), so it is pinned STRUCTURALLY: the call set of the
/// one method every carrier routes through.
///
/// Sim twin: tier0 `effects._op_grant_sly_this_turn`, pinned beside its own
/// engine in `tier0/tests/test_eb122_csharp_grammar.py`.
/// </summary>
public class SlyGrantTests
{
    private sealed class ProbeSkill : CustomCardModel
    {
        public ProbeSkill()
            : base(1, CardType.Skill, CardRarity.Uncommon, TargetType.Self,
                   autoAdd: false)
        {
        }

        protected override Task OnPlay(
            PlayerChoiceContext choiceContext, CardPlay cardPlay)
            => Task.CompletedTask;
    }

    private sealed class ProbeAttack : CustomCardModel
    {
        public ProbeAttack()
            : base(1, CardType.Attack, CardRarity.Uncommon, TargetType.AnyEnemy,
                   autoAdd: false)
        {
        }

        protected override Task OnPlay(
            PlayerChoiceContext choiceContext, CardPlay cardPlay)
            => Task.CompletedTask;
    }

    // --- the pool: a pure predicate, so it runs --------------------------

    [Fact]
    public void An_ordinary_skill_is_a_legal_target()
    {
        Assert.True(SlyGrant.Eligible(new ProbeSkill()));
    }

    [Fact]
    public void An_attack_is_not()
    {
        // The game's own filter on this verb is `card.Type == CardType.Skill`
        // (Hand Trick), and `skill` is the only `card_type` the sheet spells.
        Assert.False(SlyGrant.Eligible(new ProbeAttack()));
    }

    [Fact]
    public void A_kit_card_is_never_a_target()
    {
        // The v1.9 invariant: the Burst is never fodder. The sim spells the
        // same clause on the same pool (`not c.kit_card`).
        Assert.False(SlyGrant.Eligible(new SparksNSplash()));
        Assert.False(SlyGrant.Eligible(new CeremonialGarment()));
    }

    [Fact]
    public void A_card_already_sly_this_turn_is_skipped()
    {
        // WHY THE CLAUSE EXISTS: a second grant in one turn must pick a
        // DIFFERENT card rather than wasting itself on one already granted.
        // the_gunbai_turns grants three times in a row and would otherwise
        // spend all three on the same Skill.
        //
        // AddKeyword calls AssertMutable, and a freshly constructed CardModel
        // is the canonical prototype, so the flag ToMutable would have set is
        // set directly (M2's idiom, ParityAuthorityPinTests).
        var granted = new ProbeSkill();
        Seat.Set(granted, "IsMutable", true);
        granted.GiveSingleTurnSly();

        Assert.True(granted.IsSlyThisTurn);
        Assert.False(SlyGrant.Eligible(granted));
    }

    // --- the grant itself: STRUCTURAL pin (see the class doc) ------------

    [Fact]
    public void The_grant_selects_from_hand_and_uses_the_games_own_single_turn_call()
    {
        var calls = Il.Calls(Il.Method("SlyGrant", "Grant"));

        Assert.Contains("CardSelectCmd.FromHand", calls);
        // The expiry is the GAME's: ApplySingleTurnSly sets a flag the game
        // itself clears at end of turn. A mod-side timer would be a different
        // mechanic wearing the same name.
        Assert.Contains("CardCmd.ApplySingleTurnSly", calls);
        // The filter is the shared predicate, not a re-spelling of it.
        Assert.Contains("SlyGrant.Eligible", calls);
    }

    [Fact]
    public void The_grant_never_plays_discards_or_permanently_keywords_a_card()
    {
        // The three ways "make this Sly for a turn" could be got wrong: play
        // it now, throw it now, or make the keyword permanent.
        var calls = Il.Calls(Il.Method("SlyGrant", "Grant"));

        Assert.DoesNotContain("CardCmd.AutoPlay", calls);
        Assert.DoesNotContain("CardCmd.Discard", calls);
        Assert.DoesNotContain("CardModel.AddKeyword", calls);
    }

    [Fact]
    public void Every_carrier_routes_through_the_one_home()
    {
        // One C# home for the verb, the RecallFromExhaust discipline. A card
        // that re-spelled the filter would drift from the other carrier the
        // first time either changed.
        foreach (var name in new[] { "TheGunbaiTurns", "RaiseTheSashimono" })
        {
            var calls = Il.Calls(Il.Method(name, "OnPlay"));
            Assert.Contains("SlyGrant.Grant", calls);
            Assert.DoesNotContain("CardCmd.ApplySingleTurnSly", calls);
        }
    }

    [Fact]
    public void The_prompt_reads_the_ruled_copy_and_not_a_stand_in()
    {
        // EB-122's owed half, DISCHARGED 2026-08-25. The stand-in this
        // replaces was DiscardSelectionPrompt, which named the wrong pile
        // entirely -- this screen reads the HAND.
        Assert.Equal(
            "Choose a Skill in your hand. It gains [gold]Sly[/gold] this turn.",
            SlyGrant.PromptText);
        Assert.NotEqual(CardSelectorPrefs.DiscardSelectionPrompt.LocEntryKey,
                        SlyGrant.Prompt.LocEntryKey);
    }

    [Fact]
    public void The_prompt_is_wired_to_a_row_that_is_actually_injected()
    {
        // A LocString is a table plus a key: nothing checks at compile time
        // that the key resolves, and an unresolved one renders as the literal
        // key on the selection screen -- the exact defect that shipped as
        // "card_keywords.KLEEMOD-COMPANION_RIDER.title" in 0.2-589. The row is
        // merged in KleeMod.InjectLocStrings, which reaches Godot on the way
        // in (README, the headless boundary), so it is pinned STRUCTURALLY:
        // both the key and the ruled text are string literals in that method
        // because both are consts read from this class.
        Assert.Equal("cards", SlyGrant.Prompt.LocTable);
        Assert.Equal(SlyGrant.PromptKey, SlyGrant.Prompt.LocEntryKey);
        Assert.EndsWith(".selectionScreenPrompt", SlyGrant.PromptKey);

        var injected = Il.Strings(Il.Method("KleeMod", "InjectLocStrings"));
        Assert.Contains(SlyGrant.PromptKey, injected);
        Assert.Contains(SlyGrant.PromptText, injected);
    }
}
