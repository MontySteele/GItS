// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// THE SPIRAL ABYSS BLESSING SCREEN ON THE WIRE (2026-10-12): the node-reading
// half of `gits/GitsAbyssPage.cs`.
//
//   READ. `BuildEventState` ends by asking `GitsApplyAbyssScreen`: while the
//   klee mod's overlay root sits under the event room, the event is that page
//   (title "The Spiral Abyss", the whisper line, three options whose title is
//   the Blessing and whose description is its text and "If passed: Shadow -
//   text"), `in_dialogue` is false, and `abyss_screen` carries the act title,
//   the strip and, once the pick lands, the result line. When the overlay is
//   gone the room is the ordinary Ancient page again.
//
//   CHOOSE. `ExecuteChooseEventOption` asks `GitsChooseAbyssCard` first: card
//   i's clickable is a game `NClickableControl`, and `ForceClick` emits the
//   `Released` signal a mouse release emits, so the pick runs the same handler
//   a click does (which calls `NEventRoom.OptionButtonClicked`, the call the
//   page's own option button makes). While the screen shows its result and
//   fades, a choice is refused rather than landing on the Ancient's options
//   underneath.
//
// Reads names and meta only; references no klee type. Every failure answers
// "no overlay", and the room reads as before.

using System;
using System.Collections.Generic;
using Godot;
using MegaCrit.Sts2.Core.Nodes.GodotExtensions;

namespace STS2_MCP;

public static partial class McpMod
{
    private static Control? GitsAbyssOverlayRoot(Node? room)
    {
        try
        {
            if (room == null) return null;
            var root = room.GetNodeOrNull<Control>(GitsAbyssPage.RootName);
            if (root == null || !GodotObject.IsInstanceValid(root) || root.IsQueuedForDeletion()) return null;
            return root.HasMeta(GitsAbyssPage.MetaKey) ? root : null;
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static string? GitsAbyssPageJson(Control root)
    {
        try
        {
            return root.GetMeta(GitsAbyssPage.MetaKey).AsString();
        }
        catch (Exception)
        {
            return null;
        }
    }

    /// <summary>The event state, as the Blessing screen when it is up.</summary>
    private static void GitsApplyAbyssScreen(Dictionary<string, object?> state, Node? uiRoom)
    {
        var root = GitsAbyssOverlayRoot(uiRoom);
        var json = root == null ? null : GitsAbyssPageJson(root);
        if (json != null) GitsAbyssPage.Apply(state, json);
    }

    /// <summary>A choice while the Blessing screen is up, or null when it is
    /// not (the room's own option buttons then take it).</summary>
    private static Dictionary<string, object?>? GitsChooseAbyssCard(Node uiRoom, int index)
    {
        var root = GitsAbyssOverlayRoot(uiRoom);
        if (root == null) return null;
        var json = GitsAbyssPageJson(root);
        if (json == null || !GitsAbyssPage.IsOpen(json))
            return Error("The Spiral Abyss Blessing screen is closing - wait for the Ancient's page");
        var card = root.FindChild(GitsAbyssPage.CardNodeName(index), true, false) as NClickableControl;
        if (card == null)
            return Error($"Blessing index {index} out of range");
        var state = new Dictionary<string, object?>();
        GitsAbyssPage.Apply(state, json);
        string title = "Blessing";
        if (state["options"] is List<Dictionary<string, object?>> options && index >= 0 && index < options.Count)
            title = options[index]["title"] as string ?? title;
        card.ForceClick();
        return new Dictionary<string, object?>
        {
            ["status"] = "ok",
            ["message"] = $"Choosing Blessing: {title}"
        };
    }
}
