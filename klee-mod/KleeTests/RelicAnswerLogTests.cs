using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-695`: NO RELIC HIT GOES UNNAMED.
///
/// THE FIND (Kokomi r30, lane 2, debrief 1). The Tamakushi Casket answers a
/// debuff with a 2-damage Hydro strike. Inside a PLAN carry-out it is named --
/// "Inside the same beat: Tamakushi Casket 2 on Damp Cultist" -- because
/// <c>KokomiPlan.NoteRider</c> is standing there to catch it. Played FROM
/// HAND, the same strike landed with nothing naming it, and the seat
/// subtracted it from HP by hand on every such play.
///
/// WHAT IS PINNED HERE is the half a compile cannot see and a live run makes
/// expensive: that the two receipts do not BOTH fire (a strike named twice is
/// `EB-518`'s arithmetic defect reopened from the other side), that the relic
/// really does ask `NoteRider` whether it filed, and the log's own rows and
/// window. The page half is
/// `tier0/tests/test_eb695_a_played_card_names_the_relic_that_answered.py`.
///
/// THE BOUNDARY is `ReactionLogTests`': `TamakushiCasket.Strike` is an async
/// game path needing a live `PlayerChoiceContext` and cannot run here, so the
/// call it makes is read off IL and the log is exercised directly.
/// </summary>
public class RelicAnswerLogTests
{
    private const string Casket = "Tamakushi Casket";

    [Fact]
    public void A_strike_outside_a_plan_is_a_row_with_its_body_and_its_number()
    {
        RelicAnswerLog.MarkTurnStart();

        RelicAnswerLog.Note(Casket, 2, Seat.Kokomi().Creature);

        var row = Assert.Single(RelicAnswerLog.Snapshot());
        Assert.Equal(Casket, row["source"]);
        Assert.Equal(2, row["amount"]);
        Assert.Equal(false, row["carried"]);
    }

    [Fact]
    public void The_wire_row_carries_the_five_keys_the_page_reads()
    {
        // The key names ARE the contract with
        // `understudy/blindplay_board.relic_answers`.
        RelicAnswerLog.MarkTurnStart();
        RelicAnswerLog.Note(Casket, 2, Seat.Kokomi().Creature);

        var row = RelicAnswerLog.Snapshot().Single();

        Assert.Equal(
            new[] { "source", "amount", "target", "combat_id", "carried" },
            row.Keys.ToArray());
    }

    [Fact]
    public void Two_strikes_on_one_turn_are_two_rows_in_order()
    {
        // `EB-518`: three entries reading "Tamakushi Casket 2" cannot be
        // divided among bodies by a reader, so each strike is its own row.
        RelicAnswerLog.MarkTurnStart();

        RelicAnswerLog.Note(Casket, 2, Seat.Kokomi().Creature);
        RelicAnswerLog.Note(Casket, 3, Seat.Kokomi().Creature);

        var rows = RelicAnswerLog.Snapshot();
        Assert.Equal(2, rows.Count);
        Assert.Equal(2, rows[0]["amount"]);
        Assert.Equal(3, rows[1]["amount"]);
    }

    [Fact]
    public void A_strike_that_delivered_nothing_writes_nothing()
    {
        RelicAnswerLog.MarkTurnStart();

        RelicAnswerLog.Note(Casket, 0, Seat.Kokomi().Creature);

        Assert.Empty(RelicAnswerLog.Snapshot());
    }

    [Fact]
    public void A_strike_after_the_player_s_turn_ended_survives_one_turn()
    {
        // `EB-710`'s window, on this log, and for its reason: a strike that
        // landed with no page in front of it would otherwise be dropped before
        // anything could print it.
        RelicAnswerLog.MarkTurnStart();
        RelicAnswerLog.MarkPlayerTurnEnd();
        RelicAnswerLog.Note(Casket, 2, Seat.Kokomi().Creature);

        RelicAnswerLog.MarkTurnStart();

        var row = Assert.Single(RelicAnswerLog.Snapshot());
        Assert.Equal(true, row["carried"]);

        RelicAnswerLog.MarkPlayerTurnEnd();
        RelicAnswerLog.MarkTurnStart();
        Assert.Empty(RelicAnswerLog.Snapshot());
    }

    [Fact]
    public void The_watched_half_of_the_turn_is_dropped()
    {
        RelicAnswerLog.MarkTurnStart();
        RelicAnswerLog.Note(Casket, 2, Seat.Kokomi().Creature);
        RelicAnswerLog.MarkPlayerTurnEnd();

        RelicAnswerLog.MarkTurnStart();

        Assert.Empty(RelicAnswerLog.Snapshot());
    }

    [Fact]
    public void The_window_rides_the_same_calls_as_the_reaction_log_s()
    {
        // One boundary, named once, so two receipts on one page cannot
        // disagree about which turn they are about.
        Assert.Contains("RelicAnswerLog.MarkTurnStart",
                        Il.Calls(Il.Method("ReactionEffects", "MarkTurnStart")));
        Assert.Contains(
            "RelicAnswerLog.MarkPlayerTurnEnd",
            Il.Calls(Il.Method("KleeElementalHooks", "BeforeSideTurnEnd")));
    }

#if PROTOTYPE_CARDS
    [Fact]
    public void The_casket_asks_the_plan_first_and_logs_only_if_it_was_not_filed()
    {
        // The half that keeps one strike named ONCE. `NoteRider` files against
        // the Plan being resolved right now and answers whether it did; the
        // relic writes to this log only on the false branch.
        var calls = Il.Calls(Il.Method("TamakushiCasket", "Strike"));

        Assert.Contains("KokomiPlan.NoteRider", calls);
        Assert.Contains("RelicAnswerLog.Note", calls);
    }
#endif
}
