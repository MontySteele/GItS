// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// THE SPIRAL ABYSS ON A SEAT LANE (2026-10-12, `understudy.embark --abyss`).
// Two reads the embark and the seat page need, both guarded: a state read
// must never throw (`GitsRefusalSource.cs`).
//
// 1. `run.modifiers`: the run's modifier ids (`ModelId.Entry`), on both the
//    singleplayer and the multiplayer state. The embark reads it back after
//    the run opens, so a lane asked for the Abyss that did not get it fails
//    `abyss_not_honoured` instead of playing a plain run labelled Abyss. An
//    ordinary run answers an empty list.
//
// 2. THE ABYSS PAGE'S BODY. `BuildEventState` reads `body` off the room's
//    CANONICAL event, which never has a page set, so every event answers
//    `body: null`. The Abyss choice page is put over the Ancient's opening
//    page on the player's MUTABLE copy (`KleeMod.Abyss.AbyssChoicePage`), and
//    its body is the one sentence that says what the three options are: take
//    one Blessing, the enemies take one of the two you pass. So where the
//    canonical body is empty and the local copy is showing a page from the
//    Abyss's own loc rows, that page's text is the body. NARROW ON PURPOSE:
//    every other event reads exactly as before.

using System;
using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;

namespace STS2_MCP;

public static partial class McpMod
{
    /// <summary>The loc-key prefix of the Abyss choice page's rows
    /// (`AbyssChoicePage.KeyPrefix`).</summary>
    internal const string GitsAbyssPagePrefix = "KLEE_SPIRAL_ABYSS";

    private static List<string> GitsRunModifierIds(RunState runState)
    {
        try
        {
            return (runState.Modifiers ?? Array.Empty<MegaCrit.Sts2.Core.Models.ModifierModel>())
                .Where(m => m != null)
                .Select(m => m.Id.Entry)
                .ToList();
        }
        catch (Exception)
        {
            return new List<string>();
        }
    }

    private static string? GitsAbyssPageBody(EventRoom eventRoom, string? canonicalBody)
    {
        if (!string.IsNullOrEmpty(canonicalBody)) return canonicalBody;
        try
        {
            var local = GitsLocalEvent.OrNothing(() => eventRoom.LocalMutableEvent);
            var page = local?.Description;
            if (page == null
                || !(page.LocEntryKey ?? "").StartsWith(GitsAbyssPagePrefix, StringComparison.Ordinal))
            {
                return canonicalBody;
            }
            return SafeGetText(() => page) ?? canonicalBody;
        }
        catch (Exception)
        {
            return canonicalBody;
        }
    }
}
