using System.Collections.Generic;
using System.Linq;

namespace KleeMod.Elements;

/// <summary>
/// AN ELEMENT'S NAME AS PLAYER TEXT (the localization census, 2026-10-23).
/// Where code fills an element into a sentence -- a card face's hit element
/// (<see cref="Cards.OverriddenElementFace"/>), "Switches your current element
/// to Pyro" -- the name is a var whose value is this row, so a translation
/// names the element in its own words. <c>card_keywords</c>,
/// <c>KLEEMOD-ELEMENT_NAME.PYRO</c>.
/// </summary>
public static class ElementWords
{
    private const string Table = "card_keywords";

    /// <summary>The six elements the engine has.</summary>
    public static IReadOnlyList<Element> All { get; } = new[]
    {
        Element.Pyro, Element.Hydro, Element.Electro, Element.Cryo, Element.Anemo, Element.Geo,
    };

    /// <summary>The element's row. Its English is the enum's name.</summary>
    public static CodeRow RowOf(Element element) =>
        new(Table, "KLEEMOD-ELEMENT_NAME." + element.ToString().ToUpperInvariant(), element.ToString());

    /// <summary>The element's name as the player reads it; "" for None.</summary>
    public static string Name(Element element) =>
        element == Element.None ? "" : CodeText.Format(RowOf(element));

    public static IEnumerable<CodeRow> Rows() => All.Select(RowOf);
}
