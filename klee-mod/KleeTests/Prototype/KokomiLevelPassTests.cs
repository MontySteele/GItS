using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI LEVEL PASS (2026-10-12), <c>review/active/kokomi-level-pass-
/// 2026-10-12.md</c>, ruled "On the Kokomi level paper - agreed on all
/// defaults": the big numbers down (section 1) and a floor under the odd cards
/// (section 2). Sim twin: <c>tier0/tests/test_kokomi_level_pass_2026_10_12.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiLevelPassTests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    // ---- section 1 -------------------------------------------------------

    [Fact]
    public void Steady_tide_is_eleven_fourteen_and_change_of_plans_is_uncommon()
    {
        // The Kokomi upgrade pass (2026-10-19): 9 [12]; Plan draw 3 [4].
        Assert.Equal(9, new ProtoKkSteadyTide().DynamicVars.Block.IntValue);
        Assert.Equal(12, Upgraded<ProtoKkSteadyTide>().DynamicVars.Block.IntValue);
        Assert.Equal(4, Upgraded<ProtoKkSteadyTide>().PlanClauses.Single().Amount);
        Assert.Equal(CardRarity.Uncommon, new ProtoKkChangeOfPlans().Rarity);
    }

    // ---- section 2 -------------------------------------------------------

    [Fact]
    public void Tideturn_has_a_floor_of_eight_ten()
    {
        var card = new ProtoKkTideturn();
        Assert.Equal(8m, card.DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(10m, Upgraded<ProtoKkTideturn>()
                              .DynamicVars.CalculationBase.BaseValue);
        Assert.StartsWith("Deal {CalculationBase:diff()} [gold]Hydro[/gold] "
                        + "damage, plus {ExtraDamage:diff()} for each",
                          Face(card));
    }

    [Fact]
    public void Shoal_of_spears_hits_once_more_than_the_plans_waiting()
    {
        Assert.Contains("plus once more for each [gold]Plan[/gold] waiting, "
                      + "not Stings or Wards.",
                        Face(new ProtoKkShoalOfSpears()));
        // Kokomi v3 (2026-10-18): not Stings or Wards.
        Assert.Contains(Il.Calls(Il.Method("ProtoKkShoalOfSpears", "OnPlay")),
                        c => c.Contains("KokomiPlan.ChainPlansHeld"));
    }

    [Fact]
    public void Drowning_pressure_applies_its_own_weak_and_vulnerable_first()
    {
        var seq = Seq("ProtoKkDrowningPressure", "OnPlay");
        var weak = seq.FindIndex(c => c.Contains("WeakPower"));
        var vuln = seq.FindIndex(c => c.Contains("VulnerablePower"));
        var hit = seq.FindIndex(c => c.Contains("DamageCmd.Attack"));
        Assert.True(weak >= 0 && vuln > weak && hit > vuln,
                    string.Join(" | ", seq));
        Assert.StartsWith("Apply 1 [gold]Weak[/gold] and 1 "
                        + "[gold]Vulnerable[/gold].",
                          Face(new ProtoKkDrowningPressure()));
    }

    [Fact]
    public void Flank_plans_eleven_fourteen_at_whoever_intends_to_attack()
    {
        var clause = Assert.Single(new ProtoKkFlank().PlanClauses);
        Assert.Equal(KokomiPlan.Aim.EnemiesIntendingAttack, clause.Aim);
        Assert.Equal(11, clause.Amount);
        Assert.Equal(14, Assert.Single(Upgraded<ProtoKkFlank>().PlanClauses).Amount);
        Assert.EndsWith("each enemy that intends to attack when this is "
                        + "carried out.", Face(new ProtoKkFlank()));
    }

    [Fact]
    public void Orders_from_the_shrine_costs_one_and_chooses()
    {
        var card = new ProtoKkOrdersFromTheShrine();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(0, (int)Upgraded<ProtoKkOrdersFromTheShrine>()
            .EnergyCost.GetWithModifiers(CostModifiers.None));
        Assert.Contains(Il.Calls(Il.Method("ProtoKkOrdersFromTheShrine", "OnPlay")),
                        c => c.Contains("KokomiCards.ChooseCommonCompanion"));
        Assert.Contains(Il.Calls(Il.Method("KokomiCards", "ChooseCommonCompanion")),
                        c => c.Contains("FromChooseACardScreen"));
        Assert.StartsWith("Choose 1 of 3 random Common Inazuma "
                        + "[gold]Companions[/gold]", Face(card));
    }
}
