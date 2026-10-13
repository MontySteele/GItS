using System;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Relics;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// TOUCH OF OROBAS FOR THE PROTOTYPE ARMS (2026-09-30). [USER]'s co-op
/// playtest: "Varka and Kokomi need Ancient relics for Orobas" -- both
/// starters fell through BaseLib's <c>GetUpgradeReplacement()</c> to the
/// Circlet. Main-session design: Wolf's Gravestone (Boreas's Fang upgraded)
/// and the Watatsumi Casket (the Tamakushi Casket upgraded; since the
/// re-founding, 2026-10-12, 5 Block in place of 3). Each upgrade SUBCLASSES its starter, so every reader that
/// finds the starter by type finds the upgrade.
///
/// <c>ModelDb</c> is not booted headless, so the hand-over is pinned off the
/// compiled getter (the Salon Solitaire pin's shape); the Casket's count runs
/// for real on a headless seat. Sim twins: <c>tier0/tests/test_varka_oath.py</c>
/// (the upgraded Fang) and <c>tier0/tests/test_starter_relic_upgrades.py</c>.
/// </summary>
public class OrobasArmUpgradeTests
{
    private static T Bare<T>() where T : class =>
        (T)RuntimeHelpers.GetUninitializedObject(typeof(T));

    [Theory]
    [InlineData("BoreasFang", "WolfsGravestone")]
    [InlineData("TamakushiCasket", "WatatsumiCasket")]
    public void Orobas_hands_each_starter_its_own_upgrade(
        string starter, string upgraded)
    {
        Assert.Contains($"ModelDb.Relic<{upgraded}>",
            Il.CallSequence(Il.Method(starter, "GetUpgradeReplacement")));
    }

    [Fact]
    public void The_upgrades_are_ancient_subclasses_that_upgrade_no_further()
    {
        Assert.Equal(typeof(BoreasFang), typeof(WolfsGravestone).BaseType);
        Assert.Equal(typeof(TamakushiCasket), typeof(WatatsumiCasket).BaseType);

        // Ancient, never Starter: a second Orobas finds its target by Starter
        // rarity, and the starters themselves stay Starter.
        Assert.Equal(RelicRarity.Ancient, Bare<WolfsGravestone>().Rarity);
        Assert.Equal(RelicRarity.Ancient, Bare<WatatsumiCasket>().Rarity);
        Assert.Equal(RelicRarity.Starter, Bare<BoreasFang>().Rarity);
        Assert.Equal(RelicRarity.Starter, Bare<TamakushiCasket>().Rarity);
        Assert.Null(Bare<WolfsGravestone>().GetUpgradeReplacement());
        Assert.Null(Bare<WatatsumiCasket>().GetUpgradeReplacement());
    }

    [Fact]
    public void Both_upgrades_are_members_of_their_pools()
    {
        Assert.Contains("ModelDb.Relic<WolfsGravestone>",
            Il.CallSequence(Il.Method("VarkaRelicPool", "GenerateAllRelics")));
        Assert.Contains("ModelDb.Relic<WatatsumiCasket>",
            Il.CallSequence(Il.Method("KokomiRelicPool", "GenerateAllRelics")));
    }
}

/// <summary>Wolf's Gravestone: "The first time each combat you gain Oath, add
/// an upgraded Four Winds' Ascension to your hand. It costs 0 this turn."
/// </summary>
[Collection(VarkaArm.Name)]
public class WolfsGravestoneTests : IDisposable
{
    public WolfsGravestoneTests()
    {
        HeadlessGame.Arm();
        VarkaOathLedger.ResetAll();
    }

    public void Dispose()
    {
        VarkaOathLedger.ResetAll();
    }

    [Fact]
    public void The_oath_rule_finds_the_gravestone_as_it_finds_the_fang()
    {
        var seat = Seat.Varka().WithRelic<WolfsGravestone>();
        Assert.IsType<WolfsGravestone>(BoreasFang.HeldBy(seat.Player));
        Assert.True(BoreasFang.HeldBy(seat.Player)!.AscensionUpgraded);

        var fang = Seat.Varka().WithRelic<BoreasFang>();
        Assert.False(BoreasFang.HeldBy(fang.Player)!.AscensionUpgraded);
    }

    [Fact]
    public void Ascension_comes_upgraded_and_free_this_turn_from_the_one_path()
    {
        // One method makes the card for both relics; the Gravestone does not
        // override it.
        Assert.Equal(typeof(BoreasFang),
            typeof(WolfsGravestone).GetMethod("AddAscension", HeadlessGame.All)!
                .DeclaringType);
        var add = Il.CallSequence(Il.Method("BoreasFang", "AddAscension")).ToList();
        var upgrade = add.FindIndex(c => c.EndsWith(".UpgradeInternal"));
        var hand = add.FindIndex(c => c == "CardPileCmd.AddGeneratedCardToCombat");
        var free = add.FindIndex(c => c.EndsWith(".SetThisTurn"));
        Assert.True(upgrade >= 0 && hand > upgrade && free > hand,
            string.Join(", ", add));
    }

    [Fact]
    public void Only_the_first_oath_gain_each_combat_adds_it()
    {
        // The per-combat latch is the Fang's, set before the card is made, so
        // the Gravestone (which IS a Fang) fires once as the Fang does.
        Assert.False(VarkaOathLedger.For(Seat.Varka().Creature).FangFired);
        var gain = Il.CallSequence(Il.Method("VarkaOath", "Gain")).ToList();
        var held = gain.IndexOf("BoreasFang.HeldBy");
        var latch = gain.IndexOf("VarkaOathLedger.set_FangFired");
        var add = gain.IndexOf("BoreasFang.AddAscension");
        Assert.True(gain.Contains("VarkaOathLedger.get_FangFired")
                    && held >= 0 && latch > held && add > latch,
            string.Join(", ", gain));
    }
}


/// <summary>The Kokomi re-founding (2026-10-12): the Tamakushi Casket is
/// "At the start of your turn, if a Plan is waiting, gain 3 Block." (start,
/// not end, since 2026-10-12); the
/// Watatsumi Casket is the same sentence at 5 Block.</summary>
public class WatatsumiCasketTests
{
    private static T Bare<T>() where T : class =>
        (T)RuntimeHelpers.GetUninitializedObject(typeof(T));

    private static string Face(TamakushiCasket relic) =>
        relic.Localization!.First(r => r.Item1 == "description").Item2;

    [Fact]
    public void The_casket_pays_3_block_and_the_watatsumi_casket_5()
    {
        Assert.Equal(3, Bare<TamakushiCasket>().Block);
        Assert.Equal(5, Bare<WatatsumiCasket>().Block);
        Assert.Equal(5, WatatsumiCasket.WatatsumiBlock);
        Assert.Equal(
            "At the start of your turn, if a [gold]Plan[/gold] is waiting, gain "
          + "[blue]3[/blue] [gold]Block[/gold]." + KokomiPreRunFixesTests.CasketTail,
            Face(Bare<TamakushiCasket>()));
        Assert.Equal(
            "At the start of your turn, if a [gold]Plan[/gold] is waiting, gain "
          + "[blue]5[/blue] [gold]Block[/gold]." + KokomiPreRunFixesTests.CasketTail,
            Face(Bare<WatatsumiCasket>()));
    }

    [Fact]
    public void It_pays_only_while_a_plan_is_waiting()
    {
        Assert.False(TamakushiCasket.Pays(0));
        Assert.True(TamakushiCasket.Pays(1));
        Assert.True(TamakushiCasket.Pays(3));
        var turnStart = Il.Calls(Il.Method("TamakushiCasket", "AfterBlockCleared"));
        Assert.Contains(turnStart, c => c.Contains("KokomiPlan.PlansHeld"));
        Assert.Contains(turnStart, c => c.Contains("CreatureCmd.GainBlock"));
    }
}
