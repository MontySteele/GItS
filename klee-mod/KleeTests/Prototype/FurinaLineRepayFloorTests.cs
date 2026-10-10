using System.IO;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE POOL-75 ROUND'S RULINGS, BUILT (2026-10-09,
/// <c>review/records/furina-pool75-round-2026-10-09.md</c>, "Picks (ruled
/// 2026-10-09)"): the Drain line rule's guest and card edges, the Repay floor
/// card by card, and the ruled card numbers. The line itself, the two-part
/// ledger, the Repay order and the curtain call are pinned in
/// <see cref="FurinaTideTests"/>. Sim twin:
/// <c>tier0/tests/test_furina_line_repay_floor.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaLineRepayFloorTests
{
    private static T Run<T>(System.Threading.Tasks.Task<T> task) =>
        StageKit.Run(task);

    private static void Run(System.Threading.Tasks.Task task) =>
        StageKit.Run(task);

    private static string DrainBody => (string)typeof(ArmKeywordTips)
        .GetField("DrainBody", HeadlessGame.All)!.GetRawConstantValue()!;

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

    private const string BlockFloor =
        "Gain 1 [gold]Block[/gold] for any HP it could not [gold]Repay[/gold].";

    private const string VigorFloor =
        "Gain 1 [gold]Vigor[/gold] for any HP it could not [gold]Repay[/gold].";

    // ---- the Repay floor, in the director ----------------------------------

    [Fact]
    public void The_floor_pays_block_for_the_hp_a_repay_could_not_return()
    {
        var kit = StageKit.Of();
        Run(kit.Director.Drain(1));
        Assert.Equal(1, Run(kit.Director.RepayFloor(3, StageFloor.Block)));
        // Repay first, then the leftover: 3 - 1 = 2 Block.
        Assert.Equal(new[] { "lose 1", "heal 1", "block 2" },
                     kit.Board.Log.Where(l => !l.StartsWith("cue")).ToArray());
        // Nothing drained: the whole N.
        kit.Board.Log.Clear();
        Run(kit.Director.RepayFloor(4, StageFloor.Block));
        Assert.Equal(new[] { "block 4" }, kit.Board.Log.ToArray());
        // Everything returned: no floor.
        Run(kit.Director.Drain(5));
        kit.Board.Log.Clear();
        Run(kit.Director.RepayFloor(4, StageFloor.Block));
        Assert.Equal(new[] { "heal 4" }, kit.Board.Log.ToArray());
    }

    [Fact]
    public void The_floor_pays_vigor_and_a_plain_repay_pays_nothing()
    {
        var kit = StageKit.Of();
        Run(kit.Director.RepayFloor(2, StageFloor.Vigor));
        Assert.Equal(new[] { "vigor 2" }, kit.Board.Log.ToArray());
        kit.Board.Log.Clear();
        Run(kit.Director.RepayFloor(2, StageFloor.None));
        Run(kit.Director.Repay(2));
        Assert.Empty(kit.Board.Log);
    }

    [Fact]
    public void Charlotte_and_sigewinne_act_with_a_block_floor()
    {
        var kit = StageKit.Of(StagePerformer.Charlotte);
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.Contains("block 2", kit.Board.Log);
        var up = StageKit.Of();
        Run(up.Director.SummonGuest(StagePerformer.Sigewinne, true));
        Run(up.Director.Drain(1));
        up.Board.Log.Clear();
        Run(up.Director.Act(up.Stage.Seats[0]));
        // Repay 4 returns 1 (her line's Block 1), then the floor's 3.
        Assert.Equal(new[] { "heal 1", "cue Sigewinne", "block 1", "block 3" },
                     up.Board.Log.ToArray());
        Assert.Contains(BlockFloor.Replace("[gold]", "").Replace("[/gold]", ""),
            StagePerformerBadge.ActText(StagePerformer.Charlotte)
                .Replace("[gold]", "").Replace("[/gold]", ""));
        Assert.Contains("could not",
            StagePerformerBadge.ActText(StagePerformer.Sigewinne));
    }

    [Fact]
    public void Fountain_pneuma_tides_gentle_current_and_grand_entrance_pay_their_floor()
    {
        // Fountain: each turn's Repay pays its own Block floor.
        var kit = StageKit.Of();
        kit.Stage.ScheduleRepay(3, FurinaStageLaw.FountainTurns);
        Run(kit.Director.TurnStartRepays());
        Assert.Equal(new[] { "block 3" }, kit.Board.Log.ToArray());
        // Pneuma Tides: Vigor.
        kit.Board.Log.Clear();
        Run(kit.Director.PneumaTides(2));
        Assert.Equal(new[] { "vigor 2" }, kit.Board.Log.ToArray());
        // Gentle Current's next-turn Repay and Grand Entrance: the Block
        // floor, wired where each Repay is made.
        Assert.Contains("StageDirector.RepayFloor",
            Il.Calls(Il.Method("FurinaStage", "RepayNextTurnRepays")));
        Assert.Contains("StageDirector.RepayFloor",
            Il.Calls(Il.Method("FurinaStage", "GuestStar")));
        foreach (var card in new CardModel[]
                 {
                     new ProtoFsFountainOfLucine(), new ProtoFsGentleCurrent(),
                     new ProtoFsGrandEntrance(), new ProtoFsHymnOfManyWaters(),
                 })
        {
            Assert.Contains(BlockFloor, Face(card));
        }
        // Soothing Waters keeps no floor (ruled 2026-10-09): a 0-cost
        // draw-1 card paying out on an empty Repay looped forever.
        Assert.DoesNotContain("could not", Face(new ProtoFsSoothingWaters()));
        Assert.Contains(VigorFloor, Face(new ProtoFsPneumaTides()));
        Assert.Contains("could not",
            new PneumaTidesPower().Localization!
                .Single(r => r.Item1 == "description").Item2);
        Assert.Contains("could not",
            new GrandEntrancePower().Localization!
                .Single(r => r.Item1 == "description").Item2);
        Assert.Contains("could not",
            new RepayNextTurnPower().Localization!
                .Single(r => r.Item1 == "description").Item2);
    }

    [Fact]
    public void Hymn_passes_its_floor_to_the_repay()
    {
        Assert.Contains("DynamicVars[\"RepayAmount\"].IntValue, StageFloor.Block)",
                        Generated("ProtoFsHymnOfManyWaters"));
        // The unchanged Repays pass none, Soothing Waters among them.
        foreach (var type in new[] { "ProtoFsPneumaRefrain", "ProtoFsCleanSlate",
                                     "ProtoFsSoothingWaters",
                                     "ProtoFsBalanceTheBooks", "ProtoFsEbbAndFlow",
                                     "ProtoFsRiptideLunge" })
        {
            Assert.DoesNotContain("StageFloor.", Generated(type));
        }
    }

    [Fact]
    public void The_damage_cards_repay_first_then_add_the_leftover_to_their_damage()
    {
        foreach (var (type, n, damage) in new[]
                 {
                     ("ProtoFsSurgingWaters", "card.DynamicVars[\"RepayAmount\"].IntValue", 6m),
                     ("ProtoFsHydroLance", "4", 14m),
                     ("ProtoFsCleansingTorrent", "4", 10m),
                 })
        {
            var src = Generated(type);
            Assert.Contains($"FurinaStage.RepayLeftOrRoom(card, {n})", src);
            Assert.True(src.IndexOf("await FurinaStage.Repay(",
                                    System.StringComparison.Ordinal)
                        < src.IndexOf("await DamageCmd.Attack(",
                                      System.StringComparison.Ordinal), type);
            var card = (CardModel)System.Activator.CreateInstance(
                typeof(ProtoFsSurgingWaters).Assembly
                    .GetType("KleeMod.Cards.Prototype.Generated." + type)!)!;
            Assert.Equal(damage, card.DynamicVars.CalculationBase.BaseValue);
            Assert.Equal(1m, card.DynamicVars.ExtraDamage.BaseValue);
            Assert.Contains("plus 1 for any HP it could not", Face(card));
        }
        // The upgrades still raise the damage.
        Assert.Equal(9m, Upgraded(new ProtoFsSurgingWaters())
            .DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(18m, Upgraded(new ProtoFsHydroLance())
            .DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(14m, Upgraded(new ProtoFsCleansingTorrent())
            .DynamicVars.CalculationBase.BaseValue);
        // The ledger's record: what this play's Repay left, cleared per play.
        var kit = StageKit.Of();
        kit.Stage.BeginPlay();
        kit.Stage.NoteRepayLeft(4, 1);
        Assert.True(kit.Stage.RepayedThisPlay);
        Assert.Equal(3, kit.Stage.RepayLeftThisPlay);
        kit.Stage.EndPlay();
        Assert.Equal(0, kit.Stage.RepayLeftThisPlay);
        Assert.Equal(0, FurinaStage.RepayLeftOrRoom(null, 4));
    }

    [Fact]
    public void Endless_waltz_is_cut()
    {
        Assert.Null(typeof(ProtoFsSurgingWaters).Assembly.GetType(
            "KleeMod.Cards.Prototype.Generated.ProtoFsEndlessWaltz"));
        Assert.DoesNotContain(ArmPools.Named("KleeMod.Powers.FurinaStageRoster", "Pool"),
            c => c.GetType().Name.Contains("EndlessWaltz"));
    }

    // ---- the Drain line's guest and card edges -------------------------------

    [Fact]
    public void Near_the_line_counts_any_hp_at_or_below_it()
    {
        Assert.True(FurinaStageLaw.NearTheLine(64, 59));
        Assert.True(FurinaStageLaw.NearTheLine(59, 59));
        Assert.True(FurinaStageLaw.NearTheLine(40, 59));
        Assert.True(FurinaStageLaw.NearTheLine(1, 59));
        Assert.False(FurinaStageLaw.NearTheLine(65, 59));
    }

    [Fact]
    public void A_five_century_act_reads_its_new_text_at_the_same_cost_and_rarity()
    {
        var card = new ProtoFsAFiveCenturyAct();
        Assert.Equal("HP you [gold]Drain[/gold] past your line also returns "
                     + "when combat ends.", Face(card));
        Assert.Equal(2, card.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Rare, card.Rarity);
    }

    [Fact]
    public void The_drain_tip_states_the_quarter_of_max_hp_rule()
    {
        Assert.Contains("minus 1/4 of your Max HP", DrainBody);
        Assert.DoesNotContain("3/4", DrainBody);
        Assert.Contains("lost unless you", DrainBody);
        Assert.Equal("the HP you started this fight with, minus 1/4 of your "
                     + "Max HP", FurinaStageLaw.LineWhy(false));
        Assert.EndsWith(", 10 lower with Lyney on stage",
                        FurinaStageLaw.LineWhy(true));
    }

    // ---- the ruled card numbers ----------------------------------------------

    [Fact]
    public void Standing_ovation_is_uncommon()
    {
        Assert.Equal(CardRarity.Uncommon, new ProtoFsStandingOvationAll().Rarity);
    }

    [Fact]
    public void Bravuras_upgrade_raises_the_base_to_ten_and_keeps_two_per_point()
    {
        var plain = new ProtoFsBravura();
        Assert.Equal(6m, plain.DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(2m, plain.DynamicVars.ExtraDamage.BaseValue);
        var up = Upgraded(new ProtoFsBravura());
        Assert.Equal(10m, up.DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(2m, up.DynamicVars.ExtraDamage.BaseValue);
    }

    [Fact]
    public void Crabaletta_deals_20_and_soloists_solicitation_6()
    {
        Assert.Equal(20m, new ProtoFsMademoiselleCrabaletta().DynamicVars.Damage.BaseValue);
        Assert.Equal(26m, Upgraded(new ProtoFsMademoiselleCrabaletta())
            .DynamicVars.Damage.BaseValue);
        Assert.Equal(6m, new ProtoFsSoloistsSolicitation().DynamicVars.Damage.BaseValue);
        Assert.Equal(9m, Upgraded(new ProtoFsSoloistsSolicitation())
            .DynamicVars.Damage.BaseValue);
    }

    [Fact]
    public void Commanding_gazes_plain_mode_applies_two_vulnerable()
    {
        Assert.StartsWith("Apply 2 [gold]Vulnerable[/gold]. [gold]Spend[/gold] 4",
                          Face(new ProtoFsCommandingGaze()));
        Assert.Contains("Apply 2 Vulnerable", Generated("ProtoFsCommandingGaze"));
    }

    [Fact]
    public void Freminets_act_gives_three_block_six_upgraded()
    {
        // The Spend paper (2026-10-10) took the 5 [8] Cryo hit and set the
        // Block to 3 [6], plus half the bank (none held here).
        var kit = StageKit.Of(StagePerformer.Freminet);
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.DoesNotContain(kit.Board.Log, l => l.StartsWith("damage Freminet"));
        Assert.Contains("block 3", kit.Board.Log);
        var up = StageKit.Of();
        Run(up.Director.SummonGuest(StagePerformer.Freminet, true));
        Run(up.Director.Act(up.Stage.Seats[0]));
        Assert.Contains("block 6", up.Board.Log);
        Assert.Contains("gain 3 [gold]Block[/gold]",
            StagePerformerBadge.ActText(StagePerformer.Freminet));
        Assert.Contains("gain 6 [gold]Block[/gold]",
            StagePerformerBadge.ActText(StagePerformer.Freminet, true));
    }

    [Fact]
    public void Neuvillette_costs_one_and_acts_for_all_hp_lost_since_her_last_turn()
    {
        Assert.Equal(1, new ProtoFsGuestStarNeuvillette().EnergyCost.Canonical);
        var kit = StageKit.Of(StagePerformer.Neuvillette);
        // The enemies' turn: a hit of 7 counts.
        kit.Board.Hp -= 7;
        kit.Director.OnHpLost(7);
        // Her turn: two Drains.
        Run(kit.Director.Drain(3));
        Run(kit.Director.Drain(2));
        Assert.Equal(12, kit.Stage.HpLostSinceLastTurn);
        Run(kit.Director.EndOfTurn(0));
        Assert.Contains("damage Neuvillette All 12 Hydro", kit.Board.Log);
        // The window opens again after her acts.
        Assert.Equal(0, kit.Stage.HpLostSinceLastTurn);
        Assert.Contains("lost since your last turn",
            StagePerformerBadge.ActText(StagePerformer.Neuvillette));
        // Upgraded: the line +1, as before.
        Assert.Equal(3, FurinaStageLaw.NeuvilletteHydroBonusUpgraded);
    }

    [Fact]
    public void The_pool_is_78()
    {
        // The block gap (ruled 2026-10-09): four more, 20 / 37 / 21.
        var pool = ArmPools.Named("KleeMod.Powers.FurinaStageRoster", "Pool");
        Assert.Equal(78, pool.Count);
        Assert.Equal((20, 37, 21),
            (pool.Count(c => c.Rarity == CardRarity.Common),
             pool.Count(c => c.Rarity == CardRarity.Uncommon),
             pool.Count(c => c.Rarity == CardRarity.Rare)));
    }
}
