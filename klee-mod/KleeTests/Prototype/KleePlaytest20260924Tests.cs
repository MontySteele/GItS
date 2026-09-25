using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The owner's co-op playtest of 2026-09-24 (build 0.2.3737+proto; arms Klee,
/// Companion, Kokomi and Furina Stage): Pocket Match's new design, Boom
/// Badge's doubling, Spark Knight's cost and reach, the two Companion rows that
/// had no upgrade, and Hair Trigger's Mines.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on <see cref="KleeR276BatchTests"/>'
/// terms. The picks (which charge, what factor) and the Mine conversion are
/// pure and run against real piles. An explosion needs a live combat, so the
/// order of the calls around it is pinned off the compiled methods and says
/// so. The end-to-end arithmetic is the sim twin's:
/// <c>tier0/tests/test_klee_playtest_2026_09_24.py</c>.
///
/// NO NUMBER HERE IS QUOTABLE (R215 B): every one is a starting value.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleePlaytest20260924Tests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, new object?[] { });
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    // ---- Pocket Match ----------------------------------------------------

    [Fact]
    public void Pocket_match_is_a_free_retained_common_with_no_spark_price()
    {
        var card = new ProtoKoPocketMatch();
        Assert.Equal(CardRarity.Common, card.Rarity);
        Assert.Equal(CardType.Attack, card.Type);
        Assert.Equal(0, card.EnergyCost.Canonical);
        Assert.Contains(CardKeyword.Retain, card.CanonicalKeywords);
        Assert.False(card is ISparkPricedCard);
        Assert.Equal(
            "[gold]Set off[/gold] only your largest [gold]Bomb[/gold] on the "
          + "enemy. Deal {Damage:diff()} damage.",
            Face(card));
        Assert.Equal(3m, card.DynamicVars.Damage.BaseValue);
        Assert.Equal(5m, Upgraded<ProtoKoPocketMatch>().DynamicVars.Damage.BaseValue);
    }

    [Fact]
    public void Pocket_match_is_a_set_off_card_to_every_reader()
    {
        // ISetOffCard is what Once More!, Boom Badge, Grounded, Patience Klee!,
        // Where Did I Put It? and Treasure Map read (`KleeExpansion.IsSetOffCard`).
        Assert.True(new ProtoKoPocketMatch() is ISetOffCard);
        Assert.True(KleeExpansion.IsSetOffCard(new ProtoKoPocketMatch()));

        // And its entry point takes the Once More! / Grounded note and the
        // Boom Badge exactly as the whole-pile Set off does, before the
        // explosion and before the card's own hit.
        var seq = Il.CallSequence(Il.Method("ProtoBombPower", "SetOffLargestAimed"))
            .ToList();
        var note = seq.IndexOf("KleeOverhaulLedger.NoteSetOffCardPlayed");
        var badge = seq.IndexOf("BoomBadgePower.Spend");
        var take = seq.IndexOf("ProtoBombPower.SetOffLargest");
        var hit = seq.IndexOf("ProtoBombPower.DealCardDamage");
        Assert.True(note >= 0 && badge > note && take > badge && hit > take,
                    string.Join(", ", seq));
        Assert.Contains("ProtoBombPower.SetOffLargestAimed",
                        Il.Calls(Il.Method("ProtoKoPocketMatch", "OnPlay")));
    }

    [Fact]
    public void Pocket_match_picks_the_largest_charge_and_the_oldest_on_a_tie()
    {
        // REAL: the pick. 4, 9, 6 -> the 9 (index 1); 7, 3, 7 -> the FIRST 7.
        var klee = Seat.Klee();
        var a = Seat.Klee(200).Creature;
        var b = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, a, b);

        var pile = ProtoBombs.Place(a, klee.Creature,
            new ProtoBombs.Charge(4), new ProtoBombs.Charge(9),
            new ProtoBombs.Charge(6));
        Assert.Equal(1, pile.LargestIndex());

        var tie = ProtoBombs.Place(b, klee.Creature,
            new ProtoBombs.Charge(7, IsMine: true), new ProtoBombs.Charge(3),
            new ProtoBombs.Charge(7));
        Assert.Equal(0, tie.LargestIndex());

        // The take leaves every other charge where it was, in order.
        var taken = pile.TakeAt(pile.LargestIndex());
        Assert.Equal(9, taken!.Value.Size);
        Assert.Equal(new[] { 4, 6 }, pile.Charges.Select(c => c.Size));

        // An empty pile has no largest charge.
        Assert.Equal(-1, ProtoBombs.Place(Seat.Klee(50).Creature, klee.Creature)
                                   .LargestIndex());
    }

    [Fact]
    public void Pocket_matchs_one_charge_is_a_normal_explosion()
    {
        // STRUCTURAL (an explosion needs a live combat): ONE take, then the
        // same `Explode` every rule is priced in -- its Spark, Explosive Frags
        // and Second Surprise ride that -- and the sweep that makes the charges
        // left behind jump when the explosion killed. It SPENDS The Big One's
        // multiplier, as a card's Set off does, rather than peeking it like a
        // Mine.
        var seq = Il.CallSequence(Il.Method("ProtoBombPower", "SetOffLargest"))
            .ToList();
        var pick = seq.IndexOf("ProtoBombPower.LargestIndex");
        var take = seq.IndexOf("ProtoBombPower.TakeAt");
        var mult = seq.IndexOf("KleeOverhaulLedger.TakeMultiplier");
        var boom = seq.IndexOf("ProtoBombPower.Explode");
        var sweep = seq.LastIndexOf("ProtoBombPower.SweepJumps");
        Assert.True(pick >= 0 && take > pick && mult > take && boom > mult
                    && sweep > boom, string.Join(", ", seq));
        Assert.DoesNotContain("KleeOverhaulLedger.PeekMultiplier", seq);
        Assert.DoesNotContain("ProtoBombPower.TakeAll", seq);
    }

    // ---- Boom Badge ------------------------------------------------------

    [Fact]
    public void Boom_badge_prints_the_doubling()
    {
        var card = new ProtoKoBoomBadge();
        Assert.Equal(
            "The next time you [gold]Set off[/gold] this turn, your "
          + "[gold]Bombs[/gold] deal double damage.",
            Face(card));
        Assert.Equal(0, card.EnergyCost.Canonical);
        Assert.Equal(2, card.PrintedSparkPrice);
        Assert.Equal(1, Upgraded<ProtoKoBoomBadge>().PrintedSparkPrice);
    }

    [Fact]
    public void Boom_badge_doubles_per_copy_and_with_the_big_one_makes_eight()
    {
        // REAL: the factor. None up is 1; one badge is x2; two badges are two
        // sentences about the same next Set off, x4.
        Assert.Equal(1, BoomBadgePower.FactorFor(0));
        Assert.Equal(2, BoomBadgePower.FactorFor(1));
        Assert.Equal(4, BoomBadgePower.FactorFor(2));

        // With no badge on her, Spend is a 1 and moves nothing.
        var klee = Seat.Klee();
        Assert.Equal(1, BoomBadgePower.Spend(klee.Creature).GetAwaiter().GetResult());
        Assert.Equal(1, BoomBadgePower.Spend(null).GetAwaiter().GetResult());

        // THE BIG ONE MEETS THE BADGE AT x8: the ledger's armed multiplier and
        // the badge's factor are MULTIPLIED where the pile is taken. The Big
        // One arms 4 (its row's own number); SetOff reads it back with
        // TakeMultiplier and multiplies the badge in.
        KleeOverhaulLedger.ResetAll();
        var ledger = KleeOverhaulLedger.For(klee.Creature);
        ledger.ArmMultiplier(4);
        Assert.Equal(8, ledger.TakeMultiplier() * BoomBadgePower.FactorFor(1));
        Assert.Equal(1, ledger.TakeMultiplier());
        KleeOverhaulLedger.ResetAll();

        var setOff = Il.CallSequence(Il.Method("ProtoBombPower", "SetOff")).ToList();
        Assert.Contains("KleeOverhaulLedger.TakeMultiplier", setOff);
        Assert.Contains("KleeOverhaulLedger.ArmMultiplier",
                        Il.Calls(Il.Method("ProtoKoTheBigOne", "OnPlay")));
    }

    [Fact]
    public void Boom_badge_is_spent_by_every_card_facing_set_off_and_never_by_a_mine()
    {
        // STRUCTURAL: once per entry point, so one Set off card (Tinder Toss on
        // ALL enemies, Rapid Fire's rolls) shares the one doubling.
        foreach (var entry in new[]
                 {
                     "SetOffAimed", "SetOffAimedBouncing", "SetOffAll",
                     "SetOffRandom", "SetOffAllThenHit", "SetOffLargestAimed",
                 })
        {
            Assert.Contains("BoomBadgePower.Spend",
                            Il.Calls(Il.Method("ProtoBombPower", entry)));
        }
        // A Mine answering an attack is not a Set off.
        Assert.DoesNotContain("BoomBadgePower.Spend",
                              Il.Calls(Il.Method("ProtoBombPower", "BeforeDamageReceived")));
        // The replay surface is gone: the badge no longer plays a card twice.
        Assert.Null(typeof(BoomBadgePower).GetMethod(
            "ModifyCardPlayCount",
            System.Reflection.BindingFlags.Public
          | System.Reflection.BindingFlags.Instance
          | System.Reflection.BindingFlags.DeclaredOnly));
        Assert.Contains("PowerCmd.Remove",
                        Il.Calls(Il.Method("BoomBadgePower", "AfterSideTurnEnd")));
    }

    // ---- Spark Knight ----------------------------------------------------

    [Fact]
    public void Spark_knight_costs_one_and_hits_all_enemies_for_three()
    {
        var card = new ProtoKoSparkKnight();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(
            "Whenever you gain a [gold]Spark[/gold], deal {PowerAmount:diff()} "
          + "damage to ALL enemies.",
            Face(card));
        Assert.Equal(3m, card.DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal(4m, Upgraded<ProtoKoSparkKnight>().DynamicVars["PowerAmount"].BaseValue);
        // No random roll any more: every living enemy is hit.
        Assert.DoesNotContain(
            Il.Calls(Il.Method("SparkKnightPower", "AfterSparksGained")),
            c => c.Contains("NextItem"));
    }

    // ---- the two Companion rows that had no upgrade ----------------------

    [Fact]
    public void Lisa_violet_arc_and_sucrose_gust_upgrade_to_draw_two()
    {
        Assert.Equal(1m, new ProtoMcLisaVioletArc().DynamicVars.Cards.BaseValue);
        Assert.Equal(2m, Upgraded<ProtoMcLisaVioletArc>().DynamicVars.Cards.BaseValue);
        Assert.Equal(1m, new ProtoMcSucroseGust().DynamicVars.Cards.BaseValue);
        Assert.Equal(2m, Upgraded<ProtoMcSucroseGust>().DynamicVars.Cards.BaseValue);
        Assert.Contains("{Cards:diff()}", Face(new ProtoMcLisaVioletArc()));
        Assert.Contains("{Cards:diff()}", Face(new ProtoMcSucroseGust()));
    }

    // ---- Hair Trigger's Mines (the playtest's investigation) -------------

    [Fact]
    public void Hair_trigger_converts_every_charge_so_an_attack_takes_them_all()
    {
        // REAL, on the pile the owner described: three charges -- one placed
        // plain, one that arrived by a merge (a Mine already), one carrying
        // Jumpy Dumpty's rider -- all become Mines, and the take an enemy's
        // attack on HER makes (`BeforeDamageReceived` -> `TakeMines`) empties
        // the whole pile. Nothing is left behind as a plain Bomb.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, enemy);
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(5),
            new ProtoBombs.Charge(12, IsMine: true),
            new ProtoBombs.Charge(8, PayloadMineAll: 3));

        ProtoBombPower.MineAllOn(enemy, klee.Creature);
        Assert.All(pile.Charges, c => Assert.True(c.IsMine));

        var fired = pile.TakeMines();
        Assert.NotNull(fired);
        Assert.Equal(new[] { 5, 12, 8 }, fired!.Select(c => c.Size));
        Assert.Equal(3, fired.Last().PayloadMineAll);
        Assert.Empty(pile.Charges);

        // And the take above is the only thing the hook does with the pile,
        // before the explosions.
        var hook = Il.CallSequence(Il.Method("ProtoBombPower", "BeforeDamageReceived"))
            .ToList();
        Assert.True(hook.IndexOf("ProtoBombPower.TakeMines")
                    < hook.IndexOf("ProtoBombPower.Explode"));
    }

    // ---- Mines in co-op (the owner, 2026-09-25, "pick a") ----------------

    private static ValueProp Attack => ValueProp.Move;
    private static ValueProp Explosion => ValueProp.Unpowered;

    [Fact]
    public void A_mine_answers_its_enemys_attack_on_any_player()
    {
        // REAL: the trigger. "A Mine goes off just before ITS enemy's attack
        // lands on ANY player, not only on the Klee who placed it."
        var klee = Seat.Klee();
        var furina = Seat.Furina();
        var enemy = Seat.Klee(200).Creature;
        var other = Seat.Klee(200).Creature;

        // Single player: unchanged -- her enemy's attack on her fires it.
        Assert.True(ProtoBombPower.AnswersAttack(
            enemy, klee.Creature, klee.Creature, enemy, Attack));
        // THE RULING: the same enemy's attack on her ally fires it too.
        Assert.True(ProtoBombPower.AnswersAttack(
            enemy, klee.Creature, furina.Creature, enemy, Attack));

        // Still THIS enemy's hit, and still a powered attack.
        Assert.False(ProtoBombPower.AnswersAttack(
            enemy, klee.Creature, furina.Creature, other, Attack));
        Assert.False(ProtoBombPower.AnswersAttack(
            enemy, klee.Creature, klee.Creature, null, Attack));
        Assert.False(ProtoBombPower.AnswersAttack(
            enemy, klee.Creature, furina.Creature, enemy, Explosion));
        // A pile nobody placed answers nothing.
        Assert.False(ProtoBombPower.AnswersAttack(
            enemy, null, klee.Creature, enemy, Attack));
    }

    [Fact]
    public void An_allys_mine_still_pays_the_klee_who_placed_it()
    {
        // STRUCTURAL (an explosion needs a live combat): the explosion is the
        // pile's -- `Explode` is handed the pile's own `Applier`, and the
        // ledger it notes on is hers -- so the Spark, Look Out!'s Block and
        // Explosive Frags pay the Klee who placed it whoever was hit. The
        // target the hook was handed is used for one thing only: the EB-336
        // note of whose hit was pre-empted.
        var hook = Il.CallSequence(Il.Method("ProtoBombPower", "BeforeDamageReceived"))
            .ToList();
        Assert.Contains(hook, c => c.EndsWith(".get_Applier"));
        Assert.Contains("KleeOverhaulLedger.For", hook);
        Assert.True(hook.IndexOf("ProtoBombPower.AnswersAttack")
                    < hook.IndexOf("ProtoBombPower.TakeMines"));
        Assert.Contains("Preempted.Note", hook);
    }

    [Fact]
    public void A_lethal_mine_cancels_the_hit_on_the_ally()
    {
        // REAL, both hooks that can move the number after the Mine: the Klee
        // arm's sweep zeroes the HP, and Furina's own damage pipeline -- her
        // Encore buffer, or under the Stage her lead performer's Fanfare --
        // takes nothing from a hit that never happened, whichever of the two
        // listeners the engine asks first.
        var klee = Seat.Klee();
        var furina = Seat.Furina();
        var attacker = Seat.Klee(4).Creature;
        KleeOverhaul.Enabled = true;
        ProtoBombPower.Preempted.Clear();
        try
        {
            Seat.Set(attacker, "CurrentHp", 0);
            ProtoBombPower.Preempted.Note(furina.Creature, attacker);

            var sweep = (KleeOverhaulSweepHooks)System.Runtime.CompilerServices
                .RuntimeHelpers.GetUninitializedObject(typeof(KleeOverhaulSweepHooks));
            Assert.Equal(0m, sweep.ModifyHpLostBeforeOsty(
                furina.Creature, 8m, Attack, attacker, cardSource: null));

            var hers = (FurinaResourceHooks)System.Runtime.CompilerServices
                .RuntimeHelpers.GetUninitializedObject(typeof(FurinaResourceHooks));
            Assert.Equal(0m, hers.ModifyHpLostBeforeOsty(
                furina.Creature, 8m, Attack, attacker, cardSource: null));

            // Not Klee's hit, so Klee's own is untouched by the note.
            Assert.Equal(8m, sweep.ModifyHpLostBeforeOsty(
                klee.Creature, 8m, Attack, attacker, cardSource: null));
        }
        finally
        {
            ProtoBombPower.Preempted.Clear();
            KleeOverhaul.Enabled = KleeOverhaul.DefaultEnabled;
        }
    }
}
