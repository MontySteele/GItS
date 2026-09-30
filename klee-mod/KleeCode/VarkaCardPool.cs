#if PROTOTYPE_CARDS && VARKA_PROTOTYPE
using System.Collections.Generic;
using System.Linq;
using Godot;
using KleeMod.Cards.Prototype;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod;

/// <summary>
/// Varka's card pool (the Oath rework). Its MEMBERS are every card of his
/// -- the generated rows and Change of Guard's four element faces -- so
/// <c>CardModel.Pool</c> resolves; its OFFER is the forty-one-card pool alone
/// (<see cref="VarkaRoster.Pool"/>). Compiled only with
/// <c>-p:VarkaPrototype=true</c>, beside the character.
/// </summary>
public sealed class VarkaCardPool : CardPoolModel
{
    public override string Title => VarkaPrototype.CharacterId;

    // The Silent's green frame and energy, the borrow Kokomi's and Furina's
    // pools make; his base Strike and Defend are hers for the same reason.
    public override string EnergyColorName => "silent";

    public override string CardFrameMaterialPath => "card_frame_green";

    public override Color DeckEntryCardColor => new("4CC2A8");

    public override Color EnergyOutlineColor => new("1D5E52");

    public override bool IsColorless => false;

    /// <summary>THE OFFER: the pool. The one door into reward rolls, the
    /// shop and transforms (<c>GetUnlockedCards</c>).</summary>
    protected override IEnumerable<CardModel> FilterThroughEpochs(
        UnlockState unlockState, IEnumerable<CardModel> cards) =>
        VarkaRoster.Pool();

    protected override CardModel[] GenerateAllCards() =>
        VarkaRoster.Members()
            .Concat(VarkaModalOptions.All)
            .ToArray();
}
#endif
