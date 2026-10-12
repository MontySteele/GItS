using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI ROUND-2 CHANGES (2026-10-12), from the Fable round-1 review and
/// <c>review/records/kokomi-round-1-2026-10-12.md</c>: the jellyfish
/// generators at a Common attack's rate, the engine Powers up, the Commander
/// generators free, Call the Generals' card free this turn, Tideturn and
/// Shoal of Spears up, and Nereid's Ascension's "twice" tip. The Treatise
/// gate is pinned in <see cref="KokomiRound1FixesTests"/>. Sim twin:
/// <c>tier0/tests/test_kokomi_round2_changes_2026_10_12.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiRound2ChangesTests
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

    private static int Var<T>(string name, bool upgraded = false)
        where T : CardModel, new() =>
        (upgraded ? Upgraded<T>() : new T()).DynamicVars[name].IntValue;

    [Fact]
    public void The_jellyfish_generators_hit_and_block_harder()
    {
        Assert.Equal((8, 11), (Var<ProtoKkJellyfishDrift>("Damage"),
                               Var<ProtoKkJellyfishDrift>("Damage", true)));
        Assert.Equal((8, 11), (Var<ProtoKkWatatsumiDrill>("Damage"),
                               Var<ProtoKkWatatsumiDrill>("Damage", true)));
        Assert.Equal((7, 10), (Var<ProtoKkBubbleWard>("Block"),
                               Var<ProtoKkBubbleWard>("Block", true)));
    }

    [Fact]
    public void The_engine_powers_pay_more()
    {
        Assert.Equal((5, 7), (Var<ProtoKkWatchfulShoal>("PowerAmount"),
                              Var<ProtoKkWatchfulShoal>("PowerAmount", true)));
        Assert.Equal((6, 9), (Var<ProtoKkCoordinatedTide>("PowerAmount"),
                              Var<ProtoKkCoordinatedTide>("PowerAmount", true)));
        Assert.Equal((3, 4), (Var<ProtoKkKurageCanopy>("PowerAmount"),
                              Var<ProtoKkKurageCanopy>("PowerAmount", true)));
        Assert.Equal((7, 10), (Var<ProtoKkGrandStrategist>("PowerAmount"),
                               Var<ProtoKkGrandStrategist>("PowerAmount", true)));
        Assert.Equal((5, 6), (Var<ProtoKkShoalOfSpears>("Damage"),
                              Var<ProtoKkShoalOfSpears>("Damage", true)));
    }

    [Fact]
    public void Muster_and_shoal_call_cost_0_and_exhaust()
    {
        foreach (var card in new CardModel[]
                 { new ProtoKkWatatsumiMuster(), new ProtoKkShoalCall() })
        {
            Assert.Equal(0, card.EnergyCost.Canonical);
            Assert.Contains(CardKeyword.Exhaust, card.CanonicalKeywords);
            Assert.False(global::KleeMod.Powers.KokomiRefounding.CanBeWritten(card),
                         card.GetType().Name);
        }
    }

    [Fact]
    public void Call_the_generals_hands_a_card_that_costs_0_this_turn()
    {
        Assert.EndsWith("It costs 0 this turn.",
                        Face(new ProtoKkCallTheGenerals()));
        var calls = Il.CallSequence(
            Il.Method("KokomiCards", "CallTheGenerals")).ToList();
        var generate = calls.FindIndex(
            c => c.Contains("KokomiCompanionPlan.Generate"));
        var free = calls.FindIndex(c => c.Contains("SetThisTurn"));
        var add = calls.FindIndex(
            c => c.Contains("CardPileCmd.AddGeneratedCardToCombat"));
        Assert.True(generate >= 0 && free > generate && add > free);
    }

    [Fact]
    public void Nereids_ascension_says_twice_means_twice()
    {
        // The wrapper and not the materialised tip: building a HoverTip
        // formats a LocString through a LocManager that is null headless.
        var none = Enumerable.Empty<MegaCrit.Sts2.Core.HoverTips.IHoverTip>();
        Assert.NotSame(none, ArmKeywordTips.ForNereidsTwice(
            none, new ProtoKkNereidsAscension()));
        Assert.Equal("KLEEMOD-ARM_PLAN_TWICE_DEBUFFS",
                     ArmKeywordTips.NereidsTwiceKey);
    }
}
