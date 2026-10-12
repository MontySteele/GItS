// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// THE EVENT PAGE'S BODY, READ OFF THE MODEL THE ROOM SHOWS (2026-10-12).
// Why, and the plain-text rules: `gits/GitsEventBody.cs`.
//
// `NEventRoom.SetDescription` (decompiled) is the read copied here:
//
//     if (description.Exists())
//     {
//         _event.Owner.Character.AddDetailsTo(description);
//         description.Add("IsMultiplayer", _event.Owner.RunState.Players.Count > 1);
//         _event.DynamicVars.AddTo(description);
//         Layout.SetDescription(description.GetFormattedText());
//     }
//
// Adding the same variables again sets the same keys to the same values, so
// the page the player sees is untouched. The local copy is the player's page
// (the Spiral Abyss choice page included, `KleeMod.Abyss.AbyssChoicePage`);
// the canonical event is the fallback the rest of `BuildEventState` reads.

using System;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Rooms;

namespace STS2_MCP;

public static partial class McpMod
{
    private static string? GitsEventPageBody(EventRoom eventRoom, EventModel canonical)
    {
        return GitsEventBody.Choose(
            () => GitsFormattedPage(GitsLocalEvent.OrNothing(() => eventRoom.LocalMutableEvent)),
            () => GitsFormattedPage(canonical));
    }

    private static string? GitsFormattedPage(EventModel? ev)
    {
        var page = ev?.Description;
        if (ev == null || page == null || !page.Exists()) return null;
        try { ev.Owner?.Character?.AddDetailsTo(page); } catch (Exception) { }
        try { page.Add("IsMultiplayer", ev.Owner!.RunState.Players.Count > 1); } catch (Exception) { }
        try { ev.DynamicVars.AddTo(page); } catch (Exception) { }
        return page.GetFormattedText();
    }
}
