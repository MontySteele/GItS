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
/// (review/ruled/klee-sparks-2026-08-29.md sec.6.4 / PICK 8 option 2). The
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
/// `EB-445`. THE ONE SPARK PRICE THAT IS NOT THE NUMBER IT GATES ON.
///
/// "Spend all your Sparks" -- the X price, tier0's <c>effects.SPEND_ALL</c> --
/// charges the WHOLE BANK and gates on ONE, because an empty bank cannot pay
/// and any bank holding a Spark can. <see cref="ISparkPricedCard.PrintedSparkPrice"/>
/// is therefore 1 on such a card, which is right for the gate and wrong for
/// the cost slot: Stoke the Fuse's badge printed `1` beside a face reading
/// "Spend all your remaining Sparks", so the one surface a player reads a
/// price off named a number the card does not charge.
///
/// A MARKER AND NOT A SECOND NUMBER, deliberately. There is no number to
/// declare -- the amount is the bank at play time -- so the only thing the
/// card can tell a reader is WHICH KIND of price it prints, and every reader
/// that wants the figure still goes through <see cref="SparkCost.PriceOf"/>
/// and gets the gate. The badge answers this question and draws the base
/// game's own X instead (`MeterCostBadge`), the grammar Regent's Star cards
/// already use for a whole-bank cost.
///
/// EMITTED BY THE CODEGEN off the same `spend_spark` effect that emits
/// <see cref="ISparkPricedCard"/> (`gen_klee_cards`, the interface list), so
/// a row that prints the X price cannot arrive without it.
/// </summary>
public interface ISparkXPricedCard
{
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
    /// Does this card print the X price -- "spend all your Sparks" (`EB-445`)?
    ///
    /// The number <see cref="PriceOf"/> answers for such a card is its GATE
    /// (1), never what it charges, so the cost slot says X rather than that
    /// number. See <see cref="ISparkXPricedCard"/>.
    /// </summary>
    public static bool PricesWholeBank(CardModel card) =>
        card is ISparkXPricedCard;

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
