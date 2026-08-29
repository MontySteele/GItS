// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// EB-181, the Kokomi half. THE GAP, EXACTLY: the bridge serialises
// `creature.Powers` and (since P1.5) BaseLib's registered custom resources, so
// a meter is on the wire as an ID and an AMOUNT and nothing else. Under the
// Kurage's memory rule (review/active/kokomi-kurage-memory-2026-08-29.md
// sec.11) that is no longer enough to play the character at all:
//
//   * Charge stops being a bank with no ceiling and starts having a target --
//     the FRONT MEMORY'S OWN PRICE -- and "a meter has no maximum" is exactly
//     EB-181's second half;
//   * the QUEUE is a list of cards with a price and a stored target each, and
//     nothing on the wire carries it;
//   * the jellyfish's PULSE is keyed to the type of the last card she played,
//     so a seat that cannot read it cannot forecast the end of its own turn.
//
// A seat that cannot read the queue cannot play her. D4, in the proposal's own
// words: everything that will fire next turn must be readable this turn.
//
// WHAT THIS READS, AND WHY IT IS REFLECTION. The rule is QUARANTINED inside the
// klee mod (`Powers/Prototype/KurageMemory.cs`, compiled only under
// -p:PrototypeCards=true), so:
//
//   * a compile-time reference would make this bridge refuse to load without
//     the klee mod installed, and would not compile at all against a RELEASE
//     klee.dll, which does not contain the type;
//   * reflection makes "no klee mod, or a release klee.dll" mean "no memory",
//     which is the truth.
//
// That is the same posture GitsResources.cs takes toward BaseLib, for the same
// reason, and the failure mode is the same: every lookup is cached after the
// first attempt and every failure is swallowed into an EMPTY map, because a
// state read must never throw.
//
// THE CONTRACT. `KleeMod.Powers.KurageMemory.Snapshot(Player)` returns a plain
// Dictionary<string, object?> of primitives; this file invokes it and hands the
// result straight to the wire under `player.kurage_memory`. The field names are
// the mod's, are documented on that method, and are read by
// `understudy/blindplay.py`. An ABSENT key means "no memory rule in this
// build"; an EMPTY map means "the rule is here and this player is not Kokomi".
// Those are different facts and a reader is entitled to tell them apart.
//
// READ-ONLY. Nothing here mutates a queue, a bank or a card. It is a
// serialiser.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Godot;

namespace STS2_MCP;

public static partial class McpMod
{
    private const string GitsKurageMemoryType = "KleeMod.Powers.KurageMemory";
    private const string GitsKurageMemoryMethod = "Snapshot";

    private static bool _gitsKurageProbed;
    private static MethodInfo? _gitsKurageSnapshot;

    /// <summary>
    /// Locate the mod's snapshot method once. A null result is cached too: a
    /// release klee.dll does not contain the type and never will mid-session,
    /// and a state read should not pay for a full assembly walk on every poll.
    /// </summary>
    private static MethodInfo? GitsKurageSnapshot()
    {
        if (_gitsKurageProbed) return _gitsKurageSnapshot;
        _gitsKurageProbed = true;
        try
        {
            var type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(a =>
                {
                    try { return a.GetType(GitsKurageMemoryType, false); }
                    catch { return null; }
                })
                .FirstOrDefault(t => t != null);
            _gitsKurageSnapshot = type?.GetMethod(
                GitsKurageMemoryMethod,
                BindingFlags.Static | BindingFlags.Public);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] kurage memory probe failed: {ex.Message}");
            _gitsKurageSnapshot = null;
        }
        return _gitsKurageSnapshot;
    }

    /// <summary>
    /// The Kurage's memory for one player, or NULL when this build has no
    /// memory rule in it. Null is what keeps the wire key ABSENT rather than
    /// present-and-empty, which is the distinction the header names.
    /// </summary>
    internal static Dictionary<string, object?>? GitsKurageMemorySnapshot(
        object? player)
    {
        if (player == null) return null;
        var snapshot = GitsKurageSnapshot();
        if (snapshot == null) return null;
        try
        {
            return snapshot.Invoke(null, new[] { player })
                   as Dictionary<string, object?>;
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] kurage memory snapshot failed: "
                        + $"{ex.Message}");
            return null;
        }
    }
}
