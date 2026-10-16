using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI PRE-RUN FIXES (2026-10-12), from the Fable round-3 review sec.4:
/// Treatise names its draw and flashes, the Companion Plan tip says a written
/// Companion is played (so Strength and Weak count), Tide Wall's face says
/// when the intent is read, the Casket said when a Plan's Block arrives (the
/// Ancient audit, 2026-10-12, dropped that sentence again), and
/// Nereid's tip says an early carry-out is single. No number moves. Page
/// twin: <c>tier0/tests/test_kokomi_prerun_fixes_2026_10_12.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiPreRunFixesTests
{
    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    [Fact]
    public void Treatise_flashes_and_names_itself_as_the_draws_source()
    {
        var calls = Il.CallSequence(
            Il.Method("TreatisePower", "AfterCardPlayed")).ToList();
        var flash = calls.FindIndex(c => c.Contains("Flash"));
        var set = calls.FindIndex(c => c.Contains("set_DrawSource"));
        var draw = calls.FindIndex(c => c.Contains("CardPileCmd.Draw"));
        Assert.True(flash >= 0 && set >= 0 && draw > set);
        Assert.Contains("Treatise", Il.Strings(
            Il.Method("TreatisePower", "AfterCardPlayed")));
        // The draw hook files the source as the event's power.
        Assert.Contains(Il.Calls(Il.Method("PlayTelemetryHooks",
                                           "AfterCardDrawn")),
                        c => c.Contains("get_DrawSource"));
        Assert.Equal(string.Empty, ResolutionLedger.DrawSource);
    }

    [Fact]
    public void Treatise_counts_her_plan_cards_and_its_latch_reopens_each_turn()
    {
        // Round 4 lane 4 read Treatise as never drawing; every turn without
        // a draw was a turn its Plan cards were WRITTEN, which by rule draws
        // nothing (the gate order is pinned in KokomiCorePassTests). The
        // cards it played directly qualify, a generated Sting included...
        Assert.True(KokomiRefounding.CanBeWritten(new ProtoKkBrineSting()));
        Assert.True(KokomiRefounding.CanBeWritten(new ProtoKkKuragesOath()));
        Assert.True(KokomiRefounding.CanBeWritten(new ProtoKkSting()));
        Assert.False(KokomiRefounding.CanBeWritten(new ProtoKkJellyfishDrift()));
        // ...and the once-a-turn claim reopens on every new round.
        var ledger = new KokomiOverhaulLedger();
        ledger.RollTo(1);
        Assert.True(ledger.Claim(nameof(TreatisePower)));
        Assert.False(ledger.Claim(nameof(TreatisePower)));
        ledger.RollTo(2);
        Assert.True(ledger.Claim(nameof(TreatisePower)));
        ledger.RollTo(5);
        Assert.True(ledger.Claim(nameof(TreatisePower)));
    }

    [Fact]
    public void Nereids_tip_says_an_early_carry_out_is_single()
    {
        var said = string.Join(" ", Il.Strings(
            Il.Method("ArmKeywordTips", "ForNereidsTwice")));
        Assert.Contains("carried out early is carried out once.", said);
    }

    [Fact]
    public void Tide_wall_says_when_the_intent_is_read()
    {
        // Reworded in the Kokomi review (2026-10-13).
        Assert.EndsWith("plus the biggest attack an enemy intends on the "
                      + "turn it lands.", Face(new ProtoKkTideWall()));
    }

    [Fact]
    public void The_casket_face_is_one_sentence_again()
    {
        // The Ancient audit (ruled 2026-10-12) dropped "A Plan's own Block
        // comes at the start of your next turn."
        Assert.DoesNotContain("own [gold]Block[/gold]", new TamakushiCasket()
            .Localization!.First(r => r.Item1 == "description").Item2);
    }
}
