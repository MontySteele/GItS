// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// THE SPIRAL ABYSS SEAT ROUND (2026-10-12): WHAT A CO-OP VOTE OR BID ACTUALLY
// GAVE. Two finds, one cause: the wire showed votes while they were open and
// nothing once they resolved.
//
//   A SHARED EVENT'S VOTE. "I chose Crystallize but got First Strike." The
//   party votes one option; when the votes differ the host draws one of them
//   at random (`EventSynchronizer.ChooseSharedEventOption`,
//   `_multiplayerOptionSelectionRng.NextItem(_playerVotes)`, 0.111.0
//   decompile). `ChooseOptionForSharedEvent` then clears the votes and runs
//   the option on every copy, so the next read had no votes and no result.
//
//   A CO-OP CHEST IS A BID. "Took: Tungsten Rod" and Lasting Candy arrived.
//   `TreasureRoomRelicSynchronizer.AwardRelics` gives a relic one player bid
//   on to that player, settles a relic two bid on by a random fight, and hands
//   the loser a relic nobody bid on; `RelicsAwarded` carries the results and
//   `EndRelicVoting` then nulls the relics, so the bids left the wire too.
//
// WHAT CROSSES. `event.last_vote` -- the options' titles each player voted
// for, the title the party got, and whether the votes split -- and
// `treasure.relic_results` -- per player, the relic bid on and the relic
// received. Each is kept for the room it happened in and served only while
// that room is the current one, so a later room never prints a stale result.
//
// THE CLIENT'S PARTNER VOTE. On the client the host's own vote message can
// arrive after the result (the host builds it after its page index moved on),
// so at resolution the client may know only its own vote. With two players
// the result is one of the two votes, so a client whose vote lost knows the
// partner's: it is the result, and the row is marked `inferred`.
//
// READ-ONLY toward the game: a Harmony prefix that reads the votes before the
// game clears them, and a subscriber to the synchronizer's own public event.
// Every failure is swallowed; a state read must never throw.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.TreasureRelicPicking;
using MegaCrit.Sts2.Core.Multiplayer.Game;
using MegaCrit.Sts2.Core.Runs;

namespace STS2_MCP;

public static partial class McpMod
{
    private sealed class GitsRoomOutcome
    {
        public WeakReference Room = new(null);
        public Dictionary<string, object?> Payload = new();
    }

    private static GitsRoomOutcome? _gitsLastSharedVote;
    private static GitsRoomOutcome? _gitsLastRelicAward;

    private static bool IsCurrentRoom(GitsRoomOutcome? outcome, object? room) =>
        outcome != null && room != null && ReferenceEquals(outcome.Room.Target, room);

    /// <summary>The last shared vote's result, while its room is current.</summary>
    internal static Dictionary<string, object?>? GitsLastSharedVoteFor(object? room) =>
        IsCurrentRoom(_gitsLastSharedVote, room) ? _gitsLastSharedVote!.Payload : null;

    /// <summary>The last chest's awards, while its room is current.</summary>
    internal static Dictionary<string, object?>? GitsLastRelicAwardFor(object? room) =>
        IsCurrentRoom(_gitsLastRelicAward, room) ? _gitsLastRelicAward!.Payload : null;

    internal static void GitsRecordSharedVote(EventSynchronizer sync, uint chosen)
    {
        try
        {
            var runState = RunManager.Instance.DebugOnlyGetState();
            if (runState == null) return;
            var local = sync.GetLocalEvent();
            string? Title(int index)
            {
                var options = local?.CurrentOptions;
                if (options == null || index < 0 || index >= options.Count) return null;
                return SafeGetText(() => options[index].Title);
            }

            var rows = new List<Dictionary<string, object?>>();
            foreach (var player in runState.Players)
            {
                uint? vote = null;
                try { vote = sync.GetPlayerVote(player); } catch { /* slot gone */ }
                rows.Add(new Dictionary<string, object?>
                {
                    ["player"] = SafeGetText(() => player.Character.Title),
                    ["is_local"] = LocalContext.IsMe(player),
                    ["vote_option"] = vote.HasValue ? (int)vote.Value : null,
                    ["choice"] = vote.HasValue ? Title((int)vote.Value) : null,
                    ["inferred"] = false,
                });
            }

            // Two players: the result is one of the two votes. A vote this
            // machine never received is the result whenever the known vote
            // lost (see the header).
            if (rows.Count == 2)
            {
                var known = rows.Where(r => r["vote_option"] != null).ToList();
                if (known.Count == 1 && (int)known[0]["vote_option"]! != (int)chosen)
                {
                    var other = rows.First(r => r["vote_option"] == null);
                    other["vote_option"] = (int)chosen;
                    other["choice"] = Title((int)chosen);
                    other["inferred"] = true;
                }
            }

            var distinct = rows.Where(r => r["vote_option"] != null)
                .Select(r => (int)r["vote_option"]!).Distinct().Count();
            _gitsLastSharedVote = new GitsRoomOutcome
            {
                Room = new WeakReference(runState.CurrentRoom),
                Payload = new Dictionary<string, object?>
                {
                    ["chosen_option"] = (int)chosen,
                    ["chosen"] = Title((int)chosen),
                    ["split"] = distinct > 1,
                    ["votes"] = rows,
                },
            };
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] shared vote record failed: {ex.Message}");
        }
    }

    private static readonly ConditionalWeakTable<TreasureRoomRelicSynchronizer, object> _gitsAwardHooked = new();

    internal static void GitsHookRelicAwards(TreasureRoomRelicSynchronizer sync)
    {
        try
        {
            if (_gitsAwardHooked.TryGetValue(sync, out _)) return;
            _gitsAwardHooked.Add(sync, new object());
            sync.RelicsAwarded += results => GitsRecordRelicAward(sync, results);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] relic award hook failed: {ex.Message}");
        }
    }

    private static void GitsRecordRelicAward(
        TreasureRoomRelicSynchronizer sync, List<RelicPickingResult> results)
    {
        try
        {
            var runState = RunManager.Instance.DebugOnlyGetState();
            if (runState == null || runState.Players.Count < 2) return;
            var relics = sync.CurrentRelics;
            var rows = new List<Dictionary<string, object?>>();
            foreach (var player in runState.Players)
            {
                int? bid = null;
                bool skipped = false;
                try
                {
                    var vote = sync.GetPlayerVote(player);
                    bid = vote?.index;
                    skipped = vote != null && vote.voteReceived && !vote.index.HasValue;
                }
                catch { /* slot gone */ }
                var got = results.FirstOrDefault(r => r.player == player);
                rows.Add(new Dictionary<string, object?>
                {
                    ["player"] = SafeGetText(() => player.Character.Title),
                    ["is_local"] = LocalContext.IsMe(player),
                    ["bid"] = bid.HasValue && relics != null && bid.Value < relics.Count
                        ? SafeGetText(() => relics[bid.Value].Title) : null,
                    ["skipped"] = skipped,
                    ["received"] = got != null ? SafeGetText(() => got.relic.Title) : null,
                    // OnlyOnePlayerVoted, FoughtOver (won a contested bid),
                    // ConsolationPrize (lost one), or null for nothing.
                    ["how"] = got?.type.ToString(),
                });
            }
            _gitsLastRelicAward = new GitsRoomOutcome
            {
                Room = new WeakReference(runState.CurrentRoom),
                Payload = new Dictionary<string, object?> { ["players"] = rows },
            };
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] relic award record failed: {ex.Message}");
        }
    }
}

/// <summary>Reads the votes the moment before the game clears them. Runs on
/// the host and on every client (both reach this private method).</summary>
[HarmonyPatch(typeof(EventSynchronizer), "ChooseOptionForSharedEvent")]
internal static class GitsSharedVotePatch
{
    [HarmonyPrefix]
    private static void Prefix(EventSynchronizer __instance, uint optionIndex)
    {
        McpMod.GitsRecordSharedVote(__instance, optionIndex);
    }
}

/// <summary>Subscribes to the chest's own award event when a chest opens.</summary>
[HarmonyPatch(typeof(TreasureRoomRelicSynchronizer), nameof(TreasureRoomRelicSynchronizer.BeginRelicPicking))]
internal static class GitsRelicAwardPatch
{
    [HarmonyPrefix]
    private static void Prefix(TreasureRoomRelicSynchronizer __instance)
    {
        McpMod.GitsHookRelicAwards(__instance);
    }
}
