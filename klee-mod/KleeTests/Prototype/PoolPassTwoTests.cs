using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE ROUND-11 POOL PASS -- one row, <c>ProtoKoStokeTheFuse</c> (2026-09-04).
///
/// THE FINDING, and it is the OTHER half of the one round 10 answered. The
/// round-11 and round-12 seats ended fights holding 4 to 9 unspent Sparks:
/// the bank fills from every explosion (rule 4) and the arm had almost
/// nowhere to spend it that was not a detonator. A Spark sink was drafted
/// beside Countdown and WITHDRAWN on the card audit's C3 clause -- Explosive
/// Spark turned leftover energy into damage measured in banked Sparks, so its
/// value followed the bank rather than a decision. This row is that sink
/// written a second time with its value following the BOMB: the whole bank
/// buys growth on the one charge the player chose to keep cooking, and buys
/// nothing at all on a board with no Bomb on it.
///
/// THE FIRST X PRICE ON ANY SHEET. <c>spend_spark: all</c> prints no number,
/// so the two halves of a Spark cost line come apart here for the first time:
/// what the GATE charges is one (an empty bank cannot pay, any bank holding a
/// Spark can) and what the card PAYS is the whole bank. tier0 says the same
/// thing through <c>effects.spend_spark_price</c> and
/// <c>effects._op_spend_spark</c>.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL. The growth is real --
/// <see cref="ProtoBombPower.GrowLargestPerSpark"/> against real piles on a
/// real <c>CombatState</c>, including the board-wide pick and the two ways it
/// pays nothing -- and so is the gate's arithmetic through
/// <c>SparkPower.CanSpend</c> on a seat with a real bank. What needs a card
/// PLAY (the payment is <c>PowerCmd.ModifyAmount</c>) is pinned off the
/// compiled <c>OnPlay</c>, labelled. The end-to-end arithmetic is the sim
/// twin's: <c>tier0/tests/test_klee_overhaul_rules.py</c>, section "THE POOL
/// PASS, ROUND 11".
///
/// THE NUMBERS ARE PROTOTYPE NUMBERS (D by the ladder). Nothing here is
/// quotable.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class PoolPassTwoTests
{
    private const BindingFlags All = HeadlessGame.All;

    // ---- the X price: the gate charges one ------------------------------

    [Fact]
    public void Stoke_the_fuse_is_unplayable_at_zero_sparks()
    {
        // THE X PRICE'S GATE, real. "Spend all your Sparks" declares a
        // PrintedSparkPrice of 1, which is what makes an empty bank refuse the
        // play and any bank holding a Spark allow it. Without it the card
        // would be playable at 0 and resolve to nothing -- the silent no-play
        // the Spark cost line exists to refuse. Twin:
        // `test_stoke_the_fuse_is_unplayable_at_zero_sparks`.
        var card = new ProtoKoStokeTheFuse();
        Assert.Equal(1, card.PrintedSparkPrice);
        Assert.Equal(1, SparkCost.PriceOf(card));

        Assert.False(SparkPower.CanSpend(
            Seat.Klee().WithPower<SparkPower>(0).Creature, SparkCost.PriceOf(card)));
        Assert.True(SparkPower.CanSpend(
            Seat.Klee().WithPower<SparkPower>(1).Creature, SparkCost.PriceOf(card)));
        Assert.True(SparkPower.CanSpend(
            Seat.Klee().WithPower<SparkPower>(9).Creature, SparkCost.PriceOf(card)));
    }

    [Fact]
    public void Stoke_the_fuse_captures_the_bank_before_it_spends_it()
    {
        // STRUCTURAL, and it is the whole ordering rule. `SparkPower.Spend`
        // debits where it is called, so the number of Sparks SPENT has to be
        // read BEFORE the payment and carried to the payout -- reading the
        // bank afterwards would read zero and the card would grow nothing.
        // `SparksAtPlay` is the accessor whose sim twin is
        // `state.sparks_at_play`, and the codegen refuses the payout op on any
        // row that does not open with this price.
        var play = Il.CallSequence(Il.Method("ProtoKoStokeTheFuse", "OnPlay"))
            .ToList();
        var read = play.FindIndex(c => c.Contains("SparkPower.SparksAtPlay"));
        var spend = play.FindIndex(c => c.Contains("SparkPower.Spend"));
        var grow = play.FindIndex(
            c => c.Contains("ProtoBombPower.GrowLargestPerSpark"));

        Assert.True(read >= 0, "the row reads the bank it is about to spend");
        Assert.True(spend >= 0, "the row spends it");
        Assert.True(grow >= 0, "the row pays out");
        Assert.True(read < spend, "the bank is read before it is emptied");
        Assert.True(spend < grow, "the price is paid before the payout");
    }

    [Fact]
    public void Stoke_the_fuse_sets_nothing_off()
    {
        // IT IS NOT A DETONATOR, and that is the row's whole shape: the Sparks
        // buy a bigger Bomb and the cash-out is still a separate card, so
        // hold-or-cash stays in the player's hands. A Set off arriving here
        // later would make the sink a finisher, so its ABSENCE is the pin.
        var play = Il.Calls(Il.Method("ProtoKoStokeTheFuse", "OnPlay"));

        Assert.DoesNotContain(play, c => c.Contains("SetOff"));
        Assert.DoesNotContain(play, c => c.Contains("Detonate"));
        Assert.DoesNotContain(play, c => c.Contains("TakeAll"));
    }

    // ---- the payout, real ------------------------------------------------

    [Fact]
    public void Stoke_the_fuse_grows_the_largest_bomb_by_three_per_spark()
    {
        // REAL. Three Sparks at 3 apiece put 9 on the charge, and the charge
        // it lands on is the LARGEST ONE on the board -- not the pile summed
        // and not one enemy's. Twins:
        // `test_stoke_the_fuse_spends_the_whole_bank_and_grows_per_spark`,
        // `test_stoke_the_fuse_grows_the_largest_of_two_bombs`.
        var klee = Seat.Klee();
        var a = Seat.Klee(200).Creature;
        var b = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, a, b);

        var pileA = ProtoBombs.Place(a, klee.Creature,
                                     new ProtoBombs.Charge(4),
                                     new ProtoBombs.Charge(9));
        var pileB = ProtoBombs.Place(b, klee.Creature, new ProtoBombs.Charge(7));

        Assert.Equal(9, ProtoBombPower.GrowLargestPerSpark(
            klee.Creature, perSpark: 3, sparksSpent: 3));

        Assert.Equal(new[] { 4, 18 }, pileA.Charges.Select(c => c.Size));
        Assert.Equal(new[] { 7 }, pileB.Charges.Select(c => c.Size));
    }

    [Fact]
    public void Stoke_the_fuse_upgraded_pays_four_per_spark()
    {
        // The rate is the row's one printed number and the only thing the
        // smith moves, so three Sparks buy 12 instead of 9. Twin:
        // `test_stoke_the_fuse_upgraded_pays_four_per_spark`.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, enemy);
        var pile = ProtoBombs.Place(enemy, klee.Creature,
                                    new ProtoBombs.Charge(6));

        Assert.Equal(12, ProtoBombPower.GrowLargestPerSpark(
            klee.Creature, perSpark: 4, sparksSpent: 3));
        Assert.Equal(new[] { 18 }, pile.Charges.Select(c => c.Size));
    }

    [Fact]
    public void Stoke_the_fuse_pays_nothing_on_a_bomb_less_board()
    {
        // REAL, all the way through the shipped method: nothing to grow, so
        // the bank is spent and the card does nothing. That is the row's
        // losing line -- the one the charter asks every card to keep -- and it
        // is why the sink is keyed to the Bomb rather than to the bank.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, enemy);

        Assert.Equal(0, ProtoBombPower.GrowLargestPerSpark(
            klee.Creature, perSpark: 3, sparksSpent: 3));
    }

    [Fact]
    public void Stoke_the_fuse_pays_nothing_at_an_empty_bank()
    {
        // The gate above is what a player sees; this is the runtime's own
        // answer beside it, and it is why a bank of 0 cannot grow a Bomb
        // through some other caller either.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, enemy);
        var pile = ProtoBombs.Place(enemy, klee.Creature,
                                    new ProtoBombs.Charge(6));

        Assert.Equal(0, ProtoBombPower.GrowLargestPerSpark(
            klee.Creature, perSpark: 3, sparksSpent: 0));
        Assert.Equal(0, ProtoBombPower.GrowLargestPerSpark(
            klee.Creature, perSpark: 0, sparksSpent: 3));
        Assert.Equal(new[] { 6 }, pile.Charges.Select(c => c.Size));
    }

    [Fact]
    public void The_growth_lands_on_one_charge_and_not_the_pile()
    {
        // ONE CHARGE, NOT THE PILE, and that is the row's decision:
        // `GrowOn` (Chain Fuse, Quick Fuse) spreads growth across an enemy's
        // charges, and this pours the bank into the one she is already
        // cooking. Read off the compiled method beside the arithmetic above,
        // so a future edit that reached for `GrowBy` would fail here.
        var calls = Il.Calls(Il.Method("ProtoBombPower", "GrowLargestPerSpark"));

        Assert.Contains(calls, c => c.Contains("GrowLargestChargeBy"));
        Assert.DoesNotContain(calls, c => c.EndsWith("ProtoBombPower.GrowBy"));
    }

    // ---- the card, real off the shipped class ---------------------------

    [Fact]
    public void Stoke_the_fuse_prints_its_rate_and_the_smith_moves_it()
    {
        // The row's ONE printed number is the RATE, because the multiplier is
        // the bank and the bank is not the card's to print. So the face prints
        // the rate as a var and `OnUpgrade` moves that same var -- or the `+`
        // card promises a rate it does not pay (`EB-283` / `EB-291`).
        var card = new ProtoKoStokeTheFuse();

        Assert.Contains("{Grow:diff()}", Face(card));
        Assert.Contains("all your [gold]Sparks[/gold]", Face(card));
        Assert.Equal(3m, Vars(card).Single().BaseValue);
        Assert.Contains(
            Il.Calls(Il.Method("ProtoKoStokeTheFuse", "OnUpgrade")),
            c => c.Contains("UpgradeValueBy"));

        // And the play hands the VAR to the rule, so the smithed rate is the
        // rate the growth is measured at.
        Assert.Contains(Il.Calls(Il.Method("ProtoKoStokeTheFuse", "OnPlay")),
                        c => c.EndsWith("get_IntValue"));
    }

    [Fact]
    public void Stoke_the_fuse_is_an_uncommon_spark_priced_skill()
    {
        // AN UNCOMMON AND NOT A COMMON, which is the other half of round 10's
        // argument: a detonator a seat has to be OFFERED often is a Common,
        // and a sink that pays only into a Bomb already cooking is a card a
        // deck is built around.
        var card = new ProtoKoStokeTheFuse();

        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.Equal(CardType.Skill, card.Type);
        Assert.True(typeof(ISparkPricedCard)
                        .IsAssignableFrom(typeof(ProtoKoStokeTheFuse)));
    }

    [Fact]
    public void Stoke_the_fuse_is_offered_by_the_arm_and_is_not_in_the_starter()
    {
        // `lint_arm_pool_parity` is the gate that holds this list to the sheet
        // and to `C.KLEE_OVERHAUL_POOL_IDS`; what a pin adds is that the row
        // the finding asked for is actually on the OFFER seam, which is the
        // seam R252 forgot.
        var slice = Il.CallSequence(Il.Method("KleeOverhaulRoster", "Slice"));
        Assert.Contains(slice, c => c.Contains("ProtoKoStokeTheFuse"));

        var starter = Il.CallSequence(
            Il.Method("KleeOverhaulRoster", "StartingDeck"));
        Assert.DoesNotContain(starter, c => c.Contains("ProtoKoStokeTheFuse"));
    }

    // ---- helpers ---------------------------------------------------------

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    /// <summary><c>CanonicalVars</c> is protected, so it is read the way every
    /// other internal seam in this project is read.</summary>
    private static IReadOnlyList<DynamicVar> Vars(CardModel card) =>
        ((IEnumerable<DynamicVar>)typeof(CardModel)
            .GetProperty("CanonicalVars", All)!.GetValue(card)!).ToList();
}
