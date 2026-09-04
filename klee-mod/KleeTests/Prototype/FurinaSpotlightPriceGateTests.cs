using System;
using BaseLib.Abstracts;
using KleeMod.Cards.Furina;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-364`. ETHEREAL SPOTLIGHT REFUSES SHORT OF ITS OWN PRICE.
///
/// WHAT THE SEAT SAW (Furina reframe round 1, fight 2 round 1): the card
/// prints "Costs 2 Encore" under the arm, the seat played it at 0 Encore, and
/// nothing happened -- no refusal, no Guest Cast, no line on the page. It found
/// out two turns later that its Companions had never been empowered.
///
/// WHY THE GATE WAS MISSING, which is the finding rather than the fix: this is
/// a 0-ENERGY token whose Encore price is charged INSIDE the op rather than
/// declared as a resource cost, so `CustomResourceCost.ResourceCheck` -- the
/// gate every other Encore-priced Furina card is refused by -- had nothing to
/// read. `DesignateOneMode`'s "unpaid is a no-op" then turned the whole play
/// into an Ethereal card exhausting for nothing.
///
/// The predicate is `SpotlightSystem.DesignateOneModeIsUnpayable`, and it is
/// the designation's OWN refusal asked one phase early, so the gate and the
/// payment cannot disagree.
/// </summary>
public class FurinaSpotlightPriceGateTests
{
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _spotlight = FurinaReframe.SpotlightEnabled;

        internal Arm(bool master = true, bool spotlight = true)
        {
            FurinaReframe.Enabled = master;
            FurinaReframe.SpotlightEnabled = spotlight;
        }

        public void Dispose()
        {
            FurinaReframe.Enabled = _enabled;
            FurinaReframe.SpotlightEnabled = _spotlight;
        }
    }

    /// <summary>An Ethereal Spotlight this seat owns. `CustomCardModel`'s own
    /// constructor is used -- the card is registered with BaseLib either way,
    /// and the gate reads `Owner`, which only a real instance carries.</summary>
    private static CardModel Card(Seat seat)
    {
        var card = new EtherealSpotlight();
        Seat.Force(card, "IsMutable", true);
        Seat.Force(card, "Owner", seat.Player);
        return card;
    }

    private static bool Playable(CardModel card) =>
        (bool)typeof(CardModel)
            .GetProperty("IsPlayable", HeadlessGame.All)!
            .GetValue(card)!;

    // ==================================================================
    // 1. THE REFUSAL
    // ==================================================================

    [Fact]
    public void At_zero_encore_the_card_is_unplayable_under_the_arm()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();

        Assert.Equal(0, FurinaResources.Encore(seat.Creature));
        Assert.False(Playable(Card(seat)));
    }

    [Fact]
    public void At_the_price_the_card_is_playable_again()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        FurinaResources.GainEncore(
            seat.Creature, FurinaReframeLaw.SpotlightDesignateEncoreCost);

        Assert.True(Playable(Card(seat)));
    }

    [Fact]
    public void One_short_of_the_price_still_refuses()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        FurinaResources.GainEncore(
            seat.Creature, FurinaReframeLaw.SpotlightDesignateEncoreCost - 1);

        Assert.False(Playable(Card(seat)));
    }

    [Fact]
    public void The_shipped_selector_charges_nothing_and_refuses_nothing()
    {
        // The acceptance condition: with the arm off the card opens the
        // choose-a-card screen and takes no Encore, so an empty buffer is not a
        // refusal and this gate must be invisible.
        using var _ = new Arm(master: false, spotlight: false);
        var seat = Seat.Furina().WithCombatState();

        Assert.True(Playable(Card(seat)));
    }

    // ==================================================================
    // 2. THE SENTENCE THE PAGE PRINTS
    // ==================================================================

    [Fact]
    public void The_refusal_says_the_bank_and_the_price()
    {
        // `EB-264`: `CardModel.CanPlay` collapses every mod-side refusal into
        // `BlockedByCardLogic`, which names no reason, and the blind render
        // prints that flag verbatim. The sentence rides beside it as
        // `unplayable_reason_text`, through `KleeUnplayableReason.For`.
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        var card = Card(seat);
        var price = FurinaReframeLaw.SpotlightDesignateEncoreCost;

        var empty = KleeUnplayableReason.For(card);
        Assert.Equal($"you have no Encore, and this costs {price}", empty);

        FurinaResources.GainEncore(seat.Creature, 1);
        Assert.Equal($"you have 1 Encore, and this costs {price}",
                     KleeUnplayableReason.For(card));

        FurinaResources.GainEncore(seat.Creature, price);
        Assert.Null(KleeUnplayableReason.For(card));
    }

    // ==================================================================
    // 3. THE CASES THAT ARE NOT REFUSALS
    // ==================================================================

    [Fact]
    public void A_second_copy_while_the_spotlight_holds_is_refused()
    {
        // `EB-406`. THIS TEST USED TO ASSERT THE OPPOSITE, and the reading it
        // rested on does not survive the arm. "Re-aiming at the same target
        // bills nothing, so it cannot be refused for being unpayable" is true
        // of the price gate and was read as "so the play is fine" -- but R228
        // (1) retires Center Stage, so Guest Cast is the ONLY target and there
        // is no re-aim to make. `DesignateOneMode` answers the second copy
        // with `NoteDesignationRedundant()` and a bare return, and the card is
        // `Ethereal` + `Exhaust` with a relic putting a fresh one in hand
        // every turn.
        //
        // The Furina round-4 seat played exactly that: refused one turn at 0
        // Encore ("you have no Encore, and this costs 2"), accepted the next
        // at the same 0 Encore, Exhausting with no effect -- no Encore moved,
        // Guest Cast stayed 1.
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        CustomResources<SpotlightModeResource>
            .Get(seat.Player.PlayerCombatState).Amount =
                (int)SpotlightMode.GuestCast;

        Assert.False(Playable(Card(seat)));
        // ...and the reason is the redundancy, NOT the price, whatever the
        // buffer holds: banking Encore is not the way out of this one.
        Assert.Equal("the Spotlight is already on your Companion cards",
                     KleeUnplayableReason.For(Card(seat)));
        FurinaResources.GainEncore(
            seat.Creature, FurinaReframeLaw.SpotlightDesignateEncoreCost);
        Assert.False(Playable(Card(seat)));
        Assert.Equal("the Spotlight is already on your Companion cards",
                     KleeUnplayableReason.For(Card(seat)));
    }

    [Fact]
    public void The_first_copy_is_still_playable_at_the_price()
    {
        // The other direction, so the refusal above cannot pass by refusing
        // the card outright: with no Spotlight out and the price banked, the
        // selector plays.
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        FurinaResources.GainEncore(
            seat.Creature, FurinaReframeLaw.SpotlightDesignateEncoreCost);

        Assert.NotEqual((int)SpotlightMode.GuestCast,
                        CustomResources<SpotlightModeResource>
                            .Get(seat.Player.PlayerCombatState).Amount);
        Assert.True(Playable(Card(seat)));
        Assert.Null(KleeUnplayableReason.For(Card(seat)));
    }

    [Fact]
    public void With_the_arm_off_a_second_copy_is_not_refused()
    {
        // The quarantine. Off the arm the selector has two modes and a second
        // play RE-AIMS, so nothing here may refuse it -- and the relic's face
        // does not carry the arm's sentence either.
        using var _ = new Arm(master: false, spotlight: false);
        var seat = Seat.Furina().WithCombatState();
        CustomResources<SpotlightModeResource>
            .Get(seat.Player.PlayerCombatState).Amount =
                (int)SpotlightMode.GuestCast;

        Assert.False(SpotlightSystem.DesignateOneModeIsRedundant(
            seat.Creature));
        Assert.True(Playable(Card(seat)));
        Assert.Null(KleeUnplayableReason.For(Card(seat)));
    }

    [Fact]
    public void An_ownerless_copy_is_refused_by_nothing()
    {
        // The compendium renders cards nobody owns, and the gate runs on every
        // card in hand on every state poll: no owner and no combat both answer
        // "not unpayable" rather than throwing.
        using var _ = new Arm();

        Assert.False(SpotlightSystem.DesignateOneModeIsUnpayable(null));
        Assert.False(SpotlightSystem.DesignateOneModeIsRedundant(null));
        Assert.True(Playable(new EtherealSpotlight()));
    }
}
