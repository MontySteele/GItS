using System;
using HarmonyLib;
using KleeMod.Elements;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// Kokomi review r9 (2026-10-15, item 5): AN OVERRIDDEN ELEMENT PRINTS IN THE
/// CARD TEXT. Surging Shoal+ under Razor's Lightning Fang showed the Electro
/// gem and tip and still read "Deal 13 Hydro damage". The gem, the tip and the
/// hit already read <see cref="KleeCardTooltips.AppliedElement"/>; this makes
/// the words a fourth reader of the same expression, by rewriting the printed
/// element word in the finished face. Display only; with no override the face
/// is untouched.
///
/// Only the phrases that name the element a hit applies are rewritten:
/// "[gold]Hydro[/gold] damage" and "Apply [gold]Hydro[/gold]".
/// </summary>
public static class OverriddenElementFace
{
    /// <summary>
    /// The face with the printed element's word replaced by the applied one.
    /// PURE. Unchanged when the two are the same, or either is None.
    /// </summary>
    public static string Rewrite(string text, Element printed, Element applied)
    {
        if (string.IsNullOrEmpty(text) || printed == applied
            || printed == Element.None || applied == Element.None)
        {
            return text;
        }
        var from = $"[gold]{printed}[/gold]";
        var to = $"[gold]{applied}[/gold]";
        return text
            .Replace(from + " damage", to + " damage")
            .Replace("Apply " + from, "Apply " + to);
    }

    /// <summary>The card's live face: its printed element against the one a
    /// rider is applying now.</summary>
    public static string Line(CardModel? card, string text)
    {
        if (card == null || !card.IsMutable) return text;
        try
        {
            var printed = ElementBadge.ElementOf(card);
            if (printed == Element.None) return text;
            var applied = KleeCardTooltips.AppliedElement(card, printed);
            return Rewrite(text, printed, applied);
        }
        catch (Exception)
        {
            return text;
        }
    }
}

[HarmonyPatch(typeof(CardModel), nameof(CardModel.GetDescriptionForPile),
    new[] { typeof(PileType), typeof(Creature) })]
internal static class OverriddenElementFacePatch
{
    [HarmonyPostfix]
    public static void Postfix(CardModel __instance, ref string __result)
    {
        __result = OverriddenElementFace.Line(__instance, __result);
    }
}
