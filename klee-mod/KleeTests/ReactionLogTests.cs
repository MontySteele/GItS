using System.Linq;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-681`: NO REACTION HAPPENS UNNAMED.
///
/// THE FIND (Kokomi r27). Lane 2, fight 4: Slack Water put Hydro on a body,
/// Shinobu's Thundergrust hit it with Electro, and the panel showed Poison 8
/// where the Electro-Charged rule prints 4. The eight was TWO procs -- the
/// Tamakushi Casket answered the Weak with a 2 Hydro ping, which landed on the
/// fresh Electro aura and reacted a second time -- and the seat rebuilt the
/// whole beat from a doubled number: "I only trusted my reading because it
/// reproduced four times." Lane 1, (c) 2, is the same hole from the other
/// side: "Gorou+'s Crystallize did not visibly fire in fight 5 turn 2", and no
/// screen could settle whether it had.
///
/// THE BOUNDARY is `ReactionSeatCountTests`': `ReactionEffects.Resolve` is an
/// async game path needing a live `PlayerChoiceContext` and cannot run here.
/// What CAN run is the log's own behaviour -- what a row says, the order, the
/// window -- plus an IL read proving `Resolve` writes to it, which is what
/// makes "the single funnel" a checked claim rather than a comment.
/// </summary>
public class ReactionLogTests
{
    [Fact]
    public void The_single_funnel_writes_every_reaction_to_the_log()
    {
        // `ReactionEffects.Resolve` says of itself that it is "the single site
        // a reaction resolves in the mod". That is the whole basis for the
        // row's acceptance, so the call is pinned rather than trusted.
        var calls = Il.Calls(Il.Method("ReactionEffects", "Resolve"));

        Assert.Contains("ReactionLog.Note", calls);
    }

    [Fact]
    public void The_turn_window_is_cleared_by_the_same_call_as_the_counters()
    {
        var calls = Il.Calls(Il.Method("ReactionEffects", "MarkTurnStart"));

        Assert.Contains("ReactionLog.MarkTurnStart", calls);
    }

    [Fact]
    public void Two_reactions_in_one_beat_are_two_rows_in_order()
    {
        // The r27 beat itself: Thundergrust's Electro onto a Hydro aura, then
        // the Casket's answering Hydro ping onto the Electro aura that hit
        // left behind. One number reached the seat; two things happened.
        ReactionLog.MarkTurnStart();
        var seat = Seat.Kokomi();

        ReactionLog.Note(Reaction.ElectroCharged, seat.Creature, seat.Creature,
                         null);
        ReactionLog.Note(Reaction.ElectroCharged, seat.Creature, seat.Creature,
                         null);

        var rows = ReactionLog.Snapshot();
        Assert.Equal(2, rows.Count);
        Assert.All(rows, row => Assert.Equal("Electro-Charged",
                                             row["reaction"]));
    }

    [Fact]
    public void A_row_prints_the_words_the_page_defines()
    {
        // The enum spells `Overload` and `ElectroCharged`; every player
        // surface, the blind page's glossary included
        // (`blindplay_notes.REACTION_KEYWORDS`), prints "Overloaded" and
        // "Electro-Charged". A row and its definition on one screen cannot be
        // allowed to disagree.
        Assert.Equal("Overloaded", ReactionLog.PrintedName(Reaction.Overload));
        Assert.Equal("Electro-Charged",
                     ReactionLog.PrintedName(Reaction.ElectroCharged));
        Assert.Equal("Crystallize",
                     ReactionLog.PrintedName(Reaction.Crystallize));
    }

    [Fact]
    public void A_new_turn_drops_the_last_turn_s_beats()
    {
        ReactionLog.MarkTurnStart();
        ReactionLog.Note(Reaction.Frozen, Seat.Kokomi().Creature, null, null);
        Assert.Single(ReactionLog.Snapshot());

        ReactionLog.MarkTurnStart();

        // Present and EMPTY, which is the wire's own three-state contract: the
        // log is here and nothing has reacted yet this turn.
        Assert.Empty(ReactionLog.Snapshot());
    }

    [Fact]
    public void A_non_reaction_writes_nothing()
    {
        // `Resolve` calls in on every hit that consumed an aura, reaction or
        // not, so the guard is here rather than at the call site.
        ReactionLog.MarkTurnStart();

        ReactionLog.Note(Reaction.None, Seat.Kokomi().Creature, null, null);

        Assert.Empty(ReactionLog.Snapshot());
    }

    [Fact]
    public void The_wire_row_carries_the_four_keys_the_page_reads()
    {
        // The key names ARE the contract with
        // `understudy/blindplay_board.reaction_log`, the same discipline
        // `KokomiPlan.CarriedOutRow` keeps.
        ReactionLog.MarkTurnStart();
        ReactionLog.Note(Reaction.Swirl, Seat.Kokomi().Creature, null, null);

        var row = ReactionLog.Snapshot().Single();

        Assert.Equal(new[] { "reaction", "source", "target", "combat_id" },
                     row.Keys.ToArray());
    }
}
