using System;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// The three spendable meters a card in this mod can price. The names are the
/// PRINTED names -- <c>ToString()</c> is what a refusal line says ("needs 3
/// Encore, bank holds 2"), which is why <see cref="Sparks"/> is plural and the
/// other two are not.
/// </summary>
public enum Meter
{
    Sparks,
    Encore,
    Charge,
}

/// <summary>One meter and one amount: what a card, or one mode of a card,
/// charges right now.</summary>
public readonly struct MeterPrice
{
    public MeterPrice(Meter meter, int amount)
    {
        Meter = meter;
        Amount = amount;
    }

    public Meter Meter { get; }

    public int Amount { get; }
}

/// <summary>
/// A card face that PRINTS a meter price it does not carry as a game-side
/// resource cost. Two kinds of face declare it:
///
///   * a whole card whose row prints a TOP-LEVEL <c>spend_charge</c> (the
///     Charge cost line, R213 E1), and
///   * a MODE face on the choose-a-card screen, which declares nothing of its
///     own -- it reads the owning card's <c>ModePrices</c> table, the same one
///     the screen filter and the playability gate read (EB-182).
///
/// Sparks are the exception and deliberately so: they are a PowerModel, not a
/// resource, and their price is already state-aware through
/// <see cref="SparkCost"/> (the strict Rare Power adds to it). Encore is the
/// other exception, in the other direction: an <c>encore_cost</c> IS a BaseLib
/// resource cost, so the number is already on the card and
/// <see cref="MeterCost"/> reads it there rather than asking for a second
/// declaration.
/// </summary>
public interface IMeterPricedCard
{
    Meter PricedMeter { get; }

    int PrintedMeterPrice { get; }
}

/// <summary>
/// ONE NUMBER PER METER, and the whole point of this class is that the display
/// cannot invent a second one.
///
/// <c>EB-220</c> generalises what <see cref="SparkCost"/> did for Sparks. The
/// Spark cost badge was built (PICK 8 option 2,
/// review/ruled/klee-sparks-2026-08-29.md sec.6.4) on a single rule: the badge
/// renders the exact expression the playability gate charges, so a price a
/// player reads off a card face cannot drift from the price the engine takes.
/// [USER] then asked for the same badge on Encore and Charge, so the READ has
/// to be the same shape for all three -- one lookup that answers "what does
/// this card charge, in which meter, right now", with each arm pointing at the
/// number its own gate already consults:
///
///   * SPARKS  -- <see cref="SparkCost.PriceOf"/>, printed plus power, the
///     generated <c>IsPlayable</c>'s own expression.
///   * ENCORE  -- BaseLib's resolved resource cost, which is what
///     <c>CustomResourceCost.ResourceCheck</c> gates on and what
///     <c>FurinaResourceHooks.BeforeCardPlayed</c> spends.
///   * CHARGE  -- the printed price on <see cref="IMeterPricedCard"/>, read
///     back by the generated <c>KokomiResources.CanSpendCharge</c> gate.
///
/// WHAT IS NOT HERE, and each absence is a decision:
///
///   * FANFARE is a fourth custom resource with a <c>fanfare_cost</c> field and
///     no badge. [USER] named Encore and Charge; a Fanfare badge is a design
///     word nobody has given.
///   * A TOP-LEVEL <c>spend_encore</c> (the OVERDRAW primitive: pay Encore,
///     pay the shortfall in true HP) is NOT a price here. Nothing gates on it
///     -- the card is playable at an empty bank, by design -- so rendering it
///     in the cost slot would announce an admission fee the game does not
///     charge, and reddening it would be a lie. Those rows keep their rules
///     text.
/// </summary>
public static class MeterCost
{
    /// <summary>
    /// What this card charges right now, or null for the overwhelming majority
    /// of cards, which charge no meter at all.
    ///
    /// The arms are mutually exclusive by construction: codegen refuses a row
    /// that emits two resource cost lines ("two resource cost lines on one card
    /// -- only one IsPlayable override can be emitted"), so the order below
    /// resolves nothing and exists only to be read top to bottom.
    /// </summary>
    public static MeterPrice? Priced(CardModel card)
    {
        int sparks = SparkCost.PriceOf(card);
        if (sparks > 0)
        {
            return new MeterPrice(Meter.Sparks, sparks);
        }

        if (card is IMeterPricedCard priced && priced.PrintedMeterPrice > 0)
        {
            return new MeterPrice(priced.PricedMeter, priced.PrintedMeterPrice);
        }

        int encore = EncoreCostOf(card);
        return encore > 0 ? new MeterPrice(Meter.Encore, encore) : null;
    }

    /// <summary>
    /// This card's price IN ONE NAMED METER, 0 when it charges another meter or
    /// none. The generated Charge gate reads its own price back through here,
    /// so the gate and the badge share the single declaration on the card.
    ///
    /// A DISTINCT NAME rather than an overload of <see cref="Priced"/>: the
    /// structural pins reach a method by name through <c>Type.GetMethod</c>,
    /// which is ambiguous across an overload pair (the same argument EB-182
    /// made for <c>SelectAffordableMode</c>).
    /// </summary>
    public static int PriceIn(CardModel card, Meter meter) =>
        Priced(card) is { } price && price.Meter == meter ? price.Amount : 0;

    /// <summary>
    /// The bank, one accessor per meter, and each is the SAME read the paying
    /// call gates on: <c>SparkPower.CanSpend</c> reads
    /// <c>SparksAsResolved</c>, the Encore spend reads the resource's Amount,
    /// and <c>KokomiResources.CanSpendCharge</c> reads <c>GetCharge</c>.
    ///
    /// A null creature is 0 rather than a throw: the compendium renders cards
    /// nobody owns, and a card nobody owns can afford nothing.
    /// </summary>
    public static int BankOf(Creature? creature, Meter meter)
    {
        if (creature == null)
        {
            return 0;
        }

        return meter switch
        {
            Meter.Sparks => SparkPower.SparksAsResolved(creature),
            Meter.Encore => FurinaResources.Encore(creature),
            Meter.Charge => KokomiResources.GetCharge(creature),
            _ => 0,
        };
    }

    /// <summary>
    /// Can this card's owner pay <paramref name="price"/> right now? A priced
    /// card with no readable owner is NOT affordable -- the compendium's
    /// canonical copy has no bank behind it, and reading it as affordable would
    /// paint the badge in the playable colour on a card nobody holds.
    /// </summary>
    public static bool Affordable(CardModel card, MeterPrice price) =>
        price.Amount <= 0
        || BankOf(SparkCost.OwnerCreatureOf(card), price.Meter) >= price.Amount;

    /// <summary>
    /// Furina's <c>encore_cost</c>, resolved -- upgrades and cost modifiers
    /// included, because <c>GetResolved</c> is the number
    /// <c>CustomResourceCost.ResourceCheck</c> refuses on and the number
    /// <c>GetAmountToSpend</c> takes.
    ///
    /// An X cost is skipped: its amount is the whole bank at play time, not a
    /// printed number, and the base game draws an X in the energy orb rather
    /// than a count. No shipped row prints one.
    /// </summary>
    private static int EncoreCostOf(CardModel card)
    {
        CustomResourceCost<EncoreResource>? cost =
            CustomResources<EncoreResource>.Cost(card);
        if (cost == null || cost.CostsX)
        {
            return 0;
        }

        return Math.Max(0, cost.GetResolved());
    }
}
