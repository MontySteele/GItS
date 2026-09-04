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
/// THE ROUND-10 POOL PASS -- one row, <c>ProtoKoCountdown</c> (2026-09-04).
///
/// THE FINDING. Three round-10 seats held Spark-priced detonators at 0 Spark
/// with a fat Bomb sitting on the enemy and no energy-priced detonator drawn.
/// Ka-pow! is the arm's only unconditional cash button and it is the STARTER's
/// -- one card in ten -- so a hand that has spent its Sparks has nothing that
/// sets the pile off. Countdown is the pool's answer at Common: 1 energy, Set
/// off, draw a card, no Spark and no condition, beside Sizzle's
/// reaction-keyed one.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL. Both of the card's clauses are
/// commands (<c>ProtoBombPower.SetOffAimed</c> and <c>CardPileCmd.Draw</c>),
/// which the headless harness cannot spend, so the ORDER and the WIRING are
/// pinned off the compiled <c>OnPlay</c> and the arithmetic is the sim twin's:
/// <c>tier0/tests/test_klee_overhaul_rules.py</c>, section "THE POOL PASS".
/// The face, its var and the smith's move are real off the shipped class.
///
/// THE NUMBERS ARE PROTOTYPE NUMBERS (D by the ladder). Nothing here is
/// quotable.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class PoolPassTests
{
    private const BindingFlags All = HeadlessGame.All;

    [Fact]
    public void Countdown_sets_off_before_it_draws()
    {
        // THE ORDER IS THE CARD. The explosion resolves first, so the card the
        // draw finds arrives into a board the Set off has already cleared --
        // and a player who reads "Set off. Draw 1 card." top to bottom is
        // reading the order the method runs in. Twin:
        // `test_countdown_sets_off_the_whole_pile_and_then_draws`.
        var play = Il.CallSequence(Il.Method("ProtoKoCountdown", "OnPlay"))
            .ToList();
        var setOff = play.FindIndex(c => c.Contains("ProtoBombPower.SetOffAimed"));
        var draw = play.FindIndex(c => c.Contains("CardPileCmd.Draw"));

        Assert.True(setOff >= 0, "the row detonates");
        Assert.True(draw >= 0, "the row draws");
        Assert.True(setOff < draw, "the Bombs go off before the card is drawn");
    }

    [Fact]
    public void Countdown_is_priced_in_energy_and_asks_no_spark()
    {
        // THE WHOLE POINT OF THE ROW. Every other plain detonator in the pool
        // declares `ISparkPricedCard` (Fwoosh!, Quick Fuse, Tinder Toss), so a
        // seat at 0 Spark cannot play one; this one is priced in the resource
        // a turn always has. A Spark price arriving here later would silently
        // undo the finding it was written for, so its ABSENCE is the pin.
        var card = new ProtoKoCountdown();

        Assert.False(typeof(ISparkPricedCard)
                         .IsAssignableFrom(typeof(ProtoKoCountdown)));
        Assert.True(typeof(ISparkPricedCard)
                        .IsAssignableFrom(typeof(ProtoKoFwoosh)),
                    "the comparison is only worth making if the twin has one");
        Assert.Equal(CardRarity.Common, card.Rarity);
    }

    [Fact]
    public void Countdown_is_unconditional_on_both_clauses()
    {
        // NOT `EB-261`'s gate, and that is deliberate: a Set off that carries
        // a second clause pays on a Bomb-less board, so this row is a playable
        // cantrip rather than a card that eats a turn. Nothing in the play
        // reads a counter, a condition or the Spark meter.
        var play = Il.Calls(Il.Method("ProtoKoCountdown", "OnPlay"));

        Assert.DoesNotContain(play, c => c.Contains("SparkPower"));
        Assert.DoesNotContain(play, c => c.Contains("Reacted"));
        Assert.DoesNotContain(play, c => c.Contains("WentOff"));
        Assert.DoesNotContain(play, c => c.Contains("IsPlayable"));
    }

    [Fact]
    public void Countdown_prints_its_draw_and_the_smith_moves_it()
    {
        // The row's ONE printed number is its draw, so the face prints it as a
        // var and `OnUpgrade` moves that same var -- or the `+` card is the
        // base card back out of the smith (`EB-277` / `EB-283`).
        var card = new ProtoKoCountdown();

        Assert.Contains("{Cards:diff()}", Face(card));
        Assert.Equal(1m, Vars(card).Single().BaseValue);
        Assert.Contains(Il.Calls(Il.Method("ProtoKoCountdown", "OnUpgrade")),
                        c => c.Contains("UpgradeValueBy"));
    }

    [Fact]
    public void Countdown_is_offered_by_the_arm_and_is_not_in_the_starter()
    {
        // `lint_arm_pool_parity` is the gate that holds this list to the sheet
        // and to `C.KLEE_OVERHAUL_POOL_IDS`; what a pin adds is that the row
        // the finding asked for is actually on the OFFER seam, which is the
        // seam R252 forgot.
        var slice = Il.CallSequence(Il.Method("KleeOverhaulRoster", "Slice"));
        Assert.Contains(slice, c => c.Contains("ProtoKoCountdown"));

        var starter = Il.CallSequence(
            Il.Method("KleeOverhaulRoster", "StartingDeck"));
        Assert.DoesNotContain(starter, c => c.Contains("ProtoKoCountdown"));
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
