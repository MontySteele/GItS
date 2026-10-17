using System.Collections.Generic;
using System.Linq;
using Godot;
using KleeMod.Cards.Prototype;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod;

/// <summary>
/// Yae Miko's card pool. Its MEMBERS are every card of hers -- the generated
/// rows and Reborn as Guuji Yae's five Annotation faces -- so
/// <c>CardModel.Pool</c> resolves; its OFFER is batch one's thirty
/// (<see cref="YaeRoster.Pool"/>). Varka's arrangement.
/// </summary>
public sealed class YaeCardPool : CardPoolModel
{
    public override string Title => YaePrototype.CharacterId;

    // The Defect's blue frame and energy (Electro's nearest base colour);
    // her base Strike and Defend are his for the same reason.
    public override string EnergyColorName => "defect";

    public override string CardFrameMaterialPath => "card_frame_blue";

    public override Color DeckEntryCardColor => new("B07FE0");

    public override Color EnergyOutlineColor => new("4B2A6E");

    public override bool IsColorless => false;

    /// <summary>THE OFFER: her pool (<see cref="YaeRoster.OfferablePool"/>),
    /// the one door into reward rolls, the shop and transforms.</summary>
    protected override IEnumerable<CardModel> FilterThroughEpochs(
        UnlockState unlockState, IEnumerable<CardModel> cards) =>
        YaeRoster.OfferablePool();

    /// <summary>MEMBERSHIP: her generated rows, the five Annotation faces,
    /// then her two Ancients (<c>RosterAncientCards.Yae</c>, the Yae pass
    /// 2026-10-16; <c>tools/lint_ancient_coverage.py</c>).</summary>
    protected override CardModel[] GenerateAllCards() =>
        YaeRoster.Members()
            .Concat(YaeModalOptions.All)
            .Concat(RosterAncientCards.Yae)
            .ToArray();
}
