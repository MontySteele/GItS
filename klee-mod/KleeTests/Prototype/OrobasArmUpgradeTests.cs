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
/// and the Watatsumi Casket (the Tamakushi Casket upgraded, starting each
/// combat at 3). Each upgrade SUBCLASSES its starter, so every reader that
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


/// <summary>The Watatsumi Casket: the Tamakushi Casket, starting each combat
/// with 3.</summary>
[Collection(KleeOverhaulArm.Name)]
public class WatatsumiCasketTests : IDisposable
{

    public WatatsumiCasketTests()
    {
        KokomiOverhaulLedger.ResetAll();
    }

    public void Dispose()
    {
        KokomiOverhaulLedger.ResetAll();
    }

    [Fact]
    public void The_watatsumi_casket_starts_the_combat_at_three()
    {
        var seat = Seat.Kokomi().WithRelic<WatatsumiCasket>();
        TamakushiCasket.SeedOpeningCount(seat.Creature);
        Assert.Equal(3, KokomiOverhaulLedger.For(seat.Creature).CasketCount);
        Assert.Equal(3, WatatsumiCasket.WatatsumiOpeningCount);

        // The relic sits at the start of combat, before the jellyfish.
        var start = Il.CallSequence(Il.Method("TamakushiCasket", "BeforeCombatStart"))
            .ToList();
        var seed = start.IndexOf("TamakushiCasket.SeedOpeningCount");
        Assert.True(seed >= 0 && start.IndexOf("BakeKuragePet.Summon") > seed);
    }

    [Fact]
    public void The_tamakushi_casket_still_starts_at_zero()
    {
        var seat = Seat.Kokomi().WithRelic<TamakushiCasket>();
        TamakushiCasket.SeedOpeningCount(seat.Creature);
        Assert.Equal(0, KokomiOverhaulLedger.For(seat.Creature).CasketCount);
    }

    [Fact]
    public void It_counts_carry_outs_and_open_the_casket_reads_its_count()
    {
        var seat = Seat.Kokomi().WithRelic<WatatsumiCasket>();
        TamakushiCasket.SeedOpeningCount(seat.Creature);
        // The base relic's carry-out add finds the upgrade by type.
        TamakushiCasket.NoteCarriedOut(seat.Creature);
        Assert.Equal(4, KokomiOverhaulLedger.For(seat.Creature).CasketCount);

        // Open the Casket empties the one ledger every reader shares.
        Assert.Contains("KokomiOverhaulLedger.EmptyCasket",
            Il.CallSequence(Il.Method("KokomiOverhaulKit", "OpenCasket")));
        Assert.Equal(4, KokomiOverhaulLedger.For(seat.Creature).EmptyCasket());
        Assert.Equal(0, KokomiOverhaulLedger.For(seat.Creature).CasketCount);
    }

    [Fact]
    public void The_counter_and_the_token_are_the_base_relics()
    {
        foreach (var name in new[] { "get_ShowCounter", "get_DisplayAmount",
                                     "BeforeHandDraw", "BeforeCombatStart",
                                     "TryModifyCardRewardOptions" })
        {
            Assert.Equal(typeof(TamakushiCasket),
                typeof(WatatsumiCasket).GetMethod(name, HeadlessGame.All)!
                    .DeclaringType);
        }
        Assert.Equal(3, Bare().OpeningCount);
        Assert.Equal(0, ((TamakushiCasket)RuntimeHelpers
            .GetUninitializedObject(typeof(TamakushiCasket))).OpeningCount);
    }

    private static WatatsumiCasket Bare() =>
        (WatatsumiCasket)RuntimeHelpers.GetUninitializedObject(
            typeof(WatatsumiCasket));
}
