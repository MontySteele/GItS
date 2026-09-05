using System.Linq;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;

namespace KleeMod.Powers;

/// <summary>
/// THE RISING HAND COST (the pool pass, <c>EB-491</c>): Long Fuse's second
/// rule, "Costs 1 more each turn it stays in your hand."
///
/// WHY THE ARM NEEDED ONE. Rounds 15 and 16 asked the same question from
/// opposite ends. Round 15: every drafted detonator discards at end of turn, so
/// "hold the Bomb" meant "throw the detonator away" for most of a run, and a
/// 55-gold Steady enchantment on Perfect Timing "opened more decision-space
/// than any card I drafted". Round 16: once the pile passes the enemy's HP,
/// Ka-pow! is free and Retained, so the last turn is automatic -- "charming
/// twice, likely corrosive by the tenth time". A Retained detonator is what the
/// first wants; a Retained detonator that gets MORE expensive the longer it
/// waits is what stops it becoming the second.
///
/// <c>AddUntilPlayed</c> IS THE WHOLE MECHANISM, and it is the base game's own
/// modifier rather than a new one: it accumulates, it survives the turn
/// boundary, <c>CardEnergyCost.AfterCardPlayedCleanup</c> clears it when the
/// card is played, and it is combat-scoped like every other local modifier, so
/// the card comes out of the next fight at its printed cost. That is the
/// printed rule exactly -- "each turn it stays in your hand", never downward,
/// reset when the card leaves.
///
/// THE SITE IS THE END OF KLEE'S TURN, before the hand flush, which is the one
/// moment "it stayed in your hand" becomes true for the turn that just
/// happened. A card without Retain would be discarded a moment later and its
/// rise cleared on the next play; the rule is written for the Retained one.
///
/// A MARKER INTERFACE AND NOT A POWER, because the rule belongs to the CARD and
/// not to the board: two Long Fuses in one hand each carry their own fuse, and
/// a card that is not in hand carries none. The generated row declares
/// <see cref="IRisingHandCostCard"/> and the number it rises by; nothing else
/// in the arm knows about it. Sim twin: <c>klee_overhaul.roll_rising_costs</c>,
/// off <c>Card.rising_cost</c>.
/// </summary>
internal static class KleeOverhaulRisingCost
{
    /// <summary>
    /// One turn passed with these cards in hand: each rising-cost card in it
    /// costs its own <see cref="IRisingHandCostCard.HandCostRise"/> more, until
    /// it is played.
    ///
    /// A SNAPSHOT of the hand (<c>ToList</c>), for the reason every other sweep
    /// in this arm takes one: nothing here can move a card between piles, but a
    /// pile read that is live while it is walked is the shape that breaks the
    /// day something does.
    /// </summary>
    internal static void RollHand(Player? owner)
    {
        if (!KleeOverhaul.Enabled || owner == null) return;
        var hand = CardPile.Get(PileType.Hand, owner);
        if (hand == null) return;

        foreach (var card in hand.Cards.ToList())
        {
            if (card is not IRisingHandCostCard fuse) continue;
            var rise = fuse.HandCostRise;
            if (rise <= 0) continue;
            card.EnergyCost.AddUntilPlayed(rise);
        }
    }
}

/// <summary>
/// A card whose energy cost RISES while it waits in hand (Long Fuse).
///
/// Carried by the generated row from the sheet's <c>rising_cost:</c> key, the
/// same way <see cref="ISparkPricedCard"/> carries a Spark price: the number is
/// the ROW's, so a retune moves the sheet and nothing else.
/// </summary>
public interface IRisingHandCostCard
{
    /// <summary>How much the card costs more, per turn it stays in hand.</summary>
    int HandCostRise { get; }
}
