using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Story;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE CO-OP STORY ROOMS (ruled 2026-10-16, the chains paper's "Co-op").
/// [USER]: "Is it possible to instead give them separate events, appropriate
/// to their character? And for characters who have no events, they get a
/// placeholder like "heal 10 or gain 50 gold"".
///
/// The routing is pure (<see cref="StoryRules.RoomEventFor"/>,
/// <see cref="StoryRules.CoopRoom"/>, <see cref="StoryRules.CoopEventFor"/>)
/// and is what both clients compute from shared state; the room model's wiring
/// is pinned structurally on the calls it makes.
/// </summary>
public class CoopStoryRoomTests
{
    private static readonly Type KleeType = typeof(global::KleeMod.Klee);
    private static readonly Type VarkaType = typeof(global::KleeMod.Varka);
    private static readonly Type FurinaType = typeof(global::KleeMod.Furina);
    private static readonly Type KokomiType = typeof(global::KleeMod.Kokomi);
    private static readonly Type Ironclad = typeof(MegaCrit.Sts2.Core.Models.Characters.Ironclad);

    private static readonly IReadOnlyList<StoryRecord> None = Array.Empty<StoryRecord>();

    private static (Type, IReadOnlyList<StoryRecord>)[] Seats(params (Type, IReadOnlyList<StoryRecord>)[] s) => s;

    private static CharacterStory T(Type character) => StoryRegistry.For(character)!;

    // ---- Who gets what ---------------------------------------------------------

    [Theory]
    [InlineData(0)]
    [InlineData(1)]
    [InlineData(2)]
    public void Furina_and_Varka_each_get_their_own_event_in_one_room(int act)
    {
        var seats = Seats((FurinaType, None), (VarkaType, None));
        Assert.Equal(typeof(StoryCoopRoomEvent), StoryRules.RoomEventFor(seats, act, 7UL));
        var room = StoryRules.CoopRoom(seats, act, 7UL)!;
        Assert.Equal(2, room.Count);
        Assert.Contains(room[0]!, T(FurinaType).Events);
        Assert.Contains(room[1]!, T(VarkaType).Events);
        Assert.Equal(act, room[0]!.ActIndex);
        Assert.Equal(act, room[1]!.ActIndex);
        // Each is that player's solo routing.
        Assert.Same(StoryRules.Route(T(FurinaType), act, None, 7UL), room[0]);
        Assert.Same(StoryRules.Route(T(VarkaType), act, None, 7UL), room[1]);
    }

    [Fact]
    public void Klee_gets_her_event_and_Kokomi_the_placeholder()
    {
        foreach (var seats in new[]
                 {
                     Seats((KleeType, None), (KokomiType, None)),
                     Seats((KokomiType, None), (KleeType, None)),
                 })
        {
            Assert.Equal(typeof(StoryCoopRoomEvent), StoryRules.RoomEventFor(seats, 0, 7UL));
            var room = StoryRules.CoopRoom(seats, 0, 7UL)!;
            var klee = seats[0].Item1 == KleeType ? 0 : 1;
            Assert.Contains(room[klee]!, T(KleeType).Events);
            Assert.Null(room[1 - klee]); // the placeholder
        }
        Assert.Null(StoryRules.CoopEventFor(KokomiType, None, 0, 7UL));
        Assert.Null(StoryRules.CoopEventFor(Ironclad, None, 1, 7UL));
        Assert.Null(StoryRules.CoopEventFor(null, None, 0, 7UL));
    }

    [Fact]
    public void A_seat_whose_story_already_fired_this_act_gets_the_placeholder()
    {
        var kleeAct1 = StoryRules.Route(T(KleeType), 0, None, 7UL)!;
        var fired = new[] { new StoryRecord(0, kleeAct1.EventType, "X") };
        var seats = Seats((KleeType, fired), (VarkaType, None));
        var room = StoryRules.CoopRoom(seats, 0, 7UL)!;
        Assert.Null(room[0]);
        Assert.Contains(room[1]!, T(VarkaType).Events);

        // Every story at the table fired this act: no story room at all.
        var varkaAct1 = StoryRules.Route(T(VarkaType), 0, None, 7UL)!;
        var both = Seats((KleeType, fired), (VarkaType, new[] { new StoryRecord(0, varkaAct1.EventType, "Y") }));
        Assert.Null(StoryRules.CoopRoom(both, 0, 7UL));
        Assert.Null(StoryRules.RoomEventFor(both, 0, 7UL));
    }

    [Fact]
    public void A_table_with_no_story_this_act_keeps_the_drawn_event()
    {
        Assert.Null(StoryRules.RoomEventFor(Seats((KokomiType, None), (Ironclad, None)), 0, 7UL));
        Assert.Null(StoryRules.RoomEventFor(Seats((KleeType, None), (VarkaType, None)), 3, 7UL));
    }

    [Fact]
    public void Each_seat_routes_on_its_own_story_whatever_its_seat()
    {
        var a = StoryRules.CoopRoom(Seats((FurinaType, None), (VarkaType, None)), 0, 99UL)!;
        var b = StoryRules.CoopRoom(Seats((VarkaType, None), (FurinaType, None)), 0, 99UL)!;
        Assert.Same(a[0], b[1]);
        Assert.Same(a[1], b[0]);
        // The same shared state gives the same room, every time it is asked.
        for (var i = 0; i < 5; i++)
        {
            Assert.Equal(a, StoryRules.CoopRoom(Seats((FurinaType, None), (VarkaType, None)), 0, 99UL));
        }
    }

    // ---- Solo is unchanged -----------------------------------------------------

    [Fact]
    public void Solo_still_draws_her_own_event_type()
    {
        foreach (var c in new[] { KleeType, VarkaType, FurinaType })
        {
            for (var act = 0; act < 4; act++)
            {
                for (ulong seed = 0; seed < 20; seed++)
                {
                    var solo = Seats((c, None));
                    Assert.Equal(StoryRules.EventFor(solo, act, seed)?.EventType,
                        StoryRules.RoomEventFor(solo, act, seed));
                }
            }
            Assert.NotEqual(typeof(StoryCoopRoomEvent), StoryRules.RoomEventFor(Seats((c, None)), 0, 7UL));
        }
        Assert.Null(StoryRules.RoomEventFor(Seats((KokomiType, None)), 0, 7UL));
    }

    // ---- The chain, per player -------------------------------------------------

    private static string Choice(Type evt, string key) =>
        $"{StoryRegistry.EntryOf(evt)}.pages.INITIAL.options.{key}.title";

    [Fact]
    public void Each_players_chain_records_only_her_own_event()
    {
        // The co-op room visits its own model, never a player's event: the
        // choice in each player's run history is what records it.
        var notVisited = (Func<Type, bool>)(_ => false);
        var furinaKeys = new string?[] { Choice(typeof(FurinaRisingWater), "STAND_IN_IT") };
        var varkaKeys = new string?[] { Choice(typeof(VarkaRearguard), "LEAVE_SUPPLIES") };

        var furina = StoryRules.Records(T(FurinaType), notVisited, furinaKeys, StoryRegistry.EntryOf);
        var varka = StoryRules.Records(T(VarkaType), notVisited, varkaKeys, StoryRegistry.EntryOf);
        Assert.Equal(new StoryRecord(0, typeof(FurinaRisingWater), "STAND_IN_IT"), Assert.Single(furina));
        Assert.Equal(new StoryRecord(0, typeof(VarkaRearguard), "LEAVE_SUPPLIES"), Assert.Single(varka));
        // Another player's choice is not hers.
        Assert.Empty(StoryRules.Records(T(FurinaType), notVisited, varkaKeys, StoryRegistry.EntryOf));

        // The act's later event rooms are not story rooms again.
        Assert.Null(StoryRules.RoomEventFor(Seats((FurinaType, furina), (VarkaType, varka)), 0, 7UL));

        // Act 2: one room, each on her own thread, opening on her own choice.
        var room = StoryRules.CoopRoom(Seats((FurinaType, furina), (VarkaType, varka)), 1, 7UL)!;
        Assert.Equal(typeof(FurinaOratricesEcho), room[0]!.EventType);
        Assert.Equal(typeof(VarkaWolfOfTheNorth), room[1]!.EventType);
        Assert.Equal("STOOD", StoryRules.OpeningFor(room[0]!, furina)!.Key);
    }

    // ---- The placeholder -------------------------------------------------------

    [Fact]
    public void The_placeholder_heals_10_or_gives_50_Gold()
    {
        var q = StoryCoop.QuietLanding;
        Assert.Equal("A Quiet Landing", q.Title);
        Assert.DoesNotContain("\n", q.Body);
        Assert.Equal(2, q.Options.Count);
        var heal = q.Options[0];
        Assert.Equal("Heal 10 HP.", heal.Description);
        Assert.Equal(StoryEffectKind.Heal, heal.Effect.Kind);
        Assert.Equal(10, heal.Effect.Amount);
        Assert.Empty(heal.Then);
        var gold = q.Options[1];
        Assert.Equal("Gain 50 Gold.", gold.Description);
        Assert.Equal(StoryEffectKind.GainGold, gold.Effect.Kind);
        Assert.Equal(50, gold.Effect.Amount);
        Assert.Empty(gold.Then);
        // Never locked, and free.
        var broke = new StoryDeckView(0, 0, 0, 0, 0);
        Assert.All(q.Options, o => Assert.False(StoryRules.IsLocked(o, broke)));
        Assert.All(q.Options, o => Assert.Equal(0, o.HpCost));
        Assert.Empty(q.Openings);
        // In no character's table.
        Assert.DoesNotContain(StoryRegistry.All, s => s.Events.Contains(q));
    }

    [Fact]
    public void The_placeholder_page_has_its_loc_rows_under_the_room()
    {
        var rows = StoryLoc.EventRows();
        var entry = StoryRegistry.EntryOf(typeof(StoryCoopRoomEvent));
        var q = StoryCoop.QuietLanding;
        Assert.Equal(q.Title, rows[entry + ".title"]);
        Assert.Equal(q.Body, rows[entry + ".pages.INITIAL.description"]);
        foreach (var o in q.Options)
        {
            Assert.Equal(o.Title, rows[StoryEventModel.OptionTitleKey(entry, o)]);
            Assert.Equal(o.Description, rows[StoryEventModel.OptionDescriptionKey(entry, o)]);
            Assert.Equal(q.Body, rows[StoryEventModel.ResultKey(entry, o)]);
        }
    }

    // ---- The room model (structural) -------------------------------------------

    [Fact]
    public void The_room_routes_each_copy_from_its_owners_saved_story()
    {
        var resolve = Il.Calls(Il.Method(nameof(StoryCoopRoomEvent), "ResolveFor"));
        Assert.Contains("StoryRules.CoopEventFor", resolve);
        Assert.Contains("StoryHistory.RecordsFor", resolve);
        // Read before the page and its options: BeforeEventStarted resolves.
        Assert.Contains("StoryEventModel.ResolveFor",
            Il.Calls(Il.Method(nameof(StoryEventModel), "BeforeEventStarted")));
        // The options, results and pool prompt carry the routed event's keys.
        Assert.Contains("StoryEventModel.get_LocEntry",
            Il.Calls(Il.Method(nameof(StoryEventModel), "GenerateInitialOptions")));
        Assert.Contains("StoryEventModel.get_LocEntry",
            Il.Calls(Il.Method(nameof(StoryEventModel), "Choose")));
        // The co-op hook asks the room rule.
        var patch = typeof(StoryEventModel).Assembly.GetTypes()
            .Single(t => t.Name == "Hook_ModifyNextEvent_Story_Patch");
        Assert.Contains("StoryRules.RoomEventFor", Il.Calls(patch.GetMethod("Postfix", HeadlessGame.All)!));
        // Its title follows the routed event.
        Assert.Contains(typeof(StoryEventModel).Assembly.GetTypes(), t => t.Name == "EventModel_Title_Story_Patch");
    }

    private static object? Get(object o, string property) =>
        o.GetType().GetProperty(property, HeadlessGame.All)!.GetValue(o);

    [Fact]
    public void Every_player_takes_the_options_in_the_room()
    {
        var room = new StoryCoopRoomEvent();
        var isOwners = typeof(StoryCoopRoomEvent).GetProperty("IsOwners", HeadlessGame.All)!;
        Assert.Equal(typeof(StoryCoopRoomEvent), isOwners.GetMethod!.DeclaringType);
        Assert.True((bool)isOwners.GetValue(room)!);

        // Unrouted (the canonical model, or a player with no event): the
        // placeholder, under the room's own rows and title.
        Assert.Same(StoryCoop.QuietLanding, Get(room, "StoryData"));
        Assert.Null(Get(room, "Story"));
        Assert.Null(Get(room, "TitleKeyOverride"));
        Assert.Equal(StoryCoop.QuietLanding.FallbackPortraitPath, Get(room, "FallbackPortraitPath"));

        // Routed to Furina's An Empty House: her page, her rows, her title,
        // and the room's one base picture.
        var house = FurinaStory.Table.Events[0];
        typeof(StoryCoopRoomEvent).GetField("_routed", HeadlessGame.All)!.SetValue(room, house);
        Assert.Same(house, Get(room, "StoryData"));
        Assert.Same(FurinaStory.Table, Get(room, "Story"));
        Assert.Equal(StoryRegistry.EntryOf(typeof(FurinaEmptyHouse)) + ".title", Get(room, "TitleKeyOverride"));
        Assert.Equal(StoryCoop.QuietLanding.FallbackPortraitPath, Get(room, "FallbackPortraitPath"));
        // A character's own event type still goes only to its owner (a room
        // saved before the co-op story rooms).
        Assert.True(StoryRules.IsOwnersEvent(FurinaType, typeof(FurinaEmptyHouse)));
        Assert.False(StoryRules.IsOwnersEvent(VarkaType, typeof(FurinaEmptyHouse)));
    }
}
