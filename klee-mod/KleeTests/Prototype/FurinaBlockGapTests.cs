using System.IO;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE BLOCK GAP (2026-10-09,
/// <c>review/records/furina-drain-line-round-2026-10-09.md</c> pick 2;
/// [USER]: "Yeah, agreed - let's plug the block gap now"): Velvet Curtain,
/// Private Box, The Masquerade and The Show Must Go On. Sim twin:
/// <c>tier0/tests/test_furina_block_gap.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaBlockGapTests
{
    private static void Run(System.Threading.Tasks.Task task) =>
        StageKit.Run(task);

    private static CardModel Upgraded(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, null);
        return card;
    }

    private static string Generated(string type) => File.ReadAllText(
        Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode", "Cards",
                     "Prototype", "Generated", type + ".cs"));

    private static string Face(CardModel card) =>
        ((BaseLib.Abstracts.CustomCardModel)card).Localization!
            .Single(r => r.Item1 == "description").Item2;

    /// <summary>The CalculatedBlockVar's multiplier, read for
    /// <paramref name="card"/>: the count the face's "(Gains N Block)" and
    /// the play both multiply by.</summary>
    private static decimal Multiplier(CardModel card)
    {
        var calculated = card.DynamicVars.CalculatedBlock;
        for (var t = calculated.GetType(); t != null; t = t.BaseType)
        {
            foreach (var field in t.GetFields(HeadlessGame.All))
            {
                if (field.GetValue(calculated) is System.Delegate d
                    && d.Method.GetParameters().Length == 2)
                {
                    return System.Convert.ToDecimal(
                        d.DynamicInvoke(card, null));
                }
            }
        }
        throw new System.InvalidOperationException(
            "CalculatedBlockVar carries no multiplier delegate");
    }

    /// <summary>The Block the card's formula gives: base plus extra per
    /// count, before Dexterity and Frail (the game's CalculatedBlockVar
    /// applies those, as for any card Block).</summary>
    private static decimal Formula(CardModel card) =>
        card.DynamicVars.CalculationBase.BaseValue
        + card.DynamicVars.CalculationExtra.BaseValue * Multiplier(card);

    private static CardModel Owned(CardModel card, Seat seat)
    {
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    // ---- the pool ------------------------------------------------------------

    [Fact]
    public void The_four_are_in_her_pool_at_their_ruled_rarities_and_costs()
    {
        var pool = ArmPools.Named("KleeMod.Powers.FurinaStageRoster", "Pool");
        foreach (var (type, rarity, cost, kind) in new[]
                 {
                     (typeof(ProtoFsVelvetCurtain), CardRarity.Common, 1,
                      CardType.Skill),
                     (typeof(ProtoFsPrivateBox), CardRarity.Uncommon, 1,
                      CardType.Skill),
                     (typeof(ProtoFsTheMasquerade), CardRarity.Uncommon, 1,
                      CardType.Power),
                     (typeof(ProtoFsTheShowMustGoOn), CardRarity.Rare, 2,
                      CardType.Skill),
                 })
        {
            var card = pool.Single(c => c.GetType() == type);
            Assert.Equal((rarity, cost, kind),
                         (card.Rarity, card.EnergyCost.Canonical, card.Type));
        }
        Assert.Contains("EnergyCost.UpgradeBy(-1)",
                        Generated("ProtoFsTheMasquerade"));
        Assert.Contains("EnergyCost.UpgradeBy(-1)",
                        Generated("ProtoFsTheShowMustGoOn"));
    }

    // ---- Velvet Curtain ------------------------------------------------------

    [Fact]
    public void Velvet_curtain_gains_7_block_and_2_fanfare_through_the_gain()
    {
        var card = new ProtoFsVelvetCurtain();
        Assert.Equal(7m, card.DynamicVars.Block.BaseValue);
        Assert.Equal(2m, card.DynamicVars[FurinaCards.AmountVar].BaseValue);
        var up = Upgraded(new ProtoFsVelvetCurtain());
        Assert.Equal(10m, up.DynamicVars.Block.BaseValue);
        Assert.Equal(3m, up.DynamicVars[FurinaCards.AmountVar].BaseValue);
        // Its Fanfare is the ledger's gain, Universal Revelry's path.
        Assert.Contains("await FurinaCards.GainFanfare(",
                        Generated("ProtoFsVelvetCurtain"));
        Assert.Contains("FurinaStage.Gain",
            Il.Calls(Il.Method("FurinaCards", "GainFanfare")));
        // A gain counts as gained Fanfare.
        var kit = StageKit.Of();
        kit.Director.Gain(2, FurinaCards.CardGainSource);
        Assert.Equal(2, kit.Stage.Fanfare);
        Assert.Equal(2, kit.Stage.GainedThisTurn);
    }

    // ---- Private Box ---------------------------------------------------------

    [Fact]
    public void Private_box_gains_5_with_no_guest_and_14_with_three()
    {
        FurinaStageLedger.ResetAll();
        var seat = Seat.Furina(78).WithCombatState();
        var card = Owned(new ProtoFsPrivateBox(), seat);
        Assert.Equal(5m, Formula(card));
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Seat(StagePerformer.Charlotte);
        stage.Seat(StagePerformer.Lynette);
        stage.Seat(StagePerformer.Clorinde);
        Assert.Equal(3m, Multiplier(card));
        Assert.Equal(14m, Formula(card));
        // Upgraded: 7, plus 4 each -- 19 with three.
        var up = Owned(Upgraded(new ProtoFsPrivateBox()), seat);
        Assert.Equal(19m, Formula(up));
        // The live preview, "(Gains N Block)", and card Block (Dexterity
        // and Frail apply): the game's CalculatedBlockVar on ValueProp.Move.
        Assert.Contains("(Gains {CalculatedBlock:diff()} [gold]Block[/gold])",
                        Face(card));
        Assert.Contains("new CalculatedBlockVar(ValueProp.Move)",
                        Generated("ProtoFsPrivateBox"));
        FurinaStageLedger.ResetAll();
    }

    // ---- The Masquerade ------------------------------------------------------

    [Fact]
    public void The_masquerade_pays_the_hp_drained_past_the_line_too()
    {
        // Entered at 78: the line is 59. At 60 HP a Drain 4 goes 3 past it.
        var kit = new StageKit(new StageMods { Masquerade = 1 }, 0, 60, 78);
        Assert.True(StageKit.Run(kit.Director.Drain(4)));
        Assert.Equal(3, kit.Stage.DrainedPast);
        Assert.Contains("block 4", kit.Board.Log);
    }

    [Fact]
    public void The_masquerade_pays_a_guest_acts_drain_stopped_at_the_line()
    {
        // Line 49 with Lyney on stage; at 50 HP his Drain 2 has room for 1.
        var kit = new StageKit(new StageMods { Masquerade = 1 }, 0, 50, 78,
                               StagePerformer.Lyney);
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.Equal(1, kit.Stage.Drained);
        Assert.Contains("block 1", kit.Board.Log);
        Assert.DoesNotContain("block 2", kit.Board.Log);
        // At the line: no Drain, so no Block.
        kit.Board.Log.Clear();
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.DoesNotContain(kit.Board.Log, l => l.StartsWith("block "));
    }

    [Fact]
    public void Two_masquerades_pay_twice_and_none_pays_nothing()
    {
        var two = new StageKit(new StageMods { Masquerade = 2 }, 0, 78, 78);
        Assert.True(StageKit.Run(two.Director.Drain(3)));
        Assert.Contains("block 6", two.Board.Log);
        var none = StageKit.Of();
        Assert.True(StageKit.Run(none.Director.Drain(3)));
        Assert.DoesNotContain(none.Board.Log, l => l.StartsWith("block "));
        // The power the card applies is the one the rules read.
        Assert.Contains("PowerCmd.Apply<TheMasqueradePower>",
                        Generated("ProtoFsTheMasquerade"));
    }

    // ---- The Show Must Go On -------------------------------------------------

    [Fact]
    public void The_show_must_go_on_gains_block_equal_to_fanfare_and_spends_none()
    {
        FurinaStageLedger.ResetAll();
        var seat = Seat.Furina(78).WithCombatState();
        var card = Owned(new ProtoFsTheShowMustGoOn(), seat);
        Assert.Equal(0m, Formula(card));
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Gain(12);
        Assert.Equal(12m, Formula(card));
        // Reading the bank leaves it whole: the play spends nothing.
        Assert.Equal(12, FurinaStage.FanfareOf(seat.Creature));
        var src = Generated("ProtoFsTheShowMustGoOn");
        Assert.DoesNotContain("FurinaStage.Spend", src);
        Assert.Contains("(Gains {CalculatedBlock:diff()} [gold]Block[/gold])",
                        Face(card));
        Assert.Contains("new CalculatedBlockVar(ValueProp.Move)", src);
        FurinaStageLedger.ResetAll();
    }
}
