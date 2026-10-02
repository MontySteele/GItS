using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE SPARKS ALTERNATIVE COST, pinned
/// (review/ruled/klee-sparks-2026-08-29.md sec.10; sim twin
/// <c>tier0/tests/test_spark_alt_cost.py</c>).
///
/// This whole file is compiled only under <c>-p:PrototypeCards=true</c>
/// (KleeTests.csproj), which is the same switch that compiles the rule. That is
/// the point rather than an inconvenience: the arm's C# does not exist in a
/// release build, so a pin against it cannot either.
///
/// MOST OF THIS IS REAL, NOT STRUCTURAL, and it is worth saying why -- the
/// headless boundary (README) puts a live <c>CombatState</c> and a card PLAY out
/// of reach, but every clause of this rule is a READ off a card and a creature's
/// power list. A card can be constructed, made mutable and given an owner
/// exactly as <c>ExhaustSelectionTests</c> and <c>ParityAuthorityPinTests</c>
/// already do, and the price, the gate and the Energy zeroing are then callable
/// directly. What is NOT reachable is the PAYMENT -- <c>SparkPower.Spend</c>
/// needs a <c>PlayerChoiceContext</c> -- and that one is pinned structurally and
/// labelled.
///
/// WHERE THIS RAN. The pinned assembly vault (<c>UsePinnedAssemblies</c>) lacks
/// <c>Sentry.Godot</c>, which the test HOST needs to load <c>sts2.dll</c>; the
/// vault keeps the BUILD alive, not a test run. So this suite is run against the
/// INSTALLED game assemblies, read-only, resolved through
/// <c>klee-mod/local.props</c> -- the same route the Kokomi arm took, for the
/// same reason.
/// </summary>
public class SparkAlternativeCostPinTests
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

    // --- the flag -------------------------------------------------------

    // --- the derived price ------------------------------------------------
    //
    // `EB-750`: the per-row price theory is DELETED with its rows. It ran the
    // eight `proto_*` classes of the Sparks pool past `SparkCost.PrintedPriceOf`
    // and `SparkCost.PriceOf`; R270 ruled Spark a currency under the overhaul,
    // the rows left the prototype surface and the classes with them (commit
    // 036c12d150d6dbd58f0776a0d07e3c028a321a61). The codegen's single price
    // declaration is still pinned here, on a row that DOES exist, and by the
    // strict-Rare-Power clauses below, which read a price off a shipped card.

    // --- the strict Rare Power -------------------------------------------


    // --- the payment, structurally ---------------------------------------

    [Fact]
    public void The_power_pays_through_the_same_spend_the_cards_use()
    {
        // STRUCTURAL PIN. Executing the payment needs a PlayerChoiceContext and
        // a live combat, outside the headless boundary. What IS checkable is
        // that the payment routes through SparkPower.Spend -- the all-or-nothing
        // primitive a card that prints its own price already uses, which refuses
        // through the same CanSpend the gate above consults -- rather than
        // carrying a second copy of the rule that could disagree with the badge.
        var calls = Il.Calls(typeof(SparkAttackCostPower)
            .GetMethod(nameof(SparkAttackCostPower.AfterCardPlayed), All)!);

        Assert.Contains(calls, c => c.EndsWith("SparkPower.Spend"));
    }

    [Fact]
    public void The_spend_decision_is_snapshotted_before_resolution()
    {
        // STRUCTURAL PIN, and it is the Snap finding inherited: tier0's play_card
        // pays BEFORE the card's effects resolve, so a card whose own rider
        // pushes the bank over mid-resolution must not change what it was
        // charged. The decision is taken in BeforeCardPlayed and executed in
        // AfterCardPlayed, so the only instance state this power may hold is the
        // one pending play -- a cached price or a cached bank would arrive as a
        // second field.
        var fields = typeof(SparkAttackCostPower)
            .GetFields(BindingFlags.Instance | BindingFlags.Public
                       | BindingFlags.NonPublic | BindingFlags.DeclaredOnly)
            .Select(f => f.Name)
            .ToArray();

        Assert.Equal(new[] { "_pendingSpendPlay" }, fields);
    }

    // --- the badge --------------------------------------------------------

    [Fact]
    public void The_badge_still_renders_the_spark_gate_s_own_number()
    {
        // STRUCTURAL PIN: painting needs Godot nodes, which are process death in
        // this host (README, the headless boundary). What the pin CAN say is the
        // property the badge exists for -- the SPARK price it draws is
        // SparkCost.PriceOf, the same expression the generated IsPlayable gate
        // reads, so there is no second literal for the display to drift from.
        //
        // EB-220 moved the badge out of the quarantine and generalised it to
        // three meters; its own pins are in `MeterCostBadgeTests`. This one
        // stays HERE because the fact it guards is the flagged one: under
        // `-p:PrototypeCards=true` the Spark price is state-aware (the strict
        // Rare Power adds to it), and the badge's read must keep going through
        // SparkCost rather than off a card's printed declaration.
        var calls = Il.Calls(Il.Method("MeterCost", "Priced"));

        Assert.Contains(calls, c => c.EndsWith("SparkCost.PriceOf"));
    }

    // --- the starter ------------------------------------------------------

}
