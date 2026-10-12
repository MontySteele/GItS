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
// 2. THE ABYSS PAGE'S BODY is no longer read here: every event's body is now
//    the page on the player's local copy (`gits/GitsEventPage.cs`), and the
//    Abyss choice page (`KleeMod.Abyss.AbyssChoicePage`) is set on that copy,
//    so its sentence comes through the general read.

using System;
using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Runs;

namespace STS2_MCP;

public static partial class McpMod
{
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
}
