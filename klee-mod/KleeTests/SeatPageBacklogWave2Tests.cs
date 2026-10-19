using System.Collections.Generic;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// SEAT PAGE BACKLOG, WAVE 2 (2026-10-19), the ledger's half. A kill with
/// no card behind it ("Mawler died at end of turn with no printed cause")
/// and a power a Skill puts on its own player (Wait For It... printed
/// "Nothing ... landed"). The page half is
/// <c>tier0/tests/test_seat_page_backlog_2026_10_19_wave2.py</c>.
/// </summary>
public class SeatPageBacklogWave2Tests
{
    private static List<Dictionary<string, object?>> Events(
        Dictionary<string, object?> row) =>
        (List<Dictionary<string, object?>>)row["events"]!;

    [Fact]
    public void A_death_outside_a_play_names_what_hit_it_last()
    {
        ResolutionLedger.ResetFight();
        ResolutionLedger.NoteDamageSource("7", "Poison");
        ResolutionLedger.NoteKill("Mawler", "7");

        var rows = ResolutionLedger.Snapshot();
        Assert.Single(rows);
        var events = Events(rows[0]);
        Assert.Single(events);
        Assert.Equal(ResolutionLedger.DiedOutsidePlay, events[0]["kind"]);
        Assert.Equal("died", events[0]["kind"]);
        Assert.Equal("Mawler", events[0]["target"]);
        Assert.Equal("Poison", events[0]["card"]);
        Assert.Equal("7", events[0]["combat_id"]);
    }

    [Fact]
    public void A_death_with_no_heard_source_still_prints_the_body()
    {
        ResolutionLedger.ResetFight();
        ResolutionLedger.NoteKill("Mawler", "7");

        var events = Events(ResolutionLedger.Snapshot()[0]);
        Assert.Equal("Mawler", events[0]["target"]);
        Assert.Equal("", events[0]["card"]);
    }

    [Fact]
    public void A_source_heard_inside_a_play_is_not_kept()
    {
        ResolutionLedger.ResetFight();
        ResolutionLedger.OpenPlay("strike", "Strike", false);
        ResolutionLedger.NoteDamageSource("7", "Strike");
        ResolutionLedger.ClosePlay();
        ResolutionLedger.NoteKill("Mawler", "7");

        var rows = ResolutionLedger.Snapshot();
        Assert.Equal("", Events(rows[^1])[0]["card"]);
    }

    [Fact]
    public void A_kill_inside_a_play_stays_on_the_card()
    {
        ResolutionLedger.ResetFight();
        ResolutionLedger.OpenPlay("strike", "Strike", false);
        ResolutionLedger.NoteKill("Mawler", "7");

        var rows = ResolutionLedger.Snapshot();
        Assert.Single(rows);
        Assert.Empty(Events(rows[0]));
        Assert.Single((List<Dictionary<string, object?>>)rows[0]["hits"]!);
    }

    [Fact]
    public void The_source_is_the_power_then_the_card_then_the_dealer()
    {
        Assert.Equal("Cycle of Seasons",
                     ResolutionLedger.SourceName("Cycle of Seasons", "X", "Y"));
        Assert.Equal("Shiv", ResolutionLedger.SourceName("", "Shiv", "Y"));
        Assert.Equal("Byrdonis", ResolutionLedger.SourceName("", "", "Byrdonis"));
        Assert.Equal("", ResolutionLedger.SourceName("", "", ""));
    }

    [Fact]
    public void The_damage_hook_feeds_the_source()
    {
        Assert.Contains("ResolutionLedger.NoteDamageSource",
                        Il.Calls(Il.Method("PlayTelemetryHooks",
                                           "BeforeDamageReceived")));
    }

    [Fact]
    public void A_power_on_the_player_is_filed_as_hers()
    {
        ResolutionLedger.ResetFight();
        ResolutionLedger.OpenPlay("wait", "Wait For It...", false);
        ResolutionLedger.NotePower("Klee", "Wait For It...", 2, "1",
                                   onPlayer: true);
        ResolutionLedger.NotePower("Mawler", "Weak", 1, "7");

        var applied = (List<Dictionary<string, object?>>)
            ResolutionLedger.Snapshot()[0]["applied"]!;
        Assert.Equal(2, applied.Count);
        Assert.Equal(true, applied[0]["on_player"]);
        Assert.Equal(false, applied[1]["on_player"]);
    }

    [Fact]
    public void The_power_hook_files_player_powers_too()
    {
        var calls = Il.Calls(Il.Method("PlayTelemetryHooks",
                                       "AfterPowerAmountChanged"));
        Assert.Contains("ResolutionLedger.get_PlayOpen", calls);
    }
}
