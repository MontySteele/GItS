using System;
using KleeMod.Cards.Furina;
using KleeMod.Cards.Furina.Generated;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-505`. THE REFUSAL THAT NAMED THE WRONG RESOURCE.
///
/// WHAT THE SEAT READ (Furina r11 lane 1, (c) 3). "With energy 3/3 and the
/// card costing 1, the face read <c>CANNOT BE PLAYED: you do not have enough
/// energy</c>. The actual shortfall was Encore (2 held, 3 required) ... I
/// spent a genuine beat re-reading my energy bar trying to work out what I had
/// miscounted." Second Course, three times, in the run's first fight.
///
/// WHY THE PAGE SAID ENERGY. An <c>encore_cost</c> is a BaseLib CUSTOM
/// RESOURCE COST, so <c>CardModel.CanPlay</c> reports a cost failure and
/// <c>understudy/qa_packet.UNPLAYABLE_REASONS</c> renders that enum as "you do
/// not have enough energy" -- true of the enum and false of the board.
///
/// AND THE SEAT FOUND THE FIX ITSELF: "Ethereal Spotlight in the same position
/// printed the correct thing -- <c>you have 1 Encore, and this costs 2</c> --
/// so the right message exists and Second Course is not using it." That
/// sentence was written by hand on one card; it is
/// <see cref="KleeUnplayableReason.EncoreSentence"/> now, and both callers
/// reach it.
///
/// THE HEADLESS BOUNDARY IS WHY THE PRICE IS READ OFF A CANONICAL COPY.
/// `MeterCost.PriceIn` resolves through `CustomResourceCost.GetResolved`,
/// which walks the card's PILE for its combat state -- and this harness puts
/// no card in a pile (the same split `FurinaReframeSliceTwoTests` states at
/// its own Evoke price test: price off a canonical copy, affordability off the
/// held one). So the numbers are asserted where they can be read, the
/// SENTENCE is asserted on the function that writes it, and the WIRING is
/// asserted structurally.
/// </summary>
public class FurinaEncoreRefusalTests
{
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _spotlight = FurinaReframe.SpotlightEnabled;

        internal Arm()
        {
            FurinaReframe.Enabled = true;
            FurinaReframe.SpotlightEnabled = true;
        }

        public void Dispose()
        {
            FurinaReframe.Enabled = _enabled;
            FurinaReframe.SpotlightEnabled = _spotlight;
        }
    }

    private static CardModel Owned(CardModel card, Seat seat)
    {
        Seat.Force(card, "IsMutable", true);
        Seat.Force(card, "Owner", seat.Player);
        return card;
    }

    [Fact]
    public void Second_course_on_an_empty_buffer_names_encore_and_the_price()
    {
        // The row's own test, at the seat's own numbers. `EB-552` took the
        // printed price from 3 to 1, so the shortfall this row can still show a
        // player is the empty buffer -- which is the one every fight opens
        // three turns of Encore decay away from.
        var seat = Seat.Furina().WithCombatState();

        int price = MeterCost.Priced(new ProtoFrSecondCourse())!.Value.Amount;
        int bank = MeterCost.BankOf(seat.Creature, Meter.Encore);

        Assert.Equal(1, price);
        Assert.Equal(0, bank);
        Assert.Equal("you have no Encore, and this costs 1",
                     KleeUnplayableReason.EncoreSentence(bank, price));
    }

    [Fact]
    public void An_empty_buffer_reads_the_way_the_spotlight_reads()
    {
        // Not "the same words as" -- the SAME FUNCTION, which is what stops
        // the two from drifting apart again. `EtherealSpotlight` is driven
        // through its own gate here, exactly as its price-gate pin drives it.
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        var spotlight = Owned(new EtherealSpotlight(), seat);
        int spotlightPrice = FurinaReframeLaw.SpotlightDesignateEncoreCost;

        Assert.Equal($"you have no Encore, and this costs {spotlightPrice}",
                     KleeUnplayableReason.For(spotlight));
        Assert.Equal($"you have no Encore, and this costs {spotlightPrice}",
                     KleeUnplayableReason.EncoreSentence(0, spotlightPrice));
        Assert.Equal("you have no Encore, and this costs 3",
                     KleeUnplayableReason.EncoreSentence(0, 3));
    }

    [Fact]
    public void The_bank_covering_the_price_is_no_sentence_at_all()
    {
        // A refusal that fired on an affordable card would put a shortfall on
        // the face of every Encore-priced card in the deck.
        var seat = Seat.Furina().WithCombatState();
        FurinaResources.GainEncore(seat.Creature, 3);
        var card = Owned(new ProtoFrSecondCourse(), seat);

        Assert.Equal(3, MeterCost.BankOf(seat.Creature, Meter.Encore));
        Assert.Null(KleeUnplayableReason.EncoreShortfall(card));
    }

    [Fact]
    public void The_refusal_is_routed_for_every_row_with_the_field()
    {
        // "For every card with the field" is the row's wording, and this is
        // the pin for it: the sentence is reached from `For` through one call
        // that asks the CARD for its Encore price rather than from a property
        // written per card. A row that acquires an `encore_cost` tomorrow gets
        // the refusal without anybody remembering.
        var calls = Il.Calls(Il.Method("KleeUnplayableReason", "For"));
        Assert.Contains("KleeUnplayableReason.EncoreShortfall", calls);

        var shortfall = Il.Calls(
            Il.Method("KleeUnplayableReason", "EncoreShortfall"));
        Assert.Contains("MeterCost.PriceIn", shortfall);
        Assert.Contains("MeterCost.BankOf", shortfall);
        Assert.Contains("KleeUnplayableReason.EncoreSentence", shortfall);

        // And the Spotlight's hand-written copy is gone: it calls the shared
        // sentence, so a rewording moves both surfaces at once.
        Assert.Contains("KleeUnplayableReason.EncoreSentence",
                        Il.Calls(Il.Method("EtherealSpotlight",
                                           "get_UnplayableReason")));
    }

    [Fact]
    public void A_card_that_charges_no_encore_is_left_alone()
    {
        // The gate is as wide as the field and no wider: a row with no
        // `encore_cost` must not acquire a sentence about a meter it never
        // asks for. `DressRehearsal` is a shipped Furina row that DOES charge
        // one, and it is here as the denominator. (The unpriced row was Rolling
        // Tide until `EB-552` withdrew it; Guest List is the same shape -- an
        // arm Common on the pool pass with no `encore_cost` field at all.)
        Assert.Equal(0, MeterCost.PriceIn(new ProtoFrGuestList(),
                                          Meter.Encore));
        Assert.Equal(2, MeterCost.PriceIn(new DressRehearsal(), Meter.Encore));

        var seat = Seat.Furina().WithCombatState();
        Assert.Null(KleeUnplayableReason.EncoreShortfall(
            Owned(new ProtoFrGuestList(), seat)));
    }
}
