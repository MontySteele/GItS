using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE BOMB BADGE'S TWO OWED HALVES, both about the SAME sentence and both
/// about a number a seat could not attach to a charge.
///
/// `EB-605` -- "`Bomb 6 ... Bomb sizes here: 4`. Two numbers for one bomb in
/// one sentence. I believe the 6 is the Vaporize-adjusted forecast against a
/// Hydro aura, but I inferred that from a Spark counter, not from any printed
/// word" (Klee r22 lane 1 re-run (c) 2). The page half landed 2026-09-07; the
/// C# half was `mods.Clause` naming Vulnerable and the cap and never the
/// reaction multiplier. It is BUILT, by `EB-721`, which met the same hole from
/// the other side (Klee r25 lane 2, (c) 2: `Bomb 18` beside `sizes, oldest
/// first: 12`) and put `with Vaporize` / `with Melt` into the clause. What
/// `EB-721` pinned is the GRID -- that a row exists for every combination and
/// that each row is the plain row plus its own words
/// (`KleeOverhaulRoundFourTests`). What nothing pinned is the SELECTION: that
/// a real body wearing a real aura makes the badge choose the row that names
/// the reaction. Those are the two fixtures `EB-605`'s acceptance asks for --
/// a lone Bomb, and a reaction -- and they are here.
///
/// `EB-755` -- "'oldest first' does not say which of two Bombs placed in one
/// turn is the older, and only the first hit takes the aura, so a seat could
/// not plan a reaction." The D default is taken: the sizes print in SET-OFF
/// ORDER WITH ORDINALS, on the page and on the C# tooltip.
///
/// THE COLLECTION IS LOAD-BEARING, `KleeOverhaulRoundOneFixTests`' reason:
/// `KleeOverhaul.Enabled` is one static for the whole process.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class BombBadgeHalvesTests
{
    private static string Row(ProtoBombPower pile, string key) =>
        pile.Localization!.First(r => r.Item1 == key).Item2;

    private static string LocKey(ProtoBombPower pile) =>
        (string)typeof(ProtoBombPower)
            .GetProperty("SmartDescriptionLocKey", HeadlessGame.All)!
            .GetValue(pile)!;

    private static string Charges(ProtoBombPower pile) =>
        pile.DynamicVars["Charges"].ToString();

    // ---- EB-445: the X price's slot --------------------------------------

    /// <summary>A card in a seat's hand: mutable, owned, and therefore
    /// askable. `IsMutable` first -- Owner's setter calls AssertMutable,
    /// which is `EB-94`'s throw met from the other side.</summary>
    private static T Held<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    /// <summary>The badge's own slot text for one card at one price. Private,
    /// and reached by reflection rather than made internal: the METHOD is the
    /// unit under test and nothing else in the mod may call it.</summary>
    private static string SlotText(CardModel card, MeterPrice price) =>
        (string)Il.Method("MeterCostBadge", "PriceText")
            .Invoke(null, new object[] { card, price })!;

    [Fact]
    public void The_whole_bank_price_draws_an_X_and_never_its_gate()
    {
        // `EB-445`. Stoke the Fuse's face reads "Spend all your remaining
        // Sparks" and its badge read `1`. The 1 is honest about the GATE --
        // an empty bank cannot pay, any bank holding a Spark can -- and it is
        // not what the card charges, and the badge is where a player reads a
        // price. The blind-play page was repaired first
        // (`qa_packet.cost_label` prints `all your Sparks (1 to play)`); this
        // is the C# half, in the base game's own grammar for a whole-bank
        // cost.
        //
        // Seen to FAIL: the slot rendered `price.Amount.ToString()`, the 1.
        var klee = Seat.Klee();
        var card = Held<ProtoKoStokeTheFuse>(klee);

        Assert.True(SparkCost.PricesWholeBank(card));
        Assert.Equal("X", SlotText(card, new MeterPrice(Meter.Sparks, 1)));
    }

    [Fact]
    public void An_ordinary_spark_price_still_draws_its_number()
    {
        // The other side of the same branch: a card that prints a real number
        // is untouched, which is every priced face in the mod but one.
        var klee = Seat.Klee();
        var card = Held<ProtoKoBottomlessBag>(klee);

        Assert.False(SparkCost.PricesWholeBank(card));
        Assert.Equal("2", SlotText(card, new MeterPrice(Meter.Sparks, 2)));
        // And the X belongs to the Spark price alone: no other meter spells a
        // whole-bank cost today, so no other meter may borrow the glyph.
        Assert.Equal("3", SlotText(card, new MeterPrice(Meter.Encore, 3)));
    }

    [Fact]
    public void The_gate_still_charges_one_on_the_card_that_prints_the_X()
    {
        // The slot says X; the PRICE did not move. `PrintedSparkPrice` is what
        // `IsPlayable` reads back through `SparkCost.PriceOf`, and a display
        // row that quietly repriced a card would be the defect the badge was
        // built to prevent, one direction over.
        var card = new ProtoKoStokeTheFuse();

        Assert.Equal(1, ((ISparkPricedCard)card).PrintedSparkPrice);
        Assert.Equal(1, SparkCost.PrintedPriceOf(card));
        // And the marker is emitted by the CODEGEN off the same effect as the
        // price, so a row that prints the X price cannot arrive without it.
        Assert.IsAssignableFrom<ISparkXPricedCard>(card);
    }

    // ---- EB-605: the face a real board selects ---------------------------

    [Fact]
    public void A_lone_bomb_on_a_bare_body_names_no_modifier_at_all()
    {
        // THE FIRST FIXTURE THE ROW ASKS FOR. Nothing is moving this number,
        // so the sentence carries no clause -- and it is the baseline the
        // reaction fixture below is read against, because a clause that
        // appeared on every board would say nothing.
        var klee = Seat.Klee();
        var bare = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(bare, klee.Creature,
            new ProtoBombs.Charge(12));

        Assert.EndsWith(".smartDescription", LocKey(pile));

        var face = Row(pile, "smartDescription");
        Assert.DoesNotContain("Vaporize", face);
        Assert.DoesNotContain("Melt", face);
        Assert.DoesNotContain("Vulnerable", face);
        Assert.DoesNotContain("capped", face);
    }

    [Fact]
    public void A_bomb_standing_against_a_hydro_aura_names_the_vaporize()
    {
        // THE SECOND FIXTURE, and `EB-605`'s whole complaint: the headline is
        // `PredictedSetOffDamage` -- the amplified number -- and the list is
        // the sizes before it, so the two stood adjacent and disagreed with
        // nothing printed to join them. `EB-721` put the clause on the number
        // the amplifier moved; this pins that a live Hydro body SELECTS it.
        var klee = Seat.Klee();
        var wet = Seat.Klee(30).WithPower<HydroAuraPower>(2).Creature;
        var pile = ProtoBombs.Place(wet, klee.Creature,
            new ProtoBombs.Charge(12));

        Assert.EndsWith(".smartDescriptionVaporize", LocKey(pile));
        Assert.Contains("with [gold]Vaporize[/gold]",
                        Row(pile, "smartDescriptionVaporize"));

        // And the clause is the ONLY difference from the bare face, which is
        // what makes it a clause about that term and not a second sentence.
        Assert.Equal(
            Row(pile, "smartDescription"),
            Row(pile, "smartDescriptionVaporize")
                .Replace(" with [gold]Vaporize[/gold]", string.Empty));
    }

    [Fact]
    public void A_cryo_body_names_the_melt_and_an_electro_body_names_neither()
    {
        // The table and not a shortlist: `ReactionTable.AmplifierMultiplier`
        // answers above 1 for Pyro over Hydro and Pyro over Cryo alone, and
        // this face prints Pyro damage. An Electro body REACTS (Overloaded)
        // and does not multiply, so a clause there would put a name on a term
        // that did not move the number.
        var klee = Seat.Klee();
        var cold = Seat.Klee(30).WithPower<CryoAuraPower>(2).Creature;
        var live = Seat.Klee(30).WithPower<ElectroAuraPower>(2).Creature;

        Assert.EndsWith(".smartDescriptionMelt", LocKey(
            ProtoBombs.Place(cold, klee.Creature, new ProtoBombs.Charge(9))));
        Assert.EndsWith(".smartDescription", LocKey(
            ProtoBombs.Place(live, klee.Creature, new ProtoBombs.Charge(9))));
    }

    // ---- text pass 2026-09-25: the Sparks a Set off here gives -----------

    [Fact]
    public void The_sparks_clause_prints_only_when_the_placer_is_paid_per_explosion()
    {
        // The face says "and gives N Sparks" only when a Set off here really
        // makes Sparks: one per explosion, from Pounding Surprise (or Dodoco
        // Tales), and only under the arm. A placer holding neither -- a
        // Companion card can plant for another character -- reads no Spark
        // clause at all.
        var was = KleeOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = true;

            var bare = Seat.Klee();
            var target = Seat.Klee(60).Creature;
            var unpaid = ProtoBombs.Place(target, bare.Creature,
                new ProtoBombs.Charge(5), new ProtoBombs.Charge(4));
            Assert.Equal(0, unpaid.SparksOnSetOff());
            Assert.EndsWith(".smartDescription", LocKey(unpaid));

            var klee = Seat.Klee()
                .WithRelic<global::KleeMod.Relics.PoundingSurprise>();
            var other = Seat.Klee(60).Creature;
            var paid = ProtoBombs.Place(other, klee.Creature,
                new ProtoBombs.Charge(5), new ProtoBombs.Charge(4));
            Assert.Equal(2 * KleeOverhaulLaw.SparkPerExplosion,
                         paid.SparksOnSetOff());
            Assert.EndsWith(".smartDescriptionSparks", LocKey(paid));
            Assert.Equal(
                "[gold]Set off[/gold] here deals [blue]{Size}[/blue] "
              + "[gold]Pyro[/gold] damage and gives [blue]{Sparks}[/blue] "
              + "[gold]Spark{Sparks:plural:|s}[/gold]. Bombs here, oldest "
              + "first: [blue]{Charges}[/blue].",
                Row(paid, "smartDescriptionSparks"));

            // Off the arm the relic pays nothing per explosion, so the face
            // says nothing about Sparks.
            KleeOverhaul.Enabled = false;
            Assert.Equal(0, paid.SparksOnSetOff());
        }
        finally
        {
            KleeOverhaul.Enabled = was;
        }
    }

    // ---- EB-755: which of two placed this turn goes off first ------------

    [Fact]
    public void Two_bombs_placed_in_one_turn_print_under_their_ordinals()
    {
        // THE ROW'S ACCEPTANCE. The list was already in set-off order and the
        // clause already said "oldest first" -- and for two charges placed in
        // the SAME turn there is nothing on the board joining the rule to the
        // list, while only the leading charge takes the aura. So the list
        // names its own positions.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(60).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(12));
        pile.AddCharge(new ProtoBombPower.ProtoCharge(8, false, 0));

        Assert.Equal("1st 12 / 2nd 8", Charges(pile));
    }

    [Fact]
    public void The_ordinals_follow_the_order_the_set_off_actually_walks()
    {
        // The ordinal is a claim about DETONATION ORDER, so it is checked
        // against the take the explosion loop walks rather than against the
        // list that produced it.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(90).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(5));
        pile.AddCharge(new ProtoBombPower.ProtoCharge(8, false, 0));
        pile.AddCharge(new ProtoBombPower.ProtoCharge(20, false, 0));

        Assert.Equal("1st 5 / 2nd 8 / 3rd 20", Charges(pile));
        Assert.Equal(new[] { 5, 8, 20 },
                     pile.TakeAll()!.Select(c => c.Size).ToArray());
    }

    [Fact]
    public void A_lone_charge_carries_no_ordinal_and_an_empty_pile_prints_zero()
    {
        // `EB-536`'s argument one var over: a fact about a STACK reads as
        // noise on a single Bomb, and `1st 12` is a numeral a reader of a lone
        // Bomb has to discard. The emptied pile keeps `EB-450`'s `0` -- a face
        // caught mid-teardown must not render "Bombs here: ,".
        var klee = Seat.Klee();
        var enemy = Seat.Klee(60).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(12));

        Assert.Equal("12", Charges(pile));

        pile.TakeAll();
        Assert.Equal("0", Charges(pile));
    }

    [Fact]
    public void The_teens_take_the_th_suffix_a_long_pile_can_reach()
    {
        // 11th, 12th, 13th -- not 11st. A pile CAN get there: the r21 seat's
        // merged stack was nine charges, and Jumpy Dumpty's rider adds one per
        // enemy per detonation.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(400).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(1));
        for (var size = 2; size <= 21; size++)
        {
            pile.AddCharge(new ProtoBombPower.ProtoCharge(size, false, 0));
        }

        var printed = Charges(pile).Split(" / ");

        Assert.Equal("11th 11", printed[10]);
        Assert.Equal("12th 12", printed[11]);
        Assert.Equal("13th 13", printed[12]);
        Assert.Equal("21st 21", printed[20]);
    }
}
