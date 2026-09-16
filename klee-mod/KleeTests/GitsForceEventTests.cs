#nullable enable

using System.Collections.Generic;
using STS2_MCP;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-761. THE ONE INDEX `force_next_event` COMPUTES, PINNED HEADLESSLY.
///
/// The op puts a named event at the act's event cursor so the next `?` room
/// opens on it. Everything about that is one calculation, and the calculation
/// has exactly one way to look right and be wrong: `RoomSet.NextEvent` reads
/// `events[eventsVisited % events.Count]`, NOT `events[0]`. An op that wrote
/// index 0 would answer ok, move a real entry, and change nothing about the
/// next room -- on floor 1 of a fresh act it would even pass a live smoke,
/// because the cursor is 0 there.
///
/// `vendor/STS2_MCP/gits/GitsForceEvent.cs` is deliberately free of Godot,
/// Harmony and game types so this file can compile THAT source (not a fork of
/// it) and exercise the decision without a run, exactly as
/// `GitsPortPrecedenceTests` does for the port resolver. The half that needs
/// `ActModel` -- reaching the act's `RoomSet` by reflection and refusing an
/// event the run has already visited -- stays in `GitsDebugState.cs` and owes
/// a live smoke.
/// </summary>
public class GitsForceEventTests
{
    private static List<string> Events() => new()
    {
        "A_NIGHT_AT_THE_INN", "ROOM_FULL_OF_CHEESE", "THE_CLEANSING_SPRING",
        "WINDRISE_PICNIC"
    };

    [Fact]
    public void TheSlotIsTheCursorAndNotZero()
    {
        // Two `?` rooms visited: the act reads index 2 next, so that is where
        // a forced event has to land.
        var found = GitsForceEvent.Locate(Events(), 2, "WINDRISE_PICNIC");
        Assert.True(found.Found);
        Assert.Equal(3, found.Index);
        Assert.Equal(2, found.Slot);
        Assert.Equal(4, found.Count);
        Assert.False(found.AlreadyNext);
    }

    [Fact]
    public void TheCursorWrapsTheWayTheGameWrapsIt()
    {
        // `eventsVisited` is never reset within an act and the game allows
        // repetition once the unique events are exhausted, so a counter past
        // the list length is an ordinary state and not an error.
        Assert.Equal(1, GitsForceEvent.Locate(Events(), 5, "").Slot);
        Assert.Equal(0, GitsForceEvent.Locate(Events(), 8, "").Slot);
    }

    [Fact]
    public void ANegativeCounterCannotIndexOutOfTheList()
    {
        // C#'s `%` keeps the sign of its left operand. The game does not
        // produce a negative counter; a save that did must not crash the
        // route, which is the whole of this test.
        var slot = GitsForceEvent.Locate(Events(), -3, "").Slot;
        Assert.InRange(slot, 0, 3);
    }

    [Fact]
    public void AnEventAlreadyAtTheCursorIsNotAWrite()
    {
        var at = GitsForceEvent.Locate(Events(), 1, "ROOM_FULL_OF_CHEESE");
        Assert.True(at.Found);
        Assert.True(at.AlreadyNext);
        Assert.False(GitsForceEvent.Swap(Events(), at.Index, at.Slot));
    }

    [Fact]
    public void AnUnknownIdIsNotFoundAndStillReportsWhereTheCursorPoints()
    {
        // The refusal is the caller's to make, and it reads better with the
        // list length and the cursor in hand than without.
        var miss = GitsForceEvent.Locate(Events(), 2, "SPRINGVALE_CHEESE");
        Assert.False(miss.Found);
        Assert.Equal(-1, miss.Index);
        Assert.Equal(2, miss.Slot);
        Assert.Equal(4, miss.Count);
        Assert.Equal("", miss.Resolved);
    }

    [Fact]
    public void AnEmptyActHasNoSlotAtAll()
    {
        var none = GitsForceEvent.Locate(new List<string>(), 0, "ANYTHING");
        Assert.False(none.Found);
        Assert.Equal(-1, none.Slot);
        Assert.Equal(0, none.Count);
    }

    [Fact]
    public void AnEmptyTargetIsNotFoundButIsNotAnError()
    {
        // The GET half asks for the cursor with no target, to report
        // `next_event`. It must answer a slot and claim nothing found.
        var probe = GitsForceEvent.Locate(Events(), 3, "");
        Assert.False(probe.Found);
        Assert.Equal(3, probe.Slot);
    }

    [Fact]
    public void ALooseSpellingResolvesAndTheListsOwnSpellingComesBack()
    {
        // `GitsDebugState`'s standing rule for every id it resolves: a caller
        // that spelled it loosely is entitled to see which entry was reached.
        var hit = GitsForceEvent.Locate(Events(), 0, "room_full_of_cheese");
        Assert.True(hit.Found);
        Assert.Equal(1, hit.Index);
        Assert.Equal("ROOM_FULL_OF_CHEESE", hit.Resolved);
    }

    [Fact]
    public void AnExactMatchWinsOverACaseInsensitiveOne()
    {
        var ids = new List<string> { "cheese", "CHEESE" };
        Assert.Equal(1, GitsForceEvent.Locate(ids, 0, "CHEESE").Index);
        Assert.Equal(0, GitsForceEvent.Locate(ids, 0, "cheese").Index);
    }

    [Fact]
    public void TheSwapMovesTwoEntriesAndKeepsTheListLength()
    {
        // LENGTH IS LOAD-BEARING: it is what `NextEvent`'s modulo divides by,
        // so an insert would renumber every slot behind the cursor and change
        // which event every LATER `?` room in the act opens.
        var ids = Events();
        Assert.True(GitsForceEvent.Swap(ids, 3, 1));
        Assert.Equal(4, ids.Count);
        Assert.Equal("WINDRISE_PICNIC", ids[1]);
        Assert.Equal("ROOM_FULL_OF_CHEESE", ids[3]);
        Assert.Contains("A_NIGHT_AT_THE_INN", ids);
        Assert.Contains("THE_CLEANSING_SPRING", ids);
    }

    [Theory]
    [InlineData(-1, 0)]
    [InlineData(0, -1)]
    [InlineData(0, 4)]
    [InlineData(4, 0)]
    [InlineData(2, 2)]
    public void AnIndexTheListDoesNotHaveWritesNothing(int from, int to)
    {
        var ids = Events();
        Assert.False(GitsForceEvent.Swap(ids, from, to));
        Assert.Equal(Events(), ids);
    }

    [Fact]
    public void ForcingTwiceInARowLeavesTheSecondEventNext()
    {
        // The sequence a session actually runs: force, walk, force again. The
        // second force must read the list as the first one left it.
        var ids = Events();
        var first = GitsForceEvent.Locate(ids, 2, "WINDRISE_PICNIC");
        GitsForceEvent.Swap(ids, first.Index, first.Slot);
        Assert.Equal("WINDRISE_PICNIC", ids[2]);

        // One `?` room visited, so the cursor advances by one.
        var second = GitsForceEvent.Locate(ids, 3, "ROOM_FULL_OF_CHEESE");
        Assert.True(second.Found);
        GitsForceEvent.Swap(ids, second.Index, second.Slot);
        Assert.Equal("ROOM_FULL_OF_CHEESE", ids[3]);
        Assert.Equal(4, ids.Count);
    }
}

// -------------------------------------------------- EB-770: run facts ----
//
// THE REFUSAL THAT COST FOUR LAUNCHES. `teyvat-proofs-7` forced
// `SLIPPERY_BRIDGE`, `RELIC_TRADER`, `RANWID_THE_ELDER` and
// `WELCOME_TO_WONGOS` and got back "IsAllowed is false" and nothing else --
// four launches spent learning only that. The predicate's source cannot be
// read at runtime, so the refusal now prints what the RUN holds and the
// caller compares it against the gate in `tools/data/sts2_base_events.json`.
// These pin the half that has no game type in it: the order of the facts and
// the sentence they make.

public sealed class GitsRunFactsTests
{
    private static Dictionary<string, object?> Sample(int gold = 120,
                                                      int players = 1) =>
        GitsForceEvent.Facts(
            currentActIndex: 1, totalFloor: 9, gold: gold, potions: 2,
            relics: 4, tradableRelics: 3, deckCards: 14, removableCards: 12,
            transformableCards: 11, currentHp: 55, maxHp: 80,
            playerCount: players);

    [Fact]
    public void EveryFactABaseGateAsksAboutIsInTheAnswer()
    {
        // The names are the MEMBER names the gates read, so that the printed
        // facts and the printed gate line up word for word.
        var facts = Sample();
        foreach (var key in new[]
                 {
                     "CurrentActIndex", "TotalFloor", "Gold", "Potions",
                     "Relics", "TradableRelics", "DeckCards",
                     "RemovableCards", "TransformableCards", "CurrentHp",
                     "MaxHp", "Players"
                 })
            Assert.True(facts.ContainsKey(key), key);
        Assert.Equal(12, facts.Count);
    }

    [Fact]
    public void TheActIndexIsReportedAsTheGateSpellsIt()
    {
        // ZERO-BASED, because `WelcomeToWongos.IsAllowed` is
        // `CurrentActIndex == 1`. Reporting the player-facing act number here
        // would make every act clause read off by one, which is exactly the
        // mistake the table exists to stop.
        Assert.Equal(1, Sample()["CurrentActIndex"]);
    }

    [Fact]
    public void TheSentenceKeepsTheDictionaryOrder()
    {
        var line = GitsForceEvent.DescribeFacts(Sample());
        Assert.StartsWith("This run holds: CurrentActIndex=1, TotalFloor=9, "
                          + "Gold=120,", line);
        Assert.EndsWith("Players=1.", line);
    }

    [Fact]
    public void NoFactsIsAnEmptyStringAndNotTheWordNull()
    {
        // A refusal appends this to its sentence. An empty string disappears;
        // the string "null" would be printed at the player.
        Assert.Equal("", GitsForceEvent.DescribeFacts(null));
        Assert.Equal("", GitsForceEvent.DescribeFacts(
            new Dictionary<string, object?>()));
    }

    [Fact]
    public void ThePartySizeTravelsWithTheNumbers()
    {
        // Every base gate is `Players.All(...)`, so a two-player refusal's
        // numbers are the worst player's. The count says so.
        Assert.Equal(2, Sample(players: 2)["Players"]);
    }
}
