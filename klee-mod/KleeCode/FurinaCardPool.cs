using System.Collections.Generic;
using System.Linq;
using Godot;
using KleeMod.Cards.Furina;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod;

/// <summary>
/// Furina's complete personal pool. Generated cards are reward-eligible;
/// kit, selector, selector options, and Guest Stars are members only so their
/// CardModel.Pool lookups remain valid when they are created in combat.
/// </summary>
public sealed class FurinaCardPool : CardPoolModel
{
    public override string Title => "furina";

    // Temporary native frame while the Furina art pass is outstanding.
    public override string EnergyColorName => "silent";

    public override string CardFrameMaterialPath => "card_frame_green";

    public override Color DeckEntryCardColor => new("4AA6C8");

    public override Color EnergyOutlineColor => new("174B67");

    public override bool IsColorless => false;

    /// <summary>
    /// THE OFFER (<c>GetUnlockedCards</c>, the sole door into reward rolls,
    /// the shop and transforms): the Stage roster's pool, her Ancients and
    /// the co-op tier (<c>FurinaStageRoster.OfferablePool</c>).
    /// </summary>
    protected override IEnumerable<CardModel> FilterThroughEpochs(
        UnlockState unlockState, IEnumerable<CardModel> cards)
    {
        return Powers.FurinaStageRoster.OfferablePool();
    }

    /// <summary>
    /// MEMBERSHIP, the prototype rows first and as the pool (legacy cleanup
    /// stage 4, 2026-10-01): every `proto_` row she owns (the Stage's rows,
    /// its mode faces and the three Fontaine guest stars), then her Ancients
    /// (<c>tools/lint_ancient_coverage.py</c>), then the never-offered members
    /// (<see cref="FurinaOffPoolCards"/>). The shipped rows follow as members
    /// only until stage 5 deletes them.
    /// </summary>
    protected override CardModel[] GenerateAllCards() =>
        PrototypeCards.For("furina")
            .Concat(RosterAncientCards.Furina)
            .Concat(FurinaOffPoolCards.All)
            .Distinct()
            .ToArray();
}

public static class FurinaOffPoolCards
{
    private static List<CardModel>? _all;
    private static HashSet<ModelId>? _ids;

    public static IReadOnlyList<CardModel> All => _all ??= BuildAll();

    public static HashSet<ModelId> Ids =>
        _ids ??= All.Select(card => card.Id).ToHashSet();

    private static List<CardModel> BuildAll()
    {
        var cards = new List<CardModel>();
        // R276 batch two: Arkhe Alignment's two hand-written choice faces. A
        // choose-one option card in no pool falls through to MockCardPool,
        // whose GenerateAllCards throws "You monster!" inside
        // NChooseACardSelectionScreen._Ready() (EB-150).
        cards.Add(ModelDb.Card<Cards.Prototype.ArkheOusiaOption>());
        cards.Add(ModelDb.Card<Cards.Prototype.ArkhePneumaOption>());
        // THE RE-FOUNDING (2026-10-04): the performer picker's faces, and
        // Lyney's Trick, a token his act creates.
        cards.AddRange(Powers.FurinaStage.AllOptions());
        cards.Add(ModelDb.Card<Cards.Prototype.StageTrick>());
        return cards;
    }
}
