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
/// hands back the aura an explosion consumed so the Attack behind it reacts
/// too. The other five rows are new spellings of shapes the arm already had.
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

    // ---- Split Charge: the bridge -----------------------------------------

    [Fact]
    public void Split_charge_takes_one_charge_and_places_two()
    {
        // STRUCTURAL for the same reason: both halves land through
        // `PowerCmd.Apply`. What is pinned is that the row REMOVES exactly one
        // charge (`TakeAt`, not `TakeAll`) and rolls a destination per half
        // off the combat RNG -- the independent roll that lets both halves
        // land on one enemy, which is the row's printed losing line. Twins:
        // `test_split_charge_halves_the_largest_bomb`,
        // `test_split_charge_leaves_the_smaller_piles_alone`.
        var calls = Il.Calls(Il.Method("ProtoBombPower", "SplitLargest"));

        Assert.Contains(calls, c => c.Contains("LargestCharge"));
        Assert.Contains(calls, c => c.Contains("TakeAt"));
        Assert.DoesNotContain(calls, c => c.Contains("TakeAll"));
        Assert.Contains(calls, c => c.Contains("NextItem"));
        Assert.Contains(calls, c => c.Contains("ProtoBombPower.Place"));
    }

    [Fact]
    public void Split_charge_buys_its_growth_with_the_upgrade_only()
    {
        // The base card prints no figure for the halves' growth because there
        // is none: the upgrade BUYS a clause, so the face states it in its own
        // `{IfUpgraded:show:...}` hole and the play reads `IsUpgraded`. A
        // `Grow` var here would declare a number the base face never shows.
        var card = new ProtoKoSplitCharge();

        Assert.Contains("{IfUpgraded:show: Halves grow by 2.|}", Face(card));
        Assert.Empty(Vars(card));
        Assert.Contains(Il.Calls(Il.Method("ProtoKoSplitCharge", "OnPlay")),
                        c => c.Contains("ProtoBombPower.SplitLargest"));
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
        // Show until `EB-749` cut that row; Once More! spells the same delta.
        // Twin: `test_once_more_upgraded_charges_one_spark_less`.
        // Klee balance review, pick 4a, 2026-09-25. 3 Sparks -> 2.
        var card = new ProtoKoOnceMore();
        Assert.Equal(2, card.PrintedSparkPrice);
        Assert.Equal(2, SparkCost.PriceOf(card));

        var source = Printed("Cards/Prototype/Generated/ProtoKoOnceMore.cs");
        Assert.Contains("PrintedSparkPrice => (IsUpgraded ? 1 : 2)", source);
        Assert.Contains("SparkPower.Spend(choiceContext, Owner.Creature, "
                        + "(IsUpgraded ? 1 : 2), this)", source);
    }

    [Fact]
    public void Tinder_toss_sets_off_all_enemies_and_then_hits_them_all()
    {
        // `EB-749` (R271 sec.5.3): Tinder Toss took Fireworks Show's slot in
        // the ruling that cut that row. `SetOffAll` with the aura filter OFF
        // and a literal 0 for the card's own hit -- Flame Dance's spelling on
        // every enemy -- and then the printed 3 to all, IN THAT ORDER, which
        // is the rule and not an implementation detail. Because it HAS a line
        // of its own it is not `EB-261`-gated and does not refuse a bare
        // board.
        var source = Printed("Cards/Prototype/Generated/ProtoKoTinderToss.cs");
        var setOff = source.IndexOf("ProtoBombPower.SetOffAll(choiceContext, "
                                    + "Owner.Creature, this, cardPlay, 0, "
                                    + "nonPyroAuraOnly: false)",
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

    [Fact]
    public void The_pact_reads_the_aura_before_the_hit_and_restores_it_after()
    {
        // THE ORDERING IS THE RULE. The aura has to be read BEFORE
        // `ElementalHit` runs, because the hit is what consumes it, and handed
        // back BEFORE the card's own damage, because that hit is what the
        // Rare exists to make react. Both are read off `Explode`'s call
        // sequence, so an edit that moved either would fail here. Twin:
        // `test_the_pact_hands_back_the_aura_a_bomb_consumed`.
        var play = Il.CallSequence(Il.Method("ProtoBombPower", "Explode"))
            .ToList();
        var read = play.FindIndex(
            c => c.Contains("VermillionPactPower.AuraToRestore"));
        var hit = play.FindIndex(c => c.Contains("ElementalHit"));
        var restore = play.FindIndex(
            c => c.Contains("VermillionPactPower.Restore"));

        Assert.True(read >= 0, "the Pact reads the aura the Bomb will eat");
        Assert.True(hit >= 0, "the explosion still goes through the funnel");
        Assert.True(restore >= 0, "the Pact hands it back");
        Assert.True(read < hit, "read before the funnel consumes it");
        Assert.True(hit < restore, "handed back after the explosion landed");
    }

    [Fact]
    public void The_pact_is_attacks_only_and_reactions_only()
    {
        // "The Attack that Set it off" is the whole scope: a Mine answering an
        // enemy intent carries no card at all, and a Skill's Set off has no
        // hit behind it for the aura to feed. And `reacted` is the gate on the
        // payout -- an explosion into a Pyro aura refreshes rather than
        // reacts, consumes nothing, and is owed nothing back. Twins:
        // `test_the_pact_ignores_a_skills_set_off`,
        // `test_the_pact_ignores_a_mine_answering_an_attack`,
        // `test_the_pact_does_nothing_when_the_explosion_did_not_react`.
        var source = Printed("Powers/Prototype/KleeOverhaulPowers.cs");
        Assert.Contains("cardSource is not { Type: CardType.Attack }", source);

        var restore = Il.Calls(Il.Method("VermillionPactPower", "Restore"));
        Assert.Contains(restore, c => c.Contains("AuraCmd.Find"));
        Assert.Contains(restore, c => c.Contains("AuraCmd.Apply"));
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
                     // Long Fuse and Kindling were cut at R276.
                     "ProtoKoAllOfMyTreasures",
                     "ProtoKoFishBlasting", "ProtoKoPocketMatch",
                     "ProtoKoBombsAway", "ProtoKoFlashPoint",
                     "ProtoKoVermillionPact", "ProtoKoSplitCharge",
                 })
        {
            Assert.Contains(slice, c => c.Contains(row));
            Assert.DoesNotContain(starter, c => c.Contains(row));
        }
    }

    [Fact]
    public void Fish_blasting_shuffles_its_status_into_the_draw_pile()
    {
        // The third `add_card` zone, and the position is the point: SHUFFLED
        // IN (`CardPilePosition.Random`) rather than laid on the bottom, which
        // is the parameter's default. The whole cost of the Status is that the
        // player does not know when it will arrive. Twin:
        // `test_fish_blasting_shuffles_a_confiscated_into_the_draw_pile`.
        var source = Printed("Cards/Prototype/Generated/ProtoKoFishBlasting.cs");
        Assert.Contains("PileType.Draw, Owner, CardPilePosition.Random",
                        source);

        // And it does NOT Set off: plain pressure, which is what separates it
        // from every detonator beside it.
        Assert.DoesNotContain(
            Il.Calls(Il.Method("ProtoKoFishBlasting", "OnPlay")),
            c => c.Contains("SetOff"));
    }

    [Fact]
    public void Bombs_away_is_the_attack_placer_the_smoggy_reading_asked_for()
    {
        // Smoggy allows one SKILL per turn, and the arm's placers are Skills
        // by rule -- so the shelf needed a placer that is not one. It hits
        // ALL and places on ALL, and it sets nothing off.
        var card = new ProtoKoBombsAway();
        Assert.Equal(CardType.Attack, card.Type);
        Assert.Equal(TargetType.AllEnemies, card.TargetType);

        var play = Il.Calls(Il.Method("ProtoKoBombsAway", "OnPlay"));
        Assert.Contains(play, c => c.Contains("ProtoBombPower.PlaceOnAll"));
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
