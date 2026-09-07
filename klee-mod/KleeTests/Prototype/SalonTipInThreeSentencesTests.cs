using System;
using System.Linq;
using System.Text.RegularExpressions;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-629`: THE SALON TIP IN THREE SENTENCES.
///
/// THE FIND. [USER]'s own Furina act-1 run, 2026-09-07: the Salon tooltip is
/// "still a gigantic wall of text" -- about 700 characters carrying seven
/// rules, printed at the moment a player is deciding whether to play one card.
/// Seven rules on one tip is not seven rules read; it is one tip skipped.
///
/// WHAT STAYS: the cap, what performs, and the bonus -- the three a player
/// cannot act without. WHAT MOVES: the aim, the damage class and the dry cut,
/// all facts about a member about to perform, to the member's own tip. WHAT
/// LEAVES TEXT ENTIRELY: "the leftmost member is the front", because `EB-627`
/// draws a frame round chip 0 and a rule the player can see does not need a
/// sentence.
///
/// NOTHING IS DELETED FROM THE MOD'S TEXT AS A WHOLE, and the last section
/// below is the assertion of exactly that.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class SalonTipInThreeSentencesTests
{
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;

        internal Arm(bool master = true)
        {
            FurinaReframe.Enabled = master;
            FurinaReframe.ManualEnabled = master;
        }

        public void Dispose()
        {
            FurinaReframe.Enabled = _enabled;
            FurinaReframe.ManualEnabled = _manual;
        }
    }

    /// <summary>The paragraph WITHOUT its live tail. `SalonRulesBody` appends
    /// "You have N on stage" or the FULL line to an owner it can see, and the
    /// row keeps that tail explicitly -- so the body under a length rule is the
    /// paragraph, measured the way the row states it.</summary>
    private static string Body(bool full = false)
    {
        var seat = Seat.Furina().WithCombatState();
        var text = SalonMemberTips.SalonRulesBody(seat.Creature);
        var tail = full ? "Your stage is FULL" : "You have ";
        var cut = text.IndexOf(tail, StringComparison.Ordinal);
        return cut < 0 ? text : text[..cut].TrimEnd();
    }

    private static int Sentences(string text) =>
        Regex.Matches(text, @"[.!?](?:\s|$)").Count;

    // === 1. three sentences, under 300 characters ========================

    [Fact]
    public void The_arms_salon_paragraph_is_three_sentences_under_300()
    {
        using var _ = new Arm();
        var body = Body();

        Assert.Equal(3, Sentences(body));
        Assert.True(body.Length < 300,
                    $"{body.Length} characters: {body}");
    }

    [Fact]
    public void It_says_the_cap_what_performs_and_the_bonus()
    {
        using var _ = new Arm();
        var body = Body();

        // THE CAP, live off the owner (A12 made it a stat).
        Assert.Contains($"Your Salon holds {SalonConstants.MemberSlots} "
                      + "members.", body);

        // WHAT PERFORMS -- the arm's whole engine, in one sentence: the
        // Companion trigger, the deploy's own performance, and the full-stage
        // Evoke. All three are rules a face prints nowhere.
        Assert.Contains("[gold]Companion[/gold] card you play performs the "
                      + "front member", body);
        Assert.Contains("[gold]Deploy[/gold] performs the member it adds",
                        body);
        Assert.Contains("onto a full stage it first [gold]Evokes[/gold] the "
                      + "front one", body);

        // THE BONUS, interpolated from the constant `TickValue` divides by.
        Assert.Contains($"+1 per {SalonConstants.FocusPerFanfare} "
                      + "[gold]Fanfare[/gold] you hold", body);
    }

    [Fact]
    public void The_live_tail_still_says_how_full_the_stage_is()
    {
        // The row keeps the tail: "You have N on stage" / "FULL". It is the
        // one thing on the tip that is about THIS board rather than the rules.
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        var text = SalonMemberTips.SalonRulesBody(seat.Creature);

        Assert.Contains("You have 0 on stage.", text);
    }

    // === 2. what left, and where it went =================================

    [Theory]
    [InlineData("picks its own enemy")]
    [InlineData("[gold]Minion[/gold]")]
    [InlineData("not an [gold]Attack[/gold]")]
    [InlineData("[gold]Shatter[/gold]")]
    [InlineData("when-hit power")]
    [InlineData("three-quarters")]
    [InlineData("leftmost")]
    public void The_dropped_clauses_are_off_the_paragraph(string clause)
    {
        using var _ = new Arm();
        Assert.DoesNotContain(clause, Body());
    }

    [Theory]
    [InlineData(SalonMember.Crabaletta)]
    [InlineData(SalonMember.Chevalmarin)]
    public void The_damage_members_carry_the_aim_and_the_class(
        SalonMember member)
    {
        // NOTHING IS DELETED FROM THE MOD'S TEXT AS A WHOLE. Each clause moved
        // to the surface read at the moment it matters, which for both of
        // these is a member about to deal damage.
        //
        // `EB-632` NARROWED THIS THEORY from three members to two: these are
        // the two whose performance is a hit, and both clauses below are facts
        // about a hit.
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        var tip = SalonMemberTips.BodyFor(member, seat.Creature);

        // The aim (`EB-425`, `EB-451`).
        Assert.Contains("picks its own enemy, never a [gold]Minion[/gold] "
                      + "while another enemy stands", tip);
        // The class (`EB-476`, `EB-548`, one rule: `EB-343`).
        Assert.Contains("not an [gold]Attack[/gold] and not a hit", tip);
        Assert.Contains("[gold]Vulnerable[/gold] moves it", tip);
        Assert.Contains("no [gold]Shatter[/gold]", tip);
        Assert.Contains("no when-hit power fires", tip);
    }

    [Fact]
    public void The_usher_carries_no_clause_about_an_effect_he_does_not_have()
    {
        // `EB-632`, THE ROW'S ACCEPTANCE CONDITION. The Usher gains
        // `UsherTick` Block and hits nobody, so the enemy-selection rule never
        // runs for him and he can never be on either side of the Shatter
        // exception. `EB-629` appended both to him anyway, which moved the
        // wall one surface over rather than shrinking it.
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        var tip = SalonMemberTips.BodyFor(SalonMember.Usher, seat.Creature);

        Assert.DoesNotContain("picks its own enemy", tip);
        Assert.DoesNotContain("[gold]Minion[/gold]", tip);
        Assert.DoesNotContain("not an [gold]Attack[/gold]", tip);
        Assert.DoesNotContain("[gold]Shatter[/gold]", tip);
        Assert.DoesNotContain("[gold]Vulnerable[/gold]", tip);
        Assert.DoesNotContain("when-hit", tip);

        // What he DOES have is still printed: his own two numbers and the dry
        // cut, which is a fact about him because his Block is cut too.
        Assert.Contains($"Performs for {SalonConstants.UsherTick} Block", tip);
        Assert.Contains($"Evokes for {SalonConstants.UsherBow} Block", tip);
        Assert.Contains("three-quarters", tip);

        // And the whole tip now clears the keyword-tip CEILING on its own
        // (135 rendered characters, `docs/current/text-conventions.md`), which
        // is the length rule the row asks these to be written under.
        Assert.True(Rendered(tip).Length <= 135,
                    $"{Rendered(tip).Length} characters: {tip}");
    }

    [Theory]
    [InlineData(SalonMember.Crabaletta)]
    [InlineData(SalonMember.Usher)]
    [InlineData(SalonMember.Chevalmarin)]
    public void The_dry_cut_is_on_every_member_tip(SalonMember member)
    {
        // R220 A and `EB-587`, and it stays on all three: every member can be
        // asked to perform on an empty buffer, so the reduced number's REASON
        // is a fact about each of them. It is also the sentence `EB-633`'s pip
        // row leans on -- the pips count FULL-STRENGTH performances, so a row
        // at zero does not mean the stage is idle.
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        var tip = SalonMemberTips.BodyFor(member, seat.Creature);

        Assert.Contains("With no [gold]Encore[/gold] it performs at "
                      + "three-quarters.", tip);
    }

    /// <summary>The string as a player sees it: BBCode stripped, which is how
    /// `docs/current/text-conventions.md` measures every ceiling.</summary>
    private static string Rendered(string text) =>
        Regex.Replace(text, @"\[/?[a-z]+\]", string.Empty);

    [Fact]
    public void The_front_marker_is_what_replaced_the_leftmost_sentence()
    {
        // "The leftmost member is the front" left with no new home in TEXT
        // because `EB-627` gave it a better one: chip 0 on the Salon panel
        // wears a highlight frame AND the word FRONT. This is the pin that
        // ties the two rows together -- if the mark ever goes, the sentence
        // has to come back.
        //
        // THE WORD IS THE HALF THE FIRST REBUILD DID NOT HAVE. A gold border
        // says "this one is special" and does not say WHAT is special about
        // it, which is the rule a Companion play acts on, so the frame alone
        // was not enough to have dropped the sentence on.
        var source = System.IO.File.ReadAllText(SourcePath(
            "Vfx/Prototype/SalonPanel.cs"));
        Assert.Contains("front: i == 0", source);
        Assert.Contains("frame.Visible = lit || (occupied && front);", source);
        Assert.Contains("wordLabel.Text = word;", source);
        Assert.Equal("FRONT", Vfx.SalonPanel.FrontWord);
        Assert.Equal("FRONT", Vfx.SalonPanel.SlotWord(
            0, 1, Powers.SalonConstants.MemberSlots,
            Vfx.SalonPanel.HoverKind.None, 0));
    }

    // === 3. the shipped paragraph is untouched ===========================

    [Fact]
    public void The_shipped_paragraph_is_exactly_what_it_was()
    {
        // A release build and an arm-off dev build read the shipped kit's own
        // rules, unchanged: this row is one arm's tip, not a roster edit.
        using var _ = new Arm(master: false);
        var body = Body();

        Assert.Contains("bows the OLDEST member out for its payoff", body);
        Assert.Contains("The leftmost member bows first.", body);
        Assert.Contains("a member with no Encore to spend acts at "
                      + "three-quarters", body);
        Assert.DoesNotContain("[gold]Companion[/gold]", body);
    }

    private static string SourcePath(string relative)
    {
        var wanted = System.IO.Path.Combine("klee-mod", "KleeCode",
            relative.Replace('/', System.IO.Path.DirectorySeparatorChar));
        var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = System.IO.Path.Combine(dir.FullName, wanted);
            if (System.IO.File.Exists(candidate)) return candidate;
            dir = dir.Parent;
        }
        throw new System.IO.FileNotFoundException(wanted);
    }
}
