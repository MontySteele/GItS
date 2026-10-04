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
/// THE POOL PASS -- ten rows off the readings of rounds 13 to 16
/// (2026-09-05, <c>EB-491</c>; the packet is
/// <c>review/active/klee-pool-pass-2026-09-05.md</c>).
///
/// FOUR NEW RULES ARRIVED WITH THEM and they are what this file is about: a
/// hand cost that RISES while the card waits (built for Long Fuse; deleted at
/// R276 with the row), a Bomb COPIED at the size of the largest one on the
/// board (All of My Treasures!), a grow keyed to the enemy's AURA with a
/// floor under it (Kindling; cut at R276 with its engine verb), a Bomb SPLIT
/// into two
/// halves on random enemies (Split Charge), and the VERMILLION PACT, which
/// (since 2026-09-27) makes every Bomb in one Set off react with the aura the
/// first one consumed. The other five rows are new spellings of shapes the arm already had.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL. What
/// needs <c>PowerCmd</c> (a placement, a removal, an aura application) or a
/// card PLAY is pinned off the compiled method and says so. The end-to-end
/// arithmetic is the sim twin's:
/// <c>tier0/tests/test_klee_overhaul_rules.py</c>, section "THE POOL PASS".
///
/// THE NUMBERS ARE PROTOTYPE NUMBERS (D by the ladder). Nothing here is
/// quotable.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class PoolPassThreeTests
{
    private const BindingFlags All = HeadlessGame.All;

    // ---- All of My Treasures!: the copy -----------------------------------

    [Fact]
    public void Treasures_reads_the_board_and_places_one_plain_bomb()
    {
        // STRUCTURAL: the placement is `PowerCmd.Apply`, outside the headless
        // boundary. What is pinned is the SHAPE -- one read of the board's
        // largest charge, one `Place`, and no `TakeAt` or `TakeAll`: the card
        // COPIES, so the pile it was measured against is untouched and still
        // growing. Twins: `test_treasures_copies_the_largest_bomb_onto_the_aimed_enemy`,
        // `test_treasures_copies_a_mine_as_a_plain_bomb`.
        var calls = Il.Calls(Il.Method("ProtoBombPower", "PlaceCopyOfLargest"));

        Assert.Contains(calls, c => c.Contains("LargestCharge"));
        Assert.Contains(calls, c => c.Contains("ProtoBombPower.Place"));
        Assert.DoesNotContain(calls, c => c.Contains("TakeAt"));
        Assert.DoesNotContain(calls, c => c.Contains("TakeAll"));
    }

    [Fact]
    public void Treasures_is_an_exhausting_rare_skill_that_aims()
    {
        // The row's shape, off the shipped class: a Rare that fires ONCE (it
        // Exhausts), aimed, and printing no number of its own -- "equal to
        // your largest Bomb" is a read, and a figure here would be a second
        // reading of it.
        var card = new ProtoKoAllOfMyTreasures();

        Assert.Equal(CardRarity.Rare, card.Rarity);
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(TargetType.AnyEnemy, card.TargetType);
        Assert.Contains(card.CanonicalKeywords, k => k == CardKeyword.Exhaust);
        Assert.Empty(Vars(card));
    }

    // ---- Fireworks Show: Set off ALL, at a price the upgrade cuts ----------

    [Fact]
    public void A_spark_price_an_upgrade_cuts_still_has_a_row()
    {
        // THE ONLY UPGRADE KIND THAT MOVES A SPARK PRICE. The face prints
        // nothing for it -- a Spark price sits in the cost slot and the body
        // does not restate it -- so what the player sees move is the BADGE,
        // which renders `PrintedSparkPrice`. The gate reads the same property
        // back through `SparkCost.PriceOf`, so the price shown, the price
        // gated on and the price charged are one expression. It rode Fireworks
        // Show until `EB-749` cut that row, then Once More! until the Klee-only
        // companions (2026-10-03) cut that one; Sparkling Burst spells the
        // same delta.
        var card = new ProtoKoSparklingBurst();
        Assert.Equal(2, card.PrintedSparkPrice);
        Assert.Equal(2, SparkCost.PriceOf(card));

        var source = Printed("Cards/Prototype/Generated/ProtoKoSparklingBurst.cs");
        Assert.Contains("PrintedSparkPrice => (IsUpgraded ? 1 : 2)", source);
        Assert.Contains("SparkPower.Spend(choiceContext, Owner.Creature, "
                        + "(IsUpgraded ? 1 : 2), this)", source);
    }

    [Fact]
    public void Tinder_toss_sets_off_all_enemies_and_then_hits_them_all()
    {
        // `EB-749` (R271 sec.5.3): Tinder Toss took Fireworks Show's slot in
        // the ruling that cut that row. `SetOffAll` with a literal 0 for the card's own hit -- Flame Dance's spelling on
        // every enemy -- and then the printed 3 to all, IN THAT ORDER, which
        // is the rule and not an implementation detail. Because it HAS a line
        // of its own it is not `EB-261`-gated and does not refuse a bare
        // board.
        var source = Printed("Cards/Prototype/Generated/ProtoKoTinderToss.cs");
        var setOff = source.IndexOf("ProtoBombPower.SetOffAll(choiceContext, "
                                    + "Owner.Creature, this, cardPlay, 0)",
                                    System.StringComparison.Ordinal);
        var hit = source.IndexOf("TargetingAllOpponents",
                                 System.StringComparison.Ordinal);
        Assert.True(setOff >= 0 && hit > setOff,
                    "Set off resolves on every enemy before the 3 lands");
        Assert.DoesNotContain("no enemy is holding a Bomb", source);
        Assert.False(typeof(IUnplayableReasonCard)
                         .IsAssignableFrom(typeof(ProtoKoTinderToss)));
    }

    // ---- the Vermillion Pact ----------------------------------------------
    //
    // Reworked 2026-09-27: "When a Set off makes one of your Bombs react,
    // every other Bomb it sets off reacts with the same aura." STRUCTURAL: a
    // real board needs `AuraCmd` and `PowerCmd`, outside the headless boundary.
    // The arithmetic (three Bomb 8s into Hydro land 12/12/12, a Set off ALL
    // feeds each enemy its own aura) is the sim twin's, section "THE POOL
    // PASS" in `tier0/tests/test_klee_overhaul_rules.py`.

    [Fact]
    public void The_pact_lives_in_the_set_off_loop_and_restores_before_each_charge()
    {
        // THE ORDERING IS THE RULE. `SetOff` reads the Pact once per take,
        // and inside the loop the restore comes BEFORE the next charge's
        // `Explode`, so that charge reacts with the aura the first one ate.
        // Twin: `test_the_pact_makes_every_bomb_in_the_set_off_react`.
        var play = Il.CallSequence(Il.Method("ProtoBombPower", "SetOff"))
            .ToList();
        var holds = play.FindIndex(
            c => c.Contains("VermillionPactPower.Holds"));
        var restore = play.FindIndex(
            c => c.Contains("VermillionPactPower.Restore"));
        var explode = play.FindIndex(c => c == "ProtoBombPower.Explode");

        Assert.True(holds >= 0, "the take reads whether its owner holds the Pact");
        Assert.True(restore >= 0, "the loop puts the aura back");
        Assert.True(explode >= 0, "the loop still explodes each charge");
        Assert.True(holds < restore, "read once, before the loop");
        Assert.True(restore < explode, "restored before the charge goes off");
    }

    [Fact]
    public void Explode_reports_the_aura_it_consumed_and_no_longer_hands_it_back()
    {
        // `Explode` returns the aura it reacted with and consumed; the Pact's
        // old restore (the Attack that Set it off reacts too) is gone from it.
        // Twins: `test_the_pact_does_not_hand_the_aura_to_the_set_off_attack`,
        // `test_the_pact_carries_nothing_to_the_next_set_off`.
        var explode = (MethodInfo)Il.Method("ProtoBombPower", "Explode");
        Assert.Equal(typeof(System.Threading.Tasks.Task<global::KleeMod.Elements.Element>),
                     explode.ReturnType);
        Assert.DoesNotContain(Il.Calls(explode),
                              c => c.StartsWith("VermillionPactPower."));
        Assert.Contains(Il.Calls(explode), c => c.Contains("AuraCmd.Find"));
    }

    [Fact]
    public void The_pact_reads_the_take_not_the_card_and_skips_mines_and_pocket_match()
    {
        // "When a Set off": any card's, Skill or Attack, so the card type is
        // no longer read. A Mine answering an enemy attack is not a Set off,
        // and Pocket Match's single charge has no later charge to feed; neither
        // reaches the Pact. Twins: `test_the_pact_reads_a_skills_set_off_too`,
        // `test_the_pact_ignores_mines_answering_an_attack`.
        var source = Printed("Powers/Prototype/KleeOverhaulPowers.cs");
        Assert.DoesNotContain("cardSource is not { Type: CardType.Attack }",
                              source);
        Assert.DoesNotContain(
            Il.Calls(Il.Method("ProtoBombPower", "BeforeDamageReceived")),
            c => c.StartsWith("VermillionPactPower."));
        Assert.DoesNotContain(
            Il.Calls(Il.Method("ProtoBombPower", "SetOffLargest")),
            c => c.StartsWith("VermillionPactPower."));

        // The restore refuses a board that already holds an aura, and goes up
        // through the ordinary front door so the reaction it feeds is real.
        var restore = Il.Calls(Il.Method("VermillionPactPower", "Restore"));
        Assert.Contains(restore, c => c.Contains("AuraCmd.Find"));
        Assert.Contains(restore, c => c.Contains("AuraCmd.Apply"));
    }

    [Fact]
    public void The_pact_power_prints_the_card_face()
    {
        var power = new VermillionPactPower().Localization!
            .First(r => r.Item1 == "description").Item2;
        var card = new ProtoKoVermillionPact().Localization!
            .First(r => r.Item1 == "description").Item2;

        Assert.Equal(card, power);
        Assert.Contains("every other [gold]Bomb[/gold] it sets off", card);
    }

    [Fact]
    public void The_pact_is_a_two_energy_rare_power_whose_upgrade_is_its_cost()
    {
        // The pool's eighth Rare, and the brief's count. Its upgrade is the
        // COST PIP -- there is no number on the face to move, because the rule
        // is a fact about the board rather than an amount.
        var card = new ProtoKoVermillionPact();

        Assert.Equal(CardRarity.Rare, card.Rarity);
        Assert.Equal(CardType.Power, card.Type);
        Assert.Contains(Il.Calls(Il.Method("ProtoKoVermillionPact", "OnUpgrade")),
                        c => c.Contains("EnergyCost.UpgradeBy"));
    }

    // ---- the ten, on the offer seam ---------------------------------------

    [Fact]
    public void The_pool_pass_rows_are_offered_and_none_is_in_the_starter()
    {
        // `lint_arm_pool_parity` holds this list to the sheet and to
        // `C.KLEE_OVERHAUL_POOL_IDS`; what a pin adds is that the rows the
        // readings asked for are actually on the OFFER seam, which is the seam
        // R252 forgot.
        var slice = Il.CallSequence(Il.Method("KleeOverhaulRoster", "Slice"))
            .ToList();
        var starter = Il.CallSequence(
            Il.Method("KleeOverhaulRoster", "StartingDeck")).ToList();

        foreach (var row in new[]
                 {
                     // Long Fuse and Kindling were cut at R276, Split
                     // Charge by the Klee status package (2026-10-01).
                     "ProtoKoAllOfMyTreasures",
                     "ProtoKoFishBlasting", "ProtoKoPocketMatch",
                     "ProtoKoBombsAway", "ProtoKoFlashPoint",
                     "ProtoKoVermillionPact",
                 })
        {
            Assert.Contains(slice, c => c.Contains(row));
            Assert.DoesNotContain(starter, c => c.Contains(row));
        }
    }

    [Fact]
    public void Fish_blasting_adds_its_status_into_the_discard_pile()
    {
        // A status goes to the discard pile, as the base game adds every one
        // ([USER], 2026-10-03: "I agree that we should adopt the same
        // convention"). Twin:
        // `test_fish_blasting_adds_a_confiscated_into_the_discard_pile`.
        var source = Printed("Cards/Prototype/Generated/ProtoKoFishBlasting.cs");
        Assert.Contains("PileType.Discard, Owner);", source);
        Assert.DoesNotContain("PileType.Draw", source);

        // And it does NOT Set off: plain pressure, which is what separates it
        // from every detonator beside it.
        Assert.DoesNotContain(
            Il.Calls(Il.Method("ProtoKoFishBlasting", "OnPlay")),
            c => c.Contains("SetOff"));
    }

    [Fact]
    public void Bombs_away_places_one_bomb_and_blocks_per_bombed_enemy()
    {
        // AoE trim (2026-10-03): "Place a Bomb 4 on an enemy. Gain 4 Block,
        // plus 2 for each enemy with a Bomb." A Skill now; the Block is the
        // CalculatedBlockVar over her bombed enemies, gained AFTER the Bomb.
        var card = new ProtoKoBombsAway();
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(TargetType.AnyEnemy, card.TargetType);
        Assert.Equal(4m, card.DynamicVars["BombSize"].BaseValue);

        var play = Il.CallSequence(Il.Method("ProtoKoBombsAway", "OnPlay")).ToList();
        var place = play.IndexOf("ProtoBombPower.Place");
        var block = play.IndexOf("CreatureCmd.GainBlock");
        Assert.True(place >= 0 && block > place);
        Assert.DoesNotContain(play, c => c.Contains("PlaceOnAll"));
        Assert.DoesNotContain(play, c => c.Contains("SetOff"));
    }

    [Fact]
    public void Pocket_match_is_the_retained_single_charge_detonator()
    {
        // Playtest 2026-09-24 ([USER]: "Pocket Match is redundant with
        // Ka-pow!"): no Spark price any more, and it sets off ONLY the largest
        // charge on the enemy. The rule's own pins are in
        // `KleePlaytest20260924Tests`.
        var card = new ProtoKoPocketMatch();

        Assert.False(card is ISparkPricedCard);
        Assert.Equal(CardType.Attack, card.Type);
        Assert.Contains(card.CanonicalKeywords, k => k == CardKeyword.Retain);
        Assert.Contains(Il.Calls(Il.Method("ProtoKoPocketMatch", "OnPlay")),
                        c => c.Contains("ProtoBombPower.SetOffLargestAimed"));
    }

    [Fact]
    public void Flash_point_pays_its_rider_only_on_a_bomb_reaction()
    {
        // The React shelf's tempo rider, and it is CONDITIONAL: the Spark and
        // the card are paid only when a Bomb triggered an Elemental Reaction
        // this turn, which is Sizzle's and Perfect Timing's own grammar. It is
        // also the one card on the arm that mints a Spark, named as such in
        // `KleeOverhaulRuleTests.Rule4_no_slice_card_mints_a_spark_except_the_named_one`.
        var play = Il.Calls(Il.Method("ProtoKoFlashPoint", "OnPlay"));

        Assert.Contains(play, c => c.Contains("ProtoBombPower.SetOffAimed"));
        Assert.Contains(play, c => c.Contains("KleeOverhaulLedger"));
        Assert.Contains(play, c => c.Contains("SparkPower.Gain"));
        Assert.Contains(play, c => c.Contains("CardPileCmd.Draw"));
    }

    // ---- helpers ---------------------------------------------------------

    /// <summary>A mod source file, read whole with its comments stripped.
    /// Walked up from the test binary rather than copied at build time, which
    /// is `Round12Tests.Printed`'s idiom and its reason: a stale copy beside
    /// the dll is exactly the drift a text pin exists to catch.</summary>
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

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    /// <summary><c>CanonicalVars</c> is protected, so it is read the way every
    /// other internal seam in this project is read.</summary>
    private static IReadOnlyList<DynamicVar> Vars(CardModel card) =>
        ((IEnumerable<DynamicVar>)typeof(CardModel)
            .GetProperty("CanonicalVars", All)!.GetValue(card)!).ToList();
}
