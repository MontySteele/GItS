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
/// <c>review/ruled/kokomi-design-pass-2026-10-11.md</c>, the cards in
/// <c>review/ruled/kokomi-card-paper-2026-10-12.md</c>. The Casket's count,
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
    public void The_casket_is_3_block_while_a_plan_waits_and_the_upgrade_3_per_plan()
    {
        Assert.Equal(3, KokomiOverhaulLaw.CasketBlock);
        Assert.Equal(3, new TamakushiCasket().Block);
        Assert.Equal(3, new TamakushiCasket().BlockFor(2));
        Assert.Equal(6, new WatatsumiCasket().BlockFor(2));
        Assert.False(TamakushiCasket.Pays(0));
        Assert.True(TamakushiCasket.Pays(1));
        Assert.Equal(
            "At the start of your turn, if a [gold]Plan[/gold] is waiting, gain "
            + "[blue]3[/blue] [gold]Block[/gold].",
            new TamakushiCasket().Localization!
                .First(r => r.Item1 == "description").Item2);
        Assert.Contains("[blue]3[/blue] [gold]Block[/gold] for each",
            new WatatsumiCasket().Localization!
                .First(r => r.Item1 == "description").Item2);
    }

    [Fact]
    public void The_casket_reads_the_queue_and_gains_raw_block_after_the_block_clear()
    {
        // [USER], 2026-10-12: "let's have her starter relic apply block at the
        // beginning of the turn rather than the end." AfterBlockCleared runs
        // after the turn's Block clear and before AfterPlayerTurnStart, where
        // the waiting Plans are carried out.
        var seq = Seq(nameof(TamakushiCasket), "AfterBlockCleared");
        var held = seq.IndexOf("KokomiPlan.PlansHeld");
        var block = seq.IndexOf("CreatureCmd.GainBlock");
        Assert.True(held >= 0 && block > held, string.Join(" ", seq));
    }

    // ---- the jellyfish -----------------------------------------------------

    [Fact]
    public void Sting_and_ward_are_ethereal_exhausting_zero_cost_tokens()
    {
        // Cost 0 since the jellyfish build (2026-10-12), with their Plan
        // lines (`KokomiJellyfishBuildTests`).
        foreach (var card in new CardModel[] { new ProtoKkSting(),
                                               new ProtoKkWard() })
        {
            Assert.Equal(0, card.EnergyCost.Canonical);
            Assert.Equal(CardRarity.Token, card.Rarity);
            Assert.Contains(CardKeyword.Ethereal, card.CanonicalKeywords);
            Assert.Contains(CardKeyword.Exhaust, card.CanonicalKeywords);
        }
    }

    // ---- Companions as Plans -----------------------------------------------
    //
    // Kokomi review r9 pick 1 (a), 2026-10-15; [USER]: "let's get rid of
    // Companions as Plans unless we make a card that specifically has a Plan
    // line." The re-founding's general rule (any Companion card can be
    // written) is gone: a Companion is planned only through a Plan line it
    // prints, on the Plan path every Plan card takes.

    [Fact]
    public void A_companion_with_no_plan_line_cannot_be_planned()
    {
        foreach (var card in new CardModel[]
                 { new ProtoMiShinobuThundergrust(), new ProtoMiShinobuGrassRing(),
                   new ProtoMiChioriHasode() })
        {
            // (Kirara left this list in the Inazuma pool rework, 2026-10-18:
            // she prints a Plan line now.)
            var name = card.GetType().Name;
            Assert.IsAssignableFrom<global::KleeMod.Cards.ICompanionCard>(card);
            Assert.False(card is IPlannedCard, name);
            Assert.False(KokomiRefounding.CanBeWritten(card), name);
            // No target override, so the Bake-Kurage refuses it as it
            // refuses any card with no Plan line, and its play never asks
            // whether it was dropped on the jellyfish.
            Assert.NotEqual(card.GetType(),
                            card.GetType().GetProperty("TargetType")!.DeclaringType);
            Assert.DoesNotContain(Il.Calls(Il.Method(name, "OnPlay")),
                                  c => c.Contains("PlayedOnPet")
                                       || c.Contains("KokomiCompanionPlan"));
        }
        // The rule's machinery left with it.
        var asm = typeof(KokomiCompanionPlan).Assembly;
        Assert.Null(asm.GetType("KleeMod.Powers.IWritableCompanion"));
        foreach (var gone in new[] { "Write", "CarryOut", "TargetFor",
                                     "OnKokomi", "AimsAtAnEnemy" })
        {
            Assert.Null(typeof(KokomiCompanionPlan).GetMethod(gone));
        }
        Assert.DoesNotContain("PlayCompanion",
                              System.Enum.GetNames(typeof(KokomiPlan.Kind)));
    }

    [Fact]
    public void A_companion_that_prints_a_plan_line_is_still_planned_by_it()
    {
        // Gorou's Inuzaka: "Plan: Gain 11 Block" (the sim twin carries it out:
        // test_gorou_inuzaka_written_carries_out_its_own_plan_line).
        var gorou = new ProtoMiGorouInuzaka();
        Assert.IsAssignableFrom<global::KleeMod.Cards.ICompanionCard>(gorou);
        Assert.True(KokomiRefounding.CanBeWritten(gorou));
        var plan = Assert.Single(((IPlannedCard)gorou).PlanClauses);
        Assert.Equal(KokomiPlan.Kind.Block, plan.Kind);
        Assert.Equal(KokomiPlan.Aim.Self, plan.Aim);
        // Its play writes its own Plan line on the jellyfish.
        var seq = Seq(nameof(ProtoMiGorouInuzaka), "OnPlay");
        var onPet = seq.FindIndex(c => c.Contains("KokomiPlan.PlayedOnPet"));
        var schedule = seq.FindIndex(c => c.Contains("KokomiPlan.Schedule"));
        Assert.True(onPet >= 0 && schedule > onPet, string.Join(" ", seq));
        Assert.False(KokomiRefounding.CanBeWritten(new ProtoKkEveningWatch()));
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
