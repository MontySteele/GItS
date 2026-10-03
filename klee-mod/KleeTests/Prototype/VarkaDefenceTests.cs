#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// VARKA DEFENCE (<c>review/active/varka-defence-2026-10-01.md</c>, both
/// picks ruled 2026-10-01): Gale Mantle, Gust Ward and Windborne Resolve in
/// place of Squall, Four Banners and Favonian Standard; Oathbound Aegis at
/// half the total Oath, uncapped, upgrade a cost cut; Boreas's Fang makes the
/// starter Knight's element current at combat start. Arithmetic by value,
/// live sites by their call graph (<see cref="VarkaExpansionTests"/>' terms).
/// The sim twin is <c>tier0/tests/test_varka_defence.py</c>.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaDefenceTests : IDisposable
{
    public VarkaDefenceTests()
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

    private static List<string> Calls(string type, string method) =>
        Il.Calls(Il.Method(type, method)).ToList();

    // ---- sec.3: the three cards ----------------------------------------------

    [Fact]
    public void Gale_mantle_is_5_plus_half_the_total_oath()
    {
        var mantle = new ProtoVkGaleMantle();
        Assert.Equal(CardType.Skill, mantle.Type);
        Assert.Equal(CardRarity.Common, mantle.Rarity);
        Assert.Equal(1, mantle.EnergyCost.Canonical);
        Assert.Equal(5m, Var(mantle, "CalculationBase"));
        Assert.Equal(1m, Var(mantle, "CalculationExtra"));
        Assert.Equal(8m, Var(Upgraded<ProtoVkGaleMantle>(), "CalculationBase"));
        // Half rounds down; no cap; nothing for anyone else.
        var varka = Seat.Varka().Creature;
        var ledger = VarkaOathLedger.For(varka);
        Assert.Equal(0, VarkaOath.HalfTotalOath(varka));
        ledger.Add(Element.Pyro, 3);
        ledger.Add(Element.Hydro, 4);
        ledger.Add(Element.Electro, 2);
        Assert.Equal(4, VarkaOath.HalfTotalOath(varka));
        ledger.Add(Element.Cryo, 31);
        Assert.Equal(20, VarkaOath.HalfTotalOath(varka));
        Assert.Equal(0, VarkaOath.HalfTotalOath(Seat.Klee().Creature));
        Assert.Equal(0, VarkaOath.HalfTotalOath(null));
    }

    [Fact]
    public void Windborne_resolve_pays_block_on_every_change()
    {
        var resolve = new ProtoVkWindborneResolve();
        Assert.Equal(CardType.Power, resolve.Type);
        Assert.Equal(CardRarity.Uncommon, resolve.Rarity);
        Assert.Equal(1, resolve.EnergyCost.Canonical);
        Assert.Equal(5m, Var(resolve, "PowerAmount"));
        Assert.Equal(7m, Var(Upgraded<ProtoVkWindborneResolve>(), "PowerAmount"));
        Assert.Contains("PowerCmd.Apply",
                        Calls("ProtoVkWindborneResolve", "OnPlay"));
        // Paid on a change, after Cycle of Seasons, as unpowered Block.
        var set = Il.CallSequence(Il.Method("VarkaOath", "SetCurrent")).ToList();
        Assert.Contains("WindborneResolvePower.OnElementChanged", set);
        Assert.True(set.IndexOf("CycleOfSeasonsPower.OnElementChanged")
                    < set.IndexOf("WindborneResolvePower.OnElementChanged"));
        Assert.Contains("CreatureCmd.GainBlock",
                        Calls("WindborneResolvePower", "OnElementChanged"));
        Assert.Contains("{Amount}", ((ILocalizationProvider)new WindborneResolvePower())
            .Localization!.Single(l => l.Item1 == "description").Item2);
    }

    [Fact]
    public void Favonian_standard_left_with_its_card()
    {
        Assert.Null(typeof(VarkaOath).Assembly.GetType("KleeMod.Powers.FavonianStandardPower"));
        foreach (var gone in new[] { "ProtoVkSquall", "ProtoVkFourBanners",
                                     "ProtoVkFavonianStandard" })
        {
            Assert.Null(typeof(VarkaOath).Assembly.GetType(
                "KleeMod.Cards.Prototype.Generated." + gone));
        }
    }

    // ---- sec.3: Oathbound Aegis re-aimed ---------------------------------------

    [Fact]
    public void Oathbound_aegis_is_half_the_total_and_its_upgrade_a_cost_cut()
    {
        var aegis = new ProtoVkOathboundAegis();
        Assert.Equal(2, aegis.EnergyCost.Canonical);
        Assert.Equal(1, Upgraded<ProtoVkOathboundAegis>().EnergyCost
            .GetWithModifiers(CostModifiers.None));
        Assert.Equal(20, OathboundAegisPower.BlockFor(40, 1));
        Assert.Equal(20, OathboundAegisPower.BlockFor(41, 1));
        Assert.Equal(0, OathboundAegisPower.BlockFor(1, 1));
        Assert.DoesNotContain("up to", ((ILocalizationProvider)new OathboundAegisPower())
            .Localization!.Single(l => l.Item1 == "description").Item2);
    }

    // ---- sec.4: the Fang's starting element ------------------------------------

    [Fact]
    public void The_fang_sets_the_starter_element_on_turn_one_without_oath()
    {
        var calls = Il.CallSequence(Il.Method("BoreasFang", "AfterPlayerTurnStart")).ToList();
        Assert.Contains("VarkaArmRelics.FirstTurnOf", calls);
        Assert.Contains("BoreasFang.StartingElement", calls);
        Assert.Contains("VarkaOath.SetCurrent", calls);
        Assert.DoesNotContain("VarkaOath.Gain", calls);
        // The element: the run's record, else the starter Knight in the deck
        // (Knight's Commission's reading).
        var start = Il.CallSequence(Il.Method("BoreasFang", "StartingElement")).ToList();
        Assert.Contains("VarkaStarterKnight.Of", start);
        Assert.Contains("KnightsCommission.StartingElement", start);
        // Wolf's Gravestone is a Fang and inherits it.
        Assert.True(typeof(BoreasFang).IsAssignableFrom(typeof(WolfsGravestone)));
        var fang = (BoreasFang)RuntimeHelpers.GetUninitializedObject(typeof(BoreasFang));
        Assert.Contains("current element", ((ILocalizationProvider)fang)
            .Localization!.Single(l => l.Item1 == "description").Item2);
    }
}
