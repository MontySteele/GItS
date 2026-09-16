using System.Linq;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-710`: AN END-OF-TURN REACTION SURVIVES TO A PAGE.
///
/// THE FIND. "What reacted this turn" said *Nothing reacted this turn* through
/// a run where Electro-Charged fired six times off Shinobu's Sanctifying Ring
/// -- a power that fires AT THE END OF YOUR TURN -- and Klee r26 read the
/// header EMPTY on two Melts and an Overloaded off a played Set off.
///
/// THE LOG WAS CLEARED ON THE WRONG WINDOW. <see cref="ReactionLog.MarkTurnStart"/>
/// is called from <c>ElementalApplication.AfterSideTurnEnd(Enemy)</c>, which
/// is the OPENING of the player's next turn, and it used to be a straight
/// clear. Every reaction between the player's last action and that moment --
/// their own end-of-turn tenants (<c>CompanionOverhaulTurnEnd</c> fires the
/// Ring's volley in <c>AfterSideTurnEnd(Player)</c>), then the whole enemy
/// side -- was written into a list emptied before any page could render it.
/// There was no page on which those rows could ever have printed.
///
/// WHAT IS PINNED HERE is the window itself, which is the half a live run
/// makes expensive to check and a compile cannot see at all: where the mark
/// falls, what carries, that a carried row carries ONCE, and that the two
/// behaviours that must not move -- no mark means no carry, and a row from the
/// watched half of the turn is dropped -- are what they were. The page half is
/// `tier0/tests/test_eb710_an_end_of_turn_reaction_survives_to_a_page.py`.
///
/// THE BOUNDARY is `ReactionLogTests`': `ReactionEffects.Resolve` is an async
/// game path needing a live `PlayerChoiceContext` and cannot run here, so the
/// hook siting is read off IL and the window is exercised directly.
/// </summary>
public class ReactionLogWindowTests
{
    private static void Note(Reaction reaction) =>
        ReactionLog.Note(reaction, Seat.Kokomi().Creature, null, null);

    [Fact]
    public void A_reaction_after_the_player_s_turn_ended_survives_the_next_turn_opening()
    {
        // The r31 beat: the player acts, ends the turn, and the Ring's volley
        // reacts with nobody being shown a page. Then the next turn opens.
        ReactionLog.MarkTurnStart();
        Note(Reaction.Melt);                     // watched: on their screen
        ReactionLog.MarkPlayerTurnEnd();
        Note(Reaction.ElectroCharged);           // unwatched: the Ring

        ReactionLog.MarkTurnStart();

        var row = Assert.Single(ReactionLog.Snapshot());
        Assert.Equal("Electro-Charged", row["reaction"]);
        Assert.Equal(true, row["carried"]);
    }

    [Fact]
    public void The_watched_half_of_the_turn_is_still_dropped()
    {
        // The other direction, and it is why the mark exists rather than a
        // blanket carry: a row the player was looking at when it resolved has
        // been printed and must not print again on the next screen.
        ReactionLog.MarkTurnStart();
        Note(Reaction.Melt);
        ReactionLog.MarkPlayerTurnEnd();

        ReactionLog.MarkTurnStart();

        Assert.Empty(ReactionLog.Snapshot());
    }

    [Fact]
    public void A_carried_row_carries_exactly_one_turn()
    {
        // It is printed on the turn it carries into, so on the turn after that
        // it sits BEFORE the new mark and goes. Without this, a long enemy
        // side would pile up on every page that followed it.
        ReactionLog.MarkTurnStart();
        ReactionLog.MarkPlayerTurnEnd();
        Note(Reaction.ElectroCharged);
        ReactionLog.MarkTurnStart();
        Assert.Single(ReactionLog.Snapshot());

        ReactionLog.MarkPlayerTurnEnd();
        ReactionLog.MarkTurnStart();

        Assert.Empty(ReactionLog.Snapshot());
    }

    [Fact]
    public void A_carried_row_prints_beside_this_turn_s_own()
    {
        // Both kinds on one screen, in the order they resolved, each saying
        // which window it came from -- which is what lets the page keep the
        // heading's word "this turn" honest.
        ReactionLog.MarkTurnStart();
        ReactionLog.MarkPlayerTurnEnd();
        Note(Reaction.ElectroCharged);
        ReactionLog.MarkTurnStart();
        Note(Reaction.Overload);

        var rows = ReactionLog.Snapshot();

        Assert.Equal(2, rows.Count);
        Assert.Equal("Electro-Charged", rows[0]["reaction"]);
        Assert.Equal(true, rows[0]["carried"]);
        Assert.Equal("Overloaded", rows[1]["reaction"]);
        Assert.Equal(false, rows[1]["carried"]);
    }

    [Fact]
    public void No_mark_means_no_carry()
    {
        // The conservative direction. A window whose end was never announced
        // is a window nothing can call unwatched, and a log that carried on a
        // missing mark would carry forever.
        ReactionLog.MarkTurnStart();
        Note(Reaction.Frozen);

        ReactionLog.MarkTurnStart();

        Assert.Empty(ReactionLog.Snapshot());
    }

    [Fact]
    public void The_mark_is_taken_where_the_player_stops_watching()
    {
        // WHY `BeforeSideTurnEnd` and not the After twin: every end-of-turn
        // tenant that puts an element on the board runs later than this line
        // (Durin's consume and the whole `CompanionOverhaulTurnEnd` volley are
        // in `AfterSideTurnEnd(Player)`), so a mark taken there would file the
        // rows this row is about on the watched side.
        var calls = Il.Calls(
            Il.Method("KleeElementalHooks", "BeforeSideTurnEnd"));

        Assert.Contains("ReactionLog.MarkPlayerTurnEnd", calls);
    }

    [Fact]
    public void The_carry_rides_the_same_call_as_the_counters()
    {
        // The window is still exactly the one every other per-turn reaction
        // fact keeps -- what changed is what that call KEEPS, not when it runs.
        var calls = Il.Calls(Il.Method("ReactionEffects", "MarkTurnStart"));

        Assert.Contains("ReactionLog.MarkTurnStart", calls);
    }
}
