using System.Collections.Generic;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.HoverTips;

namespace KleeMod.Cards;

/// <summary>
/// THE TOOLTIP TRIM (2026-10-14), pick 2 (a): a reaction preview shows ONE
/// box, only for the enemy the card is being aimed at, and none while the card
/// is only hovered in hand.
///
/// WHERE THE AIM IS KNOWN (sts2.dll decompile). While a card is dragged onto
/// an enemy, <c>NCardPlay.OnCreatureHover(NCreature)</c> hands the enemy to
/// the card face (<c>NCard.SetPreviewTarget</c>) and
/// <c>OnCreatureUnhover</c> / <c>ClearTarget</c> take it back. The base game
/// removes the card's hover tips when the drag starts
/// (<c>NMouseCardPlay.StartCardDrag</c>, <c>NControllerCardPlay.Start</c>:
/// <c>NHoverTipSet.Remove(Holder)</c>), so nothing is on screen while aiming.
/// This patch puts the one preview there: on a creature hover it asks the card
/// for its previews against THAT enemy and shows them beside the held card;
/// on unhover, cancel and finish it removes them.
///
/// A card aimed at ALL enemies (or none) never calls
/// <c>OnCreatureHover</c>, so it shows no preview; the enemy's aura badge
/// still names its aura.
///
/// A blind seat is untouched: through the bridge
/// (<see cref="TipAudience.Seat"/>) the card's hover still carries every
/// matching aura's preview, as before.
/// </summary>
public static class ReactionAim
{
    [System.ThreadStatic] private static CardModel? _card;
    [System.ThreadStatic] private static Creature? _target;
    [System.ThreadStatic] private static List<IHoverTip>? _found;

    /// <summary>The enemy <paramref name="card"/> is being aimed at while
    /// its previews are asked for, or null.</summary>
    internal static Creature? TargetFor(CardModel card) =>
        _card != null && ReferenceEquals(_card, card) ? _target : null;

    /// <summary>Called by <see cref="KleeCardTooltips.ForCard"/> with the
    /// previews it built for the aimed enemy.</summary>
    internal static void Collect(IEnumerable<IHoverTip> tips) =>
        _found?.AddRange(tips);

    /// <summary>The reaction previews <paramref name="card"/> raises against
    /// <paramref name="target"/>, and nothing else. Empty for a card that
    /// applies no element or a target with no matching aura.</summary>
    public static List<IHoverTip> PreviewsFor(CardModel card, Creature target)
    {
        var was = (_card, _target, _found);
        _card = card;
        _target = target;
        _found = new List<IHoverTip>();
        try
        {
            // Walking the getter drives `ExtraHoverTips`, where ForCard
            // collects; the other boxes it yields are not shown here.
            foreach (var _ in card.HoverTips) { }
            return _found;
        }
        finally
        {
            (_card, _target, _found) = was;
        }
    }

    /// <summary>Show the aimed enemy's preview beside the held card.</summary>
    internal static void Show(NCardPlay play, Creature? target)
    {
        var holder = play.Holder;
        if (holder == null) return;
        NHoverTipSet.Remove(holder);
        var card = holder.CardModel;
        if (card == null || target == null) return;
        var tips = PreviewsFor(card, target);
        if (tips.Count == 0) return;
        NHoverTipSet.CreateAndShow(holder, tips)?.SetAlignmentForCardHolder(holder);
    }

    /// <summary>Take the preview down (unhover, cancel, finish).</summary>
    internal static void Hide(NCardPlay play)
    {
        var holder = play.Holder;
        if (holder != null) NHoverTipSet.Remove(holder);
    }
}

/// <summary><see cref="ReactionAim"/>'s show: the enemy under the aim.
/// Display only, and it never throws into the game's targeting.</summary>
[HarmonyPatch(typeof(NCardPlay), "OnCreatureHover")]
internal static class ReactionAimHoverPatch
{
    [HarmonyPostfix]
    public static void Postfix(NCardPlay __instance, NCreature creature)
    {
        try { ReactionAim.Show(__instance, creature?.Entity); }
        catch (System.Exception e)
        {
            Log.Warn($"[klee] reaction preview on aim failed: {e.Message}");
        }
    }
}

/// <summary><see cref="ReactionAim"/>'s hide: the aim left the enemy.</summary>
[HarmonyPatch(typeof(NCardPlay), "OnCreatureUnhover")]
internal static class ReactionAimUnhoverPatch
{
    [HarmonyPostfix]
    public static void Postfix(NCardPlay __instance)
    {
        try { ReactionAim.Hide(__instance); }
        catch (System.Exception) { /* display only */ }
    }
}

/// <summary><see cref="ReactionAim"/>'s hide on cancel and on finish: the
/// game's own <c>Cleanup</c> runs on both, and the card's own hover tips are
/// created again on the same holder once it is back in hand, which would
/// collide with a set still registered to it.</summary>
[HarmonyPatch(typeof(NCardPlay), "Cleanup")]
internal static class ReactionAimCleanupPatch
{
    [HarmonyPrefix]
    public static void Prefix(NCardPlay __instance)
    {
        try { ReactionAim.Hide(__instance); }
        catch (System.Exception) { /* display only */ }
    }
}
