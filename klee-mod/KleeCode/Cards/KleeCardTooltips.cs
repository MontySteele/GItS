using System.Collections.Generic;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Rooms;

namespace KleeMod.Cards;

/// <summary>
/// Shared card affordances for Bomb rules and board-aware reaction previews.
/// ExtraHoverTips is evaluated when the card is inspected, so the reaction
/// list follows the enemies' current auras without patching card UI nodes.
/// For random/all-enemy cards it intentionally lists every distinct reaction
/// currently available; choosing a particular target remains the player's
/// decision.
/// </summary>
public static class KleeCardTooltips
{
    public static IEnumerable<IHoverTip> ForCard(
        IEnumerable<IHoverTip> inherited,
        CardModel card,
        Element trigger = Element.None,
        bool includesBombRules = false,
        bool includesConfiscatedRules = false)
    {
        foreach (var tip in inherited) yield return tip;

        if (includesBombRules)
        {
            yield return HoverTipFactory.FromKeyword(KleeKeywords.Bomb);
        }

        if (includesConfiscatedRules)
        {
            yield return HoverTipFactory.FromKeyword(KleeKeywords.Confiscated);
        }

        if (trigger == Element.None || card.CombatState == null) yield break;

        var seen = new HashSet<Reaction>();
        foreach (var enemy in card.CombatState.HittableEnemies)
        {
            var aura = AuraCmd.Find(enemy);
            if (aura == null) continue;

            var reaction = ReactionTable.Lookup(aura.Element, trigger);
            if (reaction == Reaction.None || !seen.Add(reaction)) continue;

            var keyword = reaction == Reaction.Frozen
                && enemy.CombatState?.Encounter?.RoomType == RoomType.Boss
                    ? KleeKeywords.FrozenBossPreview
                    : KleeKeywords.ReactionPreview(reaction);
            if (keyword != MegaCrit.Sts2.Core.Entities.Cards.CardKeyword.None)
            {
                yield return HoverTipFactory.FromKeyword(keyword);
            }
        }
    }
}
