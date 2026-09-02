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
        return SparkShortfall(card) ?? OwnGate(card);
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

    /// <summary>The card's own gate, when it has one that can explain itself
    /// (<see cref="IUnplayableReasonCard"/>).</summary>
    private static string? OwnGate(CardModel card) =>
        card is IUnplayableReasonCard reasoned ? reasoned.UnplayableReason : null;
}
