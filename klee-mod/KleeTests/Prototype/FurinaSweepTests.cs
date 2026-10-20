using System;
using System.IO;
using System.Linq;
using HarmonyLib;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE SWEEP (<c>review/active/furina-sweep-2026-10-14.md</c> sec.2
/// and sec.3, the second set, ruled 2026-10-14): fifteen cut, fifteen new,
/// the pool still 78 at 23 / 35 / 20 with 17 Powers. Structural pins over
/// the generated cards, <see cref="FurinaCards"/>' five new verbs, the face
/// of Ousia / Pneuma and the sweep's Powers; the behaviour is the sim twin's,
/// <c>tier0/tests/test_furina_sweep_2026_10_14.py</c>.
/// </summary>
public class FurinaSweepTests
{
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

    private static readonly string[] Gone =
    {
        // The fifteen cut.
        "ProtoFsSoloistsSolicitation", "ProtoFsSpiritedAria",
        "ProtoFsStandingOvationAll", "ProtoFsHydroLance", "ProtoFsOverdraft",
        "ProtoFsPackedHouse", "ProtoFsIntervalBell", "ProtoFsSoothingWaters",
        "ProtoFsBalanceTheBooks", "ProtoFsSalonsEncore", "ProtoFsOusiaSurge",
        "ProtoFsHighStakes", "ProtoFsPneumaTides", "ProtoFsTheDeluge",
        "ProtoFsHymnOfRenewal",
        // The first set, replaced.
        "ProtoFsRainOfTears", "ProtoFsRehearsal", "ProtoFsSilenceInTheCourt",
        "ProtoFsPirouette", "ProtoFsSpotlightGrab", "ProtoFsCostumeFitting",
        "ProtoFsQuickChange", "ProtoFsReadTheScript", "ProtoFsPracticedGrace",
        "ProtoFsMiseEnScene", "ProtoFsIntermission", "ProtoFsSecondAct",
        "ProtoFsSoloRecital", "ProtoFsPneumaAndOusia", "ProtoFsStandIn",
    };

    private static readonly (Type Type, CardRarity Rarity)[] New =
    {
        (typeof(ProtoFsOusiaPneuma), CardRarity.Common),
        (typeof(ProtoFsObjection), CardRarity.Common),
        (typeof(ProtoFsTearfulMonologue), CardRarity.Common),
        (typeof(ProtoFsStageDirections), CardRarity.Common),
        (typeof(ProtoFsOpeningNumber), CardRarity.Common),
        (typeof(ProtoFsFacade), CardRarity.Common),
        (typeof(ProtoFsTrialByWater), CardRarity.Uncommon),
        (typeof(ProtoFsRainfallOverture), CardRarity.Uncommon),
        (typeof(ProtoFsEncorePerformance), CardRarity.Uncommon),
        (typeof(ProtoFsArkheInBalance), CardRarity.Uncommon),
        (typeof(ProtoFsCrowdFavorite), CardRarity.Uncommon),
        (typeof(ProtoFsTheShowsNotOver), CardRarity.Uncommon),
        (typeof(ProtoFsUnderstudysDebut), CardRarity.Uncommon),
        (typeof(ProtoFsVerdictOfTheOratrice), CardRarity.Rare),
        (typeof(ProtoFsPlotTwist), CardRarity.Rare),
    };

    [Fact]
    public void The_fifteen_new_are_in_the_pool_and_the_cut_and_first_set_are_gone()
    {
        var pool = ArmPools.Named("KleeMod.Powers.FurinaStageRoster", "Pool");
        var names = pool.Select(c => c.GetType().Name).ToHashSet();
        foreach (var (type, rarity) in New)
        {
            Assert.Contains(type.Name, names);
            Assert.Equal(rarity, ((CardModel)Activator.CreateInstance(type)!).Rarity);
        }
        foreach (var gone in Gone)
        {
            Assert.DoesNotContain(gone, names);
            Assert.Null(typeof(ProtoFsFacade).Assembly.GetType(
                "KleeMod.Cards.Prototype.Generated." + gone));
        }
        Assert.Equal(78, pool.Count);
        Assert.Equal(17, pool.Count(c => c.Type == CardType.Power));
    }

    [Fact]
    public void Each_new_card_calls_its_rule()
    {
        Assert.Contains("FurinaCards.Flip", Generated("ProtoFsOusiaPneuma"));
        Assert.Contains("FurinaFlip.OnPneuma(this)", Generated("ProtoFsOusiaPneuma"));
        Assert.Contains("PowerCmd.Apply<ObjectionPower>", Generated("ProtoFsObjection"));
        Assert.Contains("FurinaSweep.LostHpLastTurn", Generated("ProtoFsTearfulMonologue"));
        Assert.Contains("FurinaCards.StageDirections", Generated("ProtoFsStageDirections"));
        Assert.Contains("FurinaSweep.FirstTurnOfCombat", Generated("ProtoFsOpeningNumber"));
        Assert.Contains("FurinaCards.Facade", Generated("ProtoFsFacade"));
        Assert.Contains("PowerCmd.Apply<TrialByWaterPower>", Generated("ProtoFsTrialByWater"));
        Assert.Contains("PowerCmd.Apply<VulnerablePower>", Generated("ProtoFsTrialByWater"));
        Assert.Contains("PowerCmd.Apply<RainfallOverturePower>",
                        Generated("ProtoFsRainfallOverture"));
        Assert.Contains("FurinaCards.EncorePerformance",
                        Generated("ProtoFsEncorePerformance"));
        Assert.Contains("PowerCmd.Apply<ArkheInBalancePower>",
                        Generated("ProtoFsArkheInBalance"));
        Assert.Contains("PowerCmd.Apply<CrowdFavoritePower>", Generated("ProtoFsCrowdFavorite"));
        Assert.Contains("IsPlayable =>\n        CurtainCallHooks.HpLostThisTurn",
                        Generated("ProtoFsTheShowsNotOver"));
        Assert.Contains("CurrentHp * 100m < Owner.Creature.MaxHp * 50m",
                        Generated("ProtoFsUnderstudysDebut"));
        Assert.Contains("FurinaCards.Verdict", Generated("ProtoFsVerdictOfTheOratrice"));
        Assert.Contains("PowerCmd.Apply<PlotTwistPower>", Generated("ProtoFsPlotTwist"));
        Assert.Contains("IsPlayable =>\n        CurtainCallHooks.EnemyIntendsAttack",
                        Generated("ProtoFsPlotTwist"));
    }

    [Fact]
    public void The_verbs_make_the_base_games_calls()
    {
        var verdict = Il.Calls(Il.Method("FurinaCards", "Verdict"));
        Assert.Contains("CreatureCmd.Kill", verdict);                 // Doom's execute
        Assert.Contains("CreatureCmd.Damage", verdict);
        Assert.Contains("FurinaStage.FanfareOf", verdict);
        Assert.DoesNotContain("FurinaStage.Spend", verdict);
        var encore = Il.Calls(Il.Method("FurinaCards", "EncorePerformance"));
        Assert.Contains("CardCmd.AutoPlay", encore);                  // Havoc's body
        Assert.Contains("CardModel.set_ExhaustOnNextPlay", encore);
        var directions = Il.Calls(Il.Method("FurinaCards", "StageDirections"));
        Assert.Contains("CardPileCmd.Add", directions);
        Assert.Contains("FurinaSweep.CostZeroNextTurn", directions);
        Assert.Contains("FurinaSweep.LostThisCombat",
                        Il.Calls(Il.Method("FurinaCards", "Facade")));
    }

    [Fact]
    public void Ousia_pneuma_turns_over_and_names_its_face()
    {
        var card = new ProtoFsOusiaPneuma();
        Assert.False(FurinaFlip.OnPneuma(card));
        FurinaFlip.Turn(card);
        Assert.True(FurinaFlip.OnPneuma(card));
        FurinaFlip.Turn(card);
        Assert.False(FurinaFlip.OnPneuma(card));
        // A fresh card (every combat's clone) starts on Ousia.
        FurinaFlip.Turn(card);
        Assert.False(FurinaFlip.OnPneuma(new ProtoFsOusiaPneuma()));
        // Out of combat it keeps its two-faced name.
        Assert.Equal("Ousia / Pneuma", FurinaFlip.TitleOf(card, "Ousia / Pneuma"));
        var face = Face(new ProtoFsOusiaPneuma());
        // Furina's card pass (2026-10-15): each face does one half of her
        // kit, Ousia a Drain and Pneuma a Repay.
        Assert.StartsWith("{Pneuma:[gold]Repay[/gold] 2. Gain {BranchBlock:diff()}", face);
        Assert.Contains("{InCombat:[gold]Drain[/gold] 2. Deal {BranchDamage:diff()} damage.", face);
        Assert.Contains("[gold]Flip[/gold]", face);
        Assert.Contains("ArmKeywordTips.ForFlip", Generated("ProtoFsOusiaPneuma"));
    }

    [Fact]
    public void The_upgrades_move_the_printed_numbers()
    {
        // Furina's card pass (2026-10-15): 10 [13] and 8 [11].
        Assert.Equal(13m, Upgraded(new ProtoFsOusiaPneuma()).DynamicVars["BranchDamage"].BaseValue);
        Assert.Equal(11m, Upgraded(new ProtoFsOusiaPneuma()).DynamicVars["BranchBlock"].BaseValue);
        Assert.Equal(8m, Upgraded(new ProtoFsObjection()).DynamicVars.Block.BaseValue);
        Assert.Equal(9m, Upgraded(new ProtoFsTearfulMonologue()).DynamicVars.Block.BaseValue);
        Assert.Equal(8m, Upgraded(new ProtoFsStageDirections()).DynamicVars.Block.BaseValue);
        Assert.Equal(10m, Upgraded(new ProtoFsOpeningNumber()).DynamicVars.Damage.BaseValue);
        Assert.Equal(10m, Upgraded(new ProtoFsOpeningNumber()).DynamicVars["BranchDamage"].BaseValue);
        Assert.Equal(16m, Upgraded(new ProtoFsFacade()).DynamicVars["FsAmount"].BaseValue);
        Assert.Equal(3m, Upgraded(new ProtoFsTrialByWater()).DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal(3m, Upgraded(new ProtoFsArkheInBalance()).DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal(8m, Upgraded(new ProtoFsUnderstudysDebut()).DynamicVars.Damage.BaseValue);
        Assert.Equal(8m, Upgraded(new ProtoFsUnderstudysDebut()).DynamicVars["BranchBlock"].BaseValue);
        Assert.Equal(0, Upgraded(new ProtoFsRainfallOverture())
            .EnergyCost.GetWithModifiers(CostModifiers.None));
        Assert.Equal(0, Upgraded(new ProtoFsEncorePerformance())
            .EnergyCost.GetWithModifiers(CostModifiers.None));
        Assert.Equal(1, Upgraded(new ProtoFsVerdictOfTheOratrice())
            .EnergyCost.GetWithModifiers(CostModifiers.None));
        Assert.Equal(0, Upgraded(new ProtoFsPlotTwist())
            .EnergyCost.GetWithModifiers(CostModifiers.None));
        Assert.Contains(CardKeyword.Innate, Upgraded(new ProtoFsCrowdFavorite()).Keywords);
        // It keeps Exhaust (design call 2026-10-14: without it, 13 loops).
        Assert.Contains(CardKeyword.Exhaust, Upgraded(new ProtoFsTheShowsNotOver()).Keywords);
        Assert.Equal(3m, Upgraded(new ProtoFsTheShowsNotOver()).DynamicVars["Energy"].BaseValue);
    }

    [Fact]
    public void The_keywords_read_as_the_paper()
    {
        Assert.Contains(CardKeyword.Innate, new ProtoFsOpeningNumber().Keywords);
        Assert.Contains(CardKeyword.Exhaust, new ProtoFsTheShowsNotOver().Keywords);
        Assert.Contains(CardKeyword.Exhaust, new ProtoFsVerdictOfTheOratrice().Keywords);
        Assert.Contains(CardKeyword.Exhaust, new ProtoFsPlotTwist().Keywords);
        Assert.Contains("Next turn, it costs 0.", Face(new ProtoFsStageDirections()));
    }

    [Fact]
    public void The_powers_hook_where_the_paper_says()
    {
        var arkhe = Il.Calls(typeof(ArkheInBalancePower)
            .GetMethod("AfterCardPlayed", HeadlessGame.All)!);
        Assert.Contains("CreatureCmd.GainBlock", arkhe);
        Assert.Contains("ElementalHit.DealUnelemented", arkhe);
        Assert.Contains("CreatureCmd.Damage", Il.Calls(typeof(ObjectionPower)
            .GetMethod("AfterDamageReceived", HeadlessGame.All)!));
        Assert.Contains("FurinaStage.Gain", Il.Calls(typeof(TrialByWaterPower)
            .GetMethod("AfterDamageReceived", HeadlessGame.All)!));
        Assert.Contains("PlayerCmd.GainEnergy", Il.Calls(typeof(CrowdFavoritePower)
            .GetMethod("AfterEnergyReset", HeadlessGame.All)!));
        // The two seams: a widened Attack aims at every enemy, a marked
        // enemy's attack at itself.
        var types = typeof(ArkheInBalancePower).Assembly.GetTypes();
        var widen = types.Single(
            t => t.Name == "AttackCommand_Targeting_RainfallOverture_Patch");
        var info = widen.GetCustomAttributes(typeof(HarmonyPatch), false)
            .Cast<HarmonyPatch>().Single().info;
        Assert.Equal(typeof(AttackCommand), info.declaringType);
        Assert.Equal(nameof(AttackCommand.Targeting), info.methodName);
        var twist = types.Single(
            t => t.Name == "AttackCommand_FromMonster_PlotTwist_Patch");
        Assert.Equal(nameof(AttackCommand.FromMonster),
                     twist.GetCustomAttributes(typeof(HarmonyPatch), false)
                         .Cast<HarmonyPatch>().Single().info.methodName);
        // A Plot Twisted Entomancer hitting itself: Personal Hive has no
        // player to give Dazed to, and is skipped instead of throwing.
        var hive = types.Single(
            t => t.Name == "PersonalHivePower_AfterDamageReceived_PlotTwist_Patch");
        var hiveInfo = hive.GetCustomAttributes(typeof(HarmonyPatch), false)
            .Cast<HarmonyPatch>().Single().info;
        Assert.Equal(typeof(MegaCrit.Sts2.Core.Models.Powers.PersonalHivePower),
                     hiveInfo.declaringType);
        Assert.Equal("AfterDamageReceived", hiveInfo.methodName);
    }
}
