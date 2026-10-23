using System.Collections.Generic;
using System.Reflection;
using System.Text.RegularExpressions;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
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
        // Yae's Annotations have no keyed row yet (step 2 of the
        // localization census): their seat sentence is both readers'.
        Assert.Equal("SEAT", For(ArmKeywordTips.KeyOf(global::KleeMod.Powers.YaeAnnotation.RedInk), "SEAT"));
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
        // Two bodies that were seat-and-player sentences before the keying
        // (2026-10-23), measured by nothing then and longer than a box. The
        // text is unchanged on purpose (the keying is plumbing); an entry
        // that comes under the cap fails, so the list only shrinks.
        var longOk = new Dictionary<string, int>
        {
            [ArmKeywordTips.FullShrineKey] = 161,
            [ArmKeywordTips.BankDamageKey] = 116,
        };
        foreach (var (key, body) in bodies)
        {
            // A var renders as one numeral (the base game's measuring rule);
            // every other brace is a typo.
            var visible = Regex.Replace(Regex.Replace(body, @"\[/?(gold|blue)\]", ""),
                                        @"\{[A-Za-z]+\}", "6");
            if (longOk.TryGetValue(key, out var known)) Assert.Equal(known, visible.Length);
            else Assert.True(visible.Length <= 100, $"{key}: {visible.Length}");
            Assert.DoesNotContain("{", visible);
        }
    }

    [Fact]
    public void A_guest_tip_reads_its_cards_marker_and_not_its_face()
    {
        // The localization census (2026-10-23, group 3): the halves come
        // from the generator's marker; `CodeTextTests` pins every guest card
        // to the half the old English reading picked.
        Assert.True(typeof(IPrintsGuestAct).IsAssignableFrom(typeof(ProtoFsGuestStarCharlotte)));
        Assert.True(typeof(IPrintsGuestLine).IsAssignableFrom(typeof(ProtoFsGuestStarNavia)));
        Assert.False(typeof(IPrintsGuestAct).IsAssignableFrom(typeof(ProtoFsGuestStarChevreuse))
                     || typeof(IPrintsGuestLine).IsAssignableFrom(typeof(ProtoFsGuestStarChevreuse)));
        Assert.Null(Player.GetMethod("LineOpening", BindingFlags.Static | BindingFlags.NonPublic));
    }
}
