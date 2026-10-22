using System;
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
/// THE KOKOMI FINISH PASS (2026-10-19, <c>review/active/kokomi-cards-2026-10-18.md</c>
/// sec.7 "The changes", ruled all (a); [USER]: "I like this all around").
///   1. Battle Formation (Rare Power, 2): "At the start of your turn, if 2 or
///      more of your Plans were carried out, gain [E] [and draw 1 card].
///      Stings and Wards don't count." One power for both versions: every
///      copy adds Energy, each upgraded copy a card.
///   2. Grand Design (Rare Skill, 1): "Plan up to 3 [4] cards from your
///      Hand. They cost 0. Draw 1 card for each. Exhaust."
/// Structural and pure pins (the headless boundary); sim twin
/// <c>tier0/tests/test_kokomi_finish_pass_2026_10_19.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiFinishPassTests
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

    private static string PowerText(PowerModel power, string key) =>
        ((ILocalizationProvider)power).Localization!
            .First(r => r.Item1 == key).Item2;

    // ---- 1. BATTLE FORMATION ------------------------------------------------

    [Fact]
    public void Battle_formation_costs_two_and_its_upgrade_adds_the_draw()
    {
        var plain = new ProtoKkBattleFormation();
        Assert.Equal(2, plain.EnergyCost.Canonical);
        Assert.Equal(
            "At the start of your turn, if 2 or more [gold]Plans[/gold] "
          + "were carried out, gain {energyPrefix:energyIcons(1)}"
          + "{IfUpgraded:show: and draw 1 card|}. Stings and Wards don't count.",
            Face(plain));
        var up = Upgraded<ProtoKkBattleFormation>();
        Assert.Equal(2, up.EnergyCost.Canonical);
        Assert.DoesNotContain(CardKeyword.Innate, up.Keywords);
    }

    [Fact]
    public void Battle_formation_is_one_badge_for_both_versions()
    {
        Assert.True(typeof(UpgradeTwinPower)
            .IsAssignableFrom(typeof(BattleFormationPower)));
        Assert.Contains(Il.Calls(Il.Method(nameof(ProtoKkBattleFormation), "OnPlay")),
                        c => c.Contains("UpgradeTwinPower.Install"));
        Assert.Equal(
            "At the start of your turn, if 2 or more [gold]Plans[/gold] "
          + "were carried out, gain {Amount:energyIcons()}. Stings and Wards "
          + "don't count.",
            PowerText(new BattleFormationPower(), "description"));
    }

    [Fact]
    public void Every_copy_adds_energy_and_each_upgraded_copy_a_card()
    {
        Assert.Equal((1, 0), BattleFormationPower.Payout(1, 0));
        Assert.Equal((1, 1), BattleFormationPower.Payout(1, 1));
        Assert.Equal((3, 2), BattleFormationPower.Payout(3, 2));
        Assert.Equal((0, 0), BattleFormationPower.Payout(0, 0));
        Assert.False(BattleFormationPower.Pays(1));
        Assert.True(BattleFormationPower.Pays(2));
    }

    [Fact]
    public void Battle_formation_reads_the_morning_after_the_plans_not_stings_or_wards()
    {
        var morning = Il.CallSequence(
            Il.Method(nameof(ProtoBakeKuragePower), "AfterPlayerTurnStart")).ToList();
        var resolve = morning.FindIndex(c => c.Contains("KokomiPlan.ResolveAll"));
        var signal = morning.FindIndex(c => c.Contains("BattleFormationPower.Signal"));
        Assert.True(resolve >= 0 && signal > resolve, string.Join(" ", morning));
        var reads = Il.Calls(Il.Method(nameof(BattleFormationPower), "Signal"));
        Assert.Contains(reads, c => c.Contains("get_ChainPlansThisTurn"));
        Assert.DoesNotContain(reads, c => c.Contains("get_PlansCarriedOutThisTurn"));
        // No longer paid from a carry-out.
        Assert.DoesNotContain(
            Il.CallSequence(Il.Method("KokomiRefounding", "OnCarriedOut")),
            c => c.Contains("BattleFormationPower"));
    }

    // ---- 2. GRAND DESIGN ----------------------------------------------------

    [Fact]
    public void Grand_design_plans_three_or_four_draws_for_each_and_exhausts()
    {
        var plain = new ProtoKkGrandDesign();
        Assert.Equal("Plan up to {KkAmount:diff()} cards from your "
                   + "[gold]Hand[/gold]. They cost 0. Draw 1 card for each.",
                     Face(plain));
        Assert.DoesNotContain("Basic", Face(plain));
        Assert.Equal(3, plain.DynamicVars["KkAmount"].IntValue);
        Assert.Contains(CardKeyword.Exhaust, plain.CanonicalKeywords);
        var up = Upgraded<ProtoKkGrandDesign>();
        Assert.Equal(4, up.DynamicVars["KkAmount"].IntValue);
        Assert.DoesNotContain(CardKeyword.Retain, up.Keywords);
        Assert.Equal(1, up.EnergyCost.Canonical);
    }

    [Fact]
    public void Grand_design_draws_once_its_picks_are_planned()
    {
        var calls = Il.CallSequence(Il.Method("KokomiCards", "GrandDesign")).ToList();
        var write = calls.FindLastIndex(c => c.Contains("WriteAsItself"));
        var draw = calls.FindIndex(c => c.Contains("CardPileCmd.Draw"));
        Assert.True(write >= 0 && draw > write, string.Join(" ", calls));
        Assert.Equal(typeof(System.Threading.Tasks.Task<bool>),
                     typeof(KokomiRefounding).GetMethod("WriteFree")!.ReturnType);
        Assert.Equal(typeof(System.Threading.Tasks.Task<bool>),
                     typeof(KokomiRefounding).GetMethod("WriteAsItself")!.ReturnType);
        Assert.Contains("{Amount}", KokomiRefounding.GrandDesignPromptText);
    }
}
