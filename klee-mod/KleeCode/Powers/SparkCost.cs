using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// A card that prints a [Spark] price. Emitted by the codegen
/// (<c>tools/gen_klee_cards.py</c>, <c>spark_gate_member</c>) onto every card
/// whose sheet row carries a TOP-LEVEL <c>spend_spark</c>, alongside the
/// <c>IsPlayable</c> override that gates on it.
///
/// WHY AN INTERFACE AND NOT A LITERAL AT EACH SITE. Until this landed the
/// printed price existed only as a number baked into the generated
/// <c>IsPlayable</c> expression, so nothing outside the card could ask what a
/// card costs -- which is exactly what the Spark cost BADGE has to ask
/// (review/active/klee-sparks-2026-08-29.md sec.6.4 / PICK 8 option 2). The
/// alternative was a second table of prices for the display to read, and a
/// price the player sees drifting from the price the gate charges is the D4
/// defect the badge exists to repair. One number, one source.
/// </summary>
public interface ISparkPricedCard
{
    /// <summary>
    /// The card's PRINTED Spark price -- the sum of its top-level
    /// <c>spend_spark</c> amounts, a literal, never moved by an upgrade (a card
    /// that pays less on upgrade is a repricing, and repricing is [USER]'s).
    /// </summary>
    int PrintedSparkPrice { get; }
}

/// <summary>
/// What a card charges in Sparks RIGHT NOW: printed plus power. The C# twin of
/// tier0 <c>combat.spark_price</c>, and it exists for the identical reason that
/// function does -- so the playability gate, the payment and the cost badge can
/// never disagree about the number.
///
/// THE PRINTED HALF is on the card and is state-free. THE POWER HALF is
/// state-aware and is behind the flag: only the strict Rare Power
/// (<c>SparkAttackCostPower</c>, quarantined in <c>Powers/Prototype/</c>) ever
/// contributes to it, so with <c>PROTOTYPE_CARDS</c> undefined
/// <see cref="PriceOf"/> IS the printed price and the shipped behaviour is
/// unchanged.
/// </summary>
public static class SparkCost
{
    /// <summary>The price the CARD prints, 0 for a card that prints none.</summary>
    public static int PrintedPriceOf(CardModel card) =>
        card is ISparkPricedCard priced ? priced.PrintedSparkPrice : 0;

    /// <summary>
    /// The price a POWER contributes, 0 in a release build. Mirrors tier0
    /// <c>combat.spark_power_price</c>, whose whole body is behind the same
    /// flag.
    /// </summary>
    public static int PowerPriceOf(CardModel card)
    {
#if PROTOTYPE_CARDS
        return SparkAttackCostPower.PriceFor(card);
#else
        return 0;
#endif
    }

    /// <summary>Printed plus power: the one number every reader consults.</summary>
    public static int PriceOf(CardModel card) =>
        PrintedPriceOf(card) + PowerPriceOf(card);

    /// <summary>
    /// The card's owning creature, or null when there is not one to read.
    ///
    /// <c>CardModel.Owner</c>'s getter calls <c>AssertMutable</c> and THROWS on
    /// a canonical model -- <c>EB-94</c>'s root cause, met again here because
    /// the badge renders in the compendium, where every card is canonical. The
    /// guard is the base game's own (<c>CardModel.AddDescriptionVars</c> writes
    /// <c>IsMutable &amp;&amp; (Owner?...)</c> for the same reason).
    /// </summary>
    public static Creature? OwnerCreatureOf(CardModel card) =>
        card.IsMutable ? card.Owner?.Creature : null;

    /// <summary>
    /// Can the card's owner pay the price right now? TRUE for a card that
    /// charges nothing, so a caller can ask this of any card. A priced card
    /// with no readable owner is NOT affordable -- the compendium's canonical
    /// copy has no bank behind it, and reading it as affordable would paint the
    /// badge in the playable colour on a card nobody holds.
    /// </summary>
    public static bool Affordable(CardModel card)
    {
        int price = PriceOf(card);
        if (price <= 0)
        {
            return true;
        }

        Creature? creature = OwnerCreatureOf(card);
        return creature != null && SparkPower.CanSpend(creature, price);
    }
}
