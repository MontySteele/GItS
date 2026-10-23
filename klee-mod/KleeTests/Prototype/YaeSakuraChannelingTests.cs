using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// SAKURA CHANNELING (designed by the main session 2026-10-14: [USER] judged
/// Yae "generally underpowered right now"; the card that bends the 3-Sakura
/// limit, an Uncommon since the upgrade census, 2026-10-23): "You can have
/// 2 [3] more Sakura." Its amount, 2 [3] per copy, raises the
/// shrine's cap for the combat (<see cref="YaeShrine.MaxSakura"/>), and the
/// full-shrine plant fires at the new cap. Headless, so the ledger is read by
/// value and the door off its IL. Sim twin:
/// <c>tier0/tests/test_yae_shrine.py</c> (the Channeling tests).
/// </summary>
[Collection(YaeArm.Name)]
public class YaeSakuraChannelingTests : IDisposable
{
    public YaeSakuraChannelingTests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose()
    {
        YaeShrineLedger.ResetAll();
    }

    private static YaeShrineLedger Fresh() => YaeShrineLedger.For(Seat.Yae().Creature);

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    [Fact]
    public void The_card_says_two_more_sakura_and_applies_two_per_copy()
    {
        // Upgrade census (2026-10-23, [USER]): Uncommon, 1, 2 [3] more, as
        // Defect's Capacitor (was Rare, 2 [1]).
        var card = new ProtoYmSakuraChanneling();
        Assert.Equal("You can have {PowerAmount:diff()} more [gold]Sakura[/gold].", Face(card));
        Assert.Equal((1, CardRarity.Uncommon), (card.EnergyCost.Canonical, card.Rarity));
        Assert.Equal(2m, card.DynamicVars["PowerAmount"].BaseValue);
        var plus = new ProtoYmSakuraChanneling();
        Seat.Set(plus, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(plus, Array.Empty<object>());
        Assert.Equal((1, 3m), (plus.EnergyCost.Canonical, plus.DynamicVars["PowerAmount"].BaseValue));
        Assert.Contains(Il.CallSequence(Il.Method(nameof(ProtoYmSakuraChanneling), "OnPlay")),
                        c => c.Contains("SakuraChannelingPower"));
        var power = new SakuraChannelingPower();
        Assert.Equal(PowerStackType.Counter, power.StackType);
        Assert.Equal("You can have [blue]{Amount}[/blue] more [gold]Sakura[/gold].",
                     power.Localization!.First(r => r.Item1 == "description").Item2);
    }

    [Fact]
    public void The_cap_is_three_plus_channelings_amount()
    {
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.MaxSakura))!).ToList();
        Assert.Contains(calls, c => c.Contains("GetPowerAmount") && c.Contains("SakuraChannelingPower"));
        // The door plants at that cap.
        Assert.Contains(Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Plant))!),
                        c => c.Contains(nameof(YaeShrine.MaxSakura)));
        Assert.Equal(3, YaeShrine.MaxSakura(Seat.Yae().Creature));
    }

    [Fact]
    public void One_copy_holds_five_and_two_hold_seven()
    {
        var ledger = Fresh();
        for (var i = 0; i < 5; i++)
            Assert.True(ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.None, YaeLaw.SakuraCap + 2));
        Assert.Equal(5, ledger.Count);
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.None, YaeLaw.SakuraCap + 4));
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.None, YaeLaw.SakuraCap + 4));
        Assert.Equal(7, ledger.Count);
        Assert.All(ledger.Standing, s => Assert.Equal(1, s.Level));
    }

    [Fact]
    public void The_full_shrine_rule_fires_at_the_new_cap()
    {
        var ledger = Fresh();
        const int cap = YaeLaw.SakuraCap + 2;
        for (var i = 0; i < cap; i++)
            ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.None, cap);
        Assert.Empty(ledger.Tick());                 // every timer at 2
        Assert.False(ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.None, cap));
        Assert.Equal(cap, ledger.Count);
        Assert.Equal(new[] { 2, 1, 1, 1, 1 }, ledger.Standing.Select(s => s.Level));
        Assert.Equal(YaeLaw.SakuraTurns, ledger.Standing[0].TurnsLeft);
    }

    [Fact]
    public void A_full_shrine_plant_makes_the_oldest_act_first_as_its_last_bloom()
    {
        // [USER] (2026-10-14): "when you plant a Sakura with 3 already on the
        // field, do you think the outgoing Sakura should strike as though
        // withered?" Review r3: it ACTS as its kind, before the ledger levels
        // it (same kind) or withers it (another kind), once per plant, at the
        // live cap.
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Plant))!).ToList();
        var cap = calls.FindIndex(c => c == "YaeShrine.MaxSakura");
        var act = calls.FindIndex(c => c == "YaeShrine.Act");
        var plant = calls.FindIndex(c => c == "YaeShrineLedger.Plant");
        Assert.True(cap >= 0, string.Join(", ", calls));
        Assert.True(act > cap, string.Join(", ", calls));
        Assert.True(plant > act, string.Join(", ", calls));
    }

    [Fact]
    public void The_plant_faces_leave_the_full_shrine_rule_to_its_tip()
    {
        // Review r3: the rule has two branches by kind, so it is the Full
        // shrine tip every planting card carries.
        foreach (var card in new CardModel[] { new ProtoYmYakanEvocation(), new ProtoYmTwinSakura() })
        {
            Assert.DoesNotContain("shrine full", Face(card));
        }
    }
}
