using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using KleeMod.Elements;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// Kokomi review r9 (2026-10-15, item 5): AN OVERRIDDEN ELEMENT PRINTS IN THE
/// CARD TEXT. Surging Shoal+ under Razor's Lightning Fang showed the Electro
/// gem and tip and still read "Deal 13 Hydro damage". The gem, the tip and the
/// hit already read <see cref="KleeCardTooltips.AppliedElement"/>; the words
/// are a fourth reader of the same expression. Display only; with no override
/// the face is untouched.
///
/// AN ELEMENT TOKEN, NOT A REWRITE OF ENGLISH (the localization census,
/// 2026-10-23, group 3). The first version replaced "[gold]Hydro[/gold]
/// damage" in the FINISHED face, which a translated face never matches. Now
/// the hit-element words are tokens in the row itself: as our card rows are
/// written to the English table (<see cref="EnglishLoc.ModelRowText"/>), each
/// "[gold]Hydro[/gold] damage" and "Apply [gold]Hydro[/gold]" becomes
/// "[gold]{Hydro}[/gold] damage" / "Apply [gold]{Hydro}[/gold]". The
/// generated source keeps the plain English, so the face lints and the sim
/// read the face they always did; the English reference shows the token, so
/// a translation keeps it where its own sentence puts the element.
///
/// Every formatting of such a row is handed the six element names
/// (<see cref="ElementWords"/>, so a translation names them in its own
/// words), with the card's printed element's token naming the element it
/// applies now. Only the phrases that name the element a hit applies are
/// tokens.
/// </summary>
public static class OverriddenElementFace
{
    // The phrases whose element is the hit's, in our English. This is the
    // one place English is read, and it is our own row as it is written.
    private static string Damage(Element e) => $"[gold]{e}[/gold] damage";
    private static string Apply(Element e) => $"Apply [gold]{e}[/gold]";

    /// <summary>The row with its hit-element words as tokens. PURE.</summary>
    public static string Templatize(string row)
    {
        if (string.IsNullOrEmpty(row) || !row.Contains("[gold]", StringComparison.Ordinal)) return row;
        var text = row;
        foreach (var e in ElementWords.All)
        {
            text = text
                .Replace(Damage(e), "[gold]{" + e + "}[/gold] damage", StringComparison.Ordinal)
                .Replace(Apply(e), "Apply [gold]{" + e + "}[/gold]", StringComparison.Ordinal);
        }
        return text;
    }

    /// <summary>The value of each element token: its own name, except that
    /// the printed element's token names <paramref name="applied"/>.</summary>
    public static Dictionary<string, object> Tokens(Element printed, Element applied)
    {
        var tokens = new Dictionary<string, object>(StringComparer.Ordinal);
        foreach (var e in ElementWords.All)
        {
            var shown = e == printed && applied != Element.None ? applied : e;
            tokens[e.ToString()] = ElementWords.Name(shown);
        }
        return tokens;
    }

    /// <summary>The card's printed element and the one a rider is applying
    /// now; both None for a canonical card or a card with no element. Never
    /// throws.</summary>
    public static (Element Printed, Element Applied) ElementsOf(CardModel? card)
    {
        if (card == null || !card.IsMutable) return (Element.None, Element.None);
        try
        {
            var printed = ElementBadge.ElementOf(card);
            if (printed == Element.None) return (Element.None, Element.None);
            return (printed, KleeCardTooltips.AppliedElement(card, printed));
        }
        catch (Exception)
        {
            return (Element.None, Element.None);
        }
    }

    /// <summary>The <c>cards</c> rows, by key, that carry element tokens,
    /// recorded as they are written.</summary>
    internal static readonly HashSet<string> TokenRows = new(StringComparer.Ordinal);

    /// <summary>The card whose face is being formatted on this thread.</summary>
    [ThreadStatic] internal static CardModel? Formatting;

    /// <summary>The tokens for the row <paramref name="key"/>: the card's own
    /// reading while that card's face is being formatted, the plain names
    /// anywhere else.</summary>
    internal static Dictionary<string, object> TokensFor(string key)
    {
        var card = Formatting;
        if (card != null && card.Id.Entry + ".description" == key)
        {
            var (printed, applied) = ElementsOf(card);
            return Tokens(printed, applied);
        }
        return Tokens(Element.None, Element.None);
    }
}

/// <summary>Which card a face belongs to, for the length of its formatting.
/// The private overload is the one both public paths (the pile and the
/// upgrade preview) run through.</summary>
[HarmonyPatch]
internal static class OverriddenElementFace_Card_Patch
{
    // `GetDescriptionForPile(PileType, DescriptionPreviewType, Creature)`,
    // whose middle parameter is a private enum.
    private static MethodBase TargetMethod() =>
        AccessTools.GetDeclaredMethods(typeof(CardModel)).First(m =>
            m.Name == "GetDescriptionForPile" && m.GetParameters().Length == 3);

    [HarmonyPrefix]
    public static void Prefix(CardModel __instance, out CardModel? __state)
    {
        __state = OverriddenElementFace.Formatting;
        OverriddenElementFace.Formatting = __instance;
    }

    [HarmonyFinalizer]
    public static void Finalizer(CardModel? __state)
    {
        OverriddenElementFace.Formatting = __state;
    }
}

/// <summary>Every formatting of a token row is handed the names, so a token
/// never prints raw.</summary>
[HarmonyPatch(typeof(LocManager), nameof(LocManager.SmartFormat))]
internal static class OverriddenElementFace_Format_Patch
{
    [HarmonyPrefix]
    public static void Prefix(LocString locString, Dictionary<string, object> variables)
    {
        try
        {
            if (locString.LocTable != "cards"
                || !OverriddenElementFace.TokenRows.Contains(locString.LocEntryKey)) return;
            foreach (var (name, value) in OverriddenElementFace.TokensFor(locString.LocEntryKey))
            {
                variables.TryAdd(name, value);
            }
        }
        catch (Exception)
        {
            // A face is not worth a broken screen; SmartFormat reports a
            // missing token itself.
        }
    }
}
