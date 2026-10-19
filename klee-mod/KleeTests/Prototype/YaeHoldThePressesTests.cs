#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// HOLD THE PRESSES, REDESIGNED (2026-10-19, <c>review/active/pool-sweep-
/// 2026-10-18.md</c> sec.3; [USER]: "we already have an enchantment that gives
/// Retain and doing it for one turn is strictly worse. The card probably
/// needs a redesign."). "Gain 8 [11] Block. Draw 1 card for each Annotated
/// card in your Hand, up to 2." at 1 Energy; the Retain and its door are
/// gone. The count is the hand at resolution, the card itself not in it.
/// Pure reads and call-graph pins, as every Yae pin is. Sim twin:
/// <c>tier0/tests/test_yae_pool_to_78.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeHoldThePressesTests : IDisposable
{
    public YaeHoldThePressesTests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose() => YaeShrineLedger.ResetAll();

    private const BindingFlags Instance = BindingFlags.Instance | BindingFlags.NonPublic;

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static List<string> OnPlay<T>() =>
        Il.CallSequence(typeof(T).GetMethod("OnPlay", Instance)!).ToList();

    private static List<CardModel> Hand(Seat seat) =>
        (List<CardModel>)typeof(CardPile)
            .GetField("_cards", HeadlessGame.All)!
            .GetValue(PileType.Hand.GetPile(seat.Player)!)!;

    [Fact]
    public void Hold_the_presses_is_one_energy_block_and_a_capped_draw()
    {
        var card = new ProtoYmHoldThePresses();
        Assert.Equal("Gain {Block:diff()} [gold]Block[/gold]. Draw 1 card for each "
                     + "[gold]Annotated[/gold] card in your [gold]Hand[/gold], up to "
                     + "{YmAmount:diff()}.", Face(card));
        Assert.Equal(1, (int)card.EnergyCost.Canonical);
        Assert.Equal(8, (int)card.DynamicVars.Block.BaseValue);
        Assert.Equal(2, (int)card.DynamicVars["YmAmount"].BaseValue);
        var up = Upgraded<ProtoYmHoldThePresses>();
        Assert.Equal(11, (int)up.DynamicVars.Block.BaseValue);
        Assert.Equal(2, (int)up.DynamicVars["YmAmount"].BaseValue);
        Assert.Equal(1, (int)up.EnergyCost.Canonical);
    }

    [Fact]
    public void It_draws_through_the_annotated_count_and_retains_nothing()
    {
        var calls = OnPlay<ProtoYmHoldThePresses>();
        Assert.Contains(calls, c => c.Contains(nameof(YaeCards.DrawPerAnnotated)));
        Assert.DoesNotContain(calls, c => c.Contains("RetainHand"));
        Assert.Null(typeof(YaeCards).GetMethod("RetainHand"));

        var door = Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.AnnotatedDraw))!).ToList();
        Assert.Contains(door, c => c.Contains(nameof(YaeEditing.IsAnnotated)));
        Assert.Contains(door, c => c.Contains("Min"));
        var draw = Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.DrawPerAnnotated))!).ToList();
        Assert.Contains(draw, c => c.Contains(nameof(YaeCards.AnnotatedDraw)));
        Assert.Contains(draw, c => c.Contains("CardPileCmd.Draw"));
    }

    [Fact]
    public void An_unannotated_hand_draws_nothing()
    {
        var seat = Seat.Yae().WithCombatState();
        var card = new ProtoYmHoldThePresses();
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", seat.Player);
        var hand = Hand(seat);
        hand.Add(card);
        hand.Add(new ProtoYmHoldThePresses());
        hand.Add(new ProtoYmHoldThePresses());
        Assert.Equal(0, YaeCards.AnnotatedDraw(card));
    }
}
