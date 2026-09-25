using System.Collections.Generic;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-349` / `EB-611`: NO CARD RESOLVES UNRECORDED.
///
/// THE STANDING FACT this closes is printed on the blind page itself
/// (`understudy/blindplay_notes.AUTO_TURN_NOTE`): "there is no record of a card
/// resolving on the wire at all". Every screen the bridge sends is an
/// after-state, so a relic that plays a turn FOR the player left a board and no
/// turn (Vakuu: six openings, five from an empty hand -- Kokomi r4d), and a
/// multi-hit random `Set off` told a seat which bodies were hit and never the
/// order (Klee r23 lane 2).
///
/// THE BOUNDARY is `ReactionLogTests`': the hooks themselves are async game
/// paths needing a live `PlayerChoiceContext` and cannot run here. What CAN run
/// is the ledger's own behaviour -- the order, the caps, the window, the shape
/// -- plus an IL read proving the mod's one hook listener writes to it, which
/// is what makes "the single funnel" a checked claim rather than a comment.
/// </summary>
public class ResolutionLedgerTests
{
    private static void Fresh()
    {
        ResolutionLedger.ResetFight();
    }

    // --------------------------------------------------------- the funnel ---

    [Fact]
    public void The_play_boundary_opens_a_row()
    {
        var calls = Il.Calls(Il.Method("PlayTelemetryHooks", "BeforeCardPlayed"));

        Assert.Contains("ResolutionLedger.OpenPlay", calls);
    }

    [Fact]
    public void Every_number_the_game_delivers_reaches_the_ledger()
    {
        var calls = Il.Calls(
            Il.Method("PlayTelemetryHooks", "AfterDamageReceived"));

        Assert.Contains("ResolutionLedger.NoteHit", calls);
    }

    [Fact]
    public void The_play_boundary_closes_the_row()
    {
        var calls = Il.Calls(Il.Method("PlayTelemetryHooks", "AfterCardPlayed"));

        Assert.Contains("ResolutionLedger.ClosePlay", calls);
    }

    [Fact]
    public void The_turn_window_is_the_one_the_other_two_logs_keep()
    {
        Assert.Contains("ResolutionLedger.MarkTurnStart",
                        Il.Calls(Il.Method("ReactionEffects", "MarkTurnStart")));
        Assert.Contains(
            "ResolutionLedger.MarkPlayerTurnEnd",
            Il.Calls(Il.Method("KleeElementalHooks", "BeforeSideTurnEnd")));
    }

    /// <summary>The killing hit never reaches `AfterDamageReceived` (the
    /// game's own kill gate in `CreatureCmd.Damage`), so the death broadcast
    /// is the hook that has to file it. Seen to fail: three seats on
    /// 2026-09-24 read "Nothing this page can count landed off it" under a
    /// Strike that killed its target.</summary>
    [Fact]
    public void A_death_inside_a_play_reaches_the_ledger()
    {
        var calls = Il.Calls(Il.Method("PlayTelemetryHooks", "AfterDeath"));

        Assert.Contains("ResolutionLedger.NoteKill", calls);
    }

    [Fact]
    public void A_fight_does_not_inherit_the_last_ones_rows()
    {
        Assert.Contains("ResolutionLedger.ResetFight",
                        Il.Calls(Il.Method("PlayTelemetryHooks",
                                           "BeforeCombatStart")));
    }

    // ---------------------------------------------------------- the order ---

    /// <summary>`EB-611`'s acceptance, in the ledger's own terms: four hits on
    /// a hallway are four rows in the order they landed, and the two that
    /// struck the same body are two rows and not one.</summary>
    [Fact]
    public void Four_hits_on_a_hallway_are_four_rows_in_order()
    {
        Fresh();
        var seat = Seat.Kokomi();
        ResolutionLedger.OpenPlay("rapid_fire", "Rapid Fire", false);
        ResolutionLedger.NoteHit(seat.Creature, 6, 0);
        ResolutionLedger.NoteHit(null, 6, 0);
        ResolutionLedger.NoteHit(seat.Creature, 6, 0);
        ResolutionLedger.NoteHit(null, 6, 0);
        ResolutionLedger.ClosePlay();

        var rows = ResolutionLedger.Snapshot();

        Assert.Single(rows);
        var hits = (List<Dictionary<string, object?>>)rows[0]["hits"]!;
        Assert.Equal(4, hits.Count);
        Assert.Equal(new object?[] { 6, 6, 6, 6 },
                     hits.ConvertAll(h => h["amount"]).ToArray());
    }

    /// <summary>A hit that landed entirely on Block is a PLACE IN THE ORDER.
    /// `RelicAnswerLog`'s "a zero is not a row" rule is deliberately not copied
    /// whole: that log reports a subtraction, this one reports an order, and
    /// three lines for a four-hit card is the same defect in a new hat.</summary>
    [Fact]
    public void A_hit_that_landed_on_block_is_still_a_row()
    {
        Fresh();
        ResolutionLedger.OpenPlay("strike", "Strike", false);
        ResolutionLedger.NoteHit(null, 0, 7);

        var hits = (List<Dictionary<string, object?>>)
            ResolutionLedger.Snapshot()[0]["hits"]!;

        Assert.Single(hits);
        Assert.Equal(0, hits[0]["amount"]);
        Assert.Equal(7, hits[0]["blocked"]);
    }

    [Fact]
    public void A_hit_that_moved_nothing_at_all_is_not_a_row()
    {
        Fresh();
        ResolutionLedger.OpenPlay("strike", "Strike", false);
        ResolutionLedger.NoteHit(null, 0, 0);

        Assert.Empty((List<Dictionary<string, object?>>)
                     ResolutionLedger.Snapshot()[0]["hits"]!);
    }

    /// <summary>An enemy's attack, a bomb on nobody's turn and a relic's
    /// answer all reach the damage hook, and none of them is a card resolving.
    /// Each has its own receipt.</summary>
    [Fact]
    public void A_hit_outside_a_play_is_filed_nowhere()
    {
        Fresh();
        ResolutionLedger.NoteHit(null, 9, 0);

        Assert.Empty(ResolutionLedger.Snapshot());
    }

    [Fact]
    public void A_hit_after_the_play_closed_is_filed_nowhere()
    {
        Fresh();
        ResolutionLedger.OpenPlay("strike", "Strike", false);
        ResolutionLedger.ClosePlay();
        ResolutionLedger.NoteHit(null, 9, 0);

        Assert.Empty((List<Dictionary<string, object?>>)
                     ResolutionLedger.Snapshot()[0]["hits"]!);
    }

    // ---------------------------------------------------------- the kills ---

    /// <summary>A kill is an entry IN HIT ORDER, where the killing hit would
    /// have been, carrying the body and no number -- so an all-enemies card
    /// that killed one body of three still names it between the other two.
    /// </summary>
    [Fact]
    public void A_kill_is_filed_in_hit_order_with_no_number()
    {
        Fresh();
        ResolutionLedger.OpenPlay("kurages_oath", "Kurage's Oath", false);
        ResolutionLedger.NoteHit(null, 7, 0);
        ResolutionLedger.NoteKill("Toadpole", "2");
        ResolutionLedger.NoteHit(null, 7, 0);
        ResolutionLedger.ClosePlay();

        var hits = (List<Dictionary<string, object?>>)
            ResolutionLedger.Snapshot()[0]["hits"]!;

        Assert.Equal(3, hits.Count);
        Assert.Equal(new object?[] { false, true, false },
                     hits.ConvertAll(h => h["killed"]).ToArray());
        Assert.Equal("Toadpole", hits[1]["target"]);
        Assert.Equal("2", hits[1]["combat_id"]);
        Assert.Equal(0, hits[1]["amount"]);
        Assert.Equal(0, hits[1]["blocked"]);
    }

    [Fact]
    public void One_body_dies_once()
    {
        Fresh();
        ResolutionLedger.OpenPlay("strike", "Strike", false);
        ResolutionLedger.NoteKill("Toadpole", "2");
        ResolutionLedger.NoteKill("Toadpole", "2");

        Assert.Single((List<Dictionary<string, object?>>)
                      ResolutionLedger.Snapshot()[0]["hits"]!);
    }

    /// <summary>An enemy dying on its own turn, or to a bomb on nobody's
    /// turn, is not a card killing it: `NoteHit`'s rule, one hook over.
    /// </summary>
    [Fact]
    public void A_death_outside_a_play_is_filed_nowhere()
    {
        Fresh();
        ResolutionLedger.NoteKill("Toadpole", "2");

        Assert.Empty(ResolutionLedger.Snapshot());
    }

    // --------------------------------------------------------- the window ---

    /// <summary>`EB-710`'s carry, on this ledger: an auto-played turn happens
    /// on the far side of the player's end-turn, so a log cleared on the wrong
    /// window would drop exactly the turn nobody watched.</summary>
    [Fact]
    public void A_row_from_after_your_end_turn_carries_one_turn_marked()
    {
        Fresh();
        ResolutionLedger.OpenPlay("strike", "Strike", false);
        ResolutionLedger.ClosePlay();
        ResolutionLedger.MarkPlayerTurnEnd();
        ResolutionLedger.OpenPlay("vakuu_opening", "Reckless Charge", true);
        ResolutionLedger.ClosePlay();

        ResolutionLedger.MarkTurnStart();
        var rows = ResolutionLedger.Snapshot();

        Assert.Single(rows);
        Assert.Equal("Reckless Charge", rows[0]["card"]);
        Assert.Equal(true, rows[0]["carried"]);
        Assert.Equal(true, rows[0]["auto_played"]);

        // And it prints once: next turn round it sits before the new mark.
        ResolutionLedger.MarkTurnStart();
        Assert.Empty(ResolutionLedger.Snapshot());
    }

    [Fact]
    public void No_mark_no_carry()
    {
        Fresh();
        ResolutionLedger.OpenPlay("strike", "Strike", false);
        ResolutionLedger.ClosePlay();

        ResolutionLedger.MarkTurnStart();

        Assert.Empty(ResolutionLedger.Snapshot());
    }

    // ----------------------------------------------------------- the caps ---

    [Fact]
    public void A_row_past_the_hit_cap_says_so_rather_than_truncating_quietly()
    {
        Fresh();
        ResolutionLedger.OpenPlay("strike", "Strike", false);
        for (var i = 0; i < ResolutionLedger.MaxHits + 5; i++)
        {
            ResolutionLedger.NoteHit(null, 1, 0);
        }

        var row = ResolutionLedger.Snapshot()[0];

        Assert.Equal(ResolutionLedger.MaxHits,
                     ((List<Dictionary<string, object?>>)row["hits"]!).Count);
        Assert.Equal(true, row["overflowed"]);
    }

    [Fact]
    public void A_turn_past_the_row_cap_stops_minting_rows()
    {
        Fresh();
        for (var i = 0; i < ResolutionLedger.MaxRows + 5; i++)
        {
            ResolutionLedger.OpenPlay("strike", "Strike", false);
            ResolutionLedger.ClosePlay();
        }

        Assert.Equal(ResolutionLedger.MaxRows,
                     ResolutionLedger.Snapshot().Count);
    }

    // ---------------------------------------------------------- the shape ---

    /// <summary>The wire keys ARE the contract:
    /// `understudy/blindplay_board.resolutions` reads exactly these.</summary>
    [Fact]
    public void The_snapshot_carries_the_keys_the_page_reads()
    {
        Fresh();
        ResolutionLedger.OpenPlay("strike", "Strike", false);
        ResolutionLedger.NoteHit(null, 6, 0);

        var row = ResolutionLedger.Snapshot()[0];
        Assert.Equal(new[] { "card_id", "card", "auto_played", "carried",
                             "overflowed", "hits", "summoned" },
                     new List<string>(row.Keys).ToArray());

        var hit = ((List<Dictionary<string, object?>>)row["hits"]!)[0];
        Assert.Equal(new[] { "target", "amount", "blocked", "combat_id",
                             "killed" },
                     new List<string>(hit.Keys).ToArray());
        Assert.Equal(false, hit["killed"]);
    }

    /// <summary>2026-09-25 evening: a random summon inside a card names who it
    /// rolled on that card's row, and nothing outside a play is filed.
    /// </summary>
    [Fact]
    public void A_summon_inside_a_play_names_who_it_rolled()
    {
        Fresh();
        ResolutionLedger.NoteSummon("usher", "Gentilhomme Usher");  // no play
        ResolutionLedger.OpenPlay("proto_fs_understudy", "Understudy", false);
        ResolutionLedger.NoteSummon("crabaletta", "Mademoiselle Crabaletta");
        ResolutionLedger.ClosePlay();

        var row = ResolutionLedger.Snapshot()[0];
        var summoned = (List<Dictionary<string, object?>>)row["summoned"]!;
        var only = Assert.Single(summoned);
        Assert.Equal("crabaletta", only["member"]);
        Assert.Equal("Mademoiselle Crabaletta", only["name"]);
    }

    /// <summary>PRESENT AND EMPTY ON A TURN NOTHING RESOLVED, which is a fact
    /// and not a hole -- and on an auto-played turn it is THE fact.</summary>
    [Fact]
    public void An_empty_turn_is_an_empty_list_and_not_a_null()
    {
        Fresh();

        Assert.NotNull(ResolutionLedger.Snapshot());
        Assert.Empty(ResolutionLedger.Snapshot());
    }
}
