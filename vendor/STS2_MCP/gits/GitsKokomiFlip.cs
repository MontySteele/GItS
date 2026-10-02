// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// Kokomi, a Plan stays open, pick 5 (a) (2026-10-01): "Plans carry out on
// their Plan line; click a waiting Plan to flip it." A player flips a waiting
// two-line Plan by clicking its picture in the Plan strip; this is the same
// click for a seat, as the action `kokomi_flip_plan` with the Plan's queue
// position `index` (front = 0).
//
// REFLECTION, for `GitsKokomiPlan.cs`'s reason: the rule lives in the klee
// mod, and a compile-time reference would make this bridge refuse to load
// without it. The method is `KleeMod.Powers.KokomiPlan.RequestFlip(Player,
// int)`, which returns null when the flip was sent through the game's action
// queue and a plain-words refusal otherwise. No klee mod means "no Plan to
// flip", which is the truth.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using Godot;
using MegaCrit.Sts2.Core.Entities.Players;

namespace STS2_MCP;

public static partial class McpMod
{
    private const string GitsKokomiFlipMethod = "RequestFlip";

    private static bool _gitsFlipProbed;
    private static MethodInfo? _gitsFlip;

    private static MethodInfo? GitsKokomiFlip()
    {
        if (_gitsFlipProbed) return _gitsFlip;
        _gitsFlipProbed = true;
        try
        {
            var type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(a =>
                {
                    try { return a.GetType(GitsKokomiPlanType, false); }
                    catch { return null; }
                })
                .FirstOrDefault(t => t != null);
            _gitsFlip = type?.GetMethod(
                GitsKokomiFlipMethod,
                BindingFlags.Static | BindingFlags.Public);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] kokomi flip probe failed: {ex.Message}");
            _gitsFlip = null;
        }
        return _gitsFlip;
    }

    /// <summary>`kokomi_flip_plan`: flip the waiting Plan at `index`.</summary>
    private static Dictionary<string, object?> ExecuteGitsKokomiFlipPlan(
        Player player, Dictionary<string, JsonElement> data)
    {
        if (!data.TryGetValue("index", out var indexElem))
            return Error("Missing 'index'");
        var method = GitsKokomiFlip();
        if (method == null)
            return Error("there is no Plan to flip in this build");
        int index = indexElem.GetInt32();
        try
        {
            var why = method.Invoke(null, new object?[] { player, index })
                      as string;
            if (why != null) return Error(why);
        }
        catch (Exception ex)
        {
            return Error($"flip failed: {ex.InnerException?.Message ?? ex.Message}");
        }
        return new Dictionary<string, object?>
        {
            ["status"] = "ok",
            ["message"] = $"Flipped waiting Plan {index + 1}",
        };
    }
}
