using System.Collections.Generic;
using KleeMod.Elements;
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

    /// <summary>The Klee round (2026-10-11): Fire! Fire! places its Bomb 7
    /// and then sets it off, and the page printed the hit above the "Put".
    /// Hits and applied powers share one rising `seq`, so the page can merge
    /// the two lists in play order.</summary>
    [Fact]
    public void Hits_and_applied_powers_carry_one_rising_seq()
    {
        Fresh();
        ResolutionLedger.OpenPlay("fire_fire", "Fire! Fire!", false);
        ResolutionLedger.NotePower("Toadpole", "Bomb", 7, "2");
        ResolutionLedger.NoteHit(null, 15, 0);
        ResolutionLedger.NoteKill("Toadpole", "2");
        ResolutionLedger.ClosePlay();

        var row = ResolutionLedger.Snapshot()[0];
        var applied = (List<Dictionary<string, object?>>)row["applied"]!;
        var hits = (List<Dictionary<string, object?>>)row["hits"]!;

        var put = (long)applied[0]["seq"]!;
        var hit = (long)hits[0]["seq"]!;
        var kill = (long)hits[1]["seq"]!;
        Assert.True(put > 0);
        Assert.True(put < hit);
        Assert.True(hit < kill);
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

    /// <summary>The Spiral Abyss seat round (2026-10-12): whose card a row
    /// is, so a co-op page keeps the partner's plays out of "What you
    /// played", and how many times it played, so a doubled card says so. A
    /// row opened without them reads as before: no owner, not known to be
    /// anyone's, played once.</summary>
    [Fact]
    public void A_row_carries_its_owner_and_its_play_count()
    {
        Fresh();
        ResolutionLedger.OpenPlay("strike", "Strike", false, "Varka", false, 2);
        ResolutionLedger.ClosePlay();
        ResolutionLedger.OpenPlay("defend", "Defend", false);
        ResolutionLedger.ClosePlay();

        var rows = ResolutionLedger.Snapshot();
        Assert.Equal("Varka", rows[0]["owner"]);
        Assert.Equal(false, rows[0]["is_local"]);
        Assert.Equal(2, rows[0]["play_count"]);
        Assert.Equal("", rows[1]["owner"]);
        Assert.Null(rows[1]["is_local"]);
        Assert.Equal(1, rows[1]["play_count"]);
    }

    /// <summary>Seat page backlog (2026-10-13): a row carries the card's
    /// type, so the page can tell whether an Attack was played this turn
    /// (Ripple Basin). A row opened without it reads "".</summary>
    [Fact]
    public void A_row_carries_its_card_type()
    {
        Fresh();
        ResolutionLedger.OpenPlay("strike", "Strike", false, cardType: "Attack");
        ResolutionLedger.ClosePlay();
        ResolutionLedger.OpenPlay("defend", "Defend", false);
        ResolutionLedger.ClosePlay();

        var rows = ResolutionLedger.Snapshot();
        Assert.Equal("Attack", rows[0]["card_type"]);
        Assert.Equal("", rows[1]["card_type"]);
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
        Assert.Equal(new[] { "card_id", "card", "auto_played", "owner",
                             "is_local", "play_count", "card_type", "carried",
                             "overflowed", "hits", "applied", "summoned",
                             "oath", "fang_ascension", "fang_relic",
                             "swirl_no_aura", "swirl_on_aura", "between",
                             "events" },
                     new List<string>(row.Keys).ToArray());

        var hit = ((List<Dictionary<string, object?>>)row["hits"]!)[0];
        Assert.Equal(new[] { "target", "amount", "blocked", "combat_id",
                             "killed", "on_player", "source", "self",
                             "seq", "by", "label" },
                     new List<string>(hit.Keys).ToArray());
        Assert.Equal(false, hit["killed"]);
        // 2026-10-01: a hit on a player inside a play is marked as one.
        Assert.Equal(false, hit["on_player"]);
        // 2026-10-09: and only a hit on a player can be her own HP cost.
        Assert.Equal(false, hit["self"]);
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

    /// <summary>2026-09-26 (the Silent control seat): "Poison applied is
    /// never shown in 'what it did'." A power put on an enemy inside a play
    /// is filed on that card's row; outside a play, and a zero, are not.
    /// </summary>
    [Fact]
    public void A_power_put_on_an_enemy_inside_a_play_is_filed()
    {
        Fresh();
        ResolutionLedger.NotePower("Nibbit", "Poison", 6, "3");  // no play
        ResolutionLedger.OpenPlay("deadly_poison", "Deadly Poison", false);
        ResolutionLedger.NotePower("Nibbit", "Poison", 6, "3");
        ResolutionLedger.NotePower("Nibbit", "Weak", 0, "3");
        ResolutionLedger.ClosePlay();

        var row = ResolutionLedger.Snapshot()[0];
        var applied = (List<Dictionary<string, object?>>)row["applied"]!;
        var only = Assert.Single(applied);
        Assert.Equal("Nibbit", only["target"]);
        Assert.Equal("Poison", only["power"]);
        Assert.Equal(6, only["amount"]);
        Assert.Equal("3", only["combat_id"]);
    }

    [Fact]
    public void A_power_change_reaches_the_ledger()
    {
        var calls = Il.Calls(
            Il.Method("PlayTelemetryHooks", "AfterPowerAmountChanged"));

        Assert.Contains("ResolutionLedger.NotePower", calls);
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

    // ------------------------------------------- 2026-10-04, the seat page ---

    /// <summary>"Put Bomb 1" where the card placed Bomb 11: the hook files the
    /// pile's count, and the placement then sizes its own entry.</summary>
    [Fact]
    public void A_placement_sizes_the_entry_its_apply_filed()
    {
        Fresh();
        ResolutionLedger.OpenPlay("bang", "Bang Bang!", false);
        ResolutionLedger.NotePower("Toadpole", "Weak", 1, "2");
        var mark = ResolutionLedger.MarkApplied();
        ResolutionLedger.NotePower("Toadpole", "Bomb", 1, "2");
        ResolutionLedger.SizeAppliedSince(mark, "2", "Mine", 3);

        var applied = (List<Dictionary<string, object?>>)
            ResolutionLedger.Snapshot()[0]["applied"]!;
        Assert.Equal("Weak", applied[0]["power"]);
        Assert.Equal(1, applied[0]["amount"]);
        Assert.Equal("Mine", applied[1]["power"]);
        Assert.Equal(3, applied[1]["amount"]);
    }

    /// <summary>Nothing filed since the mark (the apply filed no entry)
    /// leaves the earlier entries alone.</summary>
    [Fact]
    public void A_placement_with_no_entry_since_its_mark_changes_nothing()
    {
        Fresh();
        ResolutionLedger.OpenPlay("bang", "Bang Bang!", false);
        ResolutionLedger.NotePower("Toadpole", "Weak", 1, "2");
        var mark = ResolutionLedger.MarkApplied();
        ResolutionLedger.SizeAppliedSince(mark, "2", "Bomb", 11);

        var applied = (List<Dictionary<string, object?>>)
            ResolutionLedger.Snapshot()[0]["applied"]!;
        Assert.Single(applied);
        Assert.Equal("Weak", applied[0]["power"]);
        Assert.Equal(1, applied[0]["amount"]);
    }

    // ------------------------------------- 2026-10-05: the page events ---

    [Fact]
    public void An_event_inside_a_play_is_filed_on_that_card()
    {
        Fresh();
        ResolutionLedger.OpenPlay("acrobatics", "Acrobatics", false);
        ResolutionLedger.NoteEvent(ResolutionLedger.Drawn, "Strike", "", "");

        var rows = ResolutionLedger.Snapshot();
        Assert.Single(rows);
        var events = (List<Dictionary<string, object?>>)rows[0]["events"]!;
        Assert.Single(events);
        Assert.Equal("drawn", events[0]["kind"]);
        Assert.Equal("Strike", events[0]["card"]);
        Assert.Equal(new[] { "kind", "card", "target", "power", "combat_id",
                             "on_player", "seq", "amount", "lost", "past" },
                     new List<string>(events[0].Keys).ToArray());
        Assert.Equal(0, events[0]["amount"]);
    }

    /// <summary>Design-session call (2026-10-13): Wolfpack's copy lands on
    /// the Ascension's play line, open or just closed, and nowhere else's.
    /// </summary>
    [Fact]
    public void A_play_line_event_files_on_its_card_even_after_the_row_closed()
    {
        Fresh();
        ResolutionLedger.OpenPlay("vk_fwa", "Four Winds' Ascension", false);
        ResolutionLedger.ClosePlay();
        ResolutionLedger.NoteEventOnPlay(ResolutionLedger.Wolfpack,
            "Four Winds' Ascension", "Four Winds' Ascension", "Lupical",
            amount: 1);
        var rows = ResolutionLedger.Snapshot();
        Assert.Single(rows);
        var events = (List<Dictionary<string, object?>>)rows[0]["events"]!;
        Assert.Single(events);
        Assert.Equal("wolfpack", events[0]["kind"]);
        Assert.Equal(1, events[0]["amount"]);

        // Open: the open row, as NoteEvent files it.
        Fresh();
        ResolutionLedger.OpenPlay("vk_fwa", "Four Winds' Ascension", false);
        ResolutionLedger.NoteEventOnPlay(ResolutionLedger.Wolfpack,
            "Four Winds' Ascension", "Four Winds' Ascension", "Lupical",
            amount: 2);
        rows = ResolutionLedger.Snapshot();
        Assert.Single(rows);
        Assert.Single((List<Dictionary<string, object?>>)rows[0]["events"]!);

        // Another card last: never that card's line, a between row instead.
        Fresh();
        ResolutionLedger.OpenPlay("strike", "Strike", false);
        ResolutionLedger.ClosePlay();
        ResolutionLedger.NoteEventOnPlay(ResolutionLedger.Wolfpack,
            "Four Winds' Ascension", "Four Winds' Ascension", "Lupical",
            amount: 1);
        rows = ResolutionLedger.Snapshot();
        Assert.Empty((List<Dictionary<string, object?>>)rows[0]["events"]!);
        Assert.Equal(2, rows.Count);
        Assert.Equal(true, rows[1]["between"]);
    }

    /// <summary>Seat page 3 (2026-10-05): the curtain call's figure rides
    /// the event, and a Shatter and the curtain call reach the ledger.
    /// </summary>
    [Fact]
    public void The_curtain_call_files_its_figure()
    {
        Fresh();
        ResolutionLedger.NoteEvent(ResolutionLedger.HpReturned, "", "Furina",
                                   "", "", onPlayer: true, amount: 12);
        var events = (List<Dictionary<string, object?>>)
            ResolutionLedger.Snapshot()[0]["events"]!;
        Assert.Equal("curtain", events[0]["kind"]);
        Assert.Equal(12, events[0]["amount"]);
        Assert.Equal("shattered", ResolutionLedger.Shattered);
    }

    [Fact]
    public void A_shatter_and_the_curtain_call_reach_the_ledger()
    {
        Assert.Contains("ResolutionLedger.NoteEvent",
            Il.Calls(Il.Method("FrozenPower", "AfterDamageReceived")));
        Assert.Contains("ResolutionLedger.NoteEvent",
            Il.Calls(Il.Method("FurinaStage", "CurtainCall")));
    }

    /// <summary>Outside any play the event goes on a row with no card,
    /// which a page that predates it skips; the turn's order is kept by a
    /// new such row after each play.</summary>
    [Fact]
    public void An_event_outside_a_play_rides_a_row_with_no_card()
    {
        Fresh();
        ResolutionLedger.NoteEvent(ResolutionLedger.Negated, "", "Mecha Knight",
                                   "Weak", "3");
        ResolutionLedger.NoteEvent(ResolutionLedger.Triggered, "",
                                   "Mecha Knight", "Artifact", "3");
        ResolutionLedger.OpenPlay("strike", "Strike", false);
        ResolutionLedger.ClosePlay();
        ResolutionLedger.NoteEvent(ResolutionLedger.Triggered, "", "Crusher",
                                   "Crab Rage", "1");

        var rows = ResolutionLedger.Snapshot();
        Assert.Equal(3, rows.Count);
        Assert.Equal(true, rows[0]["between"]);
        Assert.Equal("", rows[0]["card"]);
        Assert.Equal(2, ((List<Dictionary<string, object?>>)
            rows[0]["events"]!).Count);
        Assert.Equal(false, rows[1]["between"]);
        Assert.Equal(true, rows[2]["between"]);
    }

    [Fact]
    public void The_event_sequence_only_rises_across_fights()
    {
        Fresh();
        ResolutionLedger.NoteEvent(ResolutionLedger.Drawn, "Strike", "", "");
        var first = (long)((List<Dictionary<string, object?>>)
            ResolutionLedger.Snapshot()[0]["events"]!)[0]["seq"]!;
        Fresh();
        ResolutionLedger.NoteEvent(ResolutionLedger.Drawn, "Defend", "", "");
        var second = (long)((List<Dictionary<string, object?>>)
            ResolutionLedger.Snapshot()[0]["events"]!)[0]["seq"]!;
        Assert.True(second > first);
        Assert.True(first > 1_000_000_000_000L);
    }

    [Fact]
    public void The_draw_hook_reaches_the_ledger()
    {
        var calls = Il.Calls(Il.Method("PlayTelemetryHooks", "AfterCardDrawn"));

        Assert.Contains("ResolutionLedger.NoteEvent", calls);
    }

    [Fact]
    public void The_hit_hook_hands_over_the_dealer()
    {
        var calls = Il.Calls(
            Il.Method("PlayTelemetryHooks", "AfterDamageReceived"));

        Assert.Contains("ResolutionLedger.NoteHit", calls);
        Fresh();
        ResolutionLedger.OpenPlay("strike", "Strike", false);
        ResolutionLedger.NoteHit(null, 3, 0);
        var row = ((List<Dictionary<string, object?>>)
            ResolutionLedger.Snapshot()[0]["hits"]!)[0];
        Assert.True(row.ContainsKey("source"));
        Assert.Equal("", row["source"]);
    }
    // ------------------------------------------- the hit label (2026-10-18) ---

    /// <summary>Seat page: "The resolution rows do not say which hit was
    /// which" (Four Winds' Ascension+ read "2, 3, 9, 36" unlabelled). A hit
    /// filed inside a <see cref="ResolutionLedger.HitsAs"/> scope carries its
    /// label on the wire; the innermost scope wins, and a hit outside every
    /// scope carries none.</summary>
    [Fact]
    public void A_hit_inside_a_label_scope_carries_the_label()
    {
        Fresh();
        ResolutionLedger.OpenPlay("four_winds", "Four Winds' Ascension", false);
        ResolutionLedger.NoteHit(null, 2, 0);
        using (ResolutionLedger.HitsAs("Swirl"))
        {
            ResolutionLedger.NoteHit(null, 3, 0);
            using (ResolutionLedger.HitsAs("Pyro"))
            {
                ResolutionLedger.NoteHit(null, 9, 0);
            }
            ResolutionLedger.NoteKill("Slime", "7");
        }
        ResolutionLedger.NoteHit(null, 36, 0);

        var hits = (List<Dictionary<string, object?>>)
            ResolutionLedger.Snapshot()[0]["hits"]!;
        Assert.Equal(new object?[] { "", "Swirl", "Pyro", "Swirl", "" },
                     hits.ConvertAll(h => h["label"]).ToArray());
    }

    [Fact]
    public void An_element_hit_is_labelled_by_its_element_and_amplifier()
    {
        Assert.Equal("Pyro",
            ResolutionLedger.ElementLabel(Element.Pyro, Reaction.None, 1m));
        Assert.Equal("Pyro, Vaporize",
            ResolutionLedger.ElementLabel(Element.Pyro, Reaction.Vaporize, 1.5m));
        Assert.Equal("Cryo, Melt",
            ResolutionLedger.ElementLabel(Element.Cryo, Reaction.Melt, 2m));
        // A non-amplifying reaction is its own label, not the hit's.
        Assert.Equal("Electro",
            ResolutionLedger.ElementLabel(Element.Electro, Reaction.Overload, 1m));
        Assert.Equal("", ResolutionLedger.ElementLabel(Element.None, Reaction.None, 1m));
    }

    [Fact]
    public void The_element_door_and_the_reaction_site_open_the_label()
    {
        Assert.Contains("ResolutionLedger.HitsAs",
            Il.Calls(Il.Method("ElementalHit", "Deal")));
        Assert.Contains("ResolutionLedger.HitsAs",
            Il.Calls(Il.Method("ElementalHit", "DealAsIfAura")));
        Assert.Contains("ResolutionLedger.HitsAs",
            Il.Calls(Il.Method("ReactionEffects", "Resolve")));
    }
}
