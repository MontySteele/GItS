using Godot;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;

namespace KleeMod;

/// <summary>
/// Klee's card pool. C1 contains only the four starter stubs; the slice list
/// (31 cards + companions, spec C2) lands via codegen from the YAML sheet.
///
/// C1 STUB: EnergyColorName / CardFrameMaterialPath borrow Ironclad's red
/// assets because we ship no .pck yet (has_pck: false). Custom frame + energy
/// art is an art-pass item, not a boot blocker.
/// </summary>
public sealed class KleeCardPool : CardPoolModel
{
    public override string Title => "klee";

    public override string EnergyColorName => "ironclad";

    public override string CardFrameMaterialPath => "card_frame_red";

    // Klee red, per spec C1.4 (artist's final call later).
    public override Color DeckEntryCardColor => new Color("E85A4F");

    public override Color EnergyOutlineColor => new Color("7A2418");

    public override bool IsColorless => false;

    protected override CardModel[] GenerateAllCards()
    {
        return new CardModel[]
        {
            ModelDb.Card<Kaboom>(),
            ModelDb.Card<DuckAndCover>(),
            ModelDb.Card<JumpyDumpty>(),
            ModelDb.Card<Pop>(),
        };
    }
}
