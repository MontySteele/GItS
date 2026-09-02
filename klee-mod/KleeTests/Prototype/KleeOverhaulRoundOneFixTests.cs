using System;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KLEE OVERHAUL, ROUND ONE: the four things the two blind testers could not
/// read, and the sentence the wire had for none of them.
///
///   * <c>EB-260</c> -- the Bomb face ended "never goes off by itself" over a
///     stack holding Mines, which answer the enemy's attack. Read as a
///     contradiction twice (`klee-overhaul-r1-codex-b`, fights 4 and 5) and
///     once more by the other tester.
///   * <c>EB-265</c> -- the same face's damage number ignored Strength while
///     the set-off applied it per Bomb: printed 10, dealt 14
///     (`klee-overhaul-r1-opus`, fight 2), "the one number I learned not to
///     trust".
///   * <c>EB-261</c> -- Quick Fuse was playable on a Bomb-less board, spent
///     the Spark and did nothing (`klee-overhaul-r1-codex-b`, fight 3).
///   * <c>EB-264</c>, the klee-mod half -- every mod-side refusal reaches the
///     wire as the bare enum <c>BlockedByCardLogic</c>, so the page printed a
///     token instead of a reason.
///   * <c>EB-266</c> -- a reaction under the arm put <i>Burst: 5</i> on screen,
///     a meter with no card that reads it and no rule for spending it.
///
/// WHAT IS REAL HERE. All of it. The faces are strings on the power, the
/// prediction is arithmetic on a real pile against real Strength, the board
/// question is asked of the game's own <c>CombatState</c> built by its own
/// constructor, and the Burst gate is exercised through the funnel every gain
/// site goes through. Nothing is mocked and nothing is faked past.
///
/// THE COLLECTION IS LOAD-BEARING. <c>KleeOverhaul.Enabled</c> is one static
/// for the whole process; the arm tests below move it, and
/// <c>KleeOverhaulRuleTests.The_arm_ships_off</c> reads it. Sharing a
/// collection with that class is what keeps xunit from running the two at
/// once.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeOverhaulRoundOneFixTests
{
    // ---- EB-260: the face and the Mine clause ---------------------------

    private static string Row(ProtoBombPower pile, string key) =>
        pile.Localization!.First(r => r.Item1 == key).Item2;

    private static string LocKey(ProtoBombPower pile) =>
        (string)typeof(ProtoBombPower)
            .GetProperty("SmartDescriptionLocKey", HeadlessGame.All)!
            .GetValue(pile)!;

    [Fact]
    public void A_bomb_only_stack_prints_the_face_with_no_mine_clause()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(4), new ProtoBombs.Charge(6));

        Assert.Equal(0, pile.MineCount);
        Assert.EndsWith(".smartDescription", LocKey(pile));
        Assert.DoesNotContain("Mine also goes off", Row(pile, "smartDescription"));
    }

    [Fact]
    public void A_stack_holding_a_mine_prints_rule_sixs_sentence()
    {
        // The whole of EB-260: the clause the tooltip always carried, on the
        // face the wire actually prints, and only while it is true.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(4), new ProtoBombs.Charge(6, IsMine: true));

        Assert.Equal(1, pile.MineCount);
        Assert.EndsWith(".smartDescriptionMines", LocKey(pile));

        var face = Row(pile, "smartDescriptionMines");
        Assert.Contains("[gold]Mine[/gold] also goes off when this enemy "
                        + "attacks you, before the hit lands.", face);
    }

    [Fact]
    public void The_mine_face_is_the_plain_face_plus_the_count_and_that_clause()
    {
        // The mutation guard on both rows at once: they may not drift into two
        // descriptions of the same power. `EB-287` moved the Mine COUNT out of
        // the old parenthetical and into the sentence that counts the Bombs,
        // so the mined row differs in exactly two places instead of one -- and
        // this says which two by subtracting them and demanding what is left
        // be the plain row, character for character.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(4, IsMine: true));

        var mined = Row(pile, "smartDescriptionMines");
        Assert.Equal(
            Row(pile, "smartDescription"),
            mined.Replace(", including {Mines} [gold]Mine{Mines:plural:|s}[/gold]",
                          string.Empty)
                 .Replace(" A [gold]Mine[/gold] also goes off when this enemy "
                          + "attacks you, before the hit lands.", string.Empty));
        // And the static tooltip carries the identical sentence -- one clause,
        // two surfaces, which is what stopped them disagreeing in the first
        // place.
        Assert.EndsWith(
            "[gold]Mine[/gold] also goes off when this enemy attacks you, "
            + "before the hit lands.", Row(pile, "description"));
    }

    [Fact]
    public void The_face_follows_the_pile_when_the_last_mine_fires()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(4), new ProtoBombs.Charge(6, IsMine: true));

        Assert.EndsWith(".smartDescriptionMines", LocKey(pile));
        pile.TakeMines();
        Assert.EndsWith(".smartDescription", LocKey(pile));
    }

    // ---- EB-265: the number the set-off will actually deal ---------------

    /// <summary>The face's number, read the two ways SmartFormat can reach a
    /// DynamicVar: <c>ToString()</c> (what the default formatter writes) and
    /// <c>IConvertible</c> (what the numeric formatters convert).</summary>
    private static (int text, int converted) FaceSize(ProtoBombPower pile)
    {
        var var = pile.DynamicVars["Size"];
        return (int.Parse(var.ToString()), Convert.ToInt32(var));
    }

    [Theory]
    [InlineData(0, 10)]   // two Bombs of 5: what the face always said
    [InlineData(2, 14)]   // the tester's board: printed 10, dealt 14
    public void The_face_prints_the_total_the_set_off_will_deal(
        int strength, int dealt)
    {
        var klee = Seat.Klee();
        if (strength > 0) klee.WithPower<StrengthPower>(strength);
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(5));
        // Through the power's own mutator, so the STORED fallback is written
        // by the real SyncDisplay rather than seeded by the harness.
        pile.AddCharge(new ProtoBombPower.ProtoCharge(5, false, 0));

        // Against the pipeline the explosion itself runs, per charge, exactly
        // as ProtoBombPower.Explode calls it -- not against a number retyped
        // here.
        var perCharge = SimDamagePipeline.Resolve(klee.Creature, enemy, 5, 1m);
        Assert.Equal(dealt, perCharge * 2);

        Assert.Equal(dealt, pile.PredictedSetOffDamage());
        Assert.Equal((dealt, dealt), FaceSize(pile));
        Assert.Equal(dealt, (int)pile.DynamicVars["Size"].BaseValue);
    }

    [Fact]
    public void The_printed_number_is_no_longer_the_raw_pile_size()
    {
        // The mutation guard: put TotalSize back on the face and this fails.
        var klee = Seat.Klee().WithPower<StrengthPower>(2);
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(5), new ProtoBombs.Charge(5));

        Assert.Equal(10, pile.TotalSize);
        Assert.Equal(10, pile.DisplayAmount);      // the badge is unchanged
        Assert.Equal(14, pile.PredictedSetOffDamage());
    }

    [Fact]
    public void The_face_is_read_live_so_strength_gained_later_moves_it()
    {
        // Strength does not touch the pile, so a number STORED when the Bomb
        // was planted would be stale the moment Klee buffed herself -- the
        // same defect one turn later.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(5));
        pile.AddCharge(new ProtoBombPower.ProtoCharge(5, false, 0));

        Assert.Equal((10, 10), FaceSize(pile));
        Assert.Equal(10, (int)pile.DynamicVars["Size"].BaseValue);

        klee.WithPower<StrengthPower>(2);           // nothing touches the pile

        // The stored number is now the stale one, and the face does not read
        // it: this is why the var computes rather than remembers.
        Assert.Equal(10, (int)pile.DynamicVars["Size"].BaseValue);
        Assert.Equal((14, 14), FaceSize(pile));
    }

    [Fact]
    public void The_face_and_the_explosion_run_the_same_pipeline()
    {
        // The anti-drift lock. `ElementalHit.Deal` spells the three steps out
        // inline rather than calling `Resolve`, because
        // `tier0/tests/test_reaction_phase_parity.py` pins its TargetMods read
        // as happening after `ReactionEffects.Resolve`. So the two spellings
        // are held to the SAME two halves in the SAME order here instead.
        var deal = Il.CallSequence(Il.Method("ElementalHit", "Deal"))
            .Where(c => c.StartsWith("SimDamagePipeline.")).ToList();
        var resolve = Il.CallSequence(
                typeof(SimDamagePipeline).GetMethod(
                    nameof(SimDamagePipeline.Resolve), HeadlessGame.All)!)
            .Where(c => c.StartsWith("SimDamagePipeline.")).ToList();

        Assert.Equal(
            new[] { "SimDamagePipeline.DealerMods", "SimDamagePipeline.TargetMods" },
            deal);
        Assert.Equal(deal, resolve);

        // And the face is the ONE caller that asks for the whole chain.
        Assert.Contains("SimDamagePipeline.Resolve",
            Il.Calls(typeof(ProtoBombPower).GetMethod(
                nameof(ProtoBombPower.PredictedSetOffDamage), HeadlessGame.All)!));
    }

    [Fact]
    public void An_empty_pile_predicts_nothing()
    {
        var klee = Seat.Klee().WithPower<StrengthPower>(2);
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature);

        Assert.Equal(0, pile.PredictedSetOffDamage());
    }

    // ---- EB-261 / EB-264: Quick Fuse refuses, and says why ---------------

    private static ProtoKoQuickFuse QuickFuse(Seat seat)
    {
        var card = new ProtoKoQuickFuse();
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", seat.Player);
        return card;
    }

    private static bool Playable(CardModel card) =>
        (bool)typeof(CardModel)
            .GetProperty("IsPlayable", HeadlessGame.All)!
            .GetValue(card)!;

    [Fact]
    public void Quick_fuse_is_unplayable_on_a_bomb_less_board()
    {
        var klee = Seat.Klee().WithPower<SparkPower>(3);   // the bank is fine
        var enemy = Seat.Klee(30).Creature;
        ProtoBombs.Board(klee.Creature, enemy);

        Assert.False(ProtoBombPower.AnyPlacedBy(klee.Creature));
        Assert.False(Playable(QuickFuse(klee)));
    }

    [Fact]
    public void Quick_fuse_is_playable_once_any_enemy_holds_a_bomb()
    {
        var klee = Seat.Klee().WithPower<SparkPower>(3);
        var front = Seat.Klee(30).Creature;
        var back = Seat.Klee(30).Creature;
        ProtoBombs.Board(klee.Creature, front, back);
        var card = QuickFuse(klee);

        Assert.False(Playable(card));

        // ANY enemy, not the aimed one: IsPlayable is asked without a target.
        ProtoBombs.Place(back, klee.Creature, new ProtoBombs.Charge(3));

        Assert.True(ProtoBombPower.AnyPlacedBy(klee.Creature));
        Assert.True(Playable(card));
    }

    [Fact]
    public void An_emptied_pile_and_another_klees_pile_do_not_unlock_it()
    {
        var klee = Seat.Klee().WithPower<SparkPower>(3);
        var partner = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        ProtoBombs.Board(klee.Creature, enemy);

        // R205: the pile belongs to the Klee who placed it, and only she can
        // set it off -- so it is not hers to be made playable by.
        ProtoBombs.Place(enemy, partner.Creature, new ProtoBombs.Charge(4));
        Assert.False(ProtoBombPower.AnyPlacedBy(klee.Creature));

        var mine = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(4));
        Assert.True(ProtoBombPower.AnyPlacedBy(klee.Creature));

        mine.TakeAll();
        Assert.False(ProtoBombPower.AnyPlacedBy(klee.Creature));
    }

    [Fact]
    public void A_dead_enemys_bomb_does_not_keep_the_card_playable()
    {
        var klee = Seat.Klee().WithPower<SparkPower>(3);
        var enemy = Seat.Klee(30).Creature;
        ProtoBombs.Board(klee.Creature, enemy);
        ProtoBombs.Place(enemy, klee.Creature, new ProtoBombs.Charge(4));

        Assert.True(ProtoBombPower.AnyPlacedBy(klee.Creature));
        Seat.Set(enemy, "CurrentHp", 0);
        Assert.False(ProtoBombPower.AnyPlacedBy(klee.Creature));
    }

    [Fact]
    public void The_bomb_less_refusal_says_why_in_words()
    {
        // EB-264's channel. `CardModel.CanPlay` would report this as the bare
        // `BlockedByCardLogic`; this is the sentence the wire carries beside
        // it as `unplayable_reason_text`.
        var klee = Seat.Klee().WithPower<SparkPower>(3);
        var enemy = Seat.Klee(30).Creature;
        ProtoBombs.Board(klee.Creature, enemy);
        var card = QuickFuse(klee);

        Assert.Equal("no enemy is holding a Bomb",
                     KleeUnplayableReason.For(card));

        ProtoBombs.Place(enemy, klee.Creature, new ProtoBombs.Charge(4));
        Assert.Null(KleeUnplayableReason.For(card));
    }

    [Fact]
    public void A_spark_less_card_says_it_has_no_spark()
    {
        // The tester's own case: "Ka-pow! printed CANNOT BE PLAYED:
        // BlockedByCardLogic whenever I had 0 Spark ... the actual reason (you
        // have no Spark) is printed nowhere."
        var klee = Seat.Klee().WithPower<SparkPower>(0);
        var enemy = Seat.Klee(30).Creature;
        ProtoBombs.Board(klee.Creature, enemy);
        ProtoBombs.Place(enemy, klee.Creature, new ProtoBombs.Charge(4));
        var card = QuickFuse(klee);

        Assert.Equal("you have no Spark, and this costs 1",
                     KleeUnplayableReason.For(card));

        // A short bank that is not empty says how short it is.
        var kapow = new ProtoKoBangBang();          // prints 2
        Seat.Set(kapow, "IsMutable", true);
        Seat.Force(kapow, "Owner", klee.Player);
        klee.SetPowerAmount<SparkPower>(1);
        Assert.Equal("you have 1 Spark, and this costs 2",
                     KleeUnplayableReason.For(kapow));

        klee.SetPowerAmount<SparkPower>(2);
        Assert.Null(KleeUnplayableReason.For(kapow));
    }

    [Fact]
    public void A_card_with_nothing_to_say_says_nothing()
    {
        // The common answer, and the reason the wire key is omitted rather
        // than written empty.
        var klee = Seat.Klee().WithPower<SparkPower>(3);
        var enemy = Seat.Klee(30).Creature;
        ProtoBombs.Board(klee.Creature, enemy);
        ProtoBombs.Place(enemy, klee.Creature, new ProtoBombs.Charge(4));

        Assert.Null(KleeUnplayableReason.For(QuickFuse(klee)));
    }

    // ---- EB-266: the arm has one meter, and it is not Burst --------------

    private static object BurstResourceFor(Creature player) =>
        typeof(KleeBurstResource)
            .GetMethod("Find", HeadlessGame.All)!
            .Invoke(null, new object[] { player });

    [Fact]
    public async Task A_reaction_under_the_arm_leaves_burst_at_zero()
    {
        var klee = Seat.Klee().WithCombatState();
        var was = KleeOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = true;

            // The exact call ReactionEffects.Resolve makes for every named
            // reaction, at the amount it passes.
            await KleeBurstResource.Gain(
                null!, klee.Creature, BurstConstants.PerReaction, null);

            Assert.Equal(0, KleeBurstResource.AmountFor(klee.Creature));
            Assert.Null(BurstResourceFor(klee.Creature));
        }
        finally
        {
            KleeOverhaul.Enabled = was;
        }
    }

    [Fact]
    public void With_the_arm_off_the_shipped_meter_is_still_there()
    {
        // The mutation guard for the test above: with the arm off the very
        // same seat DOES have a meter, so what that one measured is the arm
        // and not a headless accident. Read only -- gaining outside the arm
        // reaches the Godot gauge, which the headless boundary forbids.
        //
        // The flag is set rather than assumed, because this project also
        // builds under `-p:KleeOverhaul=true`, where the default is the other
        // way round.
        var klee = Seat.Klee().WithCombatState();
        var was = KleeOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = false;
            Assert.NotNull(BurstResourceFor(klee.Creature));
        }
        finally
        {
            KleeOverhaul.Enabled = was;
        }
    }

    [Fact]
    public void The_reaction_funnel_still_asks_the_meter()
    {
        // The guard is at KleeBurstResource.Find, the one funnel every gain
        // and every read passes through -- NOT by deleting the reaction's
        // call, which would leave the other gain sites unguarded.
        var calls = Il.Calls(Il.Method("ReactionEffects", "Resolve"));

        Assert.Contains("KleeBurstResource.Gain", calls);
        Assert.Contains("KleeOverhaul.get_Enabled",
                        Il.Calls(typeof(KleeBurstResource)
                            .GetMethod("Find", HeadlessGame.All)!));
    }
}
