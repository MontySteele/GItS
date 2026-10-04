using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Kokomi;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// R276, Kokomi's two non-card changes.
///
/// PICK 2 IS RETIRED AS A RULE (2026-10-05). It made every damaging card in
/// Kokomi's hand apply Hydro, Skills included; [USER] ruled that a legacy
/// design -- the element "just lives in the card pool as a symbol on relevant
/// elemental cards". Her two damaging Skills that print Hydro (Opening Gambit,
/// Second Wave) now declare it on the sheet, and a card that declares nothing
/// applies nothing in her hand. Sim twin: <c>tier0/tests/test_kokomi_plan.py</c>.
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

    // ---- pick 2, now on the card ---------------------------------------------

    [Fact]
    public void Her_damaging_skills_declare_hydro()
    {
        // Each prints "Deal 7 [gold]Hydro[/gold] damage" and declares it on
        // the sheet (`applies_element: true`), so the codegen puts
        // IElementalCard and the gem on the card itself.
        foreach (var card in new CardModel[]
                 {
                     new ProtoKkOpeningGambit(),
                     new ProtoKkSecondWave(),
                 })
        {
            Assert.Equal(MegaCrit.Sts2.Core.Entities.Cards.CardType.Skill,
                         card.Type);
            var elemental = Assert.IsAssignableFrom<IElementalCard>(card);
            Assert.Equal(Element.Hydro, elemental.Element);
        }
    }

    [Fact]
    public void A_no_element_mod_damage_card_played_by_kokomi_applies_nothing()
    {
        // [USER], 2026-10-05: "I think that that Kokomi effect is a legacy
        // design." Furina's Surging Waters is a mod-authored Attack that
        // deals damage and names no element -- no IElementalCard, no carried
        // hit, no gem. In Kokomi's hand it used to apply her Hydro; it applies
        // nothing, in hers or anyone's. Before this change the funnel's
        // character fallback answered Hydro here.
        try
        {
            var cheered = new ProtoFsSurgingWaters();
            Assert.Equal(CardType.Attack, cheered.Type);
            Assert.IsNotAssignableFrom<IElementalCard>(cheered);
            Assert.Equal(Element.None,
                AuraCmd.ElementOfPlay(cheered, Seat.Kokomi().Creature));
            Assert.Equal(Element.None,
                AuraCmd.ElementOfPlay(cheered, Seat.Klee().Creature));

            // Her own Skill that declares nothing (War Council's face-up half
            // is a debuff) applies nothing in her hand either.
            var council = new ProtoKkWarCouncil();
            Assert.IsNotAssignableFrom<IElementalCard>(council);
            Assert.Equal(Element.None,
                AuraCmd.ElementOfPlay(council, Seat.Kokomi().Creature));
        }
        finally
        {
        }
    }

    // ---- her Ancient -----------------------------------------------------------

    [Fact]
    public void The_ancient_prints_the_plan_payout_under_the_arm_and_charge_off_it()
    {
        try
        {
            var arm = Description(new PrincessOfWatatsumi());
            Assert.Contains("carries out a [gold]Plan[/gold]", arm);
            Assert.Contains("{PlanBlock:diff()} [gold]Block[/gold]", arm);
            Assert.Contains("draw 1 card", arm);
            Assert.DoesNotContain("Charge", arm);

        }
        finally
        {
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
        Assert.True(live >= 0 && plan > live);
        Assert.DoesNotContain(applies, c => c.Contains("ChargePerTurnPower"));
    }

    // ---- pick 1: the halves rewrite's five new Plan clauses -----------------

    [Fact]
    public void The_new_clauses_resolve_through_their_own_seams()
    {
        var resolve = Il.CallSequence(Il.Method("KokomiPlan", "ResolveOne"));
        Assert.Contains(resolve, c => c.Contains("KokomiOverhaulKit.FirstAttackTwice"));
        Assert.Contains(resolve, c => c.Contains("KokomiOverhaulKit.FirstCardFree"));
        Assert.Contains(resolve, c => c.Contains("KokomiOverhaulKit.IntendedDamage"));
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
