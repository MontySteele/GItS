#nullable enable
using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json.Nodes;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Runs.History;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Saves.Runs;

namespace KleeMod.RunStats;

/// <summary>What the record carries that the run does not: ours, not the game's.</summary>
public sealed record RunRecordContext(
    string RunUuid, string InstallId, string ModVersion, string Variant, string BuildId);

/// <summary>
/// ONE FINISHED RUN, TRIMMED TO SCHEMA V1 (<c>telemetry-worker/schema/run-v1.json</c>).
///
/// Reads the <see cref="SerializableRun"/> the game hands
/// <c>ModManager.OnMetricsUpload</c> and keeps game ids and numbers only. It
/// never reads a player's net id into the record (the local player's id is
/// used to FIND that player's rows and is then dropped), never a name, the
/// seed, gold or potions. The killed-by rule is the game's own
/// (<c>RunHistoryUtilities.CreateRunHistoryEntry</c>): on a loss, the last
/// room's model id, as an encounter when it was a fight and as an event when
/// it was an event.
///
/// Ported from the scratch trimmer that was checked against the 186 finished
/// runs in the dev history; it read the saved .run file, this reads the live
/// object the .run file is written from. PURE: no game state, no clock, no
/// file. <c>KleeTests/RunStatsTests.cs</c> pins it against a synthetic run,
/// and <c>tier0/tests/test_run_stats_record.py</c> validates the pinned output
/// against the schema.
///
/// Compiled into the mod only in a build with a telemetry endpoint
/// (<c>-p:GitsTelemetryEndpoint</c>); the test project compiles it directly.
/// </summary>
public static class RunRecord
{
    public static JsonObject Trim(SerializableRun run, bool isVictory, ulong localPlayerId,
                                  RunRecordContext ctx)
    {
        var players = run.Players ?? new List<SerializablePlayer>();
        var me = players.FirstOrDefault(p => p.NetId == localPlayerId) ?? players.FirstOrDefault();
        var myId = me?.NetId ?? localPlayerId;

        var floors = new JsonArray();
        var ancients = new JsonArray();
        var history = run.MapPointHistory ?? new List<List<MapPointHistoryEntry>>();
        int n = 0;
        for (int ai = 0; ai < history.Count; ai++)
        {
            foreach (var mp in history[ai] ?? new List<MapPointHistoryEntry>())
            {
                n++;
                var stats = mp.PlayerStats ?? new List<PlayerMapPointHistoryEntry>();
                var ps = stats.FirstOrDefault(p => p.PlayerId == myId) ?? stats.FirstOrDefault();
                var rooms = mp.Rooms ?? new List<MapPointRoomHistoryEntry>();
                var f = new JsonObject
                {
                    ["floor"] = n,
                    ["act"] = ai + 1,
                    ["type"] = Snake(mp.MapPointType.ToString()),
                    ["room"] = rooms.Count > 0 ? Id(rooms[^1].ModelId) : null,
                    ["hp"] = Math.Max(0, ps?.CurrentHp ?? 0),
                    ["max_hp"] = Math.Max(0, ps?.MaxHp ?? 0),
                    ["damage_taken"] = Math.Max(0, ps?.DamageTaken ?? 0),
                };
                var cc = (ps?.CardChoices ?? new List<CardChoiceHistoryEntry>())
                    .Where(c => Id(c.Card?.Id) != null).ToList();
                if (cc.Count > 0)
                {
                    f["card_choice"] = new JsonObject
                    {
                        ["offered"] = Ids(cc.Select(c => Id(c.Card.Id))),
                        ["picked"] = Ids(cc.Where(c => c.wasPicked).Select(c => Id(c.Card.Id))),
                    };
                }
                floors.Add(f);

                var ac = (ps?.AncientChoices ?? new List<AncientChoiceHistoryEntry>())
                    .Select(a => (key: TextKey(a), chosen: a.WasChosen))
                    .Where(a => a.key != null).ToList();
                if (ac.Count > 0)
                {
                    ancients.Add(new JsonObject
                    {
                        ["floor"] = n,
                        ["offered"] = Ids(ac.Select(a => a.key)),
                        ["picked"] = ac.Where(a => a.chosen).Select(a => a.key).FirstOrDefault(),
                    });
                }
            }
        }

        string? killedByEncounter = null, killedByEvent = null;
        var last = history.LastOrDefault()?.LastOrDefault();
        if (!isVictory && last?.Rooms is { Count: > 0 } lastRooms)
        {
            var room = lastRooms[^1];
            if (room.RoomType.IsCombatRoom()) killedByEncounter = Id(room.ModelId);
            else if (room.RoomType == RoomType.Event) killedByEvent = Id(room.ModelId);
        }

        return new JsonObject
        {
            ["schema_version"] = 1, // run-v1.json's const
            ["run_uuid"] = ctx.RunUuid,
            ["install_id"] = ctx.InstallId,
            ["mod_version"] = ctx.ModVersion,
            ["variant"] = ctx.Variant,
            ["build_id"] = ctx.BuildId,
            ["character"] = Id(me?.CharacterId) ?? "CHARACTER.UNKNOWN",
            ["ascension"] = run.Ascension,
            ["game_mode"] = Snake(run.GameMode.ToString()),
            ["coop"] = players.Count > 1,
            ["partners"] = Ids(players.Where(p => !ReferenceEquals(p, me))
                                      .Select(p => Id(p.CharacterId) ?? "CHARACTER.UNKNOWN")),
            ["victory"] = isVictory,
            ["floor_reached"] = n,
            ["act_reached"] = history.Count,
            ["acts"] = Ids((run.Acts ?? new List<SerializableActModel>()).Select(a => Id(a.Id))),
            ["killed_by_encounter"] = killedByEncounter,
            ["killed_by_event"] = killedByEvent,
            ["run_time_s"] = Math.Max(0L, run.WinTime > 0 ? run.WinTime : run.RunTime),
            ["deck"] = new JsonArray((me?.Deck ?? new List<SerializableCard>())
                .Where(c => Id(c.Id) != null)
                .Select(c => (JsonNode)new JsonObject
                {
                    ["id"] = Id(c.Id),
                    ["upgrades"] = Math.Max(0, c.CurrentUpgradeLevel),
                }).ToArray()),
            ["relics"] = Ids((me?.Relics ?? new List<SerializableRelic>()).Select(r => Id(r.Id))),
            ["floors"] = floors,
            ["ancients"] = ancients,
        };
    }

    /// <summary>The compact wire form.</summary>
    public static string ToJson(JsonObject record) => record.ToJsonString();

    /// <summary>A model id as the record writes it; null for none.</summary>
    internal static string? Id(ModelId? id)
    {
        if (id == null || id == ModelId.none) return null;
        var s = id.ToString();
        return string.IsNullOrEmpty(s) || s == "NONE.NONE" ? null : s;
    }

    private static JsonArray Ids(IEnumerable<string?> ids) =>
        new JsonArray(ids.Where(s => s != null).Select(s => (JsonNode)JsonValue.Create(s)!).ToArray());

    /// <summary>The Ancient option's key, as the run history's TextKey reads it.</summary>
    private static string? TextKey(AncientChoiceHistoryEntry a)
    {
        try { return string.IsNullOrEmpty(a.TextKey) ? null : a.TextKey; }
        catch { return null; }
    }

    /// <summary>PURE: "RestSite" -> "rest_site", as the game's JSON names its enums.</summary>
    public static string Snake(string name)
    {
        var sb = new StringBuilder(name.Length + 4);
        for (int i = 0; i < name.Length; i++)
        {
            var c = name[i];
            if (char.IsUpper(c) && i > 0) sb.Append('_');
            sb.Append(char.ToLowerInvariant(c));
        }
        return sb.ToString();
    }

    /// <summary>A random UUID, version 4, lower case (RFC 9562 sec.5.4).</summary>
    public static string NewUuid4()
    {
        var b = RandomNumberGenerator.GetBytes(16);
        b[6] = (byte)((b[6] & 0x0F) | 0x40);
        b[8] = (byte)((b[8] & 0x3F) | 0x80);
        var hex = Convert.ToHexString(b).ToLowerInvariant();
        return $"{hex[..8]}-{hex[8..12]}-{hex[12..16]}-{hex[16..20]}-{hex[20..]}";
    }

    /// <summary>PURE: does this string have the schema's uuid4 shape?</summary>
    public static bool IsUuid4(string? s) =>
        s != null && System.Text.RegularExpressions.Regex.IsMatch(s,
            "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$");
}
