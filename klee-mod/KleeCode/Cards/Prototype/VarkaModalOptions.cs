using System.Collections.Generic;
using Godot;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Prototype;

/// <summary>
/// Change of Guard's four element faces (<see cref="Powers.VarkaRules.ChooseElement"/>),
/// carried the way every generated mode-face roster is (`EB-150`), so the
/// Varka pool puts them in <c>AllCardIds</c> and the grid can draw them.
/// </summary>
public static class VarkaModalOptions
{
    private static List<CardModel>? _all;

    public static IReadOnlyList<CardModel> All => _all ??= new List<CardModel>
    {
        ModelDb.Card<ElementOptionPyro>(),
        ModelDb.Card<ElementOptionHydro>(),
        ModelDb.Card<ElementOptionElectro>(),
        ModelDb.Card<ElementOptionCryo>(),
    };

    /// <summary>The face for <paramref name="element"/>, made for
    /// <paramref name="owner"/>, or null for an element with no face.</summary>
    public static CardModel? FaceFor(Element element, Player owner) => element switch
    {
        Element.Pyro => ModalChoice.CreateOption<ElementOptionPyro>(owner),
        Element.Hydro => ModalChoice.CreateOption<ElementOptionHydro>(owner),
        Element.Electro => ModalChoice.CreateOption<ElementOptionElectro>(owner),
        Element.Cryo => ModalChoice.CreateOption<ElementOptionCryo>(owner),
        _ => null,
    };
}

/// <summary>The element a Change of Guard face stands for.</summary>
public interface ElementOption
{
    Element OptionElement { get; }
}

/// <summary>
/// One element on Change of Guard's grid. A FACE, never played and never in
/// a pile, but a pool member (<c>VarkaModalOptions.All</c>), because a card in
/// no pool throws "You monster!" the moment the screen draws it (EB-150). It
/// wears the art of that element's starter Knight. Each is a direct
/// <c>ModalOptionCard</c> so <c>tools/lint_pool_membership.py</c> can see it.
/// </summary>
public sealed class ElementOptionPyro : ModalOptionCard, ElementOption
{
    public Element OptionElement => Element.Pyro;

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("proto_mc_amber_fiery_rain");

    public override List<(string, string)>? Localization =>
        ElementFace.For(Element.Pyro);
}

public sealed class ElementOptionHydro : ModalOptionCard, ElementOption
{
    public Element OptionElement => Element.Hydro;

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("proto_mc_barbara_melody_loop");

    public override List<(string, string)>? Localization =>
        ElementFace.For(Element.Hydro);
}

public sealed class ElementOptionElectro : ModalOptionCard, ElementOption
{
    public Element OptionElement => Element.Electro;

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("proto_mc_lisa_lightning_rose");

    public override List<(string, string)>? Localization =>
        ElementFace.For(Element.Electro);
}

public sealed class ElementOptionCryo : ModalOptionCard, ElementOption
{
    public Element OptionElement => Element.Cryo;

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("proto_mc_kaeya_glacial_waltz");

    public override List<(string, string)>? Localization =>
        ElementFace.For(Element.Cryo);
}

/// <summary>The four faces' one wording.</summary>
internal static class ElementFace
{
    internal static List<(string, string)> For(Element element) => new()
    {
        ("title", element.ToString()),
        ("description", $"Make [gold]{element}[/gold] your current element."),
    };
}
