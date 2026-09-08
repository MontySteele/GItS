using System;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI POOL PASS SEVEN -- the unwritable card (`EB-711`, 2026-09-08,
/// review/active/kokomi-defend-2026-09-08.md).
///
/// THE FINDING, named by rounds 28 to 31 from two sides. Round 28 lane 2:
/// Defend is "the only card in the deck that cannot be pointed at the
/// jellyfish, so the only card that never poses the kit's question." Round 31
/// lane 2: the one dead turn of a 39-turn run was a hand of two Defends, two
/// Wounds and two cards it could not use. Round 31 lane 1 died on the elite to
/// a five-card hand with no Block at all against 21 incoming -- "the kit's
/// defence is concentrated in three cards, and two of them only pay when the
/// Casket is firing." Defend was unwritable, and Block was thin.
///
/// WHAT CHANGES, and it is one card: her basic Defend becomes HER card. "Gain
/// 5 Block, plus 2 if the Bake-Kurage is holding a Plan", upgrading 8 and 10.
///
/// AND WHAT DELIBERATELY DOES NOT. NOT a Plan line -- Block a turn late is the
/// half every seat has rejected, and a Dusk line on the basic would make
/// Breakwater strictly worse the day after it was rebuilt. NOT a rule: "the
/// jellyfish Blocks for you" is the decoration round 27 lane 2 warned of, and
/// a rule change is [USER]'s to play. So the card asks its question by
/// ORDERING instead: write first and Block for 7, or Block first for 5 and
/// keep the energy uncommitted.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on <see cref="KokomiPoolPassSixTests"/>'
/// split. The card shape is REAL -- face, cost, type, rarity, tag, var class
/// and the smith's move are read off the shipped class. The FOLD is not: a
/// preview needs a live combat, which this harness does not build
/// (`KokomiOverhaulRuleTests.EB522_a_calculated_face_folds_the_way_the_plan_line_does`
/// states that boundary), so the face is pinned off the var's own IL. The
/// end-to-end arithmetic is the sim twin's: the five `proto_kk_defend` cases
/// in <c>tier0/tests/test_kokomi_plan.py</c>.
///
/// THE NUMBERS ARE PROTOTYPE NUMBERS (D by the ladder). Nothing here is
/// quotable (R215 B).
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiPoolPassSevenTests
{
    private const BindingFlags All = HeadlessGame.All;

    // ======================================================================
    // 1. THE CARD -- one Block clause with a rider on it
    // ======================================================================

    [Fact]
    public void The_defend_prints_five_and_a_rider_of_two()
    {
        var card = new ProtoKkDefend();

        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(CardRarity.Basic, card.Rarity);
        Assert.Equal(TargetType.Self, card.TargetType);
        Assert.Equal(5m, card.DynamicVars.Block.BaseValue);
        Assert.Equal(
            "Gain {Block:diff()} [gold]Block[/gold], plus 2 if the "
            + "[gold]Bake-Kurage[/gold] is holding a [gold]Plan[/gold].",
            Face(card));

        // NOT A PLAN CARD, which is the half the pass did not take: the row
        // prints no Plan line at all, so the deck still holds one card the
        // jellyfish has no use for and the kit's question stays a question.
        Assert.IsNotAssignableFrom<IPlannedCard>(card);

        // AND A SKILL APPLIES NOTHING, so the catalyst cadence never reaches
        // it -- unlike her Strike, this row needs no `applies_element`
        // declaration to stay elementless.
        Assert.IsNotAssignableFrom<IElementalCard>(card);
    }

    [Fact]
    public void The_smith_moves_the_printed_five_and_leaves_the_rider_alone()
    {
        // The base Defend's +3 on the printed number, 5 -> 8, with the rider
        // still 2 -- so the `+` card is 8 and 10. Both arms take the SAME
        // `conditional_block` delta, which is exactly what keeps the rider
        // fixed while the base moves.
        var card = new ProtoKkDefend();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", All)!
            .Invoke(card, Array.Empty<object?>());

        Assert.Equal(8m, card.DynamicVars.Block.BaseValue);
        Assert.Equal(2m, Rider(card));

        var body = Source("ProtoKkDefend");
        Assert.Contains("new BlockVar((IsUpgraded ? 10m : 7m)", body);
        Assert.Contains("new BlockVar((IsUpgraded ? 8m : 5m)", body);
    }

    [Fact]
    public void One_gain_either_way_and_never_a_base_plus_a_second_gain()
    {
        // THE REASON THE ROW IS A THEN/ELSE. Two `GainBlock` calls would take
        // Dexterity and Frail TWICE (5+D then 2+D), while the face folds one
        // gain of 7 -- so the card would print a number it does not pay,
        // which is `EB-486`'s defect class arriving from the other end. One
        // clause, one gain, one var.
        var body = Source("ProtoKkDefend");
        var start = body.IndexOf("if (KokomiPlan.PlansHeld",
                                 StringComparison.Ordinal);
        var play = body.Substring(
            start,
            body.IndexOf("protected override void OnUpgrade",
                         StringComparison.Ordinal) - start);
        // Two emitted arms -- counted off the SOURCE, because `Il.Calls`
        // returns the distinct callees and both arms call the same one ...
        Assert.Equal(2, play.Split("CreatureCmd.GainBlock").Length - 1);
        // ... and they are the two halves of ONE if/else, so exactly one
        // runs. An `else` between them is what says so.
        Assert.Contains("else", play);
        // The var is the FACE's and the play reads literals off the same
        // derivation, which is `folded_branch_damage`'s arrangement one op
        // over -- so the play never gains the folded number twice.
        Assert.DoesNotContain("DynamicVars.Block", play);
    }

    // ======================================================================
    // 2. "HOLDING A PLAN" -- the queue, and one reader for it
    // ======================================================================

    [Fact]
    public void Holding_a_plan_is_the_queue_and_nothing_else_spells_it()
    {
        // THE PENDING QUEUE, read LIVE at the moment the card resolves: a
        // Plan written earlier this turn counts, a Dusk entry counts until it
        // resolves, and a queue the morning drained does not. That is
        // `KokomiPlan.PlansHeld`, which is Breakwater's per-Plan count and
        // Tide Chart's draw -- ONE definition of "holding a Plan" in this
        // engine, whose sim twin is `effects._predicate`'s `plan_held` over
        // `state.kk_plan_queue`.
        //
        // NOT `KokomiOverhaulLedger.PlansThisMorning`, which is the OTHER
        // number and the one that would have been wrong: it keeps yesterday's
        // value until the next drain, so a Defend played after the carry-out
        // would have paid for Plans the jellyfish no longer holds.
        var play = Il.Calls(Il.Method("ProtoKkDefend", "OnPlay"));
        Assert.Contains(play, c => c.Contains("KokomiPlan.PlansHeld"));
        Assert.DoesNotContain(play, c => c.Contains("PlansThisMorning"));
        Assert.DoesNotContain(play, c => c.Contains("PlanCarriedOutThisTurn"));

        Assert.Contains("if (KokomiPlan.PlansHeld(Owner.Creature) > 0)",
                        Source("ProtoKkDefend"));
    }

    // ======================================================================
    // 3. THE FACE -- the seat reads 7 BEFORE playing it
    // ======================================================================

    [Fact]
    public void The_printed_number_is_one_var_of_the_arms_own_class()
    {
        // ONE NUMBER, NOT FEINT'S PAIR. Feint prints two things the card
        // might do and declares a `FoldedDamageVar` apiece; this prints one
        // thing with a rider on it, which is what "Gain 5 Block, plus 2 if..."
        // says -- so it takes ONE var and that var folds the rider live.
        var block = (object)new ProtoKkDefend().DynamicVars.Block;
        Assert.IsType<KokomiPlan.PlanHeldBlockVar>(block);
        // IT SUBCLASSES `BlockVar`, WHICH IS NOT DECORATION: `DynamicVarSet.Block`
        // CASTS to it, so a plain DynamicVar under this token throws an
        // InvalidCastException the first time anything reads the face
        // (`SpotlightSystem.SpotlitBlockVar`'s pin, verbatim).
        Assert.IsAssignableFrom<BlockVar>(block);
        Assert.Equal("Block", KokomiPlan.PlanHeldBlockVar.Token);
        Assert.Equal(2m, ((KokomiPlan.PlanHeldBlockVar)block).Rider);

        Assert.Contains("new KokomiPlan.PlanHeldBlockVar(5m, 2m)",
                        Source("ProtoKkDefend"));
    }

    [Fact]
    public void The_face_folds_the_rider_live_and_asks_the_plays_own_reader()
    {
        // STRUCTURAL, and the boundary is the harness's: a preview reaches
        // `CardModel.CombatState`, which needs a live combat this harness does
        // not build. What is pinned is the wiring, and it is three facts.
        var preview = typeof(KokomiPlan.PlanHeldBlockVar)
            .GetMethod("UpdateCardPreview", All)!;
        var calls = Il.Calls(preview);

        // The game's own `BlockVar` runs FIRST, so Dexterity and Frail are the
        // engine's answer and this adds nothing to it ...
        Assert.Contains(calls,
            c => c.EndsWith("BlockVar.UpdateCardPreview",
                            StringComparison.Ordinal));
        // ... the question it then asks is the PLAY's own reader, so the face
        // and the gain cannot disagree about what "holding a Plan" is ...
        Assert.Contains(calls, c => c.Contains("KokomiPlan.PlansHeld"));
        // ... and the rider is folded through a throwaway `BlockVar`, which is
        // the same hook pass the single emitted `GainBlock` will make -- that
        // order and not the reverse, so a percentage cannot compound against
        // the wrong base (`SpotlitBlockVar`'s own reason).
        Assert.Contains(calls, c => c.Contains(".ctor"));
    }

    // ======================================================================
    // 4. THE TAG -- "one of your Defends" still has exactly one answer
    // ======================================================================

    [Fact]
    public void Her_defend_wears_the_defend_tag_and_her_other_basics_do_not()
    {
        // `EB-543` FROM THE OTHER END, which is pool pass six's argument one
        // tag over: with her Defend now her own card, an untagged row would
        // leave Fasten's picture and every "one of your Defends" with NO
        // answer in her deck. `EB-352` is the row that found that exact throw
        // from the pool side.
        Assert.Contains(CardTag.Defend, new ProtoKkDefend().Tags);
        Assert.DoesNotContain(CardTag.Strike, new ProtoKkDefend().Tags);

        // EXCLUSIVITY: her Strike answers the other question and neither of
        // the two remaining basics answers either, so each scan has one hit
        // per copy of one card.
        Assert.Contains(CardTag.Strike, new ProtoKkStrike().Tags);
        Assert.DoesNotContain(CardTag.Defend, new ProtoKkStrike().Tags);
        foreach (var other in new CardModel[]
                 { new ProtoKkSlackWater(), new ProtoKkKuragesOath() })
        {
            Assert.Equal(CardRarity.Basic, other.Rarity);
            Assert.DoesNotContain(CardTag.Defend, other.Tags);
        }
    }

    [Fact]
    public void The_tag_is_declared_on_the_sheet_and_not_re_derived()
    {
        // DERIVATION IS WHAT OVER-TAGGED SLACK WATER (`EB-409`, `EB-543`).
        // The sheet names the ONE row that IS the Defend (`basic_tag: defend`)
        // and the codegen emits the tag from that alone; Tide Wall, Shell
        // Guard and Coral Bulwark all gain Block and none of them is it.
        Assert.Contains(
            "protected override HashSet<CardTag> CanonicalTags => "
            + "new() { CardTag.Defend };",
            Source("ProtoKkDefend"));
        Assert.DoesNotContain("CanonicalTags", Source("ProtoKkTideWall"));
        Assert.DoesNotContain("CanonicalTags", Source("ProtoKkShellGuard"));
    }

    // ======================================================================
    // 5. THE WIRING -- both starter seams, and the offer screen it stays off
    // ======================================================================

    [Fact]
    public void The_starter_deals_four_of_hers_and_no_shipped_defend()
    {
        var deck = Cards("KokomiOverhaulRoster", "StartingDeck");

        Assert.Equal(10, deck.Count);
        Assert.Equal(4, deck.Count(c => c == "ModelDb.Card<ProtoKkDefend>"));
        Assert.DoesNotContain(deck, c => c.Contains("DefendSilent"));
        Assert.DoesNotContain(deck, c => c.Contains("DefendIronclad"));
        // With pool pass six's half beside it, NEITHER basic is a base card
        // now -- so the deck screen's one borrowed-colour seam is closed.
        Assert.Equal(4, deck.Count(c => c == "ModelDb.Card<ProtoKkStrike>"));
        Assert.DoesNotContain(deck, c => c.Contains("StrikeSilent"));
    }

    [Fact]
    public void The_fourth_seam_hands_out_the_same_defend_the_deck_deals()
    {
        // `EB-351`'s seam, one card over from pool pass six: Large Capsule's
        // "an additional Strike and Defend" asks the CHARACTER, and handing
        // back a `DefendSilent` would drop a flat 5 into a deck whose Defends
        // all read the queue.
        Assert.Equal(new[] { "ModelDb.Card<ProtoKkDefend>" },
                     Cards("KokomiOverhaulRoster", "StarterDefend"));
        Assert.Equal(new[] { "ModelDb.Card<ProtoKkStrike>" },
                     Cards("KokomiOverhaulRoster", "StarterStrike"));
    }

    [Fact]
    public void The_basic_is_in_the_pool_for_lookup_and_out_of_every_offer()
    {
        // BOTH HALVES ARE LOAD-BEARING, and they are the quarantine's own
        // (`PrototypeRoster`'s header): IN `AllCards`, because a poolless card
        // throws "You monster!" the moment it is drawn and this one is drawn
        // every turn; OUT of `Slice()`, which IS `FilterThroughEpochs` and
        // therefore every reward roll, shop shelf and card transform.
        // `tools/lint_arm_pool_parity.py` is the gate on the second half --
        // `basic` is the starter's mark and the only exemption it allows.
        var roster = Il.CallSequence(
            Il.Method("PrototypeRoster", "BuildKokomi"))
            .Aggregate(string.Empty, (a, c) => a + c);
        Assert.Contains("ProtoKkDefend", roster);

        var slice = Il.CallSequence(Il.Method("KokomiOverhaulRoster", "Slice"))
            .Aggregate(string.Empty, (a, c) => a + c);
        Assert.DoesNotContain("ProtoKkDefend", slice);
    }

    // ======================================================================
    // helpers -- KokomiPoolPassSixTests' own, for its reasons
    // ======================================================================

    private static System.Collections.Generic.IReadOnlyList<string> Cards(
        string type, string method) =>
        Il.CallSequence(Il.Method(type, method))
            .Where(c => c.StartsWith("ModelDb.Card")).ToList();

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static decimal Rider(CardModel card) =>
        ((KokomiPlan.PlanHeldBlockVar)card.DynamicVars.Block).Rider;

    /// <summary>One class's own source, read off disk. A SOURCE READ and not
    /// an IL one, and only for the facts IL cannot carry: a `CanonicalTags`
    /// override is a property initialiser whose absence leaves no call at
    /// all, and a literal is not a call either.</summary>
    private static string Source(string type)
    {
        var root = System.AppContext.BaseDirectory;
        var repo = new System.IO.DirectoryInfo(root);
        while (repo != null && !System.IO.Directory.Exists(
                   System.IO.Path.Combine(repo.FullName, "klee-mod")))
        {
            repo = repo.Parent;
        }
        Assert.NotNull(repo);
        return System.IO.File.ReadAllText(System.IO.Path.Combine(
            repo!.FullName, "klee-mod", "KleeCode", "Cards", "Prototype",
            "Generated", type + ".cs"));
    }
}
