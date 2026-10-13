using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Diagnostics;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI ROUND 3 A-LIST (2026-10-13; review
/// <c>review/active/kokomi-review-r3-2026-10-13.md</c> sections 4 and 5A),
/// the C# side: Second Wave's window, Bubble Ward 6 [9], Kurage Canopy's
/// Wards, Albedo's target, and the two page receipts the mod files (a
/// generated card a full hand sent to the discard pile, and the turn's-end
/// Ethereal Exhaust). Sim and page twin:
/// <c>tier0/tests/test_kokomi_round3_alist_2026_10_13.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiRound3AListTests
{
    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    [Fact]
    public void Second_wave_names_the_plan_written_after_it_this_turn()
    {
        Assert.EndsWith("The [gold]Plan[/gold] written after it this turn is "
                      + "carried out twice.", Face(new ProtoKkSecondWave()));
    }

    [Fact]
    public void Albedo_names_the_enemy_with_the_most_auras()
    {
        Assert.EndsWith("At the end of your turn, if any enemy has an aura, deal "
                   + "8 damage to the enemy with the most auras and gain 4 "
                   + "[gold]Block[/gold].",
                     Face(new ProtoMcAlbedoSolarIsotoma()));
    }

    [Fact]
    public void Kurage_canopy_plus_is_the_upgraded_ward_twin()
    {
        Assert.True(typeof(KurageCanopyBasePower)
            .IsAssignableFrom(typeof(KurageCanopyPlusPower)));
        Assert.True(typeof(KurageCanopyBasePower)
            .IsAssignableFrom(typeof(KurageCanopyPower)));
    }

    [Fact]
    public void A_full_hand_files_the_discard_receipt()
    {
        // "1 Sting to the discard pile (hand full)": the jellyfish maker
        // files the event when the card landed in the discard pile.
        var calls = Seq("KokomiCards", "AddJellyfish");
        Assert.Contains(calls, c => c.Contains("ResolutionLedger.NoteToDiscard"));
        Assert.Equal("discarded", ResolutionLedger.ToDiscard);
    }

    [Fact]
    public void The_turns_end_ethereal_exhaust_files_a_receipt()
    {
        var calls = Seq("PlayTelemetryHooks", "AfterCardExhausted");
        Assert.Contains(calls,
            c => c.Contains("ResolutionLedger.NoteEtherealExhaust"));
        Assert.Equal("ethereal", ResolutionLedger.EtherealExhausted);
    }

    [Fact]
    public void Change_of_plans_costs_nothing_and_its_gate_is_the_queue()
    {
        // Lane 4 F6 read "no Energy" with four Plans waiting. The card's
        // cost is 0 on both faces and its one gate reads the queue, never
        // Energy; the sim twin plays it at 0 Energy with four waiting.
        var card = new ProtoKkChangeOfPlans();
        Assert.Equal(0, card.EnergyCost.Canonical);
        var gate = Il.Calls(Il.Method("ProtoKkChangeOfPlans", "get_IsPlayable"));
        Assert.Contains(gate, c => c.Contains("KokomiPlan.PlansHeld"));
        Assert.DoesNotContain(gate, c => c.Contains("Energy"));
    }

    [Fact]
    public void A_plans_strength_is_read_when_it_is_written()
    {
        // `KokomiPlan.Schedule` folds her Strength into the written number
        // (`Hers`); the carry-out deals that number.
        Assert.Contains(Seq("KokomiPlan", "Schedule"),
                        c => c.Contains("KokomiPlan.Hers"));
    }
}
