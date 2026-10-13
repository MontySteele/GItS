// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// THE SPIRAL ABYSS BLESSING SCREEN AS A PAGE (2026-10-12). The klee mod draws
// the Abyss pick as its own full-screen modal over the Ancient's room
// (`KleeMod.Abyss.AbyssOverlay`) and hides the Ancient's layout while it is
// up. The root node carries the page as JSON under the meta key
// `gits_abyss_page`; this file turns that JSON into the wire's event shape.
//
// NAMES NO GODOT, HARMONY OR GAME TYPE, so `KleeTests` compiles it beside the
// mod and pins the round trip: the mod's page in, the wire's options out
// (`gits/GitsAbyssOverlay.cs` is the node-reading half).

using System;
using System.Collections.Generic;
using System.Text.Json;

namespace STS2_MCP;

public static class GitsAbyssPage
{
    /// <summary>The overlay root's node name (the mod's
    /// <c>AbyssOverlayView.RootName</c>).</summary>
    public const string RootName = "KleeModAbyssBlessingOverlay";

    /// <summary>The meta key holding the page JSON (the mod's
    /// <c>AbyssOverlay.PageMeta</c>).</summary>
    public const string MetaKey = "gits_abyss_page";

    /// <summary>Card i's clickable (the mod's
    /// <c>AbyssOverlayView.CardNodeName</c>).</summary>
    public static string CardNodeName(int index) => $"AbyssCard{index}";

    /// <summary>
    /// Put the screen over an event state already built from the room: the
    /// page's title, body and options replace the hidden Ancient's, the
    /// dialogue is not in progress, and `abyss_screen` says what else is on
    /// the screen. Returns false (and touches nothing) for JSON it cannot read.
    /// </summary>
    public static bool Apply(Dictionary<string, object?> state, string json)
    {
        JsonElement page;
        try
        {
            page = JsonDocument.Parse(json).RootElement;
            if (page.ValueKind != JsonValueKind.Object) return false;
        }
        catch (Exception)
        {
            return false;
        }

        var options = new List<Dictionary<string, object?>>();
        if (page.TryGetProperty("options", out var opts) && opts.ValueKind == JsonValueKind.Array)
        {
            foreach (var o in opts.EnumerateArray())
            {
                options.Add(new Dictionary<string, object?>
                {
                    ["index"] = Int(o, "index") ?? options.Count,
                    ["title"] = Str(o, "title"),
                    ["description"] = Str(o, "description"),
                    ["is_locked"] = false,
                    ["is_proceed"] = false,
                    ["was_chosen"] = false,
                    ["keywords"] = new List<Dictionary<string, object?>>(),
                });
            }
        }

        state["event_name"] = Str(page, "title");
        state["body"] = Str(page, "body");
        state["in_dialogue"] = false;
        state["options"] = options;
        state["abyss_screen"] = new Dictionary<string, object?>
        {
            ["subtitle"] = Str(page, "subtitle"),
            ["resolved"] = page.TryGetProperty("resolved", out var r) && r.ValueKind == JsonValueKind.True,
            ["chosen"] = Str(page, "chosen"),
            ["result"] = Str(page, "result"),
            ["blessings_taken"] = Strings(page, "blessings_taken"),
            ["shadows_in_force"] = Strings(page, "shadows_in_force"),
        };
        return true;
    }

    /// <summary>Is the page still taking a pick?</summary>
    public static bool IsOpen(string json)
    {
        try
        {
            var page = JsonDocument.Parse(json).RootElement;
            return !(page.TryGetProperty("resolved", out var r) && r.ValueKind == JsonValueKind.True);
        }
        catch (Exception)
        {
            return false;
        }
    }

    private static string? Str(JsonElement e, string key) =>
        e.TryGetProperty(key, out var v) && v.ValueKind == JsonValueKind.String ? v.GetString() : null;

    private static int? Int(JsonElement e, string key) =>
        e.TryGetProperty(key, out var v) && v.ValueKind == JsonValueKind.Number ? v.GetInt32() : null;

    private static List<string> Strings(JsonElement e, string key)
    {
        var list = new List<string>();
        if (e.TryGetProperty(key, out var v) && v.ValueKind == JsonValueKind.Array)
        {
            foreach (var s in v.EnumerateArray())
            {
                if (s.ValueKind == JsonValueKind.String) list.Add(s.GetString()!);
            }
        }
        return list;
    }
}
