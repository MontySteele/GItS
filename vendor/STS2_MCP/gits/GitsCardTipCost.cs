// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// A CARD AN EVENT OPTION NAMES, WITH ITS COST (the Furina guest seat round,
// 2026-09-25, 0.2.3794). The Wood Carvings event's Torus option names Toric
// Toughness through a `CardHoverTip`, and `BuildHoverTips` flattens a card tip
// into its title and description and nothing else -- so the option printed the
// card's rules and never its cost, and the seat learned it costs 2 when it drew
// it. A reward row and a hand line print `cost N`; an event's named card now
// can too.
//
// WHAT IT ADDS. `cost` on the flattened row of each CARD tip, matched by the
// title `BuildHoverTips` already wrote, in the same words `GetCostDisplay`
// gives every other card on the wire ("2", or "X"). A keyword tip gains no
// key, so every other row keeps the shape it had. Every failure is swallowed:
// a state read must never throw.

using System.Collections.Generic;
using MegaCrit.Sts2.Core.HoverTips;

namespace STS2_MCP;

public static partial class McpMod
{
    internal static List<Dictionary<string, object?>> GitsWithCardTipCosts(
        List<Dictionary<string, object?>> rows, IEnumerable<IHoverTip> tips)
    {
        try
        {
            foreach (var tip in tips)
            {
                if (tip is not CardHoverTip cardTip) continue;
                var title = SafeGetText(() => cardTip.Card.Title);
                if (title == null) continue;
                var cost = SafeGetText(() => GetCostDisplay(cardTip.Card));
                if (cost == null) continue;
                foreach (var row in rows)
                {
                    if (row.TryGetValue("name", out var name)
                        && name as string == title
                        && !row.ContainsKey("cost"))
                    {
                        row["cost"] = cost;
                    }
                }
            }
        }
        catch
        {
            // A cost this read cannot give is left off, never guessed.
        }
        return rows;
    }
}
