using System.Collections.Generic;
using System.Linq;
using BaseLib.Utils.Attributes;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod;

/// <summary>
/// Klee's card pool. C1 contains only the four starter stubs; the slice list
/// (31 cards + companions, spec C2) lands via codegen from the YAML sheet.
///
/// The frame is her own tint of the base frame (card frames stage 1,
/// <see cref="CardFrameColors"/>), and the energy orb her own recolour of the
/// base one (stage 2, through <see cref="KitCardPool"/>).
/// </summary>
[CustomID("KLEE_CARD_POOL")]
public sealed class KleeCardPool : KitCardPool
{
    public override string Title => "klee";

    /// <summary>Frame tint, chip and orb-number outline:
    /// <see cref="CardFrameColors.Klee"/>.</summary>
    public override CardFrameColors.Tint Tint => CardFrameColors.Klee;

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
    /// Every `proto_` row in her pool -- her kit, its starter and tokens, and
    /// her three own companions -- then her Ancients and her never-offered
    /// tokens. The shared companions are NOT here since legacy review pick 4
    /// ([USER] 2026-10-18: "Shared companions move to their own pool with a
    /// neutral frame, out of Klee's"): they are <see cref="CompanionCardPool"/>'s,
    /// though their rows still say `character: klee`.
    /// </summary>
    protected override CardModel[] GenerateAllCards() =>
        PrototypeCards.For("klee")
            .Concat(RosterAncientCards.Klee)
            .Concat(KleeOffPoolCards.All)
            .Distinct()
            .ToArray();
}
