using System;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// A card that can say, in words a player can read, why it is refusing.
///
/// The game's own answer is an enum. <c>CardModel.CanPlay</c> collapses every
/// mod-side refusal into a single flag, <c>UnplayableReason.BlockedByCardLogic</c>
/// ("the card itself has a built-in reason"), and there is no slot on it for
/// what that reason WAS. The blind render prints the flag verbatim, so the
/// tester's screen read <c>CANNOT BE PLAYED: BlockedByCardLogic</c> for a
/// Spark-priced card with an empty bank -- a token that "tells a player
/// nothing, and the actual reason (you have no Spark) is printed nowhere"
/// (`klee-overhaul-r1-opus`, <c>EB-264</c>).
///
/// So the refusal carries its own sentence alongside the enum. A generated
/// card whose <c>IsPlayable</c> gate is anything other than a printed price
/// implements this and says what its gate is about; the price gate itself is
/// answered centrally by <see cref="KleeUnplayableReason"/>, because the price
/// is not on the card at all under the strict Rare Power.
/// </summary>
public interface IUnplayableReasonCard
{
    /// <summary>Why this card's own gate is refusing, or null when it is not.
    /// Read on a card in hand, so it may reach the owner -- but it must never
    /// throw, and a canonical (compendium) copy has no owner to read.</summary>
    string? UnplayableReason { get; }
}

/// <summary>
/// The plain-English half of <c>CardModel.CanPlay</c> for this mod's cards
/// (<c>EB-264</c>). Read by the bridge (<c>vendor/STS2_MCP/gits/GitsSparkPrice.cs</c>)
/// and emitted onto a hand card as <c>unplayable_reason_text</c>, beside the
/// game's own enum rather than in place of it: the enum is the wire contract
/// several scenarios already assert on, and this is the sentence a page can
/// print.
///
/// READ-ONLY, and it must never throw: it is called on every state poll, for
/// every card in hand, and a state read that throws loses the whole board.
/// Every accessor below is one the cost badge already uses, so what the wire
/// says, what the badge paints and what the gate charges stay one number.
/// </summary>
public static class KleeUnplayableReason
{
    /// <summary>
    /// The sentence for <paramref name="card"/>, or null when nothing here has
    /// one to give (which is almost every card in the game).
    ///
    /// THE PRICE COMES FIRST. A card can be short of Sparks AND out of targets
    /// at once; the price is the clause the player can act on this turn, and it
    /// is the one the row names.
    /// </summary>
    public static string? For(CardModel card)
    {
        return SparkShortfall(card)
               ?? EncoreShortfall(card)
               ?? OwnGate(card);
    }

    /// <summary>
    /// "You cannot pay this card's Spark price", in words, or null when it
    /// charges none or the bank covers it. Printed plus power, through
    /// <see cref="SparkCost.PriceOf"/> -- the same number the gate reads.
    /// </summary>
    public static string? SparkShortfall(CardModel card)
    {
        int price = SparkCost.PriceOf(card);
        if (price <= 0 || SparkCost.Affordable(card)) return null;

        Creature? creature = SparkCost.OwnerCreatureOf(card);
        int bank = creature == null ? 0 : SparkPower.SparksAsResolved(creature);
        return bank <= 0
            ? $"you have no Spark, and this costs {price}"
            : $"you have {bank} Spark, and this costs {price}";
    }

    /// <summary>
    /// The same sentence for Furina's <c>encore_cost</c>, or null when the card
    /// charges no Encore or the buffer covers it (`EB-505`).
    ///
    /// WHAT THE SEAT READ (Furina r11 lane 1, (c) 3). "With energy 3/3 and the
    /// card costing 1, the face read <c>CANNOT BE PLAYED: you do not have
    /// enough energy</c>. The actual shortfall was Encore (2 held, 3
    /// required) ... I spent a genuine beat re-reading my energy bar trying to
    /// work out what I had miscounted." Three times, on Second Course.
    ///
    /// WHY THE PAGE SAID ENERGY. An <c>encore_cost</c> is a BaseLib CUSTOM
    /// RESOURCE COST, so the refusal comes back through the game's own
    /// <c>UnplayableReason</c> enum as a cost failure and
    /// <c>qa_packet.UNPLAYABLE_REASONS</c> renders that as "you do not have
    /// enough energy" -- true of the enum and false of the board.
    ///
    /// AND THE RIGHT SENTENCE ALREADY EXISTED. The seat named it: "Ethereal
    /// Spotlight in the same position printed the correct thing -- <c>you have
    /// 1 Encore, and this costs 2</c> -- so the right message exists and Second
    /// Course is not using it." That one is written by hand on
    /// <c>EtherealSpotlight.UnplayableReason</c>, which reaches ONE card. This
    /// is the same sentence answered centrally off the two numbers the cost
    /// badge already reads (<see cref="MeterCost.PriceIn"/> resolves upgrades
    /// and cost modifiers; <see cref="MeterCost.BankOf"/> is the buffer the
    /// spend takes), so every row with the field gets it and the two copies
    /// cannot drift.
    /// </summary>
    public static string? EncoreShortfall(CardModel card)
    {
        int price;
        try
        {
            price = MeterCost.PriceIn(card, Meter.Encore);
        }
        catch (Exception)
        {
            // THE CLASS CONTRACT, and it is not decoration here: the resolved
            // Encore cost walks the card's PILE to find its combat state
            // (`CustomResourceCost.GetWithModifiers`), and a card that has an
            // owner but is in no pile throws inside the game's own property.
            // Every card this is asked about in play is in a hand, so the
            // branch is unreachable there -- and a state read that lost the
            // whole board over an off-pile copy is the failure this file's
            // header refuses.
            return null;
        }
        if (price <= 0) return null;

        Creature? creature = SparkCost.OwnerCreatureOf(card);
        int bank = MeterCost.BankOf(creature, Meter.Encore);
        return bank >= price ? null : EncoreSentence(bank, price);
    }

    /// <summary>
    /// THE ONE ENCORE SHORTFALL SENTENCE, and the reason it is a named method
    /// is `EB-505`'s own finding: there were two, and only one of them was
    /// right.
    ///
    /// <c>EtherealSpotlight.UnplayableReason</c> wrote this by hand for the
    /// one card whose price is charged inside its op, and the seat read the
    /// correct sentence there and the wrong one on Second Course in the same
    /// position. Both spellings live here now, so a rewording moves both and
    /// the page cannot be shown two grammars for one shortfall.
    /// </summary>
    public static string EncoreSentence(int bank, int price) =>
        bank <= 0
            ? $"you have no Encore, and this costs {price}"
            : $"you have {bank} Encore, and this costs {price}";

    /// <summary>The card's own gate, when it has one that can explain itself
    /// (<see cref="IUnplayableReasonCard"/>).</summary>
    private static string? OwnGate(CardModel card) =>
        card is IUnplayableReasonCard reasoned ? reasoned.UnplayableReason : null;
}
