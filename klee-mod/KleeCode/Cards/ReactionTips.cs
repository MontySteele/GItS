using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// ONE HOVER TIP PER ELEMENT: what it reacts with ([USER], 2026-10-22:
/// "hover tooltips are a good idea if you're about to trigger one, but it
/// would help to have some way to find them all in-game"). The body is
/// <see cref="ReactionGuide.TipBody"/>, generated from the reaction table.
///
/// WHERE IT SHOWS. Beside the element's own card keyword (the Applies-X tip
/// that rides every elemental card and its gem, <see cref="Vfx.ElementBadge"/>)
/// and beside an aura on a creature (<see cref="Powers.AuraPower"/>). A blind
/// seat's page (<see cref="TipAudience.Seat"/>) does not get it: the seat
/// already reads every live preview, and the chart is for a player.
/// </summary>
public static class ReactionTips
{
    private const string Table = "card_keywords";

    /// <summary>The title key, `KLEEMOD-REACTIONS_PYRO`; its `.title` row is
    /// registered in <c>KleeMod.InjectLocStrings</c>.</summary>
    public static string Key(Element element) =>
        "KLEEMOD-REACTIONS_" + element.ToString().ToUpperInvariant();

    public const string PyroKey = "KLEEMOD-REACTIONS_PYRO";
    public const string HydroKey = "KLEEMOD-REACTIONS_HYDRO";
    public const string ElectroKey = "KLEEMOD-REACTIONS_ELECTRO";
    public const string CryoKey = "KLEEMOD-REACTIONS_CRYO";
    public const string AnemoKey = "KLEEMOD-REACTIONS_ANEMO";
    public const string GeoKey = "KLEEMOD-REACTIONS_GEO";

    /// <summary>The element a card keyword applies, or None.</summary>
    public static Element ElementOf(CardKeyword keyword)
    {
        if (keyword == CardKeyword.None) return Element.None;
        if (keyword == KleeKeywords.AppliesPyro) return Element.Pyro;
        if (keyword == KleeKeywords.AppliesHydro) return Element.Hydro;
        if (keyword == KleeKeywords.AppliesElectro) return Element.Electro;
        if (keyword == KleeKeywords.AppliesCryo) return Element.Cryo;
        if (keyword == KleeKeywords.AppliesAnemo) return Element.Anemo;
        if (keyword == KleeKeywords.AppliesGeo) return Element.Geo;
        return Element.None;
    }

    /// <summary>The tip for <paramref name="element"/>, or null for one with
    /// no reaction.</summary>
    public static IHoverTip? For(Element element)
    {
        var body = ReactionGuide.TipBody(element);
        if (body.Length == 0) return null;
        return new HoverTip(new LocString(Table, Key(element) + ".title"), body)
        {
            Id = Key(element),
        };
    }

    /// <summary>
    /// <paramref name="tips"/> with each element's reaction tip placed right
    /// after that element's keyword tip. Never throws: a hover is not worth a
    /// broken card.
    /// </summary>
    public static IEnumerable<IHoverTip> WithReactionTips(IEnumerable<IHoverTip> tips, CardModel card)
    {
        if (TipAudience.Seat) return tips;
        try
        {
            var elements = card.Keywords.Select(ElementOf).Where(e => e != Element.None).Distinct().ToList();
            if (elements.Count == 0) return tips;
            var list = tips.ToList();
            foreach (var element in elements)
            {
                if (For(element) is not { } tip || list.Any(t => t.Id == tip.Id)) continue;
                var keywordTip = HoverTipFactory.FromKeyword(KeywordOf(element));
                var at = list.IndexOf(keywordTip);
                if (at < 0) list.Add(tip);
                else list.Insert(at + 1, tip);
            }
            return list;
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] reaction tip skipped: {e.Message}");
            return tips;
        }
    }

    private static CardKeyword KeywordOf(Element element) => element switch
    {
        Element.Anemo => KleeKeywords.AppliesAnemo,
        Element.Geo => KleeKeywords.AppliesGeo,
        _ => KleeKeywords.AuraApplication(element),
    };
}

/// <summary>The one arming point: every card's tip list, on every surface
/// (hand, reward, shop, compendium), is <c>CardModel.HoverTips</c>.</summary>
[HarmonyPatch(typeof(CardModel), nameof(CardModel.HoverTips), MethodType.Getter)]
internal static class CardModel_HoverTips_ReactionTips_Patch
{
    [HarmonyPostfix]
    public static void Postfix(CardModel __instance, ref IEnumerable<IHoverTip> __result) =>
        __result = ReactionTips.WithReactionTips(__result, __instance);
}
