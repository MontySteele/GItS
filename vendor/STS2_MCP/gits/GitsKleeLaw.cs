// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// 2026-10-08. THE KLEE KIT'S TWO RATES, ON THE WIRE.
//
// THE GAP. The blind page quotes two of Klee's numbers in sentences of its
// own -- how much a Bomb grows each turn, and how many Sparks a fight opens
// with -- and read both off Python mirrors (`understudy/blindplay_shape.py`
// `BOMB_GROWTH`, `OPENING_SPARK`). Suite 5 ran the page from one checkout
// against a game built from another branch, and where no Bomb tip was on
// screen the page taught 4 and 1 while the build said 2 and 3.
//
// WHAT THIS READS. `KleeMod.Powers.KleeOverhaulLaw.BombGrowth` and
// `.OpeningSpark`, two `public const int` fields, by reflection for
// `GitsReactionLog.cs`'s reasons: the bridge cannot reference the klee
// assembly, and "no klee mod" must mean "no key". Probed once, cached
// including the null, and every failure swallowed, because a state read must
// never throw. Emitted under `run.klee_law` on every screen; an ABSENT key
// means "this bridge or this build cannot say", and the page then falls back
// to its mirrors.
//
// READ-ONLY. A const is read; nothing is set.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Godot;

namespace STS2_MCP;

public static partial class McpMod
{
    private const string GitsKleeLawType = "KleeMod.Powers.KleeOverhaulLaw";

    private static bool _gitsKleeLawProbed;
    private static Dictionary<string, object?>? _gitsKleeLaw;

    /// <summary>
    /// `{ bomb_growth, opening_spark }` off the loaded klee mod's
    /// <c>KleeOverhaulLaw</c>, or null where the type or a field is missing.
    /// The values are compile-time constants, so one read serves the process.
    /// </summary>
    internal static Dictionary<string, object?>? GitsKleeLawState()
    {
        if (_gitsKleeLawProbed) return _gitsKleeLaw;
        _gitsKleeLawProbed = true;
        try
        {
            var type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(a =>
                {
                    try { return a.GetType(GitsKleeLawType, false); }
                    catch { return null; }
                })
                .FirstOrDefault(t => t != null);
            if (type == null) return null;
            var growth = GitsConstInt(type, "BombGrowth");
            var opening = GitsConstInt(type, "OpeningSpark");
            if (growth == null || opening == null) return null;
            _gitsKleeLaw = new Dictionary<string, object?>
            {
                ["bomb_growth"] = growth.Value,
                ["opening_spark"] = opening.Value,
            };
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] klee law probe failed: {ex.Message}");
            _gitsKleeLaw = null;
        }
        return _gitsKleeLaw;
    }

    private static int? GitsConstInt(Type type, string name)
    {
        var field = type.GetField(name, BindingFlags.Public | BindingFlags.Static);
        if (field == null) return null;
        var value = field.IsLiteral ? field.GetRawConstantValue() : field.GetValue(null);
        return value is int n ? n : null;
    }
}
