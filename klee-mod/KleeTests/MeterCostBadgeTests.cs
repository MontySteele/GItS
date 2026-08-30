using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Furina.Generated;
using KleeMod.Cards.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE METER COST BADGE, pinned (EB-220).
///
/// [USER], 2026-08-30: "Yes, I think Encore and Charge need badges." The badge
/// itself cannot be exercised here -- painting needs Godot nodes, which are
/// process death in this host (README, the headless boundary) -- but everything
/// the badge is FOR is a plain read off a card, and those are pinned for real:
/// what each meter charges, whether the bank can pay it, and the one structural
/// fact that keeps the display honest, namely that the badge asks the same
/// function the gate asks.
///
/// THIS FILE IS NOT UNDER `Prototype/`, unlike the Spark badge's pin was. That
/// is the change: the badge used to be quarantined because every priced face it
/// drew was a prototype row, and Encore's priced faces are shipped Furina cards.
/// </summary>
public class MeterCostBadgeTests
{
    private const BindingFlags All = HeadlessGame.All;

    /// <summary>A card in a seat's hand: mutable, owned, and therefore askable.
    /// `IsMutable` first -- Owner's setter calls AssertMutable, which is EB-94's
    /// throw met from the other side.</summary>
    private static T Held<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    // --- the badge reads the gate's own number ----------------------------

    [Fact]
    public void The_badge_renders_the_price_and_the_affordability_it_is_told()
    {
        // STRUCTURAL PIN, and the property it pins is the badge's whole reason
        // to exist: it asks MeterCost for the price and for affordability
        // rather than carrying either rule itself. A badge with its own copy of
        // a price -- the display-versus-gate drift this repairs -- would show up
        // here as the absence of these calls.
        var calls = Il.Calls(Il.Method("MeterCostBadge", "Paint"));

        Assert.Contains(calls, c => c.EndsWith("MeterCost.Priced"));
        Assert.Contains(calls, c => c.EndsWith("MeterCost.Affordable"));
    }

    [Fact]
    public void Every_meter_bank_is_the_paying_call_s_own_read()
    {
        // STRUCTURAL PIN. One reader per meter, and each one is the accessor
        // the matching payment gates on: SparkPower.CanSpend reads
        // SparksAsResolved, the Encore spend reads the resource Amount through
        // FurinaResources.Encore, and KokomiResources.CanSpendCharge reads
        // GetCharge. A fourth read appearing here, or one of these being
        // swapped for a raw field, is the drift this pin catches.
        var calls = Il.Calls(Il.Method("MeterCost", "BankOf"));

        Assert.Contains(calls, c => c.EndsWith("SparkPower.SparksAsResolved"));
        Assert.Contains(calls, c => c.EndsWith("FurinaResources.Encore"));
        Assert.Contains(calls, c => c.EndsWith("KokomiResources.GetCharge"));
    }

    // --- Sparks, unchanged by the generalisation --------------------------

    [Fact]
    public void A_spark_priced_card_still_reads_as_sparks()
    {
        // powder_charge is a SHIPPED Klee row printing `Spend 2`. It declared
        // ISparkPricedCard before EB-220 and still does: the generalisation
        // added meters, it did not re-home Sparks.
        var price = MeterCost.Priced(new PowderCharge());

        Assert.NotNull(price);
        Assert.Equal(Meter.Sparks, price!.Value.Meter);
        Assert.Equal(2, price.Value.Amount);
        Assert.Equal(2, MeterCost.PriceIn(new PowderCharge(), Meter.Sparks));
        Assert.Equal(0, MeterCost.PriceIn(new PowderCharge(), Meter.Encore));
    }

    // --- Encore: the top-level cost line ----------------------------------

    [Fact]
    public void An_encore_cost_row_prices_in_encore()
    {
        // ebb_and_flow (1) and dress_rehearsal (2) are the two shipped rows
        // with an `encore_cost`. Neither declares an interface: the number is
        // BaseLib's resolved resource cost, which is what the game's own
        // playability check refuses on and what FurinaResourceHooks spends. The
        // badge reads it there rather than asking the sheet for a second copy.
        var ebb = MeterCost.Priced(new EbbAndFlow());
        var rehearsal = MeterCost.Priced(new DressRehearsal());

        Assert.Equal(Meter.Encore, ebb!.Value.Meter);
        Assert.Equal(1, ebb.Value.Amount);
        Assert.Equal(Meter.Encore, rehearsal!.Value.Meter);
        Assert.Equal(2, rehearsal.Value.Amount);
    }

    [Fact]
    public void An_upgraded_encore_cost_is_the_number_the_badge_shows()
    {
        // The resolved cost, not the printed one: a badge that showed the
        // canonical price on an upgraded card would be lying in the one place
        // the player is deciding. `GetResolved` is also what ResourceCheck
        // refuses on, so the two cannot disagree.
        var card = new DressRehearsal();
        Seat.Set(card, "IsMutable", true);
        BaseLib.Abstracts.CustomResources<EncoreResource>.Cost(card)!
            .UpgradeCostBy(-1);

        Assert.Equal(1, MeterCost.Priced(card)!.Value.Amount);
    }

    // --- Encore: a MODE's cost line ---------------------------------------

    [Fact]
    public void A_priced_mode_face_carries_the_card_s_own_row()
    {
        // EB-182 declared the per-mode prices; EB-220 makes the FACE read that
        // declaration instead of repeating the number. This is the pin that
        // says so: the face's price is the table's entry, by identity, so a
        // sheet edit that moves one moves both.
        var table = (ModePrice?[])typeof(DeepBreath)
            .GetField("ModePrices", All)!
            .GetValue(null)!;

        var face = new DeepBreathModeB();

        Assert.Equal(table[1]!.Value.Meter, face.PricedMeter);
        Assert.Equal(table[1]!.Value.Amount, face.PrintedMeterPrice);
        Assert.Equal(Meter.Encore, face.PricedMeter);
        Assert.Equal(3, face.PrintedMeterPrice);
    }

    [Fact]
    public void An_unpriced_mode_face_carries_no_price_at_all()
    {
        // Mode 0 of deep_breath GAINS Encore. A face that declared a price of 0
        // would badge nothing, but it would also claim a cost line it does not
        // have; it declares no interface instead.
        Assert.IsNotAssignableFrom<IMeterPricedCard>(new DeepBreathModeA());
        Assert.Null(MeterCost.Priced(new DeepBreathModeA()));
    }

    [Fact]
    public void The_card_itself_is_not_badged_for_its_modes_prices()
    {
        // deep_breath's price belongs to ONE of its modes, and the card face
        // is not the surface that mode is chosen on. Badging the card would
        // announce a fee its first mode does not charge.
        Assert.Null(MeterCost.Priced(new DeepBreath()));
    }

    // --- affordability, per meter -----------------------------------------

    [Fact]
    public void Affordability_is_the_owner_s_bank_in_that_meter()
    {
        var seat = Seat.Furina().WithCombatState();
        var face = Held<DeepBreathModeB>(seat);
        var price = MeterCost.Priced(face)!.Value;

        Assert.False(MeterCost.Affordable(face, price));

        FurinaResources.GainEncore(seat.Creature, 2);
        Assert.False(MeterCost.Affordable(face, price));

        FurinaResources.GainEncore(seat.Creature, 1);
        Assert.True(MeterCost.Affordable(face, price));
    }

    [Fact]
    public void The_charge_bank_is_read_for_a_charge_price()
    {
        // No SHIPPED row prices Charge -- the Charge cost line is quarantined
        // on the prototype surface (its own pin lives in
        // Prototype/SparkAlternativeCostPinTests). What ships is the READ, and
        // this is it: the badge's bank for Meter.Charge is Kokomi's counter.
        var seat = Seat.Kokomi().WithCombatState();

        Assert.Equal(0, MeterCost.BankOf(seat.Creature, Meter.Charge));
        KokomiResources.GainCharge(seat.Creature, 6);
        Assert.Equal(6, MeterCost.BankOf(seat.Creature, Meter.Charge));
        Assert.Equal(
            KokomiResources.GetCharge(seat.Creature),
            MeterCost.BankOf(seat.Creature, Meter.Charge));
    }

    [Fact]
    public void A_card_nobody_owns_can_afford_nothing()
    {
        // The compendium renders canonical copies with no bank behind them.
        // Reading one as affordable would paint the playable colour on a card
        // no seat holds.
        var face = new DeepBreathModeB();
        var price = MeterCost.Priced(face)!.Value;

        Assert.False(MeterCost.Affordable(face, price));
    }

    // --- what is NOT badged, and each is a decision -----------------------

    [Fact]
    public void A_card_that_charges_no_meter_is_left_alone()
    {
        Assert.Null(MeterCost.Priced(new Kaboom()));
    }

    [Fact]
    public void The_overdraw_primitive_is_not_a_price()
    {
        // graceful_retreat and its kin print a TOP-LEVEL `spend_encore`: the
        // OVERDRAW primitive, which pays the shortfall in true HP and gates on
        // nothing. The card is playable at an empty bank by design, so putting
        // it in the cost slot would announce an admission fee the game does not
        // charge -- and reddening it would be a lie. Those rows keep their
        // rules text until [USER] rules otherwise.
        Assert.Null(MeterCost.Priced(new GracefulRetreat()));
        Assert.IsNotAssignableFrom<IMeterPricedCard>(new GracefulRetreat());
    }
}
