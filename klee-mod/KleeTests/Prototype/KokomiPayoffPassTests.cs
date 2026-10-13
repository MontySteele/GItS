using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI PAYOFF PASS (2026-10-01). The main session recommended cutting
/// Second Thoughts ("an undo button, and an undo is a dead draw") alongside a
/// Plan-volume payoff that is not damage; [USER]: "Sounds good! Please
/// proceed!" Kurage Canopy (Block per carry-out) and Coral Tithe (the Casket
/// into Energy and cards) join the pool, which is 70. What awaits a command is
/// pinned off the compiled methods. Sim twin:
/// <c>tier0/tests/test_kokomi_payoff_pass.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiPayoffPassTests : IDisposable
{

    public KokomiPayoffPassTests() { }

    public void Dispose() { }

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

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    // ---- the offer -------------------------------------------------------

    // ---- Kurage Canopy -------------------------------------------------------

    [Fact]
    public void Kurage_canopy_is_a_one_cost_uncommon_power_that_makes_wards()
    {
        // Kokomi round 3 A-list (2026-10-13): "Whenever the Bake-Kurage
        // carries out a Plan, add a Ward to your Hand." (was 3 [4] Block);
        // the upgraded card installs the Plus power, whose Ward is upgraded.
        var card = new ProtoKkKurageCanopy();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Power, card.Type);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.False(card.DynamicVars.ContainsKey("PowerAmount"));
        var up = Upgraded<ProtoKkKurageCanopy>();
        Assert.Equal(1, up.EnergyCost.Canonical);
        Assert.Equal("Whenever the [gold]Bake-Kurage[/gold] carries out a "
                   + "[gold]Plan[/gold], add {IfUpgraded:show:an upgraded|a} "
                   + "[gold]Ward[/gold] to your [gold]Hand[/gold].",
                     Face(card));
        var play = Seq("ProtoKkKurageCanopy", "OnPlay");
        Assert.Contains(play, c => c.Contains("KurageCanopyPower"));
        Assert.Contains(play, c => c.Contains("KurageCanopyPlusPower"));
        Assert.Contains(play, c => c.Contains("get_IsUpgraded"));
    }

    [Fact]
    public void Kurage_canopy_rides_the_plan_bus_once_per_carry_out()
    {
        // The bus rings from ResolveEntry, which is ONE carry-out; the drain
        // calls it `times` times (Second Wave, Nereid's Ascension, All
        // Streams' gift), so a doubled carry-out pays twice.
        Assert.True(typeof(IKokomiPlanListener)
            .IsAssignableFrom(typeof(KurageCanopyPower)));
        Assert.True(typeof(IKokomiPlanListener)
            .IsAssignableFrom(typeof(KurageCanopyPlusPower)));
        // A Ward per carry-out through the one jellyfish maker, whose full
        // hand sends it to the discard pile (Endless Shoal's rule).
        var hook = Seq("KurageCanopyBasePower", "OnPlanResolved");
        Assert.Contains(hook, c => c.Contains("KokomiCards.AddJellyfish"));
        Assert.DoesNotContain(hook, c => c.Contains("CreatureCmd.GainBlock"));
        Assert.DoesNotContain(hook,
            c => c.Contains("KokomiOverhaulLedger.ClaimOncePerTurn"));
        Assert.Contains("IKokomiPlanListener.OnPlanResolved",
                        Seq("KokomiPlan", "ResolveEntry"));
        var drain = Seq("KokomiPlan", "Drain");
        var times = drain.FindIndex(c => c.Contains("KokomiPlan.CarryOutTimes"));
        var resolve = drain.FindIndex(c => c.Contains("KokomiPlan.ResolveEntry"));
        Assert.True(times >= 0 && resolve > times,
                    "the drain must carry an entry out `times` times");
        Assert.Contains(drain, c => c.Contains("Entry.get_Extra"));
    }

    // ---- Coral Tithe ---------------------------------------------------------

}
