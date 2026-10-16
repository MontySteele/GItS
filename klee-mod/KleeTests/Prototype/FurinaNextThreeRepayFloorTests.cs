using System.IO;
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
/// FURINA-NEXT PAPER 3, BUILT (<c>review/active/furina-next-3-2026-10-16.md</c>,
/// ruled 2026-10-16, both picks (a)): "a Repay that cannot return all its HP
/// gains 1 Block for each HP it could not return, unless the card says
/// otherwise." Cleansing Torrent keeps its damage; "Repay all" has no
/// floor; the floors Hymn of Many Waters, Grand Entrance, Charlotte and
/// Sigewinne already paid apply once. Universal Revelry and Critics' Darling
/// read the HP returned, not the Block. Pneuma Refrain is Repay 4 [6];
/// Endless Waltz Repays 2 first; Fontaine Teardrop doubles the floor.
/// Sim twin: <c>tier0/tests/test_furina_next_3_repay_floor.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaNextThreeRepayFloorTests
{
    private static T Run<T>(System.Threading.Tasks.Task<T> task) =>
        StageKit.Run(task);

    private static void Run(System.Threading.Tasks.Task task) =>
        StageKit.Run(task);

    private static string Generated(string type) => File.ReadAllText(
        Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode", "Cards",
                     "Prototype", "Generated", type + ".cs")).Replace("\r\n", "\n");

    private static string Face(CardModel card) =>
        ((BaseLib.Abstracts.CustomCardModel)card).Localization!
            .Single(r => r.Item1 == "description").Item2;

    private static CardModel Upgraded(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        card.UpgradeInternal();
        return card;
    }

    private static string[] Blocks(StageKit kit) =>
        kit.Board.Log.Where(l => l.StartsWith("block")).ToArray();

    // ---- the rule: a card's Repay takes the Block floor by default --------

    [Fact]
    public void A_cards_repay_defaults_to_the_block_floor()
    {
        var repay = typeof(FurinaStage).GetMethod("Repay")!;
        var floor = repay.GetParameters().Single(p => p.Name == "floor");
        Assert.Equal(StageFloor.Block, (StageFloor)floor.DefaultValue!);
    }

    [Fact]
    public void Every_newly_covered_card_repays_with_the_default_floor()
    {
        foreach (var type in new[] { "ProtoFsPneumaRefrain", "ProtoFsCleanSlate",
                                     "ProtoFsEbbAndFlow", "ProtoFsRiptideLunge",
                                     "ProtoFsOusiaPneuma", "ProtoFsRisingTide" })
        {
            var src = Generated(type);
            Assert.Contains("await FurinaStage.Repay(choiceContext, Owner.Creature, ", src);
            Assert.DoesNotContain("StageFloor.", src);
        }
    }

    [Fact]
    public void A_repay_with_nothing_drained_pays_its_number_as_block()
    {
        var kit = StageKit.Of();
        Assert.Equal(0, Run(kit.Director.RepayFloor(4, StageFloor.Block)));
        Assert.Equal(new[] { "block 4" }, kit.Board.Log.ToArray());
    }

    [Fact]
    public void Salon_solitaire_pays_1_block_with_nothing_drained()
    {
        var kit = StageKit.Of();
        Run(kit.Director.EndOfTurn(1));
        Assert.Equal(new[] { "block 1" }, Blocks(kit));
        // With HP drained it returns it and pays no Block.
        kit = StageKit.Of();
        Run(kit.Director.Drain(1));
        kit.Board.Log.Clear();
        Run(kit.Director.EndOfTurn(1));
        Assert.Contains("heal 1", kit.Board.Log);
        Assert.Empty(Blocks(kit));
    }

    [Fact]
    public void Fountain_of_lucine_pays_the_floor_next_turn()
    {
        var kit = StageKit.Of();
        Run(kit.Director.Drain(1));
        kit.Stage.ScheduleRepay(3, 1);
        kit.Board.Log.Clear();
        Run(kit.Director.TurnStartRepays());
        Assert.Equal(new[] { "heal 1", "block 2" },
                     kit.Board.Log.Where(l => !l.StartsWith("cue")).ToArray());
    }

    // ---- the cards' numbers --------------------------------------------------

    [Fact]
    public void Pneuma_refrain_is_repay_4_6_draw_2()
    {
        Assert.Equal(4m, new ProtoFsPneumaRefrain().DynamicVars["RepayAmount"].BaseValue);
        Assert.Equal(6m, Upgraded(new ProtoFsPneumaRefrain())
                         .DynamicVars["RepayAmount"].BaseValue);
        Assert.Equal("[gold]Repay[/gold] {RepayAmount:diff()}. Draw 2 cards."
                     + "{InCombat:{StageRepay}|}",
                     Face(new ProtoFsPneumaRefrain()));
    }

    [Fact]
    public void Hymn_and_grand_entrance_drop_the_clause_and_pay_once()
    {
        Assert.Equal("Gain {Block:diff()} [gold]Block[/gold]. [gold]Repay[/gold] "
                     + "{RepayAmount:diff()}.{InCombat:{StageRepay}|}",
                     Face(new ProtoFsHymnOfManyWaters()));
        Assert.Equal("Whenever you play a Guest Star, [gold]Repay[/gold] "
                     + "{PowerAmount:diff()}.{InCombat:{StageRepay}|}",
                     Face(new ProtoFsGrandEntrance()));
        // One Repay call, the default floor: no second Block op.
        var hymn = Generated("ProtoFsHymnOfManyWaters");
        Assert.Single(System.Text.RegularExpressions.Regex.Matches(
            hymn, @"await FurinaStage\.Repay\(").Cast<object>());
    }

    [Fact]
    public void Charlotte_and_sigewinne_pay_their_floor_once()
    {
        var kit = StageKit.Of(StagePerformer.Charlotte);
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.Equal(new[] { "block 3" }, Blocks(kit));
        kit = StageKit.Of(StagePerformer.Sigewinne);
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.Equal(new[] { "block 3" }, Blocks(kit));
    }

    // ---- Endless Waltz ------------------------------------------------------

    /// <summary>Endless Waltz's play, as its generated OnPlay runs it: Repay
    /// 2 with the floor, then 6 plus 3 for each Repay that returned HP.
    /// Returns (damage, HP back, Block).</summary>
    private static (int, int, int) Waltz(int drained)
    {
        var kit = StageKit.Of();
        if (drained > 0) Run(kit.Director.Drain(drained));
        kit.Board.Log.Clear();
        var back = Run(kit.Director.RepayFloor(2, StageFloor.Block));
        var damage = 6 + 3 * kit.Stage.RepaysThisTurn;
        var block = Blocks(kit).Sum(l => int.Parse(l.Split(' ')[1]));
        return (damage, back, block);
    }

    [Fact]
    public void Endless_waltz_nothing_drained_6_damage_and_2_block()
    {
        Assert.Equal((6, 0, 2), Waltz(0));
    }

    [Fact]
    public void Endless_waltz_one_drained_9_damage_1_hp_1_block()
    {
        Assert.Equal((9, 1, 1), Waltz(1));
    }

    [Fact]
    public void Endless_waltz_two_or_more_drained_9_damage_2_hp()
    {
        Assert.Equal((9, 2, 0), Waltz(2));
        Assert.Equal((9, 2, 0), Waltz(5));
    }

    [Fact]
    public void Endless_waltz_repays_first_and_its_face_counts_its_own_repay()
    {
        var src = Generated("ProtoFsRisingTide");
        Assert.True(src.IndexOf("await FurinaStage.Repay(choiceContext, Owner.Creature, 2);",
                                System.StringComparison.Ordinal)
                    < src.IndexOf("await DamageCmd.Attack(",
                                  System.StringComparison.Ordinal));
        Assert.Contains("FurinaStage.RepaysThisTurnWith(card, 2)", src);
        Assert.StartsWith("[gold]Repay[/gold] 2. Deal {CalculationBase:diff()} damage",
                          Face(new ProtoFsRisingTide()));
        // The upgrade still adds 1 to the per-Repay bonus.
        Assert.Equal(3m, new ProtoFsRisingTide().DynamicVars.ExtraDamage.BaseValue);
        Assert.Equal(4m, Upgraded(new ProtoFsRisingTide())
                         .DynamicVars.ExtraDamage.BaseValue);
    }

    // ---- the other floors ---------------------------------------------------

    [Fact]
    public void Cleansing_torrent_keeps_its_damage_floor_and_pays_no_block()
    {
        Assert.Contains("Owner.Creature, 4, StageFloor.None);",
                        Generated("ProtoFsCleansingTorrent"));
        var kit = StageKit.Of();
        Run(kit.Director.RepayFloor(4, StageFloor.None));
        Assert.Empty(kit.Board.Log);
    }

    [Fact]
    public void Repay_all_gives_nothing_at_0()
    {
        var kit = StageKit.Of();
        Assert.Equal(0, Run(kit.Director.RepayAll()));
        Assert.Empty(kit.Board.Log);
    }

    // ---- the readers read HP returned, not Block ----------------------------

    [Fact]
    public void Revelry_and_critics_darling_read_no_block()
    {
        var kit = StageKit.With(new StageMods { Revelry = 1, CriticsDarling = 1 }, 0);
        Run(kit.Director.RepayFloor(4, StageFloor.Block));
        Assert.Equal(0, kit.Stage.Fanfare);
        Assert.DoesNotContain(kit.Board.Log, l => l.StartsWith("power"));
        Assert.Equal(new[] { "block 4" }, Blocks(kit));
        // With 1 drained: they read the 1 returned.
        kit = StageKit.With(new StageMods { Revelry = 1, CriticsDarling = 1 }, 0);
        Run(kit.Director.Drain(1));
        var before = kit.Stage.Fanfare;
        kit.Board.Log.Clear();
        Run(kit.Director.RepayFloor(4, StageFloor.Block));
        Assert.Equal(before + 2, kit.Stage.Fanfare);   // 1 Repay, 1 Revelry
        Assert.Contains("power Critics' Darling Random 1", kit.Board.Log);
        Assert.Contains("block 3", kit.Board.Log);
    }

    // ---- the text --------------------------------------------------------------

    [Fact]
    public void The_repay_tip_carries_the_rule_in_one_line()
    {
        const string Rule = "Any HP a Repay cannot return becomes [gold]Block[/gold].";
        var seat = (string)typeof(ArmKeywordTips)
            .GetField("RepayBody", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;
        Assert.EndsWith(Rule, seat);
        var bodies = typeof(ArmKeywordTips).Assembly
            .GetType("KleeMod.Cards.PlayerTips")!
            .GetField("Bodies", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null) as System.Collections.Generic.Dictionary<string, string>;
        Assert.Equal("Regain that much drained HP. " + Rule,
                     bodies![ArmKeywordTips.RepayKey]);
    }

    [Fact]
    public void The_preview_leads_with_the_block()
    {
        Assert.Equal("\n(Repay 0: gain 3 Block)",
                     FurinaStageFacePreview.Line(0, 3, FurinaStageFacePreview.PayBlock));
        Assert.Equal("\n(Repay 1: gain 2 Block)",
                     FurinaStageFacePreview.Line(1, 3, FurinaStageFacePreview.PayBlock));
        Assert.Equal("\n(Repays 3)",
                     FurinaStageFacePreview.Line(3, 3, FurinaStageFacePreview.PayBlock));
        Assert.Equal("\n(Repay 0: +4 damage)",
                     FurinaStageFacePreview.Line(0, 4, FurinaStageFacePreview.PayDamage));
        Assert.Contains("FurinaStageFacePreview.RepayAfterDrain(this, 6, 3, "
                        + "FurinaStageFacePreview.PayBlock)",
                        Generated("ProtoFsRiptideLunge"));
    }
}
