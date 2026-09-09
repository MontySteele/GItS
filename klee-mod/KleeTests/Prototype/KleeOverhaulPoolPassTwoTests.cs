using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// POOL PASS TWO -- six rows (2026-09-08, <c>EB-731</c>), in three pairs: the
/// defence shelf's two (Blast Shield, Return to Sender), the Spark sinks' two
/// beside Stoke the Fuse (Bottomless Bag, Once More!) and the Energy engines'
/// two (Sparkling Burst, Blazing Delight).
///
/// TWO NEW OPS AND TWO NEW POWERS arrive with them and they are what this file
/// is about: <c>return_to_hand</c>, which is not a statement at all but a
/// per-class <c>GetResultLocationForCardPlay</c> override;
/// <c>return_last_set_off</c>, which reads the ledger's new per-COMBAT memory
/// of the last Set off card played; <see cref="ReturnToSenderPower"/>, which is
/// <c>IcyPawsPower</c>'s Block MARK with a Bomb on the attacker instead of an
/// aura; and <see cref="BlazingDelightPower"/>, the arm's first standing
/// Energy engine.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on the README's terms. Return to
/// Sender's arithmetic is real -- <see cref="BlockMark.Absorb"/> is pure and is
/// the half a headless pin can read, which is exactly why it exists. Everything
/// that needs <c>PowerCmd</c>, <c>CardPileCmd</c> or a card PLAY is outside the
/// headless boundary and is pinned off the compiled method or off the printed
/// source, labelled. The end-to-end arithmetic is the sim twin's:
/// <c>tier0/tests/test_klee_overhaul.py</c>, section "POOL PASS TWO".
///
/// THE NUMBERS ARE PROTOTYPE NUMBERS (D by the ladder). Nothing here is
/// quotable.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeOverhaulPoolPassTwoTests
{
    private const BindingFlags All = HeadlessGame.All;

    // ---- Row 1, Blast Shield: the routing IS the rule ---------------------

    [Fact]
    public void Blast_shield_routes_its_own_play_to_the_hand()
    {
        // STRUCTURAL, and it has to be: where a played card lands is answered
        // by `CardModel.Play` switching on `GetResultLocationForCardPlay`,
        // which no headless harness runs. What is pinned is the OVERRIDE and
        // its arguments -- `PileType.Hand` at the TOP, which is
        // `KokomiPlan.Replay`'s position -- because that is the whole rule.
        // Twin: `test_blast_shield_comes_back_to_hand_and_can_be_played_again`,
        // where the flag is read at `combat._finish_play`'s routing line.
        var source = Printed("Cards/Prototype/Generated/ProtoKoBlastShield.cs");

        Assert.Contains(
            "protected override CardLocation GetResultLocationForCardPlay() =>",
            source);
        Assert.Contains(
            "new CardLocation(Owner, PileType.Hand, CardPilePosition.Top);",
            source);
    }

    [Fact]
    public void Blast_shield_charges_its_price_again_on_the_second_play()
    {
        // THE CARD IS THE PRICE. A row that comes back to hand and is free
        // would be an infinite Block engine; the Spark price is what makes the
        // second play a decision, and it is spent in `OnPlay` -- which a
        // returned card runs again from the top.
        var card = new ProtoKoBlastShield();
        Assert.Equal(2, card.PrintedSparkPrice);
        Assert.Equal(2, SparkCost.PriceOf(card));

        var play = Il.Calls(Il.Method("ProtoKoBlastShield", "OnPlay"));
        Assert.Contains(play, c => c.Contains("SparkPower.Spend"));
        Assert.Contains(play, c => c.Contains("CreatureCmd.GainBlock"));
    }

    [Fact]
    public void Blast_shield_gains_no_retain()
    {
        // IT DISCARDS AT END OF TURN LIKE ANY CARD IN HAND, which is what
        // keeps the row a tempo card rather than a permanent fixture. Nothing
        // in the override or the row grants Retain, and the absence is pinned
        // because a later reader would otherwise have to infer it.
        var card = new ProtoKoBlastShield();
        Assert.DoesNotContain(card.CanonicalKeywords,
                              k => k == CardKeyword.Retain);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(6m, Vars(card).Single().BaseValue);
    }

    // ---- Row 2, Return to Sender: the mark, real --------------------------

    [Fact]
    public void Return_to_sender_spends_its_mark_the_way_the_paws_do()
    {
        // REAL. `BlockMark.Absorb` is the pure half of the construction and
        // both marks call it, so the two cannot drift: marked-Block-eaten
        // FIRST, clamped to the standing Block on the way in, floored at zero.
        // A payout of 0 is the paws' spelling -- what this rider pays is a
        // charge on the attacker, not Block, so there is nothing to put back
        // under the mark.
        //
        // 8 marked, 8 standing, a hit of 5: 3 left, so the rider fires again
        // on the next absorption. Twin:
        // `test_return_to_sender_plants_what_the_block_absorbed_and_only_now`.
        Assert.Equal(3, Absorb(8, 8, 5));

        // The mark gone: the next hit finds nothing and the rider declines.
        Assert.Equal(0, Absorb(3, 3, 3));
        Assert.Null(Absorb(0, 4, 4));

        // NOTHING ABSORBED IS NOTHING OWED: no Block standing, no rider.
        Assert.Null(Absorb(8, 0, 7));

        // AND THE MARK IS CLAMPED TO THE STANDING BLOCK, which is what makes
        // "this Block" honest after the turn tick has taken the pool away.
        Assert.Null(Absorb(8, 0, 0));
    }

    [Fact]
    public void Return_to_sender_plants_the_absorbed_amount_and_mints_nothing()
    {
        // STRUCTURAL: the placement is `PowerCmd.Apply` through
        // `ProtoBombPower.Place`, outside the headless boundary. What is
        // pinned is the SHAPE -- one `BlockMark.Absorb`, one `Place`, and NO
        // `SparkPower.Gain`: the Bomb is an ordinary plant and rule 4 mints a
        // Spark per EXPLOSION, so nothing has gone off here.
        var bounce = Il.Calls(Il.Method("ReturnToSenderPower", "Bounce"));

        Assert.Contains(bounce, c => c.Contains("BlockMark.Absorb"));
        Assert.Contains(bounce, c => c.Contains("ProtoBombPower.Place"));
        Assert.DoesNotContain(bounce, c => c.Contains("SparkPower.Gain"));
        Assert.DoesNotContain(bounce, c => c.Contains("ElementalHit.Deal"));

        // THE SIZE IS THE ABSORBED AMOUNT and not the mark that was spent --
        // the face says "damage this Block absorbs" -- so the source computes
        // `Math.Min(standing, amount)` and hands THAT to `Place`.
        var source = Printed("Powers/Prototype/KleeOverhaulPowers.cs");
        Assert.Contains(
            "var absorbed = System.Math.Min(standing, (int)amount);", source);
        Assert.Contains("choiceContext, attacker, absorbed, isMine: false",
                        source);
    }

    [Fact]
    public void Return_to_sender_expires_when_no_block_stands_behind_it()
    {
        // "THIS TURN" NEEDS NO TIMER. The mark is housekept at the start of
        // Klee's turn -- after the block clear -- by the same
        // `BlockMark.ClearIfSpent` Diona's and Thoma's marks take, so a rider
        // whose Block the turn tick took away leaves the strip instead of
        // sitting there reading 0.
        var tick = Il.Calls(
            Il.Method("ReturnToSenderPower", "AfterPlayerTurnStart"));
        Assert.Contains(tick, c => c.Contains("BlockMark.ClearIfSpent"));

        // AND THE BADGE IS THE LIVE NUMBER, not the raw stack (`EB-337`).
        var card = new ProtoKoReturnToSender();
        Assert.Equal(2, card.PrintedSparkPrice);
        var play = Il.Calls(Il.Method("ProtoKoReturnToSender", "OnPlay"));
        Assert.Contains(play, c => c.Contains("CreatureCmd.GainBlock"));
        Assert.Contains(play, c => c.Contains("PowerCmd.Apply"));
    }

    [Fact]
    public void Return_to_sender_is_read_first_by_the_one_incoming_listener()
    {
        // ONE LISTENER, ONE ORDER. The Klee leg is first and behind its own
        // flag; the sim asserts the same order at
        // `test_the_incoming_hit_order_is_the_one_the_mod_walks`.
        var source = Printed("Powers/Prototype/CompanionOverhaulHooks.cs");
        var walk = source.Split(
            "public override async Task BeforeDamageReceived(")[1];
        walk = walk.Split("\n    }")[0];

        var order = System.Text.RegularExpressions.Regex
            .Matches(walk, @"OfType<(\w+Power)>")
            .Select(m => m.Groups[1].Value)
            .ToList();

        Assert.Equal(new[]
        {
            "ReturnToSenderPower", "SacramentalShowerPower", "BaronBunnyPower",
            "IcyPawsPower", "BlazingBarrierPower",
        }, order);
        Assert.Contains("if (KleeOverhaul.Enabled)", walk);
    }

    [Fact]
    public void Return_to_sender_moves_its_block_and_its_mark_together()
    {
        // ONE UPGRADE, TWO NUMBERS, and they have to move together or the card
        // marks Block it did not grant. The delta is authored on the row
        // rather than left to the Prototype rule, which would have moved the
        // Block by 3 and the mark by 1.
        var source = Printed(
            "Cards/Prototype/Generated/ProtoKoReturnToSender.cs");
        Assert.Contains("DynamicVars.Block.UpgradeValueBy(3m);", source);
        Assert.Contains("DynamicVars[\"PowerAmount\"].UpgradeValueBy(3m);",
                        source);
        Assert.Contains("new BlockVar(8m", source);
        Assert.Contains("new DynamicVar(\"PowerAmount\", 8m)", source);
    }

    // ---- Row 3, Bottomless Bag: the bank buys cards -----------------------

    [Fact]
    public void Bottomless_bag_draws_two_and_three_upgraded()
    {
        // Countdown's own `Cards` var and `draw` key, so the two rows move one
        // number and the face prints it. Twin:
        // `test_bottomless_bag_draws_two_and_three_upgraded`.
        var card = new ProtoKoBottomlessBag();

        Assert.Equal(CardRarity.Common, card.Rarity);
        Assert.Equal(2, card.PrintedSparkPrice);
        Assert.Equal("Draw {Cards:diff()} card{Cards:plural:|s}.", Face(card));
        Assert.Equal(2m, Vars(card).Single().BaseValue);

        var play = Il.Calls(Il.Method("ProtoKoBottomlessBag", "OnPlay"));
        Assert.Contains(play, c => c.Contains("SparkPower.Spend"));
        Assert.Contains(play, c => c.Contains("CardPileCmd.Draw"));

        var source = Printed(
            "Cards/Prototype/Generated/ProtoKoBottomlessBag.cs");
        Assert.Contains("DynamicVars.Cards.UpgradeValueBy(1m);", source);
    }

    // ---- Row 4, Once More!: the ledger's per-combat memory -----------------

    [Fact]
    public void The_last_set_off_card_is_noted_at_the_three_card_facing_doors()
    {
        // THE NOTE IS TAKEN AT THE OP SITE, above every early return, so a Set
        // off played into an empty board still counts -- "the last Set off card
        // you PLAYED". `SetOff` itself does NOT take it, because a Mine reaches
        // that one with no card at all. Twin: the same note at the head of
        // `effects._op_set_off`.
        foreach (var door in new[] { "SetOffAimed", "SetOffAll", "SetOffRandom" })
        {
            var calls = Il.Calls(Il.Method("ProtoBombPower", door));
            Assert.Contains(calls,
                            c => c.Contains("NoteSetOffCardPlayed"));
        }

        Assert.DoesNotContain(Il.Calls(Il.Method("ProtoBombPower", "SetOff")),
                              c => c.Contains("NoteSetOffCardPlayed"));

        // A NULL CARD IS DECLINED, which is what makes a Mine no answer.
        var ledger = KleeOverhaulLedger.For(Seat.Klee().Creature);
        ledger.NoteSetOffCardPlayed(null);
        Assert.Null(ledger.LastSetOffCard);

        var detonator = new ProtoKoCountdown();
        ledger.NoteSetOffCardPlayed(detonator);
        Assert.Same(detonator, ledger.LastSetOffCard);
    }

    [Fact]
    public void The_last_set_off_card_survives_the_turn_roll()
    {
        // PER COMBAT, and deliberately not rolled: the face says "this
        // combat". Every counter beside it is per turn and `RollTo` clears
        // them; this one is dropped with the table when the combat changes.
        var klee = Seat.Klee().Creature;
        var ledger = KleeOverhaulLedger.For(klee);
        var detonator = new ProtoKoCountdown();

        ledger.NoteSetOffCardPlayed(detonator);
        ledger.NoteExplosion(reacted: false, damageDealt: 4);
        Assert.Equal(1, ledger.SetOffThisTurn);

        ledger.RollTo(9);
        Assert.Equal(0, ledger.SetOffThisTurn);
        Assert.Same(detonator, ledger.LastSetOffCard);
    }

    [Fact]
    public void Once_more_moves_a_card_only_out_of_the_discard_pile()
    {
        // STRUCTURAL: the move is `CardPileCmd.Add`, outside the headless
        // boundary. What is pinned is the PILE TEST in front of it -- the
        // command takes a card out of wherever it is, so without the test a
        // card still in hand would be a silent no-op and an EXHAUSTED card
        // would be a resurrection the face does not promise. Twin:
        // `test_once_more_takes_the_last_set_off_card_out_of_the_discard`.
        var calls = Il.Calls(
            Il.Method("KleeOverhaulLedger", "ReturnLastSetOff"));

        Assert.Contains(calls, c => c.Contains("CardPile.Get"));
        Assert.Contains(calls, c => c.Contains("CardPileCmd.Add"));

        var source = Printed("Powers/Prototype/KleeOverhaulLedger.cs");
        Assert.Contains("CardPile.Get(PileType.Discard, player)", source);
        Assert.Contains("if (pile == null || !pile.Cards.Contains(card)) return;",
                        source);
        Assert.Contains(
            "await CardPileCmd.Add(card, PileType.Hand, CardPilePosition.Top);",
            source);
    }

    [Fact]
    public void Once_more_is_deterministic_and_pays_whether_or_not_it_moves()
    {
        // NO SELECTION SCREEN: there is one answer and the player already
        // knows it. And the price is a COST LINE, paid before the body runs,
        // so a card that is not in the discard pile costs the Sparks anyway --
        // the same bargain every Spark-priced row makes.
        var play = Il.Calls(Il.Method("ProtoKoOnceMore", "OnPlay"));

        Assert.Contains(play, c => c.Contains("SparkPower.Spend"));
        Assert.Contains(play, c => c.Contains("ReturnLastSetOff"));
        Assert.DoesNotContain(play, c => c.Contains("CardSelectCmd"));

        var source = Printed("Cards/Prototype/Generated/ProtoKoOnceMore.cs");
        Assert.Contains("PrintedSparkPrice => (IsUpgraded ? 2 : 3)", source);
        Assert.Contains("SparkPower.Spend(choiceContext, Owner.Creature, "
                        + "(IsUpgraded ? 2 : 3), this)", source);
    }

    // ---- Row 5, Sparkling Burst: Run Away!'s predicate, paid in Energy ----

    [Fact]
    public void Sparkling_burst_reads_run_aways_own_predicate()
    {
        // THE SAME COUNTER, so the two rows cannot disagree about what a
        // turn's explosion is: `KleeOverhaulLedger.SetOffThisTurn > 0`, which
        // is the text Run Away! emits verbatim. Twin:
        // `test_sparkling_burst_pays_one_energy_or_two_by_the_predicate`.
        var source = Printed(
            "Cards/Prototype/Generated/ProtoKoSparklingBurst.cs");
        var runAway = Printed("Cards/Prototype/Generated/ProtoKoRunAway.cs");

        const string predicate =
            "if (KleeOverhaulLedger.For(Owner.Creature).SetOffThisTurn > 0)";
        Assert.Contains(predicate, source);
        Assert.Contains(predicate, runAway);

        // TWO Energy grants, one flat and one behind the predicate.
        Assert.Equal(2, System.Text.RegularExpressions.Regex
            .Matches(source, @"PlayerCmd\.GainEnergy\(1, Owner\)").Count);
    }

    [Fact]
    public void Sparkling_burst_does_not_exhaust()
    {
        // NOT EXHAUST, which is what separates it from Sugar Rush beside it: a
        // Spark sink that fires once a fight is a burst, and this row is meant
        // to be the turn's tempo whenever the bank can pay for it.
        var card = new ProtoKoSparklingBurst();

        Assert.DoesNotContain(card.CanonicalKeywords,
                              k => k == CardKeyword.Exhaust);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.Equal(0, CanonicalCost(card));
        Assert.Equal(3, card.PrintedSparkPrice);
    }

    // ---- Row 6, Blazing Delight: the arm's first Energy engine -------------

    [Fact]
    public void Blazing_delight_pays_at_groundeds_own_hook()
    {
        // `AfterPlayerTurnStart`, and the site is the rule: the energy reset
        // and the turn's opening draw have already happened there, so the
        // Energy survives the turn and the card is drawn on top of the opening
        // hand. `BeforeSideTurnStart` would have the reset eat it. Twin:
        // `test_blazing_delight_pays_energy_and_a_card_at_turn_start`.
        var tick = Il.Calls(
            Il.Method("BlazingDelightPower", "AfterPlayerTurnStart"));

        Assert.Contains(tick, c => c.Contains("PlayerCmd.GainEnergy"));
        Assert.Contains(tick, c => c.Contains("CardPileCmd.Draw"));

        // AND IT IS UNCONDITIONAL: no ledger read, no board read. Rule 7 is
        // about nothing going OFF by itself, which is a fact about charges.
        Assert.DoesNotContain(tick, c => c.Contains("KleeOverhaulLedger"));
        Assert.DoesNotContain(tick, c => c.Contains("AnyPlacedBy"));
    }

    [Fact]
    public void Blazing_delights_amount_is_a_rate_read_by_both_halves()
    {
        // STACKS ADD: two copies pay 2 and 2, off ONE number read twice, so
        // the face's arithmetic is the power's and not a second rule.
        var source = Printed("Powers/Prototype/KleeOverhaulPowers.cs");
        var body = source.Split("public sealed class BlazingDelightPower")[1];

        Assert.Contains("var n = (int)Amount;", body);
        Assert.Contains("await PlayerCmd.GainEnergy(n, player);", body);
        Assert.Contains("await CardPileCmd.Draw(choiceContext, n, player);",
                        body);
        Assert.Contains("PowerStackType.Counter", body);
    }

    [Fact]
    public void Blazing_delight_is_a_rare_power_at_the_arms_top_spark_price()
    {
        // The row's shape: a 2-energy Rare Power costing FIVE Sparks, which is
        // the highest printed price on the surface -- the bank a Cook deck has
        // been minting is what buys the engine.
        var card = new ProtoKoBlazingDelight();

        Assert.Equal(CardRarity.Rare, card.Rarity);
        Assert.Equal(CardType.Power, card.Type);
        Assert.Equal(2, CanonicalCost(card));
        Assert.Equal(5, card.PrintedSparkPrice);

        var play = Il.Calls(Il.Method("ProtoKoBlazingDelight", "OnPlay"));
        Assert.Contains(play, c => c.Contains("SparkPower.Spend"));
        Assert.Contains(play, c => c.Contains("PowerCmd.Apply"));

        // THE UPGRADE CUTS THE SPARK PRICE, Once More!'s and Sparkling Burst's
        // rail: the `+` card is the SAME 2-energy body for 4 Sparks. It is
        // authored on the row rather than left to the Prototype rule, which
        // would have fallen through to its cost clause and sold a 1-energy Rare
        // instead -- `amount: 1` on a Power reads as "this row prints no power
        // number" (`upgrades._proto_power`'s `> 1` test).
        //
        // THE FACE PRINTS NOTHING FOR IT, because a Spark price sits in the
        // cost slot; what the player sees move is the BADGE, which renders
        // `PrintedSparkPrice`, and the gate reads that same property back
        // through `SparkCost.PriceOf` -- so the price shown, the price gated on
        // and the price charged are one expression.
        var source = Printed(
            "Cards/Prototype/Generated/ProtoKoBlazingDelight.cs");
        Assert.DoesNotContain("EnergyCost.UpgradeBy", source);
        Assert.Contains("PrintedSparkPrice => (IsUpgraded ? 4 : 5)", source);
        Assert.Contains("SparkPower.Spend(choiceContext, Owner.Creature, "
                        + "(IsUpgraded ? 4 : 5), this)", source);
    }

    // ---- The six are offered, and the roster says so ----------------------

    [Fact]
    public void The_six_rows_are_in_the_arms_offerable_slice()
    {
        // A row that compiles into `PrototypeRoster` and is not named in
        // `KleeOverhaulRoster.Slice()` is built and never OFFERED -- which is
        // exactly what R252's four rows did until `lint_arm_pool_parity`
        // caught it. Named here as well, because the lint reads the sheet and
        // this reads the compiled list.
        // READ OFF THE COMPILED METHOD, `ArmStarterBasicsTests.Cards`' idiom:
        // the roster is internal and the list is what a `ModelDb.Card<T>` call
        // per row names.
        var slice = Il.CallSequence(Il.Method("KleeOverhaulRoster", "Slice"))
            .Where(c => c.StartsWith("ModelDb.Card<", System.StringComparison.Ordinal))
            .ToList();

        foreach (var row in new[]
                 {
                     "ProtoKoBlastShield", "ProtoKoReturnToSender",
                     "ProtoKoBottomlessBag", "ProtoKoOnceMore",
                     "ProtoKoSparklingBurst", "ProtoKoBlazingDelight",
                 })
        {
            Assert.Contains(slice, c => c.Contains(row));
        }
    }

    // ---- helpers ---------------------------------------------------------

    /// <summary>A mod source file, read whole with its comments stripped.
    /// Walked up from the test binary rather than copied at build time, which
    /// is `PoolPassThreeTests.Printed`'s idiom and its reason: a stale copy
    /// beside the dll is exactly the drift a text pin exists to catch.</summary>
    private static string Printed(string relativePath)
    {
        var relative = System.IO.Path.Combine("klee-mod", "KleeCode",
            relativePath.Replace('/', System.IO.Path.DirectorySeparatorChar));
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = System.IO.Path.Combine(dir.FullName, relative);
            if (System.IO.File.Exists(candidate))
            {
                return System.Text.RegularExpressions.Regex.Replace(
                    System.IO.File.ReadAllText(candidate),
                    @"^\s*//.*$", string.Empty,
                    System.Text.RegularExpressions.RegexOptions.Multiline);
            }
            dir = dir.Parent;
        }

        throw new System.IO.FileNotFoundException(
            "no " + relative + " above " + System.AppContext.BaseDirectory);
    }

    /// <summary><c>BlockMark</c> is internal to the mod assembly, so its pure
    /// arithmetic is reached the way every other internal seam in this project
    /// is. <c>payout: 0</c> is the paws' spelling and this rider's.</summary>
    private static int? Absorb(int mark, int standing, int incoming) =>
        (int?)Il.Method("BlockMark", "Absorb")
            .Invoke(null, new object[] { mark, standing, incoming, 0 });

    private static int CanonicalCost(CardModel card) =>
        (int)typeof(CardModel)
            .GetProperty("CanonicalEnergyCost", All)!.GetValue(card)!;

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    /// <summary><c>CanonicalVars</c> is protected, so it is read the way every
    /// other internal seam in this project is read.</summary>
    private static IReadOnlyList<DynamicVar> Vars(CardModel card) =>
        ((IEnumerable<DynamicVar>)typeof(CardModel)
            .GetProperty("CanonicalVars", All)!.GetValue(card)!).ToList();
}
