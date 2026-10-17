// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// KOKOMI REVIEW R8 (2026-10-14, item 10): A POWER NEVER LEAVES THE LIST
// BECAUSE ITS TEXT COULD NOT BE READ.
//
// THE FIND. A Kokomi seat watched At Water's Edge vanish from its buff list
// on turn 5 against Hunter Killer and come back only in the next fight. The
// power was never removed: Hunter Killer's one debuff is Tender, which moves
// Strength and Dexterity and removes nothing (decompiled `TenderPower`), the
// lane's log shows the card played once that fight, and nothing in the mod
// removes `AtWatersEdgePower`. The one path that drops a power from the page
// while it stays on the creature is `BuildPowersState`'s per-power catch: a
// throw while the tooltip text is read (a state transition; that turn opened
// two potion choose-a-card screens) skipped the whole row, silently.
//
// THE FIX. The row stays, with the facts that do not need the text (name,
// amount, stack, type) and `unreadable` set to the exception's type name, so
// the page can say the text could not be read this screen, and the next
// occurrence names its cause instead of vanishing. Pure: no game type here,
// so `GitsPowerRowTests` pins it off the same file the bridge compiles.

using System.Collections.Generic;

namespace STS2_MCP;

public static class GitsPowerRow
{
    /// <summary>The row a power keeps when its text throws: what the board
    /// can still say about it, and why the rest is missing.</summary>
    public static Dictionary<string, object?> Unreadable(
        string id, string? name, int amount, string stack, string type,
        string error) =>
        new()
        {
            ["id"] = id,
            ["name"] = string.IsNullOrWhiteSpace(name) ? id : name,
            ["amount"] = amount,
            ["stack"] = stack,
            ["type"] = type,
            ["description"] = null,
            ["keywords"] = new List<Dictionary<string, object?>>(),
            ["unreadable"] = error,
        };
}
