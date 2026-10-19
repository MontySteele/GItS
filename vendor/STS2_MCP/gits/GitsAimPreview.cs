// GItS LOCAL ADDITION - not upstream STS2MCP.
// GItS addition (Swirl legibility, 2026-10-19). THE AIM PREVIEW, per enemy.
//
// A player sees a reaction preview by dragging a card onto an enemy: the klee
// mod's `ReactionAim` patch asks the card for its previews against THAT enemy
// and shows them beside the held card. A newcomer seat reads the player's
// state (`?audience=player`, `GitsSeatTips.cs`) and has no drag, so it never
// saw one. This adds, to each card in hand that aims at one enemy, the
// previews a drag onto each enemy would show:
//
//   "aim_previews": [{"combat_id": 3, "tips": [{"name": ..., "description": ...}]}]
//
// Only enemies where one would show are listed, and the key is absent when
// none would. It is emitted ONLY on a player-audience read, so every other
// state is byte-for-byte what it was.
//
// THE SAME TEXT THE GAME SHOWS: the tips come from
// `KleeMod.Cards.ReactionAim.PreviewsFor(card, enemy)`, the method the drag
// patch calls, serialised by the bridge's own `BuildHoverTips`. Reflection,
// on `GitsSeatTips.cs`'s terms: no klee mod, no previews. Every failure is
// swallowed: a state read must never throw.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;

namespace STS2_MCP;

public static partial class McpMod
{
    private const string GitsReactionAimType = "KleeMod.Cards.ReactionAim";

    /// <summary>The wire key the previews ride under.</summary>
    internal const string GitsAimPreviewsKey = "aim_previews";

    [ThreadStatic] private static bool _gitsPlayerAudience;

    private static MethodInfo? _gitsPreviewsFor;
    private static int _gitsPreviewsWait;

    /// <summary>True while <see cref="GitsAsPlayer"/> is building a state.
    /// </summary>
    internal static bool GitsPlayerAudience => _gitsPlayerAudience;

    internal static void GitsSetPlayerAudience(bool on) => _gitsPlayerAudience = on;

    private static MethodInfo? GitsPreviewsForMethod()
    {
        if (_gitsPreviewsFor != null) return _gitsPreviewsFor;
        if (_gitsPreviewsWait-- > 0) return null;
        _gitsPreviewsWait = GitsSeatTipsRetry;
        try
        {
            var type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(a =>
                {
                    try { return a.GetType(GitsReactionAimType, false); }
                    catch { return null; }
                })
                .FirstOrDefault(t => t != null);
            _gitsPreviewsFor = type?.GetMethod(
                "PreviewsFor", BindingFlags.Static | BindingFlags.Public);
        }
        catch (Exception)
        {
            _gitsPreviewsFor = null;
        }
        return _gitsPreviewsFor;
    }

    /// <summary>Add <see cref="GitsAimPreviewsKey"/> to a hand card's row on
    /// a player-audience read, for a card that aims at one enemy.</summary>
    internal static void GitsAddAimPreviews(CardModel card,
                                            Dictionary<string, object?> row)
    {
        if (!_gitsPlayerAudience) return;
        try
        {
            if (card.TargetType != TargetType.AnyEnemy) return;
            var method = GitsPreviewsForMethod();
            var enemies = card.CombatState?.HittableEnemies;
            if (method == null || enemies == null) return;
            var found = new List<Dictionary<string, object?>>();
            foreach (var enemy in enemies.ToList())
            {
                if (method.Invoke(null, new object[] { card, enemy })
                    is not IEnumerable<IHoverTip> tips)
                {
                    continue;
                }
                var built = BuildHoverTips(tips);
                if (built.Count == 0) continue;
                found.Add(new Dictionary<string, object?>
                {
                    ["combat_id"] = enemy.CombatId,
                    ["tips"] = built,
                });
            }
            if (found.Count > 0) row[GitsAimPreviewsKey] = found;
        }
        catch (Exception)
        {
            /* a state read must never throw */
        }
    }
}
