using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// YAE REVIEW R1 PICKS (ruled 2026-10-14;
/// <c>review/active/yae-design-axes-2026-10-14.md</c>, "Review r1, ruled
/// 2026-10-14"). Pick 1 (a), LAST BLOOM: a Sakura that withers strikes once
/// more under the current Rite, then leaves, and Fallen Petals banks it
/// after. Pick 2: Levels have no cap; Fox's Mooncall plants 1 Level higher
/// per copy; Sakura Grove levels the newest Sakura at her turn start; Mikage
/// Thunder levels every Sakura, then Tenko. Headless, so the ledger is read
/// by value and the door's order off its IL. Sim twin:
/// <c>tier0/tests/test_yae_review_r1_picks.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeReviewR1PicksTests : IDisposable
{
    public YaeReviewR1PicksTests()
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

    // ==== Last Bloom ========================================================

    [Fact]
    public void A_run_out_sakura_is_still_standing_until_it_withers()
    {
        var ledger = Fresh();
        ledger.Plant(YaeLaw.PlantLevel);
        ledger.Tick();
        ledger.Tick();
        var due = ledger.Tick();
        var s = Assert.Single(due);
        // It blooms from here: still standing, nothing banked yet.
        Assert.Single(ledger.Standing);
        Assert.Equal(0, ledger.PendingWithers);
        ledger.Wither(s);
        Assert.Equal(0, ledger.Count);
        Assert.Equal(1, ledger.PendingWithers);   // Fallen Petals, after
    }

    [Fact]
    public void The_bloom_is_a_normal_strike_then_the_wither()
    {
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(
            nameof(YaeShrine.TickAndBloom))!).ToList();
        var tick = calls.FindIndex(c => c.Contains(nameof(YaeShrineLedger.Tick)));
        var strike = calls.FindIndex(c => c.Contains(nameof(YaeShrine.Strike)));
        var wither = calls.FindIndex(c => c.Contains(nameof(YaeShrineLedger.Wither)));
        Assert.True(tick >= 0 && strike > tick && wither > strike, string.Join(", ", calls));
    }

    [Fact]
    public void The_bloom_strikes_under_whatever_rite_the_shrine_holds()
    {
        // Strike reads the shrine's Rite; the bloom passes none of its own,
        // so it is the current Rite's strike in each of the four.
        foreach (var rite in Enum.GetValues<YaeRite>())
        {
            Assert.True(YaeShrineLedger.StrikeSize(rite, 2, YaeAnnotation.None) > 0);
        }
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Strike))!).ToList();
        Assert.Contains(calls, c => c.Contains("get_Rite"));
    }

    [Fact]
    public void Deadline_extension_never_runs_out_so_never_blooms()
    {
        var ledger = Fresh();
        ledger.Plant(YaeLaw.PlantLevel);
        ledger.EditSakura(YaeSakuraEnd.Every, 1, YaeAnnotation.DeadlineExtension);
        for (var i = 0; i < 6; i++) Assert.Empty(ledger.Tick());
        Assert.Single(ledger.Standing);
        Assert.Equal(0, ledger.PendingWithers);
    }

    [Fact]
    public void The_sakura_tip_says_it_strikes_once_more()
    {
        Assert.Contains("when it withers, it strikes once more",
                        ArmKeywordTips.YaeSakuraTip);
        Assert.DoesNotContain("(up to", ArmKeywordTips.YaeSakuraTip);
    }

    // ==== No Level cap ======================================================

    [Fact]
    public void Levels_go_past_three()
    {
        var ledger = Fresh();
        for (var i = 0; i < 5; i++) ledger.Plant(YaeLaw.PlantLevel);
        Assert.Equal(new[] { 5, 4, 3 }, ledger.Standing.Select(s => s.Level));
        ledger.LevelUp(2);
        Assert.Equal(new[] { 7, 6, 5 }, ledger.Standing.Select(s => s.Level));
        Assert.Equal(9 + 8 + 7, YaeShrineFace.Total(ledger.Standing, YaeRite.Thunder));
    }

    [Fact]
    public void Mooncall_reads_its_amount_so_copies_stack()
    {
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.PlantLevel))!).ToList();
        Assert.Contains(calls, c => c.Contains("GetPowerAmount"));
        // Two copies: planted at 1 + 2 = Level 3.
        var ledger = Fresh();
        ledger.Plant(YaeLaw.PlantLevel + 2);
        Assert.Equal(3, ledger.Standing[0].Level);
        Assert.Equal("Your [gold]Sakura[/gold] are planted 1 Level higher.",
                     Face(new ProtoYmFoxsMooncall()));
    }

    [Fact]
    public void Grove_levels_only_the_newest()
    {
        var ledger = Fresh();
        ledger.LevelUpNewest(1);                  // none standing: nothing
        ledger.Plant(YaeLaw.PlantLevel);
        ledger.Plant(YaeLaw.PlantLevel);          // 2 / 1
        ledger.LevelUpNewest(1);
        Assert.Equal(new[] { 2, 2 }, ledger.Standing.Select(s => s.Level));
        ledger.LevelUpNewest(2);                  // two copies
        Assert.Equal(new[] { 2, 4 }, ledger.Standing.Select(s => s.Level));
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.TurnStart))!).ToList();
        Assert.Contains(calls, c => c.Contains("SakuraGrovePower"));
    }

    [Fact]
    public void Grove_upgrade_is_innate()
    {
        var card = new ProtoYmSakuraGrove();
        Assert.Equal("At the start of your turn, your newest [gold]Sakura[/gold] gains a Level.",
                     Face(card));
        Assert.Contains(Il.Calls(Il.Method(nameof(ProtoYmSakuraGrove), "OnUpgrade")),
                        c => c.Contains("AddKeyword"));
    }

    [Fact]
    public void Mikage_levels_then_tenkos()
    {
        var calls = Il.CallSequence(typeof(ProtoYmMikageThunder).GetMethod(
            "OnPlay", HeadlessGame.All)!).ToList();
        var level = calls.FindIndex(c => c.Contains("YaeCards.LevelUp"));
        var tenko = calls.FindIndex(c => c.Contains("YaeCards.Tenko"));
        Assert.True(level >= 0 && tenko > level, string.Join(", ", calls));
        Assert.StartsWith("Each [gold]Sakura[/gold] gains {IfUpgraded:show:2 Levels|a Level}. ",
                          Face(new ProtoYmMikageThunder()));
    }
}
