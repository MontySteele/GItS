// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// YAE: A COUNT THE RULE KEEPS AND THE BOARD DOES NOT SHOW. Bestseller and
// Print Run (Yae review r5, pick 1 (a)) scale with "each card you Edited this
// combat", and nothing on the board carries that number: an Edit leaves an
// enchantment on a card, and the card may since have been played, discarded
// or exhausted. The mod keeps it (`YaeShrineLedger.Edits`); this file is the
// read, so a blind seat's page can print "Cards Edited this combat: N".
//
// WHY IT IS REFLECTION -- the same posture and reasons as
// `GitsFurinaStage.cs`: a compile-time reference would make this bridge
// refuse to load without the klee mod. Probed once, the null cached with the
// hit, every failure swallowed -- a state read must never throw.
//
// THE CONTRACT. `KleeMod.Powers.YaeShrine.Snapshot(Player)` returns a
// Dictionary<string, object?> of primitives (`live`, `edits_this_combat`, and
// `sakura`: one `{slot, annotations}` row per Sakura, oldest first, each
// Annotation named in the order applied), handed straight to the wire under
// `player.yae_shrine`. ABSENT means "no Yae
// in this build"; EMPTY means "not Yae, or not in a fight".
//
// READ-ONLY.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Godot;

namespace STS2_MCP;

public static partial class McpMod
{
    private const string GitsYaeShrineType = "KleeMod.Powers.YaeShrine";
    private const string GitsYaeShrineMethod = "Snapshot";

    private static bool _gitsYaeShrineProbed;
    private static MethodInfo? _gitsYaeShrineSnapshot;

    private static MethodInfo? GitsYaeShrineSnapshot()
    {
        if (_gitsYaeShrineProbed) return _gitsYaeShrineSnapshot;
        _gitsYaeShrineProbed = true;
        try
        {
            var type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(a =>
                {
                    try { return a.GetType(GitsYaeShrineType, false); }
                    catch { return null; }
                })
                .FirstOrDefault(t => t != null);
            _gitsYaeShrineSnapshot = type?.GetMethod(
                GitsYaeShrineMethod,
                BindingFlags.Static | BindingFlags.Public);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] yae shrine probe failed: {ex.Message}");
            _gitsYaeShrineSnapshot = null;
        }
        return _gitsYaeShrineSnapshot;
    }

    /// <summary>The shrine's counts for one player, or NULL when this build
    /// has no Yae in it (the wire key stays absent).</summary>
    internal static Dictionary<string, object?>? GitsYaeShrineState(
        object? player)
    {
        if (player == null) return null;
        var snapshot = GitsYaeShrineSnapshot();
        if (snapshot == null) return null;
        try
        {
            return snapshot.Invoke(null, new[] { player })
                   as Dictionary<string, object?>;
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] yae shrine snapshot failed: "
                        + $"{ex.Message}");
            return null;
        }
    }
}
