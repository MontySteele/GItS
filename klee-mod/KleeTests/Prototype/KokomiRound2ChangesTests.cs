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

    // The jellyfish generators moved again in the jellyfish build
    // (2026-10-12): `KokomiJellyfishBuildTests`.

    [Fact]
    public void The_engine_powers_pay_more()
    {
        // Watchful Shoal was rewritten in the Kokomi round-3 changes
        // (`KokomiRound3ChangesTests`).
        // The pool overhaul (2026-10-13): Coordinated Tide adds 1 Sting (the
        // upgrade is Innate) and Grand Strategist is 4 [6]
        // (`KokomiPoolOverhaulTests`). Kurage Canopy makes Wards since the
        // Kokomi round 3 A-list (2026-10-13; `KokomiPayoffPassTests`).
        // Coordinated Tide left and Grand Strategist moved to 6 [8] with
        // the Kokomi review r6 (2026-10-14, pick 2 (b)).
        Assert.Equal((6, 8), (Var<ProtoKkGrandStrategist>("PowerAmount"),
                              Var<ProtoKkGrandStrategist>("PowerAmount", true)));
        // The pool sweep (2026-10-18): Shoal of Spears 7 [9].
        Assert.Equal((7, 9), (Var<ProtoKkShoalOfSpears>("Damage"),
                              Var<ProtoKkShoalOfSpears>("Damage", true)));
    }

    [Fact]
    public void Muster_costs_0_and_exhausts()
    {
        // Shoal Call is Blade Dance since the jellyfish build (2026-10-12):
        // cost 1 (`KokomiJellyfishBuildTests`).
        foreach (var card in new CardModel[] { new ProtoKkWatatsumiMuster() })
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
        // Wording pass (2026-10-15): "It costs 0 this turn and is Ethereal."
        Assert.EndsWith("costs 0 this turn and is [gold]Ethereal[/gold].",
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
