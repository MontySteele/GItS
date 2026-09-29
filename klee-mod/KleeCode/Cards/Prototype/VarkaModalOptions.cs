using System.Collections.Generic;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Prototype;

/// <summary>
/// The four choose-a-Knight faces (<see cref="Powers.VarkaRules.ChooseKnight"/>),
/// carried the way every generated mode-face roster is (`EB-150`), so the
/// Varka pool puts them in <c>AllCardIds</c> and the grid can draw them.
/// </summary>
public static class VarkaModalOptions
{
    private static List<CardModel>? _all;

    public static IReadOnlyList<CardModel> All => _all ??= new List<CardModel>
    {
        ModelDb.Card<KnightOptionAmber>(),
        ModelDb.Card<KnightOptionBarbara>(),
        ModelDb.Card<KnightOptionLisa>(),
        ModelDb.Card<KnightOptionKaeya>(),
    };
}
