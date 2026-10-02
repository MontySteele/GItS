using System.Collections.Generic;
using System.Linq;
using Godot;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Unlocks;

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

    /// <summary>
    /// THE OFFER. <c>GetUnlockedCards</c> is the only path into reward rolls
    /// (<c>CardCreationOptions.GetPossibleCards</c>) and card transforms
    /// (<c>CardFactory</c>), and this feeds it.
    ///
    /// The overhaul's pool, her Ancients and the co-op tier
    /// (<c>KleeOverhaulRoster.OfferablePool</c>).
    /// </summary>
    protected override IEnumerable<CardModel> FilterThroughEpochs(
        UnlockState unlockState, IEnumerable<CardModel> cards)
    {
        return Powers.KleeOverhaulRoster.OfferablePool();
    }

    /// <summary>
    /// MEMBERSHIP: every card whose <c>CardModel.Pool</c> is Klee's. A card in
    /// no pool throws "You monster!" the moment it is drawn
    /// (<see cref="KleeOffPoolCards"/>, <c>tools/lint_pool_membership.py</c>).
    /// Every `proto_` row she owns -- her kit, its starter and tokens, and the
    /// companion roster (Mondstadt, Inazuma and Fontaine) -- then her
    /// Ancients and her never-offered tokens.
    /// </summary>
    protected override CardModel[] GenerateAllCards() =>
        PrototypeCards.For("klee")
            .Concat(RosterAncientCards.Klee)
            .Concat(KleeOffPoolCards.All)
            .Distinct()
            .ToArray();
}
