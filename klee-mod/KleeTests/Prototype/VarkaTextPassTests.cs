using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// VARKA TEXT PASS (2026-10-13), the live damage previews from the
/// damage-preview census. Display only: every number the play reads is the
/// var's <c>BaseValue</c>, unchanged; the faces fold Strength, Weak and
/// Vulnerable the way a damage var does. Sim twin (the sheet and the
/// generated text): <c>tier0/tests/test_varka_text_pass_2026_10_13.py</c>.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaTextPassTests : IDisposable
{
    public VarkaTextPassTests()
    {
        HeadlessGame.Arm();
        VarkaOathLedger.ResetAll();
    }

    public void Dispose()
    {
        VarkaOathLedger.ResetAll();
    }

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static decimal Var(CardModel card, string name) =>
        card.DynamicVars[name].BaseValue;

    private static string Face(object model) =>
        ((ILocalizationProvider)model).Localization!
            .Single(l => l.Item1 == "description").Item2;

    private static decimal Preview(DynamicVar var, CardModel card)
    {
        var.UpdateCardPreview(card, CardPreviewMode.Normal, null,
                              runGlobalHooks: false);
        return var.PreviewValue;
    }

    [Fact]
    public void Plain_varka_hits_print_a_folding_damage_number()
    {
        // Charged Lunge, Ember Cleave, Chain Lightning, Tempest, Violet Storm
        // (per hit), Kindled Edge and Razor: VkBase is a damage var now, the
        // sheet number unchanged.
        var rows = new (CardModel Card, decimal Base, Element Carries)[]
        {
            (new ProtoVkChargedLunge(), 6m, Element.Electro),
            (new ProtoVkEmberCleave(), 9m, Element.Pyro),
            (new ProtoVkChainLightning(), 8m, Element.Electro),
            (new ProtoVkTempestOfTheFourWinds(), 4m, Element.None),
            (new ProtoVkVioletStorm(), 6m, Element.Electro),
            (new ProtoVkKindledEdge(), 7m, Element.Pyro),
            (new ProtoVkRazorClawAndThunder(), 6m, Element.Electro),
        };
        foreach (var (card, printed, carries) in rows)
        {
            var v = Assert.IsType<FoldedDamageVar>(card.DynamicVars["VkBase"]);
            Assert.Equal(printed, v.BaseValue);
            Assert.Equal(carries, v.Carries);
            Assert.False(v.FollowsHit);
        }
        Assert.Equal(9m, Var(Upgraded<ProtoVkChargedLunge>(), "VkBase"));
    }

    [Fact]
    public void Kindled_edges_follow_up_repeats_vkbase_as_a_folded_leg()
    {
        var edge = new ProtoVkKindledEdge();
        Assert.IsType<VarkaFollowUpDamageVar>(edge.DynamicVars["VkAgain"]);
        Assert.Contains("deal {VkAgain:diff()} additional damage", Face(edge));
        Assert.Equal(7m, Preview(edge.DynamicVars["VkAgain"], edge));
        var up = Upgraded<ProtoVkKindledEdge>();
        Assert.Equal(10m, Preview(up.DynamicVars["VkAgain"], up));
    }

    [Fact]
    public void Razors_electro_bonus_is_a_folded_bonus_on_the_same_hit()
    {
        var razor = new ProtoVkRazorClawAndThunder();
        var bonus = Assert.IsType<VarkaBonusDamageVar>(razor.DynamicVars["VkAmount"]);
        Assert.Equal(3m, bonus.BaseValue);
        Assert.Equal("VkBase", bonus.Source);
        Assert.Equal(Element.Electro, bonus.Carries);
        // Off a card nobody holds, the sheet number.
        Assert.Equal(3m, Preview(bonus, razor));
        Assert.Equal(3m, bonus.BaseValue);
    }

    [Fact]
    public void Blazing_charge_and_storm_battery_print_their_live_total()
    {
        var blazing = new ProtoVkBlazingCharge();
        var hit = Assert.IsType<VarkaHitDamageVar>(blazing.DynamicVars["VkHit"]);
        Assert.Equal(Element.Pyro, hit.OathElement);
        Assert.EndsWith("Oath[/gold].{InCombat:\n(Deals {VkHit:diff()} damage)|}"
                        + "{InCombat:{VarkaSwitch}|}{InCombat:{VarkaWildfire}|}",
                        Face(blazing));
        var battery = new ProtoVkStormBattery();
        Assert.IsType<VarkaStormBatteryDamageVar>(battery.DynamicVars["VkHit"]);
        Assert.Contains("[gold]Hand[/gold].{InCombat:\n(Deals {VkHit:diff()} damage)|}",
                        Face(battery));
        Assert.Equal(0, VarkaStormBatteryDamageVar.OthersInHand(battery));
    }
}
