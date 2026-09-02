// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// THE SPARK PRICE, PER CARD. EB-185 put the Spark BANK on the wire (it rides as
// a power, `spark`, and `understudy/adapter.py` maps it onto `Player.sparks`).
// That was enough while the bank had one destination and the engine chose it.
// Under the alternative cost it is not:
//
//   * a card's Spark price is a PRINTED cost, and `cost` on the wire is the
//     ENERGY cost, which for every one of these cards is 0 -- so an observed
//     board shows a hand of free cards and says nothing about what they charge;
//   * under the strict Rare Power the price is not on the card at all. It is
//     state, contributed by a power, and no wire key carries it;
//   * `can_play` is already there and is NOT a substitute. It collapses every
//     reason a card is unplayable into one boolean, so a seat cannot tell "I
//     cannot afford this" from "there is no legal target".
//
// A seat that cannot read the price cannot make the spend-versus-hold decision
// the whole slice is a bet on. D4: everything the player decides on must be
// readable at the decision point.
//
// WHAT THIS READS, AND WHY IT IS REFLECTION. `KleeMod.Powers.SparkCost` is a
// SHIPPED type (it is not quarantined -- three shipped Klee Skills print a Spark
// price today), but this bridge must still load with no klee mod present at all.
// A compile-time reference would make it refuse to load without one. Reflection
// makes "no klee mod" mean "no Spark prices", which is the truth. Same posture
// GitsResources.cs takes toward BaseLib and GitsKurageMemory.cs toward the
// memory rule, and the same failure mode: probed once, cached including the
// null, and every failure swallowed -- a state read must never throw.
//
// THE CONTRACT. Two public statics on `KleeMod.Powers.SparkCost`:
//
//     public static int  PriceOf(CardModel card)      // printed + power
//     public static bool Affordable(CardModel card)   // can the owner pay it
//
// PriceOf is the SAME expression the card's own IsPlayable gate and the cost
// badge read, so what the wire reports, what the player sees and what the game
// charges are one number by construction. Emitted onto a hand card as
// `spark_price` and `spark_affordable`, and only when there is a price: an
// ABSENT pair means "this card charges no Sparks", which is true of almost every
// card in the game, and the observed board stays the size it was.
//
// READ-ONLY. Nothing here plays a card, spends a bank or mutates a model.

using System;
using System.Reflection;
using MegaCrit.Sts2.Core.Models;

namespace STS2_MCP;

public static partial class McpMod
{
    private const string GitsSparkCostType = "KleeMod.Powers.SparkCost";

    // EB-264. `CardModel.CanPlay` collapses every mod-side refusal into
    // `BlockedByCardLogic`, which is the token the blind render printed at the
    // tester ("tells a player nothing, and the actual reason -- you have no
    // Spark -- is printed nowhere"). The klee mod answers the same question in
    // words; this is the third accessor on the same reflection contract:
    //
    //     public static string? For(CardModel card)   // null = nothing to say
    //
    // ADDITIVE. The enum still rides as `unplayable_reason`, which several
    // understudy scenarios assert on by name; the sentence rides beside it as
    // `unplayable_reason_text` and is omitted whenever there is none.
    private const string GitsUnplayableReasonType =
        "KleeMod.Powers.KleeUnplayableReason";

    private static bool _gitsSparkProbed;
    private static MethodInfo? _gitsSparkPriceOf;
    private static MethodInfo? _gitsSparkAffordable;
    private static MethodInfo? _gitsUnplayableReasonFor;

    /// <summary>
    /// Locate the three accessors once. A null result is cached too: a game
    /// with no klee mod will not grow one mid-session, and a state read should
    /// not pay for an assembly walk on every poll.
    /// </summary>
    private static void GitsProbeSparkCost()
    {
        if (_gitsSparkProbed) return;
        _gitsSparkProbed = true;

        try
        {
            Type? type = null;
            Type? reasonType = null;
            foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
            {
                type ??= asm.GetType(GitsSparkCostType, throwOnError: false);
                reasonType ??= asm.GetType(
                    GitsUnplayableReasonType, throwOnError: false);
                if (type != null && reasonType != null) break;
            }

            _gitsUnplayableReasonFor = reasonType?.GetMethod(
                "For", BindingFlags.Public | BindingFlags.Static,
                null, new[] { typeof(CardModel) }, null);

            if (type == null) return;

            _gitsSparkPriceOf = type.GetMethod(
                "PriceOf", BindingFlags.Public | BindingFlags.Static,
                null, new[] { typeof(CardModel) }, null);
            _gitsSparkAffordable = type.GetMethod(
                "Affordable", BindingFlags.Public | BindingFlags.Static,
                null, new[] { typeof(CardModel) }, null);
        }
        catch (Exception)
        {
            _gitsSparkPriceOf = null;
            _gitsSparkAffordable = null;
            _gitsUnplayableReasonFor = null;
        }
    }

    /// <summary>
    /// Why this card is refusing, in words a page can print, or null when the
    /// mod has nothing to say about it (and when there is no klee mod to ask).
    /// Asked only of a card the game has ALREADY refused, so a non-null answer
    /// is always about a refusal that happened.
    /// </summary>
    private static string? GitsUnplayableReasonText(CardModel card)
    {
        GitsProbeSparkCost();
        if (_gitsUnplayableReasonFor == null) return null;

        try
        {
            return _gitsUnplayableReasonFor.Invoke(
                null, new object?[] { card }) as string;
        }
        catch (Exception)
        {
            return null;
        }
    }

    /// <summary>
    /// The card's Spark price right now, or null when it charges none (and when
    /// there is no klee mod to ask). Null is the common answer and is why the
    /// keys are omitted rather than written as 0.
    /// </summary>
    private static int? GitsSparkPrice(CardModel card)
    {
        GitsProbeSparkCost();
        if (_gitsSparkPriceOf == null) return null;

        try
        {
            var price = (int)_gitsSparkPriceOf.Invoke(null, new object?[] { card })!;
            return price > 0 ? price : (int?)null;
        }
        catch (Exception)
        {
            return null;
        }
    }

    /// <summary>
    /// Can the card's owner pay that price? Asked only for a card that HAS one,
    /// so a false here means "short bank" and nothing else -- which is the
    /// distinction `can_play` cannot make.
    /// </summary>
    private static bool GitsSparkAffordable(CardModel card)
    {
        GitsProbeSparkCost();
        if (_gitsSparkAffordable == null) return true;

        try
        {
            return (bool)_gitsSparkAffordable.Invoke(null, new object?[] { card })!;
        }
        catch (Exception)
        {
            return true;
        }
    }
}
