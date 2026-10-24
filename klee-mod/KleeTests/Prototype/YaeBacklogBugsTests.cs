using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// YAE SEAT FINDINGS, ROUNDS 7 TO 10 (2026-10-16/17), the mod half. The page
/// half is <c>tier0/tests/test_yae_backlog_bugs_2026_10_17.py</c>.
///   * An Edit files a receipt on its play line: the card and Annotation,
///     with "the game picked it" when a one-card Edit had one card it could
///     reach (<c>CardSelectCmd.FromHand</c> takes it without asking); the
///     Sakura an "Edit ... Sakura" card reached; a hand Edit that found
///     nothing.
///   * The shrine snapshot carries the game's cap (<c>MaxSakura</c>, Fox
///     Ofuda included), so the page's "full" is Torii Ward's.
///   * The Tenko clause names the Sakura; Saiguu's Lesson says "a striking
///     Sakura".
/// </summary>
[Collection(YaeArm.Name)]
public class YaeBacklogBugsTests : IDisposable
{
    public YaeBacklogBugsTests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
        ResolutionLedger.ResetFight();
    }

    public void Dispose()
    {
        YaeShrineLedger.ResetAll();
        ResolutionLedger.ResetFight();
    }

    [Fact]
    public void A_one_card_edit_with_one_reachable_card_is_picked_for_you()
    {
        Assert.True(YaeEditing.EditPickedForYou(1, 1));
        Assert.False(YaeEditing.EditPickedForYou(2, 1));
        // "Up to N" opens its chooser whatever the hand holds (min 0).
        Assert.False(YaeEditing.EditPickedForYou(1, 2));
    }

    [Fact]
    public void The_edit_receipts_are_filed_on_the_play_line()
    {
        ResolutionLedger.OpenPlay("X", "Inked Branches+", false);
        YaeEditing.NoteSakuraEdited("Inked Branches+", 2, YaeAnnotation.RedInk);
        YaeEditing.NoteNothingEdited("Inked Branches+", YaeAnnotation.RedInk);
        YaeEditing.NoteEdited("Inked Branches+", "Strike", YaeAnnotation.RedInk, true);
        // No Sakura reached files nothing.
        YaeEditing.NoteSakuraEdited("Inked Branches+", 0, YaeAnnotation.RedInk);
        ResolutionLedger.ClosePlay();
        var row = Assert.Single(ResolutionLedger.Snapshot());
        var events = Assert.IsType<List<Dictionary<string, object?>>>(row["events"]);
        Assert.Equal(new[] { "yae_edit_sakura", "yae_edit_none", "yae_edit" },
                     events.Select(e => (string?)e["kind"]));
        Assert.All(events, e => Assert.Equal("Red Ink", e["power"]));
        Assert.Equal(2, events[0]["amount"]);
        Assert.Equal("Strike", events[2]["card"]);
        Assert.Equal(1, events[2]["amount"]);
    }

    [Fact]
    public void Every_hand_edit_and_the_sakura_edit_file_receipts()
    {
        foreach (var name in new[] { nameof(YaeEditing.Edit), nameof(YaeEditing.EditOneFor) })
        {
            var calls = Il.Calls(typeof(YaeEditing).GetMethod(name)!);
            Assert.Contains(calls, c => c.Contains(nameof(YaeEditing.NoteEdited)));
            Assert.Contains(calls, c => c.Contains(nameof(YaeEditing.EditPickedForYou)));
        }
        Assert.Contains(Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.Edit))!),
                        c => c.Contains(nameof(YaeEditing.NoteNothingEdited)));
        Assert.Contains(Il.Calls(typeof(YaeCards).GetMethod(nameof(YaeCards.EditSakura))!),
                        c => c.Contains(nameof(YaeEditing.NoteSakuraEdited)));
    }

    [Fact]
    public void The_snapshot_carries_the_games_cap()
    {
        var calls = Il.Calls(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Snapshot))!);
        Assert.Contains(calls, c => c.Contains(nameof(YaeShrine.MaxSakura)));
        var full = Il.Calls(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Full))!);
        Assert.Contains(full, c => c.Contains(nameof(YaeShrine.MaxSakura)));
    }

    [Fact]
    public void The_tenko_clause_names_the_sakura()
    {
        Assert.Equal(" (Sakura: 13 damage in total)", YaeShrineFace.TenkoWords(13));
        Assert.Equal(" (no Sakura)", YaeShrineFace.TenkoWords(0));
    }
}
