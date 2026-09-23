using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Kokomi;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// R276, Kokomi's two non-card changes.
///
/// PICK 2: every damaging card of hers applies Hydro under the arm, Skills
/// included -- five of her Skills dealt damage face-up and applied nothing
/// while her Attacks applied Hydro. Klee's arm keeps the Attack-only rule and
/// the base game's cards still apply nothing. Sim twin:
/// <c>tier0/tests/test_kokomi_plan.py</c>'s r276 tests.
///
/// HYGIENE: her Ancient, Princess of Watatsumi, pays on the Plan under the arm
/// ("Whenever the Bake-Kurage carries out a Plan, gain 2 Block and draw 1
/// card.") instead of the Charge the arm turns off.
///
/// THE COLLECTION IS LOAD-BEARING: both arm switches are one static apiece.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiR276Tests
{
    private static void Upgrade(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
    }

    private static string Description(CustomCardModel card) =>
        card.Localization!.Single(row => row.Item1 == "description").Item2;

    // ---- pick 2 --------------------------------------------------------------

    [Fact]
    public void Her_damaging_skills_declare_hydro()
    {
        // The generator's half: the arm's cadence puts IElementalCard on every
        // card of hers whose face-up half deals damage, Skills included.
        foreach (var card in new CardModel[]
                 {
                     new ProtoKkChainOfCommand(), new ProtoKkOpeningGambit(),
                 })
        {
            Assert.Equal(MegaCrit.Sts2.Core.Entities.Cards.CardType.Skill,
                         card.Type);
            var elemental = Assert.IsAssignableFrom<IElementalCard>(card);
            Assert.Equal(Element.Hydro, elemental.Element);
        }
    }

    [Fact]
    public void The_fallback_elements_a_skill_of_hers_and_not_of_klees()
    {
        // The character rule, asked of a Skill that declares nothing (War
        // Council's face-up half is a debuff; its Plan hit goes through the
        // same funnel). Under Kokomi's arm her Skill answers Hydro; in Klee's
        // seat the same card answers nothing, because Klee's cadence is still
        // Attack-only; with the arm off it answers nothing, as before.
        var klee = KleeOverhaul.Enabled;
        var kokomi = KokomiOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = true;
            KokomiOverhaul.Enabled = true;
            var skill = new ProtoKkWarCouncil();
            Assert.IsNotAssignableFrom<IElementalCard>(skill);

            Assert.True(CatalystCadence.EveryDamagingCardCarriesElement(
                Seat.Kokomi().Creature));
            Assert.Equal(Element.Hydro, CatalystCadence.PrintedElement(
                skill, Seat.Kokomi().Creature));
            Assert.False(CatalystCadence.EveryDamagingCardCarriesElement(
                Seat.Klee().Creature));
            Assert.Equal(Element.None, CatalystCadence.PrintedElement(
                skill, Seat.Klee().Creature));

            // The base game's cards stay outside it, Skills too.
            Assert.Equal(Element.None, CatalystCadence.PrintedElement(
                new DefendIronclad(), Seat.Kokomi().Creature));
            Assert.Equal(Element.None, CatalystCadence.PrintedElement(
                new StrikeSilent(), Seat.Kokomi().Creature));

            KokomiOverhaul.Enabled = false;
            Assert.Equal(Element.None, CatalystCadence.PrintedElement(
                skill, Seat.Kokomi().Creature));
        }
        finally
        {
            KleeOverhaul.Enabled = klee;
            KokomiOverhaul.Enabled = kokomi;
        }
    }

    // ---- her Ancient -----------------------------------------------------------

    [Fact]
    public void The_ancient_prints_the_plan_payout_under_the_arm_and_charge_off_it()
    {
        var was = KokomiOverhaul.Enabled;
        try
        {
            KokomiOverhaul.Enabled = true;
            var arm = Description(new PrincessOfWatatsumi());
            Assert.Contains("carries out a [gold]Plan[/gold]", arm);
            Assert.Contains("{PlanBlock:diff()} [gold]Block[/gold]", arm);
            Assert.Contains("draw 1 card", arm);
            Assert.DoesNotContain("Charge", arm);

            KokomiOverhaul.Enabled = false;
            var shipped = Description(new PrincessOfWatatsumi());
            Assert.Contains("[gold]Charge[/gold]", shipped);
            Assert.DoesNotContain("Plan", shipped);
        }
        finally
        {
            KokomiOverhaul.Enabled = was;
        }
    }

    [Fact]
    public void The_ancient_pays_two_block_and_three_upgraded()
    {
        var card = new PrincessOfWatatsumi();
        Assert.Equal(2m, card.DynamicVars["PlanBlock"].BaseValue);
        Assert.Equal(3m, card.DynamicVars["PowerAmount"].BaseValue);
        var upgraded = new PrincessOfWatatsumi();
        Upgrade(upgraded);
        Assert.Equal(3m, upgraded.DynamicVars["PlanBlock"].BaseValue);
        Assert.Equal(4m, upgraded.DynamicVars["PowerAmount"].BaseValue);
    }

    [Fact]
    public void The_ancient_applies_the_plan_power_only_where_the_arm_is_live()
    {
        // STRUCTURAL: applying a power needs a live PlayerChoiceContext.
        var applies = Il.CallSequence(Il.Method("PrincessOfWatatsumi", "OnPlay"))
            .ToList();
        var live = applies.FindIndex(c => c.Contains("KokomiOverhaul.LiveFor"));
        var plan = applies.FindIndex(
            c => c.Contains("PrincessOfWatatsumiPlanPower"));
        var charge = applies.FindIndex(c => c.Contains("ChargePerTurnPower"));
        Assert.True(live >= 0 && plan > live && charge > plan);
    }

    // ---- pick 1: the halves rewrite's five new Plan clauses -----------------

    [Fact]
    public void The_new_clauses_resolve_through_their_own_seams()
    {
        var resolve = Il.CallSequence(Il.Method("KokomiPlan", "ResolveOne"));
        Assert.Contains(resolve, c => c.Contains("KokomiOverhaulKit.FirstAttackTwice"));
        Assert.Contains(resolve, c => c.Contains("KokomiOverhaulKit.FirstCardFree"));
        Assert.Contains(resolve, c => c.Contains("PowerCmd.Apply<AttackUpThisTurnPower>"));
        Assert.Contains(resolve, c => c.Contains("KokomiOverhaulKit.IntendedDamage"));
        Assert.Contains(resolve, c => c.Contains("KokomiPlan.UnhurtAmount"));
        // Feigned Retreat's HP is stamped when the Plan is WRITTEN.
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "Schedule")),
                        c => c.Contains("get_CurrentHp"));
    }

    [Fact]
    public void Feigned_retreat_reads_her_hp_against_the_written_hp()
    {
        var kokomi = Seat.Kokomi().Creature;
        var hp = kokomi.CurrentHp;
        var method = typeof(KokomiPlan).GetMethod("UnhurtAmount",
                                                  HeadlessGame.All)!;
        int Pay(int? written) => (int)method.Invoke(null, new object[]
        {
            kokomi,
            new KokomiPlan.Planned(KokomiPlan.Kind.DamageIfUnhurt, 9,
                                   KokomiPlan.Aim.FrontEnemy, Alt: 14,
                                   WrittenHp: written),
        })!;
        Assert.Equal(14, Pay(hp));          // unhurt since writing
        Assert.Equal(9, Pay(hp + 1));       // lost HP since writing
        Assert.Equal(14, Pay(null));        // unstamped reads as unhurt
    }

    [Fact]
    public void Pincers_switch_skips_a_write_and_ends_with_the_turn()
    {
        Assert.Contains(
            Il.Calls(Il.Method("FirstAttackTwicePower", "ModifyCardPlayCount")),
            c => c.Contains("BakeKuragePet.Is"));
        var spent = Il.Calls(Il.Method("FirstAttackTwicePower",
                                       "AfterCardPlayed"));
        Assert.Contains(spent, c => c.Contains("KokomiPlan.PlayedOnPet"));
        Assert.Contains(spent, c => c.Contains("PowerCmd.Remove"));
        Assert.Contains(Il.Calls(Il.Method("FirstAttackTwicePower",
                                           "AfterSideTurnEnd")),
                        c => c.Contains("PowerCmd.Remove"));
    }

    [Fact]
    public void Stolen_chapters_switch_zeroes_a_cost_and_is_spent_by_a_real_play()
    {
        Assert.Contains(
            Il.Calls(Il.Method("FirstCardFreePower", "AfterCardPlayed")),
            c => c.Contains("get_IsAutoPlay"));
        Assert.Contains(Il.Calls(Il.Method("FirstCardFreePower",
                                           "AfterSideTurnEnd")),
                        c => c.Contains("PowerCmd.Remove"));
        Assert.NotNull(typeof(FirstCardFreePower).GetMethod(
            "TryModifyEnergyCostInCombat", HeadlessGame.All));
    }

    [Fact]
    public void Tide_walls_intent_read_is_null_safe()
    {
        Assert.Equal(0, KokomiOverhaulKit.IntendedDamage(null, null));
        Assert.Contains(
            Il.Calls(Il.Method("KokomiOverhaulKit", "IntendedDamage")),
            c => c.Contains("AttackIntent.GetTotalDamage"));
    }

    [Fact]
    public void The_plan_power_pays_block_and_a_card_on_every_plan()
    {
        // "Whenever", not "once per turn": no ledger claim on this hook.
        Assert.True(typeof(IKokomiPlanListener)
            .IsAssignableFrom(typeof(PrincessOfWatatsumiPlanPower)));
        var hook = typeof(PrincessOfWatatsumiPlanPower)
            .GetMethod("OnPlanResolved", HeadlessGame.All)!;
        var calls = Il.CallSequence(hook).ToList();
        Assert.DoesNotContain(calls,
            c => c.Contains("KokomiOverhaulLedger.ClaimOncePerTurn"));
        var block = calls.IndexOf("CreatureCmd.GainBlock");
        var draw = calls.IndexOf("CardPileCmd.Draw");
        Assert.True(block >= 0 && draw > block);
    }
}
