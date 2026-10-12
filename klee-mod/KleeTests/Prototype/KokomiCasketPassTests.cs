using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE CASKET PASS (2026-09-28). The Tamakushi Casket counts the Plans the
/// Bake-Kurage carries out; Open the Casket turns the count into Strength;
/// Feint and Sango Isshin read the turn's carry-outs; thirteen rows join the
/// offer and six leave it.
///
/// [USER], in his words: "an artifact that grants / tracks an alternative
/// energy that builds by 1 for every Plan played, and adds one 0-cost Retain /
/// Exhaust card that converts that energy into Strength." Counting is "when
/// it's carried out"; "1 strength per point seems fine"; "the casket keeps
/// counting."
///
/// The ledger arithmetic runs for real on a headless seat; anything that
/// awaits a command (the Strength, the hand move, the drain) is pinned off
/// the compiled methods and their order. Sim twin:
/// <c>tier0/tests/test_kokomi_casket_pass.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiCasketPassTests : IDisposable
{
    // The arm switch is one static; the rules below are the arm's, so they
    // run with it on and put it back (the shipped-kits build ships it off).

    public KokomiCasketPassTests() { }

    public void Dispose() { }

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static IReadOnlyList<DynamicVar> Vars(CardModel card) =>
        ((IEnumerable<DynamicVar>)typeof(CardModel)
            .GetProperty("CanonicalVars", HeadlessGame.All)!.GetValue(card)!)
        .ToList();

    private static decimal Var(CardModel card, string name) =>
        card.DynamicVars[name].BaseValue;

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    // ---- A. the relic ------------------------------------------------------

    // ---- B. Open the Casket -----------------------------------------------

    // ---- C. the re-keyed payoffs ------------------------------------------

    [Fact]
    public void Feint_is_six_plus_three_per_carry_out_and_plans_vulnerable()
    {
        // The cleanup pass (2026-09-29): a base of 6, upgraded 9.
        var card = new ProtoKkFeint();
        Assert.Equal(6m, Var(card, "CalculationBase"));
        Assert.Equal(3m, Var(card, "ExtraDamage"));
        var up = Upgraded<ProtoKkFeint>();
        Assert.Equal(9m, Var(up, "CalculationBase"));
        Assert.Equal(3m, Var(up, "ExtraDamage"));
        Assert.Equal((KokomiPlan.Kind.ApplyVulnerable, 1),
                     (card.PlanClauses.Single().Kind, card.PlanClauses.Single().Amount));
        Assert.Equal(2, up.PlanClauses.Single().Amount);
    }

    [Fact]
    public void Sango_isshin_is_eight_plus_two_to_all_per_carry_out_this_combat()
    {
        // [USER]'s run (2026-10-11): "plans this combat", 2 per Plan; 10, plus
        // 3 per Plan, upgraded.
        var card = new ProtoKkSangoIsshin();
        var up = Upgraded<ProtoKkSangoIsshin>();
        Assert.Equal(TargetType.AllEnemies, card.TargetType);
        Assert.Equal(8m, Var(card, "CalculationBase"));
        Assert.Equal(2m, Var(card, "ExtraDamage"));
        Assert.Equal(10m, Var(up, "CalculationBase"));
        Assert.Equal(3m, Var(up, "ExtraDamage"));
    }

    // ---- D, E. the numbers ------------------------------------------------

    [Fact]
    public void The_moved_numbers()
    {
        Assert.Equal(CardRarity.Uncommon, new ProtoKkSecondWave().Rarity);
        Assert.Equal(7m, new ProtoKkSecondWave().DynamicVars.Damage.BaseValue);
        // The Kokomi card pass (2026-10-11): Pincer 5 [6] twice.
        Assert.Equal(5m, new ProtoKkPincer().DynamicVars.Damage.BaseValue);
        Assert.Equal(6m, Upgraded<ProtoKkPincer>().DynamicVars.Damage.BaseValue);
        Assert.Equal(7m, new ProtoKkOpeningGambit().DynamicVars.Damage.BaseValue);
        Assert.Equal(9m, Upgraded<ProtoKkOpeningGambit>().DynamicVars.Damage.BaseValue);
        // The Kokomi kit review (2026-10-05): Ceremonial Garment costs 1; the
        // Kokomi card pass (2026-10-11): 1 [2] per stack of Weak and
        // Vulnerable. (Deep Current left in the re-founding, 2026-10-12.)
        Assert.Equal(1, new ProtoKkCeremonialGarment().EnergyCost.Canonical);
        Assert.Equal(1m, Var(new ProtoKkCeremonialGarment(), "PowerAmount"));
        Assert.Equal(2m, Var(Upgraded<ProtoKkCeremonialGarment>(), "PowerAmount"));
        var riptide = new ProtoKkRiptide();
        Assert.Equal(11m, riptide.DynamicVars.Damage.BaseValue);
        Assert.Equal(3m, riptide.DynamicVars.ExtraDamage.BaseValue);
        // The re-founding (2026-10-12): the Plan is "Draw 3 cards".
        Assert.Equal((KokomiPlan.Kind.Draw, 3),
                     (riptide.PlanClauses.Single().Kind,
                      riptide.PlanClauses.Single().Amount));
    }

    // ---- G. the thirteen --------------------------------------------------

    [Fact]
    public void The_commons()
    {
        // (Massed Volley and Signal Arrow left in the re-founding, 2026-10-12.)
        // The re-founding: Surging Shoal's Plan is 12 [16] to ALL enemies.
        var shoal = new ProtoKkSurgingShoal();
        Assert.Equal(2, shoal.EnergyCost.Canonical);
        Assert.Equal(14m, shoal.DynamicVars.Damage.BaseValue);
        Assert.Equal((12, KokomiPlan.Aim.AllEnemies),
                     (shoal.PlanClauses.Single().Amount,
                      shoal.PlanClauses.Single().Aim));
        var shoalUp = Upgraded<ProtoKkSurgingShoal>();
        Assert.Equal(18m, shoalUp.DynamicVars.Damage.BaseValue);
        Assert.Equal(16, shoalUp.PlanClauses.Single().Amount);

        // Pearl Diver left the pool in the status batch (2026-10-01).

        // The cleanup pass (2026-09-29): 7 / 11, upgraded 9 / 14.
        var press = new ProtoKkPressTheAdvantage();
        Assert.Equal(7m, Var(press, "PlainDamage"));
        Assert.Equal(11m, Var(press, "BranchDamage"));
        var pressUp = Upgraded<ProtoKkPressTheAdvantage>();
        Assert.Equal(9m, Var(pressUp, "PlainDamage"));
        Assert.Equal(14m, Var(pressUp, "BranchDamage"));
        Assert.Contains(Il.Calls(Il.Method("ProtoKkPressTheAdvantage", "OnPlay")),
                        c => c.Contains("KokomiPlan.PlansHeld"));

        // The re-founding (2026-10-12): Dusk is retired; 6 [9] Block now and
        // a draw, no Plan line.
        var shell = new ProtoKkShellOfSanctuary();
        Assert.Equal(1m, shell.DynamicVars.Cards.BaseValue);
        Assert.Equal(6m, shell.DynamicVars.Block.BaseValue);
        Assert.Equal(9m, Upgraded<ProtoKkShellOfSanctuary>().DynamicVars.Block.BaseValue);
        Assert.DoesNotContain(Il.Calls(Il.Method("ProtoKkShellOfSanctuary", "OnPlay")),
                              c => c.Contains("KokomiPlan.Schedule"));
        Assert.Equal("Gain {Block:diff()} [gold]Block[/gold]. Draw 1 card.", Face(shell));

        // None of these creates a card.
        foreach (var type in new[] { "ProtoKkSurgingShoal",
                                     "ProtoKkPressTheAdvantage",
                                     "ProtoKkShellOfSanctuary" })
        {
            Assert.DoesNotContain(Il.Calls(Il.Method(type, "OnPlay")),
                                  c => c.Contains("CreateCard")
                                    || c.Contains("AddGeneratedCard"));
        }
    }

    [Fact]
    public void Tide_wall_plans_a_flat_six_plus_the_intent()
    {
        // The cleanup pass (2026-09-29): the Plan read 0 on buff turns ("it
        // gave 0 Block twice on Empower turns"), so it gains a flat 6 (9
        // upgraded) on top of the intent, still read at carry-out. Sim twin:
        // `test_r276_tide_wall_blocks_the_largest_intent`.
        var card = new ProtoKkTideWall();
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal((KokomiPlan.Kind.BlockMaxIntent, 6),
                     (clause.Kind, clause.Amount));
        Assert.Equal(9, Upgraded<ProtoKkTideWall>().PlanClauses.Single().Amount);
        Assert.Equal(4m, card.DynamicVars.Block.BaseValue);
        Assert.Equal("Gain {Block:diff()} [gold]Block[/gold].\nOr [gold]plan[/gold]: "
                   + "Gain {PlanBlock:diff()} [gold]Block[/gold], plus the "
                   + "most damage an enemy intends.",
                     Face(card));
    }

    // ---- F. the offer -----------------------------------------------------

    // ---- H. the retired Garment tip ---------------------------------------

    [Fact]
    public void No_arm_attack_carries_the_retired_garment_tip()
    {
        foreach (var type in typeof(ProtoKkFeint).Assembly.GetTypes()
                     .Where(t => t.Name.StartsWith("ProtoKk", StringComparison.Ordinal)
                              && t.Namespace == typeof(ProtoKkFeint).Namespace))
        {
            var tips = type.GetMethod("get_ExtraHoverTips", HeadlessGame.All
                | System.Reflection.BindingFlags.DeclaredOnly);
            if (tips == null) continue;
            Assert.DoesNotContain(Il.Calls(tips),
                                  c => c.Contains("ForGarmentAttack"));
        }
    }
}
