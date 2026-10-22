using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using HarmonyLib;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI CARD PAPER V2 (2026-10-18,
/// <c>review/active/kokomi-cards-2026-10-18.md</c> sec.2, picks 1 (b), 2 (a),
/// 3 (a); [USER]: "On Kokomi, I'm good with all three - let's try that and
/// see if it works."). The mod's halves of the four changes: Draft the Orders
/// in Shell of Sanctuary's slot and its plan-only discount, Tidal Rebuke's
/// Block spend, Tidal Riposte's stored bonus (Vigor's shape, one card wide),
/// and Endless Shoal's and Kurage Canopy's Sting-or-Ward clause. Structural
/// pins (the headless boundary); sim twin
/// <c>tier0/tests/test_kokomi_cards_v2_2026_10_18.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiCardsV2Tests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    private static (int, int) Vars<T>(string name)
        where T : CardModel, new() =>
        (new T().DynamicVars[name].IntValue,
         Upgraded<T>().DynamicVars[name].IntValue);

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static string PowerText(ILocalizationProvider power) =>
        power.Localization!.First(r => r.Item1 == "description").Item2;

    private static List<string> Calls(string type, string method) =>
        Il.Calls(Il.Method(type, method)).ToList();

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    private static List<string> Slice() =>
        Il.CallSequence(Il.Method("KokomiOverhaulRoster", "Slice"))
            .Where(c => c.StartsWith("ModelDb.Card", StringComparison.Ordinal))
            .Select(c => c.Substring(c.IndexOf('<') + 1).TrimEnd('>'))
            .ToList();

    // ---- 1. Draft the Orders ------------------------------------------------------

    [Fact]
    public void Draft_the_orders_takes_shell_of_sanctuarys_slot()
    {
        var slice = Slice();
        Assert.Contains("ProtoKkDraftTheOrders", slice);
        Assert.DoesNotContain("ProtoKkShellOfSanctuary", slice);
        var card = new ProtoKkDraftTheOrders();
        Assert.Equal((CardType.Skill, CardRarity.Common, 1),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal((5, 8), Vars<ProtoKkDraftTheOrders>("Block"));
        Assert.Equal("Gain {Block:diff()} [gold]Block[/gold]. The next card "
                   + "you [gold]plan[/gold] this turn costs 1 less.",
                     Face(card));
        Assert.Contains(Calls("ProtoKkDraftTheOrders", "OnPlay"),
                        c => c.Contains("PowerCmd.Apply"));
    }

    [Fact]
    public void The_discount_is_only_for_a_card_that_can_be_planned()
    {
        Assert.True(DraftTheOrdersPower.Plannable(new ProtoKkBrineSting()));
        Assert.True(DraftTheOrdersPower.Plannable(new ProtoKkSting()));
        Assert.False(DraftTheOrdersPower.Plannable(new ProtoKkTidalRebuke()));
        Assert.False(DraftTheOrdersPower.Plannable(new ProtoKkDraftTheOrders()));
        Assert.False(DraftTheOrdersPower.Plannable(null));
    }

    [Fact]
    public void The_discount_is_taken_back_off_a_play_aimed_elsewhere()
    {
        // The cost hook cannot see the play (`EB-668`), so it asks the play
        // the action recorded; with nothing recorded, the hand shows it.
        Assert.Contains(Calls("DraftTheOrdersPower", "TryModifyEnergyCostInCombat"),
                        c => c.Contains("KokomiPlanCost.PlayedOffThePet"));
        Assert.False(KokomiPlanCost.PlayedOffThePet(new ProtoKkBrineSting()));
        var patch = typeof(KokomiPlanCost).Assembly
            .GetType("KleeMod.Powers.PlayCardAction_PlanTarget_Patch")!
            .GetCustomAttribute<HarmonyPatch>();
        Assert.NotNull(patch);
        Assert.Equal(typeof(PlayCardAction), patch!.info.declaringType);
        Assert.Equal("ExecuteAction", patch.info.methodName);
        Assert.NotNull(typeof(PlayCardAction).GetMethod(
            "ExecuteAction", BindingFlags.Instance | BindingFlags.NonPublic));
        Assert.Contains(Calls("KokomiPlanCost", "Capture"),
                        c => c.Contains("BakeKuragePet.Is"));
    }

    [Fact]
    public void Only_a_card_planned_at_a_price_spends_it_and_it_ends_with_the_turn()
    {
        var before = Calls("DraftTheOrdersPower", "BeforeCardPlayed");
        Assert.Contains(before, c => c.Contains("KokomiPlan.PlayedOnPet"));
        Assert.Contains(before, c => c.Contains("CardEnergyCost.GetWithModifiers"));
        Assert.Contains(Calls("DraftTheOrdersPower", "AfterCardPlayed"),
                        c => c.Contains("PowerCmd.Remove"));
        Assert.Contains(Calls("DraftTheOrdersPower", "AfterSideTurnEnd"),
                        c => c.Contains("PowerCmd.Remove"));
    }

    // ---- 3. Tidal Rebuke --------------------------------------------------------

    [Fact]
    public void Tidal_rebuke_loses_the_block_then_deals_twice_it()
    {
        var rebuke = new ProtoKkTidalRebuke();
        Assert.Equal("Lose all your [gold]Block[/gold]. Deal twice that in "
                   + "[gold]Hydro[/gold] damage to ALL enemies.{InCombat:\n"
                   + "(Deals {CalculatedDamage:diff()} damage)|}",
                     Face(rebuke));
        Assert.Equal(2m, rebuke.DynamicVars.ExtraDamage.BaseValue);
        Assert.Contains(CardKeyword.Retain, rebuke.CanonicalKeywords);
        var play = Seq("ProtoKkTidalRebuke", "OnPlay");
        var lose = play.FindIndex(c => c.Contains("KokomiCards.LoseAllBlock"));
        var hit = play.FindIndex(c => c.Contains("DamageCmd.Attack"));
        Assert.True(lose >= 0 && hit > lose, "the Block is lost first");
        Assert.Contains(Calls("KokomiCards", "LoseAllBlock"),
                        c => c.Contains("CreatureCmd.LoseBlock"));
    }

    // ---- 4. Tidal Riposte -------------------------------------------------------

    [Fact]
    public void Tidal_riposte_reads_one_attack_whole()
    {
        Assert.Equal((8, 11), Vars<ProtoKkTidalRiposte>("PowerAmount"));
        Assert.True(TidalRipostePower.FullyBlocked(new[] { (6, 0) }));
        Assert.True(TidalRipostePower.FullyBlocked(new[] { (3, 0), (3, 0), (3, 0) }));
        // One hit through, nothing blocked, or no hit on her: no bonus.
        Assert.False(TidalRipostePower.FullyBlocked(new[] { (5, 0), (2, 3) }));
        Assert.False(TidalRipostePower.FullyBlocked(new[] { (0, 0) }));
        Assert.False(TidalRipostePower.FullyBlocked(Array.Empty<(int, int)>()));
    }

    [Fact]
    public void The_stored_bonus_is_vigor_one_attack_card_wide()
    {
        var before = Calls("TidalRiposteChargePower", "BeforeCardPlayed");
        Assert.Contains(before, c => c.Contains("KokomiPlan.PlayedOnPet"));
        Assert.NotNull(typeof(TidalRiposteChargePower).GetMethod(
            "ModifyDamageAdditive",
            BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly));
        var after = Calls("TidalRiposteChargePower", "AfterCardPlayed");
        Assert.Contains(after, c => c.Contains("PowerCmd.Remove"));
        Assert.Contains(after, c => c.Contains("PowerCmd.ModifyAmount"));
        Assert.StartsWith("Your next Attack deals",
                          PowerText(new TidalRiposteChargePower()));
    }

    // ---- 5. Endless Shoal and Kurage Canopy ---------------------------------------

    [Fact]
    public void Endless_shoal_and_canopy_skip_a_sting_or_ward_plan()
    {
        Assert.Contains(Calls("KokomiRefounding", "OnCarriedOut"),
                        c => c.Contains("KokomiRefounding.IsJellyfish"));
        // Kurage Canopy reads Battle Formation's count since the Kokomi
        // defence pass (2026-10-22): the ledger's chain count, which skips
        // a Sting's or Ward's Plan.
        Assert.Contains(Calls("KurageCanopyPower", "Signal"),
                        c => c.Contains("ChainPlansThisTurn"));
        Assert.Contains("KokomiRefounding.OnCarriedOut",
                        Seq("KokomiPlan", "ResolveEntry"));
        Assert.EndsWith(" Stings and Wards don't count.",
                        Face(new ProtoKkKurageCanopy()));
        Assert.Contains(" that is not a [gold]Sting[/gold] or [gold]Ward[/gold],",
                        PowerText(new EndlessShoalPower()));
    }
}
