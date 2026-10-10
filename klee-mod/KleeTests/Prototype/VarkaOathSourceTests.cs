using System;
using System.Collections.Generic;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// WHERE EACH OATH GAIN CAME FROM (the Varka rebalance round,
/// <c>review/records/varka-rebalance-round-2026-10-03.md</c>): both act-1
/// seats could not tell which play granted Oath, so Four Winds' Ascension read
/// as an uncontrolled number. Every gain now names its source over his head
/// and under the card's row on the seat page. The line's grammar by value; the
/// live sites by their call graph.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaOathSourceTests : IDisposable
{
    public VarkaOathSourceTests()
    {
        HeadlessGame.Arm();
        VarkaOathLedger.ResetAll();
        ResolutionLedger.ResetFight();
    }

    public void Dispose()
    {
        VarkaOathLedger.ResetAll();
        ResolutionLedger.ResetFight();
    }

    [Fact]
    public void A_gain_names_its_source()
    {
        Assert.Equal("+1 Pyro Oath (applied)",
                     VarkaOath.GainClause(Element.Pyro, 1, OathSource.Applied));
        Assert.Equal("+1 Pyro Oath (Swirl)",
                     VarkaOath.GainClause(Element.Pyro, 1, OathSource.Swirl));
        Assert.Equal("+2 Hydro Oath",
                     VarkaOath.GainClause(Element.Hydro, 2, OathSource.Other));
    }

    [Fact]
    public void The_play_line_names_the_card_and_the_fang()
    {
        Assert.Equal("Amber: Precise Shot — +1 Pyro Oath (applied)",
                     VarkaOath.GainLine("Amber: Precise Shot",
                         new[] { "+1 Pyro Oath (applied)" }, fang: null));
        Assert.Equal(
            "Windbound Execution — +1 Pyro Oath (Swirl), +1 Pyro Oath. "
            + "Boreas's Fang: Four Winds' Ascension",
            VarkaOath.GainLine("Windbound Execution",
                new[] { "+1 Pyro Oath (Swirl)", "+1 Pyro Oath" },
                fang: "Boreas's Fang"));
        Assert.Equal(string.Empty,
                     VarkaOath.GainLine("Strike", Array.Empty<string>(),
                                        "Boreas's Fang"));
    }

    [Fact]
    public void The_play_line_names_the_relic_actually_held()
    {
        // The Varka payoff round (2026-10-10): after Orobas the line said
        // "Boreas's Fang" over Wolf's Gravestone's card.
        Assert.Equal("Boreas's Fang",
            ((global::KleeMod.Relics.BoreasFang)System.Runtime.CompilerServices
                .RuntimeHelpers.GetUninitializedObject(
                    typeof(global::KleeMod.Relics.BoreasFang))).RelicName);
        Assert.Equal("Wolf's Gravestone",
            ((global::KleeMod.Relics.BoreasFang)System.Runtime.CompilerServices
                .RuntimeHelpers.GetUninitializedObject(
                    typeof(global::KleeMod.Relics.WolfsGravestone))).RelicName);
        Assert.Equal(
            "Lunge — +1 Pyro Oath. Wolf's Gravestone: Four Winds' Ascension",
            VarkaOath.GainLine("Lunge", new[] { "+1 Pyro Oath" },
                               "Wolf's Gravestone"));
        var gain = Il.Calls(Il.Method("VarkaOath", "Gain"));
        Assert.Contains("BoreasFang.get_RelicName", gain);
    }

    [Fact]
    public void A_play_keeps_its_own_gains_and_the_next_play_starts_empty()
    {
        var ledger = new VarkaOathLedger();
        ledger.OpenScope(open: true);
        ledger.NoteGainClause("+1 Pyro Oath (applied)");
        ledger.NoteFangInPlay("Wolf's Gravestone");
        ledger.CloseScope();
        var (clauses, fang) = ledger.TakeGainClauses();
        Assert.Equal(new[] { "+1 Pyro Oath (applied)" }, clauses);
        Assert.Equal("Wolf's Gravestone", fang);
        Assert.Empty(ledger.GainClauses);
        Assert.Null(ledger.FangInThisPlay);

        // A stale clause never leaks into the next play.
        ledger.NoteGainClause("+1 Cryo Oath");
        ledger.OpenScope(open: true);
        Assert.Empty(ledger.GainClauses);
    }

    [Fact]
    public void The_seat_page_row_carries_each_gain_and_the_fang()
    {
        ResolutionLedger.OpenPlay("precise_shot", "Amber: Precise Shot", false);
        ResolutionLedger.NoteOath("Pyro", 1, "applied");
        ResolutionLedger.NoteFangAscension("Wolf's Gravestone");
        ResolutionLedger.ClosePlay();
        ResolutionLedger.OpenPlay("windbound", "Windbound Execution", false);
        ResolutionLedger.NoteOath("Pyro", 1, "Swirl");
        ResolutionLedger.ClosePlay();

        var rows = ResolutionLedger.Snapshot();
        var first = (List<Dictionary<string, object?>>)rows[0]["oath"]!;
        Assert.Equal("Pyro", first[0]["element"]);
        Assert.Equal(1, first[0]["amount"]);
        Assert.Equal("applied", first[0]["source"]);
        Assert.Equal(true, rows[0]["fang_ascension"]);
        Assert.Equal("Wolf's Gravestone", rows[0]["fang_relic"]);
        var second = (List<Dictionary<string, object?>>)rows[1]["oath"]!;
        Assert.Equal("Swirl", second[0]["source"]);
        Assert.Equal(false, rows[1]["fang_ascension"]);
    }

    [Fact]
    public void A_gain_outside_a_play_files_no_row()
    {
        ResolutionLedger.NoteOath("Pyro", 1, "");
        ResolutionLedger.NoteFangAscension();
        Assert.Empty(ResolutionLedger.Snapshot());
    }

    [Fact]
    public void Every_gain_reaches_the_row_and_the_badge_and_the_play_says_it()
    {
        var gain = Il.Calls(Il.Method("VarkaOath", "Gain"));
        Assert.Contains("ResolutionLedger.NoteOath", gain);
        Assert.Contains("ResolutionLedger.NoteFangAscension", gain);
        Assert.Contains("OathBadgePower.Pulse", gain);
        Assert.Contains("KurageBeat.Say",
                        Il.Calls(Il.Method("VarkaOath", "EndPlay")));
    }
}
