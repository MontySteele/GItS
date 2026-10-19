using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text.Json.Nodes;
using KleeMod.RunStats;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Map;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Runs.History;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Saves.Runs;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// OPT-IN RUN STATS (2026-10-16; <c>KleeCode/RunStats/</c>). The trimmer
/// against a synthetic run (never a real .run file: those hold a Steam id),
/// the two switches, and the dev build's having no uploader at all.
///
/// The record is pinned to <c>Fixtures/run_stats_record_v1.json</c>, and
/// <c>tier0/tests/test_run_stats_record.py</c> validates that same file
/// against <c>telemetry-worker/schema/run-v1.json</c>. To re-pin after a
/// deliberate trimmer change: <c>GITS_REPIN_RUN_STATS=1 dotnet test
/// klee-mod/KleeTests --filter RunStatsTests</c>.
/// </summary>
public class RunStatsTests
{
    // Shaped like Steam ids on purpose: neither may reach the record.
    private const ulong Me = 76561198000000001UL;
    private const ulong Partner = 76561198000000002UL;

    private static readonly RunRecordContext Ctx = new(
        RunUuid: "0b5e3c3e-6f1a-4d2b-9c4d-3a2f1e0d9c8b",
        InstallId: "7d1f2e3c-4b5a-4968-8776-a5b4c3d2e1f0",
        ModVersion: "0.3.0", Variant: "beta", BuildId: "v0.111.0");

    private static ModelId Card(string e) => new("CARD", e);

    private static SerializableCard C(string e, int up = 0) =>
        new() { Id = Card(e), CurrentUpgradeLevel = up };

    private static PlayerMapPointHistoryEntry Stats(ulong id, int hp, int max, int dmg) =>
        new() { PlayerId = id, CurrentHp = hp, MaxHp = max, DamageTaken = dmg,
                CurrentGold = 999, GoldGained = 50 };

    private static MapPointHistoryEntry Point(MapPointType type, RoomType room, ModelId? model,
                                              PlayerMapPointHistoryEntry mine,
                                              PlayerMapPointHistoryEntry? theirs = null)
    {
        var mp = new MapPointHistoryEntry { MapPointType = type };
        mp.Rooms.Add(new MapPointRoomHistoryEntry { RoomType = room, ModelId = model, TurnsTaken = 3 });
        // The partner's row comes FIRST: the trimmer must find ours by id.
        if (theirs != null) mp.PlayerStats.Add(theirs);
        mp.PlayerStats.Add(mine);
        return mp;
    }

    /// <summary>A two-act co-op loss to the act-2 boss.</summary>
    internal static SerializableRun SyntheticRun(RoomType lastRoom = RoomType.Boss,
                                                 ModelId? lastModel = null)
    {
        var neow = Stats(Me, 70, 70, 0);
        neow.AncientChoices.Add(new AncientChoiceHistoryEntry(
            new LocString("ancients", "NEOW.pages.INITIAL.options.ARCANE_SCROLL.title"), true));
        neow.AncientChoices.Add(new AncientChoiceHistoryEntry(
            new LocString("ancients", "NEOW.pages.INITIAL.options.LEAD_PAPERWEIGHT.title"), false));

        var fight = Stats(Me, 61, 70, 9);
        fight.CardChoices.Add(new CardChoiceHistoryEntry { Card = C("KLEEMOD-KABOOM"), wasPicked = true });
        fight.CardChoices.Add(new CardChoiceHistoryEntry { Card = C("KLEEMOD-PROTO_SPARK_SPLASH"), wasPicked = false });
        fight.CardChoices.Add(new CardChoiceHistoryEntry { Card = C("KLEEMOD-POP"), wasPicked = false });

        var elite = Stats(Me, 40, 72, 30);
        elite.CardChoices.Add(new CardChoiceHistoryEntry { Card = C("KLEEMOD-POP"), wasPicked = false });
        elite.CardChoices.Add(new CardChoiceHistoryEntry { Card = C("KLEEMOD-KABOOM"), wasPicked = false });

        var act1 = new List<MapPointHistoryEntry>
        {
            Point(MapPointType.Ancient, RoomType.Event, new ModelId("EVENT", "NEOW"), neow,
                  Stats(Partner, 80, 80, 0)),
            Point(MapPointType.Monster, RoomType.Monster, new ModelId("ENCOUNTER", "TOADPOLES_WEAK"), fight,
                  Stats(Partner, 55, 80, 25)),
            Point(MapPointType.Unknown, RoomType.Event, new ModelId("EVENT", "BRAIN_LEECH"),
                  Stats(Me, 58, 70, 3), Stats(Partner, 55, 80, 0)),
            Point(MapPointType.RestSite, RoomType.RestSite, null,
                  Stats(Me, 70, 72, 0), Stats(Partner, 80, 80, 0)),
        };
        var act2 = new List<MapPointHistoryEntry>
        {
            Point(MapPointType.Elite, RoomType.Elite, new ModelId("ENCOUNTER", "BYRDONIS_ELITE"), elite,
                  Stats(Partner, 30, 80, 50)),
            Point(MapPointType.Shop, RoomType.Shop, null,
                  Stats(Me, 40, 72, 0), Stats(Partner, 30, 80, 0)),
            Point(MapPointType.Boss, lastRoom, lastModel ?? new ModelId("ENCOUNTER", "THE_KIN_BOSS"),
                  Stats(Me, 0, 72, 40), Stats(Partner, 0, 80, 30)),
        };

        var me = new SerializablePlayer
        {
            CharacterId = new ModelId("CHARACTER", "KLEEMOD-KLEE"), NetId = Me,
            CurrentHp = 0, MaxHp = 72, Gold = 321,
        };
        me.Deck.AddRange(new[] { C("STRIKE_KLEE"), C("DEFEND_KLEE"), C("KLEEMOD-KABOOM", 1) });
        me.Relics.Add(new SerializableRelic { Id = new ModelId("RELIC", "KLEEMOD-DODOCO") });
        me.Relics.Add(new SerializableRelic { Id = new ModelId("RELIC", "ARCANE_SCROLL") });
        var partner = new SerializablePlayer
        {
            CharacterId = new ModelId("CHARACTER", "IRONCLAD"), NetId = Partner, MaxHp = 80,
        };
        partner.Deck.Add(C("STRIKE_IRONCLAD"));

        return new SerializableRun
        {
            // The partner is FIRST in the list: the trimmer must pick by net id.
            Players = new List<SerializablePlayer> { partner, me },
            Acts = new List<SerializableActModel>
            {
                new() { Id = new ModelId("ACT", "OVERGROWTH") },
                new() { Id = new ModelId("ACT", "HIVE") },
            },
            MapPointHistory = new List<List<MapPointHistoryEntry>> { act1, act2 },
            Ascension = 3,
            GameMode = GameMode.Standard,
            RunTime = 2345,
            WinTime = 0,
        };
    }

    private static string FixturePath([CallerFilePath] string here = "") =>
        Path.Combine(Path.GetDirectoryName(here)!, "Fixtures", "run_stats_record_v1.json");

    // ---------------------------------------------------------- trimmer ---

    [Fact]
    public void The_trimmed_synthetic_run_matches_the_pinned_record()
    {
        var record = RunRecord.Trim(SyntheticRun(), isVictory: false, Me, Ctx);
        var path = FixturePath();
        if (Environment.GetEnvironmentVariable("GITS_REPIN_RUN_STATS") == "1")
        {
            var text = record.ToJsonString(new System.Text.Json.JsonSerializerOptions
            { WriteIndented = true }).Replace("\r\n", "\n") + "\n";
            File.WriteAllText(path, text);
        }
        var pinned = JsonNode.Parse(File.ReadAllText(path));
        Assert.True(JsonNode.DeepEquals(pinned, record),
            "the trimmer's output moved; re-pin deliberately (see the class summary)\n"
            + record.ToJsonString());
    }

    [Fact]
    public void The_record_holds_no_net_id_name_seed_or_gold()
    {
        var json = RunRecord.ToJson(RunRecord.Trim(SyntheticRun(), false, Me, Ctx));
        Assert.DoesNotContain(Me.ToString(), json);
        Assert.DoesNotContain(Partner.ToString(), json);
        foreach (var banned in new[] { "net_id", "player_id", "gold", "seed", "potion", "name" })
            Assert.DoesNotContain(banned, json);
    }

    [Fact]
    public void The_local_player_is_found_by_net_id_not_by_list_position()
    {
        var r = RunRecord.Trim(SyntheticRun(), false, Me, Ctx);
        Assert.Equal("CHARACTER.KLEEMOD-KLEE", (string)r["character"]!);
        Assert.Equal(new[] { "CHARACTER.IRONCLAD" },
            r["partners"]!.AsArray().Select(n => (string)n!).ToArray());
        Assert.True((bool)r["coop"]!);
        Assert.Equal(61, (int)r["floors"]![1]!["hp"]!);
        Assert.Equal(3, r["deck"]!.AsArray().Count);
    }

    [Fact]
    public void Killed_by_follows_the_games_run_history_rule()
    {
        var loss = RunRecord.Trim(SyntheticRun(), false, Me, Ctx);
        Assert.Equal("ENCOUNTER.THE_KIN_BOSS", (string)loss["killed_by_encounter"]!);
        Assert.Null(loss["killed_by_event"]);

        var eventDeath = RunRecord.Trim(
            SyntheticRun(RoomType.Event, new ModelId("EVENT", "TRIAL")), false, Me, Ctx);
        Assert.Null(eventDeath["killed_by_encounter"]);
        Assert.Equal("EVENT.TRIAL", (string)eventDeath["killed_by_event"]!);

        var win = RunRecord.Trim(SyntheticRun(), true, Me, Ctx);
        Assert.Null(win["killed_by_encounter"]);
        Assert.Null(win["killed_by_event"]);
        Assert.True((bool)win["victory"]!);
    }

    [Fact]
    public void A_solo_run_has_no_partners()
    {
        var run = SyntheticRun();
        run.Players.RemoveAll(p => p.NetId == Partner);
        var r = RunRecord.Trim(run, false, Me, Ctx);
        Assert.False((bool)r["coop"]!);
        Assert.Empty(r["partners"]!.AsArray());
    }

    [Theory]
    [InlineData("RestSite", "rest_site")]
    [InlineData("Monster", "monster")]
    [InlineData("Standard", "standard")]
    public void Enum_names_are_written_the_way_the_game_writes_them(string name, string want) =>
        Assert.Equal(want, RunRecord.Snake(name));

    [Fact]
    public void Uuids_are_version_4()
    {
        for (int i = 0; i < 200; i++) Assert.True(RunRecord.IsUuid4(RunRecord.NewUuid4()));
        Assert.False(RunRecord.IsUuid4(""));
        Assert.False(RunRecord.IsUuid4(null));
        Assert.False(RunRecord.IsUuid4("0b5e3c3e-6f1a-1d2b-9c4d-3a2f1e0d9c8b")); // version 1
    }

    [Theory]
    [InlineData("0.3.0+workshop.beta", "0.3.0")]
    [InlineData("0.3.0", "0.3.0")]
    [InlineData(null, "0.0.0")]
    [InlineData("", "0.0.0")]
    public void The_mod_version_is_the_plain_one(string informational, string want) =>
        Assert.Equal(want, WorkshopRelease.PlainVersion(informational));

    // --------------------------------------------------------- switches ---

    private const string Endpoint = "https://gits-telemetry.example.workers.dev/v1/run";

    [Theory]
    [InlineData(false, false)]
    [InlineData(true, false)]
    [InlineData(false, true)]
    public void Nothing_is_sent_or_made_unless_both_switches_are_on(bool game, bool mod)
    {
        int sent = 0, ids = 0;
        var json = RunStatsUpload.Handle(SyntheticRun(), false, Me, game, mod, Endpoint,
            installId: () => { ids++; return Ctx.InstallId; },
            "0.3.0", "beta", "v0.111.0", send: _ => sent++);
        Assert.Null(json);
        Assert.Equal(0, sent);
        Assert.Equal(0, ids); // no install id is made for a player who never opted in
    }

    [Fact]
    public void Nothing_is_sent_without_an_endpoint()
    {
        int sent = 0;
        Assert.Null(RunStatsUpload.Handle(SyntheticRun(), false, Me, true, true, "",
            () => Ctx.InstallId, "0.3.0", "beta", "v0.111.0", _ => sent++));
        Assert.Equal(0, sent);
    }

    [Fact]
    public void Both_switches_on_sends_one_record_with_a_fresh_run_uuid()
    {
        var sent = new List<string>();
        var json = RunStatsUpload.Handle(SyntheticRun(), false, Me, true, true, Endpoint,
            () => Ctx.InstallId, "0.3.0", "beta", "v0.111.0", sent.Add);
        Assert.NotNull(json);
        Assert.Single(sent);
        var r = JsonNode.Parse(sent[0])!;
        Assert.Equal(Ctx.InstallId, (string)r["install_id"]!);
        Assert.True(RunRecord.IsUuid4((string)r["run_uuid"]!));
        Assert.NotEqual(Ctx.RunUuid, (string)r["run_uuid"]!);
    }

    [Fact]
    public void A_failure_is_logged_and_dropped_never_thrown()
    {
        var logged = new List<string>();
        var json = RunStatsUpload.Handle(SyntheticRun(), false, Me, true, true, Endpoint,
            () => throw new InvalidOperationException("boom"), "0.3.0", "beta", "v0.111.0",
            _ => { }, logged.Add);
        Assert.Null(json);
        Assert.Single(logged);
        Assert.Null(RunStatsUpload.Handle(SyntheticRun(), false, Me, true, true, Endpoint,
            () => Ctx.InstallId, "0.3.0", "beta", "v0.111.0",
            _ => throw new InvalidOperationException("send"), null));
    }

    // ---------------------------------------------- the build has none ---

    [Fact]
    public void A_build_without_an_endpoint_has_no_uploader()
    {
        var mod = typeof(global::KleeMod.KleeMod).Assembly;
        Assert.DoesNotContain(mod.GetTypes(), t => t.Namespace == "KleeMod.RunStats");
        Assert.DoesNotContain(mod.GetCustomAttributes<AssemblyMetadataAttribute>(),
            a => a.Key == "GitsTelemetryEndpoint");
        Assert.DoesNotContain(Il.Calls(Il.Method("KleeMod", "Initialize")),
            c => c.Contains("RunStats"));
        Assert.DoesNotContain(Il.Calls(Il.Method("EnglishLoc", "RunInjectors")),
            c => c.Contains("RunStats"));
        // And the mod never touches the game's metrics hook outside that folder.
        Assert.DoesNotContain(mod.GetTypes().SelectMany(t =>
                t.GetMethods(BindingFlags.Static | BindingFlags.Instance | BindingFlags.Public
                             | BindingFlags.NonPublic | BindingFlags.DeclaredOnly)),
            m => m.Name.Contains("MetricsUpload"));
    }

    [Fact]
    public void A_dev_build_names_no_variant()
    {
        Assert.Null(WorkshopRelease.Variant);
    }
}
