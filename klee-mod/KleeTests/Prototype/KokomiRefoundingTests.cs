using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI RE-FOUNDING (2026-10-12): the direction in
/// <c>review/active/kokomi-design-pass-2026-10-11.md</c>, the cards in
/// <c>review/active/kokomi-card-paper-2026-10-12.md</c>. The Casket's count,
/// Open the Casket and Dusk are retired; the relic is Block while a Plan
/// waits; Stings and Wards are her jellyfish; any Companion card can be
/// written as a Plan.
///
/// Headless: pure functions run for real, anything that awaits a command is
/// pinned off the compiled method's call order. The behaviours are the sim's,
/// <c>tier0/tests/test_kokomi_refounding.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiRefoundingTests
{
    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    // ---- the relic ---------------------------------------------------------

    [Fact]
    public void The_casket_is_3_block_while_a_plan_waits_and_the_upgrade_5()
    {
        Assert.Equal(3, KokomiOverhaulLaw.CasketBlock);
        Assert.Equal(3, new TamakushiCasket().Block);
        Assert.Equal(5, new WatatsumiCasket().Block);
        Assert.False(TamakushiCasket.Pays(0));
        Assert.True(TamakushiCasket.Pays(1));
        Assert.Equal(
            "At the end of your turn, if a [gold]Plan[/gold] is waiting, gain "
            + "[blue]3[/blue] [gold]Block[/gold].",
            new TamakushiCasket().Localization!
                .First(r => r.Item1 == "description").Item2);
        Assert.Contains("[blue]5[/blue]", new WatatsumiCasket().Localization!
            .First(r => r.Item1 == "description").Item2);
    }

    [Fact]
    public void The_casket_reads_the_queue_and_gains_raw_block_at_turn_end()
    {
        var seq = Seq(nameof(TamakushiCasket), "BeforeSideTurnEnd");
        var held = seq.IndexOf("KokomiPlan.PlansHeld");
        var block = seq.IndexOf("CreatureCmd.GainBlock");
        Assert.True(held >= 0 && block > held, string.Join(" ", seq));
    }

    // ---- the jellyfish -----------------------------------------------------

    [Fact]
    public void Sting_and_ward_are_ethereal_exhausting_one_cost_tokens()
    {
        foreach (var card in new CardModel[] { new ProtoKkSting(),
                                               new ProtoKkWard() })
        {
            Assert.Equal(1, card.EnergyCost.Canonical);
            Assert.Equal(CardRarity.Token, card.Rarity);
            Assert.Contains(CardKeyword.Ethereal, card.CanonicalKeywords);
            Assert.Contains(CardKeyword.Exhaust, card.CanonicalKeywords);
        }
    }

    // ---- Companions as Plans -----------------------------------------------

    [Fact]
    public void A_companion_without_a_plan_line_is_writable_and_gorous_carry_their_own()
    {
        Assert.IsAssignableFrom<IWritableCompanion>(
            new ProtoMiShinobuThundergrust());
        Assert.IsAssignableFrom<IWritableCompanion>(
            new ProtoMiShinobuGrassRing());
        Assert.False(new ProtoMiGorouInuzaka() is IWritableCompanion);
        Assert.True(KokomiRefounding.CanBeWritten(new ProtoMiGorouInuzaka()));
        Assert.True(KokomiRefounding.CanBeWritten(
            new ProtoMiShinobuThundergrust()));
        Assert.False(KokomiRefounding.CanBeWritten(new ProtoKkEveningWatch()));
    }

    [Fact]
    public void A_canonical_companion_prints_its_own_target()
    {
        var card = new ProtoMiShinobuThundergrust();
        Assert.Equal(TargetType.AnyEnemy, card.PrintedTargetType);
        Assert.Equal(TargetType.AnyEnemy, card.TargetType);
        Assert.True(KokomiCompanionPlan.AimsAtAnEnemy(card));
        Assert.False(KokomiCompanionPlan.AimsAtAnEnemy(
            new ProtoMiShinobuGrassRing()));
    }

    [Fact]
    public void The_carry_out_lays_hydro_first_then_auto_plays_an_exhausting_clone()
    {
        var seq = Seq(nameof(KokomiCompanionPlan), "CarryOut");
        var hydro = seq.IndexOf("ElementalHit.ApplyOnly");
        var clone = seq.IndexOf("ICombatState.CloneCard");
        var exhaust = seq.IndexOf("CardModel.set_ExhaustOnNextPlay");
        var play = seq.IndexOf("CardCmd.AutoPlay");
        Assert.True(hydro >= 0 && clone > hydro && exhaust > clone
                    && play > exhaust, string.Join(" ", seq));
    }

    [Fact]
    public void A_generated_companion_is_ethereal_and_exhausts()
    {
        var seq = Seq(nameof(KokomiCompanionPlan), "Generate");
        Assert.Equal(2, seq.Count(c => c == "CardModel.AddKeyword"));
    }

    [Fact]
    public void Grand_designs_free_write_is_the_one_auto_play_that_writes()
    {
        Assert.Contains("KokomiRefounding.IsFreeWrite",
                        Seq(nameof(KokomiPlan), "PlayedOnPet"));
        Assert.Contains("CardCmd.AutoPlay",
                        Seq(nameof(KokomiRefounding), "WriteFree"));
    }

    [Fact]
    public void Call_the_generals_offers_three_on_a_skippable_screen()
    {
        Assert.Equal(3, KokomiCompanionPlan.GeneralsOffered);
        var seq = Seq(nameof(KokomiCards), "CallTheGenerals");
        Assert.Contains("KokomiCompanionPlan.Generated", seq);
        Assert.Contains("CardSelectCmd.FromChooseACardScreen", seq);
    }

    // ---- turn order --------------------------------------------------------

    [Fact]
    public void Dawn_tide_lays_its_hydro_after_the_morning_plans()
    {
        var seq = Seq(nameof(ProtoBakeKuragePower), "AfterPlayerTurnStart");
        var resolve = seq.IndexOf("KokomiPlan.ResolveAll");
        var dawn = seq.IndexOf("DawnTidePower.Signal");
        Assert.True(resolve >= 0 && dawn > resolve, string.Join(" ", seq));
    }

    [Fact]
    public void Dusk_and_the_casket_count_are_gone()
    {
        var types = typeof(TamakushiCasket).Assembly.GetTypes()
            .Select(t => t.Name).ToHashSet();
        Assert.DoesNotContain("OpenTheCasket", types);
        Assert.DoesNotContain("FirstCardFreePower", types);
        Assert.DoesNotContain("ProtoKkFloodTide", types);
        Assert.Null(typeof(ProtoBakeKuragePower).GetMethod(
            "BeforeSideTurnEnd",
            System.Reflection.BindingFlags.DeclaredOnly
            | System.Reflection.BindingFlags.Public
            | System.Reflection.BindingFlags.Instance));
    }
}
