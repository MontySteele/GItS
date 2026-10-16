using System.Collections.Generic;
using System.Reflection;
using System.Text.RegularExpressions;
using KleeMod.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The tooltip trim (2026-10-14, review/active/tooltip-trim-2026-10-14.md):
/// a player reads <c>PlayerTips</c>' short words, a blind seat (through the
/// bridge's <see cref="TipAudience"/> scope) reads the seat sentence, word for
/// word. What is pinned here is the switch; which boxes a card raises is the
/// generator's (`tier0`) and `tools/lint_hover_tips.py`'s.
/// </summary>
public class TooltipTrimTests
{
    private static readonly System.Type Player =
        typeof(ArmKeywordTips).Assembly.GetType("KleeMod.Cards.PlayerTips")!;

    private static string For(string key, string seat) =>
        (string)Player.GetMethod("For", BindingFlags.Static | BindingFlags.NonPublic)!
            .Invoke(null, new object[] { key, seat })!;

    [Fact]
    public void A_player_reads_the_short_words_and_a_seat_the_seat_sentence()
    {
        Assert.False(TipAudience.Seat);
        var player = For(ArmKeywordTips.BombKey, "SEAT");
        Assert.NotEqual("SEAT", player);
        Assert.Contains("Set off", player);
        using (TipAudience.AsSeat())
        {
            Assert.True(TipAudience.Seat);
            Assert.Equal("SEAT", For(ArmKeywordTips.BombKey, "SEAT"));
        }
        Assert.False(TipAudience.Seat);
    }

    [Fact]
    public void A_key_with_no_player_words_prints_its_seat_sentence_to_both()
    {
        Assert.Equal("SEAT", For(ArmKeywordTips.MendKey, "SEAT"));
    }

    [Fact]
    public void Seat_scopes_nest_and_an_extra_exit_cannot_go_negative()
    {
        TipAudience.EnterSeat();
        TipAudience.EnterSeat();
        TipAudience.ExitSeat();
        Assert.True(TipAudience.Seat);
        TipAudience.ExitSeat();
        TipAudience.ExitSeat();
        Assert.False(TipAudience.Seat);
        TipAudience.EnterSeat();
        Assert.True(TipAudience.Seat);
        TipAudience.ExitSeat();
        Assert.False(TipAudience.Seat);
    }

    [Fact]
    public void Every_player_body_is_one_short_box()
    {
        var bodies = (Dictionary<string, string>)Player
            .GetField("Bodies", BindingFlags.Static | BindingFlags.NonPublic)!
            .GetValue(null)!;
        Assert.NotEmpty(bodies);
        foreach (var (key, body) in bodies)
        {
            var visible = Regex.Replace(body, @"\[/?(gold|blue)\]", "");
            Assert.True(visible.Length <= 100, $"{key}: {visible.Length}");
            Assert.DoesNotContain("{", body);
        }
    }

    [Fact]
    public void A_guest_line_opening_stops_at_its_number()
    {
        var opening = (string)Player
            .GetMethod("LineOpening", BindingFlags.Static | BindingFlags.NonPublic)!
            .Invoke(null, new object[] { "Your first [gold]Spend[/gold] each turn costs 2 less." })!;
        Assert.Equal("Your first [gold]Spend[/gold] each turn costs ", opening);
    }
}
