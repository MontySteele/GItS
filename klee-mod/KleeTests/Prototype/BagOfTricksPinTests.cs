using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// BAG OF TRICKS, pinned (<c>EB-224</c>; sim twin
/// <c>tier0/tests/test_eb224_bag_of_tricks.py</c>).
///
/// THE ROW. <c>proto_spark_mode_bombs</c>, 0 Energy, Skill, Uncommon:
/// <em>Choose one: Place 1 Bomb dealing 5 | Spend 3 Sparks: place 3 Bombs
/// dealing 5.</em> The cheap mode is the shipped <c>pop</c> printed alone; the
/// expensive one is <c>bomb_voyage</c>'s body, which ships at 2 Energy, with
/// the bank buying that Energy instead.
///
/// WHY IT IS THE FIRST OF ITS KIND. Until R225 the written Spark-cost clause
/// said the spend must stay at the CARD's top level, and the doctrine seat held
/// this arm on it twice. R225 amended the clause to read top level OR the head
/// of a <c>choose_one</c> mode; <c>EB-182</c> had already built the behaviour in
/// both engines, and the seat's other clause (D4 — an unpayable mode being
/// offered anyway) was RESOLVED by that build.
///
/// WHAT THIS FILE ADDS OVER <c>MeterCostBadgeTests</c>. That file pins the badge
/// and the per-mode rule on SHIPPED Encore rows. This one pins the rule on a
/// SPARK-priced mode, which is the meter this arm charges and the one the badge
/// had to reach through <c>MeterCost</c> rather than a printed declaration.
///
/// This whole file is compiled only under <c>-p:PrototypeCards=true</c>
/// (KleeTests.csproj), which is the switch that compiles the row. A release
/// build contains no such card and can hold no pin against one.
/// </summary>
public class BagOfTricksPinTests
{
    private const BindingFlags All = HeadlessGame.All;

    private const int Price = 3;

    /// <summary>A card in a seat's hand: mutable, owned, and therefore askable.
    /// `IsMutable` first — Owner's setter calls AssertMutable, which is EB-94's
    /// throw met from the other side.</summary>
    private static T Held<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    /// <summary>The card's own generated price table. Read by reflection rather
    /// than copied: a test carrying its own literal is the drift the table
    /// exists to prevent.</summary>
    private static ModePrice?[] Table() =>
        (ModePrice?[])typeof(ProtoSparkModeBombs)
            .GetField("ModePrices", All)!.GetValue(null)!;

    // --- the two prices, as the row declares them -------------------------

    [Fact]
    public void Mode_one_is_free_and_mode_two_costs_three_sparks()
    {
        // The whole shape of the arm in one assertion. If the price ever moved
        // to the CARD's cost line — option (5) of the closed pick list — the
        // free mode would stop being free, which the seat said outright
        // destroys the comparison. `null` is what says mode 1 charges nothing:
        // a declared price of 0 would claim a cost line it does not have.
        var table = Table();

        Assert.Equal(2, table.Length);
        Assert.Null(table[0]);
        Assert.Equal(Meter.Sparks, table[1]!.Value.Meter);
        Assert.Equal(Price, table[1]!.Value.Amount);
    }

    [Fact]
    public void The_badge_on_the_priced_face_reads_the_cards_own_row()
    {
        // EB-220's rule, on this row: the mode FACE — the thing a player is
        // choosing between on the choose-a-card screen — declares
        // IMeterPricedCard by READING the table above, so the badge paints the
        // very literal the screen filter and the playability gate consulted.
        // Painting itself needs Godot nodes, which are process death in this
        // host (README); what is provable is that there is ONE number.
        var table = Table();
        var face = new ProtoSparkModeBombsModeB();

        Assert.Equal(table[1]!.Value.Meter, face.PricedMeter);
        Assert.Equal(table[1]!.Value.Amount, face.PrintedMeterPrice);
        Assert.Equal(Meter.Sparks, face.PricedMeter);
        Assert.Equal(Price, face.PrintedMeterPrice);
        Assert.Equal(Meter.Sparks, MeterCost.Priced(face)!.Value.Meter);
        Assert.Equal(Price, MeterCost.PriceIn(face, Meter.Sparks));
    }

    [Fact]
    public void The_free_face_carries_no_price_at_all()
    {
        // Not a price of zero: a badge is absent because there is no cost line,
        // and a face that declared one would announce a fee it does not charge.
        Assert.IsNotAssignableFrom<IMeterPricedCard>(new ProtoSparkModeBombsModeA());
        Assert.Null(MeterCost.Priced(new ProtoSparkModeBombsModeA()));
    }

    [Fact]
    public void The_card_itself_is_not_badged_for_its_modes_price()
    {
        // The price belongs to ONE mode, and the card face is not the surface
        // that mode is chosen on. Badging the card would announce a fee its
        // free mode does not charge.
        Assert.Null(MeterCost.Priced(new ProtoSparkModeBombs()));
    }

    // --- affordability: two Sparks against three --------------------------

    [Theory]
    [InlineData(0)]
    [InlineData(2)]   // short by one: the whole price or nothing
    public void A_short_bank_loses_the_priced_mode_and_keeps_the_card(int bank)
    {
        // EB-182's behaviour, on this row. The expensive mode is OMITTED from
        // the choose-a-card screen — the 0.111.0 decompile gives it no
        // per-option disabled state to grey — and the free mode keeps the card
        // playable. That asymmetry is the reason the price could not sit at the
        // card's top level: there, a short bank would kill the free Bomb too.
        var klee = Seat.Klee().WithPower<SparkPower>(bank);

        Assert.Equal(new[] { 0 }, ModalChoice.Offered(klee.Player, Table()));
        Assert.True(ModalChoice.AnyAffordable(klee.Player, Table()));
    }

    [Fact]
    public void At_three_sparks_both_modes_are_offered()
    {
        // The bank is the gate, not the card: nothing about the row differs
        // between this test and the one above.
        var klee = Seat.Klee().WithPower<SparkPower>(Price);

        Assert.Equal(new[] { 0, 1 }, ModalChoice.Offered(klee.Player, Table()));
        Assert.True(ModalChoice.AnyAffordable(klee.Player, Table()));
    }

    [Fact]
    public void The_badge_is_affordable_only_at_the_price()
    {
        // The same read the badge colours with, taken off the face a player
        // holds. `MeterCost.BankOf` is the meter's own accessor — the one
        // SparkPower.CanSpend gates on — so the colour and the refusal cannot
        // disagree.
        var short_ = Seat.Klee().WithPower<SparkPower>(2);
        var paid = Seat.Klee().WithPower<SparkPower>(Price);
        var shortFace = Held<ProtoSparkModeBombsModeB>(short_);
        var paidFace = Held<ProtoSparkModeBombsModeB>(paid);
        var price = MeterCost.Priced(shortFace)!.Value;

        Assert.Equal(2, MeterCost.BankOf(short_.Creature, Meter.Sparks));
        Assert.False(MeterCost.Affordable(shortFace, price));

        Assert.Equal(Price, MeterCost.BankOf(paid.Creature, Meter.Sparks));
        Assert.True(MeterCost.Affordable(paidFace, price));
    }

    [Fact]
    public void The_refusal_names_the_price_and_the_bank()
    {
        // The printable half, the C# twin of `combat.modal_refusal`. A staged
        // turn, a replay and a log line all read it, so "the mode was not
        // there" is never the whole record of why.
        var klee = Seat.Klee().WithPower<SparkPower>(2);
        var refusals = ModalChoice.Refusals(
            klee.Player, System.Array.Empty<CardModel>(), Table());

        Assert.Contains("3", refusals);
        Assert.Contains("Sparks", refusals);
        Assert.Contains("2", refusals);
    }

    // --- the payment ------------------------------------------------------

    [Fact]
    public void The_priced_mode_pays_before_it_places_and_abandons_if_it_cannot()
    {
        // THE DEFECT EB-224 CLOSED, pinned on the emitted body. `spend_spark`
        // was in the codegen's price table but in neither BRANCH_OPS nor
        // `_emit_branch_op`, so a mode head priced in Sparks declared a price,
        // filtered the option in by it, and then paid out WITHOUT DEBITING THE
        // BANK. An op a price table knows and an emitter does not is an unpaid
        // payoff, not a blocked one.
        //
        // Executing the play needs a PlayerChoiceContext and a live combat,
        // outside the headless boundary (README), so this is structural — but
        // the two facts it pins are exactly the two that were wrong: the spend
        // is CALLED, and it is called BEFORE the Bombs are placed. The early
        // return on a refused payment is the generated `if (!await ...) return;`
        // that guards it, the same shape `spend_charge` has carried since
        // R213 E1.
        var play = Il.CallSequence(
            typeof(ProtoSparkModeBombs).GetMethod("OnPlay", All)!)
            .Select(c => c.Split('<')[0])
            .ToList();

        Assert.Contains(play, c => c.EndsWith("SparkPower.Spend"));
        Assert.Contains(play, c => c.EndsWith("BombPower.Place"));
        Assert.True(
            play.FindIndex(c => c.EndsWith("SparkPower.Spend"))
                < play.FindLastIndex(c => c.EndsWith("BombPower.Place")),
            "the bank must be debited before the priced mode places its Bombs");
    }

    [Fact]
    public void The_card_level_gate_is_the_per_mode_table_and_nothing_else()
    {
        // STRUCTURAL PIN. `IsPlayable` asks `ModalChoice.AnyAffordable` over the
        // one declared table rather than carrying a price of its own — which is
        // what keeps a card with ONE affordable mode playable, the half a
        // card-level cost line cannot express.
        var calls = Il.Calls(typeof(ProtoSparkModeBombs)
            .GetProperty("IsPlayable", All)!.GetMethod!);

        Assert.Contains(calls, c => c.EndsWith("ModalChoice.AnyAffordable"));
    }
}
