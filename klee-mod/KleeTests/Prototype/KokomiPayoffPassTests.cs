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
        // the upgraded card's copy adds an upgraded Ward (one power for both
        // versions since the icon declutter, 2026-10-19).
        var card = new ProtoKkKurageCanopy();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Power, card.Type);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.False(card.DynamicVars.ContainsKey("PowerAmount"));
        var up = Upgraded<ProtoKkKurageCanopy>();
        Assert.Equal(1, up.EnergyCost.Canonical);
        // Kokomi defence pass (2026-10-22): Battle Formation's read.
        Assert.Equal("At the start of your turn, if 2 or more of your "
                   + "[gold]Plans[/gold] were carried out, add "
                   + "{IfUpgraded:show:an upgraded|a} [gold]Ward[/gold]. "
                   + "Stings and Wards don't count.",
                     Face(card));
        var play = Seq("ProtoKkKurageCanopy", "OnPlay");
        Assert.Contains(play, c => c.Contains("UpgradeTwinPower.Install"));
        Assert.Contains(play, c => c.Contains("get_IsUpgraded"));
    }

    [Fact]
    public void Kurage_canopy_reads_the_morning_once_not_the_plan_bus()
    {
        // Kokomi defence pass (2026-10-22): it left the plan bus (was a Ward
        // per carry-out) and reads Battle Formation's count once a morning.
        Assert.False(typeof(IKokomiPlanListener)
            .IsAssignableFrom(typeof(KurageCanopyPower)));
        // A Ward through the one jellyfish maker, whose full hand sends it to
        // the discard pile (Endless Shoal's rule).
        var hook = Seq("KurageCanopyPower", "Signal");
        Assert.Contains(hook, c => c.Contains("KokomiCards.AddJellyfish"));
        Assert.DoesNotContain(hook, c => c.Contains("CreatureCmd.GainBlock"));
    }

    // ---- Coral Tithe ---------------------------------------------------------

}
