using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Diagnostics;
using KleeMod.Story;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Map;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs.History;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// WHEN THE STORY ROOM COMES, and what a story choice logs (ruled 2026-10-19,
/// <c>review/active/story-rewards-pass-2026-10-19.md</c>, items 2 and 4:
/// "Yep, agreed on all of the above!"). The act's story room is its 1st, 2nd
/// or 3rd event room, each with chance 1/3, from one roll on the run's seed
/// and the act; an act with fewer event rooms takes the chain's skip branch.
/// </summary>
public class StoryRoomTimingTests
{
    private static readonly Type KleeType = typeof(global::KleeMod.Klee);
    private static readonly Type VarkaType = typeof(global::KleeMod.Varka);
    private static readonly Type FurinaType = typeof(global::KleeMod.Furina);
    private static readonly Type KokomiType = typeof(global::KleeMod.Kokomi);

    private static readonly IReadOnlyList<StoryRecord> None = Array.Empty<StoryRecord>();

    private static ulong Seed(int i) => (ulong)i * 0x9E3779B97F4A7C15UL + 12345UL;

    // ---- The schedule -----------------------------------------------------------

    [Fact]
    public void The_schedule_is_one_third_two_thirds_certain()
    {
        Assert.Equal(new[] { 1.0 / 3.0, 2.0 / 3.0, 1.0 }, StoryRules.StoryRoomThresholds);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(1)]
    [InlineData(2)]
    public void The_story_room_is_the_1st_2nd_or_3rd_event_room_equally(int act)
    {
        const int n = 30000;
        var counts = new int[4];
        for (var i = 0; i < n; i++) counts[StoryRules.StoryRoomNumber(Seed(i), act)]++;
        Assert.Equal(0, counts[0]);
        for (var room = 1; room <= 3; room++)
        {
            Assert.InRange(counts[room] / (double)n, 1.0 / 3.0 - 0.015, 1.0 / 3.0 + 0.015);
        }
    }

    [Fact]
    public void Due_is_cumulative_one_roll_an_act_not_one_a_room()
    {
        const int n = 30000;
        var dueBy = new int[3];
        for (var i = 0; i < n; i++)
        {
            var seed = Seed(i);
            for (var act = 0; act < 3; act++)
            {
                var number = StoryRules.StoryRoomNumber(seed, act);
                for (var before = 0; before < 6; before++)
                {
                    // Due from its own room on, never before it.
                    Assert.Equal(before + 1 >= number, StoryRules.StoryRoomDue(seed, act, before));
                }
                Assert.True(StoryRules.StoryRoomDue(seed, act, 2));
            }
            for (var before = 0; before < 3; before++)
            {
                if (StoryRules.StoryRoomDue(seed, 0, before)) dueBy[before]++;
            }
        }
        // By the 2nd room 2/3 (not the 7/9 independent rolls would give).
        Assert.InRange(dueBy[0] / (double)n, 0.318, 0.348);
        Assert.InRange(dueBy[1] / (double)n, 0.652, 0.682);
        Assert.Equal(n, dueBy[2]);
        Assert.False(StoryRules.StoryRoomDue(Seed(1), 0, -1));
    }

    [Fact]
    public void The_roll_is_the_same_every_time_it_is_read_and_differs_by_act()
    {
        var sameAcrossActs = 0;
        for (var i = 0; i < 3000; i++)
        {
            var seed = Seed(i);
            for (var act = 0; act < 3; act++)
            {
                Assert.Equal(StoryRules.StoryRoomRoll(seed, act), StoryRules.StoryRoomRoll(seed, act));
                var r = StoryRules.StoryRoomRoll(seed, act);
                Assert.InRange(r, 0.0, 0.9999999999);
            }
            if (StoryRules.StoryRoomNumber(seed, 0) == StoryRules.StoryRoomNumber(seed, 1)) sameAcrossActs++;
        }
        // The acts' rolls are independent: they agree about a third of the time.
        Assert.InRange(sameAcrossActs / 3000.0, 0.28, 0.39);
    }

    // ---- The room the game's seam asks about -------------------------------------

    [Fact]
    public void Not_due_the_room_stays_the_drawn_event_due_it_is_the_story_room()
    {
        var solo = new (Type, IReadOnlyList<StoryRecord>)[] { (KleeType, None) };
        for (var i = 0; i < 200; i++)
        {
            var seed = Seed(i);
            for (var act = 0; act < 3; act++)
            {
                for (var before = 0; before < 4; before++)
                {
                    var expected = StoryRules.StoryRoomDue(seed, act, before)
                        ? StoryRules.RoomEventFor(solo, act, seed)
                        : null;
                    Assert.Equal(expected, StoryRules.StoryRoomEventFor(solo, act, seed, before));
                }
            }
        }
    }

    [Fact]
    public void Co_op_every_client_computes_the_same_room()
    {
        // Each client builds the seats from the shared run in seat order, the
        // seed and the act are shared, and the map history the count is read
        // from is shared: the same inputs, the same model.
        var table = new (Type, IReadOnlyList<StoryRecord>)[] { (FurinaType, None), (VarkaType, None) };
        for (var i = 0; i < 500; i++)
        {
            var seed = Seed(i);
            for (var act = 0; act < 3; act++)
            {
                for (var before = 0; before < 4; before++)
                {
                    var hostCopy = table.ToArray();
                    var guestCopy = table.ToArray();
                    var host = StoryRules.StoryRoomEventFor(hostCopy, act, seed, before);
                    var guest = StoryRules.StoryRoomEventFor(guestCopy, act, seed, before);
                    Assert.Equal(host, guest);
                    // The timing does not depend on who sits at the table.
                    Assert.Equal(StoryRules.StoryRoomDue(seed, act, before), host != null);
                }
            }
        }
    }

    /// <summary>A run, act by act: <paramref name="eventRooms"/>[act] event
    /// rooms, the story taking the first one due, its owner choosing "X".</summary>
    private static List<StoryRecord> Play(Type character, ulong seed, int[] eventRooms)
    {
        var records = new List<StoryRecord>();
        for (var act = 0; act < eventRooms.Length; act++)
        {
            for (var before = 0; before < eventRooms[act]; before++)
            {
                var seats = new (Type, IReadOnlyList<StoryRecord>)[] { (character, records.ToList()) };
                var room = StoryRules.StoryRoomEventFor(seats, act, seed, before);
                if (room == null) continue;
                records.Add(new StoryRecord(act, room, "X"));
            }
        }
        return records;
    }

    [Fact]
    public void One_story_room_an_act_and_none_when_the_act_runs_short()
    {
        foreach (var character in new[] { KleeType, VarkaType, FurinaType, KokomiType })
        {
            for (var i = 0; i < 300; i++)
            {
                var seed = Seed(i);
                var rooms = new[] { i % 4, (i / 4) % 4, (i / 16) % 4 };
                var records = Play(character, seed, rooms);
                for (var act = 0; act < 3; act++)
                {
                    var fired = records.Count(r => r.ActIndex == act);
                    Assert.Equal(rooms[act] >= StoryRules.StoryRoomNumber(seed, act) ? 1 : 0, fired);
                }
            }
        }
    }

    [Fact]
    public void A_skipped_act_takes_the_chains_skip_branch()
    {
        foreach (var character in new[] { KleeType, VarkaType, FurinaType, KokomiType })
        {
            var story = StoryRegistry.For(character)!;
            var home1 = story.Events.Single(e => e.ActIndex == 1 && e.Home);
            var home2 = story.Events.Single(e => e.ActIndex == 2 && e.Home);
            var checkedSkip1 = 0;
            var checkedSkip2 = 0;
            for (var i = 0; i < 400; i++)
            {
                var seed = Seed(i);
                // Act 1 with one event room: skipped unless its roll says the 1st.
                var records = Play(character, seed, new[] { 1, 3, 0 });
                var act1Fired = StoryRules.StoryRoomNumber(seed, 0) == 1;
                Assert.Equal(act1Fired, records.Any(r => r.ActIndex == 0));
                var act2 = records.Single(r => r.ActIndex == 1);
                if (!act1Fired)
                {
                    // No act-1 event: act 2 offers the home thread.
                    Assert.Equal(home1.EventType, act2.EventType);
                    checkedSkip1++;
                }
                else
                {
                    Assert.Equal(StoryRules.Route(story, 1, records.Where(r => r.ActIndex == 0).ToList(), seed)!.EventType,
                        act2.EventType);
                }
                // Act 2 with no event rooms at all: act 3 offers the home finale.
                var short2 = Play(character, seed, new[] { 3, 0, 3 });
                Assert.DoesNotContain(short2, r => r.ActIndex == 1);
                Assert.Equal(home2.EventType, short2.Single(r => r.ActIndex == 2).EventType);
                checkedSkip2++;
            }
            Assert.True(checkedSkip1 > 200, $"{story.Name}: {checkedSkip1}");
            Assert.Equal(400, checkedSkip2);
        }
    }

    // ---- Counting the act's event rooms ----------------------------------------

    private static MapPointHistoryEntry Point(MapPointType type, params RoomType[] rooms)
    {
        var point = new MapPointHistoryEntry { MapPointType = type };
        foreach (var r in rooms) point.Rooms.Add(new MapPointRoomHistoryEntry { RoomType = r });
        return point;
    }

    [Fact]
    public void Every_event_room_counts_story_or_not_and_an_Ancient_does_not()
    {
        var act = new[]
        {
            Point(MapPointType.Ancient, RoomType.Event),
            Point(MapPointType.Monster, RoomType.Monster),
            Point(MapPointType.Unknown, RoomType.Event),                   // a drawn event
            Point(MapPointType.Unknown, RoomType.Monster),                 // a ? that rolled a fight
            Point(MapPointType.Unknown, RoomType.Event, RoomType.Monster), // an event that starts a fight
            Point(MapPointType.Unknown, RoomType.Treasure),
            Point(MapPointType.Shop, RoomType.Shop),
            Point(MapPointType.Unknown, RoomType.Event),                   // a story room, or Lantern Key's
            Point(MapPointType.RestSite, RoomType.RestSite),
            Point(MapPointType.Unknown),                                   // no room recorded
        };
        Assert.Equal(3, StoryHistory.EventRooms(act));
        Assert.Equal(0, StoryHistory.EventRooms(Array.Empty<MapPointHistoryEntry>()));
        Assert.Equal(2, StoryRules.EventRoomsIn(new[] { (false, true), (true, true), (false, false), (false, true) }));
    }

    [Fact]
    public void The_seam_counts_the_current_acts_history()
    {
        var calls = Il.Calls(typeof(StoryHistory).GetMethod(nameof(StoryHistory.EventRoomsThisAct))!);
        Assert.Contains("IRunState.get_MapPointHistory", calls);
        Assert.Contains("IRunState.get_CurrentActIndex", calls);
        Assert.Contains("StoryHistory.EventRooms", calls);
    }

    // ---- The choice telemetry ---------------------------------------------------

    [Fact]
    public void A_story_choice_logs_the_state_before_and_what_it_gave()
    {
        var record = new StoryChoiceRecord
        {
            Event = "KLEEMOD-KLEE_STARSNATCH_CLIFF",
            Option = "BOMB",
            Character = "Klee",
            CharacterId = "KLEEMOD-KLEE",
            Act = 1,
            Floor = 6,
            HpBefore = 50,
            MaxHpBefore = 70,
            GoldBefore = 120,
            DeckBefore = 12,
            EventRoom = 2,
        };
        record.CardsOffered.Add(("CARD.A", false));
        record.CardsOffered.Add(("CARD.B", true));
        record.CardsPicked.Add(("CARD.B", true));
        record.RelicsGained.Add("RELIC.X");
        record.PotionsOffered.Add("POTION.Y");
        var json = record.ToJson("1", "human", "", "SEED", "s#0", 1.5);
        Assert.Equal("story", (string)json["record"]!);
        Assert.Equal("KLEEMOD-KLEE_STARSNATCH_CLIFF", (string)json["event"]!);
        Assert.Equal("BOMB", (string)json["option"]!);
        Assert.Equal(1, (int)json["act"]!);
        Assert.Equal(6, (int)json["floor"]!);
        Assert.Equal(2, (int)json["event_room"]!);
        Assert.Equal(50, (int)json["hp_before"]!);
        Assert.Equal(70, (int)json["max_hp_before"]!);
        Assert.Equal(120, (int)json["gold_before"]!);
        Assert.Equal(12, (int)json["deck_before"]!);
        Assert.Equal(2, json["cards_offered"]!.AsArray().Count);
        Assert.True((bool)json["cards_picked"]![0]!["upgraded"]!);
        Assert.Equal("CARD.B", (string)json["cards_picked"]![0]!["id"]!);
        Assert.Empty(json["cards_added"]!.AsArray());
        Assert.Equal("RELIC.X", (string)json["relics_gained"]![0]!);
        Assert.Equal("POTION.Y", (string)json["potions_offered"]![0]!);
        Assert.Equal("SEED", (string)json["run_id"]!);
        Assert.Equal("Klee", (string)json["character"]!);
        Assert.Equal("KLEEMOD-KLEE", (string)json["character_id"]!);
    }

    [Fact]
    public void Choosing_an_option_writes_the_story_record()
    {
        Assert.Contains("PlayTelemetry.StoryChoice", Il.Calls(Il.Method(nameof(StoryEventModel), "Choose")));
        Assert.Contains("StoryHistory.EventRoomsThisAct", Il.Calls(Il.Method(nameof(StoryEventModel), "BeginChoice")));
    }
}
