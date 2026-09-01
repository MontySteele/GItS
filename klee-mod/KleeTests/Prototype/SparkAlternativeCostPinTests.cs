using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
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

    [Fact]
    public void The_base_rule_is_retired_under_the_flag()
    {
        // The one fact the whole arm hangs off, and the reason KleeTests defines
        // PROTOTYPE_CARDS as well as removing this directory without it: the
        // twin assertion lives in SparkSinkPinTests and says the opposite for a
        // release build. Neither half is worth much alone.
        Assert.False(SparkPower.BaseRuleActive);
    }

    [Fact]
    public void The_zeroing_hook_does_not_fire_at_any_bank()
    {
        // The retirement, measured rather than asserted. A bank of 5 is over any
        // threshold the base rule ever had, on a printed-cost Attack the rule
        // would have zeroed, and the hook declines.
        var klee = Seat.Klee().WithPower<SparkPower>(5);
        var power = klee.Creature.Powers.OfType<SparkPower>().First();
        var card = Held<Kaboom>(klee);

        Assert.False(power.TryModifyEnergyCostInCombat(card, 1m, out var cost));
        Assert.Equal(1m, cost);
    }

    [Fact]
    public void The_consume_decision_is_never_taken()
    {
        // The other half of the retirement. BeforeCardPlayed is what SETS the
        // pending spend, and AfterCardPlayed consumes only what it set -- so a
        // null pending field after a play decision is the consume standing down.
        var klee = Seat.Klee().WithPower<SparkPower>(5);
        var power = klee.Creature.Powers.OfType<SparkPower>().First();

        Assert.Null(typeof(SparkPower).GetField("_pendingSpendPlay", All)!
                        .GetValue(power));
    }

    // --- the derived price, per proto row --------------------------------

    [Theory]
    [InlineData(typeof(ProtoKaboomSink), 1)]
    [InlineData(typeof(ProtoPopSpark), 0)]
    [InlineData(typeof(ProtoSparkStrike), 1)]
    [InlineData(typeof(ProtoSparkSweep), 1)]
    [InlineData(typeof(ProtoSparkDoubleTap), 2)]
    [InlineData(typeof(ProtoSparkBlast), 2)]
    [InlineData(typeof(ProtoSparkFinisher), 3)]
    [InlineData(typeof(ProtoTrueSparkKnight), 0)]
    public void Each_proto_row_prints_the_price_its_sheet_row_charges(
        System.Type cardType, int price)
    {
        // The sheet's own numbers (sec.10.2), read back off the emitted class.
        // `PrintedSparkPrice` is the codegen's single declaration of the price
        // and `PriceOf` is what the gate and the badge both consult, so the two
        // agreeing here is the no-drift property itself -- with no Power on the
        // board, PriceOf IS the printed half.
        var card = (CardModel)System.Activator.CreateInstance(cardType)!;

        Assert.Equal(price, SparkCost.PrintedPriceOf(card));
        Assert.Equal(price, SparkCost.PriceOf(card));
    }

    [Fact]
    public void A_card_with_no_price_is_not_a_priced_card()
    {
        // Defence in depth for the interface itself: the marker is emitted only
        // for a row that prints a top-level spend_spark, so a card that does not
        // must not answer the question at all.
        Assert.IsNotAssignableFrom<ISparkPricedCard>(new Kaboom());
        Assert.IsAssignableFrom<ISparkPricedCard>(new ProtoSparkFinisher());
    }

    // --- the strict Rare Power -------------------------------------------

    [Fact]
    public void The_power_prices_an_unpriced_attack_at_three()
    {
        var klee = Seat.Klee().WithPower<SparkAttackCostPower>(1);
        var card = Held<Kaboom>(klee);

        Assert.Equal(0, SparkCost.PrintedPriceOf(card));
        Assert.Equal(SparkAttackCostPower.Price, SparkCost.PriceOf(card));
        Assert.Equal(3, SparkAttackCostPower.Price);   // tier0 C.SPARK_ATTACK_POWER_PRICE
    }

    [Fact]
    public void The_power_zeroes_that_attack_s_energy_cost()
    {
        // "...instead of their Energy cost." The Energy line goes to 0 whether
        // or not the bank can pay, so a brick reads "0 energy, 3 Sparks, and you
        // have 1" rather than a printed cost that lies until you can afford it.
        var klee = Seat.Klee().WithPower<SparkAttackCostPower>(1);
        var power = klee.Creature.Powers.OfType<SparkAttackCostPower>().First();
        var card = Held<Kaboom>(klee);

        Assert.True(power.TryModifyEnergyCostInCombat(card, 1m, out var cost));
        Assert.Equal(0m, cost);
    }

    [Theory]
    [InlineData(0, false)]
    [InlineData(2, false)]   // short by one: the whole price or nothing
    [InlineData(3, true)]
    [InlineData(7, true)]
    public void The_gate_is_two_versus_three_sparks(int bank, bool playable)
    {
        // The decisive read. `ShouldPlay` is what Hook.ShouldPlay fans out and
        // CardModel.CanPlay consults before any energy is committed, so a short
        // bank is an unplayable card and not a play that quietly does nothing.
        var klee = Seat.Klee()
            .WithPower<SparkAttackCostPower>(1)
            .WithPower<SparkPower>(bank);
        var power = klee.Creature.Powers.OfType<SparkAttackCostPower>().First();
        var card = Held<Kaboom>(klee);

        Assert.Equal(playable, power.ShouldPlay(card, AutoPlayType.None));
        Assert.Equal(playable, SparkCost.Affordable(card));
    }

    [Fact]
    public void An_already_priced_attack_is_unaffected()
    {
        // SUB-PICK (a), and it is the clause with a live alternative: (b) would
        // have re-priced Fwoosh! from 1 to 3, punishing the very cards the
        // archetype drafts. The Power neither raises the printed price nor adds
        // to it, and the gate charges the card's own 1.
        var klee = Seat.Klee()
            .WithPower<SparkAttackCostPower>(1)
            .WithPower<SparkPower>(1);
        var power = klee.Creature.Powers.OfType<SparkAttackCostPower>().First();
        var card = Held<ProtoSparkStrike>(klee);

        Assert.Equal(1, SparkCost.PriceOf(card));
        Assert.True(power.ShouldPlay(card, AutoPlayType.None));
        Assert.False(power.TryModifyEnergyCostInCombat(card, 1m, out _));
    }

    [Fact]
    public void An_x_cost_attack_is_exempt()
    {
        // sec.5 is SILENT on X and this is the reading taken (sec.10.11 item 3,
        // and it goes back to [USER]). An X card's cost IS the energy it spends,
        // so a flat 3-Spark conversion would resolve it at X = 0 and it would
        // deal nothing -- R34's own reasoning for the base rule's X exemption,
        // reached again from the other side.
        var klee = Seat.Klee().WithPower<SparkAttackCostPower>(1);
        var power = klee.Creature.Powers.OfType<SparkAttackCostPower>().First();
        var card = Held<FishBlasting>(klee);

        Assert.True(card.EnergyCost.CostsX, "the fixture must be an X card");
        Assert.Equal(0, SparkCost.PriceOf(card));
        Assert.True(power.ShouldPlay(card, AutoPlayType.None));
    }

    [Fact]
    public void Skills_and_powers_keep_their_energy_cost()
    {
        // "Your ATTACKS..." -- Energy becomes very nearly pure Skill currency,
        // which is the payoff loop the card is a bet on. A Skill priced at 3
        // Sparks would make the Power a tax rather than a conversion.
        var klee = Seat.Klee().WithPower<SparkAttackCostPower>(1);
        var power = klee.Creature.Powers.OfType<SparkAttackCostPower>().First();
        var skill = Held<DuckAndCover>(klee);

        Assert.Equal(0, SparkCost.PriceOf(skill));
        Assert.True(power.ShouldPlay(skill, AutoPlayType.None));
        Assert.False(power.TryModifyEnergyCostInCombat(skill, 1m, out _));
    }

    [Fact]
    public void A_second_seat_s_knight_never_prices_this_seat_s_attacks()
    {
        // Every hook here is fanned to EVERY model in the combat
        // (Hook.IterateCombatHookListeners), the other seat's powers included --
        // so the ownership clause is not defensive tidiness, it is the rule. The
        // sim cannot see this at all: tier 0.5 models one seat.
        var klee = Seat.Klee();
        var partner = Seat.Klee().WithPower<SparkAttackCostPower>(1);
        var theirs = partner.Creature.Powers.OfType<SparkAttackCostPower>().First();
        var mine = Held<Kaboom>(klee);

        Assert.Equal(0, SparkCost.PriceOf(mine));
        Assert.True(theirs.ShouldPlay(mine, AutoPlayType.None));
    }

    [Fact]
    public void A_canonical_card_has_no_bank_and_is_never_affordable()
    {
        // EB-94's throw, met from this side. CardModel.Owner asserts mutability,
        // and the badge renders in the compendium where every card is canonical
        // -- so the price is still readable off the row and the AFFORDABILITY is
        // false, rather than a crash or a badge painted playable on a card
        // nobody holds.
        var card = new ProtoSparkFinisher();

        Assert.False(card.IsMutable);
        Assert.Equal(3, SparkCost.PriceOf(card));
        Assert.False(SparkCost.Affordable(card));
    }

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

    [Fact]
    public void The_starter_swaps_two_slots_and_only_two()
    {
        // STRUCTURAL PIN, and the boundary is the reason: `Klee.StartingDeck` is
        // ten `ModelDb.Card<T>()` lookups, and ModelDb is populated only by the
        // game's boot -- calling the getter here throws
        // KeyNotFoundException on the first id (README, the ModelDb row).
        //
        // What the IL DOES say is the whole of sec.10.10 item 4: the seam calls
        // the two substitutions and it still calls Ka-boom! three times, so the
        // deck is ten cards with ONE sink and not four. The count is what
        // sec.10.11 item 2 puts back to [USER], so it is asserted rather than
        // left to a reader.
        var calls = Il.CallSequence(Il.Method("Klee", "get_StartingDeck"));

        Assert.Contains(calls, c => c.EndsWith("SparkStarter.PricedKaboom"));
        Assert.Contains(calls, c => c.EndsWith("SparkStarter.SparkingPop"));
        Assert.Equal(3, calls.Count(c => c == "ModelDb.Card<Kaboom>"));
        Assert.Equal(4, calls.Count(c => c == "ModelDb.Card<DuckAndCover>"));
        Assert.DoesNotContain("ModelDb.Card<Pop>", calls);
    }
}
